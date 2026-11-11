"""Fixed holding is the only enabled policy."""
from typing import Protocol
from .cohort_state import Cohort


class SizingPolicy(Protocol):
    def candidate_notional(self, direction: int, base: float, multiplier: float) -> float: ...


class FixedHorizonPolicy:
    dynamic_rebalancing_enabled = False

    def candidate_notional(self, direction: int, base: float, multiplier: float) -> float:
        import math
        if direction not in (-1, 0, 1) or not math.isfinite(base) or base < 0 or not .5 <= multiplier <= 1.5:
            raise ValueError('INVALID_SIZE')
        return direction * base * multiplier

    def on_new_origin(self, existing: tuple[Cohort, ...]) -> tuple[Cohort, ...]:
        return existing


class DynamicRebalancePolicy:
    enabled = False

    def rebalance(self) -> None:
        raise RuntimeError('DYNAMIC_REBALANCING_DISABLED')
