"""MRK regular-way signed distribution; account-net OGN and conditional CIL.

Tax basis metadata never determines NAV. Actual quote availability and modeled
settlement are distinct; no reference is usable before its receipt.
"""

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from decimal import ROUND_DOWN, ROUND_HALF_EVEN, Decimal

from ...stage012.calendar_schedule import MarketClock
from ..internal_cross import cross

D = Decimal
ZERO = D(0)
EX = datetime(2021, 6, 3, 13, 30, tzinfo=timezone.utc)
CLOSE = datetime(2021, 6, 3, 20, 0, tzinfo=timezone.utc)


@dataclass(frozen=True)
class OGNQuote:
    at: datetime
    complete: datetime
    available: datetime
    value: Decimal
    source_hash: str
    conditional: bool = False

    def validate(self, now: datetime) -> None:
        if (
            not self.at <= self.complete <= self.available <= now
            or self.value <= 0
            or not self.value.is_finite()
            or not self.source_hash
        ):
            raise ValueError("OGN_QUOTE_CAUSALITY_OR_BASIS")
        if self.conditional and self.at < CLOSE:
            raise ValueError("POST_CLOSE_PROXY_CANNOT_PRICE_MORNING")


@dataclass(frozen=True)
class DistributionLot:
    cohort_id: str
    entitlement: Decimal
    whole_attribution: Decimal
    fraction_attribution: Decimal
    original_long_tax_basis: Decimal
    mrk_long_tax_basis: Decimal
    ogn_long_tax_basis: Decimal


@dataclass(frozen=True)
class Distribution:
    lots: tuple[DistributionLot, ...]
    physical_whole: Decimal
    physical_fraction: Decimal
    pay_at: datetime
    mark: OGNQuote | None = None
    cil_reference: OGNQuote | None = None
    whole_settled: bool = False
    cil_paid: bool = False
    whole_fills: tuple[tuple[str, Decimal], ...] = ()
    fee_allocations: tuple[tuple[str, Decimal], ...] = ()
    cost_allocations: tuple[tuple[str, Decimal], ...] = ()

    def validate(self) -> None:
        if (
            sum((lot.entitlement for lot in self.lots), ZERO)
            != self.physical_whole + self.physical_fraction
        ):
            raise AssertionError("OGN_ENTITLEMENT_CONSERVATION")
        if abs(sum((lot.whole_attribution for lot in self.lots), ZERO) - self.physical_whole) > D(
            "1e-20"
        ):
            raise AssertionError("OGN_WHOLE_ATTRIBUTION")
        if abs(
            sum((lot.fraction_attribution for lot in self.lots), ZERO) - self.physical_fraction
        ) > D("1e-20"):
            raise AssertionError("OGN_CIL_ATTRIBUTION")
        if self.physical_whole != self.physical_whole.to_integral_value():
            raise AssertionError("NO_PHYSICAL_FRACTIONAL_OGN")
        for lot in self.lots:
            if lot.mrk_long_tax_basis + lot.ogn_long_tax_basis != lot.original_long_tax_basis:
                raise AssertionError("TAX_BASIS_CREATED_VALUE")

    def values(self, now: datetime) -> tuple[tuple[str, Decimal], ...] | None:
        if not self.lots:
            return ()
        if (
            not self.whole_settled
            and self.mark is None
            or not self.cil_paid
            and self.cil_reference is None
        ):
            return None
        result = []
        for lot in self.lots:
            amount = ZERO
            if not self.whole_settled:
                if self.mark is None:
                    raise AssertionError("MARK")
                self.mark.validate(now)
                amount += (
                    lot.whole_attribution
                    + sum((q for key, q in self.whole_fills if key == lot.cohort_id), ZERO)
                ) * self.mark.value
            if not self.cil_paid:
                if self.cil_reference is None:
                    raise AssertionError("CIL_MARK")
                self.cil_reference.validate(now)
                amount += lot.fraction_attribution * self.cil_reference.value
            result.append((lot.cohort_id, amount))
        return tuple(result)


def entitled(acquired: datetime, disposed: datetime | None) -> bool:
    """Regular-way entitlement follows the stock until the ex transition, not May17."""
    return acquired < EX and (disposed is None or disposed >= EX)


def distribution(
    positions: tuple[tuple[str, Decimal, Decimal], ...], clock: MarketClock, pay_sessions: int = 5
) -> Distribution:
    if pay_sessions not in (1, 5, 10):
        raise ValueError("CIL_PAYMENT_SCENARIO")
    entitlements = [(key, q / D(10), tax if q > 0 else ZERO) for key, q, tax in sorted(positions)]
    net = sum((q for _, q, _ in entitlements), ZERO)
    whole = net.to_integral_value(rounding=ROUND_DOWN)
    fraction = net - whole
    # Proportional signed virtual claims retain opposing gross until actual disposal.
    # Final residual belongs to stable last ID; account shares are rounded only ONCE.
    lots = []
    left_whole = whole
    left_fraction = fraction
    for index, (key, q, tax) in enumerate(entitlements):
        w = q * whole / net if net else ZERO
        f = q - w
        if index == len(entitlements) - 1:
            w = left_whole
            f = left_fraction
        left_whole -= w
        left_fraction -= f
        lots.append(DistributionLot(key, q, w, f, tax, tax * D(".9523"), tax - tax * D(".9523")))
    sessions = list(clock.calendar.loc["2021-06-03":].index)
    if len(sessions) <= pay_sessions:
        raise ValueError("CIL_CALENDAR_END")
    day = str(sessions[pay_sessions])[:10]
    pay = clock.origins(day)[0]
    state = Distribution(tuple(lots), whole, fraction, pay)
    state.validate()
    return state


def observe(
    state: Distribution, quote: OGNQuote, now: datetime, cil_postclose: Decimal | None = None
) -> Distribution:
    quote.validate(now)
    if quote.at < EX:
        raise ValueError("PRE_DISTRIBUTION_MARK")
    reference = state.cil_reference
    if reference is None:
        if cil_postclose is None:
            reference = quote
        elif now >= CLOSE + timedelta(minutes=2):
            reference = OGNQuote(
                CLOSE,
                CLOSE,
                CLOSE + timedelta(minutes=2),
                cil_postclose,
                "OWNER_APPROVED_POSTCLOSE_REFERENCE_SCENARIO",
                True,
            )
    return replace(state, mark=quote, cil_reference=reference)


def settle_whole(
    state: Distribution,
    quote: OGNQuote,
    decision: datetime,
    posted: datetime,
    spread_bps: Decimal = D(5),
    impact_bps: Decimal = D(5),
    per_share: Decimal = D(".005"),
    minimum: Decimal = D(1),
    known_reference: OGNQuote | None = None,
    external_capacity: Decimal | None = None,
    previous_external_shares: Decimal = ZERO,
    previous_fee: Decimal = ZERO,
) -> tuple[Distribution, tuple[tuple[str, Decimal], ...], Decimal]:
    quote.validate(posted)
    if state.whole_settled:
        raise ValueError("DUPLICATE_OGN_DISPOSAL")
    reference = known_reference or state.mark
    if reference is None or reference.available > decision or not decision < quote.at:
        raise ValueError("OGN_FILL_BEFORE_KNOWN_MARK_OR_ORDER")
    remaining = {
        lot.cohort_id: lot.whole_attribution
        + sum((q for key, q in state.whole_fills if key == lot.cohort_id), ZERO)
        for lot in state.lots
    }
    deltas = tuple((key, -q) for key, q in sorted(remaining.items()) if q)
    target = -sum(remaining.values(), ZERO)
    cap = (
        abs(target)
        if external_capacity is None
        else external_capacity.to_integral_value(rounding=ROUND_DOWN)
    )
    if cap < 0:
        raise ValueError("NEGATIVE_OGN_CAPACITY")
    net = min(abs(target), cap) * (1 if target > 0 else -1) if target else ZERO
    if not deltas:
        return replace(state, whole_settled=True), (), ZERO
    fee = (
        (
            max(minimum, (previous_external_shares + abs(net)) * per_share).quantize(D(".01"))
            - previous_fee
        )
        if net
        else ZERO
    )
    external = quote.value * (1 + (spread_bps + impact_bps) / 10000 * (1 if net > 0 else -1))
    external = external.quantize(D(".01"), rounding="ROUND_UP" if net > 0 else ROUND_DOWN)
    legs = cross(deltas, quote.value, external, net, fee)
    amounts = {lot.cohort_id: ZERO for lot in state.lots}
    for leg in legs:
        amounts[leg.cohort_id] += -leg.quantity * leg.price - leg.fee
    if abs(sum(amounts.values(), ZERO) - (-net * external - fee)) > D("1e-18"):
        raise AssertionError("OGN_EXTERNAL_CASH_CONSERVATION")
    fills = state.whole_fills + tuple((leg.cohort_id, leg.quantity) for leg in legs)
    for leg in legs:
        remaining[leg.cohort_id] += leg.quantity
    complete = all(abs(q) <= D("1e-18") for q in remaining.values())
    return (
        replace(
            state,
            whole_settled=complete,
            whole_fills=fills,
            fee_allocations=state.fee_allocations + tuple((leg.cohort_id, leg.fee) for leg in legs),
            cost_allocations=state.cost_allocations
            + tuple(
                (
                    leg.cohort_id,
                    leg.fee
                    + (
                        abs(leg.quantity) * abs(leg.price - quote.value)
                        if not leg.internal
                        else ZERO
                    ),
                )
                for leg in legs
            ),
        ),
        tuple(sorted(amounts.items())),
        fee,
    )


def pay_cil(
    state: Distribution, now: datetime
) -> tuple[Distribution, tuple[tuple[str, Decimal], ...], Decimal]:
    if state.cil_paid or state.cil_reference is None or now < state.pay_at:
        raise ValueError("CIL_NOT_DUE_OR_UNPRICED_OR_DUPLICATE")
    state.cil_reference.validate(now)
    amounts = [
        (lot.cohort_id, lot.fraction_attribution * state.cil_reference.value) for lot in state.lots
    ]
    total = (state.physical_fraction * state.cil_reference.value).quantize(
        D(".01"), rounding=ROUND_HALF_EVEN
    )
    if amounts:
        residual = total - sum((v for _, v in amounts), ZERO)
        key, value = amounts[-1]
        amounts[-1] = (key, value + residual)
    if sum((v for _, v in amounts), ZERO) != total:
        raise AssertionError("CIL_CASH_CONSERVATION")
    return replace(state, cil_paid=True), tuple(amounts), total
