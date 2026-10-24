# P026 A2 actual-objective extreme loss

Saved refit checkpoint, dropout OFF; true equal-session/origin/stock z-MSE allocations. Ranked tails are observation percentages; range tails are fractions of fitting-prefix maxima. Disjoint numerator/MAD shares conserve total objective.

| cohort | threshold | rows | row_pct | origins | sessions | ordinary_weight_mass | objective_weight_mass | weighted_objective | unweighted_equivalent | weighted_loss_share_pct | unweighted_loss_share_pct | pointwise | pairwise | role |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | undefined | 104200 | 100 | 5210 | 2980 | 1 | 1 | 1.3241 | 138239 | 100 | 100 | 1.3241 | 0 | refit |
| TARGET_RANK_TOP1 | 7.26632 | 1042 | 1 | 930 | 742 | 0.00989094 | 0.00989094 | 0.0949957 | 9977.25 | 7.17434 | 7.2174 | 0.0949957 | 0 | refit |
| TARGET_RANK_TOP5 | 3.88616 | 5210 | 5 | 3192 | 2218 | 0.0495805 | 0.0495805 | 0.322983 | 33923.1 | 24.3926 | 24.5395 | 0.322983 | 0 | refit |
| BOTH_5 | undefined | 87 | 0.0834933 | 73 | 71 | 0.000855705 | 0.000855705 | 0.00966132 | 980.874 | 0.72965 | 0.70955 | 0.00966132 | 0 | refit |
| NUM_ONLY_5 | undefined | 5123 | 4.91651 | 2768 | 1872 | 0.0474161 | 0.0474161 | 0.258979 | 27741.9 | 19.5588 | 20.0681 | 0.258979 | 0 | refit |
| MAD_ONLY_5 | undefined | 5113 | 4.90691 | 260 | 245 | 0.0511577 | 0.0511577 | 0.0738064 | 7429.7 | 5.57407 | 5.37454 | 0.0738064 | 0 | refit |
| NEITHER_5 | undefined | 93877 | 90.0931 | 4950 | 2915 | 0.90057 | 0.90057 | 0.981655 | 102086 | 74.1374 | 73.8478 | 0.981655 | 0 | refit |
| RANGE_ABS_0.99 | 45.7387 | 1 | 0.000959693 | 1 | 1 | 1.67785e-05 | 1.67785e-05 | 0.00036533 | 21.7737 | 0.0275908 | 0.0157508 | 0.00036533 | 0 | refit |
| RANGE_ABS_0.95 | 43.8906 | 1 | 0.000959693 | 1 | 1 | 1.67785e-05 | 1.67785e-05 | 0.00036533 | 21.7737 | 0.0275908 | 0.0157508 | 0.00036533 | 0 | refit |


All four roles and complement/sign cohorts are in cohorts.parquet. Twenty-two source cases include five largest weighted losses each for AAPL, AMZN, TSLA, SBUX and distinct BOTH_5/MAD_ONLY_5. Each records52 genuine hourly candles, observed volume/quality,48×16 native/scaled/fallback values and all20 independent return operands. Private case stores remain local; source prices are not repaired or certified by these reports.
