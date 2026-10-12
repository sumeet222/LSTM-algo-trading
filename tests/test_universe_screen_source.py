"""No-network budget, durable-before-send, lifetime retry and authority boundaries."""

import json

import pytest
import requests

from lstm_data.alpaca import ENDPOINT, DataAccessError
from lstm_data.universe_screen_source import ScreenTransport


def params():
    return dict(
        symbols="COST",
        start="2021-04-19T04:00Z",
        end="2021-04-20T03:59:59Z",
        feed="sip",
        timeframe="30Min",
        adjustment="split",
        asof="2025-06-30",
        currency="USD",
        sort="asc",
        limit=10000,
    )


def test_durable_before_send_and_three_lifetime_attempts(tmp_path):
    journal = tmp_path / "journal.jsonl"
    calls = []

    def get(url, **kwargs):
        events = [json.loads(x) for x in journal.read_text().splitlines()]
        assert events[-1]["kind"] == "ATTEMPT"
        calls.append(url)
        r = requests.Response()
        r.status_code = 200
        r._content = b'{"bars":{"COST":[]},"next_page_token":null}'
        return r

    t = ScreenTransport(journal, (params(),), get=get)
    for _ in range(3):
        t.request(ENDPOINT, params=params(), headers={"secret": "do-not-log"}, timeout=1)
    assert t.used == 3 and len(calls) == 3 and "do-not-log" not in journal.read_text()
    with pytest.raises(DataAccessError, match="LIFETIME"):
        t.request(ENDPOINT, params=params(), headers={}, timeout=1)
    assert len(calls) == 3


def test_first429_stops_retry_cascade_and_wrong_endpoint_never_sends(tmp_path):
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        r = requests.Response()
        r.status_code = 429
        r._content = b"{}"
        return r

    t = ScreenTransport(tmp_path / "j", (params(),), get=get)
    with pytest.raises(DataAccessError):
        t.request("https://example.invalid", params=params(), headers={}, timeout=1)
    assert not calls
    with pytest.raises(DataAccessError, match="429"):
        t.request(ENDPOINT, params=params(), headers={}, timeout=1)
    with pytest.raises(DataAccessError, match="HOLD"):
        t.request(ENDPOINT, params=dict(params(), page_token="next"), headers={}, timeout=1)
    assert len(calls) == 1 and t.used == 1


def test_no_borrowed_budget_and_concurrent_append_rejected(tmp_path):
    t = ScreenTransport(tmp_path / "j", (params(),))
    t.append({"kind": "ATTEMPT", "page_hash": "fixture"})
    t.journal.write_text(t.journal.read_text() + "{}\n")
    with pytest.raises(DataAccessError, match="CONCURRENT"):
        t.append({"kind": "RESULT"})
    wrong = ScreenTransport(tmp_path / "other", (params(),), ceiling=900)
    with pytest.raises(DataAccessError, match="UNAUTHORIZED"):
        wrong.request(ENDPOINT, params=params(), headers={}, timeout=1)


def test_one_explicit_first_page_exception_preserves_charged_prefix(tmp_path):
    import hashlib

    from lstm_data.config import fingerprint
    from lstm_data.universe_screen import PACKAGE

    journal = tmp_path / "j"
    t = ScreenTransport(journal, (params(),))
    page = fingerprint(params())
    for i in range(3):
        t.append({"kind": "ATTEMPT", "attempt_id": i + 1, "page_hash": page})
        t.append({"kind": "RESULT", "attempt_id": i + 1, "status": "TRANSPORT_ERROR"})
    prefix = journal.read_bytes()
    ref = tmp_path / "exception.json"
    ref.write_text(
        json.dumps(
            {
                "package": PACKAGE,
                "approved": True,
                "additional_attempts": 1,
                "page_hash": page,
                "journal_prefix_sha256": hashlib.sha256(prefix).hexdigest(),
            }
        )
    )
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        r = requests.Response()
        r.status_code = 200
        r._content = b'{"bars":{}}'
        return r

    t = ScreenTransport(
        journal,
        (params(),),
        get=get,
        expected_sha=hashlib.sha256(prefix).hexdigest(),
        exception_ref=ref,
    )
    t.request(ENDPOINT, params=params(), headers={}, timeout=1)
    assert t.used == 4 and journal.read_bytes().startswith(prefix) and len(calls) == 1
    with pytest.raises(DataAccessError, match="LIFETIME"):
        t.request(ENDPOINT, params=params(), headers={}, timeout=1)


def test_schema_divergence_is_durable_and_blocks_a_different_page(tmp_path):
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        r = requests.Response()
        r.status_code = 200
        r._content = b'{"bars":{"UNKNOWN":[]}}'
        return r

    t = ScreenTransport(tmp_path / "j", (params(),), get=get)
    with pytest.raises(DataAccessError, match="SCHEMA"):
        t.request(ENDPOINT, params=params(), headers={}, timeout=1)
    with pytest.raises(DataAccessError, match="HOLD"):
        t.request(ENDPOINT, params=dict(params(), page_token="later"), headers={}, timeout=1)
    assert len(calls) == 1


def test_raw_control_and_empty_chunk_retain_material_request_and_zero_get(tmp_path):
    import pandas as pd

    from lstm_data.config import fingerprint
    from lstm_data.remediation_transport import StorageLimit, publish_chunk
    from lstm_data.universe_screen_source import read_backup_chunk

    p = dict(params(), adjustment="raw", timeframe="1Day")
    frame = pd.DataFrame(
        [
            dict(
                symbol="COST",
                timestamp=pd.Timestamp(p["start"]),
                open=100.0,
                high=110.0,
                low=90.0,
                close=105.0,
                volume=1000.0,
                feed="sip",
                adjustment="raw",
                source_timeframe="1Day",
            )
        ]
    )
    m = publish_chunk(
        tmp_path, frame, p, [], kind="FORMATION_DAILY", limit=StorageLimit((tmp_path,))
    )
    saved = read_backup_chunk(tmp_path, p)
    assert saved is not None and saved[1]["sha256"] == m["sha256"]
    assert saved[0].provenance_id.iloc[0] == fingerprint(p) and saved[0].adjustment.iloc[0] == "raw"
    with pytest.raises(ValueError):
        read_backup_chunk(tmp_path, dict(p, end="2024-07-01T04:00Z"))
