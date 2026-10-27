# HF20-S5-F23-H4-META-T2R-S42

TECHNICAL_PASS. All four roles verified; OOS remains exploratory.

| role | model | arm | rows | origins | sessions | optimized_loss | daily_ic | original_TG20_mse | year | defined_origin_fraction | defined_ic_sessions | origin_ic | pair_concordance | normalized_rank_mse | top4 | bottom4 | score_sd | pair_tie_rate | actual_objective | score_units | phase | inverse_count | original_common_mse | original_centered_mse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | NEURAL | META-T2R | 277920 | 13896 | 2547 | 1.350631 | 0.04432957 | 4.593403 | 2023 | 1 | 2547 | 0.0412842 | 0.5157397 | 0.7041746 | 0.2414654 | 0.2167797 | 0.04590599 | 0 | 1.350631 | asinh TG20 | inner | 1 | 0.1754757 | 4.417927 |
| inner_validation | NEURAL | META-T2R | 9060 | 453 | 86 | 1.350076 | 0.01545584 | 3.80901 | 2023 | 1 | 86 | 0.01319719 | 0.5050546 | 0.7254528 | 0.2255053 | 0.1968785 | 0.03952607 | 0 | 1.350076 | asinh TG20 | inner | 1 | 0.1381921 | 3.670818 |
| refit | NEURAL | META-T2R | 287900 | 14395 | 2640 | 1.34928 | 0.0465916 | 4.556263 | 2023 | 1 | 2640 | 0.04401196 | 0.5165137 | 0.7025079 | 0.2445157 | 0.2195107 | 0.04290686 | 0 | 1.34928 | asinh TG20 | refit | 1 | 0.1738434 | 4.38242 |
| oos | NEURAL | META-T2R | 17740 | 887 | 187 | 1.322844 | 0.02681478 | 3.841714 | 2023 | 1 | 187 | 0.03027102 | 0.5101571 | 0.7170833 | 0.2483957 | 0.1979023 | 0.04240031 | 0 | 1.322844 | asinh TG20 | refit | 1 | 0.1457348 | 3.695979 |


| role | reference | group | origins | model_IC | reference_IC | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | T2R | ALL_MATCHED | 13896 | 0.04432957 | 0.1362147 | -0.09188517 | -0.1022391 | -0.0816822 | 2547 | 130 |
| inner_train | T2R | OLD_MORNING | 4278 | 0.03777296 | 0.1091404 | -0.07136739 | -0.08218631 | -0.05876787 | 2433 | 129 |
| inner_train | T2R | OPENING | 1808 | 0.05449612 | 0.1418688 | -0.08737268 | -0.09889142 | -0.07429735 | 1808 | 129 |
| inner_train | T2R | AFTERNOON | 7810 | 0.04313548 | 0.1420989 | -0.09896338 | -0.1112178 | -0.08586899 | 2502 | 129 |
| inner_train | T2R | INTRADAY | 6036 | 0.04239983 | 0.1183018 | -0.07590194 | -0.08604336 | -0.06698779 | 2467 | 130 |
| inner_train | T2R | OVERNIGHT | 7860 | 0.04338816 | 0.1420807 | -0.09869251 | -0.1109098 | -0.08609864 | 2506 | 129 |
| inner_train | N1 | ALL_MATCHED | 13896 | 0.04432957 | -0.01219375 | 0.05652333 | 0.04674737 | 0.06527913 | 2547 | 130 |
| inner_train | N1 | OLD_MORNING | 4278 | 0.03777296 | -0.004780248 | 0.04255321 | 0.02865232 | 0.05508252 | 2433 | 129 |
| inner_train | N1 | OPENING | 1808 | 0.05449612 | -0.01202794 | 0.06652406 | 0.05006645 | 0.08435481 | 1808 | 129 |
| inner_train | N1 | AFTERNOON | 7810 | 0.04313548 | -0.01683788 | 0.05997335 | 0.04659058 | 0.07255794 | 2502 | 129 |
| inner_train | N1 | INTRADAY | 6036 | 0.04239983 | -0.006095193 | 0.04849503 | 0.03597308 | 0.05913849 | 2467 | 130 |
| inner_train | N1 | OVERNIGHT | 7860 | 0.04338816 | -0.01643856 | 0.05982673 | 0.04616025 | 0.07219397 | 2506 | 129 |
| inner_train | P | ALL_MATCHED | 13896 | 0.04432957 | 0.02508691 | 0.01924266 | 0.005899112 | 0.03268743 | 2547 | 130 |
| inner_train | P | OLD_MORNING | 4278 | 0.03777296 | 0.007226171 | 0.03054679 | 0.01317685 | 0.04666781 | 2433 | 129 |
| inner_train | P | OPENING | 1808 | 0.05449612 | 0.01322146 | 0.04127466 | 0.02257237 | 0.06116432 | 1808 | 129 |
| inner_train | P | AFTERNOON | 7810 | 0.04313548 | 0.03599123 | 0.007144246 | -0.007997313 | 0.02265526 | 2502 | 129 |
| inner_train | P | INTRADAY | 6036 | 0.04239983 | 0.007967013 | 0.03443282 | 0.01933809 | 0.04906701 | 2467 | 130 |
| inner_train | P | OVERNIGHT | 7860 | 0.04338816 | 0.0361589 | 0.007229267 | -0.0079768 | 0.0229132 | 2506 | 129 |
| inner_validation | T2R | ALL_MATCHED | 453 | 0.01545584 | 0.06027298 | -0.04481714 | -0.08562684 | 0.002599873 | 86 | 6 |
| inner_validation | T2R | OLD_MORNING | 144 | 0.007347876 | 0.04915019 | -0.04180231 | -0.09187997 | 0.008163027 | 81 | 6 |
| inner_validation | T2R | OPENING | 61 | 0.05139899 | 0.07822014 | -0.02682115 | -0.09421629 | 0.04367738 | 61 | 6 |
| inner_validation | T2R | AFTERNOON | 248 | 0.02326751 | 0.05716248 | -0.03389498 | -0.08624263 | 0.02278272 | 83 | 6 |
| inner_validation | T2R | INTRADAY | 203 | 0.01685058 | 0.05684608 | -0.03999549 | -0.07213439 | -0.009282491 | 82 | 6 |
| inner_validation | T2R | OVERNIGHT | 250 | 0.02165504 | 0.05808044 | -0.0364254 | -0.09095331 | 0.02274158 | 83 | 6 |
| inner_validation | N1 | ALL_MATCHED | 453 | 0.01545584 | 0.01220511 | 0.003250726 | -0.03211445 | 0.03865868 | 86 | 6 |
| inner_validation | N1 | OLD_MORNING | 144 | 0.007347876 | -0.009964825 | 0.0173127 | -0.05839353 | 0.08539158 | 81 | 6 |
| inner_validation | N1 | OPENING | 61 | 0.05139899 | 0.03154586 | 0.01985313 | -0.07184264 | 0.1161098 | 61 | 6 |
| inner_validation | N1 | AFTERNOON | 248 | 0.02326751 | 0.0011676 | 0.02209991 | -0.02655215 | 0.06899391 | 83 | 6 |
| inner_validation | N1 | INTRADAY | 203 | 0.01685058 | 0.0001917258 | 0.01665886 | -0.03054669 | 0.06871602 | 82 | 6 |
| inner_validation | N1 | OVERNIGHT | 250 | 0.02165504 | 0.001409167 | 0.02024587 | -0.02877489 | 0.06899391 | 83 | 6 |
| inner_validation | P | ALL_MATCHED | 453 | 0.01545584 | -0.003459353 | 0.01891519 | -0.04330091 | 0.09358932 | 86 | 6 |
| inner_validation | P | OLD_MORNING | 144 | 0.007347876 | 0.02697531 | -0.01962744 | -0.08866037 | 0.03967524 | 81 | 6 |
| inner_validation | P | OPENING | 61 | 0.05139899 | -0.03986195 | 0.09126094 | 0.02406015 | 0.1375076 | 61 | 6 |
| inner_validation | P | AFTERNOON | 248 | 0.02326751 | -0.01929372 | 0.04256122 | -0.06393724 | 0.1537798 | 83 | 6 |
| inner_validation | P | INTRADAY | 203 | 0.01685058 | 0.0001133957 | 0.01673719 | -0.02145744 | 0.05008108 | 82 | 6 |
| inner_validation | P | OVERNIGHT | 250 | 0.02165504 | -0.01850258 | 0.04015762 | -0.06940296 | 0.1537798 | 83 | 6 |
| refit | T2R | ALL_MATCHED | 14395 | 0.0465916 | 0.1331104 | -0.08651879 | -0.0948401 | -0.0773076 | 2640 | 136 |
| refit | T2R | OLD_MORNING | 4437 | 0.03789439 | 0.1135815 | -0.07568715 | -0.08620706 | -0.06509698 | 2522 | 135 |
| refit | T2R | OPENING | 1873 | 0.05670273 | 0.1380873 | -0.08138452 | -0.09470947 | -0.06767102 | 1873 | 135 |
| refit | T2R | AFTERNOON | 8085 | 0.04755699 | 0.1367414 | -0.08918437 | -0.1004041 | -0.07660419 | 2593 | 135 |
| refit | T2R | INTRADAY | 6258 | 0.04207377 | 0.1199014 | -0.07782763 | -0.08616296 | -0.06838642 | 2557 | 136 |
| refit | T2R | OVERNIGHT | 8137 | 0.04788632 | 0.136888 | -0.08900164 | -0.1000468 | -0.07659876 | 2597 | 135 |
| refit | N1 | ALL_MATCHED | 14395 | 0.0465916 | -0.01125239 | 0.05784399 | 0.04843244 | 0.06666387 | 2640 | 136 |
| refit | N1 | OLD_MORNING | 4437 | 0.03789439 | -0.004846119 | 0.04274051 | 0.02900076 | 0.05784614 | 2522 | 135 |
| refit | N1 | OPENING | 1873 | 0.05670273 | -0.01075334 | 0.06745608 | 0.05029425 | 0.08486137 | 1873 | 135 |
| refit | N1 | AFTERNOON | 8085 | 0.04755699 | -0.01595271 | 0.06350971 | 0.05303579 | 0.07494285 | 2593 | 135 |
| refit | N1 | INTRADAY | 6258 | 0.04207377 | -0.005835532 | 0.04790931 | 0.03607264 | 0.05837299 | 2557 | 136 |
| refit | N1 | OVERNIGHT | 8137 | 0.04788632 | -0.01556104 | 0.06344736 | 0.05286054 | 0.07509529 | 2597 | 135 |
| refit | P | ALL_MATCHED | 14395 | 0.0465916 | 0.02428423 | 0.02230737 | 0.01082378 | 0.03515324 | 2640 | 136 |
| refit | P | OLD_MORNING | 4437 | 0.03789439 | 0.007399099 | 0.03049529 | 0.01456455 | 0.04594501 | 2522 | 135 |
| refit | P | OPENING | 1873 | 0.05670273 | 0.01252139 | 0.04418134 | 0.02586491 | 0.06364285 | 1873 | 135 |
| refit | P | AFTERNOON | 8085 | 0.04755699 | 0.0346354 | 0.01292159 | -0.0006818063 | 0.02817247 | 2593 | 135 |
| refit | P | INTRADAY | 6258 | 0.04207377 | 0.007584746 | 0.03448903 | 0.02039429 | 0.04831919 | 2557 | 136 |
| refit | P | OVERNIGHT | 8137 | 0.04788632 | 0.03484059 | 0.01304574 | -0.000201063 | 0.02813541 | 2597 | 135 |
| oos | T2R | ALL_MATCHED | 887 | 0.02681478 | 0.0041718 | 0.02264298 | -0.009252166 | 0.05228236 | 187 | 12 |
| oos | T2R | OLD_MORNING | 285 | 0.02715454 | 0.01879277 | 0.008361764 | -0.02853684 | 0.04510975 | 173 | 12 |
| oos | T2R | OPENING | 99 | 0.01651893 | -0.03225642 | 0.04877535 | -0.009548151 | 0.1040518 | 99 | 12 |
| oos | T2R | AFTERNOON | 503 | 0.02576441 | 0.00673907 | 0.01902534 | -0.02644905 | 0.06013556 | 180 | 12 |
| oos | T2R | INTRADAY | 382 | 0.01980937 | -0.0009153725 | 0.02072474 | -0.0009400658 | 0.04795979 | 178 | 12 |
| oos | T2R | OVERNIGHT | 505 | 0.02459482 | 0.005998329 | 0.01859649 | -0.02694414 | 0.06013556 | 180 | 12 |
| oos | N1 | ALL_MATCHED | 887 | 0.02681478 | 0.0103904 | 0.01642438 | -0.01894953 | 0.05451724 | 187 | 12 |
| oos | N1 | OLD_MORNING | 285 | 0.02715454 | 0.01715583 | 0.009998704 | -0.04124656 | 0.06666926 | 173 | 12 |
| oos | N1 | OPENING | 99 | 0.01651893 | 0.0158644 | 0.0006545303 | -0.07405699 | 0.07145358 | 99 | 12 |
| oos | N1 | AFTERNOON | 503 | 0.02576441 | 0.01058782 | 0.01517659 | -0.02906473 | 0.05807556 | 180 | 12 |
| oos | N1 | INTRADAY | 382 | 0.01980937 | 0.01329666 | 0.006512706 | -0.03639055 | 0.05627345 | 178 | 12 |
| oos | N1 | OVERNIGHT | 505 | 0.02459482 | 0.009354178 | 0.01524064 | -0.02895403 | 0.05807556 | 180 | 12 |
| oos | P | ALL_MATCHED | 887 | 0.02681478 | 0.05694703 | -0.03013225 | -0.0555615 | 0.0001819304 | 187 | 12 |
| oos | P | OLD_MORNING | 285 | 0.02715454 | 0.08091362 | -0.05375909 | -0.08741066 | -0.01954238 | 173 | 12 |
| oos | P | OPENING | 99 | 0.01651893 | 0.0643221 | -0.04780317 | -0.09169886 | 0.01734154 | 99 | 12 |
| oos | P | AFTERNOON | 503 | 0.02576441 | 0.04574561 | -0.0199812 | -0.06971944 | 0.03762419 | 180 | 12 |
| oos | P | INTRADAY | 382 | 0.01980937 | 0.06817259 | -0.04836323 | -0.07335158 | -0.02212667 | 178 | 12 |
| oos | P | OVERNIGHT | 505 | 0.02459482 | 0.04587371 | -0.02127889 | -0.06985899 | 0.03630859 | 180 | 12 |


All diagnostic files:

- [F23_inner_recipe.json](F23_inner_recipe.json)
- [F23_inner_train_indices.csv](F23_inner_train_indices.csv)
- [F23_inner_validation_indices.csv](F23_inner_validation_indices.csv)
- [F23_oos_indices.csv](F23_oos_indices.csv)
- [F23_refit_indices.csv](F23_refit_indices.csv)
- [F23_refit_recipe.json](F23_refit_recipe.json)
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
- [refit_003.json](refit_003.json)
- [refit_003_batches.csv](refit_003_batches.csv)
- [refit_003_gradients.csv](refit_003_gradients.csv)
- [refit_binding.json](refit_binding.json)
- [refit_cohorts.csv](refit_cohorts.csv)
- [refit_final.pt](refit_final.pt)
- [refit_metrics.json](refit_metrics.json)
- [refit_scores.parquet](refit_scores.parquet)
- [refit_strata.csv](refit_strata.csv)
- [refit_target_recipe.json](refit_target_recipe.json)
