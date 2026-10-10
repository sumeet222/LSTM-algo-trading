from pathlib import Path

import pytest

from lstm_data.config import load_config


@pytest.fixture
def cfg(tmp_path):
    config = load_config(Path(__file__).resolve().parents[1] / "configs/track_a_data.json")
    config["_root"] = tmp_path
    config["timeframe"] = "1Hour"  # Legacy/native client/store tests stay controlled.
    config["_stock_store"] = tmp_path / "data/raw/alpaca/track_a"
    return config


@pytest.fixture
def bars_fixture():
    return {
        "t": "2020-07-01T14:00:00Z",
        "o": 100.0,
        "h": 102.0,
        "l": 99.0,
        "c": 101.0,
        "v": 1000.0,
        "n": 12,
        "vw": 100.5,
    }
