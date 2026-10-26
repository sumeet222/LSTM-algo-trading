# S2_FOUR_FOLD_LSTM_RANKING_COMPARISON

Retrospective OOS. LP DEFERRED_AFTER_PRIOR_FAILURE; constants undefined.

| year | model | daily_ic | pair_concordance | normalized_rank_mse | defined_origin_fraction |
| --- | --- | --- | --- | --- | --- |
| 2021 | NR | 0.01851629 | 0.5058931 | 0.7231936 | 1 |
| 2021 | T2R | 0.01379357 | 0.5052732 | 0.7266742 | 1 |
| 2022 | NR | -0.00988219 | 0.4963687 | 0.7441207 | 1 |
| 2022 | PW | 0.009431709 | 0.504044 | 0.7298896 | 1 |
| 2022 | T2R | 0.01179674 | 0.5035387 | 0.728147 | 1 |
| 2023 | NR | 0.01111004 | 0.5033126 | 0.7286551 | 1 |
| 2023 | PW | 0.01567839 | 0.5053644 | 0.7252891 | 1 |
| 2023 | T2R | 0.01844521 | 0.50547 | 0.7232502 | 1 |
| 2024 | NR | -0.01026601 | 0.4948798 | 0.7444052 | 1 |
| 2024 | PW | -0.01520033 | 0.4937118 | 0.7480407 | 1 |
| 2024 | T2R | -0.01334235 | 0.4942696 | 0.7466721 | 1 |

## Complete annual matrix, including the failed lifecycle

| year | T2R | NR | PW | LR | N1 | PW_status |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | 0.01379357 | 0.01851629 | nan | 0.0215872 | 0.01910849 | FAILED start65; no OOS model |
| 2022 | 0.01179674 | -0.00988219 | 0.009431709 | -0.002914377 | 0.002619969 | COMPLETED |
| 2023 | 0.01844521 | 0.01111004 | 0.01567839 | 0.01286957 | 0.01673101 | COMPLETED |
| 2024 | -0.01334235 | -0.01026601 | -0.01520033 | -0.007372565 | 0.00844253 | COMPLETED |

All12 authorized neural lifecycles were attempted,11 completed and1 failed. Starts63/64 F21T2R/NR completed; start65 F21PW remains FAILED during calibration epoch8, after7 complete saved epochs. It has no fresh refit/OOS model and is never filled by a partial checkpoint. Starts66–74 all completed. Final neural ledger74/200, not a count inferred from model folders. No retries/extra seeds/combinations.

Four-year dailyIC T2R0.00767329 versus NR0.00236953, deltaNR−T2R=−0.00530376. NR beats T2R in2021/2024 but loses in2022/2023; NR trails both LR and M1 in all four years. T2R beats LR in two years and loses in two; its mean edge0.00163084 is small and unstable. The simple M1 reference's mean0.01172550 exceeds both recurrent four-year means.

PW trails T2R in each of its three completed years. This is a matched2022–2024 descriptive statement, not a four-year PW mean or a completed four-year three-way experiment. PW beats NR in2022/2023 but loses in2024. Its missing2021 fold is a technical-comparability limitation, not a performance-selected omission.

400 whole-calendar-month resamples preserve daily sums/counts; annual NR−T2R and T2R−LR sensitivity intervals all span zero. These are dependence-aware descriptive intervals, not formal p-values/data-snooping corrections. Four retrospective years and one seed do not demonstrate reliable superiority or independent confirmation. No formal full-selection permutation/null or seed replication was authorized.

The objective comparison holds source/inputs, seed, architecture, optimizer, admissible dates and rank-led selector policy fixed. Actual selected durations differ as an intended consequence of that same policy. Comparing a nonlinear recurrent system to a linear model does not identify recurrence alone. Archived through2025 T2/42 predictions are not used as earlier-year OOS controls.

See paired_month_block_sensitivity.json, all_role_metrics.csv, complete_epoch_trace.csv, neural_selection_and_runtime.csv, PRIMARY_RESULTS.md, and TRAINING_AND_SELECTION_TRACE.md.
