import random
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from lstm_data.trading.track2.stage012.cohort_state import Cohort
from lstm_data.trading.track2.stage35.accounting import Book
from lstm_data.trading.track2.stage35.borrow_financing import (
    BorrowEvidence,
    BorrowState,
    calendar_charge,
)
from lstm_data.trading.track2.stage35.common import RAW, D, Price
from lstm_data.trading.track2.stage35.corporate_actions import (
    Dividend,
    ex_dividend,
    financing,
    pay_dividend,
    split,
)

T = datetime(2024, 1, 8, 15, 33, tzinfo=timezone.utc)


def price(at=T, value="100", **kw):
    return Price(at, at, D(value), "synthetic-quote", **kw)


def evidence(at=T):
    return BorrowEvidence(
        BorrowState.CONDITIONAL_SCENARIO,
        at - timedelta(days=1),
        "synthetic-fixture",
        D(".1"),
        "SYNTHETIC_FIXTURE",
    )


def cohort(key, q, at=T):
    return Cohort(
        key,
        "AAPL",
        float(q),
        abs(float(q)) * 100,
        at - timedelta(minutes=3),
        at + timedelta(hours=3, minutes=57),
        at + timedelta(minutes=2),
        RAW,
        ("synthetic",),
    )


def reserved(qs=(("a", 10), ("b", -6)), at=T):
    b = Book.funded(D(100000))
    b = b.mark("mark", "AAPL", price(at - timedelta(seconds=2)), at - timedelta(seconds=2))
    return b.reserve(
        "reserve",
        tuple(cohort(k, q, at) for k, q in qs),
        price(at - timedelta(seconds=1)),
        at - timedelta(seconds=1),
        evidence(at),
    )


def test_opposing_vintages_exit_and_cash_golden():
    b = reserved()
    b = b.execute(
        "fill", "AAPL", (("a", D(10)), ("b", D(-6))), price(), T, D(100), D(4), D(1), evidence()
    )
    assert b.positions[0].quantity == 4 and b.cash == D(99599) and b.nav() == D(99999)
    end = T + timedelta(hours=4)
    b = b.execute(
        "old_exit",
        "AAPL",
        (("a", D(-10)),),
        price(end, "110"),
        end,
        D(110),
        D(-10),
        borrow=evidence(end),
    )
    assert b.positions[0].quantity == -6 and b.cash == D(100699) and b.nav() == D(100039)
    assert b.restricted() == D(660)
    b.reconcile()
    with pytest.raises(ValueError):
        b.execute(
            "dup",
            "AAPL",
            (("a", D(1)),),
            price(end, "110"),
            end,
            D(110),
            D(1),
            borrow=evidence(end),
        )


def test_zero_net_nonzero_virtual_gross_no_recycling():
    b = reserved((("a", 10), ("b", -10)))
    b = b.execute(
        "cross", "AAPL", (("b", D(-10)), ("a", D(10))), price(), T, D(100), D(0), borrow=evidence()
    )
    assert b.cash == D(100000) and b.positions[0].quantity == 0 and b.nav() == D(100000)
    assert b.capacity(T).gross == 2000 and b.capacity(T).own_available == 98000
    with pytest.raises(ValueError):
        b.execute("resize", "AAPL", (("a", D(1)),), price(), T, D(100), D(1), cause="REBALANCE")


def test_partial_mixed_fills_fees_atomic_and_permutation():
    initial = reserved((("a", 10), ("b", -6), ("c", 4)))
    left = initial.execute(
        "one",
        "AAPL",
        (("a", D(10)), ("b", D(-6)), ("c", D(4))),
        price(),
        T,
        D(101),
        D(4),
        D(1),
        evidence(),
    )
    right = initial.execute(
        "one",
        "AAPL",
        (("c", D(4)), ("b", D(-6)), ("a", D(10))),
        price(),
        T,
        D(101),
        D(4),
        D(1),
        evidence(),
    )
    assert left.digest() == right.digest()
    assert sum(lot_item.pending for lot_item in left.lots) == 4
    pending = tuple(
        (lot_item.cohort.cohort_id, lot_item.pending) for lot_item in left.lots if lot_item.pending
    )
    p = price(T + timedelta(seconds=1))
    complete = left.execute("two", "AAPL", pending, p, p.at, D(100), D(4), D(1), evidence())
    assert (
        complete.positions[0].quantity == 8
        and sum(lot_item.pending for lot_item in complete.lots) == 0
    )
    before = complete.digest()
    with pytest.raises(ValueError):
        complete.execute(
            "overfill", "AAPL", (("a", D(100)),), p, p.at, D(100), D(100), borrow=evidence()
        )
    assert complete.digest() == before
    with pytest.raises(ValueError):
        complete.mark("two", "AAPL", p, p.at)


def test_transfer_price_changes_attribution_not_economy():
    books = []
    for reference in ("100", "105"):
        b = reserved().execute(
            "fill",
            "AAPL",
            (("a", D(10)), ("b", D(-6))),
            price(value=reference),
            T,
            D(110),
            D(4),
            borrow=evidence(),
        )
        b = b.mark(
            "same_final_mark",
            "AAPL",
            price(T + timedelta(seconds=1), "110"),
            T + timedelta(seconds=1),
        )
        books.append(b)
    assert books[0].cash == books[1].cash and books[0].nav() == books[1].nav()
    assert books[0].lots[0].basis != books[1].lots[0].basis
    # Bar-open is not known contemporaneously for an INTERNAL transfer.
    late = Price(
        T, T + timedelta(minutes=2), D(100), "synthetic-bar", completed_at=T + timedelta(minutes=1)
    )
    with pytest.raises(ValueError, match="CONTEMPORANEOUS"):
        reserved().execute(
            "bad",
            "AAPL",
            (("a", D(10)), ("b", D(-6))),
            late,
            late.available_at,
            D(100),
            D(4),
            borrow=evidence(),
        )


def test_randomized_conservation():
    rng = random.Random(35)
    for n in range(50):
        a, b = rng.randint(1, 20), rng.randint(1, 20)
        net = D(a - b)
        book = reserved((("a", a), ("b", -b)))
        book = book.execute(
            "fill",
            "AAPL",
            (("a", D(a)), ("b", D(-b))),
            price(),
            T,
            D(100 + rng.randint(-5, 5)),
            net,
            D(1) if net else D(0),
            evidence(),
        )
        book.reconcile()
        assert book.positions[0].quantity == net
        assert sum(leg.fee for leg in book.journal[-1].legs) == (1 if net else 0)


def test_dividend_split_reverse_and_double_count_trap():
    b = reserved().execute(
        "fill", "AAPL", (("a", D(10)), ("b", D(-6))), price(), T, D(100), D(4), borrow=evidence()
    )
    ex = T + timedelta(days=1)
    pay = ex + timedelta(days=10)
    event = Dividend("div", "AAPL", D(1), T, ex, pay)
    b = ex_dividend(b, event, price(ex, "99"), ex)
    assert b.nav() == 100000 and sum(lot_item.accrual for lot_item in b.lots) == 4
    with pytest.raises(ValueError):
        ex_dividend(b, event, price(ex, "99"), ex)
    with pytest.raises(ValueError):
        pay_dividend(b, "div", price(ex, "99"), ex)
    b = pay_dividend(b, "div", price(pay, "99"), pay)
    assert b.cash == 99604 and b.nav() == 100000
    p = price(pay + timedelta(seconds=1), "49.5")
    b = split(b, "split", "AAPL", D(2), p, p.at, T)
    assert b.positions[0].quantity == 8 and b.nav() == 100000
    with pytest.raises(ValueError):
        b.mark("adjusted", "AAPL", price(p.at, "49.5", basis="SPLIT_CONSISTENT_20260331"), p.at)
    b = reserved((("a", 3),)).execute("buy", "AAPL", (("a", D(3)),), price(), T, D(100), D(3))
    p = price(T + timedelta(days=1), "200")
    b = split(b, "reverse", "AAPL", D(".5"), p, p.at, T, True)
    assert b.positions[0].quantity == 1 and b.cash == 99800 and b.nav() == 100000


def test_calendar_borrow_funding_unknown_and_recall():
    friday = datetime(2024, 1, 12, 20, 0, tzinfo=timezone.utc)
    monday = friday + timedelta(days=3)
    b = reserved((("s", -10),), friday).execute(
        "short",
        "AAPL",
        (("s", D(-10)),),
        price(friday),
        friday,
        D(100),
        D(-10),
        borrow=evidence(friday),
    )
    assert b.cash == 101000 and b.restricted() == 1000 and b.capacity(friday).own_available == 99000
    charge = calendar_charge(D(1000), D(".1"), friday, monday)
    b = b.accrue_borrow("borrow", "AAPL", price(monday), monday, D(".1"))
    assert sum(lot_item.accrual for lot_item in b.lots) == -charge and b.nav() == D(100000) - charge
    b = financing(b, "fund", "s", D(1000), D(".05"), friday, price(monday), monday)
    b = b.settle_accrual("pay", "s", price(monday), monday)
    b.reconcile()
    with pytest.raises(ValueError):
        b.accrue_borrow("unknown", "AAPL", price(monday), monday, None)
    unknown = BorrowEvidence(BorrowState.UNKNOWN, friday, "unknown")
    assert not unknown.permits(friday) and not evidence(friday).permits(friday)
    b = b.unresolved_event("recall", "AAPL", price(monday), monday, "BUY_IN_PRICE_MISSING")
    assert b.capacity(monday).status == "UNRESOLVED" and b.positions[0].quantity == -10


def test_shock_and_stale_and_cost_monotonicity():
    b = reserved((("s", -10),)).execute(
        "short", "AAPL", (("s", D(-10)),), price(), T, D(100), D(-10), borrow=evidence()
    )
    assert b.capacity(T + timedelta(minutes=6)).status == "STALE_MARK"
    at = T + timedelta(seconds=1)
    b = b.mark("shock", "AAPL", price(at, "2000"), at)
    assert b.capacity(at).status == "RISK_HOLD"
    with pytest.raises(ValueError):
        b.reserve("new", (cohort("new", 1),), price(at, "2000"), at, evidence())
    values = []
    for fee in (D(0), D(1), D(10)):
        b = reserved((("a", 10),)).execute(
            "buy", "AAPL", (("a", D(10)),), price(), T, D(100), D(10), fee
        )
        at = T + timedelta(hours=4)
        b = b.execute("exit", "AAPL", (("a", D(-10)),), price(at, "110"), at, D(110), D(-10), fee)
        values.append(b.nav())
    assert values == [D(100100), D(100098), D(100080)]


def test_simultaneous_old_exit_new_entry_different_external_price():
    b = reserved((("a", 10),)).execute(
        "old_entry", "AAPL", (("a", D(10)),), price(), T, D(100), D(10)
    )
    at = T + timedelta(hours=4)
    mark = price(at - timedelta(seconds=2), "110")
    b = b.mark("mark_before", "AAPL", mark, mark.at)
    definition = cohort("b", 6, at)
    reserve_point = price(at - timedelta(seconds=1), "110")
    b = b.reserve("new_reserve", (definition,), reserve_point, reserve_point.at)
    b = b.execute(
        "exit_and_entry",
        "AAPL",
        (("a", D(-10)), ("b", D(6))),
        price(at, "110"),
        at,
        D("109.5"),
        D(-4),
        D(1),
    )
    assert b.positions[0].quantity == 6 and b.nav() == D(100097)
    assert sum(lot_item.quantity for lot_item in b.lots) == 6
    assert sum(lot_item.fee for lot_item in b.journal[-1].legs) == 1
    assert sum(abs(lot_item.quantity) for lot_item in b.journal[-1].legs if lot_item.internal) == 12
    b.reconcile()


def test_duplicate_and_future_adjusted_price_atomic():
    b = reserved((("a", 10),))
    before = b.digest()
    future = Price(T, T + timedelta(seconds=1), D(100), "future")
    with pytest.raises(ValueError):
        b.execute("bad", "AAPL", (("a", D(10)),), future, T, D(100), D(10))
    assert b.digest() == before
    bad = replace(b.lots[0], basis=D(9), cash=D(1))
    with pytest.raises(AssertionError):
        replace(b, lots=(bad,)).reconcile()


def test_certified_borrow_instrument_quantity_and_expiry():
    cert = BorrowEvidence(
        BorrowState.CERTIFIED_OBSERVED,
        T,
        "actual-evidence-required",
        D(".1"),
        "EXTERNAL_OBSERVATION",
        "AAPL",
        D(10),
        T + timedelta(minutes=1),
    )
    assert cert.permits(T, ticker="AAPL", quantity=D(10))
    assert not cert.permits(T, ticker="COP", quantity=D(1))
    assert not cert.permits(T, ticker="AAPL", quantity=D(11))
    assert not cert.permits(T + timedelta(minutes=2), ticker="AAPL", quantity=D(1))
    assert not BorrowEvidence(
        BorrowState.CERTIFIED_OBSERVED, T, "missing-quantity", reviewer_kind="EXTERNAL_OBSERVATION"
    ).permits(T, ticker="AAPL")


def test_journal_before_after_checksums_match_committed_states():
    book = reserved((("a", 10),))
    before = book.digest()
    book = book.execute("fill", "AAPL", (("a", D(10)),), price(), T, D(100), D(10))
    assert book.journal[-1].before == before and book.journal[-1].after == book.digest()
    for a, b in zip(book.journal, book.journal[1:]):
        assert a.after == b.before


def test_fresh_mark_requires_known_borrow_carry_before_new_capital():
    book = reserved((("s", -10),)).execute(
        "short", "AAPL", (("s", D(-10)),), price(), T, D(100), D(-10), borrow=evidence()
    )
    at = T + timedelta(minutes=1)
    book = book.mark("fresh", "AAPL", price(at), at)
    assert book.capacity(at).status == "CARRY_PENDING"
    with pytest.raises(ValueError):
        book.reserve("new", (cohort("new", 1),), price(at), at, evidence())
    book = book.accrue_borrow("explicit_rate", "AAPL", price(at), at, D(".1"))
    assert book.capacity(at).status == "READY"
