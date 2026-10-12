"""Physical gross / accrual equity; strict 110% differs from the entry 100% cap."""

from __future__ import annotations

from decimal import Decimal, localcontext

from .p3_accounting import ARITHMETIC
from .p3_domain import UniverseSpec


def physical_risk(
    universe: UniverseSpec,
    equity: Decimal | None,
    balances: tuple[tuple[str, Decimal], ...],
    prices: dict[str, Decimal],
) -> dict:
    if tuple(s for s, _ in balances) != universe.symbols:
        raise ValueError("RISK_UNIVERSE_MISMATCH")
    if any(not p.is_finite() or p <= 0 for p in prices.values()):
        raise ValueError("POSITIVE_FINITE_RISK_MARK_REQUIRED")
    if equity is None or any(s not in prices for s, q in balances if q):
        return {
            "status": "INCOMPLETE",
            "G": None,
            "gross": None,
            "emergency": False,
            "reason": "MISSING_CAUSAL_MARK",
            "universe_id": universe.universe_id,
        }
    if not equity.is_finite() or equity <= 0:
        return {
            "status": "INVALID",
            "G": None,
            "gross": None,
            "emergency": False,
            "reason": "NONPOSITIVE_EQUITY",
            "universe_id": universe.universe_id,
        }
    with localcontext(ARITHMETIC):
        gross = sum((abs(q) * prices[s] for s, q in balances if q), Decimal(0))
        ratio = gross / equity
    return {
        "status": "VALID",
        "G": ratio,
        "gross": gross,
        "equity": equity,
        "emergency": ratio > Decimal("1.10"),
        "reason": "OBSERVED_PHYSICAL_GROSS",
        "universe_id": universe.universe_id,
    }
