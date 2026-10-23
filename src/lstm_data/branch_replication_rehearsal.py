"""P025 full-source zero-optimizer-step lifecycle rehearsal and immutable proposal seal."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from unittest.mock import patch

import torch

from .branch_replication_authority import JOURNAL, POINTER, code_binding, ensure, require_gate
from .branch_replication_diagnostics import diagnose
from .branch_replication_run import lifecycle
from .branch_replication_spec import ARMS, P024, RUNS
from .config import digest, fingerprint, now, write_json
from .hf1m_ft16_source import checked, ref


def rehearse(out: Path, private: Path) -> None:
    """No journal reservations, optimizer calls, protected numeric reads or model claims."""
    started = time.monotonic()
    stage0_path = out / "stage_0_receipt.json"
    stage0 = json.loads(stage0_path.read_text())
    if stage0["status"] != "PASS_P025_IDENTITY_BASELINES" or private.exists():
        raise ValueError("P025_STAGE0_AND_NEW_REHEARSAL_NAMESPACE_REQUIRED")
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    pointer_before = ref(POINTER)
    if JOURNAL.exists():
        raise ValueError("P025_REHEARSAL_CANNOT_RESUME_EMPIRICAL_WORK")
    # Add independent byte verification of the common T2 context, without rerunning it.
    p024 = json.loads((P024 / "experiment_design.json").read_text())
    baseline_refs = {r["path"]: r for r in stage0["baseline_refs"]}
    for r in p024["baseline_refs"]:
        checked(r)
        baseline_refs[r["path"]] = r
    for r in list(stage0["source_hashes"].values()) + stage0["protected_refs"]:
        checked(r)
    private.mkdir(parents=True)
    (private / ".gitignore").write_text("*\n!.gitignore\n")
    binding = code_binding()
    draft = dict(
        scope="REHEARSAL_ONLY",
        code=binding,
        recipes=stage0["recipes"],
        scientific_definitions=stage0["scientific_definitions"],
        input_contract=stage0["input_contract"],
        baseline_refs=list(baseline_refs.values()),
        opening_started=51,
        maximum_new_starts=0,
        runs=list(RUNS),
    )
    draft_path = private / "rehearsal_plan.json"
    write_json(draft_path, draft)
    gates, blocked, calls = [], [], 0

    def forbidden_step(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise RuntimeError("P025_REHEARSAL_OPTIMIZER_STEP_FORBIDDEN")

    with patch.object(torch.optim.AdamW, "step", forbidden_step):
        for arm in ARMS:
            if gates:
                require_gate(
                    private / (ARMS[0] + "_diagnostics/gate.json"), ARMS[0], rehearsal=True
                )
            print(f"REHEARSAL_ONLY {arm}: full lifecycle, AdamW.step blocked", flush=True)
            result_path = lifecycle(draft_path, arm, private / arm, rehearsal=True)
            gate = diagnose(draft, result_path, private / (arm + "_diagnostics"), rehearsal=True)
            require_gate(private / (arm + "_diagnostics/gate.json"), arm, rehearsal=True)
            # A rehearsal PASS can never satisfy the live scientific stage controller.
            try:
                require_gate(private / (arm + "_diagnostics/gate.json"), arm)
            except ValueError:
                blocked.append(arm + "_REHEARSAL_CANNOT_AUTHORIZE_NEXT_MODEL")
            else:
                raise ValueError("P025_REHEARSAL_GATE_ESCAPED")
            gates.append(ref(private / (arm + "_diagnostics/gate.json")))
            print(f"REHEARSAL_ONLY {arm}: {gate['status']}, four roles, exact cases", flush=True)
    try:
        ensure(draft_path, None, RUNS[0])
    except ValueError:
        blocked.append("NO_APPROVAL_DENIED_BEFORE_RESERVATION")
    else:
        raise ValueError("P025_MISSING_APPROVAL_ESCAPED")
    for r in (
        list(stage0["source_hashes"].values())
        + list(baseline_refs.values())
        + stage0["protected_refs"]
    ):
        checked(r)
    if code_binding() != binding or ref(POINTER) != pointer_before or JOURNAL.exists() or calls:
        raise ValueError("P025_REHEARSAL_CHANGED_CODE_LEDGER_OR_WEIGHTS")
    write_json(
        out / "stage_1_receipt.json",
        dict(
            status="PASS_P025_ZERO_STEP_REHEARSAL_AND_PROPOSAL",
            at=now(),
            scope="REHEARSAL_ONLY",
            optimizer_step_calls=calls,
            neural_starts=0,
            ledger=51,
            execution_sha256=fingerprint(binding),
            code=binding,
            scientific_definitions=stage0["scientific_definitions"],
            stage0=ref(stage0_path),
            gates=gates,
            blocked=blocked,
            source_files_verified=len(stage0["source_hashes"]),
            baseline_files_verified=len(baseline_refs),
            protected_hash_only=True,
            all_role_exports=8,
            stationary_progress_replay=(
                "12 calibration receipts, two physical zero-step refit epochs per arm; "
                "not learning curves"
            ),
            seconds=time.monotonic() - started,
            previous_pointer=pointer_before,
        ),
    )
    plan: dict = dict(
        schema_version=1,
        package="P025",
        status="PREPARED_AWAITING_APPROVAL",
        scope="RESEARCH_CANDIDATE",
        runs=list(RUNS),
        opening_started=51,
        maximum_new_starts=2,
        ceiling=200,
        protected_numeric_access=False,
        code=binding,
        execution_sha256=fingerprint(binding),
        scientific_definitions=stage0["scientific_definitions"],
        input_contract=stage0["input_contract"],
        recipes=stage0["recipes"],
        stage0=ref(stage0_path),
        stage1=ref(out / "stage_1_receipt.json"),
        previous_pointer=stage0["previous_pointer"],
        previous_journal=stage0["previous_journal"],
        baseline_refs=list(baseline_refs.values()),
        protected_refs=stage0["protected_refs"],
        source_hashes=stage0["source_hashes"],
        private_root=str(private.parent / "approved_runs"),
        failure_policy="charged permanently; stop; no automatic retry; E1 complete gate before QR1",
        approval_required="Separate exact live response; Package025 opening paragraph and Stage1",
    )
    write_json(out / "experiment_design.json", plan)
    print(
        json.dumps(
            dict(
                status=plan["status"],
                proposal_sha256=digest(out / "experiment_design.json"),
                execution_sha256=plan["execution_sha256"],
                scientific_sha256=plan["scientific_definitions"]["sha256"],
                starts=0,
                ledger=51,
            )
        ),
        flush=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    args = parser.parse_args()
    rehearse(args.out, args.private)
