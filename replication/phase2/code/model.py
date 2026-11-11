"""Independent S2-C modeling layer derived solely from EXPERIMENT_SPEC §§8,11–13.

Inputs are already reconstructed, phase-specific FT16 windows. This module has
no data readers, project-helper imports, preprocessing fits, or reference scores.
"""
from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from dataclasses import asdict, dataclass, field
import hashlib
import json
import math
import os
from pathlib import Path
import random
from typing import TypeAlias

import numpy as np
from numpy.typing import NDArray
import torch
from torch import Tensor, nn

FloatArray: TypeAlias = NDArray[np.float64]
InputArray: TypeAlias = NDArray[np.float32]
IndexArray: TypeAlias = NDArray[np.int64]
BoolArray: TypeAlias = NDArray[np.bool_]
InputGetter: TypeAlias = Callable[[IndexArray], tuple[InputArray, InputArray]]

STOCKS = 20
STEPS = 48
CHANNELS = 16
CLOCK_CHANNELS = 10
HIDDEN = 32
PARAMETERS = 6572
SEED = 42


def configure_runtime() -> dict[str, str | int | bool]:
    """Enforce the specified public-library execution contract without RNG draws."""
    if torch.__version__.split("+")[0] != "2.10.0":
        raise RuntimeError(f"Torch 2.10.0 required; found {torch.__version__}")
    torch.set_num_threads(4)
    if torch.get_num_interop_threads() != 1:
        torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.set_default_dtype(torch.float32)
    return {
        "torch": str(torch.__version__),
        "numpy": str(np.__version__),
        "device": "cpu",
        "dtype": "float32",
        "intraop_threads": torch.get_num_threads(),
        "interop_threads": torch.get_num_interop_threads(),
        "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
    }


def seed_phase() -> None:
    """Reset all three stipulated RNGs once before each fresh phase model."""
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)


class S2CModel(nn.Module):
    """Shared 48×16/H32 LSTM with one dropped representation and 42-wide heads."""

    def __init__(self) -> None:
        super().__init__()
        # Constructor order is part of the seed42 RNG contract.
        self.lstm = nn.LSTM(CHANNELS, HIDDEN, num_layers=1, batch_first=True)
        self.dropout = nn.Dropout(0.10)
        self.main = nn.Linear(HIDDEN + CLOCK_CHANNELS, 1)
        self.auxiliary = nn.Linear(HIDDEN + CLOCK_CHANNELS, 3)
        self.to(device="cpu", dtype=torch.float32)
        if sum(parameter.numel() for parameter in self.parameters()) != PARAMETERS:
            raise RuntimeError("Unexpected architecture parameter count")

    def forward(self, x: Tensor, clock: Tensor) -> tuple[Tensor, Tensor]:
        """Accept feature/clock inputs only; states are zeroed for every call."""
        if x.ndim != 3 or tuple(x.shape[1:]) != (STEPS, CHANNELS):
            raise ValueError("X must have shape [stock_windows,48,16]")
        if tuple(clock.shape) != (x.shape[0], CLOCK_CHANNELS):
            raise ValueError("clock must have shape [stock_windows,10]")
        if x.device.type != "cpu" or clock.device.type != "cpu":
            raise ValueError("CPU execution is required")
        if x.dtype != torch.float32 or clock.dtype != torch.float32:
            raise ValueError("Network inputs must be float32")
        if not bool(torch.isfinite(x).all()) or not bool(torch.isfinite(clock).all()):
            raise ValueError("Network inputs must be finite")
        sequence, _ = self.lstm(x)  # Omitted initial state is independent zeros.
        representation = torch.cat((self.dropout(sequence[:, -1, :]), clock), dim=1)
        return self.main(representation).squeeze(-1), self.auxiliary(representation)


def fresh_model() -> S2CModel:
    """Create a CPU model with precisely the seed and construction order specified."""
    configure_runtime()
    seed_phase()
    return S2CModel()


def make_optimizer(model: S2CModel) -> torch.optim.AdamW:
    """Fresh exhaustive rank-two decay and bias/no-decay groups, in original order."""
    matrix = [parameter for parameter in model.parameters() if parameter.ndim == 2]
    other = [parameter for parameter in model.parameters() if parameter.ndim != 2]
    return torch.optim.AdamW(
        [{"params": matrix, "weight_decay": 0.01}, {"params": other, "weight_decay": 0.0}],
        lr=0.001,
        betas=(0.9, 0.999),
        eps=1e-8,
        amsgrad=False,
        maximize=False,
        foreach=None,
        capturable=False,
        differentiable=False,
        fused=None,
    )


def state_digest(model: S2CModel) -> str:
    """Hash named tensor values, independent of checkpoint serialization metadata."""
    digest = hashlib.sha256()
    for name, value in model.state_dict().items():
        array = value.detach().cpu().numpy()
        digest.update(name.encode("utf-8") + b"\0")
        digest.update(str(array.dtype).encode("ascii") + b"\0")
        digest.update(json.dumps(list(array.shape)).encode("ascii") + b"\0")
        digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _sessions(sessions: Sequence[str]) -> NDArray[np.str_]:
    result = np.asarray(sessions, dtype=np.str_)
    if result.ndim != 1 or len(result) == 0:
        raise ValueError("At least one session-labelled origin is required")
    if np.any(result == ""):
        raise ValueError("Session labels must be nonempty")
    return result


def origin_weights(sessions: Sequence[str]) -> FloatArray:
    """Equal sessions, then equal primary origins; weights sum to one."""
    dates = _sessions(sessions)
    unique, inverse, counts = np.unique(dates, return_inverse=True, return_counts=True)
    return np.asarray(1.0 / (len(unique) * counts[inverse]), dtype=np.float64)


def fit_scale(signed_returns: FloatArray, sessions: Sequence[str]) -> float:
    """Fit max(weighted-left median of float64 absolute R,1e-8)."""
    values = np.asarray(signed_returns, dtype=np.float64)
    weights = origin_weights(sessions)
    if values.shape != (len(weights), STOCKS) or not np.isfinite(values).all():
        raise ValueError("Scale labels must be finite [origins,20] signed returns")
    flattened = np.abs(values).reshape(-1)
    cell_weights = np.repeat(weights / STOCKS, STOCKS)
    order = np.argsort(flattened, kind="stable")
    cumulative = np.cumsum(cell_weights[order])
    cumulative /= np.sum(cell_weights, dtype=np.float64)
    index = min(int(np.searchsorted(cumulative, 0.5, side="left")), len(order) - 1)
    return max(float(flattened[order[index]]), 1e-8)


@dataclass(frozen=True)
class AuxiliaryWeights:
    """Phase-wide auxiliary hierarchy with a single supported-cell normalization."""

    values: FloatArray
    base: FloatArray
    mass: float
    sessions: int
    overnight_sessions: int


def auxiliary_weights(
    sessions: Sequence[str], overnight: BoolArray, supported: BoolArray
) -> AuxiliaryWeights:
    """Build b=1/(S_N N_d 20), then a=b*mask/Z without redistributing cells."""
    dates = _sessions(sessions)
    overnight = np.asarray(overnight, dtype=np.bool_)
    supported = np.asarray(supported, dtype=np.bool_)
    if overnight.shape != (len(dates),) or supported.shape != (len(dates), STOCKS):
        raise ValueError("Auxiliary category/mask shapes do not match origins")
    if np.any(supported[~overnight]):
        raise ValueError("Intraday auxiliary support is forbidden")
    unique_nights, counts = np.unique(dates[overnight], return_counts=True)
    if len(unique_nights) == 0:
        raise ValueError("Phase has no overnight auxiliary population")
    base = np.zeros(supported.shape, dtype=np.float64)
    for date, count in zip(unique_nights, counts, strict=True):
        base[(dates == date) & overnight] = 1.0 / (len(unique_nights) * count * STOCKS)
    mass = float(np.sum(base[supported], dtype=np.float64))
    if not math.isfinite(mass) or mass <= 0:
        raise ValueError("Phase auxiliary mass must be finite and positive")
    values = np.zeros_like(base)
    values[supported] = base[supported] / mass
    return AuxiliaryWeights(values, base, mass, len(np.unique(dates)), len(unique_nights))


@dataclass(frozen=True)
class PhaseData:
    """Admitted phase origins, immutable labels and a feature/clock-only accessor.

    ``get_inputs(indices)`` returns float32 X[n,20,48,16], clock[n,10] in exactly
    the requested origin order. The caller owns chronology and lawful role gates.
    No fitted preprocessing is performed here.
    """

    sessions: Sequence[str]
    signed_returns: FloatArray
    overnight: BoolArray
    auxiliary_returns: FloatArray
    auxiliary_mask: BoolArray
    get_inputs: InputGetter
    scale: float

    def __post_init__(self) -> None:
        n = len(_sessions(self.sessions))
        if np.shape(self.signed_returns) != (n, STOCKS):
            raise ValueError("Primary labels must be [origins,20]")
        if not np.isfinite(self.signed_returns).all():
            raise ValueError("Primary labels must all be finite")
        if np.shape(self.overnight) != (n,) or np.shape(self.auxiliary_mask) != (n, STOCKS):
            raise ValueError("Auxiliary category/mask shape mismatch")
        if np.shape(self.auxiliary_returns) != (n, STOCKS, 3):
            raise ValueError("Auxiliary labels must be [origins,20,3]")
        if np.asarray(self.overnight).dtype != np.bool_ or np.asarray(self.auxiliary_mask).dtype != np.bool_:
            raise ValueError("Category/mask arrays must be boolean")
        if np.any(self.auxiliary_mask[~self.overnight]):
            raise ValueError("Intraday auxiliary support is forbidden")
        if not np.isfinite(self.auxiliary_returns[self.auxiliary_mask]).all():
            raise ValueError("Supported auxiliary triples must all be finite")
        if not np.isnan(self.auxiliary_returns[~self.auxiliary_mask]).all():
            raise ValueError("Unsupported auxiliary labels must remain NaN")
        if not np.allclose(
            self.auxiliary_returns[self.auxiliary_mask].sum(axis=1),
            self.signed_returns[self.auxiliary_mask],
            atol=1e-12,
            rtol=1e-11,
        ):
            raise ValueError("Supported signed triples fail additivity")
        if not math.isfinite(self.scale) or self.scale <= 0:
            raise ValueError("Phase scale must be finite and positive")


def session_batches(sessions: Sequence[str], epoch: int) -> Iterator[IndexArray]:
    """Visit sorted-then-shuffled sessions once, retaining the final partial batch."""
    if epoch < 1:
        raise ValueError("Epoch numbering begins at one")
    dates = _sessions(sessions)
    unique = np.unique(dates)
    np.random.default_rng(SEED + epoch).shuffle(unique)
    for start in range(0, len(unique), 16):
        yield np.concatenate([
            np.flatnonzero(dates == date).astype(np.int64)
            for date in unique[start:start + 16]
        ])


def transformed_targets(signed_returns: Tensor, scale: float) -> Tensor:
    """Cast signed R before absolute value/division/Torch log1p, as specified."""
    return torch.log1p(signed_returns.to(dtype=torch.float32).abs() / scale)


@dataclass(frozen=True)
class Losses:
    main: Tensor
    auxiliary: Tensor
    total: Tensor


def batch_losses(
    main: Tensor,
    auxiliary: Tensor,
    signed_returns: Tensor,
    auxiliary_returns: Tensor,
    supported: Tensor,
    batch_sessions: Sequence[str],
    phase_auxiliary_weights: Tensor,
    phase_sessions: int,
    scale: float,
) -> Losses:
    """One local primary mean plus the S/B-scaled global auxiliary contribution.

    Auxiliary weights passed here are the already normalized phase values for
    these batch rows. Invalid labels are indexed away *before* any arithmetic.
    """
    n = len(batch_sessions)
    if tuple(main.shape) != (n, STOCKS) or tuple(auxiliary.shape) != (n, STOCKS, 3):
        raise ValueError("Batch predictions have incorrect shape")
    if tuple(signed_returns.shape) != (n, STOCKS):
        raise ValueError("Batch primary labels have incorrect shape")
    if tuple(auxiliary_returns.shape) != (n, STOCKS, 3) or tuple(supported.shape) != (n, STOCKS):
        raise ValueError("Batch auxiliary labels/mask have incorrect shape")
    if tuple(phase_auxiliary_weights.shape) != (n, STOCKS) or supported.dtype != torch.bool:
        raise ValueError("Batch auxiliary weights/mask have incorrect shape or type")
    actual_sessions = len(set(batch_sessions))
    if phase_sessions < actual_sessions or not math.isfinite(scale) or scale <= 0:
        raise ValueError("Invalid phase-session count or scale")
    target = transformed_targets(signed_returns, scale)
    weights = torch.as_tensor(origin_weights(batch_sessions), dtype=torch.float32)
    primary = torch.sum((main - target).square().mean(dim=1) * weights)
    if bool(supported.any()):
        labels = auxiliary_returns[supported].to(dtype=torch.float32) / scale
        error = (auxiliary[supported] - labels).square()
        weighted = error * phase_auxiliary_weights[supported].to(dtype=torch.float32).unsqueeze(-1)
        aux = weighted.sum() * (phase_sessions / actual_sessions) / 3.0
    else:
        # Exact differentiable zero maintains zero gradients, Adam moments/decay.
        aux = auxiliary.sum() * 0.0
    total = primary + 0.10 * aux
    if not bool(torch.isfinite(total)):
        raise FloatingPointError("Nonfinite training loss; stop without retry")
    return Losses(primary, aux, total)


def _input_tensors(get_inputs: InputGetter, indices: IndexArray) -> tuple[Tensor, Tensor]:
    x, clock = get_inputs(indices)
    if x.dtype != np.float32 or clock.dtype != np.float32:
        raise ValueError("Feature accessor must produce float32 arrays")
    if x.shape != (len(indices), STOCKS, STEPS, CHANNELS) or clock.shape != (len(indices), CLOCK_CHANNELS):
        raise ValueError("Feature accessor returned incorrect shape")
    return (
        torch.as_tensor(np.ascontiguousarray(x)).reshape(-1, STEPS, CHANNELS),
        torch.as_tensor(np.ascontiguousarray(np.repeat(clock, STOCKS, axis=0))),
    )


def predict_heads(model: S2CModel, get_inputs: InputGetter, n_origins: int) -> tuple[InputArray, InputArray]:
    """Frozen inference, chronological chunks of32 origins, no labels or masks."""
    if n_origins <= 0:
        raise ValueError("Inference requires at least one origin")
    model.eval()
    main_output = np.empty((n_origins, STOCKS), dtype=np.float32)
    aux_output = np.empty((n_origins, STOCKS, 3), dtype=np.float32)
    with torch.inference_mode():
        for start in range(0, n_origins, 32):
            indices = np.arange(start, min(start + 32, n_origins), dtype=np.int64)
            main, auxiliary = model(*_input_tensors(get_inputs, indices))
            if not bool(torch.isfinite(main).all()) or not bool(torch.isfinite(auxiliary).all()):
                raise FloatingPointError("Nonfinite frozen prediction; stop without retry")
            main_output[indices] = main.reshape(-1, STOCKS).cpu().numpy()
            aux_output[indices] = auxiliary.reshape(-1, STOCKS, 3).cpu().numpy()
    return main_output, aux_output


def predict(model: S2CModel, get_inputs: InputGetter, n_origins: int) -> InputArray:
    """Return main-only Mhat; diagnostic heads cannot enter its computation."""
    if n_origins <= 0:
        raise ValueError("Inference requires at least one origin")
    model.eval()
    output = np.empty((n_origins, STOCKS), dtype=np.float32)
    with torch.inference_mode():
        for start in range(0, n_origins, 32):
            indices = np.arange(start, min(start + 32, n_origins), dtype=np.int64)
            main, _ = model(*_input_tensors(get_inputs, indices))
            # Auxiliary diagnostics must not determine primary inference success.
            if not bool(torch.isfinite(main).all()):
                raise FloatingPointError("Nonfinite frozen main prediction; stop without retry")
            output[indices] = main.reshape(-1, STOCKS).cpu().numpy()
    return output


def validation_loss(model: S2CModel, phase: PhaseData) -> float:
    """Float32 stockwise transformed errors, float64 original-origin-weight dot."""
    predictions = torch.as_tensor(predict(model, phase.get_inputs, len(phase.sessions)))
    targets = transformed_targets(torch.as_tensor(phase.signed_returns), phase.scale)
    per_origin = (predictions - targets).square().mean(dim=1).numpy()
    value = float(np.dot(per_origin.astype(np.float64), origin_weights(phase.sessions)))
    if not math.isfinite(value) or value < 0:
        raise FloatingPointError("Selector loss must be finite and nonnegative")
    return value


@dataclass
class Selector:
    """Qualified-best selector; raw minimum is separate telemetry only."""

    epoch: int = 0
    selected: int = 0
    best: float = math.inf
    raw_best: float = math.inf
    raw_epoch: int = 0
    patience: int = 0
    stop_reason: str | None = None
    best_state: dict[str, Tensor] | None = field(default=None, repr=False)

    def update(self, value: float, model: S2CModel | None = None) -> bool:
        """Advance once, clone qualified state, and apply patience before epoch cap."""
        if self.stop_reason is not None:
            raise RuntimeError("Selector already stopped")
        if not math.isfinite(value) or value < 0:
            raise ValueError("Selector loss must be finite and nonnegative")
        self.epoch += 1
        if value < self.raw_best:
            self.raw_best, self.raw_epoch = value, self.epoch
        qualified = value <= 0.999 * self.best
        if qualified:
            self.best, self.selected, self.patience = value, self.epoch, 0
            if model is not None:
                self.best_state = {name: tensor.detach().clone() for name, tensor in model.state_dict().items()}
        else:
            self.patience += 1
        if self.epoch >= 12 and self.patience >= 10:
            self.stop_reason = "patience"
        elif self.epoch >= 60:
            self.stop_reason = "epoch_cap"
        return qualified

    def receipt(self) -> dict[str, int | float | str | None]:
        return {
            "epoch": self.epoch, "selected": self.selected, "best": self.best,
            "raw_best": self.raw_best, "raw_epoch": self.raw_epoch,
            "patience": self.patience, "stop_reason": self.stop_reason,
        }


@dataclass(frozen=True)
class EpochRecord:
    epoch: int
    updates: int
    batch_main_mean: float
    batch_aux_three_head_mean: float
    validation: float | None
    selected_epoch: int | None
    qualified: bool | None
    maximum_preclip_norm: float


ProgressCallback: TypeAlias = Callable[[EpochRecord], None]


def train_epoch(
    model: S2CModel, optimizer: torch.optim.AdamW, phase: PhaseData,
    weights: AuxiliaryWeights, epoch: int,
) -> EpochRecord:
    """One shuffled pass; a smaller last batch keeps its local mean and full LR."""
    model.train()
    primary_history: list[float] = []
    auxiliary_history: list[float] = []
    gradient_norms: list[float] = []
    session_array = np.asarray(phase.sessions)
    for indices in session_batches(phase.sessions, epoch):
        optimizer.zero_grad()  # Torch 2.10 default is set_to_none=True.
        main, auxiliary = model(*_input_tensors(phase.get_inputs, indices))
        losses = batch_losses(
            main.reshape(-1, STOCKS), auxiliary.reshape(-1, STOCKS, 3),
            torch.as_tensor(phase.signed_returns[indices]),
            torch.as_tensor(phase.auxiliary_returns[indices]),
            torch.as_tensor(phase.auxiliary_mask[indices]),
            session_array[indices].tolist(), torch.as_tensor(weights.values[indices]),
            weights.sessions, phase.scale,
        )
        losses.total.backward()
        norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
        optimizer.step()
        if any(not bool(torch.isfinite(parameter).all()) for parameter in model.parameters()):
            raise FloatingPointError("Nonfinite model parameters; stop without retry")
        primary_history.append(float(losses.main.detach()))
        auxiliary_history.append(float(losses.auxiliary.detach()))
        gradient_norms.append(float(norm))
    return EpochRecord(
        epoch, len(primary_history), float(np.mean(primary_history)),
        float(np.mean(auxiliary_history)), None, None, None, max(gradient_norms),
    )


def _atomic_json(path: Path, payload: object) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def save_state(model: S2CModel, path: Path) -> None:
    """Atomically save weights; caller owns the run-specific output namespace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    torch.save({name: value.detach().clone() for name, value in model.state_dict().items()}, temporary)
    os.replace(temporary, path)


def load_state(path: Path) -> S2CModel:
    """Load an independently saved phase checkpoint for frozen inference."""
    model = fresh_model()
    state = torch.load(path, map_location="cpu", weights_only=True)
    model.load_state_dict(state, strict=True)
    model.eval()
    return model


class _Recorder:
    def __init__(self, output: Path | None, model: S2CModel, phase: PhaseData, weights: AuxiliaryWeights) -> None:
        self.output = output
        if output is None:
            return
        output.mkdir(parents=True, exist_ok=True)
        # An existing start receipt is a hard refusal, never an implicit retry.
        with (output / "started.json").open("x", encoding="utf-8") as stream:
            json.dump({"status": "RUNNING", "initial_digest": state_digest(model), "scale": phase.scale,
                       "sessions": weights.sessions, "auxiliary_sessions": weights.overnight_sessions,
                       "auxiliary_global_mass": weights.mass, "initial_optimizer_state_entries": 0,
                       "runtime": configure_runtime()}, stream, indent=2, allow_nan=False)
            stream.write("\n")
        save_state(model, output / "initial_state.pt")

    def epoch(self, record: EpochRecord, model: S2CModel, selector: Selector | None) -> None:
        if self.output is None:
            return
        with (self.output / "trace.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(asdict(record), allow_nan=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        if selector is not None:
            _atomic_json(self.output / "selector_state.json", selector.receipt())
            if record.qualified:
                save_state(model, self.output / "selected_state.pt")
        else:
            save_state(model, self.output / "latest_refit_state.pt")

    def finish(self, model: S2CModel, epochs: int, selected: int, selector: Selector | None) -> None:
        if self.output is None:
            return
        save_state(model, self.output / "final_state.pt")
        _atomic_json(self.output / "completed.json", {
            "status": "COMPLETE", "epochs_executed": epochs, "selected_epochs": selected,
            "final_digest": state_digest(model), "selector": None if selector is None else selector.receipt(),
        })

    def fail(self, error: BaseException) -> None:
        if self.output is not None:
            _atomic_json(self.output / "failure.json", {
                "status": "FAILED_STOP_NO_RETRY", "error_type": type(error).__name__, "message": str(error),
            })


@dataclass(frozen=True)
class FitResult:
    model: S2CModel
    selected_epochs: int
    records: tuple[EpochRecord, ...]
    initial_digest: str
    final_digest: str
    selector: Selector | None


def train_selector(
    training: PhaseData, validation: PhaseData, *, output_dir: Path | None = None,
    progress: ProgressCallback | None = None,
) -> FitResult:
    """Fresh initial fit, qualified-best checkpoint selection, no retry path.

    Real runs must supply a fresh output directory. Omitting it is intended for
    isolated synthetic fixtures. A callback receives each persisted epoch record.
    """
    if validation.scale != training.scale:
        raise ValueError("Selector must use the initial training phase scale")
    weights = auxiliary_weights(training.sessions, training.overnight, training.auxiliary_mask)
    model = fresh_model()
    initial_digest = state_digest(model)
    optimizer = make_optimizer(model)
    recorder = _Recorder(output_dir, model, training, weights)
    selector = Selector()
    records: list[EpochRecord] = []
    try:
        while selector.stop_reason is None:
            basic = train_epoch(model, optimizer, training, weights, selector.epoch + 1)
            value = validation_loss(model, validation)
            qualified = selector.update(value, model)
            record = EpochRecord(basic.epoch, basic.updates, basic.batch_main_mean,
                                 basic.batch_aux_three_head_mean, value, selector.selected,
                                 qualified, basic.maximum_preclip_norm)
            records.append(record)
            recorder.epoch(record, model, selector)
            if progress is not None:
                progress(record)
        if selector.best_state is None:
            raise RuntimeError("Selector has no qualified checkpoint")
        model.load_state_dict(selector.best_state, strict=True)
        model.eval()
        recorder.finish(model, selector.epoch, selector.selected, selector)
    except BaseException as error:
        recorder.fail(error)
        raise
    return FitResult(model, selector.selected, tuple(records), initial_digest, state_digest(model), selector)


def train_refit(
    phase: PhaseData, selected_epochs: int, *, output_dir: Path | None = None,
    progress: ProgressCallback | None = None,
) -> FitResult:
    """Fresh seed42 restricted refit for the independent selector's exact epoch count."""
    if isinstance(selected_epochs, bool) or not isinstance(selected_epochs, int) or not 1 <= selected_epochs <= 60:
        raise ValueError("Selected epochs must be an integer from1 through60")
    weights = auxiliary_weights(phase.sessions, phase.overnight, phase.auxiliary_mask)
    model = fresh_model()
    initial_digest = state_digest(model)
    optimizer = make_optimizer(model)
    recorder = _Recorder(output_dir, model, phase, weights)
    records: list[EpochRecord] = []
    try:
        for epoch in range(1, selected_epochs + 1):
            record = train_epoch(model, optimizer, phase, weights, epoch)
            records.append(record)
            recorder.epoch(record, model, None)
            if progress is not None:
                progress(record)
        model.eval()
        recorder.finish(model, selected_epochs, selected_epochs, None)
    except BaseException as error:
        recorder.fail(error)
        raise
    return FitResult(model, selected_epochs, tuple(records), initial_digest, state_digest(model), None)
