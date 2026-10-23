"""P025 exact two-start live authority and complete-immediate-gate ordering."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .branch_replication_spec import ARMS, CONTRACT, RUNS, SCIENCE
from .config import digest, fingerprint, now, write_json
from .hf1m_ft16_source import checked, ref
from .optimization_screen_recovery_authority import rows as previous_rows
from .real_batch_authority import atomic_replace_json

POINTER = Path("configs/CURRENT_EXPERIMENT_REGISTRY.json")
JOURNAL = Path("reports/audit/track_a_real_pairs_v15_p025.jsonl")
DEFINITION = Path("configs/track_a_candidate_experiment_registry_v15_p025.json")
TRANSITIONS = {
    "STARTED": {"CALIBRATED", "FAILED"},
    "CALIBRATED": {"REFITTING", "FAILED"},
    "REFITTING": {"COMPLETED", "FAILED"},
    "COMPLETED": set(),
    "FAILED": set(),
}


def code_binding() -> dict[str, str]:
    names = (
        "branch_replication_spec",
        "branch_replication_source",
        "branch_replication_engine",
        "branch_replication_authority",
        "branch_replication_run",
        "branch_replication_diagnostics",
        "branch_replication_metrics",
        "branch_replication_comparison",
        "branch_replication_states",
        "branch_replication_rehearsal",
        "objective_screen_loss",
        "objective_screen_run",
        "objective_screen_source",
        "objective_screen_attribution",
        "objective_screen_metrics",
        "objective_screen_audit",
        "objective_screen_diagnostics",
        "dm_quantile_loss",
        "dm_quantile_diagnostics",
        "dm_quantile_cases",
        "hf1m_ft16_source",
        "hf1m_ft16_loader",
        "hf1m_training_data",
        "neural_engine",
        "neural_lifecycle",
        "config",
        "real_batch_authority",
        "optimization_screen_diagnostics",
        "visualization/hf1m_long",
    )
    return {name: digest(Path("src/lstm_data") / (name + ".py")) for name in names}


def validate(history: list[dict]) -> list[dict]:
    starts, states = 0, {}
    for i, row in enumerate(history):
        name, status = row["run_id"], row["status"]
        if row["sequence"] != i + 1 or row["previous"] != fingerprint(history[:i]):
            raise ValueError("P025_CHAIN")
        if status == "STARTED":
            if (
                starts >= 2
                or name != RUNS[starts]
                or name in states
                or (i and history[i - 1]["status"] != "COMPLETED")
            ):
                raise ValueError("P025_NO_RETRY_REORDER_EXTRA")
            starts += 1
        elif name not in states or status not in TRANSITIONS[states[name]]:
            raise ValueError("P025_TRANSITION")
        if row["global_started_pairs"] != 51 + starts or row["effective_ceiling"] != 200:
            raise ValueError("P025_BUDGET")
        states[name] = status
    return history


def rows() -> list[dict]:
    raw = JOURNAL.read_bytes() if JOURNAL.exists() else b""
    if raw and not raw.endswith(b"\n"):
        raise ValueError("P025_TRUNCATED_JOURNAL")
    return validate([json.loads(line) for line in raw.splitlines()])


def require_gate(path: Path, arm: str, *, rehearsal: bool = False) -> dict:
    gate = json.loads(path.read_text())
    if gate.get("scope") != ("REHEARSAL_ONLY" if rehearsal else "RESEARCH_CANDIDATE"):
        raise ValueError("P025_EXACT_GATE_SCOPE_REQUIRED")
    if (gate.get("scope") == "REHEARSAL_ONLY") != rehearsal:
        raise ValueError("P025_REHEARSAL_IS_NOT_RESEARCH_AUTHORITY")
    if gate["status"] != f"PASS_{arm}_S123" or gate.get("all_roles") != 4:
        raise ValueError("P025_COMPLETE_IMMEDIATE_GATE_REQUIRED")
    if not gate.get("objective_reconciled") or not gate.get("reload_reconciled"):
        raise ValueError("P025_NUMERICAL_AND_RELOAD_GATE_REQUIRED")
    for reference in gate["evidence"]:
        checked(reference)
    return gate


def predecessor_gate(plan_path: Path, run_id: str, history: list[dict]) -> None:
    """The actual production barrier, independently exercised without reserving a start."""
    index = RUNS.index(run_id)
    if [r["run_id"] for r in history if r["status"] == "COMPLETED"] != list(RUNS[:index]):
        raise ValueError("P025_ORDER")
    if index:
        gate = require_gate(plan_path.parent / "E1_immediate_gate.json", ARMS[0])
        if gate["proposal_sha256"] != digest(plan_path):
            raise ValueError("P025_PREVIOUS_STAGE_PROPOSAL")


def ensure(plan_path: Path, approval_path: Path | None, run_id: str) -> dict:
    if approval_path is None:
        raise ValueError("P025_SEPARATE_LIVE_APPROVAL_REQUIRED_ZERO_UPDATES")
    plan, approval = json.loads(plan_path.read_text()), json.loads(approval_path.read_text())
    if plan.get("scope") == "REHEARSAL_ONLY":
        raise ValueError("P025_REHEARSAL_IS_NOT_AUTHORITY")
    if (
        approval.get("status") != "APPROVED"
        or approval.get("actor_type") != "human"
        or approval.get("response_provenance") != "LIVE_USER_RESPONSE_IN_THIS_SESSION"
        or not approval.get("response_text")
        or not approval.get("response_event")
        or approval.get("approved_runs") != list(RUNS)
        or run_id not in RUNS
        or approval.get("proposal_sha256") != digest(plan_path)
        or approval.get("execution_sha256") != fingerprint(code_binding())
        or approval.get("scientific_sha256") != plan["scientific_definitions"]["sha256"]
        or plan["code"] != code_binding()
        or plan["runs"] != list(RUNS)
        or plan["opening_started"] != 51
        or plan["maximum_new_starts"] != 2
        or plan["ceiling"] != 200
        or plan["protected_numeric_access"] is not False
        or plan["input_contract"]["sha256"] != CONTRACT
        or fingerprint(json.loads(checked(plan["scientific_definitions"]).read_text()))
        != fingerprint(SCIENCE)
    ):
        raise ValueError("P025_EXACT_LIVE_SCOPE_OR_BINDING_MISMATCH")
    stage0 = json.loads(checked(plan["stage0"]).read_text())
    stage1 = json.loads(checked(plan["stage1"]).read_text())
    if (
        stage0["status"] != "PASS_P025_IDENTITY_BASELINES"
        or stage1["status"] != "PASS_P025_ZERO_STEP_REHEARSAL_AND_PROPOSAL"
        or stage1["code"] != plan["code"]
        or stage1["optimizer_step_calls"] != 0
        or stage1["neural_starts"] != 0
        or plan["recipes"] != stage0["recipes"]
    ):
        raise ValueError("P025_STAGE0_AND_COMPLETE_REHEARSAL_REQUIRED")
    for reference in (
        plan["protected_refs"]
        + plan["baseline_refs"]
        + [plan["input_contract"], plan["previous_journal"]]
    ):
        checked(reference)
    prior = previous_rows()
    if prior[-1]["global_started_pairs"] != 51 or prior[-1]["status"] != "COMPLETED":
        raise ValueError("P025_PREDECESSOR51_REQUIRED")
    pointer = json.loads(POINTER.read_text())
    if pointer["real_journal"] != str(JOURNAL):
        if digest(POINTER) != plan["previous_pointer"]["sha256"] or rows():
            raise ValueError("P025_POINTER_CHANGED")
    elif pointer["plan"] != ref(plan_path):
        raise ValueError("P025_ACTIVE_PLAN_CHANGED")
    history = rows()
    own = [r for r in history if r["run_id"] == run_id]
    if own and own[-1]["status"] in ("COMPLETED", "FAILED"):
        raise ValueError("P025_TERMINAL_NO_RETRY")
    if any(r["status"] == "FAILED" for r in history):
        raise ValueError("P025_STOP_AFTER_FAILURE")
    if not own:
        predecessor_gate(plan_path, run_id, history)
        for reference in plan["source_hashes"].values():
            checked(reference)
    return plan


def append(plan_path: Path, approval_path: Path, run_id: str, status: str, detail: dict) -> None:
    lock = JOURNAL.with_suffix(".lock")
    with lock.open("x"):
        pass
    try:
        plan = ensure(plan_path, approval_path, run_id)
        history = rows()
        record = dict(
            sequence=len(history) + 1,
            previous=fingerprint(history),
            at=now(),
            run_id=run_id,
            status=status,
            global_started_pairs=51
            + sum(r["status"] == "STARTED" for r in history)
            + int(status == "STARTED"),
            effective_ceiling=200,
            plan=ref(plan_path),
            authority=ref(approval_path),
            previous_journal=plan["previous_journal"],
            detail=detail,
        )
        validate(history + [record])
        with JOURNAL.open("ab") as stream:
            stream.write((json.dumps(record, sort_keys=True, allow_nan=False) + "\n").encode())
            stream.flush()
            os.fsync(stream.fileno())
        if not DEFINITION.exists():
            write_json(
                DEFINITION,
                dict(
                    schema_version=15,
                    package="P025",
                    runs=list(RUNS),
                    plan=ref(plan_path),
                    previous_pointer=plan["previous_pointer"],
                ),
            )
        previous = json.loads(checked(plan["previous_pointer"]).read_text())
        atomic_replace_json(
            POINTER,
            dict(
                schema_version=15,
                definition=ref(DEFINITION),
                plan=ref(plan_path),
                real_journal=str(JOURNAL),
                previous_journal=plan["previous_journal"],
                previous_pointer=plan["previous_pointer"],
                counts_started_including_failed=True,
                fit_permission=False,
                live_approval_required=True,
                effective_ceiling=200,
                budget_amendment=previous["budget_amendment"],
            ),
        )
    finally:
        lock.unlink()
