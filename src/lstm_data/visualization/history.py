"""Bounded historical navigation and explicit saved-preparation scope, without fitting."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..calendar import schedule, session_grid
from ..pretraining_store import read_preparation
from ..pretraining_tables import BaseTables
from . import figures as charts
from .controlled import feature_parameters
from .loaders import ET, Catalog, ViewUnavailable, date_window, feature_frame, source_bars
from .target_ranges import TargetSpec

HISTORY_START = date(2020, 7, 1)
HISTORY_END = date(2025, 6, 30)
SAFE_END = date(2024, 6, 30)
LOCK_MESSAGE = (
    "LOCKED — protected confirmation: 2024-07-01 through 2025-06-30. Inspecting even raw "
    "numeric prices/volume visually can compromise the untouched-confirmation claim. "
    "Separate affirmative researcher authorization and an audit record reclassifying the "
    "viewed period are required; a new holdout plan may be necessary. This implementation "
    "prompt does not unlock it. No numerical confirmation content was loaded."
)


def history_guard(start: str, end: str) -> None:
    """Run before source, feature-store, recipe or saved-outcome numeric readers."""
    a, b = date.fromisoformat(start), date.fromisoformat(end)
    if b > SAFE_END:
        raise ViewUnavailable(LOCK_MESSAGE)
    if a < HISTORY_START or b > HISTORY_END or a > b:
        raise ViewUnavailable("Choose an ordered range within the five-year timeline.")
    date_window(start, end, maximum_days=31)


def history_bars(
    catalog: Catalog, symbol: str, start: str, end: str, interval: str
) -> tuple[pd.DataFrame, dict]:
    history_guard(start, end)
    return source_bars(catalog, symbol, start, end, interval)


def nearby_sessions(day: str) -> tuple[str, str, bool]:
    """Calendar-only previous/next navigation; does not inspect prices or labels."""
    d = date.fromisoformat(day)
    days = [
        str(v.date())
        for v in schedule(
            (d - timedelta(days=12)).isoformat(), (d + timedelta(days=12)).isoformat()
        ).index
    ]
    previous = max((v for v in days if v < day), default=day)
    following = min((v for v in days if v > day), default=day)
    current = schedule(day, day)
    early = bool(not current.empty and current.iloc[0].close.tz_convert(ET).hour < 16)
    return previous, following, early


def context_window(day: str, before: int = 2, after: int = 2) -> tuple[str, str]:
    if not 0 <= before <= 5 or not 0 <= after <= 5:
        raise ViewUnavailable("Context is bounded to 0–5 exchange sessions per side.")
    history_guard(day, day)
    d = date.fromisoformat(day)
    days = [
        str(v.date())
        for v in schedule(
            max(HISTORY_START, d - timedelta(days=20)).isoformat(),
            min(SAFE_END, d + timedelta(days=20)).isoformat(),
        ).index
    ]
    if day not in days:
        raise ViewUnavailable("Selected origin has no exchange session.")
    i = days.index(day)
    return days[max(0, i - before)], days[min(len(days) - 1, i + after)]


def target_markers(row: pd.Series, spec: TargetSpec) -> pd.DataFrame:
    """Only registered full-hour horizons; reject early-close/overnight substitution."""
    if spec.horizon_full_hours is None:
        raise ViewUnavailable("Registered horizon annotations UNAVAILABLE.")
    day = str(row.session)
    history_guard(day, day)
    session = schedule(day, day)
    if session.empty:
        raise ViewUnavailable("Origin exchange calendar unavailable.")
    grid = session_grid(session.iloc[0].open, session.iloc[0].close)
    ends = [v["end"] for v in grid if not v["stub"]]
    cutoff = pd.Timestamp(row.cutoff)
    if cutoff not in ends:
        raise ViewUnavailable("Origin is not a completed full-hour boundary.")
    j = ends.index(cutoff) + spec.horizon_full_hours
    if j >= len(ends):
        raise ViewUnavailable("Target proxy horizon UNAVAILABLE in this session.")
    target = ends[j]
    if target + pd.Timedelta(minutes=3) != pd.Timestamp(row.maturity):
        raise ViewUnavailable("Registered maturity differs from scheduled proxy horizon.")
    return pd.DataFrame(
        [
            dict(
                cutoff=cutoff,
                proxy_exit_close=target,
                entry_event=cutoff + pd.Timedelta(minutes=3),
                exit_event=pd.Timestamp(row.maturity),
            )
        ]
    )


def observation_figure(bars: pd.DataFrame, row: pd.Series, spec: TargetSpec) -> go.Figure:
    markers = target_markers(row, spec)
    fig = charts.candles(bars, markers)
    for field, label, color in (
        ("cutoff", "Forecast origin · completed-hour boundary", charts.GOLD),
        ("proxy_exit_close", "EX-POST 4h target proxy close · NOT fill", charts.BLUE),
    ):
        at = pd.Timestamp(markers.iloc[0][field]).tz_convert(ET).tz_localize(None)
        fig.add_annotation(
            x=at,
            y=1 if field == "cutoff" else 0.92,
            xref="x",
            yref="paper",
            text=label,
            showarrow=True,
            arrowcolor=color,
            font=dict(color=color),
        )
    center = pd.Timestamp(row.cutoff).tz_convert(ET).tz_localize(None)
    first = pd.Timestamp(bars.timestamp.min()).tz_convert(ET).tz_localize(None)
    last = pd.Timestamp(bars.available_at.max()).tz_convert(ET).tz_localize(None)
    radius = max(center - first, last - center, pd.Timedelta(hours=4))
    fig.update_xaxes(range=[center - radius, center + radius])
    fig.update_layout(
        meta=dict(
            symbol=str(row.symbol),
            origin_UTC=str(row.cutoff),
            observation_id=str(row.observation_id),
        )
    )
    return fig


def preparation_scope(catalog: Catalog, fold: str, prefix: str) -> dict:
    if fold not in ("WF1", "WF2") or prefix not in ("inner", "refit"):
        raise ViewUnavailable("Choose an explicitly registered fitted preparation.")
    ref = catalog.config["recipes"][fold][prefix]
    prep = read_preparation(catalog.root, ref)
    stop = (
        read_preparation(catalog.root, catalog.config["recipes"][fold]["refit"]).window.stop
        if prefix == "inner"
        else pd.Timestamp(catalog.config["development_windows"][fold][1], tz=ET)
        + pd.DateOffset(days=1)
    )
    return dict(
        fold=fold,
        prefix=prefix,
        preparation_id=prep.preparation_id,
        source_binding=prep.source_binding,
        action_binding=prep.action_binding,
        training_start=str(prep.window.start),
        training_stop=str(prep.window.stop),
        fitted_at=str(prep.window.fitted_at),
        constructed_at=prep.constructed_at,
        eligible_start=prep.window.start.tz_convert(ET).date().isoformat(),
        eligible_end=(stop.tz_convert(ET).date() - timedelta(days=1)).isoformat(),
        recipe=ref,
        application="Retrospective training / saved evaluation scope only",
    )


def history_features(
    catalog: Catalog,
    base: BaseTables,
    symbol: str,
    start: str,
    end: str,
    fold: str,
    prefix: str,
    origin: int,
) -> pd.DataFrame:
    history_guard(start, end)
    scope = preparation_scope(catalog, fold, prefix)
    if start < scope["eligible_start"] or end > scope["eligible_end"]:
        raise ViewUnavailable("UNAVAILABLE / out of preparation scope. No fallback or refit.")
    return feature_frame(
        catalog,
        base,
        symbol,
        fold,
        start,
        end,
        origin,
        "Inner validation" if prefix == "inner" else "Refit training",
    )


def history_figure(
    bars: pd.DataFrame,
    features: pd.DataFrame | None,
    selected: Sequence[str],
    mode: str,
    parameters: dict[str, dict],
) -> go.Figure:
    """Share one time axis, with price, volume and every feature/unit in separate panels."""
    modes = (
        ["native", "scaled"]
        if mode == "Both"
        else ["native" if mode == "Standard / native indicator" else "scaled"]
    )
    panels = [(f, m) for f in selected for m in modes] if features is not None else []
    n = 2 + len(panels)
    fig = make_subplots(
        rows=n,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=min(0.04, 0.5 / n),
        row_heights=[3, 1] + [1.3] * len(panels),
    )
    candles = charts.candles(bars)
    for i, trace in enumerate(candles.data):
        fig.add_trace(trace, row=i + 1, col=1)
    fig.update_yaxes(title_text="USD · split-adjusted", row=1, col=1)
    fig.update_yaxes(title_text="Volume · adjusted shares", row=2, col=1)
    if features is not None:
        for index, (feature, representation) in enumerate(panels, 3):
            part = features.loc[features.feature == feature]
            param = parameters[feature]
            description = (
                (
                    f"{part.symbol.iloc[0]} · {feature} · {representation} · dimensionless"
                    f"<br>Preparation {param['preparation_id']}"
                    f"<br>Training stop {param['fitted_stop']}"
                    f"<br>Method {param['method']} · center {param.get('center', 'identity')}"
                    f" · scale {param.get('scale', 'identity')}"
                )
                if not part.empty
                else feature
            )
            fig.add_trace(
                go.Scatter(
                    x=charts.et_axis(part.timestamp),
                    y=part[representation],
                    name=f"{feature} · {representation}",
                    mode="lines+markers",
                    customdata=part.timestamp.astype(str),
                    hovertemplate=description + "<br>%{x} ET<br>UTC %{customdata}"
                    "<br>Value %{y:.17g}<extra></extra>",
                ),
                row=index,
                col=1,
            )
            fig.update_yaxes(title_text=f"{feature} · {representation}", row=index, col=1)
    fig.update_layout(xaxis_rangeslider_visible=False)
    return charts.finish(fig, 640 + 170 * len(panels))


def center_history_origin(fig: go.Figure, bars: pd.DataFrame, cutoff: str) -> None:
    """Carry only a known forecast boundary into Full data, without loading outcomes."""
    at = pd.Timestamp(cutoff).tz_convert(ET).tz_localize(None)
    first = pd.Timestamp(bars.timestamp.min()).tz_convert(ET).tz_localize(None)
    last = pd.Timestamp(bars.available_at.max()).tz_convert(ET).tz_localize(None)
    radius = max(at - first, last - at, pd.Timedelta(hours=4))
    fig.update_xaxes(range=[at - radius, at + radius])
    fig.add_shape(
        type="line",
        x0=at,
        x1=at,
        y0=0,
        y1=1,
        xref="x",
        yref="paper",
        line=dict(color=charts.GOLD, dash="dot"),
    )
    fig.add_annotation(
        x=at,
        y=1,
        xref="x",
        yref="paper",
        showarrow=True,
        text="Selected forecast origin · completed-hour boundary",
    )


def indicator_parameters(
    catalog: Catalog, fold: str, prefix: str, symbol: str, selected: Sequence[str]
) -> dict[str, dict]:
    partition = "Inner validation" if prefix == "inner" else "Refit training"
    return {f: feature_parameters(catalog, fold, partition, symbol, f) for f in selected}
