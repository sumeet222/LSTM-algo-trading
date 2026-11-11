"""Outcome-independent case axis and indexed XNYS endpoint arithmetic."""

from dataclasses import dataclass, replace
from decimal import Decimal

import numpy as np

from ..rapid_v1.shared_features import FeatureFrame
from ..rapid_v1.strategies import IDS, DirectionIntent, mode
from ..stage35.final_backtest_v4.execution_calendar import ExecutionCalendar
from ..stage35.final_backtest_v4.market import minute

D = Decimal
FIRST, LAST = "2021-01-01", "2024-12-31"


@dataclass(frozen=True)
class Case:
    strategy: str
    variant: str
    headroom: Decimal
    horizon: int
    unit: str

    @property
    def key(self) -> str:
        return self.strategy + "_" + self.variant

    @property
    def mode(self) -> str:
        return mode(self.strategy)


def case_axis() -> tuple[Case, ...]:
    axis = []
    for s in IDS:
        axis.extend(
            Case(s, key, D(factor), 240, "minutes")
            for key, factor in (
                ("H100", "1"),
                ("H85", ".85"),
                ("H70", ".70"),
            )
        )
        horizons = (60, 120, 480) if s.startswith("M") else (1, 3, 5)
        unit = "minutes" if s.startswith("M") else "sessions"
        prefix = "T" if unit == "minutes" else "D"
        axis.extend(Case(s, prefix + str(h), D(1), h, unit) for h in horizons)
    return tuple(axis)


class Endpoints:
    def __init__(self, cal: ExecutionCalendar):
        self.cal = cal
        self.cumulative = np.r_[0, np.cumsum(cal.closes - cal.opens)]
        self.cutoff = minute(LAST + "T23:59:00Z")

    def anchor(self, frame: FeatureFrame, case: Case) -> int | None:
        cal = self.cal
        session = int(np.searchsorted(cal.closes, frame.origin, side="right"))
        offset = frame.origin - int(cal.opens[session])
        if offset < 0:
            raise ValueError("INVALID_NOMINAL_ORIGIN")
        if case.unit == "sessions":
            target = session + case.horizon
            at = int(cal.opens[target]) + offset
            return at if at < int(cal.closes[target]) else None
        target_minute = int(self.cumulative[session]) + offset + case.horizon
        target = int(np.searchsorted(self.cumulative, target_minute, side="left")) - 1
        at = int(cal.opens[target]) + target_minute - int(self.cumulative[target])
        if case.horizon == 240 and at != frame.endpoint:
            raise ValueError("FROZEN_240_ENDPOINT_PARITY")
        return at

    def retime(
        self, frame: FeatureFrame, case: Case, intents: tuple[DirectionIntent, ...]
    ) -> tuple[tuple[DirectionIntent, ...], str | None]:
        if not intents:
            return (), None
        at = self.anchor(frame, case)
        if at is None:
            return (), "FUTURE_SESSION_SLOT_UNAVAILABLE"
        # V1 allocation applies the calendar cutoff in its original gate order.
        return tuple(replace(x, endpoint=at) for x in intents), None
