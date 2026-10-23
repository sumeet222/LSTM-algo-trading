"""P022 checkpoint objective accounting, train-frozen cohorts and exact case excerpts."""

from __future__ import annotations

import numpy as np
import pandas as pd
import torch

from .hf1m_action_audit import SYMBOLS
from .hf1m_ft16_source import ORDER
from .objective_screen_loss import Objective
from .objective_screen_metrics import equal_weights


def allocations(frame: pd.DataFrame, arm: str, recipe: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Replay the actual float32 pointwise loss and float64 true R1 pair directions.

    Weighted allocations sum to the equal-session checkpoint objective. Equivalent
    row loss divides the allocation by ordinary session/origin/stock mass; its
    unweighted share is a separate accounting convention, not the optimized loss.
    """
    f = frame.copy().reset_index(drop=True)
    days, di = np.unique(f.session_date_et.to_numpy().reshape(-1, 20)[:, 0], return_inverse=True)
    slots = pd.Series(di).groupby(di).cumcount().to_numpy().copy()
    assert slots.max() <= 1
    y64 = f.TG20.to_numpy(dtype=float).reshape(-1, 20).copy()
    y = torch.zeros((len(days), 2, 20), dtype=torch.float32)
    exact = torch.zeros(y.shape, dtype=torch.float64)
    mask = torch.zeros((len(days), 2), dtype=torch.bool)
    y[di, slots] = torch.from_numpy(y64.astype(np.float32))
    exact[di, slots] = torch.from_numpy(y64)
    mask[di, slots] = True
    output = torch.zeros((*y.shape, 3) if arm == "E1" else y.shape)
    raw_output = (
        f[["logit_NEG", "logit_NORMAL", "logit_POS"]].to_numpy()
        if arm == "E1"
        else f.raw_net_output.to_numpy()
    )
    output[di, slots] = torch.from_numpy(
        raw_output.astype(np.float32).reshape(-1, 20, 3)
        if arm == "E1"
        else raw_output.astype(np.float32).reshape(-1, 20)
    )
    with torch.inference_mode():
        terms = Objective(arm, recipe).contributions(output, y, mask, exact)
    w = equal_weights(f.session_date_et.to_numpy())
    f["ordinary_weight"] = w
    for key in ["pointwise", "pairwise", "total", "normalized_weight", "coefficient", "raw"]:
        values = terms[key][di, slots].numpy().astype(float).reshape(-1)
        f[key] = (
            values / len(days)
            if key in {"pointwise", "pairwise", "total", "normalized_weight"}
            else values
        )
    f["equivalent_row_loss"] = f.total / w
    f["z"] = np.arcsinh(f.TG20 / recipe["scale"])
    np.testing.assert_allclose(f.normalized_weight.sum(), 1, rtol=2e-7)
    np.testing.assert_allclose(f.total, f.pointwise + f.pairwise, rtol=3e-7, atol=1e-12)
    # Independent numpy reduction over complete days; all padding is excluded.
    independent_frame = pd.DataFrame(
        dict(day=f.session_date_et, numerator=f.raw * f.coefficient, coefficient=f.coefficient)
    )
    sums = independent_frame.groupby("day")[["numerator", "coefficient"]].sum()
    independent = (sums.numerator / sums.coefficient).mean()
    np.testing.assert_allclose(f.pointwise.sum(), independent, rtol=3e-7)
    pairs = pd.DataFrame()
    if arm == "R1":
        i, j = np.triu_indices(20, 1)
        true = np.sign(y64[:, i] - y64[:, j])
        score = raw_output.reshape(-1, 20).astype(float)
        margin = true * (score[:, i] - score[:, j])
        valid = true != 0
        loss = np.logaddexp(0, -margin) * valid
        origin_weight = w.reshape(-1, 20).sum(axis=1)
        weight = 0.5 * origin_weight[:, None] / np.maximum(valid.sum(axis=1), 1)[:, None]
        weighted = loss * weight
        independent_alloc = np.zeros_like(y64)
        for k in range(190):
            independent_alloc[:, i[k]] += weighted[:, k] / 2
            independent_alloc[:, j[k]] += weighted[:, k] / 2
        np.testing.assert_allclose(
            f.pairwise.to_numpy().reshape(-1, 20), independent_alloc, rtol=4e-7, atol=1e-11
        )
        origins = f.origin_id.to_numpy().reshape(-1, 20)[:, 0]
        pairs = pd.DataFrame(
            dict(
                origin_id=np.repeat(origins, 190),
                stock_i=np.tile(np.asarray(SYMBOLS)[i], len(origins)),
                stock_j=np.tile(np.asarray(SYMBOLS)[j], len(origins)),
                valid=valid.reshape(-1),
                true_direction=true.reshape(-1),
                signed_margin=margin.reshape(-1),
                raw_pair_loss=loss.reshape(-1),
                weighted_pair_loss=weighted.reshape(-1),
                misordered=((margin <= 0) & valid).reshape(-1),
            )
        )
        np.testing.assert_allclose(pairs.weighted_pair_loss.sum(), f.pairwise.sum(), rtol=3e-7)
    return f, pairs


def cohort_masks(f: pd.DataFrame, training: pd.DataFrame) -> tuple[dict[str, np.ndarray], dict]:
    """Rank cohorts are within this population; magnitude cutoffs always use fitting data."""
    masks = {"ALL": np.ones(len(f), dtype=bool)}
    cutoffs = {}
    keys = f.origin_id.to_numpy()
    stocks = np.tile(np.arange(20), len(f) // 20)
    for pct in (1, 5):
        for name, values in [
            ("TARGET", abs(f.TG20.to_numpy())),
            ("Z", abs(f.z.to_numpy())),
            ("NUMERATOR", abs(f.numerator.to_numpy())),
        ]:
            order = np.lexsort((stocks, keys, -values))
            chosen = order[: len(f) * pct // 100]
            m = np.zeros(len(f), dtype=bool)
            m[chosen] = True
            label = f"{name}_RANK_TOP{pct}"
            masks[label] = m
            cutoffs[label] = float(values[chosen].min()) if len(chosen) else None
        np.testing.assert_array_equal(masks[f"TARGET_RANK_TOP{pct}"], masks[f"Z_RANK_TOP{pct}"])
        origins = f.drop_duplicates("origin_id").sort_values(["cross_section_mad", "origin_id"])
        selected = origins.iloc[: len(origins) * pct // 100]
        m = f.origin_id.isin(selected.origin_id).to_numpy()
        cutoffs[f"MAD_BOTTOM{pct}"] = (
            float(selected.cross_section_mad.max()) if len(selected) else None
        )
        masks[f"MAD_BOTTOM{pct}"] = m
        n = masks[f"NUMERATOR_RANK_TOP{pct}"]
        for name, value in [
            ("BOTH", n & m),
            ("NUM_ONLY", n & ~m),
            ("MAD_ONLY", ~n & m),
            ("NEITHER", ~n & ~m),
            ("UNION", n | m),
        ]:
            masks[f"{name}_{pct}"] = value
        disjoint = np.stack(
            [masks[f"{k}_{pct}"] for k in ["BOTH", "NUM_ONLY", "MAD_ONLY", "NEITHER"]]
        )
        assert (disjoint.sum(axis=0) == 1).all()
    train_y = training.TG20.to_numpy()
    for fraction in (0.99, 0.95):
        for side, maximum, sign in [
            ("ABS", float(np.max(abs(train_y))), 0),
            ("POS", float(np.max(train_y)), 1),
            ("NEG", float(-np.min(train_y)), -1),
        ]:
            label = f"RANGE_{side}_{fraction}"
            threshold = fraction * maximum
            values = f.TG20.to_numpy()
            masks[label] = abs(values) >= threshold if sign == 0 else values * sign >= threshold
            cutoffs[label] = threshold
    for key, value in list(masks.items()):
        if key != "ALL":
            masks[key + "_COMPLEMENT"] = ~value
        masks[key + "_POS"] = value & f.TG20.gt(0).to_numpy()
        masks[key + "_NEG"] = value & f.TG20.lt(0).to_numpy()
    return masks, cutoffs


def cohort_table(f: pd.DataFrame, masks: dict[str, np.ndarray], thresholds: dict) -> pd.DataFrame:
    records = []
    for name, m in masks.items():
        g = f.loc[m]
        row = dict(
            cohort=name,
            threshold=thresholds.get(name),
            rows=len(g),
            row_pct=100 * len(g) / len(f),
            origins=g.origin_id.nunique(),
            sessions=g.session_date_et.nunique(),
            ordinary_weight_mass=g.ordinary_weight.sum(),
            objective_weight_mass=g.normalized_weight.sum(),
            weighted_objective=g.total.sum(),
            unweighted_equivalent=g.equivalent_row_loss.sum(),
            weighted_loss_share_pct=100 * g.total.sum() / f.total.sum(),
            unweighted_loss_share_pct=100
            * g.equivalent_row_loss.sum()
            / f.equivalent_row_loss.sum(),
            pointwise=g.pointwise.sum(),
            pairwise=g.pairwise.sum(),
        )
        records.append(row)
    table = pd.DataFrame(records)
    for pct in (1, 5):
        disjoint = table.loc[
            table.cohort.isin([f"{k}_{pct}" for k in ["BOTH", "NUM_ONLY", "MAD_ONLY", "NEITHER"]])
        ]
        assert int(disjoint.rows.sum()) == len(f)
        np.testing.assert_allclose(disjoint.weighted_objective.sum(), f.total.sum(), rtol=1e-13)
    return table


def feature_excerpt(
    view, arrays: dict[str, np.ndarray], origin_position: int, stock: str
) -> pd.DataFrame:
    """Only one actual48-step input window; no dense historical window store."""
    from .objective_screen_source import gather

    pos = (origin_position,)
    j = SYMBOLS.index(stock)
    native = gather(view, arrays, pos, "native")[0, j]
    fallback = gather(view, arrays, pos, "fallback")[0, j]
    scaled = view.origin_batch(pos)["x"][0, j]
    first = int(view.source.rows.iloc[origin_position].first_step)
    return pd.DataFrame(
        dict(
            step=np.repeat(np.arange(first, first + 48), 16),
            feature=np.tile(ORDER, 48),
            native=native.reshape(-1),
            scaled=scaled.reshape(-1),
            fallback=fallback.reshape(-1),
        )
    )
