"""Approved 30Min source to session-anchored hours; no stored table duplication."""

from __future__ import annotations

import pandas as pd

from .calendar import schedule, session_grid
from .validation import normalize, require_valid


def aggregate_session_hours(
    frame: pd.DataFrame,
    symbols: list[str],
    start: str,
    end: str,
) -> tuple[pd.DataFrame, dict]:
    """Combine complete half-hour constituents; retain closing stubs and missing masks.

    Timestamp labels remain interval starts. `available_at` is interval end under
    the completed-bar assumption; historical vendor publication latency is unknown.
    Incomplete windows emit metadata only, never manufactured OHLCV. Hourly panels
    are materialized on demand in memory from a single canonical source store.
    """
    frame = normalize(frame, stocks=True)
    require_valid(frame, stocks=True)
    if "source_timeframe" not in frame or not (frame.source_timeframe == "30Min").all():
        raise ValueError("Session aggregation requires explicitly identified 30Min source")
    if set(frame.symbol) - set(symbols):
        raise ValueError("Unexpected source symbol")
    if (frame.timestamp.dt.minute.mod(30) != 0).any() or (
        (frame.timestamp.dt.second != 0)
        | (frame.timestamp.dt.microsecond != 0)
        | (frame.timestamp.dt.nanosecond != 0)
    ).any():
        raise ValueError("Source starts do not align with exact half-hour boundaries")
    observations, windows = [], []
    expected_total, missing_total, stub_total = 0, 0, 0
    sessions = schedule(start, end)
    for symbol in symbols:
        group = frame[frame.symbol == symbol].set_index("timestamp")
        for day, session in sessions.iterrows():
            for interval in session_grid(session.open, session.close):
                expected = pd.date_range(
                    interval["start"], interval["end"], freq="30min", inclusive="left"
                )
                missing = [t for t in expected if t not in group.index]
                expected_total += len(expected)
                missing_total += len(missing)
                stub_total += int(interval["stub"])
                windows.append(
                    {
                        "symbol": symbol,
                        "session": str(day.date()),
                        "start_utc": interval["start"].isoformat(),
                        "end_utc": interval["end"].isoformat(),
                        "stub": interval["stub"],
                        "missing_source_starts": [t.isoformat() for t in missing],
                        "complete": not missing,
                    }
                )
                if missing:
                    continue
                constituents = group.loc[expected]
                record = {
                    "symbol": symbol,
                    "timestamp": interval["start"],
                    "available_at": interval["end"],
                    "session": str(day.date()),
                    "duration_minutes": int(
                        (interval["end"] - interval["start"]).total_seconds() / 60
                    ),
                    "is_stub": interval["stub"],
                    "source_bar_count": len(expected),
                    "open": float(constituents.iloc[0].open),
                    "high": float(constituents.high.max()),
                    "low": float(constituents.low.min()),
                    "close": float(constituents.iloc[-1].close),
                    "volume": float(constituents.volume.sum()),
                }
                if "trade_count" in constituents:
                    record["trade_count"] = constituents.trade_count.sum(min_count=len(expected))
                # Alpaca minute VWAP can use a different volume basis from bar.volume;
                # don't claim a true trade VWAP by weighting with the wrong denominator.
                observations.append(record)
    output = pd.DataFrame(
        observations,
        columns=[
            "symbol",
            "timestamp",
            "available_at",
            "session",
            "duration_minutes",
            "is_stub",
            "source_bar_count",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "trade_count",
        ],
    )
    output = normalize(output, stocks=True)
    output["available_at"] = pd.to_datetime(output.available_at, utc=True)
    output["trade_count"] = pd.to_numeric(output.trade_count).astype("Int64")
    summary = {
        "schema_version": 1,
        "source_timeframe": "30Min",
        "output_kind": "session_anchored_hours",
        "rows": len(output),
        "expected_source_bars": expected_total,
        "missing_source_bars": missing_total,
        "expected_stub_windows": stub_total,
        "complete_windows": len(output),
        "windows": windows,
        "timing_gate_pass": bool(len(sessions)) and missing_total == 0 and len(output) > 0,
        "vwap_policy": "Source VWAP retained in canonical store; aggregate VWAP intentionally "
        "omitted because provider VWAP volume basis can differ from bar volume.",
        "availability": "End of complete interval assumed; actual publication latency unknown",
    }
    return output, summary
