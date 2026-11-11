"""Frozen candidate engineering defaults; human review required before economics."""

from dataclasses import asdict, dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Limits:
    gross: Decimal = Decimal("1")
    net: Decimal = Decimal("1")
    name: Decimal = Decimal(".1")
    vintage: Decimal = Decimal(".2")
    lot: Decimal = Decimal("1")
    mark_age_minutes: int = 5
    risk_clip_min: float = 0.5
    risk_clip_max: float = 1.5
    classical_window: int = 60
    classical_minimum: int = 40
    ewma_decay: float = 0.94

    def payload(self) -> dict:
        return asdict(self)


LIMITS = Limits()
