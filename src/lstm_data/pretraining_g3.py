"""Build/audit a conditional candidate dataset. No model fitting or ledger reservation."""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import pandas as pd

from .config import atomic_new, write_json
from .ft0_transforms import ORDER
from .labels import fitting_window
from .pretraining_oracles import publish_oracles
from .pretraining_policy import CANDIDATE, load_authority
from .pretraining_source import load_history
from .pretraining_store import code_identity, save_preparation, save_tables, serial
from .pretraining_tables import BaseTables, build_tables
from .pretraining_transforms import CandidateView, fit_preparation, raw_features

Stage = Literal["WF1", "WF2", "PRECONFIRMATION"]


def summarize(rows: list[dict], nominal: int) -> dict:
    accepted = [r for r in rows if r["candidate_supervised_admissible"]]
    reasons = Counter(reason for row in rows for reason in row["exclusion_reasons"])
    return {"nominal": nominal, "measured": len(rows), "eligible": len(accepted),
            "retention": len(accepted) / nominal if nominal else None,
            "eligible_sessions": len({r["session"] for r in accepted}),
            "per_origin": {str(o): {"nominal": sum(r["origin"] == o for r in rows),
                                      "eligible": sum(r["origin"] == o for r in accepted)}
                           for o in (1, 2)},
            "exclusion_reasons": dict(sorted(reasons.items())),
            "designation": "MEASURED_ASSUMPTION_CONDITIONAL_NOT_OBSERVED_CAUSALITY"}


def admission_row(base: BaseTables, view: CandidateView, day: str, origin: int,
                  boundary: pd.Timestamp) -> dict:
    valid, reasons = view.input_status(day, origin)
    panel = base.panels[day, origin]
    matured = bool(panel.label_valid and panel.maturity is not None and panel.maturity < boundary)
    failures = list(reasons)
    if not panel.label_valid:
        failures.append("PROXY_LABEL_INVALID")
    if not matured:
        failures.append("LABEL_NOT_MATURE_BEFORE_BOUNDARY")
    return {"session": day, "origin": origin, "cutoff": panel.cutoff.isoformat(),
            "input_admissible_under_approved_assumptions": valid,
            "forecast_issuable": False, "forecast_reason": "NO_TRAINED_MODEL_OR_ISSUANCE_AUTHORITY",
            "entry_reference_eligible": valid and all(panel.entry_valid),
            "portfolio_entry_eligible": None, "label_valid": panel.label_valid,
            "label_matured_before_boundary": matured,
            "label_maturity": panel.maturity.isoformat() if panel.maturity else None,
            "candidate_supervised_admissible": valid and matured,
            "exclusion_reasons": failures,
            "observed_publication_certified": False,
            "preparation_id": view.preparation.preparation_id}


def run(root: Path, binding_path: Path, report: Path) -> dict:
    """Publish one new store + six prefix recipes. Refuse stale/overwritten artifacts."""
    started = time.perf_counter()
    starting_code = code_identity(root)
    binding = json.loads(binding_path.read_text())
    authority = load_authority(root, binding["policy_ref"], binding["approval_ref"])
    if not report.resolve().is_relative_to(root.resolve()) or report.is_absolute():
        raise ValueError("PROJECT_RELATIVE_NEW_REPORT_REQUIRED")
    report.mkdir(parents=True, exist_ok=True)
    if (report / "canonical_dataset_manifest.json").exists():
        raise ValueError("EXISTING_DATASET_IMMUTABLE_USE_NEW_NAMESPACE")
    history, source_audit = load_history(authority)
    source_seconds = time.perf_counter() - started
    print(f"SOURCE_LOADED {source_seconds:.3f}s", flush=True)
    base = build_tables(history)
    component_seconds = time.perf_counter() - started - source_seconds
    print(f"COMPONENTS_BUILT {component_seconds:.3f}s", flush=True)
    source_audit.update({"source_binding": history.binding,
                         "action_binding": history.action_binding,
                         "hourly_bars": len(history.bars), "full_hours": len(base.components),
                         "source_content_sha256": history.content_sha256})
    write_json(report / "real_source_audit.json", source_audit)
    refs, preparations, inner = {}, {}, {}
    # factual construction timestamp remains now; historical stop identifies information
    # membership only. No object claims to have been fitted or issued in 2023.
    actual_now = pd.Timestamp.now(tz="UTC")
    for stage in ("WF1", "WF2", "PRECONFIRMATION"):
        for phase in ("INNER_TRAIN", "REFIT"):
            w = fitting_window(stage, phase, fitted_at=actual_now)
            prep = fit_preparation(base, w)
            key = stage + "_" + phase
            preparations[key] = prep
            refs[key] = save_preparation(prep, report / (key + "_preprocessing.json"))
            count = prep.population_counts["origins"]
            print(f"PREPROCESS_FITTED {key} {count} origins", flush=True)
        validation = fitting_window(stage, "INNER_VALIDATION", fitted_at=actual_now)
        view = CandidateView(base, preparations[stage + "_INNER_TRAIN"])
        rows = [admission_row(base, view, day, o, validation.stop)
                for (day, o), panel in sorted(base.panels.items())
                if validation.start <= panel.cutoff < validation.stop]
        info = summarize(rows, len(rows))
        info["calendar_tail_sessions"] = 63
        info["start"] = validation.start.isoformat()
        info["stop"] = validation.stop.isoformat()
        info["adequate_50_sessions_25_each_origin"] = (
            info["eligible_sessions"] >= 50
            and all(info["per_origin"][str(o)]["eligible"] >= 25 for o in (1, 2)))
        inner[stage] = info
    populations, all_rows, stock_masks = {}, [], []
    for period, start, stop, nominal, prep_key in (
        ("TRAIN", "2020-07-01", "2023-07-01", 1502, "WF1_REFIT"),
        ("WF1", "2023-07-01", "2024-01-01", 248, "WF1_REFIT"),
        ("WF2", "2024-01-01", "2024-07-01", 248, "WF2_REFIT"),
    ):
        lo = pd.Timestamp(start, tz="America/New_York").tz_convert("UTC")
        hi = pd.Timestamp(stop, tz="America/New_York").tz_convert("UTC")
        view = CandidateView(base, preparations[prep_key])
        rows = []
        for (day, origin), panel in sorted(base.panels.items()):
            if not lo <= panel.cutoff < hi:
                continue
            row = admission_row(base, view, day, origin, hi)
            row["period"] = period
            rows.append(row)
            for symbol in CANDIDATE:
                valid_cells = 0
                for pos in base.origin_steps[day, origin]:
                    transformed = view.row(symbol, pos, origin)
                    if transformed is not None:
                        valid_cells += len(ORDER)
                    else:
                        floors = view.preparation.floors[CANDIDATE.index(symbol)]
                        raw, _ = raw_features(base, symbol, pos, origin, floors)
                        valid_cells += sum(value is not None for value in raw)
                stock_masks.append({"period": period, "session": day, "origin": origin,
                                    "symbol": symbol, "valid_cells": valid_cells,
                                    "required_cells": 48 * 16})
        if len(rows) != nominal:
            raise ValueError("FROZEN_NOMINAL_POPULATION_CHANGED")
        populations[period] = summarize(rows, nominal)
        all_rows.extend(rows)
    retention = {
        "package": authority.policy["package"], "populations": populations, "D6g_inner": inner,
        "training_1352_of_1502_pass": populations["TRAIN"]["eligible"] >= 1352,
        "development_90pct_pass": all(populations[p]["retention"] >= .90 for p in ("WF1", "WF2")),
        "fold_85pct_100sessions_pass": all(populations[p]["retention"] >= .85
                                          and populations[p]["eligible_sessions"] >= 100
                                          for p in ("WF1", "WF2")),
        "regime_retention": "NOT_MEASURED_SEPARATE_MARKET_POLICY_AND_SCOPE_HOLD",
        "observed_certified_eligible": 0,
        "strict_observed_causality_certified": False,
        "TM0": "CONDITIONAL_CANDIDATE_PREPARATION_MEASURED_NOT_FOR_TRAINING",
        "MC0_MC1_E5": "HOLD_SEPARATE_MARKET_POLICY_AND_EXTERNAL_SCOPE",
        "DATASET_READY_FOR_FIRST_P4_3_PAIR": False,
    }
    write_json(report / "genuine_G3_population_and_retention.json", retention)
    atomic_new(report / "origin_admission.jsonl",
               ("\n".join(json.dumps(r, sort_keys=True) for r in all_rows) + "\n").encode())
    atomic_new(report / "stock_window_masks.csv",
               pd.DataFrame(stock_masks).to_csv(index=False).encode())
    store_ref = save_tables(base, report.resolve() / "canonical_components.json.gz")
    publish_oracles(base, preparations["WF1_REFIT"], report)
    if code_identity(root) != starting_code:
        raise ValueError("CODE_CHANGED_DURING_BUILD_REBUILD_IN_NEW_NAMESPACE")
    manifest = {
        "schema_version": 1, "package": authority.policy["package"],
        "study_namespace": "CAND:TRACK_A_CORE5:IDEAL_CLOCK:004",
        "designation": "ASSUMPTION_CONDITIONAL_CANDIDATE_NOT_FOR_TRAINING",
        "universe": CANDIDATE, "feature_order": ORDER, "steps": 48,
        "authority": binding, "authority_binding": authority.binding,
        "source_binding": history.binding, "action_binding": history.action_binding,
        "canonical_store": store_ref, "preparations": refs,
        "code_sha256": code_identity(root), "production_migrated": False,
        "MODEL_FIT_FORBIDDEN": True, "pair_reservation_authorized": False,
        "confirmation_numerical_access": False, "minute_data_required": False,
        "DATASET_READY_FOR_FIRST_P4_3_PAIR": False,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "timings_seconds": {"source_loading": source_seconds, "component_preparation":
                            component_seconds, "total_build": time.perf_counter() - started},
        "loader": "lstm_data.pretraining_store.load_candidate_view",
        "loader_arguments": ["root", "manifest_ref", "preparation_key"],
        "fitting_permissions": "FIT_TRANSFORM_ONLY; ML/pair/forecast/replay forbidden",
    }
    write_json(report / "canonical_dataset_manifest.json", manifest)
    examples = []
    for day in ("2020-07-01", "2020-08-28", "2020-08-31", "2021-03-12", "2021-03-15"):
        for origin in (1, 2):
            panel = base.panels[day, origin]
            for i, symbol in enumerate(CANDIDATE):
                a = history.bars[symbol, day, origin]
                b = history.bars[symbol, day, origin + 4]
                examples.append({"symbol": symbol, "session": day, "origin": origin,
                                 "entry_period_start_utc": a.start.isoformat(),
                                 "entry_period_end_utc": a.end.isoformat(),
                                 "nominal_issue_utc": panel.issuance.isoformat(),
                                 "simulated_entry_utc": panel.entry_event.isoformat(),
                                 "exit_period_start_utc": b.start.isoformat(),
                                 "exit_period_end_utc": b.end.isoformat(),
                                 "simulated_exit_utc": panel.exit_event.isoformat(),
                                 "label_maturity_utc": str(panel.maturity),
                                 "entry_close": a.close, "exit_close": b.close,
                                 "log_return": panel.returns[i],
                                 "entry_native_ids": "|".join(a.source_ids),
                                 "exit_native_ids": "|".join(b.source_ids),
                                 "entry_row_id": a.row_id, "exit_row_id": b.row_id,
                                 "proxy_age_seconds": 180, "observed_available_at": "UNKNOWN",
                                 "ideal_clock_available_at": a.end.isoformat(),
                                 "price_basis": "VENDOR_SPLIT_ADJUSTED_PRICE_ONLY",
                                 "status": "ASSUMPTION_CONDITIONAL_NO_FILL_CLAIM"})
    atomic_new(report / "hourly_proxy_reference_examples.csv",
               pd.DataFrame(examples).to_csv(index=False).encode())
    # Small family trace, raw component -> floor formula -> pooled robust scaler.
    prep = preparations["WF1_REFIT"]
    trace = []
    for day in ("2020-07-01", "2020-08-31", "2021-03-15"):
        pos = history.calendar._positions[day, 1]
        for symbol in CANDIDATE:
            p = prep.floors[CANDIDATE.index(symbol)]
            raw, reasons = raw_features(base, symbol, pos, 1, p)
            scaled = prep.scaler.apply(tuple(v for v in raw if v is not None))
            trace.append({"symbol": symbol, "session": day, "origin": 1,
                          "components": base.components[symbol, day, 1].values,
                          "floors": asdict(p), "raw_ft0": raw, "scaled_ft0": scaled,
                          "reasons": reasons, "m2": serial(asdict(base.m2[symbol, day, 1]))})
    write_json(report / "real_feature_traces.json", trace)
    print(f"BUILD_COMPLETE {time.perf_counter() - started:.3f}s", flush=True)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authority-binding", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    root = Path.cwd().resolve()
    run(root, args.authority_binding, args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
