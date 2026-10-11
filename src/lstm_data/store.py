"""One canonical stock store with immutable monthly chunks and checkpoint manifests."""

from __future__ import annotations

import io
import json
from collections.abc import Callable
from pathlib import Path

import pandas as pd

from .aggregation import aggregate_session_hours
from .alpaca import HistoricalClient, request_params
from .calendar import schedule, stock_qa
from .config import atomic_new, digest, fingerprint, now, public_config, write_json
from .validation import normalize, require_valid


def monthly_requests(cfg: dict) -> list[dict]:
    """Fixed calendar dates in New York; inclusive API end excludes next chunk exactly."""
    start = pd.Timestamp(cfg["start_date"], tz=cfg["timezone"])
    stop = pd.Timestamp(cfg["end_date"], tz=cfg["timezone"]) + pd.DateOffset(days=1)
    result = []
    while start < stop:
        boundary = min(start + pd.offsets.MonthBegin(1), stop)
        result.append(
            request_params(
                cfg,
                cfg["symbols"],
                start.tz_convert("UTC").isoformat(),
                (boundary.tz_convert("UTC") - pd.Timedelta(nanoseconds=1)).isoformat(),
            )
        )
        start = boundary
    return result


def plan(cfg: dict) -> dict:
    """No credentials/network/writes. Conservative 24-hour/session size bounds."""
    requests = monthly_requests(cfg)
    sessions = len(schedule(cfg["start_date"], cfg["end_date"]))
    rows = sessions * len(cfg["symbols"]) * 24
    source_rows = rows * (2 if cfg["timeframe"] == "30Min" else 1)
    return {
        "network": False,
        "writes": False,
        "config_fingerprint": cfg["_fingerprint"],
        "requests": requests,
        "minimum_initial_calls": len(requests),
        "upper_calendar_session_hourly_rows_estimate": rows,
        "source_timeframe": cfg["timeframe"],
        "estimated_source_rows": source_rows,
        "estimated_uncompressed_bytes_at_128_per_row": source_rows * 128,
        "estimated_30min_alternative_rows": rows * 2,
        "estimated_30min_uncompressed_bytes": rows * 2 * 128,
        "estimated_30min_minimum_calls": len(requests),
        "estimated_page_bound_note": "Each monthly response may require multiple pages; "
        "30Min approximately doubles rows, not necessarily initial calls.",
        "paths_touched_on_execution": [cfg["stock_store"], cfg["report_dir"]],
        "gate": "Human bulk approval plus matching successful SIP/timing pilot required. "
        "30Min source / on-demand hourly aggregation approved; fresh pilot required.",
    }


def chunk_paths(store: Path, params: dict) -> tuple[Path, Path]:
    key = fingerprint(params)[:20]
    month = pd.Timestamp(params["start"]).strftime("%Y-%m")
    stem = f"{month}-{key}"
    return store / f"{stem}.parquet", store / f"{stem}.manifest.json"


def read_verified(path: Path, manifest_path: Path, params: dict) -> pd.DataFrame:
    """Resume only byte-verified, parameter-matched, schema-valid canonical chunks."""
    manifest = json.loads(manifest_path.read_text())
    if manifest["params"] != params or manifest["sha256"] != digest(path):
        raise ValueError("Existing chunk provenance/checksum mismatch; no overwrite or redownload")
    frame = normalize(pd.read_parquet(path), stocks=True)
    require_valid(frame, stocks=True)
    if len(frame) != manifest["rows"]:
        raise ValueError("Manifest row count differs")
    lower, upper = pd.Timestamp(params["start"]), pd.Timestamp(params["end"])
    if ((frame.timestamp < lower) | (frame.timestamp > upper)).any():
        raise ValueError("Existing chunk has out-of-bounds timestamps")
    if set(frame.symbol) != set(params["symbols"].split(",")):
        raise ValueError("Existing chunk has missing/unexpected requested symbols")
    for column, value in (
        ("feed", params["feed"]),
        ("adjustment", params["adjustment"]),
        ("source_timeframe", params["timeframe"]),
    ):
        if column not in frame or not (frame[column] == value).all():
            raise ValueError(f"Existing chunk {column} does not match manifest")
    return frame


def save_chunk(
    store: Path,
    frame: pd.DataFrame,
    params: dict,
    events: list[dict],
    cfg: dict,
    coverage_audit: dict | None = None,
    *, before_publish: Callable[[int], None] | None = None,
) -> dict:
    """Atomically publish each new file; an interrupted pair is detected on resume."""
    data_path, manifest_path = chunk_paths(store, params)
    require_valid(frame, stocks=True)
    if set(frame.symbol) != set(params["symbols"].split(",")):
        raise ValueError("Cannot checkpoint an incomplete symbol universe")
    if data_path.exists() or manifest_path.exists():
        raise FileExistsError("Chunk already exists (possibly interrupted); never overwrite it")
    buffer = io.BytesIO()
    frame = frame.copy()
    frame["provenance_id"] = fingerprint(params)
    frame.to_parquet(buffer, index=False, compression="zstd")
    payload = buffer.getvalue()
    import hashlib

    manifest = {
        "schema_version": 1,
        "retrieved_at": now(),
        "params": params,
        "rows": len(frame),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "size_bytes": len(payload),
        "source": "Alpaca historical SIP bars",
        "config": public_config(cfg),
        "canonical_kind": f"native_provider_{cfg['timeframe']}; extended hours preserved; "
        "session-anchored hourly panels created on demand only",
        "coverage": {
            symbol: {
                "rows": len(group),
                "first": str(group.timestamp.min()),
                "last": str(group.timestamp.max()),
            }
            for symbol, group in frame.groupby("symbol")
        },
        "missing_requested_symbols": sorted(set(params["symbols"].split(",")) - set(frame.symbol)),
        "events": events,
        "coverage_audit": coverage_audit,
        "coverage_status": "All API pages exhausted; market-calendar QA still required. "
        "Missing/partial sessions are diagnostic, never filled.",
    }
    if before_publish:
        before_publish(len(payload) + len((json.dumps(manifest, indent=2, sort_keys=True)
                                          + "\n").encode()))
    atomic_new(data_path, payload)
    write_json(manifest_path, manifest)
    return manifest


def check_approval(cfg: dict, approval_path: Path) -> dict:
    """Require reviewed, matching pilot evidence before any bulk request."""
    approval = json.loads(approval_path.read_text())
    if (
        approval.get("config_fingerprint") != cfg["_fingerprint"]
        or approval.get("approved") is not True
        or approval.get("source_timeframe_approved") != cfg["timeframe"]
        or approval.get("session_aggregation_approved") is not True
        or approval.get("adjustment_approved") != cfg["adjustment"]
    ):
        raise ValueError(
            "Approval must explicitly cover this config, source/aggregation and adjustment"
        )
    pilot_path = cfg["_root"] / approval["pilot_report"]
    if digest(pilot_path) != approval["pilot_sha256"]:
        raise ValueError("Pilot evidence checksum differs from approval")
    pilot = json.loads(pilot_path.read_text())
    if (
        pilot.get("config_fingerprint") != cfg["_fingerprint"]
        or pilot.get("sip_access_pass") is not True
        or pilot.get("timing_gate_pass") is not True
    ):
        raise ValueError("SIP/timing pilot did not pass; bulk blocked; no override or IEX fallback")
    return approval


def acquire(cfg: dict, client: HistoricalClient, approval_path: Path) -> list[dict]:
    """Download/resume monthly shared chunks only after the stop/go approval gate."""
    check_approval(cfg, approval_path)
    store = cfg["_stock_store"]
    store.mkdir(parents=True, exist_ok=True)
    # A lock prevents two sessions from fetching/publishing the same canonical chunk.
    lock = store / ".acquisition.lock"
    try:
        handle = lock.open("x")
    except FileExistsError:
        raise ValueError(
            "Store lock exists; inspect active/interrupted writer before resuming"
        ) from None
    result = []
    try:
        with handle:
            handle.write(now())
        for params in monthly_requests(cfg):
            data_path, manifest_path = chunk_paths(store, params)
            month = pd.Timestamp(params["start"]).strftime("%Y-%m")
            incompatible = [
                p for p in store.glob(f"{month}-*") if p not in {data_path, manifest_path}
            ]
            if incompatible:
                raise ValueError(
                    "Existing same-month data use different parameters; "
                    "review before creating another canonical dataset"
                )
            if data_path.exists() and manifest_path.exists():
                read_verified(data_path, manifest_path, params)
                result.append({"file": data_path.name, "resumed": True})
                continue
            if data_path.exists() or manifest_path.exists():
                raise ValueError("Interrupted chunk pair; preserve files and review before resume")
            event_start = len(client.events)
            frame = client.bars(params)
            if set(frame.symbol) != set(cfg["symbols"]):
                raise ValueError("Missing requested symbol(s); stop, do not replace candidates")
            qa = stock_qa(
                frame,
                cfg["symbols"],
                pd.Timestamp(params["start"]).tz_convert(cfg["timezone"]).strftime("%Y-%m-%d"),
                pd.Timestamp(params["end"]).tz_convert(cfg["timezone"]).strftime("%Y-%m-%d"),
            )
            timing_pass = qa["native_session_anchored_gate_pass"]
            coverage_audit = {"source_qa": qa["symbols"]}
            if cfg["timeframe"] == "30Min":
                _, aggregation = aggregate_session_hours(
                    frame,
                    cfg["symbols"],
                    pd.Timestamp(params["start"]).tz_convert(cfg["timezone"]).strftime("%Y-%m-%d"),
                    pd.Timestamp(params["end"]).tz_convert(cfg["timezone"]).strftime("%Y-%m-%d"),
                )
                # The pilot establishes aggregation conventions. Bulk gaps are
                # observations to preserve, not permission to invent/repair bars.
                # aggregate_session_hours already rejects off-grid timestamps.
                timing_pass = not any(
                    day["extra_overlapping_starts_utc"] or day["partial_overlap_count"]
                    for day in qa["daily"]
                )
                coverage_audit.update(
                    {
                        "missing_source_bars": aggregation["missing_source_bars"],
                        "incomplete_windows": [
                            window for window in aggregation["windows"] if not window["complete"]
                        ],
                        "complete_windows": aggregation["complete_windows"],
                        "stub_windows": aggregation["expected_stub_windows"],
                    }
                )
            if not timing_pass:
                raise ValueError(
                    "Chunk timing/coverage violates pilot gate; no canonical file written"
                )
            result.append(
                save_chunk(
                    store,
                    frame,
                    params,
                    client.events[event_start:],
                    cfg,
                    coverage_audit=coverage_audit,
                )
            )
    finally:
        lock.unlink(missing_ok=True)
    return result


def load_store(cfg: dict) -> pd.DataFrame:
    frames = []
    for params in monthly_requests(cfg):
        data, manifest = chunk_paths(cfg["_stock_store"], params)
        if data.exists() and manifest.exists():
            frames.append(read_verified(data, manifest, params))
        elif data.exists() or manifest.exists():
            raise ValueError("Interrupted store chunk; review required")
    if not frames:
        raise FileNotFoundError(
            "No verified stock chunks; run SIP pilot before approved acquisition"
        )
    frame = pd.concat(frames, ignore_index=True).sort_values(["symbol", "timestamp"])
    require_valid(frame, stocks=True)
    return frame
