"""Offline P0.2 contract inspection: metadata and synthetic evidence only.

No source rows, environment secrets, network, fitting, or confirmation metrics are
read. A matched pointer proves document identity, not provider facts or approvals.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .config import digest, now, write_json
from .ledger import (
    STATUSES,
    append_event,
    current_blockers,
    guard_operation,
    pair_budget,
    parse_json,
    read_ledger,
    relative_path,
    safe_payload,
)

AUTHORITY = (
    ("Shared_Project_Specification.md", "1.0"),
    ("Track_A_Architecture_Experiment_Roadmap_First_Pass_FROZEN_v1.0.md", "1.0"),
    ("Track_A_Consolidated_Implementation_Design_Record_v1.2_2026-10-10.md", "1.2"),
    ("Track_A_Stage_Gated_Audit_and_Failure_Traceability_Plan_v1.1_2026-10-10.md", "1.1"),
    ("Track_A_Codex_Incremental_Implementation_and_Human_Review_Plan_v1_2026-10-10.md", "1"),
)
POINTER = "configs/CURRENT_PROTOCOL.json"
LEDGER = "reports/audit/track_a_events.jsonl"
VOLATILE = frozenset(
    {
        "created_at",
        "time_utc",
        "timestamp_utc",
        "recorded_at",
        "machine_path",
        "executable",
        "git",
        "environment",
    }
)
CHECK_FIELDS = frozenset(
    {
        "schema_version",
        "gate_id",
        "check_id",
        "audit_run_id",
        "time_utc",
        "protocol_version",
        "protocol_hash",
        "code_id",
        "config_id",
        "source_ids",
        "status",
        "evidence",
        "approved_threshold",
        "example_ids",
        "affected_branches",
        "owner_action",
        "rerun_scope",
        "explanation",
    }
)


def stable_fingerprint(value: dict) -> str:
    """Hash substantive portable configuration, excluding attribution and secret fields.

    Data dates/cutoffs remain substantive; only explicit metadata timestamps are
    excluded. Internal underscore paths are attribution, not configured inputs.
    """

    def clean(item):
        if isinstance(item, dict):
            return {
                k: clean(v)
                for k, v in item.items()
                if k not in VOLATILE
                and not k.startswith("_")
                and not any(
                    part in k.lower() for part in ("secret", "password", "token", "api_key")
                )
            }
        if isinstance(item, list):
            return [clean(v) for v in item]
        return item

    portable = clean(value)
    safe_payload(portable)
    canonical = json.dumps(portable, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


def protocol_identity(pointer: dict) -> str:
    """Document/data-reference identity excludes mutable runtime/Git attribution."""
    return stable_fingerprint(
        {
            key: pointer[key]
            for key in (
                "schema_version",
                "project",
                "track",
                "documents",
                "data_refs",
                "source_ids",
            )
        }
    )


def protocol_check(root: Path, pointer: dict) -> dict:
    """Resolve exactly five pinned files; never auto-select a replacement version."""
    issues = []
    expected = [("docs/track_a/" + name, label) for name, label in AUTHORITY]
    documents = pointer.get("documents", [])
    if (
        pointer.get("schema_version") != 1
        or pointer.get("track") != "A"
        or [(d.get("path"), d.get("version")) for d in documents] != expected
    ):
        issues.append("authority/schema set mismatch")
    for reference in documents + pointer.get("data_refs", []):
        try:
            path = relative_path(root, reference["path"])
            if not path.is_file() or digest(path) != reference["sha256"]:
                issues.append("missing/mismatched: " + reference["path"])
        except (ValueError, KeyError, TypeError):
            issues.append("invalid evidence reference")
    try:
        if protocol_identity(pointer) != pointer.get("protocol_hash"):
            issues.append("pointer identity mismatch")
    except (ValueError, KeyError, TypeError):
        issues.append("invalid pointer identity")
    return {
        "status": "BLOCKED" if issues else "PASS",
        "issues": issues,
        "meaning": "Pinned document/reference identity only; no scientific or human approval",
    }


def git_metadata(root: Path) -> dict:
    """Read local Git attribution without network or diff/secret contents."""

    def git(*args):
        try:
            return subprocess.run(
                ["git", *args], cwd=root, check=True, capture_output=True, text=True
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return "unknown"

    return {
        "commit": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"),
        "dirty": bool(git("status", "--porcelain")),
        "tracked_diff": bool(git("diff", "--stat", "HEAD")),
    }


def code_identity(root: Path) -> str:
    """Hash source/tests/setup/config contents, including uncommitted implementation."""
    paths = [p for folder in ("src", "tests") for p in (root / folder).rglob("*.py")]
    paths += [root / "pyproject.toml", root / "configs/track_a_data.json"]
    return stable_fingerprint({p.relative_to(root).as_posix(): digest(p) for p in sorted(paths)})


def environment_snapshot(root: Path) -> dict:
    """Installed versions are attribution, not a cross-platform lock or clean clone test."""
    packages = {}
    for name in (
        "lstm-market-data",
        "numpy",
        "pandas",
        "pyarrow",
        "exchange-calendars",
        "requests",
        "python-dotenv",
        "pytest",
        "ruff",
        "setuptools",
        "pip",
    ):
        try:
            packages[name] = version(name)
        except PackageNotFoundError:
            packages[name] = None
    return {
        "schema_version": 1,
        "time_utc": now(),
        "os": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "python": platform.python_version(),
        "packages": packages,
        "dependency_spec": {"path": "pyproject.toml", "sha256": digest(root / "pyproject.toml")},
        "commands": [
            ".venv/bin/python -m pytest -q",
            ".venv/bin/ruff check src tests",
            ".venv/bin/lstm-data evidence",
        ],
        "limitations": (
            "Version ranges plus local snapshot; no exact portable lock or clean-machine rehearsal"
        ),
    }


def validate_check(check: dict) -> None:
    """One consistent schema for infrastructure and non-PASS scientific evidence."""
    if set(check) != CHECK_FIELDS or check["schema_version"] != 1:
        raise ValueError("Invalid audit check schema")
    if check["status"] not in STATUSES or check["gate_id"] not in {f"G{i}" for i in range(10)}:
        raise ValueError("Invalid check status/gate")
    for field in ("check_id", "audit_run_id", "time_utc", "protocol_hash", "explanation"):
        if not isinstance(check[field], str) or not check[field]:
            raise ValueError("Missing check identifier/explanation")
    if not isinstance(check["evidence"], dict):
        raise ValueError("Check evidence must be a mapping")
    try:
        stamp = datetime.fromisoformat(check["time_utc"].replace("Z", "+00:00"))
        if stamp.tzinfo is None or stamp.utcoffset() != timezone.utc.utcoffset(stamp):
            raise ValueError
    except (ValueError, TypeError, AttributeError):
        raise ValueError("Check timestamp must be explicit UTC") from None
    for field in ("example_ids", "affected_branches"):
        if not isinstance(check[field], list) or any(not isinstance(v, str) for v in check[field]):
            raise ValueError("Invalid check list")
    for field in ("code_id", "config_id", "source_ids", "approved_threshold"):
        expected = str if field in {"code_id", "config_id"} else dict
        if check[field] is not None and not isinstance(check[field], expected):
            raise ValueError("Invalid nullable check metadata")
    safe_payload(check)


def make_check(
    context: dict,
    check_id: str,
    status: str,
    evidence: dict,
    *,
    gate: str = "G0",
    branches: list[str] | None = None,
    threshold=None,
    explanation: str,
    action: str = "Human review",
    rerun: str = "Affected code/protocol changes",
) -> dict:
    """Construct and validate small audit evidence; thresholds are never invented."""
    check = {
        **context,
        "schema_version": 1,
        "gate_id": gate,
        "check_id": check_id,
        "status": status,
        "evidence": evidence,
        "approved_threshold": threshold,
        "example_ids": ["synthetic-F01"] if check_id == "F01-D2" else [],
        "affected_branches": branches or [],
        "owner_action": action,
        "rerun_scope": rerun,
        "explanation": explanation,
    }
    validate_check(check)
    return check


def f01_fixture() -> dict:
    """Live regression of historical F01; fake clocks do not verify any source."""
    import pandas as pd

    from .alignment import asof_diagnostic

    base = {"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1}
    stocks = pd.DataFrame(
        [{**base, "symbol": "FAKE", "volume": 1, "timestamp": "2001-01-02T14:00:00Z"}]
    )
    market = pd.DataFrame([{
        **base, "timestamp": "2001-01-02T13:00:00Z",
        "period_end": "2001-01-02T13:00:00Z",
        "available_at": "2001-01-02T14:00:00Z", "timing_basis": "synthetic",
    }])
    joined, _ = asof_diagnostic(
        stocks, market, index_delay_minutes=60, stock_delay_minutes=60, max_age_minutes=90
    )
    row = joined.iloc[0]
    return {
        "synthetic_only": True,
        "hypothetical_delay_minutes": 60,
        "decision_time": row.decision_time.isoformat(),
        "decision_cutoff": row.decision_cutoff.isoformat(),
        "source_timestamp_label": row.index_timestamp.isoformat(),
        "market_period_end": row.period_end.isoformat(),
        "available_at": row.available_at.isoformat(),
        "timing_basis": row.timing_basis,
        "observed_available_age_minutes": float(row.availability_age_minutes),
        "period_end_age_minutes": float(row.period_end_age_minutes),
        "required_period_end_age_minutes": 120.0,
        "observed_usable": bool(row.usable_candidate),
        "required_usable": False,
        "status": "PASS" if not bool(row.usable_candidate)
        and row.reason == "STALE_PERIOD_END" and row.period_end_age_minutes == 120
        else "INVALID",
        "reason": row.reason,
        "research_ready": False,
        "meaning": "F01_REPAIRED_IN_CODE regression only; HISTORICAL_SOURCE_CLOCK_UNVERIFIED",
    }


def inspect(
    root: Path, pointer_name: str = POINTER, ledger_name: str = LEDGER, *, diagnose: bool = False
) -> dict:
    """Read metadata and optionally fake records. Never write or open market sources."""
    pointer = parse_json(relative_path(root, pointer_name).read_text())
    checked = protocol_check(root, pointer)
    events = read_ledger(relative_path(root, ledger_name))
    protocol_hash = pointer.get("protocol_hash", "unknown")
    if any(e["protocol_hash"] != protocol_hash for e in events):
        checked = {"status": "BLOCKED", "issues": ["Ledger/protocol identity mismatch"]}
    context = {
        "audit_run_id": "p0.2-" + now(),
        "time_utc": now(),
        "protocol_version": "Track A pinned five-document contract",
        "protocol_hash": protocol_hash,
        "code_id": code_identity(root),
        "config_id": stable_fingerprint(
            json.loads((root / "configs/track_a_data.json").read_text())
        ),
        "source_ids": pointer.get("source_ids"),
    }
    checks = [
        make_check(
            context,
            "protocol-identity",
            checked["status"],
            checked,
            explanation="Hashes do not establish provider truth or sign-off",
        )
    ]
    ledger_present = bool(events)
    checks.append(
        make_check(
            context,
            "ledger-schema",
            "PASS" if ledger_present else "BLOCKED",
            {"events": len(events)},
            explanation="Valid append-only event history; not an approval",
        )
    )
    for event in current_blockers(events):
        checks.append(
            make_check(
                context,
                event["event_id"],
                event["status"],
                event["evidence"],
                gate=event["gate_id"],
                branches=event["affected_branches"],
                explanation=event["rationale"],
                action=event["owner_action"],
            )
        )
    if diagnose:
        fixture = f01_fixture()
        checks.append(
            make_check(
                context,
                "F01-D2",
                fixture["status"],
                fixture,
                gate="G2",
                branches=["market_features"],
                threshold={"max_period_age_minutes": 90, "authority": AUTHORITY[2][0] + " D2"},
                explanation="Corrected code rejects stale fake period; source gates remain blocked",
                action="Review F01 repair; historical publication validation still required",
            )
        )
    operations = {
        name: guard_operation(name, events)
        for name in (
            "stock_administration",
            "market_features",
            "economic_evaluation",
            "confirmation_evaluation",
        )
    }
    if checked["status"] != "PASS":
        for operation in operations.values():
            operation["status"] = "BLOCKED"
            operation["reasons"].append("protocol identity unresolved")
    return {
        "schema_version": 1,
        "package": "P0.2",
        "offline": True,
        "writes": False,
        "infrastructure_status": checked["status"] if ledger_present else "BLOCKED",
        "invocation": {
            "entrypoint": "lstm-data evidence",
            "mode": "diagnose" if diagnose else "inspect",
            "pointer": pointer_name,
            "ledger": ledger_name,
        },
        "run_fingerprint": stable_fingerprint(
            {
                "code_id": context["code_id"],
                "config_id": context["config_id"],
                "protocol_hash": protocol_hash,
                "diagnose": diagnose,
                "entrypoint": "lstm-data evidence",
            }
        ),
        "research_status": "BLOCKED",
        "gates": {
            **{f"G{i}": "BLOCKED" for i in range(3)},
            **{f"G{i}": "NOT_RUN" for i in range(3, 10)},
        },
        "checks": checks,
        "blockers": current_blockers(events),
        "operations": operations,
        "pair_budget": pair_budget(events),
        "git": git_metadata(root),
    }


def add_parser(subparsers) -> None:
    """Extend the existing CLI; inspect is read-only and independent of credentials."""
    parser = subparsers.add_parser("evidence", help="Offline P0.2 evidence; no research executors")
    parser.add_argument("--mode", choices=("inspect", "diagnose", "append"), default="inspect")
    parser.add_argument("--root", type=Path, default=Path("."), help="Project root")
    parser.add_argument("--pointer", default=POINTER)
    parser.add_argument("--ledger", default=LEDGER)
    parser.add_argument("--event", help="Project-relative event JSON; append mode only")
    parser.add_argument("--output", help="Explicit new small JSON report under reports/")
    parser.add_argument("--dry-run", action="store_true", help="Forbid all writes")


def run_cli(args: argparse.Namespace) -> int:
    """Explicit append/output only; diagnostic scientific failures return exit code two."""
    try:
        if args.env_file:
            raise ValueError("Evidence command does not load environment files")
        root = args.root.resolve()
        if args.mode == "append":
            if args.dry_run or not args.event:
                raise ValueError("Append requires explicit event and no dry-run")
            pointer = parse_json(relative_path(root, args.pointer).read_text())
            if protocol_check(root, pointer)["status"] != "PASS":
                raise ValueError("Append blocked by protocol identity mismatch")
            event = parse_json(relative_path(root, args.event).read_text())
            if event.get("protocol_hash") != pointer["protocol_hash"]:
                raise ValueError("Event/protocol identity mismatch")
            append_event(relative_path(root, args.ledger), event, root=root)
        elif args.event:
            raise ValueError("Event input is only accepted in explicit append mode")
        report = inspect(root, args.pointer, args.ledger, diagnose=args.mode == "diagnose")
        report["invocation"]["mode"] = args.mode
        report["writes"] = args.mode == "append" or bool(args.output)
        if args.output:
            if args.dry_run:
                raise ValueError("Dry-run forbids output writes")
            output = relative_path(root, args.output)
            if not output.is_relative_to(root / "reports"):
                raise ValueError("Small reports must stay under reports/")
            write_json(output, report)
        print(json.dumps(report, indent=2))
        return 2 if args.mode == "diagnose" or report["infrastructure_status"] != "PASS" else 0
    except (ValueError, OSError, KeyError, TypeError):
        # Never echo malformed user payloads or paths into logs.
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "reason": "Invalid, missing, mismatched, or unsafe evidence input",
                }
            )
        )
        return 2
