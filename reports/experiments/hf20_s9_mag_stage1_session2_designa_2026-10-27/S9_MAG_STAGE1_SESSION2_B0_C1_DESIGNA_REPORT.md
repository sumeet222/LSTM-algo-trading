# S9 MAG Stage 1 Session 2 — B0/C1 Design A

Prepared 27 October 2026. **PARTIAL: F21 completed; F22–F24 BLOCKED before fitting.**

## 1. Executive result

**MIXED one-year calibration evidence, not a four-year success.** F21 uses 19,100 matched stock-origin rows / 955 origins / 188 sessions. Global smearing C1a reduces raw OOS MSE versus the identical uncalibrated encoder, but the simple raw multiplier M1 does slightly better. Both improve mean level while worsening overall MAE and ordinary-period error. Large-move amplitudes remain substantially underpredicted. F22–F24 cannot be scored under the approved shortened selector because coverage fails its frozen sufficiency rules. No four-year equal-year average is available.

F21: C1a MSE improvement **6.89%**; M1 **7.46%**. Mean forecast/realized ratio 0.769 → 1.050 (C1a) / 1.041 (M1). All are historically out of fit within the new chronology, but the period is repeatedly studied, **exploratory/post-search**, not pristine confirmation.

Next decision: review whether to amend the blocked-fold selector chronology and calibration coverage. Do not launch O1 or contextual calibration automatically. If a scalar map remains a comparator, M1 deserves preference over a claim that special Jensen modeling produced an extra advantage. Its superiority here is a one-year result, not a frozen promotion choice.

## 2. Preflight, exact role populations and blockers

| year | role | cutoff | embargo_after | first_date | last_date | sessions | origins | stock_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | inner_train | 2020-06-30 | 0000 | 2011-04-01 | 2020-06-30 | 2100 | 11449 | 228980 |
| 2021 | selector | 2020-09-30 | 2020-06-30 | 2020-07-13 | 2020-09-30 | 57 | 349 | 6980 |
| 2021 | restricted_refit | 2020-09-30 | 0000 | 2011-04-01 | 2020-09-30 | 2164 | 11846 | 236920 |
| 2021 | calibration | 2020-12-31 | 2020-09-30 | 2020-10-12 | 2020-12-30 | 56 | 283 | 5660 |
| 2021 | oos | 2021-12-31 | 2020-12-31 | 2021-01-13 | 2021-12-31 | 188 | 955 | 19100 |
| 2022 | inner_train | 2021-06-30 | 0000 | 2011-04-01 | 2021-06-29 | 2331 | 12716 | 254320 |
| 2022 | selector | 2021-09-30 | 2021-06-30 | 2021-07-22 | 2021-09-30 | 35 | 172 | 3440 |
| 2022 | restricted_refit | 2021-09-30 | 0000 | 2011-04-01 | 2021-09-30 | 2366 | 12888 | 257760 |
| 2022 | calibration | 2021-12-31 | 2021-09-30 | 2021-10-12 | 2021-12-31 | 50 | 245 | 4900 |
| 2022 | oos | 2022-12-31 | 2021-12-31 | 2022-01-12 | 2022-12-30 | 210 | 1180 | 23600 |
| 2023 | inner_train | 2022-06-30 | 0000 | 2011-04-01 | 2022-06-30 | 2547 | 13896 | 277920 |
| 2023 | selector | 2022-09-30 | 2022-06-30 | 2022-07-13 | 2022-09-27 | 38 | 195 | 3900 |
| 2023 | restricted_refit | 2022-09-30 | 0000 | 2011-04-01 | 2022-09-27 | 2592 | 14137 | 282740 |
| 2023 | calibration | 2022-12-30 | 2022-09-30 | 2022-10-13 | 2022-12-30 | 48 | 258 | 5160 |
| 2023 | oos | 2023-12-31 | 2022-12-30 | 2023-01-13 | 2023-12-29 | 187 | 887 | 17740 |
| 2024 | inner_train | 2023-06-30 | 0000 | 2011-04-01 | 2023-06-30 | 2740 | 14945 | 298900 |
| 2024 | selector | 2023-09-29 | 2023-06-30 | 2023-07-14 | 2023-09-29 | 47 | 185 | 3700 |
| 2024 | restricted_refit | 2023-09-29 | 0000 | 2011-04-01 | 2023-09-29 | 2795 | 15167 | 303340 |
| 2024 | calibration | 2023-12-29 | 2023-09-29 | 2023-10-11 | 2023-12-29 | 40 | 163 | 3260 |
| 2024 | oos | 2024-12-31 | 2023-12-29 | 2024-01-11 | 2024-12-31 | 208 | 991 | 19820 |

Selector coverage by slot (minimum 50 sessions and 25 origins in each slot):

| year | sessions | 09:30 | 10:30 | 11:30 | 12:30 | 13:30 | 14:30 | 15:30 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 57 | 52 | 51 | 51 | 49 | 53 | 46 | 47 |
| 2022 | 35 | 26 | 28 | 26 | 22 | 24 | 24 | 22 |
| 2023 | 38 | 23 | 30 | 31 | 28 | 25 | 31 | 27 |
| 2024 | 47 | 22 | 24 | 33 | 30 | 19 | 26 | 31 |

Independent calibration coverage, disclosed separately:

| year | sessions | 09:30 | 10:30 | 11:30 | 12:30 | 13:30 | 14:30 | 15:30 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 56 | 36 | 38 | 48 | 43 | 37 | 40 | 41 |
| 2022 | 50 | 36 | 37 | 38 | 35 | 33 | 31 | 35 |
| 2023 | 48 | 38 | 39 | 44 | 38 | 36 | 29 | 34 |
| 2024 | 40 | 19 | 26 | 28 | 25 | 23 | 21 | 21 |

F21 passes: selector57 sessions, minimum46 origins per slot; independent tail56 sessions, minimum36 per slot. F22/F23/F24 selectors have35/38/47 sessions, with minimum22/23/19 origins per slot, and are BLOCKED. No neural, scalar or B0 fitting and no new OOS metric was performed for those years. F23/F24 tails have48/40 sessions; F24 has some slots below25. These tail figures are review flags: the live prompt supplied no new numeric calibration-tail minimum, and none was invented as an extra gate.

Latest monthly extension passing selector counts, **not approved or executed**:

| year | proposed_inner_stop | proposed_selector_start | selector_stop | sessions | origins | slot_min | approved |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | 2021-04-30 | 2021-05-01 | 2021-09-30 | 58 | 278 | 36 | False |
| 2023 | 2022-05-31 | 2022-06-01 | 2022-09-30 | 59 | 313 | 38 | False |
| 2024 | 2023-05-31 | 2023-06-01 | 2023-09-29 | 69 | 291 | 31 | False |

Those alternatives move initial training earlier and extend the selector; they are not just more rows in the same approved fold. The researcher must choose whether a common revision is preferable and settle calibration coverage before another fit. Existing fitted F21 is preserved.

Nominal dates are filtered by saved S4 source/label eligibility. Actual cutoffs use the last scheduled session on/before June30, September30 and December31. Strict maturity is before next local midnight minus4h. The first of48 completed input steps must lie strictly after the prior cutoff for selector, calibration and OOS. All original OOS keys matched in order, 20 names per origin, without dropping rows. The full timestamp limits are in session2_role_counts.csv; actual folds/maturity rules are frozen in session2_design.json and session2_protocol.json.

## 3. Matched annual results and uncertainty

Raw A is absolute endpoint log return. Means/MAE use log-return units; MSE uses squared log-return units. Within year: equal stock within origin, origin within session, session within year. Subgroup errors condition original role mass on the group; they do not rebalance surviving rows or pretend overlapping stock/clock/tail groups are independent replications.

| year | arm | raw_MSE | raw_MAE | observed | predicted | bias | ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | C0 | 9.0541114e-05 | 0.0061042972 | 0.0098002675 | 0.0075378642 | -0.0022624033 | 0.76914882 |
| 2021 | C1a | 8.4303166e-05 | 0.0064637727 | 0.0098002675 | 0.010290148 | 0.00048988031 | 1.0499864 |
| 2021 | M1 | 8.3790671e-05 | 0.0063963177 | 0.0098002675 | 0.010205226 | 0.00040495892 | 1.0413212 |
| 2021 | B0-RMEAN | 9.6342162e-05 | 0.0067870981 | 0.0098002675 | 0.0093076165 | -0.00049265105 | 0.94973086 |
| 2021 | B0-RMED | 0.00010897265 | 0.006576386 | 0.0098002675 | 0.0062980819 | -0.0035021856 | 0.64264387 |
| 2021 | B0-CLOCK | 8.8733837e-05 | 0.0064413665 | 0.0098002675 | 0.0093055751 | -0.00049469243 | 0.94952256 |
| 2021 | B0-VOL | 8.6535921e-05 | 0.0066089924 | 0.0098002675 | 0.010256419 | 0.00045615162 | 1.0465448 |

Primary paired raw-MSE differences versus C0; negative is improvement:

| year | arm | delta_MSE_vs_C0 | delta_low | delta_high |
| --- | --- | --- | --- | --- |
| 2021 | C1a | -6.2379486e-06 | -1.0569915e-05 | -3.1775387e-06 |
| 2021 | M1 | -6.7504437e-06 | -1.1211251e-05 | -3.5389704e-06 |

Additional descriptive paired comparisons with the strongest raw-MSE B0:

| year | comparison | mean | low | high | sessions | months |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | C1a minus B0-VOL | -2.2327554e-06 | -4.4699127e-06 | 3.2677938e-08 | 188 | 12 |
| 2021 | M1 minus B0-VOL | -2.7452505e-06 | -5.0613876e-06 | -1.9675275e-07 | 188 | 12 |
| 2021 | C1a minus M1 | 5.1249509e-07 | 5.3419676e-08 | 8.7838998e-07 | 188 | 12 |

Intervals resample whole observed calendar-month blocks using the existing 400-draw utility, seed22042. F21 has12 month blocks/188 sessions. They are descriptive and not selection-adjusted. No IID stock-row or four-year independence assumption is made. C1a's point MSE is lower than B0-VOL, but that paired interval includes zero. M1 is slightly better than C1a and B0-VOL in this single year; this is not multi-year robustness.

Four-year equal-year result: **NOT AVAILABLE**. A lone F21 mean is not substituted.

## 4. Fits, phase identity and calibration factors

Initial MAG recipe/scale reuse is restricted to the exact unchanged June population: S4/F21_inner_recipe.json and S9/HF20-S9-F21-H4-MAG-S42/inner_target_recipe.json (S4/S9 roots below). The initial network itself was newly trained, not an archived checkpoint. July–September alone selected epoch29 after39 selector epochs. A fresh seed42 model and empty optimizer then refit through2020-09-30 for exactly29 epochs, using new input-only-prefix FT16 floors/scalers and raw-A scale. No October–December outcome entered either phase, feature/target fitting or B0 selection.

F21 restricted model identity `5185a51700c68d3c0267d97d5de060a2c2ec9435babc9e13b9b1f98dafda1431`; checkpoint reload maximum error 0. Parameters were checked unchanged across calibration and OOS prediction. The same September input recipe, target scale and network generated both populations.

| year | selected_epoch | selector_epochs | restricted_scale | c | k | ridge_penalty | prefix95 | prefix99 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 29 | 39 | 0.0058487592 | 1.2055995 | 1.3538618 | 0.001 | 0.029152684 | 0.05559186 |

C0 = s*expm1(max(Mhat,0)). C1a fits c = E_cal,w[exp(log1p(A/s)−Mhat)] using unconstrained Mhat, then predicts s*max(0,exp(Mhat)*c−1). M1 fits k=max(0,E_cal,w[A0*A]/E_cal,w[A0²]) and predicts k*A0. There is no double inverse, inner-scale transfer, residual trimming, extra context parameter or OOS coefficient fit. Calibration exports are fitting data, not OOS improvement evidence. The menu lists multiplication within C2; this specific one-parameter M1 comparison is explicitly authorized by the live Session2 prompt, which excludes the other C2 variants.

Exponential-moment concentration: maximum exp(residual) 9.1531; largest row 0.203% of the weighted moment, largest10 rows 1.503%, largest1% 5.653%. Status FINITE; no handful dominance or nonfinite estimate was observed. Across-fold c/k stability is UNAVAILABLE because three folds are blocked.

B0-RMEAN/RMED use weighted stock mean/left empirical median of A through September. RMED is judged appropriately by raw MAE, not required to win mean-squared error. B0-CLOCK shrinks stock×slot means toward stock means with fixed50 origin-equivalent prior observations: origin weights are rescaled to mean1 before adding that prior mass. B0-VOL uses27 columns: unpenalized intercept,19 stock dummies (VZ reference),6 clock dummies (09:30 reference), and prefix-standardized log(decoded FT16 V2 RMS60). Its normalized weighted raw-MSE ridge penalties0.001/0.1/10 were tested only on the July–September selector; 0.001 won, followed by September refit. Original FT16 robust/fallback semantics are retained; the extra single-column ridge mean/SD is fitted only on its phase prefix. Full coefficients/centers/SD/candidate losses are in F21/coefficients.json. B0 has explicit stock/clock identifiers, which are not neural channels in MAG. No through-December baseline receives a silent history advantage.

## 5. Magnitude ordering, clocks, tails and reliability

| year | arm | magnitude_IC | top4 | bottom4 | pair_concordance | tie_rate | constant_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | C0 | 0.31785841 | 0.3866483 | 0.31024569 | 0.61520032 | 0 | 0 |
| 2021 | C1a | 0.31785841 | 0.3866483 | 0.31024569 | 0.61520032 | 0 | 0 |
| 2021 | M1 | 0.31785841 | 0.3866483 | 0.31024569 | 0.61520032 | 0 | 0 |
| 2021 | B0-RMEAN | 0.289525 | 0.3383327 | 0.31817059 | 0.60272715 | 0 | 0 |
| 2021 | B0-RMED | 0.28093515 | 0.3383327 | 0.31817059 | 0.59961101 | 0 | 0 |
| 2021 | B0-CLOCK | 0.29038533 | 0.3383327 | 0.31817059 | 0.60321242 | 0 | 0 |
| 2021 | B0-VOL | 0.31183632 | 0.38873797 | 0.30850747 | 0.61339001 | 0.00042106596 | 0 |

IC is within-origin Spearman using average ties, then origin→session→year means; historical pooled all-row0.408 is not substituted. Top/bottom4 retrieval uses fractional membership across boundary ties, chance0.20. Pair concordance excludes realized ties and credits predicted ties0.5, chance0.50. C0/C1a/M1 have identical rankings and zero tied/constant origins. No negative Mhat/decoder clamp occurred in calibration or OOS. B0-VOL clamps144 OOS values to zero (0.754% of rows), with small pair ties and no constant whole-origin scores. Original Mhat transformed MSE is 0.225555544 for all three network decoders; no corrected-A-to-M loss is misrepresented as the historical objective.

Intraday versus original overnight-crossing targets (all seven arms):

| year | arm | group | rows | sessions | observed | predicted | ratio | raw_MSE | raw_MAE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | C0 | INTRADAY | 8440 | 181 | 0.0071110578 | 0.0062135333 | 0.87378466 | 4.4370662e-05 | 0.0044164307 |
| 2021 | C0 | OVERNIGHT | 10660 | 183 | 0.011959003 | 0.0086009573 | 0.71920354 | 0.00012760397 | 0.0074592147 |
| 2021 | C1a | INTRADAY | 8440 | 181 | 0.0071110578 | 0.0086935351 | 1.2225375 | 4.5717544e-05 | 0.0050076726 |
| 2021 | C1a | OVERNIGHT | 10660 | 183 | 0.011959003 | 0.011571812 | 0.9676235 | 0.00011527738 | 0.0076326421 |
| 2021 | M1 | INTRADAY | 8440 | 181 | 0.0071110578 | 0.0084122654 | 1.1829837 | 4.505541e-05 | 0.0048815002 |
| 2021 | M1 | OVERNIGHT | 10660 | 183 | 0.011959003 | 0.011644508 | 0.9737022 | 0.000114885 | 0.0076123218 |
| 2021 | B0-RMEAN | INTRADAY | 8440 | 181 | 0.0071110578 | 0.0093076165 | 1.3088934 | 5.5848337e-05 | 0.0056990676 |
| 2021 | B0-RMEAN | OVERNIGHT | 10660 | 183 | 0.011959003 | 0.0093076165 | 0.77829368 | 0.00012884816 | 0.0076605033 |
| 2021 | B0-RMED | INTRADAY | 8440 | 181 | 0.0071110578 | 0.0062980819 | 0.8856744 | 5.0497946e-05 | 0.0047652754 |
| 2021 | B0-RMED | OVERNIGHT | 10660 | 183 | 0.011959003 | 0.0062980819 | 0.52663938 | 0.00015591263 | 0.0080302364 |
| 2021 | B0-CLOCK | INTRADAY | 8440 | 181 | 0.0071110578 | 0.00718104 | 1.0098413 | 4.6440058e-05 | 0.0047415919 |
| 2021 | B0-CLOCK | OVERNIGHT | 10660 | 183 | 0.011959003 | 0.011011024 | 0.92073092 | 0.00012268473 | 0.0078058432 |
| 2021 | B0-VOL | INTRADAY | 8440 | 181 | 0.0071110578 | 0.008089987 | 1.1376629 | 4.8979173e-05 | 0.0051027119 |
| 2021 | B0-VOL | OVERNIGHT | 10660 | 183 | 0.011959003 | 0.0119955 | 1.0030519 | 0.00011668421 | 0.0078181436 |

All seven original clock slots, matched network decoders:

| year | arm | group | rows | sessions | observed | predicted | ratio | raw_MSE | raw_MAE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | C0 | 09:30 | 2600 | 130 | 0.0098704912 | 0.0080800267 | 0.81860432 | 7.8251931e-05 | 0.0059774962 |
| 2021 | C0 | 10:30 | 2920 | 146 | 0.0066053177 | 0.0058658921 | 0.88805601 | 3.5507591e-05 | 0.004122494 |
| 2021 | C0 | 11:30 | 2980 | 149 | 0.0055450688 | 0.0050513705 | 0.91096623 | 2.9445437e-05 | 0.0035688737 |
| 2021 | C0 | 12:30 | 2700 | 135 | 0.010844533 | 0.0083316699 | 0.76828294 | 0.00011034454 | 0.0067462616 |
| 2021 | C0 | 13:30 | 2620 | 131 | 0.011601151 | 0.0089212239 | 0.76899475 | 0.00011908287 | 0.0072205886 |
| 2021 | C0 | 14:30 | 2500 | 125 | 0.012445275 | 0.0090900857 | 0.73040456 | 0.00012975149 | 0.0076069465 |
| 2021 | C0 | 15:30 | 2780 | 139 | 0.0127732 | 0.0082139649 | 0.6430624 | 0.00014621413 | 0.008104754 |
| 2021 | C1a | 09:30 | 2600 | 130 | 0.0098704912 | 0.010943779 | 1.108737 | 7.561858e-05 | 0.0064003849 |
| 2021 | C1a | 10:30 | 2920 | 146 | 0.0066053177 | 0.008274419 | 1.2526905 | 3.7820454e-05 | 0.0047144221 |
| 2021 | C1a | 11:30 | 2980 | 149 | 0.0055450688 | 0.0072924321 | 1.3151202 | 3.2198877e-05 | 0.0042684064 |
| 2021 | C1a | 12:30 | 2700 | 135 | 0.010844533 | 0.01124716 | 1.0371271 | 0.00010350987 | 0.0071161798 |
| 2021 | C1a | 13:30 | 2620 | 131 | 0.011601151 | 0.011957926 | 1.0307534 | 0.00011075547 | 0.0075884604 |
| 2021 | C1a | 14:30 | 2500 | 125 | 0.012445275 | 0.012161505 | 0.97719859 | 0.00011703273 | 0.0077752087 |
| 2021 | C1a | 15:30 | 2780 | 139 | 0.0127732 | 0.011105255 | 0.86941833 | 0.00012660569 | 0.0079661407 |
| 2021 | M1 | 09:30 | 2600 | 130 | 0.0098704912 | 0.010939239 | 1.1082771 | 7.5658832e-05 | 0.0063800299 |
| 2021 | M1 | 10:30 | 2920 | 146 | 0.0066053177 | 0.0079416072 | 1.2023051 | 3.7154823e-05 | 0.0045867717 |
| 2021 | M1 | 11:30 | 2980 | 149 | 0.0055450688 | 0.0068388575 | 1.2333224 | 3.1019163e-05 | 0.0040607542 |
| 2021 | M1 | 12:30 | 2700 | 135 | 0.010844533 | 0.01127993 | 1.0401489 | 0.00010353809 | 0.0070920798 |
| 2021 | M1 | 13:30 | 2620 | 131 | 0.011601151 | 0.012078104 | 1.0411126 | 0.00011049929 | 0.0075757941 |
| 2021 | M1 | 14:30 | 2500 | 125 | 0.012445275 | 0.01230672 | 0.98886683 | 0.00011642984 | 0.0077735755 |
| 2021 | M1 | 15:30 | 2780 | 139 | 0.0127732 | 0.011120573 | 0.87061762 | 0.00012585685 | 0.0079266883 |

Prefix95/99 events and ordinary≤prefix95 complement, all controls:

| year | arm | group | rows | sessions | observed | predicted | ratio | raw_MSE | raw_MAE | weight_mass | raw_MSE_loss_share | false_low_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | C0 | PREFIX95 | 1089 | 162 | 0.040259568 | 0.011461122 | 0.28468069 | 0.00097043674 | 0.028798446 | 0.05473151 | 0.58662264 | 0.17300305 |
| 2021 | C0 | LE_PREFIX95 | 18011 | 188 | 0.0080366591 | 0.0073107057 | 0.90966976 | 3.9594726e-05 | 0.0047902948 | 0.94526849 | 0.41337736 | 0.51893328 |
| 2021 | C0 | PREFIX99 | 94 | 46 | 0.069911893 | 0.012607331 | 0.1803317 | 0.0035487058 | 0.057304562 | 0.0046099291 | 0.18068346 | 0.10123626 |
| 2021 | C1a | PREFIX95 | 1089 | 162 | 0.040259568 | 0.015020025 | 0.37307964 | 0.00078137432 | 0.025239543 | 0.05473151 | 0.50728577 | 0.17300305 |
| 2021 | C1a | LE_PREFIX95 | 18011 | 188 | 0.0080366591 | 0.010016286 | 1.2463246 | 4.3942403e-05 | 0.0053766464 | 0.94526849 | 0.49271423 | 0.51893328 |
| 2021 | C1a | PREFIX99 | 94 | 46 | 0.069911893 | 0.016401894 | 0.23460807 | 0.0031365235 | 0.053509999 | 0.0046099291 | 0.17151374 | 0.10123626 |
| 2021 | M1 | PREFIX95 | 1089 | 162 | 0.040259568 | 0.015516775 | 0.38541831 | 0.00075964167 | 0.024742793 | 0.05473151 | 0.49619289 | 0.17300305 |
| 2021 | M1 | LE_PREFIX95 | 18011 | 188 | 0.0080366591 | 0.0098976852 | 1.2315671 | 4.4658566e-05 | 0.0053340477 | 0.94526849 | 0.50380711 | 0.51893328 |
| 2021 | M1 | PREFIX99 | 94 | 46 | 0.069911893 | 0.017068583 | 0.2441442 | 0.0030724039 | 0.05284331 | 0.0046099291 | 0.16903509 | 0.10123626 |
| 2021 | B0-RMEAN | PREFIX95 | 1089 | 162 | 0.040259568 | 0.01209575 | 0.30044411 | 0.00093477006 | 0.028163818 | 0.05473151 | 0.53103828 | 0.24338208 |
| 2021 | B0-RMEAN | LE_PREFIX95 | 18011 | 188 | 0.0080366591 | 0.0091461822 | 1.1380578 | 4.7796776e-05 | 0.0055493755 | 0.94526849 | 0.46896172 | 0.5148583 |
| 2021 | B0-RMEAN | PREFIX99 | 94 | 46 | 0.069911893 | 0.013656649 | 0.19534085 | 0.0034275611 | 0.056255244 | 0.0046099291 | 0.16400725 | 0.15315934 |
| 2021 | B0-RMED | PREFIX95 | 1089 | 162 | 0.040259568 | 0.0081492129 | 0.2024168 | 0.0011691529 | 0.032110355 | 0.05473151 | 0.58720697 | 0.24119539 |
| 2021 | B0-RMED | LE_PREFIX95 | 18011 | 188 | 0.0080366591 | 0.0061909005 | 0.7703326 | 4.7587698e-05 | 0.0050979567 | 0.94526849 | 0.41279303 | 0.51498491 |
| 2021 | B0-RMED | PREFIX99 | 94 | 46 | 0.069911893 | 0.0092404962 | 0.13217345 | 0.0039326552 | 0.060671397 | 0.0046099291 | 0.16636524 | 0.19601648 |
| 2021 | B0-CLOCK | PREFIX95 | 1089 | 162 | 0.040259568 | 0.013686156 | 0.33994791 | 0.00084798326 | 0.026573412 | 0.05473151 | 0.52304065 | 0.25031238 |
| 2021 | B0-CLOCK | LE_PREFIX95 | 18011 | 188 | 0.0080366591 | 0.0090519373 | 1.1263309 | 4.4772923e-05 | 0.0052757112 | 0.94526849 | 0.47695935 | 0.51445704 |
| 2021 | B0-CLOCK | PREFIX99 | 94 | 46 | 0.069911893 | 0.015631749 | 0.22359213 | 0.0032125523 | 0.054280144 | 0.0046099291 | 0.16689956 | 0.15508242 |
| 2021 | B0-VOL | PREFIX95 | 1089 | 162 | 0.040259568 | 0.015409935 | 0.38276455 | 0.00075844542 | 0.024849633 | 0.05473151 | 0.47969517 | 0.15943169 |
| 2021 | B0-VOL | LE_PREFIX95 | 18011 | 188 | 0.0080366591 | 0.009958028 | 1.2390756 | 4.7632031e-05 | 0.0055528504 | 0.94526849 | 0.52030483 | 0.51971907 |
| 2021 | B0-VOL | PREFIX99 | 94 | 46 | 0.069911893 | 0.016976705 | 0.24283 | 0.003065115 | 0.052935188 | 0.0046099291 | 0.16328436 | 0.1646978 |

Annual reliability: weighted C0-score deciles, all three decoders:

| year | arm | group | rows | sessions | observed | predicted | ratio | raw_MSE | raw_MAE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | C0 | 1 | 1793 | 175 | 0.0036623146 | 0.0033376591 | 0.91135239 | 1.0175994e-05 | 0.0022919348 |
| 2021 | C0 | 2 | 1816 | 187 | 0.0051619072 | 0.0044268832 | 0.85760612 | 2.0412996e-05 | 0.003270104 |
| 2021 | C0 | 3 | 1832 | 187 | 0.0060485501 | 0.0051674814 | 0.85433391 | 3.2120683e-05 | 0.0038352286 |
| 2021 | C0 | 4 | 1929 | 185 | 0.007352259 | 0.0058972826 | 0.80210485 | 4.6941632e-05 | 0.0046734961 |
| 2021 | C0 | 5 | 1902 | 188 | 0.0084516653 | 0.0066499766 | 0.78682441 | 6.2895057e-05 | 0.0053947867 |
| 2021 | C0 | 6 | 1924 | 186 | 0.0096458208 | 0.0074340353 | 0.77070012 | 8.3212552e-05 | 0.0060232805 |
| 2021 | C0 | 7 | 1894 | 187 | 0.010949486 | 0.0082512606 | 0.75357514 | 9.970709e-05 | 0.0068136984 |
| 2021 | C0 | 8 | 1912 | 186 | 0.012913393 | 0.0091872873 | 0.71145419 | 0.00014035264 | 0.0081732122 |
| 2021 | C0 | 9 | 2033 | 179 | 0.014456121 | 0.010607404 | 0.73376555 | 0.00014938766 | 0.0089096574 |
| 2021 | C0 | 10 | 2065 | 170 | 0.019366036 | 0.014422757 | 0.74474494 | 0.00026028367 | 0.011660518 |
| 2021 | C1a | 1 | 1793 | 175 | 0.0036623146 | 0.0052263825 | 1.4270709 | 1.2521223e-05 | 0.0029205771 |
| 2021 | C1a | 2 | 1816 | 187 | 0.0051619072 | 0.0065395505 | 1.2668865 | 2.1778831e-05 | 0.0037875937 |
| 2021 | C1a | 3 | 1832 | 187 | 0.0060485501 | 0.0074324154 | 1.2287929 | 3.324183e-05 | 0.0044653448 |
| 2021 | C1a | 4 | 1929 | 185 | 0.007352259 | 0.0083122634 | 1.1305727 | 4.5743624e-05 | 0.0051493805 |
| 2021 | C1a | 5 | 1902 | 188 | 0.0084516653 | 0.0092197109 | 1.0908751 | 6.0228296e-05 | 0.0058212099 |
| 2021 | C1a | 6 | 1924 | 186 | 0.0096458208 | 0.010164972 | 1.0538213 | 7.8584513e-05 | 0.0064381297 |
| 2021 | C1a | 7 | 1894 | 187 | 0.010949486 | 0.011150218 | 1.0183325 | 9.2468386e-05 | 0.0070411658 |
| 2021 | C1a | 8 | 1912 | 186 | 0.012913393 | 0.012278692 | 0.95084939 | 0.00012683204 | 0.0082896571 |
| 2021 | C1a | 9 | 2033 | 179 | 0.014456121 | 0.013990783 | 0.96781032 | 0.00013478967 | 0.0090046905 |
| 2021 | C1a | 10 | 2065 | 170 | 0.019366036 | 0.018590571 | 0.95995751 | 0.0002369142 | 0.011722762 |
| 2021 | M1 | 1 | 1793 | 175 | 0.0036623146 | 0.0045187292 | 1.2338452 | 1.0823019e-05 | 0.0026008527 |
| 2021 | M1 | 2 | 1816 | 187 | 0.0051619072 | 0.0059933881 | 1.1610802 | 2.0581049e-05 | 0.0035887731 |
| 2021 | M1 | 3 | 1832 | 187 | 0.0060485501 | 0.0069960557 | 1.15665 | 3.221401e-05 | 0.0042903499 |
| 2021 | M1 | 4 | 1929 | 185 | 0.007352259 | 0.0079841056 | 1.0859391 | 4.522174e-05 | 0.0050427597 |
| 2021 | M1 | 5 | 1902 | 188 | 0.0084516653 | 0.0090031493 | 1.0652515 | 5.9937435e-05 | 0.0057568578 |
| 2021 | M1 | 6 | 1924 | 186 | 0.0096458208 | 0.010064656 | 1.0434215 | 7.8489131e-05 | 0.006408443 |
| 2021 | M1 | 7 | 1894 | 187 | 0.010949486 | 0.011171067 | 1.0202366 | 9.2481335e-05 | 0.007044604 |
| 2021 | M1 | 8 | 1912 | 186 | 0.012913393 | 0.012438317 | 0.96321065 | 0.00012663116 | 0.0083153423 |
| 2021 | M1 | 9 | 2033 | 179 | 0.014456121 | 0.014360958 | 0.99341716 | 0.00013459735 | 0.0090629311 |
| 2021 | M1 | 10 | 2065 | 170 | 0.019366036 | 0.01952642 | 1.0082817 | 0.00023700218 | 0.011855194 |

Reliability bins use the predeclared ten weighted empirical C0-score deciles in each OOS year, with whole ties retained and the same membership for all arms. Their numeric boundaries are descriptive, not future calibration cutoffs. All baselines/slots/deciles and the99th-tail complement are retained in session2_groups.csv. Tail cutoffs were fitted through September only; strict A>threshold, no OOS threshold selection. False-low is role-weighted mass of an event cohort with within-origin forecast midrank≤10.5 divided by total event mass, not a calibrated probability. Prefix95 has1089 rows/162 sessions; prefix99 has94/46. The three network arms' false-low rates are unchanged at17.30%/10.12%.

## 6. Scientific interpretation and Session3 decision

C1a's mean-level correction is real within F21: ratio0.769→1.050, while raw MSE falls6.89%. It is **not a uniformly better forecast**. Overall MAE rises5.89%; ordinary≤prefix95 MSE rises10.98%, and that ordinary mean ratio becomes1.246. Intraday MSE rises3.04% with ratio1.223. Overnight MSE falls9.66%, ratio0.719→0.968;15:30 MSE falls13.41% but its mean ratio remains0.869. A global average can hide offsetting ordinary/intraday overprediction and tail underprediction.

Prefix95/99 forecast mean ratios remain only0.373/0.235 for smearing, despite raw-MSE reductions19.48%/11.62%. Mean calibration therefore does not solve jump amplitudes or change magnitude ranking. M1 gives lower overall MSE than C1a and slightly lower overall MAE, with a similar ordinary-period trade-off. B0-VOL remains competitive, including at the95/99 tails and15:30. C1a's paired advantage over B0-VOL is inconclusive under the descriptive month-block interval. This does not establish a special Jensen-based mechanism or an architecture advantage.

Decision: **MIXED/INCONCLUSIVE, overall PARTIAL**. Review chronology and coverage before filling the three unavailable years. Do not automatically start O1, C1b/c, C2 flexible maps, C3 clock/overnight calibration, another seed, Stage2 overnight targets or options work. No result here authorizes a final-test release.

## 7. Reproduction, files and integrity

Result namespace: `reports/experiments/hf20_s9_mag_stage1_session2_designa_2026-10-27`.

```bash
.venv/bin/python -m lstm_data.hf20_mag_designa --report
.venv/bin/python -m pytest tests/test_hf20_mag_designa.py -q
```

The report command reuses saved calibration/OOS forecasts and frozen coefficients; it does not train or calibrate. The original --run is single-use and rejects the existing journal. Do not evade that guard with a new output directory. --preflight is for a fresh, pre-start namespace and requires the unchanged130-start predecessor; this completed namespace is not a continuation authorization.

Verification passed: four focused synthetic fixtures, original inner/OOS key/order equality, all20 names per origin, date/maturity/48-step masks, input-only scaler prefix exclusion, archived V2 parity before fitting, initial parameter identity, fresh empty optimizer, finite gradients/weights, frozen parameters for calibration+OOS, exact checkpoint reload, same baseline keys, positive finite outputs, and independent saved c/k/decoder/weight identities. No initial or refit failure/retry. Basic Pylance-stub parity and Ruff are recorded in the mandatory session report; final editor Problems refresh remains human-confirmed.

Execution used one pair/two neural phase fits and9 bounded non-neural coefficient fits (three grouped controls, three ridge candidates+one refit, c and k), plus the newly authorized September feature/target recipe statistics. The current ledger is131/200; old130-start history is byte-identical and bound by the new append-only neural_starts.jsonl. Only configs/CURRENT_EXPERIMENT_REGISTRY.json advanced to this successor. The prior campaign's permission is not reused. Actual lifecycle elapsed1072.43s; peak RSS1,244,594,176 bytes, under the existing2GB cap. Initial project storage12.41GB was below15GB; no bulk source copy.

S4 root `reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation`; S9 root `reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation`. Inputs were saved S4 opening_reaudit_v2 masks/endpoints/read receipt, timestamp/date-only P020 grid projection through2024, and174 explicit adjusted-hourly partitions2010-07–2024-12 from that existing permitted read receipt. Original FT16 and M2-as-of math was reused in memory. No minute store, 2025/2026 observations, protected hashes, acquisition or canonical rebuild was accessed. Fixed-survivor, retrospective action vintage and source/publication qualifications persist. The original price target begins before approximate origin+2-minute issuance: no executable returns, trading or options claims.

Small immutable protocol/recipe/coefficients and epoch trace are retained; F21/oos_scores.parquet is one compressed keyed store for all seven arms, F21/calibration_scores.parquet retains fitting-pair lineage. Selected initial/restricted checkpoints are private local files; .gitignore prevents accidental score/checkpoint commits. Main aggregates are session2_metrics.csv and session2_groups.csv. No existing model, prediction, source, index, recipe, dashboard or historical report was modified. Source code: src/lstm_data/hf20_mag_designa.py; tests: tests/test_hf20_mag_designa.py. Post-fit edits affected report presentation only, not fitting, forecast or metric definitions.

Mandatory handoff: reports/codex_sessions/2026-10-27_213331_hf20_s9_mag_session2_designa.md. No commits/push were performed. **STOP after Session2.**
