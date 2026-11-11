"""Candidate inverse endpoint-magnitude sizing; no estimator fitting."""
from dataclasses import dataclass
from datetime import datetime
import math


@dataclass(frozen=True)
class RiskReference:
    ticker: str
    fold: str
    slot: str
    b: float
    floor: float
    matured_at: datetime
    available_at: datetime
    lineage: str

    def multiplier(self, magnitude: float, decision: datetime) -> float:
        if (not self.lineage or self.matured_at >= decision or self.available_at > decision
                or not all(math.isfinite(v) for v in (self.b, self.floor, magnitude))
                or min(self.b, self.floor) <= 0 or magnitude < 0):
            raise ValueError('LEGAL_PREFIX_REFERENCE_REQUIRED')
        return min(1.5, max(0.5, self.b / max(magnitude, self.floor)))
