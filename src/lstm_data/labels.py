"""P2.2A exact minute references and conditional TG0 math; no research executor.

Publication and action metadata are caller assertions requiring evidence review.
Synthetic records require explicit opt-in. No portfolio admission/fills, feature
calculation, market joins or scientific gate clearance is implemented here.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from statistics import median
from typing import Literal

import pandas as pd

from .calendar import schedule
from .clocks import Basis, ExecutionPlan, execution_plan, session_clock, utc

UNIVERSE = ("AAPL", "JPM", "JNJ", "WMT", "CAT")


@dataclass(frozen=True)
class MinuteReference:
    symbol: str
    row_id: str
    minute_start: pd.Timestamp | str
    raw_open: float
    source_version: str
    source: Literal["ALPACA_SIP", "SYNTHETIC"]
    available_at: pd.Timestamp | str | None = None
    availability_basis: Basis = "UNKNOWN"
    evidence_ref: str | None = None
    duration_minutes: int = 1
    price_field: str = "open"
    adjustment: str = "raw"

    def __post_init__(self) -> None:
        start = utc(self.minute_start)
        if start != start.floor("min") or self.duration_minutes != 1:
            raise ValueError("INVALID_MINUTE_INTERVAL")
        if self.symbol not in UNIVERSE:
            raise ValueError("UNSUPPORTED_SYMBOL")
        if self.price_field != "open" or self.adjustment != "raw":
            raise ValueError("UNSUPPORTED_SOURCE_FIELDS")
        if self.source not in {"ALPACA_SIP", "SYNTHETIC"}:
            raise ValueError("UNSUPPORTED_SOURCE")
        if not self.row_id.strip() or not self.source_version.strip():
            raise ValueError("SOURCE_ID_REQUIRED")
        if (
            isinstance(self.raw_open, bool)
            or not math.isfinite(self.raw_open)
            or self.raw_open <= 0
        ):
            raise ValueError("INVALID_RAW_OPEN")
        if self.availability_basis not in {"UNKNOWN", "DOCUMENTED", "SYNTHETIC", "ASSUMED"}:
            raise ValueError("UNSUPPORTED_AVAILABILITY_BASIS")
        object.__setattr__(self, "minute_start", start)
        if self.available_at is not None and not pd.isna(self.available_at):
            available = utc(self.available_at)
            if available < start:
                raise ValueError("AVAILABILITY_BEFORE_MINUTE")
            object.__setattr__(self, "available_at", available)
        else:
            object.__setattr__(self, "available_at", None)


def minute_reference(
    rows: tuple[MinuteReference, ...],
    symbol: str,
    minute: pd.Timestamp | str,
) -> MinuteReference | None:
    """Exact key only: duplicates fail; no next-minute/other-symbol substitution."""
    if symbol not in UNIVERSE:
        raise ValueError("UNSUPPORTED_SYMBOL")
    key = utc(minute)
    found = [row for row in rows if row.symbol == symbol and row.minute_start == key]
    if len(found) > 1:
        raise ValueError("DUPLICATE_MINUTE_REFERENCE")
    return found[0] if found else None


def _supported(row: MinuteReference, test_scenario: bool) -> bool:
    if row.available_at is None:
        return False
    if row.source == "SYNTHETIC" or row.availability_basis == "SYNTHETIC":
        return test_scenario and row.availability_basis == "SYNTHETIC"
    # ASSUMED is retained as metadata, never activated as a real source clock.
    return row.availability_basis == "DOCUMENTED" and bool(
        row.evidence_ref and row.evidence_ref.strip()
    )


def _valid_plan(plan: ExecutionPlan) -> bool:
    """Recheck supplied clock objects against P2.1, including immutable cutoff."""
    if not plan.calendar_valid or plan.issuance is None:
        return False
    if plan.issuance_kind not in {"ACTUAL", "PLANNED_SYNTHETIC"}:
        return False
    expected = execution_plan(
        session_clock(plan.session),
        plan.origin,
        issued_at=plan.issuance if plan.issuance_kind == "ACTUAL" else None,
    )
    return expected.calendar_valid and all(
        getattr(plan, field) == getattr(expected, field)
        for field in ("cutoff", "issuance", "entry", "exit")
    )


@dataclass(frozen=True)
class ForecastEvidence:
    issuable: bool
    cutoff: pd.Timestamp | str
    input_symbols: tuple[str, ...]
    basis: Basis
    evidence_ref: str


@dataclass(frozen=True)
class CausalEligibility:
    forecast_issuable: bool
    entry_eligible: tuple[bool, ...]
    entry_reasons: tuple[str, ...]
    forecast_evidence_ref: str
    entry_source_ids: tuple[str | None, ...]
    scope: str = "SOURCE_CLOCK_REFERENCE_ONLY; P3_ADMISSION_NOT_EVALUATED"


def causal_eligibility(
    plan: ExecutionPlan,
    forecast: ForecastEvidence,
    entries: tuple[MinuteReference, ...],
    *,
    test_scenario: bool = False,
) -> CausalEligibility:
    """Only origin/entry-time facts; future prices, availability and actions excluded.

    Full approved FT0/population verification is an upstream assertion, not
    calculated here. Minute-open availability may be unknown even when a later
    historical minute bar exists. Eligibility here is not brokerage fill proof.
    """
    valid = _valid_plan(plan)
    basis_supported = forecast.basis == "DOCUMENTED" or (
        forecast.basis == "SYNTHETIC" and test_scenario
    )
    issuable = bool(
        valid
        and forecast.issuable
        and forecast.input_symbols == UNIVERSE
        and basis_supported
        and forecast.evidence_ref.strip()
        and utc(forecast.cutoff) == plan.cutoff
    )
    reasons, ids = [], []
    for symbol in UNIVERSE:
        row = minute_reference(entries, symbol, plan.entry) if valid else None
        ids.append(row.row_id if row else None)
        if not issuable:
            reason = "FORECAST_NOT_ISSUABLE"
        elif row is None:
            reason = "ENTRY_REFERENCE_MISSING"
        elif not _supported(row, test_scenario):
            reason = "ENTRY_AVAILABILITY_UNVERIFIED"
        elif row.available_at > plan.entry:
            reason = "ENTRY_REFERENCE_NOT_YET_AVAILABLE"
        else:
            reason = "ENTRY_REFERENCE_ELIGIBLE"
        reasons.append(reason)
    return CausalEligibility(
        issuable,
        tuple(x == "ENTRY_REFERENCE_ELIGIBLE" for x in reasons),
        tuple(reasons),
        forecast.evidence_ref,
        tuple(ids),
    )


@dataclass(frozen=True)
class SplitFact:
    symbol: str
    effective_at: pd.Timestamp | str
    new_shares: int
    old_shares: int
    event_id: str
    basis: Basis


@dataclass(frozen=True)
class ActionScope:
    """Explicit complete split/no-action scope for this interval, not a cashbook."""

    start: pd.Timestamp | str
    end: pd.Timestamp | str
    symbols: tuple[str, ...]
    basis: Basis
    evidence_ref: str
    splits: tuple[SplitFact, ...] = ()
    unsupported_action: bool = False


def _split_factors(
    plan: ExecutionPlan, actions: ActionScope | None, test_scenario: bool
) -> tuple[float, ...] | None:
    if actions is None or actions.unsupported_action or actions.symbols != UNIVERSE:
        return None
    accepted = {"DOCUMENTED"} | ({"SYNTHETIC"} if test_scenario else set())
    if actions.basis not in accepted or not actions.evidence_ref.strip():
        return None
    if utc(actions.start) > plan.entry or utc(actions.end) < plan.exit:
        return None
    factors = dict.fromkeys(UNIVERSE, 1.0)
    ids = set()
    for split in actions.splits:
        if (
            split.symbol not in UNIVERSE
            or split.basis not in accepted
            or not split.event_id
            or split.event_id in ids
            or type(split.new_shares) is not int
            or type(split.old_shares) is not int
            or split.new_shares <= 0
            or split.old_shares <= 0
        ):
            return None
        ids.add(split.event_id)
        if plan.entry < utc(split.effective_at) <= plan.exit:
            factors[split.symbol] *= split.new_shares / split.old_shares
    return tuple(factors[symbol] for symbol in UNIVERSE)


@dataclass(frozen=True)
class LabelSample:
    plan: ExecutionPlan
    causal: CausalEligibility
    raw_returns: tuple[float, ...] | None
    centered_returns: tuple[float, ...] | None
    cross_median: float | None
    unscaled_mad: float | None
    maturity: pd.Timestamp | None
    maturity_basis: str
    observed_at: pd.Timestamp
    label_valid: bool
    reason: str
    source_ids: tuple[str, ...]
    source_versions: tuple[str, ...]
    action_evidence_ref: str | None
    split_ids: tuple[str, ...]
    scenario_only: bool
    execution_outcome: str = "NOT_EVALUATED"
    market_status: str = "HOLD"
    research_ready: bool = False

    @property
    def key(self) -> str:
        cutoff = self.plan.cutoff.isoformat() if self.plan.cutoff is not None else "NO_CUTOFF"
        return f"{self.plan.session}:{self.plan.origin}:{cutoff}"


def label_sample(
    plan: ExecutionPlan,
    forecast: ForecastEvidence,
    entries: tuple[MinuteReference, ...],
    exits: tuple[MinuteReference, ...],
    *,
    observed_at: pd.Timestamp | str,
    actions: ActionScope | None = None,
    test_scenario: bool = False,
) -> LabelSample:
    """Later five-name outcome/maturity, independent of the causal entry interface.

    Unknown maturity can retain diagnostic mathematical returns, but cannot
    enter supervised use or floor fitting. Split factors convert raw exit value
    to entry-share units only under explicit interval/event facts. No dividends.
    """
    causal = causal_eligibility(plan, forecast, entries, test_scenario=test_scenario)
    observed = utc(observed_at)
    selected = []
    reason = "LABEL_VALID"
    if not _valid_plan(plan):
        reason = plan.reason if not plan.calendar_valid else "INVALID_PLAN"
    else:
        for symbol in UNIVERSE:
            entry = minute_reference(entries, symbol, plan.entry)
            exit_row = minute_reference(exits, symbol, plan.exit)
            if entry is None or exit_row is None:
                reason = "ENTRY_REFERENCE_MISSING" if entry is None else "EXIT_REFERENCE_MISSING"
                break
            selected.extend((entry, exit_row))
    factors = _split_factors(plan, actions, test_scenario) if reason == "LABEL_VALID" else None
    if reason == "LABEL_VALID" and factors is None:
        reason = "ACTION_CONVENTION_UNVERIFIED"
    scenario = (
        test_scenario
        or any(
            row.source == "SYNTHETIC" or row.availability_basis in {"SYNTHETIC", "ASSUMED"}
            for row in selected
        )
        or forecast.basis in {"SYNTHETIC", "ASSUMED"}
        or bool(actions and actions.basis in {"SYNTHETIC", "ASSUMED"})
    )
    returns = centered = None
    m = mad = maturity = None
    maturity_basis = "MATURITY_UNVERIFIED"
    if reason == "LABEL_VALID":
        # Log differences avoid overflow/underflow of a direct price ratio.
        returns = tuple(
            math.log(selected[2 * i + 1].raw_open)
            + math.log(factors[i])
            - math.log(selected[2 * i].raw_open)
            for i in range(5)
        )
        m = median(returns)
        centered = tuple(r - m for r in returns)
        mad = median(abs(r) for r in centered)
        if all(_supported(row, test_scenario) for row in selected):
            maturity = max(plan.exit, *(row.available_at for row in selected))
            maturity_basis = "SYNTHETIC" if scenario else "DOCUMENTED_ASSERTION"
            if observed < maturity:
                reason = "LABEL_NOT_MATURED"
            elif not causal.forecast_issuable or not all(causal.entry_eligible):
                reason = "CAUSAL_ELIGIBILITY_BLOCKED"
        else:
            reason = "MATURITY_UNVERIFIED"
    return LabelSample(
        plan,
        causal,
        returns,
        centered,
        m,
        mad,
        maturity,
        maturity_basis,
        observed,
        reason == "LABEL_VALID",
        reason,
        tuple(row.row_id for row in selected),
        tuple(row.source_version for row in selected),
        actions.evidence_ref if actions else None,
        tuple(s.event_id for s in actions.splits) if actions else (),
        scenario,
    )


@dataclass(frozen=True)
class FitWindow:
    window_id: str
    start: pd.Timestamp
    stop: pd.Timestamp  # Exclusive split boundary in ET calendar dates, stored UTC.
    fitted_at: pd.Timestamp
    phase: Literal["INNER_TRAIN", "INNER_VALIDATION", "REFIT"]


def fitting_window(
    stage: Literal["WF1", "WF2", "PRECONFIRMATION"],
    phase: Literal["INNER_TRAIN", "INNER_VALIDATION", "REFIT"],
    *,
    fitted_at: pd.Timestamp | str,
) -> FitWindow:
    """Frozen boundaries and last63 calendar sessions, never best available dates.

    Exclusive next-period ET midnight defines the date split; fitted_at adds an
    independent actual observability bound. No input-lookback embargo. Inner
    population adequacy (50 sessions/25 each origin) is later production work.
    """
    ends = {"WF1": "2023-06-30", "WF2": "2023-12-31", "PRECONFIRMATION": "2024-06-30"}
    if stage not in ends or phase not in {"INNER_TRAIN", "INNER_VALIDATION", "REFIT"}:
        raise ValueError("UNSUPPORTED_FROZEN_FIT_WINDOW")
    first = pd.Timestamp("2020-07-01", tz="America/New_York").tz_convert("UTC")
    last = ends[stage]
    stop = (pd.Timestamp(last, tz="America/New_York") + pd.Timedelta(days=1)).tz_convert("UTC")
    sessions = schedule("2020-07-01", last)
    tail_start = pd.Timestamp(sessions.index[-63].date(), tz="America/New_York").tz_convert("UTC")
    start = tail_start if phase == "INNER_VALIDATION" else first
    if phase == "INNER_TRAIN":
        stop = tail_start
    return FitWindow(f"{stage}:{phase}", start, stop, utc(fitted_at), phase)


def fitting_membership(
    sample: LabelSample, window: FitWindow, *, test_scenario: bool = False
) -> str:
    """One origin's exclusion reason; no future labels enter training transforms."""
    if not sample.label_valid:
        return sample.reason
    if sample.scenario_only and not test_scenario:
        return "SYNTHETIC_NOT_RESEARCH_DATA"
    if not window.start <= sample.plan.cutoff < window.stop:
        return "ORIGIN_OUTSIDE_FIT_WINDOW"
    if sample.plan.exit >= window.stop or sample.maturity >= window.stop:
        return "PURGED_SPLIT_BOUNDARY"
    if sample.maturity > window.fitted_at:
        return "NOT_MATURED_BY_FIT"
    return "FIT_ELIGIBLE"


@dataclass(frozen=True)
class FittedFloor:
    floor_id: str
    epsilon: float
    window: FitWindow
    fitting_keys: tuple[str, ...]
    exclusions: tuple[tuple[str, str], ...]
    scenario_only: bool


def fit_tg0_floor(
    samples: tuple[LabelSample, ...], window: FitWindow, *, test_scenario: bool = False
) -> FittedFloor:
    """Fit max(1e-4,0.1*median(training MAD)); no empty/default/test leakage."""
    if window.phase not in {"INNER_TRAIN", "REFIT"}:
        raise ValueError("FLOOR_REQUIRES_TRAINING_POPULATION")
    keys = [sample.key for sample in samples]
    if len(set(keys)) != len(keys):
        raise ValueError("DUPLICATE_FITTING_ORIGIN")
    accepted, excluded = [], []
    for sample in samples:
        reason = fitting_membership(sample, window, test_scenario=test_scenario)
        if reason == "FIT_ELIGIBLE":
            accepted.append(sample)
        else:
            excluded.append((sample.key, reason))
    if not accepted:
        raise ValueError("NO_VALID_FLOOR_FITTING_POPULATION")
    if len({sample.scenario_only for sample in accepted}) > 1:
        raise ValueError("MIXED_SYNTHETIC_AND_OBSERVED_POPULATION")
    epsilon = max(1e-4, 0.1 * median(sample.unscaled_mad for sample in accepted))
    bindings = {
        "window": window.window_id,
        "start": window.start.isoformat(),
        "stop": window.stop.isoformat(),
        "fitted_at": window.fitted_at.isoformat(),
        "samples": sorted(
            (
                s.key,
                s.unscaled_mad,
                s.maturity.isoformat(),
                s.source_ids,
                s.source_versions,
                s.action_evidence_ref,
                s.split_ids,
            )
            for s in accepted
        ),
    }
    floor_id = hashlib.sha256(json.dumps(bindings, sort_keys=True).encode()).hexdigest()
    return FittedFloor(
        floor_id,
        epsilon,
        window,
        tuple(s.key for s in accepted),
        tuple(excluded),
        any(s.scenario_only for s in accepted),
    )


@dataclass(frozen=True)
class TG0Target:
    sample: LabelSample
    floor_id: str
    epsilon: float
    scores: tuple[float, ...]
    research_ready: bool = False


def apply_tg0_floor(
    sample: LabelSample, floor: FittedFloor, *, test_scenario: bool = False
) -> TG0Target:
    """Frozen floor application; no clipping, partial population or refitting."""
    if not sample.label_valid:
        raise ValueError(sample.reason)
    if (sample.scenario_only or floor.scenario_only) and not test_scenario:
        raise ValueError("SYNTHETIC_NOT_RESEARCH_DATA")
    if sample.scenario_only != floor.scenario_only:
        raise ValueError("MIXED_SYNTHETIC_AND_OBSERVED_POPULATION")
    if not floor.floor_id or not math.isfinite(floor.epsilon) or floor.epsilon < 1e-4:
        raise ValueError("INVALID_FITTED_FLOOR")
    return TG0Target(
        sample,
        floor.floor_id,
        floor.epsilon,
        tuple(r / (sample.unscaled_mad + floor.epsilon) for r in sample.centered_returns),
    )
