"""Explicitly authorized source completion, preserving every inherited HOLD."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from .alpaca import DataAccessError, HistoricalClient, credentials
from .broad_screen import read_candidate
from .candidate_acquisition import CandidateTransport
from .config import digest, fingerprint, load_config, now, write_json
from .remediation_transport import StorageLimit, publish_chunk
from .store import chunk_paths
from .universe_screen import verify_screen_authority


def validated_plan(report: Path) -> dict:
    """Require the exact user-authorized replacement and unchanged predecessor journals."""
    path = report / "completion_request_proposal.json"
    plan = json.loads(path.read_text())
    approval = json.loads((report / "legacy_hold_authorization.json").read_text())
    inherited = json.loads((report / "inherited_limits_and_hold.json").read_text())
    if (
        approval["plan_sha256"] != digest(path)
        or approval["approved"] is not True
        or approval["replacement_request_hash"] != plan["requests"][0]["request_hash"]
        or plan["requests_sha256"] != fingerprint(plan["requests"])
        or plan["inherited_limits_sha256"] != digest(report / "inherited_limits_and_hold.json")
        or plan["reuse_inventory_sha256"] != digest(report / "reused_source_inventory.json")
        or sum(r["attempts"] for r in inherited["journals"]) != plan["carried_attempts"]
    ):
        raise ValueError("EXACT_COMPLETION_AUTHORITY_REQUIRED")
    for old in inherited["journals"]:
        if digest(Path(old["path"])) != old["sha256"]:
            raise ValueError("INHERITED_JOURNAL_CHANGED")
    archive = Path(plan["archive"])
    if not archive.is_relative_to("data/raw/alpaca") or ".." in archive.parts:
        raise ValueError("DEDICATED_COMPLETION_ARCHIVE_REQUIRED")
    symbols = plan["requests"][0]["params"]["symbols"]
    if set(symbols.split(",")) - set(plan["ordered_universe"]):
        raise ValueError("ONLY_PROFILE_SOURCE_SYMBOLS_REQUIRED")
    for row in plan["requests"]:
        p = row["params"]
        start, end = pd.Timestamp(p["start"]), pd.Timestamp(p["end"])
        if (
            p["symbols"] != symbols
            or p["feed"] != "sip"
            or p["timeframe"] != "30Min"
            or p["currency"] != "USD"
            or p["adjustment"] != "split"
            or p["asof"] != "2025-06-30"
            or p["sort"] != "asc"
            or p["limit"] != 10000
            or row["request_hash"] != fingerprint(p)
            or row["max_attempts"] != 1
            or not 1 <= row["max_pages"] <= 12
            or start < pd.Timestamp("2020-03-01T05:00Z")
            or end >= pd.Timestamp("2025-07-01T04:00Z")
            or start >= end
        ):
            raise ValueError("BOUNDED_NATIVE_COMPLETION_IDENTITY_REQUIRED")
    return plan


def acquire(report: Path, *, get=requests.get) -> dict:
    """Use existing transport/parser/store; cache resume never loads credentials or sends."""
    verify_screen_authority()
    plan = validated_plan(report)
    archive = Path(plan["archive"])
    store, journal = archive / "full_native", archive / "transport_attempts.jsonl"
    limit = StorageLimit((archive, report))
    transport = CandidateTransport(
        journal,
        tuple(r["params"] for r in plan["requests"]),
        get=get,
        expected_sha=digest(journal) if journal.exists() else None,
        before_append=limit.reserve,
    )
    transport.package, transport.inherited_attempts = plan["package"], plan["carried_attempts"]
    cached = {r["request_hash"]: read_candidate(store, r["params"]) for r in plan["requests"]}
    envelope = sum(r["max_pages"] for r in plan["requests"] if cached[r["request_hash"]] is None)
    if envelope + transport.used + transport.inherited_attempts > 1000:
        raise DataAccessError("COMPLETION_CONSERVATIVE_ENVELOPE_EXCEEDED")
    cfg = load_config(Path("configs/track_a_data.json"))
    key = secret = ""
    refs = []
    for index, row in enumerate(plan["requests"], 1):
        p = row["params"]
        saved = cached[row["request_hash"]]
        if saved is None:
            if not key:
                load_dotenv(Path(".env"), override=False)
                key, secret = credentials()
            client = HistoricalClient(
                dict(
                    cfg,
                    max_pages_per_request=row["max_pages"],
                    retry=dict(cfg["retry"], max_attempts=1, requests_per_minute=100),
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
                    dict(
                        kind="HOLD",
                        reason="COMPLETION_CLIENT_OR_PAGINATION",
                        request_hash=row["request_hash"],
                        time_utc=now(),
                    )
                )
                raise DataAccessError("COMPLETION_SOURCE_HOLD") from None
            meta = publish_chunk(
                store, frame, p, transport.records()[begin:], kind="FULL_NATIVE", limit=limit
            )
        else:
            frame, meta = saved
        data, manifest = chunk_paths(store, p)
        refs.append(
            dict(
                data=str(data),
                manifest=str(manifest),
                params=p,
                sha256=digest(data),
                manifest_sha256=digest(manifest),
                rows=len(frame),
                bytes=data.stat().st_size,
                pages=sum(r.get("status") == 200 for r in meta["receipts"]),
                terminal_page_verified=meta["terminal_page_verified"],
                resumed_zero_GET=saved is not None,
            )
        )
        if index % 3 == 0 or index == len(plan["requests"]):
            print(
                dict(
                    completed=index,
                    planned=len(plan["requests"]),
                    new_attempts=transport.used,
                    cumulative=transport.used + transport.inherited_attempts,
                    bytes=limit.used,
                ),
                flush=True,
            )
    return dict(
        package=plan["package"],
        chunks=refs,
        new_attempts=transport.used,
        carried_attempts=transport.inherited_attempts,
        cumulative_attempts=transport.used + transport.inherited_attempts,
        journal=str(journal),
        journal_sha256=digest(journal),
        scientific="HOLD",
        plan_sha256=digest(report / "completion_request_proposal.json"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("IMMUTABLE_COMPLETION_OUTPUT_EXISTS")
    write_json(args.output, acquire(args.report))


if __name__ == "__main__":
    main()
