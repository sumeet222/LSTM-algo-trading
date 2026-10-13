"""Isolated historical rank-led source diagnostics; never activates a universe."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from .alpaca import DataAccessError, HistoricalClient, credentials
from .broad_screen import BroadTransport, audit_day, read_candidate
from .config import digest, fingerprint, load_config, now, write_json
from .remediation_transport import StorageLimit, publish_chunk
from .store import chunk_paths
from .universe_screen import verify_screen_authority

PACKAGE = "TA-SP500-GREEDY-UNIVERSE-001"
ARCHIVE = Path("data/raw/alpaca/track_a_sp500_greedy_candidate_v1")


def historical_order(path: Path, expected_sha: str) -> tuple[dict, ...]:
    """Validate the approved fact list; never substitute current ranks/membership."""
    if digest(path) != expected_sha:
        raise ValueError("HISTORICAL_RANK_SHA_CHANGED")
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    ordered = sorted(rows, key=lambda r: (-int(r["holding_value_USD"]), r["name"]))
    if len(rows) != 505 or sum(int(r["holding_value_USD"]) for r in rows) != 235256200309:
        raise ValueError("HISTORICAL505_FACT_CONSERVATION_REQUIRED")
    kept = tuple(r for r in ordered if r["proposed_unique_issuer_rank"])
    if len(kept) != 500 or [int(r["proposed_unique_issuer_rank"]) for r in kept] != list(
        range(1, 501)
    ):
        raise ValueError("FROZEN_CLASS_OR_TIE_ORDER_CHANGED")
    return kept


@dataclass(frozen=True)
class Candidate:
    rank: int
    name: str
    ticker: str
    sector: str
    formation_qualified: bool


@dataclass
class GreedyScan:
    """Ordered decisions only; no outcomes, fills or current-sector fallback."""

    selected: list[str] = field(default_factory=lambda: ["AAPL"])
    sectors: set[str] = field(default_factory=lambda: {"Technology"})
    pending: dict[str, str] = field(default_factory=dict)
    trace: list[dict] = field(default_factory=list)
    last_rank: int = 0
    stopped: bool = False

    def visit(self, candidate: Candidate, status: str, *, mandatory_measured: bool = False) -> str:
        if self.stopped or len(self.selected) == 5:
            raise ValueError("SCAN_ALREADY_STOPPED")
        if candidate.rank <= self.last_rank:
            raise ValueError("FIXED_INCREASING_RANK_REQUIRED")
        self.last_rank = candidate.rank
        if not candidate.formation_qualified:
            decision = "FORMATION_OR_MAPPING_HOLD"
            self.stopped = True
        elif candidate.sector in self.sectors:
            decision = "SKIP_REPRESENTED_SECTOR"
        elif status in {"MAJOR_GAP_FAIL", "COVERAGE_FAIL", "FORMATION_FAIL"}:
            decision = status
        elif status == "MINOR_GAP_CANDIDATE_ONLY":
            self.pending.setdefault(candidate.sector, candidate.ticker)
            decision = status
        elif status == "NATIVE_CLEAN" and mandatory_measured:
            if candidate.sector in self.pending:
                decision = "EARLIER_MINOR_VS_LATER_CLEAN_HUMAN_DECISION"
                self.stopped = True
            else:
                decision = "PROVISIONAL_ACCEPT"
                self.selected.append(candidate.ticker)
                self.sectors.add(candidate.sector)
        elif status in {
            "NATIVE_CLEAN",
            "NOT_MEASURED",
            "ACTION_OR_MAPPING_HOLD",
            "RESOURCE_BLOCKED",
        }:
            decision = "MANDATORY_EVIDENCE_HOLD"
            self.stopped = True
        else:
            raise ValueError("UNKNOWN_SOURCE_DISPOSITION")
        self.trace.append(
            {
                "rank": candidate.rank,
                "ticker": candidate.ticker,
                "sector": candidate.sector,
                "source_status": status,
                "decision": decision,
                "scientific_activation": False,
            }
        )
        return decision


def gap_status(days: list[dict]) -> str:
    """A positive pilot stays a pilot; terminal absences are explicit T2 blockers."""
    if not days:
        raise ValueError("MEASURED_SESSION_KEYS_REQUIRED")
    if any(d["longest_gap_half_hours"] >= 3 for d in days):
        return "MAJOR_GAP_FAIL"
    if any(d["missing"] for d in days):
        return "MINOR_GAP_CANDIDATE_ONLY"
    return "MEASURED_INTERVAL_NATIVE_COMPLETE"


class GreedyTransport(BroadTransport):
    """Reuse reviewed pacing/lifetime limits with a separate journal and identity."""

    def append(self, item: dict) -> None:
        super().append(dict(item, package=PACKAGE))

    def request(
        self,
        url: str,
        *,
        params: dict,
        headers: dict,
        timeout: float,
        allow_redirects: bool = False,
    ) -> requests.Response:
        response = super().request(
            url, params=params, headers=headers, timeout=timeout, allow_redirects=allow_redirects
        )
        if response.status_code == 200:
            payload = response.json()
            count = sum(len(bars) for bars in payload["bars"].values())
            if payload.get("next_page_token") and count < params["limit"]:
                self.append(
                    {"kind": "HOLD", "reason": "SUSPICIOUS_SHORT_CONTINUED_PAGE", "time_utc": now()}
                )
                raise DataAccessError("GREEDY_SHORT_CONTINUED_PAGE_HOLD")
        return response


def acquire_plan(
    report: Path, plan_path: Path, *, env_file: Path = Path(".env"), get=requests.get
) -> dict:
    """Only execute approved, hash-bound, formation-authenticated diagnostic plans."""
    verify_screen_authority()
    rule = json.loads((report / "frozen_selection_rule_v2.json").read_text())
    rank_path = Path(rule["approved_rank_path"])
    if (
        rule["package"] != PACKAGE
        or rule["approval"] != "Approve historical SPY proxy (recommended)"
        or digest(rank_path) != rule["approved_candidate_rank_list_sha256"]
    ):
        raise ValueError("APPROVED_IMMUTABLE_HISTORICAL_RANK_REQUIRED")
    historical_order(rank_path, rule["approved_candidate_rank_list_sha256"])
    plan = json.loads(plan_path.read_text())
    formation_path = Path(plan["formation_path"])
    if (
        plan["package"] != PACKAGE
        or digest(formation_path) != plan["formation_sha256"]
        or fingerprint(plan["requests"]) != plan["requests_sha256"]
        or digest(report / "frozen_selection_rule_v2.json") != plan["rule_sha256"]
    ):
        raise ValueError("PREQUERY_SCOPE_OR_FORMATION_CHANGED")
    formation = json.loads(formation_path.read_text())
    for row in plan["requests"]:
        p = row["params"]
        start, end = pd.Timestamp(p["start"]), pd.Timestamp(p["end"])
        if (
            p["symbols"] != formation["ticker"]
            or formation["diagnostic_identity_qualified"] is not True
            or p["feed"] != "sip"
            or p["currency"] != "USD"
            or p["sort"] != "asc"
            or p["limit"] != 10000
            or start >= end
            or not 1 <= row["max_pages"] <= 4
            or row["kind"] not in {"FORMATION_DAILY", "TARGETED_30MIN", "TRAINING_NATIVE"}
            or fingerprint(p) != row["hash"]
        ):
            raise ValueError("QUALIFIED_SINGLE_CANDIDATE_SCOPE_REQUIRED")
        if row["kind"] == "FORMATION_DAILY":
            if (
                p["timeframe"] != "1Day"
                or p["adjustment"] != "raw"
                or p["asof"] != "2020-07-01"
                or start != pd.Timestamp("2020-04-06T04:00Z")
                or end != pd.Timestamp("2020-07-01T03:59:59.999999999Z")
            ):
                raise ValueError("EXACT_FORMATION_60_SESSION_SOURCE_REQUIRED")
        elif (
            p["timeframe"] != "30Min"
            or p["adjustment"] != "split"
            or p["asof"] != "2025-06-30"
            or start < pd.Timestamp("2019-12-18T05:00Z")
            or end >= pd.Timestamp("2023-07-01T04:00Z")
        ):
            raise ValueError("TRAINING_SOURCE_ONLY_NO_CONFIRMATION_REQUIRED")
    if sum(r["max_pages"] * 3 for r in plan["requests"]) > 1000:
        raise ValueError("CONSERVATIVE_REQUEST_ENVELOPE_EXCEEDED")
    limit = StorageLimit((ARCHIVE, report))
    journal = ARCHIVE / "transport_attempts.jsonl"
    transport = GreedyTransport(
        journal,
        tuple(r["params"] for r in plan["requests"]),
        get=get,
        expected_sha=digest(journal) if journal.exists() else None,
        before_append=limit.reserve,
    )
    cfg = load_config(Path("configs/track_a_data.json"))
    chunks = []
    key = secret = ""
    for row in plan["requests"]:
        params = row["params"]
        store = ARCHIVE / row["kind"].lower()
        saved = read_candidate(store, params)
        if saved is None:
            if not key:
                load_dotenv(env_file, override=False)
                key, secret = credentials()
            client = HistoricalClient(
                dict(
                    cfg,
                    max_pages_per_request=row["max_pages"],
                    retry=dict(cfg["retry"], max_attempts=3, requests_per_minute=100),
                ),
                key,
                secret,
                get=transport.request,
            )
            begin = len(transport.records())
            try:
                frame = client.bars(params)
            except (DataAccessError, ValueError):
                transport.append(
                    {
                        "kind": "HOLD",
                        "reason": "CLIENT_OR_PAGINATION_HOLD",
                        "request_hash": row["hash"],
                        "time_utc": now(),
                    }
                )
                raise DataAccessError("GREEDY_SOURCE_HOLD") from None
            meta = publish_chunk(
                store, frame, params, transport.records()[begin:], kind=row["kind"], limit=limit
            )
            resumed = False
        else:
            frame, meta = saved
            resumed = True
        data, manifest = chunk_paths(store, params)
        chunks.append(
            {
                "kind": row["kind"],
                "data": str(data),
                "manifest": str(manifest),
                "sha256": digest(data),
                "manifest_sha256": digest(manifest),
                "params": params,
                "rows": len(frame),
                "resumed_zero_GET": resumed,
                "terminal_page_verified": meta["terminal_page_verified"],
            }
        )
    result = {
        "package": PACKAGE,
        "plan": str(plan_path),
        "plan_sha256": digest(plan_path),
        "chunks": chunks,
        "attempts_used": transport.used,
        "journal_sha256": digest(journal),
        "scientific_activation": False,
    }
    return result


def audit_interval(frame: pd.DataFrame, ticker: str, start: str, stop: str) -> list[dict]:
    """Exact per-session grids through training only; caller bounds actual source."""
    from .calendar import schedule

    if stop > "2023-06-30":
        raise ValueError("CONFIRMATION_OR_DEVELOPMENT_SELECTION_FORBIDDEN")
    return [
        audit_day(frame, ticker, day.strftime("%Y-%m-%d")) for day in schedule(start, stop).index
    ]


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("IMMUTABLE_DIAGNOSTIC_OUTPUT_EXISTS")
    write_json(args.output, acquire_plan(args.report, args.plan))


if __name__ == "__main__":
    main()
