# Package 018C boundary coverage: STOP_QUALITY

The mandatory six-month gate did not pass. All 20 requested tickers are present in the actual March 2026 source; presence does not establish usability. The first sampled month fails raw quality, so acquisition stopped before January/February, the early group, intermediate sentinels and bulk. The exact canonical universe is unchanged.

The earlier STOP_RIGHTS record remains unchanged. This continuation used HUMAN_REPORTED_PERMISSION_TO_RESUME_PRIVATE_RESEARCH from the user’s 018C instruction. This is not an independent licensing or redistribution finding.

## Actual March evidence

At the pinned revision, March contains34,379,927 provider-wide rows in33 row groups. Every ticker column was scanned; selected rows were read from16 row groups. The retained raw extract has226,433 rows (226,408 distinct ticker/timestamp keys),5,095,276 bytes. All 20 names have genuine rows in22 expected sessions,8,580 expected regular-session minutes per name. The month spans March 2–31 and includes the March 8 DST transition. Calendar-spanning data do not establish a jointly usable end. No global March truncation was found that would justify moving the end group.

Raw QA found25 conflicting ticker/timestamp keys across15 stocks (50 rows;46 regular-session rows /23 keys, plus4 extended-session TSLA rows /2 keys). They are not identical duplicates. PEP has a three-minute absent run on March 10; MRK lacks the March 19 opening minute and WFC lacks the March 31 opening minute. Four names meet this provisional month policy: VZ,SBUX,JNJ,XOM. The other16 are INSUFFICIENT. No stock was removed.

All226,433 rows have finite positive prices, valid OHLC ordering, nonnegative finite volume and minute-aligned UTC timestamps. There are387 genuinely absent expected stock-minute slots and23 additional regular-session keys with conflicting candles. No synchronous all 20 missing minute or adjacent observed regular-session close jump above25% was found in this sample. Smaller gaps remain unexplained; USABLE is a provisional screening state, not proof of no-trade minutes, adjustment consistency or full raw QA.

## Conservative policy

Each sampled stock/month requires at least98% unambiguous valid genuine RTH slots, no more than two consecutive missing/invalid regular-session minutes, genuine unambiguous opening/final minute, no malformed values or duplicates, and review of material jumps. The missing-run allowance is a screening limit, not fill authorization. Duplicate slots retain observed presence but are excluded from the unambiguous-valid mask. No deduplication, shifting, filling, clipping or corporate-action adjustment was applied. This is stricter monthly screening within the018 source criteria, not a replacement for >=98% overall/>=95% annual/full-span QA.

## Mandatory20 × 6 matrix

`boundary_20x6.csv` and `.json` contain120 ticker/month records with file identities, actual row/session/minute counts, first/last observed UTC times, malformed/duplicate counts and row groups. Unsampled counts are null, never observed zeros. The early May/June/July 2011 columns are provisional planning placeholders: Phase A failure prevented qualification of a common end and exact DateOffset(years=14,months=9) cutoff. No common start/end or15 year/14 years 9 months claim is made.

|Ticker|2011-05*|2011-06*|2011-07*|2026-01|2026-02|2026-03|
|---|---|---|---|---|---|---|
|VZ|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|USABLE|
|COP|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|INSUFFICIENT|
|BAC|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|INSUFFICIENT|
|BA|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|INSUFFICIENT|
|AAPL|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|INSUFFICIENT|
|PEP|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|INSUFFICIENT|
|MRK|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|INSUFFICIENT|
|SBUX|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|USABLE|
|CVX|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|INSUFFICIENT|
|MS|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|INSUFFICIENT|
|AMD|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|INSUFFICIENT|
|KO|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|INSUFFICIENT|
|JNJ|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|USABLE|
|AMZN|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|INSUFFICIENT|
|XOM|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|USABLE|
|WFC|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|INSUFFICIENT|
|AVGO|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|INSUFFICIENT|
|TSLA|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|INSUFFICIENT|
|MA|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|INSUFFICIENT|
|CSCO|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|NOT_SAMPLED|INSUFFICIENT|

*Early columns provisional, not released for acquisition. UNVERIFIED is their machine-readable usable state.

## Transfer, storage and next decision

Only227,345,764 HTTP response-body bytes were received:30,885 metadata plus227,314,879 Parquet ranges. No whole monthly file was downloaded. Compared with a464,192,938 byte full March file, the entire feasibility data transfer used48.97% of its size (about51.03% fewer bytes). These are measured body bytes, not a bandwidth-cap interpretation or a full15 year estimate. Locator, repeated probe and footer bytes are included. No automatic retries occurred; sandbox DNS failures received zero body bytes and were rerun only after escalation.

Raw selected data remain immutable and ignored locally. See `chunk_acquisition_manifest.json`, `monthly_checkpoint.csv`, resource receipts and `historical_data_readiness.md`. The25 conflicting keys require source clarification before any reconciliation can be proposed. Any changed raw interpretation, usable policy or source requires a separate human decision. This stop grants no continued acquisition, repair or training.
