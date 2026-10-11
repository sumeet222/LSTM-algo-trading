"""Operational limits remain separate from source and scientific identity."""

import json
from pathlib import Path

import pytest
from test_spy_completion import response

from lstm_data.alpaca import ENDPOINT, DataAccessError
from lstm_data.config import digest
from lstm_data.market_source import AttemptBudget, MarketSource
from lstm_data.spy_completion import (
    RollingProgress,
    acquisition_plan,
    storage_guard,
    verify_historical_journal,
)
from lstm_data.store import chunk_paths, save_chunk


def source_v3(tmp_path: Path) -> MarketSource:
    folder = tmp_path / "configs"
    folder.mkdir()
    path = folder / "market.json"
    path.write_text(Path("configs/track_a_market_spy_v3.json").read_text())
    return MarketSource.load(path)


def journal_fixture(source: MarketSource) -> AttemptBudget:
    journal = source.store / "transport_attempts.jsonl"
    journal.parent.mkdir(parents=True)
    journal.write_bytes(b'{"stage":"inherited"}\n' * 13)
    return AttemptBudget(journal, "fixture", 900, tuple(source.partitions()))


def test_v3_plan_counts_discarded_thirteen_and_preserves_old_source_keys(tmp_path):
    source = source_v3(tmp_path)
    evidence = json.loads(Path("reports/data_audit/ta_mkt_spy_002_2026-10-11/"
                               "pagination_diagnostic.json").read_text())
    plan = acquisition_plan(source, evidence, 13, cached_pages=0)
    assert plan["status"] == "FEASIBLE"
    assert plan["upper_cumulative_attempts"] == 853
    assert plan["actual_cached_pages"] == 0
    assert acquisition_plan(source, evidence, 13)["upper_cumulative_attempts"] == 853
    with pytest.raises(DataAccessError, match="DISCARDED_CACHE"):
        acquisition_plan(source, evidence, 13, cached_pages=4)
    assert [p["upper_pages"] for p in plan["partitions"]] == [
        15, 27, 26, 27, 26, 27, 26, 27, 26, 27, 26]
    for version in (1, 2):
        old = MarketSource.load(Path(f"configs/track_a_market_spy_v{version}.json"))
        assert old.partitions() == source.partitions()
    config = source.config | {"feed": "iex"}
    (tmp_path / "configs/market.json").write_text(json.dumps(config))
    with pytest.raises(ValueError, match="MISMATCH"):
        MarketSource.load(tmp_path / "configs/market.json")


def test_900_global_and_three_lifetime_attempts_per_page(tmp_path, monkeypatch):
    source = source_v3(tmp_path)
    budget = journal_fixture(source)
    params = source.partitions()[0]
    monkeypatch.setattr("lstm_data.market_source.requests.get", lambda *a, **k: response())
    for _ in range(3):
        budget.get(ENDPOINT, params=params)
    assert budget.used == 16
    with pytest.raises(DataAccessError, match="THREE_LIFETIME"):
        budget.get(ENDPOINT, params=params)
    assert budget.used == 16
    budget.journal.write_bytes(b'{"stage":"inherited"}\n' * 899)
    budget.get(ENDPOINT, params=params)
    assert budget.used == 900
    with pytest.raises(DataAccessError, match="BUDGET_EXHAUSTED"):
        budget.get(ENDPOINT, params=params | {"page_token": "other"})
    assert budget.used == 900


def test_32_successful_response_pages_per_original_key_and_no_identity_drift(tmp_path, monkeypatch):
    source = source_v3(tmp_path)
    budget = journal_fixture(source)
    params = source.partitions()[1]
    monkeypatch.setattr("lstm_data.market_source.requests.get", lambda *a, **k: response())
    for index in range(32):
        budget.get(ENDPOINT, params=params | {"page_token": str(index)})
    assert budget.used == 45
    with pytest.raises(DataAccessError, match="32_RESPONSE"):
        budget.get(ENDPOINT, params=params | {"page_token": "33"})
    with pytest.raises(DataAccessError, match="IDENTITY"):
        budget.get(ENDPOINT, params=params | {"asof": "2024-06-30"})
    assert budget.used == 45


def test_disk_guard_prevents_unsafe_publication_and_journal_growth(tmp_path, monkeypatch):
    import pandas as pd

    source = source_v3(tmp_path)
    budget = journal_fixture(source)
    report = tmp_path / "report"
    report.mkdir()
    with pytest.raises(DataAccessError, match="DISK_CEILING"):
        storage_guard(source, report, 256 * 1024**2)
    budget.before_write = lambda size: storage_guard(source, report, 256 * 1024**2 + size)
    monkeypatch.setattr("lstm_data.market_source.requests.get", lambda *a, **k: pytest.fail("GET"))
    with pytest.raises(DataAccessError, match="DISK_CEILING"):
        budget.get(ENDPOINT, params=source.partitions()[0])
    assert budget.used == 13
    frame = pd.DataFrame([{"symbol": "SPY", "timestamp": pd.Timestamp("2020-03-19T13:30Z"),
                           "open": 100., "high": 103., "low": 99., "close": 102., "volume": 10.}])
    with pytest.raises(DataAccessError, match="DISK_CEILING"):
        save_chunk(source.store, frame, source.partitions()[0], [], source.config,
                   before_publish=lambda size: storage_guard(source, report, 256 * 1024**2 + size))
    assert not any(p.exists() for p in chunk_paths(source.store, source.partitions()[0]))


def test_historical_prefix_tampering_concurrent_append_and_truncated_receipt_fail_closed(tmp_path):
    source = source_v3(tmp_path)
    proof_path = Path("reports/data_audit/ta_mkt_spy_002_2026-10-11/transport_journal_proof.json")
    proof = json.loads(proof_path.read_text())
    target = source.root / proof_path
    target.parent.mkdir(parents=True)
    target.write_bytes(proof_path.read_bytes())
    prior = source.root / proof["prior_evidence_ref"]
    prior.parent.mkdir(parents=True)
    prior.write_bytes(Path(proof["prior_evidence_ref"]).read_bytes())
    failure = Path("reports/data_audit/ta_mkt_spy_2026-10-11/source_failure_9.json")
    (source.root / failure).write_bytes(failure.read_bytes())
    journal = source.store / "transport_attempts.jsonl"
    journal.parent.mkdir(parents=True)
    # Reconstruct only this offline fixture. Live acquisition never reconstructs the journal.
    raw = prior.read_bytes() + b"".join((json.dumps(r, sort_keys=True) + "\n").encode()
                                       for r in proof["new_records"])
    journal.write_bytes(raw)
    budget = AttemptBudget(journal, "fixture", 900, tuple(source.partitions()))
    verify_historical_journal(source, budget)
    assert budget.used == 13 and digest(journal) == proof["sha256"]
    assert budget.legacy_first_partition_pages == 2
    assert budget.legacy_initial_page_attempts == budget.legacy_unknown_continued_attempts == 1
    journal.write_bytes(raw + b'{"stage":"unknown_writer"}\n')
    with pytest.raises(DataAccessError, match="CONCURRENT"):
        budget.append({"record_kind": "attempt"})
    journal.write_bytes(b"x" + raw[1:])
    with pytest.raises(DataAccessError, match="PROOF_MISMATCH"):
        verify_historical_journal(source, budget)
    journal.write_bytes(raw[:-1])
    with pytest.raises(DataAccessError, match="PROOF_MISMATCH"):
        verify_historical_journal(source, budget)


def test_rolling_budget_stops_before_unfinishable_requests(tmp_path):
    source = source_v3(tmp_path)
    budget = journal_fixture(source)
    report = tmp_path / "report"
    report.mkdir()
    evidence = {"pages": [{"returned_rows": 336, "has_continuation": True}]}
    plan = acquisition_plan(source, evidence, budget.used, cached_pages=0)
    progress = RollingProgress(source, report, budget, plan)
    progress.begin(plan["partitions"][0])
    progress.guard()
    progress.density = 1
    with pytest.raises(DataAccessError, match="ROLLING_PAGE"):
        progress.guard()
    assert budget.used == 13



def test_report_capacity_reserved_before_atomic_write(tmp_path, monkeypatch):
    from lstm_data.spy_completion import write_bounded_report

    source = source_v3(tmp_path)
    source.store.mkdir(parents=True)
    report = tmp_path / "reports"
    report.mkdir()
    target = report / "audit.json"

    def reject(source, report, additional):
        assert additional > 0
        raise DataAccessError("SPY_DISK_CEILING_BEFORE_WRITE")

    monkeypatch.setattr("lstm_data.spy_completion.storage_guard", reject)
    with pytest.raises(DataAccessError, match="DISK_CEILING"):
        write_bounded_report(source, report, target, {"coverage": "measured"})
    assert not target.exists()
