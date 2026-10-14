"""Predeclared fabricated forward, reverse and null cases; no source-file access."""

from __future__ import annotations

import math
from dataclasses import replace
from typing import Literal

import numpy as np

from .baseline_authority import replay_permission
from .baseline_fixtures import LEGACY_KEYS, ridge_data
from .baseline_ridge import RidgeOrigin
from .directed_ridge import DirectedArchive, RawM1
from .e5_audit import fake_formation
from .hourly_proxy import proxy_label_sample
from .labels import ActionScope, ForecastEvidence
from .m2 import ScheduledCalendar
from .neural_market import MarketEvidence, MarketStamp
from .p3_domain import MODE, Permission, UniverseSpec
from .peer_inputs import M1_INDEX

Case = Literal["FORWARD", "REVERSE", "NULL"]


def fixture(case: Case, universe: UniverseSpec | None = None):
    """Inputs generated first with RNG8050; labels are separate matured TG0 references.

    FORWARD plants prior-full-hour H M1 only in L's future log return. REVERSE
    plants prior L only in H; NULL has all zero returns. Median/MAD remain zero
    and the existing minimum TG0 floor gives a known bounded signal. Nothing
    derived from these future prices enters the input archive or preprocessing.
    """
    if case not in {"FORWARD", "REVERSE", "NULL"}:
        raise ValueError("PREDECLARED_SYNTHETIC_CASE_REQUIRED")
    permission = replay_permission(Permission(MODE))
    u = universe or UniverseSpec("SYN:D8_RIDGE", ("NOVA", "ORBIT", "PULSE", "QUARK", "RUNE"))
    data = ridge_data(u, zero_labels=True)
    calendar = ScheduledCalendar("2020-07-01", "2023-06-30")
    pair = fake_formation(u, permission)
    rng = np.random.default_rng(8050)
    original = data.origins[0].inputs.stock
    rows = tuple(
        RawM1(
            s,
            tuple(float(v) for v in rng.uniform(-0.8, 0.8, 5)),
            tuple(f"SYN:M1:{symbol}:{s.session}:{s.slot}" for symbol in u.symbols),
            (s.end,) * 5,
        )
        for s in calendar.steps
    )
    archive = DirectedArchive(
        u,
        "SYN:D8_RAW_M1:8050",
        rows,
        original.source_binding,
        original.action_binding,
        "SYN:D8_SAME_RAW_FEATURE_UNITS",
    )
    lookup = {r.step.end: r for r in rows}
    position = {s.end: i for i, s in enumerate(calendar.steps)}
    origins = []
    for origin in data.origins:
        row = origin.inputs
        raw = tuple(
            tuple(
                tuple(
                    lookup[step.end].values[i] if c == M1_INDEX else value
                    for c, value in enumerate(old)
                )
                for step, old in zip(row.stock.steps, stock)
            )
            for i, stock in enumerate(row.stock.raw_values)
        )
        lineage = tuple(
            tuple(
                tuple(
                    lookup[step.end].source_ids[i] if c == M1_INDEX else value
                    for c, value in enumerate(old)
                )
                for step, old in zip(row.stock.steps, stock)
            )
            for i, stock in enumerate(row.stock.lineage)
        )
        inputs = replace(
            row,
            input_id=f"SYN:{case}:" + row.input_id,
            stock=replace(row.stock, raw_values=raw, lineage=lineage),
        )
        assert row.plan.cutoff is not None and row.plan.exit is not None
        previous = rows[position[row.plan.cutoff] - 1].values
        h, low = u.symbols.index(pair.highest), u.symbols.index(pair.lowest)
        returns = [0.0] * 5
        if case == "FORWARD":
            returns[low] = 1e-4 * previous[h]
        if case == "REVERSE":
            returns[h] = 1e-4 * previous[low]
        entries, exits = [], []
        for i in range(5):
            entry = origin.label.references[i * 2].row
            exit_row = origin.label.references[i * 2 + 1].row
            assert entry is not None and exit_row is not None
            entries.append(
                replace(
                    entry,
                    row_id=f"SYN:D8:{case}:" + entry.row_id,
                    source_version=f"SYN:D8_LABEL_SOURCE:{case}",
                )
            )
            exits.append(
                replace(
                    exit_row,
                    raw_close=100.0 * math.exp(returns[i]),
                    row_id=f"SYN:D8:{case}:" + exit_row.row_id,
                    source_version=f"SYN:D8_LABEL_SOURCE:{case}",
                )
            )
        label = proxy_label_sample(
            row.plan,
            ForecastEvidence(True, row.plan.cutoff, LEGACY_KEYS, "SYNTHETIC", inputs.input_id),
            tuple(entries),
            tuple(exits),
            observed_at=row.plan.exit,
            actions=ActionScope(
                row.plan.cutoff, row.plan.exit, LEGACY_KEYS, "SYNTHETIC", "SYN:D8_ACTION_COVERAGE"
            ),
            test_scenario=True,
        )
        origins.append(RidgeOrigin(inputs, label))
    records = tuple(
        replace(r, value=lookup[r.available_at].values[LEGACY_KEYS.index(r.symbol)])
        if r.kind == "M1"
        else r
        for r in data.stock_records
    )
    data = replace(data, origins=tuple(origins), stock_records=records)
    history = MarketEvidence(
        "SYN:D8_MARKET",
        data.market_vectors,
        tuple(
            MarketStamp(v.timestamp, v.timestamp, v.timestamp, v.evidence_ids)
            for v in data.market_vectors
        ),
    )
    return data, history, archive, pair, permission
