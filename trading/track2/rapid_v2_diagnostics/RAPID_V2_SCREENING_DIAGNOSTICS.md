# HF20 Track 2 Rapid V2 conclusions

All 108 funded cases completed over 1,005 XNYS sessions. The H100 replay
matched every V1 daily USD component exactly at the exported precision.
The 90 alternatives use the same 18 frozen signals and prices. See the
[all-ID results and four mechanism tables](runs/rapid-v2-20261110-r1/analysis/RAPID_V2_SCREENING_DIAGNOSTICS.md).

## Headroom reduced early liquidations

| Mode | H100 early | H85 early | H70 early | H85 net improved | H70 net improved | H85/H70 exposure-normalized net improved |
|---|---:|---:|---:|---:|---:|---:|
| Micro | 25.42% | 13.67% | 12.90% | 6/9 | 6/9 | 6/9 each |
| Retail | 11.35% | 1.86% | 1.44% | 7/9 | 8/9 | 5/9 each |

H85 reduced risk-tagged physical orders from 11,948 to 6,015 in micro and
568 to 89 in retail. H70 reduced those counts further to 5,692 and 71.
Exact trigger attribution shows that both buffers removed vintage-cap
attribution for the remaining 240-minute early closes. Every remaining
early close had a name-cap trigger. An allocation can reach the unchanged
name cap even when the total eligible vintage budget is smaller.

The headroom result is mixed after normalization. H85 and H70 improved net
P&L for 13 and 14 strategies, respectively. Both improved net P&L per
gross RTH dollar-year for 11 strategies. Retail H85's median marked gross
exposure increased from approximately 1.8% to 2.0% of NAV as more positions
survived, so its improvement did not come simply from shrinking exposure.
All 36 headroom alternatives remained negative. M01 and R07 earned less
net under either buffer despite substantially fewer early closes. M06 and
R03 improved under both. Changing the budget also changes rounded shares,
filled opportunities and overlapping exposure, which prevents attributing
every P&L change solely to the timing of forced exits.

## Arrival drift and costs

| V1 mode | Signed arrival USD | Absolute arrival USD | Assumed print USD | Assumed impact USD | Commission USD | Borrow USD | Effective round-trip cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| Micro | −1,207 | 528,349 | 123,735 | 11,867 | 9,682 | 1,786 | 6.86 bp |
| Retail | −625 | 53,071 | 25,905 | 25,905 | 9,763 | 113 | 25.12 bp |

Positive signed arrival is adverse. The direction-signed aggregate was
slightly favorable in both modes. About 48.6% and 48.1% of micro and retail
fills moved adversely from the last received mark. Absolute arrival was
large in both directions and does not enter the cost stack.

The audit found no arithmetic double charge. V1 booked the modeled
price concession in execution cash and added it back once to obtain
gross signed-price P&L. Raw-open P&L already reflects the arrival path.
Retail's price components include approximately $2,700 of adverse
cent-rounding. Its $1 minimum bound on 9,517 of 9,716 physical orders.
Micro had 93,189 physical orders. The round-trip costs above use twice
the turnover-weighted cost per side, with the two-side executed notional
as denominator. The totals describe independent accounts rather than
a combined portfolio.

Setting the added price concession to zero on the same fills would
leave six V1 cases positive after commission and carry: M01, M04, M05,
M06, R03 and R07. This is an arithmetic sensitivity. A funded rerun
would have different cash, capital and potentially fills. The raw open
is a transaction-print proxy and supplies no measured midpoint or spread.
See the [cash bridge, exact formulas and worked cases](FRICTION_ACCOUNTING_CONTRACT.md).

## Horizons that generated a larger gross edge

| Positive net case | Net USD | Gross price USD per $1M traded | Cost USD per $1M traded | Early | Median actual scheduled minutes |
|---|---:|---:|---:|---:|---:|
| M04 / 480 minutes | +1,454 | 379 | 349 | 59.0% | 372 |
| R07 / 3 sessions | +1,845 | 2,236 | 1,183 | 60.4% | 350 |
| R07 / 5 sessions | +2,574 | 2,611 | 1,189 | 66.7% | 565 |

These were the only positive cases. M04/480 lost $2,353 in 2022 and
gained $2,403 in 2024. R07/5 sessions earned $2,221 of its total in 2021
and lost $268 in 2023. In both cases the realized duration was well
below the nominal horizon on many trades.

For the requested four mechanisms, M01 had its best net result at
240 minutes (−$5,843) and best gross edge per turnover at 480 minutes.
M06 improved to −$15,879 at 480 minutes, with a median actual hold of
271 trading minutes. R03's five-session case improved to −$2,214 but
gross edge per $1M traded ($695) still fell short of costs. R07's
multi-session cases cleared the assumed costs in this sample.

Across the nine strategies in each mode, the strongest median net
horizon was 240 minutes for micro (−$15,296) and one session for retail
(−$6,331). The strongest median gross edge per turnover was at the
longest horizon in both modes: $6 per $1M for micro 480 and $262 per
$1M for retail five sessions. Those medians remain far below median
modeled costs of $353 and $1,244 per $1M, respectively.

A new test could precommit the R07 multi-session mechanism and M04's
longer intraday allowance, with realized holds and risk exits reported
separately. A separately specified retail 10-session and longer study
would need the same discipline. Quote data would help distinguish
arrival from actual spread and calibrate incremental impact. The
2021–24 panel was reused, has fixed survivors and uses retrospective
QA/actions and conditional borrow. A fresh untouched period is needed
to evaluate any selected rule. This diagnostic supplies no independent
Stage 6 evidence.

[Run status and reproduction](RUN_STATUS_AND_RECOVERY.md) ·
[Annual marked cash bridge](runs/rapid-v2-20261110-r1/year_audit/ANNUAL_MARKED_BRIDGE.csv)
