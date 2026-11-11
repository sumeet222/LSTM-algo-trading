"""Active-state exact accountant with independent physical/virtual conservation.

Historical admission is owned by the research runner. This kernel has no source
reader. Money stays Decimal; float views are ONLY a conservative mark monitor,
confirmed with exact arithmetic before an order or breach response.
"""

from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from decimal import ROUND_DOWN, Decimal

import numpy as np

from ..accounting import inventory
from ..internal_cross import Leg
from .paths import canonical
from .protocol import Scenario

D = Decimal
ZERO = D(0)
EPS = D("1e-8")
YEAR = D(365 * 86400)
SCALE = D(1000000)


@dataclass
class Lot:
    key: str
    ticker: int
    origin: int
    endpoint: int
    deadline: int
    direction: int
    requested: int
    multiplier: Decimal
    quantity: Decimal = ZERO
    pending: Decimal = ZERO
    basis: Decimal = ZERO
    cash: Decimal = ZERO
    nontrade: Decimal = ZERO
    realized: Decimal = ZERO
    borrow: Decimal = ZERO
    funding: Decimal = ZERO
    entry_at: int | None = None
    entry_price: Decimal | None = None
    exit_at: int | None = None
    exit_price: Decimal | None = None
    tax_basis: Decimal = ZERO
    unit_factor: Decimal = D(1)
    proxy: Decimal = ZERO
    fees: Decimal = ZERO
    cost: Decimal = ZERO


@dataclass(frozen=True)
class Request:
    key: str
    delta: Decimal
    role: str


@dataclass
class Order:
    key: str
    ticker: int
    decision: int
    effective: int
    requests: tuple[Request, ...]
    submitted_quantity: Decimal
    prior_volume_available: int
    expiry: int | None
    cumulative_quantity: Decimal = ZERO
    paid_fee: Decimal = ZERO
    status: str = "SUBMITTED"


def integer_cross(
    requests: tuple[Request, ...],
    reference: Decimal,
    external: Decimal,
    executed: Decimal,
    fee: Decimal,
) -> tuple[Leg, ...]:
    """Ordinary shares stay whole even under a participation-limited partial.

    Stable IDs determine residual allocation; no fractional ordinary fills hidden
    in pro-rata arithmetic. Corporate-distribution claims use a separate kernel.
    """
    remaining = {r.key: r.delta for r in sorted(requests, key=lambda r: r.key)}
    if len(remaining) != len(requests) or any(
        q != q.to_integral_value() for q in remaining.values()
    ):
        raise ValueError("WHOLE_UNIQUE_STOCK_DELTAS_REQUIRED")
    buys = [k for k, q in remaining.items() if q > 0]
    sells = [k for k, q in remaining.items() if q < 0]
    legs = []
    i = j = 0
    while i < len(buys) and j < len(sells):
        a, b = buys[i], sells[j]
        q = min(remaining[a], -remaining[b])
        legs.extend((Leg(a, q, reference, ZERO, True), Leg(b, -q, reference, ZERO, True)))
        remaining[a] -= q
        remaining[b] += q
        if not remaining[a]:
            i += 1
        if not remaining[b]:
            j += 1
    target = sum(remaining.values(), ZERO)
    if executed and (target * executed <= 0 or abs(executed) > abs(target)):
        raise ValueError("EXTERNAL_NET_MISMATCH")
    if executed != executed.to_integral_value() or not executed and fee:
        raise ValueError("PHYSICAL_WHOLE_FEE_CONTRACT")
    left = executed
    fees = fee
    selected = []
    for key, q in remaining.items():
        if not left:
            break
        if not q:
            continue
        part = min(abs(left), abs(q)) * (1 if left > 0 else -1)
        selected.append((key, part))
        left -= part
    if left:
        raise AssertionError("UNALLOCATED_EXTERNAL_SHARES")
    for n, (key, q) in enumerate(selected):
        part = (
            (fee * abs(q / executed)).quantize(D(".01"), rounding=ROUND_DOWN)
            if n < len(selected) - 1
            else fees
        )
        fees -= part
        legs.append(Leg(key, q, external, part, False))
    if sum((leg.quantity for leg in legs), ZERO) != executed:
        raise AssertionError("PHYSICAL_VIRTUAL_FILL_CONSERVATION")
    return tuple(legs)


@dataclass
class Account:
    arm: str
    population: str
    scenario: Scenario
    initial: Decimal = D(100000)
    cash: Decimal = D(100000)
    lots: dict[str, Lot] = field(default_factory=dict)
    quantity: np.ndarray = field(default_factory=lambda: np.zeros(20, dtype=np.int64))
    abs_virtual: np.ndarray = field(default_factory=lambda: np.zeros(20, dtype=np.float64))
    physical_basis: list[Decimal] = field(default_factory=lambda: [ZERO] * 20)
    physical_realized: list[Decimal] = field(default_factory=lambda: [ZERO] * 20)
    borrow_anchor: list[int] = field(default_factory=lambda: [0] * 20)
    prices: list[Decimal | None] = field(default_factory=lambda: [None] * 20)
    marks_at: list[int] = field(default_factory=lambda: [-1] * 20)
    volume: list[Decimal | None] = field(default_factory=lambda: [None] * 20)
    volume_available: list[int] = field(default_factory=lambda: [-1] * 20)
    claims: dict[tuple[str, str], tuple[Decimal, int]] = field(default_factory=dict)
    special_values: dict[str, Decimal] = field(default_factory=dict)
    unpriced_special: bool = False
    archived_cash: Decimal = ZERO
    archived_nontrade: Decimal = ZERO
    pending: dict[int, Order] = field(default_factory=dict)
    order_seq: int = 0
    journal_hash: str = "GENESIS"
    maximum_residual: Decimal = ZERO
    commission: Decimal = ZERO
    friction: Decimal = ZERO
    borrow_paid: Decimal = ZERO
    funding_paid: Decimal = ZERO
    funding_at: int | None = None
    archived_proxy: Decimal = ZERO
    dividend_cash: Decimal = ZERO
    special_cash: Decimal = ZERO
    rejected: dict[str, int] = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)
    closed: list[dict] = field(default_factory=list)
    processed_origins: set[int] = field(default_factory=set)
    action_effects: dict[str, str] = field(default_factory=dict)
    risk_hold: bool = False
    nav_incomplete: bool = False

    def reject(self, reason: str, count: int = 1) -> None:
        self.rejected[reason] = self.rejected.get(reason, 0) + count

    def record(self, kind: str, at: int, **fields) -> None:
        row = {
            "kind": kind,
            "posted": at,
            "posted_at_utc": datetime.fromtimestamp(at * 60, timezone.utc).isoformat(),
            "arm": self.arm,
            "population": self.population,
            "scenario": self.scenario.name,
            "state_cash": self.cash,
            "state_restricted_proceeds": self.restricted(),
            "state_physical_shares": self.quantity.tolist(),
            "state_claims": self.claim_total(),
            "state_virtual_gross": self.gross()
            + sum((abs(v) for v in self.special_values.values()), ZERO),
            "state_special_value": sum(self.special_values.values(), ZERO),
            "state_nav": self.nav()
            if not any(self.quantity[j] and at - self.marks_at[j] > 5 for j in range(20))
            else None,
            "previous": self.journal_hash,
            **fields,
        }
        self.journal_hash = canonical(row)
        row["hash"] = self.journal_hash
        self.events.append(row)

    def cancel_unsubmitted(self, key: str, at: int, reason: str) -> None:
        if any(r.key == key for order in self.pending.values() for r in order.requests):
            raise ValueError("SUBMITTED_ORDER_CANNOT_BE_RETRO_CANCELLED")
        lot = self.lots[key]
        if lot.pending:
            quantity = lot.pending
            lot.pending = ZERO
            self.refresh()
            self.record(
                "UNSUBMITTED_ENTRY_CANCELLED", at, lot=key, quantity=quantity, reason=reason
            )

    def claim_total(self) -> Decimal:
        return sum((v for v, _ in self.claims.values()), ZERO)

    def nav(self) -> Decimal | None:
        if self.unpriced_special or self.nav_incomplete:
            return None
        total = self.cash + self.claim_total() + sum(self.special_values.values(), ZERO)
        for j, q in enumerate(self.quantity):
            if q:
                point = self.prices[j]
                if point is None:
                    return None
                total += D(int(q)) * point
        return total

    def gross(self) -> Decimal:
        total = ZERO
        for j, p in enumerate(self.prices):
            if p is not None:
                total += D(str(self.abs_virtual[j])) * p
        return total

    def restricted(self) -> Decimal:
        return sum(
            (-D(int(q)) * self.physical_basis[j] for j, q in enumerate(self.quantity) if q < 0),
            ZERO,
        )

    def refresh(self) -> None:
        self.abs_virtual[:] = 0
        for lot in self.lots.values():
            self.abs_virtual[lot.ticker] += float(abs(lot.quantity) + abs(lot.pending))

    def reconcile(self) -> None:
        attributed = (
            self.initial + self.archived_cash + sum((lot.cash for lot in self.lots.values()), ZERO)
        )
        residual = abs(self.cash - attributed)
        nontrade = self.archived_nontrade + sum((lot.nontrade for lot in self.lots.values()), ZERO)
        basis = sum((D(int(q)) * self.physical_basis[j] for j, q in enumerate(self.quantity)), ZERO)
        physical = abs(
            self.cash - self.initial + basis - sum(self.physical_realized, ZERO) - nontrade
        )
        residual = max(residual, physical)
        for j, q in enumerate(self.quantity):
            virtual = sum((lot.quantity for lot in self.lots.values() if lot.ticker == j), ZERO)
            if virtual != D(int(q)):
                raise AssertionError("SHARE_CONSERVATION")
        for lot in self.lots.values():
            residual = max(
                residual, abs(lot.cash + lot.quantity * lot.basis - lot.realized - lot.nontrade)
            )
        self.maximum_residual = max(self.maximum_residual, residual)
        if residual > EPS:
            raise AssertionError("UNBALANCED_LEDGER:" + str(residual))

    def capacity(self, now: int) -> tuple[Decimal, Decimal, dict[int, Decimal], str]:
        nav = self.nav()
        if nav is None:
            return (
                ZERO,
                ZERO,
                {},
                "UNRESOLVED_EXECUTION" if self.nav_incomplete else "UNPRICED_SPECIAL",
            )
        names = {}
        for j, v in enumerate(self.abs_virtual):
            point = self.prices[j]
            if v and point is not None:
                names[j] = D(str(v)) * point
        names[20] = sum((abs(v) for v in self.special_values.values()), ZERO)
        gross = sum(names.values(), ZERO)
        stale = any(
            self.quantity[j] and (self.prices[j] is None or now - self.marks_at[j] > 5)
            for j in range(20)
        )
        pending_gross = sum(
            (abs(lot.pending) * (self.prices[lot.ticker] or ZERO) for lot in self.lots.values()),
            ZERO,
        )
        liabilities = sum((-v for v, _ in self.claims.values() if v < 0), ZERO)
        free = max(
            ZERO, min(self.cash - self.restricted() - pending_gross - liabilities, nav - gross)
        )
        vintage: dict[int, Decimal] = {}
        for lot in self.lots.values():
            p = self.prices[lot.ticker]
            if p is not None:
                vintage[lot.origin] = (
                    vintage.get(lot.origin, ZERO) + (abs(lot.quantity) + abs(lot.pending)) * p
                )
        for key, value in self.special_values.items():
            if key in self.lots:
                origin = self.lots[key].origin
                vintage[origin] = vintage.get(origin, ZERO) + abs(value)
        breach = (
            nav <= 0
            or gross > nav + EPS
            or any(v > D(".1") * nav + EPS for v in names.values())
            or any(v > D(".2") * nav + EPS for v in vintage.values())
            or self.cash < self.restricted()
        )
        status = "RISK_BREACH" if breach else "STALE_MARK" if stale else "READY"
        return nav, free, names, status

    def accrue(self, integrals: np.ndarray, at: int) -> None:
        """Integral units are exact raw-price microdollar seconds; no unseen endpoint label."""
        for j, q in enumerate(self.quantity):
            end = int(integrals[j])
            old = self.borrow_anchor[j]
            if end < old:
                raise ValueError("BORROW_INTEGRAL_REORDER")
            if q < 0 and end > old:
                charge = D(-int(q)) * D(end - old) / SCALE * self.scenario.borrow / YEAR
                shorts = sorted(
                    (lot for lot in self.lots.values() if lot.ticker == j and lot.quantity < 0),
                    key=lambda item: item.key,
                )
                denom = sum((-lot.quantity for lot in shorts), ZERO)
                left = charge
                for n, lot in enumerate(shorts):
                    part = charge * (-lot.quantity) / denom if n < len(shorts) - 1 else left
                    left -= part
                    lot.cash -= part
                    lot.nontrade -= part
                    lot.borrow += part
                self.cash -= charge
                self.borrow_paid += charge
            if self.scenario.unknown_yield and j in (10, 13) and end > old:
                for lot in self.lots.values():
                    if lot.ticker == j:
                        lot.proxy += (
                            lot.quantity * D(end - old) / SCALE * self.scenario.unknown_yield / YEAR
                        )
            self.borrow_anchor[j] = end
        self.reconcile()

    def fill(
        self, order: Order, raw_open: Decimal, now: int, effective: int, fraction: Decimal = D(1)
    ) -> None:
        # Only touched lots are cloned. Journal publication follows validation;
        # no rejected multi-leg transaction can leave half a book committed.
        self.reconcile()
        lots = dict(self.lots)
        for req in order.requests:
            if req.key not in lots:
                raise ValueError("UNKNOWN_COHORT")
            lots[req.key] = replace(lots[req.key])
        candidate = replace(
            self,
            lots=lots,
            quantity=self.quantity.copy(),
            physical_basis=list(self.physical_basis),
            physical_realized=list(self.physical_realized),
            abs_virtual=self.abs_virtual.copy(),
            events=[],
        )
        proposed = replace(order)
        candidate._fill_candidate(proposed, raw_open, now, effective, fraction)
        receipts = self.events + candidate.events
        candidate.events = receipts
        self.__dict__.update(candidate.__dict__)
        order.__dict__.update(proposed.__dict__)

    def _fill_candidate(
        self, order: Order, raw_open: Decimal, now: int, effective: int, fraction: Decimal = D(1)
    ) -> None:
        if not raw_open.is_finite() or raw_open <= 0:
            raise ValueError("INVALID_EXECUTION_PRICE")
        if order.prior_volume_available > order.decision or now < effective + 1 + self.scenario.lag:
            raise ValueError("FILL_BEFORE_SOURCE_RECEIPT_OR_FUTURE_VOLUME")
        if not order.decision < effective or not ZERO <= fraction <= 1:
            raise ValueError("FILL_ORDER_CLOCK_OR_PARTIAL")
        if order.expiry is not None and effective > order.expiry:
            raise ValueError("LATE_ENTRY_EXECUTION")
        q = (abs(order.submitted_quantity) * fraction).to_integral_value(rounding=ROUND_DOWN) * (
            1 if order.submitted_quantity > 0 else -1
        )
        if not order.submitted_quantity:
            q = ZERO
        paid = (
            max(
                self.scenario.minimum, self.scenario.fee * (order.cumulative_quantity + abs(q))
            ).quantize(D(".01"))
            if q
            else order.paid_fee
        )
        fee = paid - order.paid_fee
        external = raw_open * (
            1 + (self.scenario.spread + self.scenario.impact) / 10000 * (1 if q > 0 else -1)
        )
        external = external.quantize(D(".01"), rounding="ROUND_UP" if q > 0 else ROUND_DOWN)
        legs = integer_cross(order.requests, raw_open, external, q, fee)
        roles = {r.key: r.role for r in order.requests}
        for leg in legs:
            lot = self.lots[leg.cohort_id]
            if roles[lot.key] == "ENTRY":
                if leg.quantity * lot.pending <= 0 or abs(leg.quantity) > abs(lot.pending):
                    raise ValueError("ENTRY_OVERFILL")
            elif leg.quantity * lot.quantity >= 0 or abs(leg.quantity) > abs(lot.quantity):
                raise ValueError("EXIT_OVERFILL")
            if roles[lot.key] == "EXIT" and effective < lot.endpoint:
                raise ValueError("FIXED_ENDPOINT_VIOLATION")
        for leg in legs:
            lot = self.lots[leg.cohort_id]
            if roles[lot.key] == "ENTRY":
                if leg.quantity * lot.pending <= 0 or abs(leg.quantity) > abs(lot.pending):
                    raise ValueError("ENTRY_OVERFILL")
                lot.pending -= leg.quantity
                if lot.entry_at is None:
                    lot.entry_at = effective
                    lot.entry_price = leg.price
                else:
                    old_price = lot.entry_price
                    if old_price is None:
                        raise AssertionError("MISSING_ENTRY_BASIS")
                    lot.entry_price = (
                        abs(lot.quantity) * old_price + abs(leg.quantity) * leg.price
                    ) / (abs(lot.quantity) + abs(leg.quantity))
            else:
                if leg.quantity * lot.quantity >= 0 or abs(leg.quantity) > abs(lot.quantity):
                    raise ValueError("EXIT_OVERFILL")
                if roles[lot.key] == "EXIT" and effective < lot.endpoint:
                    raise ValueError("FIXED_ENDPOINT_VIOLATION")
                lot.exit_at = effective
                lot.exit_price = leg.price
            qty, basis, real = inventory(lot.quantity, lot.basis, leg.quantity, leg.price)
            lot.quantity = qty
            lot.basis = basis
            lot.realized += real - leg.fee
            lot.cash -= leg.quantity * leg.price + leg.fee
            lot.fees += leg.fee
            if not leg.internal:
                lot.cost += abs(leg.quantity) * abs(leg.price - raw_open) + leg.fee
        j = order.ticker
        qty, basis, real = inventory(D(int(self.quantity[j])), self.physical_basis[j], q, external)
        if qty != qty.to_integral_value():
            raise AssertionError("PHYSICAL_FRACTIONAL_ORDINARY_STOCK")
        self.quantity[j] = int(qty)
        self.physical_basis[j] = basis
        self.physical_realized[j] += real - fee
        self.cash -= q * external + fee
        self.commission += fee
        self.friction += abs(q) * abs(external - raw_open)
        order.paid_fee = paid
        order.cumulative_quantity += abs(q)
        filled = {r.key: ZERO for r in order.requests}
        for leg in legs:
            filled[leg.cohort_id] += leg.quantity
        order.requests = tuple(
            Request(r.key, r.delta - filled[r.key], r.role)
            for r in order.requests
            if r.delta - filled[r.key]
        )
        order.submitted_quantity -= q
        order.status = "PARTIALLY_FILLED" if order.submitted_quantity else "OBSERVED"
        self.refresh()
        self.reconcile()
        self.record(
            "FILL",
            now,
            order=order.key,
            ticker=j,
            decision=order.decision,
            decision_at_utc=(
                datetime.fromtimestamp(order.decision * 60, timezone.utc)
                + timedelta(microseconds=1)
            ).isoformat(),
            submitted_at_utc=(
                datetime.fromtimestamp(order.decision * 60, timezone.utc)
                + timedelta(microseconds=1)
            ).isoformat(),
            effective_fill_at_utc=datetime.fromtimestamp(effective * 60, timezone.utc).isoformat(),
            observed_bar_complete_at_utc=datetime.fromtimestamp(
                (effective + 1) * 60, timezone.utc
            ).isoformat(),
            bar_available_at_utc=datetime.fromtimestamp(
                (effective + 1 + self.scenario.lag) * 60, timezone.utc
            ).isoformat(),
            effective=effective,
            reference=raw_open,
            external=q,
            external_price=external,
            fee=fee,
            order_status=order.status,
            order_cumulative_quantity=order.cumulative_quantity,
            order_cumulative_fee=order.paid_fee,
            legs=[
                {
                    "lot": item.cohort_id,
                    "q": item.quantity,
                    "price": item.price,
                    "fee": item.fee,
                    "internal": item.internal,
                }
                for item in legs
            ],
        )

    def credit(self, key: str, amount: Decimal, kind: str, at: int) -> None:
        lot = self.lots[key]
        lot.cash += amount
        lot.nontrade += amount
        self.cash += amount
        self.record(kind, at, lot=key, amount=amount)

    def ex_dividend(
        self, event_id: str, j: int, amount: Decimal, due: int, at: int, truth: str
    ) -> None:
        effect = event_id + ":EX"
        payload = canonical((j, amount, due))
        if effect in self.action_effects:
            if self.action_effects[effect] != payload:
                raise ValueError("CORRECTED_ACTION_REPLAY_REQUIRED")
            return
        if not amount.is_finite() or amount < 0:
            raise ValueError("INVALID_DIVIDEND")
        self.action_effects[effect] = payload
        for lot in self.lots.values():
            if lot.ticker != j or not lot.quantity:
                continue
            key = (event_id, lot.key)
            if key in self.claims:
                raise ValueError("DUPLICATE_DIVIDEND")
            self.claims[key] = (lot.quantity * amount, due)
            self.record(
                "DIVIDEND_EX",
                at,
                lot=lot.key,
                event=event_id,
                amount=lot.quantity * amount,
                due=due,
                truth=truth,
            )
        self.reconcile()

    def pay_dividend(self, event_id: str, at: int) -> None:
        if event_id + ":PAY" in self.action_effects:
            return
        if any(key[0] == event_id and due > at for key, (_, due) in self.claims.items()):
            raise ValueError("DIVIDEND_PAYMENT_BEFORE_DUE")
        self.action_effects[event_id + ":PAY"] = canonical(at)
        keys = [key for key, (_, due) in self.claims.items() if key[0] == event_id and due <= at]
        for key in keys:
            value, _ = self.claims.pop(key)
            self.credit(key[1], value, "DIVIDEND_PAY", at)
            self.dividend_cash += value
        self.reconcile()

    def split(self, j: int, ratio: Decimal, at: int) -> None:
        if not ratio.is_finite() or ratio <= 0:
            raise ValueError("SPLIT_RATIO")
        effect = f"SPLIT:{j}:{at}"
        if effect in self.action_effects:
            if self.action_effects[effect] != canonical(ratio):
                raise ValueError("CORRECTED_SPLIT_REPLAY_REQUIRED")
            return
        for lot in self.lots.values():
            if lot.ticker == j and (
                lot.quantity * ratio != (lot.quantity * ratio).to_integral_value()
                or lot.pending * ratio != (lot.pending * ratio).to_integral_value()
            ):
                raise ValueError("UNRESOLVED_SPLIT_CIL")
        self.action_effects[effect] = canonical(ratio)
        for lot in self.lots.values():
            if lot.ticker == j:
                lot.unit_factor *= ratio
                lot.quantity *= ratio
                lot.pending *= ratio
                lot.basis /= ratio
                if lot.entry_price is not None:
                    lot.entry_price /= ratio
                if lot.quantity != lot.quantity.to_integral_value():
                    raise ValueError("UNRESOLVED_SPLIT_CIL")
        q = D(int(self.quantity[j])) * ratio
        if q != q.to_integral_value():
            raise ValueError("UNRESOLVED_PHYSICAL_SPLIT_CIL")
        self.quantity[j] = int(q)
        self.physical_basis[j] /= ratio
        point = self.prices[j]
        if point is not None:
            self.prices[j] = point / ratio
        for order in self.pending.values():
            if order.ticker == j:
                order.requests = tuple(
                    Request(r.key, r.delta * ratio, r.role) for r in order.requests
                )
                order.submitted_quantity *= ratio
        self.refresh()
        self.reconcile()
        self.record("SPLIT", at, ticker=j, ratio=ratio)

    def compact(self, at: int) -> None:
        claimed = {key[1] for key in self.claims} | set(self.special_values)
        ordered = {r.key for order in self.pending.values() for r in order.requests}
        for key, lot in list(self.lots.items()):
            if lot.quantity or lot.pending or key in claimed or key in ordered:
                continue
            self.closed.append(
                {
                    "key": key,
                    "arm": self.arm,
                    "population": self.population,
                    "scenario": self.scenario.name,
                    "ticker": lot.ticker,
                    "origin": lot.origin,
                    "endpoint": lot.endpoint,
                    "direction": lot.direction,
                    "requested": lot.requested,
                    "unit_factor": lot.unit_factor,
                    "entry_price": lot.entry_price,
                    "exit_price": lot.exit_price,
                    "entry_at": lot.entry_at,
                    "exit_at": lot.exit_at,
                    "cash_pnl": lot.cash,
                    "fees": lot.fees,
                    "cost": lot.cost,
                    "borrow": lot.borrow,
                    "funding": lot.funding,
                    "proxy_standalone": lot.proxy,
                    "closed_at": at,
                }
            )
            self.archived_proxy += lot.proxy
            self.archived_cash += lot.cash
            self.archived_nontrade += lot.nontrade
            del self.lots[key]
        self.refresh()
        self.reconcile()

    def accrue_funding(self, effective: int) -> None:
        if self.funding_at is None:
            self.funding_at = effective
            return
        if effective < self.funding_at:
            raise ValueError("FUNDING_CLOCK_REORDER")
        deficit = max(ZERO, self.restricted() - self.cash)
        charge = deficit * self.scenario.funding * D((effective - self.funding_at) * 60) / YEAR
        self.funding_at = effective
        if not charge:
            return
        weights = {
            lot.key: abs(lot.quantity) * (self.prices[lot.ticker] or ZERO)
            for lot in self.lots.values()
            if lot.quantity
        }
        denom = sum(weights.values(), ZERO)
        left = charge
        if weights:
            for n, (key, w) in enumerate(sorted(weights.items())):
                part = charge * w / denom if n < len(weights) - 1 else left
                left -= part
                lot = self.lots[key]
                lot.cash -= part
                lot.nontrade -= part
                lot.funding += part
        else:
            self.archived_cash -= charge
            self.archived_nontrade -= charge
        self.cash -= charge
        self.funding_paid += charge
        self.reconcile()

    def proxy_total(self) -> Decimal:
        return self.archived_proxy + sum((lot.proxy for lot in self.lots.values()), ZERO)
