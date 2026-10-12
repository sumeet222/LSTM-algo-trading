"""Explicit synthetic outcomes; proxy execution and minute exceptions are distinct."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

import pandas as pd

from .clocks import session_clock, utc
from .corporate_actions import number
from .p3_domain import Fill, Order, PriceReference, UniverseSpec


@dataclass(frozen=True)
class ExecutionOffer:
    universe: UniverseSpec
    reference: PriceReference
    fraction: Decimal = Decimal(1)
    outcome: str = "FILLED"
    attempt_allowed: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "fraction", number(self.fraction))
        if (
            self.reference.universe != self.universe
            or not 0 <= self.fraction <= 1
            or self.outcome not in {"FILLED", "PARTIAL", "REJECTED", "CANCELED", "HALT"}
            or (self.outcome == "FILLED" and self.fraction != 1)
            or (self.outcome == "PARTIAL" and not 0 < self.fraction < 1)
            or (self.outcome in {"REJECTED", "CANCELED", "HALT"} and self.fraction != 0)
        ):
            raise ValueError("EXPLICIT_SYNTHETIC_OUTCOME_REQUIRED")


def eligible_offer(
    offer: ExecutionOffer | None,
    at: pd.Timestamp,
    *,
    cutoff: pd.Timestamp | None = None,
    minute: bool = False,
    require_at_cutoff: bool = False,
) -> bool:
    if offer is None or not offer.attempt_allowed:
        return False
    ref, at = offer.reference, utc(at)
    clock = session_clock(at.tz_convert("America/New_York").date().isoformat())
    if (
        clock.open is None
        or clock.close is None
        or not clock.open <= at < clock.close
        or at != at.floor("min")
        or ref.reason_at(at) != "REFERENCE_ELIGIBLE"
    ):
        return False
    if minute:
        return ref.kind == "SYNTHETIC_MINUTE_EVENT" and ref.observation_at == at
    return (
        ref.kind == "HOURLY_CLOSE_PROXY"
        and cutoff is not None
        and ref.observation_at == cutoff
        and ref.available_at is not None
        and (not require_at_cutoff or ref.available_at <= cutoff)
    )


def simulated_fill(
    order: Order, offer: ExecutionOffer, at: pd.Timestamp, fee: Decimal
) -> Fill | None:
    """Outcome is discovered after admission/order; zero quantity is never a fill."""
    if order.universe != offer.universe:
        raise ValueError("FILL_ADAPTER_UNIVERSE_MISMATCH")
    if not offer.fraction:
        return None
    return Fill(
        order.universe,
        order.order_id + ":FILL",
        order,
        at,
        order.quantity * offer.fraction,
        offer.reference,
        fee,
    )
