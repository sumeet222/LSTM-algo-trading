"""Immutable, label-free Stage 0–2 boundary objects."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import json
import math


def utc(t: datetime) -> datetime:
    if t.tzinfo is None or t.utcoffset() is None:
        raise ValueError('AWARE_TIME_REQUIRED')
    return t.astimezone(timezone.utc)


@dataclass(frozen=True)
class Observation:
    key: str
    event_time: datetime
    interval_end: datetime
    available_at: datetime
    price_basis: str

    def __post_init__(self) -> None:
        if not utc(self.event_time) <= utc(self.interval_end) <= utc(self.available_at):
            raise ValueError('OBSERVATION_ORDER')


@dataclass(frozen=True)
class FeatureSnapshot:
    ticker: str
    nominal_origin: datetime
    slots: tuple[datetime, ...]
    values: tuple[tuple[float, ...], ...]
    clock: tuple[float, ...]
    masks: tuple[tuple[bool, ...], ...]
    dependencies: tuple[Observation, ...]
    recipe_hash: str
    price_basis: str
    category: str
    valid: bool = True

    def __post_init__(self) -> None:
        if (len(self.values) != 48 or any(len(r) != 16 for r in self.values)
                or len(self.clock) != 10 or len(self.slots) != 48
                or len(self.masks) != 48 or any(len(r) != 16 for r in self.masks)):
            raise ValueError('FIXED_48_16_AND_CLOCK10_REQUIRED')
        times = tuple(utc(t) for t in self.slots)
        if tuple(sorted(set(times))) != times or times[-1] > utc(self.nominal_origin):
            raise ValueError('SCHEDULED_SLOTS_REQUIRED')
        if not self.dependencies:
            raise ValueError('FUTURE_OR_MISSING_INPUT')
        for o in self.dependencies:
            opening_reference = (o.key == 'origin_open_reference'
                and self.nominal_origin.astimezone(ZoneInfo('America/New_York')).strftime('%H:%M') == '09:30'
                and o.event_time == self.nominal_origin
                and o.interval_end == self.nominal_origin + timedelta(minutes=1))
            if o.interval_end > self.nominal_origin and not opening_reference:
                raise ValueError('FUTURE_OR_MISSING_INPUT')
        if any(o.price_basis != self.price_basis for o in self.dependencies):
            raise ValueError('INCOMPATIBLE_PRICE_BASIS')
        if not all(math.isfinite(v) for row in self.values for v in row) or not all(map(math.isfinite, self.clock)):
            raise ValueError('ARCHIVED_FALLBACK_OR_ABSTENTION_REQUIRED')
        if self.category not in ('INTRADAY', 'OVERNIGHT'):
            raise ValueError('CATEGORY_REQUIRED')


@dataclass(frozen=True)
class TrendSignal:
    alpha: float
    direction: int
    references: tuple[Observation, ...]
    reason: str

    def __post_init__(self) -> None:
        if not math.isfinite(self.alpha) or self.direction != (self.alpha > 0) - (self.alpha < 0):
            raise ValueError('TREND_SIGN_MISMATCH')


@dataclass(frozen=True)
class SignalRecord:
    strategy_id: str
    universe_version: str
    ticker: str
    fold_id: str
    model_id: str
    checkpoint_hash: str
    feature_recipe_id: str
    c3_calibration_id: str
    price_basis: str
    input_calendar_id: str
    nominal_origin_utc: datetime
    local_origin_et: str
    source_latest_observed_end_utc: datetime
    feature_ready_utc: datetime
    simulated_or_actual_source_receipt_utc: datetime
    model_inference_complete_utc: datetime
    decision_utc: datetime
    earliest_order_submission_utc: datetime
    earliest_executable_observation_utc: datetime
    nominal_endpoint_utc: datetime
    calibrated_magnitude: float | None
    trend_reference_keys: tuple[str, ...]
    trend_alpha: float
    direction: int
    size_multiplier: float | None
    size_unavailable_reason: str
    input_validity: bool
    eligibility_reason: str
    latency_assumption_id: str
    provenance_flags: tuple[str, ...]
    forecast_target_minutes: int = 240
    forecast_target_kind: str = 'endpoint_abs_log_return'
    forecast_is_trading_return: bool = False

    def __post_init__(self) -> None:
        chain = (self.source_latest_observed_end_utc, self.simulated_or_actual_source_receipt_utc,
                 self.feature_ready_utc, self.model_inference_complete_utc, self.decision_utc,
                 self.earliest_order_submission_utc)
        if any(utc(a) > utc(b) for a, b in zip(chain, chain[1:])):
            raise ValueError('CAUSAL_BARRIER')
        if utc(chain[-1]) >= utc(self.earliest_executable_observation_utc):
            raise ValueError('STRICT_FUTURE_EXECUTION_REQUIRED')
        if self.direction not in (-1, 0, 1) or self.forecast_is_trading_return:
            raise ValueError('SIGNAL_SEMANTICS')

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=lambda v: utc(v).isoformat(), sort_keys=True)
