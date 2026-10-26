# HF20-S4A-F23-H4-T2R-S42: complete diagnostic map

Exploratory price-only ranking; no executable P&L. Seven candidate origin slots, including conditional 09:32 opening issuance. OOS never selects epochs.

| role | origins | sessions | daily_ic | actual_objective | top4 | bottom4 | pair_concordance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | 13896 | 2547 | -0.002553446 | 1.424949 | 0.2285308 | 0.1916483 | 0.499079 |
| inner_validation | 453 | 86 | 0.04136186 | 1.396874 | 0.2405039 | 0.2313331 | 0.5148823 |
| refit | 14395 | 2640 | -0.00142101 | 1.424148 | 0.2288657 | 0.1924487 | 0.4994909 |
| oos | 887 | 187 | -0.01008385 | 1.387014 | 0.2354469 | 0.1783709 | 0.4951352 |


[Interactive run view](../plots/s4_a_rankings.html) — select the exact fold and objective. Rank trajectories, all20 heatmaps, M1, monthly/session IC, retrieval, score margins, movement, true objective tails, energy and training selector panels.

Each role has keyed scores, metrics, origin/slot/month tables, train-threshold tail cohorts, NUM/MAD intersections, original-Y and transformed-objective attribution, error-ranked complements, common/centered energy and source-quality strata. The role filename identifies inner training, inner validation, full-prefix refit or OOS.

Calibration/refit epoch JSON separates online dropout-ON from full-population OFF metrics. Batch and parameter-gradient CSVs retain preclip/postclip/update norms. Binding JSON identifies the selected checkpoint and fresh refit reload. NR ordinal MSE and T2R transformed MSE have different units.

All files for this run:

- [calibration_001.json](calibration_001.json)
- [calibration_001_batches.csv](calibration_001_batches.csv)
- [calibration_001_gradients.csv](calibration_001_gradients.csv)
- [calibration_binding.json](calibration_binding.json)
- [inner.pt](inner.pt)
- [inner_train_cohorts.csv](inner_train_cohorts.csv)
- [inner_train_energy_and_objective_cohorts.csv](inner_train_energy_and_objective_cohorts.csv)
- [inner_train_error_ranked_cohorts.csv](inner_train_error_ranked_cohorts.csv)
- [inner_train_metrics.json](inner_train_metrics.json)
- [inner_train_month.csv](inner_train_month.csv)
- [inner_train_origins.csv](inner_train_origins.csv)
- [inner_train_paired_cohort_difficulty.csv](inner_train_paired_cohort_difficulty.csv)
- [inner_train_scores.parquet](inner_train_scores.parquet)
- [inner_train_slot.csv](inner_train_slot.csv)
- [inner_train_stock_month_sector_quality.csv](inner_train_stock_month_sector_quality.csv)
- [inner_train_stock_quality.csv](inner_train_stock_quality.csv)
- [inner_train_thresholds.json](inner_train_thresholds.json)
- [inner_validation_cohorts.csv](inner_validation_cohorts.csv)
- [inner_validation_energy_and_objective_cohorts.csv](inner_validation_energy_and_objective_cohorts.csv)
- [inner_validation_error_ranked_cohorts.csv](inner_validation_error_ranked_cohorts.csv)
- [inner_validation_metrics.json](inner_validation_metrics.json)
- [inner_validation_month.csv](inner_validation_month.csv)
- [inner_validation_origins.csv](inner_validation_origins.csv)
- [inner_validation_paired_cohort_difficulty.csv](inner_validation_paired_cohort_difficulty.csv)
- [inner_validation_scores.parquet](inner_validation_scores.parquet)
- [inner_validation_slot.csv](inner_validation_slot.csv)
- [inner_validation_stock_month_sector_quality.csv](inner_validation_stock_month_sector_quality.csv)
- [inner_validation_stock_quality.csv](inner_validation_stock_quality.csv)
- [inner_validation_thresholds.json](inner_validation_thresholds.json)
- [oos_cohorts.csv](oos_cohorts.csv)
- [oos_energy_and_objective_cohorts.csv](oos_energy_and_objective_cohorts.csv)
- [oos_error_ranked_cohorts.csv](oos_error_ranked_cohorts.csv)
- [oos_metrics.json](oos_metrics.json)
- [oos_month.csv](oos_month.csv)
- [oos_origins.csv](oos_origins.csv)
- [oos_paired_cohort_difficulty.csv](oos_paired_cohort_difficulty.csv)
- [oos_scores.parquet](oos_scores.parquet)
- [oos_slot.csv](oos_slot.csv)
- [oos_stock_month_sector_quality.csv](oos_stock_month_sector_quality.csv)
- [oos_stock_quality.csv](oos_stock_quality.csv)
- [oos_thresholds.json](oos_thresholds.json)
- [refit.pt](refit.pt)
- [refit_001.json](refit_001.json)
- [refit_001_batches.csv](refit_001_batches.csv)
- [refit_001_gradients.csv](refit_001_gradients.csv)
- [refit_binding.json](refit_binding.json)
- [refit_cohorts.csv](refit_cohorts.csv)
- [refit_energy_and_objective_cohorts.csv](refit_energy_and_objective_cohorts.csv)
- [refit_error_ranked_cohorts.csv](refit_error_ranked_cohorts.csv)
- [refit_metrics.json](refit_metrics.json)
- [refit_month.csv](refit_month.csv)
- [refit_origins.csv](refit_origins.csv)
- [refit_paired_cohort_difficulty.csv](refit_paired_cohort_difficulty.csv)
- [refit_scores.parquet](refit_scores.parquet)
- [refit_slot.csv](refit_slot.csv)
- [refit_stock_month_sector_quality.csv](refit_stock_month_sector_quality.csv)
- [refit_stock_quality.csv](refit_stock_quality.csv)
- [refit_thresholds.json](refit_thresholds.json)
