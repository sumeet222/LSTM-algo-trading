"""Prospective S3 target/M2 math; no model fits, source mutation or new admission rule."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .hf1m_ft16_fit import quantile, robust
from .hf1m_ft16_math import rolling

HORIZONS = (1, 2, 4)


def horizon_guard(horizon: int) -> None:
    if horizon not in HORIZONS:
        raise ValueError("ONLY_DECLARED_H1_H2_H4")


def horizon_roles(
    rows: pd.DataFrame, grid: pd.DataFrame, plan: dict, valid: np.ndarray
) -> dict[str, np.ndarray]:
    """Amended independent-horizon membership; inherited input embargo/4h clock unchanged.

    `valid` contains endpoint/basis booleans only. Original four-hour *price*
    availability is never intersected into h1/h2. Its conservative calendar
    maturity cutoff remains applicable, independently of missing endpoint prices.
    """
    if rows.session_date_et.ge("2025-01-01").any() or valid.shape != (len(rows),):
        raise ValueError("S3_HISTORICAL_SOURCE_MASK_REQUIRED")
    if rows.first_step.lt(0).any():
        raise ValueError("EXACT_ORIGINAL_HISTORY_REQUIRED")
    first = grid.session_date_et.to_numpy()[rows.first_step.to_numpy(int)]
    day = rows.session_date_et.to_numpy()
    inner, stop = plan["inner_stop"], plan["refit_stop"]
    clock = {
        "inner_train": day <= inner,
        "inner_validation": (day >= plan["selection_start"]) & (day <= stop) & (first > inner),
        "refit": day <= stop,
        "oos": rows.session_date_et.str.startswith(str(plan["year"])).to_numpy() & (first > stop),
    }
    masks = {k: m & rows.source_input_eligible.to_numpy(bool) & valid for k, m in clock.items()}
    for role, mask in masks.items():
        cutoff = (
            inner
            if role == "inner_train"
            else str(plan["year"]) + "-12-31"
            if role == "oos"
            else stop
        )
        limit = pd.Timestamp(cutoff, tz="America/New_York") + pd.Timedelta(days=1)
        if not pd.to_datetime(rows.loc[mask, "label_maturity_utc"], utc=True).lt(limit).all():
            raise ValueError("CONSERVATIVE_4H_LABEL_CLOCK_VIOLATION")
    return masks


def endpoints(grid: pd.DataFrame, entries: np.ndarray, horizon: int) -> np.ndarray:
    """Advance scheduled full hours, rejecting session jumps/stubs before price lookup."""
    horizon_guard(horizon)
    if grid.session_date_et.ge("2025-01-01").any():
        raise ValueError("S3_POST2024_NUMERIC_GRID_DENIED")
    if "is_stub" in grid and grid.is_stub.any():
        raise ValueError("FULL_HOURS_ONLY")
    exits = entries + horizon
    if (entries < 0).any() or (exits >= len(grid)).any():
        raise ValueError("TARGET_OUTSIDE_SCHEDULED_GRID")
    start, end = grid.iloc[entries], grid.iloc[exits]
    if not np.array_equal(start.session_date_et.to_numpy(), end.session_date_et.to_numpy()):
        raise ValueError("NO_OVERNIGHT_TARGET")
    if not np.array_equal(
        pd.to_datetime(end.hour_end_utc, utc=True).to_numpy()
        - pd.to_datetime(start.hour_end_utc, utc=True).to_numpy(),
        np.full(len(entries), np.timedelta64(horizon, "h")),
    ):
        raise ValueError("MISSING_FULL_HOUR_OR_BAD_CALENDAR_GRID")
    return exits


def target_support(
    grid: pd.DataFrame,
    entries: np.ndarray,
    genuine: np.ndarray,
    basis: np.ndarray,
    horizon: int,
) -> np.ndarray:
    """Source-only endpoint eligibility, before computing or inspecting any return."""
    exits = endpoints(grid, entries, horizon)
    return genuine[entries] & genuine[exits] & (basis[entries] == basis[exits])


def returns_at(close: np.ndarray, entries: np.ndarray, exits: np.ndarray) -> np.ndarray:
    """Genuine source close log ratio; no proxy substitution, extra -1 or fill."""
    with np.errstate(divide="ignore", invalid="ignore"):
        value = np.log(close[exits] / close[entries])
    good = (close[entries] > 0) & (close[exits] > 0)
    return np.where(good, value, np.nan)


def historical_m2(
    grid: pd.DataFrame,
    close: np.ndarray,
    basis: np.ndarray,
    blocked: np.ndarray,
    horizon: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Exact P020 preceding-regular-day mean20/RMS60, horizon changed only.

    Same-origin type0/1, fixed scheduled regular-day windows (not compressed
    valid observations), min19/20 and57/60, max2 consecutive missing. Previous
    regular session's15:30 reference deliberately remains conservative for h1/2.
    """
    horizon_guard(horizon)
    if grid.session_date_et.ge("2025-01-01").any():
        raise ValueError("S3_POST2024_M2_DENIED")
    regular = [
        (str(day), np.asarray(pos, dtype=int))
        for day, pos in grid.groupby("session_date_et").indices.items()
        if len(pos) == 6
    ]
    days = np.array([day for day, _ in regular])
    past = np.full((len(days), close.shape[1], 2), np.nan)
    for k, (_, p) in enumerate(regular):
        for slot in (0, 1):
            good = basis[p[slot]] == basis[p[slot + horizon]]
            past[k, :, slot] = np.where(
                good, np.log(close[p[slot + horizon]] / close[p[slot]]), np.nan
            )
    previous = np.searchsorted(days, grid.session_date_et.to_numpy(), side="left") - 1
    mean = np.full((*close.shape, 2), np.nan)
    rms = mean.copy()
    good = previous >= 0
    for slot in (0, 1):
        a = rolling(past[:, :, slot], 20, 19)
        b = rolling(past[:, :, slot], 60, 57, True)
        mean[good, :, slot] = a[previous[good]]
        rms[good, :, slot] = b[previous[good]]
    mean[blocked] = np.nan
    rms[blocked] = np.nan
    references = np.full(len(grid), -1, dtype=np.int64)
    references[good] = np.array([p[5] for _, p in regular])[previous[good]]
    return mean, rms, references, past


def m2_parameters(
    mean: np.ndarray, rms: np.ndarray, unique_days: np.ndarray
) -> tuple[np.ndarray, dict, np.ndarray]:
    """P020 M2-only balanced floor/scale recipe; S3 preflight calls on SYN only."""
    floors = []
    for j in range(mean.shape[1]):
        vals, weights = [], []
        for slot in (0, 1):
            v = rms[unique_days, j, slot]
            v = v[np.isfinite(v) & (v > 0)]
            if not len(v):
                raise ValueError("BOTH_M2_ORIGINS_REQUIRED")
            vals.append(v)
            weights.append(np.full(len(v), 0.5 / len(v)))
        floors.append(quantile(np.concatenate(vals), 0.05, np.concatenate(weights)))
    floor = np.array(floors)
    native = mean / np.maximum(rms, floor[None, :, None])
    vals, weights = [], []
    for slot in (0, 1):
        v = native[unique_days, :, slot]
        v = v[np.isfinite(v)]
        if not len(v):
            raise ValueError("M2_TRAIN_POPULATION_REQUIRED")
        vals.append(v)
        weights.append(np.full(len(v), 0.5 / len(v)))
    scale = robust(np.concatenate(vals), np.concatenate(weights))
    return floor, scale, scale_m2(mean, rms, floor, scale)


def scale_m2(mean: np.ndarray, rms: np.ndarray, floors: np.ndarray, scale: dict) -> np.ndarray:
    native = mean / np.maximum(rms, floors[None, :, None])
    filled = np.where(np.isfinite(native), native, scale["center"])
    return ((filled - scale["center"]) / scale["scale"]).astype(np.float32)


def target_parameters(
    returns: np.ndarray, epsilon_mask: np.ndarray, scale_mask: np.ndarray
) -> dict:
    """Exact ranking-fold P020 epsilon/T2 rule; no outer data or new quantile rule."""
    if not epsilon_mask.any() or not scale_mask.any():
        raise ValueError("NONEMPTY_TRAIN_ONLY_TARGET_POPULATIONS_REQUIRED")
    r = returns[epsilon_mask]
    if not np.isfinite(r).all():
        raise ValueError("COMPLETE20_TARGET_REQUIRED")
    mad = np.median(abs(r - np.median(r, axis=1)[:, None]), axis=1)
    epsilon = max(1e-4, 0.1 * float(np.median(mad)))
    r = returns[scale_mask]
    med = np.median(r, axis=1)
    d = np.median(abs(r - med[:, None]), axis=1)
    y = (r - med[:, None]) / (d[:, None] + epsilon)
    return dict(epsilon=epsilon, t2_scale=max(float(np.median(abs(y))), 1e-6))


def substitute_m2(x: np.ndarray, rows: pd.DataFrame, scaled_m2: np.ndarray) -> np.ndarray:
    """Replace index1 only, preserving original15 channels and48×16 shape bitwise."""
    result = x.copy()
    history = rows.first_step.to_numpy(int)[:, None] + np.arange(48)
    slot = (
        pd.to_datetime(rows.entry_end_utc, utc=True)
        .dt.tz_convert("America/New_York")
        .dt.hour.to_numpy()
        - 10
    )
    result[:, :, :, 1] = scaled_m2[history, :, slot[:, None]].transpose(0, 2, 1)
    np.testing.assert_array_equal(result[..., np.arange(16) != 1], x[..., np.arange(16) != 1])
    return result
