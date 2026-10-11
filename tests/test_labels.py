"""Tagged synthetic raw opens only; no acquired or confirmation price outcomes."""

import math
from dataclasses import replace

import pandas as pd
import pytest

from lstm_data.audit import f01_fixture
from lstm_data.clocks import execution_plan, session_clock
from lstm_data.labels import (
    UNIVERSE,
    ActionScope,
    ForecastEvidence,
    MinuteReference,
    SplitFact,
    apply_tg0_floor,
    causal_eligibility,
    fit_tg0_floor,
    fitting_membership,
    fitting_window,
    label_sample,
    minute_reference,
)


def fixture(day="2020-07-01", origin=1, issued_at=None, logs=(-0.02, -0.01, 0, 0.01, 0.03)):
    plan = execution_plan(session_clock(day), origin, issued_at=issued_at)
    forecast = ForecastEvidence(True, plan.cutoff, UNIVERSE, "SYNTHETIC", "fake-inputs")
    entries = tuple(
        MinuteReference(
            symbol,
            f"{day}:{symbol}:entry",
            plan.entry,
            100 + i * 10,
            "fake-v1",
            "SYNTHETIC",
            plan.entry,
            "SYNTHETIC",
        )
        for i, symbol in enumerate(UNIVERSE)
    )
    exits = tuple(
        replace(
            row,
            row_id=row.row_id.replace("entry", "exit"),
            minute_start=plan.exit,
            raw_open=row.raw_open * math.exp(r),
            available_at=plan.exit + pd.Timedelta(minutes=2),
        )
        for row, r in zip(entries, logs, strict=True)
    )
    actions = ActionScope(plan.entry, plan.exit, UNIVERSE, "SYNTHETIC", "fake-no-actions")
    return plan, forecast, entries, exits, actions


def sample(parts, **changes):
    plan, forecast, entries, exits, actions = parts
    return label_sample(
        plan,
        forecast,
        entries,
        exits,
        observed_at=changes.pop("observed_at", plan.exit + pd.Timedelta(minutes=3)),
        actions=actions,
        test_scenario=True,
        **changes,
    )


@pytest.fixture(scope="module")
def panel():
    return fixture()


@pytest.fixture(scope="module")
def window():
    return fitting_window("WF1", "INNER_TRAIN", fitted_at="2023-06-30T23:00Z")


def test_five_log_returns_unscaled_mad_fitted_floor_and_tg0(panel, window):
    outcome = sample(panel)
    expected = (-0.02, -0.01, 0, 0.01, 0.03)
    assert outcome.raw_returns == pytest.approx(expected)
    assert outcome.cross_median == pytest.approx(0, abs=1e-14)
    assert outcome.centered_returns == pytest.approx(expected)
    assert outcome.unscaled_mad == pytest.approx(0.01)  # Unscaled, not1.4826*MAD.
    floor = fit_tg0_floor((outcome,), window, test_scenario=True)
    assert floor.epsilon == pytest.approx(0.001)
    target = apply_tg0_floor(outcome, floor, test_scenario=True)
    assert target.scores == pytest.approx(tuple(r / 0.011 for r in expected))
    assert len(outcome.source_ids) == 10 and len(outcome.source_versions) == 10
    assert target.floor_id == floor.floor_id and not target.research_ready
    assert outcome.execution_outcome == "NOT_EVALUATED" and outcome.market_status == "HOLD"
    assert floor.floor_id == fit_tg0_floor((outcome,), window, test_scenario=True).floor_id


def test_zero_mad_has_nonzero_training_fitted_floor(window):
    outcome = sample(fixture(logs=(0, 0, 0, 0, 0)))
    floor = fit_tg0_floor((outcome,), window, test_scenario=True)
    assert outcome.unscaled_mad == 0 and floor.epsilon == 1e-4
    assert apply_tg0_floor(outcome, floor, test_scenario=True).scores == (0,) * 5


@pytest.mark.parametrize("origin,entry,exit_time", [(1, "14:33", "18:33"), (2, "15:33", "19:33")])
def test_nominal_pairs_and_shifted_actual_issuance(origin, entry, exit_time):
    parts = fixture(origin=origin)
    plan = parts[0]
    assert plan.entry == pd.Timestamp(f"2020-07-01T{entry}Z")
    assert plan.exit == pd.Timestamp(f"2020-07-01T{exit_time}Z")
    assert sample(parts).label_valid
    shifted = fixture(issued_at="2020-07-01T14:34:30Z")
    assert shifted[0].entry == pd.Timestamp("2020-07-01T14:36Z")
    assert shifted[0].exit == pd.Timestamp("2020-07-01T18:36Z")
    assert sample(shifted).label_valid
    assert minute_reference(parts[2], "AAPL", shifted[0].entry) is None


@pytest.mark.parametrize(
    "day,issue,reason",
    [
        ("2020-11-27", None, "EXIT_OUTSIDE_SESSION"),
        ("2020-11-26", None, "NO_SESSION"),
        ("2020-07-01", "2020-07-01T14:35:01Z", "ISSUANCE_TOO_LATE"),
    ],
)
def test_invalid_plans_rejected_without_prices(day, issue, reason):
    plan = execution_plan(session_clock(day), 1, issued_at=issue)
    forecast = ForecastEvidence(True, "2020-07-01T14:30Z", UNIVERSE, "SYNTHETIC", "fake")
    result = label_sample(
        plan, forecast, (), (), observed_at="2020-11-28T00:00Z", test_scenario=True
    )
    assert result.reason == reason and not result.label_valid
    assert not result.causal.forecast_issuable


def test_future_exit_missing_or_later_publication_changes_only_label(panel):
    before = sample(panel)
    missing = sample((*panel[:3], panel[3][:-1], panel[4]))
    assert missing.reason == "EXIT_REFERENCE_MISSING" and missing.raw_returns is None
    assert missing.causal == before.causal
    assert before.causal.forecast_issuable and all(before.causal.entry_eligible)
    delayed_exits = (
        replace(panel[3][0], available_at=panel[0].exit + pd.Timedelta(hours=1)),
        *panel[3][1:],
    )
    delayed = sample((*panel[:3], delayed_exits, panel[4]))
    assert delayed.reason == "LABEL_NOT_MATURED" and not delayed.label_valid
    assert delayed.causal == before.causal and delayed.maturity > before.maturity
    assert missing.execution_outcome == delayed.execution_outcome == "NOT_EVALUATED"


def test_missing_entry_blocks_that_name_and_five_name_label(panel):
    result = sample((panel[0], panel[1], panel[2][:-1], panel[3], panel[4]))
    assert result.causal.forecast_issuable
    assert result.causal.entry_eligible == (True, True, True, True, False)
    assert result.reason == "ENTRY_REFERENCE_MISSING" and not result.label_valid


def test_exact_minute_symbol_and_duplicate_candidates(panel):
    row = panel[2][0]
    next_minute = replace(
        row,
        minute_start=row.minute_start + pd.Timedelta(minutes=1),
        available_at=row.available_at + pd.Timedelta(minutes=1),
    )
    assert minute_reference((next_minute,), "AAPL", row.minute_start) is None
    assert minute_reference((replace(row, symbol="JPM"),), "AAPL", row.minute_start) is None
    with pytest.raises(ValueError, match="DUPLICATE"):
        minute_reference(
            (row, replace(row, row_id="other", raw_open=999)), "AAPL", row.minute_start
        )


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("raw_open", 0, "INVALID_RAW_OPEN"),
        ("raw_open", float("inf"), "INVALID_RAW_OPEN"),
        ("raw_open", float("nan"), "INVALID_RAW_OPEN"),
        ("duration_minutes", 30, "INVALID_MINUTE"),
        ("price_field", "close", "UNSUPPORTED_SOURCE_FIELDS"),
        ("adjustment", "split", "UNSUPPORTED_SOURCE_FIELDS"),
        ("symbol", "SPY", "UNSUPPORTED_SYMBOL"),
    ],
)
def test_bad_source_fields_and_values_rejected(panel, field, value, reason):
    with pytest.raises(ValueError, match=reason):
        replace(panel[2][0], **{field: value})


def test_unknown_maturity_and_entry_publication_fail_closed(panel, window):
    exits = (replace(panel[3][0], available_at=None, availability_basis="UNKNOWN"), *panel[3][1:])
    result = sample((*panel[:3], exits, panel[4]))
    assert result.raw_returns is not None and result.maturity is None
    assert result.reason == "MATURITY_UNVERIFIED" and not result.label_valid
    assert fitting_membership(result, window, test_scenario=True) == "MATURITY_UNVERIFIED"
    with pytest.raises(ValueError, match="NO_VALID_FLOOR"):
        fit_tg0_floor((result,), window, test_scenario=True)
    entries = (
        replace(panel[2][0], available_at=panel[0].entry + pd.Timedelta(seconds=1)),
        *panel[2][1:],
    )
    causal = causal_eligibility(panel[0], panel[1], entries, test_scenario=True)
    assert causal.entry_reasons[0] == "ENTRY_REFERENCE_NOT_YET_AVAILABLE"
    assert not causal.entry_eligible[0]
    assumed = (replace(panel[2][0], availability_basis="ASSUMED"), *panel[2][1:])
    assert not causal_eligibility(panel[0], panel[1], assumed, test_scenario=True).entry_eligible[0]


def test_maturity_delay_not_usable_before_latest_availability(panel):
    result = sample(panel)
    assert result.maturity == panel[0].exit + pd.Timedelta(minutes=2)
    early = sample(panel, observed_at=panel[0].exit + pd.Timedelta(minutes=1))
    assert early.reason == "LABEL_NOT_MATURED" and not early.label_valid


def test_chronological_inner_tail_and_no_fit_floor_on_validation(panel):
    inner = fitting_window("WF1", "INNER_TRAIN", fitted_at="2023-06-30T23:00Z")
    validation = fitting_window("WF1", "INNER_VALIDATION", fitted_at="2023-06-30T23:00Z")
    # Independent XNYS count: Jun30 inclusive backwards63 sessions begins Mar31.
    assert inner.stop == validation.start == pd.Timestamp("2023-03-31T04:00Z")
    assert validation.stop == pd.Timestamp("2023-07-01T04:00Z")
    earlier = sample(fixture(day="2023-03-30"))
    tail = sample(fixture(day="2023-03-31"))
    assert fitting_membership(earlier, inner, test_scenario=True) == "FIT_ELIGIBLE"
    assert fitting_membership(tail, inner, test_scenario=True) == "ORIGIN_OUTSIDE_FIT_WINDOW"
    assert fitting_membership(tail, validation, test_scenario=True) == "FIT_ELIGIBLE"
    baseline = fit_tg0_floor((sample(panel),), inner, test_scenario=True)
    extreme_tail = sample(fixture(day="2023-03-31", logs=(-9, -8, 0, 8, 9)))
    guarded = fit_tg0_floor((sample(panel), extreme_tail), inner, test_scenario=True)
    assert guarded.epsilon == baseline.epsilon
    assert guarded.exclusions == ((extreme_tail.key, "ORIGIN_OUTSIDE_FIT_WINDOW"),)
    with pytest.raises(ValueError, match="TRAINING_POPULATION"):
        fit_tg0_floor((tail,), validation, test_scenario=True)


@pytest.mark.parametrize(
    "stage,stop",
    [
        ("WF1", "2023-07-01T04:00Z"),
        ("WF2", "2024-01-01T05:00Z"),
        ("PRECONFIRMATION", "2024-07-01T04:00Z"),
    ],
)
def test_frozen_outer_boundaries_and_maturity_purging(panel, stage, stop):
    window = fitting_window(stage, "REFIT", fitted_at=stop)
    assert window.stop == pd.Timestamp(stop)
    good = sample(panel)
    assert fitting_membership(good, window, test_scenario=True) == "FIT_ELIGIBLE"
    # Synthetic timing metadata only; no final-confirmation price observations.
    crossing = replace(good, maturity=window.stop, observed_at=window.stop)
    assert fitting_membership(crossing, window, test_scenario=True) == "PURGED_SPLIT_BOUNDARY"
    exit_crossing = replace(good, plan=replace(good.plan, exit=window.stop))
    assert fitting_membership(exit_crossing, window, test_scenario=True) == "PURGED_SPLIT_BOUNDARY"
    evaluation_origin = replace(good, plan=replace(good.plan, cutoff=window.stop))
    assert (
        fitting_membership(evaluation_origin, window, test_scenario=True)
        == "ORIGIN_OUTSIDE_FIT_WINDOW"
    )


def test_actual_fit_timestamp_empty_duplicates_and_synthetic_guard(panel, window):
    good = sample(panel)
    too_early = replace(window, fitted_at=good.maturity - pd.Timedelta(seconds=1))
    assert fitting_membership(good, too_early, test_scenario=True) == "NOT_MATURED_BY_FIT"
    assert fitting_membership(good, window) == "SYNTHETIC_NOT_RESEARCH_DATA"
    with pytest.raises(ValueError, match="NO_VALID_FLOOR"):
        fit_tg0_floor((), window, test_scenario=True)
    with pytest.raises(ValueError, match="DUPLICATE_FITTING"):
        fit_tg0_floor((good, good), window, test_scenario=True)
    floor = fit_tg0_floor((good,), window, test_scenario=True)
    with pytest.raises(ValueError, match="SYNTHETIC_NOT"):
        apply_tg0_floor(good, floor)


def test_split_share_conversion_requires_explicit_interval_facts(panel):
    no_scope = label_sample(
        *panel[:4], observed_at=panel[0].exit + pd.Timedelta(minutes=3), test_scenario=True
    )
    assert no_scope.reason == "ACTION_CONVENTION_UNVERIFIED"
    split = SplitFact(
        "AAPL", panel[0].entry + pd.Timedelta(hours=2), 4, 1, "fake-split", "SYNTHETIC"
    )
    actions = replace(panel[4], splits=(split,))
    exits = (replace(panel[3][0], raw_open=panel[2][0].raw_open / 4), *panel[3][1:])
    converted = sample((*panel[:3], exits, actions))
    assert converted.label_valid and converted.raw_returns[0] == pytest.approx(0, abs=1e-14)
    assert converted.split_ids == ("fake-split",)
    unresolved = sample((*panel[:3], exits, replace(actions, basis="UNKNOWN")))
    assert unresolved.reason == "ACTION_CONVENTION_UNVERIFIED"
    assert converted.causal == unresolved.causal
    dividend = sample((*panel[:4], replace(panel[4], unsupported_action=True)))
    assert dividend.reason == "ACTION_CONVENTION_UNVERIFIED"  # No cashflow invented.


def test_upstream_full_five_population_and_f01_preserved(panel):
    wrong_population = replace(panel[1], input_symbols=UNIVERSE[:-1])
    causal = causal_eligibility(panel[0], wrong_population, panel[2], test_scenario=True)
    assert not causal.forecast_issuable and not any(causal.entry_eligible)
    assert f01_fixture()["reason"] == "STALE_PERIOD_END"


def test_modified_plan_cannot_borrow_nominal_reference_prices(panel):
    modified = replace(panel[0], cutoff=panel[0].cutoff - pd.Timedelta(minutes=1))
    result = sample((modified, *panel[1:]))
    assert result.reason == "INVALID_PLAN" and not result.causal.forecast_issuable
    absent_issue = replace(panel[0], issuance=None)
    assert sample((absent_issue, *panel[1:])).reason == "INVALID_PLAN"


def test_unscheduled_origin_has_auditable_exclusion_key(window):
    plan = execution_plan(session_clock("2020-11-26"), 1)
    forecast = ForecastEvidence(False, "2020-11-26T15:30Z", UNIVERSE, "SYNTHETIC", "fake")
    result = label_sample(
        plan, forecast, (), (), observed_at="2020-11-26T20:00Z", test_scenario=True
    )
    assert result.key == "2020-11-26:1:NO_CUTOFF"
    with pytest.raises(ValueError, match="NO_VALID_FLOOR"):
        fit_tg0_floor((result,), window, test_scenario=True)
