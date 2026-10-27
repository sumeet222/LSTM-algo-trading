# HF20-S9-F24-H4-QUANTILE-S42

TECHNICAL_PASS. All four roles verified; OOS remains exploratory.

| role | model | arm | rows | origins | sessions | optimized_loss | pinball_05 | pinball_50 | pinball_95 | coverage_05 | coverage_50 | coverage_95 | coverage90 | width_z | crossing_fraction | interval_score90_z | width_magnitude_rank_association | year |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | QUANTILE | 298900 | 14945 | 2740 | 0.2351903 | 0.1136274 | 0.4759353 | 0.116008 | 0.05000117 | 0.5000666 | 0.9500003 | 0.8999991 | 3.721069 | 0 | 4.59271 | -2.363525e-15 | 2024 |
| inner_validation | GLOBAL | QUANTILE | 7000 | 350 | 87 | 0.2315058 | 0.1115445 | 0.4704184 | 0.1125546 | 0.04868911 | 0.5 | 0.9559606 | 0.9072715 | 3.721069 | 0 | 4.481982 | -1.929823e-16 | 2024 |
| inner_train | STOCK | QUANTILE | 298900 | 14945 | 2740 | 0.2301714 | 0.1069252 | 0.4757925 | 0.1077965 | 0.05003571 | 0.5000371 | 0.9500224 | 0.9000469 | 3.592088 | 0 | 4.294435 | 0.2421633 | 2024 |
| inner_validation | STOCK | QUANTILE | 7000 | 350 | 87 | 0.2265627 | 0.104962 | 0.47024 | 0.1044862 | 0.04667077 | 0.5004105 | 0.9560317 | 0.909361 | 3.592088 | 0 | 4.188964 | 0.2640158 | 2024 |
| inner_train | VOL | QUANTILE | 298900 | 14945 | 2740 | 0.2373204 | 0.1177577 | 0.4759353 | 0.1182682 | 0.05000152 | 0.5000666 | 0.9499985 | 0.8999996 | 3.998312 | 0 | 4.720519 | 0.2626597 | 2024 |
| inner_validation | VOL | QUANTILE | 7000 | 350 | 87 | 0.2329845 | 0.1156676 | 0.4704184 | 0.1128674 | 0.05649015 | 0.5 | 0.949595 | 0.8931048 | 3.821608 | 0 | 4.5707 | 0.2281795 | 2024 |
| inner_train | NEURAL | QUANTILE | 298900 | 14945 | 2740 | 0.2302506 | 0.1071259 | 0.4756205 | 0.1080055 | 0.04637643 | 0.5020424 | 0.9507664 | 0.90439 | 3.64105 | 0 | 4.302628 | 0.2590472 | 2024 |
| inner_validation | NEURAL | QUANTILE | 7000 | 350 | 87 | 0.227252 | 0.1058134 | 0.4706108 | 0.1053316 | 0.05025041 | 0.4996004 | 0.9501601 | 0.8999097 | 3.532301 | 0 | 4.222901 | 0.2481266 | 2024 |
| refit | GLOBAL | QUANTILE | 306640 | 15332 | 2835 | 0.2350511 | 0.1135313 | 0.4757424 | 0.1158795 | 0.05000424 | 0.5000644 | 0.9500005 | 0.9000022 | 3.71923 | 0 | 4.588218 | -3.253981e-15 | 2024 |
| oos | GLOBAL | QUANTILE | 19820 | 991 | 208 | 0.2383654 | 0.1157866 | 0.4815959 | 0.1177136 | 0.05508642 | 0.5 | 0.9454144 | 0.890328 | 3.71923 | 0 | 4.670005 | 4.394074e-16 | 2024 |
| refit | STOCK | QUANTILE | 306640 | 15332 | 2835 | 0.2300429 | 0.1068592 | 0.4755965 | 0.107673 | 0.05002549 | 0.5000308 | 0.950045 | 0.900081 | 3.589861 | 0 | 4.290645 | 0.2424243 | 2024 |
| oos | STOCK | QUANTILE | 19820 | 991 | 208 | 0.2330445 | 0.1075714 | 0.4818868 | 0.1096754 | 0.0540024 | 0.5000813 | 0.9476568 | 0.8936544 | 3.589861 | 0 | 4.344937 | 0.2854828 | 2024 |
| refit | VOL | QUANTILE | 306640 | 15332 | 2835 | 0.2371916 | 0.1177574 | 0.4757424 | 0.118075 | 0.0500013 | 0.5000644 | 0.9500027 | 0.900005 | 3.995963 | 0 | 4.716648 | 0.2612236 | 2024 |
| oos | VOL | QUANTILE | 19820 | 991 | 208 | 0.2400685 | 0.1185604 | 0.4815959 | 0.1200492 | 0.05196371 | 0.5 | 0.9533917 | 0.901428 | 4.037806 | 0 | 4.772193 | 0.2680145 | 2024 |
| refit | NEURAL | QUANTILE | 306640 | 15332 | 2835 | 0.2300921 | 0.1070001 | 0.4754552 | 0.1078211 | 0.04833426 | 0.499387 | 0.9485377 | 0.9002035 | 3.601295 | 0 | 4.296425 | 0.2585293 | 2024 |
| oos | NEURAL | QUANTILE | 19820 | 991 | 208 | 0.2325667 | 0.107018 | 0.4817128 | 0.1089694 | 0.05194368 | 0.4985937 | 0.9495061 | 0.8975624 | 3.585964 | 0 | 4.319747 | 0.2929806 | 2024 |


| role | reference | group | metric | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | ALL | proper_loss | -0.004939612 | -0.005481065 | -0.004409564 | 2740 | 142 |
| inner_train | GLOBAL | ALL | pinball_05 | -0.006501504 | -0.007359544 | -0.005614571 | 2740 | 142 |
| inner_train | GLOBAL | ALL | pinball_50 | -0.0003147478 | -0.0004258515 | -0.0002143577 | 2740 | 142 |
| inner_train | GLOBAL | ALL | pinball_95 | -0.008002584 | -0.009044181 | -0.006938787 | 2740 | 142 |
| inner_validation | GLOBAL | ALL | proper_loss | -0.004253879 | -0.005778547 | -0.002814408 | 87 | 6 |
| inner_validation | GLOBAL | ALL | pinball_05 | -0.005731028 | -0.007562666 | -0.003956421 | 87 | 6 |
| inner_validation | GLOBAL | ALL | pinball_50 | 0.0001924222 | -0.0006203347 | 0.0009739884 | 87 | 6 |
| inner_validation | GLOBAL | ALL | pinball_95 | -0.007223033 | -0.00992699 | -0.004480693 | 87 | 6 |
| inner_train | STOCK | ALL | proper_loss | 7.922331e-05 | -0.0002638711 | 0.0004918553 | 2740 | 142 |
| inner_train | STOCK | ALL | pinball_05 | 0.0002007178 | -0.0003695839 | 0.000858608 | 2740 | 142 |
| inner_train | STOCK | ALL | pinball_50 | -0.0001719802 | -0.0003175908 | -6.50826e-06 | 2740 | 142 |
| inner_train | STOCK | ALL | pinball_95 | 0.0002089322 | -0.0003824287 | 0.000826577 | 2740 | 142 |
| inner_validation | STOCK | ALL | proper_loss | 0.0006892248 | -0.0001969794 | 0.001390929 | 87 | 6 |
| inner_validation | STOCK | ALL | pinball_05 | 0.0008514157 | -0.0003289436 | 0.002322429 | 87 | 6 |
| inner_validation | STOCK | ALL | pinball_50 | 0.0003708518 | -0.0002232493 | 0.0008972544 | 87 | 6 |
| inner_validation | STOCK | ALL | pinball_95 | 0.0008454069 | -0.001026858 | 0.002604494 | 87 | 6 |
| inner_train | VOL | ALL | proper_loss | -0.007069762 | -0.007772149 | -0.006349227 | 2740 | 142 |
| inner_train | VOL | ALL | pinball_05 | -0.01063174 | -0.01189931 | -0.009473 | 2740 | 142 |
| inner_train | VOL | ALL | pinball_50 | -0.0003147478 | -0.0004258515 | -0.0002143577 | 2740 | 142 |
| inner_train | VOL | ALL | pinball_95 | -0.0102628 | -0.01127643 | -0.009143602 | 2740 | 142 |
| inner_validation | VOL | ALL | proper_loss | -0.005732515 | -0.006827784 | -0.004194777 | 87 | 6 |
| inner_validation | VOL | ALL | pinball_05 | -0.00985416 | -0.01127714 | -0.008159236 | 87 | 6 |
| inner_validation | VOL | ALL | pinball_50 | 0.0001924222 | -0.0006203347 | 0.0009739884 | 87 | 6 |
| inner_validation | VOL | ALL | pinball_95 | -0.007535806 | -0.009783648 | -0.004661165 | 87 | 6 |
| refit | GLOBAL | ALL | proper_loss | -0.004958971 | -0.005421574 | -0.004413482 | 2835 | 148 |
| refit | GLOBAL | ALL | pinball_05 | -0.006531249 | -0.00727574 | -0.005729142 | 2835 | 148 |
| refit | GLOBAL | ALL | pinball_50 | -0.0002872566 | -0.000392362 | -0.0001788707 | 2835 | 148 |
| refit | GLOBAL | ALL | pinball_95 | -0.008058406 | -0.009070404 | -0.007113357 | 2835 | 148 |
| oos | GLOBAL | ALL | proper_loss | -0.005798656 | -0.007119138 | -0.004733827 | 208 | 12 |
| oos | GLOBAL | ALL | pinball_05 | -0.008768668 | -0.01181933 | -0.006232753 | 208 | 12 |
| oos | GLOBAL | ALL | pinball_50 | 0.0001169511 | -0.0001677086 | 0.000423798 | 208 | 12 |
| oos | GLOBAL | ALL | pinball_95 | -0.00874425 | -0.01019623 | -0.007350992 | 208 | 12 |
| refit | STOCK | ALL | proper_loss | 4.924225e-05 | -0.0002796708 | 0.0004001625 | 2835 | 148 |
| refit | STOCK | ALL | pinball_05 | 0.000140859 | -0.0003933351 | 0.0006680748 | 2835 | 148 |
| refit | STOCK | ALL | pinball_50 | -0.0001412673 | -0.0002943736 | 3.138922e-05 | 2835 | 148 |
| refit | STOCK | ALL | pinball_95 | 0.000148135 | -0.000399904 | 0.0007500516 | 2835 | 148 |
| oos | STOCK | ALL | proper_loss | -0.0004778082 | -0.00100626 | -9.814539e-05 | 208 | 12 |
| oos | STOCK | ALL | pinball_05 | -0.0005534708 | -0.001152763 | -6.977107e-07 | 208 | 12 |
| oos | STOCK | ALL | pinball_50 | -0.0001739092 | -0.0007385938 | 0.0003441061 | 208 | 12 |
| oos | STOCK | ALL | pinball_95 | -0.0007060447 | -0.001660365 | 5.206465e-05 | 208 | 12 |
| refit | VOL | ALL | proper_loss | -0.007099471 | -0.007645368 | -0.006440509 | 2835 | 148 |
| refit | VOL | ALL | pinball_05 | -0.01075726 | -0.01187312 | -0.009714613 | 2835 | 148 |
| refit | VOL | ALL | pinball_50 | -0.0002872566 | -0.000392362 | -0.0001788707 | 2835 | 148 |
| refit | VOL | ALL | pinball_95 | -0.0102539 | -0.01116769 | -0.0091542 | 2835 | 148 |
| oos | VOL | ALL | proper_loss | -0.007501785 | -0.008782067 | -0.006356805 | 208 | 12 |
| oos | VOL | ALL | pinball_05 | -0.01154247 | -0.01369952 | -0.009471642 | 208 | 12 |
| oos | VOL | ALL | pinball_50 | 0.0001169511 | -0.0001677086 | 0.000423798 | 208 | 12 |
| oos | VOL | ALL | pinball_95 | -0.01107984 | -0.0133796 | -0.008799267 | 208 | 12 |


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
