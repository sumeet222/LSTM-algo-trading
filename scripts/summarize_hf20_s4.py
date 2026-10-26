"""Summarize completed S4 saved diagnostics only; no fits or raw-source access."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from lstm_data.hf20_rank_visuals import transitions
from lstm_data.hf20_ranking_continue_report import markdown
from lstm_data.hf20_s4_authority import RUNS


def interval(frame: pd.DataFrame, column: str) -> dict:
    """Fixed-year, whole-month bootstrap; equal session then equal year weights."""
    rng = np.random.default_rng(22042)
    annual, draws = [], []
    for _, year in frame.groupby("year"):
        valid = year.dropna(subset=[column])
        if valid.empty:
            continue
        monthly = valid.groupby(valid.session_date_et.str[:7])[column].agg(["sum", "count"])
        ix = rng.integers(len(monthly), size=(400, len(monthly)))
        draws.append(monthly["sum"].to_numpy()[ix].sum(1) / monthly["count"].to_numpy()[ix].sum(1))
        annual.append(float(valid[column].mean()))
    if len(annual) != 4:
        return dict(mean=None, low=None, high=None, years=len(annual), replicates=400)
    lo, hi = np.quantile(np.mean(draws, axis=0), [0.025, 0.975])
    return dict(mean=float(np.mean(annual)), low=float(lo), high=float(hi), years=4, replicates=400)


def detailed_reports(out: Path) -> None:
    """Expose all saved role, epoch and cohort diagnostics in readable reports."""
    training = [
        "# S4-A detailed training, validation, refit and OOS diagnostics\n",
        "All eight runs; all four roles. Inner validation selects the checkpoint; "
        "inner training/refit are in sample; OOS is retrospective annual evaluation. "
        "Online losses use dropout ON and evolving weights. OFF metrics use the complete "
        "role population at one checkpoint. NR ordinal MSE and T2R asinh MSE have different "
        "units. [Complete file index](DIAGNOSTIC_FILE_INDEX.csv).\n",
    ]
    tails = [
        "# S4-A detailed extreme-value, objective-error and numerator/MAD diagnostics\n",
        "All eight runs and all four roles are retained below. TRAIN_EVENT95/99 thresholds "
        "come from the appropriate training prefix. TARGET_RANK_TOP1/5 describe realized "
        "absolute TG20 tails within the evaluated role; ACTUAL_OBJECTIVE_TOP1/5 separately "
        "rank the optimized row error. These post-outcome cohorts are diagnostic, not "
        "available forecast regimes. Complements and positive/negative subsets remain explicit.\n",
        "Contribution is a population-weighted sum, not a conditional mean. Loss share "
        "divides that contribution by the same run/role ALL objective. NUM_ONLY, MAD_ONLY, "
        "BOTH and NEITHER form a partition; FLOOR can overlap. Subsets from different "
        "families must not be added. NR has no invented return inverse or original-Y MSE. "
        "T2R original-Y diagnostics invert the frozen recipe once. Energy terms below "
        "are in original TG20 squared units, separate from optimized asinh loss. "
        "Subset common/centered decompositions require their cross term. Counts reused "
        "across models are not independent source events.\n",
    ]
    for run in RUNS:
        dest = out / run
        link = f"[{run}]({run}/RUN_DIAGNOSTICS.md)"
        training.append(f"## {link}\n")
        tails.append(f"## {link}\n")
        binding = json.loads((dest / "calibration_binding.json").read_text())
        training.append(
            f"Selected epoch {binding['selected']}; raw-best epoch {binding['raw_best_epoch']}. "
            f"[Checkpoint selection]({run}/calibration_binding.json), "
            f"[fresh refit binding]({run}/refit_binding.json), "
            f"[verified stage gate]({run}/PASS.json).\n"
        )
        metrics, epochs, health = [], [], []
        for role in ("inner_train", "inner_validation", "refit", "oos"):
            metrics.append(json.loads((dest / f"{role}_metrics.json").read_text()))
            cohort = pd.read_csv(dest / f"{role}_cohorts.csv")
            total = float(
                cohort.loc[cohort.cohort.eq("ALL"), "actual_objective_contribution"].iloc[0]
            )
            cohort["actual_loss_share"] = cohort.actual_objective_contribution / total
            partition = cohort.loc[cohort.cohort.isin(["NUM_ONLY", "MAD_ONLY", "BOTH", "NEITHER"])]
            np.testing.assert_allclose(
                partition.actual_objective_contribution.sum(), total, rtol=1e-10, atol=1e-12
            )
            tails.append(
                f"### {role}\n\n[All cohorts]({run}/{role}_cohorts.csv) · "
                f"[energy and numerator/MAD]({run}/{role}_energy_and_objective_cohorts.csv) · "
                f"[exact saved event witnesses]({run}/{role}_paired_cohort_difficulty.csv) · "
                f"[train-only thresholds]({run}/{role}_thresholds.json).\n"
            )
            tails.append(markdown(cohort) + "\n")
            if "-T2R-" in run:
                energy = pd.read_csv(dest / f"{role}_energy_and_objective_cohorts.csv")
                energy = energy.loc[
                    energy.cohort.isin(["ALL", "NUM_ONLY", "MAD_ONLY", "BOTH", "NEITHER"])
                ]
                tails.append(
                    markdown(
                        energy[
                            [
                                "cohort",
                                "original_MSE_contribution",
                                "target_energy",
                                "forecast_energy",
                                "alignment",
                                "common_error",
                                "centered_error",
                                "subset_cross_term",
                            ]
                        ]
                    )
                    + "\n"
                )
        training.append(
            markdown(
                pd.DataFrame(metrics)[
                    [
                        "role",
                        "origins",
                        "sessions",
                        "rows",
                        "daily_ic",
                        "actual_objective",
                        "top4",
                        "bottom4",
                        "pair_concordance",
                        "score_sd",
                        "pair_tie_rate",
                    ]
                ]
            )
            + "\n"
        )
        for phase in ("calibration", "refit"):
            for path in sorted(dest.glob(f"{phase}_[0-9][0-9][0-9].json")):
                receipt = json.loads(path.read_text())
                row = {
                    k: receipt.get(k)
                    for k in ("phase", "epoch", "steps", "online_objective", "ic", "qualifies")
                }
                for role in ("inner_train", "inner_validation", "refit"):
                    if role + "_off" in receipt:
                        row[role + "_off_loss"] = receipt[role + "_off"]["actual_objective"]
                epochs.append(row)
            batches = pd.concat(
                [pd.read_csv(p) for p in sorted(dest.glob(f"{phase}_*_batches.csv"))],
                ignore_index=True,
            )
            if not np.isfinite(batches[["preclip", "postclip", "update_norm"]].to_numpy()).all():
                raise ValueError("NONFINITE_SAVED_GRADIENT_TRACE")
            health.append(
                dict(
                    phase=phase,
                    updates=len(batches),
                    max_preclip=batches.preclip.max(),
                    max_postclip=batches.postclip.max(),
                    clipped_batches=int(batches.preclip.gt(1).sum()),
                    max_update_norm=batches.update_norm.max(),
                )
            )
        training.append("### Epoch timeline\n\n" + markdown(pd.DataFrame(epochs)) + "\n")
        training.append("### Gradient/update summary\n\n" + markdown(pd.DataFrame(health)) + "\n")
        training.append(
            "Every batch/parameter gradient, source-quality table, month/stock/slot breakdown "
            f"and four role exports are linked in the [run file map]({run}/RUN_DIAGNOSTICS.md).\n"
        )
    (out / "S4_DETAILED_TRAINING_VALIDATION_REFIT_OOS.md").write_text("\n".join(training))
    (out / "S4_EXTREME_OBJECTIVE_NUMERATOR_MAD_DIAGNOSTICS.md").write_text("\n".join(tails))


def summarize(out: Path) -> None:
    """Require all eight completed gates and reconcile every annual primary IC."""
    if not all((out / run / "PASS.json").is_file() for run in RUNS):
        raise ValueError("ALL_EIGHT_COMPLETED_GATES_REQUIRED")
    annual_rows, daily_frames, category_rows, lifecycle, churn = [], [], [], [], []
    matched_categories = []
    for year in range(2021, 2025):
        context = pd.read_parquet(
            out / f"HF20-S4A-F{year % 100}-H4-NR-S42/oos_scores.parquet",
            columns=["origin_id", "category", "slot"],
        ).drop_duplicates("origin_id")
        expected_keys = context.origin_id.tolist()
        for model in ("N0", "N1", "N2", "P", "NR", "T2R"):
            neural = model in ("NR", "T2R")
            dest = out / (
                f"HF20-S4A-F{year % 100}-H4-{model}-S42" if neural else f"F{year % 100}_S4_{model}"
            )
            metric = json.loads((dest / "oos_metrics.json").read_text())
            annual_rows.append(metric)
            origins = pd.read_csv(dest / "oos_origins.csv")
            if origins.origin_id.tolist() != expected_keys:
                raise ValueError("SAVED_BASELINE_ORIGIN_ORDER_MISMATCH", dest)
            origins = origins.merge(
                context[["origin_id", "category"]], on="origin_id", validate="one_to_one"
            )
            daily = origins.groupby("session_date_et", as_index=False)[
                ["ic", "top4", "bottom4", "concordance"]
            ].mean()
            daily["year"], daily["model"] = year, model
            if model != "N0":
                np.testing.assert_allclose(
                    daily.ic.mean(), metric["daily_ic"], rtol=1e-11, atol=1e-12
                )
            daily_frames.append(daily)
            groups = {
                "ALL": pd.Series(True, index=origins.index),
                "OLD_MORNING": origins.slot.isin(["10:30", "11:30"]),
                "OPENING": origins.slot.eq("09:30"),
                "AFTERNOON": origins.slot.isin(["12:30", "13:30", "14:30", "15:30"]),
                "INTRADAY": origins.category.eq("INTRADAY"),
                "OVERNIGHT": origins.category.eq("OVERNIGHT"),
            }
            for group, mask in groups.items():
                subset = origins.loc[mask]
                grouped = subset.groupby("session_date_et", as_index=False)[
                    ["ic", "top4", "bottom4", "concordance"]
                ].mean()
                grouped["year"], grouped["model"], grouped["group"] = year, model, group
                grouped["origins"] = grouped.session_date_et.map(
                    subset.groupby("session_date_et").size()
                )
                category_rows.append(grouped)
            if not neural:
                continue
            binding = json.loads((dest / "calibration_binding.json").read_text())
            refit = json.loads((dest / "refit_binding.json").read_text())
            gate = json.loads((dest / "PASS.json").read_text())
            lifecycle.append(
                dict(
                    run_id=dest.name,
                    year=year,
                    model=model,
                    calibration_epochs=len(list(dest.glob("calibration_[0-9][0-9][0-9].json"))),
                    selected_epoch=binding["selected"],
                    raw_best_epoch=binding["raw_best_epoch"],
                    refit_updates=refit["optimizer_updates"],
                    seconds=gate["seconds"],
                    reload_max_error=gate["checkpoint_reload_max_error"],
                    peak_rss_bytes=gate["resources"]["peak_rss_bytes"],
                    checkpoint_sha256=refit["checkpoint_sha256"],
                )
            )
            scores = pd.read_parquet(dest / "oos_scores.parquet")
            movement, sets = transitions(scores, year, model)
            for relation, values in movement.groupby("relation"):
                matched = sets.loc[sets.relation.eq(relation)]
                churn.append(
                    dict(
                        year=year,
                        model=model,
                        relation=relation,
                        transitions=values.origin_id.nunique(),
                        mean_absolute_rank_change=values.absolute_change.mean(),
                        median_absolute_rank_change=values.absolute_change.median(),
                        mean_top4_jaccard=matched.loc[matched.side.eq("TOP4"), "jaccard"].mean(),
                        mean_bottom4_jaccard=matched.loc[
                            matched.side.eq("BOTTOM4"), "jaccard"
                        ].mean(),
                        mean_names_entering=matched.entering.mean(),
                    )
                )
            matched = pd.read_csv(dest / "oos_matched_category_sessions.csv")
            matched["year"], matched["model"] = year, model
            matched_categories.append(matched)
    annual = pd.DataFrame(annual_rows)
    annual.to_csv(out / "S4_ANNUAL_NEURAL_AND_BASELINE_METRICS.csv", index=False)
    daily = pd.concat(daily_frames, ignore_index=True)
    categories = pd.concat(category_rows, ignore_index=True)
    summary = []
    for (model, group), frame in categories.groupby(["model", "group"]):
        summary.append(
            dict(
                model=model,
                group=group,
                origins=int(frame.origins.sum()),
                sessions=len(frame),
                **interval(frame, "ic"),
                top4=frame.groupby("year").top4.mean().mean(),
                bottom4=frame.groupby("year").bottom4.mean().mean(),
                pair_concordance=frame.groupby("year").concordance.mean().mean(),
            )
        )
    pd.DataFrame(summary).to_csv(
        out / "S4_EQUAL_YEAR_BASELINE_AND_CATEGORY_INTERVALS.csv", index=False
    )
    paired = []
    for model in ("NR", "T2R"):
        a = daily.loc[daily.model.eq(model)]
        for reference in ("N1", "N2", "P"):
            b = daily.loc[daily.model.eq(reference)]
            joined = a.merge(
                b,
                on=["year", "session_date_et"],
                suffixes=("", "_reference"),
                validate="one_to_one",
            )
            if len(joined) != len(a):
                raise ValueError("PAIRED_DAILY_KEYS_CHANGED")
            joined["difference"] = joined.ic - joined.ic_reference
            paired.append(dict(model=model, reference=reference, **interval(joined, "difference")))
    pd.DataFrame(paired).to_csv(out / "S4_EQUAL_YEAR_PAIRED_BASELINE_INTERVALS.csv", index=False)
    matched = pd.concat(matched_categories, ignore_index=True)
    paired_categories = [
        dict(
            model=model,
            contrast="OVERNIGHT_MINUS_INTRADAY_SHARED_SESSIONS",
            sessions=len(frame),
            **interval(frame, "difference"),
        )
        for model, frame in matched.groupby("model")
    ]
    pd.DataFrame(paired_categories).to_csv(
        out / "S4_EQUAL_YEAR_MATCHED_CATEGORY_INTERVALS.csv", index=False
    )
    pd.DataFrame(lifecycle).to_csv(out / "S4_COMPLETE_LIFECYCLE_SUMMARY.csv", index=False)
    pd.DataFrame(churn).to_csv(out / "S4_RANK_STABILITY_AND_SELECTION_CHURN.csv", index=False)
    detailed_reports(out)
    print(
        "S4_SAVED_SUMMARY_PASS: 8 lifecycles, 24 annual model/control rows; primary IC reconciled"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    summarize(parser.parse_args().out)
