"""Additive E5 bridge over the unchanged, clock-bound P4.7 peer math."""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
import torch
from torch import Tensor

from .baseline_fit import FitData, Preparation
from .baseline_inputs import BaselineInput
from .labels import FitWindow
from .neural_engine import SessionBatch
from .neural_market import MarketEvidence
from .neural_models import NeuralModel, architecture_of
from .p3_domain import Permission, synthetic_id
from .peer_inputs import M1_INDEX, PeerView, make_peer_view, peer_input


@dataclass(frozen=True)
class E5View:
    """No stored dense peer history: delegate each ephemeral batch to PeerView."""

    peer: PeerView

    @property
    def sessions(self):
        return self.peer.market.sessions

    @property
    def rows(self):
        return self.peer.market.rows

    @property
    def values(self) -> Tensor:
        return self.peer.market.values

    @property
    def version(self) -> str:
        return self.peer.binding_id

    @property
    def excluded(self):
        return self.peer.market.excluded

    def batch(self, positions: tuple[int, ...]) -> SessionBatch:
        bound = self.peer.batch(positions)
        result = replace(bound.base, inputs=bound.inputs)
        result.validate()
        return result


def make_e5_view(
    data: FitData,
    window: FitWindow,
    prep: Preparation,
    permission: Permission,
    history: MarketEvidence,
    *,
    allow_synthetic: bool = False,
) -> E5View:
    return E5View(
        make_peer_view(data, window, prep, permission, history, allow_synthetic=allow_synthetic)
    )


def e5_input(
    row: BaselineInput,
    prep: Preparation,
    history: MarketEvidence,
    permission: Permission,
) -> tuple[Tensor, str]:
    """Forecast-only input: same 21 prefix and own-step clocks, no labels/exits."""
    processed, peers, binding = peer_input(row, prep, history, permission)
    m = processed.market
    assert m is not None and m.values is not None
    stock = np.asarray(processed.stock.values, dtype=np.float32)
    market = np.broadcast_to(np.asarray(m.values, dtype=np.float32), (5, 48, 5))
    return torch.tensor(
        np.concatenate((stock, market, peers), axis=-1), dtype=torch.float32
    ), binding


def trace_e5(model: NeuralModel, values: Tensor, provenance: str) -> dict:
    """On-demand T1 for one fabricated origin; no full tensor or future target dump."""
    synthetic_id(provenance)
    if architecture_of(model) != "E5" or tuple(values.shape) != (5, 48, 23):
        raise ValueError("EXACT_E5_FIVE_SCORE_TRACE_REQUIRED")
    training = model.training
    model.eval()
    try:
        with torch.no_grad():
            scores = model(values)
            return {
                "scope": "ENGINEERING_SYNTHETIC_ONLY",
                "provenance": provenance,
                "endpoint_M1": values[:, -1, M1_INDEX].tolist(),
                "endpoint_peer": values[:, -1, 21:].tolist(),
                "scores": scores.tolist(),
                "architecture": "E5",
                "parameters": sum(p.numel() for p in model.parameters()),
            }
    finally:
        model.train(training)
