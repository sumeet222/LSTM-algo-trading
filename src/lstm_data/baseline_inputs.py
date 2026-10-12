"""Explicit synthetic FT0 input assertions and one forecast-to-P3 adapter."""

from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd

from .baseline_authority import verify
from .baseline_cache import canonical_apply
from .clocks import ExecutionPlan, utc
from .config import fingerprint
from .ft0_tensor import StockTensor
from .ft0_transforms import ORDER, FloorCertificate, ScalerCertificate
from .m2 import ScheduledCalendar, scheduled_window
from .market_features import MarketScaler, MarketWindow
from .p3_domain import Forecast, Permission, UniverseSpec, synthetic_id

Availability = tuple[tuple[tuple[pd.Timestamp | None, ...], ...], ...]


@dataclass(frozen=True)
class BaselineInput:
    universe: UniverseSpec
    input_id: str
    plan: ExecutionPlan
    stock: StockTensor
    stock_scaler: ScalerCertificate
    stock_floors: FloorCertificate
    available_at: Availability
    basis: str
    market: MarketWindow | None = None
    market_scaler: MarketScaler | None = None

    def validate(
        self, permission: Permission, *, allow_synthetic: bool, context: str = "ASOF"
    ) -> None:
        verify(permission)
        synthetic_id(self.input_id)
        s, scaler, floor = self.stock, self.stock_scaler, self.stock_floors
        if (
            not allow_synthetic
            or self.basis != "SYNTHETIC"
            or not s.synthetic
            or s.source_only
            or not s.input_eligible
            or s.research_ready
            or context not in {"ASOF", "HISTORICAL_TRAINING"}
            or s.application_context != context
            or s.symbols != self.universe.symbols
            or s.channels != ORDER
            or scaler.basis != "SYNTHETIC"
            or floor.basis != "SYNTHETIC"
            or s.scaler_ref != scaler.certificate_id
            or s.floor_ref != floor.certificate_id
            or s.source_binding != scaler.source_binding
            or s.action_binding != scaler.action_binding
            or s.source_binding != floor.source_binding
            or s.action_binding != floor.action_binding
            or scaler.window != floor.window
            or len(s.steps) != 48
            or self.plan.cutoff != s.steps[-1].end
        ):
            raise ValueError("SYNTHETIC_CANONICAL_FT0_CONTEXT_BINDING_REQUIRED")
        calendar = ScheduledCalendar(s.steps[0].session, self.plan.session)
        if s.steps != scheduled_window(calendar, self.plan.session, self.plan.origin):
            raise ValueError("EXACT_48_SCHEDULED_STEPS_REQUIRED")
        if any(
            len(rows) != 5
            for rows in (s.values, s.raw_values, s.mask, s.lineage, self.available_at)
        ):
            raise ValueError("FIVE_STOCK_TENSOR_ROWS_REQUIRED")
        for values, raw, masks, ids, clocks in zip(
            s.values, s.raw_values, s.mask, s.lineage, self.available_at
        ):
            if any(len(rows) != 48 for rows in (values, raw, masks, ids, clocks)):
                raise ValueError("48_STOCK_STEPS_REQUIRED")
            for step, row, original, mask, lineage, times in zip(
                s.steps, values, raw, masks, ids, clocks
            ):
                if any(len(x) != 16 for x in (row, original, mask, lineage, times)) or not all(
                    mask
                ):
                    raise ValueError("COMPLETE_16_CELL_MASK_REQUIRED")
                for feature, value, raw_value, source_id, available in zip(
                    ORDER, row, original, lineage, times
                ):
                    synthetic_id(source_id)
                    if (
                        value is None
                        or raw_value is None
                        or not math.isfinite(value)
                        or not math.isfinite(raw_value)
                        or available is None
                        or utc(available) > step.end
                    ):
                        raise ValueError("CELL_MISSING_FUTURE_OR_UNKNOWN_PUBLICATION")
                    expected, _, _ = canonical_apply(
                        scaler,
                        feature,
                        raw_value,
                        step.end,
                        source_binding=s.source_binding,
                        action_binding=s.action_binding,
                        context=s.application_context,
                        training_origin=self.plan.cutoff,
                    )
                    if expected is None or expected != value:
                        raise ValueError("CANONICAL_SCALER_VALUE_OR_ASOF_MISMATCH")

    def validate_market(self, permission: Permission, *, allow_synthetic: bool) -> None:
        verify(permission)
        m, scaler = self.market, self.market_scaler
        if (
            not allow_synthetic
            or self.basis != "SYNTHETIC"
            or m is None
            or scaler is None
            or scaler.basis != "SYNTHETIC"
            or m.values is None
            or m.research_ready
            or m.application_context != self.stock.application_context
            or m.scheduled_ends != tuple(s.end for s in self.stock.steps)
            or not m.floor_ref
            or not m.scaler_ref
            or len(m.values) != 48
            or len(m.valid_mask) != 48
            or not m.valid_mask[-1]
            or sum(m.valid_mask) < 46
            or len(m.source_ids) != 48
            or len(m.source_ages_seconds) != 48
        ):
            raise ValueError("SYNTHETIC_CAUSAL_D7_46_OF_48_REQUIRED")
        from .ft0_transforms import identity

        if m.scaler_ref != identity(scaler) or m.source_version != scaler.source_version:
            raise ValueError("D7_SCALER_VERSION_REQUIRED")
        for step, values, valid, ids, age in zip(
            self.stock.steps, m.values, m.valid_mask, m.source_ids, m.source_ages_seconds
        ):
            if len(values) != 5 or not all(math.isfinite(v) for v in values):
                raise ValueError("FIVE_FINITE_D7_CHANNELS_REQUIRED")
            if valid:
                if not ids or age is None or not 0 <= age <= 5400:
                    raise ValueError("D7_PUBLICATION_FRESHNESS_REQUIRED")
                for source_id in ids:
                    synthetic_id(source_id)
            elif values != (0.0,) * 5:
                raise ValueError("D7_MISSING_FILL_MUST_BE_STANDARDIZED_ZERO")
            if self.stock.application_context == "ASOF" and step.end < scaler.window.fitted_at:
                raise ValueError("D7_SCALER_NOT_AVAILABLE_AT_STEP")


@dataclass(frozen=True)
class Prediction:
    universe: UniverseSpec
    prediction_id: str
    input_id: str
    plan: ExecutionPlan
    scores: tuple[float, ...]
    method: str
    model_id: str
    basis: str

    def __post_init__(self) -> None:
        for ident in (self.prediction_id, self.input_id, self.model_id):
            synthetic_id(ident)
        if (
            self.basis != "SYNTHETIC"
            or self.method not in {"FT0_M1", "RIDGE_OWN", "RIDGE_MARKET", "UNIFORM_RANDOM"}
            or len(self.scores) != 5
            or any(not math.isfinite(x) for x in self.scores)
        ):
            raise ValueError("SYNTHETIC_FIVE_SCORE_PREDICTION_REQUIRED")

    @property
    def ranking_status(self) -> str:
        return "CONSTANT_PREDICTION" if len(set(self.scores)) == 1 else "ORDERED_PREDICTION"


def forecast_adapter(
    prediction: Prediction, permission: Permission, *, allow_synthetic: bool = False
) -> Forecast:
    verify(permission)
    if not allow_synthetic or prediction.basis != "SYNTHETIC":
        raise ValueError("BASELINE_EMPIRICAL_ACTIVATION_HOLD")
    return Forecast(
        prediction.universe,
        prediction.prediction_id
        + ":MODEL:"
        + fingerprint(
            [
                prediction.universe.universe_id,
                prediction.method,
                prediction.model_id,
                prediction.input_id,
                prediction.scores,
            ]
        ),
        prediction.plan,
        prediction.scores,
    )


def momentum(
    row: BaselineInput, permission: Permission, *, allow_synthetic: bool = False
) -> Prediction:
    row.validate(permission, allow_synthetic=allow_synthetic)
    values = []
    for stock in row.stock.values:
        value = stock[-1][0]
        if value is None:
            raise ValueError("M1_MISSING")
        values.append(value)
    scores = tuple(values)
    return Prediction(
        row.universe,
        row.input_id + ":M1",
        row.input_id,
        row.plan,
        scores,
        "FT0_M1",
        "SYN:FT0_M1_DESCENDING:v1:" + row.stock_scaler.certificate_id,
        "SYNTHETIC",
    )
