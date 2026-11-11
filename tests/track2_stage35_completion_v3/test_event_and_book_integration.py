"""Fabricated economics; separate claim/share kernel has no performance API."""

from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from lstm_data.trading.track2.stage012.calendar_schedule import MarketClock
from lstm_data.trading.track2.stage012.cohort_state import Cohort
from lstm_data.trading.track2.stage35.accounting import Lot, Physical
from lstm_data.trading.track2.stage35.common import RAW, Price
from lstm_data.trading.track2.stage35.completion_v2.settlement import V2Book
from lstm_data.trading.track2.stage35.completion_v3.actions import Action, Evidence, Truth
from lstm_data.trading.track2.stage35.completion_v3.book_bridge import apply_action
from lstm_data.trading.track2.stage35.completion_v3.engine import EconomicReplayV3
from lstm_data.trading.track2.stage35.completion_v3.event_ledger import (
    ClaimShareBook,
    ShareLot,
    after_bar,
    verify_journal,
)
from lstm_data.trading.track2.stage35.completion_v3.tapes import (
    checkpoint,
    compile_events,
    daily_batches,
    midnight,
)

D = Decimal
T = datetime(2024, 1, 5, 21, 0, tzinfo=timezone.utc)
S = Evidence("SYNTHETIC:fixture", "synthetic://fabricated-dividend", "f" * 64, "one", T.isoformat())


def dividend(**kwargs):
    return replace(
        Action(
            "fake",
            "AAPL",
            "CASH_DIVIDEND",
            date(2024, 1, 8),
            date(2024, 1, 8),
            date(2024, 1, 12),
            D(1),
            Truth.ASSUMED_ORDINARY,
            (S,),
        ),
        **kwargs,
    )


def endowed(qs=(D(10), D(-6)), symbol="AAPL"):
    return ClaimShareBook(tuple(ShareLot(str(n), symbol, q) for n, q in enumerate(qs)))


def fabricated_book(qs=(D(10), D(-6))) -> V2Book:
    lots = tuple(
        Lot(
            Cohort(
                str(n),
                "AAPL",
                float(q),
                float(abs(q) * 100),
                T - timedelta(hours=1),
                T + timedelta(days=1),
                T + timedelta(minutes=10),
                RAW,
                ("FABRICATED",),
            ),
            quantity=q,
            basis=D(100),
            cash=-q * 100,
        )
        for n, q in enumerate(qs)
    )
    net = sum(qs, D(0))
    book = V2Book(
        D(100000),
        D(100000) - net * 100,
        lots,
        (Physical("AAPL", net, D(100), borrow_asof=T),),
        (("AAPL", Price(T, T, D(100), "FABRICATED_PRICE")),),
    )
    book.reconcile()
    return book


def test_long_short_ex_pay_exact_once_and_truth():
    action = dividend()
    tape = compile_events((action,), date(2024, 1, 1), date(2024, 1, 31))
    b = endowed()
    ex, pay = tape
    b = b.apply(
        action,
        ex.effective_at,
        ex.available_at,
        ex.available_at,
        modeled_retrospective=True,
        due_at=pay.effective_at,
    )
    assert b.physical_shares("AAPL") == 4
    assert sum((c.signed_amount for c in b.claims), D(0)) == 4
    b = b.pay(action.event_id, pay.effective_at, pay.available_at, pay.available_at)
    assert b.cash_distribution_only == 4 and not b.claims
    assert b.pay(action.event_id, pay.effective_at, pay.available_at, pay.available_at) == b
    assert (
        b.apply(
            action, ex.effective_at, ex.available_at, ex.available_at, modeled_retrospective=True
        )
        == b
    )
    verify_journal(b)
    assert all(j.truth == Truth.ASSUMED_ORDINARY.value for j in b.journal)
    assert not hasattr(b, "nav") and not hasattr(b, "realized")


def test_unknown_pay_and_post2024_claim_remain_without_price_read():
    action = dividend(ex_date=date(2024, 12, 16), payable_date=date(2025, 1, 8))
    assert action.ex_date is not None
    at = midnight(action.ex_date)
    b = endowed().apply(
        action, at, at, at, modeled_retrospective=True, due_at=midnight(date(2025, 1, 8))
    )
    assert b.claims and b.cash_distribution_only == 0
    with pytest.raises(ValueError):
        b.pay(
            action.event_id,
            midnight(date(2024, 12, 31)),
            midnight(date(2024, 12, 31)),
            midnight(date(2024, 12, 31)),
        )
    b = endowed().apply(replace(action, payable_date=None), at, at, at, modeled_retrospective=True)
    assert b.unresolved and b.claims[0].due_at is None


@pytest.mark.parametrize("ratio", [D(2), D(".2"), D(4)])
def test_split_virtual_physical_and_claim_dollars_unchanged(ratio):
    action = dividend(action_type="SPLIT", amount=None, split_ratio_new_old=ratio)
    b = endowed()
    at = midnight(date(2024, 1, 8))
    b = b.apply(action, at, at, at, modeled_retrospective=True)
    assert b.physical_shares("AAPL") == D(4) * ratio
    verify_journal(b)
    if ratio == D(".2"):
        assert b.unresolved  # preserve .8 claim; no invented CIL price


def test_ognoffspring_unpriced_hold_and_no_invented_cash():
    action = dividend(
        symbol="MRK",
        action_type="SPINOFF",
        sub_type="OGN_PER_MRK_0.1",
        amount=None,
        special=True,
        status=Truth.SPECIAL_ACTION_HOLD,
    )
    at = midnight(date(2024, 1, 8))
    b = endowed(symbol="MRK").apply(action, at, at, at, modeled_retrospective=True)
    assert sum((c.signed_amount for c in b.claims), D(0)) == D(".4")
    assert all(c.asset == "OGN_UNPRICED" for c in b.claims)
    assert b.unresolved and b.cash_distribution_only == 0


def test_correction_and_pit_not_silently_accepted():
    action = dividend()
    at = midnight(date(2024, 1, 8))
    with pytest.raises(PermissionError):
        endowed().apply(action, at, at, at, modeled_retrospective=False)
    b = endowed().apply(action, at, at, at, modeled_retrospective=True)
    with pytest.raises(ValueError, match="CORRECTED"):
        b.apply(replace(action, amount=D(2)), at, at, at, modeled_retrospective=True)


@pytest.mark.parametrize("rate", [D(".01"), D(".02"), D(".05")])
def test_friday_monday_physical_net_short_borrow(rate):
    end = T + timedelta(days=3)
    b = endowed((D(6), D(-10))).carry("AAPL", T, end, D(100), T, end, rate, "fake-source")
    assert b.carry_expense_only == D(4) * 100 * rate * D(3) / 365
    assert (
        endowed().carry("AAPL", T, end, D(100), T, end, rate, "fake-source").carry_expense_only == 0
    )


def test_missing_carry_rate_not_zero_and_future_mark_rejected():
    end = T + timedelta(days=3)
    b = endowed((D(-4),)).carry("AAPL", T, end, D(100), T, end, None, "fake-source")
    assert b.unresolved and b.carry_expense_only == 0
    with pytest.raises(ValueError, match="FRONTIER"):
        endowed().carry("AAPL", T, end, D(100), end, end, D(".02"), "fake-source")


@pytest.mark.parametrize("minutes", [1, 2, 5])
def test_bar_completion_receipt_stress_distinct(minutes):
    complete, available = after_bar(T, minutes)
    assert complete == T + timedelta(minutes=1)
    assert available == complete + timedelta(minutes=minutes)


def test_daily_resume_and_changed_cursor_fail(tmp_path):
    tape = compile_events((dividend(),), date(2024, 1, 1), date(2024, 1, 31))
    batches = list(daily_batches(tape))
    assert len(batches) == 2
    assert tuple(e for b in daily_batches(tape, tape[0].event_id) for e in b) == tape[1:]
    checkpoint(tmp_path / "check.json", tape[0], {"source": "sealed"}, "statehash")
    with pytest.raises(ValueError):
        checkpoint(tmp_path / "check.json", tape[0], {"source": "changed"}, "statehash")
    with pytest.raises(ValueError):
        list(daily_batches(tape, "unknown"))


def test_synthetic_v2_nonprice_ex_pay_conserves_attribution():
    b = fabricated_book()
    tape = compile_events((dividend(),), date(2024, 1, 1), date(2024, 1, 31))
    b = apply_action(b, tape[0], tape[0].available_at)
    assert sum((c.amount for c in b.claims), D(0)) == 4
    assert b.nav() == 100004
    before = b.cash
    b = apply_action(b, tape[1], tape[1].available_at)
    assert b.cash - before == 4 and not b.claims and b.nav() == 100004
    b.reconcile()
    assert b.journal[0].after == b.journal[1].before
    assert apply_action(b, tape[1], tape[1].available_at) == b


@pytest.mark.parametrize("ratio", [D(2), D(".2"), D(4)])
def test_v2_split_unit_conversion_keeps_old_mark_stale(ratio):
    b = fabricated_book()
    split = dividend(action_type="SPLIT", amount=None, split_ratio_new_old=ratio)
    e = compile_events((split,), date(2024, 1, 8), date(2024, 1, 8))[0]
    b = apply_action(b, e, e.available_at)
    assert b.nav() == 100000 and b.positions[0].quantity == D(4) * ratio
    assert dict(b.marks)["AAPL"].at == T
    assert dict(b.marks)["AAPL"].value == D(100) / ratio
    b.reconcile()


def test_actual_action_evidence_cannot_be_relabelled_synthetic():
    action = replace(
        dividend(),
        sources=(replace(S, source_id="ALPACA:actual", endpoint="https://data.alpaca.markets"),),
    )
    e = compile_events((action,), date(2024, 1, 8), date(2024, 1, 8))[0]
    with pytest.raises(PermissionError):
        apply_action(fabricated_book(), e, e.available_at)


def test_integrated_synthetic_due_and_weekend_carry():
    engine = EconomicReplayV3(
        "test", "S2C_RISK", fabricated_book((D(-4),)), MarketClock("2024-01-01", "2024-02-01")
    )
    engine.last_processed = T
    tape = compile_events((dividend(),), date(2024, 1, 8), date(2024, 1, 12))
    engine.replay(tape)
    engine.book.reconcile()
    assert engine.action_receipts and not engine.book.claims
    assert any("CARRY" in j.journal_id for j in engine.book.journal)
    assert any(
        dict(j.details).get("truth") == Truth.ASSUMED_ORDINARY.value for j in engine.book.journal
    )


def test_checkpoint_roundtrip_resumes_claim_payment_without_repeat(tmp_path):
    from lstm_data.trading.track2.stage35.completion_v3.restart import restore, save

    clock = MarketClock("2024-01-01", "2024-02-01")
    engine = EconomicReplayV3("fixture", "S2C_RISK", fabricated_book(), clock)
    tape = compile_events((dividend(),), date(2024, 1, 1), date(2024, 1, 31))
    engine.replay(tape[:1])
    path = tmp_path / "day1.json"
    file_hash = save(engine, path, {"source": "FABRICATED_TAPE_ONLY"})
    resumed = restore(path, file_hash, {"source": "FABRICATED_TAPE_ONLY"}, clock)
    resumed.replay(tape[1:])
    engine.replay(tape[1:])
    assert resumed.book.digest() == engine.book.digest()
    assert resumed.book.journal == engine.book.journal
    with pytest.raises(ValueError, match="BINDING"):
        restore(path, file_hash, {"source": "changed"}, clock)
    path.write_text(path.read_text() + " ")
    with pytest.raises(ValueError, match="HASH"):
        restore(path, file_hash, {"source": "FABRICATED_TAPE_ONLY"}, clock)


def test_checkpoint_rejects_untrusted_class():
    from lstm_data.trading.track2.stage35.completion_v3.restart import decode

    with pytest.raises(ValueError, match="UNTRUSTED_CHECKPOINT_CLASS"):
        decode({"$class": "os.system", "fields": {}})


def test_gap_in_carry_keeps_exact_missing_interval():
    end = T + timedelta(days=1)
    b = endowed((D(-4),)).carry("AAPL", T, end, D(100), T, end, D(".02"), "fixture")
    with pytest.raises(ValueError, match="MISSING_SEGMENT"):
        b.carry(
            "AAPL",
            end + timedelta(days=1),
            end + timedelta(days=2),
            D(100),
            T,
            end + timedelta(days=2),
            D(".02"),
            "fixture",
        )
