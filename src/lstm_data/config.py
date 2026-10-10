"""Strict, portable configuration and immutable output helpers."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def digest(path: Path) -> str:
    """Hash source bytes without changing them."""
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def fingerprint(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_config(path: Path) -> dict:
    """Resolve configured paths relative to the config's project directory."""
    path = path.resolve()
    cfg = json.loads(path.read_text())
    if cfg["schema_version"] != 1 or cfg["feed"] != "sip":
        raise ValueError("Only schema 1 / explicit SIP is supported; no IEX fallback")
    if cfg["timeframe"] not in {"1Hour", "30Min"}:
        raise ValueError("Resolution must be reviewed native 1Hour or approved 30Min source")
    if cfg["adjustment"] not in {"raw", "split", "dividend", "all", "split,spin-off"}:
        raise ValueError("An explicit documented adjustment is required")
    start = datetime.strptime(cfg["start_date"], "%Y-%m-%d")
    end = datetime.strptime(cfg["end_date"], "%Y-%m-%d")
    if start > end or not cfg["symbols"] or len(set(cfg["symbols"])) != len(cfg["symbols"]):
        raise ValueError("Invalid dates or duplicate/empty universe")
    if cfg["calendar"] != "XNYS" or cfg["timezone"] != "America/New_York":
        raise ValueError("Track A requires XNYS / America/New_York")
    if cfg["chunk_months"] != 1 or not 1 <= cfg["page_limit"] <= 10000:
        raise ValueError("Use monthly chunks and page limit 1..10000")
    retry = cfg["retry"]
    if not 1 <= retry["max_attempts"] <= 10 or retry["requests_per_minute"] <= 0:
        raise ValueError("Invalid bounded retry/rate policy")
    for name in ("base_seconds", "max_seconds", "jitter_seconds", "timeout_seconds"):
        if retry[name] < 0 or (name == "timeout_seconds" and retry[name] == 0):
            raise ValueError(f"Invalid retry {name}")
    if cfg["max_pages_per_request"] < 1:
        raise ValueError("max_pages_per_request must be positive")
    cfg["_fingerprint"] = fingerprint(cfg)
    cfg["_root"] = path.parent.parent
    for key in ("course_source", "stock_store", "report_dir"):
        relative = Path(cfg[key])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"{key} must be a project-relative path without '..'")
        cfg[f"_{key}"] = cfg["_root"] / relative
    return cfg


def public_config(cfg: dict) -> dict:
    return {key: value for key, value in cfg.items() if not key.startswith("_")}


def atomic_new(path: Path, data: bytes) -> None:
    """Publish a complete new file, refusing to replace any existing output."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".pending-")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        # Hard link is an atomic create-if-absent on supported local filesystems.
        os.link(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def write_json(path: Path, value: Any) -> None:
    atomic_new(path, (json.dumps(value, indent=2, sort_keys=True) + "\n").encode())
