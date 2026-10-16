"""HF20 study inside the existing Research Explorer, using sealed saved scores only."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..hf20_source import SYMBOLS
from ..hf20_training_authority import IDS
from .hf20 import feature_history, handoff, predictions, table
from .loaders import ViewUnavailable

CAVEAT = (
    "ASSUMPTION_CONDITIONAL · EXPLORATORY_DEVELOPMENT · retrospective surviving cohort; "
    "static source-specific sector mix; issuer/action vintage, dividends and publication "
    "uncertified. Bounded researcher-attested local use; as-reported units, idealized "
    "vendor timing and hourly-close price proxies. Held-out2026-01-07+ locked. "
    "No actual fills, economic profitability or alpha conclusion."
)


def open_hf20() -> None:
    st.session_state.section = "HF20: TM0 vs T2"


def panel(root: Path) -> None:
    st.header("HF20: TM0 vs T2")
    st.caption(CAVEAT)
    h = handoff(root)
    st.info(
        "20 stocks · seed42 · C0/T2/ZERO · canonical TG20 scores. "
        "T2 saved predictions have already been inverted once; the viewer never reinverts."
    )
    with st.expander("Study source, clock, recipes and scales"):
        st.json(
            {
                k: h[k]
                for k in (
                    "source_revision",
                    "symbols",
                    "feature_id",
                    "target_id",
                    "clock_id",
                    "preparation_id",
                    "scales",
                    "runs",
                    "global_started_pairs",
                )
            }
        )
    run_id = st.selectbox("HF20 recorded run", list(IDS), key="hf20_run")
    stock = st.selectbox("HF20 stock", list(SYMBOLS), index=4, key="hf20_stock")
    dates = st.date_input(
        "HF20 development dates",
        (date(2025, 4, 10), date(2026, 1, 6)),
        min_value=date(2025, 3, 31),
        max_value=date(2026, 1, 6),
        key="hf20_dates",
    )
    origin = st.selectbox(
        "HF20 origin", ["Both", "1 · 10:32 ET", "2 · 11:32 ET"], key="hf20_origin"
    )
    if not isinstance(dates, tuple) or len(dates) != 2:
        st.info("Choose both dates.")
        return
    h, full, subset = predictions(root, dates[0].isoformat(), dates[1].isoformat(), stock, run_id)
    if origin != "Both":
        subset = subset.loc[subset.origin.eq(int(origin[0]))]
    tabs = st.tabs(
        [
            "Predictions & Errors",
            "Training Diagnostics",
            "Price & Features / extremes",
            "Five-minute guide",
        ]
    )
    with tabs[0]:
        st.subheader("Full eligible population — fixed denominator")
        st.dataframe(table(root, h, "matched_metrics.csv"), hide_index=True, width="stretch")
        st.caption(
            "All366origins ×20stocks=7320rows over183sessions. Equal stock → eligible "
            "origin → session weights. ZERO rank IC is mathematically undefined; "
            "project-zero convention is reported separately. No five-stock MSE comparison."
        )
        st.subheader("Currently plotted subset")
        st.caption(
            f"{len(subset)} rows / {subset.session.nunique()} sessions; "
            "filters do not alter full-population metrics."
        )
        if subset.empty:
            st.info("No saved eligible origins in this filter.")
        else:
            subset = subset.copy()
            subset["origin_time"] = pd.to_datetime(subset.forecast_issuance_UTC, utc=True)
            fig = go.Figure()
            for name in ("target", "C0", "T2", "ZERO"):
                fig.add_trace(
                    go.Scatter(
                        x=subset.origin_time, y=subset[name], name=name, mode="lines+markers"
                    )
                )
            fig.update_layout(
                yaxis_title="Canonical original TG20", xaxis_title="Forecast issuance UTC"
            )
            st.plotly_chart(fig, width="stretch", key="hf20_scores")
            residual = go.Figure()
            for name in ("C0", "T2", "ZERO"):
                residual.add_trace(
                    go.Scatter(x=subset.origin_time, y=subset[name] - subset.target, name=name)
                )
            residual.update_layout(yaxis_title="Score minus TG20", title="Subset residuals")
            st.plotly_chart(residual, width="stretch", key="hf20_residual")
            st.dataframe(subset, hide_index=True, width="stretch")
        st.dataframe(table(root, h, "monthly_metrics.csv"), hide_index=True, width="stretch")
        st.caption("Monthly panels are exploratory descriptions; no tuning or final confirmation.")
    with tabs[1]:
        arm = "T2" if run_id == IDS[1] else "C0"
        r = h["run_artifacts"][arm]
        import json

        from .hf20 import verified

        result = json.loads(verified(root, r["run_result"]).read_text())
        timing = json.loads(verified(root, r["runtime"]).read_text())
        st.json(dict(selection=result["selection"], health=result["health"], actual_runtime=timing))
        for stage in ("calibration", "refit"):
            f = pd.read_csv(verified(root, r[stage]), float_precision="round_trip")
            st.subheader(arm + " · " + stage)
            st.caption(
                "Optimizer objective: "
                + (
                    "asinh(TG20/s) squared units; NOT DIRECTLY COMPARABLE to C0"
                    if arm == "T2"
                    else "original TG20 squared units"
                )
            )
            for fields, label in (
                (("optimizer_objective",), "Optimizer objective"),
                (
                    ("canonical_training_MSE", "validation_MSE")
                    if stage == "calibration"
                    else ("canonical_training_MSE",),
                    "Original TG20 MSE",
                ),
                (("median", "p90", "p99"), "Preclip global gradient norm"),
                (("clipped_fraction",), "Fraction above cap1"),
            ):
                fig = go.Figure()
                for name in fields:
                    fig.add_trace(go.Scatter(x=f.epoch, y=f[name], name=name))
                fig.add_vline(x=result["selection"]["selected"], line_dash="dash")
                fig.update_layout(title=label, xaxis_title="Epoch", height=260)
                st.plotly_chart(fig, width="stretch", key="hf20_" + stage + label)
            st.dataframe(f, hide_index=True, width="stretch")
        st.warning(
            "G6 clipping WARNs are retained; "
            "changed objective units do not establish clipping causality."
        )
    with tabs[2]:
        st.caption(
            "Ex-post extreme selection is diagnostic only; it never enters X or training choices."
        )
        options = (
            full.loc[full.symbol.eq(stock)]
            .assign(magnitude=lambda f: f.target.abs())
            .sort_values("magnitude", ascending=False)
        )
        keys = [
            f"{r.session} / origin{r.origin} / TG20={r.target:.3f}" for r in options.itertuples()
        ]
        choice = st.selectbox(
            "HF20 genuine origin (largest |TG20| first)",
            range(len(keys)),
            format_func=lambda i: keys[i],
            key="hf20_event",
        )
        row = options.iloc[choice]
        if st.button("Load genuine HF hourly candles + 48 feature steps", key="hf20_load_features"):
            st.session_state.hf20_loaded_event = (stock, str(row.session), int(row.origin))
        if st.session_state.get("hf20_loaded_event") == (stock, str(row.session), int(row.origin)):
            try:
                features, candles, clocks = feature_history(
                    root, h, stock, str(row.session), int(row.origin)
                )
                st.json(clocks)
                st.caption(
                    "Hourly interval-start OHLCV, as reported; no reconstructed30-minute bars. "
                    "Proxy price references are not executable fills; publication timing UNKNOWN."
                )
                fig = go.Figure(
                    go.Candlestick(
                        x=candles.datetime,
                        open=candles.open,
                        high=candles.high,
                        low=candles.low,
                        close=candles.close,
                        name=stock,
                    )
                )
                for label in ("feature_cutoff_UTC", "exit_proxy_reference_UTC"):
                    fig.add_vline(
                        x=pd.Timestamp(clocks[label]).timestamp() * 1000, line_dash="dash"
                    )
                fig.update_layout(
                    xaxis_title="Interval START (UTC)", yaxis_title="As-reported price"
                )
                st.plotly_chart(fig, width="stretch", key="hf20_candles")
                st.plotly_chart(
                    go.Figure(go.Bar(x=candles.datetime, y=candles.volume, name="Share volume")),
                    width="stretch",
                    key="hf20_volume",
                )
                feature = st.selectbox(
                    "HF20 FT1 channel", list(features.feature.unique()), key="hf20_channel"
                )
                if feature is None:
                    st.info("Choose a feature channel.")
                    return
                f = features.loc[features.feature.eq(feature)]
                for field in ("native", "scaled"):
                    fig = go.Figure(
                        go.Scatter(x=f.step, y=f[field], mode="lines+markers", name=feature)
                    )
                    fig.update_layout(
                        title=feature + " · " + field,
                        xaxis_title="Scheduled step (−47…0)",
                        yaxis_title=field + " FT1 units",
                    )
                    st.plotly_chart(fig, width="stretch", key="hf20_feature_" + field)
                st.dataframe(features, hide_index=True, width="stretch")
            except (OSError, ValueError, ViewUnavailable) as exc:
                st.warning("SOURCE/CHRONOLOGY HOLD: " + str(exc))
    with tabs[3]:
        guide = root / "docs/track_a/HOW_TO_VIEW_HF20_TM0_T2.md"
        if guide.is_file():
            st.markdown(guide.read_text())
        else:
            st.info("Guide is not yet recorded; no synthetic evidence is substituted.")
