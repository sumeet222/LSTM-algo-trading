"""Package 018D resumable all-month acquisition and source-only hourly derivation."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests

from .config import digest, now, write_json
from .hf_minute_boundary_io import DATASET, REVISION
from .hf_minute_long_io import (
    DERIVED,
    MARCH,
    NAMESPACE,
    Guard,
    acquire_month,
    replace_json,
    verify_remote,
)
from .hf_minute_long_qa import MonthQA, process_month


def verify_identity(out: Path) -> None:
    """Require the human-scoped first-action receipt and unchanged model budget before work."""
    identity = json.loads((out / "identity_initial.json").read_text())
    if (
        identity["dataset"] != DATASET
        or identity["revision"] != REVISION
        or identity["namespace"] != NAMESPACE
        or identity["ledger"] != 32
        or identity["permission"] != "HUMAN_REPORTED_MAINTAINER_PERMISSION_FOR_PRIVATE_RESEARCH"
    ):
        raise ValueError("STOP_IDENTITY: task identity/permission mismatch")
    pointer = json.loads(Path("configs/CURRENT_EXPERIMENT_REGISTRY.json").read_text())
    journal = [json.loads(r) for r in Path(pointer["real_journal"]).read_text().splitlines()]
    if journal[-1]["global_started_pairs"] != 32:
        raise ValueError("STOP_IDENTITY: model ledger changed externally")


def publish_qa(qa: MonthQA, month: str, folder: Path, guard: Guard) -> dict:
    """Publish canonical observations and proxy delta as separate physical layers."""
    tables = dict(
        canonical_observed=qa.canonical,
        fill_proxies_cap5=qa.proxies,
        raw_record_classification=qa.classification,
        minute_quality_issues=qa.minute_issues,
        hourly_ohlcv=qa.hourly,
        hourly_quality_issues=qa.hourly_issues,
        ticker_session_coverage=qa.sessions,
        fill_sensitivity=qa.sensitivity,
    )
    receipts = {}
    for name, frame in tables.items():
        receipts[name] = guard.parquet(
            DERIVED / "qa_v2" / name / f"{month}.parquet",
            pa.Table.from_pandas(frame, preserve_index=False),
        )
    qa.coverage.to_csv(folder / "ticker_month_coverage.csv", index=False)
    result = dict(
        month=month,
        files=receipts,
        last_observed=qa.last_observed,
        hourly_rows=len(qa.hourly),
        canonical_rows=len(qa.canonical),
        proxy_rows=len(qa.proxies),
        minute_issue_rows=len(qa.minute_issues),
        hourly_issue_rows=len(qa.hourly_issues),
        issue_counts=qa.minute_issues.issue_type.value_counts().to_dict()
        if len(qa.minute_issues)
        else {},
        at=now(),
    )
    result["qa_schema_version"] = 2
    result["code_sha256"] = {
        p.name: digest(p) for p in Path(__file__).parent.glob("hf_minute_long*.py")
    }
    write_json(folder / "qa_v2_receipt.json", result)
    return result


def update_register(out: Path, source: dict, result: dict, raw: dict) -> None:
    """Dated additive month entries; recovery never erases or duplicates an earlier block."""
    path = out / "data_quality_issue_register.md"
    marker = f"<!-- MONTH_V2:{source['month']} -->"
    if marker in path.read_text():
        return
    counts = result["issue_counts"]
    with path.open("a") as f:
        f.write(
            f"\n{marker}\n\n## {source['month']} — {now()}\n\n"
            f"RAW {raw['rows']:,} rows; CANONICAL {result['canonical_rows']:,}; "
            f"FILL proxies {result['proxy_rows']:,}; hourly {result['hourly_rows']:,}. "
            f"SOURCE/RECONCILIATION issues: `{json.dumps(counts, sort_keys=True)}`. "
            "Disposition: quality flags retained; no source correction or training admission. "
            f"Evidence: months/{source['month']}/qa_v2_receipt.json and partitioned issue tables.\n"
        )


def run(out: Path, guard: Guard) -> None:
    manifest = json.loads((out / "source_revision_manifest.json").read_text())
    scope = json.loads((out / "active_scope.json").read_text())
    if scope["start_month"] != "2010-07":
        raise ValueError("STOP_IDENTITY: active human scope must begin July2010")
    files = [r for r in manifest["files"] if r["month"] >= scope["start_month"]]
    checkpoint = out / scope["checkpoint"]
    states: dict[str, dict] = (
        json.loads(checkpoint.read_text())
        if checkpoint.exists()
        else {s["month"]: dict(status="PENDING", source=s) for s in files}
    )
    previous = {}
    start = time.monotonic()
    register = out / "data_quality_issue_register.md"
    if not register.exists():
        register.write_text(
            "# Package 018D persistent data-quality issue register\n\n"
            f"Source {DATASET} at {REVISION}; namespace {NAMESPACE}. "
            "All exact symbols retained, no old data pooling. COMPLETE_WITH_QUALITY_FLAGS is "
            "a source-collection status, not training readiness.\n\n"
            "## Policy and issue taxonomy\n\n"
            "SOURCE: absence, invalid values, zero/stale volume, action/scale uncertainty, "
            "identity/coverage unknowns. RECONCILIATION: identical copies collapsed once; "
            "all conflicting versions excluded from canonical, every raw version retained. "
            "FILL: separate zero-volume price proxies, volume unknown, <=5 minutes as known "
            "at completed-hour clock, no overnight/opening/cross-stock carry. AGGREGATION: "
            "partial/open/close/volume/stub flags. Strict/moderate/broad are source-coverage "
            "standards, never a final model mask. No price or label clipping.\n\n"
            "## Preserved March 2026 evidence\n\n"
            "018C STOP_QUALITY remains correct under its policy: 226,433 raw rows, 25 conflicting "
            "keys/50 rows, 387 absent expected RTH slots, PEP three-minute gap and MRK/WFC "
            "missing session opens. This package keeps those rows and flags instead of aborting. "
            "See the immutable ta018c_hf20_hf1m_2026-10-22_143400 audit.\n\n"
            "## Unresolved human decisions\n\n"
            "Actual adjustment/action/dividend/publication semantics and historic issuer/ticker "
            "identity remain unverified. No retroactive aliases, inferred split factors, final "
            "15-year selection, feature/target transforms or training are authorized. "
            "Missing minutes do not prove no trading. "
            "Source comparison is descriptive only.\n"
        )
    if "<!-- QA_SCHEMA_V2 -->" not in register.read_text():
        with register.open("a") as f:
            f.write(
                "\n<!-- QA_SCHEMA_V2 -->\n\n## QA schema v2 authority\n\n"
                "Initial v1 trial outputs/checkpoints are retained. The v2 issue schema "
                "correctly reports actual source multiplicity behind synthetic proxies "
                "(zero for absent minutes, all raw versions for conflicts). "
                "qa_v2 directories and qa_v2_receipt.json are authoritative; raw unchanged. "
                "The same deterministic price and volume rules apply.\n"
            )
    for i, source in enumerate(files):
        month = source["month"]
        folder = out / "months" / month
        state = states[month]
        if state["status"] == "HOURLY_DONE":
            result = json.loads((folder / "qa_v2_receipt.json").read_text())
            # One bounded final validation of every committed file, not repeated historic QA.
            for ref in result["files"].values():
                if digest(Path(ref["path"])) != ref["sha256"]:
                    raise ValueError("STOP_SOURCE_INTEGRITY: derived checkpoint changed")
            previous.update(result["last_observed"])
            continue
        print(
            json.dumps(
                dict(
                    event="MONTH_START",
                    month=month,
                    index=i + 1,
                    total=len(files),
                    source_bytes=source["bytes"],
                    at=now(),
                )
            ),
            flush=True,
        )
        state.update(status="IN_PROGRESS", started_at=now())
        replace_json(checkpoint, states)
        try:
            raw = acquire_month(source, out, guard)
            state.update(status="EXTRACTED_VERIFIED", raw=raw)
            replace_json(checkpoint, states)
            qa_path = folder / "qa_v2_receipt.json"
            if qa_path.exists():
                result = json.loads(qa_path.read_text())
                for ref in result["files"].values():
                    if digest(Path(ref["path"])) != ref["sha256"]:
                        raise ValueError("STOP_SOURCE_INTEGRITY: derived checkpoint differs")
            else:
                frame = pq.ParquetFile(raw["path"]).read().to_pandas()
                qa = process_month(frame, month, raw["sha256"], raw["path"], previous)
                state.update(status="RAW_QA_DONE")
                replace_json(checkpoint, states)
                result = publish_qa(qa, month, folder, guard)
            previous.update(result["last_observed"])
            update_register(out, source, result, raw)
            state.update(status="HOURLY_DONE", finished_at=now(), qa=result)
            replace_json(checkpoint, states)
            pd.DataFrame(
                [
                    dict(
                        month=m,
                        status=r["status"],
                        source_bytes=r["source"]["bytes"],
                        raw_rows=r.get("raw", {}).get("rows"),
                        raw_bytes=r.get("raw", {}).get("bytes"),
                        hourly_rows=r.get("qa", {}).get("hourly_rows"),
                    )
                    for m, r in states.items()
                ]
            ).to_csv(out / "monthly_checkpoint.csv", index=False)
            print(
                json.dumps(
                    dict(
                        event="MONTH_DONE",
                        month=month,
                        raw_rows=raw["rows"],
                        hourly_rows=result["hourly_rows"],
                        proxy_rows=result["proxy_rows"],
                        issue_counts=result["issue_counts"],
                        done=sum(r["status"] == "HOURLY_DONE" for r in states.values()),
                        task_disk_bytes=guard.footprint(),
                        at=now(),
                    )
                ),
                flush=True,
            )
        except Exception as exc:
            retryable = isinstance(exc, requests.RequestException)
            status = "FAILED_RETRYABLE" if retryable else "BLOCKED"
            state.update(status=status, error_type=type(exc).__name__, at=now())
            replace_json(checkpoint, states)
            replace_json(
                out / "run_status.json",
                dict(
                    status="INTERRUPTED_RESUMABLE" if retryable else str(exc),
                    failed_month=month,
                    done=sum(r["status"] == "HOURLY_DONE" for r in states.values()),
                    recovery=f".venv/bin/python -B -m lstm_data.hf_minute_long --run --out {out}",
                    unprocessed=[m for m, r in states.items() if r["status"] != "HOURLY_DONE"],
                ),
            )
            raise
    replace_json(
        out / "run_status.json",
        dict(
            status="ALL_MONTHS_EXTRACTED_AND_HOURLY_DONE",
            months=len(files),
            seconds_this_invocation=time.monotonic() - start,
            at=now(),
            ledger=32,
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--verify-only", action="store_true")
    modes.add_argument("--qa-smoke", action="store_true")
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--report", action="store_true")
    args = parser.parse_args()
    verify_identity(args.out)
    guard = Guard(args.out)
    if args.verify_only:
        verify_remote(args.out, guard)
    elif args.qa_smoke:
        raw = json.loads(MARCH.with_suffix(".manifest.json").read_text())
        frame = pq.ParquetFile(MARCH).read().to_pandas()
        tick = time.monotonic()
        qa = process_month(frame, "2026-03", raw["sha256"], MARCH.as_posix())
        smoke = args.out / "march_smoke"
        smoke.mkdir(exist_ok=False)
        qa.coverage.to_csv(smoke / "coverage.csv", index=False)
        qa.hourly.to_parquet(smoke / "hourly.parquet", index=False)
        write_json(
            smoke / "result.json",
            dict(
                raw_rows=len(frame),
                hourly_rows=len(qa.hourly),
                proxy_rows=len(qa.proxies),
                seconds=time.monotonic() - tick,
                issues=qa.minute_issues.issue_type.value_counts().to_dict(),
            ),
        )
        print((smoke / "result.json").read_text(), flush=True)
    elif args.run:
        run(args.out, guard)
    else:
        from .hf_minute_long_report import build_reports

        build_reports(args.out, guard)


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as exc:
        # Requests exception strings may embed a signed CDN redirect; never persist them.
        print(
            json.dumps(dict(status="INTERRUPTED_RESUMABLE", error_type=type(exc).__name__)),
            flush=True,
        )
        sys.exit(1)
