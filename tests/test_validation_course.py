import pandas as pd
import pytest

from lstm_data.config import atomic_new, digest
from lstm_data.course import audit_course
from lstm_data.validation import defects, normalize, parse_utc, require_valid


def frame(times=("2020-07-01T14:00:00Z", "2020-07-01T15:00:00Z")):
    return pd.DataFrame(
        {"timestamp": times, "open": 100, "high": 101, "low": 99, "close": 100, "volume": 0.5}
    )


def test_parse_offset_and_dst():
    parsed = parse_utc(pd.Series(["2020-11-01T01:00:00-04:00", "2020-11-01T01:00:00-05:00"]))
    assert parsed.iloc[1] - parsed.iloc[0] == pd.Timedelta(hours=1)
    assert str(parsed.dt.tz) == "UTC"


@pytest.mark.parametrize("bad", ["2020-07-01 14:00:00", None, "invalid"])
def test_reject_bad_or_naive_timestamp(bad):
    with pytest.raises(ValueError):
        parse_utc(pd.Series([bad]))


def test_duplicates_not_silently_removed():
    data = normalize(frame(("2020-07-01T14:00:00Z",) * 2))
    assert defects(data)["duplicate_keys"] == 1
    assert len(data) == 2
    with pytest.raises(ValueError, match="duplicate_keys"):
        require_valid(data)


@pytest.mark.parametrize(
    "column,value,expected",
    [
        ("high", 98, "invalid_ohlc_rows"),
        ("low", 102, "invalid_ohlc_rows"),
        ("close", 0, "nonpositive_price_rows"),
        ("volume", -1, "negative_volume_rows"),
        ("close", float("inf"), "nonfinite_ohlcv_rows"),
        ("open", None, "null_fields"),
    ],
)
def test_invalid_values(column, value, expected):
    raw = frame()
    raw[column] = value
    data = normalize(raw)
    assert defects(data)[expected] > 0
    with pytest.raises(ValueError):
        require_valid(data)


def test_missing_schema_and_out_of_order():
    with pytest.raises(ValueError, match="Missing required"):
        normalize(frame().drop(columns="high"))
    assert defects(normalize(frame().iloc[::-1]))["out_of_order"]


def test_source_bytes_preserved_and_trailing_local_date(tmp_path):
    path = tmp_path / "course.csv"
    frame(("2025-06-30T20:00:00Z", "2025-07-01T04:00:00Z")).to_csv(path, index=False)
    before = path.read_bytes()
    _, audit = audit_course(path, "test provider", "2025-06-30", "2025-06-30")
    assert path.read_bytes() == before
    assert audit["sha256"] == digest(path)
    assert audit["outside_named_local_dates"] == 1
    assert audit["timestamp_semantics"] == "unknown"
    assert audit["defects"]["fractional_volume_rows"] == 2


def test_atomic_new_refuses_replacement(tmp_path):
    path = tmp_path / "nested/file"
    atomic_new(path, b"original")
    with pytest.raises(FileExistsError):
        atomic_new(path, b"replacement")
    assert path.read_bytes() == b"original"
    assert not list(path.parent.glob(".pending-*"))
