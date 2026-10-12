"""Independent monetary oracles for the synthetic physical adapter."""

from dataclasses import replace
from decimal import Decimal as D

import pandas as pd
import pytest

from lstm_data.clocks import execution_plan, session_clock
from lstm_data.p3_accounting import ActionInstruction, PhysicalBook
from lstm_data.p3_domain import (
    MODE,
    SHARE_BASIS,
    Fill,
    Forecast,
    Frictions,
    Permission,
    PriceReference,
    UniverseSpec,
)
from lstm_data.p3_events import EventLedger

NAMES = ("AA", "BB", "CC", "DD", "EE")
ALT = ("ZEN", "ORB", "FOX", "TIN", "MAP")


def stamp(value="2020-08-03T14:33:00Z"):
    return pd.Timestamp(value)


def make_book(names=NAMES, bps=5, cash=1000):
    u = UniverseSpec("toy-v1", names)
    p = Permission(MODE)
    ledger = EventLedger(u, p)
    return PhysicalBook(u, p, ledger, Frictions(u, D(bps)), D(cash), stamp("2020-08-03T13:30Z"))


def quote(book, symbol, at=None, price=100, **kw):
    at = stamp() if at is None else at
    return PriceReference(
        book.universe,
        symbol,
        D(price),
        at,
        at,
        "SYN:QUOTE:" + symbol + at.isoformat(),
        "SYNTHETIC_MINUTE_EVENT",
        book.share_basis(symbol),
        **kw,
    )


def trade(book, symbol, target, at=None, price=100, key="SYN:TRADE", fraction=D(1)):
    at = stamp() if at is None else at
    targets = tuple((s, D(target) if s == symbol else q) for s, q in book.balances)
    orders = book.orders_for_target(targets, at, key)
    assert len(orders) == 1
    order = orders[0]
    ref = quote(book, symbol, at, price)
    fill = Fill(
        book.universe,
        key + ":FILL",
        order,
        at,
        order.quantity * fraction,
        ref,
        book.frictions.fee(order.quantity * fraction, ref.price),
    )
    book.fill(fill)
    return fill


@pytest.mark.parametrize("names", [NAMES, ALT])
def test_long_cash_and_equity_hand_oracle(names):
    b = make_book(names)
    trade(b, names[0], 5)
    assert b.cash == D("499.75")
    assert b.quantity(names[0]) == 5
    assert b.valuation((quote(b, names[0]),), stamp())["accrual_equity"] == D("999.75")
    trade(b, names[0], 0, stamp("2020-08-03T18:33Z"), 110, "SYN:CLOSE")
    assert b.cash == D("1049.475")
    assert b.execution_fees == D(".525")


def test_short_partial_idempotence_and_no_virtual_fee():
    b = make_book()
    f = trade(b, NAMES[0], -5)
    assert b.cash == D("1499.75")
    before = b.ledger.trace_id
    b.fill(f)
    assert b.ledger.trace_id == before
    with pytest.raises(ValueError, match="DIVERGENT"):
        b.fill(replace(f, fee=D(0)))
    trade(b, NAMES[0], 0, stamp("2020-08-03T18:33Z"), 90, "SYN:COVER")
    assert b.cash == D("1049.525") and b.execution_fees == D(".475")
    p = make_book()
    trade(p, NAMES[0], 10, fraction=D(".5"))
    assert p.quantity(NAMES[0]) == 5 and p.outstanding[0][1] == 5
    assert p.execution_fees == D(".25")
    z = make_book()
    assert z.orders_for_target(z.balances, stamp(), "SYN:ZERO") == ()
    assert z.cash == 1000 and z.execution_fees == 0


def test_net_flip_external_notional():
    b = make_book()
    trade(b, NAMES[0], 5)
    trade(b, NAMES[0], -5, stamp("2020-08-03T15:33Z"), key="SYN:FLIP")
    assert b.cash == D("1499.25") and b.execution_fees == D(".75")


def test_split_dividend_missing_exit_on_alternate_symbols():
    b = make_book(ALT, bps=0)
    trade(b, ALT[0], -10)
    at = stamp("2020-08-04T13:30Z")
    split = ActionInstruction(
        b.universe,
        "SYN:SPLIT",
        ALT[0],
        "SPLIT",
        at,
        stamp(),
        D(4),
        SHARE_BASIS,
        post_split_basis="SYN:POST",
        fractional_policy="EXACT_FRACTIONAL_ASSUMPTION",
    )
    assert b.action(split)
    assert not b.action(split)
    assert b.quantity(ALT[0]) == -40 and b.cash == 2000
    assert b.valuation((quote(b, ALT[0], at, 25),), at)["accrual_equity"] == 1000
    dividend = ActionInstruction(
        b.universe, "SYN:DIV", ALT[0], "DIVIDEND", at, stamp(), D(".5"), "SYN:POST", sequence=1
    )
    b.action(dividend)
    assert b.claims[0]["amount"] == -20 and b.cash == 2000
    assert b.valuation((quote(b, ALT[0], at, 25),), at)["accrual_equity"] == 980
    with pytest.raises(ValueError):
        b.settle(b.claims[0]["claim_id"], at)
    b.retain_missing_exit(ALT[0], at)
    v = b.valuation((), at)
    assert v["accrual_equity"] is None and v["unresolved_exits"] == [ALT[0]]


def test_ledger_monotonic_duplicate_guard_and_provenance():
    b = make_book()
    a = b.ledger.record("SYN:MARK", stamp(), "MARK", {"x": 1})
    assert b.ledger.record("SYN:MARK", stamp(), "MARK", {"x": 1}) == a
    for key, at, payload, parent in [
        ("SYN:MARK", stamp(), {"x": 2}, None),
        ("SYN:OLD", stamp("2020-08-03T13:30Z"), {}, None),
        ("SYN:ORPHAN", stamp(), {}, "SYN:ABSENT"),
        ("SYN:REAL", stamp(), {"basis": "DOCUMENTED"}, None),
        ("SYN:FILLCLAIM", stamp(), {"provider_fill_claim": True}, None),
    ]:
        with pytest.raises(ValueError):
            b.ledger.record(key, at, "MARK", payload, parent)
    b.debit(D(2), stamp(), "SYN:DEBIT", {})
    b.debit(D(2), stamp(), "SYN:DEBIT", {})
    assert b.cash == 998


def test_contract_rejections_and_canonical_ties():
    b = make_book()
    f = Forecast(
        b.universe, "SYN:FORECAST", execution_plan(session_clock("2020-08-03"), 1), (1.0,) * 5
    )
    assert f.pair == (NAMES[0], NAMES[-1]) and f.constant
    with pytest.raises(ValueError):
        replace(f, basis="DOCUMENTED")
    with pytest.raises(ValueError):
        Permission("REAL_HISTORY").ensure()
    with pytest.raises(ValueError):
        UniverseSpec("bad", ("AA",) * 5)
    for changes in (
        {"available_at": None},
        {"price": D(0)},
        {"source_id": "REAL"},
        {"provider_fill_claim": True},
        {"source_version": "unknown"},
    ):
        with pytest.raises(ValueError):
            replace(quote(b, NAMES[0]), **changes)
    trade(b, NAMES[0], 5)
    future = quote(b, NAMES[0], stamp("2020-08-03T14:34Z"))
    assert b.valuation((future,), stamp())["accrual_equity"] is None
    assert b.valuation((quote(b, NAMES[0]),), stamp("2020-08-03T16:04Z"))["accrual_equity"] is None


def test_paid_dividend_cash_and_claim_once_preserves_equity():
    from datetime import date

    b = make_book()
    trade(b, NAMES[0], 5)
    boundary = stamp("2020-08-04T13:30Z")
    action = ActionInstruction(
        b.universe,
        "SYN:PAYABLE",
        NAMES[0],
        "DIVIDEND",
        boundary,
        stamp(),
        D(1),
        SHARE_BASIS,
        payable_date=date(2020, 8, 4),
    )
    b.action(action)
    marks = (quote(b, NAMES[0], boundary),)
    assert b.cash == D("499.75") and b.claims[0]["amount"] == 5
    assert b.valuation(marks, boundary)["accrual_equity"] == D("1004.75")
    b.settle(b.claims[0]["claim_id"], boundary)
    b.settle(b.claims[0]["claim_id"], boundary)
    assert b.cash == D("504.75") and b.claims[0]["settled"]
    assert b.valuation(marks, boundary)["accrual_equity"] == D("1004.75")


def test_basis_unknown_symbols_mismatched_universes_and_unsupported_action():
    b = make_book()
    with pytest.raises(ValueError, match="OUTSIDE_UNIVERSE"):
        b.quantity("OTHER")
    with pytest.raises(ValueError):
        PhysicalBook(
            b.universe,
            b.permission,
            b.ledger,
            Frictions(UniverseSpec("other", ALT)),
            D(1000),
            stamp(),
        )
    trade(b, NAMES[0], 5)
    wrong = replace(quote(b, NAMES[0]), share_basis="SYN:OTHER_EPOCH")
    assert b.valuation((wrong,), stamp())["accrual_equity"] is None
    with pytest.raises(ValueError):
        ActionInstruction(
            b.universe,
            "SYN:MERGER",
            NAMES[0],
            "CASH_MERGER",
            stamp("2020-08-04T13:30Z"),
            stamp(),
            D(5),
            SHARE_BASIS,
        )
    with pytest.raises(ValueError, match="TYPED_EVENT_PARENT"):
        b.ledger.record("SYN:PHANTOM", stamp(), "POSITION", {"quantity": 10})


def test_fill_requires_actual_rth_reference_and_no_ambiguous_action_order():
    b = make_book(bps=0)
    at = stamp("2020-08-04T13:30Z")
    target = tuple((s, D(5) if s == NAMES[0] else D(0)) for s in NAMES)
    o = b.orders_for_target(target, at, "SYN:O")[0]
    r = quote(b, NAMES[0], at)
    with pytest.raises(ValueError):
        Fill(b.universe, "SYN:MARK_FILL", o, at, D(5), replace(r, kind="MARK"), D(0))
    action = ActionInstruction(
        b.universe, "SYN:SIMULTANEOUS", NAMES[0], "DIVIDEND", at, stamp(), D(1), SHARE_BASIS
    )
    b.action(action)
    with pytest.raises(ValueError, match="SAME_TIME"):
        b.fill(Fill(b.universe, "SYN:F", o, at, D(5), r, D(0)))
    with pytest.raises(ValueError, match="RTH"):
        Fill(
            b.universe,
            "SYN:HOLIDAY",
            o,
            stamp("2020-11-26T14:30Z"),
            D(5),
            quote(b, NAMES[0], stamp("2020-11-26T14:30Z")),
            D(0),
        )
