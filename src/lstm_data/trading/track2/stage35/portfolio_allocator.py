"""Conservative deterministic current-cross-section allocation; no water filling."""

from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal

from .common import ZERO, D
from .intents import SignalIntent
from .policy_config import LIMITS


@dataclass(frozen=True)
class Capacity:
    nav: Decimal
    gross: Decimal
    net: Decimal
    own_available: Decimal
    names: tuple[tuple[str, Decimal], ...]
    status: str = "READY"


@dataclass(frozen=True)
class Allocation:
    cohort_id: str
    ticker: str
    signed_shares: Decimal
    notional: Decimal
    reason: str


def allocate(
    candidates: tuple[SignalIntent, ...],
    capacity: Capacity,
    prices: dict[str, Decimal],
    lot: Decimal = LIMITS.lot,
) -> tuple[Allocation, ...]:
    if capacity.status != "READY" or capacity.nav <= 0:
        raise ValueError("PORTFOLIO_RISK_HOLD")
    if not candidates:
        return ()
    if len({c.cohort_id for c in candidates}) != len(candidates) or len(
        {c.ticker for c in candidates}
    ) != len(candidates):
        raise ValueError("DUPLICATE_VINTAGE_CANDIDATE")
    if len({(c.origin, c.arm) for c in candidates}) != 1:
        raise ValueError("ONE_ORIGIN_ARM_PER_ALLOCATION")
    if lot <= 0:
        raise ValueError("INVALID_LOT")
    names = dict(capacity.names)
    denom = sum((c.multiplier for c in candidates), ZERO)
    budget = min(
        LIMITS.vintage * capacity.nav,
        max(ZERO, LIMITS.gross * capacity.nav - capacity.gross),
        max(ZERO, capacity.own_available),
    )
    targets = []
    for c in sorted(candidates, key=lambda c: (c.ticker, c.cohort_id)):
        if c.ticker not in prices or not prices[c.ticker].is_finite() or prices[c.ticker] <= 0:
            raise ValueError("MISSING_CURRENT_RAW_PRICE")
        amount = min(
            budget * c.multiplier / denom,
            max(ZERO, LIMITS.name * capacity.nav - names.get(c.ticker, ZERO)),
        )
        targets.append((c, amount))
    signed = sum((D(c.direction) * v for c, v in targets), ZERO)
    scale = D(1)
    if signed > 0:
        scale = min(scale, max(ZERO, (LIMITS.net * capacity.nav - capacity.net) / signed))
    elif signed < 0:
        scale = min(scale, max(ZERO, (LIMITS.net * capacity.nav + capacity.net) / -signed))
    output = []
    for c, amount in targets:
        q = (amount * scale / prices[c.ticker] / lot).to_integral_value(rounding=ROUND_DOWN) * lot
        output.append(
            Allocation(
                c.cohort_id,
                c.ticker,
                D(c.direction) * q,
                q * prices[c.ticker],
                "ALLOCATED" if q else "NO_CAPACITY_OR_ROUNDING_CASH",
            )
        )
    return tuple(output)
