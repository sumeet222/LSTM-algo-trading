"""Contextual cash/long-only synthetic benchmarks; reuse the P3 physical engine."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext

import pandas as pd

from .baseline_authority import verify
from .calendar import schedule
from .clocks import session_clock, utc
from .p3_accounting import ARITHMETIC
from .p3_domain import Frictions, Permission, PriceReference, UniverseSpec, synthetic_id
from .p3_engine import PortfolioEngine
from .p3_execution import ExecutionOffer, eligible_offer
from .p3_policy import Policy


@dataclass(frozen=True)
class OpeningOffer:
    universe: UniverseSpec
    offer: ExecutionOffer
    price_field: str
    basis: str

    def __post_init__(self) -> None:
        if (
            self.universe != self.offer.universe
            or self.basis != "SYNTHETIC"
            or self.price_field != "open"
            or self.offer.reference.kind != "SYNTHETIC_MINUTE_EVENT"
        ):
            raise ValueError("EXPLICIT_SYNTHETIC_ONE_MINUTE_OPEN_REQUIRED")


class CashControl:
    def __init__(
        self,
        universe: UniverseSpec,
        permission: Permission,
        cash: Decimal,
        at: pd.Timestamp,
        *,
        allow_synthetic: bool = False,
    ):
        verify(permission)
        if not allow_synthetic:
            raise ValueError("SYNTHETIC_CASH_CONTROL_OPT_IN_REQUIRED")
        self.engine = PortfolioEngine(
            universe, permission, Policy(universe, "A"), Frictions(universe, Decimal(0)), cash, at
        )
        self.scope = "CASH_CONTEXTUAL_NO_INTEREST_ASSUMPTION"

    def valuation(self, at: pd.Timestamp) -> dict:
        verify(self.engine.permission)
        return {
            "scope": self.scope,
            "cash": self.engine.book.cash,
            "toy_equity": self.engine.book.valuation((), at)["accrual_equity"],
            "interest_credit": Decimal(0),
            "basis": "SYNTHETIC",
            "research_ready": False,
        }


class BuyAndHold:
    def __init__(
        self,
        universe: UniverseSpec,
        permission: Permission,
        frictions: Frictions,
        initial_equity: Decimal,
        segment_id: str,
        first_session: str,
        last_session: str,
        *,
        allow_synthetic: bool = False,
    ):
        verify(permission)
        synthetic_id(segment_id)
        first, last = session_clock(first_session), session_clock(last_session)
        if (
            not allow_synthetic
            or first.open is None
            or last.close is None
            or first_session > last_session
            or initial_equity <= 0
            or frictions.universe != universe
        ):
            raise ValueError("SYNTHETIC_NAMED_EVALUATION_SEGMENT_REQUIRED")
        self.universe, self.permission, self.frictions = universe, permission, frictions
        self.initial_equity, self.segment_id = initial_equity, segment_id
        self.first_session, self.last_session = first_session, last_session
        self.sessions = tuple(
            pd.Timestamp(day).date().isoformat()
            for day in schedule(first_session, last_session).index
        )
        self.start, self.terminal = first.open, last.close - pd.Timedelta(minutes=1)
        self.engine = PortfolioEngine(
            universe, permission, Policy(universe, "A"), frictions, initial_equity, first.open
        )
        self.scope = "LONG_ONLY_CONTEXTUAL_NOT_RISK_MATCHED"
        self.entered = self.terminal_complete = self.terminal_attempted = False
        self.entry_aborted = False
        self.entry_at: pd.Timestamp | None = None
        self.last_entry_attempt: pd.Timestamp | None = None

    def _offers(self, rows: tuple[OpeningOffer, ...]) -> tuple[ExecutionOffer, ...]:
        if any(row.universe != self.universe for row in rows):
            raise ValueError("BENCHMARK_OFFER_UNIVERSE_MISMATCH")
        return tuple(row.offer for row in rows)

    def attempt_entry(self, at: pd.Timestamp, rows: tuple[OpeningOffer, ...]) -> bool:
        verify(self.permission)
        at = utc(at)
        if self.entered or self.entry_aborted or self.engine.pending_target is not None:
            return False
        day = at.tz_convert("America/New_York").date().isoformat()
        expected_day = (
            self.sessions[0]
            if self.last_entry_attempt is None
            else self.sessions[
                self.sessions.index(
                    self.last_entry_attempt.tz_convert("America/New_York").date().isoformat()
                )
                + 1
            ]
            if self.last_entry_attempt.tz_convert("America/New_York").date().isoformat()
            != self.sessions[-1]
            else None
        )
        if (
            at != session_clock(day).open
            or not self.first_session <= day <= self.last_session
            or day != expected_day
            or (self.last_entry_attempt is not None and at <= self.last_entry_attempt)
        ):
            raise ValueError("BENCHMARK_NEXT_SESSION_0930_REQUIRED")
        self.last_entry_attempt = at
        offered = self._offers(rows)
        lookup = self.engine._offers(offered)
        if any(
            not eligible_offer(lookup.get(s), at, minute=True)
            or lookup[s].reference.share_basis != self.engine.book.share_basis(s)
            for s in self.universe.symbols
        ):
            self.engine.ledger.record(
                self.segment_id + ":NO_ENTRY:" + day,
                at,
                "REJECT",
                {"reason": "WHOLE_BENCHMARK_REMAINS_CASH_MISSING_OPEN"},
            )
            return False
        with localcontext(ARITHMETIC):
            notional = self.initial_equity / (5 * (1 + self.frictions.bps / 10000))
            targets = tuple(
                (s, notional / lookup[s].reference.price) for s in self.universe.symbols
            )
            # Audit the same sequential Decimal40 arithmetic as actual physical fills.
            remaining = self.engine.book.cash
            for s, q in targets:
                p = lookup[s].reference.price
                remaining += -q * p - self.frictions.fee(q, p)
            if remaining < 0:
                raise ValueError("DECLARED_DECIMAL_BUDGET_ROUNDING_INCOMPLETE")
        self.engine.ledger.record(
            self.segment_id + ":ALLOCATION",
            at,
            "TARGET",
            {
                "scope": self.scope,
                "initial_notional_per_name": notional,
                "targets": targets,
                "share_arithmetic": "DECIMAL40_HALF_EVEN_EXACT_FRACTIONAL_ASSUMPTION",
                "basis": "SYNTHETIC",
            },
        )
        complete = self.engine._execute(
            targets,
            at,
            self.segment_id + ":ENTRY",
            lookup,
            minute=True,
            parent=self.segment_id + ":ALLOCATION",
        )
        if not complete:
            self.entry_aborted = True
            self.engine._pending_flat(at, "BENCHMARK_PARTIAL_ENTRY")
            return False
        self.entered = True
        self.entry_at = at
        return True

    def close_session(self, at: pd.Timestamp, marks: tuple[PriceReference, ...]) -> None:
        verify(self.permission)
        self.engine.monitor(at, marks, self.segment_id + ":CLOSE:" + utc(at).date().isoformat())
        self.engine.borrow.close(self.engine.book, at)

    def attempt_terminal(self, at: pd.Timestamp, rows: tuple[OpeningOffer, ...]) -> bool:
        verify(self.permission)
        at = utc(at)
        if at != self.terminal:
            raise ValueError("BENCHMARK_LAST_RTH_MINUTE_REQUIRED")
        if self.terminal_attempted:
            return self.terminal_complete
        self.terminal_attempted = True
        target = tuple((s, Decimal(0)) for s in self.universe.symbols)
        complete = self.engine._execute(
            target,
            at,
            self.segment_id + ":TERMINAL",
            self.engine._offers(self._offers(rows)),
            minute=True,
        )
        self.terminal_complete = complete
        if not complete:
            self.engine._pending_flat(at, "BENCHMARK_MISSING_TERMINAL")
        return complete

    def retry(self, at: pd.Timestamp, rows: tuple[OpeningOffer, ...]) -> bool:
        verify(self.permission)
        if (
            self.engine.pending_since is not None
            and utc(at).tz_convert("America/New_York").date()
            != self.engine.pending_since.tz_convert("America/New_York").date()
        ):
            self.engine.overnight_unsupported = True
        return self.engine.retry(
            at, self._offers(rows), self.segment_id + ":RETRY:" + utc(at).isoformat()
        )

    def apply_actions(self, actions: tuple, at: pd.Timestamp) -> None:
        verify(self.permission)
        self.engine.apply_actions(actions, at)

    def valuation(self, at: pd.Timestamp, marks: tuple[PriceReference, ...]) -> dict:
        verify(self.permission)
        snapshot = self.engine.valuation(
            at, marks, self.segment_id + ":VALUE:" + utc(at).isoformat()
        )
        incomplete = self.entry_aborted or (utc(at) >= self.terminal and not self.terminal_complete)
        return {
            **snapshot,
            "scope": self.scope,
            "terminal_complete": self.terminal_complete,
            "NAV": None if incomplete else snapshot["NAV"],
            "segment_status": "INCOMPLETE_TERMINAL_SALE" if incomplete else snapshot["status"],
        }
