# S4-A consolidated live-fit approval request

**Preparation complete. Eight neural starts remain NOT_RUN; ledger106/200.** The opening re-audit selects seven daily origins. No separate opening-price approval is requested.

Proposal SHA256 `971765111037fb649a7c5319e4a260223301a9bc8a80ce8621fe29e7061349f0`. Execution SHA256 `a737c9219513ddbbfffb882a2e76af7708e2f3ee55a297e1b145790bc47f2a95`.

The submitted instruction, Authorization boundary, states: “Before any real historical supervised fit or neural start, if the verified live repo requires one, submit one SHA-bound S4-A approval card”. The active CURRENT_EXPERIMENT_REGISTRY.json has `fit_permission=false` and `live_approval_required=true`; it binds completed S3 only. This is the one required consolidated fit checkpoint, not a new source-question gate.

Exactly the following order; no retries, combinations or extra fits:

1. `HF20-S4A-F21-H4-NR-S42` — start107.
2. `HF20-S4A-F21-H4-T2R-S42` — start108.
3. `HF20-S4A-F22-H4-NR-S42` — start109.
4. `HF20-S4A-F22-H4-T2R-S42` — start110.
5. `HF20-S4A-F23-H4-NR-S42` — start111.
6. `HF20-S4A-F23-H4-T2R-S42` — start112.
7. `HF20-S4A-F24-H4-NR-S42` — start113.
8. `HF20-S4A-F24-H4-T2R-S42` — start114.

Before neural starts: eight phase-prefix recipes and exactly eight P profile fits (four folds × inner/refit); N0, N1=M1 and N2 need no model fitting. Optional LR is omitted. Baseline and neural models use exactly the same role/stock/origin keys.

| Origin ET | Normal-session exit |
|---|---|
|09:30|13:30 same|
|10:30|14:30 same|
|11:30|15:30 same|
|12:30|10:00 next|
|13:30|11:00 next|
|14:30|12:00 next|
|15:30|13:00 next|

09:30 uses genuine minute OPEN, with completed09:30–09:31 bar and assumed09:32 issuance. Actual publication latency and opening-auction identity are unverified. It uses only previous48 completed full hours. 13:30 remains the exact normal-session endpoint. Other origins use the completed preceding-minute close. Calendar counting includes15:30–16:00; genuine final endpoints are mandatory, intermediate close is not.

All16 FT formulas remain unchanged. Expanded M2 has7 slot-specific past-return contexts, each locked at its historical input session start with original20/60 support/maturity rules. The new S4 training recipe weights these contexts equally1/7 instead of the archived two-context1/2 pooling; archived formulas/recipes/results remain immutable.

Hidden32/layer1/dropout0.1; AdamW0.001, betas0.9/0.999, epsilon1e-8, matrix decay0.01 /bias0; clip1;16whole-session batches; seed42; strict+0.001 validation IC,12–60epochs, patience10; fresh selected-epoch refit. Equal stocks/origin, origins/session and sessions/year; equal annual primary weight. Equal-category contrast is secondary.

| year | role | slot | candidates | origins | sessions | rows | retention | unavailable_inputs | unavailable_labels | embargo | unmatured_or_4h_purge | inner_stop | refit_stop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | inner_train | ALL | 16226 | 11449 | 2100 | 228980 | 0.705596 | 1587 | 3869 | 0 | 4 | 2020-06-30 | 2020-12-31 |
| 2021 | inner_validation | ALL | 890 | 674 | 120 | 13480 | 0.7573034 | 0 | 168 | 55 | 4 | 2020-06-30 | 2020-12-31 |
| 2021 | refit | ALL | 17116 | 12171 | 2227 | 243420 | 0.711089 | 1587 | 4037 | 0 | 4 | 2020-06-30 | 2020-12-31 |
| 2021 | oos | ALL | 1761 | 955 | 188 | 19100 | 0.5423055 | 421 | 479 | 55 | 4 | 2020-06-30 | 2020-12-31 |
| 2022 | inner_train | ALL | 17984 | 12716 | 2331 | 254320 | 0.707073 | 1743 | 4256 | 0 | 4 | 2021-06-30 | 2021-12-31 |
| 2022 | inner_validation | ALL | 893 | 457 | 92 | 9140 | 0.5117581 | 265 | 260 | 55 | 4 | 2021-06-30 | 2021-12-31 |
| 2022 | refit | ALL | 18877 | 13173 | 2423 | 263460 | 0.6978333 | 2008 | 4516 | 0 | 4 | 2021-06-30 | 2021-12-31 |
| 2022 | oos | ALL | 1754 | 1180 | 210 | 23600 | 0.672748 | 258 | 324 | 55 | 4 | 2021-06-30 | 2021-12-31 |
| 2023 | inner_train | ALL | 19745 | 13896 | 2547 | 277920 | 0.7037731 | 2008 | 4659 | 0 | 4 | 2022-06-30 | 2022-12-30 |
| 2023 | inner_validation | ALL | 886 | 453 | 86 | 9060 | 0.5112867 | 258 | 181 | 55 | 4 | 2022-06-30 | 2022-12-30 |
| 2023 | refit | ALL | 20631 | 14395 | 2640 | 287900 | 0.6977364 | 2266 | 4840 | 0 | 4 | 2022-06-30 | 2022-12-30 |
| 2023 | oos | ALL | 1744 | 887 | 187 | 17740 | 0.5086009 | 383 | 582 | 55 | 4 | 2022-06-30 | 2022-12-30 |
| 2024 | inner_train | ALL | 21499 | 14945 | 2740 | 298900 | 0.6951486 | 2421 | 5072 | 0 | 4 | 2023-06-30 | 2023-12-29 |
| 2024 | inner_validation | ALL | 876 | 350 | 87 | 7000 | 0.3995434 | 228 | 350 | 56 | 4 | 2023-06-30 | 2023-12-29 |
| 2024 | refit | ALL | 22375 | 15332 | 2835 | 306640 | 0.6852291 | 2649 | 5422 | 0 | 4 | 2023-06-30 | 2023-12-29 |
| 2024 | oos | ALL | 1755 | 991 | 208 | 19820 | 0.5646724 | 274 | 567 | 55 | 4 | 2023-06-30 | 2023-12-29 |


Minimum50validation sessions and25observations per slot pass. Existing99%defined OOS IC coverage is retained as a report-support gate, not evidence of positive edge. A constant-score/undefined-IC result is preserved, never jittered or rescued.

**Resource request:** explicitly apply2.5GB task /15GB project /2GB process RAM to S4;CPU4/1,0workers. S3-only resource permission is not silently reused. Planning2–10h; actual duration depends on selected epochs. Check limits before fits and during epochs; preserve artifacts and stop on breach.

Evidence: [opening audit](opening_reaudit_v2/S4_0930_REAUDIT.md), [all role/slot populations](opening_reaudit_v2/S4_FOLD_ROLE_SLOT_COUNTS.csv), [zero-step eight-workflow receipt](opening_reaudit_v2/S4_ZERO_STEP_WORKFLOW_REHEARSAL.json), [historical report](HISTORICAL_S1_S2_RANKING_VISUAL_DIAGNOSTICS.md), [readiness](S4_CLOCK_AND_ELIGIBILITY_AUDIT.md). No new empirical result exists yet.
