"""Read-only Package011 canonical-score comparisons and compact dashboard registration."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .calendar import schedule
from .config import digest, write_json
from .controlled_authority import JOURNAL, journal_rows, load_plan, load_stock_inputs
from .four_model_diagnostics import paired_blocks, session_concentration
from .neural_health import g6_summary
from .neural_lifecycle import EarlyStop
from .pretraining_policy import CANDIDATE
from .real_batch_authority import atomic_replace_json
from .real_bridge_data import RealInputView
from .visualization.loaders import records_frame
from .visualization.metrics import matched, summary

CAVEAT = (
    "ASSUMPTION_CONDITIONAL: private researcher rights/clock attestation; retrospective "
    "universe/actions; idealized hour-end availability and hourly-close price proxy. "
    "Explored development, five stocks, two dependent folds and two seeds. No full G8, "
    "alpha, economics, independently certified rights or production/confirmation authority."
)


def reference(path: Path) -> dict:
    return dict(path=str(path), sha256=digest(path))


def finish_frame(frame: pd.DataFrame, arm: str, seed: int, fold: str) -> pd.DataFrame:
    frame = frame.copy()
    frame["arm"], frame["seed"], frame["fold"] = arm, seed, fold
    frame["score"] = frame.score.astype(float)
    frame["TG0"] = frame.TG0.astype(float)
    frame["residual"] = frame.score - frame.TG0
    frame["squared_error"] = frame.residual**2
    frame["origin_timestamp"] = (
        pd.to_datetime(frame.session + frame.origin.map({1: " 10:30", 2: " 11:30"}))
        .dt.tz_localize("America/New_York")
        .dt.tz_convert("UTC")
        .astype(str)
    )
    if (
        len(frame) != 1160
        or frame.session.nunique() != 116
        or frame.duplicated(["session", "origin", "symbol"]).any()
        or not np.isfinite(frame[["TG0", "score"]]).all().all()
    ):
        raise ValueError("TA011_FINITE_EXACT_OUTER_PANEL_REQUIRED")
    if not (
        pd.to_datetime(frame.origin_timestamp, utc=True) < pd.Timestamp("2024-07-01T04:00Z")
    ).all():
        raise ValueError("TA011_CONFIRMATION_ACCESS_FORBIDDEN")
    return frame


def checkpoint_metadata(path: Path, result: dict, stage: str, preparation: str) -> dict:
    manifest = json.loads(path.with_suffix(".manifest.json").read_text())
    expected = result[
        "selected_checkpoint" if stage == "CALIBRATION_SELECTED" else "final_checkpoint"
    ]
    if digest(path) != manifest["sha256"] or manifest != expected:
        raise ValueError("TA011_CHECKPOINT_HASH_CHANGED")
    body = torch.load(path, map_location="cpu", weights_only=True)
    if (
        body["contract"] != result["contract"]
        or body["pair_key"] != result["pair_key"]
        or body["stage"] != stage
        or body["preparation_id"] != preparation
        or body["epoch"] != result["selector"]["selected"]
        or sum(v.numel() for v in body["model"].values()) != result["contract"]["parameters"]
        or any(
            v.dtype != torch.float32 or not bool(torch.isfinite(v).all())
            for v in body["model"].values()
        )
    ):
        raise ValueError("TA011_SELECTED_FINAL_METADATA_MISMATCH")
    return dict(
        path=str(path),
        sha256=manifest["sha256"],
        stage=stage,
        epoch=body["epoch"],
        preparation_id=preparation,
        weights_only=True,
        finite=True,
        resumable=False,
    )


def association(left: pd.Series, right: pd.Series) -> float | None:
    """Undefined constant/tiny sample correlations remain missing, never NaN evidence."""
    if len(left) < 2 or left.nunique() < 2 or right.nunique() < 2:
        return None
    return float(left.corr(right))


def audit_batches(
    path: Path, trace: list[dict], view: RealInputView, seed: int, cap: float
) -> tuple[dict, list[dict]]:
    from .neural_engine import session_batches

    frame = pd.read_csv(path, float_precision="round_trip")
    if (
        frame.empty
        or not (frame.seed == seed).all()
        or not (frame.clip_cap == cap).all()
        or not frame.finite_flag.all()
    ):
        raise ValueError("TA011_BATCH_SEED_CAP_FINITE_MISMATCH")
    if frame.optimizer_step_id.tolist() != list(range(1, len(frame) + 1)):
        raise ValueError("TA011_STEP_CONSERVATION")
    if set(frame.epoch) != {record["epoch"] for record in trace} or len(frame) != sum(
        record["steps"] for record in trace
    ):
        raise ValueError("TA011_COMPLETE_EPOCH_AND_STEP_LOG_REQUIRED")
    rows = []
    for record in trace:
        epoch = record["epoch"]
        g = frame.loc[frame.epoch == epoch]
        positions = list(session_batches(len(view.sessions), seed, epoch, shuffle=True))
        expected = ["|".join(view.sessions[i] for i in batch) for batch in positions]
        if (
            g.session_ids.tolist() != expected
            or len(g) != record["steps"]
            or int(g.number_sessions.sum()) != len(view.sessions)
            or int(g.number_origins.sum()) != len(view.rows)
        ):
            raise ValueError("TA011_BATCH_SESSION_OR_ORIGIN_CONSERVATION")
        norm = g.preclip_global_grad_norm.to_numpy()
        multiplier = np.minimum(1, cap / (norm + 1e-6))
        if not np.array_equal(g.clip_applied.to_numpy(), multiplier < 1) or not np.allclose(
            g.clip_multiplier, multiplier, rtol=1e-14, atol=1e-15
        ):
            raise ValueError("TA011_ACTUAL_SINGLE_CLIP_FORMULA_MISMATCH")
        mse = float(np.average(g.batch_session_weighted_MSE, weights=g.number_sessions))
        if not math.isclose(mse, record["mse"], rel_tol=2e-7, abs_tol=1e-7):
            raise ValueError("TA011_CANONICAL_EPOCH_RECONSTRUCTION_MISMATCH")
        rows.append(
            dict(
                epoch=epoch,
                canonical_MSE_reconstructed=mse,
                steps=len(g),
                sessions=int(g.number_sessions.sum()),
                origins=int(g.number_origins.sum()),
                passed=True,
            )
        )
    return dict(
        batches=len(frame),
        fraction_above1=float((frame.preclip_global_grad_norm > 1).mean()),
        fraction_above5=float((frame.preclip_global_grad_norm > 5).mean()),
        applied_clip_fraction=float(frame.clip_applied.mean()),
        norm_p50=float(frame.preclip_global_grad_norm.median()),
        norm_p90=float(frame.preclip_global_grad_norm.quantile(0.9)),
        norm_p99=float(frame.preclip_global_grad_norm.quantile(0.99)),
        norm_max=float(frame.preclip_global_grad_norm.max()),
        canonical_loss_norm_Pearson=association(
            frame.batch_session_weighted_MSE, frame.preclip_global_grad_norm
        ),
        target_max_norm_Pearson=association(frame.target_abs_max, frame.preclip_global_grad_norm),
        association_only=True,
    ), rows


def review(out: Path, plan_path: Path | None = None) -> dict:
    root = Path.cwd()
    if (out / "review_summary.json").exists():
        raise ValueError("SEALED_TA011_REVIEW_EXISTS_USE_NEW_NAMESPACE")
    plan_path = plan_path or out / "predeclared_experiment_matrix.json"
    plan, review_authority = load_plan(root, reference(plan_path))
    journal = journal_rows(root / JOURNAL)
    frames = {}
    results = {}
    registry = []
    epoch_rows = []
    gradient_rows = []
    audits = {}
    metadata = []
    pointers = []
    parameters = []
    dashboard = json.loads((out / "visualization_config_before.json").read_text())
    dashboard["both_pass_health"] = {
        "WF1": reference(
            Path(
                "reports/data_audit/ta008_four_model_diagnostics_2026-10-15_094143/g6_summary.json"
            )
        ),
        "WF2": reference(
            Path("reports/data_audit/ta009_wf2_tm0_mc0_2026-10-15_101729/review_summary.json")
        ),
    }
    dashboard["controlled_models"] = {f: {} for f in ("WF1", "WF2")}
    dashboard["controlled_telemetry"] = {f: {} for f in ("WF1", "WF2")}
    views = {}
    for fold in ("WF1", "WF2"):
        inputs = load_stock_inputs(review_authority, plan, fold)
        views[fold] = {
            key: inputs.stock_view(key) for key in ("inner", "validation", "refit", fold)
        }
        baseline = (
            dashboard["baseline"]["path"]
            if fold == "WF1"
            else (
                "reports/data_audit/ta009_wf2_tm0_mc0_2026-10-15_101729/wf2_matched_predictions.csv"
            )
        )
        original = pd.read_csv(baseline, float_precision="round_trip")
        if fold == "WF1":
            original = original.loc[original.partition == "WF1"].copy()
        original["score"] = original.TM0
        frame = finish_frame(
            original[["session", "origin", "symbol", "TG0", "score"]], "C0", 42, fold
        )
        canonical = np.asarray(
            [r.targets for r in views[fold][fold].rows], dtype=np.float32
        ).reshape(-1)
        expected = (
            frame.set_index(["session", "origin", "symbol"])
            .loc[[(r.session, r.origin, s) for r in views[fold][fold].rows for s in CANDIDATE]]
            .TG0.to_numpy()
        )
        if not np.array_equal(canonical, expected):
            raise ValueError("TA011_CONTROL_RAW_TARGET_IDENTITY_FAILED")
        result = json.loads(Path(dashboard["models"][fold]["TM0"]["path"]).read_text())
        health = json.loads(Path(dashboard["both_pass_health"][fold]["path"]).read_text())
        result["G6_both_pass"] = health["TM0"] if fold == "WF1" else health["health"]["TM0"]
        frame["checkpoint_id"] = result["final_checkpoint"]["sha256"]
        frame["authority_id"] = result["pair_key"]
        frames[fold, 42, "C0"] = frame
        results[fold, 42, "C0"] = result
        metadata.append(
            dict(fold=fold, arm="C0", seed=42, status="REUSED_HISTORICAL_NO_FIT", source=baseline)
        )
    for fold in ("WF1", "WF2"):
        historical = results[fold, 42, "C0"]
        for stage, refs in dashboard["traces"][fold]["TM0"].items():
            saved = [json.loads(Path(ref["path"]).read_text()) for ref in refs]
            records = [r["training"] if stage == "calibration" else r for r in saved]
            count = sum(r["steps"] for r in records)
            stats = dict(
                batches=count,
                fraction_above1=sum(
                    r["gradients"]["clipped_fraction"] * r["steps"] for r in records
                )
                / count,
                fraction_above5=None,
                applied_clip_fraction=None,
                norm_p50=None,
                norm_p90=None,
                norm_p99=None,
                norm_max=max(r["gradients"]["max"] for r in records),
                observation_scope="HISTORICAL_EPOCH_AGGREGATES_NO_BATCH_RECONSTRUCTION",
            )
            if fold == "WF2":
                ref = dashboard["batch_telemetry"]["TM0"][stage]
                batches = pd.read_csv(ref["path"], float_precision="round_trip")
                stats.update(
                    fraction_above5=float((batches.preclip_global_grad_norm > 5).mean()),
                    applied_clip_fraction=float(batches.clip_applied.mean()),
                    norm_p50=float(batches.preclip_global_grad_norm.median()),
                    norm_p90=float(batches.preclip_global_grad_norm.quantile(0.9)),
                    norm_p99=float(batches.preclip_global_grad_norm.quantile(0.99)),
                    observation_scope="HISTORICAL_CAPTURED_BATCH_OBSERVER_v1",
                )
            gradient_rows.append(
                dict(
                    run_id=f"C0-S42-{fold}-REUSED",
                    fold=fold,
                    seed=42,
                    arm="C0",
                    stage=stage,
                    clip_cap=1.0,
                    G6_both_pass=historical["G6_both_pass"]["status"],
                    **stats,
                )
            )
    for descriptor in plan["runs"]:
        name = descriptor["run_id"]
        fold = descriptor["fold"]
        seed = descriptor["seed"]
        arm = descriptor["arm"]
        own = [r for r in journal if r["run_id"] == name]
        status = own[-1]["status"] if own else "NOT_STARTED"
        registry.append(
            dict(
                run_id=name,
                fold=fold,
                seed=seed,
                arm=arm,
                status=status,
                planned=True,
                started=bool(own),
                valid=status == "COMPLETED",
                input_id=descriptor["input_id"],
                proposal_sha256=digest(plan_path),
            )
        )
        for stage, param in descriptor["target_parameters"].items():
            parameters.append(
                dict(
                    run_id=name,
                    fold=fold,
                    seed=seed,
                    arm=arm,
                    stage=stage,
                    parameter_id=param["parameter_id"],
                    cap=param["policy"]["cap"] if arm == "T1" else None,
                    scale=param["policy"]["scale"] if arm == "T2" else None,
                    scale_floor=param["scale_floor"],
                    observations=param["observations"],
                    population=param["population"],
                    quantile_method=param["quantile_method"],
                    preparation_id=param["preparation_id"],
                    view_id=param["view_id"],
                    cutoff=param["cutoff"],
                )
            )
        if status != "COMPLETED":
            continue
        folder = out / name
        result = json.loads((folder / f"seed{seed}_tm0_pair_result.json").read_text())
        if (
            result["contract"] != descriptor["contract"]
            or result["target_parameters"] != descriptor["target_parameters"]
        ):
            raise ValueError("TA011_RESULT_CONTRACT_OR_PARAMETERS_CHANGED")
        frame = records_frame(result["development"]["origin_records"], arm, fold, "Development")
        frame = finish_frame(frame, arm, seed, fold)
        matched(frame, frames[fold, 42, "C0"])
        frame["checkpoint_id"] = result["final_checkpoint"]["sha256"]
        frame["authority_id"] = result["pair_key"]
        frames[fold, seed, arm] = frame
        results[fold, seed, arm] = result
        metadata.extend(
            checkpoint_metadata(
                folder / file, result, stage, descriptor["views"][key]["preparation_id"]
            )
            for file, stage, key in (
                ("calibration_selected.pt", "CALIBRATION_SELECTED", "inner"),
                ("refit_final.pt", "REFIT_FINAL", "refit"),
            )
        )
        cal_refs = sorted(folder.glob("calibration_epoch_*.json"))
        refit_refs = sorted(folder.glob("refit_epoch_*.json"))
        cal = [json.loads(p.read_text()) for p in cal_refs]
        refit = [json.loads(p.read_text()) for p in refit_refs]
        if (
            len(refit) != result["selector"]["selected"]
            or len(cal) != result["selector"]["epoch"]
            or result["initial_hashes"][0] != result["initial_hashes"][1]
            or result["initial_hashes"][0] != results[fold, 42, "C0"]["initial_hashes"][0]
            and seed == 42
        ):
            raise ValueError("TA011_D6G_FRESH_REFIT_OR_INITIAL_STATE_CHANGED")
        selector = EarlyStop()
        for epoch in cal:
            selector.observe(epoch["validation"]["mse"])
            if vars(selector) != epoch["selection"]:
                raise ValueError("TA011_CANONICAL_D6G_SELECTOR_REPLAY_MISMATCH")
        if vars(selector) != result["selector"]:
            raise ValueError("TA011_FINAL_SELECTOR_BINDING_CHANGED")
        health = g6_summary(
            tuple(r["training"] for r in cal),
            tuple(refit),
            result["development"]["score_std"],
            result["selector"]["status"],
        )
        if health != result["G6_both_pass"] or health["status"] != result["G6"]:
            raise ValueError("TA011_BOTH_PASS_G6_REPLAY_MISMATCH")
        audits[name] = {
            "D6g_original_scale_selector_replayed": True,
            "G6_both_pass_replayed": health,
        }
        runtime = json.loads((folder / "training_actual_runtime.json").read_text())
        for stage, records, refs, key in (
            ("calibration", [r["training"] for r in cal], cal_refs, "inner"),
            ("refit", refit, refit_refs, "refit"),
        ):
            path = folder / f"gradient_batches_{stage}.csv"
            stats, epoch_audit = audit_batches(
                path, records, views[fold][key], seed, descriptor["contract"]["clip"]
            )
            audits[name][stage] = epoch_audit
            gradient_rows.append(
                dict(
                    run_id=name,
                    fold=fold,
                    seed=seed,
                    arm=arm,
                    stage=stage,
                    clip_cap=descriptor["contract"]["clip"],
                    G6_both_pass=result["G6"],
                    **stats,
                )
            )
            pointers.append(
                dict(
                    run_id=name,
                    fold=fold,
                    seed=seed,
                    arm=arm,
                    stage=stage,
                    path=str(path),
                    sha256=digest(path),
                    rows=stats["batches"],
                )
            )
            for index, record in enumerate(records):
                epoch_rows.append(
                    dict(
                        run_id=name,
                        fold=fold,
                        seed=seed,
                        arm=arm,
                        stage=stage,
                        epoch=record["epoch"],
                        canonical_training_MSE=record["mse"],
                        optimizer_objective=record["optimizer_objective"],
                        objective_name=record["objective_name"],
                        inner_validation_MSE=cal[index]["validation"]["mse"]
                        if stage == "calibration"
                        else None,
                        selected_epoch=result["selector"]["selected"],
                        seconds=record["seconds"],
                        updates=record["steps"],
                        learning_rate=0.001,
                        top1_canonical_session_loss_share=record["top_session_loss_share"]["0.01"],
                        top10_canonical_session_loss_share=record["top_session_loss_share"]["0.1"],
                        **record["gradients"],
                    )
                )
        label = f"{arm} [{seed}]"
        dashboard["models"][fold][label] = reference(folder / f"seed{seed}_tm0_pair_result.json")
        dashboard["checkpoints"][fold][label] = reference(folder / "refit_final.pt")
        dashboard["traces"][fold][label] = dict(
            calibration=[reference(p) for p in cal_refs], refit=[reference(p) for p in refit_refs]
        )
        dashboard["controlled_models"][fold][label] = dict(arm=arm, seed=seed)
        dashboard["controlled_telemetry"][fold][label] = {
            stage: reference(folder / f"gradient_batches_{stage}.csv")
            for stage in ("calibration", "refit")
        }
        audits[name]["runtime"] = runtime
    # Matched initialization checks at seed123 use its own control, never seed42.
    for (fold, seed, arm), result in results.items():
        if (fold, seed, "C0") in results and result["initial_hashes"][0] != results[
            fold, seed, "C0"
        ]["initial_hashes"][0]:
            raise ValueError("TA011_SAME_SEED_INITIALIZATION_MISMATCH")
    metric_rows = []
    daily_rows = []
    by_origin_rows = []
    tail_rows = []
    monthly_rows = []
    deltas = []
    comparisons = []
    intervals = {}
    for (fold, seed, arm), frame in frames.items():
        stats = summary(frame)
        result = results[fold, seed, arm]
        duration = audits.get(f"TA011-{arm}-S{seed}-{fold}", {}).get("runtime", {})
        metric_rows.append(
            dict(
                fold=fold,
                seed=seed,
                arm=arm,
                **{k: v for k, v in stats.items() if k not in {"daily", "by_origin"}},
                selected_epoch=result["selector"]["selected"],
                calibration_epochs=result["selector"]["epoch"],
                G6=result.get("G6_both_pass", {}).get("status", result["G6"]),
                fit_seconds=duration.get("neural_fitting_seconds"),
                worker_seconds=duration.get("seconds", {}).get("total_end_to_end_worker"),
                constant_forecast_origins=int(
                    sum(g.score.nunique() == 1 for _, g in frame.groupby(["session", "origin"]))
                ),
                finite_scores=len(frame),
            )
        )
        daily_rows.extend(
            dict(fold=fold, seed=seed, arm=arm, **r) for r in stats["daily"].to_dict("records")
        )
        by_origin_rows.extend(
            dict(fold=fold, seed=seed, arm=arm, **r) for r in stats["by_origin"].to_dict("records")
        )
        concentration = session_concentration(
            stats["daily"].session.tolist(), stats["daily"].MSE.to_numpy()
        )
        tail_rows.append(
            dict(
                fold=fold,
                seed=seed,
                arm=arm,
                max_abs_TG0=float(frame.TG0.abs().max()),
                fraction_abs_gt10=float((frame.TG0.abs() > 10).mean()),
                fraction_abs_gt20=float((frame.TG0.abs() > 20).mean()),
                scope="OUTER_DEVELOPMENT",
                concentration=json.dumps(concentration, sort_keys=True),
            )
        )
        training_records = result["refit_train_evaluation"].get("origin_records")
        if training_records:
            train = records_frame(training_records, arm, fold, "Refit training")
        else:
            prior = pd.read_csv(dashboard["baseline"]["path"], float_precision="round_trip")
            train = prior.loc[prior.partition == "refit"].copy()
            train["score"] = train.TM0
        train["squared_error"] = (train.score - train.TG0) ** 2
        train_stats = summary(train)
        train_concentration = session_concentration(
            train_stats["daily"].session.tolist(), train_stats["daily"].MSE.to_numpy()
        )
        tail_rows.append(
            dict(
                fold=fold,
                seed=seed,
                arm=arm,
                scope="FINAL_REFIT_TRAIN_DROPOUT_OFF",
                max_abs_TG0=float(train.TG0.abs().max()),
                fraction_abs_gt10=float((train.TG0.abs() > 10).mean()),
                fraction_abs_gt20=float((train.TG0.abs() > 20).mean()),
                concentration=json.dumps(train_concentration, sort_keys=True),
            )
        )
        for month, g in stats["daily"].groupby(stats["daily"].session.str[:7]):
            monthly_rows.append(
                dict(
                    fold=fold,
                    seed=seed,
                    arm=arm,
                    month=month,
                    MSE=float(g.MSE.mean()),
                    daily_Rank_IC=float(g.IC.mean()),
                    days=len(g),
                )
            )
        if arm == "C0":
            continue
        if (fold, seed, "C0") not in frames:
            raise ValueError("TA011_MATCHED_SEED_CONTROL_MISSING")
        control = frames[fold, seed, "C0"]
        matched(frame, control)
        base = summary(control)["daily"]
        paired = stats["daily"].merge(
            base, on="session", suffixes=("_arm", "_C0"), validate="one_to_one"
        )
        paired["delta_MSE"] = paired.MSE_arm - paired.MSE_C0
        paired["delta_IC"] = paired.IC_arm - paired.IC_C0
        deltas.extend(dict(fold=fold, seed=seed, arm=arm, **r) for r in paired.to_dict("records"))
        calendar = schedule(str(paired.session.min()), str(paired.session.max()))
        dates = {pd.Timestamp(day).date().isoformat(): i for i, day in enumerate(calendar.index)}
        positions = np.asarray([dates[day] for day in paired.session])
        key = f"{fold}:{seed}:{arm}"
        intervals[key] = {
            metric: paired_blocks(paired[metric].to_numpy(), positions, 5)
            for metric in ("delta_MSE", "delta_IC")
        }
        comparisons.append(
            dict(
                fold=fold,
                seed=seed,
                arm=arm,
                delta_MSE=float(paired.delta_MSE.mean()),
                delta_daily_IC=float(paired.delta_IC.mean()),
                MSE_interval_low=intervals[key]["delta_MSE"].get("percentile95", [None, None])[0],
                MSE_interval_high=intervals[key]["delta_MSE"].get("percentile95", [None, None])[1],
                IC_interval_low=intervals[key]["delta_IC"].get("percentile95", [None, None])[0],
                IC_interval_high=intervals[key]["delta_IC"].get("percentile95", [None, None])[1],
                days=len(paired),
                health=metric_rows[-1]["G6"],
            )
        )
    predictions = pd.concat(list(frames.values()), ignore_index=True)
    predictions["evidence_grade"] = "ASSUMPTION_CONDITIONAL_EXPLORATORY_DEVELOPMENT"
    predictions.rename(
        columns={"score": "canonical_predicted_TG0", "TG0": "observed_canonical_TG0"}
    ).to_csv(out / "predictions_long.csv", index=False)
    tables = {
        "experiment_registry": registry,
        "model_metrics": metric_rows,
        "metrics_daily": daily_rows,
        "metrics_by_origin": by_origin_rows,
        "metrics_by_month": monthly_rows,
        "metrics_by_epoch": epoch_rows,
        "gradient_log_pointers": pointers,
        "target_tail_parameters": parameters,
        "per_day_differences": deltas,
        "paired_fold_seed_comparison": comparisons,
        "target_tail_and_clipping": gradient_rows,
        "canonical_target_tail_and_loss": tail_rows,
    }
    for name, rows in tables.items():
        pd.DataFrame(rows).to_csv(out / (name + ".csv"), index=False)
    if comparisons:
        comparison_frame = pd.DataFrame(comparisons)
        for groups, filename in (
            (["arm"], "seed_temporal_variability.csv"),
            (["arm", "fold"], "seed_variability_within_fold.csv"),
            (["arm", "seed"], "temporal_variability_within_seed.csv"),
        ):
            variability = comparison_frame.groupby(groups)[["delta_MSE", "delta_daily_IC"]].agg(
                ["count", "mean", "std", "min", "max"]
            )
            variability.columns = [f"{metric}_{stat}" for metric, stat in variability.columns]
            variability.reset_index().to_csv(out / filename, index=False)
        daily_frame = pd.DataFrame(deltas)
        daily_frame["month"] = daily_frame.session.str[:7]
        daily_frame.groupby(["fold", "seed", "arm", "month"])[
            ["delta_MSE", "delta_IC"]
        ].mean().to_csv(out / "monthly_paired_differences.csv")
    model_grid = pd.DataFrame(metric_rows).pivot(
        index=["arm", "seed"], columns="fold", values=["MSE", "daily_Rank_IC"]
    )
    model_grid.columns = [f"{metric}_{fold}" for metric, fold in model_grid.columns]
    model_grid.reset_index().to_csv(out / "model_by_fold.csv", index=False)
    # ZERO retains identical outcomes at each fold; no fitted model or seed is invented.
    zero_rows = []
    for fold in ("WF1", "WF2"):
        zero = frames[fold, 42, "C0"].copy()
        zero["score"] = 0.0
        zero["squared_error"] = zero.TG0**2
        stats = summary(zero)
        zero_rows.append(
            dict(
                fold=fold,
                model="ZERO",
                MSE=stats["MSE"],
                daily_Rank_IC=stats["daily_Rank_IC"],
                sessions=stats["days"],
                origins=stats["origins"],
            )
        )
    pd.DataFrame(zero_rows).to_csv(out / "zero_context.csv", index=False)
    # Reuse historical baseline results only; M1 is an uncalibrated ranking score.
    context_path = Path(
        "reports/data_audit/ta007_multimodel_firstpass_2026-10-15_010008/matched_metrics.json"
    )
    preserved = json.loads((out / "preservation_before.json").read_text())
    if digest(context_path) != preserved[str(context_path)]:
        raise ValueError("TA011_HISTORICAL_BASELINE_CONTEXT_CHANGED")
    historical = json.loads(context_path.read_text())
    context_rows = []
    for model in ("ZERO", "M1", "RIDGE_OWN_112", "RIDGE_MARKET_147"):
        item = historical[model]
        context_rows.append(
            dict(
                fold="WF1",
                model=model,
                MSE=item["MSE"] if model != "M1" else None,
                daily_Rank_IC=item["daily_Rank_IC"],
                origins=item["origins"],
                sessions=item["sessions"],
                score_scale="UNCALIBRATED_RANKING_SCORE_NO_MSE_COMPARISON"
                if model == "M1"
                else "TG0",
                source=str(context_path),
                source_sha256=digest(context_path),
                new_fits=0,
            )
        )
    context_rows.append(dict(**zero_rows[1], score_scale="TG0", new_fits=0))
    pd.DataFrame(context_rows).to_csv(out / "historical_baseline_context.csv", index=False)
    judgments = {}
    for arm in ("H1", "T1", "T2", "O1"):
        cells = [r for r in comparisons if r["arm"] == arm]
        favorable = sum(r["delta_MSE"] <= 0 and r["delta_daily_IC"] > 0 for r in cells)
        broad = len(cells) == 4 and favorable == 4
        # Zero-spanning exploratory intervals or health failures prevent support; retain warnings.
        supported = broad and all(
            not str(r["health"]).startswith("FAIL")
            and r["IC_interval_low"] is not None
            and r["IC_interval_low"] > 0
            for r in cells
        )
        judgments[arm] = dict(
            status="MECHANISM_SUPPORTED_EXPLORATORY" if supported else "MIXED_OR_INCONCLUSIVE",
            available_cells=len(cells),
            directionally_favorable_cells=favorable,
            valid_poor_score_is_not_invalid=True,
        )
    started = sum(r["status"] == "STARTED" for r in journal)
    completed = sum(r["status"] == "COMPLETED" for r in journal)
    status = (
        "TA011_CONTROLLED_BATCH_COMPLETED"
        if started == completed == 18
        else "TA011_CONTROLLED_BATCH_PARTIAL"
        if started
        else "TA011_AWAITING_APPROVAL"
    )
    dashboard["compatibility_amendment"] = "TA011_ADDITIVE_CANONICAL_SCORE_ADAPTER_v1"
    dashboard["global_started_at_seal"] = 6 + started
    dashboard["controlled_package"] = dict(
        path=str(out),
        status=status,
        proposal_sha256=digest(plan_path),
    )
    for name in dashboard["readers"]:
        dashboard["readers"][name] = digest(Path(name))
    # Include the additive adapter itself in the read-only provenance contract.
    for name in ("loaders.py", "figures.py"):
        source = Path("src/lstm_data/visualization") / name
        dashboard["readers"][str(source)] = digest(source)
    atomic_replace_json(Path("configs/track_a_visualization_v1.json"), dashboard)
    write_json(out / "checkpoint_metadata_audit.json", dict(checkpoints=metadata))
    write_json(out / "batch_and_lifecycle_audit.json", audits)
    write_json(
        out / "exploratory_paired_intervals.json",
        dict(
            intervals=intervals,
            limitations=CAVEAT
            + (
                " Moving 5-session blocks never bridge omitted exchange days. "
                "No selection adjustment or decisive p-values."
            ),
        ),
    )
    value = dict(
        status=status,
        opening_started=6,
        new_started=started,
        new_completed=completed,
        global_started=6 + started,
        ceiling=40,
        judgments=judgments,
        zero=zero_rows,
        comparisons=comparisons,
        qualifications=CAVEAT,
    )
    write_json(out / "review_summary.json", value)
    return value


def verify_tables(out: Path) -> dict:
    """Recompute sealed canonical metrics from compact saved scores, with no writes or fits."""
    from .pretraining_policy import verify_ref

    binding = json.loads((out / "artifact_bindings.json").read_text())
    for ref in binding["artifacts"]:
        verify_ref(Path.cwd(), ref)
    predictions = pd.read_csv(out / "predictions_long.csv", float_precision="round_trip")
    metrics = pd.read_csv(out / "model_metrics.csv", float_precision="round_trip")
    count = 0
    for (fold, seed, arm), group in predictions.groupby(["fold", "seed", "arm"]):
        frame = group.rename(
            columns={"canonical_predicted_TG0": "score", "observed_canonical_TG0": "TG0"}
        )
        frame["squared_error"] = (frame.score - frame.TG0) ** 2
        frame = finish_frame(frame, str(arm), int(group.seed.iloc[0]), str(fold))
        stats = summary(frame)
        expected = metrics.loc[
            (metrics.fold == fold) & (metrics.seed == seed) & (metrics.arm == arm)
        ]
        if (
            len(expected) != 1
            or not math.isclose(
                stats["MSE"], float(expected.MSE.iloc[0]), rel_tol=1e-13, abs_tol=1e-13
            )
            or not math.isclose(
                stats["daily_Rank_IC"],
                float(expected.daily_Rank_IC.iloc[0]),
                rel_tol=1e-13,
                abs_tol=1e-13,
            )
        ):
            raise ValueError("TA011_SEALED_METRIC_RECOMPUTATION_MISMATCH")
        count += 1
    return dict(
        status="READ_ONLY_RECOMPUTATION_MATCH",
        model_panels=count,
        forecasts=len(predictions),
        optimizer_steps=0,
        confirmation_numeric_rows=0,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    value = verify_tables(args.output) if args.verify_only else review(args.output, args.plan)
    print(json.dumps(value, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
