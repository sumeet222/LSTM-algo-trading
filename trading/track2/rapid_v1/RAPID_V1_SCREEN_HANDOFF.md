# HF20 Track 2 Rapid V1 screening handoff

**COMPLETE_EXPLORATORY.** All 18 strategies ran with $100,000 each from 2021 through 2024. All 18 finished below starting capital. Seven had positive gross signed-price P&L and lost money after modeled friction. There were zero HOLD, NO_TRADES or UNIMPLEMENTABLE accounts.

The completed screen covers the fixed 20-stock universe and 1,005 XNYS sessions. Feature preparation covers all 7,014 nominal slots and 140,280 stock opportunities, with 139,964 received price references. The funded replay read 48 monthly price partitions once across the 18 books. The feature cache read 60, including 2020 warmup. The same bars feed funded and mature-only diagnostics through separate account and outcome state.

## Funded defaults

USD except CAGR and maximum drawdown. Gross P&L is signed-price P&L before costs and action cash. Fees are physical external commissions. Total cost includes price friction and borrow. Sharpe uses 252 sessions and zero risk-free return. All rows have status COMPLETE.

| ID | Net P&L | CAGR | Sharpe | Max DD | Gross price | Gross winners | Gross losers | Fees | Total cost | External orders | Cohorts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| M01 | -5,843 | -1.50% | -0.62 | -8.71% | 12,670 | 97,131 | -84,461 | 1,231 | 18,594 | 12318 | 6021 |
| M02 | -26,783 | -7.52% | -3.25 | -26.81% | -10,591 | 74,449 | -85,039 | 1,079 | 16,204 | 12221 | 6021 |
| M03 | -13,078 | -3.45% | -1.40 | -15.21% | -1,365 | 80,717 | -82,082 | 790 | 11,739 | 8739 | 4210 |
| M04 | -6,173 | -1.58% | -0.78 | -7.82% | 3,731 | 53,048 | -49,317 | 698 | 9,905 | 4410 | 2107 |
| M05 | -13,467 | -3.56% | -1.58 | -14.83% | 4,265 | 88,312 | -84,047 | 1,172 | 17,760 | 12346 | 6026 |
| M06 | -16,729 | -4.49% | -1.80 | -20.78% | 7,817 | 124,958 | -117,141 | 1,565 | 24,543 | 12312 | 6023 |
| M07 | -19,240 | -5.22% | -2.54 | -19.93% | -4,131 | 84,735 | -88,866 | 1,004 | 15,131 | 12365 | 6029 |
| M08 | -29,242 | -8.31% | -2.62 | -29.75% | -10,279 | 95,527 | -105,805 | 1,227 | 18,814 | 8286 | 4127 |
| M09 | -15,296 | -4.08% | -1.24 | -15.52% | -593 | 113,221 | -113,814 | 915 | 14,381 | 10192 | 4988 |
| R01 | -9,834 | -2.56% | -2.77 | -9.83% | -61 | 17,392 | -17,453 | 1,711 | 9,773 | 1711 | 832 |
| R02 | -10,883 | -2.85% | -3.39 | -11.17% | -668 | 12,799 | -13,467 | 2,108 | 10,216 | 2108 | 1030 |
| R03 | -4,190 | -1.07% | -1.28 | -4.57% | 797 | 8,369 | -7,572 | 624 | 4,987 | 619 | 295 |
| R04 | -11,358 | -2.98% | -3.13 | -11.36% | -1,693 | 14,864 | -16,557 | 1,678 | 9,665 | 1677 | 816 |
| R05 | -2,698 | -0.68% | -2.99 | -2.70% | 297 | 2,747 | -2,451 | 335 | 2,995 | 320 | 160 |
| R06 | -9,538 | -2.48% | -3.16 | -9.58% | -140 | 12,593 | -12,733 | 1,524 | 9,398 | 1522 | 727 |
| R07 | -1,439 | -0.36% | -0.79 | -1.89% | 506 | 2,942 | -2,436 | 207 | 1,945 | 203 | 96 |
| R08 | -4,641 | -1.18% | -1.34 | -5.67% | -781 | 7,085 | -7,866 | 479 | 3,849 | 474 | 218 |
| R09 | -9,561 | -2.49% | -2.72 | -9.94% | -700 | 11,355 | -12,055 | 1,097 | 8,861 | 1082 | 506 |

## Outcome coverage and annual returns

| ID | 2021 | 2022 | 2023 | 2024 | Candidates | Mature price outcomes | Hit rate | Mean signed bps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| M01 | -1.34% | 0.06% | 0.40% | -5.00% | 35490 | 35475 | 49.62% | 1.56 |
| M02 | -7.42% | -8.73% | -7.84% | -5.98% | 35490 | 35475 | 50.07% | -1.56 |
| M03 | -6.23% | -6.47% | -1.91% | 1.04% | 10601 | 10600 | 50.68% | 1.11 |
| M04 | -2.15% | -2.53% | -1.33% | -0.30% | 4985 | 4985 | 48.65% | -0.35 |
| M05 | -1.18% | -6.08% | -3.45% | -3.44% | 33408 | 33383 | 50.17% | 3.19 |
| M06 | -1.94% | -5.23% | -4.21% | -6.46% | 20754 | 20743 | 50.19% | 2.47 |
| M07 | -3.79% | -4.66% | -4.36% | -7.94% | 47506 | 47477 | 49.06% | -2.58 |
| M08 | -4.65% | -14.22% | -10.77% | -3.04% | 7717 | 7716 | 49.94% | -2.18 |
| M09 | -6.72% | -1.36% | -5.34% | -2.75% | 11925 | 11915 | 50.63% | 0.50 |
| R01 | -3.10% | -2.40% | -2.11% | -2.60% | 832 | 832 | 47.36% | -0.59 |
| R02 | -2.68% | -2.65% | -3.00% | -3.03% | 1910 | 1910 | 48.06% | -3.67 |
| R03 | -0.38% | -1.26% | -0.53% | -2.07% | 308 | 308 | 47.40% | 7.67 |
| R04 | -4.85% | -1.39% | -2.66% | -2.95% | 817 | 817 | 48.35% | -4.56 |
| R05 | -0.64% | -0.95% | -0.37% | -0.78% | 94 | 94 | 57.45% | 1.61 |
| R06 | -3.16% | -1.92% | -2.24% | -2.59% | 727 | 727 | 49.24% | -2.40 |
| R07 | -0.44% | -0.59% | -0.42% | 0.00% | 96 | 96 | 50.00% | 9.29 |
| R08 | 0.34% | -1.34% | -1.21% | -2.50% | 222 | 222 | 47.75% | -4.40 |
| R09 | -2.66% | -3.09% | -2.12% | -2.05% | 506 | 506 | 51.98% | 1.80 |

The independent price-only diagnostic scored 213,281 of 213,388 intents. Censoring retained 98 calendar cutoff cases, seven MRK spinoff crossings and two entry expiries. Equal-notional scores exclude actions and capital, fees and liquidity constraints. The opposite-sign null uses the same matured outcomes. Break-even bps are descriptive.

## Cost and failure diagnosis

Across the nine separate micro books, gross winning and losing price moves summed to $812,098 and −$810,573, leaving $1,525 before costs and actions. The books paid $9,682 in commissions over 93,189 external orders, about $0.104 each. Modeled print slippage cost $123,735, impact $11,867 and borrow $1,786. The gross edge was small even with the hypothetical institutional commission. M01 had the smallest net micro loss (−$5,843). M08 lost $29,242, the largest micro loss, including a $10,279 gross signed-price loss.

Across the nine separate retail books, gross winners were $90,147 and gross losers −$92,591. The modeled commission averaged $1.005 across 9,716 external orders. The $1 floor bound on 9,517. The retail print-price friction and impact each cost $25,905, far more than the commission. The $2,000 entry floor rejected two attempts. R07 had the smallest net retail loss (−$1,439) on 96 cohorts. Its 24 cohorts in 2024 added only $1.18. R04 lost $11,358, the largest net retail loss. The sparse R07 result has less exposure and less evidence than the more frequent rules.

The funded ledger had 12,110 exits before their nominal 240-minute endpoint
(11,579 of 45,552 micro cohorts and 531 of 4,680 retail cohorts). The marked
risk caps can trigger prospective liquidation after a fill or price move,
especially for a vintage allocated near its cap. These exits are present in
the realized results. The unfunded diagnostic retains the original endpoint.
The funded P&L therefore reflects both the directional rule and the risk exits.

Gross cost-addback fields retain the original positions and decisions. They are arithmetic attribution and cannot establish how a frictionless portfolio would trade. For context, the sealed V5 matched S2C_RISK account ended near $1,927. V5 used different frequency, sign, cost and allocation conventions, limiting direct comparison.

Selected source examples are in the analysis directory. The order tables retain actual effective and posting minutes and signed quantities. The pretrade feature lineage and the source hash remain available separately from every exported price outcome. The bounded rejection context can retain the last scanned ticker for a later sizing rejection. The correction sidecar reconciles the two retail notional-floor cases against their actual decision frames. Order records, account ledgers and counts are unaffected.

The exploratory candidates for mechanism review are M01 and M06 for their positive gross continuation results, and R03 and R07 for the related channel-breakout hypothesis. None qualifies for a funded follow-on on this screen. R07's sparse opportunities and R05's small two-leg sample deserve particular caution. A later sizing experiment would first freeze a directional rule and then compare the frozen original magnitudes with equal, rolling and EWMA controls on a separately approved evaluation.

## Provenance, validation and resources

- Code-bound registry identity: ff4a5e12c7536acaaeaa03dc5017f65c41bb33787260819958afed7adc098d11
- Feature cache identity: 49a590a7d44f5900b67cf2faf37584b584a942807cca2fbab262250b80ea1f93
- Immutable results manifest SHA256: 7fe16983dbb7a77606020ce80dbd27fbc5253b53b3eb86d90ea1fe024281740f
- Financial replay wall time: 361.05 s. CPU time: 339.82 s. Peak RSS: 2,019,344,384 bytes. This includes annual checkpoint generation.
- Results: 19,292,050 bytes. Largest strategy directory: 2,021,808 bytes. Run through final publication: 108,049,046 bytes before the final receipt. Feature cache: 15,396,823 bytes, built in 35.53 s. No per-minute journal or duplicated raw panels.
- Five calendar pilots passed. Seeded AVGO −2/−3 orders match V5 retail book economics at the actual 16:34 UTC bar. The original 16:33 missing observation is retained.
- The bounded June pilot had no funded MRK shares at the distribution transition. The independent signed seed fixture verified ±4 whole OGN shares and ±0.3 fractional claims, micro $0.008 and retail $1 fees, CIL payment and short carry. AAPL, TSLA and AVGO split fixtures verified physical and virtual transformations at zero NAV residual.
- Ledger replay maximum Decimal balance residual: 4.8E-21 USD. Independent Parquet maximum NAV component residual: 2.18e-11 USD. All 18 account series have 1,005 observed dates and no terminal stock or pending order. M09 retained a priced $21.87 dividend payable in NAV.
- SHA256 and nanosecond mtime checked on 35,496 protected objects before and after. No changes during this session. Five Finder metadata drifts from the prior V5 seal already existed at start.
- 39 targeted tests passed. Ruff E/F/I and Rapid-owned Pyright passed. See the session report for repository-wide Pylance diagnostics.

## Reproduction and scope

See [REPRODUCE.md](REPRODUCE.md), [VALIDATION_MATRIX.md](VALIDATION_MATRIX.md) and [POLICY_AND_ASSUMPTIONS.md](POLICY_AND_ASSUMPTIONS.md). The CSV/Parquet outputs and annual resume states are intentionally local and ignored by Git. The run manifests bind the protocol and outputs. The January pilot reproduced byte-for-byte after restart.

Results use a reused fixed-survivor sample with retrospective source cleaning and actions, assumed receipt, conditional short availability and OHLCV fill proxies. The signal horizon is 240 scheduled minutes and may cross sessions. The realized holding period follows actual simulated entry and exit times. The project has neither synchronized NBBO nor verified historical stock locates. No new vendor data or neural inference was used. Independent Stage 6 and a prospective test remain outside this run.
