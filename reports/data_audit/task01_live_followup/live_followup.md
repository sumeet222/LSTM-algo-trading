# Task 01 live pilot follow-up

This note supersedes the missing-credentials and zero-stock-data status in
[task01_decisions.md](../task01_decisions.md) and the initial session report.
Their earlier observations are preserved as the state before credentials appeared.

The researcher created a local ignored `.env` while the task was running. Only
credential-presence booleans were inspected; no values were printed. `.env.example`
had disappeared, so the empty standard-name template was recreated. The local
credential file was preserved without modification.

The first credentialed sandbox attempt exhausted four transport failures (no HTTP
responses). The approved network retry then completed all seven pilot requests:
**seven HTTP 200 responses, historical SIP access passed, native-hour timing failed**.
There were no provider 401/403/422/429/5xx errors and no retries in the successful run.
The account's subscription tier was not queried or inferred; historical SIP availability
was demonstrated only for these selected old windows.

| Probe | Symbol | Calendar dates queried | Rows |
|---|---|---|---:|
| Historical 2020 | AAPL | 2020-07-01 through 2020-07-10 | 110 |
| Historical 2025 | AAPL | 2025-06-23 through 2025-06-30 | 96 |
| Fall DST | AAPL | 2020-10-30 through 2020-11-02 | 30 |
| Spring DST | AAPL | 2021-03-12 through 2021-03-15 | 30 |
| Early close | AAPL | 2020-11-27 | 13 |
| AAPL split window | AAPL | 2020-08-28 through 2020-09-01 | 46 |
| WMT split window | WMT | 2024-02-23 through 2024-02-27 | 45 |

Total: **370 source bars** (AAPL 325, WMT 45), seven tiny Parquet sample files,
**69,080 bytes**. JPM/JNJ/CAT and the full five-year panel were not downloaded.
The samples are ignored under `data/interim/alpaca_pilot/task01_sip_pilot_network_retry/`.
Each sample's SHA-256/path appears in
[sip_pilot.json](../task01_sip_pilot_network_retry/sip_pilot.json).
Original USA500 source bytes remain unchanged.

## Measured timing evidence

Every one of the 370 native bars starts at local minute `:00`. For example:

| Session | XNYS open / close UTC | Overlapping provider starts in New York | Desired first start |
|---|---|---|---|
| 2020-07-01 | 13:30 / 20:00 | 09:00, 10:00, …, 15:00 | 09:30 |
| 2020-11-02, after DST | 14:30 / 21:00 | 09:00, 10:00, …, 15:00 | 09:30 |
| 2020-11-27, early close | 14:30 / 18:00 | 09:00, 10:00, 11:00, 12:00 | 09:30 |
| 2021-03-15, after DST | 13:30 / 20:00 | 09:00, 10:00, …, 15:00 | 09:30 |

The opening native 09:00 hour overlaps premarket and RTH. Native 10:00–11:00
cannot be relabeled as 09:30–10:30; OHLCV does not identify either half's trades.
The desired session-anchored closing 30-minute stub is not recoverable from these
clock-hour aggregates. No regular NYSE lunch break is expected; native hourly bars
are clock-aligned there too. Detailed per-day starts/missing/extra lists are in the
live pilot JSON. Missing desired starts are a convention mismatch, not evidence
that all RTH trades are missing from SIP.

Split-adjusted AAPL/WMT pilot windows have no daily price-jump candidate exceeding
20% in the implemented QA. This is limited continuity evidence, not verification of
complete corporate-action history, adjustment vintage or volume semantics. Only
the explicitly requested split-adjusted samples were obtained.

## Alignment diagnostic

[alignment_diagnostic.json](alignment_diagnostic.json) compares the user-approved
provisional index timestamp-as-close assumption with a one-hour availability delay.
The seven checksum-verified samples are concatenated only in memory; no canonical
store or additional table copy is created. Both all-native-bar and fully-inside-RTH
subsets are examined. Native stock availability is hypothesized as start +60 minutes.
Backward-only matches forbid a future available index row and flag ages over 90 minutes.
Results are audit-only; a failed session-anchor gate is not overridden by alignment.

## Stop/go decision

**Bulk acquisition stopped.** A targeted approval question was presented for 30Min SIP
source bars, a small new pilot and causal session-anchored hourly aggregation with
closing stubs retained. No approval has been inferred from elapsed time. No 30Min
request, alternative feed, subscription or full-history acquisition has occurred.

Recommend 30Min as the next measured alternative: about twice the source rows,
approximately 301,200 rows / 38.55 MB uncompressed in the conservative full-period
plan, at least 60 monthly initial calls plus pagination/retries. Measured small
30Min samples and new aggregation tests must pass before bulk. The current config
and implementation continue to refuse resolution changes without that reviewed update.

The already approved USA500 close assumption is retained. Split price/volume adjustment
remains explicit and provisional for bulk; its retrospective-level limitations must
be reviewed with the new bar convention. Final trade-clock/feature joins and modeling
remain outside this task.
