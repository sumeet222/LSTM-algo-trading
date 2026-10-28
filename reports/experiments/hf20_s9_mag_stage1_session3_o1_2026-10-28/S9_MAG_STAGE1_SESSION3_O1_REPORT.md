# S9 MAG Stage1 / Session3 — O1 direct expected absolute magnitude

**Status: COMPLETE.** 4/4 folds; exploratory/post-search.

Ledger 134→138/200; 4 new pairs / 8 phase fits. No empirical neural failure/retry. One preparation-only checker correction occurred before any neural start and is disclosed below.

## Executive result

**NO INCREMENTAL EVIDENCE on the declared raw-mean task.** All four valid O1 folds completed on the original **80,260 rows / 4,013 origins / 793 sessions**. Ledger **134→138/200**, four new pairs/eight neural phases, one seed42, zero failed/aborted empirical fits or model retries.

- Equal-year O1 raw MSE **0.00010857812935** is **+0.332% versus C1a** (0.00010821865303) and **+0.288% versus M1** (0.00010826639919). Paired O1−C1a = +3.595e−7, descriptive95% interval [−1.588e−7,+9.124e−7]; O1−M1 = +3.117e−7 [−2.803e−7,+8.532e−7]. Both include zero: no robust incremental advantage, not proof of universal inferiority.
- O1 loses both calibrated annual point comparisons in F21–F23 and wins both in F24. Versus C1a: **+1.148%, +0.785%, +0.254%, −0.805%**; versus M1: **+1.767%, +0.005%, +0.524%, −0.614%**. The primary hypothesis of lower equal-year MSE than the better calibrated baseline is not met.
- O1 improves MSE **5.41% versus C0**, **2.67% versus B0-VOL**, and **5.31% versus B0-CLOCK** equal-year. It beats B0-VOL in annual points, but B0-CLOCK slightly wins F23. These useful comparisons do not replace the principal C1a/M1 competition.
- O1 MAE **0.006728213** improves **1.29%/2.26% versus C1a/M1**, while worsening **3.55% versus C0**. Mean ratio **0.974**, versus C0/C1a/M1 **0.779/1.018/1.053**, is a large level improvement over C0 but not a uniformly better mean forecast than C1a.
- Within-origin magnitude IC is **0.319559 versus 0.324668** for C0/C1a/M1. Event diagnostics are mixed, not evidence for an event-assisted model. Overnight/ordinary/tail trade-offs remain.

**Recommendation:** favor the existing calibrated predecessor for this raw-mean task; retain O1 as a distinct MAE/level trade-off, not a replacement winner. No additional fitting is launched.

## Frozen objective, model and chronology

A=abs(log(P_endpoint/P_origin)); Ahat=s·torch.softplus(z). Loss is mean session → mean origin → mean20 ((Ahat−A)/s)^2. Positive prefix s is the weighted left median of raw A, floored at1e−8. This changes the objective, output link and target-appropriate checkpoint monitor together; it does not isolate only an algebraic loss change.

The shared LSTM remains 48×16 FT16, one H32 layer, final-hidden dropout0.10, scalar linear head, zero state per window and6,433 parameters. CPU float32, seed42, AdamW .001/(.9,.999)/eps1e−8, matrix decay.01/bias0, clip1,16 complete sessions per batch; shuffle RNG42+epoch. Qualify first finite nonnegative score, then loss≤.999×qualified best; min12,patience10,max60. Fresh same-seed/empty-optimizer September refit uses the selected count. No EVENT head/weight, alternative link, calibration or new information.

| year | role | start | cutoff | first_date | last_date | sessions | origins | stock_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | inner_train | 2011-04-01 | 2020-06-30 | 2011-04-01 | 2020-06-30 | 2100 | 11449 | 228980 |
| 2021 | selector | 2020-07-01 | 2020-09-30 | 2020-07-13 | 2020-09-30 | 57 | 349 | 6980 |
| 2021 | restricted_refit | 2011-04-01 | 2020-09-30 | 2011-04-01 | 2020-09-30 | 2164 | 11846 | 236920 |
| 2021 | calibration | 2020-10-01 | 2020-12-31 | 2020-10-12 | 2020-12-30 | 56 | 283 | 5660 |
| 2021 | oos | 2021-01-01 | 2021-12-31 | 2021-01-13 | 2021-12-31 | 188 | 955 | 19100 |
| 2022 | inner_train | 2011-04-01 | 2021-04-30 | 2011-04-01 | 2021-04-30 | 2301 | 12560 | 251200 |
| 2022 | selector | 2021-05-01 | 2021-09-30 | 2021-05-12 | 2021-09-30 | 58 | 278 | 5560 |
| 2022 | restricted_refit | 2011-04-01 | 2021-09-30 | 2011-04-01 | 2021-09-30 | 2366 | 12888 | 257760 |
| 2022 | calibration | 2021-10-01 | 2021-12-31 | 2021-10-12 | 2021-12-31 | 50 | 245 | 4900 |
| 2022 | oos | 2022-01-01 | 2022-12-31 | 2022-01-12 | 2022-12-30 | 210 | 1180 | 23600 |
| 2023 | inner_train | 2011-04-01 | 2022-05-31 | 2011-04-01 | 2022-05-31 | 2526 | 13776 | 275520 |
| 2023 | selector | 2022-06-01 | 2022-09-30 | 2022-06-10 | 2022-09-27 | 59 | 313 | 6260 |
| 2023 | restricted_refit | 2011-04-01 | 2022-09-30 | 2011-04-01 | 2022-09-27 | 2592 | 14137 | 282740 |
| 2023 | calibration | 2022-10-01 | 2022-12-30 | 2022-10-13 | 2022-12-30 | 48 | 258 | 5160 |
| 2023 | oos | 2023-01-01 | 2023-12-31 | 2023-01-13 | 2023-12-29 | 187 | 887 | 17740 |
| 2024 | inner_train | 2011-04-01 | 2023-05-31 | 2011-04-01 | 2023-05-31 | 2719 | 14824 | 296480 |
| 2024 | selector | 2023-06-01 | 2023-09-29 | 2023-06-12 | 2023-09-29 | 69 | 291 | 5820 |
| 2024 | restricted_refit | 2011-04-01 | 2023-09-29 | 2011-04-01 | 2023-09-29 | 2795 | 15167 | 303340 |
| 2024 | calibration | 2023-10-01 | 2023-12-29 | 2023-10-11 | 2023-12-29 | 40 | 163 | 3260 |
| 2024 | oos | 2024-01-01 | 2024-12-31 | 2024-01-11 | 2024-12-31 | 208 | 991 | 19820 |

Roles reuse the saved S4 eligibility and unchanged executed Design A role-mask code/cutoffs; exact derived row indices are in role_indices.npz and all seven slot counts/maturity limits in role_counts.csv. All original OOS keys match in tensor order. First of48 completed scheduled steps is after the preceding cutoff; genuine targets span240 trading minutes, including existing crossings. October–December remains reserved and entirely excluded from O1 fitting/selection; no O1 calibration predictions or map were made.

| year | selector_epochs | selected_epoch | raw_minimum_epoch | qualified_scaled_MSE | raw_minimum_scaled_MSE | initial_scale | restricted_scale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 26 | 16 | 16 | 4.3136675 | 4.3136675 | 0.0057971177 | 0.0058487592 |
| 2022 | 23 | 13 | 13 | 1.7278699 | 1.7278699 | 0.0059351246 | 0.0059334067 |
| 2023 | 28 | 18 | 22 | 3.9810967 | 3.9796829 | 0.0060723344 | 0.0061216731 |
| 2024 | 25 | 15 | 15 | 1.6763434 | 1.6763434 | 0.0061734035 | 0.0061744472 |

| year | seconds | peak_rss | reload_error | minimum_prediction | maximum_prediction | zero_rows |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | 935.51466 | 1156300800 | 0 | 0.0028461611 | 0.03106126 | 0 |
| 2022 | 743.57986 | 1156300800 | 0 | 0.0031043477 | 0.041653596 | 0 |
| 2023 | 860.75423 | 1156300800 | 0 | 0.0027891053 | 0.039106518 | 0 |
| 2024 | 786.71223 | 1156300800 | 0 | 0.0029175456 | 0.034646895 | 0 |

All eight phase recipes were recomputed before the first neural start and every FT16 field matched the saved causal predecessor exactly (phase_parity.json). The initial whole-record checker stopped because the source F21 S4 record also has five unused target metadata keys: epsilon,t2_scale,s4_contexts,task,target_minutes. The correction recognizes only these exact source-only fields; every scaler, floor, fallback, input key and fitting quantity remains checked exactly. No canonical recipe was overwritten, and no model had started at that stop. execution.log preserves it; execution_002.log is the subsequent successful preparation/fitting log. Phase scales are recomputed on legal prefixes, not borrowed from full-December refits. Raw minimum and qualifying selected epochs are recorded separately in selection.json; raw minimum need not be selected.

## Matched annual and equal-year proper scores

Weight/unit spot-check: a one-origin day and a two-origin day, all20 stocks/origin, forecasts0.02 versus true magnitudes0.01/0.02/0.04, s=0.01, give scaled loss0.5×1+0.25×0+0.25×4=1.5 and raw MSE0.00015 squared log-return units. Naive equal-origin loss is5/3. Flipping every signed return leaves O1 loss/gradients unchanged.

| year | arm | raw_MSE | raw_MAE | observed | predicted | bias | ratio | magnitude_IC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | O1 | 8.5271069e-05 | 0.0062557455 | 0.0098002675 | 0.0091671809 | -0.00063308666 | 0.93540108 | 0.3137893 |
| 2021 | C0 | 9.0541114e-05 | 0.0061042972 | 0.0098002675 | 0.0075378642 | -0.0022624033 | 0.76914882 | 0.31785841 |
| 2021 | C1a | 8.4303166e-05 | 0.0064637727 | 0.0098002675 | 0.010290148 | 0.00048988031 | 1.0499864 | 0.31785841 |
| 2021 | M1 | 8.3790671e-05 | 0.0063963177 | 0.0098002675 | 0.010205226 | 0.00040495892 | 1.0413212 | 0.31785841 |
| 2021 | B0-RMEAN | 9.6342162e-05 | 0.0067870981 | 0.0098002675 | 0.0093076165 | -0.00049265105 | 0.94973086 | 0.289525 |
| 2021 | B0-RMED | 0.00010897265 | 0.006576386 | 0.0098002675 | 0.0062980819 | -0.0035021856 | 0.64264387 | 0.28093515 |
| 2021 | B0-CLOCK | 8.8733837e-05 | 0.0064413665 | 0.0098002675 | 0.0093055751 | -0.00049469243 | 0.94952256 | 0.29038533 |
| 2021 | B0-VOL | 8.6535921e-05 | 0.0066089924 | 0.0098002675 | 0.010256419 | 0.00045615162 | 1.0465448 | 0.31183632 |
| 2022 | O1 | 0.00014938804 | 0.0083570315 | 0.012951183 | 0.012775428 | -0.00017575533 | 0.9864294 | 0.34362343 |
| 2022 | C0 | 0.00015850978 | 0.0080691855 | 0.012951183 | 0.010049479 | -0.0029017043 | 0.77595064 | 0.35029686 |
| 2022 | C1a | 0.00014822502 | 0.008390051 | 0.012951183 | 0.013099666 | 0.00014848261 | 1.0114648 | 0.35029686 |
| 2022 | M1 | 0.00014937987 | 0.0086367779 | 0.012951183 | 0.014210493 | 0.0012593093 | 1.0972351 | 0.35029686 |
| 2022 | B0-RMEAN | 0.00017887366 | 0.0084948737 | 0.012951183 | 0.0093897435 | -0.0035614397 | 0.72501047 | 0.31318948 |
| 2022 | B0-RMED | 0.00021279945 | 0.0089435291 | 0.012951183 | 0.0063774046 | -0.0065737787 | 0.49241868 | 0.31247937 |
| 2022 | B0-CLOCK | 0.00016861834 | 0.0082521988 | 0.012951183 | 0.0093759284 | -0.0035752548 | 0.72394377 | 0.3178606 |
| 2022 | B0-VOL | 0.00015369642 | 0.0084733784 | 0.012951183 | 0.012531746 | -0.00041943677 | 0.96761402 | 0.32314717 |
| 2023 | O1 | 8.7056455e-05 | 0.0060343771 | 0.0092524379 | 0.0091027977 | -0.00014964019 | 0.98382694 | 0.30901184 |
| 2023 | C0 | 9.1161785e-05 | 0.0058106884 | 0.0092524379 | 0.0073476242 | -0.0019048138 | 0.79412845 | 0.32024473 |
| 2023 | C1a | 8.6835625e-05 | 0.0060297739 | 0.0092524379 | 0.0091368676 | -0.00011557032 | 0.9875092 | 0.32024473 |
| 2023 | M1 | 8.6602732e-05 | 0.0059913023 | 0.0092524379 | 0.0090094132 | -0.00024302474 | 0.97373398 | 0.32024473 |
| 2023 | B0-RMEAN | 9.2996729e-05 | 0.0064594275 | 0.0092524379 | 0.0096741235 | 0.00042168557 | 1.0455756 | 0.3034832 |
| 2023 | B0-RMED | 0.00010117992 | 0.0060310446 | 0.0092524379 | 0.0065814601 | -0.0026709779 | 0.71132172 | 0.29968513 |
| 2023 | B0-CLOCK | 8.6579247e-05 | 0.0061385546 | 0.0092524379 | 0.0096074191 | 0.00035498113 | 1.0383662 | 0.30364354 |
| 2023 | B0-VOL | 9.0228688e-05 | 0.0063314547 | 0.0092524379 | 0.0097563049 | 0.00050386696 | 1.0544578 | 0.2909517 |
| 2024 | O1 | 0.00011259695 | 0.006265697 | 0.0092491933 | 0.0091198538 | -0.0001293395 | 0.98601613 | 0.31181296 |
| 2024 | C0 | 0.00011892159 | 0.0060056223 | 0.0092491933 | 0.0071960535 | -0.0020531398 | 0.77801958 | 0.3102724 |
| 2024 | C1a | 0.0001135108 | 0.0063801416 | 0.0092491933 | 0.0094768388 | 0.00022764548 | 1.0246125 | 0.3102724 |
| 2024 | M1 | 0.00011329232 | 0.00651156 | 0.0092491933 | 0.0099979316 | 0.00074873831 | 1.0809517 | 0.3102724 |
| 2024 | B0-RMEAN | 0.00012124512 | 0.0067770511 | 0.0092491933 | 0.0096948401 | 0.00044564684 | 1.0481822 | 0.29475541 |
| 2024 | B0-RMED | 0.00012941663 | 0.0062474444 | 0.0092491933 | 0.0066391174 | -0.0026100759 | 0.71780502 | 0.29135808 |
| 2024 | B0-CLOCK | 0.00011474675 | 0.0065242191 | 0.0092491933 | 0.0097328363 | 0.00048364298 | 1.0522903 | 0.29931135 |
| 2024 | B0-VOL | 0.00011578065 | 0.0066372528 | 0.0092491933 | 0.0098591363 | 0.00060994296 | 1.0659455 | 0.29063745 |
| EQ | O1 | 0.00010857813 | 0.0067282128 | 0.01031327 | 0.010041315 | -0.00027195542 | 0.97363054 | 0.31955938 |
| EQ | C0 | 0.00011478357 | 0.0064974483 | 0.01031327 | 0.0080327552 | -0.0022805153 | 0.77887564 | 0.3246681 |
| EQ | C1a | 0.00010821865 | 0.0068159348 | 0.01031327 | 0.01050088 | 0.00018760952 | 1.0181911 | 0.3246681 |
| EQ | M1 | 0.0001082664 | 0.0068839895 | 0.01031327 | 0.010855766 | 0.00054249545 | 1.0526017 | 0.3246681 |
| EQ | B0-RMEAN | 0.00012236442 | 0.0071296126 | 0.01031327 | 0.0095165809 | -0.00079668959 | 0.92275102 | 0.30023827 |
| EQ | B0-RMED | 0.00013809216 | 0.006949601 | 0.01031327 | 0.006474016 | -0.0038392545 | 0.62773647 | 0.29611443 |
| EQ | B0-CLOCK | 0.00011466954 | 0.0068390848 | 0.01031327 | 0.0095054397 | -0.00080783078 | 0.92167075 | 0.3028002 |
| EQ | B0-VOL | 0.00011156042 | 0.0070127696 | 0.01031327 | 0.010600902 | 0.00028763119 | 1.0278894 | 0.30414316 |

Raw means/MAE/bias use absolute log-return units; MSE uses squared log-return units. Weights are equal stocks within origin → equal origins within session → equal sessions within year → arithmetic equal years. EQ ratio is the ratio of equal-year means. No equal-row pooling. B0-RMED targets a stock median and is primarily an MAE control, not a raw-mean model.

Frozen controls fit through September: B0-RMEAN is a stock raw mean; B0-RMED a weighted left median; B0-CLOCK a stock×slot mean shrunk by 50 origin-equivalent observations toward stock means. B0-VOL has27 columns: intercept,19 stock indicators (VZ reference),six clocks (09:30 reference),prefix-standardized log(decoded FT16 V2 RMS60). Its archived ridge penalty is0.001 in each fold. Stock/clock identities are known baseline inputs, not newly added neural channels. No reference coefficient or prediction was refitted here.

## Paired O1-minus-comparator raw MSE

| year | reference | percent_change | includes_zero | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | C0 | -5.8206102 | False | -5.2700453e-06 | -8.998686e-06 | -2.9254782e-06 | 188 | 12 |
| 2022 | C0 | -5.7546847 | False | -9.1217382e-06 | -1.2763208e-05 | -5.1208091e-06 | 210 | 12 |
| 2023 | C0 | -4.5033453 | False | -4.1053299e-06 | -6.2535467e-06 | -2.4069241e-06 | 187 | 12 |
| 2024 | C0 | -5.3183287 | False | -6.324641e-06 | -9.0105694e-06 | -3.7819191e-06 | 208 | 12 |
| EQ | C0 | -5.4062082 | False | -6.2054386e-06 | -7.7122926e-06 | -4.8575811e-06 | nan | nan |
| 2021 | C1a | 1.1481221 | True | 9.6790327e-07 | -7.1281523e-08 | 1.9175707e-06 | 188 | 12 |
| 2022 | C1a | 0.78463654 | True | 1.1630276e-06 | -3.9586177e-07 | 2.7333399e-06 | 210 | 12 |
| 2023 | C1a | 0.25430904 | True | 2.2083084e-07 | -6.0709138e-07 | 1.0765994e-06 | 187 | 12 |
| 2024 | C1a | -0.80508325 | False | -9.1385648e-07 | -1.6788263e-06 | -1.2149985e-07 | 208 | 12 |
| EQ | C1a | 0.33217593 | True | 3.5947632e-07 | -1.5879186e-07 | 9.1241585e-07 | nan | nan |
| 2021 | M1 | 1.7667819 | False | 1.4803984e-06 | 2.116428e-07 | 2.6809292e-06 | 188 | 12 |
| 2022 | M1 | 0.0054698467 | True | 8.1708501e-09 | -1.7024105e-06 | 1.7978403e-06 | 210 | 12 |
| 2023 | M1 | 0.5239141 | True | 4.5372392e-07 | -1.8126346e-07 | 1.1097977e-06 | 187 | 12 |
| 2024 | M1 | -0.61378606 | True | -6.9537247e-07 | -1.2575248e-06 | 8.5562035e-08 | 208 | 12 |
| EQ | M1 | 0.28792882 | True | 3.1173016e-07 | -2.8025147e-07 | 8.5322428e-07 | nan | nan |
| 2021 | B0-VOL | -1.4616498 | True | -1.2648521e-06 | -3.2068031e-06 | 1.2782416e-06 | 188 | 12 |
| 2022 | B0-VOL | -2.8031735 | False | -4.3083774e-06 | -6.885557e-06 | -1.3825274e-06 | 210 | 12 |
| 2023 | B0-VOL | -3.5157698 | False | -3.172233e-06 | -5.9565303e-06 | -1.0026071e-06 | 187 | 12 |
| 2024 | B0-VOL | -2.749773 | False | -3.1837052e-06 | -4.8211891e-06 | -1.4765229e-06 | 208 | 12 |
| EQ | B0-VOL | -2.6732526 | False | -2.9822919e-06 | -4.0455561e-06 | -1.770181e-06 | nan | nan |

Negative deltas favor O1. All seven reference contrasts are in paired_MSE.csv. Annual intervals reuse whole-calendar-month400-draw bootstrap seed22042. Equal-year intervals independently resample months within each year, then average four annual session means. All stocks/overlapping origins stay in their session. Intervals are descriptive95% percentile bounds conditional on fitted models, not selection/search-adjusted confirmation; four folds are not IID replications.

## Clocks, ordinary periods and large moves

Relative to calibrated C0, O1 does not remove the clock trade-off. Equal-year intraday MSE is −0.36%/−2.34% versus C1a/M1, but overnight-crossing MSE is +0.53%/+1.03%. Mean ratios are **1.093 intraday /0.917 overnight**; at15:30, ratio **0.832** and MSE **+0.40%/+1.96%** versus C1a/M1. All seven clocks and annual differences are retained below/in groups.csv; these are the original targets, not close-to-open jumps.

Prefix-95/99 event ratios remain **0.357/0.235** (C1a0.351/0.227; M10.376/0.244). O1 tail MSE improves 1.48%/1.87% over C1a, but is worse3.63%/1.78% than M1. The prefix-95 ordinary complement worsens **2.30% versus C1a** and improves **6.37% versus M1**; versus C0 it worsens **15.97%**, with deterioration in all four years. Thus lower MAE or larger forecasts is not a unanimous proper-score improvement.

Mean annual event mass is5.93% for prefix95 and0.94% for prefix99; these contribute **58.35%/32.48% of O1 raw MSE**. A small realized-event cohort still dominates loss. Outcome-conditioned event ratios below1 do not alone prove that a conditional mean is miscalibrated: even an ideal E[A|X] averages event and non-event possibilities. Forecast-score reliability and overall proper loss must be assessed separately.

The optional O1_abs_dLdz_share is a **post-fit analytic score-gradient diagnostic**: original weights times abs(2·(softplus(z)−A/s)·sigmoid(z)), normalized over the year, then equal years. It uses saved logits only, with no backward pass, fitting or extra forecasts. It is not a parameter-gradient attribution or proof of a causal training mechanism. Actual epoch-level gradient-norm/clip summaries remain in training.csv.

| year | group | rows | sessions | origins | weight_mass | false_low_rank |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | PREFIX95 | 1089 | 162 | 503 | 0.05473151 | 0.16419845 |
| 2021 | PREFIX99 | 94 | 46 | 86 | 0.0046099291 | 0.089697802 |
| 2022 | PREFIX95 | 2471 | 201 | 782 | 0.10077098 | 0.2242518 |
| 2022 | PREFIX99 | 429 | 109 | 268 | 0.017190476 | 0.11861892 |
| 2023 | PREFIX95 | 686 | 158 | 395 | 0.038100331 | 0.15741545 |
| 2023 | PREFIX99 | 131 | 49 | 106 | 0.0074306086 | 0.20150788 |
| 2024 | PREFIX95 | 930 | 171 | 471 | 0.043671589 | 0.14025661 |
| 2024 | PREFIX99 | 187 | 53 | 140 | 0.0082617903 | 0.10142016 |

| field | group | raw_MSE | raw_MAE | observed | predicted | ratio | weight_mass | raw_MSE_loss_share | O1_abs_dLdz_share | percent_MSE_vs_C0 | percent_MSE_vs_C1a | percent_MSE_vs_M1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| category | OVERNIGHT | 0.00015149878 | 0.0080030653 | 0.012430622 | 0.011403309 | 0.91735623 | 0.56501361 | 0.78844848 | 0.69576804 | -6.9598816 | 0.53363438 | 1.029392 |
| category | INTRADAY | 5.2644513e-05 | 0.0050780961 | 0.0075759099 | 0.0082789574 | 1.0928004 | 0.43498639 | 0.21155152 | 0.30423196 | 0.80924411 | -0.35964163 | -2.3380774 |
| slot | 15:30 | 0.00016889502 | 0.0082465911 | 0.013016966 | 0.010829531 | 0.83195507 | 0.14948643 | 0.23161461 | 0.18780263 | -9.3580111 | 0.39970421 | 1.9587377 |
| slot | 10:30 | 4.4338109e-05 | 0.0047419533 | 0.0072290401 | 0.0076557869 | 1.0590323 | 0.15232523 | 0.061909731 | 0.095650928 | 0.84494666 | -0.69782261 | -2.2425425 |
| slot | 11:30 | 3.7614568e-05 | 0.0043329492 | 0.0061621815 | 0.0070966325 | 1.1516429 | 0.16814413 | 0.058131917 | 0.093054725 | 5.3374132 | 0.60730505 | -1.1448901 |
| slot | 14:30 | 0.00014553961 | 0.0081277738 | 0.012666227 | 0.012183527 | 0.96189077 | 0.13023273 | 0.17487327 | 0.16661659 | -6.4213754 | 0.41977752 | 0.51002004 |
| slot | 09:30 | 8.6490989e-05 | 0.006651498 | 0.010148502 | 0.010734601 | 1.0577522 | 0.11960313 | 0.096470591 | 0.12050389 | -2.278018 | -0.31236226 | -2.5095159 |
| slot | 12:30 | 0.00013549557 | 0.0074561807 | 0.011562181 | 0.010523402 | 0.91015716 | 0.15436347 | 0.19262968 | 0.17244643 | -5.188481 | 0.98348185 | 0.86518207 |
| slot | 13:30 | 0.00015843511 | 0.0082652913 | 0.012572072 | 0.012467456 | 0.9916787 | 0.12584488 | 0.1843702 | 0.16392481 | -5.9977083 | 0.16684064 | 0.36930635 |
| tail | PREFIX95 | 0.0011442688 | 0.028615898 | 0.044512429 | 0.015904989 | 0.35731569 | 0.059318601 | 0.58348773 | 0.25884262 | -15.393751 | -1.4790333 | 3.6253223 |
| tail | LE_PREFIX95 | 4.8333703e-05 | 0.0054201636 | 0.008196338 | 0.0096704259 | 1.1798471 | 0.9406814 | 0.41651227 | 0.74115738 | 15.973831 | 2.2996156 | -6.3725344 |
| tail | PREFIX99 | 0.0039252438 | 0.058046855 | 0.075877916 | 0.017831061 | 0.23499672 | 0.009373201 | 0.32482223 | 0.085376273 | -10.882404 | -1.8732632 | 1.784556 |
| tail | LE_PREFIX99 | 7.4069807e-05 | 0.0062589018 | 0.0096994324 | 0.0099628665 | 1.0271597 | 0.9906268 | 0.67517777 | 0.91462373 | -1.9651003 | 1.6037236 | -0.79980151 |

Annual subgroup counts/sessions and paired point differences are in groups.csv. Conditional errors normalize the original weights within group, then average years; loss shares use equal-year unconditional contribution divided by total loss. Prefix95/99 strict thresholds come from the saved restricted-September fitting population, not OOS. Group differences are paired point descriptions, not independent subgroup tests or new targets. No separate overnight model was fitted.

## Magnitude and event discrimination

O1 has lower magnitude IC than C0/C1a/M1 in three years and slightly higher IC in F24. Equal-year pair concordance is0.61525 versus0.61730, top-four retrieval0.42176 versus0.42461, bottom-four0.29875 versus0.29915. No O1 negative/nonfinite/zero forecasts, constant cross-sections or score ties occurred. Scalar calibration keeps predecessor rankings unchanged; O1's learned ordering differs.

For prefix95, O1 weighted AP/AUC **0.21939/0.81972** are below C1a/M1 **0.22441/0.82327**. For prefix99, AP improves **0.06344 versus0.06037**, but AUC worsens **0.85474 versus0.85699**, false-low rate worsens **12.78% versus11.84%**, and top-four event recall is slightly lower. Prefix95 top-four recall improves slightly, while its false-low rate worsens slightly. This is mixed discrimination, not a consistent tail-information gain or evidence of complementarity with the earlier EVENT classifiers. No event-head/stacking experiment is justified automatically.

| year | arm | magnitude_IC | pair_concordance | top4 | bottom4 | tie_rate | constant_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | O1 | 0.3137893 | 0.61338175 | 0.37749493 | 0.31302242 | 0 | 0 |
| 2022 | O1 | 0.34362343 | 0.62484496 | 0.43909014 | 0.32388605 | 0 | 0 |
| 2023 | O1 | 0.30901184 | 0.61100124 | 0.41301248 | 0.29272027 | 0 | 0 |
| 2024 | O1 | 0.31181296 | 0.61175845 | 0.45745765 | 0.26537317 | 0 | 0 |
| EQ | O1 | 0.31955938 | 0.6152466 | 0.4217638 | 0.29875048 | 0 | 0 |
| EQ | C0 | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| EQ | C1a | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| EQ | M1 | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| EQ | B0-RMEAN | 0.30023827 | 0.60754095 | 0.39069215 | 0.30584502 | 0 | 0 |
| EQ | B0-RMED | 0.29611443 | 0.60612527 | 0.37416629 | 0.30584502 | 0 | 0 |
| EQ | B0-CLOCK | 0.3028002 | 0.60852865 | 0.38668138 | 0.30584502 | 0 | 0 |
| EQ | B0-VOL | 0.30414316 | 0.6094227 | 0.40988649 | 0.29618868 | 0.00026150811 | 0 |

Magnitude IC uses within-origin average ranks then origin/session/year aggregation. Undefined constant-output IC is omitted and its rate reported. Pair concordance excludes actual ties and gives half credit to predicted ties (chance.5). Top/bottom4 uses fractional boundary-tie membership (chance.2). No alphabetical tie advantage or signed-return interpretation.

| arm | group | event_prevalence | event_AP | event_AUC | false_low_rank | top4_event_recall | top4_event_precision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| O1 | PREFIX95 | 0.059318601 | 0.21939243 | 0.81971758 | 0.17153058 | 0.5524599 | 0.1569961 |
| O1 | PREFIX99 | 0.009373201 | 0.063434644 | 0.85474175 | 0.12781119 | 0.64598734 | 0.030429871 |
| C0 | PREFIX95 | 0.059318601 | 0.22440991 | 0.82327247 | 0.16997937 | 0.54589131 | 0.15486425 |
| C0 | PREFIX99 | 0.009373201 | 0.060366889 | 0.85698894 | 0.11835925 | 0.64821943 | 0.030488859 |
| C1a | PREFIX95 | 0.059318601 | 0.22440991 | 0.82327247 | 0.16997937 | 0.54589131 | 0.15486425 |
| C1a | PREFIX99 | 0.009373201 | 0.060366889 | 0.85698894 | 0.11835925 | 0.64821943 | 0.030488859 |
| M1 | PREFIX95 | 0.059318601 | 0.22440991 | 0.82327247 | 0.16997937 | 0.54589131 | 0.15486425 |
| M1 | PREFIX99 | 0.009373201 | 0.060366889 | 0.85698894 | 0.11835925 | 0.64821943 | 0.030488859 |
| B0-RMEAN | PREFIX95 | 0.059318601 | 0.14144104 | 0.73699351 | 0.19114747 | 0.49965433 | 0.13969838 |
| B0-RMEAN | PREFIX99 | 0.009373201 | 0.030398272 | 0.76643436 | 0.14267008 | 0.58304197 | 0.026774371 |
| B0-RMED | PREFIX95 | 0.059318601 | 0.14255813 | 0.73699335 | 0.1906008 | 0.48981698 | 0.13624577 |
| B0-RMED | PREFIX99 | 0.009373201 | 0.03078586 | 0.77020425 | 0.15338437 | 0.58989781 | 0.026514927 |
| B0-CLOCK | PREFIX95 | 0.059318601 | 0.19294421 | 0.8012234 | 0.19550888 | 0.49902849 | 0.13938304 |
| B0-CLOCK | PREFIX99 | 0.009373201 | 0.048691587 | 0.83616765 | 0.14231029 | 0.5776502 | 0.026310936 |
| B0-VOL | PREFIX95 | 0.059318601 | 0.21124497 | 0.80525551 | 0.19221866 | 0.52736259 | 0.15116679 |
| B0-VOL | PREFIX99 | 0.009373201 | 0.059754742 | 0.83695487 | 0.16638324 | 0.6231073 | 0.029617205 |

Event AP/AUC reuse the executed threshold-grouped weighted routines on continuous scores and prefix-defined raw-A events. These annual pooled scores can reflect stock/calendar risk levels; EQ averages annual AP/AUC, not pooled rows. Constant-score AP equals event prevalence; AUC chance.5. False-low rate is event mass at within-origin midrank≤10.5 divided by event mass, then mean years; top4 recall is event mass captured by fractional top4. Magnitudes are not event probabilities. Stock-prior comparator unavailable: archived EVENT labels use |TG20|, not the same raw-A prefix95/99 labels. Earlier E1/S9-EVENT results therefore establish no complementary event benefit here.

## Descriptive reliability

| group | observed | predicted | ratio | raw_MSE | raw_MAE |
| --- | --- | --- | --- | --- | --- |
| 1 | 0.00442062 | 0.0044548973 | 1.007754 | 1.6079667e-05 | 0.0028758697 |
| 2 | 0.0057755681 | 0.0056508071 | 0.97839849 | 2.8691925e-05 | 0.0037830342 |
| 3 | 0.0067470842 | 0.0065892968 | 0.97661398 | 4.0095506e-05 | 0.0044312329 |
| 4 | 0.0077264166 | 0.007518705 | 0.9731167 | 5.5205262e-05 | 0.0050806336 |
| 5 | 0.0088399148 | 0.0085055314 | 0.96217346 | 7.2558058e-05 | 0.0057607329 |
| 6 | 0.0097324176 | 0.0095697836 | 0.98328946 | 7.8920428e-05 | 0.006351675 |
| 7 | 0.011112675 | 0.010784937 | 0.97050774 | 0.00011621615 | 0.007403592 |
| 8 | 0.012798115 | 0.012241045 | 0.95647254 | 0.0001402924 | 0.0082639515 |
| 9 | 0.014953233 | 0.014496785 | 0.96947498 | 0.00019455498 | 0.0097200615 |
| 10 | 0.021032911 | 0.020607351 | 0.97976694 | 0.00034329734 | 0.013615543 |

Ten weighted empirical O1 score deciles per annual OOS population; same bins for every comparator. Numeric ranges, counts and sessions are in groups.csv. These are descriptive percentile bins, not future calibration boundaries. Equal-year deciles average corresponding annual percentile bins without claiming common numerical cutpoints. No correction is fitted on these diagnostics.

## Historical context and interpretation

**Favor C1a/M1 for the current raw-mean benchmark; do not promote O1.** O1 is technically valid and reduces raw-MSE relative to C0 and strong non-neural references, but it does not beat either principal calibrated baseline in equal-year MSE and loses three of four annual point comparisons. The intervals include zero, so the conclusion is absence of demonstrated incremental advantage rather than a claim that O1 must always be worse. Lower MAE versus calibrated arms and near-level reliability are legitimate trade-offs.

| Finding | Scientific decision |
| --- | --- |
| Primary O1−C1a/M1 equal-year differences are positive, intervals include zero | Retain the calibrated predecessor; no direct-raw objective breakthrough established |
| O1 improves on C0 and B0-VOL | Preserve the completed O1 evidence; do not erase a valid nonwinning model |
| Ordinary/overnight/tail trade-offs remain and differ by comparator | Decide which functional/conditional risk matters before another fit; no outcome-weighting rescue |
| O1 IC is lower; event AP/AUC/false-low checks disagree | No claim of new jump information, event complementarity, signed alpha or trading value |
| Stable opposite intraday/overnight level errors remain | If a follow-up is desired, a separately predeclared, pooled clock-calibration question is more directly motivated than another objective/architecture sweep; calibration-tail adequacy must be reviewed, especially F24 |

One seed and repeatedly inspected annual folds do not identify whether remaining error comes from functional mismatch, optimization/regularization/link choices, finite capacity, noise, nonstationarity or unavailable shock information. The objective/link/checkpoint-monitor package was tested jointly. Forecasting raw mean movement is distinct from forecasting an upper quantile or event probability; a future O4 question requires its own same-task priors/proper scores and explicit authorization. No O1 calibration, C3, O2–O7, second seed, Stage2 overnight target, strategy or protected confirmation starts here.

| year | arm | rows | sessions | origins | observed | predicted | bias | ratio | raw_MAE | raw_MSE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | HIST_MAG_DIFFERENT_HISTORY | 19100 | 188 | 955 | 0.0098002675 | 0.0076260872 | -0.0021741803 | 0.77815092 | 0.0060936559 | 8.9308779e-05 |
| 2022 | HIST_MAG_DIFFERENT_HISTORY | 23600 | 210 | 1180 | 0.012951183 | 0.010627653 | -0.0023235298 | 0.82059324 | 0.0080708064 | 0.00015442406 |
| 2023 | HIST_MAG_DIFFERENT_HISTORY | 17740 | 187 | 887 | 0.0092524379 | 0.0074599629 | -0.0017924751 | 0.80626997 | 0.0058250789 | 9.0812482e-05 |
| 2024 | HIST_MAG_DIFFERENT_HISTORY | 19820 | 208 | 991 | 0.0092491933 | 0.0077311926 | -0.0015180007 | 0.83587751 | 0.0060294375 | 0.00011557095 |
| EQ | HIST_MAG_DIFFERENT_HISTORY | 80260 | 793 | 4013 | 0.01031327 | 0.008361224 | -0.0019520464 | 0.81072479 | 0.0065047447 | 0.00011252907 |

HIST_MAG refit through December and is contextual only: no primary paired causal comparison or model selection uses it. Its archived transformed MSE0.232454 is a different objective/scale and cannot be the raw-mean O1 promotion score. The original price-only label begins before approximate origin+2min issuance. Endpoint magnitude is not integrated variance, option-IV mispricing, execution P&L or a tradability result.

## Reproduction, preservation and stop

Run IDs: HF20-O1-F{21,22,23,24}-DESIGNA-S42. Under this report root, F21/F22/F23/F24 each contain restricted_final.pt, selected_initial.pt, oos_scores.parquet, initial_recipe.json, restricted_recipe.json, phases.json, selection.json, training.csv and result.json. Source entry point: src/lstm_data/hf20_mag_o1.py; focused fixtures: tests/test_hf20_mag_o1.py. Aggregate outputs are metrics.csv, paired_MSE.csv and groups.csv. interpretation.json stores the reviewed post-fit narrative, not fitting choices. No predecessor predictions or bulk feature store were copied.

`.venv/bin/python -m lstm_data.hf20_mag_o1 --out reports/experiments/hf20_s9_mag_stage1_session3_o1_2026-10-28 --report` replays saved scores only; --run is single-use. protocol.json fixes all choices before fitting. phases.json, selection.json and result.json bind each new run to recipes/scales, fresh initialization, selected epoch and final checkpoint. Comparator scores remain referenced from Session2/2B and are never copied or refitted. New O1 stores contain only its keys/labels/weights/z/O1 forecasts.

Source allowlist: reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation/opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv; 174 existing adjusted-hourly partitions2010-07 through2024-12; same S4 target/eligibility and original S9 OOS keys. No minute reconstruction, download, protected2026 numerical read/hash or opportunistic2025 exploration. No prior artifact/dashboard/ledger history was overwritten; only the current append-only successor pointer changes.

Final verification is in verification.json and the mandatory session report reports/codex_sessions/2026-10-28_004000_hf20_s9_mag_session3_o1.md. No automatic O2–O7, C3, new architecture/seed, overnight target, options/backtest or protected confirmation. STOP for researcher review.

Final verification PASS: all four canonical-role/key/label/weight/axis/prefix-recipe/softplus/checkpoint/selector checks pass; all eight pre-fit numerical kernels and bound predecessor assets remain unchanged. Thirteen focused tests, Ruff, and full basic Pylance-stub parity504 files/zero errors and warnings pass. Four new pairs/eight phase fits,164 epochs/25,059 optimizer updates; ledger134→138/200; no neural failure/retry; empty continuation queue. One preparation-only metadata-checker correction before any start is retained in execution.log. Actual fit lifecycle sum3,326.56s; peak RSS1,156,300,800 bytes, under2GB. New namespace approximately4.08MB, under2.5GB; whole project remains under15GB. PyArrow cache-query warnings are environmental. PyTorch warns on the read-only Parquet NumPy view used for decoder replay; softplus/multiplication are out-of-place and no input is mutated; exact decoder/reload checks pass. The current registry pointer is the only existing file changed. No commit/push. Editor: select .venv/bin/python, Pylance basic, refresh Problems; actual editor refresh remains human-confirmed. STOP; no further experiment or protected release.
