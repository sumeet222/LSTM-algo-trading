"""Atomic synthetic accountant wrapping frozen Stage012 cohort definitions.

Cash includes restricted proceeds exactly once. NAV and attributed virtual equity
are reconciled on every immutable state transaction. No historical prices accepted.
"""

from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal

from ..stage012.cohort_state import Cohort
from ..stage012.contracts import utc
from .borrow_financing import BorrowEvidence, calendar_charge
from .common import EPS, RAW, ZERO, D, Price, checksum
from .internal_cross import Leg, cross
from .policy_config import LIMITS
from .portfolio_allocator import Capacity


@dataclass(frozen=True)
class Lot:
    cohort: Cohort
    quantity: Decimal = ZERO
    basis: Decimal = ZERO
    cash: Decimal = ZERO
    realized: Decimal = ZERO
    nontrade_cash: Decimal = ZERO
    accrual: Decimal = ZERO
    pending: Decimal = ZERO
    unit_factor: Decimal = D(1)
    closed: bool = False


@dataclass(frozen=True)
class Physical:
    ticker: str
    quantity: Decimal = ZERO
    basis: Decimal = ZERO
    realized: Decimal = ZERO
    borrow_asof: datetime | None = None


@dataclass(frozen=True)
class Journal:
    journal_id: str
    event_time: datetime
    observation_time: datetime
    available_at: datetime
    processed_at: datetime
    cause: str
    ticker: str
    currency: str
    basis: str
    legs: tuple[Leg, ...]
    amount: Decimal
    before: str
    after: str
    reference: Price | None = None
    details: tuple[tuple[str, str], ...] = ()


def inventory(
    q: Decimal, basis: Decimal, delta: Decimal, price: Decimal
) -> tuple[Decimal, Decimal, Decimal]:
    new = q + delta
    realized = ZERO
    if not q or q * delta > 0:
        b = (abs(q) * basis + abs(delta) * price) / abs(new) if new else ZERO
    else:
        closing = min(abs(q), abs(delta))
        realized = closing * (price - basis) * (D(1) if q > 0 else D(-1))
        b = ZERO if not new else price if q * new < 0 else basis
    return new, b, realized


@dataclass(frozen=True)
class CashClaim:
    action_id: str
    cohort_id: str
    amount: Decimal
    due_at: datetime


@dataclass(frozen=True)
class Book:
    initial_cash: Decimal
    cash: Decimal
    lots: tuple[Lot, ...] = ()
    positions: tuple[Physical, ...] = ()
    marks: tuple[tuple[str, Price], ...] = ()
    journal: tuple[Journal, ...] = ()
    unresolved: tuple[str, ...] = ()
    claims: tuple[CashClaim, ...] = ()
    action_keys: tuple[str, ...] = ()

    @classmethod
    def funded(cls, cash: Decimal) -> "Book":
        if not cash.is_finite() or cash <= 0:
            raise ValueError("POSITIVE_OWN_CAPITAL")
        return cls(cash, cash)

    def digest(self) -> str:
        return checksum(
            {
                "cash": self.cash,
                "initial": self.initial_cash,
                "lots": self.lots,
                "positions": self.positions,
                "marks": self.marks,
                "claims": self.claims,
                "actions": self.action_keys,
                "unresolved": self.unresolved,
            }
        )

    def nav(self) -> Decimal:
        marks = dict(self.marks)
        return (
            self.cash
            + sum(
                (pos.quantity * marks[pos.ticker].value for pos in self.positions if pos.quantity),
                ZERO,
            )
            + sum((lot_item.accrual for lot_item in self.lots), ZERO)
        )

    def restricted(self) -> Decimal:
        return sum((-p.quantity * p.basis for p in self.positions if p.quantity < 0), ZERO)

    def capacity(self, at: datetime) -> Capacity:
        marks = dict(self.marks)
        names: dict[str, Decimal] = {}
        vintages: dict[str, Decimal] = {}
        stale = False
        for lot in self.lots:
            if not lot.quantity and not lot.pending:
                continue
            mark = marks.get(lot.cohort.ticker)
            if mark is None:
                raise ValueError("UNMARKED_POSITION")
            stale |= utc(at) - utc(mark.at) > timedelta(minutes=LIMITS.mark_age_minutes)
            gross = (abs(lot.quantity) + abs(lot.pending)) * mark.value
            names[lot.cohort.ticker] = names.get(lot.cohort.ticker, ZERO) + gross
            key = lot.cohort.origin.isoformat()
            vintages[key] = vintages.get(key, ZERO) + gross
        gross = sum(names.values(), ZERO)
        nav = self.nav()
        net = sum((p.quantity * marks[p.ticker].value for p in self.positions if p.quantity), ZERO)
        status = (
            "UNRESOLVED"
            if self.unresolved
            else "STALE_MARK"
            if stale
            else "RISK_HOLD"
            if nav <= 0
            or self.cash < self.restricted()
            or gross > LIMITS.gross * nav + EPS
            or abs(net) > LIMITS.net * nav + EPS
            or any(v > LIMITS.name * nav + EPS for v in names.values())
            or any(v > LIMITS.vintage * nav + EPS for v in vintages.values())
            else "CARRY_PENDING"
            if any(
                position.quantity < 0
                and position.borrow_asof is not None
                and position.borrow_asof < marks[position.ticker].at
                for position in self.positions
            )
            else "READY"
        )
        available = max(ZERO, min(self.cash - self.restricted(), nav - gross))
        return Capacity(nav, gross, net, available, tuple(sorted(names.items())), status)

    def reconcile(self) -> None:
        if self.cash < 0:
            raise ValueError("UNFUNDED_NEGATIVE_CASH")
        if (
            abs(
                self.cash - self.initial_cash - sum((lot_item.cash for lot_item in self.lots), ZERO)
            )
            > EPS
        ):
            raise AssertionError("CASH_ATTRIBUTION")
        marks = dict(self.marks)
        for lot in self.lots:
            if abs(lot.cash + lot.quantity * lot.basis - lot.realized - lot.nontrade_cash) > EPS:
                raise AssertionError("VIRTUAL_BASIS_REALIZATION")
        physical_basis = sum((p.quantity * p.basis for p in self.positions), ZERO)
        physical_realized = sum((p.realized for p in self.positions), ZERO)
        if (
            abs(
                self.cash
                - self.initial_cash
                + physical_basis
                - physical_realized
                - sum((lot_item.nontrade_cash for lot_item in self.lots), ZERO)
            )
            > EPS
        ):
            raise AssertionError("PHYSICAL_BASIS_REALIZATION")
        for ticker in {lot_item.cohort.ticker for lot_item in self.lots} | {
            p.ticker for p in self.positions
        }:
            virtual = sum(
                (lot_item.quantity for lot_item in self.lots if lot_item.cohort.ticker == ticker),
                ZERO,
            )
            physical = sum((p.quantity for p in self.positions if p.ticker == ticker), ZERO)
            if abs(virtual - physical) > EPS:
                raise AssertionError("VIRTUAL_PHYSICAL_SHARES")
        equity = self.initial_cash + sum(
            (
                lot_item.cash
                + lot_item.accrual
                + (
                    lot_item.quantity * marks[lot_item.cohort.ticker].value
                    if lot_item.quantity
                    else ZERO
                )
                for lot_item in self.lots
            ),
            ZERO,
        )
        if abs(self.nav() - equity) > EPS:
            raise AssertionError("EQUITY_ATTRIBUTION")

    def commit(
        self,
        new: "Book",
        journal_id: str,
        point: Price,
        processed: datetime,
        cause: str,
        ticker: str,
        legs: tuple[Leg, ...] = (),
        amount: Decimal = ZERO,
        details: tuple[tuple[str, str], ...] = (),
    ) -> "Book":
        point.validate(processed)
        if any(j.journal_id == journal_id for j in self.journal):
            raise ValueError("DUPLICATE_JOURNAL")
        if self.journal and (
            utc(processed) < utc(self.journal[-1].processed_at)
            or utc(point.at) < utc(self.journal[-1].event_time)
        ):
            raise ValueError("OUT_OF_ORDER_EVENT")
        new.reconcile()
        entry = Journal(
            journal_id,
            utc(point.at),
            utc(point.completed_at or point.at),
            utc(point.available_at),
            utc(processed),
            cause,
            ticker,
            "USD",
            RAW,
            legs,
            amount,
            self.digest(),
            new.digest(),
            point,
            details,
        )
        return replace(new, journal=self.journal + (entry,))

    def mark(self, journal_id: str, ticker: str, point: Price, processed: datetime) -> "Book":
        point.validate(processed)
        marks = dict(self.marks)
        if ticker in marks and point.at < marks[ticker].at:
            raise ValueError("BACKDATED_MARK")
        marks[ticker] = point
        new = replace(self, marks=tuple(sorted(marks.items())))
        return self.commit(
            new, journal_id, point, processed, "MARK_" + new.capacity(processed).status, ticker
        )

    def reserve(
        self,
        journal_id: str,
        cohorts: tuple[Cohort, ...],
        point: Price,
        processed: datetime,
        borrow: BorrowEvidence | None = None,
    ) -> "Book":
        if self.capacity(processed).status != "READY":
            raise ValueError("CAPACITY_HOLD")
        ids = {lot_item.cohort.cohort_id for lot_item in self.lots}
        if len({c.cohort_id for c in cohorts}) != len(cohorts) or any(
            c.cohort_id in ids for c in cohorts
        ):
            raise ValueError("DUPLICATE_COHORT")
        for c in cohorts:
            if c.basis != RAW or point.at > c.entry_deadline or point.at < c.origin:
                raise ValueError("COHORT_ENTRY_CONTRACT")
            if c.requested < 0 and (
                borrow is None
                or not borrow.permits(point.at, True, ticker=c.ticker, quantity=D(str(c.requested)))
            ):
                raise ValueError("SHORT_AVAILABILITY_UNKNOWN")
        marks = dict(self.marks)
        requested = sum((abs(D(str(c.requested))) * marks[c.ticker].value for c in cohorts), ZERO)
        if requested > self.capacity(processed).own_available + EPS:
            raise ValueError("RESERVATION_OWN_CAPITAL")
        lots = self.lots + tuple(
            Lot(c, pending=D(str(c.requested))) for c in sorted(cohorts, key=lambda c: c.cohort_id)
        )
        new = replace(self, lots=lots)
        if new.capacity(processed).status != "READY" or new.cash - new.restricted() < 0:
            raise ValueError("RESERVATION_LIMIT")
        return self.commit(
            new,
            journal_id,
            point,
            processed,
            "RESERVE",
            "MULTI",
            details=(
                ("definitions", str(tuple(sorted(cohorts, key=lambda c: c.cohort_id)))),
                ("borrow_evidence", str(borrow)),
            ),
        )

    def cancel(self, journal_id: str, cohort_id: str, point: Price, processed: datetime) -> "Book":
        lots = tuple(
            replace(lot_item, pending=ZERO, closed=not lot_item.quantity)
            if lot_item.cohort.cohort_id == cohort_id
            else lot_item
            for lot_item in self.lots
        )
        if not any(lot_item.cohort.cohort_id == cohort_id for lot_item in self.lots):
            raise ValueError("UNKNOWN_COHORT")
        return self.commit(
            replace(self, lots=lots),
            journal_id,
            point,
            processed,
            "CANCEL",
            next(
                lot_item.cohort.ticker
                for lot_item in lots
                if lot_item.cohort.cohort_id == cohort_id
            ),
        )

    def execute(
        self,
        journal_id: str,
        ticker: str,
        deltas: tuple[tuple[str, Decimal], ...],
        point: Price,
        processed: datetime,
        external_price: Decimal,
        external_quantity: Decimal,
        fee: Decimal = ZERO,
        borrow: BorrowEvidence | None = None,
        cause: str = "FIXED_FILL",
    ) -> "Book":
        point.validate(processed)
        if cause in ("REBALANCE", "RESIZE"):
            raise ValueError("DYNAMIC_REBALANCING_DISABLED")
        both = any(q > 0 for _, q in deltas) and any(q < 0 for _, q in deltas)
        if both and point.available_at > point.at:
            raise ValueError("CONTEMPORANEOUS_INTERNAL_REFERENCE_UNAVAILABLE")
        legs = cross(deltas, point.value, external_price, external_quantity, fee)
        lots = {lot_item.cohort.cohort_id: lot_item for lot_item in self.lots}
        positions = {p.ticker: p for p in self.positions}
        previous = positions.get(ticker, Physical(ticker))
        if (
            previous.quantity < 0
            and previous.borrow_asof is not None
            and point.at > previous.borrow_asof
        ):
            raise ValueError("BORROW_ACCRUAL_REQUIRED")
        entry = False
        for leg in legs:
            if leg.cohort_id not in lots:
                raise ValueError("UNKNOWN_COHORT")
            lot = lots[leg.cohort_id]
            c = lot.cohort
            if c.ticker != ticker or lot.closed:
                raise ValueError("CLOSED_OR_WRONG_TICKER")
            opening = leg.quantity * D(str(c.requested)) > 0
            if opening:
                entry = True
                if (
                    point.at > c.entry_deadline
                    or leg.quantity * lot.pending <= 0
                    or abs(leg.quantity) > abs(lot.pending) + EPS
                ):
                    raise ValueError("ENTRY_EXPIRY_OR_OVERFILL")
                pending = lot.pending - leg.quantity
            else:
                if leg.quantity * lot.quantity >= 0 or abs(leg.quantity) > abs(lot.quantity) + EPS:
                    raise ValueError("EXIT_OVERFILL")
                if point.at < c.endpoint and cause not in ("FORCED_BUY_IN", "RISK_LIQUIDATION"):
                    raise ValueError("FIXED_HORIZON_EXIT")
                pending = ZERO
            q, b, real = inventory(lot.quantity, lot.basis, leg.quantity, leg.price)
            lots[leg.cohort_id] = replace(
                lot,
                quantity=q,
                basis=b,
                pending=pending,
                cash=lot.cash - leg.quantity * leg.price - leg.fee,
                realized=lot.realized + real - leg.fee,
                closed=(not q and not pending),
            )
        q, b, real = inventory(previous.quantity, previous.basis, external_quantity, external_price)
        if q < min(previous.quantity, ZERO) and (
            borrow is None or not borrow.permits(point.at, True, ticker=ticker, quantity=q)
        ):
            raise ValueError("PHYSICAL_BORROW_UNAVAILABLE")
        positions[ticker] = Physical(
            ticker, q, b, previous.realized + real - fee, point.at if q < 0 else None
        )
        marks = dict(self.marks)
        marks[ticker] = point
        new = replace(
            self,
            cash=self.cash - external_quantity * external_price - fee,
            lots=tuple(lots[k] for k in sorted(lots)),
            positions=tuple(positions[k] for k in sorted(positions)),
            marks=tuple(sorted(marks.items())),
        )
        if entry and new.capacity(processed).status != "READY":
            raise ValueError("POST_FILL_RISK_HOLD")
        return self.commit(
            new,
            journal_id,
            point,
            processed,
            cause,
            ticker,
            legs,
            -external_quantity * external_price - fee,
            details=(
                ("external_quantity", str(external_quantity)),
                ("external_price", str(external_price)),
                ("fee", str(fee)),
                ("borrow_evidence", str(borrow)),
            ),
        )

    def accrue_borrow(
        self, journal_id: str, ticker: str, point: Price, processed: datetime, rate: Decimal | None
    ) -> "Book":
        positions = {p.ticker: p for p in self.positions}
        pos = positions.get(ticker)
        if rate is None or pos is None or pos.quantity >= 0 or pos.borrow_asof is None:
            raise ValueError("BORROW_RATE_OR_POSITION_UNKNOWN")
        charge = calendar_charge(-pos.quantity * point.value, rate, pos.borrow_asof, point.at)
        shorts = [
            lot_item
            for lot_item in self.lots
            if lot_item.cohort.ticker == ticker and lot_item.quantity < 0
        ]
        denom = sum((-lot_item.quantity for lot_item in shorts), ZERO)
        lots = {lot_item.cohort.cohort_id: lot_item for lot_item in self.lots}
        left = charge
        for i, lot_item in enumerate(
            sorted(shorts, key=lambda lot_item: lot_item.cohort.cohort_id)
        ):
            debit = charge * (-lot_item.quantity) / denom if i < len(shorts) - 1 else left
            left -= debit
            lots[lot_item.cohort.cohort_id] = replace(lot_item, accrual=lot_item.accrual - debit)
        positions[ticker] = replace(pos, borrow_asof=point.at)
        new = replace(
            self,
            lots=tuple(lots[k] for k in sorted(lots)),
            positions=tuple(positions[k] for k in sorted(positions)),
        )
        return self.commit(
            new,
            journal_id,
            point,
            processed,
            "BORROW_ACCRUAL",
            ticker,
            amount=-charge,
            details=(
                ("annual_rate", str(rate)),
                ("from", pos.borrow_asof.isoformat()),
                ("notional_basis", "interval_end_raw_mark"),
            ),
        )

    def settle_accrual(
        self, journal_id: str, cohort_id: str, point: Price, processed: datetime
    ) -> "Book":
        lot = next(lot_item for lot_item in self.lots if lot_item.cohort.cohort_id == cohort_id)
        if any(c.cohort_id == cohort_id for c in self.claims):
            raise ValueError("USE_DIVIDEND_PAYMENT_DUE_DATE")
        if lot.accrual < 0 and self.cash - self.restricted() < -lot.accrual:
            raise ValueError("FUNDING_INFEASIBLE_ACCRUAL_RETAINED")
        cash = lot.accrual
        updated = replace(
            lot, cash=lot.cash + cash, nontrade_cash=lot.nontrade_cash + cash, accrual=ZERO
        )
        return self.commit(
            replace(
                self,
                cash=self.cash + cash,
                lots=tuple(updated if lot_item == lot else lot_item for lot_item in self.lots),
            ),
            journal_id,
            point,
            processed,
            "SETTLE_ACCRUAL",
            lot.cohort.ticker,
            amount=cash,
        )

    def unresolved_event(
        self, journal_id: str, ticker: str, point: Price, processed: datetime, reason: str
    ) -> "Book":
        return self.commit(
            replace(self, unresolved=self.unresolved + (reason,)),
            journal_id,
            point,
            processed,
            reason,
            ticker,
        )

    def status_event(
        self,
        journal_id: str,
        at: datetime,
        processed: datetime,
        cause: str,
        ticker: str,
        cancel_ids: tuple[str, ...] = (),
        unresolved: bool = False,
    ) -> "Book":
        """Non-price observation: never fabricate a quote to journal a missing bar."""
        if utc(processed) < utc(at):
            raise ValueError("STATUS_CLOCK")
        if any(j.journal_id == journal_id for j in self.journal):
            raise ValueError("DUPLICATE_JOURNAL")
        if self.journal and (
            processed < self.journal[-1].processed_at or at < self.journal[-1].event_time
        ):
            raise ValueError("OUT_OF_ORDER_EVENT")
        lots = tuple(
            replace(lot_item, pending=ZERO, closed=not lot_item.quantity)
            if lot_item.cohort.cohort_id in cancel_ids
            else lot_item
            for lot_item in self.lots
        )
        new = replace(
            self, lots=lots, unresolved=self.unresolved + ((cause,) if unresolved else ())
        )
        new.reconcile()
        journal = Journal(
            journal_id,
            at,
            at,
            processed,
            processed,
            cause,
            ticker,
            "USD",
            RAW,
            (),
            ZERO,
            self.digest(),
            new.digest(),
            None,
            (("cancel_ids", str(cancel_ids)), ("unresolved", str(unresolved))),
        )
        return replace(new, journal=self.journal + (journal,))
