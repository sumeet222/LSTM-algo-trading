"""Read-only, matched Package007 review; no optimizer, fitting or journal writes."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import digest, write_json
from .neural_engine import session_batches
from .neural_health import g6_summary
from .peer_inputs import peer_summaries
from .pilot_postrun import locked_scores, summarize, target_array
from .pretraining_policy import CANDIDATE
from .real_batch_authority import load_pair_authority, load_plan
from .real_batch_data import ConditionedView, load_batch_inputs
from .real_bridge_run import batch_prediction, execution_model, load_real_checkpoint

GRADE = "ASSUMPTION_CONDITIONAL_RESEARCHER_ATTESTED_RETROSPECTIVE_IDEAL_CLOCK_HOURLY_PROXY"


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def table(path: Path, rows: list[dict]) -> None:
    with path.open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def predictions(model, view: ConditionedView) -> np.ndarray:
    """Chronological evaluation with immutable origin order and five-stock order."""
    lookup = {}
    model.eval().requires_grad_(False)
    with torch.inference_mode():
        for positions in session_batches(len(view.sessions), 42, 1, shuffle=False):
            batch = view.batch(positions)
            scores = batch_prediction(model, batch)
            for i, day in enumerate(batch.ids):
                for origin in (1, 2):
                    if bool(batch.origins[i, origin - 1]):
                        lookup[day, origin] = scores[i, origin - 1].numpy().copy()
    return np.asarray([lookup[r.session, r.origin] for r in view.rows])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    out = args.package
    plan_ref = {"path": str(out / "batch_plan.json"), "sha256": digest(out / "batch_plan.json")}
    approval_ref = {
        "path": str(out / "batch_authorization.json"),
        "sha256": digest(out / "batch_authorization.json"),
    }
    plan, review = load_plan(Path.cwd(), plan_ref)
    inputs = load_batch_inputs(review, read(Path(plan["dataset"]["path"])))
    stock = inputs.stock_view("WF1")
    keys = [(r.session, r.origin) for r in stock.rows]
    if len(keys) != 232 or len(stock.sessions) != 116:
        raise ValueError("EXPECTED_UNCHANGED_WF1_POPULATION_REQUIRED")
    y = target_array(stock)
    snapshot = pd.read_csv(plan["baseline_snapshot"]["path"], float_precision="round_trip")
    snapshot = snapshot.loc[snapshot.partition == "WF1"]
    actual_keys = list(zip(snapshot.session, snapshot.origin, snapshot.symbol))
    expected_keys = [(day, origin, symbol) for day, origin in keys for symbol in CANDIDATE]
    if actual_keys != expected_keys or not np.array_equal(
        snapshot.TG0.to_numpy().reshape(-1, 5), y
    ):
        raise ValueError("HISTORICAL_BASELINE_TARGET_OR_KEY_MISMATCH")
    tm0_result_path = Path(plan["tm0_result"]["path"])
    tm0 = read(tm0_result_path)
    torch.set_num_threads(1)
    scores = {
        "TM0": locked_scores(
            stock,
            tm0_result_path.parent / "refit_final.pt",
            tm0["final_checkpoint"],
            tm0["pair_key"],
        ),
        "ZERO": np.zeros_like(y),
        "M1": snapshot.M1.to_numpy().reshape(-1, 5),
        "RIDGE_OWN_112": snapshot.RIDGE_OWN_112.to_numpy().reshape(-1, 5),
    }
    if not np.array_equal(scores["TM0"], snapshot.TM0.to_numpy().reshape(-1, 5)):
        raise ValueError("ORIGINAL_TM0_CHECKPOINT_PREDICTIONS_CHANGED")
    health, runtimes = {}, {}
    verification: dict = {"TM0_frozen_checkpoint_exact_snapshot_match": True}
    for architecture in ("MC0", "MC1", "E5"):
        folder = out / architecture
        result = read(folder / f"seed42_{architecture.lower()}_pair_result.json")
        authority = load_pair_authority(Path.cwd(), plan_ref, approval_ref, architecture)
        authority.cache["inputs"] = inputs
        view = authority.view("WF1")
        if [(r.session, r.origin) for r in view.rows] != keys:
            raise ValueError("NEW_MODEL_WF1_KEY_MISMATCH")
        model = execution_model(authority)
        load_real_checkpoint(
            folder / "refit_final.pt",
            model,
            result["pair_key"],
            view.preparation_id,
            "REFIT_FINAL",
            authority,
        )
        scores[architecture] = predictions(model, view)
        records = result["development"]["origin_records"]
        if [(r["session"], r["origin"]) for r in records] != keys:
            raise ValueError("STORED_PREDICTION_ORDER_MISMATCH")
        if not np.array_equal(scores[architecture], np.asarray([r["scores"] for r in records])):
            raise ValueError("FINAL_CHECKPOINT_PREDICTIONS_CHANGED")
        if not np.array_equal(y, np.asarray([r["targets"] for r in records])):
            raise ValueError("NEW_MODEL_TARGET_MISMATCH")
        calibration = [read(p) for p in sorted(folder.glob("calibration_epoch_*.json"))]
        refit = [read(p) for p in sorted(folder.glob("refit_epoch_*.json"))]
        h = g6_summary(
            tuple(r["training"] for r in calibration),
            tuple(refit),
            result["development"]["score_std"],
            result["selector"]["status"],
        )
        h["calibration"] = [
            {
                "epoch": r["training"]["epoch"],
                "train_MSE": r["training"]["mse"],
                "validation_MSE": r["validation"]["mse"],
                **r["training"]["gradients"],
            }
            for r in calibration
        ]
        h["refit"] = [{"epoch": r["epoch"], "MSE": r["mse"], **r["gradients"]} for r in refit]
        h["selected_epoch"] = result["selector"]["selected"]
        h["loss_concentration"] = result["refit_train_evaluation"]["top_session_loss_share"]
        if architecture == "MC1":
            h["gate"] = result["development"]["gate"]
            h["gate_by_standardized_U5_sign"] = result["development"][
                "gate_by_standardized_U5_sign"
            ]
            h["slice_qualification"] = (
                "Endpoint standardized U5 sign, computed only from inputs. "
                "Descriptive state slice; no learned regime or causal effect claim."
            )
            endpoints = np.asarray(
                [float(view.market[indices[-1], 4]) for _, indices in view.market_indices]
            )
            h["slice_support_origins"] = {
                str(sign): int(np.sum((endpoints >= 0) == bool(sign))) for sign in (0, 1)
            }
        if architecture == "E5":
            train_view = authority.view("inner")
            batch = train_view.batch((0,))
            z = batch.inputs[0, 0].clone()
            changed_stock = z[:, :, :16].clone()
            changed_stock[1, :, 0] += 1.0
            peer = torch.tensor(peer_summaries(changed_stock.numpy()), dtype=torch.float32)
            altered = z.clone()
            altered[:, :, 21:] = peer
            with torch.inference_mode():
                # Direct model forward accepts a five-stock sequence tensor.
                before = model(z)
                after = model(altered)
            h["peer_perturbation"] = {
                "source": "First permissible inner-training origin; no held-out tuning",
                "changed": (
                    "Counterfactual peer1 scaled M1 +1; "
                    "only recomputed peer-summary channels supplied to model"
                ),
                "target0_peer_mean_change": (peer[0, :, 0] - z[0, :, 21]).tolist(),
                "max_abs_score_change": float(torch.max(torch.abs(after - before))),
                "original_21_channel_prefix_equal": bool(
                    torch.equal(z[:, :, :21], altered[:, :, :21])
                ),
                "interpretation": "Input sensitivity only; no causal peer effect or ablation fit",
            }
        health[architecture] = h
        verification[architecture] = {
            "exact_WF1_scores_and_targets": True,
            "checkpoint": result["final_checkpoint"],
            "selected_checkpoint": result["selected_checkpoint"],
            "fresh_identical_seeded_initial_hashes": result["initial_hashes"],
            "fresh_optimizer_state_empty": result["fresh_optimizer_state_empty"],
        }
        runtimes[architecture] = read(folder / "training_actual_runtime.json")
        text = (
            f"# {architecture} training health\n\n{GRADE}. Candidate only.\n\n"
            f"G6: {h['status']}; warnings by pass: {h['warning_epochs']}; "
            f"nonfinite gradients: {h['nonfinite_gradient_count']}. "
            f"Selected epoch {h['selected_epoch']}; a fresh model and empty optimizer "
            "refitted exactly that many epochs.\n\n"
        )
        text += (
            "| Pass | Epoch | MSE | Validation MSE | Clip fraction | Max preclip norm |\n"
            "|---|---:|---:|---:|---:|---:|\n"
        )
        for phase in ("calibration", "refit"):
            for r in h[phase]:
                text += (
                    f"| {phase} | {r['epoch']} | {r.get('train_MSE', r.get('MSE')):.7f} | "
                    f"{r.get('validation_MSE', '—')} | {r['clipped_fraction']:.3f} | "
                    f"{r['max']:.5g} |\n"
                )
        text += (
            "\nFull telemetry, curve and loss concentration: ../training_health.json. "
            "No rescue, extra fit, significance or trading claim.\n"
        )
        (folder / "training_health.md").write_text(text)
    ridge = read(out / "RIDGE_MARKET_147/result.json")
    if [tuple(k) for k in ridge["origin_keys"]] != keys:
        raise ValueError("MARKET_RIDGE_WF1_KEY_MISMATCH")
    scores["RIDGE_MARKET_147"] = np.asarray(ridge["scores"])
    metrics = {name: summarize(stock, value) for name, value in scores.items()}
    rows, daily_rows, origin_rows, month_rows = [], [], [], []
    for name in ("TM0", "MC0", "MC1", "E5", "ZERO", "M1", "RIDGE_OWN_112", "RIDGE_MARKET_147"):
        m = metrics[name]
        score = scores[name]
        fit = (
            runtimes[name]["neural_fitting_seconds"]
            if name in runtimes
            else (
                read(tm0_result_path.parent / "training_actual_runtime.json")[
                    "neural_fitting_seconds"
                ]
                if name == "TM0"
                else None
            )
        )
        rows.append(
            {
                "model": name,
                "scope": "COMPLETED_WF1_DESCRIPTIVE",
                "MSE": m["MSE"],
                "daily_Rank_IC": m["daily_Rank_IC"],
                "defined_only_daily_IC": m["defined_only_daily_Rank_IC"],
                "origin_1_IC": m["by_origin"]["1"]["IC"],
                "origin_2_IC": m["by_origin"]["2"]["IC"],
                "origins": m["origins"],
                "sessions": m["sessions"],
                "score_std": m["score_std"],
                "mean_cross_sectional_score_std": float(np.std(score, axis=1).mean()),
                "constant_share": m["constant_forecast_origins"] / 232,
                "tied_share": m["tied_score_origins"] / 232,
                "MSE_minus_ZERO": m["MSE"] - metrics["ZERO"]["MSE"],
                "beats_ZERO_MSE": m["MSE"] < metrics["ZERO"]["MSE"],
                "neural_fit_seconds": fit,
                "evidence_grade": GRADE,
            }
        )
        daily_rows.extend({"model": name, **r, "evidence_grade": GRADE} for r in m["daily"])
        origin_rows.extend(
            {"model": name, "origin": origin, **r, "evidence_grade": GRADE}
            for origin, r in m["by_origin"].items()
        )
        month_rows.extend(
            {"model": name, "month": month, **r, "evidence_grade": GRADE}
            for month, r in m["monthly"].items()
        )
    differences = []
    paired_daily = []
    for a, b in (("MC0", "TM0"), ("MC1", "MC0"), ("E5", "MC0")):
        for left, right in zip(metrics[a]["daily"], metrics[b]["daily"]):
            if left["session"] != right["session"]:
                raise ValueError("PAIRED_DAILY_KEY_MISMATCH")
            paired_daily.append(
                {
                    "contrast": f"{a}-{b}",
                    "session": left["session"],
                    "delta_MSE": left["MSE"] - right["MSE"],
                    "delta_IC": left["IC"] - right["IC"],
                    "evidence_grade": GRADE,
                }
            )
        subset = [r for r in paired_daily if r["contrast"] == f"{a}-{b}"]
        differences.append(
            {
                "contrast": f"{a}-{b}",
                "days": len(subset),
                "mean_delta_MSE": float(np.mean([r["delta_MSE"] for r in subset])),
                "mean_delta_IC": float(np.mean([r["delta_IC"] for r in subset])),
                "evidence_grade": GRADE,
            }
        )
    table(out / "matched_wf1_model_comparison.csv", rows)
    table(out / "matched_wf1_daily.csv", daily_rows)
    table(out / "matched_wf1_by_origin.csv", origin_rows)
    table(out / "matched_wf1_monthly.csv", month_rows)
    table(out / "paired_daily_deltas.csv", paired_daily)
    table(out / "paired_delta_summary.csv", differences)
    paired_months = []
    for contrast in sorted({r["contrast"] for r in paired_daily}):
        for month in sorted({r["session"][:7] for r in paired_daily}):
            selected = [
                r
                for r in paired_daily
                if r["contrast"] == contrast and r["session"].startswith(month)
            ]
            paired_months.append(
                {
                    "contrast": contrast,
                    "month": month,
                    "sessions": len(selected),
                    "mean_delta_MSE": float(np.mean([r["delta_MSE"] for r in selected])),
                    "mean_delta_IC": float(np.mean([r["delta_IC"] for r in selected])),
                    "evidence_grade": GRADE,
                }
            )
    table(out / "paired_monthly_deltas.csv", paired_months)
    write_json(out / "training_health.json", health)
    write_json(out / "checkpoint_inference_verification.json", verification)
    write_json(out / "matched_metrics.json", metrics)
    md = (
        f"# Matched WF1 screening\n\n{GRADE}. Retrospective universe/representation, "
        "idealized clock, researcher-attested rights and hourly-close proxy; "
        "SPY is an ETF state proxy. No observed-publication, executable-fill, "
        "course-substitution or production claim.\n\nAll eight rows use exactly "
        "232 origins / 116 sessions / 1,160 stock predictions, same five targets "
        "and ordered names. No additional attrition.\n\n"
        "| Model | MSE | Daily Rank IC | Neural fit seconds | Beats ZERO MSE |\n"
        "|---|---:|---:|---:|---|\n"
    )
    for r in rows:
        seconds = r["neural_fit_seconds"] if r["neural_fit_seconds"] is not None else "n/a"
        md += (
            f"| {r['model']} | {r['MSE']:.7f} | {r['daily_Rank_IC']:.7f} | "
            f"{seconds} | {r['beats_ZERO_MSE']} |\n"
        )
    md += (
        "\nDaily IC uses the existing midrank Spearman implementation: average two origins "
        "within session, then equal sessions. Constant forecasts receive project IC=0; "
        "defined-only ZERO IC is unavailable. MSE uses equal stock → origin → session "
        "weighting. M1 is an unfitted ranking score in different units; its MSE is diagnostic. "
        "Ridge uses seven lag snapshots, LSTM all 48 steps, so information is comparable "
        "but not identical. Pairwise ranking accuracy was not already implemented "
        "and was not added.\n\n"
    )
    for d in differences:
        md += (
            f"{d['contrast']}: mean paired daily ΔIC={d['mean_delta_IC']:.7f}, "
            f"ΔMSE={d['mean_delta_MSE']:.7f}, n={d['days']}.\n\n"
        )
    md += (
        "Existing TM0 final weights were safely reloaded and reproduced the frozen "
        "Package006 snapshot exactly; no TM0 or own-ridge refit. Each new final checkpoint "
        "reproduced its stored WF1 scores exactly. Monthly/origin/daily tables retain all "
        "observations. These are one-seed/one-development-fold descriptive contrasts; "
        "no significance, bootstrap, economic replay or causal increment claim. "
        "Frozen models were not modified after WF1.\n"
    )
    (out / "matched_wf1_model_comparison.md").write_text(md)
    print(json.dumps({"status": "READ_ONLY_MATCHED_REVIEW_COMPLETE", "rows": rows, "new_fits": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
