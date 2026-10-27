# MAG

UNTRAINED_REHEARSAL. No fitted controls or scientific results.

| role | model | arm | rows | origins | sessions | optimized_loss | magnitude_MAE | magnitude_RMSE | negative_m_fraction | magnitude_rank_association |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | MAG | 200 | 10 | 2 | 0.4654232 | 0.009019905 | 0.0140337 | 0 | -9.614934e-19 |
| inner_validation | GLOBAL | MAG | 160 | 8 | 2 | 0.8344628 | 0.01461861 | 0.01994094 | 0 | 2.332734e-16 |
| inner_train | STOCK | MAG | 200 | 10 | 2 | 0.4654232 | 0.009019905 | 0.0140337 | 0 | -9.614934e-19 |
| inner_validation | STOCK | MAG | 160 | 8 | 2 | 0.8344628 | 0.01461861 | 0.01994094 | 0 | 2.332734e-16 |
| inner_train | VOL | MAG | 200 | 10 | 2 | 0.1573183 | 0.006113177 | 0.01064421 | 0 | 0.3622673 |
| inner_validation | VOL | MAG | 160 | 8 | 2 | 0.2007675 | 0.008745002 | 0.01335517 | 0 | 0.3986789 |
| inner_train | NEURAL | MAG | 200 | 10 | 2 | 0.5497941 | 0.008959929 | 0.01396739 | 0.855 | 0.1942782 |
| inner_validation | NEURAL | MAG | 160 | 8 | 2 | 0.9369851 | 0.01449019 | 0.01984007 | 0.7178571 | -0.02203312 |
| refit | GLOBAL | MAG | 200 | 10 | 2 | 0.4654232 | 0.009019905 | 0.0140337 | 0 | -9.614934e-19 |
| oos | GLOBAL | MAG | 100 | 5 | 2 | 0.8178586 | 0.0142331 | 0.01935201 | 0 | 6.6684e-16 |
| refit | STOCK | MAG | 200 | 10 | 2 | 0.4654232 | 0.009019905 | 0.0140337 | 0 | -9.614934e-19 |
| oos | STOCK | MAG | 100 | 5 | 2 | 0.8178586 | 0.0142331 | 0.01935201 | 0 | 6.6684e-16 |
| refit | VOL | MAG | 200 | 10 | 2 | 0.1563501 | 0.006102055 | 0.01062081 | 0 | 0.3636319 |
| oos | VOL | MAG | 100 | 5 | 2 | 0.2389292 | 0.009895344 | 0.01368218 | 0 | 0.3074021 |
| refit | NEURAL | MAG | 200 | 10 | 2 | 0.5515535 | 0.008959509 | 0.01396627 | 0.86 | 0.2014594 |
| oos | NEURAL | MAG | 100 | 5 | 2 | 0.9775752 | 0.01414785 | 0.01930808 | 0.8625 | 0.06460136 |


| role | reference | group | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | ALL | 0.0843709 | 0.0843709 | 0.0843709 | 2 | 1 |
| inner_validation | GLOBAL | ALL | 0.1025223 | 0.1025223 | 0.1025223 | 2 | 1 |
| inner_train | STOCK | ALL | 0.0843709 | 0.0843709 | 0.0843709 | 2 | 1 |
| inner_validation | STOCK | ALL | 0.1025223 | 0.1025223 | 0.1025223 | 2 | 1 |
| inner_train | VOL | ALL | 0.3924758 | 0.3924758 | 0.3924758 | 2 | 1 |
| inner_validation | VOL | ALL | 0.7362176 | 0.7362176 | 0.7362176 | 2 | 1 |
| refit | GLOBAL | ALL | 0.08613028 | 0.08613028 | 0.08613028 | 2 | 1 |
| oos | GLOBAL | ALL | 0.1597166 | 0.1597166 | 0.1597166 | 2 | 1 |
| refit | STOCK | ALL | 0.08613028 | 0.08613028 | 0.08613028 | 2 | 1 |
| oos | STOCK | ALL | 0.1597166 | 0.1597166 | 0.1597166 | 2 | 1 |
| refit | VOL | ALL | 0.3952035 | 0.3952035 | 0.3952035 | 2 | 1 |
| oos | VOL | ALL | 0.738646 | 0.738646 | 0.738646 | 2 | 1 |


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
