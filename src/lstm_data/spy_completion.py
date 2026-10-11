"""Bounded TA-MKT-SPY-002 orchestration around the existing source/client/store APIs."""

from __future__ import annotations

import argparse
import hashlib
import math
from dataclasses import dataclass, field
from pathlib import Path

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
            self.cache[key] = response
            self.last_response = response
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


def acquisition_plan(source: MarketSource, evidence: dict, used: int) -> dict:
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
    cached = len(evidence["pages"])
    new_upper = max(0, new_upper - cached * 3)
    estimate_bytes = sum(p["calendar_day_row_upper_bound"] for p in partitions) * 256
    feasible = (used + new_upper <= 240 and len(partitions) <= 96
                and max(p["upper_pages"] for p in partitions) <= 12
                and estimate_bytes <= 256 * 1024**2)
    return {"version": 2, "source_version": source.config["source_version"],
            "config_id": source.identity, "density_lower_bound_observed": density,
            "partitions": partitions, "unique_partitions": len(partitions),
            "expected_session_rows": sum(p["estimated_rows"] for p in partitions),
            "used_attempts": used, "upper_additional_attempts_with_retries": new_upper,
            "upper_cumulative_attempts": used + new_upper,
            "estimated_storage_upper_bytes": estimate_bytes,
            "limits": {"cumulative_attempts": 240, "partitions": 96,
                       "additional_disk_bytes": 256 * 1024**2, "attempts_per_page": 3},
            "retry": source.config["retry"],
            "restart": "python -m lstm_data.spy_completion --env-file .env --report "
                       "reports/data_audit/ta_mkt_spy_002_2026-10-11",
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


def complete(source: MarketSource, report: Path, env_file: Path | None) -> int:
    if source.config.get("acquisition_policy_version") != 2:
        raise ValueError("TA_MKT_SPY_002_VERSIONED_POLICY_REQUIRED")
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
    budget = AttemptBudget(source.store / "transport_attempts.jsonl", "SPY002", 240)
    transport = ReplayTransport(budget, budget.used)
    client = HistoricalClient(source.config, key, secret, get=transport.get)
    lock = source.store / ".acquire.lock"
    source.store.mkdir(parents=True, exist_ok=True)
    with lock.open("x"):
        pass
    try:
        plan_path = report / "acquisition_plan_v2.json"
        if plan_path.exists():
            plan = parse_json(plan_path.read_bytes())
            if plan["config_id"] != source.identity or plan["status"] != "FEASIBLE":
                raise ValueError("SPY_MATCHING_FEASIBLE_PLAN_REQUIRED")
        else:
            evidence = diagnostic(client, source, transport)
            write_json(report / "pagination_diagnostic.json", evidence)
            plan = acquisition_plan(source, evidence, budget.used)
            write_json(plan_path, plan)
        if plan["status"] != "FEASIBLE":
            raise DataAccessError("SPY_MEASURED_PLAN_EXCEEDS_AUTHORIZED_CEILINGS")
        if [p["params"] for p in plan["partitions"]] != source.partitions():
            raise ValueError("SPY_PLAN_FIXED_REQUEST_IDENTITIES_REQUIRED_NO_FALLBACK")
        transport.diagnostic = False
        for partition in plan["partitions"]:
            if sum(p.stat().st_size for p in source.store.rglob("*") if p.is_file()) \
                    > 256 * 1024**2:
                raise DataAccessError("SPY_DISK_CEILING")
            # Remaining conservative page envelope must still fit after errors/retries.
            remaining = [p for p in plan["partitions"]
                         if not chunk_paths(source.store, p["params"])[1].exists()]
            if budget.used + sum(p["upper_pages"] * 3 for p in remaining) \
                    - len(transport.cache) * 3 > 240:
                raise DataAccessError("SPY_ROLLING_ATTEMPT_BOUND_EXCEEDS_CEILING")
            result = acquire_partition(source, client, partition["params"],
                                       completion_check=transport.completion_audit)
            actual_pages = sum(e["status"] == 200 for e in result["events"])
            if actual_pages > partition["upper_pages"]:
                raise DataAccessError("SPY_OBSERVED_PAGE_COUNT_EXCEEDS_PLAN_RECOMPUTE_REQUIRED")
            transport.cache.clear()
        proof = archive_complete(source)
        proof["transport_attempts"] = budget.used
        proof["diagnostic_pages_replayed_without_GET"] = transport.replayed_pages
        if not (report / "archive_manifest.json").exists():
            write_json(report / "archive_manifest.json", proof)
        print({"status": proof["status"], "attempts": budget.used, "rows": proof["rows"]})
        return 0
    except (DataAccessError, ValueError, FileNotFoundError) as exc:
        failure = report / f"failure_{budget.used}.json"
        if failure.exists():
            suffix = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%S%fZ")
            failure = report / f"failure_{budget.used}_{suffix}.json"
        write_json(failure, {"status": "SOURCE_BLOCKED",
                   "reason": str(exc), "transport_attempts": budget.used,
                   "completed_partitions": len(list(source.store.glob("*.manifest.json")))})
        return 2
    finally:
        lock.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/track_a_market_spy_v2.json"))
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args()
    return complete(MarketSource.load(args.config), args.report, args.env_file)


if __name__ == "__main__":
    raise SystemExit(main())
