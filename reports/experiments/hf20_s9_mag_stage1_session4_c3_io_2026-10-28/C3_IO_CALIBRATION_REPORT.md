# C3 IO calibration — HF20 Stage1 / Session4

**Status: COMPLETE — four valid folds.** One fixed C3-IO-SMEAR arm; zero neural fits or forward passes. All results exploratory/post-search.

## Executive decision

**Provisional raw-MSE candidate, with a mixed ordinary/tail trade-off.** C3 equal-year raw MSE is **0.000107226942123**, versus C1a 0.000108218653033 (−0.9164%) and M1 0.000108266399189 (−0.9601%). C3 wins on point MSE in all four years. Equal-year paired 95% descriptive intervals are [−1.25137e−6, −7.31857e−7] against C1a and [−1.36283e−6, −7.23168e−7] against M1; both exclude zero, conditional on the fitted histories. Annual C3−M1 for F21 includes zero. C3 also has lower equal-year MSE than frozen O1 and all B0 controls. These are repeatedly inspected exploratory years, not independent confirmation.

C3 improves intraday MSE relative to both global corrections and reduces their intraday overprediction. It slightly improves overnight MSE versus C1a, while overnight MSE remains 0.0714% worse than M1. **The prefix95 ordinary complement worsens by 2.4411% versus C1a at equal-year aggregation, with deterioration in all four years**, despite improving versus M1 in aggregate. No new ranking information is acquired. The pooled mean ratio moves farther from one than C1a (1.02670 vs 1.01819), although conditional means become better balanced. No claim of universal calibration improvement is warranted.

Exact evaluation population: **80,260 stock-origin rows, 4,013 origins, 793 sessions**, 20 stocks per admitted origin, unchanged across all arms. Annual coverage:

| year | rows | origins | sessions |
| --- | --- | --- | --- |
| 2021 | 19100 | 955 | 188 |
| 2022 | 23600 | 1180 | 210 |
| 2023 | 17740 | 887 | 187 |
| 2024 | 19820 | 991 | 208 |
| EQ | 80260 | 4013 | 793 |

## Experiment and preflight

A=abs(log(P_endpoint/P_origin)); existing four-trading-hour endpoints and the exact original20-stock tensor order are preserved. On regular full sessions, origin slots09:30/10:30/11:30 map to INTRADAY;12:30/13:30/14:30/15:30 map to saved OVERNIGHT, meaning overnight-crossing. On saved scheduled early-close days, some morning origins also cross sessions. Executed category and endpoint keys take precedence over the prompt's simplified slot map: these existing labels are preserved, verified against saved exchange session-close metadata, and enumerated in protocol.json. No outcome-based regrouping occurs. The closing stub, genuine endpoints and price-only timing before approximate origin+2min issuance are unchanged. No new jump label or information set.

The saved September-restricted encoder/scale supplies both October–December independent calibration and next-year C0 scores. OOS keys are matched to saved S4 eligibility/DesignA role indices and original S9 score keys, preserving the previously verified48-step embargo. Calibration labels mature before the saved December cutoff and outer evaluation. Receipts/result hashes bind the same frozen network across both populations; no checkpoint is opened or called here.

| year | group | sessions | origins | rows | weight_mass | n_eff | first_date | last_date |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | INTRADAY | 53 | 118 | 2360 | 0.40616497 | 49.969862 | 2020-10-13 | 2020-12-30 |
| 2021 | OVERNIGHT | 56 | 165 | 3300 | 0.59383503 | 53.007529 | 2020-10-12 | 2020-12-30 |
| 2022 | INTRADAY | 47 | 108 | 2160 | 0.45461905 | 42.707587 | 2021-10-13 | 2021-12-31 |
| 2022 | OVERNIGHT | 47 | 137 | 2740 | 0.54538095 | 44.696801 | 2021-10-12 | 2021-12-30 |
| 2023 | INTRADAY | 46 | 119 | 2380 | 0.46507937 | 44.089425 | 2022-10-13 | 2022-12-30 |
| 2023 | OVERNIGHT | 47 | 139 | 2780 | 0.53492063 | 44.983946 | 2022-10-13 | 2022-12-29 |
| 2024 | INTRADAY | 35 | 73 | 1460 | 0.45630952 | 30.687987 | 2023-10-12 | 2023-12-29 |
| 2024 | OVERNIGHT | 36 | 90 | 1800 | 0.54369048 | 32.95592 | 2023-10-11 | 2023-12-28 |

q=exp(log1p(A/s)−unconstrained_Mhat). c0=Ecal,w[q]; c_raw,g=Ecal,w[q|g]. Session mass is each group's existing row-weight sum per session, normalized over sessions with that group. n_eff=1/sum(p_day²), rho=n_eff/(n_eff+25), c_star=c0+rho(c_raw−c0). Ahat_C3=s*max(0,exp(Mhat)*c_star−1). κ=25 session-equivalents was fixed before category moments; no grid, stock effects, seven-slot fitting, clipping, trimming or post-hoc renormalization.

All-four preflight and protocol.json were saved before calculating new category moments. Preflight projected OOS keys/predictions but no OOS labels. All eight factors were frozen in calibration_coefficients.csv before OOS outcomes were read for scoring. Existing global c0 and saved C1a/C0/M1 decoders reproduce on both calibration and OOS rows within atol1e−14/rtol1e−13. This is reconstruction of old controls, not a new arm. Empty/nonfinite category moments block rather than fall back.

## Coefficients and precision

| year | group | scale | c0 | c_raw | n_eff | rho | c_star | delta_from_global |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | INTRADAY | 0.0058487592 | 1.2055995 | 1.0957086 | 49.969862 | 0.66653267 | 1.1323536 | -0.073245902 |
| 2021 | OVERNIGHT | 0.0058487592 | 1.2055995 | 1.2807616 | 53.007529 | 0.67951811 | 1.2566735 | 0.051073965 |
| 2022 | INTRADAY | 0.0059334067 | 1.1908408 | 1.0726385 | 42.707587 | 0.63076516 | 1.1162829 | -0.074557875 |
| 2022 | OVERNIGHT | 0.0059334067 | 1.1908408 | 1.2893719 | 44.696801 | 0.64130348 | 1.2540292 | 0.063188359 |
| 2023 | INTRADAY | 0.0061216731 | 1.1328387 | 1.0674075 | 44.089425 | 0.63815012 | 1.0910838 | -0.041754907 |
| 2023 | OVERNIGHT | 0.0061216731 | 1.1328387 | 1.1897269 | 44.983946 | 0.64277522 | 1.169405 | 0.036566341 |
| 2024 | INTRADAY | 0.0061744472 | 1.1705834 | 1.0722635 | 30.687987 | 0.55107014 | 1.1164022 | -0.054181175 |
| 2024 | OVERNIGHT | 0.0061744472 | 1.1705834 | 1.2531015 | 32.95592 | 0.56863769 | 1.2175063 | 0.046922915 |

| year | group | sessions | origins | rows | weight_mass | q_max | top10_share | top1pct_share | global_q_max | global_top10_share | global_top1pct_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | INTRADAY | 53 | 118 | 2360 | 0.40616497 | 4.952466 | 0.020568006 | 0.038688093 | 9.1530765 | 0.015028698 | 0.056525852 |
| 2021 | OVERNIGHT | 56 | 165 | 3300 | 0.59383503 | 9.1530765 | 0.023822664 | 0.05954951 | 9.1530765 | 0.015028698 | 0.056525852 |
| 2022 | INTRADAY | 47 | 108 | 2160 | 0.45461905 | 5.9480228 | 0.029290233 | 0.050422579 | 8.2372115 | 0.015570929 | 0.055273496 |
| 2022 | OVERNIGHT | 47 | 137 | 2740 | 0.54538095 | 8.2372115 | 0.024493421 | 0.054857784 | 8.2372115 | 0.015570929 | 0.055273496 |
| 2023 | INTRADAY | 46 | 119 | 2380 | 0.46507937 | 6.9630566 | 0.020540679 | 0.041381855 | 6.9630566 | 0.017732427 | 0.058433541 |
| 2023 | OVERNIGHT | 47 | 139 | 2780 | 0.53492063 | 5.1366467 | 0.031564551 | 0.066504153 | 6.9630566 | 0.017732427 | 0.058433541 |
| 2024 | INTRADAY | 35 | 73 | 1460 | 0.45630952 | 5.2193332 | 0.041393822 | 0.055319305 | 10.898311 | 0.032815579 | 0.072587355 |
| 2024 | OVERNIGHT | 36 | 90 | 1800 | 0.54369048 | 10.898311 | 0.056382516 | 0.082870482 | 10.898311 | 0.032815579 | 0.072587355 |

n_eff is a weight-concentration measure in sessions, not an independent-observation count or posterior probability. Shrinkage is a fixed convention. Calibration tails have56/50/48/40 sessions; F24 precision remains limited. Top10/top1% shares use weighted q contributions, not the largest q alone. No trimming is used. All values remain finite; concentration diagnostics are reported without OOS repair.

## Annual and equal-year matched scores

| year | arm | raw_MSE | raw_MAE | observed | predicted | bias | ratio | magnitude_IC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | C3-IO-SMEAR | 8.3320658e-05 | 0.006421753 | 0.0098002675 | 0.010306108 | 0.00050584098 | 1.051615 | 0.31785841 |
| 2021 | C1a | 8.4303166e-05 | 0.0064637727 | 0.0098002675 | 0.010290148 | 0.00048988031 | 1.0499864 | 0.31785841 |
| 2021 | M1 | 8.3790671e-05 | 0.0063963177 | 0.0098002675 | 0.010205226 | 0.00040495892 | 1.0413212 | 0.31785841 |
| 2021 | C0 | 9.0541114e-05 | 0.0061042972 | 0.0098002675 | 0.0075378642 | -0.0022624033 | 0.76914882 | 0.31785841 |
| 2021 | O1 | 8.5271069e-05 | 0.0062557455 | 0.0098002675 | 0.0091671809 | -0.00063308666 | 0.93540108 | 0.3137893 |
| 2021 | B0-VOL | 8.6535921e-05 | 0.0066089924 | 0.0098002675 | 0.010256419 | 0.00045615162 | 1.0465448 | 0.31183632 |
| 2021 | B0-CLOCK | 8.8733837e-05 | 0.0064413665 | 0.0098002675 | 0.0093055751 | -0.00049469243 | 0.94952256 | 0.29038533 |
| 2021 | B0-RMEAN | 9.6342162e-05 | 0.0067870981 | 0.0098002675 | 0.0093076165 | -0.00049265105 | 0.94973086 | 0.289525 |
| 2021 | B0-RMED | 0.00010897265 | 0.006576386 | 0.0098002675 | 0.0062980819 | -0.0035021856 | 0.64264387 | 0.28093515 |
| 2022 | C3-IO-SMEAR | 0.00014667567 | 0.0083746314 | 0.012951183 | 0.013237313 | 0.00028613009 | 1.022093 | 0.35029686 |
| 2022 | C1a | 0.00014822502 | 0.008390051 | 0.012951183 | 0.013099666 | 0.00014848261 | 1.0114648 | 0.35029686 |
| 2022 | M1 | 0.00014937987 | 0.0086367779 | 0.012951183 | 0.014210493 | 0.0012593093 | 1.0972351 | 0.35029686 |
| 2022 | C0 | 0.00015850978 | 0.0080691855 | 0.012951183 | 0.010049479 | -0.0029017043 | 0.77595064 | 0.35029686 |
| 2022 | O1 | 0.00014938804 | 0.0083570315 | 0.012951183 | 0.012775428 | -0.00017575533 | 0.9864294 | 0.34362343 |
| 2022 | B0-VOL | 0.00015369642 | 0.0084733784 | 0.012951183 | 0.012531746 | -0.00041943677 | 0.96761402 | 0.32314717 |
| 2022 | B0-CLOCK | 0.00016861834 | 0.0082521988 | 0.012951183 | 0.0093759284 | -0.0035752548 | 0.72394377 | 0.3178606 |
| 2022 | B0-RMEAN | 0.00017887366 | 0.0084948737 | 0.012951183 | 0.0093897435 | -0.0035614397 | 0.72501047 | 0.31318948 |
| 2022 | B0-RMED | 0.00021279945 | 0.0089435291 | 0.012951183 | 0.0063774046 | -0.0065737787 | 0.49241868 | 0.31247937 |
| 2023 | C3-IO-SMEAR | 8.6258208e-05 | 0.0060253978 | 0.0092524379 | 0.0092152346 | -3.7203377e-05 | 0.99597907 | 0.32024473 |
| 2023 | C1a | 8.6835625e-05 | 0.0060297739 | 0.0092524379 | 0.0091368676 | -0.00011557032 | 0.9875092 | 0.32024473 |
| 2023 | M1 | 8.6602732e-05 | 0.0059913023 | 0.0092524379 | 0.0090094132 | -0.00024302474 | 0.97373398 | 0.32024473 |
| 2023 | C0 | 9.1161785e-05 | 0.0058106884 | 0.0092524379 | 0.0073476242 | -0.0019048138 | 0.79412845 | 0.32024473 |
| 2023 | O1 | 8.7056455e-05 | 0.0060343771 | 0.0092524379 | 0.0091027977 | -0.00014964019 | 0.98382694 | 0.30901184 |
| 2023 | B0-VOL | 9.0228688e-05 | 0.0063314547 | 0.0092524379 | 0.0097563049 | 0.00050386696 | 1.0544578 | 0.2909517 |
| 2023 | B0-CLOCK | 8.6579247e-05 | 0.0061385546 | 0.0092524379 | 0.0096074191 | 0.00035498113 | 1.0383662 | 0.30364354 |
| 2023 | B0-RMEAN | 9.2996729e-05 | 0.0064594275 | 0.0092524379 | 0.0096741235 | 0.00042168557 | 1.0455756 | 0.3034832 |
| 2023 | B0-RMED | 0.00010117992 | 0.0060310446 | 0.0092524379 | 0.0065814601 | -0.0026709779 | 0.71132172 | 0.29968513 |
| 2024 | C3-IO-SMEAR | 0.00011265323 | 0.0063823356 | 0.0092491933 | 0.0095956812 | 0.00034648786 | 1.0374614 | 0.3102724 |
| 2024 | C1a | 0.0001135108 | 0.0063801416 | 0.0092491933 | 0.0094768388 | 0.00022764548 | 1.0246125 | 0.3102724 |
| 2024 | M1 | 0.00011329232 | 0.00651156 | 0.0092491933 | 0.0099979316 | 0.00074873831 | 1.0809517 | 0.3102724 |
| 2024 | C0 | 0.00011892159 | 0.0060056223 | 0.0092491933 | 0.0071960535 | -0.0020531398 | 0.77801958 | 0.3102724 |
| 2024 | O1 | 0.00011259695 | 0.006265697 | 0.0092491933 | 0.0091198538 | -0.0001293395 | 0.98601613 | 0.31181296 |
| 2024 | B0-VOL | 0.00011578065 | 0.0066372528 | 0.0092491933 | 0.0098591363 | 0.00060994296 | 1.0659455 | 0.29063745 |
| 2024 | B0-CLOCK | 0.00011474675 | 0.0065242191 | 0.0092491933 | 0.0097328363 | 0.00048364298 | 1.0522903 | 0.29931135 |
| 2024 | B0-RMEAN | 0.00012124512 | 0.0067770511 | 0.0092491933 | 0.0096948401 | 0.00044564684 | 1.0481822 | 0.29475541 |
| 2024 | B0-RMED | 0.00012941663 | 0.0062474444 | 0.0092491933 | 0.0066391174 | -0.0026100759 | 0.71780502 | 0.29135808 |
| EQ | C3-IO-SMEAR | 0.00010722694 | 0.0068010295 | 0.01031327 | 0.010588584 | 0.00027531389 | 1.0266951 | 0.3246681 |
| EQ | C1a | 0.00010821865 | 0.0068159348 | 0.01031327 | 0.01050088 | 0.00018760952 | 1.0181911 | 0.3246681 |
| EQ | M1 | 0.0001082664 | 0.0068839895 | 0.01031327 | 0.010855766 | 0.00054249545 | 1.0526017 | 0.3246681 |
| EQ | C0 | 0.00011478357 | 0.0064974483 | 0.01031327 | 0.0080327552 | -0.0022805153 | 0.77887564 | 0.3246681 |
| EQ | O1 | 0.00010857813 | 0.0067282128 | 0.01031327 | 0.010041315 | -0.00027195542 | 0.97363054 | 0.31955938 |
| EQ | B0-VOL | 0.00011156042 | 0.0070127696 | 0.01031327 | 0.010600902 | 0.00028763119 | 1.0278894 | 0.30414316 |
| EQ | B0-CLOCK | 0.00011466954 | 0.0068390848 | 0.01031327 | 0.0095054397 | -0.00080783078 | 0.92167075 | 0.3028002 |
| EQ | B0-RMEAN | 0.00012236442 | 0.0071296126 | 0.01031327 | 0.0095165809 | -0.00079668959 | 0.92275102 | 0.30023827 |
| EQ | B0-RMED | 0.00013809216 | 0.006949601 | 0.01031327 | 0.006474016 | -0.0038392545 | 0.62773647 | 0.29611443 |

Means/MAE/bias are raw absolute log-return units; MSE is squared log-return units. Annual weights: equal20 stocks/origin → equal eligible origins/session → equal sessions/year. EQ averages four annual metrics; EQ ratio is the ratio of equal-year means. Other B0 arms remain included; B0-RMED targets a median and is chiefly an MAE comparator. All eight existing comparator forecasts are read unchanged, never refitted.

Paired C3-minus-calibrated raw MSE (negative favors C3):

| year | C3_minus_C1a_mean | C3_minus_C1a_low | C3_minus_C1a_high | C3_minus_C1a_percent | C3_minus_M1_mean | C3_minus_M1_low | C3_minus_M1_high | C3_minus_M1_percent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | -9.8250756e-07 | -1.6781291e-06 | -5.0697009e-07 | -1.1654456 | -4.7001247e-07 | -1.1212388e-06 | 9.4095284e-08 | -0.56093652 |
| 2022 | -1.5493448e-06 | -2.1888031e-06 | -8.03746e-07 | -1.0452654 | -2.7042015e-06 | -3.7775805e-06 | -1.7299367e-06 | -1.8102851 |
| 2023 | -5.7741687e-07 | -8.2773592e-07 | -3.444498e-07 | -0.6649539 | -3.445238e-07 | -5.8766808e-07 | -6.4318167e-08 | -0.39782094 |
| 2024 | -8.5757445e-07 | -1.3240406e-06 | -4.6524749e-07 | -0.75550028 | -6.3909045e-07 | -1.0293592e-06 | -2.5711532e-07 | -0.56410747 |
| EQ | -9.9171091e-07 | -1.251371e-06 | -7.3185663e-07 | -0.91639554 | -1.0394571e-06 | -1.3628274e-06 | -7.2316843e-07 | -0.96009203 |

400 whole-calendar-month bootstrap draws, seed22042, using executed annual routine and year-stratified equal-year routine. Full sessions/stocks/overlapping origins remain together. Bounds are descriptive95% intervals conditional on these fitted encoders/factors; they do not refit calibration tails or adjust for model/hypothesis/κ selection after repeated research. No IID stock-row or four-year significance claim.

## Clocks, tails and ordinary periods

Equal-year intraday raw MSE changes −2.7478% versus C1a and −4.6788% versus M1; overnight changes −0.4197% and +0.0714%, respectively. All four years improve intraday MSE versus both controls. Intraday forecast/realized ratio falls from C1a 1.16774 to C3 1.06510; overnight rises from 0.94785 to 1.00887. Overnight MAE nevertheless rises from C1a 0.00804019 to 0.00819675.

The 15:30 ratio remains 0.91902; MSE is −1.5074% versus C1a but +0.0220% versus M1. C3 slightly worsens the 12:30/13:30/14:30 equal-year MSE versus C1a. A two-category correction does not remove all clock variation.

Prefix95 events account for 57.7783% of C3 loss, with forecast/realized ratio only 0.36408; prefix99 events account for 32.8178%, ratio 0.23635. Event MSE improves versus C1a (−2.8590% / −2.1166%) but worsens versus M1 (+2.1739% / +1.5321%). The prefix95 complement has ratio 1.24742 and MSE +2.4411% versus C1a, +16.1342% versus C0, −6.2430% versus M1. Thus C3 reallocates level correction across clocks, rather than discovering jumps or solving the ordinary-versus-tail trade-off. Outcome-selected tail amplitudes are descriptive and do not by themselves identify conditional-mean model bias.

| field | group | rows | sessions | raw_MSE | raw_MAE | observed | predicted | ratio | weight_mass | raw_MSE_loss_share | percent_MSE_vs_C1a | percent_MSE_vs_M1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| category | OVERNIGHT | 45460 | 771 | 0.00015006219 | 0.0081967497 | 0.012430622 | 0.012540867 | 1.0088688 | 0.56501361 | 0.79096457 | -0.41967498 | 0.071381631 |
| category | INTRADAY | 34800 | 757 | 5.1382745e-05 | 0.0049946708 | 0.0075759099 | 0.0080690821 | 1.0650974 | 0.43498639 | 0.20903543 | -2.7477923 | -4.6788095 |
| slot | 15:30 | 11500 | 575 | 0.00016568682 | 0.0083426259 | 0.013016966 | 0.011962834 | 0.91901863 | 0.14948643 | 0.22998056 | -1.5074147 | 0.022004469 |
| slot | 10:30 | 12200 | 610 | 4.3160707e-05 | 0.0047153549 | 0.0072290401 | 0.0077418038 | 1.0709311 | 0.15232523 | 0.061037839 | -3.3347998 | -4.8384995 |
| slot | 11:30 | 12920 | 646 | 3.5679162e-05 | 0.0042170967 | 0.0061621815 | 0.006812176 | 1.1054812 | 0.16814413 | 0.055848974 | -4.5693069 | -6.2313452 |
| slot | 14:30 | 10940 | 547 | 0.00014500067 | 0.008347103 | 0.012666227 | 0.013258983 | 1.0467981 | 0.13023273 | 0.17643494 | 0.047917769 | 0.13782612 |
| slot | 09:30 | 9900 | 495 | 8.5686661e-05 | 0.006535592 | 0.010148502 | 0.010284745 | 1.0134249 | 0.11960313 | 0.096789453 | -1.2394127 | -3.4161338 |
| slot | 12:30 | 12000 | 600 | 0.00013438596 | 0.0077700103 | 0.011562181 | 0.012106274 | 1.0470579 | 0.15436347 | 0.19351378 | 0.15650259 | 0.039171596 |
| slot | 13:30 | 10800 | 540 | 0.0001581792 | 0.0084177689 | 0.012572072 | 0.013145035 | 1.0455743 | 0.12584488 | 0.18639445 | 0.0050479263 | 0.2071866 |
| tail | PREFIX95 | 5176 | 692 | 0.0011282416 | 0.028323945 | 0.044512429 | 0.016206184 | 0.36408222 | 0.059318601 | 0.57778267 | -2.8589637 | 2.1738978 |
| tail | LE_PREFIX95 | 75084 | 793 | 4.8400551e-05 | 0.0055254622 | 0.008196338 | 0.010224269 | 1.2474192 | 0.9406814 | 0.42221733 | 2.4411008 | -6.2430432 |
| tail | PREFIX99 | 841 | 257 | 0.0039155094 | 0.05794399 | 0.075877916 | 0.017933926 | 0.23635238 | 0.009373201 | 0.32817818 | -2.1166127 | 1.5321353 |
| tail | LE_PREFIX99 | 79419 | 793 | 7.2784097e-05 | 0.0063329367 | 0.0096994324 | 0.010513953 | 1.0839761 | 0.9906268 | 0.67182182 | -0.15992279 | -2.5217273 |

All annual clocks/categories, prefix95/99 cohorts and complements are in groups.csv. Thresholds are the saved September-prefix weighted raw-A quantiles, never OOS-fitted. Conditional errors normalize original group weight within year, then average years. Event loss shares average unconditional annual contributions divided by equal-year total MSE; no equal-row pooling or independent-strata claim. These are retrospective outcome cohorts, not a fitted event detector; even an ideal conditional mean can underpredict a cohort selected on large realized outcomes.

## Ranking and reliability

| year | arm | magnitude_IC | pair_concordance | top4 | bottom4 | tie_rate | constant_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | C3-IO-SMEAR | 0.31785841 | 0.61520032 | 0.3866483 | 0.31024569 | 0 | 0 |
| 2022 | C3-IO-SMEAR | 0.35029686 | 0.62723692 | 0.43397959 | 0.32302721 | 0 | 0 |
| 2023 | C3-IO-SMEAR | 0.32024473 | 0.61514505 | 0.41768844 | 0.29774001 | 0 | 0 |
| 2024 | C3-IO-SMEAR | 0.3102724 | 0.61162619 | 0.46012191 | 0.26560783 | 0 | 0 |
| EQ | C3-IO-SMEAR | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| EQ | C1a | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| EQ | M1 | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| EQ | C0 | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| EQ | O1 | 0.31955938 | 0.6152466 | 0.4217638 | 0.29875048 | 0 | 0 |
| EQ | B0-VOL | 0.30414316 | 0.6094227 | 0.40988649 | 0.29618868 | 0.00026150811 | 0 |
| EQ | B0-CLOCK | 0.3028002 | 0.60852865 | 0.38668138 | 0.30584502 | 0 | 0 |
| EQ | B0-RMEAN | 0.30023827 | 0.60754095 | 0.39069215 | 0.30584502 | 0 | 0 |
| EQ | B0-RMED | 0.29611443 | 0.60612527 | 0.37416629 | 0.30584502 | 0 | 0 |

| year | rank_vectors_identical | clamp_rows |
| --- | --- | --- |
| 2021 | True | 0 |
| 2022 | True | 0 |
| 2023 | True | 0 |
| 2024 | True | 0 |

Every stock at an origin shares the same positive category factor and scale. With no clamp-induced ties, the decoder is strictly increasing, so within-origin ranks must remain identical. This is calibration, not new rank/jump information. Spearman uses average ranks; pair concordance gives score ties half credit and excludes actual ties (chance0.5). Top/bottom4 uses fractional boundary-tie membership (chance0.2). Any clamp/tie exception is disclosed above.

| group | observed | predicted | ratio | raw_MSE | raw_MAE |
| --- | --- | --- | --- | --- | --- |
| 1 | 0.0042863489 | 0.0048022319 | 1.1203549 | 1.5441168e-05 | 0.0029049725 |
| 2 | 0.0056328831 | 0.0063048421 | 1.1192922 | 2.5769372e-05 | 0.0038403123 |
| 3 | 0.00680728 | 0.0074095293 | 1.0884714 | 3.932458e-05 | 0.0046168458 |
| 4 | 0.0077347889 | 0.0084069419 | 1.0869 | 5.8149425e-05 | 0.0053434618 |
| 5 | 0.0086473296 | 0.0093976502 | 1.0867691 | 6.6697576e-05 | 0.0058571511 |
| 6 | 0.0097795526 | 0.010394231 | 1.0628534 | 7.9142576e-05 | 0.0065387269 |
| 7 | 0.011137962 | 0.011469022 | 1.0297236 | 0.00011555069 | 0.0074561216 |
| 8 | 0.012866212 | 0.01273629 | 0.98990201 | 0.00014014745 | 0.0084141701 |
| 9 | 0.014977084 | 0.01475389 | 0.98509759 | 0.00019597883 | 0.009745236 |
| 10 | 0.021268165 | 0.020215554 | 0.95050768 | 0.0003361583 | 0.013296274 |

Reliability bins are ten predeclared weighted empirical C0-score deciles per year, shared across arms. Numeric ranges/counts/session coverage are in groups.csv. Boundaries are descriptive historical bins, not future calibration thresholds. EQ bins average corresponding annual percentile groups.

## Scientific decision and limits

**Retain C3 only as a provisional exploratory raw-mean benchmark; retain C1a/M1 as simpler benchmarks and close this Stage 1 execution.** Its consistent annual MSE direction and better intraday balance support the narrow hypothesis that known calendar categories help calibration. The gain is small, pooled mean calibration is slightly worse than C1a, and ordinary-period MSE versus C1a deteriorates in all years. The researcher must decide whether that cost is acceptable; the report does not approve deployment or another fit. No κ or boundary tuning is justified by this screen.

Within-origin rank vectors are exactly identical in all four years, with zero C3 clamp rows. Hence magnitude IC, retrieval and concordance are inherited from C0; there is no evidence here of new causal jump discrimination. Calibration-tail effective sessions are 30.69–53.01; F24 is least precise. Its overnight maximum q is 10.8983, top10 weighted contribution 5.6383%, top1% contribution 8.2870%; all moments are finite, no trimming or instability rescue occurred. Shrinkage weights range 0.5511–0.6795. The descriptive OOS bootstrap does not propagate calibration-factor estimation uncertainty.

Existing overnight-crossing endpoints are not a separate close-to-open jump target, integrated variance, option valuation or executable post-issuance returns. No Stage 2 or trading experiment follows automatically.

Calendar reconciliation: nine calibration origins and eleven OOS origins are morning-slot exceptions to the regular-session shorthand, all already saved as OVERNIGHT with next-session endpoints on scheduled early-close dates. The prompt gives executed categories/endpoint keys priority; these are preserved, not relabelled. No observations were removed.

| year | role | origins | dates |
| --- | --- | --- | --- |
| 2021 | calibration | 4 | 2020-11-27, 2020-12-24 |
| 2021 | oos | 3 | 2021-11-26 |
| 2022 | calibration | 3 | 2021-11-26 |
| 2022 | oos | 2 | 2022-11-25 |
| 2023 | calibration | 2 | 2022-11-25 |
| 2023 | oos | 2 | 2023-07-03 |
| 2024 | oos | 4 | 2024-07-03, 2024-12-24 |

## Reproduction, preservation and stop

`.venv/bin/python -m lstm_data.hf20_mag_c3_io --out reports/experiments/hf20_s9_mag_stage1_session4_c3_io_2026-10-28 --preflight` performs saved-artifact checks; initial `--run` computes only this C3 arm once. `--report` reuses frozen coefficient CSV, never refits, and replays the saved-score tables. The coefficient file is single-use/exclusive; no C3 score Parquet or historical predictor copy is needed because old Mhat plus fixed coefficients reproduces the vector.

Sources: Session2 F21 parent and Session2B F22–F24 roots listed in protocol.json; each calibration_scores.parquet/oos_scores.parquet, restricted_target.json, restricted_recipe.json, coefficients.json and result.json. O1 scores remain under Session3/Fxx/oos_scores.parquet. Saved S4 eligibility metadata, original S9 keys and Session3 role_indices.npz verify identity. No raw/minute/hourly feature observations, checkpoint, training runner or source rebuild is used.

New files only: protocol.json, calibration_coefficients.csv, metrics.csv, groups.csv, verification.json, interpretation.json, this report, one module and focused fixtures, plus the usual reports/codex_sessions handoff. The neural registry/journal and all previous assets remain unchanged at138/200. No2025/2026 numerical access/hash, data download, dashboard edit, strategy or extra fitting arm.

Verification: five focused tests pass (2.72s); Ruff and `git diff --check` pass. Full repository Pylance-parity basic check: **506 files, zero errors, zero warnings** (63.504s). Exact commands: `.venv/bin/python -m pytest tests/test_hf20_mag_c3_io.py -q`; `.venv/bin/ruff check src/lstm_data/hf20_mag_c3_io.py tests/test_hf20_mag_c3_io.py --output-format concise`; `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist`. Select repository `.venv/bin/python`, retain Pylance basic and refresh editor Problems; actual editor refresh remains human-confirmed. Two initial type diagnostics in exception-record key construction were corrected without changing numerical formulas or data. Frozen protocol/coefficients and both numerical CSVs replay byte-identically. All14 explicitly bound previous score/ledger/registry files remain byte-identical. No previous file is written. Branch `feat/track-a-data-intake`, SHA `5f7bb86a35d5aaff34ff79ef8f471117de6d3e42`, fetched0/0 upstream; prior dirty work preserved, no commit/push. Exact saved metadata root: `reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation/opening_reaudit_v2/S4_ORIGIN_SOURCE_ELIGIBILITY.parquet`; original S9 references: `reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation/HF20-S9-Fxx-H4-MAG-S42/oos_scores.parquet`. Session handoff: `reports/codex_sessions/2026-10-28_085747_hf20_s9_mag_session4_c3_io.md`.

STOP for researcher review. No Stage2 target/model, additional calibration/objective, event head, trading threshold, options/backtest or protected confirmation.
