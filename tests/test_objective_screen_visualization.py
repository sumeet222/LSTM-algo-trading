"""P022 protected-before-read guards and actual existing-app routes."""

from pathlib import Path
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

from lstm_data.visualization.objective_screen import CONFIG, Screen, safe_features
from lstm_data.visualization.objective_screen_ui import SECTION

ROOT = Path(__file__).resolve().parents[1]


def test_p022_guards_precede_file_or_feature_access() -> None:
    screen = Screen(ROOT, {}, "test", {})
    with patch.object(Screen, "file", side_effect=AssertionError("numeric access")):
        with pytest.raises(ValueError):
            screen.filtered("H2", "development", "AAPL", "2026-01-01", "2026-01-02")
        with pytest.raises(ValueError):
            screen.population("H2", "confirmation")
        with pytest.raises(ValueError):
            screen.population("legacy-alpaca", "refit")
    with patch(
        "lstm_data.visualization.objective_screen.LongStudy.table",
        side_effect=AssertionError("numeric access"),
    ):
        from lstm_data.visualization.hf1m_long import LongStudy

        study = LongStudy(ROOT, {}, {}, ROOT, {}, "test")
        with pytest.raises(ValueError):
            safe_features(study, "AAPL", "2026-01-01", "2026-01-02", "refit", 1)


@pytest.mark.skipif(not (ROOT / CONFIG).exists(), reason="Private completed P022 release required")
def test_actual_p022_all_model_views_and_legacy_preservation() -> None:
    app = AppTest.from_file(str(ROOT / "apps/track_a_dashboard.py"), default_timeout=60)
    app.session_state["section"] = SECTION
    app.run()
    assert not app.exception and not app.error
    for model in ("H2", "W1", "E1", "R1"):
        app.selectbox(key="p022_model").select(model)
        for view in (
            "Matched Comparisons",
            "Training / Gradients",
            "Objective Tail Attribution",
            "Exact Event Cases",
        ):
            app.selectbox(key="p022_view").select(view).run()
            assert not app.exception and not app.error, (model, view)
    for view in ("Feature / Event Audit", "History / 16 Features", "Guide"):
        app.selectbox(key="p022_view").select(view).run()
        assert not app.exception and not app.error, view
    app.query_params["start"] = "2026-01-01"
    app.run()
    assert not app.exception and app.error
    app.query_params.clear()
    app.session_state["section"] = "HF1M Long — 20 stocks (2010–2025)"
    app.run()
    assert not app.exception and not app.error


@pytest.mark.skipif(not (ROOT / CONFIG).exists(), reason="Private completed P022 release required")
def test_actual_all_roles_and_full_population_filter() -> None:
    screen = Screen.discover(ROOT)
    for model in ("H2", "W1", "E1", "R1", "T2_42", "T2_123", "ZERO"):
        for role, count in [
            ("inner_train", 88560),
            ("inner_validation", 15320),
            ("refit", 104200),
            ("development", 3660),
        ]:
            f = screen.population(model, role)
            assert len(f) == count
            assert f.groupby("origin_id").size().eq(20).all()
        f = screen.filtered(model, "refit", "CSCO", "2025-06-01", "2025-06-30")
        assert len(f) > 0 and f.ticker.eq("CSCO").all()
