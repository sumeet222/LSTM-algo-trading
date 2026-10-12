"""Bounded secondary requests and truthful native schema; no invented source contracts."""

import hashlib
import json

import pandas as pd
import pytest

from lstm_data import remediation_secondary as secondary
from lstm_data.alpaca import DataAccessError
from lstm_data.config import digest, write_json
from lstm_data.remediation_plan import PACKAGE
from lstm_data.remediation_secondary import acquire_secondary, parse_secondary, secondary_plan


def reviewed_archive(tmp_path, monkeypatch):
    """An existing denied attempt and a distinct current human access decision."""
    plan = secondary_plan()
    plan["requests"] = plan["requests"][:2]
    monkeypatch.setattr(secondary, "secondary_plan", lambda: plan)
    monkeypatch.setattr(secondary, "SECONDARY_ARCHIVE", tmp_path / "raw")
    monkeypatch.setattr(secondary, "ARCHIVE", tmp_path / "primary")
    monkeypatch.setattr(secondary.time, "sleep", lambda _: None)
    # Register cleanup before dotenv inserts the synthetic key into os.environ.
    monkeypatch.setenv("MASSIVE_API_KEY", "temporary-test-placeholder")
    monkeypatch.delenv("MASSIVE_API_KEY")
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)
    env = tmp_path / ".env"
    env.write_text("MASSIVE_API_KEY=synthetic-test-key\n")
    request_hash = plan["requests"][0]["request_hash"]
    journal = tmp_path / "raw" / "source_transport_journal.jsonl"
    journal.parent.mkdir()
    original = (
        json.dumps({"kind": "ATTEMPT", "attempt_id": 1, "page_hash": request_hash})
        + "\n"
        + json.dumps({"kind": "RESULT", "attempt_id": 1, "status": 403})
        + "\n"
    ).encode()
    journal.write_bytes(original)
    review = tmp_path / "review.json"
    write_json(
        review,
        {
            "package": PACKAGE,
            "review_id": "synthetic-human-review",
            "prior_journal_sha256": digest(journal),
            "prior_attempts": 1,
            "validation_request_hash": request_hash,
        },
    )
    return tmp_path / "report", env, review, journal, original, plan


@pytest.mark.parametrize("status", [403, 429, "TRANSPORT_ERROR"])
def test_reviewed_access_failure_consumes_one_attempt_and_never_repeats(
    tmp_path, monkeypatch, status
):
    report, env, review, journal, original, _ = reviewed_archive(tmp_path, monkeypatch)
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        assert "apiKey" not in kwargs["params"]
        assert kwargs["headers"]["Authorization"] == "Bearer synthetic-test-key"
        assert kwargs["allow_redirects"] is False
        if status == "TRANSPORT_ERROR":
            raise secondary.requests.ConnectionError("untrusted secret-bearing error")
        response = secondary.requests.Response()
        response.status_code = status
        response._content = b"{}"
        return response

    monkeypatch.setattr(secondary.requests, "get", get)
    result = acquire_secondary(report, env, access_review=review)
    assert result["status"] == "HOLD" and result["attempts"] == 2 and result["remaining"] == 78
    resumed = acquire_secondary(report, env, access_review=review)
    assert resumed["attempts"] == 2 and len(calls) == 1
    assert journal.read_bytes().startswith(original)
    assert b"synthetic-test-key" not in journal.read_bytes()
    assert b"untrusted" not in journal.read_bytes()
    assert not list((tmp_path / "raw").rglob("*.parquet"))


def test_successful_review_preserves_budget_and_immutable_resume(tmp_path, monkeypatch):
    report, env, review, journal, original, plan = reviewed_archive(tmp_path, monkeypatch)
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        request = next(r for r in plan["requests"] if r["endpoint"] == url)
        response = secondary.requests.Response()
        response.status_code = 200
        response._content = json.dumps(
            {
                "ticker": request["symbol"],
                "adjusted": True,
                "resultsCount": 0,
                "results": [],
            }
        ).encode()
        return response

    monkeypatch.setattr(secondary.requests, "get", get)
    result = acquire_secondary(report, env, access_review=review)
    assert result["status"] == "COMPLETE_CANDIDATE_ONLY"
    assert result["attempts"] == 3 and result["remaining"] == 77 and len(calls) == 2
    assert journal.read_bytes().startswith(original)
    before = journal.read_bytes()
    resumed = acquire_secondary(report, env, access_review=review)
    assert resumed["attempts"] == 3 and len(calls) == 2 and journal.read_bytes() == before
    assert all(r["status"] == "SHA_VERIFIED_RESUME" for r in resumed["results"])


def test_unreviewed_or_mismatched_access_authority_sends_no_get(tmp_path, monkeypatch):
    report, env, review, journal, original, _ = reviewed_archive(tmp_path, monkeypatch)

    def forbidden(*args, **kwargs):
        raise AssertionError("No GET before a journal-bound access review")

    monkeypatch.setattr(secondary.requests, "get", forbidden)
    assert acquire_secondary(report, env)["attempts"] == 1
    value = json.loads(review.read_text())
    bad_review = tmp_path / "mismatched_review.json"
    write_json(bad_review, value | {"prior_attempts": 0})
    with pytest.raises(DataAccessError, match="BINDING"):
        acquire_secondary(report, env, access_review=bad_review)
    assert journal.read_bytes() == original


@pytest.mark.parametrize("prior_status", [401, 429])
def test_review_cannot_clear_authentication_or_rate_limit_denial(
    tmp_path, monkeypatch, prior_status
):
    report, env, review, journal, original, _ = reviewed_archive(tmp_path, monkeypatch)
    journal.write_bytes(original.replace(b'"status": 403', f'"status": {prior_status}'.encode()))
    value = json.loads(review.read_text())
    bad_review = tmp_path / "ineligible_review.json"
    write_json(bad_review, value | {"prior_journal_sha256": digest(journal)})
    with pytest.raises(DataAccessError, match="BINDING"):
        acquire_secondary(report, env, access_review=bad_review)
    assert not any(
        json.loads(line)["kind"] == "ACCESS_REVIEW" for line in journal.read_bytes().splitlines()
    )


@pytest.mark.parametrize("used, same_page", [(3, True), (80, False)])
def test_access_review_does_not_reset_page_or_global_ceiling(
    tmp_path, monkeypatch, used, same_page
):
    report, env, review, journal, _, plan = reviewed_archive(tmp_path, monkeypatch)
    request_hash = plan["requests"][0]["request_hash"]
    records = []
    for attempt in range(1, used + 1):
        records.extend(
            [
                {
                    "kind": "ATTEMPT",
                    "attempt_id": attempt,
                    "page_hash": request_hash if same_page else f"prior-page-{attempt}",
                },
                {
                    "kind": "RESULT",
                    "attempt_id": attempt,
                    "status": 403 if attempt == used else 500,
                },
            ]
        )
    journal.write_text("".join(json.dumps(r) + "\n" for r in records))
    value = json.loads(review.read_text())
    bound_review = tmp_path / "budget_review.json"
    write_json(
        bound_review, value | {"prior_journal_sha256": digest(journal), "prior_attempts": used}
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("Access review cannot reset a consumed ceiling")

    monkeypatch.setattr(secondary.requests, "get", forbidden)
    result = acquire_secondary(report, env, access_review=bound_review)
    assert result["status"] == "HOLD" and result["attempts"] == used
    assert result["remaining"] == 80 - used


def test_secondary_scope_current_gaps_small_controls_and_budget():
    plan = secondary_plan()
    assert len(plan["requests"]) == 22 and plan["maximum_declared_attempt_envelope"] == 66
    assert plan["requests"][0]["session"] == "2022-03-08"
    assert sum(r["kind"] == "GAP_CORROBORATION" for r in plan["requests"]) == 15
    assert sum(r["kind"] == "ADJACENT_CONTROL" for r in plan["requests"]) == 2
    assert sum(r["kind"] == "CONDITIONAL_RAW_BASIS_DIAGNOSTIC" for r in plan["requests"]) == 5
    assert all(
        "apiKey" not in json.dumps(r) and "SPY" not in r["endpoint"] for r in plan["requests"]
    )


def approved_budget(report, journal, tmp_path, plan):
    write_json(report / "secondary_request_manifest_v1.json", plan)
    raw = journal.read_bytes()
    amendment = tmp_path / "budget.json"
    write_json(
        amendment,
        {
            "package": PACKAGE,
            "provider": "MASSIVE",
            "previous_cumulative_ceiling": 80,
            "cumulative_ceiling": 200,
            "per_page_lifetime_attempts": 3,
            "prior_journal_bytes": len(raw),
            "prior_journal_sha256": hashlib.sha256(raw).hexdigest(),
            "prior_attempts": 1,
            "request_manifest_sha256": digest(report / "secondary_request_manifest_v1.json"),
        },
    )
    return amendment


def test_budget_amendment_preserves_spent_attempts_and_does_not_clear_403(tmp_path, monkeypatch):
    report, env, _, journal, original, plan = reviewed_archive(tmp_path, monkeypatch)
    amendment = approved_budget(report, journal, tmp_path, plan)

    def forbidden(*args, **kwargs):
        raise AssertionError("A larger budget cannot clear an access hold")

    monkeypatch.setattr(secondary.requests, "get", forbidden)
    first = acquire_secondary(report, env, budget_amendment=amendment)
    assert first["attempts"] == 1 and first["remaining"] == 199
    assert first["attempt_ceiling"] == 200 and first["status"] == "HOLD"
    assert journal.read_bytes() == original
    # Later historical receipts extend the bound prefix; they still consume the total.
    with journal.open("ab") as stream:
        for record in [
            {"kind": "ATTEMPT", "attempt_id": 2, "page_hash": plan["requests"][0]["request_hash"]},
            {"kind": "RESULT", "attempt_id": 2, "status": 403},
        ]:
            stream.write((json.dumps(record) + "\n").encode())
    second = acquire_secondary(report, env, budget_amendment=amendment)
    assert second["attempts"] == 2 and second["remaining"] == 198
    assert journal.read_bytes().startswith(original)


@pytest.mark.parametrize(
    "field, value",
    [
        ("cumulative_ceiling", 201),
        ("prior_attempts", 0),
        ("per_page_lifetime_attempts", 4),
    ],
)
def test_budget_amendment_rejects_unapproved_limit_or_reset(tmp_path, monkeypatch, field, value):
    report, env, _, journal, original, plan = reviewed_archive(tmp_path, monkeypatch)
    amendment = approved_budget(report, journal, tmp_path, plan)
    bad = tmp_path / "bad_budget.json"
    write_json(bad, json.loads(amendment.read_text()) | {field: value})
    with pytest.raises(DataAccessError, match="AMENDMENT"):
        acquire_secondary(report, env, budget_amendment=bad)
    assert journal.read_bytes() == original


def test_secondary_native_labels_and_unknown_volume_publication_are_not_alpaca():
    request = secondary_plan()["requests"][0]
    t = pd.Timestamp(request["start"])
    payload = {
        "ticker": request["symbol"],
        "adjusted": True,
        "resultsCount": 1,
        "results": [{"t": t.value // 1_000_000, "o": 10, "h": 11, "l": 9, "c": 10, "v": 100}],
    }
    frame = parse_secondary(payload, request)
    assert frame.timestamp.iloc[0] == t and frame.provider.iloc[0] == "MASSIVE"
    assert frame.volume_unit.iloc[0] == "VENDOR_NATIVE_SHARES_UNVERIFIED_ADJUSTMENT"
    assert "feed" not in frame
    with pytest.raises(DataAccessError, match="ADJUSTMENT"):
        parse_secondary(payload | {"adjusted": False}, request)
    with pytest.raises(DataAccessError, match="INCOMPLETE"):
        parse_secondary(payload | {"next_url": "private-cursor"}, request)
    with pytest.raises(DataAccessError, match="TRUNCATION"):
        parse_secondary(payload | {"resultsCount": 2}, request)
    with pytest.raises(DataAccessError, match="BOUNDARY"):
        parse_secondary(
            payload | {"results": [payload["results"][0] | {"t": t.value // 1_000_000 - 1}]},
            request,
        )
