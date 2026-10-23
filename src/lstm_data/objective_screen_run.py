"""P022 four fixed candidate starts. Every optimizer step requires exact live authority."""

from __future__ import annotations

import argparse
import json
import math
import resource
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import fingerprint, now, write_json
from .hf1m_ft16_source import ref
from .hf1m_training_data import TrainingView
from .hf1m_training_run import distribution
from .neural_engine import (
    SessionBatch,
    SharedLSTM,
    clip,
    optimizer,
    session_batches,
    session_losses,
)
from .neural_lifecycle import state_hash
from .objective_screen_authority import append, ensure
from .objective_screen_loss import ARMS, RUNS, Objective, model_for
from .objective_screen_metrics import classification, regression
from .objective_screen_source import ordered_targets, scoped_view
from .visualization.hf1m_long import LongStudy


@dataclass
class Selector:
    epoch: int = 0
    selected: int = 0
    best: float = math.inf
    raw_best: float = math.inf
    raw_epoch: int = 0
    patience: int = 0
    status: str = "CALIBRATING"

    def observe(self, value: float) -> bool:
        if self.status != "CALIBRATING" or not math.isfinite(value) or value < 0:
            raise ValueError("P022_VALID_SELECTION_METRIC")
        self.epoch += 1
        qualifies = value <= 0.999 * self.best
        if value < self.raw_best:
            self.raw_best, self.raw_epoch = value, self.epoch
        if qualifies:
            self.best, self.selected, self.patience = value, self.epoch, 0
        else:
            self.patience += 1
        if self.epoch >= 12 and self.patience >= 10:
            self.status = "PATIENCE_STOP"
        elif self.epoch >= 60:
            self.status = "MAX_EPOCHS"
        return qualifies


def forward(model: SharedLSTM, batch: SessionBatch, arm: str) -> torch.Tensor:
    valid = batch.inputs[batch.origins]
    output = model(valid.reshape(-1, 48, 16))
    if arm == "E1":
        result = torch.zeros((*batch.targets.shape, 3), dtype=output.dtype)
        result[batch.origins] = output.reshape(-1, 20, 3)
    else:
        result = torch.zeros_like(batch.targets)
        result[batch.origins] = output.reshape(-1, 20)
    return result


def epoch_pass(
    model: SharedLSTM,
    view: TrainingView,
    epoch: int,
    policy: Objective,
    opt: torch.optim.AdamW | None = None,
    telemetry: Path | None = None,
) -> dict:
    """Streaming durable per-batch telemetry; never replay a failed calibration."""
    model.train(opt is not None)
    started = time.monotonic()
    objectives = []
    mse = []
    aux = []
    pair = []
    ordering = []
    pre = []
    post = []
    outputs = []
    targets = []
    dates = []
    order = []
    exact_labels = ordered_targets(view).TG20.to_numpy(dtype=np.float64).reshape(-1, 20)
    for number, positions in enumerate(
        session_batches(len(view.sessions), 42, epoch, shuffle=opt is not None), 1
    ):
        batch = view.batch(positions)
        exact_batch = torch.zeros(batch.targets.shape, dtype=torch.float64)
        for day, k in enumerate(positions):
            for origin in view.positions_by_session[k]:
                exact_batch[day, int(view.origin_slots[origin])] = torch.from_numpy(
                    exact_labels[origin].copy()
                )
        order.extend(batch.ids)
        with torch.set_grad_enabled(opt is not None):
            raw = forward(model, batch, policy.arm)
            terms = policy.contributions(raw, batch.targets, batch.origins, exact_batch)
            losses = terms["total"].sum(dim=(1, 2))
            if not bool(torch.isfinite(losses).all()):
                raise ValueError("P022_NONFINITE_LOSS")
            if policy.arm != "E1":
                canonical = policy.recipe["scale"] * torch.sinh(raw)
                mse.extend(
                    session_losses(canonical, batch.targets, batch.origins, stock_count=20)
                    .detach()
                    .tolist()
                )
                z = torch.asinh(batch.targets / policy.recipe["scale"])
                aux.extend(session_losses(raw, z, batch.origins, stock_count=20).detach().tolist())
            else:
                aux.extend(
                    (terms["raw"] * terms["ordinary_weight"]).sum(dim=(1, 2)).detach().tolist()
                )
            if policy.arm == "R1":
                i, j = torch.triu_indices(20, 20, offset=1)
                true = torch.sign(exact_batch[..., i] - exact_batch[..., j])
                valid = true.ne(0)
                correct = (torch.sign(raw[..., i] - raw[..., j]) == true) & valid
                by_origin = correct.sum(dim=-1) / valid.sum(dim=-1).clamp_min(1)
                by_day = (by_origin * batch.origins).sum(dim=1) / batch.origins.sum(dim=1)
                ordering.extend(by_day.detach().tolist())
            if opt is not None:
                opt.zero_grad(set_to_none=True)
                losses.mean().backward()
                pre.append(clip(model))
                norm = torch.sqrt(
                    sum(
                        (p.grad.square().sum() for p in model.parameters() if p.grad is not None),
                        torch.tensor(0.0),
                    )
                )
                post.append(float(norm))
                opt.step()
                if any(not bool(torch.isfinite(p).all()) for p in model.parameters()):
                    raise ValueError("P022_NONFINITE_WEIGHTS")
        objectives.extend(losses.detach().tolist())
        pair.extend(terms["pairwise"].sum(dim=(1, 2)).detach().tolist())
        outputs.append(
            raw.detach()[batch.origins].numpy().reshape(-1, 3 if policy.arm == "E1" else 1)
        )
        targets.append(exact_batch[batch.origins].numpy().reshape(-1))
        dates.extend(
            d for k, d in enumerate(batch.ids) for _ in range(int(batch.origins[k].sum()) * 20)
        )
        if telemetry:
            row = dict(
                epoch=epoch,
                batch=number,
                role=view.split,
                optimizer_step=opt is not None,
                objective=float(losses.detach().mean()),
                sessions=len(batch.ids),
                preclip=pre[-1] if opt else None,
                postclip=post[-1] if opt else None,
                lr=opt.param_groups[0]["lr"] if opt else None,
                at=now(),
            )
            with telemetry.open("a") as stream:
                stream.write(json.dumps(row, sort_keys=True) + "\n")
                stream.flush()
    if len(order) != len(view.sessions) or len(set(order)) != len(order):
        raise ValueError("P022_EXACT_SESSION_EPOCH")
    raw_np = np.concatenate(outputs)
    y = np.concatenate(targets)
    day = np.asarray(dates)
    if policy.arm == "E1":
        p = torch.softmax(torch.from_numpy(raw_np), dim=-1).numpy().astype(float)
        measures = classification(y, p, day, policy.recipe)
    else:
        pred = (
            (policy.recipe["scale"] * torch.sinh(torch.from_numpy(raw_np[:, 0])))
            .numpy()
            .astype(float)
        )
        measures = regression(y, pred, day)
    result = dict(
        epoch=epoch,
        role=view.split,
        optimized_objective=float(np.mean(objectives)),
        original_mse=float(np.mean(mse)) if mse else None,
        auxiliary_unweighted_loss=float(np.mean(aux)),
        scaled_pairwise_objective=float(np.mean(pair)),
        pairwise_ordering_accuracy=float(np.mean(ordering)) if ordering else None,
        optimizer_steps=len(pre),
        sessions=len(order),
        seconds=time.monotonic() - started,
        nonfinite_count=0,
        order_sha256=fingerprint(order),
        forward_state="online pre-update dropoutON" if opt else "fixed checkpoint dropoutOFF",
        output_units="logits NEG/NORMAL/POS" if policy.arm == "E1" else "z",
        metrics=measures,
        output_distribution=distribution(raw_np.reshape(-1), "output"),
    )
    if pre:
        result.update(
            preclip=distribution(pre, "norm"),
            postclip=distribution(post, "norm"),
            clipped_count=sum(x > 1 for x in pre),
            clipped_denominator=len(pre),
            clipped_fraction=float(np.mean(np.asarray(pre) > 1)),
            learning_rate=0.001,
        )
    return result


def predict(model: SharedLSTM, view: TrainingView, arm: str, identity: dict) -> pd.DataFrame:
    """Final checkpoint inference with raw logits/z and original64 canonical target."""
    model.eval()
    chunks = []
    with torch.inference_mode():
        for positions in session_batches(len(view.source.rows), 42, 1, shuffle=False):
            batch = view.origin_batch(positions)
            raw = model(torch.from_numpy(batch["x"].reshape(-1, 48, 16)))
            chunks.append(raw.numpy().reshape(-1, 3 if arm == "E1" else 1))
    raw = np.concatenate(chunks)
    frame = ordered_targets(view)
    if arm == "E1":
        p = torch.softmax(torch.from_numpy(raw), dim=-1).numpy()
        for k, name in enumerate(["NEG", "NORMAL", "POS"]):
            frame["logit_" + name] = raw[:, k]
            frame["p_" + name] = p[:, k]
        frame["signed_event_score"] = p[:, 2] - p[:, 0]
    else:
        frame["raw_net_output"] = raw[:, 0]
        frame["pred_original_TG20"] = (
            view.source.fit["t2_scale"] * torch.sinh(torch.from_numpy(raw[:, 0]))
        ).numpy()
        frame["inverse_count"] = 1
    for key, value in identity.items():
        frame[key] = value
    frame["partition"] = view.split
    frame["arm"] = arm
    frame["seed"] = 42
    if frame.session_date_et.ge("2026-01-01").any():
        raise ValueError("P022_PROTECTED_EXPORT")
    return frame


def save_checkpoint(path: Path, model: SharedLSTM, binding: dict, arm: str) -> dict:
    if path.exists():
        raise ValueError("P022_CHECKPOINT_IMMUTABLE")
    torch.save({"state_dict": model.state_dict(), "binding": binding}, path)
    reloaded = model_for(arm)
    saved = torch.load(path, map_location="cpu", weights_only=True)
    reloaded.load_state_dict(saved["state_dict"])
    if saved["binding"] != binding or state_hash(model) != state_hash(reloaded):
        raise ValueError("P022_CHECKPOINT_RELOAD")
    return ref(path)


def storage_bytes(roots: list[Path]) -> int:
    return sum(
        p.stat().st_size
        for root in roots
        for p in root.rglob("*")
        if p.is_file() and not p.is_symlink()
    )


def run(plan: Path, approval: Path, run_id: str) -> None:
    p = ensure(plan, approval, run_id)
    initial_storage = storage_bytes([Path("data"), Path("artifacts"), Path("reports")])
    if initial_storage + p["resources"]["additional_storage_ceiling_bytes"] > 10_000_000_000:
        raise ValueError("P022_STORAGE_RESERVATION_EXCEEDS_10GB")
    arm = ARMS[RUNS.index(run_id)]
    started = time.monotonic()
    destination = Path(p["private_root"]) / run_id
    public = plan.parent / run_id
    # Exclusive creation makes concurrent/repeated invocations fail before reserving starts.
    destination.mkdir(parents=True, exist_ok=False)
    public.mkdir(exist_ok=False)
    study = LongStudy.discover(Path.cwd())
    views = {
        split: scoped_view(study, split, stage=2)
        for split in ["inner_train", "inner_validation", "refit"]
    }
    for split, v in views.items():
        if v.summary() != p["views"][split]:
            raise ValueError("P022_INPUT_PARITY")
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    policies = {
        split: Objective(arm, p["recipes"][v.source.fit_version]) for split, v in views.items()
    }
    append(plan, approval, run_id, "STARTED", {"execution": p["execution_sha256"]})
    try:
        model = model_for(arm)
        initial = state_hash(model)
        opt = optimizer(model)
        selector = Selector()
        best = None
        epochs = []
        telemetry = destination / "optimizer_batches.jsonl"
        while selector.status == "CALIBRATING":
            ensure(plan, approval, run_id)
            e = selector.epoch + 1
            training = epoch_pass(
                model, views["inner_train"], e, policies["inner_train"], opt, telemetry
            )
            validation = epoch_pass(
                model,
                views["inner_validation"],
                e,
                policies["inner_validation"],
                telemetry=telemetry,
            )
            selected_metric = (
                validation["optimized_objective"] if arm == "E1" else validation["original_mse"]
            )
            qualifies = selector.observe(selected_metric)
            if qualifies:
                best = {k: v.detach().clone() for k, v in model.state_dict().items()}
            record = dict(
                phase="calibration",
                training=training,
                validation=validation,
                selector=asdict(selector),
                qualifies=qualifies,
            )
            epochs.append(record)
            write_json(public / "epochs_progress.json", epochs)
            print(
                json.dumps(
                    dict(
                        run_id=run_id,
                        epoch=e,
                        selection_metric=selected_metric,
                        selector=asdict(selector),
                    )
                ),
                flush=True,
            )
        if best is None:
            raise ValueError("P022_NO_SELECTED_CHECKPOINT")
        model.load_state_dict(best)
        common = dict(
            run_id=run_id,
            arm=arm,
            seed=42,
            plan_sha256=ref(plan)["sha256"],
            execution_sha256=p["execution_sha256"],
            input_contract=p["input_contract"],
            selected_epoch=selector.selected,
        )
        calibration = save_checkpoint(
            destination / "calibration_selected.pt",
            model,
            dict(**common, fit_version="inner", recipe=p["recipes"]["inner"]),
            arm,
        )
        append(
            plan,
            approval,
            run_id,
            "CALIBRATED",
            dict(checkpoint=calibration, selector=asdict(selector)),
        )
        for split in ["inner_train", "inner_validation"]:
            predict(
                model,
                views[split],
                arm,
                dict(run_id=run_id, checkpoint_sha256=calibration["sha256"]),
            ).to_parquet(destination / (split + "_predictions.parquet"), index=False)
        model = model_for(arm)
        if state_hash(model) != initial:
            raise ValueError("P022_FRESH_INIT")
        opt = optimizer(model)
        if opt.state:
            raise ValueError("P022_FRESH_OPTIMIZER")
        append(
            plan, approval, run_id, "REFITTING", dict(initial_hash=initial, optimizer_empty=True)
        )
        for e in range(1, selector.selected + 1):
            ensure(plan, approval, run_id)
            training = epoch_pass(model, views["refit"], e, policies["refit"], opt, telemetry)
            epochs.append(dict(phase="refit", training=training))
            write_json(public / "epochs_progress.json", epochs)
            print(
                json.dumps(
                    dict(
                        run_id=run_id,
                        phase="refit",
                        epoch=e,
                        objective=training["optimized_objective"],
                    )
                ),
                flush=True,
            )
        final = save_checkpoint(
            destination / "refit_final.pt",
            model,
            dict(**common, fit_version="refit", recipe=p["recipes"]["refit"]),
            arm,
        )
        frame = predict(
            model, views["refit"], arm, dict(run_id=run_id, checkpoint_sha256=final["sha256"])
        )
        frame.to_parquet(destination / "refit_predictions.parquet", index=False)
        write_json(public / "epochs.json", epochs)
        result = dict(
            status="COMPLETED",
            run_id=run_id,
            arm=arm,
            seed=42,
            plan=ref(plan),
            input_contract=p["input_contract"],
            calibration=calibration,
            refit=final,
            initial_hash=initial,
            selector=asdict(selector),
            calibration_epochs=selector.epoch,
            refit_epochs=selector.selected,
            parameters=sum(t.numel() for t in model.parameters()),
            elapsed_seconds=time.monotonic() - started,
            peak_rss_bytes_macos=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            * (1 if sys.platform == "darwin" else 1024),
            initial_storage_bytes=initial_storage,
            run_artifact_bytes=storage_bytes([destination, public]),
            artifacts={f.name: ref(f) for f in destination.iterdir() if f.is_file()},
            epochs=ref(public / "epochs.json"),
            development_numeric_access=False,
        )
        write_json(public / "run_result.json", result)
        append(plan, approval, run_id, "COMPLETED", dict(result=ref(public / "run_result.json")))
        write_json(
            plan.parent / f"stage_{3 + RUNS.index(run_id):02d}_{arm}_gate.json",
            dict(
                status="PASS_" + arm,
                run=ref(public / "run_result.json"),
                development="DEFERRED_STAGE7",
            ),
        )
        (plan.parent / f"P022_{arm}_TRAINING_AND_CHECKPOINT.md").write_text(
            f"# P022 {arm} training and checkpoint\n\nCompleted {run_id}. "
            f"Calibration {selector.epoch}epochs; selected {selector.selected}; "
            "fresh refit same count. "
            f"Raw best epoch{selector.raw_epoch}. "
            "Actual objective, gradients and selector history: "
            f"[{run_id}/epochs.json]({run_id}/epochs.json). Checkpoint identities and resources: "
            f"[{run_id}/run_result.json]({run_id}/run_result.json). "
            "Development comparison remains deferred until all four arms pass.\n"
        )
    except Exception as exc:
        append(
            plan, approval, run_id, "FAILED", dict(error_type=type(exc).__name__, error=str(exc))
        )
        write_json(
            public / "failure.json",
            dict(status="STOP_" + arm, error=repr(exc), no_retry=True, at=now()),
        )
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--run-id", choices=RUNS, required=True)
    args = parser.parse_args()
    run(args.plan, args.approval, args.run_id)
