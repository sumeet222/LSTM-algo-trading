"""Durable append-before-send transport and immutable new remediation chunks."""

from __future__ import annotations

import hashlib
import io
import json
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import requests

from .alpaca import ENDPOINT, DataAccessError
from .config import atomic_new, digest, fingerprint, now, write_json
from .store import chunk_paths
from .validation import normalize, require_valid


@dataclass
class RemediationTransport:
    """A separate NEW-task budget; never touches existing source or SPY journals."""

    journal: Path
    allowed_requests: tuple[dict, ...]
    get: Callable = requests.get
    ceiling: int = 180
    expected_sha: str | None = field(default=None, repr=False)
    before_append: Callable[[int], None] | None = field(default=None, repr=False)

    def records(self) -> list[dict]:
        raw = self.journal.read_bytes() if self.journal.exists() else b""
        if raw and not raw.endswith(b"\n"):
            raise DataAccessError("REMEDIATION_TRUNCATED_JOURNAL_REVIEW_REQUIRED")
        return [json.loads(line) for line in raw.splitlines()]

    @property
    def used(self) -> int:
        return sum(r["kind"] == "ATTEMPT" for r in self.records())

    def append(self, item: dict) -> None:
        self.journal.parent.mkdir(parents=True, exist_ok=True)
        actual = digest(self.journal) if self.journal.exists() else None
        if actual != self.expected_sha:
            raise DataAccessError("REMEDIATION_CONCURRENT_JOURNAL_CHANGE")
        payload = (json.dumps(item, sort_keys=True) + "\n").encode()
        if self.before_append:
            self.before_append(len(payload))
        with self.journal.open("ab") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        self.expected_sha = digest(self.journal)

    def request(
        self,
        url: str,
        *,
        params: dict,
        headers: dict,
        timeout: float,
        allow_redirects: bool = False,
    ) -> requests.Response:
        base = {k: v for k, v in params.items() if k != "page_token"}
        page_id = fingerprint(params)
        records = self.records()
        if (
            url != ENDPOINT
            or base not in self.allowed_requests
            or allow_redirects
            or self.ceiling != 180
        ):
            raise DataAccessError("REMEDIATION_UNAUTHORIZED_REQUEST")
        if any(r.get("status") in (401, 403, 429) for r in records):
            raise DataAccessError("REMEDIATION_ACCESS_OR_RATE_LIMIT_HOLD")
        if self.used >= self.ceiling:
            raise DataAccessError("REMEDIATION_ATTEMPT_BUDGET_EXHAUSTED")
        if sum(r["kind"] == "ATTEMPT" and r["page_hash"] == page_id for r in records) >= 3:
            raise DataAccessError("REMEDIATION_PAGE_LIFETIME_LIMIT")
        attempt_id = self.used + 1
        self.append(
            {
                "kind": "ATTEMPT",
                "provider": "ALPACA",
                "attempt_id": attempt_id,
                "page_hash": page_id,
                "request_hash": fingerprint(base),
                "params": base,
                "continued_page": "page_token" in params,
                "endpoint": ENDPOINT,
                "time_utc": now(),
            }
        )
        try:
            response = self.get(
                url, params=params, headers=headers, timeout=timeout, allow_redirects=False
            )
        except requests.RequestException:
            self.append(
                {
                    "kind": "RESULT",
                    "attempt_id": attempt_id,
                    "status": "TRANSPORT_ERROR",
                    "time_utc": now(),
                }
            )
            raise requests.ConnectionError("REMEDIATION_TRANSPORT_ERROR") from None
        status = response.status_code
        receipt = {
            "kind": "RESULT",
            "attempt_id": attempt_id,
            "status": status,
            "bytes": len(response.content),
            "response_sha256": hashlib.sha256(response.content).hexdigest(),
            "time_utc": now(),
            "request_hash": fingerprint(base),
        }
        if status == 200:
            try:
                payload = response.json()
                if isinstance(payload, dict) and isinstance(payload.get("bars"), dict):
                    receipt["returned_rows"] = sum(
                        len(v) for v in payload["bars"].values() if isinstance(v, list)
                    )
                    receipt["terminal_page"] = not bool(payload.get("next_page_token"))
            except ValueError:
                receipt["schema"] = "INVALID_JSON"
        self.append(receipt)
        if status in (401, 403, 429):
            raise DataAccessError(f"REMEDIATION_HTTP_{status}_HOLD_NO_RETRY_CASCADE")
        return response


@dataclass
class StorageLimit:
    """Count new archive plus task evidence; no duplicate original/full-panel store."""

    roots: tuple[Path, ...]
    maximum: int = 256 * 1024 * 1024

    @property
    def used(self) -> int:
        return sum(
            f.stat().st_size
            for root in self.roots
            if root.exists()
            for f in root.rglob("*")
            if f.is_file()
        )

    def reserve(self, size: int) -> None:
        if size < 0 or self.used + size > self.maximum:
            raise DataAccessError("REMEDIATION_STORAGE_LIMIT")


def publish_chunk(
    store: Path,
    frame: pd.DataFrame,
    params: dict,
    receipts: list[dict],
    *,
    kind: str,
    limit: StorageLimit,
) -> dict:
    """Publish true native rows (including an honestly empty result) atomically once."""
    data, manifest = chunk_paths(store, params)
    if data.exists() or manifest.exists():
        raise FileExistsError("REMEDIATION_EXISTING_OR_INTERRUPTED_CHUNK")
    frame = normalize(frame, stocks=True)
    require_valid(frame, stocks=True)
    if set(frame.symbol) - set(params["symbols"].split(",")):
        raise ValueError("REMEDIATION_UNREQUESTED_SYMBOL")
    selected = frame.copy()
    selected["provenance_id"] = fingerprint(params)
    buffer = io.BytesIO()
    selected.to_parquet(buffer, index=False, compression="zstd")
    payload = buffer.getvalue()
    value = {
        "schema_version": 1,
        "provider": "ALPACA",
        "kind": kind,
        "source_version": "ALPACA_SIP_SPLIT_REMED_NATIVE_V1",
        "params": params,
        "retrieved_at": now(),
        "rows": len(selected),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "size_bytes": len(payload),
        "missing_requested_symbols": sorted(set(params["symbols"].split(",")) - set(frame.symbol)),
        "availability_basis": "UNKNOWN",
        "available_at": None,
        "action_vintage": "UNVERIFIED",
        "terminal_page_verified": True,
        "scientific_activation": False,
        "receipts": receipts,
    }
    limit.reserve(len(payload) + len(json.dumps(value, sort_keys=True).encode()) + 1024)
    atomic_new(data, payload)
    write_json(manifest, value)
    return value


def read_chunk(store: Path, params: dict) -> tuple[pd.DataFrame, dict] | None:
    """A missing pair is not completion; an orphan/corrupt pair stops rather than overwrites."""
    data, manifest = chunk_paths(store, params)
    if not data.exists() and not manifest.exists():
        return None
    if not data.exists() or not manifest.exists():
        raise ValueError("REMEDIATION_INTERRUPTED_PAIR_REVIEW_REQUIRED")
    value = json.loads(manifest.read_text())
    if (
        value["params"] != params
        or value["sha256"] != digest(data)
        or value["source_version"] != "ALPACA_SIP_SPLIT_REMED_NATIVE_V1"
        or not value["terminal_page_verified"]
    ):
        raise ValueError("REMEDIATION_CHECKSUM_OR_SOURCE_VERSION_MISMATCH")
    frame = normalize(pd.read_parquet(data), stocks=True)
    require_valid(frame, stocks=True)
    if len(frame) != value["rows"] or set(frame.symbol) - set(params["symbols"].split(",")):
        raise ValueError("REMEDIATION_CHUNK_ROWS_MISMATCH")
    if (
        (frame.timestamp < pd.Timestamp(params["start"]))
        | (frame.timestamp > pd.Timestamp(params["end"]))
    ).any():
        raise ValueError("REMEDIATION_CHUNK_BOUNDS_MISMATCH")
    for column, expected in (
        ("feed", "sip"),
        ("adjustment", "split"),
        ("source_timeframe", params["timeframe"]),
        ("provenance_id", fingerprint(params)),
    ):
        if column not in frame or not (frame[column] == expected).all():
            raise ValueError("REMEDIATION_CHUNK_METADATA_MISMATCH")
    return frame, value
