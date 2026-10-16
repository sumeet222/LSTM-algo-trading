"""Two approved HF20 pairs using the existing shared epoch and D6g engine."""

from __future__ import annotations

import argparse
import io
import json
import platform
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import atomic_new, digest, now, write_json
from .controlled_loss import LossPolicy
from .hf20_source import SYMBOLS
from .hf20_training_authority import IDS, append, ensure, reference
from .hf20_training_data import TrainingView, fit_scale, load_views
from .neural_engine import SharedLSTM, batch_prediction, optimizer, seed_all, session_batches
from .neural_health import g6_summary
from .neural_lifecycle import EarlyStop, epoch_pass, state_hash


def stamp() -> dict:
    current = pd.Timestamp.now(tz="UTC")
    return dict(UTC=current.isoformat(), ET=current.tz_convert("America/New_York").isoformat())


def checkpoint(path: Path, model: SharedLSTM, binding: dict) -> dict:
    """Safe CPU float32 tensor-only payload; exact binding checked before reload."""
    state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
    if any(v.dtype != torch.float32 or not bool(torch.isfinite(v).all()) for v in state.values()):
        raise ValueError("HF20_CHECKPOINT_FINITE_FLOAT32_REQUIRED")
    stream = io.BytesIO()
    torch.save(dict(binding=binding, model=state), stream)
    atomic_new(path, stream.getvalue())
    manifest = dict(binding=binding, checkpoint=reference(path), bytes=path.stat().st_size)
    write_json(path.with_suffix(".manifest.json"), manifest)
    return manifest


def reload_checkpoint(path: Path, expected: dict, manifest: dict) -> SharedLSTM:
    if manifest["binding"] != expected or digest(path) != manifest["checkpoint"]["sha256"]:
        raise ValueError("HF20_CHECKPOINT_SOURCE_TARGET_ORDER_STAGE_SCALE_DENIED")
    body = torch.load(path, map_location="cpu", weights_only=True)
    if (
        not isinstance(body, dict)
        or body.get("binding") != expected
        or not isinstance(body.get("model"), dict)
    ):
        raise ValueError("HF20_CHECKPOINT_BODY_DENIED")
    model = SharedLSTM()
    state, schema = body["model"], model.state_dict()
    if set(state) != set(schema) or any(
        not isinstance(state[k], torch.Tensor)
        or state[k].shape != v.shape
        or state[k].dtype != torch.float32
        or state[k].device.type != "cpu"
        or not bool(torch.isfinite(state[k]).all())
        for k, v in schema.items()
    ):
        raise ValueError("HF20_CHECKPOINT_TENSOR_SCHEMA_DENIED")
    model.load_state_dict(state, strict=True)
    model.eval()
    return model


def scores(model: SharedLSTM, view: TrainingView, policy: LossPolicy) -> pd.DataFrame:
    model.eval()
    records = []
    with torch.no_grad():
        for pos in session_batches(len(view.sessions), 42, 1, shuffle=False):
            batch = view.batch(pos)
            # Exactly one inverse, including T2; saved CSV is already canonical.
            values = policy.canonical(batch_prediction(model, batch))
            for j, day in enumerate(batch.ids):
                for o in (1, 2):
                    if not bool(batch.origins[j, o - 1]):
                        continue
                    row = view.source.rows.loc[
                        view.source.rows.session.eq(day) & view.source.rows.origin.eq(o)
                    ].iloc[0]
                    for i, symbol in enumerate(SYMBOLS):
                        records.append(
                            dict(
                                session=day,
                                origin=o,
                                symbol=symbol,
                                symbol_index=i,
                                source_key=f"{day}:{o}:{symbol}",
                                target=float(batch.targets[j, o - 1, i]),
                                score=float(values[j, o - 1, i]),
                                day_index=int(row.day_index),
                                forecast_cutoff_UTC=str(row.feature_cutoff_UTC),
                                forecast_issuance_UTC=str(row.forecast_issuance_UTC),
                                entry_proxy_reference_UTC=str(row.entry_proxy_reference_UTC),
                                exit_proxy_reference_UTC=str(row.exit_proxy_reference_UTC),
                                label_maturity_UTC=str(row.label_maturity_UTC),
                                preparation_id=view.source.preparation_id,
                                recipe_id=view.source.recipe_id,
                                target_id="TG20_HF20_CROSS_SECTIONAL_V1",
                                inverse_count=int(policy.arm == "T2"),
                                score_units="CANONICAL_TG20",
                                stage="REFIT_FINAL",
                            )
                        )
    return pd.DataFrame(records)


def flatten(records: list[dict], stage: str) -> pd.DataFrame:
    rows = []
    for r in records:
        rows.append(
            dict(
                stage=stage,
                epoch=r["epoch"],
                canonical_training_MSE=r["mean_session_mse"],
                optimizer_objective=r["optimizer_objective"],
                seconds=r["seconds"],
                optimizer_steps=r["optimizer_steps"],
                validation_MSE=r.get("validation_MSE"),
                validation_seconds=r.get("validation_seconds"),
                selected=r.get("qualifying", False),
                score_std=r["score_std"],
                target_abs_max=r["target_abs_max"],
                target_abs_p99=r["target_abs_p99"],
                loss_top1pct=r["loss_concentration"]["0.01"],
                loss_top5pct=r["loss_concentration"]["0.05"],
                **(r["gradients"] or {}),
            )
        )
    return pd.DataFrame(rows)


def run(plan_path: Path, approval: Path, run_id: str, out: Path) -> None:
    started, timestamps = time.monotonic(), stamp()
    p = ensure(plan_path, approval, run_id)
    if out.exists():
        raise ValueError("HF20_IMMUTABLE_RUN_DIRECTORY_EXISTS")
    load_started = time.monotonic()
    views = load_views(Path(p["input_contract"]["path"]))
    loading_seconds = time.monotonic() - load_started
    if {k: v.summary() for k, v in views.items()} != p["views"]:
        raise ValueError("HF20_INPUT_MASK_CHANGED_BEFORE_START")
    scale_started = time.monotonic()
    scales = {s: fit_scale(views[s], s) for s in ("inner_train", "refit")}
    if scales != p["scales"]:
        raise ValueError("HF20_SCALE_CHANGED_BEFORE_START")
    scale_seconds = time.monotonic() - scale_started
    # Thread count is fixed in the approved execution plan, with no real-data tuning.
    torch.set_num_threads(p["cpu_threads"])
    torch.set_num_interop_threads(1)
    arm = "T2" if run_id == IDS[1] else "C0"
    policies = {
        s: LossPolicy(arm, scale=scales[s]["scale"] if arm == "T2" else 1.0) for s in scales
    }
    deadline = time.monotonic() + max(
        0.0, (pd.Timestamp(p["fit_deadline"]) - pd.Timestamp.now(tz="UTC")).total_seconds()
    )
    if deadline - time.monotonic() < p["minimum_pair_reserve_seconds"]:
        raise TimeoutError("HF20_INSUFFICIENT_WHOLE_PAIR_RESERVE_BEFORE_START")
    out.mkdir(parents=True)
    append(
        plan_path, approval, run_id, "STARTED", dict(start=timestamps, code_sha256=p["code_sha256"])
    )
    calibration, refit, batches = [], [], []
    runtime: dict = dict(
        run_id=run_id,
        started=timestamps,
        source_input_loading_seconds=loading_seconds,
        actual_T2_parameter_fitting_seconds=scale_seconds,
        recipe_application="SEALED_PRECOMPUTED_TRAIN_ONLY",
        calibration_train_seconds=0.0,
        validation_selection_seconds=0.0,
        refit_train_seconds=0.0,
        inference_seconds=0.0,
        artifact_write_reload_seconds=0.0,
    )
    try:
        seed_all(42)
        model = SharedLSTM()
        initial = state_hash(model)
        opt = optimizer(model)
        selector = EarlyStop()
        best = None
        while selector.status == "CALIBRATING":
            ensure(plan_path, approval, run_id)
            e = selector.epoch + 1
            r = epoch_pass(
                model,
                views["inner_train"],
                e,
                42,
                opt,
                policy=policies["inner_train"],
                batch_sink=lambda b: batches.append(dict(stage="calibration", **b)),
                deadline=deadline,
            )
            runtime["calibration_train_seconds"] += r["seconds"]
            val = epoch_pass(
                model,
                views["inner_validation"],
                e,
                42,
                policy=policies["inner_train"],
                deadline=deadline,
            )
            runtime["validation_selection_seconds"] += val["seconds"]
            qualifies = selector.observe(val["mean_session_mse"])
            r.update(
                validation_MSE=val["mean_session_mse"],
                validation_seconds=val["seconds"],
                qualifying=qualifies,
            )
            calibration.append(r)
            if qualifies:
                best = {k: v.detach().clone() for k, v in model.state_dict().items()}
            print(
                json.dumps(
                    dict(
                        run_id=run_id,
                        stage="calibration",
                        epoch=e,
                        objective=r["optimizer_objective"],
                        canonical_validation_MSE=val["mean_session_mse"],
                        seconds=r["seconds"],
                    )
                ),
                flush=True,
            )
        if best is None:
            raise ValueError("HF20_NO_SELECTED_CHECKPOINT")
        model.load_state_dict(best)
        artifact_started = time.monotonic()
        common = dict(
            run_id=run_id,
            architecture="TM0",
            parameters=6433,
            seed=42,
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
        cb = dict(
            **common,
            stage="CALIBRATION_SELECTED",
            recipe_id=views["inner_train"].source.recipe_id,
            scale=scales["inner_train"] if arm == "T2" else None,
        )
        cm = checkpoint(out / "calibration_selected.pt", model, cb)
        reloaded = reload_checkpoint(out / "calibration_selected.pt", cb, cm)
        if state_hash(model) != state_hash(reloaded):
            raise ValueError("HF20_CALIBRATION_RELOAD_CHANGED")
        runtime["artifact_write_reload_seconds"] += time.monotonic() - artifact_started
        append(
            plan_path,
            approval,
            run_id,
            "CALIBRATED",
            dict(selected_epoch=selector.selected, status=selector.status),
        )
        seed_all(42)
        final = SharedLSTM()
        fresh_initial = state_hash(final)
        refit_opt = optimizer(final)
        if initial != fresh_initial or refit_opt.state or final is model or refit_opt is opt:
            raise ValueError("HF20_FRESH_REFIT_INVARIANT")
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
                42,
                refit_opt,
                policy=policies["refit"],
                batch_sink=lambda b: batches.append(dict(stage="refit", **b)),
                deadline=deadline,
            )
            refit.append(r)
            runtime["refit_train_seconds"] += r["seconds"]
            print(
                json.dumps(
                    dict(
                        run_id=run_id,
                        stage="refit",
                        epoch=e,
                        objective=r["optimizer_objective"],
                        seconds=r["seconds"],
                    )
                ),
                flush=True,
            )
        artifact_started = time.monotonic()
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
            raise ValueError("HF20_REFIT_CPU_RELOAD_NOT_EXACT")
        runtime["artifact_write_reload_seconds"] += time.monotonic() - artifact_started
        inference_started = time.monotonic()
        prediction = scores(loaded, views["development"], policies["refit"])
        runtime["inference_seconds"] = time.monotonic() - inference_started
        if (
            len(prediction) != 7320
            or len(prediction[["session", "origin"]].drop_duplicates()) != 366
        ):
            raise ValueError("HF20_DEVELOPMENT_POPULATION_MISMATCH")
        artifact_started = time.monotonic()
        prediction.to_csv(out / "predictions_development.csv", index=False)
        flatten(calibration, "calibration").to_csv(out / "calibration_epochs.csv", index=False)
        flatten(refit, "refit").to_csv(out / "refit_epochs.csv", index=False)
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
        result = dict(
            status="COMPLETED",
            run_id=run_id,
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
        )
        write_json(out / "run_result.json", result)
        runtime["artifact_write_reload_seconds"] += time.monotonic() - artifact_started
        append(
            plan_path,
            approval,
            run_id,
            "COMPLETED",
            dict(result=reference(out / "run_result.json")),
        )
    except Exception as exc:
        runtime.update(exception_type=type(exc).__name__, exception=str(exc))
        write_json(out / "failure.json", dict(type=type(exc).__name__, message=str(exc), at=now()))
        append(
            plan_path, approval, run_id, "FAILED", dict(reason=type(exc).__name__, message=str(exc))
        )
        raise
    finally:
        runtime.update(
            finished=stamp(),
            worker_wall_seconds=time.monotonic() - started,
            neural_fitting_seconds=runtime["calibration_train_seconds"]
            + runtime["refit_train_seconds"],
            calibration_epochs=len(calibration),
            refit_epochs=len(refit),
            calibration_steps=sum(r["optimizer_steps"] for r in calibration),
            refit_steps=sum(r["optimizer_steps"] for r in refit),
            per_epoch_seconds={
                s: dict(
                    first=rr[0]["seconds"],
                    last=rr[-1]["seconds"],
                    median=float(np.median([r["seconds"] for r in rr])),
                )
                for s, rr in [("calibration", calibration), ("refit", refit)]
                if rr
            },
            cpu=platform.machine(),
            device="CPU_FLOAT32",
            python=platform.python_version(),
            torch=torch.__version__,
            numpy=np.__version__,
            threads=torch.get_num_threads(),
            interop_threads=torch.get_num_interop_threads(),
            peak_RSS_bytes=int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
            * (1 if sys.platform == "darwin" else 1024),
        )
        write_json(out / "training_actual_runtime.json", runtime)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--run-id", choices=IDS)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(json.dumps(dict(status="NO_FITTING", optimizer_steps=0, planned=list(IDS))))
        return 0
    if args.approval is None or args.run_id is None or args.out is None:
        raise ValueError("HF20_LIVE_APPROVAL_RUN_AND_NEW_OUTPUT_REQUIRED")
    run(args.plan, args.approval, args.run_id, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
