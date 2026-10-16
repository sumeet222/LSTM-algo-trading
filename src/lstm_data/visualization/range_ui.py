"""Range table with inline genuine candles, plus chart-only Full data navigation."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from ..ft0_transforms import ORDER
from ..pretraining_policy import CANDIDATE
from .definitions import FEATURES
from .history import (
    HISTORY_END,
    HISTORY_START,
    LOCK_MESSAGE,
    SAFE_END,
    center_history_origin,
    context_window,
    history_bars,
    history_features,
    history_figure,
    history_guard,
    indicator_parameters,
    nearby_sessions,
    observation_figure,
    preparation_scope,
)
from .loaders import Catalog, ViewUnavailable
from .target_ranges import (
    SORTS,
    TARGETS,
    TargetRange,
    TargetSpec,
    denominator_comparison,
    ordered,
    page_rows,
    retained_selection,
    target_spec,
)

PLOT_CONFIG = {"displaylogo": False, "scrollZoom": True, "modeBarButtonsToRemove": ["toImage"]}


@st.cache_data(max_entries=8, show_spinner=False)
def target_relation(
    root: str, token: tuple, target: str, fold: str, population: str, seed: int
) -> pd.DataFrame:
    from .controlled import Study
    from .controlled_ui import base

    spec = target_spec(target)
    c = Catalog.discover(Path(root))
    return spec.decomposition(Study.discover(c), base(root, token), fold, population, seed)


@st.cache_data(max_entries=24, show_spinner=False)
def candles_slice(
    root: str, token: tuple, symbol: str, start: str, end: str, interval: str
) -> tuple[pd.DataFrame, dict]:
    history_guard(start, end)
    return history_bars(Catalog.discover(Path(root)), symbol, start, end, interval)


@st.cache_data(max_entries=16, show_spinner=False)
def indicator_slice(
    root: str,
    token: tuple,
    symbol: str,
    start: str,
    end: str,
    fold: str,
    prefix: str,
    origin: int,
) -> pd.DataFrame:
    # Guard before loading the canonical store, including on the first cache miss.
    history_guard(start, end)
    c = Catalog.discover(Path(root))
    scope = preparation_scope(c, fold, prefix)
    if start < scope["eligible_start"] or end > scope["eligible_end"]:
        raise ViewUnavailable("UNAVAILABLE / out of preparation scope. No fallback or refit.")
    from .controlled_ui import base

    return history_features(c, base(root, token), symbol, start, end, fold, prefix, origin)


def open_full_data(row: pd.Series) -> None:
    day = date.fromisoformat(str(row.session))
    history_guard(day.isoformat(), day.isoformat())
    st.session_state.update(
        section="Price & Features",
        partition="Full data",
        full_stock=str(row.symbol),
        full_jump=day,
        full_dates=(day, day),
        full_observation=str(row.observation_id),
        full_origin=int(row.origin),
        full_selected=dict(
            symbol=str(row.symbol),
            session=str(row.session),
            cutoff=str(row.cutoff),
            observation_id=str(row.observation_id),
        ),
    )


def inline_candles(c: Catalog, token: tuple, row: pd.Series, spec: TargetSpec) -> None:
    st.subheader("Selected observation · genuine candles & volume")
    st.write(f"**{row.symbol} · {row.session} · origin {row.origin} · {row.origin_ET}**")
    st.caption(f"UTC {row.origin_UTC} · identity {row.observation_id}")
    st.json(
        {
            "Known at forecast cutoff (idealized period-end clock)": {
                "stock": row.symbol,
                "origin_ET": row.origin_ET,
                "origin_UTC": row.origin_UTC,
            },
            "EX-POST; unavailable at cutoff": {
                name: row[name]
                for name in (
                    spec.key,
                    "log_return",
                    "median",
                    "MAD",
                    "numerator",
                    "denominator",
                    "floor_ge_MAD",
                    "maturity",
                )
            },
            "Fixed training-derived parameter (retrospective application)": {
                "epsilon": row.epsilon,
                "preparation_id": row.preparation_id,
            },
        },
        expanded=False,
    )
    cols = st.columns(2)
    before = cols[0].number_input("Context sessions before", 0, 5, 2)
    after = cols[1].number_input("Context sessions after", 0, 5, 2)
    start, end = context_window(str(row.session), int(before), int(after))
    try:
        bars, meta = candles_slice(str(c.root), token, str(row.symbol), start, end, "30 min source")
        fig = observation_figure(bars, row, spec)
    except ViewUnavailable as exc:
        st.warning(str(exc))
        return
    st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG, key="inline_target_candles")
    completed = bars.loc[bars.available_at.le(pd.Timestamp(row.cutoff))].tail(2)
    st.caption(
        "Genuine source intervals are labeled at START; origin marks the completed-hour "
        "boundary, not an invented candle. Prices USD, vendor retrospective split-adjusted; "
        "volume inverse-split adjusted shares. Forecast cutoff gold; EX-POST target proxy "
        "blue; dashed nominal 3-minute events are NOT fills. "
        "Future candles are hindsight context, never the 48-hour model input trace."
    )
    st.write("Last completed underlying source intervals at cutoff")
    st.dataframe(
        completed[["time_ET", "UTC_key", "available_at", "open", "high", "low", "close", "volume"]],
        hide_index=True,
        width="stretch",
    )
    if start == HISTORY_START.isoformat() or end == SAFE_END.isoformat():
        st.info("Context truncated at permitted archive boundary; only actual data is shown.")
    with st.expander("Exact candle/source values (full numeric precision)"):
        st.json(meta)
        st.dataframe(
            bars[["time_ET", "UTC_key", "open", "high", "low", "close", "volume"]].astype(str),
            hide_index=True,
            width="stretch",
        )
    st.button("Open in Full data", on_click=open_full_data, args=(row,))


def range_explorer(c: Catalog, token: tuple, fold: str, seed: int) -> None:
    st.subheader("Generic target range explorer")
    target = st.selectbox("Registered target", list(TARGETS))
    spec = target_spec(target)
    st.caption(f"{spec.key} · {spec.unit} · {spec.semantics}. {spec.provenance}. {spec.maturity}.")
    population = st.radio(
        "Range population",
        ["Full refit prefix", "Inner-training prefix", "Development"],
        horizontal=True,
    )
    raw = target_relation(str(c.root), token, target, fold, population, seed)
    st.caption(
        f"{fold} / {population} / seed {seed} (training labels seed-independent). "
        f"Eligible population ID {raw.population_id.iloc[0]} · preparation "
        f"{raw.preparation_id.iloc[0]} · source {c.config['manifest']['sha256']}. "
        "Independent of sidebar development dates/stock/origin; controls below subset display. "
        "Original canonical TG0, not T1 clipping, T2 asinh labels or predicted scores."
    )
    mode = st.radio("Range variable", ["Absolute", "Signed"], horizontal=True)
    a, b, d, e = st.columns(4)
    lower = a.text_input("Lower bound (blank = unbounded)", key="tg_lower")
    upper = b.text_input("Upper bound (blank = unbounded)", key="tg_upper")
    left = d.checkbox("Include lower endpoint", value=True)
    right = e.checkbox("Include upper endpoint", value=True)
    stock = st.selectbox("Range stock", ["All stocks", *CANDIDATE])
    origin = st.selectbox("Range origin", ["Both", "10:30 ET", "11:30 ET"])
    dates = st.date_input(
        "Range dates (ET; independent of sidebar)",
        value=(
            date.fromisoformat(str(raw.session.min())),
            date.fromisoformat(str(raw.session.max())),
        ),
        key="tg_dates_" + str(raw.population_id.iloc[0]),
    )
    try:
        bounds = TargetRange.parse(mode, lower, upper, left, right)
    except ViewUnavailable as exc:
        st.session_state.pop("tg_selected", None)
        st.warning(str(exc))
        return
    if not isinstance(dates, tuple) or len(dates) != 2:
        st.info("Select both range dates.")
        return
    start, end = (v.isoformat() for v in dates)
    eligible = raw.loc[raw.session.between(start, end)]
    if stock != "All stocks":
        eligible = eligible.loc[eligible.symbol.eq(stock)]
    if origin != "Both":
        eligible = eligible.loc[eligible.origin.eq(1 if origin.startswith("10") else 2)]
    matches = bounds.select(eligible, spec)
    order = st.selectbox("Sort matching rows", list(SORTS))
    ascending = st.checkbox("Ascending order", value=False)
    matches = ordered(matches, order, ascending, spec)
    selected = retained_selection(matches, st.session_state.get("tg_selected"))
    st.session_state.tg_selected = selected
    size = st.selectbox("Rows per page", [25, 50, 100, 200], index=1)
    _, pages = page_rows(matches, 1, size)
    # Filtering/sorting restarts pagination; identity selection remains if still eligible.
    fingerprint = (tuple(matches.observation_id), size)
    if st.session_state.get("tg_page_context") != fingerprint:
        st.session_state.tg_page = 1
        st.session_state.tg_page_context = fingerprint
    page = st.number_input(
        "Matching page", min_value=1, max_value=pages, value=1, step=1, key="tg_page"
    )
    visible, pages = page_rows(matches, int(page), size)
    st.write(
        f"Total eligible population: {len(raw):,} · after stock/date/origin: {len(eligible):,} · "
        f"range matches: {len(matches):,} · rendered: {len(visible):,} · page {page}/{pages}"
    )
    columns = [
        "session",
        "origin_ET",
        "origin_UTC",
        "origin",
        "symbol",
        spec.key,
        "abs_target",
        "log_return",
        "median",
        "MAD",
        "epsilon",
        "denominator",
        "numerator",
        "floor_ge_MAD",
        "MAD_lt_epsilon",
        "maturity",
        "observation_id",
    ]
    st.dataframe(visible[columns], hide_index=True, width="stretch", key="tg_matching_table")
    st.caption(
        "EX-POST: target, |target|, future log return, median, MAD, numerator, denominator, "
        "floor status and maturity. floor_ge_MAD means epsilon >= MAD (equality included). "
        "Denominator is MAD + epsilon, never max(MAD, epsilon). All pages are reachable."
    )
    if matches.empty:
        st.info("No observations match these bounds and filters. Blank both bounds to include all.")
        return
    # The supported accessible alternative avoids version-dependent cell-click behavior.
    options = [None, *matches.observation_id.tolist()]
    labels = {
        str(r.observation_id): f"{r.symbol} / {r.session} / origin {r.origin} / {r.origin_UTC}"
        for r in matches.itertuples()
    }
    chosen = st.selectbox(
        "Select observation (stock / session / origin / UTC)",
        options,
        format_func=lambda v: "Choose an observation" if v is None else labels[v],
        key="tg_selected",
    )
    st.button("Show candles", disabled=chosen is None, key="show_target_candles")
    st.caption(
        "Select observation updates the inline chart immediately; Show candles is always "
        "visible. Table cells are not clickable. Search the selector by stock/date."
    )
    if chosen is not None:
        row = matches.loc[matches.observation_id.eq(chosen)].iloc[0]
        inline_candles(c, token, row, spec)
        with st.expander("Exact EX-POST decomposition (full underlying precision)"):
            st.json({k: row[k] for k in columns})
    with st.expander("Full selected population denominator comparison"):
        st.caption(
            "Uses all stock/date/origin-selected rows before target-range filtering, "
            "independent of visible page. MAD is shared within session/origin; "
            "the five stock observations are not statistically independent."
        )
        st.dataframe(denominator_comparison(eligible, spec), hide_index=True, width="stretch")


def jump_history() -> None:
    day = st.session_state.full_jump
    st.session_state.full_dates = (day, day)


def step_history(day: str) -> None:
    value = max(HISTORY_START, min(HISTORY_END, date.fromisoformat(day)))
    st.session_state.update(full_jump=value, full_dates=(value, value))


def full_data_page(c: Catalog, token: tuple) -> None:
    st.header("Price & Features")
    st.subheader("Full data — chart-only history, not a training/evaluation partition")
    st.caption(
        "Five-year timeline: 2020-07-01 through 2025-06-30. "
        "Confirmation after 2024-06-30 stays locked. No forecasts or TG outcomes here."
    )
    stock = st.selectbox("Stock", CANDIDATE, key="full_stock")
    if "full_jump" not in st.session_state:
        st.session_state.full_jump = date(2020, 12, 9)
        st.session_state.full_dates = (date(2020, 12, 9),) * 2
    st.date_input(
        "Jump to date (ET)",
        key="full_jump",
        min_value=HISTORY_START,
        max_value=HISTORY_END,
        on_change=jump_history,
    )
    dates = st.date_input(
        "Date range (Full data, ET inclusive)",
        key="full_dates",
        min_value=HISTORY_START,
        max_value=HISTORY_END,
    )
    interval = st.selectbox("Candle interval", ["30 min source", "Completed hour"])
    selected = st.multiselect(
        "Indicator(s) · all registered FT0 channels",
        list(ORDER),
        format_func=lambda f: f"{f} · {FEATURES[f]}",
    )
    mode = st.radio(
        "Indicator display",
        ["Standard / native indicator", "Normalized / model input", "Both"],
        horizontal=True,
    )
    recipe = st.selectbox(
        "Fitted preparation (explicit retrospective recipe)",
        ["WF1 / refit", "WF1 / inner", "WF2 / refit", "WF2 / inner"],
    )
    origin = st.selectbox("Indicator origin context", [1, 2], key="full_origin")
    if not isinstance(dates, tuple) or len(dates) != 2:
        st.info("Select both history endpoints.")
        return
    start, end = (v.isoformat() for v in dates)
    # Absolute boundary: no recipe/feature/source numeric reads before this guard.
    try:
        history_guard(start, end)
    except ViewUnavailable as exc:
        st.warning(LOCK_MESSAGE if end > SAFE_END.isoformat() else str(exc))
        return
    previous, following, early = nearby_sessions(start)
    a, b = st.columns(2)
    a.button("Previous exchange session", on_click=step_history, args=(previous,))
    b.button("Next exchange session", on_click=step_history, args=(following,))
    if early:
        st.info(
            "Early-close session: only scheduled genuine intervals; no invented afternoon bars."
        )
    try:
        bars, meta = candles_slice(str(c.root), token, stock, start, end, interval)
    except ViewUnavailable as exc:
        st.info(str(exc) + " Use previous/next exchange session for a holiday/weekend.")
        return
    fold, prefix = recipe.split(" / ")
    scope = preparation_scope(c, fold, prefix)
    st.json(scope, expanded=False)
    st.caption(
        "Native means the registered FT0 formula with this recipe's saved floors, "
        "not unsplit prices. Pooled scaled channels use saved centers/scales; "
        "B2/T2/T5 are bounded identity. Retrospective training-prefix values can use "
        "a later fitted training recipe; these are not historical live forecasts."
    )
    features = None
    parameters = {}
    if selected:
        try:
            features = indicator_slice(str(c.root), token, stock, start, end, fold, prefix, origin)
            parameters = indicator_parameters(c, fold, prefix, stock, selected)
        except ViewUnavailable as exc:
            st.warning(str(exc))
    fig = history_figure(bars, features, selected, mode, parameters)
    linked = st.session_state.get("full_selected")
    if linked and stock == linked["symbol"] and start <= linked["session"] <= end:
        st.caption("Opened from exact observation " + linked["observation_id"])
        center_history_origin(fig, bars, linked["cutoff"])
    st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG, key="full_history_candles")
    st.caption(
        "Source candle START / completed feature END; both ET and UTC on hover. "
        "USD split-adjusted prices; inverse-split volume in shares. Shared time axis, "
        "separate price, volume and feature panels; zoom/pan/reset in chart toolbar. "
        "Only genuine local source values; missing data remain gaps."
    )
    with st.expander("Exact source values and fitted indicator parameters"):
        st.json(meta)
        st.json(parameters)
        st.dataframe(
            bars[["time_ET", "UTC_key", "open", "high", "low", "close", "volume"]].astype(str),
            hide_index=True,
            width="stretch",
        )
        if features is not None:
            st.dataframe(
                features.loc[features.feature.isin(selected)].astype(str),
                hide_index=True,
                width="stretch",
            )
