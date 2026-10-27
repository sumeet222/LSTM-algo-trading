# HF20-S5-F24-H4-META-T2R-S42

TECHNICAL_PASS. All four roles verified; OOS remains exploratory.

| role | model | arm | rows | origins | sessions | optimized_loss | daily_ic | original_TG20_mse | year | defined_origin_fraction | defined_ic_sessions | origin_ic | pair_concordance | normalized_rank_mse | top4 | bottom4 | score_sd | pair_tie_rate | actual_objective | score_units | phase | inverse_count | original_common_mse | original_centered_mse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | NEURAL | META-T2R | 298900 | 14945 | 2740 | 1.3489 | 0.04039565 | 4.535953 | 2024 | 1 | 2740 | 0.03877199 | 0.5142313 | 0.7070734 | 0.2458207 | 0.2098366 | 0.03456291 | 0 | 1.3489 | asinh TG20 | inner | 1 | 0.1733534 | 4.3626 |
| inner_validation | NEURAL | META-T2R | 7000 | 350 | 87 | 1.310291 | 0.03431514 | 3.676677 | 2024 | 1 | 87 | 0.02910849 | 0.5118507 | 0.7115573 | 0.256616 | 0.1951697 | 0.03487045 | 0 | 1.310291 | asinh TG20 | inner | 1 | 0.1307005 | 3.545976 |
| refit | NEURAL | META-T2R | 306640 | 15332 | 2835 | 1.347518 | 0.03848807 | 4.504062 | 2024 | 1 | 2835 | 0.03612494 | 0.5135238 | 0.7084791 | 0.2571103 | 0.1989099 | 0.03735539 | 0 | 1.347518 | asinh TG20 | refit | 1 | 0.1719052 | 4.332157 |
| oos | NEURAL | META-T2R | 19820 | 991 | 208 | 1.394347 | -0.005277992 | 4.752201 | 2024 | 1 | 208 | -0.01087758 | 0.4983441 | 0.7407305 | 0.2325979 | 0.1768258 | 0.03713747 | 0 | 1.394347 | asinh TG20 | refit | 1 | 0.1933009 | 4.5589 |


| role | reference | group | origins | model_IC | reference_IC | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | T2R | ALL_MATCHED | 14945 | 0.04039565 | 0.07865822 | -0.03826258 | -0.04617391 | -0.02957799 | 2740 | 142 |
| inner_train | T2R | OLD_MORNING | 4612 | 0.03503009 | 0.06917486 | -0.03414477 | -0.04460233 | -0.02346378 | 2621 | 141 |
| inner_train | T2R | OPENING | 1935 | 0.04559695 | 0.0874319 | -0.04183495 | -0.05384417 | -0.02925272 | 1935 | 141 |
| inner_train | T2R | AFTERNOON | 8398 | 0.04238865 | 0.07635109 | -0.03396244 | -0.04329938 | -0.02348367 | 2693 | 141 |
| inner_train | T2R | INTRADAY | 6495 | 0.03699781 | 0.07366349 | -0.03666568 | -0.04517401 | -0.02844591 | 2657 | 142 |
| inner_train | T2R | OVERNIGHT | 8450 | 0.04247089 | 0.07679863 | -0.03432774 | -0.04380483 | -0.02364746 | 2697 | 141 |
| inner_train | N1 | ALL_MATCHED | 14945 | 0.04039565 | -0.01113097 | 0.05152661 | 0.04264634 | 0.06068582 | 2740 | 142 |
| inner_train | N1 | OLD_MORNING | 4612 | 0.03503009 | -0.004491422 | 0.03952151 | 0.02715226 | 0.05192768 | 2621 | 141 |
| inner_train | N1 | OPENING | 1935 | 0.04559695 | -0.0117703 | 0.05736725 | 0.04118582 | 0.07581917 | 1935 | 141 |
| inner_train | N1 | AFTERNOON | 8398 | 0.04238865 | -0.01537054 | 0.05775918 | 0.04806009 | 0.06872104 | 2693 | 141 |
| inner_train | N1 | INTRADAY | 6495 | 0.03699781 | -0.006063487 | 0.0430613 | 0.03111255 | 0.05472882 | 2657 | 142 |
| inner_train | N1 | OVERNIGHT | 8450 | 0.04247089 | -0.01499424 | 0.05746513 | 0.04792055 | 0.06839635 | 2697 | 141 |
| inner_train | P | ALL_MATCHED | 14945 | 0.04039565 | 0.02663377 | 0.01376188 | 0.001307482 | 0.02460698 | 2740 | 142 |
| inner_train | P | OLD_MORNING | 4612 | 0.03503009 | 0.009681917 | 0.02534817 | 0.01060696 | 0.04015597 | 2621 | 141 |
| inner_train | P | OPENING | 1935 | 0.04559695 | 0.01545113 | 0.03014583 | 0.01252665 | 0.04742869 | 1935 | 141 |
| inner_train | P | AFTERNOON | 8398 | 0.04238865 | 0.03672588 | 0.005662765 | -0.007482877 | 0.01975415 | 2693 | 141 |
| inner_train | P | INTRADAY | 6495 | 0.03699781 | 0.01026386 | 0.02673396 | 0.01209651 | 0.03906456 | 2657 | 142 |
| inner_train | P | OVERNIGHT | 8450 | 0.04247089 | 0.03690916 | 0.005561729 | -0.007516157 | 0.01971715 | 2697 | 141 |
| inner_validation | T2R | ALL_MATCHED | 350 | 0.03431514 | 0.004322835 | 0.0299923 | -0.02458827 | 0.08994327 | 87 | 6 |
| inner_validation | T2R | OLD_MORNING | 111 | 0.04283682 | 0.0647531 | -0.02191628 | -0.06512929 | 0.01407063 | 74 | 6 |
| inner_validation | T2R | OPENING | 41 | -0.009132588 | -0.06385476 | 0.05472217 | -0.08091382 | 0.188587 | 41 | 6 |
| inner_validation | T2R | AFTERNOON | 198 | 0.01936404 | -0.02495927 | 0.04432331 | -0.006063122 | 0.1050642 | 80 | 6 |
| inner_validation | T2R | INTRADAY | 152 | 0.02558319 | 0.02330506 | 0.002278131 | -0.05043131 | 0.05660447 | 78 | 6 |
| inner_validation | T2R | OVERNIGHT | 198 | 0.01936404 | -0.02495927 | 0.04432331 | -0.006063122 | 0.1050642 | 80 | 6 |
| inner_validation | N1 | ALL_MATCHED | 350 | 0.03431514 | 0.0131476 | 0.02116754 | -0.04287938 | 0.1075232 | 87 | 6 |
| inner_validation | N1 | OLD_MORNING | 111 | 0.04283682 | 0.03002417 | 0.01281265 | -0.1010961 | 0.1925198 | 74 | 6 |
| inner_validation | N1 | OPENING | 41 | -0.009132588 | 0.05216475 | -0.06129733 | -0.1627167 | 0.02850565 | 41 | 6 |
| inner_validation | N1 | AFTERNOON | 198 | 0.01936404 | 0.00781092 | 0.01155312 | -0.05039625 | 0.07943442 | 80 | 6 |
| inner_validation | N1 | INTRADAY | 152 | 0.02558319 | 0.02974994 | -0.004166756 | -0.1001041 | 0.1374344 | 78 | 6 |
| inner_validation | N1 | OVERNIGHT | 198 | 0.01936404 | 0.00781092 | 0.01155312 | -0.05039625 | 0.07943442 | 80 | 6 |
| inner_validation | P | ALL_MATCHED | 350 | 0.03431514 | 0.01979193 | 0.01452321 | -0.02164994 | 0.07042395 | 87 | 6 |
| inner_validation | P | OLD_MORNING | 111 | 0.04283682 | 0.08952449 | -0.04668767 | -0.1237604 | 0.04394886 | 74 | 6 |
| inner_validation | P | OPENING | 41 | -0.009132588 | 0.03157895 | -0.04071153 | -0.1181325 | 0.04688191 | 41 | 6 |
| inner_validation | P | AFTERNOON | 198 | 0.01936404 | -0.01107769 | 0.03044173 | -0.04158972 | 0.09292113 | 80 | 6 |
| inner_validation | P | INTRADAY | 152 | 0.02558319 | 0.05811644 | -0.03253326 | -0.09043153 | 0.02931964 | 78 | 6 |
| inner_validation | P | OVERNIGHT | 198 | 0.01936404 | -0.01107769 | 0.03044173 | -0.04158972 | 0.09292113 | 80 | 6 |
| refit | T2R | ALL_MATCHED | 15332 | 0.03848807 | 0.07364212 | -0.03515405 | -0.04570849 | -0.0244536 | 2835 | 148 |
| refit | T2R | OLD_MORNING | 4736 | 0.03065213 | 0.06892186 | -0.03826972 | -0.05041849 | -0.02565567 | 2703 | 147 |
| refit | T2R | OPENING | 1980 | 0.03926783 | 0.08686538 | -0.04759754 | -0.06209274 | -0.03330395 | 1980 | 147 |
| refit | T2R | AFTERNOON | 8616 | 0.04143628 | 0.06913284 | -0.02769656 | -0.03875125 | -0.01512637 | 2782 | 147 |
| refit | T2R | INTRADAY | 6662 | 0.03296908 | 0.07258508 | -0.03961599 | -0.05147474 | -0.02885645 | 2743 | 148 |
| refit | T2R | OVERNIGHT | 8670 | 0.04122808 | 0.06947345 | -0.02824537 | -0.03951899 | -0.01566764 | 2786 | 147 |
| refit | N1 | ALL_MATCHED | 15332 | 0.03848807 | -0.009947299 | 0.04843537 | 0.03861259 | 0.05869658 | 2835 | 148 |
| refit | N1 | OLD_MORNING | 4736 | 0.03065213 | -0.00334376 | 0.03399589 | 0.02083836 | 0.04695093 | 2703 | 147 |
| refit | N1 | OPENING | 1980 | 0.03926783 | -0.009877573 | 0.04914541 | 0.03382733 | 0.06516757 | 1980 | 147 |
| refit | N1 | AFTERNOON | 8616 | 0.04143628 | -0.01428185 | 0.05571813 | 0.04373049 | 0.06807237 | 2782 | 147 |
| refit | N1 | INTRADAY | 6662 | 0.03296908 | -0.004665739 | 0.03763482 | 0.02668529 | 0.05054823 | 2743 | 148 |
| refit | N1 | OVERNIGHT | 8670 | 0.04122808 | -0.01399803 | 0.05522611 | 0.04320844 | 0.06727009 | 2786 | 147 |
| refit | P | ALL_MATCHED | 15332 | 0.03848807 | 0.02662051 | 0.01186756 | 0.0009758228 | 0.02420351 | 2835 | 148 |
| refit | P | OLD_MORNING | 4736 | 0.03065213 | 0.01227429 | 0.01837784 | 0.005277639 | 0.03243145 | 2703 | 147 |
| refit | P | OPENING | 1980 | 0.03926783 | 0.01686121 | 0.02240662 | 0.003907476 | 0.04152424 | 1980 | 147 |
| refit | P | AFTERNOON | 8616 | 0.04143628 | 0.03534049 | 0.006095794 | -0.005520416 | 0.01897297 | 2782 | 147 |
| refit | P | INTRADAY | 6662 | 0.03296908 | 0.01228043 | 0.02068865 | 0.007078461 | 0.03433816 | 2743 | 148 |
| refit | P | OVERNIGHT | 8670 | 0.04122808 | 0.03554671 | 0.005681375 | -0.006306663 | 0.01878848 | 2786 | 147 |
| oos | T2R | ALL_MATCHED | 991 | -0.005277992 | -0.01184016 | 0.006562166 | -0.01862993 | 0.03382053 | 208 | 12 |
| oos | T2R | OLD_MORNING | 311 | -0.03050957 | -0.02780347 | -0.002706094 | -0.03784781 | 0.04009928 | 187 | 12 |
| oos | T2R | OPENING | 114 | -0.03461285 | -0.006173328 | -0.02843952 | -0.07211293 | 0.02111774 | 114 | 12 |
| oos | T2R | AFTERNOON | 566 | 0.009573738 | -0.008707612 | 0.01828135 | -0.01275811 | 0.0436594 | 201 | 12 |
| oos | T2R | INTRADAY | 421 | -0.02800505 | -0.0261461 | -0.001858942 | -0.02814831 | 0.03204746 | 192 | 12 |
| oos | T2R | OVERNIGHT | 570 | 0.009742388 | -0.008984799 | 0.01872719 | -0.01142749 | 0.04411015 | 203 | 12 |
| oos | N1 | ALL_MATCHED | 991 | -0.005277992 | -0.002945501 | -0.00233249 | -0.04900369 | 0.03793108 | 208 | 12 |
| oos | N1 | OLD_MORNING | 311 | -0.03050957 | 0.009875831 | -0.0403854 | -0.09720193 | 0.006384329 | 187 | 12 |
| oos | N1 | OPENING | 114 | -0.03461285 | 0.01550274 | -0.05011559 | -0.1308336 | 0.02157246 | 114 | 12 |
| oos | N1 | AFTERNOON | 566 | 0.009573738 | -0.01289049 | 0.02246423 | -0.02587477 | 0.07206554 | 201 | 12 |
| oos | N1 | INTRADAY | 421 | -0.02800505 | 0.008157924 | -0.03616297 | -0.08808694 | 0.00793508 | 192 | 12 |
| oos | N1 | OVERNIGHT | 570 | 0.009742388 | -0.01166369 | 0.02140608 | -0.02691111 | 0.07117181 | 203 | 12 |
| oos | P | ALL_MATCHED | 991 | -0.005277992 | -0.01267275 | 0.007394756 | -0.03079243 | 0.0500931 | 208 | 12 |
| oos | P | OLD_MORNING | 311 | -0.03050957 | 0.02041288 | -0.05092245 | -0.08929868 | 0.001293791 | 187 | 12 |
| oos | P | OPENING | 114 | -0.03461285 | -0.02638174 | -0.008231104 | -0.07214401 | 0.05380582 | 114 | 12 |
| oos | P | AFTERNOON | 566 | 0.009573738 | -0.01666089 | 0.02623463 | -0.01802273 | 0.07825279 | 201 | 12 |
| oos | P | INTRADAY | 421 | -0.02800505 | -0.002916589 | -0.02508846 | -0.06422298 | 0.02497192 | 192 | 12 |
| oos | P | OVERNIGHT | 570 | 0.009742388 | -0.01170768 | 0.02145007 | -0.02668345 | 0.07495444 | 203 | 12 |


All diagnostic files:

- [F24_inner_recipe.json](F24_inner_recipe.json)
- [F24_inner_train_indices.csv](F24_inner_train_indices.csv)
- [F24_inner_validation_indices.csv](F24_inner_validation_indices.csv)
- [F24_oos_indices.csv](F24_oos_indices.csv)
- [F24_refit_indices.csv](F24_refit_indices.csv)
- [F24_refit_recipe.json](F24_refit_recipe.json)
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
- [inner_target_recipe.json](inner_target_recipe.json)
- [inner_train_cohorts.csv](inner_train_cohorts.csv)
- [inner_train_metrics.json](inner_train_metrics.json)
- [inner_train_scores.parquet](inner_train_scores.parquet)
- [inner_train_strata.csv](inner_train_strata.csv)
- [inner_validation_cohorts.csv](inner_validation_cohorts.csv)
- [inner_validation_metrics.json](inner_validation_metrics.json)
- [inner_validation_scores.parquet](inner_validation_scores.parquet)
- [inner_validation_strata.csv](inner_validation_strata.csv)
- [matched_baseline_differences.csv](matched_baseline_differences.csv)
- [model_and_control_metrics.csv](model_and_control_metrics.csv)
- [oos_cohorts.csv](oos_cohorts.csv)
- [oos_metrics.json](oos_metrics.json)
- [oos_scores.parquet](oos_scores.parquet)
- [oos_strata.csv](oos_strata.csv)
- [ranking/NUMERICAL_DIAGNOSTICS_PASS.json](ranking/NUMERICAL_DIAGNOSTICS_PASS.json)
- [ranking/calibration_binding.json](ranking/calibration_binding.json)
- [ranking/category_and_anchor_metrics.csv](ranking/category_and_anchor_metrics.csv)
- [ranking/inner_train_cohorts.csv](ranking/inner_train_cohorts.csv)
- [ranking/inner_train_energy_and_objective_cohorts.csv](ranking/inner_train_energy_and_objective_cohorts.csv)
- [ranking/inner_train_error_ranked_cohorts.csv](ranking/inner_train_error_ranked_cohorts.csv)
- [ranking/inner_train_matched_category_sessions.csv](ranking/inner_train_matched_category_sessions.csv)
- [ranking/inner_train_metrics.json](ranking/inner_train_metrics.json)
- [ranking/inner_train_month.csv](ranking/inner_train_month.csv)
- [ranking/inner_train_origins.csv](ranking/inner_train_origins.csv)
- [ranking/inner_train_paired_cohort_difficulty.csv](ranking/inner_train_paired_cohort_difficulty.csv)
- [ranking/inner_train_scores.parquet](ranking/inner_train_scores.parquet)
- [ranking/inner_train_slot.csv](ranking/inner_train_slot.csv)
- [ranking/inner_train_stock_month_sector_quality.csv](ranking/inner_train_stock_month_sector_quality.csv)
- [ranking/inner_train_stock_quality.csv](ranking/inner_train_stock_quality.csv)
- [ranking/inner_train_thresholds.json](ranking/inner_train_thresholds.json)
- [ranking/inner_validation_cohorts.csv](ranking/inner_validation_cohorts.csv)
- [ranking/inner_validation_energy_and_objective_cohorts.csv](ranking/inner_validation_energy_and_objective_cohorts.csv)
- [ranking/inner_validation_error_ranked_cohorts.csv](ranking/inner_validation_error_ranked_cohorts.csv)
- [ranking/inner_validation_matched_category_sessions.csv](ranking/inner_validation_matched_category_sessions.csv)
- [ranking/inner_validation_metrics.json](ranking/inner_validation_metrics.json)
- [ranking/inner_validation_month.csv](ranking/inner_validation_month.csv)
- [ranking/inner_validation_origins.csv](ranking/inner_validation_origins.csv)
- [ranking/inner_validation_paired_cohort_difficulty.csv](ranking/inner_validation_paired_cohort_difficulty.csv)
- [ranking/inner_validation_scores.parquet](ranking/inner_validation_scores.parquet)
- [ranking/inner_validation_slot.csv](ranking/inner_validation_slot.csv)
- [ranking/inner_validation_stock_month_sector_quality.csv](ranking/inner_validation_stock_month_sector_quality.csv)
- [ranking/inner_validation_stock_quality.csv](ranking/inner_validation_stock_quality.csv)
- [ranking/inner_validation_thresholds.json](ranking/inner_validation_thresholds.json)
- [ranking/oos_cohorts.csv](ranking/oos_cohorts.csv)
- [ranking/oos_energy_and_objective_cohorts.csv](ranking/oos_energy_and_objective_cohorts.csv)
- [ranking/oos_error_ranked_cohorts.csv](ranking/oos_error_ranked_cohorts.csv)
- [ranking/oos_matched_category_sessions.csv](ranking/oos_matched_category_sessions.csv)
- [ranking/oos_metrics.json](ranking/oos_metrics.json)
- [ranking/oos_month.csv](ranking/oos_month.csv)
- [ranking/oos_origins.csv](ranking/oos_origins.csv)
- [ranking/oos_paired_cohort_difficulty.csv](ranking/oos_paired_cohort_difficulty.csv)
- [ranking/oos_scores.parquet](ranking/oos_scores.parquet)
- [ranking/oos_slot.csv](ranking/oos_slot.csv)
- [ranking/oos_stock_month_sector_quality.csv](ranking/oos_stock_month_sector_quality.csv)
- [ranking/oos_stock_quality.csv](ranking/oos_stock_quality.csv)
- [ranking/oos_thresholds.json](ranking/oos_thresholds.json)
- [ranking/refit_binding.json](ranking/refit_binding.json)
- [ranking/refit_cohorts.csv](ranking/refit_cohorts.csv)
- [ranking/refit_energy_and_objective_cohorts.csv](ranking/refit_energy_and_objective_cohorts.csv)
- [ranking/refit_error_ranked_cohorts.csv](ranking/refit_error_ranked_cohorts.csv)
- [ranking/refit_matched_category_sessions.csv](ranking/refit_matched_category_sessions.csv)
- [ranking/refit_metrics.json](ranking/refit_metrics.json)
- [ranking/refit_month.csv](ranking/refit_month.csv)
- [ranking/refit_origins.csv](ranking/refit_origins.csv)
- [ranking/refit_paired_cohort_difficulty.csv](ranking/refit_paired_cohort_difficulty.csv)
- [ranking/refit_scores.parquet](ranking/refit_scores.parquet)
- [ranking/refit_slot.csv](ranking/refit_slot.csv)
- [ranking/refit_stock_month_sector_quality.csv](ranking/refit_stock_month_sector_quality.csv)
- [ranking/refit_stock_quality.csv](ranking/refit_stock_quality.csv)
- [ranking/refit_thresholds.json](ranking/refit_thresholds.json)
- [refit_001.json](refit_001.json)
- [refit_001_batches.csv](refit_001_batches.csv)
- [refit_001_gradients.csv](refit_001_gradients.csv)
- [refit_002.json](refit_002.json)
- [refit_002_batches.csv](refit_002_batches.csv)
- [refit_002_gradients.csv](refit_002_gradients.csv)
- [refit_binding.json](refit_binding.json)
- [refit_cohorts.csv](refit_cohorts.csv)
- [refit_final.pt](refit_final.pt)
- [refit_metrics.json](refit_metrics.json)
- [refit_scores.parquet](refit_scores.parquet)
- [refit_strata.csv](refit_strata.csv)
- [refit_target_recipe.json](refit_target_recipe.json)
