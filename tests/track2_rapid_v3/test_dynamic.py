"""Exact risk, variable timing, frozen events and offline separation."""

import ast
from dataclasses import replace
from decimal import Decimal as D
from pathlib import Path

import numpy as np
import pytest

from lstm_data.trading.track2.rapid_v1.paths import canonical
from lstm_data.trading.track2.rapid_v1.portfolio import Lot
from lstm_data.trading.track2.rapid_v1.shared_features import FeatureCache, FeatureFrame
from lstm_data.trading.track2.rapid_v1.strategies import IDS, evaluate
from lstm_data.trading.track2.rapid_v3_dynamic.book import DynamicLedger, cap_causes
from lstm_data.trading.track2.rapid_v3_dynamic.engine import DynamicRiskScreen
from lstm_data.trading.track2.rapid_v3_dynamic.offline import extension, targets
from lstm_data.trading.track2.rapid_v3_dynamic.policy import (
    ADAPTERS,
    HoldingClock,
    case_axis,
    initial,
    monitored,
    observe,
    scores,
)
from lstm_data.trading.track2.stage012.calendar_schedule import MarketClock
from lstm_data.trading.track2.stage35.final_backtest_v4.execution_calendar import ExecutionCalendar
from lstm_data.trading.track2.stage35.final_backtest_v4.market import minute
from lstm_data.trading.track2.stage35.final_backtest_v4.protocol import Scenario


def frame(now=102, value=0.0):
    p = np.full(20, 100.0)
    return FeatureFrame(
        "2021-01-04",
        1,
        100,
        now,
        340,
        now - 2,
        0,
        True,
        {
            "price": p,
            "raw_price": p,
            "factor": np.ones(20),
            "r60_z": np.full(20, value),
        },
        np.zeros((3, 4)),
        "causal",
    )


def state():
    return {
        "sid": "M01",
        "tickers": (0,),
        "signs": (1,),
        "active_at": 90,
        "entry_slot": 1,
        "strength": 2.0,
        "minimum_age": 200,
        "trail_distance": 0.1,
        "peak": None,
        "weak": 0,
        "reversal": 0,
    }


def test_all_ids_and_original_features_real():
    axis = case_axis()
    assert set(ADAPTERS) == set(IDS)
    assert len(axis) == len({c.key for c in axis}) == 54
    root = Path("trading/track2/rapid_v1/cache")
    cache = FeatureCache(next(p for p in root.iterdir() if (p / "manifest.json").is_file()))
    found = set()
    for day in cache.by_date:
        for f in cache.frames(day):
            for sid in set(IDS) - found:
                d = evaluate(sid, f)
                if not d.intents:
                    continue
                it = d.intents[0]
                t = initial(sid, it, f, np.ones(20))
                t.update(active_at=f.latest_observation_end - 1, minimum_age=0)
                z, rank = scores(sid, f)
                observe(t, f, z, rank, f.decision)
                assert t["strength"] == it.strength
                assert tuple(t["signs"]) == it.signs
                found.add(sid)
        if found == set(IDS):
            break
    assert found == set(IDS)


def test_receipt_reversal_weakening_and_missing_reset():
    s = state()
    f = frame(value=-1.2)
    z, r = scores("M01", f)
    assert observe(s, f, z, r, 102) == ()
    bad = frame(103, float("nan"))
    zb, rb = scores("M01", bad)
    assert not observe(s, bad, zb, rb, 103)
    assert s["reversal"] == 0
    assert not observe(s, f, z, r, 102)
    later = frame(104, -1.2)
    assert observe(s, later, z, r, 104) == ("SIGNAL_REVERSAL",)
    s = state()
    f = frame(202, 0.4)
    z, r = scores("M01", f)
    assert not observe(s, f, z, r, 202)
    assert observe(s, frame(203, 0.4), z, r, 203) == ("SIGNAL_WEAKENING",)
    with pytest.raises(ValueError, match="FEATURE_NOT_RECEIVED"):
        observe(s, replace(f, latest_observation_end=202), z, r, 202)


def test_short_trailing_and_postexit_mutation():
    s = state()
    s["signs"] = (-1,)
    s["trail_distance"] = 0.03
    f = frame(102, -2.0)
    z, r = scores("M01", f)
    assert observe(s, f, z, r, 102) == ()
    f2 = frame(104, -2.0)
    f2.values["price"][0] = 105
    assert observe(s, f2, z, r, 104) == ("TRAILING_STOP",)
    before = canonical(s)
    assert extension(-10, 106, 99) == 70
    assert extension(-10, 106, 125) == -190
    assert extension(10, 106, 125) == 190
    assert canonical(s) == before
    assert not monitored("R07", f2, False)
    assert monitored("R07", f2, True)


def test_risk_regime_cap_and_unlevered_constraint():
    low = DynamicLedger("M01_STANDARD", "MICRO_PRO", Scenario())
    high = DynamicLedger("M01_HIGH_RISK", "MICRO_PRO", Scenario(), name_cap=D(".15"))
    for a in (low, high):
        a.lots["x"] = Lot("x", 0, 0, 0, 0, 1, 120, D(1), pending=D(120))
        a.refresh()
        a.prices[0] = D(100)
        a.marks_at[0] = 100
        a.groups["x"] = {"reason": None, "max_decision": None}
        a.group_of["x"] = "x"
    assert "NAME_CAP" in cap_causes(low) and low.capacity(102)[3] == "RISK_BREACH"
    assert high.capacity(102)[3] == "READY"
    screen = DynamicRiskScreen(2)
    for n, a in enumerate((low, high)):
        screen.update(n, a, False)
    breach = screen.status(np.r_[100.0, np.zeros(19)], np.zeros(20), np.full(2, 0.02))[0]
    assert list(breach) == [True, False]
    high.lots["x"].pending = D(1100)
    high.refresh()
    assert high.capacity(102)[3] == "RISK_BREACH"
    assert "GROSS_CAP" in cap_causes(high)


def test_actual_clock_limits_and_offline_future_targets():
    c = HoldingClock(ExecutionCalendar(MarketClock("2021-01-01", "2025-02-01")))
    start = minute("2024-11-27T19:30:00Z")
    assert c.sessions(start, 1) == minute("2024-11-29T18:00:00Z")
    t = targets(c, np.array([start]))
    assert int(t["NEXT_FULL_SESSION"][0]) == minute("2024-12-02T19:30:00Z")
    assert c.index(c.advance(start, 780)) - c.index(start) == 780
    year = minute("2024-12-31T20:30:00Z")
    assert c.maximum(year, False) > minute("2024-12-31T23:59:00Z")
    assert c.cal.next(c.maximum(start, True) + 2) > c.maximum(start, True)


def test_offline_module_has_no_import_into_funded_engine():
    root = Path("src/lstm_data/trading/track2/rapid_v3_dynamic")
    for name in ("engine", "decisions", "policy", "book", "state", "report", "cli"):
        tree = ast.parse((root / (name + ".py")).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert "offline" not in (node.module or "")


def test_m04_entry_confirmation_scale_when_current_price_returns_to_open():
    from lstm_data.trading.track2.rapid_v1.strategies import DirectionIntent

    f = frame()
    f.values.update(v20=np.full(20, 0.01), intraday=np.zeros(20), first_hour=np.full(20, 0.01))
    intent = DirectionIntent(
        "M04", f.session, f.origin, f.decision, f.endpoint, (0,), (1,), (1.0,), 2.0, "test"
    )
    s = initial("M04", intent, f, np.ones(20))
    s.update(active_at=90, minimum_age=200)
    z, r = scores("M04", f)
    assert s["event_scale"] == 0.005
    assert observe(s, f, z, r, f.decision) == ("EVENT_RESOLVED",)
