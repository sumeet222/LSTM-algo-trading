"""Offline P2 engineering evidence and versioned deferred-work handoff; no fits/trades."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from .clocks import execution_plan, session_clock
from .config import digest, fingerprint, write_json
from .ft0_tensor import StockTensor, join_market
from .ft0_transforms import ORDER
from .labels import UNIVERSE
from .m2 import ScheduledCalendar, scheduled_window
from .market_features import (
    DailyScaleSample,
    MarketClose,
    MarketFitWindow,
    MarketHistory,
    MarketObservation,
    fit_synthetic_floors,
    fit_synthetic_scaler,
    history_from_archive,
    vector,
    window_from_history,
)
from .market_source import hourly_archive
from .market_tensor import assemble_market_inputs
from .store import chunk_paths, read_verified

PACKAGE = "TA-P2-FINAL-CLOSE-001"
REMEDIATION = Path("reports/data_audit/ta_data_remed_ft0_001_2026-10-11_195135")
BASELINE = Path("reports/data_audit/ta_p2_close_ft0_2026-10-11")
SPY = Path("reports/data_audit/ta_mkt_spy_003_2026-10-11")
REGISTER_DOC = Path("docs/track_a/P2_DEFERRED_WORK_REGISTER_v1.md")
HANDOFF_CONFIG = Path("configs/track_a_p2_engineering_handoff_v1.json")


def reference(path: Path) -> dict:
    return {"path": path.as_posix(), "sha256": digest(path)}


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def retention_evidence() -> dict:
    """Reuse immutable evidenced audits, verifying identical origin keys and counts."""
    old_path = BASELINE / "retention_and_attrition.json"
    new_path = REMEDIATION / "alpaca_only_extended/retention.json"
    old, candidate = read(old_path), read(new_path)
    old_keys = [(r["session"], r["origin"]) for r in old["origins"]]
    new_keys = [(r["session"], r["origin"]) for r in candidate["origins"]]
    if old_keys != new_keys or len(set(old_keys)) != 1998:
        raise ValueError("FROZEN_PRECONFIRMATION_ORIGIN_UNIVERSE_CHANGED")
    gaps_path = REMEDIATION / "gap_cluster_reconciliation.json"
    gaps = read(gaps_path)
    if (
        len(gaps["clusters"]) != 15
        or sum(c["original_missing_count"] for c in gaps["clusters"]) != 168
    ):
        raise ValueError("ORIGINAL_GAP_IDENTITY_CHANGED")
    views = {}
    for name, result, expected in [
        ("ORIGINAL", old, 919),
        ("INACTIVE_PREHISTORY_CANDIDATE", candidate, 1183),
    ]:
        if result["populations"]["train"]["numerator"] != expected:
            raise ValueError("REPORTED_TRAIN_RETENTION_DIVERGED")
        groups = result["market_intersection"]["by_population"]
        for key, denominator in [("train", 1502), ("development", 496), ("WF1", 248), ("WF2", 248)]:
            if groups[key]["denominator"] != denominator:
                raise ValueError("FROZEN_POPULATION_DENOMINATOR_CHANGED")
        valid = [r for r in result["origins"] if r["mechanical_ft0"]]
        views[name] = {
            "by_population": groups,
            "by_origin": result["by_origin"],
            "first_stock_structural": valid[0],
            "last_stock_structural": valid[-1],
            "per_channel_overlapping_losses": result["feature_loss_counts"],
            "inner_63_session_tails": result["inner_63_session_tails"],
            "regimes": result["volatility_regimes"],
            "stock_guard": result["populations"],
            "exact_origin_keys_sha256": fingerprint(old_keys),
            "first_divergence_by_stock_nonexhaustive": dict(
                Counter(
                    r["first_bad"]["symbol"]
                    for r in result["origins"]
                    if r.get("first_bad") and "symbol" in r["first_bad"]
                )
            ),
            "per_stock_attribution_scope": "First divergence only; not full stock rejection unions",
        }
    clusters = [
        {
            k: c[k]
            for k in (
                "symbol",
                "session",
                "original_missing_count",
                "original_missing_keys",
                "original_missing_keys_still_absent",
                "missing_keys_now_returned",
                "disposition",
            )
        }
        for c in gaps["clusters"]
    ]
    return {
        "classification": "STRUCTURAL_ONLY; SCIENTIFIC_CAUSAL_BLOCKED",
        "evidence": [reference(old_path), reference(new_path), reference(gaps_path)],
        "views": views,
        "gaps": clusters,
        "missing_native_by_stock": {
            symbol: sum(c["original_missing_count"] for c in clusters if c["symbol"] == symbol)
            for symbol in UNIVERSE
        },
        "cause_union": {
            "startup_original": 264,
            "startup_recovered": 264,
            "later_direct48": 75,
            "later_propagated": 244,
            "later_union_remaining": 319,
            "channel_losses_overlap": True,
        },
        "train_minimum": 1352,
        "candidate_deficit": 169,
        "candidate_active": False,
        "causal_admitted": 0,
        "market_structural_first": "2020-07-01 origin1",
        "market_structural_last": "2024-06-28 origin2",
        "source_only_no_confirmation_computation": True,
    }


def synthetic_trace() -> dict:
    """Small analytic data fixture; no empirical floor/scaler or fitted model."""
    cal = ScheduledCalendar("2019-12-02", "2020-12-01")
    hours = tuple(
        MarketObservation(
            s.start,
            s.end,
            100.0,
            100.0 * math.exp(0.02),
            s.end,
            "SYNTHETIC",
            f"synthetic-hour:{i}",
            True,
        )
        for i, s in enumerate(cal.steps)
    )
    closes = {
        day: MarketClose(
            c.close, 100.0 * math.exp(0.01 * i), c.close, "SYNTHETIC", f"synthetic-day:{i}", True
        )
        for i, (day, c) in enumerate(cal._sessions.items())
        if c.close is not None
    }
    history = MarketHistory(cal, hours, closes, allow_synthetic=True)
    w = MarketFitWindow(
        pd.Timestamp("2020-07-01T04:00Z"),
        pd.Timestamp("2020-07-10T04:00Z"),
        pd.Timestamp("2020-07-10T04:00Z"),
        "INNER_TRAIN",
    )
    measures = tuple(history.measures(s) for s in cal.steps if w.contains(s.end))
    daily = tuple(
        DailyScaleSample(c.period_end, 0.01) for c in closes.values() if w.contains(c.period_end)
    )
    floors = fit_synthetic_floors(measures, daily, w, "SYNTHETIC_P2_CLOSURE", allow_synthetic=True)
    vectors = tuple(vector(r, floors, allow_synthetic=True) for r in measures)
    # Five identical stock appearances never change market timestamp weighting.
    scaler = fit_synthetic_scaler(vectors * 5, w, "SYNTHETIC_P2_CLOSURE", allow_synthetic=True)
    steps = scheduled_window(cal, "2020-08-03", 1)
    raw = vector(history.measures(steps[-1]), floors, allow_synthetic=True, context="ASOF")
    expected = (1.0, math.log(0.02), 0.0, math.sqrt(5), math.sqrt(20))
    if raw.values is None or any(abs(a - b) > 1e-10 for a, b in zip(raw.values, expected)):
        raise ValueError("FROZEN_D7_HAND_ARITHMETIC_CHANGED")
    values = tuple(tuple((1.0,) * 16 for _ in steps) for _ in UNIVERSE)
    mask = tuple(tuple((True,) * 16 for _ in steps) for _ in UNIVERSE)
    reasons = tuple(tuple(("SYNTHETIC_VALID",) * 16 for _ in steps) for _ in UNIVERSE)
    lineage = tuple(
        tuple(tuple(f"synthetic:{symbol}:{s.end}:{k}" for k in ORDER) for s in steps)
        for symbol in UNIVERSE
    )
    stock = StockTensor(
        UNIVERSE,
        steps,
        ORDER,
        values,
        values,
        mask,
        reasons,
        lineage,
        True,
        "synthetic",
        ("synthetic",) * 5,
        "synthetic",
        "ASOF",
        fingerprint("synthetic-source"),
        fingerprint("synthetic-actions"),
        False,
        True,
    )
    joined = join_market(stock, history, floors, scaler, origin=1)
    assembly = assemble_market_inputs(joined)
    plans = []
    for day in ("2020-08-03", "2020-11-16", "2020-11-27"):
        clock = session_clock(day)
        plans.append(
            {
                "session": day,
                "complete_hours": len(clock.hours),
                "stub": clock.terminal_stub is not None,
                "origins": [
                    {
                        "origin": o,
                        "cutoff": str(p.cutoff),
                        "entry": str(p.entry),
                        "exit": str(p.exit),
                        "reason": p.reason,
                        "hourly_proxy_exit": str(p.cutoff + pd.Timedelta(hours=4))
                        if p.cutoff is not None
                        else None,
                    }
                    for o in (1, 2)
                    for p in [execution_plan(clock, o)]
                ],
            }
        )
    return {
        "classification": "SYNTHETIC_TEST",
        "U1_U5": raw.values,
        "independent_expected": expected,
        "floor_H": floors.hourly,
        "floor_D": floors.daily,
        "fit_window": {"start": str(w.start), "stop": str(w.stop), "fitted_at": str(w.fitted_at)},
        "unique_hour_floor_keys": len(floors.timestamps),
        "unique_daily_floor_keys": len(floors.daily_timestamps),
        "unique_scaler_timestamps": len(scaler.timestamps),
        "replicated_input_rows": len(vectors) * 5,
        "scaler_methods": scaler.methods,
        "own_cutoff_context": "ASOF",
        "stock_shape": stock.shape,
        "market_shape": [48, 5],
        "MC0_shape": assembly.shape,
        "model_wiring": assembly.model_wiring,
        "research_ready": False,
        "first_step": str(steps[0].end),
        "last_step": str(steps[-1].end),
        "48_endpoint_identity": assembly.scheduled_ends == tuple(s.end for s in steps),
        "first_market_lineage": assembly.market_lineage[0],
        "last_market_lineage": assembly.market_lineage[-1],
        "one_stock_cell_lineage": assembly.stock_lineage[0][-1][0],
        "edge_tests": "tests/test_market_features.py and tests/test_p2_market_closure.py",
        "calendar_traces": plans,
        "actual_data_fits": 0,
    }


def real_negative_trace() -> dict:
    """Two immutable partitions only; first July source integrity and unknown clock."""
    inventory = read(SPY / "archive_manifest.json")
    frames, refs = [], []
    for partition in inventory["partitions"][:2]:
        params = partition["params"]
        data, manifest = chunk_paths(Path("data/raw/alpaca/track_a_spy_v1"), params)
        frame = read_verified(data, manifest, params)
        frames.append(frame[frame.timestamp < pd.Timestamp("2020-07-02T04:00Z")])
        refs.extend([reference(data), reference(manifest)])
    frame = pd.concat(frames, ignore_index=True)
    hourly, _ = hourly_archive(frame, "2020-03-19", "2020-07-01")
    history = history_from_archive(ScheduledCalendar("2020-03-19", "2020-07-01"), hourly)
    windows = []
    for origin in (1, 2):
        result = window_from_history(history, "2020-07-01", origin, context="ASOF")
        step = scheduled_window(history.calendar, "2020-07-01", origin)[-1]
        measures = history.measures(step)
        if (
            result.values is not None
            or result.reason != "PUBLICATION_UNKNOWN"
            or measures.basis != "UNKNOWN"
        ):
            raise ValueError("REAL_SPY_UNKNOWN_CLOCK_MUST_BLOCK")
        windows.append(
            {
                "origin": origin,
                "cutoff": str(step.end),
                "reason": result.reason,
                "valid_cells": sum(sum(mask) for mask in result.cell_mask),
                "basis": measures.basis,
                "source_ids": measures.evidence_ids[-3:],
                "floor": None,
                "scaler": None,
                "values": None,
            }
        )
    return {
        "classification": "SOURCE_INTEGRITY_ONLY; SCIENTIFIC_CAUSAL_BLOCKED",
        "read_partitions": 2,
        "source_refs": refs,
        "windows": windows,
        "no_synthetic_availability_or_actual_fitting": True,
    }


def load_deferred_work(config: Path) -> tuple[dict, ...]:
    """Mandatory portable handoff read, preserving the frozen protocol pointer.

    This validates evidence/version bindings; it grants no P3 activity or science
    permission. Future empirical admission requires separate gate approval.
    """
    root = config.resolve().parent.parent
    binding = read(config)
    if binding.get("version") != 1 or binding.get("empirical_work_authorized") is not False:
        raise ValueError("P2_HANDOFF_AUTHORITY_REQUIRED")
    for key in ("register", "readable_register"):
        ref = binding[key]
        path = (root / ref["path"]).resolve()
        if not path.is_relative_to(root) or digest(path) != ref["sha256"]:
            raise ValueError("P2_REGISTER_VERSION_OR_HASH_CHANGED")
    register = read(root / binding["register"]["path"])
    entries = register["entries"]
    required = {f"P2-DEF-{i:03d}" for i in range(1, 15)}
    fields = {
        "id",
        "status",
        "scientific_status",
        "responsible_phase",
        "category",
        "predecessor_evidence",
        "code_boundary",
        "affected_branches",
        "next_minimal_action",
        "closure_test",
        "human_authority_required",
        "blocks_engineering",
        "blocks_scientific_activation",
        "last_evidence_version",
    }
    ids = [e["id"] for e in entries]
    categories = {
        "DATA",
        "SOURCE_CLOCK",
        "ACTION",
        "FIT",
        "RETENTION",
        "APPROVAL",
        "EXECUTION",
        "GIT_INTEGRATION",
        "OTHER",
    }
    if (
        register.get("version") != 1
        or len(ids) != len(set(ids))
        or not required <= set(ids)
        or any(not fields <= set(e) for e in entries)
        or any(
            e["category"] not in categories
            or not isinstance(e["blocks_engineering"], bool)
            or not isinstance(e["blocks_scientific_activation"], bool)
            or not e["code_boundary"]
            or not e["closure_test"]
            for e in entries
        )
    ):
        raise ValueError("COMPLETE_VERSIONED_P2_DEFERRED_REGISTER_REQUIRED")
    return tuple(entries)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    # No credential loading and no transport calls are allowed, including indirectly.
    with patch("requests.sessions.Session.request", side_effect=RuntimeError("P2_OFFLINE_ONLY")):
        write_json(args.report / "stock_market_retention.json", retention_evidence())
        write_json(
            args.report / "p2_4_market_trace.json",
            {"synthetic": synthetic_trace(), "real_negative": real_negative_trace()},
        )
    print({"package": PACKAGE, "network": False, "real_fits": 0, "report": str(args.report)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
