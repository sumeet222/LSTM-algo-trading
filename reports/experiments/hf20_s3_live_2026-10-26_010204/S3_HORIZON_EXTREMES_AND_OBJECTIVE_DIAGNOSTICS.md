# Original-target extremes and actual objective diagnostics

Every accepted model has inner_train, inner_validation, refit and oos scores, cohorts, prior-fit thresholds, tail_energy, tail_strata, tail_pairs and extreme_examples. See DIAGNOSTIC_FILE_INDEX.csv for every path/hash.

S3_ALL_ROLE_TAIL_ENERGY_AND_NUM_MAD.csv records original-Y stable top1/5%, ordinary complements, prior 95/99% events, positive/negative events, NUM_ONLY/MAD_ONLY/BOTH/NEITHER and floor cohorts. Role cohorts.csv additionally separates error-ranked top1/5% and complements. These definitions are distinct.

T2R optimizes float32 asinh-target squared error; Z_actual_float32 records that target. Original Y error is a once-inverse diagnostic. Energy = target energy + forecast energy − alignment; subset error = common + centered + cross term. All identities and disjoint objective partitions are asserted. NR/P/LR retain rank-score units, with no invented return MSE.

## Measured equal-year OOS attribution

Shares below divide equal-year mean contributions by equal-year mean total loss; they are not averages of yearly percentages. Original-MSE cells are unavailable for ordinal NR. Target-ranked tails, numerator/MAD categories and floor flags overlap and must not be added together. NUM_ONLY/MAD_ONLY/BOTH/NEITHER alone form a disjoint partition.

| stage | horizon | model | cohort | weight_mass | actual_objective_share | original_MSE_share |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1 | NR | BOTH | 0.0001579886 | 0.0004634426 | nan |
| A | 1 | NR | FLOOR | 0 | 0 | nan |
| A | 1 | NR | MAD_ONLY | 0.02307583 | 0.02269598 | nan |
| A | 1 | NR | NUM_ONLY | 0.06117949 | 0.1477082 | nan |
| A | 1 | NR | TARGET_RANK_TOP1 | 0.009950914 | 0.02644358 | nan |
| A | 1 | NR | TARGET_RANK_TOP5 | 0.04984348 | 0.1260222 | nan |
| A | 1 | T2R | BOTH | 0.0001579886 | 0.00125817 | 0.005726379 |
| A | 1 | T2R | FLOOR | 0 | 0 | 0 |
| A | 1 | T2R | MAD_ONLY | 0.02307583 | 0.02576938 | 0.0299044 |
| A | 1 | T2R | NUM_ONLY | 0.06117949 | 0.231998 | 0.4600953 |
| A | 1 | T2R | TARGET_RANK_TOP1 | 0.009950914 | 0.06530232 | 0.247805 |
| A | 1 | T2R | TARGET_RANK_TOP5 | 0.04984348 | 0.2308134 | 0.5048829 |
| A | 2 | NR | BOTH | 0.0006638623 | 0.001722503 | nan |
| A | 2 | NR | FLOOR | 0 | 0 | nan |
| A | 2 | NR | MAD_ONLY | 0.03002918 | 0.0288567 | nan |
| A | 2 | NR | NUM_ONLY | 0.05698269 | 0.1375974 | nan |
| A | 2 | NR | TARGET_RANK_TOP1 | 0.009769385 | 0.02611177 | nan |
| A | 2 | NR | TARGET_RANK_TOP5 | 0.049858 | 0.1256753 | nan |
| A | 2 | T2R | BOTH | 0.0006638623 | 0.005141417 | 0.02445558 |
| A | 2 | T2R | FLOOR | 0 | 0 | 0 |
| A | 2 | T2R | MAD_ONLY | 0.03002918 | 0.03491228 | 0.03936538 |
| A | 2 | T2R | NUM_ONLY | 0.05698269 | 0.2190697 | 0.4464644 |
| A | 2 | T2R | TARGET_RANK_TOP1 | 0.009769385 | 0.0665929 | 0.2709439 |
| A | 2 | T2R | TARGET_RANK_TOP5 | 0.049858 | 0.2328955 | 0.5229333 |
| B | 1 | NR | BOTH | 0.0001579886 | 0.000459425 | nan |
| B | 1 | NR | FLOOR | 0 | 0 | nan |
| B | 1 | NR | MAD_ONLY | 0.02307583 | 0.02265937 | nan |
| B | 1 | NR | NUM_ONLY | 0.06117949 | 0.1477141 | nan |
| B | 1 | NR | TARGET_RANK_TOP1 | 0.009950914 | 0.02651438 | nan |
| B | 1 | NR | TARGET_RANK_TOP5 | 0.04984348 | 0.1258824 | nan |
| B | 1 | T2R | BOTH | 0.0001579886 | 0.001315743 | 0.005788075 |
| B | 1 | T2R | FLOOR | 0 | 0 | 0 |
| B | 1 | T2R | MAD_ONLY | 0.02307583 | 0.02577578 | 0.02991266 |
| B | 1 | T2R | NUM_ONLY | 0.06117949 | 0.2321048 | 0.4602301 |
| B | 1 | T2R | TARGET_RANK_TOP1 | 0.009950914 | 0.06540286 | 0.2479358 |
| B | 1 | T2R | TARGET_RANK_TOP5 | 0.04984348 | 0.2308859 | 0.5050099 |
| B | 2 | NR | BOTH | 0.0006638623 | 0.00173464 | nan |
| B | 2 | NR | FLOOR | 0 | 0 | nan |
| B | 2 | NR | MAD_ONLY | 0.03002918 | 0.02884366 | nan |
| B | 2 | NR | NUM_ONLY | 0.05698269 | 0.1374582 | nan |
| B | 2 | NR | TARGET_RANK_TOP1 | 0.009769385 | 0.02630814 | nan |
| B | 2 | NR | TARGET_RANK_TOP5 | 0.049858 | 0.1259367 | nan |
| B | 2 | T2R | BOTH | 0.0006638623 | 0.005213068 | 0.02454937 |
| B | 2 | T2R | FLOOR | 0 | 0 | 0 |
| B | 2 | T2R | MAD_ONLY | 0.03002918 | 0.03503379 | 0.03947872 |
| B | 2 | T2R | NUM_ONLY | 0.05698269 | 0.2182847 | 0.4461681 |
| B | 2 | T2R | TARGET_RANK_TOP1 | 0.009769385 | 0.06635927 | 0.2709775 |
| B | 2 | T2R | TARGET_RANK_TOP5 | 0.049858 | 0.2332213 | 0.5233553 |


S3_EQUAL_YEAR_ROLE_TAIL_ATTRIBUTION.csv includes every role, ordinary complements, positive/negative tails, training-threshold events, target/forecast energy, alignment, and exact common/centered/subset-cross terms. Counts there are yearly means; exact integer counts are in S3_ALL_ROLE_TAIL_ENERGY_AND_NUM_MAD.csv and each role file. Paired A/B actual loss, normalized-rank error, IC, concordance and top/bottom retrieval are in S3_AB_PAIRED_ROLE_LOSS_AND_RETRIEVAL.csv. OOS stock/slot/month/quality slices are in S3_AB_PAIRED_OOS_STOCK_SLOT_MONTH_QUALITY.csv. Slice effects use equal sessions and equal rows within each session; they are conditional effects, not additive contributions. Whole-origin IC/retrieval are deliberately blank for individual-stock and quality-row slices.


Final numerical reconciliation: whole-origin/slot/month paired losses reproduce inherited FP32 origin reductions before session aggregation. Stock/quality slices retain conditional row loss. All 416 primary-role metric deltas match saved A/B metrics at rtol=atol=1e-12 (READ_ONLY_CLOSEOUT_FINAL_CHECKS.json). Original model outputs and gate tolerances are unchanged. Initial draft paired tables remain explicitly archived in paired_report_initial_float64_rank_aggregation/; use the top-level paired tables.
