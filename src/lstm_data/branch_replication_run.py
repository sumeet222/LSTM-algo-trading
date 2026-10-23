"""P025 shared full lifecycle. Real updates require exact live authority before STARTED."""

from __future__ import annotations

import argparse
import io
import json
import time
from dataclasses import asdict
from pathlib import Path

import pandas as pd
import torch

from . import branch_replication_authority as authority
from .branch_replication_diagnostics import diagnose, exact_optimizer
from .branch_replication_engine import (
    epoch_pass,
    model_for,
    peak_rss_bytes,
    predict,
    save_checkpoint,
)
from .branch_replication_spec import ARMS, ROLES, RUNS
from .config import atomic_new, digest, fingerprint, write_json
from .hf1m_ft16_source import ref
from .neural_engine import optimizer
from .neural_lifecycle import state_hash
from .objective_screen_run import Selector, record_epoch, storage_bytes
from .objective_screen_source import scoped_view
from .visualization.hf1m_long import LongStudy


def lifecycle(
    plan_path: Path,
    arm: str,
    destination: Path,
    *,
    approval: Path | None = None,
    rehearsal: bool = False,
) -> Path:
    """One arm, fresh same-seed refit, durable progress, exact full-role exports."""
    plan = json.loads(plan_path.read_text())
    run_id = RUNS[ARMS.index(arm)]
    if not rehearsal:
        if approval is None:
            raise ValueError("P025_APPROVAL_REQUIRED_BEFORE_RESERVATION")
        authority.ensure(plan_path, approval, run_id)
    elif plan.get("scope") != "REHEARSAL_ONLY":
        raise ValueError("P025_EXPLICIT_REHEARSAL_PLAN_REQUIRED")
    if destination.exists():
        raise ValueError("P025_IMMUTABLE_NEW_RUN_DIRECTORY_REQUIRED")
    initial_storage = storage_bytes([Path("data"), Path("artifacts"), Path("reports")])
    if initial_storage + 1_000_000_000 > 10_000_000_000:
        raise ValueError("P025_STORAGE_HEADROOM_REQUIRED_BEFORE_START")
    if not rehearsal:
        assert approval is not None
        authority.append(plan_path, approval, run_id, "STARTED", dict(destination=str(destination)))
    try:
        destination.mkdir(parents=True)
        (destination / ".gitignore").write_text("*\n!.gitignore\n")
        started = time.monotonic()
        study = LongStudy.discover(Path.cwd())
        train, validation = (scoped_view(study, role, stage=2) for role in ROLES[:2])
        model = model_for(arm)
        initial = state_hash(model)
        opt = optimizer(model)
        settings = exact_optimizer(model, opt)
        selector, epochs, selected = Selector(), [], None

        def checkpoint_binding(phase: str, epoch: int) -> dict:
            version = "inner" if phase == "calibration" else "refit"
            return dict(
                arm=arm,
                seed=123,
                phase=phase,
                epoch=epoch,
                scope=plan.get("scope", "RESEARCH_CANDIDATE"),
                proposal_sha256=digest(plan_path),
                scientific_sha256=plan["scientific_definitions"]["sha256"],
                execution_sha256=fingerprint(authority.code_binding()),
                input_contract_sha256=plan["input_contract"]["sha256"],
                recipe_sha256=fingerprint(plan["recipes"][arm][version]),
            )

        update_authority = (plan_path, approval, run_id) if approval else None
        if rehearsal:
            # Full population backward and validation, followed by an explicitly
            # stationary selector/receipt replay. These are never learning curves.
            tr = epoch_pass(
                model,
                train,
                arm,
                plan["recipes"][arm]["inner"],
                1,
                opt,
                destination / "updates.jsonl",
                update=not rehearsal,
                authority=update_authority,
            )
            va = epoch_pass(
                model,
                validation,
                arm,
                plan["recipes"][arm]["inner"],
                1,
                None,
                destination / "validation.jsonl",
                update=False,
            )
        while selector.status == "CALIBRATING":
            epoch = selector.epoch + 1
            if not rehearsal:
                tr = epoch_pass(
                    model,
                    train,
                    arm,
                    plan["recipes"][arm]["inner"],
                    epoch,
                    opt,
                    destination / "updates.jsonl",
                    update=not rehearsal,
                    authority=update_authority,
                )
                va = epoch_pass(
                    model,
                    validation,
                    arm,
                    plan["recipes"][arm]["inner"],
                    epoch,
                    None,
                    destination / "validation.jsonl",
                    update=False,
                )
            qualifies = selector.observe(va["optimized_objective"])
            row = dict(
                phase="calibration",
                training=dict(tr, epoch=epoch),
                validation=dict(va, epoch=epoch),
                qualifies=qualifies,
                selector=asdict(selector),
                stationary_zero_step_replay=rehearsal,
            )
            epochs.append(row)
            record_epoch(destination, epochs)
            if qualifies:
                selected, _ = save_checkpoint(
                    destination / f"calibration_{epoch:03d}.pt",
                    model,
                    arm,
                    checkpoint_binding("calibration", epoch),
                )
        if selected is None:
            raise ValueError("P025_SELECTED_CHECKPOINT_REQUIRED")
        stream = io.BytesIO()
        torch.save(opt.state_dict(), stream)
        atomic_new(destination / "calibration_stop_optimizer.pt", stream.getvalue())
        if not rehearsal:
            assert approval is not None
            authority.append(
                plan_path,
                approval,
                run_id,
                "CALIBRATED",
                dict(selector=asdict(selector), checkpoint=selected),
            )
        del train, validation, model, opt
        model = model_for(arm)
        if state_hash(model) != initial:
            raise ValueError("P025_FRESH_REFIT_SAME_INITIALIZATION")
        refit_initial = state_hash(model)
        opt = optimizer(model)
        exact_optimizer(model, opt)
        if opt.state:
            raise ValueError("P025_FRESH_OPTIMIZER_REQUIRED")
        if not rehearsal:
            assert approval is not None
            authority.append(
                plan_path, approval, run_id, "REFITTING", dict(selected=selector.selected)
            )
        view = scoped_view(study, "refit", stage=2)
        refit_epochs = 2 if rehearsal else selector.selected
        for epoch in range(1, refit_epochs + 1):
            tr = epoch_pass(
                model,
                view,
                arm,
                plan["recipes"][arm]["refit"],
                epoch,
                opt,
                destination / "updates.jsonl",
                update=not rehearsal,
                authority=update_authority,
            )
            epochs.append(dict(phase="refit", training=tr, stationary_zero_step_replay=rehearsal))
            record_epoch(destination, epochs)
        final, loaded = save_checkpoint(
            destination / "refit_final.pt",
            model,
            arm,
            checkpoint_binding("refit", refit_epochs),
        )
        buffer = io.BytesIO()
        torch.save(opt.state_dict(), buffer)
        atomic_new(destination / "optimizer_final.pt", buffer.getvalue())
        restored_optimizer = optimizer(loaded)
        restored_optimizer.load_state_dict(
            torch.load(destination / "optimizer_final.pt", weights_only=True)
        )
        exact_optimizer(loaded, restored_optimizer)
        if not rehearsal:
            for state in restored_optimizer.state.values():
                if not all(
                    bool(torch.isfinite(v).all())
                    for v in state.values()
                    if isinstance(v, torch.Tensor)
                ):
                    raise ValueError("P025_NONFINITE_OPTIMIZER_STATE")
        del opt, view, model, loaded, restored_optimizer
        populations = {}
        for role in ROLES:
            version = "inner" if role.startswith("inner") else "refit"
            checkpoint = selected if version == "inner" else final
            model = model_for(arm)
            model.load_state_dict(
                torch.load(Path(checkpoint["path"]), weights_only=True)["state_dict"]
            )
            # Save/reload another immutable checkpoint to exercise the same exporter.
            _, reload = save_checkpoint(
                destination / (role + "_export_reload.pt"),
                model,
                arm,
                dict(source_checkpoint=checkpoint),
            )
            view = scoped_view(study, role, stage=7)
            binding = dict(
                run_id=run_id,
                checkpoint_sha256=checkpoint["sha256"],
                input_contract_sha256=plan["input_contract"]["sha256"],
                scope=plan.get("scope", "RESEARCH_CANDIDATE"),
            )
            native = predict(model, view, arm, plan["recipes"][arm][version], binding)
            written = predict(reload, view, arm, plan["recipes"][arm][version], binding)
            pd.testing.assert_frame_equal(native, written, check_exact=True)
            path = destination / (role + ".parquet")
            native.to_parquet(path, index=False)
            pd.testing.assert_frame_equal(native, pd.read_parquet(path), check_exact=True)
            evaluation = epoch_pass(
                reload,
                view,
                arm,
                plan["recipes"][arm][version],
                1,
                None,
                destination / (role + "_fixed_batches.jsonl"),
                update=False,
            )
            populations[role] = dict(
                population=ref(path),
                binding=binding,
                fixed_objective=evaluation["optimized_objective"],
                reload_exact=True,
                summary=view.summary(),
            )
            del view, model, reload, native, written
        result = dict(
            status="COMPLETED_FIT_PENDING_IMMEDIATE_GATE",
            scope=plan.get("scope", "RESEARCH_CANDIDATE"),
            arm=arm,
            run_id=run_id,
            seed=123,
            parameters=6499,
            settings=settings,
            initial_hash=initial,
            refit_initial_hash=refit_initial,
            selector=asdict(selector),
            epochs=epochs,
            rehearsal_refit_epochs_override=2 if rehearsal else None,
            calibration=selected,
            refit=final,
            optimizer_final=ref(destination / "optimizer_final.pt"),
            calibration_stop_optimizer=ref(destination / "calibration_stop_optimizer.pt"),
            populations=populations,
            optimizer_telemetry=ref(destination / "updates.jsonl"),
            proposal_sha256=digest(plan_path),
            execution_sha256=fingerprint(authority.code_binding()),
            seconds=time.monotonic() - started,
            peak_rss_bytes=peak_rss_bytes(),
            storage_before=initial_storage,
        )
        final_storage = storage_bytes([Path("data"), Path("artifacts"), Path("reports")])
        if final_storage > 10_000_000_000 or final_storage - initial_storage > 1_000_000_000:
            raise ValueError("P025_STORAGE_LIMIT")
        result["storage_after"] = final_storage
        result_path = destination / "run_result.json"
        write_json(result_path, result)
        if not rehearsal:
            assert approval is not None
            authority.append(
                plan_path, approval, run_id, "COMPLETED", dict(result=ref(result_path))
            )
        return result_path
    except BaseException as error:
        if not rehearsal:
            assert approval is not None
            authority.append(
                plan_path,
                approval,
                run_id,
                "FAILED",
                dict(error_type=type(error).__name__, error=str(error)),
            )
        raise


def run(plan_path: Path, approval: Path, arm: str) -> None:
    """Run one approved arm and finish its complete gate before any next start."""
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    plan = json.loads(plan_path.read_text())
    run_id = RUNS[ARMS.index(arm)]
    result = lifecycle(plan_path, arm, Path(plan["private_root"]) / run_id, approval=approval)
    try:
        gate = diagnose(plan, result, Path(plan["private_root"]) / (arm + "_immediate_diagnostics"))
        write_json(plan_path.parent / (arm + "_immediate_gate.json"), gate)
    except BaseException as error:
        write_json(
            plan_path.parent / (arm + "_STOP_IMMEDIATE_GATE.json"),
            dict(status="STOP_" + arm, error=str(error)),
        )
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--arm", choices=ARMS, required=True)
    a = parser.parse_args()
    run(a.plan, a.approval, a.arm)
