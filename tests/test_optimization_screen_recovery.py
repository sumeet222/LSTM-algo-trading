"""P024 no-update repair oracles: numerical parity and complete-prior-gate enforcement."""

import ast
import inspect
import json
from pathlib import Path

import pytest

from lstm_data.config import fingerprint
from lstm_data.hf1m_ft16_source import ref
from lstm_data.optimization_screen import VARIANTS as ORIGINAL_VARIANTS
from lstm_data.optimization_screen_recovery_authority import (
    RUNS,
    VARIANTS,
    ensure,
    require_complete_gate,
    require_rehearsal_gate,
    validate,
)


def test_numerical_lifecycle_is_unchanged_and_only_five_declared_runs():
    from lstm_data.optimization_screen_recovery_run import run as repaired
    from lstm_data.optimization_screen_run import run as original

    a = ast.parse(inspect.getsource(original))
    b = ast.parse(inspect.getsource(repaired))
    assert ast.dump(a, include_attributes=False) == ast.dump(b, include_attributes=False)
    assert VARIANTS == ORIGINAL_VARIANTS[1:]
    assert len(RUNS) == 5 and RUNS[0].endswith("-DROP0-S42-DEV1-REPAIR1")


def test_core_gate_alone_cannot_permit_next_start(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("payload.txt").write_text("verified")
    evidence = ref(Path("payload.txt"))
    Path("base.json").write_text(json.dumps(dict(status="PASS_LRLOW", evidence=[evidence])))
    # The exact failure mode: core succeeded but supplemental receipt is missing/failed.
    with pytest.raises(FileNotFoundError):
        require_complete_gate(Path("complete.json"), "LRLOW")
    Path("complete.json").write_text(json.dumps(dict(status="STOP_LRLOW")))
    with pytest.raises(ValueError, match="COMPLETE_PRIOR"):
        require_complete_gate(Path("complete.json"), "LRLOW")
    Path("complete.json").write_text(
        json.dumps(
            dict(
                status="PASS_IMMEDIATE_LRLOW", base_gate=ref(Path("base.json")), evidence=[evidence]
            )
        )
    )
    require_complete_gate(Path("complete.json"), "LRLOW")
    Path("payload.txt").write_text("changed")
    with pytest.raises(ValueError, match="input bytes changed"):
        require_complete_gate(Path("complete.json"), "LRLOW")


def test_new_approval_is_required_and_old_six_run_response_is_rejected():
    p = Path("reports/experiments/ta024_hf1m_long_optimization_2026-10-23_preparation_v3")
    with pytest.raises(ValueError, match="LIVE_APPROVAL"):
        ensure(p / "experiment_design.json", None, RUNS[0])
    with pytest.raises(ValueError, match="EXACT_SCOPE"):
        ensure(p / "experiment_design.json", p / "live_approval.json", RUNS[0])


def test_recovery_charges_from46_and_blocks_every_retry_after_failure():
    history = []

    def event(status, name=RUNS[0], count=47):
        return dict(
            sequence=len(history) + 1,
            previous=fingerprint(history),
            run_id=name,
            status=status,
            global_started_pairs=count,
            effective_ceiling=200,
        )

    history.append(event("STARTED"))
    history.append(event("FAILED"))
    assert validate(history) == history
    with pytest.raises(ValueError):
        validate(history + [event("STARTED")])
    with pytest.raises(ValueError):
        validate(history + [event("STARTED", RUNS[1], 48)])


def test_complete_rehearsal_can_never_authorize_real_model(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("payload.txt").write_text("verified rehearsal only")
    evidence = ref(Path("payload.txt"))
    Path("base.json").write_text(
        json.dumps(dict(status="PASS_DROP0", scope="REHEARSAL_ONLY", evidence=[evidence]))
    )
    Path("complete.json").write_text(
        json.dumps(
            dict(
                status="PASS_IMMEDIATE_DROP0",
                scope="REHEARSAL_ONLY",
                base_gate=ref(Path("base.json")),
                evidence=[evidence],
            )
        )
    )
    require_rehearsal_gate(Path("complete.json"), "DROP0")
    with pytest.raises(ValueError, match="REHEARSAL_CANNOT_AUTHORIZE"):
        require_complete_gate(Path("complete.json"), "DROP0")
