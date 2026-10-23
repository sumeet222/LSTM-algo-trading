"""P025 causal, training-frozen quantile-state diagnostics; never creates inputs."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .hf1m_ft16_source import ORDER
from .hf1m_training_data import TrainingView
from .objective_screen_metrics import equal_weights
from .objective_screen_source import gather, native_arrays, ordered_targets
from .visualization.hf1m_long import LongStudy


def inverse_quantiles(values: np.ndarray, weights: np.ndarray, quantiles: tuple) -> np.ndarray:
    if not np.isfinite(values).all() or (weights < 0).any() or weights.sum() <= 0:
        raise ValueError("P025_FINITE_TRAINING_STATE_REQUIRED")
    order = np.argsort(values, kind="stable")
    cumulative = np.cumsum(weights[order]) / weights.sum()
    cumulative[-1] = 1
    return values[
        order[np.minimum(np.searchsorted(cumulative, quantiles, side="left"), len(order) - 1)]
    ]


def causal_states(study: LongStudy, view: TrainingView) -> pd.DataFrame:
    """Only released input step47; future outcome candles never enter a state."""
    arrays = native_arrays(study, view)
    frames = []
    for start in range(0, len(view.source.rows), 128):
        positions = tuple(range(start, min(start + 128, len(view.source.rows))))
        native = gather(view, arrays, positions, "native")[:, :, 47, :]
        fallback = gather(view, arrays, positions, "fallback")[:, :, 47, :]
        part = {}
        for channel in ("V1", "M2", "Q2"):
            value, flag = native[:, :, ORDER.index(channel)], fallback[:, :, ORDER.index(channel)]
            if not np.array_equal(~np.isfinite(value), flag):
                raise ValueError("P025_STATE_FALLBACK_FLAG_MISMATCH")
            filled = np.where(flag, view.source.fit["fallbacks"][channel], value)
            part[channel + "_native_missing"] = ~np.isfinite(value.reshape(-1))
            part[channel] = filled.reshape(-1)
            part[channel + "_fallback"] = flag.reshape(-1)
            part["market_" + channel] = np.repeat(np.median(filled, axis=1), 20)
        frames.append(pd.DataFrame(part))
    result = pd.concat(frames, ignore_index=True)
    target = ordered_targets(view)
    result["origin_id"], result["ticker"] = target.origin_id, target.ticker
    return result


def state_cutoffs(f: pd.DataFrame, states: pd.DataFrame) -> dict:
    w = equal_weights(f.session_date_et.to_numpy())
    result = {}
    for name in ("V1", "M2", "Q2", "market_V1", "market_M2", "market_Q2"):
        result[name] = inverse_quantiles(states[name].to_numpy(), w, (1 / 3, 2 / 3)).tolist()
    width = (f.quantiles_z_95 - f.quantiles_z_05).to_numpy()
    result["predicted_width_z"] = inverse_quantiles(width, w, (1 / 3, 2 / 3)).tolist()
    return result


def variability(values: np.ndarray, w: np.ndarray, reference_width: float) -> dict:
    w = w / w.sum()
    mean = float(w @ values)
    q = inverse_quantiles(values, w, (0.05, 0.25, 0.75, 0.95))
    sd = float(np.sqrt(w @ ((values - mean) ** 2)))
    return dict(
        mean=mean,
        sd=sd,
        iqr=float(q[2] - q[1]),
        p05=float(q[0]),
        p95=float(q[3]),
        range=float(values.max() - values.min()),
        sd_over_unconditional_width=sd / reference_width,
    )


def state_analysis(
    f: pd.DataFrame, states: pd.DataFrame, cutoffs: dict, recipe: dict
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Conditional reductions keep the original population weight mass visible."""
    if not np.array_equal(
        f[["origin_id", "ticker"]].to_numpy(), states[["origin_id", "ticker"]].to_numpy()
    ):
        raise ValueError("P025_STATE_POPULATION_ALIGNMENT")
    g = f.copy()
    for name in states:
        if name not in g:
            g[name] = states[name].to_numpy()
    q = g[["quantiles_z_05", "quantiles_z_50", "quantiles_z_95"]].to_numpy(dtype=float)
    z = np.arcsinh(g.TG20.to_numpy() / recipe["scale"])
    widths = q[:, 2] - q[:, 0]
    g["predicted_width_z"] = widths
    g["center_z"], g["lower_span_z"], g["upper_span_z"] = (
        q[:, 1],
        q[:, 1] - q[:, 0],
        q[:, 2] - q[:, 1],
    )
    g["asymmetry_z"] = g.upper_span_z - g.lower_span_z
    w = equal_weights(g.session_date_et.to_numpy())
    error = z[:, None] - q
    tau = np.array([0.05, 0.5, 0.95])
    pin = np.maximum(tau * error, (tau - 1) * error).mean(axis=1)
    constant = np.asarray(recipe["quantiles_z"])
    e0 = z[:, None] - constant
    pin0 = np.maximum(tau * e0, (tau - 1) * e0).mean(axis=1)
    coverage = (z >= q[:, 0]) & (z <= q[:, 2])
    interval = widths + 20 * np.maximum(q[:, 0] - z, 0) + 20 * np.maximum(z - q[:, 2], 0)
    width_y = recipe["scale"] * (np.sinh(q[:, 2]) - np.sinh(q[:, 0]))
    rows = []
    groups = [("ALL", "ALL", np.ones(len(g), bool))]
    for name, cuts in cutoffs.items():
        labels = np.where(
            g[name].to_numpy() <= cuts[0],
            "LOW",
            np.where(g[name].to_numpy() <= cuts[1], "MID", "HIGH"),
        )
        g[name + "_state"] = labels
        groups.extend((name, label, labels == label) for label in ("LOW", "MID", "HIGH"))
    year = g.session_date_et.str[:4].astype(int)
    groups.extend(
        ("era", label, year.between(a, b).to_numpy())
        for label, a, b in (
            ("2011-2015", 2011, 2015),
            ("2016-2020", 2016, 2020),
            ("2021-2025", 2021, 2025),
        )
    )
    for name, label, mask in groups:
        mass = float(w[mask].sum())
        row = dict(
            state=name,
            group=label,
            rows=int(mask.sum()),
            origins=g.loc[mask, "origin_id"].nunique(),
            sessions=g.loc[mask, "session_date_et"].nunique(),
            stocks=g.loc[mask, "ticker"].nunique(),
            weight_mass=mass,
        )
        if mass:
            ww = w[mask] / mass
            row.update(
                pinball_z=float(ww @ pin[mask]),
                unconditional_pinball_z=float(ww @ pin0[mask]),
                pinball_skill=1 - float(ww @ pin[mask]) / float(ww @ pin0[mask]),
                interval90_coverage=float(ww @ coverage[mask]),
                width_z=float(ww @ widths[mask]),
                width_TG20=float(ww @ width_y[mask]),
                interval_score_z=float(ww @ interval[mask]),
                abs_future_z=float(ww @ abs(z[mask])),
                center_z=float(ww @ q[mask, 1]),
                lower_span_z=float(ww @ (q[mask, 1] - q[mask, 0])),
                upper_span_z=float(ww @ (q[mask, 2] - q[mask, 1])),
                asymmetry_z=float(ww @ (q[mask, 2] + q[mask, 0] - 2 * q[mask, 1])),
            )
            for k, suffix in enumerate(("05", "50", "95")):
                row["coverage_" + suffix] = float(ww @ (z[mask] <= q[mask, k]))
            for channel in ("V1", "M2", "Q2"):
                row[channel + "_fallback_rate"] = float(
                    ww @ g.loc[mask, channel + "_fallback"].to_numpy()
                )
            for column in g:
                if "volume" in str(column) and ("zero" in str(column) or "fallback" in str(column)):
                    if pd.api.types.is_bool_dtype(g[column]):
                        row[str(column) + "_rate"] = float(ww @ g[str(column)].to_numpy()[mask])
        rows.append(row)
    reference = float(constant[2] - constant[0])
    response: dict = {
        name: variability(g[name].to_numpy(dtype=float), w, reference)
        for name in ("center_z", "lower_span_z", "upper_span_z", "predicted_width_z", "asymmetry_z")
    }
    response["within_stock_width_variability"] = {
        str(ticker): variability(part.predicted_width_z.to_numpy(), w[part.index], reference)
        for ticker, part in g.groupby("ticker")
    }
    origin_width_sd = g.groupby("origin_id").predicted_width_z.std(ddof=0)
    origin_mass = (
        pd.Series(w, index=g.origin_id).groupby(level=0).sum().reindex(origin_width_sd.index)
    )
    response["within_origin_cross_stock_width_sd_mean"] = float(
        origin_mass.to_numpy() @ origin_width_sd.to_numpy()
    )
    # Intact-day read-only negative control. Average origin medians within each day.
    daily = pd.DataFrame(
        dict(day=g.session_date_et, origin=g.origin_id, width=widths, absolute_z=abs(z))
    )
    daily = daily.groupby(["day", "origin"])[["width", "absolute_z"]].median().groupby("day").mean()
    x, y = daily.width.to_numpy(), daily.absolute_z.to_numpy()

    def corr(a, b):
        return (
            float(pd.Series(a).rank().corr(pd.Series(b).rank()))
            if np.std(a) > 1e-15 and np.std(b) > 1e-15
            else np.nan
        )

    observed = corr(x, y)
    rng = np.random.default_rng(25042)
    null = (
        [corr(x, np.roll(y, int(rng.integers(1, len(y))))) for _ in range(400)]
        if len(y) > 1
        else []
    )
    response["negative_control"] = dict(
        statistic=observed,
        seed=25042,
        replicates=400,
        circular_shift_interval=np.nanquantile(null, [0.025, 0.975]).tolist()
        if null and np.isfinite(null).any()
        else [float("nan"), float("nan")],
        interpretation="read-only association; not neural permutation evidence",
    )
    return pd.DataFrame(rows), g, response


def plots(table: pd.DataFrame, destination) -> None:
    """Three exportable figures; each identifies quantile units and conditional metric."""
    import plotly.graph_objects as go

    v = table.loc[table.state.eq("V1")].set_index("group").reindex(["LOW", "MID", "HIGH"])
    for name, columns, title in (
        ("width_vs_V1", ["width_z"], "Predicted 90% z-width by causal V1 state"),
        (
            "conditional_pinball_skill",
            ["pinball_skill"],
            "Pinball skill vs frozen unconditional quantiles",
        ),
        (
            "coverage_and_realized_dispersion",
            ["interval90_coverage", "abs_future_z"],
            "Coverage and retrospective absolute future z",
        ),
    ):
        fig = go.Figure()
        for column in columns:
            fig.add_trace(go.Bar(x=v.index.tolist(), y=v[column].tolist(), name=column))
        fig.update_layout(title=title, xaxis_title="Training-frozen V1 tercile", barmode="group")
        fig.write_html(destination / (name + ".html"), include_plotlyjs="directory")
