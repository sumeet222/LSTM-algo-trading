"""Fast read-only controlled-study oracles; no fitting or checkpoint inference."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lstm_data.pretraining_policy import CANDIDATE
from lstm_data.stock_source import numeric
from lstm_data.visualization.controlled import (
    OBJECTIVES,
    Study,
    arm_model,
    event_state,
    exact_match,
    label_views,
    paired_table,
)
from lstm_data.visualization.loaders import Catalog, ViewUnavailable, records_frame


@pytest.fixture
def fabricated_panel():
    """Fabricated unit-test observations, never displayed as market data."""
    records = [
        dict(
            session=day,
            origin=o,
            targets=[-3.0, -1.0, 0.0, 2.0, 5.0],
            scores=[-0.3, -0.1, 0.1, 0.3, 0.4],
        )
        for day in ("2023-07-17", "2023-07-18")
        for o in (1, 2)
    ]
    frame = records_frame(records, "C0", "WF1", "Development")
    frame["cutoff"] = (
        pd.to_datetime(frame.session + frame.origin.map({1: " 10:30", 2: " 11:30"}))
        .dt.tz_localize("America/New_York")
        .dt.tz_convert("UTC")
    )
    frame["maturity"] = frame.cutoff + pd.Timedelta(hours=4, minutes=3)
    frame["residual"] = frame.score - frame.TG0
    frame["squared_error"] = frame.residual**2
    return frame


def test_fixed_label_parameters_round_trip_and_no_forecast_inverse():
    t1 = {"policy": {"cap": 3.0}}
    t2 = {"policy": {"scale": 0.9}}
    before = deepcopy((t1, t2))
    values = pd.Series([-84.0, -2.0, 0.0, 2.0, 84.0])
    transformed = label_views(values, t1, t2)
    np.testing.assert_allclose(0.9 * np.sinh(transformed.iloc[:, 2]), values, rtol=1e-14)
    np.testing.assert_array_equal(transformed.iloc[:, 1], [-3.0, -2.0, 0.0, 2.0, 3.0])
    assert (t1, t2) == before
    assert "Huber" in OBJECTIVES["H1"] and "asinh" in OBJECTIVES["T2"]
    with pytest.raises(ViewUnavailable):
        label_views(values, t1, {"policy": {"scale": 0.0}})


@pytest.mark.parametrize("defect", ["duplicate", "mask", "target", "clock"])
def test_exact_masks_fail_closed(fabricated_panel, defect):
    a = fabricated_panel
    b = a.copy()
    if defect == "duplicate":
        b = pd.concat([b, b.iloc[:1]])
    elif defect == "mask":
        b = b.iloc[1:]
    elif defect == "target":
        b.loc[b.index[0], "TG0"] += 1
    else:
        b.loc[b.index[0], "cutoff"] += pd.Timedelta(minutes=1)
    with pytest.raises(ViewUnavailable, match="NOT_COMPARABLE"):
        exact_match(a, b)


def test_paired_metrics_independent_equal_day_oracle(fabricated_panel):
    c = fabricated_panel
    t = c.assign(score=c.score * 2)
    t["squared_error"] = (t.score - t.TG0) ** 2
    table, daily = paired_table(c, t)
    expected = t.groupby(["session", "origin"]).squared_error.mean().groupby(level=0).mean().mean()
    actual = table.set_index("forecast")
    assert actual.at["Treatment", "MSE"] == pytest.approx(expected)
    assert actual.at["ZERO", "daily_Rank_IC"] == 0
    assert actual.at["ZERO", "defined_origins"] == 0
    assert daily.delta_MSE.mean() == pytest.approx(
        numeric(actual.at["Treatment", "MSE"]) - numeric(actual.at["C0", "MSE"])
    )


def test_event_navigation_sets_every_filter_and_rejects_confirmation(fabricated_panel):
    row = fabricated_panel.iloc[3]
    state = event_state(row, "WF1", 123, "T2", "Development")
    assert state["symbol"] == "SBUX"
    assert state["dates"] == (date(2023, 7, 17),) * 2
    assert state["model"] == "T2 [123]" and state["fold"] == "WF1"
    assert state["feature_origin"] == row.origin and state["price_markers"]
    forbidden = row.copy()
    forbidden["session"] = "2024-07-01"
    with pytest.raises(ViewUnavailable, match="permitted history"):
        event_state(forbidden, "WF2", 42, "T2", "Development")
    assert arm_model("C0", 42) == "TM0"
    with pytest.raises(ViewUnavailable):
        arm_model("T2", 999)


@pytest.fixture(scope="module")
def study():
    root = Path(__file__).resolve().parents[1]
    c = Catalog.discover(root)
    if not (root / c.config["baseline"]["path"]).is_file():
        pytest.skip("Provision legitimate saved study artifacts to run local reconciliation")
    return Study.discover(c)


def test_actual_saved_t2_forecasts_are_read_verbatim_once(study):
    frame = study.panel("WF1", 42, "T2", "Development")
    obj = study.catalog.result("WF1", "T2 [42]")
    expected = np.asarray([r["scores"] for r in obj["development"]["origin_records"]]).reshape(-1)
    np.testing.assert_array_equal(frame.score, expected)
    assert len(frame) == 1160 and set(frame.symbol) == set(CANDIDATE)
    p = study.parameter("WF1", "T2", "inner")
    q = study.parameter("WF1", "T2", "refit")
    assert p["parameter_id"] != q["parameter_id"] and p["policy"]["scale"] != q["policy"]["scale"]


def test_actual_o1_applied_cap_and_historical_missingness(study):
    from lstm_data.visualization.loaders import gradient_batches

    b = gradient_batches(study.catalog, "WF1", "O1 [42]", "calibration")
    assert (b.clip_cap == 5).all()
    np.testing.assert_allclose(
        b.clip_multiplier, np.minimum(1.0, 5 / (b.preclip_global_grad_norm + 1e-6))
    )
    assert b.exceeds1.sum() > b.clip_applied.sum()
    trace = study.trace("WF1", 42, "C0")
    assert trace.applied_clipping_fraction.isna().all()
    with pytest.raises(ViewUnavailable, match="Not recorded"):
        gradient_batches(study.catalog, "WF1", "TM0", "calibration")
    h = study.trace("WF1", 42, "H1")
    assert (h.objective_name == "HUBER_DELTA_2").all()
    assert not np.array_equal(h.optimizer_objective, h.training_MSE)


def test_actual_paired_table_reconciles_sealed_delta(study):
    a = study.panel("WF2", 42, "C0", "Development")
    b = study.panel("WF2", 42, "T2", "Development")
    table, _ = paired_table(a, b)
    expected = study.table("paired_fold_seed_comparison.csv")
    row = expected.loc[
        (expected.fold == "WF2") & (expected.seed == 42) & (expected.arm == "T2")
    ].iloc[0]
    assert table.set_index("forecast").at["Treatment", "MSE minus C0"] == pytest.approx(
        row.delta_MSE
    )
    with pytest.raises(ViewUnavailable, match="preconfirmation"):
        study.panel("WF2", 42, "T2", "Confirmation")


def test_confirmation_partition_rejected_before_any_loader(monkeypatch, tmp_path):
    def forbidden(*args, **kwargs):
        raise AssertionError("No result or numeric reader may run")

    monkeypatch.setattr(Catalog, "result", forbidden)
    with pytest.raises(ViewUnavailable, match="preconfirmation"):
        Study(Catalog(tmp_path, {}), {}).panel("WF2", 42, "T2", "Confirmation")


def test_actual_streamlit_study_and_event_drilldown(study):
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(
        str(study.catalog.root / "apps/track_a_dashboard.py"), default_timeout=90
    ).run()
    assert not app.exception and not app.error
    next(x for x in app.button if x.label == "Package 011: Compare C0 and T2").click().run()
    assert not app.exception and not app.error
    assert len(app.get("plotly_chart")) == 4
    next(x for x in app.radio if x.label == "Study view").set_value("Extreme Events").run()
    next(x for x in app.checkbox if x.label.startswith("Use full recorded partition")).check().run()
    next(x for x in app.button if x.label == "Inspect on Price & Features").click().run()
    assert not app.exception and not app.error
    assert app.session_state["symbol"] == "SBUX"
    assert app.session_state["dates"] == (date(2023, 11, 17),) * 2
    assert app.session_state["origin_label"] == "11:30 ET"
    assert app.session_state["model"] == "T2 [42]"
    assert app.session_state["price_markers"]
    next(
        x for x in app.checkbox if x.label == "Open read-only Feature Scaling Explorer"
    ).check().run()
    assert not app.exception and not app.error
    assert len(app.get("plotly_chart")) == 6
