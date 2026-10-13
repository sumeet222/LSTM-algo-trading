"""Configuration-bound diagnostic SIP acquisition; no production stock activation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from .alpaca import DataAccessError, HistoricalClient, credentials
from .broad_screen import BroadTransport, read_candidate
from .config import digest, fingerprint, load_config, now, write_json
from .remediation_transport import StorageLimit, publish_chunk
from .store import chunk_paths
from .universe_screen import verify_screen_authority


class CandidateTransport(BroadTransport):
    """Reuse the reviewed durable transport without touching predecessor journals."""

    package: str = "DIAGNOSTIC_CANDIDATE_SOURCE"
    inherited_attempts: int = 26

    def append(self, item: dict) -> None:
        if item["kind"] == "ATTEMPT" and self.used + self.inherited_attempts >= self.ceiling:
            raise DataAccessError("CANDIDATE_CUMULATIVE_ATTEMPT_LIMIT")
        super().append(dict(item, package=self.package, inherited_attempts=self.inherited_attempts))

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
            token = response.json().get("next_page_token")
            if token:
                self.append(
                    {
                        "kind": "CONTINUATION_HASH",
                        "request_hash": fingerprint(
                            {k: v for k, v in params.items() if k != "page_token"}
                        ),
                        "next_token_sha256": hashlib.sha256(str(token).encode()).hexdigest(),
                        "time_utc": now(),
                    }
                )
        return response


def acquire(report: Path, plan_path: Path, *, get=requests.get) -> dict:
    """Validate frozen diagnostic identities, exhaust pages, publish only complete pairs."""
    verify_screen_authority()
    pool_path = report / "frozen_pool.json"
    pool, plan = json.loads(pool_path.read_text()), json.loads(plan_path.read_text())
    if (
        plan["package"] != pool["package"]
        or plan["pool_sha256"] != digest(pool_path)
        or plan["requests_sha256"] != fingerprint(plan["requests"])
    ):
        raise ValueError("CANDIDATE_PREQUERY_PLAN_SHA_REQUIRED")
    for old in pool["inherited_journals"]:
        if digest(Path(old["path"])) != old["sha256"]:
            raise ValueError("CANDIDATE_INHERITED_JOURNAL_CHANGED")
    archive = Path(pool["archive"])
    if not archive.is_relative_to(Path("data/raw/alpaca")) or ".." in archive.parts:
        raise ValueError("DEDICATED_PROJECT_RELATIVE_CANDIDATE_ARCHIVE_REQUIRED")
    symbols = [r["ticker"] for r in pool["candidates"]]
    selected = None
    if plan.get("selected_sha256"):
        chosen_path = report / "selected_fifth.json"
        if digest(chosen_path) != plan["selected_sha256"]:
            raise ValueError("FROZEN_FIFTH_SELECTION_CHANGED")
        chosen = json.loads(chosen_path.read_text())
        if not chosen["historical_eligibility_qualified"] or not chosen["liquidity_pass"]:
            raise ValueError("QUALIFIED_HISTORICAL_FIFTH_REQUIRED")
        selected = chosen["ticker"]
    for row in plan["requests"]:
        p = row["params"]
        start, end = pd.Timestamp(p["start"]), pd.Timestamp(p["end"])
        if (
            set(p["symbols"].split(",")) - set(symbols)
            or p["feed"] != "sip"
            or p["currency"] != "USD"
            or p["sort"] != "asc"
            or p["limit"] != 10000
            or fingerprint(p) != row["request_hash"]
            or not 1 <= row["max_pages"] <= 12
            or row["max_attempts"] != 1
            or start >= end
        ):
            raise ValueError("BOUNDED_EXPLICIT_DIAGNOSTIC_SOURCE_REQUIRED")
        if row["kind"] == "FORMATION_DAILY":
            if (
                p["timeframe"] != "1Day"
                or p["adjustment"] != "raw"
                or p["asof"] != "2020-07-01"
                or start != pd.Timestamp("2020-04-06T04:00Z")
                or end != pd.Timestamp("2020-07-01T03:59:59.999999999Z")
            ):
                raise ValueError("FORMATION60_SOURCE_REQUIRED")
        elif row["kind"] in {"TARGETED_30MIN", "FULL_NATIVE"}:
            if p["timeframe"] != "30Min" or p["adjustment"] != "split" or p["asof"] != "2025-06-30":
                raise ValueError("NATIVE_SPLIT30_SOURCE_REQUIRED")
            if row["kind"] == "TARGETED_30MIN":
                if start.tz_convert("America/New_York").strftime("%Y-%m-%d") not in pool[
                    "training_dates"
                ] or end - start != pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1):
                    raise ValueError("ONLY_FIXED_TRAINING_SCREEN_DATES_REQUIRED")
            elif (
                selected is None
                or p["symbols"] != selected
                or start
                < pd.Timestamp(pool["prehistory_start"], tz="America/New_York").tz_convert("UTC")
                or end >= pd.Timestamp("2025-07-01T04:00Z")
            ):
                raise ValueError("ONLY_SELECTED_FIFTH_FULL_SOURCE_REQUIRED")
        else:
            raise ValueError("UNKNOWN_DIAGNOSTIC_SOURCE_KIND")
    limit = StorageLimit((archive, report))
    journal = archive / "transport_attempts.jsonl"
    transport = CandidateTransport(
        journal,
        tuple(r["params"] for r in plan["requests"]),
        get=get,
        expected_sha=digest(journal) if journal.exists() else None,
        before_append=limit.reserve,
    )
    transport.package = pool["package"]
    transport.inherited_attempts = pool["inherited_attempts_charged"]
    cached = {
        r["request_hash"]: read_candidate(archive / r["kind"].lower(), r["params"])
        for r in plan["requests"]
    }
    envelope = sum(
        r["max_pages"] * r["max_attempts"]
        for r in plan["requests"]
        if cached[r["request_hash"]] is None
    )
    if transport.used + transport.inherited_attempts + envelope > 1000:
        raise DataAccessError("CONSERVATIVE_ATTEMPT_ENVELOPE_EXCEEDED")
    cfg = load_config(Path("configs/track_a_data.json"))
    key = secret = ""
    chunks = []
    for index, row in enumerate(plan["requests"], 1):
        p = row["params"]
        store = archive / row["kind"].lower()
        saved = cached[row["request_hash"]]
        if saved is None:
            if not key:
                load_dotenv(Path(".env"), override=False)
                key, secret = credentials()
            client = HistoricalClient(
                dict(
                    cfg,
                    max_pages_per_request=row["max_pages"],
                    retry=dict(
                        cfg["retry"], max_attempts=row["max_attempts"], requests_per_minute=100
                    ),
                ),
                key,
                secret,
                get=transport.request,
            )
            begin = len(transport.records())
            try:
                frame = client.bars(p)
            except (DataAccessError, ValueError):
                transport.append(
                    {
                        "kind": "HOLD",
                        "reason": "CLIENT_OR_PAGINATION_HOLD",
                        "request_hash": row["request_hash"],
                        "time_utc": now(),
                    }
                )
                raise DataAccessError("CANDIDATE_SOURCE_HOLD") from None
            meta = publish_chunk(
                store, frame, p, transport.records()[begin:], kind=row["kind"], limit=limit
            )
            resumed = False
        else:
            frame, meta = saved
            resumed = True
        data, manifest = chunk_paths(store, p)
        chunks.append(
            {
                "data": str(data),
                "manifest": str(manifest),
                "params": p,
                "sha256": digest(data),
                "manifest_sha256": digest(manifest),
                "kind": row["kind"],
                "rows": len(frame),
                "bytes": data.stat().st_size,
                "pages": sum(r.get("status") == 200 for r in meta["receipts"]),
                "terminal_page_verified": meta["terminal_page_verified"],
                "resumed_zero_GET": resumed,
            }
        )
        if index % 3 == 0 or index == len(plan["requests"]):
            print(
                {
                    "completed_chunks": index,
                    "planned": len(plan["requests"]),
                    "new_attempts": transport.used,
                    "bytes_used": limit.used,
                }
            )
    return {
        "package": pool["package"],
        "plan_sha256": digest(plan_path),
        "chunks": chunks,
        "new_attempts": transport.used,
        "inherited_charged": transport.inherited_attempts,
        "cumulative_charged": transport.used + transport.inherited_attempts,
        "journal": str(journal),
        "journal_sha256": digest(journal),
        "scientific": "HOLD",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("IMMUTABLE_SOURCE_OUTPUT_EXISTS")
    write_json(args.output, acquire(args.report, args.plan))


if __name__ == "__main__":
    main()
