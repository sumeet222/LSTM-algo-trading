# S2-B — explicit clock/calendar MAG

**Status: COMPLETE — 4/4 folds.** Original four-hour target, exploratory/post-search.

**S2-B COMPLETE — provisional calibrated-package improvement; S2-C and S2-D BLOCKED before fitting.** No pooled winner across tasks. S2-B retains the original **80,260 stock-origin rows /4,013 origins /793 sessions**,20 stocks per origin. Equal-year CLOCK-C3 raw MSE is **0.000106665945886**, versus frozen C3 **0.000107226942123**: **−0.5232%**. All four annual point estimates improve (−0.9194%,−0.5224%,−0.0987%,−0.5563%). Paired delta−5.60996e−7, whole-month descriptive95% interval [−1.00812e−6,−1.82444e−7]. F22/F23 annual intervals include zero. These are repeatedly inspected exploratory years, not selection-adjusted confirmation.

Full raw MAE improves0.6460% to0.00675709312; equal-year mean ratio improves1.02670→1.01376, and within-origin magnitude IC rises0.324668→0.330254 with positive annual IC differences in all four years. The system beats M1 full MSE by1.4783% and B0-VOL by4.3873%. Intraday/overnight conditional MSE changes are−0.5778%/−0.5150% versus C3.

The gain is modest and qualified: prefix95/99 realized-tail MSE worsens1.0232%/0.7384%, while ordinary complements improve3.2626%/1.2337%. CLOCK-RAW versus C0 improves only0.4472% equal-year MSE, driven mainly by F24; F21/F22 raw point scores worsen. Thus the primary result supports the clock-aware model **with its fixed matched past-only calibration**, not an isolated claim about raw conditional-mean representation, any individual clock feature or parameter capacity.

Only4 authorized pairs/8 neural phases ran; selected epochs8/13/11/16. No failures, retries, extra variants or seeds. Budget ceiling200→300 was recorded prospectively with the opening count154 preserved; live counter now **158/300**,142 capacity remaining but no further fit authority. No auxiliary/gap model or gap baseline was fitted. Intraday C0-MAE versus C3-MSE preference remains unresolved, and the deferred C0-intraday/M1-overnight routed comparison was not created.

## Design and fairness

One shared H32/one-layer LSTM on the original48×16 own-stock FT16 windows; seed42/CPU float32. Ten known schedule values enter the scalar head after final-hidden dropout.10: seven slot one-hots, current-session remaining trading minutes/240, known horizon-crossing flag, and calendar days until next scheduled XNYS session/7. No metadata sequence, stock/peer ID, event input, proxy or future return enters the model. The trunk is unchanged; head32→1 becomes42→1, increasing parameters6,433→6,443. This tests input/head/optimization together, not information isolated from parameter capacity.

Calendar entries follow the executed XNYS schedule and actual early closes. The complete distinct vector dictionary is clock_dictionary.csv; regular09:30 has390/240 remaining and crossing0, early-close09:30 has210/240 and crossing1. Metadata is repeated identically across20 stocks at an origin and is not dropped. Last15:30 input history still contains48 completed scheduled full hours; its closing stub is not an input hour. The calendar-only lookup may include January2025 dates; no2025 market observation is read.

Original M=log1p(abs(R_total)/own_phase_s) transformed MSE, original qualified-best selector and exact Design A role indices/cutoffs are preserved. Phase target scales and input recipes are independently verified on legal prefixes before starts. Each selected count gets a fresh seed42 model/empty optimizer through September. Reserved Oct–Dec is only for this new encoder’s own fixed C3 IO smearing (session shrinkage kappa25); all coefficients freeze before next-year scores. Raw decoder is diagnostic. No new calibration choice or post-OOS rescue.

| year | role | origins | sessions | rows |
| --- | --- | --- | --- | --- |
| 2021 | inner_train | 11449 | 2100 | 228980 |
| 2021 | selector | 349 | 57 | 6980 |
| 2021 | restricted_refit | 11846 | 2164 | 236920 |
| 2021 | calibration | 283 | 56 | 5660 |
| 2021 | oos | 955 | 188 | 19100 |
| 2022 | inner_train | 12560 | 2301 | 251200 |
| 2022 | selector | 278 | 58 | 5560 |
| 2022 | restricted_refit | 12888 | 2366 | 257760 |
| 2022 | calibration | 245 | 50 | 4900 |
| 2022 | oos | 1180 | 210 | 23600 |
| 2023 | inner_train | 13776 | 2526 | 275520 |
| 2023 | selector | 313 | 59 | 6260 |
| 2023 | restricted_refit | 14137 | 2592 | 282740 |
| 2023 | calibration | 258 | 48 | 5160 |
| 2023 | oos | 887 | 187 | 17740 |
| 2024 | inner_train | 14824 | 2719 | 296480 |
| 2024 | selector | 291 | 69 | 5820 |
| 2024 | restricted_refit | 15167 | 2795 | 303340 |
| 2024 | calibration | 163 | 40 | 3260 |
| 2024 | oos | 991 | 208 | 19820 |

Frozen C3/M1/C0/C1a/B0 comparisons retain original keys, labels, scales and forecast vectors. C0-vs-C3 intraday preference remains metric-dependent and unresolved. No deferred C0-intraday/M1-overnight routed experiment is created.

## Fits and independent calibration

| year | selected_epoch | selector_epochs | raw_minimum_epoch | initial_scale | scale | parameters | seconds | peak_rss_bytes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 8 | 18 | 8 | 0.0057971177 | 0.0058487592 | 6443 | 440.72538 | 904708096 |
| 2022 | 13 | 23 | 13 | 0.0059351246 | 0.0059334067 | 6443 | 485.49587 | 920141824 |
| 2023 | 11 | 21 | 20 | 0.0060723344 | 0.0061216731 | 6443 | 499.61789 | 978681856 |
| 2024 | 16 | 26 | 23 | 0.0061734035 | 0.0061744472 | 6443 | 757.99376 | 978681856 |

| year | group | c0 | c_raw | n_eff | rho | c_star | q_max | top10_share | top1pct_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | INTRADAY | 1.2104693 | 1.1259303 | 49.969862 | 0.66653267 | 1.1541213 | 4.9364507 | 0.020071721 | 0.038310101 |
| 2021 | OVERNIGHT | 1.2104693 | 1.2682915 | 53.007529 | 0.67951811 | 1.2497605 | 8.8361067 | 0.022325273 | 0.055970108 |
| 2022 | INTRADAY | 1.1904559 | 1.105608 | 42.707587 | 0.63076516 | 1.1369368 | 6.1099662 | 0.029180532 | 0.049764705 |
| 2022 | OVERNIGHT | 1.1904559 | 1.2611834 | 44.696801 | 0.64130348 | 1.2358137 | 8.2347742 | 0.024153793 | 0.054167673 |
| 2023 | INTRADAY | 1.1337883 | 1.0963486 | 44.089425 | 0.63815012 | 1.1098961 | 7.2285857 | 0.020236365 | 0.04154134 |
| 2023 | OVERNIGHT | 1.1337883 | 1.1663397 | 44.983946 | 0.64277522 | 1.1547115 | 5.1344732 | 0.029703799 | 0.063558739 |
| 2024 | INTRADAY | 1.1381899 | 1.0682918 | 30.687987 | 0.55107014 | 1.0996711 | 5.1876413 | 0.040403059 | 0.05370229 |
| 2024 | OVERNIGHT | 1.1381899 | 1.1968541 | 32.95592 | 0.56863769 | 1.1715486 | 10.241991 | 0.05659856 | 0.082788596 |

These are new model-specific calibration moments, not transferred historical C3 coefficients. q uses unconstrained Mhat. Finite/nonnegative decoder guards and exact selected checkpoint reload equality are required. F24 tail precision remains limited; no q trimming or alternative scalar map is fitted.

## Same-target annual and equal-year results

| year | scope | arm | raw_MSE | raw_MAE | observed | predicted | bias | ratio | magnitude_IC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | FULL | CLOCK-C3 | 8.2554613e-05 | 0.0063781675 | 0.0098002675 | 0.010211883 | 0.00041161566 | 1.0420005 | 0.32627607 |
| 2021 | FULL | CLOCK-RAW | 9.0561076e-05 | 0.0060824636 | 0.0098002675 | 0.0074034373 | -0.0023968303 | 0.75543216 | 0.32627607 |
| 2021 | FULL | C3 | 8.3320658e-05 | 0.006421753 | 0.0098002675 | 0.010306108 | 0.00050584098 | 1.051615 | 0.31785841 |
| 2021 | FULL | M1 | 8.3790671e-05 | 0.0063963177 | 0.0098002675 | 0.010205226 | 0.00040495892 | 1.0413212 | 0.31785841 |
| 2021 | FULL | C0 | 9.0541114e-05 | 0.0061042972 | 0.0098002675 | 0.0075378642 | -0.0022624033 | 0.76914882 | 0.31785841 |
| 2021 | FULL | B0-VOL | 8.6535921e-05 | 0.0066089924 | 0.0098002675 | 0.010256419 | 0.00045615162 | 1.0465448 | 0.31183632 |
| 2021 | FULL | B0-CLOCK | 8.8733837e-05 | 0.0064413665 | 0.0098002675 | 0.0093055751 | -0.00049469243 | 0.94952256 | 0.29038533 |
| 2022 | FULL | CLOCK-C3 | 0.00014590951 | 0.0083086676 | 0.012951183 | 0.012936514 | -1.4668811e-05 | 0.99886738 | 0.35445091 |
| 2022 | FULL | CLOCK-RAW | 0.0001591903 | 0.0080603043 | 0.012951183 | 0.0098267996 | -0.0031243837 | 0.75875689 | 0.35445091 |
| 2022 | FULL | C3 | 0.00014667567 | 0.0083746314 | 0.012951183 | 0.013237313 | 0.00028613009 | 1.022093 | 0.35029686 |
| 2022 | FULL | M1 | 0.00014937987 | 0.0086367779 | 0.012951183 | 0.014210493 | 0.0012593093 | 1.0972351 | 0.35029686 |
| 2022 | FULL | C0 | 0.00015850978 | 0.0080691855 | 0.012951183 | 0.010049479 | -0.0029017043 | 0.77595064 | 0.35029686 |
| 2022 | FULL | B0-VOL | 0.00015369642 | 0.0084733784 | 0.012951183 | 0.012531746 | -0.00041943677 | 0.96761402 | 0.32314717 |
| 2022 | FULL | B0-CLOCK | 0.00016861834 | 0.0082521988 | 0.012951183 | 0.0093759284 | -0.0035752548 | 0.72394377 | 0.3178606 |
| 2023 | FULL | CLOCK-C3 | 8.6173073e-05 | 0.0059986859 | 0.0092524379 | 0.0091179546 | -0.00013448331 | 0.9854651 | 0.32380415 |
| 2023 | FULL | CLOCK-RAW | 9.1029308e-05 | 0.005794158 | 0.0092524379 | 0.0072747552 | -0.0019776827 | 0.78625279 | 0.32380415 |
| 2023 | FULL | C3 | 8.6258208e-05 | 0.0060253978 | 0.0092524379 | 0.0092152346 | -3.7203377e-05 | 0.99597907 | 0.32024473 |
| 2023 | FULL | M1 | 8.6602732e-05 | 0.0059913023 | 0.0092524379 | 0.0090094132 | -0.00024302474 | 0.97373398 | 0.32024473 |
| 2023 | FULL | C0 | 9.1161785e-05 | 0.0058106884 | 0.0092524379 | 0.0073476242 | -0.0019048138 | 0.79412845 | 0.32024473 |
| 2023 | FULL | B0-VOL | 9.0228688e-05 | 0.0063314547 | 0.0092524379 | 0.0097563049 | 0.00050386696 | 1.0544578 | 0.2909517 |
| 2023 | FULL | B0-CLOCK | 8.6579247e-05 | 0.0061385546 | 0.0092524379 | 0.0096074191 | 0.00035498113 | 1.0383662 | 0.30364354 |
| 2024 | FULL | CLOCK-C3 | 0.00011202659 | 0.0063428514 | 0.0092491933 | 0.0095544881 | 0.00030529483 | 1.0330077 | 0.31648505 |
| 2024 | FULL | CLOCK-RAW | 0.00011630047 | 0.0059863549 | 0.0092491933 | 0.0075584134 | -0.0016907799 | 0.81719704 | 0.31648505 |
| 2024 | FULL | C3 | 0.00011265323 | 0.0063823356 | 0.0092491933 | 0.0095956812 | 0.00034648786 | 1.0374614 | 0.3102724 |
| 2024 | FULL | M1 | 0.00011329232 | 0.00651156 | 0.0092491933 | 0.0099979316 | 0.00074873831 | 1.0809517 | 0.3102724 |
| 2024 | FULL | C0 | 0.00011892159 | 0.0060056223 | 0.0092491933 | 0.0071960535 | -0.0020531398 | 0.77801958 | 0.3102724 |
| 2024 | FULL | B0-VOL | 0.00011578065 | 0.0066372528 | 0.0092491933 | 0.0098591363 | 0.00060994296 | 1.0659455 | 0.29063745 |
| 2024 | FULL | B0-CLOCK | 0.00011474675 | 0.0065242191 | 0.0092491933 | 0.0097328363 | 0.00048364298 | 1.0522903 | 0.29931135 |
| EQ | FULL | CLOCK-C3 | 0.00010666595 | 0.0067570931 | 0.01031327 | 0.01045521 | 0.00014193959 | 1.0137628 | 0.33025404 |
| EQ | FULL | CLOCK-RAW | 0.00011427029 | 0.0064808202 | 0.01031327 | 0.0080158513 | -0.0022974191 | 0.77723661 | 0.33025404 |
| EQ | FULL | C3 | 0.00010722694 | 0.0068010295 | 0.01031327 | 0.010588584 | 0.00027531389 | 1.0266951 | 0.3246681 |
| EQ | FULL | M1 | 0.0001082664 | 0.0068839895 | 0.01031327 | 0.010855766 | 0.00054249545 | 1.0526017 | 0.3246681 |
| EQ | FULL | C0 | 0.00011478357 | 0.0064974483 | 0.01031327 | 0.0080327552 | -0.0022805153 | 0.77887564 | 0.3246681 |
| EQ | FULL | B0-VOL | 0.00011156042 | 0.0070127696 | 0.01031327 | 0.010600902 | 0.00028763119 | 1.0278894 | 0.30414316 |
| EQ | FULL | B0-CLOCK | 0.00011466954 | 0.0068390848 | 0.01031327 | 0.0095054397 | -0.00080783078 | 0.92167075 | 0.3028002 |

All baselines and both category scopes are in metrics.csv. Raw MSE uses squared absolute-log-return units; MAE/means/bias use absolute log-return units. Annual weights are equal stocks→origins/session→sessions/year; conditional raw scores restrict and normalize the original weights. EQ averages four annual metrics, ratio of equal-year means. Ranking uses existing midrank origin→session→year reducer. Four years are not four seeds or independent confirmation.

## Paired month-block uncertainty

| scope | left | right | year | delta | low | high | percent | includes_zero |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FULL | CLOCK-C3 | C3 | 2021 | -7.6604495e-07 | -1.5592304e-06 | -1.4208389e-07 | -0.91939378 | False |
| FULL | CLOCK-C3 | C3 | 2022 | -7.6616623e-07 | -2.0956709e-06 | 6.7072798e-07 | -0.52235399 | True |
| FULL | CLOCK-C3 | C3 | 2023 | -8.513437e-08 | -5.6012667e-07 | 3.2367465e-07 | -0.098697123 | True |
| FULL | CLOCK-C3 | C3 | 2024 | -6.266394e-07 | -1.0833898e-06 | -2.0935969e-07 | -0.55625515 | False |
| FULL | CLOCK-C3 | C3 | EQ | -5.6099624e-07 | -1.0081164e-06 | -1.824438e-07 | -0.52318589 | False |
| FULL | CLOCK-C3 | M1 | 2021 | -1.2360574e-06 | -2.6427291e-06 | -2.0635429e-07 | -1.4751731 | False |
| FULL | CLOCK-C3 | M1 | 2022 | -3.4703678e-06 | -5.7342216e-06 | -1.4705607e-06 | -2.323183 | False |
| FULL | CLOCK-C3 | M1 | 2023 | -4.2965817e-07 | -9.4992688e-07 | 1.3515186e-07 | -0.49612542 | True |
| FULL | CLOCK-C3 | M1 | 2024 | -1.2657298e-06 | -1.746468e-06 | -7.5861583e-07 | -1.1172247 | False |
| FULL | CLOCK-C3 | M1 | EQ | -1.6004533e-06 | -2.2538426e-06 | -1.0469585e-06 | -1.4782549 | False |
| FULL | CLOCK-C3 | B0-VOL | 2021 | -3.9813079e-06 | -5.6560935e-06 | -2.3331358e-06 | -4.6007575 | False |
| FULL | CLOCK-C3 | B0-VOL | 2022 | -7.786916e-06 | -1.0470547e-05 | -5.1069727e-06 | -5.0664263 | False |
| FULL | CLOCK-C3 | B0-VOL | 2023 | -4.0556151e-06 | -6.2271349e-06 | -2.4322034e-06 | -4.4948177 | False |
| FULL | CLOCK-C3 | B0-VOL | 2024 | -3.7540625e-06 | -4.78243e-06 | -2.6124691e-06 | -3.2423919 | False |
| FULL | CLOCK-C3 | B0-VOL | EQ | -4.8944754e-06 | -5.9106947e-06 | -3.9154683e-06 | -4.3872866 | False |
| FULL | CLOCK-RAW | C0 | 2021 | 1.9961544e-08 | -8.9140377e-07 | 7.2133559e-07 | 0.022046939 | True |
| FULL | CLOCK-RAW | C0 | 2022 | 6.8052151e-07 | -2.7772265e-07 | 1.7363337e-06 | 0.42932461 | True |
| FULL | CLOCK-RAW | C0 | 2023 | -1.3247741e-07 | -6.4534245e-07 | 3.6895711e-07 | -0.14532121 | True |
| FULL | CLOCK-RAW | C0 | 2024 | -2.6211211e-06 | -3.6195879e-06 | -1.8949615e-06 | -2.2040751 | False |
| FULL | CLOCK-RAW | C0 | EQ | -5.1327887e-07 | -9.2809557e-07 | -1.4160747e-07 | -0.44717104 | False |
| INTRADAY | CLOCK-C3 | C3 | 2021 | 8.9949209e-08 | -3.9934418e-07 | 4.9428132e-07 | 0.20558508 | True |
| INTRADAY | CLOCK-C3 | C3 | 2022 | -7.3375851e-07 | -1.610819e-06 | 2.7554446e-07 | -0.96374274 | True |
| INTRADAY | CLOCK-C3 | C3 | 2023 | 1.4363451e-07 | -1.3735534e-07 | 4.2106388e-07 | 0.36275927 | True |
| INTRADAY | CLOCK-C3 | C3 | 2024 | -6.8747744e-07 | -1.3056232e-06 | -5.691135e-08 | -1.4929956 | False |
| INTRADAY | CLOCK-C3 | C3 | EQ | -2.9691306e-07 | -6.2500713e-07 | -2.7998193e-08 | -0.57784585 | False |
| OVERNIGHT | CLOCK-C3 | C3 | 2021 | -1.4531855e-06 | -2.5842004e-06 | -4.9694679e-07 | -1.2627242 | False |
| OVERNIGHT | CLOCK-C3 | C3 | 2022 | -7.9210311e-07 | -2.6553601e-06 | 1.0140246e-06 | -0.38994798 | True |
| OVERNIGHT | CLOCK-C3 | C3 | 2023 | -2.6240169e-07 | -9.5022052e-07 | 3.9829718e-07 | -0.21435179 | True |
| OVERNIGHT | CLOCK-C3 | C3 | 2024 | -5.8374142e-07 | -1.176974e-06 | 1.6669203e-07 | -0.36571022 | True |
| OVERNIGHT | CLOCK-C3 | C3 | EQ | -7.7285792e-07 | -1.3569559e-06 | -2.2312207e-07 | -0.51502509 | False |

400 draws/seed22042 whole-calendar-month blocks within year, then equal years. Conditional numerator and original group weight mass are sampled together. No IID rows; intervals condition on selected encoders/scalars and repeated research, not selection-adjusted significance.

## Clocks, calendar periods, tails and ranking

The mean ratio improves on aggregate and in three years; F23’s new ratio0.98547 is farther from1 than old C3 0.99598. Both conditional means improve at equal-year aggregation: intraday1.06510→1.04039, overnight1.00887→1.00111. Intraday MSE worsens slightly in F21/F23 and improves F22/F24; overnight MSE improves in every annual point, with several wide intervals. Do not treat those overlapping groups as independent replications or declare a universally preferred intraday forecast. C0’s intraday MAE0.00474032 still undercuts calibrated CLOCK-C3 0.00494253, despite the latter’s lower MSE. No routed mixture is evaluated.

The ordinary prefix95 complement improves3.2626% MSE versus C3, while prefix95 tails worsen1.0232%; prefix99 complement improves1.2337%, tails worsen0.7384%. Whole-panel prefix95/99 amplitude ratios are0.35787/0.23239 and loss shares58.9180%/33.2966%. Tail-outcome selection does not itself establish conditional-mean miscalibration. Whole-panel prefix99 false-low rank fraction rises11.8359%→12.6699%, despite better overall IC; prefix95 is roughly unchanged16.9979%→16.9008%. This is not a new event detector or gap predictor.

15:30 mean ratio improves0.91902→0.96752 and MSE improves1.5749%, while MAE worsens0.9077%.09:30 MSE worsens0.3704% while MAE improves1.2088%. All seven slots, quarters and shared reliability deciles remain in groups.csv; fixed historical binning is descriptive, not a deployable correction map. Calendar/early-close exceptions retain their original endpoint category.

All eight new calibration factors are finite. F24 remains least precise: n_eff30.69 intraday/32.96 overnight; overnight maximum q10.2420, top10 weighted contribution5.6599%, top1%8.2789%. No residual trimming, pooling-strength search or fallback was used. Raw and calibrated within-origin ranks are identical with zero clamp rows; calibration cannot account for the observed ranking change versus the old encoder. The new input/head/learning package can alter trained weights, but no authorized ablation isolates information from the additional10 head parameters.

| field | group | rows | sessions | raw_MSE | raw_MAE | ratio | raw_MSE_loss_share | false_low_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| slot | 09:30 | 9900 | 495 | 8.6004041e-05 | 0.0064565913 | 0.96388652 | 0.097607236 | 0.5 |
| slot | 10:30 | 12200 | 610 | 4.2668682e-05 | 0.0046726649 | 1.0607265 | 0.060648222 | 0.5 |
| slot | 11:30 | 12920 | 646 | 3.5084057e-05 | 0.0041945651 | 1.1115589 | 0.055230749 | 0.5 |
| slot | 12:30 | 12000 | 600 | 0.00013402839 | 0.0077031288 | 1.022969 | 0.19410675 | 0.5 |
| slot | 13:30 | 10800 | 540 | 0.00015826973 | 0.0083132083 | 1.0069231 | 0.18750269 | 0.5 |
| slot | 14:30 | 10940 | 547 | 0.00014499436 | 0.008250306 | 1.0111282 | 0.1773489 | 0.5 |
| slot | 15:30 | 11500 | 575 | 0.00016307744 | 0.0084183492 | 0.96752063 | 0.22755546 | 0.5 |
| tail_OVERNIGHT | PREFIX95 | 4201 | 638 | 0.0011936796 | 0.028876471 | 0.3633727 | 0.50779541 | 0.17962689 |
| tail_OVERNIGHT | LE_PREFIX95 | 41259 | 771 | 5.9114777e-05 | 0.0063090167 | 1.2879838 | 0.28325974 | 0.5297461 |
| tail_OVERNIGHT | PREFIX99 | 745 | 226 | 0.0040241844 | 0.058625492 | 0.23305245 | 0.30565801 | 0.14097586 |
| tail_OVERNIGHT | LE_PREFIX99 | 44715 | 771 | 9.3403734e-05 | 0.00741959 | 1.0769914 | 0.48539714 | 0.50552082 |

Outcome-selected tails are retrospective diagnostics, not event probabilities; their underforecast amplitudes alone do not prove conditional-mean bias. False-low means average within-origin magnitude rank≤10.5. Reliability groups use identical saved-C3 decile membership across arms, with explicit annual numeric ranges/counts; no map is fitted on the bins. Quarter/clock/stock observations are dependent, not independent replications.

| arm | magnitude_IC | pair_concordance | top4 | bottom4 | tie_rate | constant_rate |
| --- | --- | --- | --- | --- | --- | --- |
| CLOCK-C3 | 0.33025404 | 0.61944331 | 0.42946585 | 0.30302756 | 0 | 0 |
| CLOCK-RAW | 0.33025404 | 0.61944331 | 0.42946585 | 0.30302756 | 0 | 0 |
| C3 | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| M1 | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| C1a | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| C0 | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| B0-VOL | 0.30414316 | 0.6094227 | 0.40988649 | 0.29618868 | 0.00026150811 | 0 |
| B0-CLOCK | 0.3028002 | 0.60852865 | 0.38668138 | 0.30584502 | 0 | 0 |
| B0-RMEAN | 0.30023827 | 0.60754095 | 0.39069215 | 0.30584502 | 0 | 0 |
| B0-RMED | 0.29611443 | 0.60612527 | 0.37416629 | 0.30584502 | 0 | 0 |

Clock metadata enters as a common additive term in the linear M head for all stocks at an origin; it cannot itself reorder those stocks absent clamp ties. Changed rankings can arise through newly trained trunk/head weights. Do not interpret level correction or a nonzero clock-head gradient as new cross-sectional information. Pair ties get half credit (chance.5); retrieval uses fractional boundary ties (chance.2).

## Scientific decision

**Retain S2-B CLOCK-C3 as a provisional exploratory candidate for researcher review**, with frozen C3/M1/C0 and B0 controls still visible. The declared same-target raw-MSE comparison improves in all four annual points and equal-year mean, accompanied by better MAE/overall rank association. Benefits are mostly ordinary-period accuracy and conditional level balance; extreme-event errors and some clocks worsen. No universal model, intraday preference, clock feature or independent-confirmation claim is established. Do not auto-promote, alter the feature vector, fit another calibrator or create a routed system.

S2-C is unknown, not a failed model: original overnight origins lack all20 genuine component prices, especially next opens. Supported signed additivity is numerically correct but cannot fill missing labels. No price proxy, source repair, partial-component population rescue or auxiliary fit is authorized. S2-D is also unknown: new genuine-gap admissions and next-open maturity produce too few selector sessions in F22/F23 under the frozen minimums. No minimum/window/horizon change was made. A future researcher decision must address those exact gates; neither task inherits S2-B’s outcome or four-hour metric.

The label remains a nominal-origin price-only240-trading-minute endpoint return, beginning before approximate origin+2min issuance; it is not an executable post-issuance return, integrated variance, option value or trading P&L. S2-D’s specified close-to-next-open label would be a different task at a15:32 forecast time, but no such model or economic test ran.

## Reproduction and integrity

Commands: `.venv/bin/python -m pytest tests/test_hf20_stage2_bcd.py tests/test_hf20_mag_c3_io.py -q` — **10 passed** (4.64s); `.venv/bin/ruff check src/lstm_data/hf20_stage2_bcd.py tests/test_hf20_stage2_bcd.py --output-format concise` — PASS; `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist` — **510 files, zero errors/warnings** (83.335s). Select repository `.venv/bin/python`, keep Pylance basic and refresh Problems; final editor refresh remains human-confirmed. No ignores, exclusions, casts or severity reductions. Exact source/key/weight/C3 reproduction, all eight own-phase scale/FT16 parity checks, same frozen calibration/OOS checkpoint and zero-error reload pass. Fit traces total136 epochs/21,020 updates/302 clipped batches; fit-lifecycle sum2,183.83s, peak training RSS978,681,856 bytes, below inherited2GB process cap. No extra optimizer start occurred.

The source/role/price specifications were frozen before numerical endpoint proof; the common gate receipt preceded every fit. D’s inherited four-hour target scale/threshold references were removed through an append-only protocol_v2.json and planning_receipt_v2.json clarification before fitting; previous versions remain unchanged. No gap scale or threshold was fitted/transferred. Existing genuine minute references were read from the saved S4 component artifact only; no minute store was opened or rebuilt. Historical input components use only the174 permitted adjusted-hourly partitions through2024 and original causal FT16 definitions. Calendar-only next-session dates can extend into January2025; no2025 market value or protected2026 content/hash was accessed. No deferred route, new source, options/trade, dashboard, commit or push. Standard session handoff: `reports/codex_sessions/2026-10-28_132355_hf20_stage2_bcd_clock_components_gap.md`.

Run `.venv/bin/python -m lstm_data.hf20_stage2_bcd --report` for saved-score replay only; no training/inference or raw-source numerical reads. The original `--run` is single use and refuses a started namespace. No future data, source repairs, unselected forecasts, deferred router, dashboard, options/trading, extra seed or automatic next stage.
