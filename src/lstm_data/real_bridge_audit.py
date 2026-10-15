"""Portable Package005 nonconfirmation bridge audit; never invokes a model fit."""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from .clocks import execution_plan
from .config import digest, fingerprint, write_json
from .ft0_transforms import ORDER
from .labels import FitWindow
from .ledger import pair_budget, read_ledger
from .pretraining_policy import CANDIDATE, verify_ref
from .real_bridge_authority import CONTRACT, BridgeReview, bridge_code, load_review
from .real_bridge_data import build_view, first_pair_views, load_inputs, supervised_status
from .real_bridge_run import JOURNAL, journal_rows


def reference(root: Path, p: Path) -> dict:
    return {"path": str(p.resolve().relative_to(root.resolve())), "sha256": digest(p)}


def native_close(review: BridgeReview, manifest: dict, symbol: str, end: pd.Timestamp) -> dict:
    """Two exact genuine half-hours; only explicitly chosen preconfirmation examples."""
    if end >= pd.Timestamp("2024-07-01T04:00Z"):
        raise ValueError("CONFIRMATION_NATIVE_EXAMPLE_FORBIDDEN")
    start = end - pd.Timedelta(hours=1)
    found = []
    for ref in manifest["source_by_stock"][symbol]:
        p = ref["params"]
        if start < pd.Timestamp(p["start"]) or end > pd.Timestamp(p["end"]):
            continue
        path = verify_ref(review.root, {"path": ref["data"], "sha256": ref["sha256"]})
        frame = (
            pq.read_table(
                path,
                columns=["timestamp", "close"],
                filters=[
                    ("symbol", "==", symbol),
                    ("timestamp", ">=", start.to_pydatetime()),
                    ("timestamp", "<", end.to_pydatetime()),
                ],
            )
            .to_pandas()
            .sort_values("timestamp")
        )
        for row in frame.to_dict("records"):
            found.append((pd.Timestamp(row["timestamp"]), float(row["close"]), ref["data"]))
    if len(found) != 2 or tuple(r[0] for r in found) != (start, start + pd.Timedelta(minutes=30)):
        raise ValueError("INDEPENDENT_EXACT_NATIVE_PROXY_PAIR_REQUIRED")
    return {
        "close": found[-1][1],
        "keys": [str(r[0]) for r in found],
        "source": found[-1][2],
        "period_end": end.isoformat(),
    }


def audit(review: BridgeReview, out: Path) -> dict:
    started = time.monotonic()
    if (out / "dataset_input_binding.json").exists():
        raise ValueError("IMMUTABLE_BRIDGE_AUDIT_OUTPUT_EXISTS")
    out.mkdir(parents=True, exist_ok=True)
    t = time.monotonic()
    base, candidates = load_inputs(review)
    load_seconds = time.monotonic() - t
    t = time.monotonic()
    views = first_pair_views(review, candidates)
    reconstruction_seconds = time.monotonic() - t
    masks, populations, outer_views = [], {}, {}
    for name, start, stop, recipe in (
        ("TRAIN", "2020-07-01T04:00Z", "2023-07-01T04:00Z", "WF1_REFIT"),
        ("WF1", "2023-07-01T04:00Z", "2024-01-01T05:00Z", "WF1_REFIT"),
        ("WF2", "2024-01-01T05:00Z", "2024-07-01T04:00Z", "WF2_REFIT"),
    ):
        view = candidates[recipe]
        accepted = []
        for (day, origin), panel in sorted(base.panels.items()):
            if not pd.Timestamp(start) <= panel.cutoff < pd.Timestamp(stop):
                continue
            input_ok, reasons = view.input_status(day, origin)
            label_ok = bool(
                panel.label_valid
                and panel.maturity is not None
                and panel.maturity < pd.Timestamp(stop)
            )
            if input_ok and label_ok:
                view.window(day, origin)  # Actual16×48×5 and TG0, not key counts.
                accepted.append((day, origin))
            masks.append(
                {
                    "population": name,
                    "session": day,
                    "origin": origin,
                    "input_complete_five_stocks": input_ok,
                    "label_valid_matured": label_ok,
                    "reason": "ELIGIBLE" if input_ok and label_ok else ";".join(reasons),
                }
            )
        populations[name] = {
            "nominal": len([m for m in masks if m["population"] == name]),
            "FT0_and_TG0_retained": len(accepted),
            "sessions": len({d for d, _ in accepted}),
            "per_origin": {str(o): sum(x[1] == o for x in accepted) for o in (1, 2)},
        }
        if name != "TRAIN":
            w = FitWindow(
                "BRIDGE_REVIEW:" + name,
                pd.Timestamp(start),
                pd.Timestamp(stop),
                pd.Timestamp(stop),
                "INNER_VALIDATION",
            )
            outer_views[name] = build_view(review, view, w, asof=True)
    assert [populations[k]["FT0_and_TG0_retained"] for k in ("TRAIN", "WF1", "WF2")] == [
        1502,
        248,
        248,
    ]
    assert len(views["validation"].sessions) >= 50
    assert all(sum(r.origin == o for r in views["validation"].rows) >= 25 for o in (1, 2))
    all_views = {**views, **outer_views}
    cells = 0
    for value in all_views.values():
        for first in range(0, len(value.sessions), 16):
            batch = value.batch(tuple(range(first, min(first + 16, len(value.sessions)))))
            cells += int(batch.origins.sum()) * 5 * 48 * 16
    for name, value in outer_views.items():
        assert len(value.rows) / 248 >= 0.9 and len(value.sessions) >= 100
        allowed = {(r.session, r.origin) for r in value.rows}
        for mask in masks:
            if mask["population"] == name:
                mask["TM0_ASOF_model_eligible"] = (mask["session"], mask["origin"]) in allowed
    with (out / "day_origin_masks.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[*masks[0], "TM0_ASOF_model_eligible"])
        writer.writeheader()
        writer.writerows(masks)
    for key, value in views.items():
        rows = [{"session": r.session, "origin": r.origin, "admitted": True} for r in value.rows]
        rows += [
            {"session": k[0], "origin": k[1], "admitted": False, "reason": reason}
            for k, reason in value.excluded
        ]
        write_json(
            out / (key + "_mask.json"), sorted(rows, key=lambda r: (r["session"], r["origin"]))
        )
    # Independently verify epsilon from the exact earlier supervised prefix only.
    epsilon = {}
    for name, key in (("inner", "WF1_INNER_TRAIN"), ("refit", "WF1_REFIT")):
        mads = []
        for row in views[name].rows:
            returns = base.panels[row.session, row.origin].returns
            values = [x for x in returns if x is not None]
            center = statistics.median(values)
            mads.append(statistics.median(abs(x - center) for x in values))
        expected = max(1e-4, 0.1 * statistics.median(mads))
        actual = candidates[key].preparation.target_epsilon
        assert expected == actual
        epsilon[name] = {"independent": expected, "recipe": actual, "origins": len(mads)}
    old_root = (review.root / review.producer["manifest"]["path"]).parent
    oracle_path = old_root / "build_v4/independent_real_oracles.json"
    # Producer inventory binds the inherited independent full-feature oracle.
    inventory = Path(verify_ref(review.root, review.producer["inventory"]))
    old_hashes = {r["path"]: r["sha256"] for r in csv.DictReader(inventory.open())}
    assert digest(oracle_path) == old_hashes[str(oracle_path.relative_to(review.root))]
    independent = json.loads(oracle_path.read_text())
    traces = []
    for example in independent:
        row = next(r for r in views["refit"].rows if r.session == example["day"] and r.origin == 1)
        actual = views["refit"].values[row.indices[0][-1]].numpy()
        expected = np.asarray(example["scaled_values"], dtype=np.float32)
        assert np.array_equal(actual, expected)
        traces.append(
            {
                "day": example["day"],
                "symbol": "AAPL",
                "features": ORDER,
                "independent_raw": example["independent_values"],
                "scaled_float32": actual.tolist(),
                "all16_exact_float32_match": True,
                "inherited_independent_oracle": reference(review.root, oracle_path),
            }
        )
    manifest = json.loads(
        verify_ref(review.root, review.preparation_authority.policy["source_manifest"]).read_text()
    )
    examples = []
    for day in ("2020-07-01", "2020-08-28", "2020-08-31", "2021-03-15"):
        for origin in (1, 2):
            panel = base.panels[day, origin]
            entry = [native_close(review, manifest, s, panel.cutoff) for s in CANDIDATE]
            exit_rows = [
                native_close(review, manifest, s, panel.cutoff + pd.Timedelta(hours=4))
                for s in CANDIDATE
            ]
            returns = [math.log(b["close"] / a["close"]) for a, b in zip(entry, exit_rows)]
            center = statistics.median(returns)
            mad = statistics.median(abs(x - center) for x in returns)
            eps = candidates["WF1_REFIT"].preparation.target_epsilon
            y = [(x - center) / (mad + eps) for x in returns]
            _, stored = candidates["WF1_REFIT"].window(day, origin)
            assert np.allclose(y, stored, rtol=0, atol=1e-12)
            for i, symbol in enumerate(CANDIDATE):
                assert entry[i]["close"] == panel.entry_prices[i]
                assert exit_rows[i]["close"] == panel.exit_prices[i]
                examples.append(
                    {
                        "day": day,
                        "origin": origin,
                        "symbol": symbol,
                        "cutoff_UTC": panel.cutoff.isoformat(),
                        "cutoff_ET": panel.cutoff.tz_convert("America/New_York").isoformat(),
                        "issuance_UTC": panel.issuance.isoformat(),
                        "entry_event_UTC": panel.entry_event.isoformat(),
                        "exit_event_UTC": panel.exit_event.isoformat(),
                        "maturity_UTC": str(panel.maturity),
                        "entry_proxy_end_UTC": entry[i]["period_end"],
                        "exit_proxy_end_UTC": exit_rows[i]["period_end"],
                        "entry_close": entry[i]["close"],
                        "exit_close": exit_rows[i]["close"],
                        "log_return": returns[i],
                        "median": center,
                        "MAD": mad,
                        "epsilon": eps,
                        "TG0": y[i],
                        "entry_native_keys": ";".join(entry[i]["keys"]),
                        "exit_native_keys": ";".join(exit_rows[i]["keys"]),
                        "designation": "ASSUMPTION_CONDITIONAL_PRICE_PROXY_NOT_FILL",
                    }
                )
    with (out / "hourly_proxy_and_maturity_examples.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(examples[0]))
        writer.writeheader()
        writer.writerows(examples)
    # Actual C01 counterfactual in memory; canonical source/store files stay immutable.
    panel = base.panels["2020-07-01", 1]
    changed = replace(panel, outcome_valid=(False, *panel.outcome_valid[1:]), maturity=None)
    counter = replace(base, panels={**base.panels, (panel.session, panel.origin): changed})
    assert counter.potential(panel.session, panel.origin) == base.potential(
        panel.session, panel.origin
    )
    assert supervised_status(
        counter,
        panel.session,
        panel.origin,
        views["refit"].window,
        candidates["WF1_REFIT"].preparation.window.stop,
        asof=False,
    ).startswith("LABEL_")
    assert not execution_plan(base.history.calendar.clock("2020-11-27"), 1).calendar_valid
    target_values = [abs(x) for r in views["refit"].rows for x in r.targets]
    energy = []
    for day in views["refit"].sessions:
        energy.append(
            float(
                np.mean(
                    [np.mean(np.square(r.targets)) for r in views["refit"].rows if r.session == day]
                )
            )
        )
    tail = {
        str(p): sum(sorted(energy, reverse=True)[: max(1, math.ceil(len(energy) * p))])
        / sum(energy)
        for p in (0.01, 0.05, 0.1)
    }
    input_id = fingerprint(
        [
            review.binding,
            bridge_code(review.root),
            {k: v.version for k, v in all_views.items()},
            ORDER,
            CANDIDATE,
        ]
    )
    binding = {
        "schema": 1,
        "status": "BRIDGE_READY",
        "input_id": input_id,
        "MODEL_FIT_AUTHORIZED": False,
        "DATASET_READY_FOR_FIRST_P4_3_PAIR": False,
        "review_binding": review.binding,
        "producer": review.producer_ref,
        "code_sha256": bridge_code(review.root),
        "contract": CONTRACT,
        "first_pair_views": {k: v.version for k, v in views.items()},
        "views": {k: v.summary() for k, v in all_views.items()},
        "canonical_stock_store": review.manifest["canonical_store"],
        "SPY_store_reference_only_not_TM0_input": review.manifest["market_components"],
        "feature_order": ORDER,
        "shape": [5, 48, 16],
        "dense_windows_saved": False,
        "strict_observed_causality_certified": False,
        "preprocessing_actual_vs_historical": (
            "Original actual constructed_at preserved; window.stop is counterfactual historical "
            "information membership, not proof a model existed then"
        ),
    }
    write_json(out / "dataset_input_binding.json", binding)
    write_json(
        out / "eligibility_and_retention.json",
        {
            "source_FT0_TG0_populations": populations,
            "model_views": binding["views"],
            "finite_batch_cells_checked": cells,
            "nominal_training_threshold": 1352,
            "training_pass": len(views["refit"].rows) >= 1352,
            "model_development_90pct_pass": True,
            "invalid_source_admitted": 0,
            "confirmation_numeric_rows": 0,
            "target_abs_max": max(target_values),
            "target_only_squared_energy_concentration": tail,
            "no_estimator_or_benchmark_fitted": True,
            "epsilon_independent_checks": epsilon,
        },
    )
    write_json(
        out / "train_prefix_and_inner_tail.json",
        {
            "calendar_sessions": 63,
            "tail_start": "2023-03-31",
            "tail_stop": "2023-07-01",
            "nominal_origins": 126,
            "eligible_sessions": len(views["validation"].sessions),
            "eligible_origins": len(views["validation"].rows),
            "excluded_lookbacks": views["validation"].excluded,
            "minima": {"sessions": 50, "each_origin": 25},
            "actual_recipe_windows": {
                k: {
                    "window": str(candidates[k].preparation.window),
                    "constructed_at": candidates[k].preparation.constructed_at,
                    "preparation_id": candidates[k].preparation.preparation_id,
                }
                for k in ("WF1_INNER_TRAIN", "WF1_REFIT")
            },
        },
    )
    write_json(
        out / "independent_numeric_checks.json",
        {
            "all16_bridge_vs_inherited_independent_oracle": traces,
            "fresh_native_proxy_rows": len(examples),
            "epsilon": epsilon,
            "C01_future_outcome_removed_inputs_unchanged": True,
            "early_close_reject": True,
            "source_GETs": 0,
            "confirmation_numeric_rows": 0,
        },
    )
    legacy = review.root / "reports/audit/track_a_events.jsonl"
    assert pair_budget(read_ledger(legacy))["attempted_pairs"] == 0
    actual_rows = journal_rows(review.root / JOURNAL)
    assert not actual_rows
    write_json(
        out / "experiment_registry.json",
        {
            "status": "NOT_STARTED",
            "legacy": reference(review.root, legacy),
            "append_only_real_journal": JOURNAL,
            "real_journal_exists": (review.root / JOURNAL).exists(),
            "real_pairs_started": 0,
            "ceiling": 40,
            "reserved": False,
            "neural_training": "N/A",
        },
    )
    proposal = {
        "schema": 1,
        "status": "PROPOSED_NOT_AUTHORIZED",
        "review_binding": review.binding,
        "input_id": input_id,
        "code_sha256": bridge_code(review.root),
        "contract": CONTRACT,
        "dataset_input_binding": reference(review.root, out / "dataset_input_binding.json"),
        "legacy_ledger": reference(review.root, legacy),
        "new_append_only_journal": JOURNAL,
        "registry_definition": reference(
            review.root, review.root / "configs/track_a_candidate_experiment_registry_v1.json"
        ),
        "registry_transition": (
            "Activate CURRENT_EXPERIMENT_REGISTRY only at the authorized first fit; "
            "preserve legacy history and production D1"
        ),
        "production_migration": False,
        "course_substitution": False,
        "requires": [
            "exact attributable researcher GO including retrospective parameter application",
            "actual applicable local research-use rights evidence",
            "attributable Track B common-clock acknowledgment",
            "bound applicable conditional G0-G5 evidence and G6 postrun plan",
        ],
    }
    write_json(out / "single_run_proposal.json", proposal)
    write_json(
        out / "training_authority_PENDING.json",
        {
            "status": "TRAINING_HOLD",
            "proposal": reference(review.root, out / "single_run_proposal.json"),
            "no_human_response_or_external_evidence_created": True,
        },
    )
    timings = {
        "canonical_store_load": load_seconds,
        "prefix_view_reconstruction": reconstruction_seconds,
        "total_bridge_audit": time.monotonic() - started,
    }
    write_json(
        out / "training_actual_runtime.json",
        {
            "status": "NOT_AUTHORIZED_NOT_RUN",
            "bridge_audit_seconds": timings,
            "calibration_neural_seconds": "N/A",
            "refit_neural_seconds": "N/A",
            "test_suite_seconds": "RECORDED_SEPARATELY_IN_CHECKS",
            "preprocessing_statistics": "REUSED_IMMUTABLE_RECIPES_NOT_REFITTED",
        },
    )
    return {"input_id": input_id, "views": binding["views"], "seconds": timings}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--producer", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args()
    root = Path.cwd()
    review = load_review(root, reference(root, args.producer))
    print(json.dumps(audit(review, args.report), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
