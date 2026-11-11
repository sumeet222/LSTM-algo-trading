"""Actual inference receipts separated from all-fabricated portfolio economics."""

import json
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

import pandas as pd
import pytest
from test_settlement_v2 import T

from lstm_data.trading.track2.stage012.calendar_schedule import MarketClock
from lstm_data.trading.track2.stage012.model_registry import SYMBOLS
from lstm_data.trading.track2.stage35.borrow_financing import BorrowEvidence, BorrowState
from lstm_data.trading.track2.stage35.common import D, Price
from lstm_data.trading.track2.stage35.completion_v2.engine import ReplayEngine, ReplayEvent
from lstm_data.trading.track2.stage35.completion_v2.intents import from_full_signal
from lstm_data.trading.track2.stage35.completion_v2.orchestration import PortfolioOrchestrator
from lstm_data.trading.track2.stage35.completion_v2.settlement import FinalBar, V2Book
from lstm_data.trading.track2.stage35.intents import SignalIntent

ROOT = Path("trading/track2/stage35/completion_v2")


def test_fabricated_all_twenty_intent_allocation_fill_and_fixed_exits():
    clock = MarketClock("2024-01-01", "2024-02-01")
    known = T - timedelta(minutes=1)
    book = V2Book.funded(D(100000))
    assert isinstance(book, V2Book)
    for ticker in SYMBOLS:
        marked = book.mark(
            "mark:" + ticker, ticker, Price(known, known, D(100), "FABRICATED"), known
        )
        assert isinstance(marked, V2Book)
        book = marked
    engine = ReplayEngine("fixture", "EQUAL", book, clock)
    manager = PortfolioOrchestrator(engine)
    origin = T - timedelta(minutes=3)
    endpoint = clock.endpoint(origin)
    intents = tuple(
        SignalIntent(
            t,
            t,
            "EQUAL",
            origin,
            known,
            T,
            origin + timedelta(minutes=10),
            endpoint,
            endpoint + timedelta(minutes=2),
            1 if i % 2 else -1,
            D(1),
            "FABRICATED",
            "FABRICATED",
            "FABRICATED",
            "FABRICATED",
            "FABRICATED",
        )
        for i, t in enumerate(SYMBOLS)
    )
    volume = {t: (D(100000), known) for t in SYMBOLS}
    borrow = BorrowEvidence(
        BorrowState.CONDITIONAL_SCENARIO, known, "FABRICATED", D(".02"), "SYNTHETIC_FIXTURE"
    )
    assert len(manager.new_vintage(intents, known, volume, borrow)) == 20
    assert engine.book.capacity(known).gross <= D(".2") * engine.book.nav()
    orders = tuple(engine.pending.values())
    engine.process(
        tuple(
            ReplayEvent(
                T + timedelta(minutes=2),
                1,
                "fill:" + o.ticker,
                "BAR",
                o,
                FinalBar(
                    T,
                    T + timedelta(minutes=1),
                    T + timedelta(minutes=2),
                    D(100),
                    "FABRICATED",
                    "ORIGINAL_OBSERVED",
                ),
            )
            for o in orders
        )
    )
    assert engine.book.capacity(T + timedelta(minutes=2)).status == "READY"
    targets = {lot.cohort.cohort_id: lot.quantity for lot in engine.book.lots}
    mark_at = endpoint + timedelta(minutes=1)
    ready = endpoint + timedelta(minutes=2)
    engine.process(
        tuple(
            ReplayEvent(
                ready,
                0,
                "exit_mark:" + t,
                "MARK",
                reference=Price(mark_at, ready, D(100), "FABRICATED"),
                ticker=t,
            )
            for t in SYMBOLS
        )
    )
    assert {lot.cohort.cohort_id: lot.quantity for lot in engine.book.lots} == targets
    exits = manager.due_exits(ready, {t: (D(100000), ready) for t in SYMBOLS})
    assert len(exits) == 20
    minute = clock.next_observation(ready)
    engine.process(
        tuple(
            ReplayEvent(
                minute + timedelta(minutes=2),
                1,
                "close:" + o.ticker,
                "BAR",
                o,
                FinalBar(
                    minute,
                    minute + timedelta(minutes=1),
                    minute + timedelta(minutes=2),
                    D(100),
                    "FABRICATED",
                    "ORIGINAL_OBSERVED",
                ),
            )
            for o in tuple(engine.pending.values())
        )
    )
    assert all(p.quantity == 0 for p in engine.book.positions)
    assert all(lot.closed for lot in engine.book.lots)
    engine.book.reconcile()


def test_actual_input_only_full_coverage_and_original_h4_witness():
    report = json.loads((ROOT / "audits/FINAL_COVERAGE_AND_INTEGRITY.json").read_text())
    assert report["status"] == "PASS" and report["unique_opportunities"] == 140280
    assert report["totals"]["forecasts"] == 131111 and report["source_partitions"] == 227
    assert len(report["fold_ticker_coverage"]) == 80 and len(report["H4_shared_keys"]) == 16
    assert report["protected_changed"] == report["source_changed"] == []
    assert report["historical_financial_outputs"] is False


def test_actual_intent_expiry_ten_and_wrong_recipe_rejected():
    data = pd.read_parquet(ROOT / "audits/signals_release/F24/2024-01-08.parquet")
    row = data.loc[(data.ticker == "AAPL") & data.input_eligible].iloc[0]
    clock = MarketClock("2024-01-01", "2025-01-10")
    intent = from_full_signal(row, "S2C_RISK", clock)
    assert intent.entry_deadline - intent.origin == timedelta(minutes=10)
    twin = row.copy()
    twin["recipe_hash"] = "PHASE2_FORBIDDEN"
    with pytest.raises(ValueError, match="BUNDLE_MISMATCH"):
        from_full_signal(twin, "S2C_RISK", clock)
    assert replace(intent, arm="ROLLING_RISK").direction == intent.direction
