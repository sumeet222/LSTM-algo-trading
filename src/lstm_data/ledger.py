"""Small local evidence ledger. No fitting, approval inference, or data executors.

Publication replaces a file atomically with its exact old byte prefix plus one row.
An exclusive sidecar lock protects cooperating single-machine writers; a stale
lock fails closed and requires human inspection. This is not OS access control.
"""

from __future__ import annotations

import json
import math
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath

STATUSES = frozenset(
    {"PASS", "WARN", "BLOCKED", "INVALID", "INCONCLUSIVE", "INACTIVE_CONDITIONAL", "NOT_RUN"}
)
KINDS = frozenset({"audit", "decision", "approval", "blocker", "experiment"})
REQUIRED = frozenset(
    {
        "schema_version",
        "event_id",
        "time_utc",
        "track",
        "protocol_hash",
        "gate_id",
        "package",
        "kind",
        "status",
        "code_id",
        "config_id",
        "source_ids",
        "affected_branches",
        "artifact_refs",
        "evidence",
        "rationale",
        "owner_action",
        "blocks",
        "supersedes",
    }
)
OPTIONAL = frozenset({"decision_ref", "run_id", "seed", "fitting_cutoff", "attempt_id"})
GATES = frozenset(f"G{i}" for i in range(10))
PAIR_CEILING = 40
MAX_LEDGER_BYTES = 2_000_000
OPERATIONS = {
    "stock_administration": set(),
    "stock_features": {"stock_timing", "formation", "shared_clock"},
    "market_features": {"stock_timing", "formation", "shared_clock", "market_timing", "F01"},
    "predictive_evaluation": {"stock_timing", "formation", "shared_clock"},
    "economic_evaluation": {
        "stock_timing",
        "formation",
        "shared_clock",
        "minute_execution",
        "corporate_actions",
        "portfolio_accounting",
    },
    "training": {"stock_timing", "formation", "shared_clock"},
    "confirmation_evaluation": {"confirmation_lock"},
}


def safe_payload(value: object) -> None:
    """Reject credential fields/URLs and absolute paths without echoing their values."""
    if isinstance(value, dict):
        for key, item in value.items():
            if re.search(r"secret|password|token|api_key|credential", str(key), re.I):
                raise ValueError("Credential-bearing fields are forbidden")
            safe_payload(item)
    elif isinstance(value, list):
        for item in value:
            safe_payload(item)
    elif isinstance(value, str):
        if Path(value).is_absolute() or PureWindowsPath(value).is_absolute():
            raise ValueError("Absolute paths are forbidden in portable evidence")
        if re.search(
            r"https?://[^/\s]+@|(?:api[_ -]?key|secret|password|token)\s*[=:]", value, re.I
        ):
            raise ValueError("Credential-like values are forbidden")
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Non-finite evidence numbers are forbidden")


def parse_json(raw: str | bytes) -> dict:
    """Reject duplicate JSON fields instead of silently using the last value."""

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON field")
            result[key] = value
        return result

    return json.loads(raw, object_pairs_hook=unique)


def relative_path(root: Path, name: str) -> Path:
    """Resolve a project-relative evidence path, excluding raw data and .env files."""
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or PureWindowsPath(name).is_absolute():
        raise ValueError("Expected project-relative evidence path")
    target = (root / path).resolve()
    if not target.is_relative_to(root.resolve()) or ".env" in path.name:
        raise ValueError("Unsafe evidence path")
    resolved = target.relative_to(root.resolve())
    if path.parts[:2] == ("data", "raw") or resolved.parts[:2] == ("data", "raw"):
        raise ValueError("Evidence runner never opens raw source data")
    if ".env" in resolved.name:
        raise ValueError("Environment files are not evidence inputs")
    return target


def validate_event(event: dict) -> None:
    """Validate the version-one contract; nullable identifiers never imply approval."""
    if (
        not isinstance(event, dict)
        or not REQUIRED <= event.keys()
        or event.keys() - REQUIRED - OPTIONAL
    ):
        raise ValueError("Invalid event schema fields")
    if event["schema_version"] != 1 or event["track"] != "A":
        raise ValueError("Unsupported event schema/track")
    if (
        event["status"] not in STATUSES
        or event["kind"] not in KINDS
        or event["gate_id"] not in GATES
    ):
        raise ValueError("Invalid status, kind, or gate")
    for field in ("event_id", "package", "rationale", "owner_action", "protocol_hash"):
        if not isinstance(event[field], str) or not event[field].strip():
            raise ValueError("Required event text missing")
    if not re.fullmatch(r"[a-zA-Z0-9_.:-]{1,120}", event["event_id"]):
        raise ValueError("Invalid event identifier")
    if not re.fullmatch(r"[0-9a-f]{64}", event["protocol_hash"]):
        raise ValueError("Invalid protocol hash")
    try:
        stamp = datetime.fromisoformat(event["time_utc"].replace("Z", "+00:00"))
        if stamp.tzinfo is None or stamp.utcoffset() != timezone.utc.utcoffset(stamp):
            raise ValueError
    except (ValueError, TypeError, AttributeError):
        raise ValueError("Event timestamp must be explicit UTC") from None
    for field in ("affected_branches", "artifact_refs", "blocks", "supersedes"):
        if not isinstance(event[field], list) or any(
            not isinstance(x, str) or not x for x in event[field]
        ):
            raise ValueError("Invalid event list")
    for field in ("code_id", "config_id"):
        if event[field] is not None and not isinstance(event[field], str):
            raise ValueError("Invalid nullable identifier")
    if event["source_ids"] is not None and not isinstance(event["source_ids"], dict):
        raise ValueError("Source identifiers must be a mapping or null")
    if not isinstance(event["evidence"], dict) or not event["evidence"]:
        raise ValueError("Evidence reference required")
    if event["kind"] == "approval" and not isinstance(event.get("decision_ref"), dict):
        raise ValueError("Approval requires a real human decision reference")
    if event["kind"] == "experiment" and event["status"] not in {"NOT_RUN", "INACTIVE_CONDITIONAL"}:
        raise ValueError("P0.2 cannot register genuine fitting results")
    if event.get("attempt_id") is not None:
        raise ValueError("P0.2 cannot register genuine fitting attempts")
    safe_payload(event)


def decode_ledger(raw: bytes) -> list[dict]:
    """Fail closed on malformed/truncated history rather than repairing or dropping rows."""
    if len(raw) > MAX_LEDGER_BYTES or (raw and not raw.endswith(b"\n")):
        raise ValueError("Ledger too large or truncated; preserve and inspect")
    events, ids = [], set()
    try:
        for row in raw.splitlines():
            event = parse_json(row)
            validate_event(event)
            if event["event_id"] in ids or not set(event["supersedes"]) <= ids:
                raise ValueError("Duplicate event or unknown correction target")
            if event["event_id"] in event["supersedes"]:
                raise ValueError("Self-superseding event")
            if events and event["protocol_hash"] != events[0]["protocol_hash"]:
                raise ValueError("Mixed protocol identity in ledger")
            previous_blocks = {
                dep
                for previous in events
                if previous["event_id"] in event["supersedes"]
                for dep in previous["blocks"]
            }
            if previous_blocks and (
                event["status"] == "PASS" or not previous_blocks <= set(event["blocks"])
            ):
                raise ValueError("P0.2 cannot resolve or narrow scientific blockers")
            ids.add(event["event_id"])
            events.append(event)
    except (UnicodeError, json.JSONDecodeError, TypeError):
        raise ValueError("Malformed ledger; preserve and inspect") from None
    return events


def read_ledger(path: Path) -> list[dict]:
    """Read only; absence is empty history, never completed prerequisites."""
    return decode_ledger(path.read_bytes()) if path.exists() else []


def current_blockers(events: list[dict]) -> list[dict]:
    """Derive dependency blockers without letting unrelated PASS events clear them."""
    replaced = {item for event in events for item in event["supersedes"]}
    return [
        event
        for event in events
        if event["event_id"] not in replaced and event["blocks"] and event["status"] != "PASS"
    ]


def pair_budget(events: list[dict], candidate_attempt_id: str | None = None) -> dict:
    """Future guard: count all unique attempted pairs across history, including failures.

    Synthetic tests call this pure function. The P0.2 writer forbids actual attempts.
    Superseding or changing a result never subtracts the original attempt.
    """
    attempts = {e["attempt_id"] for e in events if e.get("attempt_id") is not None}
    if any(not isinstance(item, str) or not item for item in attempts):
        raise ValueError("Invalid attempt identifiers")
    if candidate_attempt_id is not None and (
        not isinstance(candidate_attempt_id, str) or not candidate_attempt_id
    ):
        raise ValueError("Invalid candidate attempt identifier")
    prospective = attempts | ({candidate_attempt_id} if candidate_attempt_id else set())
    return {
        "ceiling": PAIR_CEILING,
        "attempted_pairs": len(attempts),
        "prospective_pairs": len(prospective),
        "status": "PASS"
        if len(prospective) <= PAIR_CEILING and candidate_attempt_id not in attempts
        else "BLOCKED",
        "duplicate_candidate": candidate_attempt_id in attempts,
    }


def guard_operation(operation: str, events: list[dict]) -> dict:
    """Only administration is runnable here. No research or confirmation executor exists.

    Dependencies are narrow; missing evidence remains blocked. G9 additionally needs
    a future frozen manifest plus human authorization and a separately reviewed runner.
    """
    if operation not in OPERATIONS:
        raise ValueError("Unknown managed operation")
    required = OPERATIONS[operation]
    blockers = sorted({dep for e in current_blockers(events) for dep in e["blocks"]} & required)
    reasons = ["unresolved:" + dep for dep in blockers]
    if operation != "stock_administration":
        reasons.append("research executor and reviewed human authorization unavailable in P0.2")
    if operation == "confirmation_evaluation":
        reasons.append(
            "G9 immutable manifest lock and human decision required; no metrics accessed"
        )
    return {"operation": operation, "status": "BLOCKED" if reasons else "PASS", "reasons": reasons}


def verify_decision(root: Path, reference: dict) -> None:
    """Require hash-bound human attribution. This local attestation is not authentication."""
    from .config import digest

    if set(reference) != {"path", "sha256", "decision_id"}:
        raise ValueError("Invalid human decision reference")
    path = relative_path(root, reference["path"])
    if not path.is_file() or digest(path) != reference["sha256"]:
        raise ValueError("Human decision absent or mismatched")
    decision = parse_json(path.read_text())
    safe_payload(decision)
    if (
        decision.get("decision_id") != reference["decision_id"]
        or decision.get("actor_type") != "human"
        or not decision.get("owner")
        or not isinstance(decision.get("scope"), list)
        or not decision["scope"]
    ):
        raise ValueError("Human decision attribution/scope missing")


def append_event(path: Path, event: dict, *, root: Path) -> None:
    """Explicit append only, crash-safe before publication; no research-blocker clearance.

    A new correction preserves every historical row and explains its superseded IDs.
    P0.2 may refine blocking evidence but cannot narrow/resolve scientific blockers.
    """
    validate_event(event)
    if not path.resolve().is_relative_to((root / "reports").resolve()):
        raise ValueError("Ledger writes must stay under project reports")
    if event.get("decision_ref") is not None:
        verify_decision(root, event["decision_ref"])
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(path.name + ".lock")
    with lock.open("x"):
        pass
    temporary = None
    try:
        old = path.read_bytes() if path.exists() else b""
        history = decode_ledger(old)
        targets = {e["event_id"]: e for e in history}
        if event["event_id"] in targets or not set(event["supersedes"]) <= targets.keys():
            raise ValueError("Duplicate event or unknown correction target")
        previous_blocks = {d for item in event["supersedes"] for d in targets[item]["blocks"]}
        if previous_blocks and (
            event["status"] == "PASS" or not previous_blocks <= set(event["blocks"])
        ):
            raise ValueError("P0.2 cannot resolve or narrow scientific blockers")
        if history and event["protocol_hash"] != history[-1]["protocol_hash"]:
            raise ValueError("Protocol amendment requires a separately reviewed migration")
        payload = old + json.dumps(event, sort_keys=True, allow_nan=False).encode() + b"\n"
        decode_ledger(payload)
        with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix=".ledger-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        lock.unlink()
