"""Synthetic bar-open proxy with prior-volume participation. Not a historical runner."""

from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal

from ..stage012.calendar_schedule import MarketClock
from .accounting import Book
from .borrow_financing import BorrowEvidence
from .common import RAW, ZERO, D, Price
from .execution_clock import OrderWindow


@dataclass(frozen=True)
class CostScenario:
    name: str
    half_spread_bps: Decimal
    impact_bps: Decimal
    per_share: Decimal
    minimum: Decimal
    participation: Decimal = D(".01")

    def cost(self, quantity: Decimal, raw: Decimal) -> tuple[Decimal, Decimal]:
        if (
            min(self.half_spread_bps, self.impact_bps, self.per_share, self.minimum) < 0
            or not ZERO < self.participation <= 1
        ):
            raise ValueError("COST_SCENARIO")
        sign = D(1) if quantity > 0 else D(-1)
        price = raw * (1 + sign * (self.half_spread_bps + self.impact_bps) / D(10000))
        if price <= 0:
            raise ValueError("COST_PRICE_NONPOSITIVE")
        return price, max(self.minimum, abs(quantity) * self.per_share) if quantity else ZERO


@dataclass(frozen=True)
class CommissionState:
    order_id: str
    filled_absolute: Decimal = ZERO
    paid: Decimal = ZERO

    def next_fill(
        self, quantity: Decimal, scenario: CostScenario
    ) -> tuple["CommissionState", Decimal]:
        if not self.order_id or not quantity:
            raise ValueError("COMMISSION_ORDER_ID")
        cumulative = self.filled_absolute + abs(quantity)
        total = max(scenario.minimum, cumulative * scenario.per_share)
        incremental = total - self.paid
        if incremental < 0:
            raise ValueError("COST_SCENARIO_CHANGED_MID_ORDER")
        return CommissionState(self.order_id, cumulative, total), incremental


@dataclass(frozen=True)
class SyntheticBar:
    start: datetime
    available_at: datetime
    open_price: Decimal
    prior_volume: Decimal
    prior_volume_available_at: datetime
    kind: str = "SYNTHETIC"
    halted: bool = False
    basis: str = RAW


@dataclass(frozen=True)
class ExecutionOutcome:
    status: str
    quantity: Decimal = ZERO
    price: Decimal | None = None
    fee: Decimal = ZERO
    fill_time: datetime | None = None
    processed_at: datetime | None = None
    reason: str = ""
    commission_state: CommissionState | None = None


def propose_fill(
    clock: MarketClock,
    order: OrderWindow,
    quantity: Decimal,
    bar: SyntheticBar | None,
    scenario: CostScenario,
    now: datetime,
) -> ExecutionOutcome:
    if bar is not None and bar.kind != "SYNTHETIC":
        raise ValueError("HISTORICAL_ECONOMICS_DISABLED")
    if bar is None or bar.halted:
        return ExecutionOutcome(
            "CANCELLED" if order.kind == "ENTRY" else "UNRESOLVED",
            reason="MISSING_OR_HALTED_NO_INVENTED_FILL",
        )
    if order.deadline is not None and bar.start > order.deadline:
        return ExecutionOutcome("CANCELLED", reason="ENTRY_EXPIRED")
    if (
        bar.start <= order.submission
        or bar.start < order.first_minute
        or bar.prior_volume_available_at > order.submission
        or now < bar.available_at
        or bar.available_at < bar.start + timedelta(minutes=1)
    ):
        raise ValueError("EXECUTION_CAUSALITY")
    # next_observation(submission) is only a marker; verify the supplied bar is in XNYS.
    if clock.next_observation(bar.start - timedelta(minutes=1)) != bar.start:
        raise ValueError("CLOSED_EXCHANGE")
    point = Price(
        bar.start,
        bar.available_at,
        bar.open_price,
        "synthetic-bar-open",
        bar.basis,
        bar.kind,
        bar.start + timedelta(minutes=1),
    )
    point.validate(now)
    if bar.prior_volume < 0:
        raise ValueError("INVALID_PRIOR_VOLUME")
    cap = (bar.prior_volume * scenario.participation).to_integral_value(rounding="ROUND_DOWN")
    filled = min(abs(quantity), cap) * (D(1) if quantity > 0 else D(-1))
    if not filled:
        return ExecutionOutcome("PENDING", reason="NO_PRIOR_VOLUME_CAPACITY")
    price, fee = scenario.cost(filled, bar.open_price)
    return ExecutionOutcome(
        "FILLED" if abs(filled) == abs(quantity) else "PARTIAL",
        filled,
        price,
        fee,
        bar.start,
        now,
        "BAR_OPEN_PROXY_NOT_NBBO",
    )


def apply_synthetic(
    book: Book,
    clock: MarketClock,
    order: OrderWindow,
    ticker: str,
    requests: tuple[tuple[str, Decimal], ...],
    bar: SyntheticBar | None,
    scenario: CostScenario,
    now: datetime,
    journal_id: str,
    borrow: BorrowEvidence | None = None,
    commission: CommissionState | None = None,
) -> tuple[Book, ExecutionOutcome]:
    """Atomic physical order adapter, strictly synthetic. Failed exits retain inventory."""
    net = sum((q for _, q in requests), ZERO)
    result = propose_fill(clock, order, net, bar, scenario, now)
    marked = book
    # An observed market move is retained even when the proposed fill fails risk.
    # This is a synthetic proposal, not evidence a resting broker order was cancelled.
    if bar is not None and not bar.halted:
        point = Price(
            bar.start,
            bar.available_at,
            bar.open_price,
            "synthetic-bar-open",
            bar.basis,
            bar.kind,
            bar.start + timedelta(minutes=1),
        )
        marked = book.mark(journal_id + ":MARK", ticker, point, now)
    if result.status in ("CANCELLED", "UNRESOLVED"):
        updated = marked.status_event(
            journal_id,
            now,
            now,
            result.reason,
            ticker,
            tuple(k for k, _ in requests) if order.kind == "ENTRY" else (),
            order.kind == "EXIT",
        )
        return updated, result
    if result.status == "PENDING":
        return marked, result
    if bar is None or result.price is None:
        raise AssertionError("FILL_NEEDS_BAR")
    state, incremental = (commission or CommissionState(journal_id)).next_fill(
        result.quantity, scenario
    )
    result = replace(result, fee=incremental, commission_state=state)
    external_price = result.price
    if external_price is None:
        raise AssertionError("FILL_PRICE_REQUIRED")
    point = Price(
        bar.start,
        bar.available_at,
        bar.open_price,
        "synthetic-bar-open",
        bar.basis,
        bar.kind,
        bar.start + timedelta(minutes=1),
    )
    try:
        updated = marked.execute(
            journal_id,
            ticker,
            requests,
            point,
            now,
            external_price,
            result.quantity,
            result.fee,
            borrow,
        )
    except ValueError as error:
        reason = "PROPOSED_PROXY_FILL_UNRESOLVED:" + str(error)
        updated = marked.status_event(journal_id, now, now, reason, ticker, unresolved=True)
        return updated, ExecutionOutcome("UNRESOLVED", reason=reason)
    return updated, result
