# S3 final research decision

**Technical stages: PASS. Scientific interpretation: QUALIFIED / EXPLORATORY.** All 72 authorized non-neural attempts and 32 neural starts completed, with zero new failed starts or retries. Ledger: **74 → 106 / 200**. S3-A passed before S3-B started. No protected 2026 numerical access, 2025 tuning, extra model, trading simulation or Git publication occurred.

## Research conclusion

Shorter horizons alone do **not** show a robust neural improvement. On secondary common evaluation keys, T2R IC is 0.007222 / −0.000707 / 0.014836 for h1/h2/h4, and NR is 0.008443 / 0.005232 / 0.010354. Historical stock-profile baseline P is stronger at h1/h2 (0.016350 / 0.011674) than at h4 (0.006949). This is useful baseline context, not evidence that a shorter-horizon LSTM is superior.

Horizon-aligned M2 merits **bounded further research**, most clearly h2 T2R: B−A IC is +0.015958 on its primary population, positive in all four years, and +0.011140 on common keys. Its primary optimized loss falls by 0.004185 and original-TG20 MSE by 0.005181. The resulting absolute primary IC is still only 0.004283. The 400 whole-month descriptive interval for the primary IC difference is [−0.000770, 0.029417], including zero. This is neither confirmatory evidence nor permission for another experiment.

For h1 NR, the primary gain +0.009197 shrinks to +0.001548 on common keys. h1 T2R has a small primary IC gain (+0.001535) but slightly worse actual loss (+0.000175). h2 NR's primary IC gain (+0.002543) reverses on common keys (−0.001072), and its primary actual loss increases (+0.000621). Every B−A equal-year descriptive IC interval includes zero; no post-search significance claim is made.

## S3-A yearly Rank IC: strictly matched evaluation

Origins are equally weighted within session, sessions within year, and the four years equally in the final column. N1 is the naive M1 control; N2 reverses it. N0 IC is undefined, not zero. Fitting populations remain horizon-specific: identical evaluation keys do not imply identical training populations. Four-hour scores and recipes are unchanged archived references, not new fits.

| model | horizon | 2021 | 2022 | 2023 | 2024 | equal_year |
| --- | --- | --- | --- | --- | --- | --- |
| LR | 1 | 0.006611999 | 0.01489743 | 0.0231159 | -0.020474 | 0.006037833 |
| LR | 2 | -0.007394914 | -0.0003035539 | 0.04678653 | -0.03581241 | 0.0008189123 |
| LR | 4 | 0.01949689 | 0.01078853 | 0.01131089 | -0.01182765 | 0.007442164 |
| N1 | 1 | -0.008462292 | 0.01377388 | 0.03333744 | 0.001438861 | 0.01002197 |
| N1 | 2 | 0.01138066 | -0.003528604 | 0.00272336 | 0.0003901795 | 0.002741398 |
| N1 | 4 | 0.0004236052 | 0.01700851 | 0.002288699 | 0.002871677 | 0.005648122 |
| N2 | 1 | 0.008462292 | -0.01377388 | -0.03333744 | -0.001438861 | -0.01002197 |
| N2 | 2 | -0.01138066 | 0.003528604 | -0.00272336 | -0.0003901795 | -0.002741398 |
| N2 | 4 | -0.0004236052 | -0.01700851 | -0.002288699 | -0.002871677 | -0.005648122 |
| NR | 1 | 0.006001309 | 0.007843056 | 0.03088899 | -0.01096032 | 0.008443261 |
| NR | 2 | -0.0006726377 | 0.008924485 | 0.02088264 | -0.008207489 | 0.00523175 |
| NR | 4 | 0.02900421 | -0.01437955 | 0.02276561 | 0.004025448 | 0.01035393 |
| P | 1 | 0.02257127 | -0.007098142 | 0.01590021 | 0.03402837 | 0.01635043 |
| P | 2 | 0.008248585 | -0.02368188 | 0.03932004 | 0.02281113 | 0.01167447 |
| P | 4 | -0.0158726 | -0.005569225 | 0.02182413 | 0.02741469 | 0.006949248 |
| T2R | 1 | 0.01518036 | 0.009550156 | 0.0160644 | -0.01190578 | 0.007222284 |
| T2R | 2 | 0.002665832 | 0.0006117779 | 0.01101013 | -0.01711708 | -0.000707335 |
| T2R | 4 | 0.0115085 | 0.01161912 | 0.03602484 | 0.0001908618 | 0.01483583 |


## S3-A primary horizon-specific populations

| model | horizon | 2021 | 2022 | 2023 | 2024 | equal_year |
| --- | --- | --- | --- | --- | --- | --- |
| LR | 1 | -0.01341597 | 0.02153585 | 0.01093203 | -0.008650887 | 0.002600256 |
| LR | 2 | -0.007240157 | 0.008655202 | 0.003000654 | -0.0295641 | -0.006287101 |
| LR | 4 | 0.0215872 | -0.002914377 | 0.01286957 | -0.007372565 | 0.006042457 |
| N1 | 1 | -0.008511049 | 0.005595227 | 0.04428291 | -0.007135725 | 0.00855784 |
| N1 | 2 | 0.005102357 | -0.01182768 | 0.04376082 | -0.01195844 | 0.006269267 |
| N1 | 4 | 0.01910849 | 0.002619969 | 0.01673101 | 0.00844253 | 0.0117255 |
| N2 | 1 | 0.008511049 | -0.005595227 | -0.04428291 | 0.007135725 | -0.00855784 |
| N2 | 2 | -0.005102357 | 0.01182768 | -0.04376082 | 0.01195844 | -0.006269267 |
| N2 | 4 | -0.01910849 | -0.002619969 | -0.01673101 | -0.00844253 | -0.0117255 |
| NR | 1 | -0.002799737 | 0.008284329 | 0.02387483 | -0.01446043 | 0.003724749 |
| NR | 2 | -0.01888177 | 0.02208403 | -0.003056398 | -0.0141614 | -0.003503884 |
| NR | 4 | 0.01851629 | -0.00988219 | 0.01111004 | -0.01026601 | 0.002369531 |
| P | 1 | 0.004462933 | 0.00273972 | 0.01401219 | 0.01347791 | 0.00867319 |
| P | 2 | 0.008795312 | -0.03412231 | 0.03214428 | 0.03118034 | 0.009499406 |
| P | 4 | -0.02827002 | -0.007668944 | 0.01836232 | 0.02011702 | 0.0006350939 |
| T2R | 1 | 0.01914667 | 0.01287917 | 0.009732459 | -0.02318972 | 0.004642147 |
| T2R | 2 | -0.0151273 | 0.001969583 | -0.01119443 | -0.02234679 | -0.01167473 |
| T2R | 4 | 0.01379357 | 0.01179674 | 0.01844521 | -0.01334235 | 0.007673292 |


## S3-B primary yearly results

| model | horizon | 2021 | 2022 | 2023 | 2024 | equal_year |
| --- | --- | --- | --- | --- | --- | --- |
| NR | 1 | 0.02533538 | 0.005296658 | 0.03423785 | -0.01318242 | 0.01292187 |
| NR | 2 | -0.02254542 | 0.01883596 | 0.006192712 | -0.006326652 | -0.0009608485 |
| T2R | 1 | 0.01980658 | 0.000407621 | 0.02486296 | -0.02036804 | 0.006177281 |
| T2R | 2 | -0.004758836 | 0.02103383 | -0.002410299 | 0.003268424 | 0.00428328 |


## S3-B secondary common yearly results

| model | horizon | 2021 | 2022 | 2023 | 2024 | equal_year |
| --- | --- | --- | --- | --- | --- | --- |
| NR | 1 | 0.01905143 | 0.008828499 | 0.03458633 | -0.02250133 | 0.009991232 |
| NR | 2 | 0.002812886 | 0.003488535 | 0.03019287 | -0.01985549 | 0.0041597 |
| T2R | 1 | 0.0175826 | 0.000464772 | 0.03656444 | -0.01373646 | 0.01021884 |
| T2R | 2 | 0.007856369 | 0.01019007 | 0.02107878 | 0.002607332 | 0.01043314 |


## Matched B minus A

A/B have identical keys, stocks, target recipes, weights and clocks within horizon; only M2 differs. Positive IC deltas and negative loss deltas favor B. Never mix full-population A with common-population B.

| comparison | model | population | year | delta_ic | low | high | origins | sessions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B_MINUS_A_H1 | T2R | PRIMARY_HORIZON_SPECIFIC | EQUAL_YEAR | 0.001535135 | -0.01050447 | 0.01388071 | nan | nan |
| B_MINUS_A_H1 | T2R | SECONDARY_COMMON | EQUAL_YEAR | 0.002996551 | -0.00666134 | 0.0131244 | nan | nan |
| B_MINUS_A_H2 | T2R | PRIMARY_HORIZON_SPECIFIC | EQUAL_YEAR | 0.01595802 | -0.0007703241 | 0.02941688 | nan | nan |
| B_MINUS_A_H2 | T2R | SECONDARY_COMMON | EQUAL_YEAR | 0.01114047 | -0.007806012 | 0.02830477 | nan | nan |
| B_MINUS_A_H1 | NR | PRIMARY_HORIZON_SPECIFIC | EQUAL_YEAR | 0.009197117 | -0.003710527 | 0.02229882 | nan | nan |
| B_MINUS_A_H1 | NR | SECONDARY_COMMON | EQUAL_YEAR | 0.001547972 | -0.0151234 | 0.01948351 | nan | nan |
| B_MINUS_A_H2 | NR | PRIMARY_HORIZON_SPECIFIC | EQUAL_YEAR | 0.002543036 | -0.007314253 | 0.01312591 | nan | nan |
| B_MINUS_A_H2 | NR | SECONDARY_COMMON | EQUAL_YEAR | -0.00107205 | -0.01253379 | 0.01069203 | nan | nan |


## Extreme targets and the actual objective

Across A/B and h1/h2 OOS results, original-target top 5% rows account for **50.49–52.34% of original-TG20 MSE**, but only **23.08–23.32% of actual transformed T2R loss**. Top 1% shares are 24.78–27.10% and 6.53–6.66%, respectively. The ordinary top-5% complement contributes approximately 76.7–76.9% of transformed loss. The same original-target top 5% contributes about 12.57–12.60% of NR rank loss; NR has no manufactured original-return MSE.

NUM_ONLY accounts for 44.62–46.02% of original-target MSE, MAD_ONLY 2.99–3.95%, BOTH 0.57–2.45%, and the remainder is NEITHER. These training-threshold cohort associations are not a causal diagnosis or the same partition as ranked target tails. The floor cohort has zero OOS weight here, not necessarily in other roles or archived h4 data.

T2R equal-year forecast energy is small (0.001776–0.007757) relative to target energy (3.479436–3.560910). Reports preserve target energy + forecast energy − alignment and common-level + centered-vector + selected-subset cross-term identities. Original-Y tail dominance must not be confused with dominance of the optimized transformed objective. A once-inverted score is not an expected raw return.

## Support and clock qualifications

The 50-session validation minimum is unchanged: F24 h1/h2/h4 has 66/64/74 inner-validation sessions. The 42-session three-horizon intersection is secondary evaluation only, never checkpoint selection. [Actual role metrics](S3_ALL_ROLE_METRICS.csv) give all model/year/horizon/role counts. The frozen [support/retention/slot table](../hf20_s3_horizons_2026-10-26_000127_preparation/eligibility_amendment_v2/S3_HORIZON_ROLE_SUPPORT.csv) and [exclusion table](../hf20_s3_horizons_2026-10-26_000127_preparation/eligibility_amendment_v2/S3_EXCLUSION_REASON_COUNTS.csv) retain all reasons and denominators. Exports independently match those frozen role indices.

FT16 and 48-step inputs persist; B changes only M2. Genuine h-specific endpoints and source-basis rules are unchanged. The conservative four-hour admission purge/embargo remains for all horizons, distinct from each target's actual endpoint-plus-two-minute maturity. The witness audit verifies 4,224 historical M2 steps across 88 stage/horizon/event contexts, from 22 stock events, 20 origins and 13 sessions. The 176 model-stock-event replays are not 176 independent observations.

Historical publication availability, action vintage, retrospective surviving-stock selection and bounded private-use rights remain conditional, not independently certified. Returns start at the close two minutes before assumed issuance. These are price-only ranking labels, not certified executable returns; no P&L, costs, Sharpe or profitability claim is made.

## Verification and resource amendment

All 216 new saved-role exports independently reconstruct prices/returns, targets, keys, weights and objectives; all 64 A/B identities pass. All 5,846 old reference files except the explicitly authorized current-registry pointer, plus all 63 preparation-inventory files, retain their hashes. Old h4 artifacts remain unchanged.

Task cap **1 GB → 2.5 GB**, total project **10 GB → 15 GB**, RAM unchanged **2 GB**. Applied at the boundary after 12 completed models (ledger 86); the exact 20 unstarted models continued. The retained FATAL_STOP.json is the deliberate before-start journal-lock hold, **not a failed model**. No completed fit was restarted, and no scientific artifact was deleted or recompressed to meet a cap. Resource authority is separate from frozen science.

[WORK_SESSION_REPORT.md](WORK_SESSION_REPORT.md) records tests/static/resources, exact commands, and the post-training report-only performance and floating-point reduction reconciliations. Scientific gate tolerances and model outputs were unchanged.

## Complete diagnostics and analysis map

- [Every diagnostic, analysis file, checkpoint and receipt, with hashes](DIAGNOSTIC_FILE_INDEX.csv).
- [S3-A horizon comparison](S3A_HORIZON_ONLY_COMPARISON.md) and [S3-B aligned-M2 comparison](S3B_HORIZON_ALIGNED_M2.md).
- [Training, validation, refit and OOS diagnostics](S3_TRAINING_AND_FAILURE_TRACE.md).
- [Original-target extremes, transformed-objective errors, NUM/MAD and energy decomposition](S3_HORIZON_EXTREMES_AND_OBJECTIVE_DIAGNOSTICS.md).
- [Every role metric](S3_ALL_ROLE_METRICS.csv), [paired all-role losses/retrieval](S3_AB_PAIRED_ROLE_LOSS_AND_RETRIEVAL.csv), and [OOS stock/slot/month/quality slices](S3_AB_PAIRED_OOS_STOCK_SLOT_MONTH_QUALITY.csv).
- [All-role tail contributions](S3_ALL_ROLE_TAIL_ENERGY_AND_NUM_MAD.csv), [equal-year attribution](S3_EQUAL_YEAR_ROLE_TAIL_ATTRIBUTION.csv), and [paired horizon/A-B estimates](S3_MATCHED_HORIZON_AND_AB_DIFFERENCES.csv).
- [Historical M2 audit](S3_WITNESS_M2_HISTORY_VERIFICATION.json) and its [4,224 source-history rows](S3_WITNESS_M2_HISTORIES.parquet).
- [Portable interactive plot](S3_DIAGNOSTIC_OVERVIEW.html), [final verification](FINAL_VERIFICATION.json), and [session handoff](WORK_SESSION_REPORT.md).

The index includes every model's batches, per-parameter gradients, checkpoints, selected/raw-best epochs, full-role scores, thresholds, error-ranked and target-ranked tails, ordinary complements, pair/stratum tables, source examples, and the unchanged prior h4 diagnostic index. No further training is authorized.
