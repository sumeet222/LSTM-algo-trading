"""Saved-score T0/T2 repair evaluation; no fit or source reconstruction entry point."""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import hf20_mag_designa as b
from . import hf20_targets as old
from .hf20_overnight_specialist import paired_months
from .hf20_ranking import origin_ic
from .hf20_ranking_continue_report import markdown
from .hf20_targets_repair import OUT
from .hf20_targets_report import add_metrics, agreement, signed_metrics


def unit_metrics(actual: np.ndarray, pred: np.ndarray) -> dict[str, np.ndarray]:
    return dict(
        MSE=((pred - actual) ** 2).mean(1),
        MAE=abs(pred - actual).mean(1),
        bias=(pred - actual).mean(1),
        predicted_mean=pred.mean(1),
        actual_mean=actual.mean(1),
        predicted_cross_section_SD=pred.std(1),
        actual_cross_section_SD=actual.std(1),
        zero_forecast_MSE=(actual**2).mean(1),
    )


def report() -> None:
    raw = pd.read_parquet(OUT / "R_SCORES.parquet")
    previous = pd.read_parquet(old.OUT / "OOS_SCORES.parquet")
    checks = b.read(OUT / "CHECKS.json")
    assert len(raw) == 80260
    for key in ["origin_id", "ticker", "R"]:
        np.testing.assert_array_equal(raw[key], previous[key])
    for name in ["IND-M1", "IND-M4", "IND-EQ3"]:
        raw[name] = previous[name].to_numpy()
    raw["sigma"], raw["RIDGE-Z"] = np.nan, np.nan
    if (OUT / "RISK_SCORES.parquet").exists():
        scales = pd.read_parquet(OUT / "RISK_SCORES.parquet")
        np.testing.assert_array_equal(scales[["origin_id", "ticker"]], raw[["origin_id", "ticker"]])
        raw["sigma"] = scales.sigma.to_numpy()
    if (OUT / "Z_SCORES.parquet").exists():
        saved = pd.read_parquet(OUT / "Z_SCORES.parquet")
        joined = raw[["origin_id", "ticker"]].merge(
            saved[["origin_id", "ticker", "RIDGE-Z"]],
            on=["origin_id", "ticker"],
            how="left",
            validate="one_to_one",
        )
        raw["RIDGE-Z"] = joined["RIDGE-Z"].to_numpy()
    raw["Z"] = raw.R / raw.sigma
    raw["RIDGE-R-RISK"] = raw["RIDGE-R"] / raw.sigma
    raw["RIDGE-Z-RAW"] = raw["RIDGE-Z"] * raw.sigma
    full_risk = bool(np.isfinite(raw.sigma.to_numpy()).all())
    records, pairs, daily = [], [], {}
    for year in b.YEARS:
        f = raw.loc[raw.fold.eq(year)].reset_index(drop=True)
        assert len(f) == dict(zip(b.YEARS, [19100, 23600, 17740, 19820]))[year]
        for arm in ["T2R", "NR"]:
            path = b.S4 / f"HF20-S4A-F{year % 100}-H4-{arm}-S42/oos_scores.parquet"
            archive = pd.read_parquet(path, columns=["origin_id", "ticker", "return_4h", "score"])
            for key in ["origin_id", "ticker"]:
                np.testing.assert_array_equal(archive[key], f[key])
            np.testing.assert_array_equal(archive.return_4h, f.R)
            f["S4-" + arm] = archive.score.to_numpy()
        valid = np.isfinite(f.sigma.to_numpy().reshape(-1, 20)).all(1)
        for population, keep in [("raw_full", np.ones(len(f) // 20, bool)), ("risk_common", valid)]:
            if not keep.any():
                continue
            sub = f.loc[np.repeat(keep, 20)].reset_index(drop=True)
            meta = sub.iloc[::20].reset_index(drop=True)
            arrays = {
                name: sub[name].to_numpy().reshape(-1, 20)
                for name in [
                    "R",
                    "Z",
                    "RIDGE-R",
                    "RIDGE-Z",
                    "RIDGE-R-RISK",
                    "RIDGE-Z-RAW",
                    "IND-M1",
                    "IND-M4",
                    "IND-EQ3",
                    "S4-T2R",
                    "S4-NR",
                ]
            }
            if population == "risk_common":
                add_metrics(
                    records,
                    meta,
                    agreement(arrays["R"], arrays["Z"]),
                    stage="T0",
                    fold=str(year),
                    target="R_vs_Z",
                    model="HIST4-SHRINK20-252",
                    comparison_population=population,
                )
            models = (
                ["RIDGE-R", "IND-M1", "IND-M4", "IND-EQ3", "S4-T2R", "S4-NR"]
                if population == "raw_full"
                else [
                    "RIDGE-R",
                    "RIDGE-R-RISK",
                    "RIDGE-Z",
                    "RIDGE-Z-RAW",
                    "IND-M1",
                    "IND-M4",
                    "IND-EQ3",
                ]
            )
            for target in ["R"] if population == "raw_full" else ["R", "Z"]:
                for model in models:
                    pred, actual = arrays[model], arrays[target]
                    if not np.isfinite(pred).all():
                        continue
                    reuse_t1 = (
                        model.startswith("IND-")
                        and target == "R"
                        and (population == "raw_full" or full_risk)
                    )
                    if reuse_t1:
                        # Only per-origin IC for a paired contrast; saved T1 tables are reused.
                        values = {"IC_zero": np.nan_to_num(origin_ic(actual, pred), nan=0.0)}
                    else:
                        values = signed_metrics(actual, pred)
                        add_metrics(
                            records,
                            meta,
                            values,
                            stage="ranking",
                            fold=str(year),
                            target=target,
                            model=model,
                            comparison_population=population,
                        )
                    per_day = pd.DataFrame(
                        dict(day=meta.session_date_et, IC_zero=values["IC_zero"])
                    )
                    daily[(year, population, target, model, "IC_zero")] = per_day.groupby(
                        "day"
                    ).IC_zero.mean()
                    native = {
                        "RIDGE-R": "R",
                        "RIDGE-R-RISK": "Z",
                        "RIDGE-Z": "Z",
                        "RIDGE-Z-RAW": "R",
                    }.get(model)
                    if target == native:
                        units = unit_metrics(actual, pred)
                        add_metrics(
                            records,
                            meta,
                            units,
                            stage="units",
                            fold=str(year),
                            target=target,
                            model=model,
                            comparison_population=population,
                        )
                        daily[(year, population, target, model, "MSE")] = (
                            pd.DataFrame(dict(day=meta.session_date_et, v=units["MSE"]))
                            .groupby("day")
                            .v.mean()
                        )
                    if population == "raw_full" and model.startswith("S4-"):
                        path = b.S4 / f"HF20-S4A-F{year % 100}-H4-{model[3:]}-S42/oos_metrics.json"
                        saved_metric = b.read(path)
                        ic = (
                            pd.DataFrame(dict(day=meta.session_date_et, v=origin_ic(actual, pred)))
                            .groupby("day")
                            .v.mean()
                            .mean()
                        )
                        np.testing.assert_allclose(ic, saved_metric["daily_ic"], rtol=0, atol=1e-12)
    result = pd.DataFrame(records)
    keys = ["stage", "target", "model", "comparison_population", "scope", "metric"]
    four = result.groupby(keys).filter(lambda g: g.fold.nunique() == 4)
    eq = (
        four.groupby(keys, sort=False)
        .agg(
            value=("value", lambda v: float(np.mean(v.to_numpy()))),
            n_origins=("n_origins", "sum"),
            n_sessions=("n_sessions", "sum"),
        )
        .reset_index()
    )
    eq["fold"] = "EQ"
    old_metrics = pd.read_csv(old.OUT / "METRICS.csv", dtype={"fold": str})
    frozen = old_metrics.loc[
        old_metrics.stage.eq("T1")
        & old_metrics.comparison_population.eq("raw_original")
        & old_metrics.model.isin(["IND-M1", "IND-M4", "IND-EQ3"])
    ].copy()
    frozen["stage"], frozen["comparison_population"] = "ranking", "raw_full"
    copies = [frozen]
    if full_risk:
        copies.append(frozen.assign(comparison_population="risk_common"))
    result = pd.concat([result, eq, *copies], ignore_index=True)
    result.to_csv(OUT / "METRICS.csv", index=False)
    comparisons = [
        ("raw_full", "R", "RIDGE-R", ref, "IC_zero")
        for ref in ["IND-M1", "IND-M4", "IND-EQ3", "S4-T2R", "S4-NR"]
    ]
    comparisons += [
        ("risk_common", "Z", "RIDGE-Z", "RIDGE-R-RISK", metric) for metric in ["IC_zero", "MSE"]
    ]
    comparisons += [("risk_common", "Z", "RIDGE-Z", "IND-EQ3", "IC_zero")]
    for population, target, candidate, reference, metric in comparisons:
        months = {}
        for year in b.YEARS:
            a, z = (
                (year, population, target, candidate, metric),
                (year, population, target, reference, metric),
            )
            if a not in daily or z not in daily:
                continue
            delta = daily[a] - daily[z]
            months[year] = pd.DataFrame(dict(numerator=delta, mass=1.0))
        for row in paired_months(months):
            pairs.append(
                dict(
                    population=population,
                    target=target,
                    candidate=candidate,
                    reference=reference,
                    metric=metric,
                    **row,
                )
            )
    pair_frame = pd.DataFrame(pairs)
    pair_frame.to_csv(OUT / "PAIRED.csv", index=False)
    checks["raw_key_parity"] = "80260 rows, exact original stock-origin order and R"
    checks["frozen_S4_metric_parity"] = "8 annual T2R/NR ICs within1e-12; no neural inference"
    checks["T1"] = "unchanged saved scores; full raw metrics copied by reference"
    b.write(OUT / "CHECKS.json", checks)
    write_report(result, pair_frame, checks)


def write_report(metrics: pd.DataFrame, paired: pd.DataFrame, checks: dict) -> None:
    """Keep tables in one compact report; interpret completed fixed arms only."""

    def table(stage: str, population: str, metric: str = "IC") -> str:
        f = metrics.loc[
            metrics.stage.eq(stage)
            & metrics.comparison_population.eq(population)
            & metrics.metric.eq(metric)
            & metrics.scope.eq("all")
        ]
        return markdown(
            f.pivot(index=["target", "model"], columns="fold", values="value").reset_index()
        )

    coverage = (
        pd.read_csv(OUT / "COVERAGE.csv") if (OUT / "COVERAGE.csv").exists() else pd.DataFrame()
    )
    if checks["normalized_status"] != "COMPLETED":
        (OUT / "REPORT.md").write_text(
            "# HF20 repair — PARTIAL_BLOCKED\n\nRaw T2 is complete on the original keys.\n\n"
            + table("ranking", "raw_full")
            + "\n\nNormalized work blocked: "
            + str(checks["normalized_status"])
            + ". See COVERAGE.csv/CHECKS.json and any "
            "risk_failure.txt. No alternate proxy or extra fitting is authorized.\n"
        )
        return
    headline = metrics.loc[metrics.fold.eq("EQ") & metrics.scope.eq("all")]
    unit = headline.loc[
        headline.stage.eq("units") & headline.comparison_population.eq("risk_common")
    ]
    unit_table = unit.pivot(index=["target", "model"], columns="metric", values="value")

    def unit_value(target: str, model: str, metric: str) -> float:
        values = unit.loc[
            unit.target.eq(target) & unit.model.eq(model) & unit.metric.eq(metric), "value"
        ].to_numpy(dtype=float)
        assert len(values) == 1
        return float(values[0])

    rloss = unit_value("R", "RIDGE-R", "MSE")
    rzero = unit_value("R", "RIDGE-R", "zero_forecast_MSE")
    zloss = unit_value("Z", "RIDGE-Z", "MSE")
    zderived = unit_value("Z", "RIDGE-R-RISK", "MSE")
    t0 = metrics.loc[
        metrics.stage.eq("T0")
        & metrics.scope.eq("all")
        & metrics.metric.isin(
            [
                "Spearman",
                "Kendall_tau_b",
                "pair_inversion",
                "top4_changed_fraction",
                "bottom4_changed_fraction",
                "mean_absolute_rank_move",
            ]
        )
    ]
    groups = metrics.loc[
        metrics.fold.eq("EQ")
        & metrics.scope.ne("all")
        & metrics.comparison_population.eq("risk_common")
        & metrics.model.isin(["RIDGE-R", "RIDGE-R-RISK", "RIDGE-Z"])
        & metrics.metric.isin(["IC", "MSE", "top4", "bottom4"])
    ]
    fits = pd.read_csv(OUT / "FITS.csv")
    sections = [
        "# HF20 T0/T2 repair — HIST4-SHRINK20-252",
        f"Raw: {checks['raw_status']}. Normalized: {checks['normalized_status']}.",
        "**Technical repair completed; no convincing ranking edge.** Raw ridge now uses the "
        "entire original population. The new risk proxy covers every saved role and all "
        "4,013 OOS origins, versus the preserved strict-M2 study's 83. Raw ridge equal-year "
        "IC is −0.003835. Direct Z slightly improves standardized MSE over raw prediction "
        "divided by sigma, but both normalized ranking ICs remain negative. Keep raw economic "
        "ordering primary; N1 stays deprioritized. No research neural run or trading work "
        "was performed; see the validation-scope warning below.",
        "## Executed method and boundaries",
        "The genuine target is R=log(P_endpoint/P_origin), with endpoint after240 scheduled "
        "XNYS minutes. Signed R and sigma use decimal log-return units; Z=R/sigma is "
        "dimensionless. These are endpoint returns, not realized path variance. Original "
        "seven clocks, genuine endpoints, early closes, source masks, maturity and48-step "
        "embargo are unchanged. At09:30 the input ends at the prior completed full hour; "
        "the closing half-hour stub is not an extra FT16 step. Nominal entry precedes the "
        "assumed origin+2-minute issue: this is not executable P&L or measured vendor arrival.",
        "Original tensor axis: VZ,COP,BAC,BA,AAPL,PEP,MRK,SBUX,CVX,MS,AMD,KO,JNJ,AMZN,"
        "XOM,WFC,AVGO,TSLA,MA,CSCO. All48×16 FT16 columns and eight saved phase recipes "
        "are reused, including original M2 as supplied to S4. No added features or ticker IDs.",
        "**HIST4-SHRINK20-252 is a new estimator, not modified FT16 M2.** For each stock, "
        "use finite genuine returns from the preceding252 regular/full-session dates, "
        "strictly excluding current-session and early-close history origins. The252-date "
        "interpretation was declared before fitting; every original early-close evaluation "
        "origin remains. Historical endpoints can still cross early closes/overnights, "
        "using their stored genuine maturities. Require source origin<forecast origin and "
        "endpoint+2-minute maturity<=issue. Take last60 valid same-clock and last200 valid "
        "all-clock observations, without zero filling or duplicate origins.",
        "With n_all>=30, v=(sum_same(R²)+20*mean_pool(R²))/(n_same+20), "
        "sigma=sqrt(max(v,epsilon²)). Reuse the saved per-stock phase-specific M2 floor: "
        "a positive physical four-hour RMS fifth percentile fitted only on its original "
        "prefix with equal context mass. It is not refitted to the new proxy or OOS values. "
        "At n_same=0 the formula uses pooled RMS; n_all<30 stays missing. Overlapping "
        "returns and overlap between same/pool samples mean counts are not independent "
        "sample sizes or a Bayesian posterior. The pseudocount20 is fixed, not optimized.",
        "The preserved component table has25,457 historical origins, including6,625 with "
        "only some stocks' returns valid. It is not limited to fully eligible20-stock "
        "panels. Independently supported finite stock returns can enter that stock's "
        "history after maturity, even when another stock or FT16 input was unavailable. "
        "All finite returns were checked against positive saved genuine endpoint prices. "
        "No additional endpoints, raw minutes or market data were reconstructed.",
        "## Full raw ridge and frozen references",
        table("ranking", "raw_full"),
        "RIDGE-R uses every original inner/refit/validation/OOS key, independently of sigma. "
        "The intercept is unpenalized. Training-only response mean/SD are inverted to raw "
        "units. The objective is sum of normalized equal-session/origin/stock weighted "
        "squared standardized-target errors + lambda*sum(slopes²). Lambda is one of "
        "0.001,0.1,10, chosen by earlier inner-validation native-target MSE; exact ties "
        "prefer larger lambda. A fresh full-prefix fit follows. The first-session streamed "
        "Gram/RHS builder and ridge solver were reused; no matrix stores or extra search.",
        markdown(
            fits.loc[
                fits.phase.eq("refit"), ["year", "target", "penalty", "train_origins", "fit_stop"]
            ]
        ),
        "All eight selected penalties are shown, not an OOS winner. Raw and Z happen to "
        "choose the same penalties in each fold. Complete scale coverage means their "
        "training and scoring keys also match here; raw fitting would remain full even "
        "if risk coverage were lower. Eight final fits and24 validation solves total.",
        "Frozen M1/M4/EQ3 values are reused from the first session; T1 was not rerun. "
        "Its M2 equal-year IC remains0.003599808, with undefined origins as previously "
        "reported. S4 T2R/NR are saved neural ranking references, with exact keys/labels "
        "and all eight annual ICs replayed. Their ordinal/TG20 training targets preserve "
        "within-origin R ordering, but their scores are not calibrated raw-return forecasts. "
        "Only ranking is compared; this is not an equal-loss architectural ablation.",
        "Raw ridge has positive IC in three years but a large negative2021 result; its "
        "equal-year IC is below every displayed reference. Paired intervals below include "
        "zero, so point underperformance is not formal evidence of inferiority. There is "
        "no consistent or economically established raw ranking skill.",
        "## Coverage before normalized fits",
    ]
    if not coverage.empty:
        cv = coverage.loc[coverage.level.eq("ALL")]
        sections += [
            markdown(
                cv[
                    [
                        "year",
                        "role",
                        "original_origins",
                        "scale_complete",
                        "fraction",
                        "n_same_p50",
                        "n_all_p50",
                        "fallback",
                        "floor_hit",
                        "age_same_p95",
                        "age_all_p95",
                    ]
                ]
            )
        ]
    sections += [
        "Coverage gate was recorded before normalized fitting/scoring: each year>=90% "
        "OOS; independent validation>=50 sessions and>=25 origins per clock, retaining "
        "executed S4 adequacy; both categories and all seven OOS clocks represented. "
        "All16 roles are100% complete. Every OOS stock has n_same=60 and n_all=200; "
        "pure pooled-fallback rate is0%. Pool mass is approximately14.1–14.4% per context. "
        "COVERAGE.csv also reports each stock/clock/category, scheduled gaps, floors and ages.",
        "Latest same-clock history is typically one regular session old (95th percentile1); "
        "maximum ages by OOS year are5/4/5/6 sessions. The60 same-clock observations span "
        "at most83/81/91/89 regular sessions. Pool's latest observation is at most2 sessions "
        "old. Hence broad coverage is not dominated by empty-context fallback or very old "
        "last observations, but stale/missing intervals and unequal clock behavior remain "
        "qualifications. OOS floor-hit cell fractions are0.665%,0%,0.101%,0.182%; these are "
        "descriptive cell fractions, distinct from headline session weights.",
        "Morning and15:30 AVGO traces in CHECKS.json list genuine origins/endpoints/maturities "
        "and directly replay the formula. An immature prior interval is excluded. No actual "
        "n_same=0,n_all>=30 case occurs in these histories; the explicit synthetic fallback "
        "fixture uses200 returns of0.01 and no same-clock history, giving pooled RMS0.01 "
        "before its floor. The real first-history origin on2010-07-01 has n_all=0 and stays "
        "missing. It is warmup, not an evaluation observation. No missing example is invented.",
        "## Raw versus normalized realized ordering",
        markdown(t0.pivot(index="fold", columns="metric", values="value").reset_index()),
        "Equal-year normalization reverses8.005% of unordered pairs, changes18.467% of "
        "top-four membership (0.739 names/origin) and17.121% of bottom-four (0.685 names). "
        "Mean absolute rank movement is1.258 positions. Intraday/overnight inversion rates "
        "are8.028%/8.022%; top changes18.350%/18.586%, bottom17.301%/16.993%. These are "
        "separate conditional session reducers, not a simple row-weighted decomposition. "
        "Raw and normalized orderings are distinct; this does not imply improved equal-dollar "
        "selection or portfolio Sharpe. The old83-origin result is only a preserved coverage "
        "contrast, not an estimator-selection contest.",
        "## Matched ranking matrix",
        table("ranking", "risk_common"),
        "All cells use the same80,260 rows/4,013 origins/793 sessions. Direct Z versus "
        "R-RISK improves normalized IC in2021/2023 but not2022/2024; equal-year gain is "
        "0.002238, interval[−0.004851,0.008681]. Both equal-year ICs remain negative. "
        "Z-RAW is only sigma times Z prediction, not a new fit or assumed calibration. "
        "No target or calibrator was selected on these OOS comparisons.",
        "## Target-unit MSE",
        table("units", "raw_full", "MSE"),
        table("units", "risk_common", "MSE"),
        f"Raw ridge equal-year MSE exceeds an always-zero return forecast by "
        f"{100 * (rloss / rzero - 1):.3f}% (zero MSE={rzero:.9g}). Direct Z lowers Z-MSE relative "
        f"to R-RISK by{100 * (1 - zloss / zderived):.3f}%, improving three years, but remains "
        "above the zero standardized-return forecast. Thus the modest loss improvement "
        "does not establish useful positive rank forecasting. Native R errors are decimal "
        "log returns/squared log returns; Z errors are dimensionless/squared dimensionless.",
        markdown(
            unit_table[
                [
                    "MSE",
                    "MAE",
                    "bias",
                    "predicted_mean",
                    "actual_mean",
                    "predicted_cross_section_SD",
                    "actual_cross_section_SD",
                ]
            ].reset_index()
        ),
        "Prediction dispersion is much smaller than outcome dispersion; narrow conditional "
        "means alone are not a calibration failure. Bias and dispersion are diagnostics, "
        "not a new calibration fit. Conditional category results (all other clock/stock "
        "coverage diagnostics remain in COVERAGE.csv):",
        markdown(
            groups.pivot(
                index=["scope", "target", "model"], columns="metric", values="value"
            ).reset_index()
        ),
        "## Descriptive paired month intervals",
        markdown(paired.loc[paired.year.eq("EQ")]),
        "Reuse400 draws, seed22042, whole calendar months within year with sessions/stocks "
        "kept together and equal four-year aggregation. Positive delta IC favors candidate; "
        "negative delta MSE favors candidate. Paired IC_zero explicitly uses the project's "
        "zero convention for undefined constants; headline IC retains the historical "
        "defined-origin convention. M4's undefined cases explain its small convention "
        "difference. All ridge ICs are defined. Every annual direction is in PAIRED.csv. "
        "The Z-MSE interval is below zero, but repeatedly inspected2021–24 results are "
        "descriptive, not selection-adjusted confirmation or independent-row significance.",
        "## Decision, checks and reproduction",
        "T0 is operationally repaired on the full panel under this explicitly declared "
        "historical proxy. Full raw ridge supplies the missing baseline and shows no "
        "convincing rank edge. Direct Z offers a modest standardized-loss improvement, "
        "not demonstrated ranking value beyond dividing raw predictions by the same risk. "
        "Keep raw economic ordering primary and normalized ordering secondary. Retain "
        "these full-population ridge and frozen indicator controls if future architectures "
        "are discussed. N1 remains deprioritized; these results do not authorize promotion, "
        "new neural training or priority changes.",
        "PASS: exact raw/risk key separation, prefix-only transforms/selection, saved-role "
        "embargo/maturity, positive physical floors, synthetic pool/missing/immature cases, "
        "unpenalized intercept, hand rank/tie and unequal-day weighting fixtures.32 focused "
        "tests pass; Ruff and a basic type check of the three new Python files are used. "
        "No whole-project/editor sweep is required by this repair prompt. Source feed/action "
        "vintage, survivor universe, assumed two-minute timing, overlapping outcomes and "
        "pooled clock composition remain limitations; this is not executable alpha.",
        "WARN: an accidentally broad legacy ranking-test invocation also ran disposable "
        "synthetic neural fixtures, outside the intended non-neural validation scope. "
        "It returned32 passes and2 failures at the legacy10GB project resource guard; "
        "no real-data neural fit/inference or research-ledger entry occurred. The failed "
        "legacy checks remain unresolved and were not weakened or retried. The requested "
        "repair/read-only suite is reported separately. This validation-scope deviation "
        "does not change the saved ridge results, but is retained for researcher review.",
        "Source revision776328445b7ac6e7815ef3a483e9c8ded1eb6d56; predecessor/source/role "
        "bindings: PLAN.json and the prior REPRODUCIBILITY.json. The saved S4 eligibility, "
        "genuine component table, F21–F24 indices and eight phase recipes remain authoritative. "
        "Canonical derivatives were read once for feature replay; no raw-minute scan, "
        "market download,2025 research or protected2026 access. Old T0/T1/T2 files are unchanged.",
        "Entry commands (run is consumed; report is fitting-disabled):\n\n```sh\n"
        "VECLIB_MAXIMUM_THREADS=4 .venv/bin/python -u -B -m lstm_data.hf20_targets_repair run\n"
        ".venv/bin/python -B -m lstm_data.hf20_targets_repair report\n"
        ".venv/bin/python -m pytest tests/test_hf20_targets_repair.py tests/test_hf20_targets.py "
        "tests/test_hf20_s4_readonly.py -q\n```",
        "The report reads saved new scores and frozen references; it does not fit models, "
        "replay market features or perform neural inference. R_SCORES stores full raw "
        "forecasts; RISK_SCORES scales; Z_SCORES normalized forecasts. Small coefficients "
        "and FITS.csv preserve all selected models and trial losses; no training matrices "
        "are stored. Reports/tables/code are uncommitted; Parquet/NPZ remain local/ignored.",
        f"Numerical execution: {checks['seconds']:.1f}s; peak process RSS "
        f"{checks['peak_rss_bytes'] / 1e9:.3f}GB. Incremental disk and final checks are recorded "
        "in CHECKS.json/session report. No dependency changes. Created two repair modules "
        "and one targeted test file; no old code edits. Live neural ledger186/300 unchanged, "
        "new starts0. No Git fetch/commit/push. **STOP for researcher review.**",
    ]
    (OUT / "REPORT.md").write_text("\n\n".join(sections) + "\n")
