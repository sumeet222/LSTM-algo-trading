"""Read-only P025 two-seed calibration, state sensitivity and collective release."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .branch_replication_authority import rows
from .branch_replication_comparison import baseline_path
from .branch_replication_release import (
    checked_arm,
    diagnosis,
    document,
    initialize,
    load_json,
    markdown_table,
)
from .branch_replication_spec import ARMS, ROLES
from .branch_replication_states import variability
from .config import digest, now, write_json
from .hf1m_ft16_source import ref
from .objective_screen_attribution import cohort_masks
from .objective_screen_diagnostics import canonical
from .objective_screen_metrics import equal_weights, regression
from .visualization.hf1m_long import LongStudy


def month_counts(days: np.ndarray, size: int) -> np.ndarray:
    """Exact original block draws represented by intact-day multiplicities."""
    unique = np.unique(days)
    months = pd.to_datetime(unique).to_period("M").astype(str)
    names = sorted(set(months))
    groups = [
        np.flatnonzero(np.isin(months, names[i : i + size])) for i in range(0, len(names), size)
    ]
    rng = np.random.default_rng(22042)
    return np.stack(
        [
            np.bincount(
                np.concatenate([groups[i] for i in rng.integers(len(groups), size=len(groups))]),
                minlength=len(unique),
            )
            for _ in range(400)
        ]
    )


def conditional_sensitivity(f: pd.DataFrame, recipe: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Same frozen month bootstrap, preserving full-population mass inside each regime."""
    days, di = np.unique(f.session_date_et.to_numpy(), return_inverse=True)
    w = equal_weights(f.session_date_et.to_numpy())
    q = f[["quantiles_z_05", "quantiles_z_50", "quantiles_z_95"]].to_numpy(dtype=float)
    z = np.arcsinh(f.TG20.to_numpy() / recipe["scale"])
    tau = np.array([0.05, 0.5, 0.95])
    e = z[:, None] - q
    e0 = z[:, None] - np.asarray(recipe["quantiles_z"])
    difference = np.maximum(tau * e, (tau - 1) * e).mean(axis=1) - np.maximum(
        tau * e0, (tau - 1) * e0
    ).mean(axis=1)
    records, associations = [], []
    daily = pd.DataFrame(
        dict(day=f.session_date_et, origin=f.origin_id, width=q[:, 2] - q[:, 0], absolute_z=abs(z))
    )
    daily = (
        daily.groupby(["day", "origin"])[["width", "absolute_z"]]
        .median()
        .groupby("day")
        .mean()
        .reindex(days)
    )
    for size in (1, 2):
        counts = month_counts(f.session_date_et.to_numpy(), size)
        for state in ("V1", "M2", "Q2", "market_V1", "market_M2", "market_Q2", "predicted_width_z"):
            for label in ("LOW", "MID", "HIGH"):
                mask = f[state + "_state"].eq(label).to_numpy()
                numerator = np.bincount(di, weights=w * mask * difference, minlength=len(days))
                denominator = np.bincount(di, weights=w * mask, minlength=len(days))
                a, b = counts @ numerator, counts @ denominator
                sampled = np.divide(a, b, out=np.full(len(a), np.nan), where=b > 0)
                interval = (
                    np.nanquantile(sampled, [0.025, 0.975]).tolist()
                    if np.isfinite(sampled).any()
                    else [np.nan, np.nan]
                )
                records.append(
                    dict(
                        state=state,
                        group=label,
                        block_months=size,
                        replicates=400,
                        defined_replicates=int(np.isfinite(sampled).sum()),
                        weight_mass=float(denominator.sum()),
                        difference_neural_minus_unconditional=float(
                            numerator.sum() / denominator.sum()
                        )
                        if denominator.sum()
                        else np.nan,
                        low=interval[0],
                        high=interval[1],
                    )
                )
        # Bootstrap the same predeclared equal-day width / future-dispersion rank statistic.
        values = []
        for count in counts:
            positions = np.repeat(np.arange(len(days)), count)
            x, y = daily.width.to_numpy()[positions], daily.absolute_z.to_numpy()[positions]
            values.append(
                float(pd.Series(x).rank().corr(pd.Series(y).rank()))
                if np.std(x) > 1e-15 and np.std(y) > 1e-15
                else np.nan
            )
        associations.append(
            dict(
                block_months=size,
                replicates=400,
                low=float(np.nanquantile(values, 0.025)) if np.isfinite(values).any() else np.nan,
                high=float(np.nanquantile(values, 0.975)) if np.isfinite(values).any() else np.nan,
            )
        )
    return pd.DataFrame(records), pd.DataFrame(associations)


def calibration(plan_path: Path, out: Path) -> None:
    plan, _, _ = checked_arm(plan_path, "E1")
    initialize(out)
    diag = diagnosis(plan, "E1")
    summary, reliability, thresholds, curves = [], [], [], []
    for role in ROLES:
        m = load_json(diag / role / "metrics.json")
        old = load_json(diag / role / "matched_seed42_comparison.json")
        for seed, raw, corr in (
            (123, m, m["analytical_inverse_weight"]),
            (42, old["seed42_raw"], old["seed42_analytical_inverse_weight"]),
        ):
            for mapping, s in (("RAW_SOFTMAX", raw), ("INVERSE_CLASS_WEIGHT", corr)):
                summary.append(
                    dict(
                        seed=seed,
                        role=role,
                        mapping=mapping,
                        ANY_AP=s["ANY_AP"],
                        NEG_AP=s["NEG_AP"],
                        POS_AP=s["POS_AP"],
                        signed_IC=s["ordinal_daily_IC"],
                        CE=s["unweighted_CE"],
                        Brier=sum(s["Brier_by_class"]),
                        ANY_ECE=s["ANY_ECE10"],
                        mean_NEG=s["probability_mean"][0],
                        observed_NEG=s["observed_prevalence"][0],
                        mean_POS=s["probability_mean"][2],
                        observed_POS=s["observed_prevalence"][2],
                        raw_corrected_ANY_rank_correlation=corr.get(
                            "ANY_raw_corrected_rank_correlation", np.nan
                        ),
                        changed_top4_fraction=corr.get(
                            "ANY_top4_membership_changed_fraction", np.nan
                        ),
                    )
                )
                reliability.extend(
                    dict(seed=seed, role=role, mapping=mapping, **r) for r in s["reliability"]
                )
                thresholds.extend(
                    dict(seed=seed, role=role, mapping=mapping, **r)
                    for r in s["threshold_diagnostics"]
                )
        if role == "development":
            for mapping, filename in (
                ("RAW_SOFTMAX", "PR_raw.parquet"),
                ("INVERSE_CLASS_WEIGHT", "PR_inverse_weight.parquet"),
            ):
                f = pd.read_parquet(diag / role / filename)
                f["seed"], f["mapping"] = 123, mapping
                curves.append(f)
            # Seed42 PR uses saved probabilities, without model inference or fitting.
            from .branch_replication_metrics import event_metrics

            original = pd.read_parquet(baseline_path("E1", role))
            for inverse in (False, True):
                _, f = event_metrics(original, plan["recipes"]["E1"]["refit"], inverse=inverse)
                f["seed"], f["mapping"] = 42, "INVERSE_CLASS_WEIGHT" if inverse else "RAW_SOFTMAX"
                curves.append(f)
    score = pd.DataFrame(summary)
    score.to_csv(out / "E1_calibration_scores.csv", index=False)
    rel = pd.DataFrame(reliability)
    rel.to_csv(out / "E1_reliability.csv", index=False)
    pd.DataFrame(thresholds).to_csv(out / "E1_thresholds.csv", index=False)
    curve = pd.concat(curves)
    curve.to_parquet(out / "E1_PR_curves.parquet", index=False)
    dev = score.loc[score.role.eq("development")]
    fig = px.line(
        curve.loc[curve.event.isin(["ANY", "NEG", "POS"])],
        x="recall",
        y="precision",
        color="seed",
        line_dash="mapping",
        facet_col="event",
        title="E1 event PR: ANY ranking is separate from signed direction",
    )
    fig.write_html(out / "E1_two_seed_PR.html", include_plotlyjs="directory")
    r = rel.loc[rel.role.eq("development") & rel.event.isin(["ANY", "NEG", "POS"]) & rel.rows.gt(0)]
    fig = px.scatter(
        r,
        x="confidence",
        y="frequency",
        color="seed",
        symbol="mapping",
        facet_col="event",
        hover_data=["rows", "mass"],
        title="Natural-frequency reliability: identity line is ideal, bins retain sample counts",
    )
    fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line=dict(dash="dash"))
    fig.write_html(out / "E1_two_seed_reliability.html", include_plotlyjs="directory")
    text = (
        """# P025 E1 natural-frequency calibration analysis

Raw class-weighted softmax is assessed separately from natural event frequency.
The inverse-class-weight mapping divides each probability by its correct saved prefix
weight and renormalizes. It is an analytical diagnostic, not a fitted or guaranteed
calibrator. Temperature scaling is omitted; no map or threshold is fitted on development.

## Two-seed exploratory development

"""
        + markdown_table(
            dev,
            [
                "seed",
                "mapping",
                "ANY_AP",
                "NEG_AP",
                "POS_AP",
                "signed_IC",
                "CE",
                "Brier",
                "ANY_ECE",
                "mean_NEG",
                "observed_NEG",
                "mean_POS",
                "observed_POS",
                "raw_corrected_ANY_rank_correlation",
                "changed_top4_fraction",
            ],
        )
        + """

AP reflects ranking, not calibration or tradable signed returns. Check whether correction
reduces CE/Brier/ECE for both seeds and whether multiclass renormalization changes ANY
ranking/top4 membership; raw outputs remain intact. Ordinary CE and weighted optimized
CE have different normalization. Training/refit are in-sample; inner validation selected
the checkpoint; development has109 repeatedly inspected dependent sessions.

Full four-role scores, reliability bins with counts/mass, class thresholds/top-k,
slopes and proper metrics are in E1_calibration_scores.csv, E1_reliability.csv,
E1_thresholds.csv and the bound immediate metric JSONs. Plots:
[two-seed PR](E1_two_seed_PR.html), [reliability](E1_two_seed_reliability.html).
No branch promotion or trading claim follows automatically.
"""
    )
    document(out / "P025_E1_CALIBRATION_ANALYSIS.md", text)


def quantile_states(plan_path: Path, out: Path) -> None:
    plan, _, _ = checked_arm(plan_path, "QR1")
    diag = diagnosis(plan, "QR1")
    tables, variation, decision, uncertainty, association = [], [], [], [], []
    for role in ROLES:
        recipe = plan["recipes"]["QR1"]["inner" if role.startswith("inner") else "refit"]
        for seed, prefix in ((123, ""), (42, "seed42_")):
            table = pd.read_parquet(diag / role / (prefix + "state_metrics.parquet"))
            table["seed"], table["role"] = seed, role
            tables.append(table)
            response = load_json(diag / role / (prefix + "state_response.json"))
            if seed == 123:
                f = pd.read_parquet(diag / role / "state_population.parquet")
            else:
                original = pd.read_parquet(baseline_path("QR1", role))
                states = pd.read_parquet(diag / role / "state_population.parquet")
                from .branch_replication_states import state_analysis

                _, f, _ = state_analysis(
                    original,
                    states[
                        [
                            c
                            for c in states
                            if c
                            in [
                                "origin_id",
                                "ticker",
                                "V1",
                                "M2",
                                "Q2",
                                "market_V1",
                                "market_M2",
                                "market_Q2",
                                "V1_fallback",
                                "M2_fallback",
                                "Q2_fallback",
                            ]
                        ]
                    ],
                    load_json(diag / role / "seed42_training_state_cutoffs.json"),
                    recipe,
                )
            w = equal_weights(f.session_date_et.to_numpy())
            for unit in ("z", "y"):
                q = f[
                    [f"quantiles_{unit}_05", f"quantiles_{unit}_50", f"quantiles_{unit}_95"]
                ].to_numpy(dtype=float)
                unconditional = np.asarray(recipe["quantiles_z"])
                if unit == "y":
                    unconditional = recipe["scale"] * np.sinh(unconditional)
                for name, values in (
                    ("center", q[:, 1]),
                    ("lower_span", q[:, 1] - q[:, 0]),
                    ("upper_span", q[:, 2] - q[:, 1]),
                    ("width", q[:, 2] - q[:, 0]),
                    ("asymmetry", q[:, 2] + q[:, 0] - 2 * q[:, 1]),
                ):
                    variation.append(
                        dict(
                            seed=seed,
                            role=role,
                            unit="TG20" if unit == "y" else "z",
                            quantity=name,
                            **variability(values, w, float(unconditional[2] - unconditional[0])),
                        )
                    )
            if role == "development":
                intervals, corr = conditional_sensitivity(f, recipe)
                intervals["seed"] = seed
                uncertainty.append(intervals)
                corr["seed"] = seed
                association.append(corr)
                v = table.loc[table.state.eq("V1")].set_index("group")
                overall = table.loc[table.state.eq("ALL")].iloc[0]
                decision.append(
                    dict(
                        seed=seed,
                        output_width_sd=response["predicted_width_z"]["sd"],
                        width_sd_over_unconditional=response["predicted_width_z"][
                            "sd_over_unconditional_width"
                        ],
                        high_minus_low_V1_width=float(
                            v.loc[["HIGH"], "width_z"].to_numpy(dtype=float)[0]
                            - v.loc[["LOW"], "width_z"].to_numpy(dtype=float)[0]
                        ),
                        coverage90=overall.interval90_coverage,
                        pinball_skill=overall.pinball_skill,
                        width_dispersion_rank_statistic=response["negative_control"]["statistic"],
                        shuffle_low=response["negative_control"]["circular_shift_interval"][0],
                        shuffle_high=response["negative_control"]["circular_shift_interval"][1],
                    )
                )
    state = pd.concat(tables)
    state.to_csv(out / "QR1_all_state_metrics.csv", index=False)
    var = pd.DataFrame(variation)
    var.to_csv(out / "QR1_output_variability.csv", index=False)
    decision_table = pd.DataFrame(decision)
    decision_table.to_csv(out / "QR1_state_decision_matrix.csv", index=False)
    pd.concat(uncertainty).to_csv(out / "QR1_conditional_month_sensitivity.csv", index=False)
    pd.concat(association).to_csv(out / "QR1_width_dispersion_month_sensitivity.csv", index=False)
    d = state.loc[state.role.eq("development") & state.state.eq("V1")]
    for name, y, title in (
        (
            "P025_QR1_WIDTH_VS_VOLATILITY",
            "width_z",
            "Predicted z-width vs training-frozen causal V1 state",
        ),
        (
            "P025_QR1_CONDITIONAL_PINBALL_SKILL",
            "pinball_skill",
            "Conditional proper-score skill vs frozen unconditional quantiles",
        ),
    ):
        fig = px.bar(
            d,
            x="group",
            y=y,
            color="seed",
            barmode="group",
            title=title,
            category_orders={"group": ["LOW", "MID", "HIGH"]},
        )
        fig.write_html(out / (name + ".html"), include_plotlyjs="directory")
    fig = go.Figure()
    for seed in (42, 123):
        v = d.loc[d.seed.eq(seed)].set_index("group").reindex(["LOW", "MID", "HIGH"])
        fig.add_trace(
            go.Scatter(x=v.index, y=v.interval90_coverage, name=f"seed{seed} 90% coverage")
        )
        fig.add_trace(
            go.Scatter(
                x=v.index, y=v.abs_future_z, name=f"seed{seed} realized |future z|", yaxis="y2"
            )
        )
    fig.update_layout(
        title="Conditional coverage and retrospective future dispersion",
        yaxis=dict(title="90% interval coverage"),
        yaxis2=dict(title="Mean |future z|", overlaying="y", side="right"),
    )
    fig.write_html(out / "P025_QR1_COVERAGE_AND_DISPERSION.html", include_plotlyjs="directory")
    text = (
        """# P025 QR1 conditional-state analysis

Three findings are assessed separately: output variability, conditional calibration,
and useful proper-score improvement. Nonconstant intervals or overall90% coverage alone
do not establish conditional predictive skill. Original-TG20 median MSE is auxiliary.

## Both-seed development decision matrix

"""
        + markdown_table(decision_table, list(decision_table.columns))
        + """

The width SD/unconditional-width ratio quantifies response size without a post-hoc
success threshold. V1 HIGH-minus-LOW width measures the direction of volatility response.
Coverage must be checked per regime and for q05/q50/q95, alongside proper pinball and
interval score, not merely average interval width. Positive point skill means lower
pinball than frozen training unconditional quantiles; consult the month sensitivity
before interpreting improvement. No automatic promotion follows from these statistics.

## Causal regimes and uncertainty

Last input step47 V1/M2/Q2 and same-origin median20 market states use the already frozen
inner/refit training-only terciles. Prefix fallbacks remain marked. LOW/MID/HIGH ties
retain empty cohorts. Width terciles are training-only separately for each seed/phase.
Full tables include stock versus market regimes and preregistered2011–2015,2016–2020,
2021–2025 eras; development supplies only the final era and cannot independently test
historical era stability. Quality/fallback rates, stock/origin/session counts and weight
mass remain visible. Whole-session month bootstrap uses400 draws at seed22042 for one
and two-month blocks; native population mass is conserved inside each conditional cohort.
The width/absolute-future-z negative control uses400 nonzero intact-day circular shifts
at seed25042. It is a read-only association reference, not neural permutation evidence.

## Plots and complete tables

- [Conditional width vs volatility](P025_QR1_WIDTH_VS_VOLATILITY.html)
- [Conditional pinball skill](P025_QR1_CONDITIONAL_PINBALL_SKILL.html)
- [Coverage and realized dispersion](P025_QR1_COVERAGE_AND_DISPERSION.html)

QR1_all_state_metrics.csv contains all roles/seeds/regimes/eras; QR1_output_variability.csv
separates z and once-inverted TG20 center/spans/width/asymmetry. Per-stock time variation
and origin-wise cross-stock variation remain in the source-bound state_response JSONs.
QR1_conditional_month_sensitivity.csv and QR1_width_dispersion_month_sensitivity.csv
report sensitivity intervals. Signed event frequency, return errors and tail cohorts are
retrospective context.109 reused development days, dependent stocks and sparse calendar
blocks limit all inference. Protected2026 outcomes are untouched; no causal/trading claim.
"""
    )
    document(out / "P025_QR1_CONDITIONAL_STATE_ANALYSIS.md", text)


def finish(plan_path: Path, out: Path) -> None:
    plan, _, _ = checked_arm(plan_path, "E1")
    checked_arm(plan_path, "QR1")
    if rows()[-1]["global_started_pairs"] != 53:
        raise ValueError("P025_TWO_ACTUAL_STARTS_REQUIRED")
    initialize(out)
    if not (out / "P025_E1_CALIBRATION_ANALYSIS.md").exists():
        calibration(plan_path, out)
    quantile_states(plan_path, out)
    frames = []
    for arm in ARMS:
        f = pd.read_parquet(diagnosis(plan, arm) / "cohorts.parquet")
        f["conditional_optimized_loss"] = np.divide(
            f.weighted_objective,
            f.objective_weight_mass,
            out=np.full(len(f), np.nan),
            where=f.objective_weight_mass.gt(0),
        )
        f["arm"] = arm
        frames.append(f)
    tails = pd.concat(frames)
    tails.to_parquet(out / "actual_objective_cohorts.parquet", index=False)
    tails.to_csv(out / "actual_objective_cohorts.csv", index=False)
    component_rows = []
    for role in ROLES:
        version = "inner_train" if role.startswith("inner") else "refit"
        f = pd.read_parquet(diagnosis(plan, "QR1") / role / "population.parquet")
        train = pd.read_parquet(diagnosis(plan, "QR1") / version / "population.parquet")
        masks, _ = cohort_masks(f, train)
        for cohort, mask in masks.items():
            component_rows.append(
                dict(
                    role=role,
                    cohort=cohort,
                    **{
                        "weighted_pinball_tau" + tau: float(
                            f.loc[mask, "component_" + str(k)].sum()
                        )
                        for k, tau in enumerate(("05", "50", "95"))
                    },
                )
            )
    pd.DataFrame(component_rows).to_csv(out / "QR1_actual_component_cohorts.csv", index=False)
    selected = tails.loc[
        tails.role.eq("refit")
        & tails.cohort.isin(
            [
                "ALL",
                "TARGET_RANK_TOP1",
                "TARGET_RANK_TOP5",
                "BOTH_5",
                "MAD_ONLY_5",
                "RANGE_ABS_0.99",
                "RANGE_ABS_0.95",
            ]
        )
    ]
    document(
        out / "P025_OBJECTIVE_SPACE_EXTREME_LOSS.md",
        (
            "# P025 actual-objective extreme loss\n\nE1 CE and QR1 pinball have different"
            " units and must not be compared numerically across arms. Fixed-checkpoint "
            "dropout-OFF allocations conserve the true optimized session weights. "
            "Ranked1%/5% tails and fitting-maximum99%/95% magnitude ranges are "
            "different groups.\n\n"
        )
        + markdown_table(selected, list(selected.columns))
        + (
            "\nAll four roles, numerator/MAD disjoint groups, signs/complements, masses "
            "and component shares are in actual_objective_cohorts.csv and the private "
            "per-arm populations. Inner recipes apply to inner roles and refit recipes "
            "to refit/development. See [E1 cases](E1_EXACT_CASES.md) and [QR1 "
            "cases](QR1_EXACT_CASES.md):44 exact source witnesses,48 input candles "
            "plus4 future outcome candles per case,20 genuine return operands and16 "
            "native/scaled features. Source volume/proxy/zero-volume flags remain "
            "preserved; no raw-minute duplication or repair.\n"
        ),
    )
    e = pd.read_csv(out / "E1_calibration_scores.csv")
    q = pd.read_csv(out / "QR1_state_decision_matrix.csv")
    label_counts = []
    for split in ROLES:
        f = pd.read_parquet(diagnosis(plan, "E1") / split / "population.parquet")
        for label, name in enumerate(("NEG", "NORMAL", "POS")):
            label_counts.append(
                dict(
                    role=split,
                    event=name,
                    stock_rows=len(f),
                    class_rows=int(f.label.eq(label).sum()),
                    weighted_prevalence=float(
                        equal_weights(f.session_date_et.to_numpy()) @ f.label.eq(label).to_numpy()
                    ),
                )
            )
    pd.DataFrame(label_counts).to_csv(out / "E1_label_event_counts.csv", index=False)
    raw = e.loc[e.role.eq("development") & e.mapping.eq("RAW_SOFTMAX")].set_index("seed")
    ap123 = float(raw.loc[[123], "ANY_AP"].to_numpy(dtype=float)[0])
    ap42 = float(raw.loc[[42], "ANY_AP"].to_numpy(dtype=float)[0])
    event_verdict = (
        "ANY-event ranking advantage over the constant-prior reference replicates in seed123: "
        f"AP {ap123:.6f} versus seed42 {ap42:.6f}. "
        "Signed probability IC remains close to zero; signed alpha has not been demonstrated. "
        "Analytical correction improves CE, Brier and ECE in both seeds while preserving "
        "ANY ranking/top4 membership here, because both rare-class weights equal4. "
        "Residual calibration error and reused development prevent a general calibration claim. "
        "The one-month AP-difference interval is positive; the two-month interval crosses zero, "
        "so the apparent gain over seed42 is sensitive to block choice."
    )
    document(out / "P025_E1_RESEARCH_VERDICT.md", "# P025 E1 research verdict\n\n" + event_verdict)
    proper = []
    for seed in (42, 123):
        m = load_json(diagnosis(plan, "QR1") / "development/metrics.json")
        if seed == 42:
            m = load_json(diagnosis(plan, "QR1") / "development/matched_seed42_comparison.json")[
                "seed42"
            ]
        proper.append(
            dict(
                seed=seed,
                pinball=m["pinball"],
                unconditional=m["unconditional"]["pinball"],
                pinball_skill=m["pinball_skill"],
                coverage05=m["coverage"][0],
                coverage50=m["coverage"][1],
                coverage95=m["coverage"][2],
                coverage90=m["interval_coverage"],
                interval_score=m["interval_score"],
            )
        )
    proper_table = pd.DataFrame(proper)
    proper_table.to_csv(out / "QR1_two_seed_proper_scores.csv", index=False)
    qr_verdict = (
        "Proper-score improvement versus frozen unconditional quantiles "
        + (
            "replicates in both seeds at the point-estimate level. "
            if all(x["pinball_skill"] > 0 for x in proper)
            else "does not replicate as a point improvement in both seeds. "
        )
        + "Output variability and volatility response remain separate findings. "
        "The state matrix and conditional block intervals show whether response has local skill."
    )
    study = LongStudy.discover(Path.cwd())
    context = []
    target = pd.read_parquet(diagnosis(plan, "QR1") / "development/population.parquet")
    for seed in (42, 123):
        pred = canonical(study.prediction(f"HF1M-LONG-TM0-T2-S{seed}-DEV1", "development"), target)
        metrics = regression(
            target.TG20.to_numpy(),
            pred.pred_original_TG20.to_numpy(),
            target.session_date_et.to_numpy(),
        )
        context.append(
            dict(
                model=f"T2/{seed}",
                mse=metrics["mse"],
                rank_IC=metrics["daily_ic"],
                interpretation="Common signed-return regression context only",
            )
        )
    context.append(
        dict(
            model="ZERO",
            mse=float(
                equal_weights(target.session_date_et.to_numpy()) @ (target.TG20.to_numpy() ** 2)
            ),
            rank_IC=np.nan,
            interpretation="Constant-score IC undefined",
        )
    )
    pd.DataFrame(context).to_csv(out / "T2_ZERO_regression_context.csv", index=False)
    text = (
        """# P025 final research comparison

Both authorized seed123 fits completed and passed their source/checkpoint/numerical gates.
Exactly two new starts were charged:52(E1) and53(QR1); ledger53/200. No other fitting,
confirmation access, combinations, trading or production promotion occurred.

## E1: event ranking, signed discrimination and calibration

"""
        + event_verdict
        + "\n\n"
        + markdown_table(
            e.loc[e.role.eq("development")],
            [
                "seed",
                "mapping",
                "ANY_AP",
                "NEG_AP",
                "POS_AP",
                "signed_IC",
                "CE",
                "Brier",
                "ANY_ECE",
            ],
        )
        + """

Event-ranking replication is assessed separately from signed direction and calibrated
natural event probabilities. Inverse-class-weight correction is an unchanged mathematical
diagnostic, not a development-fitted replacement. Compare both seeds to their correct
training-prior/alwaysNORMAL references and consult paired AP month-block sensitivity.

## QR1: proper quantile skill and the separate state-response question

"""
        + qr_verdict
        + "\n\n"
        + markdown_table(proper_table, list(proper_table.columns))
        + "\n\n"
        + markdown_table(q, list(q.columns))
        + """

Proper pinball versus frozen unconditional quantiles is primary. Output variability,
conditional coverage and useful proper-score skill have separate verdicts in the state
analysis. A changing interval or roughly90% average coverage alone is insufficient.
Median TG20 MSE/IC are descriptive; QR1 is not a conditional-mean regression objective.

## Existing signed-return context

"""
        + markdown_table(pd.DataFrame(context), ["model", "mse", "rank_IC", "interpretation"])
        + """

These T2 checkpoints were read, never refit. Do not compare classification probabilities
to return MSE or conflate event AP with signed alpha. All models share183 development
origins/3,660 stock rows/109 dependent sessions. Whole-month/two-month sensitivity uses
400 fixed-seed replicates; reused development and few blocks preclude confirmation claims.

Read [E1 result](P025_E1_S123_RESULT.md), [E1 calibration](P025_E1_CALIBRATION_ANALYSIS.md),
[QR1 result](P025_QR1_S123_RESULT.md), [QR1 states](P025_QR1_CONDITIONAL_STATE_ANALYSIS.md),
and [actual-objective tails](P025_OBJECTIVE_SPACE_EXTREME_LOSS.md). Original P021–P024
baselines and all failed starts are preserved. Walk-forward, neural null testing, the
remaining research hypotheses, USA500 comparison and protected confirmation remain
separate future work. Humans decide whether either independent branch merits further work.
"""
    )
    document(out / "P025_FINAL_RESEARCH_COMPARISON.md", text)
    document(
        out / "guide.md",
        """# P025 click guide

Choose E1 or QR1, seed42 or123, and a permitted chronological role.
Inner validation selected the calibration checkpoint; training/refit are in-sample.
Development is an exploratory comparison on109 reused sessions.

1. E1 Ranking / Calibration compares event PR, natural-frequency reliability,
   raw softmax and the analytical inverse-class-weight diagnostic.
2. QR1 Quantiles / States separates interval response, conditional coverage and
   proper pinball skill against frozen unconditional quantiles.
3. Outputs shows saved probabilities/signed event scores or ordered quantiles.
   E1 scores are not return forecasts; QR1's center is a median.
4. Actual-Objective Tails distinguishes ranked row tails from training-maximum
   magnitude ranges, with original loss units and conserved weights.
5. Exact Cases shows48 genuine input hours plus4 future outcome hours. Orange
   marks the entry/input boundary; green marks exit. Volume/proxy flags remain visible.
6. History / Features covers all20 stocks, with native/scaled values and fallback flags.
7. Training / Gradients separates online/dropout losses from final-checkpoint evaluation.

January–March2026 queries are blocked. No trading or production promotion is implied.
""",
    )
    write_json(out / "recipes.json", plan["recipes"])
    files = {}
    for arm in ARMS:
        diag = diagnosis(plan, arm)
        for role in ROLES:
            for f in (diag / role).iterdir():
                if f.is_file():
                    files[f"{arm}_123/{role}/{f.name}"] = ref(f)
            files[f"{arm}_42/{role}/population.parquet"] = ref(baseline_path(arm, role))
        for seed, folder in ((123, diag / "refit"), (42, baseline_path(arm, "refit").parent)):
            for name in ("cases", "case_candles", "case_features", "case_20_returns"):
                files[f"{arm}_{seed}/{name}.parquet"] = ref(folder / (name + ".parquet"))
    for f in out.iterdir():
        if f.is_file() and not f.name.startswith("."):
            files[f.name] = ref(f)
    manifest = dict(
        status="PASS_COLLECTIVE_P025",
        ledger=53,
        source_contract=plan["input_contract"],
        proposal=ref(plan_path),
        scientific_definitions=plan["scientific_definitions"],
        files=files,
        gates=[ref(plan_path.parent / (arm + "_immediate_gate.json")) for arm in ARMS],
        phase="exploratory development only",
        protected_numeric_access=False,
        at=now(),
    )
    write_json(out / "view_manifest.json", manifest)
    write_json(
        Path("configs/track_a_p025_visualization_v1.json"),
        dict(manifest=ref(out / "view_manifest.json")),
    )
    print(
        json.dumps(
            dict(
                status=manifest["status"],
                ledger=53,
                manifest_sha256=digest(out / "view_manifest.json"),
            )
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--calibration-only", action="store_true")
    a = parser.parse_args()
    if a.calibration_only:
        calibration(a.plan, a.out)
    else:
        finish(a.plan, a.out)
