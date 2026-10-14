"""Frozen TM0 computation and complete-session training; no data acquisition."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Iterator

import numpy as np
import torch
from torch import Tensor, nn

SEEDS = (42, 123, 2026)
MODEL_VERSION = "SYN:TM0:1"


def seed_all(seed: int) -> None:
    """Explicit same-device synthetic RNG stream; no cross-device equality claim."""
    if seed not in SEEDS:
        raise ValueError("REGISTERED_SEED_REQUIRED")
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)


class SharedLSTM(nn.Module):
    """Independent zero-state 48-step stock sequences and one shared scalar head."""

    def __init__(self, input_dim: int = 16) -> None:
        super().__init__()
        if input_dim not in (16, 21, 23):
            raise ValueError("DECLARED_INPUT_DIMENSION_REQUIRED")
        self.input_dim = input_dim
        self.lstm = nn.LSTM(input_dim, 32, num_layers=1, batch_first=True)
        self.dropout = nn.Dropout(0.10)
        self.head = nn.Linear(32, 1)

    def forward(self, x: Tensor) -> Tensor:
        parameter = self.head.weight
        if (
            x.ndim != 3
            or tuple(x.shape[1:]) != (48, self.input_dim)
            or x.shape[0] == 0
            or x.dtype != parameter.dtype
            or x.device != parameter.device
            or not bool(torch.isfinite(x).all())
        ):
            raise ValueError("FINITE_EXACT_48_STEP_DTYPE_DEVICE_REQUIRED")
        # Omitted h0/c0 are fresh zeros on every call; no persistent recurrent state.
        _, (hidden, _) = self.lstm(x)
        return self.head(self.dropout(hidden[-1])).squeeze(-1)


@dataclass(frozen=True)
class SessionBatch:
    """Whole sessions, padded absent origins only; never incomplete stock rows."""

    ids: tuple[str, ...]
    inputs: Tensor
    targets: Tensor
    origins: Tensor

    def validate(self) -> None:
        n = len(self.ids)
        if (
            not n
            or len(set(self.ids)) != n
            or self.inputs.ndim != 5
            or tuple(self.inputs.shape[:4]) != (n, 2, 5, 48)
            or self.inputs.shape[-1] not in (16, 21, 23)
            or tuple(self.targets.shape) != (n, 2, 5)
            or tuple(self.origins.shape) != (n, 2)
            or self.origins.dtype != torch.bool
            or not bool(self.origins.any(dim=1).all())
            or self.inputs.dtype != torch.float32
            or self.targets.dtype != torch.float32
            or self.inputs.device != self.targets.device
            or self.inputs.device != self.origins.device
            or not bool(torch.isfinite(self.inputs).all())
            or not bool(torch.isfinite(self.targets).all())
        ):
            raise ValueError("COMPLETE_FINITE_FIVE_STOCK_SESSION_BATCH_REQUIRED")

        if self.inputs.shape[-1] in (21, 23):
            valid = self.inputs[self.origins][..., 16:21]
            if not torch.equal(valid, valid[:, :1].expand(-1, 5, -1, -1)):
                raise ValueError("ONE_SHARED_D7_HISTORY_REQUIRED")
        if self.inputs.shape[-1] == 23:
            from .peer_inputs import peer_summaries

            for values in self.inputs[self.origins]:
                expected = torch.tensor(
                    peer_summaries(values[:, :, :16].detach().cpu().numpy()),
                    dtype=values.dtype,
                    device=values.device,
                )
                if not torch.equal(values[:, :, 21:], expected):
                    raise ValueError("EXACT_CANONICAL_E5_PEER_CHANNELS_REQUIRED")


def session_losses(prediction: Tensor, target: Tensor, origins: Tensor) -> Tensor:
    """Mean over five stocks, then eligible origins; preserve equal session mass."""
    if (
        prediction.shape != target.shape
        or prediction.ndim != 3
        or tuple(prediction.shape[1:]) != (2, 5)
        or tuple(origins.shape) != tuple(prediction.shape[:2])
        or origins.dtype != torch.bool
        or not bool(origins.any(dim=1).all())
        or not bool(torch.isfinite(prediction).all())
        or not bool(torch.isfinite(target).all())
    ):
        raise ValueError("FINITE_COMPLETE_SESSION_LOSS_REQUIRED")
    by_origin = (prediction - target).square().mean(dim=2)
    return (by_origin * origins).sum(dim=1) / origins.sum(dim=1)


def batch_prediction(model: nn.Module, batch: SessionBatch) -> Tensor:
    batch.validate()
    valid = batch.inputs[batch.origins]  # (eligible origins, five, 48, 16)
    values = model(valid.reshape(-1, 48, valid.shape[-1])).reshape(-1, 5)
    output = torch.zeros_like(batch.targets)
    output[batch.origins] = values
    return output


def session_batches(
    count: int, seed: int, epoch: int, *, shuffle: bool
) -> Iterator[tuple[int, ...]]:
    """Each eligible session once, 16-session target and retained smaller final batch."""
    if count <= 0 or epoch < 1 or seed not in SEEDS:
        raise ValueError("VALID_SESSION_SAMPLER_REQUIRED")
    order = list(range(count))
    if shuffle:
        value = int.from_bytes(hashlib.sha256(f"{seed}:{epoch}".encode()).digest(), "big")
        random.Random(value).shuffle(order)
    for start in range(0, count, 16):
        yield tuple(order[start : start + 16])


def optimizer(model: nn.Module) -> torch.optim.AdamW:
    """Exactly two disjoint exhaustive frozen AdamW parameter groups."""
    weights, biases = [], []
    for name, parameter in model.named_parameters():
        if parameter.requires_grad:
            (weights if parameter.ndim == 2 else biases).append(parameter)
    return torch.optim.AdamW(
        [{"params": weights, "weight_decay": 0.01}, {"params": biases, "weight_decay": 0.0}],
        lr=0.001,
        betas=(0.9, 0.999),
        eps=1e-8,
        amsgrad=False,
    )


def clip(model: nn.Module) -> float:
    """One direction-preserving global L2 clip; nonfinite norms fail closed."""
    return float(nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True))


def norm_summary(values: tuple[float, ...]) -> dict:
    if not values or not all(np.isfinite(values)):
        raise ValueError("FINITE_GRADIENT_TELEMETRY_REQUIRED")
    array = np.asarray(values)
    multiplier = np.minimum(1.0, 1.0 / (array + 1e-6))
    return {
        "median": float(np.median(array)),
        "p90": float(np.quantile(array, 0.90)),
        "p95": float(np.quantile(array, 0.95)),
        "p99": float(np.quantile(array, 0.99)),
        "max": float(array.max()),
        "clipped_fraction": float(np.mean(array > 1.0)),
        "multiplier_min": float(multiplier.min()),
        "multiplier_median": float(np.median(multiplier)),
        "nonfinite_count": 0,
        "sustained_clipping_warning": bool(np.mean(array > 1.0) > 0.5),
    }
