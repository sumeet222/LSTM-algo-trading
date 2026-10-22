"""Typed seed123 lifecycle over the unchanged HF20 numerical and checkpoint engines."""

from __future__ import annotations

import argparse
import json
import platform
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import now, write_json
from .controlled_loss import LossPolicy
from .hf20_replication_authority import IDS, append, ensure
from .hf20_source import SYMBOLS
from .hf20_training_authority import reference
from .hf20_training_data import fit_scale, load_views
from .hf20_training_run import checkpoint, flatten, reload_checkpoint, scores, stamp
from .neural_engine import SharedLSTM, batch_prediction, optimizer, seed_all
from .neural_health import g6_summary
from .neural_lifecycle import EarlyStop, epoch_pass, state_hash

SEED = 123


def run(plan_path: Path, approval: Path, run_id: str, out: Path) -> None:
    """One charged calibration/refit pair; failures are terminal under this grant."""
    tick, started = time.monotonic(), stamp()
    p = ensure(plan_path, approval, run_id)
    if out.exists():
        raise ValueError("P017_IMMUTABLE_RUN_EXISTS")
    loading = time.monotonic()
    views = load_views(Path(p["input_contract"]["path"]))
    load_seconds = time.monotonic() - loading
    if {k: v.summary() for k, v in views.items()} != p["views"]:
        raise ValueError("P017_CHANGED_MASK_PRESTART")
    scale_tick = time.monotonic()
    scales = {s: fit_scale(views[s], s) for s in ("inner_train", "refit")}
    if scales != p["scales"]:
        raise ValueError("P017_CHANGED_STAGE_SCALE_PRESTART")
    scale_seconds = time.monotonic() - scale_tick
    torch.set_num_threads(p["cpu_threads"])
    torch.set_num_interop_threads(1)
    arm = "T2" if run_id == IDS[1] else "C0"
    policies = {
        s: LossPolicy(arm, scale=scales[s]["scale"] if arm == "T2" else 1.0) for s in scales
    }
    remaining = (pd.Timestamp(p["fit_deadline"]) - pd.Timestamp.now(tz="UTC")).total_seconds()
    if remaining < p["minimum_pair_reserve_seconds"]:
        raise TimeoutError("P017_INSUFFICIENT_PAIR_RESERVE")
    deadline = time.monotonic() + remaining
    out.mkdir(parents=True)
    append(plan_path, approval, run_id, "STARTED", dict(seed=SEED, started=started))
    calibration: list[dict] = []
    refit: list[dict] = []
    batches: list[dict] = []
    timing: dict[str, float] = dict(
        source_input_loading_seconds=load_seconds,
        actual_T2_parameter_fitting_seconds=scale_seconds,
        calibration_train_seconds=0.0,
        validation_selection_seconds=0.0,
        checkpoint_selection_seconds=0.0,
        refit_train_seconds=0.0,
        artifact_write_reload_seconds=0.0,
        inference_seconds=0.0,
    )
    try:
        seed_all(SEED)
        model = SharedLSTM()
        initial = state_hash(model)
        opt, selector = optimizer(model), EarlyStop()
        best = None
        while selector.status == "CALIBRATING":
            ensure(plan_path, approval, run_id)
            e = selector.epoch + 1
            r = epoch_pass(
                model,
                views["inner_train"],
                e,
                SEED,
                opt,
                policy=policies["inner_train"],
                deadline=deadline,
                batch_sink=lambda b: batches.append(dict(stage="calibration", **b)),
            )
            val = epoch_pass(
                model,
                views["inner_validation"],
                e,
                SEED,
                policy=policies["inner_train"],
                deadline=deadline,
            )
            timing["calibration_train_seconds"] += r["seconds"]
            timing["validation_selection_seconds"] += val["seconds"]
            selection_tick = time.monotonic()
            qualifies = selector.observe(val["mean_session_mse"])
            if qualifies:
                best = {k: v.detach().clone() for k, v in model.state_dict().items()}
            timing["checkpoint_selection_seconds"] += time.monotonic() - selection_tick
            r.update(
                validation_MSE=val["mean_session_mse"],
                validation_seconds=val["seconds"],
                qualifying=qualifies,
            )
            calibration.append(r)
            print(
                json.dumps(
                    dict(
                        run_id=run_id,
                        stage="calibration",
                        epoch=e,
                        validation_MSE=val["mean_session_mse"],
                        seconds=r["seconds"],
                    )
                ),
                flush=True,
            )
        if best is None:
            raise ValueError("P017_NO_SELECTED_CHECKPOINT")
        model.load_state_dict(best)
        common = dict(
            run_id=run_id,
            architecture="TM0",
            parameters=6433,
            seed=SEED,
            input_contract=p["input_contract"],
            preparation_id=views["refit"].source.preparation_id,
            source_revision=p["source_revision"],
            symbols=list(SYMBOLS),
            feature_id=p["feature_id"],
            target_id=p["target_id"],
            clock_id=p["clock_id"],
            code_sha256=p["code_sha256"],
            plan=reference(plan_path),
            selected_epoch=selector.selected,
            arm=arm,
            inverse="SCALE_TIMES_SINH_ONCE" if arm == "T2" else "IDENTITY",
            checkpoint_outputs="LOGITS",
        )
        artifact_tick = time.monotonic()
        cb = dict(
            **common,
            stage="CALIBRATION_SELECTED",
            recipe_id=views["inner_train"].source.recipe_id,
            scale=scales["inner_train"] if arm == "T2" else None,
        )
        cm = checkpoint(out / "calibration_selected.pt", model, cb)
        if state_hash(reload_checkpoint(out / "calibration_selected.pt", cb, cm)) != state_hash(
            model
        ):
            raise ValueError("P017_CALIBRATION_RELOAD_CHANGED")
        timing["artifact_write_reload_seconds"] += time.monotonic() - artifact_tick
        append(plan_path, approval, run_id, "CALIBRATED", dict(selection=vars(selector)))
        seed_all(SEED)
        final = SharedLSTM()
        refit_opt = optimizer(final)
        fresh_initial = state_hash(final)
        if fresh_initial != initial or refit_opt.state or final is model or refit_opt is opt:
            raise ValueError("P017_FRESH_REFIT_REQUIRED")
        append(
            plan_path,
            approval,
            run_id,
            "REFITTING",
            dict(fresh_initial_hash=fresh_initial, optimizer_state_empty=True),
        )
        for e in range(1, selector.selected + 1):
            ensure(plan_path, approval, run_id)
            r = epoch_pass(
                final,
                views["refit"],
                e,
                SEED,
                refit_opt,
                policy=policies["refit"],
                deadline=deadline,
                batch_sink=lambda b: batches.append(dict(stage="refit", **b)),
            )
            refit.append(r)
            timing["refit_train_seconds"] += r["seconds"]
        artifact_tick = time.monotonic()
        fb = dict(
            **common,
            stage="REFIT_FINAL",
            recipe_id=views["refit"].source.recipe_id,
            scale=scales["refit"] if arm == "T2" else None,
        )
        fm = checkpoint(out / "refit_final.pt", final, fb)
        loaded = reload_checkpoint(out / "refit_final.pt", fb, fm)
        final.eval()
        example = views["development"].batch((0,))
        with torch.no_grad():
            exact = torch.equal(batch_prediction(final, example), batch_prediction(loaded, example))
        if not exact or state_hash(final) != state_hash(loaded):
            raise ValueError("P017_EXACT_RELOAD_REQUIRED")
        timing["artifact_write_reload_seconds"] += time.monotonic() - artifact_tick
        inference_tick = time.monotonic()
        prediction = scores(loaded, views["development"], policies["refit"])
        timing["inference_seconds"] = time.monotonic() - inference_tick
        if (
            len(prediction) != 7320
            or len(prediction[["session", "origin"]].drop_duplicates()) != 366
        ):
            raise ValueError("P017_DEVELOPMENT_MASK_MISMATCH")
        prediction["run_id"], prediction["seed"] = run_id, SEED
        prediction.to_csv(out / "predictions_development.csv", index=False)
        for stage, records in (("calibration", calibration), ("refit", refit)):
            flatten(records, stage).to_csv(out / (stage + "_epochs.csv"), index=False)
        pd.concat([flatten(calibration, "calibration"), flatten(refit, "refit")]).to_csv(
            out / "gradient_health.csv", index=False
        )
        pd.DataFrame(batches).to_csv(out / "batch_telemetry.csv", index=False)
        write_json(
            out / "epoch_records.json",
            dict(calibration=calibration, refit=refit, selection=vars(selector)),
        )
        health = g6_summary(
            tuple(calibration), tuple(refit), float(prediction.score.std()), selector.status
        )
        write_json(
            out / "run_result.json",
            dict(
                status="COMPLETED",
                run_id=run_id,
                seed=SEED,
                arm=arm,
                selection=vars(selector),
                input_contract=p["input_contract"],
                plan=reference(plan_path),
                approval=reference(approval),
                code_sha256=p["code_sha256"],
                scales=scales,
                views=p["views"],
                health=health,
                initial_hash=initial,
                fresh_initial_hash=fresh_initial,
                fresh_optimizer=True,
                reload_exact=exact,
                calibration_checkpoint=cm,
                refit_checkpoint=fm,
                heldout_numeric_rows=0,
                inverse_count=int(arm == "T2"),
                score_units="CANONICAL_TG20",
                calibration_steps=sum(r["optimizer_steps"] for r in calibration),
                refit_steps=sum(r["optimizer_steps"] for r in refit),
                development_rows=len(prediction),
            ),
        )
        append(
            plan_path,
            approval,
            run_id,
            "COMPLETED",
            dict(result=reference(out / "run_result.json")),
        )
    except Exception as exc:
        write_json(out / "failure.json", dict(type=type(exc).__name__, message=str(exc), at=now()))
        append(
            plan_path, approval, run_id, "FAILED", dict(reason=type(exc).__name__, message=str(exc))
        )
        raise
    finally:
        if not (out / "epoch_records.json").exists():
            write_json(
                out / "epoch_records.json",
                dict(calibration=calibration, refit=refit, status="INCOMPLETE_TERMINAL_FAILURE"),
            )
            pd.DataFrame(batches).to_csv(out / "batch_telemetry.csv", index=False)
        write_json(
            out / "training_actual_runtime.json",
            dict(
                **timing,
                recipe_application="SEALED_PRECOMPUTED_TRAIN_ONLY_NO_NEW_PREPARATION",
                run_id=run_id,
                seed=SEED,
                started=started,
                finished=stamp(),
                worker_wall_seconds=time.monotonic() - tick,
                neural_fitting_seconds=timing["calibration_train_seconds"]
                + timing["refit_train_seconds"],
                calibration_epochs=len(calibration),
                refit_epochs=len(refit),
                calibration_steps=sum(r["optimizer_steps"] for r in calibration),
                refit_steps=sum(r["optimizer_steps"] for r in refit),
                cpu=platform.machine(),
                device="CPU_FLOAT32",
                python=platform.python_version(),
                torch=torch.__version__,
                numpy=np.__version__,
                threads=torch.get_num_threads(),
                interop_threads=torch.get_num_interop_threads(),
                peak_RSS_bytes=int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
                * (1 if sys.platform == "darwin" else 1024),
            ),
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--run-id", choices=IDS, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.approval is None:
        raise ValueError("P017_LIVE_APPROVAL_REQUIRED_ZERO_STEPS")
    run(args.plan, args.approval, args.run_id, args.out)


if __name__ == "__main__":
    main()
