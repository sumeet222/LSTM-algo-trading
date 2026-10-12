"""Independent analytic FT0 cases and timing/state boundaries, explicitly synthetic."""

import math
from dataclasses import replace

import pandas as pd
import pytest

from lstm_data.clocks import execution_plan
from lstm_data.config import fingerprint
from lstm_data.ft0_tensor import fitting_observations, forecast_bridge, join_market, stock_window
from lstm_data.ft0_transforms import (
    ORDER,
    FitObservation,
    fit_floors,
    fit_scaler,
)
from lstm_data.labels import UNIVERSE, FitWindow
from lstm_data.m2 import HistoricalReturn, M2FloorCertificate, ReturnIndex
from lstm_data.stock_features import FeatureCalculator, IndicatorState
from lstm_data.stock_source import StockBar, StockCalendar, StockHistory


@pytest.fixture(scope="module")
def engine():
    calendar = StockCalendar("2019-01-02", "2020-10-15")
    bars = []
    for di, (day, clock) in enumerate(calendar._sessions.items()):
        intervals = [(slot, h) for slot, h in enumerate(clock.hours, 1)]
        if clock.terminal_stub is not None:
            intervals.append((0, clock.terminal_stub))
        for si, symbol in enumerate(UNIVERSE):
            for slot, h in intervals:
                close = (
                    100.0 * (1 + si / 10) * math.exp(0.001 * di + 0.002 * (slot - 1 if slot else 5))
                )
                bars.append(
                    StockBar(
                        symbol,
                        day,
                        slot,
                        h.start,
                        h.end,
                        close * math.exp(-0.01),
                        close * 1.02,
                        close * math.exp(-0.01) * 0.99,
                        close,
                        100.0 * (slot + 1 if slot else 0.5) * (1 + 0.001 * di),
                        (f"synthetic:{symbol}:{day}:{slot}",),
                        available_at=h.end,
                        basis="SYNTHETIC",
                        action_verified=True,
                        action_ref="synthetic-common-epoch",
                        evidence_ref="synthetic-publication",
                    )
                )
    history = StockHistory(calendar, tuple(bars), synthetic=True)
    returns = []
    for day, clock in calendar._sessions.items():
        if day < "2020-04-01":
            continue
        for origin in (1, 2):
            plan = execution_plan(clock, origin)
            if not plan.calendar_valid:
                continue
            for symbol in UNIVERSE:
                entry, exit = (
                    history.bars[symbol, day, origin],
                    history.bars[symbol, day, origin + 4],
                )
                returns.append(
                    HistoricalReturn(
                        plan,
                        symbol,
                        0.008,
                        plan.exit,
                        "RETURN_VALID",
                        (entry.row_id, exit.row_id),
                        (),
                        fingerprint([day, symbol, origin]),
                        True,
                    )
                )
    return FeatureCalculator(history, ReturnIndex(tuple(returns)))


def july_m2_floors():
    window = FitWindow(
        "synthetic",
        pd.Timestamp("2020-07-01T04:00Z"),
        pd.Timestamp("2020-07-02T04:00Z"),
        pd.Timestamp("2020-07-02T04:00Z"),
        "INNER_TRAIN",
    )
    return tuple(
        M2FloorCertificate(
            0.008,
            window,
            ((symbol, "2020-07-01", 1), (symbol, "2020-07-01", 2)),
            "EXPLICIT_SYNTHETIC_CONSTANT_RMS_P05",
            "SYNTHETIC",
        )
        for symbol in UNIVERSE
    )


@pytest.fixture(scope="module")
def parameters(engine):
    window = FitWindow(
        "SYNTHETIC:INNER_TRAIN",
        pd.Timestamp("2020-08-01T04:00Z"),
        pd.Timestamp("2020-09-01T04:00Z"),
        pd.Timestamp("2020-09-01T04:00Z"),
        "INNER_TRAIN",
    )
    records = []
    for symbol in UNIVERSE:
        for step in engine.history.calendar.steps:
            if not window.start <= step.end < window.stop:
                continue
            comp = engine.components(symbol, step)
            for kind in ("RMS12", "RMS60", "VOLUME_H"):
                value = comp.values[kind]
                if value is not None:
                    records.append(
                        FitObservation(
                            symbol,
                            step.end,
                            kind,
                            (symbol, step.session, step.slot),
                            value,
                            comp.lineage_id,
                            engine.history.binding,
                            engine.history.action_binding,
                            "SYNTHETIC",
                            step.end,
                        )
                    )
            if step.slot == 1:
                value = comp.values["RMS63"]
                if value is not None:
                    records.append(
                        FitObservation(
                            symbol,
                            step.end,
                            "RMS63",
                            (symbol, step.session, 0),
                            value,
                            comp.lineage_id,
                            engine.history.binding,
                            engine.history.action_binding,
                            "SYNTHETIC",
                            step.end,
                        )
                    )
        for (stock, day), daily in engine.history.daily.items():
            if (
                stock == symbol
                and window.start <= daily.end < window.stop
                and daily.volume is not None
            ):
                records.append(
                    FitObservation(
                        symbol,
                        daily.end,
                        "VOLUME_D",
                        (symbol, day, 0),
                        daily.volume,
                        fingerprint(daily.source_ids),
                        engine.history.binding,
                        engine.history.action_binding,
                        "SYNTHETIC",
                        daily.end,
                    )
                )
    return fit_floors(tuple(records), window, "synthetic-floors", allow_synthetic=True)


def test_fifteen_other_channels_and_approved_m2_analytic_hand_values(engine, parameters):
    cal = engine.history.calendar
    step = cal.steps[cal._positions["2020-09-15", 2]]
    cells = engine.evaluate("AAPL", step, 1, parameters, july_m2_floors()[0])
    values = {c.feature: c.value for c in cells}
    assert tuple(c.feature for c in cells) == ORDER and all(c.valid for c in cells)
    assert values["M1"] == pytest.approx(1.0, abs=1e-12)
    assert values["M2"] == pytest.approx(1.0, abs=1e-12)
    assert values["M3"] == pytest.approx(math.sqrt(5), abs=1e-10)
    assert values["M4"] == pytest.approx(math.sqrt(105), abs=1e-10)
    assert values["V1"] == pytest.approx(math.log(0.01), abs=1e-12)
    assert values["V2"] == pytest.approx(math.log(0.01), abs=1e-12)
    assert values["V3"] == pytest.approx(0.0, abs=1e-12)
    assert values["B1"] == pytest.approx(math.log(1.02 / 0.99) + 0.01, abs=1e-12)
    bar = engine.history.bars["AAPL", step.session, step.slot]
    assert values["B2"] == pytest.approx(
        (2 * bar.close - bar.high - bar.low) / (bar.high - bar.low)
    )
    p = parameters.for_stock("AAPL")
    matching = cal.matching[step.session, step.slot]
    historical = [engine.history.bars["AAPL", day, step.slot].volume for day in matching]
    expected_q1 = math.log(
        (bar.volume + p.hourly_pseudocount) / (sum(historical) / 20 + p.hourly_pseudocount)
    )
    assert values["Q1"] == pytest.approx(expected_q1)
    days = cal.days[: cal.days.index(step.session)]
    volumes = [engine.history.daily["AAPL", d].volume for d in days[-60:]]
    assert all(v is not None for v in volumes)
    expected_q2 = math.log(
        (sum(v for v in volumes[-5:] if v is not None) / 5 + p.daily_pseudocount)
        / (sum(v for v in volumes if v is not None) / 60 + p.daily_pseudocount)
    )
    assert values["Q2"] == pytest.approx(expected_q2)
    closes = [engine.history.daily["AAPL", d].close for d in days[-20:]]
    assert values["T1"] == pytest.approx(
        math.log(bar.close / (sum(v for v in closes if v is not None) / 20))
    )
    assert values["T2"] == 1
    assert values["T3"] is not None and values["T4"] is not None and values["T5"] is not None


@pytest.mark.parametrize("direction,expected", [(1.0, 1.0), (0.0, 0.0), (-1.0, -1.0)])
def test_wilder_14_plus_140_updates_zero_gain_loss_cases(direction, expected):
    state = IndicatorState()
    for i in range(154):
        state.update(1000 + direction * i)
    assert state.wilder_updates == 139 and state.normalized_rsi() is None
    state.update(1000 + direction * 154)
    assert state.wilder_updates == 140 and state.normalized_rsi() == expected


def test_gap_freezes_wilder_recovery_has_no_return_while_ema_skips_only_missing_updates():
    state = IndicatorState()
    for i in range(155):
        state.update(100 + i)
    before = state.average_gain, state.average_loss, state.wilder_updates, state.ema_updates
    state.update(None)
    assert (
        state.average_gain,
        state.average_loss,
        state.wilder_updates,
        state.ema_updates,
    ) == before
    state.update(10000.0)
    assert (state.average_gain, state.average_loss, state.wilder_updates) == before[:3]
    assert state.ema_updates == before[3] + 1
    state.update(10001.0)
    assert state.wilder_updates == before[2] + 1 and state.average_gain == before[0]


def test_exact_360_good_ema_updates_and_no_synthetic_overnight_updates(engine):
    cal = engine.history.calendar
    assert engine.components("AAPL", cal.steps[359]).values["T3"] is None
    assert engine.components("AAPL", cal.steps[360]).values["T3"] is not None
    assert engine.components("AAPL", cal.steps[153]).values["T5"] is None
    assert engine.components("AAPL", cal.steps[154]).values["T5"] is not None
    state = IndicatorState()
    state.update(100.0)
    state.update(107.0)
    assert state.emas[6] == 102.0 and state.emas[18] == pytest.approx(100 + 14 / 19)


def test_previous_daily_state_future_close_counterfactual_matching_slot_and_exact_old_endpoints(
    engine, parameters
):
    cal = engine.history.calendar
    first = cal.steps[cal._positions["2020-09-15", 1]]
    last = cal.steps[cal._positions["2020-09-15", 6]]
    a = engine.components("AAPL", first)
    b = engine.components("AAPL", last)
    for name in ("RMS63", "MOM5", "MOM105", "Q2_5", "Q2_60", "T2"):
        assert a.values[name] == b.values[name]
    # A future session close has no role in a prior input's scheduled history.
    future = engine.history.daily["AAPL", "2020-09-16"]
    assert future.end > first.end
    matching = cal.matching["2019-07-05", 6]
    assert "2019-07-03" not in matching  # actual 2019 early-close has no sixth full hour


def test_unknown_clocks_never_become_valid_source_only_data_and_confirmation_math_is_blocked(
    engine,
):
    bar = engine.history.bars["AAPL", "2020-09-15", 1]
    changed = replace(bar, basis="UNKNOWN", available_at=None, action_verified=False)
    history = StockHistory(
        engine.history.calendar,
        tuple(changed if b.row_id == bar.row_id else b for b in engine.history.bars.values()),
        synthetic=True,
    )
    calc = FeatureCalculator(history, engine.returns)
    step = history.calendar.steps[history.calendar._positions["2020-09-15", 1]]
    cells = calc.evaluate("AAPL", step, 1)
    assert all(not c.valid and c.reason == "SOURCE_PUBLICATION_UNKNOWN" for c in cells)
    diagnostic = calc.evaluate("AAPL", step, 1, source_only=True)
    assert not any(c.valid for c in diagnostic) and diagnostic[7].value is not None


@pytest.fixture(scope="module")
def normalizer(engine, parameters):
    m2 = july_m2_floors()
    training = []
    for symbol, mf in zip(UNIVERSE, m2):
        for step in engine.history.calendar.steps:
            if parameters.window.start <= step.end < parameters.window.stop:
                training.extend(
                    engine.evaluate(
                        symbol,
                        step,
                        1,
                        parameters,
                        mf,
                        context="HISTORICAL_TRAINING",
                        training_origin=step.end,
                    )
                )
                training.extend(
                    engine.evaluate(
                        symbol,
                        step,
                        2,
                        parameters,
                        mf,
                        context="HISTORICAL_TRAINING",
                        training_origin=step.end,
                    )
                )
    return fit_scaler(
        fitting_observations(tuple(training)),
        parameters.window,
        "synthetic-scaler",
        allow_synthetic=True,
    )


def test_complete_5_48_16_scaler_admission_c01_bridge_and_missing_scaler_hold(
    engine,
    parameters,
    normalizer,
):
    m2 = july_m2_floors()
    scaler = normalizer
    tensor = stock_window(engine, "2020-09-15", 1, parameters, m2, scaler)
    assert tensor.shape == (5, 48, 16) and tensor.input_eligible
    assert sum(v for s in tensor.mask for r in s for v in r) == 3840
    assert all(len(r) == 16 for s in tensor.values for r in s)
    assert not tensor.research_ready
    plan = execution_plan(engine.history.calendar.clock("2020-09-15"), 1)
    forecast = forecast_bridge(tensor, plan)
    assert forecast.issuable and forecast.input_symbols == UNIVERSE
    assert join_market(tensor, None, origin=1).stock_only_eligible
    assert not join_market(tensor, None, origin=1).matched_market_eligible
    assert not stock_window(engine, "2020-09-15", 1, parameters, m2).input_eligible
    with pytest.raises(ValueError, match="BINDING"):
        stock_window(
            engine, "2020-09-15", 1, replace(parameters, source_binding="c" * 64), m2, scaler
        )


def test_m2_floor_is_still_checked_at_each_step_and_late_outcome_cannot_enter(engine, parameters):
    cal = engine.history.calendar
    step = cal.steps[cal._positions["2020-09-15", 1]]
    floor = july_m2_floors()[0]
    future_floor = replace(
        floor,
        window=replace(floor.window, fitted_at=step.information_cutoff + pd.Timedelta(minutes=1)),
    )
    cell = engine.evaluate("AAPL", step, 1, parameters, future_floor)[1]
    assert cell.value is None and cell.reason == "FLOOR_NOT_AVAILABLE_AT_STEP"
    last_day = cal.previous_origins(step, 1)[-1]
    source = engine.returns.get("AAPL", last_day, 1)
    assert source is not None
    records = tuple(
        replace(r, value=999.0, maturity=step.end + pd.Timedelta(minutes=1))
        if r.key == source.key
        else r
        for r in engine.returns._records.values()
    )
    calc = FeatureCalculator(engine.history, ReturnIndex(records))
    # Reuse immutable rolling components, not an altered or forward-filled source.
    calc._components = engine._components.copy()
    calc._built = engine._built.copy()
    late = calc.evaluate("AAPL", step, 1, parameters, floor)[1]
    assert late.value == pytest.approx(1.0) and late.m2 is not None
    assert late.m2.valid20 == 19 and late.m2.missing_reasons[-1] == "NOT_MATURED_AT_STEP"
    assert step.information_cutoff == step.end


def test_exact_zero_volume_pseudocount_hand_case_no_zero_imputation(
    engine, parameters, monkeypatch
):
    step = engine.history.calendar.steps[engine.history.calendar._positions["2020-09-15", 1]]
    component = engine.components("AAPL", step)
    changed = replace(
        component,
        values=component.values | {"VOLUME_H": 0.0, "Q1_MEAN": 100.0, "Q2_5": 0.0, "Q2_60": 100.0},
    )
    monkeypatch.setattr(engine, "components", lambda *a, **k: changed)
    cells = engine.evaluate("AAPL", step, 1, parameters, july_m2_floors()[0])
    p = parameters.for_stock("AAPL")
    assert cells[9].value == pytest.approx(
        math.log(p.hourly_pseudocount / (100 + p.hourly_pseudocount))
    )
    assert cells[10].value == pytest.approx(
        math.log(p.daily_pseudocount / (100 + p.daily_pseudocount))
    )


def test_m2_floor_fit_reuses_existing_rms_and_origin_contract(engine, parameters):
    from lstm_data.ft0_transforms import fit_m2_floor

    results = []
    for step in engine.history.calendar.steps:
        if parameters.window.start <= step.end < parameters.window.stop:
            for origin in (1, 2):
                value = engine.evaluate(
                    "AAPL",
                    step,
                    origin,
                    parameters,
                    july_m2_floors()[0],
                    context="HISTORICAL_TRAINING",
                    training_origin=step.end,
                )[1].m2
                assert value is not None
                results.append(value)
    certificate = fit_m2_floor(
        tuple(results), parameters.window, "AAPL", "synthetic-m2", allow_synthetic=True
    )
    assert certificate.epsilon == pytest.approx(0.008)
    assert {key[2] for key in certificate.fitting_keys} == {1, 2}
    assert (
        len(certificate.fitting_keys) == 42
    )  # 21 calendar sessions, two origins, no six-hour copies
    with pytest.raises(ValueError, match="PENDING"):
        fit_m2_floor(tuple(results), parameters.window, "AAPL", "not-approved")


def test_stock_spy_positive_join_reuses_frozen_D7_with_same_48_positions(
    engine,
    parameters,
    normalizer,
):
    from lstm_data.market_features import (
        DailyScaleSample,
        MarketClose,
        MarketFitWindow,
        MarketHistory,
        MarketObservation,
        fit_synthetic_floors,
        fit_synthetic_scaler,
        vector,
    )

    cal = engine.history.calendar
    hours = tuple(
        MarketObservation(
            s.start,
            s.end,
            100.0,
            100.0 * math.exp(0.02),
            s.end,
            "SYNTHETIC",
            f"synthetic-market:{i}",
            True,
        )
        for i, s in enumerate(cal.steps)
    )
    closes = {
        day: MarketClose(
            clock.close,
            100.0 * math.exp(0.01 * i),
            clock.close,
            "SYNTHETIC",
            f"synthetic-daily-market:{i}",
            True,
        )
        for i, (day, clock) in enumerate(cal._sessions.items())
        if clock.close is not None
    }
    history = MarketHistory(cal, hours, closes, allow_synthetic=True)
    w = MarketFitWindow(
        parameters.window.start, parameters.window.stop, parameters.window.fitted_at, "INNER_TRAIN"
    )
    measures = tuple(history.measures(s) for s in cal.steps if w.contains(s.end))
    daily = tuple(
        DailyScaleSample(c.period_end, 0.01) for c in closes.values() if w.contains(c.period_end)
    )
    market_floors = fit_synthetic_floors(measures, daily, w, "synthetic", allow_synthetic=True)
    market_scaler = fit_synthetic_scaler(
        tuple(vector(m, market_floors, allow_synthetic=True) for m in measures),
        w,
        "synthetic",
        allow_synthetic=True,
    )
    # Stock scaler already validated in the full tensor test; this join also accepts a
    # negative stock tensor and must preserve the valid separate market-shaped object.
    stock = stock_window(engine, "2020-09-15", 1, parameters, july_m2_floors(), normalizer)
    candidate = join_market(stock, history, market_floors, market_scaler, origin=1)
    assert candidate.market is not None and candidate.market.values is not None
    assert len(candidate.market.values) == 48 and all(len(v) == 5 for v in candidate.market.values)
    assert candidate.market.scheduled_ends == tuple(s.end for s in stock.steps)
    assert candidate.stock_only_eligible and candidate.matched_market_eligible
    assert not candidate.research_ready and candidate.future_mc0_width == 21


def test_full_ft0_c01_future_source_price_publication_counterfactual_is_identical(
    engine, parameters, normalizer
):
    day = "2020-09-15"
    bar = engine.history.bars["AAPL", day, 5]  # future exit relative to first-hour origin
    changed = replace(
        bar, close=bar.close * 2, high=bar.high * 2, available_at=bar.end + pd.Timedelta(days=1)
    )
    history = StockHistory(
        engine.history.calendar,
        tuple(changed if b.row_id == bar.row_id else b for b in engine.history.bars.values()),
        synthetic=True,
    )
    assert history.binding == engine.history.binding
    assert history.content_sha256 != engine.history.content_sha256
    alternate = FeatureCalculator(history, engine.returns)
    before = stock_window(engine, day, 1, parameters, july_m2_floors(), normalizer)
    after = stock_window(alternate, day, 1, parameters, july_m2_floors(), normalizer)
    assert before.input_eligible == after.input_eligible is True
    assert before.raw_values == after.raw_values and before.values == after.values
    plan = execution_plan(history.calendar.clock(day), 1)
    assert forecast_bridge(before, plan) == forecast_bridge(after, plan)


def test_ema_and_wilder_closed_form_independent_price_history_with_overnight_gap(engine):
    cal = engine.history.calendar
    step = cal.steps[cal._positions["2020-09-14", 1]]
    stop = cal._positions[step.session, step.slot]
    prices = [engine.history.bars["AAPL", s.session, s.slot].close for s in cal.steps[: stop + 1]]

    def exponential(period):
        alpha = 2 / (period + 1)
        return (1 - alpha) ** (len(prices) - 1) * prices[0] + alpha * math.fsum(
            (1 - alpha) ** (len(prices) - 1 - i) * value for i, value in enumerate(prices[1:], 1)
        )

    comp = engine.components("AAPL", step)
    assert comp.values["T3"] == pytest.approx((exponential(6) - exponential(18)) / prices[-1])
    assert comp.values["T4"] == pytest.approx((exponential(24) - exponential(72)) / prices[-1])
    # The previous scheduled observation is Friday's final complete-hour close.
    assert cal.steps[stop - 1].session == "2020-09-11" and prices[-1] < prices[-2]
    changes = [b - a for a, b in zip(prices, prices[1:])]
    gain0 = sum(max(x, 0) for x in changes[:14]) / 14
    loss0 = sum(max(-x, 0) for x in changes[:14]) / 14
    decay = 13 / 14
    count = len(changes) - 14
    gain = decay**count * gain0 + math.fsum(
        decay ** (count - 1 - i) * max(x, 0) / 14 for i, x in enumerate(changes[14:])
    )
    loss = decay**count * loss0 + math.fsum(
        decay ** (count - 1 - i) * max(-x, 0) / 14 for i, x in enumerate(changes[14:])
    )
    assert comp.values["T5"] == pytest.approx((100 - 100 / (1 + gain / loss) - 50) / 50)


def test_daily_locked_scaler_keys_are_distinct_stock_hours_and_m2_keys_are_session_origin(
    engine, parameters
):
    cal = engine.history.calendar
    first = cal.steps[cal._positions["2020-09-15", 1]]
    second = cal.steps[cal._positions["2020-09-15", 2]]
    a = engine.evaluate("AAPL", first, 1, parameters, july_m2_floors()[0])
    b = engine.evaluate("AAPL", second, 1, parameters, july_m2_floors()[0])
    assert a[2].value == b[2].value and a[2].key != b[2].key
    assert a[1].value == b[1].value and a[1].key == b[1].key


def test_later_batch_training_normalization_cannot_become_an_asof_forecast(
    engine, parameters, normalizer
):
    day = "2020-08-17"
    training = stock_window(
        engine, day, 1, parameters, july_m2_floors(), normalizer, context="HISTORICAL_TRAINING"
    )
    assert training.input_eligible and training.application_context == "HISTORICAL_TRAINING"
    assert parameters.window.fitted_at > training.steps[-1].information_cutoff
    plan = execution_plan(engine.history.calendar.clock(day), 1)
    assert not forecast_bridge(training, plan).issuable
    retrospective = stock_window(engine, day, 1, parameters, july_m2_floors(), normalizer)
    assert not retrospective.input_eligible


def test_p2_4_actual_feature_calculator_to_causal_mc0_data_only(engine, parameters, normalizer):
    from test_p2_market_closure import earlier_certificates, synthetic_market

    from lstm_data.market_tensor import assemble_market_inputs

    market = synthetic_market(engine.history.calendar)
    floors, scaler = earlier_certificates(market)
    stock = stock_window(engine, "2020-09-15", 1, parameters, july_m2_floors(), normalizer)
    output = assemble_market_inputs(join_market(stock, market, floors, scaler, origin=1))
    assert output.shape == (5, 48, 21) and not output.scientific_ready
    assert output.scheduled_ends == tuple(s.information_cutoff for s in stock.steps)
    assert output.stock_lineage == stock.lineage
    for i, rows in enumerate(output.mc0_values):
        for j, row in enumerate(rows):
            assert row[:16] == stock.values[i][j]
            assert row[16:] == output.direct_market[j]
