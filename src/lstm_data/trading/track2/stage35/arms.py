"""Predeclared dimensionless controls, independent of directional alpha."""

import math
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from statistics import median

from ..stage012.contracts import utc
from ..stage012.risk_sizing import RiskReference
from .policy_config import LIMITS


@dataclass(frozen=True)
class MaturedRisk:
    magnitude: float
    endpoint: datetime
    available_at: datetime
    source_id: str
    horizon_minutes: int = 240
    units: str = "absolute_log_return"
    ticker: str = ""
    slot: str = ""
    fold: str = ""


def size_multiplier(
    arm: str,
    decision: datetime,
    mhat: float,
    reference: RiskReference,
    history: tuple[MaturedRisk, ...] = (),
) -> Decimal:
    if arm == "EQUAL":
        return Decimal(1)
    if arm == "NULL_CONTROL":
        raise ValueError("NULL_SCHEME_REQUIRES_STAGE6_SPECIFICATION")
    if arm == "S2C_RISK":
        return Decimal(str(reference.multiplier(mhat, decision)))
    if arm not in ("ROLLING_RISK", "EWMA_RISK"):
        raise ValueError("UNKNOWN_ARM")
    # Strict frontier BEFORE reading magnitude; never compress known missing past rows.
    eligible = sorted(
        (
            r
            for r in history
            if utc(r.available_at) < utc(decision) and utc(r.endpoint) < utc(decision)
        ),
        key=lambda r: r.endpoint,
    )[-LIMITS.classical_window :]
    if len(eligible) < LIMITS.classical_minimum or len({r.endpoint for r in eligible}) != len(
        eligible
    ):
        raise ValueError("CLASSICAL_RISK_SUPPORT")
    if any(
        (r.ticker, r.slot, r.fold) != (reference.ticker, reference.slot, reference.fold)
        or r.horizon_minutes != 240
        or r.units != "absolute_log_return"
        or not r.source_id
        or r.available_at < r.endpoint
        or not math.isfinite(r.magnitude)
        or r.magnitude < 0
        for r in eligible
    ):
        raise ValueError("CLASSICAL_RISK_MISSING_OR_INVALID")
    if reference.available_at > decision or reference.matured_at >= decision:
        raise ValueError("REFERENCE_NOT_MATURE")
    if arm == "ROLLING_RISK":
        risk = float(median(r.magnitude for r in eligible))
    else:
        variance = eligible[0].magnitude ** 2
        for row in eligible[1:]:
            variance = LIMITS.ewma_decay * variance + (1 - LIMITS.ewma_decay) * row.magnitude**2
        risk = math.sqrt(variance)
    return Decimal(
        str(
            min(
                LIMITS.risk_clip_max,
                max(LIMITS.risk_clip_min, reference.b / max(risk, reference.floor)),
            )
        )
    )
