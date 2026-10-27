# HF20-S5-F22-H4-META-T2R-S42

TECHNICAL_PASS. All four roles verified; OOS remains exploratory.

| role | model | arm | rows | origins | sessions | optimized_loss | daily_ic | original_TG20_mse | year | defined_origin_fraction | defined_ic_sessions | origin_ic | pair_concordance | normalized_rank_mse | top4 | bottom4 | score_sd | pair_tie_rate | actual_objective | score_units | phase | inverse_count | original_common_mse | original_centered_mse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | NEURAL | META-T2R | 254320 | 12716 | 2331 | 1.358174 | 0.03313524 | 4.697127 | 2022 | 1 | 2331 | 0.03042816 | 0.5114688 | 0.7124228 | 0.2434945 | 0.206448 | 0.03149925 | 0 | 1.358174 | asinh TG20 | inner | 1 | 0.1797959 | 4.517331 |
| inner_validation | NEURAL | META-T2R | 9140 | 457 | 92 | 1.331195 | 0.03183771 | 3.86209 | 2022 | 1 | 92 | 0.02375088 | 0.5123775 | 0.713382 | 0.2673978 | 0.1823564 | 0.03417564 | 0 | 1.331195 | asinh TG20 | inner | 1 | 0.127977 | 3.734113 |
| refit | NEURAL | META-T2R | 263460 | 13173 | 2423 | 1.356602 | 0.03145934 | 4.659322 | 2022 | 1 | 2423 | 0.02906999 | 0.5109678 | 0.7136577 | 0.2492814 | 0.207515 | 0.03005896 | 0 | 1.356602 | asinh TG20 | refit | 1 | 0.1777476 | 4.481574 |
| oos | NEURAL | META-T2R | 23600 | 1180 | 210 | 1.348672 | -0.005200797 | 3.816692 | 2022 | 1 | 210 | -0.003814618 | 0.4978577 | 0.7406736 | 0.2309836 | 0.1939257 | 0.03053551 | 0 | 1.348672 | asinh TG20 | refit | 1 | 0.1430046 | 3.673688 |


| role | reference | group | origins | model_IC | reference_IC | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | T2R | ALL_MATCHED | 12716 | 0.03313524 | 0.03484988 | -0.001714649 | -0.009631136 | 0.005845105 | 2331 | 118 |
| inner_train | T2R | OLD_MORNING | 3921 | 0.02619356 | 0.03089256 | -0.004699002 | -0.01418637 | 0.00451466 | 2223 | 117 |
| inner_train | T2R | OPENING | 1648 | 0.03884463 | 0.03456131 | 0.004283324 | -0.01084078 | 0.01634154 | 1648 | 117 |
| inner_train | T2R | AFTERNOON | 7147 | 0.03402882 | 0.03588722 | -0.001858399 | -0.01243221 | 0.006332924 | 2291 | 117 |
| inner_train | T2R | INTRADAY | 5522 | 0.02973137 | 0.0307839 | -0.001052533 | -0.01033012 | 0.007357664 | 2256 | 118 |
| inner_train | T2R | OVERNIGHT | 7194 | 0.0339069 | 0.03622688 | -0.002319989 | -0.01297458 | 0.005783638 | 2295 | 117 |
| inner_train | N1 | ALL_MATCHED | 12716 | 0.03313524 | -0.01269243 | 0.04582766 | 0.03658045 | 0.0574579 | 2331 | 118 |
| inner_train | N1 | OLD_MORNING | 3921 | 0.02619356 | -0.005532731 | 0.03172629 | 0.01847715 | 0.04597774 | 2223 | 117 |
| inner_train | N1 | OPENING | 1648 | 0.03884463 | -0.01310154 | 0.05194617 | 0.03480661 | 0.06890124 | 1648 | 117 |
| inner_train | N1 | AFTERNOON | 7147 | 0.03402882 | -0.0175227 | 0.05155152 | 0.03945115 | 0.0637797 | 2291 | 117 |
| inner_train | N1 | INTRADAY | 5522 | 0.02973137 | -0.006877669 | 0.03660904 | 0.0249217 | 0.05034512 | 2256 | 118 |
| inner_train | N1 | OVERNIGHT | 7194 | 0.0339069 | -0.0170555 | 0.0509624 | 0.03893403 | 0.06292806 | 2295 | 117 |
| inner_train | P | ALL_MATCHED | 12716 | 0.03313524 | 0.03055665 | 0.002578587 | -0.01068932 | 0.01543713 | 2331 | 118 |
| inner_train | P | OLD_MORNING | 3921 | 0.02619356 | 0.01098051 | 0.01521305 | -0.001652541 | 0.02931075 | 2223 | 117 |
| inner_train | P | OPENING | 1648 | 0.03884463 | 0.01926142 | 0.01958321 | 5.187438e-05 | 0.04017586 | 1648 | 117 |
| inner_train | P | AFTERNOON | 7147 | 0.03402882 | 0.04310264 | -0.009073815 | -0.02258253 | 0.004064406 | 2291 | 117 |
| inner_train | P | INTRADAY | 5522 | 0.02973137 | 0.01208971 | 0.01764166 | 0.001798416 | 0.03267835 | 2256 | 118 |
| inner_train | P | OVERNIGHT | 7194 | 0.0339069 | 0.0432991 | -0.009392205 | -0.02265646 | 0.003810358 | 2295 | 117 |
| inner_validation | T2R | ALL_MATCHED | 457 | 0.03183771 | 0.02172109 | 0.01011662 | -0.02203872 | 0.03941734 | 92 | 6 |
| inner_validation | T2R | OLD_MORNING | 139 | 0.03687645 | 0.05587816 | -0.01900171 | -0.06929041 | 0.01295848 | 88 | 6 |
| inner_validation | T2R | OPENING | 69 | 0.03007519 | 0.001874251 | 0.02820094 | -0.01567369 | 0.07184628 | 69 | 6 |
| inner_validation | T2R | AFTERNOON | 249 | 0.03068063 | 0.006666948 | 0.02401369 | -0.01294665 | 0.05932735 | 89 | 6 |
| inner_validation | T2R | INTRADAY | 205 | 0.03090974 | 0.03392991 | -0.003020166 | -0.05108276 | 0.03056698 | 88 | 6 |
| inner_validation | T2R | OVERNIGHT | 252 | 0.03038495 | 0.00639661 | 0.02398834 | -0.01294665 | 0.05925911 | 89 | 6 |
| inner_validation | N1 | ALL_MATCHED | 457 | 0.03183771 | -0.007690666 | 0.03952837 | 0.0002965362 | 0.08192905 | 92 | 6 |
| inner_validation | N1 | OLD_MORNING | 139 | 0.03687645 | -0.007943027 | 0.04481948 | 0.008915969 | 0.07218836 | 88 | 6 |
| inner_validation | N1 | OPENING | 69 | 0.03007519 | 0.0173528 | 0.01272239 | -0.04768699 | 0.06515237 | 69 | 6 |
| inner_validation | N1 | AFTERNOON | 249 | 0.03068063 | -0.009132907 | 0.03981354 | -0.01832852 | 0.1041524 | 89 | 6 |
| inner_validation | N1 | INTRADAY | 205 | 0.03090974 | -0.004082803 | 0.03499255 | 0.006444774 | 0.05653025 | 88 | 6 |
| inner_validation | N1 | OVERNIGHT | 252 | 0.03038495 | -0.009893235 | 0.04027819 | -0.01832852 | 0.1055755 | 89 | 6 |
| inner_validation | P | ALL_MATCHED | 457 | 0.03183771 | 0.007133961 | 0.02470375 | -0.03192006 | 0.08375042 | 92 | 6 |
| inner_validation | P | OLD_MORNING | 139 | 0.03687645 | 0.02911718 | 0.007759272 | -0.05373997 | 0.06162186 | 88 | 6 |
| inner_validation | P | OPENING | 69 | 0.03007519 | -0.05576986 | 0.08584505 | -0.0225856 | 0.1687816 | 69 | 6 |
| inner_validation | P | AFTERNOON | 249 | 0.03068063 | 0.003327138 | 0.0273535 | -0.05019956 | 0.1054894 | 89 | 6 |
| inner_validation | P | INTRADAY | 205 | 0.03090974 | 0.002950021 | 0.02795972 | -0.02637274 | 0.08221523 | 88 | 6 |
| inner_validation | P | OVERNIGHT | 252 | 0.03038495 | 0.002233111 | 0.02815184 | -0.05013716 | 0.1054894 | 89 | 6 |
| refit | T2R | ALL_MATCHED | 13173 | 0.03145934 | 0.03400437 | -0.002545035 | -0.0120294 | 0.00517006 | 2423 | 124 |
| refit | T2R | OLD_MORNING | 4060 | 0.02505468 | 0.03052537 | -0.005470697 | -0.01549995 | 0.003522054 | 2311 | 123 |
| refit | T2R | OPENING | 1717 | 0.03077374 | 0.03214166 | -0.001367915 | -0.01836448 | 0.01259765 | 1717 | 123 |
| refit | T2R | AFTERNOON | 7396 | 0.03425262 | 0.03524941 | -0.0009967923 | -0.0132711 | 0.009098371 | 2380 | 123 |
| refit | T2R | INTRADAY | 5727 | 0.02675059 | 0.02920439 | -0.002453802 | -0.01119677 | 0.005596432 | 2344 | 124 |
| refit | T2R | OVERNIGHT | 7446 | 0.03421376 | 0.035566 | -0.001352238 | -0.0138059 | 0.008902883 | 2384 | 123 |
| refit | N1 | ALL_MATCHED | 13173 | 0.03145934 | -0.01252166 | 0.043981 | 0.03443561 | 0.05416819 | 2423 | 124 |
| refit | N1 | OLD_MORNING | 4060 | 0.02505468 | -0.005643385 | 0.03069806 | 0.01601571 | 0.04357474 | 2311 | 123 |
| refit | N1 | OPENING | 1717 | 0.03077374 | -0.01190398 | 0.04267772 | 0.02610417 | 0.06085196 | 1717 | 123 |
| refit | N1 | AFTERNOON | 7396 | 0.03425262 | -0.01722898 | 0.0514816 | 0.04123153 | 0.06272804 | 2380 | 123 |
| refit | N1 | INTRADAY | 5727 | 0.02675059 | -0.006791672 | 0.03354226 | 0.02199433 | 0.04612156 | 2344 | 124 |
| refit | N1 | OVERNIGHT | 7446 | 0.03421376 | -0.0168081 | 0.05102186 | 0.04063284 | 0.0622429 | 2384 | 123 |
| refit | P | ALL_MATCHED | 13173 | 0.03145934 | 0.02971301 | 0.001746322 | -0.01052005 | 0.01303301 | 2423 | 124 |
| refit | P | OLD_MORNING | 4060 | 0.02505468 | 0.01153659 | 0.01351809 | -0.002702267 | 0.02898927 | 2311 | 123 |
| refit | P | OPENING | 1717 | 0.03077374 | 0.01656017 | 0.01421357 | -0.006553878 | 0.03517843 | 1717 | 123 |
| refit | P | AFTERNOON | 7396 | 0.03425262 | 0.04168187 | -0.007429251 | -0.02201865 | 0.007796186 | 2380 | 123 |
| refit | P | INTRADAY | 5727 | 0.02675059 | 0.01176074 | 0.01498985 | 0.0001016998 | 0.02804983 | 2344 | 124 |
| refit | P | OVERNIGHT | 7446 | 0.03421376 | 0.0418471 | -0.007633333 | -0.02185442 | 0.007080455 | 2384 | 123 |
| oos | T2R | ALL_MATCHED | 1180 | -0.005200797 | 0.01614774 | -0.02134854 | -0.05173876 | 0.005337889 | 210 | 12 |
| oos | T2R | OLD_MORNING | 365 | -0.009867798 | 0.01404239 | -0.02391018 | -0.06552192 | 0.009459012 | 204 | 12 |
| oos | T2R | OPENING | 152 | -0.01366245 | 0.02856154 | -0.04222398 | -0.09512548 | 0.01378708 | 152 | 12 |
| oos | T2R | AFTERNOON | 663 | 0.003682377 | 0.02083868 | -0.01715631 | -0.04421049 | 0.01063164 | 205 | 12 |
| oos | T2R | INTRADAY | 515 | -0.01108069 | 0.01774577 | -0.02882646 | -0.06657202 | 0.007082018 | 206 | 12 |
| oos | T2R | OVERNIGHT | 665 | 0.00320802 | 0.02023473 | -0.01702671 | -0.04392595 | 0.01074876 | 205 | 12 |
| oos | N1 | ALL_MATCHED | 1180 | -0.005200797 | 0.002257178 | -0.007457975 | -0.03370713 | 0.01026238 | 210 | 12 |
| oos | N1 | OLD_MORNING | 365 | -0.009867798 | 0.002127987 | -0.01199578 | -0.05861948 | 0.0273286 | 204 | 12 |
| oos | N1 | OPENING | 152 | -0.01366245 | 0.001120028 | -0.01478247 | -0.07095046 | 0.05110103 | 152 | 12 |
| oos | N1 | AFTERNOON | 663 | 0.003682377 | -0.002153733 | 0.00583611 | -0.0111964 | 0.02745646 | 205 | 12 |
| oos | N1 | INTRADAY | 515 | -0.01108069 | 0.00301029 | -0.01409098 | -0.05417127 | 0.01874648 | 206 | 12 |
| oos | N1 | OVERNIGHT | 665 | 0.00320802 | -0.002055927 | 0.005263947 | -0.01219244 | 0.02708247 | 205 | 12 |
| oos | P | ALL_MATCHED | 1180 | -0.005200797 | -0.02841185 | 0.02321105 | -0.01510428 | 0.06084627 | 210 | 12 |
| oos | P | OLD_MORNING | 365 | -0.009867798 | -0.03255469 | 0.02268689 | -0.05445323 | 0.09255334 | 204 | 12 |
| oos | P | OPENING | 152 | -0.01366245 | -0.0434903 | 0.02982786 | -0.03694452 | 0.09481898 | 152 | 12 |
| oos | P | AFTERNOON | 663 | 0.003682377 | -0.03380647 | 0.03748884 | -0.01029049 | 0.08380195 | 205 | 12 |
| oos | P | INTRADAY | 515 | -0.01108069 | -0.03432912 | 0.02324843 | -0.04547502 | 0.08806835 | 206 | 12 |
| oos | P | OVERNIGHT | 665 | 0.00320802 | -0.03350083 | 0.03670885 | -0.01114438 | 0.08380195 | 205 | 12 |


All diagnostic files:

- [F22_inner_recipe.json](F22_inner_recipe.json)
- [F22_inner_train_indices.csv](F22_inner_train_indices.csv)
- [F22_inner_validation_indices.csv](F22_inner_validation_indices.csv)
- [F22_oos_indices.csv](F22_oos_indices.csv)
- [F22_refit_indices.csv](F22_refit_indices.csv)
- [F22_refit_recipe.json](F22_refit_recipe.json)
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
- [refit_binding.json](refit_binding.json)
- [refit_cohorts.csv](refit_cohorts.csv)
- [refit_final.pt](refit_final.pt)
- [refit_metrics.json](refit_metrics.json)
- [refit_scores.parquet](refit_scores.parquet)
- [refit_strata.csv](refit_strata.csv)
- [refit_target_recipe.json](refit_target_recipe.json)
