"""Pinned, single-month acquisition and bounded storage for Package 018D."""

from __future__ import annotations

import hashlib
import json
import os
import resource
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .config import digest, now, write_json
from .hf20_source import SYMBOLS
from .hf_hourly_source import PublicHTTP, storage_bytes
from .hf_minute_boundary import COLUMNS, validate_schema
from .hf_minute_boundary_io import DATASET, REVISION, RemoteParquet, describe
from .hf_minute_preflight import validate_months

NAMESPACE = "HF20_HF1M_LONG_v1"
RAW = Path("data/raw/hf20_hf1m_long_v1") / REVISION
SCRATCH = Path("data/interim/hf20_hf1m_long_v1") / REVISION
DERIVED = Path("data/processed/hf20_hf1m_long_v1") / REVISION
MARCH = (
    Path("data/raw/hf20_hf1m_15y_v1")
    / REVISION
    / "raw_selected_1m/year=2026/month=03/selected.parquet"
)


def replace_json(path: Path, value: dict) -> None:
    """Atomic task-owned checkpoint update; immutable source data use no-clobber publication."""
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix(path.suffix + ".pending")
    pending.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    with pending.open("rb") as f:
        os.fsync(f.fileno())
    os.replace(pending, path)


def tables_equal(left: pa.Table, right: pa.Table) -> bool:
    """Preserve source NaNs as NaNs and nulls as nulls during independent roundtrip checks."""
    if not left.schema.equals(right.schema) or left.num_rows != right.num_rows:
        return False
    for a, b in zip(left.columns, right.columns, strict=True):
        if a.equals(b):
            continue
        if not pa.types.is_floating(a.type) or not a.is_null().equals(b.is_null()):
            return False
        if not np.array_equal(
            a.to_numpy(zero_copy_only=False), b.to_numpy(zero_copy_only=False), equal_nan=True
        ):
            return False
    return True


@dataclass
class Guard:
    out: Path
    peak: int = 0

    def footprint(self) -> int:
        paths = (self.out, RAW, SCRATCH, DERIVED, Path(".ruff_cache"), Path(".pytest_cache"))
        return storage_bytes(paths) + sum(
            p.stat().st_size
            for pattern in (
                "src/lstm_data/hf_minute_long*.py",
                "src/lstm_data/__pycache__/hf_minute_long*.pyc",
                "tests/test_hf_minute_long*.py",
                "docs/track_a/HF1M_LONG_SOURCE_018D.md",
                "reports/codex_sessions/*018d*.md",
            )
            for p in Path().glob(pattern)
        )

    def check(self, reserve: int, purpose: str) -> dict:
        """Reserve uncertain writes before they start; count existing tool caches conservatively."""
        if reserve < 0:
            raise ValueError("STOP_STORAGE: negative reservation")
        used = self.footprint()
        self.peak = max(self.peak, used)
        free = shutil.disk_usage(self.out).free
        row = dict(
            at=now(),
            used_bytes=used,
            reserved_bytes=reserve,
            purpose=purpose,
            free_bytes=free,
            hard_ceiling=10_000_000_000,
            pause_ceiling=9_000_000_000,
            external_tool_temp_reserve=2_000_000,
            hf_xet_cache_bytes=0,
        )
        row["sha256"] = hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest()
        if used + reserve + 2_000_000 >= 9_000_000_000 or free < reserve + 2_000_000_000:
            raise ValueError("STOP_STORAGE: guarded occupied/free-space reservation failed")
        with (self.out / "resource_guard.jsonl").open("a") as f:
            f.write(json.dumps(row) + "\n")
        return row

    def parquet(self, path: Path, table: pa.Table) -> dict:
        """Bounded immutable output, reopened and checked before atomic publication."""
        if path.exists():
            if not tables_equal(pq.ParquetFile(path).read(), table):
                raise ValueError(
                    "STOP_SOURCE_INTEGRITY: existing output differs on deterministic replay"
                )
            return dict(
                path=path.as_posix(),
                bytes=path.stat().st_size,
                sha256=digest(path),
                rows=table.num_rows,
            )
        self.check(max(table.nbytes * 2 + 1_000_000, 2_000_000), "before_write:" + str(path))
        path.parent.mkdir(parents=True, exist_ok=True)
        pending = path.with_suffix(".part")
        if pending.exists():
            pending.unlink()  # own uncommitted output, never a source snapshot
        pq.write_table(table, pending, compression="zstd", row_group_size=65536)
        restored = pq.ParquetFile(pending).read()
        if not tables_equal(restored, table):
            raise ValueError("STOP_SOURCE_INTEGRITY: independent output equality failed")
        sha = digest(pending)
        with pending.open("rb") as f:
            os.fsync(f.fileno())
        os.link(pending, path)
        pending.unlink()
        self.check(0, "after_write:" + str(path))
        return dict(
            path=path.as_posix(), bytes=path.stat().st_size, sha256=sha, rows=table.num_rows
        )


class LoggedHTTP(PublicHTTP):
    """Persist each request receipt, including failed/partial reads, without signed URLs."""

    def __init__(self, log: Path):
        super().__init__(1_000_000_000_000)
        self.log = log

    def get(self, url: str, maximum: int, byte_range: tuple[int, int] | None = None) -> bytes:
        before = len(self.events)
        try:
            return super().get(url, maximum, byte_range)
        finally:
            if len(self.events) > before:
                with self.log.open("a") as f:
                    f.write(json.dumps(self.events[-1]) + "\n")


class GroupRemote(RemoteParquet):
    """Coalesce one contiguous compressed row group to avoid seven separate HTTP requests."""

    def __init__(self, http: PublicHTTP, path: str, size: int):
        super().__init__(http, path, size)
        self.block = b""
        self.block_start = 0

    def prefetch(self, group) -> None:
        chunks = [group.column(i) for i in range(group.num_columns)]
        starts = [c.dictionary_page_offset or c.data_page_offset for c in chunks]
        start = min(starts)
        end = max(s + c.total_compressed_size for s, c in zip(starts, chunks, strict=True))
        self.block = b""
        self.seek(start)
        self.block = super().read(end - start)
        self.block_start = start

    def read(self, size: int = -1) -> bytes:
        if (
            size >= 0
            and self.block_start <= self.position
            and (self.position + size <= self.block_start + len(self.block))
        ):
            start = self.position - self.block_start
            self.position += size
            return self.block[start : start + size]
        return super().read(size)


def verify_remote(out: Path, guard: Guard) -> list[dict]:
    """Revalidate complete immutable listing; no raw data read before logged identity PASS."""
    http = LoggedHTTP(out / "metadata_http.jsonl")
    try:
        api = f"https://huggingface.co/api/datasets/{DATASET}"
        info = json.loads(http.get(f"{api}/revision/{REVISION}", 1_000_000))
        if info["sha"] != REVISION or info["id"] != DATASET:
            raise ValueError("STOP_IDENTITY: remote source/pin differs")
        tree = json.loads(http.get(f"{api}/tree/{REVISION}?recursive=true&limit=1000", 1_000_000))
        files = validate_months(REVISION, tree)
        local = json.loads((out / "identity_initial.json").read_text())
        keys = ("month", "path", "bytes", "lfs_sha256", "git_blob_oid", "xet_hash")
        if [{k: r[k] for k in keys} for r in files] != [
            {k: r[k] for k in keys} for r in local["files"]
        ] or {r["path"] for r in tree if r["type"] == "file"} != {
            r["rfilename"] for r in info["siblings"]
        }:
            raise ValueError("STOP_IDENTITY: immutable complete file listing changed")
        guard.check(1_000_000, "metadata_publication")
        write_json(
            out / "source_revision_manifest.json",
            dict(
                dataset=DATASET,
                revision=REVISION,
                namespace=NAMESPACE,
                files=files,
                metadata_body_bytes=http.bytes_received,
                at=now(),
            ),
        )
        with (out / "dataset_identity_preflight_018D.md").open("a") as f:
            f.write(
                f"\nRemote ID/pin/listing verified: PASS_IDENTITY. {len(files)} monthly files; "
                "no raw transfer before this checkpoint.\n"
            )
        print(
            json.dumps(
                dict(
                    status="PASS_IDENTITY",
                    months=len(files),
                    upstream_total_bytes=sum(r["bytes"] for r in files),
                )
            ),
            flush=True,
        )
        return files
    finally:
        http.session.close()


def selected_table(table: pa.Table, source: dict, group: int, offset: int) -> pa.Table:
    mask = pd.Series(table.column("ticker").to_pylist()).isin(SYMBOLS).to_numpy()
    positions = np.flatnonzero(mask)
    selected = table.filter(pa.array(mask))
    n = selected.num_rows
    for name, value in (
        ("source_dataset", DATASET),
        ("source_revision", REVISION),
        ("source_file", source["path"]),
        ("source_row_group", group),
        ("is_genuine", True),
    ):
        dtype = (
            pa.bool_()
            if isinstance(value, bool)
            else pa.int64()
            if isinstance(value, int)
            else pa.string()
        )
        selected = selected.append_column(name, pa.array([value] * n, type=dtype))
    return selected.append_column("source_row", pa.array(positions + offset, type=pa.int64()))


def stream_full(source: dict, folder: Path, http: LoggedHTTP, guard: Guard) -> Path:
    """One allowlisted provider month, identity encoding, exact SHA256 and bounded disk writes."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "provider.parquet.part"
    if path.exists():
        if path.stat().st_size == source["bytes"]:
            if digest(path) != source["lfs_sha256"]:
                raise ValueError("STOP_SOURCE_INTEGRITY: completed staged source checksum changed")
            return path  # completed download is reused, never transferred twice
        # Partial transport bytes are disposable; selected raw/source evidence are never deleted.
        path.unlink()
    guard.check(source["bytes"] + 64_000_000, "reserve_single_provider_month")
    url = f"https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/{source['path']}"
    event: dict = dict(
        url=url, started_at=now(), bytes=0, strategy="FULL_MONTH_STREAM", redirects=0
    )
    http.events.append(event)
    start = time.monotonic()
    try:
        with http.session.get(
            url, headers={"Accept-Encoding": "identity"}, stream=True, timeout=(15, 90)
        ) as response:
            response.raise_for_status()
            event.update(status=response.status_code, redirects=len(response.history))
            if response.headers.get("Content-Encoding", "identity") != "identity":
                raise ValueError("STOP_SOURCE_INTEGRITY: encoded full response")
            if int(response.headers.get("Content-Length", source["bytes"])) != source["bytes"]:
                raise ValueError("STOP_SOURCE_INTEGRITY: full response size mismatch")
            hashed = hashlib.sha256()
            with path.open("xb") as f:
                while event["bytes"] < source["bytes"]:
                    # The complete file size has already been reserved, including this write.
                    block = response.raw.read(min(1_048_576, source["bytes"] - event["bytes"]))
                    if not block:
                        break
                    f.write(block)
                    hashed.update(block)
                    event["bytes"] += len(block)
                    http.bytes_received += len(block)
            if event["bytes"] != source["bytes"] or hashed.hexdigest() != source["lfs_sha256"]:
                raise ValueError("STOP_SOURCE_INTEGRITY: incomplete or corrupt full source month")
        return path
    finally:
        event["seconds"] = time.monotonic() - start
        with http.log.open("a") as f:
            f.write(json.dumps(event) + "\n")


def acquire_month(source: dict, out: Path, guard: Guard) -> dict:
    """Actual ticker scan, measured adaptive strategy and exact selected-only raw transaction."""
    month = source["month"]
    if month < "2010-07":
        raise ValueError("STOP_IDENTITY: pre-July2010 acquisition prohibited by human amendment")
    folder = out / "months" / month
    folder.mkdir(parents=True, exist_ok=True)
    receipt_path = folder / "raw_receipt.json"
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        if receipt["source"] != source or digest(Path(receipt["path"])) != receipt["sha256"]:
            raise ValueError("STOP_SOURCE_INTEGRITY: committed raw checkpoint changed")
        staged = SCRATCH / month / "provider.parquet.part"
        if staged.exists():
            staged.unlink()  # raw independently reverified first; completed source is disposable
            replace_json(
                folder / "raw_cleanup.json",
                dict(
                    provider_scratch_deleted=True,
                    raw_reverified_before_cleanup=True,
                    remaining_scratch_bytes=0,
                ),
            )
        return receipt
    guard.check(source["bytes"] + 128_000_000, "before_month:" + month)
    if month == "2026-03" and MARCH.exists() and MARCH.with_suffix(".manifest.json").exists():
        old = json.loads(MARCH.with_suffix(".manifest.json").read_text())
        if old["source"] != source or digest(MARCH) != old["sha256"]:
            raise ValueError("STOP_SOURCE_INTEGRITY: prior March snapshot differs")
        result = dict(
            source=source,
            path=MARCH.as_posix(),
            sha256=old["sha256"],
            bytes=old["bytes"],
            rows=old["rows"],
            strategy="REUSE_HASH_VERIFIED_018C_SINGLE_COPY",
            source_bytes_this_package=0,
            full_source_hash_verified=False,
            source_row_equality_verified=True,
            at=now(),
        )
        write_json(receipt_path, result)
        return result
    http = LoggedHTTP(folder / "http_events.jsonl")
    staged = None
    try:
        remote = GroupRemote(http, source["path"], source["bytes"])
        parquet = pq.ParquetFile(remote, pre_buffer=False)
        validate_schema(parquet.schema_arrow)
        meta = describe(parquet)
        location_path = folder / "row_groups.json"
        if location_path.exists():
            saved = json.loads(location_path.read_text())
            if saved["footer"] != meta:
                raise ValueError("STOP_SOURCE_INTEGRITY: source footer changed on resume")
            groups = saved["groups"]
        else:
            groups = []
            for i in range(parquet.num_row_groups):
                ticker = parquet.read_row_group(i, columns=["ticker"], use_threads=False)
                counts = {
                    r["values"]: r["counts"]
                    for r in ticker.column("ticker").value_counts().to_pylist()
                    if r["values"] in SYMBOLS
                }
                group = parquet.metadata.row_group(i)
                groups.append(
                    dict(
                        group=i,
                        rows=group.num_rows,
                        selected=counts,
                        compressed=sum(
                            group.column(j).total_compressed_size for j in range(group.num_columns)
                        ),
                    )
                )
            write_json(location_path, dict(footer=meta, groups=groups, source=source))
        expected_counts = {s: sum(g["selected"].get(s, 0) for g in groups) for s in SYMBOLS}
        projected = sum(g["compressed"] for g in groups if g["selected"])
        full = projected > source["bytes"] * 0.75 and projected > 0
        if full:
            staged = stream_full(source, SCRATCH / month, http, guard)
            parquet = pq.ParquetFile(staged)
            validate_schema(parquet.schema_arrow)
        tables = []
        offset = 0
        for spec in groups:
            i = spec["group"]
            if spec["selected"]:
                group = parquet.metadata.row_group(i)
                if group.total_byte_size > 128_000_000:
                    raise ValueError("STOP_RESOURCE: uncompressed source row group exceeds128MB")
                if not full:
                    remote.prefetch(group)
                table = parquet.read_row_group(i, columns=COLUMNS, use_threads=False)
                selected = selected_table(table, source, i, offset)
                counts = pd.Series(selected.column("ticker").to_pylist()).value_counts().to_dict()
                if counts != spec["selected"]:
                    raise ValueError(
                        "STOP_SOURCE_INTEGRITY: selected counts disagree with ticker scan"
                    )
                tables.append(selected)
                if sum(t.nbytes for t in tables) > 256_000_000:
                    raise ValueError("STOP_RESOURCE: selected month exceeds256MB verification plan")
            offset += spec["rows"]
        if tables:
            table = pa.concat_tables(tables)
        else:
            # Real observed zero across all ticker columns, not an unsampled/guessed zero.
            table = selected_table(
                pa.Table.from_batches([], schema=parquet.schema_arrow), source, 0, 0
            )
        record = guard.parquet(RAW / "raw_1m_selected" / f"{month}.parquet", table)
        result = dict(
            record,
            source=source,
            strategy="FULL_MONTH_SHA_VERIFIED"
            if full
            else "TICKER_SCAN_THEN_COALESCED_SELECTED_GROUPS",
            counts=expected_counts,
            source_bytes_this_package=http.bytes_received,
            projected_group_bytes=projected,
            source_row_equality_verified=True,
            full_source_hash_verified=full,
            at=now(),
            hidden_cache_bytes=0,
            scratch_deleted=False,
            source_schema=meta["schema"],
        )
        write_json(receipt_path, result)
        if staged is not None:
            staged.unlink()  # only after independently verified raw publication and receipt
        result["scratch_deleted"] = True
        replace_json(
            folder / "raw_cleanup.json",
            dict(
                provider_scratch_deleted=True,
                remaining_scratch_bytes=storage_bytes((SCRATCH / month,)),
            ),
        )
        guard.check(0, "after_raw_cleanup:" + month)
        return result
    finally:
        replace_json(
            folder / "transfer_runtime.json",
            dict(
                bytes_this_attempt=http.bytes_received,
                events_this_attempt=len(http.events),
                peak_RSS_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                * (1 if sys.platform == "darwin" else 1024),
                automatic_retries=0,
            ),
        )
        http.session.close()
