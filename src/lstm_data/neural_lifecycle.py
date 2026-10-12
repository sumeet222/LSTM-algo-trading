"""D6g chronological synthetic calibration/refit and compact training health."""

from __future__ import annotations

import json
import math
import platform
import time
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .baseline_authority import replay_permission, verify
from .baseline_fit import FitData, Preparation, prepare
from .baseline_inputs import BaselineInput
from .baseline_ridge import RidgeOrigin, Stage, adequacy, fitting_origins, windows
from .config import digest, fingerprint, write_json
from .ft0_transforms import identity
from .neural_artifacts import MODE, PairIdentity, PairRegistry, load_checkpoint, save_checkpoint
from .neural_data import (
    NeuralView,
    data_identity,
    make_view,
    preparation_identity,
    validate_label_clocks,
)
from .neural_engine import (
    SharedLSTM,
    batch_prediction,
    clip,
    norm_summary,
    optimizer,
    seed_all,
    session_batches,
    session_losses,
)
from .p3_domain import Forecast, Permission, synthetic_id


@dataclass
class EarlyStop:
    """Strict qualifying best differs from raw minimum; epoch numbers are one-based."""

    epoch: int = 0
    best: float | None = None
    selected: int = 0
    raw_min: float | None = None
    raw_epoch: int = 0
    patience: int = 0
    status: str = "CALIBRATING"

    def observe(self, loss: float | None) -> bool:
        if self.status != "CALIBRATING" or loss is None or not math.isfinite(loss) or loss < 0:
            raise ValueError("VALID_SEQUENTIAL_VALIDATION_MSE_REQUIRED")
        self.epoch += 1
        qualifying = self.best is None or loss < .999 * self.best
        if self.raw_min is None or loss < self.raw_min:
            self.raw_min, self.raw_epoch = loss, self.epoch
        if qualifying:
            self.best, self.selected, self.patience = loss, self.epoch, 0
        else:
            self.patience += 1
        if self.epoch >= 12 and self.patience >= 10:
            self.status = "PATIENCE_STOP"
        elif self.epoch == 60:
            self.status = "MAX_EPOCHS_REACHED"
        return qualifying


def epoch_pass(
    model: SharedLSTM, view: NeuralView, epoch: int, seed: int,
    opt: torch.optim.AdamW | None = None,
) -> dict:
    """Aggregate the exact session sum across batches; no average of batch means."""
    model.train(opt is not None)
    total, count, norms, order, losses_by_day, scores, targets = 0.0, 0, [], [], [], [], []
    for positions in session_batches(len(view.sessions), seed, epoch, shuffle=opt is not None):
        batch = view.batch(positions)
        order.extend(batch.ids)
        with torch.set_grad_enabled(opt is not None):
            predictions = batch_prediction(model, batch)
            losses = session_losses(predictions, batch.targets, batch.origins)
            loss = losses.mean()
            if opt is not None:
                opt.zero_grad(set_to_none=True)
                loss.backward()
                norms.append(clip(model))
                opt.step()
        measured = losses.detach()
        total += float(measured.sum())
        count += len(batch.ids)
        losses_by_day.extend(measured.tolist())
        scores.extend(predictions.detach()[batch.origins].reshape(-1).tolist())
        targets.extend(batch.targets[batch.origins].reshape(-1).tolist())
    if count != len(view.sessions) or len(set(order)) != count:
        raise ValueError("EXACT_SESSION_EPOCH_CONSERVATION_REQUIRED")
    sorted_losses = sorted(losses_by_day, reverse=True)
    return {
        "epoch": epoch, "mean_session_mse": total / count, "sessions": count,
        "optimizer_steps": len(norms), "permutation_hash": fingerprint(order),
        "gradients": norm_summary(tuple(norms)) if norms else None,
        "score_std": float(np.std(scores)), "constant_scores": bool(np.ptp(scores) == 0),
        "mature_synthetic_stock_labels": len(targets),
        "target_abs_max": float(np.max(np.abs(targets))),
        "target_abs_p99": float(np.quantile(np.abs(targets), .99)),
        "loss_concentration": {str(p): sum(sorted_losses[:max(1, math.ceil(count * p))])
                               / total if total else 0.0 for p in (.01, .05, .1)},
    }


def state_hash(model: SharedLSTM) -> str:
    return identity({name: value.detach().cpu().tolist()
                     for name, value in model.state_dict().items()})


def code_identity() -> str:
    modules = ("neural_engine.py", "neural_data.py", "neural_artifacts.py",
               "neural_lifecycle.py", "baseline_fit.py", "baseline_inputs.py",
               "ft0_transforms.py", "hourly_proxy.py", "labels.py")
    return fingerprint({
        "modules": {name: digest(Path(__file__).with_name(name)) for name in modules},
        "torch": torch.__version__, "numpy": np.__version__, "pandas": pd.__version__,
        "python": platform.python_version(),
        "device_contract": "CPU_FLOAT32_SAME_DEVICE_RESUME",
    })


@dataclass(frozen=True)
class PairRun:
    evidence: dict
    preparation: Preparation
    pair: PairIdentity
    checkpoint: Path


def validation_adequacy(rows: tuple[RidgeOrigin, ...]) -> dict:
    """Keep the existing 50/25 guards, with an explicit neural blocking status."""
    try:
        return adequacy(rows)
    except ValueError:
        raise ValueError("BLOCKED_INADEQUATE_INNER_VALIDATION") from None


def run_pair(
    data: FitData, stage: Stage, fitted_at: pd.Timestamp, permission: Permission, out: Path,
    *, seed: int = 42, mode: str = MODE,
) -> PairRun:
    """One bounded synthetic D6g pair. No empirical executor or source loader exists."""
    if mode != MODE or out.exists():
        raise ValueError("P4_3_BLOCKED_OR_IMMUTABLE_OUTPUT_EXISTS")
    verify(permission)
    data.validate(permission, mode == MODE)
    validate_label_clocks(data)
    inner, validation, full = windows(stage, fitted_at)
    inner = replace(inner, fitted_at=inner.stop)
    train_rows, train_rejected = fitting_origins(data.origins, data.universe, inner)
    valid_rows, valid_rejected = fitting_origins(data.origins, data.universe, validation)
    refit_rows, refit_rejected = fitting_origins(data.origins, data.universe, full)
    adequate = validation_adequacy(valid_rows)
    guard = replay_permission(permission)
    calibration_prep = prepare(data, inner, train_rows, market=False, permission=guard,
                               allow_synthetic=True)
    train = make_view(data, inner, calibration_prep, guard, allow_synthetic=True)
    valid = make_view(data, validation, calibration_prep, guard, allow_synthetic=True)
    usable = {(row.session, row.origin) for row in valid.rows}
    adequate = validation_adequacy(tuple(row for row in valid_rows if (
        row.inputs.plan.session, row.inputs.plan.origin
    ) in usable))
    config = {"lr": .001, "betas": [.9, .999], "eps": 1e-8, "decay": [.01, 0],
              "clip": 1, "batch_sessions": 16, "dropout": .1, "width": 32,
              "layers": 1, "steps": 48, "channels": 16, "stop": [60, 12, 10, .999]}
    pair = PairIdentity("SYN:TM0:" + stage, data.universe.universe_id, "FT0_STOCK_ONLY",
                        "TG0_HOURLY_PROXY", identity((inner, validation, full)),
                        data_identity(data),
                        preparation_identity(calibration_prep), fingerprint(config),
                        code_identity(), seed)
    out.mkdir(parents=True)
    registry = PairRegistry(out / "synthetic_pair_registry.json")
    registry.reserve(pair)
    registry.transition(pair, "CALIBRATING")
    started = time.monotonic()
    seed_all(seed)
    model = SharedLSTM()
    initial_hash = state_hash(model)
    opt = optimizer(model)
    selector = EarlyStop()
    trace = []
    best = None
    try:
        while selector.status == "CALIBRATING":
            e = selector.epoch + 1
            training = epoch_pass(model, train, e, seed, opt)
            evaluation = epoch_pass(model, valid, e, seed)
            qualifies = selector.observe(evaluation["mean_session_mse"])
            trace.append({"training": training, "validation": evaluation,
                          "selection": dict(vars(selector)), "qualifying": qualifies})
            if qualifies:
                best = {name: value.detach().clone() for name, value in model.state_dict().items()}
        if best is None:
            raise ValueError("NO_QUALIFYING_CALIBRATION_CHECKPOINT")
        model.load_state_dict(best)
        selected = save_checkpoint(out / "calibration_selected.pt", model, pair,
                                   "CALIBRATION_SELECTED", selector.selected, trace=tuple(trace))
        registry.transition(pair, "CALIBRATED")
        calibration_seconds = time.monotonic() - started
        refit_prep = prepare(data, full, refit_rows, market=False, permission=guard,
                             allow_synthetic=True)
        if preparation_identity(refit_prep) == preparation_identity(calibration_prep):
            raise ValueError("FRESH_FULL_PREFIX_PREPROCESS_REQUIRED")
        refit = make_view(data, full, refit_prep, guard, allow_synthetic=True)
        registry.transition(pair, "REFITTING")
        seed_all(seed)  # Reset deterministic fresh initialization/dropout stream.
        final = SharedLSTM()
        fresh_hash = state_hash(final)
        refit_opt = optimizer(final)
        assert not refit_opt.state and final is not model and refit_opt is not opt
        refit_started = time.monotonic()
        refit_trace = tuple(epoch_pass(final, refit, e, seed, refit_opt)
                            for e in range(1, selector.selected + 1))
        checkpoint = out / "refit_final.pt"
        manifest = save_checkpoint(checkpoint, final, pair, "REFIT_FINAL", selector.selected,
                                   trace=refit_trace, fit_binding=preparation_identity(refit_prep))
        loaded = SharedLSTM()
        load_checkpoint(checkpoint, loaded, pair, "REFIT_FINAL",
                        fit_binding=preparation_identity(refit_prep))
        final.eval()
        example = refit.batch((len(refit.sessions) - 1,))
        expected = batch_prediction(final, example)
        actual = batch_prediction(loaded, example)
        if not torch.equal(expected, actual):
            raise ValueError("SAME_CPU_CHECKPOINT_RELOAD_MISMATCH")
        result = {
            "mode": mode, "pair": vars(pair), "pair_key": pair.key, "selector": vars(selector),
            "adequacy": adequate, "calibration_checkpoint": selected, "final_checkpoint": manifest,
            "calibration_initial_hash": initial_hash, "refit_initial_hash": fresh_hash,
            "calibration_selected_hash": state_hash(model), "refit_final_hash": state_hash(final),
            "fresh_optimizer_state_empty": True, "calibration_seconds": calibration_seconds,
            "refit_seconds": time.monotonic() - refit_started,
            "calibration_steps": sum(r["training"]["optimizer_steps"] for r in trace),
            "refit_steps": sum(r["optimizer_steps"] for r in refit_trace),
            "calibration_preparation": preparation_identity(calibration_prep),
            "refit_preparation": preparation_identity(refit_prep), "train_view": train.version,
            "validation_view": valid.version, "refit_view": refit.version,
            "validation_preprocess_exclusions": valid.excluded,
            "canonical_feature_rows": len(refit.values), "indexed_origins": len(refit.rows),
            "purged_or_invalid_origins": [len(train_rejected), len(valid_rejected),
                                         len(refit_rejected)],
            "fitting_origin_dispositions": {
                "inner_train": dict(Counter(reason for _, reason in train_rejected)),
                "inner_validation": dict(Counter(reason for _, reason in valid_rejected)),
                "refit": dict(Counter(reason for _, reason in refit_rejected)),
            },
            "reload_max_error": float((expected - actual).abs().max().detach()),
            "example_scores": actual[0, 0].detach().tolist(),
        }
        write_json(out / "selection_trace.json", trace)
        write_json(out / "refit_trace.json", refit_trace)
        write_json(out / "pair_result.json", result)
        verify(permission)
        registry.transition(pair, "COMPLETE", checkpoint=checkpoint,
                            seconds=time.monotonic() - started)
        return PairRun(result, refit_prep, pair, checkpoint)
    except Exception:
        registry.transition(pair, "FAILED", seconds=time.monotonic() - started)
        raise


def forecast_scores(run: PairRun, row: BaselineInput, permission: Permission) -> Forecast:
    """Evaluation-only five-score P3 binding; labels and exit availability are absent."""
    verify(permission)
    synthetic_id(row.input_id)
    if run.pair.universe != row.universe.universe_id or run.pair.code != code_identity():
        raise ValueError("NEURAL_FORECAST_ORDERED_UNIVERSE_REQUIRED")
    registry = json.loads((run.checkpoint.parent / "synthetic_pair_registry.json").read_text())
    completed = registry["entries"][run.pair.key]
    if (completed["state"] != "COMPLETE"
            or completed["checkpoint_sha"] != digest(run.checkpoint)
            or run.evidence["final_checkpoint"]["sha256"] != completed["checkpoint_sha"]):
        raise ValueError("COMPLETE_REFIT_ONLY_FOR_PREDICTION")
    if preparation_identity(run.preparation) != run.evidence["refit_preparation"]:
        raise ValueError("EXACT_FINAL_PREPROCESS_BINDING_REQUIRED")
    processed = run.preparation.apply(row, "ASOF")
    processed.validate(permission, allow_synthetic=True)
    model = SharedLSTM()
    load_checkpoint(run.checkpoint, model, run.pair, "REFIT_FINAL",
                    fit_binding=preparation_identity(run.preparation))
    model.eval()
    with torch.no_grad():
        scores = tuple(float(v) for v in model(torch.tensor(processed.stock.values)))
    if len(scores) != 5:
        raise ValueError("COMPLETE_FIVE_NEURAL_FORECAST_REQUIRED")
    return Forecast(row.universe, "SYN:NEURAL_FORECAST:" + fingerprint(
        [run.pair.key, run.evidence["final_checkpoint"]["sha256"], row.input_id, scores]
    ), row.plan, scores)
