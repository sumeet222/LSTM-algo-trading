"""P023 additive explorer; all numeric paths are completed-study hash-bound."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ..config import digest
from ..hf1m_action_audit import SYMBOLS
from ..hf1m_ft16_source import ORDER
from .hf1m_long import LongStudy, dates, role
from .objective_screen import Screen, safe_features

SECTION = "HF1M Long — Direction / Quantiles / Sampling (P023)"
VIEWS = (
    "Comparisons",
    "Optimization / Gradients",
    "Head Outputs",
    "Actual-Objective Tails",
    "Exact Cases",
    "History / Features",
    "Guide",
)


def chart(figure, key: str) -> None:
    st.plotly_chart(figure, width="stretch", key=key)


def panel(root: Path) -> None:
    for key in ["start", "end", "date"]:
        if key in st.query_params:
            dates(str(st.query_params[key]), str(st.query_params[key]))
    if "role" in st.query_params:
        role(str(st.query_params["role"]))
    config = json.loads((root / "configs/track_a_p023_visualization_v1.json").read_text())
    path = root / config["manifest"]["path"]
    if digest(path) != config["manifest"]["sha256"]:
        raise ValueError("P023 manifest changed")
    manifest = json.loads(path.read_text())
    if manifest["ledger"] != 44:
        raise ValueError("P023 completed study required")
    s = Screen(root, manifest["files"], config["manifest"]["sha256"], config)
    st.title(SECTION)
    st.caption("FT16 / TG20 · exact seed42 screens · ledger44/200 · protected2026locked")
    st.info(
        (
            "Development109sessions is exploratory. QR1 predicts quantiles; "
            "median MSE is descriptive. No trading or automatic promotion."
        )
    )
    view = st.selectbox("P023 view", VIEWS, key="p023_view")
    arm = st.selectbox("P023 model", ("DM1", "QR1", "SS1"), key="p023_model")
    split = st.selectbox(
        "P023 role", ("development", "inner_validation", "refit", "inner_train"), key="p023_role"
    )
    role(split)
    if view == "Guide":
        st.markdown(s.file("guide.md").read_text())
        return
    if view == "Comparisons":
        f = pd.DataFrame(json.loads(s.file("scores.json").read_text()))
        f = f.loc[f.role.eq(split) & f.arm.eq(arm)]
        st.dataframe(f, width="stretch")
        st.dataframe(
            s.table("paired_differences.csv").query("role == @split and arm == @arm"),
            width="stretch",
        )
        st.caption(
            (
                "T2/42 is primary; T2/123 is seed sensitivity. Prefix constants "
                "are task-specific. ZERO rank IC is undefined."
            )
        )
        return
    if view == "Optimization / Gradients":
        f = s.table("optimization.csv")
        f = f.loc[f.arm.eq(arm)]
        for phase in ["calibration", "refit"]:
            g = f.loc[f.phase.eq(phase)]
            st.subheader(phase)
            chart(
                px.line(
                    g,
                    x="epoch",
                    y="optimized_objective",
                    color="kind",
                    title=arm + " actual loss · incompatible across arms",
                ),
                "p023_loss_" + phase,
            )
            if arm != "QR1":
                chart(
                    px.line(
                        g, x="epoch", y="original_mse", color="kind", title="Original TG20 MSE"
                    ),
                    "p023_mse_" + phase,
                )
            t = g.loc[g.kind.eq("training")]
            chart(
                px.line(
                    t,
                    x="epoch",
                    y=[
                        "preclip_norm_p50",
                        "preclip_norm_p90",
                        "preclip_norm_p99",
                        "postclip_norm_max",
                    ],
                    title="Global gradient norm · cap1",
                ),
                "p023_grad_" + phase,
            )
            st.dataframe(g, width="stretch")
        return
    if view == "Actual-Objective Tails":
        f = s.table("cohorts.parquet")
        f = f.loc[f.arm.eq(arm) & f.role.eq(split)]
        names = st.multiselect(
            "P023 cohorts",
            f.cohort.tolist(),
            default=[
                "TARGET_RANK_TOP1",
                "TARGET_RANK_TOP5",
                "RANGE_ABS_0.99",
                "RANGE_ABS_0.95",
                "BOTH_5",
                "NUM_ONLY_5",
                "MAD_ONLY_5",
                "NEITHER_5",
            ],
        )
        g = f.loc[f.cohort.isin(names)]
        chart(px.bar(g, x="cohort", y="weighted_loss_share_pct"), "p023_tails")
        st.dataframe(g, width="stretch")
        st.caption(
            (
                "Final checkpoint dropoutOFF; online sampled/dropoutON losses are "
                "separate. Ranked vs maximum-anchored ranges differ. Overlapping "
                "groups do not add. RMSE is not additive."
            )
        )
        return
    if view == "Exact Cases":
        st.caption(
            (
                "Refit in-sample cases regardless of role selector. First48hours "
                "are inputs; last4hours are outcomes."
            )
        )
        cases = s.table(arm + "/cases.parquet")
        case = st.selectbox("P023 exact case", cases.case_id.tolist())
        if case is None:
            return
        st.dataframe(cases.loc[cases.case_id.eq(case)].T.astype(str), width="stretch")
        candles = s.table(arm + "/case_candles.parquet")
        candles = candles.loc[candles.case_id.eq(case)]
        chart(
            go.Figure(
                go.Candlestick(
                    x=candles.hour_end_utc,
                    open=candles.open,
                    high=candles.high,
                    low=candles.low,
                    close=candles.close,
                )
            ),
            "p023_case",
        )
        st.dataframe(candles, width="stretch")
        features = s.table(arm + "/case_features.parquet")
        st.dataframe(features.loc[features.case_id.eq(case)], width="stretch")
        return
    if view == "History / Features":
        ticker = st.selectbox("P023 history stock", SYMBOLS, index=4)
        start = st.date_input(
            "P023 start",
            date(2025, 7, 15),
            min_value=date(2010, 7, 1),
            max_value=date(2025, 12, 31),
        )
        end = st.date_input(
            "P023 end", date(2025, 7, 25), min_value=date(2010, 7, 1), max_value=date(2025, 12, 31)
        )
        dates(str(start), str(end))
        if (end - start).days > 93:
            st.warning("Choose at most93days.")
            return
        study = LongStudy.discover(root)
        candles = study.history(ticker, str(start), str(end))
        from .hf1m_long_ui import candles as history_plot

        history_plot(candles, "p023_history")
        st.dataframe(candles, width="stretch")
        fit = st.selectbox("P023 feature recipe", ("inner", "refit"), index=1)
        origin = st.selectbox("P023 M2 context", (1, 2))
        feature = st.selectbox("P023 channel", ORDER)
        f = safe_features(study, ticker, str(start), str(end), fit, origin)
        if len(f):
            chart(
                px.line(f.loc[f.feature.eq(feature)], x="hour_end_utc", y=["native", "scaled"]),
                "p023_feature",
            )
        st.dataframe(f, width="stretch")
        return
    f = s.table(arm + "/" + split + "/population.parquet")
    if arm == "DM1":
        truth = f.TG20.map(lambda value: 1 if value > 0 else -1 if value < 0 else 0)
        predicted = f.p.ge(0.5).map({True: 1, False: -1})
        st.caption("DM1 all-stock sign confusion: true −1/0/+1, predicted binary −1/+1")
        st.dataframe(
            pd.crosstab(truth, predicted).reindex(index=[-1, 0, 1], columns=[-1, 1], fill_value=0)
        )
    ticker = st.selectbox("P023 output stock", SYMBOLS, index=4)
    f = f.loc[f.ticker.eq(ticker)]
    if arm == "DM1":
        chart(
            px.line(f, x="entry_end_utc", y=["p", "mu_positive", "mu_negative", "z_hat"]),
            "p023_heads",
        )
        st.json(json.loads(s.file(arm + "/" + split + "/metrics.json").read_text()))
        if arm == "DM1":
            st.json(json.loads(s.file(arm + "/" + split + "/sign_calibration.json").read_text()))
    elif arm == "QR1":
        chart(
            px.line(
                f,
                x="entry_end_utc",
                y=["quantiles_y_05", "quantiles_y_50", "quantiles_y_95", "TG20"],
                title="Noncrossing original-TG20 quantiles, not probabilities",
            ),
            "p023_quantiles",
        )
        st.json(json.loads(s.file(arm + "/" + split + "/metrics.json").read_text()))
    else:
        chart(px.line(f, x="entry_end_utc", y=["TG20", "y_hat"]), "p023_ss1_forecast")
        st.dataframe(s.table("SS1/sampler_exposure.csv"), width="stretch")
    st.dataframe(f, width="stretch")
