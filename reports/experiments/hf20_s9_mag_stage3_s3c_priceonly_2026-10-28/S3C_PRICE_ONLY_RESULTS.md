# S3-C newest-hour price-only H8

## Scientific decision

**Execution COMPLETE, 4/4 folds. No incremental evidence over CLOCK-C3; retain CLOCK-C3 and close this fixed S3-C candidate.** No training restart, retry or new candidate was made during resumed supervision. The completed four selector/refit pairs consumed starts 171–174 (170 → 174/300).

The primary calibrated model has equal-year raw magnitude MSE **0.000106739896737**, versus **0.000106665945886** for CLOCK-C3: **+0.069329% (worse)**. The paired difference is +7.39509e-8, with 400-draw, year-stratified whole-month descriptive 95% interval **[−1.40500e-7, +2.63861e-7]**. F21/F23/F24 lose (+0.114%, +0.051%, +0.298%); F22 improves (−0.121%). F24's descriptive interval is entirely positive; these intervals do not adjust for repeated research selection. Near equality is not evidence of equivalence or improvement.

Equal-year magnitude IC falls from **0.330254043 to 0.327834230**; top-four retrieval falls from 0.429466 to 0.424269 (fixed20 chance 0.20). Pair concordance is 0.618639 versus 0.619443; bottom-four retrieval is essentially unchanged (0.303025 versus 0.303028). No clamp ties or constant outputs occurred; raw/C3 rankings match exactly within every origin. MAE is slightly worse, **0.0067606731 versus 0.0067570931**. The ratio of equal-year weighted forecast and observed means is 1.014784 versus 1.013763; bias is +0.000152476 versus +0.000141941 in log-return units. MSE is in squared log-return units; MAE/means/bias are in log-return units.

The raw diagnostic improves raw MSE by **0.449590%** against CLOCK-RAW (descriptive delta interval [−7.91645e-7, −2.75640e-7]), with gains in 2021–23 but a loss in 2024. This does not promote RAW over the predeclared calibrated primary. The calibrated model is also 0.068509% worse than completed S3B-C3, with an interval spanning zero. Improvements over older C3 (−0.454219%), C0 (−7.007685%) and B0-VOL (−4.320999%) do not demonstrate incremental minute-path value beyond CLOCK-C3.

### Conditional effects and source sensitivity

Against CLOCK-C3, equal-year intraday MSE changes −0.089787%, overnight-crossing MSE +0.107268%; both intervals include zero. Intraday IC falls from 0.318046 to 0.313254 and overnight IC from 0.340991 to 0.339607. The late 15:30 slot worsens by 0.303023%. Small prefix95/99 tail improvements coexist with ordinary-complement deterioration. Prefix95 events account for 58.69% of the new model's total MSE, despite about 5.93% of unconditional weight; prefix99 events account for 33.19% with 0.94% of weight. Tail forecast/realized ratios (0.359/0.234) remain small, but retrospective outcome-selected underprediction alone is not proof of conditional-mean miscalibration.

Prefix95 false-low ranking increases from 0.169008 to 0.170755 and top-four event capture falls from 0.553064 to 0.549933. Prefix99 false-low improves (0.126699 → 0.122433), while top-four capture worsens (0.675660 → 0.667260). This is mixed descriptive event ordering, not a fitted event classifier. Shared C0-score deciles, per-stock/month results, early-close categories and tail-by-category diagnostics are in groups.csv; bins are descriptive and never fitted into a new calibration map.

Complete and incomplete newest-hour cohorts both have slightly worse MSE. Thus missingness does not reveal a hidden same-task success. The masks, revised-vintage source coverage, selected epoch and 488 additional parameters remain attribution confounders; no fixed newest-hour summary control was separately authorized or fitted. S3-B sees summaries across 48 hours; this candidate sees minute ordering only in the newest hour. Their contrast cannot isolate ordering or architecture. These results do not justify automatically escalating to S3-D or another feature/seed sweep. Any Stage 3 closure or Stage 5 ranking work requires a separate researcher decision.

| field | group | C_MSE | CLOCK_MSE | MSE_change_pct | C_MAE | C_mean_ratio |
| --- | --- | --- | --- | --- | --- | --- |
| slot | 09:30 | 8.58950282e-05 | 8.60040411e-05 | -0.126753235 | 0.00644915139 | 0.957330008 |
| slot | 10:30 | 4.2559332e-05 | 4.26686823e-05 | -0.256277532 | 0.00466985578 | 1.06182904 |
| slot | 11:30 | 3.50961979e-05 | 3.50840572e-05 | 0.034604462 | 0.00419578401 | 1.11362241 |
| slot | 12:30 | 0.000134199726 | 0.000134028386 | 0.127838732 | 0.00771300734 | 1.028012 |
| slot | 13:30 | 0.000158300758 | 0.000158269726 | 0.0196070918 | 0.00831589858 | 1.00968157 |
| slot | 14:30 | 0.000144955345 | 0.000144994355 | -0.0269047984 | 0.00824781958 | 1.01201857 |
| slot | 15:30 | 0.000163571604 | 0.000163077441 | 0.303023473 | 0.0084390492 | 0.967379488 |
| calendar | EARLY | 9.22352936e-05 | 9.51614792e-05 | -3.07496865 | 0.0071375086 | 0.975671937 |
| calendar | NORMAL | 0.000106830886 | 0.000106745194 | 0.0802769872 | 0.00675770544 | 1.01508983 |
| source_latest | COMPLETE | 0.000109195977 | 0.000109122545 | 0.0672934114 | 0.00679626368 | 1.01175619 |
| source_latest | INCOMPLETE | 8.6473743e-05 | 8.63552405e-05 | 0.137226802 | 0.00646575886 | 1.04191042 |
| tail_ALL | PREFIX95 | 0.00113858295 | 0.0011397858 | -0.105532535 | 0.0285569912 | 0.358643651 |
| tail_ALL | LE_PREFIX95 | 4.71237818e-05 | 4.68214117e-05 | 0.645794625 | 0.00546434767 | 1.23372963 |
| tail_ALL | PREFIX99 | 0.00393488218 | 0.00394442122 | -0.241836243 | 0.0581488181 | 0.233652938 |
| tail_ALL | LE_PREFIX99 | 7.20534878e-05 | 7.18861545e-05 | 0.232775311 | 0.00628961966 | 1.07144607 |

Conditional rows preserve inherited weights renormalized on the reported subset, then equal-weight annual scores; their losses cannot be added without original group mass. Tail loss contributions use unconditional row weights. `source_complete_fraction` in groups.csv means the average fraction of observed scheduled minute positions, while the COMPLETE/INCOMPLETE cohort uses all60 validity. Equal-year source/calendar counts sum annual counts; a session can appear in both source cohorts across its stocks. Early-close support is only about 0.63% of unconditional weight, so its favorable slice is not a promotion criterion.

## Source, timing, training and preservation

The pinned pre-2025 canonical source passed the price-only numerical/time/action checks on the required footprint: **14,628 unique newest hours**, 292,560 stock-hours, 17,553,600 expected minute positions, 17,452,556 genuine observations, 17,075,244 adjacent return positions, 261,093 complete stock-hours and zero entirely empty stock-hours. All blocks were covered by the prior certified footprint; 159 bounded monthly OHLC projections were used, no minute volume values. The retained hourly FT16 volume channels are unchanged. Native OHLC reconstruction matched on checked aggregates (maximum difference zero, tolerance 1e-10); source_receipt.json and coverage.csv distinguish the unique-block source proof from overlapping role populations.

At 09:30, the newest full hour is the previous session's last full block; at normal 15:30 it is 14:30–15:30. No closing stub or 49th input was added. Publication by approximately origin+2 minutes is a historical availability assumption, not measured vendor arrival. Action/quarantine decisions retain the prior revised-vintage limitations; no retrospective issue-code feature was introduced. All source dates remain through 2024; no 2025 market or protected 2026 observations/hashes were accessed. No network, download, trading, options, new gap labels or later experiment.

All five roles per fold and eight phase recipes passed preflight before the first start. Original FT16 and target scales were reproduced, the original 10 clock fields retained, and saved CLOCK output replay matched exactly. Primary population is unchanged: 80,260 rows / 4,013 origins / 793 sessions; all20 ticker order retained. Each fold independently used 60×5 newest-hour inputs alongside 48×16 FT16, H8+H32, 6,931 parameters, seed42 and the original transformed-M selector. Every refit began with a fresh optimizer and initial seed, used its own September recipe, and was frozen across calibration/OOS. The same source scale h is input-only; it is distinct from target scale s. No feature or target statistics were fitted on selector, calibration or OOS features.

### Fitting receipt

| year | selected_epoch | selector_epochs | raw_minimum_epoch | initial_scale | scale | seconds | reload_max_error |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 29 | 39 | 29 | 0.00579711768 | 0.00584875919 | 1191.58999 | 0 |
| 2022 | 13 | 23 | 13 | 0.00593512463 | 0.00593340672 | 735.907063 | 0 |
| 2023 | 22 | 32 | 22 | 0.00607233442 | 0.00612167308 | 1458.45048 | 0 |
| 2024 | 16 | 26 | 16 | 0.0061734035 | 0.0061744472 | 1185.58746 | 0 |

Selected epochs are the qualifying-best epochs, which can precede the minimum stopping duration; no C0 epoch was transplanted. All four stopped after ten nonqualifying selector epochs. Refit epochs exactly match selected epochs.

### Independent calibration receipt

| year | group | c0 | c_raw | n_eff | rho | c_star | sessions | origins | q_max | top10_share | top1pct_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | INTRADAY | 1.19366602 | 1.11376609 | 49.969862 | 0.666532666 | 1.14041011 | 53 | 118 | 4.5221329 | 0.0202549522 | 0.0390609241 |
| 2021 | OVERNIGHT | 1.19366602 | 1.24831513 | 53.007529 | 0.679518114 | 1.23080108 | 56 | 165 | 8.09877516 | 0.0223371602 | 0.0564230543 |
| 2022 | INTRADAY | 1.18824627 | 1.102029 | 42.7075874 | 0.630765163 | 1.13386342 | 47 | 108 | 5.7686546 | 0.0295580509 | 0.050402579 |
| 2022 | OVERNIGHT | 1.18824627 | 1.26011533 | 44.6968006 | 0.641303477 | 1.23433615 | 47 | 137 | 8.30355181 | 0.0240885609 | 0.0543149324 |
| 2023 | INTRADAY | 1.11870625 | 1.07746613 | 44.0894253 | 0.638150124 | 1.09238886 | 46 | 119 | 7.3571512 | 0.0203117028 | 0.0415687475 |
| 2023 | OVERNIGHT | 1.11870625 | 1.15456191 | 44.9839458 | 0.642775215 | 1.14175338 | 47 | 139 | 4.989857 | 0.029622365 | 0.063572697 |
| 2024 | INTRADAY | 1.14238011 | 1.07211189 | 30.6879867 | 0.551070142 | 1.10365739 | 35 | 73 | 5.06175556 | 0.0405898058 | 0.0539791992 |
| 2024 | OVERNIGHT | 1.14238011 | 1.20135496 | 32.9559205 | 0.568637686 | 1.17591543 | 36 | 90 | 10.2456417 | 0.0566438295 | 0.0828923452 |

Group factors are newly estimated only from each frozen September model's Oct–Dec residuals, using unconstrained Mhat, unchanged κ=25 and no trimming. Algebraic replay reproduces saved C3 factors/decodes; all moments are finite. F24 effective sessions are only 30.69/32.96 and its overnight largest1% contributes about 8.29% of the weighted moment: an uncertainty limitation, not permission for another correction. Raw/C3 share unchanged encoder M-loss diagnostics; calibration does not improve that encoder loss.

### Verification and resources

`verification.json`: PASS for exact keys/labels/canonical order, all four reload maximum differences zero, finite nonnegative decodes, independent hierarchical aggregation, coefficient replay, unchanged prefitted hashes and bound predecessor assets (except authorized registry successor). Journal records four starts, eight phases, no retries. Opening ledger170; closing174/300. All prior journal entries and the blocked volume-based S3-C record remain intact. Only the authorized current pointer advances to schema33 with fit_permission=false.

23 focused tests passed; Ruff passed. Full installed Pylance-basic parity check: **522 project Python files, zero errors, zero warnings**. Human VSCode Problems refresh is still outstanding, not claimed. Peak training RSS 1,185,546,240 bytes (~1.19GB); final-fit project store12,822,974,464 bytes and task162,687,464 bytes, below 2GB/15GB/2.5GB caps. Four-fold fit time sums to about76.2 minutes. Arrow's sandbox CPU-cache sysctl warnings were nonfatal; no dependencies or environment settings changed. No failure/retry was hidden.

Machine-readable details: metrics.csv, paired_MSE.csv, groups.csv, fit_summary.csv, calibration_coefficients.csv, role_counts.csv, coverage.csv, readiness.json and per-fold phase/checkpoint/training/score files. See SESSION_HANDOFF.md and the standard Codex session report for exact commands and Git state. STOP: no further model or baseline fitting is authorized.


## Full numerical appendix


**COMPLETE: 4/4 folds; exploratory/post-search.**

Same complete20 original4h target/keys/weights. Unchanged48x16 plus newest60x5 price-only H8,6931parameters,H32,seed42,original transformed-M selector/refit and own independentOct-Dec C3kappa25. Raw is a diagnostic,never an OOS-selected replacement.

## Annual/equal-year primary metrics

| year | arm | raw_MSE | raw_MAE | predicted | observed | ratio | magnitude_IC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | S3C-PRICE-C3 | 8.2648464e-05 | 0.006371975 | 0.010191718 | 0.0098002675 | 1.0399428 | 0.32149789 |
| 2021 | S3C-PRICE-RAW | 8.9427293e-05 | 0.0060780745 | 0.0075718444 | 0.0098002675 | 0.7726161 | 0.32149789 |
| 2021 | CLOCK-C3 | 8.2554613e-05 | 0.0063781675 | 0.010211883 | 0.0098002675 | 1.0420005 | 0.32627607 |
| 2021 | CLOCK-RAW | 9.0561076e-05 | 0.0060824636 | 0.0074034373 | 0.0098002675 | 0.75543216 | 0.32627607 |
| 2021 | S3B-C3 | 8.2726943e-05 | 0.0064117162 | 0.010325957 | 0.0098002675 | 1.0536403 | 0.32557556 |
| 2021 | S3B-RAW | 9.1029084e-05 | 0.0060865747 | 0.0073247884 | 0.0098002675 | 0.74740698 | 0.32557556 |
| 2021 | C3 | 8.3320658e-05 | 0.006421753 | 0.010306108 | 0.0098002675 | 1.051615 | 0.31785841 |
| 2021 | M1 | 8.3790671e-05 | 0.0063963177 | 0.010205226 | 0.0098002675 | 1.0413212 | 0.31785841 |
| 2021 | C1a | 8.4303166e-05 | 0.0064637727 | 0.010290148 | 0.0098002675 | 1.0499864 | 0.31785841 |
| 2021 | C0 | 9.0541114e-05 | 0.0061042972 | 0.0075378642 | 0.0098002675 | 0.76914882 | 0.31785841 |
| 2021 | B0-VOL | 8.6535921e-05 | 0.0066089924 | 0.010256419 | 0.0098002675 | 1.0465448 | 0.31183632 |
| 2021 | B0-CLOCK | 8.8733837e-05 | 0.0064413665 | 0.0093055751 | 0.0098002675 | 0.94952256 | 0.29038533 |
| 2021 | B0-RMEAN | 9.6342162e-05 | 0.0067870981 | 0.0093076165 | 0.0098002675 | 0.94973086 | 0.289525 |
| 2021 | B0-RMED | 0.00010897265 | 0.006576386 | 0.0062980819 | 0.0098002675 | 0.64264387 | 0.28093515 |
| 2022 | S3C-PRICE-C3 | 0.0001457335 | 0.0083359369 | 0.013063576 | 0.012951183 | 1.0086782 | 0.35038171 |
| 2022 | S3C-PRICE-RAW | 0.00015817797 | 0.0080568733 | 0.0099606353 | 0.012951183 | 0.76909076 | 0.35038171 |
| 2022 | CLOCK-C3 | 0.00014590951 | 0.0083086676 | 0.012936514 | 0.012951183 | 0.99886738 | 0.35445091 |
| 2022 | CLOCK-RAW | 0.0001591903 | 0.0080603043 | 0.0098267996 | 0.012951183 | 0.75875689 | 0.35445091 |
| 2022 | S3B-C3 | 0.00014621023 | 0.0083120127 | 0.012899277 | 0.012951183 | 0.99599216 | 0.34963178 |
| 2022 | S3B-RAW | 0.0001596413 | 0.0080636698 | 0.0097972378 | 0.012951183 | 0.75647434 | 0.34963178 |
| 2022 | C3 | 0.00014667567 | 0.0083746314 | 0.013237313 | 0.012951183 | 1.022093 | 0.35029686 |
| 2022 | M1 | 0.00014937987 | 0.0086367779 | 0.014210493 | 0.012951183 | 1.0972351 | 0.35029686 |
| 2022 | C1a | 0.00014822502 | 0.008390051 | 0.013099666 | 0.012951183 | 1.0114648 | 0.35029686 |
| 2022 | C0 | 0.00015850978 | 0.0080691855 | 0.010049479 | 0.012951183 | 0.77595064 | 0.35029686 |
| 2022 | B0-VOL | 0.00015369642 | 0.0084733784 | 0.012531746 | 0.012951183 | 0.96761402 | 0.32314717 |
| 2022 | B0-CLOCK | 0.00016861834 | 0.0082521988 | 0.0093759284 | 0.012951183 | 0.72394377 | 0.3178606 |
| 2022 | B0-RMEAN | 0.00017887366 | 0.0084948737 | 0.0093897435 | 0.012951183 | 0.72501047 | 0.31318948 |
| 2022 | B0-RMED | 0.00021279945 | 0.0089435291 | 0.0063774046 | 0.012951183 | 0.49241868 | 0.31247937 |
| 2023 | S3C-PRICE-C3 | 8.6216689e-05 | 0.0059915087 | 0.0090692393 | 0.0092524379 | 0.98019996 | 0.32275894 |
| 2023 | S3C-PRICE-RAW | 9.0534259e-05 | 0.0057974335 | 0.0074078918 | 0.0092524379 | 0.80064215 | 0.32275894 |
| 2023 | CLOCK-C3 | 8.6173073e-05 | 0.0059986859 | 0.0091179546 | 0.0092524379 | 0.9854651 | 0.32380415 |
| 2023 | CLOCK-RAW | 9.1029308e-05 | 0.005794158 | 0.0072747552 | 0.0092524379 | 0.78625279 | 0.32380415 |
| 2023 | S3B-C3 | 8.5959777e-05 | 0.0060201546 | 0.0092425707 | 0.0092524379 | 0.99893355 | 0.32501187 |
| 2023 | S3B-RAW | 9.1023829e-05 | 0.005786105 | 0.0072412554 | 0.0092524379 | 0.78263215 | 0.32501187 |
| 2023 | C3 | 8.6258208e-05 | 0.0060253978 | 0.0092152346 | 0.0092524379 | 0.99597907 | 0.32024473 |
| 2023 | M1 | 8.6602732e-05 | 0.0059913023 | 0.0090094132 | 0.0092524379 | 0.97373398 | 0.32024473 |
| 2023 | C1a | 8.6835625e-05 | 0.0060297739 | 0.0091368676 | 0.0092524379 | 0.9875092 | 0.32024473 |
| 2023 | C0 | 9.1161785e-05 | 0.0058106884 | 0.0073476242 | 0.0092524379 | 0.79412845 | 0.32024473 |
| 2023 | B0-VOL | 9.0228688e-05 | 0.0063314547 | 0.0097563049 | 0.0092524379 | 1.0544578 | 0.2909517 |
| 2023 | B0-CLOCK | 8.6579247e-05 | 0.0061385546 | 0.0096074191 | 0.0092524379 | 1.0383662 | 0.30364354 |
| 2023 | B0-RMEAN | 9.2996729e-05 | 0.0064594275 | 0.0096741235 | 0.0092524379 | 1.0455756 | 0.3034832 |
| 2023 | B0-RMED | 0.00010117992 | 0.0060310446 | 0.0065814601 | 0.0092524379 | 0.71132172 | 0.29968513 |
| 2024 | S3C-PRICE-C3 | 0.00011236094 | 0.0063432718 | 0.0095384505 | 0.0092491933 | 1.0312738 | 0.31669837 |
| 2024 | S3C-PRICE-RAW | 0.00011688665 | 0.0059836773 | 0.0074940513 | 0.0092491933 | 0.81023837 | 0.31669837 |
| 2024 | CLOCK-C3 | 0.00011202659 | 0.0063428514 | 0.0095544881 | 0.0092491933 | 1.0330077 | 0.31648505 |
| 2024 | CLOCK-RAW | 0.00011630047 | 0.0059863549 | 0.0075584134 | 0.0092491933 | 0.81719704 | 0.31648505 |
| 2024 | S3B-C3 | 0.00011177033 | 0.0063239381 | 0.009490959 | 0.0092491933 | 1.0261391 | 0.31497657 |
| 2024 | S3B-RAW | 0.0001160693 | 0.0059827222 | 0.0075574675 | 0.0092491933 | 0.81709477 | 0.31497657 |
| 2024 | C3 | 0.00011265323 | 0.0063823356 | 0.0095956812 | 0.0092491933 | 1.0374614 | 0.3102724 |
| 2024 | M1 | 0.00011329232 | 0.00651156 | 0.0099979316 | 0.0092491933 | 1.0809517 | 0.3102724 |
| 2024 | C1a | 0.0001135108 | 0.0063801416 | 0.0094768388 | 0.0092491933 | 1.0246125 | 0.3102724 |
| 2024 | C0 | 0.00011892159 | 0.0060056223 | 0.0071960535 | 0.0092491933 | 0.77801958 | 0.3102724 |
| 2024 | B0-VOL | 0.00011578065 | 0.0066372528 | 0.0098591363 | 0.0092491933 | 1.0659455 | 0.29063745 |
| 2024 | B0-CLOCK | 0.00011474675 | 0.0065242191 | 0.0097328363 | 0.0092491933 | 1.0522903 | 0.29931135 |
| 2024 | B0-RMEAN | 0.00012124512 | 0.0067770511 | 0.0096948401 | 0.0092491933 | 1.0481822 | 0.29475541 |
| 2024 | B0-RMED | 0.00012941663 | 0.0062474444 | 0.0066391174 | 0.0092491933 | 0.71780502 | 0.29135808 |
| EQ | S3C-PRICE-C3 | 0.0001067399 | 0.0067606731 | 0.010465746 | 0.01031327 | 1.0147844 | 0.32783423 |
| EQ | S3C-PRICE-RAW | 0.00011375654 | 0.0064790146 | 0.0081086057 | 0.01031327 | 0.7862303 | 0.32783423 |
| EQ | CLOCK-C3 | 0.00010666595 | 0.0067570931 | 0.01045521 | 0.01031327 | 1.0137628 | 0.33025404 |
| EQ | CLOCK-RAW | 0.00011427029 | 0.0064808202 | 0.0080158513 | 0.01031327 | 0.77723661 | 0.33025404 |
| EQ | S3B-C3 | 0.00010666682 | 0.0067669554 | 0.010489691 | 0.01031327 | 1.0171062 | 0.32879894 |
| EQ | S3B-RAW | 0.00011444088 | 0.006479768 | 0.0079801873 | 0.01031327 | 0.77377853 | 0.32879894 |
| EQ | C3 | 0.00010722694 | 0.0068010295 | 0.010588584 | 0.01031327 | 1.0266951 | 0.3246681 |
| EQ | M1 | 0.0001082664 | 0.0068839895 | 0.010855766 | 0.01031327 | 1.0526017 | 0.3246681 |
| EQ | C1a | 0.00010821865 | 0.0068159348 | 0.01050088 | 0.01031327 | 1.0181911 | 0.3246681 |
| EQ | C0 | 0.00011478357 | 0.0064974483 | 0.0080327552 | 0.01031327 | 0.77887564 | 0.3246681 |
| EQ | B0-VOL | 0.00011156042 | 0.0070127696 | 0.010600902 | 0.01031327 | 1.0278894 | 0.30414316 |
| EQ | B0-CLOCK | 0.00011466954 | 0.0068390848 | 0.0095054397 | 0.01031327 | 0.92167075 | 0.3028002 |
| EQ | B0-RMEAN | 0.00012236442 | 0.0071296126 | 0.0095165809 | 0.01031327 | 0.92275102 | 0.30023827 |
| EQ | B0-RMED | 0.00013809216 | 0.006949601 | 0.006474016 | 0.01031327 | 0.62773647 | 0.29611443 |

## Paired whole-month descriptive uncertainty

| left | right | scope | year | delta | low | high | percent | interval_includes_zero |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S3C-PRICE-C3 | CLOCK-C3 | FULL | 2021 | 9.3850996e-08 | -3.952045e-07 | 6.8333663e-07 | 0.11368353 | True |
| S3C-PRICE-C3 | CLOCK-C3 | FULL | 2022 | -1.7601036e-07 | -5.5445558e-07 | 2.9371062e-07 | -0.12062981 | True |
| S3C-PRICE-C3 | CLOCK-C3 | FULL | 2023 | 4.3615698e-08 | -9.579187e-08 | 1.6529308e-07 | 0.050614068 | True |
| S3C-PRICE-C3 | CLOCK-C3 | FULL | 2024 | 3.3434706e-07 | 4.4024859e-08 | 6.8205261e-07 | 0.29845331 | False |
| S3C-PRICE-C3 | CLOCK-C3 | FULL | EQ | 7.3950851e-08 | -1.4050045e-07 | 2.6386056e-07 | 0.069329391 | True |
| S3C-PRICE-C3 | S3B-C3 | FULL | 2021 | -7.8479218e-08 | -5.9814558e-07 | 5.4925733e-07 | -0.094865366 | True |
| S3C-PRICE-C3 | S3B-C3 | FULL | 2022 | -4.7673367e-07 | -1.1047838e-06 | 2.8635244e-07 | -0.32606041 | True |
| S3C-PRICE-C3 | S3B-C3 | FULL | 2023 | 2.5691233e-07 | -8.4005169e-08 | 6.390871e-07 | 0.29887505 | True |
| S3C-PRICE-C3 | S3B-C3 | FULL | 2024 | 5.9060809e-07 | 2.0863185e-07 | 1.0418523e-06 | 0.52841223 | False |
| S3C-PRICE-C3 | S3B-C3 | FULL | EQ | 7.3076882e-08 | -1.6628984e-07 | 3.2694466e-07 | 0.068509479 | True |
| S3C-PRICE-RAW | S3B-RAW | FULL | 2021 | -1.6017901e-06 | -2.5658868e-06 | -5.6996365e-07 | -1.7596465 | False |
| S3C-PRICE-RAW | S3B-RAW | FULL | 2022 | -1.4633355e-06 | -2.1632749e-06 | -6.3334374e-07 | -0.91663967 | False |
| S3C-PRICE-RAW | S3B-RAW | FULL | 2023 | -4.8957014e-07 | -8.9491308e-07 | -9.0400423e-08 | -0.53784832 | False |
| S3C-PRICE-RAW | S3B-RAW | FULL | 2024 | 8.1734833e-07 | 4.2454096e-07 | 1.2413582e-06 | 0.70418995 | False |
| S3C-PRICE-RAW | S3B-RAW | FULL | EQ | -6.8433686e-07 | -1.0591817e-06 | -3.6612262e-07 | -0.59798288 | False |
| S3C-PRICE-C3 | C3 | FULL | 2021 | -6.7219396e-07 | -1.3766371e-06 | -3.3838299e-08 | -0.80675546 | False |
| S3C-PRICE-C3 | C3 | FULL | 2022 | -9.4217658e-07 | -2.2045293e-06 | 3.4606393e-07 | -0.64235368 | True |
| S3C-PRICE-C3 | C3 | FULL | 2023 | -4.1518672e-08 | -5.3281487e-07 | 4.1188336e-07 | -0.04813301 | True |
| S3C-PRICE-C3 | C3 | FULL | 2024 | -2.9229234e-07 | -5.642138e-07 | 9.4194845e-08 | -0.25946201 | True |
| S3C-PRICE-C3 | C3 | FULL | EQ | -4.8704539e-07 | -9.0392031e-07 | -1.0982549e-07 | -0.45421923 | False |
| S3C-PRICE-C3 | M1 | FULL | 2021 | -1.1422064e-06 | -2.3208694e-06 | -2.3138809e-07 | -1.3631666 | False |
| S3C-PRICE-C3 | M1 | FULL | 2022 | -3.6463781e-06 | -5.5789956e-06 | -1.7003844e-06 | -2.4410103 | False |
| S3C-PRICE-C3 | M1 | FULL | 2023 | -3.8604247e-07 | -9.4644289e-07 | 2.4263752e-07 | -0.44576246 | True |
| S3C-PRICE-C3 | M1 | FULL | 2024 | -9.3138278e-07 | -1.3881198e-06 | -3.6249585e-07 | -0.82210584 | False |
| S3C-PRICE-C3 | M1 | FULL | EQ | -1.5265025e-06 | -2.1432569e-06 | -1.0034026e-06 | -1.4099503 | False |
| S3C-PRICE-C3 | C0 | FULL | 2021 | -7.8926501e-06 | -1.3610827e-05 | -3.971803e-06 | -8.7172001 | False |
| S3C-PRICE-C3 | C0 | FULL | 2022 | -1.2776287e-05 | -1.63939e-05 | -8.8309323e-06 | -8.0602515 | False |
| S3C-PRICE-C3 | C0 | FULL | 2023 | -4.9450963e-06 | -6.2545098e-06 | -3.7127762e-06 | -5.4245277 | False |
| S3C-PRICE-C3 | C0 | FULL | 2024 | -6.5606513e-06 | -9.2447222e-06 | -4.4027621e-06 | -5.5167874 | False |
| S3C-PRICE-C3 | C0 | FULL | EQ | -8.0436712e-06 | -9.6226346e-06 | -6.4791577e-06 | -7.0076853 | False |
| S3C-PRICE-C3 | B0-VOL | FULL | 2021 | -3.8874569e-06 | -5.8907146e-06 | -1.7295316e-06 | -4.4923043 | False |
| S3C-PRICE-C3 | B0-VOL | FULL | 2022 | -7.9629264e-06 | -1.0682553e-05 | -5.4632689e-06 | -5.1809445 | False |
| S3C-PRICE-C3 | B0-VOL | FULL | 2023 | -4.0119994e-06 | -6.2659764e-06 | -2.3864798e-06 | -4.4464787 | False |
| S3C-PRICE-C3 | B0-VOL | FULL | 2024 | -3.4197155e-06 | -4.6483102e-06 | -2.0389628e-06 | -2.9536156 | False |
| S3C-PRICE-C3 | B0-VOL | FULL | EQ | -4.8205245e-06 | -5.8861796e-06 | -3.7662611e-06 | -4.3209989 | False |
| S3C-PRICE-C3 | B0-CLOCK | FULL | 2021 | -6.0853731e-06 | -9.2199011e-06 | -2.9082858e-06 | -6.8580074 | False |
| S3C-PRICE-C3 | B0-CLOCK | FULL | 2022 | -2.2884844e-05 | -3.2919583e-05 | -1.2465273e-05 | -13.571978 | False |
| S3C-PRICE-C3 | B0-CLOCK | FULL | 2023 | -3.6255821e-07 | -1.5371333e-06 | 1.0327644e-06 | -0.41875879 | True |
| S3C-PRICE-C3 | B0-CLOCK | FULL | 2024 | -2.3858094e-06 | -4.5232682e-06 | -4.4599418e-07 | -2.0791956 | False |
| S3C-PRICE-C3 | B0-CLOCK | FULL | EQ | -7.9296462e-06 | -1.0947342e-05 | -5.3585454e-06 | -6.9152157 | False |
| S3C-PRICE-RAW | CLOCK-RAW | FULL | 2021 | -1.1337823e-06 | -1.8146317e-06 | -4.2735289e-07 | -1.2519533 | False |
| S3C-PRICE-RAW | CLOCK-RAW | FULL | 2022 | -1.0123367e-06 | -1.4748609e-06 | -4.680002e-07 | -0.63592861 | False |
| S3C-PRICE-RAW | CLOCK-RAW | FULL | 2023 | -4.9504885e-07 | -7.5282073e-07 | -2.9415078e-07 | -0.54383457 | False |
| S3C-PRICE-RAW | CLOCK-RAW | FULL | 2024 | 5.861778e-07 | 1.1995406e-07 | 1.09242e-06 | 0.50402015 | False |
| S3C-PRICE-RAW | CLOCK-RAW | FULL | EQ | -5.1374752e-07 | -7.9164453e-07 | -2.7563951e-07 | -0.44958976 | False |
| S3C-PRICE-RAW | C0 | FULL | 2021 | -1.1138208e-06 | -2.3554703e-06 | -1.8358473e-07 | -1.2301823 | False |
| S3C-PRICE-RAW | C0 | FULL | 2022 | -3.3181519e-07 | -1.4057865e-06 | 7.0970496e-07 | -0.2093342 | True |
| S3C-PRICE-RAW | C0 | FULL | 2023 | -6.2752626e-07 | -1.1642874e-06 | -3.2382528e-08 | -0.68836547 | False |
| S3C-PRICE-RAW | C0 | FULL | 2024 | -2.0349433e-06 | -2.6559591e-06 | -1.5372112e-06 | -1.7111639 | False |
| S3C-PRICE-RAW | C0 | FULL | EQ | -1.0270264e-06 | -1.4682409e-06 | -6.7454397e-07 | -0.89475037 | False |

## Boundaries

400 whole-calendar-month draws/seed22042,year-stratified equal-year. Conditional on trained/selected/calibrated models and repeatedly inspected years;not selection-adjusted confirmation. Group scores renormalize original row weights within the conditional population,not an independent replication. Tail thresholds are original lawful September-prefix95/99;cohorts retrospective. C0 score deciles are descriptive shared memberships,not future calibration boundaries. See groups.csv for clocks,IO,early closes,stock/month,tails and source missingness. Magnitudes are not signed alpha,volatility-integral,option-IV or P&L.

Source publication byorigin+2min and revised-vintage action/quarantine rules are disclosed historical proxies. Masks/extra parameters and B's full48-hour information versus C's intended newest-hour reach prevent architecture-only attribution. No minute volume/share-regime normalizer is used in the new model.

The former S3-C volume-based experiment remains BLOCKED and unchanged. This price-only amendment is separate. No optional latest-hour fitted control,third LSTM,S3-D/E,Stage5,protected release or trading work.
