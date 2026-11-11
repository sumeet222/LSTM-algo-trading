# R07 descriptive deep dive

All amounts describe executed archived books or separately labeled offline marks. The investigation followed repeated inspection of the same survivor sample. Full net individual-cohort outcomes were compacted. Exact frozen grouped net and raw reconstruction support are identified in the data table.

## Executed mechanism

R03 breakout only when latest completed RV10 below prior60RV10 20th percentile. first full ISO-week session, 5 physical tickets/week. Slots 1.
frozen channel breakout boundary, no continued compression gate. 10:30 each full XNYS session, decision after receipt.
The entry event qualifier is preserved at formation. Breakout and gap event references stay frozen for the hold. Ongoing monitoring, trail, maximum and account risk follow the original V3 adapter. Compression or confirmation volume need not persist after entry. 10 following sessions, same offset/clamp close.

## Executed account evidence

| Regime | Gross price USD | Actions USD | Costs USD | Net USD | Risk lots / closed | Median trading min | Mean gross/NAV |
|---|---:|---:|---:|---:|---:|---:|---:|
| CONSERVATIVE | 1,891 | 63 | 1,837 | 117 | 27/94 | 780.0 | 2.3% |
| STANDARD | 615 | 139 | 1,984 | -1,230 | 62/96 | 390.0 | 1.4% |
| HIGH_RISK | -1,010 | 76 | 2,300 | -3,234 | 50/96 | 392.0 | 2.0% |

| Regime | 2021 | 2022 | 2023 | 2024 | Sharpe | CAGR | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|
| CONSERVATIVE | -0.39% | -0.34% | -0.03% | 0.88% | 0.028 | 0.03% | -2.69% |
| STANDARD | -0.23% | -0.73% | -0.82% | 0.55% | -0.294 | -0.31% | -3.12% |
| HIGH_RISK | -0.33% | -1.44% | -1.62% | 0.13% | -0.563 | -0.82% | -5.39% |

Prior V2/D3 net was USD 1,845.214888. That configuration retains its own holding and cap rules.

Prior V2/D5 net was USD 2,574.485154. That configuration retains its own holding and cap rules.

Prior V3/CONSERVATIVE net was USD 117.009705. That configuration retains its own holding and cap rules.

## Attribution and fragility

| Regime | Long net USD | Short net USD | Top two net tickers | Their net contribution | Account less their contribution |
|---|---:|---:|---|---:|---:|
| CONSERVATIVE | 161 | -44 | TSLA,WFC | 1,058 | -941 |
| STANDARD | -1,221 | -9 | TSLA,VZ | 1,468 | -2,699 |
| HIGH_RISK | -3,322 | 87 | VZ,BAC | 458 | -3,692 |

Raw tails, winner/loser sums, months, realized holding, side, ticker, drawdown episodes and shared-entry/changed-exit counts are in the companion table. A raw reconstruction mismatch prevents raw cohort claims for that case. Exact group tables remain usable. Removing contributors is arithmetic with all other book effects fixed.

## Nonforced external extensions

| Regime | Horizon | Valid / exits | Raw mean bps | Conditional bps per exit dollar | Missed upside USD | Avoided loss USD |
|---|---|---:|---:|---:|---:|---:|
| CONSERVATIVE | T60 | 72/72 | -4.00 | -4.87 | 1,174 | 1,414 |
| CONSERVATIVE | T240 | 72/72 | -5.14 | -3.20 | 2,013 | 2,167 |
| CONSERVATIVE | NEXT_FULL_SESSION | 69/72 | 67.62 | 66.45 | 5,052 | 1,899 |
| STANDARD | T60 | 40/40 | -3.32 | -4.38 | 508 | 619 |
| STANDARD | T240 | 40/40 | -2.49 | 4.33 | 1,176 | 1,065 |
| STANDARD | NEXT_FULL_SESSION | 37/40 | 77.92 | 68.43 | 2,333 | 748 |
| HIGH_RISK | T60 | 54/54 | 0.44 | -0.79 | 935 | 966 |
| HIGH_RISK | T240 | 54/54 | 0.64 | 4.69 | 1,905 | 1,704 |
| HIGH_RISK | NEXT_FULL_SESSION | 51/54 | 61.93 | 59.61 | 3,684 | 1,317 |

This panel excludes recorded risk-forced and internal portions. The complete table retains both and all source censors. Conditional standalone margin has a hypothetical replacement exit, frozen-mark short carry and standalone ticket difference. It neither reserves capital nor cancels other cohorts. Exact net preceding-cohort versus future-mark correlation is unavailable from the compacted archive. The separate raw-leg and saved-strength strata describe associations without replacing absent net allocations.

## Cost intensity

| Regime | External orders | Commission | Price concession | Impact | Borrow | Turnover | Account cost bps | Break-even bps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CONSERVATIVE | 193 | 195 | 791 | 791 | 59 | 1,504,793 | 12.21 | 12.98 |

CONSERVATIVE same-holdings price-cost arithmetic at .5/1/1.5× gives 908/117/-674 USD. Quantities, fees and carry stay fixed in this accounting sensitivity.
| STANDARD | 199 | 202 | 869 | 869 | 43 | 1,653,044 | 12.00 | 4.56 |

STANDARD same-holdings price-cost arithmetic at .5/1/1.5× gives -361/-1,230/-2,100 USD. Quantities, fees and carry stay fixed in this accounting sensitivity.
| HIGH_RISK | 200 | 209 | 1,018 | 1,018 | 54 | 1,936,969 | 11.87 | -4.82 |

HIGH_RISK same-holdings price-cost arithmetic at .5/1/1.5× gives -2,216/-3,234/-4,252 USD. Quantities, fees and carry stay fixed in this accounting sensitivity.

Risk labels may be whole-account spillovers. Their incidence and primary precedence cannot reconstruct missing per-order headroom. Strong or weak scores may have different stock, side and year mixes. All 2024 reference cutoffs, half-days, ordinary actions and unsupported special crossings stay visible in the common coverage table.

## Comparison and next hypothesis

R01 is a weekly six-minus-one-month momentum rank with concentrated long gains. This mechanism keeps its own cadence and cost mode. The unchanged V1/V2/V3 controls remain available, with different executed holds and book feedback. The companion findings appendix sets the proposal and its falsification rule.

## Findings and falsifiable next test

**HOLD_INSUFFICIENT_EVIDENCE for a general continuation claim.**
A narrowly frozen event-failure hypothesis is available for later testing.
V2 D3 and D5 had 96 cohorts each. Gross/action/cost/net were
3,766.52/72.28/1,993.59/1,845.214888 USD and
4,436.50/159.01/2,021.03/2,574.485154 USD. Their mean marked RTH
gross/NAV was only 1.06% and 1.59%. Both had positive longs and shorts
in aggregate. D3 annual NAV changes were +1,137, −96, −45 and +849.
D5 gave +2,221, +29, −268 and +593. TSLA supplied USD 1,636 of D3
and USD 2,160 of D5 net. Removing its contribution leaves about
USD 209/415. Removing the top two net tickers turns D3 negative
and leaves about USD 76 for D5. This is narrow name support.

The planned 3/5-session policies had median realized 350/565 scheduled
minutes. Early closure affected 58/96 and 64/96 cohorts. They were
not portfolios that held every lot for the advertised multi-day duration.
V3 H85's USD 117 gain had USD 8,163 gross winners and −USD 6,273 losers,
a 1.301 gross profit factor, 43.6% gross hit rate, USD 199 average gross
winner, −USD 118 average gross loser and −USD 25.79 median. Its best raw
trade was USD 929. Removing that raw contribution while retaining other
components makes net −USD 812. TSLA and WFC jointly contributed
USD 1,058 net. Other names combined were negative. Only 2024 had a
positive V3 H85 annual return.

H85 nonforced +60 and +240 were negative (−USD 241 and −USD 154 raw).
Next-full-session was +USD 3,153 raw over 69 valid of 72 legs, with
USD 5,052 upside and USD 1,899 avoided loss. The below-100 population
and horizon disagreement prevented diagnostic promotion under the rubric.
Risk next-session marks were negative (−USD 1,047), with USD 1,187 upside
and USD 2,233 avoided loss. These do not support overriding caps.
The EVENT_RESOLVED next-session subgroup had 29 valid legs and
USD 1,634 raw continuation. Both favorable and adverse examples remain.

If later authorized, one fixed rule can require **two consecutive valid
daily channel-failure checks** before EVENT_RESOLVED. The known original
breakout boundary and 5 bp failure band stay frozen. Reset confirmation
on missing data. Original weakening, reversal, trail, ten-session maximum
and hard-cap handling remain. Entries stay weekly 10:30 and costs stay
retail. Use unchanged H85 as control. This tests failed-breakout whipsaw,
with prompt control for a genuine break whose loss worsens during waiting.
Falsify if normalized net fails to improve, or the apparent benefit is
restricted to TSLA or one chronological half. No extra horizon grid is
proposed. Until wider source-supported sample exists, retain this as a
low-priority hypothesis and preserve all fixed-horizon references.
