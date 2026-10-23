"""P021 full-population filters, protected barrier and real local component-state checks."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from lstm_data.hf1m_action_audit import SYMBOLS
from lstm_data.hf1m_training_authority import IDS
from lstm_data.hf1m_training_diagnostics import daily_metrics, origin_metrics, summary
from lstm_data.visualization.hf1m_long import LongStudy, select_events
from lstm_data.visualization.hf1m_long_ui import SECTION, VIEWS


def population() -> pd.DataFrame:
    rows = []
    for k in range(120):
        for j, s in enumerate(SYMBOLS):
            y = (j - 9.5) * (1 + k / 100)
            rows.append(
                dict(
                    ticker=s,
                    origin_id=f"origin{k:03d}",
                    session_date_et="2020-01-02" if k < 2 else "2020-01-03",
                    TG20=y,
                    actual_TG20=y,
                    pred_original_TG20=0.2 * y,
                    return_4h=y * 0.001,
                    numerator=y * 0.001,
                    cross_section_mad=0.0001 * (k + 1),
                    denominator=0.001 + 0.0001 * (k + 1),
                    tail_class="neither",
                    large_numerator=False,
                    small_mad=False,
                    target_p99=False,
                )
            )
    return pd.DataFrame(rows)


def test_filter_search_and_sort_cover_rows_beyond_first30() -> None:
    f = population()
    result = select_events(f, "Largest |TG20|", ticker="CSCO", search="origin119")
    assert len(result) == 1 and result.origin_id.iloc[0] == "origin119"
    assert select_events(f, "Largest |numerator|").origin_id.iloc[0] == "origin119"
    origins = select_events(f, "Smallest raw MAD")
    assert len(origins) == 120 and not origins.origin_id.duplicated().any()


def test_weighted_zero_decomposition_and_ic_independent_oracles() -> None:
    source = population()
    f = source.loc[source.origin_id.isin(["origin000", "origin001", "origin002"])].copy()
    result = summary(f)
    day_mse = (
        f.assign(loss=(f.pred_original_TG20 - f.actual_TG20) ** 2)
        .groupby("session_date_et")
        .loss.mean()
        .mean()
    )
    assert result["mse"] == pytest.approx(day_mse)
    assert result["mse"] - result["zero_mse"] == pytest.approx(
        result["prediction_squared"] - result["twice_target_prediction"]
    )
    assert np.allclose(origin_metrics(f).rank_ic, 1)
    assert np.allclose(daily_metrics(f).top4_recall, 1)
    f["pred_original_TG20"] = 0.0
    assert origin_metrics(f).rank_ic.isna().all()


def test_protected_readers_reject_before_filesystem() -> None:
    s = LongStudy(Path("does-not-exist"), {}, {}, Path("does-not-exist"), {}, "test")
    with pytest.raises(ValueError, match="protected"):
        s.history("AAPL", "2026-01-01", "2026-01-02")
    with pytest.raises(ValueError, match="protected"):
        s.features("AAPL", "2025-12-31", "2026-01-01", "refit", 1)
    with pytest.raises(ValueError, match="protected"):
        s.targets("confirmation")
    with pytest.raises(ValueError, match="protected"):
        s.prediction(IDS[0], "confirmation")


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_revision", "ad48edaf3828ec855ab4a5bb1b8336fa0b68cdec"),
        ("symbols", list(reversed(SYMBOLS))),
        ("runs", ["HF20-TM0-C0-S42-DEV1"]),
    ],
)
def test_old_source_stock_order_or_run_denied_before_numerics(
    tmp_path: Path, field: str, value: str | list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    from lstm_data.config import digest
    from lstm_data.hf1m_action_audit import REVISION
    from lstm_data.visualization.hf1m_long import CONFIG

    p = dict(protected_refs=[], runs=list(IDS), symbols=list(SYMBOLS), source_revision=REVISION)
    p[field] = value
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps(p))
    config = tmp_path / CONFIG
    config.parent.mkdir(parents=True)
    config.write_text(json.dumps(dict(plan=dict(path="plan.json", sha256=digest(plan)))))

    def denied(*args: object, **kwargs: object) -> None:
        raise AssertionError("numerical reader called before identity rejection")

    monkeypatch.setattr(pd, "read_parquet", denied)
    monkeypatch.setattr(np, "load", denied)
    with pytest.raises(ValueError, match="source/run/order"):
        LongStudy.discover(tmp_path)


def test_wrong_phase_scaler_and_old_checkpoint_denied_before_weight_load(tmp_path: Path) -> None:
    from lstm_data.hf1m_ft16_loader import load_model_input
    from lstm_data.hf20_training_run import reload_checkpoint

    with pytest.raises(ValueError, match="SPLIT_FIT_MISMATCH"):
        load_model_input(tmp_path / "no-file", split="inner_validation", fit_version="refit")
    with pytest.raises(ValueError, match="SOURCE_TARGET_ORDER_STAGE_SCALE"):
        reload_checkpoint(
            tmp_path / "no-weights.pt",
            {"source_revision": "HF1M"},
            {"binding": {"source_revision": "TWELVE_DATA"}},
        )


@pytest.fixture
def app() -> AppTest:
    path = Path(
        "data/processed/hf20_hf1m_long_v1_ft16_v1/ta020_hf1m_long_ft16_tg20_2026-10-22_211122"
    )
    if not path.exists():
        pytest.skip("exact P020 private research stores not provisioned on this machine")
    a = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "apps/track_a_dashboard.py", default_timeout=90
    )
    a.session_state["section"] = SECTION
    return a


def test_real_target_ui_full_population_extremes_and48steps(app: AppTest) -> None:
    app.session_state["hf1m_view"] = VIEWS[1]
    app.run()
    assert not app.exception and not app.error
    assert len(app.selectbox(key="hf1m_target_stock").options) == 21
    assert len(app.multiselect(key="hf1m_event_feature_channels").options) == 16
    matrix = app.dataframe[-3].value
    assert any(d.value.shape == (48, 16) for d in app.dataframe)
    assert matrix is not None
    app.selectbox(key="hf1m_event_mode").select("Smallest raw MAD").run()
    assert not app.exception and not app.error
    app.selectbox(key="hf1m_target_role").select("development").run()
    assert not app.exception and not app.error
    assert any("3,660" in m.value for m in app.markdown)


def test_real_history20stocks_and16features(app: AppTest) -> None:
    app.session_state["hf1m_view"] = VIEWS[0]
    app.run()
    assert not app.exception and not app.error
    assert app.selectbox(key="hf1m_history_stock").options == list(SYMBOLS)
    assert len(app.multiselect(key="hf1m_history_feature_channels").options) == 16
    app.selectbox(key="hf1m_history_stock").select("CSCO").run()
    assert not app.exception and not app.error


@pytest.mark.parametrize("view", VIEWS)
def test_protected_url_denied_on_every_view_before_data(app: AppTest, view: str) -> None:
    app.session_state["hf1m_view"] = view
    app.query_params["start"] = "2026-01-01"
    app.run()
    assert not app.exception
    assert any("protected" in e.value for e in app.error)
    assert len(app.dataframe) == 0


def test_remaining_view_states_before_training(app: AppTest) -> None:
    for view in VIEWS[2:]:
        app.session_state["hf1m_view"] = view
        app.run()
        assert not app.exception
        if view in VIEWS[2:4]:
            # Missing predictions are explicit errors, never another study's fallback.
            assert all("artifact unavailable" in e.value for e in app.error)
            if view == VIEWS[2]:
                assert len(app.multiselect(key="hf1m_training_runs").options) == 4
        else:
            assert not app.error
            if view == VIEWS[4]:
                assert any("terminal_input_age_p95_minutes" in d.value for d in app.dataframe)


def test_completed_four_run_views_and_all_prediction_roles(app: AppTest) -> None:
    study = LongStudy.discover(Path.cwd())
    try:
        for name in IDS:
            study.run_result(name)
    except (OSError, ValueError):
        pytest.skip("four exact completed local candidate runs are not provisioned")
    app.session_state["hf1m_view"] = VIEWS[2]
    app.run()
    assert not app.exception and not app.error
    epochs = app.dataframe[-1].value
    assert set(epochs.run_id) == set(IDS) and len(epochs) == 63
    app.session_state["hf1m_view"] = VIEWS[3]
    app.run()
    assert not app.exception and not app.error
    charts = [str(chart.proto) for chart in app.get("plotly_chart")]
    for key in (
        "hf1m_forecast_timeseries",
        "hf1m_residual_timeseries",
        "hf1m_prediction_identity_scatter",
        "hf1m_mse_by_target_bin",
        "hf1m_ic_heatmap",
    ):
        assert any(key in chart for chart in charts), key
    assert len(app.selectbox(key="hf1m_forecast_detail_stock").options) == 20
    for split, count in (
        ("development", 3660),
        ("inner_train", 88560),
        ("inner_validation", 15320),
        ("refit", 104200),
    ):
        app.selectbox(key="hf1m_prediction_role").select(split).run()
        assert not app.exception and not app.error
        summaries = [
            d.value for d in app.dataframe if {"run_id", "mse", "rows"}.issubset(d.value.columns)
        ]
        assert any(len(f) == 4 and f.rows.eq(count).all() for f in summaries)
