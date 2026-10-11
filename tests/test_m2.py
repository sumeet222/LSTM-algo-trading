"""Independent P2.3A synthetic arithmetic/grid/as-of tests; no source prices."""

import math
from dataclasses import replace
from typing import cast

import pandas as pd
import pytest

from lstm_data.clocks import execution_plan
from lstm_data.hourly_proxy import HourlyCloseReference
from lstm_data.labels import UNIVERSE, ActionScope, FitWindow, SplitFact
from lstm_data.m2 import (
    M2FloorCertificate,
    ReturnIndex,
    ScheduledCalendar,
    canonical_m2_keys,
    evaluate_m2,
    historical_return,
    scheduled_window,
    window_quality,
)


@pytest.fixture(scope="module")
def calendar():
    return ScheduledCalendar("2020-07-01", "2021-04-01")


def one_return(
    calendar, day, value, symbol="AAPL", origin=1, *, delay=None, basis="SYNTHETIC", split=False
):
    plan = execution_plan(calendar.clock(day), origin)
    entry = HourlyCloseReference(
        symbol,
        f"{symbol}:{day}:{origin}:entry",
        # The fixture selects complete normal-session plans; post-init normalizes rows.
        cast(pd.Timestamp, plan.cutoff) - pd.Timedelta(hours=1),
        cast(pd.Timestamp, plan.cutoff),
        100.0,
        "fake-raw-v1",
        "SYNTHETIC",
        plan.cutoff,
        "SYNTHETIC",
    )
    exit = replace(
        entry,
        row_id=entry.row_id.replace("entry", "exit"),
        period_start=cast(pd.Timestamp, entry.period_start) + pd.Timedelta(hours=4),
        period_end=cast(pd.Timestamp, entry.period_end) + pd.Timedelta(hours=4),
        available_at=delay or cast(pd.Timestamp, plan.cutoff) + pd.Timedelta(hours=4),
        availability_basis=basis,
        raw_close=100 * math.exp(value) / (2 if split else 1),
    )
    actions = ActionScope(
        cast(pd.Timestamp, plan.cutoff),
        cast(pd.Timestamp, plan.exit),
        UNIVERSE,
        "SYNTHETIC",
        "fake-complete-scope",
        (SplitFact(
            symbol, cast(pd.Timestamp, plan.cutoff) + pd.Timedelta(minutes=1),
            2, 1, "fake-split", "SYNTHETIC",
        ),)
        if split
        else (),
    )
    return historical_return(plan, symbol, (entry, exit), actions, test_scenario=True)


@pytest.fixture(scope="module")
def history(calendar):
    step = scheduled_window(calendar, "2021-03-15", 1)[-1]
    days = calendar.previous_origins(step, 1)[-60:]
    return tuple(one_return(calendar, d, (i + 1) * 0.001) for i, d in enumerate(days))


@pytest.fixture
def floor():
    window = FitWindow(
        "synthetic-prefix",
        pd.Timestamp("2020-07-01T04:00Z"),
        pd.Timestamp("2020-07-03T04:00Z"),
        pd.Timestamp("2020-07-03T04:00Z"),
        "INNER_TRAIN",
    )
    return M2FloorCertificate(
        0.0001, window, (("AAPL", "2020-07-01", 1),), "fake-positive-p05", "SYNTHETIC"
    )


def calc(calendar, history, floor, *, origin=1, symbol="AAPL", step=None):
    return evaluate_m2(
        calendar,
        ReturnIndex(tuple(history)),
        symbol,
        step or scheduled_window(calendar, "2021-03-15", 1)[-1],
        origin,
        floor,
        test_scenario=True,
    )


def test_exact_grid_dst_and_early_close(calendar):
    steps = scheduled_window(calendar, "2021-03-15", 1)
    assert len(steps) == 48
    assert (steps[0].session, steps[0].slot) == ("2021-03-03", 2)
    assert (steps[-1].session, steps[-1].slot) == ("2021-03-15", 1)
    assert steps[-2].end == pd.Timestamp("2021-03-12T20:30Z")
    assert steps[-1].end == pd.Timestamp("2021-03-15T14:30Z")
    short = calendar.clock("2020-11-27")
    assert len(
        short.hours
    ) == 3 and short.terminal_stub.end - short.terminal_stub.start == pd.Timedelta(minutes=30)
    before = scheduled_window(calendar, "2020-11-30", 1)
    assert [(x.session, x.slot) for x in before[-4:-1]] == [("2020-11-27", i) for i in (1, 2, 3)]
    with pytest.raises(ValueError, match="STRUCTURALLY"):
        scheduled_window(calendar, "2020-11-27", 1)
    with pytest.raises(ValueError, match="INSUFFICIENT"):
        scheduled_window(calendar, "2020-07-01", 1)


def test_independent_mean20_rms60_and_shuffle(calendar, history, floor):
    out = calc(calendar, history, floor)
    expected_mean = 0.001 * sum(range(41, 61)) / 20
    expected_rms = 0.001 * math.sqrt(sum(i * i for i in range(1, 61)) / 60)
    assert out.mean20 == pytest.approx(expected_mean)
    assert out.rms60 == pytest.approx(expected_rms)
    assert out.value == pytest.approx(expected_mean / expected_rms)
    assert out == calc(calendar, tuple(reversed(history)), floor)
    assert (out.valid20, out.valid60, out.max_missing_run) == (20, 60, 0)
    assert not out.research_ready


def test_origin_and_stock_isolation(calendar, history, floor):
    b = one_return(calendar, history[-1].plan.session, 0.8, "JPM", 2)
    assert calc(calendar, history + (b,), floor) == calc(calendar, history, floor)
    assert calc(calendar, history, floor, origin=2).valid60 == 0
    assert calc(calendar, history + (b,), floor, origin=2, symbol="JPM").valid60 == 1
    assert calc(calendar, history, floor, symbol="JPM").valid60 == 0
    assert calc(calendar, (), floor).reason == "RETURN_COVERAGE_BLOCKED"


@pytest.mark.parametrize(
    "positions,valid20,valid60,run,valid",
    [
        ((59,), 19, 59, 1, True),
        ((58, 59), 18, 58, 2, False),
        ((0, 10, 20), 20, 57, 1, True),
        ((0, 10, 20, 30), 20, 56, 1, False),
        ((0, 1), 20, 58, 2, True),
        ((0, 1, 2), 20, 57, 3, False),
    ],
)
def test_scheduled_missing_counts_and_runs(
    calendar, history, floor, positions, valid20, valid60, run, valid
):
    remaining = tuple(r for i, r in enumerate(history) if i not in positions)
    out = calc(calendar, remaining, floor)
    assert (out.valid20, out.valid60, out.max_missing_run) == (valid20, valid60, run)
    assert (out.reason == "M2_VALID") == valid
    if valid:
        nums = [(i + 1) * 0.001 for i in range(40, 60) if i not in positions]
        dens = [(i + 1) * 0.001 for i in range(60) if i not in positions]
        assert out.value == pytest.approx(
            (sum(nums) / len(nums)) / math.sqrt(sum(x * x for x in dens) / len(dens))
        )


def test_zero_rms_and_no_unapproved_constant(calendar, history, floor):
    zero = tuple(replace(r, value=0.0) for r in history)
    out = calc(calendar, zero, floor)
    assert out.value == 0 and out.rms60 == 0 and out.floor_id == floor.floor_id
    assert calc(calendar, zero, None).reason == "FLOOR_UNVERIFIED"
    tiny = tuple(replace(r, value=0.00001) for r in history)
    assert calc(calendar, tiny, floor).value == pytest.approx(0.1)


def test_maturity_counterfactual_and_unknown_clock(calendar, history, floor):
    step = scheduled_window(calendar, "2021-03-15", 1)[-1]
    late = one_return(
        calendar, history[-1].plan.session, 0.06, delay=step.end + pd.Timedelta(minutes=1)
    )
    out = calc(calendar, history[:-1] + (late,), floor)
    assert out.valid20 == 19 and out.missing_reasons[-1] == "NOT_MATURED_AT_STEP"
    absent = calc(calendar, history[:-1], floor)
    assert out.value == absent.value and out.reference_ids == absent.reference_ids
    unknown = one_return(calendar, history[-1].plan.session, 0.06, basis="UNKNOWN")
    assert unknown.maturity is None and unknown.reason == "SOURCE_CLOCK_BLOCKED"
    assert calc(calendar, history[:-1] + (unknown,), floor).value == absent.value
    future = one_return(calendar, "2021-03-16", 2.0)
    assert calc(calendar, history + (future,), floor) == calc(calendar, history, floor)
    early = scheduled_window(calendar, "2021-03-12", 1)[-1]
    early_out = calc(calendar, history, floor, step=early)
    assert history[-1].plan.session not in early_out.sessions
    assert early_out == calc(calendar, history[:-1], floor, step=early)


def test_split_lineage_and_unsupported_epoch(calendar):
    normal = one_return(calendar, "2021-03-12", math.log(1.02))
    split = one_return(calendar, "2021-03-12", math.log(1.02), split=True)
    assert split.value == pytest.approx(math.log(1.02))
    assert split.action_ids == ("fake-split",) and split.lineage_id != normal.lineage_id
    assert replace(split, value=0.0).lineage_id != split.lineage_id
    plan = split.plan
    row = HourlyCloseReference(
        "AAPL",
        "fake",
        cast(pd.Timestamp, plan.cutoff) - pd.Timedelta(hours=1),
        cast(pd.Timestamp, plan.cutoff),
        100.0,
        "fake",
        "SYNTHETIC",
        plan.cutoff,
        "SYNTHETIC",
    )
    exit = replace(
        row,
        row_id="fake-exit",
        period_start=cast(pd.Timestamp, row.period_start) + pd.Timedelta(hours=4),
        period_end=cast(pd.Timestamp, row.period_end) + pd.Timedelta(hours=4),
        available_at=cast(pd.Timestamp, row.available_at) + pd.Timedelta(hours=4),
    )
    unsupported = ActionScope(
        cast(pd.Timestamp, plan.cutoff), cast(pd.Timestamp, plan.exit),
        UNIVERSE, "SYNTHETIC", "fake", unsupported_action=True,
    )
    assert (
        historical_return(plan, "AAPL", (row, exit), unsupported, test_scenario=True).reason
        == "ACTION_CONVENTION_UNVERIFIED"
    )
    invalid = replace(plan, cutoff=None)
    assert (
        historical_return(invalid, "AAPL", (row, exit), unsupported, test_scenario=True).reason
        == "INVALID_PLAN"
    )
    changed = replace(exit, source_version="fake-new")
    supported = replace(unsupported, unsupported_action=False)
    missing_clock = replace(exit, available_at=pd.NaT)
    assert (
        historical_return(plan, "AAPL", (row, missing_clock), supported, test_scenario=True).reason
        == "SOURCE_CLOCK_BLOCKED"
    )
    with pytest.raises(ValueError, match="timezone-aware"):
        replace(row, available_at="2021-03-12T15:30")
    assert (
        historical_return(plan, "AAPL", (row, exit), supported, test_scenario=True).lineage_id
        != historical_return(plan, "AAPL", (row, changed), supported, test_scenario=True).lineage_id
    )


def test_canonical_keys_deduplicate_and_balance(calendar, history, floor):
    out = calc(calendar, history, floor)
    other = replace(out, key=("AAPL", out.key[1], 2))
    weights = canonical_m2_keys((out, other, out))
    assert weights == ((out.key, 0.5), (other.key, 0.5))
    with pytest.raises(ValueError, match="CONFLICTING"):
        # calc's complete history produces M2_VALID with a numeric value.
        canonical_m2_keys((out, replace(out, value=cast(float, out.value) + 1), other))
    with pytest.raises(ValueError, match="BOTH_ORIGIN"):
        canonical_m2_keys((out,))


def test_window_mask_missing_never_shifts_and_no_future_label_filter(calendar, history, floor):
    steps = scheduled_window(calendar, "2021-03-15", 1)
    rows = tuple(
        HourlyCloseReference(
            s, f"{s}:{i}", x.start, x.end, 100.0, "fake-raw", "SYNTHETIC", x.end, "SYNTHETIC"
        )
        for s in UNIVERSE
        for i, x in enumerate(steps)
    )
    complete = window_quality(calendar, steps, rows, test_scenario=True)
    assert complete.raw_window_eligible and not complete.full_ft0_eligible
    missing = window_quality(
        calendar, steps, tuple(r for r in rows if r.row_id != "JNJ:24"), test_scenario=True
    )
    assert sum(sum(x) for x in missing.mask) == 239
    assert missing.steps == complete.steps and missing.reasons[2][24] == "SOURCE_MISSING"
    # Re-evaluate input eligibility after modifying only an unobserved future exit.
    future = one_return(calendar, "2021-03-16", 0.8)
    calc(calendar, history + (future,), floor)
    assert window_quality(calendar, steps, rows, test_scenario=True) == complete
    late = tuple(
        replace(r, available_at=cast(pd.Timestamp, r.period_end) + pd.Timedelta(minutes=1))
        if r.row_id == "AAPL:47"
        else r
        for r in rows
    )
    assert (
        window_quality(calendar, steps, late, test_scenario=True).reasons[0][-1]
        == "NOT_AVAILABLE_AT_STEP"
    )
    with pytest.raises(ValueError, match="DUPLICATE"):
        window_quality(calendar, steps, rows + (rows[0],), test_scenario=True)
    with pytest.raises(ValueError, match="NONCONSECUTIVE"):
        window_quality(calendar, steps[:-1] + (steps[0],), rows, test_scenario=True)


def test_version_keys_timestamps_and_future_floor_fail_closed(calendar, history, floor):
    with pytest.raises(ValueError, match="VERSION"):
        ReturnIndex((replace(history[0], execution_version="MINUTE_OPEN"),))
    with pytest.raises(ValueError, match="DUPLICATE"):
        ReturnIndex((history[0], history[0]))
    for bad in ("2021-03-12T10:00", pd.NaT):
        with pytest.raises(ValueError, match="finite|aware"):
            replace(history[0], maturity=bad)
    with pytest.raises(ValueError, match="BEFORE"):
        replace(history[0], maturity=history[0].plan.cutoff)
    with pytest.raises(ValueError, match="INVALID_RETURN_PLAN"):
        replace(
            history[0],
            plan=replace(history[0].plan, cutoff=history[0].plan.cutoff + pd.Timedelta(minutes=1)),
        )
    with pytest.raises(ValueError, match="TRAINING"):
        replace(floor, window=replace(floor.window, start=pd.Timestamp("2019-01-01T05:00Z")))
    assert replace(floor, window=replace(floor.window, phase="REFIT")).epsilon == floor.epsilon
    with pytest.raises(ValueError, match="CERTIFICATE"):
        calc(calendar, history, object())
    for invalid in (0.0, -1.0, float("nan"), float("inf")):
        with pytest.raises(ValueError, match="POSITIVE"):
            replace(floor, epsilon=invalid)
    with pytest.raises(ValueError, match="TRAINING"):
        replace(floor, window=replace(floor.window, phase="INNER_VALIDATION"))
    with pytest.raises(ValueError, match="TRAINING"):
        replace(floor, window=replace(floor.window, stop=pd.Timestamp("2025-06-30T00:00Z")))
    with pytest.raises(ValueError, match="OUTSIDE"):
        replace(floor, fitting_keys=(("AAPL", "2024-07-02", 1),))
    with pytest.raises(ValueError, match="UNIQUE"):
        replace(floor, fitting_keys=floor.fitting_keys * 2)
    future = replace(
        floor, window=replace(floor.window, fitted_at=pd.Timestamp("2021-03-16T00:00Z"))
    )
    assert calc(calendar, history, future).reason == "FLOOR_NOT_AVAILABLE_AT_STEP"
    out = evaluate_m2(
        calendar,
        ReturnIndex(history),
        "AAPL",
        scheduled_window(calendar, "2021-03-15", 1)[-1],
        1,
        floor,
    )
    assert out.value is None and out.valid60 == 0
    with pytest.raises(ValueError, match="HISTORICAL_STEP"):
        calc(
            calendar,
            history,
            floor,
            step=replace(out.step, end=out.step.end - pd.Timedelta(minutes=1)),
        )
    with pytest.raises(ValueError, match="CANONICAL_SESSION"):
        canonical_m2_keys((replace(out, key=("AAPL", "NaT", 1)),))
