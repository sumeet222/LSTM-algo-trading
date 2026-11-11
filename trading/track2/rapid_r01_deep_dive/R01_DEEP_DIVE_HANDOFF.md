# R01 deep-dive handoff

**Decision: REVISE the entry risk reserve. HOLD S2-C sizing.** The
frozen R01 account evidence reconciles and justifies a small controlled
test of cap feedback. It provides weak evidence for an immediately
profitable or stable directional rule.

| 2021–2024 outcome | Conservative H85 | Standard H100 | Higher concentration |
|---|---:|---:|---:|
| Gross signed-price P&L | USD 19,099.29 | USD 1,499.05 | −USD 1,294.21 |
| Action value | −USD 507.01 | −USD 273.20 | −USD 392.16 |
| Modeled costs | USD 8,103.89 | USD 8,855.24 | USD 8,924.65 |
| Net P&L | **USD 10,488.39** | **−USD 7,629.39** | **−USD 10,611.02** |
| Risk-closed lots | 140/498 | 420/618 | 374/610 |
| Median actual scheduled hold | 1,986 minutes | 1,170 minutes | 1,170 minutes |
| Mean marked RTH gross/NAV | 16.54% | 11.93% | 12.66% |

Gate A passed on the committed accounts, all 3,015 daily marks and the
reconstructed 3,510 physical tickets. H85 annual returns were +2.06%,
+4.61%, −2.08% and +5.69%, with 2.53% CAGR, 0.604 daily Sharpe annualized
at zero cash return and −4.65% maximum drawdown. High-risk ending cash
includes a separate USD 34.02 MRK dividend payable, marked in NAV and
due January 8, 2025. No 2025 stock prices were used.

## Mechanism and conflicting evidence

**Exit path explains most of the gap to standard.** On 463 shared
opportunities, both books entered at the same time and 309 exits changed.
Observed exit-price differences contributed USD 14,320 of the USD 17,600
gross gap. Cost savings were USD 751. H85 avoided vintage-cap-tagged
closures, held more exposure over time and skipped more duplicate
same-side candidates. Against high-risk, unshared opportunities explain
USD 9,988 of the USD 20,394 gross gap.

**Extending every risk exit would be a different experiment.** H85
outperformed by USD 17,479 gross on the shared H85/standard lots where
both books risk-closed. Where H85 closed by policy and standard by risk,
H85 underperformed by USD 4,538. Its five largest gross winners were
name-cap-tagged. Whole-account liquidation makes a lot's tag insufficient
to identify which name or vintage triggered the check. Archived
per-decision risk headroom and reservations are unavailable.

**The gains are concentrated.** Longs made USD 15,703 net and shorts lost
USD 5,214. TSLA and AVGO contributed USD 11,390 net. Removing their
contributions arithmetically leaves −USD 901. The five largest raw-price
winners contributed USD 10,861. The retained 2023 loss and nonmonotonic
strength deciles weaken a persistent-signal claim. Exact fully net
individual-cohort tails are unavailable because action/carry allocations
were compacted. The gain stays positive under the 1.5× price-cost
arithmetic on frozen holdings. That diagnostic leaves capital and orders
fixed. Offline next-session marks for H85 risk exits show USD 7,851
additional upside and USD 9,652 avoided loss, before new costs. Those
extensions were infeasible under the triggering limits.

## Next experiment

On a prespecified untouched period, compare unchanged H85 and H100
with one H100 arm using a one-v20 pre-entry vintage reserve. Keep the
same R01 rank, full-session weekly scan, caps, exit logic and costs.
Capture the per-decision risk/mark/reservation ledger and exact cohort
allocations. Falsify the reserve if it cuts vintage exits without
improving net per gross exposure-year. Require positive after-cost
performance from unchanged H85 on the new period before interpreting
sizing readiness. The selection of R01×H85 followed 18 strategies,
54 V3 cases and earlier fixed-horizon screens. All 18 remain in the
project.

Input-only audit found same-origin C3 support for 778/832 historical
candidates. Classical archive values carry the legacy sign and neural
readiness mask. A future overlay requires sign-independent control
readiness and a frozen R01 policy. A 240-minute absolute forecast
conditions entry exposure only in that proposed test. It does not
measure the variance of a ten-session hold.

All findings are exploratory on fixed survivors, with retrospective
actions and cleaning, assumed receipt and locates, and OHLCV print-based
execution. No new strategy-performance search, funded strategy replay
or LSTM sizing run occurred.

[Reconciliation](R01_RECONCILIATION_NOTES.md) · [Attribution](R01_ATTRIBUTION_REPORT.md) · [Matched analysis](R01_REGIME_DIVERGENCE.md) · [Friction and offline marks](R01_ECONOMIC_FRAGILITY.md) · [Refinement](R01_REFINEMENT_DECISION.md) · [Sizing readiness](R01_S2C_OVERLAY_READINESS.md) · [Hashes and validation](R01_ANALYSIS_MANIFEST.json)
