"""Exact monetary units and synthetic-only economic observations."""

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal

from ..stage012.contracts import utc

D = Decimal
ZERO = D(0)
EPS = D("1e-18")
RAW = "RAW_UNADJUSTED"


def number(value: str | int | Decimal) -> Decimal:
    result = D(value)
    if not result.is_finite():
        raise ValueError("FINITE_DECIMAL_REQUIRED")
    return result


def checksum(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, default=str, separators=(",", ":")).encode()
    ).hexdigest()


@dataclass(frozen=True)
class Price:
    at: datetime
    available_at: datetime
    value: Decimal
    source_id: str
    basis: str = RAW
    kind: str = "SYNTHETIC"
    completed_at: datetime | None = None

    def validate(self, processed: datetime) -> None:
        end = self.completed_at or self.at
        if not utc(self.at) <= utc(end) <= utc(self.available_at) <= utc(processed):
            raise ValueError("PRICE_CAUSALITY")
        if self.kind != "SYNTHETIC":
            raise ValueError("HISTORICAL_ECONOMICS_DISABLED")
        if self.basis != RAW:
            raise ValueError("ADJUSTED_EXECUTION_PRICE_FORBIDDEN")
        if not self.value.is_finite() or self.value <= 0 or not self.source_id:
            raise ValueError("INVALID_RAW_PRICE")

    def payload(self) -> dict:
        return asdict(self)
