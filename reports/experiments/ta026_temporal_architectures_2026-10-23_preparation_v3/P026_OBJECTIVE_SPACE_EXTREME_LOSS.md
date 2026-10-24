# P026 actual-objective extreme-loss closeout

All three saved refit models passed independent target, reload and objective checks. This report uses dropout-OFF z squared error with equal-session, equal-origin and equal20-stock weights. Historical online dropout-ON losses remain separate. All four roles, signs, complements, numerator/MAD1% and5% groups and side-specific range maxima are retained in each arm's private cohorts.parquet and the dashboard.

| cohort | threshold | rows | row_pct | origins | sessions |
|---|---|---|---|---|---|
| TARGET_RANK_TOP1 | 7.26632 | 1042 | 1 | 930 | 742 |
| TARGET_RANK_TOP5 | 3.88616 | 5210 | 5 | 3192 | 2218 |
| RANGE_ABS_0.99 | 45.7387 | 1 | 0.000959693 | 1 | 1 |
| RANGE_ABS_0.95 | 43.8906 | 1 | 0.000959693 | 1 | 1 |


These rank cutoffs are ordered observation groups with the frozen tie policy, while range cutoffs are fractions of the fitted maximum. Both absolute range groups contain one refit row. They must not be described as the top1%/5% of observations. Exact thresholds for other roles use their fitting-prefix versions and remain in thresholds.json/cohorts.parquet.

| arm | cohort | loss_share_pct | objective | rows | weight_mass | conditional_z_MSE |
|---|---|---|---|---|---|---|
| A1 | ALL | 100 | 1.32394 | 104200 | 1 | 1.32394 |
| A1 | TARGET_RANK_TOP1 | 7.1588 | 0.0947786 | 1042 | 0.00989094 | 9.58236 |
| A1 | TARGET_RANK_TOP5 | 24.3718 | 0.322668 | 5210 | 0.0495805 | 6.50797 |
| A1 | BOTH_5 | 0.732294 | 0.00969516 | 87 | 0.000855705 | 11.33 |
| A1 | NUM_ONLY_5 | 19.5399 | 0.258697 | 5123 | 0.0474161 | 5.4559 |
| A1 | MAD_ONLY_5 | 5.57556 | 0.0738174 | 5113 | 0.0511577 | 1.44294 |
| A1 | NEITHER_5 | 74.1522 | 0.981734 | 93877 | 0.90057 | 1.09012 |
| A1 | RANGE_ABS_0.99 | 0.0274523 | 0.000363453 | 1 | 1.67785e-05 | 21.6618 |
| A1 | RANGE_ABS_0.95 | 0.0274523 | 0.000363453 | 1 | 1.67785e-05 | 21.6618 |
| A2 | ALL | 100 | 1.3241 | 104200 | 1 | 1.3241 |
| A2 | TARGET_RANK_TOP1 | 7.17434 | 0.0949957 | 1042 | 0.00989094 | 9.60431 |
| A2 | TARGET_RANK_TOP5 | 24.3926 | 0.322983 | 5210 | 0.0495805 | 6.51431 |
| A2 | BOTH_5 | 0.72965 | 0.00966132 | 87 | 0.000855705 | 11.2905 |
| A2 | NUM_ONLY_5 | 19.5588 | 0.258979 | 5123 | 0.0474161 | 5.46184 |
| A2 | MAD_ONLY_5 | 5.57407 | 0.0738064 | 5113 | 0.0511577 | 1.44272 |
| A2 | NEITHER_5 | 74.1374 | 0.981655 | 93877 | 0.90057 | 1.09004 |
| A2 | RANGE_ABS_0.99 | 0.0275908 | 0.00036533 | 1 | 1.67785e-05 | 21.7737 |
| A2 | RANGE_ABS_0.95 | 0.0275908 | 0.00036533 | 1 | 1.67785e-05 | 21.7737 |
| A3 | ALL | 100 | 1.32751 | 104200 | 1 | 1.32751 |
| A3 | TARGET_RANK_TOP1 | 7.20112 | 0.0955955 | 1042 | 0.00989094 | 9.66495 |
| A3 | TARGET_RANK_TOP5 | 24.4593 | 0.3247 | 5210 | 0.0495805 | 6.54894 |
| A3 | BOTH_5 | 0.737938 | 0.00979619 | 87 | 0.000855705 | 11.4481 |
| A3 | NUM_ONLY_5 | 19.6479 | 0.260827 | 5123 | 0.0474161 | 5.50081 |
| A3 | MAD_ONLY_5 | 5.56948 | 0.0739352 | 5113 | 0.0511577 | 1.44524 |
| A3 | NEITHER_5 | 74.0447 | 0.98295 | 93877 | 0.90057 | 1.09147 |
| A3 | RANGE_ABS_0.99 | 0.0275197 | 0.000365327 | 1 | 1.67785e-05 | 21.7735 |
| A3 | RANGE_ABS_0.95 | 0.0275197 | 0.000365327 | 1 | 1.67785e-05 | 21.7735 |


The disjoint BOTH_5/NUM_ONLY_5/MAD_ONLY_5/NEITHER_5 totals conserve104,200 rows and the complete objective for each arm. The ranked top1% accounts for about7.16–7.20% of transformed loss, and top5% for24.37–24.46%; untransformed target extremes are damped by asinh, not removed. The single99%-of-range row contributes only about0.0275% of z-MSE. Objective contribution, conditional objective and overlapping marginal shares are distinct quantities.

Every arm has22 distinct source witnesses: five largest weighted fixed-checkpoint z losses each for AAPL/AMZN/TSLA/SBUX plus distinct BOTH_5 and MAD_ONLY_5. Total66 cases,3,432 genuine hourly candles,50,688 feature cells and1,320 independently reconstructed stock returns. Each52-hour panel includes48 inputs/four future labels, native/scaled features and masks, observed_volume_sum and volume_quality_tier; missing-minute volume is not certified zero. Cases and point-level records stay local/ignored. Use Exact Cases in the P026 explorer; no protected2026 rows are accessed.

[A1 report](P026_A1_OBJECTIVE_SPACE_EXTREME_LOSS.md), [A2 report](P026_A2_OBJECTIVE_SPACE_EXTREME_LOSS.md), [A3 report](P026_A3_OBJECTIVE_SPACE_EXTREME_LOSS.md). The three immutable gate inventories bind every private point-level file. postfit_analysis_summary.json, postfit_exact_population_counts.json and postfit_independent_audit_002.txt are the independent aggregate receipts. The accounting oracle retains the approved rtol3e-5/atol2e-6 point-loss and rtol5e-7/atol1e-8 population tolerances; no tolerance was loosened.
