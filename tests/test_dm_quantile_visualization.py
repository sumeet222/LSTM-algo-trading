"""Actual P023 components, source guards and preserved prior explorer navigation."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/track_a_p023_visualization_v1.json"


@pytest.mark.skipif(not CONFIG.exists(), reason="Completed private P023 release required")
def test_all_three_model_views_and_prior_navigation() -> None:
    from lstm_data.visualization.dm_quantile_ui import SECTION

    a = AppTest.from_file(str(ROOT / "apps/track_a_dashboard.py"), default_timeout=90)
    a.session_state["section"] = SECTION
    a.run()
    assert not a.exception and not a.error
    for model in ["DM1", "QR1", "SS1"]:
        a.selectbox(key="p023_model").select(model)
        for view in [
            "Comparisons",
            "Optimization / Gradients",
            "Head Outputs",
            "Actual-Objective Tails",
            "Exact Cases",
        ]:
            a.selectbox(key="p023_view").select(view).run()
            assert not a.exception and not a.error, (model, view, [e.value for e in a.error])
    for view in ["History / Features", "Guide"]:
        a.selectbox(key="p023_view").select(view).run()
        assert not a.exception and not a.error
    a.query_params["start"] = "2026-01-01"
    a.run()
    assert a.error and not a.exception
    a.query_params.clear()
    a.session_state["section"] = "HF1M Long — Objective Improvement Screen (P022)"
    a.run()
    assert not a.exception and not a.error
    a.session_state["section"] = "HF1M Long — 20 stocks (2010–2025)"
    a.run()
    assert not a.exception and not a.error
