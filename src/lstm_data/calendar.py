"""NYSE session grids and native-hour timing diagnostics, without relabeling."""

from __future__ import annotations

import exchange_calendars as xcals
import pandas as pd


def schedule(start: str, end: str) -> pd.DataFrame:
    """Real historical XNYS opens/closes (UTC), including DST and early closes."""
    lower, upper = pd.Timestamp(start), pd.Timestamp(end)
    if lower > upper:
        raise ValueError("Calendar start must not follow end")
    # Padding supports one-day and holiday-only audits; calendar construction
    # itself requires a nonempty range even when the requested slice is empty.
    calendar = xcals.get_calendar(
        "XNYS", start=lower - pd.Timedelta(days=7), end=upper + pd.Timedelta(days=7)
    )
    return calendar.schedule.loc[start:end, ["open", "close"]]


def session_grid(open_time: pd.Timestamp, close_time: pd.Timestamp) -> list[dict]:
    """Desired session-anchored hours plus a flagged, unmerged closing stub."""
    result = []
    start = open_time
    while start < close_time:
        end = min(start + pd.Timedelta(hours=1), close_time)
        result.append({"start": start, "end": end, "stub": end - start < pd.Timedelta(hours=1)})
        start = end
    return result


def fully_inside_rth(frame: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """Select completed native intervals wholly inside RTH for audits only."""
    minutes = (
        30 if "source_timeframe" in frame and (frame.source_timeframe == "30Min").all() else 60
    )
    inside = pd.Series(False, index=frame.index)
    for _, session in schedule(start, end).iterrows():
        inside |= (frame.timestamp >= session.open) & (
            frame.timestamp + pd.Timedelta(minutes=minutes) <= session.close
        )
    return frame.loc[inside].copy()


def stock_qa(frame: pd.DataFrame, symbols: list[str], start: str, end: str) -> dict:
    """Compare native provider starts to desired grids, never shifting any bar."""
    from .validation import defects, normalize

    frame = normalize(frame, stocks=True)
    minutes = 60
    if "source_timeframe" in frame:
        if frame.source_timeframe.nunique() > 1:
            raise ValueError("Stock QA refuses mixed source resolutions")
        minutes = 30 if (frame.source_timeframe == "30Min").all() else 60
    sessions = schedule(start, end)
    result = {
        "defects": defects(frame, stocks=True),
        "symbols": {},
        "daily": [],
        "source_interval_minutes": minutes,
    }
    unexpected = set(frame.symbol) - set(symbols)
    result["unexpected_symbols"] = sorted(unexpected)
    for symbol in symbols:
        group = frame[frame.symbol == symbol].sort_values("timestamp")
        source_minutes = group.timestamp.dt.tz_convert("America/New_York").dt.minute
        summary = {
            "rows": len(group),
            "earliest_utc": str(group.timestamp.min()) if len(group) else None,
            "latest_utc": str(group.timestamp.max()) if len(group) else None,
            "local_start_minute_counts": {
                str(k): int(v) for k, v in source_minutes.value_counts().items()
            },
            "missing_session_anchored_starts": 0,
            "partial_session_overlap_bars": 0,
            "no_rth_overlap_sessions": 0,
            "outside_session_bars": 0,
            "price_jump_candidates": [],
            "price_range": {
                "min": float(group[["open", "high", "low", "close"]].min().min())
                if len(group)
                else None,
                "max": float(group[["open", "high", "low", "close"]].max().max())
                if len(group)
                else None,
            },
            "volume_range": {
                "min": float(group.volume.min()) if len(group) else None,
                "max": float(group.volume.max()) if len(group) else None,
            },
        }
        in_any_session = pd.Series(False, index=group.index)
        previous_close = None
        for day, row in sessions.iterrows():
            grid = session_grid(row.open, row.close)
            expected = (
                set(pd.date_range(row.open, row.close, freq="30min", inclusive="left"))
                if minutes == 30
                else {item["start"] for item in grid}
            )
            # Native timestamps are candidate starts; this is an audit assumption only.
            native_ends = group.timestamp + pd.Timedelta(minutes=minutes)
            overlaps = (group.timestamp < row.close) & (native_ends > row.open)
            in_any_session |= overlaps
            current = group[overlaps]
            starts = set(current.timestamp)
            partial = (current.timestamp < row.open) | (
                current.timestamp + pd.Timedelta(minutes=minutes) > row.close
            )
            missing = expected - starts
            summary["missing_session_anchored_starts"] += len(missing)
            summary["partial_session_overlap_bars"] += int(partial.sum())
            summary["no_rth_overlap_sessions"] += int(current.empty)
            result["daily"].append(
                {
                    "symbol": symbol,
                    "session": str(day.date()),
                    "open_utc": row.open.isoformat(),
                    "close_utc": row.close.isoformat(),
                    "early_close": row.close.tz_convert("America/New_York").hour < 16,
                    "native_rth_overlap_starts_local": current.timestamp.dt.tz_convert(
                        "America/New_York"
                    )
                    .dt.strftime("%H:%M")
                    .tolist(),
                    "missing_expected_starts_utc": sorted(t.isoformat() for t in missing),
                    "extra_overlapping_starts_utc": sorted(
                        t.isoformat() for t in starts - expected
                    ),
                    "partial_overlap_count": int(partial.sum()),
                    "expected_stub_minutes": int(
                        (grid[-1]["end"] - grid[-1]["start"]).total_seconds() / 60
                    ),
                }
            )
            if not current.empty:
                opening = float(current.iloc[0].open)
                if previous_close is not None and abs(opening / previous_close - 1) > 0.2:
                    summary["price_jump_candidates"].append(
                        {"session": str(day.date()), "ratio": opening / previous_close}
                    )
                previous_close = float(current.iloc[-1].close)
        summary["outside_session_bars"] = int((~in_any_session).sum())
        # Candidates include real news gaps: neither automatic repair nor event confirmation.
        result["symbols"][symbol] = summary
    result["native_session_anchored_gate_pass"] = (
        not unexpected
        and not frame.empty
        and not any(
            value
            for key, value in result["defects"].items()
            if key not in {"fractional_volume_rows", "zero_volume_rows"}
        )
        and all(
            s["rows"]
            and s["missing_session_anchored_starts"] == 0
            and s["partial_session_overlap_bars"] == 0
            for s in result["symbols"].values()
        )
    )
    result["warning"] = (
        "Missing desired starts may reflect incompatible aggregation boundaries, "
        "not missing trades. "
        "Partial overlap bars cannot be truncated using aggregated OHLCV. No lunch break in XNYS. "
        "Native 60-minute closing bars cannot establish a 30-minute stub; gate is conservative."
    )
    return result
