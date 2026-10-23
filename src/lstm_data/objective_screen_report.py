"""Generate objective-specific human review reports from verified saved diagnostics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .config import write_json
from .hf1m_ft16_source import ref
from .objective_screen_loss import ARMS, RUNS


def markdown(frame: pd.DataFrame) -> str:
    def cell(value: object) -> str:
        if isinstance(value, float):
            return f"{value:.8g}" if np.isfinite(value) else "undefined"
        return str(value).replace("|", "/").replace("\n", " ")

    return (
        "| "
        + " | ".join(map(str, frame.columns))
        + " |\n|"
        + "|".join(["---"] * len(frame.columns))
        + "|\n"
        + "\n".join(
            "| " + " | ".join(cell(v) for v in row) + " |"
            for row in frame.itertuples(index=False, name=None)
        )
        + "\n"
    )


def reports(plan_path: Path, out: Path) -> None:
    receipt = json.loads((out / "stage7_computation_receipt.json").read_text())
    assert receipt["status"] == "COMPUTATION_VERIFIED_PENDING_REPORT_REVIEW"
    scores = pd.read_json(out / "scoreboard.json")
    cohorts = pd.read_parquet(out / "cohort_metrics.parquet")
    differences = pd.read_csv(out / "paired_daily_differences.csv")
    optimization = pd.read_csv(out / "optimization.csv")
    results = {
        arm: json.loads((plan_path.parent / run / "run_result.json").read_text())
        for arm, run in zip(ARMS, RUNS, strict=True)
    }
    resources = pd.DataFrame(
        [
            dict(
                arm=arm,
                calibration_epochs=r["calibration_epochs"],
                selected_epoch=r["refit_epochs"],
                raw_best_epoch=r["selector"]["raw_epoch"],
                stop=r["selector"]["status"],
                parameters=r["parameters"],
                seconds=r["elapsed_seconds"],
                peak_RSS_bytes=r["peak_rss_bytes"],
                artifact_bytes=r["run_artifact_bytes"],
            )
            for arm, r in results.items()
        ]
    )
    resources.to_csv(out / "resources.csv", index=False)
    comparison = [
        "# P022 collective model comparison\n\n"
        "Four independent seed42 arms completed under the exact repaired approval. "
        "Ledger41/200 includes preserved failed start37 and successful starts38–41. "
        "No seed123 improvement replication, combination, trading result or "
        "protected2026 access.\n\n"
        "The following are checkpoint metrics on exactly matched populations. Inner validation "
        "selected epochs; refit is in-sample. Development has183origins /3660rows /109sessions "
        "and remains exploratory. Roles overlap and must not be pooled as "
        "independent OOS evidence.\n"
    ]
    for role in ("development", "inner_validation", "refit", "inner_train"):
        frame = scores.loc[scores.role.eq(role)]
        reg = frame.loc[frame.model.isin(["H2", "W1", "R1", "T2/42", "T2/123", "ZERO"])]
        comparison += [
            f"\n## {role}: regression in original TG20 units\n\n",
            markdown(
                reg[
                    [
                        "model",
                        "mse",
                        "mae",
                        "rmse",
                        "daily_ic",
                        "sign_hit",
                        "prediction_sd",
                        "actual_sd",
                        "top4_recall",
                        "bottom4_recall",
                        "excess_mse",
                        "prediction_energy",
                        "twice_y_pred",
                    ]
                ]
            ),
            "\nE[p²]−2E[yp] equals MSE(model)−MSE(ZERO) under identical equal-session weights. "
            "Positive excess is worse than ZERO. ZERO rank/recall are "
            "undefined because all scores tie.\n",
            f"\n## {role}: E1 classification\n\n",
            markdown(
                frame.loc[
                    frame.model.str.startswith("E1"),
                    [
                        "model",
                        "normalized_class_weighted_CE",
                        "unweighted_CE",
                        "NEG_AP",
                        "POS_AP",
                        "ANY_AP",
                        "NEG_precision",
                        "POS_precision",
                        "NEG_recall",
                        "POS_recall",
                        "NEG_FPR",
                        "POS_FPR",
                        "NEG_recall_at4",
                        "POS_recall_at4",
                        "macro_F1",
                        "ordinal_daily_IC",
                    ],
                ]
            ),
        ]
        comparison += [
            "\nClass order NEG/NORMAL/POS. AP uses tie-grouped noninterpolated precision–recall "
            "area; chance AP is each role's observed event prevalence, not "
            "necessarily the fitting prior. "
            "The constant prior uses fitting-only prevalences. Undefined precision means no calls. "
            "Always-NORMAL log loss uses float64 tiny only to represent zero "
            "assigned probability.\n",
            markdown(
                frame.loc[
                    frame.model.str.startswith("E1"),
                    [
                        "model",
                        "observed_prevalence",
                        "probability_mean",
                        "probability_sd",
                        "Brier_by_class",
                        "NEG_ECE10",
                        "POS_ECE10",
                        "confusion_weighted",
                        "argmax_counts",
                    ],
                ]
            ),
        ]
    dev = scores.loc[scores.role.eq("development")].set_index("model")

    def number(model: str, metric: str) -> float:
        values = dev.loc[[model], [metric]].to_numpy(dtype=float)
        if values.shape != (1, 1):
            raise ValueError("P022_ONE_COMPARISON_VALUE")
        return float(values[0, 0])

    comparison += ["\n## Development interpretation\n\n"]
    for arm in ("H2", "W1", "R1"):
        dm = number(arm, "mse") - number("T2/42", "mse")
        di = number(arm, "daily_ic") - number("T2/42", "daily_ic")
        comparison += [
            f"{arm}: MSE difference versus T2/42 {dm:+.8f}; daily IC difference {di:+.8f}. "
            "Lower MSE and higher IC are favorable; a one-seed difference is not replication.\n\n"
        ]
    comparison += [
        f"E1 development ANY AP {number('E1', 'ANY_AP'):.8f}, "
        f"constant-prior ANY AP {number('E1_TRAIN_PRIOR', 'ANY_AP'):.8f}; "
        f"weighted CE {number('E1', 'normalized_class_weighted_CE'):.8f} versus "
        f"{number('E1_TRAIN_PRIOR', 'normalized_class_weighted_CE'):.8f}. "
        "These are classification outcomes; no E1 return MSE is defined.\n\n",
        "## Paired uncertainty\n\n400 fixed-seed22042 whole-calendar-month bootstrap replicates; "
        "two-month-block sensitivity. Each daily difference preserves "
        "dependent stocks and origins. "
        "Only a few development month blocks exist; intervals are exploratory, "
        "not an alpha/significance claim.\n\n",
        markdown(differences.loc[differences.role.eq("development")]),
        "\n## Optimization and resources\n\n",
        markdown(resources),
        "\nFull phase/epoch objective, output, gradient, clipping "
        "numerator/denominator and step records "
        "are in optimization.csv and the immutable run epoch receipts. "
        "Training is online/pre-update "
        "dropoutON; validation and final checkpoint attribution use dropoutOFF. Their gaps include "
        "this computational distinction. Lower Huber or CE numbers cannot be compared with zMSE. "
        "Original P021 C0/42 missing per-batch calibration telemetry remains "
        "missing; none was invented.\n\n",
        "## Limitations and next decision\n\nRetrospective fixed survivors, "
        "conditional source rights/publication "
        "and action-vintage assumptions, volume/fallback/proxy limitations "
        "remain. quality_sensitivity.json "
        "reports complete-origin strata with and without "
        "proxy/poor-volume/fallback flags; these are "
        "retrospective diagnostics, not new selection rules. No "
        "permutation/null or walk-forward retuning "
        "was performed. Larger forecast amplitudes or lower incomparable "
        "objectives do not establish signal. "
        "Do not promote automatically. Consider at most one or two separately "
        "authorized seed123 replications "
        "only after reviewing both regression accuracy/rank and event "
        "calibration. The original10+3 backlog "
        "is preserved; its authoritative list/path remains unresolved and no "
        "thirteen-item list is fabricated.\n",
    ]
    (out / "P022_COLLECTIVE_MODEL_COMPARISON.md").write_text("".join(comparison))
    tails = [
        "# P022 actual-objective extreme-loss attribution\n\n"
        "Final saved refit checkpoints, dropoutOFF,104200rows /5210origins /2980sessions. "
        "These are in-sample accounting diagnostics, distinct from historical "
        "online dropoutON loss. "
        "H2 uses2×Huber(delta1) on z; W1 uses session-normalized doubled-tail zMSE; "
        "E1 uses session-normalized class-weighted CE; R1 uses zMSE+0.5mean "
        "all-valid-pair softplus.\n\n"
        "All population Parquets preserve raw coefficients, normalized weights, raw point loss, "
        "point/pair/total contributions, predictions/logits, target "
        "components, source quality, role and checkpoint hash. "
        "Weighted contributions sum to the actual equal-session objective. "
        "Equivalent row loss divides "
        "by ordinary session/origin/stock mass; its unweighted share is a "
        "separate accounting convention.\n\n"
        "Rank top1/5 uses floor(pct×N), stable origin/canonical-stock ties. "
        "MAD bottom1/5 ranks unique "
        "origins before expanding to20stocks. All after-asinh ranked "
        "memberships exactly match raw |TG20|. "
        "Magnitude ranges use ≥.99/.95 of the fitting maximum, with separate side-specific maxima; "
        "validation/development reuse fitting thresholds. A5% range is not a5%-of-rows percentile. "
        "All thresholds, sign groups, complements, intersections and zero "
        "counts are saved per role.\n"
    ]
    keep = [
        "ALL",
        "TARGET_RANK_TOP1",
        "TARGET_RANK_TOP5",
        "NUMERATOR_RANK_TOP1",
        "NUMERATOR_RANK_TOP5",
        "MAD_BOTTOM1",
        "MAD_BOTTOM5",
        "BOTH_5",
        "NUM_ONLY_5",
        "MAD_ONLY_5",
        "NEITHER_5",
        "RANGE_ABS_0.99",
        "RANGE_ABS_0.95",
        "RANGE_POS_0.99",
        "RANGE_NEG_0.99",
    ]
    for arm in ARMS:
        table = cohorts.loc[
            cohorts.arm.eq(arm) & cohorts.role.eq("refit") & cohorts.cohort.isin(keep)
        ]
        tails += [
            f"\n## {arm}\n\n",
            markdown(
                table[
                    [
                        "cohort",
                        "threshold",
                        "rows",
                        "row_pct",
                        "origins",
                        "sessions",
                        "ordinary_weight_mass",
                        "objective_weight_mass",
                        "weighted_loss_share_pct",
                        "unweighted_loss_share_pct",
                        "pointwise",
                        "pairwise",
                    ]
                ]
            ),
            f"\n[Exact case annex](P022_{arm}_EXACT_CASE_ANNEX.md).\n",
        ]
        case_root = out / arm / "refit"
        cases = pd.read_parquet(case_root / "cases.parquet")
        candles = pd.read_parquet(case_root / "case_candles.parquet")
        features = pd.read_parquet(case_root / "case_features.parquet")
        returns = pd.read_parquet(case_root / "case_20_returns.parquet")
        annex = [
            f"# P022 {arm} exact actual-objective cases\n\n"
            "Five highest-contributing examples each for AAPL/AMZN/TSLA/SBUX, plus available "
            "E1 misses/false positives or R1 misordered-pair endpoints. Every case has48scheduled "
            "input hours and4future outcome hours. Future candles are shown for diagnosis only. "
            "Raw/source rows were not repaired or filled here. Native/scaled full48×16values "
            "and quality flags are in the case Parquets and dashboard.\n"
        ]
        for row in cases.itertuples():
            annex += [
                f"\n## Case{row.case_id}: {row.ticker}, {row.origin_id}\n\n",
                markdown(
                    cases.loc[cases.case_id.eq(row.case_id)]
                    .T.reset_index()
                    .rename(
                        columns={
                            "index": "field",
                            cases.loc[cases.case_id.eq(row.case_id)].index[0]: "value",
                        }
                    )
                ),
                "\nExact52candles (unknown extrema remain missing):\n\n",
            ]
            c = candles.loc[candles.case_id.eq(row.case_id)]
            cols = [
                k
                for k in [
                    "step",
                    "hour_end_utc",
                    "open",
                    "high",
                    "low",
                    "close",
                    "observed_volume",
                    "genuine_close",
                    "proxy_count",
                    "assumed_zero_missing_count",
                    "volume_for_feature",
                    "context",
                ]
                if k in c
            ]
            annex += [
                markdown(c[cols]),
                "\nAll20endpoint returns:\n\n",
                markdown(returns.loc[returns.case_id.eq(row.case_id)]),
                "\nEntry-step16channel native/scaled values (all48steps retained privately):\n\n",
                markdown(
                    features.loc[
                        features.case_id.eq(row.case_id) & features.step.eq(row.entry_step)
                    ]
                ),
            ]
        (out / f"P022_{arm}_EXACT_CASE_ANNEX.md").write_text("".join(annex))
        r = results[arm]
        g = optimization.loc[optimization.arm.eq(arm)]
        (out / f"P022_{arm}_TRAINING_AND_CHECKPOINT.md").write_text(
            f"# P022 {arm} training and checkpoint\n\nRun `{r['run_id']}`,seed42. "
            f"Calibration{r['calibration_epochs']}epochs; qualified selection{r['refit_epochs']}; "
            f"raw best{r['selector']['raw_epoch']}; {r['selector']['status']}. Fresh refit "
            f"{r['refit_epochs']}epochs. Checkpoints SHA256: calibration "
            f"`{r['calibration']['sha256']}`, "
            f"refit `{r['refit']['sha256']}`. No resumed trained weights or "
            "development selection.\n\n"
            + markdown(
                g[
                    [
                        "phase",
                        "kind",
                        "epoch",
                        "optimized_objective",
                        "original_mse",
                        "optimizer_steps",
                        "preclip_norm_p50",
                        "preclip_norm_p90",
                        "preclip_norm_p99",
                        "postclip_norm_max",
                        "clipped_count",
                        "clipped_denominator",
                        "clipped_fraction",
                        "nonfinite_count",
                        "learning_rate",
                    ]
                ]
            )
            + "\nSee the collective report for matched forecasting/event "
            "results. Objective units differ "
            "across arms. Final-checkpoint attribution is separate from these "
            "online training losses.\n"
        )
    if (out / "R1/refit/pair_tail_breakdown.csv").exists():
        tails += [
            "\n## R1 pair allocation\n\nHalf of each correctly normalized pair contribution is "
            "allocated to each endpoint. NumPy independent allocations reconcile with Torch. "
            "This is loss accounting, not causal gradient attribution. Genuine "
            "target ties are skipped.\n\n",
            markdown(pd.read_csv(out / "R1/refit/pair_tail_breakdown.csv")),
        ]
    tails += [
        "\nP021B T2/42 refit top-|y|1/5% shares were7.16337%/24.37726% of its zMSE. "
        "They are contextual concentration references; Huber/CE/rank losses have different units. "
        "Original TG20 MSE and ZERO decomposition are compared only in the "
        "collective regression table. "
        "Overlapping cohorts must not be summed; the BOTH/NUM_ONLY/MAD_ONLY/NEITHER partition "
        "reconciles exactly. RMSE is non-additive.\n"
    ]
    (out / "P022_OBJECTIVE_SPACE_EXTREME_LOSS_ATTRIBUTION.md").write_text("".join(tails))
    write_json(
        out / "report_generation_receipt.json",
        dict(status="REPORTS_WRITTEN", reports=[ref(f) for f in out.glob("*.md")]),
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    reports(a.plan, a.out)
