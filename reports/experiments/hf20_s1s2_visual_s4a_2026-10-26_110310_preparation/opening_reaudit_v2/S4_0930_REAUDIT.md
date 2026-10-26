# S4-A09:30 source re-audit

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

| ticker | candidate_sessions | genuine_first_minutes | missing_minutes |
| --- | --- | --- | --- |
| AAPL | 3650 | 3645 | 5 |
| AMD | 3650 | 3628 | 22 |
| AMZN | 3650 | 3643 | 7 |
| AVGO | 3650 | 3645 | 5 |
| BA | 3650 | 3627 | 23 |
| BAC | 3650 | 3641 | 9 |
| COP | 3650 | 3642 | 8 |
| CSCO | 3650 | 3646 | 4 |
| CVX | 3650 | 3613 | 37 |
| JNJ | 3650 | 3642 | 8 |
| KO | 3650 | 3642 | 8 |
| MA | 3650 | 3410 | 240 |
| MRK | 3650 | 3527 | 123 |
| MS | 3650 | 3545 | 105 |
| PEP | 3650 | 3615 | 35 |
| SBUX | 3650 | 3645 | 5 |
| TSLA | 3650 | 3641 | 9 |
| VZ | 3650 | 3634 | 16 |
| WFC | 3650 | 3613 | 37 |
| XOM | 3650 | 3635 | 15 |

Complete year/ticker counts: S4_0930_ALL20_SOURCE_COVERAGE.csv.
Twenty fixed-date exact-price/input witnesses: S4_0930_ALL20_EXACT_SOURCE_WITNESSES.csv.
Publication uncertainty is separate from missing-price counts. The JSON decision binds
the exact local source documentation by path and SHA256. Raw/derived prices remain
local/private; no protected2026 partition was opened.
