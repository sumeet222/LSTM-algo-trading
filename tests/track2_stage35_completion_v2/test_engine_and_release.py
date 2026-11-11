import json
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

import pytest
from test_settlement_v2 import T, bar, initial, order

from lstm_data.trading.track2.stage012.calendar_schedule import MarketClock
from lstm_data.trading.track2.stage35.completion_v2.engine import (
    ReplayEngine,
    ReplayEvent,
    historical_financial_entry,
)
from lstm_data.trading.track2.stage35.completion_v2.release import GATES, REQUIRED_BINDINGS


def test_engine_receipt_not_effective_time_controls_later_decisions():
    engine = ReplayEngine(
        "account1", "S2C_RISK", initial(), MarketClock("2024-01-01", "2024-02-01")
    )
    o = order()
    engine.add(o)
    assert not engine.decision_ready(T + timedelta(minutes=1))
    engine.process((ReplayEvent(T + timedelta(minutes=2), 1, "fill", "BAR", o, bar()),))
    assert engine.decision_ready(T + timedelta(minutes=2))
    j = engine.book.journal[-1]
    assert j.event_time == T and j.processed_at == T + timedelta(minutes=2)
    assert j.observation_time == T + timedelta(minutes=1)


def test_missing_bar_retains_uncertain_resting_and_inventory():
    engine = ReplayEngine(
        "account1", "S2C_RISK", initial(), MarketClock("2024-01-01", "2024-02-01")
    )
    o = order()
    engine.add(o)
    engine.process((ReplayEvent(T + timedelta(minutes=2), 1, "hole", "MISSING", o),))
    assert o.order_id in engine.pending and engine.book.unresolved
    assert not engine.decision_ready(T + timedelta(hours=1))
    assert sum(abs(x.pending) for x in engine.book.lots) == 16


def test_no_cross_account_or_holiday_fill():
    engine = ReplayEngine(
        "account1", "S2C_RISK", initial(), MarketClock("2024-01-01", "2024-02-01")
    )
    with pytest.raises(ValueError, match="ACCOUNT_ARM"):
        engine.add(replace(order(), arm="EQUAL"))
    o = replace(order(), event_minute=T + timedelta(days=7))  # MLK closure
    engine.add(o)
    with pytest.raises(ValueError, match="CLOSED_EXCHANGE"):
        engine.process(
            (
                ReplayEvent(
                    o.event_minute + timedelta(minutes=2),
                    1,
                    "bad",
                    "BAR",
                    o,
                    bar(at=o.event_minute),
                ),
            )
        )


@pytest.mark.parametrize("forge", [False, True])
def test_historical_release_denied_before_io_or_output(tmp_path: Path, forge):
    path = tmp_path / "gate.json"
    output = tmp_path / "financial" / "state.json"
    gates = {k: {"status": "PASS" if forge else "HOLD"} for k in GATES}
    gate = {"gates": gates, "binding": {}}
    binding = {k: "forged-or-candidate" for k in REQUIRED_BINDINGS}
    gate = {"gates": gates, "binding": binding}
    gates["G_HUMAN"] = {
        "status": "PASS" if forge else "NOT_APPROVED",
        "approval_id": "self_signed",
        "approver": "pretend external human",
        "actor_kind": "EXTERNAL_HUMAN",
        "approved_at": T.isoformat(),
    }
    path.write_text(json.dumps(gate))
    key = tmp_path / "key"
    key.write_text("not a trusted reviewer key")

    def loader(_):
        raise AssertionError("HISTORICAL SOURCE MUST NOT BE OPENED")

    with pytest.raises(PermissionError):
        historical_financial_entry(path, binding, key, tmp_path / "signature", output, loader)
    assert not output.parent.exists()


def test_mechanical_split_order_units_and_rate_segments():
    from test_settlement_v2 import quote

    from lstm_data.trading.track2.stage35.common import D
    from lstm_data.trading.track2.stage35.completion_v2.settlement import split_order_units

    clock = MarketClock("2024-01-01", "2024-02-01")
    old = order()
    adjusted = split_order_units(old, D(2), T - timedelta(seconds=20), T - timedelta(days=1))
    assert old.net == 4 and adjusted.net == 8 and adjusted.reference_price == 50
    with pytest.raises(ValueError, match="UNRESOLVED"):
        split_order_units(old, D(2), T - timedelta(seconds=20), T)
    eng = ReplayEngine("account1", "S2C_RISK", initial((("a", -6),)), clock)
    o = order((("a", -6),))
    eng.add(o)
    eng.process((ReplayEvent(T + timedelta(minutes=2), 1, "short", "BAR", o, bar()),))
    end = T + timedelta(days=1)
    eng.process(
        (ReplayEvent(end, 0, "rate", "RATE", reference=quote(end), ticker="AAPL", rate=D(".05")),)
    )
    first = sum(x.accrual for x in eng.book.lots)
    next_day = end + timedelta(days=1)
    eng.process(
        (
            ReplayEvent(
                next_day,
                0,
                "rate_segment_mark",
                "MARK",
                reference=quote(next_day, "150"),
                ticker="AAPL",
            ),
        )
    )
    second = sum(x.accrual for x in eng.book.lots)
    assert first == -D(600) * D(".02") / D(365)
    assert second == first - D(600) * D(".05") / D(365)
    eng.book.reconcile()


def test_fixed_seed_short_stress_has_no_market_or_profit_input():
    from lstm_data.trading.track2.stage35.completion_v2.tapes import fixed_short_stress

    dates = tuple(f"2024-01-{n:02}" for n in range(1, 31))
    a = fixed_short_stress(
        ("AAPL", "COP"), dates, seed=20261108, reject_per_million=100000, recall_per_million=100000
    )
    b = fixed_short_stress(
        ("COP", "AAPL"),
        tuple(reversed(dates)),
        seed=20261108,
        reject_per_million=100000,
        recall_per_million=100000,
    )
    assert a == b and {e.kind for e in a} == {"REJECT", "RECALL_BUY_IN"}
    assert all(e.scenario_id == "CONDITIONAL_SCENARIO_NOT_OBSERVED" for e in a)


def test_gap_liquidation_is_later_submitted_and_missing_close_retains_inventory():
    from lstm_data.trading.track2.stage35.common import D
    from lstm_data.trading.track2.stage35.completion_v2.orchestration import submit_liquidation

    eng = ReplayEngine(
        "account1", "S2C_RISK", initial((("a", 90),)), MarketClock("2024-01-01", "2024-02-01")
    )
    o = order((("a", 90),))
    eng.add(o)
    now = T + timedelta(minutes=2)
    eng.process((ReplayEvent(now, 1, "gap", "BAR", o, bar("2000")),))
    assert eng.book.capacity(now).status == "FUNDING_DEBT_HOLD"
    assert len(submit_liquidation(eng, now, {"AAPL": (D(100000), now)})) == 1
    close = next(iter(eng.pending.values()))
    assert close.event_minute > now and close.submitted_at == now
    eng.process(
        (ReplayEvent(close.event_minute + timedelta(minutes=2), 1, "halted_liq", "HALT", close),)
    )
    assert eng.book.positions[0].quantity == 90 and eng.book.unresolved


def test_known_partial_remainder_expires_but_unknown_resting_is_not_cancelled():
    from lstm_data.trading.track2.stage35.common import D
    from lstm_data.trading.track2.stage35.completion_v2.orchestration import (
        expire_unsubmitted_remainders,
    )

    clock = MarketClock("2024-01-01", "2024-02-01")
    eng = ReplayEngine("account1", "S2C_RISK", initial(), clock)
    o = replace(order(), external_capacity=D(2))
    eng.add(o)
    eng.process((ReplayEvent(T + timedelta(minutes=2), 1, "partial", "BAR", o, bar()),))
    held = tuple(lot.quantity for lot in eng.book.lots)
    cash = eng.book.cash
    assert expire_unsubmitted_remainders(eng, T + timedelta(minutes=8)) == ("a",)
    assert tuple(lot.quantity for lot in eng.book.lots) == held and eng.book.cash == cash
    assert not any(lot.pending for lot in eng.book.lots)
    unknown = ReplayEngine("account1", "S2C_RISK", initial(), clock)
    unknown.add(order())
    unknown.process((ReplayEvent(T + timedelta(minutes=2), 1, "missing", "MISSING", order()),))
    assert expire_unsubmitted_remainders(unknown, T + timedelta(minutes=8)) == ()
    assert unknown.book.unresolved and any(lot.pending for lot in unknown.book.lots)
