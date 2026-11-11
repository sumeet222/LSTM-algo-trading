"""Fabricated economics plus separately verified primary/source contracts."""

from dataclasses import replace
from datetime import timedelta
from decimal import Decimal

import numpy as np
import pytest

from lstm_data.trading.track2.stage012.calendar_schedule import MarketClock
from lstm_data.trading.track2.stage35.final_backtest_v4.book import (
    Account,
    Lot,
    Order,
    Request,
    integer_cross,
)
from lstm_data.trading.track2.stage35.final_backtest_v4.protocol import Scenario
from lstm_data.trading.track2.stage35.final_backtest_v4.special import (
    CLOSE,
    EX,
    OGNQuote,
    distribution,
    entitled,
    observe,
    pay_cil,
    settle_whole,
)

D = Decimal
CLOCK = MarketClock("2021-01-01", "2022-01-01")


def quote(at=EX, value="37"):
    return OGNQuote(
        at, at + timedelta(minutes=1), at + timedelta(minutes=3), D(value), "FABRICATED_QUOTE"
    )


@pytest.mark.parametrize("mrk,ogn", [(100, 10), (-100, -10), (4, D(".4")), (-4, D("-.4"))])
def test_signed_regular_way_entitlements_and_basis(mrk, ogn):
    state = distribution((("one", D(mrk), D(1000) if mrk > 0 else D(0)),), CLOCK)
    assert state.lots[0].entitlement == ogn
    assert (
        state.lots[0].mrk_long_tax_basis + state.lots[0].ogn_long_tax_basis
        == state.lots[0].original_long_tax_basis
    )
    assert state.physical_whole == D(ogn).to_integral_value(rounding="ROUND_DOWN")
    assert entitled(EX - timedelta(days=5), None)
    assert not entitled(EX - timedelta(days=5), EX - timedelta(minutes=1))
    assert not entitled(EX, None)


@pytest.mark.parametrize("sessions,day", [(1, "2021-06-04"), (5, "2021-06-10"), (10, "2021-06-17")])
def test_fractional_account_net_cil_payment(sessions, day):
    state = distribution((("long", D(10), D(1000)), ("short", D(-6), D(0))), CLOCK, sessions)
    assert state.physical_whole == 0 and state.physical_fraction == D(".4")
    assert str(state.pay_at.date()) == day
    assert state.values(EX) is None
    q = quote()
    state = observe(state, q, q.available)
    with pytest.raises(ValueError):
        pay_cil(state, state.pay_at - timedelta(seconds=1))
    paid, amounts, total = pay_cil(state, state.pay_at)
    assert sum((v for _, v in amounts), D(0)) == total == D("14.80")
    assert paid.cil_paid
    with pytest.raises(ValueError):
        pay_cil(paid, state.pay_at)


def test_zero_net_does_not_make_external_stock_cash_or_fee():
    state = distribution((("a", D(100), D(10000)), ("b", D(-100), D(0))), CLOCK)
    assert state.physical_whole == state.physical_fraction == 0
    q = quote()
    state = observe(state, q, q.available)
    state, _, fee = settle_whole(
        state,
        quote(EX + timedelta(minutes=4)),
        q.available,
        EX + timedelta(minutes=7),
        known_reference=q,
    )
    state, amounts, total = pay_cil(state, state.pay_at)
    assert total == fee == 0 and sum((v for _, v in amounts), D(0)) == 0
    assert abs(amounts[0][1]) + abs(amounts[1][1]) == 740


def test_postclose_37_cannot_price_morning_and_tax_does_not_value_asset():
    state = distribution((("a", D(100), D(10000)),), CLOCK)
    morning = quote()
    state = observe(state, morning, morning.available, D(37))
    assert state.values(morning.available) is None
    assert state.lots[0].ogn_long_tax_basis == 477
    with pytest.raises(ValueError):
        replace(morning, conditional=True).validate(morning.available)
    close = OGNQuote(CLOSE, CLOSE, CLOSE + timedelta(minutes=2), D(37), "OWNER_APPROVED", True)
    state = observe(state, close, close.available, D(37))
    assert sum((v for _, v in state.values(close.available) or ()), D(0)) == 370


def test_ogn_partial_and_known_order_reference_survives_later_marks():
    state = distribution((("a", D(100), D(10000)),), CLOCK)
    original = quote()
    state = observe(state, original, original.available)
    fillquote = quote(EX + timedelta(minutes=4), "36")
    later = quote(EX + timedelta(minutes=5), "35")
    state = observe(state, later, later.available)
    state, cash, fee = settle_whole(
        state,
        fillquote,
        original.available,
        later.available,
        known_reference=original,
        external_capacity=D(4),
    )
    assert not state.whole_settled and sum((q for _, q in state.whole_fills), D(0)) == -4
    assert fee == 1 and cash
    with pytest.raises(ValueError):
        settle_whole(state, fillquote, original.available, later.available)


def test_whole_share_partial_external_and_fee_residuals():
    requests = tuple(Request(str(i), D(1), "ENTRY") for i in range(8))
    legs = integer_cross(requests, D(10), D("10.01"), D(8), D(".05"))
    assert all(
        item.quantity == item.quantity.to_integral_value() and item.fee >= 0 for item in legs
    )
    assert sum((item.fee for item in legs), D(0)) == D(".05")
    partial = integer_cross(requests, D(10), D("10.01"), D(3), D(1))
    assert sum((item.quantity for item in partial), D(0)) == 3
    assert all(item.quantity == 1 for item in partial)


def account_fixture():
    a = Account("EQUAL", "attainable", Scenario())
    a.prices[0] = D(100)
    a.marks_at[0] = 10
    a.lots = {
        "long": Lot("long", 0, 0, 240, 10, 1, 10, D(1), pending=D(10)),
        "short": Lot("short", 0, 0, 240, 10, -1, -6, D(1), pending=D(-6)),
    }
    a.refresh()
    return a


def test_physical_virtual_cash_plus10minus6_then_exit_and_carry():
    a = account_fixture()
    order = Order(
        "one",
        0,
        1,
        2,
        (Request("long", D(10), "ENTRY"), Request("short", D(-6), "ENTRY")),
        D(4),
        0,
        10,
    )
    a.fill(order, D(100), 5, 2)
    assert a.quantity[0] == 4
    assert a.lots["long"].quantity == 10 and a.lots["short"].quantity == -6
    exitorder = Order("two", 0, 241, 242, (Request("long", D(-10), "EXIT"),), D(-10), 240, None)
    a.fill(exitorder, D(110), 245, 242)
    assert a.quantity[0] == -6
    a.accrue(np.array([100 * 1000000 * 86400 * 3] + [0] * 19, dtype=np.int64), 250)
    assert a.borrow_paid == D(600) * D(".02") * 3 / 365
    assert a.restricted() == a.physical_basis[0] * 6
    a.reconcile()


def test_future_price_changes_fill_not_preceding_quantity_and_no_retro_cancel():
    a = account_fixture()
    b = account_fixture()
    o = Order(
        "same",
        0,
        1,
        2,
        (Request("long", D(10), "ENTRY"), Request("short", D(-6), "ENTRY")),
        D(4),
        0,
        10,
    )
    a.fill(replace(o), D(100), 5, 2)
    b.fill(replace(o), D(100000), 5, 2)
    assert a.quantity[0] == b.quantity[0] == 4
    assert b.cash < a.cash and b.capacity(10)[3] == "RISK_BREACH"


def test_ex_pay_once_and_archive_keeps_attribution():
    a = account_fixture()
    a.fill(
        Order(
            "o",
            0,
            1,
            2,
            (Request("long", D(10), "ENTRY"), Request("short", D(-6), "ENTRY")),
            D(4),
            0,
            10,
        ),
        D(100),
        5,
        2,
    )
    before = a.cash
    a.ex_dividend("div", 0, D(".25"), 100, 50, "OBSERVED_UNCORROBORATED")
    assert a.claim_total() == 1
    a.pay_dividend("div", 100)
    assert a.cash - before == 1 and not a.claims
    a.pay_dividend("div", 100)
    assert a.cash - before == 1
    a.reconcile()


def test_received_volume_and_bar_completion_are_hard_not_metadata():
    a = Account("EQUAL", "fabricated", Scenario())
    a.lots["l"] = Lot("l", 0, 0, 240, 10, 1, 1, D(1), pending=D(1))
    a.refresh()
    order = Order("order", 0, 2, 3, (Request("l", D(1), "ENTRY"),), D(1), 2, 10)
    with pytest.raises(ValueError, match="SOURCE_RECEIPT"):
        a.fill(order, D(100), 5, 3)
    with pytest.raises(ValueError, match="FUTURE_VOLUME"):
        a.fill(replace(order, prior_volume_available=3), D(100), 6, 3)
    assert a.cash == a.initial and a.quantity[0] == 0 and not a.events


def test_future_gap_cannot_change_submitted_order_or_create_internal_fees():
    a = Account("EQUAL", "fabricated", Scenario())
    a.lots["l"] = Lot("l", 0, 0, 240, 10, 1, 10, D(1), pending=D(10))
    a.lots["s"] = Lot("s", 0, 0, 240, 10, -1, -6, D(1), pending=D(-6))
    a.refresh()
    request = (Request("l", D(10), "ENTRY"), Request("s", D(-6), "ENTRY"))
    from lstm_data.trading.track2.stage35.final_backtest_v4.checkpoint import seal, unseal

    before = seal(a)
    results = []
    for price in (D(100), D(500)):
        copied = unseal(before)
        assert isinstance(copied, Account)
        order = Order("same-submission", 0, 2, 3, request, D(4), 2, 10)
        copied.fill(order, price, 6, 3)
        assert copied.quantity[0] == 4 and copied.commission == 1
        assert all(item["fee"] == 0 for item in copied.events[-1]["legs"] if item["internal"])
        copied.reconcile()
        results.append(copied.cash)
    assert results[0] != results[1]
    assert before == seal(a)


def test_special_tax_allocation_never_changes_constant_price_economic_equity():
    """Fabricated neutral decomposition, not a claim of actual ex-date equality."""
    state = distribution((("long", D(100), D(10000)),), CLOCK)
    q = quote(value="37")
    state = observe(state, q, q.available)
    values = state.values(q.available)
    assert values is not None
    before = D(100) * D(100)
    after = D(100) * D("96.30") + sum((v for _, v in values), D(0))
    assert before == after
    assert state.lots[0].mrk_long_tax_basis + state.lots[0].ogn_long_tax_basis == 10000


def test_descriptive_metrics_only_use_supplied_fabricated_nav():
    import pandas as pd

    from lstm_data.trading.track2.stage35.final_backtest_v4.analysis import metrics

    result = metrics(
        np.array([100000.0, 101000.0, 99000.0]), pd.date_range("2021-01-04", periods=3)
    )
    assert result["status"] == "OBSERVED_EXPLORATORY"
    assert abs(result["cumulative_return"] + 0.01) < 1e-12
    assert result["maximum_daily_drawdown"] < 0
    assert metrics(np.array([100000.0, np.nan]), pd.date_range("2021-01-04", periods=2))[
        "status"
    ].startswith("UNDEFINED")


def test_randomized_integer_cross_cash_fee_and_permutation_conservation():
    import random

    rng = random.Random(20261109)
    for case in range(200):
        requests = tuple(
            Request(str(i), D(rng.choice([-1, 1]) * rng.randint(1, 30)), "ENTRY")
            for i in range(rng.randint(2, 20))
        )
        net = sum((r.delta for r in requests), D(0))
        q = min(abs(net), D(rng.randint(0, 25))) * (1 if net > 0 else -1) if net else D(0)
        fee = D("1.03") if q else D(0)
        reference = D("37.123")
        external = D("37.17") if q > 0 else D("37.08")
        first = integer_cross(requests, reference, external, q, fee)
        shuffled = list(requests)
        rng.shuffle(shuffled)
        assert first == integer_cross(tuple(shuffled), reference, external, q, fee)
        assert sum((leg.quantity for leg in first), D(0)) == q
        assert sum((leg.fee for leg in first), D(0)) == fee
        assert all(leg.fee == 0 for leg in first if leg.internal)
        cash = sum((-leg.quantity * leg.price - leg.fee for leg in first), D(0))
        assert cash == -q * external - fee


def test_risk_cancellation_only_releases_unsent_target_never_resizes_held_lot():
    a = Account("EQUAL", "fabricated", Scenario())
    a.lots["lot"] = Lot("lot", 0, 0, 240, 10, 1, 10, D(1), pending=D(10))
    order = Order("first", 0, 2, 3, (Request("lot", D(10), "ENTRY"),), D(2), 2, 10)
    a.fill(order, D(100), 6, 3)
    assert a.lots["lot"].quantity == 2 and a.lots["lot"].pending == 8
    a.cancel_unsubmitted("lot", 7, "OBSERVED_CAP_BREACH")
    assert a.lots["lot"].quantity == 2 and a.lots["lot"].pending == 0
    a.pending[0] = Order("submitted", 0, 7, 8, (Request("lot", D(-2), "EXIT"),), D(-2), 7, None)
    with pytest.raises(ValueError, match="CANNOT_BE_RETRO_CANCELLED"):
        a.cancel_unsubmitted("lot", 8, "not permitted")
