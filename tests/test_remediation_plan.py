"""Independent source-boundary arithmetic and exact original gap/request identities."""

from pathlib import Path

import pandas as pd

from lstm_data.config import load_config
from lstm_data.remediation_plan import dependency_calendar, gap_keys, source_request_manifest
from lstm_data.stock_source import StockCalendar


def test_first_july_dependency_graph_and_sufficient_ema_rsi_context():
    d = dependency_calendar()
    cal = StockCalendar("2019-01-02", "2020-07-01")
    assert d["first_input"]["session"] == "2020-06-19" and d["first_input"]["slot"] == 2
    day = cal.days.index("2020-06-19")
    assert cal.days[day - 126] == d["minimal_calendar_start"] == "2019-12-18"
    assert cal.days[day - 21] == d["lower_bounds"]["M4_endpoint_d21"]
    index = cal._positions["2020-06-19", 2]
    assert cal.steps[index - 360].session == d["lower_bounds"]["EMA_seed_plus360_good_updates"]
    assert (
        cal.steps[index - 154].session == d["lower_bounds"]["RSI_14_seed_changes_plus140_updates"]
    )
    assert d["complete_hour_updates_at_first_input_if_no_gaps"] >= 360
    for origins in d["M2"].values():
        assert len(origins["sessions"]) == 60
        assert pd.Timestamp(origins["last_exit"]) <= pd.Timestamp(d["first_input"]["end"])
    assert d["extra_safety_sessions"] == 0 and not d["scientific_readiness"]


def test_exact_gap_key_dedup_and_bounded_manifest_uses_original_basis():
    qa = {
        "missing_windows": [
            {
                "symbol": "JPM",
                "session": "2021-04-19",
                "missing_source_starts": ["2021-04-19T14:00:00+00:00"],
            }
        ]
    }
    assert len(gap_keys(qa)["JPM", "2021-04-19"]) == 1
    manifest = source_request_manifest(load_config(Path("configs/track_a_data.json")), qa)
    warmup = [r for r in manifest["requests"] if r["kind"] == "WARMUP"]
    assert len(warmup) == 7
    assert (
        pd.Timestamp(warmup[0]["params"]["start"]).tz_convert("America/New_York").date().isoformat()
        == "2019-12-18"
    )
    assert manifest["conservative_Alpaca_attempt_envelope"] <= 180
    for row in manifest["requests"]:
        p = row["params"]
        assert (p["feed"], p["adjustment"], p["asof"]) == ("sip", "split", "2025-06-30")
        assert row["availability_basis"] == "UNKNOWN" and row["available_at"] is None
        assert "SPY" not in p["symbols"]
