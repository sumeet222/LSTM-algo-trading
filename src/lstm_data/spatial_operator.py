"""Frozen five-name D9 rank-two operator; synthetic readiness, no fit executor."""

from __future__ import annotations

import math

import torch
from torch import Tensor, nn

from .neural_engine import SharedLSTM
from .p3_domain import MODE, UniverseSpec, synthetic_id


class StockMixer(nn.Module):
    """LN on hidden coordinates, bias-free 5→2→5 on the stock axis only."""

    def __init__(self) -> None:
        super().__init__()
        self.norm = nn.LayerNorm(32, eps=1e-5, elementwise_affine=False)
        self.m1 = nn.Parameter(torch.empty(2, 5))
        self.m2 = nn.Parameter(torch.zeros(5, 2))
        # Same seeded standard initialization as a bias-free Linear(5, 2).
        # D9 allows standard small-matrix initialization; there is no initializer search.
        nn.init.kaiming_uniform_(self.m1, a=math.sqrt(5))

    def components(self, hidden: Tensor) -> tuple[Tensor, Tensor, Tensor, Tensor, Tensor]:
        if (
            hidden.ndim not in (2, 3)
            or tuple(hidden.shape[-2:]) != (5, 32)
            or hidden.numel() == 0
            or hidden.dtype != self.m1.dtype
            or hidden.device != self.m1.device
            or not bool(torch.isfinite(hidden).all())
        ):
            raise ValueError("FINITE_GROUPED_FIVE_BY_32_HIDDEN_REQUIRED")
        normalized = self.norm(hidden)
        compressed = self.m1 @ normalized
        activated = torch.nn.functional.gelu(compressed, approximate="none")
        message = self.m2 @ activated
        transformed = hidden + message
        if not bool(torch.isfinite(transformed).all()):
            raise ValueError("FINITE_SP3_RESIDUAL_REQUIRED")
        return normalized, compressed, activated, message, transformed

    def forward(self, hidden: Tensor) -> Tensor:
        return self.components(hidden)[-1]


class SpatialLSTM(nn.Module):
    """MC0 shared encoder, per-origin StockMixer and original dropout/shared head."""

    input_dim = 21

    def __init__(self, universe: UniverseSpec, *, mode: str = MODE) -> None:
        super().__init__()
        if mode != MODE:
            raise ValueError("SP3_SCIENTIFIC_ACTIVATION_HOLD")
        synthetic_id(universe.version)
        self.universe = universe
        self.core = SharedLSTM(21)
        self.mixer = StockMixer()

    def encode_grouped(self, x: Tensor) -> Tensor:
        if x.ndim != 3 or not len(x) or len(x) % 5 or tuple(x.shape[1:]) != (48, 21):
            raise ValueError("SP3_COMPLETE_FIVE_NAME_ORIGINS_REQUIRED")
        grouped = x.reshape(-1, 5, 48, 21)
        if not torch.equal(grouped[..., 16:], grouped[:, :1, :, 16:].expand(-1, 5, -1, -1)):
            raise ValueError("SP3_SHARED_D7_PER_ORIGIN_REQUIRED")
        return self.core.encode(x).reshape(-1, 5, 32)

    def forward(self, x: Tensor) -> Tensor:
        hidden = self.mixer(self.encode_grouped(x))
        # Dropout is applied once, after spatial exchange, immediately before the head.
        return self.core.head(self.core.dropout(hidden.reshape(-1, 32))).squeeze(-1)
