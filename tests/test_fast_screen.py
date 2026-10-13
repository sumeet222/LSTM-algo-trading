"""Finite selection, actual session runs and zero-GET immutable resumption."""

import itertools
import json

import pandas as pd
import pytest
import requests

from lstm_data.broad_screen import audit_day
from lstm_data.config import digest
from lstm_data.fast_inventory import expand_missing, saved_session_audit
from lstm_data.fast_screen import ALL, NEW, acquire, clusters, prepare, quality, select_four


def row(ticker, sector, missing=0, terminal=0, run=0, dv=100_000_000, qualified=True):
    return dict(
        ticker=ticker,
        sector=sector,
        missing=missing,
        terminal_missing=terminal,
        longest_run=run,
        dollar_volume=dv,
        liquidity_pass=qualified,
        affected_dates=int(missing > 0),
        action_identity_risk=1,
    )


def test_exact49_and_selection_matches_independent_all_stock_panel_oracle():
    assert len(ALL) == len(set(ALL)) == 49 and len(NEW) == 20
    assert "GM" in NEW and ALL[0] == "AAPL" and "AMZN" not in ALL
    rows = [
        row("AAPL", "Technology"),
        row("AA", "Staples", dv=200_000_000),
        row("AB", "Staples", dv=300_000_000),
        row("BA", "Comms"),
        row("CA", "Discretionary"),
        row("DA", "Industrial", 12, 1, 12),
        row("EA", "Financial", 13, 2, 9),
        row("FA", "Healthcare", qualified=False),
    ]
    selected, _ = select_four(rows)
    admissible = [r for r in rows if r["ticker"] != "AAPL" and r["liquidity_pass"]]
    panels = [
        p for p in itertools.combinations(admissible, 4) if len({r["sector"] for r in p}) == 4
    ]
    oracle = min(panels, key=lambda p: tuple(sorted((quality(r) for r in p), reverse=True)))
    assert {r["ticker"] for r in selected} == {r["ticker"] for r in oracle}
    assert [r["ticker"] for r in selected] == ["AB", "BA", "CA", "DA"]
    assert select_four(list(reversed(rows)))[0] == selected


def test_later_performance_cannot_choose_or_replace_symbols():
    rows = [row("AA", "one"), row("BB", "two"), row("CC", "three"), row("DD", "four")]
    before = select_four(rows)[0]
    changed = [dict(r, confirmation_performance=999, full_history_missing=0) for r in rows]
    assert [r["ticker"] for r in select_four(changed)[0]] == [r["ticker"] for r in before]
    with pytest.raises(ValueError, match="FOUR_LIQUIDITY"):
        select_four(rows[:3])


def test_early_close_dst_maximal_runs_and_exact_terminal_flags():
    # Thanksgiving Friday has six regular half-hours plus the closing stub.
    stamps = pd.date_range("2021-11-26T14:30Z", "2021-11-26T18:00Z", freq="30min", inclusive="left")
    retained = [t for i, t in enumerate(stamps) if i not in {1, 2, 6}]
    frame = pd.DataFrame(
        [
            dict(
                symbol="COST",
                timestamp=t,
                open=1.0,
                high=1.0,
                low=1.0,
                close=1.0,
                volume=1.0,
                source_timeframe="30Min",
            )
            for t in retained
        ]
    )
    day = audit_day(frame, "COST", "2021-11-26")
    assert (
        saved_session_audit(
            frame, "COST", "2021-11-26", stamps[0], pd.Timestamp("2021-11-26T18:00Z")
        )
        == day
    )
    assert day["expected"] == 7 and day["missing"] == 3 and day["longest_gap_half_hours"] == 2
    assert day["terminal_stub_missing"]
    gaps = clusters(day, dict(data="fixture", manifest="fixture", sha256="fixture"))
    assert [g["run_size"] for g in gaps] == [2, 1]
    absent = expand_missing(gaps)
    assert sum(r["terminal_stub"] for r in absent) == 1
    assert len(absent) == 3 and all("-05:00" in r["start_et"] for r in absent)
    frame["source_timeframe"] = "1Hour"
    with pytest.raises(ValueError, match="NATIVE_30MIN"):
        audit_day(frame, "COST", "2021-11-26")


def test_completed_empty_sources_resume_zero_get_with_original_journal_hash(tmp_path, monkeypatch):
    import lstm_data.fast_screen as module

    report = tmp_path / "report"
    report.mkdir()
    monkeypatch.setattr(module, "ARCHIVE", tmp_path / "archive")
    monkeypatch.setattr(module, "credentials", lambda: ("synthetic-key", "synthetic-secret"))
    prepare(report)
    calls = []

    def get(*args, **kwargs):
        calls.append(kwargs["params"])
        result = requests.Response()
        result.status_code = 200
        result._content = json.dumps({"bars": {}, "next_page_token": None}).encode()
        return result

    first = acquire(report, report / "screen_request_plan.json", get=get)
    assert len(calls) == 6 and len(first["chunks"]) == 6
    journal = tmp_path / "archive" / "transport_attempts.jsonl"
    sha = digest(journal)

    def forbidden(*args, **kwargs):
        raise AssertionError("GET on immutable completed resumption")

    second = acquire(report, report / "screen_request_plan.json", get=forbidden)
    assert all(c["resumed_zero_GET"] for c in second["chunks"])
    assert digest(journal) == sha and second["cumulative_attempts"] == first["cumulative_attempts"]


def test_per_stock_quality_preserves_gap_priorities():
    assert quality(row("A", "one", dv=50_000_000)) < quality(
        row("B", "one", 1, 0, 1, 9_000_000_000)
    )
    assert quality(row("A", "one", 2, 0, 2)) < quality(row("B", "one", 1, 1, 1))
    assert quality(row("A", "one", 8, 0, 2)) < quality(row("B", "one", 3, 0, 3))
