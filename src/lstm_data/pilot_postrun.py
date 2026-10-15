"""Package006: locked-checkpoint inference and separately approved P3 baselines.

No optimizer, neural fit, trading replay or confirmation path is exposed here.
The synthetic-only P3 public interfaces remain untouched; their pure weighted
algebra and declared lag/penalty constants are reused for reviewed real views.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .baseline_ridge import LAGS, PENALTIES, choose_penalty, session_weights, solve_weighted
from .config import atomic_new, digest, write_json
from .ft0_transforms import identity
from .labels import FitWindow
from .market_features import MarketMeasures
from .neural_engine import SharedLSTM, batch_prediction, session_batches
from .neural_health import g6_summary
from .neural_lifecycle import EarlyStop
from .pretraining_market import conditional_vector
from .pretraining_policy import CANDIDATE, verify_ref
from .pretraining_source import BARRIER
from .pretraining_tables import BaseTables
from .real_bridge_authority import CONTRACT, load_review
from .real_bridge_data import RealInputView, build_view, first_pair_views, load_inputs
from .real_bridge_run import daily_ic, journal_rows, rank_ic


def target_array(view: RealInputView) -> np.ndarray:
    """Use the actual float32 neural targets, with no new floor or normalization."""
    return np.asarray([r.targets for r in view.rows], dtype=np.float32)


def lag_design(sequence: np.ndarray) -> np.ndarray:
    """Frozen lag-major/channel-minor112 columns from five48×16 stock histories."""
    if sequence.shape != (5, 48, 16) or not np.isfinite(sequence).all():
        raise ValueError("FIVE_FINITE_48_BY_16_STOCK_SEQUENCES_REQUIRED")
    return sequence[:, [47 - lag for lag in LAGS], :].reshape(5, 112).astype(np.float64)


def design(view: RealInputView) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    view.verify()
    x = np.concatenate([lag_design(view.values[np.asarray(r.indices)].numpy()) for r in view.rows])
    keys = tuple((r.session, r.origin, s) for r in view.rows for s in CANDIDATE)
    return x, target_array(view).astype(np.float64).reshape(-1), session_weights(keys)


def summarize(view: RealInputView, scores: np.ndarray) -> dict:
    """Equal-stock/origin/day metrics; uncertainty and economics are not inferred."""
    y = target_array(view).astype(np.float64)
    if scores.shape != y.shape or not np.isfinite(scores).all():
        raise ValueError("FINITE_MATCHED_FIVE_SCORE_POPULATION_REQUIRED")
    origin_mse = np.mean((scores - y) ** 2, axis=1)
    ranks = [rank_ic(tuple(p), tuple(t)) for p, t in zip(scores, y)]
    days = sorted(set(r.session for r in view.rows))
    daily = []
    for day in days:
        indices = [i for i, r in enumerate(view.rows) if r.session == day]
        vals = [value for i in indices if (value := ranks[i][0]) is not None]
        daily.append(
            {
                "session": day,
                "MSE": float(np.mean(origin_mse[indices])),
                "IC": float(np.mean(vals)) if vals else None,
            }
        )
    ic_rows = tuple(
        (r.session, ranks[i][0], ranks[i][1] == "DEFINED") for i, r in enumerate(view.rows)
    )
    return {
        "origins": len(view.rows),
        "sessions": len(days),
        "MSE": float(np.mean([r["MSE"] for r in daily])),
        "daily_Rank_IC": daily_ic(ic_rows, defined_only=False),
        "defined_only_daily_Rank_IC": daily_ic(ic_rows, defined_only=True),
        "score_std": float(np.std(scores)),
        "score_variance": float(np.var(scores)),
        "finite_predictions": int(scores.size),
        "constant_forecast_origins": int(sum(np.ptp(p) == 0 for p in scores)),
        "tied_score_origins": sum(len(set(p)) < 5 for p in scores),
        "constant_target_origins": sum(status.startswith("TARGET_CONSTANT") for _, status in ranks),
        "by_origin": {
            str(o): {
                "count": sum(r.origin == o for r in view.rows),
                "MSE": float(
                    np.mean([origin_mse[i] for i, r in enumerate(view.rows) if r.origin == o])
                ),
                "IC": daily_ic(
                    tuple(
                        (r.session, ranks[i][0], ranks[i][1] == "DEFINED")
                        for i, r in enumerate(view.rows)
                        if r.origin == o
                    ),
                    defined_only=False,
                ),
            }
            for o in (1, 2)
        },
        "monthly": {
            month: {
                "sessions": sum(r["session"].startswith(month) for r in daily),
                "MSE": float(np.mean([r["MSE"] for r in daily if r["session"].startswith(month)])),
                "IC": float(
                    np.mean(
                        [
                            r["IC"]
                            for r in daily
                            if r["session"].startswith(month) and r["IC"] is not None
                        ]
                    )
                )
                if any(r["session"].startswith(month) and r["IC"] is not None for r in daily)
                else None,
            }
            for month in sorted({d[:7] for d in days})
        },
        "daily": daily,
    }


def locked_scores(view: RealInputView, checkpoint: Path, manifest: dict, key: str) -> np.ndarray:
    """Safe, frozen-weight inference only; no fitting authority or optimizer used."""
    if digest(checkpoint) != manifest["sha256"]:
        raise ValueError("HISTORICAL_CHECKPOINT_HASH_CHANGED")
    obj = torch.load(checkpoint, map_location="cpu", weights_only=True)
    if (
        obj["contract"] != CONTRACT
        or obj["pair_key"] != key
        or obj["preparation_id"] != view.preparation_id
        or obj["epoch"] != 4
        or obj["stage"] != manifest["stage"]
    ):
        raise ValueError("EXACT_HISTORICAL_CHECKPOINT_PREPARATION_REQUIRED")
    model = SharedLSTM(16)
    model.load_state_dict(obj["model"], strict=True)
    model.eval().requires_grad_(False)
    lookup = {}
    with torch.inference_mode():
        for positions in session_batches(len(view.sessions), 42, 1, shuffle=False):
            batch = view.batch(positions)
            p = batch_prediction(model, batch)
            for i, day in enumerate(batch.ids):
                for origin in (1, 2):
                    if batch.origins[i, origin - 1]:
                        lookup[day, origin] = p[i, origin - 1].numpy().copy()
    return np.asarray([lookup[r.session, r.origin] for r in view.rows])


def require_baseline_decision(decision: dict, proposal: Path) -> None:
    """An explicit real-baseline approval is separate from the consumed TM0 GO."""
    if (
        decision.get("actor_type") != "human"
        or decision.get("owner") != "Track A researcher"
        or decision.get("status") != "APPROVED"
        or decision.get("scope") != "M1_AND_OWN_RIDGE_112_WF1_ONLY"
        or decision.get("proposal_sha256") != digest(proposal)
        or not decision.get("response_text")
        or not decision.get("response_provenance")
    ):
        raise ValueError("EXACT_ATTRIBUTABLE_NONNEURAL_BASELINE_APPROVAL_REQUIRED")


def market_readiness(base: BaseTables, views: dict[str, RealInputView], store: dict) -> dict:
    """Review existing U1–U5 recipes and actual matched masks; grant no MC0 fit."""
    measures = []
    for original in store["measures"]:
        row = dict(original)
        row["timestamp"] = pd.Timestamp(row["timestamp"])
        if row["timestamp"] >= BARRIER:
            raise ValueError("CONFIRMATION_MARKET_VECTOR_FORBIDDEN")
        row["evidence_ids"] = tuple(row["evidence_ids"])
        measures.append(MarketMeasures(**row))
    summary = {}
    for key, view in views.items():
        recipe_key = "WF1_INNER_TRAIN" if key in {"inner", "validation"} else "WF1_REFIT"
        recipe = store["preparations"][recipe_key]
        transformed = {}
        for row in measures:
            raw = conditional_vector(row, recipe["hourly_floor"], recipe["daily_floor"])
            if raw is not None:
                transformed[row.timestamp] = np.asarray(
                    [
                        0.0 if method == "CONSTANT" else (v - c) / s
                        for v, c, s, method in zip(
                            raw, recipe["centers"], recipe["scales"], recipe["methods"]
                        )
                    ],
                    dtype=np.float32,
                )
        valid, invalid, finite_cells = [], [], 0
        for r in view.rows:
            steps = [base.history.calendar.steps[p] for p in base.origin_steps[r.session, r.origin]]
            mask = [s.end in transformed for s in steps]
            asof = key in {"validation", "WF1"}
            clock = not asof or all(s.end >= pd.Timestamp(recipe["window"]["stop"]) for s in steps)
            vectors = [transformed[s.end] for s in steps if s.end in transformed]
            if (
                mask[-1]
                and sum(mask) >= 46
                and clock
                and all(np.isfinite(v).all() for v in vectors)
            ):
                valid.append((r.session, r.origin))
                finite_cells += sum(mask) * 5
            else:
                invalid.append((r.session, r.origin))
        summary[key] = {
            "stock_origins": len(view.rows),
            "matched_market_origins": len(valid),
            "matched_sessions": len({d for d, _ in valid}),
            "excluded_keys": invalid,
            "stock_view_id": view.version,
            "market_recipe_id": identity(recipe),
            "matched_mask_id": identity(valid),
            "finite_market_cells_before_replication": finite_cells,
            "shape_if_joined": [5, 48, 21],
            "market_source_shared_across_five": True,
            "neutral_missing_fill": "STANDARDIZED_ZERO_WITH_SEPARATE_AUDIT_MASK",
            "clock_evidence": "IDEALIZED_PERIOD_END_NOT_OBSERVED_PUBLICATION",
            "actual_recipe_fitted_at": recipe["window"]["fitted_at"],
            "historical_information_stop": recipe["window"]["stop"],
        }
    return {
        "status": "P4_4_HOLD",
        "input_review": summary,
        "parameters": sum(p.numel() for p in SharedLSTM(21).parameters()),
        "neural_training": "NOT_RUN_NOT_AUTHORIZED",
        "holds": [
            "Separate exact MC0 authorization and qualified SPY fitting scope",
            "Candidate MC0 typed executor and multi-pair journal version not implemented",
        ],
        "pair_budget": "1/40",
        "production_migration": False,
    }


def run_baselines(
    views: dict[str, RealInputView], decision: dict, proposal: Path, attempt: Path
) -> tuple[dict, dict]:
    require_baseline_decision(decision, proposal)
    t = time.monotonic()
    x, y, weights = design(views["inner"])
    vx, vy, vw = design(views["validation"])
    fx, fy, fw = design(views["refit"])
    ex, _, _ = design(views["WF1"])
    application_seconds = time.monotonic() - t
    candidates = []
    atomic_new(
        attempt,
        (
            json.dumps(
                {
                    "status": "STARTED_NONNEURAL_BASELINES",
                    "proposal_sha256": digest(proposal),
                    "scope": "M1_AND_OWN_RIDGE_112_WF1_ONLY",
                    "neural_fits": 0,
                }
            )
            + "\n"
        ).encode(),
    )
    t = time.monotonic()
    for penalty in PENALTIES:
        solution = solve_weighted(x, y, weights, penalty)
        error = vy - solution.intercept - vx @ np.asarray(solution.coefficients)
        candidates.append(
            {
                "penalty": penalty,
                "validation_MSE": float(vw @ (error**2)),
                "condition": solution.condition,
                "residual": solution.residual_norm,
            }
        )
    selection_seconds = time.monotonic() - t
    chosen = choose_penalty(tuple((r["penalty"], r["validation_MSE"]) for r in candidates))
    t = time.monotonic()
    final = solve_weighted(fx, fy, fw, chosen)
    refit_seconds = time.monotonic() - t
    t = time.monotonic()
    ridge = (final.intercept + ex @ np.asarray(final.coefficients)).reshape(-1, 5)
    m1 = np.asarray(
        [views["WF1"].values[np.asarray(r.indices)][:, -1, 0].numpy() for r in views["WF1"].rows]
    )
    scores = {"M1": m1, "RIDGE_OWN_112": ridge}
    summary = {name: summarize(views["WF1"], s) for name, s in scores.items()}
    evaluation_seconds = time.monotonic() - t
    return {
        "status": "COMPLETED_EXPLICITLY_APPROVED_NONNEURAL_BASELINES",
        "approval": decision,
        "proposal_sha256": digest(proposal),
        "candidates": candidates,
        "chosen_penalty": chosen,
        "final": {
            "intercept": final.intercept,
            "coefficients": final.coefficients,
            "condition": final.condition,
            "residual": final.residual_norm,
        },
        "timing_seconds": {
            "design_recipe_application": application_seconds,
            "five_inner_solutions": selection_seconds,
            "fresh_refit": refit_seconds,
            "prediction_and_metrics": evaluation_seconds,
        },
        "fit_counts": {"inner": 5, "fresh_refit": 1, "neural": 0},
        "metrics": summary,
        "mask": views["WF1"].summary(),
        "matrix_basis": (
            "Float64 algebra on the identical float32 FT0 values and TG0 targets seen by TM0"
        ),
        "prior_synthetic_guards_unchanged": True,
    }, scores


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", type=Path, required=True)
    parser.add_argument("--bridge", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--baseline-decision", type=Path)
    args = parser.parse_args()
    started = time.monotonic()
    out = args.report
    if (out / "pilot_metrics.json").exists():
        raise ValueError("IMMUTABLE_REVIEW_OUTPUT_ALREADY_EXISTS")
    out.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(1)
    run = args.pilot / "first_tm0_seed42_WF1"
    result = json.loads((run / "seed42_tm0_first_pair_result.json").read_text())
    binding = json.loads((args.bridge / "final_v2/dataset_input_binding.json").read_text())
    journal = journal_rows(Path("reports/audit/track_a_real_pairs_v1.jsonl"))
    if [r["status"] for r in journal] != ["STARTED", "CALIBRATED", "REFITTING", "COMPLETED"]:
        raise ValueError("EXACT_ONE_COMPLETED_NEURAL_PAIR_REQUIRED")
    cal = tuple(json.loads(p.read_text()) for p in sorted(run.glob("calibration_epoch_*.json")))
    refit = tuple(json.loads(p.read_text()) for p in sorted(run.glob("refit_epoch_*.json")))
    selector = EarlyStop()
    for row in cal:
        selector.observe(row["validation"]["mse"])
        if vars(selector) != row["selection"]:
            raise ValueError("HISTORICAL_SELECTION_TRACE_CHANGED")
    if vars(selector) != result["selector"] or len(refit) != selector.selected:
        raise ValueError("HISTORICAL_FRESH_REFIT_EPOCHS_CHANGED")
    review = load_review(
        Path.cwd(),
        {
            "path": str(args.bridge / "verified_producer.json"),
            "sha256": digest(args.bridge / "verified_producer.json"),
        },
    )
    base, candidates = load_inputs(review, ("WF1_INNER_TRAIN", "WF1_REFIT"))
    views = first_pair_views(review, candidates)
    w = FitWindow(
        "BRIDGE_REVIEW:WF1",
        pd.Timestamp("2023-07-01T04:00Z"),
        pd.Timestamp("2024-01-01T05:00Z"),
        pd.Timestamp("2024-01-01T05:00Z"),
        "INNER_VALIDATION",
    )
    views["WF1"] = build_view(review, candidates["WF1_REFIT"], w, asof=True)
    for key, view in views.items():
        if view.version != binding["views"][key]["view_id"]:
            raise ValueError("EXACT_HISTORICAL_VIEW_ID_REQUIRED")
    market_path = verify_ref(Path.cwd(), binding["SPY_store_reference_only_not_TM0_input"])
    write_json(
        out / "mc0_input_readiness.json",
        market_readiness(base, views, json.loads(gzip.decompress(market_path.read_bytes()))),
    )
    t = time.monotonic()
    predictions, metrics = {}, {}
    for key in ("validation", "refit", "WF1"):
        checkpoint = "calibration_selected" if key == "validation" else "refit_final"
        manifest = json.loads((run / (checkpoint + ".manifest.json")).read_text())
        predictions[key] = locked_scores(
            views[key], run / (checkpoint + ".pt"), manifest, result["pair_key"]
        )
        metrics[key] = summarize(views[key], predictions[key])
    inference_seconds = time.monotonic() - t
    for key, expected in (
        ("validation", result["selector"]["best"]),
        ("refit", result["refit_train_evaluation"]["mse"]),
        ("WF1", result["development"]["mse"]),
    ):
        if abs(metrics[key]["MSE"] - expected) > 2e-6:
            raise ValueError("LOCKED_INFERENCE_DOES_NOT_REPRODUCE_HISTORICAL_METRICS")
    zero = summarize(views["WF1"], np.zeros((len(views["WF1"].rows), 5)))
    health = g6_summary(
        tuple(r["training"] for r in cal),
        refit,
        result["development"]["score_std"],
        selector.status,
    )
    clipping = [
        {"pass": phase, "epoch": r["epoch"], **r["gradients"]}
        for phase, records in (("calibration", tuple(r["training"] for r in cal)), ("refit", refit))
        for r in records
    ]
    with (out / "clipping_by_epoch.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(clipping[0]))
        writer.writeheader()
        writer.writerows(clipping)
    quantiles = {
        key: {
            str(q): float(np.quantile(target_array(view), q))
            for q in (0, 0.01, 0.1, 0.5, 0.9, 0.99, 1)
        }
        for key, view in views.items()
    }
    write_json(
        out / "training_health_review.json",
        {
            "G6": health,
            "TG0_quantiles": quantiles,
            "quantile_basis": "Actual float32 targets",
            "source_loss_shares": {
                "train": result["refit_train_evaluation"]["top_session_loss_share"],
                "WF1": result["development"]["top_session_loss_share"],
            },
            "selected_epoch": selector.selected,
            "selected_before_warning_epochs": True,
            "batch_telemetry_limit": (
                "Only per-epoch norm quantiles/fractions were saved; per-batch attribution absent."
            ),
            "gradient_accumulation_code": (
                "Each batch calls zero_grad, backward, clip once, step once; no accumulation."
            ),
            "outlier_attribution": (
                "High target/loss concentration is compatible with large gradients. "
                "Per-example gradients absent; causal attribution unproven."
            ),
        },
    )
    baseline, scores = {"status": "BASELINES_NOT_RUN_NO_APPROVAL"}, {}
    if args.baseline_decision:
        baseline, scores = run_baselines(
            views,
            json.loads(args.baseline_decision.read_text()),
            out / "baseline_proposal_v1.json",
            out / "baseline_started.json",
        )
    write_json(out / "baseline_execution.json", baseline)
    predictions["WF1_ZERO"] = np.zeros_like(predictions["WF1"])
    with (out / "permitted_prediction_snapshot.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ("partition", "session", "origin", "symbol", "TG0", "TM0", "M1", "RIDGE_OWN_112")
        )
        for key in ("validation", "refit", "WF1"):
            targets = target_array(views[key])
            for i, row in enumerate(views[key].rows):
                for j, symbol in enumerate(CANDIDATE):
                    writer.writerow(
                        (
                            key,
                            row.session,
                            row.origin,
                            symbol,
                            float(targets[i, j]),
                            float(predictions[key][i, j]),
                            float(scores["M1"][i, j]) if key == "WF1" and scores else "",
                            float(scores["RIDGE_OWN_112"][i, j]) if key == "WF1" and scores else "",
                        )
                    )
    summary = {
        "status": "ACCEPT_WITH_G6_WARN",
        "metrics": metrics,
        "zero_reference": zero,
        "views": {key: view.summary() for key, view in views.items()},
        "new_inference_only": True,
        "original_forecasts_were_not_persisted": True,
        "historical_metrics_reproduced_tolerance": 2e-6,
        "inference_seconds": inference_seconds,
        "fresh_model_fits": 0,
        "neural_pair_budget": "1/40",
        "confirmation_outcome_rows": 0,
        "preparation_windows": {k: identity(v.preparation.window) for k, v in candidates.items()},
        "inner_calendar_tail": {
            "start": views["validation"].window.start.isoformat(),
            "stop": views["validation"].window.stop.isoformat(),
        },
        "total_analysis_seconds": time.monotonic() - started,
        "data_population": len(base.panels),
        "new_source_requests": 0,
    }
    write_json(out / "pilot_metrics.json", summary)
    print(
        json.dumps(
            {
                "status": summary["status"],
                "baselines": baseline["status"],
                "seconds": summary["total_analysis_seconds"],
                "neural_budget": "1/40",
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
