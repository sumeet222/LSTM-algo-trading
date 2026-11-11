"""Causal calendar, account, cash-flow and allocation fixtures for Rapid V2."""

import ast
import inspect
from dataclasses import replace
from decimal import Decimal as D
from textwrap import dedent

import numpy as np
import pandas as pd
import pytest

from lstm_data.hf20_s4_clock import endpoint
from lstm_data.trading.track2.rapid_v1.costs import CostReference
from lstm_data.trading.track2.rapid_v1.portfolio import Lot, Order, Request
from lstm_data.trading.track2.rapid_v1.runner import FastEngine
from lstm_data.trading.track2.rapid_v1.scheduler import EntryBudget
from lstm_data.trading.track2.rapid_v1.shared_features import FeatureFrame
from lstm_data.trading.track2.rapid_v1.strategies import DirectionIntent
from lstm_data.trading.track2.rapid_v2_diagnostics.allocation import AllocationEngine
from lstm_data.trading.track2.rapid_v2_diagnostics.book import Ledger, cap_causes, price_bridge
from lstm_data.trading.track2.rapid_v2_diagnostics.engine import RiskScreen
from lstm_data.trading.track2.rapid_v2_diagnostics.variants import Case, Endpoints, case_axis
from lstm_data.trading.track2.stage012.calendar_schedule import MarketClock
from lstm_data.trading.track2.stage35.final_backtest_v4.execution_calendar import ExecutionCalendar
from lstm_data.trading.track2.stage35.final_backtest_v4.market import minute
from lstm_data.trading.track2.stage35.final_backtest_v4.protocol import Scenario


def test_axis_and_only_allocation_change():
    cases = case_axis()
    assert len(cases) == len({c.key for c in cases}) == 108
    assert sum(c.variant == "H100" for c in cases) == 18
    original = dedent(inspect.getsource(FastEngine.allocate))
    new = dedent(inspect.getsource(AllocationEngine.allocate))
    edited = new.replace(
        "commitment_budget(budget, self.case_by_key[a.arm].headroom) / len(ready)",
        "budget / len(ready)",
    )
    assert edited != new
    assert ast.dump(ast.parse(edited)) == ast.dump(ast.parse(original))


def at(date: str, hour: str) -> pd.Timestamp:
    value = pd.Timestamp(date + " " + hour, tz="America/New_York")
    if not isinstance(value, pd.Timestamp):
        raise ValueError("INVALID_TEST_TIMESTAMP")
    return value


def f_at(clock: MarketClock, date: str, hour: str) -> FeatureFrame:
    stamp = at(date, hour)
    origin = minute(stamp)
    return FeatureFrame(
        date,
        1,
        origin,
        origin + 2,
        minute(endpoint(stamp, clock.calendar)),
        origin,
        origin,
        True,
        {},
        np.empty((0, 4)),
        "frozen",
    )


@pytest.mark.parametrize(
    "date,hour",
    [
        ("2024-03-08", "09:30"),
        ("2024-03-08", "15:30"),
        ("2024-11-27", "14:30"),
        ("2024-11-29", "12:30"),
        ("2024-12-31", "15:30"),
    ],
)
def test_minute_endpoints(date, hour):
    clock = MarketClock("2024-01-01", "2025-01-10")
    indexed = Endpoints(ExecutionCalendar(clock))
    frame = f_at(clock, date, hour)
    for minutes in (60, 120, 240, 480):
        c = Case("M01", "T", D(1), minutes, "minutes")
        expected = minute(endpoint(at(date, hour), clock.calendar, minutes))
        assert indexed.anchor(frame, c) == expected
        assert indexed.cal.next(expected + 2) > expected + 2


def test_session_endpoints_abstain_on_halfday_and_skip_closures():
    clock = MarketClock("2024-01-01", "2025-01-10")
    ix = Endpoints(ExecutionCalendar(clock))
    case = Case("R08", "D1", D(1), 1, "sessions")
    f = f_at(clock, "2024-11-27", "14:30")
    intent = DirectionIntent(
        "R08", f.session, f.origin, f.decision, f.endpoint, (0,), (1,), (1.0,), 1.0, "frozen"
    )
    assert ix.retime(f, case, (intent,)) == ((), "FUTURE_SESSION_SLOT_UNAVAILABLE")
    assert ix.anchor(f, replace(case, horizon=3)) == minute(at("2024-12-03", "14:30"))
    assert ix.anchor(f, replace(case, horizon=5)) == minute(at("2024-12-05", "14:30"))
    dst = f_at(clock, "2024-03-08", "09:30")
    assert ix.anchor(dst, case) == minute(at("2024-03-11", "09:30"))
    late = f_at(clock, "2024-12-31", "15:30")
    target = ix.anchor(late, case)
    assert target is not None and ix.cal.next(target + 2) > ix.cutoff


def test_paired_headroom_uses_same_caps_and_does_not_resize():
    clock = MarketClock("2024-01-01", "2025-01-10")
    frame = f_at(clock, "2024-02-05", "10:30")
    it = DirectionIntent(
        "R05",
        frame.session,
        frame.origin,
        frame.decision,
        frame.endpoint,
        (0, 1),
        (1, -1),
        (1.0, 1.0),
        1.0,
        "frozen",
    )
    engine = AllocationEngine.__new__(AllocationEngine)
    engine.last = "2024-12-31"
    engine.execution_calendar = ExecutionCalendar(clock)
    engine.account_holds = {}
    engine.paired_lots = {}
    quantities = []
    for factor in ("1", ".85", ".70"):
        c = Case("R05", factor, D(factor), 240, "minutes")
        a = Ledger(c.key, c.mode, Scenario())
        engine.case_by_key = {c.key: c}
        engine.budgets = {c.key: EntryBudget(c.mode)}
        a.prices[:2] = [D(100), D(100)]
        a.volume[:2] = [D(100000), D(100000)]
        a.marks_at[:2] = [frame.decision - 2] * 2
        orders = engine.allocate(a, frame, (it,), frame.decision)
        assert len(orders) == 2 and {r.role for v in orders.values() for r in v} == {"ENTRY"}
        assert a.quantity.tolist() == [0] * 20
        assert a.gross() == D(sum(abs(r.delta) for v in orders.values() for r in v)) * D(100)
        assert a.capacity(frame.decision)[1] <= a.cash - a.gross()
        quantities.append(orders[0][0].delta)
        a.prices[0] = D(400)  # Reserve-aware mark breach stays a hard gate.
        assert a.capacity(frame.decision)[3] == "RISK_BREACH"
        assert cap_causes(a)
        screen = RiskScreen(1)
        screen.update(0, a)
        assert screen.status(np.array([400.0, 100.0] + [0.0] * 18), np.zeros(20), np.array([0.02]))[
            0
        ][0]
    assert quantities == [99, 84, 69]


@pytest.mark.parametrize(
    "q,mark,raw,fill,expected",
    [
        (10, "100", "101", "101.10", ("10", "1", "11")),
        (-10, "100", "101", "100.90", ("-10", "1", "-9")),
        (-10, "100", "99", "98.90", ("10", "1", "11")),
        (10, "100", "99", "99.10", ("-10", "1", "-9")),
        (0, "100", "99", "99.10", ("0", "0", "0")),
    ],
)
def test_directional_arrival_bridge(q, mark, raw, fill, expected):
    assert price_bridge(D(q), D(mark), D(raw), D(fill)) == tuple(D(v) for v in expected)


def test_mixed_partial_fill_order_fee_and_forced_notional():
    a = Ledger("R01_H100", "RETAIL_CONSERVATIVE", Scenario())
    a.prices[0] = D(100)
    a.marks_at[0] = 10
    a.lots["long"] = Lot("long", 0, 8, 250, 18, 1, 250, D(1), pending=D(250))
    a.lots["short"] = Lot("short", 0, 8, 250, 18, -1, -50, D(1), pending=D(-50))
    a.refresh()
    o = Order(
        "pair",
        0,
        12,
        13,
        (Request("long", D(250), "ENTRY"), Request("short", D(-50), "ENTRY")),
        D(200),
        12,
        18,
    )
    a.pending[0] = o
    a.cost_references[o.key] = CostReference(a.population, available_at=12)
    a.record("ORDER", 12, ticker=0)
    a.fill(o, D(100), 16, 13, D(".5"))
    assert a.commission == D(1)
    assert a.quantity[0] == 100 and a.abs_virtual[0] == 300
    a.fill(o, D(100), 17, 14)
    assert a.commission == D(1) and a.quantity[0] == 200 and a.abs_virtual[0] == 300
    assert a.totals["physical_orders"] == 1 and a.totals["external_fills"] == 2
    assert a.nav() == D(100000) - a.commission - a.friction
    a.reconcile()
