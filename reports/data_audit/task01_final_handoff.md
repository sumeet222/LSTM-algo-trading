# Task 01 final intake handoff

This is the current status. It supersedes the earlier missing-credential, native-hour,
pending-resolution and pending-bulk statements in the preserved initial reports.

Implemented and executed data intake only: original course audit, live SIP pilots,
approved five-stock acquisition, stock QA and causal alignment diagnostics. No labels,
features, models, trading, split definitions or architecture experiments were added.

## Actual source coverage

All five stocks cover the intended July 1, 2020–June 30, 2025 local session dates.
Provider extended-session bars are preserved; the table's missing counts refer only
to the historical XNYS regular-session half-hour grid.

| Source | Source rows | Missing RTH half hours | Issue |
|---|---:|---:|---|
| USA500 original CSV | 29,510 | Not comparable to equity grid | Upstream semantics/volume/calendar unknown; last timestamp is July 1, 2025 00:00 New York. Provisional timestamp-as-close approved. |
| AAPL SIP | 39,528 | 0 | No RTH gaps detected. |
| JPM SIP | 32,898 | 36 | Gaps in returned history; independently checked one affected day. |
| JNJ SIP | 27,982 | 37 | One session with no RTH observations, plus partial gaps. |
| WMT SIP | 31,934 | 48 | Partial-session gaps. |
| CAT SIP | 26,666 | 47 | One session with no RTH observations, plus partial gaps. |

Stock total: **159,008 bars**, 60 monthly multi-symbol Parquet chunks,
**5,845,266 bytes** Parquet plus **581,833 bytes** manifests. Small native-hour and
30Min pilot evidence totals 151,317 bytes of ignored Parquet. No second full adjusted,
raw, hourly, per-experiment or feature store exists.

Original course SHA-256:
`ba78d6bf933f0aca4dfcdedb69454d19aa29bfed84481b6ba1bcccdaf7b1634a`.
Its 2,083,715 bytes are unchanged. The full course UTC bounds are
2020-07-01 04:00 through 2025-07-01 04:00. Overnight and Sunday rows are preserved.

## Approved conventions and measured gates

The researcher explicitly approved:

1. USA500 timestamp-as-close **for now**, with provider semantics still unverified.
2. `30Min` SIP source and session-anchored hourly aggregation with flagged closing stubs.
3. Full five-stock acquisition with retrospective split price/volume adjustment.

Native `1Hour` failed the required grid: all 370 sampled starts were at local `:00`,
including DST and early-close examples. The approved 30Min pilot fetched 738 source
bars with seven HTTP 200 responses, produced 165 complete session windows including
24 stubs, and had zero missing regular-session constituents. The gate passed.

The dated [approval](../../configs/track_a_bulk_approval_2026-10-10.json) binds the
config to the passing pilot's hash and records full acquisition/split authorization.
Reuse it for resumption; no new permission is needed for the same approved choices.

Canonical source schema: symbol, offset-aware UTC interval start, OHLCV float64,
optional trade_count/VWAP, explicit SIP/split/source_timeframe and provenance ID.
`aggregate_session_hours` produces hourly panels in memory, with real `available_at`,
duration, constituent count and stub flag. Source VWAP remains preserved; aggregate
VWAP is intentionally omitted because Alpaca's VWAP volume basis can differ from
source bar volume. Actual historical publication latency remains unknown.

## QA results and preserved gaps

All 6,275 symbol-session grids were audited. No null required fields, duplicate keys,
unordered timestamps, nonfinite/nonpositive prices, invalid OHLC or negative/zero
stock volumes were found. All source intervals are compatible half-hour boundaries.
No split-window daily price-jump candidate exceeded the diagnostic 20% threshold;
this does not replace an authoritative corporate-action reference dataset.

There are **168 missing RTH half-hour observations across 15 symbol-session pairs**:

| Month | Missing bars |
|---|---:|
| 2021-04 | 48 |
| 2021-10 | 48 |
| 2022-01 | 22 |
| 2022-03 | 50 |

The [compact QA JSON](task01_stock_qa_compact/stock_qa.json) lists every affected
session, missing timestamps, symbol ranges, early closes and representative DST grids.
The first bulk attempt stopped at April 2021 because the implementation mistakenly
required every source bar for storing a chunk. This was corrected to preserve actual
observations plus missing masks, as the task requires; invalid/off-grid data still fail.
The resume reused nine verified chunks and fetched the remaining 51. No old file was
overwritten, gap filled, stock replaced or later eligibility rule chosen.

A [single-symbol JPM probe](task01_gap_probe_jpm_20210419.json) for April 19, 2021
returned only the 09:30 local bar, matching the multi-symbol store's gap. This is
evidence of incomplete returned provider history rather than an omitted pagination
page. It is not evidence that the actual market had no trades. Other gap causes
remain unresolved. Do not substitute IEX, silently backfill, or use future labels
to decide eligibility around these gaps.

The source store has 81,137 fully-contained RTH half-hour bars. On-demand aggregation
emits **43,692** complete hourly/stub windows; **98** incomplete windows are omitted
with diagnostic masks. Stub observations must not be counted as complete hours when
a later task defines four-trading-hour timing.

## Alignment evidence

The [full alignment report](task01_full_alignment/alignment.md) uses backward-only
as-of comparisons. With the user-approved close assumption and a 90-minute diagnostic
stale bound, all 43,692 observed hourly/stub windows have an available candidate index
row and zero stale/unmatched cases. The +60-minute index-delay sensitivity also has
zero stale/unmatched hourly cases. This measures candidate matching, not verified
provider latency or permission to finalize a feature join.

Across all 159,008 native source bars, including extended hours, there are 2,434 stale
index matches under timestamp-as-close and 1,123 under +60-minute sensitivity; no
unmatched rows. No stale/overnight price was filled. Both scenarios are audit-only.

## Reproduce or resume

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
ruff check src tests
lstm-data source-audit
lstm-data download --dry-run
lstm-data --env-file .env sip-pilot
lstm-data --env-file .env download --approval configs/track_a_bulk_approval_2026-10-10.json
lstm-data stock-qa
lstm-data alignment --max-age-minutes 90
```

Supply the exact researcher-owned course file and local credential variables; omit
`--env-file` if credentials are exported. The same canonical chunks resume without
network requests after hash/schema/parameter verification. New report directories
prevent overwriting old runs. The full-store resume smoke verified all 60 chunks with
**zero HTTP calls**. Another machine must retrieve/supply source data; ignored local
data are not implicitly available after cloning.

Final validation: **60 offline tests passed**, Ruff and compile checks passed,
source CLI audit passed, live pilots/collection/QA/alignment completed. PyArrow emitted
harmless sandbox CPU-cache probing warnings during local reads; operations succeeded.
There are no known failing final tests. Initial unsuccessful attempts remain reported.

## Git and next task

Branch `feat/track-a-data-intake`; HEAD remains
`d335de9528092852b3049687f53fbfaf007812d1`. Implementation, approval and small reports
are uncommitted; nothing was pushed. `.env`, raw data, pilot samples and the earlier
3.85 MB exhaustive healthy-grid report remain ignored. Compact QA is 57,731 bytes
and retains all issue rows. The [final session report](../codex_sessions/2026-10-10_053128_feat-track-a-data-intake_task01-complete.md)
contains exact files/interfaces/commands and historical failure corrections.

Next research task: resolve treatment of the 15 affected symbol-session combinations,
obtain/verify source/provider and corporate-action metadata, and agree the trade clock,
execution latency, stub treatment and final causal join before implementing labels
or models. Universe/targets/splits/costs/model definitions remain unchanged.
