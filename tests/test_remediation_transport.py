"""Offline durable budgets, secret-free receipts, immutable chunks and safe resume."""

import json

import pandas as pd
import pytest
import requests

from lstm_data.alpaca import ENDPOINT, DataAccessError
from lstm_data.config import fingerprint
from lstm_data.remediation_transport import (
    RemediationTransport,
    StorageLimit,
    publish_chunk,
    read_chunk,
)
from lstm_data.store import chunk_paths


def params():
    return {
        "symbols": "AAPL",
        "start": "2020-06-01T13:30:00Z",
        "end": "2020-06-01T14:29:59Z",
        "feed": "sip",
        "adjustment": "split",
        "asof": "2025-06-30",
        "currency": "USD",
        "timeframe": "30Min",
        "sort": "asc",
        "limit": 10000,
    }


def response(status=200):
    value = requests.Response()
    value.status_code = status
    value._content = json.dumps({"bars": {}, "next_page_token": None}).encode()
    return value


def test_append_before_send_redaction_and_three_lifetime_page_attempts(tmp_path):
    journal = tmp_path / "journal.jsonl"
    call_count = []

    def get(*args, **kwargs):
        rows = [json.loads(line) for line in journal.read_text().splitlines()]
        assert rows[-1]["kind"] == "ATTEMPT"
        call_count.append(1)
        return response()

    transport = RemediationTransport(journal, (params(),), get=get)
    page = params() | {"page_token": "sensitive-page-token"}
    for _ in range(3):
        transport.request(ENDPOINT, params=page, headers={"secret": "private-key"}, timeout=1)
    assert transport.used == len(call_count) == 3
    assert (
        "sensitive-page-token" not in journal.read_text()
        and "private-key" not in journal.read_text()
    )
    restarted = RemediationTransport(
        journal, (params(),), get=get, expected_sha=transport.expected_sha
    )
    with pytest.raises(DataAccessError, match="PAGE_LIFETIME"):
        restarted.request(ENDPOINT, params=page, headers={}, timeout=1)
    assert restarted.used == 3


def test_429_stops_without_cascade_and_wrong_request_is_rejected_before_send(tmp_path):
    transport = RemediationTransport(
        tmp_path / "journal.jsonl", (params(),), get=lambda *args, **kwargs: response(429)
    )
    with pytest.raises(DataAccessError, match="UNAUTHORIZED"):
        transport.request(ENDPOINT, params=params() | {"feed": "iex"}, headers={}, timeout=1)
    assert transport.used == 0
    with pytest.raises(DataAccessError, match="429_HOLD"):
        transport.request(ENDPOINT, params=params(), headers={}, timeout=1)
    with pytest.raises(DataAccessError, match="RATE_LIMIT_HOLD"):
        transport.request(ENDPOINT, params=params(), headers={}, timeout=1)
    assert transport.used == 1


def test_global_attempt_ceiling_and_truncated_concurrent_journal(tmp_path):
    transport = RemediationTransport(tmp_path / "journal.jsonl", (params(),))
    for i in range(180):
        transport.append({"kind": "ATTEMPT", "page_hash": str(i)})
    with pytest.raises(DataAccessError, match="BUDGET_EXHAUSTED"):
        transport.request(ENDPOINT, params=params(), headers={}, timeout=1)
    with transport.journal.open("ab") as stream:
        stream.write(b"{")
    with pytest.raises(DataAccessError, match="TRUNCATED"):
        transport.records()
    with pytest.raises(DataAccessError, match="CONCURRENT"):
        transport.append({"kind": "RESULT"})


def frame(empty=False):
    rows = (
        []
        if empty
        else [
            {
                "symbol": "AAPL",
                "timestamp": "2020-06-01T13:30Z",
                "open": 10.0,
                "high": 11.0,
                "low": 9.0,
                "close": 10.0,
                "volume": 100.0,
            }
        ]
    )
    result = pd.DataFrame(
        rows, columns=["symbol", "timestamp", "open", "high", "low", "close", "volume"]
    )
    for col, value in (("feed", "sip"), ("adjustment", "split"), ("source_timeframe", "30Min")):
        result[col] = value
    return result


@pytest.mark.parametrize("empty", [False, True])
def test_atomic_additive_chunk_resume_empty_absence_and_corruption(tmp_path, empty):
    store = tmp_path / "new_native"
    limit = StorageLimit((store,))
    publish_chunk(store, frame(empty), params(), [], kind="GAP_RETRY", limit=limit)
    pair = read_chunk(store, params())
    assert pair is not None and len(pair[0]) == (0 if empty else 1)
    assert pair[1]["availability_basis"] == "UNKNOWN" and pair[1]["available_at"] is None
    assert not pair[1]["scientific_activation"]
    assert pair[1]["params"]["adjustment"] == "split"
    with pytest.raises(FileExistsError):
        publish_chunk(store, frame(empty), params(), [], kind="GAP_RETRY", limit=limit)
    data, _ = chunk_paths(store, params())
    with data.open("ab") as stream:
        stream.write(b"CORRUPTION")
    with pytest.raises(ValueError, match="CHECKSUM"):
        read_chunk(store, params())


def test_interrupted_pair_and_storage_cap_never_overwrite(tmp_path):
    store = tmp_path / "new"
    data, _ = chunk_paths(store, params())
    store.mkdir()
    data.write_bytes(b"orphan")
    with pytest.raises(ValueError, match="INTERRUPTED"):
        read_chunk(store, params())
    limit = StorageLimit((tmp_path,), maximum=1)
    with pytest.raises(DataAccessError, match="STORAGE_LIMIT"):
        publish_chunk(tmp_path / "other", frame(), params(), [], kind="WARMUP", limit=limit)
    assert data.read_bytes() == b"orphan"
    assert read_chunk(tmp_path / "absent", params()) is None
    assert fingerprint(params())
