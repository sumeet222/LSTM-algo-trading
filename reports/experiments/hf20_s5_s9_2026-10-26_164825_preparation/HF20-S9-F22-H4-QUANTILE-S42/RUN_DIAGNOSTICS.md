# HF20-S9-F22-H4-QUANTILE-S42

TECHNICAL_PASS. All four roles verified; OOS remains exploratory.

| role | model | arm | rows | origins | sessions | optimized_loss | pinball_05 | pinball_50 | pinball_95 | coverage_05 | coverage_50 | coverage_95 | coverage90 | width_z | crossing_fraction | interval_score90_z | width_magnitude_rank_association | year |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | QUANTILE | 254320 | 12716 | 2331 | 0.2359128 | 0.1141051 | 0.4768904 | 0.1167427 | 0.05000291 | 0.5000717 | 0.9500022 | 0.9000036 | 3.737285 | 0 | 4.616957 | 1.026064e-15 | 2022 |
| inner_validation | GLOBAL | QUANTILE | 9140 | 457 | 92 | 0.2335795 | 0.1113727 | 0.4754895 | 0.1138763 | 0.04922748 | 0.5 | 0.955977 | 0.9067495 | 3.737285 | 0 | 4.504979 | 1.032954e-16 | 2022 |
| inner_train | STOCK | QUANTILE | 254320 | 12716 | 2331 | 0.2307077 | 0.1071896 | 0.4767067 | 0.1082267 | 0.05002972 | 0.5000491 | 0.9500521 | 0.9000901 | 3.603749 | 0 | 4.308326 | 0.2477171 | 2022 |
| inner_validation | STOCK | QUANTILE | 9140 | 457 | 92 | 0.2292744 | 0.1065225 | 0.4757238 | 0.105577 | 0.05041537 | 0.5009705 | 0.9539182 | 0.9035028 | 3.603749 | 0 | 4.241989 | 0.229439 | 2022 |
| inner_train | VOL | QUANTILE | 254320 | 12716 | 2331 | 0.2378266 | 0.1177959 | 0.4768904 | 0.1187934 | 0.04999745 | 0.5000717 | 0.9500025 | 0.900005 | 4.001273 | 0 | 4.731786 | 0.2649731 | 2022 |
| inner_validation | VOL | QUANTILE | 9140 | 457 | 92 | 0.2359767 | 0.1175984 | 0.4754895 | 0.1148423 | 0.06775621 | 0.5 | 0.9391434 | 0.8713872 | 3.738105 | 0 | 4.648814 | 0.2431881 | 2022 |
| inner_train | NEURAL | QUANTILE | 254320 | 12716 | 2331 | 0.2304508 | 0.1069293 | 0.4764872 | 0.1079359 | 0.04966972 | 0.4997292 | 0.9500319 | 0.9003622 | 3.602102 | 0 | 4.297303 | 0.2674517 | 2022 |
| inner_validation | NEURAL | QUANTILE | 9140 | 457 | 92 | 0.2285671 | 0.1050794 | 0.4754365 | 0.1051855 | 0.04633929 | 0.4984045 | 0.9599754 | 0.9136361 | 3.651239 | 0 | 4.205297 | 0.2650364 | 2022 |
| refit | GLOBAL | QUANTILE | 263460 | 13173 | 2423 | 0.235771 | 0.1139807 | 0.4767199 | 0.1166125 | 0.05000334 | 0.5000689 | 0.9500024 | 0.9000031 | 3.73392 | 0 | 4.611865 | -1.582791e-15 | 2022 |
| oos | GLOBAL | QUANTILE | 23600 | 1180 | 210 | 0.2349944 | 0.113428 | 0.4796666 | 0.1118885 | 0.0511644 | 0.5000737 | 0.9549104 | 0.903746 | 3.73392 | 0 | 4.50633 | 5.44044e-16 | 2022 |
| refit | STOCK | QUANTILE | 263460 | 13173 | 2423 | 0.2305973 | 0.1071395 | 0.476549 | 0.1081032 | 0.05002855 | 0.5000466 | 0.9500484 | 0.9001004 | 3.600079 | 0 | 4.304855 | 0.2467433 | 2022 |
| oos | STOCK | QUANTILE | 23600 | 1180 | 210 | 0.232049 | 0.1076449 | 0.4802299 | 0.1082722 | 0.05354705 | 0.5011111 | 0.9488277 | 0.8952806 | 3.600079 | 0 | 4.318342 | 0.1827542 | 2022 |
| refit | VOL | QUANTILE | 263460 | 13173 | 2423 | 0.2377415 | 0.1178488 | 0.4767199 | 0.1186559 | 0.0499972 | 0.5000689 | 0.9499979 | 0.9000007 | 4.001709 | 0 | 4.730093 | 0.2642215 | 2022 |
| oos | VOL | QUANTILE | 23600 | 1180 | 210 | 0.237874 | 0.1168364 | 0.4796666 | 0.1171189 | 0.05711395 | 0.5000737 | 0.9441134 | 0.8869994 | 3.873666 | 0 | 4.679107 | 0.2389627 | 2022 |
| refit | NEURAL | QUANTILE | 263460 | 13173 | 2423 | 0.2303225 | 0.1067957 | 0.4763468 | 0.107825 | 0.04844452 | 0.4997356 | 0.9505382 | 0.9020937 | 3.612128 | 0 | 4.292414 | 0.2676441 | 2022 |
| oos | NEURAL | QUANTILE | 23600 | 1180 | 210 | 0.233462 | 0.1100735 | 0.4796798 | 0.1106328 | 0.02911621 | 0.497191 | 0.9746497 | 0.9455334 | 4.077221 | 0 | 4.414125 | 0.2258268 | 2022 |


| role | reference | group | metric | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | ALL | proper_loss | -0.005461969 | -0.005987321 | -0.004911533 | 2331 | 118 |
| inner_train | GLOBAL | ALL | pinball_05 | -0.007175877 | -0.007990105 | -0.006417765 | 2331 | 118 |
| inner_train | GLOBAL | ALL | pinball_50 | -0.0004032075 | -0.0005367063 | -0.0002892701 | 2331 | 118 |
| inner_train | GLOBAL | ALL | pinball_95 | -0.008806822 | -0.009967051 | -0.007722985 | 2331 | 118 |
| inner_validation | GLOBAL | ALL | proper_loss | -0.005012359 | -0.00628897 | -0.003666879 | 92 | 6 |
| inner_validation | GLOBAL | ALL | pinball_05 | -0.006293325 | -0.00939212 | -0.002029396 | 92 | 6 |
| inner_validation | GLOBAL | ALL | pinball_50 | -5.297922e-05 | -0.000521011 | 0.000438279 | 92 | 6 |
| inner_validation | GLOBAL | ALL | pinball_95 | -0.008690772 | -0.01290082 | -0.005183122 | 92 | 6 |
| inner_train | STOCK | ALL | proper_loss | -0.0002568849 | -0.0006038374 | 6.182651e-05 | 2331 | 118 |
| inner_train | STOCK | ALL | pinball_05 | -0.0002603599 | -0.0008042932 | 0.0003064897 | 2331 | 118 |
| inner_train | STOCK | ALL | pinball_50 | -0.0002195045 | -0.0004129147 | -2.644996e-05 | 2331 | 118 |
| inner_train | STOCK | ALL | pinball_95 | -0.0002907902 | -0.0008511948 | 0.0002952277 | 2331 | 118 |
| inner_validation | STOCK | ALL | proper_loss | -0.0007072778 | -0.001870171 | 0.0007607121 | 92 | 6 |
| inner_validation | STOCK | ALL | pinball_05 | -0.001443113 | -0.003195402 | 0.001072312 | 92 | 6 |
| inner_validation | STOCK | ALL | pinball_50 | -0.0002872381 | -0.0006626356 | 0.0001898075 | 92 | 6 |
| inner_validation | STOCK | ALL | pinball_95 | -0.0003914821 | -0.00267814 | 0.001521913 | 92 | 6 |
| inner_train | VOL | ALL | proper_loss | -0.007375792 | -0.008036607 | -0.00675351 | 2331 | 118 |
| inner_train | VOL | ALL | pinball_05 | -0.01086664 | -0.01198987 | -0.009853617 | 2331 | 118 |
| inner_train | VOL | ALL | pinball_50 | -0.0004032075 | -0.0005367063 | -0.0002892701 | 2331 | 118 |
| inner_train | VOL | ALL | pinball_95 | -0.01085753 | -0.01182427 | -0.009872531 | 2331 | 118 |
| inner_validation | VOL | ALL | proper_loss | -0.007409604 | -0.009028117 | -0.005729703 | 92 | 6 |
| inner_validation | VOL | ALL | pinball_05 | -0.01251906 | -0.01656716 | -0.009523841 | 92 | 6 |
| inner_validation | VOL | ALL | pinball_50 | -5.297922e-05 | -0.000521011 | 0.000438279 | 92 | 6 |
| inner_validation | VOL | ALL | pinball_95 | -0.009656768 | -0.01429891 | -0.005563441 | 92 | 6 |
| refit | GLOBAL | ALL | proper_loss | -0.005448555 | -0.005974212 | -0.004956488 | 2423 | 124 |
| refit | GLOBAL | ALL | pinball_05 | -0.007185057 | -0.008003644 | -0.006400767 | 2423 | 124 |
| refit | GLOBAL | ALL | pinball_50 | -0.0003731104 | -0.0004698192 | -0.0002692333 | 2423 | 124 |
| refit | GLOBAL | ALL | pinball_95 | -0.008787499 | -0.009829796 | -0.0078096 | 2423 | 124 |
| oos | GLOBAL | ALL | proper_loss | -0.001532354 | -0.002769672 | -0.0002635033 | 210 | 12 |
| oos | GLOBAL | ALL | pinball_05 | -0.003354505 | -0.005745008 | -0.001235572 | 210 | 12 |
| oos | GLOBAL | ALL | pinball_50 | 1.317348e-05 | -0.0004049727 | 0.0003827999 | 210 | 12 |
| oos | GLOBAL | ALL | pinball_95 | -0.001255732 | -0.003349552 | 0.0005410309 | 210 | 12 |
| refit | STOCK | ALL | proper_loss | -0.0002747718 | -0.0005706445 | 2.018957e-05 | 2423 | 124 |
| refit | STOCK | ALL | pinball_05 | -0.0003438777 | -0.0008158795 | 0.0001117928 | 2423 | 124 |
| refit | STOCK | ALL | pinball_50 | -0.0002022663 | -0.0003464481 | -2.120797e-05 | 2423 | 124 |
| refit | STOCK | ALL | pinball_95 | -0.0002781713 | -0.0008460641 | 0.0002081281 | 2423 | 124 |
| oos | STOCK | ALL | proper_loss | 0.001412994 | 0.0005532496 | 0.002413911 | 210 | 12 |
| oos | STOCK | ALL | pinball_05 | 0.002428573 | 0.0008601775 | 0.003879762 | 210 | 12 |
| oos | STOCK | ALL | pinball_50 | -0.0005501562 | -0.001313668 | 0.0001257973 | 210 | 12 |
| oos | STOCK | ALL | pinball_95 | 0.002360566 | 0.0005579549 | 0.004019621 | 210 | 12 |
| refit | VOL | ALL | proper_loss | -0.007419022 | -0.007998356 | -0.006832271 | 2423 | 124 |
| refit | VOL | ALL | pinball_05 | -0.01105308 | -0.01214864 | -0.0100472 | 2423 | 124 |
| refit | VOL | ALL | pinball_50 | -0.0003731104 | -0.0004698192 | -0.0002692333 | 2423 | 124 |
| refit | VOL | ALL | pinball_95 | -0.01083088 | -0.01185619 | -0.009898353 | 2423 | 124 |
| oos | VOL | ALL | proper_loss | -0.00441197 | -0.005827738 | -0.002808078 | 210 | 12 |
| oos | VOL | ALL | pinball_05 | -0.006762914 | -0.01024407 | -0.002911863 | 210 | 12 |
| oos | VOL | ALL | pinball_50 | 1.317348e-05 | -0.0004049727 | 0.0003827999 | 210 | 12 |
| oos | VOL | ALL | pinball_95 | -0.006486168 | -0.00838771 | -0.004707388 | 210 | 12 |


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
