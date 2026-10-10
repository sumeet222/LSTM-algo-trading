import pandas as pd
import pytest

from lstm_data.aggregation import aggregate_session_hours
from lstm_data.alignment import asof_diagnostic
from lstm_data.calendar import fully_inside_rth, stock_qa
from lstm_data.cli import main
from lstm_data.config import digest, write_json
from lstm_data.pilot import load_pilot_samples
from lstm_data.store import acquire, chunk_paths, monthly_requests, read_verified


def half_hours(start="2020-07-01T13:30Z", count=13):
    return pd.DataFrame(
        {
            "symbol": ["AAPL"] * count,
            "timestamp": pd.date_range(start, periods=count, freq="30min"),
            "open": [100 + i for i in range(count)],
            "high": [102 + i for i in range(count)],
            "low": [99 + i for i in range(count)],
            "close": [101 + i for i in range(count)],
            "volume": [10] * count,
            "trade_count": [3] * count,
            "source_timeframe": "30Min",
            "feed": "sip",
            "adjustment": "split",
        }
    )


def test_complete_session_pairs_and_stub_without_duplication():
    source = half_hours()
    hours, qa = aggregate_session_hours(source, ["AAPL"], "2020-07-01", "2020-07-01")
    assert qa["timing_gate_pass"]
    assert len(hours) == 7
    assert hours.iloc[0].open == 100
    assert hours.iloc[0].close == 102
    assert hours.iloc[0].high == 103
    assert hours.iloc[0].low == 99
    assert hours.iloc[0].volume == 20
    assert hours.iloc[0].trade_count == 6
    assert hours.iloc[-1].duration_minutes == 30
    assert hours.iloc[-1].is_stub
    assert hours.iloc[-1].source_bar_count == 1
    assert hours.iloc[-1].available_at == pd.Timestamp("2020-07-01T20:00Z")
    assert hours.volume.sum() == source.volume.sum()
    assert "vwap" not in hours


def test_missing_constituent_emits_mask_and_never_manufactures_ohlcv():
    source = half_hours().drop(index=1)
    hours, qa = aggregate_session_hours(source, ["AAPL"], "2020-07-01", "2020-07-01")
    assert not qa["timing_gate_pass"]
    assert qa["missing_source_bars"] == 1
    assert len(hours) == 6
    assert not qa["windows"][0]["complete"]
    assert pd.Timestamp("2020-07-01T13:30Z") not in set(hours.timestamp)


def test_early_close_and_dst_windows():
    hours, qa = aggregate_session_hours(
        half_hours("2020-11-27T14:30Z", 7), ["AAPL"], "2020-11-27", "2020-11-27"
    )
    assert qa["timing_gate_pass"]
    assert len(hours) == 4
    assert hours.iloc[-1].available_at == pd.Timestamp("2020-11-27T18:00Z")
    for day, utc in [("2021-03-12", "2021-03-12T14:30Z"), ("2021-03-15", "2021-03-15T13:30Z")]:
        hours, qa = aggregate_session_hours(half_hours(utc), ["AAPL"], day, day)
        assert qa["timing_gate_pass"]
        assert hours.iloc[0].timestamp.tz_convert("America/New_York").hour == 9


def test_future_and_extended_source_bars_do_not_change_session_aggregates():
    source = half_hours()
    original, _ = aggregate_session_hours(source, ["AAPL"], "2020-07-01", "2020-07-01")
    extra = half_hours("2020-07-02T13:30Z")
    extra["open"] = 1000
    extra["high"] = 1002
    extra["low"] = 999
    extra["close"] = 1001
    appended = pd.concat([source, extra], ignore_index=True)
    changed, _ = aggregate_session_hours(appended, ["AAPL"], "2020-07-01", "2020-07-01")
    pd.testing.assert_frame_equal(original, changed)


def test_half_hour_stock_qa_and_rth_selection_use_real_duration():
    source = half_hours()
    qa = stock_qa(source, ["AAPL"], "2020-07-01", "2020-07-01")
    assert qa["native_session_anchored_gate_pass"]
    assert qa["source_interval_minutes"] == 30
    assert len(fully_inside_rth(source, "2020-07-01", "2020-07-01")) == 13


def test_stub_alignment_uses_its_actual_end_not_an_extra_half_hour():
    hours, _ = aggregate_session_hours(half_hours(), ["AAPL"], "2020-07-01", "2020-07-01")
    course = half_hours("2020-07-01T19:00Z", 4).drop(columns="symbol")
    joined, summary = asof_diagnostic(hours.tail(1), course, index_delay_minutes=0)
    assert joined.iloc[0].decision_time == pd.Timestamp("2020-07-01T20:00Z")
    assert joined.iloc[0].index_timestamp == pd.Timestamp("2020-07-01T20:00Z")
    assert summary["stock_availability_policy"] == "explicit available_at"


def test_pilot_sample_load_checks_hash(cfg):
    path = cfg["_root"] / "sample.parquet"
    half_hours().to_parquet(path, index=False)
    report = cfg["_root"] / "pilot.json"
    write_json(
        report,
        {
            "config_fingerprint": cfg["_fingerprint"],
            "probes": [{"sample_path": "sample.parquet", "sample_sha256": digest(path)}],
        },
    )
    assert len(load_pilot_samples(cfg, report)) == 13
    path.write_bytes(path.read_bytes() + b"tamper")
    with pytest.raises(ValueError, match="checksum"):
        load_pilot_samples(cfg, report)


def test_hourly_source_cannot_be_relabelled_as_half_hours():
    source = half_hours()
    source["source_timeframe"] = "1Hour"
    with pytest.raises(ValueError, match="30Min"):
        aggregate_session_hours(source, ["AAPL"], "2020-07-01", "2020-07-01")


def test_pilot_alignment_cli_sorts_reverse_order_probe_windows(cfg, monkeypatch):
    cfg["timeframe"] = "30Min"
    cfg["symbols"] = ["AAPL"]
    cfg["start_date"] = "2020-07-01"
    cfg["end_date"] = "2020-07-02"
    probes, requests, source_parts = [], [], []
    for day in ["2020-07-02", "2020-07-01"]:
        frame = half_hours(day + "T13:30Z")
        path = cfg["_root"] / (day + ".parquet")
        frame.to_parquet(path, index=False)
        probes.append({"sample_path": path.name, "sample_sha256": digest(path)})
        requests.append(
            {
                "start_date": day,
                "end_date": day,
                "params": {"start": day + "T00:00Z", "end": day + "T23:59Z", "symbols": "AAPL"},
            }
        )
        source_parts.append(frame.drop(columns="symbol"))
    report = cfg["_root"] / "pilot.json"
    write_json(
        report, {"config_fingerprint": cfg["_fingerprint"], "probes": probes, "requests": requests}
    )
    course = pd.concat(source_parts).sort_values("timestamp").reset_index(drop=True)
    monkeypatch.setattr("lstm_data.cli.load_config", lambda *_: cfg)
    monkeypatch.setattr("lstm_data.cli.audit_course", lambda *_: (course, {}))
    output = cfg["_root"] / "alignment"
    assert main(["alignment", "--pilot-report", str(report), "--output", str(output)]) == 0
    assert (output / "alignment.json").exists()


def test_bulk_preserves_real_gap_with_metadata_and_without_fill(cfg, monkeypatch):
    cfg["timeframe"] = "30Min"
    cfg["symbols"] = ["AAPL"]
    cfg["start_date"] = cfg["end_date"] = "2020-07-01"
    source = half_hours().drop(index=1).reset_index(drop=True)
    monkeypatch.setattr("lstm_data.store.check_approval", lambda *_: {})

    class Client:
        events = []

        def bars(self, _params):
            return source

    result = acquire(cfg, Client(), cfg["_root"] / "unused")
    assert result[0]["coverage_audit"]["missing_source_bars"] == 1
    assert len(result[0]["coverage_audit"]["incomplete_windows"]) == 1
    params = monthly_requests(cfg)[0]
    path, manifest = chunk_paths(cfg["_stock_store"], params)
    stored = read_verified(path, manifest, params)
    assert len(stored) == len(source)
    assert pd.Timestamp("2020-07-01T14:00Z") not in set(stored.timestamp)
