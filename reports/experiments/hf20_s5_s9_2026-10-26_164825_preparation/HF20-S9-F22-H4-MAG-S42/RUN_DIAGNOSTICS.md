# HF20-S9-F22-H4-MAG-S42

TECHNICAL_PASS. All four roles verified; OOS remains exploratory.

| role | model | arm | rows | origins | sessions | optimized_loss | magnitude_MAE | magnitude_RMSE | negative_m_fraction | magnitude_rank_association | year |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | MAG | 254320 | 12716 | 2331 | 0.2875496 | 0.006760344 | 0.01199127 | 0 | 7.866881e-15 | 2022 |
| inner_validation | GLOBAL | MAG | 9140 | 457 | 92 | 0.2901282 | 0.00687374 | 0.01109159 | 0 | 5.178275e-16 | 2022 |
| inner_train | STOCK | MAG | 254320 | 12716 | 2331 | 0.2618808 | 0.006497862 | 0.01153177 | 0 | 0.2605182 | 2022 |
| inner_validation | STOCK | MAG | 9140 | 457 | 92 | 0.2637018 | 0.0066115 | 0.01059247 | 0 | 0.2594599 | 2022 |
| inner_train | VOL | MAG | 254320 | 12716 | 2331 | 0.246707 | 0.006380573 | 0.01075594 | 0 | 0.3541332 | 2022 |
| inner_validation | VOL | MAG | 9140 | 457 | 92 | 0.2647464 | 0.006687513 | 0.01019616 | 0 | 0.2911967 | 2022 |
| inner_train | NEURAL | MAG | 254320 | 12716 | 2331 | 0.2159519 | 0.00597335 | 0.01031264 | 0 | 0.4507765 | 2022 |
| inner_validation | NEURAL | MAG | 9140 | 457 | 92 | 0.2229356 | 0.006134352 | 0.009822001 | 0 | 0.4581664 | 2022 |
| refit | GLOBAL | MAG | 263460 | 13173 | 2423 | 0.28673 | 0.006767067 | 0.01195433 | 0 | 1.124717e-15 | 2022 |
| oos | GLOBAL | MAG | 23600 | 1180 | 210 | 0.3805561 | 0.00901884 | 0.01477084 | 0 | 2.921709e-16 | 2022 |
| refit | STOCK | MAG | 263460 | 13173 | 2423 | 0.2611009 | 0.006504105 | 0.01149289 | 0 | 0.260438 | 2022 |
| oos | STOCK | MAG | 23600 | 1180 | 210 | 0.3487978 | 0.00873589 | 0.01422331 | 0 | 0.2742463 | 2022 |
| refit | VOL | MAG | 263460 | 13173 | 2423 | 0.2465541 | 0.006392167 | 0.01073481 | 0 | 0.3526881 | 2022 |
| oos | VOL | MAG | 23600 | 1180 | 210 | 0.3187141 | 0.008597898 | 0.01285998 | 0 | 0.2983213 | 2022 |
| refit | NEURAL | MAG | 263460 | 13173 | 2423 | 0.2146971 | 0.005967295 | 0.01030818 | 0 | 0.4528363 | 2022 |
| oos | NEURAL | MAG | 23600 | 1180 | 210 | 0.2792002 | 0.008070806 | 0.01242675 | 0 | 0.4193015 | 2022 |


| role | reference | group | metric | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | ALL | proper_loss | -0.07159772 | -0.08507635 | -0.06120513 | 2331 | 118 |
| inner_train | GLOBAL | ALL | magnitude_MAE | -0.0007869949 | -0.0009030675 | -0.0006956905 | 2331 | 118 |
| inner_train | GLOBAL | ALL | magnitude_MSE | -3.744011e-05 | -5.210908e-05 | -2.593052e-05 | 2331 | 118 |
| inner_validation | GLOBAL | ALL | proper_loss | -0.0671926 | -0.08561188 | -0.04515793 | 92 | 6 |
| inner_validation | GLOBAL | ALL | magnitude_MAE | -0.0007393878 | -0.00092708 | -0.00052091 | 92 | 6 |
| inner_validation | GLOBAL | ALL | magnitude_MSE | -2.655173e-05 | -3.750317e-05 | -1.395893e-05 | 92 | 6 |
| inner_train | STOCK | ALL | proper_loss | -0.04592894 | -0.0588594 | -0.03553873 | 2331 | 118 |
| inner_train | STOCK | ALL | magnitude_MAE | -0.0005245127 | -0.0006386948 | -0.0004350426 | 2331 | 118 |
| inner_train | STOCK | ALL | magnitude_MSE | -2.663116e-05 | -4.117852e-05 | -1.584921e-05 | 2331 | 118 |
| inner_validation | STOCK | ALL | proper_loss | -0.04076626 | -0.05137301 | -0.02915454 | 92 | 6 |
| inner_validation | STOCK | ALL | magnitude_MAE | -0.0004771484 | -0.0006049759 | -0.0003546834 | 92 | 6 |
| inner_validation | STOCK | ALL | magnitude_MSE | -1.572867e-05 | -2.290933e-05 | -7.057586e-06 | 92 | 6 |
| inner_train | VOL | ALL | proper_loss | -0.03075517 | -0.0335612 | -0.02858811 | 2331 | 118 |
| inner_train | VOL | ALL | magnitude_MAE | -0.0004072231 | -0.0004455015 | -0.0003765757 | 2331 | 118 |
| inner_train | VOL | ALL | magnitude_MSE | -9.339694e-06 | -1.10809e-05 | -7.647137e-06 | 2331 | 118 |
| inner_validation | VOL | ALL | proper_loss | -0.04181086 | -0.05646231 | -0.02973078 | 92 | 6 |
| inner_validation | VOL | ALL | magnitude_MAE | -0.0005531611 | -0.0008098584 | -0.0003504505 | 92 | 6 |
| inner_validation | VOL | ALL | magnitude_MSE | -7.489944e-06 | -1.06447e-05 | -4.614156e-06 | 92 | 6 |
| refit | GLOBAL | ALL | proper_loss | -0.07203297 | -0.08562956 | -0.06171163 | 2423 | 124 |
| refit | GLOBAL | ALL | magnitude_MAE | -0.0007997722 | -0.0009218616 | -0.0007074299 | 2423 | 124 |
| refit | GLOBAL | ALL | magnitude_MSE | -3.664758e-05 | -5.355772e-05 | -2.620809e-05 | 2423 | 124 |
| oos | GLOBAL | ALL | proper_loss | -0.1013559 | -0.1209294 | -0.07816443 | 210 | 12 |
| oos | GLOBAL | ALL | magnitude_MAE | -0.0009480336 | -0.001166084 | -0.000743598 | 210 | 12 |
| oos | GLOBAL | ALL | magnitude_MSE | -6.375361e-05 | -7.911498e-05 | -4.750031e-05 | 210 | 12 |
| refit | STOCK | ALL | proper_loss | -0.0464038 | -0.05977824 | -0.03643 | 2423 | 124 |
| refit | STOCK | ALL | magnitude_MAE | -0.0005368108 | -0.0006592032 | -0.0004455498 | 2423 | 124 |
| refit | STOCK | ALL | magnitude_MSE | -2.58281e-05 | -4.14019e-05 | -1.582926e-05 | 2423 | 124 |
| oos | STOCK | ALL | proper_loss | -0.06959752 | -0.08849941 | -0.04829044 | 210 | 12 |
| oos | STOCK | ALL | magnitude_MAE | -0.0006650839 | -0.0008621411 | -0.0004597714 | 210 | 12 |
| oos | STOCK | ALL | magnitude_MSE | -4.787855e-05 | -6.143995e-05 | -3.350866e-05 | 210 | 12 |
| refit | VOL | ALL | proper_loss | -0.03185702 | -0.03485567 | -0.02953779 | 2423 | 124 |
| refit | VOL | ALL | magnitude_MAE | -0.0004248726 | -0.0004651683 | -0.0003900681 | 2423 | 124 |
| refit | VOL | ALL | magnitude_MSE | -8.97756e-06 | -1.085263e-05 | -7.57954e-06 | 2423 | 124 |
| oos | VOL | ALL | proper_loss | -0.03951383 | -0.04960762 | -0.0302805 | 210 | 12 |
| oos | VOL | ALL | magnitude_MAE | -0.0005270919 | -0.0006586673 | -0.0004089531 | 210 | 12 |
| oos | VOL | ALL | magnitude_MSE | -1.095512e-05 | -1.337626e-05 | -8.402636e-06 | 210 | 12 |


All diagnostic files:

- [calibration_001.json](calibration_001.json)
- [calibration_001.pt](calibration_001.pt)
- [calibration_001_batches.csv](calibration_001_batches.csv)
- [calibration_001_gradients.csv](calibration_001_gradients.csv)
- [calibration_002.json](calibration_002.json)
- [calibration_002.pt](calibration_002.pt)
- [calibration_002_batches.csv](calibration_002_batches.csv)
- [calibration_002_gradients.csv](calibration_002_gradients.csv)
- [calibration_003.json](calibration_003.json)
- [calibration_003.pt](calibration_003.pt)
- [calibration_003_batches.csv](calibration_003_batches.csv)
- [calibration_003_gradients.csv](calibration_003_gradients.csv)
- [calibration_004.json](calibration_004.json)
- [calibration_004.pt](calibration_004.pt)
- [calibration_004_batches.csv](calibration_004_batches.csv)
- [calibration_004_gradients.csv](calibration_004_gradients.csv)
- [calibration_005.json](calibration_005.json)
- [calibration_005.pt](calibration_005.pt)
- [calibration_005_batches.csv](calibration_005_batches.csv)
- [calibration_005_gradients.csv](calibration_005_gradients.csv)
- [calibration_006.json](calibration_006.json)
- [calibration_006.pt](calibration_006.pt)
- [calibration_006_batches.csv](calibration_006_batches.csv)
- [calibration_006_gradients.csv](calibration_006_gradients.csv)
- [calibration_007.json](calibration_007.json)
- [calibration_007.pt](calibration_007.pt)
- [calibration_007_batches.csv](calibration_007_batches.csv)
- [calibration_007_gradients.csv](calibration_007_gradients.csv)
- [calibration_008.json](calibration_008.json)
- [calibration_008.pt](calibration_008.pt)
- [calibration_008_batches.csv](calibration_008_batches.csv)
- [calibration_008_gradients.csv](calibration_008_gradients.csv)
- [calibration_009.json](calibration_009.json)
- [calibration_009.pt](calibration_009.pt)
- [calibration_009_batches.csv](calibration_009_batches.csv)
- [calibration_009_gradients.csv](calibration_009_gradients.csv)
- [calibration_010.json](calibration_010.json)
- [calibration_010.pt](calibration_010.pt)
- [calibration_010_batches.csv](calibration_010_batches.csv)
- [calibration_010_gradients.csv](calibration_010_gradients.csv)
- [calibration_011.json](calibration_011.json)
- [calibration_011.pt](calibration_011.pt)
- [calibration_011_batches.csv](calibration_011_batches.csv)
- [calibration_011_gradients.csv](calibration_011_gradients.csv)
- [calibration_012.json](calibration_012.json)
- [calibration_012.pt](calibration_012.pt)
- [calibration_012_batches.csv](calibration_012_batches.csv)
- [calibration_012_gradients.csv](calibration_012_gradients.csv)
- [calibration_013.json](calibration_013.json)
- [calibration_013.pt](calibration_013.pt)
- [calibration_013_batches.csv](calibration_013_batches.csv)
- [calibration_013_gradients.csv](calibration_013_gradients.csv)
- [calibration_014.json](calibration_014.json)
- [calibration_014.pt](calibration_014.pt)
- [calibration_014_batches.csv](calibration_014_batches.csv)
- [calibration_014_gradients.csv](calibration_014_gradients.csv)
- [calibration_015.json](calibration_015.json)
- [calibration_015.pt](calibration_015.pt)
- [calibration_015_batches.csv](calibration_015_batches.csv)
- [calibration_015_gradients.csv](calibration_015_gradients.csv)
- [calibration_016.json](calibration_016.json)
- [calibration_016.pt](calibration_016.pt)
- [calibration_016_batches.csv](calibration_016_batches.csv)
- [calibration_016_gradients.csv](calibration_016_gradients.csv)
- [calibration_017.json](calibration_017.json)
- [calibration_017.pt](calibration_017.pt)
- [calibration_017_batches.csv](calibration_017_batches.csv)
- [calibration_017_gradients.csv](calibration_017_gradients.csv)
- [calibration_018.json](calibration_018.json)
- [calibration_018.pt](calibration_018.pt)
- [calibration_018_batches.csv](calibration_018_batches.csv)
- [calibration_018_gradients.csv](calibration_018_gradients.csv)
- [calibration_019.json](calibration_019.json)
- [calibration_019.pt](calibration_019.pt)
- [calibration_019_batches.csv](calibration_019_batches.csv)
- [calibration_019_gradients.csv](calibration_019_gradients.csv)
- [calibration_020.json](calibration_020.json)
- [calibration_020.pt](calibration_020.pt)
- [calibration_020_batches.csv](calibration_020_batches.csv)
- [calibration_020_gradients.csv](calibration_020_gradients.csv)
- [calibration_021.json](calibration_021.json)
- [calibration_021.pt](calibration_021.pt)
- [calibration_021_batches.csv](calibration_021_batches.csv)
- [calibration_021_gradients.csv](calibration_021_gradients.csv)
- [calibration_022.json](calibration_022.json)
- [calibration_022.pt](calibration_022.pt)
- [calibration_022_batches.csv](calibration_022_batches.csv)
- [calibration_022_gradients.csv](calibration_022_gradients.csv)
- [calibration_023.json](calibration_023.json)
- [calibration_023.pt](calibration_023.pt)
- [calibration_023_batches.csv](calibration_023_batches.csv)
- [calibration_023_gradients.csv](calibration_023_gradients.csv)
- [calibration_024.json](calibration_024.json)
- [calibration_024.pt](calibration_024.pt)
- [calibration_024_batches.csv](calibration_024_batches.csv)
- [calibration_024_gradients.csv](calibration_024_gradients.csv)
- [calibration_025.json](calibration_025.json)
- [calibration_025.pt](calibration_025.pt)
- [calibration_025_batches.csv](calibration_025_batches.csv)
- [calibration_025_gradients.csv](calibration_025_gradients.csv)
- [calibration_026.json](calibration_026.json)
- [calibration_026.pt](calibration_026.pt)
- [calibration_026_batches.csv](calibration_026_batches.csv)
- [calibration_026_gradients.csv](calibration_026_gradients.csv)
- [calibration_027.json](calibration_027.json)
- [calibration_027.pt](calibration_027.pt)
- [calibration_027_batches.csv](calibration_027_batches.csv)
- [calibration_027_gradients.csv](calibration_027_gradients.csv)
- [calibration_028.json](calibration_028.json)
- [calibration_028.pt](calibration_028.pt)
- [calibration_028_batches.csv](calibration_028_batches.csv)
- [calibration_028_gradients.csv](calibration_028_gradients.csv)
- [calibration_029.json](calibration_029.json)
- [calibration_029.pt](calibration_029.pt)
- [calibration_029_batches.csv](calibration_029_batches.csv)
- [calibration_029_gradients.csv](calibration_029_gradients.csv)
- [calibration_030.json](calibration_030.json)
- [calibration_030.pt](calibration_030.pt)
- [calibration_030_batches.csv](calibration_030_batches.csv)
- [calibration_030_gradients.csv](calibration_030_gradients.csv)
- [calibration_binding.json](calibration_binding.json)
- [calibration_stop_optimizer.pt](calibration_stop_optimizer.pt)
- [configuration.json](configuration.json)
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
- [refit_002.json](refit_002.json)
- [refit_002_batches.csv](refit_002_batches.csv)
- [refit_002_gradients.csv](refit_002_gradients.csv)
- [refit_003.json](refit_003.json)
- [refit_003_batches.csv](refit_003_batches.csv)
- [refit_003_gradients.csv](refit_003_gradients.csv)
- [refit_004.json](refit_004.json)
- [refit_004_batches.csv](refit_004_batches.csv)
- [refit_004_gradients.csv](refit_004_gradients.csv)
- [refit_005.json](refit_005.json)
- [refit_005_batches.csv](refit_005_batches.csv)
- [refit_005_gradients.csv](refit_005_gradients.csv)
- [refit_006.json](refit_006.json)
- [refit_006_batches.csv](refit_006_batches.csv)
- [refit_006_gradients.csv](refit_006_gradients.csv)
- [refit_007.json](refit_007.json)
- [refit_007_batches.csv](refit_007_batches.csv)
- [refit_007_gradients.csv](refit_007_gradients.csv)
- [refit_008.json](refit_008.json)
- [refit_008_batches.csv](refit_008_batches.csv)
- [refit_008_gradients.csv](refit_008_gradients.csv)
- [refit_009.json](refit_009.json)
- [refit_009_batches.csv](refit_009_batches.csv)
- [refit_009_gradients.csv](refit_009_gradients.csv)
- [refit_010.json](refit_010.json)
- [refit_010_batches.csv](refit_010_batches.csv)
- [refit_010_gradients.csv](refit_010_gradients.csv)
- [refit_011.json](refit_011.json)
- [refit_011_batches.csv](refit_011_batches.csv)
- [refit_011_gradients.csv](refit_011_gradients.csv)
- [refit_012.json](refit_012.json)
- [refit_012_batches.csv](refit_012_batches.csv)
- [refit_012_gradients.csv](refit_012_gradients.csv)
- [refit_013.json](refit_013.json)
- [refit_013_batches.csv](refit_013_batches.csv)
- [refit_013_gradients.csv](refit_013_gradients.csv)
- [refit_014.json](refit_014.json)
- [refit_014_batches.csv](refit_014_batches.csv)
- [refit_014_gradients.csv](refit_014_gradients.csv)
- [refit_015.json](refit_015.json)
- [refit_015_batches.csv](refit_015_batches.csv)
- [refit_015_gradients.csv](refit_015_gradients.csv)
- [refit_016.json](refit_016.json)
- [refit_016_batches.csv](refit_016_batches.csv)
- [refit_016_gradients.csv](refit_016_gradients.csv)
- [refit_017.json](refit_017.json)
- [refit_017_batches.csv](refit_017_batches.csv)
- [refit_017_gradients.csv](refit_017_gradients.csv)
- [refit_018.json](refit_018.json)
- [refit_018_batches.csv](refit_018_batches.csv)
- [refit_018_gradients.csv](refit_018_gradients.csv)
- [refit_019.json](refit_019.json)
- [refit_019_batches.csv](refit_019_batches.csv)
- [refit_019_gradients.csv](refit_019_gradients.csv)
- [refit_020.json](refit_020.json)
- [refit_020_batches.csv](refit_020_batches.csv)
- [refit_020_gradients.csv](refit_020_gradients.csv)
- [refit_GLOBAL_control.json](refit_GLOBAL_control.json)
- [refit_GLOBAL_control_scores.parquet](refit_GLOBAL_control_scores.parquet)
- [refit_STOCK_control.json](refit_STOCK_control.json)
- [refit_STOCK_control_scores.parquet](refit_STOCK_control_scores.parquet)
- [refit_VOL_control.json](refit_VOL_control.json)
- [refit_VOL_control_scores.parquet](refit_VOL_control_scores.parquet)
- [refit_binding.json](refit_binding.json)
- [refit_cohorts.csv](refit_cohorts.csv)
- [refit_final.pt](refit_final.pt)
- [refit_metrics.json](refit_metrics.json)
- [refit_scores.parquet](refit_scores.parquet)
- [refit_strata.csv](refit_strata.csv)
- [refit_target_recipe.json](refit_target_recipe.json)
