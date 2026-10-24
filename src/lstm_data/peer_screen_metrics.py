"""Independent P027 transformed-objective accounting and matched forecast evidence."""

from __future__ import annotations

import numpy as np
import pandas as pd
import torch

from .branch_replication_followup import month_counts
from .config import fingerprint
from .objective_screen_audit import origin_ic
from .objective_screen_diagnostics import daily_scores
from .objective_screen_metrics import equal_weights, regression
from .optimization_screen_supplement import forecast_profile


def allocation(frame: pd.DataFrame, scale: float) -> pd.DataFrame:
    """Allocate the actual float32 z objective with exact float64 population weights."""
    f = frame.copy().reset_index(drop=True)
    y = f.TG20.to_numpy(dtype=np.float64)
    raw = f.raw_net_output.to_numpy(dtype=np.float32).copy()
    z32 = torch.asinh(torch.from_numpy(y.astype(np.float32)) / scale)
    loss = (torch.from_numpy(raw) - z32).square().numpy().astype(float)
    oracle = (raw.astype(float) - np.arcsinh(y.astype(np.float32).astype(float) / scale)) ** 2
    np.testing.assert_allclose(loss, oracle, rtol=3e-5, atol=2e-6)
    w = equal_weights(f.session_date_et.to_numpy())
    f["z"] = np.arcsinh(y / scale)
    f["ordinary_weight"] = w
    f["normalized_weight"] = w
    f["raw"] = loss
    f["coefficient"] = 1.0
    f["total"] = loss * w
    f["pointwise"] = f.total
    f["pairwise"] = 0.0
    f["equivalent_row_loss"] = loss
    np.testing.assert_allclose(w.sum(), 1, rtol=0, atol=1e-14)
    independent = (
        pd.DataFrame(dict(day=f.session_date_et, loss=loss)).groupby("day").loss.mean().mean()
    )
    np.testing.assert_allclose(f.total.sum(), independent, rtol=0, atol=1e-14)
    return f


def metrics(f: pd.DataFrame, training: pd.DataFrame) -> dict:
    y = f.TG20.to_numpy(dtype=float)
    p = f.pred_original_TG20.to_numpy(dtype=float)
    days = f.session_date_et.to_numpy()
    result = regression(y, p, days)
    result.update(forecast_profile(f))
    result["optimized_z_mse"] = float(f.total.sum())
    result["origin_ic_mean"] = (
        float(np.nanmean(origin_ic(p, y))) if result["defined_ic_days"] else None
    )
    result["target_zero_rows"] = int((y == 0).sum())
    result["prediction_zero_rows"] = int((p == 0).sum())
    result["sign_tie_rule"] = "sign(y)==sign(pred); zero matches zero only; report zero counts"
    thresholds = {
        str(q): float(np.quantile(abs(training.TG20.to_numpy()), q)) for q in (0.95, 0.99)
    }
    events = []
    w = equal_weights(days)
    for q, threshold in thresholds.items():
        for side, truth, called in [
            ("ABS", abs(y) > threshold, abs(p) > threshold),
            ("POS", y > threshold, p > threshold),
            ("NEG", y < -threshold, p < -threshold),
        ]:
            mass = float(w[truth].sum())
            events.append(
                dict(
                    quantile=q,
                    side=side,
                    threshold=threshold,
                    rows=int(truth.sum()),
                    recall=float(w[truth & called].sum() / mass) if mass else None,
                    conditional_mse=float(w[truth] @ ((p[truth] - y[truth]) ** 2) / mass)
                    if mass
                    else None,
                )
            )
    result["events"] = events
    result["event_threshold_fit"] = "fitting-prefix unweighted unique target row quantile; strict >"
    return result


def paired(f: pd.DataFrame, baseline: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    """Identical complete panels; aggregate origin ranks per day before month resampling."""
    if not f[["origin_id", "ticker", "TG20"]].equals(baseline[["origin_id", "ticker", "TG20"]]):
        raise ValueError("P027_MATCHED_BASELINE_ROWS")
    a = daily_scores(f, f.pred_original_TG20.to_numpy(), True).set_index("session_date_et")
    b = daily_scores(baseline, baseline.pred_original_TG20.to_numpy(), True).set_index(
        "session_date_et"
    )
    if not a.index.equals(b.index):
        raise ValueError("P027_PAIRED_DAYS")
    d = (a[["mse", "ic"]] - b[["mse", "ic"]]).reset_index()
    intervals = []
    occupancy = []
    days = d.session_date_et.to_numpy()
    own_ic = origin_ic(f.pred_original_TG20.to_numpy(), f.TG20.to_numpy())
    base_ic = origin_ic(baseline.pred_original_TG20.to_numpy(), baseline.TG20.to_numpy())
    valid_origin = np.isfinite(own_ic) & np.isfinite(base_ic)
    origin_days = f.session_date_et.to_numpy()[::20]
    origin_delta = pd.DataFrame(
        dict(day=origin_days[valid_origin], delta=(own_ic - base_ic)[valid_origin])
    )
    joint = (
        origin_delta.groupby("day").delta.agg(["sum", "count"]).reindex(d.session_date_et).fillna(0)
    )
    origin_counts = joint["count"].to_numpy()
    origin_values = np.divide(
        joint["sum"].to_numpy(),
        origin_counts,
        out=np.full(len(joint), np.nan),
        where=origin_counts > 0,
    )
    for size in (1, 2):
        counts = month_counts(days, size)
        month_labels = np.asarray([str(day)[:7] for day in days])
        month_draws = np.column_stack(
            [
                counts[:, np.flatnonzero(month_labels == month)[0]]
                for month in sorted(set(month_labels))
            ]
        )
        occupancy.append(
            dict(
                block_months=size,
                replicates=400,
                seed=22042,
                calendar_months=sorted(set(month_labels)),
                occupied_month_min=int((month_draws > 0).sum(1).min()),
                occupied_month_max=int((month_draws > 0).sum(1).max()),
                resampled_session_min=int(counts.sum(1).min()),
                resampled_session_max=int(counts.sum(1).max()),
                session_multiplicity_sha256=fingerprint(counts.tolist()),
            )
        )
        for key in ("mse", "ic", "origin_ic"):
            v = origin_values if key == "origin_ic" else d[key].to_numpy(dtype=float)
            valid = np.isfinite(v)
            weights = counts * origin_counts if key == "origin_ic" else counts
            denominator = weights[:, valid].sum(1)
            draws = np.divide(
                weights[:, valid] @ v[valid],
                denominator,
                out=np.full(400, np.nan),
                where=denominator > 0,
            )
            intervals.append(
                dict(
                    metric=key,
                    block_months=size,
                    seed=22042,
                    replicates=400,
                    delta=float(np.average(v[valid], weights=origin_counts[valid]))
                    if key == "origin_ic" and valid.any()
                    else float(np.nanmean(v))
                    if valid.any()
                    else None,
                    interval=np.nanquantile(draws, [0.025, 0.975]).tolist()
                    if valid.any()
                    else [None, None],
                )
            )
    return dict(
        intervals=intervals,
        block_occupancy=occupancy,
        defined_origin_pairs=int(valid_origin.sum()),
        candidate_defined_origins=int(np.isfinite(own_ic).sum()),
        comparator_defined_origins=int(np.isfinite(base_ic).sum()),
        undefined_IC_policy=(
            "No zero imputation. Origin deltas use jointly defined within20 origin pairs; "
            "daily deltas use jointly defined daily statistics. Only the IC statistic "
            "is conditional, never the model/evaluation population."
        ),
        interpretation=(
            "candidate minus T2/42; MSE negative better, IC positive better; "
            "exploratory block sensitivity, reused development"
        ),
    ), d


def heterogeneity(f: pd.DataFrame) -> pd.DataFrame:
    """Descriptive conditional moments and time-rank association; keep weights explicit."""
    rows = []
    for dimension in (
        "ticker",
        "sector_context",
        "year",
        "era",
        "month",
        "quality",
        "fallback_state",
        "V1_state",
    ):
        if dimension not in f:
            continue
        for value, g in f.groupby(dimension, dropna=False):
            y = g.TG20.to_numpy(dtype=float)
            p = g.pred_original_TG20.to_numpy(dtype=float)
            w = g.ordinary_weight.to_numpy(dtype=float)
            mass = w.sum()
            rows.append(
                dict(
                    dimension=dimension,
                    value=str(value),
                    rows=len(g),
                    weight_mass=mass,
                    mse=float(w @ ((p - y) ** 2) / mass),
                    objective=float(g.total.sum() / mass),
                    prediction_sd=float(np.sqrt(w @ ((p - w @ p / mass) ** 2) / mass)),
                    time_rank_association=float(
                        np.corrcoef(pd.Series(y).rank().to_numpy(), pd.Series(p).rank().to_numpy())[
                            0, 1
                        ]
                    )
                    if np.std(p) > 0 and np.std(y) > 0
                    else np.nan,
                    ic_semantics="within-slice time/row association; not cross-sectional day IC",
                )
            )
    return pd.DataFrame(rows)
