"""Report-only T0–T2 reducers; never loads market inputs or fits a predictor."""

from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

from . import hf20_mag_designa as b
from .hf20_mag_rank_report import membership
from .hf20_overnight_specialist import paired_months
from .hf20_ranking import origin_ic, origin_weights, ranks
from .hf20_ranking_continue_report import markdown
from .hf20_targets import OUT

INDICATORS = ["IND-M1", "IND-M2", "IND-M4", "IND-EQ3"]
RIDGES = ["RIDGE-R", "RIDGE-R-RISK", "RIDGE-Z", "RIDGE-Z-RAW"]
PAIR_I, PAIR_J = np.triu_indices(20, 1)


def signed_metrics(actual: np.ndarray, score: np.ndarray) -> dict[str, np.ndarray]:
    """S4 signed-target rank/tie conventions; no magnitude-only target helper."""
    sign = np.sign(actual[:, PAIR_I] - actual[:, PAIR_J])
    pred = np.sign(score[:, PAIR_I] - score[:, PAIR_J])
    valid = sign != 0
    ic = origin_ic(actual, score)
    return dict(
        IC=ic,
        IC_zero=np.nan_to_num(ic, nan=0.0),
        undefined_IC_rate=(~np.isfinite(ic)).astype(float),
        constant_rate=(np.ptp(score, axis=1) == 0).astype(float),
        pair_concordance=np.divide(
            (((sign * pred > 0) + 0.5 * (pred == 0)) * valid).sum(1),
            valid.sum(1),
            out=np.full(len(score), np.nan),
            where=valid.sum(1) > 0,
        ),
        top4=(membership(actual) * membership(score)).sum(1) / 4,
        bottom4=(membership(actual, False) * membership(score, False)).sum(1) / 4,
        pair_tie_rate=(pred == 0).mean(1),
    )


def agreement(raw: np.ndarray, scaled: np.ndarray) -> dict[str, np.ndarray]:
    """Kendall tau-b and strict inversions among all190 unordered stock pairs."""
    a = np.sign(raw[:, PAIR_I] - raw[:, PAIR_J])
    z = np.sign(scaled[:, PAIR_I] - scaled[:, PAIR_J])
    denom = np.sqrt((a != 0).sum(1) * (z != 0).sum(1))
    m = signed_metrics(raw, scaled)
    return dict(
        Spearman=m["IC"],
        Kendall_tau_b=np.divide(
            (a * z).sum(1), denom, out=np.full(len(raw), np.nan), where=denom > 0
        ),
        pair_inversion=(a * z < 0).mean(1),
        raw_pair_ties=(a == 0).mean(1),
        top4_changed_fraction=1 - m["top4"],
        bottom4_changed_fraction=1 - m["bottom4"],
        top4_changed_count=4 * (1 - m["top4"]),
        bottom4_changed_count=4 * (1 - m["bottom4"]),
        mean_absolute_rank_move=abs(ranks(raw) - ranks(scaled)).mean(1),
    )


def add_metrics(records: list, meta: pd.DataFrame, values: dict, **labels) -> None:
    """Conditional group reductions re-equalize eligible origins within session."""
    for scope, keep in [
        ("all", np.ones(len(meta), dtype=bool)),
        *[(str(c), meta.category.eq(c).to_numpy()) for c in meta.category.unique()],
    ]:
        frame = pd.DataFrame({k: v[keep] for k, v in values.items()})
        frame["day"] = meta.session_date_et.to_numpy()[keep]
        means = frame.groupby("day").mean().mean()
        for metric, value in means.items():
            records.append(
                dict(
                    **labels,
                    scope=scope,
                    metric=metric,
                    value=float(value),
                    n_origins=len(frame),
                    n_sessions=frame.day.nunique(),
                )
            )


def quantile(values: np.ndarray, weights: np.ndarray, probability: float) -> float:
    """Inverse weighted empirical CDF, for descriptive distributions only."""
    order = np.argsort(values)
    cumulative = np.cumsum(weights[order]) / weights.sum()
    return float(values[order[min(np.searchsorted(cumulative, probability), len(order) - 1)]])


def report() -> None:
    scores = pd.read_parquet(OUT / "OOS_SCORES.parquet")
    checks = b.read(OUT / "CHECKS.json")
    if "saved_scores_sha256" in checks:
        assert b.digest(OUT / "OOS_SCORES.parquet") == checks["saved_scores_sha256"]
    records, pairs, stock_rows, distributions = [], [], [], []
    daily, raw_daily = {}, {}
    for year in b.YEARS:
        original = scores.loc[scores.fold.eq(year)].reset_index(drop=True)
        common = original.loc[original.risk_valid].reset_index(drop=True)
        assert len(original) == dict(zip(b.YEARS, [19100, 23600, 17740, 19820]))[year]
        for population, frame in [("raw_original", original), ("risk_common", common)]:
            if frame.empty:
                continue
            assert frame.groupby("origin_id").size().eq(20).all()
            np.testing.assert_array_equal(
                frame.ticker.to_numpy().reshape(-1, 20),
                np.tile(b.SYMBOLS, (len(frame) // 20, 1)),
            )
            meta = frame.iloc[::20].reset_index(drop=True)
            arrays = {c: frame[c].to_numpy().reshape(-1, 20) for c in ["R", *INDICATORS]}
            if population == "raw_original":
                for a, z in itertools.combinations(INDICATORS[:3], 2):
                    add_metrics(
                        records,
                        meta,
                        {
                            "IC": origin_ic(arrays[a], arrays[z]),
                            "pair_inversion": agreement(arrays[a], arrays[z])["pair_inversion"],
                        },
                        stage="T1_complementarity",
                        fold=str(year),
                        target=a,
                        model=z,
                        comparison_population=population,
                    )
            if population == "risk_common":
                arrays.update(
                    {
                        c: frame[c].to_numpy().reshape(-1, 20)
                        for c in ["Z", *RIDGES]
                        if frame[c].notna().all()
                    }
                )
                assert all(np.isfinite(v).all() for v in arrays.values())
                add_metrics(
                    records,
                    meta,
                    agreement(arrays["R"], arrays["Z"]),
                    stage="T0",
                    fold=str(year),
                    target="R_vs_Z",
                    model="realized",
                    comparison_population=population,
                )
                for a, z in itertools.combinations(INDICATORS[:3], 2):
                    add_metrics(
                        records,
                        meta,
                        {
                            "IC": origin_ic(arrays[a], arrays[z]),
                            "pair_inversion": agreement(arrays[a], arrays[z])["pair_inversion"],
                        },
                        stage="T1_complementarity",
                        fold=str(year),
                        target=a,
                        model=z,
                        comparison_population=population,
                    )
                w = np.repeat(origin_weights(meta.session_date_et.to_numpy()) / 20, 20)
                for column in ["sigma", "native_rms", "R", "Z"]:
                    vals = frame[column].to_numpy()
                    if column in ["R", "Z"]:
                        vals = abs(vals)
                    row: dict[str, str | float] = dict(fold=str(year), variable=column)
                    row.update(
                        {f"p{p:g}": quantile(vals, w, p / 100) for p in [0, 1, 5, 50, 95, 99, 100]}
                    )
                    row["weighted_mean"] = float(w @ vals)
                    distributions.append(row)
                add_metrics(
                    records,
                    meta,
                    {
                        "floor_hit_rate": frame.floor_hit.to_numpy().reshape(-1, 20).mean(1),
                        "abs_Z_gt_3": (abs(arrays["Z"]) > 3).mean(1),
                        "abs_Z_gt_5": (abs(arrays["Z"]) > 5).mean(1),
                    },
                    stage="T0",
                    fold=str(year),
                    target="sigma",
                    model="RMS60",
                    comparison_population=population,
                )
                move = ranks(arrays["Z"]) - ranks(arrays["R"])
                ow = origin_weights(meta.session_date_et.to_numpy())
                for j, ticker in enumerate(b.SYMBOLS):
                    stock_rows.append(
                        dict(
                            fold=str(year),
                            ticker=ticker,
                            mean_absolute_rank_move=float(ow @ abs(move[:, j])),
                            mean_signed_rank_move=float(ow @ move[:, j]),
                            mean_sigma=float(ow @ frame.sigma.to_numpy().reshape(-1, 20)[:, j]),
                        )
                    )
            for target in ["R"] if population == "raw_original" else ["R", "Z"]:
                for model in INDICATORS if population == "raw_original" else INDICATORS + RIDGES:
                    if model not in arrays:
                        continue
                    values = signed_metrics(arrays[target], arrays[model])
                    stage = "T1" if model in INDICATORS else "T2"
                    add_metrics(
                        records,
                        meta,
                        values,
                        stage=stage,
                        fold=str(year),
                        target=target,
                        model=model,
                        comparison_population=population,
                    )
                    if population == "risk_common":
                        daily[(year, target, model)] = (
                            pd.DataFrame(dict(day=meta.session_date_et, IC=values["IC_zero"]))
                            .groupby("day")
                            .IC.mean()
                        )
                    else:
                        raw_daily[(year, model)] = (
                            pd.DataFrame(dict(day=meta.session_date_et, IC=values["IC_zero"]))
                            .groupby("day")
                            .IC.mean()
                        )
                    native_target = {
                        "RIDGE-R": "R",
                        "RIDGE-R-RISK": "Z",
                        "RIDGE-Z": "Z",
                        "RIDGE-Z-RAW": "R",
                    }.get(model)
                    if target == native_target:
                        actual, pred = arrays[target], arrays[model]
                        add_metrics(
                            records,
                            meta,
                            dict(
                                MSE=((actual - pred) ** 2).mean(1),
                                MAE=abs(actual - pred).mean(1),
                                bias=(pred - actual).mean(1),
                                actual_mean=actual.mean(1),
                                predicted_mean=pred.mean(1),
                                actual_RMS=np.sqrt((actual**2).mean(1)),
                                predicted_RMS=np.sqrt((pred**2).mean(1)),
                                actual_cross_section_SD=actual.std(1),
                                predicted_cross_section_SD=pred.std(1),
                            ),
                            stage="T2_units",
                            fold=str(year),
                            target=target,
                            model=model,
                            comparison_population=population,
                        )
    result = pd.DataFrame(records)
    keys = ["stage", "target", "model", "comparison_population", "scope", "metric"]
    complete_groups = result.groupby(keys, sort=False).filter(lambda g: g.fold.nunique() == 4)
    eq = (
        complete_groups.groupby(keys, sort=False)
        .agg(
            value=("value", lambda v: float(np.mean(v.to_numpy()))),
            n_origins=("n_origins", "sum"),
            n_sessions=("n_sessions", "sum"),
        )
        .reset_index()
    )
    eq["fold"] = "EQ"
    result = pd.concat([result, eq], ignore_index=True)
    for year in b.YEARS:
        archived = b.read(b.S4 / f"F{year % 100}_S4_N1/oos_metrics.json")
        own = (
            result.loc[
                result.fold.eq(str(year))
                & result.model.eq("IND-M1")
                & result.comparison_population.eq("raw_original")
                & result.scope.eq("all")
            ]
            .set_index("metric")
            .value
        )
        for metric, old in [
            ("IC", "daily_ic"),
            ("top4", "top4"),
            ("bottom4", "bottom4"),
            ("pair_concordance", "pair_concordance"),
        ]:
            np.testing.assert_allclose(own[metric], archived[old], rtol=0, atol=1e-12)
    result.to_csv(OUT / "METRICS.csv", index=False)
    # Fixed explanatory comparisons; no OOS-based sign or score choice.
    comparisons = [(t, "IND-EQ3", "IND-M1") for t in ["R", "Z"]]
    comparisons += [("R", "RIDGE-R", c) for c in ["IND-M1", "IND-EQ3"]]
    comparisons += [("Z", m, c) for m in ["RIDGE-R-RISK", "RIDGE-Z"] for c in ["IND-M1", "IND-EQ3"]]
    comparisons += [("Z", "RIDGE-Z", "RIDGE-R-RISK")]
    for target, candidate, reference in comparisons:
        months = {}
        for year in b.YEARS:
            if (year, target, candidate) not in daily or (year, target, reference) not in daily:
                continue
            delta = daily[(year, target, candidate)] - daily[(year, target, reference)]
            months[year] = pd.DataFrame(dict(numerator=delta, mass=1.0))
        for row in paired_months(months):
            n_months = sum(g.index.astype(str).str[:7].nunique() for g in months.values())
            if row["year"] != "EQ":
                n_months = months[int(row["year"])].index.astype(str).str[:7].nunique()
            if n_months < 2:
                row["low"], row["high"] = np.nan, np.nan
            pairs.append(
                dict(
                    target=target,
                    candidate=candidate,
                    reference=reference,
                    comparison_population="risk_common",
                    n_months=n_months,
                    interval_status="DEGENERATE_ONE_MONTH" if n_months < 2 else "DESCRIPTIVE",
                    **row,
                )
            )
    months = {}
    for year in b.YEARS:
        delta = raw_daily[(year, "IND-EQ3")] - raw_daily[(year, "IND-M1")]
        months[year] = pd.DataFrame(dict(numerator=delta, mass=1.0))
    for row in paired_months(months):
        pairs.append(
            dict(
                target="R",
                candidate="IND-EQ3",
                reference="IND-M1",
                comparison_population="raw_original",
                interval_status="DESCRIPTIVE",
                n_months=(
                    sum(g.index.astype(str).str[:7].nunique() for g in months.values())
                    if row["year"] == "EQ"
                    else months[int(row["year"])].index.astype(str).str[:7].nunique()
                ),
                **row,
            )
        )
    pd.DataFrame(pairs).to_csv(OUT / "PAIRED.csv", index=False)
    dist = pd.DataFrame(distributions)
    write_summary(scores, checks, result, pd.DataFrame(pairs), dist)


def write_summary(
    scores: pd.DataFrame,
    checks: dict,
    metrics: pd.DataFrame,
    paired: pd.DataFrame,
    distributions: pd.DataFrame,
) -> None:
    """Compact evidence report, including unsupported folds rather than invented headlines."""

    def table(stage: str, population: str, metric: str = "IC") -> str:
        f = metrics.loc[
            metrics.stage.eq(stage)
            & metrics.comparison_population.eq(population)
            & metrics.scope.eq("all")
            & metrics.metric.eq(metric)
        ]
        return markdown(
            f.pivot(index=["target", "model"], columns="fold", values="value").reset_index()
        )

    common = scores.loc[scores.risk_valid]
    common_meta = common.iloc[::20]
    pooled = agreement(common.R.to_numpy().reshape(-1, 20), common.Z.to_numpy().reshape(-1, 20))
    coverage = pd.DataFrame(checks["coverage"])
    support = coverage.pivot(index="year", columns="role", values="risk_origins").reset_index()
    t0 = metrics.loc[
        metrics.stage.eq("T0")
        & metrics.target.eq("R_vs_Z")
        & metrics.scope.eq("all")
        & metrics.metric.isin(
            [
                "Spearman",
                "Kendall_tau_b",
                "pair_inversion",
                "top4_changed_fraction",
                "bottom4_changed_fraction",
            ]
        )
    ]
    t1 = metrics.loc[
        metrics.stage.eq("T1")
        & metrics.comparison_population.eq("raw_original")
        & metrics.scope.eq("all")
        & metrics.fold.eq("EQ")
        & metrics.metric.isin(
            ["top4", "bottom4", "pair_concordance", "undefined_IC_rate", "IC_zero"]
        )
    ]
    complement = metrics.loc[
        metrics.stage.eq("T1_complementarity")
        & metrics.comparison_population.eq("raw_original")
        & metrics.scope.eq("all")
        & metrics.fold.eq("EQ")
    ]
    units = metrics.loc[
        metrics.stage.eq("T2_units")
        & metrics.scope.eq("all")
        & metrics.metric.isin(
            ["MSE", "bias", "actual_cross_section_SD", "predicted_cross_section_SD"]
        )
    ]
    unit_table = units.pivot(index=["fold", "target", "model"], columns="metric", values="value")
    selected_pairs = paired.loc[
        (paired.comparison_population.eq("raw_original") & paired.year.eq("EQ"))
        | (
            paired.year.eq("2023")
            & paired.candidate.isin(["RIDGE-R", "RIDGE-Z"])
            & paired.reference.isin(["IND-M1", "RIDGE-R-RISK"])
        )
    ]
    tails = distributions.loc[
        ~distributions.variable.eq("native_rms"), ["fold", "variable", "p0", "p50", "p99", "p100"]
    ]
    validation = checks.get("validation", {})
    eq3_delta = paired.loc[
        paired.comparison_population.eq("raw_original") & paired.year.eq("EQ")
    ].iloc[0]
    footprint = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    human = validation.get("human_editor", "pending fresh VSCode Problems refresh for this task")
    complement_table = markdown(
        complement.pivot(index=["target", "model"], columns="metric", values="value").reset_index()
    )
    pair_table = markdown(
        selected_pairs[
            [
                "comparison_population",
                "target",
                "candidate",
                "reference",
                "year",
                "delta",
                "low",
                "high",
                "n_months",
            ]
        ]
    )
    text = f"""# HF20 T0–T2: raw versus ex-ante RMS-normalized ranking

**PARTIAL_BLOCKED — retain raw-return ordering as the primary outcome.** The original raw
indicator comparison is complete on all 80,260 rows. The required 20-stock RMS coverage leaves
only {len(common_meta)}/4,013 origins ({len(common_meta) / 4013:.2%}), with no 2024 support.
Consequently there is **no four-year normalized-target or ridge conclusion**. This is a
coverage failure, not empirical evidence that risk normalization is inferior. No ARCH-N1 work
was launched.

## 1. Frozen design and causal scale

Source: pinned `mito0o852/OHLCV-1m` revision `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`, using
only authorized saved adjusted hourly derivatives and genuine endpoint returns. Executed S4
directory: `reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation`. Its
`opening_reaudit_v2/S4_ORIGIN_SOURCE_ELIGIBILITY.parquet`,
`S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet`, `F21–F24_*_indices.csv`, and eight
`*_recipe.json` files are the actual bindings; exact IDs/hashes are in REPRODUCIBILITY.json.
The S9 `S4_REUSED_RECIPES.json` independently authenticates the same recipes. No reconstructed
calendar split or substitute indicator was used.

The tensor order remains
VZ,COP,BAC,BA,AAPL,PEP,MRK,SBUX,CVX,MS,AMD,KO,JNJ,AMZN,XOM,WFC,AVGO,TSLA,MA,CSCO. Original
annual rows are 19,100/23,600/17,740/19,820 (955/1,180/887/991 origins),793 sessions total. R
is the signed genuine 240-scheduled-XNYS-minute endpoint log return. Nominal entry precedes the
assumed issuance by approximately 2 minutes; actual vendor arrival is unmeasured. Calendar,
early-close and overnight definitions remain those stored by S4.

**Explicit convention difference:** executed M2 uses the preceding 60 *regular-session
scheduled occurrences*, locked strictly before 09:30 on the historical input session, retaining
unavailable slots as missing. It needs 57 finite outcomes and rejects three consecutive missing
slots. We reuse the physical RMS at the latest actual S4 input step and the forecast clock
context. At 09:30 this inherits the prior input-session lock. This conservative, potentially
stale denominator is not a newly refreshed issue-time volatility forecast. The saved per-stock
floor is the prefix-fitted fifth percentile of positive RMS values with equal mass across seven
contexts; inner/refit floors and feature recipes remain phase-specific. Sigma=max(native
RMS,floor); missing RMS is never filled. Z=R/sigma. No scaled V2 or future volatility is used.

Weights are equal stocks within origin, equal eligible origins within session, equal sessions
within year, then equal four annual scores only when all four exist. Rank ties use midranks;
top/bottom membership is fractional at boundary ties. Constant scores have undefined historical
IC; the separately labeled zero convention and its frequency are retained. METRICS.csv includes
annual/category rank, retrieval, pair, tie and output-unit diagnostics.

## 2. Coverage is the decisive limitation

Risk-complete origin counts by saved role:

{markdown(support)}

OOS coverage is 3/955,56/1,180,24/887,0/991. All 78 intraday origins are 11:30; the five
overnight origins are 15:30 in 2022. No 09:30,10:30,12:30,13:30 or 14:30 origin is
risk-complete. The 2021 sample is just January 14,15,19;2023 is January–February. Only 1,660
stock rows and 83 sessions support the target comparison. This is not representative
seven-clock coverage.

Native sigma is unavailable in 88.99% of AVGO OOS rows,48.37% for MA and 36.36% for AMZN
(simple row proportions, not headline weights). One missing stock removes an origin from the
common 20-stock analysis. S4 features retain their original prefix fallbacks, so raw-only
indicators remain evaluable. F22/F24 have zero risk-valid inner-validation origins, blocking
both ridge target variants there. F24 also has no risk-valid OOS origins. No stocks, coverage
rule, source or validation window were changed to rescue these arms.

## 3. T0 — realized ordering differs, on a very narrow sample

{markdown(t0.pivot(index="fold", columns="metric", values="value").reset_index())}

For the 83 available origins pooled descriptively (each has its own session; **not an
equal-four-year score**), Spearman is{pooled["Spearman"].mean():.4f}, Kendall
tau-b{pooled["Kendall_tau_b"].mean():.4f}, and{pooled["pair_inversion"].mean():.2%} of 190
pairs invert. Top-four membership changes{pooled["top4_changed_fraction"].mean():.2%} (0.807
names/origin), bottom-four{pooled["bottom4_changed_fraction"].mean():.2%} (0.819 names/origin).
Raw target pairs have no ties in this sample. In the five overnight cases, inversions are
9.47%, top-four changes 25%, bottom-four 30%; this cannot establish an overnight effect.

Sigma and absolute-target distributions below use annual hierarchical weighted empirical
quantiles; R and sigma are decimal log-return units, Z dimensionless. No common OOS cell hits
its floor. Minimum sigma is 0.004739, so the observed differences are not numerical near-zero
divisions. The largest absolute Z is 5.305; normalized tails remain. Per-stock exploratory
movements include high-risk TSLA/AMD and lower-risk PEP; normalization moves positive low-risk
returns upward and negative low-risk returns downward relative to peers, preserving individual
signs. It is not universally a preference for low-risk stocks. Common TG20 median/MAD
transformation preserves raw ordering; individual sigma division need not.

{markdown(tails)}

## 4. T1 — distinct indicators, weak evidence of incremental prediction

Original raw population, annual and equal-four-year historical Spearman IC:

{table("T1", "raw_original")}

M1 is the executed latest normalized hourly open-to-close movement; M2 is the same-context
historical mean 20/RMS60 indicator; M4 is the executed older daily momentum excluding the
newest approximately 20 sessions. Positive signs are fixed. Each is converted to normalized
ascending cross-sectional midranks; EQ3 is their unweighted mean. Native scaling/fallbacks are
preserved. BASELINE-N1 is M1, not proposed ARCH-N1. Archived M1 scores, keys and R match
exactly, and all four annual IC/retrieval/pair metrics replay within 1e-12; equal-year IC is
0.003382987.

Equal-year retrieval/pair/undefined-IC diagnostics:

{markdown(t1.pivot(index="model", columns="metric", values="value").reset_index())}

M2 and M4 have undefined/constant cross-sections at 3.40% and 5.63% under hierarchical
weighting; M1/EQ3 have none. Historical IC excludes undefined origins within each day's defined
support. IC_zero instead assigns them 0; these differ and are not silently interchanged.
Top/bottom chance retrieval is 0.20 and pair chance credit 0.50.

The indicators give substantially different orderings:

{complement_table}

M1–M2 and M1–M4 rank correlations are only 0.0098/0.0047, but difference alone is not useful
complementarity. EQ3 exceeds M1 IC in three of four years by an equal-year {eq3_delta.delta:.6f},
with descriptive 95% interval [{eq3_delta.low:.6f}, {eq3_delta.high:.6f}].
Its top-four retrieval is lower than M1. Thus the
fixed combination does not establish a reliable incremental advantage.

Matched risk-valid indicators, with identical raw/Z keys within each displayed fold:

{table("T1", "risk_common")}

There is no 2024 result or four-year average. Normalized IC changes sign/direction across these
sparse slices; they cannot identify a winning target.

## 5. T2 — valid partial fits, insufficient comparative evidence

Inputs are all 48×16=768 chronological FT16 values, not the 112-column alternative. One pooled
stock-shared model per target includes an unpenalized intercept. Training-only target mean/SD
are inverted back to R or Z units. The objective is weighted mean squared standardized-target
error plus lambda times squared slopes; observation weights sum 1. Penalties were fixed at
0.001,0.1,10 and selected by earlier inner-validation native-target MSE, with exact ties
preferring larger lambda. Full-prefix refits use the same risk-complete origins for R and Z.
F21 selected 10 for both; F23 selected 0.1 for both. Neither feature scales nor penalties use
OOS observations.

Four final target fits and 12 inner target trial solves were executed: R/Z in F21 and F23 only.
F22/F24 were not fitted. IND-RIDGE3 was omitted. R-RISK divides the saved raw forecast by
sigma; Z-RAW multiplies the saved Z forecast by sigma; neither is another fit. Cross-target
ranking matrix:

{table("T2", "risk_common")}

The F21 results use only 3 origins; F23 only 24. RIDGE-R beats M1 raw IC in F21 but not F23.
Direct Z has slightly higher Z IC than R-RISK in both, but F23 both remain negative. This does
not establish consistent ridge superiority or select a target/architecture. Target-unit
diagnostics (MSE in squared log-return units for R and squared standardized units for Z; SD is
the mean within-origin cross-sectional SD):

{markdown(unit_table.reset_index())}

Forecast dispersion is much smaller than realized dispersion. A conditional-mean forecast can
be narrow without being wrongly calibrated; this tiny sample cannot establish calibration.
Z-RAW is a derived diagnostic, not automatically a calibrated raw-return forecast.

Paired IC differences, candidate minus reference; positive favors candidate:

{pair_table}

The existing 400-draw, seed 22042 whole-calendar-month within-year routine is reused, retaining
whole sessions/cross-sections. F21 has one month, so its degenerate interval is suppressed as
uninformative in PAIRED.csv. F23 has only two months; even the positive direct-Z versus R-RISK
interval is fragile and not selection-adjusted confirmation. All 2021–24 years have been
repeatedly researched. No independent-row inference is reported.

## 6. Decision and minimal next decision

Keep **raw signed-return ordering primary** for the stated equal-dollar long-upper/short-lower
economic question. Dividing each stock by its own sigma changes that economic ordering; it is a
distinct secondary risk-aware question, not an automatic improvement in portfolio returns.
Covariance, exposures, execution and costs remain necessary for any portfolio claim.

The highest-information next design decision is whether ARCH-N1 should learn a **direct
residual rank correction around M1**, with a matched linear correction control, versus a
raw-return prediction objective. This is a hypothesis for researcher discussion, not approval
to train either. The present raw indicators provide a reproducible anchor; the sparse ridge
comparison cannot adjudicate the objectives. Before a full normalized-target comparison, a
researcher must approve a coverage remedy and verify lawful historical validation support. The
minimal remedy is an explicitly approved historical support/validation plan using existing
permitted derivatives; do not silently relax 57/60, impute sigma, drop stocks, shift OOS keys
or choose a penalty from OOS results.

## 7. Correctness, reproduction and stop

| Check | Result |
| --- | --- |
| Exact S4 keys/order | PASS: all 80,260 original rows; risk exclusions explicit; archived M1 \
parity |
| Causality | PASS: morning/overnight three-history traces, strict lock and endpoint+2 \
maturity; immature overnight observation excluded |
| Floors/ranks | PASS: positive prefix floors, synthetic low-vol floor hit, sign/tie/TG20 \
fixture, no nonfinite admitted Z |
| Training isolation | PASS: saved roles, genuine maturity cutoffs,48-completed-step embargo, \
saved phase recipes; F22/F24 fitting BLOCKED |
| Metrics | PASS: hand origin, unequal-origin day weights, signed pair/tie fixtures; no \
portfolio results |

Focused tests: 29 passed; Ruff passes. Full installed Pylance/basic analyzes 549 Python files
with zero errors/warnings without changed severity/exclusions. Human editor check: {human}.
Source vintage/vendor provenance, surviving-universe bias, nominal-origin/+2-minute issuance
assumptions and repeated-search limitations remain unresolved.

Operational failures are preserved in execution.log/recovery.log: a diagnostic mistakenly
requested a risk-complete morning origin, then the continuation reached F22's zero-support
gate. F21 saved coefficients were reused byte-for-byte, never refitted. Six F21 trial MSE
values were lost from memory at the first abort; their selected penalties remain in
coefficients and the log. RIDGE_SELECTION.csv labels the missing values explicitly. No solver
failure, penalty retuning or extra neural start occurred. The final completion pass
took {checks["seconds"]:.1f} s with measured peak RSS {checks["peak_rss_bytes"] / 1e9:.3f} GB;
The initial pass had already used 110.8 s before its diagnostic abort; the first recovery
reached 122.3 s before the zero-validation-support stop. Current compact output is
approximately {footprint / 1e6:.2f} MB. No dependency changes; .venv Python 3.14.6 and existing
NumPy/pandas routines only.

The final arithmetic review corrected EQ3 rounding: summing exact half-integer midranks before
division preserves ties in the declared equal-weight combination. Directly averaging the
float32 rank encodings had broken13,094 exact pair ties through rounding. The old EQ3 column
is retained as a small diagnostic NPZ; only saved-score arithmetic was corrected, with zero
additional model fits. Numerical tables and uncertainty intervals use the corrected scores.

Report-only replay, with **no fitting, feature replay or market reads**:

```sh
.venv/bin/python -B -m lstm_data.hf20_targets report
.venv/bin/python -m pytest tests/test_hf20_targets.py tests/test_hf20_s4_readonly.py -q
.venv/bin/ruff check src/lstm_data/hf20_targets.py
.venv/bin/ruff check src/lstm_data/hf20_targets_report.py tests/test_hf20_targets.py
.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-pylance-extension>/dist
```

The report command uses only OOS_SCORES.parquet, CHECKS.json and the four archived M1 metrics;
saved inputs/recipes remain project-relative. Numerical tables replay from saved predictions.
Historical fit/recovery commands are logged but consumed: do not rerun them. A clean-machine
refit would require the authenticated private artifacts and renewed execution authority; no
download is implied.

Created code: `src/lstm_data/hf20_targets.py`, `src/lstm_data/hf20_targets_report.py`; test:
`tests/test_hf20_targets.py`. This experiment contains REPORT.md, METRICS.csv, PAIRED.csv,
small keyed OOS_SCORES.parquet, F21/F23 coefficients, selection/fit tables,
predeclaration/checks and execution/validation logs. Parquet/NPZ are intentionally ignored;
small code/tables/reports are uncommitted. The mandatory session report is under
`reports/codex_sessions/`. No pre-existing file, source, registry or historical experiment was
changed. No Git fetch/commit/push, raw-minute read, download, 2025/2026 market access, neural
inference/training or trading backtest. Live neural ledger remains 186/300; new neural starts
0.

**STOP.** T1 raw analysis is complete; T0 and T2 are partial for the stated coverage reasons.
Further coverage changes, architecture design or neural fitting require explicit researcher
approval.
"""
    (OUT / "REPORT.md").write_text(text)
