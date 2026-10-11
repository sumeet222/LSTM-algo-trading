import json
from pathlib import Path

import pandas as pd
import pytest
import requests

from lstm_data.alpaca import ENDPOINT, DataAccessError, HistoricalClient
from lstm_data.config import fingerprint
from lstm_data.market_features import window_from_history
from lstm_data.market_source import (
    AttemptBudget,
    MarketSource,
    acquire_partition,
    archive_qa,
    load_market_history,
)
from lstm_data.spy_completion import ReplayTransport, acquisition_plan, archive_complete, diagnostic
from lstm_data.store import chunk_paths


def source_v2(tmp_path: Path) -> MarketSource:
    folder = tmp_path / "configs"
    folder.mkdir()
    path = folder / "market.json"
    path.write_text(Path("configs/track_a_market_spy_v2.json").read_text())
    return MarketSource.load(path)


def response(status: int = 200, *, minute: int = 0, token: str | None = None) -> requests.Response:
    result = requests.Response()
    result.status_code = status
    start = pd.Timestamp("2020-03-19T13:30Z") + pd.Timedelta(minutes=minute)
    result._content = json.dumps({"bars": {"SPY": [
        {"t": start.isoformat(), "o": 100, "h": 103, "l": 99, "c": 102, "v": 10}
    ]}, "next_page_token": token}).encode()
    return result


def client_fixture(
    source: MarketSource, budget: AttemptBudget,
) -> tuple[HistoricalClient, ReplayTransport]:
    transport = ReplayTransport(budget, budget.used)
    client = HistoricalClient(source.config, "fixture", "fixture", get=transport.get,
                              sleep=lambda _: None, jitter=lambda: 0)
    return client, transport


def test_three_short_pages_replayed_once_and_completed_resume_zero_get(tmp_path, monkeypatch):
    source = source_v2(tmp_path)
    journal = source.store / "transport_attempts.jsonl"
    journal.parent.mkdir(parents=True)
    prefix = b'{"stage":"inherited"}\n' * 9
    journal.write_bytes(prefix)
    budget = AttemptBudget(journal, "fixture", 240)
    responses = iter([response(token="a"), response(minute=30, token="b"), response(minute=60)])
    calls = []

    def get(url, **kwargs):
        calls.append(kwargs["params"])
        return next(responses)

    monkeypatch.setattr(requests, "get", get)
    client, transport = client_fixture(source, budget)
    evidence = diagnostic(client, source, transport)
    assert evidence["new_transport_attempts"] == 3
    assert evidence["exhausted_first_partition"]
    assert [p["returned_rows"] for p in evidence["pages"]] == [1, 1, 1]
    transport.diagnostic = False
    result = acquire_partition(source, client, source.partitions()[0])
    assert result["rows"] == 3 and transport.replayed_pages == 3
    assert budget.used == 12 and len(calls) == 3
    assert journal.read_bytes().startswith(prefix)
    assert "page_token" not in journal.read_text()
    assert acquire_partition(source, client, source.partitions()[0]) == result
    assert budget.used == 12 and len(calls) == 3
    assert all(p["feed"] == "sip" and p["adjustment"] == "raw" for p in calls)


def test_diagnostic_four_transports_counts_timeout_retries(tmp_path, monkeypatch):
    source = source_v2(tmp_path)
    budget = AttemptBudget(source.store / "transport_attempts.jsonl", "fixture", 240)
    count = 0

    def get(url, **kwargs):
        nonlocal count
        count += 1
        if count == 1:
            raise requests.Timeout("fixture")
        return response(minute=count * 30, token=str(count))

    monkeypatch.setattr(requests, "get", get)
    client, transport = client_fixture(source, budget)
    evidence = diagnostic(client, source, transport)
    assert count == budget.used == evidence["new_transport_attempts"] == 4
    assert len(evidence["pages"]) == 3 and not evidence["exhausted_first_partition"]
    with pytest.raises(DataAccessError, match="FOUR_TRANSPORT"):
        transport.get(ENDPOINT, params={"new": "page"})
    assert count == 4


@pytest.mark.parametrize("status,attempts", [(401, 1), (403, 1), (422, 1), (503, 3), (429, 2)])
def test_failures_are_bounded_and_never_publish(tmp_path, monkeypatch, status, attempts):
    source = source_v2(tmp_path)
    budget = AttemptBudget(source.store / "transport_attempts.jsonl", "fixture", 240)
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: response(status))
    client, transport = client_fixture(source, budget)
    transport.diagnostic = False
    with pytest.raises(DataAccessError):
        acquire_partition(source, client, source.partitions()[0])
    assert budget.used == attempts
    assert not list(source.store.glob("*.parquet"))


def test_cycle_never_publishes_and_incomplete_partition_restarts(tmp_path, monkeypatch):
    source = source_v2(tmp_path)
    budget = AttemptBudget(source.store / "transport_attempts.jsonl", "fixture", 240)
    pages = iter([response(token="cycle"), response(minute=30, token="cycle")])
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: next(pages))
    client, transport = client_fixture(source, budget)
    transport.diagnostic = False
    with pytest.raises(DataAccessError, match="Repeated"):
        acquire_partition(source, client, source.partitions()[0])
    assert budget.used == 2 and not list(source.store.glob("*.parquet"))
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: response())
    resumed, replay = client_fixture(source, budget)
    replay.diagnostic = False
    assert acquire_partition(source, resumed, source.partitions()[0])["rows"] == 1
    assert budget.used == 3  # No durable partial response is claimed after a crash.


def test_repeated_429_across_success_and_restart_stops(tmp_path, monkeypatch):
    source = source_v2(tmp_path)
    budget = AttemptBudget(source.store / "transport_attempts.jsonl", "fixture", 240)
    responses = iter([response(429), response(), response(429)])
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: next(responses))
    _, transport = client_fixture(source, budget)
    transport.diagnostic = False
    transport.get(ENDPOINT, params={"page": 1})
    transport.get(ENDPOINT, params={"page": 2})
    with pytest.raises(DataAccessError, match="REPEATED_429"):
        transport.get(ENDPOINT, params={"page": 3})
    _, resumed = client_fixture(source, budget)
    with pytest.raises(DataAccessError, match="REPEATED_429"):
        resumed.get(ENDPOINT, params={"page": 4})
    assert budget.used == 3


def test_false_nonstring_token_is_not_terminal_proof(tmp_path, monkeypatch):
    source = source_v2(tmp_path)
    budget = AttemptBudget(source.store / "transport_attempts.jsonl", "fixture", 240)
    result = response()
    payload = result.json()
    payload["next_page_token"] = False
    result._content = json.dumps(payload).encode()
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: result)
    client, _ = client_fixture(source, budget)
    with pytest.raises(DataAccessError, match="INVALID_CONTINUATION"):
        acquire_partition(source, client, source.partitions()[0])
    assert budget.used == 1 and not list(source.store.glob("*.parquet"))


def test_plan_measured_density_includes_retries_and_hard_limits(tmp_path):
    source = source_v2(tmp_path)
    plan = acquisition_plan(source, {"pages": [
        {"returned_rows": 1500, "has_continuation": True}]}, 13)
    assert plan["status"] == "FEASIBLE"
    assert plan["upper_cumulative_attempts"] <= 240
    assert len(plan["partitions"]) == 11 and plan["expected_session_rows"] == 63696
    assert plan["partitions"][0]["request_key"] == fingerprint(source.partitions()[0])
    small = acquisition_plan(source, {"pages": [
        {"returned_rows": 100, "has_continuation": True}]}, 13)
    assert small["status"] == "SOURCE_BLOCKED" and small["upper_cumulative_attempts"] > 240


def test_empty_partial_and_corrupt_archives_are_not_complete(tmp_path):
    source = source_v2(tmp_path)
    with pytest.raises(FileNotFoundError, match="MISSING_SPY"):
        archive_complete(source)
    client = HistoricalClient(source.config, "fixture", "fixture",
                              get=lambda *args, **kwargs: response(), sleep=lambda _: None)
    acquire_partition(source, client, source.partitions()[0])
    with pytest.raises(FileNotFoundError, match="MISSING_SPY"):
        archive_complete(source)
    path, _ = chunk_paths(source.store, source.partitions()[0])
    path.write_bytes(path.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="checksum"):
        archive_complete(source)


def test_all_eleven_keys_terminal_proof_and_actual_adapter_hold(tmp_path, monkeypatch):
    source = source_v2(tmp_path)
    budget = AttemptBudget(source.store / "transport_attempts.jsonl", "fixture", 240)

    def get(url, **kwargs):
        from lstm_data.calendar import schedule

        params = kwargs["params"]
        start = pd.Timestamp(params["start"]).date().isoformat()
        end = pd.Timestamp(params["end"]).date().isoformat()
        opening = schedule(start, end).iloc[0].open
        result = response()
        payload = result.json()
        payload["bars"]["SPY"][0]["t"] = opening.isoformat()
        second = dict(payload["bars"]["SPY"][0])
        second["t"] = (opening + pd.Timedelta(minutes=30)).isoformat()
        payload["bars"]["SPY"].append(second)
        result._content = json.dumps(payload).encode()
        return result

    monkeypatch.setattr(requests, "get", get)
    client, transport = client_fixture(source, budget)
    transport.diagnostic = False
    for params in source.partitions():
        acquire_partition(source, client, params, completion_check=transport.completion_audit)
    proof = archive_complete(source)
    assert proof["completed_partitions"] == 11 and proof["rows"] == 22
    assert proof["archive_complete"] and not proof["publication_verified"]
    history = load_market_history(source)
    assert len(history.hours) == 11 and not history.closes
    output = window_from_history(history, "2020-07-01", 1)
    assert output.values is None and not any(output.valid_mask) and not output.research_ready
    assert output.reason == "PUBLICATION_UNKNOWN"
    qa = archive_qa(source)
    assert qa["totals"]["sessions"] == 1327
    assert qa["totals"]["observed_native_rth"] == 22
    assert qa["totals"]["missing_native_rth"] == qa["totals"]["expected_native_rth"] - 22
    assert len(qa["months"]) == 64 and len(qa["years"]) == 6
    assert qa["session_types"]["early"]["sessions"] > 0
    assert not qa["complete_grid_pass"] and qa["causal_feature_eligible_windows"] == 0
    _, path = chunk_paths(source.store, source.partitions()[0])
    manifest = json.loads(path.read_text())
    manifest["coverage_audit"]["pagination_exhausted"] = False
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="TERMINAL"):
        archive_complete(source)
