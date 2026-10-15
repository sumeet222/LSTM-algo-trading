"""Small local Plotly figures; canonical UTC keys remain intact in hover data."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .definitions import FEATURES, MARKET
from .loaders import ET

TEAL, RED, GOLD, BLUE = "#168b8a", "#c75b68", "#c38f2e", "#4166ac"


def et_axis(values: pd.Series) -> pd.Series:
    """Plot Eastern wall time; retain unmodified UTC keys separately for unambiguous hover."""
    return pd.to_datetime(values, utc=True).dt.tz_convert(ET).dt.tz_localize(None)


def finish(fig: go.Figure, height: int = 560) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=height,
        hovermode="x unified",
        margin=dict(l=30, r=25, t=35, b=35),
        legend=dict(orientation="h", y=1.12),
        font=dict(size=13),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(title_text="Eastern time (America/New_York)")
    return fig


def candles(
    frame: pd.DataFrame,
    markers: pd.DataFrame | None = None,
    overlay: pd.DataFrame | None = None,
    log_price: bool = False,
    compress: bool = False,
) -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.045, row_heights=[0.73, 0.27]
    )
    custom = np.column_stack(
        (
            frame.time_ET,
            frame.UTC_key,
            frame.source_archive,
            frame.volume.astype(str),
            frame.is_stub.astype(str),
        )
    )
    fig.add_trace(
        go.Candlestick(
            x=et_axis(frame.timestamp),
            open=frame.open,
            high=frame.high,
            low=frame.low,
            close=frame.close,
            name="Adjusted USD · source OHLC",
            customdata=custom,
            increasing_line_color=TEAL,
            decreasing_line_color=RED,
            text=[
                f"{r.symbol} · {r.time_ET}<br>UTC start {r.UTC_key}"
                f"<br>O {r.open:.4f} H {r.high:.4f} L {r.low:.4f} C {r.close:.4f}"
                f"<br>Volume {r.volume:,.0f}; stub={r.is_stub}"
                f"<br>Source {r.source_archive}"
                for r in frame.itertuples()
            ],
            hoverinfo="text",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=et_axis(frame.timestamp),
            y=frame.volume,
            marker_color=[
                GOLD if stub else TEAL if c >= o else RED
                for stub, c, o in zip(frame.is_stub, frame.close, frame.open)
            ],
            name="Inverse-split volume · gold = closing stub",
            customdata=custom,
            hovertemplate="%{customdata[0]}<br>UTC %{customdata[1]}"
            "<br>Volume %{y:,.0f}<br>Stub %{customdata[4]}<extra></extra>",
        ),
        row=2,
        col=1,
    )
    if overlay is not None and not overlay.empty:
        fig.add_trace(
            go.Scatter(
                x=et_axis(overlay.timestamp),
                y=overlay.price,
                name="Prior20 daily-close SMA = C/exp(T1)",
                line=dict(color=BLUE, width=2),
            ),
            row=1,
            col=1,
        )
    if markers is not None and not markers.empty:
        low, high = float(frame.low.min()), float(frame.high.max())
        for r in markers.itertuples():
            # Separate three-minute nominal events from observed completed close proxies.
            for field, color, dash, name in [
                ("cutoff", GOLD, "dot", "Forecast cutoff"),
                ("proxy_exit_close", BLUE, "dot", "Future label proxy close"),
                ("entry_event", TEAL, "dash", "Idealized entry event, NOT fill"),
                ("exit_event", RED, "dash", "Idealized maturity/exit, NOT fill"),
            ]:
                t = pd.Timestamp(getattr(r, field)).tz_convert(ET).tz_localize(None)
                fig.add_trace(
                    go.Scatter(
                        x=[t, t],
                        y=[low, high],
                        mode="lines",
                        line=dict(color=color, dash=dash, width=1),
                        showlegend=False,
                        name=name,
                        hovertemplate=name + "<br>%{x}<extra></extra>",
                    ),
                    row=1,
                    col=1,
                )
    fig.update_yaxes(
        title_text="USD · split-adjusted", type="log" if log_price else "linear", row=1, col=1
    )
    fig.update_yaxes(title_text="Volume · adjusted shares", row=2, col=1)
    fig.update_layout(xaxis_rangeslider_visible=False)
    if compress:
        fig.update_xaxes(
            rangebreaks=[dict(bounds=["sat", "mon"]), dict(bounds=[16, 9.5], pattern="hour")]
        )
    return finish(fig, 640)


def features(frame: pd.DataFrame, selected: Sequence[str], mode: str) -> go.Figure:
    fig = go.Figure()
    for feature in selected:
        part = frame.loc[frame.feature == feature]
        definition = {**FEATURES, **MARKET}.get(feature, feature)
        fig.add_trace(
            go.Scatter(
                x=et_axis(part.timestamp),
                y=part[mode],
                mode="lines+markers",
                name=feature,
                customdata=part.timestamp.astype(str),
                hovertemplate=feature
                + " · "
                + definition
                + "<br>%{x} ET<br>UTC %{customdata}<br>%{y:.5f}<extra></extra>",
            )
        )
    fig.update_yaxes(title_text="Dimensionless · " + mode + " FT0/state")
    return finish(fig, 330)


def forecasts(frame: pd.DataFrame, baseline: pd.DataFrame | None = None) -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12, row_heights=[0.7, 0.3]
    )
    x = et_axis(frame.cutoff)
    model = str(frame.model.iloc[0])
    custom = np.column_stack((frame.cutoff.astype(str), frame.maturity.astype(str), frame.residual))
    for name, y, color in [
        ("Realized TG0 · EX-POST LABEL", frame.TG0, GOLD),
        (model + " score", frame.score, TEAL),
    ]:
        row = 2 if model == "M1" and name.startswith("M1") else 1
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines+markers",
                name=name,
                line=dict(color=color),
                customdata=custom,
                hovertemplate=name + "<br>%{x} ET<br>%{y:.5f}"
                "<br>UTC cutoff %{customdata[0]}"
                "<br>Label maturity %{customdata[1]}"
                "<br>Residual %{customdata[2]:.5f}<extra></extra>",
            ),
            row=row,
            col=1,
        )
    if baseline is not None:
        fig.add_trace(
            go.Scatter(
                x=et_axis(baseline.cutoff),
                y=baseline.score,
                name=str(baseline.model.iloc[0]) + " reference",
                line=dict(color=BLUE, dash="dot"),
            ),
            row=1,
            col=1,
        )
    if model != "M1":
        fig.add_trace(
            go.Bar(x=x, y=frame.residual, name="Score − realized TG0", marker_color=RED),
            row=2,
            col=1,
        )
    fig.update_yaxes(title_text="TG0 units", row=1, col=1)
    fig.update_yaxes(
        title_text="M1 ranking units" if model == "M1" else "Residual TG0", row=2, col=1
    )
    return finish(fig)


def lines(
    frame: pd.DataFrame,
    x: str,
    ys: list[str],
    ylabel: str,
    selected_epoch: int | None = None,
    cap: float | None = None,
) -> go.Figure:
    fig = go.Figure()
    for y in ys:
        fig.add_trace(go.Scatter(x=frame[x], y=frame[y], name=y, mode="lines+markers"))
    if selected_epoch is not None:
        fig.add_vline(
            x=selected_epoch,
            line_dash="dot",
            line_color=GOLD,
            annotation_text="Selected qualifying checkpoint",
        )
    if cap is not None:
        fig.add_hline(y=cap, line_color=RED, line_dash="dash")
    fig.update_yaxes(title_text=ylabel)
    finish(fig, 360)
    fig.update_xaxes(title_text=x.replace("_", " "))
    return fig


def gradient_scatter(frame: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Scattergl(
            x=frame.batch_session_weighted_MSE,
            y=frame.preclip_global_grad_norm,
            mode="markers",
            marker=dict(
                color=frame.target_abs_max,
                colorscale="Viridis",
                size=7,
                colorbar=dict(title="Max |TG0|"),
            ),
            customdata=np.column_stack((frame.epoch, frame.batch_index, frame.session_ids)),
            hovertemplate="MSE %{x:.4f} · norm %{y:.4f}<br>Epoch %{customdata[0]}"
            " · batch %{customdata[1]}<br>Sessions %{customdata[2]}<extra></extra>",
        )
    )
    fig.add_hline(y=1, line_dash="dash", line_color=RED)
    finish(fig, 420)
    fig.update_xaxes(title_text="Effective-batch session-weighted MSE")
    fig.update_yaxes(title_text="Preclip global L2 norm")
    return fig
