"""P021 complete local research experience, isolated from both older studies."""

from __future__ import annotations

import json
import math
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..config import digest
from ..hf1m_action_audit import SYMBOLS
from ..hf1m_ft16_source import ORDER
from ..hf1m_training_authority import IDS
from ..hf1m_training_diagnostics import daily_metrics, grouped, summary
from .hf1m_long import CONFIG, ROLES, LongStudy, dates, role, select_events

SECTION = "HF1M Long — 20 stocks (2010–2025)"
VIEWS = (
    "Complete History / Candles & Volume",
    "Training Data / Targets & Extremes",
    "Training Diagnostics",
    "Predictions / Errors / Comparisons",
    "Feature / Source QA",
    "Guide",
)
MODES = (
    "Largest |TG20|",
    "Largest |numerator|",
    "Largest |return|",
    "Smallest raw MAD",
    "Smallest denominator",
    "Large numerator AND small MAD",
    "Training p99 exceedance",
)


def open_long() -> None:
    st.session_state.section = SECTION


@st.cache_resource(max_entries=1, show_spinner=False)
def study(root: str, token: str) -> LongStudy:
    return LongStudy.discover(Path(root))


@st.cache_data(max_entries=12, show_spinner=False)
def target_data(root: str, token: str, split: str) -> pd.DataFrame:
    role(split)
    return study(root, token).targets(split)


@st.cache_data(max_entries=12, show_spinner=False)
def history_data(root: str, token: str, ticker: str, start: str, end: str) -> pd.DataFrame:
    dates(start, end)
    return study(root, token).history(ticker, start, end)


@st.cache_data(max_entries=8, show_spinner=False)
def feature_data(
    root: str, token: str, ticker: str, start: str, end: str, fit: str, origin: int
) -> pd.DataFrame:
    dates(start, end)
    return study(root, token).features(ticker, start, end, fit, origin)


@st.cache_data(max_entries=12, show_spinner=False)
def prediction_data(root: str, token: str, run: str, split: str, result_token: str) -> pd.DataFrame:
    role(split)
    return study(root, token).prediction(run, split)


def plot(fig: go.Figure, key: str) -> None:
    st.plotly_chart(
        fig, width="stretch", key=key, config={"displaylogo": False, "scrollZoom": True}
    )


def candles(
    f: pd.DataFrame,
    key: str,
    entry: pd.Timestamp | None = None,
    exit_: pd.Timestamp | None = None,
    first: pd.Timestamp | None = None,
) -> None:
    if f.empty:
        st.info("No scheduled observations in this window.")
        return
    g = f.loc[~f.is_stub]
    fig = go.Figure(
        go.Candlestick(
            x=g.hour_end_utc,
            open=g.open,
            high=g.high,
            low=g.low,
            close=g.close,
            name="Approved split units · full hour",
            customdata=g.hour_id,
        )
    )
    unknown = g.loc[g.high.isna() | g.low.isna()]
    fig.add_trace(
        go.Scatter(
            x=unknown.hour_end_utc,
            y=unknown.close,
            mode="markers",
            name="Close only · unknown wick",
            marker=dict(symbol="x", color="orange"),
        )
    )
    stub = f.loc[f.is_stub]
    fig.add_trace(
        go.Scatter(
            x=stub.hour_end_utc,
            y=stub.close,
            mode="markers",
            name="Closing stub · not model hour",
            marker_symbol="diamond",
        )
    )
    proxy = g.loc[g.proxy_count.gt(0)]
    fig.add_trace(
        go.Scatter(
            x=proxy.hour_end_utc,
            y=proxy.close_input_cap5,
            mode="markers",
            name="Input proxy only",
            marker_symbol="circle-open",
        )
    )
    flagged = g.loc[g.quarantine_count.gt(0) | g.conflict_count.gt(0) | ~g.extrema_complete]
    fig.add_scatter(
        x=flagged.hour_end_utc,
        y=flagged.close,
        mode="markers",
        name="Quarantine / conflict / incomplete extrema",
        marker=dict(color="red", symbol="x"),
        customdata=flagged[["missing_count", "quarantine_count", "conflict_count", "proxy_count"]],
        hovertemplate=(
            "%{x}<br>missing=%{customdata[0]} quarantine=%{customdata[1]}"
            "<br>conflict=%{customdata[2]} proxy=%{customdata[3]}"
        ),
    )
    for _, boundary in g.loc[g.action_boundary].iterrows():
        fig.add_shape(
            type="line",
            x0=boundary.hour_end_utc,
            x1=boundary.hour_end_utc,
            y0=0,
            y1=1,
            yref="paper",
            line=dict(color="purple", dash="dot"),
        )
    missing = g.loc[g.close.isna()]
    fig.add_trace(
        go.Scatter(
            x=missing.hour_end_utc,
            y=[0] * len(missing),
            yaxis="y2",
            mode="markers",
            name="Missing scheduled close",
            marker_symbol="x",
        )
    )
    if entry is not None and exit_ is not None:
        fig.add_vrect(
            x0=first if first is not None else g.hour_end_utc.min(),
            x1=entry,
            fillcolor="blue",
            opacity=0.08,
            line_width=0,
        )
        fig.add_vrect(x0=entry, x1=exit_, fillcolor="orange", opacity=0.12, line_width=0)
        for t, label in ((entry, "origin"), (exit_, "future endpoint")):
            fig.add_shape(type="line", x0=t, x1=t, y0=0, y1=1, yref="paper", line_dash="dot")
            fig.add_annotation(x=t, y=1, yref="paper", text=label, showarrow=False)
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        yaxis_title="Approved split-adjusted price",
        yaxis2=dict(overlaying="y", visible=False, range=[-1, 1]),
        height=440,
        legend_orientation="h",
    )
    plot(fig, key + "_candles")
    volume = go.Figure()
    volume.add_bar(
        x=f.hour_end_utc, y=f.observed_volume, name="Observed share volume · as reported"
    )
    if "volume_for_feature" in f:
        volume.add_scatter(
            x=f.hour_end_utc,
            y=f.volume_for_feature,
            mode="markers",
            name="Feature lower bound · small absent gaps assume0",
        )
    volume.update_layout(
        yaxis_title="As-reported shares; no split share conversion",
        height=220,
        legend_orientation="h",
    )
    plot(volume, key + "_volume")
    st.caption(
        (
            "Candles are source observations, not fills. Missing wick stays "
            "unknown. Closing stubs are separate; feature volume remains a lower "
            "bound. UTC x-axis; ET shown in detail."
        )
    )


def feature_panel(
    s: LongStudy,
    ticker: str,
    start: str,
    end: str,
    fit: str,
    origin: int,
    key: str,
    first_step: int | None = None,
    last_step: int | None = None,
) -> None:
    names = st.multiselect(
        "FT16 channels", ORDER, default=["M1", "Q1", "Q2"], key=key + "_channels"
    )
    data = feature_data(str(s.root), s.token, ticker, start, end, fit, origin)
    if first_step is not None and last_step is not None:
        data = data.loc[data.step.between(first_step, last_step)]
    for column, title in (
        ("native", "Native causal feature · dimensionless"),
        ("model_scaled", "Model normalized · train-only recipe"),
    ):
        fig = go.Figure()
        for name in names:
            f = data.loc[data.feature.eq(name)]
            fig.add_scatter(
                x=f.hour_end_utc,
                y=f[column],
                name=name,
                mode="lines+markers",
                connectgaps=False,
                customdata=f[["fallback", "center", "scale"]],
                hovertemplate=(
                    "%{x}<br>value=%{y}<br>fallback=%{customdata[0]}<br>center=%{customdata[1]}"
                    " scale=%{customdata[2]}"
                ),
            )
        fig.update_layout(yaxis_title=title, height=280)
        plot(fig, key + "_" + column)
    dictionary = s.report_file("P020_FEATURE_DICTIONARY_AND_AUDIT.md").read_text()
    with st.expander("Actual16 formulas, causal history and availability policy"):
        st.markdown(dictionary)
    with st.expander(
        "Every displayed native, fallback, normalization coefficient and quality reason"
    ):
        st.dataframe(data.loc[data.feature.isin(names)], hide_index=True, width="stretch")
    if not data.empty:
        step = st.selectbox(
            "Inspect exact feature step (UTC)",
            sorted(data.hour_end_utc.unique()),
            key=key + "_step",
        )
        if step is None:
            return
        chosen = data.loc[data.hour_end_utc.eq(step)]
        st.dataframe(
            chosen[
                [
                    "feature",
                    "native",
                    "fallback",
                    "fallback_value",
                    "filled",
                    "center",
                    "scale",
                    "model_scaled",
                    "method",
                    "identity",
                ]
            ],
            hide_index=True,
            width="stretch",
            column_config={
                name: st.column_config.NumberColumn(format="%.16g")
                for name in (
                    "native",
                    "fallback_value",
                    "filled",
                    "center",
                    "scale",
                    "model_scaled",
                )
            },
        )
        with st.expander("Actual stock-specific floors and share-regime pseudocounts"):
            st.json(next(f for f in s.recipe(fit)["floors"] if f["symbol"] == ticker))
        if st.button("Reconstruct source operands at this step", key=key + "_operands"):
            expected, operands = s.feature_operands(ticker, int(chosen.step.iloc[0]), fit, origin)
            st.dataframe(
                pd.DataFrame(
                    {"operand": list(operands), "value": [str(v) for v in operands.values()]}
                ),
                hide_index=True,
            )
            reconcile = chosen[["feature", "native", "fallback", "model_scaled"]].copy()
            reconcile["independent_formula_value"] = reconcile.feature.map(expected)
            reconcile["reconstruction_difference"] = (
                reconcile.native - reconcile.independent_formula_value
            )
            st.dataframe(reconcile, hide_index=True, width="stretch")
            st.caption(
                "Source-quality, basis and COP masks remain authoritative. "
                "A computable scalar formula does not override a saved unavailable "
                "native value or admit a forecast origin."
            )


def history_page(s: LongStudy) -> None:
    st.write(
        (
            "Choose any stock and window in the permitted history. Jump controls "
            "keep the display bounded; every permitted month is available."
        )
    )
    ticker = st.selectbox("History stock", SYMBOLS, key="hf1m_history_stock")
    if "hf1m_history_dates" not in st.session_state:
        st.session_state.hf1m_history_dates = (date(2020, 3, 2), date(2020, 3, 13))
    anchor = st.date_input(
        "Jump to day / week / month",
        date(2010, 7, 1),
        min_value=date(2010, 7, 1),
        max_value=date(2025, 12, 31),
        key="hf1m_jump_day",
    )
    span = st.selectbox("Jump window", ("Day", "Week", "Month"), index=1, key="hf1m_jump_span")
    if st.button("Apply history jump"):
        length = {"Day": 0, "Week": 6, "Month": 30}[span]
        st.session_state.hf1m_history_dates = (
            anchor,
            min(anchor + timedelta(days=length), date(2025, 12, 31)),
        )
    selected = st.date_input(
        "History dates (ET)",
        key="hf1m_history_dates",
        min_value=date(2010, 7, 1),
        max_value=date(2025, 12, 31),
    )
    if not isinstance(selected, tuple) or len(selected) != 2:
        st.info("Choose start and end dates.")
        return
    start, end = map(str, selected)
    dates(start, end)
    f = history_data(str(s.root), s.token, ticker, start, end)
    selected_origin = st.session_state.get("hf1m_history_origin_id")
    if selected_origin:
        origins = s.table("origins")
        matching = origins.loc[
            origins.origin_id.eq(selected_origin) & origins.session_date_et.between(start, end)
        ]
        if not matching.empty:
            current = matching.iloc[0]
            grid = s.table("grid")
            candles(
                f,
                "hf1m_history",
                pd.Timestamp(current.entry_end_utc),
                pd.Timestamp(current.exit_end_utc),
                pd.Timestamp(grid.hour_end_utc.iloc[int(current.first_step)]),
            )
        else:
            candles(f, "hf1m_history")
    else:
        candles(f, "hf1m_history")
    if not f.empty:
        chosen = st.selectbox(
            "Candle numeric detail · exact source hour", f.hour_id, key="hf1m_candle_detail"
        )
        row = f.loc[f.hour_id.eq(chosen)].copy()
        row["end_ET"] = row.hour_end_utc.dt.tz_convert("America/New_York").astype(str)
        for field in ("open", "high", "low", "close"):
            row["as_reported_units_" + field] = row[field] / row.price_factor
        st.dataframe(row.T.rename(columns={row.index[0]: "value"}), width="stretch")
        with st.expander("All scheduled hours and source-quality flags in this window"):
            st.dataframe(f, hide_index=True, width="stretch")
    fit = st.selectbox("Feature recipe", ("inner", "refit"), index=1, key="hf1m_history_fit")
    origin = st.selectbox("Historical M2 forecast context", (1, 2), key="hf1m_history_context")
    feature_panel(s, ticker, start, end, fit, origin, "hf1m_history_feature")
    st.caption(
        (
            "Warmup and non-admitted hours may have unavailable native features. "
            "Saved train-only fallback values do not make them eligible forecast "
            "origins."
        )
    )


def event_detail(s: LongStudy, all_targets: pd.DataFrame, row: pd.Series, split: str) -> None:
    ticker = str(row.ticker)
    version = role(split)
    entry = pd.Timestamp(row.entry_end_utc)
    exit_ = pd.Timestamp(row.exit_end_utc)
    origins = s.table("origins")
    origin = origins.loc[origins.origin_id.eq(row.origin_id)].iloc[0]
    grid = s.table("grid")
    first = pd.Timestamp(grid.hour_end_utc.iloc[int(origin.first_step)])
    start = str(first.tz_convert("America/New_York").date())
    end = str(exit_.tz_convert("America/New_York").date())
    hours = history_data(str(s.root), s.token, ticker, start, end)
    a = hours.loc[hours.hour_end_utc.eq(entry)].iloc[0]
    b = hours.loc[hours.hour_end_utc.eq(exit_)].iloc[0]
    recipe = s.recipe(version)
    scale = recipe["t2_scale"]
    reconstructed = scale * np.sinh(float(row.T2_z))
    operands = dict(
        ticker=ticker,
        origin_id=row.origin_id,
        role=ROLES[split],
        fit_version=version,
        entry_UTC=str(entry),
        entry_ET=str(entry.tz_convert("America/New_York")),
        exit_UTC=str(exit_),
        exit_ET=str(exit_.tz_convert("America/New_York")),
        issuance_UTC=str(origin.issuance_utc),
        maturity_UTC=str(row.label_maturity_utc),
        genuine_entry_price=float(a.close),
        genuine_exit_price=float(b.close),
        genuine_entry=bool(a.genuine_close),
        genuine_exit=bool(b.genuine_close),
        entry_source_hour=a.hour_id,
        exit_source_hour=b.hour_id,
        entry_price_factor=float(a.price_factor),
        exit_price_factor=float(b.price_factor),
        return_from_prices=float(np.log(b.close / a.close)),
        r=float(row.return_4h),
        m=float(row.cross_section_median),
        signed_numerator=float(row.numerator),
        absolute_numerator=abs(float(row.numerator)),
        raw_MAD=float(row.cross_section_mad),
        epsilon=float(row.epsilon),
        denominator=float(row.denominator),
        TG20=float(row.TG20),
        s=float(scale),
        z=float(row.T2_z),
        inverse_reconstruction_error=float(reconstructed - row.TG20),
        tail_class=row.tail_class,
        entry_anomaly_flags=str(a.anomaly_event_ids),
        exit_anomaly_flags=str(b.anomaly_event_ids),
        epsilon_inner=s.recipe("inner")["epsilon"],
        epsilon_refit=s.recipe("refit")["epsilon"],
        scale_inner=s.recipe("inner")["t2_scale"],
        scale_refit=s.recipe("refit")["t2_scale"],
    )
    st.subheader(f"{ticker} · {row.origin_id}")
    st.caption(ROLES[split] + " · extreme chosen ex post; future returns were labels only")
    st.code(
        (
            "r=log(Pexit/Pentry); m=median20(r); n=r−m; MAD=median20(|r−m|)\n"
            "TG20=n/(MAD+epsilon_fit); z=asinh(TG20/s_fit); inverse=s_fit*sinh(z)"
        )
    )
    st.dataframe(
        pd.DataFrame({"operand": list(operands), "value": [str(v) for v in operands.values()]}),
        hide_index=True,
        width="stretch",
    )
    with st.expander(
        "All20 future returns, contemporaneous median and target operands", expanded=True
    ):
        st.dataframe(
            all_targets.loc[
                all_targets.origin_id.eq(row.origin_id),
                [
                    "ticker",
                    "return_4h",
                    "cross_section_median",
                    "numerator",
                    "cross_section_mad",
                    "epsilon",
                    "denominator",
                    "TG20",
                    "T2_z",
                    "tail_class",
                ],
            ],
            hide_index=True,
            width="stretch",
            column_config={
                name: st.column_config.NumberColumn(format="%.16g")
                for name in (
                    "return_4h",
                    "cross_section_median",
                    "numerator",
                    "cross_section_mad",
                    "epsilon",
                    "denominator",
                    "TG20",
                    "T2_z",
                )
            },
        )
    comparisons = []
    for run in IDS:
        try:
            r = s.run_result(run)
            p = prediction_data(
                str(s.root), s.token, run, split, digest(s.root / r["epochs"]["path"])
            )
            e = p.loc[p.origin_id.eq(row.origin_id) & p.ticker.eq(ticker)]
            if len(e) == 1:
                comparisons.append(
                    e[
                        [
                            "run_id",
                            "seed",
                            "arm",
                            "phase",
                            "partition",
                            "checkpoint_sha256",
                            "actual_TG20",
                            "pred_original_TG20",
                            "raw_net_output",
                            "raw_output_units",
                            "error",
                        ]
                    ]
                )
        except (ValueError, OSError) as error:
            st.caption(str(error))
    if comparisons:
        st.dataframe(pd.concat(comparisons, ignore_index=True), hide_index=True, width="stretch")
    candles(hours, "hf1m_event", entry, exit_, first)

    def jump_to_history() -> None:
        st.session_state.hf1m_history_stock = ticker
        st.session_state.hf1m_history_dates = (date.fromisoformat(start), date.fromisoformat(end))
        st.session_state.hf1m_view = VIEWS[0]
        st.session_state.hf1m_history_origin_id = str(row.origin_id)
        st.session_state.hf1m_history_fit = version
        st.session_state.hf1m_history_context = entry.tz_convert("America/New_York").hour - 9

    st.button("Open this event in Complete History", on_click=jump_to_history)
    features = feature_data(
        str(s.root),
        s.token,
        ticker,
        start,
        end,
        version,
        entry.tz_convert("America/New_York").hour - 9,
    )
    window = features.loc[features.step.between(int(origin.first_step), int(origin.entry_index))]
    st.write(
        "Exact48 scheduled inputs ×16 channels; the outcome interval is excluded from this matrix."
    )
    st.dataframe(
        window.pivot(index="hour_end_utc", columns="feature", values="model_scaled").reindex(
            columns=ORDER
        ),
        width="stretch",
    )
    with st.expander("48×16 native values, coefficients, fallbacks and source quality"):
        st.dataframe(window, hide_index=True, width="stretch")
    feature_panel(
        s,
        ticker,
        start,
        end,
        version,
        entry.tz_convert("America/New_York").hour - 9,
        "hf1m_event_feature",
        int(origin.first_step),
        int(origin.entry_index),
    )


def targets_page(s: LongStudy) -> None:
    split = st.selectbox(
        "Target role", tuple(ROLES), index=2, format_func=lambda x: ROLES[x], key="hf1m_target_role"
    )
    role(split)
    st.caption(
        ROLES[split]
        + ". Thresholds come from the corresponding training prefix, not the displayed date window."
    )
    all_targets = target_data(str(s.root), s.token, split)
    ticker = st.selectbox("Target stock", ("All", *SYMBOLS), key="hf1m_target_stock")
    mode = st.selectbox("Event sort / selection", MODES, key="hf1m_event_mode")
    search = st.text_input(
        "Search all eligible rows · ticker, exact origin or date", key="hf1m_event_search"
    )
    interval = st.date_input(
        "Target date filter (ET)",
        value=(
            date.fromisoformat(all_targets.session_date_et.min()),
            date.fromisoformat(all_targets.session_date_et.max()),
        ),
        min_value=date(2010, 7, 1),
        max_value=date(2025, 12, 31),
        key="hf1m_target_dates_" + split,
    )
    if len(interval) != 2:
        return
    start, end = map(str, interval)
    dates(start, end)
    tail = st.selectbox(
        "Numerator / denominator group",
        ("All", "large numerator", "small MAD", "both", "neither"),
        key="hf1m_tail_group",
    )
    sign = st.selectbox("Target sign", ("Both", "Positive", "Negative"), key="hf1m_target_sign")
    quality = st.selectbox(
        "All-name input-context quality",
        (
            "All",
            "No input proxies",
            "Some input proxies",
            "No assumed-zero volume minutes",
            "Some assumed-zero volume minutes",
            "No poor-volume hours",
            "Some poor-volume hours",
        ),
        key="hf1m_target_quality",
    )
    quality_columns = {
        "input proxies": "price_proxy_minute_count",
        "assumed-zero volume minutes": "assumed_zero_minute_count",
        "poor-volume hours": "poor_volume_hour_count",
    }
    qualified = all_targets
    if quality != "All":
        category = quality.split(" ", 1)[1]
        values = all_targets[quality_columns[category]]
        qualified = all_targets.loc[values.eq(0) if quality.startswith("No ") else values.gt(0)]
    f = select_events(qualified, mode, ticker, search, start, end, tail, sign)
    st.write(
        f"Full role: {len(all_targets):,} stock rows / "
        f"{all_targets.origin_id.nunique():,} origins. Filtered selection: {len(f):,} rows. "
        "Filters and sorting run before pagination."
    )
    st.caption(
        (
            "Large numerator=|n|≥training p95; small MAD=origin MAD≤training p05;"
            " p99=|TG20|≥training p99. Small-MAD sorts deduplicate origins before"
            " pagination."
        )
    )
    st.dataframe(
        all_targets.groupby("tail_class", as_index=False).agg(
            stock_rows=("ticker", "size"), origins=("origin_id", "nunique")
        ),
        hide_index=True,
    )
    if f.empty:
        st.info("No matching eligible rows.")
        return
    counts, edges = np.histogram(f.TG20, bins=60)
    plot(
        go.Figure(go.Bar(x=(edges[:-1] + edges[1:]) / 2, y=counts)).update_layout(
            xaxis_title="Original TG20", yaxis_title="Filtered stock rows"
        ),
        "hf1m_target_hist",
    )
    heat, xedges, yedges = np.histogram2d(f.numerator.abs(), f.denominator, bins=45)
    plot(
        go.Figure(
            go.Heatmap(x=(xedges[:-1] + xedges[1:]) / 2, y=(yedges[:-1] + yedges[1:]) / 2, z=heat.T)
        ).update_layout(
            xaxis_title="|Numerator|", yaxis_title="MAD+epsilon · full-population density"
        ),
        "hf1m_num_mad",
    )
    concentration = f.assign(target_square=f.TG20**2).sort_values("target_square", ascending=False)
    denom = concentration.target_square.sum()
    plot(
        go.Figure(
            go.Scatter(
                x=np.arange(1, len(concentration) + 1) / len(concentration),
                y=concentration.target_square.cumsum() / denom
                if denom
                else np.zeros(len(concentration)),
            )
        ).update_layout(
            xaxis_title="Fraction of selected stock rows · largest first",
            yaxis_title="Cumulative target-square share",
        ),
        "hf1m_target_concentration",
    )
    pages = math.ceil(len(f) / 50)
    if st.session_state.get("hf1m_target_page", 1) > pages:
        st.session_state.hf1m_target_page = 1
    page = int(
        st.number_input(
            "Result page ·50 rows",
            min_value=1,
            max_value=pages,
            value=1,
            step=1,
            key="hf1m_target_page",
        )
    )
    part = f.iloc[(page - 1) * 50 : page * 50]
    st.dataframe(
        part[
            [
                "ticker",
                "origin_id",
                "session_date_et",
                "TG20",
                "return_4h",
                "numerator",
                "cross_section_mad",
                "epsilon",
                "denominator",
                "tail_class",
            ]
        ],
        hide_index=True,
        width="stretch",
    )
    keys: list[str] = (part.ticker + "|" + part.origin_id).tolist()
    selected = st.session_state.get("hf1m_selected_event")
    if isinstance(selected, str) and selected not in keys:
        stock, origin = selected.split("|", 1)
        if ((f.ticker == stock) & (f.origin_id == origin)).any():
            keys.append(selected)
    selected = st.selectbox(
        "Event detail · durable ticker | origin", keys, key="hf1m_selected_event"
    )
    if selected is None:
        return
    stock, origin = selected.split("|", 1)
    row = all_targets.loc[all_targets.ticker.eq(stock) & all_targets.origin_id.eq(origin)].iloc[0]
    event_detail(s, all_targets, row, split)


def training_page(s: LongStudy) -> None:
    st.caption(
        (
            "C0 objective is TG20 squared; T2 objective is z squared. Compare "
            "original-scale losses across arms. Selected epoch, raw best and stop"
            " epoch are separate."
        )
    )
    chosen = st.multiselect("Training runs", IDS, default=list(IDS), key="hf1m_training_runs")
    tables = []
    for run in chosen:
        try:
            result = s.run_result(run)
            if result.get("telemetry_limitation"):
                st.warning(result["telemetry_limitation"])
            path = s.root / result["epochs"]["path"]
            if digest(path) != result["epochs"]["sha256"]:
                raise ValueError("HF1M epoch file changed")
            f = pd.read_csv(path)
            f["run_id"] = run
            f["arm"] = result["arm"]
            f["seed"] = result["seed"]
            tables.append(f)
            st.write(run)
            st.json(
                {
                    k: result[k]
                    for k in (
                        "selector",
                        "calibration_epochs",
                        "refit_epochs",
                        "calibration_steps",
                        "refit_steps",
                        "fresh_optimizer_state_empty",
                        "device",
                        "elapsed_seconds",
                    )
                }
            )
        except (ValueError, OSError) as error:
            st.error(str(error))
    if not tables:
        return
    all_epochs = pd.concat(tables, ignore_index=True)
    for phase in ("calibration", "refit"):
        st.subheader(phase.title())
        for field in (
            "original_mse",
            "validation_mse",
            "preclip_p50",
            "preclip_p90",
            "preclip_p99",
            "preclip_max",
            "clipped_fraction",
        ):
            if field not in all_epochs:
                continue
            fig = go.Figure()
            for run, f in all_epochs.loc[all_epochs.phase.eq(phase)].groupby("run_id"):
                fig.add_scatter(x=f.epoch, y=f[field], name=run, mode="lines+markers")
            if field.startswith("preclip"):
                fig.add_hline(y=1, line_dash="dot", annotation_text="clip cap1")
            plot(
                fig.update_layout(
                    xaxis_title="All actual epochs, including after selected checkpoint",
                    yaxis_title=field,
                ),
                "hf1m_" + phase + field,
            )
        for arm in ("C0", "T2"):
            fig = go.Figure()
            for run, f in all_epochs.loc[
                all_epochs.phase.eq(phase) & all_epochs.arm.eq(arm)
            ].groupby("run_id"):
                fig.add_scatter(x=f.epoch, y=f.objective, name=run, mode="lines+markers")
            plot(
                fig.update_layout(
                    yaxis_title=arm
                    + " objective · "
                    + ("z squared" if arm == "T2" else "TG20 squared")
                ),
                "hf1m_objective_" + phase + arm,
            )
    st.dataframe(all_epochs, hide_index=True, width="stretch")


def predictions_page(s: LongStudy) -> None:
    st.caption(
        "Cross-study context: five-stock Alpaca FT0/TG0 and former Twelve Data HF20 "
        "FT1/TG20 have different sources, dates, universes and feature/target versions. "
        "The controlled comparisons here are within HF1M-LONG FT16/TG20 only."
    )
    split = st.selectbox(
        "Prediction role",
        tuple(ROLES),
        index=3,
        format_func=lambda x: ROLES[x],
        key="hf1m_prediction_role",
    )
    st.caption(
        ROLES[split]
        + (
            ". ZERO rank IC is undefined; a horizontal0 line is a reference only."
            " No source-audited trading engine exists for this exact protocol; no"
            " P&L is inferred."
        )
    )
    frames = []
    metrics = []
    for run in IDS:
        try:
            r = s.run_result(run)
            f = prediction_data(
                str(s.root),
                s.token,
                run,
                split,
                r["artifacts"][split + "_predictions.parquet"]["sha256"],
            )
            frames.append(f)
            metrics.append(dict(run_id=run, **summary(f)))
        except (ValueError, OSError) as error:
            st.error(str(error))
    if not frames:
        return
    st.dataframe(pd.DataFrame(metrics), hide_index=True, width="stretch")
    try:
        saved = s.diagnostic("metrics.csv")
        st.dataframe(saved.loc[saved.partition.eq(split)], hide_index=True, width="stretch")
        comparisons = s.diagnostic("paired_comparisons.csv")
        st.dataframe(
            comparisons.loc[comparisons.partition.eq(split)], hide_index=True, width="stretch"
        )
    except (OSError, ValueError) as error:
        st.info("Full saved diagnostic publication pending: " + str(error))
    fig = go.Figure()
    ic_months = []
    for f in frames:
        try:
            d = s.diagnostic(str(f.run_id.iloc[0]) + "_" + split + "_daily.parquet")
        except (OSError, ValueError):
            d = daily_metrics(f)
        fig.add_scatter(x=d.session_date_et, y=d.rank_ic, name=f.run_id.iloc[0], mode="lines")
        monthly = d.assign(month=d.session_date_et.str[:7]).groupby("month").rank_ic.mean()
        ic_months.extend(
            dict(run_id=f.run_id.iloc[0], month=month, rank_ic=value)
            for month, value in monthly.items()
        )
        valid = d.rank_ic.dropna()
        st.write(
            dict(
                run_id=f.run_id.iloc[0],
                daily_ic_mean=float(valid.mean()),
                daily_ic_median=float(valid.median()),
                positive_fraction=float(valid.gt(0).mean()),
                eligible_days=len(d),
                defined_ic_days=len(valid),
            )
        )
    fig.add_hline(y=0, line_dash="dot", annotation_text="Reference0 · ZERO IC undefined")
    heat = pd.DataFrame(ic_months).pivot(index="run_id", columns="month", values="rank_ic")
    left, right = st.columns((2, 1))
    with left:
        plot(fig.update_layout(yaxis_title="Daily mean of20-stock origin Spearman IC"), "hf1m_ic")
    with right:
        plot(
            go.Figure(
                go.Heatmap(
                    x=heat.columns, y=heat.index, z=heat.to_numpy(), zmid=0, colorscale="RdBu"
                )
            ).update_layout(xaxis_title="Month", yaxis_title="Run", title="Mean daily rank IC"),
            "hf1m_ic_heatmap",
        )
    run = st.selectbox(
        "Inspect prediction run", [f.run_id.iloc[0] for f in frames], key="hf1m_pred_run"
    )
    f = next(f for f in frames if f.run_id.iloc[0] == run).copy()
    source = target_data(str(s.root), s.token, split)
    f = f.merge(
        source[
            [
                "origin_id",
                "ticker",
                "tail_class",
                "target_p99",
                "assumed_zero_minute_count",
                "price_proxy_minute_count",
            ]
        ],
        on=["origin_id", "ticker"],
        validate="one_to_one",
    )
    ticker = st.selectbox("Prediction stock", ("All", *SYMBOLS), key="hf1m_pred_stock")
    interval = st.date_input(
        "Prediction date filter (ET)",
        value=(
            date.fromisoformat(f.session_date_et.min()),
            date.fromisoformat(f.session_date_et.max()),
        ),
        min_value=date(2010, 7, 1),
        max_value=date(2025, 12, 31),
        key="hf1m_pred_dates_" + split,
    )
    if len(interval) != 2:
        return
    dates(str(interval[0]), str(interval[1]))
    filtered = f.loc[f.session_date_et.between(str(interval[0]), str(interval[1]))]
    if ticker != "All":
        filtered = filtered.loc[filtered.ticker.eq(ticker)]
    st.write("Filtered population (separately reweighted):", summary(filtered))
    matched_frames = []
    for candidate in frames:
        current = candidate.loc[
            candidate.session_date_et.between(str(interval[0]), str(interval[1]))
        ]
        if ticker != "All":
            current = current.loc[current.ticker.eq(ticker)]
        matched_frames.append(current)
    st.write("Matched four-run comparison on this exact stock/date window:")
    st.dataframe(
        pd.DataFrame(
            [
                dict(run_id=d.run_id.iloc[0] if len(d) else frames[i].run_id.iloc[0], **summary(d))
                for i, d in enumerate(matched_frames)
            ]
        ),
        hide_index=True,
        width="stretch",
    )
    if filtered.empty:
        st.info("No admitted origins in this stock/date window.")
        return
    detail_options = list(SYMBOLS) if ticker == "All" else [ticker]
    detail_stock = st.selectbox(
        "Forecast detail stock",
        detail_options,
        index=detail_options.index("AAPL") if "AAPL" in detail_options else 0,
        key="hf1m_forecast_detail_stock",
    )
    detail = filtered.loc[filtered.ticker.eq(detail_stock)].sort_values("entry_end_utc")
    forecast = go.Figure(
        go.Scatter(
            x=detail.entry_end_utc,
            y=detail.actual_TG20,
            mode="lines+markers",
            name="Actual TG20",
            line=dict(color="black"),
        )
    )
    for candidate in matched_frames:
        current = candidate.loc[candidate.ticker.eq(detail_stock)].sort_values("entry_end_utc")
        forecast.add_scatter(
            x=current.entry_end_utc,
            y=current.pred_original_TG20,
            mode="lines+markers",
            name=str(current.run_id.iloc[0]),
            connectgaps=False,
        )
    plot(
        forecast.update_layout(
            xaxis_title="Forecast origin UTC · " + ROLES[split],
            yaxis_title="Original TG20 · " + str(detail_stock),
        ),
        "hf1m_forecast_timeseries",
    )
    residual = go.Figure(
        go.Scatter(
            x=detail.entry_end_utc,
            y=detail.error,
            mode="lines+markers",
            name="Prediction − actual TG20",
            marker_color=np.where(detail.error.ge(0), "red", "blue"),
        )
    )
    residual.add_hline(y=0, line_dash="dot")
    plot(
        residual.update_layout(
            xaxis_title="Forecast origin UTC", yaxis_title="Signed residual · " + str(run)
        ),
        "hf1m_residual_timeseries",
    )
    scatter = go.Figure(
        go.Scattergl(
            x=detail.actual_TG20,
            y=detail.pred_original_TG20,
            mode="markers",
            name="Saved forecast",
            customdata=detail[["origin_id", "session_date_et"]],
            hovertemplate="%{customdata[0]}<br>actual=%{x}<br>forecast=%{y}",
        )
    )
    low = float(min(detail.actual_TG20.min(), detail.pred_original_TG20.min()))
    high = float(max(detail.actual_TG20.max(), detail.pred_original_TG20.max()))
    scatter.add_scatter(
        x=[low, high], y=[low, high], mode="lines", name="Identity · prediction=actual"
    )
    plot(
        scatter.update_layout(xaxis_title="Actual TG20", yaxis_title="Predicted original TG20"),
        "hf1m_prediction_identity_scatter",
    )
    binned = filtered.copy()
    binned["target_magnitude_bin"] = pd.cut(
        binned.actual_TG20.abs(),
        bins=[0, 0.5, 1, 2, 4, 8, np.inf],
        labels=["0–0.5", "0.5–1", "1–2", "2–4", "4–8", ">8"],
        include_lowest=True,
    ).astype(str)
    bin_metrics = grouped(binned, "target_magnitude_bin")
    st.write("MSE by fixed diagnostic |TG20| bins · filtered window, separately reweighted:")
    st.dataframe(bin_metrics, hide_index=True, width="stretch")
    bin_plot = go.Figure(go.Bar(x=bin_metrics.group, y=bin_metrics.mse, name="Model MSE"))
    bin_plot.add_bar(x=bin_metrics.group, y=bin_metrics.zero_mse, name="Matched ZERO MSE")
    plot(
        bin_plot.update_layout(
            barmode="group", xaxis_title="|TG20| bin", yaxis_title="Original TG20 MSE"
        ),
        "hf1m_mse_by_target_bin",
    )
    st.caption(
        "Time series and scatter use one detail stock; the matched comparison and "
        "bin table use the selected stock/date population. Full-role group summaries follow."
    )
    f["month"] = f.session_date_et.str[:7]
    f["year"] = f.session_date_et.str[:4]
    f["volume_quality"] = np.where(
        f.assumed_zero_minute_count.gt(0), "some feature assumed0 minutes", "no assumed0 minutes"
    )
    for group in ("ticker", "month", "year", "tail_class", "volume_quality"):
        with st.expander("Original-scale errors by " + group):
            st.dataframe(grouped(f, group), hide_index=True, width="stretch")
    plot(
        go.Figure(go.Histogram(x=filtered.pred_original_TG20, name="prediction", opacity=0.6))
        .add_histogram(x=filtered.actual_TG20, name="actual", opacity=0.6)
        .update_layout(barmode="overlay", xaxis_title="Original TG20"),
        "hf1m_prediction_hist",
    )
    worst = filtered.sort_values("squared_error", ascending=False)
    pages = max(1, math.ceil(len(worst) / 50))
    if st.session_state.get("hf1m_error_page", 1) > pages:
        st.session_state.hf1m_error_page = 1
    page = int(
        st.number_input(
            "Error result page ·50 rows",
            min_value=1,
            max_value=pages,
            value=1,
            key="hf1m_error_page",
        )
    )
    st.dataframe(worst.iloc[(page - 1) * 50 : page * 50], hide_index=True, width="stretch")
    st.caption(
        (
            "All four comparisons are exploratory: C0/T2 within seed42 and123; "
            "seed42/123 within C0 and T2. Two seeds do not establish "
            "significance. Legacy cohorts and losses are never pooled."
        )
    )


def qa_page(s: LongStudy) -> None:
    st.write(
        (
            "Reported source rights are private research permission, not "
            "independent licensing certification. Split-adjusted price units do "
            "not imply adjusted share volumes or certified publication timing."
        )
    )
    names = (
        "origin_attrition_waterfall.csv",
        "admitted_feature_fallback_rates.csv",
        "feature_missingness_stock_year.csv",
        "volume_quality_stock_year.csv",
        "source_channel_reason_rates_stock_year.csv",
        "training_input_target_correlation_diagnostic.csv",
    )
    ticker = st.selectbox("QA stock", ("All", *SYMBOLS), key="hf1m_qa_stock")
    candles = s.table("candles_quality")
    provenance = s.table("P020_hour_provenance_overlay.parquet")
    audit = candles.merge(
        provenance[["hour_id", "terminal_input_price_age_minutes"]],
        on="hour_id",
        validate="one_to_one",
    )
    if ticker != "All":
        audit = audit.loc[audit.ticker.eq(ticker)]
    audit["year"] = audit.session_date_et.str[:4]
    audit["incomplete_volume"] = audit.hourly_volume_lower_bound.astype(bool)
    age = audit.groupby(["ticker", "year"], as_index=False).agg(
        scheduled_full_hours=("hour_id", "size"),
        genuine_close_hours=("genuine_close", "sum"),
        missing_minutes=("missing_count", "sum"),
        expected_minutes=("expected_minutes", "sum"),
        input_proxy_minutes=("proxy_count", "sum"),
        quarantined_minutes=("quarantine_count", "sum"),
        incomplete_volume_fraction=("incomplete_volume", "mean"),
        assumed_zero_minutes=("assumed_zero_missing_count", "sum"),
        terminal_input_age_max_minutes=("terminal_input_price_age_minutes", "max"),
        terminal_input_age_p95_minutes=(
            "terminal_input_price_age_minutes",
            lambda x: x.quantile(0.95),
        ),
    )
    age["missing_minute_fraction"] = age.missing_minutes / age.expected_minutes
    st.write("Actual source quality and terminal input-price ages by stock/year:")
    st.dataframe(age, hide_index=True, width="stretch")
    for name in names:
        with st.expander(name, expanded=name == "admitted_feature_fallback_rates.csv"):
            f = pd.read_csv(s.report_file(name))
            if ticker != "All" and "ticker" in f:
                f = f.loc[f.ticker.eq(ticker)]
            st.dataframe(f, hide_index=True, width="stretch")
    st.caption(
        (
            "Saved training correlations are descriptive, not importance "
            "estimates or new fits. Q1/Q2 fallbacks are measured, never quiet "
            "constants; fallback cannot repair a banned price context."
        )
    )
    with st.expander("Action, quarantine, COP and original source-quality register"):
        st.markdown((s.root / "UNRESOLVED_MARKET_DATA_ANOMALIES.md").read_text())


def guide_page(s: LongStudy) -> None:
    st.markdown("""Take5–10 minutes to follow one real training event through its inputs and target.

1. Open **Training Data / Targets & Extremes**, default **Full-prefix refit training**.
2. Select **Largest |numerator|**. Record the displayed stock and origin; open its numeric detail.
3. Select **Smallest raw MAD**. This ranks each origin once; inspect all20 returns underneath.
4. Compare the genuine entry/exit prices, r, median m, signed numerator n, raw MAD, epsilon and
   TG20.
   The target uses contemporaneous cross-sectional MAD, not historical volatility. There is no
 invented MST channel.
5. Open **Complete History** from the event. Browse any of20 stocks; jump to any permitted month.
   Inspect candles/volume and **M1**, **Q1**, **Q2** native versus normalized traces. M1 is the
 completed-hour log return divided by its frozen RMS floor, not the target median.
6. Return to the event's exact **48×16** input matrix and quality flags. Orange future shading
   is outcome information excluded from those inputs.
7. Open **Training Diagnostics**, select both seeds and arms. Compare original TG20 losses,
   selected versus raw-best/stop epochs and preclip norms. C0 and T2 objective scales differ.
8. Open **Predictions / Errors / Comparisons**, choose **Exploratory development**. Compare each
   run with matched ZERO and the exact p²−2yp decomposition, then inspect the largest miss.

Forward target transformation is **asinh(TG20/s)**. **sinh** is its inverse, applied once to
 predictions before original-scale comparison. Feature **T2** is a different bounded FT16
 channel.

Training is14years3months with nine months of startup. Inner validation selects checkpoints;
 refit training includes those historical dates. Development is exploratory and post-fit.
 Protected2026 numerical data are unavailable everywhere.
""")
    examples = target_data(str(s.root), s.token, "refit")
    records = []
    for mode in ("Largest |numerator|", "Smallest raw MAD", "Largest |TG20|"):
        e = select_events(examples, mode).iloc[0]
        records.append(
            dict(
                selection=mode,
                ticker=e.ticker,
                origin_id=e.origin_id,
                TG20=e.TG20,
                numerator=e.numerator,
                MAD=e.cross_section_mad,
            )
        )
    try:
        forecast = s.prediction(IDS[0], "development")
        worst = forecast.sort_values("squared_error", ascending=False).iloc[0]
        target = target_data(str(s.root), s.token, "development")
        event = target.loc[
            target.origin_id.eq(worst.origin_id) & target.ticker.eq(worst.ticker)
        ].iloc[0]
        records.append(
            dict(
                selection="C0/42 development largest error",
                ticker=worst.ticker,
                origin_id=worst.origin_id,
                TG20=event.TG20,
                numerator=event.numerator,
                MAD=event.cross_section_mad,
            )
        )
    except (OSError, ValueError) as error:
        st.caption(str(error))
    st.write("Genuine examples from the labeled training and development populations:")
    st.dataframe(pd.DataFrame(records), hide_index=True, width="stretch")


def panel(root: Path) -> None:
    # URL and restored widget state must be checked before discovery, filesystem or caches.
    for key in ("start", "end", "date"):
        value = st.query_params.get(key)
        if value:
            dates(str(value), str(value))
    queried_role = st.query_params.get("role")
    if queried_role:
        role(str(queried_role))
    for key, value in tuple(st.session_state.items()):
        if str(key).startswith("hf1m_") and ("dates" in str(key) or "jump_day" in str(key)):
            values = value if isinstance(value, (tuple, list)) else (value,)
            for v in values:
                if isinstance(v, (str, date)):
                    dates(str(v), str(v))
    config = json.loads((root / CONFIG).read_text())
    s = study(str(root), config["plan"]["sha256"])
    st.title(SECTION)
    journal = root / s.plan.get("journal", "reports/audit/track_a_real_pairs_v8.jsonl")
    if journal.exists():
        events = [json.loads(line) for line in journal.read_text().splitlines() if line]
        if events:
            st.caption(
                "Research starts charged across studies: "
                f"{events[-1]['global_started_pairs']}/200. "
                "A failed original start is retained; approved continuation does not "
                "refund or duplicate it."
            )
    st.info(
        "Hugging Face minute-derived hourly · "
        + s.plan["source_revision"]
        + " · FT16_v1 / TG20_4H_v1 ·20 fixed stocks · EXPLORATORY / PROTECTED CONFIRMATION LOCKED"
    )
    st.caption(
        (
            "As-reported share-volume regimes; verified split-price units; "
            "bounded input proxies; quarantine and missingness masks; publication"
            " timing assumed, not verified."
        )
    )
    view = st.radio("HF1M research view", VIEWS, key="hf1m_view", horizontal=True)
    pages = {
        VIEWS[0]: history_page,
        VIEWS[1]: targets_page,
        VIEWS[2]: training_page,
        VIEWS[3]: predictions_page,
        VIEWS[4]: qa_page,
        VIEWS[5]: guide_page,
    }
    pages[view](s)
