"""Fabricated prices ONLY. No historical economic state or performance."""

import random
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from lstm_data.trading.track2.stage012.cohort_state import Cohort
from lstm_data.trading.track2.stage35.borrow_financing import BorrowEvidence, BorrowState
from lstm_data.trading.track2.stage35.common import RAW, D, Price
from lstm_data.trading.track2.stage35.completion_v2.settlement import (
    FinalBar,
    Request,
    V2Book,
    carry_to,
    liquidation_requests,
    settle,
    submit,
)
from lstm_data.trading.track2.stage35.completion_v2.tapes import (
    ActionEvent,
    DueEvent,
    RawObservation,
    apply_due,
    due_events,
)

T = datetime(2024, 1, 8, 15, 33, tzinfo=timezone.utc)


def quote(at=T - timedelta(minutes=1), value="100"):
    return Price(at, at, D(value), "FABRICATED_V2_FIXTURE")


def initial(qs=(("a", 10), ("b", -6)), cash="100000", at=T) -> V2Book:
    book = V2Book.funded(D(cash))
    assert isinstance(book, V2Book)
    book = book.mark("mark", "AAPL", quote(at - timedelta(minutes=1)), at - timedelta(minutes=1))
    cohorts = tuple(
        Cohort(
            k,
            "AAPL",
            q,
            abs(q) * 100,
            at - timedelta(minutes=3),
            at + timedelta(hours=4),
            at + timedelta(minutes=7),
            RAW,
            ("FABRICATED",),
        )
        for k, q in qs
    )
    result = book.reserve(
        "reserve",
        cohorts,
        quote(at - timedelta(minutes=1)),
        at - timedelta(seconds=30),
        BorrowEvidence(
            BorrowState.CONDITIONAL_SCENARIO,
            at - timedelta(days=1),
            "FIXTURE",
            D(".02"),
            "SYNTHETIC_FIXTURE",
        ),
    )
    assert isinstance(result, V2Book)
    return result


def order(qs=(("a", 10), ("b", -6)), at=T, role="ENTRY", key="order"):
    return submit(
        key,
        "account1",
        "S2C_RISK",
        "AAPL",
        tuple(Request(k, D(q), role) for k, q in qs),
        at - timedelta(minutes=1),
        at - timedelta(seconds=30),
        at,
        at + timedelta(minutes=7) if role == "ENTRY" else None,
        quote(at - timedelta(minutes=1)),
        D(100000),
        at - timedelta(minutes=1),
        True,
    )


def bar(value="100", at=T):
    return FinalBar(
        at,
        at + timedelta(minutes=1),
        at + timedelta(minutes=2),
        D(value),
        "FABRICATED_BAR",
        "ORIGINAL_OBSERVED",
    )


def test_expost_opposing_fill_then_old_exit():
    b = settle(initial(), order(), bar(), T + timedelta(minutes=2))
    assert b.positions[0].quantity == 4
    assert b.cash == D("99598.6000")
    assert sum(x.quantity for x in b.lots) == 4
    assert sum(x.fee for x in b.journal[-1].legs if x.internal) == 0
    end = T + timedelta(hours=4, minutes=3)
    b = settle(
        b, order((("a", -10),), end, "EXIT", "close"), bar("110", end), end + timedelta(minutes=2)
    )
    assert b.positions[0].quantity == -6
    b.reconcile()
    assert all(a.after == c.before for a, c in zip(b.journal, b.journal[1:]))


def test_zero_physical_nonzero_virtual_gross():
    b = settle(
        initial((("a", 10), ("b", -10))),
        order((("a", 10), ("b", -10))),
        bar(),
        T + timedelta(minutes=2),
    )
    assert b.cash == 100000 and b.positions[0].quantity == 0
    assert b.capacity(T + timedelta(minutes=2)).gross == 2000
    assert b.order_fees[0].paid == 0


def test_opposite_partials_cumulative_fee_and_permutation():
    qs = (("a", 10), ("b", -6), ("c", 4))
    b = initial(qs)
    first = settle(b, order(qs), bar("101"), T + timedelta(minutes=2), D(".5"))
    twin = settle(b, order(tuple(reversed(qs))), bar("101"), T + timedelta(minutes=2), D(".5"))
    assert first.digest() == twin.digest()
    remain = tuple((x.cohort.cohort_id, x.pending) for x in first.lots if x.pending)
    later = T + timedelta(minutes=3)
    final = settle(
        first, order(remain, later, key="order"), bar("99", later), later + timedelta(minutes=2)
    )
    assert final.positions[0].quantity == 8 and final.order_fees[0].paid == 1
    assert not any(x.pending for x in final.lots)
    final.reconcile()


def test_future_open_never_changes_submission_and_gap_not_rejected():
    b = initial((("a", 90),))
    o = order((("a", 90),))
    calm = settle(b, o, bar("100"), T + timedelta(minutes=2))
    gap = settle(b, o, bar("2000"), T + timedelta(minutes=2))
    assert calm.positions[0].quantity == gap.positions[0].quantity == 90
    assert gap.emergency_funding_debt > 0 and gap.cash == 0
    assert gap.journal[-1].cause == "OBSERVED_FILL_RISK_BREACH"
    gap.reconcile()
    assert liquidation_requests(gap, "AAPL")[0].delta == -90
    assert o.reference_price == 100 and o.net == 90


@pytest.mark.parametrize("status", ["MISSING", "HALTED", "CORRECTED"])
def test_unobservable_preserves_book(status):
    b = initial()
    before = b.digest()
    with pytest.raises(ValueError, match="UNRESOLVED"):
        settle(b, order(), replace(bar(), status=status), T + timedelta(minutes=2))
    assert b.digest() == before and sum(abs(x.pending) for x in b.lots) == 16


def test_borrow_physical_net_weekend_previous_mark():
    friday = datetime(2024, 1, 5, 20, 30, tzinfo=timezone.utc)
    b = initial((("a", 10), ("b", -16)), at=friday)
    b = settle(
        b, order((("a", 10), ("b", -16)), at=friday), bar(at=friday), friday + timedelta(minutes=2)
    )
    end = friday + timedelta(days=3)
    b = carry_to(b, "AAPL", end, D(".02"), end + timedelta(minutes=2), "carry")
    charge = D(600) * D(".02") * D(3) / D(365)
    assert sum(x.accrual for x in b.lots) == -charge
    assert friday.weekday() == 4 and end.weekday() == 0
    b.reconcile()
    with pytest.raises(ValueError, match="CARRY_PENDING"):
        carry_to(b, "AAPL", end + timedelta(days=1), None, end + timedelta(days=1), "bad")


def test_prior_volume_future_and_strict_borrow_fail():
    with pytest.raises(ValueError, match="VOLUME"):
        submit(
            "x",
            "a",
            "EQUAL",
            "AAPL",
            (Request("a", D(1)),),
            T - timedelta(minutes=1),
            T - timedelta(seconds=1),
            T,
            None,
            quote(),
            D(100),
            T,
            True,
        )
    with pytest.raises(ValueError, match="STRICT_LOCATE"):
        submit(
            "x",
            "a",
            "EQUAL",
            "AAPL",
            (Request("a", D(-1)),),
            T - timedelta(minutes=1),
            T - timedelta(seconds=1),
            T,
            None,
            quote(),
            D(100),
            T - timedelta(minutes=1),
            True,
            "STRICT_LOCATE",
            strict_locate_id="a made up ID",
        )


@pytest.mark.parametrize("role", ["RESIZE", "REBALANCE"])
def test_dynamic_disabled(role):
    with pytest.raises(ValueError, match="DYNAMIC"):
        order(role=role)


def test_randomized_conservation_and_cost_monotonicity():
    rng = random.Random(20261108)
    for n in range(30):
        qs = tuple((str(j), rng.choice((-1, 1)) * rng.randint(1, 20)) for j in range(5))
        b = initial(qs)
        o = order(qs, key=str(n))
        p = bar(str(rng.randint(60, 150)))
        cheap = settle(
            b,
            o,
            p,
            T + timedelta(minutes=2),
            half_spread_bps=D(0),
            impact_bps=D(0),
            minimum_fee=D(0),
        )
        costly = settle(b, o, p, T + timedelta(minutes=2))
        assert costly.nav() <= cheap.nav()
        assert sum(x.quantity for x in costly.lots) == costly.positions[0].quantity
        costly.reconcile()


def test_due_dividend_split_and_unknown_pay():
    b = settle(initial(), order(), bar(), T + timedelta(minutes=2))
    ex = T + timedelta(days=1)
    pay = ex + timedelta(days=3)
    event = ActionEvent(
        "div",
        "AAPL",
        "DIVIDEND",
        ex,
        ex - timedelta(days=1),
        "FIXTURE",
        D(1),
        pay,
        status="SYNTHETIC_KNOWN",
    )
    due = due_events((event,), T, pay, ())
    b = apply_due(b, due[0], quote(ex, "99"), ex)
    assert sum(x.accrual for x in b.lots) == 4
    b = apply_due(b, due[1], quote(pay, "99"), pay)
    assert not b.claims
    unknown = replace(event, action_id="unknown", effective=pay, pay_at=None)
    b = apply_due(b, DueEvent(pay, 1, "unknown", "DIVIDEND", "AAPL", unknown), quote(pay), pay)
    assert "PAY_DATE_UNKNOWN:unknown" in b.unresolved
    assert sum(c.amount for c in b.undated_claims) == 4
    b.reconcile()


@pytest.mark.parametrize("ratio", ["2", ".2"])
def test_split_reverse_transforms_virtual_and_pending(ratio):
    b = settle(initial(), order(), bar(), T + timedelta(minutes=2))
    at = T + timedelta(days=1)
    action = ActionEvent(
        "split",
        "AAPL",
        "SPLIT",
        at,
        at - timedelta(days=1),
        "FIXTURE",
        ratio=D(ratio),
        status="SYNTHETIC_KNOWN",
    )
    nav = b.nav()
    b = apply_due(
        b, DueEvent(at, 1, "split", "SPLIT", "AAPL", action), quote(at, str(D(100) / D(ratio))), at
    )
    assert b.positions[0].quantity == 4 * D(ratio) and b.nav() == nav
    b.reconcile()


def test_raw_adjusted_double_counting_and_invalid_ohlc():
    raw = RawObservation(
        "AAPL",
        T,
        T + timedelta(minutes=1),
        T + timedelta(minutes=2),
        D(100),
        D(101),
        D(99),
        D(100),
        D(1000),
        RAW,
        "h",
        "ORIGINAL_OBSERVED",
    )
    raw.validate()
    with pytest.raises(ValueError, match="BASIS"):
        replace(raw, basis="SPLIT_CONSISTENT").validate()
    with pytest.raises(ValueError, match="OHLCV"):
        replace(raw, high=D(95)).validate()


def test_gap_funding_claim_repaid_once_after_observed_liquidation():
    b = settle(initial((("a", 90),)), order((("a", 90),)), bar("2000"), T + timedelta(minutes=2))
    assert sum(v for _, v in b.funding_claims) == b.emergency_funding_debt > 0
    later = T + timedelta(minutes=3)
    b = settle(
        b,
        order((("a", -90),), later, "RISK_LIQUIDATION", "liq"),
        bar("2000", later),
        later + timedelta(minutes=2),
    )
    before = b.nav()
    point = quote(later + timedelta(minutes=3), "2000")
    b = b.settle_accrual("repay", "a", point, point.at)
    assert b.emergency_funding_debt == 0 and not b.funding_claims
    assert b.nav() == before and b.cash == before
    b.reconcile()
