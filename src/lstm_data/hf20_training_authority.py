"""Exact two-pair live authority and append-only successor of the 28-start journal."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .config import atomic_new, digest, fingerprint, now
from .nb1_authority import journal_rows as previous_rows
from .pretraining_policy import verify_ref
from .real_batch_authority import TRANSITIONS, atomic_replace_json

IDS = ("HF20-TM0-C0-S42-DEV1", "HF20-TM0-T2-S42-DEV1")
JOURNAL = Path("reports/audit/track_a_real_pairs_v6.jsonl")
POINTER = Path("configs/CURRENT_EXPERIMENT_REGISTRY.json")
MODULES = (
    "hf20_training_data.py",
    "hf20_training_authority.py",
    "hf20_training_run.py",
    "neural_engine.py",
    "neural_lifecycle.py",
    "controlled_loss.py",
    "config.py",
    "neural_models.py",
    "neural_health.py",
)


def reference(path: Path) -> dict:
    return dict(path=str(path), sha256=digest(path))


def code_binding() -> dict:
    return {name: digest(Path("src/lstm_data") / name) for name in MODULES}


def read_rows(path: Path = JOURNAL) -> list[dict]:
    raw = path.read_bytes() if path.exists() else b""
    if raw and not raw.endswith(b"\n"):
        raise ValueError("HF20_TRUNCATED_JOURNAL")
    rows = [json.loads(line) for line in raw.splitlines()]
    states: dict[str, str] = {}
    starts = 0
    for i, r in enumerate(rows):
        name, status = r["run_id"], r["status"]
        if r["sequence"] != i + 1 or r["previous"] != fingerprint(rows[:i]) or name not in IDS:
            raise ValueError("HF20_JOURNAL_CHAIN")
        if status == "STARTED":
            if (
                starts >= 2
                or name in states
                or name != IDS[starts]
                or (i and rows[i - 1]["status"] != "COMPLETED")
            ):
                raise ValueError("HF20_NO_DUPLICATE_REORDER_OR_RETRY")
            starts += 1
        elif name not in states or status not in TRANSITIONS[states[name]]:
            raise ValueError("HF20_INVALID_TRANSITION")
        if r["global_started_pairs"] != 28 + starts or r["effective_ceiling"] != 200:
            raise ValueError("HF20_BUDGET_CHAIN")
        states[name] = status
    return rows


def validate_approval(plan_path: Path, receipt_path: Path | None) -> dict:
    if receipt_path is None:
        raise ValueError("HF20_NO_LIVE_APPROVAL_ZERO_OPTIMIZER_STEPS")
    p, a = json.loads(plan_path.read_text()), json.loads(receipt_path.read_text())
    if (
        a.get("status") != "APPROVED"
        or a.get("actor_type") != "human"
        or a.get("proposal_sha256") != digest(plan_path)
        or a.get("approved_runs") != list(IDS)
        or a.get("response_provenance") != "LIVE_USER_RESPONSE_IN_THIS_SESSION"
        or not a.get("response_text")
        or a.get("scope") != p["scope"]
        or a.get("code_sha256") != fingerprint(code_binding())
        or a.get("input_contract") != p["input_contract"]
        or a.get("scales") != p["scales"]
    ):
        raise ValueError("HF20_EXACT_LIVE_TWO_PAIR_APPROVAL_REQUIRED")
    return p


def ensure(plan_path: Path, receipt_path: Path | None, run_id: str) -> dict:
    p = validate_approval(plan_path, receipt_path)
    if (
        run_id not in IDS
        or p["runs"] != list(IDS)
        or p["code"] != code_binding()
        or p["opening_started"] != 28
        or p["ceiling"] != 200
        or p["maximum_new_starts"] != 2
        or p["heldout_access"] is not False
    ):
        raise ValueError("HF20_SEALED_SCOPE_CODE_REQUIRED")
    for ref in p["protected_refs"] + [p["input_contract"], p["registry_definition"]]:
        verify_ref(Path.cwd(), ref)
    old = previous_rows(Path("reports/audit/track_a_real_pairs_v5.jsonl"))
    if old[-1]["global_started_pairs"] != 28 or old[-1]["status"] != "COMPLETED":
        raise ValueError("HF20_EXPECTED_28_COMPLETED_PREFIX")
    ptr = json.loads(POINTER.read_text())
    if digest(POINTER) != p["previous_pointer"]["sha256"] and (
        ptr.get("schema") != 6
        or ptr.get("plan") != reference(plan_path)
        or ptr.get("real_journal") != str(JOURNAL)
        or ptr.get("definition") != p["registry_definition"]
    ):
        raise ValueError("HF20_OTHER_ACTIVE_REGISTRY")
    read_rows()
    return p


def append(plan_path: Path, receipt_path: Path, run_id: str, status: str, detail: dict) -> None:
    """Lock, verify authority/budget, then preserve journal byte prefix and old pointer."""
    lock = JOURNAL.with_suffix(".lock")
    with lock.open("x"):
        pass
    try:
        p = ensure(plan_path, receipt_path, run_id)
        rows = read_rows()
        starts = sum(r["status"] == "STARTED" for r in rows)
        own = [r for r in rows if r["run_id"] == run_id]
        if status == "STARTED":
            if (
                own
                or starts >= 2
                or 28 + starts >= 200
                or run_id != IDS[starts]
                or (rows and rows[-1]["status"] != "COMPLETED")
            ):
                raise ValueError("HF20_NO_DUPLICATE_REORDER_OVERBUDGET")
        elif not own or status not in TRANSITIONS[own[-1]["status"]]:
            raise ValueError("HF20_INVALID_TRANSITION")
        event = dict(
            sequence=len(rows) + 1,
            previous=fingerprint(rows),
            at=now(),
            run_id=run_id,
            status=status,
            detail=detail,
            authority=reference(receipt_path),
            plan=reference(plan_path),
            previous_journal=p["previous_journal"],
            global_started_pairs=28 + starts + int(status == "STARTED"),
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
                    schema=6,
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
