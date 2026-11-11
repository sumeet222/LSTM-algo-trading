# All-18 post-exit mechanism report

The full population has 158,118 actual exit legs and 474,354 predeclared targets. Rows are leg quantities, including partial and internal/external portions. Each independent account has its own capital. Extension dollars do not combine into a portfolio result.

## Conservative-account context

| ID | Executed V3 net USD | Nonforced external +60 raw bps | +240 raw bps | Next-full-session raw bps | Diagnostic evidence |
|---|---:|---:|---:|---:|---|
| M01 | -9,004 | 0.29 | 0.62 | 2.88 | DIAGNOSTICALLY_INTERESTING |
| M02 | -20,736 | -0.83 | -1.07 | -3.30 | NEGATIVE_OR_INCONCLUSIVE |
| M03 | -11,882 | 1.15 | 1.43 | 4.04 | DIAGNOSTICALLY_INTERESTING |
| M04 | -2,118 | 3.66 | 5.05 | 5.21 | DIAGNOSTICALLY_INTERESTING |
| M05 | -21,100 | 0.65 | 2.94 | 3.54 | DIAGNOSTICALLY_INTERESTING |
| M06 | -17,189 | 0.85 | 1.54 | 3.15 | DIAGNOSTICALLY_INTERESTING |
| M07 | -9,784 | -3.96 | -6.59 | -1.25 | NEGATIVE_OR_INCONCLUSIVE |
| M08 | -26,886 | 0.23 | -0.79 | 0.96 | DIAGNOSTICALLY_INTERESTING |
| M09 | -15,609 | 1.20 | 1.52 | 2.13 | NEGATIVE_OR_INCONCLUSIVE |
| R01 | 10,488 | 1.69 | -4.13 | -22.17 | DIAGNOSTICALLY_INTERESTING |
| R02 | -19,724 | 2.53 | -1.35 | -5.38 | DIAGNOSTICALLY_INTERESTING |
| R03 | -7,469 | -1.08 | -11.62 | 25.56 | NEGATIVE_OR_INCONCLUSIVE |
| R04 | -13,365 | -0.98 | 4.97 | 5.28 | DIAGNOSTICALLY_INTERESTING |
| R05 | -3,873 | -2.14 | -3.30 | -8.92 | NEGATIVE_OR_INCONCLUSIVE |
| R06 | -9,347 | -0.93 | -1.56 | -8.43 | NEGATIVE_OR_INCONCLUSIVE |
| R07 | 117 | -4.00 | -5.14 | 67.62 | NEGATIVE_OR_INCONCLUSIVE |
| R08 | -5,862 | -1.88 | -3.20 | -3.67 | NEGATIVE_OR_INCONCLUSIVE |
| R09 | -7,771 | 1.51 | -5.55 | -12.02 | NEGATIVE_OR_INCONCLUSIVE |

All 54 account/regime combinations and conditional cost columns are in the CSV. This table uses the conservative regime consistently. Negative actual performance remains visible. Nonforced means no recorded risk trigger on that leg and supplies no capital-feasibility certificate.

## Previously executed positive configurations

| Study | ID | Exact configuration | Net USD |
|---|---|---|---:|
| V2 | M04 | T480 | 1,454 |
| V2 | R07 | D3 | 1,845 |
| V2 | R07 | D5 | 2,574 |
| V3 | R01 | CONSERVATIVE | 10,488 |
| V3 | R07 | CONSERVATIVE | 117 |

## Price, action and cost basis

Primary bps and favorable fractions use raw-to-raw signed price change, adjusted for supported share splits. Signed ordinary distributions are shown separately, as paid cash or an unpaid claim at the reference. Unsupported distributed assets are censored. Old V3 pooling used the actual adverse exit fill as anchor and censored every intervening corporate action. The legacy four-state means are independently reproduced in a dedicated CSV. They include exit-concession recovery.

Conditional standalone dollars add ordinary action value and original exit-concession recovery, subtract a new assumed exit concession and 2% ACT/365 short carry at the frozen exit mark, then subtract the difference of hypothetical standalone old/new ticket fees. No new entry or full roundtrip is charged. Actual netting, constraints and fee allocation may differ. Internal-only actual legs carry no external execution charge in the saved book. A hypothetical later standalone sale is a distinct conditional treatment. It is kept identifiable through the external flag.

Raw exit-dollar weighting and absolute share weighting are separate. Equal-exit-day means and 5/95% day dispersion are descriptive dependence checks. The leg count does not establish an independent sample size. Exit-score quintiles are formed from the saved per-strategy score distribution without future prices and preserve unknown scores. A latched submission score can predate its fill.

## Coverage and confounds

The five-minute reference search is restricted to the target session. The next-full-session target retains the same opening offset and skips half-days. Censoring distinguishes cutoff, absent price, forward-limit gaps and unsupported distributions. No market data after 2024 was opened. Risk-forced rows are labeled INFEASIBLE_UNDER_REALIZED_RISK. A good later mark can follow a correct risk exit. Every horizon is a fixed later reference with both missed upside and avoided loss.

No independent Stage 6 analysis, funded refinement, final baseline selection or LSTM sizing occurred. The 2021–2024 survivor panel and source/action cleaning have been repeatedly researched. Positive hypotheses require untouched evidence.

## Interpreting the state comparison and risk panel

At +240, the independently recomputed original actual-exit-anchor means
were +5.281642/+4.298624/+2.338254/+3.349880 bps for reversed/weak/strong/
unknown. New raw-to-raw means were +1.84455/+0.25625/−1.45504/−0.14456.
The reference population also changes because ordinary actions and splits
are supported here. The new means cannot isolate a cost effect by simple
subtraction. Neither set is a forecast or a feasible strategy return.

Risk continuation was not uniformly favorable. In conservative M04,
USD 1,809 of +240 raw continuation came from risk-tagged legs and
USD 3,250 from nonforced legs. M05 had negative risk continuation
against positive nonforced continuation. M06's +240 net raw diagnostic
had USD 5,510 in the infeasible risk panel versus USD 3,312 nonforced.
R03 had +USD 2,117 risk versus −USD 948 nonforced. R07's next-session
risk panel was negative. These differences preclude an automatic
“hold through risk liquidation” rule.

A separate cost-requirement table reports the raw bps needed to cover
the assumed replacement-exit cost, carry, standalone fee difference,
and signed action benefit. It is an unfunded accounting comparison,
with no extra roundtrip entry cost. Original individual-net outcomes
cannot be recovered where per-cohort actions/carry were compacted.
