"""Hermetic P0.2 checks: synthetic records and metadata, never historical rows."""

from __future__ import annotations

import copy
import json
import socket
from pathlib import Path

import pytest

from lstm_data.audit import (
    AUTHORITY,
    f01_fixture,
    inspect,
    protocol_check,
    protocol_identity,
    stable_fingerprint,
    validate_check,
)
from lstm_data.cli import main
from lstm_data.ledger import (
    append_event,
    current_blockers,
    decode_ledger,
    guard_operation,
    pair_budget,
    read_ledger,
    validate_event,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def event():
    return {
        "schema_version": 1,
        "event_id": "synthetic-blocker",
        "time_utc": "2001-01-02T15:00:00Z",
        "track": "A",
        "protocol_hash": "a" * 64,
        "gate_id": "G0",
        "package": "P0.2",
        "kind": "blocker",
        "status": "BLOCKED",
        "code_id": None,
        "config_id": None,
        "source_ids": None,
        "affected_branches": ["market_features"],
        "artifact_refs": [],
        "evidence": {"example_id": "fake-only"},
        "rationale": "Synthetic unverified source",
        "owner_action": "Human validation",
        "blocks": ["market_timing"],
        "supersedes": [],
    }


def test_fingerprint_portable_substantive():
    a = {
        "horizon": 240,
        "start_date": "2000-01-01",
        "created_at": "one",
        "_root": "/fake/machine/one",
        "api_key": "synthetic-secret",
    }
    b = {**a, "created_at": "two", "_root": "/fake/machine/two", "api_key": "different"}
    assert stable_fingerprint(a) == stable_fingerprint(b) == stable_fingerprint(a)
    assert stable_fingerprint(a) != stable_fingerprint({**b, "horizon": 120})
    assert stable_fingerprint(a) != stable_fingerprint({**b, "start_date": "2000-01-02"})
    with pytest.raises(ValueError):
        stable_fingerprint({"source": "/fake/absolute/input"})


def test_real_pointer_and_p01_links():
    pointer = json.loads((ROOT / "configs/CURRENT_PROTOCOL.json").read_text())
    assert len(pointer["documents"]) == len(AUTHORITY) == 5
    assert protocol_check(ROOT, pointer)["status"] == "PASS"


@pytest.mark.parametrize("change", ["missing", "modified", "version", "hash", "extra"])
def test_pointer_mismatch_blocks(tmp_path, change):
    pointer = json.loads((ROOT / "configs/CURRENT_PROTOCOL.json").read_text())
    for reference in pointer["documents"] + pointer["data_refs"]:
        path = tmp_path / reference["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / reference["path"]).read_bytes())
    first = pointer["documents"][0]
    if change == "missing":
        (tmp_path / first["path"]).unlink()
    elif change == "modified":
        (tmp_path / first["path"]).write_text("synthetic mismatch")
    elif change == "version":
        first["version"] = "future"
    elif change == "hash":
        first["sha256"] = "0" * 64
    else:
        pointer["documents"].append(copy.deepcopy(first))
    pointer["protocol_hash"] = protocol_identity(pointer)
    assert protocol_check(tmp_path, pointer)["status"] == "BLOCKED"


def test_append_correction_preserves_prefix(tmp_path, event):
    path = tmp_path / "reports/events.jsonl"
    append_event(path, event, root=tmp_path)
    before = path.read_bytes()
    correction = {
        **event,
        "event_id": "correction",
        "supersedes": [event["event_id"]],
        "rationale": "More precise synthetic rationale",
    }
    append_event(path, correction, root=tmp_path)
    assert path.read_bytes().startswith(before)
    assert read_ledger(path) == [event, correction]
    assert current_blockers(read_ledger(path)) == [correction]
    with pytest.raises(ValueError):
        append_event(path, event, root=tmp_path)
    assert read_ledger(path) == [event, correction]


@pytest.mark.parametrize("change", ["status", "schema", "time", "field", "approval", "attempt"])
def test_invalid_event_rejected(event, change):
    if change == "status":
        event["status"] = "HARD FAIL"
    elif change == "schema":
        event["schema_version"] = 2
    elif change == "time":
        event["time_utc"] = "2001-01-02T15:00:00"
    elif change == "field":
        event["approve"] = True
    elif change == "approval":
        event["kind"] = "approval"
    else:
        event["attempt_id"] = "unauthorized-fit"
    with pytest.raises(ValueError):
        validate_event(event)


@pytest.mark.parametrize("payload", [b'{"truncated":', b"{}\n", b"not-json\n", b"\xff\n"])
def test_corrupt_history_preserved(tmp_path, event, payload):
    path = tmp_path / "reports/events.jsonl"
    path.parent.mkdir()
    path.write_bytes(payload)
    with pytest.raises(ValueError):
        append_event(path, event, root=tmp_path)
    assert path.read_bytes() == payload


@pytest.mark.parametrize("failure_at", ["fsync", "replace"])
def test_partial_publication_failure_preserves_history(tmp_path, event, monkeypatch, failure_at):
    path = tmp_path / "reports/events.jsonl"
    append_event(path, event, root=tmp_path)
    before = path.read_bytes()

    def fail(*args):
        raise OSError("synthetic failure before publication")

    monkeypatch.setattr("lstm_data.ledger.os." + failure_at, fail)
    with pytest.raises(OSError):
        append_event(path, {**event, "event_id": "second"}, root=tmp_path)
    assert path.read_bytes() == before
    assert list(path.parent.iterdir()) == [path]


def test_stale_lock_fails_closed(tmp_path, event):
    path = tmp_path / "reports/events.jsonl"
    path.parent.mkdir()
    lock = path.with_name(path.name + ".lock")
    lock.write_text("preserve this stale-lock evidence")
    with pytest.raises(FileExistsError):
        append_event(path, event, root=tmp_path)
    assert lock.exists() and not path.exists()


@pytest.mark.parametrize("status,blocks", [("PASS", ["market_timing"]), ("BLOCKED", [])])
def test_cannot_clear_or_narrow_blockers(tmp_path, event, status, blocks):
    path = tmp_path / "reports/events.jsonl"
    append_event(path, event, root=tmp_path)
    correction = {
        **event,
        "event_id": "illegal",
        "supersedes": [event["event_id"]],
        "status": status,
        "blocks": blocks,
    }
    with pytest.raises(ValueError):
        append_event(path, correction, root=tmp_path)
    with pytest.raises(ValueError):
        decode_ledger(path.read_bytes() + json.dumps(correction).encode() + b"\n")


def test_narrow_failure_and_no_test_auto_approval(event):
    passed_tests = {
        **event,
        "event_id": "pytest-passed",
        "kind": "audit",
        "status": "PASS",
        "blocks": [],
    }
    history = [event, passed_tests]
    assert guard_operation("stock_administration", history)["status"] == "PASS"
    assert "unresolved:market_timing" in guard_operation("market_features", history)["reasons"]
    assert current_blockers(history) == [event]
    portfolio = {**event, "blocks": ["portfolio_accounting"]}
    assert (
        "unresolved:portfolio_accounting"
        in guard_operation("economic_evaluation", [portfolio])["reasons"]
    )
    assert (
        "unresolved:portfolio_accounting"
        not in guard_operation("predictive_evaluation", [portfolio])["reasons"]
    )


def test_f01_historical_counterexample_is_rejected_after_repair():
    example = f01_fixture()
    assert example["observed_available_age_minutes"] == 60
    assert example["required_period_end_age_minutes"] == 120
    assert example["period_end_age_minutes"] == 120
    assert not example["observed_usable"] and not example["required_usable"]
    assert example["status"] == "PASS" and example["reason"] == "STALE_PERIOD_END"
    assert example["synthetic_only"] and not example["research_ready"]


def test_external_blockers_and_confirmation_locked():
    report = inspect(ROOT, diagnose=True)
    ids = {e["event_id"] for e in report["blockers"]}
    assert {
        "p0.1-F01",
        "p0.1-USA500-source-clock",
        "p0.1-shared-D3-clock",
        "p0.1-minute-execution",
    } <= ids
    assert report["research_status"] == "BLOCKED"
    assert report["gates"] == {
        **{f"G{i}": "BLOCKED" for i in range(3)},
        **{f"G{i}": "NOT_RUN" for i in range(3, 10)},
    }
    assert report["operations"]["confirmation_evaluation"]["status"] == "BLOCKED"
    assert guard_operation("confirmation_evaluation", [])["status"] == "BLOCKED"
    for check in report["checks"]:
        validate_check(check)


def test_budget_counts_failed_attempts_and_preserves_history():
    synthetic = [{"attempt_id": f"fake-pair-{i}", "status": "INVALID"} for i in range(40)]
    assert pair_budget(synthetic[:39], "fake-pair-39")["status"] == "PASS"
    assert pair_budget(synthetic)["attempted_pairs"] == 40
    assert pair_budget(synthetic, "fake-pair-39")["status"] == "BLOCKED"
    assert pair_budget(synthetic, "fake-pair-40")["status"] == "BLOCKED"
    synthetic += [{"attempt_id": "fake-pair-0", "status": "NOT_RUN", "supersedes": ["old"]}]
    assert pair_budget(synthetic)["attempted_pairs"] == 40
    assert pair_budget([])["attempted_pairs"] == 0


def test_duplicate_json_fields_rejected(event):
    encoded = json.dumps(event).replace(
        '"status": "BLOCKED"', '"status": "PASS", "status": "BLOCKED"'
    )
    with pytest.raises(ValueError):
        decode_ledger(encoded.encode() + b"\n")


def test_explicit_cli_append_and_read(tmp_path, event, capsys):
    pointer = json.loads((ROOT / "configs/CURRENT_PROTOCOL.json").read_text())
    names = [r["path"] for r in pointer["documents"] + pointer["data_refs"]]
    names += ["configs/CURRENT_PROTOCOL.json", "configs/track_a_data.json", "pyproject.toml"]
    for name in names:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / name).read_bytes())
    event["protocol_hash"] = pointer["protocol_hash"]
    (tmp_path / "reports/example.json").write_text(json.dumps(event))
    args = ["evidence", "--root", str(tmp_path), "--ledger", "reports/demo.jsonl"]
    assert main([*args, "--mode", "append", "--event", "reports/example.json"]) == 0
    assert read_ledger(tmp_path / "reports/demo.jsonl") == [event]
    assert main(args) == 0
    assert main([*args, "--mode", "append", "--event", "reports/example.json"]) == 2
    capsys.readouterr()


def test_approval_needs_real_hash_bound_human_record(tmp_path, event):
    event.update(
        kind="approval",
        status="PASS",
        blocks=[],
        decision_ref={
            "path": "reports/missing-decision.json",
            "sha256": "0" * 64,
            "decision_id": "missing",
        },
    )
    with pytest.raises(ValueError):
        append_event(tmp_path / "reports/events.jsonl", event, root=tmp_path)
    assert not (tmp_path / "reports/events.jsonl").exists()


@pytest.mark.parametrize(
    "payload",
    [{"api_key": "fake"}, {"path": "/fake/private"}, {"text": "https://fake:fake@example.test"}],
)
def test_sensitive_event_payload_rejected(event, payload):
    event["evidence"] = payload
    with pytest.raises(ValueError):
        validate_event(event)


def test_default_cli_offline_no_writes_or_source_reads(monkeypatch, capsys):
    def forbidden(*args, **kwargs):
        raise AssertionError("Network, source or credential access attempted")

    for name in ("load_dotenv", "credentials", "load_store", "audit_course"):
        monkeypatch.setattr("lstm_data.cli." + name, forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    original_open = Path.open

    def evidence_only(path, *args, **kwargs):
        resolved = path.resolve()
        if resolved.is_relative_to(ROOT / "data/raw") or ".env" in resolved.name:
            raise AssertionError("Raw data or secret file opened")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", evidence_only)
    before = {
        p: (p.stat().st_size, p.stat().st_mtime_ns)
        for folder in ("data", "reports")
        for p in (ROOT / folder).rglob("*")
        if p.is_file()
    }
    assert main(["evidence", "--dry-run"]) == 0
    assert main(["evidence", "--mode", "diagnose"]) == 2
    assert main(["--env-file", ".env", "evidence"]) == 2
    assert main(["evidence", "--mode", "append", "--dry-run"]) == 2
    after = {
        p: (p.stat().st_size, p.stat().st_mtime_ns)
        for folder in ("data", "reports")
        for p in (ROOT / folder).rglob("*")
        if p.is_file()
    }
    assert before == after
    output = capsys.readouterr().out
    assert '"reason": "STALE_PERIOD_END"' in output
    assert '"research_status": "BLOCKED"' in output
    assert '"meaning": "F01_REPAIRED_IN_CODE regression only;' in output
    assert "/Users/" not in output
