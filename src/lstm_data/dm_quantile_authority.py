"""P023 exact three-start authority, append-only successor journal and fail-closed order."""

from __future__ import annotations

import json
from pathlib import Path

from .config import digest, fingerprint, now, write_json
from .dm_quantile_loss import RUNS
from .hf1m_ft16_source import checked, ref
from .objective_screen_recovery import rows as previous_rows
from .real_batch_authority import atomic_replace_json

POINTER = Path("configs/CURRENT_EXPERIMENT_REGISTRY.json")
JOURNAL = Path("reports/audit/track_a_real_pairs_v12_p023.jsonl")


def code_binding() -> dict[str, str]:
    names = [
        "dm_quantile_loss",
        "dm_quantile_run",
        "dm_quantile_authority",
        "objective_screen_source",
        "hf1m_ft16_loader",
        "hf1m_training_data",
        "objective_screen_run",
        "neural_engine",
        "neural_lifecycle",
        "config",
        "real_batch_authority",
        "hf1m_training_run",
        "objective_screen_loss",
        "objective_screen_metrics",
        "objective_screen_audit",
        "objective_screen_authority",
    ]
    return {name: digest(Path("src/lstm_data") / (name + ".py")) for name in names}


def rows() -> list[dict]:
    if not JOURNAL.exists():
        return []
    raw = JOURNAL.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise ValueError("P023_TRUNCATED_JOURNAL")
    result = [json.loads(line) for line in raw.splitlines()]
    return validate_history(result)


def validate_history(result: list[dict]) -> list[dict]:
    """Validate a proposed append before writing any journal bytes."""
    starts = 0
    states = {}
    allowed = {
        "STARTED": {"CALIBRATED", "FAILED"},
        "CALIBRATED": {"REFITTING", "FAILED"},
        "REFITTING": {"COMPLETED", "FAILED"},
        "COMPLETED": set(),
        "FAILED": set(),
    }
    for i, row in enumerate(result):
        name = row["run_id"]
        status = row["status"]
        if row["sequence"] != i + 1 or row["previous"] != fingerprint(result[:i]):
            raise ValueError("P023_JOURNAL_CHAIN")
        if status == "STARTED":
            if starts >= 3 or name != RUNS[starts] or name in states:
                raise ValueError("P023_NO_EXTRA_RETRY_OR_REORDER")
            if i and result[i - 1]["status"] != "COMPLETED":
                raise ValueError("P023_PRIOR_MUST_COMPLETE")
            starts += 1
        elif name not in states or status not in allowed[states[name]]:
            raise ValueError("P023_JOURNAL_TRANSITION")
        if row["global_started_pairs"] != 41 + starts or row["effective_ceiling"] != 200:
            raise ValueError("P023_LEDGER_MISMATCH")
        states[name] = status
    return result


def ensure(plan: Path, approval: Path | None, run_id: str) -> dict:
    if approval is None:
        raise ValueError("P023_SEPARATE_LIVE_THREE_RUN_APPROVAL_REQUIRED")
    p = json.loads(plan.read_text())
    a = json.loads(approval.read_text())
    if (
        a.get("status") != "APPROVED"
        or a.get("actor_type") != "human"
        or a.get("response_provenance") != "LIVE_USER_RESPONSE_IN_THIS_SESSION"
        or not a.get("response_text")
        or a.get("proposal_sha256") != digest(plan)
        or a.get("execution_sha256") != fingerprint(code_binding())
        or a.get("approved_runs") != list(RUNS)
        or p["runs"] != list(RUNS)
        or p["code"] != code_binding()
        or run_id not in RUNS
        or p["opening_started"] != 41
        or p["maximum_new_starts"] != 3
        or p["ceiling"] != 200
        or p["protected_numeric_access"] is not False
    ):
        raise ValueError("P023_EXACT_LIVE_AUTHORITY_MISMATCH")
    for r in p["protected_refs"] + [
        p["design"],
        p["audit_gate"],
        p["input_contract"],
        p["previous_journal"],
    ]:
        checked(r)
    prior = previous_rows()
    if prior[-1]["global_started_pairs"] != 41 or prior[-1]["status"] != "COMPLETED":
        raise ValueError("STOP_LEDGER_MISMATCH")
    pointer = json.loads(POINTER.read_text())
    if pointer["real_journal"] != str(JOURNAL):
        checked(p["previous_pointer"])
        if rows() or digest(POINTER) != p["previous_pointer"]["sha256"]:
            raise ValueError("P023_POINTER_CHAIN")
    elif pointer["plan"]["sha256"] != digest(plan):
        raise ValueError("P023_POINTER_PLAN")
    history = rows()
    own = [r for r in history if r["run_id"] == run_id]
    if own and own[-1]["status"] in {"COMPLETED", "FAILED"}:
        raise ValueError("P023_TERMINAL_NO_RETRY")
    if not own and RUNS.index(run_id):
        gate = json.loads((plan.parent / f"stage_{RUNS.index(run_id) + 1}_gate.json").read_text())
        if gate["status"] != "PASS_" + RUNS[RUNS.index(run_id) - 1].split("-")[3]:
            raise ValueError("P023_PRIOR_IMMEDIATE_DIAGNOSTICS_REQUIRED")
    if not own:
        complete = [r["run_id"] for r in history if r["status"] == "COMPLETED"]
        if complete != list(RUNS[: RUNS.index(run_id)]) or any(
            r["status"] == "FAILED" for r in history
        ):
            raise ValueError("P023_EXACT_ORDER_REQUIRED")
    return p


def append(plan: Path, approval: Path, run_id: str, status: str, detail: dict) -> None:
    p = ensure(plan, approval, run_id)
    history = rows()
    count = 41 + sum(r["status"] == "STARTED" for r in history) + int(status == "STARTED")
    record = dict(
        sequence=len(history) + 1,
        previous=fingerprint(history),
        at=now(),
        run_id=run_id,
        status=status,
        global_started_pairs=count,
        effective_ceiling=200,
        plan=ref(plan),
        authority=ref(approval),
        previous_journal=p["previous_journal"],
        detail=detail,
    )
    validate_history(history + [record])
    # A per-run exclusive claim is acquired by the executor before invoking this function.
    with JOURNAL.open("ab") as stream:
        stream.write((json.dumps(record, sort_keys=True) + "\n").encode())
        stream.flush()
        import os

        os.fsync(stream.fileno())
    rows()
    definition = Path(p["registry_definition"])
    if not definition.exists():
        write_json(
            definition,
            dict(
                schema_version=12,
                package="P023",
                runs=list(RUNS),
                plan=ref(plan),
                previous_pointer=p["previous_pointer"],
            ),
        )
    atomic_replace_json(
        POINTER,
        dict(
            schema_version=12,
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
