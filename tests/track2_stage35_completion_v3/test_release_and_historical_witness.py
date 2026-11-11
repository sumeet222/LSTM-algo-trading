"""Actual historical evidence stays nonfinancial; all economic release paths refuse."""

import json
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path

import pytest

from lstm_data.trading.track2.stage35.common import Price
from lstm_data.trading.track2.stage35.completion_v3.engine import historical_entry_v3
from lstm_data.trading.track2.stage35.completion_v3.event_ledger import (
    ClaimShareBook,
    ShareLot,
    sha,
)
from lstm_data.trading.track2.stage35.completion_v3.inventory import digest
from lstm_data.trading.track2.stage35.completion_v3.release import BINDINGS, GATES
from lstm_data.trading.track2.stage35.completion_v3.tapes import compile_events, load_actions

ROOT = Path("trading/track2/stage35/completion_v3")


@pytest.mark.parametrize("forge", [False, True])
def test_v3_flag_owner_env_source_relabelling_never_releases(tmp_path, monkeypatch, forge):
    monkeypatch.setenv("ALLOW_HISTORICAL_BACKTEST", "1")
    binding: dict[str, object] = {k: "candidate" for k in BINDINGS}
    binding["authorized_period"] = ["2021-01-01", "2024-12-31"]
    gates = {k: {"status": "PASS"} for k in GATES}
    gates["G_HUMAN"] = {
        "status": "PASS" if forge else "NOT_APPROVED",
        "actor_kind": "EXTERNAL_HUMAN",
        "approval_id": "agent-edited-flag",
        "approver": "pretended external reviewer",
        "approved_at": "2026-11-09T14:00:00Z",
    }
    gate = tmp_path / "gate.json"
    gate.write_text(json.dumps({"gates": gates, "binding": binding, "source_type": "SYNTHETIC"}))
    key = tmp_path / "key"
    key.write_text("untrusted public key text;no real key generated")
    output = tmp_path / "financial" / "performance.json"

    def loader(_):
        raise AssertionError("No historical financial loader is allowed to run")

    with pytest.raises(PermissionError):
        historical_entry_v3(gate, binding, key, tmp_path / "signature", output, loader)
    assert not output.parent.exists()


def test_raw_historical_price_cannot_enter_old_synthetic_ledger():
    from datetime import datetime
    from decimal import Decimal

    at = datetime.fromisoformat("2024-05-10T13:30:00+00:00")
    actual = Price(at, at, Decimal("1"), "actualsource", kind="HISTORICAL")
    with pytest.raises(ValueError, match="HISTORICAL_ECONOMICS_DISABLED"):
        actual.validate(at)


def test_actual_bounded_witness_has_claims_shares_no_financial_wealth_or_trades():
    report = json.loads((ROOT / "audits/HISTORICAL_CLAIM_SHARE_WITNESS_V3.json").read_text())
    assert report["source_rows"] == 11 and report["source_partitions"] == 5
    assert report["historical_orders"] == report["historical_fills"] == 0
    assert report["historical_NAV_or_PnL_or_return_computed"] is False
    assert report["model_forward_calls"] == report["post2024_price_reads"] == 0
    assert report["original_signal_rows_reused"] == 2
    assert len(report["dimensionless_allocations"]) == 8
    by_symbol = {b["source_action"]["symbol"]: b for b in report["books"]}
    assert by_symbol["AAPL"]["claim_cash_only"] == "1.00"
    assert by_symbol["TSLA"]["physical_share_sum"] == "12"
    assert by_symbol["MRK"]["unresolved"]
    for book in report["books"]:
        assert not {"nav", "pnl", "realized", "unrealized", "trade_price", "initial_cash"} & set(
            book
        )
        for before, after in zip(book["journal"], book["journal"][1:]):
            assert before["after"] == after["before"]


def test_future_action_changes_cannot_change_prior_due_tape_or_frozen_signals():
    actions = load_actions()
    earlier = tuple(
        e for e in actions if (e.ex_date or e.effective_date or date.max) < date(2024, 6, 1)
    )
    later = next(
        e for e in actions if e.symbol == "AAPL" and e.ex_date and e.ex_date > date(2024, 6, 1)
    )
    mutate = replace(later, payable_date=date(2025, 1, 1))
    before = compile_events(earlier + (later,), date(2024, 1, 1), date(2024, 5, 31))
    after = compile_events(earlier + (mutate,), date(2024, 1, 1), date(2024, 5, 31))
    assert before == after
    # Frozen signal production has no dependency edge to the newly constructed action tape.
    h0 = json.loads((ROOT / "audits/H0_PROVENANCE.json").read_text())
    coverage = Path("trading/track2/stage35/completion_v2/FULL_SIGNAL_COVERAGE_REPORT.json")
    expected = next(r["sha256"] for r in h0["protected"] if r["path"] == str(coverage))
    assert digest(coverage) == expected
    counts = json.loads(coverage.read_text())["totals"]
    assert counts["forecasts"] == 131111 and counts["matched"] == 87557


def test_carry_duplicate_and_overlap_cannot_double_charge():
    from datetime import datetime, timezone
    from decimal import Decimal

    t = datetime(2024, 1, 5, tzinfo=timezone.utc)
    end = t + timedelta(days=3)
    b = ClaimShareBook((ShareLot("s", "AAPL", Decimal(-4)),))
    b = b.carry("AAPL", t, end, Decimal(100), t, end, Decimal(".02"), "fixture")
    assert b.carry("AAPL", t, end, Decimal(100), t, end, Decimal(".02"), "fixture") == b
    with pytest.raises(ValueError, match="OVERLAP"):
        b.carry(
            "AAPL",
            t + timedelta(days=1),
            end + timedelta(days=1),
            Decimal(100),
            t,
            end + timedelta(days=1),
            Decimal(".02"),
            "fixture",
        )
    assert b.carry_expense_only == sum(v for _, v in b.carry_allocations)


def test_raw_covered_bytes_and_claim_source_truth_not_upgraded():
    coverage = json.loads((ROOT / "RAW_SHARE_SOURCE_COVERAGE_V3.json").read_text())
    assert coverage["oos_minute_partitions"] == 48
    assert coverage["PIT_corporate_action_certification"] is False
    assert coverage["missing_fixture_rows"] == []
    actions = load_actions()
    event = next(a for a in actions if a.symbol == "COP" and a.action_type == "CASH_DIVIDEND")
    assert event.publication_available_at_or_unknown is None
    assert sha(event.record())
