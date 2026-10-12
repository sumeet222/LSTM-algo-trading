"""Per-session maximum observed physical net short, not virtual sleeve notional."""

from __future__ import annotations

from decimal import Decimal, localcontext

import pandas as pd

from .clocks import session_clock, utc
from .p3_accounting import ARITHMETIC, PhysicalBook
from .p3_domain import Frictions, Permission, UniverseSpec


class BorrowTracker:
    def __init__(self, universe: UniverseSpec, permission: Permission, frictions: Frictions):
        permission.ensure()
        if universe != frictions.universe:
            raise ValueError("BORROW_UNIVERSE_MISMATCH")
        self.universe, self.permission, self.frictions = universe, permission, frictions
        self.maxima: dict[str, dict[str, Decimal]] = {}
        self.incomplete: set[str] = set()
        self.charged: dict[str, Decimal | None] = {}
        self.last_at: pd.Timestamp | None = None

    def observe(self, book: PhysicalBook, prices: dict[str, Decimal], at: pd.Timestamp) -> None:
        self.permission.ensure()
        at = utc(at)
        if book.universe != self.universe or (self.last_at is not None and at < self.last_at):
            raise ValueError("BORROW_UNIVERSE_OR_CLOCK_MISMATCH")
        day = at.tz_convert("America/New_York").date().isoformat()
        clock = session_clock(day)
        if clock.open is None or clock.close is None or not clock.open <= at <= clock.close:
            raise ValueError("BORROW_OBSERVATION_SESSION_REQUIRED")
        if day in self.charged:
            raise ValueError("OBSERVATION_AFTER_DAILY_BORROW_CLOSE")
        for previous in self.maxima:
            if previous < day and previous not in self.charged:
                self.incomplete.add(previous)
        observed = self.maxima.setdefault(day, dict.fromkeys(self.universe.symbols, Decimal(0)))
        with localcontext(ARITHMETIC):
            for symbol, quantity in book.balances:
                if quantity >= 0:
                    continue
                if symbol not in prices or not prices[symbol].is_finite() or prices[symbol] <= 0:
                    self.incomplete.add(day)
                else:
                    observed[symbol] = max(observed[symbol], -quantity * prices[symbol])
        self.last_at = at

    def close(self, book: PhysicalBook, at: pd.Timestamp) -> Decimal | None:
        self.permission.ensure()
        at = utc(at)
        day = at.tz_convert("America/New_York").date().isoformat()
        if at != session_clock(day).close or book.universe != self.universe:
            raise ValueError("DAILY_BORROW_CLOSE_CLOCK_REQUIRED")
        if day in self.charged:
            return self.charged[day]
        if day not in self.maxima or day in self.incomplete:
            self.charged[day] = None
            book.ledger.record(
                "SYN:BORROW:" + day,
                at,
                "BORROW",
                {
                    "amount": None,
                    "reason": "MISSING_DAY_MAX_EVIDENCE",
                    "annual_rate": self.frictions.annual_borrow,
                },
            )
            return None
        with localcontext(ARITHMETIC):
            amount = sum(self.maxima[day].values(), Decimal(0)) * self.frictions.annual_borrow / 360
        book.debit(
            amount,
            at,
            "SYN:BORROW:" + day,
            {
                "maxima": self.maxima[day],
                "annual_rate": self.frictions.annual_borrow,
                "convention": "OBSERVED_PHYSICAL_NET_SHORT_DAY_MAX_ACT_360",
                "friction_id": self.frictions.friction_id,
            },
        )
        self.charged[day] = amount
        return amount

    @property
    def total(self) -> Decimal | None:
        if self.incomplete or any(x is None for x in self.charged.values()):
            return None
        with localcontext(ARITHMETIC):
            return sum((x for x in self.charged.values() if x is not None), Decimal(0))
