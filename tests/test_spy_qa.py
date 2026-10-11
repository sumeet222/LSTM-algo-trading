"""Small offline fixtures for canonical timing, warm-up and metadata holds."""

from dataclasses import replace
from pathlib import Path

import pandas as pd
import pytest
from test_spy_completion import response
from test_spy_policy_v3 import source_v3

from lstm_data.config import fingerprint
from lstm_data.m2 import ScheduledCalendar, scheduled_window
from lstm_data.market_features import (
    MarketClose,
    MarketHistory,
    MarketObservation,
    window_from_history,
)
from lstm_data.market_source import ACTION_ENDPOINT, ACTION_PARAMS, MarketSource, hourly_archive
from lstm_data.spy_actions import inspect_actions
from lstm_data.spy_qa import structural_history


def small_history() -> MarketHistory:
    calendar = ScheduledCalendar("2020-03-19", "2020-07-02")
    hours = tuple(MarketObservation(s.start, s.end, 100., 101., None, "UNKNOWN",
                                    fingerprint([s.session, s.slot]), False)
                  for s in calendar.steps)
    closes = {d: MarketClose(c.close, 101., None, "UNKNOWN", fingerprint(d), False)
              for d, c in calendar._sessions.items() if c.close is not None}
    return MarketHistory(calendar, hours, closes)


def test_first_july_warmup_is_per_step_and_future_close_cannot_fill_earlier_daily_lock():
    history = small_history()
    for origin in (1, 2):
        result = structural_history(history, "2020-07-01", origin)
        assert result["all_48_history_requirements_met"]
        assert result["structural_vector_count"] == 48
        assert all(r["previous_completed_sessions"] == 64 for r in result["step_requirements"])
        assert result["step_requirements"][0]["daily_lock"] == "2020-06-18"
        window = window_from_history(history, "2020-07-01", origin)
        assert window.values is None and window.reason == "PUBLICATION_UNKNOWN"
        assert len(window.valid_mask) == 48 and not any(window.valid_mask)
        assert not window.research_ready
    closes = history.closes.copy()
    closes.pop("2020-06-18")
    closes["2020-07-02"] = replace(closes["2020-07-02"], close=999999.)
    changed = MarketHistory(history.calendar, tuple(history.hours.values()), closes)
    result = structural_history(changed, "2020-07-01", 1)
    assert not result["step_requirements"][0]["structural_vector_complete"]
    assert result["step_requirements"][0]["observed_previous_closes"] == 63


def test_missing_hour_preserves_scheduled_position_and_blocks_structural_vector():
    history = small_history()
    steps = scheduled_window(history.calendar, "2020-07-01", 1)
    hours = tuple(x for t, x in history.hours.items() if t != steps[-1].end)
    changed = MarketHistory(history.calendar, hours, history.closes)
    result = structural_history(changed, "2020-07-01", 1)
    assert result["scheduled_positions"] == 48 and result["observed_hours"] == 47
    assert not result["endpoint_structurally_complete"]
    assert window_from_history(changed, "2020-07-01", 1).reason == "MISSING_SPY_SOURCE"


@pytest.mark.parametrize("day", ["2020-07-01", "2020-11-27"])
def test_derived_lineage_qualifies_native_timestamp_with_original_request_key(day):
    source = MarketSource.load(Path("configs/track_a_market_spy_v3.json"))
    clock = ScheduledCalendar(day, day).clock(day)
    assert clock.open is not None and clock.close is not None
    starts = pd.date_range(clock.open, clock.close, freq="30min", inclusive="left")
    raw = pd.DataFrame({"symbol": "SPY", "timestamp": starts, "open": 100., "high": 102.,
                        "low": 99., "close": 101., "volume": 10., "feed": "sip",
                        "adjustment": "raw", "source_timeframe": "30Min",
                        "provenance_id": "fixed-original-request"})
    hours, qa = hourly_archive(raw, day, day)
    assert qa["timing_gate_pass"] and hours.evidence_id.nunique() == len(hours)
    assert len(hours) == (7 if day == "2020-07-01" else 4)
    assert hours.available_at.isna().all()
    assert (hours.available_at_basis == "UNKNOWN").all()
    assert raw.provenance_id.eq("fixed-original-request").all()
    assert source.config["adjustment"] == "raw"


@pytest.mark.parametrize("status", [200, 403])
def test_bounded_actions_count_same_journal_and_never_certify_absence(
    tmp_path, monkeypatch, status,
):
    import json

    source = source_v3(tmp_path)
    source.store.mkdir(parents=True)
    journal = source.store / "transport_attempts.jsonl"
    journal.write_bytes(b'{"stage":"inherited"}\n' * 13)
    report = tmp_path / "reports"
    report.mkdir()
    monkeypatch.setattr("lstm_data.spy_actions.verify_historical_journal", lambda *a: None)
    monkeypatch.setattr("lstm_data.spy_actions.credentials", lambda: ("fixture", "fixture"))
    returned = response(status)
    returned._content = json.dumps({"corporate_actions": {}, "next_page_token": None}).encode()

    def get(url, **kwargs):
        assert url == ACTION_ENDPOINT and kwargs["params"] == ACTION_PARAMS
        return returned

    monkeypatch.setattr("lstm_data.market_source.requests.get", get)
    result = inspect_actions(source, report, None)
    assert result["transport_attempts"] == 14 and result["new_metadata_attempts"] == 1
    assert result["exhausted"] == (status == 200)
    assert not result["certified_no_splits"] and not result["publication_verified"]
    assert result["status"] == "HOLD_UNVERIFIED_SCOPE"
    assert not (source.store / ".acquire.lock").exists()
