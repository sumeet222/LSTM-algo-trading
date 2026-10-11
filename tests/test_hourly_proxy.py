"""P2.2A-R1 synthetic reference arithmetic/timing; no source rows or fills."""

import math
from dataclasses import replace
from typing import Callable, cast

import pandas as pd
import pytest

from lstm_data.clocks import execution_plan, session_clock
from lstm_data.hourly_proxy import (
    EXECUTION_VERSION,
    M2_VERSION,
    TARGET_VERSION,
    HourlyCloseReference,
    ProxyFloor,
    apply_proxy_floor,
    fit_proxy_floor,
    proxy_causal_eligibility,
    proxy_fitting_membership,
    proxy_label_sample,
    resolve_reference,
)
from lstm_data.labels import (
    UNIVERSE,
    ActionScope,
    FitWindow,
    ForecastEvidence,
    MinuteReference,
    SplitFact,
    fit_tg0_floor,
    fitting_window,
    label_sample,
)


def fixture(day="2020-07-01", origin=1, issued_at=None, ratios=(0.98, 0.99, 1.0, 1.01, 1.03)):
    plan = execution_plan(session_clock(day), origin, issued_at=issued_at)
    # Fixture callers select complete normal-session plans; row post-init normalizes clocks.
    forecast = ForecastEvidence(
        True, cast(pd.Timestamp, plan.cutoff), UNIVERSE, "SYNTHETIC", "fake-input"
    )
    entries = tuple(
        HourlyCloseReference(
            s,
            f"{day}:{s}:entry",
            cast(pd.Timestamp, plan.cutoff) - pd.Timedelta(hours=1),
            cast(pd.Timestamp, plan.cutoff),
            100.0,
            "fake-raw-v1",
            "SYNTHETIC",
            plan.cutoff,
            "SYNTHETIC",
        )
        for s in UNIVERSE
    )
    exits = tuple(
        replace(
            r,
            row_id=r.row_id.replace("entry", "exit"),
            period_start=cast(pd.Timestamp, r.period_start) + pd.Timedelta(hours=4),
            period_end=cast(pd.Timestamp, r.period_end) + pd.Timedelta(hours=4),
            available_at=cast(pd.Timestamp, r.period_end) + pd.Timedelta(hours=4),
            raw_close=100.0 * ratio,
        )
        for r, ratio in zip(entries, ratios, strict=True)
    )
    actions = ActionScope(
        cast(pd.Timestamp, plan.cutoff), cast(pd.Timestamp, plan.exit),
        UNIVERSE, "SYNTHETIC", "fake-no-actions",
    )
    return plan, forecast, entries, exits, actions


def sample(parts, **changes):
    plan, forecast, entries, exits, actions = parts
    return proxy_label_sample(
        plan,
        forecast,
        entries,
        exits,
        observed_at=changes.pop("observed_at", plan.exit),
        actions=actions,
        test_scenario=True,
        **changes,
    )


@pytest.fixture
def window():
    return fitting_window("WF1", "INNER_TRAIN", fitted_at="2023-06-30T23:00Z")


@pytest.mark.parametrize(
    "origin,end,exit_event",
    [(1, "2020-07-01T18:30Z", "2020-07-01T18:33Z"), (2, "2020-07-01T19:30Z", "2020-07-01T19:33Z")],
)
def test_exact_nominal_slots_and_independent_five_name_tg0(origin, end, exit_event, window):
    outcome = sample(fixture(origin=origin))
    assert outcome.references[1].expected_period_end == pd.Timestamp(end)
    assert outcome.references[1].scheduled_event_at == pd.Timestamp(exit_event)
    assert all(r.lag_seconds == 180 for r in outcome.references)
    expected = tuple(math.log(x) for x in (0.98, 0.99, 1.0, 1.01, 1.03))
    assert outcome.raw_returns == pytest.approx(expected)
    assert outcome.cross_median == pytest.approx(0, abs=1e-14)
    assert outcome.unscaled_mad == pytest.approx(-math.log(0.99))
    floor = fit_proxy_floor((outcome,), window, test_scenario=True)
    epsilon = 0.1 * -math.log(0.99)
    assert floor.epsilon == pytest.approx(epsilon)
    target = apply_proxy_floor(outcome, floor, test_scenario=True)
    assert target.scores == pytest.approx(tuple(r / (-math.log(0.99) + epsilon) for r in expected))
    assert outcome.maturity == outcome.plan.exit and outcome.label_valid
    assert target.execution_version == EXECUTION_VERSION
    assert target.target_version == TARGET_VERSION and target.m2_version == M2_VERSION
    assert outcome.execution_outcome == "NOT_EVALUATED" and not target.research_ready
    assert outcome.market_status == "HOLD"


def test_two_requested_single_stock_hand_returns():
    one = sample(fixture(ratios=(1.02, 1.0, 1.0, 1.0, 1.0)))
    two = sample(fixture(origin=2, ratios=(0.99, 1.0, 1.0, 1.0, 1.0)))
    # These complete synthetic panels construct nonmissing diagnostic returns.
    assert cast(tuple[float, ...], one.raw_returns)[0] == pytest.approx(math.log(102 / 100))
    assert cast(tuple[float, ...], two.raw_returns)[0] == pytest.approx(math.log(198 / 200))


def test_delayed_issuance_keeps_original_source_boundaries_and_true_age():
    parts = fixture(issued_at="2020-07-01T14:35Z")
    out = sample(parts)
    assert out.plan.cutoff == pd.Timestamp("2020-07-01T14:30Z")
    assert out.plan.entry == pd.Timestamp("2020-07-01T14:36Z")
    assert out.plan.exit == pd.Timestamp("2020-07-01T18:36Z")
    assert all(ref.lag_seconds == 360 for ref in out.references)
    assert cast(HourlyCloseReference, out.references[1].row).period_end == pd.Timestamp(
        "2020-07-01T18:30Z"
    )
    assert out.maturity == out.plan.exit


def test_no_early_maturity_even_with_available_exit_closes(window):
    parts = fixture()
    out = sample(parts, observed_at="2020-07-01T18:30Z")
    assert out.maturity == pd.Timestamp("2020-07-01T18:33Z")
    assert out.reason == "LABEL_NOT_MATURED" and not out.label_valid
    with pytest.raises(ValueError, match="NO_VALID"):
        fit_proxy_floor((out,), window, test_scenario=True)


def test_late_exit_availability_matures_later_without_implying_fill():
    plan, forecast, entries, exits, actions = fixture()
    delayed = tuple(replace(r, available_at="2020-07-01T18:40Z") for r in exits)
    parts = plan, forecast, entries, delayed, actions
    early = sample(parts)
    mature = sample(parts, observed_at="2020-07-01T18:40Z")
    assert early.reason == "LABEL_NOT_MATURED"
    assert mature.maturity == pd.Timestamp("2020-07-01T18:40Z") and mature.label_valid
    assert not mature.references[1].valid_at_event
    assert mature.execution_outcome == "NOT_EVALUATED"


def test_future_exit_counterfactual_does_not_change_causal_admission():
    plan, forecast, entries, exits, actions = fixture()
    before = proxy_causal_eligibility(plan, forecast, entries, test_scenario=True)
    missing = sample((plan, forecast, entries, exits[:-1], actions))
    delayed = sample(
        (
            plan,
            forecast,
            entries,
            tuple(
                replace(r, available_at=cast(pd.Timestamp, plan.exit) + pd.Timedelta(days=1))
                for r in exits
            ),
            actions,
        )
    )
    assert missing.causal == delayed.causal == before
    assert all(before.entry_eligible)
    assert not missing.label_valid and not delayed.label_valid


def test_exact_lookup_no_next_hour_and_duplicate_or_minute_fallback():
    plan, _, entries, _, _ = fixture()
    shifted = tuple(
        replace(
            r,
            period_start=cast(pd.Timestamp, r.period_start) + pd.Timedelta(hours=1),
            period_end=cast(pd.Timestamp, r.period_end) + pd.Timedelta(hours=1),
            available_at=cast(pd.Timestamp, r.available_at) + pd.Timedelta(hours=1),
        )
        for r in entries
    )
    assert resolve_reference(shifted, plan, "AAPL", "ENTRY", test_scenario=True).row is None
    with pytest.raises(ValueError, match="DUPLICATE"):
        resolve_reference(entries + (entries[0],), plan, "AAPL", "ENTRY", test_scenario=True)
    minute = MinuteReference(
        "AAPL", "fake", cast(pd.Timestamp, plan.entry), 100.0, "fake", "SYNTHETIC"
    )
    with pytest.raises(ValueError, match="TYPE_REQUIRED"):
        # Deliberately call outside the static input contract to test runtime rejection.
        # Erase only callable parameter types, without claiming the minute row is hourly.
        cast(Callable[..., object], resolve_reference)(
            (minute,), plan, "AAPL", "ENTRY", test_scenario=True
        )


@pytest.mark.parametrize(
    "change",
    [
        dict(raw_close=0),
        dict(raw_close=float("nan")),
        dict(raw_close=float("inf")),
        dict(adjustment="split"),
        dict(price_field="open"),
        dict(symbol="USA500"),
        dict(source="DUKASCOPY"),
        dict(period_end="2020-07-01T14:00Z"),
        dict(available_at="2020-07-01T14:29Z"),
    ],
)
def test_reject_bad_price_basis_source_and_stub_interval(change):
    with pytest.raises(ValueError):
        replace(fixture()[2][0], **change)


@pytest.mark.parametrize("basis", ["UNKNOWN", "ASSUMED"])
def test_unknown_or_assumed_exit_clock_blocks_supervision(basis, window):
    plan, forecast, entries, exits, actions = fixture()
    rows = tuple(
        replace(
            r,
            source="ALPACA_SIP",
            availability_basis=basis,
            available_at=None if basis == "UNKNOWN" else r.available_at,
        )
        for r in exits
    )
    out = sample((plan, forecast, entries, rows, actions))
    assert out.raw_returns is not None and out.reason == "MATURITY_UNVERIFIED"
    assert out.maturity is None and not out.label_valid
    with pytest.raises(ValueError, match="NO_VALID"):
        fit_proxy_floor((out,), window, test_scenario=True)


def test_entry_close_must_be_available_at_original_input_cutoff():
    plan, forecast, entries, exits, actions = fixture()
    late = tuple(
        replace(r, available_at=cast(pd.Timestamp, plan.cutoff) + pd.Timedelta(minutes=1))
        for r in entries
    )
    out = sample((plan, forecast, late, exits, actions))
    assert out.reason == "CAUSAL_ELIGIBILITY_BLOCKED"
    assert set(out.causal.entry_reasons) == {"ENTRY_REFERENCE_NOT_AVAILABLE_BY_CUTOFF"}
    assert out.plan.cutoff == plan.cutoff


def test_split_covers_reference_interval_even_before_scheduled_entry():
    plan, forecast, entries, exits, actions = fixture(ratios=(0.51, 1.0, 1.0, 1.0, 1.0))
    fact = SplitFact(
        "AAPL", cast(pd.Timestamp, plan.cutoff) + pd.Timedelta(minutes=1),
        2, 1, "fake-split", "SYNTHETIC",
    )
    out = sample((plan, forecast, entries, exits, replace(actions, splits=(fact,))))
    assert cast(tuple[float, ...], out.raw_returns)[0] == pytest.approx(math.log(1.02))
    assert out.label_valid and out.split_ids == ("fake-split",)
    wrong_scope = replace(actions, start=plan.entry, splits=(fact,))
    assert (
        sample((plan, forecast, entries, exits, wrong_scope)).reason
        == "ACTION_CONVENTION_UNVERIFIED"
    )


def test_purge_uses_actual_event_and_availability_not_hour_end():
    parts = fixture()
    out = sample(parts)
    boundary = FitWindow(
        "synthetic-boundary",
        cast(pd.Timestamp, parts[0].cutoff),
        pd.Timestamp("2020-07-01T18:31Z"),
        cast(pd.Timestamp, out.maturity),
        "INNER_TRAIN",
    )
    assert proxy_fitting_membership(out, boundary, test_scenario=True) == "PURGED_SPLIT_BOUNDARY"
    plan, forecast, entries, exits, actions = parts
    later = sample(
        (
            plan,
            forecast,
            entries,
            tuple(replace(r, available_at="2020-07-01T18:40Z") for r in exits),
            actions,
        ),
        observed_at="2020-07-01T18:40Z",
    )
    boundary = replace(boundary, stop=pd.Timestamp("2020-07-01T18:35Z"), fitted_at=later.maturity)
    assert proxy_fitting_membership(later, boundary, test_scenario=True) == "PURGED_SPLIT_BOUNDARY"
    boundary = replace(boundary, stop=pd.Timestamp("2020-07-02T00:00Z"), fitted_at=out.maturity)
    assert proxy_fitting_membership(later, boundary, test_scenario=True) == "NOT_MATURED_BY_FIT"


def test_version_bound_floor_determinism_and_minute_mix_rejection(window):
    parts = fixture()
    out = sample(parts)
    floor = fit_proxy_floor((out,), window, test_scenario=True)
    assert floor == fit_proxy_floor((out,), window, test_scenario=True)
    assert out.key.startswith(EXECUTION_VERSION)
    plan, forecast, entries, exits, actions = parts
    minutes = tuple(
        MinuteReference(
            r.symbol,
            r.row_id,
            cast(pd.Timestamp, plan.entry),
            r.raw_close,
            r.source_version,
            "SYNTHETIC",
            plan.entry,
            "SYNTHETIC",
        )
        for r in entries
    )
    minute_exits = tuple(
        replace(r, minute_start=plan.exit, available_at=plan.exit, raw_open=exits[i].raw_close)
        for i, r in enumerate(minutes)
    )
    old = label_sample(
        plan,
        forecast,
        minutes,
        minute_exits,
        observed_at=cast(pd.Timestamp, plan.exit),
        actions=actions,
        test_scenario=True,
    )
    old_floor = fit_tg0_floor((old,), window, test_scenario=True)
    assert old.label_valid and floor.floor_id != old_floor.floor_id
    with pytest.raises(ValueError, match="VERSION_REQUIRED"):
        # Invalid minute/proxy mixtures intentionally exercise runtime boundary guards.
        cast(Callable[..., object], fit_proxy_floor)((out, old), window, test_scenario=True)
    with pytest.raises(ValueError, match="VERSION_REQUIRED"):
        cast(Callable[..., object], apply_proxy_floor)(out, old_floor, test_scenario=True)
    with pytest.raises(ValueError, match="LINEAGE_REQUIRED"):
        ProxyFloor(old_floor, "b" * 64)
    with pytest.raises(ValueError, match="VERSION_REQUIRED"):
        fit_proxy_floor((replace(out, target_version="minute"),), window, test_scenario=True)
    with pytest.raises(ValueError, match="LINEAGE_REQUIRED"):
        fit_proxy_floor((replace(out, references=()),), window, test_scenario=True)


def test_floor_train_only_zero_mad_no_refit_and_scenario_opt_in(window):
    out = sample(fixture(ratios=(1.0,) * 5))
    floor = fit_proxy_floor((out,), window, test_scenario=True)
    assert floor.epsilon == 0.0001
    assert apply_proxy_floor(out, floor, test_scenario=True).scores == (0.0,) * 5
    with pytest.raises(ValueError, match="TRAINING"):
        fit_proxy_floor((out,), replace(window, phase="INNER_VALIDATION"), test_scenario=True)
    with pytest.raises(ValueError, match="SYNTHETIC"):
        apply_proxy_floor(out, floor)
    no_opt_in = proxy_label_sample(
        *fixture()[:4], observed_at=cast(pd.Timestamp, out.plan.exit), actions=fixture()[4]
    )
    assert not no_opt_in.label_valid


def test_early_close_invalid_and_tampered_plan_not_accepted():
    plan, forecast, entries, exits, actions = fixture()
    tampered = replace(plan, exit=cast(pd.Timestamp, plan.exit) + pd.Timedelta(minutes=1))
    assert sample((tampered, forecast, entries, exits, actions)).reason == "INVALID_PLAN"
    short = execution_plan(session_clock("2020-11-27"), 1)
    assert not short.calendar_valid
    assert (
        resolve_reference(entries, short, "AAPL", "ENTRY", test_scenario=True).reason
        == "INVALID_PLAN"
    )
