"""P025 matched saved-seed comparisons; no refitting, threshold selection or trading."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .branch_replication_metrics import corrected, event_metrics, paired_month_blocks, qr_metrics
from .branch_replication_spec import P022, P023
from .objective_screen_audit import average_precision
from .objective_screen_diagnostics import canonical
from .objective_screen_loss import classes
from .objective_screen_metrics import equal_weights


def baseline_path(arm: str, role: str) -> Path:
    if arm == "E1":
        return P022 / "collective_diagnostics_v2/E1" / role / "population.parquet"
    if arm == "QR1":
        return P023 / "QR1_diagnostics_v1" / role / "population.parquet"
    raise ValueError("P025_ARM")


def comparison(f: pd.DataFrame, arm: str, role: str, recipe: dict) -> tuple[dict, pd.DataFrame]:
    old = canonical(pd.read_parquet(baseline_path(arm, role)), f)
    days = f.session_date_et.to_numpy()
    if not np.array_equal(days, old.session_date_et.to_numpy()):
        raise ValueError("P025_MATCHED_DAYS")
    result: dict = dict(
        arm=arm,
        role=role,
        rows=len(f),
        origins=f.origin_id.nunique(),
        sessions=len(set(days)),
        weights="equal session, eligible origin,20 stocks",
        scope="exploratory matched development",
    )
    daily = pd.DataFrame(dict(day=days))
    if arm == "E1":
        y = f.TG20.to_numpy(dtype=float)
        label = classes(y, recipe["q95_abs_y"])
        a = f[["p_NEG", "p_NORMAL", "p_POS"]].to_numpy(dtype=float)
        b = old[["p_NEG", "p_NORMAL", "p_POS"]].to_numpy(dtype=float)
        metrics42, _ = event_metrics(old, recipe)
        result["seed42_raw"] = metrics42
        result["seed42_analytical_inverse_weight"] = event_metrics(old, recipe, inverse=True)[0]
        for name, p, q in (
            ("raw", a, b),
            ("inverse_weight", corrected(a, recipe), corrected(b, recipe)),
        ):
            ce_a = -np.log(np.maximum(p[np.arange(len(f)), label], np.finfo(float).tiny))
            ce_b = -np.log(np.maximum(q[np.arange(len(f)), label], np.finfo(float).tiny))
            truth = np.eye(3)[label]
            daily[name + "_CE_difference_123_minus_42"] = ce_a - ce_b
            daily[name + "_Brier_difference_123_minus_42"] = ((p - truth) ** 2).sum(axis=1) - (
                (q - truth) ** 2
            ).sum(axis=1)
            for k, event in ((-1, "ANY"), (0, "NEG"), (2, "POS")):
                actual = label != 1 if k == -1 else label == k
                score_a = p[:, 0] + p[:, 2] if k == -1 else p[:, k]
                score_b = q[:, 0] + q[:, 2] if k == -1 else q[:, k]

                def delta(indices, pseudo):
                    w = equal_weights(pseudo)
                    return average_precision(
                        actual[indices], score_a[indices], w
                    ) - average_precision(actual[indices], score_b[indices], w)

                key = name + "_" + event + "_AP_difference_123_minus_42"
                result[key] = float(delta(np.arange(len(f)), days))
                if role == "development":
                    result[key + "_month_blocks"] = paired_month_blocks(days, delta)
    else:
        result["seed42"] = qr_metrics(old, recipe)
        q_a = f[["quantiles_z_05", "quantiles_z_50", "quantiles_z_95"]].to_numpy(dtype=float)
        q_b = old[["quantiles_z_05", "quantiles_z_50", "quantiles_z_95"]].to_numpy(dtype=float)
        z = np.arcsinh(f.TG20.to_numpy() / recipe["scale"])
        tau = np.array([0.05, 0.5, 0.95])
        ea, eb = z[:, None] - q_a, z[:, None] - q_b
        loss_a = np.maximum(tau * ea, (tau - 1) * ea).mean(axis=1)
        loss_b = np.maximum(tau * eb, (tau - 1) * eb).mean(axis=1)
        daily["pinball_difference_123_minus_42"] = loss_a - loss_b
        e0 = z[:, None] - np.asarray(recipe["quantiles_z"])
        daily["pinball_difference_123_minus_unconditional"] = loss_a - np.maximum(
            tau * e0, (tau - 1) * e0
        ).mean(axis=1)
    means = daily.groupby("day").mean()
    result["paired_daily_means"] = means.mean().to_dict()
    if role == "development":
        for column in means:
            values = daily[str(column)].to_numpy()

            def difference(indices, pseudo):
                return float(equal_weights(pseudo) @ values[indices])

            result[str(column) + "_month_blocks"] = paired_month_blocks(days, difference)
    result["interpretation"] = (
        "Negative proper-loss difference favors seed123; AP differences favor seed123 "
        "when positive. Exploratory dependent-day block intervals; "
        "no significance or promotion claim."
    )
    return result, means.reset_index()


def heterogeneity(f: pd.DataFrame) -> pd.DataFrame:
    """Conserved actual-objective shares by stock/year/era and released quality flags."""
    groups = [("ticker", str(k), g.index.to_numpy()) for k, g in f.groupby("ticker")]
    groups.extend(
        ("year", str(k), g.index.to_numpy()) for k, g in f.groupby(f.session_date_et.str[:4])
    )
    for name, a, b in (
        ("2011-2015", "2011", "2015"),
        ("2016-2020", "2016", "2020"),
        ("2021-2025", "2021", "2025"),
    ):
        mask = f.session_date_et.str[:4].between(a, b)
        groups.append(("era", name, np.flatnonzero(mask)))
    for column in f:
        if pd.api.types.is_bool_dtype(f[column]) and any(
            x in str(column) for x in ("volume", "proxy", "fallback", "quality")
        ):
            for value in (True, False):
                groups.append(
                    (str(column), str(value), np.flatnonzero(f[column].to_numpy() == value))
                )
    result = []
    for kind, label, indices in groups:
        g = f.iloc[indices]
        mass = float(g.ordinary_weight.sum())
        result.append(
            dict(
                kind=kind,
                group=label,
                rows=len(g),
                origins=g.origin_id.nunique(),
                sessions=g.session_date_et.nunique(),
                weight_mass=mass,
                actual_objective_share=float(g.total.sum() / f.total.sum()),
                objective_contribution=float(g.total.sum()),
                conditional_equivalent_loss=float(g.total.sum() / mass) if mass else np.nan,
            )
        )
    return pd.DataFrame(result)
