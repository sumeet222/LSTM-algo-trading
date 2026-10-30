"""Fixed same-target classical estimators; no source access or neural fitting."""

from __future__ import annotations

import math

import numpy as np


def deoverlap(starts: np.ndarray, ends: np.ndarray) -> np.ndarray:
    """Greedy chronological intervals; decisions depend only on earlier endpoints."""
    if len(starts) != len(ends) or (ends <= starts).any() or (np.diff(starts) < 0).any():
        raise ValueError("INVALID_INTERVAL_SEQUENCE")
    retained = np.zeros(len(starts), bool)
    last = None
    for n, (start, end) in enumerate(zip(starts, ends)):
        if last is None or start >= last:
            retained[n] = True
            last = end
    return retained


def folded_normal(mu: np.ndarray, variance: np.ndarray) -> np.ndarray:
    """Gaussian absolute expectation, including the deterministic zero-sigma limit."""
    mu, variance = np.broadcast_arrays(np.asarray(mu, float), np.asarray(variance, float))
    if not np.isfinite(mu).all() or not np.isfinite(variance).all() or (variance < 0).any():
        raise ValueError("INVALID_NORMAL_PARAMETERS")
    sigma = np.sqrt(variance)
    result = abs(mu).copy()
    active = sigma > 0
    a = abs(mu[active]) / sigma[active]
    erf = np.asarray([math.erf(float(x) / math.sqrt(2)) for x in a.ravel()]).reshape(a.shape)
    result[active] = (
        sigma[active] * math.sqrt(2 / math.pi) * np.exp(-a * a / 2) + abs(mu[active]) * erf
    )
    return result


def ewma(state: np.ndarray, observation: np.ndarray) -> np.ndarray:
    """One observed same-slot session update, never one elapsed-hour update."""
    return 0.94 * state + 0.06 * observation


def multiplier(a: np.ndarray, pred: np.ndarray, weights: np.ndarray) -> dict:
    """One out-of-fit raw-A least-squares multiplier with no fallback."""
    if not all(np.isfinite(x).all() for x in [a, pred, weights]):
        raise ValueError("NONFINITE_CALIBRATION")
    if (pred < 0).any() or (a < 0).any() or (weights <= 0).any():
        raise ValueError("INVALID_CALIBRATION")
    w = weights / weights.sum()
    den, num = float(w @ pred**2), float(w @ (a * pred))
    if not np.isfinite(den) or den <= 0:
        raise ValueError("CALIBRATION_DENOMINATOR")
    return dict(k=max(0.0, num / den), numerator=num, denominator=den)


def rv_value(close: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """390 scheduled positions; absent closes never create bridged returns."""
    if close.shape[-1] != 390:
        raise ValueError("FULL_SESSION_390_REQUIRED")
    observed = np.isfinite(close) & (close > 0)
    pairs = observed[..., 1:] & observed[..., :-1]
    safe = np.where(observed, close, 1.0)
    r = np.diff(np.log(safe), axis=-1)
    count = pairs.sum(-1)
    value = np.divide(
        389 * (r**2 * pairs).sum(-1),
        count,
        out=np.full(count.shape, np.nan),
        where=count >= math.ceil(0.95 * 389),
    )
    return value, count


def har_features(
    rv: np.ndarray,
    dates: np.ndarray,
    origin_dates: np.ndarray,
    medians: np.ndarray,
    floors: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Prior 1/5/22 regular-session RV logs and missing fractions, stockwise."""
    ends = np.searchsorted(dates, origin_dates, side="left")
    if (ends < 22).any():
        raise ValueError("INSUFFICIENT_22_REGULAR_SESSION_HISTORY")
    blocks = rv[ends[:, None] - np.arange(1, 23)]
    missing = ~np.isfinite(blocks)
    filled = np.where(missing, medians[None, None, :], blocks)
    values = [np.log(np.maximum(filled[:, :n].mean(1), floors)) for n in [1, 5, 22]]
    values += [missing[:, :n].mean(1) for n in [1, 5, 22]]
    x = np.stack(values, axis=-1)
    assert np.isfinite(x).all() and (dates[ends - 1] < origin_dates).all()
    return x, missing.mean(1)


def ridge_fit(x: np.ndarray, y: np.ndarray, w: np.ndarray) -> dict:
    """Weighted mean squared response loss plus .01 slope L2, free intercept."""
    w = w / w.sum()
    center = w @ x
    scale = np.sqrt(w @ ((x - center) ** 2))
    scale[scale == 0] = 1
    z = np.column_stack([np.ones(len(x)), (x - center) / scale])
    gram = z.T @ (w[:, None] * z) + np.diag([0.0] + [0.01] * x.shape[1])
    beta = np.linalg.solve(gram, z.T @ (w * y))
    return dict(
        center=center.tolist(),
        scale=scale.tolist(),
        beta=beta.tolist(),
        condition=float(np.linalg.cond(gram)),
    )


def ridge_predict(x: np.ndarray, fit: dict, scale: float) -> np.ndarray:
    """Frozen prefix standardization and one nonnegative raw-magnitude decode."""
    z = np.column_stack(
        [np.ones(len(x)), (x - np.asarray(fit["center"])) / np.asarray(fit["scale"])]
    )
    return scale * np.maximum(0, z @ np.asarray(fit["beta"]))
