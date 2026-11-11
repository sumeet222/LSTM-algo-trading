"""Fabricated raw-source fixtures; no historical accounting or network calls."""

import json

import numpy as np
import pandas as pd
import pytest

from lstm_data.trading.track2.stage012.calendar_schedule import MarketClock
from lstm_data.trading.track2.stage012.model_registry import SYMBOLS
from lstm_data.trading.track2.stage35.final_backtest_v4 import market
from lstm_data.trading.track2.stage35.final_backtest_v4.paths import digest


def test_gap_layer_only_populates_exact_original_missing_key(tmp_path, monkeypatch):
    clock = MarketClock("2021-01-01", "2021-02-01")
    start = pd.Timestamp(clock.origins("2021-01-04")[0])
    dates = pd.date_range(start, periods=390, freq="min")
    rows = [
        dict(
            ticker=s,
            timestamp=t,
            is_rth=True,
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.0,
            volume=1000.0,
        )
        for t in dates
        for s in SYMBOLS
        if not (t == start and s == "VZ")
    ]
    source = tmp_path / "canonical.parquet"
    pd.DataFrame(rows).to_parquet(source, index=False)
    extra = tmp_path / "selected.json"
    quote = dict(symbol="VZ", t=start.isoformat(), o=99.0, h=102.0, l=98.0, c=101.0, v=1000.0)
    extra.write_text(json.dumps({"basis": "RAW_SHARE", "bars": [quote]}))

    def instance():
        result = market.Market.__new__(market.Market)
        result.first = result.last = "2021-01-04"
        result.clock = clock
        result.reads = []
        result.ogn = {}
        result.parts = {"2021-01": {"path": str(source), "sha256": digest(source)}}
        result.gap_entries = {"2021-01-04": {"path": str(extra), "projected_sha256": digest(extra)}}
        return result

    monkeypatch.setattr(market, "V2", tmp_path)
    folder = tmp_path / "audits/signals_release/F21"
    folder.mkdir(parents=True)
    # Source-only projection does not open signals, but existence is required by
    # the shared calendar/source contract; contents are never a scored panel.
    (folder / "2021-01-04.parquet").touch()
    day = next(instance().days(include_signals=False))
    assert day.valid.all() and day.opens[0, 0] == 99 and day.closes[0, 0] == 101
    np.testing.assert_array_equal(day.opens[0, 1:], 100.0)
    quote["symbol"] = "AAPL"
    extra.write_text(json.dumps({"basis": "RAW_SHARE", "bars": [quote]}))
    with pytest.raises(ValueError, match="OVERWRITES_VALID_SOURCE"):
        next(instance().days(include_signals=False))
