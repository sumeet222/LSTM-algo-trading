"""P024 exact six-start live authority; ordered durable journal, no retries."""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

from .config import digest, fingerprint, now, write_json
from .dm_quantile_authority import rows as prior_rows
from .hf1m_ft16_source import checked, ref
from .optimization_screen import RUNS, VARIANTS
from .real_batch_authority import atomic_replace_json

POINTER = Path("configs/CURRENT_EXPERIMENT_REGISTRY.json")
JOURNAL = Path("reports/audit/track_a_real_pairs_v13_p024.jsonl")
TRANSITIONS = {
    "STARTED": {"CALIBRATED", "FAILED"},
    "CALIBRATED": {"REFITTING", "FAILED"},
    "REFITTING": {"COMPLETED", "FAILED"},
    "COMPLETED": set(),
    "FAILED": set(),
}


def code_binding() -> dict[str, str]:
    names = (
        "optimization_screen",
        "optimization_screen_authority",
        "optimization_screen_run",
        "optimization_screen_preflight",
        "hf1m_training_run",
        "hf1m_training_data",
        "objective_screen_source",
        "hf1m_ft16_loader",
        "hf1m_ft16_source",
        "neural_engine",
        "neural_lifecycle",
        "controlled_loss",
        "config",
        "real_batch_authority",
        "objective_screen_run",
        "visualization/hf1m_long",
        "hf1m_action_audit",
        "hf1m_action_source",
    )
    return {n: digest(Path("src/lstm_data") / (n + ".py")) for n in names}


def validate(history: list[dict]) -> list[dict]:
    starts, states = 0, {}
    for i, r in enumerate(history):
        name, status = r["run_id"], r["status"]
        if r["sequence"] != i + 1 or r["previous"] != fingerprint(history[:i]):
            raise ValueError("P024_CHAIN")
        if status == "STARTED":
            if (
                starts >= 6
                or name != RUNS[starts]
                or name in states
                or (i and history[i - 1]["status"] != "COMPLETED")
            ):
                raise ValueError("P024_NO_REORDER_RETRY_EXTRA")
            starts += 1
        elif name not in states or status not in TRANSITIONS[states[name]]:
            raise ValueError("P024_TRANSITION")
        if r["global_started_pairs"] != 44 + starts or r["effective_ceiling"] != 200:
            raise ValueError("P024_BUDGET")
        states[name] = status
    return history


def rows() -> list[dict]:
    raw = JOURNAL.read_bytes() if JOURNAL.exists() else b""
    if raw and not raw.endswith(b"\n"):
        raise ValueError("P024_TRUNCATED_JOURNAL")
    return validate([json.loads(line) for line in raw.splitlines()])


def ensure(plan: Path, approval: Path | None, run_id: str) -> dict:
    if approval is None:
        raise ValueError("P024_SEPARATE_LIVE_APPROVAL_REQUIRED_ZERO_UPDATES")
    p, a = json.loads(plan.read_text()), json.loads(approval.read_text())
    if (
        a.get("status") != "APPROVED"
        or a.get("actor_type") != "human"
        or a.get("response_provenance") != "LIVE_USER_RESPONSE_IN_THIS_SESSION"
        or not a.get("response_text")
        or a.get("proposal_sha256") != digest(plan)
        or a.get("execution_sha256") != fingerprint(code_binding())
        or a.get("approved_runs") != list(RUNS)
        or p["runs"] != list(RUNS)
        or p["variants"] != [asdict(v) for v in VARIANTS]
        or p["code"] != code_binding()
        or p["execution_sha256"] != fingerprint(code_binding())
        or run_id not in RUNS
        or p["opening_started"] != 44
        or p["maximum_new_starts"] != 6
        or p["ceiling"] != 200
        or p["protected_numeric_access"] is not False
    ):
        raise ValueError("P024_EXACT_SCOPE_OR_HASH_MISMATCH")
    for r in (
        p["protected_refs"]
        + p["baseline_refs"]
        + [p["stage0"], p["stage1"], p["input_contract"], p["previous_journal"], p["frozen_design"]]
    ):
        checked(r)
    prior = prior_rows()
    if prior[-1]["status"] != "COMPLETED" or prior[-1]["global_started_pairs"] != 44:
        raise ValueError("P024_COMPLETED44_PREFIX_REQUIRED")
    ptr = json.loads(POINTER.read_text())
    if ptr["real_journal"] != str(JOURNAL):
        if digest(POINTER) != p["previous_pointer"]["sha256"] or rows():
            raise ValueError("P024_POINTER_CHAIN")
    elif ptr["plan"] != ref(plan):
        raise ValueError("P024_POINTER_PLAN")
    history = rows()
    own = [r for r in history if r["run_id"] == run_id]
    if own and own[-1]["status"] in {"COMPLETED", "FAILED"}:
        raise ValueError("P024_TERMINAL_NO_RETRY")
    if any(r["status"] == "FAILED" for r in history):
        raise ValueError("P024_STOP_AFTER_FAILURE")
    if not own:
        index = RUNS.index(run_id)
        if [r["run_id"] for r in history if r["status"] == "COMPLETED"] != list(RUNS[:index]):
            raise ValueError("P024_ORDER_REQUIRED")
        if index:
            gate_path = plan.parent / f"stage_{index + 2}_receipt.json"
            gate = json.loads(gate_path.read_text())
            if (
                gate["status"] != "PASS_" + VARIANTS[index - 1].arm
                or gate["run_id"] != RUNS[index - 1]
                or gate["proposal_sha256"] != digest(plan)
            ):
                raise ValueError("P024_PRIOR_IMMEDIATE_SCIENTIFIC_GATE_REQUIRED")
            for r in gate["evidence"]:
                checked(r)
    return p


def append(plan: Path, approval: Path, run_id: str, status: str, detail: dict) -> None:
    """Exclusive journal claim; append/fsync charged starts before any optimizer update."""
    lock = JOURNAL.with_suffix(".lock")
    with lock.open("x"):
        pass
    try:
        p = ensure(plan, approval, run_id)
        history = rows()
        record = dict(
            sequence=len(history) + 1,
            previous=fingerprint(history),
            at=now(),
            run_id=run_id,
            status=status,
            global_started_pairs=44
            + sum(r["status"] == "STARTED" for r in history)
            + int(status == "STARTED"),
            effective_ceiling=200,
            plan=ref(plan),
            authority=ref(approval),
            previous_journal=p["previous_journal"],
            detail=detail,
        )
        validate(history + [record])
        with JOURNAL.open("ab") as stream:
            stream.write((json.dumps(record, sort_keys=True, allow_nan=False) + "\n").encode())
            stream.flush()
            os.fsync(stream.fileno())
        definition = Path(p["registry_definition"])
        if not definition.exists():
            write_json(
                definition,
                dict(
                    schema_version=13,
                    package="P024",
                    runs=list(RUNS),
                    plan=ref(plan),
                    previous_pointer=p["previous_pointer"],
                ),
            )
        atomic_replace_json(
            POINTER,
            dict(
                schema_version=13,
                definition=ref(definition),
                plan=ref(plan),
                real_journal=str(JOURNAL),
                previous_pointer=p["previous_pointer"],
                previous_journal=p["previous_journal"],
                counts_started_including_failed=True,
                fit_permission=False,
                effective_ceiling=200,
                live_approval_required=True,
                budget_amendment=json.loads(checked(p["previous_pointer"]).read_text())[
                    "budget_amendment"
                ],
            ),
        )
    finally:
        lock.unlink()
