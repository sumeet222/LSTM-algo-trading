"""Hermetic source-only oracles: no live network, original prices, labels or neural fitting."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pytest

from lstm_data.hf_hourly_audit import (
    Census,
    calendar_grid,
    max_gap,
    quality_flags,
    require_schema,
    vendor_boundary_ok,
)
from lstm_data.hf_hourly_feasibility import best_overlap, evaluate, geometry, qualifying
from lstm_data.hf_hourly_source import PublicHTTP, download, validate_listing, verify_cached


def candle_frame() -> pd.DataFrame:
    return pd.DataFrame(
        dict(
            datetime=pd.to_datetime(["2024-03-08 14:30Z", "2024-03-11 13:30Z"]).tz_convert(
                "America/New_York"
            ),
            symbol=["SYN:A"] * 2,
            timeframe=["1h"] * 2,
            open=[10.0, 10.0],
            high=[12.0, 12.0],
            low=[9.0, 9.0],
            close=[11.0, 11.0],
            close_adj=[11.0, 11.0],
            volume=[100, 200],
        )
    )


def test_schema_timezone_columns_and_price_invariants():
    frame = candle_frame()
    schema = pa.Table.from_pandas(frame, preserve_index=False).schema
    require_schema(schema)
    wrong = schema.set(0, pa.field("datetime", pa.timestamp("us", tz="UTC")))
    with pytest.raises(ValueError, match="START_CLOCK"):
        require_schema(wrong)
    with pytest.raises(ValueError, match="MISSING"):
        require_schema(pa.schema([schema.field("datetime")]))
    assert quality_flags(frame).valid.all()
    frame.loc[0, "volume"] = -1
    frame.loc[1, "high"] = 9
    flags = quality_flags(frame)
    assert flags.negative_volume.iloc[0] and flags.bad_OHLC.iloc[1]
    assert not flags.valid.any()


def test_duplicates_nulls_and_adjusted_close_not_native_candle():
    frame = candle_frame()
    doubled = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
    assert quality_flags(doubled).duplicate_key.sum() == 2
    frame.loc[0, "close_adj"] = 8.0  # Legitimately separate representation, not a repaired candle.
    assert quality_flags(frame).valid.all()
    frame.loc[1, "open"] = 0
    frame.loc[0, "close_adj"] = np.nan
    flags = quality_flags(frame)
    assert flags.nonpositive_price.iloc[1] and flags.bad_close_adj.iloc[0]


def test_early_close_dst_and_complete_hour_missingness_oracle():
    grid, _ = calendar_grid("2023-11-24", "2023-11-24")
    assert len(grid) == 4 and int(grid.stub.sum()) == 1
    assert list(grid.start.dt.tz_convert("America/New_York").dt.hour) == [9, 10, 11, 12]
    assert grid.iloc[-1].end - grid.iloc[-1].start == pd.Timedelta(minutes=30)
    before, _ = calendar_grid("2024-03-08", "2024-03-08")
    after, _ = calendar_grid("2024-03-11", "2024-03-11")
    assert before.start.iloc[0].hour == 14 and after.start.iloc[0].hour == 13
    assert before.start.iloc[0].minute == after.start.iloc[0].minute == 30
    assert max_gap(np.array([True, False, False, True])) == 2
    assert max_gap(np.array([False, False, False])) == 3
    assert max_gap(np.array([True, True])) == 0


@pytest.mark.parametrize(
    "day,split,expected",
    [
        ("2023-12-31", "train", True),
        ("2024-01-01", "train", False),
        ("2024-12-31", "val", True),
        ("2025-01-01", "val", False),
        ("2025-01-01", "test", True),
        ("2024-12-31", "test", False),
    ],
)
def test_strict_vendor_split_boundaries(day: str, split: str, expected: bool):
    frame = candle_frame().iloc[[0]].copy()
    frame["datetime"] = pd.DatetimeIndex([pd.Timestamp(day + " 09:30", tz="America/New_York")])
    assert vendor_boundary_ok(frame, split) is expected


class FakeHTTP(PublicHTTP):
    def __init__(self, body: bytes, limit: int):
        super().__init__(limit)
        self.body = body
        self.calls = 0

    def get(self, url: str, maximum: int, byte_range: tuple[int, int] | None = None) -> bytes:
        self.calls += 1
        result = self.body[byte_range[0] : byte_range[1] + 1] if byte_range else self.body
        assert len(result) <= maximum
        self.bytes_received += len(result)
        return result


def fixture_row(body: bytes, name: str = "train") -> dict:
    return dict(
        path=f"bars_1h/{name}.parquet",
        size=len(body),
        lfs=dict(size=len(body), oid=hashlib.sha256(body).hexdigest()),
    )


def test_download_cap_denies_before_network_or_cache_mutation(tmp_path: Path):
    body = b"PAR1" + bytes(range(64)) + b"PAR1"
    files = [fixture_row(body, s) for s in ("train", "val", "test")]
    with pytest.raises(ValueError, match="DOWNLOAD_CAP"):
        validate_listing("a" * 40, files, len(body) * 3 - 1)
    http = PublicHTTP(1)
    with pytest.raises(ValueError, match="CAP_BEFORE"):
        http.get("https://huggingface.co/test", 2)
    fake = FakeHTTP(body, 1000)
    with pytest.raises(ValueError, match="STORAGE_CAP"):
        download(fake, tmp_path / "cache", tmp_path / "report", "a" * 40, files[0], 1)
    assert fake.calls == 0
    with pytest.raises(ValueError, match="IMMUTABLE"):
        validate_listing("main", files, 1000)


def test_exact_revision_cache_reuse_partial_resume_and_corruption(tmp_path: Path):
    body = b"PAR1" + bytes(range(64)) + b"PAR1"
    row = fixture_row(body)
    path = tmp_path / "cache" / ("a" * 40) / row["path"]
    path.parent.mkdir(parents=True)
    path.with_suffix(".parquet.part").write_bytes(body[:12])
    http = FakeHTTP(body, 1000)
    result = download(http, tmp_path / "cache", tmp_path / "report", "a" * 40, row, 10000)
    assert result["resumed_bytes"] == 12 and path.read_bytes() == body
    assert http.bytes_received == len(body) - 12 and http.calls == 1
    reused = download(http, tmp_path / "cache", tmp_path / "report", "a" * 40, row, 10000)
    assert reused["reused"] and http.calls == 1
    path.write_bytes(body[:-1] + b"X")
    with pytest.raises(ValueError, match="HASH_OR_SIZE"):
        verify_cached(path, row)
    assert http.calls == 1


def synthetic_census() -> Census:
    grid, session_table = calendar_grid("2023-10-01", "2024-01-31")
    full = grid.loc[~grid.stub].reset_index(drop=True)
    symbols = [f"SYN:{i:02d}" for i in range(21)]
    usable = np.ones((len(full), len(symbols)), dtype=bool)
    frames = []
    monthly = []
    for symbol in symbols:
        f = pd.DataFrame(
            dict(symbol=symbol, session=full.session, year=full.session.str[:4], valid=True)
        )
        frames.append(f)
        for month, group in full.groupby(full.session.str[:7]):
            monthly.append(
                dict(
                    symbol=symbol,
                    month=month,
                    usable_full_hours=len(group),
                    expected_full_hours=len(group),
                    no_usable_aligned_sessions=0,
                    invalid_rows=0,
                )
            )
    return Census(
        pd.concat(frames, ignore_index=True),
        full,
        grid,
        [str(d.date()) for d in session_table.index],
        symbols,
        usable,
        usable.copy(),
        pd.DataFrame(monthly),
        pd.DataFrame(),
        {},
        {},
    )


def test_no_label_or_price_selection_and_exact_48step_geometry():
    c = synthetic_census()
    config: dict[str, object] = dict(
        minimum_hour_coverage=0.995,
        maximum_consecutive_missing_hours=2,
        maximum_missing_entire_sessions=0,
        minimum_cohort=20,
    )
    overlap = best_overlap(c, config)
    assert len(overlap["best"]["qualifying_symbols"]) == 21
    assert overlap["best"]["start"] == "2023-10-02"
    origins, masks = geometry(c)
    assert masks.shape == (len(origins), 21) and masks.any()
    before = masks[:, 1:].copy()
    c.usable[60, 0] = False
    _, changed = geometry(c)
    assert np.array_equal(changed[:, 1:], before)
    assert changed[:, 0].sum() < masks[:, 0].sum()
    # A three-hour hole rejects this name without dropping peers or fabricating bars.
    c.usable[60:63, 0] = False
    good = qualifying(c, "2023-10-01", "2024-01-31", config)
    assert not good[0] and good[1:].all()
    config["identity_caution_exclusions"] = ["SYN:01"]
    assert not qualifying(c, "2023-10-01", "2024-01-31", config)[1]


def test_warmup_counts_complete_regular_sessions_and_requires_stub(tmp_path: Path):
    c = synthetic_census()
    # One otherwise complete regular day lacks its terminal row for every name.
    rows = []
    for symbol in c.symbols:
        selected = c.grid.loc[~(c.grid.session.eq("2023-10-02") & c.grid.stub)]
        rows.append(
            pd.DataFrame(
                dict(
                    symbol=symbol,
                    session=selected.session,
                    year=selected.session.str[:4],
                    valid=True,
                    UTC=selected.start,
                )
            )
        )
    c.frame = pd.concat(rows, ignore_index=True)
    config: dict[str, object] = dict(
        minimum_hour_coverage=0.995,
        maximum_consecutive_missing_hours=2,
        maximum_missing_entire_sessions=0,
        minimum_cohort=20,
        minimum_warmup_complete_regular_sessions=40,
        strict_start="2023-10-01",
        strict_end="2024-01-31",
        strict_prehistory_start="2023-10-01",
    )
    result = evaluate(c, config, {}, tmp_path)
    proposal = result["proposal"]
    assert proposal["warmup"]["complete_regular_sessions"] == 40
    # Oct2 is missing its stub; Nov24 is an early close, so neither counts.
    assert proposal["warmup"]["calendar_sessions"] == 42
    assert proposal["warmup"]["end"] == "2023-11-29"
    assert proposal["splits"][0]["start"] == "2023-11-30"
    assert all(row["target_values_created"] == 0 for row in proposal["splits"])
