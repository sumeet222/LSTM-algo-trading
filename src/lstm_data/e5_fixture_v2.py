"""Prospectively fixed, causal E5 sensitivity law; no external data access.

Fabricated FT0 values test adapters, not OHLC indicator construction. B2 is a
bounded observed sensitivity covariate, never a ticker identity or target value.
"""

from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import pandas as pd

from .baseline_authority import replay_permission
from .baseline_fit import FitData, Preparation, prepare
from .baseline_fixtures import LEGACY_KEYS, feature_input, ridge_data
from .baseline_inputs import BaselineInput
from .baseline_ridge import RidgeOrigin, fitting_origins, windows
from .clocks import utc
from .config import fingerprint
from .ft0_transforms import ORDER
from .hourly_proxy import proxy_label_sample
from .labels import ActionScope, ForecastEvidence
from .neural_market import MarketEvidence, MarketStamp
from .p3_domain import MODE, Permission, UniverseSpec

FIXTURE = "SYN:E5_HEALTH_FIXTURE:v2:8051"
B2 = ORDER.index("B2")


def step_values(at: pd.Timestamp) -> np.ndarray:
    """Independent timestamp-keyed Gaussian movements and one random recipient.

    No label, fit, universe name/order, seed42 model RNG or future time is read.
    Ordinal positions are permuted in the order test, including the covariate.
    """
    at = utc(at)
    rng = np.random.default_rng([8051, int(at.value // 60_000_000_000)])
    values = np.zeros((5, 16))
    values[:, 0] = rng.normal(size=5)
    values[int(rng.integers(5)), B2] = 1.0
    return values


def planted_returns(values: np.ndarray, at: pd.Timestamp, *, null: bool = False) -> np.ndarray:
    """Separate fabricated future law, median/MAD zero by four zero recipients."""
    if values.shape != (5, 16) or not np.isfinite(values).all():
        raise ValueError("FIVE_FINITE_FABRICATED_STEP_VALUES_REQUIRED")
    z = values[:, 0]
    mean = (z.sum() - z) / 4
    if null:
        # Independent target noise with the same conditional variance. Source is
        # a future LABEL stream, never inserted into any current feature record.
        rng = np.random.default_rng([8052, int(at.value // 60_000_000_000)])
        mean = rng.normal(0, 0.5, 5)
    return 1e-4 * values[:, B2] * mean


def input_values(row: BaselineInput, source: str, version: str) -> BaselineInput:
    raw = tuple(
        tuple(tuple(float(v) for v in step_values(s.end)[i]) for s in row.stock.steps)
        for i in range(5)
    )
    lineage = tuple(
        tuple(
            tuple(f"{version}:FEATURE:{name}:{s.end.isoformat()}:{f}" for f in ORDER)
            for s in row.stock.steps
        )
        for name in row.universe.symbols
    )
    return replace(
        row,
        input_id=version + ":" + row.input_id,
        stock=replace(row.stock, raw_values=raw, lineage=lineage, source_binding=source),
    )


def fixture(
    *, null: bool = False, version: str = FIXTURE
) -> tuple[FitData, MarketEvidence, Permission]:
    """Existing 100 calendar sessions, actual P2 fit/label contracts and 48 steps."""
    if not version.startswith("SYN:"):
        raise ValueError("SYNTHETIC_VERSION_REQUIRED")
    u = UniverseSpec("SYN:E5_V2", ("NOVA", "ORBIT", "PULSE", "QUARK", "RUNE"))
    data = ridge_data(u, zero_labels=True)
    source = fingerprint([version, "FABRICATED_FEATURE_SOURCE"])
    origins = []
    for old in data.origins:
        row = input_values(old.inputs, source, version)
        assert row.plan.cutoff is not None and row.plan.exit is not None
        returns = planted_returns(step_values(row.plan.cutoff), row.plan.cutoff, null=null)
        entries, exits = [], []
        for i in range(5):
            entry, exit_row = old.label.references[i * 2].row, old.label.references[i * 2 + 1].row
            assert entry is not None and exit_row is not None
            tag = version + (":NULL" if null else ":PLANTED")
            entries.append(replace(entry, row_id=tag + ":" + entry.row_id, source_version=tag))
            exits.append(
                replace(
                    exit_row,
                    raw_close=100 * math.exp(float(returns[i])),
                    row_id=tag + ":" + exit_row.row_id,
                    source_version=tag,
                )
            )
        label = proxy_label_sample(
            row.plan,
            ForecastEvidence(True, row.plan.cutoff, LEGACY_KEYS, "SYNTHETIC", row.input_id),
            tuple(entries),
            tuple(exits),
            observed_at=row.plan.exit,
            actions=ActionScope(
                row.plan.cutoff,
                row.plan.exit,
                LEGACY_KEYS,
                "SYNTHETIC",
                version + ":LABEL_ACTION_SCOPE",
            ),
            test_scenario=True,
        )
        origins.append(RidgeOrigin(row, label))
    records = tuple(
        replace(
            r,
            value=float(step_values(r.timestamp)[LEGACY_KEYS.index(r.symbol), 0])
            if r.kind == "M1"
            else r.value,
            source_binding=source,
            source_id=version + ":" + r.source_id,
        )
        for r in data.stock_records
    )
    floors = tuple(
        replace(r, source_binding=source, source_id=version + ":" + r.source_id)
        for r in data.floor_records
    )
    data = replace(data, origins=tuple(origins), stock_records=records, floor_records=floors)
    history = MarketEvidence(
        "SYN:E5_V2_MARKET",
        data.market_vectors,
        tuple(
            MarketStamp(v.timestamp, v.timestamp, v.timestamp, v.evidence_ids)
            for v in data.market_vectors
        ),
    )
    return data, history, replay_permission(Permission(MODE))


def training_preparation(data: FitData, permission: Permission) -> Preparation:
    inner, _, _ = windows("WF1", pd.Timestamp("2023-07-01T04:00Z"))
    inner = replace(inner, fitted_at=inner.stop)
    rows, _ = fitting_origins(data.origins, data.universe, inner)
    return prepare(data, inner, rows, market=True, permission=permission, allow_synthetic=True)


def forecast_input(data: FitData, version: str = FIXTURE) -> BaselineInput:
    row = feature_input(data.universe, day="2023-07-20")
    return input_values(row, data.origins[0].inputs.stock.source_binding, version)


def later_history(row: BaselineInput, history: MarketEvidence) -> MarketEvidence:
    from .market_features import MarketVector

    vectors = tuple(
        MarketVector(
            s.end,
            (0.0, 0.0, 0.0, 0.0, 0.0),
            "VECTOR_VALID",
            ("SYN:E5_V2_MARKET:" + s.end.isoformat(),),
        )
        for s in row.stock.steps
    )
    return MarketEvidence(
        history.version,
        vectors,
        tuple(MarketStamp(v.timestamp, v.timestamp, v.timestamp, v.evidence_ids) for v in vectors),
    )
