"""S4 source-only trading-minute clock; no fitting or protected-price access."""

from __future__ import annotations

import exchange_calendars as xcals
import numpy as np
import pandas as pd


def sessions(start: str, stop: str) -> pd.DataFrame:
    """Authoritative XNYS intervals, including the closing stub and early closes."""
    if stop >= "2026-01-01":
        raise ValueError("S4_CALENDAR_SCOPE")
    cal = xcals.get_calendar("XNYS", start=start, end=stop)
    return cal.schedule.loc[start:stop, ["open", "close"]].copy()


def endpoint(origin: pd.Timestamp, calendar: pd.DataFrame, minutes: int = 240) -> pd.Timestamp:
    """Consume continuous regular-session minutes, pausing during every closure."""
    if origin.tzinfo is None or minutes <= 0:
        raise ValueError("AWARE_ORIGIN_POSITIVE_HORIZON_REQUIRED")
    if not ((calendar.open <= origin) & (calendar.close > origin)).any():
        raise ValueError("ORIGIN_MUST_BE_INSIDE_REGULAR_SESSION")
    remaining = pd.Timedelta(minutes=minutes)
    cursor = origin
    for opened, closed in calendar[["open", "close"]].itertuples(index=False, name=None):
        if closed <= cursor:
            continue
        if cursor < opened:
            cursor = opened
        available = closed - cursor
        if remaining <= available:
            return cursor + remaining
        remaining -= available
        cursor = closed
    raise ValueError("CALENDAR_LOOKAHEAD_EXHAUSTED")


def schedule(calendar: pd.DataFrame, stop: str = "2024-12-31") -> pd.DataFrame:
    """Candidate origins only; a conditional open is distinguished from full-hour ends."""
    rows = []
    for day, part in calendar.iterrows():
        date = str(pd.Timestamp(str(day)).date())
        if date > stop:
            break
        opened, closed = pd.Timestamp(part["open"]), pd.Timestamp(part["close"])
        for k in range(7):
            t = opened + pd.Timedelta(hours=k)
            if t >= closed:
                continue
            end = endpoint(t, calendar.loc[day:])
            rows.append(
                dict(
                    origin_id=t.isoformat(),
                    session_date_et=date,
                    slot=t.tz_convert("America/New_York").strftime("%H:%M"),
                    context=6 if k == 0 else k - 1,
                    entry_end_utc=t,
                    exit_end_utc=end,
                    issuance_utc=t + pd.Timedelta(minutes=2),
                    label_maturity_utc=end + pd.Timedelta(minutes=2),
                    session_open=opened,
                    session_close=closed,
                    category="INTRADAY" if end <= closed else "OVERNIGHT",
                    conditional_open=k == 0,
                    regular_session=closed - opened == pd.Timedelta(minutes=390),
                    trading_minutes=240,
                )
            )
    return pd.DataFrame(rows)


def complete_prices(prices: np.ndarray) -> np.ndarray:
    """No proxy endpoint or partial cross-section can become a valid target panel."""
    if prices.ndim != 2 or prices.shape[1] != 20:
        raise ValueError("COMPLETE20_REQUIRED")
    return np.isfinite(prices).all(axis=1) & (prices > 0).all(axis=1)


def month_guard(month: str) -> None:
    """Reject disallowed partitions before any stat, hashing or numerical read."""
    if not "2010-07" <= month <= "2024-12":
        raise ValueError("S4_NUMERIC_PARTITION_DENIED_BEFORE_IO")
