"""Causal HF20 component mathematics; independent of targets, fitting and permission."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .hf20_source import BARRIER, SYMBOLS
from .hf_hourly_audit import calendar_grid, quality_flags
from .stock_features import IndicatorState

ORDER = (
    "M1",
    "M2",
    "M3",
    "M4",
    "V1",
    "V2",
    "V3",
    "B1",
    "B2",
    "Q1",
    "Q2",
    "T1",
    "T2",
    "T3",
    "T4",
    "T5",
)
COMMON = tuple(name for name in ORDER if name != "M2")
BOUNDED = {"B2", "T2", "T5"}


def rolling(values: np.ndarray, count: int, minimum: int, *, square: bool = False) -> np.ndarray:
    """Exact scheduled positions, minimum valid count and no three consecutive misses."""
    frame = pd.DataFrame(values)
    finite = frame.notna()
    triple = (~finite).rolling(3, min_periods=3).sum().eq(3)
    gaps = triple.rolling(max(1, count - 2), min_periods=1).max().astype(bool)
    result = (frame.pow(2) if square else frame).rolling(count, min_periods=minimum).mean()
    result.iloc[: count - 1] = np.nan
    result = result.mask(gaps)
    array = result.to_numpy(dtype=float)
    return np.sqrt(array) if square else array


@dataclass
class Components:
    grid: pd.DataFrame
    days: tuple[str, ...]
    day_index: np.ndarray
    source: dict[str, np.ndarray]
    values: dict[str, np.ndarray]
    daily_close: np.ndarray
    daily_volume: np.ndarray
    regular_days: tuple[str, ...]
    m2_mean: np.ndarray
    m2_rms: np.ndarray
    origin_indices: np.ndarray
    returns: np.ndarray
    independent_daily_close: bool = False


def build_components(
    frame: pd.DataFrame, *, start: str, stop: str, independent_daily_close: bool = False
) -> Components:
    """No TG20 input: all component references are at/before each historical cutoff."""
    if pd.Timestamp(stop, tz="America/New_York") >= BARRIER or frame.datetime.ge(BARRIER).any():
        raise ValueError("HF20_CONFIRMATION_FEATURE_ACCESS_DENIED")
    grid, _ = calendar_grid(start, stop)
    grid = grid.loc[~grid.stub].reset_index(drop=True)
    days = tuple(sorted(grid.session.unique()))
    day_index = np.asarray([days.index(day) for day in grid.session], dtype=np.int64)
    regular_days = tuple(str(day) for day, group in grid.groupby("session") if len(group) == 6)
    source = {}
    permitted = frame.loc[quality_flags(frame).valid].copy()
    for field in ("open", "high", "low", "close", "volume"):
        table = permitted.pivot(index="UTC", columns="symbol", values=field)
        source[field] = table.reindex(index=pd.DatetimeIndex(grid.start), columns=SYMBOLS).to_numpy(
            dtype=float
        )
    n, stocks = source["close"].shape
    values: dict[str, np.ndarray] = {}
    values["OC"] = np.log(source["close"] / source["open"])
    values["RMS12"] = rolling(values["OC"], 12, 12, square=True)
    values["RMS60"] = rolling(values["OC"], 60, 57, square=True)
    values["B1"] = np.log(source["high"] / source["low"])
    spread = source["high"] - source["low"]
    values["B2"] = np.divide(
        2 * source["close"] - source["high"] - source["low"],
        spread,
        out=np.zeros((n, stocks)),
        where=spread != 0,
    )
    values["B2"][~np.isfinite(spread)] = np.nan
    values["VOLUME_H"] = source["volume"]
    daily_close = np.full((len(regular_days), stocks), np.nan)
    daily_volume = np.full_like(daily_close, np.nan)
    origin_indices = np.full((len(days), 2), -1, dtype=np.int64)
    returns = np.full((len(days), stocks, 2), np.nan)
    groups = grid.groupby("session", sort=True).indices
    for day, positions in groups.items():
        p = np.asarray(positions, dtype=np.int64)
        d = days.index(str(day))
        if len(p) != 6:
            continue
        r = regular_days.index(str(day))
        valid_day = np.isfinite(source["close"][p]).all(axis=0)
        daily_close[r] = (
            source["close"][p[-1]].copy()
            if independent_daily_close
            else np.where(valid_day, source["close"][p[-1]], np.nan)
        )
        daily_volume[r] = np.where(valid_day, source["volume"][p].sum(axis=0), np.nan)
        for o in range(2):
            origin_indices[d, o] = p[o]
            valid = np.isfinite(source["close"][p[o : o + 5]]).all(axis=0)
            returns[d, :, o] = np.where(
                valid, np.log(source["close"][p[o + 4]] / source["close"][p[o]]), np.nan
            )
    daily = pd.DataFrame(daily_close)
    daily_changes = np.asarray(np.log(daily / daily.shift(1)), dtype=float)
    proxy = {
        "RMS63": rolling(daily_changes, 63, 60, square=True),
        "MOM5": np.asarray(np.log(daily / daily.shift(5)), dtype=float),
        "MOM105": np.asarray(np.log(daily.shift(20) / daily.shift(125)), dtype=float),
        "SMA20": rolling(daily_close, 20, 19),
        "T2": rolling(np.sign(daily_changes), 20, 19),
        "Q2_5": rolling(daily_volume, 5, 5),
        "Q2_60": rolling(daily_volume, 60, 57),
        "VOLUME_D": daily_volume,
    }
    # Search the structural regular-session calendar, not only observed good days.
    previous = np.searchsorted(np.asarray(regular_days), np.asarray(days), side="left") - 1
    for name, daily_values in proxy.items():
        expanded = np.full((len(days), stocks), np.nan)
        good = previous >= 0
        expanded[good] = daily_values[previous[good]]
        values[name] = expanded[day_index]
    values["T1"] = np.log(source["close"] / values["SMA20"])
    values["Q1_MEAN"] = np.full((n, stocks), np.nan)
    for _, positions in grid.groupby("slot").indices.items():
        p = np.asarray(positions, dtype=np.int64)
        lagged = pd.DataFrame(source["volume"][p]).shift(1).to_numpy()
        values["Q1_MEAN"][p] = rolling(lagged, 20, 19)
    for name in ("T3", "T4", "T5"):
        values[name] = np.full((n, stocks), np.nan)
    recent = np.isfinite(rolling(source["close"], 72, 69))
    for j in range(stocks):
        state = IndicatorState()
        for i in range(n):
            close = float(source["close"][i, j])
            state.update(close if np.isfinite(close) else None)
            if not np.isfinite(close) or not recent[i, j]:
                continue
            if state.ema_updates >= 360:
                values["T3"][i, j] = (state.emas[6] - state.emas[18]) / close
                values["T4"][i, j] = (state.emas[24] - state.emas[72]) / close
            rsi = state.normalized_rsi()
            if rsi is not None:
                values["T5"][i, j] = rsi
    m2_mean = np.full((len(days), stocks, 2), np.nan)
    m2_rms = np.full_like(m2_mean, np.nan)
    normal = np.asarray([days.index(day) for day in regular_days], dtype=np.int64)
    for o in range(2):
        means = rolling(returns[normal, :, o], 20, 19)
        scales = rolling(returns[normal, :, o], 60, 57, square=True)
        good = previous >= 0
        m2_mean[good, :, o] = means[previous[good]]
        m2_rms[good, :, o] = scales[previous[good]]
    return Components(
        grid,
        days,
        day_index,
        source,
        values,
        daily_close,
        daily_volume,
        regular_days,
        m2_mean,
        m2_rms,
        origin_indices,
        returns,
        independent_daily_close,
    )
