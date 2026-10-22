"""Metadata-only rights/duration/snapshot gates; no network or financial bar fixtures."""

import json
import sys

import pandas as pd
import pytest

from lstm_data.config import digest, write_json
from lstm_data.hf_minute_preflight import (
    calendar_duration_pass,
    main,
    publish,
    required_start,
    rights_gate,
    validate_months,
)

REVISION = "e" * 40


def month(name="2011-06", size=100):
    return dict(
        path=f"data/ohlcv_{name}.parquet", type="file", size=size, lfs=dict(oid="a" * 64, size=size)
    )


def test_calendar_duration_is_not_inclusive_file_count():
    assert required_start("2026-03-31") == "2011-06-30"
    assert calendar_duration_pass("2011-06-30", "2026-03-31")
    assert not calendar_duration_pass("2011-07-01", "2026-03-31")
    assert calendar_duration_pass("2011-07-01", "2026-04-01")
    with pytest.raises(ValueError):
        calendar_duration_pass("2026-04-01", "2011-07-01")


def test_monthly_file_metadata_not_a_content_checksum_or_coverage_pass():
    rows = validate_months(REVISION, [month("2026-03"), month()])
    assert rows[0]["month"] == "2011-06" and rows[-1]["month"] == "2026-03"
    assert all(r["downloaded_bytes"] == 0 and r["persisted_raw_rows"] is None for r in rows)
    assert all(r["transfer_status"] == "NOT_REQUESTED_RIGHTS_GATE" for r in rows)
    with pytest.raises(ValueError):
        validate_months("main", [month()])
    with pytest.raises(ValueError):
        validate_months(REVISION, [month(), month()])
    bad = month()
    bad["lfs"] = dict(oid="a" * 64, size=101)
    with pytest.raises(ValueError):
        validate_months(REVISION, [bad])


@pytest.mark.parametrize("license_name", [None, "mit", "cc-by-4.0"])
def test_public_card_license_does_not_establish_underlying_finnhub_rights(license_name):
    r = rights_gate(
        dict(private=False, gated=False, cardData=dict(license=license_name)),
        [month()],
        "Originally sourced from Finnhub.io",
        "Do not redistribute without written approval",
    )
    assert r["public_access"] and r["provider_restriction_observed"]
    assert r["decision"] == "STOP_RIGHTS"
    assert r["local_research_permission"] == "UNSUBSTANTIATED"
    assert r["prior_Twelve_Data_attestation_applies"] is False


def test_wrong_source_remains_unverified():
    r = rights_gate({}, [month()], "Unknown origin", "")
    assert r["decision"] == "STOP_UNVERIFIED"


def snapshot(tmp_path):
    out = tmp_path / "snapshot"
    out.mkdir()
    info = dict(sha=REVISION, cardData={})
    listing = [month(), month("2026-03")]
    rights = rights_gate(info, listing, "Finnhub", "redistribution needs written approval")
    write_json(out / "dataset_info.json", info)
    write_json(out / "pinned_dataset_info.json", info)
    write_json(out / "pinned_tree.json", listing)
    (out / "dataset_card_snapshot.md").write_text("Finnhub")
    write_json(
        out / "http_events.json",
        dict(events=[dict(started_at="2026-10-22T18:00:00Z")], bytes_received=100),
    )
    write_json(out / "provider_terms_receipt.json", dict(bytes=50, restriction_observed=True))
    publish(out, dict(info=info, listing=listing, revision=REVISION, rights=rights))
    return out


def test_stop_publishes_unknown_rows_and_no_fake_data_release(tmp_path):
    out = snapshot(tmp_path)
    result = json.loads((out / "source_manifest.json").read_text())
    assert (
        result["downloaded_data_bytes"] == 0 and result["latest_genuinely_complete_month"] is None
    )
    assert result["common_genuine_start"] is None and not result["calendar_duration_verified"]
    assert len(result["missing_filename_months"]) > 100
    stocks = pd.read_csv(out / "coverage_preflight.csv")
    assert len(stocks) == 20 and stocks.first_genuine_minute_UTC.isna().all()
    planned = pd.read_csv(out / "stock_by_sampled_month.csv")
    assert planned.sampling_status.eq("NOT_SAMPLED_STOP_RIGHTS").all()
    assert planned.observed_rows.isna().all()
    assert not list(out.rglob("*.parquet"))
    assert not (out / "hourly_qa_report.md").exists()


def test_offline_snapshot_never_calls_network_or_decodes_parquet(tmp_path, monkeypatch):
    old = snapshot(tmp_path)
    new = tmp_path / "offline"

    def denied(*args, **kwargs):
        raise AssertionError("No network or numerical market I/O under STOP_RIGHTS")

    import requests

    monkeypatch.setattr(requests.Session, "get", denied)
    monkeypatch.setattr(pd, "read_parquet", denied)
    monkeypatch.setattr(sys, "argv", ["preflight", "--snapshot", str(old), "--out", str(new)])
    main()
    assert json.loads((new / "gate_record.json").read_text())["decision"] == "STOP_RIGHTS"
    assert (
        json.loads((new / "preflight_runtime.json").read_text())["network_requests_this_invocation"]
        == 0
    )
    assert digest(new / "dataset_info.json") == digest(old / "dataset_info.json")


def test_corrupted_snapshot_fails_closed_before_replay(tmp_path, monkeypatch):
    old = snapshot(tmp_path)
    (old / "dataset_info.json").write_text("{}")
    monkeypatch.setattr(
        sys, "argv", ["preflight", "--snapshot", str(old), "--out", str(tmp_path / "replay")]
    )
    with pytest.raises(ValueError, match="SNAPSHOT_HASH"):
        main()


def test_metadata_cannot_be_promoted_to_data_pass(tmp_path):
    with pytest.raises(ValueError, match="METADATA_CANNOT_PASS"):
        publish(tmp_path, dict(rights=dict(decision="PASS_TO_INCREMENTAL_DOWNLOAD")))


def test_forged_snapshot_permission_rejected(tmp_path, monkeypatch):
    old = snapshot(tmp_path)
    path = old / "source_manifest.json"
    manifest = json.loads(path.read_text())
    manifest["rights"]["decision"] = "PASS_TO_INCREMENTAL_DOWNLOAD"
    path.write_text(json.dumps(manifest))
    monkeypatch.setattr(
        sys, "argv", ["preflight", "--snapshot", str(old), "--out", str(tmp_path / "replay")]
    )
    with pytest.raises(ValueError, match="RIGHTS_GATE_CHANGED"):
        main()
