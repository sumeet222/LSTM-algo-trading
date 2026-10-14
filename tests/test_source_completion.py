"""Scoped legacy-hold replacement, durable source publication and zero-GET resumption."""

import json
from pathlib import Path

import pytest
import requests

from lstm_data import source_completion as completion
from lstm_data.config import digest, fingerprint, load_config, write_json


def prepare(tmp_path, monkeypatch):
    cfg = load_config(Path("configs/track_a_data.json"))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(completion, "load_config", lambda path: cfg)
    monkeypatch.setattr(completion, "verify_screen_authority", lambda: {})
    report = Path("report")
    old = Path("old_journal.jsonl")
    old.write_text('{"kind":"HOLD","reason":"PAGINATION"}\n')
    inherited = dict(journals=[dict(path=str(old), sha256=digest(old), attempts=0)])
    write_json(report / "inherited_limits_and_hold.json", inherited)
    write_json(report / "reused_source_inventory.json", {})
    p = dict(
        symbols="ALPHA",
        start="2020-03-01T05:00:00Z",
        end="2020-04-01T03:59:59.999999999Z",
        feed="sip",
        timeframe="30Min",
        adjustment="split",
        asof="2025-06-30",
        currency="USD",
        sort="asc",
        limit=10000,
    )
    rows = [dict(params=p, request_hash=fingerprint(p), max_pages=12, max_attempts=1)]
    plan = dict(
        package="SYN_TEST_SOURCE",
        requests=rows,
        requests_sha256=fingerprint(rows),
        inherited_limits_sha256=digest(report / "inherited_limits_and_hold.json"),
        reuse_inventory_sha256=digest(report / "reused_source_inventory.json"),
        carried_attempts=0,
        ordered_universe=["ALPHA"],
        archive="data/raw/alpaca/test_candidate",
    )
    write_json(report / "completion_request_proposal.json", plan)
    write_json(
        report / "legacy_hold_authorization.json",
        dict(
            approved=True,
            plan_sha256=digest(report / "completion_request_proposal.json"),
            replacement_request_hash=fingerprint(p),
        ),
    )
    return report, old


def test_scoped_source_completion_preserves_hold_and_resumes_without_secrets(tmp_path, monkeypatch):
    report, old = prepare(tmp_path, monkeypatch)
    old_sha = digest(old)
    monkeypatch.setattr(completion, "load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr(completion, "credentials", lambda: ("PRIVATE_KEY", "PRIVATE_SECRET"))
    sends = []

    def get(url, **kwargs):
        journal = Path("data/raw/alpaca/test_candidate/transport_attempts.jsonl")
        assert json.loads(journal.read_text().splitlines()[-1])["kind"] == "ATTEMPT"
        sends.append(url)
        r = requests.Response()
        r.status_code = 200
        r._content = json.dumps(
            dict(
                bars=dict(
                    ALPHA=[dict(t="2020-03-02T14:30:00Z", o=10, h=11, l=9, c=10, v=100, n=5, vw=10)]
                ),
                next_page_token=None,
            )
        ).encode()
        return r

    first = completion.acquire(report, get=get)
    assert len(sends) == first["new_attempts"] == 1 and first["chunks"][0]["rows"] == 1
    monkeypatch.setattr(completion, "credentials", lambda: pytest.fail("NO_CREDENTIALS_ON_RESUME"))
    second = completion.acquire(report, get=lambda *a, **k: pytest.fail("NO_GET_ON_RESUME"))
    assert (
        second["chunks"][0]["resumed_zero_GET"]
        and first["journal_sha256"] == second["journal_sha256"]
    )
    assert digest(old) == old_sha
    assert "PRIVATE_KEY" not in Path(first["journal"]).read_text()


def test_changed_inherited_prefix_cannot_be_bypassed(tmp_path, monkeypatch):
    report, old = prepare(tmp_path, monkeypatch)
    old.write_text(old.read_text() + '{"kind":"RESULT","status":403}\n')
    with pytest.raises(ValueError, match="INHERITED_JOURNAL_CHANGED"):
        completion.acquire(report, get=lambda *a, **k: pytest.fail("NO_GET"))


def test_plan_change_does_not_reuse_old_authorization(tmp_path, monkeypatch):
    report, _ = prepare(tmp_path, monkeypatch)
    path = report / "completion_request_proposal.json"
    p = json.loads(path.read_text())
    p["requests"][0]["params"]["adjustment"] = "all"
    path.write_text(json.dumps(p))
    with pytest.raises(ValueError, match="EXACT_COMPLETION_AUTHORITY"):
        completion.acquire(report, get=lambda *a, **k: pytest.fail("NO_GET"))
