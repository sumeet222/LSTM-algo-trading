"""Disabled until new live approval: four starts after the preserved P022 failure."""

from __future__ import annotations

import json
from pathlib import Path

from .config import digest, fingerprint, now, write_json
from .hf1m_ft16_source import checked, ref
from .objective_screen_authority import code_binding as original_code_binding
from .objective_screen_authority import rows as failed_history
from .objective_screen_loss import RUNS
from .real_batch_authority import atomic_replace_json

POINTER = Path("configs/CURRENT_EXPERIMENT_REGISTRY.json")
JOURNAL = Path("reports/audit/track_a_real_pairs_v11_p022_repair.jsonl")


def code_binding() -> dict[str, str]:
    result = original_code_binding()
    result["objective_screen_recovery"] = digest(Path("src/lstm_data/objective_screen_recovery.py"))
    result["config"] = digest(Path("src/lstm_data/config.py"))
    result["real_batch_authority"] = digest(Path("src/lstm_data/real_batch_authority.py"))
    return result


def rows() -> list[dict]:
    if not JOURNAL.exists():
        return []
    raw = JOURNAL.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise ValueError("P022_TRUNCATED_JOURNAL")
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
            raise ValueError("P022_JOURNAL_CHAIN")
        if status == "STARTED":
            if starts >= 4 or name != RUNS[starts] or name in states:
                raise ValueError("P022_NO_EXTRA_RETRY_OR_REORDER")
            if i and result[i - 1]["status"] != "COMPLETED":
                raise ValueError("P022_PRIOR_MUST_COMPLETE")
            starts += 1
        elif name not in states or status not in allowed[states[name]]:
            raise ValueError("P022_JOURNAL_TRANSITION")
        if row["global_started_pairs"] != 37 + starts or row["effective_ceiling"] != 200:
            raise ValueError("P022_LEDGER_MISMATCH")
        states[name] = status
    return result


def ensure(plan: Path, approval: Path | None, run_id: str) -> dict:
    if approval is None:
        raise ValueError("P022_REPAIR_SEPARATE_LIVE_APPROVAL_REQUIRED")
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
        or a.get("failed_start_preserved") is not True
        or a.get("additional_h2_restart_authorized") is not True
        or p.get("recovery") != "P022_PROGRESS_REPAIR_V1"
        or p["runs"] != list(RUNS)
        or p["code"] != code_binding()
        or run_id not in RUNS
        or p["opening_started"] != 37
        or p["maximum_new_starts"] != 4
        or p["ceiling"] != 200
        or p["protected_numeric_access"] is not False
    ):
        raise ValueError("P022_EXACT_LIVE_AUTHORITY_MISMATCH")
    for r in p["protected_refs"] + [
        p["design"],
        p["audit_gate"],
        p["input_contract"],
        p["previous_journal"],
    ]:
        checked(r)
    prior = failed_history()
    if (
        len(prior) != 2
        or prior[-1]["global_started_pairs"] != 37
        or prior[-1]["status"] != "FAILED"
        or prior[-1]["run_id"] != RUNS[0]
    ):
        raise ValueError("STOP_LEDGER_MISMATCH")
    pointer = json.loads(POINTER.read_text())
    if pointer["real_journal"] != str(JOURNAL):
        checked(p["previous_pointer"])
        if rows() or digest(POINTER) != p["previous_pointer"]["sha256"]:
            raise ValueError("P022_POINTER_CHAIN")
    elif pointer["plan"]["sha256"] != digest(plan):
        raise ValueError("P022_POINTER_PLAN")
    history = rows()
    own = [r for r in history if r["run_id"] == run_id]
    if own and own[-1]["status"] in {"COMPLETED", "FAILED"}:
        raise ValueError("P022_TERMINAL_NO_RETRY")
    if not own:
        complete = [r["run_id"] for r in history if r["status"] == "COMPLETED"]
        if complete != list(RUNS[: RUNS.index(run_id)]) or any(
            r["status"] == "FAILED" for r in history
        ):
            raise ValueError("P022_EXACT_ORDER_REQUIRED")
    return p


def append(plan: Path, approval: Path, run_id: str, status: str, detail: dict) -> None:
    p = ensure(plan, approval, run_id)
    history = rows()
    count = 37 + sum(r["status"] == "STARTED" for r in history) + int(status == "STARTED")
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
                schema_version=11,
                package="P022_REPAIR_V1",
                runs=list(RUNS),
                plan=ref(plan),
                previous_pointer=p["previous_pointer"],
            ),
        )
    atomic_replace_json(
        POINTER,
        dict(
            schema_version=11,
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
