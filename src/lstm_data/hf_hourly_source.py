"""Public, revision-pinned hourly-only Hugging Face acquisition with hard byte limits."""

from __future__ import annotations

import io
import json
import os
import re
import struct
import time
from dataclasses import dataclass, field
from pathlib import Path

import pyarrow.parquet as pq
import requests

from .config import atomic_new, digest, now, write_json

DATASET = "twelvedata/financial-world-model"
FILES = tuple(f"bars_1h/{s}.parquet" for s in ("train", "val", "test"))
API = "https://huggingface.co/api/datasets/" + DATASET


def storage_bytes(paths: tuple[Path, ...]) -> int:
    """Count only this task's raw cache/reports; count hard-linked bytes once."""
    seen: set[tuple[int, int]] = set()
    total = 0
    for root in paths:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.is_file():
                st = p.stat()
                key = st.st_dev, st.st_ino
                if key not in seen:
                    total += st.st_size
                    seen.add(key)
    return total


@dataclass
class PublicHTTP:
    """No environment credentials, login, cookies from user profiles, or automatic retries."""

    limit: int
    bytes_received: int = 0
    events: list[dict] = field(default_factory=list)
    session: requests.Session = field(default_factory=requests.Session)

    def __post_init__(self) -> None:
        self.session.trust_env = False

    def get(self, url: str, maximum: int, byte_range: tuple[int, int] | None = None) -> bytes:
        if maximum <= 0 or self.bytes_received + maximum > self.limit:
            raise ValueError("DOWNLOAD_CAP_BEFORE_REQUEST")
        if not url.startswith(
            (
                "https://huggingface.co/",
                "https://raw.githubusercontent.com/",
                "https://api.github.com/",
            )
        ):
            raise ValueError("ONLY_REVIEWED_PUBLIC_METADATA_AND_HF_HOSTS")
        headers = {"Accept-Encoding": "identity"}
        if byte_range is not None:
            headers["Range"] = f"bytes={byte_range[0]}-{byte_range[1]}"
        started = time.monotonic()
        event = dict(url=url, requested_range=byte_range, bytes=0, started_at=now(), seconds=0.0)
        self.events.append(event)
        try:
            with self.session.get(url, headers=headers, stream=True, timeout=(15, 60)) as response:
                event["status"] = response.status_code
                event["redirects"] = len(response.history)
                response.raise_for_status()
                if response.headers.get("Content-Encoding", "identity") != "identity":
                    raise ValueError("IDENTITY_TRANSFER_REQUIRED_FOR_BYTE_ACCOUNTING")
                length = response.headers.get("Content-Length")
                if length is not None and int(length) > maximum:
                    raise ValueError("RESPONSE_SIZE_EXCEEDS_RESERVED_BYTES")
                if byte_range is not None:
                    expected = f"bytes {byte_range[0]}-{byte_range[1]}/"
                    if response.status_code != 206 or not response.headers.get(
                        "Content-Range", ""
                    ).startswith(expected):
                        raise ValueError("RANGE_NOT_HONORED_NO_FULL_FILE_READ")
                body = bytearray()
                received = 0
                while len(body) < maximum:
                    block = response.raw.read(min(65536, maximum - len(body)))
                    if not block:
                        break
                    self.bytes_received += len(block)
                    received += len(block)
                    event["bytes"] = received
                    if len(body) + len(block) > maximum or self.bytes_received > self.limit:
                        raise ValueError("DOWNLOAD_CAP_DURING_RESPONSE")
                    body.extend(block)
                return bytes(body)
        except (requests.RequestException, ValueError) as exc:
            # Never persist signed redirect URLs, authentication headers or credential text.
            event["failure"] = type(exc).__name__
            raise
        finally:
            event["seconds"] = time.monotonic() - started


def validate_listing(revision: str, listing: list[dict], budget: int) -> list[dict]:
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("IMMUTABLE_COMMIT_REQUIRED")
    files = [r for r in listing if r.get("path") in FILES]
    if len(files) != 3 or {r["path"] for r in files} != set(FILES):
        raise ValueError("EXACT_THREE_HOURLY_FILES_REQUIRED")
    for row in files:
        if (
            type(row.get("size")) is not int
            or row["size"] <= 8
            or row.get("lfs", {}).get("size") != row["size"]
            or not re.fullmatch(r"[0-9a-f]{64}", row.get("lfs", {}).get("oid", ""))
        ):
            raise ValueError("EXACT_REMOTE_SIZE_AND_LFS_SHA256_REQUIRED")
    if sum(r["size"] for r in files) > budget:
        raise ValueError("THREE_FILE_DOWNLOAD_CAP")
    return sorted(files, key=lambda r: FILES.index(r["path"]))


def metadata(http: PublicHTTP, revision: str | None = None) -> dict:
    info = json.loads(http.get(API + ("/revision/" + revision if revision else ""), 1000000))
    rev = info["sha"]
    if revision and revision != rev:
        raise ValueError("REQUESTED_REVISION_CHANGED")
    listing = json.loads(http.get(f"{API}/tree/{rev}/bars_1h?expand=true", 1000000))
    files = validate_listing(rev, listing, http.limit)
    card = http.get(f"https://huggingface.co/datasets/{DATASET}/raw/{rev}/README.md", 200000)
    return dict(
        dataset=DATASET,
        revision=rev,
        retrieved_at=now(),
        info=info,
        files=files,
        card=card.decode(),
        credentials_used=False,
        automatic_retries=0,
    )


def parquet_summary(p: pq.ParquetFile) -> dict:
    groups = []
    for i in range(p.metadata.num_row_groups):
        g = p.metadata.row_group(i)
        stats = {}
        for j in range(g.num_columns):
            col = g.column(j)
            if col.path_in_schema in {"symbol", "datetime"} and col.statistics:
                s = col.statistics
                stats[col.path_in_schema] = dict(min=str(s.min), max=str(s.max), nulls=s.null_count)
        groups.append(dict(group=i, rows=g.num_rows, stats=stats))
    return dict(
        rows=p.metadata.num_rows,
        row_groups=groups,
        schema=str(p.schema_arrow),
        columns=p.schema_arrow.names,
        created_by=p.metadata.created_by,
    )


def remote_footer(http: PublicHTTP, revision: str, row: dict) -> dict:
    size = row["size"]
    url = f"https://huggingface.co/datasets/{DATASET}/resolve/{revision}/{row['path']}"
    tail = http.get(url, 8, (size - 8, size - 1))
    if len(tail) != 8 or tail[-4:] != b"PAR1":
        raise ValueError("PARQUET_FOOTER_REQUIRED")
    n = struct.unpack("<I", tail[:4])[0]
    if not 0 < n < min(size - 8, 5000000):
        raise ValueError("BOUNDED_PARQUET_METADATA_REQUIRED")
    body = http.get(url, n + 8, (size - n - 8, size - 1))
    return parquet_summary(pq.ParquetFile(io.BytesIO(b"PAR1" + body)))


def cached_file(cache: Path, revision: str, row: dict) -> Path:
    if row["path"] not in FILES or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("EXACT_HOURLY_CACHE_KEY_REQUIRED")
    return cache / revision / row["path"]


def verify_cached(path: Path, row: dict) -> None:
    if path.stat().st_size != row["size"] or digest(path) != row["lfs"]["oid"]:
        raise ValueError("IMMUTABLE_CACHE_HASH_OR_SIZE_MISMATCH")


def download(
    http: PublicHTTP, cache: Path, out: Path, revision: str, row: dict, working_limit: int
) -> dict:
    """One streaming file; verified final cache reuse and bounded exact-revision partial resume."""
    path = cached_file(cache, revision, row)
    if path.exists():
        verify_cached(path, row)
        return dict(
            path=str(path),
            sha256=digest(path),
            bytes=path.stat().st_size,
            reused=True,
            download_seconds=0.0,
            resumed_bytes=0,
        )
    if storage_bytes((cache, out)) + row["size"] > working_limit:
        raise ValueError("WORKING_STORAGE_CAP")
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(".parquet.part")
    offset = partial.stat().st_size if partial.exists() else 0
    if offset > row["size"] or http.bytes_received + row["size"] - offset > http.limit:
        raise ValueError("DOWNLOAD_CAP_BEFORE_FILE")
    started = time.monotonic()
    if offset < row["size"]:
        # The file is small enough for this bounded transfer buffer (<102MB), but written
        # exactly once; Arrow audit later projects only the nine source columns.
        body = http.get(
            f"https://huggingface.co/datasets/{DATASET}/resolve/{revision}/{row['path']}",
            row["size"] - offset,
            (offset, row["size"] - 1) if offset else None,
        )
        with partial.open("ab" if offset else "xb") as stream:
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
    verify_cached(partial, row)
    os.link(partial, path)
    partial.unlink()
    return dict(
        path=str(path),
        sha256=digest(path),
        bytes=path.stat().st_size,
        reused=False,
        download_seconds=time.monotonic() - started,
        resumed_bytes=offset,
    )


def publish_cache_manifest(cache: Path, meta: dict, local: list[dict]) -> dict:
    value = dict(
        dataset=DATASET,
        revision=meta["revision"],
        files=local,
        remote_files=meta["files"],
        retrieved_at=now(),
        purpose="LOCAL_EXPLORATORY_ONLY",
        rights="UNRESOLVED; no redistribution or model authority",
    )
    path = cache / meta["revision"] / "acquisition_manifest.json"
    if not path.exists():
        write_json(path, value)
        atomic_new(path.parent / "dataset_card.md", meta["card"].encode())
    return value
