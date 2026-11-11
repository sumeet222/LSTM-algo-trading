"""Indexed equivalent of the frozen next-minute calendar, without linear rescans."""

import numpy as np

from ...stage012.calendar_schedule import MarketClock
from .market import minute


class ExecutionCalendar:
    def __init__(self, clock: MarketClock):
        self.opens = np.asarray([minute(v) for v in clock.calendar["open"]], dtype=np.int64)
        self.closes = np.asarray([minute(v) for v in clock.calendar["close"]], dtype=np.int64)

    def next(self, submitted_minute: int) -> int:
        target = submitted_minute + 1
        index = int(np.searchsorted(self.closes, target, side="right"))
        if index >= len(self.closes):
            raise ValueError("CALENDAR_EXHAUSTED")
        result = max(target, int(self.opens[index]))
        if result >= int(self.closes[index]):
            raise AssertionError("IMPOSSIBLE_EXECUTION_MINUTE")
        return result
