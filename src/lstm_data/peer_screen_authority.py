"""P027 exact three-start live authority and complete-immediate-gate ordering."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .config import digest, fingerprint, now, write_json
from .hf1m_ft16_source import checked, ref
from .peer_screen_spec import ARCHITECTURES, ARMS, CONTRACT, ROLES, RUNS, SCIENCE
from .real_batch_authority import atomic_replace_json
from .temporal_screen_authority import rows as previous_rows

POINTER = Path("configs/CURRENT_EXPERIMENT_REGISTRY.json")
JOURNAL = Path("reports/audit/track_a_real_pairs_v17_p027.jsonl")
DEFINITION = Path("configs/track_a_candidate_experiment_registry_v17_p027.json")
TRANSITIONS = {
    "STARTED": {"CALIBRATED", "FAILED"},
    "CALIBRATED": {"REFITTING", "FAILED"},
    "REFITTING": {"COMPLETED", "FAILED"},
    "COMPLETED": set(),
    "FAILED": set(),
}


def code_binding() -> dict[str, str]:
    names = (
        "peer_screen_spec",
        "peer_screen_models",
        "peer_screen_source",
        "peer_screen_data",
        "peer_screen_control",
        "peer_screen_engine",
        "peer_screen_authority",
        "peer_screen_run",
        "peer_screen_diagnostics",
        "peer_screen_metrics",
        "peer_screen_mechanisms",
        "peer_screen_rehearsal",
        "temporal_screen_source",
        "temporal_screen_metrics",
        "temporal_screen_authority",
        "temporal_screen_rehearsal",
        "peer_screen_release",
        "visualization/peer_screen_ui",
        "controlled_loss",
        "hf1m_action_audit",
        "hf1m_training_run",
        "hf20_training_run",
        "visualization/objective_screen",
        "objective_screen_run",
        "objective_screen_source",
        "objective_screen_attribution",
        "objective_screen_metrics",
        "objective_screen_audit",
        "objective_screen_diagnostics",
        "dm_quantile_cases",
        "hf1m_ft16_source",
        "hf1m_ft16_loader",
        "hf1m_training_data",
        "neural_engine",
        "neural_lifecycle",
        "config",
        "real_batch_authority",
        "optimization_screen_diagnostics",
        "optimization_screen_supplement",
        "branch_replication_metrics",
        "branch_replication_followup",
        "branch_replication_diagnostics",
        "branch_replication_release",
        "visualization/hf1m_long",
        "branch_replication_authority",
    )
    binding = {name: digest(Path("src/lstm_data") / (name + ".py")) for name in names}
    binding["apps/track_a_dashboard.py"] = digest(Path("apps/track_a_dashboard.py"))
    return binding


def validate(history: list[dict]) -> list[dict]:
    starts, states = 0, {}
    for i, row in enumerate(history):
        name, status = row["run_id"], row["status"]
        if row["sequence"] != i + 1 or row["previous"] != fingerprint(history[:i]):
            raise ValueError("P027_CHAIN")
        if status == "STARTED":
            if (
                starts >= 3
                or name != RUNS[starts]
                or name in states
                or (i and history[i - 1]["status"] != "COMPLETED")
            ):
                raise ValueError("P027_NO_RETRY_REORDER_EXTRA")
            starts += 1
        elif name not in states or status not in TRANSITIONS[states[name]]:
            raise ValueError("P027_TRANSITION")
        if row["global_started_pairs"] != 56 + starts or row["effective_ceiling"] != 200:
            raise ValueError("P027_BUDGET")
        states[name] = status
    return history


def rows() -> list[dict]:
    raw = JOURNAL.read_bytes() if JOURNAL.exists() else b""
    if raw and not raw.endswith(b"\n"):
        raise ValueError("P027_TRUNCATED_JOURNAL")
    return validate([json.loads(line) for line in raw.splitlines()])


def required_artifacts(arm: str) -> list[str]:
    """Named deliverables are mandatory even if a boolean or prose summary says PASS."""
    if arm not in ARMS:
        raise ValueError("P027_ARM")
    names = [
        "cohorts.parquet",
        "refit/cases.parquet",
        "refit/case_candles.parquet",
        "refit/case_features.parquet",
        "refit/case_20_returns.parquet",
        "refit/case_peer_hidden.parquet",
        "refit/mechanisms.json",
        "refit/peer_input_sensitivity.parquet",
        "ui_payload/manifest.json",
        "ui_payload/component_receipt.json",
        f"P027_{arm}_{ARCHITECTURES[arm]}_RESULT.md",
        f"P027_{arm}_OBJECTIVE_SPACE_EXTREME_LOSS.md",
    ]
    for role in ROLES:
        names.extend(
            role + "/" + name
            for name in (
                "population.parquet",
                "metrics.json",
                "thresholds.json",
                "matched_T2_S42.json",
                "paired_daily.parquet",
                "heterogeneity.parquet",
                "T2_S42.parquet",
                "T2_S123.parquet",
                "peer_information_control.json",
                "peer_shift_slices.parquet",
                "peer_shift_mapping.parquet",
                "peer_original_matched.parquet",
                "peer_shifted_matched.parquet",
            )
        )
    extra = dict(
        A4=[
            "case_peer_M1_operands.parquet",
            "case_peer_summaries.parquet",
            "peer_summary_distribution.parquet",
        ],
        A5=[
            "stock_mixing_matrix.parquet",
            "stock_mixing_parameters.parquet",
            "peer_hidden_jacobian.parquet",
        ],
        A6=[
            "attention_rows.parquet",
            "case_peer_attention.parquet",
            "peer_hidden_jacobian.parquet",
        ],
    )
    return names + ["refit/" + name for name in extra[arm]]


def require_gate(path: Path, arm: str, *, rehearsal: bool = False) -> dict:
    gate = json.loads(path.read_text())
    if gate.get("scope") != ("REHEARSAL_ONLY" if rehearsal else "RESEARCH_CANDIDATE"):
        raise ValueError("P027_EXACT_GATE_SCOPE_REQUIRED")
    if (gate.get("scope") == "REHEARSAL_ONLY") != rehearsal:
        raise ValueError("P027_REHEARSAL_IS_NOT_RESEARCH_AUTHORITY")
    if gate["status"] != f"PASS_P027_{arm}" or gate.get("all_roles") != 4:
        raise ValueError("P027_COMPLETE_IMMEDIATE_GATE_REQUIRED")
    if (
        not all(
            gate.get(k)
            for k in (
                "objective_reconciled",
                "reload_reconciled",
                "mechanisms_verified",
                "resources_verified",
                "source_verified",
                "uncertainty_verified",
                "tests_verified",
                "peer_control_verified",
                "case_peer_evidence_verified",
                "ui_verified",
                "order_and_clock_verified",
            )
        )
        or gate.get("cases", {}).get("cases", 0) < 22
    ):
        raise ValueError("P027_NUMERICAL_AND_RELOAD_GATE_REQUIRED")
    if gate.get("evidence_fingerprint") != fingerprint(gate["evidence"]):
        raise ValueError("P027_GATE_EVIDENCE_FINGERPRINT")
    for reference in gate["evidence"]:
        checked(reference)
    required = required_artifacts(arm)
    deliverables = gate.get("deliverables", {})
    if set(deliverables) != set(required):
        raise ValueError("P027_MISSING_REQUIRED_SCIENTIFIC_ARTIFACT")
    root = Path(gate["diagnostics_root"])
    for name in required:
        if Path(deliverables[name]["path"]) != root / name:
            raise ValueError("P027_ARTIFACT_NAMESPACE")
        checked(deliverables[name])
    ui = json.loads(checked(deliverables["ui_payload/component_receipt.json"]).read_text())
    if (
        ui.get("status") != "PASS_P027_ARM_COMPONENTS"
        or ui.get("arm") != arm
        or ui.get("scope") != gate["scope"]
        or ui.get("role_view_pairs") != 36
        or ui.get("case_choices") != 22
        or ui.get("stock_histories") != 20
        or ui.get("feature_channels") != 16
        or ui.get("optimizer_step_calls") != 0
    ):
        raise ValueError("P027_REAL_COMPLETE_UI_RECEIPT_REQUIRED")
    manifest = json.loads(checked(ui["manifest"]).read_text())
    if (
        ui.get("execution_sha256") != gate["execution_sha256"]
        or manifest.get("execution_sha256") != gate["execution_sha256"]
        or ui.get("files_fingerprint") != fingerprint(manifest["files"])
    ):
        raise ValueError("P027_UI_PAYLOAD_EXECUTION_BINDING")
    for reference in manifest["files"].values():
        checked(reference)
    return gate


def append_failure(plan_path: Path, approval_path: Path, run_id: str, error: BaseException) -> None:
    """Record only FAILED for an already charged start, even if current code/source changed.

    This grants no fitting authority. Original start-bound refs are retained, rather
    than rebinding an altered approval/plan or refunding its permanently charged start.
    """
    lock = JOURNAL.with_suffix(".lock")
    with lock.open("x"):
        pass
    try:
        history = rows()
        own = [r for r in history if r["run_id"] == run_id]
        if not own or own[0]["status"] != "STARTED" or own[-1]["status"] in ("COMPLETED", "FAILED"):
            raise ValueError("P027_FAILURE_ONLY_FOR_CHARGED_NONTERMINAL_RUN")
        start = own[0]
        if (
            Path(start["plan"]["path"]) != plan_path
            or Path(start["authority"]["path"]) != approval_path
        ):
            raise ValueError("P027_FAILURE_START_BINDING")
        record = dict(
            sequence=len(history) + 1,
            previous=fingerprint(history),
            at=now(),
            run_id=run_id,
            status="FAILED",
            global_started_pairs=history[-1]["global_started_pairs"],
            effective_ceiling=200,
            plan=start["plan"],
            authority=start["authority"],
            previous_journal=start["previous_journal"],
            detail=dict(
                error_type=type(error).__name__,
                error=str(error),
                original_charged_start_preserved=True,
                new_fit_permission=False,
                current_binding_may_be_invalid=True,
            ),
        )
        validate(history + [record])
        with JOURNAL.open("ab") as stream:
            stream.write((json.dumps(record, sort_keys=True, allow_nan=False) + "\n").encode())
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        lock.unlink()


def predecessor_gate(plan_path: Path, run_id: str, history: list[dict]) -> None:
    """The actual production barrier, independently exercised without reserving a start."""
    index = RUNS.index(run_id)
    if [r["run_id"] for r in history if r["status"] == "COMPLETED"] != list(RUNS[:index]):
        raise ValueError("P027_ORDER")
    if index:
        gate = require_gate(
            plan_path.parent / (ARMS[index - 1] + "_immediate_gate.json"), ARMS[index - 1]
        )
        plan = json.loads(plan_path.read_text())
        if (
            gate["proposal_sha256"] != digest(plan_path)
            or gate["execution_sha256"] != fingerprint(code_binding())
            or gate["result_sha256"] != history[-1]["detail"]["result"]["sha256"]
            or gate["scientific_sha256"] != plan["scientific_definitions"]["sha256"]
        ):
            raise ValueError("P027_PREVIOUS_STAGE_PROPOSAL")


def ensure(plan_path: Path, approval_path: Path | None, run_id: str) -> dict:
    if approval_path is None:
        raise ValueError("P027_SEPARATE_LIVE_APPROVAL_REQUIRED_ZERO_UPDATES")
    if any(plan_path.parent.glob("*_STOP_IMMEDIATE_GATE.json")):
        raise ValueError("P027_STOP_REQUIRES_NEW_RECOVERY_AUTHORITY")
    plan, approval = json.loads(plan_path.read_text()), json.loads(approval_path.read_text())
    if plan.get("scope") == "REHEARSAL_ONLY":
        raise ValueError("P027_REHEARSAL_IS_NOT_AUTHORITY")
    if (
        approval.get("status") != "APPROVED_P027_THREE_STARTS"
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
        or plan["opening_started"] != 56
        or plan["maximum_new_starts"] != 3
        or plan["ceiling"] != 200
        or plan["protected_numeric_access"] is not False
        or plan["input_contract"]["sha256"] != CONTRACT
        or fingerprint(json.loads(checked(plan["scientific_definitions"]).read_text()))
        != fingerprint(SCIENCE)
    ):
        raise ValueError("P027_EXACT_LIVE_SCOPE_OR_BINDING_MISMATCH")
    stage0 = json.loads(checked(plan["stage0"]).read_text())
    stage1 = json.loads(checked(plan["stage1"]).read_text())
    if (
        stage0["status"] != "PASS_P027_STAGE0_AUTHORITY_IDENTITY"
        or stage1["status"] != "PASS_P027_ZERO_STEP_REHEARSAL"
        or stage1["code"] != plan["code"]
        or stage1["optimizer_step_calls"] != 0
        or stage1["neural_starts"] != 0
        or any(plan["recipes"][arm] != stage0["recipes"] for arm in ARMS)
    ):
        raise ValueError("P027_STAGE0_AND_COMPLETE_REHEARSAL_REQUIRED")
    for reference in (
        plan["protected_refs"]
        + plan["baseline_refs"]
        + plan["preservation_refs"]
        + [plan["input_contract"], plan["previous_journal"]]
    ):
        checked(reference)
    for key in ("validation", "design_gate", "architecture_reconciliation"):
        checked(plan[key])
    for reference in plan["analysis_references"]:
        checked(reference)
    if (
        json.loads(checked(plan["design_gate"]).read_text())["status"] != "PASS_P027_FROZEN_DESIGNS"
        or json.loads(checked(plan["architecture_reconciliation"]).read_text())["status"]
        != "PASS_P027_ARCHITECTURE_RECONCILIATION"
    ):
        raise ValueError("P027_FROZEN_DESIGN_RECONCILIATION_REQUIRED")
    validation = json.loads(checked(plan["validation"]).read_text())
    if (
        validation["status"] != "PASS_P027_VALIDATION"
        or validation.get("scope") != "PREPARED_FOR_LIVE_APPROVAL"
        or validation["code"] != plan["code"]
    ):
        raise ValueError("P027_FULL_CURRENT_VALIDATION_REQUIRED")
    prior = previous_rows()
    if prior[-1]["global_started_pairs"] != 56 or prior[-1]["status"] != "COMPLETED":
        raise ValueError("P027_PREDECESSOR56_REQUIRED")
    pointer = json.loads(POINTER.read_text())
    if pointer["real_journal"] != str(JOURNAL):
        if digest(POINTER) != plan["previous_pointer"]["sha256"] or rows():
            raise ValueError("P027_POINTER_CHANGED")
    elif pointer["plan"] != ref(plan_path):
        raise ValueError("P027_ACTIVE_PLAN_CHANGED")
    history = rows()
    own = [r for r in history if r["run_id"] == run_id]
    if own and own[-1]["status"] in ("COMPLETED", "FAILED"):
        raise ValueError("P027_TERMINAL_NO_RETRY")
    if any(r["status"] == "FAILED" for r in history):
        raise ValueError("P027_STOP_AFTER_FAILURE")
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
            global_started_pairs=56
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
                    schema_version=17,
                    package="P027",
                    runs=list(RUNS),
                    plan=ref(plan_path),
                    previous_pointer=plan["previous_pointer"],
                ),
            )
        previous = json.loads(checked(plan["previous_pointer"]).read_text())
        atomic_replace_json(
            POINTER,
            dict(
                schema_version=17,
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
