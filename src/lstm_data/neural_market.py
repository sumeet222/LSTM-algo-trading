"""Explicit synthetic D7 publication evidence and a shared indexed market view."""

from __future__ import annotations

from dataclasses import dataclass, replace

import pandas as pd
import torch
from torch import Tensor

from .baseline_fit import FitData, Preparation
from .baseline_inputs import BaselineInput
from .clocks import utc
from .ft0_transforms import identity
from .labels import FitWindow
from .market_features import MarketVector
from .neural_data import NeuralView, data_identity, make_view, preparation_identity
from .neural_engine import SessionBatch
from .p3_domain import Permission, synthetic_id


@dataclass(frozen=True)
class MarketStamp:
    """Caller evidence of a fabricated vector's own-step publication, not period end inference."""

    timestamp: pd.Timestamp
    period_end: pd.Timestamp | None
    available_at: pd.Timestamp | None
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class MarketEvidence:
    """Single immutable synthetic D7 history with a separate clock trace."""

    version: str
    vectors: tuple[MarketVector, ...]
    stamps: tuple[MarketStamp, ...]

    def validate(self) -> None:
        synthetic_id(self.version)
        times = tuple(utc(v.timestamp) for v in self.vectors)
        if (
            not times
            or len(set(times)) != len(times)
            or len({utc(s.timestamp) for s in self.stamps}) != len(self.stamps)
            or set(times) != {utc(s.timestamp) for s in self.stamps}
        ):
            raise ValueError("EXACT_UNIQUE_D7_CLOCK_TRACE_REQUIRED")
        lookup = {utc(s.timestamp): s for s in self.stamps}
        for v in self.vectors:
            if v.basis != "SYNTHETIC":
                raise ValueError("OBSERVED_D7_NOT_AUTHORIZED")
            stamp = lookup[utc(v.timestamp)]
            if stamp.evidence_ids != v.evidence_ids:
                raise ValueError("CONFLICTING_MARKET_PUBLICATION_PROVENANCE")
            valid = v.values is not None and v.reason == "VECTOR_VALID"
            if valid or stamp.period_end is not None or stamp.available_at is not None:
                if stamp.available_at is None or stamp.period_end is None:
                    raise ValueError("D7_PUBLICATION_UNKNOWN")
                end, available, at = (
                    utc(stamp.period_end),
                    utc(stamp.available_at),
                    utc(v.timestamp),
                )
                if not end <= available <= at or not 0 <= (at - end).total_seconds() <= 5400:
                    raise ValueError("D7_FUTURE_LATE_OR_STALE_PUBLICATION")
                if not v.evidence_ids:
                    raise ValueError("D7_SOURCE_EVIDENCE_REQUIRED")
            elif v.reason not in {"MISSING_SPY_SOURCE", "MARKET_ROLLING_OR_CHAIN_INCOMPLETE"}:
                raise ValueError("UNKNOWN_D7_STATE_IS_NOT_MISSING_SOURCE")
            for source_id in v.evidence_ids:
                synthetic_id(source_id)

    @property
    def evidence_id(self) -> str:
        self.validate()
        return identity([self.version, self.vectors, self.stamps])

    def extend(self, later: MarketEvidence) -> MarketEvidence:
        """Forecast history may extend a bound source, never replace its existing records."""
        self.validate()
        later.validate()
        if later.version != self.version:
            raise ValueError("MARKET_ARCHIVE_VERSION_CHANGED")
        vectors = {v.timestamp: v for v in self.vectors}
        stamps = {s.timestamp: s for s in self.stamps}
        for v in later.vectors:
            if v.timestamp in vectors and vectors[v.timestamp] != v:
                raise ValueError("D7_HISTORY_REBUILD_REQUIRED")
            vectors[v.timestamp] = v
        for s in later.stamps:
            if s.timestamp in stamps and stamps[s.timestamp] != s:
                raise ValueError("D7_CLOCK_REBUILD_REQUIRED")
            stamps[s.timestamp] = s
        return MarketEvidence(
            self.version,
            tuple(vectors[t] for t in sorted(vectors)),
            tuple(stamps[t] for t in sorted(stamps)),
        )


def market_preparation_identity(prep: Preparation) -> str:
    if prep.market_scaler is None or prep.market_floors is None:
        raise ValueError("D7_FITTED_PREPROCESS_REQUIRED")
    stock = replace(prep, market_scaler=None, market_floors=None)
    return identity(
        [preparation_identity(stock), identity(prep.market_scaler), identity(prep.market_floors)]
    )


def market_data_identity(data: FitData, history: MarketEvidence) -> str:
    history.validate()
    if data.market_vectors != history.vectors:
        raise ValueError("EXACT_FIT_D7_HISTORY_BINDING_REQUIRED")
    return identity(
        [data_identity(data), history.evidence_id, data.market_measures, data.daily_scales]
    )


def market_input(
    row: BaselineInput,
    prep: Preparation,
    history: MarketEvidence,
    permission: Permission,
    context: str = "ASOF",
) -> tuple[BaselineInput, str]:
    """No labels/exits. Reuse P2 normalization and P3 FT0/D7 checks; add own-step clocks."""
    history.validate()
    if prep.market_scaler is None or prep.market_floors is None:
        raise ValueError("D7_PREPROCESS_REQUIRED")
    if history.vectors != prep.market_vectors:
        raise ValueError("EXACT_PREPARATION_MARKET_HISTORY_REQUIRED")
    processed = prep.apply(row, context)
    processed.validate(permission, allow_synthetic=True, context=context)
    if processed.market is not None:
        stamp_lookup = {s.timestamp: s for s in history.stamps}
        ages = []
        for step in processed.stock.steps:
            stamp = stamp_lookup.get(step.end)
            end = stamp.period_end if stamp is not None else None
            ages.append((step.end - utc(end)).total_seconds() if end is not None else None)
        processed = replace(
            processed, market=replace(processed.market, source_ages_seconds=tuple(ages))
        )
    processed.validate_market(permission, allow_synthetic=True)
    m = processed.market
    assert m is not None and m.values is not None
    floors, scaler = prep.market_floors, prep.market_scaler
    if (
        floors.basis != "SYNTHETIC"
        or floors.window != scaler.window
        or floors.source_version != scaler.source_version
        or floors.action_version != scaler.action_version
        or m.floor_ref != identity(floors)
    ):
        raise ValueError("D7_FLOOR_SCALER_CONTEXT_REQUIRED")
    vectors = {v.timestamp: v for v in history.vectors}
    stamps = {s.timestamp: s for s in history.stamps}
    trace = []
    novel: set[int] = set()
    for step, values, valid in zip(processed.stock.steps, m.values, m.valid_mask):
        raw = vectors.get(step.end)
        if context == "ASOF" and utc(floors.window.fitted_at) > step.end:
            raise ValueError("D7_FLOOR_NOT_AVAILABLE_AT_STEP")
        if context == "HISTORICAL_TRAINING" and (
            step.end < floors.window.fitted_at and not floors.window.contains(step.end)
        ):
            raise ValueError("D7_FLOOR_OUTSIDE_HISTORICAL_FIT")
        stamp = stamps.get(step.end)
        if valid:
            if raw is None or raw.values is None or stamp is None:
                raise ValueError("D7_OWN_STEP_CLOCK_REQUIRED")
            transformed, flags = scaler.transform(raw.values)
            novel.update(flags)
            if values != transformed:
                raise ValueError("CANONICAL_D7_TRANSFORM_REQUIRED")
        trace.append((step, valid, raw, stamp))
    processed = replace(processed, market=replace(m, novel_constant_channels=tuple(sorted(novel))))
    return processed, identity(
        [
            processed.universe.universe_id,
            processed.stock.source_binding,
            processed.stock.action_binding,
            processed.input_id,
            processed.stock.channels,
            processed.stock.lineage,
            processed.stock.steps,
            processed.stock.mask,
            processed.available_at,
            processed.stock.raw_values,
            history.version,
            trace,
            market_preparation_identity(prep),
            context,
            row.plan.cutoff,
        ]
    )


@dataclass(frozen=True)
class MarketIndex:
    session: str
    origin: int
    indices: tuple[int, ...]
    mask: tuple[bool, ...]
    trace: str


@dataclass(frozen=True)
class MarketNeuralView:
    """One stock table plus one unique market-time table; broadcast only in current batch."""

    stock: NeuralView
    market_values: Tensor
    market_rows: tuple[MarketIndex, ...]
    preparation_id: str
    version: str
    market_hash: str

    def __post_init__(self) -> None:
        if (
            not self.version.startswith("SYN:NEURAL_MARKET_DATA:")
            or self.market_values.ndim != 2
            or self.market_values.shape[1] != 5
            or self.market_values.dtype != torch.float32
            or self.market_values.device.type != "cpu"
            or not bool(torch.isfinite(self.market_values).all())
            or {(r.session, r.origin) for r in self.market_rows}
            != {(r.session, r.origin) for r in self.stock.rows}
            or len(self.market_rows) != len(self.stock.rows)
            or any(
                len(r.indices) != 48
                or len(r.mask) != 48
                or not r.mask[-1]
                or sum(r.mask) < 46
                or any(type(b) is not bool for b in r.mask)
                or not r.trace
                or any(i < 0 or i >= len(self.market_values) for i in r.indices)
                for r in self.market_rows
            )
        ):
            raise ValueError("EXACT_SHARED_CAUSAL_MARKET_VIEW_REQUIRED")
        for row in self.market_rows:
            for i, valid in zip(row.indices, row.mask):
                if not valid and not torch.equal(self.market_values[i], torch.zeros(5)):
                    raise ValueError("D7_INVALID_VECTOR_MUST_BE_NEUTRAL_ZERO")

    @property
    def sessions(self) -> tuple[str, ...]:
        return self.stock.sessions

    @property
    def rows(self):
        return self.stock.rows

    @property
    def values(self) -> Tensor:
        return self.stock.values

    @property
    def excluded(self):
        return self.stock.excluded

    def batch(self, positions: tuple[int, ...]) -> SessionBatch:
        if identity([self.market_values.tolist(), self.market_rows]) != self.market_hash:
            raise ValueError("CANONICAL_MARKET_VIEW_MUTATED")
        batch = self.stock.batch(positions)
        m = torch.zeros(len(positions), 2, 48, 5)
        for i, day in enumerate(batch.ids):
            for row in self.market_rows:
                if row.session == day:
                    m[i, row.origin - 1] = self.market_values[torch.tensor(row.indices)]
        result = replace(
            batch, inputs=torch.cat((batch.inputs, m[:, :, None].expand(-1, -1, 5, -1, -1)), dim=-1)
        )
        result.validate()
        return result


def make_market_view(
    data: FitData,
    window: FitWindow,
    prep: Preparation,
    permission: Permission,
    history: MarketEvidence,
    *,
    allow_synthetic: bool = False,
) -> MarketNeuralView:
    """Same mature stock origin population for MC0 and MC1; invalid D7 fails closed."""
    market_data_identity(data, history)
    plain = replace(prep, market_scaler=None, market_floors=None)
    stock = make_view(data, window, plain, permission, allow_synthetic=allow_synthetic)
    origins = {(r.inputs.plan.session, r.inputs.plan.origin): r for r in data.origins}
    table: dict[pd.Timestamp, int] = {}
    values = []
    rows = []
    for r in stock.rows:
        context = "ASOF" if window.phase == "INNER_VALIDATION" else "HISTORICAL_TRAINING"
        processed, trace = market_input(
            origins[(r.session, r.origin)].inputs, prep, history, permission, context
        )
        m = processed.market
        assert m is not None and m.values is not None
        indices = []
        for end, value in zip(m.scheduled_ends, m.values):
            pos = table.setdefault(end, len(values))
            if pos == len(values):
                values.append(value)
            elif values[pos] != value:
                raise ValueError("CONFLICTING_CANONICAL_D7_VALUE")
            indices.append(pos)
        rows.append(MarketIndex(r.session, r.origin, tuple(indices), m.valid_mask, trace))
    tensor = torch.tensor(values, dtype=torch.float32).reshape(-1, 5)
    content = identity([tensor.tolist(), tuple(rows)])
    preparation = market_preparation_identity(prep)
    version = "SYN:NEURAL_MARKET_DATA:" + identity(
        [stock.version, market_data_identity(data, history), preparation, content]
    )
    return MarketNeuralView(stock, tensor, tuple(rows), preparation, version, content)
