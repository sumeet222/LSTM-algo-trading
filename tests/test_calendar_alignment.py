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


def test_calendar_dst_and_early_close():
    days = schedule("2020-10-30", "2020-11-27")
    assert days.loc["2020-10-30", "open"].hour == 13
    assert days.loc["2020-11-02", "open"].hour == 14
    assert days.loc["2020-11-27", "close"].hour == 18
    assert pd.Timestamp("2020-11-26") not in days.index
    early = days.loc["2020-11-27"]
    grid = session_grid(early.open, early.close)
    assert len(grid) == 4
    assert grid[-1]["stub"]
    assert grid[-1]["end"] - grid[-1]["start"] == pd.Timedelta(minutes=30)


def test_spring_dst():
    days = schedule("2021-03-12", "2021-03-15")
    assert days.loc["2021-03-12", "open"].hour == 14
    assert days.loc["2021-03-15", "open"].hour == 13


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
    course = observations(["2020-07-01T13:00Z", "2020-07-01T14:00Z", "2020-07-01T16:00Z"])
    joined, summary = asof_diagnostic(stocks, course, index_delay_minutes=delay)
    assert (joined.candidate_available_at <= joined.decision_time).all()
    assert (joined.index_timestamp < pd.Timestamp("2020-07-01T16:00Z")).all()
    assert summary["audit_only"]


def test_asof_stale_and_unmatched_weekend():
    stocks = observations(["2020-07-02T12:00Z", "2020-07-06T13:30Z"], "AAPL")
    course = observations(["2020-07-02T18:00Z"])
    joined, summary = asof_diagnostic(stocks, course, index_delay_minutes=0)
    assert summary["unmatched"] == 1
    assert summary["stale"] == 1
    assert not joined.usable_candidate.any()


def test_negative_delay_rejected():
    with pytest.raises(ValueError, match="nonnegative"):
        asof_diagnostic(observations([], "AAPL"), observations([]), index_delay_minutes=-1)
