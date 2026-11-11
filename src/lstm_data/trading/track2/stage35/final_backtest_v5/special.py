"""Exact virtual OGN residual allocation; physical terms and cash policy unchanged."""

from dataclasses import replace
from datetime import datetime
from decimal import ROUND_DOWN, Decimal

from ...stage012.calendar_schedule import MarketClock
from ..final_backtest_v4.special import (
    EX,
    Distribution,
    DistributionLot,
    OGNQuote,
    observe,
    pay_cil,
)
from ..final_backtest_v4.special import distribution as frozen_distribution
from ..internal_cross import Leg

D = Decimal
ZERO = D(0)
SCALE = 10**18
TICK = D("1e-18")


def distribution(
    positions: tuple[tuple[str, Decimal, Decimal], ...], clock: MarketClock, pay_sessions: int = 5
) -> Distribution:
    original = frozen_distribution(positions, clock, pay_sessions)
    lots = []
    remainder = original.physical_whole
    for i, lot in enumerate(original.lots):
        whole = (
            lot.whole_attribution.quantize(TICK, rounding=ROUND_DOWN)
            if i < len(original.lots) - 1
            else remainder
        )
        remainder -= whole
        lots.append(
            replace(lot, whole_attribution=whole, fraction_attribution=lot.entitlement - whole)
        )
    state = replace(original, lots=tuple(lots))
    state.validate()
    assert sum((v.whole_attribution for v in state.lots), ZERO) == state.physical_whole
    return state


def cross_exact(
    deltas: tuple[tuple[str, Decimal], ...],
    reference: Decimal,
    external_price: Decimal,
    external_quantity: Decimal,
    fee: Decimal,
) -> tuple[Leg, ...]:
    if len({k for k, _ in deltas}) != len(deltas) or not deltas:
        raise ValueError("UNIQUE_OGN_COHORT_DELTAS")
    if min(reference, external_price) <= 0 or fee < 0:
        raise ValueError("OGN_CROSS_PRICE_OR_FEE")
    units = {}
    for key, q in sorted(deltas):
        integer = q * SCALE
        if not q.is_finite() or not q or integer != integer.to_integral_value():
            raise ValueError("OGN_EXACT_VIRTUAL_UNIT_REQUIRED")
        units[key] = int(integer)
    external = external_quantity * SCALE
    if (
        external != external.to_integral_value()
        or external_quantity != external_quantity.to_integral_value()
    ):
        raise ValueError("OGN_PHYSICAL_WHOLE_SHARES_REQUIRED")
    physical = int(external)
    buys = [k for k, q in units.items() if q > 0]
    sells = [k for k, q in units.items() if q < 0]
    legs = []
    i = j = 0
    while i < len(buys) and j < len(sells):
        buyer, seller = buys[i], sells[j]
        q = min(units[buyer], -units[seller])
        legs += [
            Leg(buyer, D(q) / SCALE, reference, ZERO, True),
            Leg(seller, -D(q) / SCALE, reference, ZERO, True),
        ]
        units[buyer] -= q
        units[seller] += q
        if not units[buyer]:
            i += 1
        if not units[seller]:
            j += 1
    target = sum(units.values())
    if physical and (target * physical <= 0 or abs(physical) > abs(target)) or not physical and fee:
        raise ValueError("OGN_EXTERNAL_RESIDUAL_MISMATCH")
    remaining = physical
    selected = []
    for key, q in units.items():
        if not q or not remaining:
            continue
        amount = min(abs(q), abs(remaining)) * (1 if remaining > 0 else -1)
        selected.append((key, amount))
        remaining -= amount
    if remaining:
        raise AssertionError("OGN_UNALLOCATED_PHYSICAL_FILL")
    fees = fee
    for i, (key, q) in enumerate(selected):
        cost = (
            (fee * abs(D(q) / D(physical))).quantize(D(".01"), rounding=ROUND_DOWN)
            if i < len(selected) - 1
            else fees
        )
        fees -= cost
        legs.append(Leg(key, D(q) / SCALE, external_price, cost, False))
    assert sum(int(leg.quantity * SCALE) for leg in legs) == physical
    assert sum((leg.quantity for leg in legs), ZERO) == external_quantity
    assert sum((leg.fee for leg in legs), ZERO) == fee
    return tuple(legs)


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
    legs = cross_exact(deltas, quote.value, external, net, fee)
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


__all__ = [
    "EX",
    "Distribution",
    "DistributionLot",
    "OGNQuote",
    "observe",
    "pay_cil",
    "distribution",
    "settle_whole",
    "cross_exact",
]
