"""Research-critical rank and transport guards without live requests."""

import json
from pathlib import Path

import pytest
import requests

from lstm_data.alpaca import ENDPOINT, DataAccessError
from lstm_data.config import digest
from lstm_data.greedy_screen import (
    Candidate,
    GreedyScan,
    GreedyTransport,
    gap_status,
    historical_order,
)
from lstm_data.remediation_transport import StorageLimit


def candidate(rank=1, ticker="AMZN", sector="Consumer Discretionary", qualified=True):
    return Candidate(rank, ticker, ticker, sector, qualified)


def test_rank_facts_are_fixed_and_class_exclusions_not_current(tmp_path):
    path = Path(
        "reports/data_audit/ta_sp500_greedy_2026-10-13_013143/ranked_formation_constituents.csv"
    )
    # The reproducible source-fact fixture is an explicitly reviewed local report.
    if not path.exists():
        pytest.skip("Historical source-fact report is not supplied in this checkout")
    order = historical_order(path, digest(path))
    assert [r["name"] for r in order[:3]] == ["Microsoft Corp.", "Apple, Inc.", "Amazon.com, Inc."]
    assert len(order) == 500
    assert all(r["snapshot"] == "2020-03-31" for r in order)
    with pytest.raises(ValueError, match="SHA_CHANGED"):
        historical_order(path, "0" * 64)


def test_sector_skip_failure_advances_and_five_sector_stop():
    scan = GreedyScan()
    assert (
        scan.visit(candidate(1, "MSFT", "Technology"), "NOT_MEASURED") == "SKIP_REPRESENTED_SECTOR"
    )
    assert scan.visit(candidate(3), "MAJOR_GAP_FAIL") == "MAJOR_GAP_FAIL"
    for rank, ticker, sector in [
        (4, "FB", "Communication Services"),
        (5, "BRK.B", "Financials"),
        (7, "JNJ", "Health Care"),
        (10, "PG", "Consumer Staples"),
    ]:
        assert (
            scan.visit(candidate(rank, ticker, sector), "NATIVE_CLEAN", mandatory_measured=True)
            == "PROVISIONAL_ACCEPT"
        )
    assert len(scan.selected) == len(scan.sectors) == 5
    with pytest.raises(ValueError, match="ALREADY_STOPPED"):
        scan.visit(candidate(11), "NATIVE_CLEAN", mandatory_measured=True)


def test_unverified_membership_and_clean_unmeasured_fail_closed():
    scan = GreedyScan()
    assert (
        scan.visit(candidate(qualified=False), "NATIVE_CLEAN", mandatory_measured=True)
        == "FORMATION_OR_MAPPING_HOLD"
    )
    assert scan.stopped and scan.selected == ["AAPL"]
    scan = GreedyScan()
    assert scan.visit(candidate(), "NATIVE_CLEAN") == "MANDATORY_EVIDENCE_HOLD"
    assert scan.stopped


def test_minor_before_clean_requires_human_no_cleanup():
    scan = GreedyScan()
    assert scan.visit(candidate(3), "MINOR_GAP_CANDIDATE_ONLY") == "MINOR_GAP_CANDIDATE_ONLY"
    assert (
        scan.visit(candidate(16, "HD"), "NATIVE_CLEAN", mandatory_measured=True)
        == "EARLIER_MINOR_VS_LATER_CLEAN_HUMAN_DECISION"
    )
    assert scan.stopped and scan.selected == ["AAPL"]


def test_major_terminal_and_positive_pilot_not_qualification():
    assert gap_status([dict(longest_gap_half_hours=3, missing=3)]) == "MAJOR_GAP_FAIL"
    assert (
        gap_status([dict(longest_gap_half_hours=1, missing=1, terminal_stub_missing=True)])
        == "MINOR_GAP_CANDIDATE_ONLY"
    )
    assert (
        gap_status([dict(longest_gap_half_hours=0, missing=0)])
        == "MEASURED_INTERVAL_NATIVE_COMPLETE"
    )
    with pytest.raises(ValueError):
        gap_status([])


def test_rank_cannot_reverse_or_use_duplicate_visit():
    scan = GreedyScan()
    scan.visit(candidate(3), "MAJOR_GAP_FAIL")
    with pytest.raises(ValueError, match="INCREASING_RANK"):
        scan.visit(candidate(3), "MAJOR_GAP_FAIL")


def response(status=200, continued=False):
    result = requests.Response()
    result.status_code = status
    result._content = json.dumps(
        {"bars": {"AMZN": []}, "next_page_token": "redacted-test-token" if continued else None}
    ).encode()
    return result


def test_separate_durable_budget_permission_hold_and_no_headers(tmp_path):
    p = {"symbols": "AMZN", "limit": 10000}
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        records = [
            json.loads(line) for line in (tmp_path / "journal.jsonl").read_text().splitlines()
        ]
        assert records[-1]["kind"] == "ATTEMPT"
        return response(403)

    t = GreedyTransport(tmp_path / "journal.jsonl", (p,), get=get)
    with pytest.raises(DataAccessError):
        t.request(ENDPOINT, params=p, headers={"secret": "never-record"}, timeout=1)
    assert t.used == 1 and len(calls) == 1
    with pytest.raises(DataAccessError):
        t.request(ENDPOINT, params=p, headers={}, timeout=1)
    assert len(calls) == 1 and "never-record" not in t.journal.read_text()
    assert all(r["package"] == "TA-SP500-GREEDY-UNIVERSE-001" for r in t.records())


def test_page_lifetime_storage_and_suspicious_short_hold(tmp_path):
    p = {"symbols": "AMZN", "limit": 10000}
    t = GreedyTransport(
        tmp_path / "short.jsonl", (p,), get=lambda *a, **k: response(continued=True)
    )
    with pytest.raises(DataAccessError, match="SHORT_CONTINUED"):
        t.request(ENDPOINT, params=p, headers={}, timeout=1)
    assert t.used == 1
    t = GreedyTransport(tmp_path / "budget.jsonl", (p,), get=lambda *a, **k: response())
    for _ in range(3):
        t.request(ENDPOINT, params=p, headers={}, timeout=1)
    with pytest.raises(DataAccessError, match="PAGE_LIMIT"):
        t.request(ENDPOINT, params=p, headers={}, timeout=1)
    with pytest.raises(DataAccessError, match="STORAGE_LIMIT"):
        StorageLimit((tmp_path,), maximum=1).reserve(1)
