"""Hermetic boundary, raw-integrity and bounded acquisition oracles for Package018C."""

from __future__ import annotations

import io
import json

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
import requests

from lstm_data import hf_minute_boundary as boundary
from lstm_data.config import digest
from lstm_data.hf20_source import SYMBOLS
from lstm_data.hf_hourly_source import PublicHTTP
from lstm_data.hf_minute_boundary_io import DATASET, REVISION, RemoteParquet


def candles() -> pd.DataFrame:
    _, grid = boundary.session_grid("2026-03")
    return pd.DataFrame(
        dict(
            timestamp=grid.as_unit("ns"),
            open=10.0,
            high=11.0,
            low=9.0,
            close=10.0,
            volume=100.0,
            ticker="VZ",
        )
    )


def source_table(frame: pd.DataFrame) -> pa.Table:
    table = pa.Table.from_pandas(frame, preserve_index=False)
    return table.set_column(6, "ticker", pa.array(frame.ticker.tolist(), type=pa.string()))


def test_schema_exact_filter_and_original_row_offsets():
    f = candles().iloc[:4].copy()
    f["ticker"] = ["VZ", "vz", "AAPL", "SPY"]
    table = source_table(f)
    boundary.validate_schema(table.schema)
    selected = boundary.add_provenance(table, dict(path="data/ohlcv_2026-03.parquet"), 3, 100)
    assert selected.column("ticker").to_pylist() == ["VZ", "AAPL"]
    assert selected.column("source_row").to_pylist() == [100, 102]
    assert selected.column("is_genuine").to_pylist() == [True, True]
    assert selected.select(boundary.COLUMNS).equals(table.take(pa.array([0, 2])))
    assert len(SYMBOLS) == len(set(SYMBOLS)) == 20
    with pytest.raises(ValueError, match="STOP_IDENTITY"):
        boundary.validate_schema(table.set_column(0, "timestamp", pa.array([1, 2, 3, 4])).schema)


def test_calendar_dst_holiday_and_early_close():
    sessions, grid = boundary.session_grid("2026-03")
    assert len(sessions) == 22 and len(grid) == 8580
    assert sessions[0].open.hour == 14
    assert next(s for s in sessions if str(s.day.date()) == "2026-03-09").open.hour == 13
    november, _ = boundary.session_grid("2025-11")
    half = next(s for s in november if str(s.day.date()) == "2025-11-28")
    assert (half.close - half.open).total_seconds() == 210 * 60
    assert all(str(s.day.date()) != "2025-11-27" for s in november)


def test_quality_absence_and_missing_gap_are_not_imputed(monkeypatch):
    monkeypatch.setattr(boundary, "SYMBOLS", ("VZ", "COP"))
    f = candles()
    before = f.copy(deep=True)
    summary, _, _ = boundary.audit_month(f, "2026-03")
    assert summary[0]["state"] == "USABLE"
    assert summary[1]["state"] == "NOT_PRESENT" and summary[1]["actual_rows"] == 0
    pd.testing.assert_frame_equal(before, f)
    broken = f.drop(f.index[[10, 11, 12]])
    summary, _, _ = boundary.audit_month(broken, "2026-03")
    assert summary[0]["max_consecutive_missing"] == 3
    assert summary[0]["state"] == "INSUFFICIENT"
    assert len(broken) == len(f) - 3


def test_duplicate_conflict_and_bad_ohlc_produce_reviewable_evidence(monkeypatch):
    monkeypatch.setattr(boundary, "SYMBOLS", ("VZ",))
    f = candles()
    duplicate = f.iloc[[100]].copy()
    duplicate["volume"] = 200.0
    bad = pd.concat([f, duplicate], ignore_index=True)
    bad.loc[120, "high"] = 1.0
    summary, _, evidence = boundary.audit_month(bad, "2026-03")
    assert summary[0]["duplicate_rows"] == 2
    assert summary[0]["conflicting_duplicate_rows"] == 2
    assert summary[0]["malformed_rows"] == 1
    assert summary[0]["state"] == "INSUFFICIENT"
    assert any(r["kind"] == "INVALID_OR_DUPLICATE" for r in evidence)


def test_range_reader_pin_size_and_bounds(monkeypatch):
    http = PublicHTTP(1000)
    calls = []

    def get(url, maximum, byte_range=None):
        calls.append((url, maximum, byte_range))
        return b"x" * maximum

    monkeypatch.setattr(http, "get", get)
    remote = RemoteParquet(http, "data/ohlcv_2026-03.parquet", 100)
    remote.seek(-8, io.SEEK_END)
    assert remote.read(20) == b"x" * 8
    assert REVISION in calls[0][0] and "main" not in calls[0][0]
    assert calls[0][2] == (92, 99)
    with pytest.raises(ValueError, match="STOP_STORAGE"):
        remote.read()
    with pytest.raises(ValueError, match="STOP_IDENTITY"):
        RemoteParquet(http, "data/../old.parquet", 100)
    response = requests.Response()
    response.status_code = 206
    response.request = requests.Request(
        "GET", "https://huggingface.co/test", headers={"Range": "bytes=92-99"}
    ).prepare()
    response.headers["Content-Range"] = "bytes 92-99/101"
    with pytest.raises(ValueError, match="STOP_SOURCE"):
        remote.validate_response(response)


def test_storage_guard_counts_staging_and_cache_and_records_hash(tmp_path):
    staging = tmp_path / "scratch"
    cache = tmp_path / "cache"
    staging.mkdir()
    cache.mkdir()
    (staging / "month.part").write_bytes(b"x" * 100)
    (cache / "xet.bin").write_bytes(b"y" * 200)
    guard = boundary.ResourceGuard((staging, cache), tmp_path / "guard.jsonl")
    record = guard.check(1000, "test")
    assert record["current_bytes"] == 300 and len(record["sha256"]) == 64
    with pytest.raises(ValueError, match="STOP_STORAGE"):
        guard.check(9_000_000_000, "too_large")


def test_atomic_extract_resume_and_corruption_rejection(tmp_path, monkeypatch):
    monkeypatch.setattr(boundary, "BASE", tmp_path / "new_raw")
    f = candles().iloc[:4].copy()
    f["ticker"] = ["VZ", "SPY", "AAPL", "VZ"]
    upstream = tmp_path / "fixture.parquet"
    pq.write_table(source_table(f), upstream)
    original_parquet = pq.ParquetFile
    real = original_parquet(upstream)
    monkeypatch.setattr(boundary, "RemoteParquet", lambda *args: upstream)
    counts = {s: int((f.ticker == s).sum()) for s in SYMBOLS}
    source = dict(month="2026-03", path="data/ohlcv_2026-03.parquet", bytes=upstream.stat().st_size)
    loc = dict(
        source=source,
        source_rows=4,
        counts=counts,
        groups=[dict(row_group=0, rows=4, selected_counts={"VZ": 2, "AAPL": 1})],
    )
    guard = boundary.ResourceGuard((tmp_path,), tmp_path / "guard.jsonl")
    destination = boundary.partition_path("2026-03")
    result = boundary.acquire(loc, destination, guard, PublicHTTP(1000))
    assert result["source_rows_equal_independently_read_output"]
    assert result["rows"] == 3 and digest(destination) == result["sha256"]
    assert not destination.with_suffix(".part").exists()
    assert upstream.exists() and real.metadata.num_rows == 4
    assert boundary.acquire(loc, destination, guard, PublicHTTP(1000))["reused_verified_partition"]
    manifest = json.loads(destination.with_suffix(".manifest.json").read_text())
    assert manifest["source"]["path"] == source["path"]
    destination.write_bytes(b"corruption")
    with pytest.raises(ValueError, match="STOP_IDENTITY"):
        boundary.acquire(loc, destination, guard, PublicHTTP(1000))


def test_max_run_includes_endpoints():
    assert boundary.longest_run(np.array([True, True, False, True])) == 2
    assert boundary.longest_run(np.array([False, False])) == 0
    assert DATASET == "mito0o852/OHLCV-1m"


def test_uncommitted_partition_and_old_namespace_are_never_overwritten(tmp_path, monkeypatch):
    monkeypatch.setattr(boundary, "BASE", tmp_path / "new_raw")
    destination = boundary.partition_path("2026-03")
    destination.parent.mkdir(parents=True)
    destination.with_suffix(".part").write_bytes(b"interrupted source extraction")
    location = dict(source=dict(month="2026-03"))
    guard = boundary.ResourceGuard((tmp_path,), tmp_path / "guard.jsonl")
    with pytest.raises(ValueError, match="STOP_INTERRUPTED_RESUMABLE"):
        boundary.acquire(location, destination, guard, PublicHTTP(1000))
    assert destination.with_suffix(".part").read_bytes() == b"interrupted source extraction"
    old = tmp_path / "old_hf20.parquet"
    old.write_bytes(b"old protected bytes")
    with pytest.raises(ValueError, match="STOP_IDENTITY"):
        boundary.acquire(location, old, guard, PublicHTTP(1000))
    assert old.read_bytes() == b"old protected bytes"
