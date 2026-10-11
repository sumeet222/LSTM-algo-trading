# P1.3B formation matrix

**Retrospective source diagnostics only; every formation eligibility decision remains BLOCKED.** No backups queried or activated. Each mean uses all 60 received sessions, April 6–June 30, 2020. Exact sums/means, quality counts and source locators are in `probe_results.json`; no raw panel retained.

| Primary | Present / expected | Missing / duplicate / unordered / invalid | Mean O×V USD m | Mean C×V USD m | Mean L×V USD m | Mean H×V USD m | Formation / membership |
|---|---:|---|---:|---:|---:|---:|---|
| AAPL | 60 / 60 | 0 / 0 / 0 / 0 | 12347.411 | 12373.672 | 12195.573 | 12527.798 | BLOCKED / UNKNOWN-BLOCKED |
| JPM | 60 / 60 | 0 / 0 / 0 / 0 | 2602.198 | 2588.086 | 2544.335 | 2644.333 | BLOCKED / UNKNOWN-BLOCKED |
| JNJ | 60 / 60 | 0 / 0 / 0 / 0 | 1439.041 | 1437.484 | 1421.427 | 1453.538 | BLOCKED / UNKNOWN-BLOCKED |
| WMT | 60 / 60 | 0 / 0 / 0 / 0 | 1249.318 | 1247.123 | 1232.920 | 1262.693 | BLOCKED / UNKNOWN-BLOCKED |
| CAT | 60 / 60 | 0 / 0 / 0 / 0 | 577.623 | 576.226 | 565.844 | 586.103 | BLOCKED / UNKNOWN-BLOCKED |

All 20 proxy means exceed the fixed $50m reference. **These are not approved liquidity estimates, actual traded-dollar bounds, or a formation PASS.** Daily volume includes eligible extended-hours trades under provider rules; OHLC extrema use a different eligible-trade set. The low/high products therefore show only price-statistic sensitivity. No missing rows were dropped, repaired or filled; no 98%/95% full-study threshold was applied to eligibility.

All four diagnostic rankings: **AAPL > JPM > JNJ > WMT > CAT**. Prospective high=AAPL and low=CAT remain unapproved D8 identity candidates. No H→L/L→H activation. Paired split-price/inverse-volume transforms preserve each product algebraically; adjusted prices with raw volume do not, and dividend price-only adjustments need not. Adjustment-choice sensitivity is algebraic only; no additional adjusted query or complete action ledger was authorized. Any split/dividend events in this window remain unidentified/unresolved here.

Source requested: SIP/raw/1Day/USD, `asof=2020-07-01`, five exact primaries. Returned symbols match. Every label is midnight ET (`04:00 UTC` during this window), corresponding to the New York day left boundary, not the first-trade time or historical publication. No evidence of then-available data vintages. Course membership remains undefined; backups would need separately authorized matching 60-session source evidence and genuine eligibility-failure/sector/membership decisions.

Two independent April 6 hand checks from source index 0 for each symbol:

- AAPL: 262.47 × 55,182,629 = **$14,483,784,633.63** (integer cents: 26,247 × 55,182,629 ÷ 100).
- JPM: 89.46 × 31,402,576 = **$2,809,274,448.96** (8,946 × 31,402,576 ÷ 100).

The five retained examples share response hash `d0fd39ba1fb4f3b96eea1305d419c61649da3319c3da68e6c9a23e8e73a98c6c`; exact request+symbol+timestamp and response-array index are their locators. Hashes establish received bytes, not permanent upstream versions or historical publication.

[Alpaca aggregation FAQ](https://docs.alpaca.markets/us/docs/market-data-faq) documents the daily timestamp and separate trade-condition update rules. [Bars reference](https://docs.alpaca.markets/us/reference/stockbars) documents raw/split adjustments and entity-mapping `asof`.
