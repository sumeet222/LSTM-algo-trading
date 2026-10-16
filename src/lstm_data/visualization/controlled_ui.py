"""Additive Streamlit pages for existing, sealed controlled-study evidence."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..ft0_transforms import ORDER
from ..pretraining_policy import CANDIDATE
from ..pretraining_tables import BaseTables
from . import figures as charts
from .controlled import (
    ARMS,
    KEYS,
    OBJECTIVES,
    Study,
    arm_model,
    event_state,
    feature_parameters,
    input_context,
    label_views,
    paired_table,
    quantiles,
)
from .definitions import FEATURES
from .loaders import (
    CAVEAT,
    PARTITIONS,
    Catalog,
    ViewUnavailable,
    component_base,
    feature_frame,
    gradient_batches,
)
from .metrics import loss_concentration

VIEWS = (
    "Target & denominator",
    "Training Curves & Gradients",
    "Predictions & Errors",
    "Extreme Events",
    "Feature Scaling Explorer",
)
PLOT_CONFIG = {"displaylogo": False, "scrollZoom": True, "modeBarButtonsToRemove": ["toImage"]}


@st.cache_data(max_entries=32, show_spinner=False)
def panel(root: str, token: tuple, fold: str, seed: int, arm: str, partition: str) -> pd.DataFrame:
    return Study.discover(Catalog.discover(Path(root))).panel(fold, seed, arm, partition)


@st.cache_resource(max_entries=1, show_spinner=False)
def base(root: str, token: tuple) -> BaseTables:
    return component_base(Catalog.discover(Path(root)))


@st.cache_data(max_entries=4, show_spinner=False)
def training_labels(root: str, token: tuple, fold: str, prefix: str) -> pd.DataFrame:
    c = Catalog.discover(Path(root))
    return Study.discover(c).training_targets(base(root, token), fold, prefix)


def plot(fig: go.Figure, key: str) -> None:
    st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG, key=key)


def histogram(values: pd.Series, units: str, log: bool, central: bool) -> go.Figure:
    fig = charts.finish(go.Figure(go.Histogram(x=values, nbinsx=70, name=units)), 320)
    fig.update_xaxes(title_text=units)
    if central:
        limits = values.quantile([0.01, 0.99]).to_list()
        fig.update_xaxes(range=limits)
    fig.update_yaxes(title_text="Stock-observation count", type="log" if log else "linear")
    return fig


def study_preset(view: str, arm: str | None = None) -> None:
    st.session_state.study_view = view
    if arm is not None:
        st.session_state.study_arm = arm
    if view == VIEWS[3]:
        st.session_state.event_order = "Worst session loss"
    if view == VIEWS[0]:
        st.session_state.study_comparator = "C0"


def open_study() -> None:
    st.session_state.section = "Controlled Experiments"
    study_preset(VIEWS[0], "T2")


def reset_study_dates() -> None:
    # Use actual saved cohort bounds, never suggest confirmation or an absent run.
    c = Catalog.discover(Path(st.session_state.study_root))
    frame = panel(
        str(c.root),
        c.token(),
        st.session_state.study_fold,
        42,
        "C0",
        st.session_state.study_partition,
    )
    first = date.fromisoformat(str(frame.session.min()))
    last = date.fromisoformat(str(frame.session.max()))
    st.session_state.study_dates = (first, min(first + timedelta(days=3), last))


def navigate_event(row: pd.Series, fold: str, seed: int, arm: str, partition: str) -> None:
    st.session_state.update(event_state(row, fold, seed, arm, partition))


def training_view(study: Study, fold: str, seed: int, arm: str) -> None:
    st.subheader("Training Curves & Gradients")
    st.caption(
        "Full recorded epoch trajectories: stock/date/origin/partition filters do not apply."
    )
    stage = st.radio("Study pass", ["calibration", "refit"], horizontal=True)
    traces = {}
    validation = go.Figure()
    for name in dict.fromkeys(("C0", arm)):
        trace = study.trace(fold, seed, name)
        phase = trace.loc[trace.stage == stage]
        traces[name] = phase
        obj = study.catalog.result(fold, arm_model(name, seed))
        selected = obj["selector"]["selected"]
        objective = charts.lines(
            phase,
            "epoch",
            ["optimizer_objective"],
            OBJECTIVES[name],
            selected if stage == "calibration" else None,
        )
        stop = int(phase.epoch.max())
        objective.add_vline(x=stop, line_dash="dot", annotation_text="Recorded stop")
        warnings = phase.loc[phase.warning]
        if not warnings.empty:
            objective.add_vline(
                x=int(warnings.epoch.min()), line_color=charts.RED, annotation_text="Warning onset"
            )
        st.markdown(f"**{name}: {OBJECTIVES[name]}** · {study.run_id(fold, seed, name)}")
        plot(objective, "objective_" + name)
        st.caption(
            f"Selected calibration epoch {selected}; actual {stage} stop {stop}. "
            f"Selector status: {obj['selector'].get('status', 'Not recorded')}. "
            "Fresh refit locks the selected epoch count; it has no second selection."
        )
        if stage == "calibration":
            validation.add_trace(
                go.Scatter(
                    x=phase.epoch, y=phase.inner_validation_MSE, name=name, mode="lines+markers"
                )
            )
            validation.add_vline(x=selected, line_dash="dash", annotation_text=f"{name} selected")
    st.warning(
        "Optimizer objectives use different units/derivatives. Lower values across arms "
        "do not establish better canonical prediction or less causal instability."
    )
    if stage == "calibration":
        plot(
            charts.finish(validation)
            .update_xaxes(title_text="Calibration epoch")
            .update_yaxes(title_text="Original TG0 inner-validation MSE"),
            "study_validation",
        )
    else:
        st.info("Inner-validation MSE is recorded for calibration only, not fresh refit.")
    for name, phase in traces.items():
        cap = 5.0 if name == "O1" else 1.0
        st.markdown(f"**{name} · preclip global norms · applied cap {cap:g}**")
        plot(
            charts.lines(
                phase,
                "epoch",
                ["grad_p50", "grad_p90", "grad_p99"],
                "Preclip global L2 gradient norm",
                cap=cap,
            ),
            "quantile_" + name,
        )
        plot(
            charts.lines(
                phase,
                "epoch",
                ["clipped_fraction", "applied_clipping_fraction", "fraction_above5"],
                "Fraction of batches",
            ),
            "fractions_" + name,
        )
        st.caption(
            "clipped_fraction = legacy norm>1; applied_clipping_fraction = measured "
            f"multiplier<1 at cap {cap:g}; fraction_above5 = norm>5. "
            "These are distinct for O1. Missing p90/p99/>5 remain gaps: Not recorded."
        )
        st.dataframe(
            phase[
                [
                    "epoch",
                    "grad_p50",
                    "grad_p90",
                    "grad_p99",
                    "nonfinite",
                    "warning",
                    "clipped_fraction",
                    "applied_clipping_fraction",
                    "fraction_above5",
                ]
            ],
            hide_index=True,
            width="stretch",
        )
        try:
            batch = gradient_batches(study.catalog, fold, arm_model(name, seed), stage)
            plot(charts.gradient_scatter(batch), "association_" + name)
            st.caption(
                f"{len(batch)} actual {stage} batches. Same-batch canonical TG0 MSE "
                "versus preclip norm; color = maximum |TG0|. Association only: "
                "repeated sessions/changing weights do not identify per-example causation."
            )
        except ViewUnavailable as exc:
            st.info(str(exc))


def target_view(
    study: Study, token: tuple, fold: str, stock: str, origins: tuple[int, ...], seed: int
) -> None:
    st.subheader("Target & denominator")
    prefix_label = st.radio(
        "Registered training population",
        ["Full refit prefix", "Inner-training prefix"],
        horizontal=True,
    )
    prefix = "inner" if prefix_label.startswith("Inner") else "refit"
    t1, t2 = (study.parameter(fold, arm, prefix) for arm in ("T1", "T2"))
    raw = training_labels(str(study.catalog.root), token, fold, prefix)
    raw = raw.loc[raw.origin.isin(origins)]
    if stock != "All stocks":
        raw = raw.loc[raw.symbol == stock]
    st.caption(
        f"{fold} · {prefix_label} · {stock} · {len(raw)} unique training stock/origin rows. "
        "This is the registered training population, independent of the development date "
        "window/seed. Stock/origin filters subset display only; parameters stay fixed."
    )
    st.write(
        f"Actual T1 cap **{t1['policy']['cap']:.12g}** · actual T2 s_{prefix} "
        f"**{t2['policy']['scale']:.12g}** · floor1e−6 · NumPy linear pooled q99."
    )
    st.caption(
        f"Preparation {t2['preparation_id']} · T1 parameter {t1['parameter_id']} · "
        f"T2 parameter {t2['parameter_id']} · source {study.catalog.config['manifest']['sha256']}"
    )
    log = st.checkbox("Log histogram counts", value=True)
    central = st.checkbox("Zoom central p1–p99 (display only)", value=False)
    labels = label_views(raw.TG0, t1, t2)
    for col, name in zip(st.columns(3), labels.columns):
        with col:
            st.markdown(f"**{name}**")
            plot(histogram(labels[name], str(name), log, central), "hist_" + str(name))
    st.dataframe(
        pd.DataFrame({name: quantiles(labels[name]) for name in labels}).T, width="stretch"
    )
    plot(
        charts.finish(
            go.Figure(
                go.Scattergl(
                    x=labels["Original TG0"],
                    y=labels["T2 asinh optimizer label"],
                    mode="markers",
                    marker=dict(size=4, opacity=0.35),
                )
            ),
            370,
        )
        .update_xaxes(title_text="Original canonical TG0 · training labels")
        .update_yaxes(title_text="T2 optimizer label asinh(TG0/s)"),
        "transform_map",
    )
    s = float(t2["policy"]["scale"])
    error = float(
        np.max(np.abs(s * np.sinh(labels["T2 asinh optimizer label"]) - labels["Original TG0"]))
    )
    st.caption(
        f"Read-only round trip TG0 → asinh(TG0/s) → s·sinh(z): max error {error:.3g}. "
        "Display transforms use registered float64 labels; optimizer arithmetic was float32. "
        "All points rendered; no metric decimation. Saved T2 forecasts are already inverted "
        "once into canonical TG0; they are never transformed by this reader."
    )
    absolute = raw.TG0.abs()
    st.dataframe(
        absolute.quantile([0.5, 0.9, 0.95, 0.99, 0.999, 1]).rename("|TG0|").to_frame(),
        width="stretch",
    )
    from .range_ui import range_explorer

    st.info(
        "TG0 = (future four-hour log return − cross-sectional median) / (MAD + "
        "training-fitted epsilon). All outcome quantities are EX-POST. "
        "Historical volatility normalization is not part of TG0."
    )
    range_explorer(study.catalog, token, fold, seed)


def prediction_view(
    study: Study, control: pd.DataFrame, treatment: pd.DataFrame, stock: str, arm: str
) -> None:
    st.subheader("Predictions & Errors")
    st.warning(
        "EX-POST TG0 / explored development or in-sample diagnostic. No profits, fills "
        "or selection-adjusted significance are implied."
    )
    table, daily = paired_table(control, treatment)
    st.dataframe(table, hide_index=True, width="stretch")
    st.caption(
        "Exact key/target/clock match: mismatches 0. Metrics use all five stocks regardless "
        "of Stock. Equal stocks → origins → sessions. ZERO project IC=0; defined-only "
        "Spearman IC=N/A. Residual = forecast−TG0. All canonical saved scores; T2 inverse once."
    )
    visible = CANDIDATE if stock == "All stocks" else (stock,)
    for symbol in visible:
        a, b = control.loc[control.symbol == symbol], treatment.loc[treatment.symbol == symbol]
        fig = charts.finish(go.Figure(), 380)
        for name, x, values in (
            ("EX-POST TG0", a, a.TG0),
            ("C0", a, a.score),
            (arm, b, b.score),
            ("ZERO", a, a.score * 0),
        ):
            fig.add_trace(
                go.Scatter(
                    x=charts.et_axis(x.cutoff),
                    y=values,
                    mode="lines+markers",
                    name=name,
                    customdata=x.cutoff.astype(str),
                )
            )
        fig.update_yaxes(title_text=f"{symbol} · canonical TG0")
        plot(fig, "study_forecast_" + symbol)
        residual = a[["cutoff", "residual"]].rename(columns={"residual": "C0 residual"}).copy()
        # Exact keys already checked, order explicitly aligned for the residual display.
        b = b.set_index(KEYS).loc[list(a[KEYS].itertuples(index=False, name=None))].reset_index()
        residual[arm + " residual"] = b.residual.to_numpy()
        residual["time_ET"] = charts.et_axis(residual.cutoff)
        plot(
            charts.lines(
                residual,
                "time_ET",
                ["C0 residual", arm + " residual"],
                "Canonical TG0 residual · forecast minus target",
            ),
            "study_residual_" + symbol,
        )
    for metric in ("delta_MSE", "delta_IC"):
        plot(charts.lines(daily, "session", [metric], f"{arm} − C0 daily {metric}"), metric)
    with st.expander("Exact daily numerical values"):
        st.dataframe(daily, hide_index=True, width="stretch")
    st.subheader("Full development fold × seed summary (ignores current filters)")
    pairs = study.table("paired_fold_seed_comparison.csv")
    st.dataframe(pairs.loc[pairs.arm == arm], hide_index=True, width="stretch")
    st.caption(
        "Existing Package011 exploratory intervals only: 5-session moving blocks, "
        "5,000 samples, seed8008, no bridging omitted exchange sessions. These intervals "
        "describe full development folds only. All arms remain mixed/inconclusive; "
        "all IC intervals span zero. No new resampling or significance test is performed."
    )


def extreme_view(
    control: pd.DataFrame,
    treatment: pd.DataFrame,
    fold: str,
    seed: int,
    arm: str,
    partition: str,
    stock: str,
) -> None:
    st.subheader("Extreme Events")
    daily, concentration = loss_concentration(treatment)
    st.write("Canonical raw-TG0 squared-loss session concentration", concentration)
    st.caption(
        "All five stocks, current dates/origins, equal-origin session MSE. "
        "Top shares use ceil(p×sessions). This is not the optimizer objective or a P&L curve."
    )
    plot(
        charts.lines(
            daily,
            "fraction_sessions",
            ["cumulative_loss_share"],
            "Cumulative canonical squared-loss share, worst sessions first",
        ),
        "study_loss_share",
    )
    criterion = st.selectbox(
        "Extreme event ordering",
        ["Highest |TG0|", "Largest squared residual", "Worst session loss"],
        key="event_order",
    )
    events = treatment.copy()
    events["abs_target"] = events.TG0.abs()
    events["session_MSE"] = events.session.map(daily.set_index("session").MSE)
    if stock != "All stocks":
        events = events.loc[events.symbol == stock]
    sort = {
        "Highest |TG0|": "abs_target",
        "Largest squared residual": "squared_error",
        "Worst session loss": "session_MSE",
    }[criterion]
    events = events.sort_values(sort, ascending=False).head(40).reset_index(drop=True)
    events["origin_ET"] = events.cutoff.dt.tz_convert("America/New_York").astype(str)
    events["origin_UTC"] = events.cutoff.astype(str)
    st.dataframe(
        events[
            [
                "run_id",
                "fold",
                "seed",
                "arm",
                "session",
                "origin_ET",
                "origin_UTC",
                "symbol",
                "TG0",
                "score",
                "residual",
                "squared_error",
                "session_MSE",
            ]
        ],
        hide_index=True,
        width="stretch",
    )
    i = st.selectbox(
        "Selected extreme event",
        range(len(events)),
        format_func=lambda i: (
            f"{events.iloc[i].session} / {events.iloc[i].symbol} / "
            f"{events.iloc[i].origin_ET} / {arm}"
        ),
    )
    st.button(
        "Inspect on Price & Features",
        on_click=navigate_event,
        args=(events.iloc[i], fold, seed, arm, partition),
        type="primary",
    )
    st.caption(
        "The button sets exact fold, seed/arm model, partition, stock, date and origin. "
        "Genuine candles/volume and EX-POST horizon markers open there; no fill is inferred."
    )


def feature_explorer(
    catalog: Catalog,
    token: tuple,
    fold: str,
    partition: str,
    stock: str,
    start: str,
    end: str,
    origin: int,
    event: dict | None = None,
) -> None:
    st.subheader("Feature Scaling Explorer")
    with st.expander("Package012A · full-population normalization audit", expanded=False):
        if st.checkbox("Open Package012A audit", key="audit_open"):
            from .normalization_ui import audit_panel

            audit_panel(catalog)
    symbol = st.selectbox(
        "Scaling stock", list(CANDIDATE), index=CANDIDATE.index(stock) if stock in CANDIDATE else 0
    )
    feature = st.selectbox("Scaling FT0 channel", list(ORDER), index=0)
    context = st.checkbox(
        "Use selected event's actual 48-step input context",
        value=event is not None,
        disabled=event is None,
    )
    if context and event is not None:
        frame = input_context(
            catalog,
            base(str(catalog.root), token),
            fold,
            partition,
            symbol,
            event["session"],
            int(event["origin"]),
        )
        st.caption(
            f"Exact 48 scheduled full hours ending at {event['session']} origin {event['origin']}. "
            "Approved inputs reconstructed from saved components/recipe; no model inference."
        )
    else:
        frame = feature_frame(
            catalog, base(str(catalog.root), token), symbol, fold, start, end, origin, partition
        )
        st.caption(
            "Completed-hour endpoints within the date window; not 48-step window duplicates."
        )
    chosen = frame.loc[frame.feature == feature].copy()
    if chosen.empty:
        raise ViewUnavailable("Not recorded: chosen FT0 channel has no values in this window.")
    st.caption(f"{symbol} / {fold} / {partition} · {feature}: {FEATURES[feature]} · dimensionless")
    st.json(feature_parameters(catalog, fold, partition, symbol, feature))
    chosen["time_ET"] = charts.et_axis(chosen.timestamp)
    for mode in ("native", "scaled"):
        plot(
            charts.lines(chosen, "time_ET", [mode], f"{feature} · {mode} dimensionless units"),
            "scaling_trace_" + mode,
        )
        plot(histogram(chosen[mode], f"{feature} · {mode}", False, False), "scaling_hist_" + mode)
    st.dataframe(
        pd.DataFrame({mode: quantiles(chosen[mode]) for mode in ("native", "scaled")}).T,
        width="stretch",
    )
    st.info(
        "Package012 readiness only. Existing fitted floors/centers/scales stay fixed. "
        "No alternative rolling z-score, MAD, floor or cross-sectional transform is applied."
    )


def controlled_page(catalog: Catalog, token: tuple) -> None:
    study = Study.discover(catalog)
    st.header("Controlled Experiments")
    st.session_state.study_root = str(catalog.root)
    st.sidebar.selectbox("Study", ["Package 011"])
    st.sidebar.caption("Base architecture: TM0 · shared stock-only LSTM")
    arm = st.sidebar.selectbox("Treatment", ARMS, index=3, key="study_arm")
    st.sidebar.selectbox("Paired comparator", ["C0"], key="study_comparator")
    fold = st.sidebar.selectbox(
        "Study fold", ["WF1", "WF2"], key="study_fold", on_change=reset_study_dates
    )
    seed = st.sidebar.selectbox("Study seed", [42, 123], key="study_seed")
    partition = st.sidebar.selectbox(
        "Study partition", PARTITIONS, key="study_partition", on_change=reset_study_dates
    )
    stock = st.sidebar.selectbox("Study stock", ["All stocks", *CANDIDATE], key="study_stock")
    control = panel(str(catalog.root), token, fold, seed, "C0", partition)
    treatment = panel(str(catalog.root), token, fold, seed, arm, partition)
    if "study_dates" not in st.session_state:
        first = date.fromisoformat(str(control.session.min()))
        st.session_state.study_dates = (first, first + timedelta(days=3))
    dates = st.sidebar.date_input(
        "Study dates (ET, inclusive)",
        key="study_dates",
        min_value=date(2020, 7, 1),
        max_value=date(2024, 6, 30),
    )
    label = st.sidebar.selectbox(
        "Study origins", ["Both", "10:30 ET", "11:30 ET"], key="study_origins"
    )
    origins = (1, 2) if label == "Both" else (1,) if label.startswith("10") else (2,)
    st.sidebar.caption("24/40 · candidate only · production D1 unchanged · confirmation locked")
    st.caption(CAVEAT)
    prediction_sha = catalog.config["models"][fold][arm_model(arm, seed)]["sha256"]
    st.caption(
        f"{study.run_id(fold, seed, arm)} / comparator {study.run_id(fold, seed, 'C0')} · "
        f"{partition} · canonical saved TG0 forecasts · SHA {prediction_sha}"
    )
    prefix = "inner" if partition == "Inner validation" else "refit"
    bound_parameter = study.parameter(fold, arm, prefix)
    st.caption(
        f"Source manifest SHA {catalog.config['manifest']['sha256']} · "
        f"{prefix} preparation {bound_parameter['preparation_id']}. "
        "Partition/dates apply to predictions/events; training panels label their own populations."
    )
    for col, text, view, selected_arm in zip(
        st.columns(4),
        ("Compare C0 vs T2", "Target tails", "Gradient clipping", "Worst loss sessions"),
        (VIEWS[0], VIEWS[0], VIEWS[1], VIEWS[3]),
        ("T2", None, None, None),
    ):
        col.button(text, on_click=study_preset, args=(view, selected_arm))
    view = st.radio("Study view", VIEWS, horizontal=True, key="study_view")
    if view == VIEWS[0]:
        target_view(study, token, fold, stock, origins, seed)
        return
    if view == VIEWS[1]:
        training_view(study, fold, seed, arm)
        return
    if not isinstance(dates, tuple) or len(dates) != 2:
        st.info("Select both study date endpoints.")
        return
    start, end = (x.isoformat() for x in dates)
    from .loaders import date_window

    date_window(start, end)
    first, last = str(control.session.min()), str(control.session.max())
    if start < first or end > last:
        raise ViewUnavailable(
            f"Not recorded: {fold}/{partition} saved mask spans {first} to {last}."
        )
    full = st.checkbox("Use full recorded partition for predictions/events metrics", value=False)

    def select(frame: pd.DataFrame) -> pd.DataFrame:
        mask = frame.origin.isin(origins)
        if not full:
            mask &= frame.session.between(start, end)
        return frame.loc[mask].copy()

    a, b = select(control), select(treatment)
    if a.empty:
        raise ViewUnavailable("Not recorded: no eligible saved origins in this date/origin window.")
    period = "full recorded partition" if full else start + " to " + end
    st.caption(
        f"Selected {fold}/{partition}, {period}, "
        f"{label}. Source/preparation references verified against the sealed study."
    )
    if view == VIEWS[2]:
        prediction_view(study, a, b, stock, arm)
    elif view == VIEWS[3]:
        extreme_view(a, b, fold, seed, arm, partition, stock)
    else:
        if full:
            st.caption(
                "Feature plots retain the bounded sidebar date window; no full-panel copy is built."
            )
        feature_explorer(catalog, token, fold, partition, stock, start, end, origins[0])
