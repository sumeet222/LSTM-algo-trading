"""Additive P2/P3 hold verification; never grants an empirical permission."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .config import digest
from .p3_domain import MODE, Permission

P3_API = Path("reports/data_audit/ta_p3_engineering_2026-10-11_230724/api_handoff.json")


def verify(permission: Permission) -> dict:
    p2_sha = permission.ensure()
    api = json.loads(P3_API.read_text())
    ref = api["new_register"]
    path = Path(ref["path"])
    if path.is_absolute() or ".." in path.parts or digest(path) != ref["sha256"]:
        raise ValueError("P3_V1_REGISTER_SHA_REQUIRED")
    registry = json.loads(path.read_text())
    entries = registry["entries"]
    if (
        len(entries) != 26
        or len({e["id"] for e in entries}) != 26
        or any(e["scientific_status"] != "HOLD" or e["NO_AUTO_CLEAR"] is not True for e in entries)
    ):
        raise ValueError("P3_SCIENTIFIC_HOLDS_MUST_REMAIN")
    return {"P2_handoff_sha": p2_sha, "P3_v1_sha": ref["sha256"], "scientific_status": "HOLD"}


@dataclass(frozen=True)
class _ReplayGuard(Permission):
    """Private one-account lease after full SHA verification, invalidated on file change.

    Every mutation retains a stat/ctime/inode guard. Full P2/P3 SHA verification
    happens before and after each replay activation; no empirical mode can lease.
    """

    snapshots: tuple[tuple[str, int, int, int, int], ...] = ()
    p2_sha: str = ""

    def ensure(self) -> str:
        if self.mode != MODE or not self.snapshots or not self.p2_sha:
            raise ValueError("SYNTHETIC_VERIFIED_REPLAY_LEASE_REQUIRED")
        for name, size, mtime, ctime, inode in self.snapshots:
            stat = Path(name).stat()
            if (stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns, stat.st_ino) != (
                size,
                mtime,
                ctime,
                inode,
            ):
                raise ValueError("AUTHORITY_CHANGED_DURING_SYNTHETIC_REPLAY")
        return self.p2_sha


def replay_permission(permission: Permission) -> Permission:
    proof = verify(permission)
    config = json.loads(permission.handoff.read_text())
    api = json.loads(P3_API.read_text())
    paths = (
        permission.handoff,
        Path(config["register"]["path"]),
        Path(config["readable_register"]["path"]),
        P3_API,
        Path(api["new_register"]["path"]),
        Path("docs/track_a/P3_DEFERRED_WORK_REGISTER_v1.md"),
        Path("configs/CURRENT_PROTOCOL.json"),
        Path("reports/audit/track_a_events.jsonl"),
    )
    rows = []
    for path in paths:
        stat = path.stat()
        rows.append(
            (path.as_posix(), stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns, stat.st_ino)
        )
    return _ReplayGuard(permission.mode, permission.handoff, tuple(rows), proof["P2_handoff_sha"])
