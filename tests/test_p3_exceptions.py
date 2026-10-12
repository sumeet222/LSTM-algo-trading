"""Causal adverse paths: no phantom fills, terminal sale or historical authority."""

from dataclasses import replace
from decimal import Decimal as D

import pandas as pd
import pytest
from test_p3_financing import script_for
from test_p3_policy import NAMES, engine, entry, forecast, references

from lstm_data.p3_accounting import ActionInstruction
from lstm_data.p3_domain import MODE, SHARE_BASIS, Fill, Frictions, Permission, UniverseSpec
from lstm_data.p3_execution import ExecutionOffer
from lstm_data.p3_replay import ReplayFrame, replay


def offers(e, at, price=100, fraction=D(1), outcome="FILLED", cutoff=None):
    return tuple(
        ExecutionOffer(e.universe, r, fraction, outcome)
        for r in references(e, at, price=price, cutoff=cutoff)
    )


def seed_risk_book(e):
    at = pd.Timestamp("2020-08-03T14:00Z")
    target = tuple((s, D(5) if i == 0 else D(-5) if i == 4 else D(0)) for i, s in enumerate(NAMES))
    quotes = dict((r.symbol, r) for r in references(e, at))
    for o in e.book.orders_for_target(target, at, "SYN:SEED"):
        r = quotes[o.symbol]
        e.book.fill(
            Fill(
                e.universe,
                o.order_id + ":FILL",
                o,
                at,
                o.quantity,
                r,
                e.book.frictions.fee(o.quantity, r.price),
            )
        )


@pytest.mark.parametrize(
    "price,expected", [(D("109.9"), False), (D(110), False), (D("110.1"), True)]
)
def test_strict_emergency_1099_1100_1101(price, expected):
    e = engine(cash=1000)
    seed_risk_book(e)
    at = pd.Timestamp("2020-08-03T15:00Z")
    before = e.book.balances
    result = e.monitor(at, references(e, at, price=price), "SYN:RISK")
    assert result["G"] == price / 100 and result["emergency"] is expected
    assert e.book.balances == before
    assert bool(e.pending_target) is expected
    assert bool(e.halted_sessions) is expected


def test_emergency_partial_later_fill_no_session_restart():
    e = engine(bps=5)
    assert entry(e, forecast(e))
    at = pd.Timestamp("2020-08-03T15:00Z")
    # Equal-price long and short: equity stays 9997.525, gross=14850 (>110%).
    e.monitor(at, references(e, at, price=300), "SYN:TRIGGER")
    assert e.pending_reason == "EMERGENCY_GROSS" and len(e.sleeves) == 1
    original = e.book.balances
    fees = e.book.execution_fees
    with pytest.raises(ValueError):
        e.retry(at, offers(e, at), "SYN:SAME")
    canceled_at = at + pd.Timedelta(minutes=1)
    assert not e.retry(canceled_at, offers(e, canceled_at, 300, D(0), "CANCELED"), "SYN:CANCELED")
    assert e.book.balances == original and e.book.execution_fees == fees
    half = at + pd.Timedelta(minutes=2)
    assert not e.retry(half, offers(e, half, 300, D(".5"), "PARTIAL"), "SYN:HALF")
    assert e.book.quantity(NAMES[0]) == D("12.375") and len(e.sleeves) == 1
    assert e.book.execution_fees - fees == D("3.7125")
    final = at + pd.Timedelta(minutes=3)
    assert e.retry(final, offers(e, final, 300), "SYN:FLAT")
    assert all(q == 0 for _, q in e.book.balances) and not e.sleeves
    assert e.book.execution_fees - fees == D("7.425")
    assert not entry(e, forecast(e, 2))
    assert e.rejections[-1] == "EMERGENCY_SESSION_HALT"
    e.borrow.observe(e.book, {}, pd.Timestamp("2020-08-03T20:00Z"))
    e.borrow.close(e.book, pd.Timestamp("2020-08-03T20:00Z"))
    assert entry(e, forecast(e, day="2020-08-04", key="SYN:NEXT"))


def test_missing_1433_exit_1434_retry_and_terminal_incomplete():
    e = engine(bps=5)
    f = forecast(e)
    assert entry(e, f)
    assert f.plan.exit is not None
    before, cash, fee = e.book.balances, e.book.cash, e.book.execution_fees
    e.expire(f.plan.exit, (), "SYN:MISSING")
    assert e.book.balances == before and e.book.cash == cash and e.book.execution_fees == fee
    assert e.pending_reason == "MISSING_SCHEDULED_EXIT" and e.sleeves
    assert e.valuation(f.plan.exit, (), "SYN:TERMINAL")["NAV"] is None
    at = f.plan.exit + pd.Timedelta(minutes=1)
    assert f.plan.cutoff is not None
    # Nearest hourly quote is expressly ineligible for the minute retry.
    assert not e.retry(
        at, offers(e, at, cutoff=f.plan.cutoff + pd.Timedelta(hours=4)), "SYN:HOURLY"
    )
    assert e.book.balances == before
    later = at + pd.Timedelta(minutes=1)
    assert any(
        row["kind"] == "EXCEPTION" and row["payload"].get("reason") == "INELIGIBLE_REFERENCE"
        for row in e.ledger.export()
    )
    assert e.retry(later, offers(e, later), "SYN:MINUTE")
    assert not e.sleeves and e.book.cash == D("9995.05")
    assert e.book.execution_fees == D("4.95")
    exact = engine()
    f = forecast(exact)
    assert f.plan.exit is not None
    assert entry(exact, f)
    exact.expire(f.plan.exit, (), "SYN:MISSING")
    assert exact.retry(
        f.plan.exit + pd.Timedelta(minutes=1),
        offers(exact, f.plan.exit + pd.Timedelta(minutes=1)),
        "SYN:1434",
    )


def test_partial_pair_fill_flatten_no_retrospective_cancel():
    e = engine(bps=5)
    f = forecast(e)
    assert f.plan.entry is not None
    rows = references(e, f.plan.entry, cutoff=f.plan.cutoff)
    proposed = tuple(
        ExecutionOffer(e.universe, r, D(0), "HALT")
        if r.symbol == NAMES[-1]
        else ExecutionOffer(e.universe, r)
        for r in rows
    )
    assert e.enter(f, f.plan.entry, proposed, rows)
    assert e.book.cash == D("7523.7625") and e.book.execution_fees == D("1.2375")
    at = f.plan.entry + pd.Timedelta(minutes=1)
    assert e.retry(at, offers(e, at), "SYN:FAILED_PAIR_FLAT")
    assert e.book.cash == D("9997.525") and e.book.execution_fees == D("2.475")
    assert not e.sleeves and not e.book.outstanding


def test_overnight_early_close_holiday_next_session_preserves_actions():
    e = engine(bps=0)
    f = forecast(e, day="2020-11-25")
    assert entry(e, f)
    assert f.plan.exit is not None
    e.expire(f.plan.exit, (), "SYN:MISSING")
    for at in ("2020-11-26T14:30Z", "2020-11-27T18:01Z", "2020-11-28T14:30Z"):
        with pytest.raises(ValueError, match="OUTSIDE_RTH"):
            e.retry(pd.Timestamp(at), (), "SYN:CLOSED:" + at)
    early_open = pd.Timestamp("2020-11-27T14:30Z")
    assert not e.retry(early_open, (), "SYN:EARLY_MISSING")
    assert e.book.quantity(NAMES[-1]) == D("-24.75")
    nav = e.valuation(early_open, references(e, early_open), "SYN:OVERNIGHT")
    assert nav["NAV"] is None and "UNAPPROVED_OVERNIGHT_FINANCING" in nav["incomplete_reasons"]
    boundary = pd.Timestamp("2020-11-30T14:30Z")
    split = ActionInstruction(
        e.universe,
        "SYN:SPLIT",
        NAMES[-1],
        "SPLIT",
        boundary,
        early_open,
        D(4),
        SHARE_BASIS,
        post_split_basis="SYN:SPLIT_EPOCH",
        fractional_policy="EXACT_FRACTIONAL_ASSUMPTION",
    )
    dividend = ActionInstruction(
        e.universe,
        "SYN:DIV",
        NAMES[-1],
        "DIVIDEND",
        boundary,
        early_open,
        D(".5"),
        "SYN:SPLIT_EPOCH",
        sequence=1,
    )
    e.apply_actions((split, dividend), boundary)
    assert e.book.quantity(NAMES[-1]) == -99
    assert e.sleeves[0].quantities[-1][1] == -99 and e.book.cash == 10000
    assert e.book.claims[0]["amount"] == D("-49.5")
    next_minute = boundary + pd.Timedelta(minutes=1)
    assert e.retry(next_minute, offers(e, next_minute), "SYN:MONDAY_FLAT")
    assert all(q == 0 for _, q in e.book.balances) and e.book.claims[0]["amount"] == D("-49.5")
    assert e.valuation(next_minute, (), "SYN:FINAL")["NAV"] is None


def test_c01_mutate_future_exit_keep_entry_prefix_identical():
    e = engine(bps=5)
    script = script_for(e)
    past = script[:2]
    first_exit = script[2]
    variants = (
        first_exit,
        replace(first_exit, offers=()),
        replace(
            first_exit,
            offers=tuple(
                replace(o, reference=replace(o.reference, price=D(90))) for o in first_exit.offers
            ),
        ),
        replace(
            first_exit,
            offers=tuple(
                replace(
                    o,
                    reference=replace(
                        o.reference, available_at=first_exit.at + pd.Timedelta(minutes=1)
                    ),
                )
                for o in first_exit.offers
            ),
        ),
    )
    traces = []
    for future in variants:
        account = replay(
            Permission(MODE),
            e.universe,
            past + (future,),
            "A",
            Frictions(e.universe, D(5)),
            D(10000),
            pd.Timestamp("2020-08-03T13:30Z"),
        )
        traces.append(account.ledger.export())
    cutoff = past[-1].at.isoformat()
    prefixes = [[row for row in trace if row["at"] <= cutoff] for trace in traces]
    assert all(prefix == prefixes[0] for prefix in prefixes)
    assert len({str(t) for t in traces}) >= 3


def test_permission_clock_identity_ordering_and_unknown_coverage_guards():
    e = engine()
    script = script_for(e)
    with pytest.raises(ValueError):
        replay(
            Permission("REAL"), e.universe, script, "A", e.book.frictions, D(10000), script[0].at
        )
    with pytest.raises(ValueError):
        replace(script[0], universe=UniverseSpec("v2", NAMES[::-1]))
    with pytest.raises(ValueError):
        replay(
            Permission(MODE),
            e.universe,
            (script[0], replace(script[0], offers=())),
            "A",
            e.book.frictions,
            D(10000),
            pd.Timestamp("2020-08-03T13:30Z"),
        )
    one = replay(
        Permission(MODE),
        e.universe,
        (script[0],),
        "A",
        e.book.frictions,
        D(10000),
        pd.Timestamp("2020-08-03T13:30Z"),
    )
    two = replay(
        Permission(MODE),
        e.universe,
        (script[0], script[0]),
        "A",
        e.book.frictions,
        D(10000),
        pd.Timestamp("2020-08-03T13:30Z"),
    )
    assert one.ledger.trace_id == two.ledger.trace_id
    unknown = replace(script[0], action_coverage="UNKNOWN")
    held = replay(
        Permission(MODE),
        e.universe,
        (unknown,),
        "A",
        e.book.frictions,
        D(10000),
        pd.Timestamp("2020-08-03T13:30Z"),
    )
    assert not held.sleeves and held.book.cash == 10000
    assert held.rejections == ["RISK_OR_ACTION_INCOMPLETE"]
    boundary = pd.Timestamp("2020-08-04T13:30Z")
    action = ActionInstruction(
        e.universe, "SYN:A", NAMES[0], "DIVIDEND", boundary, script[0].at, D(1), SHARE_BASIS
    )
    frame = ReplayFrame(
        e.universe, "SYN:AMBIG", boundary, offers=offers(e, boundary), actions=(action,)
    )
    with pytest.raises(ValueError, match="SAME_TIME"):
        replay(
            Permission(MODE),
            e.universe,
            (frame,),
            "A",
            e.book.frictions,
            D(10000),
            pd.Timestamp("2020-08-03T13:30Z"),
        )


def test_missing_marks_and_nonpositive_equity_no_fake_leverage():
    e = engine(cash=1000)
    seed_risk_book(e)
    at = pd.Timestamp("2020-08-03T15:00Z")
    result = e.monitor(at, (), "SYN:MISSING_RISK")
    assert result["status"] == "INCOMPLETE" and result["G"] is None
    assert e.valuation(at, (), "SYN:NAV")["NAV"] is None
    bad = engine(cash=-1)
    result = bad.monitor(at, (), "SYN:BANKRUPT")
    assert result["status"] == "INVALID" and result["G"] is None
    assert bad.valuation(at, (), "SYN:INVALID_NAV")["NAV"] is None
