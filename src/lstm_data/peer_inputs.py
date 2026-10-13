"""Bound synthetic leave-one-out M1 summaries; ephemeral E5 input, no model."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from torch import Tensor

from .baseline_fit import FitData, Preparation
from .baseline_inputs import BaselineInput
from .baseline_ridge import LAGS, lag_vectors
from .config import digest
from .ft0_transforms import ORDER, identity
from .labels import FitWindow
from .neural_engine import SessionBatch
from .neural_market import MarketEvidence, MarketNeuralView, make_market_view, market_input
from .p3_domain import Permission, UniverseSpec

M1_INDEX = ORDER.index("M1")
PEER_VERSION = "SYN:E5_PEER_INPUT:1"


def peer_summaries(values: np.ndarray) -> np.ndarray:
    """Five ×48×16 already-scaled values → five ×48×2, population four-peer SD."""
    if values.shape != (5, 48, 16) or not np.isfinite(values).all():
        raise ValueError("FIVE_COMPLETE_FINITE_48_STEP_FT0_PEERS_REQUIRED")
    z = values[:, :, M1_INDEX]
    output = []
    # Centered differences avoid catastrophic cancellation in E[z²]-E[z]².
    for i in range(5):
        peers = z[np.arange(5) != i].astype(np.float64)
        mean = peers.mean(axis=0)
        dispersion = np.sqrt(np.mean((peers - mean) ** 2, axis=0))
        output.append(np.stack((mean, dispersion), axis=-1))
    result = np.stack(output)
    if not np.isfinite(result).all():
        raise ValueError("NONFINITE_PEER_SUMMARY")
    return result


def peer_input(
    row: BaselineInput,
    prep: Preparation,
    history: MarketEvidence,
    permission: Permission,
    context: str = "ASOF",
) -> tuple[BaselineInput, np.ndarray, str]:
    """Canonical P2 validation includes every peer's own-step clocks and fit/action identity."""
    processed, trace = market_input(row, prep, history, permission, context)
    peers = peer_summaries(np.asarray(processed.stock.values, dtype=float))
    binding = identity(
        [PEER_VERSION, row.universe.universe_id, trace, peers.tolist(), peer_code_identity()]
    )
    return processed, peers, binding


def peer_lag_vectors(
    row: BaselineInput,
    prep: Preparation,
    history: MarketEvidence,
    permission: Permission,
    context: str = "ASOF",
) -> tuple[tuple[float, ...], ...]:
    """Exact original147 prefix, then seven lag-major [peer mean, dispersion] pairs."""
    processed, peers, _ = peer_input(row, prep, history, permission, context)
    prefix = lag_vectors(processed, permission, market=True, allow_synthetic=True, context=context)
    return tuple(
        base + tuple(float(v) for lag in LAGS for v in peers[i, 47 - lag])
        for i, base in enumerate(prefix)
    )


def peer_code_identity() -> str:
    return identity(
        [
            PEER_VERSION,
            ORDER,
            LAGS,
            digest(Path(__file__)),
            digest(Path(__file__).with_name("neural_market.py")),
            digest(Path(__file__).with_name("baseline_inputs.py")),
            digest(Path(__file__).with_name("ft0_transforms.py")),
            digest(Path(__file__).with_name("baseline_fit.py")),
            digest(Path(__file__).with_name("baseline_ridge.py")),
            digest(Path(__file__).with_name("peer_ridge.py")),
        ]
    )


def _view_binding(view: MarketNeuralView) -> str:
    return identity(
        [
            PEER_VERSION,
            view.version,
            view.preparation_id,
            view.stock.universe.universe_id,
            view.stock.preparation_id,
            view.stock.window,
            view.stock.content_hash,
            view.stock.rows,
            view.market_hash,
            view.market_rows,
            peer_code_identity(),
        ]
    )


@dataclass(frozen=True)
class PeerBatch:
    """Data-only 23-channel batch; intentionally not accepted by the neural engine."""

    base: SessionBatch
    inputs: Tensor
    input_id: str

    def __post_init__(self) -> None:
        self.base.validate()
        if (
            self.inputs.shape != self.base.inputs.shape[:-1] + (23,)
            or self.inputs.dtype != torch.float32
            or self.inputs.device.type != "cpu"
            or not bool(torch.isfinite(self.inputs).all())
            or not torch.equal(self.inputs[..., :21], self.base.inputs)
            or not self.input_id.startswith("SYN:E5_PEER_BATCH:")
        ):
            raise ValueError("EXACT_EPHEMERAL23_MC0_PREFIX_REQUIRED")
        for d in range(len(self.base.ids)):
            for o in range(2):
                if bool(self.base.origins[d, o]):
                    expected = torch.tensor(
                        peer_summaries(self.base.inputs[d, o, :, :, :16].numpy()),
                        dtype=torch.float32,
                    )
                    if not torch.equal(self.inputs[d, o, :, :, 21:], expected):
                        raise ValueError("CANONICAL_FOUR_PEER_BATCH_REQUIRED")


@dataclass(frozen=True)
class PeerView:
    """Only references existing canonical tables/indices; never stores dense windows."""

    market: MarketNeuralView
    universe: UniverseSpec
    binding_id: str

    def batch(self, positions: tuple[int, ...]) -> PeerBatch:
        if self.universe != self.market.stock.universe or self.binding_id != _view_binding(
            self.market
        ):
            raise ValueError("PEER_VIEW_SOURCE_FIT_ORDER_CODE_CHANGED")
        base = self.market.batch(positions)  # Both canonical tensor hashes checked here.
        values = torch.zeros(base.inputs.shape[:-1] + (2,), dtype=torch.float32)
        for day in range(len(base.ids)):
            for origin in range(2):
                if bool(base.origins[day, origin]):
                    peers = peer_summaries(base.inputs[day, origin, :, :, :16].numpy())
                    values[day, origin] = torch.tensor(peers, dtype=torch.float32)
        return PeerBatch(
            base,
            torch.cat((base.inputs, values), dim=-1),
            "SYN:E5_PEER_BATCH:" + identity([self.binding_id, base.ids, positions]),
        )


def make_peer_view(
    data: FitData,
    window: FitWindow,
    prep: Preparation,
    permission: Permission,
    history: MarketEvidence,
    *,
    allow_synthetic: bool = False,
) -> PeerView:
    view = make_market_view(
        data, window, prep, permission, history, allow_synthetic=allow_synthetic
    )
    return PeerView(view, data.universe, _view_binding(view))
