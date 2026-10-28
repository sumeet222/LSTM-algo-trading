# S2-C C-A masked signed decomposition-assisted four-hour MAG

**Status: COMPLETE — 4/4 folds.** Exploratory/post-search. Verdict: **PRIMARY_MSE_WIN_TRADEOFF_REVIEW_REQUIRED**.

**Complete: four valid folds; a marginal, mixed exploratory gain.** Calibrated C-A raw MSE is **0.000106548167844**, **0.1104% below CLOCK-C3** (0.000106665945886) and **0.6330% below C3** (0.000107226942123). Annual changes versus CLOCK-C3 are **+0.02565%, −0.09906%, −0.02881%, −0.28826%**; F21 loses and only F24 has an annual paired interval excluding zero. Equal-year delta is −1.17778e−7, descriptive month-block95% interval [−2.29973e−7, −5.11120e−9], barely below zero. The interval is conditional on selected fits/calibrators and repeatedly searched history, not independent confirmation.

Full MAE is effectively unchanged (−0.01476%); magnitude IC increases slightly **0.330254→0.331236**. Mean calibration is slightly worse (ratio1.01376→1.01522). Conditional overnight MSE improves0.1455%, while intraday MSE/MAE worsen0.0277%/0.1127%. Prefix95/99 tail MSE improves0.3560%/0.2462% versus CLOCK-C3, but the95 complement worsens0.4136%; against older C3 the tails still worsen0.6636%/0.4903%. This is a small tail/overnight trade-off, not uniform improvement.

Four charged pairs/eight phases completed without failures or retries, ledger **158→162/300**. All original80260 rows/4013 origins/793 sessions remain. Selected epochs8/13/22/17; actual160 epochs,24885 updates,304 clipped batches; peakRSS846200832 bytes. No S2-D, extra model/calibration choice, deferred route,2025 research or protected2026 access.

## Frozen design and primary cohort

Same20-name panel,48 completed scheduled-hour FT16×16 own-stock inputs, one-layerH32, final hidden dropout.10,10 fixed S2-B clock values and identical primary head initialization. Three signed linear aux rows add129 parameters:6572 total. Head outputs u represent Rhat=s*u. No future labels or availability flag enters inputs. Main loss remains complete-panel transformed M MSE; selector monitors only it. Aux objective is .10 times mean of the three global normalized masked signed squared risks. Complete triples only; no imputation, C-B, absolute-component addition or gap-task reinterpretation.

Initial/selector/September-refit/Oct–Dec/annual-OOS roles are exactly Design A; own independently fitted legal prefix FT16 recipe/weighted-left-median scale matches all8 S2-B recipes/scales. Seed42 AdamW lr.001 beta(.9,.999)eps1e-8, matrix decay.01 bias0, norm clip1,16 complete sessions, seeded shuffle42+epoch. Fresh optimizer/refit at qualified epoch; main .999 best rule,min12,patience10,max60. Batch aux weight is phase-global masked overnight hierarchy times S_phase/B_batch; no minibatch denominator or missing-stock redistribution. Empty aux batch gives zero gradient. Calibrated primary uses own independent tail C3 IO kappa25; raw diagnostic is not an OOS-selected alternative.

Original OOS population80260 stock-origin rows/4013 origins/793 sessions,20 per origin. Primary target starts at nominal origin before approximately+2min issuance; it is price-only, not verified executable returns. All2021–24 history is repeatedly inspected. No2025 market/2026 protected access, minute rebuild/download, options/backtest, S2-D or deferred route.

## Fit and source receipts

| year | status | run_id | parameters | selected_epoch | selector_epochs | raw_minimum_epoch | initial_scale | scale | initial_sha256 | frozen_parameter_sha256 | reload_max_error | optimizer_fresh | seconds | peak_rss_bytes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | COMPLETED | HF20-S2C-CA-F21-S42 | 6572 | 8 | 18 | 8 | 0.0057971177 | 0.0058487592 | 6a344d4ac1e7fe68aada23a2ee93b9074f827fd9e5d77fe246f40a37d9d11362 | e3e5a50fa50706d70c4e2fb1d01442e3458ee994ffcaabba2f359417b4e2bcfa | 0 | True | 548.9249 | 846200832 |
| 2022 | COMPLETED | HF20-S2C-CA-F22-S42 | 6572 | 13 | 23 | 13 | 0.0059351246 | 0.0059334067 | 6a344d4ac1e7fe68aada23a2ee93b9074f827fd9e5d77fe246f40a37d9d11362 | 19ad7789748a03a71108bfa0d22fc4722c8ec34aba9e6a0b10f2250cc437388e | 0 | True | 897.51266 | 846200832 |
| 2023 | COMPLETED | HF20-S2C-CA-F23-S42 | 6572 | 22 | 32 | 22 | 0.0060723344 | 0.0061216731 | 6a344d4ac1e7fe68aada23a2ee93b9074f827fd9e5d77fe246f40a37d9d11362 | 6eea95d9810bf0d4c70f4c9f8e5a190a12ed647d46e4961cfc26c21a439aa529 | 0 | True | 1478.198 | 846200832 |
| 2024 | COMPLETED | HF20-S2C-CA-F24-S42 | 6572 | 17 | 27 | 23 | 0.0061734035 | 0.0061744472 | 6a344d4ac1e7fe68aada23a2ee93b9074f827fd9e5d77fe246f40a37d9d11362 | 3d325314f95083b81753b86e50b2c725f31320e457ae4051dde689ba33e4c064 | 0 | True | 1153.9188 | 846200832 |

| year | role | sessions | origins | rows | aux_phase_sessions | aux_overnight_sessions | aux_overnight_origins | aux_supported_cells | aux_global_masked_base_mass | aux_normalized_aux_mass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | inner_train | 2100 | 11449 | 228980 | 2100 | 2065 | 6474 | 128566 | 0.99237288 | 1 |
| 2021 | selector | 57 | 349 | 6980 | nan | nan | nan | 3890 | nan | nan |
| 2021 | restricted_refit | 2164 | 11846 | 236920 | 2164 | 2129 | 6697 | 133012 | 0.99250822 | 1 |
| 2021 | calibration | 56 | 283 | 5660 | nan | nan | nan | 3256 | nan | nan |
| 2021 | oos | 188 | 955 | 19100 | nan | nan | nan | 10465 | nan | nan |
| 2022 | inner_train | 2301 | 12560 | 251200 | 2301 | 2265 | 7103 | 141061 | 0.99240618 | 1 |
| 2022 | selector | 58 | 278 | 5560 | nan | nan | nan | 2901 | nan | nan |
| 2022 | restricted_refit | 2366 | 12888 | 257760 | 2366 | 2329 | 7286 | 144561 | 0.99136969 | 1 |
| 2022 | calibration | 50 | 245 | 4900 | nan | nan | nan | 2729 | nan | nan |
| 2022 | oos | 210 | 1180 | 23600 | nan | nan | nan | 13167 | nan | nan |
| 2023 | inner_train | 2526 | 13776 | 275520 | 2526 | 2485 | 7793 | 154640 | 0.9915493 | 1 |
| 2023 | selector | 59 | 313 | 6260 | nan | nan | nan | 3477 | nan | nan |
| 2023 | restricted_refit | 2592 | 14137 | 282740 | 2592 | 2550 | 7998 | 158667 | 0.99119608 | 1 |
| 2023 | calibration | 48 | 258 | 5160 | nan | nan | nan | 2763 | nan | nan |
| 2023 | oos | 187 | 887 | 17740 | nan | nan | nan | 9978 | nan | nan |
| 2024 | inner_train | 2719 | 14824 | 296480 | 2719 | 2676 | 8380 | 166238 | 0.99119955 | 1 |
| 2024 | selector | 69 | 291 | 5820 | nan | nan | nan | 3291 | nan | nan |
| 2024 | restricted_refit | 2795 | 15167 | 303340 | 2795 | 2750 | 8578 | 170146 | 0.99112727 | 1 |
| 2024 | calibration | 40 | 163 | 3260 | nan | nan | nan | 1782 | nan | nan |
| 2024 | oos | 208 | 991 | 19820 | nan | nan | nan | 11251 | nan | nan |

Supported source prices were checked positive/finite using only saved genuine adjusted quarantine-filtered entry/exit/last-minute close/next09:30 open. Signed identity atol1e-12 rtol1e-11, actual maximum 4.2500725161431774e-16. One-closure calendar geometry and COP action basis verified. No primary key deleted; no all20 aux gate. Source concentration in MS/MRK and historical MA remains; original audit stock/month/slot marginals are referenced rather than copied, and masks are identical to audit counts. No MCAR assumption. Labels mature before each legal phase cutoff and remain outside features. All previous source/control artifacts preserve their bound hashes.

## Primary annual and equal-year comparisons

| year | arm | raw_MSE | raw_MAE | observed | predicted | bias | ratio | magnitude_IC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | S2C-C3 | 8.2575787e-05 | 0.0063847103 | 0.0098002675 | 0.0102434 | 0.00044313262 | 1.0452164 | 0.32746071 |
| 2021 | S2C-RAW | 9.0822602e-05 | 0.0060839333 | 0.0098002675 | 0.0073540942 | -0.0024461733 | 0.75039729 | 0.32746071 |
| 2021 | CLOCK-C3 | 8.2554613e-05 | 0.0063781675 | 0.0098002675 | 0.010211883 | 0.00041161566 | 1.0420005 | 0.32627607 |
| 2021 | CLOCK-RAW | 9.0561076e-05 | 0.0060824636 | 0.0098002675 | 0.0074034373 | -0.0023968303 | 0.75543216 | 0.32627607 |
| 2021 | C3 | 8.3320658e-05 | 0.006421753 | 0.0098002675 | 0.010306108 | 0.00050584098 | 1.051615 | 0.31785841 |
| 2021 | M1 | 8.3790671e-05 | 0.0063963177 | 0.0098002675 | 0.010205226 | 0.00040495892 | 1.0413212 | 0.31785841 |
| 2021 | C1a | 8.4303166e-05 | 0.0064637727 | 0.0098002675 | 0.010290148 | 0.00048988031 | 1.0499864 | 0.31785841 |
| 2021 | C0 | 9.0541114e-05 | 0.0061042972 | 0.0098002675 | 0.0075378642 | -0.0022624033 | 0.76914882 | 0.31785841 |
| 2021 | B0-VOL | 8.6535921e-05 | 0.0066089924 | 0.0098002675 | 0.010256419 | 0.00045615162 | 1.0465448 | 0.31183632 |
| 2021 | B0-CLOCK | 8.8733837e-05 | 0.0064413665 | 0.0098002675 | 0.0093055751 | -0.00049469243 | 0.94952256 | 0.29038533 |
| 2021 | B0-RMEAN | 9.6342162e-05 | 0.0067870981 | 0.0098002675 | 0.0093076165 | -0.00049265105 | 0.94973086 | 0.289525 |
| 2021 | B0-RMED | 0.00010897265 | 0.006576386 | 0.0098002675 | 0.0062980819 | -0.0035021856 | 0.64264387 | 0.28093515 |
| 2021 | O1 | 8.5271069e-05 | 0.0062557455 | 0.0098002675 | 0.0091671809 | -0.00063308666 | 0.93540108 | 0.3137893 |
| 2022 | S2C-C3 | 0.00014576497 | 0.0083145016 | 0.012951183 | 0.012995212 | 4.4029223e-05 | 1.0033996 | 0.3517645 |
| 2022 | S2C-RAW | 0.00015811435 | 0.0080541699 | 0.012951183 | 0.0099502131 | -0.0030009701 | 0.76828603 | 0.3517645 |
| 2022 | CLOCK-C3 | 0.00014590951 | 0.0083086676 | 0.012951183 | 0.012936514 | -1.4668811e-05 | 0.99886738 | 0.35445091 |
| 2022 | CLOCK-RAW | 0.0001591903 | 0.0080603043 | 0.012951183 | 0.0098267996 | -0.0031243837 | 0.75875689 | 0.35445091 |
| 2022 | C3 | 0.00014667567 | 0.0083746314 | 0.012951183 | 0.013237313 | 0.00028613009 | 1.022093 | 0.35029686 |
| 2022 | M1 | 0.00014937987 | 0.0086367779 | 0.012951183 | 0.014210493 | 0.0012593093 | 1.0972351 | 0.35029686 |
| 2022 | C1a | 0.00014822502 | 0.008390051 | 0.012951183 | 0.013099666 | 0.00014848261 | 1.0114648 | 0.35029686 |
| 2022 | C0 | 0.00015850978 | 0.0080691855 | 0.012951183 | 0.010049479 | -0.0029017043 | 0.77595064 | 0.35029686 |
| 2022 | B0-VOL | 0.00015369642 | 0.0084733784 | 0.012951183 | 0.012531746 | -0.00041943677 | 0.96761402 | 0.32314717 |
| 2022 | B0-CLOCK | 0.00016861834 | 0.0082521988 | 0.012951183 | 0.0093759284 | -0.0035752548 | 0.72394377 | 0.3178606 |
| 2022 | B0-RMEAN | 0.00017887366 | 0.0084948737 | 0.012951183 | 0.0093897435 | -0.0035614397 | 0.72501047 | 0.31318948 |
| 2022 | B0-RMED | 0.00021279945 | 0.0089435291 | 0.012951183 | 0.0063774046 | -0.0065737787 | 0.49241868 | 0.31247937 |
| 2022 | O1 | 0.00014938804 | 0.0083570315 | 0.012951183 | 0.012775428 | -0.00017575533 | 0.9864294 | 0.34362343 |
| 2023 | S2C-C3 | 8.6148245e-05 | 0.0059815765 | 0.0092524379 | 0.0090553581 | -0.00019707979 | 0.97869969 | 0.32630073 |
| 2023 | S2C-RAW | 9.0616623e-05 | 0.0057907704 | 0.0092524379 | 0.007374455 | -0.0018779829 | 0.79702831 | 0.32630073 |
| 2023 | CLOCK-C3 | 8.6173073e-05 | 0.0059986859 | 0.0092524379 | 0.0091179546 | -0.00013448331 | 0.9854651 | 0.32380415 |
| 2023 | CLOCK-RAW | 9.1029308e-05 | 0.005794158 | 0.0092524379 | 0.0072747552 | -0.0019776827 | 0.78625279 | 0.32380415 |
| 2023 | C3 | 8.6258208e-05 | 0.0060253978 | 0.0092524379 | 0.0092152346 | -3.7203377e-05 | 0.99597907 | 0.32024473 |
| 2023 | M1 | 8.6602732e-05 | 0.0059913023 | 0.0092524379 | 0.0090094132 | -0.00024302474 | 0.97373398 | 0.32024473 |
| 2023 | C1a | 8.6835625e-05 | 0.0060297739 | 0.0092524379 | 0.0091368676 | -0.00011557032 | 0.9875092 | 0.32024473 |
| 2023 | C0 | 9.1161785e-05 | 0.0058106884 | 0.0092524379 | 0.0073476242 | -0.0019048138 | 0.79412845 | 0.32024473 |
| 2023 | B0-VOL | 9.0228688e-05 | 0.0063314547 | 0.0092524379 | 0.0097563049 | 0.00050386696 | 1.0544578 | 0.2909517 |
| 2023 | B0-CLOCK | 8.6579247e-05 | 0.0061385546 | 0.0092524379 | 0.0096074191 | 0.00035498113 | 1.0383662 | 0.30364354 |
| 2023 | B0-RMEAN | 9.2996729e-05 | 0.0064594275 | 0.0092524379 | 0.0096741235 | 0.00042168557 | 1.0455756 | 0.3034832 |
| 2023 | B0-RMED | 0.00010117992 | 0.0060310446 | 0.0092524379 | 0.0065814601 | -0.0026709779 | 0.71132172 | 0.29968513 |
| 2023 | O1 | 8.7056455e-05 | 0.0060343771 | 0.0092524379 | 0.0091027977 | -0.00014964019 | 0.98382694 | 0.30901184 |
| 2024 | S2C-C3 | 0.00011170367 | 0.0063435957 | 0.0092491933 | 0.0095870175 | 0.00033782424 | 1.0365247 | 0.31941796 |
| 2024 | S2C-RAW | 0.00011638445 | 0.0059692089 | 0.0092491933 | 0.0074297353 | -0.001819458 | 0.80328468 | 0.31941796 |
| 2024 | CLOCK-C3 | 0.00011202659 | 0.0063428514 | 0.0092491933 | 0.0095544881 | 0.00030529483 | 1.0330077 | 0.31648505 |
| 2024 | CLOCK-RAW | 0.00011630047 | 0.0059863549 | 0.0092491933 | 0.0075584134 | -0.0016907799 | 0.81719704 | 0.31648505 |
| 2024 | C3 | 0.00011265323 | 0.0063823356 | 0.0092491933 | 0.0095956812 | 0.00034648786 | 1.0374614 | 0.3102724 |
| 2024 | M1 | 0.00011329232 | 0.00651156 | 0.0092491933 | 0.0099979316 | 0.00074873831 | 1.0809517 | 0.3102724 |
| 2024 | C1a | 0.0001135108 | 0.0063801416 | 0.0092491933 | 0.0094768388 | 0.00022764548 | 1.0246125 | 0.3102724 |
| 2024 | C0 | 0.00011892159 | 0.0060056223 | 0.0092491933 | 0.0071960535 | -0.0020531398 | 0.77801958 | 0.3102724 |
| 2024 | B0-VOL | 0.00011578065 | 0.0066372528 | 0.0092491933 | 0.0098591363 | 0.00060994296 | 1.0659455 | 0.29063745 |
| 2024 | B0-CLOCK | 0.00011474675 | 0.0065242191 | 0.0092491933 | 0.0097328363 | 0.00048364298 | 1.0522903 | 0.29931135 |
| 2024 | B0-RMEAN | 0.00012124512 | 0.0067770511 | 0.0092491933 | 0.0096948401 | 0.00044564684 | 1.0481822 | 0.29475541 |
| 2024 | B0-RMED | 0.00012941663 | 0.0062474444 | 0.0092491933 | 0.0066391174 | -0.0026100759 | 0.71780502 | 0.29135808 |
| 2024 | O1 | 0.00011259695 | 0.006265697 | 0.0092491933 | 0.0091198538 | -0.0001293395 | 0.98601613 | 0.31181296 |
| EQ | S2C-C3 | 0.00010654817 | 0.006756096 | 0.01031327 | 0.010470247 | 0.00015697657 | 1.0152208 | 0.33123598 |
| EQ | S2C-RAW | 0.00011398451 | 0.0064745206 | 0.01031327 | 0.0080271244 | -0.0022861461 | 0.77832967 | 0.33123598 |
| EQ | CLOCK-C3 | 0.00010666595 | 0.0067570931 | 0.01031327 | 0.01045521 | 0.00014193959 | 1.0137628 | 0.33025404 |
| EQ | CLOCK-RAW | 0.00011427029 | 0.0064808202 | 0.01031327 | 0.0080158513 | -0.0022974191 | 0.77723661 | 0.33025404 |
| EQ | C3 | 0.00010722694 | 0.0068010295 | 0.01031327 | 0.010588584 | 0.00027531389 | 1.0266951 | 0.3246681 |
| EQ | M1 | 0.0001082664 | 0.0068839895 | 0.01031327 | 0.010855766 | 0.00054249545 | 1.0526017 | 0.3246681 |
| EQ | C1a | 0.00010821865 | 0.0068159348 | 0.01031327 | 0.01050088 | 0.00018760952 | 1.0181911 | 0.3246681 |
| EQ | C0 | 0.00011478357 | 0.0064974483 | 0.01031327 | 0.0080327552 | -0.0022805153 | 0.77887564 | 0.3246681 |
| EQ | B0-VOL | 0.00011156042 | 0.0070127696 | 0.01031327 | 0.010600902 | 0.00028763119 | 1.0278894 | 0.30414316 |
| EQ | B0-CLOCK | 0.00011466954 | 0.0068390848 | 0.01031327 | 0.0095054397 | -0.00080783078 | 0.92167075 | 0.3028002 |
| EQ | B0-RMEAN | 0.00012236442 | 0.0071296126 | 0.01031327 | 0.0095165809 | -0.00079668959 | 0.92275102 | 0.30023827 |
| EQ | B0-RMED | 0.00013809216 | 0.006949601 | 0.01031327 | 0.006474016 | -0.0038392545 | 0.62773647 | 0.29611443 |
| EQ | O1 | 0.00010857813 | 0.0067282128 | 0.01031327 | 0.010041315 | -0.00027195542 | 0.97363054 | 0.31955938 |

Raw errors/means in absolute log-return units; MSE in squared units. Equal-stock/origin/session/year hierarchy, arithmetic equal-year scores, ratio of equal-year means. Four years are not seeds.

## Paired whole-calendar-month descriptive uncertainty

| scope | reference | year | delta | low | high | percent_change | interval_includes_zero |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FULL | CLOCK-C3 | 2021 | 2.1173756e-08 | -1.1935567e-07 | 1.7965569e-07 | 0.02564818 | True |
| FULL | CLOCK-C3 | 2022 | -1.4453422e-07 | -4.411805e-07 | 1.5257217e-07 | -0.099057442 | True |
| FULL | CLOCK-C3 | 2023 | -2.4828278e-08 | -2.4401523e-07 | 1.9594918e-07 | -0.028812106 | True |
| FULL | CLOCK-C3 | 2024 | -3.2292342e-07 | -5.310951e-07 | -1.1600386e-07 | -0.28825605 | False |
| FULL | CLOCK-C3 | EQ | -1.1777804e-07 | -2.29973e-07 | -5.1112014e-09 | -0.11041766 | False |
| FULL | C3 | 2021 | -7.448712e-07 | -1.6048204e-06 | -6.6666505e-08 | -0.89398141 | False |
| FULL | C3 | 2022 | -9.1070045e-07 | -2.0886189e-06 | 5.2044744e-07 | -0.620894 | True |
| FULL | C3 | 2023 | -1.0996265e-07 | -5.3955558e-07 | 4.1528924e-07 | -0.12748079 | True |
| FULL | C3 | 2024 | -9.4956282e-07 | -1.471613e-06 | -4.4826158e-07 | -0.84290776 | False |
| FULL | C3 | EQ | -6.7877428e-07 | -1.0904706e-06 | -3.0765337e-07 | -0.63302587 | False |
| FULL | M1 | 2021 | -1.2148837e-06 | -2.6516831e-06 | -1.1745059e-07 | -1.4499033 | False |
| FULL | M1 | 2022 | -3.614902e-06 | -5.6883181e-06 | -1.7534479e-06 | -2.4199391 | False |
| FULL | M1 | 2023 | -4.5448645e-07 | -9.8782052e-07 | 2.2116344e-07 | -0.52479459 | True |
| FULL | M1 | 2024 | -1.5886533e-06 | -2.0157321e-06 | -1.128885e-06 | -1.4022603 | False |
| FULL | M1 | EQ | -1.7182313e-06 | -2.3358079e-06 | -1.1807457e-06 | -1.5870403 | False |
| FULL | C0 | 2021 | -7.9653273e-06 | -1.3574438e-05 | -4.0315516e-06 | -8.79747 | False |
| FULL | C0 | 2022 | -1.2744811e-05 | -1.6202558e-05 | -8.9288517e-06 | -8.040394 | False |
| FULL | C0 | 2023 | -5.0135403e-06 | -6.3305489e-06 | -3.7607075e-06 | -5.4996074 | False |
| FULL | C0 | 2024 | -7.2179218e-06 | -1.0376868e-05 | -4.8063061e-06 | -6.0694798 | False |
| FULL | C0 | EQ | -8.2354001e-06 | -9.9260457e-06 | -6.6702008e-06 | -7.1747204 | False |
| FULL | B0-VOL | 2021 | -3.9601341e-06 | -5.7084287e-06 | -2.2323301e-06 | -4.5762893 | False |
| FULL | B0-VOL | 2022 | -7.9314502e-06 | -1.0502495e-05 | -5.3498555e-06 | -5.1604651 | False |
| FULL | B0-VOL | 2023 | -4.0804434e-06 | -6.4259645e-06 | -2.4475109e-06 | -4.5223348 | False |
| FULL | B0-VOL | 2024 | -4.076986e-06 | -5.0424417e-06 | -3.0767307e-06 | -3.5213016 | False |
| FULL | B0-VOL | EQ | -5.0122534e-06 | -6.0466432e-06 | -4.0506639e-06 | -4.4928599 | False |
| OVERNIGHT | CLOCK-C3 | 2021 | 2.2121438e-08 | -1.6070069e-07 | 2.3095233e-07 | 0.019467926 | True |
| OVERNIGHT | CLOCK-C3 | 2022 | -3.0791028e-07 | -7.1607571e-07 | 1.3140145e-07 | -0.15217593 | True |
| OVERNIGHT | CLOCK-C3 | 2023 | -9.3025988e-08 | -3.7130947e-07 | 2.0456283e-07 | -0.076154698 | True |
| OVERNIGHT | CLOCK-C3 | 2024 | -4.8983081e-07 | -8.4827502e-07 | -1.5359488e-07 | -0.30800223 | False |
| OVERNIGHT | CLOCK-C3 | EQ | -2.1716141e-07 | -3.8000016e-07 | -5.2231658e-08 | -0.14546345 | False |
| OVERNIGHT | C3 | 2021 | -1.431064e-06 | -2.6083732e-06 | -3.8733208e-07 | -1.2435021 | False |
| OVERNIGHT | C3 | 2022 | -1.1000134e-06 | -2.788497e-06 | 8.8009116e-07 | -0.5415305 | True |
| OVERNIGHT | C3 | 2023 | -3.5542768e-07 | -1.0487114e-06 | 3.7845353e-07 | -0.29034325 | True |
| OVERNIGHT | C3 | 2024 | -1.0735722e-06 | -1.8235041e-06 | -1.9320592e-07 | -0.67258606 | False |
| OVERNIGHT | C3 | EQ | -9.9001933e-07 | -1.5650115e-06 | -4.0726788e-07 | -0.65973936 | False |
| OVERNIGHT | M1 | 2021 | -1.2327088e-06 | -3.7288124e-06 | 6.5892286e-07 | -1.0729937 | True |
| OVERNIGHT | M1 | 2022 | -9.6265961e-07 | -3.280306e-06 | 1.1922169e-06 | -0.47423266 | True |
| OVERNIGHT | M1 | 2023 | -8.6777548e-07 | -1.7274712e-06 | 1.9068975e-07 | -0.70591761 | True |
| OVERNIGHT | M1 | 2024 | -4.6877171e-07 | -1.07358e-06 | 3.2705063e-07 | -0.29479945 | True |
| OVERNIGHT | M1 | EQ | -8.829789e-07 | -1.6834409e-06 | -8.2896095e-08 | -0.58882866 | False |
| OVERNIGHT | C0 | 2021 | -1.3951676e-05 | -2.2941611e-05 | -7.677711e-06 | -10.933575 | False |
| OVERNIGHT | C0 | 2022 | -2.1147717e-05 | -2.6726845e-05 | -1.5245707e-05 | -9.4757106 | False |
| OVERNIGHT | C0 | 2023 | -8.4059353e-06 | -1.0697517e-05 | -6.324971e-06 | -6.4429649 | False |
| OVERNIGHT | C0 | 2024 | -1.1532658e-05 | -1.6520894e-05 | -7.7370339e-06 | -6.7808189 | False |
| OVERNIGHT | C0 | EQ | -1.3759496e-05 | -1.6358044e-05 | -1.1211507e-05 | -8.4501355 | False |
| OVERNIGHT | B0-VOL | 2021 | -3.0319206e-06 | -5.354523e-06 | -3.745486e-07 | -2.5983983 | False |
| OVERNIGHT | B0-VOL | 2022 | -1.1118551e-05 | -1.55127e-05 | -6.3745409e-06 | -5.2163282 | False |
| OVERNIGHT | B0-VOL | 2023 | -3.171012e-06 | -5.6716327e-06 | -1.0918285e-06 | -2.5321108 | False |
| OVERNIGHT | B0-VOL | 2024 | -3.4912129e-06 | -4.522664e-06 | -2.3189638e-06 | -2.1545881 | False |
| OVERNIGHT | B0-VOL | EQ | -5.2031742e-06 | -6.7286018e-06 | -3.6837786e-06 | -3.3726544 | False |
| INTRADAY | CLOCK-C3 | 2021 | 1.9993195e-08 | -9.0205069e-08 | 1.4243484e-07 | 0.045602068 | True |
| INTRADAY | CLOCK-C3 | 2022 | 5.9601465e-08 | -1.6739533e-07 | 2.9302468e-07 | 0.079044322 | True |
| INTRADAY | CLOCK-C3 | 2023 | 6.3182947e-08 | -2.3003043e-07 | 2.9459382e-07 | 0.1589963 | True |
| INTRADAY | CLOCK-C3 | 2024 | -8.6214873e-08 | -2.8096474e-07 | 8.8231453e-08 | -0.19007069 | True |
| INTRADAY | CLOCK-C3 | EQ | 1.4140684e-08 | -8.6459199e-08 | 1.05922e-07 | 0.027680245 | True |
| INTRADAY | C3 | 2021 | 1.099424e-07 | -3.4743587e-07 | 5.6574843e-07 | 0.2512809 | True |
| INTRADAY | C3 | 2022 | -6.7415705e-07 | -1.5385555e-06 | 3.0372646e-07 | -0.88546021 | True |
| INTRADAY | C3 | 2023 | 2.0681746e-07 | -7.0343301e-08 | 5.3231452e-07 | 0.52233235 | True |
| INTRADAY | C3 | 2024 | -7.7369231e-07 | -1.3332264e-06 | -2.6523085e-07 | -1.6802285 | False |
| INTRADAY | C3 | EQ | -2.8277238e-07 | -6.1993958e-07 | -1.5541223e-08 | -0.55032556 | False |
| INTRADAY | M1 | 2021 | -1.1926783e-06 | -2.0600306e-06 | -3.1104742e-07 | -2.6471367 | False |
| INTRADAY | M1 | 2022 | -6.9288352e-06 | -9.0774794e-06 | -4.8990211e-06 | -8.4096966 | False |
| INTRADAY | M1 | 2023 | 7.8875657e-08 | -3.8111482e-07 | 6.9017522e-07 | 0.19856452 | True |
| INTRADAY | M1 | 2024 | -3.1768726e-06 | -4.3673374e-06 | -2.1153813e-06 | -6.5570085 | False |
| INTRADAY | M1 | EQ | -2.8048776e-06 | -3.5028123e-06 | -2.2120385e-06 | -5.2033864 | False |
| INTRADAY | C0 | 2021 | -5.0793045e-07 | -1.7273777e-06 | 6.0578117e-07 | -1.1447439 | True |
| INTRADAY | C0 | 2022 | -2.2455187e-06 | -3.9294734e-06 | -2.5412959e-07 | -2.8896988 | False |
| INTRADAY | C0 | 2023 | -6.3555114e-07 | -1.2650373e-06 | -1.8344789e-07 | -1.5716929 | False |
| INTRADAY | C0 | 2024 | -1.0987507e-06 | -2.1176932e-06 | -1.5377051e-08 | -2.3694316 | False |
| INTRADAY | C0 | EQ | -1.1219377e-06 | -1.7134285e-06 | -5.9664904e-07 | -2.1484043 | False |
| INTRADAY | B0-VOL | 2021 | -5.116441e-06 | -6.3901651e-06 | -3.8638883e-06 | -10.446157 | False |
| INTRADAY | B0-VOL | 2022 | -3.94922e-06 | -5.2841564e-06 | -2.6718697e-06 | -4.9731141 | False |
| INTRADAY | B0-VOL | 2023 | -5.2540923e-06 | -7.4800616e-06 | -3.4266722e-06 | -11.661274 | False |
| INTRADAY | B0-VOL | 2024 | -4.907731e-06 | -6.2002507e-06 | -3.6733879e-06 | -9.78008 | False |
| INTRADAY | B0-VOL | EQ | -4.8068711e-06 | -5.5334364e-06 | -4.1052997e-06 | -8.5980013 | False |

400 draws,seed22042, whole months within year and equal years. Full correlated stock/origin/session blocks retained. No IID row inference, selection-adjusted p-values or independent confirmation; intervals condition on selected encoders and fitted calibration factors.

## Independent calibration

| year | group | scale | c0 | c_raw | n_eff | kappa | rho | c_star | delta_from_global | sessions | origins | rows | weight_mass | q_max | top10_share | top1pct_share | global_q_max | global_top10_share | global_top1pct_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | INTRADAY | 0.0058487592 | 1.2173685 | 1.1330098 | 49.969862 | 25 | 0.66653267 | 1.1611407 | -0.056227807 | 53 | 118 | 2360 | 0.40616497 | 4.9471359 | 0.020207683 | 0.038565245 | 8.8197213 | 0.014021795 | 0.053330843 |
| 2021 | OVERNIGHT | 0.0058487592 | 1.2173685 | 1.2750672 | 53.007529 | 25 | 0.67951811 | 1.2565758 | 0.039207341 | 56 | 165 | 3300 | 0.59383503 | 8.8197213 | 0.022407255 | 0.056288257 | 8.8197213 | 0.014021795 | 0.053330843 |
| 2022 | INTRADAY | 0.0059334067 | 1.1849396 | 1.1008178 | 42.707587 | 25 | 0.63076516 | 1.1318785 | -0.053061107 | 47 | 108 | 2160 | 0.45461905 | 5.9106464 | 0.029445345 | 0.050188605 | 8.1874113 | 0.015426554 | 0.054484145 |
| 2022 | OVERNIGHT | 0.0059334067 | 1.1849396 | 1.2550619 | 44.696801 | 25 | 0.64130348 | 1.2299093 | 0.044969687 | 47 | 137 | 2740 | 0.54538095 | 8.1874113 | 0.024353901 | 0.054441403 | 8.1874113 | 0.015426554 | 0.054484145 |
| 2023 | INTRADAY | 0.0061216731 | 1.1206776 | 1.0817723 | 44.089425 | 25 | 0.63815012 | 1.0958502 | -0.02482738 | 46 | 119 | 2380 | 0.46507937 | 7.1952632 | 0.02007715 | 0.041207219 | 7.1952632 | 0.016161654 | 0.054883458 |
| 2023 | OVERNIGHT | 0.0061216731 | 1.1206776 | 1.1545032 | 44.983946 | 25 | 0.64277522 | 1.1424198 | 0.021742269 | 47 | 139 | 2780 | 0.53492063 | 5.0208538 | 0.029327969 | 0.062822665 | 7.1952632 | 0.016161654 | 0.054883458 |
| 2024 | INTRADAY | 0.0061744472 | 1.1517971 | 1.0869484 | 30.687987 | 25 | 0.55107014 | 1.1160609 | -0.035736163 | 35 | 73 | 1460 | 0.45630952 | 5.1584382 | 0.040239588 | 0.053395352 | 10.380999 | 0.032129814 | 0.070918459 |
| 2024 | OVERNIGHT | 0.0061744472 | 1.1517971 | 1.2062234 | 32.95592 | 25 | 0.56863769 | 1.182746 | 0.030948848 | 36 | 90 | 1800 | 0.54369048 | 10.380999 | 0.056428638 | 0.082574888 | 10.380999 | 0.032129814 | 0.070918459 |

Each factor uses own frozen September network/scale and only Oct–Dec outcomes. q uses unconstrained main Mhat; finite positivity and concentration guards apply without trimming. Calibration tail scores are not OOS. Within-origin raw/cal ranks must coincide absent new clamp ties; output files record finite nonnegative predictions.

## Clock, reliability and ordinary/tail trade-offs

| year | scope | arm | rows | sessions | origins | observed | predicted | bias | ratio | raw_MAE | raw_MSE | magnitude_IC | pair_concordance | top4 | bottom4 | tie_rate | constant_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EQ | FULL | S2C-C3 | 80260 | 793 | 4013 | 0.01031327 | 0.010470247 | 0.00015697657 | 1.0152208 | 0.006756096 | 0.00010654817 | 0.33123598 | 0.61981899 | 0.42964073 | 0.30288517 | 0 | 0 |
| EQ | FULL | S2C-RAW | 80260 | 793 | 4013 | 0.01031327 | 0.0080271244 | -0.0022861461 | 0.77832967 | 0.0064745206 | 0.00011398451 | 0.33123598 | 0.61981899 | 0.42964073 | 0.30288517 | 0 | 0 |
| EQ | FULL | CLOCK-C3 | 80260 | 793 | 4013 | 0.01031327 | 0.01045521 | 0.00014193959 | 1.0137628 | 0.0067570931 | 0.00010666595 | 0.33025404 | 0.61944331 | 0.42946585 | 0.30302756 | 0 | 0 |
| EQ | FULL | C3 | 80260 | 793 | 4013 | 0.01031327 | 0.010588584 | 0.00027531389 | 1.0266951 | 0.0068010295 | 0.00010722694 | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| EQ | FULL | M1 | 80260 | 793 | 4013 | 0.01031327 | 0.010855766 | 0.00054249545 | 1.0526017 | 0.0068839895 | 0.0001082664 | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| EQ | FULL | C0 | 80260 | 793 | 4013 | 0.01031327 | 0.0080327552 | -0.0022805153 | 0.77887564 | 0.0064974483 | 0.00011478357 | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| EQ | INTRADAY | S2C-C3 | 34800 | 757 | 1740 | 0.0075759099 | 0.0079011446 | 0.00032523467 | 1.0429301 | 0.0049480963 | 5.1099972e-05 | 0.31811022 | 0.61516697 | 0.42610967 | 0.29628817 | 0 | 0 |
| EQ | INTRADAY | S2C-RAW | 34800 | 757 | 1740 | 0.0075759099 | 0.0063394956 | -0.0012364143 | 0.8367966 | 0.0047176374 | 5.2864102e-05 | 0.31811022 | 0.61516697 | 0.42610967 | 0.29628817 | 0 | 0 |
| EQ | INTRADAY | CLOCK-C3 | 34800 | 757 | 1740 | 0.0075759099 | 0.0078819071 | 0.00030599718 | 1.0403908 | 0.0049425262 | 5.1085832e-05 | 0.31804631 | 0.61505755 | 0.42717511 | 0.29598844 | 0 | 0 |
| EQ | INTRADAY | C3 | 34800 | 757 | 1740 | 0.0075759099 | 0.0080690821 | 0.00049317221 | 1.0650974 | 0.0049946708 | 5.1382745e-05 | 0.31055911 | 0.61222379 | 0.42296056 | 0.2911356 | 0 | 0 |
| EQ | INTRADAY | M1 | 34800 | 757 | 1740 | 0.0075759099 | 0.0089577906 | 0.0013818807 | 1.1824046 | 0.0052666348 | 5.390485e-05 | 0.31055911 | 0.61222379 | 0.42296056 | 0.2911356 | 0 | 0 |
| EQ | INTRADAY | C0 | 34800 | 757 | 1740 | 0.0075759099 | 0.0066260867 | -0.00094982322 | 0.87462586 | 0.0047403156 | 5.222191e-05 | 0.31055911 | 0.61222379 | 0.42296056 | 0.2911356 | 0 | 0 |
| EQ | OVERNIGHT | S2C-C3 | 45460 | 771 | 2273 | 0.012430622 | 0.01245563 | 2.5007829e-05 | 1.0020118 | 0.0081514723 | 0.00014907217 | 0.34240804 | 0.62392834 | 0.43140148 | 0.31083578 | 0 | 0 |
| EQ | OVERNIGHT | S2C-RAW | 45460 | 771 | 2273 | 0.012430622 | 0.0093283026 | -0.0031023194 | 0.75042927 | 0.0078321296 | 0.00016094785 | 0.34240804 | 0.62392834 | 0.43140148 | 0.31083578 | 0 | 0 |
| EQ | OVERNIGHT | CLOCK-C3 | 45460 | 771 | 2273 | 0.012430622 | 0.012444453 | 1.3830835e-05 | 1.0011126 | 0.0081575796 | 0.00014928933 | 0.34099113 | 0.62331562 | 0.43118663 | 0.31143076 | 0 | 0 |
| EQ | OVERNIGHT | C3 | 45460 | 771 | 2273 | 0.012430622 | 0.012540867 | 0.00011024505 | 1.0088688 | 0.0081967497 | 0.00015006219 | 0.33746026 | 0.62193351 | 0.426739 | 0.30933661 | 0 | 0 |
| EQ | OVERNIGHT | M1 | 45460 | 771 | 2273 | 0.012430622 | 0.012325338 | -0.00010528415 | 0.99153026 | 0.0081336573 | 0.00014995515 | 0.33746026 | 0.62193351 | 0.426739 | 0.30933661 | 0 | 0 |
| EQ | OVERNIGHT | C0 | 45460 | 771 | 2273 | 0.012430622 | 0.0091219793 | -0.0033086427 | 0.73383128 | 0.0078555806 | 0.00016283167 | 0.33746026 | 0.62193351 | 0.426739 | 0.30933661 | 0 | 0 |

| arm | field | group | rows | raw_MSE | raw_MAE | ratio | raw_MSE_loss_share | false_low_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2C-C3 | slot | 09:30 | 9900 | 8.5937715e-05 | 0.0064592002 | 0.96478582 | 0.097634323 | 0.5 |
| S2C-C3 | slot | 10:30 | 12200 | 4.2730591e-05 | 0.0046774306 | 1.0628389 | 0.060799452 | 0.5 |
| S2C-C3 | slot | 11:30 | 12920 | 3.5092985e-05 | 0.0042017489 | 1.1164922 | 0.055303645 | 0.5 |
| S2C-C3 | slot | 12:30 | 12000 | 0.00013388451 | 0.0077004187 | 1.0253365 | 0.19408786 | 0.5 |
| S2C-C3 | slot | 13:30 | 10800 | 0.00015808897 | 0.0083107848 | 1.0078636 | 0.18749867 | 0.5 |
| S2C-C3 | slot | 14:30 | 10940 | 0.00014462995 | 0.0082354877 | 1.0104454 | 0.17709834 | 0.5 |
| S2C-C3 | slot | 15:30 | 11500 | 0.00016291099 | 0.0084149171 | 0.96824907 | 0.22757772 | 0.5 |
| S2C-C3 | calendar | EARLY_CLOSE | 280 | 9.390029e-05 | 0.0073455048 | 1.0566446 | 0.0054538458 | 0.5 |
| S2C-C3 | calendar | NORMAL | 79980 | 0.00010663477 | 0.0067520152 | 1.0149692 | 0.99454615 | 0.5 |
| S2C-C3 | tail_ALL | PREFIX95 | 5176 | 0.0011357282 | 0.028504888 | 0.35979035 | 0.58707878 | 0.16429971 |
| S2C-C3 | tail_ALL | LE_PREFIX95 | 75084 | 4.7015082e-05 | 0.005461198 | 1.2339566 | 0.41292122 | 0.52055051 |
| S2C-C3 | tail_ALL | PREFIX99 | 841 | 0.0039347087 | 0.058153658 | 0.23358916 | 0.33216956 | 0.12770865 |
| S2C-C3 | tail_ALL | LE_PREFIX99 | 79419 | 7.1892976e-05 | 0.0062852078 | 1.0718662 | 0.66783044 | 0.50357772 |
| CLOCK-C3 | slot | 09:30 | 9900 | 8.6004041e-05 | 0.0064565913 | 0.96388652 | 0.097607236 | 0.5 |
| CLOCK-C3 | slot | 10:30 | 12200 | 4.2668682e-05 | 0.0046726649 | 1.0607265 | 0.060648222 | 0.5 |
| CLOCK-C3 | slot | 11:30 | 12920 | 3.5084057e-05 | 0.0041945651 | 1.1115589 | 0.055230749 | 0.5 |
| CLOCK-C3 | slot | 12:30 | 12000 | 0.00013402839 | 0.0077031288 | 1.022969 | 0.19410675 | 0.5 |
| CLOCK-C3 | slot | 13:30 | 10800 | 0.00015826973 | 0.0083132083 | 1.0069231 | 0.18750269 | 0.5 |
| CLOCK-C3 | slot | 14:30 | 10940 | 0.00014499436 | 0.008250306 | 1.0111282 | 0.1773489 | 0.5 |
| CLOCK-C3 | slot | 15:30 | 11500 | 0.00016307744 | 0.0084183492 | 0.96752063 | 0.22755546 | 0.5 |
| CLOCK-C3 | calendar | EARLY_CLOSE | 280 | 9.5161479e-05 | 0.0074119973 | 1.0553544 | 0.0055252299 | 0.5 |
| CLOCK-C3 | calendar | NORMAL | 79980 | 0.00010674519 | 0.0067525906 | 1.0135087 | 0.99447477 | 0.5 |
| CLOCK-C3 | tail_ALL | PREFIX95 | 5176 | 0.0011397858 | 0.028590717 | 0.3578698 | 0.58918019 | 0.16900817 |
| CLOCK-C3 | tail_ALL | LE_PREFIX95 | 75084 | 4.6821412e-05 | 0.0054553553 | 1.232714 | 0.41081981 | 0.52038539 |
| CLOCK-C3 | tail_ALL | PREFIX99 | 841 | 0.0039444212 | 0.058244634 | 0.23239017 | 0.33296611 | 0.12669868 |
| CLOCK-C3 | tail_ALL | LE_PREFIX99 | 79419 | 7.1886155e-05 | 0.0062849775 | 1.0704171 | 0.66703389 | 0.50357254 |
| C3 | slot | 09:30 | 9900 | 8.5686661e-05 | 0.006535592 | 1.0134249 | 0.096789453 | 0.5 |
| C3 | slot | 10:30 | 12200 | 4.3160707e-05 | 0.0047153549 | 1.0709311 | 0.061037839 | 0.5 |
| C3 | slot | 11:30 | 12920 | 3.5679162e-05 | 0.0042170967 | 1.1054812 | 0.055848974 | 0.5 |
| C3 | slot | 12:30 | 12000 | 0.00013438596 | 0.0077700103 | 1.0470579 | 0.19351378 | 0.5 |
| C3 | slot | 13:30 | 10800 | 0.0001581792 | 0.0084177689 | 1.0455743 | 0.18639445 | 0.5 |
| C3 | slot | 14:30 | 10940 | 0.00014500067 | 0.008347103 | 1.0467981 | 0.17643494 | 0.5 |
| C3 | slot | 15:30 | 11500 | 0.00016568682 | 0.0083426259 | 0.91901863 | 0.22998056 | 0.5 |
| C3 | calendar | EARLY_CLOSE | 280 | 9.7163746e-05 | 0.0070715327 | 0.85814826 | 0.0056393261 | 0.5 |
| C3 | calendar | NORMAL | 79980 | 0.00010729431 | 0.0067989864 | 1.0279185 | 0.99436067 | 0.5 |
| C3 | tail_ALL | PREFIX95 | 5176 | 0.0011282416 | 0.028323945 | 0.36408222 | 0.57778267 | 0.16997937 |
| C3 | tail_ALL | LE_PREFIX95 | 75084 | 4.8400551e-05 | 0.0055254622 | 1.2474192 | 0.42221733 | 0.52031774 |
| C3 | tail_ALL | PREFIX99 | 841 | 0.0039155094 | 0.05794399 | 0.23635238 | 0.32817818 | 0.11835925 |
| C3 | tail_ALL | LE_PREFIX99 | 79419 | 7.2784097e-05 | 0.0063329367 | 1.0839761 | 0.67182182 | 0.50363835 |

groups.csv also contains all annual seven clocks, actual early-close cases, conditional intraday/overnight prefix95/99 events and complements, and shared C0-score weighted-decile membership (fixed q=.1.. .9, descriptive only). False-low is average-tie within-origin bottom-half rank <=10.5, weighted on event cohorts; not a calibrated event probability. Cohorts use saved restricted-prefix95/99 raw-A thresholds, never OOS fitted. Tail loss contributions use unchanged unconditional row weights. Within-origin IC/pair/top4/bottom4/ties/constant rates appear in metrics.csv; top/bottom chance .2, pair chance .5, canonical tie handling reused. Tail-underprediction alone is not proof of conditional-mean miscalibration.

## Auxiliary signed diagnostics (separate task quantities)

| year | component | ticker | rows | sessions | signed_MSE | signed_MAE | observed_signed_mean | predicted_signed_mean | weighted_Pearson |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | origin_to_close | ALL | 10465 | 183 | 3.7022663e-05 | 0.0040678912 | -0.000208217 | -0.00010777397 | 0.043820201 |
| 2021 | close_to_next_open | ALL | 10465 | 183 | 0.00010414633 | 0.0067283587 | 0.00046172575 | 0.00062238738 | -0.0018691254 |
| 2021 | next_open_to_exit | ALL | 10465 | 183 | 0.00013746693 | 0.0083994635 | 0.00028041434 | -0.00013026067 | 0.0095141521 |
| 2022 | origin_to_close | ALL | 13167 | 205 | 7.5009245e-05 | 0.0058907269 | 0.00010804083 | -8.071315e-05 | 0.027333573 |
| 2022 | close_to_next_open | ALL | 13167 | 205 | 0.00020201055 | 0.0095892993 | -0.00031177632 | 0.0011292945 | -0.0038495382 |
| 2022 | next_open_to_exit | ALL | 13167 | 205 | 0.00021479857 | 0.010386495 | -0.00012440722 | -0.00023080807 | 0.010046631 |
| 2023 | origin_to_close | ALL | 9978 | 180 | 3.3560433e-05 | 0.0039873608 | 0.00014251344 | -0.00012932323 | 0.0046284262 |
| 2023 | close_to_next_open | ALL | 9978 | 180 | 0.00012443971 | 0.0064674019 | -0.00027120041 | 0.00092831835 | 0.026114607 |
| 2023 | next_open_to_exit | ALL | 9978 | 180 | 0.00013910313 | 0.0078975739 | 0.0005026919 | -8.1306295e-05 | -0.0053324707 |
| 2024 | origin_to_close | ALL | 11251 | 203 | 3.9433097e-05 | 0.0041238045 | 0.00012132244 | 6.2702425e-05 | -0.056016054 |
| 2024 | close_to_next_open | ALL | 11251 | 203 | 0.00015282592 | 0.0063853704 | 0.00067534232 | 0.00086720512 | 0.058712813 |
| 2024 | next_open_to_exit | ALL | 11251 | 203 | 0.00013020785 | 0.00788203 | -9.9947415e-05 | 5.9551446e-05 | -0.0081940833 |

auxiliary_diagnostics.csv gives all20 stocks and pooled per-year/component weighted signed MSE/MAE/Pearson with genuine supported-cell/session denominators. These are signed-return auxiliary tasks, not primary magnitude MSE or gap-forecast model results. They are post-fit and were not used for model choice. Correlations are descriptive and selected source support may be nonrandom.

## Decision and limitations

The predeclared point-MSE hurdle is passed versus both same-task references, with three annual point wins. **Retain C-A only as a provisional near-tie candidate; keep CLOCK-C3 as a reference and do not declare a general replacement.** About68.5% of the net equal-year gain versus CLOCK-C3 comes from F24. The tiny mean gain, modest ordinary/intraday costs and almost unchanged MAE/ranking deserve researcher review; they do not warrant alpha/kappa tuning or another automatic fit.

The signed auxiliary heads provide weak/inconsistent discrimination: pooled annual signed Pearson correlations are −0.0560..0.0438 for pre-close, −0.00385..0.0587 for gap, and −0.00819..0.01005 for post-open. This does not establish a reliable jump detector or causal decomposition mechanism. Auxiliary metrics condition on genuine source support and use original OOS row weights renormalized on that supported subset (and each ticker for stock tables); they differ from the training phase's global overnight-conditional weights. Stocks/overlapping origins remain dependent.

Read-only event_retrieval.csv supplies the prespecified prefix95/99 top-four event checks, without fitting a classifier or thresholds. Top-four recall at95 is55.3486% vs55.3064% CLOCK-C3; at99 it falls66.6869% vs67.5660%. False-low95 improves16.9008%→16.4300%, but false-low99 worsens12.6699%→12.7709%. Event prevalence is5.9319%/.9373% under earlier-prefix thresholds, not an OOS-selected percentile. Fractional membership across forecast ties preserves exactly4 names/origin; random-ranking recall convention is20%. Precision is weighted event mass retrieved divided by weighted top-four mass. These are retrospective diagnostic cohorts, not calibrated event probabilities, signed alpha or economic results.

Any benefit mixes auxiliary supervision, added heads, changed training trajectory/epoch count and own calibration; no authorized ablation isolates a causal effect. Primary raw/cal rankings are identical with zero clamp rows in all four folds. All saved control metrics reproduce. Supported source component formulas match saved price ratios exactly (supplemental source-only cross-check during execution before performance inspection); the pre-fit positive/finite, signed-additivity and source/version gates had already passed. Independent signed-gap modeling remains S2-D and was not run. STOP for researcher review.

Coverage-table nan values in auxiliary training-normalization columns for selector/calibration/OOS mean NOT APPLICABLE: no training loss denominator is fitted on those roles. They are not nonfinite predictions or labels. The explicit finite-value guards passed. Final focused checks:14 tests passed (3.94s), Ruff PASS, full512-file Pylance basic check zero errors/warnings (109.308s); numerical replay of9 frozen protocol/metric/coefficient/journal files is byte-identical. The actual editor Problems refresh remains human-confirmed: select repository .venv/bin/python, retain Pylance basic and refresh Problems. Source, earlier ledgers and all bound prior artifacts are unchanged; only the permitted successor registry pointer/journal advances to162/300. See integrity_checks.json/final_checks.json and the standard Codex session handoff. No commit or push.

Any benefit is an auxiliary-supervision/extra-head/optimization package; no ablation isolates capacity from supervision. No signed alpha, causal jump mechanism or option profitability claim is supported. Intraday C0/C3 preference and deferred routed test remain unresolved. STOP for researcher review.

## Reproduction and preservation

Commands: `.venv/bin/python -m lstm_data.hf20_s2c_ca --preflight`, focused tests/Ruff/full static as recorded in readiness/session handoff, then one single-use `--run`; `--report` reads only saved outputs. Do not rerun --run on this namespace. No commit/push. Only new module/test/output namespace/session handoff and permitted successor registry pointer/journal; old assets never overwritten. See protocol,preflight,readiness,phase_parity,verification and journal for sources,tests,budget/resources. Model state dicts/prediction Parquets are local ignored artifacts; no old scores/inputs duplicated.
