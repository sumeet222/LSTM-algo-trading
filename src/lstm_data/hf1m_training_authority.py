"""P021 live four-start authority; immutable 32-start prefix, no retries."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

from .config import atomic_new, digest, fingerprint, now
from .hf1m_ft16_source import checked, ref
from .hf20_replication_authority import read_rows as prefix_rows
from .real_batch_authority import atomic_replace_json

IDS = tuple(f"HF1M-LONG-TM0-{arm}-S{seed}-DEV1" for seed in (42, 123) for arm in ("C0", "T2"))
POINTER = Path("configs/CURRENT_EXPERIMENT_REGISTRY.json")
JOURNAL = Path("reports/audit/track_a_real_pairs_v8.jsonl")
TRANSITIONS = {
    "STARTED": {"CALIBRATED", "FAILED_AFTER_START"},
    "CALIBRATED": {"REFITTING", "FAILED_AFTER_START"},
    "REFITTING": {"COMPLETED", "FAILED_AFTER_START"},
    "COMPLETED": set(),
    "FAILED_AFTER_START": set(),
}
MODULES = (
    "hf1m_training_authority.py",
    "hf1m_training_data.py",
    "hf1m_training_run.py",
    "hf1m_ft16_loader.py",
    "hf1m_ft16_source.py",
    "neural_engine.py",
    "neural_lifecycle.py",
    "controlled_loss.py",
    "hf20_training_run.py",
)


def code_binding() -> dict:
    return {n: digest(Path("src/lstm_data") / n) for n in MODULES}


def read_rows(path: Path = JOURNAL) -> list[dict]:
    raw = path.read_bytes() if path.exists() else b""
    if raw and not raw.endswith(b"\n"):
        raise ValueError("P021_TRUNCATED_JOURNAL")
    rows = [json.loads(line) for line in raw.splitlines()]
    states: dict[str, str] = {}
    starts = 0
    for i, r in enumerate(rows):
        name, status = r["run_id"], r["status"]
        if r["sequence"] != i + 1 or r["previous"] != fingerprint(rows[:i]) or name not in IDS:
            raise ValueError("P021_JOURNAL_CHAIN")
        if status == "STARTED":
            if (
                starts >= 4
                or name in states
                or name != IDS[starts]
                or (i and rows[i - 1]["status"] != "COMPLETED")
            ):
                raise ValueError("P021_NO_EXTRA_START_REORDER_RETRY")
            starts += 1
        elif name not in states or status not in TRANSITIONS[states[name]]:
            raise ValueError("P021_INVALID_TRANSITION")
        if r["global_started_pairs"] != 32 + starts or r["effective_ceiling"] != 200:
            raise ValueError("P021_BUDGET_CHAIN")
        states[name] = status
    return rows


def ensure(plan_path: Path, receipt: Path | None, run_id: str, *, terminal: bool = False) -> dict:
    p = json.loads(plan_path.read_text())
    if receipt is None:
        raise ValueError("P021_LIVE_APPROVAL_REQUIRED_ZERO_STEPS")
    a = json.loads(receipt.read_text())
    if (
        a.get("status") != "APPROVED"
        or a.get("actor_type") != "human"
        or a.get("response_provenance") != "LIVE_USER_RESPONSE_IN_THIS_SESSION"
        or not a.get("response_text")
        or a.get("approved_runs") != list(IDS)
        or a.get("proposal_sha256") != digest(plan_path)
        or a.get("code_sha256") != fingerprint(code_binding())
        or a.get("input_contract") != p["input_contract"]
        or p["runs"] != list(IDS)
        or run_id not in IDS
        or p["opening_started"] != 32
        or p["maximum_new_starts"] != 4
        or p["ceiling"] != 200
        or p["code"] != code_binding()
        or p["code_sha256"] != fingerprint(code_binding())
        or p["heldout_access"] is not False
    ):
        raise ValueError("P021_EXACT_FOUR_START_SCOPE_REQUIRED")
    if not terminal and pd.Timestamp.now(tz="UTC") >= pd.Timestamp(p["fit_deadline"]):
        raise ValueError("P021_AUTHORITY_EXPIRED")
    for reference in p["protected_refs"] + [
        p["input_contract"],
        p["previous_journal"],
        p["registry_definition"],
    ]:
        checked(reference)
    old = prefix_rows(Path(p["previous_journal"]["path"]))
    if old[-1]["global_started_pairs"] != 32 or old[-1]["status"] != "COMPLETED":
        raise ValueError("P021_EXPECT_COMPLETED32_PREFIX")
    ptr = json.loads(POINTER.read_text())
    if digest(POINTER) != p["previous_pointer"]["sha256"] and (
        ptr.get("schema") != 8
        or ptr.get("plan") != ref(plan_path)
        or ptr.get("real_journal") != str(JOURNAL)
        or ptr.get("definition") != p["registry_definition"]
    ):
        raise ValueError("P021_OTHER_ACTIVE_REGISTRY_RECONCILE")
    read_rows()
    return p


def append(plan_path: Path, receipt: Path, run_id: str, status: str, detail: dict) -> None:
    """Charge each start durably; terminal failure never releases budget or permits retry."""
    lock = JOURNAL.with_suffix(".lock")
    with lock.open("x"):
        pass
    try:
        p = ensure(
            plan_path, receipt, run_id, terminal=status in ("COMPLETED", "FAILED_AFTER_START")
        )
        rows = read_rows()
        starts = sum(r["status"] == "STARTED" for r in rows)
        own = [r for r in rows if r["run_id"] == run_id]
        if status == "STARTED":
            if (
                own
                or starts >= 4
                or run_id != IDS[starts]
                or (rows and rows[-1]["status"] != "COMPLETED")
            ):
                raise ValueError("P021_NO_EXTRA_START_REORDER_RETRY")
            if starts == 2:
                pair = json.loads((plan_path.parent / "PASS_SEED42_PAIR.json").read_text())
                if pair["status"] != "PASS_SEED42_PAIR" or pair["runs"] != list(IDS[:2]):
                    raise ValueError("P021_FIRST_PAIR_AUDIT_REQUIRED")
        elif not own or status not in TRANSITIONS[own[-1]["status"]]:
            raise ValueError("P021_INVALID_TRANSITION")
        event = dict(
            sequence=len(rows) + 1,
            previous=fingerprint(rows),
            at=now(),
            run_id=run_id,
            status=status,
            detail=detail,
            authority=ref(receipt),
            plan=ref(plan_path),
            previous_journal=p["previous_journal"],
            global_started_pairs=32 + starts + int(status == "STARTED"),
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
                    schema=8,
                    definition=p["registry_definition"],
                    plan=ref(plan_path),
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
