"""P024 completed numerical views and date/role barriers before any artifact access."""

import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from lstm_data.config import digest
from lstm_data.hf1m_action_audit import SYMBOLS
from lstm_data.visualization.optimization_screen_ui import ARMS, SECTION, VIEWS, OptimizationStudy

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/track_a_p024_visualization_v1.json"


def test_other_source_manifest_is_rejected_before_numerics(tmp_path: Path, monkeypatch) -> None:
    def denied(*args, **kwargs):
        raise AssertionError("Wrong source reached a numerical artifact")

    monkeypatch.setattr("pandas.read_parquet", denied)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            dict(
                status="PASS_COLLECTIVE_P024",
                ledger=51,
                source_contract=dict(path="wrong.json", sha256="0" * 64),
                files={},
            )
        )
    )
    config = tmp_path / "configs/track_a_p024_visualization_v1.json"
    config.parent.mkdir()
    config.write_text(
        json.dumps(dict(manifest=dict(path="manifest.json", sha256=digest(manifest))))
    )
    with pytest.raises(ValueError, match="source contract"):
        OptimizationStudy.discover(tmp_path)


def test_protected_requests_are_rejected_before_file_access(monkeypatch) -> None:
    def denied(*args, **kwargs):
        raise AssertionError("A protected request reached a numerical artifact")

    monkeypatch.setattr(OptimizationStudy, "table", denied)
    study = OptimizationStudy(ROOT, {}, "test", {})
    for arm in ARMS:
        with pytest.raises(ValueError):
            study.population(arm, "confirmation")
        with pytest.raises(ValueError):
            study.filtered(arm, "development", "AAPL", "2026-01-01", "2026-03-31")
    with pytest.raises(ValueError):
        study.population("UNAPPROVED", "development")


@pytest.mark.skipif(not CONFIG.exists(), reason="Completed private P024 release required")
def test_all_arms_views_stock_history_and_prior_navigation() -> None:
    app = AppTest.from_file(str(ROOT / "apps/track_a_dashboard.py"), default_timeout=90)
    app.session_state["section"] = SECTION
    app.run()
    assert not app.exception and not app.error
    for arm in ARMS:
        app.selectbox(key="p024_arm").select(arm)
        for view in VIEWS:
            app.selectbox(key="p024_view").select(view).run()
            assert not app.exception and not app.error, (arm, view, [e.value for e in app.error])
            if view == "Comparisons":
                figures = [json.loads(element.proto.spec) for element in app.get("plotly_chart")]
                assert len(figures) == 2
                assert "Original TG20 MSE" in figures[0]["layout"]["title"]["text"]
                assert set(figures[0]["data"][0]["x"]) == set(ARMS) | {"T2/42", "T2/123", "ZERO"}
                assert "ZERO undefined" in figures[1]["layout"]["title"]["text"]
            if view == "Exact Cases":
                figure = json.loads(app.get("plotly_chart")[0].proto.spec)
                assert figure["data"][0]["type"] == "candlestick"
                assert figure["layout"]["shapes"][0]["line"]["dash"] == "dash"
            if arm == ARMS[0]:
                app.query_params["date"] = "2026-02-01"
                app.run()
                assert app.error and not app.exception, ("protected route", view)
                app.query_params.clear()
                app.run()
                assert not app.exception and not app.error
    app.selectbox(key="p024_view").select("History / Features").run()
    for ticker in SYMBOLS:
        next(s for s in app.selectbox if s.label == "P024 history stock").select(ticker).run()
        assert not app.exception and not app.error, ticker
    app.selectbox(key="p024_view").select("Forecasts / Residuals").run()
    next(s for s in app.selectbox if s.label == "P024 output stock").select("AAPL").run()
    assert not app.exception and not app.error
    for split in ("inner_train", "inner_validation", "refit", "development"):
        app.selectbox(key="p024_role").select(split).run()
        assert not app.exception and not app.error, split
    app.query_params["start"] = "2026-01-01"
    app.run()
    assert app.error and not app.exception
    app.query_params.clear()
    for section in (
        "HF1M Long — Direction / Quantiles / Sampling (P023)",
        "HF1M Long — Objective Improvement Screen (P022)",
        "HF1M Long — 20 stocks (2010–2025)",
        "Start Here",
    ):
        app.session_state["section"] = section
        app.run()
        assert not app.exception and not app.error, section
