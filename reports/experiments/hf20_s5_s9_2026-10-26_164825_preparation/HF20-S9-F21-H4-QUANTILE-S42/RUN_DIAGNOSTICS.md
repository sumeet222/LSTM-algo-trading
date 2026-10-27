# HF20-S9-F21-H4-QUANTILE-S42

TECHNICAL_PASS. All four roles verified; OOS remains exploratory.

| role | model | arm | rows | origins | sessions | optimized_loss | pinball_05 | pinball_50 | pinball_95 | coverage_05 | coverage_50 | coverage_95 | coverage90 | width_z | crossing_fraction | interval_score90_z | width_magnitude_rank_association | year |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | QUANTILE | 228980 | 11449 | 2100 | 0.236581 | 0.1148211 | 0.4777666 | 0.1171555 | 0.05000255 | 0.5000761 | 0.9500016 | 0.9000031 | 3.750404 | 0 | 4.639531 | -1.254097e-15 | 2021 |
| inner_validation | GLOBAL | QUANTILE | 13480 | 674 | 120 | 0.236978 | 0.1108657 | 0.4815138 | 0.1185545 | 0.04483135 | 0.5 | 0.946129 | 0.9012976 | 3.750404 | 0 | 4.588404 | 1.362688e-15 | 2021 |
| inner_train | STOCK | QUANTILE | 228980 | 11449 | 2100 | 0.2311973 | 0.107624 | 0.477557 | 0.108411 | 0.05006344 | 0.5000521 | 0.9500441 | 0.9000737 | 3.611791 | 0 | 4.3207 | 0.2497895 | 2021 |
| inner_validation | STOCK | QUANTILE | 13480 | 674 | 120 | 0.2327231 | 0.1066875 | 0.4810877 | 0.1103941 | 0.04646131 | 0.5006339 | 0.9439306 | 0.8974692 | 3.611791 | 0 | 4.341631 | 0.2432171 | 2021 |
| inner_train | VOL | QUANTILE | 228980 | 11449 | 2100 | 0.2386632 | 0.1187648 | 0.4777666 | 0.1194581 | 0.05000244 | 0.5000761 | 0.9500018 | 0.8999993 | 4.023697 | 0 | 4.764459 | 0.2610928 | 2021 |
| inner_validation | VOL | QUANTILE | 13480 | 674 | 120 | 0.2365716 | 0.1116137 | 0.4815138 | 0.1165872 | 0.04316567 | 0.5 | 0.9449692 | 0.9018036 | 3.892297 | 0 | 4.564019 | 0.3392029 | 2021 |
| inner_train | NEURAL | QUANTILE | 228980 | 11449 | 2100 | 0.2316927 | 0.1081716 | 0.4775359 | 0.1093707 | 0.05229416 | 0.4986739 | 0.9450452 | 0.892751 | 3.569996 | 0 | 4.350846 | 0.2532688 | 2021 |
| inner_validation | NEURAL | QUANTILE | 13480 | 674 | 120 | 0.233124 | 0.1072289 | 0.4811581 | 0.1109851 | 0.02032044 | 0.4962421 | 0.9664861 | 0.9461657 | 4.016822 | 0 | 4.364278 | 0.3261687 | 2021 |
| refit | GLOBAL | QUANTILE | 243420 | 12171 | 2227 | 0.2363636 | 0.1144811 | 0.4774401 | 0.1171697 | 0.05000187 | 0.5000718 | 0.9500026 | 0.9000039 | 3.746134 | 0 | 4.633016 | 1.771439e-15 | 2021 |
| oos | GLOBAL | QUANTILE | 19100 | 955 | 188 | 0.2311498 | 0.1092657 | 0.4730585 | 0.111125 | 0.04422556 | 0.500038 | 0.9571378 | 0.9129122 | 3.746134 | 0 | 4.407815 | 7.014488e-16 | 2021 |
| refit | STOCK | QUANTILE | 243420 | 12171 | 2227 | 0.231019 | 0.1074413 | 0.4772077 | 0.1084081 | 0.05004624 | 0.5000436 | 0.9500403 | 0.9000824 | 3.608485 | 0 | 4.316987 | 0.2495025 | 2021 |
| oos | STOCK | QUANTILE | 19100 | 955 | 188 | 0.228005 | 0.1048068 | 0.4736711 | 0.1055371 | 0.04631966 | 0.5010157 | 0.9522682 | 0.9059486 | 3.608485 | 0 | 4.206878 | 0.2228641 | 2021 |
| refit | VOL | QUANTILE | 243420 | 12171 | 2227 | 0.2382546 | 0.1181066 | 0.4774401 | 0.1192171 | 0.04999914 | 0.5000718 | 0.9500017 | 0.9000025 | 4.010871 | 0 | 4.746475 | 0.2658906 | 2021 |
| oos | VOL | QUANTILE | 19100 | 955 | 188 | 0.2334924 | 0.1146615 | 0.4730585 | 0.1127572 | 0.06200101 | 0.500038 | 0.9416331 | 0.8796321 | 3.72336 | 0 | 4.548374 | 0.2422427 | 2021 |
| refit | NEURAL | QUANTILE | 243420 | 12171 | 2227 | 0.2314985 | 0.1079898 | 0.4771852 | 0.1093206 | 0.05138581 | 0.5013662 | 0.9491875 | 0.8978017 | 3.609706 | 0 | 4.346209 | 0.2545238 | 2021 |
| oos | NEURAL | QUANTILE | 19100 | 955 | 188 | 0.228354 | 0.1054652 | 0.4733992 | 0.1061975 | 0.03900393 | 0.502602 | 0.9662373 | 0.9272334 | 3.772864 | 0 | 4.233254 | 0.2493223 | 2021 |


| role | reference | group | metric | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | ALL | proper_loss | -0.004888312 | -0.005435054 | -0.004315886 | 2100 | 106 |
| inner_train | GLOBAL | ALL | pinball_05 | -0.006649446 | -0.007456787 | -0.00575297 | 2100 | 106 |
| inner_train | GLOBAL | ALL | pinball_50 | -0.0002306925 | -0.0003448104 | -0.0001196618 | 2100 | 106 |
| inner_train | GLOBAL | ALL | pinball_95 | -0.007784797 | -0.00889494 | -0.006748231 | 2100 | 106 |
| inner_validation | GLOBAL | ALL | proper_loss | -0.003853986 | -0.004995693 | -0.002769285 | 120 | 6 |
| inner_validation | GLOBAL | ALL | pinball_05 | -0.003636841 | -0.005677012 | -0.001961008 | 120 | 6 |
| inner_validation | GLOBAL | ALL | pinball_50 | -0.0003556899 | -0.001003999 | 0.0002499306 | 120 | 6 |
| inner_validation | GLOBAL | ALL | pinball_95 | -0.007569428 | -0.01169469 | -0.004331268 | 120 | 6 |
| inner_train | STOCK | ALL | proper_loss | 0.00049541 | 0.0001200966 | 0.0008778541 | 2100 | 106 |
| inner_train | STOCK | ALL | pinball_05 | 0.0005476752 | -4.412976e-05 | 0.001142743 | 2100 | 106 |
| inner_train | STOCK | ALL | pinball_50 | -2.108473e-05 | -0.0002157491 | 0.0001761908 | 2100 | 106 |
| inner_train | STOCK | ALL | pinball_95 | 0.0009596395 | 0.0002900698 | 0.00161242 | 2100 | 106 |
| inner_validation | STOCK | ALL | proper_loss | 0.0004009299 | -0.000364472 | 0.001100518 | 120 | 6 |
| inner_validation | STOCK | ALL | pinball_05 | 0.0005413707 | -0.000239071 | 0.001184868 | 120 | 6 |
| inner_validation | STOCK | ALL | pinball_50 | 7.042518e-05 | -0.0006598986 | 0.0007820158 | 120 | 6 |
| inner_validation | STOCK | ALL | pinball_95 | 0.0005909939 | -0.001687775 | 0.002597629 | 120 | 6 |
| inner_train | VOL | ALL | proper_loss | -0.006970443 | -0.007667792 | -0.00618456 | 2100 | 106 |
| inner_train | VOL | ALL | pinball_05 | -0.0105932 | -0.01188313 | -0.009381811 | 2100 | 106 |
| inner_train | VOL | ALL | pinball_50 | -0.0002306925 | -0.0003448104 | -0.0001196618 | 2100 | 106 |
| inner_train | VOL | ALL | pinball_95 | -0.01008743 | -0.0112162 | -0.008842528 | 2100 | 106 |
| inner_validation | VOL | ALL | proper_loss | -0.003447575 | -0.007088254 | -0.0002438038 | 120 | 6 |
| inner_validation | VOL | ALL | pinball_05 | -0.004384889 | -0.009723308 | 0.0003482446 | 120 | 6 |
| inner_validation | VOL | ALL | pinball_50 | -0.0003556899 | -0.001003999 | 0.0002499306 | 120 | 6 |
| inner_validation | VOL | ALL | pinball_95 | -0.005602148 | -0.01089184 | -0.001186569 | 120 | 6 |
| refit | GLOBAL | ALL | proper_loss | -0.004865089 | -0.005347334 | -0.004272333 | 2227 | 112 |
| refit | GLOBAL | ALL | pinball_05 | -0.006491274 | -0.007326222 | -0.005577084 | 2227 | 112 |
| refit | GLOBAL | ALL | pinball_50 | -0.0002548978 | -0.0003729561 | -0.0001416391 | 2227 | 112 |
| refit | GLOBAL | ALL | pinball_95 | -0.007849097 | -0.008895548 | -0.006621541 | 2227 | 112 |
| oos | GLOBAL | ALL | proper_loss | -0.002795806 | -0.004094126 | -0.001506603 | 188 | 12 |
| oos | GLOBAL | ALL | pinball_05 | -0.003800529 | -0.006025181 | -0.001665863 | 188 | 12 |
| oos | GLOBAL | ALL | pinball_50 | 0.0003406439 | -0.0001085258 | 0.0008545943 | 188 | 12 |
| oos | GLOBAL | ALL | pinball_95 | -0.004927534 | -0.007986302 | -0.002119589 | 188 | 12 |
| refit | STOCK | ALL | proper_loss | 0.0004795104 | 0.0001327228 | 0.0009368438 | 2227 | 112 |
| refit | STOCK | ALL | pinball_05 | 0.0005485452 | 3.218169e-06 | 0.001248956 | 2227 | 112 |
| refit | STOCK | ALL | pinball_50 | -2.253245e-05 | -0.000212485 | 0.0001686773 | 2227 | 112 |
| refit | STOCK | ALL | pinball_95 | 0.0009125185 | 0.0003100113 | 0.001653521 | 2227 | 112 |
| oos | STOCK | ALL | proper_loss | 0.0003489634 | -0.000684052 | 0.001563258 | 188 | 12 |
| oos | STOCK | ALL | pinball_05 | 0.0006583589 | -0.0009541141 | 0.002269193 | 188 | 12 |
| oos | STOCK | ALL | pinball_50 | -0.0002718983 | -0.001041778 | 0.0006652386 | 188 | 12 |
| oos | STOCK | ALL | pinball_95 | 0.0006604295 | -0.001318656 | 0.002906071 | 188 | 12 |
| refit | VOL | ALL | proper_loss | -0.006756071 | -0.007408972 | -0.005945751 | 2227 | 112 |
| refit | VOL | ALL | pinball_05 | -0.0101168 | -0.01116779 | -0.008796201 | 2227 | 112 |
| refit | VOL | ALL | pinball_50 | -0.0002548978 | -0.0003729561 | -0.0001416391 | 2227 | 112 |
| refit | VOL | ALL | pinball_95 | -0.009896519 | -0.01105637 | -0.008591252 | 2227 | 112 |
| oos | VOL | ALL | proper_loss | -0.005138455 | -0.006674878 | -0.003827783 | 188 | 12 |
| oos | VOL | ALL | pinball_05 | -0.009196366 | -0.01234541 | -0.006676097 | 188 | 12 |
| oos | VOL | ALL | pinball_50 | 0.0003406439 | -0.0001085258 | 0.0008545943 | 188 | 12 |
| oos | VOL | ALL | pinball_95 | -0.006559643 | -0.009273797 | -0.004533764 | 188 | 12 |


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
