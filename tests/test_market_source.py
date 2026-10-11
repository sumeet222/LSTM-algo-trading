import json
from pathlib import Path

import pandas as pd
import pytest

from lstm_data.alpaca import HistoricalClient
from lstm_data.market_source import (
    DECISION_ID,
    AttemptBudget,
    MarketSource,
    acquire_partition,
    hourly_archive,
    load_archive,
)


def source_fixture(tmp_path: Path) -> MarketSource:
    cfg = json.loads(Path("configs/track_a_market_spy_v1.json").read_text())
    folder = tmp_path / "configs"
    folder.mkdir()
    path = folder / "market.json"
    path.write_text(json.dumps(cfg))
    return MarketSource.load(path)


def coarse(day: str = "2020-07-01", count: int = 13) -> pd.DataFrame:
    starts = pd.date_range(f"{day} 09:30", periods=count, freq="30min",
                           tz="America/New_York").tz_convert("UTC")
    return pd.DataFrame({"timestamp": starts, "symbol": "SPY", "open": 100.,
                         "high": 103., "low": 99., "close": 102., "volume": 10.,
                         "feed": "sip", "adjustment": "raw", "source_timeframe": "30Min"})


def test_selector_and_missing_no_fallback(tmp_path):
    source = source_fixture(tmp_path)
    assert source.config["decision_id"] == DECISION_ID
    assert len(source.partitions()) == 11
    assert source.partitions()[-1]["end"] == "2025-07-01T03:59:59.999999999+00:00"
    with pytest.raises(FileNotFoundError, match="MISSING_SPY"):
        load_archive(source)


@pytest.mark.parametrize("change", [{"symbols": ["USA500"]}, {"symbols": []},
                                    {"feed": "iex"}, {"adjustment": "split"},
                                    {"research_status": "PASS"}])
def test_selector_rejects_wrong_policy(tmp_path, change):
    source = source_fixture(tmp_path)
    path = tmp_path / "configs/market.json"
    path.write_text(json.dumps(source.config | change))
    with pytest.raises(ValueError, match="NO_FALLBACK"):
        MarketSource.load(path)


@pytest.mark.parametrize("day,count,hours,utc_hour", [
    ("2020-07-01", 13, 6, 13), ("2021-01-04", 13, 6, 14),
    ("2020-11-27", 7, 3, 14),
])
def test_anchored_hours_stubs_and_unknown_publication(day, count, hours, utc_hour):
    result, qa = hourly_archive(coarse(day, count), day, day)
    assert qa["timing_gate_pass"]
    assert len(result) == hours + 1
    assert result.iloc[0].period_start.hour == utc_hour
    assert result.iloc[0].period_start.minute == 30
    assert result.iloc[0].period_end == result.iloc[1].period_start
    assert result.iloc[-1].is_stub and result.iloc[-1].duration_minutes == 30
    assert result.iloc[0].volume == 20
    assert result.iloc[0].close == 102
    assert result.available_at.isna().all()
    assert set(result.available_at_basis) == {"UNKNOWN"}


def test_missing_constituent_invalidates_whole_hour():
    frame = coarse().drop(index=1)
    hours, qa = hourly_archive(frame, "2020-07-01", "2020-07-01")
    assert len(hours) == 6
    assert qa["missing_source_bars"] == 1
    assert hours.iloc[0].period_start.hour == 14
    assert hours.iloc[0].period_start.minute == 30


@pytest.mark.parametrize("change", [{"feed": "iex"}, {"adjustment": "all"},
                                    {"symbol": "AAPL"}, {"high": 50.}])
def test_hourly_rejects_policy_and_ohlc(change):
    frame = coarse()
    for key, value in change.items():
        frame[key] = value
    with pytest.raises(ValueError):
        hourly_archive(frame, "2020-07-01", "2020-07-01")


def test_spy_short_page_retry_checkpoint_resume_and_hash(tmp_path):
    source = source_fixture(tmp_path)
    responses = iter([
        (503, {}), (200, {"bars": {"SPY": [{"t": "2020-03-19T13:30:00Z",
            "o": 100, "h": 103, "l": 99, "c": 102, "v": 10}]},
            "next_page_token": "fixture-continuation"}),
        (200, {"bars": {"SPY": [{"t": "2020-03-19T14:00:00Z",
            "o": 102, "h": 103, "l": 99, "c": 101, "v": 10}]}}),
    ])
    calls = []

    class Response:
        headers: dict[str, str] = {}

        def __init__(self, status, body):
            self.status_code, self.body = status, body

        def json(self):
            return self.body

    def get(url, **kwargs):
        calls.append(kwargs["params"])
        return Response(*next(responses))

    client = HistoricalClient(source.config, "fixture", "fixture", get=get, sleep=lambda _: None)
    params = source.partitions()[0]
    first = acquire_partition(source, client, params)
    assert len(calls) == 3 and first["rows"] == 2
    assert calls[2]["page_token"] == "fixture-continuation"
    assert all(p["adjustment"] == "raw" and p["feed"] == "sip" for p in calls)
    assert acquire_partition(source, client, params) == first
    assert len(calls) == 3
    path = next(source.store.glob("*.parquet"))
    path.write_bytes(path.read_bytes() + b"corrupt")
    with pytest.raises(ValueError, match="checksum"):
        acquire_partition(source, client, params)


def test_partial_page_budget_never_checkpoints(tmp_path):
    source = source_fixture(tmp_path)
    page = 0

    class Response:
        status_code = 200
        headers: dict[str, str] = {}

        def json(self):
            return {"bars": {"SPY": []}, "next_page_token": str(page)}

    def get(url, **kwargs):
        nonlocal page
        page += 1
        return Response()

    client = HistoricalClient(source.config, "fixture", "fixture", get=get, sleep=lambda _: None)
    with pytest.raises(RuntimeError, match="page budget"):
        acquire_partition(source, client, source.partitions()[0])
    assert page == 2
    assert not source.store.exists()


def test_attempt_budget_exhaustion_and_truncation_are_offline(tmp_path):
    journal = tmp_path / "attempts.jsonl"
    journal.write_bytes(b'{"stage":"fixture"}\n' * 60)
    budget = AttemptBudget(journal, "fixture")
    with pytest.raises(RuntimeError, match="BUDGET_EXHAUSTED"):
        budget.get("https://data.alpaca.markets/v2/stocks/bars")
    assert budget.used == 60
    journal.write_bytes(b'{"stage":"fixture"}')
    with pytest.raises(ValueError, match="TRUNCATED"):
        budget.used
