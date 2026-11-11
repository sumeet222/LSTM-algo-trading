# M03 descriptive deep dive

All amounts describe executed archived books or separately labeled offline marks. The investigation followed repeated inspection of the same survivor sample. Full net individual-cohort outcomes were compacted. Exact frozen grouped net and raw reconstruction support are identified in the data table.

## Executed mechanism

negative opening gap sign when abs(gap/past20gap_sd)>=1. legal strategy slots, 6 new physical tickets/session. Slots 0,1.
distance to frozen prior close in initial gap units. legal micro slots; M07 same-clock score; M09 extra next-day open/first hour.
The entry event qualifier is preserved at formation. Breakout and gap event references stay frozen for the hold. Ongoing monitoring, trail, maximum and account risk follow the original V3 adapter. Compression or confirmation volume need not persist after entry. 780 scheduled minutes.

## Executed account evidence

| Regime | Gross price USD | Actions USD | Costs USD | Net USD | Risk lots / closed | Median trading min | Mean gross/NAV |
|---|---:|---:|---:|---:|---:|---:|---:|
| CONSERVATIVE | -431 | -343 | 11,108 | -11,882 | 740/3864 | 449.0 | 19.3% |
| STANDARD | 1,044 | -293 | 13,288 | -12,538 | 1713/4100 | 390.0 | 17.9% |
| HIGH_RISK | 2,737 | -445 | 13,802 | -11,510 | 1375/3998 | 390.0 | 20.6% |

| Regime | 2021 | 2022 | 2023 | 2024 | Sharpe | CAGR | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|
| CONSERVATIVE | -4.97% | -0.72% | -4.89% | -1.79% | -0.746 | -3.12% | -12.59% |
| STANDARD | -3.17% | -3.93% | -3.71% | -2.36% | -0.873 | -3.30% | -12.98% |
| HIGH_RISK | -4.04% | -5.54% | -2.51% | 0.14% | -0.724 | -3.02% | -12.45% |

## Attribution and fragility

| Regime | Long net USD | Short net USD | Top two net tickers | Their net contribution | Account less their contribution |
|---|---:|---:|---|---:|---:|
| CONSERVATIVE | -1,737 | -10,145 | AMZN,CVX | 3,196 | -15,078 |
| STANDARD | 1,476 | -14,013 | AMZN,MA | 2,941 | -15,479 |
| HIGH_RISK | -814 | -10,696 | MA,AMZN | 3,180 | -14,689 |

Raw tails, winner/loser sums, months, realized holding, side, ticker, drawdown episodes and shared-entry/changed-exit counts are in the companion table. A raw reconstruction mismatch prevents raw cohort claims for that case. Exact group tables remain usable. Removing contributors is arithmetic with all other book effects fixed.

## Nonforced external extensions

| Regime | Horizon | Valid / exits | Raw mean bps | Conditional bps per exit dollar | Missed upside USD | Avoided loss USD |
|---|---|---:|---:|---:|---:|---:|
| CONSERVATIVE | T60 | 3213/3213 | 1.15 | 0.89 | 38,109 | 37,011 |
| CONSERVATIVE | T240 | 3213/3213 | 1.43 | 1.96 | 55,292 | 52,863 |
| CONSERVATIVE | NEXT_FULL_SESSION | 3207/3213 | 4.04 | 4.40 | 88,103 | 81,706 |
| STANDARD | T60 | 2492/2492 | 2.13 | 1.06 | 29,774 | 28,764 |
| STANDARD | T240 | 2492/2492 | 3.77 | 2.06 | 42,798 | 40,744 |
| STANDARD | NEXT_FULL_SESSION | 2485/2492 | 5.18 | 2.92 | 68,406 | 65,218 |
| HIGH_RISK | T60 | 2738/2738 | 1.96 | 1.23 | 36,380 | 34,897 |
| HIGH_RISK | T240 | 2738/2738 | 3.09 | 1.49 | 51,560 | 49,712 |
| HIGH_RISK | NEXT_FULL_SESSION | 2732/2738 | 7.39 | 4.35 | 83,244 | 77,607 |

This panel excludes recorded risk-forced and internal portions. The complete table retains both and all source censors. Conditional standalone margin has a hypothetical replacement exit, frozen-mark short carry and standalone ticket difference. It neither reserves capital nor cancels other cohorts. Exact net preceding-cohort versus future-mark correlation is unavailable from the compacted archive. The separate raw-leg and saved-strength strata describe associations without replacing absent net allocations.

## Cost intensity

| Regime | External orders | Commission | Price concession | Impact | Borrow | Turnover | Account cost bps | Break-even bps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CONSERVATIVE | 7556 | 688 | 8,844 | 858 | 718 | 31,097,159 | 3.57 | -0.25 |

CONSERVATIVE same-holdings price-cost arithmetic at .5/1/1.5× gives -7,031/-11,882/-16,733 USD. Quantities, fees and carry stay fixed in this accounting sensitivity.
| STANDARD | 8071 | 847 | 10,761 | 1,060 | 620 | 37,990,356 | 3.50 | 0.20 |

STANDARD same-holdings price-cost arithmetic at .5/1/1.5× gives -6,627/-12,538/-18,448 USD. Quantities, fees and carry stay fixed in this accounting sensitivity.
| HIGH_RISK | 7881 | 865 | 11,120 | 1,130 | 687 | 39,152,459 | 3.53 | 0.59 |

HIGH_RISK same-holdings price-cost arithmetic at .5/1/1.5× gives -5,385/-11,510/-17,635 USD. Quantities, fees and carry stay fixed in this accounting sensitivity.

Risk labels may be whole-account spillovers. Their incidence and primary precedence cannot reconstruct missing per-order headroom. Strong or weak scores may have different stock, side and year mixes. All 2024 reference cutoffs, half-days, ordinary actions and unsupported special crossings stay visible in the common coverage table.

## Comparison and next hypothesis

R01 is a weekly six-minus-one-month momentum rank with concentrated long gains. This mechanism keeps its own cadence and cost mode. The unchanged V1/V2/V3 controls remain available, with different executed holds and book feedback. The companion findings appendix sets the proposal and its falsification rule.

## Findings and falsifiable next test

**REVISE_MECHANISM.** The entry fades a received opening gap, at 09:30
or 10:30 with later execution. It is not a continuation breakout. The
known prior close remains the resolution reference for that trade.
Conservative raw winners/losses were USD 120,314/−120,745 and net was
−USD 11,882. Shorts lost USD 10,145; longs lost USD 1,737. The successful
event-resolution group earned USD 91,246 net, while trailing-stop and
maximum groups lost USD 59,803 and USD 31,570. This is a failed-fade
tail problem with endogenous exit selection.

Nonforced external +240 raw was USD 2,428 and next-session USD 6,397;
conditional standalone values were USD 2,330/5,223. Yet the event-resolved
+240 subgroup showed only USD 150 raw across 1,633 legs. The larger
later opportunity belongs to other types of closure. Risk extensions
were negative at all three H85 horizons. Delaying all profitable gap
fills would be a poor reading of these facts. Original raw-cohort
reconstruction had a USD 13.48 residual and is explicitly unsupported
for exact individual-tail claims.

One future risk hypothesis is to initialize the trailing distance
at min(2×entry v20, absolute original log gap), anchored to the received
entry reference, without changing the favorable-extremum rule. Trigger
on a completed received observation, then fill prospectively. Keep
gap-fill resolution, existing mandatory risk and maximum intact. This
bounded stop may reduce failed-fade losses, while it could also cut
recovering fades before the observed next-session move. Test unchanged
H85 versus this one rule on a fixed untouched period. Falsify on worse
net per turnover or cost/exposure-normalized net, even if average loss
size falls. This does not endorse the previous post-exit oracle.
