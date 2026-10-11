"""P2.3A scheduled source grid and causal M2 only; no scaler fit or dataset.

Availability remains caller evidence. Synthetic opt-in never certifies a source.
M2 uses stock returns, not TG0 or five-name ex-post eligibility. No floor is fit
here: an explicit training-derived certificate is required, otherwise blocked.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, replace
from statistics import fmean

import pandas as pd

from .calendar import schedule, session_grid
from .clocks import ExecutionPlan, HourSlot, SessionClock, execution_plan, utc
from .hourly_proxy import (
    EXECUTION_VERSION,
    HourlyCloseReference,
    _supported,
    resolve_reference,
)
from .labels import UNIVERSE, ActionScope, FitWindow, _split_factors, _valid_plan

M2_VERSION = "M2:HOURLY_CLOSE_PROXY:v1"


def _hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


@dataclass(frozen=True)
class ScheduledStep:
    session: str
    slot: int
    start: pd.Timestamp
    end: pd.Timestamp

    @property
    def information_cutoff(self) -> pd.Timestamp:
        return self.end


class ScheduledCalendar:
    """Small reusable calendar index; construct from existing exchange metadata."""

    def __init__(self, start: str, end: str):
        self._sessions: dict[str, SessionClock] = {}
        for day, row in schedule(start, end).iterrows():
            key = day.date().isoformat()
            slots = tuple(
                HourSlot(x["start"], x["end"], x["stub"]) for x in session_grid(row.open, row.close)
            )
            self._sessions[key] = SessionClock(
                key,
                utc(row.open),
                utc(row.close),
                tuple(x for x in slots if not x.is_stub),
                next((x for x in slots if x.is_stub), None),
                "SCHEDULE_VALID",
            )
        self.steps = tuple(
            ScheduledStep(c.session, i, h.start, h.end)
            for c in self._sessions.values()
            for i, h in enumerate(c.hours, 1)
        )
        self._positions = {(x.session, x.slot): i for i, x in enumerate(self.steps)}

    def clock(self, session: str) -> SessionClock:
        if session not in self._sessions:
            raise ValueError("SESSION_OUTSIDE_CALENDAR")
        return self._sessions[session]

    def validate_step(self, step: ScheduledStep) -> None:
        i = self._positions.get((step.session, step.slot))
        if i is None or self.steps[i] != step:
            raise ValueError("WRONG_HISTORICAL_STEP")
        utc(step.start)
        utc(step.end)

    def previous_origins(self, step: ScheduledStep, origin: int) -> tuple[str, ...]:
        self.validate_step(step)
        if origin not in (1, 2):
            raise ValueError("ORIGIN_REQUIRED")
        return tuple(
            d
            for d, c in self._sessions.items()
            if d < step.session and execution_plan(c, origin).calendar_valid
        )


def scheduled_window(
    calendar: ScheduledCalendar, session: str, origin: int
) -> tuple[ScheduledStep, ...]:
    """48 scheduled slots ending at the forecast cutoff; missing rows cannot shift it."""
    plan = execution_plan(calendar.clock(session), origin)
    if not plan.calendar_valid:
        raise ValueError("STRUCTURALLY_INELIGIBLE_ORIGIN")
    last = calendar._positions[(session, origin)]
    if last < 47:
        raise ValueError("SCHEDULED_HISTORY_INSUFFICIENT")
    return calendar.steps[last - 47 : last + 1]


@dataclass(frozen=True)
class WindowQuality:
    steps: tuple[ScheduledStep, ...]
    source_ids: tuple[tuple[str | None, ...], ...]
    mask: tuple[tuple[bool, ...], ...]
    reasons: tuple[tuple[str, ...], ...]
    raw_window_eligible: bool
    full_ft0_eligible: bool = False
    research_ready: bool = False


def window_quality(
    calendar: ScheduledCalendar,
    steps: tuple[ScheduledStep, ...],
    rows: tuple[HourlyCloseReference, ...],
    *,
    test_scenario: bool = False,
) -> WindowQuality:
    """Five-by-48 CLOSE/source quality only; no outcomes or 16-channel claim."""
    if len(steps) != 48:
        raise ValueError("48_SCHEDULED_STEPS_REQUIRED")
    for step in steps:
        calendar.validate_step(step)
    indices = [calendar._positions[(x.session, x.slot)] for x in steps]
    if indices != list(range(indices[0], indices[0] + 48)):
        raise ValueError("NONCONSECUTIVE_SCHEDULED_STEPS")
    index = {}
    observation_ids = set()
    for row in rows:
        if not isinstance(row, HourlyCloseReference):
            raise ValueError("HOURLY_SOURCE_REQUIRED")
        key = row.symbol, row.period_end
        if key in index or row.row_id in observation_ids:
            raise ValueError("DUPLICATE_SOURCE_KEY")
        observation_ids.add(row.row_id)
        index[key] = row
    masks, reasons, ids = [], [], []
    for symbol in UNIVERSE:
        sm, sr, si = [], [], []
        for step in steps:
            row = index.get((symbol, step.end))
            if row is None:
                reason = "SOURCE_MISSING"
            elif row.period_start != step.start:
                reason = "WRONG_SCHEDULED_SLOT"
            elif not _supported(row, test_scenario):
                reason = "SOURCE_CLOCK_BLOCKED"
            elif row.available_at > step.information_cutoff:
                reason = "NOT_AVAILABLE_AT_STEP"
            else:
                reason = "SOURCE_VALID"
            sm.append(reason == "SOURCE_VALID")
            sr.append(reason)
            si.append(row.row_id if row else None)
        masks.append(tuple(sm))
        reasons.append(tuple(sr))
        ids.append(tuple(si))
    return WindowQuality(
        steps, tuple(ids), tuple(masks), tuple(reasons), all(all(x) for x in masks)
    )


@dataclass(frozen=True)
class HistoricalReturn:
    plan: ExecutionPlan
    symbol: str
    value: float | None
    maturity: pd.Timestamp | None
    reason: str
    source_ids: tuple[str, ...]
    action_ids: tuple[str, ...]
    source_binding: str
    synthetic: bool
    execution_version: str = EXECUTION_VERSION
    m2_version: str = M2_VERSION

    def __post_init__(self):
        if self.symbol not in UNIVERSE or self.plan.origin not in (1, 2):
            raise ValueError("RETURN_KEY_REQUIRED")
        if self.reason == "RETURN_VALID" and not _valid_plan(self.plan):
            raise ValueError("INVALID_RETURN_PLAN")
        if self.value is not None and (
            isinstance(self.value, bool) or not math.isfinite(self.value)
        ):
            raise ValueError("INVALID_RETURN")
        if self.maturity is not None:
            object.__setattr__(self, "maturity", utc(self.maturity))
            if self.plan.exit is None or self.maturity < utc(self.plan.exit):
                raise ValueError("MATURITY_BEFORE_SCHEDULED_EXIT")
        if self.reason == "RETURN_VALID" and (
            self.value is None or self.maturity is None or len(self.source_ids) != 2
        ):
            raise ValueError("VALID_RETURN_PROVENANCE_REQUIRED")
        if len(self.source_binding) != 64 or any(
            c not in "0123456789abcdef" for c in self.source_binding
        ):
            raise ValueError("RETURN_LINEAGE_REQUIRED")

    @property
    def lineage_id(self) -> str:
        return _hash(vars(self))

    @property
    def key(self) -> tuple[str, str, int]:
        return self.symbol, self.plan.session, self.plan.origin


def historical_return(
    plan: ExecutionPlan,
    symbol: str,
    rows: tuple[HourlyCloseReference, ...],
    actions: ActionScope | None,
    *,
    test_scenario: bool = False,
) -> HistoricalReturn:
    """Resolve one stock without importing five-name label validity or TG0 fields."""
    refs = tuple(
        resolve_reference(rows, plan, symbol, event, test_scenario=test_scenario)
        for event in ("ENTRY", "EXIT")
    )
    value = maturity = None
    factors = None
    if (
        all(r.reason != "INVALID_PLAN" for r in refs)
        and plan.calendar_valid
        and actions is not None
        and utc(actions.start) <= plan.cutoff
        and utc(actions.end) >= plan.exit
    ):
        factors = _split_factors(
            replace(plan, entry=plan.cutoff, exit=plan.cutoff + pd.Timedelta(hours=4)),
            actions,
            test_scenario,
        )
    if any(r.reason == "INVALID_PLAN" for r in refs):
        reason = "INVALID_PLAN"
    elif any(r.row is None for r in refs):
        reason = "REFERENCE_MISSING"
    elif any(r.reason == "WRONG_SCHEDULED_SLOT" for r in refs):
        reason = "WRONG_SCHEDULED_SLOT"
    elif factors is None:
        reason = "ACTION_CONVENTION_UNVERIFIED"
    elif not all(_supported(r.row, test_scenario) for r in refs):
        reason = "SOURCE_CLOCK_BLOCKED"
    elif refs[0].row.available_at > plan.cutoff:
        reason = "ENTRY_NOT_AVAILABLE_AT_ORIGINAL_CUTOFF"
    else:
        value = (
            math.log(refs[1].price)
            + math.log(factors[UNIVERSE.index(symbol)])
            - math.log(refs[0].price)
        )
        maturity = max(plan.exit, *(r.row.available_at for r in refs))
        reason = "RETURN_VALID"
    sources = tuple(r.row.row_id for r in refs if r.row)
    action_ids = tuple(s.event_id for s in actions.splits) if actions else ()
    synthetic = any(
        r.row
        and (r.row.source == "SYNTHETIC" or r.row.availability_basis in {"SYNTHETIC", "ASSUMED"})
        for r in refs
    ) or bool(actions and actions.basis in {"SYNTHETIC", "ASSUMED"})
    binding = {
        "plan": vars(plan),
        "symbol": symbol,
        "refs": [vars(r.row) if r.row else None for r in refs],
        "actions": str(actions),
        "execution": EXECUTION_VERSION,
        "m2": M2_VERSION,
        "value": value,
        "maturity": maturity,
        "reason": reason,
    }
    return HistoricalReturn(
        plan, symbol, value, maturity, reason, sources, action_ids, _hash(binding), synthetic
    )


class ReturnIndex:
    """Unique stock/session/origin lookups, independent of row order or future panels."""

    def __init__(self, records: tuple[HistoricalReturn, ...]):
        self._records: dict[tuple[str, str, int], HistoricalReturn] = {}
        for record in records:
            if not isinstance(record, HistoricalReturn) or (
                record.execution_version,
                record.m2_version,
            ) != (EXECUTION_VERSION, M2_VERSION):
                raise ValueError("PROXY_RETURN_VERSION_REQUIRED")
            if record.key in self._records:
                raise ValueError("DUPLICATE_RETURN_KEY")
            self._records[record.key] = record

    def get(self, symbol: str, session: str, origin: int) -> HistoricalReturn | None:
        return self._records.get((symbol, session, origin))


@dataclass(frozen=True)
class M2FloorCertificate:
    """Caller assertion of an already derived training positive-volatility p05.

    No fitting here. Source population and numerical percentile need separate
    review; DOCUMENTED is assertion, SYNTHETIC requires explicit opt-in.
    """

    epsilon: float
    window: FitWindow
    fitting_keys: tuple[tuple[str, str, int], ...]
    evidence_ref: str
    basis: str
    method: str = "TRAINING_POSITIVE_VOLATILITY_P05"
    m2_version: str = M2_VERSION

    def __post_init__(self):
        if isinstance(self.epsilon, bool) or not math.isfinite(self.epsilon) or self.epsilon <= 0:
            raise ValueError("POSITIVE_FLOOR_REQUIRED")
        start, stop, fitted = (
            utc(self.window.start),
            utc(self.window.stop),
            utc(self.window.fitted_at),
        )
        if (
            self.window.phase not in {"INNER_TRAIN", "REFIT"}
            or start < pd.Timestamp("2020-07-01", tz="America/New_York").tz_convert("UTC")
            or stop > pd.Timestamp("2024-07-01", tz="America/New_York").tz_convert("UTC")
        ):
            raise ValueError("PERMITTED_TRAINING_PREFIX_REQUIRED")
        if start >= stop or fitted < stop:
            raise ValueError("INVALID_FLOOR_FIT_CLOCK")
        object.__setattr__(
            self, "window", replace(self.window, start=start, stop=stop, fitted_at=fitted)
        )
        if not self.fitting_keys or len(set(self.fitting_keys)) != len(self.fitting_keys):
            raise ValueError("UNIQUE_FLOOR_FIT_KEYS_REQUIRED")
        for key in self.fitting_keys:
            _validate_key(key)
            day = pd.Timestamp(key[1], tz="America/New_York").tz_convert("UTC")
            if not start <= day < stop:
                raise ValueError("FLOOR_KEY_OUTSIDE_TRAINING_PREFIX")
        if (
            self.method != "TRAINING_POSITIVE_VOLATILITY_P05"
            or self.m2_version != M2_VERSION
            or self.basis not in {"SYNTHETIC", "DOCUMENTED"}
            or not self.evidence_ref.strip()
        ):
            raise ValueError("FLOOR_PROVENANCE_REQUIRED")

    @property
    def floor_id(self) -> str:
        return _hash(vars(self))


@dataclass(frozen=True)
class M2Result:
    key: tuple[str, str, int]
    step: ScheduledStep
    value: float | None
    reason: str
    sessions: tuple[str, ...]
    valid20: int
    valid60: int
    max_missing_run: int
    reference_ids: tuple[str | None, ...]
    missing_reasons: tuple[str, ...]
    mean20: float | None = None
    rms60: float | None = None
    floor_id: str | None = None
    m2_version: str = M2_VERSION
    research_ready: bool = False


def evaluate_m2(
    calendar: ScheduledCalendar,
    index: ReturnIndex,
    symbol: str,
    step: ScheduledStep,
    origin: int,
    floor: M2FloorCertificate | None = None,
    *,
    test_scenario: bool = False,
) -> M2Result:
    """Last scheduled 20/60 earlier eligible sessions; valid means mature at step."""
    _validate_key((symbol, step.session, origin))
    if floor is not None and not isinstance(floor, M2FloorCertificate):
        raise ValueError("M2_FLOOR_CERTIFICATE_REQUIRED")
    sessions = calendar.previous_origins(step, origin)[-60:]
    values, ids, missing = [], [], []
    longest = run = 0
    for day in sessions:
        record = index.get(symbol, day, origin)
        if record is None:
            reason = "RETURN_MISSING"
        elif record.reason != "RETURN_VALID":
            reason = record.reason
        elif record.synthetic and not test_scenario:
            reason = "SOURCE_CLOCK_BLOCKED"
        elif record.plan.cutoff is None or record.plan.cutoff >= step.end:
            reason = "FUTURE_ORIGIN"
        elif record.maturity is None or record.maturity > step.information_cutoff:
            reason = "NOT_MATURED_AT_STEP"
        else:
            reason = "RETURN_VALID"
        values.append(record.value if reason == "RETURN_VALID" else None)
        ids.append(record.lineage_id if reason == "RETURN_VALID" else None)
        missing.append(reason)
        run = run + 1 if values[-1] is None else 0
        longest = max(longest, run)
    n20 = sum(x is not None for x in values[-20:])
    n60 = sum(x is not None for x in values)
    mean = rms = value = None
    floor_id = None
    if len(sessions) < 60:
        reason = "SCHEDULED_HISTORY_INSUFFICIENT"
    elif n20 < 19 or n60 < 57 or longest > 2:
        reason = "RETURN_COVERAGE_BLOCKED"
    elif floor is None:
        reason = "FLOOR_UNVERIFIED"
    elif floor.window.fitted_at > step.end or (floor.basis == "SYNTHETIC" and not test_scenario):
        reason = "FLOOR_NOT_AVAILABLE_AT_STEP"
    else:
        numerator = [x for x in values[-20:] if x is not None]
        denominator = [x for x in values if x is not None]
        scale = max(abs(x) for x in denominator)
        mean = fmean(x / scale for x in numerator) * scale if scale else 0.0
        rms = math.sqrt(fmean((x / scale) ** 2 for x in denominator)) * scale if scale else 0.0
        floor_id = floor.floor_id
        if not math.isfinite(rms) or not math.isfinite(mean):
            reason = "INVALID_DENOMINATOR"
        else:
            value = mean / max(rms, floor.epsilon)
            reason = "M2_VALID" if math.isfinite(value) else "INVALID_DENOMINATOR"
            if reason != "M2_VALID":
                value = None
    return M2Result(
        (symbol, step.session, origin),
        step,
        value,
        reason,
        sessions,
        n20,
        n60,
        longest,
        tuple(ids),
        tuple(missing),
        mean,
        rms,
        floor_id,
    )


def _validate_key(key: tuple[str, str, int]) -> None:
    if len(key) != 3 or key[0] not in UNIVERSE or type(key[2]) is not int or key[2] not in (1, 2):
        raise ValueError("M2_CANONICAL_KEY_REQUIRED")
    stamp = pd.Timestamp(key[1])
    if (
        pd.isna(stamp)
        or stamp.tzinfo is not None
        or stamp != stamp.normalize()
        or stamp.date().isoformat() != key[1]
    ):
        raise ValueError("CANONICAL_SESSION_DATE_REQUIRED")


def canonical_m2_keys(
    results: tuple[M2Result, ...],
) -> tuple[tuple[tuple[str, str, int], float], ...]:
    """Deduplicate repeated window appearances; 50/50 origin weights, no scaler fit.

    Session/origin values must agree across appearances. A late-publication
    conflict is blocked rather than silently inventing a session freeze clock.
    """
    unique = {}
    for result in results:
        _validate_key(result.key)
        if (
            result.reason != "M2_VALID"
            or result.value is None
            or not math.isfinite(result.value)
            or result.m2_version != M2_VERSION
        ):
            raise ValueError("VALID_PROXY_M2_REQUIRED")
        signature = (
            result.value,
            result.mean20,
            result.rms60,
            result.floor_id,
            result.sessions,
            result.reference_ids,
            result.valid20,
            result.valid60,
        )
        if result.key in unique and unique[result.key] != signature:
            raise ValueError("CONFLICTING_SESSION_LOCKED_M2")
        unique[result.key] = signature
    counts = {o: sum(k[2] == o for k in unique) for o in (1, 2)}
    if not all(counts.values()):
        raise ValueError("BOTH_ORIGIN_TYPES_REQUIRED")
    return tuple((key, 0.5 / counts[key[2]]) for key in sorted(unique))
