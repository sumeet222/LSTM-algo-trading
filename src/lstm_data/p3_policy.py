"""Frozen five-name rank-to-intent and nonrebalanced virtual sleeve policies."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext

import pandas as pd

from .clocks import utc
from .corporate_actions import number
from .p3_accounting import ARITHMETIC
from .p3_domain import Forecast, Frictions, UniverseSpec, synthetic_id

D = Decimal


@dataclass(frozen=True)
class PairIntent:
    universe: UniverseSpec
    intent_id: str
    forecast_id: str
    long: str
    short: str
    constant_scores: bool

    def __post_init__(self) -> None:
        synthetic_id(self.intent_id)
        synthetic_id(self.forecast_id)
        self.universe.check_symbol(self.long)
        self.universe.check_symbol(self.short)
        if self.long == self.short:
            raise ValueError("TWO_DISTINCT_INTENT_LEGS_REQUIRED")


def rank_intent(forecast: Forecast) -> PairIntent:
    """No score sign filter, future return, exit quote or label-valid argument."""
    long, short = forecast.pair
    return PairIntent(
        forecast.universe,
        forecast.forecast_id + ":INTENT",
        forecast.forecast_id,
        long,
        short,
        forecast.constant,
    )


@dataclass(frozen=True)
class Sleeve:
    universe: UniverseSpec
    sleeve_id: str
    intent: PairIntent
    entered_at: pd.Timestamp
    expires_at: pd.Timestamp
    quantities: tuple[tuple[str, D], ...]
    pre_entry_equity: D
    exit_reference_at: pd.Timestamp

    def __post_init__(self) -> None:
        synthetic_id(self.sleeve_id)
        for field in ("entered_at", "expires_at", "exit_reference_at"):
            object.__setattr__(self, field, utc(getattr(self, field)))
        object.__setattr__(self, "pre_entry_equity", number(self.pre_entry_equity))
        if (
            self.intent.universe != self.universe
            or tuple(s for s, _ in self.quantities) != self.universe.symbols
            or self.expires_at - self.entered_at != pd.Timedelta(minutes=240)
            or not isinstance(self.quantities, tuple)
            or self.pre_entry_equity <= 0
            or any(not q.is_finite() for _, q in self.quantities)
            or dict(self.quantities)[self.intent.long] <= 0
            or dict(self.quantities)[self.intent.short] >= 0
            or any(
                q != 0 for s, q in self.quantities if s not in {self.intent.long, self.intent.short}
            )
        ):
            raise ValueError("BOUND_ORDERED_240_MINUTE_SLEEVE_REQUIRED")


@dataclass(frozen=True)
class Policy:
    universe: UniverseSpec
    name: str
    version: str = "P3_D5e_V1"

    def __post_init__(self) -> None:
        if self.name not in {"A", "B"} or self.version != "P3_D5e_V1":
            raise ValueError("FROZEN_POLICY_REQUIRED")

    def veto(self, intent: PairIntent, active: tuple[Sleeve, ...]) -> bool:
        if intent.universe != self.universe or any(s.universe != self.universe for s in active):
            raise ValueError("POLICY_UNIVERSE_MISMATCH")
        if self.name == "A":
            return False
        return any(
            dict(s.quantities)[intent.long] < 0 or dict(s.quantities)[intent.short] > 0
            for s in active
        )

    def propose(
        self,
        intent: PairIntent,
        equity: D,
        prices: dict[str, D],
        entered_at: pd.Timestamp,
        expires_at: pd.Timestamp,
        exit_reference_at: pd.Timestamp,
    ) -> Sleeve:
        if intent.universe != self.universe or equity <= 0:
            raise ValueError("POSITIVE_EQUITY_MATCHED_INTENT_REQUIRED")
        if any(
            s not in prices or not prices[s].is_finite() or prices[s] <= 0
            for s in (intent.long, intent.short)
        ):
            raise ValueError("POSITIVE_CAUSAL_PAIR_PRICES_REQUIRED")
        with localcontext(ARITHMETIC):
            leg = D(".2475") * equity
            quantities = tuple(
                (
                    s,
                    leg / prices[s]
                    if s == intent.long
                    else -leg / prices[s]
                    if s == intent.short
                    else D(0),
                )
                for s in self.universe.symbols
            )
        return Sleeve(
            self.universe,
            intent.intent_id + ":SLEEVE",
            intent,
            entered_at,
            expires_at,
            quantities,
            equity,
            exit_reference_at,
        )


def net_target(universe: UniverseSpec, sleeves: tuple[Sleeve, ...]) -> tuple[tuple[str, D], ...]:
    if any(s.universe != universe for s in sleeves):
        raise ValueError("TARGET_UNIVERSE_MISMATCH")
    with localcontext(ARITHMETIC):
        return tuple(
            (symbol, sum((dict(s.quantities)[symbol] for s in sleeves), D(0)))
            for symbol in universe.symbols
        )


def admission(
    frictions: Frictions,
    equity: D,
    physical: tuple[tuple[str, D], ...],
    target: tuple[tuple[str, D], ...],
    prices: dict[str, D],
) -> dict:
    """Full paired post-cost projection, after physical netting; no later fills read."""
    if (
        tuple(s for s, _ in physical) != frictions.universe.symbols
        or tuple(s for s, _ in target) != frictions.universe.symbols
    ):
        raise ValueError("ADMISSION_UNIVERSE_MISMATCH")
    with localcontext(ARITHMETIC):
        old = dict(physical)
        required = {s for s, q in target if q or q != old[s]}
        if not required <= prices.keys():
            return {"accepted": False, "reason": "MISSING_PROJECTION_PRICE"}
        fees = sum((frictions.fee(q - old[s], prices[s]) for s, q in target if q != old[s]), D(0))
        gross = sum((abs(q) * prices[s] for s, q in target if q), D(0))
        post_equity = equity - fees
        accepted = post_equity > 0 and gross <= post_equity
        return {
            "accepted": accepted,
            "reason": "ADMITTED" if accepted else "POST_COST_100_CAP",
            "projected_fee": fees,
            "projected_gross": gross,
            "post_cost_equity": post_equity,
        }
