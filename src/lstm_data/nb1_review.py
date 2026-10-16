"""Matched descriptive review of the four immutable N-B1 results; no fitting."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd

from .calendar import schedule
from .config import write_json
from .controlled_review import audit_batches, checkpoint_metadata, finish_frame
from .four_model_diagnostics import paired_blocks
from .nb1_authority import JOURNAL, authority, journal_rows
from .nb1_experiment import reference
from .nb1_inputs import transform
from .neural_engine import SharedLSTM
from .neural_health import g6_summary
from .normalization_population import PARTS, PREFIX, fit_records, population, preparations
from .normalization_stats import distribution
from .pretraining_policy import verify_ref
from .real_bridge_run import load_real_checkpoint
from .visualization.controlled import Study
from .visualization.loaders import (
    Catalog,
    component_base,
    feature_frame,
    read_json,
    records_frame,
    source_bars,
)
from .visualization.metrics import loss_concentration, matched, summary


def genuine_b1_oracles(catalog: Catalog, recipes: dict) -> list[dict]:
    """Independent 30-minute H/L aggregation for each development tail and an ordinary bar."""
    base = component_base(catalog)
    rows = []
    for fold, day in (("WF1", "2023-10-27"), ("WF2", "2024-01-25")):
        source, _ = source_bars(catalog, "CMCSA", day, day)
        for prefix in ("inner", "refit"):
            frame = feature_frame(
                catalog,
                base,
                "CMCSA",
                fold,
                day,
                day,
                1,
                "Inner validation" if prefix == "inner" else "Development",
            )
            recipe = recipes[fold][prefix]
            for slot in (1, 3):
                pair = source.iloc[(slot - 1) * 2 : slot * 2]
                if len(pair) != 2 or (
                    pair.timestamp.iloc[1] - pair.timestamp.iloc[0]
                ) != pd.Timedelta(minutes=30):
                    raise ValueError("GENUINE_TWO_HALF_HOURS_REQUIRED")
                end = pair.timestamp.iloc[1] + pd.Timedelta(minutes=30)
                high, low = float(pair.high.max()), float(pair.low.min())
                x = math.log(high / low)
                registered = frame.loc[frame.feature.eq("B1") & frame.timestamp.eq(end)].iloc[0]
                if not math.isclose(x, float(registered.native), rel_tol=0, abs_tol=1e-12):
                    raise ValueError("INDEPENDENT_B1_SOURCE_ORACLE_FAILED")
                q = math.asinh(x / recipe["s"])
                z = float(np.float32((q - recipe["c"]) / recipe["a"]))
                expected = float(
                    np.float32(
                        (np.arcsinh(float(registered.native) / recipe["s"]) - recipe["c"])
                        / recipe["a"]
                    )
                )
                if z != expected:
                    raise ValueError("INDEPENDENT_B1_FLOAT32_ORACLE_FAILED")
                rows.append(
                    dict(
                        fold=fold,
                        prefix=prefix,
                        symbol="CMCSA",
                        day=day,
                        slot=slot,
                        end_UTC=str(end),
                        high=high,
                        low=low,
                        native_x=x,
                        s=recipe["s"],
                        q=q,
                        c=recipe["c"],
                        a=recipe["a"],
                        scaled=z,
                        original_scaled=float(registered.scaled),
                        source_lineage=pair.provenance_id.tolist(),
                        passed=True,
                    )
                )
    return rows


def b1_diagnostics(catalog: Catalog, recipes: dict, out: Path) -> dict:
    """Reuse the012A exact populations; deduplicate hourly keys and overlapping exposures."""
    base = component_base(catalog)
    study = Study.discover(catalog)
    candidates = preparations(catalog, base)
    rows, histograms, ties = [], {}, []
    for fold in ("WF1", "WF2"):
        for part in PARTS:
            prefix = PREFIX[part]
            r = recipes[fold][prefix]
            pop = population(catalog, base, study, fold, part, candidates[fold, prefix])
            frame = fit_records(pop, "B1") if part.endswith("training") else pop.channel("B1")
            frame = frame.loc[frame.B1.notna()].copy()
            if part.endswith("training") and len(frame) != r["count"]:
                raise ValueError("B1_DIAGNOSTIC_FIT_POPULATION_MISMATCH")
            x = frame.B1.to_numpy(dtype=float)
            frame["native"] = x
            frame["q"] = np.arcsinh(x / r["s"])
            frame["C0"] = ((x - r["original_center"]) / r["original_scale"]).astype(np.float32)
            frame["N-B1"] = transform(x, r)
            valid = frame.B1_scaled.notna()
            if not np.array_equal(
                frame.loc[valid, "C0"].to_numpy(), frame.loc[valid, "B1_scaled"].to_numpy()
            ):
                raise ValueError("ORIGINAL_B1_DIAGNOSTIC_NOT_EXACT_FLOAT32")
            for symbol in ("POOLED", *r["symbol_order"]):
                group = frame if symbol == "POOLED" else frame.loc[frame.symbol.eq(symbol)]
                for rep in ("native", "q", "C0", "N-B1"):
                    values = group[rep].to_numpy()
                    rows.append(
                        dict(
                            fold=fold,
                            partition=part,
                            symbol=symbol,
                            representation=rep,
                            recipe_id=r["recipe_id"],
                            population="canonical unique hourly keys",
                            **distribution(values, False),
                        )
                    )
                    counts, edges = np.histogram(values, bins=80)
                    histograms[f"{fold}:{part}:{symbol}:{rep}"] = dict(
                        counts=counts.tolist(), edges=edges.tolist()
                    )
            # Count information loss across the five-stock contrasts without assuming IID rows.
            added, reversals, total, incomplete = 0, 0, 0, 0
            for _, group in frame.groupby("timestamp"):
                if len(group) != 5:
                    incomplete += 1
                    continue
                old, new = group.C0.to_numpy(), group["N-B1"].to_numpy()
                for i in range(5):
                    for j in range(i + 1, 5):
                        total += int(old[i] != old[j])
                        added += int(old[i] != old[j] and new[i] == new[j])
                        reversals += int((old[i] - old[j]) * (new[i] - new[j]) < 0)
            ties.append(
                dict(
                    fold=fold,
                    partition=part,
                    distinct_C0_pairs=total,
                    new_float32_pair_ties=added,
                    ordering_reversals=reversals,
                    incomplete_cross_sections=incomplete,
                )
            )
    pd.DataFrame(rows).to_csv(out / "b1_canonical_distributions.csv", index=False)
    write_json(out / "b1_histograms.json", dict(histograms=histograms))
    write_json(
        out / "b1_rank_and_ties.json",
        dict(
            comparisons=ties,
            limitation=(
                "q strictly increasing; any final float32 ties are arithmetic rounding, "
                "no hard clipping"
            ),
        ),
    )
    return dict(distribution_rows=len(rows), canonical_populations=8, rank_comparisons=ties)


def review(out: Path, approval: Path) -> dict:
    started = time.monotonic()
    root = Path.cwd()
    plan_ref = reference(out / "experiment_design.json")
    plan = json.loads(verify_ref(root, plan_ref).read_text())
    catalog = Catalog.discover(root)
    Study.discover(catalog)
    comparisons, differences, origins, gradients, forecasts, curves, concentrations = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    intervals, audits, timings = {}, {}, {}
    for run in plan["runs"]:
        fold, seed, name = run["fold"], run["seed"], run["run_id"]
        permit = authority(root, plan_ref, reference(approval), name)
        run_out = out / name
        result_path = run_out / f"seed{seed}_tm0_pair_result.json"
        result = json.loads(result_path.read_text())
        records = result["development"]["origin_records"]
        frame = finish_frame(
            records_frame(records, "N-B1", fold, "Development"), "N-B1", seed, fold
        )
        control = pd.read_csv(
            verify_ref(root, plan["controls"][fold][str(seed)]), float_precision="round_trip"
        )
        matched(frame, control)
        if frame.session.max() > ("2023-12-31" if fold == "WF1" else "2024-06-30"):
            raise ValueError("NB1_PROTECTED_FORECAST")
        panel = permit.view(fold)
        if (
            panel.summary() != run["views"][fold]
            or result["development_population"] != panel.summary()
        ):
            raise ValueError("NB1_RESULT_RECIPE_OR_PANEL_CHANGED")
        snapshots = {}
        for stage, filename, key in (
            ("CALIBRATION_SELECTED", "calibration_selected.pt", "inner"),
            ("REFIT_FINAL", "refit_final.pt", "refit"),
        ):
            path = run_out / filename
            prep = run["views"][key]["preparation_id"]
            snapshots[stage] = checkpoint_metadata(path, result, stage, prep)
            load_real_checkpoint(path, SharedLSTM(16), result["pair_key"], prep, stage, permit)
        trace = [
            json.loads(p.read_text()) for p in sorted(run_out.glob("calibration_epoch_*.json"))
        ]
        refit = [json.loads(p.read_text()) for p in sorted(run_out.glob("refit_epoch_*.json"))]
        if (
            len(trace) != result["selector"]["epoch"]
            or len(refit) != result["selector"]["selected"]
            or result["initial_hashes"][0] != result["initial_hashes"][1]
            or result["fresh_optimizer_state_empty"] is not True
        ):
            raise ValueError("NB1_FRESH_D6G_PROVENANCE_FAILED")
        health = g6_summary(
            tuple(r["training"] for r in trace),
            tuple(refit),
            result["development"]["score_std"],
            result["selector"]["status"],
        )
        if health != result["G6_both_pass"]:
            raise ValueError("NB1_G6_CHANGED")
        for pass_name, epochs, key in (
            ("calibration", [r["training"] for r in trace], "inner"),
            ("refit", refit, "refit"),
        ):
            batch, checks = audit_batches(
                run_out / f"gradient_batches_{pass_name}.csv", epochs, permit.view(key), seed, 1.0
            )
            gradients.append(
                dict(
                    fold=fold,
                    seed=seed,
                    arm="N-B1",
                    pass_name=pass_name,
                    G6=health["status"],
                    **batch,
                )
            )
            audits[f"{name}:{pass_name}"] = checks
        model = "TM0" if seed == 42 else f"C0 [{seed}]"
        control_result = catalog.result(fold, model)
        # Original traces remain read-only; the explicit chart table labels stages.
        for arm in ("C0", "N-B1"):
            if arm == "C0":
                calibration = [
                    read_json(root, r) for r in catalog.config["traces"][fold][model]["calibration"]
                ]
                final = [read_json(root, r) for r in catalog.config["traces"][fold][model]["refit"]]
            else:
                calibration, final = trace, refit
            for record in calibration:
                tr, va = record["training"], record["validation"]
                curves.append(
                    dict(
                        fold=fold,
                        seed=seed,
                        arm=arm,
                        pass_name="calibration",
                        epoch=tr["epoch"],
                        training_MSE=tr["mse"],
                        validation_MSE=va["mse"],
                        clipping_fraction=tr["gradients"]["clipped_fraction"],
                        steps=tr["steps"],
                        preclip_norm_max=tr["gradients"]["max"],
                        preclip_norm_median=tr["gradients"]["median"],
                    )
                )
            for record in final:
                curves.append(
                    dict(
                        fold=fold,
                        seed=seed,
                        arm=arm,
                        pass_name="refit",
                        epoch=record["epoch"],
                        training_MSE=record["mse"],
                        validation_MSE=None,
                        clipping_fraction=record["gradients"]["clipped_fraction"],
                        steps=record["steps"],
                        preclip_norm_max=record["gradients"]["max"],
                        preclip_norm_median=record["gradients"]["median"],
                    )
                )
        treatment_stats, control_stats = summary(frame), summary(control)
        paired = treatment_stats["daily"].merge(
            control_stats["daily"], on="session", suffixes=("_NB1", "_C0"), validate="one_to_one"
        )
        paired["delta_MSE"] = paired.MSE_NB1 - paired.MSE_C0
        paired["delta_IC"] = paired.IC_NB1 - paired.IC_C0
        differences.extend(dict(fold=fold, seed=seed, **row) for row in paired.to_dict("records"))
        calendar = schedule(str(paired.session.min()), str(paired.session.max()))
        mapping = {pd.Timestamp(day).date().isoformat(): i for i, day in enumerate(calendar.index)}
        positions = np.asarray([mapping[day] for day in paired.session])
        intervals[name] = {
            metric: paired_blocks(paired[metric].to_numpy(), positions, 5)
            for metric in ("delta_MSE", "delta_IC")
        }
        comparisons.append(
            dict(
                fold=fold,
                seed=seed,
                C0_MSE=control_stats["MSE"],
                NB1_MSE=treatment_stats["MSE"],
                delta_MSE=treatment_stats["MSE"] - control_stats["MSE"],
                C0_IC=control_stats["daily_Rank_IC"],
                NB1_IC=treatment_stats["daily_Rank_IC"],
                delta_IC=treatment_stats["daily_Rank_IC"] - control_stats["daily_Rank_IC"],
                origins=treatment_stats["origins"],
                sessions=treatment_stats["days"],
                canonical_targets_exact=True,
                masks_exact=True,
                C0_G6=control_result["G6"],
                NB1_G6=result["G6"],
                C0_selected_epoch=control_result["selector"]["selected"],
                NB1_selected_epoch=result["selector"]["selected"],
                ZERO_MSE=float(
                    control.groupby(["session", "origin"])
                    .TG0.apply(lambda s: (s * s).mean())
                    .groupby("session")
                    .mean()
                    .mean()
                ),
            )
        )
        for arm, f in (("N-B1", frame), ("C0", control)):
            _, concentration = loss_concentration(f)
            concentrations.append(dict(fold=fold, seed=seed, arm=arm, **concentration))
            for row in summary(f)["by_origin"].to_dict("records"):
                origins.append(dict(fold=fold, seed=seed, arm=arm, **row))
        forecasts.append(frame)
        timings[name] = json.loads((run_out / "training_actual_runtime.json").read_text())
        audits[name] = dict(
            checkpoints=snapshots,
            fresh_seed_and_optimizer=True,
            exact_targets_and_masks=True,
            G6=health,
            result=reference(result_path),
            target_binding=run["views"][fold]["view_id"],
        )
    comparison = pd.DataFrame(comparisons)
    daily = pd.DataFrame(differences)
    daily["month"] = daily.session.str[:7]
    comparison.to_csv(out / "matched_results.csv", index=False)
    daily.to_csv(out / "paired_daily_differences.csv", index=False)
    daily.groupby(["fold", "seed", "month"])[
        ["MSE_NB1", "MSE_C0", "delta_MSE", "IC_NB1", "IC_C0", "delta_IC"]
    ].mean().reset_index().to_csv(out / "monthly_comparison.csv", index=False)
    pd.DataFrame(origins).to_csv(out / "origin_comparison.csv", index=False)
    pd.DataFrame(gradients).to_csv(out / "gradient_health.csv", index=False)
    curve_frame = pd.DataFrame(curves)
    curve_frame.to_csv(out / "training_curves.csv", index=False)
    comparison_rows = []
    for (fold, seed, arm, pass_name), group in curve_frame.groupby(
        ["fold", "seed", "arm", "pass_name"]
    ):
        comparison_rows.append(
            dict(
                fold=fold,
                seed=seed,
                arm=arm,
                pass_name=pass_name,
                epochs=len(group),
                updates=int(group.steps.sum()),
                fraction_preclip_above1=float(
                    np.average(group.clipping_fraction, weights=group.steps)
                ),
                preclip_norm_max=float(group.preclip_norm_max.max()),
                source="Exact saved per-epoch gradient summaries; no control fitting",
            )
        )
    pd.DataFrame(comparison_rows).to_csv(out / "gradient_comparison.csv", index=False)
    pd.DataFrame(concentrations).to_csv(out / "loss_concentration.csv", index=False)
    pd.concat(forecasts).to_csv(out / "forecasts.csv", index=False)
    write_json(out / "postrun_audits.json", audits)
    write_json(
        out / "exploratory_block_intervals.json",
        dict(status="EXPLORATORY_POST_SCREEN_NOT_SELECTION_ADJUSTED", intervals=intervals),
    )
    mse_wins = int((comparison.delta_MSE < 0).sum())
    ic_wins = int((comparison.delta_IC > 0).sum())
    rows = journal_rows(Path(JOURNAL))
    if (
        len(rows) != 16
        or rows[-1]["global_started_pairs"] != 28
        or rows[-1]["status"] != "COMPLETED"
    ):
        raise ValueError("NB1_COMPLETE_FOUR_PAIR_ACCOUNTING_REQUIRED")
    results = dict(
        status="P012B_ENGINEERING_PASS",
        MSE_wins=mse_wins,
        IC_wins=ic_wins,
        cells=4,
        global_started_pairs=28,
        ceiling=200,
        confirmation_numeric_rows=0,
        interpretation="Exploratory already-inspected development; no significance or alpha claim",
        N_V12="UNTRAINED",
        G6="WARN retained; see each pass and control comparison",
        seconds=time.monotonic() - started,
        neural_fitting_seconds=sum(v["neural_fitting_seconds"] for v in timings.values()),
        pair_runtime=timings,
    )
    write_json(out / "results_summary.json", results)
    (out / "summary.md").write_text(
        f"# Package012B · historical N-B1\n\nEngineering PASS; 28/200 starts. "
        f"N-B1 improves matched MSE in {mse_wins}/4 and daily Rank IC in {ic_wins}/4 cells. "
        "Each cell is in matched_results.csv; five-session intervals are exploratory, "
        "post-screen and not selection-adjusted. This is no independent confirmation. "
        "The monotone feature transform changes B1 amplitude only; TG0 remains unchanged. "
        "G6 WARNs and both-pass clipping remain visible. Neither finite predictions nor "
        "smaller B1 tails establish a useful ranking mechanism. A separately preregistered "
        "independent development evaluation would be needed for stronger evidence; "
        "no further fit or confirmation access is authorized here. N-V12 remains untrained. "
        "Source/publication/actions/PIT/rights/course/joint/production qualifications persist.\n"
    )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--approval", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(review(args.out, args.approval)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
