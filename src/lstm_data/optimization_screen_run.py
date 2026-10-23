"""P024 reuses the P021 T2 epoch/export kernel, adding observational optimizer hooks."""

from __future__ import annotations

import argparse
import io
import json
import math
import resource
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import atomic_new, now, write_json
from .controlled_loss import LossPolicy
from .hf1m_ft16_source import checked, ref
from .hf1m_training_run import distribution, epoch_pass, predictions
from .neural_lifecycle import state_hash
from .objective_screen_run import storage_bytes
from .objective_screen_source import scoped_view
from .optimization_screen import (
    RUNS,
    VARIANTS,
    ScreenLSTM,
    ScreenStop,
    Variant,
    make_model,
    make_optimizer,
)
from .optimization_screen_authority import append, ensure
from .real_batch_authority import atomic_replace_json
from .visualization.hf1m_long import LongStudy


def peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if sys.platform == "darwin" else value * 1024


def save_optimizer(path: Path, opt: torch.optim.AdamW) -> dict:
    stream = io.BytesIO()
    torch.save(opt.state_dict(), stream)
    atomic_new(path, stream.getvalue())
    return ref(path)


def persist(public: Path, record: dict, epochs: list[dict]) -> None:
    """Only the progress snapshot is replaceable; epoch receipts remain exclusive."""
    phase, epoch = record["phase"], record["training"]["epoch"]
    directory = public / "epoch_receipts"
    directory.mkdir(exist_ok=True)
    write_json(directory / f"{phase}_{epoch:03d}.json", record)
    atomic_replace_json(public / "epochs_progress.json", dict(epochs=epochs))


class Telemetry:
    """Observe autograd/AdamW without changing tensors, RNG streams or update math."""

    def __init__(
        self, model: ScreenLSTM, opt: torch.optim.AdamW, path: Path, phase: str, epoch: int
    ) -> None:
        self.model, self.opt, self.path = model, opt, path
        self.phase, self.epoch, self.step = phase, epoch, 0
        self.raw: dict[str, float] = {}
        self.before: dict[str, torch.Tensor] = {}
        self.records: list[dict] = []
        self.handles = [p.register_hook(self.capture(n)) for n, p in model.named_parameters()]
        self.handles += [
            opt.register_step_pre_hook(self.pre),
            opt.register_step_post_hook(self.post),
        ]

    def capture(self, name: str):
        def observe(gradient: torch.Tensor) -> None:
            self.raw[name] = float(gradient.detach().square().sum())

        return observe

    def pre(self, opt, args, kwargs) -> None:
        self.before = {n: p.detach().clone() for n, p in self.model.named_parameters()}

    def post(self, opt, args, kwargs) -> None:
        self.step += 1
        groups = {
            "lstm_l" + str(i): [
                n
                for n, _ in self.model.named_parameters()
                if n.startswith("lstm.") and n.endswith("_l" + str(i))
            ]
            for i in range(self.model.lstm.num_layers)
        }
        groups["head"] = [n for n, _ in self.model.named_parameters() if n.startswith("head.")]
        pre = math.sqrt(sum(self.raw.values()))
        post = math.sqrt(
            sum(float(p.grad.square().sum()) for p in self.model.parameters() if p.grad is not None)
        )
        update = math.sqrt(
            sum(
                float((p.detach() - self.before[n]).square().sum())
                for n, p in self.model.named_parameters()
            )
        )
        weight = math.sqrt(sum(float(p.detach().square().sum()) for p in self.model.parameters()))
        if not np.isfinite([pre, post, update, weight]).all():
            raise ValueError("P024_NONFINITE_TELEMETRY")
        record = dict(
            phase=self.phase,
            epoch=self.epoch,
            batch=self.step,
            preclip_norm=pre,
            postclip_norm=post,
            update_norm=update,
            weight_norm=weight,
            lr=[g["lr"] for g in opt.param_groups],
            weight_decay=[g["weight_decay"] for g in opt.param_groups],
            module_preclip={
                k: math.sqrt(sum(self.raw[n] for n in names)) for k, names in groups.items()
            },
        )
        with self.path.open("a") as stream:
            stream.write(json.dumps(record, allow_nan=False) + "\n")
            stream.flush()
        self.records.append(record)
        self.raw.clear()

    def close(self) -> None:
        for handle in self.handles:
            handle.remove()


def measured_epoch(
    model: ScreenLSTM,
    view,
    epoch: int,
    v: Variant,
    opt: torch.optim.AdamW | None,
    private: Path,
    *,
    suffix: str = "",
) -> dict:
    telemetry = (
        Telemetry(model, opt, private / "optimizer_updates.jsonl", view.split, epoch)
        if opt
        else None
    )
    try:
        r, batches = epoch_pass(
            model, view, epoch, v.seed, LossPolicy("T2", scale=view.source.fit["t2_scale"]), opt
        )
    finally:
        if telemetry:
            telemetry.close()
    if telemetry:
        np.testing.assert_allclose(
            [b["preclip_norm"] for b in batches],
            [b["preclip_norm"] for b in telemetry.records],
            rtol=2e-6,
            atol=1e-7,
        )
        np.testing.assert_allclose(
            [b["postclip_norm"] for b in batches],
            [b["postclip_norm"] for b in telemetry.records],
            rtol=2e-6,
            atol=1e-7,
        )
        r["update_norm"] = distribution([b["update_norm"] for b in telemetry.records], "norm")
        r["weight_norm"] = distribution([b["weight_norm"] for b in telemetry.records], "norm")
    path = private / f"{view.split}_{epoch:03d}{suffix}_batches.parquet"
    if path.exists():
        raise ValueError("P024_IMMUTABLE_BATCH_RECEIPT")
    pd.DataFrame(batches).to_parquet(path, index=False)
    r["head_dropout"] = v.head_dropout
    r["learning_rate"] = v.learning_rate
    r["matrix_decay"] = v.matrix_decay
    r["forward_context"] = (
        "online pre-update, head dropout=" + str(v.head_dropout)
        if opt
        else "fixed checkpoint, dropout OFF"
    )
    return r


def save_reload(
    path: Path, model: ScreenLSTM, v: Variant, binding: dict
) -> tuple[dict, ScreenLSTM]:
    """Preserve RNG state: instantiation for read-only reload cannot alter the training stream."""
    if path.exists():
        raise ValueError("P024_IMMUTABLE_CHECKPOINT")
    stream = io.BytesIO()
    torch.save(dict(model=model.state_dict(), binding=binding, variant=asdict(v)), stream)
    atomic_new(path, stream.getvalue())
    with torch.random.fork_rng():
        loaded = ScreenLSTM(v)
    body = torch.load(path, weights_only=True)
    if body["binding"] != binding or body["variant"] != asdict(v):
        raise ValueError("P024_CHECKPOINT_BINDING")
    loaded.load_state_dict(body["model"])
    if state_hash(model) != state_hash(loaded):
        raise ValueError("P024_RELOAD_IDENTITY")
    return ref(path), loaded


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
    args = parser.parse_args()
    run(args.plan, args.approval, args.run_id)
