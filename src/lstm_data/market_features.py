"""Frozen D7 U1–U5 mathematics with synthetic certificates and fail-closed clocks.

No empirical SPY fitting executor or scientific approval is provided. Certificates
are caller assertions; even DOCUMENTED inputs do not clear external project gates.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from numbers import Real
from typing import Literal

import numpy as np
import pandas as pd

from .clocks import utc
from .m2 import ScheduledCalendar, ScheduledStep, scheduled_window
from .market_source import SOURCE_VERSION

Basis = Literal["UNKNOWN", "SYNTHETIC", "DOCUMENTED"]
Vector = tuple[float, float, float, float, float]


@dataclass(frozen=True)
class MarketObservation:
    """Hourly or daily raw price observation; publication is separate from period end."""

    period_start: pd.Timestamp
    period_end: pd.Timestamp
    open: float
    close: float
    available_at: pd.Timestamp | None
    basis: Basis
    evidence_id: str
    splits_verified: bool
    source_version: str = SOURCE_VERSION
    adjustment: str = "raw"

    def __post_init__(self) -> None:
        utc(self.period_start)
        utc(self.period_end)
        if self.period_start >= self.period_end:
            raise ValueError("MARKET_PERIOD_REQUIRED")
        if self.available_at is not None:
            utc(self.available_at)
            if self.available_at < self.period_end:
                raise ValueError("MARKET_PUBLICATION_BEFORE_COMPLETION")
        if (self.source_version != SOURCE_VERSION or self.adjustment != "raw"
                or self.basis not in {"UNKNOWN", "SYNTHETIC", "DOCUMENTED"}
                or not self.evidence_id.strip()):
            raise ValueError("MARKET_SOURCE_PROVENANCE_REQUIRED")
        if any(isinstance(x, bool) or not math.isfinite(x) or x <= 0
               for x in (self.open, self.close)):
            raise ValueError("MARKET_POSITIVE_PRICE_REQUIRED")


@dataclass(frozen=True)
class MarketClose:
    """Observed session closing value; no invented session open or daily OHLC."""

    period_end: pd.Timestamp
    close: float
    available_at: pd.Timestamp | None
    basis: Basis
    evidence_id: str
    splits_verified: bool
    source_version: str = SOURCE_VERSION

    def __post_init__(self) -> None:
        utc(self.period_end)
        if self.available_at is not None and utc(self.available_at) < self.period_end:
            raise ValueError("MARKET_PUBLICATION_BEFORE_COMPLETION")
        if (not math.isfinite(self.close) or self.close <= 0 or isinstance(self.close, bool)
                or self.basis not in {"UNKNOWN", "SYNTHETIC", "DOCUMENTED"}
                or not self.evidence_id.strip() or self.source_version != SOURCE_VERSION):
            raise ValueError("MARKET_CLOSE_PROVENANCE_REQUIRED")


def observation_reason(
    row: MarketObservation | None, cutoff: pd.Timestamp, *, allow_synthetic: bool = False,
) -> str:
    """Causal/freshness gate, never a claim of scientific source approval."""
    cutoff = utc(cutoff)
    if row is None:
        return "MISSING_SPY_SOURCE"
    if row.basis == "UNKNOWN" or row.available_at is None:
        return "PUBLICATION_UNKNOWN"
    if row.basis == "SYNTHETIC" and not allow_synthetic:
        return "SYNTHETIC_NOT_AUTHORIZED"
    if not row.splits_verified:
        return "SPLIT_SCOPE_UNVERIFIED"
    if row.period_end > cutoff or row.available_at > cutoff:
        return "FUTURE_OR_LATE_PUBLICATION"
    if cutoff - row.period_end > pd.Timedelta(minutes=90):
        return "STALE_MARKET_STATE"
    return "OBSERVATION_VALID"


def rms(values: tuple[float | None, ...], count: int, minimum: int) -> float | None:
    """Keep scheduled positions. Missing data never shift the rolling window."""
    if len(values) != count:
        return None
    gap = 0
    valid = []
    for value in values:
        if value is None:
            gap += 1
            if gap > 2:
                return None
        else:
            if not math.isfinite(value):
                raise ValueError("FINITE_MARKET_RETURN_REQUIRED")
            gap = 0
            valid.append(value)
    if len(valid) < minimum:
        return None
    return math.sqrt(sum(x * x for x in valid) / len(valid))


@dataclass(frozen=True)
class MarketMeasures:
    timestamp: pd.Timestamp
    hourly_return: float | None
    rms12: float | None
    rms60: float | None
    daily_rms63: float | None
    momentum5: float | None
    momentum20: float | None
    reason: str
    evidence_ids: tuple[str, ...]


class MarketHistory:
    """Exact scheduled index and session closes; daily fields lock to d−1 at each step."""

    def __init__(
        self, calendar: ScheduledCalendar, hours: tuple[MarketObservation, ...],
        closes: dict[str, MarketClose], *, allow_synthetic: bool = False,
    ):
        self.calendar = calendar
        self.allow_synthetic = allow_synthetic
        self.hours = {x.period_end: x for x in hours}
        if len(self.hours) != len(hours):
            raise ValueError("DUPLICATE_MARKET_TIMESTAMP")
        self.closes = dict(closes)
        self.days = tuple(calendar._sessions)
        scheduled = {s.end: s for s in calendar.steps}
        for row in hours:
            step = scheduled.get(row.period_end)
            if step is None or step.start != row.period_start:
                raise ValueError("MARKET_HOUR_NOT_ON_COMPLETE_SESSION_GRID")
        for day, row in closes.items():
            clock = calendar.clock(day)
            if row.period_end != clock.close:
                raise ValueError("GENUINE_SESSION_CLOSE_REQUIRED")

    def _return(self, step: ScheduledStep) -> float | None:
        row = self.hours.get(step.end)
        reason = observation_reason(row, step.end, allow_synthetic=self.allow_synthetic)
        if row is None or reason != "OBSERVATION_VALID":
            return None
        return math.log(row.close / row.open)

    def _close(self, day: str, cutoff: pd.Timestamp) -> float | None:
        row = self.closes.get(day)
        # Daily closes intentionally age across overnight/weekends; 90m applies to
        # current hourly market state, not preceding-session-locked momentum inputs.
        if (row is None or row.basis == "UNKNOWN" or row.available_at is None
                or not row.splits_verified
                or (row.basis == "SYNTHETIC" and not self.allow_synthetic)
                or row.period_end > cutoff or row.available_at > cutoff):
            return None
        return row.close

    def measures(self, step: ScheduledStep) -> MarketMeasures:
        self.calendar.validate_step(step)
        position = self.calendar.steps.index(step)
        window = self.calendar.steps[max(0, position - 59):position + 1]
        returns = tuple(self._return(s) for s in window)
        short, long = rms(returns[-12:], 12, 12), rms(returns, 60, 57)
        di = self.days.index(step.session)
        previous = self.days[max(0, di - 64):di]
        prices = tuple(self._close(d, step.end) for d in previous)
        daily_returns = tuple(None if a is None or b is None else math.log(b / a)
                              for a, b in zip(prices, prices[1:]))
        daily = rms(daily_returns, 63, 60)

        def momentum(length: int) -> float | None:
            chain = prices[-length - 1:]
            if len(chain) != length + 1 or any(x is None for x in chain):
                return None
            first, last = chain[0], chain[-1]
            if first is None or last is None:
                return None
            return math.log(last / first)

        row = self.hours.get(step.end)
        reason = observation_reason(row, step.end, allow_synthetic=self.allow_synthetic)
        ids = tuple(self.hours[s.end].evidence_id for s in window if s.end in self.hours)
        ids += tuple(self.closes[d].evidence_id for d in previous if d in self.closes)
        return MarketMeasures(step.end, self._return(step), short, long, daily,
                              momentum(5), momentum(20), reason, ids)


def history_from_archive(calendar: ScheduledCalendar, hourly: pd.DataFrame) -> MarketHistory:
    """Actual SPY adapter preserves UNKNOWN publication and unverified action scope.

    No modeled end-time availability is installed by this conversion. Session close
    comes from the observed terminal interval (including the retained closing stub).
    """
    required = {"period_start", "period_end", "session", "open", "close", "is_stub",
                "available_at_basis", "source_version", "evidence_id"}
    if not required <= set(hourly.columns) or hourly.empty:
        raise ValueError("SPY_ARCHIVE_SCHEMA_REQUIRED")
    if (not (hourly.available_at_basis == "UNKNOWN").all()
            or not (hourly.source_version == SOURCE_VERSION).all()
            or not hourly.available_at.isna().all()):
        raise ValueError("ARCHIVE_PUBLICATION_MUST_REMAIN_UNKNOWN")

    def timestamp(value: object) -> pd.Timestamp:
        if not isinstance(value, pd.Timestamp):
            raise ValueError("ARCHIVE_TIMESTAMP_REQUIRED")
        return utc(value)

    def price(value: object) -> float:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError("ARCHIVE_NUMERIC_PRICE_REQUIRED")
        return float(value)

    hours = []
    closes: dict[str, MarketClose] = {}
    for row in hourly.itertuples():
        if not isinstance(row.session, str) or not isinstance(row.evidence_id, str):
            raise ValueError("ARCHIVE_SESSION_LINEAGE_REQUIRED")
        start, end = timestamp(row.period_start), timestamp(row.period_end)
        observation = MarketObservation(start, end, price(row.open), price(row.close),
                                        None, "UNKNOWN", row.evidence_id, False)
        if not row.is_stub:
            hours.append(observation)
        clock = calendar.clock(row.session)
        if end == clock.close:
            if row.session in closes:
                raise ValueError("DUPLICATE_DAILY_MARKET_CLOSE")
            if clock.close is None:
                raise ValueError("VALID_SESSION_CLOSE_CLOCK_REQUIRED")
            closes[row.session] = MarketClose(clock.close, observation.close, None, "UNKNOWN",
                                             row.evidence_id, False)
    return MarketHistory(calendar, tuple(hours), closes)


@dataclass(frozen=True)
class MarketFitWindow:
    """Training-only certificate bounds. No confirmation or development-only fitting."""

    start: pd.Timestamp
    stop: pd.Timestamp
    fitted_at: pd.Timestamp
    phase: Literal["INNER_TRAIN", "REFIT"]

    def __post_init__(self) -> None:
        start, stop, fitted = utc(self.start), utc(self.stop), utc(self.fitted_at)
        cap = "2023-07-01" if self.phase == "INNER_TRAIN" else "2024-07-01"
        if (self.phase not in {"INNER_TRAIN", "REFIT"} or start >= stop or fitted < stop
                or start < pd.Timestamp("2020-07-01", tz="America/New_York")
                or stop > pd.Timestamp(cap, tz="America/New_York")):
            raise ValueError("MARKET_PERMITTED_TRAINING_FIT_REQUIRED")

    def contains(self, timestamp: pd.Timestamp) -> bool:
        return self.start <= utc(timestamp) < self.stop


@dataclass(frozen=True)
class MarketFloors:
    hourly: float
    daily: float
    window: MarketFitWindow
    basis: Basis
    evidence_ref: str
    timestamps: tuple[pd.Timestamp, ...]
    daily_timestamps: tuple[pd.Timestamp, ...]
    source_version: str = SOURCE_VERSION

    def __post_init__(self) -> None:
        if (any(isinstance(x, bool) or not math.isfinite(x) or x <= 0
                for x in (self.hourly, self.daily))
                or self.basis not in {"SYNTHETIC", "DOCUMENTED"}
                or self.source_version != SOURCE_VERSION or not self.evidence_ref.strip()
                or not self.timestamps or len(set(self.timestamps)) != len(self.timestamps)
                or not self.daily_timestamps
                or len(set(self.daily_timestamps)) != len(self.daily_timestamps)
                or any(not self.window.contains(t)
                       for t in self.timestamps + self.daily_timestamps)):
            raise ValueError("MARKET_FLOOR_PROVENANCE_AND_POSITIVE_SCALE_REQUIRED")


@dataclass(frozen=True)
class DailyScaleSample:
    timestamp: pd.Timestamp  # actual completed daily observation, not intraday copies
    rms63: float | None


def fit_synthetic_floors(
    rows: tuple[MarketMeasures, ...], daily_rows: tuple[DailyScaleSample, ...],
    window: MarketFitWindow, evidence_ref: str,
    *, allow_synthetic: bool = False,
) -> MarketFloors:
    """Verification-only p05 calculation. Real floor fitting is not authorized here.

    Daily RMS samples have their actual session-close timestamp, rather than an
    intraday timestamp that could wrongly admit a pre-training daily value.
    """
    if not allow_synthetic:
        raise ValueError("EMPIRICAL_MARKET_FITTING_NOT_AUTHORIZED")
    unique = {r.timestamp: r for r in rows}
    if (len(unique) != len(rows) or any(not window.contains(r.timestamp) for r in rows)
            or any(r.reason != "OBSERVATION_VALID" or not r.evidence_ids for r in rows)):
        raise ValueError("UNIQUE_TRAINING_MARKET_TIMESTAMPS_REQUIRED")
    hourly = [x for r in rows for x in (r.rms12, r.rms60) if x is not None and x > 0]
    if any(x is not None and (not math.isfinite(x) or x < 0)
           for r in rows for x in (r.rms12, r.rms60)):
        raise ValueError("VALID_MARKET_SCALE_POPULATION_REQUIRED")
    daily_unique = {r.timestamp: r for r in daily_rows}
    if (len(daily_unique) != len(daily_rows)
            or any(not window.contains(r.timestamp) for r in daily_rows)
            or any(r.rms63 is not None and (not math.isfinite(r.rms63) or r.rms63 < 0)
                   for r in daily_rows)):
        raise ValueError("UNIQUE_TRAINING_DAILY_TIMESTAMPS_REQUIRED")
    daily = [r.rms63 for r in daily_rows if r.rms63 is not None and r.rms63 > 0]
    if not hourly or not daily or not all(math.isfinite(x) for x in hourly + daily):
        raise ValueError("MARKET_POSITIVE_SCALE_POPULATION_INSUFFICIENT")
    return MarketFloors(float(np.percentile(hourly, 5)),
                        float(np.percentile(daily, 5)), window,
                        "SYNTHETIC", evidence_ref, tuple(unique), tuple(daily_unique))


@dataclass(frozen=True)
class MarketVector:
    timestamp: pd.Timestamp
    values: Vector | None
    reason: str
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        utc(self.timestamp)
        if self.values is not None and (
            len(self.values) != 5 or not all(math.isfinite(x) for x in self.values)
        ):
            raise ValueError("EXACTLY_FIVE_FINITE_MARKET_CHANNELS_REQUIRED")


def vector(
    row: MarketMeasures, floors: MarketFloors, *, allow_synthetic: bool = False,
) -> MarketVector:
    """D7 equations only. An implementation-valid vector is not research authorization."""
    reason = row.reason
    if floors.basis == "SYNTHETIC" and not allow_synthetic:
        reason = "SYNTHETIC_FLOOR_NOT_AUTHORIZED"
    # A training observation may be retrospectively transformed within its fit set;
    # future observations require the fit to have completed by their own cutoff.
    if not floors.window.contains(row.timestamp) and row.timestamp < floors.window.fitted_at:
        reason = "MARKET_FLOOR_NOT_AVAILABLE_AT_CUTOFF"
    r, short, long, daily, m5, m20 = (row.hourly_return, row.rms12, row.rms60,
                                    row.daily_rms63, row.momentum5, row.momentum20)
    if reason != "OBSERVATION_VALID":
        return MarketVector(row.timestamp, None, reason, row.evidence_ids)
    if any(x is None for x in (r, short, long, daily, m5, m20)):
        return MarketVector(row.timestamp, None, "MARKET_ROLLING_OR_CHAIN_INCOMPLETE",
                            row.evidence_ids)
    if r is None or short is None or long is None or daily is None or m5 is None or m20 is None:
        raise AssertionError("Unreachable incomplete vector")
    h, d = max(long, floors.hourly), max(daily, floors.daily)
    values = (r / h, math.log(h), math.log(max(short, floors.hourly) / h),
              m5 / (math.sqrt(5) * d), m20 / (math.sqrt(20) * d))
    if not all(math.isfinite(x) for x in values):
        raise ValueError("FINITE_MARKET_VECTOR_REQUIRED")
    return MarketVector(row.timestamp, values, "VECTOR_VALID", row.evidence_ids)


@dataclass(frozen=True)
class MarketScaler:
    centers: Vector
    scales: Vector
    methods: tuple[str, str, str, str, str]
    window: MarketFitWindow
    timestamps: tuple[pd.Timestamp, ...]
    evidence_ref: str
    basis: Basis = "SYNTHETIC"
    source_version: str = SOURCE_VERSION

    def __post_init__(self) -> None:
        if (len(self.centers) != 5 or len(self.scales) != 5 or len(self.methods) != 5
                or not all(math.isfinite(x) for x in self.centers)
                or not all(math.isfinite(x) and x > 0 for x in self.scales)
                or not set(self.methods) <= {
                    "MAD", "IQR_1.349", "AUDITED_POPULATION_SD", "CONSTANT"}
                or self.basis not in {"SYNTHETIC", "DOCUMENTED"}
                or self.source_version != SOURCE_VERSION or not self.evidence_ref.strip()
                or not self.timestamps or len(set(self.timestamps)) != len(self.timestamps)
                or any(not self.window.contains(t) for t in self.timestamps)):
            raise ValueError("MARKET_SCALER_PROVENANCE_REQUIRED")

    def transform(self, values: Vector) -> tuple[Vector, tuple[int, ...]]:
        result = tuple(0. if method == "CONSTANT" else (x - c) / s
                       for x, c, s, method in zip(values, self.centers, self.scales, self.methods))
        novel = tuple(i for i, (x, c, m) in enumerate(zip(values, self.centers, self.methods))
                      if m == "CONSTANT" and x != c)
        return (result[0], result[1], result[2], result[3], result[4]), novel


def fit_synthetic_scaler(
    rows: tuple[MarketVector, ...], window: MarketFitWindow, evidence_ref: str,
    *, allow_synthetic: bool = False,
) -> MarketScaler:
    """Deduplicate identical repeated timestamps; reject conflicting five-stock copies."""
    if not allow_synthetic or not evidence_ref.strip():
        raise ValueError("EMPIRICAL_MARKET_FITTING_NOT_AUTHORIZED")
    unique: dict[pd.Timestamp, Vector] = {}
    for row in rows:
        if (not window.contains(row.timestamp) or row.values is None
                or row.reason != "VECTOR_VALID" or not row.evidence_ids
                or not all(math.isfinite(x) for x in row.values)):
            raise ValueError("VALID_TRAINING_MARKET_VECTORS_REQUIRED")
        previous = unique.get(row.timestamp)
        if previous is not None and previous != row.values:
            raise ValueError("CONFLICTING_MARKET_TIMESTAMP")
        unique[row.timestamp] = row.values
    if not unique:
        raise ValueError("MARKET_SCALER_POPULATION_INSUFFICIENT")
    array = np.array(list(unique.values()), dtype=float)
    centers, scales, methods = [], [], []
    for i in range(5):
        data = array[:, i]
        center = float(np.median(data))
        mad = float(np.median(np.abs(data - center)))
        iqr = float((np.percentile(data, 75) - np.percentile(data, 25)) / 1.349)
        sd = float(np.std(data, ddof=0))
        if mad > 0:
            scale, method = mad, "MAD"
        elif iqr > 0:
            scale, method = iqr, "IQR_1.349"
        elif sd > 0:
            scale, method = sd, "AUDITED_POPULATION_SD"
        else:
            scale, method = 1., "CONSTANT"
        centers.append(center)
        scales.append(scale)
        methods.append(method)
    return MarketScaler((centers[0], centers[1], centers[2], centers[3], centers[4]),
                        (scales[0], scales[1], scales[2], scales[3], scales[4]),
                        (methods[0], methods[1], methods[2], methods[3], methods[4]),
                        window, tuple(unique), evidence_ref)


@dataclass(frozen=True)
class MarketWindow:
    """Separate mask; five numeric channels. External scientific readiness always held."""

    values: tuple[Vector, ...] | None
    valid_mask: tuple[bool, ...]
    reason: str
    novel_constant_channels: tuple[int, ...]
    research_ready: bool = False
    scheduled_ends: tuple[pd.Timestamp, ...] = ()
    source_ids: tuple[tuple[str, ...], ...] = ()
    step_reasons: tuple[str, ...] = ()
    source_version: str = SOURCE_VERSION
    floor_ref: str | None = None
    scaler_ref: str | None = None


def standardized_window(
    steps: tuple[ScheduledStep, ...], rows: tuple[MarketVector, ...], scaler: MarketScaler,
    *, calendar: ScheduledCalendar, allow_synthetic: bool = False,
) -> MarketWindow:
    if (len(steps) != 48 or len(rows) != 48 or len(set(s.end for s in steps)) != 48
            or any(r.timestamp != s.end for s, r in zip(steps, rows))):
        raise ValueError("48_EXACT_SCHEDULED_MARKET_POSITIONS_REQUIRED")
    for step in steps:
        calendar.validate_step(step)
    endpoint = calendar.steps.index(steps[-1])
    if tuple(calendar.steps[max(0, endpoint - 47):endpoint + 1]) != steps:
        raise ValueError("MARKET_HISTORY_MUST_KEEP_CONSECUTIVE_SCHEDULED_POSITIONS")
    mask = tuple(r.values is not None and r.reason == "VECTOR_VALID" for r in rows)
    if scaler.basis == "SYNTHETIC" and not allow_synthetic:
        return MarketWindow(None, mask, "MARKET_SCALER_UNVERIFIED", ())
    if any(not scaler.window.contains(r.timestamp) and r.timestamp < scaler.window.fitted_at
           for r in rows):
        return MarketWindow(None, mask, "MARKET_SCALER_NOT_AVAILABLE_AT_CUTOFF", ())
    if not mask[-1] or sum(mask) < 46:
        return MarketWindow(None, mask, "MARKET_ENDPOINT_OR_46_OF_48_REQUIRED", ())
    output: list[Vector] = []
    novel: set[int] = set()
    for valid, row in zip(mask, rows):
        if valid and row.values is not None:
            transformed, flags = scaler.transform(row.values)
            output.append(transformed)
            novel.update(flags)
        else:
            output.append((0., 0., 0., 0., 0.))
    return MarketWindow(tuple(output), mask, "IMPLEMENTATION_VALID_SCIENTIFIC_HOLD",
                        tuple(sorted(novel)))


def window_from_history(
    history: MarketHistory, session: str, origin: int,
    floors: MarketFloors | None = None, scaler: MarketScaler | None = None,
    *, allow_synthetic: bool = False,
) -> MarketWindow:
    """Stable downstream handoff using the existing exact schedule and D7 transforms.

    This composes existing mathematics; it neither fits certificates nor installs
    availability assumptions. Each historical step uses its own causal cutoff.
    Even a valid synthetic 48×5 window keeps external scientific readiness false.
    """
    steps = scheduled_window(history.calendar, session, origin)
    measures = tuple(history.measures(s) for s in steps)

    def traced(output: MarketWindow) -> MarketWindow:
        return replace(output, scheduled_ends=tuple(s.end for s in steps),
                       source_ids=tuple(m.evidence_ids for m in measures),
                       step_reasons=tuple(m.reason for m in measures),
                       floor_ref=floors.evidence_ref if floors else None,
                       scaler_ref=scaler.evidence_ref if scaler else None)

    if floors is None:
        reason = measures[-1].reason
        if reason == "OBSERVATION_VALID":
            reason = "MARKET_FLOOR_CERTIFICATE_REQUIRED"
        return traced(MarketWindow(None, (False,) * 48, reason, ()))
    vectors = tuple(vector(m, floors, allow_synthetic=allow_synthetic) for m in measures)
    if scaler is None:
        return traced(MarketWindow(None, tuple(v.values is not None for v in vectors),
                                   "MARKET_SCALER_CERTIFICATE_REQUIRED", ()))
    return traced(standardized_window(steps, vectors, scaler, calendar=history.calendar,
                                     allow_synthetic=allow_synthetic))
