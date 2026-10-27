# EVENT

UNTRAINED_REHEARSAL. No fitted controls or scientific results.

| role | model | arm | rows | origins | sessions | optimized_loss | prevalence | ANY_AP | ANY_AUC | ANY_Brier | ANY_log_loss | precision_at_half | recall_at_half |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | EVENT | 200 | 10 | 2 | 0.8333743 | 0.215 | 0.215 | 0.5 | 0.196 | 0.6843477 | nan | 0 |
| inner_validation | GLOBAL | EVENT | 160 | 8 | 2 | 1.012655 | 0.2642857 | 0.2642857 | 0.5 | 0.2403571 | 0.8294665 | nan | 0 |
| inner_train | STOCK | EVENT | 200 | 10 | 2 | 0.8333743 | 0.215 | 0.215 | 0.5 | 0.196 | 0.6843477 | nan | 0 |
| inner_validation | STOCK | EVENT | 160 | 8 | 2 | 1.012655 | 0.2642857 | 0.2642857 | 0.5 | 0.2403571 | 0.8294665 | nan | 0 |
| inner_train | VOL | EVENT | 200 | 10 | 2 | 0.8333743 | 0.215 | 0.215 | 0.5 | 0.196 | 0.6843477 | nan | 0 |
| inner_validation | VOL | EVENT | 160 | 8 | 2 | 1.012655 | 0.2642857 | 0.2642857 | 0.5 | 0.2403571 | 0.8294665 | nan | 0 |
| inner_train | NEURAL | EVENT | 200 | 10 | 2 | 1.082941 | 0.215 | 0.2176334 | 0.5342172 | 0.3636113 | 0.93116 | 0.215 | 1 |
| inner_validation | NEURAL | EVENT | 160 | 8 | 2 | 1.114808 | 0.2642857 | 0.5318071 | 0.725269 | 0.3548075 | 0.9130047 | 0.2642857 | 1 |
| refit | GLOBAL | EVENT | 200 | 10 | 2 | 0.8333743 | 0.215 | 0.215 | 0.5 | 0.196 | 0.6843477 | nan | 0 |
| oos | GLOBAL | EVENT | 100 | 5 | 2 | 0.4150519 | 0.1 | 0.1 | 0.5 | 0.0925 | 0.3457372 | nan | 0 |
| refit | STOCK | EVENT | 200 | 10 | 2 | 0.8333743 | 0.215 | 0.215 | 0.5 | 0.196 | 0.6843477 | nan | 0 |
| oos | STOCK | EVENT | 100 | 5 | 2 | 0.4150519 | 0.1 | 0.1 | 0.5 | 0.0925 | 0.3457372 | nan | 0 |
| refit | VOL | EVENT | 200 | 10 | 2 | 0.8333743 | 0.215 | 0.215 | 0.5 | 0.196 | 0.6843477 | nan | 0 |
| oos | VOL | EVENT | 100 | 5 | 2 | 0.4150519 | 0.1 | 0.1 | 0.5 | 0.0925 | 0.3457372 | nan | 0 |
| refit | NEURAL | EVENT | 200 | 10 | 2 | 1.082633 | 0.215 | 0.2175429 | 0.5336246 | 0.3634112 | 0.930722 | 0.215 | 1 |
| oos | NEURAL | EVENT | 100 | 5 | 2 | 1.05657 | 0.1 | 0.1108906 | 0.5073785 | 0.3890334 | 0.9817593 | 0.1 | 1 |


| role | reference | group | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | ALL | 0.2495665 | 0.2495665 | 0.2495665 | 2 | 1 |
| inner_validation | GLOBAL | ALL | 0.1021525 | 0.1021525 | 0.1021525 | 2 | 1 |
| inner_train | STOCK | ALL | 0.2495665 | 0.2495665 | 0.2495665 | 2 | 1 |
| inner_validation | STOCK | ALL | 0.1021525 | 0.1021525 | 0.1021525 | 2 | 1 |
| inner_train | VOL | ALL | 0.2495665 | 0.2495665 | 0.2495665 | 2 | 1 |
| inner_validation | VOL | ALL | 0.1021525 | 0.1021525 | 0.1021525 | 2 | 1 |
| refit | GLOBAL | ALL | 0.2492586 | 0.2492586 | 0.2492586 | 2 | 1 |
| oos | GLOBAL | ALL | 0.6415179 | 0.6415179 | 0.6415179 | 2 | 1 |
| refit | STOCK | ALL | 0.2492586 | 0.2492586 | 0.2492586 | 2 | 1 |
| oos | STOCK | ALL | 0.6415179 | 0.6415179 | 0.6415179 | 2 | 1 |
| refit | VOL | ALL | 0.2492586 | 0.2492586 | 0.2492586 | 2 | 1 |
| oos | VOL | ALL | 0.6415179 | 0.6415179 | 0.6415179 | 2 | 1 |


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
