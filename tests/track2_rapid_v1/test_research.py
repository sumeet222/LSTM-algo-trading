"""Reference signals and causal clocks for the frozen research defaults."""

from dataclasses import replace
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

from lstm_data.trading.track2.rapid_v1.diagnostics import QualityBook
from lstm_data.trading.track2.rapid_v1.scheduler import EntryBudget, weekly_scan_dates
from lstm_data.trading.track2.rapid_v1.shared_features import FeatureBuilder, FeatureFrame
from lstm_data.trading.track2.rapid_v1.sources import RawDay, RawMarket, valid_ohlcv
from lstm_data.trading.track2.rapid_v1.strategies import IDS, SLOTS, DirectionIntent, evaluate
from lstm_data.trading.track2.stage012.calendar_schedule import MarketClock
from lstm_data.trading.track2.stage35.final_backtest_v4.market import minute


def day_fixture(first: int, date: str = "2021-01-04") -> RawDay:
    prices = np.full((390, 20), 100.0)
    return RawDay(
        date,
        np.arange(first, first + 390),
        prices.copy(),
        prices.copy(),
        np.full_like(prices, 100_000),
        np.ones_like(prices, dtype=bool),
        pd.DataFrame(),
        "fabricated",
        {},
        prices * 1.001,
        prices * 0.999,
    )


@pytest.mark.parametrize(
    "sid,sign,count",
    [
        ("M01", 1, 20),
        ("M02", -1, 20),
        ("M03", -1, 20),
        ("M04", 1, 20),
        ("M05", 1, 20),
        ("M06", 1, 2),
        ("M07", 1, 20),
        ("M08", -1, 20),
        ("M09", -1, 20),
        ("R01", 1, 2),
        ("R02", 1, 20),
        ("R03", 1, 20),
        ("R04", -1, 2),
        ("R05", -1, 3),
        ("R06", -1, 2),
        ("R07", 1, 20),
        ("R08", 1, 20),
        ("R09", 1, 2),
    ],
)
def test_all_menu_rules(sid: str, sign: int, count: int):
    v = {
        key: np.full(20, value)
        for key, value in {
            "raw_price": 102.0,
            "price": 102.0,
            "r60_z": 2.0,
            "r60": 0.02,
            "volume_z": 2.0,
            "gap_z": 2.0,
            "gap": 0.02,
            "first_hour_z": 2.0,
            "first_hour": 0.01,
            "cumulative_volume_ratio": 1.5,
            "or_high": 101.0,
            "or_low": 99.0,
            "h20": 101.0,
            "l20": 99.0,
            "v20": 0.02,
            "v60": 0.02,
            "compression": 1.0,
            "residual_z": 2.0,
            "residual": 0.02,
            "peer_count": 20.0,
            "same_clock_z": 2.0,
            "intraday_z": 2.0,
            "intraday": 0.02,
            "j6minus1": 0.1,
            "j5": 0.03,
            "residual5": 2.0,
            "volume_rank": 2.0,
            "trend": 2.0,
            "on10": 0.02,
            "on_scale": 0.01,
            "intra10": -0.02,
            "intra_scale": 0.01,
        }.items()
    }
    f = FeatureFrame(
        "2021-01-04",
        SLOTS[sid][0],
        100,
        103,
        340,
        101,
        50,
        True,
        v,
        np.tile((1.0, -0.1, 0.01, 0.8), (3, 1)),
        "asof",
    )
    result = evaluate(sid, f)
    assert len(result.intents) == count
    assert all(i.signs[0] == sign for i in result.intents)
    if sid == "R05":
        assert all(i.signs == (-1, 1) and len(i.tickers) == 2 for i in result.intents)
    else:
        assert result.intents[0].tickers == (0,)
    with pytest.raises(ValueError, match="FEATURE_NOT_RECEIVED"):
        evaluate(sid, replace(f, latest_observation_end=102))
    if sid.startswith("R"):
        assert not evaluate(sid, replace(f, weekly_scan=False)).scheduled


def test_registry_axis():
    assert len(IDS) == len(set(IDS)) == 18
    assert set(IDS) == set(SLOTS)


def test_shared_signal_frontier_cannot_see_future():
    clock = MarketClock("2020-01-01", "2021-01-12")
    builder = FeatureBuilder(clock)
    first = minute("2021-01-04T14:30:00Z")
    day = day_fixture(first)
    day.closes[59] = 104
    day.highs[59] = 105
    refs, pairs = builder.references()
    before = builder.frame(day, 1, refs, pairs)
    opening = builder.frame(day, 0, refs, pairs)
    assert opening.decision == first + 3
    assert before.decision == first + 62
    assert before.values["r60"][0] == pytest.approx(np.log(1.04))
    assert before.values["or_high"][0] == pytest.approx(100.1)
    day.closes[60:] *= 30
    day.volumes[60:] *= 500
    day.highs[60:] *= 50
    after = builder.frame(day, 1, refs, pairs)
    for name in before.values:
        np.testing.assert_array_equal(before.values[name], after.values[name])
    assert evaluate("M01", before) == evaluate("M01", after)
    assert evaluate("M02", before) == evaluate("M02", after)
    assert evaluate("M06", before) == evaluate("M06", after)


def test_calendar_cutoff_and_weekly_budget():
    clock = MarketClock("2024-03-01", "2025-01-08")
    assert len(clock.origins("2024-11-29")) == 4
    assert not clock.origins("2024-11-28")
    assert clock.origins("2024-03-08")[0].hour == 14
    assert clock.origins("2024-03-11")[0].hour == 13
    assert clock.endpoint(clock.origins("2024-12-31")[-1]).year == 2025
    assert "2024-11-25" in weekly_scan_dates(clock)
    assert "2024-11-29" not in weekly_scan_dates(clock)
    with pytest.raises(ValueError, match="PRICE_PERIOD_SCOPE"):
        RawMarket("2024-12-31", "2025-01-02")
    retail = EntryBudget("RETAIL_CONSERVATIVE")
    retail.reserve("2024-11-25", 2)
    retail.reserve("2024-11-27", 2)
    with pytest.raises(ValueError, match="ENTRY_BUDGET"):
        retail.reserve("2024-11-29", 2)
    assert retail.remaining("2024-12-02") == 5
    micro = EntryBudget("MICRO_PRO")
    micro.reserve("2024-11-27", 6)
    assert micro.remaining("2024-11-27") == 0
    assert micro.remaining("2024-11-29") == 6


def test_quality_matures_only_after_next_valid_bar():
    origin = minute(datetime(2021, 1, 4, 14, 30, tzinfo=timezone.utc))
    day = day_fixture(origin)
    intent = DirectionIntent(
        "M01", day.date, origin, origin + 3, origin + 240, (0,), (1,), (1.0,), 2.0, "asof"
    )
    q = QualityBook()
    q.add(intent, origin + 4, origin + 243)
    day.valid[4, 0] = False
    for i in range(243):
        q.tick(day, i, np.ones(20))
    assert not q.completed["M01"]
    assert q.pending[0].entry_at == origin + 5
    day.opens[243, 0] = 101
    q.tick(day, 243, np.ones(20))
    [result] = q.completed["M01"]
    assert result["gross_equal_notional_USD"] == pytest.approx(100)
    assert not q.pending
    bad = np.array([np.nan, -1.0, 10.0, 10.0])
    assert list(
        valid_ohlcv(
            bad, np.full(4, 11.0), np.full(4, 9.0), bad, np.array([100.0, 100.0, 100.0, -1.0])
        )
    ) == [False, False, True, False]
