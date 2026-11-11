# M01 descriptive deep dive

All amounts describe executed archived books or separately labeled offline marks. The investigation followed repeated inspection of the same survivor sample. Full net individual-cohort outcomes were compacted. Exact frozen grouped net and raw reconstruction support are identified in the data table.

## Executed mechanism

sign received intraday r60 when abs(r60/sigma_past20slot)>=1. legal strategy slots, 6 new physical tickets/session. Slots 1,2,3,4,5,6.
own standardized r60. legal micro slots; M07 same-clock score; M09 extra next-day open/first hour.
The entry event qualifier is preserved at formation. Breakout and gap event references stay frozen for the hold. Ongoing monitoring, trail, maximum and account risk follow the original V3 adapter. Compression or confirmation volume need not persist after entry. 780 scheduled minutes.

## Executed account evidence

| Regime | Gross price USD | Actions USD | Costs USD | Net USD | Risk lots / closed | Median trading min | Mean gross/NAV |
|---|---:|---:|---:|---:|---:|---:|---:|
| CONSERVATIVE | 7,184 | -64 | 16,124 | -9,004 | 568/6007 | 120.0 | 10.4% |
| STANDARD | 5,362 | -67 | 18,209 | -12,914 | 960/6007 | 120.0 | 11.1% |
| HIGH_RISK | 5,961 | -80 | 19,172 | -13,290 | 631/6005 | 120.0 | 12.3% |

| Regime | 2021 | 2022 | 2023 | 2024 | Sharpe | CAGR | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|
| CONSERVATIVE | -1.95% | -3.11% | -0.19% | -4.04% | -1.037 | -2.34% | -11.90% |
| STANDARD | -1.92% | -3.37% | -2.76% | -5.50% | -1.445 | -3.41% | -14.86% |
| HIGH_RISK | -2.56% | -3.98% | -1.64% | -5.78% | -1.343 | -3.51% | -15.58% |

## Attribution and fragility

| Regime | Long net USD | Short net USD | Top two net tickers | Their net contribution | Account less their contribution |
|---|---:|---:|---|---:|---:|
| CONSERVATIVE | -3,228 | -5,776 | TSLA,AVGO | 3,055 | -12,059 |
| STANDARD | -6,388 | -6,526 | BA,AMD | 2,215 | -15,129 |
| HIGH_RISK | -6,937 | -6,353 | BA,AVGO | 2,587 | -15,877 |

Raw tails, winner/loser sums, months, realized holding, side, ticker, drawdown episodes and shared-entry/changed-exit counts are in the companion table. A raw reconstruction mismatch prevents raw cohort claims for that case. Exact group tables remain usable. Removing contributors is arithmetic with all other book effects fixed.

## Nonforced external extensions

| Regime | Horizon | Valid / exits | Raw mean bps | Conditional bps per exit dollar | Missed upside USD | Avoided loss USD |
|---|---|---:|---:|---:|---:|---:|
| CONSERVATIVE | T60 | 5879/5879 | 0.29 | 0.25 | 39,240 | 38,540 |
| CONSERVATIVE | T240 | 5877/5879 | 0.62 | 1.08 | 121,031 | 118,136 |
| CONSERVATIVE | NEXT_FULL_SESSION | 5877/5879 | 2.88 | 3.16 | 142,184 | 134,748 |
| STANDARD | T60 | 5573/5573 | 0.61 | 0.76 | 39,428 | 37,682 |
| STANDARD | T240 | 5571/5573 | 1.76 | 2.00 | 122,749 | 117,962 |
| STANDARD | NEXT_FULL_SESSION | 5571/5573 | 3.55 | 3.90 | 143,819 | 134,863 |
| HIGH_RISK | T60 | 5987/5987 | 0.49 | 0.75 | 45,429 | 43,412 |
| HIGH_RISK | T240 | 5985/5987 | 2.87 | 3.55 | 142,407 | 133,184 |
| HIGH_RISK | NEXT_FULL_SESSION | 5985/5987 | 5.50 | 6.05 | 166,659 | 151,164 |

This panel excludes recorded risk-forced and internal portions. The complete table retains both and all source censors. Conditional standalone margin has a hypothetical replacement exit, frozen-mark short carry and standalone ticket difference. It neither reserves capital nor cancels other cohorts. Exact net preceding-cohort versus future-mark correlation is unavailable from the compacted archive. The separate raw-leg and saved-strength strata describe associations without replacing absent net allocations.

## Cost intensity

| Regime | External orders | Commission | Price concession | Impact | Borrow | Turnover | Account cost bps | Break-even bps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CONSERVATIVE | 12348 | 1,071 | 13,643 | 1,267 | 143 | 47,223,946 | 3.41 | 1.51 |

CONSERVATIVE same-holdings price-cost arithmetic at .5/1/1.5× gives -1,549/-9,004/-16,459 USD. Quantities, fees and carry stay fixed in this accounting sensitivity.
| STANDARD | 12454 | 1,204 | 15,410 | 1,448 | 148 | 53,341,505 | 3.41 | 0.99 |

STANDARD same-holdings price-cost arithmetic at .5/1/1.5× gives -4,485/-12,914/-21,343 USD. Quantities, fees and carry stay fixed in this accounting sensitivity.
| HIGH_RISK | 12531 | 1,262 | 16,189 | 1,550 | 171 | 55,960,684 | 3.43 | 1.05 |

HIGH_RISK same-holdings price-cost arithmetic at .5/1/1.5× gives -4,421/-13,290/-22,160 USD. Quantities, fees and carry stay fixed in this accounting sensitivity.

Risk labels may be whole-account spillovers. Their incidence and primary precedence cannot reconstruct missing per-order headroom. Strong or weak scores may have different stock, side and year mixes. All 2024 reference cutoffs, half-days, ordinary actions and unsupported special crossings stay visible in the common coverage table.

## Comparison and next hypothesis

R01 is a weekly six-minus-one-month momentum rank with concentrated long gains. This mechanism keeps its own cadence and cost mode. The unchanged V1/V2/V3 controls remain available, with different executed holds and book feedback. The companion findings appendix sets the proposal and its falsification rule.

## Findings and falsifiable next test

**REVISE_MECHANISM.** No executed positive configuration was identified.
Conservative raw winners/losses were USD 77,363/−70,180, but net was
−USD 9,004. Both sides lost after costs. SIGNAL_WEAKENING accounted
for 5,175 of 6,007 lot closures and earned USD 8,653 gross while losing
USD 5,047 net. This is a turnover/cost mechanism rather than evidence
that every direction was wrong. Nonforced external +240 and next-session
raw continuation was USD 2,895/7,436, with conditional USD 2,256/6,633.
Those margins are small relative to USD 118,136/134,748 avoided losses.
The +240 raw advantage disappears without the top two stocks. The
next-session margin survives those concentration diagnostics.

The weakening group itself had only USD 46 raw after +60 and a slightly
negative conditional margin, then USD 2,962 after +240 and USD 6,957 at
the next session. Thus a blanket one-hour extension has weak backing.
Risk next-session continuation was negative. The raw-cohort reconstruction
differs from the archived total by USD 2.265 because the first-entry
marker does not identify every entry-basis component. Exact grouped
net and gross remain valid. Fully net cohort quantiles are unavailable.

A precise future hypothesis is three valid weakening confirmations
instead of two **only while the aligned score remains nonnegative**.
A sign reversal or other unchanged exit stays effective. Entries,
receipt, budget, stops, maximum and costs remain fixed. Use unchanged
conservative V3 as control on a fixed untouched period. Falsify if
extra gross payoff per turnover does not cover costs or if additional
losses and carry offset the reduced churn. The small one-hour evidence
and correlated stock drift are direct competing explanations.
