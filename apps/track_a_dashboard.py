"""Local read-only Track A research explorer. Launch using the documented .venv command."""

from __future__ import annotations

import logging
import time
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from lstm_data.ft0_transforms import ORDER
from lstm_data.pretraining_policy import CANDIDATE
from lstm_data.pretraining_tables import BaseTables
from lstm_data.visualization import figures as charts
from lstm_data.visualization.controlled_ui import (
    base as shared_base_store,
)
from lstm_data.visualization.controlled_ui import (
    controlled_page,
    feature_explorer,
    open_study,
)
from lstm_data.visualization.definitions import FEATURES, MARKET
from lstm_data.visualization.loaders import (
    CAVEAT,
    PARTITIONS,
    Catalog,
    ViewUnavailable,
    event_markers,
    feature_frame,
    gradient_batches,
    market_frame,
    peer_window,
    predictions,
    read_json,
    saved_gates,
    source_bars,
    target_details,
    training_trace,
)
from lstm_data.visualization.metrics import loss_concentration, matched, summary
from lstm_data.visualization.range_ui import full_data_page

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = (
    "Start Here",
    "Price & Features",
    "Predictions & Errors",
    "Training Diagnostics",
    "Research Notes / Provenance",
    "Controlled Experiments",
    "B1 Normalization (012B)",
    "HF20: TM0 vs T2",
    "HF1M Long — 20 stocks (2010–2025)",
    "HF1M Long — Objective Improvement Screen (P022)",
    "HF1M Long — Direction / Quantiles / Sampling (P023)",
    "HF1M Long — Optimization & Capacity (P024)",
    "HF1M Long — E1 / QR1 Replication (P025)",
    "HF1M Long — Temporal Architectures (P026)",
    "HF1M Long — Cross-Stock Sharing (P027)",
)
PLOT_CONFIG = {"displaylogo": False, "scrollZoom": True, "modeBarButtonsToRemove": ["toImage"]}


@st.cache_data(max_entries=48, show_spinner=False)
def saved_predictions(
    root: str, token: tuple, fold: str, model: str, partition: str
) -> pd.DataFrame:
    return predictions(Catalog.discover(Path(root)), fold, model, partition)


@st.cache_resource(max_entries=1, show_spinner="Reading the existing canonical feature store…")
def base_store(root: str, token: tuple) -> BaseTables:
    return shared_base_store(root, token)


@st.cache_data(max_entries=24, show_spinner=False)
def price_data(
    root: str, token: tuple, symbol: str, start: str, end: str, interval: str
) -> tuple[pd.DataFrame, dict]:
    return source_bars(Catalog.discover(Path(root)), symbol, start, end, interval)


@st.cache_data(max_entries=24, show_spinner=False)
def feature_data(
    root: str,
    token: tuple,
    symbol: str,
    fold: str,
    start: str,
    end: str,
    origin: int,
    partition: str,
) -> pd.DataFrame:
    c = Catalog.discover(Path(root))
    return feature_frame(c, base_store(root, token), symbol, fold, start, end, origin, partition)


def plot(fig: go.Figure, key: str) -> None:
    st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG, key=key)


def set_section(section: str) -> None:
    st.session_state.section = section


def reset_dates() -> None:
    c = Catalog.discover(ROOT)
    f = st.session_state.get("fold", "WF2")
    p = st.session_state.get("partition", "Development")
    if p == "Full data":
        return
    frame = saved_predictions(str(ROOT), c.token(), f, "TM0", p)
    first, last = date.fromisoformat(frame.session.min()), date.fromisoformat(frame.session.max())
    if f == "WF2" and p == "Development":
        first = date(2024, 1, 16)
    st.session_state.dates = (first, min(first + timedelta(days=3), last))


def filter_frame(
    frame: pd.DataFrame, start: str, end: str, origins: tuple[int, ...], symbol: str | None = None
) -> pd.DataFrame:
    mask = frame.session.between(start, end) & frame.origin.isin(origins)
    if symbol is not None:
        mask &= frame.symbol.eq(symbol)
    return frame.loc[mask].copy()


def start_here(c: Catalog) -> None:
    from lstm_data.visualization.hf1m_long_ui import open_long

    st.button("Open HF1M Long —20 stocks (2010–2025)", on_click=open_long, key="start_hf1m_long")
    from lstm_data.visualization.hf20_ui import open_hf20

    st.button("Open HF20: TM0 vs T2", on_click=open_hf20, key="start_hf20")
    from lstm_data.visualization.hf20_ui import open_replication

    st.button("HF20 seed replication", on_click=open_replication, key="start_hf20_replication")
    from lstm_data.visualization.nb1_ui import open_nb1
    from lstm_data.visualization.normalization_ui import open_audit

    st.info(
        "New: target ranges, inline candles and Price & Features → Partition → Full data. "
        "Walkthrough: docs/track_a/HOW_TO_INSPECT_TG_RANGES_AND_CANDLES.md"
    )
    with st.expander("Read the target ranges & Full data guide · three-minute example"):
        st.markdown((ROOT / "docs/track_a/HOW_TO_INSPECT_TG_RANGES_AND_CANDLES.md").read_text())
    st.title("See the data. Follow the evidence.")
    st.write(
        "Explore the completed candidate experiments, from genuine candles to saved forecasts "
        "and training diagnostics. Everything stays on this computer."
    )
    a, b, d = st.columns(3)
    a.metric("Candidate stocks", "5")
    b.metric("Explored folds", "WF1 · WF2")
    if c.config.get("nb1_experiment"):
        packet = read_json(c.root, c.config["nb1_experiment"])
        d.metric("Cumulative research pairs", f"{packet.get('global_started_pairs', 24)} / 200")
    else:
        d.metric("Pairs at package seal", f"{c.config.get('global_started_at_seal', 6)} / 40")
    if c.config.get("controlled_models"):
        st.caption(
            "Package011 arms use seed labels in brackets. TM0 is C0 seed42; "
            "compare seed123 arms with C0 [123]. These are saved package results."
        )
    st.button("Package 011: Compare C0 and T2", on_click=open_study, type="primary")
    st.button("Package012A normalization audit", on_click=open_audit)
    if c.config.get("nb1_experiment"):
        st.button("Package012B B1 experiment", on_click=open_nb1)
    st.caption("TM0 architecture · matched C0/H1/T1/T2/O1 arms · seeds42/123 · saved evidence only")
    st.subheader("Your first five minutes")
    st.markdown(
        "1. Open **Price & Features**. Keep **AAPL / WF2 / TM0 / January16–19,2024**. "
        "You will see candles, volume below and normalized RSI14 (T5).\n"
        "2. Switch **30 min source → Completed hour**, then try M1 in the feature panel. "
        "Enable event markers to see cutoff, idealized events and future label close.\n"
        "3. Open **Predictions & Errors**, then **Training Diagnostics**. Compare saved "
        "scores with EX-POST TG0, and inspect calibration clipping separately from refit."
    )
    st.button(
        "Open Price & Features", on_click=set_section, args=("Price & Features",), type="primary"
    )
    st.info(
        "T5 = (Wilder RSI14−50)/50, native [−1,1]. M1 is a volatility-normalized move. "
        "TG0 is future universe-relative performance. Score sign is not absolute return direction. "
        "Rank IC compares all five names; constant ZERO gets IC0 by project convention."
    )
    with st.expander("Coverage, setup and interpretation"):
        st.markdown(
            "**WF1:** TM0, MC0, MC1, E5, ZERO, M1 and two saved ridge baselines.\n\n"
            "**WF2:** TM0, MC0 and ZERO. MC1/E5 do not have WF2 fits.\n\n"
            "Price candles are vendor split-adjusted USD and inverse-split volume. "
            "These are retrospective representations. Model inputs use training-fitted "
            "scaling, distinct from prices and native feature transforms.\n\n"
            "Training-view forecasts are in-sample final-refit diagnostics. Inner-validation "
            "scores come from the selected calibration checkpoint. Neither is outer-fold OOS."
        )
        st.code("./scripts/run_track_a_dashboard.sh", language="bash")
        st.caption(
            "Guides: docs/track_a/Visualization_Quickstart.md and Visualization_User_Guide.md"
        )
    st.caption(CAVEAT)


def price_page(
    c: Catalog,
    token: tuple,
    fold: str,
    model: str,
    partition: str,
    symbol: str,
    start: str,
    end: str,
    origins: tuple[int, ...],
) -> None:
    st.header("Price & Features")
    controls = st.columns(3)
    interval = controls[0].selectbox("Candle interval", ["30 min source", "Completed hour"])
    scale = controls[1].selectbox("Price scale", ["Linear", "Log"])
    context = controls[2].selectbox(
        "Feature origin context",
        [1, 2],
        format_func=lambda x: "10:30 ET" if x == 1 else "11:30 ET",
        key="feature_origin",
        help="M2 is locked to its historical forecast-origin type.",
    )
    selected = st.multiselect(
        "FT0 features (up to4)",
        list(ORDER),
        default=["T5"],
        max_selections=4,
        help="Native transform and scaled input differ. All FT0 channels here are dimensionless.",
    )
    mode = st.radio(
        "Feature representation",
        ["native", "scaled"],
        horizontal=True,
        help="Scaled means the exact bound inner/full-prefix recipe; no new fitting.",
    )
    options = st.columns(3)
    markers_on = options[0].checkbox(
        "Show forecast / horizon events", value=False, key="price_markers"
    )
    overlay_on = options[1].checkbox(
        "Overlay previous20 daily SMA",
        value=False,
        help="Faithful reconstruction: completed close / exp(native T1).",
    )
    compress = options[2].checkbox(
        "Compress overnight/weekend gaps",
        value=False,
        help="Display rangebreaks only; UTC keys and data stay unchanged.",
    )
    t = time.monotonic()
    with st.spinner("Reading the selected local source window…"):
        bars, meta = price_data(str(ROOT), token, symbol, start, end, interval)
    features = None
    if selected or overlay_on:
        features = feature_data(str(ROOT), token, symbol, fold, start, end, context, partition)
    overlay = None
    if overlay_on and features is not None:
        native_t1 = features.loc[features.feature == "T1", ["timestamp", "native"]]
        overlay = native_t1.merge(
            bars[["available_at", "close"]],
            left_on="timestamp",
            right_on="available_at",
            validate="one_to_one",
        )
        overlay["price"] = overlay.close / np.exp(overlay.native)
    markers = event_markers(start, end, origins) if markers_on else None
    plot(charts.candles(bars, markers, overlay, scale == "Log", compress), "price_candles")
    st.caption(
        "What am I looking at? Genuine RTH bars labeled at interval START; hover shows ET "
        "and exact UTC. Volume uses the same interval. Gold volume is the closing stub. "
        "Completed-hour mode excludes stubs and never fills missing candles. "
        "Features below are timestamped at completed interval END."
    )
    if markers_on:
        st.warning(
            "MODEL/LABEL EVENTS, NOT FILLS: 10:30→14:30 and11:30→15:30 completed-close "
            "proxies; nominal entry10:33/11:33 and exit/maturity14:33/15:33. Future "
            "boundaries are EX-POST LABEL context; early-close ineligible origins are omitted."
        )
    st.caption(
        f"{meta['rows']} candles · {meta['stub_count']} closing stubs · "
        f"load + figure submission {time.monotonic() - t:.3f}s (server wall time)."
    )
    if features is not None and selected:
        plot(charts.features(features, selected, mode), "ft0_features")
        st.caption(
            "Native = approved feature transform with the bound floors; scaled = "
            "float32 model-input values using the selected recipe. Historical fitting "
            "availability is assumed retrospectively. Missing values remain gaps."
        )
        for feature in selected:
            st.caption(f"**{feature}:** {FEATURES[feature]}")
    if model in ("MC0", "MC1", "E5") and st.checkbox("Show SPY U1–U5 state panel"):
        channels = st.multiselect("SPY channels", list(MARKET), default=["U1"], max_selections=3)
        plot(
            charts.features(market_frame(c, fold, start, end, partition), channels, mode), "market"
        )
        st.caption(
            "SPY ETF state at its own completed-hour clock; no certified USA500 substitution. "
            "Missing native states stay gaps; they are not presented as observed zeros."
        )
    if start <= "2020-08-31" and end >= "2020-08-28":
        st.warning(
            "AAPL split-period context: the entire axis uses the same retrospective vendor "
            "split-price/inverse-volume basis. Raw/unadjusted prices and PIT action vintage "
            "are not recorded here; scales are never blended."
        )
    with st.expander("Selected candle and source information"):
        position = st.selectbox(
            "Inspect candle",
            list(range(len(bars))),
            format_func=lambda i: str(bars.iloc[i].time_ET),
        )
        candle = bars.iloc[position]
        st.write(f"**{symbol}** · {candle.time_ET} · UTC {candle.UTC_key}")
        st.write(
            f"O {candle.open:.4f} · H {candle.high:.4f} · L {candle.low:.4f} · "
            f"C {candle.close:.4f} USD · volume {candle.volume:,.0f} adjusted shares"
        )
        st.json(meta)
        st.caption(
            "Observed publication latency, local rights and action vintage remain unverified. "
            "Only the approved idealized period-end clock is used."
        )

    with st.expander("Feature Scaling Explorer / actual 48-step context"):
        if st.checkbox("Open read-only Feature Scaling Explorer"):
            event = st.session_state.get("selected_study_event")
            if event is not None and (
                event["fold"] != fold
                or event["partition"] != partition
                or event["session"] != start
                or start != end
            ):
                event = None
            feature_explorer(c, token, fold, partition, symbol, start, end, context, event)


def predictions_page(
    c: Catalog,
    token: tuple,
    fold: str,
    model: str,
    partition: str,
    symbol: str,
    start: str,
    end: str,
    origins: tuple[int, ...],
) -> None:
    st.header("Predictions & Errors")
    full = saved_predictions(str(ROOT), token, fold, model, partition)
    panel = filter_frame(full, start, end, origins)
    if panel.empty:
        raise ViewUnavailable("No observations for these filters. Try another trading date/origin.")
    stock = panel.loc[panel.symbol == symbol]
    choices = ["None"] + [n for n in c.model_names(fold, partition) if n != "M1" and n != model]
    baseline_name = st.selectbox(
        "Optional saved reference", choices, index=choices.index("ZERO") if "ZERO" in choices else 0
    )
    baseline = None
    baseline_full = None
    if baseline_name != "None":
        baseline_full = saved_predictions(str(ROOT), token, fold, baseline_name, partition)
        baseline_all = filter_frame(baseline_full, start, end, origins)
        matched(panel, baseline_all)
        baseline = baseline_all.loc[baseline_all.symbol == symbol]
    st.warning(
        "EX-POST OUTCOMES: realized TG0 and residuals mature four hours +3 minutes after "
        "cutoff. They were not available to the forecast. No trading P&L is shown."
    )
    if model == "M1":
        st.info(
            "M1 is a ranking feature, not a calibrated TG0 forecast. Its score uses a separate "
            "panel; the historical score-to-target MSE is only a unit-sensitive diagnostic."
        )
    plot(charts.forecasts(stock, baseline), "forecasts")
    st.caption(
        "What am I looking at? Immutable saved scores and future relative TG0, in "
        "separate units from dollar candles. ZERO IC0 is a project convention; defined "
        "Spearman for constant ZERO is unavailable."
    )
    scope = st.radio(
        "Summary scope", ["Visible date/origin window", "Full recorded partition"], horizontal=True
    )
    cohort = panel if scope.startswith("Visible") else full
    stats = summary(cohort)
    cols = st.columns(4)
    cols[0].metric("Equal-day five-stock MSE", f"{stats['MSE']:.6f}")
    cols[1].metric(
        "Daily five-stock Rank IC",
        f"{stats['daily_Rank_IC']:+.6f}" if stats["daily_Rank_IC"] is not None else "N/A",
    )
    cols[2].metric("Sessions / origins", f"{stats['days']} / {stats['origins']}")
    cols[3].metric("Tied-score origins", stats["tied_origins"])
    stock_mse = (
        cohort.loc[cohort.symbol == symbol].groupby(["session", "origin"]).squared_error.mean()
    )
    st.caption(
        f"{symbol} equal-day MSE: {stock_mse.groupby(level=0).mean().mean():.6f}; "
        "Rank IC is cross-sectional across five stocks, not a one-stock statistic. "
        f"Score SD {stats['score_std']:.6f}; {stats['defined_origins']} defined IC origins."
    )
    by_month = stats["daily"].assign(month=lambda x: x.session.str[:7]).groupby("month")
    month_table = by_month.agg(
        MSE=("MSE", "mean"), daily_IC=("IC", "mean"), days=("session", "count")
    )
    stock_daily = stock_mse.groupby(level=0).mean()
    month_table[f"{symbol}_MSE"] = stock_daily.groupby(stock_daily.index.str[:7]).mean()
    a, b = st.columns(2)
    a.dataframe(month_table, width="stretch")
    b.dataframe(stats["by_origin"], hide_index=True, width="stretch")
    if baseline_full is not None:
        reference_panel = (
            filter_frame(baseline_full, start, end, origins)
            if scope.startswith("Visible")
            else baseline_full
        )
        matched(cohort, reference_panel)
        reference_stats = summary(reference_panel)
        paired = stats["daily"].merge(
            reference_stats["daily"],
            on="session",
            suffixes=("_model", "_reference"),
            validate="one_to_one",
        )
        paired["delta_MSE"] = paired.MSE_model - paired.MSE_reference
        paired["delta_IC"] = paired.IC_model - paired.IC_reference
        st.caption(
            f"Paired {model} − {baseline_name}: mean ΔMSE "
            f"{paired.delta_MSE.mean():+.6f}, mean ΔIC {paired.delta_IC.mean():+.6f}; "
            f"{len(paired)} identical days. Descriptive comparison, no significance claim."
        )
        with st.expander("Paired daily comparison"):
            st.dataframe(paired, hide_index=True, width="stretch")
    keys = list(dict.fromkeys(zip(panel.session, panel.origin)))
    key = st.selectbox(
        "Inspect five-stock forecast origin",
        keys,
        format_func=lambda x: f"{x[0]} · {'10:30' if x[1] == 1 else '11:30'} ET",
    )
    cross = panel.loc[panel.session.eq(key[0]) & panel.origin.eq(key[1])].copy()
    cross["predicted_rank"] = cross.score.rank(ascending=False, method="average")
    cross["realized_rank"] = cross.TG0.rank(ascending=False, method="average")
    cross["rank_difference"] = cross.predicted_rank - cross.realized_rank
    st.dataframe(
        cross[
            [
                "symbol",
                "score",
                "TG0",
                "residual",
                "predicted_rank",
                "realized_rank",
                "rank_difference",
            ]
        ].sort_values("predicted_rank"),
        hide_index=True,
        width="stretch",
    )
    if model == "E5" and st.checkbox("Show actual four-peer M1 context for this origin"):
        peer = peer_window(c, base_store(str(ROOT), token), fold, key[0], key[1], symbol, partition)
        peer["time_ET"] = charts.et_axis(peer.timestamp)
        plot(
            charts.lines(
                peer,
                "time_ET",
                ["four_peer_M1_mean", "four_peer_M1_population_SD"],
                "Four-peer scaled M1 units",
            ),
            "peers",
        )
        st.caption(
            "Population SD of the other four names' actual scaled M1; same48-step context. "
            "The focal stock is excluded. No learned coupling or causal claim."
        )
    if model == "MC1":
        with st.expander("Recorded MC1 gate examples"):
            cases = saved_gates(c)
            case_index = st.selectbox(
                "Saved evaluated gate origin",
                list(range(len(cases))),
                format_func=lambda i: str(cases[i]["key"]),
            )
            example = cases[case_index]
            weights = example["B4_B5"]["MC1"]["gate"]["weights"]
            plot(
                charts.finish(
                    go.Figure(go.Bar(x=list(ORDER), y=weights, marker_color=charts.TEAL)), 330
                ),
                "gate",
            )
            st.caption(
                "16 × softmax(W_g m_t + b_g); weights sum16. Exact Package008 final-checkpoint "
                "examples only, not every date. Feature modulation is not validated feature "
                "importance; other dates' gate values were not saved."
            )


def show_anomaly(day: str, symbol: str, partition: str) -> None:
    st.session_state.dates = (date.fromisoformat(day), date.fromisoformat(day))
    st.session_state.symbol = symbol
    st.session_state.partition = partition
    st.session_state.section = "Price & Features"


def diagnostics_page(
    c: Catalog, token: tuple, fold: str, model: str, start: str, end: str, origins: tuple[int, ...]
) -> None:
    st.header("Training Diagnostics")
    if model not in c.config["models"][fold]:
        st.info(
            "No neural optimizer trace for this saved baseline. Select TM0/MC0/MC1/E5 as available."
        )
        return
    obj = c.result(fold, model)
    trace = training_trace(c, fold, model)
    st.warning(
        f"G6 {obj['G6']} · stop {obj['selector']['status']} · "
        f"selected epoch {obj['selector']['selected']} · raw minimum epoch "
        f"{obj['selector']['raw_epoch']}. Warnings from either pass remain visible."
    )
    cal, refit = trace.loc[trace.stage == "calibration"], trace.loc[trace.stage == "refit"]
    plot(
        charts.lines(
            cal,
            "epoch",
            ["training_MSE", "inner_validation_MSE"],
            "Session-weighted MSE",
            obj["selector"]["selected"],
        ),
        "calibration_curve",
    )
    st.caption(
        "Calibration: dropout-ON training versus dropout-OFF inner-validation MSE. "
        "Selection uses strict >0.1% qualifying improvement and frozen minimum12/patience10. "
        "The raw numerical minimum may differ from the qualifying checkpoint."
    )
    plot(charts.lines(refit, "epoch", ["training_MSE"], "Fresh-refit training MSE"), "refit_curve")
    st.caption(
        "Fresh initialization and optimizer, distinct full-prefix recipe, locked selected "
        "epoch count. Refit is a separate trajectory; there is no second selection."
    )
    stage = st.radio("Diagnostic pass", ["calibration", "refit"], horizontal=True)
    phase = trace.loc[trace.stage == stage]
    plot(
        charts.lines(
            phase, "epoch", ["clipped_fraction"], "Fraction batches with preclip norm >1", cap=0.5
        ),
        "clip_fraction",
    )
    st.dataframe(
        phase[
            [
                "epoch",
                "grad_p50",
                "grad_p95",
                "grad_max",
                "clipped_fraction",
                "nonfinite",
                "warning",
                "steps",
            ]
        ],
        hide_index=True,
        width="stretch",
    )
    cap = float(obj["contract"]["clip"])
    st.caption(
        f"One global clip; applied multiplier min(1,{cap}/(norm+1e−6)). "
        "The historical norm>1 warning remains visible; it differs from the applied cap for O1."
    )
    if model in c.config.get("controlled_models", {}).get(fold, {}):
        st.dataframe(
            phase[
                [
                    "epoch",
                    "objective_name",
                    "optimizer_objective",
                    "training_MSE",
                    "applied_clipping_fraction",
                    "fraction_above5",
                ]
            ],
            hide_index=True,
            width="stretch",
        )
        st.caption(
            "T2 scores are already converted once to canonical TG0. "
            "T1 preserves original targets. These are explored development comparisons."
        )
    if fold == "WF2" or model in c.config.get("controlled_models", {}).get(fold, {}):
        batches = gradient_batches(c, fold, model, stage)
        plot(
            charts.lines(
                batches,
                "optimizer_step_id",
                ["preclip_global_grad_norm"],
                "Preclip global L2 norm",
                cap=float(obj["contract"]["clip"]),
            ),
            "batch_norms",
        )
        plot(charts.gradient_scatter(batches), "batch_scatter")
        st.caption(
            "ASSOCIATION, NOT CAUSATION. Color = batch maximum |TG0|. Repeated sessions, "
            "epochs and changing weights prevent per-example causal attribution. "
            "Full optimizer-state histories and dropout masks were not recorded."
        )
    else:
        st.info(
            "Not recorded: WF1 paired batch losses/norms. Only saved epoch aggregates are "
            "available; historical batch telemetry is never fabricated."
        )
    st.subheader("Extreme targets and session loss concentration")
    target_partition = st.selectbox("Target / loss partition", list(PARTITIONS), index=2)
    frame = saved_predictions(str(ROOT), token, fold, model, target_partition)
    if st.checkbox("Limit tails and concentration to visible dates", value=False):
        frame = filter_frame(frame, start, end, origins)
    else:
        frame = frame.loc[frame.origin.isin(origins)]
    if frame.empty:
        st.info("No saved targets in the selected partition/date/origin combination.")
        return
    months = st.multiselect(
        "Tail / loss months (empty = all)", sorted(frame.session.str[:7].unique())
    )
    if months:
        frame = frame.loc[frame.session.str[:7].isin(months)]
    if frame.empty:
        st.info("No observations for these months.")
        return
    tail_stock = st.selectbox("Tail stock", ["All five"] + list(CANDIDATE))
    tails = frame if tail_stock == "All five" else frame.loc[frame.symbol == tail_stock]
    log_count = st.checkbox("Log histogram counts", value=False)
    hist = charts.finish(
        go.Figure(go.Histogram(x=tails.TG0, nbinsx=60, marker_color=charts.TEAL)), 340
    )
    hist.update_xaxes(title_text="Realized TG0 · EX-POST " + target_partition)
    hist.update_yaxes(title_text="Stock-observation count", type="log" if log_count else "linear")
    plot(hist, "target_hist")
    quantiles = tails.TG0.quantile([0, 0.01, 0.5, 0.95, 0.99, 1])
    st.write(
        f"Actual max |TG0| **{tails.TG0.abs().max():.5f}** · {len(tails)} stock rows "
        f"· {tails.session.nunique()} sessions · {target_partition}"
    )
    st.dataframe(quantiles.rename("TG0").to_frame().T, width="stretch")
    percentile = st.slider("Absolute-target extreme percentile (display filter only)", 90, 100, 99)
    cutoff = float(tails.TG0.abs().quantile(percentile / 100))
    extreme = tails.loc[tails.TG0.abs() >= cutoff].copy()
    extreme = extreme.assign(abs_target=extreme.TG0.abs()).sort_values(
        "abs_target", ascending=False
    )
    st.dataframe(
        extreme[["session", "origin", "symbol", "TG0", "score", "residual", "maturity"]].head(25),
        hide_index=True,
        width="stretch",
    )
    if not extreme.empty:
        i = st.selectbox(
            "Navigate an extreme observation",
            list(range(min(25, len(extreme)))),
            format_func=lambda j: (
                f"{extreme.iloc[j].session} · "
                f"{extreme.iloc[j].symbol} · origin {extreme.iloc[j].origin}"
            ),
        )
        row = extreme.iloc[i]
        st.button(
            "Inspect this date's candles",
            on_click=show_anomaly,
            args=(str(row.session), str(row.symbol), target_partition),
        )
    if st.checkbox("Inspect canonical numerator / MAD / fitted floor", value=False):
        details = target_details(
            c, base_store(str(ROOT), token), fold, target_partition, extreme.head(25)
        )
        st.dataframe(details, hide_index=True, width="stretch")
        st.caption(
            "TG0 = (stock future log return − five-stock median)/(MAD + fitted epsilon). "
            "Uses the exact existing inner/refit floor. No floor is fitted for this display."
        )
    ranked, concentration = loss_concentration(frame)
    plot(
        charts.lines(
            ranked,
            "fraction_sessions",
            ["cumulative_loss_share"],
            "Cumulative loss share, worst sessions first",
        ),
        "concentration",
    )
    st.caption(
        "Five stocks averaged within origin, origins averaged within day, equal days. "
        "This is a worst-first cumulative concentration curve, not a trading equity curve."
    )
    st.json(concentration["shares"])
    st.dataframe(ranked.head(25), hide_index=True, width="stretch")
    st.caption(
        "The top1/5/10% counts use ceil(p×N). Concentration is descriptive; it does not "
        "establish that those sessions caused gradient clipping."
    )


def provenance_page(c: Catalog, token: tuple) -> None:
    st.header("Research Notes / Provenance")
    st.write(CAVEAT)
    st.markdown(
        "**Timing:** candle keys are interval starts in UTC; display uses ET with DST. "
        "Features use completed-hour ends. Proxy target prices are10:30→14:30 or "
        "11:30→15:30 closes; idealized event/maturity times are three minutes later.\n\n"
        "**Scope:** explored training/inner/WF1/WF2 only. Confirmation begins July1,2024 "
        "and is blocked before raw numeric reads. No strategy, orders, model fitting, "
        "scaler fitting, vendor connection or bulk export is provided.\n\n"
        "**Interpretation:** native FT0, training-scaled inputs, prices, targets, residuals "
        "and cross-sectional ranks have different meanings. Gate weights are modulation, "
        "not causal importance. Predictive metrics are not profitability or alpha.\n\n"
        "**Future experiments:** target/loss/normalization studies remain a separate "
        "human-controlled package. This app makes no experimental decision."
    )
    st.subheader("Source-backed fold summaries")
    records = []
    for fold in ("WF1", "WF2"):
        reference = read_json(c.root, c.config["reference_metrics"][fold])
        if fold == "WF2":
            reference = reference["metrics"]
        for model in ("TM0", "MC0", "MC1", "E5", "ZERO"):
            if model not in c.model_names(fold):
                continue
            frame = saved_predictions(str(ROOT), token, fold, model, "Development")
            m = summary(frame)
            expected = reference[model]
            if (
                abs(m["MSE"] - expected["MSE"]) > 2e-6
                or abs(m["daily_Rank_IC"] - expected["daily_Rank_IC"]) > 1e-12
            ):
                raise ViewUnavailable("Saved fold reference failed metric reconciliation.")
            records.append(
                {
                    "fold": fold,
                    "model": model,
                    "MSE": m["MSE"],
                    "daily_Rank_IC": m["daily_Rank_IC"],
                    "sessions": m["days"],
                    "origins": m["origins"],
                    "reference_reconciled": True,
                    "local_checkpoint": (
                        "Available / hash checked"
                        if (c.root / c.config["checkpoints"][fold][model]["path"]).is_file()
                        else "Unavailable; saved snapshot only"
                    )
                    if model != "ZERO"
                    else "N/A",
                }
            )
    st.dataframe(pd.DataFrame(records), hide_index=True, width="stretch")
    st.caption(
        "Each value is computed from actual loaded snapshots and reconciled to its bound "
        "report. No current model beats its fold's ZERO MSE. ZERO defined-only IC is N/A."
    )
    st.subheader("Local file bindings")
    st.json(
        {
            k: c.config[k]
            for k in ("manifest", "source_manifest", "market", "recipes", "models", "checkpoints")
        }
    )
    st.info(
        "Missing checkpoints do not create new forecasts: the app uses bound saved snapshots. "
        "Weight bytes, if present, are hash-checked but never deserialized by this app. "
        "Local data must be provisioned using data/README.md and the existing manifests."
    )
    st.caption(
        "Guides: docs/track_a/Visualization_Quickstart.md · Visualization_User_Guide.md. "
        "Stop with Ctrl+C in the launching terminal. Localhost only; do not share raw-data "
        "screenshots before checking applicable rights."
    )


def main() -> None:
    st.set_page_config(page_title="Track A · Research Explorer", page_icon="📊", layout="wide")
    t = time.monotonic()
    st.sidebar.title("Track A")
    st.sidebar.caption("Research explorer · local / read-only")
    section = st.sidebar.radio("Explore", SECTIONS, key="section")
    if section == "HF1M Long — Cross-Stock Sharing (P027)":
        from lstm_data.visualization.peer_screen_ui import panel as peer_panel

        try:
            peer_panel(ROOT)
        except (OSError, ValueError, KeyError) as exc:
            st.error(str(exc))
        return
    if section == "HF1M Long — Temporal Architectures (P026)":
        from lstm_data.visualization.temporal_screen_ui import panel as temporal_panel

        try:
            temporal_panel(ROOT)
        except (OSError, ValueError, KeyError) as exc:
            st.error(str(exc))
        return
    if section == "HF1M Long — E1 / QR1 Replication (P025)":
        from lstm_data.visualization.branch_replication_ui import panel as replication_panel

        try:
            replication_panel(ROOT)
        except (OSError, ValueError, KeyError) as exc:
            st.error(str(exc))
        return
    if section == "HF1M Long — Optimization & Capacity (P024)":
        from lstm_data.visualization.optimization_screen_ui import panel as optimization_panel

        try:
            optimization_panel(ROOT)
        except (OSError, ValueError, KeyError) as exc:
            st.error(str(exc))
        return
    if section == "HF1M Long — Direction / Quantiles / Sampling (P023)":
        from lstm_data.visualization.dm_quantile_ui import panel as dm_quantile_panel

        try:
            dm_quantile_panel(ROOT)
        except (OSError, ValueError, KeyError) as exc:
            st.error(str(exc))
        return
    if section == "HF1M Long — Objective Improvement Screen (P022)":
        from lstm_data.visualization.objective_screen_ui import panel as objective_panel

        try:
            objective_panel(ROOT)
        except (OSError, ValueError, KeyError) as exc:
            st.error(str(exc))
        return
    if section == "HF1M Long — 20 stocks (2010–2025)":
        from lstm_data.visualization.hf1m_long_ui import panel as long_panel

        try:
            long_panel(ROOT)
        except (OSError, ValueError, KeyError) as exc:
            st.error(str(exc))
        return
    try:
        c = Catalog.discover(ROOT)
        token = c.token()
    except (OSError, ValueError, KeyError) as exc:
        st.title("Track A · local setup")
        st.error(str(exc))
        st.info(
            "Local evidence is unavailable. Follow docs/track_a/Visualization_Quickstart.md "
            "and provision the exact existing artifacts. No synthetic market data is displayed."
        )
        return
    if section == "HF20: TM0 vs T2":
        from lstm_data.visualization.hf20_ui import panel as hf20_panel

        try:
            hf20_panel(ROOT)
        except (ViewUnavailable, OSError, ValueError) as exc:
            st.warning(str(exc))
        return
    if section == "B1 Normalization (012B)":
        from lstm_data.visualization.nb1_ui import panel as nb1_panel

        try:
            nb1_panel(c, token)
        except ViewUnavailable as exc:
            st.warning(str(exc))
        return
    # Keep independent study and legacy filters when their widgets are off-page.
    keep = (
        ("fold", "partition", "model", "symbol", "dates", "origin_label")
        if (section == "Controlled Experiments")
        else tuple(k for k in st.session_state if str(k).startswith("study_"))
    )
    for key in keep:
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]
    if section == "Controlled Experiments":
        try:
            controlled_page(c, token)
        except ViewUnavailable as exc:
            st.warning(str(exc))
            st.caption("Affected study view unavailable; no fallback cohort or synthetic evidence.")
        return
    fold = st.sidebar.selectbox("Fold", ["WF2", "WF1"], key="fold", on_change=reset_dates)
    partitions = (*PARTITIONS, "Full data") if section == "Price & Features" else PARTITIONS
    if st.session_state.get("partition") == "Full data" and section != "Price & Features":
        st.session_state.partition = "Development"
    partition = st.sidebar.selectbox(
        "Partition", partitions, key="partition", on_change=reset_dates
    )
    if partition == "Full data":
        try:
            full_data_page(c, token)
        except ViewUnavailable as exc:
            st.warning(str(exc))
        return
    names = c.model_names(fold, partition)
    if st.session_state.get("model", "TM0") not in names:
        st.session_state.model = "TM0"
    model = st.sidebar.selectbox("Model", names, key="model")
    symbol = st.sidebar.selectbox("Stock", CANDIDATE, key="symbol")
    if "dates" not in st.session_state:
        st.session_state.dates = tuple(date.fromisoformat(d) for d in c.config["default_dates"])
    dates = st.sidebar.date_input(
        "Date range (ET, inclusive)",
        key="dates",
        min_value=date(2020, 7, 1),
        max_value=date(2024, 6, 30),
    )
    origin_label = st.sidebar.selectbox(
        "Forecast origins", ["Both", "10:30 ET", "11:30 ET"], key="origin_label"
    )
    origins = (1, 2) if origin_label == "Both" else (1,) if origin_label.startswith("10") else (2,)
    st.sidebar.info(
        "TM0 is C0 seed42. Package011 arms show their seed in brackets when recorded. "
        "WF1 also has MC1, E5 and recorded baselines."
    )
    if c.config.get("nb1_experiment"):
        packet = read_json(c.root, c.config["nb1_experiment"])
        st.sidebar.caption(
            f"Ledger{packet.get('global_started_pairs', 24)}/200 · "
            "production D1 unchanged · no confirmation access"
        )
    else:
        st.sidebar.caption("Ledger24/40 · production D1 unchanged · no confirmation access")
    st.caption(f"{symbol} / {fold} / {model} / {partition} · ASSUMPTION_CONDITIONAL")
    missing_files = c.missing_required(token)
    if missing_files:
        st.warning(
            f"{len(missing_files)} local artifacts are unavailable. Affected views will "
            "show an explanation; help and available views remain usable. Missing paths: "
            + "; ".join(missing_files[:3])
            + ". Run the launcher with --check for details."
        )
    if not isinstance(dates, tuple) or len(dates) != 2:
        st.info("Select both start and end dates.")
        return
    start, end = (d.isoformat() for d in dates)
    try:
        if section in ("Price & Features", "Predictions & Errors"):
            if partition == "Development":
                first, last = c.config["development_windows"][fold]
            else:
                recipes = c.config["recipes"][fold]
                full_recipe = read_json(c.root, recipes["refit"])
                first = (
                    read_json(c.root, recipes["inner"])["window"]["stop"]
                    if partition == "Inner validation"
                    else full_recipe["window"]["start"]
                )
                first = pd.Timestamp(first).tz_convert("America/New_York").date().isoformat()
                last = (
                    pd.Timestamp(full_recipe["window"]["stop"])
                    .tz_convert("America/New_York")
                    .date()
                    - timedelta(days=1)
                ).isoformat()
            if start < first or end > last:
                raise ViewUnavailable(
                    f"{fold} / {partition} covers {first} through {last}. "
                    "Choose dates there; use Refit training for earlier source/split inspection."
                )
        if section == "Start Here":
            start_here(c)
        elif section == "Price & Features":
            price_page(c, token, fold, model, partition, symbol, start, end, origins)
        elif section == "Predictions & Errors":
            predictions_page(c, token, fold, model, partition, symbol, start, end, origins)
        elif section == "Training Diagnostics":
            diagnostics_page(c, token, fold, model, start, end, origins)
        else:
            provenance_page(c, token)
    except ViewUnavailable as exc:
        st.info(str(exc))
        st.caption("Change the filters or see Start Here / the Quickstart troubleshooting guide.")
    except Exception as exc:
        logging.exception("Read-only dashboard view failed")
        st.error(
            f"This view could not load ({type(exc).__name__}). No research files were changed. "
            "See the local terminal log and Quickstart; other sections remain available."
        )
    st.caption(
        f"This page's server-side work: {time.monotonic() - t:.3f}s. "
        "Browser drawing time is not included. Local data caches invalidate on file changes."
    )


if __name__ == "__main__":
    main()
