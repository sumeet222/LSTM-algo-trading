"""Package017 authority: exactly two seed123 pairs, linked to the sealed 30-start prefix."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

from .config import atomic_new, digest, fingerprint, now
from .hf20_training_authority import (
    JOURNAL as PREVIOUS_JOURNAL,
)
from .hf20_training_authority import (
    MODULES,
    POINTER,
    reference,
)
from .hf20_training_authority import (
    code_binding as previous_code,
)
from .hf20_training_authority import (
    read_rows as previous_rows,
)
from .pretraining_policy import verify_ref
from .real_batch_authority import TRANSITIONS, atomic_replace_json

IDS = ("HF20-TM0-C0-S123-DEV1", "HF20-TM0-T2-S123-DEV1")
JOURNAL = Path("reports/audit/track_a_real_pairs_v7.jsonl")
SCIENTIFIC_KEYS = (
    "input_contract",
    "source_revision",
    "symbols",
    "feature_id",
    "target_id",
    "clock_id",
    "views",
    "scales",
    "cpu_threads",
    "heldout_access",
)


def code_binding() -> dict:
    """Bind the original numerical code plus the new typed orchestration route."""
    names = (*MODULES, "hf20_replication_authority.py", "hf20_replication_run.py")
    return {n: digest(Path("src/lstm_data") / n) for n in names}


def read_rows(path: Path = JOURNAL) -> list[dict]:
    raw = path.read_bytes() if path.exists() else b""
    if raw and not raw.endswith(b"\n"):
        raise ValueError("P017_TRUNCATED_JOURNAL")
    rows = [json.loads(line) for line in raw.splitlines()]
    states: dict[str, str] = {}
    starts = 0
    for i, r in enumerate(rows):
        name, status = r["run_id"], r["status"]
        if r["sequence"] != i + 1 or r["previous"] != fingerprint(rows[:i]) or name not in IDS:
            raise ValueError("P017_JOURNAL_CHAIN")
        if status == "STARTED":
            if (
                starts >= 2
                or name in states
                or name != IDS[starts]
                or (i and rows[i - 1]["status"] != "COMPLETED")
            ):
                raise ValueError("P017_DUPLICATE_REORDER_RETRY")
            starts += 1
        elif name not in states or status not in TRANSITIONS[states[name]]:
            raise ValueError("P017_INVALID_TRANSITION")
        if r["global_started_pairs"] != 30 + starts or r["effective_ceiling"] != 200:
            raise ValueError("P017_BUDGET_CHAIN")
        states[name] = status
    return rows


def validate_approval(plan_path: Path, receipt: Path | None, *, terminal: bool = False) -> dict:
    if receipt is None:
        raise ValueError("P017_LIVE_APPROVAL_REQUIRED_ZERO_STEPS")
    p, a = json.loads(plan_path.read_text()), json.loads(receipt.read_text())
    if (
        a.get("status") != "APPROVED"
        or a.get("actor_type") != "human"
        or a.get("response_provenance") != "LIVE_USER_RESPONSE_IN_THIS_SESSION"
        or not a.get("response_text")
        or a.get("approved_runs") != list(IDS)
        or a.get("proposal_sha256") != digest(plan_path)
        or a.get("code_sha256") != fingerprint(code_binding())
        or a.get("input_contract") != p["input_contract"]
        or a.get("scope") != p["scope"]
        or a.get("scales") != p["scales"]
    ):
        raise ValueError("P017_EXACT_FRESH_TWO_PAIR_APPROVAL_REQUIRED")
    if not terminal and pd.Timestamp.now(tz="UTC") >= pd.Timestamp(p["fit_deadline"]):
        raise ValueError("P017_EXPIRED_AUTHORITY")
    return p


def ensure(plan_path: Path, receipt: Path | None, run_id: str, *, terminal: bool = False) -> dict:
    p = validate_approval(plan_path, receipt, terminal=terminal)
    if (
        run_id not in IDS
        or p["runs"] != list(IDS)
        or p["scope"]["seed"] != 123
        or p["opening_started"] != 30
        or p["maximum_new_starts"] != 2
        or p["ceiling"] != 200
        or p["code"] != code_binding()
        or p["code_sha256"] != fingerprint(code_binding())
        or p["heldout_access"] is not False
    ):
        raise ValueError("P017_EXACT_SEED_CODE_SCOPE_REQUIRED")
    for ref in p["protected_refs"] + [p["baseline_plan"], p["registry_definition"]]:
        verify_ref(Path.cwd(), ref)
    baseline = json.loads(Path(p["baseline_plan"]["path"]).read_text())
    if baseline["code"] != previous_code() or any(p[k] != baseline[k] for k in SCIENTIFIC_KEYS):
        raise ValueError("P017_SCIENTIFIC_CONTRACT_CHANGED")
    old = previous_rows(PREVIOUS_JOURNAL)
    if old[-1]["global_started_pairs"] != 30 or [r["status"] for r in old].count("COMPLETED") != 2:
        raise ValueError("P017_EXPECT_COMPLETED30_PREFIX")
    ptr = json.loads(POINTER.read_text())
    if digest(POINTER) != p["previous_pointer"]["sha256"] and (
        ptr.get("schema") != 7
        or ptr.get("plan") != reference(plan_path)
        or ptr.get("real_journal") != str(JOURNAL)
        or ptr.get("definition") != p["registry_definition"]
    ):
        raise ValueError("P017_OTHER_ACTIVE_REGISTRY")
    read_rows()
    return p


def append(plan_path: Path, receipt: Path, run_id: str, status: str, detail: dict) -> None:
    """Publish only after approval; charge starts permanently, never retry a failed slot."""
    lock = JOURNAL.with_suffix(".lock")
    with lock.open("x"):
        pass
    try:
        # Expiry forbids further fitting but must not prevent charging a terminal failure.
        p = ensure(plan_path, receipt, run_id, terminal=status in ("FAILED", "COMPLETED"))
        rows = read_rows()
        starts = sum(r["status"] == "STARTED" for r in rows)
        own = [r for r in rows if r["run_id"] == run_id]
        if status == "STARTED":
            if (
                own
                or starts >= 2
                or run_id != IDS[starts]
                or (rows and rows[-1]["status"] != "COMPLETED")
            ):
                raise ValueError("P017_DUPLICATE_REORDER_RETRY")
        elif not own or status not in TRANSITIONS[own[-1]["status"]]:
            raise ValueError("P017_INVALID_TRANSITION")
        event = dict(
            sequence=len(rows) + 1,
            previous=fingerprint(rows),
            at=now(),
            run_id=run_id,
            status=status,
            detail=detail,
            authority=reference(receipt),
            plan=reference(plan_path),
            previous_journal=p["previous_journal"],
            global_started_pairs=30 + starts + int(status == "STARTED"),
            effective_ceiling=200,
        )
        pending = JOURNAL.with_suffix(".pending")
        atomic_new(
            pending,
            (JOURNAL.read_bytes() if JOURNAL.exists() else b"")
            + json.dumps(event, sort_keys=True, allow_nan=False).encode()
            + b"\n",
        )
        read_rows(pending)
        if status == "STARTED" and starts == 0:
            atomic_replace_json(
                POINTER,
                dict(
                    schema=7,
                    definition=p["registry_definition"],
                    plan=reference(plan_path),
                    real_journal=str(JOURNAL),
                    previous_pointer=p["previous_pointer"],
                    previous_journal=p["previous_journal"],
                    budget_amendment=p["budget_amendment"],
                    counts_started_including_failed=True,
                    fit_permission=False,
                ),
            )
        os.replace(pending, JOURNAL)
    finally:
        lock.unlink()
