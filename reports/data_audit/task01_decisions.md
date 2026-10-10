# Task 01 decisions and coverage

## Execution status

The original course CSV was audited without modification. The reusable data package,
five CLI commands, immutable canonical-store skeleton and offline tests were implemented.
No stock bars, other assets, features, labels, models or trading outputs were acquired/generated.

| Source | Actual coverage | Quality / blocker |
|---|---|---|
| Course USA500 | 29,510 observations; 2020-07-01 04:00 UTC to 2025-07-01 04:00 UTC | No nulls, duplicate timestamps, ordering defects, invalid OHLC or nonpositive prices. Overnight/Sunday data and fractional volume preserved. Final observation is July 1 00:00 New York, beyond named end date. |
| AAPL, JPM, JNJ, WMT, CAT SIP stocks | None downloaded | Credentials absent; live entitlement, timing and corporate-action behavior not measured. Candidates retained without replacement. |
| Common stock/index coverage | Not yet measurable | Stock acquisition and approved trade-clock rules still required. |

Course file: 2,083,715 bytes, SHA-256
`ba78d6bf933f0aca4dfcdedb69454d19aa29bfed84481b6ba1bcccdaf7b1634a`.
There are 22,008 timestamps outside XNYS regular sessions and 1,542 Sunday
observations in New York. Of the volume fields, 29,508 are fractional; their meaning
is unknown. Gap counts and representative UTC/New York days are in the
[source audit](task01_course/course_audit.md). Gaps cannot be labeled provider defects
without the upstream instrument's calendar.

## Follow-up to the source audit: researcher assumption

After the factual audit, the researcher explicitly instructed **"assume close for now"**
on 2026-10-10. This supersedes the audit's pending-approval statement for the
provisional timestamp-as-close assumption. The config records that instruction;
`course_timestamp_semantics` stays `unknown` because source/provider verification is
still absent. No additional approval is needed to retain the requested assumption.

The future audit-only stock alignment command treats `timestamp` as candidate index
availability and compares a +60-minute delay sensitivity scenario. Neither scenario
has been run against live stocks yet. Real publication delays may exceed either
assumption; no final feature join, decision clock or model was designed in this task.

## SIP pilot and stop/go gate

The [pilot command result](task01_sip_pilot/sip_pilot.md) records missing local
credentials. There were **zero HTTP requests, zero provider errors/retries and zero
downloaded stock bytes**. This is not an entitlement failure or a successful pilot.
Do not infer that the account has or lacks historical SIP access.

Current official docs describe explicit SIP and split price/volume adjustment,
symbol-first pagination, and historical free-plan limitations. The implementation
always specifies the material parameters, consumes every page and refuses IEX fallback.
See [Alpaca historical bars](https://docs.alpaca.markets/us/reference/stockbars)
and [Alpaca FAQ](https://docs.alpaca.markets/us/docs/market-data-faq).

The next live pilot requests seven small AAPL/WMT windows: July 2020, June 2025,
both DST transitions, a 2020 early close and issuer-documented split windows.
Per-session starts and partial overlaps are compared with XNYS opens/closes.
This cannot prove point-in-time vintage data or historical latency.

The native-hour gate intentionally fails when a session-anchored opening interval or
closing 30-minute stub cannot be established from native 60-minute aggregates.
Even apparently `:30`-anchored native hours cannot by themselves prove the stub.
The current bulk implementation therefore remains a **guarded skeleton**, expected
to block on normal NYSE sessions. It is not a completed acquisition or an approved
hourly convention. A code/config change and new pilot are required for a 30Min route.

## Size and cost safeguards

The saved [dry-run plan](task01_download_plan_v2.json) uses the intended fixed dates,
1,255 XNYS sessions and five candidates. Conservative session-day estimates:

| Source resolution | Rows at 24 hours/session-day | Uncompressed estimate at 128 bytes/row | Monthly initial calls |
|---|---:|---:|---:|
| Native 1Hour | 150,600 | 19,276,800 bytes | 60 |
| Proposed 30Min alternative | 301,200 | 38,553,600 bytes | 60 |

Pagination/retries can add requests. These are planning estimates, not actual provider
row counts or compressed sizes; extended/holiday coverage must be measured. Only
the original 2.08 MB CSV exists as source market data. No subscription, alternate
feed, other asset or high-storage download was attempted.

The v2 plan removes a theoretical globally-packed page count from the initial plan;
monthly chunks still need at least 60 initial requests. Both small plans are preserved
for traceability; neither is a record of actual acquisition.

## Commands and remaining decisions

After local credentials are set, run:

```bash
source .venv/bin/activate
lstm-data --env-file .env sip-pilot
lstm-data download --dry-run
```

If credentials are exported instead, omit `--env-file .env`. Keep credentials out
of chat and reports. The split adjustment is provisional: recommend approving it
for continuous price/volume analysis, with retrospective-level limitations recorded.

If measured native hours fail, the minimal research decision is whether to approve
a small **30Min SIP pilot**, followed by session-anchored 60-minute aggregation and
flagged 30-minute stubs. Recommended default: that controlled alternative, after
evidence is available. Consequences: roughly twice the input rows, new aggregation
tests and a fresh gate; no five-year minute download.

After a matching successful gate and human approval, the native skeleton exposes:

```bash
lstm-data --env-file .env download --approval configs/local_bulk_approval.json
lstm-data stock-qa
lstm-data alignment --max-age-minutes 90
```

These commands do not authorize bypassing failed native timing. The approval schema
is documented in [data/README.md](../../data/README.md). Stock QA and alignment need
a verified store. A 90-minute stale bound remains diagnostic, not a final research
parameter. Final target/trading-clock/index alignment choices belong to a later
research design task. The provisional close assumption already has researcher approval.
