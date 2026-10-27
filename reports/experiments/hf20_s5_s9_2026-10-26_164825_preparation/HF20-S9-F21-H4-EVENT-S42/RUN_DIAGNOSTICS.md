# HF20-S9-F21-H4-EVENT-S42

TECHNICAL_PASS. All four roles verified; OOS remains exploratory.

| role | model | arm | rows | origins | sessions | optimized_loss | prevalence | ANY_AP | ANY_AUC | ANY_Brier | ANY_log_loss | precision_at_half | recall_at_half | year |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | EVENT | 228980 | 11449 | 2100 | 0.2341219 | 0.05028827 | 0.05028827 | 0.5 | 0.04775936 | 0.1993631 | nan | 0 | 2021 |
| inner_validation | GLOBAL | EVENT | 13480 | 674 | 120 | 0.2257529 | 0.048125 | 0.048125 | 0.5 | 0.04581366 | 0.1930066 | nan | 0 | 2021 |
| inner_train | STOCK | EVENT | 228980 | 11449 | 2100 | 0.2038154 | 0.05028827 | 0.1714412 | 0.7869776 | 0.04366095 | 0.169137 | nan | 0 | 2021 |
| inner_validation | STOCK | EVENT | 13480 | 674 | 120 | 0.2008078 | 0.048125 | 0.1356566 | 0.757442 | 0.04287273 | 0.1685121 | nan | 0 | 2021 |
| inner_train | VOL | EVENT | 228980 | 11449 | 2100 | 0.2165752 | 0.05028827 | 0.1022937 | 0.7245694 | 0.04590897 | 0.1818386 | nan | 0 | 2021 |
| inner_validation | VOL | EVENT | 13480 | 674 | 120 | 0.2180406 | 0.048125 | 0.08001169 | 0.6982799 | 0.04549614 | 0.1853816 | nan | 0 | 2021 |
| inner_train | NEURAL | EVENT | 228980 | 11449 | 2100 | 0.206541 | 0.05028827 | 0.1979648 | 0.7841175 | 0.04407713 | 0.1719032 | 1 | 0.0002029118 | 2021 |
| inner_validation | NEURAL | EVENT | 13480 | 674 | 120 | 0.2031788 | 0.048125 | 0.1876018 | 0.7969711 | 0.04294141 | 0.1702112 | nan | 0 | 2021 |
| refit | GLOBAL | EVENT | 243420 | 12171 | 2227 | 0.234298 | 0.05034608 | 0.05034608 | 0.5 | 0.04781135 | 0.199533 | nan | 0 | 2021 |
| oos | GLOBAL | EVENT | 19100 | 955 | 188 | 0.1970795 | 0.04010512 | 0.04010512 | 0.5 | 0.03860157 | 0.1694535 | nan | 0 | 2021 |
| refit | STOCK | EVENT | 243420 | 12171 | 2227 | 0.2040478 | 0.05034608 | 0.1697805 | 0.786225 | 0.04373318 | 0.1693892 | nan | 0 | 2021 |
| oos | STOCK | EVENT | 19100 | 955 | 188 | 0.1776946 | 0.04010512 | 0.1265949 | 0.7442734 | 0.03633149 | 0.1498205 | nan | 0 | 2021 |
| refit | VOL | EVENT | 243420 | 12171 | 2227 | 0.2169619 | 0.05034608 | 0.10186 | 0.7234751 | 0.04598481 | 0.1822193 | nan | 0 | 2021 |
| oos | VOL | EVENT | 19100 | 955 | 188 | 0.1882511 | 0.04010512 | 0.07371819 | 0.7053634 | 0.03807475 | 0.1606343 | nan | 0 | 2021 |
| refit | NEURAL | EVENT | 243420 | 12171 | 2227 | 0.2064583 | 0.05034608 | 0.1933261 | 0.7825257 | 0.04407031 | 0.1718124 | 0.7291667 | 0.0007432465 | 2021 |
| oos | NEURAL | EVENT | 19100 | 955 | 188 | 0.1804943 | 0.04010512 | 0.139907 | 0.7628848 | 0.03703512 | 0.1528068 | nan | 0 | 2021 |


| role | reference | group | metric | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | ALL | proper_loss | -0.02758097 | -0.03059887 | -0.02422964 | 2100 | 106 |
| inner_train | GLOBAL | ALL | ANY_Brier | -0.00368223 | -0.004197959 | -0.003058439 | 2100 | 106 |
| inner_train | GLOBAL | ALL | ANY_log_loss | -0.02745994 | -0.0304519 | -0.02399227 | 2100 | 106 |
| inner_validation | GLOBAL | ALL | proper_loss | -0.02257406 | -0.02942592 | -0.01603255 | 120 | 6 |
| inner_validation | GLOBAL | ALL | ANY_Brier | -0.002872254 | -0.004485356 | -0.001421631 | 120 | 6 |
| inner_validation | GLOBAL | ALL | ANY_log_loss | -0.0227954 | -0.02967195 | -0.01601343 | 120 | 6 |
| inner_train | STOCK | ALL | proper_loss | 0.002725551 | 0.0007941332 | 0.004939534 | 2100 | 106 |
| inner_train | STOCK | ALL | ANY_Brier | 0.0004161751 | 4.677995e-05 | 0.0007625853 | 2100 | 106 |
| inner_train | STOCK | ALL | ANY_log_loss | 0.002766191 | 0.0008289134 | 0.004897756 | 2100 | 106 |
| inner_validation | STOCK | ALL | proper_loss | 0.002371044 | -0.001670092 | 0.005404411 | 120 | 6 |
| inner_validation | STOCK | ALL | ANY_Brier | 6.867986e-05 | -0.0004381212 | 0.0006098426 | 120 | 6 |
| inner_validation | STOCK | ALL | ANY_log_loss | 0.001699142 | -0.002521766 | 0.005072618 | 120 | 6 |
| inner_train | VOL | ALL | proper_loss | -0.01003424 | -0.01194845 | -0.008259705 | 2100 | 106 |
| inner_train | VOL | ALL | ANY_Brier | -0.001831842 | -0.002191509 | -0.001448958 | 2100 | 106 |
| inner_train | VOL | ALL | ANY_log_loss | -0.009935418 | -0.01183246 | -0.00820812 | 2100 | 106 |
| inner_validation | VOL | ALL | proper_loss | -0.01486177 | -0.02002351 | -0.01018648 | 120 | 6 |
| inner_validation | VOL | ALL | ANY_Brier | -0.002554734 | -0.003828031 | -0.001299684 | 120 | 6 |
| inner_validation | VOL | ALL | ANY_log_loss | -0.01517034 | -0.02023856 | -0.01058473 | 120 | 6 |
| refit | GLOBAL | ALL | proper_loss | -0.02783976 | -0.03070119 | -0.02430294 | 2227 | 112 |
| refit | GLOBAL | ALL | ANY_Brier | -0.00374104 | -0.004333864 | -0.003067365 | 2227 | 112 |
| refit | GLOBAL | ALL | ANY_log_loss | -0.0277206 | -0.03060193 | -0.02411437 | 2227 | 112 |
| oos | GLOBAL | ALL | proper_loss | -0.01658525 | -0.02813661 | -0.006350179 | 188 | 12 |
| oos | GLOBAL | ALL | ANY_Brier | -0.001566455 | -0.003838115 | 0.000661493 | 188 | 12 |
| oos | GLOBAL | ALL | ANY_log_loss | -0.01664671 | -0.02810265 | -0.006523905 | 188 | 12 |
| refit | STOCK | ALL | proper_loss | 0.00241048 | 0.0002032176 | 0.004966036 | 2227 | 112 |
| refit | STOCK | ALL | ANY_Brier | 0.0003371319 | -4.974642e-05 | 0.0007791125 | 2227 | 112 |
| refit | STOCK | ALL | ANY_log_loss | 0.00242318 | 0.0002379868 | 0.004951209 | 2227 | 112 |
| oos | STOCK | ALL | proper_loss | 0.002799712 | -0.003122895 | 0.008357598 | 188 | 12 |
| oos | STOCK | ALL | ANY_Brier | 0.0007036243 | -0.0002940769 | 0.001679846 | 188 | 12 |
| oos | STOCK | ALL | ANY_log_loss | 0.002986251 | -0.003041644 | 0.008425692 | 188 | 12 |
| refit | VOL | ALL | proper_loss | -0.01050368 | -0.01216183 | -0.008689281 | 2227 | 112 |
| refit | VOL | ALL | ANY_Brier | -0.0019145 | -0.00229248 | -0.001483897 | 2227 | 112 |
| refit | VOL | ALL | ANY_log_loss | -0.01040688 | -0.01202706 | -0.008620666 | 2227 | 112 |
| oos | VOL | ALL | proper_loss | -0.007756817 | -0.01514146 | -0.001662939 | 188 | 12 |
| oos | VOL | ALL | ANY_Brier | -0.001039637 | -0.002760158 | 0.0004665667 | 188 | 12 |
| oos | VOL | ALL | ANY_log_loss | -0.00782749 | -0.01526383 | -0.001706016 | 188 | 12 |


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
