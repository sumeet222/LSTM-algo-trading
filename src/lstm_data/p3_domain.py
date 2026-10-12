"""Universe-injected, explicitly synthetic P3 contracts; no empirical permissions."""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal, localcontext
from pathlib import Path
from typing import Literal

import pandas as pd

from .clocks import ExecutionPlan, execution_plan, session_clock, utc
from .config import digest, fingerprint
from .corporate_actions import number
from .p2_closure import HANDOFF_CONFIG, load_deferred_work

MODE = "ENGINEERING_SYNTHETIC_ONLY"
PRICE_VERSION = "P3:SYNTHETIC_PRICE:v1"
MODEL_VERSION = "P3:SYNTHETIC_SCORE_SCRIPT:v1"
INPUT_VERSION = "P3:SYNTHETIC_INPUT:v1"
SHARE_BASIS = "SYN:RAW_SHARES:v1"


def synthetic_id(value: str) -> None:
    if (
        not value.startswith("SYN:")
        or not value.strip()
        or any(x in value.lower() for x in ("confirmation", "data/raw", "alpaca", "broker"))
    ):
        raise ValueError("SYNTHETIC_ID_REQUIRED_NO_HISTORICAL_SOURCE")


@dataclass(frozen=True)
class UniverseSpec:
    """Generic membership, fixed scientific five-name arity; order resolves ties."""

    version: str
    symbols: tuple[str, ...]
    sectors: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if (
            not self.version.strip()
            or not isinstance(self.symbols, tuple)
            or len(self.symbols) != 5
            or len(set(self.symbols)) != 5
            or any(not s.strip() or s.upper() != s for s in self.symbols)
            or not isinstance(self.sectors, tuple)
            or (self.sectors and tuple(s for s, _ in self.sectors) != self.symbols)
        ):
            raise ValueError("VERSIONED_ORDERED_FIVE_SYMBOL_UNIVERSE_REQUIRED")

    @property
    def universe_id(self) -> str:
        return fingerprint([self.version, self.symbols, self.sectors])

    def check_symbol(self, symbol: str) -> None:
        if symbol not in self.symbols:
            raise ValueError("SYMBOL_OUTSIDE_UNIVERSE")


@dataclass(frozen=True)
class Permission:
    mode: str
    handoff: Path = HANDOFF_CONFIG

    def ensure(self) -> str:
        if self.mode != MODE:
            raise ValueError("P3_REAL_EMPIRICAL_ACTIVITY_NOT_AUTHORIZED")
        entries = load_deferred_work(self.handoff)
        if len(entries) != 16:
            raise ValueError("P3_P2_REGISTER_VERSION_REQUIRED")
        return digest(self.handoff)


@dataclass(frozen=True)
class Frictions:
    universe: UniverseSpec
    bps: Decimal = Decimal(5)
    annual_borrow: Decimal = Decimal(0)
    version: str = "P3_FRICTIONS_V1"

    def __post_init__(self) -> None:
        object.__setattr__(self, "bps", number(self.bps))
        object.__setattr__(self, "annual_borrow", number(self.annual_borrow))
        if (
            self.bps not in {Decimal(x) for x in (0, 2, 5, 10)}
            or self.annual_borrow not in {Decimal(0), Decimal(".005"), Decimal(".03")}
            or self.version != "P3_FRICTIONS_V1"
        ):
            raise ValueError("FROZEN_COST_BORROW_SCENARIOS_REQUIRED")

    @property
    def friction_id(self) -> str:
        return fingerprint(
            [self.universe.universe_id, self.version, str(self.bps), str(self.annual_borrow)]
        )

    def fee(self, quantity: Decimal, price: Decimal) -> Decimal:
        quantity, price = number(quantity), number(price)
        if price <= 0:
            raise ValueError("POSITIVE_FILL_PRICE_REQUIRED")
        with localcontext() as ctx:
            ctx.prec = 40
            return abs(quantity) * price * self.bps / Decimal(10000)


@dataclass(frozen=True)
class Forecast:
    universe: UniverseSpec
    forecast_id: str
    plan: ExecutionPlan
    scores: tuple[float, ...]
    basis: str = "SYNTHETIC"
    model_version: str = MODEL_VERSION
    input_version: str = INPUT_VERSION

    def __post_init__(self) -> None:
        synthetic_id(self.forecast_id)
        if (
            self.basis != "SYNTHETIC"
            or self.model_version != MODEL_VERSION
            or self.input_version != INPUT_VERSION
            or not isinstance(self.scores, tuple)
            or len(self.scores) != len(self.universe.symbols)
            or any(isinstance(s, bool) or not math.isfinite(s) for s in self.scores)
        ):
            raise ValueError("SYNTHETIC_CAUSAL_ORDERED_FORECAST_REQUIRED")
        if self.plan.issuance is None:
            raise ValueError("FORECAST_ISSUANCE_REQUIRED")
        expected = execution_plan(
            session_clock(self.plan.session),
            self.plan.origin,
            issued_at=self.plan.issuance if self.plan.issuance_kind == "ACTUAL" else None,
        )
        if self.plan != expected:
            raise ValueError("P2_CANONICAL_PLAN_REQUIRED")

    @property
    def pair(self) -> tuple[str, str]:
        order = sorted(range(len(self.scores)), key=lambda i: (-self.scores[i], i))
        return self.universe.symbols[order[0]], self.universe.symbols[order[-1]]

    @property
    def constant(self) -> bool:
        return len(set(self.scores)) == 1


@dataclass(frozen=True)
class PriceReference:
    universe: UniverseSpec
    symbol: str
    price: Decimal
    observation_at: pd.Timestamp
    available_at: pd.Timestamp | None
    source_id: str
    kind: Literal["HOURLY_CLOSE_PROXY", "SYNTHETIC_MINUTE_EVENT", "MARK"]
    share_basis: str = SHARE_BASIS
    period_start: pd.Timestamp | None = None
    basis: str = "SYNTHETIC"
    source_version: str = PRICE_VERSION
    provider_fill_claim: bool = False

    def __post_init__(self) -> None:
        self.universe.check_symbol(self.symbol)
        synthetic_id(self.source_id)
        synthetic_id(self.share_basis)
        object.__setattr__(self, "price", number(self.price))
        object.__setattr__(self, "observation_at", utc(self.observation_at))
        if self.available_at is not None:
            object.__setattr__(self, "available_at", utc(self.available_at))
        if (
            self.price <= 0
            or self.basis != "SYNTHETIC"
            or self.source_version != PRICE_VERSION
            or self.provider_fill_claim
            or self.kind not in {"HOURLY_CLOSE_PROXY", "SYNTHETIC_MINUTE_EVENT", "MARK"}
        ):
            raise ValueError("POSITIVE_SYNTHETIC_RAW_REFERENCE_REQUIRED")
        if self.available_at is None:
            raise ValueError("P3_PUBLICATION_UNKNOWN_REJECTED")
        if self.available_at < self.observation_at:
            raise ValueError("REFERENCE_PUBLICATION_BEFORE_OBSERVATION")
        if self.kind == "HOURLY_CLOSE_PROXY":
            if self.period_start is None:
                raise ValueError("COMPLETE_HOUR_REFERENCE_REQUIRED")
            object.__setattr__(self, "period_start", utc(self.period_start))
            if self.observation_at - self.period_start != pd.Timedelta(hours=1):
                raise ValueError("COMPLETE_HOUR_REFERENCE_REQUIRED")
        if (
            self.kind == "SYNTHETIC_MINUTE_EVENT"
            and self.observation_at != self.observation_at.floor("min")
        ):
            raise ValueError("EXPLICIT_MINUTE_EVENT_REQUIRED")

    def reason_at(self, at: pd.Timestamp) -> str:
        at = utc(at)
        if self.available_at is None or self.available_at > at or self.observation_at > at:
            return "FUTURE_OR_UNAVAILABLE_PRICE"
        if at - self.observation_at > pd.Timedelta(minutes=90):
            return "STALE_PRICE_MARK"
        return "REFERENCE_ELIGIBLE"


@dataclass(frozen=True)
class Order:
    universe: UniverseSpec
    order_id: str
    parent_id: str
    at: pd.Timestamp
    symbol: str
    quantity: Decimal
    share_basis: str = SHARE_BASIS

    def __post_init__(self) -> None:
        for name in (self.order_id, self.parent_id, self.share_basis):
            synthetic_id(name)
        self.universe.check_symbol(self.symbol)
        object.__setattr__(self, "at", utc(self.at))
        object.__setattr__(self, "quantity", number(self.quantity))
        if not self.quantity:
            raise ValueError("ZERO_EXTERNAL_ORDER_NOT_PERMITTED")


@dataclass(frozen=True)
class Fill:
    universe: UniverseSpec
    fill_id: str
    order: Order
    at: pd.Timestamp
    quantity: Decimal
    reference: PriceReference
    fee: Decimal
    outcome: str = "SCRIPTED_SYNTHETIC_FILL"

    def __post_init__(self) -> None:
        synthetic_id(self.fill_id)
        object.__setattr__(self, "at", utc(self.at))
        object.__setattr__(self, "quantity", number(self.quantity))
        object.__setattr__(self, "fee", number(self.fee))
        if (
            self.universe != self.order.universe
            or self.universe != self.reference.universe
            or self.order.symbol != self.reference.symbol
            or self.at < self.order.at
            or self.quantity * self.order.quantity <= 0
            or abs(self.quantity) > abs(self.order.quantity)
            or self.fee < 0
            or self.reference.share_basis != self.order.share_basis
            or self.reference.reason_at(self.at) != "REFERENCE_ELIGIBLE"
            or self.reference.kind == "MARK"
            or self.outcome != "SCRIPTED_SYNTHETIC_FILL"
        ):
            raise ValueError("VALID_CAUSAL_SYNTHETIC_FILL_REQUIRED")
        clock = session_clock(self.at.tz_convert("America/New_York").date().isoformat())
        if (
            clock.open is None
            or clock.close is None
            or not clock.open <= self.at < clock.close
            or self.at != self.at.floor("min")
        ):
            raise ValueError("RTH_MINUTE_FILL_REQUIRED")
