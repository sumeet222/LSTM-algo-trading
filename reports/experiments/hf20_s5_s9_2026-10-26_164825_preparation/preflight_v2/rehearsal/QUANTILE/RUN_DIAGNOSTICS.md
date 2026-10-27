# QUANTILE

UNTRAINED_REHEARSAL. No fitted controls or scientific results.

| role | model | arm | rows | origins | sessions | optimized_loss | pinball_05 | pinball_50 | pinball_95 | coverage_05 | coverage_50 | coverage_95 | coverage90 | width_z | crossing_fraction | interval_score90_z | width_magnitude_rank_association |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | QUANTILE | 200 | 10 | 2 | 0.3020542 | 0.2178582 | 0.5116671 | 0.1766374 | 0.215 | 0.5 | 0.78 | 0.565 | 2 | 0 | 7.889911 | -4.615179e-16 |
| inner_validation | GLOBAL | QUANTILE | 160 | 8 | 2 | 0.2888271 | 0.1963099 | 0.492106 | 0.1780653 | 0.1857143 | 0.5 | 0.7464286 | 0.5607143 | 2 | 0 | 7.487504 | 4.618495e-16 |
| inner_train | STOCK | QUANTILE | 200 | 10 | 2 | 0.3020542 | 0.2178582 | 0.5116671 | 0.1766374 | 0.215 | 0.5 | 0.78 | 0.565 | 2 | 0 | 7.889911 | -4.615179e-16 |
| inner_validation | STOCK | QUANTILE | 160 | 8 | 2 | 0.2888271 | 0.1963099 | 0.492106 | 0.1780653 | 0.1857143 | 0.5 | 0.7464286 | 0.5607143 | 2 | 0 | 7.487504 | 4.618495e-16 |
| inner_train | VOL | QUANTILE | 200 | 10 | 2 | 0.2996625 | 0.2011694 | 0.5116671 | 0.186151 | 0.225 | 0.5 | 0.77 | 0.545 | 1.999031 | 0 | 7.746408 | 0.2867234 |
| inner_validation | VOL | QUANTILE | 160 | 8 | 2 | 0.2788809 | 0.1509665 | 0.492106 | 0.1935702 | 0.1535714 | 0.5 | 0.725 | 0.5714286 | 2.277368 | 0 | 6.890735 | 0.1709483 |
| inner_train | NEURAL | QUANTILE | 200 | 10 | 2 | 0.3597781 | 0.3020265 | 0.52276 | 0.254548 | 0.345 | 0.51 | 0.685 | 0.34 | 1.366248 | 0 | 11.13149 | 0.00736519 |
| inner_validation | NEURAL | QUANTILE | 160 | 8 | 2 | 0.3376949 | 0.2563669 | 0.4916443 | 0.2650736 | 0.2857143 | 0.5071429 | 0.6178571 | 0.3321429 | 1.363625 | 0 | 10.42881 | -0.0192637 |
| refit | GLOBAL | QUANTILE | 200 | 10 | 2 | 0.3016615 | 0.2175358 | 0.5111372 | 0.1763116 | 0.215 | 0.5 | 0.78 | 0.565 | 2 | 0 | 7.876949 | -4.615179e-16 |
| oos | GLOBAL | QUANTILE | 100 | 5 | 2 | 0.2285744 | 0.1303027 | 0.4395541 | 0.1158664 | 0.16875 | 0.5 | 0.75 | 0.58125 | 2 | 0 | 4.923382 | 6.711421e-16 |
| refit | STOCK | QUANTILE | 200 | 10 | 2 | 0.3016615 | 0.2175358 | 0.5111372 | 0.1763116 | 0.215 | 0.5 | 0.78 | 0.565 | 2 | 0 | 7.876949 | -4.615179e-16 |
| oos | STOCK | QUANTILE | 100 | 5 | 2 | 0.2285744 | 0.1303027 | 0.4395541 | 0.1158664 | 0.16875 | 0.5 | 0.75 | 0.58125 | 2 | 0 | 4.923382 | 6.711421e-16 |
| refit | VOL | QUANTILE | 200 | 10 | 2 | 0.2990803 | 0.2008974 | 0.5111372 | 0.1852061 | 0.225 | 0.5 | 0.77 | 0.545 | 1.998113 | 0 | 7.722071 | 0.2938802 |
| oos | VOL | QUANTILE | 100 | 5 | 2 | 0.2384432 | 0.1352221 | 0.4395541 | 0.1405532 | 0.18125 | 0.5 | 0.7125 | 0.53125 | 2.063224 | 0 | 5.515507 | 0.1176234 |
| refit | NEURAL | QUANTILE | 200 | 10 | 2 | 0.3592857 | 0.3009873 | 0.522171 | 0.2546989 | 0.345 | 0.505 | 0.685 | 0.34 | 1.365474 | 0 | 11.11372 | 0.009460744 |
| oos | NEURAL | QUANTILE | 100 | 5 | 2 | 0.2611748 | 0.1817632 | 0.4273965 | 0.1743647 | 0.31875 | 0.5125 | 0.65 | 0.33125 | 1.401639 | 0 | 7.122557 | 0.06953931 |


| role | reference | group | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | ALL | 0.05772391 | 0.05772391 | 0.05772391 | 2 | 1 |
| inner_validation | GLOBAL | ALL | 0.04886786 | 0.04886786 | 0.04886786 | 2 | 1 |
| inner_train | STOCK | ALL | 0.05772391 | 0.05772391 | 0.05772391 | 2 | 1 |
| inner_validation | STOCK | ALL | 0.04886786 | 0.04886786 | 0.04886786 | 2 | 1 |
| inner_train | VOL | ALL | 0.06011563 | 0.06011563 | 0.06011563 | 2 | 1 |
| inner_validation | VOL | ALL | 0.05881402 | 0.05881402 | 0.05881402 | 2 | 1 |
| refit | GLOBAL | ALL | 0.05762419 | 0.05762419 | 0.05762419 | 2 | 1 |
| oos | GLOBAL | ALL | 0.03260038 | 0.03260038 | 0.03260038 | 2 | 1 |
| refit | STOCK | ALL | 0.05762419 | 0.05762419 | 0.05762419 | 2 | 1 |
| oos | STOCK | ALL | 0.03260038 | 0.03260038 | 0.03260038 | 2 | 1 |
| refit | VOL | ALL | 0.06020548 | 0.06020548 | 0.06020548 | 2 | 1 |
| oos | VOL | ALL | 0.02273163 | 0.02273163 | 0.02273163 | 2 | 1 |


All diagnostic files:

- [calibration_001.json](calibration_001.json)
- [calibration_001_batches.csv](calibration_001_batches.csv)
- [calibration_001_gradients.csv](calibration_001_gradients.csv)
- [calibration_binding.json](calibration_binding.json)
- [inner_GLOBAL_control.json](inner_GLOBAL_control.json)
- [inner_STOCK_control.json](inner_STOCK_control.json)
- [inner_VOL_control.json](inner_VOL_control.json)
- [inner_target_recipe.json](inner_target_recipe.json)
- [inner_train_GLOBAL_control_scores.parquet](inner_train_GLOBAL_control_scores.parquet)
- [inner_train_STOCK_control_scores.parquet](inner_train_STOCK_control_scores.parquet)
- [inner_train_VOL_control_scores.parquet](inner_train_VOL_control_scores.parquet)
- [inner_train_cohorts.csv](inner_train_cohorts.csv)
- [inner_train_metrics.json](inner_train_metrics.json)
- [inner_train_scores.parquet](inner_train_scores.parquet)
- [inner_train_strata.csv](inner_train_strata.csv)
- [inner_validation_GLOBAL_control_scores.parquet](inner_validation_GLOBAL_control_scores.parquet)
- [inner_validation_STOCK_control_scores.parquet](inner_validation_STOCK_control_scores.parquet)
- [inner_validation_VOL_control_scores.parquet](inner_validation_VOL_control_scores.parquet)
- [inner_validation_cohorts.csv](inner_validation_cohorts.csv)
- [inner_validation_metrics.json](inner_validation_metrics.json)
- [inner_validation_scores.parquet](inner_validation_scores.parquet)
- [inner_validation_strata.csv](inner_validation_strata.csv)
- [inner_zero_step.pt](inner_zero_step.pt)
- [matched_baseline_differences.csv](matched_baseline_differences.csv)
- [model_and_control_metrics.csv](model_and_control_metrics.csv)
- [oos_GLOBAL_control_scores.parquet](oos_GLOBAL_control_scores.parquet)
- [oos_STOCK_control_scores.parquet](oos_STOCK_control_scores.parquet)
- [oos_VOL_control_scores.parquet](oos_VOL_control_scores.parquet)
- [oos_cohorts.csv](oos_cohorts.csv)
- [oos_metrics.json](oos_metrics.json)
- [oos_scores.parquet](oos_scores.parquet)
- [oos_strata.csv](oos_strata.csv)
- [refit_001.json](refit_001.json)
- [refit_001_batches.csv](refit_001_batches.csv)
- [refit_001_gradients.csv](refit_001_gradients.csv)
- [refit_GLOBAL_control.json](refit_GLOBAL_control.json)
- [refit_GLOBAL_control_scores.parquet](refit_GLOBAL_control_scores.parquet)
- [refit_STOCK_control.json](refit_STOCK_control.json)
- [refit_STOCK_control_scores.parquet](refit_STOCK_control_scores.parquet)
- [refit_VOL_control.json](refit_VOL_control.json)
- [refit_VOL_control_scores.parquet](refit_VOL_control_scores.parquet)
- [refit_binding.json](refit_binding.json)
- [refit_cohorts.csv](refit_cohorts.csv)
- [refit_metrics.json](refit_metrics.json)
- [refit_scores.parquet](refit_scores.parquet)
- [refit_strata.csv](refit_strata.csv)
- [refit_target_recipe.json](refit_target_recipe.json)
- [refit_zero_step.pt](refit_zero_step.pt)
