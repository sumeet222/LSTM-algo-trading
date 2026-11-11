"""Bounded actual raw/action fixtures and dimensionless shadow; NO financial books."""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from ...stage012.historical_source_store import file_hash
from ...stage012.model_registry import SYMBOLS
from ..common import RAW, D
from .cache import ROOT, publish
from .tapes import RawObservation


def audit() -> None:
    path = ROOT / "RAW_ACTION_SHADOW_SOURCE_PLAN_V2.json"
    seal = json.loads(path.with_suffix(".seal.json").read_text())
    if file_hash(path) != seal["sha256"]:
        raise ValueError("SOURCE_PLAN_IDENTITY")
    plan = json.loads(path.read_text())
    frames = []
    reads = []
    keys = pd.to_datetime([r["time"] for r in plan["keys"]], utc=True)
    for item in plan["sources"]:
        p = Path(item["path"])
        if (
            p.is_absolute()
            or ".." in p.parts
            or p.stem > "2024-12"
            or file_hash(p) != item["sha256"]
        ):
            raise ValueError("SOURCE_SCOPE_OR_HASH")
        rows = pd.read_parquet(
            p,
            columns=plan["columns"],
            filters=[
                ("timestamp", "in", keys),
                ("ticker", "in", ["AAPL", "COP"]),
                ("is_rth", "==", True),
            ],
        )
        allowed = {(r["ticker"], pd.Timestamp(r["time"])) for r in plan["keys"]}
        rows = rows.loc[
            [
                (t, at) in allowed
                for t, at in rows[["ticker", "timestamp"]].itertuples(index=False, name=None)
            ]
        ]
        frames.append(rows)
        reads.append(
            {
                "path": str(p),
                "sha256": item["sha256"],
                "mtime_ns": p.stat().st_mtime_ns,
                "rows": len(rows),
            }
        )
    frame = pd.concat(frames).sort_values(["timestamp", "ticker"])
    checked = []
    for ticker, at, op, high, low, close, volume in frame[
        ["ticker", "timestamp", "open", "high", "low", "close", "volume"]
    ].itertuples(index=False, name=None):
        t = datetime.fromisoformat(at.isoformat())
        obs = RawObservation(
            ticker,
            t,
            t + timedelta(minutes=1),
            t + timedelta(minutes=2),
            D(str(op)),
            D(str(high)),
            D(str(low)),
            D(str(close)),
            D(str(volume)),
            RAW,
            next(r["sha256"] for r in reads if Path(r["path"]).stem == at.strftime("%Y-%m")),
            "ORIGINAL_OBSERVED",
        )
        obs.validate()
        checked.append(
            {
                "ticker": ticker,
                "at": at.isoformat(),
                "raw_ohlcv": "VALID",
                "available_at": obs.available.isoformat(),
                "source_hash": obs.source_hash,
            }
        )
    facts_path = Path(plan["action_metadata"])
    facts = json.loads(facts_path.read_text())["events"]
    facts = [r for r in facts if r["date"] <= "2024-12-31"]
    splits = [r for r in facts if r["kind"] == "SPLIT"]
    action_tape = {
        "status": "INCOMPLETE_MATERIAL_DIVIDEND_AND_SPECIAL_ACTION_COVERAGE",
        "fact_source": str(facts_path),
        "fact_sha256": file_hash(facts_path),
        "verified_split_events": splits,
        "other_pre2025_facts": [r for r in facts if r["kind"] != "SPLIT"],
        "per_ticker": [
            {
                "ticker": t,
                "dividend_completeness": "NOT_ESTABLISHED",
                "pay_date_coverage": "NOT_ESTABLISHED",
                "strict_PIT": "NOT_ESTABLISHED",
            }
            for t in SYMBOLS
        ],
        "apple_2024_dividend_partial": {
            "amount_usd": ".25",
            "record_date": "2024-05-13",
            "pay_date": "2024-05-16",
            "ex_date": None,
            "source_url": "https://www.apple.com/newsroom/2024/05/apple-reports-second-quarter-results/",
            "download_sha256": file_hash(ROOT / "audits/apple_2024_05_02.html"),
            "status": "EX_DATE_NOT_STATED_DO_NOT_INFER",
        },
        "yahoo_dividend_probe": {
            "http_status": 429,
            "body_sha256": file_hash(ROOT / "audits/yahoo_dividend_probe.body"),
            "status": "RATE_LIMITED_NOT_USED",
        },
        "borrow_source": "CONDITIONAL_USER_POLICY_NOT_OBSERVED_LOCATE",
        "financial_release": "HOLD",
    }
    publish(ROOT / "HISTORICAL_ACTION_AND_CARRY_TAPE_MANIFEST.json", action_tape)
    raw = frame.loc[(frame.ticker == "AAPL") & (frame.timestamp.dt.year == 2020)]
    split_witness = {
        "action": "AAPL 4-for-1 split 2020-08-31",
        "source_fact": [r for r in splits if r["ticker"] == "AAPL" and r["date"] == "2020-08-31"][
            0
        ],
        "raw_before": float(raw.iloc[0].close),
        "raw_after": float(raw.iloc[1].open),
        "before_divided_by_declared_factor": float(raw.iloc[0].close) / 4,
        "price_units": "canonical source raw shares;not total return adjusted",
        "interpretation": "source-level split boundary only,no trade/return/economic holdings",
    }
    publish(
        ROOT / "audits/RAW_ACTION_SOURCE_FIXTURES.json",
        {
            "plan_sha256": seal["sha256"],
            "reads": reads,
            "rows": checked,
            "split": split_witness,
            "quarantine_source_hash": file_hash(Path(plan["quarantine_metadata"])),
            "financial_booking": False,
        },
    )


def shadow() -> None:
    """Same source keys into signal/control/allocator/executor boundary; never mint an order."""
    path = ROOT / "audits/signals/F24/2024-01-08.parquet"
    signals = pd.read_parquet(path)
    chosen = signals.loc[
        (signals.origin == pd.Timestamp("2024-01-08T15:30:00Z"))
        & signals.ticker.isin(["AAPL", "COP"])
    ]
    weights = []
    for arm in ("EQUAL", "S2C_RISK", "ROLLING_RISK", "EWMA_RISK"):
        valid = chosen.loc[chosen["g_" + arm].notna()]
        denom = valid["g_" + arm].sum()
        for _, row in valid.iterrows():
            weights.append(
                {
                    "ticker": row["ticker"],
                    "arm": arm,
                    "direction": int(row["direction"]),
                    "shadow_nav_fraction": min(0.1, 0.2 * row["g_" + arm] / denom),
                    "magnitude_c3": row["magnitude_c3"],
                    "control_latest_available": row["control_latest_available"],
                    "issued_at": str(row["issued_at"]),
                    "first_entry_marker": str(row["earliest_entry_marker"]),
                }
            )
    publish(
        ROOT / "audits/HISTORICAL_SOURCE_SHADOW_BOUNDARY.json",
        {
            "mode": "REAL_SOURCE_SIGNAL_AND_DIMENSIONLESS_SHADOW_ONLY",
            "signal_partition_sha256": file_hash(path),
            "source_fixture": "RAW_ACTION_SOURCE_FIXTURES.json",
            "candidate_weights": weights,
            "capital_instantiated": False,
            "orders": 0,
            "fills": 0,
            "positions": 0,
            "cash_postings": 0,
            "simulator_boundary": "REFUSED_FINANCIAL_RELEASE_NO_LEDGER_INSTANTIATED",
            "action_feed": "HISTORICAL_ACTION_AND_CARRY_TAPE_MANIFEST.json;incomplete=>HOLD",
            "convention": (
                "prior 15:31 minute completes15:32/received15:33,not available15:32 decision;"
                "pretrade volume must come from earlier received minute"
            ),
        },
    )


if __name__ == "__main__":
    audit()
    shadow()


def shadow_release() -> None:
    """Source-backed intent+unit-fraction allocation+financial refusal, never a book."""
    from ...stage012.calendar_schedule import MarketClock
    from ..portfolio_allocator import Capacity, allocate
    from .engine import historical_financial_entry
    from .intents import from_full_signal

    source = ROOT / "audits/signals_release/F24/2024-01-08.parquet"
    frame = pd.read_parquet(source)
    frame = frame.loc[
        (frame.origin == pd.Timestamp("2024-01-08T15:30:00Z")) & frame.ticker.isin(["AAPL", "COP"])
    ]
    clock = MarketClock("2024-01-01", "2025-01-10")
    records = []
    for arm in ("EQUAL", "S2C_RISK", "ROLLING_RISK", "EWMA_RISK"):
        candidates = tuple(
            from_full_signal(row, arm, clock)
            for _, row in frame.iterrows()
            if pd.notna(row["g_" + arm])
        )
        # Unit-price/normalized-capacity arithmetic yields fractions, not actual shares,
        # market capital, a funded account, or executable orders.
        result = allocate(
            candidates,
            Capacity(D(1), D(0), D(0), D(1), ()),
            {c.ticker: D(1) for c in candidates},
            lot=D(".000000000001"),
        )
        records.extend(
            {
                "ticker": item.ticker,
                "arm": arm,
                "absolute_capacity_fraction": str(item.notional),
                "reason": item.reason,
                "basis": "DIMENSIONLESS_NO_MARKET_EXECUTION_PRICE",
            }
            for item in result
        )
    gate_path = ROOT / "BACKTEST_READINESS_GATE_V2.json"
    gate = json.loads(gate_path.read_text())
    output = ROOT / "audits/PROHIBITED_FINANCIAL_OUTPUT.json"

    def blocked_loader(_):
        raise AssertionError("GATE_MUST_REFUSE_BEFORE_FINANCIAL_SOURCE_LOADER")

    try:
        historical_financial_entry(
            gate_path,
            gate["binding"],
            ROOT / "EXTERNAL_REVIEWER_KEY_NOT_REGISTERED",
            ROOT / "NO_EXTERNAL_SIGNATURE",
            output,
            blocked_loader,
        )
    except PermissionError as exc:
        refusal = str(exc)
    else:
        raise AssertionError("HISTORICAL_FINANCIAL_ENTRY_MUST_REFUSE")
    if output.exists():
        raise AssertionError("FORBIDDEN_FINANCIAL_OUTPUT_CREATED")
    publish(
        ROOT / "audits/HISTORICAL_SOURCE_SHADOW_BOUNDARY_FINAL.json",
        {
            "source": "ACTUAL_HISTORICAL_INPUT_AND_RAW_ACTION_FIXTURE",
            "source_partition_sha256": file_hash(source),
            "source_fixture": "RAW_ACTION_SOURCE_FIXTURES.json",
            "action_manifest_sha256": file_hash(
                ROOT / "HISTORICAL_ACTION_AND_CARRY_TAPE_MANIFEST.json"
            ),
            "allocations": records,
            "financial_gate_refusal": refusal,
            "orders": 0,
            "fills": 0,
            "positions": 0,
            "cash_postings": 0,
            "historical_NAV_or_PnL_computed": False,
            "funded_account_created": False,
            "financial_output_exists": False,
            "limitation": (
                "pure unit-fraction allocation only;"
                "cost/funding limits tested on separate fabricated economics"
            ),
        },
    )
