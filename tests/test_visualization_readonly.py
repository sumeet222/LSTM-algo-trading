"""Small fabricated candle oracles and optional local, read-only artifact reconciliation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lstm_data.config import digest
from lstm_data.ft0_transforms import ORDER
from lstm_data.pretraining_policy import CANDIDATE
from lstm_data.pretraining_store import read_preparation
from lstm_data.visualization import loaders
from lstm_data.visualization.definitions import FEATURES
from lstm_data.visualization.launch import available_port
from lstm_data.visualization.loaders import Catalog, ViewUnavailable
from lstm_data.visualization.metrics import matched, summary


@pytest.fixture
def chart_module():
    pytest.importorskip(
        "plotly", reason="Install the declared visualization extra for chart checks"
    )
    from lstm_data.visualization import figures

    return figures


def fabricated_bars(start: str, count: int) -> pd.DataFrame:
    """SYNTHETIC TEST ONLY; never loaded into an app or scientific store."""
    return pd.DataFrame(
        {
            "symbol": ["AAPL"] * count,
            "timestamp": pd.date_range(start, periods=count, freq="30min"),
            "open": np.arange(count) + 100.0,
            "high": np.arange(count) + 102.0,
            "low": np.arange(count) + 99.0,
            "close": np.arange(count) + 101.0,
            "volume": [10.0] * count,
            "trade_count": [3] * count,
            "source_timeframe": "30Min",
            "feed": "sip",
            "adjustment": "split",
            "provenance_id": "SYNTHETIC_TEST_ONLY",
        }
    )


def source_fixture(tmp_path: Path, day: str, start: str, count: int) -> Catalog:
    data = tmp_path / "SYNTHETIC_TEST_ONLY.parquet"
    # The physical file straddles the protected boundary; Arrow must filter first.
    pd.concat(
        [fabricated_bars(start, count), fabricated_bars("2024-07-01T13:30Z", 13)], ignore_index=True
    ).to_parquet(data)
    params = {
        "start": day + "T00:00:00Z",
        "end": "2024-07-02T00:00:00Z",
        "feed": "sip",
        "adjustment": "split",
        "currency": "USD",
        "timeframe": "30Min",
        "asof": "2025-06-30",
    }
    meta = tmp_path / "meta.json"
    meta.write_text(json.dumps({"params": params}))
    manifest = tmp_path / "source.json"
    manifest.write_text(
        json.dumps(
            {
                "source_by_stock": {
                    "AAPL": [
                        {
                            "data": data.name,
                            "sha256": digest(data),
                            "manifest": meta.name,
                            "manifest_sha256": digest(meta),
                            "params": params,
                        }
                    ]
                }
            }
        )
    )
    return Catalog(
        tmp_path, {"source_manifest": {"path": manifest.name, "sha256": digest(manifest)}}
    )


@pytest.mark.parametrize(
    "day,start,count,hours",
    [
        ("2024-06-28", "2024-06-28T13:30Z", 13, 6),
        ("2023-11-24", "2023-11-24T14:30Z", 7, 3),
    ],
)
def test_candle_oracle_stub_and_predicate_before_conversion(
    tmp_path, monkeypatch, day, start, count, hours, chart_module
):
    c = source_fixture(tmp_path, day, start, count)
    original = loaders.pq.read_table
    reads = []

    def bounded(*args, **kwargs):
        assert ("timestamp", "<", loaders.BARRIER.to_pydatetime()) in kwargs["filters"]
        table = original(*args, **kwargs)
        assert max(table.column("timestamp").to_pylist()) < loaders.BARRIER
        reads.append(table.num_rows)
        return table

    monkeypatch.setattr(loaders.pq, "read_table", bounded)
    native, _ = loaders.source_bars(c, "AAPL", day, day)
    full, _ = loaders.source_bars(c, "AAPL", day, day, "Completed hour")
    assert len(native) == count and native.is_stub.sum() == 1
    assert len(full) == hours and not full.is_stub.any()
    assert tuple(full.iloc[0][["open", "high", "low", "close", "volume"]]) == (
        100,
        103,
        99,
        102,
        20,
    )
    assert full.iloc[0].timestamp == pd.Timestamp(start)
    assert full.iloc[0].available_at == pd.Timestamp(start) + pd.Timedelta(hours=1)
    assert reads == [count, count]
    fig = chart_module.candles(full)
    data = fig.to_plotly_json()["data"]
    assert data[0]["type"] == "candlestick" and data[1]["type"] == "bar"
    assert data[0]["yaxis"] == "y" and data[1]["yaxis"] == "y2"


def test_forbidden_dates_and_actions_fail_before_io(monkeypatch, tmp_path):
    def forbidden(*args, **kwargs):
        raise AssertionError("No file/network/numeric reader may be called")

    monkeypatch.setattr(loaders, "read_json", forbidden)
    monkeypatch.setattr(loaders.pq, "read_table", forbidden)
    c = Catalog(tmp_path, {})
    for a, b in [("2024-07-01", "2024-07-01"), ("2024-06-28", "2024-07-01")]:
        with pytest.raises(ViewUnavailable, match="permitted history"):
            loaders.source_bars(c, "AAPL", a, b)
    for action in ("FIT", "REFIT", "FIT_TRANSFORM_ONLY", "WRITE", "TRADE", "DOWNLOAD"):
        with pytest.raises(ViewUnavailable, match="read-only"):
            c.require(action)
    with pytest.raises(ViewUnavailable):
        loaders.date_window("2024-01-01", "2024-06-30")


def test_marker_maturity_dst_and_project_zero_weighting():
    for day, hour in [("2024-03-08", 15), ("2024-03-11", 14)]:
        events = loaders.event_markers(day, day, (1,))
        r = events.iloc[0]
        assert r.cutoff.hour == hour and r.cutoff.minute == 30
        assert r.entry_event - r.cutoff == pd.Timedelta(minutes=3)
        assert r.exit_event - r.cutoff == pd.Timedelta(hours=4, minutes=3)
        assert r.proxy_exit_close - r.cutoff == pd.Timedelta(hours=4)
    assert loaders.event_markers("2023-11-24", "2023-11-24", (1, 2)).empty
    rows = []
    for day, origin, target in [("2023-07-17", 1, 2), ("2023-07-18", 1, 1), ("2023-07-18", 2, 3)]:
        for symbol in CANDIDATE:
            # Nonconstant targets preserve defined target ranks, constant score gets project0.
            y = target if symbol == "AAPL" else -target
            rows.append(
                {
                    "session": day,
                    "origin": origin,
                    "symbol": symbol,
                    "TG0": y,
                    "score": 0.0,
                    "squared_error": float(target**2),
                }
            )
    s = summary(pd.DataFrame(rows))
    assert s["MSE"] == 4.5 and s["daily_Rank_IC"] == 0
    assert s["defined_origins"] == 0 and s["origins"] == 3


@pytest.fixture(scope="module")
def local_catalog() -> Catalog:
    root = Path(__file__).resolve().parents[1]
    c = Catalog.discover(root)
    store = loaders.read_json(root, c.config["manifest"])["canonical_store"]
    if not (root / store["path"]).is_file():
        pytest.skip("Local canonical data not provisioned; see documented source setup")
    return c


def test_local_stock_feature_native_scaled_identity(local_catalog, chart_module):
    c = local_catalog
    base = loaders.component_base(c)
    frame = loaders.feature_frame(
        c, base, "AAPL", "WF2", "2024-01-16", "2024-01-16", 1, "Development"
    )
    first = frame.loc[frame.timestamp == frame.timestamp.min()].set_index("feature")
    prep = read_preparation(c.root, c.config["recipes"]["WF2"]["refit"])
    floor = next(p for p in prep.floors if p.symbol == "AAPL")
    component = base.components["AAPL", "2024-01-16", 1]
    oc, rms = component.values["OC"], component.values["RMS60"]
    assert oc is not None and rms is not None
    assert first.loc["M1", "native"] == oc / max(rms, floor.hourly_floor)
    assert tuple(first.index) == ORDER and set(FEATURES) == set(ORDER)
    assert -1 <= first.loc["T5", "native"] <= 1
    assert first.loc["T5", "native"] == first.loc["T5", "scaled"] or np.isclose(
        first.loc["T5", "native"], first.loc["T5", "scaled"], rtol=1e-7
    )
    assert frame.symbol.unique().tolist() == ["AAPL"]
    fig = chart_module.features(frame, ["M1", "T5"], "native")
    doc = fig.to_plotly_json()
    assert len(doc["data"]) == 2 and "Dimensionless" in doc["layout"]["yaxis"]["title"]["text"]


def test_local_matched_fold_snapshots_and_historical_missingness(local_catalog):
    c = local_catalog
    for fold in ("WF1", "WF2"):
        a = loaders.predictions(c, fold, "TM0", "Development")
        b = loaders.predictions(c, fold, "MC0", "Development")
        matched(a, b)
        expected = loaders.read_json(c.root, c.config["reference_metrics"][fold])
        if fold == "WF2":
            expected = expected["metrics"]
        actual = summary(a)
        assert abs(actual["MSE"] - expected["TM0"]["MSE"]) < 1e-12
        assert abs(actual["daily_Rank_IC"] - expected["TM0"]["daily_Rank_IC"]) < 1e-12
        changed = b.copy()
        changed.loc[changed.index[0], "TG0"] += 1
        with pytest.raises(ViewUnavailable, match="Different masks"):
            matched(a, changed)
    with pytest.raises(ViewUnavailable, match="not recorded"):
        loaders.predictions(c, "WF2", "E5", "Development")
    with pytest.raises(ViewUnavailable, match="Not recorded"):
        loaders.gradient_batches(c, "WF1", "TM0", "calibration")
    frame = loaders.gradient_batches(c, "WF2", "TM0", "calibration")
    assert len(frame) == 612 and frame.optimizer_step_id.tolist() == list(range(1, 613))
    assert len(loaders.training_trace(c, "WF1", "MC1")) > 0


def test_bound_hash_change_and_local_port_selection(tmp_path):
    c = Catalog(tmp_path, {"checkpoints": {"WF1": {"TM0": {"path": "optional.pt"}}}})
    assert c.missing_required(
        (
            ("required.parquet", ("SYN:SHA", -1, -1, -1)),
            ("optional.pt", ("SYN:SHA", -1, -1, -1)),
        )
    ) == ["required.parquet"]
    p = tmp_path / "evidence.json"
    p.write_text("{}")
    ref = {"path": p.name, "sha256": digest(p)}
    assert loaders.verified(tmp_path, ref) == p
    p.write_text('{"changed":true}')
    with pytest.raises(ViewUnavailable, match="hash changed"):
        loaders.verified(tmp_path, ref)
    import socket

    with socket.socket() as occupied:
        occupied.bind(("127.0.0.1", 0))
        port = occupied.getsockname()[1]
        if port <= 65515:
            assert available_port(port) != port
