"""Matched descriptive HF20 development review; never fits or opens held-out outcomes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .calendar import schedule
from .config import write_json
from .four_model_diagnostics import paired_blocks
from .hf20_source import SYMBOLS
from .hf20_training_authority import IDS, read_rows, reference


def origin_metrics(f: pd.DataFrame, arm: str) -> dict:
    score = f[arm].to_numpy(dtype=float)
    target = f.target.to_numpy(dtype=float)
    residual = score - target
    constant = bool(np.ptp(score) == 0)
    constant_target = bool(np.ptp(target) == 0)
    ic = (
        None
        if constant or constant_target
        else float(
            np.corrcoef(
                pd.Series(score).rank(method="average"), pd.Series(target).rank(method="average")
            )[0, 1]
        )
    )
    pair = []
    for i in range(len(score)):
        for j in range(i + 1, len(score)):
            a, b = score[i] - score[j], target[i] - target[j]
            if b:
                pair.append(0.5 if a == 0 else float(a * b > 0))
    return dict(
        MSE=float(np.mean(residual**2)),
        MAE=float(np.mean(np.abs(residual))),
        Rank_IC=ic,
        project_zero_IC=0.0 if constant and not constant_target else ic,
        mathematical_IC_status="UNDEFINED_CONSTANT_SCORE"
        if constant
        else "UNDEFINED_CONSTANT_TARGET"
        if constant_target
        else "DEFINED",
        relative_sign_accuracy=float(np.mean(np.sign(score) == np.sign(target))),
        pairwise_concordance=float(np.mean(pair)) if pair else None,
        score_std=float(np.std(score)),
        tied_pairs=int(
            sum(score[i] == score[j] for i in range(len(score)) for j in range(i + 1, len(score)))
        ),
        score_constant=constant,
        target_variance=float(np.var(target)),
        target_second_moment=float(np.mean(target**2)),
        target_mean=float(np.mean(target)),
    )


def review(out: Path) -> dict:
    p = json.loads((out / "experiment_design.json").read_text())
    frames = []
    results = {}
    for arm, name in zip(("C0", "T2"), IDS):
        directory = out / name
        r = json.loads((directory / "run_result.json").read_text())
        if (
            r["status"] != "COMPLETED"
            or r["score_units"] != "CANONICAL_TG20"
            or r["inverse_count"] != int(arm == "T2")
        ):
            raise ValueError("HF20_INCOMPLETE_OR_WRONG_INVERSE")
        f = pd.read_csv(directory / "predictions_development.csv", float_precision="round_trip")
        if (
            len(f) != 7320
            or f.session.ge("2026-01-07").any()
            or not f.stage.eq("REFIT_FINAL").all()
        ):
            raise ValueError("HF20_UNMATCHED_OR_PROTECTED_ROWS")
        for _, g in f.groupby(["session", "origin"], sort=False):
            if tuple(g.symbol) != SYMBOLS:
                raise ValueError("HF20_COHORT_ORDER")
        frames.append(f)
        results[arm] = r
    keys = [
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
    if not frames[0][keys].equals(frames[1][keys]):
        raise ValueError("HF20_EXACT_MATCH_REQUIRED_NO_INTERSECTION")
    matched = frames[0][keys].copy()
    matched["C0"] = frames[0].score
    matched["T2"] = frames[1].score
    matched["ZERO"] = 0.0
    c = json.loads(Path(p["input_contract"]["path"]).read_text())
    recipes = json.loads(Path(c["recipes"]["path"]).read_text())
    epsilon = recipes["refit"]["epsilon"]
    with np.load(c["targets"]["path"], allow_pickle=False) as labels:
        raw = []
        med = []
        mad = []
        for r in matched.itertuples():
            d, o, j = int(r.day_index), int(r.origin) - 1, int(r.symbol_index)
            raw.append(float(labels["returns"][d, j, o]))
            med.append(float(labels["median"][d, o]))
            mad.append(float(labels["mad"][d, o]))
    matched["raw_future_return"] = raw
    matched["cross_sectional_median"] = med
    matched["cross_sectional_MAD"] = mad
    matched["epsilon"] = epsilon
    if not np.array_equal(
        (
            (matched.raw_future_return - matched.cross_sectional_median)
            / (matched.cross_sectional_MAD + epsilon)
        ).to_numpy(dtype=np.float32),
        matched.target.to_numpy(dtype=np.float32),
    ):
        raise ValueError("HF20_SAVED_TARGET_DECOMPOSITION_CHANGED")
    for arm in ("C0", "T2", "ZERO"):
        matched[arm + "_residual"] = matched[arm] - matched.target
        matched[arm + "_absolute_error"] = matched[arm + "_residual"].abs()
        matched[arm + "_squared_error"] = matched[arm + "_residual"] ** 2
    matched.to_csv(out / "matched_predictions_development.csv", index=False)
    origins = []
    for (day, o), g in matched.groupby(["session", "origin"], sort=True):
        for arm in ("C0", "T2", "ZERO"):
            origins.append(
                dict(session=day, origin=o, arm=arm, stocks=len(g), **origin_metrics(g, arm))
            )
    origin = pd.DataFrame(origins)
    origin.to_csv(out / "per_origin_metrics.csv", index=False)
    numeric = [
        "MSE",
        "MAE",
        "Rank_IC",
        "project_zero_IC",
        "relative_sign_accuracy",
        "pairwise_concordance",
        "score_std",
        "target_variance",
        "target_second_moment",
        "target_mean",
    ]
    daily = origin.groupby(["session", "arm"])[numeric].mean().reset_index()
    daily.to_csv(out / "daily_metrics.csv", index=False)
    metrics = daily.groupby("arm")[numeric].mean().reset_index()
    metrics["sessions"] = matched.session.nunique()
    metrics["origins"] = len(matched) // 20
    metrics["stock_rows"] = len(matched)
    metrics["defined_IC_origins"] = [
        int(origin.loc[origin.arm.eq(a), "Rank_IC"].notna().sum()) for a in metrics.arm
    ]
    metrics["constant_score_origins"] = [
        int(origin.loc[origin.arm.eq(a), "score_constant"].sum()) for a in metrics.arm
    ]
    zero = float(metrics.loc[metrics.arm.eq("ZERO"), "MSE"].iloc[0])
    c0 = float(metrics.loc[metrics.arm.eq("C0"), "MSE"].iloc[0])
    metrics["delta_MSE_vs_ZERO"] = metrics.MSE - zero
    metrics["delta_MSE_vs_C0"] = metrics.MSE - c0
    metrics.to_csv(out / "matched_metrics.csv", index=False)
    daily["month"] = daily.session.str[:7]
    daily.groupby(["month", "arm"])[numeric].mean().reset_index().to_csv(
        out / "monthly_metrics.csv", index=False
    )
    stocks = []
    for symbol, g in matched.groupby("symbol", sort=False):
        for arm in ("C0", "T2", "ZERO"):
            # Within each stock, still aggregate origins first, then days.
            gg = g.assign(squared=(g[arm] - g.target) ** 2, absolute=(g[arm] - g.target).abs())
            days = gg.groupby("session")[["squared", "absolute"]].mean()
            stocks.append(
                dict(
                    symbol=symbol,
                    arm=arm,
                    MSE=float(days.squared.mean()),
                    MAE=float(days.absolute.mean()),
                    sessions=len(days),
                    stock_rows=len(g),
                )
            )
    pd.DataFrame(stocks).to_csv(out / "per_stock_metrics.csv", index=False)
    paired = daily.loc[daily.arm.eq("T2")].merge(
        daily.loc[daily.arm.eq("C0")], on="session", suffixes=("_T2", "_C0")
    )
    paired["delta_MSE"] = paired.MSE_T2 - paired.MSE_C0
    paired["delta_IC"] = paired.Rank_IC_T2 - paired.Rank_IC_C0
    paired.to_csv(out / "paired_daily_contrasts.csv", index=False)
    calendar = schedule(str(paired.session.min()), str(paired.session.max()))
    positions = {
        day: i for i, day in enumerate(pd.DatetimeIndex(calendar.index).strftime("%Y-%m-%d"))
    }
    uncertainty = {
        metric: paired_blocks(
            paired[metric].to_numpy(), np.asarray([positions[d] for d in paired.session]), 5
        )
        for metric in ("delta_MSE", "delta_IC")
    }
    write_json(
        out / "exploratory_paired_intervals.json",
        dict(
            status="EXPLORATORY_NOT_G8_NOT_SELECTION_ADJUSTED",
            contrasts=uncertainty,
            replication="ONE_SEED_ONE_DEVELOPMENT_PANEL_NO_ALPHA_OR_ECONOMIC_CLAIM",
        ),
    )
    artifacts = {
        name: reference(out / name)
        for name in (
            "matched_predictions_development.csv",
            "matched_metrics.csv",
            "per_origin_metrics.csv",
            "daily_metrics.csv",
            "monthly_metrics.csv",
            "per_stock_metrics.csv",
            "paired_daily_contrasts.csv",
            "exploratory_paired_intervals.json",
        )
    }
    example = matched.loc[matched.symbol.eq("AAPL")].iloc[0]
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
    h.update(
        preparation_id=c["preparation_id"],
        score_units="CANONICAL_TG20",
        T2_saved_inverse_count=1,
        heldout_numeric_rows=0,
        global_started_pairs=read_rows()[-1]["global_started_pairs"],
        artifacts=artifacts,
        example=dict(
            symbol=str(example.symbol), session=str(example.session), origin=int(example.origin)
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
        qualification="ASSUMPTION_CONDITIONAL_RETROSPECTIVE_AS_REPORTED_IDEAL_VENDOR_TIME_HOURLY_CLOSE_PROXY",
    )
    write_json(out / "visualization_handoff.json", h)
    write_json(
        Path("configs/track_a_hf20_visualization_v1.json"),
        dict(handoff=reference(out / "visualization_handoff.json")),
    )
    write_json(
        out / "health_and_stage_gates.json",
        dict(
            status="COMPLETED_CONDITIONAL_EXPLORATORY",
            matched_exact=True,
            stock_rows=7320,
            origins=366,
            sessions=183,
            health={a: r["health"] for a, r in results.items()},
            heldout_locked=True,
        ),
    )
    return dict(metrics=metrics.to_dict("records"), example=h["example"], uncertainty=uncertainty)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    print(json.dumps(review(parser.parse_args().out), allow_nan=True))


if __name__ == "__main__":
    main()
