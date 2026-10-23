"""P024 proposed repair executor: unchanged numerical lifecycle, strengthened live/gate routing."""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import asdict
from pathlib import Path

import torch

from .config import now, write_json
from .controlled_loss import LossPolicy
from .hf1m_ft16_source import checked, ref
from .hf1m_training_run import predictions
from .neural_lifecycle import state_hash
from .objective_screen_run import storage_bytes
from .objective_screen_source import scoped_view
from .optimization_screen import ScreenStop, make_model, make_optimizer
from .optimization_screen_recovery_authority import RUNS, VARIANTS, append, ensure
from .optimization_screen_run import (
    measured_epoch,
    peak_rss_bytes,
    persist,
    save_optimizer,
    save_reload,
)
from .visualization.hf1m_long import LongStudy


def run(plan_path: Path, approval: Path, run_id: str) -> None:
    p = ensure(plan_path, approval, run_id)
    v = VARIANTS[RUNS.index(run_id)]
    public, private = plan_path.parent / run_id, Path(p["private_root"]) / run_id
    if public.exists() or private.exists():
        raise ValueError("P024_NO_RESTART_EXISTING_RUN")
    if (
        storage_bytes([Path("data"), Path("artifacts"), Path("reports")]) + 2_000_000_000
        > 10_000_000_000
    ):
        raise ValueError("P024_STORAGE_LIMIT")
    stage0 = json.loads(checked(p["stage0"]).read_text())
    for r in stage0["source_hashes"].values():
        checked(r)
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    study = LongStudy.discover(Path.cwd())
    views = {
        role: scoped_view(study, role, stage=2)
        for role in ("inner_train", "inner_validation", "refit")
    }
    if any(view.summary() != p["views"][role] for role, view in views.items()):
        raise ValueError("P024_INPUT_POPULATION_CHANGED")
    public.mkdir(exist_ok=False)
    private.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    append(plan_path, approval, run_id, "STARTED", dict(variant=asdict(v)))
    try:
        model = make_model(v)
        initial = state_hash(model)
        opt = make_optimizer(model, v)
        selector, epochs, best = ScreenStop(improvement=v.improvement), [], None
        baseline_counterfactual = ScreenStop()
        while selector.status == "CALIBRATING":
            ensure(plan_path, approval, run_id)
            e = selector.epoch + 1
            training = measured_epoch(model, views["inner_train"], e, v, opt, private)
            validation = measured_epoch(model, views["inner_validation"], e, v, None, private)
            previous = selector.best
            qualifies = selector.observe(validation["original_mse"])
            # Counterfactual stops at its own first stop; later values are not its trajectory.
            if baseline_counterfactual.status == "CALIBRATING":
                baseline_counterfactual.observe(validation["original_mse"])
            record = dict(
                phase="calibration",
                training=training,
                validation=validation,
                qualifies=qualifies,
                selector=asdict(selector),
                model_state_hash=state_hash(model),
                counterfactual_001=asdict(baseline_counterfactual),
                relative_improvement=None
                if previous in (None, 0)
                else (previous - validation["original_mse"]) / previous,
            )
            if qualifies:
                best = {k: t.detach().clone() for k, t in model.state_dict().items()}
                # Persist every qualifying checkpoint, not only the last selected one.
                save_reload(
                    private / f"calibration_epoch_{e:03d}.pt",
                    model,
                    v,
                    dict(plan=ref(plan_path), run_id=run_id, epoch=e, role="calibration"),
                )
            epochs.append(record)
            persist(public, record, epochs)
            print(json.dumps(dict(run_id=run_id, **record)), flush=True)
            if peak_rss_bytes() > 2_000_000_000:
                raise ValueError("P024_RAM_LIMIT")
        if best is None:
            raise ValueError("P024_NO_SELECTED_MODEL")
        calibration_optimizer = save_optimizer(private / "calibration_stop_optimizer.pt", opt)
        model.load_state_dict(best)
        binding = dict(
            plan=ref(plan_path),
            run_id=run_id,
            variant=asdict(v),
            selected_epoch=selector.selected,
            source_revision=p["source_revision"],
            input_contract=p["input_contract"],
        )
        cal, loaded = save_reload(
            private / "calibration_selected.pt",
            model,
            v,
            dict(
                **binding,
                phase="calibration",
                recipe=ref(Path(study.contract["fit_recipes"]["path"])),
            ),
        )
        append(
            plan_path,
            approval,
            run_id,
            "CALIBRATED",
            dict(selector=asdict(selector), checkpoint=cal),
        )
        reload_checks, artifacts = [], []
        for role in ("inner_train", "inner_validation"):
            identity = dict(
                run_id=run_id,
                arm=v.arm,
                seed=v.seed,
                selected_epoch=selector.selected,
                checkpoint_sha256=cal["sha256"],
            )
            a = predictions(
                model,
                views[role],
                LossPolicy("T2", scale=views[role].source.fit["t2_scale"]),
                identity,
            )
            b = predictions(
                loaded,
                views[role],
                LossPolicy("T2", scale=views[role].source.fit["t2_scale"]),
                identity,
            )
            if not a.equals(b):
                raise ValueError("P024_CALIBRATION_RELOAD_PREDICTION")
            a.to_parquet(private / (role + "_predictions.parquet"), index=False)
            artifacts.append(ref(private / (role + "_predictions.parquet")))
            reload_checks.append(dict(role=role, rows=len(a), max_error=0.0))
        final = make_model(v)
        fresh = state_hash(final)
        refit_opt = make_optimizer(final, v)
        if fresh != initial or refit_opt.state:
            raise ValueError("P024_FRESH_REFIT_REQUIRED")
        append(
            plan_path, approval, run_id, "REFITTING", dict(initial_hash=fresh, optimizer_empty=True)
        )
        for e in range(1, selector.selected + 1):
            ensure(plan_path, approval, run_id)
            training = measured_epoch(final, views["refit"], e, v, refit_opt, private)
            record = dict(phase="refit", training=training, model_state_hash=state_hash(final))
            epochs.append(record)
            persist(public, record, epochs)
            print(json.dumps(dict(run_id=run_id, **record)), flush=True)
        fit, reloaded = save_reload(
            private / "refit_final.pt",
            final,
            v,
            dict(**binding, phase="refit", recipe=ref(Path(study.contract["fit_recipes"]["path"]))),
        )
        views["development"] = scoped_view(study, "development", stage=7)
        for role in ("refit", "development"):
            identity = dict(
                run_id=run_id,
                arm=v.arm,
                seed=v.seed,
                selected_epoch=selector.selected,
                checkpoint_sha256=fit["sha256"],
            )
            policy = LossPolicy("T2", scale=views[role].source.fit["t2_scale"])
            a, b = (
                predictions(final, views[role], policy, identity),
                predictions(reloaded, views[role], policy, identity),
            )
            if not a.equals(b):
                raise ValueError("P024_REFIT_RELOAD_PREDICTION")
            a.to_parquet(private / (role + "_predictions.parquet"), index=False)
            artifacts.append(ref(private / (role + "_predictions.parquet")))
            reload_checks.append(dict(role=role, rows=len(a), max_error=0.0))
        for role in ("refit", "inner_train", "inner_validation", "development"):
            fixed = measured_epoch(
                reloaded if role in ("refit", "development") else loaded,
                views[role],
                1,
                v,
                None,
                private,
                suffix="_checkpoint",
            )
            write_json(public / (role + "_checkpoint_metrics.json"), fixed)
        for r in p["protected_refs"]:
            checked(r)
        result = dict(
            status="COMPLETED",
            run_id=run_id,
            variant=asdict(v),
            selector=asdict(selector),
            baseline_counterfactual=asdict(baseline_counterfactual),
            epochs=epochs,
            initial_hash=initial,
            refit_initial_hash=fresh,
            fresh_optimizer_empty=True,
            calibration=cal,
            refit=fit,
            artifacts=artifacts,
            reload_checks=reload_checks,
            calibration_steps=math.ceil(2513 / 16) * selector.epoch,
            refit_steps=math.ceil(2980 / 16) * selector.selected,
            seconds=time.monotonic() - started,
            peak_rss_bytes=peak_rss_bytes(),
            parameters=sum(t.numel() for t in model.parameters()),
            plan=ref(plan_path),
            optimizer_telemetry=ref(private / "optimizer_updates.jsonl"),
            calibration_stop_optimizer=calibration_optimizer,
            refit_final_optimizer=save_optimizer(private / "refit_final_optimizer.pt", refit_opt),
        )
        write_json(public / "run_result.json", result)
        append(
            plan_path, approval, run_id, "COMPLETED", dict(result=ref(public / "run_result.json"))
        )
    except BaseException as error:
        write_json(
            public / "failure.json",
            dict(status="FAILED", at=now(), error_type=type(error).__name__, error=str(error)),
        )
        append(plan_path, approval, run_id, "FAILED", dict(failure=ref(public / "failure.json")))
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--run-id", choices=RUNS, required=True)
    a = parser.parse_args()
    run(a.plan, a.approval, a.run_id)
