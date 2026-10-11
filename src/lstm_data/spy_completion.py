"""Versioned bounded SPY completion using the existing source/client/store APIs."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

import pandas as pd
import requests
from dotenv import load_dotenv

from .alpaca import DataAccessError, HistoricalClient, credentials
from .calendar import schedule
from .config import digest, fingerprint, now, write_json
from .ledger import parse_json
from .market_source import PILOT_DATES, AttemptBudget, MarketSource, acquire_partition, load_archive
from .store import chunk_paths, read_verified


@dataclass
class ReplayTransport:
    """Reuse genuine diagnostic responses in memory; nothing secret/body-sized in reports.

    After a crash no cache is claimed. Completed partitions resume by SHA; incomplete
    partitions are re-requested, with every retry counted against the durable journal.
    """

    budget: AttemptBudget
    diagnostic_start: int
    diagnostic: bool = True
    cache: dict[str, requests.Response] = field(default_factory=dict, repr=False)
    repeated_429: int = 0
    replayed_pages: int = 0
    last_response: requests.Response | None = field(default=None, repr=False)
    before_page: Callable[[], None] | None = field(default=None, repr=False)
    after_page: Callable[[dict], None] | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.budget.journal.exists():
            self.repeated_429 = sum(parse_json(line).get("status") == 429
                                    for line in self.budget.journal.read_bytes().splitlines())

    def get(self, url: str, **kwargs) -> requests.Response:
        if self.repeated_429 >= 2:
            raise DataAccessError("SPY_REPEATED_429_STOP")
        key = fingerprint(kwargs.get("params", {}))
        if key in self.cache:
            self.replayed_pages += 1
            self.last_response = self.cache[key]
            return self.last_response
        if self.diagnostic and self.budget.used >= self.diagnostic_start + 4:
            raise DataAccessError("SPY_DIAGNOSTIC_FOUR_TRANSPORT_CEILING")
        if self.before_page:
            self.before_page()
        response = self.budget.get(url, **kwargs)
        if response.status_code == 429:
            self.repeated_429 += 1
            if self.repeated_429 > 1:
                raise DataAccessError("SPY_REPEATED_429_STOP")
        if response.status_code == 200:
            payload = response.json()
            token = payload.get("next_page_token") if isinstance(payload, dict) else None
            if token is not None and not isinstance(token, str):
                raise DataAccessError("SPY_INVALID_CONTINUATION_TYPE")
            if self.budget.ceiling != 900:
                self.cache[key] = response
            self.last_response = response
            if self.after_page:
                self.after_page(payload)
        return response

    def completion_audit(self) -> dict:
        response = self.last_response
        if (response is None or response.status_code != 200
                or response.json().get("next_page_token")):
            raise DataAccessError("SPY_TERMINAL_RESPONSE_REQUIRED_BEFORE_PUBLISH")
        return {"pagination_exhausted": True, "terminal_status": 200,
                "terminal_response_sha256": hashlib.sha256(response.content).hexdigest(),
                "terminal_response_bytes": len(response.content),
                "source_clock": "PUBLICATION_UNKNOWN"}


def diagnostic(client: HistoricalClient, source: MarketSource, transport: ReplayTransport) -> dict:
    """At most four new transports, including retries; explicit continuation is terminal proof."""
    params = source.partitions()[0]
    pages = []
    continuation = None
    seen = set()
    for index in range(1, 5):
        if transport.budget.used >= transport.diagnostic_start + 4:
            break
        request = params | ({"page_token": continuation} if continuation else {})
        payload = client._request(request)
        bars = payload["bars"].get("SPY", [])
        if set(payload["bars"]) - {"SPY"} or not isinstance(bars, list):
            raise DataAccessError("SPY_DIAGNOSTIC_SCHEMA_MISMATCH")
        continuation = payload.get("next_page_token")
        pages.append({"page_index": index, "requested_limit": params["limit"],
                      "returned_rows": len(bars), "request_key": fingerprint(request),
                      "first_timestamp": bars[0]["t"] if bars else None,
                      "last_timestamp": bars[-1]["t"] if bars else None,
                      "has_continuation": bool(continuation), "status": 200})
        response = transport.cache[fingerprint(request)]
        pages[-1].update({"response_bytes": len(response.content),
                         "response_sha256": hashlib.sha256(response.content).hexdigest(),
                         "retrieved_at": now(), "asof": params["asof"],
                         "rate_limit_remaining": response.headers.get("X-RateLimit-Remaining")})
        if not continuation:
            break
        if not isinstance(continuation, str) or continuation in seen:
            raise DataAccessError("SPY_DIAGNOSTIC_UNSTABLE_CONTINUATION")
        seen.add(continuation)
    return {"time_utc": now(), "start_attempts": transport.diagnostic_start,
            "new_transport_attempts": transport.budget.used - transport.diagnostic_start,
            "cumulative_attempts": transport.budget.used, "params": params, "pages": pages,
            "exhausted_first_partition": bool(pages) and not pages[-1]["has_continuation"],
            "response_storage": "Temporary genuine responses eligible for in-memory reuse only "
                                "if plan is feasible; no durable partial-page recovery claimed",
            "journal": "data/raw/alpaca/track_a_spy_v1/transport_attempts.jsonl"}


def acquisition_plan(
    source: MarketSource, evidence: dict, used: int, *, cached_pages: int | None = None,
) -> dict:
    """Conservative density/calendar bound, including three attempts per page and rounding."""
    full_pages = [p["returned_rows"] for p in evidence["pages"] if p["has_continuation"]]
    if not full_pages or min(full_pages) <= 0:
        raise DataAccessError("SPY_PAGE_DENSITY_NOT_ESTABLISHED")
    density = min(full_pages)
    partitions = []
    for params in source.partitions():
        start = pd.Timestamp(params["start"]).tz_convert("America/New_York").date().isoformat()
        end = pd.Timestamp(params["end"]).tz_convert("America/New_York").date().isoformat()
        sessions = len(schedule(start, end))
        # Expected 48 half-hours per exchange session is the inherited estimate.
        # A 24-hour EVERY calendar day envelope also covers anomalous off-session data.
        days = (pd.Timestamp(end) - pd.Timestamp(start)).days + 1
        upper_rows = days * 48
        pages = math.ceil(upper_rows / density)
        data, manifest = chunk_paths(source.store, params)
        complete = data.exists() and manifest.exists()
        if complete:
            read_verified(data, manifest, params)
        partitions.append({"request_key": fingerprint(params), "params": params,
                           "sessions": sessions, "estimated_rows": sessions * 48,
                           "calendar_day_row_upper_bound": upper_rows,
                           "upper_pages": pages, "already_complete": complete,
                           "path": str(data.relative_to(source.root))})
    new_upper = sum(p["upper_pages"] * 3 for p in partitions if not p["already_complete"])
    # Genuine cached first pages do not consume transports again, including retries.
    if source.config.get("acquisition_policy_version") == 3:
        if cached_pages not in (None, 0):
            raise DataAccessError("SPY_V3_DISCARDED_CACHE_CANNOT_BE_REUSED")
        cached = 0
    else:
        cached = len(evidence["pages"]) if cached_pages is None else cached_pages
    new_upper = max(0, new_upper - cached * 3)
    estimate_bytes = sum(p["calendar_day_row_upper_bound"] for p in partitions) * 256
    ceiling = cast(int, source.config["max_transport_attempts"])
    max_pages = cast(int, source.config["max_pages_per_request"])
    max_parts = cast(int, source.config["max_partitions"])
    feasible = (used + new_upper <= ceiling and len(partitions) <= max_parts
                and max(p["upper_pages"] for p in partitions) <= max_pages
                and estimate_bytes <= 256 * 1024**2)
    return {"version": source.config.get("acquisition_policy_version"),
            "source_version": source.config["source_version"],
            "config_id": source.identity, "density_lower_bound_observed": density,
            "partitions": partitions, "unique_partitions": len(partitions),
            "expected_session_rows": sum(p["estimated_rows"] for p in partitions),
            "used_attempts": used, "actual_cached_pages": cached,
            "upper_additional_attempts_with_retries": new_upper,
            "upper_cumulative_attempts": used + new_upper,
            "estimated_storage_upper_bytes": estimate_bytes,
            "limits": {"cumulative_attempts": ceiling, "partitions": max_parts,
                       "pages_per_partition": max_pages,
                       "additional_disk_bytes": 256 * 1024**2, "attempts_per_page": 3},
            "retry": source.config["retry"],
            "restart": "python -m lstm_data.spy_completion --env-file .env --report "
                       "reports/data_audit/ta_mkt_spy_00"
                       f"{source.config.get('acquisition_policy_version')}_2026-10-11",
            "status": "FEASIBLE" if feasible else "SOURCE_BLOCKED",
            "density_caveat": "Measured page density is a planning bound, not provider guarantee. "
                              "Recompute remaining budget if actual pages exceed planned bound.",
            "asof_meaning": "Entity mapping only; publication UNKNOWN",
            "partial_checkpoint_policy": "No partial durable cache; retry incomplete partition. "
                                         "Never refetch completed SHA-verified partition."}


def archive_complete(source: MarketSource) -> dict:
    """Deterministic fail-closed proof: all fixed keys, SHA checks, range and unique rows."""
    params_list = source.partitions()
    if len(params_list) != 11 or any(
        pd.Timestamp(b["start"]) != pd.Timestamp(a["end"]) + pd.Timedelta(nanoseconds=1)
        for a, b in zip(params_list, params_list[1:])
    ):
        raise ValueError("SPY_CONTIGUOUS_ELEVEN_PARTITIONS_REQUIRED")
    frame = load_archive(source)
    manifests = []
    for params in source.partitions():
        data, manifest_path = chunk_paths(source.store, params)
        manifest = parse_json(manifest_path.read_bytes())
        if not manifest["events"] or manifest["events"][-1]["status"] != 200:
            raise ValueError("SPY_COMPLETION_EVENTS_REQUIRED")
        audit = manifest.get("coverage_audit")
        if not isinstance(audit, dict) or audit.get("pagination_exhausted") is not True:
            raise ValueError("SPY_VERIFIED_TERMINAL_RESPONSE_REQUIRED")
        manifests.append({"request_key": fingerprint(params), "params": params,
                          "path": str(data.relative_to(source.root)), "sha256": digest(data),
                          "manifest_sha256": digest(manifest_path), "rows": manifest["rows"],
                          "bytes": data.stat().st_size,
                          "manifest_bytes": manifest_path.stat().st_size,
                          "first_timestamp": manifest["coverage"]["SPY"]["first"],
                          "last_timestamp": manifest["coverage"]["SPY"]["last"],
                          "pagination_exhausted": audit["pagination_exhausted"],
                          "terminal_response_sha256": audit.get("terminal_response_sha256"),
                          "request_event_sha256": fingerprint(manifest["events"]),
                          "pages": sum(e["status"] == 200 for e in manifest["events"])})
    if sum(m["rows"] for m in manifests) != len(frame):
        raise ValueError("SPY_ARCHIVE_ROW_COUNTS_MISMATCH")
    return {"status": "SOURCE_ARCHIVE_COMPLETE", "archive_complete": True,
            "partitions": manifests, "completed_partitions": len(manifests),
            "rows": len(frame), "bytes": sum(m["bytes"] for m in manifests),
            "source_version": source.config["source_version"],
            "native_first_utc": frame.timestamp.min().isoformat(),
            "native_last_utc": frame.timestamp.max().isoformat(),
            "publication_verified": False, "research_status": "BLOCKED"}


def storage_guard(source: MarketSource, report: Path, additional: int = 0) -> None:
    """Reserve actual new bytes before journal append or immutable chunk publication."""
    size = sum(p.stat().st_size for root in (source.store, report)
               for p in root.rglob("*") if p.is_file())
    if additional < 0 or size + additional > 256 * 1024**2:
        raise DataAccessError("SPY_DISK_CEILING_BEFORE_WRITE")
    if shutil.disk_usage(source.store).free < additional + 1024**2:
        raise DataAccessError("SPY_AVAILABLE_DISK_RESERVE_REQUIRED")


def write_bounded_report(source: MarketSource, report: Path, path: Path, value: object) -> None:
    """Reserve exact audit payload bytes before immutable report publication."""
    if path.parent != report:
        raise ValueError("SPY_REPORT_NAMESPACE_REQUIRED")
    payload_bytes = len((json.dumps(value, indent=2, sort_keys=True) + "\n").encode())
    storage_guard(source, report, payload_bytes)
    write_json(path, value)


def verify_historical_journal(source: MarketSource, budget: AttemptBudget) -> None:
    """Verify original 13 bytes and every appended attempt/result association on restart."""
    proof = parse_json((source.root / "reports/data_audit/ta_mkt_spy_002_2026-10-11/"
                        "transport_journal_proof.json").read_bytes())
    raw = budget.journal.read_bytes()
    prefix = raw[:proof["bytes"]]
    if (len(prefix) != proof["bytes"]
            or hashlib.sha256(prefix).hexdigest() != proof["sha256"]
            or not raw.endswith(b"\n")):
        raise DataAccessError("SPY_ORIGINAL_13_JOURNAL_PROOF_MISMATCH")
    prior = (source.root / proof["prior_evidence_ref"]).read_bytes()
    failure = parse_json((source.root / "reports/data_audit/ta_mkt_spy_2026-10-11/"
                          "source_failure_9.json").read_bytes())
    if failure.get("bulk_attempts") != 2 or failure.get("transport_attempts") != 9:
        raise DataAccessError("SPY_LEGACY_PAGE_EVIDENCE_MISMATCH")
    budget.legacy_first_partition_pages = 2
    budget.legacy_initial_page_attempts = 1
    budget.legacy_unknown_continued_attempts = 1
    if (prefix[:proof["prior_prefix_bytes"]] != prior
            or hashlib.sha256(prior).hexdigest() != proof["prior_prefix_sha256"]):
        raise DataAccessError("SPY_ORIGINAL_NINE_PREFIX_MISMATCH")
    attempts: dict[int, dict] = {}
    outcomes = set()
    count = 0
    for line in raw.splitlines():
        record = parse_json(line)
        if record.get("record_kind") != "result":
            count += 1
            if count > 9:
                if record.get("record_kind") != "attempt" or record.get("attempt_id") != count:
                    raise DataAccessError("SPY_ATTEMPT_ID_SEQUENCE_MISMATCH")
                attempts[count] = record
        else:
            identifier = record.get("attempt_id")
            if identifier not in attempts or identifier in outcomes:
                raise DataAccessError("SPY_RESULT_WITHOUT_UNIQUE_ATTEMPT")
            expected = attempts[identifier]["request_key"]
            if record.get("request_key", expected) != expected:
                raise DataAccessError("SPY_RECEIPT_REQUEST_KEY_MISMATCH")
            outcomes.add(identifier)
    if count != budget.used:
        raise DataAccessError("SPY_RESULT_DOUBLE_COUNT_DETECTED")
    budget.expected_journal_sha256 = hashlib.sha256(raw).hexdigest()


@dataclass
class RollingProgress:
    """Measured rolling envelope; progress is evidence, never a second attempt counter."""

    source: MarketSource
    report: Path
    budget: AttemptBudget
    plan: dict
    current: dict = field(default_factory=dict)
    pages: int = 0
    density: int = 0
    last_timestamp: pd.Timestamp | None = None

    def __post_init__(self) -> None:
        self.density = self.plan["density_lower_bound_observed"]

    def begin(self, partition: dict) -> None:
        self.current, self.pages, self.last_timestamp = partition, 0, None

    def remaining_bound(self) -> int:
        result = 0
        for partition in self.plan["partitions"]:
            data, manifest = chunk_paths(self.source.store, partition["params"])
            if data.exists() and manifest.exists():
                continue
            rows = partition["calendar_day_row_upper_bound"]
            if partition == self.current and self.last_timestamp is not None:
                stop = pd.Timestamp(partition["params"]["end"])
                # Calendar-time residual covers every possible remaining half-hour slot.
                rows = max(0, math.ceil((stop - self.last_timestamp).total_seconds() / 1800))
            pages = math.ceil(rows / self.density)
            if pages + (self.pages if partition == self.current else 0) > 32:
                raise DataAccessError("SPY_ROLLING_PAGE_BOUND_EXCEEDS_32")
            result += pages * 3
        return result

    def guard(self) -> None:
        storage_guard(self.source, self.report, 16 * 1024)
        if self.budget.used + self.remaining_bound() > self.budget.ceiling:
            raise DataAccessError("SPY_ROLLING_ATTEMPT_BOUND_EXCEEDS_CEILING")

    def record(self, kind: str) -> None:
        row = {"kind": kind, "time_utc": now(), "request_key": self.current["request_key"],
               "successful_pages_this_run": self.pages, "attempts_used": self.budget.used,
               "density_lower_bound": self.density,
               "remaining_attempt_upper": self.remaining_bound(),
               "canonical_bytes": sum(p.stat().st_size for p in self.source.store.rglob("*")
                                      if p.is_file())}
        payload = (json.dumps(row, sort_keys=True) + "\n").encode()
        storage_guard(self.source, self.report, len(payload))
        with (self.report / "acquisition_progress.jsonl").open("ab") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if kind == "partition_complete" or self.pages % 5 == 0:
            print(row, flush=True)

    def observe(self, payload: dict) -> None:
        bars = payload.get("bars", {}).get("SPY", [])
        if not isinstance(bars, list):
            raise DataAccessError("SPY_PAGE_SCHEMA_MISMATCH")
        self.pages += 1
        if bars:
            stamps = [pd.Timestamp(b["t"]) for b in bars]
            if (any(a >= b for a, b in zip(stamps, stamps[1:]))
                    or (self.last_timestamp is not None and stamps[0] <= self.last_timestamp)):
                raise DataAccessError("SPY_PAGE_ORDER_OR_DUPLICATE_MISMATCH")
            self.last_timestamp = stamps[-1]
        if payload.get("next_page_token"):
            if not bars:
                raise DataAccessError("SPY_EMPTY_CONTINUED_PAGE")
            self.density = min(self.density, len(bars))
        self.record("page_received")

    def finished(self, manifest: dict) -> None:
        if manifest.get("coverage_audit", {}).get("pagination_exhausted") is not True:
            raise DataAccessError("SPY_CHECKPOINT_TERMINALITY_REQUIRED")
        self.record("partition_complete")


def complete(source: MarketSource, report: Path, env_file: Path | None) -> int:
    version = source.config.get("acquisition_policy_version")
    if version not in (2, 3):
        raise ValueError("TA_MKT_SPY_002_VERSIONED_POLICY_REQUIRED")
    def emit(path: Path, value: dict) -> None:
        if version == 3:
            write_bounded_report(source, report, path, value)
        else:
            write_json(path, value)

    prior = source.root / "reports/data_audit/ta_mkt_spy_2026-10-11/pilot.json"
    evidence = parse_json(prior.read_bytes())
    if (evidence.get("pilot_pass") is not True
            or evidence.get("source_version") != source.config["source_version"]
            or [d["session"] for d in evidence.get("days", [])] != list(PILOT_DATES)
            or any(d["params"] != source.interval(
                d["session"], (pd.Timestamp(d["session"]) + pd.Timedelta(days=1)).date().isoformat()
            ) for d in evidence["days"])):
        raise ValueError("INHERITED_MATCHING_SPY_SOURCE_PILOT_REQUIRED")
    if env_file:
        load_dotenv(env_file, override=False)
    key, secret = credentials()
    budget = AttemptBudget(source.store / "transport_attempts.jsonl", f"SPY00{version}",
                           cast(int, source.config["max_transport_attempts"]),
                           fixed_requests=tuple(source.partitions()))
    transport = ReplayTransport(budget, budget.used)
    client = HistoricalClient(source.config, key, secret, get=transport.get)
    lock = source.store / ".acquire.lock"
    source.store.mkdir(parents=True, exist_ok=True)
    with lock.open("x"):
        pass
    try:
        if version == 3:
            verify_historical_journal(source, budget)
            budget.before_write = lambda size: storage_guard(source, report, size)
        plan_path = report / f"acquisition_plan_v{version}.json"
        if plan_path.exists():
            plan = parse_json(plan_path.read_bytes())
            if plan["config_id"] != source.identity or plan["status"] != "FEASIBLE":
                raise ValueError("SPY_MATCHING_FEASIBLE_PLAN_REQUIRED")
        else:
            if version == 3:
                evidence = parse_json((source.root / "reports/data_audit/"
                    "ta_mkt_spy_002_2026-10-11/pagination_diagnostic.json").read_bytes())
                plan = acquisition_plan(source, evidence, budget.used, cached_pages=0)
                plan["prior_restart_upper"] = 853
                plan["disk_free_bytes"] = shutil.disk_usage(source.store).free
                plan["prior_measurement_ref"] = (
                    "reports/data_audit/ta_mkt_spy_002_2026-10-11/pagination_diagnostic.json")
            else:
                evidence = diagnostic(client, source, transport)
                emit(report / "pagination_diagnostic.json", evidence)
                plan = acquisition_plan(source, evidence, budget.used)
            emit(plan_path, plan)
        if plan["status"] != "FEASIBLE":
            raise DataAccessError("SPY_MEASURED_PLAN_EXCEEDS_AUTHORIZED_CEILINGS")
        if [p["params"] for p in plan["partitions"]] != source.partitions():
            raise ValueError("SPY_PLAN_FIXED_REQUEST_IDENTITIES_REQUIRED_NO_FALLBACK")
        transport.diagnostic = False
        progress = RollingProgress(source, report, budget, plan) if version == 3 else None
        for partition in plan["partitions"]:
            if progress:
                progress.begin(partition)
                transport.before_page = progress.guard
                transport.after_page = progress.observe
            if sum(p.stat().st_size for p in source.store.rglob("*") if p.is_file()) \
                    > 256 * 1024**2:
                raise DataAccessError("SPY_DISK_CEILING")
            # Remaining conservative page envelope must still fit after errors/retries.
            remaining = [p for p in plan["partitions"]
                         if not chunk_paths(source.store, p["params"])[1].exists()]
            if budget.used + sum(p["upper_pages"] * 3 for p in remaining) \
                    - len(transport.cache) * 3 > budget.ceiling:
                raise DataAccessError("SPY_ROLLING_ATTEMPT_BOUND_EXCEEDS_CEILING")
            result = acquire_partition(source, client, partition["params"],
                                       completion_check=transport.completion_audit,
                                       before_publish=(lambda size: storage_guard(
                                           source, report, size))
                                       if version == 3 else None)
            actual_pages = sum(e["status"] == 200 for e in result["events"])
            if progress:
                progress.finished(result)
            if not progress and actual_pages > partition["upper_pages"]:
                raise DataAccessError("SPY_OBSERVED_PAGE_COUNT_EXCEEDS_PLAN_RECOMPUTE_REQUIRED")
            transport.cache.clear()
        proof = archive_complete(source)
        proof["transport_attempts"] = budget.used
        proof["diagnostic_pages_replayed_without_GET"] = transport.replayed_pages
        if not (report / "archive_manifest.json").exists():
            emit(report / "archive_manifest.json", proof)
        print({"status": proof["status"], "attempts": budget.used, "rows": proof["rows"]})
        return 0
    except (DataAccessError, ValueError, FileNotFoundError) as exc:
        failure = report / f"failure_{budget.used}.json"
        if failure.exists():
            suffix = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%S%fZ")
            failure = report / f"failure_{budget.used}_{suffix}.json"
        emit(failure, {"status": "SOURCE_BLOCKED",
                   "reason": str(exc), "transport_attempts": budget.used,
                   "completed_partitions": len(list(source.store.glob("*.manifest.json")))})
        return 2
    finally:
        lock.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/track_a_market_spy_v3.json"))
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args()
    return complete(MarketSource.load(args.config), args.report, args.env_file)


if __name__ == "__main__":
    raise SystemExit(main())
