"""Net shares are physical; gross virtual risk is reserved conservatively."""
from dataclasses import dataclass
import math
from .cohort_state import Cohort


@dataclass(frozen=True)
class NetOrderIntent:
    ticker: str
    quantity: float
    virtual_deltas: tuple[tuple[str, float], ...]


def net_order(ticker: str, deltas: tuple[tuple[str, float], ...]) -> NetOrderIntent:
    if len({k for k, _ in deltas}) != len(deltas) or not all(math.isfinite(q) for _, q in deltas):
        raise ValueError('UNIQUE_FINITE_DELTAS_REQUIRED')
    return NetOrderIntent(ticker, math.fsum(q for _, q in deltas), deltas)


def allocate_external_fill(order: NetOrderIntent, quantity: float, fee: float = 0
                           ) -> tuple[tuple[str, float, float], ...]:
    """Stable pro rata allocation; crossing virtual claims need later transfer-price policy."""
    if not all(math.isfinite(x) for x in (quantity, fee)) or fee < 0:
        raise ValueError('INVALID_FILL')
    if any(q * order.quantity <= 0 for _, q in order.virtual_deltas):
        raise ValueError('INTERNAL_CROSS_ALLOCATION_UNSUPPORTED')
    if quantity * order.quantity <= 0 or abs(quantity) > abs(order.quantity):
        raise ValueError('INVALID_FILL')
    allocated = []
    remaining_q, remaining_fee = quantity, fee
    for i, (key, q) in enumerate(order.virtual_deltas):
        part = quantity * q / order.quantity if i < len(order.virtual_deltas) - 1 else remaining_q
        cost = fee * abs(q / order.quantity) if i < len(order.virtual_deltas) - 1 else remaining_fee
        allocated.append((key, part, cost))
        remaining_q -= part
        remaining_fee -= cost
    return tuple(allocated)


@dataclass(frozen=True)
class Reservation:
    cohort_id: str
    ticker: str
    signed_notional: float
    cash_collateral: float


@dataclass(frozen=True)
class ReservationBook:
    nav: float
    cash_capacity: float
    reservations: tuple[Reservation, ...] = ()

    def reserve(self, cohort_id: str, ticker: str, signed_notional: float,
                borrow_available: bool | None = None) -> 'ReservationBook':
        if not all(math.isfinite(v) for v in (self.nav, self.cash_capacity, signed_notional)) or self.nav <= 0 or signed_notional == 0:
            raise ValueError('INVALID_CAPACITY')
        if any(r.cohort_id == cohort_id for r in self.reservations):
            raise ValueError('DUPLICATE_RESERVATION')
        if signed_notional < 0 and borrow_available is not True:
            raise ValueError('SHORT_AVAILABILITY_UNKNOWN_OR_REJECTED')
        amount = abs(signed_notional)
        # Proposal: shorts reserve 100% own capital; proceeds never create capacity.
        if (amount > .2 * self.nav or
                sum(abs(r.signed_notional) for r in self.reservations) + amount > self.nav or
                sum(abs(r.signed_notional) for r in self.reservations if r.ticker == ticker) + amount > .1 * self.nav or
                sum(r.cash_collateral for r in self.reservations) + amount > self.cash_capacity):
            raise ValueError('CAPACITY_REJECTED')
        r = Reservation(cohort_id, ticker, signed_notional, amount)
        return ReservationBook(self.nav, self.cash_capacity, self.reservations + (r,))

    def release(self, cohort: Cohort) -> 'ReservationBook':
        if cohort.status not in ('CLOSED', 'REJECTED') or cohort.shares != 0:
            raise ValueError('LIVE_RISK_CANNOT_RELEASE')
        return ReservationBook(self.nav, self.cash_capacity,
                               tuple(r for r in self.reservations if r.cohort_id != cohort.cohort_id))
