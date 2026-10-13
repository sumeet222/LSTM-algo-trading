"""Candidate-only source qualification; no empirical features or future outcomes."""

import json
from pathlib import Path

import pandas as pd
import pytest
import requests

from lstm_data import candidate_acquisition as acquisition
from lstm_data import candidate_quality as quality
from lstm_data.alpaca import ENDPOINT, DataAccessError, HistoricalClient
from lstm_data.calendar import schedule
from lstm_data.config import digest, fingerprint, load_config, write_json
from lstm_data.remediation_transport import StorageLimit, publish_chunk
from lstm_data.store import chunk_paths


def params():
    return dict(
        symbols="EXAMPLE",
        start="2021-04-19T04:00:00+00:00",
        end="2021-04-20T03:59:59.999999999+00:00",
        timeframe="30Min",
        feed="sip",
        adjustment="split",
        currency="USD",
        asof="2025-06-30",
        sort="asc",
        limit=10000,
    )


def frame(day="2021-04-19"):
    c = schedule(day, day).iloc[0]
    return pd.DataFrame(
        [
            dict(
                symbol="EXAMPLE",
                timestamp=t,
                open=10.0,
                high=11.0,
                low=9.0,
                close=10.0,
                volume=100.0,
                feed="sip",
                adjustment="split",
                source_timeframe="30Min",
            )
            for t in pd.date_range(c.open, c.close, freq="30min", inclusive="left")
        ]
    )


@pytest.mark.parametrize("run", [0, 1, 2, 3, 12, 13])
def test_exact_run_reconciliation_and_terminal(run, monkeypatch):
    f = frame().iloc[: 13 - run] if run else frame()
    monkeypatch.setattr(quality, "verified_frame", lambda ref: f)
    ref: dict = dict(
        data="synthetic",
        manifest="synthetic",
        sha256="synthetic",
        manifest_sha256="synthetic",
        params=params(),
    )
    audit = quality.audit_native([ref], "EXAMPLE", "2021-04-19", "2021-04-19")
    assert audit["summary"]["missing"] == len(audit["missing"]) == run
    assert audit["summary"]["longest_run"] == run
    assert audit["summary"]["terminal_missing"] == bool(run)
    assert all(r["interval_minutes"] == 30 for r in audit["missing"])
    if run:
        assert sum(r["run_size"] for r in audit["clusters"]) == run
        assert sum(r["terminal_stub"] for r in audit["missing"]) == 1


@pytest.mark.parametrize(
    "day,count,utc",
    [("2020-11-27", 7, "14:30"), ("2021-03-12", 13, "14:30"), ("2021-03-15", 13, "13:30")],
)
def test_early_close_and_dst(day, count, utc, monkeypatch):
    f = frame(day)
    monkeypatch.setattr(quality, "verified_frame", lambda ref: f)
    p = params()
    midnight = pd.Timestamp(day, tz="America/New_York").tz_convert("UTC")
    p.update(
        start=midnight.isoformat(),
        end=(midnight + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)).isoformat(),
    )
    r = quality.audit_native(
        [
            dict(
                data="synthetic",
                manifest="synthetic",
                sha256="synthetic",
                manifest_sha256="synthetic",
                params=p,
            )
        ],
        "EXAMPLE",
        day,
        day,
    )
    assert r["summary"]["observed"] == count and r["summary"]["missing"] == 0
    assert f.timestamp.iloc[0].strftime("%H:%M") == utc


def test_unknown_source_is_not_verified_absence():
    result = quality.audit_native([], "EXAMPLE", "2021-04-19", "2021-04-19")
    assert result["missing"] == [] and len(result["unknown"]) == 1
    assert not result["summary"]["full_interval_verified"]


def test_source_identity_duplicate_and_overlap_fail_closed(monkeypatch):
    ref: dict = dict(
        data="synthetic",
        manifest="synthetic",
        sha256="synthetic",
        manifest_sha256="synthetic",
        params=params(),
    )
    monkeypatch.setattr(
        quality, "verified_frame", lambda ref: pd.concat([frame(), frame().iloc[:1]])
    )
    with pytest.raises(ValueError, match="DUPLICATE"):
        quality.audit_native([ref], "EXAMPLE", "2021-04-19", "2021-04-19")
    monkeypatch.setattr(quality, "verified_frame", lambda ref: frame())
    with pytest.raises(ValueError, match="OVERLAPPING"):
        quality.audit_native([ref, ref], "EXAMPLE", "2021-04-19", "2021-04-19")
    ref["params"]["adjustment"] = "all"
    with pytest.raises(ValueError, match="IDENTITY"):
        quality.audit_native([ref], "EXAMPLE", "2021-04-19", "2021-04-19")


def test_formation60_uses_dollars_and_rejects_incomplete_sessions():
    clocks = schedule("2020-04-06", "2020-06-30")
    f = pd.DataFrame(
        [
            dict(
                symbol="EXAMPLE",
                timestamp=c.open.normalize() + pd.Timedelta(hours=4),
                close=100,
                volume=600_000,
                source_timeframe="1Day",
            )
            for _, c in clocks.iterrows()
        ]
    )
    result = quality.liquidity60(f, "EXAMPLE")
    assert result["daily_sessions"] == 60 and result["mean_daily_dollar_volume"] == 60_000_000
    assert result["liquidity_pass"]
    with pytest.raises(ValueError, match="FORMATION60"):
        quality.liquidity60(f.iloc[1:], "EXAMPLE")


def candidate(priority, missing=0, qualified=True):
    return dict(
        ticker=str(priority),
        priority=priority,
        sector="OTHER",
        missing=missing,
        terminal_missing=0,
        longest_run=min(missing, 2),
        historical_eligibility_qualified=qualified,
        liquidity_pass=True,
        source_complete=True,
    )


def test_formation_and_sector_guards_training_only_rank():
    rows = [candidate(1, qualified=False), candidate(3), candidate(2), candidate(4, 1)]
    assert [r["priority"] for r in quality.rank_candidates(rows, fixed_sectors=("FIXED",))] == [
        2,
        3,
        4,
    ]
    rows[0]["confirmation_missing"] = 0
    with pytest.raises(ValueError, match="TRAINING_ONLY"):
        quality.rank_candidates(rows, fixed_sectors=("FIXED",))
    rows = [candidate(1)]
    with pytest.raises(ValueError, match="DISTINCT"):
        quality.rank_candidates(rows, fixed_sectors=("OTHER",))


def test_zero_get_resume_works_at_exhausted_envelope_and_preserves_sha(tmp_path, monkeypatch):
    cfg = load_config(Path("configs/track_a_data.json"))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(acquisition, "verify_screen_authority", lambda: None)
    monkeypatch.setattr(acquisition, "load_config", lambda path: cfg)
    report = tmp_path / "report"
    archive = Path("data/raw/alpaca/diagnostic")
    p = params()
    store = archive / "targeted_30min"
    publish_chunk(
        store,
        frame(),
        p,
        [dict(kind="RESULT", status=200)],
        kind="TARGETED_30MIN",
        limit=StorageLimit((archive, report)),
    )
    data, manifest = chunk_paths(store, p)
    before = (digest(data), digest(manifest))
    pool = dict(
        package="SYNTHETIC",
        inherited_journals=[],
        archive=str(archive),
        inherited_attempts_charged=1000,
        candidates=[dict(ticker="EXAMPLE")],
        training_dates=["2021-04-19"],
        prehistory_start="2019-12-18",
    )
    write_json(report / "frozen_pool.json", pool)
    rows = [
        dict(
            params=p,
            kind="TARGETED_30MIN",
            request_hash=fingerprint(p),
            max_pages=12,
            max_attempts=1,
        )
    ]
    plan = dict(
        package="SYNTHETIC",
        pool_sha256=digest(report / "frozen_pool.json"),
        requests=rows,
        requests_sha256=fingerprint(rows),
    )
    write_json(report / "plan.json", plan)
    # An empty journal exists for the hypothetical exhausted inherited budget.
    (archive / "transport_attempts.jsonl").write_text("")
    monkeypatch.setattr(
        acquisition, "credentials", lambda: pytest.fail("RESUME_MUST_NOT_LOAD_SECRETS")
    )
    result = acquisition.acquire(
        report, report / "plan.json", get=lambda *a, **k: pytest.fail("NO_GET")
    )
    assert result["new_attempts"] == 0 and result["chunks"][0]["resumed_zero_GET"]
    assert before == (digest(data), digest(manifest))


def test_repeated_token_never_publishes_partial_and_tokens_are_hashed(tmp_path, monkeypatch):
    cfg = load_config(Path("configs/track_a_data.json"))
    monkeypatch.setattr("lstm_data.broad_screen.time.sleep", lambda s: None)

    def get(url, **kwargs):
        r = requests.Response()
        r.status_code = 200
        r._content = b'{"bars":{"EXAMPLE":[]},"next_page_token":"PRIVATE_TOKEN"}'
        return r

    journal = tmp_path / "journal.jsonl"
    transport = acquisition.CandidateTransport(journal, (params(),), get=get)
    c = HistoricalClient(
        dict(cfg, max_pages_per_request=12), "PRIVATE_KEY", "PRIVATE_SECRET", get=transport.request
    )
    with pytest.raises(DataAccessError):
        c.bars(params())
    assert transport.used == 2
    assert "PRIVATE_TOKEN" not in journal.read_text() and "PRIVATE_KEY" not in journal.read_text()
    assert (
        sum(
            json.loads(line)["kind"] == "CONTINUATION_HASH"
            for line in journal.read_text().splitlines()
        )
        == 2
    )


def test_cumulative_budget_rejects_before_send(tmp_path):
    transport = acquisition.CandidateTransport(
        tmp_path / "journal", (params(),), get=lambda *a, **k: pytest.fail("NO_GET")
    )
    transport.inherited_attempts = 1000
    with pytest.raises(DataAccessError, match="CUMULATIVE"):
        transport.request(ENDPOINT, params=params(), headers={}, timeout=1)
    assert transport.used == 0
