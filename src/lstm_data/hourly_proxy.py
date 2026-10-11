"""P2.2A-R1 completed-hour CLOSE proxy; synthetic foundation, no fills/executor.

Raw source price, its availability, scheduled event and maturity remain distinct.
Original minute API is untouched. All public fitting/application entry points
here reject minute artifacts and carry independent execution/target/M2 versions.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, replace
from statistics import median
from typing import Literal, cast

import pandas as pd

from .clocks import Basis, ExecutionPlan, session_clock, utc
from .labels import (
    UNIVERSE,
    ActionScope,
    CausalEligibility,
    FittedFloor,
    FitWindow,
    ForecastEvidence,
    LabelSample,
    TG0Target,
    _split_factors,
    _valid_plan,
    apply_tg0_floor,
    fit_tg0_floor,
    fitting_membership,
)

EXECUTION_VERSION = "COMPLETED_HOURLY_CLOSE_PROXY:v1"
TARGET_VERSION = "TG0:HOURLY_CLOSE_PROXY:v1"
M2_VERSION = "M2:HOURLY_CLOSE_PROXY:v1:REBUILD_REQUIRED"


@dataclass(frozen=True)
class HourlyCloseReference:
    symbol: str
    row_id: str
    period_start: pd.Timestamp | str
    period_end: pd.Timestamp | str
    raw_close: float
    source_version: str
    source: Literal["ALPACA_SIP", "SYNTHETIC"]
    available_at: pd.Timestamp | str | None = None
    availability_basis: Basis = "UNKNOWN"
    evidence_ref: str | None = None
    price_field: str = "close"
    adjustment: str = "raw"

    def __post_init__(self):
        start, end = utc(self.period_start), utc(self.period_end)
        if end - start != pd.Timedelta(hours=1):
            raise ValueError("FULL_HOUR_REQUIRED")
        if self.symbol not in UNIVERSE or self.source not in {"ALPACA_SIP", "SYNTHETIC"}:
            raise ValueError("STOCK_SOURCE_REQUIRED")
        if self.price_field != "close" or self.adjustment != "raw":
            raise ValueError("RAW_STOCK_CLOSE_REQUIRED")
        if not self.row_id.strip() or not self.source_version.strip():
            raise ValueError("SOURCE_ID_REQUIRED")
        if (
            isinstance(self.raw_close, bool)
            or not math.isfinite(self.raw_close)
            or self.raw_close <= 0
        ):
            raise ValueError("INVALID_RAW_CLOSE")
        if self.availability_basis not in {"UNKNOWN", "ASSUMED", "SYNTHETIC", "DOCUMENTED"}:
            raise ValueError("UNSUPPORTED_AVAILABILITY_BASIS")
        object.__setattr__(self, "period_start", start)
        object.__setattr__(self, "period_end", end)
        if self.available_at is not None and not pd.isna(self.available_at):
            available = utc(self.available_at)
            if available < end:
                raise ValueError("AVAILABILITY_BEFORE_COMPLETION")
            object.__setattr__(self, "available_at", available)
        else:
            object.__setattr__(self, "available_at", None)


def _supported(row: HourlyCloseReference, scenario: bool) -> bool:
    if row.available_at is None:
        return False
    if row.source == "SYNTHETIC" or row.availability_basis == "SYNTHETIC":
        return scenario and row.availability_basis == "SYNTHETIC"
    return row.availability_basis == "DOCUMENTED" and bool(
        row.evidence_ref and row.evidence_ref.strip()
    )


@dataclass(frozen=True)
class ExecutionReference:
    symbol: str
    side: Literal["LONG", "SHORT"] | None
    scheduled_event_at: pd.Timestamp | None
    expected_period_end: pd.Timestamp | None
    row: HourlyCloseReference | None
    lag_seconds: float | None
    valid_at_event: bool
    reason: str
    execution_version: str = EXECUTION_VERSION

    @property
    def price(self) -> float | None:
        """Diagnostic source price; valid_at_event is required for event use."""
        return self.row.raw_close if self.row else None


def resolve_reference(
    rows: tuple[HourlyCloseReference, ...],
    plan: ExecutionPlan,
    symbol: str,
    event: Literal["ENTRY", "EXIT"],
    *,
    side: Literal["LONG", "SHORT"] | None = None,
    test_scenario: bool = False,
) -> ExecutionReference:
    """Exact calendar slot only; never fallback, nearest price or shift(4)."""
    if symbol not in UNIVERSE or event not in {"ENTRY", "EXIT"}:
        raise ValueError("UNSUPPORTED_EVENT_KEY")
    if side not in {None, "LONG", "SHORT"}:
        raise ValueError("UNSUPPORTED_SIDE")
    if any(not isinstance(row, HourlyCloseReference) for row in rows):
        raise ValueError("HOURLY_REFERENCE_TYPE_REQUIRED")
    if not _valid_plan(plan):
        return ExecutionReference(symbol, side, None, None, None, None, False, "INVALID_PLAN")
    # _valid_plan established all clocks; row post-init normalizes its timestamp fields.
    end = cast(pd.Timestamp, plan.cutoff) + (
        pd.Timedelta(hours=4) if event == "EXIT" else pd.Timedelta(0)
    )
    when = plan.exit if event == "EXIT" else plan.entry
    slot = next((hour for hour in session_clock(plan.session).hours if hour.end == end), None)
    if slot is None:
        return ExecutionReference(symbol, side, when, end, None, None, False, "NO_FULL_HOUR")
    matching = [r for r in rows if r.symbol == symbol and r.period_end == end]
    if len(matching) > 1:
        raise ValueError("DUPLICATE_HOURLY_REFERENCE")
    row = matching[0] if matching else None
    if row is None:
        reason = "REFERENCE_MISSING"
    elif row.period_start != slot.start:
        reason = "WRONG_SCHEDULED_SLOT"
    elif not _supported(row, test_scenario):
        reason = "AVAILABILITY_UNVERIFIED"
    elif cast(pd.Timestamp, row.available_at) > cast(pd.Timestamp, when):
        reason = "REFERENCE_NOT_AVAILABLE_AT_EVENT"
    else:
        reason = "REFERENCE_AVAILABLE_AT_EVENT"
    return ExecutionReference(
        symbol,
        side,
        when,
        end,
        row,
        (cast(pd.Timestamp, when) - cast(pd.Timestamp, row.period_end)).total_seconds()
        if row else None,
        reason == "REFERENCE_AVAILABLE_AT_EVENT",
        reason,
    )


def proxy_causal_eligibility(
    plan: ExecutionPlan,
    forecast: ForecastEvidence,
    entries: tuple[HourlyCloseReference, ...],
    *,
    test_scenario: bool = False,
) -> CausalEligibility:
    """Only input/entry facts; no exit/action/floor arguments or P3 admission."""
    issuable = bool(
        _valid_plan(plan)
        and forecast.issuable
        and forecast.input_symbols == UNIVERSE
        and forecast.basis in ({"DOCUMENTED", "SYNTHETIC"} if test_scenario else {"DOCUMENTED"})
        and forecast.evidence_ref.strip()
        and utc(forecast.cutoff) == plan.cutoff
    )
    reasons, ids = [], []
    for symbol in UNIVERSE:
        ref = resolve_reference(entries, plan, symbol, "ENTRY", test_scenario=test_scenario)
        ids.append(ref.row.row_id if ref.row else None)
        if not issuable:
            reason = "FORECAST_NOT_ISSUABLE"
        elif not ref.valid_at_event:
            reason = ref.reason
        # valid_at_event entails a supported, present row on the valid plan.
        elif cast(pd.Timestamp, cast(HourlyCloseReference, ref.row).available_at) > cast(
            pd.Timestamp, plan.cutoff
        ):
            # This same close is the completed input endpoint, not later information.
            reason = "ENTRY_REFERENCE_NOT_AVAILABLE_BY_CUTOFF"
        else:
            reason = "ENTRY_REFERENCE_ELIGIBLE"
        reasons.append(reason)
    return CausalEligibility(
        issuable,
        tuple(r == "ENTRY_REFERENCE_ELIGIBLE" for r in reasons),
        tuple(reasons),
        forecast.evidence_ref,
        tuple(ids),
    )


@dataclass(frozen=True)
class ProxyLabelSample(LabelSample):
    references: tuple[ExecutionReference, ...] = ()
    execution_version: str = EXECUTION_VERSION
    target_version: str = TARGET_VERSION
    m2_version: str = M2_VERSION

    @property
    def key(self) -> str:
        return f"{EXECUTION_VERSION}:{TARGET_VERSION}:{M2_VERSION}:{super().key}"


def proxy_label_sample(
    plan: ExecutionPlan,
    forecast: ForecastEvidence,
    entries: tuple[HourlyCloseReference, ...],
    exits: tuple[HourlyCloseReference, ...],
    *,
    observed_at: pd.Timestamp | str,
    actions: ActionScope | None = None,
    test_scenario: bool = False,
) -> ProxyLabelSample:
    """Proxy price-return label, with maturity at/after scheduled event, not close.

    Splits adjust raw reference prices over (entry close, exit close], while
    complete action scope must cover the original cutoff through scheduled exit.
    Late exit publication may mature a diagnostic label later; it never proves
    a fill at the earlier scheduled event. Dividends and portfolio absent.
    """
    causal = proxy_causal_eligibility(plan, forecast, entries, test_scenario=test_scenario)
    observed = utc(observed_at)
    refs = tuple(
        resolve_reference(
            rows, plan, symbol, cast(Literal["ENTRY", "EXIT"], event), test_scenario=test_scenario
        )
        for symbol in UNIVERSE
        for rows, event in ((entries, "ENTRY"), (exits, "EXIT"))
    )
    reason = "LABEL_VALID"
    if not _valid_plan(plan):
        reason = "INVALID_PLAN"
    elif any(ref.row is None for ref in refs):
        reason = "REFERENCE_MISSING"
    elif any(ref.reason == "WRONG_SCHEDULED_SLOT" for ref in refs):
        reason = "WRONG_SCHEDULED_SLOT"
    factors = None
    if reason == "LABEL_VALID" and actions is not None:
        # LABEL_VALID above establishes the validated plan and present references.
        if (
            utc(actions.start) <= cast(pd.Timestamp, plan.cutoff)
            and utc(actions.end) >= cast(pd.Timestamp, plan.exit)
        ):
            # Reuse accepted share-factor validation with explicit price boundaries.
            price_interval = replace(
                plan, entry=plan.cutoff,
                exit=cast(pd.Timestamp, plan.cutoff) + pd.Timedelta(hours=4),
            )
            factors = _split_factors(price_interval, actions, test_scenario)
    if reason == "LABEL_VALID" and factors is None:
        reason = "ACTION_CONVENTION_UNVERIFIED"
    rows = tuple(ref.row for ref in refs if ref.row is not None)
    scenario = bool(
        test_scenario
        or forecast.basis in {"SYNTHETIC", "ASSUMED"}
        or any(
            r.source == "SYNTHETIC" or r.availability_basis in {"SYNTHETIC", "ASSUMED"}
            for r in rows
        )
        or (actions and actions.basis in {"SYNTHETIC", "ASSUMED"})
    )
    returns = centered = m = mad = maturity = None
    maturity_basis = "MATURITY_UNVERIFIED"
    if reason == "LABEL_VALID":
        # Present rows have positive raw_close prices, and factors passed the None gate.
        returns = tuple(
            math.log(cast(float, refs[2 * i + 1].price))
            + math.log(cast(tuple[float, ...], factors)[i])
            - math.log(cast(float, refs[2 * i].price))
            for i in range(5)
        )
        m = median(returns)
        centered = tuple(r - m for r in returns)
        mad = median(abs(r) for r in centered)
        if all(_supported(row, test_scenario) for row in rows):
            maturity = max(
                cast(pd.Timestamp, plan.exit),
                *(cast(pd.Timestamp, row.available_at) for row in rows),
            )
            maturity_basis = "SYNTHETIC" if scenario else "DOCUMENTED_ASSERTION"
            if observed < maturity:
                reason = "LABEL_NOT_MATURED"
            elif not causal.forecast_issuable or not all(causal.entry_eligible):
                reason = "CAUSAL_ELIGIBILITY_BLOCKED"
        else:
            reason = "MATURITY_UNVERIFIED"
    return ProxyLabelSample(
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
        tuple(row.row_id for row in rows),
        tuple(row.source_version for row in rows),
        actions.evidence_ref if actions else None,
        tuple(s.event_id for s in actions.splits) if actions else (),
        scenario,
        references=refs,
    )


def _require_proxy(sample: ProxyLabelSample) -> None:
    if not isinstance(sample, ProxyLabelSample) or (
        sample.execution_version,
        sample.target_version,
        sample.m2_version,
    ) != (EXECUTION_VERSION, TARGET_VERSION, M2_VERSION):
        raise ValueError("PROXY_VERSION_REQUIRED; MINUTE_ARTIFACT_REUSE_FORBIDDEN")
    if sample.label_valid:
        if len(sample.references) != 10 or any(
            not isinstance(ref.row, HourlyCloseReference)
            or ref.execution_version != EXECUTION_VERSION
            or ref.symbol != UNIVERSE[i // 2]
            or ref.row.symbol != ref.symbol
            or ref.expected_period_end
            != cast(pd.Timestamp, sample.plan.cutoff) + pd.Timedelta(hours=4 * (i % 2))
            or ref.row.period_end != ref.expected_period_end
            or ref.scheduled_event_at != (sample.plan.exit if i % 2 else sample.plan.entry)
            for i, ref in enumerate(sample.references)
        ):
            raise ValueError("PROXY_REFERENCE_LINEAGE_REQUIRED")
        # The preceding lineage guard checked every row's type.
        if sample.source_ids != tuple(
            cast(HourlyCloseReference, r.row).row_id for r in sample.references
        ):
            raise ValueError("PROXY_SOURCE_LINEAGE_REQUIRED")


@dataclass(frozen=True)
class ProxyFloor:
    foundation: FittedFloor
    floor_id: str
    execution_version: str = EXECUTION_VERSION
    target_version: str = TARGET_VERSION
    m2_version: str = M2_VERSION

    def __post_init__(self):
        prefix = f"{EXECUTION_VERSION}:{TARGET_VERSION}:{M2_VERSION}:"
        if (
            not isinstance(self.foundation, FittedFloor)
            or not self.foundation.fitting_keys
            or not all(k.startswith(prefix) for k in self.foundation.fitting_keys)
            or len(self.floor_id) != 64
            or any(c not in "0123456789abcdef" for c in self.floor_id)
        ):
            raise ValueError("PROXY_FLOOR_LINEAGE_REQUIRED")

    @property
    def epsilon(self) -> float:
        return self.foundation.epsilon


def proxy_fitting_membership(
    sample: ProxyLabelSample, window: FitWindow, *, test_scenario: bool = False
) -> str:
    _require_proxy(sample)
    return fitting_membership(sample, window, test_scenario=test_scenario)


def fit_proxy_floor(
    samples: tuple[ProxyLabelSample, ...], window: FitWindow, *, test_scenario: bool = False
) -> ProxyFloor:
    """Accepted TG0 train-only fit, with additional proxy lineage binding."""
    for sample in samples:
        _require_proxy(sample)
    foundation = fit_tg0_floor(samples, window, test_scenario=test_scenario)
    bindings = {
        "execution": EXECUTION_VERSION,
        "target": TARGET_VERSION,
        "m2": M2_VERSION,
        "foundation": foundation.floor_id,
        "references": sorted(
            (
                s.key,
                tuple(
                    (
                        # Fitting membership and _require_proxy establish present normalized rows.
                        cast(HourlyCloseReference, r.row).row_id,
                        cast(HourlyCloseReference, r.row).source_version,
                        cast(
                            pd.Timestamp, cast(HourlyCloseReference, r.row).period_start
                        ).isoformat(),
                        cast(
                            pd.Timestamp, cast(HourlyCloseReference, r.row).period_end
                        ).isoformat(),
                        r.price,
                        cast(
                            pd.Timestamp, cast(HourlyCloseReference, r.row).available_at
                        ).isoformat()
                        if cast(HourlyCloseReference, r.row).available_at is not None else None,
                        cast(HourlyCloseReference, r.row).availability_basis,
                        cast(HourlyCloseReference, r.row).evidence_ref,
                        r.lag_seconds,
                    )
                    for r in s.references
                ),
            )
            for s in samples
            if s.key in foundation.fitting_keys
        ),
    }
    floor_id = hashlib.sha256(json.dumps(bindings, sort_keys=True).encode()).hexdigest()
    return ProxyFloor(foundation, floor_id)


@dataclass(frozen=True)
class ProxyTG0Target(TG0Target):
    execution_version: str = EXECUTION_VERSION
    target_version: str = TARGET_VERSION
    m2_version: str = M2_VERSION


def apply_proxy_floor(
    sample: ProxyLabelSample, floor: ProxyFloor, *, test_scenario: bool = False
) -> ProxyTG0Target:
    _require_proxy(sample)
    if not isinstance(floor, ProxyFloor) or (
        floor.execution_version,
        floor.target_version,
        floor.m2_version,
    ) != (EXECUTION_VERSION, TARGET_VERSION, M2_VERSION):
        raise ValueError("PROXY_FLOOR_VERSION_REQUIRED")
    result = apply_tg0_floor(sample, floor.foundation, test_scenario=test_scenario)
    return ProxyTG0Target(sample, floor.floor_id, result.epsilon, result.scores)
