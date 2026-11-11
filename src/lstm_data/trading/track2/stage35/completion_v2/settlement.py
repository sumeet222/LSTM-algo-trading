"""V2 pre-event orders / ex-post raw bar settlement. Old V1 remains untouched.

No price observed after submission changes the submitted quantity. Gaps are booked
as economic truth, then reported as breaches. Internal cash cancels exactly.
"""

from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal

from ...stage012.contracts import utc
from ..accounting import Book, Journal, Physical, inventory
from ..borrow_financing import calendar_charge
from ..common import EPS, RAW, ZERO, D, Price, checksum
from ..internal_cross import Leg, cross
from ..portfolio_allocator import Capacity


@dataclass(frozen=True)
class FeeState:
    order_id: str
    shares: Decimal = ZERO
    paid: Decimal = ZERO


@dataclass(frozen=True)
class Request:
    cohort_id: str
    delta: Decimal
    role: str = "ENTRY"


@dataclass(frozen=True)
class NetSubmission:
    order_id: str
    account: str
    arm: str
    ticker: str
    decision_at: datetime
    submitted_at: datetime
    event_minute: datetime
    expiry: datetime | None
    requests: tuple[Request, ...]
    net: Decimal
    external_capacity: Decimal
    prior_volume_available: datetime
    reference_price: Decimal
    borrow_mode: str
    conditional_assumption_id: str


def submit(
    order_id: str,
    account: str,
    arm: str,
    ticker: str,
    requests: tuple[Request, ...],
    decision: datetime,
    submitted: datetime,
    event: datetime,
    expiry: datetime | None,
    prior_price: Price,
    prior_volume: Decimal,
    prior_volume_available: datetime,
    risk_ready: bool,
    borrow_mode: str = "CONDITIONAL_ACADEMIC_SHORT",
    assumption_id: str = "USER_POLICY_V2",
    strict_locate_id: str = "",
) -> NetSubmission:
    """Only prior received state is accepted; no future fill bar argument exists."""
    prior_price.validate(decision)
    if not utc(decision) <= utc(submitted) < utc(event):
        raise ValueError("SUBMISSION_MUST_PRECEDE_EVENT")
    if expiry is not None and event > expiry:
        raise ValueError("ENTRY_EXPIRED")
    if (
        not requests
        or len({r.cohort_id for r in requests}) != len(requests)
        or any(not r.delta.is_finite() or not r.delta for r in requests)
    ):
        raise ValueError("UNIQUE_FINITE_REQUESTS")
    if any(r.role not in ("ENTRY", "EXIT", "FORCED_BUY_IN", "RISK_LIQUIDATION") for r in requests):
        raise ValueError("DYNAMIC_REBALANCING_DISABLED")
    if (
        prior_price.basis != RAW
        or decision - prior_price.at > timedelta(minutes=5)
        or prior_volume_available > decision
        or not prior_volume.is_finite()
        or prior_volume < 0
    ):
        raise ValueError("PRIOR_MARK_VOLUME_UNAVAILABLE_OR_STALE")
    reducing = all(r.role != "ENTRY" for r in requests)
    if not risk_ready and not reducing:
        raise ValueError("RISK_INCREASING_HOLD")
    if any(r.delta < 0 and r.role == "ENTRY" for r in requests):
        if borrow_mode == "STRICT_LOCATE":
            # An arbitrary ID is not observed locate evidence. V2 intentionally fails
            # until a separately verified actual provider/receipt is integrated.
            raise ValueError("STRICT_LOCATE_OBSERVATION_NOT_AVAILABLE")
        if borrow_mode != "CONDITIONAL_ACADEMIC_SHORT" or not assumption_id:
            raise ValueError("BORROW_ASSUMPTION_UNAPPROVED")
    return NetSubmission(
        order_id,
        account,
        arm,
        ticker,
        utc(decision),
        utc(submitted),
        utc(event),
        utc(expiry) if expiry else None,
        tuple(sorted(requests, key=lambda r: r.cohort_id)),
        sum((r.delta for r in requests), ZERO),
        prior_volume * D(".01"),
        utc(prior_volume_available),
        prior_price.value,
        borrow_mode,
        assumption_id,
    )


@dataclass(frozen=True)
class FinalBar:
    start: datetime
    complete: datetime
    available: datetime
    open: Decimal | None
    source_id: str
    vintage: str
    kind: str = "SYNTHETIC"
    basis: str = RAW
    status: str = "VALID"

    def reference(self, posted: datetime) -> Price:
        if self.status != "VALID" or self.open is None or self.vintage != "ORIGINAL_OBSERVED":
            raise ValueError("UNRESOLVED_BAR_OR_CORRECTION_REPLAY_REQUIRED")
        p = Price(
            self.start,
            self.available,
            self.open,
            self.source_id,
            self.basis,
            self.kind,
            self.complete,
        )
        p.validate(posted)
        if self.complete != self.start + timedelta(minutes=1):
            raise ValueError("MINUTE_COMPLETION")
        return p


@dataclass(frozen=True)
class UndatedClaim:
    action_id: str
    cohort_id: str
    amount: Decimal


@dataclass(frozen=True)
class V2Book(Book):
    order_fees: tuple[FeeState, ...] = ()
    emergency_funding_debt: Decimal = ZERO
    undated_claims: tuple[UndatedClaim, ...] = ()
    funding_claims: tuple[tuple[str, Decimal], ...] = ()

    def digest(self) -> str:
        return checksum(
            (
                super().digest(),
                self.order_fees,
                self.emergency_funding_debt,
                self.undated_claims,
                self.funding_claims,
            )
        )

    def capacity(self, at: datetime) -> Capacity:
        result = super().capacity(at)
        return (
            replace(result, status="FUNDING_DEBT_HOLD", own_available=ZERO)
            if self.emergency_funding_debt
            else result
        )

    def settle_accrual(
        self, journal_id: str, cohort_id: str, point: Price, processed: datetime
    ) -> "V2Book":
        if any(c.cohort_id == cohort_id for c in self.undated_claims) or any(
            c.cohort_id == cohort_id for c in self.claims
        ):
            raise ValueError("DIVIDEND_PAY_DATE_OR_CLAIM_RETAINED")
        lot = next(item for item in self.lots if item.cohort.cohort_id == cohort_id)
        if lot.accrual < 0 and self.cash - self.restricted() < -lot.accrual:
            raise ValueError("FUNDING_INFEASIBLE_ACCRUAL_RETAINED")
        updated = replace(
            lot,
            cash=lot.cash + lot.accrual,
            nontrade_cash=lot.nontrade_cash + lot.accrual,
            accrual=ZERO,
        )
        remaining = tuple((key, value) for key, value in self.funding_claims if key != cohort_id)
        new = replace(
            self,
            cash=self.cash + lot.accrual,
            lots=tuple(updated if item == lot else item for item in self.lots),
            funding_claims=remaining,
            emergency_funding_debt=sum((v for _, v in remaining), ZERO),
        )
        return self.commit(
            new,
            journal_id,
            point,
            processed,
            "SETTLE_CARRY_AND_EMERGENCY_FUNDING",
            lot.cohort.ticker,
            amount=lot.accrual,
        )

    def commit(
        self,
        new: Book,
        journal_id: str,
        point: Price,
        processed: datetime,
        cause: str,
        ticker: str,
        legs: tuple[Leg, ...] = (),
        amount: Decimal = ZERO,
        details: tuple[tuple[str, str], ...] = (),
    ) -> "V2Book":
        point.validate(processed)
        if not isinstance(new, V2Book):
            raise ValueError("V2_STATE_REQUIRED")
        if any(j.journal_id == journal_id for j in self.journal):
            raise ValueError("DUPLICATE_JOURNAL")
        if self.journal and (
            processed < self.journal[-1].processed_at or point.at < self.journal[-1].event_time
        ):
            raise ValueError("OUT_OF_ORDER_REQUIRES_REPLAY")
        new.reconcile()
        entry = Journal(
            journal_id,
            point.at,
            point.completed_at or point.at,
            point.available_at,
            processed,
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


def carry_to(
    book: V2Book,
    ticker: str,
    end: datetime,
    rate: Decimal | None,
    posted: datetime,
    journal_id: str,
) -> V2Book:
    """Accrue on PREVIOUS known mark, not interval-end future price; segment each update."""
    positions = {p.ticker: p for p in book.positions}
    pos = positions.get(ticker)
    if pos is None or pos.quantity >= 0:
        return book
    if rate is None or pos.borrow_asof is None:
        raise ValueError("CARRY_PENDING_RATE_OR_FRONTIER_UNKNOWN")
    mark = dict(book.marks)[ticker]
    if end < pos.borrow_asof or mark.available_at > posted:
        raise ValueError("CARRY_CAUSALITY")
    charge = calendar_charge(-pos.quantity * mark.value, rate, pos.borrow_asof, end)
    shorts = sorted(
        (item for item in book.lots if item.cohort.ticker == ticker and item.quantity < 0),
        key=lambda item: item.cohort.cohort_id,
    )
    denom = sum((-item.quantity for item in shorts), ZERO)
    left = charge
    lots = {item.cohort.cohort_id: item for item in book.lots}
    for i, lot in enumerate(shorts):
        part = charge * (-lot.quantity) / denom if i < len(shorts) - 1 else left
        left -= part
        lots[lot.cohort.cohort_id] = replace(lot, accrual=lot.accrual - part)
    positions[ticker] = replace(pos, borrow_asof=end)
    new = replace(
        book,
        lots=tuple(lots[k] for k in sorted(lots)),
        positions=tuple(positions[k] for k in sorted(positions)),
    )
    # A due-time journal reference is a declared accrual basis, not a fabricated market mark.
    reference = replace(
        mark,
        at=end,
        available_at=posted,
        completed_at=end,
        source_id="ACCRUAL_BASIS:" + mark.source_id,
    )
    return book.commit(
        new,
        journal_id,
        reference,
        posted,
        "BORROW_ACT365_PREVIOUS_MARK",
        ticker,
        amount=-charge,
        details=(
            ("from", pos.borrow_asof.isoformat()),
            ("rate", str(rate)),
            ("mark_event", mark.at.isoformat()),
        ),
    )


def settle(
    book: V2Book,
    order: NetSubmission,
    bar: FinalBar,
    posted: datetime,
    external_fraction: Decimal = D(1),
    fee_per_share: Decimal = D(".005"),
    minimum_fee: Decimal = D(1),
    half_spread_bps: Decimal = D(5),
    impact_bps: Decimal = D(5),
) -> V2Book:
    """Post one observed interval. No post-fill rejection on newly observed price/caps."""
    point = bar.reference(posted)
    if point.at != order.event_minute or order.submitted_at >= point.at:
        raise ValueError("ORDER_BAR_TIME_MISMATCH")
    if (
        not ZERO <= external_fraction <= 1
        or min(fee_per_share, minimum_fee, half_spread_bps, impact_bps) < 0
    ):
        raise ValueError("COST_OR_PARTIAL_POLICY")
    q = (
        min(abs(order.net), order.external_capacity)
        * external_fraction
        * (D(1) if order.net > 0 else D(-1))
        if order.net
        else ZERO
    )
    previous_fees = next(
        (f for f in book.order_fees if f.order_id == order.order_id), FeeState(order.order_id)
    )
    paid = (
        max(minimum_fee, fee_per_share * (previous_fees.shares + abs(q)))
        if q
        else previous_fees.paid
    )
    if paid < previous_fees.paid:
        raise ValueError("COST_SCENARIO_CHANGED_MID_ORDER")
    fee = paid - previous_fees.paid
    external = point.value * (
        D(1) + (half_spread_bps + impact_bps) / D(10000) * (D(1) if q > 0 else D(-1))
    )
    legs = cross(
        tuple((r.cohort_id, r.delta) for r in order.requests), point.value, external, q, fee
    )
    lots = {item.cohort.cohort_id: item for item in book.lots}
    positions = {p.ticker: p for p in book.positions}
    old = positions.get(order.ticker, Physical(order.ticker))
    if old.quantity < 0 and old.borrow_asof != point.at:
        raise ValueError("AUTOMATIC_CARRY_MUST_PRECEDE_SETTLEMENT")
    roles = {r.cohort_id: r.role for r in order.requests}
    for leg in legs:
        lot = lots[leg.cohort_id]
        if lot.cohort.ticker != order.ticker or lot.closed:
            raise ValueError("COHORT_OR_TICKER")
        opening = roles[leg.cohort_id] == "ENTRY"
        if opening:
            if (
                leg.quantity * lot.pending <= 0
                or abs(leg.quantity) > abs(lot.pending) + EPS
                or point.at > lot.cohort.entry_deadline
            ):
                raise ValueError("ENTRY_OVERFILL_OR_EXPIRY")
            pending = lot.pending - leg.quantity
        else:
            if leg.quantity * lot.quantity >= 0 or abs(leg.quantity) > abs(lot.quantity) + EPS:
                raise ValueError("EXIT_OVERFILL")
            if point.at < lot.cohort.endpoint and roles[leg.cohort_id] == "EXIT":
                raise ValueError("FIXED_HORIZON")
            pending = ZERO
        qty, basis, real = inventory(lot.quantity, lot.basis, leg.quantity, leg.price)
        lots[leg.cohort_id] = replace(
            lot,
            quantity=qty,
            basis=basis,
            realized=lot.realized + real - leg.fee,
            cash=lot.cash - leg.quantity * leg.price - leg.fee,
            pending=pending,
            closed=not qty and not pending,
        )
    qty, basis, real = inventory(old.quantity, old.basis, q, external)
    positions[order.ticker] = Physical(
        order.ticker, qty, basis, old.realized + real - fee, point.at if qty < 0 else None
    )
    marks = dict(book.marks)
    marks[order.ticker] = point
    fees = {f.order_id: f for f in book.order_fees}
    fees[order.order_id] = FeeState(order.order_id, previous_fees.shares + abs(q), paid)
    cash = book.cash - q * external - fee
    funding_claims = dict(book.funding_claims)
    debt = ZERO
    if cash < 0:
        # Failed buying power on a previously submitted market order is debt, not a
        # retroactive cancel. Explicit liability offsets the forced cash advance.
        debt = -cash
        cash = ZERO
        key = sorted({leg.cohort_id for leg in legs})[0]
        lot = lots[key]
        funding_claims[key] = funding_claims.get(key, ZERO) + debt
        lots[key] = replace(
            lot,
            cash=lot.cash + debt,
            nontrade_cash=lot.nontrade_cash + debt,
            accrual=lot.accrual - debt,
        )
    new = replace(
        book,
        cash=cash,
        lots=tuple(lots[k] for k in sorted(lots)),
        positions=tuple(positions[k] for k in sorted(positions)),
        marks=tuple(sorted(marks.items())),
        order_fees=tuple(fees[k] for k in sorted(fees)),
        emergency_funding_debt=book.emergency_funding_debt + debt,
        funding_claims=tuple(sorted(funding_claims.items())),
    )
    breach = new.capacity(posted).status != "READY" or bool(debt)
    return book.commit(
        new,
        order.order_id + ":" + bar.start.isoformat(),
        point,
        posted,
        "OBSERVED_FILL_RISK_BREACH" if breach else "OBSERVED_FILL",
        order.ticker,
        legs,
        -q * external - fee,
        (
            ("submitted_at", order.submitted_at.isoformat()),
            ("transfer", "EX_POST_RAW_OPEN_NOT_PRETRADE_QUOTE"),
            ("account", order.account),
            ("arm", order.arm),
        ),
    )


def liquidation_requests(book: V2Book, ticker: str) -> tuple[Request, ...]:
    """Prospective response only; caller must submit at a STRICTLY later eligible minute."""
    return tuple(
        Request(item.cohort.cohort_id, -item.quantity, "RISK_LIQUIDATION")
        for item in sorted(book.lots, key=lambda item: item.cohort.cohort_id)
        if item.cohort.ticker == ticker and item.quantity
    )


def split_order_units(
    order: NetSubmission, ratio: Decimal, effective: datetime, available: datetime
) -> NetSubmission:
    """Mechanical split unit change, not a forecast resize; original order stays immutable.

    Unknown/late action notice and an already-effective fill cannot be repaired silently.
    Prior volume capacity is converted into the same new-share units, not re-estimated.
    """
    if (
        not ratio.is_finite()
        or ratio <= 0
        or available > effective
        or effective > order.event_minute
    ):
        raise ValueError("SPLIT_ORDER_UNITS_UNRESOLVED")
    if any(
        r.role == "ENTRY" and r.delta * ratio != (r.delta * ratio).to_integral_value()
        for r in order.requests
    ):
        raise ValueError("SPLIT_PENDING_FRACTION_POLICY_HOLD")
    return replace(
        order,
        requests=tuple(replace(r, delta=r.delta * ratio) for r in order.requests),
        net=order.net * ratio,
        external_capacity=order.external_capacity * ratio,
        reference_price=order.reference_price / ratio,
    )
