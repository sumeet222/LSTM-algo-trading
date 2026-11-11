"""Fabricated source tape exercises the production replay, never historical cash."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lstm_data.trading.track2.stage012.calendar_schedule import MarketClock
from lstm_data.trading.track2.stage012.model_registry import SYMBOLS
from lstm_data.trading.track2.stage35.final_backtest_v4 import driver, release
from lstm_data.trading.track2.stage35.final_backtest_v4.market import Day, minute
from lstm_data.trading.track2.stage35.final_backtest_v4.protocol import ARMS, Scenario


class FabricatedMarket:
    def __init__(self, first, last):
        self.clock = MarketClock("2020-12-01", "2022-01-01")
        self.ogn = {}
        self.first = first
        self.last = last

    def days(self):
        for date in pd.date_range(self.first, self.last):
            day = str(date.date())
            origins = self.clock.origins(day)
            if not origins:
                continue
            starts = np.arange(minute(origins[0]), minute(origins[0]) + 390)
            values = np.full((390, 20), 100.0)
            records = []
            for origin in origins:
                for i, ticker in enumerate(SYMBOLS):
                    row: dict[str, object] = dict(
                        origin=origin,
                        endpoint=self.clock.endpoint(origin),
                        ticker=ticker,
                        input_eligible=True,
                        direction=1 if i % 2 else -1,
                        checkpoint_hash="FABRICATED_MODEL",
                        issued_at=origin + pd.Timedelta(minutes=2),
                        matched_four_arms=True,
                    )
                    for arm in ARMS:
                        row["g_" + arm] = 1.0
                    records.append(row)
            yield Day(
                day,
                starts,
                values,
                values,
                np.full((390, 20), 100000.0),
                np.ones((390, 20), bool),
                pd.DataFrame(records),
                "FABRICATED_SOURCE",
                {},
            )


def test_fabricated_production_replay_all_arms_and_reproducibility(tmp_path, monkeypatch):
    # The only replacement data reader is a hardcoded fabricated tape; no
    # historical reader survives this test's admission stub.
    monkeypatch.setattr(driver, "Market", FabricatedMarket)
    monkeypatch.setattr(driver, "load_actions", lambda: ())
    monkeypatch.setattr(release, "check_admission", lambda *args: None)
    summaries = []
    journals = []
    for name in ("one", "two"):
        engine = driver.Driver((Scenario(),), "2021-01-04", "2021-01-05", tmp_path / name)
        summaries.append(engine.run())
        journals.append(tuple(a.journal_hash for a in engine.accounts))
        assert all(a.maximum_residual <= driver.D("1e-8") for a in engine.accounts)
        assert all(
            a.quantity.sum() == sum(lot.quantity for lot in a.lots.values())
            for a in engine.accounts
        )
    assert journals[0] == journals[1]
    assert summaries[0]["opportunities"] == 280
    assert summaries[0]["terminal_pending_orders"] == 0


def test_real_driver_without_admission_refuses_before_market_or_output(tmp_path, monkeypatch):
    def forbidden(*args):
        raise AssertionError("must reject before opening historical source")

    monkeypatch.setattr(driver, "Market", forbidden)
    output = tmp_path / "must_not_exist"
    with pytest.raises(PermissionError, match="MISSING_RESEARCH_ADMISSION"):
        driver.Driver((Scenario(),), "2021-01-04", "2021-01-05", output)
    assert not output.exists()


def test_primary_source_facts_and_full_input_coverage_are_real_not_economic():
    root = Path("trading/track2/stage35/final_backtest_v4")
    source = json.loads((root / "MRK_OGN_SOURCE_AND_ACCOUNTING_MANIFEST_V4.json").read_text())
    assert source["primary_terms_verified"]
    scan = json.loads((root / "RAW_SOURCE_AND_SIGNAL_PREFLIGHT_V4.json").read_text())
    assert scan["totals"]["forecasts"] == 131111
    assert scan["totals"]["matched"] == 87557
    assert len(scan["sources"]) == 48
    assert scan["financial_outputs"] is False
    assert scan["post2024_price_reads"] == 0


def test_checkpoint_restart_preserves_entire_fabricated_book(tmp_path, monkeypatch):
    monkeypatch.setattr(driver, "Market", FabricatedMarket)
    monkeypatch.setattr(driver, "load_actions", lambda: ())
    monkeypatch.setattr(release, "check_admission", lambda *args: None)
    whole = driver.Driver((Scenario(),), "2021-01-04", "2021-01-05", tmp_path / "whole")
    whole.run()
    cut = driver.Driver((Scenario(),), "2021-01-04", "2021-01-05", tmp_path / "restart")
    cut.run(stop_after=1)
    point = tmp_path / "restart/checkpoints/2021-01-04.json"
    resumed = driver.Driver.restart(point, tmp_path / "restart", None)
    resumed.run()
    assert [a.journal_hash for a in resumed.accounts] == [a.journal_hash for a in whole.accounts]
    assert [a.cash for a in resumed.accounts] == [a.cash for a in whole.accounts]
    assert [a.claims for a in resumed.accounts] == [a.claims for a in whole.accounts]
    import gzip

    with gzip.open(tmp_path / "restart/baseline/daily.jsonl.gz", "rt") as f:
        rest = f.read()
    with gzip.open(tmp_path / "whole/baseline/daily.jsonl.gz", "rt") as f:
        full = f.read()
    assert rest == full


def test_checkpoint_corruption_and_unknown_class_fail_closed():
    from lstm_data.trading.track2.stage35.final_backtest_v4.checkpoint import decode, seal, unseal

    value = seal(Scenario())
    value["sha256"] = "tampered"
    with pytest.raises(ValueError, match="CHECKPOINT_CORRUPT"):
        unseal(value)
    with pytest.raises(ValueError, match="UNKNOWN_CHECKPOINT_SCHEMA"):
        decode({"class": "arbitrary_import"})


@pytest.mark.parametrize(
    "day", ["2012-10-26", "2012-10-30", "2018-12-04", "2024-11-29", "2024-03-08"]
)
def test_indexed_execution_calendar_equals_frozen_clock(day):
    from datetime import datetime, timedelta, timezone

    from lstm_data.trading.track2.stage35.final_backtest_v4.execution_calendar import (
        ExecutionCalendar,
    )

    clock = MarketClock("2012-01-01", "2025-01-10")
    fast = ExecutionCalendar(clock)
    for hour in (13, 17, 20, 23):
        submitted = datetime.fromisoformat(day).replace(hour=hour, tzinfo=timezone.utc)
        for offset in (0, 1, 59):
            at = submitted + timedelta(minutes=offset)
            assert fast.next(minute(at)) == minute(clock.next_observation(at))


def test_edited_pass_flags_are_not_a_research_release(tmp_path, monkeypatch):
    from lstm_data.trading.track2.stage35.final_backtest_v4.paths import canonical

    monkeypatch.setattr(release, "ROOT", tmp_path)
    (tmp_path / "audits").mkdir()
    (tmp_path / "FINAL_CONSOLIDATED_PROTOCOL.json").write_text(json.dumps({"pilot_windows": []}))
    folder = tmp_path / "forged"
    folder.mkdir()
    binding = {
        "mode": "financial",
        "files": {},
        "owner": {
            "period": ["2021-01-01", "2024-12-31"],
            "arms": list(ARMS),
            "live_or_paper": False,
        },
    }
    (folder / "RESEARCH_AUTHORIZATION_AND_BINDING_V4.json").write_text(json.dumps(binding))
    report = {
        "overall": "PASS",
        "binding_sha256": canonical(binding),
        "gates": {gate: "PASS" for gate in release.GATES},
    }
    (folder / "RESEARCH_BACKTEST_READINESS_V4.json").write_text(json.dumps(report))
    fake = release.Admission(folder, canonical(binding), "financial")
    with pytest.raises(PermissionError):
        release.check_admission(fake, "2021-01-01", "2024-12-31", False)
    assert list((tmp_path / "audits").glob("rejection_*.json"))
    assert not (tmp_path / "performance").exists()


def test_actual_frozen_action_roundtrip_preserves_dates_and_confidence():
    from lstm_data.trading.track2.stage35.completion_v3.tapes import load_actions
    from lstm_data.trading.track2.stage35.final_backtest_v4.checkpoint import seal, unseal

    actions = load_actions()
    value = unseal(seal(actions))
    assert value == actions


def test_nullable_classical_control_does_not_suppress_equal_attainable(tmp_path, monkeypatch):
    from dataclasses import replace

    class NullableMarket(FabricatedMarket):
        def days(self):
            for day in super().days():
                frame = day.signals.copy()
                for arm in ("ROLLING_RISK", "EWMA_RISK"):
                    frame["g_" + arm] = pd.Series([None] * len(frame), dtype=object)
                frame["matched_four_arms"] = False
                yield replace(day, signals=frame)

    monkeypatch.setattr(driver, "Market", NullableMarket)
    monkeypatch.setattr(driver, "load_actions", lambda: ())
    monkeypatch.setattr(release, "check_admission", lambda *args: None)
    engine = driver.Driver((Scenario(),), "2021-01-04", "2021-01-04", tmp_path / "nullable")
    engine.run()
    for account in engine.accounts:
        if account.population == "attainable" and account.arm in ("EQUAL", "S2C_RISK"):
            assert account.order_seq > 0
        else:
            assert account.order_seq == 0


def test_nullable_multiplier_is_an_abstention_not_a_numeric_cast():
    from decimal import Decimal

    from lstm_data.trading.track2.stage35.final_backtest_v4.protocol import valid_multiplier

    for value in (None, pd.NA, float("nan"), float("inf"), 0, -1, True, "1"):
        assert not valid_multiplier(value)
    for value in (1.0, 1, Decimal(".75"), np.float64(1.2)):
        assert valid_multiplier(value)


def test_unobservable_submitted_fill_is_not_replaced_by_a_later_bar(tmp_path, monkeypatch):
    from dataclasses import replace

    class MissingEventMarket(FabricatedMarket):
        def days(self):
            for day in super().days():
                mask = day.valid.copy()
                # First opening decision is at open+3, order targets open+4.
                mask[4, 0] = False
                yield replace(day, valid=mask)

    monkeypatch.setattr(driver, "Market", MissingEventMarket)
    monkeypatch.setattr(driver, "load_actions", lambda: ())
    monkeypatch.setattr(release, "check_admission", lambda *args: None)
    engine = driver.Driver((Scenario(),), "2021-01-04", "2021-01-04", tmp_path / "unknown")
    result = engine.run()
    assert result["unresolved"]
    for account in engine.accounts:
        assert account.nav_incomplete
        assert account.pending[0].status == "UNRESOLVED_SOURCE_BAR"
        assert account.quantity[0] == 0
        assert account.nav() is None
        assert sum(abs(r.delta) for r in account.pending[0].requests) > 0
        assert account.capacity(100000000)[3] == "UNRESOLVED_EXECUTION"


def test_known_future_order_does_not_make_current_marked_equity_unknown(tmp_path, monkeypatch):
    from dataclasses import replace

    class ShockCloseMarket(FabricatedMarket):
        def days(self):
            for day in super().days():
                prices = day.closes.copy()
                if day.date == "2021-01-04":
                    prices[-1, :] = 130.0
                yield replace(day, closes=prices)

    monkeypatch.setattr(driver, "Market", ShockCloseMarket)
    monkeypatch.setattr(driver, "load_actions", lambda: ())
    monkeypatch.setattr(release, "check_admission", lambda *args: None)
    engine = driver.Driver((Scenario(),), "2021-01-04", "2021-01-05", tmp_path / "future_order")
    engine.run()
    first = [row for row in engine.daily if row["date"] == "2021-01-04"]
    assert any(row["pending_orders"] for row in first)
    assert all(row["status"] == "OBSERVED" and row["nav"] is not None for row in first)
