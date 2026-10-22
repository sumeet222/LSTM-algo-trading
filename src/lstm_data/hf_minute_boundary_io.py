"""Isolated, metered HTTP range access for the Package018C source boundary gate."""

from __future__ import annotations

import io
import json
import re
from pathlib import Path

import pyarrow.parquet as pq
import requests

from .config import write_json
from .hf20_source import SYMBOLS
from .hf_hourly_source import PublicHTTP

DATASET = "mito0o852/OHLCV-1m"
REVISION = "776328445b7ac6e7815ef3a483e9c8ded1eb6d56"
NAMESPACE = "HF20_HF1M_15Y_v1"


class RemoteParquet(io.RawIOBase):
    """Seekable range reader; no filesystem/HF/Xet cache and no whole-file reads."""

    def __init__(self, http: PublicHTTP, path: str, size: int):
        super().__init__()
        if not re.fullmatch(r"data/ohlcv_\d{4}-(?:0[1-9]|1[0-2])\.parquet", path):
            raise ValueError("STOP_IDENTITY: unexpected source path")
        if type(size) is not int or size < 8:
            raise ValueError("STOP_IDENTITY: source file size required")
        self.http, self.size, self.position = http, size, 0
        self.url = f"https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/{path}"
        self.http.session.hooks["response"] = [self.validate_response]

    def validate_response(self, response: requests.Response, **kwargs: object) -> requests.Response:
        """Check final range totals as well as boundaries; redirects have no body reads here."""
        if response.status_code == 206:
            requested = response.request.headers.get("Range", "")
            if not isinstance(requested, str):
                raise ValueError("STOP_SOURCE: textual byte range required")
            expected = requested.replace("bytes=", "bytes ") + f"/{self.size}"
            if response.headers.get("Content-Range") != expected:
                raise ValueError("STOP_SOURCE: range total or boundaries differ from pinned file")
        return response

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.position

    def seek(self, offset: int, whence: int = 0) -> int:
        position = offset + (0 if whence == 0 else self.position if whence == 1 else self.size)
        if whence not in (0, 1, 2) or not 0 <= position <= self.size:
            raise ValueError("Invalid range seek")
        self.position = position
        return position

    def read(self, size: int = -1) -> bytes:
        if size < 0 or size > 64_000_000:
            raise ValueError("STOP_STORAGE: unbounded or oversized range read")
        size = min(size, self.size - self.position)
        if not size:
            return b""
        end = self.position + size - 1
        # Distinct public range keys avoid intermediaries serving a cached different range.
        url = self.url + f"?range_start={self.position}&range_end={end}"
        body = self.http.get(url, size, (self.position, end))
        if len(body) != size:
            raise ValueError("STOP_SOURCE: short range response")
        self.position += size
        return body


def describe(parquet: pq.ParquetFile) -> dict:
    """Capture actual footer identities, statistics, and projected transfer estimates."""
    groups = []
    for i in range(parquet.metadata.num_row_groups):
        group = parquet.metadata.row_group(i)
        cols = []
        for j in range(group.num_columns):
            col = group.column(j)
            stat = col.statistics
            cols.append(
                dict(
                    name=col.path_in_schema,
                    compressed_bytes=col.total_compressed_size,
                    uncompressed_bytes=col.total_uncompressed_size,
                    dictionary_offset=col.dictionary_page_offset,
                    data_offset=col.data_page_offset,
                    min=str(stat.min) if stat and stat.has_min_max else None,
                    max=str(stat.max) if stat and stat.has_min_max else None,
                    nulls=stat.null_count if stat else None,
                )
            )
        groups.append(dict(row_group=i, rows=group.num_rows, columns=cols))
    return dict(
        schema=str(parquet.schema_arrow),
        columns=parquet.schema_arrow.names,
        rows=parquet.metadata.num_rows,
        row_groups=groups,
        created_by=parquet.metadata.created_by,
    )


def probe(out: Path, prior_manifest: Path, month: str) -> None:
    """Verify remote pin first, then measure one real ticker row-group range read."""
    manifest = json.loads(prior_manifest.read_text())
    if manifest["dataset"] != DATASET or manifest["revision"] != REVISION:
        raise ValueError("STOP_IDENTITY: source manifest mismatch")
    source = next(r for r in manifest["files"] if r["month"] == month)
    http = PublicHTTP(128_000_000)
    try:
        body = http.get(
            f"https://huggingface.co/api/datasets/{DATASET}/revision/{REVISION}", 1_000_000
        )
        info = json.loads(body)
        if info["sha"] != REVISION or info["id"] != DATASET:
            raise ValueError("STOP_IDENTITY: remote pin or dataset mismatch")
        write_json(
            out / "identity_remote_verified.json",
            dict(
                status="PASS_IDENTITY",
                dataset=DATASET,
                revision=REVISION,
                namespace=NAMESPACE,
                remote_info=info,
                source=source,
            ),
        )
        print("PASS_IDENTITY: exact remote dataset and immutable pin verified", flush=True)
        remote = RemoteParquet(http, source["path"], source["bytes"])
        parquet = pq.ParquetFile(remote, pre_buffer=False)
        footer = describe(parquet)
        write_json(out / f"footer_{month}.json", footer)
        before = http.bytes_received
        tickers = parquet.read_row_group(0, columns=["ticker"], use_threads=False)
        write_json(
            out / "selective_trial.json",
            dict(
                month=month,
                row_group=0,
                rows=tickers.num_rows,
                actual_tickers=tickers.column("ticker").unique().to_pylist(),
                ticker_group_transfer_bytes=http.bytes_received - before,
                total_body_bytes=http.bytes_received,
                whole_month_bytes=source["bytes"],
                persistent_data_cache_bytes=0,
                cache_backend="NONE_NATIVE_REQUESTS",
                footer_and_real_column_read=True,
            ),
        )
        print(
            json.dumps(
                dict(
                    rows=footer["rows"],
                    groups=len(footer["row_groups"]),
                    schema=footer["schema"],
                    total_body_bytes=http.bytes_received,
                    ticker_group_bytes=http.bytes_received - before,
                )
            ),
            flush=True,
        )
    finally:
        write_json(
            out / "probe_http_events.json",
            dict(
                events=http.events,
                bytes_received=http.bytes_received,
                automatic_retries=0,
                signed_redirect_urls_logged=False,
                credentials_used=False,
                disk_cache_bytes=0,
            ),
        )
        http.session.close()


def locate(out: Path, prior_manifest: Path, month: str) -> None:
    """Scan actual ticker columns, proving absence only after every row group is read."""
    out.mkdir(parents=True, exist_ok=False)
    manifest = json.loads(prior_manifest.read_text())
    if manifest["dataset"] != DATASET or manifest["revision"] != REVISION:
        raise ValueError("STOP_IDENTITY: source manifest mismatch")
    source = next(r for r in manifest["files"] if r["month"] == month)
    http = PublicHTTP(4_000_000)
    counts = {s: 0 for s in SYMBOLS}
    groups = []
    try:
        remote = RemoteParquet(http, source["path"], source["bytes"])
        parquet = pq.ParquetFile(remote, pre_buffer=False)
        for i in range(parquet.metadata.num_row_groups):
            column = parquet.read_row_group(i, columns=["ticker"], use_threads=False)
            values = column.column("ticker").value_counts().to_pylist()
            found = {r["values"]: r["counts"] for r in values if r["values"] in counts}
            for s, n in found.items():
                counts[s] += n
            group = parquet.metadata.row_group(i)
            groups.append(
                dict(
                    row_group=i,
                    selected_counts=found,
                    rows=group.num_rows,
                    compressed_bytes=sum(
                        group.column(j).total_compressed_size for j in range(group.num_columns)
                    ),
                )
            )
            print(json.dumps(dict(row_group=i, found=found, bytes=http.bytes_received)), flush=True)
        selected_bytes = sum(g["compressed_bytes"] for g in groups if g["selected_counts"])
        write_json(
            out / "ticker_location.json",
            dict(
                source=source,
                all_ticker_row_groups_scanned=True,
                counts=counts,
                groups=groups,
                absent=[s for s in SYMBOLS if not counts[s]],
                source_rows=parquet.metadata.num_rows,
                measured_range_body_bytes=http.bytes_received,
                selected_row_groups_compressed_bytes=selected_bytes,
                projected_selected_group_fraction=selected_bytes / source["bytes"],
                footer=describe(parquet),
                note="Ticker presence only; timestamp/OHLCV quality not yet established",
            ),
        )
    finally:
        write_json(
            out / "http_events.json",
            dict(
                events=http.events,
                bytes_received=http.bytes_received,
                automatic_retries=0,
                signed_redirect_urls_logged=False,
                credentials_used=False,
                disk_cache_bytes=0,
            ),
        )
        http.session.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--month", default="2026-03")
    parser.add_argument("--locate", action="store_true")
    args = parser.parse_args()
    if args.locate:
        locate(args.out, args.manifest, args.month)
    else:
        if (args.out / "probe_http_events.json").exists():
            raise ValueError("Probe receipts already exist; use a fresh output directory")
        probe(args.out, args.manifest, args.month)
