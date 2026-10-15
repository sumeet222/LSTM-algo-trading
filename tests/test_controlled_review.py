"""Fabricated observer reconstruction and canonical artifact adapter boundaries."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import torch

from lstm_data.batch_telemetry import BatchTelemetry
from lstm_data.controlled_review import audit_batches, finish_frame
from lstm_data.neural_engine import SessionBatch, session_batches
from lstm_data.visualization import figures
from lstm_data.visualization.loaders import Catalog, ViewUnavailable


def test_batch_audit_is_session_weighted_and_rejects_wrong_norm_scale(tmp_path: Path):
    from unittest.mock import Mock

    from lstm_data.real_bridge_data import RealInputView

    # Audit needs only the already-bound sessions/rows; no fabricated market store.
    view = Mock(spec=RealInputView)
    view.sessions = ("SYN:A", "SYN:B")
    view.rows = (1, 2, 3)
    positions = next(session_batches(2, 42, 1, shuffle=True))
    ids = tuple(view.sessions[i] for i in positions)
    origins = torch.tensor([[True, True], [True, False]])
    batch = SessionBatch(ids, torch.zeros(2, 2, 5, 48, 16), torch.zeros(2, 2, 5), origins)
    path = tmp_path / "batches.csv"
    BatchTelemetry(path, "SYN:PAIR", "TM0", "CALIBRATION", arm="O1", cap=5).record(
        1, 1, batch, torch.tensor([1.0, 2.0]), 3.0
    )
    stats, rows = audit_batches(path, [dict(epoch=1, steps=1, mse=1.5)], view, 42, 5.0)
    assert stats["fraction_above1"] == 1 and stats["fraction_above5"] == 0
    assert stats["applied_clip_fraction"] == 0 and rows[0]["passed"]
    frame = pd.read_csv(path)
    frame["clip_multiplier"] = 0.1
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError, match="SINGLE_CLIP"):
        audit_batches(path, [dict(epoch=1, steps=1, mse=1.5)], view, 42, 5.0)


def test_partial_or_protected_panel_rejected_before_reporting():
    frame = pd.DataFrame(
        dict(session=["2024-07-01"], origin=[1], symbol=["AAPL"], TG0=[0.0], score=[0.0])
    )
    with pytest.raises(ValueError, match="EXACT_OUTER"):
        finish_frame(frame, "T2", 42, "WF2")


def test_controlled_names_and_applied_cap_plot_keep_legacy_choices():
    catalog = Catalog(
        Path.cwd(),
        dict(
            models=dict(WF1=dict(TM0={}, MC0={})),
            controlled_models=dict(WF1={"O1 [42]": dict(arm="O1", seed=42)}),
        ),
    )
    assert catalog.model_names("WF1")[:3] == ("TM0", "MC0", "O1 [42]")
    with pytest.raises(ViewUnavailable):
        catalog.require("FIT")
    frame = pd.DataFrame(
        dict(
            batch_session_weighted_MSE=[1.0, 2.0],
            preclip_global_grad_norm=[2.0, 4.0],
            target_abs_max=[8.0, 9.0],
            epoch=[1, 1],
            batch_index=[1, 2],
            session_ids=["SYN:A", "SYN:B"],
            clip_cap=[5.0, 5.0],
        )
    )
    chart = figures.gradient_scatter(frame)
    assert {shape["y0"] for shape in chart.to_plotly_json()["layout"]["shapes"]} == {1, 5}


def test_saved_t2_canonical_scores_and_t1_extremes_are_never_transformed_again(
    tmp_path: Path, monkeypatch
):
    from lstm_data.pretraining_policy import CANDIDATE
    from lstm_data.visualization.loaders import predictions

    c = Catalog(
        tmp_path,
        dict(
            models={"WF1": {"T2 [42]": {}}},
            controlled_models={"WF1": {"T2 [42]": dict(arm="T2", seed=42)}},
            development_windows={"WF1": ["2023-07-01", "2023-12-31"]},
        ),
    )
    scores = [-0.9, -0.1, 0.0, 0.3, 1.2]
    targets = [-82.0, -1.0, 0.0, 1.0, 82.0]
    result = dict(
        development=dict(
            origin_records=[dict(session="2023-07-12", origin=1, scores=scores, targets=targets)]
        )
    )
    monkeypatch.setattr(Catalog, "result", lambda *args: result)
    frame = predictions(c, "WF1", "T2 [42]", "Development")
    assert frame.symbol.tolist() == list(CANDIDATE)
    assert frame.score.tolist() == scores and frame.TG0.tolist() == targets
