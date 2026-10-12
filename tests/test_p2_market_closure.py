"""Independent P2.4 hand arithmetic, own-step certificates and guarded data assembly."""

import math
from dataclasses import replace

import pandas as pd
import pytest

from lstm_data.clocks import execution_plan
from lstm_data.config import fingerprint
from lstm_data.ft0_tensor import StockTensor, forecast_bridge, join_market
from lstm_data.ft0_transforms import ORDER
from lstm_data.labels import UNIVERSE
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
    observation_reason,
    vector,
    window_from_history,
)
from lstm_data.market_tensor import assemble_market_inputs


def synthetic_market(calendar):
    hours = tuple(
        MarketObservation(
            s.start,
            s.end,
            100.0,
            100.0 * math.exp(0.02),
            s.end,
            "SYNTHETIC",
            f"synthetic-hour:{i}",
            True,
        )
        for i, s in enumerate(calendar.steps)
    )
    closes = {
        day: MarketClose(
            c.close, 100.0 * math.exp(0.01 * i), c.close, "SYNTHETIC", f"synthetic-day:{i}", True
        )
        for i, (day, c) in enumerate(calendar._sessions.items())
        if c.close is not None
    }
    return MarketHistory(calendar, hours, closes, allow_synthetic=True)


def earlier_certificates(history):
    window = MarketFitWindow(
        pd.Timestamp("2020-07-01T04:00Z"),
        pd.Timestamp("2020-07-10T04:00Z"),
        pd.Timestamp("2020-07-10T04:00Z"),
        "INNER_TRAIN",
    )
    rows = tuple(history.measures(s) for s in history.calendar.steps if window.contains(s.end))
    daily = tuple(
        DailyScaleSample(c.period_end, 0.01)
        for c in history.closes.values()
        if window.contains(c.period_end)
    )
    floors = fit_synthetic_floors(rows, daily, window, "synthetic-earlier", allow_synthetic=True)
    vectors = tuple(vector(r, floors, allow_synthetic=True) for r in rows)
    scaler = fit_synthetic_scaler(vectors, window, "synthetic-earlier", allow_synthetic=True)
    return floors, scaler


@pytest.fixture(scope="module")
def market():
    history = synthetic_market(ScheduledCalendar("2019-12-02", "2020-12-01"))
    floors, scaler = earlier_certificates(history)
    return history, floors, scaler


def synthetic_stock(history, day="2020-08-03", origin=1):
    """A tiny upstream tensor assertion; full feature calculation is tested separately."""
    steps = scheduled_window(history.calendar, day, origin)
    values = tuple(tuple(tuple(float(i + k) for k in range(16)) for _ in steps) for i in range(5))
    masks = tuple(tuple((True,) * 16 for _ in steps) for _ in UNIVERSE)
    reasons = tuple(tuple(("SYNTHETIC_VALID",) * 16 for _ in steps) for _ in UNIVERSE)
    lineage = tuple(
        tuple(tuple(f"synthetic:{symbol}:{s.end}:{k}" for k in ORDER) for s in steps)
        for symbol in UNIVERSE
    )
    return StockTensor(
        UNIVERSE,
        steps,
        ORDER,
        values,
        values,
        masks,
        reasons,
        lineage,
        True,
        "synthetic-floor",
        ("synthetic-m2",) * 5,
        "synthetic-scaler",
        "ASOF",
        fingerprint("source"),
        fingerprint("actions"),
        False,
        True,
    )


def test_independent_unequal_scales_absolute_u2_and_ratio_u3():
    w = MarketFitWindow(
        pd.Timestamp("2020-07-01T04:00Z"),
        pd.Timestamp("2020-07-02T04:00Z"),
        pd.Timestamp("2020-07-02T04:00Z"),
        "INNER_TRAIN",
    )
    f = MarketFloors(
        0.005,
        0.005,
        w,
        "SYNTHETIC",
        "synthetic",
        (pd.Timestamp("2020-07-01T14:30Z"),),
        (pd.Timestamp("2020-07-01T20:00Z"),),
    )
    row = MarketMeasures(
        pd.Timestamp("2020-08-03T14:30Z"),
        0.04,
        0.03,
        0.02,
        0.01,
        0.05,
        0.2,
        "OBSERVATION_VALID",
        ("synthetic",),
    )
    assert vector(row, f, allow_synthetic=True, context="ASOF").values == pytest.approx(
        (2.0, math.log(0.02), math.log(1.5), math.sqrt(5), math.sqrt(20))
    )
    assert math.log(0.02) < 0  # Absolute scale in log space is allowed to be negative.


@pytest.mark.parametrize("day", ["2020-08-03", "2020-11-16"])
def test_earlier_certificate_exact_48_by_5_positive_and_ordinary_day(market, day):
    history, floors, scaler = market
    result = window_from_history(
        history, day, 2, floors, scaler, allow_synthetic=True, context="ASOF"
    )
    assert result.values is not None and len(result.values) == 48
    assert all(result.valid_mask) and all(all(mask) for mask in result.cell_mask)
    assert result.application_context == "ASOF" and not result.research_ready
    assert result.scheduled_ends[0] >= floors.window.fitted_at
    assert all(age == 0 for age in result.source_ages_seconds)
    assert len(history.calendar.clock(day).hours) == 6
    assert history.calendar.clock(day).terminal_stub is not None
    expected_hour = 15 if day == "2020-08-03" else 16
    assert result.scheduled_ends[-1].hour == expected_hour


def test_certificates_after_own_step_block_asof_but_not_explicit_retrospective_training(market):
    history, floors, scaler = market
    day = "2020-07-09"
    training = window_from_history(history, day, 2, floors, scaler, allow_synthetic=True)
    causal = window_from_history(
        history, day, 2, floors, scaler, allow_synthetic=True, context="ASOF"
    )
    # Earlier warmup steps precede permitted fitting start and cannot borrow later parameters.
    assert training.values is None and causal.values is None
    step = next(s for s in history.calendar.steps if s.session == day)
    row = history.measures(step)
    assert vector(row, floors, allow_synthetic=True).values is not None
    assert vector(row, floors, allow_synthetic=True, context="ASOF").reason == (
        "MARKET_FLOOR_NOT_AVAILABLE_AT_CUTOFF"
    )
    assert not any(any(mask) for mask in causal.cell_mask)
    assert not join_market(
        synthetic_stock(history, day, 1), history, floors, scaler, origin=1
    ).matched_market_eligible


@pytest.mark.parametrize(
    "field, value",
    [
        ("source_version", "WRONG_SOURCE"),
        ("feature_version", "D7_NEW_FORMULAS"),
        ("action_version", "UNVERIFIED_OTHER_EPOCH"),
        ("hourly", 0.0),
        ("daily", -1.0),
    ],
)
def test_market_certificate_versions_and_positive_scales(market, field, value):
    _, floors, _ = market
    with pytest.raises(ValueError, match="PROVENANCE"):
        replace(floors, **{field: value})


def test_actual_basis_cannot_use_synthetic_fitting_or_application(market):
    history, floors, scaler = market
    step = scheduled_window(history.calendar, "2020-08-03", 1)[-1]
    actual = replace(history.measures(step), basis="DOCUMENTED")
    documented_floors = replace(floors, basis="DOCUMENTED")
    assert vector(history.measures(step), documented_floors, context="ASOF").values is None
    mixed = join_market(
        replace(synthetic_stock(history), synthetic=False),
        history,
        documented_floors,
        replace(scaler, basis="DOCUMENTED"),
        origin=1,
    )
    assert not mixed.matched_market_eligible
    unknown = replace(actual, basis="UNKNOWN")
    assert vector(unknown, replace(floors, basis="DOCUMENTED"), context="ASOF").values is None
    with pytest.raises(ValueError, match="UNKNOWN"):
        MarketVector(step.end, (1.0, 2.0, 3.0, 4.0, 5.0), "VECTOR_VALID", ("unknown",), "UNKNOWN")
    assert vector(actual, floors, allow_synthetic=True, context="ASOF").reason == (
        "SYNTHETIC_FLOOR_REAL_SOURCE_MISMATCH"
    )
    with pytest.raises(ValueError, match="NOT_AUTHORIZED"):
        fit_synthetic_floors((actual,), (), floors.window, "actual", allow_synthetic=True)
    with pytest.raises(ValueError, match="NOT_AUTHORIZED"):
        fit_synthetic_scaler(
            (
                MarketVector(
                    scaler.timestamps[0],
                    (1.0, 2.0, 3.0, 4.0, 5.0),
                    "VECTOR_VALID",
                    ("actual",),
                    "DOCUMENTED",
                ),
            ),
            scaler.window,
            "actual",
            allow_synthetic=True,
        )
    with pytest.raises(ValueError, match="PROVENANCE"):
        replace(scaler, methods=("MAD", "MAD", "MAD", "MAD", "UNAPPROVED_FALLBACK"))
    with pytest.raises(ValueError, match="TRAINING_FIT"):
        replace(floors.window, fitted_at=floors.window.stop - pd.Timedelta(seconds=1))


@pytest.mark.parametrize("minutes, valid", [(90, True), (90.0001, False)])
def test_exact_market_age_boundary(market, minutes, valid):
    row = next(iter(market[0].hours.values()))
    assert (
        observation_reason(
            row, row.period_end + pd.Timedelta(minutes=minutes), allow_synthetic=True
        )
        == "OBSERVATION_VALID"
    ) == valid


def test_early_close_excludes_stub_and_no_240_min_forecast(market):
    history, _, _ = market
    clock = history.calendar.clock("2020-11-27")
    assert len(clock.hours) == 3 and clock.terminal_stub is not None
    assert clock.close == pd.Timestamp("2020-11-27T18:00Z")
    assert clock.close not in history.hours and clock.session in history.closes
    assert all(not execution_plan(clock, origin).calendar_valid for origin in (1, 2))
    assert history.measures(
        next(s for s in history.calendar.steps if s.session == clock.session)
    ).daily_rms63 == pytest.approx(0.01)


def test_data_only_mc0_assembly_and_future_exit_counterfactual(market):
    history, floors, scaler = market
    stock = synthetic_stock(history)
    joined = join_market(stock, history, floors, scaler, origin=1)
    output = assemble_market_inputs(joined)
    assert output.shape == (5, 48, 21) and not output.scientific_ready
    assert output.model_wiring == "NOT_BUILT"
    assert joined.market is not None
    assert output.direct_market is joined.market.values
    assert all(
        row[16:] == output.direct_market[i]
        for rows in output.mc0_values
        for i, row in enumerate(rows)
    )
    assert len(output.market_mask) == 48 and all(len(x) == 5 for x in output.market_mask)
    # A future hourly price/publication and hypothetical future fill cannot be input arguments.
    future = next(
        r
        for r in history.hours.values()
        if r.period_end == stock.steps[-1].end + pd.Timedelta(hours=4)
    )
    changed = replace(
        future, close=future.close * 9, available_at=future.period_end + pd.Timedelta(days=1)
    )
    alternate = MarketHistory(
        history.calendar,
        tuple(changed if r == future else r for r in history.hours.values()),
        history.closes,
        allow_synthetic=True,
    )
    assert assemble_market_inputs(join_market(stock, alternate, floors, scaler, origin=1)) == output
    plan = execution_plan(history.calendar.clock(stock.steps[-1].session), 1)
    assert forecast_bridge(joined.stock, plan) == forecast_bridge(stock, plan)


@pytest.mark.parametrize(
    "kind", ["shifted", "endpoint", "45", "age", "source_only", "training", "source"]
)
def test_assembly_rejects_misalignment_invalid_endpoint_age_and_noncausal_context(market, kind):
    history, floors, scaler = market
    stock = synthetic_stock(history)
    joined = join_market(stock, history, floors, scaler, origin=1)
    window = joined.market
    assert window is not None
    if kind == "shifted":
        shifted = (window.scheduled_ends[0] + pd.Timedelta(minutes=1),)
        window = replace(window, scheduled_ends=shifted + window.scheduled_ends[1:])
    elif kind in {"endpoint", "45"}:
        mask = list(window.valid_mask)
        for i in [-1] if kind == "endpoint" else [0, 1, 2]:
            mask[i] = False
        window = replace(window, valid_mask=tuple(mask))
    elif kind == "age":
        window = replace(window, source_ages_seconds=(5401.0,) + window.source_ages_seconds[1:])
    elif kind == "source_only":
        stock = replace(stock, source_only=True)
    elif kind == "source":
        window = replace(window, source_version="WRONG_SOURCE")
    else:
        stock = replace(stock, application_context="HISTORICAL_TRAINING")
    with pytest.raises(ValueError):
        assemble_market_inputs(replace(joined, stock=stock, market=window))


def test_scaler_availability_is_checked_at_every_own_step(market):
    history, floors, scaler = market
    late = replace(
        scaler.window,
        stop=pd.Timestamp("2020-08-01T04:00Z"),
        fitted_at=pd.Timestamp("2020-08-01T04:00Z"),
    )
    scaler = replace(scaler, window=late)
    retrospective = window_from_history(
        history, "2020-07-31", 1, floors, scaler, allow_synthetic=True
    )
    causal = window_from_history(
        history, "2020-07-31", 1, floors, scaler, allow_synthetic=True, context="ASOF"
    )
    assert retrospective.values is not None
    assert causal.values is None and causal.reason == "MARKET_SCALER_NOT_AVAILABLE_AT_CUTOFF"
    assert not any(any(row) for row in causal.cell_mask)


def test_46_valid_assembly_uses_only_standardized_neutral_zero_and_separate_mask(market):
    history, floors, scaler = market
    joined = join_market(synthetic_stock(history), history, floors, scaler, origin=1)
    window = joined.market
    assert window is not None and window.values is not None
    two_missing = replace(
        window,
        valid_mask=(False, False) + window.valid_mask[2:],
        values=((0.0,) * 5,) * 2 + window.values[2:],
    )
    output = assemble_market_inputs(replace(joined, market=two_missing))
    assert sum(all(row) for row in output.market_mask) == 46
    assert output.mc0_values[0][0][16:] == (0.0,) * 5
    assert output.mc0_values[0][0][:16] == joined.stock.values[0][0]


def test_scaler_validation_timestamp_and_malformed_numeric_values_rejected(market):
    _, floors, scaler = market
    validation = MarketVector(
        floors.window.stop, (1.0, 2.0, 3.0, 4.0, 5.0), "VECTOR_VALID", ("synthetic-validation",)
    )
    with pytest.raises(ValueError, match="TRAINING_MARKET"):
        fit_synthetic_scaler((validation,), floors.window, "synthetic", allow_synthetic=True)
    with pytest.raises(ValueError, match="FINITE"):
        scaler.transform((float("nan"), 2.0, 3.0, 4.0, 5.0))
    # U1 is constant in this fixture and maps to zero; U2 has an audited SD scale.
    assert scaler.methods[1] != "CONSTANT"
    tiny = replace(scaler, scales=(scaler.scales[0], 5e-324) + scaler.scales[2:])
    with pytest.raises(ValueError, match="NORMALIZED"):
        tiny.transform((1.0, 1e308, 3.0, 4.0, 5.0))
