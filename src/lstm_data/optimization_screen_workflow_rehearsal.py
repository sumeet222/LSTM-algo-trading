"""Explicitly non-authorizing P024 end-to-end rehearsal: zero optimizer step calls."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

import numpy as np
import torch

from . import optimization_screen_recovery_diagnostics as diagnostics
from .config import write_json
from .controlled_loss import LossPolicy
from .hf1m_ft16_source import checked, ref
from .hf1m_training_run import predictions
from .neural_engine import batch_prediction, clip
from .neural_lifecycle import state_hash
from .objective_screen_source import scoped_view
from .optimization_screen import ScreenStop, make_model, make_optimizer
from .optimization_screen_recovery_authority import (
    JOURNAL,
    RUNS,
    VARIANTS,
    code_binding,
    ensure,
    require_complete_gate,
    require_rehearsal_gate,
)
from .optimization_screen_recovery_supplement import supplement
from .optimization_screen_run import measured_epoch, persist, save_optimizer, save_reload
from .optimization_screen_supplement import read_updates
from .visualization.hf1m_long import LongStudy

ORIGINAL = Path("reports/experiments/ta024_hf1m_long_optimization_2026-10-23_preparation_v3")


def blocked(path: Path, arm: str) -> bool:
    """No exception suppression for numerical checks; only explicit negative gate probes."""
    try:
        require_rehearsal_gate(path, arm)
    except (FileNotFoundError, ValueError):
        return True
    return False


def rehearse(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=False)
    (out / ".gitignore").write_text("*\n!.gitignore\n")
    before = {
        str(p): ref(p)
        for p in (
            Path("configs/CURRENT_EXPERIMENT_REGISTRY.json"),
            Path("reports/audit/track_a_real_pairs_v13_p024.jsonl"),
            ORIGINAL / "HF1M-LONG-TM0-LRLOW-S42-DEV1/run_result.json",
            ORIGINAL / "HF1M-LONG-TM0-DROP0-S42-DEV1/failure.json",
        )
    }
    if JOURNAL.exists():
        raise ValueError("P024_REHEARSAL_REQUIRES_NO_RECOVERY_STARTS")
    old = json.loads((ORIGINAL / "experiment_design.json").read_text())
    for r in old["protected_refs"]:
        checked(r)
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    study = LongStudy.discover(Path.cwd())
    views = {role: scoped_view(study, role, stage=7) for role in old["views"]}
    if {k: v.summary() for k, v in views.items()} != old["views"]:
        raise ValueError("P024_REHEARSAL_SOURCE_POPULATION_MISMATCH")
    plan_path = out / "REHEARSAL_PLAN_NOT_AUTHORITY.json"
    write_json(
        plan_path,
        dict(
            scope="REHEARSAL_ONLY",
            code=code_binding(),
            protected_refs=old["protected_refs"],
            views=old["views"],
            runs=list(RUNS),
        ),
    )
    not_approval = out / "NOT_A_TRAINING_APPROVAL.json"
    write_json(not_approval, dict(status="NOT_AN_APPROVAL", purpose="zero-step QA only"))
    # Check the original bug against all actual LRLOW update records and optimizer states.
    lr_result = json.loads((ORIGINAL / "HF1M-LONG-TM0-LRLOW-S42-DEV1/run_result.json").read_text())
    updates = read_updates(checked(lr_result["optimizer_telemetry"]))
    if any(value != [0.0003, 0.0003] for value in updates.lr):
        raise ValueError("P024_REAL_LRLOW_EXACT_LR_FAILED")
    for key in ("calibration_stop_optimizer", "refit_final_optimizer"):
        groups = torch.load(checked(lr_result[key]), weights_only=True)["param_groups"]
        if [g["lr"] for g in groups] != [0.0003, 0.0003]:
            raise ValueError("P024_REAL_LRLOW_OPTIMIZER_MISMATCH")
    records = []
    with patch.object(
        torch.optim.AdamW, "step", side_effect=AssertionError("FORBIDDEN_OPTIMIZER_STEP")
    ) as step:
        for index, (v, run_id) in enumerate(zip(VARIANTS, RUNS, strict=True)):
            if index:
                require_rehearsal_gate(
                    out / (VARIANTS[index - 1].arm + "_immediate_complete.json"),
                    VARIANTS[index - 1].arm,
                )
            public = out / run_id
            private = out / "private" / run_id
            public.mkdir()
            private.mkdir(parents=True)
            gate_path = out / (v.arm + "_immediate_complete.json")
            if not blocked(gate_path, v.arm):
                raise ValueError("P024_MISSING_GATE_NOT_BLOCKED")
            model = make_model(v)
            initial = state_hash(model)
            opt = make_optimizer(model, v)
            # One real whole-session backward pass; step is never invoked.
            batch = views["inner_train"].batch(tuple(range(16)))
            model.train()
            raw = batch_prediction(model, batch)
            policy = LossPolicy("T2", scale=views["inner_train"].source.fit["t2_scale"])
            objective = policy.objective(raw, batch.targets, batch.origins, stock_count=20)
            objective.mean().backward()
            norm = clip(model)
            if not np.isfinite(norm) or opt.state or state_hash(model) != initial:
                raise ValueError("P024_ZERO_UPDATE_BACKWARD_INVARIANT")
            # Unchanged checkpoint/data imply identical deterministic dropoutOFF metrics.
            # Reuse ONE measured train/validation pass through the12 selector observations,
            # explicitly recording reuse rather than inventing12 numerical passes.
            train = measured_epoch(model, views["inner_train"], 1, v, None, private)
            val = measured_epoch(model, views["inner_validation"], 1, v, None, private)
            selector = ScreenStop(improvement=v.improvement)
            epochs = []
            while selector.status == "CALIBRATING":
                e = selector.epoch + 1
                if state_hash(model) != initial:
                    raise ValueError("P024_REHEARSAL_WEIGHTS_CHANGED")
                qualifies = selector.observe(val["original_mse"])
                record = dict(
                    phase="calibration",
                    training=dict(train, epoch=e),
                    validation=dict(val, epoch=e),
                    qualifies=qualifies,
                    selector=asdict(selector),
                    model_state_hash=initial,
                    scope="REHEARSAL_ONLY",
                    fixed_checkpoint_pass_reused=True,
                )
                epochs.append(record)
                persist(public, record, epochs)
            calibration, loaded = save_reload(
                private / "calibration_selected.pt",
                model,
                v,
                dict(scope="REHEARSAL_ONLY", run_id=run_id),
            )
            cal_opt = save_optimizer(private / "calibration_stop_optimizer.pt", opt)
            final = make_model(v)
            refit_opt = make_optimizer(final, v)
            if state_hash(final) != initial or refit_opt.state:
                raise ValueError("P024_REHEARSAL_FRESH_REFIT")
            # This stationary zero-update replay selects1, hence one zero-update refit pass.
            if selector.selected != 1 or selector.epoch != 12:
                raise ValueError("P024_STATIONARY_SELECTOR_REPLAY")
            fit_record = dict(
                phase="refit",
                training=measured_epoch(final, views["refit"], 1, v, None, private),
                model_state_hash=initial,
                scope="REHEARSAL_ONLY",
            )
            epochs.append(fit_record)
            persist(public, fit_record, epochs)
            fit, reloaded = save_reload(
                private / "refit_final.pt", final, v, dict(scope="REHEARSAL_ONLY", run_id=run_id)
            )
            artifacts = []
            reloads = []
            for role, view in views.items():
                a_model, b_model, checkpoint = (
                    (model, loaded, calibration)
                    if role.startswith("inner")
                    else (final, reloaded, fit)
                )
                p = LossPolicy("T2", scale=view.source.fit["t2_scale"])
                identity = dict(
                    run_id=run_id,
                    arm=v.arm,
                    seed=v.seed,
                    scope="REHEARSAL_ONLY",
                    checkpoint_sha256=checkpoint["sha256"],
                    selected_epoch=1,
                )
                a, b = (
                    predictions(a_model, view, p, identity),
                    predictions(b_model, view, p, identity),
                )
                if not a.equals(b):
                    raise ValueError("P024_REHEARSAL_RELOAD_NOT_EXACT")
                path = private / (role + "_predictions.parquet")
                a.to_parquet(path, index=False)
                artifacts.append(ref(path))
                metrics = measured_epoch(b_model, view, 1, v, None, private, suffix="_checkpoint")
                write_json(public / (role + "_checkpoint_metrics.json"), metrics)
                reloads.append(dict(role=role, rows=len(a), max_reload_error=0.0))
                print(
                    json.dumps(
                        dict(
                            arm=v.arm, role=role, status="PASS_REHEARSAL_EXPORT", optimizer_steps=0
                        )
                    ),
                    flush=True,
                )
            telemetry = private / "optimizer_updates.jsonl"
            telemetry.write_text("")
            result = dict(
                status="REHEARSAL_ONLY_COMPLETE",
                scope="REHEARSAL_ONLY",
                run_id=run_id,
                epochs=epochs,
                selector=asdict(selector),
                initial_hash=initial,
                refit_initial_hash=state_hash(final),
                calibration=calibration,
                refit=fit,
                calibration_stop_optimizer=cal_opt,
                refit_final_optimizer=save_optimizer(
                    private / "refit_final_optimizer.pt", refit_opt
                ),
                calibration_steps=0,
                refit_steps=0,
                optimizer_telemetry=ref(telemetry),
                artifacts=artifacts,
                variant=asdict(v),
            )
            rp = public / "run_result.json"
            write_json(rp, result)
            # Only the research-journal lookup is replaced with an explicit read-only test fixture.
            # All numeric diagnosis, target/source reconstruction and receipt writers are real.
            fixture = [
                dict(
                    run_id=run_id,
                    status="COMPLETED",
                    scope="REHEARSAL_ONLY",
                    detail=dict(result=ref(rp)),
                )
            ]
            with patch.object(diagnostics, "rows", return_value=fixture):
                diagnostics.diagnose(plan_path, v.arm, out / (v.arm + "_diagnostics"))
            if not blocked(gate_path, v.arm):
                raise ValueError("P024_CORE_ONLY_GATE_NOT_BLOCKED")
            failed = out / (v.arm + "_failed_gate_probe.json")
            write_json(failed, dict(status="STOP_" + v.arm, scope="REHEARSAL_ONLY"))
            if not blocked(failed, v.arm):
                raise ValueError("P024_FAILED_GATE_NOT_BLOCKED")
            supplement(plan_path, v.arm)
            require_rehearsal_gate(gate_path, v.arm)
            try:
                require_complete_gate(gate_path, v.arm)
            except ValueError:
                pass
            else:
                raise ValueError("P024_REHEARSAL_GATE_ACCEPTED_FOR_REAL_START")
            try:
                ensure(plan_path, not_approval, run_id)
            except ValueError as error:
                if "REHEARSAL_CANNOT" not in str(error):
                    raise
            else:
                raise ValueError("P024_REHEARSAL_PLAN_ACCEPTED_FOR_REAL_START")
            records.append(
                dict(
                    arm=v.arm,
                    status="PASS_ZERO_STEP_WORKFLOW",
                    calibration_observations=12,
                    cached_fixed_checkpoint_metrics=True,
                    refit_passes=1,
                    backward_batches=1,
                    optimizer_step_calls=0,
                    weights_unchanged=True,
                    full_role_exports=reloads,
                    diagnostics_gate=ref(gate_path),
                    missing_gate_blocks=True,
                    core_only_blocks=True,
                    failed_gate_blocks=True,
                    production_guard_rejects_rehearsal=True,
                )
            )
            print(
                json.dumps(dict(arm=v.arm, status="PASS_COMPLETE_ZERO_STEP_WORKFLOW")), flush=True
            )
        if step.call_count:
            raise ValueError("P024_OPTIMIZER_STEP_ATTEMPTED")
    for r in before.values():
        checked(r)
    if JOURNAL.exists():
        raise ValueError("P024_REHEARSAL_CREATED_REAL_JOURNAL")
    write_json(
        out / "workflow_rehearsal_receipt.json",
        dict(
            status="PASS_COMPLETE_ZERO_STEP_WORKFLOW",
            scope="REHEARSAL_ONLY",
            checks=records,
            optimizer_step_calls=0,
            research_starts=0,
            actual_ledger=46,
            original_records_preserved=before,
            failed46_preserved=True,
            lrlow_exact_lr_updates_verified=len(updates),
            hyperparameter_tolerance=0,
            protected_numeric_access=False,
            authority_fixture="journal lookup only; no live approval fabricated",
            state_machine=(
                "real selector on reused stationary checkpoint metrics; not learning curves"
            ),
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    rehearse(parser.parse_args().out)
