"""Package018 bounded public metadata gate; never transfers or decodes market-data files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import resource
import shutil
import sys
import time
from pathlib import Path

import pandas as pd
import requests

from .config import atomic_new, digest, now, write_json
from .hf20_source import SYMBOLS
from .hf_hourly_source import PublicHTTP

DATASET = "mito0o852/OHLCV-1m"
API = "https://huggingface.co/api/datasets/" + DATASET
TERMS = "https://finnhub.io/terms-of-service"
MONTH = re.compile(r"data/ohlcv_(\d{4}-(?:0[1-9]|1[0-2]))\.parquet")
METADATA_LIMIT = 4_000_000
POLICY_LIMIT = 250_000


def validate_months(revision: str, listing: list[dict]) -> list[dict]:
    """Keep exact monthly paths and distinguish content SHA256 from Git/Xet identities."""
    if not re.fullmatch(r"[a-f0-9]{40}", revision):
        raise ValueError("P018_IMMUTABLE_REVISION_REQUIRED")
    result = []
    for row in listing:
        match = MONTH.fullmatch(row["path"])
        if match is None:
            continue
        if row.get("type") != "file" or type(row.get("size")) is not int or row["size"] < 8:
            raise ValueError("P018_INVALID_MONTHLY_FILE_METADATA")
        lfs = row.get("lfs") or {}
        sha = lfs.get("oid")
        if sha is not None and (
            not re.fullmatch(r"[a-f0-9]{64}", sha) or lfs.get("size") != row["size"]
        ):
            raise ValueError("P018_LFS_SIZE_OR_SHA_INVALID")
        result.append(
            dict(
                month=match[1],
                path=row["path"],
                bytes=row["size"],
                lfs_sha256=sha,
                git_blob_oid=row.get("oid"),
                xet_hash=row.get("xetHash"),
                transfer_status="NOT_REQUESTED_RIGHTS_GATE",
                downloaded_bytes=0,
                persisted_raw_rows=None,
            )
        )
    if not result or len({r["month"] for r in result}) != len(result):
        raise ValueError("P018_UNIQUE_NONEMPTY_MONTHLY_LIST_REQUIRED")
    return sorted(result, key=lambda r: r["month"])


def required_start(end: str) -> str:
    """Conservative calendar boundary, using real year/month arithmetic rather than days."""
    return str((pd.Timestamp(end) - pd.DateOffset(years=14, months=9)).date())


def calendar_duration_pass(start: str, end: str) -> bool:
    """Compare actual endpoints; an inclusive month-file count is not a duration proof."""
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    if a > b:
        raise ValueError("P018_REVERSED_WINDOW")
    return bool(a + pd.DateOffset(years=14, months=9) <= b)


def rights_gate(info: dict, files: list[dict], card: str, terms: str) -> dict:
    """Do not infer third-party permissions from public visibility or a publisher license."""
    source_matches = "finnhub" in card.lower()
    license_paths = [r["path"] for r in files if Path(r["path"]).name.lower().startswith("license")]
    restriction_observed = "redistribut" in terms.lower() and "written approval" in terms.lower()
    return dict(
        decision="STOP_RIGHTS" if source_matches else "STOP_UNVERIFIED",
        reason=(
            "No attributable permission for this Finnhub source and local research use."
            if source_matches
            else "Declared source could not be reconciled."
        ),
        card_license=(info.get("cardData") or {}).get("license"),
        license_files=license_paths,
        public_access=not info.get("private") and not info.get("gated"),
        provider_restriction_observed=restriction_observed,
        provider_terms_url=TERMS,
        local_research_permission="UNSUBSTANTIATED",
        redistribution_permission="UNSUBSTANTIATED",
        prior_Twelve_Data_attestation_applies=False,
        legal_finding="NONE; this is the researcher's required operational evidence gate.",
    )


def policy_snapshot() -> tuple[dict, str]:
    """Bounded direct public terms check; no cookies, credentials, proxy env or retries."""
    tick = time.monotonic()
    session = requests.Session()
    session.trust_env = False
    receipt = dict(url=TERMS, requested_at=now(), bytes=0, maximum_bytes=POLICY_LIMIT)
    received = 0
    try:
        with session.get(
            TERMS, headers={"Accept-Encoding": "identity"}, stream=True, timeout=(15, 45)
        ) as response:
            response.raise_for_status()
            receipt.update(status=response.status_code, redirects=len(response.history))
            if response.headers.get("Content-Encoding", "identity") != "identity":
                raise ValueError("P018_IDENTITY_ENCODING_REQUIRED")
            if int(response.headers.get("Content-Length", "0")) > POLICY_LIMIT:
                raise ValueError("P018_POLICY_TOO_LARGE_NO_BODY_READ")
            chunks = []
            while received < POLICY_LIMIT:
                block = response.raw.read(min(65536, POLICY_LIMIT - received))
                if not block:
                    break
                chunks.append(block)
                received += len(block)
            receipt["bytes"] = received
            if received == POLICY_LIMIT:
                raise ValueError("P018_POLICY_COMPLETE_RESPONSE_UNVERIFIED")
            body = b"".join(chunks)
            return {
                **receipt,
                "sha256": hashlib.sha256(body).hexdigest(),
                "seconds": time.monotonic() - tick,
            }, body.decode("utf-8")
    finally:
        session.close()


def capture(out: Path, revision: str | None) -> dict:
    """Only info/tree/README and terms; no resolve endpoint, footer, row group or data stream."""
    http = PublicHTTP(METADATA_LIMIT)
    try:
        info_body = http.get(API + ("/revision/" + revision if revision else ""), 1_000_000)
        info = json.loads(info_body)
        rev = info["sha"]
        if not re.fullmatch(r"[a-f0-9]{40}", rev) or (revision and rev != revision):
            raise ValueError("P018_IMMUTABLE_REVISION_MISMATCH")
        atomic_new(out / "dataset_info.json", info_body)
        pinned_body = http.get(API + "/revision/" + rev, 1_000_000)
        if json.loads(pinned_body)["sha"] != rev:
            raise ValueError("P018_PIN_CHANGED")
        atomic_new(out / "pinned_dataset_info.json", pinned_body)
        tree_body = http.get(API + f"/tree/{rev}?recursive=true&limit=1000", 1_000_000)
        listing = json.loads(tree_body)
        atomic_new(out / "pinned_tree.json", tree_body)
        actual = {r["path"] for r in listing if r["type"] == "file"}
        if actual != {r["rfilename"] for r in info["siblings"]}:
            raise ValueError("P018_PAGINATION_OR_FILE_LIST_MISMATCH")
        card_body = http.get(
            f"https://huggingface.co/datasets/{DATASET}/raw/{rev}/README.md", 250_000
        )
        atomic_new(out / "dataset_card_snapshot.md", card_body)
        policy, terms = policy_snapshot()
        # Retain a short rights excerpt and full-response hash, not a copied terms document.
        write_json(
            out / "provider_terms_receipt.json",
            dict(
                **policy,
                restriction_observed="redistribut" in terms.lower()
                and "written approval" in terms.lower(),
                excerpt="not redistribute or share access to data or derived results",
                interpretation=(
                    "Sharing requires Finnhub written approval; public third-party "
                    "access does not establish a grant."
                ),
            ),
        )
        return dict(
            info=info,
            listing=listing,
            revision=rev,
            rights=rights_gate(info, listing, card_body.decode(), terms),
        )
    finally:
        write_json(
            out / "http_events.json",
            dict(
                events=http.events,
                bytes_received=http.bytes_received,
                body_bytes_only=True,
                credentials_used=False,
                automatic_retries=0,
            ),
        )


def publish(out: Path, meta: dict) -> None:
    if meta["rights"]["decision"] not in ("STOP_RIGHTS", "STOP_UNVERIFIED"):
        raise ValueError("P018_METADATA_CANNOT_PASS_DATA_GATE")
    months = validate_months(meta["revision"], meta["listing"])
    latest = months[-1]["month"]
    last_day = str(pd.Period(latest, freq="M").end_time.date())
    earliest_boundary = required_start(last_day)
    candidate = [r for r in months if r["month"] >= earliest_boundary[:7]]
    listed = {r["month"] for r in months}
    expected = {str(m) for m in pd.period_range(months[0]["month"], latest, freq="M")}
    resources = dict(
        disk_free_bytes=shutil.disk_usage(".").free,
        monthly_files=len(months),
        all_monthly_upstream_bytes=sum(r["bytes"] for r in months),
        theoretical_boundary_month=earliest_boundary[:7],
        theoretical_candidate_files=len(candidate),
        theoretical_candidate_upstream_bytes=sum(r["bytes"] for r in candidate),
        largest_month_bytes=max(r["bytes"] for r in months),
        persistent_selected_stock_bytes="NOT_MEASURED_NO_ROW_SAMPLE",
        working_set="UNVERIFIED; row-group processing required, no whole-market pandas load",
        bandwidth="NOT_BENCHMARKED_ON_DATA; metadata latency is not bulk throughput",
        candidate_transfer_hours_at_10_Mbps=sum(r["bytes"] for r in candidate) * 8 / 10e6 / 3600,
        candidate_transfer_hours_at_50_Mbps=sum(r["bytes"] for r in candidate) * 8 / 50e6 / 3600,
        transfer_scenario_scope="Hypothetical sustained rates; not measurements or permission",
        no_full_repo_clone_or_data_load=True,
    )
    http = json.loads((out / "http_events.json").read_text())
    policy = json.loads((out / "provider_terms_receipt.json").read_text())
    manifest = dict(
        namespace="HF20_1M_HIST_v1:METADATA_ONLY_NOT_RELEASED",
        dataset=DATASET,
        dataset_url="https://huggingface.co/datasets/" + DATASET,
        revision=meta["revision"],
        snapshot_at=http["events"][0]["started_at"],
        report_generated_at=now(),
        symbols=list(SYMBOLS),
        files=months,
        nonmonthly_files=[
            r for r in meta["listing"] if r["type"] == "file" and not MONTH.fullmatch(r["path"])
        ],
        rights=meta["rights"],
        claimed_schema=(meta["info"].get("cardData") or {}).get("dataset_info", {}).get("features"),
        schema_status="CARD_ONLY_NOT_PARQUET_VERIFIED",
        source_declared_by_publisher="Finnhub",
        raw_source_lineage="UNVERIFIED",
        adjustments="UNVERIFIED",
        publication="UNVERIFIED",
        first_listed_month=months[0]["month"],
        latest_listed_month=latest,
        latest_genuinely_complete_month=None,
        missing_filename_months=sorted(expected - listed),
        common_genuine_start=None,
        common_genuine_end=None,
        calendar_duration_verified=False,
        resources=resources,
        downloaded_data_bytes=0,
        persisted_minute_rows=0,
        native_metadata_and_policy_body_bytes=http["bytes_received"] + policy["bytes"],
        web_research_bytes="UNMETERED_SEPARATE",
        all_later_stages="NOT_REACHED_" + meta["rights"]["decision"],
        model_pairs=32,
        new_model_starts=0,
        protected_numeric_rows=0,
    )
    metadata_names = (
        "dataset_info.json",
        "pinned_dataset_info.json",
        "pinned_tree.json",
        "dataset_card_snapshot.md",
        "provider_terms_receipt.json",
        "http_events.json",
    )
    manifest["snapshot_refs"] = [
        dict(path=name, sha256=digest(out / name)) for name in metadata_names
    ]
    write_json(out / "source_manifest.json", manifest)
    pd.DataFrame(months).to_csv(out / "monthly_file_manifest.csv", index=False)
    pd.DataFrame(
        [
            dict(
                symbol=s,
                symbol_index=i,
                first_genuine_minute_UTC=None,
                last_genuine_minute_UTC=None,
                sampled_months=0,
                genuine_coverage=None,
                status="UNVERIFIED_STOP_RIGHTS",
            )
            for i, s in enumerate(SYMBOLS)
        ]
    ).to_csv(out / "coverage_preflight.csv", index=False)
    planned = sorted(
        {
            earliest_boundary[:7],
            "2011-07",
            "2012-03",
            "2015-11",
            "2016-11",
            "2020-03",
            "2022-03",
            "2025-11",
            latest,
        }
    )
    pd.DataFrame(
        [
            dict(
                symbol=s,
                symbol_index=i,
                month=m,
                listed=m in listed,
                sampling_status="NOT_SAMPLED_STOP_RIGHTS",
                observed_rows=None,
                first_genuine_minute_UTC=None,
                last_genuine_minute_UTC=None,
                RTH_genuine_coverage=None,
                invalid_rows=None,
                maximum_gap_minutes=None,
            )
            for i, s in enumerate(SYMBOLS)
            for m in planned
        ]
    ).to_csv(out / "stock_by_sampled_month.csv", index=False)
    write_json(
        out / "gate_record.json",
        dict(
            decision=meta["rights"]["decision"],
            failed_gate="LOCAL_RESEARCH_RIGHTS_SUBSTANTIATION",
            reason=meta["rights"]["reason"],
            market_data_transfer_authorized=False,
            row_sampling="NOT_REACHED",
            coverage="STOP_UNVERIFIED_SECONDARY_NOT_A_SHORT_WINDOW_FINDING",
            raw_QA="NOT_REACHED",
            filling="NOT_REACHED",
            hourly="NOT_REACHED",
            training="FORBIDDEN",
            new_source_activation=False,
            ledger=32,
        ),
    )
    from .hf_minute_preflight_report import write_reports

    write_reports(out, manifest, earliest_boundary)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--revision")
    parser.add_argument(
        "--snapshot", type=Path, help="Offline replay of captured metadata, no network"
    )
    args = parser.parse_args()
    tick = time.monotonic()
    args.out.mkdir(parents=True, exist_ok=False)
    if args.snapshot:
        manifest = json.loads((args.snapshot / "source_manifest.json").read_text())
        for ref in manifest["snapshot_refs"]:
            path = (args.snapshot / ref["path"]).resolve()
            if not path.is_relative_to(args.snapshot.resolve()) or digest(path) != ref["sha256"]:
                raise ValueError("P018_SNAPSHOT_HASH_OR_PATH_CHANGED")
        if args.revision and args.revision != manifest["revision"]:
            raise ValueError("P018_OFFLINE_REVISION_CHANGED")
        for name in (
            "dataset_info.json",
            "pinned_dataset_info.json",
            "pinned_tree.json",
            "dataset_card_snapshot.md",
            "provider_terms_receipt.json",
            "http_events.json",
        ):
            atomic_new(args.out / name, (args.snapshot / name).read_bytes())
        meta = dict(
            info=json.loads((args.out / "dataset_info.json").read_text()),
            listing=json.loads((args.out / "pinned_tree.json").read_text()),
            revision=manifest["revision"],
            rights=manifest["rights"],
        )
        expected = rights_gate(
            meta["info"], meta["listing"], (args.out / "dataset_card_snapshot.md").read_text(), ""
        )
        expected["provider_restriction_observed"] = json.loads(
            (args.out / "provider_terms_receipt.json").read_text()
        )["restriction_observed"]
        if expected != meta["rights"]:
            raise ValueError("P018_OFFLINE_RIGHTS_GATE_CHANGED")
    else:
        meta = capture(args.out, args.revision)
    publish(args.out, meta)
    write_json(
        args.out / "preflight_runtime.json",
        dict(
            seconds=time.monotonic() - tick,
            mode="OFFLINE" if args.snapshot else "PUBLIC_METADATA_ONLY",
            network_requests_this_invocation=0 if args.snapshot else 5,
            peak_RSS_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            * (1 if sys.platform == "darwin" else 1024),
            market_data_bytes=0,
        ),
    )
    print(
        json.dumps(
            dict(
                decision=meta["rights"]["decision"],
                out=str(args.out),
                minute_data_bytes=0,
                model_starts=0,
            )
        )
    )


if __name__ == "__main__":
    main()
