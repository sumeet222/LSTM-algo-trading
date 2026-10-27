# META-T2R

UNTRAINED_REHEARSAL. No fitted controls or scientific results.

| role | model | arm | rows | origins | sessions | optimized_loss | daily_ic | original_TG20_mse | year | defined_origin_fraction | defined_ic_sessions | origin_ic | pair_concordance | normalized_rank_mse | top4 | bottom4 | score_sd | pair_tie_rate | actual_objective | score_units | phase | inverse_count | original_common_mse | original_centered_mse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | NEURAL | META-T2R | 200 | 10 | 2 | 1.560713 | 0.0356391 | 5.321481 | 2021 | 1 | 2 | 0.0356391 | 0.5105263 | 0.7105817 | 0.125 | 0.175 | 0.07062525 | 0 | 1.560713 | asinh TG20 | inner | 1 | 0.2017707 | 5.119711 |
| inner_validation | NEURAL | META-T2R | 160 | 8 | 2 | 1.444939 | -0.1225564 | 3.556346 | 2021 | 1 | 2 | -0.118609 | 0.4601504 | 0.8271468 | 0.08928571 | 0.07142857 | 0.03677177 | 0 | 1.444939 | asinh TG20 | inner | 1 | 0.01847717 | 3.537869 |
| refit | NEURAL | META-T2R | 200 | 10 | 2 | 1.558745 | 0.03699248 | 5.307029 | 2021 | 1 | 2 | 0.03699248 | 0.5110526 | 0.7095845 | 0.125 | 0.175 | 0.06985897 | 0 | 1.558745 | asinh TG20 | refit | 1 | 0.2013275 | 5.105702 |
| oos | NEURAL | META-T2R | 100 | 5 | 2 | 1.043622 | 0.0962406 | 1.890372 | 2021 | 1 | 2 | -0.02827068 | 0.5276316 | 0.665928 | 0.1875 | 0.03125 | 0.05914392 | 0 | 1.043621 | asinh TG20 | refit | 1 | 0.02819435 | 1.862178 |


| role | reference | group | origins | model_IC | reference_IC | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | T2R | ALL_MATCHED | 10 | 0.0356391 | -0.01969925 | 0.05533835 | 0.05533835 | 0.05533835 | 2 | 1 |
| inner_train | T2R | OLD_MORNING | 3 | 0.2052632 | 0.0424812 | 0.162782 | 0.162782 | 0.162782 | 2 | 1 |
| inner_train | T2R | OPENING | 1 | -0.07969925 | 0.1639098 | -0.243609 | -0.243609 | -0.243609 | 1 | 1 |
| inner_train | T2R | AFTERNOON | 6 | 0.01754386 | -0.09799499 | 0.1155388 | 0.1155388 | 0.1155388 | 2 | 1 |
| inner_train | T2R | INTRADAY | 4 | 0.06278195 | 0.09774436 | -0.03496241 | -0.03496241 | -0.03496241 | 2 | 1 |
| inner_train | T2R | OVERNIGHT | 6 | 0.01754386 | -0.09799499 | 0.1155388 | 0.1155388 | 0.1155388 | 2 | 1 |
| inner_train | N1 | ALL_MATCHED | 10 | 0.0356391 | -0.004668211 | 0.04030731 | 0.04030731 | 0.04030731 | 2 | 1 |
| inner_train | N1 | OLD_MORNING | 3 | 0.2052632 | 0.06186537 | 0.1433978 | 0.1433978 | 0.1433978 | 2 | 1 |
| inner_train | N1 | OPENING | 1 | -0.07969925 | 0.2274099 | -0.3071091 | -0.3071091 | -0.3071091 | 1 | 1 |
| inner_train | N1 | AFTERNOON | 6 | 0.01754386 | -0.07952931 | 0.09707317 | 0.09707317 | 0.09707317 | 2 | 1 |
| inner_train | N1 | INTRADAY | 4 | 0.06278195 | 0.1076234 | -0.04484149 | -0.04484149 | -0.04484149 | 2 | 1 |
| inner_train | N1 | OVERNIGHT | 6 | 0.01754386 | -0.07952931 | 0.09707317 | 0.09707317 | 0.09707317 | 2 | 1 |
| inner_train | P | ALL_MATCHED | 10 | 0.0356391 | -0.01684211 | 0.0524812 | 0.0524812 | 0.0524812 | 2 | 1 |
| inner_train | P | OLD_MORNING | 3 | 0.2052632 | -0.06917293 | 0.2744361 | 0.2744361 | 0.2744361 | 2 | 1 |
| inner_train | P | OPENING | 1 | -0.07969925 | -0.04360902 | -0.03609023 | -0.03609023 | -0.03609023 | 1 | 1 |
| inner_train | P | AFTERNOON | 6 | 0.01754386 | 0.05137845 | -0.03383459 | -0.03383459 | -0.03383459 | 2 | 1 |
| inner_train | P | INTRADAY | 4 | 0.06278195 | -0.1191729 | 0.1819549 | 0.1819549 | 0.1819549 | 2 | 1 |
| inner_train | P | OVERNIGHT | 6 | 0.01754386 | 0.05137845 | -0.03383459 | -0.03383459 | -0.03383459 | 2 | 1 |
| inner_validation | T2R | ALL_MATCHED | 8 | -0.1225564 | 0.1749731 | -0.2975295 | -0.2975295 | -0.2975295 | 2 | 1 |
| inner_validation | T2R | OLD_MORNING | 2 | -0.05639098 | -0.1849624 | 0.1285714 | 0.1285714 | 0.1285714 | 1 | 1 |
| inner_validation | T2R | OPENING | 1 | -0.2 | 0.5533835 | -0.7533835 | -0.7533835 | -0.7533835 | 1 | 1 |
| inner_validation | T2R | AFTERNOON | 5 | -0.1274436 | 0.0656015 | -0.1930451 | -0.1930451 | -0.1930451 | 2 | 1 |
| inner_validation | T2R | INTRADAY | 3 | -0.1042607 | 0.06115288 | -0.1654135 | -0.1654135 | -0.1654135 | 1 | 1 |
| inner_validation | T2R | OVERNIGHT | 5 | -0.1274436 | 0.0656015 | -0.1930451 | -0.1930451 | -0.1930451 | 2 | 1 |
| inner_validation | N1 | ALL_MATCHED | 8 | -0.1225564 | 0.1251343 | -0.2476907 | -0.2476907 | -0.2476907 | 2 | 1 |
| inner_validation | N1 | OLD_MORNING | 2 | -0.05639098 | -0.2278195 | 0.1714286 | 0.1714286 | 0.1714286 | 1 | 1 |
| inner_validation | N1 | OPENING | 1 | -0.2 | 0.2120301 | -0.4120301 | -0.4120301 | -0.4120301 | 1 | 1 |
| inner_validation | N1 | AFTERNOON | 5 | -0.1274436 | 0.1535714 | -0.281015 | -0.281015 | -0.281015 | 2 | 1 |
| inner_validation | N1 | INTRADAY | 3 | -0.1042607 | -0.08120301 | -0.02305764 | -0.02305764 | -0.02305764 | 1 | 1 |
| inner_validation | N1 | OVERNIGHT | 5 | -0.1274436 | 0.1535714 | -0.281015 | -0.281015 | -0.281015 | 2 | 1 |
| inner_validation | P | ALL_MATCHED | 8 | -0.1225564 | -0.3156821 | 0.1931257 | 0.1931257 | 0.1931257 | 2 | 1 |
| inner_validation | P | OLD_MORNING | 2 | -0.05639098 | 0.1992481 | -0.2556391 | -0.2556391 | -0.2556391 | 1 | 1 |
| inner_validation | P | OPENING | 1 | -0.2 | -0.4285714 | 0.2285714 | 0.2285714 | 0.2285714 | 1 | 1 |
| inner_validation | P | AFTERNOON | 5 | -0.1274436 | -0.3671053 | 0.2396617 | 0.2396617 | 0.2396617 | 2 | 1 |
| inner_validation | P | INTRADAY | 3 | -0.1042607 | -0.01002506 | -0.09423559 | -0.09423559 | -0.09423559 | 1 | 1 |
| inner_validation | P | OVERNIGHT | 5 | -0.1274436 | -0.3671053 | 0.2396617 | 0.2396617 | 0.2396617 | 2 | 1 |
| refit | T2R | ALL_MATCHED | 10 | 0.03699248 | -0.01293233 | 0.04992481 | 0.04992481 | 0.04992481 | 2 | 1 |
| refit | T2R | OLD_MORNING | 3 | 0.2026316 | 0.1078947 | 0.09473684 | 0.09473684 | 0.09473684 | 2 | 1 |
| refit | T2R | OPENING | 1 | -0.06466165 | 0.2120301 | -0.2766917 | -0.2766917 | -0.2766917 | 1 | 1 |
| refit | T2R | AFTERNOON | 6 | 0.01904762 | -0.1130326 | 0.1320802 | 0.1320802 | 0.1320802 | 2 | 1 |
| refit | T2R | INTRADAY | 4 | 0.06390977 | 0.137218 | -0.07330827 | -0.07330827 | -0.07330827 | 2 | 1 |
| refit | T2R | OVERNIGHT | 6 | 0.01904762 | -0.1130326 | 0.1320802 | 0.1320802 | 0.1320802 | 2 | 1 |
| refit | N1 | ALL_MATCHED | 10 | 0.03699248 | -0.004668211 | 0.04166069 | 0.04166069 | 0.04166069 | 2 | 1 |
| refit | N1 | OLD_MORNING | 3 | 0.2026316 | 0.06186537 | 0.1407662 | 0.1407662 | 0.1407662 | 2 | 1 |
| refit | N1 | OPENING | 1 | -0.06466165 | 0.2274099 | -0.2920716 | -0.2920716 | -0.2920716 | 1 | 1 |
| refit | N1 | AFTERNOON | 6 | 0.01904762 | -0.07952931 | 0.09857693 | 0.09857693 | 0.09857693 | 2 | 1 |
| refit | N1 | INTRADAY | 4 | 0.06390977 | 0.1076234 | -0.04371367 | -0.04371367 | -0.04371367 | 2 | 1 |
| refit | N1 | OVERNIGHT | 6 | 0.01904762 | -0.07952931 | 0.09857693 | 0.09857693 | 0.09857693 | 2 | 1 |
| refit | P | ALL_MATCHED | 10 | 0.03699248 | -0.04285714 | 0.07984962 | 0.07984962 | 0.07984962 | 2 | 1 |
| refit | P | OLD_MORNING | 3 | 0.2026316 | -0.08646617 | 0.2890977 | 0.2890977 | 0.2890977 | 2 | 1 |
| refit | P | OPENING | 1 | -0.06466165 | -0.1052632 | 0.0406015 | 0.0406015 | 0.0406015 | 1 | 1 |
| refit | P | AFTERNOON | 6 | 0.01904762 | 0.02105263 | -0.002005013 | -0.002005013 | -0.002005013 | 2 | 1 |
| refit | P | INTRADAY | 4 | 0.06390977 | -0.1387218 | 0.2026316 | 0.2026316 | 0.2026316 | 2 | 1 |
| refit | P | OVERNIGHT | 6 | 0.01904762 | 0.02105263 | -0.002005013 | -0.002005013 | -0.002005013 | 2 | 1 |
| oos | T2R | ALL_MATCHED | 5 | 0.0962406 | -0.008458647 | 0.1046992 | 0.1046992 | 0.1046992 | 2 | 1 |
| oos | T2R | OLD_MORNING | 2 | 0.1691729 | -0.01804511 | 0.187218 | 0.187218 | 0.187218 | 1 | 1 |
| oos | T2R | AFTERNOON | 3 | -0.04398496 | -0.08684211 | 0.04285714 | 0.04285714 | 0.04285714 | 2 | 1 |
| oos | T2R | INTRADAY | 2 | 0.1691729 | -0.01804511 | 0.187218 | 0.187218 | 0.187218 | 1 | 1 |
| oos | T2R | OVERNIGHT | 3 | -0.04398496 | -0.08684211 | 0.04285714 | 0.04285714 | 0.04285714 | 2 | 1 |
| oos | N1 | ALL_MATCHED | 5 | 0.0962406 | 0.07293233 | 0.02330827 | 0.02330827 | 0.02330827 | 2 | 1 |
| oos | N1 | OLD_MORNING | 2 | 0.1691729 | 0.4451128 | -0.2759398 | -0.2759398 | -0.2759398 | 1 | 1 |
| oos | N1 | AFTERNOON | 3 | -0.04398496 | -0.08646617 | 0.0424812 | 0.0424812 | 0.0424812 | 2 | 1 |
| oos | N1 | INTRADAY | 2 | 0.1691729 | 0.4451128 | -0.2759398 | -0.2759398 | -0.2759398 | 1 | 1 |
| oos | N1 | OVERNIGHT | 3 | -0.04398496 | -0.08646617 | 0.0424812 | 0.0424812 | 0.0424812 | 2 | 1 |
| oos | P | ALL_MATCHED | 5 | 0.0962406 | -0.399812 | 0.4960526 | 0.4960526 | 0.4960526 | 2 | 1 |
| oos | P | OLD_MORNING | 2 | 0.1691729 | -0.7729323 | 0.9421053 | 0.9421053 | 0.9421053 | 1 | 1 |
| oos | P | AFTERNOON | 3 | -0.04398496 | -0.0943609 | 0.05037594 | 0.05037594 | 0.05037594 | 2 | 1 |
| oos | P | INTRADAY | 2 | 0.1691729 | -0.7729323 | 0.9421053 | 0.9421053 | 0.9421053 | 1 | 1 |
| oos | P | OVERNIGHT | 3 | -0.04398496 | -0.0943609 | 0.05037594 | 0.05037594 | 0.05037594 | 2 | 1 |


All diagnostic files:

- [F21_inner_recipe.json](F21_inner_recipe.json)
- [F21_inner_train_indices.csv](F21_inner_train_indices.csv)
- [F21_inner_validation_indices.csv](F21_inner_validation_indices.csv)
- [F21_oos_indices.csv](F21_oos_indices.csv)
- [F21_refit_indices.csv](F21_refit_indices.csv)
- [F21_refit_recipe.json](F21_refit_recipe.json)
- [calibration_001.json](calibration_001.json)
- [calibration_001_batches.csv](calibration_001_batches.csv)
- [calibration_001_gradients.csv](calibration_001_gradients.csv)
- [calibration_binding.json](calibration_binding.json)
- [inner_target_recipe.json](inner_target_recipe.json)
- [inner_train_cohorts.csv](inner_train_cohorts.csv)
- [inner_train_metrics.json](inner_train_metrics.json)
- [inner_train_scores.parquet](inner_train_scores.parquet)
- [inner_train_strata.csv](inner_train_strata.csv)
- [inner_validation_cohorts.csv](inner_validation_cohorts.csv)
- [inner_validation_metrics.json](inner_validation_metrics.json)
- [inner_validation_scores.parquet](inner_validation_scores.parquet)
- [inner_validation_strata.csv](inner_validation_strata.csv)
- [inner_zero_step.pt](inner_zero_step.pt)
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
- [refit_binding.json](refit_binding.json)
- [refit_cohorts.csv](refit_cohorts.csv)
- [refit_metrics.json](refit_metrics.json)
- [refit_scores.parquet](refit_scores.parquet)
- [refit_strata.csv](refit_strata.csv)
- [refit_target_recipe.json](refit_target_recipe.json)
- [refit_zero_step.pt](refit_zero_step.pt)
