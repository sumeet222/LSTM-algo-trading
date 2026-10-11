import math
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from test_market_source import coarse

from lstm_data.m2 import ScheduledCalendar, scheduled_window
from lstm_data.market_features import (
    DailyScaleSample,
    MarketClose,
    MarketFitWindow,
    MarketFloors,
    MarketHistory,
    MarketMeasures,
    MarketObservation,
    MarketVector,
    fit_synthetic_floors,
    fit_synthetic_scaler,
    history_from_archive,
    observation_reason,
    rms,
    standardized_window,
    vector,
    window_from_history,
)
from lstm_data.market_source import hourly_archive


@pytest.fixture
def history():
    cal = ScheduledCalendar("2019-12-01", "2020-09-01")
    hours = tuple(MarketObservation(s.start, s.end, 100., 100. * math.exp(.02),
                                   s.end, "SYNTHETIC", f"h-{i}", True)
                  for i, s in enumerate(cal.steps))
    closes = {}
    for i, (day, clock) in enumerate(cal._sessions.items()):
        if clock.close is None:
            raise ValueError("Synthetic XNYS fixture requires a valid close")
        closes[day] = MarketClose(clock.close, 100. * math.exp(.01 * i), clock.close,
                                 "SYNTHETIC", f"d-{i}", True)
    return MarketHistory(cal, hours, closes, allow_synthetic=True)


def fit_window():
    return MarketFitWindow(pd.Timestamp("2020-07-01", tz="America/New_York"),
                           pd.Timestamp("2020-08-01", tz="America/New_York"),
                           pd.Timestamp("2020-08-01", tz="America/New_York"), "INNER_TRAIN")


def floor():
    w = fit_window()
    return MarketFloors(.005, .005, w, "SYNTHETIC", "synthetic-p05",
                        (pd.Timestamp("2020-07-01T14:30Z"),),
                        (pd.Timestamp("2020-07-01T20:00Z"),))


def test_hand_computed_u1_u5_and_daily_lock(history):
    steps = [s for s in history.calendar.steps if s.session == "2020-07-01"]
    measures = [history.measures(s) for s in steps]
    for m in measures:
        assert m.rms12 == pytest.approx(.02)
        assert m.rms60 == pytest.approx(.02)
        assert m.daily_rms63 == pytest.approx(.01)
        v = vector(m, floor(), allow_synthetic=True)
        assert v.values == pytest.approx((1., math.log(.02), 0., math.sqrt(5), math.sqrt(20)))
        assert m.evidence_ids
    assert len({m.momentum5 for m in measures}) == 1
    changed = dict(history.closes)
    changed[steps[0].session] = replace(changed[steps[0].session], close=9999.)
    altered = MarketHistory(history.calendar, tuple(history.hours.values()), changed,
                            allow_synthetic=True)
    assert altered.measures(steps[0]) == measures[0]  # current-day/future close is not read


def test_composed_positive_48_by_five_window_and_certificate_holds(history):
    w = fit_window()
    steps = tuple(s for s in history.calendar.steps if w.contains(s.end))
    measures = tuple(history.measures(s) for s in steps)
    daily = tuple(DailyScaleSample(c.period_end, .01) for c in history.closes.values()
                  if w.contains(c.period_end))
    floors = fit_synthetic_floors(measures, daily, w, "synthetic-composition",
                                  allow_synthetic=True)
    vectors = tuple(vector(m, floors, allow_synthetic=True) for m in measures)
    scaler = fit_synthetic_scaler(vectors, w, "synthetic-composition", allow_synthetic=True)
    output = window_from_history(history, "2020-07-30", 2, floors, scaler, allow_synthetic=True)
    assert output.values is not None and len(output.values) == 48
    assert all(len(v) == 5 for v in output.values) and all(output.valid_mask)
    assert len(output.scheduled_ends) == len(output.source_ids) == len(output.step_reasons) == 48
    assert output.floor_ref == output.scaler_ref == "synthetic-composition"
    assert not output.research_ready
    assert window_from_history(history, "2020-07-30", 2).reason == \
        "MARKET_FLOOR_CERTIFICATE_REQUIRED"
    assert window_from_history(history, "2020-07-30", 2, floors).reason == \
        "MARKET_SCALER_CERTIFICATE_REQUIRED"
    assert window_from_history(history, "2020-07-30", 2, floors, scaler).values is None


@pytest.mark.parametrize("count,minimum,missing,expected", [
    (12, 12, (), True), (12, 12, (1,), False),
    (60, 57, (1, 2, 4), True), (60, 57, (1, 2, 3), False),
    (60, 57, (1, 3, 5, 7), False), (63, 60, (2, 4, 6), True),
    (63, 60, (2, 3, 4), False), (63, 60, (1, 3, 5, 7), False),
])
def test_rms_scheduled_thresholds(count, minimum, missing, expected):
    data = tuple(None if i in missing else .02 for i in range(count))
    result = rms(data, count, minimum)
    assert (result is not None) == expected
    if expected:
        assert result == pytest.approx(.02)


def test_gap_does_not_shift_and_momentum_chain_is_complete(history):
    step = next(s for s in history.calendar.steps if s.session == "2020-07-01")
    position = history.calendar.steps.index(step)
    missing = history.calendar.steps[position - 1].end
    hours = tuple(r for r in history.hours.values() if r.period_end != missing)
    changed = MarketHistory(history.calendar, hours, history.closes, allow_synthetic=True)
    assert changed.measures(step).rms12 is None
    assert changed.measures(step).rms60 == pytest.approx(.02)
    closes = dict(history.closes)
    del closes[history.days[history.days.index(step.session) - 2]]
    changed = MarketHistory(history.calendar, tuple(history.hours.values()), closes,
                            allow_synthetic=True)
    m = changed.measures(step)
    assert m.daily_rms63 == pytest.approx(.01)  # two adjacent daily returns missing, allowed
    assert m.momentum5 is None and m.momentum20 is None
    assert vector(m, floor(), allow_synthetic=True).values is None


@pytest.mark.parametrize("kind,reason", [
    ("unknown", "PUBLICATION_UNKNOWN"), ("late", "FUTURE_OR_LATE_PUBLICATION"),
    ("stale", "STALE_MARKET_STATE"), ("split", "SPLIT_SCOPE_UNVERIFIED"),
])
def test_source_clock_rejections(history, kind, reason):
    row = next(iter(history.hours.values()))
    cutoff = row.period_end
    if kind == "unknown":
        row = replace(row, available_at=None, basis="UNKNOWN")
    elif kind == "late":
        row = replace(row, available_at=row.period_end + pd.Timedelta(seconds=1))
    elif kind == "stale":
        cutoff += pd.Timedelta(minutes=91)
    else:
        row = replace(row, splits_verified=False)
    assert observation_reason(row, cutoff, allow_synthetic=True) == reason


def test_unknown_archive_is_actual_feature_adapter_blocked():
    hours, _ = hourly_archive(coarse(), "2020-07-01", "2020-07-01")
    cal = ScheduledCalendar("2020-07-01", "2020-07-01")
    h = history_from_archive(cal, hours)
    assert h.measures(cal.steps[0]).reason == "PUBLICATION_UNKNOWN"
    assert vector(h.measures(cal.steps[0]), floor(), allow_synthetic=True).values is None
    assert len(h.hours) == 6 and len(h.closes) == 1


def test_late_hour_and_prior_daily_close_cannot_enter_history(history):
    step = next(s for s in history.calendar.steps if s.session == "2020-07-01")
    hours = tuple(replace(r, available_at=r.period_end + pd.Timedelta(seconds=1))
                  if r.period_end == step.end else r for r in history.hours.values())
    closes = dict(history.closes)
    day = history.days[history.days.index(step.session) - 1]
    closes[day] = replace(closes[day], available_at=step.end + pd.Timedelta(seconds=1))
    h = MarketHistory(history.calendar, hours, closes, allow_synthetic=True)
    assert h.measures(step).reason == "FUTURE_OR_LATE_PUBLICATION"
    assert h.measures(step).momentum5 is None


def test_training_positive_p05_unique_daily_times_and_no_empirical_fitting():
    w = fit_window()
    times = tuple(pd.Timestamp(f"2020-07-0{i}T20:00Z") for i in (1, 2, 6))
    rows = tuple(MarketMeasures(t, .02, a, b, .01, .05, .2,
                               "OBSERVATION_VALID", ("synthetic",))
                 for t, a, b in zip(times, (.01, .02, .03), (.02, .03, .04)))
    daily = tuple(DailyScaleSample(t, x) for t, x in zip(times, (.01, .02, .03)))
    f = fit_synthetic_floors(rows, daily, w, "synthetic", allow_synthetic=True)
    assert f.hourly == pytest.approx(float(np.percentile([.01, .02, .03, .02, .03, .04], 5)))
    assert f.daily == pytest.approx(.011)
    with pytest.raises(ValueError, match="NOT_AUTHORIZED"):
        fit_synthetic_floors(rows, daily, w, "synthetic")
    with pytest.raises(ValueError, match="UNIQUE_TRAINING_DAILY"):
        fit_synthetic_floors(rows, daily * 2, w, "synthetic", allow_synthetic=True)
    with pytest.raises(ValueError, match="UNIQUE_TRAINING"):
        fit_synthetic_floors(rows + (replace(rows[0], timestamp=w.stop),), daily,
                             w, "synthetic", allow_synthetic=True)
    with pytest.raises(ValueError, match="INSUFFICIENT"):
        fit_synthetic_floors(tuple(replace(r, rms12=0., rms60=0.) for r in rows), daily,
                             w, "synthetic", allow_synthetic=True)


@pytest.mark.parametrize("stop,phase", [("2023-07-02", "INNER_TRAIN"),
                                       ("2024-07-02", "REFIT")])
def test_fit_may_not_cross_training_prefix(stop, phase):
    # Parametrized phase intentionally exercises runtime validation of the public contract.
    with pytest.raises(ValueError, match="TRAINING_FIT"):
        MarketFitWindow(pd.Timestamp("2020-07-01T04:00Z"), pd.Timestamp(stop, tz="UTC"),
                        pd.Timestamp("2025-01-01T00:00Z"), phase)


def scaler_rows():
    # Channel 0 MAD, 1 IQR, 2 SD (one tail), 3 constant, 4 MAD.
    return tuple(MarketVector(pd.Timestamp("2020-07-01T14:30Z") + pd.Timedelta(minutes=i),
                              (float(i), 1. if i < 6 else 3., 10. if i == 9 else 0.,
                               7., float(i * 2)), "VECTOR_VALID", ("synthetic",))
                 for i in range(10))


def test_unique_timestamp_scaler_fallbacks_constant_and_no_clipping():
    rows = scaler_rows()
    scaler = fit_synthetic_scaler(rows * 5, fit_window(), "synthetic", allow_synthetic=True)
    assert len(scaler.timestamps) == 10
    assert scaler.methods == ("MAD", "IQR_1.349", "AUDITED_POPULATION_SD", "CONSTANT", "MAD")
    values, novel = scaler.transform((1e9, 1., 0., 8., 1e9))
    assert values[0] > 1e6 and values[3] == 0. and novel == (3,)
    with pytest.raises(ValueError, match="CONFLICTING"):
        fit_synthetic_scaler(rows + (replace(rows[0], values=(1., 1., 0., 7., 0.)),),
                             fit_window(), "synthetic", allow_synthetic=True)
    with pytest.raises(ValueError, match="NOT_AUTHORIZED"):
        fit_synthetic_scaler(rows, fit_window(), "synthetic")


@pytest.mark.parametrize("missing,endpoint,valid", [(0, True, True), (2, True, True),
                                                   (3, True, False), (1, False, False)])
def test_48_by_5_endpoint_46_threshold_neutral_masks(history, missing, endpoint, valid):
    steps = scheduled_window(history.calendar, "2020-07-31", 1)
    rows = tuple(MarketVector(s.end, (1., 2., 3., 4., 5.), "VECTOR_VALID", ("synthetic",))
                 for s in steps)
    changed = list(rows)
    for i in range(missing):
        changed[i] = replace(changed[i], values=None, reason="MISSING_SPY_SOURCE")
    if not endpoint:
        changed[-1] = replace(changed[-1], values=None, reason="PUBLICATION_UNKNOWN")
    scaler = fit_synthetic_scaler(scaler_rows(), fit_window(), "synthetic", allow_synthetic=True)
    result = standardized_window(steps, tuple(changed), scaler, calendar=history.calendar,
                                 allow_synthetic=True)
    assert (result.values is not None) == valid
    assert not result.research_ready
    assert len(result.valid_mask) == 48
    if result.values is not None:
        assert len(result.values) == 48 and all(len(x) == 5 for x in result.values)
        assert all(x == (0., 0., 0., 0., 0.) for x in result.values[:missing])
    assert standardized_window(steps, rows, scaler, calendar=history.calendar).values is None


def test_duplicate_hours_stubs_and_invented_publication_rejected(history):
    row = next(iter(history.hours.values()))
    with pytest.raises(ValueError, match="DUPLICATE_MARKET"):
        MarketHistory(history.calendar, (row, row), history.closes)
    with pytest.raises(ValueError, match="COMPLETE_SESSION_GRID"):
        MarketHistory(history.calendar, (replace(row, period_start=row.period_end
                      - pd.Timedelta(minutes=30)),), history.closes)
    with pytest.raises(ValueError, match="BEFORE_COMPLETION"):
        replace(row, available_at=row.period_start)


def test_future_floor_information_cutoff_blocks(history):
    step = next(s for s in history.calendar.steps if s.session == "2020-08-03")
    w = replace(fit_window(), fitted_at=pd.Timestamp("2020-08-04T00:00Z"))
    f = replace(floor(), window=w)
    assert vector(history.measures(step), f, allow_synthetic=True).reason == (
        "MARKET_FLOOR_NOT_AVAILABLE_AT_CUTOFF")


def test_no_sixth_channel_or_gap_compression(history):
    valid = MarketVector(pd.Timestamp("2020-07-01T14:30Z"),
                         (1., 2., 3., 4., 5.), "VECTOR_VALID", ())
    with pytest.raises(ValueError, match="FIVE_FINITE"):
        # dataclass replacement exercises malformed external data and invokes the
        # real constructor validation; no false static Vector annotation or ignore.
        replace(valid, values=tuple(range(6)))
    steps = scheduled_window(history.calendar, "2020-07-31", 1)
    first = history.calendar.steps.index(steps[0])
    shifted = (history.calendar.steps[first - 1],) + steps[1:]
    rows = tuple(MarketVector(s.end, (1., 2., 3., 4., 5.), "VECTOR_VALID", ("synthetic",))
                 for s in shifted)
    scaler = fit_synthetic_scaler(scaler_rows(), fit_window(), "synthetic", allow_synthetic=True)
    with pytest.raises(ValueError, match="CONSECUTIVE"):
        standardized_window(shifted, rows, scaler, calendar=history.calendar,
                            allow_synthetic=True)
