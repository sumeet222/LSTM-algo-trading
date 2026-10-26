"""Source-backed opening-reference audit; latency remains a disclosed research proxy."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .hf1m_action_audit import SYMBOLS, digest
from .hf20_ranking_continue_report import markdown


def audit(
    clock: pd.DataFrame,
    grid: pd.DataFrame,
    prices: pd.DataFrame,
    entry: np.ndarray,
    exit_: np.ndarray,
    returns: np.ndarray,
    out: Path,
) -> None:
    opening = clock.conditional_open.to_numpy()
    rows = clock.loc[opening]
    start = pd.DatetimeIndex(rows.entry_end_utc)
    candle = prices.set_index(["timestamp", "ticker"]).reindex(
        pd.MultiIndex.from_product([start, SYMBOLS], names=["timestamp", "ticker"])
    )
    minute_open = candle.open.to_numpy().reshape(-1, 20)
    minute_close = candle.close.to_numpy().reshape(-1, 20)
    np.testing.assert_array_equal(minute_open, entry[opening])
    present = (
        np.isfinite(minute_open)
        & np.isfinite(minute_close)
        & (minute_open > 0)
        & (minute_close > 0)
    )
    records = []
    for year in sorted(set(rows.session_date_et.str[:4])):
        m = rows.session_date_et.str.startswith(year).to_numpy()
        for j, symbol in enumerate(SYMBOLS):
            records.append(
                dict(
                    year=year,
                    ticker=symbol,
                    candidate_sessions=int(m.sum()),
                    genuine_0930_start_minute=int(present[m, j].sum()),
                    missing_or_quarantined_minute=int((~present[m, j]).sum()),
                    genuine_final_endpoint=int(np.isfinite(exit_[opening][m, j]).sum()),
                    joint_complete20_admitted=int(rows.loc[m, "eligible"].sum()),
                    publication_latency="UNVERIFIED_NOT_A_MISSING_PRICE",
                )
            )
    coverage = pd.DataFrame(records)
    coverage.to_csv(out / "S4_0930_ALL20_SOURCE_COVERAGE.csv", index=False)
    samples = []
    chosen = rows.loc[rows.session_date_et.eq("2024-06-18")].iloc[0]
    k = int(chosen.row_index)
    for j, symbol in enumerate(SYMBOLS):
        minute = candle.loc[[(pd.Timestamp(chosen.entry_end_utc), symbol)]].iloc[0]
        samples.append(
            dict(
                ticker=symbol,
                source_minute_start=str(chosen.entry_end_utc),
                source_minute_end=str(chosen.entry_end_utc + pd.Timedelta(minutes=1)),
                price_field="OPEN",
                reference_price=float(entry[k, j]),
                minute_close_unused_as_entry=float(minute.close),
                assumed_issue=str(chosen.issuance_utc),
                last_full_hour_input_end=str(grid.hour_end_utc.iloc[int(chosen.entry_index)]),
                exact_target_end=str(chosen.exit_end_utc),
                genuine_exit_price=float(exit_[k, j]),
                direct_price_only_return=float(returns[k, j]),
                provenance=(
                    "canonical_observed/2024-06.parquet; exact ticker+UTC minute key; "
                    "P019B factors/quarantines"
                ),
            )
        )
    pd.DataFrame(samples).to_csv(out / "S4_0930_ALL20_EXACT_SOURCE_WITNESSES.csv", index=False)
    has = rows.entry_index.ge(0)
    last = pd.DatetimeIndex(grid.hour_end_utc.iloc[rows.loc[has, "entry_index"].to_numpy(int)])
    origins = pd.DatetimeIndex(rows.loc[has, "entry_end_utc"])
    if (
        not (last < origins).all()
        or not (rows.loc[has, "entry_index"] - rows.loc[has, "first_step"]).eq(47).all()
    ):
        raise ValueError("OPENING_INPUT_USES_UNFINISHED_CURRENT_HOUR")
    normal = rows.regular_session
    ends = rows.loc[normal, "exit_end_utc"].dt.tz_convert("America/New_York")
    if not ends.dt.strftime("%H:%M").eq("13:30").all():
        raise ValueError("OPENING_ENDPOINT_SHIFTED")
    docpaths = [
        Path("reports/data_audit/ta018_hf20_1m_2026-10-22_134833/dataset_card_snapshot.md"),
        Path(
            "reports/data_audit/ta019b_action_qa_2026-10-22_201224/P019B_QUARANTINE_POLICY_AND_COVERAGE.md"
        ),
        Path(
            "reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122/P020_TARGET_TG20_AND_CLOCK_AUDIT.md"
        ),
    ]
    source_docs = [dict(path=str(p), sha256=digest(p)) for p in docpaths]
    result = dict(
        status="INCLUDE_0930_UNDER_DISCLOSED_TIMING_PROXY",
        daily_origins_on_regular_session=7,
        starts_before_audit=0,
        ledger=106,
        all20_stock_coverage=True,
        opening_price_panels=int(rows.opening_reference_complete20.sum()),
        eligible_opening_origins=int(rows.eligible.sum()),
        minute_timestamp="START:09:30 represents09:30–09:31",
        target_entry="Genuine09:30 minute OPEN; not09:31 close, not certified auction",
        target_exit="Genuine13:29 minute CLOSE at13:30 on normal sessions",
        publication_latency_verified=False,
        missing_data_distinguished=True,
        issuance="09:32 assumed under existing origin+2 price-only proxy",
        features="48 previously completed full-hour steps; no current09:30–10:30 data",
        early_close="Exact240trading-minute calendar; may cross into following session",
        source_documents=source_docs,
        previous_six_origin_draft_preserved=True,
        new_training=False,
    )
    (out / "S4_0930_REAUDIT_DECISION.json").write_text(json.dumps(result, indent=2) + "\n")
    summary = coverage.groupby("ticker", as_index=False).agg(
        candidate_sessions=("candidate_sessions", "sum"),
        genuine_first_minutes=("genuine_0930_start_minute", "sum"),
        missing_minutes=("missing_or_quarantined_minute", "sum"),
    )
    text = (
        """# S4-A09:30 source re-audit

**Decision: include09:30 conditionally; seven daily origins on normal sessions.**
No S4 training has begun; ledger106/200.

The first audit correctly found opening prices but incorrectly treated an additional
two-minute delay after the first minute's completion as mandatory. That09:33 rule
was stricter than the existing origin+2 price-only timing proxy. The six-origin
draft, its counts and logs are preserved in the parent directory and superseded.

The pinned publisher card explicitly defines `timestamp` as the **start time of the
minute**. A09:30 row describes09:30–09:31, and its OPEN is the source-backed09:30
reference. It is a genuine vendor minute opening price, not independently verified
opening-auction data. The completed minute is available in the historical files;
its actual publication latency is unknown. Assuming it could be used at09:32 is
consistent with the accepted origin+2 research proxy, not proof of real-time delivery.
No09:31 close is substituted for the09:30 target start, and no extra publication lag
is silently added. Missing or quarantined prices still invalidate the affected panel.

All48 inputs end at previously completed full hours, normally the prior session's
15:30 endpoint (or latest full hour on an early close). The unfinished current
09:30–10:30 bar never enters FT16. All16 formulas stay defined at their actual
historical full-hour timestamps. Opening-context M2 uses prior matured09:30→13:30
signals, locked at each historical input session's open, with the unchanged20/60
scheduled-session rules. It is not refreshed with current morning outcomes.

On normal sessions the240-minute target ends exactly13:30, using the genuine
13:29–13:30 minute CLOSE. Early-close sessions follow the authoritative240-minute
clock and are labeled overnight when appropriate. Missing intermediate16:00 closes
affect only supported decomposition, not a valid direct endpoint return.

## Actual all-stock source coverage, July2010–December2024

"""
        + markdown(summary)
        + "\nComplete year/ticker counts: S4_0930_ALL20_SOURCE_COVERAGE.csv.\n"
        "Twenty fixed-date exact-price/input witnesses: S4_0930_ALL20_EXACT_SOURCE_WITNESSES.csv.\n"
        "Publication uncertainty is separate from missing-price counts. The JSON decision binds\n"
        "the exact local source documentation by path and SHA256. Raw/derived prices remain\n"
        "local/private; no protected2026 partition was opened.\n"
    )
    (out / "S4_0930_REAUDIT.md").write_text(text)
