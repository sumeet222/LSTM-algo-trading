"""Bounded provider-native Massive corroboration; no automatic source mixing/activation."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from .alpaca import DataAccessError
from .config import atomic_new, digest, fingerprint, now, write_json
from .remediation import ARCHIVE, ORIGINAL_REPORT
from .remediation_plan import PACKAGE, gap_keys
from .remediation_transport import RemediationTransport, StorageLimit
from .stock_source import StockCalendar
from .validation import normalize, require_valid

SECONDARY_ARCHIVE = Path("data/raw/massive/track_a_gap_candidate_v1")
SECONDARY_VERSION = "MASSIVE_NATIVE_30MIN_CANDIDATE_V1"


def secondary_plan() -> dict:
    """Only unresolved original native sessions and two tight whole-gap controls."""
    qa = json.loads((ORIGINAL_REPORT / "ft0_source_qa.json").read_text())
    cal = StockCalendar("2021-01-01", "2022-12-31")
    rows = []

    def add(
        symbol: str,
        day: str,
        kind: str,
        start: pd.Timestamp,
        stop: pd.Timestamp,
        *,
        adjusted: bool = True,
    ) -> None:
        lower, upper = start.value // 1_000_000, stop.value // 1_000_000 - 1
        endpoint = (
            f"https://api.massive.com/v2/aggs/ticker/{symbol}/range/30/minute/{lower}/{upper}"
        )
        query = {"adjusted": "true" if adjusted else "false", "sort": "asc", "limit": 50000}
        value = {
            "symbol": symbol,
            "session": day,
            "kind": kind,
            "endpoint": endpoint,
            "query": query,
            "start": start.isoformat(),
            "stop_exclusive": stop.isoformat(),
            "provider": "MASSIVE",
            "available_at": None,
            "availability_basis": "UNKNOWN",
        }
        value["request_hash"] = fingerprint(value)
        rows.append(value)

    for (symbol, day), missing in gap_keys(qa).items():
        clock = cal.clock(day)
        assert clock.open is not None and clock.close is not None
        add(symbol, day, "GAP_CORROBORATION", clock.open, clock.close)
        if len(missing) == 13:
            previous = cal.days[cal.days.index(day) - 1]
            prev = cal.clock(previous)
            assert prev.close is not None
            add(
                symbol, previous, "ADJACENT_CONTROL", prev.close - pd.Timedelta(hours=1), prev.close
            )
        if symbol == "WMT":
            # Diagnose share basis; never infer original publication or action vintage.
            add(
                symbol,
                day,
                "CONDITIONAL_RAW_BASIS_DIAGNOSTIC",
                clock.open,
                clock.close,
                adjusted=False,
            )
    # Probe the most recent disputed date first; an access denial here blocks older history too.
    rows.sort(key=lambda r: (r["session"], r["kind"] == "GAP_CORROBORATION"), reverse=True)
    assert len(rows) * 3 <= 80
    return {
        "package": PACKAGE,
        "version": 1,
        "requests": rows,
        "new_provider_attempt_ceiling": 80,
        "same_page_lifetime_attempts": 3,
        "maximum_declared_attempt_envelope": len(rows) * 3,
        "storage_scope": "Shared256MiB with primary acquisition and QA",
        "authentication": "Bearer header; no query credential or persisted token",
        "contract_docs": [
            "https://massive.com/docs/rest/quickstart",
            "https://www.massive.com/docs/rest/stocks/aggregates/custom-bars",
        ],
        "source_status": "SECONDARY_CANDIDATE_ONLY_NOT_ACTIVATED",
        "volume_unit": "UNVERIFIED_UNTIL_RAW_ADJUSTED_CONTROLS_AND_CORPORATE_ACTION_EVIDENCE",
        "historical_publication": "UNKNOWN",
    }


def secondary_paths(request: dict) -> tuple[Path, Path]:
    stem = f"{request['symbol']}-{request['session']}-{request['request_hash'][:20]}"
    return SECONDARY_ARCHIVE / f"{stem}.parquet", SECONDARY_ARCHIVE / f"{stem}.manifest.json"


def parse_secondary(payload: dict, request: dict) -> pd.DataFrame:
    """Exact native 30Min starts and raw volume retained; never labeled Alpaca SIP."""
    adjusted = request["query"]["adjusted"] == "true"
    if payload.get("ticker") != request["symbol"] or payload.get("adjusted") is not adjusted:
        raise DataAccessError("MASSIVE_TICKER_OR_ADJUSTMENT_RESPONSE_MISMATCH")
    if payload.get("next_url"):
        raise DataAccessError("MASSIVE_INCOMPLETE_PAGE_HOLD_NO_PARTIAL_PUBLICATION")
    bars = payload.get("results", [])
    if not isinstance(bars, list) or payload.get("resultsCount", len(bars)) != len(bars):
        raise DataAccessError("MASSIVE_SCHEMA_OR_TRUNCATION_MISMATCH")
    rows = []
    for bar in bars:
        if not isinstance(bar, dict):
            raise DataAccessError("MASSIVE_INVALID_BAR_SCHEMA")
        try:
            rows.append(
                {
                    "symbol": request["symbol"],
                    "timestamp": pd.Timestamp(bar["t"], unit="ms", tz="UTC"),
                    "open": bar["o"],
                    "high": bar["h"],
                    "low": bar["l"],
                    "close": bar["c"],
                    "volume": bar["v"],
                }
            )
        except (KeyError, TypeError, ValueError):
            raise DataAccessError("MASSIVE_NATIVE_BAR_FIELDS_REQUIRED") from None
    frame = normalize(
        pd.DataFrame(
            rows, columns=["symbol", "timestamp", "open", "high", "low", "close", "volume"]
        ),
        stocks=True,
    )
    require_valid(frame, stocks=True)
    lower, upper = pd.Timestamp(request["start"]), pd.Timestamp(request["stop_exclusive"])
    if ((frame.timestamp < lower) | (frame.timestamp >= upper)).any():
        raise DataAccessError("MASSIVE_EXPANDED_BAR_BOUNDARY_HOLD")
    if ((frame.timestamp.dt.minute.mod(30) != 0) | (frame.timestamp.dt.second != 0)).any():
        raise DataAccessError("MASSIVE_OFF_NATIVE30MIN_GRID")
    frame["provider"] = "MASSIVE"
    frame["source_timeframe"] = "30Min"
    frame["claimed_adjustment"] = "split" if adjusted else "raw"
    frame["volume_unit"] = "VENDOR_NATIVE_SHARES_UNVERIFIED_ADJUSTMENT"
    frame["provenance_id"] = request["request_hash"]
    return frame


def read_secondary(request: dict) -> tuple[pd.DataFrame, dict] | None:
    data, meta = secondary_paths(request)
    if not data.exists() and not meta.exists():
        return None
    if not data.exists() or not meta.exists():
        raise ValueError("MASSIVE_INTERRUPTED_PAIR_REVIEW_REQUIRED")
    manifest = json.loads(meta.read_text())
    if (
        manifest["source_version"] != SECONDARY_VERSION
        or manifest["request"] != request
        or manifest["sha256"] != digest(data)
        or not manifest["terminal_page"]
    ):
        raise ValueError("MASSIVE_SOURCE_OR_CHECKSUM_MISMATCH")
    frame = normalize(pd.read_parquet(data), stocks=True)
    require_valid(frame, stocks=True)
    if len(frame) != manifest["rows"]:
        raise ValueError("MASSIVE_MANIFEST_ROWS_MISMATCH")
    return frame, manifest


def register_access_review(
    sink: RemediationTransport, review_path: Path, validation_request_hash: str
) -> None:
    """Record explicit renewed access authority without resetting failed attempts.

    Only a prior 403 can be reviewed. A fresh 401/429 needs separate resolution;
    the renewed historical check gets one attempt, including transport failures.
    """
    review = json.loads(review_path.read_text())
    records = sink.records()
    for record in records:
        if record.get("kind") == "ACCESS_REVIEW" and record.get("review_id") == review.get(
            "review_id"
        ):
            if (
                record.get("review_sha256") != digest(review_path)
                or record.get("validation_request_hash") != validation_request_hash
            ):
                raise DataAccessError("MASSIVE_ACCESS_REVIEW_BINDING_REQUIRED")
            return  # Resuming this authority never grants another validation attempt.
    results = [r for r in records if r.get("kind") == "RESULT"]
    if (
        review.get("package") != PACKAGE
        or not isinstance(review.get("review_id"), str)
        or not review["review_id"].strip()
        or review.get("prior_journal_sha256") != sink.expected_sha
        or review.get("prior_attempts") != sink.used
        or review.get("validation_request_hash") != validation_request_hash
        or not results
        or records[-1].get("kind") != "RESULT"
        or results[-1].get("status") != 403
        or any(r.get("status") in (401, 429) for r in records)
    ):
        raise DataAccessError("MASSIVE_ACCESS_REVIEW_BINDING_REQUIRED")
    sink.append(
        {
            "kind": "ACCESS_REVIEW",
            "provider": "MASSIVE",
            "review_id": review["review_id"],
            "review_sha256": digest(review_path),
            "prior_journal_sha256": sink.expected_sha,
            "prior_attempts": sink.used,
            "validation_request_hash": validation_request_hash,
            "time_utc": now(),
        }
    )


def access_hold(records: list[dict], request_hash: str) -> bool:
    """Allow one reviewed historical check; require its success before more GETs."""
    reviews = [i for i, r in enumerate(records) if r.get("kind") == "ACCESS_REVIEW"]
    if not reviews:
        return any(r.get("status") in (401, 403, 429) for r in records)
    index = reviews[-1]
    review = records[index]
    after = records[index + 1 :]
    if any(r.get("status") in (401, 429) for r in records[:index]):
        return True
    if any(r.get("status") in (401, 403, 429) for r in after):
        return True
    attempts = [r for r in after if r.get("kind") == "ATTEMPT"]
    if not attempts:
        return request_hash != review["validation_request_hash"]
    first = attempts[0]
    return first.get("request_hash") != review["validation_request_hash"] or not any(
        r.get("kind") == "RESULT"
        and r.get("attempt_id") == first["attempt_id"]
        and r.get("status") == 200
        for r in after
    )


def secondary_ceiling(amendment: Path | None, journal: Path, manifest: Path) -> int:
    """Apply the human-approved 200 total attempts against preserved prior history.

    The original 80-attempt plan remains immutable. An additive amendment binds
    the enlarged ceiling to its journal prefix and identical frozen requests.
    Budget authority does not grant access or clear any transport denial.
    """
    if amendment is None:
        return 80
    value = json.loads(amendment.read_text())
    length = value.get("prior_journal_bytes")
    if (
        value.get("package") != PACKAGE
        or value.get("provider") != "MASSIVE"
        or value.get("previous_cumulative_ceiling") != 80
        or value.get("cumulative_ceiling") != 200
        or value.get("per_page_lifetime_attempts") != 3
        or value.get("request_manifest_sha256") != digest(manifest)
        or not isinstance(length, int)
        or isinstance(length, bool)
        or length <= 0
        or not journal.exists()
    ):
        raise DataAccessError("MASSIVE_BUDGET_AMENDMENT_BINDING_REQUIRED")
    raw = journal.read_bytes()
    prefix = raw[:length]
    if (
        len(prefix) != length
        or not prefix.endswith(b"\n")
        or hashlib.sha256(prefix).hexdigest() != value.get("prior_journal_sha256")
        or sum(json.loads(line).get("kind") == "ATTEMPT" for line in prefix.splitlines())
        != value.get("prior_attempts")
    ):
        raise DataAccessError("MASSIVE_BUDGET_AMENDMENT_HISTORY_CHANGED")
    return 200


def acquire_secondary(
    report: Path,
    env_file: Path,
    *,
    access_review: Path | None = None,
    budget_amendment: Path | None = None,
) -> dict:
    plan = secondary_plan()
    existing = report / "secondary_request_manifest_v1.json"
    if existing.exists():
        if json.loads(existing.read_text()) != plan:
            raise ValueError("MASSIVE_FROZEN_REQUEST_MANIFEST_CHANGED")
    else:
        write_json(existing, plan)
    load_dotenv(env_file, override=False)
    key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY")
    if not key:
        raise DataAccessError("MASSIVE_KEY_NOT_PROVISIONED_NO_SECRET_SEARCH")
    journal = SECONDARY_ARCHIVE / "source_transport_journal.jsonl"
    ceiling = secondary_ceiling(budget_amendment, journal, existing)
    limit = StorageLimit((ARCHIVE, SECONDARY_ARCHIVE, report))
    sink = RemediationTransport(
        journal,
        (),
        ceiling=ceiling,
        expected_sha=digest(journal) if journal.exists() else None,
        before_append=limit.reserve,
    )
    if access_review is not None:
        register_access_review(sink, access_review, plan["requests"][0]["request_hash"])
    results = []
    blocked = None
    for request in plan["requests"]:
        saved = read_secondary(request)
        if saved is not None:
            results.append(
                {
                    "request_hash": request["request_hash"],
                    "rows": len(saved[0]),
                    "status": "SHA_VERIFIED_RESUME",
                    "sha256": saved[1]["sha256"],
                }
            )
            continue
        for retry in range(3):
            records = sink.records()
            if (
                sink.used >= ceiling
                or access_hold(records, request["request_hash"])
                or sum(
                    r["kind"] == "ATTEMPT" and r["page_hash"] == request["request_hash"]
                    for r in records
                )
                >= 3
            ):
                blocked = "MASSIVE_ACCESS_RATE_OR_BUDGET_HOLD"
                break
            attempt = sink.used + 1
            sink.append(
                {
                    "kind": "ATTEMPT",
                    "provider": "MASSIVE",
                    "attempt_id": attempt,
                    "page_hash": request["request_hash"],
                    "request_hash": request["request_hash"],
                    "endpoint": request["endpoint"],
                    "query": request["query"],
                    "time_utc": now(),
                }
            )
            response = None
            try:
                response = requests.get(
                    request["endpoint"],
                    params=request["query"],
                    headers={"Authorization": f"Bearer {key}"},
                    timeout=30,
                    allow_redirects=False,
                )
                status = response.status_code
            except requests.RequestException:
                status = "TRANSPORT_ERROR"
            receipt = {
                "kind": "RESULT",
                "provider": "MASSIVE",
                "attempt_id": attempt,
                "request_hash": request["request_hash"],
                "status": status,
                "time_utc": now(),
            }
            if response is not None:
                receipt.update(
                    response_sha256=hashlib.sha256(response.content).hexdigest(),
                    bytes=len(response.content),
                )
            sink.append(receipt)
            if status == 200 and response is not None:
                try:
                    payload = response.json()
                    if not isinstance(payload, dict):
                        raise DataAccessError("MASSIVE_OBJECT_RESPONSE_REQUIRED")
                    frame = parse_secondary(payload, request)
                    buffer = io.BytesIO()
                    frame.to_parquet(buffer, index=False, compression="zstd")
                    raw = buffer.getvalue()
                    manifest = {
                        "source_version": SECONDARY_VERSION,
                        "provider": "MASSIVE",
                        "request": request,
                        "rows": len(frame),
                        "retrieved_at": now(),
                        "sha256": hashlib.sha256(raw).hexdigest(),
                        "receipt": receipt,
                        "terminal_page": True,
                        "available_at": None,
                        "availability_basis": "UNKNOWN",
                        "action_vintage": "UNVERIFIED",
                        "volume_unit": "UNVERIFIED_NATIVE",
                        "activation": False,
                    }
                    limit.reserve(len(raw) + len(json.dumps(manifest).encode()) + 1024)
                    data, meta = secondary_paths(request)
                    atomic_new(data, raw)
                    write_json(meta, manifest)
                    results.append(
                        {
                            "request_hash": request["request_hash"],
                            "rows": len(frame),
                            "sha256": manifest["sha256"],
                            "status": "VERIFIED_NATIVE_CANDIDATE",
                        }
                    )
                except (ValueError, DataAccessError):
                    blocked = "MASSIVE_SCHEMA_BOUNDARY_OR_ADJUSTMENT_HOLD"
                break
            if status in (401, 403, 429) or (isinstance(status, int) and status < 500):
                blocked = f"MASSIVE_HTTP_{status}_NO_ACCESS_CHANGE_OR_RETRY"
                break
            if retry == 2:
                blocked = "MASSIVE_TRANSIENT_RETRIES_EXHAUSTED"
                break
            time.sleep(1 + retry)
        if blocked is not None:
            break
        time.sleep(0.4)
    value = {
        "provider": "MASSIVE",
        "status": "COMPLETE_CANDIDATE_ONLY" if blocked is None else "HOLD",
        "attempts": sink.used,
        "remaining": max(0, ceiling - sink.used),
        "attempt_ceiling": ceiling,
        "budget_amendment_sha256": digest(budget_amendment) if budget_amendment else None,
        "blocked": blocked,
        "results": results,
        "journal": journal.as_posix(),
        "journal_sha256": digest(journal),
        "original_and_Alpaca_source_activation": False,
        "scientific_activation": False,
        "key_presence_checked": True,
        "no_purchase_contract_or_credential_created": True,
    }
    runs = report / "secondary_runs"
    number = len(list(runs.glob("*.json"))) + 1 if runs.exists() else 1
    write_json(runs / f"run_{number:03d}.json", value)
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--authorization", required=True)
    parser.add_argument(
        "--access-review", type=Path, help="Explicit journal-bound renewed historical access review"
    )
    parser.add_argument(
        "--budget-amendment", type=Path, help="Explicit journal-bound cumulative budget increase"
    )
    args = parser.parse_args()
    if args.authorization != PACKAGE:
        parser.error("explicit remediation package authorization required")
    value = acquire_secondary(
        args.report,
        args.env_file,
        access_review=args.access_review,
        budget_amendment=args.budget_amendment,
    )
    print(
        {
            "status": value["status"],
            "attempts": value["attempts"],
            "remaining": value["remaining"],
            "blocked": value["blocked"],
        }
    )
    return 0 if value["blocked"] is None else 2


if __name__ == "__main__":
    raise SystemExit(main())
