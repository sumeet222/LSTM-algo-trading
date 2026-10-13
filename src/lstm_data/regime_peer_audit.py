"""Bounded fabricated P4.6/P4.7 evidence; no neural fitting, raw inputs or credentials."""

from __future__ import annotations

import argparse
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from .baseline_authority import replay_permission
from .baseline_fit import prepare
from .baseline_fixtures import LEGACY_KEYS, ridge_data
from .baseline_ridge import LAGS, fitting_origins, windows
from .calendar import schedule
from .clocks import execution_plan
from .config import write_json
from .ft0_transforms import identity
from .m2 import ScheduledCalendar, scheduled_window
from .market_features import MarketWindow
from .neural_audit import peak_memory
from .neural_market import MarketEvidence, MarketStamp
from .p3_domain import MODE, Permission, UniverseSpec
from .p3_events import json_value
from .peer_inputs import M1_INDEX, make_peer_view, peer_input, peer_lag_vectors
from .peer_ridge import matched_peer_ridge
from .regime_diagnostics import (
    DiagnosticWindow,
    Regime,
    classify,
    diagnostic_window,
    mc2_readiness,
    occupancy,
    training_threshold,
    variation,
)


def fabricated_case():
    """One100-session fabricated source; existing frozen floor-dependent basis preserved."""
    permission = replay_permission(Permission(MODE))
    universe = UniverseSpec("SYN:E5_TEST", ("AA", "BB", "CC", "DD", "EE"))
    data = ridge_data(universe)
    origins = []
    for origin in data.origins:
        raw = tuple(
            tuple(
                tuple(float(i + 1) if c == M1_INDEX else v for c, v in enumerate(step))
                for step in stock
            )
            for i, stock in enumerate(origin.inputs.stock.raw_values)
        )
        origins.append(
            replace(
                origin,
                inputs=replace(origin.inputs, stock=replace(origin.inputs.stock, raw_values=raw)),
            )
        )
    records = tuple(
        replace(r, value=float(LEGACY_KEYS.index(r.symbol) + 1)) if r.kind == "M1" else r
        for r in data.stock_records
    )
    data = replace(data, origins=tuple(origins), stock_records=records)
    history = MarketEvidence(
        "SYN:E5_MKT",
        data.market_vectors,
        tuple(
            MarketStamp(v.timestamp, v.timestamp, v.timestamp, v.evidence_ids)
            for v in data.market_vectors
        ),
    )
    inner, val, _ = windows("WF1", pd.Timestamp("2023-07-01T04:00Z"))
    inner = replace(inner, fitted_at=inner.stop)
    rows, _ = fitting_origins(data.origins, universe, inner)
    prep = prepare(data, inner, rows, market=True, permission=permission, allow_synthetic=True)
    return data, history, prep, val, permission


def fabricated_window(
    calendar: ScheduledCalendar, day: str, *, changed: int, missing: int = 0, u1_only: bool = False
) -> DiagnosticWindow:
    """Already-standardized arithmetic fixture with real calendar metadata, fake states."""
    steps = scheduled_window(calendar, day, 1)
    values = [(0.0, 0.0, 0.0, 0.0, 1.0)] * 48
    for i in range(changed):
        values[i] = (1.0, 0.0, 0.0, 0.0, 1.0) if u1_only else (0.0, 1.0, 0.0, 0.0, 1.0)
    mask = [True] * 48
    for i in range(45 - missing, 45):
        values[i] = (0.0, 0.0, 0.0, 0.0, 0.0)
        mask[i] = False
    ids = tuple(
        ("SYN:STATE:" + s.end.isoformat(),) if valid else () for s, valid in zip(steps, mask)
    )
    m = MarketWindow(
        tuple(values),
        tuple(mask),
        "SYNTHETIC_PREPARED",
        (),
        scheduled_ends=tuple(s.end for s in steps),
        source_ids=ids,
        scaler_ref="SYN:ORACLE_SCALER",
        floor_ref="SYN:ORACLE_FLOOR",
    )
    stamps = tuple(
        MarketStamp(s.end, s.end if valid else None, s.end if valid else None, source)
        for s, valid, source in zip(steps, mask, ids)
    )
    return DiagnosticWindow(day, 1, m, stamps, "SYN:ORACLE_HISTORY", "SYN:ORACLE_INPUT", "TRAINING")


def audit(out: Path, mode: str) -> dict:
    if mode != MODE or out.exists() or "reports/audit" in out.as_posix():
        raise ValueError("NEW_SYNTHETIC_REPORT_DIRECTORY_ONLY")
    permission = Permission(mode)
    permission.ensure()
    out.mkdir(parents=True)
    start = time.monotonic()
    data, history, prep, val, permission = fabricated_case()
    row = data.origins[-1].inputs
    processed, peers, trace = peer_input(row, prep, history, permission)
    assert prep.market_scaler is not None
    threshold = training_threshold(history, prep.market_scaler, permission)
    window = diagnostic_window(row, prep, history, permission, phase="TRAINING")
    state = classify(window, threshold)
    view = make_peer_view(
        replace(data, origins=data.origins[-2:]),
        val,
        prep,
        permission,
        history,
        allow_synthetic=True,
    )
    batch = view.batch((0,))
    vectors = peer_lag_vectors(row, prep, history, permission)
    control, peer, ridge = matched_peer_ridge(
        data, "WF1", history, permission, allow_synthetic=True
    )
    calendar = ScheduledCalendar("2020-07-01", "2021-01-29")
    days = tuple(
        str(d.date())
        for d in schedule("2020-08-03", "2021-01-29").index
        if execution_plan(calendar.clock(str(d.date())), 1).calendar_valid
    )[:100]
    synthetic = tuple(
        fabricated_window(calendar, day, changed=12 if i < 20 else 0) for i, day in enumerate(days)
    )
    changes = mc2_readiness(synthetic)
    slices = occupancy(
        tuple(
            Regime((d, 1), "BULL", "HIGH", "SYN:W", "SYN:T")
            for i, d in enumerate(days)
            if i not in (10, 21)
        ),
        tuple(str(d.date()) for d in schedule(days[0], days[-1]).index),
    )
    boundaries = [
        variation(fabricated_window(calendar, days[0], changed=n, missing=m))
        for n, m in ((11, 2), (12, 2), (12, 0))
    ]
    u1 = variation(fabricated_window(calendar, days[0], changed=30, u1_only=True))
    z = np.zeros((5, 48, 16))
    z[:, :, M1_INDEX] = np.arange(1, 6)[:, None]
    from .peer_inputs import peer_summaries

    arithmetic = peer_summaries(z)
    result = {
        "scope": MODE,
        "source": history.evidence_id,
        "preparation": view.market.preparation_id,
        "threshold": threshold,
        "state": state,
        "window_id": window.window_id,
        "48_step_stamps": window.stamps,
        "mask": window.market.valid_mask,
        "occupancy": slices,
        "MC2_boundaries": boundaries,
        "U1_only": u1,
        "MC2_population": {k: v for k, v in changes.items() if k != "windows"},
        "peer_hand_z": (1, 2, 3, 4, 5),
        "peer_hand_results": arithmetic[:, 0].tolist(),
        "canonical_scaled_peer_results": peers[:, 0].tolist(),
        "peer_trace": trace,
        "batch23": list(batch.inputs.shape),
        "lag_positions": [47 - lag for lag in LAGS],
        "ridge_prefix147": list(vectors[0][:147]),
        "ridge_peer14": list(vectors[0][147:]),
        "ridge": ridge,
        "control_selection": control.evidence,
        "peer_selection": peer.evidence,
        "selected_penalties": (control.selected_penalty, peer.selected_penalty),
        "solution_ids": (identity(control.solution), identity(peer.solution)),
        "training_neural_pairs": 0,
        "science_pairs_consumed": 0,
        "provider_attempts": 0,
        "scientific_status": "SCIENTIFIC_ACTIVATION_HOLD",
        "seconds": time.monotonic() - start,
        "peak_memory": peak_memory(),
    }
    write_json(out / "synthetic_evidence.json", json_value(result))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mode", choices=[MODE], required=True)
    args = parser.parse_args()
    result = audit(args.out, args.mode)
    print({"scope": result["scope"], "seconds": result["seconds"], "neural_pairs": 0})


if __name__ == "__main__":
    main()
