"""Read-only Package012B evidence inside the existing dashboard."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..ft0_transforms import identity
from ..normalization_report import AuditPacket
from ..pretraining_policy import CANDIDATE
from .controlled_ui import base
from .loaders import (
    CAVEAT,
    Catalog,
    ViewUnavailable,
    date_window,
    feature_frame,
    read_json,
    verified,
)
from .normalization_ui import open_example


def handoff(catalog: Catalog) -> dict:
    ref = catalog.config.get("nb1_experiment")
    if ref is None:
        raise ViewUnavailable("Package012B evidence has not been registered.")
    value = read_json(catalog.root, ref)
    if (
        value.get("package") != "TA012B_NB1_v1"
        or value.get("confirmation_numeric_rows") != 0
        or value.get("source") != catalog.config["manifest"]
        or value.get("original_recipes") != catalog.config["recipes"]
    ):
        raise ViewUnavailable("Package012B source/recipe/scope binding changed.")
    return value


def table(catalog: Catalog, manifest: dict, name: str) -> pd.DataFrame:
    if name not in manifest["artifacts"]:
        raise ViewUnavailable("Not recorded: " + name)
    return pd.read_csv(
        verified(catalog.root, manifest["artifacts"][name]), float_precision="round_trip"
    )


def open_nb1() -> None:
    st.session_state.section = "B1 Normalization (012B)"


def tail_example(row: pd.Series) -> None:
    open_example(row)
    st.session_state.normalization_context = True
    st.session_state.normalization_nb1 = True


def recipe(catalog: Catalog, manifest: dict, fold: str, prefix: str) -> dict:
    if fold not in ("WF1", "WF2") or prefix not in ("inner", "refit"):
        raise ViewUnavailable("Only registered preconfirmation recipes.")
    value = read_json(catalog.root, manifest["artifacts"]["normalization_recipes.json"])[fold][
        prefix
    ]
    if identity({k: v for k, v in value.items() if k != "recipe_id"}) != value["recipe_id"]:
        raise ViewUnavailable("N-B1 recipe identity changed.")
    return value


def panel(catalog: Catalog, token: tuple) -> None:
    st.header("Package012B · B1 input normalization")
    manifest = handoff(catalog)
    st.caption(CAVEAT)
    st.caption(
        f"Cumulative pair starts: {manifest.get('global_started_pairs', 24)} / 200. "
        "Package011 remains historically sealed at24/40."
    )
    st.info(
        "B1 input compression only. Canonical TG0 is unchanged; "
        "these are explored development data. "
        "N-V12 remains untrained. Confirmation is locked."
    )
    if "matched_results.csv" in manifest["artifacts"]:
        matched = table(catalog, manifest, "matched_results.csv")
        if (
            len(matched) != 4
            or not matched.canonical_targets_exact.all()
            or not matched.masks_exact.all()
        ):
            raise ViewUnavailable("NOT_MATCHED: incomplete four-cell table.")
        a, b = st.columns(2)
        a.metric("MSE improvements", f"{int((matched.delta_MSE < 0).sum())} / 4")
        b.metric("Rank IC improvements", f"{int((matched.delta_IC > 0).sum())} / 4")
        st.dataframe(matched, hide_index=True, width="stretch")
        st.caption(
            "Δ = N-B1 minus C0. MSE lower is better; IC higher is better. "
            "Consistency counts are descriptive, with no significance claim."
        )
    else:
        st.warning("FIT_AUTHORITY_HOLD · recipes/preflight ready; no new fitted result recorded.")
    fold = st.selectbox("N-B1 fold", ["WF2", "WF1"], key="nb1_fold")
    prefix = st.selectbox("N-B1 fit scope", ["refit", "inner"], key="nb1_prefix")
    r = recipe(catalog, manifest, fold, prefix)
    st.json(
        {
            key: r[key]
            for key in (
                "recipe_id",
                "original_preparation_id",
                "window",
                "count",
                "keys_sha256",
                "s",
                "c",
                "a",
                "method",
                "fallback",
            )
        },
        expanded=False,
    )
    stock = st.selectbox("N-B1 stock", CANDIDATE, index=2, key="nb1_stock")
    origin = st.selectbox("N-B1 historical origin context", [1, 2], key="nb1_origin")
    dates = st.date_input(
        "N-B1 source dates (ET)",
        (date(2024, 1, 25), date(2024, 1, 25))
        if fold == "WF2"
        else (date(2023, 10, 27), date(2023, 10, 27)),
        min_value=date(2020, 7, 1),
        max_value=date(2024, 6, 30),
        key="nb1_dates",
    )
    if not isinstance(dates, tuple) or len(dates) != 2:
        st.info("Select both dates.")
        return
    start, end = (d.isoformat() for d in dates)
    date_window(start, end)
    frame = feature_frame(
        catalog,
        base(str(catalog.root), token),
        stock,
        fold,
        start,
        end,
        origin,
        "Inner validation" if prefix == "inner" else "Development",
    )
    f = frame.loc[frame.feature.eq("B1") & frame.native.notna()].copy()
    if f.empty:
        raise ViewUnavailable("No genuine B1 rows for those dates.")
    f["q"] = np.arcsinh(f.native.to_numpy(dtype=float) / r["s"])
    f["N_B1_scaled"] = ((f.q - r["c"]) / r["a"]).astype(np.float32)
    st.caption(
        "Native x=log(H/L); q=asinh(x/s); N-B1=(q−c)/a. "
        "Dates before the recorded fit stop are retrospective training illustrations. "
        "Each axis below has its own explicitly labeled units."
    )
    st.dataframe(
        f[["timestamp", "symbol", "origin_context", "native", "q", "scaled", "N_B1_scaled"]],
        hide_index=True,
        width="stretch",
    )
    for field, label in (
        ("native", "Native B1 log(H/L)"),
        ("q", "q = asinh(x/s)"),
        ("scaled", "Original C0 pooled-MAD B1"),
        ("N_B1_scaled", "N-B1 pooled-MAD input"),
    ):
        fig = go.Figure(go.Scatter(x=f.timestamp, y=f[field], mode="lines+markers", name=label))
        fig.update_layout(height=220, yaxis_title=label, xaxis_title="Completed-hour END (UTC)")
        st.plotly_chart(fig, width="stretch", key="nb1_trace_" + field)
    st.subheader("Whole-population B1 tails and drift")
    distribution_name = (
        "b1_canonical_distributions.csv"
        if "b1_canonical_distributions.csv" in manifest["artifacts"]
        else "b1_distribution_before_after.csv"
    )
    d = table(catalog, manifest, distribution_name)
    st.dataframe(
        d.loc[d.fold.eq(fold) & d.symbol.isin([stock, "POOLED"])], hide_index=True, width="stretch"
    )
    if "b1_histograms.json" in manifest["artifacts"]:
        part = st.selectbox(
            "B1 distribution population",
            ["Development", "Inner training", "Inner validation", "Refit training"],
        )
        histograms = read_json(catalog.root, manifest["artifacts"]["b1_histograms.json"])[
            "histograms"
        ]
        for column, rep in zip(st.columns(2), ("C0", "N-B1")):
            hist = histograms[f"{fold}:{part}:{stock}:{rep}"]
            edges = hist["edges"]
            fig = go.Figure(
                go.Bar(
                    x=[(a + b) / 2 for a, b in zip(edges, edges[1:])],
                    y=hist["counts"],
                    width=[b - a for a, b in zip(edges, edges[1:])],
                )
            )
            fig.update_layout(
                height=240,
                title=rep + " · " + part,
                xaxis_title=rep + " scaled B1",
                yaxis_title="Canonical hourly observations",
            )
            column.plotly_chart(fig, width="stretch", key="nb1_hist_" + rep)
    examples = AuditPacket.discover(catalog).table("feature_replay_examples.csv")
    candidates = examples.loc[
        examples.fold.eq(fold) & examples.feature.eq("B1") & examples.partition.eq("Development")
    ]
    example = candidates.assign(magnitude=candidates.scaled.abs()).sort_values("magnitude").iloc[-1]
    st.button("Show genuine B1 tail candles + 48 steps", on_click=tail_example, args=(example,))
    if "training_curves.csv" in manifest["artifacts"]:
        seed = st.selectbox("N-B1 paired seed", [42, 123], key="nb1_seed")
        curves = table(catalog, manifest, "training_curves.csv")
        for pass_name in ("calibration", "refit"):
            data = curves.loc[
                curves.fold.eq(fold) & curves.seed.eq(seed) & curves.pass_name.eq(pass_name)
            ]
            for metric in ("training_MSE", "validation_MSE", "clipping_fraction"):
                if pass_name == "refit" and metric == "validation_MSE":
                    continue
                fig = go.Figure()
                for arm, group in data.groupby("arm"):
                    fig.add_trace(go.Scatter(x=group.epoch, y=group[metric], name=str(arm)))
                fig.update_layout(height=240, title=pass_name + " · " + metric, xaxis_title="Epoch")
                st.plotly_chart(fig, width="stretch", key="nb1_curve_" + pass_name + metric)
        health = table(catalog, manifest, "gradient_health.csv")
        st.warning(
            "G6 WARNs remain scientific findings; "
            "input compression does not change the target tails."
        )
        st.dataframe(
            health.loc[health.fold.eq(fold) & health.seed.eq(seed)],
            hide_index=True,
            width="stretch",
        )
        if "gradient_comparison.csv" in manifest["artifacts"]:
            comparison = table(catalog, manifest, "gradient_comparison.csv")
            chosen = comparison.loc[comparison.fold.eq(fold) & comparison.seed.eq(seed)]
            st.dataframe(chosen, hide_index=True, width="stretch")
            fig = go.Figure()
            for arm, group in chosen.groupby("arm"):
                fig.add_trace(go.Bar(x=group.pass_name, y=group.preclip_norm_max, name=str(arm)))
            fig.update_layout(
                height=260,
                title="Maximum preclip norm · saved batches",
                yaxis_title="Preclip global gradient norm",
            )
            st.plotly_chart(fig, width="stretch", key="nb1_gradient_max")
    with st.expander("Five-minute guide"):
        path = verified(catalog.root, manifest["artifacts"]["HOW_TO_VIEW_PACKAGE_012B.md"])
        st.markdown(path.read_text())
