# S4-A clock, opening source and eligibility audit

**Decision: seven candidate daily origins on normal sessions, including 09:30. No S4 fit has begun.**

The [opening re-audit](opening_reaudit_v2/S4_0930_REAUDIT.md) distinguishes genuinely missing prices from unknown publication latency. The pinned source explicitly labels minute START times. A 09:30 row covers 09:30–09:31; its genuine OPEN is the 09:30 reference, while the bar completes by clock at 09:31. Assumed issuance at 09:32 is consistent with the existing price-only origin+2 proxy. It is neither certified real-time delivery nor a verified auction print. No 09:31 close replaces the start; the normal-session endpoint is exactly 13:30 using the 13:29 minute CLOSE.

The earlier six-origin draft imposed an extra two minutes after completion of the first minute. That was too strict for the accepted convention. It remains preserved with its source counts/logs, but the opening_reaudit_v2 population supersedes it before any S4 training.

All 20 stocks have observed first-minute bars. Across July 2010–December 2024, 3,062 of 3,650 candidate sessions have a complete 20-stock opening panel; 2,101 opening origins survive input/target eligibility. This is seven *candidate slots*, not seven guaranteed observations every day. Missing/quarantined genuine prices and input-quality failures still exclude the affected complete-panel observation. [All-stock/year coverage](opening_reaudit_v2/S4_0930_ALL20_SOURCE_COVERAGE.csv) and private fixed-date 20-stock exact-candle witnesses are retained.

## Clock and causal inputs

| Origin ET | Normal exit | Counter |
|---|---|---|
|09:30|13:30 same session|240 regular minutes|
|10:30|14:30 same session|240 regular minutes|
|11:30|15:30 same session|240 regular minutes|
|12:30|10:00 next regular session|210+30 minutes|
|13:30|11:00 next regular session|150+90 minutes|
|14:30|12:00 next regular session|90+150 minutes|
|15:30|13:00 next regular session|30+210 minutes|

The XNYS calendar supplies early closes, DST, holidays and weekends. The closing 30-minute stub counts toward the target clock, but is never fabricated into a full-hour LSTM step. A missing genuine 16:00 close prevents only the affected decomposition; valid direct origin-to-final-endpoint returns remain eligible. No endpoint is shifted or forward-filled.

Opening inputs are the previous 48 completed scheduled full-hour steps, ending normally at the preceding session's 15:30 endpoint. The unfinished 09:30–10:30 bar is excluded. The original 16 channels retain their prescribed historical-step lookbacks, 126-session/360-genuine-update warmup, close cap5 fallback and corporate-action dependency masks. No current opening price is added as a feature. Input eligibility is established independently of outcome magnitudes.

Expanded M2 preserves 20/60 scheduled regular-origin-day windows, 19/20 and 57/60 support, at most two consecutive missing observations, and maturity strictly before each historical input session's open. Current/future overnight outcomes remain unavailable. Seven slot contexts are pooled equally (1/7) only in the proposed new phase-prefix floor/scaler/fallback recipe; the original morning raw contexts still match, and archived recipes/results are unchanged.

## Measured support

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


All four inner-validation folds exceed the unchanged 50-session minimum: 120, 92, 86 and 87. Every slot has at least 41 validation origins, exceeding the frozen 25-origin support floor. Retention is measured against nominal scheduled candidates, including source/input exclusions and purge/embargo; OOS retention is about 51–67%, not full coverage. This selection conditions the estimand and must remain visible in every interpretation. [Every role × slot count, retention and exclusion reason](opening_reaudit_v2/S4_FOLD_ROLE_SLOT_COUNTS.csv) is available; reasons can overlap and must not be summed as disjoint counts.

No threshold has been relaxed. Labels must mature before their role cutoff; the inherited conservative four-hour boundary and 48-step cross-fold embargo also apply. Numerical source access ends December 2024. Calendar-only lookahead is used to identify unavailable next-year endpoints; no 2025 tuning and no protected 2026 file open or hash occurred.

## Independent evidence

- [348 explicitly permitted numerical source reads](opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv): 174 adjusted-hourly plus 174 canonical-minute monthly files, checked against existing hashes, no acquisition.
- [22 archived 48×16 tensor witnesses](opening_reaudit_v2/S4_ARCHIVED_ALL16_TENSOR_IDENTITY.csv): bitwise input identity under archived phase recipes; original source returns agree at atol1e-12/rtol1e-11.
- [119 independent scalar checks](opening_reaudit_v2/S4_ALL16_SCALAR_SOURCE_WITNESSES.csv): all 16 channels across seven contexts, plus seven source-native Q2 checks; atol/rtol1e-11, matching NaN fallback cases disclosed.
- [Seven-context native/fallback coverage](opening_reaudit_v2/S4_SHIFTED_FEATURE_COVERAGE.csv), [M2 history support](opening_reaudit_v2/S4_M2_SOURCE_SUPPORT.csv), [old morning key/target identity](opening_reaudit_v2/S4_OLD_ANCHOR_IDENTITY.json).
- [Eight-workflow zero-update rehearsal](opening_reaudit_v2/S4_ZERO_STEP_WORKFLOW_REHEARSAL.json): full role exports and exact checkpoint reloads, representative gradient batch per phase, blocked AdamW.step and new recipe fitting. Archived recipes are structural rehearsal inputs only, never claimed to be newly fitted S4 recipes.
- Synthetic calendar, opening-input future perturbation, rank/loss/weight arithmetic, strict selector, no-authority and sequential gate checks are in tests/test_hf20_s4_readonly.py. Loss oracles use FP32-appropriate rtol3e-7/atol1e-8; IC uses1e-12; no tolerances were loosened to fit empirical results.

The initial audit failures were engineering preflight issues (read-only NumPy assignment, and requiring a native Q2 value on a fixed missing-source date). Their logs and initial fixed-date witnesses are preserved. Q2 now includes separately identified first-native-source examples; no feature formula or missingness policy changed.

## Remaining authorization boundary

The original task requires one SHA-bound live-fit approval if the active repository requires it. The active registry still requires that approval and only binds completed S3. [Consolidated S4 card](S4_LIVE_FIT_APPROVAL_REQUEST.md) includes seven slots, exactly eight NR/T2R starts, eight P baseline fits, eight prefix recipes, all gates and explicit S4 resource caps. This source correction itself needs no additional approval. No current S4 empirical outcome, model selection or new ledger entry is claimed.
