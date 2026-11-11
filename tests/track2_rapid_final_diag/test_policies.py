"""Prespecified branch witnesses, unit safety and future-input isolation."""

import ast
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal as D
from pathlib import Path

import numpy as np
import pytest

from lstm_data.trading.track2.rapid_final_diag.policy import (
    capped_trail,
    cases,
    confirm,
    observe_changed,
    stress_scale,
)
from lstm_data.trading.track2.rapid_v1.paths import canonical
from lstm_data.trading.track2.rapid_v1.shared_features import FeatureFrame
from lstm_data.trading.track2.rapid_v3_dynamic.offline import extension, targets
from lstm_data.trading.track2.rapid_v3_dynamic.policy import HoldingClock, observe
from lstm_data.trading.track2.stage012.calendar_schedule import MarketClock
from lstm_data.trading.track2.stage35.final_backtest_v4.execution_calendar import ExecutionCalendar
from lstm_data.trading.track2.stage35.final_backtest_v4.market import minute


def frame(now=102, price=99.9, session="2021-01-04"):
    p = np.full(20, price)
    return FeatureFrame(
        session,
        1,
        now - 2,
        now,
        now + 240,
        now - 2,
        0,
        True,
        {"price": p, "raw_price": p, "factor": np.ones(20)},
        np.zeros((3, 4)),
        "source-frontier",
    )


def state(s="M04"):
    return {
        "sid": s,
        "tickers": (0,),
        "signs": (1,),
        "active_at": 90,
        "entry_slot": 1,
        "strength": 2.0,
        "minimum_age": 1000,
        "trail_distance": 0.5,
        "peak": None,
        "weak": 0,
        "reversal": 0,
        "base": 100.0,
        "event_scale": 0.02,
    }


@pytest.mark.parametrize("sid", ["M04", "M05", "R07"])
def test_two_distinct_resolution_checks_and_recovery(sid):
    s = state(sid)
    z = np.full(20, np.nan)
    f = frame()
    assert "EVENT_RESOLVED" not in observe_changed(s, f, z, z, f.decision)
    observe_changed(s, f, z, z, f.decision)
    assert s["confirmation_count"] == 1
    f = frame(104, session="2021-01-05" if sid == "R07" else "2021-01-04")
    assert "EVENT_RESOLVED" in observe_changed(s, f, z, z, f.decision)
    f = frame(106, 100.5, "2021-01-06")
    assert "EVENT_RESOLVED" not in observe_changed(s, f, z, z, f.decision)
    assert s["confirmation_count"] == 0


def test_resolved_missing_resolved_reset_and_no_double_daily():
    s = state("R07")
    z = np.full(20, np.nan)
    for f in (frame(), frame(104, float("nan"), "2021-01-05"), frame(106, 99.9, "2021-01-06")):
        assert "EVENT_RESOLVED" not in observe_changed(s, f, z, z, f.decision)
    f = frame(108, 99.9, "2021-01-06")
    assert "EVENT_RESOLVED" not in observe_changed(s, f, z, z, f.decision)
    assert s["confirmation_count"] == 1


def test_reversal_and_hard_trail_preempt_pending_resolution():
    z = np.full(20, np.nan)
    s = state()
    s["trail_distance"], s["peak"] = 0.001, np.log(100.0)
    assert "TRAILING_STOP" in observe_changed(s, frame(price=99), z, z, 102)
    s = state()
    s["reversal"] = 1
    f = frame(price=97)
    assert "SIGNAL_REVERSAL" in observe_changed(s, f, z, z, 102)


def test_m01_faithful_existing_two_check_identity():
    a, b = state("M01"), state("M01")
    a["minimum_age"] = b["minimum_age"] = 0
    score = np.full(20, 0.4)
    for now in (102, 104, 106):
        f = frame(now, 100)
        assert observe_changed(a, f, score, score, now) == observe(b, f, score, score, now)
        assert a == b
    assert a["weak"] == 3


def test_no_future_data_dependency_and_receipt_guard():
    z = np.full(20, np.nan)
    a = state()
    observe_changed(a, frame(), z, z, 102)
    frozen = canonical(a)
    future = frame(1002, 999)
    future.values["price"][0] += 10000
    assert canonical(a) == frozen
    with pytest.raises(ValueError, match="FEATURE_NOT_RECEIVED"):
        observe_changed(a, replace(frame(), latest_observation_end=102), z, z, 102)


@pytest.mark.parametrize("v", ["0", ".00001", ".02", ".25", "1"])
def test_reserve_largest_feasible_t_and_stress_monotonicity(v):
    nav, reserve, A, L = D(100000), D(204), D(1000), D(20)
    proposals = ((D(9000), D(v)), (D(9000), D(v)))
    t, num, den = stress_scale(nav, reserve, A, L, proposals)
    S = sum((u * x.exp() for u, x in proposals), D(0))
    K = sum((u * (x.exp() - 1) for u, x in proposals), D(0))
    assert A + t * S <= D(".2") * (nav - reserve - L - t * K) + D("1e-20")
    assert 0 <= t <= 1
    if 0 < t < 1:
        assert abs(t - num / den) < D("1e-25")
    lower = stress_scale(nav, reserve, A, L, ((D(9000), D(0)),) * 2)[0]
    assert t <= lower
    assert stress_scale(nav, reserve, A + 20000, L, proposals)[0] == 0


def test_reserve_invalid_and_zero_proposal():
    assert stress_scale(D(1), D(0), D(0), D(0), ())[0] == 0
    for x in ("NaN", "-.1", "1.1"):
        with pytest.raises(ValueError):
            stress_scale(D(1000), D(2), D(0), D(0), ((D(200), D(x)),))


def test_m03_entry_log_scale_and_side_symmetry():
    assert capped_trail(0.04, 0.01) == 0.01
    assert capped_trail(0.004, 0.01) == 0.004
    assert capped_trail(0.04, float("nan")) is None
    assert capped_trail(None, 0.01) is None
    z = np.full(20, np.nan)
    for sign, p in ((1, 98.0), (-1, 102.0)):
        s = state("M03")
        s["signs"], s["trail_distance"] = (sign,), capped_trail(0.04, 0.01)
        s["peak"] = sign * np.log(100.0)
        assert "TRAILING_STOP" in observe_changed(s, frame(price=p), z, z, 102)
        assert frame(price=p).latest_observation_end < 102


def test_calendar_weekend_halfday_and_evaluation_cutoff():
    c = HoldingClock(ExecutionCalendar(MarketClock("2021-01-01", "2025-02-01")))
    f = minute("2024-11-27T19:30:00Z")
    p = targets(c, np.array([f]))
    assert int(p["NEXT_FULL_SESSION"][0]) == minute("2024-12-02T19:30:00Z")
    assert c.advance(minute("2024-11-29T17:30:00Z"), 60) == minute("2024-12-02T15:00:00Z")
    late = targets(c, np.array([minute("2024-12-31T20:30:00Z")]))
    assert int(late["T240"][0]) > minute("2024-12-31T23:59:00Z")
    assert extension(-10, 100, 101) == -10
    assert extension(10, 100, 101) == 10


def test_confirmation_missing_and_new_branch_inventory():
    s = {}
    assert not confirm(s, ("a",), True, True)
    assert not confirm(s, ("b",), False, False)
    assert not confirm(s, ("c",), True, True)
    assert confirm(s, ("d",), True, True)
    axis = cases()
    assert len(axis) == 13
    assert len({c.key for c in axis}) == 13
    assert {c.strategy for c in axis} == {"M01", "M03", "M04", "M05", "R01", "R07"}
    assert sum(c.variant not in ("CONTROL", "H100") for c in axis) == 6


def test_engine_never_imports_offline_or_neural():
    root = Path("src/lstm_data/trading/track2/rapid_final_diag")
    for name in ("engine.py", "policy.py", "allocation.py", "book.py"):
        tree = ast.parse((root / name).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert not any(s in (node.module or "") for s in ("offline", "torch", "phase2"))
    # Unexecuted future extension data cannot mutate an earlier state object.
    a = state()
    b = deepcopy(a)
    extension(1, 100, 10000)
    assert a == b
