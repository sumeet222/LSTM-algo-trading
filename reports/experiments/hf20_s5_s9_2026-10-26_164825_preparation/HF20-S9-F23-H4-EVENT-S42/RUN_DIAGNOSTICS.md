# HF20-S9-F23-H4-EVENT-S42

TECHNICAL_PASS. All four roles verified; OOS remains exploratory.

| role | model | arm | rows | origins | sessions | optimized_loss | prevalence | ANY_AP | ANY_AUC | ANY_Brier | ANY_log_loss | precision_at_half | recall_at_half | year |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | EVENT | 277920 | 13896 | 2547 | 0.2339553 | 0.05024899 | 0.05024899 | 0.5 | 0.04772403 | 0.1992477 | nan | 0 | 2023 |
| inner_validation | GLOBAL | EVENT | 9060 | 453 | 86 | 0.2222114 | 0.04696429 | 0.04696429 | 0.5 | 0.04476943 | 0.1895933 | nan | 0 | 2023 |
| inner_train | STOCK | EVENT | 277920 | 13896 | 2547 | 0.2048057 | 0.05024899 | 0.1655744 | 0.7802964 | 0.04378635 | 0.1701753 | nan | 0 | 2023 |
| inner_validation | STOCK | EVENT | 9060 | 453 | 86 | 0.2015403 | 0.04696429 | 0.123319 | 0.7307682 | 0.04225704 | 0.1689246 | nan | 0 | 2023 |
| inner_train | VOL | EVENT | 277920 | 13896 | 2547 | 0.2176849 | 0.05024899 | 0.09921463 | 0.7179663 | 0.04602659 | 0.1829981 | nan | 0 | 2023 |
| inner_validation | VOL | EVENT | 9060 | 453 | 86 | 0.2148375 | 0.04696429 | 0.07874924 | 0.6862819 | 0.04430066 | 0.182215 | nan | 0 | 2023 |
| inner_train | NEURAL | EVENT | 277920 | 13896 | 2547 | 0.2031038 | 0.05024899 | 0.2215546 | 0.7943826 | 0.04335174 | 0.1688282 | 0.803391 | 0.004363449 | 2023 |
| inner_validation | NEURAL | EVENT | 9060 | 453 | 86 | 0.2028966 | 0.04696429 | 0.1468768 | 0.7692014 | 0.04258186 | 0.1697935 | nan | 0 | 2023 |
| refit | GLOBAL | EVENT | 287900 | 14395 | 2640 | 0.2335882 | 0.05014646 | 0.05014646 | 0.5 | 0.0476318 | 0.1989463 | nan | 0 | 2023 |
| oos | GLOBAL | EVENT | 17740 | 887 | 187 | 0.2127923 | 0.04445569 | 0.04445569 | 0.5 | 0.04251177 | 0.1822077 | nan | 0 | 2023 |
| refit | STOCK | EVENT | 287900 | 14395 | 2640 | 0.2046778 | 0.05014646 | 0.1641533 | 0.7791179 | 0.04373629 | 0.1701131 | nan | 0 | 2023 |
| oos | STOCK | EVENT | 17740 | 887 | 187 | 0.1857902 | 0.04445569 | 0.1623884 | 0.7809512 | 0.03911715 | 0.1553986 | nan | 0 | 2023 |
| refit | VOL | EVENT | 287900 | 14395 | 2640 | 0.2174736 | 0.05014646 | 0.09874852 | 0.7169295 | 0.04595339 | 0.1828542 | nan | 0 | 2023 |
| oos | VOL | EVENT | 17740 | 887 | 187 | 0.1953983 | 0.04445569 | 0.1002619 | 0.7352251 | 0.04069935 | 0.1647655 | nan | 0 | 2023 |
| refit | NEURAL | EVENT | 287900 | 14395 | 2640 | 0.2023696 | 0.05014646 | 0.2183014 | 0.7936327 | 0.04322067 | 0.1681884 | 0.628026 | 0.0110346 | 2023 |
| oos | NEURAL | EVENT | 17740 | 887 | 187 | 0.1941089 | 0.04445569 | 0.12387 | 0.7709898 | 0.04167142 | 0.1637736 | 0 | 0 | 2023 |


| role | reference | group | metric | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | ALL | proper_loss | -0.03085148 | -0.03381907 | -0.02804866 | 2547 | 130 |
| inner_train | GLOBAL | ALL | ANY_Brier | -0.004372287 | -0.004945247 | -0.003850754 | 2547 | 130 |
| inner_train | GLOBAL | ALL | ANY_log_loss | -0.03041956 | -0.03337189 | -0.02759281 | 2547 | 130 |
| inner_validation | GLOBAL | ALL | proper_loss | -0.01931475 | -0.02571997 | -0.00977845 | 86 | 6 |
| inner_validation | GLOBAL | ALL | ANY_Brier | -0.002187573 | -0.003519213 | -0.0006411515 | 86 | 6 |
| inner_validation | GLOBAL | ALL | ANY_log_loss | -0.01979984 | -0.02646526 | -0.009850022 | 86 | 6 |
| inner_train | STOCK | ALL | proper_loss | -0.001701891 | -0.003501148 | -4.707704e-05 | 2547 | 130 |
| inner_train | STOCK | ALL | ANY_Brier | -0.0004346086 | -0.000755778 | -0.0001647846 | 2547 | 130 |
| inner_train | STOCK | ALL | ANY_log_loss | -0.001347156 | -0.003111625 | 0.0003233375 | 2547 | 130 |
| inner_validation | STOCK | ALL | proper_loss | 0.001356286 | -0.005847932 | 0.007735125 | 86 | 6 |
| inner_validation | STOCK | ALL | ANY_Brier | 0.000324819 | -0.0007522217 | 0.001264109 | 86 | 6 |
| inner_validation | STOCK | ALL | ANY_log_loss | 0.0008688181 | -0.006444858 | 0.007653454 | 86 | 6 |
| inner_train | VOL | ALL | proper_loss | -0.01458112 | -0.01655015 | -0.01283543 | 2547 | 130 |
| inner_train | VOL | ALL | ANY_Brier | -0.00267485 | -0.003123656 | -0.002341287 | 2547 | 130 |
| inner_train | VOL | ALL | ANY_log_loss | -0.01416999 | -0.01613668 | -0.01242737 | 2547 | 130 |
| inner_validation | VOL | ALL | proper_loss | -0.01194084 | -0.01638661 | -0.007467112 | 86 | 6 |
| inner_validation | VOL | ALL | ANY_Brier | -0.001718798 | -0.002811831 | -0.0007911423 | 86 | 6 |
| inner_validation | VOL | ALL | ANY_log_loss | -0.01242159 | -0.01691708 | -0.007807014 | 86 | 6 |
| refit | GLOBAL | ALL | proper_loss | -0.03121855 | -0.03387507 | -0.02819216 | 2640 | 136 |
| refit | GLOBAL | ALL | ANY_Brier | -0.004411127 | -0.004963254 | -0.003846867 | 2640 | 136 |
| refit | GLOBAL | ALL | ANY_log_loss | -0.03075789 | -0.03339353 | -0.02775558 | 2640 | 136 |
| oos | GLOBAL | ALL | proper_loss | -0.01868337 | -0.0266954 | -0.01097068 | 187 | 12 |
| oos | GLOBAL | ALL | ANY_Brier | -0.000840352 | -0.002725837 | 0.001381821 | 187 | 12 |
| oos | GLOBAL | ALL | ANY_log_loss | -0.01843407 | -0.0263589 | -0.01063692 | 187 | 12 |
| refit | STOCK | ALL | proper_loss | -0.00230812 | -0.003873565 | -0.0004224944 | 2640 | 136 |
| refit | STOCK | ALL | ANY_Brier | -0.0005156192 | -0.0008252109 | -0.0001943466 | 2640 | 136 |
| refit | STOCK | ALL | ANY_log_loss | -0.001924713 | -0.003468094 | -6.233983e-05 | 2640 | 136 |
| oos | STOCK | ALL | proper_loss | 0.008318748 | 0.001504791 | 0.01539701 | 187 | 12 |
| oos | STOCK | ALL | ANY_Brier | 0.002554265 | 0.0008158023 | 0.004612101 | 187 | 12 |
| oos | STOCK | ALL | ANY_log_loss | 0.008375006 | 0.001630183 | 0.01547685 | 187 | 12 |
| refit | VOL | ALL | proper_loss | -0.01510394 | -0.01661924 | -0.01344679 | 2640 | 136 |
| refit | VOL | ALL | ANY_Brier | -0.002732725 | -0.003106928 | -0.002365909 | 2640 | 136 |
| refit | VOL | ALL | ANY_log_loss | -0.01466584 | -0.01614335 | -0.01300167 | 2640 | 136 |
| oos | VOL | ALL | proper_loss | -0.001289382 | -0.007908686 | 0.005422657 | 187 | 12 |
| oos | VOL | ALL | ANY_Brier | 0.0009720624 | -0.0007707403 | 0.003262154 | 187 | 12 |
| oos | VOL | ALL | ANY_log_loss | -0.0009919521 | -0.007703563 | 0.005810229 | 187 | 12 |


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
