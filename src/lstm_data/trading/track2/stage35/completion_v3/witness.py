"""Actual source + synthetic endowments, isolated NO-performance consistency.

Never uses a historical trade/fill/position strategy or a funded economic book.
Full V2 financial guard remains closed; raw observations are validated, not valued.
"""

import json
from dataclasses import asdict
from datetime import date
from decimal import Decimal
from pathlib import Path

import pandas as pd

from ...stage012.calendar_schedule import MarketClock
from ..completion_v2.engine import historical_financial_entry
from ..completion_v2.intents import from_full_signal
from ..portfolio_allocator import Capacity, allocate
from .acquire import ROOT, write_once
from .event_ledger import ClaimShareBook, ShareLot, verify_journal
from .inventory import digest
from .tapes import compile_events, load_actions, midnight

D = Decimal


def run(root: Path = ROOT) -> dict:
    fixtures = json.loads((root / "audits/RAW_SOURCE_FIXTURES_V3.json").read_text())
    if fixtures["missing"] or fixtures["projected_rows"] != 11:
        raise ValueError("SOURCE_FIXTURE_COVERAGE")
    actions = load_actions(root)
    aapl = next(
        e
        for e in actions
        if e.symbol == "AAPL"
        and e.action_type == "CASH_DIVIDEND"
        and e.ex_date == date(2024, 5, 10)
    )
    split = next(e for e in actions if e.symbol == "TSLA" and e.action_type == "SPLIT")
    special = next(e for e in actions if e.symbol == "MRK" and e.action_type == "SPINOFF")
    books = []
    for action in (aapl, split, special):
        b = ClaimShareBook(
            (
                ShareLot("endowed_long", action.symbol, D(10)),
                ShareLot("endowed_short", action.symbol, D(-6)),
            )
        )
        start = action.ex_date or action.effective_date
        if start is None:
            raise ValueError("ACTION_EFFECTIVE_UNKNOWN")
        tape = compile_events(
            (action,),
            start,
            action.payable_date
            if action.action_type == "CASH_DIVIDEND" and action.payable_date
            else start,
        )
        # Special legal distribution precedes ex-trading date: terms remain an
        # unpriced pending asset, not a fictional pre-ex cash payment.
        if action.action_type == "SPINOFF":
            tape = compile_events((action,), start, start)
        for event in tape:
            if event.kind == "CASH_SETTLEMENT":
                b = b.pay(
                    action.event_id, event.effective_at, event.available_at, event.available_at
                )
            else:
                b = b.apply(
                    action,
                    event.effective_at,
                    event.available_at,
                    event.available_at,
                    modeled_retrospective=True,
                    due_at=midnight(action.payable_date) if action.payable_date else None,
                )
        verify_journal(b)
        books.append(
            {
                "source_action": action.record(),
                "mode": "SYNTHETIC_ENDOWED_SHARES_NO_TRADES",
                "shares": [asdict(lot) for lot in b.lots],
                "physical_share_sum": str(b.physical_shares(action.symbol)),
                "claim_cash_only": str(b.cash_distribution_only),
                "claims": [asdict(claim) for claim in b.claims],
                "settled_claims": [asdict(claim) for claim in b.settled],
                "unresolved": b.unresolved,
                "journal": [asdict(j) for j in b.journal],
            }
        )
    signal_plan = json.loads((root / "SHADOW_SIGNAL_PLAN_V3.json").read_text())
    signal = Path(signal_plan["source"])
    if digest(signal) != signal_plan["sha256"]:
        raise ValueError("FROZEN_SIGNAL_PARTITION_CHANGED")
    frame = pd.read_parquet(signal)
    chosen = frame.loc[
        (frame.origin == pd.Timestamp(signal_plan["origin"]))
        & frame.ticker.isin(signal_plan["tickers"])
    ]
    clock = MarketClock("2024-01-01", "2025-01-10")
    allocations = []
    for arm in ("EQUAL", "ROLLING_RISK", "EWMA_RISK", "S2C_RISK"):
        candidates = tuple(
            from_full_signal(row, arm, clock)
            for _, row in chosen.iterrows()
            if pd.notna(row["g_" + arm])
        )
        result = allocate(
            candidates,
            Capacity(D(1), D(0), D(0), D(1), ()),
            {c.ticker: D(1) for c in candidates},
            lot=D(".000000000001"),
        )
        allocations.extend(
            {
                "ticker": item.ticker,
                "arm": arm,
                "dimensionless_fraction": str(item.notional),
                "reason": item.reason,
            }
            for item in result
        )
    old_gate = Path("trading/track2/stage35/completion_v2/BACKTEST_READINESS_GATE_V2.json")
    gate = json.loads(old_gate.read_text())
    forbidden = root / "audits/FORBIDDEN_HISTORICAL_FINANCIAL_OUTPUT.json"

    def loader(_):
        raise AssertionError("FINANCIAL_SOURCE_LOADER_MUST_NOT_RUN")

    try:
        historical_financial_entry(
            old_gate,
            gate["binding"],
            root / "NO_REVIEW_KEY",
            root / "NO_REVIEW_SIGNATURE",
            forbidden,
            loader,
        )
    except PermissionError as exc:
        refusal = str(exc)
    else:
        raise AssertionError("FINANCIAL_RELEASE_NOT_APPROVED")
    if forbidden.exists():
        raise AssertionError("FINANCIAL_OUTPUT_CREATED")
    report = {
        "mode": "ISOLATED_NONPERFORMANCE_CLAIM_SHARE_CONSISTENCY",
        "raw_kind": "ACTUAL_HISTORICAL_NEVER_RELABELLED_SYNTHETIC",
        "quantity_origin": "synthetic endowments;no original strategy quantity or historical fill",
        "source_partitions": len(fixtures["reads"]),
        "source_rows": fixtures["projected_rows"],
        "action_inventory_sha256": digest(root / "ACTION_PROVENANCE_V3.jsonl"),
        "books": books,
        "original_signal_rows_reused": len(chosen),
        "signal_partition_sha256": digest(signal),
        "dimensionless_allocations": allocations,
        "prior_financial_gate_refusal": refusal,
        "historical_orders": 0,
        "historical_fills": 0,
        "funded_account_created": False,
        "historical_NAV_or_PnL_or_return_computed": False,
        "post2024_price_reads": 0,
        "model_forward_calls": 0,
        "unpriced_special": "MRK OGN +1/-.6 illustrative asset claims;value/CIL unresolved",
    }
    write_once(root / "audits/HISTORICAL_CLAIM_SHARE_WITNESS_V3.json", report)
    return report


if __name__ == "__main__":
    run()
