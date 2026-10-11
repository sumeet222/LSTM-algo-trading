from typing import cast

import pandas as pd
import pytest

from lstm_data.alignment import asof_diagnostic
from lstm_data.calendar import schedule, session_grid, stock_qa


def observations(times, symbol=None):
    data = pd.DataFrame(
        {"timestamp": times, "open": 100, "high": 101, "low": 99, "close": 100, "volume": 100}
    )
    if symbol:
        data["symbol"] = symbol
    return data


def synthetic_market(times, ends=None, availability=None):
    """Explicit fake clocks for code tests, never factual source attestations."""
    frame = observations(times)
    frame["period_end"] = times if ends is None else ends
    frame["available_at"] = times if availability is None else availability
    frame["timing_basis"] = "synthetic"
    return frame


def test_calendar_dst_and_early_close():
    days = schedule("2020-10-30", "2020-11-27")
    # XNYS open/close cells are timestamps; generic pandas scalar stubs are broader.
    assert cast(pd.Timestamp, days.loc["2020-10-30", "open"]).hour == 13
    assert cast(pd.Timestamp, days.loc["2020-11-02", "open"]).hour == 14
    assert cast(pd.Timestamp, days.loc["2020-11-27", "close"]).hour == 18
    assert pd.Timestamp("2020-11-26") not in days.index
    early = days.loc["2020-11-27"]
    grid = session_grid(cast(pd.Timestamp, early.open), cast(pd.Timestamp, early.close))
    assert len(grid) == 4
    assert grid[-1]["stub"]
    assert grid[-1]["end"] - grid[-1]["start"] == pd.Timedelta(minutes=30)


def test_spring_dst():
    days = schedule("2021-03-12", "2021-03-15")
    assert cast(pd.Timestamp, days.loc["2021-03-12", "open"]).hour == 14
    assert cast(pd.Timestamp, days.loc["2021-03-15", "open"]).hour == 13


def test_native_clock_hours_fail_gate_and_are_not_shifted():
    source = observations(pd.date_range("2020-07-01T13:00Z", periods=8, freq="h"), "AAPL")
    before = source.copy(deep=True)
    qa = stock_qa(source, ["AAPL", "JPM"], "2020-07-01", "2020-07-01")
    assert not qa["native_session_anchored_gate_pass"]
    assert qa["symbols"]["AAPL"]["missing_session_anchored_starts"] == 7
    assert qa["symbols"]["AAPL"]["partial_session_overlap_bars"] == 1
    assert qa["symbols"]["JPM"]["rows"] == 0
    pd.testing.assert_frame_equal(before, source)


def test_aligned_native_hour_cannot_prove_closing_stub():
    source = observations(pd.date_range("2020-07-01T13:30Z", periods=7, freq="h"), "AAPL")
    qa = stock_qa(source, ["AAPL"], "2020-07-01", "2020-07-01")
    assert qa["symbols"]["AAPL"]["missing_session_anchored_starts"] == 0
    assert qa["symbols"]["AAPL"]["partial_session_overlap_bars"] == 1
    assert not qa["native_session_anchored_gate_pass"]


@pytest.mark.parametrize("delay", [0, 60])
def test_asof_never_uses_future_index_availability(delay):
    stocks = observations(["2020-07-01T13:30Z", "2020-07-01T14:30Z"], "AAPL")
    labels = ["2020-07-01T13:00Z", "2020-07-01T14:00Z", "2020-07-01T16:00Z"]
    course = synthetic_market(
        labels, availability=pd.to_datetime(labels, utc=True) + pd.Timedelta(minutes=delay)
    )
    joined, summary = asof_diagnostic(stocks, course, index_delay_minutes=delay)
    assert (joined.candidate_available_at <= joined.decision_time).all()
    assert (joined.index_timestamp < pd.Timestamp("2020-07-01T16:00Z")).all()
    assert summary["audit_only"]


def test_asof_stale_and_unmatched_weekend():
    stocks = observations(["2020-07-02T12:00Z", "2020-07-06T13:30Z"], "AAPL")
    course = synthetic_market(["2020-07-02T18:00Z"])
    joined, summary = asof_diagnostic(stocks, course, index_delay_minutes=0)
    assert summary["unmatched"] == 1
    assert summary["stale"] == 1
    assert not joined.usable_candidate.any()


def test_negative_delay_rejected():
    with pytest.raises(ValueError, match="nonnegative"):
        asof_diagnostic(observations([], "AAPL"), observations([]), index_delay_minutes=-1)


@pytest.mark.parametrize("age,available_age,usable,reason", [
    (120, 60, False, "STALE_PERIOD_END"),  # Original P0.1 F01.
    (60, 30, True, "ACCEPTED_DIAGNOSTIC_ONLY"),
    (60, -5, False, "FUTURE_AVAILABILITY"),
    (90, 30, True, "ACCEPTED_DIAGNOSTIC_ONLY"),
    (90.01, 30, False, "STALE_PERIOD_END"),
    (-5, -10, False, "FUTURE_PERIOD_END"),
    (60, 70, False, "AVAILABILITY_BEFORE_PERIOD_END"),
])
def test_period_freshness_and_publication_are_independent(age, available_age, usable, reason):
    cutoff = pd.Timestamp("2001-01-02T15:00Z")
    stocks = observations([cutoff - pd.Timedelta(hours=1)], "FAKE")
    stocks["decision_cutoff"] = cutoff
    course = synthetic_market(
        ["2001-01-02T12:00Z"],  # Label is deliberately distinct from period end.
        ends=[cutoff - pd.Timedelta(minutes=age)],
        availability=[cutoff - pd.Timedelta(minutes=available_age)],
    )
    joined, summary = asof_diagnostic(stocks, course, index_delay_minutes=0)
    row = joined.iloc[0]
    assert row.usable_candidate == usable
    assert row.reason == reason
    assert row.period_end_age_minutes == pytest.approx(age)
    assert row.availability_age_minutes == pytest.approx(available_age)
    assert row.timing_basis == "synthetic"
    assert not row.research_ready and not summary["research_ready"]


@pytest.mark.parametrize("missing,basis,reason", [
    ("period_end", "synthetic", "UNKNOWN_PERIOD_END"),
    ("available_at", "synthetic", "UNKNOWN_AVAILABLE_AT"),
    (None, "unverified", "UNVERIFIED_TIMING_METADATA"),
    (None, "ambiguous", "UNVERIFIED_TIMING_METADATA"),
    (None, "hypothetical", "UNVERIFIED_TIMING_METADATA"),
    ("timing_basis", None, "UNVERIFIED_TIMING_METADATA"),
])
def test_unknown_clocks_fail_closed(missing, basis, reason):
    stocks = observations(["2001-01-02T14:00Z"], "FAKE")
    course = synthetic_market(["2001-01-02T14:00Z"])
    course["timing_basis"] = basis
    if missing:
        course = course.drop(columns=missing)
    row = asof_diagnostic(stocks, course, index_delay_minutes=60)[0].iloc[0]
    assert row.reason == reason and row.timing_status == "BLOCKED"
    assert not row.usable_candidate and not row.research_ready
    if missing == "available_at":
        assert row.availability_basis == "hypothetical label plus delay"
        assert pd.isna(row.available_at)


def test_legacy_label_only_and_null_metadata_remain_blocked():
    stocks = observations(["2001-01-02T14:00Z"], "FAKE")
    for course in (
        observations(["2001-01-02T14:00Z"]),
        synthetic_market(["2001-01-02T14:00Z"], ends=[None], availability=[None]),
    ):
        row = asof_diagnostic(stocks, course, index_delay_minutes=0)[0].iloc[0]
        assert row.reason == "UNKNOWN_PERIOD_END"
        assert row.timing_status == "BLOCKED" and not row.usable_candidate


def test_each_historical_step_uses_its_own_cutoff():
    stocks = observations(["2001-01-02T13:00Z", "2001-01-02T14:00Z"], "FAKE")
    stocks["decision_cutoff"] = ["2001-01-02T14:00Z", "2001-01-02T15:00Z"]
    course = synthetic_market(
        ["2001-01-02T12:00Z", "2001-01-02T13:00Z"],
        ends=["2001-01-02T13:00Z", "2001-01-02T14:00Z"],
        availability=["2001-01-02T13:30Z", "2001-01-02T14:05Z"],
    )
    joined, _ = asof_diagnostic(stocks, course, index_delay_minutes=0)
    assert joined.usable_candidate.all()
    assert joined.period_end.tolist() == list(pd.to_datetime(
        ["2001-01-02T13:00Z", "2001-01-02T14:00Z"], utc=True
    ))
    assert (joined.available_at <= joined.decision_cutoff).all()


def test_recent_arrival_of_old_period_does_not_displace_fresher_observation():
    stocks = observations(["2001-01-02T14:00Z"], "FAKE")
    course = synthetic_market(
        ["2001-01-02T12:00Z", "2001-01-02T13:00Z"],
        ends=["2001-01-02T13:00Z", "2001-01-02T14:00Z"],
        availability=["2001-01-02T14:59Z", "2001-01-02T14:30Z"],
    )
    row = asof_diagnostic(stocks, course, index_delay_minutes=0)[0].iloc[0]
    assert row.period_end == pd.Timestamp("2001-01-02T14:00Z")
    assert row.usable_candidate and row.period_end_age_minutes == 60


def test_empty_market_has_explicit_blocked_reason():
    stocks = observations(["2001-01-02T14:00Z"], "FAKE")
    row = asof_diagnostic(stocks, observations([]), index_delay_minutes=0)[0].iloc[0]
    assert row.reason == "NO_CANDIDATE" and row.timing_status == "BLOCKED"
