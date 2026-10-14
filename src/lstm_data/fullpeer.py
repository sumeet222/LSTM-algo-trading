"""Synthetic D9 inputs over existing P2/P4 canonical tables and clocks."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import torch
from torch import Tensor

from .baseline_fit import FitData, Preparation
from .baseline_inputs import BaselineInput
from .config import digest
from .ft0_transforms import identity
from .labels import FitWindow
from .neural_engine import SessionBatch
from .neural_market import (
    MarketEvidence,
    MarketNeuralView,
    make_market_view,
    market_input,
    market_preparation_identity,
)
from .p3_domain import MODE, Permission, UniverseSpec, synthetic_id

FULLPEER = "FULLPEER"
SP3 = "SP3"


def require_mode(mode: str) -> None:
    if mode != MODE:
        raise ValueError("P4_11_SCIENTIFIC_ACTIVATION_HOLD")


def operator_code_identity() -> str:
    """Version-safe additive binding; does not relabel any old P4 artifact."""
    folder = Path(__file__).parent
    return identity(
        [
            digest(folder / name)
            for name in (
                "fullpeer.py",
                "spatial_operator.py",
                "operator_artifacts.py",
                "neural_engine.py",
                "neural_models.py",
                "neural_market.py",
                "neural_data.py",
                "baseline_inputs.py",
                "baseline_fit.py",
                "ft0_transforms.py",
                "m2.py",
                "clocks.py",
            )
        ]
    )


def fullpeer_values(joined: Tensor) -> Tensor:
    """Ephemeral [...,5,48,21]→[...,5,48,85], excluding self in canonical order."""
    if (
        joined.ndim < 3
        or tuple(joined.shape[-3:]) != (5, 48, 21)
        or joined.numel() == 0
        or joined.dtype != torch.float32
        or not bool(torch.isfinite(joined).all())
        or not torch.equal(joined[..., 16:], joined[..., :1, :, 16:].expand_as(joined[..., 16:]))
    ):
        raise ValueError("COMPLETE_FINITE_CANONICAL_MC0_PANEL_REQUIRED")
    return torch.stack(
        [
            torch.cat(
                (joined[..., i, :, :], *[joined[..., j, :, :16] for j in range(5) if j != i]),
                dim=-1,
            )
            for i in range(5)
        ],
        dim=-3,
    )


def strict_masks(row: BaselineInput) -> None:
    if any(
        type(b) is not bool or not b for stock in row.stock.mask for step in stock for b in step
    ):
        raise ValueError("KNOWN_COMPLETE_STOCK_MASK_REQUIRED")
    if row.market is not None and any(type(b) is not bool for b in row.market.valid_mask):
        raise ValueError("KNOWN_D7_MASK_REQUIRED")


@dataclass(frozen=True)
class OperatorBinding:
    """Ordered axis + source/clock/target/preprocessing/code, no scientific authority."""

    universe: UniverseSpec
    source: str
    preparation: str
    target: str
    code: str
    mode: str = MODE

    def __post_init__(self) -> None:
        require_mode(self.mode)
        synthetic_id(self.universe.version)
        if any(
            not isinstance(v, str) or not v for v in (self.source, self.preparation, self.target)
        ):
            raise ValueError("EXACT_OPERATOR_SOURCE_PREPARATION_TARGET_REQUIRED")
        if self.code != operator_code_identity():
            raise ValueError("OPERATOR_CODE_REBUILD_REQUIRED")

    @property
    def binding_id(self) -> str:
        return identity(
            [
                self.universe.universe_id,
                self.source,
                self.preparation,
                self.target,
                self.code,
                self.mode,
            ]
        )


@dataclass(frozen=True)
class OperatorInput:
    """One forecast origin; exact MC0 prefix remains the trusted canonical representation."""

    binding: OperatorBinding
    architecture: str
    prefix: Tensor
    values: Tensor
    trace: str
    content: str

    def validate(self) -> None:
        require_mode(self.binding.mode)
        if self.binding.code != operator_code_identity():
            raise ValueError("OPERATOR_CODE_REBUILD_REQUIRED")
        if self.architecture not in (FULLPEER, SP3) or not self.trace:
            raise ValueError("P4_11_EXPLICIT_ARCHITECTURE_TRACE_REQUIRED")
        expected = fullpeer_values(self.prefix) if self.architecture == FULLPEER else self.prefix
        # For SP3 this also validates complete shared-market geometry.
        if self.architecture == SP3:
            fullpeer_values(self.prefix)
        if tuple(self.prefix.shape) != (5, 48, 21) or not torch.equal(self.values, expected):
            raise ValueError("CANONICAL_OPERATOR_INPUT_REQUIRED")
        if self.content != identity([self.prefix.tolist(), self.values.tolist(), self.trace]):
            raise ValueError("OPERATOR_INPUT_MUTATED")


def operator_input(
    row: BaselineInput,
    prep: Preparation,
    history: MarketEvidence,
    permission: Permission,
    *,
    architecture: str,
    mode: str = MODE,
) -> OperatorInput:
    """No future label/exit argument; reuse canonical P2 application and every own-step clock."""
    require_mode(mode)
    if architecture not in (FULLPEER, SP3):
        raise ValueError("P4_11_EXPLICIT_ARCHITECTURE_REQUIRED")
    permission.ensure()
    if row.universe != prep.universe:
        raise ValueError("OPERATOR_ORDERED_UNIVERSE_REQUIRED")
    strict_masks(row)
    processed, trace = market_input(row, prep, history, permission)
    strict_masks(processed)
    m = processed.market
    assert m is not None and m.values is not None
    prefix = torch.tensor(
        np.concatenate(
            (
                np.asarray(processed.stock.values, dtype=np.float32),
                np.broadcast_to(np.asarray(m.values, dtype=np.float32), (5, 48, 5)),
            ),
            axis=-1,
        ),
        dtype=torch.float32,
    )
    source = identity([row.stock.source_binding, row.stock.action_binding, history.version])
    binding = OperatorBinding(
        row.universe,
        source,
        market_preparation_identity(prep),
        prep.tg0_floor.floor_id,
        operator_code_identity(),
    )
    values = fullpeer_values(prefix) if architecture == FULLPEER else prefix
    result = OperatorInput(
        binding,
        architecture,
        prefix,
        values,
        trace,
        identity([prefix.tolist(), values.tolist(), trace]),
    )
    result.validate()
    return result


def _view_binding(view: MarketNeuralView) -> str:
    return identity(
        [
            view.version,
            view.stock.universe.universe_id,
            view.preparation_id,
            view.stock.window,
            view.stock.content_hash,
            view.stock.rows,
            view.market_rows,
            view.market_hash,
            operator_code_identity(),
        ]
    )


@dataclass(frozen=True)
class FullPeerView:
    """One reference to the original indexed stock/D7 tables, no stored peer windows."""

    market: MarketNeuralView
    universe: UniverseSpec
    binding_id: str

    @property
    def sessions(self) -> tuple[str, ...]:
        return self.market.sessions

    @property
    def rows(self):
        return self.market.rows

    @property
    def version(self) -> str:
        return self.binding_id

    def batch(self, positions: tuple[int, ...]) -> SessionBatch:
        if self.universe != self.market.stock.universe or self.binding_id != _view_binding(
            self.market
        ):
            raise ValueError("FULLPEER_ORDER_SOURCE_FIT_CODE_CHANGED")
        base = self.market.batch(positions)
        result = replace(base, inputs=fullpeer_values(base.inputs))
        result.validate()
        return result


def make_fullpeer_view(
    data: FitData,
    window: FitWindow,
    prep: Preparation,
    permission: Permission,
    history: MarketEvidence,
    *,
    allow_synthetic: bool = False,
    mode: str = MODE,
) -> FullPeerView:
    require_mode(mode)
    if not allow_synthetic:
        raise ValueError("FULLPEER_SYNTHETIC_OPT_IN_REQUIRED")
    permission.ensure()
    for row in data.origins:
        strict_masks(row.inputs)
    view = make_market_view(data, window, prep, permission, history, allow_synthetic=True)
    return FullPeerView(view, data.universe, _view_binding(view))


@dataclass(frozen=True)
class OperatorBatch:
    """Complete-session binding carried alongside existing SessionBatch tensors."""

    binding: OperatorBinding
    architecture: str
    batch: SessionBatch
    content: str

    def validate(self) -> None:
        require_mode(self.binding.mode)
        self.batch.validate()
        width = {FULLPEER: 85, SP3: 21}.get(self.architecture)
        if (
            self.binding.code != operator_code_identity()
            or self.batch.inputs.shape[-1] != width
            or self.content
            != identity(
                [
                    self.binding.binding_id,
                    self.architecture,
                    self.batch.ids,
                    self.batch.inputs.tolist(),
                    self.batch.targets.tolist(),
                    self.batch.origins.tolist(),
                ]
            )
        ):
            raise ValueError("BOUND_OPERATOR_SESSION_CONTENT_REQUIRED")


def operator_batch(
    market: MarketNeuralView,
    positions: tuple[int, ...],
    *,
    architecture: str,
    mode: str = MODE,
) -> OperatorBatch:
    """MC0/full-peer/SP3 reuse the very same tables, eligibility and mature target rows."""
    require_mode(mode)
    if architecture not in (FULLPEER, SP3):
        raise ValueError("P4_11_EXPLICIT_ARCHITECTURE_REQUIRED")
    base = market.batch(positions)
    binding = OperatorBinding(
        market.stock.universe,
        market.version,
        market.preparation_id,
        # The stock view version binds actual TG0 floor, contents and maturity membership.
        market.stock.version,
        operator_code_identity(),
    )
    batch = replace(base, inputs=fullpeer_values(base.inputs)) if architecture == FULLPEER else base
    result = OperatorBatch(
        binding,
        architecture,
        batch,
        identity(
            [
                binding.binding_id,
                architecture,
                batch.ids,
                batch.inputs.tolist(),
                batch.targets.tolist(),
                batch.origins.tolist(),
            ]
        ),
    )
    result.validate()
    return result
