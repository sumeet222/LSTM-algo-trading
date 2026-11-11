"""Exact fee, mixed-side crossing and resumable state witnesses."""

from decimal import Decimal as D

import numpy as np
import pytest

from lstm_data.trading.track2.rapid_v1.costs import CostReference
from lstm_data.trading.track2.rapid_v1.diagnostics import QualityBook
from lstm_data.trading.track2.rapid_v1.portfolio import FastAccount, Lot, Order, Request
from lstm_data.trading.track2.rapid_v1.state import decode, encode
from lstm_data.trading.track2.rapid_v1.strategies import DirectionIntent
from lstm_data.trading.track2.stage35.final_backtest_v4.protocol import Scenario


def test_micro_cost_and_retail_cumulative_minimum():
    m = CostReference("MICRO_PRO", 1.0, 1_000_000.0, 10)
    assert m.quote(D(100), D(100), D(0), D(0), 10) == (
        D("100.04"),
        D(".2"),
        D(".2"),
        D(".0003"),
        D(".0001"),
    )
    with pytest.raises(ValueError, match="FUTURE_COST_REFERENCE"):
        m.quote(D(100), D(100), D(0), D(0), 9)
    r = CostReference("RETAIL_CONSERVATIVE")
    assert r.quote(D(100), D(-100), D(0), D(0), 10)[:3] == (D("99.90"), D(1), D(1))
    assert r.quote(D(100), D(-50), D(100), D(1), 10)[1] == 0
    assert r.quote(D(100), D(-100), D(150), D(1), 10)[1] == D(".25")


@pytest.mark.parametrize("short", [-6, -10, -14])
def test_opposed_virtual_lots_conserve(short: int):
    a = FastAccount("M01", "MICRO_PRO", Scenario(fee=D(".002"), minimum=D(0)))
    a.prices[0] = D(100)
    a.lots = {
        key: Lot(key, 0, 10, 250, 20, 1 if q > 0 else -1, q, D(1), pending=D(q))
        for key, q in (("long", 10), ("short", short))
    }
    a.refresh()
    q = D(10 + short)
    order = Order(
        "cross",
        0,
        12,
        13,
        (
            Request("long", D(10), "ENTRY"),
            Request("short", D(short), "ENTRY"),
        ),
        q,
        12,
        20,
    )
    a.cost_references["cross"] = CostReference(a.population, 1.0, 1_000_000.0, 12)
    with pytest.raises(ValueError, match="FILL_BEFORE_SOURCE_RECEIPT"):
        a.fill(order, D(100), 15, 13)
    a.fill(order, D(100), 16, 13)
    assert a.quantity[0] == q
    assert a.abs_virtual[0] == 10 - short
    assert a.commission == D(".002") * abs(q)
    assert a.nav() == D(100000) - a.commission - a.friction
    assert len(a.stats.physical_rows) == int(q != 0)
    assert (a.restricted() > 0) == (q < 0)
    restored = decode(encode(a))
    assert isinstance(restored, FastAccount)
    assert restored.nav() == a.nav()
    assert encode(restored) == encode(a)
    np.testing.assert_array_equal(restored.quantity, a.quantity)


def test_pending_quality_resume_order_stable():
    quality = QualityBook()
    for k in (5, 4, 6, 4):
        quality.add(
            DirectionIntent("M01", "2021-01-04", 0, 3, 240, (0,), (1,), (1.0,), 1.0, "source"),
            k,
            243,
        )
    restored = decode(encode(quality))
    assert isinstance(restored, QualityBook)
    assert encode(restored) == encode(quality)
    assert restored.queue[0][:2] == (4, 2)


def test_pair_two_legs_wait_and_settle_atomically():
    from test_research import day_fixture

    from lstm_data.trading.track2.rapid_v1.runner import FastEngine

    engine = FastEngine.__new__(FastEngine)
    day = day_fixture(100)
    a = FastAccount("R05", "RETAIL_CONSERVATIVE", Scenario())
    engine.fast_accounts = [a]
    engine.paired_lots = {"long": "pair", "short": "pair"}
    engine.policy_counts = {}
    engine.known_closes = np.full(20, 100.0)
    engine.known_volumes = np.full(20, 10_000.0)
    engine.known_marks = np.full(20, 100)
    for ticker, lot_id, quantity in ((0, "long", 20), (1, "short", -20)):
        q = D(quantity)
        a.lots[lot_id] = Lot(
            lot_id, ticker, 100, 340, 110, 1 if q > 0 else -1, quantity, D(1), pending=q
        )
        a.pending[ticker] = Order(
            lot_id, ticker, 103, 104, (Request(lot_id, q, "ENTRY"),), q, 103, 110
        )
        a.cost_references[lot_id] = CostReference(a.population, available_at=103)
    a.refresh()
    integrals = np.zeros(20, dtype=object)
    day.valid[4, 1] = False
    assert engine.settle_pending(0, day, 4, 107, 104, integrals)
    assert not np.any(a.quantity)
    assert len(a.pending) == 2
    assert a.commission == 0
    assert engine.settle_pending(0, day, 5, 108, 105, integrals)
    assert tuple(a.quantity[:2]) == (20, -20)
    assert a.commission == 2
    assert a.restricted() == D("1998")
    assert not a.pending
    assert {row["effective"] for row in a.stats.physical_rows} == {105}
    assert a.nav() == D("99994")
