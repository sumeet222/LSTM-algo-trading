"""Evidence modes never upgrade unknown locates into historical executability."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Protocol

from ..stage012.contracts import utc
from .common import D


class BorrowState(str, Enum):
    CERTIFIED_OBSERVED = "CERTIFIED_OBSERVED"
    CONDITIONAL_SCENARIO = "CONDITIONAL_SCENARIO"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class BorrowEvidence:
    state: BorrowState
    available_at: datetime
    evidence_id: str
    annual_rate: Decimal | None = None
    reviewer_kind: str = "NONE"
    ticker: str = "*"
    max_shares: Decimal | None = None
    valid_until: datetime | None = None

    def permits(
        self,
        at: datetime,
        synthetic: bool = False,
        ticker: str | None = None,
        quantity: Decimal = Decimal(0),
    ) -> bool:
        if utc(self.available_at) > utc(at) or not self.evidence_id:
            return False
        if self.state == BorrowState.CERTIFIED_OBSERVED:
            return (
                self.reviewer_kind == "EXTERNAL_OBSERVATION"
                and ticker is not None
                and self.ticker == ticker
                and self.max_shares is not None
                and self.max_shares >= abs(quantity)
                and self.valid_until is not None
                and utc(at) <= utc(self.valid_until)
            )
        if self.ticker not in ("*", ticker):
            return False
        return self.state == BorrowState.CONDITIONAL_SCENARIO and self.reviewer_kind == (
            "SYNTHETIC_FIXTURE" if synthetic else "HUMAN_APPROVED_EXTERNAL"
        )


class BorrowAvailabilityProvider(Protocol):
    def evidence(self, ticker: str, at: datetime) -> BorrowEvidence: ...


def calendar_charge(
    notional: Decimal, annual_rate: Decimal, start: datetime, end: datetime
) -> Decimal:
    if (
        not annual_rate.is_finite()
        or annual_rate < 0
        or not notional.is_finite()
        or notional < 0
        or utc(end) < utc(start)
    ):
        raise ValueError("INVALID_CARRY")
    return notional * annual_rate * D(str((utc(end) - utc(start)).total_seconds())) / D(365 * 86400)
