import json
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

import pytest

from lstm_data.trading.track2.stage012.calendar_schedule import MarketClock
from lstm_data.trading.track2.stage012.model_registry import SYMBOLS
from lstm_data.trading.track2.stage012.risk_sizing import RiskReference
from lstm_data.trading.track2.stage012.sign_scheduler import session_opportunities
from lstm_data.trading.track2.stage35.arms import MaturedRisk, size_multiplier
from lstm_data.trading.track2.stage35.common import D
from lstm_data.trading.track2.stage35.intents import from_signal, signal_from_payload
from lstm_data.trading.track2.stage35.portfolio_allocator import Capacity, allocate


def seed_signal():
    p = Path(
        "trading/track2/stage012/audits/completion_v1/historical_run_v1/signals_with_prefix_risk.json"
    )
    return signal_from_payload(json.loads(p.read_text())[0]["signal"])


def candidates():
    s = seed_signal()
    return tuple(
        from_signal(replace(s, ticker=t), "EQUAL", D(1), "prefix", "synthetic-lineage")
        for t in SYMBOLS
    )


def test_all_twenty_seven_origins_four_folds():
    clock = MarketClock("2021-01-01", "2025-01-10")
    s = seed_signal()
    for day in ("2021-01-08", "2022-01-10", "2023-01-09", "2024-01-08"):
        keys = session_opportunities(clock, day)
        assert len(keys) == 140
        for ticker, origin in keys:
            end = clock.endpoint(origin)
            decision = origin + timedelta(minutes=2)
            identity = json.loads(
                Path("trading/track2/stage012/original_bundles.json").read_text()
            )["bundles"][day[:4]]["sha256"]
            sample = replace(
                s,
                ticker=ticker,
                fold_id="F" + day[2:4],
                model_id="S2C-CA-F" + day[2:4],
                checkpoint_hash=identity[0],
                feature_recipe_id=identity[1],
                c3_calibration_id=identity[2],
                nominal_origin_utc=origin,
                source_latest_observed_end_utc=origin,
                feature_ready_utc=decision,
                simulated_or_actual_source_receipt_utc=decision,
                model_inference_complete_utc=decision,
                decision_utc=decision,
                earliest_order_submission_utc=decision,
                earliest_executable_observation_utc=clock.next_observation(decision),
                nominal_endpoint_utc=end,
            )
            intent = from_signal(sample, "EQUAL", D(1), "prefix", "synthetic")
            assert intent.direction == s.direction and intent.endpoint == end
    assert len(session_opportunities(clock, "2024-11-29")) == 80
    assert not session_opportunities(clock, "2018-12-05")


def test_allocator_cash_caps_rounding_and_subset():
    cs = candidates()
    prices = {t: D(100) for t in SYMBOLS}
    capacity = Capacity(D(10000), D(0), D(0), D(10000), ())
    rows = allocate(cs, capacity, prices)
    assert sum(r.notional for r in rows) == D(2000)
    assert all(r.notional <= D(1000) for r in rows)
    assert allocate(tuple(reversed(cs)), capacity, prices) == rows
    capped = replace(capacity, names=tuple((t, D(999)) for t in SYMBOLS))
    assert sum(r.notional for r in allocate(cs, capped, prices)) == 0
    with pytest.raises(ValueError):
        allocate(cs, replace(capacity, status="RISK_HOLD"), prices)
    assert sum(r.notional for r in allocate(cs[:1], capacity, prices)) == D(1000)
    assert all(r.notional == 0 for r in allocate(cs, replace(capacity, gross=D(10000)), prices))


def test_arms_strict_frontier_and_no_direction():
    s = seed_signal()
    t = s.decision_utc
    ref = RiskReference(
        "AAPL",
        "F24",
        "09:30",
        0.01,
        0.002,
        t - timedelta(days=1),
        t - timedelta(days=1),
        "synthetic",
    )
    history = tuple(
        MaturedRisk(
            0.01,
            t - timedelta(days=k + 1),
            t - timedelta(days=k + 1) + timedelta(minutes=2),
            "synthetic",
            ticker="AAPL",
            slot="09:30",
            fold="F24",
        )
        for k in range(60)
    )
    for arm in ("EQUAL", "ROLLING_RISK", "EWMA_RISK", "S2C_RISK"):
        g = size_multiplier(arm, t, s.calibrated_magnitude or 0, ref, history)
        assert D(".5") <= g <= D("1.5")
        future = MaturedRisk(float("nan"), t + timedelta(days=1), t + timedelta(days=1), "future")
        assert size_multiplier(arm, t, s.calibrated_magnitude or 0, ref, history + (future,)) == g
    with pytest.raises(ValueError):
        size_multiplier("NULL_CONTROL", t, 0.01, ref, history)
    with pytest.raises(ValueError):
        size_multiplier("EWMA_RISK", t, 0.01, ref, history[:39])


def test_wrong_original_identity_and_expired_or_missing_signal():
    s = seed_signal()
    for bad in (
        replace(s, fold_id="F21"),
        replace(s, checkpoint_hash="wrong"),
        replace(s, feature_recipe_id="phase2"),
        replace(s, c3_calibration_id="other"),
    ):
        with pytest.raises(ValueError):
            from_signal(bad, "S2C_RISK", D(1), "prefix", "lineage")
    with pytest.raises(ValueError):
        from_signal(replace(s, direction=0), "EQUAL", D(1), "prefix", "lineage")
    with pytest.raises(ValueError):
        from_signal(
            replace(
                s, earliest_executable_observation_utc=s.nominal_origin_utc + timedelta(minutes=6)
            ),
            "EQUAL",
            D(1),
            "prefix",
            "lineage",
        )
