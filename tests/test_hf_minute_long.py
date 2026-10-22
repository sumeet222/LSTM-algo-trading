"""Source-only reconciliation, causal clock, resource and immutable checkpoint oracles."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pyarrow as pa
import pytest

from lstm_data import hf_minute_long_qa as qa
from lstm_data.hf_minute_boundary_io import DATASET, REVISION
from lstm_data.hf_minute_long_io import Guard, selected_table


@pytest.fixture
def source_day(monkeypatch):
    grid = qa.calendar_frame("2026-03")
    first = grid.loc[grid.session_date_et == "2026-03-02"].copy()
    monkeypatch.setattr(qa, "calendar_frame", lambda month: first.copy())
    monkeypatch.setattr(qa, "SYMBOLS", ("VZ",))
    return pd.DataFrame(
        dict(
            timestamp=first.timestamp,
            open=10.0,
            high=10.1,
            low=9.9,
            close=10.0,
            volume=2.0,
            ticker="VZ",
            source_row=np.arange(len(first)),
        )
    )


def test_exact_duplicate_once_conflicts_all_excluded_raw_unchanged(source_day):
    exact = source_day.iloc[[5]].copy()
    conflict = source_day.iloc[[10]].copy()
    conflict["volume"] = 99.0
    raw = pd.concat([source_day, exact, conflict], ignore_index=True)
    before = raw.copy(deep=True)
    result = qa.process_month(raw, "2026-03", "0" * 64, "raw")
    pd.testing.assert_frame_equal(raw, before)
    assert len(result.canonical) == 389
    assert result.canonical.volume.sum() == 778.0
    assert result.minute_issues.issue_type.eq("CONFLICTING_DUPLICATE").sum() == 2
    assert result.proxies.volume.sum() == 0 and len(result.proxies) == 1
    first = result.hourly.iloc[0]
    assert first.exact_duplicate_minutes == 1 and first.ambiguous_minutes == 1
    assert first.observed_volume == 118.0 and not first.volume_is_complete
    assert first.open_is_genuine and first.close_is_genuine


def test_five_minute_limit_and_two_minute_sensitivity(source_day):
    short = source_day.drop(index=range(10, 15))
    long = source_day.drop(index=range(10, 16))
    a = qa.process_month(short, "2026-03", "0" * 64, "raw")
    b = qa.process_month(long, "2026-03", "0" * 64, "raw")
    assert len(a.proxies) == 5 and len(b.proxies) == 0
    assert a.sensitivity.iloc[0].filled_cap2 == 0 and a.sensitivity.iloc[0].filled_cap5 == 5
    assert a.hourly.iloc[0].moderate_candidate and not b.hourly.iloc[0].moderate_candidate


def test_open_missing_and_empty_hour_never_fabricated(source_day):
    raw = source_day.drop(index=[0, 1, *range(60, 120)])
    result = qa.process_month(raw, "2026-03", "0" * 64, "raw")
    assert result.proxies.empty
    assert result.hourly.iloc[0].first_observed_open
    assert not result.hourly.iloc[0].open_is_genuine
    empty = result.hourly.iloc[1]
    assert empty.genuine_minutes == 0 and pd.isna(empty.open) and pd.isna(empty.close)
    assert empty.quality_tier == "MISSING"


def test_later_hour_cannot_change_completed_endpoint_proxy(source_day):
    short = source_day.drop(index=[58, 59])
    extended = source_day.drop(index=range(58, 72))
    a = qa.process_month(short, "2026-03", "0" * 64, "raw")
    b = qa.process_month(extended, "2026-03", "0" * 64, "raw")
    pd.testing.assert_series_equal(a.hourly.iloc[0], b.hourly.iloc[0])
    assert a.hourly.iloc[0].filled_minutes == 2 and not a.hourly.iloc[0].close_is_genuine
    assert all(a.proxies.available_at_utc > a.proxies.timestamp)


def test_price_changes_in_future_do_not_change_earlier_hour(source_day):
    raw = source_day.drop(index=[10, 11])
    changed = raw.copy()
    changed.loc[changed.index >= 60, ["open", "high", "low", "close"]] *= 2.0
    a = qa.process_month(raw, "2026-03", "0" * 64, "raw")
    b = qa.process_month(changed, "2026-03", "0" * 64, "raw")
    pd.testing.assert_series_equal(a.hourly.iloc[0], b.hourly.iloc[0])
    assert b.hourly.iloc[1].action_uncertainty


def test_action_uncertain_hour_keeps_observed_jump_but_blocks_fill(source_day):
    raw = source_day.drop(index=[10, 11]).copy()
    raw.loc[raw.index >= 20, ["open", "high", "low", "close"]] *= 3.0
    result = qa.process_month(raw, "2026-03", "0" * 64, "raw")
    assert result.proxies.empty
    assert result.hourly.iloc[0].action_uncertainty
    assert result.canonical.close.max() == 30.0
    assert result.hourly.iloc[0].high == raw.high.max()


def test_hour_membership_ohlcv_and_stub_conservation(source_day):
    raw = source_day.copy()
    raw["volume"] = np.arange(len(raw), dtype=float)
    result = qa.process_month(raw, "2026-03", "0" * 64, "raw")
    assert result.hourly.bin_length_minutes.tolist() == [60] * 6 + [30]
    assert result.hourly.observed_volume.sum() == raw.volume.sum()
    assert (result.hourly.hour_end_utc == result.hourly.completed_at_utc).all()
    assert result.hourly.strict_candidate.all()
    for row in result.hourly.itertuples():
        selected = raw[(raw.timestamp >= row.hour_start_utc) & (raw.timestamp < row.hour_end_utc)]
        assert len(selected) == row.expected_minutes
        assert row.observed_volume == selected.volume.sum()


def test_dst_and_halfday_grid():
    march = qa.calendar_frame("2026-03")
    assert march.loc[march.session_date_et == "2026-03-02"].timestamp.iloc[0].hour == 14
    assert march.loc[march.session_date_et == "2026-03-09"].timestamp.iloc[0].hour == 13
    nov = qa.calendar_frame("2025-11")
    assert len(nov.loc[nov.session_date_et == "2025-11-28"]) == 210


def test_guard_cap_atomic_replay_and_corruption(tmp_path, monkeypatch):
    guard = Guard(tmp_path)
    table = pa.table(dict(close=[1.0, 2.0]))
    path = tmp_path / "canonical.parquet"
    first = guard.parquet(path, table)
    assert guard.parquet(path, table)["sha256"] == first["sha256"]
    assert not path.with_suffix(".part").exists()
    with pytest.raises(ValueError, match="STOP_SOURCE_INTEGRITY"):
        guard.parquet(path, pa.table(dict(close=[3.0, 4.0])))
    monkeypatch.setattr(guard, "footprint", lambda: 9_000_000_000)
    with pytest.raises(ValueError, match="STOP_STORAGE"):
        guard.check(1, "test")


def test_exact_filter_keeps_source_values_and_ids(source_day):
    raw = source_day.iloc[:3].copy()
    raw["ticker"] = ["VZ", "vz", "SPY"]
    table = pa.Table.from_pandas(raw[qa.COLUMNS], preserve_index=False)
    result = selected_table(table, dict(path="data/ohlcv_2026-03.parquet"), 2, 100)
    assert result.num_rows == 1 and result.column("source_row").to_pylist() == [100]
    assert result.column("source_dataset").to_pylist() == [DATASET]
    assert result.column("source_revision").to_pylist() == [REVISION]


def test_unlisted_exact_symbol_is_observed_zero_without_synthetic_history(source_day, monkeypatch):
    monkeypatch.setattr(qa, "SYMBOLS", ("VZ", "COP"))
    result = qa.process_month(source_day, "2026-03", "0" * 64, "raw")
    empty = result.coverage.loc[result.coverage.ticker == "COP"].iloc[0]
    assert empty.raw_rows == 0 and empty.status == "EXAMINED_NO_EXACT_SYMBOL_ROWS"
    assert not result.hourly.ticker.eq("COP").any()
    issue = result.minute_issues.loc[result.minute_issues.ticker == "COP"].iloc[0]
    assert issue.issue_type == "NO_EXACT_SYMBOL_SOURCE_ROWS" and pd.isna(issue.timestamp_utc)


def test_invalid_bar_excluded_without_ohlc_clipping(source_day):
    raw = source_day.copy()
    raw.loc[12, "high"] = 1.0
    result = qa.process_month(raw, "2026-03", "0" * 64, "raw")
    assert raw.loc[12, "high"] == 1.0
    assert len(result.canonical) == 389 and len(result.proxies) == 1
    assert result.proxies.iloc[0].fill_reason == "INVALID"
    assert result.hourly.iloc[0].observed_volume == 118.0


def test_next_session_open_cannot_borrow_previous_close(source_day, monkeypatch):
    base = qa.calendar_frame("2026-03")
    second = base.copy()
    for col in ("timestamp", "hour_start_utc", "hour_end_utc"):
        second[col] += pd.Timedelta(days=1)
    second["session_date_et"] = "2026-03-03"
    monkeypatch.setattr(
        qa, "calendar_frame", lambda month: pd.concat([base, second], ignore_index=True)
    )
    day2 = source_day.copy()
    day2["timestamp"] += pd.Timedelta(days=1)
    day2 = day2.iloc[1:].copy()
    result = qa.process_month(pd.concat([source_day, day2]), "2026-03", "0" * 64, "raw")
    assert result.proxies.empty
    hour = result.hourly.loc[result.hourly.session_date_et == "2026-03-03"].iloc[0]
    assert not hour.open_is_genuine and hour.opening_minutes_missing


def test_real_calendar_duration_and_uninterrupted_runs():
    from lstm_data.hf_minute_long_report import duration_pass, window_runs

    first = pd.Timestamp("2011-06-30 09:30", tz="America/New_York")
    end = first + pd.DateOffset(years=14, months=9)
    assert duration_pass(first, end, 14, 9)
    assert not duration_pass(first, end - pd.Timedelta(minutes=1), 14, 9)
    starts = pd.date_range("2026-03-02 14:30", periods=4, freq="h", tz="UTC")
    rows = window_runs(
        starts, starts + pd.Timedelta(hours=1), np.array([True, False, True, True]), "TEST"
    )
    assert rows[0]["common_full_hours"] == 2 and rows[1]["common_full_hours"] == 1


def test_human_july2010_cutoff_before_source_access(tmp_path):
    from lstm_data.hf_minute_long_io import acquire_month
    from lstm_data.hf_minute_long_report import reconstruct_month

    guard = Guard(tmp_path)
    with pytest.raises(ValueError, match="pre-July2010 acquisition prohibited"):
        acquire_month(dict(month="2010-06"), tmp_path, guard)
    with pytest.raises(ValueError, match="pre-July2010 processing prohibited"):
        qa.process_month(pd.DataFrame(), "2010-06", "0" * 64, "unused")
    with pytest.raises(ValueError, match="pre-July2010 reconstruction prohibited"):
        reconstruct_month({}, "2010-06")
    assert not list(tmp_path.iterdir())


def test_completed_staged_source_reused_without_network(tmp_path, monkeypatch):
    from lstm_data.config import digest
    from lstm_data.hf_minute_long_io import LoggedHTTP, stream_full

    staged = tmp_path / "provider.parquet.part"
    transport_bytes = b"immutable completed transport snapshot"
    staged.write_bytes(transport_bytes)
    source = dict(bytes=staged.stat().st_size, lfs_sha256=digest(staged))
    http = LoggedHTTP(tmp_path / "http.jsonl")

    def forbidden(*args, **kwargs):
        raise AssertionError("A verified completed source must not be downloaded twice")

    monkeypatch.setattr(http.session, "get", forbidden)
    assert stream_full(source, tmp_path, http, Guard(tmp_path)) == staged
    assert http.bytes_received == 0 and not http.events
    staged.write_bytes(b"x" * len(transport_bytes))
    with pytest.raises(ValueError, match="completed staged source checksum changed"):
        stream_full(source, tmp_path, http, Guard(tmp_path))


def test_all_hour_accounting_detects_missing_volume_or_minute_count(source_day):
    from lstm_data.hf_minute_long_report import verify_hourly_consistency

    result = qa.process_month(source_day, "2026-03", "0" * 64, "raw")
    verify_hourly_consistency(result.hourly, result.canonical)
    changed = result.hourly.copy()
    changed["observed_volume"] = changed.observed_volume + 1
    with pytest.raises(ValueError, match="full-history hourly accounting failed"):
        verify_hourly_consistency(changed, result.canonical)
    changed = result.hourly.copy()
    changed.loc[0, "absent_minutes"] = 1
    with pytest.raises(ValueError, match="full-history hourly accounting failed"):
        verify_hourly_consistency(changed, result.canonical)


def test_guard_retains_source_nan_separately_from_null_and_infinity(tmp_path):
    from lstm_data.hf_minute_long_io import tables_equal

    table = pa.table(dict(price=[float("nan"), None, float("inf"), 1.0]))
    path = tmp_path / "invalid_source_evidence.parquet"
    guard = Guard(tmp_path)
    receipt = guard.parquet(path, table)
    assert guard.parquet(path, table)["sha256"] == receipt["sha256"]
    swapped = pa.table(dict(price=[None, float("nan"), float("inf"), 1.0]))
    assert not tables_equal(table, swapped)
    with pytest.raises(ValueError, match="existing output differs"):
        guard.parquet(path, swapped)


def test_reconstruction_detects_proxy_range_invention_hidden_inside_hour_range(
    source_day, tmp_path
):
    from lstm_data.config import digest
    from lstm_data.hf_minute_long_report import reconstruct_month

    raw = source_day.drop(index=10)
    raw_path = tmp_path / "raw.parquet"
    raw.to_parquet(raw_path, index=False)
    result = qa.process_month(raw, "2026-03", digest(raw_path), str(raw_path))
    hour_path = tmp_path / "hour.parquet"
    proxy_path = tmp_path / "proxy.parquet"
    result.hourly.to_parquet(hour_path, index=False)
    result.proxies.to_parquet(proxy_path, index=False)
    state = dict(
        raw=dict(path=str(raw_path), sha256=digest(raw_path)),
        qa=dict(
            files=dict(
                hourly_ohlcv=dict(path=str(hour_path)), fill_proxies_cap5=dict(path=str(proxy_path))
            )
        ),
    )
    assert all(r["reconstruction_pass"] for r in reconstruct_month(state, "2026-03"))
    # This would not alter the resulting hourly high (10.1), so an hourly-only
    # OHLC equality check cannot detect the invented proxy high.
    changed = result.proxies.copy()
    changed["high"] = 10.05
    changed.to_parquet(proxy_path, index=False)
    with pytest.raises(ValueError, match="sampled-hour reconstruction failed"):
        reconstruct_month(state, "2026-03")
