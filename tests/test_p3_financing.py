"""Independent friction arithmetic and fresh policy/borrow scenario paths."""

from decimal import Decimal as D

import pandas as pd
import pytest
from test_p3_policy import NAMES, engine, entry, exit_at, forecast, references

from lstm_data.p3_domain import MODE, Forecast, Frictions, Permission
from lstm_data.p3_execution import ExecutionOffer
from lstm_data.p3_policy import Policy, rank_intent
from lstm_data.p3_replay import ReplayFrame, replay, scenario_matrix


def script_for(e):
    frames = []
    for origin, reverse in ((1, False), (2, True)):
        f = forecast(e, origin, reverse)
        assert f.plan.entry is not None
        refs = references(e, f.plan.entry, cutoff=f.plan.cutoff)
        frames.append(
            ReplayFrame(
                e.universe,
                f"SYN:FRAME:{origin}",
                f.plan.entry,
                refs,
                tuple(ExecutionOffer(e.universe, r) for r in refs),
                f,
            )
        )
    for origin in (1, 2):
        f = forecast(e, origin)
        assert f.plan.exit is not None and f.plan.cutoff is not None
        refs = references(e, f.plan.exit, cutoff=f.plan.cutoff + pd.Timedelta(hours=4))
        frames.append(
            ReplayFrame(
                e.universe,
                f"SYN:EXIT:{origin}",
                f.plan.exit,
                refs,
                tuple(ExecutionOffer(e.universe, r) for r in refs),
            )
        )
    frames.append(
        ReplayFrame(e.universe, "SYN:CLOSE", pd.Timestamp("2020-08-03T20:00Z"), borrow_close=True)
    )
    return tuple(frames)


def test_policy_b_whole_pair_veto_even_at_physical_zero_and_no_sign_filter():
    a = engine()
    assert entry(a, forecast(a)) and entry(a, forecast(a, 2, True))
    assert all(q == 0 for _, q in a.book.balances)
    intent = rank_intent(forecast(a, 2, True, key="SYN:NEW"))
    assert Policy(a.universe, "B").veto(intent, a.sleeves)
    b = engine(policy="B")
    assert entry(b, forecast(b))
    first = b.sleeves
    assert not entry(b, forecast(b, 2, True))
    assert b.sleeves == first and b.rejections == ["POLICY_B_VIRTUAL_CONFLICT"]
    assert entry(b, forecast(b, 2, key="SYN:SAME"))
    # Another pair with no same-name conflict is accepted by the shared engine.
    c = engine(policy="B")
    assert entry(c, forecast(c))
    plan = forecast(c, 2).plan
    f = Forecast(c.universe, "SYN:OTHER", plan, (0.0, 3.0, 1.0, -3.0, -1.0))
    assert entry(c, f)


@pytest.mark.parametrize(
    "rate,expected", [(D(0), D(0)), (D(".005"), D(".034375")), (D(".03"), D(".20625"))]
)
def test_day_max_net_short_retained_after_offset_and_cover(rate, expected):
    e = engine(borrow=rate)
    assert entry(e, forecast(e)) and entry(e, forecast(e, 2, True))
    assert all(q == 0 for _, q in e.book.balances)
    assert e.borrow.maxima["2020-08-03"][NAMES[-1]] == 2475
    assert e.borrow.maxima["2020-08-03"][NAMES[0]] == 0
    # End first sleeve reopens the opposite physical short: each name day max 2475.
    exit_at(e, forecast(e).plan.exit)
    exit_at(e, forecast(e, 2).plan.exit, "SYN:EXIT2")
    at = pd.Timestamp("2020-08-03T20:00Z")
    assert e.borrow.close(e.book, at) == expected * 2
    cash = e.book.cash
    assert e.borrow.close(e.book, at) == expected * 2 and e.book.cash == cash
    assert e.book.cash == D(10000) - expected * 2
    with pytest.raises(ValueError):
        e.borrow.observe(e.book, {}, at)


def test_missing_observation_financing_is_not_zero_even_zero_rate():
    e = engine()
    assert entry(e, forecast(e))
    e.borrow.observe(e.book, {}, pd.Timestamp("2020-08-03T15:00Z"))
    assert e.borrow.close(e.book, pd.Timestamp("2020-08-03T20:00Z")) is None
    assert e.borrow.total is None and e.book.cash == 10000


def test_cost_scenarios_change_admission_path_not_posthoc_subtraction():
    zero, costly = engine(), engine(bps=5)
    assert entry(zero, forecast(zero)) and entry(costly, forecast(costly))
    assert entry(zero, forecast(zero, 2), price=D("102.02"))
    assert not entry(costly, forecast(costly, 2), price=D("102.02"))
    assert len(zero.sleeves) == 2 and len(costly.sleeves) == 1
    assert costly.rejections == ["POST_COST_100_CAP"]


def test_complete_24_fresh_replay_matrix_and_alternate_universe():
    e = engine(("FOX", "ZEN", "MAP", "ORB", "TIN"))
    script = script_for(e)
    rows = scenario_matrix(
        Permission(MODE), e.universe, script, D(10000), pd.Timestamp("2020-08-03T13:30Z")
    )
    assert len(rows) == 24 and len({r["friction_id"] for r in rows}) == 12
    assert len({r["trace_id"] for r in rows}) == 24
    assert len({r["script_id"] for r in rows}) == 1
    assert all(r["scope"] == "SYNTHETIC_ACCOUNTING_ONLY" and not r["research_ready"] for r in rows)
    assert all("POLICY_B_VIRTUAL_CONFLICT" in r["rejections"] for r in rows if r["policy"] == "B")
    a = replay(
        Permission(MODE),
        e.universe,
        script,
        "A",
        Frictions(e.universe),
        D(10000),
        pd.Timestamp("2020-08-03T13:30Z"),
    )
    b = replay(
        Permission(MODE),
        e.universe,
        script,
        "A",
        Frictions(e.universe),
        D(10000),
        pd.Timestamp("2020-08-03T13:30Z"),
    )
    assert a is not b and a.book is not b.book and a.ledger.trace_id == b.ledger.trace_id
