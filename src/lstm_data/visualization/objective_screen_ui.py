"""Additive P022 screen in the existing Track A Streamlit explorer."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ..hf1m_action_audit import SYMBOLS
from ..hf1m_ft16_source import ORDER
from .hf1m_long import LongStudy, dates, role
from .objective_screen import MODELS, Screen, safe_features

SECTION = "HF1M Long — Objective Improvement Screen (P022)"
VIEWS = (
    "Feature / Event Audit",
    "Matched Comparisons",
    "Training / Gradients",
    "Objective Tail Attribution",
    "Exact Event Cases",
    "History / 16 Features",
    "Guide",
)


def chart(fig, key: str) -> None:
    st.plotly_chart(fig, width="stretch", key=key, config={"displaylogo": False})


def panel(root: Path) -> None:
    # Reject protected/unknown query state before constructing numeric readers or cache keys.
    for key in ("start", "end", "date"):
        if key in st.query_params:
            value = str(st.query_params[key])
            dates(value, value)
    if "role" in st.query_params:
        role(str(st.query_params["role"]))
    s = Screen.discover(root)
    st.title(SECTION)
    st.caption(
        "Frozen FT16 / TG20 · seed42 objective screen · ledger41/200 · failed start37 preserved"
    )
    st.info(
        "Development is exploratory (109 sessions). Inner validation selected epochs. "
        "2026 confirmation is locked. No trading or automatic model promotion."
    )
    view = st.selectbox("P022 view", VIEWS, key="p022_view")
    split = st.selectbox(
        "Data role", ("development", "inner_validation", "refit", "inner_train"), key="p022_role"
    )
    model = st.selectbox("Model", MODELS, key="p022_model")
    st.caption(
        "E1 is a classifier: probabilities and signed event score are not return forecasts. "
        "ZERO has undefined rank IC; objective losses in different units are not comparable."
    )
    if view == "Feature / Event Audit":
        audit = st.selectbox(
            "Audit table",
            (
                "associations",
                "quintiles",
                "precursors",
                "event_rates",
                "stability",
                "missing_fallback",
            ),
        )
        f = s.table("audit/" + audit + ".csv")
        if audit in ("quintiles", "precursors", "associations"):
            channel = st.selectbox("Audit feature", ORDER)
            selected = f.loc[f.feature.eq(channel)]
            if audit == "quintiles":
                selected = selected.loc[selected.representation.eq("scaled_latest")]
                chart(
                    px.line(
                        selected,
                        x="bin",
                        y="target_mean",
                        color="role",
                        title="Train-frozen quintiles · mean TG20",
                    ),
                    "p022_audit_quintiles",
                )
            elif audit == "precursors":
                chart(
                    px.line(
                        selected,
                        x="step",
                        y="scaled_mean",
                        color="event",
                        facet_col="role",
                        title="48-step event precursors",
                    ),
                    "p022_audit_precursors",
                )
            else:
                chart(
                    px.bar(
                        selected,
                        x="representation",
                        y="daily_ic",
                        color="role",
                        barmode="group",
                        title="Exploratory daily feature IC",
                    ),
                    "p022_audit_ic",
                )
        st.dataframe(f, width="stretch")
        st.markdown(s.file("audit/triage.md").read_text())
        if audit == "quintiles":
            st.caption(
                "Quintile boundaries were fitted on inner training only; validation is exploratory."
            )
        return
    if view == "Matched Comparisons":
        scores = pd.DataFrame(json.loads(s.file("scoreboard.json").read_text()))
        selected = scores.loc[scores.role.eq(split)]
        regressors = selected.loc[
            selected.model.isin(["H2", "W1", "R1", "T2/42", "T2/123", "ZERO"])
        ]
        st.subheader("Regression · original TG20 units")
        st.dataframe(
            regressors[
                [
                    "model",
                    "rows",
                    "sessions",
                    "mse",
                    "mae",
                    "rmse",
                    "daily_ic",
                    "prediction_sd",
                    "top4_recall",
                    "bottom4_recall",
                ]
            ],
            width="stretch",
        )
        st.subheader("Classification · E1 and frozen training-prior baselines")
        classification = selected.loc[selected.model.str.startswith("E1")]
        st.dataframe(
            classification[
                [
                    "model",
                    "normalized_class_weighted_CE",
                    "NEG_AP",
                    "POS_AP",
                    "ANY_AP",
                    "NEG_recall_at4",
                    "POS_recall_at4",
                    "macro_F1",
                    "ordinal_daily_IC",
                ]
            ],
            width="stretch",
        )
        st.dataframe(
            s.table("paired_daily_differences.csv").query("role == @split"), width="stretch"
        )
        f = s.population(model, split)
        ticker = st.selectbox("Forecast stock", SYMBOLS, index=4)
        g = f.loc[
            f.ticker.eq(ticker)
        ].copy()  # Filter complete population before any display sampling.
        x = "session_date_et"
        if model == "E1":
            chart(
                px.line(g, x=x, y=["p_NEG", "p_NORMAL", "p_POS"], title="Class probabilities"),
                "p022_prob",
            )
            chart(
                px.line(g, x=x, y="signed_event_score", title="p(POS) − p(NEG)"), "p022_event_score"
            )
        else:
            prediction = (
                "comparison_score"
                if model.startswith("T2_") or model == "ZERO"
                else "pred_original_TG20"
            )
            chart(
                px.line(g, x=x, y=["TG20", prediction], title="Original TG20 target and forecast"),
                "p022_forecast",
            )
            g["squared_error"] = (g.TG20 - g[prediction]) ** 2
            chart(
                px.line(g, x=x, y="squared_error", title="Original-scale squared error"),
                "p022_errors",
            )
        d = s.table("daily_metrics.parquet")
        label = model.replace("_", "/")
        d = d.loc[d.role.eq(split) & d.model.eq(label)]
        chart(
            px.line(
                d, x=x, y=["ic", "top4_recall", "bottom4_recall"], title="Daily rank diagnostics"
            ),
            "p022_daily",
        )
        chart(
            px.line(
                d,
                x=x,
                y=["prediction_sd", "actual_sd"],
                title="Dispersion · E1 score and target units differ",
            ),
            "p022_dispersion",
        )
        return
    if view == "Training / Gradients":
        if model not in ("H2", "W1", "E1", "R1"):
            st.info(
                "Saved T2 training diagnostics remain in HF1M Long —20 stocks "
                "→ Training Diagnostics."
            )
            return
        f = s.table("optimization.csv")
        f = f.loc[f.arm.eq(model)]
        for phase in ("calibration", "refit"):
            g = f.loc[f.phase.eq(phase)]
            st.subheader(phase.capitalize())
            chart(
                px.line(
                    g,
                    x="epoch",
                    y="optimized_objective",
                    color="kind",
                    title=f"{model} actual objective · online training vs checkpoint validation",
                ),
                "p022_loss_" + phase,
            )
            if phase == "calibration" and model != "E1":
                chart(
                    px.line(
                        g,
                        x="epoch",
                        y="original_mse",
                        color="kind",
                        title="Original TG20 MSE · selection uses validation",
                    ),
                    "p022_mse",
                )
            if model == "E1":
                chart(
                    px.line(
                        g,
                        x="epoch",
                        y=["metric_NEG_AP", "metric_POS_AP", "metric_ANY_AP"],
                        facet_col="kind",
                        title="E1 event AP · separate from CE",
                    ),
                    "p022_e1_ap_" + phase,
                )
            training = g.loc[g.kind.eq("training")]
            chart(
                px.line(
                    training,
                    x="epoch",
                    y=[
                        "preclip_norm_p50",
                        "preclip_norm_p90",
                        "preclip_norm_p99",
                        "postclip_norm_max",
                    ],
                    title="Global gradient norms · cap1",
                ),
                "p022_grad_" + phase,
            )
            chart(
                px.line(
                    training, x="epoch", y="clipped_fraction", title="Fraction of updates clipped"
                ),
                "p022_clip_" + phase,
            )
            st.dataframe(g, width="stretch")
        return
    if view == "Objective Tail Attribution":
        if model not in ("H2", "W1", "E1", "R1"):
            st.info("Select a new arm for its actual objective; P021B preserves T2/42 attribution.")
            return
        f = s.table("cohort_metrics.parquet")
        f = f.loc[f.arm.eq(model) & f.role.eq(split)]
        choices = [x for x in f.cohort if not x.endswith(("_POS", "_NEG", "_COMPLEMENT"))]
        names = st.multiselect(
            "Cohorts",
            choices,
            default=[
                x
                for x in choices
                if x
                in (
                    "TARGET_RANK_TOP1",
                    "TARGET_RANK_TOP5",
                    "RANGE_ABS_0.99",
                    "RANGE_ABS_0.95",
                    "BOTH_5",
                    "NUM_ONLY_5",
                    "MAD_ONLY_5",
                    "NEITHER_5",
                )
            ],
        )
        g = f.loc[f.cohort.isin(names)]
        chart(
            px.bar(
                g,
                x="cohort",
                y="weighted_loss_share_pct",
                title="Share of this model's actual checkpoint objective (%)",
            ),
            "p022_tail",
        )
        st.dataframe(g, width="stretch")
        st.caption(
            "Ranked cohorts and magnitude ranges differ. Groups overlap except "
            "the four stated disjoint mechanisms. RMSE is not additive. "
            "R1 pair loss is allocated half to each endpoint; "
            "this is accounting, not causal attribution. "
            "Attribution uses dropout OFF; historical online training used dropout ON."
        )
        return
    if view == "Exact Event Cases":
        if model not in ("H2", "W1", "E1", "R1"):
            st.info(
                "Choose H2/W1/E1/R1 for new actual-objective cases. "
                "Existing T2 cases remain in P021."
            )
            return
        st.caption(
            "Cases use the final refit checkpoint and in-sample refit population, "
            "regardless of role selector."
        )
        cases = s.table(f"{model}/refit/cases.parquet")
        case = st.selectbox(
            "Exact case",
            cases.case_id.tolist(),
            format_func=lambda n: (
                str(n)
                + " · "
                + str(cases.loc[cases.case_id.eq(n), "ticker"].iloc[0])
                + " · "
                + str(cases.loc[cases.case_id.eq(n), "origin_id"].iloc[0])
            ),
        )
        if case is None:
            st.info("No saved case available.")
            return
        selected = cases.loc[cases.case_id.eq(case)]
        st.dataframe(
            selected.T.rename(columns={selected.index[0]: "value"}).astype(str), width="stretch"
        )
        c = s.table(f"{model}/refit/case_candles.parquet")
        c = c.loc[c.case_id.eq(case)]
        chart(
            go.Figure(
                go.Candlestick(x=c.hour_end_utc, open=c.open, high=c.high, low=c.low, close=c.close)
            ),
            "p022_case_candles",
        )
        st.dataframe(c, width="stretch")
        features = s.table(f"{model}/refit/case_features.parquet")
        st.dataframe(features.loc[features.case_id.eq(case)], width="stretch")
        returns = s.table(f"{model}/refit/case_20_returns.parquet")
        st.dataframe(returns.loc[returns.case_id.eq(case)], width="stretch")
        return
    if view == "History / 16 Features":
        ticker = st.selectbox("History stock", SYMBOLS, index=4)
        start = st.date_input(
            "History start",
            date(2025, 7, 15),
            min_value=date(2010, 7, 1),
            max_value=date(2025, 12, 31),
        )
        end = st.date_input(
            "History end",
            date(2025, 7, 25),
            min_value=date(2010, 7, 1),
            max_value=date(2025, 12, 31),
        )
        dates(str(start), str(end))
        if (end - start).days > 93:
            st.warning("Choose at most93 days; all permitted history is navigable.")
            return
        study = LongStudy.discover(root)
        candles = study.history(ticker, str(start), str(end))
        from .hf1m_long_ui import candles as plot_candles

        plot_candles(candles, "p022_history")
        st.dataframe(candles, width="stretch")
        fit = st.selectbox("Feature fitting recipe", ("inner", "refit"), index=1)
        origin = st.selectbox("M2 origin context", (1, 2))
        features = safe_features(study, ticker, str(start), str(end), fit, origin)
        channel = st.selectbox("Feature channel", ORDER)
        if len(features):
            chart(
                px.line(
                    features.loc[features.feature.eq(channel)],
                    x="hour_end_utc",
                    y=["native", "scaled"],
                    title=channel + " · native / model-scaled",
                ),
                "p022_features",
            )
        st.dataframe(features, width="stretch")
        return
    st.markdown(s.file("P022_DASHBOARD_USER_GUIDE.md").read_text())
    with st.expander("Exact source and release provenance"):
        st.json(s.config)
