"""Package016: bounded read-only HF20 diagnosis; no fitting or registry transitions."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .calendar import schedule
from .config import digest, now, write_json
from .controlled_loss import LossPolicy
from .four_model_diagnostics import paired_blocks
from .hf20_diagnostic_math import day_weights, quantiles, selection_trace, weighted_decomposition
from .hf20_features import COMMON, ORDER
from .hf20_source import REVISION, SYMBOLS
from .hf20_training_authority import IDS, code_binding, read_rows
from .hf20_training_data import TrainingView, load_views, target_values
from .hf20_training_review import origin_metrics
from .hf20_training_run import reload_checkpoint
from .neural_engine import SharedLSTM
from .neural_lifecycle import state_hash
from .visualization.hf20 import handoff, predictions, verified

TARGET = "TG20_HF20_CROSS_SECTIONAL_V1"
SPLITS = ("inner_train", "inner_validation", "refit", "development")


def guard_scope(split: str, start: str = "2022-06-01", end: str = "2026-01-06") -> None:
    """Reject protected numerical scope before opening any numerical application rows."""
    if split not in SPLITS or not "2022-06-01" <= start <= end < "2026-01-07":
        raise ValueError("P016_HELD_OUT_OR_UNREGISTERED_SCOPE_DENIED_BEFORE_IO")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def ref(path: Path) -> dict:
    return dict(path=str(path), sha256=digest(path), bytes=path.stat().st_size)


def validate_family(plan: dict, contract: dict) -> None:
    """Explicit actual family and preparation identities, independent of numerical loaders."""
    if (
        plan.get("source_revision") != REVISION
        or contract.get("source_revision") != REVISION
        or plan.get("target_id") != TARGET
        or contract.get("target_id") != TARGET
        or plan.get("symbols") != list(SYMBOLS)
        or contract.get("symbols") != list(SYMBOLS)
        or plan.get("runs") != list(IDS)
        or plan.get("feature_id") != "FT1_HF20_HOURLY_NATIVE_V2"
        or contract.get("feature_order") != list(ORDER)
        or not contract.get("preparation_id")
        or plan.get("heldout_access") is not False
        or contract.get("confirmation_locked") is not True
    ):
        raise ValueError("P016_EXACT_SOURCE_TARGET_ORDER_PREPARATION_REQUIRED")
    for k in ("feature_id", "clock_id"):
        if plan[k] != contract[k]:
            raise ValueError("P016_WRONG_INPUT_FAMILY")
    if any(
        v.get("preparation_id") != contract["preparation_id"]
        or v.get("recipe_id")
        != contract["recipe_ids"]["inner" if k.startswith("inner") else "refit"]
        for k, v in plan["views"].items()
    ):
        raise ValueError("P016_WRONG_INPUT_OR_RECIPE_ID")


def discover(
    report: Path | None,
) -> tuple[Path, dict, dict, dict, pd.DataFrame, dict[str, TrainingView]]:
    guard_scope("development")
    root = Path.cwd()
    pointer = read_json(Path("configs/CURRENT_EXPERIMENT_REGISTRY.json"))
    plan_path = verified(root, pointer["plan"])
    directory = plan_path.parent
    if report is not None and report.resolve() != directory.resolve():
        raise ValueError("P016_REPORT_NOT_CURRENT_LINKED_COMPLETED_STUDY")
    verified(root, pointer["definition"])
    plan = read_json(plan_path)
    if plan["code"] != code_binding():
        raise ValueError("P016_TRAINING_CODE_CHANGED")
    c = read_json(verified(root, plan["input_contract"]))
    validate_family(plan, c)
    rows = read_rows()
    if rows[-1]["global_started_pairs"] != 30 or [
        r["run_id"] for r in rows if r["status"] == "COMPLETED"
    ] != list(IDS):
        raise ValueError("P016_EXPECT_EXACT30_COMPLETED_PREFIX")
    h = handoff(root)
    _, f, _ = predictions(root, "2025-03-31", "2026-01-06", "AAPL", IDS[0])
    views = load_views(Path(plan["input_contract"]["path"]))
    if {k: v.summary() for k, v in views.items()} != plan["views"]:
        raise ValueError("P016_MASK_OR_INPUT_ID_MISMATCH_NO_INTERSECTION")
    actual = f[["session", "origin"]].drop_duplicates().to_numpy().tolist()
    expected = views["development"].source.rows[["session", "origin"]].to_numpy().tolist()
    if actual != expected:
        raise ValueError("P016_SAVED_DEVELOPMENT_MASK_DIFFERS")
    y = target_values(views["development"]).reshape(-1)
    if not np.array_equal(f.target.to_numpy(dtype=np.float32), y):
        raise ValueError("P016_TG20_TARGETS_CHANGED")
    for arm, name in zip(("C0", "T2"), IDS):
        run = read_json(verified(root, h["run_artifacts"][arm]["run_result"]))
        if (
            run["status"] != "COMPLETED"
            or run["plan"] != pointer["plan"]
            or run["input_contract"] != plan["input_contract"]
            or run["views"] != plan["views"]
            or run["scales"] != plan["scales"]
            or run["inverse_count"] != int(arm == "T2")
            or run["score_units"] != "CANONICAL_TG20"
        ):
            raise ValueError("P016_RUN_TARGET_SCALE_INPUT_BINDING_CHANGED")
        saved = pd.read_csv(
            directory / name / "predictions_development.csv", float_precision="round_trip"
        )
        if not np.array_equal(saved.score, f[arm]) or not np.array_equal(saved.target, f.target):
            raise ValueError("P016_SAVED_SCORE_INVERSE_ONCE_OR_TARGET_MISMATCH")
    return directory, plan, c, h, f, views


def epoch_audit(
    report: Path, views: dict[str, TrainingView]
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    traces = []
    health = []
    details = {}
    for arm, name in zip(("C0", "T2"), IDS):
        d = report / name
        e = read_json(d / "epoch_records.json")
        r = read_json(d / "run_result.json")
        trace = selection_trace([x["validation_MSE"] for x in e["calibration"]])
        if (
            int(trace.iloc[-1].selected_epoch) != r["selection"]["selected"]
            or int(trace.iloc[-1].raw_epoch) != r["selection"]["raw_epoch"]
        ):
            raise ValueError("P016_SELECTION_RECONSTRUCTION_DIFFERS")
        b = pd.read_csv(d / "batch_telemetry.csv", float_precision="round_trip")
        for i, record in enumerate(e["calibration"]):
            if bool(trace.iloc[i].qualifying) != record["qualifying"]:
                raise ValueError("P016_QUALIFYING_FLAG")
            trace.loc[i, "optimizer_objective"] = record["optimizer_objective"]
            trace.loc[i, "canonical_training_MSE_online_dropout_ON"] = record["mean_session_mse"]
            trace.loc[i, "train_optimizer_steps"] = record["optimizer_steps"]
            trace.loc[i, "train_sessions"] = record["sessions"]
            trace.loc[i, "validation_sessions"] = len(views["inner_validation"].sessions)
            trace.loc[i, "validation_origins"] = len(views["inner_validation"].source.rows)
            trace.loc[i, "training_score_std_online_dropout_ON"] = record["score_std"]
        trace["arm"] = arm
        trace["optimizer_units"] = "TG20_SQUARED" if arm == "C0" else "ASINH_TG20_OVER_S_SQUARED"
        trace["training_MSE_semantics"] = "ONLINE_CHANGING_WEIGHTS_DROPOUT_ON_NOT_END_EPOCH_EVAL"
        trace["lr"] = 0.001
        traces.append(trace)
        for stage in ("calibration", "refit"):
            for record in e[stage]:
                group = b.loc[b.stage.eq(stage) & b.epoch.eq(record["epoch"])]
                norms = group.preclip_norm.to_numpy(dtype=float)
                actual = float(np.mean(1 / (norms + 1e-6) < 1))
                if not np.isfinite(norms).all() or record["gradients"]["nonfinite_count"]:
                    raise ValueError("P016_NONFINITE_TELEMETRY")
                health.append(
                    dict(
                        arm=arm,
                        stage=stage,
                        epoch=record["epoch"],
                        updates=len(group),
                        p50=float(np.median(norms)),
                        p90=float(np.quantile(norms, 0.9)),
                        p99=float(np.quantile(norms, 0.99)),
                        maximum=float(norms.max()),
                        actual_clipped_fraction=actual,
                        nonfinite_count=0,
                        objective=record["optimizer_objective"],
                        canonical_online_MSE=record["mean_session_mse"],
                        target_abs_max=record["target_abs_max"],
                        target_abs_p99=record["target_abs_p99"],
                        top1pct_session_loss_share=record["loss_concentration"]["0.01"],
                        top5pct_session_loss_share=record["loss_concentration"]["0.05"],
                        selected_epoch=r["selection"]["selected"],
                        lr=0.001,
                        G6="WARN" if actual > 0.5 else "PASS_NO_SUSTAINED_CLIPPING",
                    )
                )
        details[arm] = dict(
            selection=r["selection"],
            health=r["health"],
            initial_hash=r["initial_hash"],
            fresh_initial_hash=r["fresh_initial_hash"],
            fresh_optimizer=r["fresh_optimizer"],
            runtime=read_json(d / "training_actual_runtime.json"),
        )
    cal = schedule("2022-12-01", "2025-03-28")
    tail = pd.DatetimeIndex(cal.index[-63:]).strftime("%Y-%m-%d").tolist()
    if tail[0] != "2024-12-26":
        raise ValueError("P016_INNER63_EXCHANGE_TAIL_CHANGED")
    temporal = {}
    crossing_labels = 0
    for split, v in views.items():
        rows = v.source.rows
        for col in (
            "feature_cutoff_UTC",
            "forecast_issuance_UTC",
            "entry_proxy_reference_UTC",
            "exit_proxy_reference_UTC",
            "label_maturity_UTC",
        ):
            if col not in rows:
                raise ValueError("P016_CLOCK_MISSING")
        assert (
            (pd.to_datetime(rows.forecast_issuance_UTC) - pd.to_datetime(rows.feature_cutoff_UTC))
            .eq(pd.Timedelta(minutes=2))
            .all()
        )
        assert (
            (
                pd.to_datetime(rows.exit_proxy_reference_UTC)
                - pd.to_datetime(rows.entry_proxy_reference_UTC)
            )
            .eq(pd.Timedelta(hours=4))
            .all()
        )
        assert (
            (
                pd.to_datetime(rows.label_maturity_UTC)
                - pd.to_datetime(rows.exit_proxy_reference_UTC)
            )
            .eq(pd.Timedelta(minutes=2))
            .all()
        )
        if split == "inner_train":
            assert rows.session.max() < tail[0]
        if split == "inner_validation":
            assert set(rows.session).issubset(set(tail))
        if split != "development":
            assert rows.session.max() <= "2025-03-28"
        maturity_days = (
            pd.to_datetime(rows.label_maturity_UTC, utc=True)
            .dt.tz_convert("America/New_York")
            .dt.strftime("%Y-%m-%d")
        )
        cutoff = (
            "2024-12-24"
            if split == "inner_train"
            else ("2026-01-06" if split == "development" else "2025-03-28")
        )
        crossing = int((maturity_days.gt(cutoff) | maturity_days.ne(rows.session)).sum())
        crossing_labels += crossing
        if crossing:
            raise ValueError("P016_LABEL_MATURITY_CROSSES_SESSION_OR_FIT_BOUNDARY")
        temporal[split] = dict(
            first=str(rows.session.min()),
            last=str(rows.session.max()),
            latest_maturity=str(rows.label_maturity_UTC.max()),
            origins=len(rows),
            sessions=len(v.sessions),
        )
    details["chronology"] = dict(
        tail63=tail,
        permitted_populations=temporal,
        purge_cross_boundary_labels=crossing_labels,
        inner_refit_recipes_distinct=views["inner_train"].source.recipe_id
        != views["refit"].source.recipe_id,
        development_used_for_selection=False,
    )
    return pd.concat(traces, ignore_index=True), pd.DataFrame(health), details


def target_panel(
    view: TrainingView, labels: dict[str, np.ndarray], epsilon: float, split: str
) -> pd.DataFrame:
    guard_scope(split)
    guard_scope(split, str(view.source.rows.session.min()), str(view.source.rows.session.max()))
    records = []
    for row in view.source.rows.to_dict("records"):
        d, o = int(row["day_index"]), int(row["origin"]) - 1
        returns = labels["returns"][d, :, o]
        median = float(np.median(returns))
        mad = float(np.median(np.abs(returns - median)))
        y = view.source.targets[d, :, o]
        formula = (returns - median) / (mad + epsilon)
        if not np.array_equal(formula.astype(np.float32), y):
            raise ValueError("P016_TG20_DECOMPOSITION_CHANGED")
        for j, symbol in enumerate(SYMBOLS):
            records.append(
                dict(
                    split=split,
                    session=str(row["session"]),
                    origin=o + 1,
                    symbol=symbol,
                    target=float(y[j]),
                    raw_return=float(returns[j]),
                    median=median,
                    numerator=float(returns[j] - median),
                    MAD=mad,
                    epsilon=epsilon,
                    denominator=mad + epsilon,
                    MAD_over_epsilon=mad / epsilon,
                    floor_share=epsilon / (mad + epsilon),
                )
            )
    return pd.DataFrame(records)


def matched_audit(
    f: pd.DataFrame, report: Path, threshold: float
) -> dict[str, pd.DataFrame | dict]:
    guard_scope("development", str(f.session.min()), str(f.session.max()))
    f = f.copy()
    f["weight"] = day_weights(f)
    f["month"] = f.session.str[:7]
    f["tail"] = np.where(f.target.abs().ge(threshold), "TRAIN_Q99_TAIL", "NON_TAIL")
    f["magnitude_bin"] = pd.cut(
        f.target.abs(),
        [0, 1, 2, 5, 10, np.inf],
        right=False,
        labels=["[0,1)", "[1,2)", "[2,5)", "[5,10)", "[10,inf)"],
    ).astype(str)
    decomposition = []
    dispersion = []
    groups = []
    origin_rows = []
    for arm in ("C0", "T2", "ZERO"):
        terms = weighted_decomposition(f.target.to_numpy(), f[arm].to_numpy(), f.weight.to_numpy())
        decomposition.append(dict(arm=arm, **terms))
        for field in (arm, "target"):
            a = f[field].to_numpy(dtype=float)
            dispersion.append(
                dict(
                    arm=arm,
                    record="POOLED_UNIQUE_OBSERVATIONS",
                    variable=field,
                    **quantiles(a),
                    absolute=False,
                    pooled_Spearman=float(
                        np.corrcoef(
                            pd.Series(a).rank(method="average"), f.target.rank(method="average")
                        )[0, 1]
                    )
                    if np.ptp(a) > 0
                    else None,
                )
            )
            dispersion.append(
                dict(
                    arm=arm,
                    record="POOLED_UNIQUE_OBSERVATIONS",
                    variable=field,
                    **quantiles(a, True),
                    absolute=True,
                )
            )
        for (day, o), g in f.groupby(["session", "origin"], sort=True):
            origin_rows.append(
                dict(
                    session=day,
                    origin=o,
                    arm=arm,
                    **origin_metrics(g, arm),
                    target_cs_mean=float(g.target.mean()),
                    target_cs_median=float(g.target.median()),
                )
            )
        for group_kind in ("origin", "symbol", "month", "tail", "magnitude_bin"):
            for key, g in f.groupby(group_kind, sort=True):
                groups.append(
                    dict(
                        arm=arm,
                        group_kind=group_kind,
                        group=str(key),
                        sessions=g.session.nunique(),
                        population_weight_mass=float(g.weight.sum()),
                        weighting="CONDITIONAL_INHERITED_FULL_DAY_WEIGHTS",
                        **weighted_decomposition(
                            g.target.to_numpy(), g[arm].to_numpy(), g.weight.to_numpy()
                        ),
                    )
                )
        # Fixed post-hoc score bins: descriptive, never a fitted predictive calibration.
        if arm != "ZERO":
            bins = pd.qcut(f[arm], 5, labels=False, duplicates="drop")
            for k, g in f.groupby(bins):
                dispersion.append(
                    dict(
                        arm=arm,
                        record="POSTHOC_DEV_SCORE_QUINTILE_NOT_PREDICTOR",
                        bin=int(k) + 1,
                        rows=len(g),
                        prediction_mean=float(g[arm].mean()),
                        target_mean=float(g.target.mean()),
                        target_sd=float(g.target.std(ddof=0)),
                        minimum=float(g[arm].min()),
                        maximum=float(g[arm].max()),
                    )
                )
    original = pd.read_csv(report / "matched_metrics.csv", float_precision="round_trip").set_index(
        "arm"
    )
    original_values = original.to_dict("index")
    for r in decomposition:
        if not np.isclose(r["MSE"], original_values[r["arm"]]["MSE"], rtol=0, atol=2e-12):
            raise ValueError("P016_ORIGINAL_WEIGHTED_MSE_DOES_NOT_RECONCILE")
    origin = pd.DataFrame(origin_rows)
    group_frame = pd.DataFrame(groups)
    group_frame["defined_full_panel_Rank_IC"] = np.nan
    for i, record in group_frame.iterrows():
        if record.group_kind not in ("origin", "month"):
            continue
        selected = origin.loc[origin.arm.eq(record.arm)]
        selected = (
            selected.loc[selected.origin.eq(int(record.group))]
            if record.group_kind == "origin"
            else (selected.loc[selected.session.str[:7].eq(record.group)])
        )
        group_frame.loc[i, "defined_full_panel_Rank_IC"] = float(
            selected.groupby("session").Rank_IC.mean().mean()
        )
    stock_rank = []
    true_rank = f.groupby(["session", "origin"]).target.rank(method="average")
    for arm in ("C0", "T2"):
        score_rank = f.groupby(["session", "origin"])[arm].rank(method="average")
        for symbol, g in f.assign(true_rank=true_rank, score_rank=score_rank).groupby("symbol"):
            w = g.weight.to_numpy(dtype=float)
            w = w / w.sum()
            stock_rank.append(
                dict(
                    arm=arm,
                    symbol=symbol,
                    rows=len(g),
                    mean_forecast_rank=float(w @ g.score_rank.to_numpy()),
                    mean_actual_rank=float(w @ g.true_rank.to_numpy()),
                    rank_MAE=float(w @ np.abs(g.score_rank.to_numpy() - g.true_rank.to_numpy())),
                    definition=(
                        "Ranks within complete20stock origin; not a single-stock cross-sectional IC"
                    ),
                )
            )
    daily = (
        origin.groupby(["session", "arm"])[
            ["MSE", "MAE", "Rank_IC", "relative_sign_accuracy", "pairwise_concordance"]
        ]
        .mean()
        .reset_index()
    )
    for arm in ("C0", "T2"):
        observed = float(daily.loc[daily.arm.eq(arm), "Rank_IC"].mean())
        if abs(observed - float(original_values[arm]["Rank_IC"])) > 2e-12:
            raise ValueError("P016_IC_NOT_REPRODUCED")
    paired = daily.loc[daily.arm.eq("C0")].merge(
        daily.loc[daily.arm.eq("T2")], on="session", suffixes=("_C0", "_T2")
    )
    zero = daily.loc[daily.arm.eq("ZERO"), ["session", "MSE", "MAE"]].rename(
        columns={"MSE": "MSE_ZERO", "MAE": "MAE_ZERO"}
    )
    paired = paired.merge(zero, on="session")
    paired["delta_MSE"] = paired.MSE_T2 - paired.MSE_C0
    paired["delta_IC"] = paired.Rank_IC_T2 - paired.Rank_IC_C0
    paired["delta_MAE"] = paired.MAE_T2 - paired.MAE_C0
    paired["C0_minus_ZERO"] = paired.MSE_C0 - paired.MSE_ZERO
    paired["T2_minus_ZERO"] = paired.MSE_T2 - paired.MSE_ZERO
    pairgroup = group_frame.pivot(
        index=["group_kind", "group"],
        columns="arm",
        values=[
            "MSE",
            "MAE",
            "delta_MSE_vs_ZERO",
            "relative_sign_accuracy",
            "defined_full_panel_Rank_IC",
        ],
    )
    pairgroup.columns = ["_".join(c) for c in pairgroup.columns]
    pairgroup = pairgroup.reset_index()
    pairgroup["delta_MSE_T2_minus_C0"] = pairgroup.MSE_T2 - pairgroup.MSE_C0
    calendar = schedule(str(paired.session.min()), str(paired.session.max()))
    positions = {d: i for i, d in enumerate(pd.DatetimeIndex(calendar.index).strftime("%Y-%m-%d"))}
    pos = np.asarray([positions[d] for d in paired.session])
    intervals = {
        key: paired_blocks(paired[key].to_numpy(), pos, 5) for key in ("delta_MSE", "delta_IC")
    }
    for arm in ("C0", "T2"):
        intervals["daily_IC_" + arm + "_reference_zero_NOT_ZERO_FORECAST_IC"] = paired_blocks(
            paired["Rank_IC_" + arm].to_numpy(), pos, 5
        )
    return dict(
        decomposition=pd.DataFrame(decomposition),
        dispersion=pd.DataFrame(dispersion),
        groups=group_frame,
        stock_rank=pd.DataFrame(stock_rank),
        per_origin=origin,
        daily=daily,
        paired=paired,
        paired_groups=pairgroup,
        intervals=dict(
            status="EXPLORATORY_NOT_SELECTION_ADJUSTED_NOT_G8",
            diagnostics=intervals,
            caveat=(
                "Single development panel/seed already used in research; no formal temporal null, "
                "independent replication or economic claim."
            ),
        ),
    )


def tail_study(panels: dict[str, pd.DataFrame], f: pd.DataFrame) -> dict[str, pd.DataFrame | dict]:
    for split, panel in panels.items():
        guard_scope(split, str(panel.session.min()), str(panel.session.max()))
    train = panels["refit"]
    thresholds = {f"q{q}": float(np.quantile(train.target.abs(), q / 100)) for q in (95, 99, 99.9)}
    numerator_q95 = float(np.quantile(train.numerator.abs(), 0.95))
    mad_q5 = float(np.quantile(train.drop_duplicates(["session", "origin"]).MAD, 0.05))
    common_q95 = float(
        np.quantile(train.drop_duplicates(["session", "origin"])["median"].abs(), 0.95)
    )
    stats = []
    for split, panel in panels.items():
        for group_kind, group in (
            [("ALL", panel)]
            + [("symbol:" + str(k), g) for k, g in panel.groupby("symbol")]
            + [("origin:" + str(k), g) for k, g in panel.groupby("origin")]
        ):
            for absolute in (False, True):
                stats.append(
                    dict(
                        split=split,
                        group=group_kind,
                        absolute=absolute,
                        **quantiles(group.target.to_numpy(), absolute),
                        positive_fraction=float(group.target.gt(0).mean()),
                        negative_fraction=float(group.target.lt(0).mean()),
                        sessions=group.session.nunique(),
                        event_q99_fraction=float(group.target.abs().ge(thresholds["q99"]).mean()),
                        MAD_median=float(group.MAD.median()),
                        MAD_q05=float(group.MAD.quantile(0.05)),
                        MAD_over_epsilon_median=float(group.MAD_over_epsilon.median()),
                        floor_dominant_fraction=float(group.floor_share.ge(0.5).mean()),
                        epsilon=float(group.epsilon.iloc[0]),
                        numerator_abs_q99=float(group.numerator.abs().quantile(0.99)),
                    )
                )
    dev = panels["development"].copy()
    dev["large_numerator"] = dev.numerator.abs().ge(numerator_q95)
    dev["small_MAD"] = dev.MAD.le(mad_q5)
    dev["mechanism"] = np.select(
        [dev.large_numerator & dev.small_MAD, dev.large_numerator, dev.small_MAD],
        ["BOTH_LARGE_NUMERATOR_SMALL_MAD", "LARGE_NUMERATOR", "SMALL_MAD"],
        default="NEITHER_TRAIN_Q95_Q05_FLAG",
    )
    event_records = []
    for name, threshold in thresholds.items():
        event = dev.target.abs().ge(threshold)
        for mechanism, g in dev.loc[event].groupby("mechanism"):
            event_records.append(
                dict(
                    record="EXPOST_DENOMINATOR_ATTRIBUTION",
                    threshold=name,
                    value=threshold,
                    mechanism=mechanism,
                    rows=len(g),
                    events=int(event.sum()),
                    event_fraction=len(g) / int(event.sum()),
                    median_abs_numerator=float(g.numerator.abs().median()),
                    median_MAD=float(g.MAD.median()),
                    median_MAD_over_epsilon=float(g.MAD_over_epsilon.median()),
                    common_move_flag_fraction=float(g["median"].abs().ge(common_q95).mean()),
                )
            )
        for arm in ("C0", "T2"):
            score = f[arm].to_numpy(dtype=float)
            rank = f.groupby(["session", "origin"])[arm].rank(method="average", pct=True).to_numpy()
            abs_rank = (
                f.assign(magnitude=np.abs(score))
                .groupby(["session", "origin"])
                .magnitude.rank(method="first", ascending=False)
                .to_numpy()
            )
            chosen = abs_rank <= 4
            truth = dev.target.to_numpy()
            flags = event.to_numpy()
            favorable = np.where(truth > 0, rank, 1 - rank + 1 / 20)
            event_records.append(
                dict(
                    record="POSTHOC_DEV_TOP4_ABS_SCORE_NOT_VALIDATED_CLASSIFIER",
                    threshold=name,
                    value=threshold,
                    arm=arm,
                    rows=len(dev),
                    events=int(flags.sum()),
                    event_prevalence=float(flags.mean()),
                    event_days=dev.loc[event, "session"].nunique(),
                    event_positive_fraction=float((truth[flags] > 0).mean()),
                    event_score_abs_median=float(np.median(np.abs(score[flags]))),
                    event_score_abs_q95=float(np.quantile(np.abs(score[flags]), 0.95)),
                    event_target_abs_median=float(np.median(np.abs(truth[flags]))),
                    event_sign_accuracy=float(
                        np.mean(np.sign(score[flags]) == np.sign(truth[flags]))
                    ),
                    event_favorable_signed_rank_pct_mean=float(favorable[flags].mean()),
                    event_top4_magnitude_recall=float(chosen[flags].mean()),
                    top4_magnitude_precision=float(flags[chosen].mean()),
                    score_absolute_threshold_from_training="NOT_AVAILABLE_NOT_FITTED",
                )
            )
    examples = (
        dev.assign(abs_target=dev.target.abs()).sort_values("abs_target", ascending=False).head(12)
    )
    concentrations = []
    weights = day_weights(f)
    for arm in ("C0", "T2", "ZERO"):
        losses = (f[arm].to_numpy() - f.target.to_numpy()) ** 2
        total = float(weights @ losses)
        day = (
            pd.DataFrame(dict(session=f.session, loss=weights * losses))
            .groupby("session")
            .loss.sum()
            .sort_values(ascending=False)
        )
        for fraction in (0.01, 0.05, 0.1):
            n = math.ceil(len(day) * fraction)
            concentrations.append(
                dict(
                    arm=arm,
                    group_kind="WORST_DAYS",
                    group=str(fraction),
                    rows=n,
                    loss_share=float(day.iloc[:n].sum() / total),
                )
            )
        for name, mask in [
            ("TRAIN_Q99_TAIL", f.target.abs().ge(thresholds["q99"]).to_numpy()),
            ("NON_TAIL", f.target.abs().lt(thresholds["q99"]).to_numpy()),
        ]:
            concentrations.append(
                dict(
                    arm=arm,
                    group_kind="TARGET_BIN",
                    group=name,
                    rows=int(mask.sum()),
                    loss_share=float(np.sum(weights[mask] * losses[mask]) / total),
                    conditional_MSE=float(np.average(losses[mask], weights=weights[mask])),
                )
            )
        for symbol in SYMBOLS:
            mask = f.symbol.eq(symbol).to_numpy()
            concentrations.append(
                dict(
                    arm=arm,
                    group_kind="STOCK",
                    group=symbol,
                    rows=int(mask.sum()),
                    loss_share=float(np.sum(weights[mask] * losses[mask]) / total),
                )
            )
    return dict(
        distributions=pd.DataFrame(stats),
        events=pd.DataFrame(event_records),
        examples=examples.drop(columns="abs_target"),
        concentration=pd.DataFrame(concentrations),
        thresholds=dict(
            target_absolute_train_pooled=thresholds,
            raw_numerator_abs_train_q95=numerator_q95,
            MAD_train_unique_origin_q05=mad_q5,
            absolute_peer_median_train_q95=common_q95,
            scope="DESCRIPTIVE_TRAIN_ONLY_FLAGS_NOT_MODEL_PARAMETERS",
        ),
    )


def denominator_contrasts(panels: dict[str, pd.DataFrame], threshold: float) -> pd.DataFrame:
    """Tail versus ordinary denominator facts, preserving every target observation."""
    rows = []
    for split, panel in panels.items():
        stage_q99 = (
            float(np.quantile(panel.target.abs(), 0.99)) if split == "inner_train" else threshold
        )
        for tail, selected in [
            ("TAIL", panel.target.abs().ge(stage_q99)),
            ("ORDINARY", panel.target.abs().lt(stage_q99)),
        ]:
            g = panel.loc[selected]
            rows.append(
                dict(
                    split=split,
                    group=tail,
                    threshold=stage_q99,
                    threshold_population="INNER_TRAIN_ONLY"
                    if split == "inner_train"
                    else "REFIT_TRAIN_ONLY",
                    stock_rows=len(g),
                    sessions=g.session.nunique(),
                    MAD_median=float(g.MAD.median()),
                    MAD_p05=float(g.MAD.quantile(0.05)),
                    MAD_p95=float(g.MAD.quantile(0.95)),
                    MAD_over_epsilon_median=float(g.MAD_over_epsilon.median()),
                    floor_dominant_fraction=float(g.floor_share.ge(0.5).mean()),
                    numerator_abs_median=float(g.numerator.abs().median()),
                    numerator_abs_p99=float(g.numerator.abs().quantile(0.99)),
                    TG20_abs_median=float(g.target.abs().median()),
                )
            )
    return pd.DataFrame(rows)


def input_audit(c: dict, views: dict[str, TrainingView]) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Unique component cells in admitted windows; descriptive shifts, never new scalers."""
    for split, view in views.items():
        guard_scope(split, str(view.source.rows.session.min()), str(view.source.rows.session.max()))
    summaries = []
    masks = []
    with np.load(verified(Path.cwd(), c["store"]), allow_pickle=False) as store:
        guard_scope("refit", end=str(store["maximum_numeric_date"].item()))
        if (
            str(store["preparation_id"].item()) != c["preparation_id"]
            or tuple(store["symbols"].tolist()) != SYMBOLS
        ):
            raise ValueError("P016_COMPONENT_METADATA_IDENTITY_CHANGED")
        source_valid = store["source_valid"]
        native = store["native_refit"]
        for split in ("inner_train", "refit", "development"):
            v = views[split].source
            indices = np.unique(
                np.concatenate(
                    [
                        np.arange(last - 47, last + 1)
                        for last in v.rows.last_step.to_numpy(dtype=int)
                    ]
                )
            )
            for name in ORDER:
                if name == "M2":
                    parts = []
                    for o in (1, 2):
                        lasts = v.rows.loc[v.rows.origin.eq(o), "last_step"].to_numpy(dtype=int)
                        idx = np.unique(
                            np.concatenate([np.arange(last - 47, last + 1) for last in lasts])
                        )
                        parts.append(v.m2[v.day_index[idx], :, o - 1].reshape(-1))
                    values = np.concatenate(parts)
                else:
                    values = v.common[indices, :, COMMON.index(name)].reshape(-1)
                finite = values[np.isfinite(values)]
                summaries.append(
                    dict(
                        split=split,
                        feature=name,
                        unique_hour_stock_cells=len(values),
                        selection="UNIQUE_ADMITTED_WINDOW_HOURS;M2_ORIGIN_CONTEXT_SEPARATE",
                        nonfinite=int((~np.isfinite(values)).sum()),
                        constant=bool(np.ptp(finite) == 0),
                        mean=float(finite.mean()),
                        sd=float(finite.std()),
                        abs_gt5_fraction=float(np.mean(np.abs(finite) > 5)),
                        abs_gt10_fraction=float(np.mean(np.abs(finite) > 10)),
                        **quantiles(finite),
                    )
                )
        records = []
        for recipe in ("inner", "refit"):
            index = pd.read_csv(verified(Path.cwd(), c["origins"][recipe]))
            guard_scope("refit", str(index.session.min()), str(index.session.max()))
            for row in index.to_dict("records"):
                day = str(row["session"])
                split = (
                    "inner_train"
                    if recipe == "inner" and day < c["inner_validation_start"]
                    else "inner_validation"
                    if recipe == "inner" and day <= "2025-03-28"
                    else "refit"
                    if recipe == "refit" and day <= "2025-03-28"
                    else "development"
                    if recipe == "refit"
                    else "IGNORE"
                )
                if split == "IGNORE":
                    continue
                last = int(row["last_step"])
                historical = source_valid[last - 47 : last + 1]
                current = native[last, :, COMMON.index("V2")]
                rms = float(np.exp(np.nanmedian(current))) if np.isfinite(current).any() else None
                records.append(
                    dict(
                        split=split,
                        session=day,
                        origin=int(row["origin"]),
                        month=day[:7],
                        source_ready=bool(row["source_ready"]),
                        feature_ready=bool(row["feature_ready"]),
                        forecast_issuable=bool(row["forecast_issuable"]),
                        label_ready=bool(row["label_ready"]),
                        supervised_ready=bool(row["supervised_ready"]),
                        current_hourly_rms_proxy=rms,
                        input_exclusion=str(row["input_exclusion"]),
                        label_exclusion=str(row["label_exclusion"]),
                        missing_window_symbols="|".join(
                            symbol for j, symbol in enumerate(SYMBOLS) if not historical[:, j].all()
                        ),
                    )
                )
        table = pd.DataFrame(records)
        train_rms = table.loc[table.split.eq("refit"), "current_hourly_rms_proxy"].dropna()
        low, high = float(train_rms.quantile(0.25)), float(train_rms.quantile(0.75))
        table["volatility_context"] = np.select(
            [
                table.current_hourly_rms_proxy.isna(),
                table.current_hourly_rms_proxy.lt(low),
                table.current_hourly_rms_proxy.gt(high),
            ],
            ["NOT_MEASURABLE", "LOW_TRAIN_Q25", "HIGH_TRAIN_Q75"],
            default="MIDDLE",
        )
        for kind in ("month", "origin", "volatility_context"):
            for (split, key), g in table.groupby(["split", kind]):
                masks.append(
                    dict(
                        split=split,
                        group_kind=kind,
                        group=str(key),
                        structural_origins=len(g),
                        source_ready=int(g.source_ready.sum()),
                        feature_ready=int(g.feature_ready.sum()),
                        supervised_ready=int(g.supervised_ready.sum()),
                        retention=float(g.supervised_ready.mean()),
                        fraction_current_vol_proxy_measurable=float(
                            g.current_hourly_rms_proxy.notna().mean()
                        ),
                    )
                )
        for split, g in table.groupby("split"):
            for symbol in SYMBOLS:
                present = g.missing_window_symbols.map(
                    lambda value: symbol in str(value).split("|")
                )
                masks.append(
                    dict(
                        split=split,
                        group_kind="STOCK_SOURCE_WINDOW_DEFECT",
                        group=symbol,
                        structural_origins=len(g),
                        origins_with_own_missing_source_window=int(present.sum()),
                        joint_supervised_ready=int(g.supervised_ready.sum()),
                        qualification=(
                            "Own source defects only; missing others or "
                            "long-history features can exclude whole20panel"
                        ),
                    )
                )
        totals = {
            k: dict(
                structural_origins=len(g),
                supervised_origins=int(g.supervised_ready.sum()),
                retained=float(g.supervised_ready.mean()),
            )
            for k, g in table.groupby("split")
        }
        return (
            pd.DataFrame(summaries),
            pd.DataFrame(masks),
            dict(
                totals=totals,
                volatility_context_train_q25=low,
                volatility_context_train_q75=high,
                source_missing_counts={
                    s: int((~source_valid[:, j]).sum()) for j, s in enumerate(SYMBOLS)
                },
                missingness=(
                    "Coverage-conditioned selection; regime summaries descriptive, "
                    "not evidence missing-at-random"
                ),
                excluded_origins=table.loc[
                    ~table.supervised_ready,
                    [
                        "split",
                        "session",
                        "origin",
                        "input_exclusion",
                        "label_exclusion",
                        "missing_window_symbols",
                    ],
                ]
                .head(8)
                .fillna("NONE")
                .to_dict("records"),
            ),
        )


def checked_binding(
    manifest: dict, plan: dict, c: dict, arm: str, stage: str, result: dict
) -> dict:
    """Validate semantic expected checkpoint identity before tensor deserialization."""
    b = manifest["binding"]
    split = "inner_train" if stage == "CALIBRATION_SELECTED" else "refit"
    if stage not in ("CALIBRATION_SELECTED", "REFIT_FINAL"):
        raise ValueError("P016_FORGED_STAGE")
    result_key = "calibration_checkpoint" if stage == "CALIBRATION_SELECTED" else "refit_checkpoint"
    if manifest != result[result_key]:
        raise ValueError("P016_CHECKPOINT_MANIFEST_DIFFERS_FROM_HASH_BOUND_RUN_RESULT")
    expected = dict(
        run_id=IDS[0 if arm == "C0" else 1],
        architecture="TM0",
        parameters=6433,
        seed=42,
        input_contract=plan["input_contract"],
        preparation_id=c["preparation_id"],
        source_revision=REVISION,
        symbols=list(SYMBOLS),
        feature_id=plan["feature_id"],
        target_id=TARGET,
        clock_id=plan["clock_id"],
        code_sha256=plan["code_sha256"],
        plan=result["plan"],
        selected_epoch=result["selection"]["selected"],
        arm=arm,
        inverse="SCALE_TIMES_SINH_ONCE" if arm == "T2" else "IDENTITY",
        checkpoint_outputs="LOGITS",
        stage=stage,
        recipe_id=plan["views"][split]["recipe_id"],
        scale=plan["scales"][split] if arm == "T2" else None,
    )
    if b != expected:
        raise ValueError("P016_CHECKPOINT_STAGE_INPUT_ORDER_TARGET_SCALE_DENIED")
    return expected


def choose_examples(f: pd.DataFrame) -> list[dict]:
    """Ex-post chart examples are isolated from the outcome-blind replay schedule."""
    near = (
        f.assign(ratio=f.target.abs() / (f.C0.abs() + 0.01))
        .sort_values("ratio", ascending=False)
        .iloc[0]
    )
    tail = f.iloc[int(np.argmax(f.target.abs().to_numpy()))]
    disagree = f.iloc[int(np.argmax((f.C0 - f.T2).abs().to_numpy()))]
    activity = f.groupby(["session", "origin"]).raw_future_return.agg(
        lambda x: float(np.sqrt(np.mean(x * x)))
    )
    quiets = activity.sort_values()
    quiet_key = quiets.index[max(0, len(quiets) // 8)]
    quiet = f.loc[
        f.session.eq(quiet_key[0]) & f.origin.eq(quiet_key[1]) & f.symbol.eq("AAPL")
    ].iloc[0]
    result = []
    for reason, row in [
        ("NEAR_ZERO_SCORE_LARGE_TARGET", near),
        ("TYPICAL_QUIET_RAW_RETURN_ORIGIN", quiet),
        ("LARGEST_STOCK_SPECIFIC_TG20_TAIL", tail),
        ("LARGEST_C0_T2_DISAGREEMENT", disagree),
    ]:
        result.append(
            dict(
                reason=reason,
                selection="POST_HOC_DIAGNOSTIC",
                session=str(row.session),
                origin=int(row.origin),
                symbol=str(row.symbol),
                source_key=str(row.source_key),
                TG20=float(row.target),
                C0=float(row.C0),
                T2=float(row.T2),
                raw_future_return=float(row.raw_future_return),
                numerator=float(row.raw_future_return - row.cross_sectional_median),
                MAD=float(row.cross_sectional_MAD),
                epsilon=float(row.epsilon),
                issuance=str(row.forecast_issuance_UTC),
                cutoff=str(row.forecast_cutoff_UTC),
                exit=str(row.exit_proxy_reference_UTC),
            )
        )
    return result


def evaluation_forward(
    model: SharedLSTM, x: torch.Tensor, policy: LossPolicy
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """One inference-only encoder/head pass; training mode fails before computation."""
    if any(module.training for module in model.modules()):
        raise ValueError("P016_TRAINING_MODE_FORBIDDEN")
    with torch.no_grad():
        hidden = model.encode(x)
        logits = model.head(model.dropout(hidden)).squeeze(-1)
        canonical = policy.canonical(logits)
    return hidden, logits, canonical


def replay(
    report: Path,
    plan: dict,
    c: dict,
    f: pd.DataFrame,
    views: dict[str, TrainingView],
    examples: list[dict],
) -> tuple[pd.DataFrame, dict]:
    """At most21eval forwards/arm, no autograd/backward/optimizer; outputs not re-fit."""
    torch.set_num_threads(1)
    rows = []
    checks = []
    models = []
    dev = views["development"].source
    fixed = np.linspace(0, len(dev.rows) - 1, 8, dtype=int).tolist()
    chosen = {p: "OUTCOME_BLIND_EVENLY_SPACED_ORIGIN_INDEX" for p in fixed}
    for e in examples:
        match = dev.rows.index[dev.rows.session.eq(e["session"]) & dev.rows.origin.eq(e["origin"])]
        chosen.setdefault(int(match[0]), "POST_HOC_DIAGNOSTIC")
    if len(chosen) > 12:
        raise ValueError("P016_BOUNDED_REPLAY_LIMIT")
    for arm, name in zip(("C0", "T2"), IDS):
        result = read_json(report / name / "run_result.json")
        calls = 0
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(42)  # Reconstruct the recorded seed42initialization only, never fit.
            initial = SharedLSTM()
        if state_hash(initial) != result["initial_hash"]:
            raise ValueError("P016_RECORDED_INITIAL_STATE_NOT_REPRODUCIBLE")
        initial_head = float(initial.head.weight.detach().norm())
        initial_bias = float(initial.head.bias.detach()[0])
        for stem, stage in [
            ("calibration_selected", "CALIBRATION_SELECTED"),
            ("refit_final", "REFIT_FINAL"),
        ]:
            path = report / name / (stem + ".pt")
            manifest = read_json(path.with_suffix(".manifest.json"))
            expected = checked_binding(manifest, plan, c, arm, stage, result)
            model = reload_checkpoint(path, expected, manifest)
            before = state_hash(model)
            sets = (
                [("development", p, reason) for p, reason in sorted(chosen.items())]
                if stage == "REFIT_FINAL"
                else [
                    (split, int(p), "OUTCOME_BLIND_EVENLY_SPACED_ORIGIN_INDEX")
                    for split in ("inner_train", "inner_validation")
                    for p in np.linspace(0, len(views[split].source.rows) - 1, 4, dtype=int)
                ]
            )
            scale = expected["scale"]["scale"] if expected["scale"] is not None else 1.0
            policy = LossPolicy(arm, scale=scale)
            model.eval()
            for n, (split, position, reason) in enumerate(sets):
                guard_scope(split)
                view = views[split].source
                row = view.rows.iloc[position]
                guard_scope(split, str(row.session), str(row.session))
                batch = view.batch((position,))
                x = torch.from_numpy(batch.x[0])
                hidden, logits, score = evaluation_forward(model, x, policy)
                calls += 1
                repeat_equal = None
                if stage == "REFIT_FINAL" and n == 0:
                    _, _, again = evaluation_forward(model, x, policy)
                    calls += 1
                    repeat_equal = torch.equal(score, again)
                    if not repeat_equal:
                        raise ValueError("P016_NONDETERMINISTIC_EVAL")
                saved = (
                    f.loc[
                        f.session.eq(str(row.session)) & f.origin.eq(int(row.origin)), arm
                    ].to_numpy(dtype=np.float32)
                    if split == "development"
                    else None
                )
                maximum_difference = None
                if saved is not None:
                    maximum_difference = float(np.max(np.abs(score.numpy() - saved)))
                    if not np.allclose(score.numpy(), saved, rtol=2e-5, atol=2e-6):
                        raise ValueError("P016_REPLAY_SAVED_PREDICTION_MISMATCH")
                h = hidden.numpy()
                s = score.numpy()
                y = batch.y[0].astype(float)
                rows.append(
                    dict(
                        arm=arm,
                        stage=stage,
                        split=split,
                        session=str(row.session),
                        origin=int(row.origin),
                        selection=reason,
                        stock_outputs=20,
                        input_shape="20x48x16",
                        input_sha256=hashlib.sha256(batch.x.tobytes()).hexdigest(),
                        checkpoint_sha256=digest(path),
                        recipe_id=view.recipe_id,
                        preparation_id=view.preparation_id,
                        output_sha256=hashlib.sha256(s.tobytes()).hexdigest(),
                        head_weight_L2=float(model.head.weight.detach().norm()),
                        head_bias=float(model.head.bias.detach()[0]),
                        initial_head_weight_L2=initial_head,
                        initial_head_bias=initial_bias,
                        head_norm_ratio_to_recorded_init=float(model.head.weight.detach().norm())
                        / initial_head,
                        hidden_L2_median=float(np.median(np.linalg.norm(h, axis=1))),
                        hidden_L2_max=float(np.linalg.norm(h, axis=1).max()),
                        hidden_cross_stock_sd_mean=float(h.std(axis=0).mean()),
                        hidden_abs_gt095_fraction=float(np.mean(np.abs(h) > 0.95)),
                        output_mean=float(s.mean()),
                        output_sd=float(s.std()),
                        output_abs_max=float(np.abs(s).max()),
                        eval_sample_MSE=float(np.mean((s - y) ** 2)),
                        target_abs_max=float(np.abs(y).max()),
                        saved_score_max_absolute_difference=maximum_difference,
                        saved_comparison="MATCHED_CANONICAL_ONCE_INVERTED"
                        if saved is not None
                        else "NOT_RECORDED_TRAIN_OR_VALIDATION_PER_ORIGIN_SCORE",
                        repeat_bitwise_equal=repeat_equal,
                        grad_enabled_during_forward=False,
                        model_eval=True,
                    )
                )
            if before != state_hash(model) or any(p.grad is not None for p in model.parameters()):
                raise ValueError("P016_REPLAY_CHANGED_MODEL_OR_ACCUMULATED_GRADIENT")
            models.append(
                dict(
                    arm=arm,
                    stage=stage,
                    checkpoint=ref(path),
                    manifest=ref(path.with_suffix(".manifest.json")),
                    state_hash_unchanged=before,
                    head_norm_initial=initial_head,
                    head_bias_initial=initial_bias,
                    head_norm_saved=float(model.head.weight.detach().norm()),
                    head_bias_saved=float(model.head.bias.detach()[0]),
                )
            )
        if calls > 24:
            raise ValueError("P016_TOO_MANY_REPLAY_FORWARDS")
        checks.append(
            dict(
                arm=arm,
                actual_forward_calls=calls,
                maximum_allowed=24,
                optimizer_steps=0,
                backward_calls=0,
                saved_output_tolerance=dict(atol=2e-6, rtol=2e-5),
                qualification="Different legal CPU batch geometry may change float32last bits",
            )
        )
    return pd.DataFrame(rows), dict(
        status="PASS",
        arms=checks,
        checkpoints=models,
        initial_state="RECORDED_SEED42_HASH_RECONSTRUCTED_NO_INITIAL_FORWARD_OR_FIT",
        historical_training_dropout_masks="NOT_RECORDED",
        per_example_training_gradients="NOT_RECORDED",
        optimizer_internal_states="NOT_RECORDED",
        later_epoch_checkpoints="NOT_RECORDED",
        no_backpropagation=True,
        no_parameter_updates=True,
    )


def snapshot(report: Path, c: dict) -> list[dict]:
    paths = {p for p in Path("data/raw").rglob("*") if p.is_file()}
    paths |= {p for p in report.rglob("*") if p.is_file()}
    paths |= {p for p in Path("reports/audit").glob("*.jsonl")}
    paths |= {p for p in Path("docs/track_a").glob("*.md")}
    paths |= {
        Path("configs/CURRENT_PROTOCOL.json"),
        Path("configs/CURRENT_EXPERIMENT_REGISTRY.json"),
        Path("configs/track_a_visualization_v1.json"),
        Path("configs/track_a_hf20_visualization_v1.json"),
    }
    paths |= {
        Path(r["path"])
        for r in c["code"]
        + [c["config"], c["recipes"], c["store"], c["targets"]]
        + list(c["origins"].values())
    }
    paths |= {Path("src/lstm_data") / name for name in code_binding()}
    paths |= {p for p in Path("reports").rglob("*.pt")}
    return [ref(path) for path in sorted(paths)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--through", default="2026-01-06")
    args = parser.parse_args()
    guard_scope("development", end=args.through)
    if args.through != "2026-01-06":
        raise ValueError("P016_FIXED_COMPLETE_POPULATION_ONLY_NO_SILENT_FILTER")
    started = time.monotonic()
    report, plan, c, h, f, views = discover(args.report)
    out = args.out
    out.mkdir(parents=True, exist_ok=False)
    before = snapshot(report, c)
    write_json(out / "preservation_before.json", dict(files=before))
    preflight = dict(
        package="TA-HF20-P016-READONLY-DIAGNOSIS-001",
        at=now(),
        report=str(report),
        registry=ref(Path("configs/CURRENT_EXPERIMENT_REGISTRY.json")),
        journal=ref(Path("reports/audit/track_a_real_pairs_v6.jsonl")),
        ledger=30,
        ceiling=200,
        input_contract=plan["input_contract"],
        source_revision=REVISION,
        source=c["source"],
        store=c["store"],
        targets=c["targets"],
        recipes=c["recipes"],
        recipe_ids=c["recipe_ids"],
        T2_parameters=plan["scales"],
        original_training_code=plan["code"],
        original_training_execution_SHA=plan["code_sha256"],
        model_manifests={
            arm: {
                stage: ref(report / name / (stage + ".manifest.json"))
                for stage in ("calibration_selected", "refit_final")
            }
            for arm, name in zip(("C0", "T2"), IDS)
        },
        numerical_scope="HELD_OUT_LOCKED2026-01-07+;original five-stock lock independent",
        qualification="ASSUMPTION_CONDITIONAL_RETROSPECTIVE_SURVIVOR_SECTORS_AS_REPORTED_UNCERTIFIED_ACTION_PUBLICATION_PIT_LOCAL_USE_ONLY",
        optimizer_steps=0,
        source_requests=0,
    )
    write_json(out / "preflight_sources_and_authority.json", preflight)
    epoch, health, selection = epoch_audit(report, views)
    recipes = read_json(verified(Path.cwd(), c["recipes"]))
    with np.load(verified(Path.cwd(), c["targets"]), allow_pickle=False) as store:
        labels = {key: store[key] for key in ("returns", "median", "mad")}
    panels = {
        split: target_panel(
            views[split],
            labels,
            recipes["inner" if split.startswith("inner") else "refit"]["epsilon"],
            split,
        )
        for split in ("inner_train", "refit", "development")
    }
    tails = tail_study(panels, f)
    threshold = tails["thresholds"]["target_absolute_train_pooled"]["q99"]
    matched = matched_audit(f, report, threshold)
    features, mask, coverage = input_audit(c, views)
    examples = choose_examples(f)
    activations, replay_info = replay(report, plan, c, f, views, examples)
    outputs = {
        "epoch_selection_reconstruction.csv": epoch,
        "hf20_training_and_gradient_health.csv": health,
        "mse_vs_zero_exact_decomposition.csv": matched["decomposition"],
        "forecast_dispersion_and_calibration.csv": matched["dispersion"],
        "stock_origin_month_diagnostics.csv": matched["groups"],
        "tg20_tail_denominator_study.csv": tails["distributions"],
        "tg20_extreme_event_examples.csv": tails["examples"],
        "rare_event_prediction_summary.csv": tails["events"],
        "loss_concentration.csv": tails["concentration"],
        "model_output_and_hidden_diagnostics.csv": activations,
        "paired_c0_t2_development.csv": matched["paired"],
        "paired_origin_stock_month.csv": matched["paired_groups"],
        "per_origin_rank_diagnostics.csv": matched["per_origin"],
        "stock_rank_behavior.csv": matched["stock_rank"],
        "tg20_denominator_tail_contrast.csv": denominator_contrasts(panels, threshold),
        "input_channel_distribution_shift.csv": features,
        "input_coverage_context.csv": mask,
    }
    for name, frame in outputs.items():
        if not isinstance(frame, pd.DataFrame):
            raise TypeError("P016_TABLE_TYPE")
        frame.to_csv(out / name, index=False)
    write_json(out / "replay_identity_results.json", replay_info)
    write_json(out / "paired_interval_exploratory.json", matched["intervals"])
    write_json(out / "tail_thresholds_train_only.json", tails["thresholds"])
    write_json(
        out / "stage_specific_descriptive_thresholds.json",
        {
            **tails["thresholds"],
            "inner_training_absolute_pooled": {
                f"q{q}": float(np.quantile(panels["inner_train"].target.abs(), q / 100))
                for q in (95, 99, 99.9)
            },
        },
    )
    write_json(out / "chronology_and_selection_checks.json", selection)
    write_json(out / "coverage_checks.json", coverage)
    from .hf20_diagnostic_report import write_reports

    write_reports(
        out, report, plan, c, h, matched, tails, epoch, features, activations, examples, replay_info
    )
    changed = [
        r["path"]
        for r in before
        if not Path(r["path"]).is_file() or digest(Path(r["path"])) != r["sha256"]
    ]
    if changed:
        raise ValueError("P016_ORIGINAL_EVIDENCE_CHANGED:" + str(changed))
    if read_rows()[-1]["global_started_pairs"] != 30:
        raise ValueError("P016_LEDGER_CHANGED")
    write_json(
        out / "preservation.json",
        dict(
            status="PASS",
            files_verified=len(before),
            changed=changed,
            ledger_before=30,
            ledger_after=30,
            new_pairs=0,
            optimizer_updates=0,
            original_evidence_unchanged=True,
        ),
    )
    try:
        import resource
        import sys

        peak = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * (
            1 if sys.platform == "darwin" else 1024
        )
    except ImportError:
        peak = None
    write_json(
        out / "analysis_actual_runtime.json",
        dict(
            seconds=time.monotonic() - started,
            peak_RSS_bytes=peak,
            source_requests=0,
            optimizer_updates=0,
            derived_bytes=sum(p.stat().st_size for p in out.rglob("*") if p.is_file()),
            replay_forward_calls=replay_info["arms"],
        ),
    )
    print(
        json.dumps(
            dict(
                status="HF20_P016_DIAGNOSIS_COMPLETE",
                out=str(out),
                ledger=30,
                seconds=time.monotonic() - started,
                optimizer_steps=0,
            )
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
