"""Saved four-model comparison in the existing HF20 route; no inference or fitting."""

from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from .hf20 import REPLICATION_CONFIG, handoff, table, verified


def comparison_panel(root: Path) -> None:
    if not (root / REPLICATION_CONFIG).exists():
        st.info("Seed123 TRAINING_HOLD / results not released. Seed42 evidence remains available.")
        return
    h = handoff(root, 123)
    st.warning(
        "Exploratory paired development; five-session intervals are not selection-adjusted "
        "G8. Two seeds share one market history. No significance, promotion or trading claim."
    )
    st.dataframe(table(root, h, "four_model_metrics.csv"), hide_index=True, width="stretch")
    st.dataframe(table(root, h, "paired_intervals.csv"), hide_index=True, width="stretch")
    st.dataframe(table(root, h, "mse_decomposition.csv"), hide_index=True, width="stretch")
    st.dataframe(table(root, h, "epoch_selection_trace.csv"), hide_index=True, width="stretch")
    st.dataframe(table(root, h, "tail_event_metrics.csv"), hide_index=True, width="stretch")
    first = table(root, handoff(root, 42), "matched_predictions_development.csv")
    second = table(root, h, "matched_predictions_development.csv")
    keys = ["source_key", "session", "origin", "symbol", "target"]
    if not first[keys].equals(second[keys]):
        raise ValueError("HF20 exact four-model keys differ; intersection prohibited")
    for arm in ("C0", "T2"):
        fig = go.Figure(
            go.Scattergl(
                x=first[arm],
                y=second[arm],
                mode="markers",
                marker=dict(size=3, opacity=0.25),
                name=arm,
            )
        )
        limits = [
            float(min(first[arm].min(), second[arm].min())),
            float(max(first[arm].max(), second[arm].max())),
        ]
        if not np.isfinite(limits).all():
            raise ValueError("HF20 nonfinite saved scatter")
        fig.add_trace(go.Scatter(x=limits, y=limits, mode="lines", name="Equal score"))
        fig.update_layout(
            title=arm + " · same 7320 forecast IDs",
            xaxis_title="Seed42 canonical TG20",
            yaxis_title="Seed123 canonical TG20",
        )
        st.plotly_chart(fig, width="stretch", key="hf20_seed_scatter_" + arm)
    st.markdown(verified(root, h["researcher_diagnosis"]).read_text())
