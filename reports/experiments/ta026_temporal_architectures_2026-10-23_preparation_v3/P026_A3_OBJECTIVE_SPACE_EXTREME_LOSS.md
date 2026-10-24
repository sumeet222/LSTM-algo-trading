# P026 A3 actual-objective extreme loss

Saved refit checkpoint, dropout OFF; true equal-session/origin/stock z-MSE allocations. Ranked tails are observation percentages; range tails are fractions of fitting-prefix maxima. Disjoint numerator/MAD shares conserve total objective.

| cohort | threshold | rows | row_pct | origins | sessions | ordinary_weight_mass | objective_weight_mass | weighted_objective | unweighted_equivalent | weighted_loss_share_pct | unweighted_loss_share_pct | pointwise | pairwise | role |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | undefined | 104200 | 100 | 5210 | 2980 | 1 | 1 | 1.32751 | 138585 | 100 | 100 | 1.32751 | 0 | refit |
| TARGET_RANK_TOP1 | 7.26632 | 1042 | 1 | 930 | 742 | 0.00989094 | 0.00989094 | 0.0955955 | 10039.2 | 7.20112 | 7.24409 | 0.0955955 | 0 | refit |
| TARGET_RANK_TOP5 | 3.88616 | 5210 | 5 | 3192 | 2218 | 0.0495805 | 0.0495805 | 0.3247 | 34107.9 | 24.4593 | 24.6115 | 0.3247 | 0 | refit |
| BOTH_5 | undefined | 87 | 0.0834933 | 73 | 71 | 0.000855705 | 0.000855705 | 0.00979619 | 994.364 | 0.737938 | 0.717512 | 0.00979619 | 0 | refit |
| NUM_ONLY_5 | undefined | 5123 | 4.91651 | 2768 | 1872 | 0.0474161 | 0.0474161 | 0.260827 | 27936.4 | 19.6479 | 20.1583 | 0.260827 | 0 | refit |
| MAD_ONLY_5 | undefined | 5113 | 4.90691 | 260 | 245 | 0.0511577 | 0.0511577 | 0.0739352 | 7436.79 | 5.56948 | 5.36623 | 0.0739352 | 0 | refit |
| NEITHER_5 | undefined | 93877 | 90.0931 | 4950 | 2915 | 0.90057 | 0.90057 | 0.98295 | 102217 | 74.0447 | 73.7579 | 0.98295 | 0 | refit |
| RANGE_ABS_0.99 | 45.7387 | 1 | 0.000959693 | 1 | 1 | 1.67785e-05 | 1.67785e-05 | 0.000365327 | 21.7735 | 0.0275197 | 0.0157113 | 0.000365327 | 0 | refit |
| RANGE_ABS_0.95 | 43.8906 | 1 | 0.000959693 | 1 | 1 | 1.67785e-05 | 1.67785e-05 | 0.000365327 | 21.7735 | 0.0275197 | 0.0157113 | 0.000365327 | 0 | refit |


All four roles and complement/sign cohorts are in cohorts.parquet. Twenty-two source cases include five largest weighted losses each for AAPL, AMZN, TSLA, SBUX and distinct BOTH_5/MAD_ONLY_5. Each records52 genuine hourly candles, observed volume/quality,48×16 native/scaled/fallback values and all20 independent return operands. Private case stores remain local; source prices are not repaired or certified by these reports.
