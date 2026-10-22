"""Package018C single-month extraction and source-only boundary quality evidence.

There is deliberately no historical loop, filling, feature construction or modeling API.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import exchange_calendars as xcals
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .config import digest, now, write_json
from .hf20_source import SYMBOLS
from .hf_hourly_source import PublicHTTP, storage_bytes
from .hf_minute_boundary_io import DATASET, NAMESPACE, REVISION, RemoteParquet

COLUMNS = ["timestamp", "open", "high", "low", "close", "volume", "ticker"]
BASE = Path("data/raw/hf20_hf1m_15y_v1") / REVISION / "raw_selected_1m"
SCRATCH = Path("data/interim/hf20_hf1m_15y_v1") / REVISION
DERIVED = Path("data/processed/hf20_hf1m_15y_v1") / REVISION


@dataclass
class ResourceGuard:
    """Count all managed task paths, reserve uncertain writes and independent free space."""

    paths: tuple[Path, ...]
    log: Path
    peak_bytes: int = 0

    def check(self, reserve: int, purpose: str) -> dict:
        current = storage_bytes(tuple(p for p in self.paths if p.is_dir()))
        current += sum(p.stat().st_size for p in self.paths if p.is_file())
        self.peak_bytes = max(self.peak_bytes, current)
        free = shutil.disk_usage(self.log.parent).free
        record = dict(
            at=now(),
            purpose=purpose,
            current_bytes=current,
            reserve_bytes=reserve,
            worst_case_bytes=current + reserve,
            free_bytes=free,
            ceiling=10_000_000_000,
            conservative_pause=9_000_000_000,
            independent_free_reserve=2_000_000_000,
            hf_xet_disk_cache_bytes=0,
            memory_plan="One <=128MB uncompressed row group plus <=256MB extracts",
        )
        record["sha256"] = hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
        if current + reserve >= 9_000_000_000 or free < reserve + 2_000_000_000:
            raise ValueError("STOP_STORAGE: reservation or independent free-space check failed")
        with self.log.open("a") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")
        return record


def validate_schema(schema: pa.Schema) -> None:
    """Reject changed clocks, fields or numeric representations rather than coercing raw rows."""
    expected = pa.schema(
        [
            pa.field("timestamp", pa.timestamp("ns", tz="UTC")),
            *[pa.field(c, pa.float64()) for c in COLUMNS[1:6]],
            pa.field("ticker", pa.string()),
        ]
    )
    if not schema.remove_metadata().equals(expected):
        raise ValueError("STOP_IDENTITY: actual minute schema differs from verified source schema")


def partition_path(month: str) -> Path:
    """Accept only literal monthly partition keys in the new isolated raw namespace."""
    period = pd.Period(month, freq="M")
    if str(period) != month:
        raise ValueError("STOP_IDENTITY: noncanonical month")
    return BASE / f"year={period.year:04d}" / f"month={period.month:02d}" / "selected.parquet"


def add_provenance(table: pa.Table, source: dict, group: int, offset: int) -> pa.Table:
    """Filter exact ticker strings, preserving original columns, values and source row order."""
    mask = pd.Series(table.column("ticker").to_pylist()).isin(SYMBOLS).to_numpy()
    positions = np.flatnonzero(mask)
    result = table.filter(pa.array(mask))
    n = result.num_rows
    for key, value in (
        ("source_dataset", DATASET),
        ("source_revision", REVISION),
        ("source_file", source["path"]),
        ("source_row_group", group),
        ("is_genuine", True),
    ):
        result = result.append_column(key, pa.array([value] * n))
    return result.append_column("source_row", pa.array(positions + offset, type=pa.int64()))


def acquire(location: dict, destination: Path, guard: ResourceGuard, http: PublicHTTP) -> dict:
    """One remote month: write selected rows, independently compare, then atomically publish.

    This selective strategy creates no provider-wide local file or HF/Xet cache to delete.
    A committed receipt is required before a subsequent invocation can reuse a partition.
    """
    source = location["source"]
    if destination.resolve() != partition_path(source["month"]).resolve():
        raise ValueError("STOP_IDENTITY: destination outside exact new monthly partition")
    receipt = destination.with_suffix(".manifest.json")
    if receipt.exists():
        previous = json.loads(receipt.read_text())
        if (
            previous["source"] != source
            or previous["sha256"] != digest(destination)
            or previous["namespace"] != NAMESPACE
        ):
            raise ValueError("STOP_IDENTITY: checkpoint source or checksum mismatch")
        return dict(previous, reused_verified_partition=True)
    if destination.exists() or destination.with_suffix(".part").exists():
        raise ValueError("STOP_INTERRUPTED_RESUMABLE: uncommitted output; inspect before resuming")
    guard.check(512_000_000, "before_month_" + source["month"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".part")
    remote = RemoteParquet(http, source["path"], source["bytes"])
    parquet = pq.ParquetFile(remote, pre_buffer=False)
    validate_schema(parquet.schema_arrow)
    if parquet.metadata.num_rows != location["source_rows"]:
        raise ValueError("STOP_IDENTITY: source footer rows changed")
    if len(location["groups"]) != parquet.metadata.num_row_groups:
        raise ValueError("STOP_IDENTITY: incomplete ticker scan")
    tables = []
    writer = None
    offset = 0
    started = time.monotonic()
    try:
        for spec in location["groups"]:
            i = spec["row_group"]
            if spec["selected_counts"]:
                group = parquet.metadata.row_group(i)
                if group.total_byte_size > 128_000_000:
                    raise ValueError("STOP_STORAGE: row group exceeds bounded memory plan")
                table = parquet.read_row_group(i, columns=COLUMNS, use_threads=False)
                selected = add_provenance(table, source, i, offset)
                actual = pd.Series(selected.column("ticker").to_pylist()).value_counts().to_dict()
                if actual != spec["selected_counts"]:
                    raise ValueError("STOP_SOURCE: independently located ticker counts changed")
                guard.check(max(selected.nbytes * 2, 1_000_000), f"before_output_group_{i}")
                if writer is None:
                    writer = pq.ParquetWriter(temporary, selected.schema, compression="zstd")
                writer.write_table(selected)
                tables.append(selected)
                if sum(t.nbytes for t in tables) > 256_000_000:
                    raise ValueError("STOP_STORAGE: bounded selected verification set exceeded")
                print(
                    json.dumps(
                        dict(
                            month=source["month"],
                            row_group=i,
                            selected_rows=selected.num_rows,
                            network_bytes=http.bytes_received,
                        )
                    ),
                    flush=True,
                )
            offset += spec["rows"]
    finally:
        if writer is not None:
            writer.close()
    if not tables:
        raise ValueError("STOP_BOUNDARY_STOCK_MISSING: no selected rows")
    restored = pq.ParquetFile(temporary)
    if restored.num_row_groups != len(tables):
        raise ValueError("STOP_SOURCE: extracted row-group count mismatch")
    for i, original in enumerate(tables):
        if not restored.read_row_group(i).equals(original):
            raise ValueError("STOP_SOURCE: exact source-to-output value comparison failed")
    checksum = digest(temporary)
    with temporary.open("rb") as f:
        os.fsync(f.fileno())
    os.link(temporary, destination)  # atomic no-clobber promotion; same inode, not a mirror
    temporary.unlink()
    result = dict(
        namespace=NAMESPACE,
        source=source,
        path=destination.as_posix(),
        bytes=destination.stat().st_size,
        sha256=checksum,
        rows=sum(t.num_rows for t in tables),
        ticker_counts=location["counts"],
        read_strategy="REMOTE_TICKER_LOCATION_THEN_SELECTED_ROW_GROUPS",
        source_rows_equal_independently_read_output=True,
        upstream_whole_file_sha256_verified_locally=False,
        whole_file_note=(
            "Pinned ranges; upstream LFS hash is metadata, not a local full-file hash"
        ),
        temporary_deleted=True,
        provider_wide_scratch_files=0,
        hidden_cache_bytes=0,
        resumability="COMMITTED_VERIFIED",
        seconds=time.monotonic() - started,
        reused_verified_partition=False,
    )
    guard.check(1_000_000, "after_atomic_publication")
    write_json(receipt, result)
    return result


@dataclass(frozen=True)
class Session:
    day: pd.Timestamp
    open: pd.Timestamp
    close: pd.Timestamp


def session_grid(month: str) -> tuple[list[Session], pd.DatetimeIndex]:
    """Actual XNYS minute-start grid with holidays, DST and shortened sessions."""
    period = pd.Period(month, freq="M")
    cal = xcals.get_calendar("XNYS", start=period.start_time, end=period.end_time.normalize())
    schedule = cal.schedule.loc[str(period.start_time.date()) : str(period.end_time.date())]
    sessions = [
        Session(day, opened, closed)
        for day, opened, closed in zip(
            pd.DatetimeIndex(schedule.index),
            pd.DatetimeIndex(schedule["open"]),
            pd.DatetimeIndex(schedule["close"]),
            strict=True,
        )
    ]
    grids = [pd.date_range(r.open, r.close, freq="min", inclusive="left") for r in sessions]
    grid = pd.DatetimeIndex(grids[0].append(grids[1:]))
    return sessions, grid


def longest_run(mask: np.ndarray) -> int:
    edges = np.diff(np.r_[False, mask, False].astype(np.int8))
    starts, ends = np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)
    return int((ends - starts).max()) if len(starts) else 0


def audit_month(frame: pd.DataFrame, month: str) -> tuple[list[dict], list[dict], list[dict]]:
    """Conservative raw QA; no price repair, imputation, labels or model eligibility."""
    if not isinstance(frame["timestamp"].dtype, pd.DatetimeTZDtype):
        raise ValueError("STOP_IDENTITY: timezone-aware genuine timestamps required")
    if str(frame["timestamp"].dt.tz) != "UTC":
        raise ValueError("STOP_IDENTITY: UTC source required")
    schedule, grid = session_grid(month)
    summary, sessions, anomalies = [], [], []
    for symbol_index, symbol in enumerate(SYMBOLS):
        part = frame.loc[frame.ticker == symbol].sort_values("timestamp")
        idx = pd.DatetimeIndex(part.timestamp)
        numbers = part[["open", "high", "low", "close", "volume"]].to_numpy()
        invalid = (
            ~np.isfinite(numbers).all(axis=1)
            | (numbers[:, :4] <= 0).any(axis=1)
            | (numbers[:, 4] < 0)
            | (numbers[:, 1] < numbers[:, :4].max(axis=1))
            | (numbers[:, 2] > numbers[:, :4].min(axis=1))
        )
        off_minute = idx != idx.floor("min")
        wrong_month = idx.tz_convert("America/New_York").strftime("%Y-%m") != month
        duplicates = part.duplicated("timestamp", keep=False)
        conflicting = (
            part.loc[duplicates].drop_duplicates(COLUMNS).duplicated("timestamp", keep=False)
        )
        observed = grid.isin(idx)
        usable_idx = pd.DatetimeIndex(
            part.loc[~invalid & ~off_minute & ~wrong_month & ~duplicates, "timestamp"]
        )
        usable = grid.isin(usable_idx)
        missing = ~usable
        session_rows = []
        cursor = 0
        for session in schedule:
            expected = int((session.close - session.open).total_seconds() // 60)
            seen = usable[cursor : cursor + expected]
            raw_seen = observed[cursor : cursor + expected]
            row = dict(
                ticker=symbol,
                month=month,
                session=str(session.day.date()),
                open_utc=session.open.isoformat(),
                close_utc=session.close.isoformat(),
                expected_minutes=expected,
                genuine_minutes=int(raw_seen.sum()),
                valid_genuine_minutes=int(seen.sum()),
                missing_minutes=int((~seen).sum()),
                max_consecutive_missing=longest_run(~seen),
                opening_minute_genuine=bool(seen[0]),
                final_minute_genuine=bool(seen[-1]),
            )
            sessions.append(row)
            session_rows.append(row)
            if not seen.all():
                for t in grid[cursor : cursor + expected][~seen]:
                    anomalies.append(
                        dict(
                            ticker=symbol,
                            month=month,
                            kind="MISSING_OR_INVALID_RTH",
                            timestamp=t.isoformat(),
                        )
                    )
            cursor += expected
        bad = part.loc[invalid | off_minute | wrong_month | duplicates]
        for record in bad.head(20).to_dict("records"):
            anomalies.append(
                dict(
                    month=month,
                    kind="INVALID_OR_DUPLICATE",
                    **{str(k): str(v) for k, v in record.items()},
                )
            )
        rth = part.loc[part.timestamp.isin(grid)].drop_duplicates("timestamp")
        jumps = np.abs(np.log(rth.close.to_numpy()[1:] / rth.close.to_numpy()[:-1]))
        jump_count = int((jumps > np.log(1.25)).sum())
        for i in np.flatnonzero(jumps > np.log(1.25))[:20]:
            anomalies.append(
                dict(
                    ticker=symbol,
                    month=month,
                    kind="UNRESOLVED_25PCT_JUMP",
                    previous_timestamp=str(rth.iloc[i].timestamp),
                    timestamp=str(rth.iloc[i + 1].timestamp),
                    previous_close=float(rth.iloc[i].close),
                    close=float(rth.iloc[i + 1].close),
                )
            )
        absent = len(part) == 0
        material = (
            invalid.any()
            or off_minute.any()
            or wrong_month.any()
            or duplicates.any()
            or jump_count > 0
            or max(r["max_consecutive_missing"] for r in session_rows) > 2
            or any(
                not r["opening_minute_genuine"] or not r["final_minute_genuine"]
                for r in session_rows
            )
        )
        ratio = float(usable.sum() / len(grid))
        state = (
            "NOT_PRESENT" if absent else ("INSUFFICIENT" if material or ratio < 0.98 else "USABLE")
        )
        summary.append(
            dict(
                ticker=symbol,
                symbol_index=symbol_index,
                month=month,
                sampling_status="SAMPLED_ALL_SOURCE_ROWS",
                state=state,
                actual_rows=len(part),
                first_genuine_utc=str(idx.min()) if len(idx) else None,
                last_genuine_utc=str(idx.max()) if len(idx) else None,
                observed_regular_sessions=sum(r["genuine_minutes"] > 0 for r in session_rows),
                expected_sessions=len(schedule),
                expected_rth_minutes=len(grid),
                observed_rth_minutes=int(observed.sum()),
                observed_rth_ratio=float(observed.sum() / len(grid)),
                valid_genuine_rth_minutes=int(usable.sum()),
                missing_genuine_minutes=int((~observed).sum()),
                missing_minutes=int(missing.sum()),
                coverage_ratio=ratio,
                malformed_rows=int(invalid.sum()),
                duplicate_rows=int(duplicates.sum()),
                duplicate_rth_rows=int((duplicates & part.timestamp.isin(grid)).sum()),
                exact_duplicate_rows=int(part.duplicated(COLUMNS, keep=False).sum()),
                conflicting_duplicate_rows=int(conflicting.sum()),
                off_minute_rows=int(off_minute.sum()),
                wrong_month_rows=int(wrong_month.sum()),
                max_consecutive_missing=max(r["max_consecutive_missing"] for r in session_rows),
                missing_open_sessions=sum(not r["opening_minute_genuine"] for r in session_rows),
                missing_final_sessions=sum(not r["final_minute_genuine"] for r in session_rows),
                unresolved_25pct_jumps=jump_count,
                row_groups=sorted(int(i) for i in part.source_row_group.unique())
                if "source_row_group" in part
                else [],
            )
        )
    all_missing = ~grid.isin(frame.timestamp)
    for t in grid[all_missing]:
        anomalies.append(
            dict(ticker="ALL20", month=month, kind="SYNCHRONOUS_MISSING", timestamp=t.isoformat())
        )
    return summary, sessions, anomalies


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--location", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    location = json.loads(args.location.read_text())
    identity = json.loads((args.out.parent / "identity_remote_verified.json").read_text())
    if (
        identity["status"] != "PASS_IDENTITY"
        or identity["dataset"] != DATASET
        or identity["revision"] != REVISION
        or not location["all_ticker_row_groups_scanned"]
        or location["source"] != identity["source"]
    ):
        raise ValueError("STOP_IDENTITY: logged remote preflight and complete ticker scan required")
    month = location["source"]["month"]
    # This entry point cannot be used to bypass the first end-month gate for historical acquisition.
    if month != "2026-03":
        raise ValueError("STOP_UNVERIFIED: only the initial latest boundary month is released")
    code = tuple(Path(__file__).parent.glob("hf_minute_boundary*.py"))
    guard = ResourceGuard(
        (args.out.parent, BASE, SCRATCH, DERIVED, *code), args.out / "resource_guard.jsonl"
    )
    http = PublicHTTP(location["source"]["bytes"] + 1_000_000)
    started = time.monotonic()
    status = "STOP_INTERRUPTED_RESUMABLE"
    try:
        result = acquire(location, partition_path(month), guard, http)
        write_json(args.out / "acquisition.json", result)
        frame = pq.ParquetFile(result["path"]).read().to_pandas()
        summary, sessions, anomalies = audit_month(frame, month)
        pd.DataFrame(summary).to_csv(args.out / "ticker_month_qa.csv", index=False)
        pd.DataFrame(sessions).to_csv(args.out / "ticker_session_qa.csv", index=False)
        pd.DataFrame(anomalies).to_csv(args.out / "anomalies.csv", index=False)
        status = (
            "STOP_BOUNDARY_STOCK_MISSING"
            if any(r["state"] == "NOT_PRESENT" for r in summary)
            else "STOP_QUALITY"
            if any(r["state"] != "USABLE" for r in summary)
            else "LATEST_MONTH_USABLE_BOUNDARY_GATE_STILL_PENDING"
        )
        write_json(
            args.out / "gate.json",
            dict(
                status=status, month=month, summary=summary, training="FORBIDDEN", ledger_pairs=32
            ),
        )
        print(
            json.dumps(dict(status=status, rows=result["rows"], bytes=result["bytes"])), flush=True
        )
    finally:
        write_json(
            args.out / "http_events.json",
            dict(
                events=http.events,
                body_bytes=http.bytes_received,
                automatic_retries=0,
                cache_bytes=0,
            ),
        )
        guard.check(1_000_000, "final_resource_receipt")
        write_json(
            args.out / "runtime.json",
            dict(
                status=status,
                seconds=time.monotonic() - started,
                body_bytes=http.bytes_received,
                peak_task_disk_bytes=guard.peak_bytes,
                peak_RSS_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                * (1 if sys.platform == "darwin" else 1024),
                hf_xet_cache_bytes=0,
                new_model_starts=0,
            ),
        )
        http.session.close()


if __name__ == "__main__":
    main()
