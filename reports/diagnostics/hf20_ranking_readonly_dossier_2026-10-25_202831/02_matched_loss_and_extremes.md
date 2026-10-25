# 02 — Matched loss and heavy-tail attribution

**PASS for exact saved four-role T2/42–A7/A12 comparisons; scientific conclusions exploratory.**

All findings are descriptive. Inner training/refit are in sample; inner validation is selection-influenced; development is 109 repeatedly inspected sessions, not confirmation. No new model, objective fit, labels, inference or trading.


## Exact four-role quantities

| role | model | rows | mse | z_mse | daily_ic |
| --- | --- | --- | --- | --- | --- |
| inner_train | T2_S42 | 88560 | 4.141503593 | 1.327756193 | 0.06869564222 |
| inner_train | A7 | 88560 | 4.139654586 | 1.326602853 | 0.07468954452 |
| inner_train | A12 | 88560 | 4.140175868 | 1.327076359 | 0.07221790405 |
| inner_validation | T2_S42 | 15320 | 3.652177634 | 1.312833705 | 0.01511319346 |
| inner_validation | A7 | 15320 | 3.650002908 | 1.311444832 | 0.02463450242 |
| inner_validation | A12 | 15320 | 3.650648282 | 1.311887599 | 0.02075720391 |
| refit | T2_S42 | 104200 | 4.055393999 | 1.324015512 | 0.06817597297 |
| refit | A7 | 104200 | 4.052234116 | 1.322188539 | 0.07401140935 |
| refit | A12 | 104200 | 4.053759667 | 1.322983837 | 0.07227705568 |
| development | T2_S42 | 3660 | 3.106560016 | 1.281044206 | 0.07555944626 |
| development | A7 | 3660 | 3.105712862 | 1.282083732 | 0.06053632545 |
| development | A12 | 3660 | 3.105433252 | 1.281777317 | 0.06569613042 |


| phase | epsilon | scale | train_frozen_event_p95 | train_frozen_event_p99 | frozen_recipe_path | frozen_recipe_sha256 |
| --- | --- | --- | --- | --- | --- | --- |
| inner | 0.0003297043193 | 0.90640683 | 3.919022661 | 7.350173695 | reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122/train_only_fit_recipes.json | d6c394bebb35131522d05c2b91b33347cfadb4e3204a8a4525b60cd9305ababc |
| refit | 0.000334640211 | 0.9057319697 | 3.885302874 | 7.265029595 | reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122/train_only_fit_recipes.json | d6c394bebb35131522d05c2b91b33347cfadb4e3204a8a4525b60cd9305ababc |


Saved predictions are joined one-to-one on role/phase, session, origin and the frozen20-ticker order. Zero duplicates/missing keys. Each comparison keeps its actual calibration or refit checkpoint SHA, original64-bit TG20, raw saved32-bit z output and actual phase recipe. No later checkpoint is substituted. `four_role_metrics.csv` records checkpoint IDs. Training scales/floors are reused at full precision.

Weights are equal session→admitted origin within session→20stocks. Original loss is (Y−p)^2. Actual objective allocation uses torch float32 asinh(float32(Y)/s) and float32 squared residuals; it is not an arbitrary float64 z surrogate. Inverse s*sinh(raw_z) is checked once at the existing rtol7e−7/atol1e−7; original target operands use1e−11/1e−12; P028 aggregate z uses its existing5e−7/1e−8, original MSE1e−13 and IC1e−12. No tolerance was loosened. [metric_reconciliation.csv](metric_reconciliation.csv) reconciles all8 candidate-role pairs and P028 top1/top5 transformed contributions.

## Development signed attribution: candidate minus T2

| model | cohort | rows | weight_mass | y_delta | z_delta | y_fraction_total_change |
| --- | --- | --- | --- | --- | --- | --- |
| A7 | ALL | 3660 | 1 | -0.0008471539485 | 0.001039526951 | 1 |
| A7 | TARGET_TOP5 | 183 | 0.0497706422 | -0.004164826593 | -0.001786003255 | 4.916257075 |
| A7 | TARGET_TOP5_COMPLEMENT | 3477 | 0.9502293578 | 0.003317672644 | 0.002825530206 | -3.916257075 |
| A7 | NUM_ONLY_5 | 179 | 0.04541284404 | -0.003031011639 | -0.001271165497 | 3.577875832 |
| A7 | MAD_ONLY_5 | 176 | 0.0495412844 | -0.0008075406313 | -0.0004145926583 | 0.9532395295 |
| A7 | BOTH_5 | 4 | 0.0009174311927 | 0.0001861379014 | 6.05881761e-05 | -0.2197214588 |
| A7 | NEITHER_5 | 3301 | 0.9041284404 | 0.00280526042 | 0.002664696931 | -3.311393903 |
| A12 | ALL | 3660 | 1 | -0.001126763555 | 0.0007331112586 | 1 |
| A12 | TARGET_TOP5 | 183 | 0.0497706422 | -0.004462623485 | -0.001987532519 | 3.960567826 |
| A12 | TARGET_TOP5_COMPLEMENT | 3477 | 0.9502293578 | 0.003335859929 | 0.002720643778 | -2.960567826 |
| A12 | NUM_ONLY_5 | 179 | 0.04541284404 | -0.002454012217 | -0.0009677465492 | 2.177930059 |
| A12 | MAD_ONLY_5 | 176 | 0.0495412844 | -0.000963883617 | -0.0004792080896 | 0.8554444385 |
| A12 | BOTH_5 | 4 | 0.0009174311927 | 0.000177264418 | 5.830001394e-05 | -0.1573217532 |
| A12 | NEITHER_5 | 3301 | 0.9041284404 | 0.002113867861 | 0.002121765884 | -1.876052745 |


Negative loss deltas favor the candidate. Fractions may exceed1 or be negative because improvements and degradations cancel. A7's target-top5 original-loss change is−0.004165 against+0.003318 in its complement; A12 is−0.004463 against+0.003336. Thus the small net original-MSE gains are concentrated in original-target extremes and offset elsewhere. Both models have worse aggregate actual z-loss and lower ranking IC than T2 on development. This supports a narrow descriptive magnitude-error trade-off, not reliable extreme-event prediction or alpha.

## Cohort definitions and conservation

`matched_loss_cohorts.csv` contains all4roles×3models: stable original-target top1/top5 with exact complements; stable own original-error/z-error top1/top5 and complements; T2-error selections evaluated on the identical candidate rows; positive/negative/zero targets; training-frozen95/99 outcome events split ABS/POS/NEG; percentages-of-training-maximum; floor support; and state/quality/fallback strata. Each entry reports row/session/origin counts, weight mass, weighted and conditional losses, signed deltas and share of total change. Own-model error cohorts are explicitly different populations and must not be used to claim paired cohort superiority across models; the T2-selected error cohorts provide a fixed paired reference.

P028 target/numerator topK is floor(nrows×p); ties are broken by origin and frozen ticker order. Small-MAD selections rank unique origins, then retain all20 stocks. NUM_ONLY/MAD_ONLY/BOTH/NEITHER are disjoint within each1%/5% role-ranked selection and conserve loss exactly. These role-specific ranks are diagnostic, not newly fitted predictive thresholds. They are distinct from `P020_FROZEN_*` flags based on P020's existing training diagnostic thresholds in the joined populations. Exact P028 thresholds remain linked in each role's archived thresholds.json; training event thresholds are in phase_thresholds.csv.

A ranked top5 target set is not the numerator/MAD union.95%/99%-of-maximum ranges are not95th/99th quantiles. Floor support MAD≤epsilon is empty in the archived roles; this does not justify a floor change. Original TG20 tail observations are retained unaltered. [extreme_examples.csv](extreme_examples.csv) identifies large-numerator-only, small-MAD-only, both and neither witnesses in each role, with original and actual-z errors on the same rows. Genuine candle provenance and22-preserved-case verification are separate referenced evidence; not every loss-selected row is claimed as a newly replayed full source case.

[matched_stock_quality_strata.csv](matched_stock_quality_strata.csv) provides disaggregated ticker/state/quality loss deltas; `ranking_periods.csv` provides date/origin groups. No subset is excluded and no threshold is selected from development. Loss concentration is not gradient influence. Existing P028 gradient and mechanism reports are reused; no new backward pass.
