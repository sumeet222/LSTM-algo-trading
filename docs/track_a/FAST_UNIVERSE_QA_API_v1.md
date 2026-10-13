# FAST 49-name provisional source QA API v1

`lstm_data.fast_screen` is an isolated diagnostic entry point for
TA-FAST-UNIVERSE-SELECT4-DOWNLOAD-QA-001. The original production universe, source
pointer and scientific gates are unchanged. Setup is the existing README route;
no dependency or editor setting changed.

From the repository root, choose a new report directory:

```sh
.venv/bin/python -B -m lstm_data.fast_screen --phase prepare --report reports/data_audit/NEW_FAST49
.venv/bin/python -B -m lstm_data.fast_screen --phase acquire --report reports/data_audit/NEW_FAST49 --plan reports/data_audit/NEW_FAST49/screen_request_plan.json --output reports/data_audit/NEW_FAST49/screen_acquisition.json
.venv/bin/python -B -m lstm_data.fast_screen --phase screen --report reports/data_audit/NEW_FAST49
.venv/bin/python -B -m lstm_data.fast_screen --phase full-plan --report reports/data_audit/NEW_FAST49
.venv/bin/python -B -m lstm_data.fast_screen --phase acquire --report reports/data_audit/NEW_FAST49 --plan reports/data_audit/NEW_FAST49/full_request_plan.json --output reports/data_audit/NEW_FAST49/full_acquisition.json
.venv/bin/python -B -m lstm_data.fast_inventory --report reports/data_audit/NEW_FAST49
```

Live commands require applicable authorization. `.env` is loaded explicitly with
`override=False` only for an absent completed chunk. The sole endpoint is Alpaca
historical stock bars; no account/trading calls. Pool, policy, request plan and
selected-four hashes are checked before sending. One source namespace stores
shared partitions. Transport reuses the reviewed SIP client, pacing and durable
append-before-send lifetime attempts, with a separate FAST journal conservatively
charging the six interrupted greedy-task attempts against the same 1,000 ceiling.
A HOLD stops further sends. It is never cleared by a new directory or plan.

`select_four(rows)` compares only formation liquidity and fixed five-date source
quality. It first picks the best eligible member of each provisional sector, then
enumerates four-sector combinations and minimizes worst-first quality tuples.
Full-history QA cannot replace/re-rank the frozen four. Sector/member/PIT action
facts remain unverified unless independent evidence exists.

`fast_inventory.saved_session_audit` uses one actual XNYS schedule instead of
rebuilding calendars per day; its output is tested against `broad_screen.audit_day`
on an early-close/DST fixture. Source schemas/hashes are verified before auditing.
`expand_missing` preserves each native key, UTC/ET offsets, maximal within-session
run and terminal flag. No feature formulas, labels, empirical transforms or fills
are implemented. T2 is an explicitly optimistic source-only bound using the
existing predicate and 1,502-origin denominator, never measured full FT0 retention.

If bulk fails before publication, the inventory discovers only completed immutable
pairs and exact matching archived day samples. Missing partitions become
`source_nonresponse.csv` records, not fabricated absent candles. Full-interval
percentages stay NOT_MEASURED; a partial per-candle CSV is labeled PARTIAL.
Completed source pairs can be checksum-reused with zero GETs even on a HOLD journal;
this does not authorize resuming an incomplete request.

The current result in `reports/data_audit/ta_fast49_2026-10-13_024752` selected
AAPL/COST/CMCSA/SBUX/HON provisionally. The first three shared prehistory months
completed; March 2020 still had continuation after four pages. The bounded client
stopped without publishing partial data. Further acquisition needs a separately
reviewed capacity/resumption plan, with all prior attempts/page histories conserved.
No claim of a complete five-stock archive or scientific readiness is made.

Focused tests need no live credentials:

```sh
.venv/bin/python -B -m pytest -q tests/test_fast_screen.py tests/test_greedy_screen.py tests/test_broad_screen.py tests/test_remediation_transport.py
```

The halted rank-led module and source evidence are preserved as interrupted work;
the FAST pool excludes AMZN and does not continue that algorithm. All source
stores remain ignored; small plans, hashes, reports and APIs support reproduction.
Do not stage source files, `.env` or unrelated work. No Git integration is authorized.
