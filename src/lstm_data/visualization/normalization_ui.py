"""Lightweight registered Package012A tables in the existing Feature Scaling Explorer."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..ft0_transforms import ORDER
from ..normalization_report import AuditPacket
from ..pretraining_policy import CANDIDATE
from . import figures as charts
from .loaders import Catalog, ViewUnavailable


def open_audit() -> None:
    st.session_state.update(
        section="Controlled Experiments",
        study_view="Feature Scaling Explorer",
        study_fold="WF2",
        study_partition="Development",
        study_dates=(date(2024, 1, 16), date(2024, 1, 19)),
        study_stock="All stocks",
        audit_open=True,
    )


@st.cache_data(max_entries=12, show_spinner=False)
def table(root: str, name: str, token: tuple) -> pd.DataFrame:
    return AuditPacket.discover(Catalog.discover(Path(root))).table(name)


def file_token(packet: AuditPacket, name: str) -> tuple:
    ref = packet.manifest["artifacts"][name]
    path = packet.catalog.root / ref["path"]
    s = path.stat()
    return (ref["sha256"], s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def read_table(packet: AuditPacket, name: str) -> pd.DataFrame:
    return table(str(packet.catalog.root), name, file_token(packet, name))


@st.cache_data(max_entries=2, show_spinner=False)
def histogram_data(root: str, token: tuple) -> dict:
    return AuditPacket.discover(Catalog.discover(Path(root))).json("histograms.json")


def open_example(row: pd.Series) -> None:
    from .history import history_guard

    day = str(row.session)
    consumer = str(row.consuming_session)
    history_guard(day, consumer)
    st.session_state.update(
        section="Price & Features",
        partition="Full data",
        full_stock=str(row.symbol),
        full_jump=date.fromisoformat(day),
        full_dates=(date.fromisoformat(day), date.fromisoformat(consumer)),
        full_origin=int(row.origin),
        full_recipe=str(row.fold)
        + " / "
        + ("inner" if str(row.partition).startswith("Inner") else "refit"),
        full_indicators=[str(row.feature)],
        normalization_example=dict(row),
        normalization_context=False,
        normalization_nb1=False,
        full_selected=dict(
            symbol=str(row.symbol),
            session=consumer,
            cutoff=str(row.consuming_cutoff),
            observation_id="FT0:"
            + str(row.recipe_id)
            + ":"
            + str(row.feature)
            + ":"
            + str(row.symbol)
            + ":"
            + str(row.timestamp),
        ),
    )


def audit_panel(catalog: Catalog) -> None:
    """Grouped distributions and drift are independent of the page's bounded live trace."""
    st.subheader("Package012A · normalization audit")
    packet = AuditPacket.discover(catalog)
    distributions = read_table(packet, "ft0_normalization_distribution.csv")
    a, b = st.columns(2)
    fold = a.selectbox("Audit fold", ["WF1", "WF2"])
    if set(distributions.feature) != set(ORDER):
        raise ViewUnavailable("Audit feature registry incomplete; no fallback.")
    feature = b.selectbox("Audit FT0 channel", list(ORDER))
    partition = st.selectbox(
        "Audit population",
        ["Inner training", "Inner validation", "Refit training", "Development"],
        index=2,
    )
    stock = st.selectbox("Audit stock or pooled", ["POOLED", *CANDIDATE])
    mask = distributions.fold.eq(fold) & distributions.feature.eq(feature)
    chosen = distributions.loc[mask & distributions.partition.eq(partition)]
    selected = chosen.loc[chosen.symbol.eq(stock)]
    st.caption(
        "All canonical unique hourly keys; M2 retains its distinct origin context. "
        "Native and actual float32 scaled units are separate. No alternate fitting, "
        "no target correlations, no Gaussianity goal. Source clock is conditional."
    )
    st.dataframe(selected, hide_index=True, width="stretch")
    st.caption(
        "Source / recipe "
        + str(selected.iloc[0].source_binding)
        + " / "
        + str(selected.iloc[0].recipe_id)
    )
    hist = histogram_data(str(catalog.root), file_token(packet, "histograms.json"))["histograms"]
    for column, representation in zip(st.columns(2), ("native", "scaled")):
        h = next(
            v
            for v in hist
            if v["fold"] == fold
            and v["feature"] == feature
            and v["partition"] == partition
            and v["symbol"] == stock
            and v["representation"] == representation
        )
        edges = h["edges"]
        fig = charts.finish(
            go.Figure(
                go.Bar(
                    x=[(a + b) / 2 for a, b in zip(edges, edges[1:])],
                    y=h["counts"],
                    width=[b - a for a, b in zip(edges, edges[1:])],
                    name=representation,
                )
            ),
            300,
        )
        fig.update_xaxes(title_text=feature + " · dimensionless " + representation)
        fig.update_yaxes(title_text="Canonical observation count")
        column.plotly_chart(fig, width="stretch", key="audit_hist_" + representation)
    st.markdown("**Pooled versus per-stock · identical recipe, no per-stock rescaling**")
    st.dataframe(
        chosen[
            [
                "symbol",
                "representation",
                "observed",
                "ever_model_input_count",
                "median",
                "MAD",
                "IQR",
                "abs_p99",
                "abs_gt_3_rate",
                "abs_gt_10_rate",
            ]
        ],
        hide_index=True,
        width="stretch",
    )
    drift = read_table(packet, "ft0_temporal_drift.csv")
    part = drift.loc[
        drift.fold.eq(fold)
        & drift.feature.eq(feature)
        & drift.symbol.eq(stock)
        & drift.frequency.eq("M" if stock == "POOLED" else "Q")
        & drift.representation.eq("scaled")
    ]
    fig = charts.finish(go.Figure(), 340)
    for label in (
        ("Inner training", "Inner validation")
        if partition.startswith("Inner")
        else ("Refit training", "Development")
    ):
        values = part.loc[part.partition.eq(label)]
        fig.add_trace(
            go.Scatter(x=values.period, y=values["median"], mode="lines+markers", name=label)
        )
    fig.update_xaxes(title_text="Non-overlapping ET month / quarter")
    fig.update_yaxes(title_text=feature + " · scaled median (training recipe fixed)")
    st.plotly_chart(fig, width="stretch", key="audit_drift")
    st.caption(
        "Train and evaluation masks stay separate. Descriptive drift; dependent "
        "stocks/time, no change-point significance or predictive-importance inference."
    )
    parameters = read_table(packet, "ft0_tail_and_fallback_audit.csv")
    prefix = "Inner training" if partition.startswith("Inner") else "Refit training"
    st.dataframe(
        parameters.loc[
            parameters.fold.eq(fold)
            & parameters.feature.eq(feature)
            & parameters.partition.eq(prefix)
        ],
        hide_index=True,
        width="stretch",
    )
    examples = read_table(packet, "feature_replay_examples.csv")
    options = examples.loc[
        examples.fold.eq(fold)
        & examples.feature.eq(feature)
        & examples.partition.eq(partition)
        & examples.ever_model_input
    ]
    if stock != "POOLED":
        options = options.loc[options.symbol.eq(stock)]
    if not options.empty:
        options = options.reset_index(drop=True)
        selected_example = st.selectbox(
            "Open a normalization example",
            range(len(options)),
            format_func=lambda i: (
                f"{options.iloc[i].symbol} / {options.iloc[i].session} / "
                f"{feature} / {options.iloc[i].timestamp}"
            ),
        )
        row = options.iloc[selected_example]
        st.caption(f"Native {row.native!r} · scaled {row.scaled!r} · lineage {row.source_lineage}")
        st.button("Open normalization example", on_click=open_example, args=(row,))
    st.info(
        "012A is read-only. 52 recorded MAD fits, no active fallback; B2/T2/T5 identity. "
        "A synthetic nonzero-constant rounding edge in the SD fallback is disclosed "
        "in the audit; no historical recipe changed. Confirmation remains locked."
    )


def linked_context(catalog: Catalog, token: tuple) -> None:
    """A bounded exact consuming window, including inner-training recipes absent from old scores."""
    row = st.session_state.get("normalization_example")
    if not row or st.session_state.get("full_stock") != row["symbol"]:
        return
    if not st.checkbox(
        "Show normalization example's actual 48-step input context", key="normalization_context"
    ):
        return
    from ..normalization_population import PREFIX
    from .controlled_ui import base
    from .history import history_guard

    history_guard(row["session"], row["consuming_session"])
    # Locate only the bound recipe and registered forecast; never assemble full datasets here.
    from ..pretraining_store import read_preparation
    from ..pretraining_transforms import CandidateView, canonical_population, raw_features
    from .loaders import predictions

    expected = row["fold"] + " / " + PREFIX[row["partition"]]
    dates = st.session_state.get("full_dates", ())
    if (
        st.session_state.get("full_recipe") != expected
        or len(dates) != 2
        or not (
            dates[0].isoformat()
            <= row["session"]
            <= row["consuming_session"]
            <= dates[1].isoformat()
        )
    ):
        st.info("Normalization example context is outside the currently selected window/recipe.")
        return

    store = base(str(catalog.root), token)
    prefix = PREFIX[row["partition"]]
    prep = read_preparation(catalog.root, catalog.config["recipes"][row["fold"]][prefix])
    if prep.preparation_id != row["recipe_id"]:
        raise ViewUnavailable("Example recipe mismatch")
    key = (row["consuming_session"], int(row["origin"]))
    if str(row["partition"]).endswith("training"):
        legal, _ = canonical_population(store, prep.window)
    else:
        saved = predictions(catalog, row["fold"], "TM0", row["partition"])
        legal = tuple(zip(saved.session, saved.origin))
    if key not in legal:
        raise ViewUnavailable("Example outside saved consuming mask")
    positions = store.origin_steps[key]
    view = CandidateView(store, prep)
    floors = next(p for p in prep.floors if p.symbol == row["symbol"])
    records = []
    import numpy as np

    from ..ft0_transforms import ORDER

    j = ORDER.index(row["feature"])
    for pos in positions:
        native, _ = raw_features(store, row["symbol"], pos, int(row["origin"]), floors)
        scaled = view.row(row["symbol"], pos, int(row["origin"]))
        if scaled is None:
            raise ViewUnavailable("Registered input row unavailable")
        records.append(
            dict(
                timestamp=store.history.calendar.steps[pos].end,
                feature=row["feature"],
                native=native[j],
                scaled=float(np.float32(scaled[j])),
            )
        )
    frame = pd.DataFrame(records)
    for mode in ("native", "scaled"):
        st.plotly_chart(
            charts.features(frame, [row["feature"]], mode),
            width="stretch",
            key="normalization_linked_" + mode,
        )
    st.caption(
        "Exact registered consuming forecast "
        + str(key)
        + " / recipe "
        + prep.preparation_id
        + "; 48 endpoints, no future candles or new TG0 computation."
    )
    if st.session_state.get("normalization_nb1") and row["feature"] == "B1":
        from .nb1_ui import handoff, recipe

        r = recipe(catalog, handoff(catalog), row["fold"], prefix)
        if r["original_preparation_id"] != prep.preparation_id:
            raise ViewUnavailable("N-B1 linked context recipe mismatch")
        frame["q"] = np.arcsinh(frame.native.to_numpy(dtype=float) / r["s"])
        frame["N_B1_scaled"] = ((frame.q - r["c"]) / r["a"]).astype(np.float32)
        st.dataframe(frame, hide_index=True, width="stretch")
        for field in ("q", "N_B1_scaled"):
            fig = go.Figure(go.Scatter(x=frame.timestamp, y=frame[field], mode="lines+markers"))
            fig.update_layout(
                height=240, yaxis_title=field, xaxis_title="48 completed-hour ends UTC"
            )
            st.plotly_chart(fig, width="stretch", key="normalization_nb1_" + field)
        st.caption(f"N-B1 s={r['s']!r}; c={r['c']!r}; a={r['a']!r}; recipe {r['recipe_id']}")
