"""Pre-I/O independent locks and actual saved two-run dashboard integration."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lstm_data.config import digest
from lstm_data.hf20_source import SYMBOLS
from lstm_data.hf20_training_authority import IDS
from lstm_data.visualization.hf20 import CONFIG, feature_history, guard, handoff, predictions
from lstm_data.visualization.loaders import ViewUnavailable

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "start,end,symbol,run",
    [
        ("2026-01-07", "2026-01-08", "AAPL", IDS[0]),
        ("2025-04-10", "2026-10-15", "AAPL", IDS[1]),
        ("2025-04-10", "2025-04-10", "COST", IDS[0]),
        ("2025-04-10", "2025-04-10", "AAPL", "TA011-T2-TG0"),
        ("2025-04-10", "2025-04-09", "AAPL", IDS[0]),
    ],
)
def test_forbidden_request_denied_before_numerical_io(monkeypatch, start, end, symbol, run):
    def fail(*args, **kwargs):
        raise AssertionError("Numerical I/O before guard")

    monkeypatch.setattr(pd, "read_csv", fail)
    with pytest.raises(ViewUnavailable):
        predictions(Path("/absent"), start, end, symbol, run)


def test_all20_fixed_names_are_allowed_and_legacy_dates_independent():
    for symbol in SYMBOLS:
        guard("2025-04-10", "2026-01-06", symbol, IDS[0])
    from lstm_data.visualization.loaders import date_window

    date_window("2024-06-28", "2024-06-28")
    with pytest.raises(ViewUnavailable):
        date_window("2025-04-10", "2025-04-10")
    with pytest.raises(ViewUnavailable):
        guard("2024-06-28", "2024-06-28", "AAPL", IDS[0])


@pytest.mark.parametrize(
    "field,value",
    [
        ("target_id", "TG0"),
        ("symbols", list(reversed(SYMBOLS))),
        ("T2_saved_inverse_count", 2),
        ("source_revision", "WRONG"),
        ("heldout_numeric_rows", 1),
    ],
)
def test_wrong_family_order_inverse_deny(tmp_path, field, value):
    (tmp_path / "configs").mkdir()
    h: dict = dict(
        target_id="TG20_HF20_CROSS_SECTIONAL_V1",
        symbols=list(SYMBOLS),
        runs=list(IDS),
        score_units="CANONICAL_TG20",
        T2_saved_inverse_count=1,
        heldout_numeric_rows=0,
        source_revision="PINNED",
        feature_id="FT1",
        clock_id="CLOCK",
    )
    contract = dict(h)
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(contract))
    h["input_contract"] = dict(path=path.name, sha256=digest(path))
    h[field] = value
    path = tmp_path / "handoff.json"
    path.write_text(json.dumps(h))
    (tmp_path / CONFIG).write_text(
        json.dumps(dict(handoff=dict(path=path.name, sha256=digest(path))))
    )
    with pytest.raises(ViewUnavailable):
        handoff(tmp_path)


def actual():
    if not (ROOT / CONFIG).exists():
        pytest.skip("Actual two-pair handoff not yet released")
    return handoff(ROOT)


def test_actual_two_run_selections_exact_targets_and_no_second_inverse():
    h = actual()
    for run in IDS:
        _, full, subset = predictions(ROOT, "2025-04-10", "2026-01-06", "AAPL", run)
        assert len(full) == 7320 and len(subset) == 366
        assert set(full.symbol) == set(SYMBOLS) and full.source_key.is_unique
        arm = "T2" if run == IDS[1] else "C0"
        result_path = ROOT / h["run_artifacts"][arm]["run_result"]["path"]
        saved = pd.read_csv(
            result_path.parent / "predictions_development.csv", float_precision="round_trip"
        )
        assert np.array_equal(full[arm], saved.score)
        assert np.array_equal(full.target, saved.target)
    assert h["T2_saved_inverse_count"] == 1


def test_actual_genuine48_feature_and_source_example():
    h = actual()
    e = h["example"]
    features, candles, clocks = feature_history(ROOT, h, e["symbol"], e["session"], e["origin"])
    assert len(features) == 48 * 16 and features.feature.nunique() == 16
    assert features.step.nunique() == 48 and not candles.empty
    assert np.isfinite(features[["native", "scaled"]]).all().all()
    assert candles.datetime.max() < pd.Timestamp("2026-01-07", tz="America/New_York")
    assert pd.Timestamp(clocks["forecast_issuance_UTC"]) - pd.Timestamp(
        clocks["feature_cutoff_UTC"]
    ) == pd.Timedelta(minutes=2)
    assert pd.Timestamp(clocks["exit_proxy_reference_UTC"]) - pd.Timestamp(
        clocks["entry_proxy_reference_UTC"]
    ) == pd.Timedelta(hours=4)


def test_actual_streamlit_two_run_selections_and_legacy_route():
    actual()
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(ROOT / "apps/track_a_dashboard.py"), default_timeout=60).run()
    assert not app.exception
    assert "HF20: TM0 vs T2" in app.sidebar.radio[0].options
    assert "Controlled Experiments" in app.sidebar.radio[0].options
    app.sidebar.radio[0].set_value("HF20: TM0 vs T2").run()
    assert not app.exception
    for run in IDS:
        app.selectbox(key="hf20_run").set_value(run).run()
        assert not app.exception
        assert len(app.get("plotly_chart")) >= 10
        assert set(app.selectbox(key="hf20_stock").options) == set(SYMBOLS)
    app.button(key="hf20_load_features").click().run()
    assert not app.exception
    assert len(app.get("plotly_chart")) >= 14
    assert not any("SOURCE/CHRONOLOGY HOLD" in w.value for w in app.warning)
    app.selectbox(key="hf20_channel").set_value("M2").run()
    assert not app.exception
    assert len(app.get("plotly_chart")) >= 14
    app.sidebar.radio[0].set_value("Start Here").run()
    assert not app.exception
