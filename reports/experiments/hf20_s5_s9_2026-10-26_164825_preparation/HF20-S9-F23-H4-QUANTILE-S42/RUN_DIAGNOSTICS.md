# HF20-S9-F23-H4-QUANTILE-S42

TECHNICAL_PASS. All four roles verified; OOS remains exploratory.

| role | model | arm | rows | origins | sessions | optimized_loss | pinball_05 | pinball_50 | pinball_95 | coverage_05 | coverage_50 | coverage_95 | coverage90 | width_z | crossing_fraction | interval_score90_z | width_magnitude_rank_association | year |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | QUANTILE | 277920 | 13896 | 2547 | 0.2353779 | 0.1137856 | 0.4761313 | 0.1162168 | 0.04999963 | 0.5000688 | 0.950002 | 0.9000024 | 3.726072 | 0 | 4.600048 | -8.19816e-16 | 2023 |
| inner_validation | GLOBAL | QUANTILE | 9060 | 453 | 86 | 0.2353706 | 0.1140242 | 0.4799263 | 0.1121614 | 0.05376661 | 0.5000831 | 0.953062 | 0.8992954 | 3.726072 | 0 | 4.523712 | 7.542048e-16 | 2023 |
| inner_train | STOCK | QUANTILE | 277920 | 13896 | 2547 | 0.2303353 | 0.1070194 | 0.4760099 | 0.1079764 | 0.05004094 | 0.5000379 | 0.9500547 | 0.9000842 | 3.595014 | 0 | 4.299917 | 0.2430744 | 2023 |
| inner_validation | STOCK | QUANTILE | 9060 | 453 | 86 | 0.2318225 | 0.1082524 | 0.4800451 | 0.1071701 | 0.05625831 | 0.5001675 | 0.9509842 | 0.8947259 | 3.595014 | 0 | 4.308448 | 0.2123252 | 2023 |
| inner_train | VOL | QUANTILE | 277920 | 13896 | 2547 | 0.237428 | 0.1176395 | 0.4761313 | 0.1185131 | 0.0499964 | 0.5000688 | 0.9500026 | 0.9000062 | 3.999391 | 0 | 4.723052 | 0.2625218 | 2023 |
| inner_validation | VOL | QUANTILE | 9060 | 453 | 86 | 0.2374337 | 0.1173883 | 0.4799263 | 0.1149865 | 0.05638566 | 0.5000831 | 0.9537334 | 0.8973477 | 3.90929 | 0 | 4.647496 | 0.2648686 | 2023 |
| inner_train | NEURAL | QUANTILE | 277920 | 13896 | 2547 | 0.2302284 | 0.1069078 | 0.4757785 | 0.107999 | 0.05105895 | 0.495233 | 0.9462845 | 0.8952255 | 3.555394 | 0 | 4.298137 | 0.2606344 | 2023 |
| inner_validation | NEURAL | QUANTILE | 9060 | 453 | 86 | 0.2320044 | 0.1083087 | 0.4802434 | 0.107461 | 0.03808416 | 0.4917442 | 0.9715352 | 0.933451 | 3.896935 | 0 | 4.315394 | 0.2610394 | 2023 |
| refit | GLOBAL | QUANTILE | 287900 | 14395 | 2640 | 0.2352839 | 0.1137564 | 0.4760469 | 0.1160484 | 0.05000176 | 0.5000691 | 0.950002 | 0.9000003 | 3.724328 | 0 | 4.596096 | -8.514932e-16 | 2023 |
| oos | GLOBAL | QUANTILE | 17740 | 887 | 187 | 0.232657 | 0.1105779 | 0.4735949 | 0.1137981 | 0.04670805 | 0.5 | 0.9535791 | 0.906871 | 3.724328 | 0 | 4.48752 | -4.525996e-16 | 2023 |
| refit | STOCK | QUANTILE | 287900 | 14395 | 2640 | 0.2302835 | 0.1070048 | 0.475931 | 0.1079146 | 0.05002769 | 0.5000308 | 0.9500555 | 0.9000847 | 3.594225 | 0 | 4.298388 | 0.2420052 | 2023 |
| oos | STOCK | QUANTILE | 17740 | 887 | 187 | 0.2278684 | 0.1054671 | 0.4731002 | 0.1050378 | 0.04796028 | 0.4999618 | 0.9542806 | 0.9063203 | 3.594225 | 0 | 4.210098 | 0.2362551 | 2023 |
| refit | VOL | QUANTILE | 287900 | 14395 | 2640 | 0.237314 | 0.1175978 | 0.4760469 | 0.1182974 | 0.05000446 | 0.5000691 | 0.9500061 | 0.900008 | 3.995676 | 0 | 4.717904 | 0.2629221 | 2023 |
| oos | VOL | QUANTILE | 17740 | 887 | 187 | 0.2361902 | 0.1191921 | 0.4735949 | 0.1157836 | 0.05958811 | 0.5 | 0.9488675 | 0.8892793 | 3.91549 | 0 | 4.699514 | 0.2329445 | 2023 |
| refit | NEURAL | QUANTILE | 287900 | 14395 | 2640 | 0.2302058 | 0.1070096 | 0.4757625 | 0.1078455 | 0.04608897 | 0.4933558 | 0.9509607 | 0.9048718 | 3.636064 | 0 | 4.297101 | 0.2598918 | 2023 |
| oos | NEURAL | QUANTILE | 17740 | 887 | 187 | 0.228439 | 0.1060133 | 0.473737 | 0.1055667 | 0.04741788 | 0.4924433 | 0.9514852 | 0.9040674 | 3.585566 | 0 | 4.231599 | 0.2519414 | 2023 |


| role | reference | group | metric | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | GLOBAL | ALL | proper_loss | -0.005149475 | -0.005654562 | -0.004631259 | 2547 | 130 |
| inner_train | GLOBAL | ALL | pinball_05 | -0.00687774 | -0.007601368 | -0.006162907 | 2547 | 130 |
| inner_train | GLOBAL | ALL | pinball_50 | -0.0003528666 | -0.0004434327 | -0.0002505247 | 2547 | 130 |
| inner_train | GLOBAL | ALL | pinball_95 | -0.008217818 | -0.009299123 | -0.007237446 | 2547 | 130 |
| inner_validation | GLOBAL | ALL | proper_loss | -0.003366289 | -0.004514281 | -0.001734504 | 86 | 6 |
| inner_validation | GLOBAL | ALL | pinball_05 | -0.005715492 | -0.008704581 | -0.00256206 | 86 | 6 |
| inner_validation | GLOBAL | ALL | pinball_50 | 0.000317036 | -0.000241851 | 0.0008584156 | 86 | 6 |
| inner_validation | GLOBAL | ALL | pinball_95 | -0.00470041 | -0.007596892 | -0.001767362 | 86 | 6 |
| inner_train | STOCK | ALL | proper_loss | -0.0001068266 | -0.000420983 | 0.0002009882 | 2547 | 130 |
| inner_train | STOCK | ALL | pinball_05 | -0.0001115975 | -0.0005691836 | 0.0003546133 | 2547 | 130 |
| inner_train | STOCK | ALL | pinball_50 | -0.0002314583 | -0.0003594311 | -8.085188e-05 | 2547 | 130 |
| inner_train | STOCK | ALL | pinball_95 | 2.257601e-05 | -0.0005154968 | 0.00056701 | 2547 | 130 |
| inner_validation | STOCK | ALL | proper_loss | 0.0001818583 | -0.000904213 | 0.001210897 | 86 | 6 |
| inner_validation | STOCK | ALL | pinball_05 | 5.631601e-05 | -0.002847089 | 0.002761967 | 86 | 6 |
| inner_validation | STOCK | ALL | pinball_50 | 0.000198281 | -0.0006158955 | 0.0009215974 | 86 | 6 |
| inner_validation | STOCK | ALL | pinball_95 | 0.0002909779 | -0.001141194 | 0.001799317 | 86 | 6 |
| inner_train | VOL | ALL | proper_loss | -0.007199538 | -0.007794434 | -0.006585076 | 2547 | 130 |
| inner_train | VOL | ALL | pinball_05 | -0.01073169 | -0.0118292 | -0.009617193 | 2547 | 130 |
| inner_train | VOL | ALL | pinball_50 | -0.0003528666 | -0.0004434327 | -0.0002505247 | 2547 | 130 |
| inner_train | VOL | ALL | pinball_95 | -0.01051406 | -0.0115425 | -0.009531272 | 2547 | 130 |
| inner_validation | VOL | ALL | proper_loss | -0.005429353 | -0.007662231 | -0.003519388 | 86 | 6 |
| inner_validation | VOL | ALL | pinball_05 | -0.009079632 | -0.01529594 | -0.003498179 | 86 | 6 |
| inner_validation | VOL | ALL | pinball_50 | 0.000317036 | -0.000241851 | 0.0008584156 | 86 | 6 |
| inner_validation | VOL | ALL | pinball_95 | -0.007525462 | -0.009036374 | -0.005258655 | 86 | 6 |
| refit | GLOBAL | ALL | proper_loss | -0.005078067 | -0.005562907 | -0.004541915 | 2640 | 136 |
| refit | GLOBAL | ALL | pinball_05 | -0.006746814 | -0.007513017 | -0.005951428 | 2640 | 136 |
| refit | GLOBAL | ALL | pinball_50 | -0.0002844482 | -0.0003966698 | -0.0001625508 | 2640 | 136 |
| refit | GLOBAL | ALL | pinball_95 | -0.00820294 | -0.009143475 | -0.007171353 | 2640 | 136 |
| oos | GLOBAL | ALL | proper_loss | -0.004218004 | -0.005052793 | -0.003429115 | 187 | 12 |
| oos | GLOBAL | ALL | pinball_05 | -0.004564677 | -0.005995747 | -0.00337672 | 187 | 12 |
| oos | GLOBAL | ALL | pinball_50 | 0.0001420379 | -0.0003589163 | 0.0006397653 | 187 | 12 |
| oos | GLOBAL | ALL | pinball_95 | -0.008231373 | -0.01010427 | -0.006127645 | 187 | 12 |
| refit | STOCK | ALL | proper_loss | -7.761481e-05 | -0.0003928129 | 0.0002959202 | 2640 | 136 |
| refit | STOCK | ALL | pinball_05 | 4.786764e-06 | -0.000532574 | 0.0005830151 | 2640 | 136 |
| refit | STOCK | ALL | pinball_50 | -0.0001685292 | -0.0003161096 | -2.242324e-05 | 2640 | 136 |
| refit | STOCK | ALL | pinball_95 | -6.910196e-05 | -0.0005577164 | 0.0004758433 | 2640 | 136 |
| oos | STOCK | ALL | proper_loss | 0.0005705902 | -0.0001248772 | 0.001379479 | 187 | 12 |
| oos | STOCK | ALL | pinball_05 | 0.0005461646 | -0.0001479201 | 0.001628592 | 187 | 12 |
| oos | STOCK | ALL | pinball_50 | 0.0006367549 | 0.0002123135 | 0.001083039 | 187 | 12 |
| oos | STOCK | ALL | pinball_95 | 0.0005288513 | -0.0009909529 | 0.002053357 | 187 | 12 |
| refit | VOL | ALL | proper_loss | -0.007108198 | -0.007751293 | -0.00645527 | 2640 | 136 |
| refit | VOL | ALL | pinball_05 | -0.01058821 | -0.01161516 | -0.009460477 | 2640 | 136 |
| refit | VOL | ALL | pinball_50 | -0.0002844482 | -0.0003966698 | -0.0001625508 | 2640 | 136 |
| refit | VOL | ALL | pinball_95 | -0.01045193 | -0.01157919 | -0.009504099 | 2640 | 136 |
| oos | VOL | ALL | proper_loss | -0.007751238 | -0.009925296 | -0.005457214 | 187 | 12 |
| oos | VOL | ALL | pinball_05 | -0.01317889 | -0.01678397 | -0.009409766 | 187 | 12 |
| oos | VOL | ALL | pinball_50 | 0.0001420379 | -0.0003589163 | 0.0006397653 | 187 | 12 |
| oos | VOL | ALL | pinball_95 | -0.01021687 | -0.0133451 | -0.006801606 | 187 | 12 |


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
