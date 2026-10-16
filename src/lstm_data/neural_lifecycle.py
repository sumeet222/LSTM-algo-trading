"""D6g chronological synthetic calibration/refit and compact training health."""

from __future__ import annotations

import json
import math
import platform
import time
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Protocol

import numpy as np
import pandas as pd
import torch

from .baseline_authority import replay_permission, verify
from .baseline_fit import FitData, Preparation, prepare
from .baseline_inputs import BaselineInput
from .baseline_ridge import RidgeOrigin, Stage, adequacy, fitting_origins, windows
from .config import digest, fingerprint, write_json
from .controlled_loss import LossPolicy
from .ft0_transforms import identity
from .labels import FitWindow
from .neural_artifacts import MODE, PairIdentity, PairRegistry, load_checkpoint, save_checkpoint
from .neural_data import (
    NeuralView,
    data_identity,
    make_view,
    preparation_identity,
    validate_label_clocks,
)
from .neural_engine import (
    SessionBatch,
    batch_prediction,
    clip,
    norm_summary,
    optimizer,
    seed_all,
    session_batches,
    session_losses,
)
from .neural_market import (
    MarketEvidence,
    MarketNeuralView,
    make_market_view,
    market_data_identity,
    market_input,
    market_preparation_identity,
)
from .neural_models import (
    EndpointGatedLSTM,
    NeuralModel,
    architecture_for_information,
    create_model,
    gate_diagnostics,
)
from .p3_domain import Forecast, Permission, synthetic_id
from .peer_neural import E5View, e5_input, make_e5_view


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
        qualifying = self.best is None or loss < 0.999 * self.best
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


class SessionView(Protocol):
    """A panel-specific adapter supplies whole sessions to the shared epoch engine."""

    @property
    def sessions(self) -> tuple[str, ...]: ...

    def batch(self, positions: tuple[int, ...]) -> SessionBatch: ...


def epoch_pass(
    model: NeuralModel,
    view: SessionView,
    epoch: int,
    seed: int,
    opt: torch.optim.AdamW | None = None,
    *,
    policy: LossPolicy | None = None,
    batch_sink: Callable[[dict], None] | None = None,
    deadline: float | None = None,
) -> dict:
    """Aggregate the exact session sum across batches; no average of batch means."""
    model.train(opt is not None)
    total, count, norms, order, losses_by_day, scores, targets = 0.0, 0, [], [], [], [], []
    gate_weights, gate_norms, input_norms = [], [], []
    peer_gradient_norms = []
    objectives = []
    started = time.monotonic()
    for batch_index, positions in enumerate(
        session_batches(len(view.sessions), seed, epoch, shuffle=opt is not None), 1
    ):
        step_started = time.monotonic()
        if deadline is not None and step_started >= deadline:
            raise TimeoutError("FROZEN_FITTING_DEADLINE")
        batch = view.batch(positions)
        if opt is not None and isinstance(model, EndpointGatedLSTM):
            batch.inputs.requires_grad_()
        if opt is not None and isinstance(view, E5View):
            batch.inputs.requires_grad_()
        if isinstance(model, EndpointGatedLSTM):
            with torch.no_grad():
                gate_weights.append(
                    model.compose(batch.inputs[batch.origins].reshape(-1, 48, 21))[1]
                )
        order.extend(batch.ids)
        with torch.set_grad_enabled(opt is not None):
            logits = batch_prediction(model, batch)
            predictions = policy.canonical(logits) if policy is not None else logits
            losses = session_losses(
                predictions, batch.targets, batch.origins, stock_count=batch.stock_count
            )
            objective = (
                policy.objective(
                    logits, batch.targets, batch.origins, stock_count=batch.stock_count
                )
                if policy is not None
                else losses
            )
            objectives.extend(objective.detach().tolist())
            loss = objective.mean()
            if opt is not None:
                opt.zero_grad(set_to_none=True)
                loss.backward()
                if isinstance(view, E5View):
                    if batch.inputs.grad is None:
                        raise ValueError("E5_PEER_INPUT_GRADIENT_REQUIRED")
                    peer_gradient_norms.append(float(batch.inputs.grad[..., 21:].norm()))
                if isinstance(model, EndpointGatedLSTM):
                    gate_norms.append(
                        float(
                            torch.sqrt(
                                sum(
                                    (
                                        p.grad.square().sum()
                                        for p in model.gate.parameters()
                                        if p.grad is not None
                                    ),
                                    torch.tensor(0.0),
                                )
                            )
                        )
                    )
                    if batch.inputs.grad is None:
                        raise ValueError("MC1_INPUT_GRADIENT_REQUIRED")
                    input_norms.append(float(batch.inputs.grad.norm()))
                norms.append(clip(model))
                opt.step()
                if any(not bool(torch.isfinite(p).all()) for p in model.parameters()):
                    raise ValueError("NONFINITE_WEIGHT_INVALID")
        measured = losses.detach()
        total += float(measured.sum())
        count += len(batch.ids)
        losses_by_day.extend(measured.tolist())
        scores.extend(predictions.detach()[batch.origins].reshape(-1).tolist())
        targets.extend(batch.targets[batch.origins].reshape(-1).tolist())
        if batch_sink is not None:
            truth = batch.targets[batch.origins].detach().cpu().numpy().reshape(-1)
            batch_sink(
                dict(
                    epoch=epoch,
                    batch_index=batch_index,
                    sessions=list(batch.ids),
                    origins=int(batch.origins.sum()),
                    seconds=time.monotonic() - step_started,
                    optimizer_step=opt is not None,
                    preclip_norm=norms[-1] if opt is not None else None,
                    canonical_mse=float(measured.mean()),
                    objective=float(objective.detach().mean()),
                    target_abs_max=float(np.max(np.abs(truth))),
                    target_abs_p99=float(np.quantile(np.abs(truth), 0.99)),
                    target_abs_gt10=int(np.sum(np.abs(truth) > 10)),
                    target_abs_gt20=int(np.sum(np.abs(truth) > 20)),
                    largest_session_loss_share=float(measured.max() / measured.sum())
                    if float(measured.sum())
                    else 0.0,
                )
            )
    if count != len(view.sessions) or len(set(order)) != count:
        raise ValueError("EXACT_SESSION_EPOCH_CONSERVATION_REQUIRED")
    sorted_losses = sorted(losses_by_day, reverse=True)
    result = {
        "epoch": epoch,
        "optimizer_objective": float(np.mean(objectives)),
        "seconds": time.monotonic() - started,
        "mean_session_mse": total / count,
        "sessions": count,
        "optimizer_steps": len(norms),
        "permutation_hash": fingerprint(order),
        "gradients": norm_summary(tuple(norms)) if norms else None,
        "score_std": float(np.std(scores)),
        "constant_scores": bool(np.ptp(scores) == 0),
        "mature_synthetic_stock_labels": len(targets),
        "target_abs_max": float(np.max(np.abs(targets))),
        "target_abs_p99": float(np.quantile(np.abs(targets), 0.99)),
        "loss_concentration": {
            str(p): sum(sorted_losses[: max(1, math.ceil(count * p))]) / total if total else 0.0
            for p in (0.01, 0.05, 0.1)
        },
    }

    if gate_weights:
        result["gate"] = gate_diagnostics(torch.cat(gate_weights))
        result["gate_gradient_norms"] = gate_norms
        result["input_gradient_norms"] = input_norms
    if peer_gradient_norms:
        result["peer_gradient_norms"] = peer_gradient_norms
    return result


def state_hash(model: NeuralModel) -> str:
    return identity(
        {name: value.detach().cpu().tolist() for name, value in model.state_dict().items()}
    )


def code_identity() -> str:
    modules = (
        "peer_neural.py",
        "peer_inputs.py",
        "neural_engine.py",
        "neural_data.py",
        "neural_artifacts.py",
        "neural_lifecycle.py",
        "neural_models.py",
        "neural_market.py",
        "baseline_fit.py",
        "baseline_inputs.py",
        "ft0_transforms.py",
        "hourly_proxy.py",
        "labels.py",
        "market_features.py",
        "market_tensor.py",
        "baseline_cache.py",
    )
    return fingerprint(
        {
            "modules": {name: digest(Path(__file__).with_name(name)) for name in modules},
            "torch": torch.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "python": platform.python_version(),
            "device_contract": "CPU_FLOAT32_SAME_DEVICE_RESUME",
        }
    )


@dataclass(frozen=True)
class PairRun:
    evidence: dict
    preparation: Preparation
    pair: PairIdentity
    checkpoint: Path
    market_history: MarketEvidence | None = None


def validation_adequacy(rows: tuple[RidgeOrigin, ...]) -> dict:
    """Keep the existing 50/25 guards, with an explicit neural blocking status."""
    try:
        return adequacy(rows)
    except ValueError:
        raise ValueError("BLOCKED_INADEQUATE_INNER_VALIDATION") from None


def run_pair(
    data: FitData,
    stage: Stage,
    fitted_at: pd.Timestamp,
    permission: Permission,
    out: Path,
    *,
    seed: int = 42,
    mode: str = MODE,
    architecture: str = "TM0",
    market_history: MarketEvidence | None = None,
    synthetic_validation_trace: tuple[float, ...] | None = None,
) -> PairRun:
    """One bounded synthetic D6g pair. No empirical executor or source loader exists."""
    if mode != MODE or out.exists():
        raise ValueError("P4_3_BLOCKED_OR_IMMUTABLE_OUTPUT_EXISTS")
    if architecture not in {"TM0", "MC0", "MC1", "E5"}:
        raise ValueError("DECLARED_NEURAL_ARCHITECTURE_REQUIRED")
    if (architecture == "TM0") != (market_history is None):
        raise ValueError("ARCHITECTURE_INFORMATION_BINDING_REQUIRED")
    if synthetic_validation_trace is not None and (
        not synthetic_validation_trace
        or len(synthetic_validation_trace) > 60
        or any(not math.isfinite(v) or v < 0 for v in synthetic_validation_trace)
    ):
        raise ValueError("BOUNDED_SYNTHETIC_SELECTION_ORACLE_REQUIRED")
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

    def preparation(window: FitWindow, rows: tuple[RidgeOrigin, ...]) -> Preparation:
        if market_history is None:
            return prepare(data, window, rows, market=False, permission=guard, allow_synthetic=True)
        market_data_identity(data, market_history)
        # D7 fits only valid unique training vectors; full history/masks retained for inputs.
        fitting = replace(
            data,
            market_vectors=tuple(
                v
                for v in data.market_vectors
                if v.values is not None and v.reason == "VECTOR_VALID"
            ),
        )
        value = prepare(fitting, window, rows, market=True, permission=guard, allow_synthetic=True)
        return replace(value, market_vectors=data.market_vectors)

    def prep_id(value: Preparation) -> str:
        return (
            preparation_identity(value)
            if market_history is None
            else market_preparation_identity(value)
        )

    def view(window: FitWindow, prep: Preparation) -> NeuralView | MarketNeuralView | E5View:
        # Explicit fitting-window API; no source or empirical loader.
        if not isinstance(window, FitWindow):
            raise ValueError("EXPLICIT_FIT_WINDOW_REQUIRED")
        if market_history is None:
            return make_view(data, window, prep, guard, allow_synthetic=True)
        if architecture == "E5":
            return make_e5_view(data, window, prep, guard, market_history, allow_synthetic=True)
        return make_market_view(data, window, prep, guard, market_history, allow_synthetic=True)

    calibration_prep = preparation(inner, train_rows)
    train = view(inner, calibration_prep)
    valid = view(validation, calibration_prep)
    usable = {(row.session, row.origin) for row in valid.rows}
    adequate = validation_adequacy(
        tuple(
            row for row in valid_rows if (row.inputs.plan.session, row.inputs.plan.origin) in usable
        )
    )
    config = {
        "lr": 0.001,
        "betas": [0.9, 0.999],
        "eps": 1e-8,
        "decay": [0.01, 0],
        "clip": 1,
        "batch_sessions": 16,
        "dropout": 0.1,
        "width": 32,
        "layers": 1,
        "steps": 48,
        "channels": {"TM0": 16, "MC0": 21, "MC1": 21, "E5": 23}[architecture],
        "stop": [60, 12, 10, 0.999],
    }
    if architecture != "TM0":
        config["architecture"] = architecture
        config["gate"] = "16_SOFTMAX_ENDPOINT_TAU1_ZERO_INIT" if architecture == "MC1" else None
    if synthetic_validation_trace is not None:
        config["synthetic_validation_trace"] = synthetic_validation_trace
    information = "FT0_STOCK_ONLY" if architecture == "TM0" else "FT0_D7_" + architecture
    source_id = (
        data_identity(data)
        if market_history is None
        else market_data_identity(data, market_history)
    )
    pair = PairIdentity(
        "SYN:" + architecture + ":" + stage,
        data.universe.universe_id,
        information,
        "TG0_HOURLY_PROXY",
        identity((inner, validation, full)),
        source_id,
        prep_id(calibration_prep),
        fingerprint(config),
        code_identity(),
        seed,
    )
    out.mkdir(parents=True)
    registry = PairRegistry(out / "synthetic_pair_registry.json")
    registry.reserve(pair)
    registry.transition(pair, "CALIBRATING")
    started = time.monotonic()
    seed_all(seed)
    model = create_model(architecture)
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
            monitored = evaluation["mean_session_mse"]
            if synthetic_validation_trace is not None:
                if e > len(synthetic_validation_trace):
                    raise ValueError("SYNTHETIC_SELECTION_TRACE_EXHAUSTED")
                monitored = synthetic_validation_trace[e - 1]
                evaluation["scripted_selection_mse"] = monitored
            qualifies = selector.observe(monitored)
            trace.append(
                {
                    "training": training,
                    "validation": evaluation,
                    "selection": dict(vars(selector)),
                    "qualifying": qualifies,
                }
            )
            if qualifies:
                best = {name: value.detach().clone() for name, value in model.state_dict().items()}
        if best is None:
            raise ValueError("NO_QUALIFYING_CALIBRATION_CHECKPOINT")
        model.load_state_dict(best)
        selected = save_checkpoint(
            out / "calibration_selected.pt",
            model,
            pair,
            "CALIBRATION_SELECTED",
            selector.selected,
            trace=tuple(trace),
        )
        registry.transition(pair, "CALIBRATED")
        calibration_seconds = time.monotonic() - started
        refit_prep = preparation(full, refit_rows)
        if prep_id(refit_prep) == prep_id(calibration_prep):
            raise ValueError("FRESH_FULL_PREFIX_PREPROCESS_REQUIRED")
        refit = view(full, refit_prep)
        registry.transition(pair, "REFITTING")
        seed_all(seed)  # Reset deterministic fresh initialization/dropout stream.
        final = create_model(architecture)
        fresh_hash = state_hash(final)
        refit_opt = optimizer(final)
        assert not refit_opt.state and final is not model and refit_opt is not opt
        refit_started = time.monotonic()
        refit_trace = tuple(
            epoch_pass(final, refit, e, seed, refit_opt) for e in range(1, selector.selected + 1)
        )
        checkpoint = out / "refit_final.pt"
        manifest = save_checkpoint(
            checkpoint,
            final,
            pair,
            "REFIT_FINAL",
            selector.selected,
            trace=refit_trace,
            fit_binding=prep_id(refit_prep),
        )
        loaded = create_model(architecture)
        load_checkpoint(checkpoint, loaded, pair, "REFIT_FINAL", fit_binding=prep_id(refit_prep))
        final.eval()
        example = refit.batch((len(refit.sessions) - 1,))
        expected = batch_prediction(final, example)
        actual = batch_prediction(loaded, example)
        if not torch.equal(expected, actual):
            raise ValueError("SAME_CPU_CHECKPOINT_RELOAD_MISMATCH")
        result = {
            "mode": mode,
            "architecture": architecture,
            "selection_monitor": "SYNTHETIC_SCRIPTED_ORACLE"
            if synthetic_validation_trace is not None
            else "ACTUAL_INNER_MSE",
            "pair": vars(pair),
            "pair_key": pair.key,
            "selector": vars(selector),
            "adequacy": adequate,
            "calibration_checkpoint": selected,
            "final_checkpoint": manifest,
            "calibration_initial_hash": initial_hash,
            "refit_initial_hash": fresh_hash,
            "calibration_selected_hash": state_hash(model),
            "refit_final_hash": state_hash(final),
            "fresh_optimizer_state_empty": True,
            "calibration_seconds": calibration_seconds,
            "refit_seconds": time.monotonic() - refit_started,
            "calibration_steps": sum(r["training"]["optimizer_steps"] for r in trace),
            "refit_steps": sum(r["optimizer_steps"] for r in refit_trace),
            "calibration_preparation": prep_id(calibration_prep),
            "refit_preparation": prep_id(refit_prep),
            "train_view": train.version,
            "validation_view": valid.version,
            "refit_view": refit.version,
            "validation_preprocess_exclusions": valid.excluded,
            "canonical_feature_rows": len(refit.values),
            "indexed_origins": len(refit.rows),
            "purged_or_invalid_origins": [
                len(train_rejected),
                len(valid_rejected),
                len(refit_rejected),
            ],
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
        registry.transition(
            pair, "COMPLETE", checkpoint=checkpoint, seconds=time.monotonic() - started
        )
        return PairRun(result, refit_prep, pair, checkpoint, market_history)
    except Exception:
        registry.transition(pair, "FAILED", seconds=time.monotonic() - started)
        raise


def forecast_scores(
    run: PairRun,
    row: BaselineInput,
    permission: Permission,
    *,
    market_history: MarketEvidence | None = None,
) -> Forecast:
    """Evaluation-only five-score P3 binding; labels and exit availability are absent."""
    verify(permission)
    synthetic_id(row.input_id)
    if run.pair.universe != row.universe.universe_id or run.pair.code != code_identity():
        raise ValueError("NEURAL_FORECAST_ORDERED_UNIVERSE_REQUIRED")
    registry = json.loads((run.checkpoint.parent / "synthetic_pair_registry.json").read_text())
    completed = registry["entries"][run.pair.key]
    if (
        completed["state"] != "COMPLETE"
        or completed["checkpoint_sha"] != digest(run.checkpoint)
        or run.evidence["final_checkpoint"]["sha256"] != completed["checkpoint_sha"]
    ):
        raise ValueError("COMPLETE_REFIT_ONLY_FOR_PREDICTION")
    architecture = architecture_for_information(run.pair.information)
    prep = run.preparation
    if architecture == "TM0":
        if market_history is not None or run.market_history is not None:
            raise ValueError("STOCK_ONLY_INFORMATION_REQUIRED")
        binding = preparation_identity(prep)
        processed = prep.apply(row, "ASOF")
        processed.validate(permission, allow_synthetic=True)
        trace = row.input_id  # Legacy TM0 identity and values are preserved.
        x = torch.tensor(processed.stock.values)
    else:
        if run.market_history is None or market_history is None:
            raise ValueError("EXPLICIT_FORECAST_D7_HISTORY_REQUIRED")
        history = run.market_history.extend(market_history)
        binding = market_preparation_identity(prep)
        prep = prep.with_market_history(history.vectors, permission, allow_synthetic=True)
        if architecture == "E5":
            x, trace = e5_input(row, prep, history, permission)
        else:
            processed, trace = market_input(row, prep, history, permission)
            m = processed.market
            assert m is not None and m.values is not None
            stock = torch.tensor(processed.stock.values)
            market = torch.tensor(m.values)
            x = torch.cat((stock, market[None].expand(5, -1, -1)), dim=-1)
    if binding != run.evidence["refit_preparation"]:
        raise ValueError("EXACT_FINAL_PREPROCESS_BINDING_REQUIRED")
    model = create_model(architecture)
    load_checkpoint(run.checkpoint, model, run.pair, "REFIT_FINAL", fit_binding=binding)
    model.eval()
    with torch.no_grad():
        scores = tuple(float(v) for v in model(x))
    if len(scores) != 5:
        raise ValueError("COMPLETE_FIVE_NEURAL_FORECAST_REQUIRED")
    return Forecast(
        row.universe,
        "SYN:NEURAL_FORECAST:"
        + fingerprint([run.pair.key, run.evidence["final_checkpoint"]["sha256"], trace, scores]),
        row.plan,
        scores,
    )
