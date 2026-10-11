"""P2.1 candidate clocks only: no prices, labels, fills or scientific gate promotion.

All keys are UTC. Planned synthetic issuance is distinct from actual issuance;
source completion and availability are independently asserted, never inferred
from aggregation's legacy ``available_at`` field. Shared registration is pending.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

from .calendar import schedule, session_grid

Basis = Literal["UNKNOWN", "DOCUMENTED", "DERIVED", "SYNTHETIC", "ASSUMED"]
IssuanceKind = Literal["ACTUAL", "PLANNED_SYNTHETIC"]


def utc(value: pd.Timestamp | str) -> pd.Timestamp:
    """Require an explicit timezone and return a finite UTC timestamp."""
    stamp = pd.Timestamp(value)
    if pd.isna(stamp) or stamp.tzinfo is None:
        raise ValueError("Clock timestamps must be finite and timezone-aware")
    return stamp.tz_convert("UTC")


@dataclass(frozen=True)
class HourSlot:
    start: pd.Timestamp
    end: pd.Timestamp
    is_stub: bool = False


@dataclass(frozen=True)
class SessionClock:
    session: str
    open: pd.Timestamp | None
    close: pd.Timestamp | None
    hours: tuple[HourSlot, ...]
    terminal_stub: HourSlot | None
    reason: str


def session_clock(day: str) -> SessionClock:
    """Reuse XNYS session metadata and anchored grid, preserving terminal stubs."""
    stamp = pd.Timestamp(day)
    if stamp.tzinfo is not None or stamp != stamp.normalize():
        raise ValueError("Session key must be a timezone-free calendar date")
    key = stamp.date().isoformat()
    days = schedule(key, key)
    if days.empty:
        return SessionClock(key, None, None, (), None, "NO_SESSION")
    row = days.iloc[0]
    slots = tuple(
        HourSlot(utc(x["start"]), utc(x["end"]), x["stub"])
        for x in session_grid(row.open, row.close)
    )
    return SessionClock(
        key,
        utc(row.open),
        utc(row.close),
        tuple(x for x in slots if not x.is_stub),
        next((x for x in slots if x.is_stub), None),
        "SCHEDULE_VALID",
    )


@dataclass(frozen=True)
class ExecutionPlan:
    session: str
    origin: int
    cutoff: pd.Timestamp | None
    issuance: pd.Timestamp | None
    issuance_kind: IssuanceKind
    entry: pd.Timestamp | None
    exit: pd.Timestamp | None
    reason: str

    @property
    def calendar_valid(self) -> bool:
        return self.reason == "SCHEDULE_VALID"


def execution_plan(
    clock: SessionClock,
    origin: int,
    *,
    issued_at: pd.Timestamp | str | None = None,
) -> ExecutionPlan:
    """Plan ceil(issuance + 1min) entry and entry + 240min exit, never a fill.

    Missing issued_at requests visibly synthetic nominal cutoff+2min issuance.
    Actual issuance is accepted from cutoff through cutoff+5min inclusive.
    An opening at the session close is outside RTH. Shifted times are preserved;
    downstream fixed-strategy exception/admission rules remain unresolved.
    """
    if origin not in (1, 2):
        raise ValueError("Only candidate origins 1 and 2 are defined")
    kind: IssuanceKind = "ACTUAL" if issued_at is not None else "PLANNED_SYNTHETIC"
    if clock.open is None or clock.close is None:
        return ExecutionPlan(clock.session, origin, None, None, kind, None, None, "NO_SESSION")
    if len(clock.hours) < origin:
        return ExecutionPlan(clock.session, origin, None, None, kind, None, None, "NO_FULL_HOUR")
    cutoff = clock.hours[origin - 1].end
    issuance = utc(issued_at) if issued_at is not None else cutoff + pd.Timedelta(minutes=2)
    if issuance < cutoff:
        reason = "ISSUANCE_BEFORE_CUTOFF"
    elif issuance > cutoff + pd.Timedelta(minutes=5):
        reason = "ISSUANCE_TOO_LATE"
    else:
        entry = (issuance + pd.Timedelta(minutes=1)).ceil("min")
        exit_time = entry + pd.Timedelta(minutes=240)
        reason = "SCHEDULE_VALID"
        if not clock.open <= entry < clock.close:
            reason = "ENTRY_OUTSIDE_SESSION"
        elif not clock.open <= exit_time < clock.close:
            reason = "EXIT_OUTSIDE_SESSION"
        return ExecutionPlan(
            clock.session, origin, cutoff, issuance, kind, entry, exit_time, reason
        )
    return ExecutionPlan(clock.session, origin, cutoff, issuance, kind, None, None, reason)


def forecast_origins(clock: SessionClock) -> tuple[ExecutionPlan, ...]:
    """Two candidate plans on a session, with rejection reasons; none on holidays."""
    return tuple(execution_plan(clock, i) for i in (1, 2)) if clock.open is not None else ()


@dataclass(frozen=True)
class SourceObservation:
    observation_id: str
    symbol: str
    native_label: pd.Timestamp | str | None
    native_basis: Basis
    period_start: pd.Timestamp | str | None
    period_end: pd.Timestamp | str | None
    period_basis: Basis
    available_at: pd.Timestamp | str | None
    availability_basis: Basis
    evidence_ref: str | None = None


@dataclass(frozen=True)
class AvailabilityCheck:
    observation_id: str
    symbol: str
    cutoff: pd.Timestamp
    usable: bool
    source_asof_verified: bool
    scenario_only: bool
    reason: str


def observation_at_cutoff(
    observation: SourceObservation,
    cutoff: pd.Timestamp | str,
    *,
    expected_slot: HourSlot | None = None,
    test_scenario: bool = False,
) -> AvailabilityCheck:
    """Check each historical step's own cutoff, without consulting issuance.

    DOCUMENTED/DERIVED intervals need an evidence locator; publication must be
    DOCUMENTED. SYNTHETIC/ASSUMED records are opt-in isolated tests, always
    non-verified. DERIVED publication is never accepted. Supplying documented
    metadata is a caller assertion, not independent provider certification.
    expected_slot enforces stock complete-hour compatibility; no market joins.
    """
    cut = utc(cutoff)
    bases = (observation.native_basis, observation.period_basis, observation.availability_basis)
    if any(b not in {"UNKNOWN", "DOCUMENTED", "DERIVED", "SYNTHETIC", "ASSUMED"} for b in bases):
        raise ValueError("Unsupported clock basis")
    scenario = any(b in {"SYNTHETIC", "ASSUMED"} for b in bases)

    def result(reason: str) -> AvailabilityCheck:
        usable = reason == "AVAILABLE_AT_CUTOFF"
        return AvailabilityCheck(
            observation.observation_id,
            observation.symbol,
            cut,
            usable,
            usable and not scenario,
            scenario,
            reason,
        )

    if (
        any(
            value is None or pd.isna(value)
            for value in (
                observation.native_label,
                observation.period_start,
                observation.period_end,
                observation.available_at,
            )
        )
        or "UNKNOWN" in bases
    ):
        return result("SOURCE_CLOCK_UNKNOWN")
    if observation.availability_basis == "DERIVED":
        return result("SOURCE_CLOCK_UNKNOWN")
    if scenario and not test_scenario:
        return result("SCENARIO_NOT_AUTHORIZED")
    if not scenario and not (observation.evidence_ref and observation.evidence_ref.strip()):
        return result("SOURCE_CLOCK_UNKNOWN")
    utc(observation.native_label)
    start, end, available = (
        utc(observation.period_start),
        utc(observation.period_end),
        utc(observation.available_at),
    )
    if start >= end or available < end:
        return result("INVALID_SOURCE_INTERVAL")
    if end > cut:
        return result("SOURCE_PERIOD_INCOMPLETE")
    if available > cut:
        return result("SOURCE_BAR_UNAVAILABLE")
    if expected_slot is not None:
        if (
            expected_slot.is_stub
            or start != utc(expected_slot.start)
            or end != utc(expected_slot.end)
        ):
            return result("INCOMPATIBLE_FEATURE_SLOT")
        if end - start != pd.Timedelta(hours=1):
            return result("NO_FULL_HOUR")
    return result("AVAILABLE_AT_CUTOFF")


@dataclass(frozen=True)
class OriginBoundary:
    clock_and_information_issuable: bool
    source_asof_verified: bool
    entry_eligible: None = None
    label_valid: None = None
    execution_outcome: None = None


def origin_boundary(plan: ExecutionPlan, steps: tuple[AvailabilityCheck, ...]) -> OriginBoundary:
    """Clock/information subclaim only; full forecast admission waits for P2.2+.

    No future exit records, prices, model/risk state or label flags are inputs.
    Historical checks cannot extend past the original forecast information cutoff.
    Missing historical steps stay unusable; callers must preserve scheduled slots.
    """
    causal = (
        bool(steps)
        and plan.cutoff is not None
        and all(x.usable and x.cutoff <= plan.cutoff for x in steps)
    )
    usable = plan.calendar_valid and causal
    return OriginBoundary(usable, usable and all(x.source_asof_verified for x in steps))


def clock_trace(
    plan: ExecutionPlan,
    observation: SourceObservation,
    check: AvailabilityCheck,
) -> dict:
    """Small portable source→cutoff→planned-execution trace; never G2 clearance."""
    if (check.observation_id, check.symbol) != (observation.observation_id, observation.symbol):
        raise ValueError("Trace observation/check identity mismatch")

    def stamp(value):
        return utc(value).isoformat() if value is not None and not pd.isna(value) else None

    return {
        "session": plan.session,
        "origin": plan.origin,
        "symbol": observation.symbol,
        "observation_id": observation.observation_id,
        "native_label": stamp(observation.native_label),
        "native_basis": observation.native_basis,
        "period_start": stamp(observation.period_start),
        "period_end": stamp(observation.period_end),
        "period_basis": observation.period_basis,
        "available_at": stamp(observation.available_at),
        "availability_basis": observation.availability_basis,
        "evidence_ref": observation.evidence_ref,
        "historical_step_cutoff": stamp(check.cutoff),
        "forecast_cutoff": stamp(plan.cutoff),
        "issuance": stamp(plan.issuance),
        "issuance_kind": plan.issuance_kind,
        "proposed_entry": stamp(plan.entry),
        "proposed_exit": stamp(plan.exit),
        "calendar_valid": plan.calendar_valid,
        "schedule_reason": plan.reason,
        "information_reason": check.reason,
        "source_asof_verified": check.source_asof_verified,
        "scenario_only": check.scenario_only,
        "entry_eligible": None,
        "label_valid": None,
        "execution_outcome": None,
        "G2_status": "BLOCKED",
    }
