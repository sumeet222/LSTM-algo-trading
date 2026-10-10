import json
from pathlib import Path

import pandas as pd
import pytest

from lstm_data.alpaca import credentials
from lstm_data.cli import main
from lstm_data.config import digest, load_config, write_json
from lstm_data.pilot import run_pilot
from lstm_data.store import (
    acquire,
    check_approval,
    chunk_paths,
    monthly_requests,
    plan,
    read_verified,
    save_chunk,
)
from lstm_data.validation import normalize


def stock_frame():
    return normalize(
        pd.DataFrame(
            {
                "symbol": ["AAPL"],
                "timestamp": ["2020-07-01T14:00Z"],
                "open": [100],
                "high": [101],
                "low": [99],
                "close": [100],
                "volume": [123],
                "feed": ["sip"],
                "adjustment": ["split"],
                "source_timeframe": ["1Hour"],
            }
        ),
        stocks=True,
    )


def one_chunk(cfg):
    cfg["symbols"] = ["AAPL"]
    cfg["start_date"] = "2020-07-01"
    cfg["end_date"] = "2020-07-31"
    return monthly_requests(cfg)[0]


def test_monthly_requests_exact_dates_dst_and_no_overlap(cfg):
    requests = monthly_requests(cfg)
    assert len(requests) == 60
    assert requests[0]["start"] == "2020-07-01T04:00:00+00:00"
    assert requests[-1]["end"] == "2025-07-01T03:59:59.999999999+00:00"
    for left, right in zip(requests, requests[1:]):
        assert pd.Timestamp(left["end"]) + pd.Timedelta(nanoseconds=1) == pd.Timestamp(
            right["start"]
        )
    assert requests[4]["end"].startswith("2020-12-01T04:59")


def test_store_roundtrip_no_overwrite_and_tamper_detection(cfg):
    params = one_chunk(cfg)
    store = cfg["_stock_store"]
    frame = stock_frame()
    saved = save_chunk(store, frame, params, [], cfg)
    path, manifest = chunk_paths(store, params)
    loaded = read_verified(path, manifest, params)
    assert saved["sha256"] == digest(path)
    assert loaded.timestamp.tolist() == frame.timestamp.tolist()
    assert "provenance_id" in loaded
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        save_chunk(store, frame, params, [], cfg)
    assert path.read_bytes() == before
    path.write_bytes(before + b"tamper")
    with pytest.raises(ValueError, match="checksum"):
        read_verified(path, manifest, params)


def test_resume_verified_chunk_makes_no_request(cfg, monkeypatch):
    params = one_chunk(cfg)
    save_chunk(cfg["_stock_store"], stock_frame(), params, [], cfg)
    monkeypatch.setattr("lstm_data.store.check_approval", lambda *_: {})

    class NoNetwork:
        def bars(self, *_):
            raise AssertionError("Verified chunk must not be fetched again")

    assert acquire(cfg, NoNetwork(), Path("unused"))[0]["resumed"]
    assert not (cfg["_stock_store"] / ".acquisition.lock").exists()


def test_interrupted_pair_stops_without_network(cfg, monkeypatch):
    params = one_chunk(cfg)
    path, _ = chunk_paths(cfg["_stock_store"], params)
    path.parent.mkdir(parents=True)
    path.write_bytes(b"unknown local work")
    monkeypatch.setattr("lstm_data.store.check_approval", lambda *_: {})
    with pytest.raises(ValueError, match="Interrupted"):
        acquire(cfg, object(), Path("unused"))
    assert path.read_bytes() == b"unknown local work"


def test_bulk_does_not_bypass_failed_pilot(cfg):
    pilot_path = cfg["_root"] / "pilot.json"
    write_json(
        pilot_path,
        {
            "config_fingerprint": cfg["_fingerprint"],
            "sip_access_pass": True,
            "timing_gate_pass": False,
        },
    )
    approval_path = cfg["_root"] / "approval.json"
    write_json(
        approval_path,
        {
            "approved": True,
            "config_fingerprint": cfg["_fingerprint"],
            "source_timeframe_approved": "1Hour",
            "session_aggregation_approved": True,
            "adjustment_approved": "split",
            "pilot_report": "pilot.json",
            "pilot_sha256": digest(pilot_path),
        },
    )
    with pytest.raises(ValueError, match="bulk blocked"):
        check_approval(cfg, approval_path)
    with pytest.raises(ValueError, match="bulk blocked"):
        acquire(cfg, object(), approval_path)
    assert not cfg["_stock_store"].exists()


def test_approval_bound_to_config_and_checksum(cfg):
    path = cfg["_root"] / "approval.json"
    write_json(path, {"approved": True, "config_fingerprint": "different"})
    with pytest.raises(ValueError, match="Approval"):
        check_approval(cfg, path)


def test_pilot_missing_credentials_preserves_useful_report(cfg, monkeypatch):
    for key in ("APCA_API_KEY_ID", "APCA_API_SECRET_KEY", "ALPACA_API_KEY", "ALPACA_API_SECRET"):
        monkeypatch.delenv(key, raising=False)
    output = cfg["_root"] / "reports/pilot"
    report = run_pilot(cfg, output)
    assert not report["sip_access_pass"]
    assert report["events"] == []
    assert report["sample_storage_bytes"] == 0
    assert "Missing" in report["diagnostic"]
    assert (output / "sip_pilot.md").exists()


def test_legacy_credentials_supported_without_printing(monkeypatch):
    monkeypatch.delenv("APCA_API_KEY_ID", raising=False)
    monkeypatch.delenv("APCA_API_SECRET_KEY", raising=False)
    monkeypatch.setenv("ALPACA_API_KEY", "fixture-legacy-key")
    monkeypatch.setenv("ALPACA_API_SECRET", "fixture-legacy-secret")
    assert credentials() == ("fixture-legacy-key", "fixture-legacy-secret")


@pytest.mark.parametrize(
    "command", ["source-audit", "sip-pilot", "download", "stock-qa", "alignment"]
)
def test_every_cli_dry_run_without_network_or_writes(command, tmp_path, monkeypatch, capsys):
    config = Path(__file__).resolve().parents[1] / "configs/track_a_data.json"

    def forbidden(*_args, **_kwargs):
        raise AssertionError("Dry run made network request")

    monkeypatch.setattr("requests.get", forbidden)
    output = tmp_path / "should-not-exist"
    assert main(["--config", str(config), command, "--dry-run", "--output", str(output)]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["network"] is False
    assert not output.exists()
    assert not printed["writes"]


def test_plan_storage_estimate_no_data_writes(cfg):
    planned = plan(cfg)
    assert (
        planned["estimated_30min_alternative_rows"]
        == 2 * planned["upper_calendar_session_hourly_rows_estimate"]
    )
    assert not cfg["_stock_store"].exists()


def test_configuration_refuses_unapproved_resolution_and_absolute_paths(tmp_path):
    original = Path(__file__).resolve().parents[1] / "configs/track_a_data.json"
    data = json.loads(original.read_text())
    path = tmp_path / "config.json"
    for updates, message in [
        ({"timeframe": "15Min"}, "Resolution"),
        ({"feed": "iex"}, "SIP"),
        ({"stock_store": "/developer/data"}, "project-relative"),
    ]:
        path.write_text(json.dumps(data | updates))
        with pytest.raises(ValueError, match=message):
            load_config(path)
