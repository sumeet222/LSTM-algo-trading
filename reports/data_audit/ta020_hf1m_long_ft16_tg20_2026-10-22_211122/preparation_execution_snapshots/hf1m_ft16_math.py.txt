"""Causal new-source components; no labels, fitted statistics, or protected rows."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .hf1m_action_audit import SYMBOLS
from .hf1m_ft16_source import BARRIER
from .stock_features import IndicatorState


def rolling(values: np.ndarray, n: int, minimum: int, square: bool = False) -> np.ndarray:
    """FT1 scheduled-position means/RMS, max2 consecutive misses, no time compression."""
    f = pd.DataFrame(values)
    triples = f.isna().rolling(3, min_periods=3).sum().eq(3)
    gaps = triples.rolling(max(1, n - 2), min_periods=1).max().astype(bool)
    r = (f**2 if square else f).rolling(n, min_periods=minimum).mean()
    r.iloc[: n - 1] = np.nan
    a = r.mask(gaps).to_numpy(dtype=float, copy=True)
    return np.sqrt(a) if square else a


def regime_rolling(values: np.ndarray, basis: np.ndarray, n: int, minimum: int) -> np.ndarray:
    """A rolling ratio may use only one known price/share-unit regime."""
    a = rolling(values, n, minimum)
    for j in range(a.shape[1]):
        for i in range(n - 1, len(a)):
            if basis[i - n + 1, j] != basis[i, j]:
                a[i, j] = np.nan
    return a


def volume_fields(hours: pd.DataFrame, maximum: int = 5) -> pd.DataFrame:
    """Absent-minute zeros change computation only; all sums remain source lower bounds."""
    result = hours[["hour_id", "ticker", "session_date_et"]].copy()
    result["observed_volume_sum"] = hours.observed_volume.to_numpy()
    result["assumed_zero_missing_count"] = hours.missing_count.to_numpy()
    result["quarantine_volume_unknown_count"] = (
        hours.quarantine_count + hours.conflict_count + hours.invalid_minutes
    ).to_numpy()
    result["observed_minute_fraction"] = (hours.genuine_count / hours.expected_minutes).to_numpy()
    result["source_volume_observed"] = hours.observed_volume_complete.to_numpy()
    result["volume_missing_assumed_zero"] = hours.missing_count.gt(0).to_numpy()
    result["hourly_volume_lower_bound"] = ~hours.observed_volume_complete.to_numpy()
    good = (
        hours.genuine_count.gt(0)
        & hours.missing_count.le(maximum)
        & hours.longest_gap_minutes.le(maximum)
        & hours.conflict_count.eq(0)
        & hours.quarantine_count.eq(0)
        & hours.invalid_minutes.eq(0)
    )
    result["volume_usable_for_feature"] = good.to_numpy()
    result["volume_for_feature"] = hours.observed_volume.where(good).to_numpy()
    result["volume_quality_tier"] = np.where(
        good,
        np.where(hours.observed_volume_complete, "OBSERVED_COMPLETE", "ABSENT_ZERO_LOWER_BOUND"),
        "UNKNOWN_OR_SEVERE_MASKED",
    )
    return result


@dataclass
class Components:
    grid: pd.DataFrame
    hours: pd.DataFrame
    source: dict[str, np.ndarray]
    values: dict[str, np.ndarray]
    regular_days: np.ndarray
    daily_close: np.ndarray
    daily_volume: np.ndarray
    daily_basis: np.ndarray
    hourly_volume_basis: np.ndarray
    m2_mean: np.ndarray
    m2_rms: np.ndarray
    m2_reference_end: np.ndarray
    day_index: np.ndarray
    volume: pd.DataFrame


def build(hours: pd.DataFrame, field_masks: pd.DataFrame, maximum: int = 5) -> Components:
    """Hourly source-only math, preceding-day M2 locked to matured historical endpoints."""
    if hours.session_date_et.ge(BARRIER).any():
        raise ValueError("P020_PROTECTED_FEATURE_DENIED")
    h = hours.loc[~hours.is_stub].copy()
    grid = h[["hour_start_utc", "hour_end_utc", "session_date_et"]].drop_duplicates()
    grid = grid.sort_values("hour_start_utc").reset_index(drop=True)
    if len(h) != len(grid) * 20 or h.hour_id.duplicated().any():
        raise ValueError("SCHEDULED20_GRID_REQUIRED")
    volume = volume_fields(h, maximum)
    h["volume_for_feature"] = volume.volume_for_feature.to_numpy()
    fields = field_masks.set_index("hour_id")
    h["volume_basis_id"] = h.hour_id.map(fields.volume_basis_id)
    h["cop_dependency"] = h.hour_id.map(fields.hour_feature_dependency_action_crossing)

    def matrix(name: str) -> np.ndarray:
        return (
            h.pivot(index="hour_start_utc", columns="ticker", values=name)
            .reindex(index=grid.hour_start_utc, columns=SYMBOLS)
            .to_numpy()
        )

    s = {
        f: matrix(f).astype(float)
        for f in [
            "open",
            "high",
            "low",
            "close",
            "close_input_cap5",
            "volume_for_feature",
            "missing_count",
            "quarantine_count",
            "conflict_count",
            "proxy_count",
        ]
    }
    basis = matrix("price_basis_id")
    vb = matrix("volume_basis_id")
    close = s["close_input_cap5"]
    v: dict[str, np.ndarray] = {}
    v["OC"] = np.log(close / s["open"])
    v["RMS12"] = rolling(v["OC"], 12, 12, True)
    v["RMS60"] = rolling(v["OC"], 60, 57, True)
    v["B1"] = np.log(s["high"] / s["low"])
    width = s["high"] - s["low"]
    v["B2"] = np.divide(
        2 * close - s["high"] - s["low"], width, out=np.zeros_like(close), where=width != 0
    )
    v["B2"][~np.isfinite(width)] = np.nan
    # A bounded proxy close can lie outside the observed range; do not clip to fabricate location.
    v["B2"][np.abs(v["B2"]) > 1 + 1e-10] = np.nan
    regular = [
        (str(d), np.asarray(p, dtype=int))
        for d, p in grid.groupby("session_date_et").indices.items()
        if len(p) == 6
    ]
    days = np.asarray([d for d, _ in regular])
    dc = np.full((len(days), 20), np.nan)
    dv = np.full_like(dc, np.nan)
    db = np.empty(dc.shape, dtype=object)
    price_db = np.empty(dc.shape, dtype=object)
    past = np.full((len(days), 20, 2), np.nan)
    for d, (_, p) in enumerate(regular):
        dc[d] = s["close"][p[-1]]  # Independent genuine15:30, never a stub or older close.
        price_db[d] = basis[p[-1]]
        db[d] = vb[p[-1]]
        compatible = (vb[p] == vb[p[-1]]).all(axis=0)
        dv[d] = np.where(
            np.isfinite(s["volume_for_feature"][p]).all(axis=0) & compatible,
            s["volume_for_feature"][p].sum(axis=0),
            np.nan,
        )
        for o in (0, 1):
            good = basis[p[o]] == basis[p[o + 4]]
            past[d, :, o] = np.where(good, np.log(s["close"][p[o + 4]] / s["close"][p[o]]), np.nan)
    dr = np.log(dc / pd.DataFrame(dc).shift(1).to_numpy())
    for d in range(1, len(days)):
        dr[d, price_db[d] != price_db[d - 1]] = np.nan
    daily = {
        "RMS63": rolling(dr, 63, 60, True),
        "MOM5": np.log(dc / pd.DataFrame(dc).shift(5).to_numpy()),
        "MOM105": np.log(
            pd.DataFrame(dc).shift(20).to_numpy() / pd.DataFrame(dc).shift(125).to_numpy()
        ),
        "SMA20": regime_rolling(dc, price_db, 20, 19),
        "T2": rolling(np.sign(dr), 20, 19),
        "Q2_5": regime_rolling(dv, db, 5, 5),
        "Q2_60": regime_rolling(dv, db, 60, 57),
    }
    previous = np.searchsorted(days, grid.session_date_et.to_numpy(), side="left") - 1
    for name, a in daily.items():
        target = np.full_like(close, np.nan)
        good = previous >= 0
        target[good] = a[previous[good]]
        v[name] = target
    v["VOLUME_H"] = s["volume_for_feature"]
    v["T1"] = np.log(close / v["SMA20"])
    v["Q1_MEAN"] = np.full_like(close, np.nan)
    # Slot determined from actual XNYS session grid; half-day full hours retain their true slot.
    grid["slot"] = grid.groupby("session_date_et").cumcount()
    for positions in grid.groupby("slot").indices.values():
        p = np.asarray(positions, dtype=int)
        lag = pd.DataFrame(s["volume_for_feature"][p]).shift(1).to_numpy()
        a = regime_rolling(lag, vb[p], 20, 19)
        for k in range(20, len(p)):
            a[k, vb[p[k - 20]] != vb[p[k]]] = np.nan
        v["Q1_MEAN"][p] = a
    for name in ["T3", "T4", "T5"]:
        v[name] = np.full_like(close, np.nan)
    recent = np.isfinite(rolling(close, 72, 69))
    for j in range(20):
        state = IndicatorState()
        gap = 0
        for i in range(len(grid)):
            if i and basis[i, j] != basis[i - 1, j]:
                state = IndicatorState()
            value = float(close[i, j])
            good = np.isfinite(value)
            gap = 0 if good else gap + 1
            if gap >= 3:
                state = IndicatorState()
            state.update(value if good else None)
            if good and recent[i, j]:
                if state.ema_updates >= 360:
                    v["T3"][i, j] = (state.emas[6] - state.emas[18]) / value
                    v["T4"][i, j] = (state.emas[24] - state.emas[72]) / value
                r = state.normalized_rsi()
                if r is not None:
                    v["T5"][i, j] = r
    m2mean = np.full((len(grid), 20, 2), np.nan)
    m2rms = m2mean.copy()
    references = np.full(len(grid), -1, dtype=np.int64)
    for o in (0, 1):
        mean = rolling(past[:, :, o], 20, 19)
        rms = rolling(past[:, :, o], 60, 57, True)
        good = previous >= 0
        m2mean[good, :, o] = mean[previous[good]]
        m2rms[good, :, o] = rms[previous[good]]
    references[previous >= 0] = np.asarray([p[5] for _, p in regular])[previous[previous >= 0]]
    # Full019B dependency envelope controls long COP histories, separately from feature missingness.
    blocked = matrix("cop_dependency").astype(bool)
    for value in v.values():
        value[blocked] = np.nan
    m2mean[blocked] = np.nan
    m2rms[blocked] = np.nan
    return Components(
        grid, h, s, v, days, dc, dv, db, vb, m2mean, m2rms, references, previous, volume
    )
