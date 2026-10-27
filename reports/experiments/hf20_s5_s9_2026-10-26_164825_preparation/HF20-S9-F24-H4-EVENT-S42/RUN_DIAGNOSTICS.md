# HF20-S9-F24-H4-EVENT-S42

TECHNICAL_PASS. All four roles verified; OOS remains exploratory.

| role | model | arm | rows | origins | sessions | optimized_loss | prevalence | ANY_AP | ANY_AUC | ANY_Brier | ANY_log_loss | precision_at_half | recall_at_half | year |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | EVENT | 298900 | 14945 | 2740 | 0.2333479 | 0.05008346 | 0.05008346 | 0.5 | 0.04757511 | 0.1987609 | nan | 0 | 2024 |
| inner_validation | GLOBAL | EVENT | 7000 | 350 | 87 | 0.2158955 | 0.04527915 | 0.04527915 | 0.5 | 0.04325203 | 0.1846233 | nan | 0 | 2024 |
| inner_train | STOCK | EVENT | 298900 | 14945 | 2740 | 0.2042903 | 0.05008346 | 0.1651254 | 0.7797862 | 0.04365463 | 0.1697933 | nan | 0 | 2024 |
| inner_validation | STOCK | EVENT | 7000 | 350 | 87 | 0.1889278 | 0.04527915 | 0.1595331 | 0.779673 | 0.03987439 | 0.1576671 | nan | 0 | 2024 |
| inner_train | VOL | EVENT | 298900 | 14945 | 2740 | 0.2171366 | 0.05008346 | 0.09890444 | 0.7174142 | 0.04588636 | 0.1825713 | nan | 0 | 2024 |
| inner_validation | VOL | EVENT | 7000 | 350 | 87 | 0.1973944 | 0.04527915 | 0.1111909 | 0.7381176 | 0.04120569 | 0.1660221 | nan | 0 | 2024 |
| inner_train | NEURAL | EVENT | 298900 | 14945 | 2740 | 0.2088284 | 0.05008346 | 0.1732651 | 0.7681653 | 0.0443856 | 0.1742753 | nan | 0 | 2024 |
| inner_validation | NEURAL | EVENT | 7000 | 350 | 87 | 0.1972835 | 0.04527915 | 0.1294991 | 0.7395691 | 0.04120287 | 0.1660226 | nan | 0 | 2024 |
| refit | GLOBAL | EVENT | 306640 | 15332 | 2835 | 0.2331181 | 0.05002049 | 0.05002049 | 0.5 | 0.04751844 | 0.1985756 | nan | 0 | 2024 |
| oos | GLOBAL | EVENT | 19820 | 991 | 208 | 0.2537315 | 0.05562271 | 0.05562271 | 0.5 | 0.05256021 | 0.2150686 | nan | 0 | 2024 |
| refit | STOCK | EVENT | 306640 | 15332 | 2835 | 0.2040738 | 0.05002049 | 0.1652745 | 0.7797755 | 0.04359979 | 0.1696223 | nan | 0 | 2024 |
| oos | STOCK | EVENT | 19820 | 991 | 208 | 0.2225626 | 0.05562271 | 0.1858586 | 0.7944883 | 0.04826021 | 0.1841363 | nan | 0 | 2024 |
| refit | VOL | EVENT | 306640 | 15332 | 2835 | 0.2168612 | 0.05002049 | 0.09902754 | 0.7177998 | 0.04582247 | 0.1823378 | nan | 0 | 2024 |
| oos | VOL | EVENT | 19820 | 991 | 208 | 0.2320337 | 0.05562271 | 0.1264613 | 0.731104 | 0.04989373 | 0.1933138 | nan | 0 | 2024 |
| refit | NEURAL | EVENT | 306640 | 15332 | 2835 | 0.2087488 | 0.05002049 | 0.1733099 | 0.7675223 | 0.04433536 | 0.17423 | 0.5384615 | 5.876486e-05 | 2024 |
| oos | NEURAL | EVENT | 19820 | 991 | 208 | 0.223347 | 0.05562271 | 0.2025737 | 0.7834284 | 0.04828969 | 0.1848102 | nan | 0 | 2024 |


| role | reference | group | metric | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | ALL | proper_loss | -0.0245195 | -0.02726699 | -0.02149012 | 2740 | 142 |
| inner_train | GLOBAL | ALL | ANY_Brier | -0.003189509 | -0.003750255 | -0.002539926 | 2740 | 142 |
| inner_train | GLOBAL | ALL | ANY_log_loss | -0.02448561 | -0.02720113 | -0.02147101 | 2740 | 142 |
| inner_validation | GLOBAL | ALL | proper_loss | -0.01861204 | -0.02737735 | -0.01050111 | 87 | 6 |
| inner_validation | GLOBAL | ALL | ANY_Brier | -0.002049157 | -0.003479442 | -0.0006599574 | 87 | 6 |
| inner_validation | GLOBAL | ALL | ANY_log_loss | -0.01860077 | -0.02783574 | -0.01017938 | 87 | 6 |
| inner_train | STOCK | ALL | proper_loss | 0.004538103 | 0.002796673 | 0.006861735 | 2740 | 142 |
| inner_train | STOCK | ALL | ANY_Brier | 0.0007309671 | 0.0003767478 | 0.001153146 | 2740 | 142 |
| inner_train | STOCK | ALL | ANY_log_loss | 0.004482004 | 0.002687555 | 0.006781484 | 2740 | 142 |
| inner_validation | STOCK | ALL | proper_loss | 0.00835575 | 0.001144791 | 0.01438295 | 87 | 6 |
| inner_validation | STOCK | ALL | ANY_Brier | 0.001328482 | 0.0002822779 | 0.002262069 | 87 | 6 |
| inner_validation | STOCK | ALL | ANY_log_loss | 0.008355448 | 0.001925903 | 0.01384914 | 87 | 6 |
| inner_train | VOL | ALL | proper_loss | -0.008308157 | -0.009518913 | -0.006621112 | 2740 | 142 |
| inner_train | VOL | ALL | ANY_Brier | -0.001500762 | -0.001802032 | -0.001096558 | 2740 | 142 |
| inner_train | VOL | ALL | ANY_log_loss | -0.008296016 | -0.00948506 | -0.006602274 | 2740 | 142 |
| inner_validation | VOL | ALL | proper_loss | -0.0001108773 | -0.002976973 | 0.0028091 | 87 | 6 |
| inner_validation | VOL | ALL | ANY_Brier | -2.818175e-06 | -0.0004975955 | 0.0006746832 | 87 | 6 |
| inner_validation | VOL | ALL | ANY_log_loss | 5.079043e-07 | -0.002972336 | 0.002667265 | 87 | 6 |
| refit | GLOBAL | ALL | proper_loss | -0.0243693 | -0.02688884 | -0.02124946 | 2835 | 148 |
| refit | GLOBAL | ALL | ANY_Brier | -0.003183082 | -0.003702412 | -0.00250462 | 2835 | 148 |
| refit | GLOBAL | ALL | ANY_log_loss | -0.02434558 | -0.02693071 | -0.02121141 | 2835 | 148 |
| oos | GLOBAL | ALL | proper_loss | -0.0303845 | -0.04017422 | -0.02389732 | 208 | 12 |
| oos | GLOBAL | ALL | ANY_Brier | -0.004270521 | -0.006096532 | -0.003087794 | 208 | 12 |
| oos | GLOBAL | ALL | ANY_log_loss | -0.03025836 | -0.03977096 | -0.02390959 | 208 | 12 |
| refit | STOCK | ALL | proper_loss | 0.004674983 | 0.002851272 | 0.006811718 | 2835 | 148 |
| refit | STOCK | ALL | ANY_Brier | 0.0007355687 | 0.0003683708 | 0.001147729 | 2835 | 148 |
| refit | STOCK | ALL | ANY_log_loss | 0.004607707 | 0.002744906 | 0.006775761 | 2835 | 148 |
| oos | STOCK | ALL | proper_loss | 0.0007843456 | -0.004416029 | 0.004864784 | 208 | 12 |
| oos | STOCK | ALL | ANY_Brier | 2.948233e-05 | -0.0009923903 | 0.0009001356 | 208 | 12 |
| oos | STOCK | ALL | ANY_log_loss | 0.0006739014 | -0.004546491 | 0.004646191 | 208 | 12 |
| refit | VOL | ALL | proper_loss | -0.008112457 | -0.00932697 | -0.006498761 | 2835 | 148 |
| refit | VOL | ALL | ANY_Brier | -0.001487114 | -0.001802271 | -0.001093848 | 2835 | 148 |
| refit | VOL | ALL | ANY_log_loss | -0.008107833 | -0.009264797 | -0.006499306 | 2835 | 148 |
| oos | VOL | ALL | proper_loss | -0.008686682 | -0.01239916 | -0.005576202 | 208 | 12 |
| oos | VOL | ALL | ANY_Brier | -0.001604043 | -0.002492273 | -0.001000648 | 208 | 12 |
| oos | VOL | ALL | ANY_log_loss | -0.008503636 | -0.0122694 | -0.005319181 | 208 | 12 |


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
