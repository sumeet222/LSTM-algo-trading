"""Stable matched internal legs plus one external residual; exact cash conservation."""

from dataclasses import dataclass
from decimal import Decimal

from .common import ZERO


@dataclass(frozen=True)
class Leg:
    cohort_id: str
    quantity: Decimal
    price: Decimal
    fee: Decimal
    internal: bool


def cross(
    deltas: tuple[tuple[str, Decimal], ...],
    reference: Decimal,
    external_price: Decimal,
    external_quantity: Decimal,
    fee: Decimal,
) -> tuple[Leg, ...]:
    if len({k for k, _ in deltas}) != len(deltas) or not deltas:
        raise ValueError("UNIQUE_COHORT_DELTAS")
    if (
        any(not q.is_finite() or not q for _, q in deltas)
        or min(reference, external_price) <= 0
        or fee < 0
    ):
        raise ValueError("INVALID_CROSS")
    remaining = dict(sorted(deltas))
    buys = sorted(k for k, q in deltas if q > 0)
    sells = sorted(k for k, q in deltas if q < 0)
    legs = []
    i = j = 0
    while i < len(buys) and j < len(sells):
        buyer, seller = buys[i], sells[j]
        q = min(remaining[buyer], -remaining[seller])
        legs.extend((Leg(buyer, q, reference, ZERO, True), Leg(seller, -q, reference, ZERO, True)))
        remaining[buyer] -= q
        remaining[seller] += q
        if not remaining[buyer]:
            i += 1
        if not remaining[seller]:
            j += 1
    net = sum(remaining.values(), ZERO)
    if (
        external_quantity
        and (not net or external_quantity * net < 0 or abs(external_quantity) > abs(net))
    ) or (not external_quantity and fee):
        raise ValueError("EXTERNAL_FILL_MISMATCH")
    keys = sorted(k for k, q in remaining.items() if q)
    left = external_quantity
    fees = fee
    for index, key in enumerate(keys):
        if not external_quantity:
            break
        q = external_quantity * remaining[key] / net if index < len(keys) - 1 else left
        cost = fee * abs(q / external_quantity) if index < len(keys) - 1 else fees
        legs.append(Leg(key, q, external_price, cost, False))
        left -= q
        fees -= cost
    if sum((leg.quantity for leg in legs), ZERO) != external_quantity:
        raise AssertionError("SHARE_CONSERVATION")
    return tuple(legs)
