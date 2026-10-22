"""Read-only Package017 stage audits and exactly matched two-seed diagnostics."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .calendar import schedule
from .config import write_json
from .controlled_loss import LossPolicy
from .four_model_diagnostics import paired_blocks
from .hf20_diagnostic_math import day_weights, selection_trace, weighted_decomposition
from .hf20_postrun_diagnostics import matched_audit, tail_study, target_panel
from .hf20_replication_authority import IDS, code_binding, read_rows
from .hf20_source import SYMBOLS
from .hf20_training_authority import reference
from .hf20_training_data import TrainingView, load_views, target_values
from .hf20_training_review import origin_metrics
from .hf20_training_run import reload_checkpoint, scores
from .neural_lifecycle import EarlyStop, epoch_pass, state_hash
from .visualization.hf20 import handoff, table, verified

KEYS = [
    "session",
    "origin",
    "symbol",
    "symbol_index",
    "source_key",
    "target",
    "day_index",
    "forecast_cutoff_UTC",
    "forecast_issuance_UTC",
    "entry_proxy_reference_UTC",
    "exit_proxy_reference_UTC",
    "label_maturity_UTC",
    "preparation_id",
    "recipe_id",
    "target_id",
]


def matched_frames(first: pd.DataFrame, second: pd.DataFrame) -> None:
    """No intersection/attrition: all four models must retain the exact same original keys."""
    for f in (first, second):
        if (
            len(f) != 7320
            or f.session.min() < "2025-03-31"
            or f.session.max() > "2026-01-06"
            or f.session.nunique() != 183
            or f.source_key.duplicated().any()
            or len(f[["session", "origin"]].drop_duplicates()) != 366
        ):
            raise ValueError("P017_EXACT_DEVELOPMENT_MASK_REQUIRED")
        for _, g in f.groupby(["session", "origin"], sort=False):
            if tuple(g.symbol) != SYMBOLS or not np.array_equal(g.symbol_index, np.arange(20)):
                raise ValueError("P017_FIXED_STOCK_ORDER_REQUIRED")
    if not first[KEYS].equals(second[KEYS]):
        raise ValueError("P017_EXACT_KEYS_REQUIRED_NO_INTERSECTION")


def expected_binding(p: dict, r: dict, arm: str, stage: str) -> dict:
    if stage not in ("CALIBRATION_SELECTED", "REFIT_FINAL"):
        raise ValueError("P017_WRONG_CHECKPOINT_STAGE")
    split = "inner_train" if stage == "CALIBRATION_SELECTED" else "refit"
    return dict(
        run_id=IDS[0 if arm == "C0" else 1],
        architecture="TM0",
        parameters=6433,
        seed=123,
        input_contract=p["input_contract"],
        preparation_id=p["views"][split]["preparation_id"],
        source_revision=p["source_revision"],
        symbols=list(SYMBOLS),
        feature_id=p["feature_id"],
        target_id=p["target_id"],
        clock_id=p["clock_id"],
        code_sha256=p["code_sha256"],
        plan=r["plan"],
        selected_epoch=r["selection"]["selected"],
        arm=arm,
        inverse="SCALE_TIMES_SINH_ONCE" if arm == "T2" else "IDENTITY",
        checkpoint_outputs="LOGITS",
        stage=stage,
        recipe_id=p["views"][split]["recipe_id"],
        scale=p["scales"][split] if arm == "T2" else None,
    )


def audit_run(out: Path, run_id: str) -> dict:
    """Validate a completed run and replay selected validation/refit forecasts without updates."""
    tick = time.monotonic()
    if run_id not in IDS:
        raise ValueError("P017_WRONG_AUDIT_SEED")
    p = json.loads((out / "experiment_design.json").read_text())
    if p["code"] != code_binding():
        raise ValueError("P017_STALE_TRAINING_CODE")
    views = load_views(Path(p["input_contract"]["path"]))
    if {k: v.summary() for k, v in views.items()} != p["views"]:
        raise ValueError("P017_CHANGED_INPUT_MASK")
    directory = out / run_id
    r = json.loads((directory / "run_result.json").read_text())
    arm = "C0" if run_id == IDS[0] else "T2"
    if (
        r["status"] != "COMPLETED"
        or r["seed"] != 123
        or r["run_id"] != run_id
        or r["input_contract"] != p["input_contract"]
        or r["views"] != p["views"]
        or r["scales"] != p["scales"]
        or r["plan"] != reference(out / "experiment_design.json")
        or r["inverse_count"] != int(arm == "T2")
        or r["heldout_numeric_rows"] != 0
        or r["score_units"] != "CANONICAL_TG20"
        or not r["reload_exact"]
    ):
        raise ValueError("P017_RUN_BINDING_CHANGED")
    e = json.loads((directory / "epoch_records.json").read_text())
    selector = EarlyStop()
    for row in e["calibration"]:
        if selector.observe(row["validation_MSE"]) != row["qualifying"]:
            raise ValueError("P017_QUALIFYING_SELECTION_CHANGED")
        if row["optimizer_steps"] != math.ceil(len(views["inner_train"].sessions) / 16):
            raise ValueError("P017_CALIBRATION_UPDATES_CHANGED")
    if (
        vars(selector) != r["selection"]
        or len(e["refit"]) != selector.selected
        or selector.status == "CALIBRATING"
        or not r["fresh_optimizer"]
        or r["initial_hash"] != r["fresh_initial_hash"]
        or r["refit_steps"] != selector.selected * math.ceil(len(views["refit"].sessions) / 16)
    ):
        raise ValueError("P017_D6G_FRESH_REFIT_CHANGED")
    scales = {
        s: max(float(np.median(np.abs(target_values(views[s]).astype(float)))), 1e-6)
        for s in ("inner_train", "refit")
    }
    if scales != {s: p["scales"][s]["scale"] for s in scales}:
        raise ValueError("P017_INDEPENDENT_TRAIN_ONLY_SCALE_CHANGED")
    torch.set_num_threads(1)
    checked = []
    for key, stage, split, stem in (
        ("calibration_checkpoint", "CALIBRATION_SELECTED", "inner_train", "calibration_selected"),
        ("refit_checkpoint", "REFIT_FINAL", "refit", "refit_final"),
    ):
        expected = expected_binding(p, r, arm, stage)
        manifest = json.loads((directory / (stem + ".manifest.json")).read_text())
        if manifest != r[key] or manifest["binding"] != expected:
            raise ValueError("P017_WRONG_SEED_STAGE_TARGET_INVERSE")
        loaded = reload_checkpoint(directory / (stem + ".pt"), expected, manifest)
        before = state_hash(loaded)
        policy = LossPolicy(arm, scale=scales[split] if arm == "T2" else 1.0)
        if stage == "CALIBRATION_SELECTED":
            actual = epoch_pass(
                loaded, views["inner_validation"], selector.selected, 123, policy=policy
            )
            if selector.best is None or not np.isclose(
                actual["mean_session_mse"], selector.best, atol=2e-12, rtol=0
            ):
                raise ValueError("P017_SELECTED_VALIDATION_REPLAY_DIFFERS")
        else:
            actual_scores = scores(loaded, views["development"], policy)
            saved = pd.read_csv(
                directory / "predictions_development.csv", float_precision="round_trip"
            )
            matched_frames(actual_scores, saved)
            if not np.array_equal(actual_scores.score, saved.score):
                raise ValueError("P017_CANONICAL_SCORE_REPLAY_NOT_EXACT")
        if before != state_hash(loaded) or any(
            param.grad is not None for param in loaded.parameters()
        ):
            raise ValueError("P017_READONLY_AUDIT_MUTATED_MODEL")
        checked.append(dict(stage=stage, checkpoint=manifest["checkpoint"], exact_eval_replay=True))
    receipt = dict(
        status="PASS",
        run_id=run_id,
        scales=scales,
        checkpoints=checked,
        selection=vars(selector),
        optimizer_steps=0,
        heldout_numeric_rows=0,
        seconds=time.monotonic() - tick,
    )
    write_json(directory / "independent_postrun_audit.json", receipt)
    return receipt


def stage_tables(
    directory: Path, seed: int, ids: tuple[str, str]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    traces, gradients = [], []
    for arm, name in zip(("C0", "T2"), ids):
        d = directory / name
        e = json.loads((d / "epoch_records.json").read_text())
        trace = selection_trace([r["validation_MSE"] for r in e["calibration"]])
        trace["seed"], trace["arm"] = seed, arm
        trace["optimizer_objective"] = [r["optimizer_objective"] for r in e["calibration"]]
        traces.append(trace)
        batches = pd.read_csv(d / "batch_telemetry.csv", float_precision="round_trip")
        for stage in ("calibration", "refit"):
            for row in e[stage]:
                norms = batches.loc[
                    batches.stage.eq(stage) & batches.epoch.eq(row["epoch"]), "preclip_norm"
                ].to_numpy(dtype=float)
                if (
                    not len(norms)
                    or not np.isfinite(norms).all()
                    or row["gradients"]["nonfinite_count"]
                ):
                    raise ValueError("P017_NONFINITE_GRADIENTS")
                gradients.append(
                    dict(
                        seed=seed,
                        arm=arm,
                        stage=stage,
                        epoch=row["epoch"],
                        updates=len(norms),
                        p50=float(np.median(norms)),
                        p90=float(np.quantile(norms, 0.9)),
                        p99=float(np.quantile(norms, 0.99)),
                        maximum=float(norms.max()),
                        actual_clipped_fraction=float(np.mean(norms + 1e-6 > 1)),
                        nonfinite_count=0,
                        optimizer_objective=row["optimizer_objective"],
                        canonical_online_training_MSE_dropout_ON=row["mean_session_mse"],
                        optimizer_units="TG20_SQUARED"
                        if arm == "C0"
                        else "ASINH_TG20_OVER_S_SQUARED",
                    )
                )
    return pd.concat(traces, ignore_index=True), pd.DataFrame(gradients)


def summarize(f: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    records = [
        dict(session=day, origin=o, arm=arm, **origin_metrics(g, arm))
        for (day, o), g in f.groupby(["session", "origin"], sort=True)
        for arm in ("C0", "T2", "ZERO")
    ]
    origins = pd.DataFrame(records)
    fields = [
        "MSE",
        "MAE",
        "Rank_IC",
        "relative_sign_accuracy",
        "pairwise_concordance",
        "score_std",
    ]
    daily = origins.groupby(["session", "arm"])[fields].mean().reset_index()
    metrics = daily.groupby("arm")[fields].mean().reset_index()
    metrics["sessions"], metrics["origins"], metrics["stock_rows"] = 183, 366, 7320
    return origins, daily, metrics


def stock_diagnostics(f: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Separate temporal stock correlation from additive contributions to cross-sectional IC."""
    records = []
    for arm in ("C0", "T2"):
        values = f.copy()
        values["squared_error"] = (values[arm] - values.target) ** 2
        values["IC_contribution"] = np.nan
        values["rank_error"] = np.nan
        for _, g in values.groupby(["session", "origin"], sort=False):
            a = g[arm].rank(method="average").to_numpy(dtype=float)
            b = g.target.rank(method="average").to_numpy(dtype=float)
            a, b = a - a.mean(), b - b.mean()
            denominator = float(np.sqrt((a @ a) * (b @ b)))
            if denominator > 0:
                values.loc[g.index, "IC_contribution"] = a * b / denominator
            values.loc[g.index, "rank_error"] = np.abs(a - b)
        for symbol, g in values.groupby("symbol", sort=False):
            temporal_a = g[arm].rank(method="average").to_numpy(dtype=float)
            temporal_b = g.target.rank(method="average").to_numpy(dtype=float)
            temporal_ic = float(np.corrcoef(temporal_a, temporal_b)[0, 1])
            daily = g.groupby("session")[["squared_error", "IC_contribution", "rank_error"]].mean()
            records.append(
                dict(
                    seed=seed,
                    arm=arm,
                    symbol=symbol,
                    MSE=float(daily.squared_error.mean()),
                    cross_sectional_IC_contribution=float(daily.IC_contribution.mean()),
                    rank_MAE=float(daily.rank_error.mean()),
                    temporal_Spearman_NOT_cross_sectional_IC=temporal_ic,
                )
            )
    return pd.DataFrame(records)


def review(out: Path) -> dict:
    tick = time.monotonic()
    if (out / "visualization_handoff.json").exists():
        raise ValueError("P017_FINAL_RESULT_ALREADY_PUBLISHED")
    p = json.loads((out / "experiment_design.json").read_text())
    journal = read_rows()
    if [r["run_id"] for r in journal if r["status"] == "COMPLETED"] != list(IDS):
        raise ValueError("P017_BOTH_COMPLETED_REQUIRED")
    root = Path.cwd()
    old_h = handoff(root, 42)
    first = table(root, old_h, "matched_predictions_development.csv")
    frames = []
    for name in IDS:
        d = out / name
        a = json.loads((d / "independent_postrun_audit.json").read_text())
        if a["status"] != "PASS" or a["run_id"] != name:
            raise ValueError("P017_POSTRUN_AUDIT_REQUIRED")
        frame = pd.read_csv(d / "predictions_development.csv", float_precision="round_trip")
        if not frame.seed.eq(123).all() or not frame.run_id.eq(name).all():
            raise ValueError("P017_FORECAST_SEED_ID_CHANGED")
        matched_frames(first, frame)
        frames.append(frame)
    f = first.copy()
    for arm, frame in zip(("C0", "T2"), frames):
        f[arm] = frame.score
        f[arm + "_residual"] = f[arm] - f.target
        f[arm + "_absolute_error"] = f[arm + "_residual"].abs()
        f[arm + "_squared_error"] = f[arm + "_residual"] ** 2
    f.to_csv(out / "matched_predictions_development.csv", index=False)
    origins, daily, metrics = summarize(f)
    metrics.to_csv(out / "matched_metrics.csv", index=False)
    origins.to_csv(out / "per_origin_metrics.csv", index=False)
    daily.to_csv(out / "daily_metrics.csv", index=False)
    daily.assign(month=daily.session.str[:7]).groupby(["month", "arm"]).mean(
        numeric_only=True
    ).reset_index().to_csv(out / "monthly_metrics.csv", index=False)
    views = load_views(Path(p["input_contract"]["path"]))
    c = json.loads(verified(root, p["input_contract"]).read_text())
    if {k: v.summary() for k, v in views.items()} != p["views"]:
        raise ValueError("P017_FINAL_MASK_CHANGED")
    if not np.array_equal(
        target_values(views["development"]).reshape(-1), f.target.to_numpy(dtype=np.float32)
    ):
        raise ValueError("P017_CANONICAL_TARGET_MISMATCH")
    recipes = json.loads(verified(root, c["recipes"]).read_text())
    with np.load(verified(root, c["targets"]), allow_pickle=False) as labels:
        panels = {
            s: target_panel(
                views[s],
                dict(returns=labels["returns"]),
                recipes["inner" if s.startswith("inner") else "refit"]["epsilon"],
                s,
            )
            for s in ("inner_train", "refit", "development")
        }
    threshold = float(np.quantile(panels["refit"].target.abs(), 0.99))
    diagnostics = matched_audit(f, out, threshold)
    for key, value in diagnostics.items():
        if isinstance(value, pd.DataFrame):
            value.to_csv(out / ("diagnostic_" + key + ".csv"), index=False)
    tails = tail_study(panels, f)
    for key, value in tails.items():
        if isinstance(value, pd.DataFrame):
            value.to_csv(out / ("tail_" + key + ".csv"), index=False)
    write_json(out / "tail_thresholds.json", tails["thresholds"])
    stock_groups = diagnostics["groups"]
    if not isinstance(stock_groups, pd.DataFrame):
        raise TypeError("P017_GROUP_TABLE_REQUIRED")
    stock_groups.loc[stock_groups.group_kind.eq("symbol")].rename(
        columns={"group": "symbol"}
    ).to_csv(out / "per_stock_metrics.csv", index=False)
    paired_analysis(out, first, f, old_h, views)
    # Alias concise canonical filenames for the viewer; each is an aggregate table, no tensors.
    for source, target in (
        ("diagnostic_decomposition.csv", "mse_decomposition.csv"),
        ("tail_events.csv", "tail_event_metrics.csv"),
    ):
        (out / target).write_bytes((out / source).read_bytes())
    from .hf20_replication_report import write_reports

    write_reports(out, first, f, threshold)
    h = {
        k: p[k]
        for k in (
            "runs",
            "source_revision",
            "symbols",
            "feature_id",
            "target_id",
            "clock_id",
            "scales",
            "input_contract",
        )
    }
    example = f.iloc[int(np.argmax(np.abs(f.target.to_numpy(dtype=float))))]
    h.update(
        seed=123,
        preparation_id=c["preparation_id"],
        score_units="CANONICAL_TG20",
        T2_saved_inverse_count=1,
        heldout_numeric_rows=0,
        global_started_pairs=32,
        train_target_abs_q99=threshold,
        artifacts={path.name: reference(path) for path in out.glob("*.csv")},
        researcher_diagnosis=reference(out / "researcher_diagnosis.md"),
        example=dict(
            symbol=str(example.symbol),
            session=str(example.session),
            origin=int(example.origin),
        ),
        run_artifacts={
            arm: dict(
                run_result=reference(out / name / "run_result.json"),
                runtime=reference(out / name / "training_actual_runtime.json"),
                calibration=reference(out / name / "calibration_epochs.csv"),
                refit=reference(out / name / "refit_epochs.csv"),
            )
            for arm, name in zip(("C0", "T2"), IDS)
        },
    )
    write_json(out / "visualization_handoff.json", h)
    config = Path("configs/track_a_hf20_replication_visualization_v1.json")
    if config.exists():
        raise ValueError("P017_VIEWER_RELEASE_EXISTS")
    write_json(config, dict(handoff=reference(out / "visualization_handoff.json")))
    write_json(
        out / "review_actual_runtime.json",
        dict(
            seconds=time.monotonic() - tick,
            optimizer_steps=0,
            heldout_numeric_rows=0,
            source_requests=0,
        ),
    )
    return dict(status="COMPLETED_EXPLORATORY", metrics=metrics.to_dict("records"))


def paired_analysis(
    out: Path,
    first: pd.DataFrame,
    second: pd.DataFrame,
    old_h: dict,
    views: dict[str, TrainingView],
) -> None:
    """Compare seeds on complete sessions; preserve gaps in block resampling."""
    from .hf20_training_authority import IDS as OLD_IDS

    old_directory = Path(old_h["run_artifacts"]["C0"]["run_result"]["path"]).parent.parent
    all_daily, all_metrics, traces, gradients, decompositions = [], [], [], [], []
    for seed, f, directory, ids in ((42, first, old_directory, OLD_IDS), (123, second, out, IDS)):
        _, daily, metrics = summarize(f)
        daily["seed"], metrics["seed"] = seed, seed
        all_daily.append(daily)
        all_metrics.append(metrics)
        trace, gradient = stage_tables(directory, seed, ids)
        traces.append(trace)
        gradients.append(gradient)
        for arm in ("C0", "T2", "ZERO"):
            decompositions.append(
                dict(
                    seed=seed,
                    arm=arm,
                    **weighted_decomposition(
                        f.target.to_numpy(), f[arm].to_numpy(), day_weights(f)
                    ),
                )
            )
    pd.concat(all_metrics).to_csv(out / "four_model_metrics.csv", index=False)
    pd.concat(all_daily).to_csv(out / "four_model_daily_metrics.csv", index=False)
    pd.concat([stock_diagnostics(first, 42), stock_diagnostics(second, 123)]).to_csv(
        out / "four_model_stock_diagnostics.csv", index=False
    )
    pd.DataFrame(decompositions).to_csv(out / "four_model_mse_decomposition.csv", index=False)
    pd.concat(traces).to_csv(out / "epoch_selection_trace.csv", index=False)
    pd.concat(gradients).to_csv(out / "epoch_gradient_telemetry.csv", index=False)
    days = pd.concat(all_daily).pivot(
        index="session", columns=["seed", "arm"], values=["MSE", "Rank_IC"]
    )
    calendar = schedule(str(days.index.min()), str(days.index.max()))
    positions = {d: i for i, d in enumerate(pd.DatetimeIndex(calendar.index).strftime("%Y-%m-%d"))}
    pos = np.asarray([positions[d] for d in days.index])
    contrasts, paired = [], pd.DataFrame(dict(session=days.index))
    for label, left, right in (
        ("S123_T2_minus_C0", (123, "T2"), (123, "C0")),
        ("S42_T2_minus_C0", (42, "T2"), (42, "C0")),
        ("C0_S123_minus_S42", (123, "C0"), (42, "C0")),
        ("T2_S123_minus_S42", (123, "T2"), (42, "T2")),
    ):
        for metric in ("MSE", "Rank_IC"):
            values = (days[(metric, *left)] - days[(metric, *right)]).to_numpy(dtype=float)
            interval = paired_blocks(values, pos, 5)
            contrasts.append(
                {
                    **interval,
                    "contrast": label,
                    "metric": metric,
                    "estimate": float(values.mean()),
                    "lower95": interval["percentile95"][0],
                    "upper95": interval["percentile95"][1],
                    "status": "EXPLORATORY_NOT_G8_NOT_SELECTION_ADJUSTED",
                }
            )
            paired[label + "_" + metric] = values
    pd.DataFrame(contrasts).to_csv(out / "paired_intervals.csv", index=False)
    paired.to_csv(out / "four_model_paired_daily_contrasts.csv", index=False)
    disagreements = second[KEYS].copy()
    for arm in ("C0", "T2"):
        disagreements[arm + "_seed42"] = first[arm]
        disagreements[arm + "_seed123"] = second[arm]
        disagreements[arm + "_absolute_difference"] = (second[arm] - first[arm]).abs()
        rank42 = first.groupby(["session", "origin"])[arm].rank(method="average")
        rank123 = second.groupby(["session", "origin"])[arm].rank(method="average")
        disagreements[arm + "_rank_difference"] = (rank123 - rank42).abs()
    disagreements[["source_key", "session", "origin", "symbol"]].to_csv(
        out / "exact_paired_forecast_ids.csv", index=False
    )
    fields = [c for c in disagreements if c.endswith("difference")]
    disagreements["month"] = disagreements.session.str[:7]
    # Outcome dispersion is explicit ex-post context, never an observable regime input.
    disagreements["expost_outcome_dispersion"] = first.cross_sectional_MAD
    for group in ("symbol", "month", "origin"):
        disagreements.groupby(group)[fields].mean().reset_index().to_csv(
            out / ("seed_disagreement_by_" + group + ".csv"), index=False
        )
    development_mad = float(first.cross_sectional_MAD.median())
    disagreements["expost_dispersion_bin"] = np.where(
        first.cross_sectional_MAD.ge(development_mad), "DEV_MEDIAN_OR_HIGHER", "BELOW_DEV_MEDIAN"
    )
    disagreements.groupby("expost_dispersion_bin")[fields].mean().reset_index().to_csv(
        out / "seed_disagreement_by_expost_dispersion.csv", index=False
    )
    from .hf20_features import COMMON

    channel = COMMON.index("V2")
    train_volatility = np.asarray(
        [
            np.median(views["refit"].source.common[int(r.last_step), :, channel])
            for r in views["refit"].source.rows.itertuples()
        ]
    )
    cut = float(np.median(train_volatility))
    volatility = {
        (str(r.session), int(r.origin)): float(
            np.median(views["development"].source.common[int(r.last_step), :, channel])
        )
        for r in views["development"].source.rows.itertuples()
    }
    disagreements["observed_current_V2_train_scaled_cross_stock_median"] = [
        volatility[(str(r.session), int(r.origin))] for r in disagreements.itertuples()
    ]
    disagreements["observed_V2_bin"] = np.where(
        disagreements.observed_current_V2_train_scaled_cross_stock_median.ge(cut),
        "AT_OR_ABOVE_TRAIN_MEDIAN",
        "BELOW_TRAIN_MEDIAN",
    )
    disagreements.groupby("observed_V2_bin")[fields].mean().reset_index().to_csv(
        out / "seed_disagreement_by_observed_volatility.csv", index=False
    )
    write_json(
        out / "observed_volatility_context.json",
        dict(
            feature="V2",
            statistic="Cross-stock median at actual final input step",
            units="SEALED_REFIT_TRAIN_SCALED_V2",
            training_only_median=cut,
            training_origins=len(train_volatility),
            development_origins=len(volatility),
            scope="DESCRIPTIVE_CONTEXT_ONLY_NOT_MODEL_PARAMETER_OR_CAUSAL_CLAIM",
        ),
    )
    threshold = float(np.quantile(np.abs(target_values(views["refit"])), 0.99))
    events = disagreements.loc[second.target.abs().ge(threshold)].copy()
    events.to_csv(out / "same_tail_event_seed_comparison.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--run-id", choices=IDS)
    args = parser.parse_args()
    result = audit_run(args.out, args.run_id) if args.run_id else review(args.out)
    print(json.dumps(result, allow_nan=True))


if __name__ == "__main__":
    main()
