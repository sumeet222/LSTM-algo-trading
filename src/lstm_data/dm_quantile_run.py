"""P023 frozen fitting executor; exact live approval required before charged starts."""

from __future__ import annotations

import argparse
import json
import resource
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import write_json
from .dm_quantile_authority import append, ensure
from .dm_quantile_loss import ARMS, RUNS, draw_batch, draws, model_for, outputs, terms
from .hf1m_ft16_loader import load_model_input
from .hf1m_ft16_source import ref
from .hf1m_training_data import TrainingView
from .hf1m_training_run import distribution
from .neural_engine import clip, optimizer, session_batches
from .neural_lifecycle import state_hash
from .objective_screen_run import Selector, record_epoch, storage_bytes
from .objective_screen_source import ordered_targets


def epoch_pass(
    model,
    view: TrainingView,
    arm: str,
    recipe: dict,
    epoch: int,
    opt=None,
    telemetry: Path | None = None,
) -> dict:
    model.train(opt is not None)
    batches = (
        draws(recipe, epoch)
        if arm == "SS1" and opt is not None
        else [
            (ids, np.ones(len(ids), dtype=np.float32))
            for ids in session_batches(len(view.sessions), 42, epoch, shuffle=opt is not None)
        ]
    )
    session_losses = []
    mse = []
    components = []
    pre = []
    post = []
    seen = []
    weights = []
    for step, (ids, iw) in enumerate(batches, 1):
        batch = draw_batch(view, ids)
        with torch.set_grad_enabled(opt is not None):
            raw_valid = model(batch.inputs[batch.origins].reshape(-1, 48, 16))
            raw = torch.zeros((*batch.targets.shape, 3) if arm != "SS1" else batch.targets.shape)
            raw[batch.origins] = (
                raw_valid.reshape(-1, 20, 3) if arm != "SS1" else raw_valid.reshape(-1, 20)
            )
            loss = terms(raw, batch.targets, batch.origins, arm, recipe["scale"])
            corrected = loss["session_loss"] * torch.from_numpy(iw)
            projected = outputs(raw, arm, recipe["scale"])["y_hat"]
            by_origin = (projected - batch.targets).square().mean(dim=-1)
            mse.extend(
                ((by_origin * batch.origins).sum(dim=1) / batch.origins.sum(dim=1))
                .detach()
                .tolist()
            )
            ordinary = batch.origins[..., None, None] / (
                batch.origins.sum(dim=1)[:, None, None, None] * 20
            )
            components.extend((loss["components"] * ordinary).sum(dim=(1, 2)).detach().tolist())
            if not bool(torch.isfinite(corrected).all()):
                raise ValueError("P023_NONFINITE_LOSS")
            if opt is not None:
                opt.zero_grad(set_to_none=True)
                corrected.mean().backward()
                pre.append(clip(model))
                if not np.isfinite(pre[-1]):
                    raise ValueError("P023_NONFINITE_GRADIENT")
                norm = torch.sqrt(
                    sum(
                        (p.grad.square().sum() for p in model.parameters() if p.grad is not None),
                        torch.tensor(0.0),
                    )
                )
                post.append(float(norm))
                opt.step()
                if any(not bool(torch.isfinite(p).all()) for p in model.parameters()):
                    raise ValueError("P023_NONFINITE_WEIGHTS")
        session_losses.extend(corrected.detach().tolist())
        seen.extend(ids)
        weights.extend(iw.tolist())
        if telemetry:
            with telemetry.open("a") as stream:
                stream.write(
                    json.dumps(
                        dict(
                            epoch=epoch,
                            role=view.split,
                            batch=step,
                            sampled_positions=ids,
                            importance=iw.tolist(),
                            objective=float(corrected.detach().mean()),
                            optimizer_step=opt is not None,
                            preclip=pre[-1] if pre else None,
                            postclip=post[-1] if post else None,
                        )
                    )
                    + "\n"
                )
                stream.flush()
    if len(seen) != len(view.sessions):
        raise ValueError("P023_DRAW_COUNT")
    r: dict = dict(
        epoch=epoch,
        role=view.split,
        optimized_objective=float(np.mean(session_losses)),
        original_mse=float(np.mean(mse)),
        component_means=np.mean(components, axis=0).tolist(),
        optimizer_steps=len(pre),
        session_draws=len(seen),
        unique_sessions=len(set(seen)),
        duplicates=len(seen) - len(set(seen)),
        omitted=len(view.sessions) - len(set(seen)),
        importance_ESS=float(np.sum(weights) ** 2 / np.sum(np.square(weights))),
        importance_mean=float(np.mean(weights)),
        forward_state="online_dropoutON" if opt else "fixed_dropoutOFF",
    )
    if pre:
        r.update(
            preclip=distribution(pre, "norm"),
            postclip=distribution(post, "norm"),
            clipped_count=sum(x > 1 for x in pre),
            clipped_denominator=len(pre),
            clipped_fraction=float(np.mean(np.asarray(pre) > 1)),
            learning_rate=0.001,
            nonfinite_count=0,
        )
    return r


def predict(model, view: TrainingView, arm: str, checkpoint: dict) -> pd.DataFrame:
    model.eval()
    chunks = []
    with torch.inference_mode():
        for ids in session_batches(len(view.source.rows), 42, 1, shuffle=False):
            raw = model(torch.from_numpy(view.origin_batch(ids)["x"].reshape(-1, 48, 16)))
            chunks.append(raw)
    raw = torch.cat(chunks)
    f = ordered_targets(view)
    for i in range(1 if arm == "SS1" else 3):
        f[f"raw_{i}"] = raw.numpy().reshape(-1, 1 if arm == "SS1" else 3)[:, i]
    for key, value in outputs(raw, arm, view.source.fit["t2_scale"]).items():
        a = value.numpy()
        if a.ndim == 2:
            for i, tau in enumerate(["05", "50", "95"]):
                f[key + "_" + tau] = a[:, i]
        else:
            f[key] = a
    f["checkpoint_sha256"] = checkpoint["sha256"]
    f["arm"] = arm
    f["seed"] = 42
    f["partition"] = view.split
    f["inverse_count"] = 1
    return f


def save(path: Path, model, binding: dict, arm: str) -> dict:
    if path.exists():
        raise ValueError("P023_CHECKPOINT_EXISTS")
    torch.save(dict(state_dict=model.state_dict(), binding=binding), path)
    reloaded = model_for(arm)
    reloaded.load_state_dict(torch.load(path, weights_only=True)["state_dict"])
    if state_hash(model) != state_hash(reloaded):
        raise ValueError("P023_CHECKPOINT_RELOAD")
    return ref(path)


def run(plan_path: Path, approval: Path, run_id: str) -> None:
    plan = ensure(plan_path, approval, run_id)
    arm = ARMS[RUNS.index(run_id)]
    if (
        storage_bytes([Path("data"), Path("artifacts"), Path("reports")]) + 1_000_000_000
        > 10_000_000_000
    ):
        raise ValueError("P023_STORAGE_LIMIT")
    public = plan_path.parent / run_id
    private = Path(plan["private_root"]) / run_id
    public.mkdir(exist_ok=False)
    private.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    views = {
        role: TrainingView(
            load_model_input(
                Path(plan["input_contract"]["path"]),
                split=role,
                fit_version="inner" if role.startswith("inner") else "refit",
            ),
            role,
        )
        for role in ["inner_train", "inner_validation", "refit"]
    }
    for role, v in views.items():
        if v.summary() != plan["views"][role]:
            raise ValueError("P023_INPUT_PARITY")
    started = time.monotonic()
    append(plan_path, approval, run_id, "STARTED", dict(arm=arm))
    try:
        model = model_for(arm)
        initial = state_hash(model)
        opt = optimizer(model)
        selector = Selector()
        epochs = []
        best = None
        while selector.status == "CALIBRATING":
            ensure(plan_path, approval, run_id)
            e = selector.epoch + 1
            training = epoch_pass(
                model,
                views["inner_train"],
                arm,
                plan["recipes"]["inner"],
                e,
                opt,
                private / "batches.jsonl",
            )
            if arm == "SS1":
                training["fixed_population_objective"] = epoch_pass(
                    model, views["inner_train"], arm, plan["recipes"]["inner"], e
                )["optimized_objective"]
            validation = epoch_pass(
                model,
                views["inner_validation"],
                arm,
                plan["recipes"]["inner"],
                e,
                telemetry=private / "batches.jsonl",
            )
            metric = (
                validation["optimized_objective"] if arm == "QR1" else validation["original_mse"]
            )
            qualifies = selector.observe(metric)
            if qualifies:
                best = {k: v.detach().clone() for k, v in model.state_dict().items()}
            epochs.append(
                dict(
                    phase="calibration",
                    training=training,
                    validation=validation,
                    selector=asdict(selector),
                    qualifies=qualifies,
                )
            )
            record_epoch(public, epochs)
        if best is None:
            raise ValueError("P023_NO_CHECKPOINT")
        model.load_state_dict(best)
        binding = dict(
            run_id=run_id,
            plan=ref(plan_path),
            input_contract=plan["input_contract"],
            selected_epoch=selector.selected,
        )
        calibration = save(
            private / "calibration.pt", model, dict(**binding, recipe=plan["recipes"]["inner"]), arm
        )
        torch.save(opt.state_dict(), private / "optimizer_calibration_stop.pt")
        append(plan_path, approval, run_id, "CALIBRATED", dict(checkpoint=calibration))
        for role in ["inner_train", "inner_validation"]:
            predict(model, views[role], arm, calibration).to_parquet(
                private / (role + ".parquet"), index=False
            )
        model = model_for(arm)
        assert state_hash(model) == initial
        opt = optimizer(model)
        assert not opt.state
        append(plan_path, approval, run_id, "REFITTING", dict(initial_hash=initial))
        for e in range(1, selector.selected + 1):
            ensure(plan_path, approval, run_id)
            t = epoch_pass(
                model,
                views["refit"],
                arm,
                plan["recipes"]["refit"],
                e,
                opt,
                private / "batches.jsonl",
            )
            epochs.append(dict(phase="refit", training=t))
            record_epoch(public, epochs)
        final = save(
            private / "refit.pt", model, dict(**binding, recipe=plan["recipes"]["refit"]), arm
        )
        torch.save(opt.state_dict(), private / "optimizer_refit_final.pt")
        predict(model, views["refit"], arm, final).to_parquet(
            private / "refit.parquet", index=False
        )
        # Development is inference only; each arm's immediate diagnostics follow before next start.
        development = TrainingView(
            load_model_input(
                Path(plan["input_contract"]["path"]), split="development", fit_version="refit"
            ),
            "development",
        )
        predict(model, development, arm, final).to_parquet(
            private / "development.parquet", index=False
        )
        result = dict(
            status="COMPLETED_FIT_PENDING_IMMEDIATE_DIAGNOSTICS",
            run_id=run_id,
            arm=arm,
            calibration=calibration,
            refit=final,
            selector=asdict(selector),
            epochs=epochs,
            seconds=time.monotonic() - started,
            peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            artifacts=[ref(f) for f in private.iterdir() if f.is_file()],
        )
        write_json(public / "run_result.json", result)
        append(
            plan_path, approval, run_id, "COMPLETED", dict(result=ref(public / "run_result.json"))
        )
    except Exception as exc:
        append(plan_path, approval, run_id, "FAILED", dict(error=repr(exc)))
        raise


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--approval", type=Path, required=True)
    p.add_argument("--run-id", choices=RUNS, required=True)
    a = p.parse_args()
    run(a.plan, a.approval, a.run_id)
