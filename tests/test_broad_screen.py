"""Source/grid/pool/quarantine tests; no network, empirical fitting or imputation."""

import json
from pathlib import Path

import pandas as pd
import pytest
import requests

from lstm_data import broad_screen as screen
from lstm_data.aggregation import aggregate_session_hours
from lstm_data.alpaca import ENDPOINT, DataAccessError, HistoricalClient
from lstm_data.calendar import schedule, stock_qa
from lstm_data.config import digest, fingerprint, write_json
from lstm_data.remediation_transport import StorageLimit, publish_chunk
from lstm_data.store import chunk_paths


def params(**changes):
    return dict(
        symbols="COST",
        start="2021-04-19T04:00:00+00:00",
        end="2021-04-20T03:59:59.999999999+00:00",
        timeframe="30Min",
        feed="sip",
        adjustment="split",
        currency="USD",
        asof="2025-06-30",
        sort="asc",
        limit=10000,
        **changes,
    )


def frame(day="2021-04-19", symbol="COST", hourly=False):
    clock = schedule(day, day).iloc[0]
    stamps = pd.date_range(clock.open, clock.close, freq="30min", inclusive="left")
    if hourly:
        stamps = pd.date_range(clock.open.floor("h"), clock.close, freq="h", inclusive="left")
    return pd.DataFrame(
        [
            dict(
                symbol=symbol,
                timestamp=t,
                open=100.0,
                high=101.0,
                low=99.0,
                close=100.0,
                volume=1000.0,
                feed="sip",
                adjustment="split",
                source_timeframe="1Hour" if hourly else "30Min",
            )
            for t in stamps
        ]
    )


@pytest.mark.parametrize(
    "day,count,open_utc",
    [
        ("2021-04-19", 13, "13:30"),
        ("2020-11-27", 7, "14:30"),
        ("2021-03-12", 13, "14:30"),
        ("2021-03-15", 13, "13:30"),
    ],
)
def test_exact_half_hour_calendar_stubs_and_dst(day, count, open_utc):
    source = frame(day)
    row = screen.audit_day(source, "COST", day)
    assert row["expected"] == row["actual"] == count and row["missing"] == 0
    assert source.timestamp.iloc[0].strftime("%H:%M") == open_utc
    hourly, _ = aggregate_session_hours(source, ["COST"], day, day)
    assert hourly.is_stub.sum() == 1 and hourly.iloc[-1].duration_minutes == 30
    assert hourly.iloc[-1].volume == 1000 and hourly.iloc[0].volume == 2000


def test_native_hourly_premarket_is_not_a_complete_half_hour_or_stub_audit():
    source = frame(symbol="AAPL", hourly=True)
    extra = source.iloc[:1].copy()
    extra["timestamp"] = pd.Timestamp("2021-04-19T08:00Z")
    source = pd.concat([extra, source], ignore_index=True)
    qa = stock_qa(source, ["AAPL"], "2021-04-19", "2021-04-19")
    assert not qa["native_session_anchored_gate_pass"]
    assert qa["symbols"]["AAPL"]["outside_session_bars"] == 1
    with pytest.raises(ValueError, match="30MIN"):
        screen.audit_day(source, "AAPL", "2021-04-19")


def test_missing_half_hours_and_missing_symbol_emit_no_fictional_prices():
    source = frame().iloc[:1]
    row = screen.audit_day(source, "COST", "2021-04-19")
    assert row["actual"] == 1 and row["missing"] == row["longest_gap_half_hours"] == 12
    assert row["terminal_stub_missing"]
    absent = screen.audit_day(source, "JPM", "2021-04-19")
    assert absent["actual"] == 0 and absent["missing"] == 13
    hourly, qa = aggregate_session_hours(source, ["COST"], "2021-04-19", "2021-04-19")
    assert hourly.empty and qa["missing_source_bars"] == 12


def test_holidays_duplicates_and_offgrid_are_not_zero_bar_success():
    source = frame()
    with pytest.raises(ValueError, match="SESSION"):
        screen.audit_day(source, "COST", "2021-07-05")
    with pytest.raises(ValueError):
        screen.audit_day(pd.concat([source, source.iloc[:1]]), "COST", "2021-04-19")
    source.loc[0, "timestamp"] = pd.Timestamp("2021-04-19T13:31Z")
    with pytest.raises(ValueError, match="OFF_GRID"):
        screen.audit_day(source, "COST", "2021-04-19")


def test_flexible_sectors_are_provisional_and_tech_controls_cannot_enter_panel():
    assert len(screen.POOL) == 29 and len(set(screen.POOL)) == 29
    assert len(screen.GROUPS) == 11
    assert screen.panel_identity(("AAPL", "COST", "HON", "CMCSA", "DUK"))
    assert screen.panel_identity(("AAPL", "JPM", "JNJ", "WMT", "CAT"))
    for symbols in (
        ("AAPL", "COST", "WMT", "CMCSA", "DUK"),
        ("AAPL", "MSFT", "HON", "CMCSA", "DUK"),
        ("COST", "AAPL", "HON", "CMCSA", "DUK"),
    ):
        with pytest.raises(ValueError):
            screen.panel_identity(symbols)


def test_flexible_five_sector_identity_uses_existing_p3_adapter_only_synthetically():
    from lstm_data.baseline_fixtures import feature_input
    from lstm_data.baseline_inputs import forecast_adapter, momentum
    from lstm_data.p3_domain import MODE, Permission, UniverseSpec

    for names in (("AAPL", "JPM", "JNJ", "WMT", "CAT"), ("AAPL", "COST", "HON", "CMCSA", "DUK")):
        universe = UniverseSpec("SYN:BROAD:" + screen.panel_identity(names), names)
        row = feature_input(universe)
        prediction = forecast_adapter(
            momentum(row, Permission(MODE), allow_synthetic=True),
            Permission(MODE),
            allow_synthetic=True,
        )
        assert prediction.universe == universe
        assert prediction.pair == (names[0], names[-1])


def test_fixed_mask_intersection_exactly_preserves_original_feature_derived_counts():
    names = ("AAPL", "JPM", "JNJ", "WMT", "CAT")
    folder = Path("reports/data_audit/ta_universe_screen_2026-10-12_092402")
    for filename, numerator in (
        ("original_origin_masks.json", 919),
        ("warmup_origin_masks.json", 1183),
    ):
        rows = json.loads((folder / filename).read_text())
        assert len(rows) == 1502 and len({r["id"] for r in rows}) == 1502
        masks = {s: {r["id"]: r["masks"][s] for r in rows} for s in names}
        assert len(screen.mask_intersection(masks, names)) == numerator
        assert set(screen.mask_intersection(masks, names)) == {
            r["id"] for r in rows if r["mechanical_ft0"]
        }
        masks.pop("CAT")
        with pytest.raises(ValueError, match="COMPLETE_FIVE"):
            screen.mask_intersection(masks, names)


def test_partial_origin_keys_and_one_invalid_channel_cannot_shrink_denominator():
    names = ("AAPL", "COST", "HON", "CMCSA", "DUK")
    masks = {s: {"one": 65535, "two": 65535} for s in names}
    masks["HON"]["one"] = 65534
    assert screen.mask_intersection(masks, names) == ("two",)
    del masks["DUK"]["one"]
    with pytest.raises(ValueError):
        screen.mask_intersection(masks, names)


def test_durable_redacted_pacing_and_lifetime_budget(tmp_path, monkeypatch):
    journal = tmp_path / "attempts.jsonl"
    sends = []
    sleeps = []
    monkeypatch.setattr(screen.time, "sleep", sleeps.append)

    def get(url, **kwargs):
        assert json.loads(journal.read_text().splitlines()[-1])["kind"] == "ATTEMPT"
        sends.append(url)
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"bars":{"COST":[]},"next_page_token":null}'
        return response

    transport = screen.BroadTransport(journal, (params(),), get=get)
    for _ in range(3):
        transport.request(ENDPOINT, params=params(), headers={"private": "SECRET"}, timeout=1)
    assert transport.used == len(sends) == 3 and "SECRET" not in journal.read_text()
    assert len(sleeps) == 2 and all(0 < s <= 0.6 for s in sleeps)
    with pytest.raises(DataAccessError, match="LIMIT"):
        transport.request(ENDPOINT, params=params(), headers={}, timeout=1)
    assert len(sends) == 3


@pytest.mark.parametrize(
    "status,content",
    [
        (401, b"{}"),
        (403, b"{}"),
        (429, b"{}"),
        (200, b'{"bars":{"ALIEN":[]}}'),
        (200, b'{"bars":[]}'),
    ],
)
def test_access_rate_and_population_schema_holds_stop_all_followup_pages(tmp_path, status, content):
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        response = requests.Response()
        response.status_code = status
        response._content = content
        return response

    transport = screen.BroadTransport(tmp_path / "j", (params(),), get=get)
    with pytest.raises(DataAccessError):
        transport.request(ENDPOINT, params=params(), headers={}, timeout=1)
    with pytest.raises(DataAccessError, match="HOLD"):
        transport.request(ENDPOINT, params=dict(params(), page_token="next"), headers={}, timeout=1)
    assert len(calls) == transport.used == 1


def test_hash_bound_journal_and_orphan_attempt_fail_closed(tmp_path):
    transport = screen.BroadTransport(tmp_path / "j", (params(),))
    transport.append({"kind": "ATTEMPT", "page_hash": "unknown", "time_utc": screen.now()})
    with pytest.raises(DataAccessError, match="UNRESOLVED"):
        transport.request(ENDPOINT, params=params(), headers={}, timeout=1)
    transport.journal.write_text(transport.journal.read_text() + "{}\n")
    with pytest.raises(DataAccessError, match="CONCURRENT"):
        transport.append({"kind": "HOLD"})


def test_split_and_raw_cache_identity_and_atomic_immutability(tmp_path):
    source = frame().iloc[:1]
    p = params()
    publish_chunk(tmp_path, source, p, [], kind="TARGETED_30MIN", limit=StorageLimit((tmp_path,)))
    saved = screen.read_candidate(tmp_path, p)
    assert saved is not None and saved[0].close.iloc[0] == 100.0
    before = digest(chunk_paths(tmp_path, p)[0])
    with pytest.raises(FileExistsError):
        publish_chunk(
            tmp_path, source, p, [], kind="TARGETED_30MIN", limit=StorageLimit((tmp_path,))
        )
    assert digest(chunk_paths(tmp_path, p)[0]) == before
    assert screen.read_candidate(tmp_path, dict(p, asof="-")) is None
    assert screen.read_candidate(tmp_path, dict(p, adjustment="raw")) is None
    # Synthetic2:1 split: preserve separate source observations, never convert cached raw.
    raw = source.copy()
    raw[["open", "high", "low", "close"]] *= 2
    raw["volume"] /= 2
    raw["adjustment"] = "raw"
    raw_params = dict(p, adjustment="raw")
    publish_chunk(
        tmp_path, raw, raw_params, [], kind="RAW_CONTROL", limit=StorageLimit((tmp_path,))
    )
    saved_raw = screen.read_candidate(tmp_path, raw_params)
    assert saved_raw is not None
    assert saved_raw[0].close.iloc[0] * saved_raw[0].volume.iloc[0] == 100_000
    saved_again = screen.read_candidate(tmp_path, p)
    assert saved_again is not None and saved_again[0].close.iloc[0] == 100.0


@pytest.mark.parametrize(
    "changes",
    [
        {"start": "2024-07-01T04:00:00Z", "end": "2024-07-02T03:59:59.999999999Z"},
        {"asof": "-"},
        {"feed": "iex"},
        {"symbols": "UNAPPROVED"},
        {"adjustment": "all"},
        {"timeframe": "1Min"},
    ],
)
def test_confirmation_source_and_symbol_quarantine_precedes_credentials(
    tmp_path, monkeypatch, changes
):
    monkeypatch.setattr(screen, "verify_screen_authority", lambda: {})
    monkeypatch.setattr(screen, "credentials", lambda: pytest.fail("credentials must not load"))
    write_json(tmp_path / "candidate_predeclared_pool.json", {"symbols": screen.POOL})
    p = dict(params(), **changes)
    rows = [{"kind": "TARGETED_30MIN", "params": p, "hash": fingerprint(p), "max_pages": 1}]
    write_json(
        tmp_path / "targeted_request_manifest.json",
        {
            "package": screen.PACKAGE,
            "requests": rows,
            "requests_sha256": fingerprint(rows),
            "pool_sha256": digest(tmp_path / "candidate_predeclared_pool.json"),
        },
    )
    with pytest.raises(ValueError):
        screen.acquire(tmp_path, get=lambda *a, **kw: pytest.fail("no network"))


def test_prequery_pool_freeze_and_five_date_plan_reproducibility(tmp_path, monkeypatch):
    monkeypatch.setattr(screen, "verify_screen_authority", lambda: {})
    monkeypatch.setattr(screen, "cache_sources", lambda: [])
    left = screen.prepare(tmp_path / "left")
    right = screen.prepare(tmp_path / "right")
    assert left == right and len(left["requests"]) == 7
    pool = json.loads((tmp_path / "left/candidate_predeclared_pool.json").read_text())
    assert pool["sector_status"] == "PROVISIONAL_2020_NOT_CERTIFIED"
    assert pool["production_universe_unchanged"] and len(pool["symbols"]) == 29
    days = [
        pd.Timestamp(r["params"]["start"]).tz_convert("America/New_York").strftime("%Y-%m-%d")
        for r in left["requests"]
        if r["kind"] == "TARGETED_30MIN"
    ]
    assert tuple(days) == screen.DATES


def test_bounded_pagination_exhaustion_never_publishes_partial_population():
    response = {"bars": {"COST": []}, "next_page_token": "repeat"}
    client = HistoricalClient({"max_pages_per_request": 2}, "fake", "fake")
    client._request = lambda params: response
    with pytest.raises(DataAccessError, match="Repeated"):
        client.bars(params())


def test_actual_close_absence_bounds_have_independent_daily_window_oracle():
    from lstm_data.clocks import execution_plan
    from lstm_data.m2 import scheduled_window
    from lstm_data.stock_source import StockCalendar

    folder = Path("reports/data_audit/ta_broad_universe_2026-10-13_000736")
    rows = json.loads((folder / "five_date_exact_keys.json").read_text())
    evidence = json.loads((folder / "panel_overlap_loss_attribution.json").read_text())
    cal = StockCalendar("2019-12-18", "2023-06-30")
    for symbol in screen.POOL:
        absent = {
            r["session_et"] for r in rows if r["symbol"] == symbol and r["terminal_stub_missing"]
        }
        invalid_days = set()
        for index, day in enumerate(cal.days):
            prior = cal.days[max(0, index - 21) : index]
            # Count actual missing adjacent endpoints independently of covered().
            good = sum(a not in absent and b not in absent for a, b in zip(prior, prior[1:]))
            if len(prior) < 21 or good < 19:
                invalid_days.add(day)
        expected = set()
        for day, clock in cal._sessions.items():
            if not "2020-07-01" <= day < "2023-07-01":
                continue
            for origin in (1, 2):
                if execution_plan(clock, origin).calendar_valid and any(
                    step.session in invalid_days for step in scheduled_window(cal, day, origin)
                ):
                    expected.add((day, origin))
        got = {(r["session"], r["origin"]) for r in evidence["failed_origins_by_symbol"][symbol]}
        assert got == expected
    assert evidence["maximum_upper"] == 1340 < evidence["required"] == 1352
    assert evidence["panels_enumerated"] == 12515
    assert evidence["measured_candidate_panels"] == 0
    assert evidence["scientific_status"] == "HOLD"
