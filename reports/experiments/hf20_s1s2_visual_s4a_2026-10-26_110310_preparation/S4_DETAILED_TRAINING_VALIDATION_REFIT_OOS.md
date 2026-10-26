# S4-A detailed training, validation, refit and OOS diagnostics

All eight runs; all four roles. Inner validation selects the checkpoint; inner training/refit are in sample; OOS is retrospective annual evaluation. Online losses use dropout ON and evolving weights. OFF metrics use the complete role population at one checkpoint. NR ordinal MSE and T2R asinh MSE have different units. [Complete file index](DIAGNOSTIC_FILE_INDEX.csv).

## [HF20-S4A-F21-H4-NR-S42](HF20-S4A-F21-H4-NR-S42/RUN_DIAGNOSTICS.md)

Selected epoch 4; raw-best epoch 4. [Checkpoint selection](HF20-S4A-F21-H4-NR-S42/calibration_binding.json), [fresh refit binding](HF20-S4A-F21-H4-NR-S42/refit_binding.json), [verified stage gate](HF20-S4A-F21-H4-NR-S42/PASS.json).

| role | origins | sessions | rows | daily_ic | actual_objective | top4 | bottom4 | pair_concordance | score_sd | pair_tie_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | 11449 | 2100 | 228980 | 0.05086427 | 0.3674818 | 0.2294354 | 0.240273 | 0.5180672 | 0.02090828 | 0 |
| inner_validation | 674 | 120 | 13480 | 0.0481304 | 0.3680995 | 0.2417609 | 0.2340972 | 0.5171353 | 0.02304893 | 0 |
| refit | 12171 | 2227 | 243420 | 0.04880695 | 0.3676079 | 0.218365 | 0.2496699 | 0.5172683 | 0.0226324 | 0 |
| oos | 955 | 188 | 19100 | -0.005321352 | 0.3690579 | 0.1998005 | 0.2100557 | 0.4980865 | 0.02126692 | 0 |


### Epoch timeline

| phase | epoch | steps | online_objective | ic | qualifies | inner_train_off_loss | inner_validation_off_loss | refit_off_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| calibration | 1 | 132 | 0.3712697 | 0.007640778 | True | 0.3683369 | 0.3690411 | nan |
| calibration | 2 | 132 | 0.3688828 | 0.0257426 | True | 0.3678145 | 0.3681796 | nan |
| calibration | 3 | 132 | 0.368297 | 0.0408549 | True | 0.3676125 | 0.3678829 | nan |
| calibration | 4 | 132 | 0.3681021 | 0.0481304 | True | 0.3674818 | 0.3680995 | nan |
| calibration | 5 | 132 | 0.3678588 | 0.03120981 | False | 0.3673351 | 0.3681674 | nan |
| calibration | 6 | 132 | 0.3678564 | 0.03012149 | False | 0.3671629 | 0.3682491 | nan |
| calibration | 7 | 132 | 0.3676271 | 0.03666252 | False | 0.3669845 | 0.3680465 | nan |
| calibration | 8 | 132 | 0.3674683 | 0.04458358 | False | 0.3669176 | 0.3681896 | nan |
| calibration | 9 | 132 | 0.3673273 | 0.03227712 | False | 0.3666293 | 0.3684082 | nan |
| calibration | 10 | 132 | 0.3672378 | 0.03425565 | False | 0.3663913 | 0.3683508 | nan |
| calibration | 11 | 132 | 0.3669956 | 0.03361828 | False | 0.3662246 | 0.3686098 | nan |
| calibration | 12 | 132 | 0.3667871 | 0.03854459 | False | 0.3660157 | 0.3685817 | nan |
| calibration | 13 | 132 | 0.3667537 | 0.03421517 | False | 0.3657922 | 0.3687701 | nan |
| calibration | 14 | 132 | 0.3664605 | 0.0351426 | False | 0.3655138 | 0.3689787 | nan |
| refit | 1 | 140 | 0.3712049 | nan | None | nan | nan | 0.368304 |
| refit | 2 | 140 | 0.3688538 | nan | None | nan | nan | 0.367907 |
| refit | 3 | 140 | 0.3682887 | nan | None | nan | nan | 0.3677344 |
| refit | 4 | 140 | 0.3680295 | nan | None | nan | nan | 0.3676079 |


### Gradient/update summary

| phase | updates | max_preclip | max_postclip | clipped_batches | max_update_norm |
| --- | --- | --- | --- | --- | --- |
| calibration | 1848 | 0.3012086 | 0.3012086 | 0 | 0.08015935 |
| refit | 560 | 0.3061809 | 0.3061808 | 0 | 0.0801654 |


Every batch/parameter gradient, source-quality table, month/stock/slot breakdown and four role exports are linked in the [run file map](HF20-S4A-F21-H4-NR-S42/RUN_DIAGNOSTICS.md).

## [HF20-S4A-F21-H4-T2R-S42](HF20-S4A-F21-H4-T2R-S42/RUN_DIAGNOSTICS.md)

Selected epoch 3; raw-best epoch 3. [Checkpoint selection](HF20-S4A-F21-H4-T2R-S42/calibration_binding.json), [fresh refit binding](HF20-S4A-F21-H4-T2R-S42/refit_binding.json), [verified stage gate](HF20-S4A-F21-H4-T2R-S42/PASS.json).

| role | origins | sessions | rows | daily_ic | actual_objective | top4 | bottom4 | pair_concordance | score_sd | pair_tie_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | 11449 | 2100 | 228980 | 0.04038154 | 1.36533 | 0.2253484 | 0.2412543 | 0.5143649 | 0.03936224 | 0 |
| inner_validation | 674 | 120 | 13480 | 0.05416369 | 1.365308 | 0.2534276 | 0.2507292 | 0.5197179 | 0.04496329 | 0 |
| refit | 12171 | 2227 | 243420 | 0.04015535 | 1.363213 | 0.2241345 | 0.2418596 | 0.5144315 | 0.04745316 | 3.9389e-07 |
| oos | 955 | 188 | 19100 | 0.01520458 | 1.30277 | 0.2218592 | 0.2090267 | 0.5050957 | 0.04662139 | 0 |


### Epoch timeline

| phase | epoch | steps | online_objective | ic | qualifies | inner_train_off_loss | inner_validation_off_loss | refit_off_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| calibration | 1 | 132 | 1.372472 | 0.008110315 | True | 1.367177 | 1.368376 | nan |
| calibration | 2 | 132 | 1.368285 | 0.02115263 | True | 1.365857 | 1.367312 | nan |
| calibration | 3 | 132 | 1.366961 | 0.05416369 | True | 1.36533 | 1.365308 | nan |
| calibration | 4 | 132 | 1.366269 | 0.04224331 | False | 1.364487 | 1.365792 | nan |
| calibration | 5 | 132 | 1.36538 | 0.02530806 | False | 1.363573 | 1.365924 | nan |
| calibration | 6 | 132 | 1.365074 | 0.03039732 | False | 1.362165 | 1.366561 | nan |
| calibration | 7 | 132 | 1.363988 | 0.0407245 | False | 1.361111 | 1.366609 | nan |
| calibration | 8 | 132 | 1.363295 | 0.04594091 | False | 1.360783 | 1.366176 | nan |
| calibration | 9 | 132 | 1.362101 | 0.03145658 | False | 1.358922 | 1.368211 | nan |
| calibration | 10 | 132 | 1.361814 | 0.02985224 | False | 1.358388 | 1.367971 | nan |
| calibration | 11 | 132 | 1.360614 | 0.02689081 | False | 1.356603 | 1.368668 | nan |
| calibration | 12 | 132 | 1.35908 | 0.027135 | False | 1.355637 | 1.370063 | nan |
| calibration | 13 | 132 | 1.358932 | 0.0240808 | False | 1.354082 | 1.369674 | nan |
| refit | 1 | 140 | 1.369376 | nan | None | nan | nan | 1.364663 |
| refit | 2 | 140 | 1.365675 | nan | None | nan | nan | 1.363357 |
| refit | 3 | 140 | 1.364129 | nan | None | nan | nan | 1.363213 |


### Gradient/update summary

| phase | updates | max_preclip | max_postclip | clipped_batches | max_update_norm |
| --- | --- | --- | --- | --- | --- |
| calibration | 1716 | 1.183631 | 0.9999992 | 1 | 0.08017217 |
| refit | 420 | 0.4691769 | 0.4691769 | 0 | 0.08017209 |


Every batch/parameter gradient, source-quality table, month/stock/slot breakdown and four role exports are linked in the [run file map](HF20-S4A-F21-H4-T2R-S42/RUN_DIAGNOSTICS.md).

## [HF20-S4A-F22-H4-NR-S42](HF20-S4A-F22-H4-NR-S42/RUN_DIAGNOSTICS.md)

Selected epoch 1; raw-best epoch 1. [Checkpoint selection](HF20-S4A-F22-H4-NR-S42/calibration_binding.json), [fresh refit binding](HF20-S4A-F22-H4-NR-S42/refit_binding.json), [verified stage gate](HF20-S4A-F22-H4-NR-S42/PASS.json).

| role | origins | sessions | rows | daily_ic | actual_objective | top4 | bottom4 | pair_concordance | score_sd | pair_tie_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | 12716 | 2331 | 254320 | 0.02432038 | 0.368233 | 0.2251568 | 0.2109519 | 0.5086765 | 0.0207059 | 0 |
| inner_validation | 457 | 92 | 9140 | 0.01300953 | 0.368588 | 0.2357337 | 0.2076605 | 0.5040046 | 0.02055106 | 0 |
| refit | 13173 | 2423 | 263460 | 0.02220334 | 0.3682462 | 0.2330361 | 0.2140791 | 0.5079996 | 0.01982624 | 0 |
| oos | 1180 | 210 | 23600 | 0.01059864 | 0.3684956 | 0.2274065 | 0.2096173 | 0.5039601 | 0.02194581 | 0 |


### Epoch timeline

| phase | epoch | steps | online_objective | ic | qualifies | inner_train_off_loss | inner_validation_off_loss | refit_off_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| calibration | 1 | 146 | 0.3711745 | 0.01300953 | True | 0.368233 | 0.368588 | nan |
| calibration | 2 | 146 | 0.3688664 | 0.01116865 | False | 0.3679312 | 0.36863 | nan |
| calibration | 3 | 146 | 0.368351 | 0.006054762 | False | 0.3677419 | 0.3686621 | nan |
| calibration | 4 | 146 | 0.3681041 | -0.01555401 | False | 0.3676787 | 0.3690731 | nan |
| calibration | 5 | 146 | 0.3679758 | 0.008882381 | False | 0.3674976 | 0.3683913 | nan |
| calibration | 6 | 146 | 0.367823 | 0.007133463 | False | 0.3672331 | 0.3685658 | nan |
| calibration | 7 | 146 | 0.3676802 | 0.001142219 | False | 0.3670747 | 0.3687522 | nan |
| calibration | 8 | 146 | 0.3676094 | 0.006621457 | False | 0.3669122 | 0.368678 | nan |
| calibration | 9 | 146 | 0.36752 | 0.009667085 | False | 0.3668125 | 0.3685913 | nan |
| calibration | 10 | 146 | 0.3673661 | 0.003051145 | False | 0.3666579 | 0.3688843 | nan |
| calibration | 11 | 146 | 0.3671258 | 0.0007963395 | False | 0.3664195 | 0.3689912 | nan |
| calibration | 12 | 146 | 0.3669464 | 0.002252755 | False | 0.3663391 | 0.36908 | nan |
| refit | 1 | 152 | 0.3712984 | nan | None | nan | nan | 0.3682462 |


### Gradient/update summary

| phase | updates | max_preclip | max_postclip | clipped_batches | max_update_norm |
| --- | --- | --- | --- | --- | --- |
| calibration | 1752 | 0.3623143 | 0.3623142 | 0 | 0.08015172 |
| refit | 152 | 0.4594463 | 0.4594463 | 0 | 0.08016826 |


Every batch/parameter gradient, source-quality table, month/stock/slot breakdown and four role exports are linked in the [run file map](HF20-S4A-F22-H4-NR-S42/RUN_DIAGNOSTICS.md).

## [HF20-S4A-F22-H4-T2R-S42](HF20-S4A-F22-H4-T2R-S42/RUN_DIAGNOSTICS.md)

Selected epoch 2; raw-best epoch 2. [Checkpoint selection](HF20-S4A-F22-H4-T2R-S42/calibration_binding.json), [fresh refit binding](HF20-S4A-F22-H4-T2R-S42/refit_binding.json), [verified stage gate](HF20-S4A-F22-H4-T2R-S42/PASS.json).

| role | origins | sessions | rows | daily_ic | actual_objective | top4 | bottom4 | pair_concordance | score_sd | pair_tie_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | 12716 | 2331 | 254320 | 0.03484988 | 1.35785 | 0.2521555 | 0.1938728 | 0.5125278 | 0.03347709 | 0 |
| inner_validation | 457 | 92 | 9140 | 0.02172109 | 1.331972 | 0.2574664 | 0.1780732 | 0.5072754 | 0.03494166 | 0 |
| refit | 13173 | 2423 | 263460 | 0.03400437 | 1.356244 | 0.251928 | 0.1956513 | 0.5122556 | 0.03248409 | 0 |
| oos | 1180 | 210 | 23600 | 0.01614774 | 1.346568 | 0.2443963 | 0.182157 | 0.5057282 | 0.02952683 | 0 |


### Epoch timeline

| phase | epoch | steps | online_objective | ic | qualifies | inner_train_off_loss | inner_validation_off_loss | refit_off_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| calibration | 1 | 146 | 1.363713 | 0.009380198 | True | 1.358792 | 1.332157 | nan |
| calibration | 2 | 146 | 1.360129 | 0.02172109 | True | 1.35785 | 1.331972 | nan |
| calibration | 3 | 146 | 1.358786 | 0.006857742 | False | 1.357238 | 1.333377 | nan |
| calibration | 4 | 146 | 1.358072 | -0.005954744 | False | 1.356294 | 1.333579 | nan |
| calibration | 5 | 146 | 1.357402 | 0.01754706 | False | 1.355902 | 1.331779 | nan |
| calibration | 6 | 146 | 1.35672 | 0.01067294 | False | 1.354425 | 1.333691 | nan |
| calibration | 7 | 146 | 1.356047 | 0.006623729 | False | 1.353408 | 1.333543 | nan |
| calibration | 8 | 146 | 1.355426 | 0.01292266 | False | 1.352367 | 1.333607 | nan |
| calibration | 9 | 146 | 1.354888 | 0.009877772 | False | 1.351749 | 1.333809 | nan |
| calibration | 10 | 146 | 1.353873 | 0.002032019 | False | 1.350965 | 1.335589 | nan |
| calibration | 11 | 146 | 1.352649 | 0.00584811 | False | 1.349541 | 1.33373 | nan |
| calibration | 12 | 146 | 1.35143 | 0.007202675 | False | 1.347864 | 1.334114 | nan |
| refit | 1 | 152 | 1.362307 | nan | None | nan | nan | 1.357538 |
| refit | 2 | 152 | 1.358586 | nan | None | nan | nan | 1.356244 |


### Gradient/update summary

| phase | updates | max_preclip | max_postclip | clipped_batches | max_update_norm |
| --- | --- | --- | --- | --- | --- |
| calibration | 1752 | 0.5293971 | 0.5293971 | 0 | 0.08017511 |
| refit | 304 | 0.5324624 | 0.5324624 | 0 | 0.0801724 |


Every batch/parameter gradient, source-quality table, month/stock/slot breakdown and four role exports are linked in the [run file map](HF20-S4A-F22-H4-T2R-S42/RUN_DIAGNOSTICS.md).

## [HF20-S4A-F23-H4-NR-S42](HF20-S4A-F23-H4-NR-S42/RUN_DIAGNOSTICS.md)

Selected epoch 3; raw-best epoch 3. [Checkpoint selection](HF20-S4A-F23-H4-NR-S42/calibration_binding.json), [fresh refit binding](HF20-S4A-F23-H4-NR-S42/refit_binding.json), [verified stage gate](HF20-S4A-F23-H4-NR-S42/PASS.json).

| role | origins | sessions | rows | daily_ic | actual_objective | top4 | bottom4 | pair_concordance | score_sd | pair_tie_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | 13896 | 2547 | 277920 | 0.038832 | 0.3679586 | 0.2239944 | 0.2270046 | 0.5135899 | 0.02504602 | 0 |
| inner_validation | 453 | 86 | 9060 | 0.02993578 | 0.3680699 | 0.2221622 | 0.2332157 | 0.5111038 | 0.02122254 | 0 |
| refit | 14395 | 2640 | 287900 | 0.04263157 | 0.3677233 | 0.2351429 | 0.221812 | 0.5150966 | 0.02190459 | 0 |
| oos | 887 | 187 | 17740 | 0.009054869 | 0.3689495 | 0.2349758 | 0.1921473 | 0.5038624 | 0.02093716 | 0 |


### Epoch timeline

| phase | epoch | steps | online_objective | ic | qualifies | inner_train_off_loss | inner_validation_off_loss | refit_off_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| calibration | 1 | 160 | 0.3708376 | 0.01592204 | True | 0.3681647 | 0.3682037 | nan |
| calibration | 2 | 160 | 0.3688319 | 0.02327719 | True | 0.3679044 | 0.3683385 | nan |
| calibration | 3 | 160 | 0.3683445 | 0.02993578 | True | 0.3679586 | 0.3680699 | nan |
| calibration | 4 | 160 | 0.3680995 | 0.02070497 | False | 0.3677639 | 0.3683739 | nan |
| calibration | 5 | 160 | 0.3679281 | 0.001314661 | False | 0.3676114 | 0.3685781 | nan |
| calibration | 6 | 160 | 0.3678959 | 0.01187981 | False | 0.3673718 | 0.3684842 | nan |
| calibration | 7 | 160 | 0.3677227 | 0.009399029 | False | 0.3672555 | 0.3685878 | nan |
| calibration | 8 | 160 | 0.3676257 | 0.01147836 | False | 0.3670907 | 0.3685817 | nan |
| calibration | 9 | 160 | 0.3674983 | 0.004559098 | False | 0.3669584 | 0.3690062 | nan |
| calibration | 10 | 160 | 0.3673713 | 0.01287248 | False | 0.3668013 | 0.3687537 | nan |
| calibration | 11 | 160 | 0.3673159 | 0.02591676 | False | 0.3666498 | 0.3686594 | nan |
| calibration | 12 | 160 | 0.3672 | 0.01156104 | False | 0.3665386 | 0.3691821 | nan |
| calibration | 13 | 160 | 0.367097 | 0.0006149436 | False | 0.3662758 | 0.3694217 | nan |
| refit | 1 | 165 | 0.3709196 | nan | None | nan | nan | 0.3681666 |
| refit | 2 | 165 | 0.3687526 | nan | None | nan | nan | 0.3679448 |
| refit | 3 | 165 | 0.3684137 | nan | None | nan | nan | 0.3677233 |


### Gradient/update summary

| phase | updates | max_preclip | max_postclip | clipped_batches | max_update_norm |
| --- | --- | --- | --- | --- | --- |
| calibration | 2080 | 0.2878318 | 0.2878318 | 0 | 0.0801556 |
| refit | 495 | 0.2919651 | 0.2919651 | 0 | 0.08014325 |


Every batch/parameter gradient, source-quality table, month/stock/slot breakdown and four role exports are linked in the [run file map](HF20-S4A-F23-H4-NR-S42/RUN_DIAGNOSTICS.md).

## [HF20-S4A-F23-H4-T2R-S42](HF20-S4A-F23-H4-T2R-S42/RUN_DIAGNOSTICS.md)

Selected epoch 28; raw-best epoch 35. [Checkpoint selection](HF20-S4A-F23-H4-T2R-S42/calibration_binding.json), [fresh refit binding](HF20-S4A-F23-H4-T2R-S42/refit_binding.json), [verified stage gate](HF20-S4A-F23-H4-T2R-S42/PASS.json).

| role | origins | sessions | rows | daily_ic | actual_objective | top4 | bottom4 | pair_concordance | score_sd | pair_tie_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | 13896 | 2547 | 277920 | 0.1362147 | 1.312968 | 0.2975305 | 0.2830351 | 0.5489483 | 0.1429189 | 0 |
| inner_validation | 453 | 86 | 9060 | 0.06027298 | 1.362276 | 0.2539106 | 0.2258859 | 0.521887 | 0.1687672 | 0 |
| refit | 14395 | 2640 | 287900 | 0.1331104 | 1.314637 | 0.2989038 | 0.2726838 | 0.5476392 | 0.1419087 | 0 |
| oos | 887 | 187 | 17740 | 0.0041718 | 1.345839 | 0.2467596 | 0.2128788 | 0.5007628 | 0.1388507 | 5.629046e-06 |


### Epoch timeline

| phase | epoch | steps | online_objective | ic | qualifies | inner_train_off_loss | inner_validation_off_loss | refit_off_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| calibration | 1 | 160 | 1.357212 | 0.003777837 | True | 1.352671 | 1.348603 | nan |
| calibration | 2 | 160 | 1.354105 | 0.02687058 | True | 1.351787 | 1.348494 | nan |
| calibration | 3 | 160 | 1.35281 | 0.0266544 | False | 1.351793 | 1.347778 | nan |
| calibration | 4 | 160 | 1.35199 | 0.02658174 | False | 1.350749 | 1.348294 | nan |
| calibration | 5 | 160 | 1.351474 | 0.005739715 | False | 1.350103 | 1.349986 | nan |
| calibration | 6 | 160 | 1.351219 | 0.01741514 | False | 1.348966 | 1.349387 | nan |
| calibration | 7 | 160 | 1.350242 | 0.01710716 | False | 1.348174 | 1.350149 | nan |
| calibration | 8 | 160 | 1.349673 | 0.02316067 | False | 1.34713 | 1.349201 | nan |
| calibration | 9 | 160 | 1.348952 | 0.006279288 | False | 1.346497 | 1.352125 | nan |
| calibration | 10 | 160 | 1.348026 | 0.01695463 | False | 1.345711 | 1.35243 | nan |
| calibration | 11 | 160 | 1.347578 | 0.03316635 | True | 1.344442 | 1.350838 | nan |
| calibration | 12 | 160 | 1.346754 | 0.02069907 | False | 1.343338 | 1.353299 | nan |
| calibration | 13 | 160 | 1.345612 | 0.01237766 | False | 1.342041 | 1.353486 | nan |
| calibration | 14 | 160 | 1.344412 | 0.0256023 | False | 1.339935 | 1.354575 | nan |
| calibration | 15 | 160 | 1.342374 | 0.01687795 | False | 1.338549 | 1.357126 | nan |
| calibration | 16 | 160 | 1.341949 | 0.03290836 | False | 1.336898 | 1.35492 | nan |
| calibration | 17 | 160 | 1.340171 | 0.0265609 | False | 1.335257 | 1.355772 | nan |
| calibration | 18 | 160 | 1.338635 | 0.03572122 | True | 1.333356 | 1.356249 | nan |
| calibration | 19 | 160 | 1.337359 | 0.03562287 | False | 1.330173 | 1.357157 | nan |
| calibration | 20 | 160 | 1.335402 | 0.04543895 | True | 1.329114 | 1.360448 | nan |
| calibration | 21 | 160 | 1.333664 | 0.0346195 | False | 1.326299 | 1.361801 | nan |
| calibration | 22 | 160 | 1.332948 | 0.03778044 | False | 1.325228 | 1.361588 | nan |
| calibration | 23 | 160 | 1.330943 | 0.05120911 | True | 1.325064 | 1.366641 | nan |
| calibration | 24 | 160 | 1.329181 | 0.0376779 | False | 1.323411 | 1.36713 | nan |
| calibration | 25 | 160 | 1.327322 | 0.05530734 | True | 1.317935 | 1.360937 | nan |
| calibration | 26 | 160 | 1.325334 | 0.04812291 | False | 1.316585 | 1.366341 | nan |
| calibration | 27 | 160 | 1.324002 | 0.04788567 | False | 1.320056 | 1.367749 | nan |
| calibration | 28 | 160 | 1.322947 | 0.06027298 | True | 1.312968 | 1.362276 | nan |
| calibration | 29 | 160 | 1.320833 | 0.0389381 | False | 1.310909 | 1.370943 | nan |
| calibration | 30 | 160 | 1.319822 | 0.04209215 | False | 1.309767 | 1.376377 | nan |
| calibration | 31 | 160 | 1.31722 | 0.04478291 | False | 1.308009 | 1.376659 | nan |
| calibration | 32 | 160 | 1.31644 | 0.04108592 | False | 1.30676 | 1.378041 | nan |
| calibration | 33 | 160 | 1.314443 | 0.05072356 | False | 1.30215 | 1.376468 | nan |
| calibration | 34 | 160 | 1.313116 | 0.03304284 | False | 1.302263 | 1.384729 | nan |
| calibration | 35 | 160 | 1.31141 | 0.06034425 | False | 1.302655 | 1.369414 | nan |
| calibration | 36 | 160 | 1.308956 | 0.05039404 | False | 1.298784 | 1.383927 | nan |
| calibration | 37 | 160 | 1.306966 | 0.04402589 | False | 1.297361 | 1.384973 | nan |
| calibration | 38 | 160 | 1.306972 | 0.03866762 | False | 1.295149 | 1.383908 | nan |
| refit | 1 | 165 | 1.355973 | nan | None | nan | nan | 1.351562 |
| refit | 2 | 165 | 1.352506 | nan | None | nan | nan | 1.350669 |
| refit | 3 | 165 | 1.351754 | nan | None | nan | nan | 1.349974 |
| refit | 4 | 165 | 1.35109 | nan | None | nan | nan | 1.349294 |
| refit | 5 | 165 | 1.350215 | nan | None | nan | nan | 1.349175 |
| refit | 6 | 165 | 1.350049 | nan | None | nan | nan | 1.348008 |
| refit | 7 | 165 | 1.349203 | nan | None | nan | nan | 1.34713 |
| refit | 8 | 165 | 1.348696 | nan | None | nan | nan | 1.346275 |
| refit | 9 | 165 | 1.347912 | nan | None | nan | nan | 1.345704 |
| refit | 10 | 165 | 1.347124 | nan | None | nan | nan | 1.345205 |
| refit | 11 | 165 | 1.346335 | nan | None | nan | nan | 1.343137 |
| refit | 12 | 165 | 1.345815 | nan | None | nan | nan | 1.34204 |
| refit | 13 | 165 | 1.344951 | nan | None | nan | nan | 1.341157 |
| refit | 14 | 165 | 1.343484 | nan | None | nan | nan | 1.339346 |
| refit | 15 | 165 | 1.342208 | nan | None | nan | nan | 1.338214 |
| refit | 16 | 165 | 1.341119 | nan | None | nan | nan | 1.336261 |
| refit | 17 | 165 | 1.340014 | nan | None | nan | nan | 1.335112 |
| refit | 18 | 165 | 1.338738 | nan | None | nan | nan | 1.333979 |
| refit | 19 | 165 | 1.337297 | nan | None | nan | nan | 1.330972 |
| refit | 20 | 165 | 1.335378 | nan | None | nan | nan | 1.329995 |
| refit | 21 | 165 | 1.334312 | nan | None | nan | nan | 1.327857 |
| refit | 22 | 165 | 1.33355 | nan | None | nan | nan | 1.326738 |
| refit | 23 | 165 | 1.332044 | nan | None | nan | nan | 1.325533 |
| refit | 24 | 165 | 1.330092 | nan | None | nan | nan | 1.32319 |
| refit | 25 | 165 | 1.32871 | nan | None | nan | nan | 1.320532 |
| refit | 26 | 165 | 1.326605 | nan | None | nan | nan | 1.318171 |
| refit | 27 | 165 | 1.325146 | nan | None | nan | nan | 1.320388 |
| refit | 28 | 165 | 1.323633 | nan | None | nan | nan | 1.314637 |


### Gradient/update summary

| phase | updates | max_preclip | max_postclip | clipped_batches | max_update_norm |
| --- | --- | --- | --- | --- | --- |
| calibration | 6080 | 3.107871 | 0.9999998 | 107 | 0.08016663 |
| refit | 4620 | 1.156592 | 0.9999992 | 2 | 0.08016434 |


Every batch/parameter gradient, source-quality table, month/stock/slot breakdown and four role exports are linked in the [run file map](HF20-S4A-F23-H4-T2R-S42/RUN_DIAGNOSTICS.md).

## [HF20-S4A-F24-H4-NR-S42](HF20-S4A-F24-H4-NR-S42/RUN_DIAGNOSTICS.md)

Selected epoch 7; raw-best epoch 7. [Checkpoint selection](HF20-S4A-F24-H4-NR-S42/calibration_binding.json), [fresh refit binding](HF20-S4A-F24-H4-NR-S42/refit_binding.json), [verified stage gate](HF20-S4A-F24-H4-NR-S42/PASS.json).

| role | origins | sessions | rows | daily_ic | actual_objective | top4 | bottom4 | pair_concordance | score_sd | pair_tie_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | 14945 | 2740 | 298900 | 0.05581972 | 0.3672986 | 0.2409144 | 0.2358021 | 0.5200246 | 0.02046668 | 0 |
| inner_validation | 350 | 87 | 7000 | -0.002138063 | 0.3693771 | 0.209558 | 0.1946976 | 0.4989426 | 0.02234597 | 0 |
| refit | 15332 | 2835 | 306640 | 0.05371891 | 0.3673811 | 0.2382 | 0.2364733 | 0.5192307 | 0.02072784 | 0 |
| oos | 991 | 208 | 19820 | 0.0009395374 | 0.3689281 | 0.2057063 | 0.2084936 | 0.501 | 0.02071469 | 0 |


### Epoch timeline

| phase | epoch | steps | online_objective | ic | qualifies | inner_train_off_loss | inner_validation_off_loss | refit_off_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| calibration | 1 | 172 | 0.3708499 | -0.03741118 | True | 0.3681862 | 0.370192 | nan |
| calibration | 2 | 172 | 0.3688093 | -0.01302085 | True | 0.3679071 | 0.3693066 | nan |
| calibration | 3 | 172 | 0.3683642 | -0.02689351 | False | 0.3678841 | 0.3701663 | nan |
| calibration | 4 | 172 | 0.3681132 | -0.02803215 | False | 0.3676765 | 0.3701232 | nan |
| calibration | 5 | 172 | 0.3679264 | -0.009538748 | True | 0.3676373 | 0.3692935 | nan |
| calibration | 6 | 172 | 0.367965 | -0.01748427 | False | 0.3674015 | 0.3693822 | nan |
| calibration | 7 | 172 | 0.3677726 | -0.002138063 | True | 0.3672986 | 0.3693771 | nan |
| calibration | 8 | 172 | 0.3676442 | -0.01571873 | False | 0.3672119 | 0.3700719 | nan |
| calibration | 9 | 172 | 0.3675908 | -0.01601306 | False | 0.3669947 | 0.370102 | nan |
| calibration | 10 | 172 | 0.367474 | -0.01177813 | False | 0.366973 | 0.3702587 | nan |
| calibration | 11 | 172 | 0.3673981 | -0.02342383 | False | 0.3668073 | 0.3701115 | nan |
| calibration | 12 | 172 | 0.3672848 | -0.02860974 | False | 0.3665952 | 0.3707899 | nan |
| calibration | 13 | 172 | 0.3671736 | -0.01718343 | False | 0.3664077 | 0.3702046 | nan |
| calibration | 14 | 172 | 0.3668191 | -0.006641192 | False | 0.3662411 | 0.370721 | nan |
| calibration | 15 | 172 | 0.3667176 | -0.03175282 | False | 0.3659959 | 0.3717365 | nan |
| calibration | 16 | 172 | 0.3666681 | -0.01126601 | False | 0.3655957 | 0.3706943 | nan |
| calibration | 17 | 172 | 0.366279 | -0.02680671 | False | 0.3652035 | 0.3716069 | nan |
| refit | 1 | 178 | 0.3707954 | nan | None | nan | nan | 0.3682031 |
| refit | 2 | 178 | 0.3688611 | nan | None | nan | nan | 0.3679702 |
| refit | 3 | 178 | 0.3683996 | nan | None | nan | nan | 0.3678412 |
| refit | 4 | 178 | 0.3681852 | nan | None | nan | nan | 0.3678795 |
| refit | 5 | 178 | 0.3680051 | nan | None | nan | nan | 0.3676944 |
| refit | 6 | 178 | 0.3679278 | nan | None | nan | nan | 0.3674833 |
| refit | 7 | 178 | 0.3678096 | nan | None | nan | nan | 0.3673811 |


### Gradient/update summary

| phase | updates | max_preclip | max_postclip | clipped_batches | max_update_norm |
| --- | --- | --- | --- | --- | --- |
| calibration | 2924 | 0.2961966 | 0.2961966 | 0 | 0.0801647 |
| refit | 1246 | 0.2867953 | 0.2867953 | 0 | 0.0801449 |


Every batch/parameter gradient, source-quality table, month/stock/slot breakdown and four role exports are linked in the [run file map](HF20-S4A-F24-H4-NR-S42/RUN_DIAGNOSTICS.md).

## [HF20-S4A-F24-H4-T2R-S42](HF20-S4A-F24-H4-T2R-S42/RUN_DIAGNOSTICS.md)

Selected epoch 13; raw-best epoch 13. [Checkpoint selection](HF20-S4A-F24-H4-T2R-S42/calibration_binding.json), [fresh refit binding](HF20-S4A-F24-H4-T2R-S42/refit_binding.json), [verified stage gate](HF20-S4A-F24-H4-T2R-S42/PASS.json).

| role | origins | sessions | rows | daily_ic | actual_objective | top4 | bottom4 | pair_concordance | score_sd | pair_tie_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inner_train | 14945 | 2740 | 298900 | 0.07865822 | 1.339883 | 0.2580396 | 0.2547647 | 0.5282671 | 0.06637704 | 0 |
| inner_validation | 350 | 87 | 7000 | 0.004322835 | 1.316904 | 0.2236658 | 0.2065613 | 0.5003955 | 0.06698875 | 0 |
| refit | 15332 | 2835 | 306640 | 0.07364212 | 1.339713 | 0.2433682 | 0.2623896 | 0.5260611 | 0.06763185 | 0 |
| oos | 991 | 208 | 19820 | -0.01184016 | 1.400496 | 0.2074548 | 0.2227278 | 0.4959342 | 0.06905828 | 0 |


### Epoch timeline

| phase | epoch | steps | online_objective | ic | qualifies | inner_train_off_loss | inner_validation_off_loss | refit_off_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| calibration | 1 | 172 | 1.354837 | -0.0279877 | True | 1.350275 | 1.314046 | nan |
| calibration | 2 | 172 | 1.351547 | -0.009852587 | True | 1.349413 | 1.31352 | nan |
| calibration | 3 | 172 | 1.350552 | -0.02580808 | False | 1.349428 | 1.317521 | nan |
| calibration | 4 | 172 | 1.3498 | -0.01690552 | False | 1.348169 | 1.316062 | nan |
| calibration | 5 | 172 | 1.348987 | -0.004202913 | True | 1.347993 | 1.312617 | nan |
| calibration | 6 | 172 | 1.349032 | -0.0150071 | False | 1.34697 | 1.313222 | nan |
| calibration | 7 | 172 | 1.348193 | 0.0007716335 | True | 1.346167 | 1.313574 | nan |
| calibration | 8 | 172 | 1.347606 | -0.009751678 | False | 1.345394 | 1.315649 | nan |
| calibration | 9 | 172 | 1.347037 | -0.01489553 | False | 1.344283 | 1.316738 | nan |
| calibration | 10 | 172 | 1.346193 | -0.01090419 | False | 1.343735 | 1.319298 | nan |
| calibration | 11 | 172 | 1.345793 | -0.008514719 | False | 1.342432 | 1.315916 | nan |
| calibration | 12 | 172 | 1.344712 | -0.008901153 | False | 1.340762 | 1.319457 | nan |
| calibration | 13 | 172 | 1.343683 | 0.004322835 | True | 1.339883 | 1.316904 | nan |
| calibration | 14 | 172 | 1.341993 | -0.007146314 | False | 1.337906 | 1.320095 | nan |
| calibration | 15 | 172 | 1.340983 | -0.02128898 | False | 1.337309 | 1.32364 | nan |
| calibration | 16 | 172 | 1.340301 | -0.01229881 | False | 1.335455 | 1.322571 | nan |
| calibration | 17 | 172 | 1.338233 | -0.02694857 | False | 1.333056 | 1.326197 | nan |
| calibration | 18 | 172 | 1.336942 | -0.01229655 | False | 1.331611 | 1.325205 | nan |
| calibration | 19 | 172 | 1.33609 | -0.0291619 | False | 1.330689 | 1.329411 | nan |
| calibration | 20 | 172 | 1.334766 | -0.01195118 | False | 1.32888 | 1.323288 | nan |
| calibration | 21 | 172 | 1.333703 | -0.01326638 | False | 1.326535 | 1.325623 | nan |
| calibration | 22 | 172 | 1.331348 | -0.02648501 | False | 1.325275 | 1.331049 | nan |
| calibration | 23 | 172 | 1.330223 | -0.009761143 | False | 1.322898 | 1.326302 | nan |
| refit | 1 | 178 | 1.353103 | nan | None | nan | nan | 1.348906 |
| refit | 2 | 178 | 1.350264 | nan | None | nan | nan | 1.348108 |
| refit | 3 | 178 | 1.349222 | nan | None | nan | nan | 1.347697 |
| refit | 4 | 178 | 1.348506 | nan | None | nan | nan | 1.347269 |
| refit | 5 | 178 | 1.347839 | nan | None | nan | nan | 1.346779 |
| refit | 6 | 178 | 1.347411 | nan | None | nan | nan | 1.345538 |
| refit | 7 | 178 | 1.346849 | nan | None | nan | nan | 1.344788 |
| refit | 8 | 178 | 1.346171 | nan | None | nan | nan | 1.34393 |
| refit | 9 | 178 | 1.345601 | nan | None | nan | nan | 1.34316 |
| refit | 10 | 178 | 1.344601 | nan | None | nan | nan | 1.342683 |
| refit | 11 | 178 | 1.344043 | nan | None | nan | nan | 1.341139 |
| refit | 12 | 178 | 1.34369 | nan | None | nan | nan | 1.340048 |
| refit | 13 | 178 | 1.342525 | nan | None | nan | nan | 1.339713 |


### Gradient/update summary

| phase | updates | max_preclip | max_postclip | clipped_batches | max_update_norm |
| --- | --- | --- | --- | --- | --- |
| calibration | 3956 | 1.098861 | 0.9999993 | 1 | 0.08017571 |
| refit | 2314 | 0.7951411 | 0.795141 | 0 | 0.08016837 |


Every batch/parameter gradient, source-quality table, month/stock/slot breakdown and four role exports are linked in the [run file map](HF20-S4A-F24-H4-T2R-S42/RUN_DIAGNOSTICS.md).
