# S2-A / S2-E overnight specialization

**Status: COMPLETE — 4/4 folds.** Exploratory/post-search research, not independent confirmation.

**COMPLETE execution; NO INCREMENTAL EVIDENCE for this specialization package.** All four selected models and both predeclared routed variants are valid on the original **80,260 rows / 4,013 origins / 793 sessions**, with 20 stocks per origin. The overnight subset contains45,460 rows / 2,273 origins / 771 sessions; group session counts overlap and are not independent replications.

Primary ROUTE-SMEAR equal-year full-panel raw MSE is **0.000107517993606**, versus frozen C3 **0.000107226942123**: **+0.2714% (worse)**. All four annual full-C3 contrasts lose (+0.0078%, +0.3129%, +0.0567%, +0.5769%). Equal-year paired delta is +2.91051e−7, descriptive95% interval [+4.70415e−8, +5.29381e−7]. Intraday vectors are bit-identical; full-score changes derive only from overnight origins under their original weight masses, not50/50 group averaging.

Overnight N-SMEAR raw MSE is **0.000150570401605**: **+0.3387% versus C3**, **+0.4103% versus M1**, **+0.1905% versus OLD-N-SMEAR-MATCHED**. The respective descriptive paired95% intervals are [+8.55432e−8, +9.38438e−7], [+7.65907e−9, +1.21945e−6], and [−4.71110e−8, +6.02577e−7]. It loses to C3 in all years, M1 in three, and matched old calibration in three. The matched-control equal-year interval includes zero. No confirmatory inference is warranted on these repeatedly reviewed years.

N-RAW improves overnight MSE **1.0124% versus uncalibrated C0**, but does not establish improvement beyond the stronger calibrated controls. Full ROUTE-SMEAR beats full M1 by0.6913%, yet loses to overnight M1: the full comparison also inherits C3’s better frozen intraday branch. Do not attribute that full-M1 advantage to new overnight learning. The deployed candidate remains the predeclared smear variant; no ex-post switch to N-RAW is made.

Selected lambda/epoch: F21 .50/30, F22 .50/27, F23 0/11, F24 0/3; no exact raw-score ties. Ledger **138→154/200**:16 charged starts,20 neural phase fits, zero failed/retried fits.425 epochs /63,309 optimizer updates; fit-lifecycle sum6,746.00s, peak RSS1,137,885,184 bytes. End task store≈2.55MB and project≈12.43GB, below all inherited caps.

## Frozen experiment and preflight

Same FT16 48×16 own-stock input, 20-stock tensor axis, one-layer H32 LSTM/final-hidden dropout0.10/scalar M head,6,433 parameters, seed42, CPU float32. Same raw A=|log(Pendpoint/Porigin)| and M=log1p(A/s); no input step or origin is removed. Saved calendar/endpoint categories govern early-close morning exceptions. Price-only labels start before approximate origin+2-minute issuance; no executable-return claim.

Design A initial/selector/September-refit/Oct–Dec calibration/OOS indices exactly match Session2B/3. Eight phase recipes and positive left-median target scales reproduce before any start. No Oct–Dec label enters optimizer/epoch/lambda/scale fitting. No2025/2026 numerical access, hash, source scan, download or minute rebuild. Preflight reads OOS keys/predictors but not outcomes. Allowed hourly partitions match the original174-partition read receipt2010-07–2024-12.

Training L_N + lambda L_D uses separate equal category-session/origin/20-stock means. Full-prefix conditional origin weights are multiplied by all-role-session-count / minibatch-session-count. Thus a missing category contributes zero and the batch-session-weighted mean of fixed-model batch losses exactly equals the declared population objective. Global group denominators do not depend on a batch's category mix. AdamW/clip/session shuffle are unchanged. Selector overnight transformed MSE uses min12/patience10/max60 and0.999 qualification; selected checkpoints compete on initial-scale raw overnight MSE; exact ties prefer larger lambda. Dual selector reuse introduces selection optimism.

| year | role | group | sessions | origins | rows | conditional_weight_sum |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | inner_train | INTRADAY | 2031 | 4975 | 99500 | 1 |
| 2021 | inner_train | OVERNIGHT | 2065 | 6474 | 129480 | 1 |
| 2021 | selector | INTRADAY | 56 | 154 | 3080 | 1 |
| 2021 | selector | OVERNIGHT | 56 | 195 | 3900 | 1 |
| 2021 | restricted_refit | INTRADAY | 2095 | 5149 | 102980 | 1 |
| 2021 | restricted_refit | OVERNIGHT | 2129 | 6697 | 133940 | 1 |
| 2021 | calibration | INTRADAY | 53 | 118 | 2360 | 1 |
| 2021 | calibration | OVERNIGHT | 56 | 165 | 3300 | 1 |
| 2021 | oos | INTRADAY | 181 | 422 | 8440 | 1 |
| 2021 | oos | OVERNIGHT | 183 | 533 | 10660 | 1 |
| 2022 | inner_train | INTRADAY | 2227 | 5457 | 109140 | 1 |
| 2022 | inner_train | OVERNIGHT | 2265 | 7103 | 142060 | 1 |
| 2022 | selector | INTRADAY | 54 | 126 | 2520 | 1 |
| 2022 | selector | OVERNIGHT | 56 | 152 | 3040 | 1 |
| 2022 | restricted_refit | INTRADAY | 2289 | 5602 | 112040 | 1 |
| 2022 | restricted_refit | OVERNIGHT | 2329 | 7286 | 145720 | 1 |
| 2022 | calibration | INTRADAY | 47 | 108 | 2160 | 1 |
| 2022 | calibration | OVERNIGHT | 47 | 137 | 2740 | 1 |
| 2022 | oos | INTRADAY | 206 | 515 | 10300 | 1 |
| 2022 | oos | OVERNIGHT | 205 | 665 | 13300 | 1 |
| 2023 | inner_train | INTRADAY | 2446 | 5983 | 119660 | 1 |
| 2023 | inner_train | OVERNIGHT | 2485 | 7793 | 155860 | 1 |
| 2023 | selector | INTRADAY | 57 | 136 | 2720 | 1 |
| 2023 | selector | OVERNIGHT | 57 | 177 | 3540 | 1 |
| 2023 | restricted_refit | INTRADAY | 2511 | 6139 | 122780 | 1 |
| 2023 | restricted_refit | OVERNIGHT | 2550 | 7998 | 159960 | 1 |
| 2023 | calibration | INTRADAY | 46 | 119 | 2380 | 1 |
| 2023 | calibration | OVERNIGHT | 47 | 139 | 2780 | 1 |
| 2023 | oos | INTRADAY | 178 | 382 | 7640 | 1 |
| 2023 | oos | OVERNIGHT | 180 | 505 | 10100 | 1 |
| 2024 | inner_train | INTRADAY | 2636 | 6444 | 128880 | 1 |
| 2024 | inner_train | OVERNIGHT | 2676 | 8380 | 167600 | 1 |
| 2024 | selector | INTRADAY | 64 | 124 | 2480 | 1 |
| 2024 | selector | OVERNIGHT | 66 | 167 | 3340 | 1 |
| 2024 | restricted_refit | INTRADAY | 2708 | 6589 | 131780 | 1 |
| 2024 | restricted_refit | OVERNIGHT | 2750 | 8578 | 171560 | 1 |
| 2024 | calibration | INTRADAY | 35 | 73 | 1460 | 1 |
| 2024 | calibration | OVERNIGHT | 36 | 90 | 1800 | 1 |
| 2024 | oos | INTRADAY | 192 | 421 | 8420 | 1 |
| 2024 | oos | OVERNIGHT | 203 | 570 | 11400 | 1 |

## Candidate selection and fits

| year | lambda | selector_epochs | selected_epoch | selector_transformed_MSE | selector_raw_MSE | raw_minimum_epoch | chosen | raw_tie |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 0 | 18 | 8 | 0.31862326 | 0.00021368235 | 8 | False | False |
| 2021 | 0.1 | 18 | 8 | 0.31981595 | 0.00021692844 | 9 | False | False |
| 2021 | 0.25 | 19 | 9 | 0.32057382 | 0.00021542471 | 11 | False | False |
| 2021 | 0.5 | 40 | 30 | 0.31933689 | 0.00021326757 | 33 | True | True |
| 2022 | 0 | 23 | 13 | 0.23396825 | 8.9484855e-05 | 13 | False | False |
| 2022 | 0.1 | 23 | 13 | 0.2333129 | 9.0095581e-05 | 13 | False | False |
| 2022 | 0.25 | 23 | 13 | 0.23344958 | 9.0055628e-05 | 22 | False | False |
| 2022 | 0.5 | 37 | 27 | 0.23125029 | 8.724205e-05 | 27 | True | True |
| 2023 | 0 | 21 | 11 | 0.32147772 | 0.00021210508 | 18 | True | True |
| 2023 | 0.1 | 21 | 11 | 0.32245402 | 0.00021405741 | 11 | False | False |
| 2023 | 0.25 | 16 | 6 | 0.32433518 | 0.00021560971 | 11 | False | False |
| 2023 | 0.5 | 16 | 6 | 0.32588374 | 0.00021755757 | 6 | False | False |
| 2024 | 0 | 13 | 3 | 0.22845063 | 9.322636e-05 | 3 | True | True |
| 2024 | 0.1 | 13 | 3 | 0.2294269 | 9.4112414e-05 | 3 | False | False |
| 2024 | 0.25 | 31 | 21 | 0.22885914 | 9.3716018e-05 | 21 | False | False |
| 2024 | 0.5 | 22 | 12 | 0.23037093 | 9.3477267e-05 | 12 | False | False |

| year | lambda | selected_epoch | initial_scale | scale | seconds | peak_rss_bytes | phase_fits | charged_starts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 0.5 | 30 | 0.0057971177 | 0.0058487592 | 1579.0842 | 1137885184 | 5 | 4 |
| 2022 | 0.5 | 27 | 0.0059351246 | 0.0059334067 | 2169.9854 | 1137885184 | 5 | 4 |
| 2023 | 0 | 11 | 0.0060723344 | 0.0061216731 | 1337.6827 | 1137885184 | 5 | 4 |
| 2024 | 0 | 3 | 0.0061734035 | 0.0061744472 | 1659.251 | 1137885184 | 5 | 4 |

Four independent initial candidates plus exactly one fresh selected refit per completed year. No warm start or unselected OOS inference. Each candidate is one charged start; the selected candidate's refit is part of the same ledger pair. Maximum16 starts and20 phase fits, not20 ledger pairs. Selected checkpoint is reloaded for exact prediction equality; the same frozen model/scale produces calibration and OOS forecasts.

## Calibration and attribution

| year | c_N | old_c_N | sessions | origins | rows | n_eff | q_max | top10_share | top1pct_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 1.2723935 | 1.2807616 | 56 | 165 | 3300 | 53.007529 | 8.9757259 | 0.022697143 | 0.057914642 |
| 2022 | 1.2738221 | 1.2893719 | 47 | 137 | 2740 | 44.696801 | 8.1514938 | 0.02422599 | 0.054468425 |
| 2023 | 1.1521248 | 1.1897269 | 47 | 139 | 2780 | 44.983946 | 4.87053 | 0.029193398 | 0.063234908 |
| 2024 | 1.1982353 | 1.2531015 | 36 | 90 | 1800 | 32.95592 | 10.293196 | 0.056033444 | 0.083116092 |

One predefined overnight smear per selected model, plus the identical operation on saved old C0. Both use original calibration row weights restricted to overnight and normalized, and the same September scale. No partial pooling, multiplier choice, trimming or OOS repair. N-RAW remains the historical inverse. ROUTE-RAW/ROUTE-SMEAR denote N-RAW/N-SMEAR in the OVERNIGHT rows; full rows hard-route frozen C3 intraday. OLD-N-SMEAR-MATCHED full rows also retain C3 intraday; its scientific role is the overnight matched-calibration control. F24 has limited calibration-tail precision.

## Annual and equal-year matched scores

| year | scope | arm | raw_MSE | raw_MAE | ratio | magnitude_IC |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | FULL | ROUTE-SMEAR | 8.3327117e-05 | 0.0064492685 | 1.0612155 | 0.31862102 |
| 2021 | FULL | OLD-N-SMEAR-MATCHED | 8.3489624e-05 | 0.0064712404 | 1.0713161 | 0.31785841 |
| 2021 | FULL | C3 | 8.3320658e-05 | 0.006421753 | 1.051615 | 0.31785841 |
| 2021 | FULL | M1 | 8.3790671e-05 | 0.0063963177 | 1.0413212 | 0.31785841 |
| 2021 | OVERNIGHT | ROUTE-SMEAR | 0.000115095 | 0.0078408344 | 1.0435177 | 0.34454639 |
| 2021 | OVERNIGHT | OLD-N-SMEAR-MATCHED | 0.00011538796 | 0.0078804441 | 1.0584396 | 0.34385579 |
| 2021 | OVERNIGHT | C3 | 0.00011508336 | 0.0077912311 | 1.0293347 | 0.34385579 |
| 2021 | OVERNIGHT | M1 | 0.000114885 | 0.0076123218 | 0.9737022 | 0.34385579 |
| 2022 | FULL | ROUTE-SMEAR | 0.00014713463 | 0.0084631834 | 1.0502901 | 0.3480789 |
| 2022 | FULL | OLD-N-SMEAR-MATCHED | 0.0001469488 | 0.0084537523 | 1.048428 | 0.35029686 |
| 2022 | FULL | C3 | 0.00014667567 | 0.0083746314 | 1.022093 | 0.35029686 |
| 2022 | FULL | M1 | 0.00014937987 | 0.0086367779 | 1.0972351 | 0.35029686 |
| 2022 | OVERNIGHT | ROUTE-SMEAR | 0.00020395673 | 0.010274415 | 1.0569303 | 0.36032459 |
| 2022 | OVERNIGHT | OLD-N-SMEAR-MATCHED | 0.00020362219 | 0.010257435 | 1.0541509 | 0.36406382 |
| 2022 | OVERNIGHT | C3 | 0.00020313046 | 0.010114992 | 1.0148448 | 0.36406382 |
| 2022 | OVERNIGHT | M1 | 0.00020299311 | 0.010159313 | 1.0355511 | 0.36406382 |
| 2023 | FULL | ROUTE-SMEAR | 8.6307112e-05 | 0.0060404331 | 0.99649602 | 0.31437885 |
| 2023 | FULL | OLD-N-SMEAR-MATCHED | 8.6194901e-05 | 0.006062 | 1.0139485 | 0.32024473 |
| 2023 | FULL | C3 | 8.6258208e-05 | 0.0060253978 | 0.99597907 | 0.32024473 |
| 2023 | FULL | M1 | 8.6602732e-05 | 0.0059913023 | 0.97373398 | 0.32024473 |
| 2023 | OVERNIGHT | ROUTE-SMEAR | 0.00012250317 | 0.0073240763 | 0.97694016 | 0.31299777 |
| 2023 | OVERNIGHT | OLD-N-SMEAR-MATCHED | 0.00012230401 | 0.0073623548 | 1.0027042 | 0.32418964 |
| 2023 | OVERNIGHT | C3 | 0.00012241637 | 0.0072973906 | 0.97617703 | 0.32418964 |
| 2023 | OVERNIGHT | M1 | 0.00012292872 | 0.0071905228 | 0.92581073 | 0.32418964 |
| 2024 | FULL | ROUTE-SMEAR | 0.00011330312 | 0.0065060406 | 1.0741179 | 0.31150401 |
| 2024 | FULL | OLD-N-SMEAR-MATCHED | 0.00011277253 | 0.0064709671 | 1.06956 | 0.3102724 |
| 2024 | FULL | C3 | 0.00011265323 | 0.0063823356 | 1.0374614 | 0.3102724 |
| 2024 | FULL | M1 | 0.00011329232 | 0.00651156 | 1.0809517 | 0.3102724 |
| 2024 | OVERNIGHT | ROUTE-SMEAR | 0.0001607267 | 0.0077943168 | 1.0636616 | 0.32032846 |
| 2024 | OVERNIGHT | OLD-N-SMEAR-MATCHED | 0.00015982199 | 0.0077345124 | 1.0571371 | 0.31773178 |
| 2024 | OVERNIGHT | C3 | 0.00015961857 | 0.0075833854 | 1.011189 | 0.31773178 |
| 2024 | OVERNIGHT | M1 | 0.00015901377 | 0.0075724715 | 1.01482 | 0.31773178 |

All arms, including raw routed, O1 and the four B0 controls:

| year | scope | arm | raw_MSE | raw_MAE | observed | predicted | bias | ratio | magnitude_IC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EQ | FULL | ROUTE-RAW | 0.00011347005 | 0.0066164686 | 0.01031327 | 0.0088252562 | -0.0014880143 | 0.85571848 | 0.32314569 |
| EQ | FULL | ROUTE-SMEAR | 0.00010751799 | 0.0068647314 | 0.01031327 | 0.010789359 | 0.00047608896 | 1.0461628 | 0.32314569 |
| EQ | FULL | OLD-N-SMEAR-MATCHED | 0.00010735147 | 0.0068644899 | 0.01031327 | 0.010837908 | 0.00052463721 | 1.0508701 | 0.3246681 |
| EQ | FULL | C3 | 0.00010722694 | 0.0068010295 | 0.01031327 | 0.010588584 | 0.00027531389 | 1.0266951 | 0.3246681 |
| EQ | FULL | M1 | 0.0001082664 | 0.0068839895 | 0.01031327 | 0.010855766 | 0.00054249545 | 1.0526017 | 0.3246681 |
| EQ | FULL | C1a | 0.00010821865 | 0.0068159348 | 0.01031327 | 0.01050088 | 0.00018760952 | 1.0181911 | 0.3246681 |
| EQ | FULL | C0 | 0.00011478357 | 0.0064974483 | 0.01031327 | 0.0080327552 | -0.0022805153 | 0.77887564 | 0.3246681 |
| EQ | FULL | O1 | 0.00010857813 | 0.0067282128 | 0.01031327 | 0.010041315 | -0.00027195542 | 0.97363054 | 0.31955938 |
| EQ | FULL | B0-VOL | 0.00011156042 | 0.0070127696 | 0.01031327 | 0.010600902 | 0.00028763119 | 1.0278894 | 0.30414316 |
| EQ | FULL | B0-CLOCK | 0.00011466954 | 0.0068390848 | 0.01031327 | 0.0095054397 | -0.00080783078 | 0.92167075 | 0.3028002 |
| EQ | FULL | B0-RMEAN | 0.00012236442 | 0.0071296126 | 0.01031327 | 0.0095165809 | -0.00079668959 | 0.92275102 | 0.30023827 |
| EQ | FULL | B0-RMED | 0.00013809216 | 0.006949601 | 0.01031327 | 0.006474016 | -0.0038392545 | 0.62773647 | 0.29611443 |
| EQ | OVERNIGHT | ROUTE-RAW | 0.00016118317 | 0.0078705586 | 0.012430622 | 0.0094063062 | -0.0030243159 | 0.75670438 | 0.3345493 |
| EQ | OVERNIGHT | ROUTE-SMEAR | 0.0001505704 | 0.0083084105 | 0.012430622 | 0.012894285 | 0.00046366246 | 1.0373 | 0.3345493 |
| EQ | OVERNIGHT | OLD-N-SMEAR-MATCHED | 0.00015028404 | 0.0083086867 | 0.012430622 | 0.012981723 | 0.00055110082 | 1.0443341 | 0.33746026 |
| EQ | OVERNIGHT | C3 | 0.00015006219 | 0.0081967497 | 0.012430622 | 0.012540867 | 0.00011024505 | 1.0088688 | 0.33746026 |
| EQ | OVERNIGHT | M1 | 0.00014995515 | 0.0081336573 | 0.012430622 | 0.012325338 | -0.00010528415 | 0.99153026 | 0.33746026 |
| EQ | OVERNIGHT | C1a | 0.00015069462 | 0.0080401879 | 0.012430622 | 0.011782335 | -0.00064828738 | 0.94784755 | 0.33746026 |
| EQ | OVERNIGHT | C0 | 0.00016283167 | 0.0078555806 | 0.012430622 | 0.0091219793 | -0.0033086427 | 0.73383128 | 0.33746026 |
| EQ | OVERNIGHT | O1 | 0.00015149878 | 0.0080030653 | 0.012430622 | 0.011403309 | -0.0010273135 | 0.91735623 | 0.33527113 |
| EQ | OVERNIGHT | B0-VOL | 0.00015427534 | 0.0083224134 | 0.012430622 | 0.012375953 | -5.4669465e-05 | 0.99560203 | 0.31794838 |
| EQ | OVERNIGHT | B0-CLOCK | 0.00016039776 | 0.0082545149 | 0.012430622 | 0.011251787 | -0.0011788349 | 0.90516686 | 0.30998426 |
| EQ | OVERNIGHT | B0-RMEAN | 0.00016847754 | 0.0080917289 | 0.012430622 | 0.0095165809 | -0.0029140412 | 0.7655756 | 0.30682653 |
| EQ | OVERNIGHT | B0-RMED | 0.00019875051 | 0.0084401769 | 0.012430622 | 0.006474016 | -0.0059566061 | 0.52081191 | 0.30177131 |

Raw MSE is in squared log-return units; MAE/means/bias in absolute log-return units. Full-panel weights are unchanged, never50/50 by category. Conditional raw scores restrict and renormalize canonical weights within year. Ranking uses existing within-origin midrank→group-session→year reducer. EQ averages annual metrics and uses the ratio of equal-year means. No four-year value is produced before four valid folds.

## Paired uncertainty

| scope | left | right | year | delta | low | high | percent | includes_zero |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FULL | ROUTE-SMEAR | C3 | 2021 | 6.4586059e-09 | -4.0399916e-07 | 3.8081436e-07 | 0.0077515061 | True |
| FULL | ROUTE-SMEAR | C3 | 2022 | 4.5895603e-07 | -6.5042196e-08 | 1.0152523e-06 | 0.31290535 | True |
| FULL | ROUTE-SMEAR | C3 | 2023 | 4.8904602e-08 | -2.4711897e-07 | 4.0010266e-07 | 0.056695592 | True |
| FULL | ROUTE-SMEAR | C3 | 2024 | 6.4988669e-07 | -1.9952046e-07 | 1.295182e-06 | 0.57689131 | True |
| FULL | ROUTE-SMEAR | C3 | EQ | 2.9105148e-07 | 4.704149e-08 | 5.2938106e-07 | 0.27143503 | False |
| FULL | ROUTE-SMEAR | M1 | 2021 | -4.6355386e-07 | -1.4645717e-06 | 3.3508664e-07 | -0.55322849 | True |
| FULL | ROUTE-SMEAR | M1 | 2022 | -2.2452455e-06 | -3.1190541e-06 | -1.2178294e-06 | -1.5030442 | False |
| FULL | ROUTE-SMEAR | M1 | 2023 | -2.956192e-07 | -7.4332249e-07 | 1.9161657e-07 | -0.34135089 | True |
| FULL | ROUTE-SMEAR | M1 | 2024 | 1.0796246e-08 | -6.4302375e-07 | 6.3533434e-07 | 0.0095295482 | True |
| FULL | ROUTE-SMEAR | M1 | EQ | -7.4840558e-07 | -1.0855818e-06 | -3.5462094e-07 | -0.69126302 | False |
| FULL | ROUTE-SMEAR | B0-VOL | 2021 | -3.2088043e-06 | -4.866173e-06 | -1.3291245e-06 | -3.7080605 | False |
| FULL | ROUTE-SMEAR | B0-VOL | 2022 | -6.5617937e-06 | -8.4580228e-06 | -4.2762741e-06 | -4.2693211 | False |
| FULL | ROUTE-SMEAR | B0-VOL | 2023 | -3.9215761e-06 | -6.3146931e-06 | -2.2439174e-06 | -4.346263 | False |
| FULL | ROUTE-SMEAR | B0-VOL | 2024 | -2.4775365e-06 | -3.4596888e-06 | -1.4570328e-06 | -2.1398536 | False |
| FULL | ROUTE-SMEAR | B0-VOL | EQ | -4.0424277e-06 | -4.9224069e-06 | -3.1240525e-06 | -3.6235321 | False |
| OVERNIGHT | ROUTE-SMEAR | C3 | 2021 | 1.1643185e-08 | -7.067676e-07 | 6.9212825e-07 | 0.010117176 | True |
| OVERNIGHT | ROUTE-SMEAR | C3 | 2022 | 8.2627262e-07 | -1.1704926e-07 | 1.8820673e-06 | 0.40676944 | True |
| OVERNIGHT | ROUTE-SMEAR | C3 | 2023 | 8.6799562e-08 | -4.4540466e-07 | 7.1849585e-07 | 0.07090519 | True |
| OVERNIGHT | ROUTE-SMEAR | C3 | 2024 | 1.1081333e-06 | -3.4115986e-07 | 2.185333e-06 | 0.69423834 | True |
| OVERNIGHT | ROUTE-SMEAR | C3 | EQ | 5.0821217e-07 | 8.5543184e-08 | 9.3843764e-07 | 0.3386677 | False |
| OVERNIGHT | ROUTE-SMEAR | M1 | 2021 | 2.0999841e-07 | -1.6864186e-06 | 1.7674157e-06 | 0.1827901 | True |
| OVERNIGHT | ROUTE-SMEAR | M1 | 2022 | 9.636264e-07 | 3.0097258e-07 | 1.6066872e-06 | 0.47470893 | False |
| OVERNIGHT | ROUTE-SMEAR | M1 | 2023 | -4.2554824e-07 | -1.3548812e-06 | 4.6353231e-07 | -0.34617479 | True |
| OVERNIGHT | ROUTE-SMEAR | M1 | 2024 | 1.7129338e-06 | 6.1860906e-07 | 2.7581546e-06 | 1.0772236 | False |
| OVERNIGHT | ROUTE-SMEAR | M1 | EQ | 6.152526e-07 | 7.65907e-09 | 1.2194469e-06 | 0.41029108 | False |
| OVERNIGHT | ROUTE-SMEAR | OLD-N-SMEAR-MATCHED | 2021 | -2.9295848e-07 | -1.0667853e-06 | 2.810155e-07 | -0.25388999 | True |
| OVERNIGHT | ROUTE-SMEAR | OLD-N-SMEAR-MATCHED | 2022 | 3.3454637e-07 | -1.1443783e-07 | 7.5697379e-07 | 0.1642976 | True |
| OVERNIGHT | ROUTE-SMEAR | OLD-N-SMEAR-MATCHED | 2023 | 1.9916149e-07 | -2.9022526e-07 | 7.8688713e-07 | 0.16284134 | True |
| OVERNIGHT | ROUTE-SMEAR | OLD-N-SMEAR-MATCHED | 2024 | 9.0470673e-07 | 8.0643083e-09 | 1.7690192e-06 | 0.56607148 | False |
| OVERNIGHT | ROUTE-SMEAR | OLD-N-SMEAR-MATCHED | EQ | 2.8636403e-07 | -4.7111006e-08 | 6.0257732e-07 | 0.19054853 | True |
| OVERNIGHT | ROUTE-RAW | C0 | 2021 | 4.362016e-07 | -2.7099775e-08 | 9.0133687e-07 | 0.34184015 | True |
| OVERNIGHT | ROUTE-RAW | C0 | 2022 | -2.2886803e-06 | -2.9915487e-06 | -1.455666e-06 | -1.0254947 | False |
| OVERNIGHT | ROUTE-RAW | C0 | 2023 | -1.3804355e-06 | -2.0276566e-06 | -7.3184589e-07 | -1.0580735 | False |
| OVERNIGHT | ROUTE-RAW | C0 | 2024 | -3.3610791e-06 | -5.3858406e-06 | -1.9054584e-06 | -1.9762027 | False |
| OVERNIGHT | ROUTE-RAW | C0 | EQ | -1.6484983e-06 | -2.2438684e-06 | -1.1440002e-06 | -1.0123942 | False |

400 whole-month draws, seed22042, year-stratified EQ; full stocks/origins/sessions remain together. The existing month-bootstrap construction is extended only to retain group weight numerator and mass together, avoiding incorrect equal weighting of low-coverage category sessions. Full-panel results reduce to the old convention. Intervals are descriptive, conditional on selected networks and scalars; lambda/epoch selection and calibration uncertainty are not propagated or selection-adjusted.

## Clocks, ordinary periods, tails and magnitude ordering

The overnight mean ratio moves from C3 **1.00887** to N-SMEAR **1.03730**, and overnight MAE worsens from0.00819675 to0.00830841. Full-system ratio is1.04616 versus C3 1.02670; full MAE0.00686473 versus0.00680103. N-RAW has ratio0.75670, slightly above uncalibrated C0 0.73383; changed output level can explain some uncalibrated score gain without proving new discrimination.

Overnight prefix95/99 event MSE improves **2.0424% /1.3780% versus C3**, but ordinary complements worsen **5.2887% /1.7137%**. Against the same-operation old smear, even event MSE is worse (+0.4800% /+0.2423%). Event amplitude ratios remain0.37771 /0.24282; these are outcome-selected cohorts, not proof of conditional-mean bias or calibrated event probabilities. Overnight prefix95/99 false-low rank fractions rise from18.1269% /13.1764% to18.3364% /14.0291%. No event head or event threshold is fitted.

15:30 MSE improves0.3545% versus C3 and its mean ratio improves0.91902→0.95731, while12:30 MSE worsens0.9186% and its ratio rises1.04706→1.10425. The15:30 score remains0.1894% worse than matched old smearing. Morning-slot rows may change slightly because saved early-close OVERNIGHT origins occur there; genuine INTRADAY-category scores remain exactly unchanged. The scheduled early-close subset improves MSE on point estimates but worsens MAE, with small counts; do not treat it as a separate independent success.

Overnight magnitude IC declines **0.337460→0.334549**; full IC declines0.324668→0.323146. Pair concordance also falls (overnight0.621934→0.621077), while top-four retrieval rises slightly (0.426739→0.429455). This is mixed ranking evidence, not a new signed alpha. All score pair-tie/constant rates are zero.

Smearing factors are1.27239 /1.27382 /1.15212 /1.19824. Residual moments are finite and not dominated by one or ten rows under the reported concentration summaries; F24 remains least precise (36 overnight sessions,n_eff32.96; maximum q10.2932, top10 contribution5.6033%, top1%8.3116%). No trimming or fallback was used. Reliability CSV rows use common saved-C3 bin membership; EQ subgroup rows are emitted only when present in all four years.

| field | group | rows | sessions | raw_MSE | raw_MAE | ratio | raw_MSE_loss_share | false_low_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| category | INTRADAY | 34800 | 757 | 5.1382745e-05 | 0.0049946708 | 1.0650974 | 0.20846957 | 0.5 |
| category | OVERNIGHT | 45460 | 771 | 0.0001505704 | 0.0083084105 | 1.0373 | 0.79153043 | 0.5 |
| slot | 09:30 | 9900 | 495 | 8.563817e-05 | 0.006535637 | 1.0138578 | 0.096476933 | 0.5 |
| slot | 10:30 | 12200 | 610 | 4.3150317e-05 | 0.0047248001 | 1.0763134 | 0.060858258 | 0.5 |
| slot | 11:30 | 12920 | 646 | 3.5615845e-05 | 0.0042165386 | 1.1101517 | 0.055612503 | 0.5 |
| slot | 12:30 | 12000 | 600 | 0.00013562041 | 0.0079961437 | 1.1042504 | 0.19487469 | 0.5 |
| slot | 13:30 | 10800 | 540 | 0.00015881954 | 0.0084665896 | 1.0538772 | 0.18666075 | 0.5 |
| slot | 14:30 | 10940 | 547 | 0.00014583619 | 0.0083640222 | 1.0423128 | 0.17697353 | 0.5 |
| slot | 15:30 | 11500 | 575 | 0.00016509952 | 0.0084537343 | 0.95730964 | 0.22854333 | 0.5 |
| tail_OVERNIGHT | PREFIX95 | 4201 | 638 | 0.0011608298 | 0.028257525 | 0.37770971 | 0.48570992 | 0.18336369 |
| tail_OVERNIGHT | LE_PREFIX95 | 41259 | 771 | 6.4483355e-05 | 0.0065541 | 1.3334184 | 0.30582051 | 0.52959714 |
| tail_OVERNIGHT | PREFIX99 | 745 | 226 | 0.0039451757 | 0.057878534 | 0.24282428 | 0.29508191 | 0.1402906 |
| tail_OVERNIGHT | LE_PREFIX99 | 44715 | 771 | 9.6308032e-05 | 0.007588934 | 1.1156401 | 0.49644852 | 0.50552492 |

| scope | arm | magnitude_IC | pair_concordance | top4 | bottom4 | tie_rate | constant_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FULL | ROUTE-RAW | 0.32314569 | 0.61682474 | 0.42584364 | 0.29902299 | 0 | 0 |
| FULL | ROUTE-SMEAR | 0.32314569 | 0.61682474 | 0.42584364 | 0.29902299 | 0 | 0 |
| FULL | OLD-N-SMEAR-MATCHED | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| FULL | C3 | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| FULL | M1 | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| FULL | C0 | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| OVERNIGHT | ROUTE-RAW | 0.3345493 | 0.62107732 | 0.42945534 | 0.30937645 | 0 | 0 |
| OVERNIGHT | ROUTE-SMEAR | 0.3345493 | 0.62107732 | 0.42945534 | 0.30937645 | 0 | 0 |
| OVERNIGHT | OLD-N-SMEAR-MATCHED | 0.33746026 | 0.62193351 | 0.426739 | 0.30933661 | 0 | 0 |
| OVERNIGHT | C3 | 0.33746026 | 0.62193351 | 0.426739 | 0.30933661 | 0 | 0 |
| OVERNIGHT | M1 | 0.33746026 | 0.62193351 | 0.426739 | 0.30933661 | 0 | 0 |
| OVERNIGHT | C0 | 0.33746026 | 0.62193351 | 0.426739 | 0.30933661 | 0 | 0 |

Prefix95/99 thresholds are unchanged September-prefix quantiles. Tail loss shares are unconditional contributions to the full routed score; conditional tables normalize their own mass. False-low means within-origin average rank≤10.5; denominator is the declared cohort's original weight. These outcome-selected cohorts are retrospective, not calibrated event probabilities. Shared reliability memberships are ten saved-C3 weighted deciles per year, with separate overnight rows; no bin is fitted into a correction. Pair ties get half credit; true ties are excluded; retrieval uses fractional boundary ties. New night weights may change stock ordering, unlike scalar-only calibration.

## Scientific decision

**Do not promote the overnight specialist. Retain the provisional full C3 system and C1a/M1 benchmarks.** The predeclared joint criterion fails: the specialized calibrated model does not beat C3/M1/matched old calibration, every annual full-C3 point comparison loses, mean calibration/MAE worsen, and average rank association falls. Its small uncalibrated improvement and stronger tail amplitudes do not establish incremental recurrent information. This is evidence against this specific loss-weighting + overnight-monitor + selector package, not proof that overnight predictability is impossible or that only one mathematical loss caused the result.

Do not widen the lambda grid, rerun seeds, choose N-RAW ex post or retrofit calibration after seeing these outcomes. If the researcher requests another Stage2 test, **S2-B explicit known-clock information is the more direct separately gated question** suggested by the opposing12:30/15:30 level errors; that is a research choice, not authorization. S2-C jump decomposition and S2-D new holding targets are not established as needed by these four-hour magnitude results and require their own labels, timing, controls and approval. No actual jump detection, options mispricing or tradeability claim follows.

The two-group objective uses separately normalized training group-session means, whereas scalar calibration deliberately preserves the existing canonical calibration-row weights restricted to N. The documented selector is reused for epochs and four-way lambda choice, inducing development optimism; the dependent-time intervals condition on selected weights/scalars and omit their estimation/selection uncertainty. All2021–24 outcomes remain post-search exploratory. F24’s selected epoch3 is valid under the original minimum12 selector-duration rule (its selector ran13 epochs); it was neither forced upward nor retrained.

## Reproduction, integrity and stop

`.venv/bin/python -m lstm_data.hf20_overnight_specialist --preflight`; initial `--run` executes only this frozen campaign; `--report` replays completed saved selected scores without inference/refitting. Started namespaces cannot be rerun. Source inputs/old predictors are referenced, never copied; only selected new night scores and one final checkpoint per year are saved. Protocol contains source/recipe/role bindings and resource caps; selection/training traces contain no unselected OOS scores.

Final focused tests: `.venv/bin/python -m pytest tests/test_hf20_overnight_specialist.py tests/test_hf20_mag_c3_io.py -q` — **10 passed** (4.06s). Ruff command: `.venv/bin/ruff check src/lstm_data/hf20_overnight_specialist.py tests/test_hf20_overnight_specialist.py --output-format concise` — PASS. Full-project static command: `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist` — **508 files, zero errors/warnings** (95.923s). Select repository `.venv/bin/python`, Pylance basic and refresh editor Problems; actual editor refresh remains human-confirmed. No ignore/severity/exclusion changes. The five new fixtures verify separate group means and zero D-label gradient at lambda0, exact fixed-model minibatch aggregation with a missing group, deterministic raw-score lambda ties, saved-category early-close hard routing/decoder identities, and conditional month-mass bootstrap parity with the historical full-panel construction. A toy fixture has L_N=9,L_D=10,lambda=.25 giving11.5; signs cannot leak through abs(R).

All eight phase recipes/scales reproduce exactly; selected checkpoint reload error is zero in all folds; the same frozen model hash supplies calibration/OOS. Canonical full key coverage and all previous C3 annual metrics reproduce; intraday scores are bit-identical. New code/tests match pre-fit readiness hashes. Original score/recipe/journal bindings are unchanged. The only existing file changed is the authorized current-registry successor pointer (schema26→27); previous journals remain untouched. No unselected OOS forecasts, no2025/2026 numerical/hash access, download, new source, dashboard or trading work. Standard handoff: `reports/codex_sessions/2026-10-28_114629_hf20_stage2_s2a_s2e_overnight.md`.

STOP. No S2-B/C/D, event head, alternate seed/lambda, new jump target, trade/options analysis or protected confirmation.
