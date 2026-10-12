"""Thin synthetic-only P2 certificate adapter and shared indexed neural views."""

from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd
import torch
from torch import Tensor

from .baseline_fit import FitData, Preparation
from .baseline_ridge import RidgeOrigin, fitting_origins
from .clocks import utc
from .ft0_transforms import FitObservation, identity
from .hourly_proxy import apply_proxy_floor
from .labels import FitWindow
from .neural_engine import SessionBatch
from .p3_domain import Permission, UniverseSpec


def validate_label_clocks(data: FitData) -> None:
    """Finite label clocks are mandatory before any fitting-membership comparison."""
    for row in data.origins:
        row.validate(data.universe)
        for stamp in (row.label.maturity, row.label.plan.cutoff, row.label.plan.exit):
            if stamp is None:
                raise ValueError("FINITE_SYNTHETIC_LABEL_CLOCK_REQUIRED")
            utc(stamp)  # NaT comparisons can otherwise silently return False.


def preparation_identity(preparation: Preparation) -> str:
    """Bind the actual stock-only fit objects, excluding unused market payloads."""
    if preparation.market_scaler is not None or preparation.market_floors is not None:
        raise ValueError("STOCK_ONLY_TM0_PREPROCESS_REQUIRED")
    return identity([preparation.universe.universe_id, preparation.window,
                     preparation.stock_scaler.certificate_id,
                     preparation.stock_floors.certificate_id, preparation.tg0_floor.floor_id])


def data_identity(data: FitData) -> str:
    """Hash explicit input/label contents without repeatedly repr-printing certificates."""
    times: dict[pd.Timestamp, str] = {}

    def clock(value: pd.Timestamp | None) -> str | None:
        if value is None:
            return None
        if value not in times:
            times[value] = utc(value).isoformat()
        return times[value]

    origins = []
    for row in data.origins:
        inputs, stock = row.inputs, row.inputs.stock
        origins.append(identity([
            inputs.input_id, inputs.universe.universe_id, inputs.plan,
            [(s.session, s.slot, clock(s.start), clock(s.end)) for s in stock.steps],
            stock.channels, stock.raw_values, stock.mask, stock.lineage,
            stock.source_binding, stock.action_binding, stock.synthetic, stock.source_only,
            stock.input_eligible, stock.research_ready,
            tuple(tuple(tuple(clock(t) for t in step) for step in symbol)
                  for symbol in inputs.available_at),
            inputs.stock_scaler.certificate_id, inputs.stock_floors.certificate_id,
            row.label,
        ]))
    def records(rows: tuple[FitObservation, ...]) -> list[tuple[object, ...]]:
        return [(r.symbol, clock(r.timestamp), r.kind, r.key, r.value, r.source_id,
                 r.source_binding, r.action_binding, r.basis, clock(r.available_at),
                 r.origin, r.label, r.source_version, r.dictionary_id) for r in rows]

    return identity([data.universe.universe_id, data.basis, origins,
                     records(data.stock_records), records(data.floor_records)])


@dataclass(frozen=True)
class IndexedOrigin:
    session: str
    origin: int
    indices: tuple[tuple[int, ...], ...]
    targets: tuple[float, ...]


@dataclass(frozen=True)
class NeuralView:
    """One canonical step table with lightweight indices, not stored 48-step windows."""

    universe: UniverseSpec
    version: str
    values: Tensor
    rows: tuple[IndexedOrigin, ...]
    sessions: tuple[str, ...]
    preparation_id: str
    window: FitWindow
    content_hash: str
    excluded: tuple[tuple[tuple[str, int], str], ...] = ()

    def __post_init__(self) -> None:
        if (
            not self.version.startswith("SYN:NEURAL_DATA:")
            or self.values.ndim != 2 or self.values.shape[1] != 16
            or self.values.dtype != torch.float32 or self.values.device.type != "cpu"
            or not bool(torch.isfinite(self.values).all())
            or self.sessions != tuple(sorted(set(self.sessions)))
            or len({(r.session, r.origin) for r in self.rows}) != len(self.rows)
            or any(r.origin not in (1, 2) or len(r.targets) != 5
                   or not all(math.isfinite(v) for v in r.targets)
                   or len(r.indices) != 5 or any(len(s) != 48 for s in r.indices)
                   or any(i < 0 or i >= len(self.values) for s in r.indices for i in s)
                   for r in self.rows)
        ):
            raise ValueError("SYNTHETIC_COMPLETE_INDEXED_VIEW_REQUIRED")

    def verify(self) -> None:
        # Tensor mutability cannot silently change a supposedly immutable dataset.
        if identity(self.values.tolist()) != self.content_hash:
            raise ValueError("CANONICAL_NEURAL_DATA_MUTATED")

    def batch(self, positions: tuple[int, ...]) -> SessionBatch:
        self.verify()
        if not positions or len(set(positions)) != len(positions):
            raise ValueError("UNIQUE_SESSION_POSITIONS_REQUIRED")
        selected = tuple(self.sessions[i] for i in positions)
        x = torch.zeros(len(selected), 2, 5, 48, 16)
        y = torch.zeros(len(selected), 2, 5)
        mask = torch.zeros(len(selected), 2, dtype=torch.bool)
        for i, day in enumerate(selected):
            for row in self.rows:
                if row.session == day:
                    x[i, row.origin - 1] = self.values[torch.tensor(row.indices)]
                    y[i, row.origin - 1] = torch.tensor(row.targets)
                    mask[i, row.origin - 1] = True
        batch = SessionBatch(selected, x, y, mask)
        batch.validate()
        return batch


def make_view(
    data: FitData, window: FitWindow, preparation: Preparation, permission: Permission,
    *, allow_synthetic: bool = False,
) -> NeuralView:
    """Reuse mature P2 membership, scaler application, exact windows and TG0 math."""
    data.validate(permission, allow_synthetic)
    validate_label_clocks(data)
    accepted, _ = fitting_origins(data.origins, data.universe, window)
    return view_from_origins(data, accepted, window, preparation, permission)


def view_from_origins(
    data: FitData, origins: tuple[RidgeOrigin, ...], window: FitWindow,
    preparation: Preparation, permission: Permission,
) -> NeuralView:
    data.validate(permission, True)
    validate_label_clocks(data)
    accepted, rejected = fitting_origins(origins, data.universe, window)
    owned = {id(row) for row in data.origins}
    if (not accepted or rejected or preparation.universe != data.universe
            or any(id(row) not in owned for row in origins)):
        raise ValueError("SYNTHETIC_PERMITTED_POPULATION_REQUIRED")
    table: dict[tuple[str, str, int], int] = {}
    values: list[tuple[float, ...]] = []
    rows, origin_keys, excluded = [], set(), []
    for origin in origins:
        origin.validate(data.universe)
        key = (origin.inputs.plan.session, origin.inputs.plan.origin)
        if key in origin_keys:
            raise ValueError("DUPLICATE_NEURAL_ORIGIN")
        origin_keys.add(key)
        context = "ASOF" if window.phase == "INNER_VALIDATION" else "HISTORICAL_TRAINING"
        if context == "ASOF" and any(
            step.end < preparation.window.fitted_at for step in origin.inputs.stock.steps
        ):
            excluded.append((key, "SCALER_NOT_AVAILABLE_AT_EVERY_HISTORICAL_STEP"))
            continue
        processed = preparation.apply(origin.inputs, context)
        processed.validate(permission, allow_synthetic=True, context=context)
        indices = []
        for symbol, stock in zip(data.universe.symbols, processed.stock.values):
            stock_indices = []
            for step, row in zip(processed.stock.steps, stock):
                if any(value is None for value in row):
                    raise ValueError("NO_NEURAL_CELL_IMPUTATION")
                numbers = tuple(float(value) for value in row if value is not None)
                cell_key = (symbol, step.session, step.slot)
                position = table.setdefault(cell_key, len(values))
                if position == len(values):
                    values.append(numbers)
                elif values[position] != numbers:
                    raise ValueError("CONFLICTING_CANONICAL_FEATURE_OBSERVATION")
                stock_indices.append(position)
            indices.append(tuple(stock_indices))
        scores = apply_proxy_floor(origin.label, preparation.tg0_floor, test_scenario=True).scores
        if scores is None or len(scores) != 5:
            raise ValueError("COMPLETE_MATURE_TG0_REQUIRED")
        rows.append(IndexedOrigin(*key, tuple(indices), scores))
    tensor = torch.tensor(values, dtype=torch.float32).reshape(-1, 16)
    version = "SYN:NEURAL_DATA:" + identity(
        [data.universe.universe_id, data_identity(data), preparation_identity(preparation),
         window, rows, tensor.tolist()]
    )
    return NeuralView(data.universe, version, tensor, tuple(rows),
                      tuple(sorted({r.session for r in rows})), preparation_identity(preparation),
                      window, identity(tensor.tolist()), tuple(excluded))
