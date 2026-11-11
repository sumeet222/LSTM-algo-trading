"""Portfolio intent allocator and automatic fixed exits, behind the price boundary.

No file/data reader; fabricated fixtures exercise the complete intent-to-book path.
Historical prices must be ReleasedPrice and can only enter after signed release.
"""

from dataclasses import replace
from datetime import datetime, timedelta
from decimal import Decimal

from ..accounting import Journal, Lot
from ..borrow_financing import BorrowEvidence
from ..common import EPS, RAW, ZERO, D
from ..intents import SignalIntent
from ..portfolio_allocator import allocate
from .engine import ReplayEngine
from .settlement import Request, V2Book, submit


class PortfolioOrchestrator:
    def __init__(self, engine: ReplayEngine):
        self.engine = engine
        self.exit_started: set[str] = set()

    def new_vintage(
        self,
        candidates: tuple[SignalIntent, ...],
        now: datetime,
        volume: dict[str, tuple[Decimal, datetime]],
        borrow: BorrowEvidence,
    ) -> tuple[str, ...]:
        expire_unsubmitted_remainders(self.engine, now)
        if not self.engine.decision_ready(now):
            raise ValueError("UNRECONCILED_FILL_BLOCKS_DEPENDENT_DECISION")
        if any(
            c.arm != self.engine.arm or c.decision > now or c.entry_deadline < now
            for c in candidates
        ):
            raise ValueError("ARM_OR_INTENT_NOT_AVAILABLE_OR_EXPIRED")
        book = self.engine.book
        marks = dict(book.marks)
        for candidate in candidates:
            mark = marks.get(candidate.ticker)
            if mark is None:
                raise ValueError("RAW_PRETRADE_MARK_MISSING")
            mark.validate(now)
        capacity = book.capacity(now)
        minimum = min((marks[c.ticker].value for c in candidates), default=D(1))
        expense_reserve = (
            D(len(candidates)) * D(1)
            + D(".005") * D(".2") * capacity.nav / minimum
            + D(".001") * D(".2") * capacity.nav
        )
        conservative = replace(
            capacity,
            nav=capacity.nav - expense_reserve,
            own_available=max(ZERO, capacity.own_available - expense_reserve),
        )
        allocations = allocate(candidates, conservative, {k: v.value for k, v in marks.items()})
        by_id = {c.cohort_id: c for c in candidates}
        cohorts = tuple(
            by_id[a.cohort_id].cohort(a.signed_shares, a.notional, RAW)
            for a in allocations
            if a.signed_shares
        )
        if not cohorts:
            return ()
        # One atomic cross-section reservation, preserving all virtual gross.
        if any(lot.cohort.cohort_id in {c.cohort_id for c in cohorts} for lot in book.lots):
            raise ValueError("FIXED_COHORT_DUPLICATE_OR_RESIZE")
        requested = sum((abs(D(str(c.requested))) * marks[c.ticker].value for c in cohorts), ZERO)
        if requested > book.capacity(now).own_available + EPS:
            raise ValueError("UNENCUMBERED_CAPITAL")
        for c in cohorts:
            if c.requested < 0 and not borrow.permits(
                now,
                marks[c.ticker].kind == "SYNTHETIC",
                ticker=c.ticker,
                quantity=D(str(c.requested)),
            ):
                raise ValueError("SHORT_EVIDENCE_UNAVAILABLE")
        reserved = replace(
            book, lots=book.lots + tuple(Lot(c, pending=D(str(c.requested))) for c in cohorts)
        )
        if reserved.capacity(now).status != "READY":
            raise ValueError("RESERVATION_LIMIT")
        orders = []
        staged = []
        for ticker in sorted({c.ticker for c in cohorts}):
            group = tuple(c for c in cohorts if c.ticker == ticker)
            if ticker not in volume:
                raise ValueError("PRIOR_VOLUME_UNAVAILABLE_RESERVATIONS_RETAINED")
            v, available = volume[ticker]
            key = "ENTRY:" + "|".join(sorted(c.cohort_id for c in group))
            order = submit(
                key,
                self.engine.account,
                self.engine.arm,
                ticker,
                tuple(Request(c.cohort_id, D(str(c.requested))) for c in group),
                now,
                now,
                self.engine.clock.next_observation(now),
                min(c.entry_deadline for c in group),
                marks[ticker],
                v,
                available,
                True,
            )
            staged.append(order)
            orders.append(key)
        ref = max(marks.values(), key=lambda p: p.at)
        journal_id = "RESERVE:" + cohorts[0].origin.isoformat()
        if any(j.journal_id == journal_id for j in book.journal):
            raise ValueError("DUPLICATE_RESERVATION")
        reserved.reconcile()
        journal = Journal(
            journal_id,
            now,
            ref.at,
            ref.available_at,
            now,
            "CROSS_SECTION_RESERVE",
            "MULTI",
            "USD",
            RAW,
            (),
            ZERO,
            book.digest(),
            reserved.digest(),
            ref,
            (("borrow", str(borrow)), ("expense_reserve", str(expense_reserve))),
        )
        self.engine.book = replace(reserved, journal=book.journal + (journal,))
        for order in staged:
            self.engine.add(order)
        return tuple(orders)

    def due_exits(
        self,
        now: datetime,
        volume: dict[str, tuple[Decimal, datetime]],
        borrow_recall: bool = False,
    ) -> tuple[str, ...]:
        """Original endpoint+2 issue, or explicit recall; no guaranteed close price."""
        expire_unsubmitted_remainders(self.engine, now)
        if not self.engine.decision_ready(now):
            return ()
        lots = [
            lot
            for lot in self.engine.book.lots
            if lot.quantity
            and not any(
                r.cohort_id == lot.cohort.cohort_id
                for order in self.engine.pending.values()
                for r in order.requests
            )
            and (
                borrow_recall
                and lot.quantity < 0
                or now >= lot.cohort.endpoint.replace()
                and now >= lot.cohort.endpoint
            )
        ]
        # A target endpoint observation must be assumed received, never fill its earlier close.

        lots = [
            lot
            for lot in lots
            if borrow_recall or now >= lot.cohort.endpoint + timedelta(minutes=2)
        ]
        result = []
        marks = dict(self.engine.book.marks)
        for ticker in sorted({lot.cohort.ticker for lot in lots}):
            if ticker not in marks or ticker not in volume:
                self.engine.statuses.append(
                    {"ticker": ticker, "status": "EXIT_PENDING_SOURCE_MISSING", "decision_at": now}
                )
                continue
            group = tuple(lot for lot in lots if lot.cohort.ticker == ticker)
            v, available = volume[ticker]
            key = "EXIT:" + str(now) + "|" + ticker
            request = tuple(
                Request(
                    lot.cohort.cohort_id,
                    -lot.quantity,
                    "FORCED_BUY_IN" if borrow_recall else "EXIT",
                )
                for lot in group
            )
            try:
                order = submit(
                    key,
                    self.engine.account,
                    self.engine.arm,
                    ticker,
                    request,
                    now,
                    now,
                    self.engine.clock.next_observation(now),
                    None,
                    marks[ticker],
                    v,
                    available,
                    False,
                )
            except ValueError as exc:
                self.engine.statuses.append(
                    {
                        "ticker": ticker,
                        "status": "EXIT_PENDING",
                        "reason": str(exc),
                        "decision_at": now,
                    }
                )
                continue
            self.engine.add(order)
            result.append(key)
            self.exit_started.update(lot.cohort.cohort_id for lot in group)
        return tuple(result)


def submit_liquidation(
    engine: ReplayEngine, now: datetime, volume: dict[str, tuple[Decimal, datetime]]
) -> tuple[str, ...]:
    """Attempt prospective hard-breach reduction, never invent a successful fill."""
    from .settlement import liquidation_requests

    if not engine.decision_ready(now) or engine.book.capacity(now).status == "READY":
        return ()
    marks = dict(engine.book.marks)
    result = []
    for ticker in sorted({lot.cohort.ticker for lot in engine.book.lots if lot.quantity}):
        if ticker not in marks or ticker not in volume:
            engine.statuses.append(
                {"ticker": ticker, "status": "LIQUIDATION_SOURCE_UNRESOLVED", "decision_at": now}
            )
            continue
        v, available = volume[ticker]
        key = "LIQUIDATE:" + ticker + ":" + now.isoformat()
        try:
            order = submit(
                key,
                engine.account,
                engine.arm,
                ticker,
                liquidation_requests(engine.book, ticker),
                now,
                now,
                engine.clock.next_observation(now),
                None,
                marks[ticker],
                v,
                available,
                False,
            )
        except ValueError as exc:
            engine.statuses.append(
                {
                    "ticker": ticker,
                    "status": "LIQUIDATION_PENDING",
                    "decision_at": now,
                    "reason": str(exc),
                }
            )
            continue
        engine.add(order)
        result.append(key)
    return tuple(result)


def expire_unsubmitted_remainders(engine: ReplayEngine, now: datetime) -> tuple[str, ...]:
    """Expiry cancels only KNOWN unsubmitted target remainder, never uncertain broker status."""
    active = {r.cohort_id for order in engine.pending.values() for r in order.requests}
    ids = tuple(
        sorted(
            lot.cohort.cohort_id
            for lot in engine.book.lots
            if lot.pending
            and now > lot.cohort.entry_deadline
            and lot.cohort.cohort_id not in active
        )
    )
    if not ids:
        return ()
    updated = engine.book.status_event(
        "EXPIRY:" + now.isoformat(),
        now,
        now,
        "CANCEL_UNSUBMITTED_REMAINDER_EXPIRY",
        "MULTI",
        cancel_ids=ids,
    )
    if not isinstance(updated, V2Book):
        raise AssertionError("V2_EXPIRY_STATE")
    engine.book = updated
    return ids
