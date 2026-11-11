# Rapid V1 failure diagnosis

The 2021–24 screen uses the reused 20-stock survivor panel, retrospective
source cleaning and corporate actions, assumed receipt, conditional short
availability and OHLCV execution proxies.

| Failure mode | Observed evidence |
|---|---|
| Negative gross direction | Eleven of 18 funded price components were negative. For M01 on Jan 4 2021, AMD's decision was 15:32 UTC. Its actual modeled interval was 15:33–19:33 UTC and lost $115.60 before costs. The M01 Jan 6 KO trade lost $2.64 gross. |
| Positive gross direction with thin edge | Seven strategies had positive gross price P&L and lost after costs. M01 MRK on Jan 8 2021 gained $0.40 gross and lost $1.82 net. M01 VZ on Jan 12 gained $0.87 gross and lost $1.50 net. Both were decided at 15:32 UTC and entered at 15:33 UTC. |
| Print-price friction and order count | Micro had 93,189 external orders and about $135,602 in modeled print slippage and impact. M01's $12,670 gross price gain was smaller than its $18,594 total cost. M06 had about $71.1 million external notional and $24,543 costs across 12,312 orders. |
| Ticket minimum | The $1 floor bound for 9,517 of 9,716 retail external orders. Commissions were $9,763. Modeled retail slippage and impact together were $51,810. |
| Participation, rounding and floor | The two retail floor rejections were for 25 WFC shares at the received $49.455 mark on Dec 26 2023 at 15:32 UTC. The observed quote basis implies $1,236.375 proposed notional. The correction receipt resolves the bounded rejection sample's stale ticker context. R05 also recorded 13 hedge rounding or participation rejections and 73 joint-capacity waits. |
| Frequency and duplication | Micro recorded 119,882 cap and 34,073 same-side duplication rejections. The Jan 4 2021 M01 16:32 UTC batch included PEP, KO and SBUX duplicate suppressions. Retail recorded 897 cap rejections. These counts precede any outcome observation. |
| Marked risk exits | 11,579 micro and 531 retail lots closed before their original endpoint. The marked cap can bind when a filled vintage moves beyond its allocation headroom. No filled position was retrospectively rejected. |
| Missing observations and pending orders | M01 had an absent 18:33 UTC PEP opening bar on Jul 8 2022 and AVGO opening bars at 18:33 UTC on Oct 4 2022 and 16:33 UTC on Mar 30 2023. The execution ledger retains actual later times. There were 72 missing-bar attempt records and two modeled entry expiries across all accounts. No unresolved terminal stock or order remained. |
| Sparse and clustered support | R07 had 96 cohorts over four years. In 2024, 278 of 1,060 scheduled name rows lacked a complete range or scale, 51 failed compression and 24 qualified. Per-name, slot, overnight and long/short totals are in FUNDED_ATTRIBUTION.csv. |
| Action caveats | The unseeded June pilot carried no MRK lot through the spinoff. Source-backed seeded long and short fixtures checked whole OGN shares, fractional claims and fee/carry treatment. The market inputs remain subject to the original survivor and action-vintage qualifications. |

Each rejected example is from the decision-time frontier. Subsequent entry,
exit and P&L examples use the settled trade rows with their source and order
links. Additional cases and exact amounts are in
runs/rapid-v1-defaults-20261110-r1/analysis/SOURCE_BACKED_EXAMPLES.json,
ANOMALY_CONTEXT_CORRECTION.json and FUNDED_ATTRIBUTION.csv. Gross cost-addback
uses the same holdings and decisions. The table does not imply observed
fills or a simulated frictionless counterfactual.
