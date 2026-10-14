"""Strict schemas; bad observations are diagnosed, never repaired."""

from __future__ import annotations

import numpy as np
import pandas as pd

OHLCV = ["open", "high", "low", "close", "volume"]


def parse_utc(values: pd.Series) -> pd.Series:
    """Reject naive timestamps before conversion to offset-aware UTC."""
    parsed = []
    for value in values:
        timestamp = pd.Timestamp(value)
        if pd.isna(timestamp) or timestamp.tzinfo is None:
            raise ValueError("Every timestamp must have an explicit UTC offset/timezone")
        parsed.append(timestamp.tz_convert("UTC"))
    return pd.Series(pd.to_datetime(parsed, utc=True), index=values.index, name=values.name).astype(
        "datetime64[ns, UTC]"
    )


def normalize(frame: pd.DataFrame, *, stocks: bool = False) -> pd.DataFrame:
    """Validate required dtypes, leaving duplicates and numerical defects for audit."""
    required = ["timestamp", *OHLCV] + (["symbol"] if stocks else [])
    missing = set(required) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    result = frame.copy()
    result["timestamp"] = parse_utc(result["timestamp"])
    for column in OHLCV:
        result[column] = pd.to_numeric(result[column], errors="raise").astype("float64")
    if stocks and (result.symbol.isna().any() or (result.symbol.astype(str) == "").any()):
        raise ValueError("Null/empty symbol")
    return result


def defects(frame: pd.DataFrame, *, stocks: bool = False) -> dict:
    """Count invalid rows; never silently drop, coerce, sort, or deduplicate."""
    prices = frame[["open", "high", "low", "close"]]
    keys = ["symbol", "timestamp"] if stocks else ["timestamp"]
    invalid_ohlc = (
        (frame.high < prices.max(axis=1))
        | (frame.low > prices.min(axis=1))
        | (frame.high < frame.low)
    )
    ordered = (
        all(group.timestamp.is_monotonic_increasing for _, group in frame.groupby("symbol"))
        if stocks
        else frame.timestamp.is_monotonic_increasing
    )
    return {
        "null_fields": int(frame[[*keys, *OHLCV]].isna().sum().sum()),
        "duplicate_keys": int(frame.duplicated(keys).sum()),
        "out_of_order": not ordered,
        "nonfinite_ohlcv_rows": int((~np.isfinite(frame[OHLCV])).any(axis=1).sum()),
        "nonpositive_price_rows": int((prices <= 0).any(axis=1).sum()),
        "invalid_ohlc_rows": int(invalid_ohlc.sum()),
        "negative_volume_rows": int((frame.volume < 0).sum()),
        "zero_volume_rows": int((frame.volume == 0).sum()),
        "fractional_volume_rows": int((frame.volume.mod(1) != 0).sum()),
    }


def require_valid(frame: pd.DataFrame, *, stocks: bool = False) -> None:
    # Engineering overlays must never be normalized into genuine source, daily
    # evidence, hourly inputs or references, even when they contain zero fills.
    if frame.attrs.get("engineering_only") or any(
        column in frame and frame[column].eq(True).any()
        for column in ("engineering_only", "is_synthetic")
    ):
        raise ValueError("ENGINEERING_CANDLE_VIEW_IS_NOT_GENUINE_SOURCE")
    checks = defects(frame, stocks=stocks)
    fatal = {
        key: value
        for key, value in checks.items()
        if value and key not in {"zero_volume_rows", "fractional_volume_rows"}
    }
    if fatal:
        raise ValueError(f"Invalid immutable source observations: {fatal}")
