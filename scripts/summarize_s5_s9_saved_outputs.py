"""Readable S5/S9 closeout from completed saved outputs; no fitting or source I/O."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from lstm_data.hf20_ranking import daily_ic
from lstm_data.hf20_ranking_continue_report import markdown
from lstm_data.hf20_s5s9 import RUNS
from lstm_data.hf20_s5s9_metrics import metrics
from lstm_data.hf20_s5s9_run import ensure


def summarize(out: Path) -> None:
    """Reconcile tails/gradients and explain annual matched-control results."""
    ensure(out)
    verification = json.loads((out / "S5_S9_NUMERICAL_VERIFICATION.json").read_text())
    assert verification["neural_completed"] == verification["neural_starts"] == 16
    assert verification["control_attempts"] == 64 and verification["prefix_recipes"] == 32
    tails, examples, training, volatility, median_rank, paired_strata = [], [], [], [], [], []
    effects = pd.read_csv(out / "S5_S9_PAIRED_OOS_UNCERTAINTY.csv")
    for run in RUNS:
        dest = out / run
        binding = json.loads((dest / "calibration_binding.json").read_text())
        refit = json.loads((dest / "refit_binding.json").read_text())
        cfg = json.loads((dest / "configuration.json").read_text())
        batches = pd.concat(
            [pd.read_csv(p) for p in sorted(dest.glob("*_batches.csv"))], ignore_index=True
        )
        gradients = pd.concat(
            [pd.read_csv(p) for p in sorted(dest.glob("*_gradients.csv"))], ignore_index=True
        )
        assert np.isfinite(gradients.norm).all() and gradients.nonzero.sum() > 0
        assert np.isfinite(batches.postclip).all() and batches.postclip.max() <= 1.00001
        assert (batches.update_norm > 0).all() and refit["reload_max_error"] == 0
        selector = binding["selector"]
        training.append(
            dict(
                run=run,
                calibration_epochs=len(list(dest.glob("calibration_???.json"))),
                selected_epoch=binding["selected"],
                raw_best_epoch=selector["raw_epoch"],
                calibration_updates=binding["optimizer_updates"],
                refit_epochs=refit["selected"],
                refit_updates=refit["optimizer_updates"],
                positive_update_batches=len(batches),
                gradient_records=len(gradients),
                nonzero_gradient_records=int((gradients.nonzero > 0).sum()),
                clipping_fraction=float((batches.preclip > 1).mean()),
                max_postclip=float(batches.postclip.max()),
                reload_error=0,
            )
        )
        for role in ("inner_train", "inner_validation", "refit", "oos"):
            f = pd.read_parquet(dest / f"{role}_scores.parquet")
            c = pd.read_csv(dest / f"{role}_cohorts.csv").set_index("cohort")
            m = json.loads((dest / f"{role}_metrics.json").read_text())
            np.testing.assert_allclose(
                f.TG20, f.numerator / (f.mad + f.epsilon), atol=1e-12, rtol=1e-11
            )
            np.testing.assert_allclose(
                np.sum(f.weight * f.actual_loss), m["optimized_loss"], atol=1e-12, rtol=1e-11
            )
            np.testing.assert_allclose(
                c.loc[["TARGET_TOP1", "TARGET_TOP1_COMPLEMENT"], "actual_loss_share"]
                .to_numpy(dtype=np.float64)
                .sum(),
                1,
                atol=1e-12,
                rtol=1e-11,
            )
            assert m["arm"] == cfg["arm"]
            record = dict(m, run=run, role=role)
            if cfg["arm"] == "MAG":
                record["mean_forecast_A"] = float(np.average(f.prediction_A, weights=f.weight))
                record["mean_observed_A"] = float(np.average(abs(f.return_4h), weights=f.weight))
            for cohort in (
                "TRAIN_TASK95",
                "TRAIN_TASK99",
                "POS",
                "NEG",
                "NUM_ONLY",
                "MAD_ONLY",
                "BOTH",
                "NEITHER",
                "FLOOR",
                "TARGET_TOP1",
                "ERROR_TOP1",
                "ERROR_TOP5",
            ):
                for field in ("weight_mass", "actual_loss_share"):
                    record[f"{cohort}_{field}"] = c.loc[cohort, field]
            tails.append(record)
            if role == "oos" and cfg["arm"] != "META-T2R":
                for reference in ("GLOBAL", "STOCK", "VOL"):
                    g = pd.read_parquet(dest / f"oos_{reference}_control_scores.parquet")
                    np.testing.assert_array_equal(
                        f[["origin_id", "ticker"]], g[["origin_id", "ticker"]]
                    )
                    paired = f.assign(difference=f.actual_loss - g.actual_loss)
                    original = effects[
                        effects.arm.eq(cfg["arm"])
                        & effects.reference.eq(reference)
                        & effects.metric.eq("proper_loss")
                        & effects.year.eq(str(int(f.year.iloc[0])))
                    ]
                    assert len(original) == 1
                    np.testing.assert_allclose(
                        np.average(paired.difference, weights=paired.weight),
                        original["mean"].iloc[0],
                        atol=1e-12,
                        rtol=1e-11,
                    )
                    for field in (
                        "ticker",
                        "month",
                        "slot",
                        "category",
                        "quality",
                        "fallback",
                        "age_band",
                    ):
                        for group, sample in paired.groupby(field):
                            paired_strata.append(
                                dict(
                                    run=run,
                                    arm=cfg["arm"],
                                    year=int(f.year.iloc[0]),
                                    reference=reference,
                                    field=field,
                                    group=str(group),
                                    rows=len(sample),
                                    origins=sample.origin_id.nunique(),
                                    sessions=sample.session_date_et.nunique(),
                                    role_weight_mass=float(sample.weight.sum()),
                                    proper_loss_difference=float(
                                        np.average(sample.difference, weights=sample.weight)
                                    ),
                                )
                            )
            if cfg["arm"] == "QUANTILE":
                median_rank.append(
                    dict(
                        run=run,
                        role=role,
                        year=int(f.year.iloc[0]),
                        median_daily_ic=daily_ic(
                            f.return_4h.to_numpy().reshape(-1, 20),
                            f.quantiles_y_50.to_numpy().reshape(-1, 20),
                            f.session_date_et.to_numpy()[::20],
                        ),
                    )
                )
            if cfg["arm"] != "META-T2R":
                phase = "inner" if role.startswith("inner") else "refit"
                event = out / f"HF20-S9-F{int(f.year.iloc[0]) % 100}-H4-EVENT-S42"
                control = event / f"{phase}_VOL_control.json"
                cuts = json.loads(control.read_text())["cuts"]
                # Reuse already-fitted EVENT prefix cuts; no new threshold fit.
                f["source_vol_bin"] = np.digitize(np.log(f.sigma_proxy), cuts)
                for group, sample in f.groupby("source_vol_bin"):
                    value = dict(metrics(sample, cfg["arm"]))
                    value.update(run=run, role=role, volatility_bin=group, cut_source=str(control))
                    volatility.append(value)
            kinds = {
                "LARGEST_OPTIMIZED_ROW_LOSS": f.sort_values(
                    ["actual_loss", "origin_id", "ticker"],
                    ascending=[False, True, True],
                    kind="stable",
                )
            }
            if cfg["arm"] == "EVENT":
                kinds["FALSE_ALARM_AT_FROZEN_HALF"] = f[
                    f.event_class.eq(1) & f.p_ANY.ge(0.5)
                ].sort_values(["p_ANY", "origin_id", "ticker"], ascending=[False, True, True])
                kinds["MISSED_TAIL_AT_FROZEN_HALF"] = f[
                    f.event_class.ne(1) & f.p_ANY.lt(0.5)
                ].sort_values(["p_ANY", "origin_id", "ticker"])
            if cfg["arm"] == "QUANTILE":
                for label, col, sign in (
                    ("LOWER_QUANTILE_MISS", "quantiles_y_05", -1),
                    ("UPPER_QUANTILE_MISS", "quantiles_y_95", 1),
                ):
                    miss = f.assign(miss_size=sign * (f.TG20 - f[col]))
                    kinds[label] = miss[miss.miss_size > 0].sort_values(
                        ["miss_size", "origin_id", "ticker"], ascending=[False, True, True]
                    )
            for kind, cases in kinds.items():
                cols = [
                    k
                    for k in (
                        "origin_id",
                        "ticker",
                        "slot",
                        "category",
                        "exit_end_utc",
                        "return_4h",
                        "TG20",
                        "Z",
                        "numerator",
                        "mad",
                        "epsilon",
                        "weight",
                        "actual_loss",
                        "prediction_m",
                        "prediction_A",
                        "event_class",
                        "p_ANY",
                        "quantiles_y_05",
                        "quantiles_y_50",
                        "quantiles_y_95",
                        "quality",
                        "fallback",
                    )
                    if k in cases
                ]
                for row in cases.head(3)[cols].to_dict("records"):
                    example = dict(row)
                    example.update(run=run, role=role, case_kind=kind)
                    examples.append(example)
    tail = pd.DataFrame(tails)
    trace = pd.DataFrame(training)
    tail.to_csv(out / "S5_S9_EXTREME_LOSS_SUMMARY.csv", index=False)
    trace.to_csv(out / "S5_S9_TRAINING_INTEGRITY_SUMMARY.csv", index=False)
    pd.DataFrame(volatility).to_csv(out / "S5_S9_VOLATILITY_CONDITIONAL_METRICS.csv", index=False)
    pd.DataFrame(median_rank).to_csv(out / "S5_S9_QUANTILE_MEDIAN_RANK_DIAGNOSTIC.csv", index=False)
    pd.DataFrame(paired_strata).to_csv(
        out / "S5_S9_OOS_PAIRED_SOURCE_STOCK_STRATA.csv", index=False
    )
    pd.DataFrame(examples).to_csv(out / "S5_S9_FIXED_RULE_DIAGNOSTIC_EXAMPLES.csv", index=False)
    body = "# Detailed training and extreme-value diagnostics\n\n"
    body += (
        "All64 role bundles reconcile TG20=NUM/(MAD+epsilon), actual weighted optimized loss, "
        "and target-top1/complement shares with atol1e-12/rtol1e-11. Every recorded optimizer "
        "batch changed weights; checkpoint reload error is0. No new fit or source read.\n\n"
        "## Training, validation and fresh refit\n\n"
    )
    body += markdown(trace) + "\n\n"
    body += (
        "Online dropout-ON losses are training-path statistics, whereas epoch JSON records "
        "dropout-OFF full-prefix/validation losses for a fixed checkpoint. Raw-best and "
        "qualifying-selected epochs differ by the frozen improvement rule. Refit starts "
        "from the recorded same-seed initial state. See S5_S9_TRAINING_TRACE.csv and each "
        "run's immutable epoch/batch/gradient/checkpoint files in the complete index. "
        "Inner and refit recipes/scales differ; their numeric loss levels are not a "
        "controlled comparison.\n\n## Actual optimized tail loss\n\n"
        "S5: asinh-TG20 MSE. MAG: log1p(raw-|R|/scale) MSE. EVENT: natural three-class CE, "
        "not ANY Brier or TG20 MSE. QUANTILE: mean asinh-unit pinball. TRAIN_TASK95/99 "
        "use phase-training thresholds (raw|R| for MAG; |TG20| for the others). "
        "TARGET_TOP1 and ERROR_TOP1 are retrospective within-role diagnostic cohorts, "
        "not fitting thresholds. Their complements remain included.\n\n"
        "NUM_ONLY/MAD_ONLY/BOTH/NEITHER use the frozen phase NUM95 and MAD05 thresholds. "
        "They are an attribution partition, not a causal explanation of predictability. "
        "FLOOR identifies epsilon-dominated denominators. POS/NEG are TG20 signs and can "
        "overlap the other cohort families. Never add overlapping shares.\n\n"
    )
    cols = [
        "run",
        "optimized_loss",
        "TRAIN_TASK95_actual_loss_share",
        "TRAIN_TASK99_actual_loss_share",
        "NUM_ONLY_actual_loss_share",
        "MAD_ONLY_actual_loss_share",
        "BOTH_actual_loss_share",
        "FLOOR_weight_mass",
        "ERROR_TOP1_actual_loss_share",
    ]
    body += markdown(tail[tail.role.eq("oos")][cols]) + "\n\n"
    body += (
        "[All64 role/tail summaries](S5_S9_EXTREME_LOSS_SUMMARY.csv) · "
        "[Fixed-rule exact examples](S5_S9_FIXED_RULE_DIAGNOSTIC_EXAMPLES.csv) · "
        "[Full file index](S5_S9_DIAGNOSTIC_INDEX.md).\n\n"
        "Examples choose the largest3 actual optimized row losses per run/role, ties "
        "by origin UTC/ticker. EVENT additionally selects highest-probability false alarms "
        "and lowest-probability missed tails at the existing frozen0.5 reporting threshold. "
        "An empty false-alarm set contributes no invented example; precision is undefined "
        "when there are no predicted positives. These retrospective examples never alter "
        "eligibility, training or primary metrics. Source/fallback/age/stock/month/clock "
        "strata and all individual observations remain in each saved role bundle.\n"
        "Quantile miss cases select the largest lower/upper original-TG20 interval miss, "
        "with UTC/ticker ties. Volatility conditional tables reuse the already fitted "
        "EVENT inner/refit log-sigma quartile cuts for the same fold; no new cutoff fit "
        "or sample exclusion occurs. Conditional metrics renormalize existing role "
        "weights within each stratum. The quantile median's cross-sectional daily IC "
        "is secondary and separate from interval width.\n"
    )
    (out / "S5_S9_DETAILED_TRAINING_AND_EXTREME_DIAGNOSTICS.md").write_text(body)
    decision = out / "S5_S9_FINAL_RESEARCH_DECISION.md"
    archive = out / "S5_S9_GENERATED_RESEARCH_TABLES.md"
    if not archive.exists():
        shutil.copyfile(decision, archive)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    summarize(parser.parse_args().out)
