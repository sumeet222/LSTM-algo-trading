"""Hand-computed invariants; no market access, simulator, labels or credentials."""

import hashlib
import json
from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal as D
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from lstm_data.corporate_actions import (
    Account,
    Action,
    Position,
    RawMark,
    SourceEvidence,
    apply_action,
    apply_actions,
    field_evidence,
    normalize_action,
    raw_price_from_split_adjusted,
    reconcile_source,
    retain_missing_exit,
    settle_dividend,
    snapshot,
)

ET = ZoneInfo("America/New_York")


def time(day=2, hour=9, minute=30):
    return datetime(2020, 3, day, hour, minute, tzinfo=ET)


def source(name="div"):
    return SourceEvidence(name, "a" * 64, time(10))


def account(q="100", cash="1000", opened=None, basis="before"):
    opened = opened or time(1)
    return Account(
        D(cash), (Position("AAPL", "physical-AAPL", D(q), opened, basis),), max(time(1), opened)
    )


def dividend(pay: date | None = date(2020, 3, 5), basis="before", sequence=1):
    return Action(source(), "AAPL", "DIVIDEND", time(), sequence, D(".77"), basis, payable_date=pay)


def split(ratio="4", sequence=0, policy: str | None = "INTEGER_ONLY"):
    return Action(
        source("split"),
        "AAPL",
        "SPLIT",
        time(),
        sequence,
        D(ratio),
        "before",
        "after",
        fractional_policy=policy,
    )


def mark(price, at=None, basis="before"):
    at = at or time()
    return RawMark("AAPL", D(price), at, at, basis, "fake-raw")


@pytest.mark.parametrize("quantity", ["100", "-100"])
def test_split_long_short_wealth_and_cash_invariant(quantity):
    # Short-sale proceeds are supplied in cash; the liability is signed shares × price.
    initial = account(quantity, "20000")
    before = snapshot(initial, (mark("100", time(1)),), time(1))
    after = apply_action(initial, split())
    result = snapshot(after, (mark("25", basis="after"),), time())
    assert after.positions[0].quantity == D(quantity) * 4
    assert after.cash == initial.cash and not after.claims
    assert before["accrual_equity"] == result["accrual_equity"]
    assert result["accrual_equity"] == (D(30000) if quantity == "100" else D(10000))
    assert apply_action(after, split()) is after


def test_fractional_policy_explicit_and_no_favorable_cash_in_lieu():
    initial = account(".5")
    with pytest.raises(ValueError, match="Fractional"):
        apply_action(initial, split("3"))
    after = apply_action(initial, split("3", policy="EXACT_FRACTIONAL_ASSUMPTION"))
    assert after.positions[0].quantity == D("1.5") and after.cash == D(1000)
    assert "EXACT_FRACTIONAL_ASSUMPTION" in after.assumptions
    with pytest.raises(ValueError, match="rounding"):
        split(policy=None)


@pytest.mark.parametrize(
    "quantity,amount,expected", [("100", "77", "11077"), ("-100", "-77", "-9077")]
)
def test_dividend_accrual_then_settlement_no_second_gain(quantity, amount, expected):
    initial = account(quantity)
    accrued = apply_action(initial, dividend())
    assert accrued.cash == D(1000)
    assert accrued.claims[0].eligible_shares == D(quantity)
    assert accrued.claims[0].signed_amount == D(amount)
    statement = snapshot(accrued, (mark("100"),), time())
    assert statement["accrual_equity"] == D(expected)
    assert statement["receivables"] == max(D(amount), D(0))
    assert statement["dividend_liabilities"] == max(-D(amount), D(0))
    paid = settle_dividend(accrued, accrued.claims[0].claim_id, time(5))
    assert paid.cash == D(1000) + D(amount)
    final = snapshot(paid, (mark("100", time(5)),), time(5))
    assert final["accrual_equity"] == statement["accrual_equity"]
    assert final["receivables"] == final["dividend_liabilities"] == 0
    assert settle_dividend(paid, paid.claims[0].claim_id, time(6)) is paid
    assert apply_action(paid, dividend()) is paid


@pytest.mark.parametrize("opened", [time(), time(hour=10)])
def test_opened_at_or_after_ex_boundary_no_entitlement(opened):
    # At a later state timestamp, a past event cannot be applied as if it were known then.
    if opened > time():
        with pytest.raises(ValueError, match="rewind"):
            apply_action(account(opened=opened), dividend())
    else:
        assert not apply_action(account(opened=opened), dividend()).claims


def test_zero_net_or_closed_position_has_no_virtual_sleeve_entitlements():
    assert not apply_action(account("0"), dividend()).claims
    empty = Account(D(1000), (), time(1))
    assert not apply_action(empty, dividend()).claims
    with pytest.raises(ValueError, match="net physical"):
        Account(D(0), (account("100").positions[0], account("-100").positions[0]), time(1))


def test_unknown_pay_date_persists_in_two_statements():
    accrued = apply_action(account(), dividend(None))
    view = snapshot(accrued, (mark("100"),), time())
    assert view["cash"] == 1000 and view["cash_only_equity"] == 11000
    assert view["accrual_equity"] == 11077 and view["paid_cash_scope"] == "INCOMPLETE"
    assert view["unknown_payment_claims"] == [accrued.claims[0].claim_id]
    with pytest.raises(ValueError, match="UNKNOWN_PAYMENT_DATE"):
        settle_dividend(accrued, accrued.claims[0].claim_id, time(9))
    assert accrued.claims[0].signed_amount == 77 and not accrued.claims[0].settled


def test_missing_exit_overnight_actions_and_permitted_marks():
    initial = account()
    outstanding = retain_missing_exit(initial, "AAPL", time(1, 16))
    assert outstanding.positions == initial.positions and outstanding.cash == initial.cash
    carried = apply_actions(outstanding, (dividend(basis="after"), split()))
    assert carried.positions[0].quantity == 400
    assert carried.claims[0].signed_amount == 308
    assert snapshot(carried, (), time())["accrual_equity"] is None
    with pytest.raises(ValueError, match="basis mismatch"):
        snapshot(carried, (mark("100", time(1)),), time())
    view = snapshot(carried, (mark("25", basis="after"),), time())
    assert view["accrual_equity"] == 11308
    assert view["unresolved_exits"] == ["AAPL"]
    with pytest.raises(ValueError, match="Future"):
        snapshot(carried, (mark("25", time(3), "after"),), time())


def test_order_and_rate_basis_fail_closed():
    after = apply_actions(account(), (dividend(basis="after"), split()))
    assert after.claims[0].eligible_shares == 400
    with pytest.raises(ValueError, match="share basis"):
        apply_actions(account(), (split(), dividend(basis="before")))
    with pytest.raises(ValueError, match="simultaneous"):
        apply_actions(account(), (split(), dividend(sequence=0)))
    first = apply_actions(account(), (dividend(sequence=0), split(sequence=1)))
    assert first.claims[0].eligible_shares == 100 and first.claims[0].signed_amount == 77
    assert first.positions[0].quantity == 400
    assert apply_actions(after, (split(), dividend(basis="after"))) == after
    assert apply_actions(account(), (split(), split())).positions[0].quantity == 400


@pytest.mark.parametrize("bad", ["0", "-1", "NaN", "Infinity"])
def test_invalid_split_ratios(bad):
    with pytest.raises(ValueError):
        split(bad)


@pytest.mark.parametrize("bad", ["NaN", "Infinity", "-.01"])
def test_invalid_dividend_rates(bad):
    with pytest.raises(ValueError):
        replace(dividend(), amount=D(bad))


def test_cash_settlement_date_order_and_identity_guards():
    accrued = apply_action(account(), dividend())
    with pytest.raises(ValueError, match="payable"):
        settle_dividend(accrued, accrued.claims[0].claim_id, time(3))
    with pytest.raises(ValueError, match="changed content"):
        apply_action(accrued, replace(dividend(), amount=D(".78")))
    with pytest.raises(ValueError, match="Positive raw"):
        replace(mark("100"), price_basis="SPLIT_ADJUSTED")
    assert raw_price_from_split_adjusted("25", "4") == 100
    with pytest.raises(ValueError):
        raw_price_from_split_adjusted("25", "0")
    with pytest.raises(ValueError, match="09:30"):
        replace(dividend(), boundary=time(hour=10))


def test_null_absent_fields_and_quarantined_acquirer_role():
    assert field_evidence({}, "payable_date")["presence"] == "ABSENT"
    assert field_evidence({"payable_date": None}, "payable_date")["presence"] == "NULL"
    native = {"id": "div", "acquirer_symbol": "AAPL", "acquiree_symbol": "OTHER"}
    with pytest.raises(ValueError, match="ACQUIRER_ROLE"):
        normalize_action(
            native,
            "cash_mergers",
            held_symbol="AAPL",
            source=source(),
            boundary=time(),
            sequence=0,
            share_basis="before",
        )


def test_reconciliation_preserves_native_null_absence_and_rejects_duplicate_ids():
    native = {
        "id": "div",
        "symbol": "AAPL",
        "ex_date": "2020-03-02",
        "rate": 0.77,
        "record_date": None,
    }
    payload = {"corporate_actions": {"cash_dividends": [native]}}
    result = reconcile_source(payload, "a" * 64, time(10))
    fields = result["events"][0]["fields"]
    assert result["rows"] == 1 and result["unique_ids"] == 1
    assert fields["record_date"]["presence"] == "NULL"
    assert fields["payable_date"]["presence"] == "ABSENT"
    assert fields["rate"]["value"] == 0.77
    assert fields["first_published_at"]["evidence"] == "UNKNOWN"
    assert native == {
        "id": "div",
        "symbol": "AAPL",
        "ex_date": "2020-03-02",
        "rate": 0.77,
        "record_date": None,
    }
    with pytest.raises(ValueError, match="Duplicate source"):
        reconcile_source(
            {"corporate_actions": {"cash_dividends": [native, native]}}, "a" * 64, time(10)
        )


def test_mapping_requires_valid_payable_date_and_rate_basis():
    native = {
        "id": "div",
        "symbol": "AAPL",
        "ex_date": "2020-03-02",
        "rate": 0.77,
        "payable_date": "",
    }
    with pytest.raises(ValueError):
        normalize_action(
            native,
            "cash_dividends",
            held_symbol="AAPL",
            source=source(),
            boundary=time(),
            sequence=0,
            share_basis="before",
        )
    with pytest.raises(ValueError, match="identity/basis"):
        replace(dividend(), share_basis="")


def test_bounded_existing_real_source_mapping_if_present():
    # Clean clones lack ignored vendor records: synthetic tests remain fully portable.
    root = Path(__file__).resolve().parents[1]
    path = root / "data/raw/alpaca/track_a_close_v1/actions-d7e39f2015b86602ac9c.json"
    if not path.exists():
        pytest.skip("Optional retained 116-action source unavailable; no download")
    manifest = json.loads(path.with_suffix(".manifest.json").read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest["sha256"]
    rows = json.loads(path.read_text())["corporate_actions"]
    assert {k: len(v) for k, v in rows.items()} == {
        "cash_dividends": 110,
        "forward_splits": 2,
        "cash_mergers": 4,
    }
    assert manifest["rows"] == 116
    reconciliation = reconcile_source(
        {"corporate_actions": rows},
        manifest["sha256"],
        datetime.fromisoformat(manifest["retrieved_at"]),
    )
    assert reconciliation["rows"] == reconciliation["unique_ids"] == 116
    assert len(reconciliation["missing_dates"]) == 4
    assert all(
        e["classification"] == "NO_SUPPORTED_ACQUIRER_HOLDINGS_TRANSFORMATION"
        for e in reconciliation["events"]
        if e["category"] == "cash_mergers"
    )
    missing = [r for r in rows["cash_dividends"] if r.get("payable_date") is None]
    assert len(missing) == 4
    for r in rows["forward_splits"] + missing:
        category = "forward_splits" if "new_rate" in r else "cash_dividends"
        boundary = datetime.combine(
            date.fromisoformat(r["ex_date"]), datetime.min.time(), ET
        ).replace(hour=9, minute=30)
        src = SourceEvidence(
            r["id"], manifest["sha256"], datetime.fromisoformat(manifest["retrieved_at"])
        )
        event = normalize_action(
            r,
            category,
            held_symbol=r["symbol"],
            source=src,
            boundary=boundary,
            sequence=0,
            share_basis="before",
            post_split_basis="after" if category == "forward_splits" else None,
            fractional_policy="INTEGER_ONLY" if category == "forward_splits" else None,
        )
        if category == "forward_splits":
            assert event.amount == (4 if r["symbol"] == "AAPL" else 3)
        else:
            assert event.payable_date is None
    assert all(r["acquirer_symbol"] in {"JNJ", "WMT"} for r in rows["cash_mergers"])
