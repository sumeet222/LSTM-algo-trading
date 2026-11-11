# Rapid V3 findings

All 54 requested cases are accounted for. Status census {'COMPLETE': 54}. The 54 portfolios contain 146,744 completed directional cohorts. The cohort and order units differ. Gross raw-price P&L, signed action value, and each physical cost are separate in the financial tables.

[Full 18-ID assessment](runs/rapid-v3-20261110-r1/V3_SCREENING_ASSESSMENT.md)

## Outcomes and fixed reference

| Strategy | Regime | Net USD | Gross price USD | Action USD | Cost USD | Max DD |
|---|---|---:|---:|---:|---:|---:|
| R01 | CONSERVATIVE | 10,488 | 19,099 | -507 | 8,104 | -4.65% |
| R07 | CONSERVATIVE | 117 | 1,891 | 63 | 1,837 | -2.69% |

| Regime | Improved vs V1 fixed | Above its highest observed V2 fixed net |
|---|---:|---:|
| CONSERVATIVE | 9/18 | 3/18 |
| STANDARD | 8/18 | 2/18 |
| HIGH_RISK | 7/18 | 2/18 |

V2 maxima are exploratory references across its frozen horizons. The comparison changes realized holds, participation, available capacity and churn. It cannot isolate the independent value of an exit reason. The funded model remains at the V1 assumed print concessions and commission rates.

## Concentration, turnover and exit mix

| Mode | Regime | Median marked gross/NAV | Physical orders | Name-cap exits | Vintage-cap exits | All risk exits | Median strategy hold min |
|---|---|---:|---:|---:|---:|---:|---:|
| MICRO_PRO | CONSERVATIVE | 15.53% | 89,822 | 11,184 | 0 | 11,184 | 330 |
| MICRO_PRO | STANDARD | 14.65% | 91,495 | 15,589 | 2,417 | 18,006 | 184 |
| MICRO_PRO | HIGH_RISK | 18.20% | 91,558 | 8,447 | 5,895 | 14,368 | 271 |
| RETAIL_CONSERVATIVE | CONSERVATIVE | 10.75% | 7,896 | 469 | 0 | 469 | 1,170 |
| RETAIL_CONSERVATIVE | STANDARD | 7.17% | 8,473 | 880 | 1,143 | 2,023 | 721 |
| RETAIL_CONSERVATIVE | HIGH_RISK | 9.81% | 8,433 | 248 | 1,532 | 1,780 | 780 |

V1 fixed H100 used 93,189 micro and 9,716 retail external orders. These reference counts use the same physical ticket definition. The high-risk name cap allows more concentration with the same vintage and capital limits. Realized exposure, not the nominal cap, governs the economic comparison. Observed exact cap checks can cure a reservation-only breach by releasing an unsent quantity. The final exit reason counts actual settled cohorts.

Conservative risk exit shares were 25.09% micro and 12.04% retail, against 39.91% and 48.59% in standard. Higher concentration reduced name-related pressure but shifted realized closures toward the still-binding vintage cap. Measured gross exposure did not fall in every buffered case, since longer realized holds and slower capital erosion can keep more capital invested. The risk-exit share counts every dynamic risk exit, so use `risk_before_240` for comparisons against the four-hour cutoff.

Micro used 89,822–91,558 physical orders per regime against 93,189 under V1. Retail used 7,896–8,473 against 9,716. Fewer orders did not make any micro case profitable. M04 conservative gross price gain was USD 6,017 against USD 8,319 of modeled cost. R07 conservative was net positive by USD 117, entirely dependent on a positive 2024, and both other risk cases lost money. R01 conservative had the largest net gain, with losses in 2023 and in both other risk regimes across the full period.

## Sealed offline extension

| Horizon | Valid | Positive fraction | Missed gross USD | Losses avoided USD | Censored |
|---|---:|---:|---:|---:|---:|
| T60 | 158,008 | 53.79% | 1,889,557 | 1,617,383 | 110 |
| T240 | 157,204 | 51.69% | 3,936,042 | 3,628,371 | 914 |
| NEXT_FULL_SESSION | 156,195 | 51.49% | 5,333,831 | 5,029,867 | 1,923 |

Every actual directional exit leg is included, with its original signed quantity and actual modeled raw-share exit price. Partial legs are separate observations. The proposed later reference uses a raw open and has no assumed additional fee or carry. Relative to the actual fill this can include recovery of the paid exit concession. Dollars for separate horizons reuse the same exits. They must not be combined. Risk-forced cases are labeled infeasible. Score strata mix exit causes and market states. An unknown exit score often reflects a risk order without a simultaneous score refresh. Entry-strength strata remain available for every leg.

This evidence uses an already researched 2021–24 survivor panel, retrospective action and source QA, assumed receipt, OHLCV print proxies, and conditional short availability. A prospective experiment would precommit the exit mechanism and separately evaluate position sizes and execution with fresh data. Larger buffers and wider name limits change portfolios, not just the price at which the same trades exit. No offline continuation is a funded trading result.

A focused next test would freeze R01's conservative settings and compare the dynamic rule with a fixed-horizon control on a genuinely untouched period at matched initial risk. R07's small margin and M04's cost gap make them useful mechanism checks rather than a basis for expanding the grid. The pooled strength comparison is descriptive and cannot separate exit-cause mix, concentration or the exit concession.
