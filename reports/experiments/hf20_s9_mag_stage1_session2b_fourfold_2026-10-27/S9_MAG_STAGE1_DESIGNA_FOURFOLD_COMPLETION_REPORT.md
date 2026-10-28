# S9 MAG Stage1 / Session2B — Design A four-fold completion

**Status: COMPLETE.** F21 reused by reference; only F22–F24 are new fits. All results exploratory/post-search.

## Executive result

**COMPLETE execution; MIXED scientific outcome.** All four folds are valid on the original **80,260 stock-origin rows / 4,013 origins / 793 sessions**, with F21 reused unchanged. Three new selector/refit pairs (six neural phases) completed once; no retries. These are past-only fits on repeatedly studied, exploratory/post-search evaluation years.

- C1a reduces equal-year raw MSE from **0.000114783568 to 0.000108218653 (-5.72%)**. Annual changes are −6.89%, −6.49%, −4.75%, −4.55%. Its equal-year paired difference is −6.565e−6, descriptive 95% month-block interval [−7.789e−6, −5.278e−6].
- M1 achieves **0.0001082663992 (-5.68%)**. C1a−M1 is −4.775e−8 [−4.121e−7, +3.217e−7], including zero. M1 wins three annual point comparisons, but C1a wins F22. There is no consistent M1 dominance or demonstrated special smearing advantage.
- Mean forecast/realized ratio improves **0.779 → 1.018 / 1.053**. However, raw MAE worsens **4.90% / 5.95%**, and prefix-95 ordinary-complement MSE worsens in every year.
- Both calibrated arms beat B0-VOL equal-year raw MSE by **3.00% / 2.95%**. B0-CLOCK and raw-mean/median controls remain in the same-key comparison. C0 has the lowest overall MAE; the per-stock median is judged as an MAE comparator, not disqualified for its larger MSE.
- Gains concentrate in existing overnight-crossing and large-move targets. Intraday errors generally worsen. Tail amplitudes remain much too low, while within-origin IC is unchanged at **0.324668**.

**Next researcher question:** is a separately authorized direct raw-mean objective (O1), with the same strong B0 and simple M1 comparators, a better next controlled intervention than adding contextual calibration? This report does not approve or start either.

## Amendment and preflight

F21 reuse: PASS for exact chronology, keys, parameter identity, formulas and bound artifacts. It was not retrained or retrospectively corrected.

Uniform rule: test July1, June1, May1 in order; choose first meeting>=50 sessions and>=25 origins in every slot, after exact48-step embargo and label maturity. Initial training/scaling ends before that nominal start. No loss, IC, forecast or OOS performance enters this choice.

| year | preflight_status | selector_start | initial_stop | selector_sessions | slot_min |
| --- | --- | --- | --- | --- | --- |
| 2021 | REUSE | 2020-07-01 | 2020-06-30 | 57 | 46 |
| 2022 | READY | 2021-05-01 | 2021-04-30 | 58 | 36 |
| 2023 | READY | 2022-06-01 | 2022-05-31 | 59 | 38 |
| 2024 | READY | 2023-06-01 | 2023-05-31 | 69 | 31 |

| year | role | cutoff | first_date | last_date | sessions | origins | stock_rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | inner_train | 2020-06-30 | 2011-04-01 | 2020-06-30 | 2100 | 11449 | 228980 |
| 2021 | selector | 2020-09-30 | 2020-07-13 | 2020-09-30 | 57 | 349 | 6980 |
| 2021 | restricted_refit | 2020-09-30 | 2011-04-01 | 2020-09-30 | 2164 | 11846 | 236920 |
| 2021 | calibration | 2020-12-31 | 2020-10-12 | 2020-12-30 | 56 | 283 | 5660 |
| 2021 | oos | 2021-12-31 | 2021-01-13 | 2021-12-31 | 188 | 955 | 19100 |
| 2022 | inner_train | 2021-04-30 | 2011-04-01 | 2021-04-30 | 2301 | 12560 | 251200 |
| 2022 | selector | 2021-09-30 | 2021-05-12 | 2021-09-30 | 58 | 278 | 5560 |
| 2022 | restricted_refit | 2021-09-30 | 2011-04-01 | 2021-09-30 | 2366 | 12888 | 257760 |
| 2022 | calibration | 2021-12-31 | 2021-10-12 | 2021-12-31 | 50 | 245 | 4900 |
| 2022 | oos | 2022-12-31 | 2022-01-12 | 2022-12-30 | 210 | 1180 | 23600 |
| 2023 | inner_train | 2022-05-31 | 2011-04-01 | 2022-05-31 | 2526 | 13776 | 275520 |
| 2023 | selector | 2022-09-30 | 2022-06-10 | 2022-09-27 | 59 | 313 | 6260 |
| 2023 | restricted_refit | 2022-09-30 | 2011-04-01 | 2022-09-27 | 2592 | 14137 | 282740 |
| 2023 | calibration | 2022-12-30 | 2022-10-13 | 2022-12-30 | 48 | 258 | 5160 |
| 2023 | oos | 2023-12-31 | 2023-01-13 | 2023-12-29 | 187 | 887 | 17740 |
| 2024 | inner_train | 2023-05-31 | 2011-04-01 | 2023-05-31 | 2719 | 14824 | 296480 |
| 2024 | selector | 2023-09-29 | 2023-06-12 | 2023-09-29 | 69 | 291 | 5820 |
| 2024 | restricted_refit | 2023-09-29 | 2011-04-01 | 2023-09-29 | 2795 | 15167 | 303340 |
| 2024 | calibration | 2023-12-29 | 2023-10-11 | 2023-12-29 | 40 | 163 | 3260 |
| 2024 | oos | 2024-12-31 | 2024-01-11 | 2024-12-31 | 208 | 991 | 19820 |

Full per-role seven-slot counts, maturity timestamps and embargo cutoffs: role_counts.csv. All original S4/S9 OOS keys and stock order match; no dropped rows.

Selector and independent-tail seven-slot coverage:

| year | role | sessions | 09:30 | 10:30 | 11:30 | 12:30 | 13:30 | 14:30 | 15:30 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | selector | 57 | 52 | 51 | 51 | 49 | 53 | 46 | 47 |
| 2021 | calibration | 56 | 36 | 38 | 48 | 43 | 37 | 40 | 41 |
| 2022 | selector | 58 | 38 | 44 | 44 | 36 | 38 | 38 | 40 |
| 2022 | calibration | 50 | 36 | 37 | 38 | 35 | 33 | 31 | 35 |
| 2023 | selector | 59 | 38 | 48 | 50 | 47 | 40 | 46 | 44 |
| 2023 | calibration | 48 | 38 | 39 | 44 | 38 | 36 | 29 | 34 |
| 2024 | selector | 69 | 33 | 40 | 53 | 47 | 31 | 40 | 47 |
| 2024 | calibration | 40 | 19 | 26 | 28 | 25 | 23 | 21 | 21 |

Calibration adequacy:56/50/48/40 sessions. These are global scalar fits; no invented selector50/25 minimum is applied to the calibration tail. F24's smaller/sparser tail warrants limited-precision caution, not independent certification. Event/month coverage below uses archived June-prefix95/99 thresholds only as preflight descriptors; evaluation tails use each restricted September prefix.

| year | sessions | origins | rows | max_A | June_prefix95 | June_prefix99 | exceed95_rows | exceed99_rows | Oct/Nov/Dec_origins |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 56 | 283 | 5660 | 0.15022641 | 0.028876179 | 0.055052003 | 499 | 110 | 76/102/105 |
| 2022 | 50 | 245 | 4900 | 0.13989949 | 0.029438986 | 0.055218675 | 387 | 52 | 30/95/120 |
| 2023 | 48 | 258 | 5160 | 0.11896382 | 0.030356344 | 0.056174263 | 336 | 44 | 65/74/119 |
| 2024 | 40 | 163 | 3260 | 0.12418185 | 0.030526468 | 0.056080802 | 131 | 30 | 63/64/36 |

Strict label maturity is before local cutoff midnight +1 day -4 hours. For selector, calibration and OOS, the first of 48 scheduled completed input hours must be strictly after the preceding cutoff. Genuine targets span 240 trading minutes; later clocks cross sessions. All-four admissibility was saved before the first new neural start.

## Annual and equal-year proper scores

| year | arm | raw_MSE | raw_MAE | observed | predicted | bias | ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | C0 | 9.0541114e-05 | 0.0061042972 | 0.0098002675 | 0.0075378642 | -0.0022624033 | 0.76914882 |
| 2021 | C1a | 8.4303166e-05 | 0.0064637727 | 0.0098002675 | 0.010290148 | 0.00048988031 | 1.0499864 |
| 2021 | M1 | 8.3790671e-05 | 0.0063963177 | 0.0098002675 | 0.010205226 | 0.00040495892 | 1.0413212 |
| 2021 | B0-RMEAN | 9.6342162e-05 | 0.0067870981 | 0.0098002675 | 0.0093076165 | -0.00049265105 | 0.94973086 |
| 2021 | B0-RMED | 0.00010897265 | 0.006576386 | 0.0098002675 | 0.0062980819 | -0.0035021856 | 0.64264387 |
| 2021 | B0-CLOCK | 8.8733837e-05 | 0.0064413665 | 0.0098002675 | 0.0093055751 | -0.00049469243 | 0.94952256 |
| 2021 | B0-VOL | 8.6535921e-05 | 0.0066089924 | 0.0098002675 | 0.010256419 | 0.00045615162 | 1.0465448 |
| 2022 | C0 | 0.00015850978 | 0.0080691855 | 0.012951183 | 0.010049479 | -0.0029017043 | 0.77595064 |
| 2022 | C1a | 0.00014822502 | 0.008390051 | 0.012951183 | 0.013099666 | 0.00014848261 | 1.0114648 |
| 2022 | M1 | 0.00014937987 | 0.0086367779 | 0.012951183 | 0.014210493 | 0.0012593093 | 1.0972351 |
| 2022 | B0-RMEAN | 0.00017887366 | 0.0084948737 | 0.012951183 | 0.0093897435 | -0.0035614397 | 0.72501047 |
| 2022 | B0-RMED | 0.00021279945 | 0.0089435291 | 0.012951183 | 0.0063774046 | -0.0065737787 | 0.49241868 |
| 2022 | B0-CLOCK | 0.00016861834 | 0.0082521988 | 0.012951183 | 0.0093759284 | -0.0035752548 | 0.72394377 |
| 2022 | B0-VOL | 0.00015369642 | 0.0084733784 | 0.012951183 | 0.012531746 | -0.00041943677 | 0.96761402 |
| 2023 | C0 | 9.1161785e-05 | 0.0058106884 | 0.0092524379 | 0.0073476242 | -0.0019048138 | 0.79412845 |
| 2023 | C1a | 8.6835625e-05 | 0.0060297739 | 0.0092524379 | 0.0091368676 | -0.00011557032 | 0.9875092 |
| 2023 | M1 | 8.6602732e-05 | 0.0059913023 | 0.0092524379 | 0.0090094132 | -0.00024302474 | 0.97373398 |
| 2023 | B0-RMEAN | 9.2996729e-05 | 0.0064594275 | 0.0092524379 | 0.0096741235 | 0.00042168557 | 1.0455756 |
| 2023 | B0-RMED | 0.00010117992 | 0.0060310446 | 0.0092524379 | 0.0065814601 | -0.0026709779 | 0.71132172 |
| 2023 | B0-CLOCK | 8.6579247e-05 | 0.0061385546 | 0.0092524379 | 0.0096074191 | 0.00035498113 | 1.0383662 |
| 2023 | B0-VOL | 9.0228688e-05 | 0.0063314547 | 0.0092524379 | 0.0097563049 | 0.00050386696 | 1.0544578 |
| 2024 | C0 | 0.00011892159 | 0.0060056223 | 0.0092491933 | 0.0071960535 | -0.0020531398 | 0.77801958 |
| 2024 | C1a | 0.0001135108 | 0.0063801416 | 0.0092491933 | 0.0094768388 | 0.00022764548 | 1.0246125 |
| 2024 | M1 | 0.00011329232 | 0.00651156 | 0.0092491933 | 0.0099979316 | 0.00074873831 | 1.0809517 |
| 2024 | B0-RMEAN | 0.00012124512 | 0.0067770511 | 0.0092491933 | 0.0096948401 | 0.00044564684 | 1.0481822 |
| 2024 | B0-RMED | 0.00012941663 | 0.0062474444 | 0.0092491933 | 0.0066391174 | -0.0026100759 | 0.71780502 |
| 2024 | B0-CLOCK | 0.00011474675 | 0.0065242191 | 0.0092491933 | 0.0097328363 | 0.00048364298 | 1.0522903 |
| 2024 | B0-VOL | 0.00011578065 | 0.0066372528 | 0.0092491933 | 0.0098591363 | 0.00060994296 | 1.0659455 |
| EQ | C0 | 0.00011478357 | 0.0064974483 | 0.01031327 | 0.0080327552 | -0.0022805153 | 0.77887564 |
| EQ | C1a | 0.00010821865 | 0.0068159348 | 0.01031327 | 0.01050088 | 0.00018760952 | 1.0181911 |
| EQ | M1 | 0.0001082664 | 0.0068839895 | 0.01031327 | 0.010855766 | 0.00054249545 | 1.0526017 |
| EQ | B0-RMEAN | 0.00012236442 | 0.0071296126 | 0.01031327 | 0.0095165809 | -0.00079668959 | 0.92275102 |
| EQ | B0-RMED | 0.00013809216 | 0.006949601 | 0.01031327 | 0.006474016 | -0.0038392545 | 0.62773647 |
| EQ | B0-CLOCK | 0.00011466954 | 0.0068390848 | 0.01031327 | 0.0095054397 | -0.00080783078 | 0.92167075 |
| EQ | B0-VOL | 0.00011156042 | 0.0070127696 | 0.01031327 | 0.010600902 | 0.00028763119 | 1.0278894 |

A=abs(log(P_endpoint/P_origin)). MAE/bias/means are log-return units; MSE is squared log-return units. Annual weights equal stocks/origin, origins/session, sessions/year. EQ losses/means/IC average four annual values; EQ ratio is the ratio of EQ predicted/observed means, not a pooled-row ratio or mean annual ratio. EQ is unavailable if any fold fails.

## Paired raw-MSE uncertainty

| year | model | reference | percent_change | includes_zero | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | C1a | C0 | -6.8896309 | False | -6.2379486e-06 | -1.0569915e-05 | -3.1775387e-06 | 188 | 12 |
| 2022 | C1a | C0 | -6.4884108 | False | -1.0284766e-05 | -1.279881e-05 | -7.1692407e-06 | 210 | 12 |
| 2023 | C1a | C0 | -4.7455858 | False | -4.3261608e-06 | -5.686506e-06 | -3.2231452e-06 | 187 | 12 |
| 2024 | C1a | C0 | -4.5498757 | False | -5.4107845e-06 | -7.568223e-06 | -3.6150379e-06 | 208 | 12 |
| EQ | C1a | C0 | -5.7193857 | False | -6.5649149e-06 | -7.7891515e-06 | -5.2779619e-06 | nan | nan |
| 2021 | M1 | C0 | -7.4556666 | False | -6.7504437e-06 | -1.1211251e-05 | -3.5389704e-06 | 188 | 12 |
| 2022 | M1 | C0 | -5.7598395 | False | -9.1299091e-06 | -1.2341515e-05 | -4.8689453e-06 | 210 | 12 |
| 2023 | M1 | C0 | -5.0010581 | False | -4.5590539e-06 | -6.0711824e-06 | -3.3410504e-06 | 187 | 12 |
| 2024 | M1 | C0 | -4.7335968 | False | -5.6292685e-06 | -8.5408463e-06 | -3.109032e-06 | 208 | 12 |
| EQ | M1 | C0 | -5.677789 | False | -6.5171688e-06 | -7.9032866e-06 | -5.1431839e-06 | nan | nan |
| 2021 | C1a | M1 | 0.61163741 | False | 5.1249509e-07 | 5.3419676e-08 | 8.7838998e-07 | 188 | 12 |
| 2022 | C1a | M1 | -0.77310066 | False | -1.1548568e-06 | -2.4716234e-06 | -5.0894742e-08 | 210 | 12 |
| 2023 | C1a | M1 | 0.26892117 | False | 2.3289308e-07 | 2.9408097e-08 | 4.1918496e-07 | 187 | 12 |
| 2024 | C1a | M1 | 0.19284979 | True | 2.18484e-07 | -4.7950472e-07 | 9.4092166e-07 | 208 | 12 |
| EQ | C1a | M1 | -0.044100623 | True | -4.7746156e-08 | -4.1214547e-07 | 3.217233e-07 | nan | nan |
| 2021 | C1a | B0-VOL | -2.5801486 | True | -2.2327554e-06 | -4.4699127e-06 | 3.2677938e-08 | 188 | 12 |
| 2022 | C1a | B0-VOL | -3.5598779 | False | -5.471405e-06 | -7.2833544e-06 | -3.2864593e-06 | 210 | 12 |
| 2023 | C1a | B0-VOL | -3.7605155 | False | -3.3930639e-06 | -5.664252e-06 | -1.7133199e-06 | 187 | 12 |
| 2024 | C1a | B0-VOL | -1.9604732 | False | -2.2698487e-06 | -3.8577655e-06 | -6.018199e-07 | 208 | 12 |
| EQ | C1a | B0-VOL | -2.9954783 | False | -3.3417682e-06 | -4.3833389e-06 | -2.3040199e-06 | nan | nan |
| 2021 | M1 | B0-VOL | -3.1723826 | False | -2.7452505e-06 | -5.0613876e-06 | -1.9675275e-07 | 188 | 12 |
| 2022 | M1 | B0-VOL | -2.8084897 | False | -4.3165482e-06 | -6.4718738e-06 | -1.6405011e-06 | 210 | 12 |
| 2023 | M1 | B0-VOL | -4.0186298 | False | -3.6259569e-06 | -5.9942648e-06 | -1.9369718e-06 | 187 | 12 |
| 2024 | M1 | B0-VOL | -2.1491783 | False | -2.4883327e-06 | -3.8036307e-06 | -1.2004782e-06 | 208 | 12 |
| EQ | M1 | B0-VOL | -2.9526798 | False | -3.2940221e-06 | -4.3637054e-06 | -2.2749054e-06 | nan | nan |

Annual bounds use the unchanged Session2 whole-month400-draw routine,seed22042. EQ uses the executed S5/S9 year-stratified month bootstrap: independent whole-month draws within each year, then mean four annual resampled means. No IID stock/overlapping-origin/year resampling or selection-adjusted significance claim.

Bounds are descriptive 95% percentile intervals conditional on these already fitted encoders/scalars and chosen protocol. They do not refit calibration tails or account for model-selection/search uncertainty. Stocks, overlapping origins and four annual folds are not IID replicates.

## Fits and calibration precision

| year | disposition | selector_start | selector_epochs | selected_epoch | initial_scale | scale | c | k | ridge_penalty | cal_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | REUSED | 2020-07-01 | 39 | 29 | 0.0057971177 | 0.0058487592 | 1.2055995 | 1.3538618 | 0.001 | 5660 |
| 2022 | NEW | 2021-05-01 | 37 | 27 | 0.0059351246 | 0.0059334067 | 1.1908408 | 1.4140527 | 0.001 | 4900 |
| 2023 | NEW | 2022-06-01 | 32 | 22 | 0.0060723344 | 0.0061216731 | 1.1328387 | 1.2261669 | 0.001 | 5160 |
| 2024 | NEW | 2023-06-01 | 25 | 15 | 0.0061734035 | 0.0061744472 | 1.1705834 | 1.3893632 | 0.001 | 3260 |

| year | exp_top10_share | exp_top1pct_share | exp_max | negative_Mhat_oos | C1a_zero_oos | M1_zero_oos | seconds | peak_rss | reload_max_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 0.015028698 | 0.056525852 | 9.1530765 | 0 | 0 | 0 | 1072.4257 | 1244594176 | 0 |
| 2022 | 0.015570929 | 0.055273496 | 8.2372115 | 0 | 0 | 0 | 1029.2108 | 1140572160 | 0 |
| 2023 | 0.017732427 | 0.058433541 | 6.9630566 | 0 | 0 | 0 | 824.3723 | 1165688832 | 0 |
| 2024 | 0.032815579 | 0.072587355 | 10.898311 | 0 | 0 | 0 | 684.76951 | 1165688832 | 0 |

New initial FT16 floors/scalers and target scales were fitted only before the chosen selector start; restricted recipes/scales only through September. The exact September encoder supplies both independent October–December and next-year OOS forecasts. Original MAG initialization, optimizer, dropout, loss, selector, seed42, fresh-refit logic and B0 formulas/penalties are unchanged. No c/k clipping, trimming or contextual fitting.

Model: shared own-stock 48×16 FT16 input, one H32 LSTM layer, 6,433 parameters, final-hidden dropout 0.10, seed 42. AdamW LR 0.001, matrix decay 0.01/bias decay 0, gradient cap 1, 16 complete sessions per batch. First finite nonnegative selector loss qualifies; later loss must be ≤0.999×best qualified loss; stop at ≥12 epochs and ten nonqualifying epochs, or 60 maximum. Fresh September initialization/optimizer uses the selected count. Scale s is the phase-prefix session/origin/stock-weighted left median of A, floored at 1e−8.

C0=s·expm1(max(Mhat,0)); c=weighted mean_cal exp(log1p(A/s)−Mhat); C1a=s·max(0,exp(Mhat)c−1). k=max(0,weighted mean_cal(A0·A)/weighted mean_cal(A0²)); M1=k·A0. Smearing uses unconstrained Mhat; only original decoding clamps Mhat. Every coefficient was frozen before outer prediction. All factor statuses are FINITE; top-10 and top-1% shares describe weighted contributions to c, not independent observations or winsorization. F24's top 10 rows supply 3.28% of c, versus 1.50–1.77% in earlier folds, and its 40 sessions warrant greater precision caution.

B0-RMEAN targets a stock raw mean; B0-RMED a stock weighted left median. B0-CLOCK uses exactly 50 origin-equivalent pseudo-observations toward each stock mean. B0-VOL has 27 columns: unpenalized intercept, 19 stock indicators (VZ reference), six clock indicators (09:30 reference), and initial/refit-prefix standardized log(decoded FT16 V2 hourly RMS60). Penalties 0.001/0.1/10 are evaluated only on each actual amended selector, then the chosen model refits through September, with max(0,prediction). All four chose 0.001. No reserved-tail labels fit B0 or its standardization. The inherited baseline helper's historical July–September docstring describes its original caller; its executed code consumes the supplied selector indices, including the approved May/June extensions.

## Magnitude ordering

Annual C0 and equal-year all-arm ranking; every annual arm is in fourfold_metrics.csv.

| year | arm | magnitude_IC | top4 | bottom4 | pair_concordance | tie_rate | constant_rate | original_Mhat_transformed_MSE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | C0 | 0.31785841 | 0.3866483 | 0.31024569 | 0.61520032 | 0 | 0 | 0.22555554 |
| 2022 | C0 | 0.35029686 | 0.43397959 | 0.32302721 | 0.62723692 | 0 | 0 | 0.27969024 |
| 2023 | C0 | 0.32024473 | 0.41768844 | 0.29774001 | 0.61514505 | 0 | 0 | 0.20948538 |
| 2024 | C0 | 0.3102724 | 0.46012191 | 0.26560783 | 0.61162619 | 0 | 0 | 0.21873201 |
| EQ | C0 | 0.3246681 | 0.42460956 | 0.29915518 | 0.61730212 | 0 | 0 | 0.23336579 |
| EQ | C1a | 0.3246681 | 0.42460956 | 0.29915518 | 0.61730212 | 0 | 0 | 0.23336579 |
| EQ | M1 | 0.3246681 | 0.42460956 | 0.29915518 | 0.61730212 | 0 | 0 | 0.23336579 |
| EQ | B0-RMEAN | 0.30023827 | 0.39069215 | 0.30584502 | 0.60754095 | 0 | 0 | nan |
| EQ | B0-RMED | 0.29611443 | 0.37416629 | 0.30584502 | 0.60612527 | 0 | 0 | nan |
| EQ | B0-CLOCK | 0.3028002 | 0.38668138 | 0.30584502 | 0.60852865 | 0 | 0 | nan |
| EQ | B0-VOL | 0.30414316 | 0.40988649 | 0.29618868 | 0.6094227 | 0.00026150811 | 0 | nan |

Magnitude IC is within-origin tie-aware Spearman, then origins/sessions/years; not archived all-row0.408 or signed-return IC. Strictly monotone positive maps are asserted to preserve C0 rankings; clamping/tie exceptions are disclosed. Original Mhat loss is unchanged across network decoders, not a loss of inverse-corrected outputs.

Spearman uses average ranks; constant-score origins yield undefined IC and would be omitted, with their rate disclosed (none here). Pair concordance excludes true-outcome ties and gives half credit to score ties; chance is 0.5. Top/bottom-four retrieval uses fractional membership at tied boundaries; chance is 0.2. No jitter or alphabetical tie breaking.

## Clock and tail diagnostics

**Systematic trade-off, not an unqualified calibration success.** Equal-year overnight-crossing MSE improves 7.45% / 7.91% (C1a/M1); intraday MSE worsens 1.17% / 3.22%. Overnight improvement occurs in all four years; intraday deterioration occurs in three of four (F23 improves slightly). At 15:30, MSE improves 9.72% / 11.10%, but mean ratios remain only 0.863 / 0.898. These are the original four-trading-hour labels, including next-session crossings; no separate overnight target was created.

For prefix-95 events, equal-year mean predicted/realized ratios rise from 0.279 to **0.351 / 0.376**; prefix-99 ratios from 0.181 to **0.227 / 0.244**. Thus severe event amplitudes remain missed. The prefix-95 ordinary complement has MSE **+13.37% / +23.87%**, worsening in every year (annual ranges +4.10–24.52% / +5.11–48.89%). Prefix-95 events occupy mean annual weight 5.93% but contribute 65.96% of C0 loss and 59.15% / 55.47% of calibrated loss; prefix-99 weight is 0.94%, with loss shares 34.85% → 33.33% / 31.75%.

False-low rate is the original-weight mass of event rows whose within-origin average forecast rank is ≤10.5, divided by event mass; average the four annual conditional rates. It is **17.00% / 11.84%** for prefix-95/99 and identical across C0/C1a/M1. With no forecast ties these are bottom-half ranks (chance 50%); true-event and baseline tie conventions remain disclosed. This suggests useful magnitude separation alongside inadequate event amplitude, not a direction or profitability result. Causes of remaining jumps/heterogeneity remain unresolved.

Annual prefix-defined event counts (same cohorts for every arm):

| year | group | rows | sessions | origins | weight_mass | false_low_rank |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | PREFIX95 | 1089 | 162 | 503 | 0.05473151 | 0.17300305 |
| 2021 | PREFIX99 | 94 | 46 | 86 | 0.0046099291 | 0.10123626 |
| 2022 | PREFIX95 | 2471 | 201 | 782 | 0.10077098 | 0.21186431 |
| 2022 | PREFIX99 | 429 | 109 | 268 | 0.017190476 | 0.10658225 |
| 2023 | PREFIX95 | 686 | 158 | 395 | 0.038100331 | 0.1459865 |
| 2023 | PREFIX99 | 131 | 49 | 106 | 0.0074306086 | 0.15352981 |
| 2024 | PREFIX95 | 930 | 171 | 471 | 0.043671589 | 0.1490636 |
| 2024 | PREFIX99 | 187 | 53 | 140 | 0.0082617903 | 0.11208867 |

| arm | field | group | observed | predicted | ratio | raw_MSE | raw_MAE | MSE_percent_vs_C0 | weight_mass | raw_MSE_loss_share | false_low_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C0 | category | INTRADAY | 0.0075759099 | 0.0066260867 | 0.87462586 | 5.222191e-05 | 0.0047403156 | 0 | nan | nan | nan |
| C0 | category | OVERNIGHT | 0.012430622 | 0.0091219793 | 0.73383128 | 0.00016283167 | 0.0078555806 | 0 | nan | nan | nan |
| C0 | slot | 09:30 | 0.010148502 | 0.0085949751 | 0.84692054 | 8.8507199e-05 | 0.0063020101 | 0 | nan | nan | nan |
| C0 | slot | 10:30 | 0.0072290401 | 0.006317621 | 0.87392253 | 4.3966615e-05 | 0.0044799607 | 0 | nan | nan | nan |
| C0 | slot | 11:30 | 0.0061621815 | 0.0054906333 | 0.89102104 | 3.570865e-05 | 0.0039420059 | 0 | nan | nan | nan |
| C0 | slot | 12:30 | 0.011562181 | 0.0087667077 | 0.75822265 | 0.00014291045 | 0.0073178389 | 0 | nan | nan | nan |
| C0 | slot | 13:30 | 0.012572072 | 0.0096157612 | 0.76485093 | 0.00016854388 | 0.0079286855 | 0 | nan | nan | nan |
| C0 | slot | 14:30 | 0.012666227 | 0.0097085329 | 0.76648972 | 0.00015552656 | 0.0079102688 | 0 | nan | nan | nan |
| C0 | slot | 15:30 | 0.013016966 | 0.0086510501 | 0.66459803 | 0.00018633199 | 0.0082987565 | 0 | nan | nan | nan |
| C0 | tail | PREFIX95 | 0.044512429 | 0.012401814 | 0.27861463 | 0.0013524637 | 0.032111709 | 0 | 0.059318601 | 0.65961046 | 0.16997937 |
| C0 | tail | LE_PREFIX95 | 0.008196338 | 0.0077527446 | 0.94587907 | 4.1676387e-05 | 0.0049445884 | 0 | 0.9406814 | 0.34038954 | 0.52031774 |
| C0 | tail | PREFIX99 | 0.075877916 | 0.013723842 | 0.1808674 | 0.0044045665 | 0.062154074 | 0 | 0.009373201 | 0.34846533 | 0.11835925 |
| C0 | tail | LE_PREFIX99 | 0.0096994324 | 0.0079753738 | 0.8222516 | 7.5554529e-05 | 0.0059835779 | 0 | 0.9906268 | 0.65153467 | 0.50363835 |
| C1a | category | INTRADAY | 0.0075759099 | 0.008846669 | 1.1677368 | 5.2834528e-05 | 0.0052316247 | 1.1731047 | nan | nan | nan |
| C1a | category | OVERNIGHT | 0.012430622 | 0.011782335 | 0.94784755 | 0.00015069462 | 0.0080401879 | -7.4537403 | nan | nan | nan |
| C1a | slot | 09:30 | 0.010148502 | 0.011161087 | 1.0997768 | 8.6762001e-05 | 0.0067571271 | -1.971815 | nan | nan | nan |
| C1a | slot | 10:30 | 0.0072290401 | 0.0084822076 | 1.1733519 | 4.4649685e-05 | 0.0049438278 | 1.5536107 | nan | nan | nan |
| C1a | slot | 11:30 | 0.0061621815 | 0.0075096341 | 1.2186649 | 3.7387512e-05 | 0.004464277 | 4.7015553 | nan | nan | nan |
| C1a | slot | 12:30 | 0.011562181 | 0.011365233 | 0.98296621 | 0.00013417597 | 0.0075858245 | -6.1118539 | nan | nan | nan |
| C1a | slot | 13:30 | 0.012572072 | 0.012361698 | 0.98326652 | 0.00015817122 | 0.0082290938 | -6.1542811 | nan | nan | nan |
| C1a | slot | 14:30 | 0.012666227 | 0.012471198 | 0.98460245 | 0.00014493122 | 0.0081682197 | -6.8125553 | nan | nan | nan |
| C1a | slot | 15:30 | 0.013016966 | 0.011228543 | 0.86260828 | 0.00016822263 | 0.008255187 | -9.7188686 | nan | nan | nan |
| C1a | tail | PREFIX95 | 0.044512429 | 0.015630753 | 0.3511548 | 0.001161447 | 0.028892991 | -14.12361 | 0.059318601 | 0.59147516 | 0.16997937 |
| C1a | tail | LE_PREFIX95 | 0.008196338 | 0.010170199 | 1.2408223 | 4.7247199e-05 | 0.0055022876 | 13.36683 | 0.9406814 | 0.40852484 | 0.52031774 |
| C1a | tail | PREFIX99 | 0.075877916 | 0.017189421 | 0.2265405 | 0.0040001777 | 0.058688495 | -9.1811272 | 0.009373201 | 0.33325301 | 0.11835925 |
| C1a | tail | LE_PREFIX99 | 0.0096994324 | 0.010433287 | 1.0756595 | 7.2900681e-05 | 0.0063399084 | -3.5124932 | 0.9906268 | 0.66674699 | 0.50363835 |
| M1 | category | INTRADAY | 0.0075759099 | 0.0089577906 | 1.1824046 | 5.390485e-05 | 0.0052666348 | 3.2226701 | nan | nan | nan |
| M1 | category | OVERNIGHT | 0.012430622 | 0.012325338 | 0.99153026 | 0.00014995515 | 0.0081336573 | -7.9078706 | nan | nan | nan |
| M1 | slot | 09:30 | 0.010148502 | 0.011611549 | 1.1441638 | 8.8717365e-05 | 0.0069038449 | 0.23745693 | nan | nan | nan |
| M1 | slot | 10:30 | 0.0072290401 | 0.0085388215 | 1.1811833 | 4.5355219e-05 | 0.0049572411 | 3.1583157 | nan | nan | nan |
| M1 | slot | 11:30 | 0.0061621815 | 0.0074217109 | 1.2043967 | 3.8050201e-05 | 0.0044352692 | 6.557378 | nan | nan | nan |
| M1 | slot | 12:30 | 0.011562181 | 0.011844027 | 1.0243765 | 0.00013433334 | 0.0076868011 | -6.0017371 | nan | nan | nan |
| M1 | slot | 13:30 | 0.012572072 | 0.012992258 | 1.0334221 | 0.00015785215 | 0.0083497799 | -6.3435874 | nan | nan | nan |
| M1 | slot | 14:30 | 0.012666227 | 0.01311672 | 1.0355664 | 0.0001448011 | 0.0082975371 | -6.8962233 | nan | nan | nan |
| M1 | slot | 15:30 | 0.013016966 | 0.011689804 | 0.89804365 | 0.00016565037 | 0.0082890125 | -11.099342 | nan | nan | nan |
| M1 | tail | PREFIX95 | 0.044512429 | 0.016738559 | 0.37604235 | 0.0011042366 | 0.027814386 | -18.353692 | 0.059318601 | 0.55465401 | 0.16997937 |
| M1 | tail | LE_PREFIX95 | 0.008196338 | 0.010472764 | 1.277737 | 5.1623424e-05 | 0.005661102 | 23.867319 | 0.9406814 | 0.44534599 | 0.52031774 |
| M1 | tail | PREFIX99 | 0.075877916 | 0.018532348 | 0.24423902 | 0.0038564238 | 0.057345568 | -12.444874 | 0.009373201 | 0.31748543 | 0.11835925 |
| M1 | tail | LE_PREFIX99 | 0.0096994324 | 0.010777212 | 1.1111178 | 7.4666995e-05 | 0.0064257327 | -1.174694 | 0.9906268 | 0.68251457 | 0.50363835 |
| B0-VOL | category | INTRADAY | 0.0075759099 | 0.0082934741 | 1.0947166 | 5.5906843e-05 | 0.0053142406 | 7.0562976 | nan | nan | nan |
| B0-VOL | category | OVERNIGHT | 0.012430622 | 0.012375953 | 0.99560203 | 0.00015427534 | 0.0083224134 | -5.2547041 | nan | nan | nan |
| B0-VOL | slot | 09:30 | 0.010148502 | 0.010353496 | 1.0201994 | 8.8672741e-05 | 0.0067150268 | 0.18703801 | nan | nan | nan |
| B0-VOL | slot | 10:30 | 0.0072290401 | 0.0080169907 | 1.108998 | 4.7864083e-05 | 0.005048748 | 8.8646098 | nan | nan | nan |
| B0-VOL | slot | 11:30 | 0.0061621815 | 0.0070891936 | 1.1504357 | 4.1184782e-05 | 0.0046248181 | 15.335591 | nan | nan | nan |
| B0-VOL | slot | 12:30 | 0.011562181 | 0.01168157 | 1.0103258 | 0.00013731811 | 0.0078221134 | -3.9131797 | nan | nan | nan |
| B0-VOL | slot | 13:30 | 0.012572072 | 0.012610963 | 1.0030934 | 0.00016331905 | 0.008477597 | -3.099981 | nan | nan | nan |
| B0-VOL | slot | 14:30 | 0.012666227 | 0.012757396 | 1.0071978 | 0.00015074016 | 0.0084192328 | -3.0775427 | nan | nan | nan |
| B0-VOL | slot | 15:30 | 0.013016966 | 0.012699445 | 0.97560712 | 0.0001689435 | 0.0086418151 | -9.3319928 | nan | nan | nan |
| B0-VOL | tail | PREFIX95 | 0.044512429 | 0.01591286 | 0.35749251 | 0.0011406978 | 0.028599569 | -15.657783 | 0.059318601 | 0.57629252 | 0.19221866 |
| B0-VOL | tail | LE_PREFIX95 | 0.008196338 | 0.010278147 | 1.2539925 | 5.0403074e-05 | 0.005696923 | 20.939162 | 0.9406814 | 0.42370748 | 0.51913736 |
| B0-VOL | tail | PREFIX99 | 0.075877916 | 0.017188853 | 0.22653301 | 0.0039752789 | 0.058689064 | -9.746421 | 0.009373201 | 0.32681841 | 0.16638324 |
| B0-VOL | tail | LE_PREFIX99 | 0.0096994324 | 0.010538587 | 1.0865159 | 7.5871414e-05 | 0.0065325304 | 0.41941205 | 0.9906268 | 0.67318159 | 0.50324057 |

All annual categories and seven slots, prefix95/99 and complements are in fourfold_groups.csv. Conditional group errors retain original role weights normalized within the group and then equal years. Tail loss shares use EQ unconditional loss contribution divided by EQ total MSE; no equal-row pooling. False-low rate: event-mass fraction with forecast within-origin midrank<=10.5.

Annual reliability is recorded for ten weighted empirical **C0 score deciles**, using one predeclared rule and identical bins across arms. Numeric C0 ranges, means, counts and sessions are in fourfold_groups.csv; annual cutoffs are descriptive historical scores, not deployable calibration boundaries. Equal-year deciles average corresponding annual percentile bins, without pretending they share fixed numerical boundaries. Lowest/highest-decile predicted/realized ratios are C0 0.840/0.743, C1a 1.233/0.923, and M1 1.135/1.003. C1a overcorrects the lowest bin and still underpredicts the highest. These patterns motivate a future question, not an authorized conditional map.

## Decision and limitations

**Retain the global corrections as research benchmarks; do not promote C1a as a complete solution.** The primary raw-MSE improvement and mean-level improvement survive all four chronological years and the stronger B0-VOL comparison. The full success criterion is mixed because MAE and ordinary/intraday errors worsen and extreme-event amplitudes remain very low.

| Finding | Implication | Evidence / researcher decision |
| --- | --- | --- |
| C1a/M1 each improve raw MSE in all years | Global level correction is a useful matched benchmark | Exploratory, same-key, past-only; choose the acceptable MSE/MAE trade-off |
| M1 wins three years; equal-year contrast includes zero | Use simple M1 as the parsimonious scalar comparator; no demonstrated special Jensen advantage | C1a has slightly lower aggregate MSE and MAE and a closer mean ratio; no uniform winner |
| Tail/overnight gains coexist with ordinary/intraday damage | A pooled mean is insufficient to claim full conditional calibration | Consider O1's raw-mean objective as the next controlled question before adding C3 complexity; no implementation authorized |
| B0-VOL is competitive but below calibrated equal-year MSE | Preserve B0-VOL and B0-CLOCK in later same-task comparisons | B0-CLOCK slightly beats C1a in F23; no blanket annual dominance over all controls |
| Rank statistics remain identical | Calibration changes amplitude, not forecast information | No signed-return, economic or tradability inference |

The experiment supports correcting a transformed-location/raw-mean mismatch as a useful amplitude operation. It does not causally allocate the original bias to Jensen's inequality, prove that a conditional smearing law is correct, or remove model misspecification, heteroskedasticity, shifts, source/clock differences and noise. F24's small tail limits estimated-factor precision. Any O1, C2/C3, additional seed or confirmation requires a new explicit decision. **STOP after this report.**

## Reproduction and verification

`.venv/bin/python -m lstm_data.hf20_mag_designa_continue --out reports/experiments/hf20_s9_mag_stage1_session2b_fourfold_2026-10-27 --report` replays saved outputs only. Original --run is single-use; no rerun or new objective is authorized.

Authoritative sources accessed (all numerical populations end in 2024):

- Parent F21 namespace: `reports/experiments/hf20_s9_mag_stage1_session2_designa_2026-10-27/`, with exact bindings in parent_bindings.json. Source F21 checkpoints and scores are referenced, not copied.
- Original S4 root: `reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation/`; `opening_reaudit_v2/S4_ORIGIN_SOURCE_ELIGIBILITY.parquet`, `S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet`, `S4_NUMERICAL_SOURCE_READS.csv`, and original phase recipes/card. The saved read receipt limits source opens to 174 existing adjusted-hourly partitions from 2010-07 through 2024-12. No minute-source reconstruction or new dataset store.
- Original S9 root: `reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation/`; `HF20-S9-F{21,22,23,24}-H4-MAG-S42/{configuration.json,inner_target_recipe.json,oos_scores.parquet}` and target/baseline contract.
- Historical grid/maturity/as-of and FT16 routines, original `hf20_s5s9`, `objective_screen_run.Selector`, `neural_engine.optimizer`, S4 source/math/fit, and ranking/bootstrap implementations are reused. Numerical kernels remain identical to the parent source snapshot.
- D0 report: `reports/experiments/hf20_s9_mag_stage1_session1_d0_2026-10-27/S9_MAG_STAGE1_SESSION1_D0_READONLY_REPORT.md`; research menu under `docs/track_a/`; methodological and consolidation handoffs under `docs/track_a/Consolidation/`. Executed artifacts govern any prose mismatch.

Commands actually used: `--preflight` before fitting, then a single `.venv/bin/python -u -m lstm_data.hf20_mag_designa_continue --run`; execution.log records all epochs. The successor ledger records 132/133/134 and COMPLETED for each new pair, with no failed/aborted start. The initial numerical fit settings were not changed after looking at new OOS results. Only saved-score report fields/narrative were added after fitting.

F21 artifacts and original numerical kernels remain bound in parent_bindings.json; parent code snapshot preserved as parent_implementation.py.txt. F21 annual values are copied unchanged from Session2 and checked against the identical saved population. No F21 scores/checkpoints are duplicated. New per-fold files retain initial/restricted recipes, target scale/tails, selected/final checkpoints, compact epoch trace, coefficients and compressed calibration/OOS scores. New ledgers append a successor; prior131-start history stays byte-identical.

Historical MAG is context, not the causal calibration comparator: it refit through December, whereas C0/C1a/M1 share September training. The archived equal-year transformed MSE0.232454/raw MAE0.006505 and raw mean bias remain untouched. Four years are not independent seeds and have been inspected repeatedly. Source publication/action vintage, fixed survivors and price-only entry before origin+2min issuance remain qualifications. No2025/2026 numerical reads/hashes, acquisitions, strategies, dashboards, O1, C2/C3 or overnight-jump model.

Files: amendment.json, preflight.json, parent_bindings.json, role_counts.csv, selector_candidates.csv, fourfold_metrics.csv, fourfold_groups.csv, paired_MSE.csv, fit_summary.csv, neural_starts.jsonl; F22/F23/F24 outputs only. F21 source reference: reports/experiments/hf20_s9_mag_stage1_session2_designa_2026-10-27

Verification PASS: eight focused tests; Ruff clean; full basic Pylance-stub parity 502 Python files, zero errors/warnings. All four key/weight/axis/phase-recipe/decoder/rank/checkpoint checks pass; 16 bound parent files and ten numerical kernels are unchanged. New work: three pairs, six neural phases, 158 epochs, no retries; ledger134/200; empty continuation queue. Resources remain below 2GB process RAM, 2.5GB task and 15GB project caps. Exact checks/commands: execution_receipt.json, integrity_checks.json and ../../codex_sessions/2026-10-27_230800_hf20_s9_mag_session2b_fourfold.md. For editor verification select .venv/bin/python, Pylance basic, and refresh Problems; the actual editor refresh remains human-confirmed. No commit or push.

STOP: no subsequent fitting or protected-data release is authorized.
