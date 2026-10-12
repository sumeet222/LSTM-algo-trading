"""Independent contextual accounting: open clocks, costs, actions and failed fills."""

from datetime import date
from decimal import Decimal as D
from decimal import localcontext

import pandas as pd
import pytest

from lstm_data.baseline_benchmarks import BuyAndHold, CashControl, OpeningOffer
from lstm_data.p3_accounting import ARITHMETIC, ActionInstruction
from lstm_data.p3_domain import (
    MODE,
    SHARE_BASIS,
    Frictions,
    Permission,
    PriceReference,
    UniverseSpec,
)
from lstm_data.p3_execution import ExecutionOffer


def universe():
    return UniverseSpec("SYN:BH:v1", ("FOX", "ZEN", "MAP", "ORB", "TIN"))


def benchmark(bps=5, first="2020-08-03", last="2020-08-04", cash=10000):
    u = universe()
    return BuyAndHold(
        u,
        Permission(MODE),
        Frictions(u, D(bps)),
        D(cash),
        "SYN:SEGMENT",
        first,
        last,
        allow_synthetic=True,
    )


def offers(b, at, prices=(100, 100, 100, 100, 100), fraction=D(1), outcome="FILLED"):
    return tuple(
        OpeningOffer(
            b.universe,
            ExecutionOffer(
                b.universe,
                PriceReference(
                    b.universe,
                    s,
                    D(p),
                    at,
                    at,
                    "SYN:OPEN:" + s + at.isoformat(),
                    "SYNTHETIC_MINUTE_EVENT",
                    b.engine.book.share_basis(s),
                ),
                fraction,
                outcome,
            ),
            "open",
            "SYNTHETIC",
        )
        for s, p in zip(b.universe.symbols, prices)
    )


@pytest.mark.parametrize("bps", [0, 2, 5, 10])
def test_hand_initial_allocation_and_cash_no_rebalance(bps):
    b = benchmark(bps)
    at = b.start
    assert b.attempt_entry(at, offers(b, at))
    with localcontext(ARITHMETIC):
        expected = D(10000) / (5 * (1 + D(bps) / 10000)) / 100
    assert all(q == expected for _, q in b.engine.book.balances)
    assert b.engine.book.cash >= 0 and abs(b.engine.book.cash) < D("1e-30")
    before = b.engine.book.balances
    assert not b.attempt_entry(
        pd.Timestamp("2020-08-04T13:30Z"),
        offers(b, pd.Timestamp("2020-08-04T13:30Z"), prices=(110,) * 5),
    )
    assert before == b.engine.book.balances
    assert b.scope == "LONG_ONLY_CONTEXTUAL_NOT_RISK_MATCHED"


def test_missing_first_open_entire_cash_next_session_only():
    b = benchmark()
    assert not b.attempt_entry(b.start, offers(b, b.start)[:-1])
    assert b.engine.book.cash == 10000 and all(q == 0 for _, q in b.engine.book.balances)
    next_at = pd.Timestamp("2020-08-04T13:30Z")
    assert b.attempt_entry(next_at, offers(b, next_at))
    fresh = benchmark()
    with pytest.raises(ValueError):
        fresh.attempt_entry(next_at, offers(fresh, next_at))
    assert fresh.engine.book.cash == 10000


def test_last_minute_normal_early_close_and_no_hourly_substitute():
    ordinary = benchmark(first="2020-08-03", last="2020-08-03", bps=0)
    early = benchmark(first="2020-11-27", last="2020-11-27", bps=0)
    assert ordinary.terminal == pd.Timestamp("2020-08-03T19:59Z")
    assert early.terminal == pd.Timestamp("2020-11-27T17:59Z")
    for b in (ordinary, early):
        assert b.attempt_entry(b.start, offers(b, b.start))
        assert b.attempt_terminal(b.terminal, offers(b, b.terminal))
        assert b.engine.book.cash == 10000 and all(q == 0 for _, q in b.engine.book.balances)
        assert b.valuation(b.terminal, ())["NAV"] == 10000
    with pytest.raises(ValueError):
        ordinary.attempt_terminal(ordinary.terminal - pd.Timedelta(minutes=1), ())
    with pytest.raises(ValueError):
        OpeningOffer(
            ordinary.universe, offers(ordinary, ordinary.start)[0].offer, "close", "SYNTHETIC"
        )


def test_split_dividend_paid_cash_no_reinvestment_no_double_count():
    b = benchmark(bps=0)
    assert b.attempt_entry(b.start, offers(b, b.start))
    close = pd.Timestamp("2020-08-03T20:00Z")
    b.close_session(close, tuple(o.offer.reference for o in offers(b, close)))
    boundary = pd.Timestamp("2020-08-04T13:30Z")
    split = ActionInstruction(
        b.universe,
        "SYN:SPLIT",
        b.universe.symbols[0],
        "SPLIT",
        boundary,
        b.start,
        D(2),
        SHARE_BASIS,
        post_split_basis="SYN:POST",
        fractional_policy="EXACT_FRACTIONAL_ASSUMPTION",
    )
    div = ActionInstruction(
        b.universe,
        "SYN:DIV",
        b.universe.symbols[0],
        "DIVIDEND",
        boundary,
        b.start,
        D(1),
        "SYN:POST",
        sequence=1,
        payable_date=date(2020, 8, 4),
    )
    b.apply_actions((split, div), boundary)
    assert b.engine.book.quantity(b.universe.symbols[0]) == 40 and b.engine.book.cash == 0
    marks = tuple(o.offer.reference for o in offers(b, boundary, prices=(50, 100, 100, 100, 100)))
    assert b.engine.book.valuation(marks, boundary)["accrual_equity"] == 10040
    claim = b.engine.book.claims[0]["claim_id"]
    b.engine.book.settle(claim, boundary)
    b.engine.book.settle(claim, boundary)
    assert b.engine.book.cash == 40 and b.engine.book.quantity(b.universe.symbols[0]) == 40
    assert b.engine.book.valuation(marks, boundary)["accrual_equity"] == 10040


def test_partial_initial_entry_keeps_fill_fee_then_causal_flatten():
    b = benchmark()
    rows = offers(b, b.start)
    bad = rows[:-1] + (
        OpeningOffer(
            b.universe,
            ExecutionOffer(b.universe, rows[-1].offer.reference, D(0), "REJECTED"),
            "open",
            "SYNTHETIC",
        ),
    )
    assert not b.attempt_entry(b.start, bad)
    assert any(q > 0 for _, q in b.engine.book.balances) and b.engine.book.execution_fees > 0
    with localcontext(ARITHMETIC):
        expected = D(10000) / (5 * (1 + D(5) / 10000)) * 4 * D(5) / 10000
    assert b.engine.book.execution_fees == expected
    next_at = b.start + pd.Timedelta(minutes=1)
    assert b.retry(next_at, offers(b, next_at))
    assert all(q == 0 for _, q in b.engine.book.balances)
    assert b.entry_aborted and not b.attempt_entry(pd.Timestamp("2020-08-04T13:30Z"), ())
    assert b.valuation(next_at, ())["NAV"] is None


def test_missing_terminal_no_phantom_sale_and_later_retry_not_segment_return():
    b = benchmark(first="2020-08-03", last="2020-08-03")
    assert b.attempt_entry(b.start, offers(b, b.start))
    before, fee = b.engine.book.balances, b.engine.book.execution_fees
    assert not b.attempt_terminal(b.terminal, ())
    assert before == b.engine.book.balances and b.engine.book.execution_fees == fee
    assert b.valuation(b.terminal, ())["NAV"] is None
    next_at = pd.Timestamp("2020-08-04T13:30Z")
    assert b.retry(next_at, offers(b, next_at))
    assert all(q == 0 for _, q in b.engine.book.balances)
    assert b.valuation(next_at, ())["NAV"] is None


def test_cash_context_permission_and_unavailable_open():
    u = universe()
    at = pd.Timestamp("2020-08-03T13:30Z")
    c = CashControl(u, Permission(MODE), D(10000), at, allow_synthetic=True)
    assert c.valuation(at)["cash"] == 10000 and c.valuation(at)["interest_credit"] == 0
    with pytest.raises(ValueError):
        CashControl(u, Permission("EMPIRICAL"), D(10000), at, allow_synthetic=True)
