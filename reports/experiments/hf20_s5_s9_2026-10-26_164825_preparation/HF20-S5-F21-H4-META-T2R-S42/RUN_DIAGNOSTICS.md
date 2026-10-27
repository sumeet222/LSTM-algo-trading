# HF20-S5-F21-H4-META-T2R-S42

TECHNICAL_PASS. All four roles verified; OOS remains exploratory.

| role | model | arm | rows | origins | sessions | optimized_loss | daily_ic | original_TG20_mse | year | defined_origin_fraction | defined_ic_sessions | origin_ic | pair_concordance | normalized_rank_mse | top4 | bottom4 | score_sd | pair_tie_rate | actual_objective | score_units | phase | inverse_count | original_common_mse | original_centered_mse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | NEURAL | META-T2R | 228980 | 11449 | 2100 | 1.364841 | 0.04582188 | 4.834023 | 2021 | 1 | 2100 | 0.04361444 | 0.5162816 | 0.7030745 | 0.2274702 | 0.2379317 | 0.04260486 | 0 | 1.364841 | asinh TG20 | inner | 1 | 0.1846465 | 4.649377 |
| inner_validation | NEURAL | META-T2R | 13480 | 674 | 120 | 1.364668 | 0.05569224 | 4.15437 | 2021 | 1 | 120 | 0.05245192 | 0.5200266 | 0.6958039 | 0.2516667 | 0.2282738 | 0.04800847 | 0 | 1.364668 | asinh TG20 | inner | 1 | 0.1678735 | 3.986497 |
| refit | NEURAL | META-T2R | 243420 | 12171 | 2227 | 1.362453 | 0.04389949 | 4.783197 | 2021 | 1 | 2227 | 0.04085994 | 0.515607 | 0.7044911 | 0.2254314 | 0.2373038 | 0.0484642 | 0 | 1.362453 | asinh TG20 | refit | 1 | 0.1833837 | 4.599814 |
| oos | NEURAL | META-T2R | 19100 | 955 | 188 | 1.302347 | 0.01927938 | 3.44258 | 2021 | 1 | 188 | 0.01335958 | 0.5065306 | 0.7226342 | 0.2320067 | 0.2030079 | 0.05087374 | 4.66592e-06 | 1.302346 | asinh TG20 | refit | 1 | 0.1241571 | 3.318423 |


| role | reference | group | origins | model_IC | reference_IC | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | T2R | ALL_MATCHED | 11449 | 0.04582188 | 0.04038154 | 0.005440341 | 0.0003266071 | 0.01119339 | 2100 | 106 |
| inner_train | T2R | OLD_MORNING | 3539 | 0.03672974 | 0.0371737 | -0.000443968 | -0.007325963 | 0.007057099 | 2001 | 105 |
| inner_train | T2R | OPENING | 1479 | 0.06647694 | 0.05031003 | 0.01616692 | 0.006841035 | 0.02561379 | 1479 | 105 |
| inner_train | T2R | AFTERNOON | 6431 | 0.04509387 | 0.03748902 | 0.007604854 | -0.0003226681 | 0.01606167 | 2062 | 105 |
| inner_train | T2R | INTRADAY | 4975 | 0.04480004 | 0.04043276 | 0.004367272 | -0.002266174 | 0.01044053 | 2031 | 106 |
| inner_train | T2R | OVERNIGHT | 6474 | 0.04499864 | 0.03772815 | 0.007270486 | -0.0007943081 | 0.01574389 | 2065 | 105 |
| inner_train | N1 | ALL_MATCHED | 11449 | 0.04582188 | -0.0142073 | 0.06002919 | 0.04976316 | 0.06946567 | 2100 | 106 |
| inner_train | N1 | OLD_MORNING | 3539 | 0.03672974 | -0.009062609 | 0.04579235 | 0.03038951 | 0.05991353 | 2001 | 105 |
| inner_train | N1 | OPENING | 1479 | 0.06647694 | -0.01266477 | 0.07914171 | 0.06153022 | 0.09581056 | 1479 | 105 |
| inner_train | N1 | AFTERNOON | 6431 | 0.04509387 | -0.01827038 | 0.06336425 | 0.05044944 | 0.07681137 | 2062 | 105 |
| inner_train | N1 | INTRADAY | 4975 | 0.04480004 | -0.009105986 | 0.05390602 | 0.04082405 | 0.06614611 | 2031 | 106 |
| inner_train | N1 | OVERNIGHT | 6474 | 0.04499864 | -0.01786482 | 0.06286346 | 0.05024862 | 0.07602014 | 2065 | 105 |
| inner_train | P | ALL_MATCHED | 11449 | 0.04582188 | 0.03147201 | 0.01434987 | 0.001600938 | 0.02638042 | 2100 | 106 |
| inner_train | P | OLD_MORNING | 3539 | 0.03672974 | 0.01234173 | 0.024388 | 0.006502291 | 0.03870533 | 2001 | 105 |
| inner_train | P | OPENING | 1479 | 0.06647694 | 0.02097288 | 0.04550406 | 0.02440612 | 0.06413745 | 1479 | 105 |
| inner_train | P | AFTERNOON | 6431 | 0.04509387 | 0.04402851 | 0.001065367 | -0.0143031 | 0.01419293 | 2062 | 105 |
| inner_train | P | INTRADAY | 4975 | 0.04480004 | 0.0144714 | 0.03032863 | 0.01576723 | 0.04464656 | 2031 | 106 |
| inner_train | P | OVERNIGHT | 6474 | 0.04499864 | 0.04419314 | 0.000805501 | -0.01410751 | 0.01365043 | 2065 | 105 |
| inner_validation | T2R | ALL_MATCHED | 674 | 0.05569224 | 0.05416369 | 0.001528541 | -0.01420223 | 0.01461632 | 120 | 6 |
| inner_validation | T2R | OLD_MORNING | 199 | 0.058862 | 0.04666098 | 0.01220102 | -0.009458859 | 0.03068051 | 117 | 6 |
| inner_validation | T2R | OPENING | 93 | 0.003088366 | 0.01065567 | -0.007567305 | -0.03731756 | 0.02014163 | 93 | 6 |
| inner_validation | T2R | AFTERNOON | 382 | 0.06201533 | 0.05527474 | 0.006740591 | -0.0112129 | 0.0252722 | 119 | 6 |
| inner_validation | T2R | INTRADAY | 288 | 0.0354724 | 0.02723604 | 0.008236356 | -0.01707253 | 0.02923753 | 116 | 6 |
| inner_validation | T2R | OVERNIGHT | 386 | 0.0624551 | 0.05746032 | 0.004994779 | -0.01348726 | 0.0239514 | 120 | 6 |
| inner_validation | N1 | ALL_MATCHED | 674 | 0.05569224 | -0.0027825 | 0.05847474 | 0.02664101 | 0.09891666 | 120 | 6 |
| inner_validation | N1 | OLD_MORNING | 199 | 0.058862 | 0.02017551 | 0.03868649 | -0.01596198 | 0.126429 | 117 | 6 |
| inner_validation | N1 | OPENING | 93 | 0.003088366 | -0.01245101 | 0.01553938 | -0.05033117 | 0.08284552 | 93 | 6 |
| inner_validation | N1 | AFTERNOON | 382 | 0.06201533 | -0.01244891 | 0.07446424 | 0.04190286 | 0.109566 | 119 | 6 |
| inner_validation | N1 | INTRADAY | 288 | 0.0354724 | -0.001284949 | 0.03675735 | -0.006279891 | 0.09964472 | 116 | 6 |
| inner_validation | N1 | OVERNIGHT | 386 | 0.0624551 | -0.01051639 | 0.07297148 | 0.03744467 | 0.1123312 | 120 | 6 |
| inner_validation | P | ALL_MATCHED | 674 | 0.05569224 | 0.06235163 | -0.006659397 | -0.04532429 | 0.02972357 | 120 | 6 |
| inner_validation | P | OLD_MORNING | 199 | 0.058862 | 0.04579838 | 0.01306361 | -0.01814796 | 0.04130968 | 117 | 6 |
| inner_validation | P | OPENING | 93 | 0.003088366 | 0.01059099 | -0.007502628 | -0.07748969 | 0.07594443 | 93 | 6 |
| inner_validation | P | AFTERNOON | 382 | 0.06201533 | 0.07026916 | -0.008253828 | -0.05157935 | 0.03754413 | 119 | 6 |
| inner_validation | P | INTRADAY | 288 | 0.0354724 | 0.03421943 | 0.00125297 | -0.04491883 | 0.04661956 | 116 | 6 |
| inner_validation | P | OVERNIGHT | 386 | 0.0624551 | 0.07175125 | -0.009296157 | -0.05320713 | 0.03902692 | 120 | 6 |
| refit | T2R | ALL_MATCHED | 12171 | 0.04389949 | 0.04015535 | 0.003744145 | -0.0008527646 | 0.008003854 | 2227 | 112 |
| refit | T2R | OLD_MORNING | 3751 | 0.03440325 | 0.03546406 | -0.001060813 | -0.006972298 | 0.004680034 | 2126 | 111 |
| refit | T2R | OPENING | 1579 | 0.05830359 | 0.05307739 | 0.0052262 | -0.00384775 | 0.01272352 | 1579 | 111 |
| refit | T2R | AFTERNOON | 6841 | 0.0436804 | 0.03770738 | 0.005973021 | 0.0001728604 | 0.01214867 | 2189 | 111 |
| refit | T2R | INTRADAY | 5283 | 0.04041456 | 0.03974589 | 0.0006686698 | -0.004369021 | 0.005993886 | 2155 | 112 |
| refit | T2R | OVERNIGHT | 6888 | 0.04398633 | 0.03806945 | 0.005916875 | 3.729549e-06 | 0.01204086 | 2193 | 111 |
| refit | N1 | ALL_MATCHED | 12171 | 0.04389949 | -0.01378125 | 0.05768074 | 0.04707602 | 0.06820416 | 2227 | 112 |
| refit | N1 | OLD_MORNING | 3751 | 0.03440325 | -0.007523768 | 0.04192702 | 0.02726099 | 0.05636019 | 2126 | 111 |
| refit | N1 | OPENING | 1579 | 0.05830359 | -0.01261897 | 0.07092257 | 0.05164493 | 0.08759845 | 1579 | 111 |
| refit | N1 | AFTERNOON | 6841 | 0.0436804 | -0.01822018 | 0.06190058 | 0.04964646 | 0.07661308 | 2189 | 111 |
| refit | N1 | INTRADAY | 5283 | 0.04041456 | -0.008798553 | 0.04921311 | 0.03585707 | 0.06088911 | 2155 | 112 |
| refit | N1 | OVERNIGHT | 6888 | 0.04398633 | -0.01772998 | 0.06171631 | 0.04937378 | 0.07603438 | 2193 | 111 |
| refit | P | ALL_MATCHED | 12171 | 0.04389949 | 0.03392056 | 0.009978928 | -0.002013342 | 0.02208712 | 2227 | 112 |
| refit | P | OLD_MORNING | 3751 | 0.03440325 | 0.01346309 | 0.02094016 | 0.004869564 | 0.03636749 | 2126 | 111 |
| refit | P | OPENING | 1579 | 0.05830359 | 0.02192879 | 0.0363748 | 0.01684232 | 0.05445696 | 1579 | 111 |
| refit | P | AFTERNOON | 6841 | 0.0436804 | 0.04652677 | -0.002846373 | -0.0151289 | 0.009760854 | 2189 | 111 |
| refit | P | INTRADAY | 5283 | 0.04041456 | 0.01551651 | 0.02489805 | 0.00899391 | 0.03971288 | 2155 | 112 |
| refit | P | OVERNIGHT | 6888 | 0.04398633 | 0.04671984 | -0.002733515 | -0.01526797 | 0.009844559 | 2193 | 111 |
| oos | T2R | ALL_MATCHED | 955 | 0.01927938 | 0.01520458 | 0.004074809 | -0.007924208 | 0.0165956 | 188 | 12 |
| oos | T2R | OLD_MORNING | 295 | 0.03860238 | 0.04139542 | -0.002793041 | -0.02106531 | 0.0168391 | 178 | 12 |
| oos | T2R | OPENING | 130 | 0.01349913 | 0.006107577 | 0.007391556 | -0.01200697 | 0.02869915 | 130 | 12 |
| oos | T2R | AFTERNOON | 530 | 0.007621063 | -0.005471981 | 0.01309304 | -0.0004712492 | 0.02956874 | 183 | 12 |
| oos | T2R | INTRADAY | 422 | 0.03359286 | 0.03630747 | -0.00271461 | -0.01604529 | 0.01316278 | 181 | 12 |
| oos | T2R | OVERNIGHT | 533 | 0.007327295 | -0.006166339 | 0.01349363 | -0.0004712492 | 0.03076327 | 183 | 12 |
| oos | N1 | ALL_MATCHED | 955 | 0.01927938 | 0.003829874 | 0.01544951 | -0.02058421 | 0.04809836 | 188 | 12 |
| oos | N1 | OLD_MORNING | 295 | 0.03860238 | 0.01830839 | 0.02029398 | -0.01399163 | 0.05599041 | 178 | 12 |
| oos | N1 | OPENING | 130 | 0.01349913 | 0.002860977 | 0.01063816 | -0.02671919 | 0.04826707 | 130 | 12 |
| oos | N1 | AFTERNOON | 530 | 0.007621063 | -0.004738142 | 0.0123592 | -0.03664639 | 0.05755685 | 183 | 12 |
| oos | N1 | INTRADAY | 422 | 0.03359286 | 0.021096 | 0.01249686 | -0.01939903 | 0.04325404 | 181 | 12 |
| oos | N1 | OVERNIGHT | 533 | 0.007327295 | -0.005107918 | 0.01243521 | -0.03648397 | 0.05756049 | 183 | 12 |
| oos | P | ALL_MATCHED | 955 | 0.01927938 | -0.01887889 | 0.03815828 | -0.03592659 | 0.0977394 | 188 | 12 |
| oos | P | OLD_MORNING | 295 | 0.03860238 | -0.008189017 | 0.04679139 | -0.009776545 | 0.1137852 | 178 | 12 |
| oos | P | OPENING | 130 | 0.01349913 | -0.04514748 | 0.05864662 | -0.01501103 | 0.1282151 | 130 | 12 |
| oos | P | AFTERNOON | 530 | 0.007621063 | -0.01334898 | 0.02097004 | -0.06676753 | 0.09991664 | 183 | 12 |
| oos | P | INTRADAY | 422 | 0.03359286 | -0.0294296 | 0.06302247 | 0.004295141 | 0.1281182 | 181 | 12 |
| oos | P | OVERNIGHT | 533 | 0.007327295 | -0.01386461 | 0.02119191 | -0.06651048 | 0.1001442 | 183 | 12 |


All diagnostic files:

- [F21_inner_recipe.json](F21_inner_recipe.json)
- [F21_inner_train_indices.csv](F21_inner_train_indices.csv)
- [F21_inner_validation_indices.csv](F21_inner_validation_indices.csv)
- [F21_oos_indices.csv](F21_oos_indices.csv)
- [F21_refit_indices.csv](F21_refit_indices.csv)
- [F21_refit_recipe.json](F21_refit_recipe.json)
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
