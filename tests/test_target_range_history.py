"""Focused Package010C software oracles; never train or inspect confirmation numerics."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pyarrow.parquet as pq
import pytest

from lstm_data.pretraining_store import read_preparation
from lstm_data.visualization import history, loaders
from lstm_data.visualization.controlled import Study, input_context
from lstm_data.visualization.target_ranges import (
    TargetRange,
    denominator_comparison,
    ordered,
    page_rows,
    retained_selection,
    target_spec,
)


@pytest.fixture(scope="module")
def real():
    c = loaders.Catalog.discover(Path(__file__).resolve().parents[1])
    if not (c.root / c.config["baseline"]["path"]).is_file():
        pytest.skip("Provision legitimately accessible existing source/study artifacts")
    b = loaders.component_base(c)
    s = Study.discover(c)
    frame = target_spec("TG0").decomposition(s, b, "WF1", "Full refit prefix", 42)
    return c, b, s, frame


@pytest.mark.parametrize("lo,hi", [("nan", ""), ("", "inf"), ("abc", ""), ("3", "2")])
def test_range_invalid_bounds(lo, hi):
    with pytest.raises(loaders.ViewUnavailable):
        TargetRange.parse("Signed", lo, hi, True, True)


def test_range_edges_signed_empty_and_nonfinite():
    frame = pd.DataFrame({"TG0": [-2.0, -1.0, 0.0, 1.0, 2.0, np.nan, np.inf]})
    spec = target_spec("TG0")
    assert TargetRange("Signed", -2, 2).select(frame, spec).TG0.tolist() == [-2, -1, 0, 1, 2]
    assert TargetRange("Signed", -2, 0, False, False).select(frame, spec).TG0.tolist() == [-1]
    assert TargetRange("Absolute", 1, 2, False, False).select(frame, spec).empty
    assert TargetRange.parse("Absolute", "", "2", True, False).select(frame, spec).TG0.tolist() == [
        -1,
        0,
        1,
    ]
    assert len(TargetRange.parse("Signed", "", "", True, True).select(frame, spec)) == 5


def test_registry_never_falls_back():
    assert target_spec("TG0").horizon_full_hours == 4
    with pytest.raises(loaders.ViewUnavailable, match="NOT_IMPLEMENTED"):
        target_spec("TG7")


def test_full_relation_counts_and_every_page_independent_oracle(real):
    _, base, study, frame = real
    prep = read_preparation(study.catalog.root, study.catalog.config["recipes"]["WF1"]["refit"])
    keys = study.training_targets(base, "WF1", "refit")
    # Independent immutable panel calculation, rather than reading range status or its output.
    expected = []
    for r in keys.itertuples():
        p = base.panels[str(r.session), int(r.origin)]
        values = np.asarray(p.returns, dtype=float)
        center = np.median(values)
        mad = np.median(np.abs(values - center))
        from lstm_data.pretraining_policy import CANDIDATE

        j = CANDIDATE.index(str(r.symbol))
        expected.append((values[j] - center) / (mad + prep.target_epsilon))
    np.testing.assert_allclose(frame.TG0, expected, rtol=0, atol=0)
    assert len(frame) == 7510
    assert np.sum(np.abs(expected) > 1) == 2860
    assert np.sum(np.abs(expected) > 10) == 67
    spec = target_spec("TG0")
    for limit, count in ((1, 2860), (10, 67)):
        matches = TargetRange("Absolute", limit, include_lower=False).select(frame, spec)
        assert len(matches) == count
        for sort in ("Absolute target", "Signed target", "Date", "Stock", "Origin"):
            sorted_rows = ordered(matches, sort, False)
            _, total = page_rows(sorted_rows, 1, 50)
            identities = []
            for page in range(1, total + 1):
                part, _ = page_rows(sorted_rows, page, 50)
                assert part.TG0.abs().gt(limit).all()
                identities.extend(part.observation_id)
            assert len(identities) == len(set(identities)) == count
            assert set(identities) == set(matches.observation_id)
    ordinary = TargetRange("Absolute", upper=2, include_upper=False).select(frame, spec)
    negative = TargetRange("Signed", -2, -1).select(frame, spec)
    assert len(ordinary) > 5000 and not negative.empty and negative.TG0.lt(0).all()
    selected = str(ordinary.iloc[0].observation_id)
    assert retained_selection(ordered(ordinary, "Date", True), selected) == selected
    assert retained_selection(frame.loc[frame.TG0.abs() > 10], selected) is None
    other = spec.decomposition(study, base, "WF1", "Inner-training prefix", 42)
    assert retained_selection(other, selected) is None
    assert denominator_comparison(frame, spec).observations.max() == len(ordinary)


def test_extreme_and_ordinary_exact_decomposition(real):
    _, base, _, frame = real
    extreme = frame.loc[
        (frame.symbol == "AAPL") & (frame.session == "2020-12-09") & (frame.origin == 2)
    ].iloc[0]
    ordinary = frame.loc[(frame.symbol == "AAPL") & frame.TG0.abs().between(0.1, 1)].iloc[0]
    assert extreme.TG0 == pytest.approx(-29.11614698023523, abs=1e-12)
    for r in (extreme, ordinary):
        panel = base.panels[str(r.session), int(r.origin)]
        assert panel.median_mad == (r["median"], r.MAD)
        assert r.TG0 == pytest.approx(r.numerator / (r.MAD + r.epsilon), abs=1e-12)
        assert bool(r.floor_ge_MAD) == (r.epsilon >= r.MAD)
        assert r.origin_ET.endswith("-05:00") or r.origin_ET.endswith("-04:00")


def test_candles_follow_row_and_full_history_native_exactness(real):
    c, base, _, frame = real
    extreme = frame.loc[
        (frame.symbol == "AAPL") & (frame.session == "2020-12-09") & (frame.origin == 2)
    ].iloc[0]
    ordinary = frame.loc[(frame.symbol == "AAPL") & frame.TG0.abs().between(0.1, 1)].iloc[0]
    for r in (extreme, ordinary):
        start, end = history.context_window(str(r.session))
        bars, _ = history.history_bars(c, "AAPL", start, end, "30 min source")
        old, _ = loaders.source_bars(c, "AAPL", str(r.session), str(r.session))
        full, _ = history.history_bars(c, "AAPL", str(r.session), str(r.session), "30 min source")
        pd.testing.assert_frame_equal(old, full)
        subset = bars.loc[bars.session.eq(r.session)]
        np.testing.assert_array_equal(
            subset[["open", "high", "low", "close", "volume"]],
            old[["open", "high", "low", "close", "volume"]],
        )
        figure = history.observation_figure(bars, r, target_spec("TG0"))
        assert figure.layout.meta["symbol"] == "AAPL"
        assert figure.layout.meta["origin_UTC"] == str(r.cutoff)
        volume = figure.data[1]
        assert isinstance(volume, go.Bar)
        np.testing.assert_array_equal(volume.y, bars.volume)
        assert bars.volume.sum() > 0
        assert any("Forecast origin" in a.text for a in figure.layout.annotations)
        end_mark = history.target_markers(r, target_spec("TG0")).iloc[0]
        assert end_mark.exit_event == r.maturity
        assert end_mark.proxy_exit_close + pd.Timedelta(minutes=3) == r.maturity
        completed = bars.loc[bars.available_at.le(r.cutoff)].tail(2)
        assert completed.available_at.max() == r.cutoff
        assert completed.timestamp.max() < r.cutoff
    context = input_context(c, base, "WF1", "Refit training", "AAPL", "2020-12-09", 2)
    assert context.timestamp.nunique() == 48 and context.timestamp.max() == extreme.cutoff
    assert not context.timestamp.gt(extreme.cutoff).any()


def test_native_normalized_both_exact_recipe_and_scope(real):
    c, base, _, _ = real
    features = history.history_features(
        c, base, "AAPL", "2020-12-09", "2020-12-09", "WF1", "refit", 2
    )
    bars, _ = history.history_bars(c, "AAPL", "2020-12-09", "2020-12-09", "30 min source")
    parameters = history.indicator_parameters(c, "WF1", "refit", "AAPL", ["M1", "B2"])
    m1 = features.loc[features.feature.eq("M1")]
    p = parameters["M1"]
    # Native M1 independently matches the saved component formula and genuine hour OHLC.
    floor = p["hourly_floor"]
    hourly, _ = loaders.source_bars(c, "AAPL", "2020-12-09", "2020-12-09", "Completed hour")
    for r in m1.itertuples():
        completed = hourly.loc[hourly.available_at.eq(r.timestamp)].iloc[0]
        slot = next(step.slot for step in base.history.calendar.steps if step.end == r.timestamp)
        component = base.components["AAPL", "2020-12-09", slot]
        rms60 = component.values["RMS60"]
        assert rms60 is not None
        native = np.log(completed.close / completed.open) / max(rms60, floor)
        assert r.native == pytest.approx(native, rel=1e-13, abs=1e-13)
    # Direct exact-key raw Arrow oracle: one genuine candle, no aggregate or UI adapter.
    observed = bars.iloc[0]
    manifest = loaders.read_json(c.root, c.config["source_manifest"])
    ref = next(
        r for r in manifest["source_by_stock"]["AAPL"] if r["data"] == observed.source_archive
    )
    raw = pq.read_table(
        loaders.verified(c.root, {"path": ref["data"], "sha256": ref["sha256"]}),
        columns=["open", "high", "low", "close", "volume"],
        filters=[("symbol", "=", "AAPL"), ("timestamp", "=", observed.timestamp.to_pydatetime())],
    ).to_pandas()
    assert len(raw) == 1
    np.testing.assert_array_equal(raw.iloc[0], observed[["open", "high", "low", "close", "volume"]])
    expected = ((m1.native - p["center"]) / p["scale"]).to_numpy().astype(np.float32)
    np.testing.assert_array_equal(m1.scaled, expected)
    assert parameters["B2"]["method"] == "NATIVE_BOUNDED_IDENTITY"
    for mode, count in (
        ("Standard / native indicator", 4),
        ("Normalized / model input", 4),
        ("Both", 6),
    ):
        fig = history.history_figure(bars, features, ["M1", "B2"], mode, parameters)
        traces = fig.to_plotly_json()["data"]
        assert len(traces) == count
        assert [t["yaxis"] for t in traces] == ["y", "y2"] + [f"y{i}" for i in range(3, count + 1)]
        assert p["preparation_id"] in traces[2]["hovertemplate"]
    with pytest.raises(loaders.ViewUnavailable, match="out of preparation scope"):
        history.history_features(c, base, "AAPL", "2024-02-14", "2024-02-14", "WF1", "refit", 1)
    later, _ = history.history_bars(c, "CME", "2024-02-14", "2024-02-14", "30 min source")
    assert not later.empty


def test_protected_guard_runs_before_any_reader(monkeypatch, tmp_path):
    def forbidden(*args, **kwargs):
        raise AssertionError("Protected selection cannot call source/feature/recipe readers")

    monkeypatch.setattr(history, "source_bars", forbidden)
    monkeypatch.setattr(history, "feature_frame", forbidden)
    monkeypatch.setattr(history, "read_preparation", forbidden)
    c = loaders.Catalog(tmp_path, {})
    for a, b in (("2024-07-01", "2025-06-30"), ("2024-06-28", "2024-07-01")):
        with pytest.raises(loaders.ViewUnavailable, match="LOCKED"):
            history.history_bars(c, "AAPL", a, b, "30 min source")
        with pytest.raises(loaders.ViewUnavailable, match="LOCKED"):
            history.history_guard(a, b)


def test_dst_early_close_overnight_archive_and_unavailable_horizon(real):
    c, _, _, frame = real
    for day, hour in (("2021-03-12", 15), ("2021-03-15", 14)):
        r = frame.loc[(frame.session == day) & (frame.origin == 1)].iloc[0]
        assert pd.Timestamp(r.cutoff).hour == hour
        assert pd.Timestamp(r.cutoff).tz_convert(loaders.ET).hour == 10
        markers = history.target_markers(r, target_spec("TG0"))
        assert markers.iloc[0].proxy_exit_close.tz_convert(loaders.ET).hour == 14
    previous, following, early = history.nearby_sessions("2023-11-24")
    assert previous == "2023-11-22" and following == "2023-11-27" and early
    bars, _ = history.history_bars(c, "AAPL", "2023-11-24", "2023-11-24", "30 min source")
    assert len(bars) == 7 and bars.available_at.max().tz_convert(loaders.ET).hour == 13
    assert history.context_window("2020-07-01")[0] == "2020-07-01"
    assert history.context_window("2024-06-28")[1] == "2024-06-28"
    assert history.context_window("2020-12-07")[0] == "2020-12-03"
    assert not history.history_bars(c, "AAPL", "2020-07-01", "2020-07-01", "30 min source")[0].empty
    with pytest.raises(loaders.ViewUnavailable, match="horizon"):
        history.target_markers(frame.iloc[0], replace(target_spec("TG0"), horizon_full_hours=None))
    early_row = frame.iloc[0].copy()
    early_row["session"] = "2023-11-24"
    early_row["cutoff"] = pd.Timestamp("2023-11-24T15:30Z")
    with pytest.raises(loaders.ViewUnavailable, match="UNAVAILABLE"):
        history.target_markers(early_row, target_spec("TG0"))


def widget(app, kind, label):
    return next(v for v in getattr(app, kind) if v.label == label)


def test_actual_apptest_range_selection_full_data_and_lock(real, monkeypatch):
    from streamlit.testing.v1 import AppTest

    c, _, _, frame = real
    app = AppTest.from_file(str(c.root / "apps/track_a_dashboard.py"), default_timeout=90).run()
    widget(app, "button", "Package 011: Compare C0 and T2").click().run()
    assert not app.exception and not app.error
    widget(app, "text_input", "Lower bound (blank = unbounded)").set_value("1").run()
    widget(app, "checkbox", "Include lower endpoint").uncheck().run()
    assert any("range matches: 2,860" in m.value for m in app.markdown)
    widget(app, "number_input", "Matching page").set_value(58).run()
    table = next(
        d.value for d in app.dataframe if "observation_id" in d.value and "origin_UTC" in d.value
    )
    assert len(table) == 10 and table.TG0.abs().gt(1).all()
    widget(app, "text_input", "Lower bound (blank = unbounded)").set_value("").run()
    widget(app, "text_input", "Upper bound (blank = unbounded)").set_value("2").run()
    widget(app, "checkbox", "Include upper endpoint").uncheck().run()
    ordinary = frame.loc[(frame.symbol == "AAPL") & frame.TG0.abs().between(0.1, 1)].iloc[0]
    label = "Select observation (stock / session / origin / UTC)"
    widget(app, "selectbox", label).set_value(str(ordinary.observation_id)).run()
    widget(app, "button", "Show candles").click().run()
    assert not app.exception and not app.error
    assert app.session_state["tg_selected"] == ordinary.observation_id
    charts = [json.loads(p.proto.spec) for p in app.get("plotly_chart")]
    selected = next(p for p in charts if p["layout"].get("meta", {}).get("observation_id"))
    assert selected["layout"]["meta"]["origin_UTC"] == str(ordinary.cutoff)
    widget(app, "selectbox", "Sort matching rows").set_value("Stock").run()
    assert app.session_state["tg_selected"] == ordinary.observation_id
    widget(app, "text_input", "Upper bound (blank = unbounded)").set_value("").run()
    extreme = frame.loc[
        (frame.symbol == "AAPL") & (frame.session == "2020-12-09") & (frame.origin == 2)
    ].iloc[0]
    widget(app, "selectbox", label).set_value(str(extreme.observation_id)).run()
    widget(app, "button", "Show candles").click().run()
    assert not app.exception and not app.error
    charts = [json.loads(p.proto.spec) for p in app.get("plotly_chart")]
    selected = next(p for p in charts if p["layout"].get("meta", {}).get("observation_id"))
    assert selected["layout"]["meta"]["origin_UTC"] == str(extreme.cutoff)
    widget(app, "radio", "Range population").set_value("Inner-training prefix").run()
    assert app.session_state["tg_selected"] is None
    widget(app, "radio", "Range population").set_value("Full refit prefix").run()
    widget(app, "selectbox", label).set_value(str(extreme.observation_id)).run()
    widget(app, "button", "Open in Full data").click().run()
    assert not app.exception and not app.error
    assert app.session_state["partition"] == "Full data"
    assert app.session_state["full_dates"] == (date(2020, 12, 9),) * 2
    full_chart = json.loads(app.get("plotly_chart")[0].proto.spec)
    assert any("Selected forecast origin" in a["text"] for a in full_chart["layout"]["annotations"])
    widget(app, "multiselect", "Indicator(s) · all registered FT0 channels").set_value(["M1"]).run()
    for mode in ("Standard / native indicator", "Normalized / model input", "Both"):
        widget(app, "radio", "Indicator display").set_value(mode).run()
        assert not app.exception and not app.error and len(app.get("plotly_chart")) == 1

    def forbidden(*args, **kwargs):
        raise AssertionError("Lock must precede numerical source/feature/preparation reads")

    from lstm_data.visualization import range_ui

    monkeypatch.setattr(range_ui, "candles_slice", forbidden)
    monkeypatch.setattr(range_ui, "indicator_slice", forbidden)
    monkeypatch.setattr(range_ui, "preparation_scope", forbidden)
    widget(app, "date_input", "Jump to date (ET)").set_value(date(2024, 7, 1)).run()
    assert not app.exception and not app.error and not app.get("plotly_chart")
    assert any("LOCKED" in w.value for w in app.warning)
