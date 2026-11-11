"""Pure append-only virtual lot transitions; no historical execution or P&L engine."""
from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
import math


class EventKind(str, Enum):
    ENTRY = 'ENTRY'
    FILL = 'FILL'
    EXIT = 'EXIT'
    CANCEL = 'CANCEL'
    HALT = 'HALT'
    BUY_IN = 'BUY_IN'
    COMMISSION = 'COMMISSION'
    SPREAD_SLIPPAGE = 'SPREAD_SLIPPAGE'
    BORROW_CHARGE = 'BORROW_CHARGE'
    SHORT_AVAILABILITY = 'SHORT_AVAILABILITY'
    DIVIDEND = 'DIVIDEND'
    SPLIT = 'SPLIT'
    FINANCING = 'FINANCING'
    COLLATERAL = 'COLLATERAL'
    LIMIT_REJECTION = 'LIMIT_REJECTION'
    REBALANCE = 'REBALANCE'


@dataclass(frozen=True)
class Event:
    event_id: str
    kind: EventKind
    at: datetime
    quantity: float = 0
    price: float = 0
    amount: float = 0
    basis: str = ''


@dataclass(frozen=True)
class Cohort:
    cohort_id: str
    ticker: str
    requested: float
    budget: float
    origin: datetime
    endpoint: datetime
    entry_deadline: datetime
    basis: str
    provenance: tuple[str, ...]
    status: str = 'CREATED'
    shares: float = 0
    entered: float = 0
    entry_at: datetime | None = None
    entry_price: float | None = None
    exit_at: datetime | None = None
    exit_price: float | None = None
    planned_exit_order_at: datetime | None = None
    events: tuple[Event, ...] = ()

    def __post_init__(self) -> None:
        if (not self.provenance or not math.isfinite(self.requested) or self.requested == 0
                or not math.isfinite(self.budget) or self.budget <= 0
                or not self.origin < self.entry_deadline < self.endpoint):
            raise ValueError('INVALID_COHORT')

    def apply(self, event: Event) -> 'Cohort':
        if any(e.event_id == event.event_id for e in self.events):
            raise ValueError('DUPLICATE_EVENT')
        if event.at < self.origin or (self.events and event.at < self.events[-1].at):
            raise ValueError('NONCHRONOLOGICAL_EVENT')
        if not all(math.isfinite(v) for v in (event.quantity, event.price, event.amount)):
            raise ValueError('FINITE_EVENT_REQUIRED')
        changes: dict = {}
        if event.kind == EventKind.REBALANCE:
            raise ValueError('DYNAMIC_REBALANCING_DISABLED')
        if event.kind == EventKind.ENTRY:
            if self.status != 'CREATED' or event.at > self.entry_deadline:
                raise ValueError('INVALID_ENTRY')
            changes = dict(status='ORDER_PENDING')
        elif event.kind == EventKind.FILL:
            if event.basis != self.basis or event.price <= 0 or event.quantity == 0:
                raise ValueError('FILL_BASIS_PRICE_QUANTITY')
            if not self.events or event.at <= self.events[-1].at:
                raise ValueError('FILL_MUST_FOLLOW_ORDER')
            if self.status in ('ORDER_PENDING', 'PARTIALLY_FILLED'):
                if event.at > self.entry_deadline:
                    raise ValueError('LATE_ENTRY_CANCEL_REQUIRED')
                total = self.entered + event.quantity
                if event.quantity * self.requested <= 0 or abs(total) > abs(self.requested):
                    raise ValueError('OVERFILL_OR_WRONG_SIDE')
                average = ((self.entry_price or 0) * abs(self.entered) + event.price * abs(event.quantity)) / abs(total)
                changes = dict(entered=total, shares=total, entry_at=self.entry_at or event.at,
                               entry_price=average, status='OPEN' if total == self.requested else 'PARTIALLY_FILLED')
            elif self.status == 'EXIT_PENDING':
                if event.at <= self.endpoint or event.quantity * self.shares >= 0 or abs(event.quantity) > abs(self.shares):
                    raise ValueError('INVALID_EXIT_FILL')
                shares = self.shares + event.quantity
                changes = dict(shares=shares, status='CLOSED' if shares == 0 else 'EXIT_PENDING',
                               exit_at=event.at, exit_price=event.price)
            else:
                raise ValueError('NO_PENDING_ORDER')
        elif event.kind == EventKind.EXIT:
            if self.status not in ('OPEN', 'PARTIALLY_FILLED') or event.at < self.endpoint:
                raise ValueError('FIXED_HORIZON_REQUIRED')
            changes = dict(status='EXIT_PENDING', planned_exit_order_at=event.at)
        elif event.kind == EventKind.CANCEL:
            if self.status not in ('CREATED', 'ORDER_PENDING', 'PARTIALLY_FILLED'):
                raise ValueError('NOT_CANCELLABLE')
            changes = dict(status='OPEN' if self.shares else 'REJECTED')
        elif event.kind in (EventKind.HALT, EventKind.BUY_IN, EventKind.SPLIT, EventKind.DIVIDEND,
                            EventKind.BORROW_CHARGE, EventKind.FINANCING):
            # Deliberately stop until an action/fee allocation convention is approved.
            changes = dict(status='UNRESOLVED')
        else:
            raise ValueError('ACCOUNTING_EVENT_UNSUPPORTED_PENDING_STAGE3')
        return replace(self, **changes, events=self.events + (event,))
