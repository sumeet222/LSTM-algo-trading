"""Source geometry, maturity and protected-reader tests; no economic replay."""

import ast
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lstm_data.trading.track2.stage012.calendar_schedule import MarketClock
from lstm_data.trading.track2.stage35.completion_v2.cache import Sources, geometry
from lstm_data.trading.track2.stage35.completion_v2.signals import controls


def test_calendar_only_universe_and_half_day():
    clock = MarketClock("2024-01-01", "2025-01-10")
    g = geometry(clock, "2024-01-08", "2024-11-29")
    assert len(g[g.session_date_et == "2024-01-08"]) == 7
    assert list(g[g.session_date_et == "2024-11-29"].slot) == ["09:30", "10:30", "11:30", "12:30"]
    assert g.iloc[-1].exit_end_utc > g.iloc[-1].session_close


def test_mature_controls_future_mutation():
    ends = pd.date_range("2020-01-01", periods=70, tz="UTC", freq="D")
    geo = pd.DataFrame({"exit_end_utc": ends, "slot": ["10:30"] * 70})
    moves = np.tile(np.arange(1, 71)[:, None] * 0.001, (1, 20))
    decision = (ends[59] + pd.Timedelta(minutes=2)).value
    a = controls(moves, geo, geo.iloc[0], decision)
    twin = moves.copy()
    twin[59:] = 99
    b = controls(twin, geo, geo.iloc[0], decision)
    np.testing.assert_array_equal(a[0], b[0])
    np.testing.assert_array_equal(a[1], b[1])
    assert a[3] == 59  # equal receipt timestamp is excluded conservatively
    assert a[0][0] == pytest.approx(0.03)
    moves[0, 0] = np.nan
    assert np.isnan(controls(moves, geo, geo.iloc[0], decision)[0][0])


def test_forbidden_source_denied_before_io():
    source = object.__new__(Sources)
    source.plan = {"sources": []}
    with pytest.raises(ValueError, match="DENIED_BEFORE_IO"):
        source.check({"path": "unavailable/2025-01.parquet", "sha256": ""})


def test_runtime_has_no_evaluation_or_economics_import():
    base = Path("src/lstm_data/trading/track2/stage35/completion_v2")
    for file in ("cache.py", "signals.py"):
        tree = ast.parse((base / file).read_text())
        imported = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        assert not any(
            x in m
            for m in imported
            for x in ("phase2", "accounting", "hf20_mag_designa", "execution_model")
        )


def test_actual_cached_window_and_sign_future_source_mutation():
    from lstm_data.trading.track2.stage35.completion_v2.signals import Inputs

    cache = Path("trading/track2/stage35/completion_v2/audits/cache")
    inp = Inputs(cache, 2024)
    geo = pd.read_parquet(cache / "movement_geometry.parquet")
    selected = geo.loc[(geo.session_date_et == "2024-01-08") & (geo.slot == "10:30")]
    original = inp.x(selected)
    clock = MarketClock("2010-07-01", "2025-01-10")
    alpha, sign, _ = inp.trend(clock, "2024-01-08")
    origin_ns = int(pd.Timestamp("2024-01-08T15:30:00Z").value)
    future = inp.end_ns > origin_ns
    inp.common = inp.common.copy()
    inp.m2 = inp.m2.copy()
    inp.close = inp.close.copy()
    inp.common[future] = 987654
    inp.m2[future] = 123456
    inp.close[future] = 999999
    np.testing.assert_array_equal(original, inp.x(selected))
    current_alpha, current_sign, _ = inp.trend(clock, "2024-01-08")
    np.testing.assert_array_equal(alpha, current_alpha)
    np.testing.assert_array_equal(sign, current_sign)
    last = int(np.searchsorted(inp.end_ns, origin_ns, side="right") - 1)
    inp.common[last, 0, 0] += 1
    assert not np.array_equal(original, inp.x(selected))
