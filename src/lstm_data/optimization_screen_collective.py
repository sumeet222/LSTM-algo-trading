"""Read-only P024 six-arm closeout, including the preserved LRLOW and failed start46."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from .config import fingerprint, now, write_json
from .hf1m_ft16_source import checked, ref
from .objective_screen_diagnostics import canonical
from .objective_screen_metrics import equal_weights, regression
from .optimization_screen import RUNS as ORIGINAL_RUNS
from .optimization_screen import VARIANTS
from .optimization_screen_recovery_authority import RUNS, code_binding, require_complete_gate, rows
from .optimization_screen_supplement import forecast_profile, read_updates
from .visualization.hf1m_long import LongStudy

OLD = Path("reports/experiments/ta024_hf1m_long_optimization_2026-10-23_preparation_v3")
ROLES = ("inner_train", "inner_validation", "refit", "development")
COUNTS = dict(inner_train=88560, inner_validation=15320, refit=104200, development=3660)


def markdown(frame: pd.DataFrame) -> str:
    """Render a small portable table without an optional tabulate dependency."""

    def cell(value: object) -> str:
        if isinstance(value, (float, np.floating)):
            return "undefined" if not np.isfinite(value) else f"{value:.7g}"
        return str(value).replace("|", "/").replace("\n", " ")

    return "\n".join(
        [
            "| " + " | ".join(map(str, frame.columns)) + " |",
            "| " + " | ".join(["---"] * len(frame.columns)) + " |",
        ]
        + [
            "| " + " | ".join(cell(v) for v in row) + " |"
            for row in frame.itertuples(index=False, name=None)
        ]
    )


def collective(plan_path: Path, out: Path) -> None:
    """Require every real gate before combining immutable diagnostics; never create a model."""
    plan = json.loads(plan_path.read_text())
    if plan["code"] != code_binding():
        raise ValueError("P024_FIT_CODE_CHANGED")
    history = rows()
    if [r["run_id"] for r in history if r["status"] == "COMPLETED"] != list(RUNS):
        raise ValueError("P024_ALL_FIVE_RECOVERY_COMPLETIONS_REQUIRED")
    if history[-1]["global_started_pairs"] != 51 or history[-1]["status"] != "COMPLETED":
        raise ValueError("P024_LEDGER51_REQUIRED")
    gates = [checked(plan["completed_lrlow"])] + [
        plan_path.parent / (v.arm + "_immediate_complete.json") for v in VARIANTS[1:]
    ]
    for v, gate in zip(VARIANTS, gates, strict=True):
        require_complete_gate(gate, v.arm)
    for reference in plan["protected_refs"] + plan["baseline_refs"]:
        checked(reference)
    stage0 = json.loads(checked(plan["stage0"]).read_text())
    for reference in stage0["source_hashes"].values():
        checked(reference)
    out.mkdir(parents=True, exist_ok=False)
    (out / ".gitignore").write_text("*\n!.gitignore\n!*.md\n!*.json\n!*.csv\n")
    study = LongStudy.discover(Path.cwd())
    files: dict[str, dict] = {}
    scores, selection, curves, audits, differences, cohorts, sensitivity = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    result_refs = []
    population_checks = []
    for i, (v, gate_path) in enumerate(zip(VARIANTS, gates, strict=True)):
        gate = json.loads(gate_path.read_text())
        base_gate = json.loads(checked(gate["base_gate"]).read_text())
        diag = Path(base_gate["diagnostics"])
        run_id = ORIGINAL_RUNS[0] if i == 0 else RUNS[i - 1]
        root = OLD if i == 0 else plan_path.parent
        result_path = root / run_id / "run_result.json"
        result = json.loads(result_path.read_text())
        result_refs.append(ref(result_path))
        if result["variant"] != asdict(v) or result["status"] != "COMPLETED":
            raise ValueError("P024_VARIANT_OR_COMPLETION")
        if (
            result["initial_hash"] != result["refit_initial_hash"]
            or not result["fresh_optimizer_empty"]
        ):
            raise ValueError("P024_FRESH_REFIT_REQUIRED")
        if len(result["reload_checks"]) != 4 or any(
            c["max_error"] != 0 for c in result["reload_checks"]
        ):
            raise ValueError("P024_EXACT_RELOAD_REQUIRED")
        updates = read_updates(checked(result["optimizer_telemetry"]))
        summaries = result["epochs"]
        cal = [r for r in summaries if r["phase"] == "calibration"]
        sel = result["selector"]
        matched = f"HF1M-LONG-TM0-T2-S{v.seed}-DEV1"
        clipping = int(updates.preclip_norm.gt(1).sum())
        selection.append(
            dict(
                arm=v.arm,
                seed=v.seed,
                parameters=result["parameters"],
                layers=v.layers,
                hidden=v.hidden,
                learning_rate=v.learning_rate,
                head_dropout=v.head_dropout,
                matrix_decay=v.matrix_decay,
                improvement=v.improvement,
                selected=sel["selected"],
                raw_best=sel["raw_epoch"],
                stop=sel["epoch"],
                stop_reason=sel["status"],
                counterfactual_001_selected=result["baseline_counterfactual"]["selected"],
                first_train_zmse=cal[0]["training"]["objective"],
                last_train_zmse=cal[-1]["training"]["objective"],
                first_validation_mse=cal[0]["validation"]["original_mse"],
                last_validation_mse=cal[-1]["validation"]["original_mse"],
                raw_best_validation_mse=sel["raw_min"],
                selected_validation_mse=sel["best"],
                calibration_steps=result["calibration_steps"],
                refit_steps=result["refit_steps"],
                clipped_count=clipping,
                updates=len(updates),
                clipping_fraction=clipping / len(updates),
                nonfinite_count=int((~np.isfinite(updates.preclip_norm)).sum()),
                seconds=result["seconds"],
                peak_rss_bytes=result["peak_rss_bytes"],
                calibration_sha256=result["calibration"]["sha256"],
                refit_sha256=result["refit"]["sha256"],
            )
        )
        audits.append(
            dict(
                arm=v.arm,
                start=45 if i == 0 else 46 + i,
                run_id=run_id,
                core=base_gate["status"],
                supplement=gate["status"],
                status="PASS",
                failed46_preserved=True,
            )
        )
        for r in summaries:
            for kind in ("training", "validation"):
                if kind in r:
                    curves.append(
                        dict(
                            arm=v.arm,
                            phase=r["phase"],
                            kind=kind,
                            **r[kind],
                            qualifies=r.get("qualifies"),
                            selected=r.get("selector", {}).get("selected"),
                        )
                    )
        table = pd.read_parquet(diag / "cohorts.parquet").assign(arm=v.arm)
        cohorts.append(table)
        differences.append(pd.read_csv(diag / "matched_daily_intervals.csv").assign(arm=v.arm))
        m = json.loads((diag / "metrics.json").read_text())
        profiles = json.loads((diag / "supplement_v2/forecast_profiles.json").read_text())
        for item in m:
            if item["model"] == v.arm:
                profile = next(p for p in profiles if p["role"] == item["role"])
                item.update({k: value for k, value in profile.items() if k not in ("arm", "role")})
        scores.extend(m)
        for name in ("gradient_quantiles.csv", "forecast_profiles.json", "model_identity.json"):
            files[v.arm + "/" + name] = ref(diag / "supplement_v2" / name)
        for name in (
            "cases.parquet",
            "case_candles.parquet",
            "case_features.parquet",
            "case_20_returns.parquet",
            "case_verification.json",
        ):
            files[v.arm + "/" + name] = ref(diag / "refit" / name)
        for split in ROLES:
            for name in (
                "population.parquet",
                "daily.parquet",
                "recurrent_state_sample.json",
                "thresholds.json",
            ):
                files[f"{v.arm}/{split}/{name}"] = ref(diag / split / name)
            f = pd.read_parquet(diag / split / "population.parquet")
            if len(f) != COUNTS[split] or f.session_date_et.ge("2026-01-01").any():
                raise ValueError("P024_POPULATION_OR_PROTECTED_DATE")
            w = equal_weights(f.session_date_et.to_numpy())
            fixed = json.loads(
                (result_path.parent / (split + "_checkpoint_metrics.json")).read_text()
            )
            # Fixed training metrics supervise float32 labels; exports retain original64
            # TG20. Use the already approved checkpoint reduction tolerance, unchanged.
            mse = float(w @ ((f.y_hat.to_numpy() - f.TG20.to_numpy()) ** 2))
            np.testing.assert_allclose(mse, fixed["original_mse"], rtol=5e-7, atol=1e-8)
            np.testing.assert_allclose(f.total.sum(), fixed["objective"], rtol=5e-7, atol=1e-8)
            unweighted = float(np.mean((f.y_hat.to_numpy() - f.TG20.to_numpy()) ** 2))
            np.testing.assert_allclose(unweighted, f.squared_error.mean(), rtol=0, atol=0)
            np.testing.assert_allclose(w.sum(), 1, rtol=0, atol=1e-14)
            population_checks.append(
                dict(
                    arm=v.arm,
                    role=split,
                    weighted_original_mse=mse,
                    fixed_float32_original_mse=fixed["original_mse"],
                    unweighted_original_mse=unweighted,
                    unweighted_z_mse=float(f.raw.mean()),
                    weighted_z_mse=float(f.total.sum()),
                    weight_sum=float(w.sum()),
                    checkpoint_rtol=5e-7,
                    checkpoint_atol=1e-8,
                )
            )
            # Add fixed QA sensitivities without changing any eligibility or fitted forecast.
            version = "inner" if split.startswith("inner") else "refit"
            suspect = (
                f.price_proxy_minute_count.gt(0)
                | f.assumed_zero_minute_count.gt(0)
                | f.poor_volume_hour_count.gt(0)
                | f[version + "_feature_fallback_cells"].gt(0)
            )
            for label, mask in (
                ("all", np.ones(len(f), dtype=bool)),
                ("QA_flagged", suspect.to_numpy()),
                ("QA_unflagged", ~suspect.to_numpy()),
            ):
                if mask.any():
                    g = f.loc[mask]
                    w = equal_weights(f.session_date_et.to_numpy())[mask]
                    mass = float(w.sum())
                    error = g.y_hat.to_numpy() - g.TG20.to_numpy()
                    # Partial stock panels retain original mass; fixed20 IC is not defined.
                    sensitivity.append(
                        dict(
                            arm=v.arm,
                            role=split,
                            group=label,
                            rows=len(g),
                            weight_mass=mass,
                            conditional_mse=float(w @ (error**2) / mass),
                            conditional_mae=float(w @ abs(error) / mass),
                            conditional_sign_hit=float(
                                w @ (np.sign(g.y_hat) == np.sign(g.TG20)) / mass
                            ),
                        )
                    )
            # Assert a common ordered population across all arms and both frozen T2 seeds.
            for seed in (42, 123):
                b = canonical(study.prediction(f"HF1M-LONG-TM0-T2-S{seed}-DEV1", split), f)
                np.testing.assert_array_equal(b.TG20, f.TG20)
                if i == 0:
                    prof = forecast_profile(f.assign(pred_original_TG20=b.pred_original_TG20))
                    event = next(
                        item["event_threshold"]
                        for item in m
                        if item["model"] == v.arm and item["role"] == split
                    )
                    w = equal_weights(f.session_date_et.to_numpy())
                    y, hat = f.TG20.to_numpy(), b.pred_original_TG20.to_numpy()
                    mask = abs(y) >= event
                    prof.update(
                        event_threshold=event,
                        event_recall=float(w @ (mask & (abs(hat) >= event)) / w[mask].sum()),
                        tail_mse=float(w[mask] @ ((y[mask] - hat[mask]) ** 2) / w[mask].sum()),
                        nontail_mse=float(
                            w[~mask] @ ((y[~mask] - hat[~mask]) ** 2) / w[~mask].sum()
                        ),
                    )
                    scores.append(
                        dict(
                            model=f"HF1M-LONG-TM0-T2-S{seed}-DEV1",
                            role=split,
                            seed=seed,
                            **regression(
                                f.TG20.to_numpy(),
                                b.pred_original_TG20.to_numpy(),
                                f.session_date_et.to_numpy(),
                            ),
                            **prof,
                        )
                    )
        dev = next(r for r in m if r["model"] == v.arm and r["role"] == "development")
        bd = next(r for r in m if r["model"] == matched and r["role"] == "development")
        delta_mse, delta_ic = dev["mse"] - bd["mse"], dev["daily_ic"] - bd["daily_ic"]
        decision = (
            "inconclusive exploratory positive signal"
            if delta_mse < 0 and delta_ic > 0
            else "unsupported on joint MSE/IC point estimates"
        )
        (plan_path.parent / f"P024_{v.arm}_RESULT.md").write_text(
            f"# P024 {v.arm}: completed\n\nSeed {v.seed}; primary reference T2/{v.seed}. "
            f"Single frozen variant: `{asdict(v)}`. "
            f"Measured parameters {result['parameters']}; calibration stopped "
            f"{sel['epoch']}, qualified-selected {sel['selected']}, raw-best "
            f"{sel['raw_epoch']}; fresh refit {sel['selected']} epochs.\n\n"
            f"Exploratory development MSE {dev['mse']:.9f} (difference {delta_mse:+.9f});"
            f" daily Rank IC {dev['daily_ic']:.9f} (difference {delta_ic:+.9f}). "
            f"Judgment: {decision}. "
            "This is one seed, with 109 reused development sessions. No independent "
            "replication or promotion.\n\n"
            f"Full four-role metrics, exact cases, objective allocation and gradient "
            f"records: `{diag}`. Core and supplemental gates both passed. "
            "Online training uses pre-update/dropout settings; fixed-checkpoint "
            "validation is dropout OFF. Counterfactual selector fields never imply "
            "another trained refit.\n"
        )
    # Keep the richer baseline row when repeated across matched comparisons.
    score_frame = pd.DataFrame(scores)
    score_frame = (
        score_frame.assign(completeness=score_frame.notna().sum(axis=1))
        .sort_values("completeness", kind="stable")
        .drop_duplicates(["model", "role"], keep="last")
        .drop(columns="completeness")
    )
    # ZERO ranking is undefined; do not turn a reference zero line into a measured IC.
    score_frame.loc[score_frame.model.eq("ZERO"), "daily_ic"] = np.nan
    audits.append(
        dict(
            arm="DROP0 original",
            start=46,
            run_id=ORIGINAL_RUNS[1],
            core="NOT_COMPLETED",
            supplement="NOT_COMPLETED",
            status="FAILED_PERMANENT_NO_REFUND",
            failed46_preserved=True,
        )
    )
    sel_frame, audit_frame = pd.DataFrame(selection), pd.DataFrame(audits)
    audit_frame = audit_frame.sort_values("start")
    score_frame.to_json(out / "scores.json", orient="records", indent=2, double_precision=15)
    sel_frame.to_csv(out / "selection.csv", index=False)
    audit_frame.to_csv(out / "stage_audit.csv", index=False)
    pd.DataFrame(curves).to_csv(out / "optimization.csv", index=False)
    difference_frame = pd.concat(differences)
    difference_frame.to_csv(out / "paired_differences.csv", index=False)
    cohort_frame = pd.concat(cohorts)
    cohort_frame.to_parquet(out / "cohorts.parquet", index=False)
    pd.DataFrame(sensitivity).to_json(out / "quality_sensitivity.json", orient="records", indent=2)
    write_json(
        out / "population_consistency.json",
        dict(
            status="PASS_ALL24_REAL_POPULATIONS",
            checks=population_checks,
            tolerances_relaxed=False,
            optimizer_updates=0,
            protected_numeric_access=False,
        ),
    )
    dev = score_frame.loc[
        score_frame.role.eq("development"),
        [
            "model",
            "seed",
            "mse",
            "mae",
            "rmse",
            "daily_ic",
            "prediction_sd",
            "sign_hit",
            "excess_mse",
        ],
    ]
    decisions = []
    for v in VARIANTS:
        a = dev.loc[dev.model.eq(v.arm)].iloc[0]
        b = dev.loc[dev.model.eq(f"HF1M-LONG-TM0-T2-S{v.seed}-DEV1")].iloc[0]
        decisions.append(
            dict(
                arm=v.arm,
                reference=f"T2/{v.seed}",
                mse_difference=a.mse - b.mse,
                ic_difference=a.daily_ic - b.daily_ic,
                sd_ratio_to_baseline=a.prediction_sd / b.prediction_sd,
                judgment="inconclusive positive point estimates"
                if a.mse < b.mse and a.daily_ic > b.daily_ic
                else "unsupported joint improvement",
            )
        )
    decisions_frame = pd.DataFrame(decisions)
    decisions_frame.to_csv(out / "decision_matrix.csv", index=False)
    review = (
        "# P024 collective model comparison\n\nSix successful frozen single-factor arms; "
        "seven charged starts45–51 include preserved failed DROP0 start46. Ledger51/200. "
        "All six core and supplemental gates passed, with four exact full-population "
        "checkpoint reloads per arm. No protected2026 numerical access.\n\n"
        "## Exploratory development\n\n"
        + markdown(dev)
        + "\n\n## Mechanism decision matrix\n\n"
        + markdown(decisions_frame)
        + "\n\nThese are single-seed mechanism screens, without across-seed replication. "
        "Positive point estimates remain inconclusive; larger forecast SD, less clipping or lower "
        "training loss alone does not establish predictive improvement. "
        "ES025/123 uses T2/123 as its only matched primary reference; other arms use "
        "T2/42. No automatic promotion or single winning hyperparameter is declared.\n\n"
        "## Optimization and selection\n\n"
        + markdown(
            sel_frame[
                [
                    "arm",
                    "parameters",
                    "selected",
                    "raw_best",
                    "stop",
                    "counterfactual_001_selected",
                    "first_train_zmse",
                    "last_train_zmse",
                    "clipping_fraction",
                    "seconds",
                ]
            ]
        )
        + "\n\nFull settings, checkpoint hashes, raw/qualified minima, first/last validation "
        "errors and step counts are in selection.csv. "
        "optimization.csv retains online pre-update training z-MSE versus "
        "fixed-checkpoint dropout-OFF validation z-MSE and original TG20 MSE. "
        "The ES025 counterfactual replays historical strict0.1% qualification on the same"
        " available calibration curve only; it is not a counterfactual trained refit. "
        "A counterfactual still CALIBRATING at the observed end is censored. Hidden/cell "
        "sample norms do not prove saturation or vanishing gradients.\n\n"
        "## Uncertainty, conditional skill and falsification\n\npaired_differences.csv "
        "contains signed candidate-minus-reference daily MSE/IC differences and 400 "
        "seed22042 intact-calendar-month and two-month-block intervals for every role. "
        "These are exploratory sensitivity intervals on 109 repeatedly inspected "
        "development sessions, not p-values. The3660 stock rows and overlapping four-hour"
        " outcomes are correlated. "
        "Inner train/refit are in-sample; inner validation selects epochs; roles overlap "
        "and must not be pooled as independent OOS trials. ZERO IC is undefined. "
        "Scores retain original MSE/MAE/RMSE/sign/dispersion, tails and train-frozen "
        "event recall; forecast_profiles.json retains calibration slope/intercept, "
        "residual quantiles and top/bottom4 recall. "
        "quality_sensitivity.json adds flagged/unflagged conditional summaries; per-arm "
        "heterogeneity.csv retains stock/year/era/proxy/zero-volume/fallback weighted "
        "errors. No flagged observation was removed.\n\n"
        "## Research holds\n\nNo trading P&L, alpha claim or protected confirmation "
        "evaluation. Any promising factor needs a separately approved matched second seed"
        " and a new frozen protocol. "
        "The broader10+3 backlog, E1 seed123/calibration, QR1 seed123/state-dependence, "
        "walk-forward, permutation/null and final-confirmation holds remain open. "
        "Rights remain researcher-attested bounded local private use; "
        "publication/action-vintage/clock qualifications persist.\n"
    )
    review += "\n## All role populations\n\n"
    for split in ROLES:
        table = score_frame.loc[
            score_frame.role.eq(split),
            ["model", "seed", "mse", "mae", "rmse", "daily_ic", "sign_hit", "prediction_sd"],
        ]
        review += f"### {split}\n\n{markdown(table)}\n\n"
    review += "## Matched development intervals\n\n"
    paired = difference_frame.loc[
        difference_frame.role.eq("development") & difference_frame.baseline.ne("ZERO"),
        ["arm", "baseline", "metric", "block_months", "sessions", "difference", "low", "high"],
    ]
    review += markdown(paired) + "\n\n## Conditional forecast and tail skill\n\n"
    review += (
        markdown(
            score_frame.loc[
                score_frame.role.eq("development") & score_frame.model.ne("ZERO"),
                [
                    "model",
                    "top4_recall",
                    "bottom4_recall",
                    "calibration_slope_y_on_prediction",
                    "forecast_target_sd_ratio",
                    "event_recall",
                    "tail_mse",
                    "nontail_mse",
                ],
            ]
        )
        + "\n"
    )
    (out / "P024_COLLECTIVE_MODEL_COMPARISON.md").write_text(review)
    tail = cohort_frame.loc[
        cohort_frame.role.eq("refit")
        & cohort_frame.cohort.isin(
            [
                "TARGET_RANK_TOP1",
                "TARGET_RANK_TOP5",
                "RANGE_ABS_0.99",
                "RANGE_ABS_0.95",
                "BOTH_5",
                "NUM_ONLY_5",
                "MAD_ONLY_5",
                "NEITHER_5",
            ]
        ),
        [
            "arm",
            "cohort",
            "rows",
            "row_pct",
            "ordinary_weight_mass",
            "weighted_objective",
            "weighted_loss_share_pct",
            "unweighted_loss_share_pct",
        ],
    ]
    (out / "P024_OBJECTIVE_SPACE_EXTREME_LOSS_ATTRIBUTION.md").write_text(
        "# P024 actual-objective extreme loss attribution\n\nAll six arms optimize the "
        "same equal-session/origin/stock z-MSE with unchanged train-only scale. "
        "These are fixed saved-checkpoint refit in-sample allocations, not online loss or"
        " original-scale MSE.\n\n"
        + markdown(tail)
        + "\n\nRank top1/5% counts observations; .99/.95 times the fitting maximum selects a "
        "magnitude range and can contain one row. "
        "Signed extrema use separate positive/negative train maxima. Numerator/MAD "
        "disjoint cells partition the population; overlapping rank/range/union groups "
        "must not be added. "
        "cohorts.parquet contains all four roles, complements and sign splits, "
        "thresholds, counts, session mass, weighted/unweighted shares. Asinh rank "
        "invariance and group conservation were checked in every immediate gate. "
        "Extreme TG20 may reflect a large genuine numerator, small cross-sectional MAD or"
        " both; no target clipping or floor change was made. "
        "Every arm has22 independently reconstructed genuine all20-return witnesses: top5"
        " refit weighted z-loss for each AAPL/AMZN/TSLA/SBUX, plus BOTH_5 and MAD_ONLY_5 "
        "representatives. "
        "The linked tables preserve48input+4future hours, ET/UTC times, "
        "epsilon/scale/z/y/prediction/errors, all16native/scaled features and "
        "source-quality descriptors. "
        "QA descriptors are retrospective context and do not become decision-time "
        "predictors. Original split/quarantine/COP guards and missing-volume assumptions "
        "persist.\n"
    )
    guide = (
        "# P024 dashboard guide\n\nRun `./scripts/run_track_a_dashboard.sh`, then Explore"
        " → **HF1M Long — Optimization & Capacity (P024)**.\n\n"
        "1. **Start Here**: review all stage gates and ledger51/200. Failed start46 "
        "remains charged.\n"
        "2. Choose the arm and role. **Comparisons** shows original TG20 MSE, daily IC "
        "and matched daily intervals; ES025 uses T2/123. ZERO IC is undefined.\n"
        "3. **Optimization / Gradients** shows actual epoch traces and per-update "
        "gradient quantiles; **Capacity** shows measured shapes/counts and hidden/cell "
        "samples.\n"
        "4. **Forecasts / Residuals** shows target/residual distributions, daily metrics,"
        " calibration and ZERO identity. Select one stock for the frozen matched T2 "
        "overlay.\n"
        "5. **Actual-Objective Tails** compares ranked1/5% and magnitude-range99/95% "
        "losses. Sort and page through all observations; denominator and numerator are "
        "preserved.\n"
        "6. **Exact Cases** selects saved refit witnesses with48input+4future genuine "
        "candles, volume flags, all16features and all20returns. The orange line marks the"
        " input/outcome boundary.\n"
        "7. **History / Features** supports any canonical stock, a≤93day pre2026window "
        "and native/scaled channel values. Missing OHLC is never fabricated; read volume "
        "flags.\n\n"
        "Inner train/refit are in-sample, inner validation selects, development is "
        "exploratory109reused sessions. Protected Jan–Mar2026 is LOCKED. "
        "Prior P021/P022/P023 and legacy sections remain available. Full reports: "
        "P024_COLLECTIVE_MODEL_COMPARISON.md and "
        "P024_OBJECTIVE_SPACE_EXTREME_LOSS_ATTRIBUTION.md alongside this guide. "
        "No trading returns, model promotion or additional training is authorized.\n"
    )
    (out / "P024_DASHBOARD_USER_GUIDE.md").write_text(guide)
    files["guide.md"] = ref(out / "P024_DASHBOARD_USER_GUIDE.md")
    for name in (
        "scores.json",
        "selection.csv",
        "stage_audit.csv",
        "optimization.csv",
        "paired_differences.csv",
        "cohorts.parquet",
        "decision_matrix.csv",
        "quality_sensitivity.json",
        "population_consistency.json",
        "P024_COLLECTIVE_MODEL_COMPARISON.md",
        "P024_OBJECTIVE_SPACE_EXTREME_LOSS_ATTRIBUTION.md",
    ):
        files[name] = ref(out / name)
    write_json(
        out / "viewer_manifest.json",
        dict(
            status="PASS_COLLECTIVE_P024",
            ledger=51,
            source_contract=plan["input_contract"],
            files=files,
            result_refs=result_refs,
            failed46_preserved=True,
            protected_numeric_access=False,
        ),
    )
    write_json(
        plan_path.parent / "stage_9_receipt.json",
        dict(
            status="PASS_COLLECTIVE_P024",
            at=now(),
            ledger=51,
            evidence=[ref(p) for p in out.iterdir() if p.is_file() and p.name != ".gitignore"],
            gates=[ref(p) for p in gates],
            source_files=len(stage0["source_hashes"]),
            execution_sha256=fingerprint(code_binding()),
            optimizer_updates=0,
            protected_numeric_access=False,
        ),
    )
    print(json.dumps(dict(status="PASS_COLLECTIVE_P024", ledger=51, arms=6, output=str(out))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    collective(args.plan, args.out)
