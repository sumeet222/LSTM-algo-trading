"""Descriptive FT0 diagnostics; no estimated parameter is applied to research inputs."""

from __future__ import annotations

import numpy as np
import pandas as pd

QUANTILES = (0.001, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 0.999)
Q_NAMES = ("p0_1", "p1", "p5", "p25", "median", "p75", "p95", "p99", "p99_9")
THRESHOLDS = (3, 5, 10, 20)


def distribution(values: np.ndarray, bounded: bool = False) -> dict:
    """Signed and magnitude quantiles, population SD and explicitly descriptive rates."""
    data = np.asarray(values, dtype=float)
    finite = data[np.isfinite(data)]
    result: dict = dict(
        observed=len(data),
        valid=len(finite),
        missing=int(np.isnan(data).sum()),
        nonfinite=int(np.isinf(data).sum()),
    )
    if not len(finite):
        return result
    q = np.quantile(finite, QUANTILES)
    a = np.quantile(np.abs(finite), QUANTILES)
    _, counts = np.unique(finite, return_counts=True)
    iqr, center = float(q[5] - q[3]), float(q[4])
    result.update(dict(zip(Q_NAMES, q)))
    result.update({"abs_" + key: value for key, value in zip(Q_NAMES, a)})
    result.update(
        min=float(finite.min()),
        max=float(finite.max()),
        unique=len(counts),
        constant_rate=float(counts.max() / len(finite)),
        mean=float(finite.mean()),
        std=float(finite.std(ddof=0)),
        MAD=float(np.median(np.abs(finite - center))),
        IQR=iqr,
        bowley_skew=float((q[5] + q[3] - 2 * center) / iqr) if iqr else None,
        near_zero_rate=float(np.mean(np.abs(finite) <= 1e-8)),
    )
    for limit in THRESHOLDS:
        n = int(np.sum(np.abs(finite) > limit))
        result[f"abs_gt_{limit}_count"] = n
        result[f"abs_gt_{limit}_rate"] = n / len(finite)
    if bounded:
        result.update(
            bound_violations=int(np.sum(np.abs(finite) > 1)),
            abs_ge_095_rate=float(np.mean(np.abs(finite) >= 0.95)),
            minus1_rate=float(np.mean(finite == -1)),
            plus1_rate=float(np.mean(finite == 1)),
        )
    return result


def clipping_collisions(values: np.ndarray, keys: pd.DataFrame, limit: int) -> dict:
    """Counterfactual collisions only; never return a transformed research feature."""
    finite = np.isfinite(values)
    x = np.asarray(values)[finite]
    k = keys.loc[finite].copy()
    k["value"] = x
    before = len(np.unique(x))
    after = len(np.unique(np.clip(x, -limit, limit)))
    wide = k.pivot(index=["timestamp", "origin"], columns="symbol", values="value")
    complete = wide.notna().all(axis=1) if wide.shape[1] == 5 else np.zeros(len(wide), dtype=bool)
    v = wide.loc[complete].to_numpy()
    left, right = np.triu_indices(5, 1)
    distinct = v[:, left] != v[:, right] if v.shape[1] == 5 else np.empty((0, 10), dtype=bool)
    clipped = np.clip(v, -limit, limit)
    lost = int(np.sum(distinct & (clipped[:, left] == clipped[:, right]))) if v.shape[1] == 5 else 0
    pairs = int(np.sum(distinct))
    return dict(
        hypothetical_clip=limit,
        unique_before=before,
        unique_after=after,
        unique_lost=before - after,
        cross_stock_distinct_pairs=pairs,
        cross_stock_pairs_lost=lost,
        lost_pair_rate=lost / pairs if pairs else None,
        incomplete_cross_sections=int(len(wide) - np.sum(complete)),
        ordering_reversals=0,
        interpretation="Monotone clipping creates ties, no reversals",
    )


def independent_scaler_check(
    values: np.ndarray, origins: np.ndarray | None, center: float, scale: float, method: str
) -> dict:
    """Read-only verification of recorded fit statistics; creates no scaler object."""
    x = np.asarray(values, dtype=float)
    weights = np.ones(len(x), dtype=float)
    if origins is not None:
        weights = np.asarray([0.5 / np.sum(origins == o) for o in origins])
    weights /= weights.sum()

    def quantile(data: np.ndarray, q: float) -> float:
        if origins is None:
            return float(np.quantile(data, q))
        order = np.argsort(data, kind="stable")
        sorted_x, cdf = data[order], weights[order].cumsum()
        index = min(int(np.searchsorted(cdf, q, side="left")), len(data) - 1)
        if index + 1 < len(data) and np.isclose(cdf[index], q, rtol=1e-9, atol=1e-12):
            return float((sorted_x[index] + sorted_x[index + 1]) / 2)
        return float(sorted_x[index])

    median = quantile(x, 0.5)
    mad = quantile(np.abs(x - median), 0.5)
    iqr = (quantile(x, 0.75) - quantile(x, 0.25)) / 1.349
    sd = float(np.sqrt(np.sum(weights * (x - np.sum(weights * x)) ** 2)))
    if mad > 0:
        expected, expected_method = mad, "MAD"
    elif iqr > 0:
        expected, expected_method = iqr, "IQR_1.349"
    elif sd > 0:
        expected, expected_method = sd, "AUDITED_POPULATION_SD"
    else:
        expected, expected_method = 1.0, "CONSTANT"
    return dict(
        recorded_center=center,
        recorded_scale=scale,
        method=method,
        diagnostic_median=median,
        diagnostic_MAD=mad,
        diagnostic_IQR_1_349=iqr,
        diagnostic_population_SD=sd,
        diagnostic_method=expected_method,
        center_error=abs(center - median),
        scale_error=abs(scale - expected),
        passed=bool(
            np.isclose(center, median, rtol=1e-12, atol=1e-14)
            and np.isclose(scale, expected, rtol=1e-12, atol=1e-14)
            and method == expected_method
        ),
    )
