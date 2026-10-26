# Detailed partial extreme-value and objective diagnostics

**F21 P/LR inner training and validation only. Full four-fold/neural diagnostics NOT_RUN.** No LP coefficients or losses survived, and no return-output T2R was trained. There is no meaningful new asinh training loss, original TG20 prediction error or neural gradient analysis to report. NR/PW were not run. No ordinal score is inverted with sinh.

All four keyed saved score tables preserve raw four-hour returns, future20-stock median, numerator, MAD, phase epsilon, Y, Z, q, score, normalized predicted rank, actual point-loss allocation, weights, source-age/fallback/proxy flags and source/recipe/coefficient hashes. Future label quantities are diagnostic/target operands only, never inputs.

## Original-target tails and NUM/MAD conservation

The table below uses weighted-mean actual rank-regression loss, not original-target MSE. Weight mass and objective share differ from raw row fraction because sessions and their admitted origins have equal hierarchical weights. Top1/5 cohorts sort |Y| deterministically with canonical key ties; complements retain every ordinary row. TRAIN_EVENT95/99 and NUM/MAD thresholds use the applicable earlier training population. NUM_ONLY/MAD_ONLY/BOTH/NEITHER are disjoint and sum back to ALL. Additional positive/negative and optimized-error cohorts are preserved in the complete CSV.

| model | role | cohort | rows | origins | sessions | weight_mass | actual_objective_contribution | objective_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LR | inner_train | ALL | 70200 | 3510 | 1982 | 1 | 0.36498912 | 1 |
| LR | inner_train | TRAIN_EVENT95 | 3510 | 2161 | 1491 | 0.049886478 | 0.04595399 | 0.1259051 |
| LR | inner_train | TRAIN_EVENT99 | 702 | 631 | 504 | 0.010015136 | 0.0097762648 | 0.026785086 |
| LR | inner_train | FLOOR | 0 | 0 | 0 | 0 | 0 | 0 |
| LR | inner_train | NUM_ONLY | 3442 | 1910 | 1286 | 0.04756559 | 0.041815295 | 0.11456587 |
| LR | inner_train | MAD_ONLY | 3452 | 176 | 165 | 0.051463169 | 0.018204069 | 0.04987565 |
| LR | inner_train | BOTH | 68 | 55 | 52 | 0.0010090817 | 0.0010283379 | 0.002817448 |
| LR | inner_train | NEITHER | 63238 | 3334 | 1939 | 0.89996216 | 0.30394141 | 0.83274104 |
| LR | inner_train | TARGET_RANK_TOP1 | 702 | 631 | 504 | 0.010015136 | 0.0097762648 | 0.026785086 |
| LR | inner_train | TARGET_RANK_TOP1_COMPLEMENT | 69498 | 3510 | 1982 | 0.98998486 | 0.35521285 | 0.97321491 |
| LR | inner_train | TARGET_RANK_TOP5 | 3510 | 2161 | 1491 | 0.049886478 | 0.04595399 | 0.1259051 |
| LR | inner_train | TARGET_RANK_TOP5_COMPLEMENT | 66690 | 3510 | 1982 | 0.95011352 | 0.31903513 | 0.8740949 |
| LR | inner_validation | ALL | 3940 | 197 | 115 | 1 | 0.36963089 | 1 |
| LR | inner_validation | TRAIN_EVENT95 | 189 | 111 | 80 | 0.046086957 | 0.042357051 | 0.11459283 |
| LR | inner_validation | TRAIN_EVENT99 | 29 | 26 | 22 | 0.007173913 | 0.0071366702 | 0.019307559 |
| LR | inner_validation | FLOOR | 0 | 0 | 0 | 0 | 0 | 0 |
| LR | inner_validation | NUM_ONLY | 324 | 144 | 95 | 0.079565217 | 0.068885539 | 0.18636305 |
| LR | inner_validation | MAD_ONLY | 18 | 1 | 1 | 0.0039130435 | 0.0012031095 | 0.0032548942 |
| LR | inner_validation | BOTH | 2 | 1 | 1 | 0.00043478261 | 0.00041105074 | 0.0011120573 |
| LR | inner_validation | NEITHER | 3596 | 196 | 115 | 0.91608696 | 0.29913119 | 0.80927 |
| LR | inner_validation | TARGET_RANK_TOP1 | 39 | 35 | 30 | 0.0093478261 | 0.0092372179 | 0.024990384 |
| LR | inner_validation | TARGET_RANK_TOP1_COMPLEMENT | 3901 | 197 | 115 | 0.99065217 | 0.36039367 | 0.97500962 |
| LR | inner_validation | TARGET_RANK_TOP5 | 197 | 115 | 82 | 0.047826087 | 0.043894439 | 0.11875208 |
| LR | inner_validation | TARGET_RANK_TOP5_COMPLEMENT | 3743 | 197 | 115 | 0.95217391 | 0.32573645 | 0.88124792 |
| P | inner_train | ALL | 70200 | 3510 | 1982 | 1 | 0.3680672 | 1 |
| P | inner_train | TRAIN_EVENT95 | 3510 | 2161 | 1491 | 0.049886478 | 0.046756942 | 0.12703371 |
| P | inner_train | TRAIN_EVENT99 | 702 | 631 | 504 | 0.010015136 | 0.0098958149 | 0.026885891 |
| P | inner_train | FLOOR | 0 | 0 | 0 | 0 | 0 | 0 |
| P | inner_train | NUM_ONLY | 3442 | 1910 | 1286 | 0.04756559 | 0.042808197 | 0.11630538 |
| P | inner_train | MAD_ONLY | 3452 | 176 | 165 | 0.051463169 | 0.018326581 | 0.049791399 |
| P | inner_train | BOTH | 68 | 55 | 52 | 0.0010090817 | 0.00097917951 | 0.0026603281 |
| P | inner_train | NEITHER | 63238 | 3334 | 1939 | 0.89996216 | 0.30595325 | 0.83124289 |
| P | inner_train | TARGET_RANK_TOP1 | 702 | 631 | 504 | 0.010015136 | 0.0098958149 | 0.026885891 |
| P | inner_train | TARGET_RANK_TOP1_COMPLEMENT | 69498 | 3510 | 1982 | 0.98998486 | 0.35817139 | 0.97311411 |
| P | inner_train | TARGET_RANK_TOP5 | 3510 | 2161 | 1491 | 0.049886478 | 0.046756942 | 0.12703371 |
| P | inner_train | TARGET_RANK_TOP5_COMPLEMENT | 66690 | 3510 | 1982 | 0.95011352 | 0.32131026 | 0.87296629 |
| P | inner_validation | ALL | 3940 | 197 | 115 | 1 | 0.36840242 | 1 |
| P | inner_validation | TRAIN_EVENT95 | 189 | 111 | 80 | 0.046086957 | 0.04298075 | 0.11666794 |
| P | inner_validation | TRAIN_EVENT99 | 29 | 26 | 22 | 0.007173913 | 0.0070881393 | 0.019240209 |
| P | inner_validation | FLOOR | 0 | 0 | 0 | 0 | 0 | 0 |
| P | inner_validation | NUM_ONLY | 324 | 144 | 95 | 0.079565217 | 0.069165459 | 0.18774432 |
| P | inner_validation | MAD_ONLY | 18 | 1 | 1 | 0.0039130435 | 0.0012136215 | 0.003294282 |
| P | inner_validation | BOTH | 2 | 1 | 1 | 0.00043478261 | 0.00039778372 | 0.0010797533 |
| P | inner_validation | NEITHER | 3596 | 196 | 115 | 0.91608696 | 0.29762555 | 0.80788165 |
| P | inner_validation | TARGET_RANK_TOP1 | 39 | 35 | 30 | 0.0093478261 | 0.0093109408 | 0.025273832 |
| P | inner_validation | TARGET_RANK_TOP1_COMPLEMENT | 3901 | 197 | 115 | 0.99065217 | 0.35909147 | 0.97472617 |
| P | inner_validation | TARGET_RANK_TOP5 | 197 | 115 | 82 | 0.047826087 | 0.04450755 | 0.12081232 |
| P | inner_validation | TARGET_RANK_TOP5_COMPLEMENT | 3743 | 197 | 115 | 0.95217391 | 0.32389487 | 0.87918768 |

On LR inner validation, original-|Y| top1% contains39 rows and contributes about2.50% of actual ordinal score loss; top5% contains197 rows and contributes about11.88%. Their ordinary complements contribute the rest. NUM_ONLY contributes about18.64%, MAD_ONLY0.33%, BOTH0.11%, NEITHER80.93%; these are descriptive loss attribution, not a causal feature explanation. Denominator-floor activity is0 rows in that validation population. No tail-based exclusion or new threshold was applied.

The optimized-error cohorts differ from original-target extremes and are explicitly labeled in `partial_all_cohorts.csv`. These ordinal-loss shares cannot be compared as identical units with archived T2/A7/A12 asinh or original-MSE shares. Earlier A7/A12 contextual findings are preserved and confer no model promotion here.

## Complete tables and source examples

- [All partial cohorts](partial_all_cohorts.csv): all/ordinary complements, signed events, true objective shares, predicted-rank errors and floor/NUM/MAD counts for all four saved role/model combinations.
- [Stock/month/quality/fallback concentration](partial_tail_stock_month_quality.csv): cohort rows/origins/sessions/weight mass and actual objective contributions, including all20 tickers where present. Month groups are descriptive; no independence/significance inference.
- [Top1% original-target examples](partial_extreme_examples.csv): exact keys and existing source/age/clock/provenance fields for both selected models and roles. These are diagnostic row examples, not new genuine minute-window certifications.
- [Selected-model metrics](partial_selected_model_metrics.csv): rank IC, concordance, score spread/ties/retrieval and actual loss; four complete metric JSONs remain in parent model folders.
- Parent `F21_S1_{P,LR}/inner_{train,validation}_origins.csv`, `_month.csv`, `_slot.csv`, `_stock_quality.csv`, `_thresholds.json` and `_cohorts.csv` contain the full existing diagnostics.
- [Independent reconciliation](partial_output_reconciliation.csv) verifies exact admitted keys, hierarchical weights, independent IC and objective/complement/NUM–MAD conservation for all four outputs.

No source replay or neural weights were invented to fill the missing portions. Pairwise endpoint loss/oracle checks passed in synthetic preflight, but actual fitted LP pair-type diagnostics are unavailable because that fit failed before saving an accepted scorer.
