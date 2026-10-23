"""Read-only matched P022 diagnostics after four successful and verified fits."""

from __future__ import annotations

import argparse
import json
import resource
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import now, write_json
from .hf1m_action_audit import SYMBOLS
from .hf1m_ft16_source import checked, ref
from .objective_screen_attribution import allocations, cohort_masks, cohort_table, feature_excerpt
from .objective_screen_audit import month_ci, origin_ic
from .objective_screen_loss import ARMS, RUNS, classes, model_for
from .objective_screen_metrics import classification, regression
from .objective_screen_recovery import rows
from .objective_screen_run import predict
from .objective_screen_source import native_arrays, ordered_targets, scoped_view
from .visualization.hf1m_long import LongStudy

ROLES = ("inner_train", "inner_validation", "refit", "development")
BASELINES = ("HF1M-LONG-TM0-T2-S42-DEV1", "HF1M-LONG-TM0-T2-S123-DEV1")


def daily_scores(f: pd.DataFrame, score: np.ndarray, regression_output: bool) -> pd.DataFrame:
    y = f.TG20.to_numpy(dtype=float).reshape(-1, 20)
    p = score.astype(float).reshape(-1, 20)
    origin_days = f.session_date_et.to_numpy().reshape(-1, 20)[:, 0]
    frame = pd.DataFrame(
        dict(
            session_date_et=origin_days,
            ic=origin_ic(p, y),
            prediction_sd=p.std(axis=1),
            actual_sd=y.std(axis=1),
        )
    )
    for side, sign in [("top", -1), ("bottom", 1)]:
        actual = np.argsort(sign * y, axis=1, kind="stable")[:, :4]
        forecast = np.argsort(sign * p, axis=1, kind="stable")[:, :4]
        hits = (forecast[:, :, None] == actual[:, None, :]).any(axis=2).sum(axis=1) / 4
        frame[side + "4_recall"] = np.where(p.std(axis=1) > 0, hits, np.nan)
    if regression_output:
        frame["mse"] = ((y - p) ** 2).mean(axis=1)
        frame["mae"] = abs(y - p).mean(axis=1)
        frame["zero_mse"] = (y**2).mean(axis=1)
    return frame.groupby("session_date_et").mean().reset_index()


def canonical(frame: pd.DataFrame, target: pd.DataFrame) -> pd.DataFrame:
    keys = pd.MultiIndex.from_frame(target[["origin_id", "ticker"]])
    assert not frame.duplicated(["origin_id", "ticker"]).any() and len(frame) == len(target)
    f = frame.set_index(["origin_id", "ticker"]).reindex(keys).reset_index()
    np.testing.assert_array_equal(f.TG20, target.TG20)
    assert f.session_date_et.lt("2026-01-01").all()
    return f


def daily_classification(f: pd.DataFrame, probability: np.ndarray, recipe: dict) -> pd.DataFrame:
    labels = classes(f.TG20.to_numpy(), recipe["q95_abs_y"])
    coef = np.asarray(recipe["class_weights"])[labels]
    ce = -np.log(np.maximum(probability[np.arange(len(f)), labels], np.finfo(float).tiny))
    frame = pd.DataFrame(
        dict(
            session_date_et=f.session_date_et.to_numpy(),
            weighted_CE=ce * coef,
            coefficient=coef,
            CE=ce,
            Brier=((probability - np.eye(3)[labels]) ** 2).sum(axis=1),
        )
    )
    grouped = frame.groupby("session_date_et")
    result = grouped[["CE", "Brier"]].mean()
    result["weighted_CE"] = grouped.weighted_CE.sum() / grouped.coefficient.sum()
    return result.reset_index()


def exact_cases(
    study: LongStudy,
    view,
    f: pd.DataFrame,
    pairs: pd.DataFrame,
    arm: str,
    recipe: dict,
    destination: Path,
) -> dict:
    indices: dict[int, str] = {}
    for ticker in ("AAPL", "AMZN", "TSLA", "SBUX"):
        selected = (
            f.loc[f.ticker.eq(ticker)]
            .sort_values(["total", "origin_id"], ascending=[False, True])
            .head(5)
        )
        indices.update(
            {int(i): "top5 within ticker by actual weighted objective" for i in selected.index}
        )
    if arm == "E1":
        labels = classes(f.TG20.to_numpy(), recipe["q95_abs_y"])
        predicted = f[["p_NEG", "p_NORMAL", "p_POS"]].to_numpy().argmax(axis=1)
        for k, name in [(0, "NEG"), (2, "POS")]:
            for reason, mask in [
                ("miss", (labels == k) & (predicted != k)),
                ("false_positive", (labels != k) & (predicted == k)),
            ]:
                chosen = f.loc[mask].sort_values("total", ascending=False).head(2)
                indices.update({int(i): name + "_" + reason for i in chosen.index})
    if arm == "R1":
        leading = pairs.loc[pairs.misordered].nlargest(5, "weighted_pair_loss")
        leading.to_parquet(destination / "leading_misordered_pairs.parquet", index=False)
        for row in leading.itertuples():
            chosen = f.loc[
                f.origin_id.eq(row.origin_id) & f.ticker.isin([row.stock_i, row.stock_j])
            ]
            indices.update({int(i): "leading misordered pair endpoint" for i in chosen.index})
    origins = view.source.rows.set_index("origin_id")
    quality = study.table("candles_quality")
    qi = quality.set_index(["step", "ticker"])
    arrays = native_arrays(study, view)
    positions = {key: n for n, key in enumerate(view.source.rows.origin_id)}
    candle_frames, feature_frames, vectors, cases = [], [], [], []
    epsilon = float(study.recipe("refit")["epsilon"])
    for case, (index, reason) in enumerate(indices.items(), 1):
        row = f.loc[[index]].iloc[0]
        origin = origins.loc[[row.origin_id]].iloc[0]
        first, entry, exit_ = (
            int(origin.first_step),
            int(origin.entry_index),
            int(origin.exit_index),
        )
        assert entry - first == 47 and exit_ - entry == 4
        candles = (
            quality.loc[quality.ticker.eq(row.ticker) & quality.step.between(first, exit_)]
            .sort_values("step")
            .copy()
        )
        assert len(candles) == 52
        candles["case_id"] = case
        candles["context"] = np.where(
            candles.step <= entry, "INPUT_BEFORE_ISSUANCE", "OUTCOME_AFTER_ISSUANCE"
        )
        candle_frames.append(candles)
        returns = []
        for ticker in SYMBOLS:
            a = qi.loc[[(entry, ticker)]].iloc[0]
            b = qi.loc[[(exit_, ticker)]].iloc[0]
            assert a.genuine_close and b.genuine_close
            r = float(np.log(float(b.close) / float(a.close)))
            returns.append(r)
            vectors.append(
                dict(
                    case_id=case,
                    ticker=ticker,
                    entry_close=a.close,
                    exit_close=b.close,
                    return_4h=r,
                )
            )
        median = float(np.median(returns))
        mad = float(np.median(abs(np.asarray(returns) - median)))
        target = (returns[SYMBOLS.index(row.ticker)] - median) / (mad + epsilon)
        np.testing.assert_allclose(
            [target, median, mad],
            [row.TG20, row.cross_section_median, row.cross_section_mad],
            rtol=1e-11,
            atol=1e-12,
        )
        features = feature_excerpt(view, arrays, positions[row.origin_id], row.ticker)
        features["case_id"] = case
        feature_frames.append(features)
        assert float(row.epsilon) == epsilon
        cases.append(
            dict(
                **{str(k): v for k, v in row.to_dict().items()},
                case_id=case,
                selection=reason,
                first_step=first,
                entry_step=entry,
                exit_step=exit_,
                issuance_utc=str(origin.issuance_utc),
                reconstructed_TG20=target,
            )
        )
    for name, frame in [
        ("cases", pd.DataFrame(cases)),
        ("case_candles", pd.concat(candle_frames)),
        ("case_features", pd.concat(feature_frames)),
        ("case_20_returns", pd.DataFrame(vectors)),
    ]:
        frame.to_parquet(destination / (name + ".parquet"), index=False)
    return dict(
        cases=len(cases),
        candles=sum(len(g) for g in candle_frames),
        feature_cells=sum(len(g) for g in feature_frames),
        target_reconstruction="PASS",
    )


def run(plan_path: Path, out: Path) -> None:
    started = time.monotonic()
    history = rows()
    if [r["run_id"] for r in history if r["status"] == "COMPLETED"] != list(RUNS):
        raise ValueError("P022_FOUR_COMPLETED_RUNS_REQUIRED_BEFORE_DEVELOPMENT")
    plan = json.loads(plan_path.read_text())
    for name in RUNS:
        gate = json.loads((plan_path.parent / (name + "_stage_verification.json")).read_text())
        assert gate["status"] == "PASS_STAGE_VERIFIED"
        checked(gate["result"])
    out.mkdir(parents=True, exist_ok=False)
    (out / ".gitignore").write_text("*\n!.gitignore\n")
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    study = LongStudy.discover(Path.cwd())
    write_json(
        out / "identity.json",
        dict(
            plan=ref(plan_path),
            input_contract=plan["input_contract"],
            source=study.contract,
            ledger=41,
            protected_numeric_access=False,
            status="READ_ONLY_STAGE7",
            role_notes={
                "inner_train": "calibration in-sample",
                "inner_validation": "epoch selection",
                "refit": "fresh fit in-sample",
                "development": "exploratory 109 sessions",
            },
        ),
    )
    scores, daily, cohorts, conservation, optimization, case_checks = [], [], [], [], [], []
    sensitivity = []
    results = {
        arm: json.loads((plan_path.parent / run_id / "run_result.json").read_text())
        for arm, run_id in zip(ARMS, RUNS, strict=True)
    }
    training_targets = {}
    for role in ROLES:
        view = scoped_view(study, role, stage=7)
        target = ordered_targets(view)
        version = view.source.fit_version
        recipe = plan["recipes"][version]
        if role in ("inner_train", "refit"):
            training_targets[version] = target
        q = study.targets(role)
        extras = [c for c in q if c not in target and c not in {"origin_id", "ticker"}]
        for arm, run_id in zip(ARMS, RUNS, strict=True):
            destination = out / arm / role
            destination.mkdir(parents=True)
            result = results[arm]
            checkpoint = result["calibration" if version == "inner" else "refit"]
            if role == "development":
                model = model_for(arm)
                saved = torch.load(checked(checkpoint), map_location="cpu", weights_only=True)
                model.load_state_dict(saved["state_dict"])
                f = predict(
                    model, view, arm, dict(run_id=run_id, checkpoint_sha256=checkpoint["sha256"])
                )
            else:
                f = pd.read_parquet(checked(result["artifacts"][role + "_predictions.parquet"]))
            f = canonical(f, target)
            f = f.merge(
                q[["origin_id", "ticker"] + extras],
                on=["origin_id", "ticker"],
                validate="one_to_one",
                sort=False,
            )
            np.testing.assert_allclose(
                f.numerator / (f.cross_section_mad + study.recipe(version)["epsilon"]),
                f.TG20,
                rtol=1e-12,
                atol=1e-12,
            )
            f, pair_frame = allocations(f, arm, recipe)
            f["fit_version"] = version
            f["source_revision"] = study.contract["revision"]
            f.to_parquet(destination / "population.parquet", index=False)
            masks, cutoffs = cohort_masks(f, training_targets[version])
            table = cohort_table(f, masks, cutoffs)
            table["arm"] = arm
            table["role"] = role
            cohorts.append(table)
            write_json(
                destination / "thresholds.json",
                dict(
                    values=cutoffs,
                    training_role="inner_train" if version == "inner" else "refit",
                    ranked_definition=(
                        "floor(pct*N), stable origin/canonical stock ties; within named population"
                    ),
                    range_definition=(
                        "frozen fitting raw TG20 maxima; >= .99/.95; side-specific separate"
                    ),
                ),
            )
            conservation.append(
                dict(
                    arm=arm,
                    role=role,
                    rows=len(f),
                    ordinary_weight=float(f.ordinary_weight.sum()),
                    objective_weight=float(f.normalized_weight.sum()),
                    pointwise=float(f.pointwise.sum()),
                    pairwise=float(f.pairwise.sum()),
                    total=float(f.total.sum()),
                    pair_allocated="PASS",
                    monotonic_rank_identity="PASS",
                    disjoint_cohorts="PASS",
                    inverse_count=0 if arm == "E1" else 1,
                )
            )
            if len(pair_frame) and role == "refit":
                pair_frame.to_parquet(destination / "pair_population.parquet", index=False)
                breakdown = []
                for pct in (1, 5):
                    tail = masks[f"TARGET_RANK_TOP{pct}"].reshape(-1, 20)
                    i, j = np.triu_indices(20, 1)
                    counts = (tail[:, i].astype(int) + tail[:, j]).reshape(-1)
                    for count in range(3):
                        selected = pair_frame.loc[counts == count]
                        breakdown.append(
                            dict(
                                pct=pct,
                                tail_endpoints=count,
                                pairs=len(selected),
                                valid_pairs=int(selected.valid.sum()),
                                weighted_pair_loss=float(selected.weighted_pair_loss.sum()),
                            )
                        )
                pd.DataFrame(breakdown).to_csv(destination / "pair_tail_breakdown.csv", index=False)
            y = f.TG20.to_numpy(dtype=float)
            days = f.session_date_et.to_numpy()
            if arm == "E1":
                probabilities = f[["p_NEG", "p_NORMAL", "p_POS"]].to_numpy(dtype=float)
                metrics = classification(y, probabilities, days, recipe)
                prediction = probabilities[:, 2] - probabilities[:, 0]
            else:
                prediction = f.pred_original_TG20.to_numpy(dtype=float)
                metrics = regression(y, prediction, days)
            d = daily_scores(f, prediction, arm != "E1")
            if arm == "E1":
                d = d.merge(
                    daily_classification(f, probabilities, recipe),
                    on="session_date_et",
                    validate="one_to_one",
                )
            metrics.update({k: float(d[k].mean()) for k in ("top4_recall", "bottom4_recall")})
            scores.append(dict(model=arm, role=role, rows=len(f), sessions=len(d), **metrics))
            d["model"] = arm
            d["role"] = role
            daily.append(d)
            write_json(destination / "metrics.json", metrics)
            if arm == "E1":
                for name, prob in [
                    ("E1_TRAIN_PRIOR", np.tile(recipe["prevalence"], (len(y), 1))),
                    ("E1_ALWAYS_NORMAL", np.tile([0.0, 1.0, 0.0], (len(y), 1))),
                ]:
                    scores.append(
                        dict(
                            model=name,
                            role=role,
                            rows=len(f),
                            sessions=len(d),
                            **classification(y, prob, days, recipe),
                        )
                    )
                    baseline_day = daily_classification(f, prob, recipe)
                    baseline_day["model"] = name
                    baseline_day["role"] = role
                    daily.append(baseline_day)
            quality_mask = (
                f.price_proxy_minute_count.eq(0)
                & f.poor_volume_hour_count.eq(0)
                & f[version + "_feature_fallback_cells"].eq(0)
            )
            for group, mask in [
                ("no_proxy_poor_volume_or_fallback", quality_mask),
                ("any_proxy_poor_volume_or_fallback", ~quality_mask),
            ]:
                g = f.loc[mask]
                if not len(g):
                    sensitivity.append(dict(arm=arm, role=role, group=group, rows=0))
                    continue
                assert g.groupby("origin_id").size().eq(20).all()
                if arm == "E1":
                    values = classification(
                        g.TG20.to_numpy(),
                        g[["p_NEG", "p_NORMAL", "p_POS"]].to_numpy(dtype=float),
                        g.session_date_et.to_numpy(),
                        recipe,
                    )
                else:
                    values = regression(
                        g.TG20.to_numpy(),
                        g.pred_original_TG20.to_numpy(),
                        g.session_date_et.to_numpy(),
                    )
                sensitivity.append(dict(arm=arm, role=role, group=group, rows=len(g), **values))
            if role == "refit":
                case_checks.append(
                    dict(
                        arm=arm, **exact_cases(study, view, f, pair_frame, arm, recipe, destination)
                    )
                )
            print(json.dumps(dict(arm=arm, role=role, status="DIAGNOSTICS_SAVED")), flush=True)
        for name in (*BASELINES, "ZERO"):
            f = target.copy() if name == "ZERO" else canonical(study.prediction(name, role), target)
            prediction = (
                np.zeros(len(f)) if name == "ZERO" else f.pred_original_TG20.to_numpy(dtype=float)
            )
            model_name = "ZERO" if name == "ZERO" else ("T2/42" if "S42" in name else "T2/123")
            metrics = regression(f.TG20.to_numpy(), prediction, f.session_date_et.to_numpy())
            d = daily_scores(f, prediction, True)
            metrics.update({k: float(d[k].mean()) for k in ("top4_recall", "bottom4_recall")})
            scores.append(
                dict(model=model_name, role=role, rows=len(f), sessions=len(d), **metrics)
            )
            d["model"] = model_name
            d["role"] = role
            daily.append(d)
            f["comparison_score"] = prediction
            dest = out / model_name.replace("/", "_") / role
            dest.mkdir(parents=True)
            f.to_parquet(dest / "population.parquet", index=False)
    for arm, result in results.items():
        epochs = json.loads(checked(result["epochs"]).read_text())
        for row in epochs:
            for split in ["training", "validation"]:
                if split not in row:
                    continue
                t = row[split]
                record = {k: v for k, v in t.items() if not isinstance(v, (dict, list))}
                record.update(
                    {
                        "metric_" + k: v
                        for k, v in t["metrics"].items()
                        if not isinstance(v, (list, dict))
                    }
                )
                if row["phase"] == "calibration":
                    record["validation_minus_training_objective"] = (
                        row["validation"]["optimized_objective"]
                        - row["training"]["optimized_objective"]
                    )
                for key in ("preclip", "postclip", "output_distribution"):
                    record.update({key + "_" + k: v for k, v in t.get(key, {}).items()})
                record.update(
                    arm=arm,
                    phase=row["phase"],
                    kind=split,
                    selected_epoch=result["selector"]["selected"],
                    raw_best_epoch=result["selector"]["raw_epoch"],
                    stop_reason=result["selector"]["status"],
                )
                optimization.append(record)
    score_frame = pd.DataFrame(scores)
    daily_frame = pd.concat(daily, ignore_index=True)
    score_frame.to_json(out / "scoreboard.json", orient="records", indent=2)
    score_frame.loc[
        :,
        [
            c
            for c in score_frame
            if not score_frame[c].map(lambda x: isinstance(x, (list, dict))).any()
        ],
    ].to_csv(out / "scoreboard.csv", index=False)
    daily_frame.to_parquet(out / "daily_metrics.parquet", index=False)
    pd.concat(cohorts, ignore_index=True).to_parquet(out / "cohort_metrics.parquet", index=False)
    pd.DataFrame(optimization).to_csv(out / "optimization.csv", index=False)
    pd.DataFrame(conservation).to_csv(out / "objective_conservation.csv", index=False)
    write_json(out / "case_checks.json", case_checks)
    pd.DataFrame(sensitivity).to_json(out / "quality_sensitivity.json", orient="records", indent=2)
    differences = []
    for role in ROLES:
        data = daily_frame.loc[daily_frame.role.eq(role)]
        for arm in ("H2", "W1", "R1", "E1"):
            for baseline in ("T2/42", "T2/123", "ZERO"):
                for metric in ("ic",) if arm == "E1" else ("mse", "ic"):
                    lhs = data.loc[data.model.eq(arm)].set_index("session_date_et")[metric]
                    rhs = data.loc[data.model.eq(baseline)].set_index("session_date_et")[metric]
                    diff = (lhs - rhs).dropna()
                    for block in (1, 2):
                        low, high = month_ci(diff, block)
                        differences.append(
                            dict(
                                role=role,
                                model=arm,
                                baseline=baseline,
                                metric=metric,
                                sessions=len(diff),
                                difference=float(diff.mean()),
                                block_months=block,
                                lower=low,
                                upper=high,
                                seed=22042,
                                bootstrap_replicates=400,
                            )
                        )
        for baseline in ("E1_TRAIN_PRIOR", "E1_ALWAYS_NORMAL"):
            for metric in ("weighted_CE", "CE", "Brier"):
                lhs = data.loc[data.model.eq("E1")].set_index("session_date_et")[metric]
                rhs = data.loc[data.model.eq(baseline)].set_index("session_date_et")[metric]
                diff = (lhs - rhs).dropna()
                for block in (1, 2):
                    low, high = month_ci(diff, block)
                    differences.append(
                        dict(
                            role=role,
                            model="E1",
                            baseline=baseline,
                            metric=metric,
                            sessions=len(diff),
                            difference=float(diff.mean()),
                            block_months=block,
                            lower=low,
                            upper=high,
                            seed=22042,
                            bootstrap_replicates=400,
                        )
                    )
    pd.DataFrame(differences).to_csv(out / "paired_daily_differences.csv", index=False)
    for item in plan["protected_refs"]:
        checked(item)
    write_json(
        out / "stage7_computation_receipt.json",
        dict(
            status="COMPUTATION_VERIFIED_PENDING_REPORT_REVIEW",
            at=now(),
            ledger=41,
            model_starts=0,
            optimizer_steps=0,
            source_preserved=True,
            protected_numeric_access=False,
            seconds=time.monotonic() - started,
            peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            files=[ref(f) for f in out.rglob("*") if f.is_file()],
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run(args.plan, args.out)
