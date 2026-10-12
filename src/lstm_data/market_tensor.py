"""P2.4 data-only MC0/MC1 information contract; no model, fit or portfolio engine."""

from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd

from .ft0_tensor import CandidateJoin
from .ft0_transforms import ORDER
from .labels import UNIVERSE
from .market_features import SOURCE_VERSION, Vector

MC0Row = tuple[float, ...]
MC0Values = tuple[tuple[MC0Row, ...], ...]
MARKET_ORDER = ("U1", "U2", "U3", "U4", "U5")


@dataclass(frozen=True)
class MarketAssembly:
    """The same market history is repeated numerically, never as replicated fit keys.

    Masks/lineage remain metadata. MC1 may later consume the same direct channels
    and endpoint; this package implements neither its gate nor its model.
    """

    mc0_values: MC0Values
    direct_market: tuple[Vector, ...]
    market_mask: tuple[tuple[bool, ...], ...]
    scheduled_ends: tuple[pd.Timestamp, ...]
    stock_lineage: tuple[tuple[tuple[str, ...], ...], ...]
    market_lineage: tuple[tuple[str, ...], ...]
    source_version: str
    floor_ref: str
    scaler_ref: str
    scientific_ready: bool = False
    model_wiring: str = "NOT_BUILT"

    @property
    def shape(self) -> tuple[int, int, int]:
        return 5, 48, 21


def assemble_market_inputs(join: CandidateJoin) -> MarketAssembly:
    """Fail closed on malformed, noncausal or source-only inputs; no future exits.

    The supplied upstream tensors are guarded interface assertions, not independent
    source certification. Even accepted synthetic data keep scientific_ready false.
    """
    stock, market = join.stock, join.market
    if (
        not join.matched_market_eligible
        or not stock.input_eligible
        or stock.source_only
        or stock.application_context != "ASOF"
        or market is None
        or market.values is None
        or market.application_context != "ASOF"
    ):
        raise ValueError("CAUSAL_COMPLETE_STOCK_MARKET_INPUTS_REQUIRED")
    ends = tuple(s.information_cutoff for s in stock.steps)
    if (
        stock.symbols != UNIVERSE
        or stock.channels != ORDER
        or len(ends) != 48
        or len(set(ends)) != 48
        or market.scheduled_ends != ends
        or market.source_version != SOURCE_VERSION
        or not market.floor_ref
        or not market.scaler_ref
    ):
        raise ValueError("CANONICAL_STOCK_MARKET_BINDING_REQUIRED")
    if (
        len(stock.values) != 5
        or len(stock.mask) != 5
        or len(stock.lineage) != 5
        or len(market.values) != 48
        or len(market.valid_mask) != 48
        or len(market.source_ids) != 48
        or len(market.step_reasons) != 48
        or len(market.source_ages_seconds) != 48
        or not market.valid_mask[-1]
        or sum(market.valid_mask) < 46
    ):
        raise ValueError("EXACT_STOCK_MARKET_SHAPES_AND_MASKS_REQUIRED")
    for valid, values, ids, age in zip(
        market.valid_mask, market.values, market.source_ids, market.source_ages_seconds
    ):
        if len(values) != 5 or not all(math.isfinite(x) for x in values):
            raise ValueError("FIVE_FINITE_MARKET_CHANNELS_REQUIRED")
        if valid and (not ids or age is None or not math.isfinite(age) or not 0 <= age <= 5400):
            raise ValueError("FRESH_MARKET_SOURCE_LINEAGE_REQUIRED")
        if not valid and values != (0.0, 0.0, 0.0, 0.0, 0.0):
            raise ValueError("ONLY_STANDARDIZED_MISSING_MARKET_NEUTRAL_ZERO_ALLOWED")
    output = []
    for rows, masks, lineage in zip(stock.values, stock.mask, stock.lineage):
        if len(rows) != 48 or len(masks) != 48 or len(lineage) != 48:
            raise ValueError("EXACT_48_STOCK_POSITIONS_REQUIRED")
        current = []
        for row, mask, ids, shared in zip(rows, masks, lineage, market.values):
            if len(row) != 16 or len(mask) != 16 or not all(mask) or len(ids) != 16 or not all(ids):
                raise ValueError("COMPLETE_16_STOCK_CHANNELS_REQUIRED")
            numbers = []
            for value in row:
                if value is None or not math.isfinite(value):
                    raise ValueError("NO_MISSING_OR_NONFINITE_STOCK_VALUES")
                numbers.append(value)
            current.append(tuple(numbers) + shared)
        output.append(tuple(current))
    return MarketAssembly(
        tuple(output),
        market.values,
        market.cell_mask,
        ends,
        stock.lineage,
        market.source_ids,
        market.source_version,
        market.floor_ref,
        market.scaler_ref,
    )
