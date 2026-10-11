"""Independent calendar expectations and synthetic causal boundaries, no source reads."""

from dataclasses import replace
from pathlib import Path

import pandas as pd
import pytest

from lstm_data.audit import f01_fixture
from lstm_data.clocks import (
    SessionClock,
    SourceObservation,
    clock_trace,
    execution_plan,
    forecast_origins,
    observation_at_cutoff,
    origin_boundary,
    session_clock,
)
from lstm_data.ledger import current_blockers, read_ledger


def et(day, time):
    return pd.Timestamp(f"{day} {time}", tz="America/New_York")


@pytest.fixture(scope="module")
def ordinary():
    return session_clock("2020-07-01")


def synthetic(slot, *, available=None):
    return SourceObservation(
        "synthetic-hour",
        "FAKE",
        slot.start,
        "SYNTHETIC",
        slot.start,
        slot.end,
        "SYNTHETIC",
        slot.end if available is None else available,
        "SYNTHETIC",
    )


def test_ordinary_slots_stub_and_two_exact_240_minute_pairs(ordinary):
    assert len(ordinary.hours) == 6
    for i, slot in enumerate(ordinary.hours):
        assert slot.start == et("2020-07-01", f"{9 + i}:30")
        assert slot.end == et("2020-07-01", f"{10 + i}:30")
        assert not slot.is_stub
    assert ordinary.terminal_stub.start == et("2020-07-01", "15:30")
    assert ordinary.terminal_stub.end == et("2020-07-01", "16:00")
    assert ordinary.terminal_stub.is_stub
    for plan, hour in zip(forecast_origins(ordinary), (10, 11), strict=True):
        assert plan.cutoff == et("2020-07-01", f"{hour}:30")
        assert plan.issuance == et("2020-07-01", f"{hour}:32")
        assert plan.entry == et("2020-07-01", f"{hour}:33")
        assert plan.exit == et("2020-07-01", f"{hour + 4}:33")
        assert plan.exit - plan.entry == pd.Timedelta(minutes=240)
        assert plan.issuance_kind == "PLANNED_SYNTHETIC"
        assert plan.reason == "SCHEDULE_VALID"
        assert str(plan.entry.tz) == "UTC"


def test_real_early_close_rejects_both_origins():
    clock = session_clock("2020-11-27")
    assert clock.close == et("2020-11-27", "13:00")
    assert len(clock.hours) == 3
    assert clock.hours[-1].end == et("2020-11-27", "12:30")
    assert clock.terminal_stub.start == et("2020-11-27", "12:30")
    assert clock.terminal_stub.end == et("2020-11-27", "13:00")
    assert [p.reason for p in forecast_origins(clock)] == ["EXIT_OUTSIDE_SESSION"] * 2
    assert forecast_origins(clock)[1].exit == et("2020-11-27", "15:33")


@pytest.mark.parametrize("day,utc_hour", [("2020-01-02", 15), ("2020-07-01", 14)])
def test_dst_local_events_stable_utc_changes(day, utc_hour):
    plan = forecast_origins(session_clock(day))[0]
    assert plan.entry == et(day, "10:33")
    assert plan.entry.hour == utc_hour
    assert plan.exit == et(day, "14:33")
    assert plan.exit - plan.entry == pd.Timedelta(minutes=240)


def test_holiday_and_no_full_hour():
    clock = session_clock("2020-11-26")
    assert clock.reason == "NO_SESSION" and clock.hours == ()
    assert forecast_origins(clock) == ()
    assert execution_plan(clock, 1).entry is None
    short = SessionClock(
        "synthetic-short",
        et("2020-07-01", "09:30"),
        et("2020-07-01", "10:00"),
        (),
        None,
        "SYNTHETIC",
    )
    assert execution_plan(short, 1).reason == "NO_FULL_HOUR"


@pytest.mark.parametrize(
    "seconds,entry_time,reason",
    [
        (120, "10:33", "SCHEDULE_VALID"),
        (300, "10:36", "SCHEDULE_VALID"),
        (270, "10:36", "SCHEDULE_VALID"),
        (301, None, "ISSUANCE_TOO_LATE"),
        (-1, None, "ISSUANCE_BEFORE_CUTOFF"),
    ],
)
def test_actual_issuance_inclusive_boundary_and_ceiling(ordinary, seconds, entry_time, reason):
    cutoff = et("2020-07-01", "10:30")
    issued = cutoff + pd.Timedelta(seconds=seconds)
    plan = execution_plan(ordinary, 1, issued_at=issued)
    assert plan.reason == reason
    assert plan.issuance_kind == "ACTUAL" and plan.issuance == issued
    if entry_time is None:
        assert plan.entry is None and plan.exit is None
    else:
        assert plan.entry == et("2020-07-01", entry_time)
        assert plan.entry >= issued + pd.Timedelta(minutes=1)
        assert plan.entry.second == 0
        assert plan.exit == plan.entry + pd.Timedelta(minutes=240)
        assert plan.cutoff == cutoff


def test_minute_open_at_close_is_rejected(ordinary):
    shortened = replace(ordinary, close=et("2020-07-01", "14:33"))
    assert execution_plan(shortened, 1).reason == "EXIT_OUTSIDE_SESSION"


def test_publication_predicate_synthetic_only_unknowns_fail_closed(ordinary):
    slot = ordinary.hours[0]
    cutoff = slot.end + pd.Timedelta(seconds=1)
    bar = synthetic(slot)
    check = observation_at_cutoff(bar, cutoff, expected_slot=slot, test_scenario=True)
    assert check.usable and check.scenario_only and not check.source_asof_verified
    late = replace(bar, available_at=cutoff + pd.Timedelta(seconds=1))
    assert (
        observation_at_cutoff(late, cutoff, test_scenario=True).reason == "SOURCE_BAR_UNAVAILABLE"
    )
    assert observation_at_cutoff(bar, cutoff).reason == "SCENARIO_NOT_AUTHORIZED"
    assert (
        observation_at_cutoff(replace(bar, available_at=None), cutoff).reason
        == "SOURCE_CLOCK_UNKNOWN"
    )
    assert (
        observation_at_cutoff(replace(bar, period_basis="UNKNOWN"), cutoff).reason
        == "SOURCE_CLOCK_UNKNOWN"
    )


def test_documented_contract_needs_evidence_and_never_derives_publication(ordinary):
    slot = ordinary.hours[0]
    bar = replace(
        synthetic(slot),
        native_basis="DOCUMENTED",
        period_basis="DERIVED",
        availability_basis="DOCUMENTED",
        evidence_ref="synthetic-test-reference-only",
    )
    assert observation_at_cutoff(bar, slot.end, expected_slot=slot).source_asof_verified
    assert not observation_at_cutoff(replace(bar, evidence_ref=None), slot.end).usable
    assert not observation_at_cutoff(replace(bar, availability_basis="DERIVED"), slot.end).usable
    assert not observation_at_cutoff(replace(bar, availability_basis="ASSUMED"), slot.end).usable


def test_completion_and_anchored_slot_compatibility(ordinary):
    slot = ordinary.hours[0]
    bar = synthetic(slot)
    assert (
        observation_at_cutoff(bar, slot.end - pd.Timedelta(seconds=1), test_scenario=True).reason
        == "SOURCE_PERIOD_INCOMPLETE"
    )
    assert (
        observation_at_cutoff(
            replace(bar, available_at=slot.start), slot.end, test_scenario=True
        ).reason
        == "INVALID_SOURCE_INTERVAL"
    )
    incompatible = replace(bar, period_start=slot.start - pd.Timedelta(minutes=30))
    assert (
        observation_at_cutoff(incompatible, slot.end, expected_slot=slot, test_scenario=True).reason
        == "INCOMPATIBLE_FEATURE_SLOT"
    )
    stub = ordinary.terminal_stub
    assert not observation_at_cutoff(
        synthetic(stub), stub.end, expected_slot=stub, test_scenario=True
    ).usable


def test_later_issuance_never_admits_post_cutoff_observation_mutation(ordinary):
    plan = execution_plan(ordinary, 1, issued_at=et("2020-07-01", "10:35"))
    bar = synthetic(ordinary.hours[0])
    post_cutoff = replace(
        bar,
        observation_id="future",
        period_start=plan.cutoff,
        period_end=plan.cutoff + pd.Timedelta(minutes=2),
        available_at=plan.cutoff + pd.Timedelta(minutes=2),
    )
    records = [(bar, 100), (post_cutoff, 101)]

    def information_set(items):
        return [
            (observation.observation_id, price)
            for observation, price in items
            if observation_at_cutoff(observation, plan.cutoff, test_scenario=True).usable
        ]

    before = information_set(records)
    records[1] = (post_cutoff, 99999)
    assert information_set(records) == before == [("synthetic-hour", 100)]
    late_check = observation_at_cutoff(post_cutoff, plan.issuance, test_scenario=True)
    assert late_check.usable  # Wrong cutoff would admit it; boundary independently rejects it.
    assert not origin_boundary(plan, (late_check,)).clock_and_information_issuable


def test_d13_future_exit_not_an_origin_or_entry_input(ordinary):
    plan = execution_plan(ordinary, 1)
    bar = synthetic(ordinary.hours[0])
    step = observation_at_cutoff(bar, plan.cutoff, test_scenario=True)
    future = {"exit_observation": 100}
    before = origin_boundary(plan, (step,))
    future["exit_observation"] = None
    assert origin_boundary(plan, (step,)) == before
    assert before.clock_and_information_issuable
    assert not before.source_asof_verified
    assert before.entry_eligible is before.label_valid is before.execution_outcome is None
    assert not origin_boundary(plan, ()).clock_and_information_issuable
    unknown = observation_at_cutoff(replace(bar, available_at=None), plan.cutoff)
    assert not origin_boundary(plan, (unknown,)).clock_and_information_issuable


def test_f01_existing_counterexample_and_research_blockers():
    fixture = f01_fixture()
    assert fixture["status"] == "PASS"
    assert fixture["period_end_age_minutes"] == 120
    assert fixture["observed_available_age_minutes"] == 60
    assert fixture["reason"] == "STALE_PERIOD_END" and not fixture["observed_usable"]
    root = Path(__file__).resolve().parents[1]
    blockers = current_blockers(read_ledger(root / "reports/audit/track_a_events.jsonl"))
    assert {
        "p0.1-stock-publication",
        "p0.1-shared-D3-clock",
        "p0.1-USA500-source-clock",
        "p0.1-minute-execution",
    } <= {event["event_id"] for event in blockers}


def test_trace_unknown_publication_and_invalid_inputs(ordinary):
    plan = execution_plan(ordinary, 1)
    bar = replace(synthetic(ordinary.hours[0]), available_at=None, availability_basis="UNKNOWN")
    check = observation_at_cutoff(bar, plan.cutoff)
    trace = clock_trace(plan, bar, check)
    assert trace["calendar_valid"] and not trace["source_asof_verified"]
    assert trace["G2_status"] == "BLOCKED" and trace["available_at"] is None
    assert trace["information_reason"] == "SOURCE_CLOCK_UNKNOWN"
    missing = replace(bar, available_at=pd.NaT)
    missing_check = observation_at_cutoff(missing, plan.cutoff)
    assert missing_check.reason == "SOURCE_CLOCK_UNKNOWN"
    assert clock_trace(plan, missing, missing_check)["available_at"] is None
    with pytest.raises(ValueError, match="identity"):
        clock_trace(plan, bar, replace(check, observation_id="wrong"))
    with pytest.raises(ValueError, match="timezone-aware"):
        execution_plan(ordinary, 1, issued_at="2020-07-01 10:32")
    with pytest.raises(ValueError, match="origins"):
        execution_plan(ordinary, 3)
