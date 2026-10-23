"""P019 detector boundaries and fail-closed source identity oracles."""

import json
from pathlib import Path

import pandas as pd
import pytest

from lstm_data.hf1m_action_audit import REVISION, ActivePanel, scan_stock, write_json
from lstm_data.hf1m_action_review import gate_decision

ROOT = Path(__file__).resolve().parents[1]


def candles(times: list[str], closes: list[float], rth: bool = True) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(times, utc=True),
            "ticker": "AAPL",
            "close": closes,
            "open": closes,
            "high": closes,
            "low": closes,
            "volume": 100.0,
            "is_rth": rth,
            "source_row": range(len(times)),
        }
    )


def test_cross_month_split_and_overnight_are_not_interpolated():
    state = {}
    scan_stock(candles(["2020-08-31T19:59Z"], [100.0]), state, 1.25, 1.5)
    events = scan_stock(candles(["2020-09-01T13:30Z"], [25.0]), state, 1.25, 1.5)
    assert len(events) == 1
    assert events[0]["before_close"] == 100
    assert events[0]["after_close"] == 25
    assert "RTH_ADJACENT_CLOSE" in events[0]["rules"]
    assert "SESSION_MEDIAN_SHIFT" in events[0]["rules"]


def test_extended_hours_does_not_replace_prior_rth_endpoint():
    frame = candles(
        ["2020-08-28T19:59Z", "2020-08-28T21:00Z", "2020-08-31T13:30Z"], [100.0, 25.0, 25.0]
    )
    frame.loc[1, "is_rth"] = False
    events = scan_stock(frame, {}, 1.25, 1.5)
    assert len(events) == 2
    assert "RTH_ADJACENT_CLOSE" in events[1]["rules"]


def test_dst_exchange_dates_and_gaps_preserve_actual_instants():
    frame = candles(["2020-03-06T20:59Z", "2020-03-09T13:30Z"], [100.0, 70.0])
    event = scan_stock(frame, {}, 1.25, 1.5)[0]
    assert event["before_timestamp"] == pd.Timestamp("2020-03-06T20:59Z")
    assert event["after_timestamp"] == pd.Timestamp("2020-03-09T13:30Z")
    assert event["before_timestamp"].tz_convert("America/New_York").hour == 15
    assert event["after_timestamp"].tz_convert("America/New_York").hour == 9


def test_small_missing_endpoint_gap_does_not_generate_false_jump():
    frame = candles(["2020-03-09T14:00Z", "2020-03-09T14:05Z"], [100.0, 101.0])
    assert scan_stock(frame, {}, 1.25, 1.5) == []


def test_intraminute_extreme_is_found_without_adjacent_close_jump():
    frame = candles(["2020-03-09T14:00Z"], [100.0])
    frame.loc[0, "low"] = 50
    assert scan_stock(frame, {}, 1.25, 1.5)[0]["rules"] == ["MINUTE_RANGE"]


def test_many_detectors_merge_one_event_without_flattening_real_return():
    frame = candles(["2020-03-09T14:00Z", "2020-03-09T14:01Z"], [100.0, 70.0])
    before = frame.copy(deep=True)
    event = scan_stock(frame, {}, 1.25, 1.5)[0]
    assert len(event["rules"]) == 3
    assert event["after_close"] / event["before_close"] == 0.7
    pd.testing.assert_frame_equal(frame, before)


@pytest.mark.parametrize(
    "name",
    [
        "data/raw/alpaca/track_a/prices.parquet",
        f"data/processed/hf20_hf1m_long_v1/{REVISION}/qa_v2/canonical_observed/1992-01.parquet",
        "data/processed/hf20_twelvedata/prices.parquet",
        f"data/processed/hf20_hf1m_long_v1/{'0' * 40}/qa_v2/canonical_observed/2020-03.parquet",
    ],
)
def test_legacy_or_wrong_revision_cannot_enter_any_consumer(name):
    config = json.loads((ROOT / "configs/hf1m_p019_action_scan_v1.json").read_text())
    panel = ActivePanel(ROOT, config)
    with pytest.raises(ValueError, match="unverified or unallowlisted"):
        panel.read(name)


def test_legitimate_march_reuse_is_exact_membership_only():
    config = json.loads((ROOT / "configs/hf1m_p019_action_scan_v1.json").read_text())
    panel = ActivePanel(ROOT, config)
    assert panel.months[-1]["raw_path"] in panel.refs
    name = panel.months[0]["raw_path"]
    with pytest.raises(ValueError, match="unverified"):
        panel.read(name)


def test_changed_order_revision_or_binding_is_rejected():
    config = json.loads((ROOT / "configs/hf1m_p019_action_scan_v1.json").read_text())
    config["symbols"] = list(reversed(config["symbols"]))
    with pytest.raises(ValueError, match="configuration changed"):
        ActivePanel(ROOT, config)


def test_artifact_publication_never_overwrites_prior_evidence(tmp_path):
    path = tmp_path / "receipt.json"
    write_json(path, {"status": "STOP"})
    with pytest.raises(FileExistsError):
        write_json(path, {"status": "PASS"})
    assert json.loads(path.read_text())["status"] == "STOP"


def reviewed_events():
    return [
        {
            "original_018d": True,
            "classification": "VERIFIED_REAL_MARKET_MOVE",
            "sources": [{"url": "https://issuer.example/event"}],
            "post_treatment_status": "VERIFIED_CLEAN",
        }
        for _ in range(13)
    ]


def test_no_post_treatment_scan_cannot_release_even_externally_verified_actions():
    assert gate_decision(reviewed_events(), False) == "STOP_ACTION_UNVERIFIED"


def test_one_new_unresolved_event_blocks_all_downstream_work():
    events = reviewed_events()
    events.append({"original_018d": False, "classification": "UNRESOLVED_MATERIAL_JUMP"})
    assert gate_decision(events, True) == "STOP_ACTION_UNVERIFIED"


def test_ratio_only_or_missing_public_evidence_cannot_release():
    events = reviewed_events()
    events[0]["sources"] = []
    assert gate_decision(events, True) == "STOP_ACTION_UNVERIFIED"


def test_verified_action_without_implemented_treatment_cannot_release():
    events = reviewed_events()
    events[0]["post_treatment_status"] = "FACT_VERIFIED; ADJUSTMENT_NOT_ACTIVATED"
    assert gate_decision(events, True) == "STOP_ACTION_UNVERIFIED"


def test_missing_original_candidate_blocks_release():
    assert gate_decision(reviewed_events()[:-1], True) == "STOP_ACTION_UNVERIFIED"


def test_exact_action_metadata_never_activates_a_price_store():
    facts = json.loads((ROOT / "configs/hf1m_p019_verified_event_facts_v1.json").read_text())
    assert facts["activation"] == "FACTS_ONLY_NOT_AN_ADJUSTED_PRICE_STORE"
    splits = {
        (e["ticker"], e["date"]): e["factor_denominator"]
        for e in facts["events"]
        if e["kind"] == "SPLIT"
    }
    assert splits == {
        ("KO", "2012-08-13"): 2,
        ("MA", "2014-01-22"): 10,
        ("AAPL", "2014-06-09"): 7,
        ("SBUX", "2015-04-09"): 2,
        ("AAPL", "2020-08-31"): 4,
        ("TSLA", "2020-08-31"): 5,
        ("AMZN", "2022-06-06"): 20,
        ("TSLA", "2022-08-25"): 3,
        ("AVGO", "2024-07-15"): 10,
    }
