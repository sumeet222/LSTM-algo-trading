"""Actual saved source evidence and bounded mocked HTTP failure/retry contracts."""

import json
from collections import Counter
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest
import requests

from lstm_data.trading.track2.stage35.completion_v3 import acquire
from lstm_data.trading.track2.stage35.completion_v3.actions import Truth, reconcile
from lstm_data.trading.track2.stage35.completion_v3.inventory import digest
from lstm_data.trading.track2.stage35.completion_v3.tapes import load_actions

ROOT = Path("trading/track2/stage35/completion_v3")


def response(code, data):
    result = requests.Response()
    result.status_code = code
    result._content = json.dumps(data).encode()
    return result


def test_bounded_429_retry_and_immutable_cached_reuse(tmp_path, monkeypatch):
    calls = []
    sleeps = []

    def get(*args, **kwargs):
        calls.append((args, kwargs))
        return response(429 if len(calls) == 1 else 200, {"corporate_actions": {}})

    monkeypatch.setattr(acquire.requests, "get", get)
    monkeypatch.setattr(acquire.time, "sleep", lambda seconds: sleeps.append(seconds))
    instance = acquire.Acquisition(tmp_path)
    r = instance.fetch("429", "https://example.invalid/actions", retry429=True)
    assert r["http_status"] == 200 and len(calls) == 2 and sleeps == [2]
    assert instance.fetch("429", "https://example.invalid/actions", retry429=True) == r
    assert len(calls) == 2


def test_auth_failure_no_retry_no_credentials_in_receipt(tmp_path, monkeypatch):
    secret = "test-credential-never-log-12345"
    monkeypatch.setenv("FINNHUB_API_KEY", secret)
    calls = []

    def get(*args, **kwargs):
        calls.append(1)
        return response(401, {"error": "invalid token: " + secret})

    monkeypatch.setattr(acquire.requests, "get", get)
    instance = acquire.Acquisition(tmp_path)
    r = instance.fetch("auth", "https://example.invalid/actions", {"token": secret}, retry429=True)
    assert r["status"] == "ACCESS_DENIED" and len(calls) == 1
    for p in tmp_path.rglob("*.json"):
        assert secret not in p.read_text()


def test_repeated_page_token_fails_not_duplicate_inventory(tmp_path, monkeypatch):
    (tmp_path / "ACTION_SOURCE_PLAN_V3.json").write_text(json.dumps({"symbols": ["AAPL"]}))
    payload = tmp_path / "page.json"
    payload.write_text(json.dumps({"next_page_token": "same", "corporate_actions": {}}))
    instance = acquire.Acquisition(tmp_path)
    calls = []

    def fetch(*args, **kwargs):
        calls.append(1)
        return {"http_status": 200, "payload_path": str(payload)}

    monkeypatch.setattr(instance, "fetch", fetch)
    with pytest.raises(ValueError, match="REPEATED_PROVIDER_PAGE_TOKEN"):
        instance.provider_probe()
    assert len(calls) == 2


def test_actual_cash_inventory_complete_fields_and_unique_ids():
    actions = load_actions()
    assert len(actions) == 298
    assert len({a.event_id for a in actions}) == len(actions)
    cash = [a for a in actions if a.action_type == "CASH_DIVIDEND"]
    assert len(cash) == 267
    assert all(
        a.amount is not None and a.ex_date and a.payable_date and not a.inferred_fields
        for a in cash
    )
    assert sum(a.payable_date.year > 2024 for a in cash if a.payable_date) == 2
    apple = next(a for a in cash if a.symbol == "AAPL" and a.ex_date == date(2024, 5, 10))
    assert str(apple.amount) == "0.25"
    assert apple.status == Truth.VERIFIED_PRIMARY
    assert {s.source_id.split(":")[0] for s in apple.sources} == {
        "APPLE_ISSUER",
        "ALPACA",
        "NASDAQ",
    }
    assert apple.record_date == date(2024, 5, 13) and apple.payable_date == date(2024, 5, 16)


def test_coverage_after_reconciliation_not_duplicate_provider_sum():
    coverage = json.loads((ROOT / "ACTION_COVERAGE_V3.json").read_text())
    assert len(coverage["ticker_years"]) == 80
    for row in coverage["ticker_years"]:
        if row["symbol"] == "AAPL":
            assert row["provider_cash_records"] == 4
    assert sum(row["provider_cash_records"] for row in coverage["ticker_years"]) == 267
    assert coverage["yield_proxy_security_years"] == 8
    unknown = {
        row["symbol"] for row in coverage["ticker_years"] if row["coverage_status"] == "UNKNOWN"
    }
    assert unknown == {"AMD", "AMZN"}
    zero = {a.symbol for a in load_actions() if a.status == Truth.NO_EVENT_VERIFIED}
    assert zero == {"TSLA", "BA"}


def test_merck_omitted_by_successful_provider_special_not_ordinary_imputed():
    actions = load_actions()
    special = [a for a in actions if a.action_type == "SPINOFF"]
    assert len(special) == 1 and special[0].symbol == "MRK"
    assert special[0].status == Truth.SPECIAL_ACTION_HOLD
    assert special[0].inferred_fields == ()
    assert "OGN" in special[0].spinoff_distribution_terms
    payload = json.loads((ROOT / "audits/payloads/network_v2_alpaca_0.json").read_text())
    assert "spin_offs" not in payload["corporate_actions"]


def test_conditional_inputs_not_upgraded_by_observed_reconciler():
    event = next(
        a for a in load_actions() if a.symbol == "AAPL" and a.action_type == "CASH_DIVIDEND"
    )
    with pytest.raises(ValueError, match="OBSERVED_RECONCILIATION_BEFORE_FALLBACK"):
        reconcile(
            (replace(event, status=Truth.ASSUMED_ORDINARY, inferred_fields=("payable_date",)),)
        )


def test_all_source_receipt_hashes_and_ignored_future_metadata():
    checked = 0
    for receipt_path in (ROOT / "audits").glob("*.receipt.json"):
        r = json.loads(receipt_path.read_text())
        if "payload_path" in r:
            assert digest(Path(r["payload_path"])) == r["stored_payload_sha256"]
            checked += 1
    assert checked >= 15
    assert all(
        (a.ex_date or a.effective_date or date.min) <= date(2024, 12, 31) for a in load_actions()
    )
    statuses = Counter(a.status.value for a in load_actions())
    assert statuses["SPECIAL_ACTION_HOLD"] == 1
