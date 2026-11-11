"""Approved incremental trade-print proxies, not measured quote spreads."""

import math
from dataclasses import dataclass
from decimal import ROUND_DOWN, ROUND_UP, Decimal

D = Decimal


@dataclass(frozen=True)
class CostReference:
    mode: str
    volatility_ratio: float = 1.0
    adv20_raw_shares: float = 1.0
    available_at: int = -1

    def rates(self, quantity: Decimal) -> tuple[Decimal, Decimal]:
        if self.mode == "RETAIL_CONSERVATIVE":
            return D(".0005"), D(".0005")
        if self.mode != "MICRO_PRO":
            raise ValueError("UNKNOWN_COST_MODE")
        if not math.isfinite(self.volatility_ratio) or not math.isfinite(self.adv20_raw_shares):
            raise ValueError("NONFINITE_COST_REFERENCE")
        ratio = min(2.0, max(0.5, self.volatility_ratio))
        h = min(0.0006, max(0.0001, 0.0003 * ratio))
        j = min(
            0.0005,
            max(
                0.000025,
                0.0001
                * ratio
                * math.sqrt((float(abs(quantity)) / max(self.adv20_raw_shares, 1.0)) / 0.0001),
            ),
        )
        return D(str(h)), D(str(j))

    def quote(
        self,
        raw: Decimal,
        q: Decimal,
        cumulative: Decimal,
        previously_paid: Decimal,
        decision: int,
    ) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal]:
        if self.available_at > decision:
            raise ValueError("FUTURE_COST_REFERENCE")
        h, j = self.rates(q)
        side = 1 if q > 0 else -1
        external = raw * (1 + (h + j) * side)
        if self.mode == "RETAIL_CONSERVATIVE":
            external = external.quantize(D(".01"), rounding=ROUND_UP if q > 0 else ROUND_DOWN)
            paid = (
                max(D(1), D(".005") * (cumulative + abs(q))).quantize(D(".01"))
                if q
                else previously_paid
            )
        else:
            paid = D(".002") * (cumulative + abs(q)) if q else previously_paid
        fee = paid - previously_paid
        if fee < 0:
            raise ValueError("NEGATIVE_INCREMENTAL_COMMISSION")
        return external, fee, paid, h, j
