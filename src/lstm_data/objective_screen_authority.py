"""P022 exact four-start authority, append-only successor journal and fail-closed order."""

from __future__ import annotations

import json
from pathlib import Path

from .config import digest, fingerprint, now, write_json
from .hf1m_ft16_source import checked, ref
from .hf1m_training_recovery import read_rows as previous_rows
from .objective_screen_loss import RUNS
from .real_batch_authority import atomic_replace_json

POINTER = Path("configs/CURRENT_EXPERIMENT_REGISTRY.json")
JOURNAL = Path("reports/audit/track_a_real_pairs_v10_p022.jsonl")


def code_binding() -> dict[str, str]:
    names = [
        "objective_screen_source",
        "objective_screen_loss",
        "objective_screen_audit",
        "objective_screen_authority",
        "objective_screen_run",
        "objective_screen_metrics",
        "hf1m_training_data",
        "hf1m_ft16_loader",
        "neural_engine",
        "neural_lifecycle",
    ]
    return {name: digest(Path("src/lstm_data") / (name + ".py")) for name in names}


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
        if row["global_started_pairs"] != 36 + starts or row["effective_ceiling"] != 200:
            raise ValueError("P022_LEDGER_MISMATCH")
        states[name] = status
    return result


def ensure(plan: Path, approval: Path | None, run_id: str) -> dict:
    if approval is None:
        raise ValueError("P022_SEPARATE_LIVE_FOUR_RUN_APPROVAL_REQUIRED")
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
        or p["opening_started"] != 36
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
    prior = previous_rows(Path(p["previous_journal"]["path"]))
    if prior[-1]["global_started_pairs"] != 36 or prior[-1]["status"] != "COMPLETED":
        raise ValueError("STOP_LEDGER_MISMATCH")
    pointer = json.loads(POINTER.read_text())
    if pointer["real_journal"] != str(JOURNAL):
        checked(p["previous_pointer"])
        if rows():
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
    count = 36 + sum(r["status"] == "STARTED" for r in history) + int(status == "STARTED")
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
                schema_version=10,
                package="P022",
                runs=list(RUNS),
                plan=ref(plan),
                previous_pointer=p["previous_pointer"],
            ),
        )
    atomic_replace_json(
        POINTER,
        dict(
            schema_version=10,
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
