"""Bounded Hugging Face hourly acquisition and feasibility CLI; never trains a model."""

from __future__ import annotations

import argparse
import json
import platform
import re
import resource
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

from .config import digest, now, write_json
from .hf_hourly_audit import census, load_core
from .hf_hourly_diagnostics import action_diagnostics, cached_overlap, nominal_interval_diagnostics
from .hf_hourly_feasibility import evaluate
from .hf_hourly_report import documents
from .hf_hourly_source import (
    PublicHTTP,
    download,
    metadata,
    publish_cache_manifest,
    remote_footer,
    storage_bytes,
    verify_cached,
)


def audit(manifest: dict, config: dict, out: Path, compare: bool = True) -> dict:
    started = time.monotonic()
    frame, schema = load_core(manifest)
    c = census(frame, schema, out)
    print(f"CENSUS {len(frame)} rows / {len(c.symbols)} symbols", flush=True)
    phase = time.monotonic()
    decision = evaluate(c, config, config["publisher_sector_etfs"], out)
    evaluate_seconds = time.monotonic() - phase
    authority = json.loads(Path("configs/hf_twelvedata_action_checks_v1.json").read_text())
    action_diagnostics(frame, authority, out)
    nominal_interval_diagnostics(frame, out)
    if compare:
        cached_overlap(frame, out, Path.cwd())
    documents(out, manifest, decision, c.quality, Path(config["_config_path"]))
    write_json(
        out / "audit_actual_runtime.json",
        dict(
            elapsed_seconds=time.monotonic() - started,
            scan_seconds=schema["scan_seconds"],
            census_seconds=c.quality["census_seconds"],
            feasibility_seconds=evaluate_seconds,
            model_training=False,
            targets_created=0,
        ),
    )
    return decision


def run(args: argparse.Namespace) -> int:
    started = time.monotonic()
    config = json.loads(args.config.read_text())
    config["_config_path"] = str(args.config)
    if (
        config.get("task") != "TA-HF-TWELVEDATA-1H-FEASIBILITY-001"
        or config.get("training_authorized") is not False
    ):
        raise ValueError("SOURCE_ONLY_CONFIGURATION_REQUIRED")
    out = args.out or Path("reports/data_audit") / (
        "ta_hf_twelvedata_hourly_"
        + datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d_%H%M%S")
    )
    out.mkdir(parents=True, exist_ok=False)
    cache = args.cache or Path(config["cache_root"])
    http = PublicHTTP(int(config["download_budget_bytes"]))
    result = {"flags": ["SOURCE_NOT_ACQUIRED"]}
    try:
        if args.audit_cached:
            if not args.revision or not re.fullmatch(r"[0-9a-f]{40}", args.revision):
                raise ValueError("AUDIT_CACHED_REQUIRES_EXACT_REVISION")
            cache_manifest = cache / args.revision / "acquisition_manifest.json"
            manifest = json.loads(cache_manifest.read_text())
            if manifest["revision"] != args.revision:
                raise ValueError("CACHED_REVISION_CHANGED")
            remote = {Path(r["path"]).name: r for r in manifest["remote_files"]}
            for row in manifest["files"]:
                verify_cached(Path(row["path"]), remote[Path(row["path"]).name])
            write_json(out / "acquisition_manifest.json", manifest)
        else:
            meta = metadata(http, args.revision)
            write_json(out / "remote_metadata.json", meta)
            footers = {}
            for row in meta["files"]:
                try:
                    footers[row["path"]] = remote_footer(http, meta["revision"], row)
                except (requests.RequestException, ValueError) as exc:
                    footers[row["path"]] = dict(metadata_unavailable=type(exc).__name__)
            write_json(out / "remote_parquet_metadata.json", footers)
            if args.metadata_only:
                (out / "NEXT_DECISION.md").write_text(
                    "# Metadata-only source inspection\n\nSOURCE_NOT_ACQUIRED. "
                    f"Pinned revision{meta['revision']}; three hourly files "
                    f"{sum(r['size'] for r in meta['files']):,}bytes. "
                    "Per-symbol exact missingness,20-stock qualification, adjustment and rights "
                    "remain UNVERIFIED until the bounded acquisition and row audit. "
                    "No credentials, training, provider API or original-confirmation access.\n"
                )
                return 0
            local = [
                download(
                    http, cache, out, meta["revision"], row, int(config["working_budget_bytes"])
                )
                for row in meta["files"]
            ]
            manifest = publish_cache_manifest(cache, meta, local)
            write_json(out / "acquisition_manifest.json", manifest)
        result = audit(manifest, config, out, not args.no_cached_comparison)
        return 0
    except (requests.RequestException, ValueError, FileNotFoundError) as exc:
        write_json(
            out / "source_hold.json",
            dict(
                status="SOURCE_NOT_ACQUIRED_OR_AUDIT_HOLD",
                exception_type=type(exc).__name__,
                code=str(exc) if isinstance(exc, ValueError) else None,
                original_sources_unchanged=True,
                training=False,
            ),
        )
        (out / "NEXT_DECISION.md").write_text(
            "# Source acquisition/audit HOLD\n\nSOURCE_NOT_ACQUIRED or causal/schema/cache "
            "integrity HOLD; see source_hold.json and HTTP event types. Coverage/20names/dates "
            "are UNVERIFIED. Retry only the three bars_1h files with a pinned revision and byte "
            "caps; do not infer feasibility or acquire another source automatically.\n"
        )
        return 2
    finally:
        write_json(
            out / "resource_usage.json",
            dict(
                at=now(),
                elapsed_seconds=time.monotonic() - started,
                application_HTTP_requests=len(http.events),
                requests_including_redirects=sum(
                    1 + int(r.get("redirects", 0)) for r in http.events
                ),
                response_body_bytes=http.bytes_received,
                automatic_retries=0,
                events=http.events,
                download_budget_bytes=http.limit,
                working_budget_bytes=config["working_budget_bytes"],
                storage_bytes=storage_bytes((cache, out)),
                peak_RSS_bytes=int(
                    resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                    * (1 if sys.platform == "darwin" else 1024)
                ),
                Python=platform.python_version(),
                machine=platform.machine(),
                flags=result["flags"],
                config_sha256=digest(args.config),
                new_neural_pairs=0,
                original_confirmation_access=False,
            ),
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--metadata-only", action="store_true")
    mode.add_argument("--audit-cached", action="store_true")
    mode.add_argument("--download-bars-1h", action="store_true")
    parser.add_argument("--revision", help="Immutable40-character HF commit SHA; required offline")
    parser.add_argument(
        "--config", type=Path, default=Path("configs/hf_twelvedata_hourly_audit_v3.json")
    )
    parser.add_argument("--out", type=Path, help="New immutable report namespace")
    parser.add_argument(
        "--cache", type=Path, help="Existing one-copy raw cache or new configured location"
    )
    parser.add_argument(
        "--no-cached-comparison",
        action="store_true",
        help="Skip unavailable original-source comparison",
    )
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
