# Detailed training and extreme-value diagnostics

All64 role bundles reconcile TG20=NUM/(MAD+epsilon), actual weighted optimized loss, and target-top1/complement shares with atol1e-12/rtol1e-11. Every recorded optimizer batch changed weights; checkpoint reload error is0. No new fit or source read.

## Training, validation and fresh refit

| run | calibration_epochs | selected_epoch | raw_best_epoch | calibration_updates | refit_epochs | refit_updates | positive_update_batches | gradient_records | nonzero_gradient_records | clipping_fraction | max_postclip | reload_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HF20-S5-F21-H4-META-T2R-S42 | 13 | 3 | 3 | 1716 | 3 | 420 | 2136 | 12816 | 12816 | 0.0009363296 | 0.9999995 | 0 |
| HF20-S5-F22-H4-META-T2R-S42 | 12 | 1 | 1 | 1752 | 1 | 152 | 1904 | 11424 | 11424 | 0 | 0.4906041 | 0 |
| HF20-S5-F23-H4-META-T2R-S42 | 13 | 3 | 3 | 2080 | 3 | 495 | 2575 | 15450 | 15450 | 0 | 0.8123738 | 0 |
| HF20-S5-F24-H4-META-T2R-S42 | 12 | 2 | 2 | 2064 | 2 | 356 | 2420 | 14520 | 14520 | 0 | 0.6784814 | 0 |
| HF20-S9-F21-H4-MAG-S42 | 37 | 27 | 30 | 4884 | 27 | 3780 | 8664 | 51984 | 51984 | 0.00900277 | 0.9999997 | 0 |
| HF20-S9-F22-H4-MAG-S42 | 30 | 20 | 20 | 4380 | 20 | 3040 | 7420 | 44520 | 44520 | 0.01024259 | 0.9999996 | 0 |
| HF20-S9-F23-H4-MAG-S42 | 51 | 41 | 41 | 8160 | 41 | 6765 | 14925 | 89550 | 89550 | 0.005092127 | 0.9999997 | 0 |
| HF20-S9-F24-H4-MAG-S42 | 37 | 27 | 27 | 6364 | 27 | 4806 | 11170 | 67020 | 67020 | 0.006624888 | 0.9999996 | 0 |
| HF20-S9-F21-H4-EVENT-S42 | 14 | 4 | 4 | 1848 | 4 | 560 | 2408 | 14448 | 14448 | 0 | 0.9372929 | 0 |
| HF20-S9-F22-H4-EVENT-S42 | 37 | 27 | 27 | 5402 | 27 | 4104 | 9506 | 57036 | 57036 | 0 | 0.9287868 | 0 |
| HF20-S9-F23-H4-EVENT-S42 | 24 | 14 | 14 | 3840 | 14 | 2310 | 6150 | 36900 | 36900 | 0 | 0.8867179 | 0 |
| HF20-S9-F24-H4-EVENT-S42 | 12 | 2 | 2 | 2064 | 2 | 356 | 2420 | 14520 | 14520 | 0 | 0.8837944 | 0 |
| HF20-S9-F21-H4-QUANTILE-S42 | 14 | 4 | 4 | 1848 | 4 | 560 | 2408 | 14448 | 14448 | 0 | 0.09868327 | 0 |
| HF20-S9-F22-H4-QUANTILE-S42 | 22 | 12 | 15 | 3212 | 12 | 1824 | 5036 | 30216 | 30216 | 0 | 0.1003284 | 0 |
| HF20-S9-F23-H4-QUANTILE-S42 | 21 | 11 | 18 | 3360 | 11 | 1815 | 5175 | 31050 | 31050 | 0 | 0.1149559 | 0 |
| HF20-S9-F24-H4-QUANTILE-S42 | 19 | 9 | 9 | 3268 | 9 | 1602 | 4870 | 29220 | 29220 | 0 | 0.1287853 | 0 |


Online dropout-ON losses are training-path statistics, whereas epoch JSON records dropout-OFF full-prefix/validation losses for a fixed checkpoint. Raw-best and qualifying-selected epochs differ by the frozen improvement rule. Refit starts from the recorded same-seed initial state. See S5_S9_TRAINING_TRACE.csv and each run's immutable epoch/batch/gradient/checkpoint files in the complete index. Inner and refit recipes/scales differ; their numeric loss levels are not a controlled comparison.

## Actual optimized tail loss

S5: asinh-TG20 MSE. MAG: log1p(raw-|R|/scale) MSE. EVENT: natural three-class CE, not ANY Brier or TG20 MSE. QUANTILE: mean asinh-unit pinball. TRAIN_TASK95/99 use phase-training thresholds (raw|R| for MAG; |TG20| for the others). TARGET_TOP1 and ERROR_TOP1 are retrospective within-role diagnostic cohorts, not fitting thresholds. Their complements remain included.

NUM_ONLY/MAD_ONLY/BOTH/NEITHER use the frozen phase NUM95 and MAD05 thresholds. They are an attribution partition, not a causal explanation of predictability. FLOOR identifies epsilon-dominated denominators. POS/NEG are TG20 signs and can overlap the other cohort families. Never add overlapping shares.

| run | optimized_loss | TRAIN_TASK95_actual_loss_share | TRAIN_TASK99_actual_loss_share | NUM_ONLY_actual_loss_share | MAD_ONLY_actual_loss_share | BOTH_actual_loss_share | FLOOR_weight_mass | ERROR_TOP1_actual_loss_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HF20-S5-F21-H4-META-T2R-S42 | 1.302347 | 0.2004239 | 0.0386496 | 0.2286604 | 0.02704851 | 0 | 0 | 0.06686002 |
| HF20-S5-F22-H4-META-T2R-S42 | 1.348672 | 0.2242652 | 0.0566846 | 0.3017827 | 0.02149751 | 0.001459429 | 0 | 0.0675671 |
| HF20-S5-F23-H4-META-T2R-S42 | 1.322844 | 0.2234849 | 0.05828524 | 0.2125192 | 0.02170168 | 0.0004856715 | 0 | 0.07229962 |
| HF20-S5-F24-H4-META-T2R-S42 | 1.394347 | 0.2702821 | 0.07567887 | 0.247134 | 0.0341946 | 0.002060531 | 0 | 0.07482489 |
| HF20-S9-F21-H4-MAG-S42 | 0.2227765 | 0.2359997 | 0.04019922 | 0.2200965 | 0.01354178 | 0 | 0 | 0.08533143 |
| HF20-S9-F22-H4-MAG-S42 | 0.2792002 | 0.2823413 | 0.09089879 | 0.2095319 | 0.01308383 | 0.0002351062 | 0 | 0.07504 |
| HF20-S9-F23-H4-MAG-S42 | 0.2088575 | 0.2152381 | 0.07639579 | 0.2268745 | 0.01076564 | 0.0001672876 | 0 | 0.1058667 |
| HF20-S9-F24-H4-MAG-S42 | 0.2189824 | 0.2297948 | 0.0940834 | 0.2517672 | 0.02108959 | 0.0009886206 | 0 | 0.1132633 |
| HF20-S9-F21-H4-EVENT-S42 | 0.1804943 | 0.6744199 | 0.07509968 | 0.4605226 | 0.04216019 | 0 | 0 | 0.2436438 |
| HF20-S9-F22-H4-EVENT-S42 | 0.2101632 | 0.6177826 | 0.1011079 | 0.4725863 | 0.02448774 | 0.002145748 | 0 | 0.1843718 |
| HF20-S9-F23-H4-EVENT-S42 | 0.1941089 | 0.7670045 | 0.1214965 | 0.5003022 | 0.02285643 | 0.0003346467 | 0 | 0.2486183 |
| HF20-S9-F24-H4-EVENT-S42 | 0.223347 | 0.8133516 | 0.1410911 | 0.5422392 | 0.0399772 | 0.002657699 | 0 | 0.2226008 |
| HF20-S9-F21-H4-QUANTILE-S42 | 0.228354 | 0.108373 | 0.01916544 | 0.1327428 | 0.02515261 | 0 | 0 | 0.03545401 |
| HF20-S9-F22-H4-QUANTILE-S42 | 0.233462 | 0.1170327 | 0.02819295 | 0.1787586 | 0.02039756 | 0.0006946879 | 0 | 0.03450469 |
| HF20-S9-F23-H4-QUANTILE-S42 | 0.228439 | 0.1270258 | 0.03076039 | 0.1239799 | 0.02273084 | 0.0001996358 | 0 | 0.03956656 |
| HF20-S9-F24-H4-QUANTILE-S42 | 0.2325667 | 0.1550546 | 0.04044026 | 0.1466769 | 0.03410397 | 0.001023122 | 0 | 0.04175405 |


[All64 role/tail summaries](S5_S9_EXTREME_LOSS_SUMMARY.csv) · [Fixed-rule exact examples](S5_S9_FIXED_RULE_DIAGNOSTIC_EXAMPLES.csv) · [Full file index](S5_S9_DIAGNOSTIC_INDEX.md).

Examples choose the largest3 actual optimized row losses per run/role, ties by origin UTC/ticker. EVENT additionally selects highest-probability false alarms and lowest-probability missed tails at the existing frozen0.5 reporting threshold. An empty false-alarm set contributes no invented example; precision is undefined when there are no predicted positives. These retrospective examples never alter eligibility, training or primary metrics. Source/fallback/age/stock/month/clock strata and all individual observations remain in each saved role bundle.
Quantile miss cases select the largest lower/upper original-TG20 interval miss, with UTC/ticker ties. Volatility conditional tables reuse the already fitted EVENT inner/refit log-sigma quartile cuts for the same fold; no new cutoff fit or sample exclusion occurs. Conditional metrics renormalize existing role weights within each stratum. The quantile median's cross-sectional daily IC is secondary and separate from interval width.

## Observed equal-year OOS concentration

| Actual optimized objective | Training95th-tail observation mass | Loss share of that tail | Loss share of largest-error1% |
| --- | --- | --- | --- |
| S5 transformed MSE |4.63%|22.96%|7.04%|
| MAG transformed MSE |5.87%|24.08%|9.49%|
| EVENT natural3-class CE |4.63%|71.81%|22.48%|
| QUANTILE mean Z-pinball |4.63%|12.69%|3.78%|

These are concentration shares of different optimized objectives, not interchangeable loss levels. EVENT's tail concentration is expected to reflect rare-class log losses; it must not be labelled TG20 squared-error domination. No OOS row belongs to the epsilon-dominated denominator cohort. NUM_ONLY accounts for24.75%/22.71%/49.39%/14.55% of S5/MAG/EVENT/QUANTILE losses, while MAD_ONLY accounts for2.61%/1.46%/3.24%/2.56%; BOTH is reported separately. This does not certify a causal source mechanism. All complements remain in the evaluation.

[Volatility-conditional proper scores and coverage](S5_S9_VOLATILITY_CONDITIONAL_METRICS.csv) reuse already fitted EVENT prefix bins, with no new parameter fitting. [Quantile median rank diagnostic](S5_S9_QUANTILE_MEDIAN_RANK_DIAGNOSTIC.csv) is ancillary, separate from risk width. The main dashboard includes selected-trajectory magnitude scatter/residual, probability histograms, quantile misses/width and rolling coverage. These visible-ticker rolling windows are descriptive, not full-role weighted metrics or model inputs.
