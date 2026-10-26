# Recent36 versus saved expanding-history linear ranking

Primary estimand: shorten eligible coefficient-estimation rows to36 calendar months, preserving the saved fold/phase feature recipe and all OOS keys. Scaler statistics intentionally retain earlier permissible expanding-prefix observations. Causal warmup may precede the36-month fitting boundary. This is a single predeclared window, not a window search, scaler treatment or LSTM retraining test.

All28 authorized non-neural attempts succeeded:24 inner candidates and4 fresh refits. Separate [nonneural_attempts.jsonl](nonneural_attempts.jsonl) counts every attempt; no neural allocation was used. Each fold's full scientific gate preceded the next fold's first solve. Failed LP and F21PW65 remain unchanged. Neural ledger74/200.

## Matched OOS results

| year | selected_penalty | recent36_ic | expanding_ic | ic_difference | concordance_difference | top4_difference | bottom4_difference |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 10 | 0.02111466 | 0.0215872 | -0.0004725334 | 0.0001455457 | 0.02330508 | -0.01624294 |
| 2022 | 0.001 | -0.001227402 | -0.002914377 | 0.001686975 | 0.002216131 | 0.005541872 | -0.03817734 |
| 2023 | 0.0001 | 0.01150101 | 0.01286957 | -0.001368565 | 0.0003960159 | 0.01453488 | -0.0130814 |
| 2024 | 0.1 | 0.008148744 | -0.007372565 | 0.01552131 | 0.004012132 | 0.01891892 | -0.02364865 |


Recent36 equal-year mean IC0.00988425 versus expanding0.00604246, delta+0.00384180. It improves2/4 years (2022/2024), worsens2/4 (2021/2023), and is positive3/4 rather than2/4. M1's saved equal-year0.01172550 still exceeds recent36. All4 year-specific intervals include zero. The equal-year month-block sensitivity interval also includes zero; consult canonical MONTH_BLOCK_SENSITIVITY.csv. The initial aggregate resampling reused identical yearly random draws; a read-only follow-up gives each year's aggregate draw independent month indices. Annual registered-seed intervals, point metrics, fits and all21 other CSV outputs remain unchanged; v1 retained, explanation in READONLY_REPORTING_FOLLOWUP.json. This is not prospective or selection-adjusted inference.

Pair concordance improves slightly in every year, while top-four retrieval improves and bottom-four retrieval worsens in every year. These are different aspects of ranking, not trading returns. Better IC does not mean uniformly better tail selection. In2024, actual normalized-rank score loss is worse even though ordinal ranking error and IC improve; the score-regression functional and ordering metric differ.

## Selection, fitting support and overfit gap

| year | role | origins | sessions | ic | actual_loss |
| --- | --- | --- | --- | --- | --- |
| 2021 | inner_train | 1366 | 724 | 0.08545718 | 0.3664038 |
| 2021 | inner_validation | 197 | 115 | 0.02380021 | 0.3682656 |
| 2021 | refit | 1358 | 727 | 0.08777949 | 0.366337 |
| 2021 | oos | 293 | 177 | 0.02111466 | 0.3682364 |
| 2022 | inner_train | 1291 | 699 | 0.1802825 | 0.3555738 |
| 2022 | inner_validation | 137 | 87 | 0.02112119 | 0.3775691 |
| 2022 | refit | 1209 | 672 | 0.1844545 | 0.3551363 |
| 2022 | oos | 364 | 203 | -0.001227402 | 0.3815334 |
| 2023 | inner_train | 1188 | 670 | 0.1975153 | 0.3530787 |
| 2023 | inner_validation | 143 | 80 | -0.01574641 | 0.3882509 |
| 2023 | refit | 1121 | 635 | 0.1986314 | 0.3529383 |
| 2023 | oos | 284 | 172 | 0.01150101 | 0.3878549 |
| 2024 | inner_train | 1068 | 616 | 0.1582511 | 0.3595285 |
| 2024 | inner_validation | 111 | 74 | -0.002072749 | 0.3734779 |
| 2024 | refit | 983 | 575 | 0.1612613 | 0.3595875 |
| 2024 | oos | 308 | 185 | 0.008148744 | 0.3741576 |


Selected λs:2021=10;2022=.001;2023=.0001;2024=.1. Selection uses existing normalized weighted-mean objective and original inner validation equal-session IC; exact IC ties prefer larger penalty. [RECENT36_INNER_SELECTION.csv](RECENT36_INNER_SELECTION.csv) records all24 candidates, train/validation actual rank loss, penalty term, objective, residual, coefficient hash/norm, elapsed solve time and status. Negative selected validation ICs in2023/2024 are retained: no selection on their subsequent OOS outcomes, no surrogate rescue. [RECENT36_ROLE_SUPPORT.csv](RECENT36_ROLE_SUPPORT.csv) contains all16 roles' effective oldest/newest feature and matured-label times, session/origin/row counts and recipe paths/hashes. [FOLD_SOURCE_RECIPE_MANIFEST.csv](FOLD_SOURCE_RECIPE_MANIFEST.csv) documents the8 shortened fit populations and exact calendar lower bounds. Training/refit are in sample; inner validation is selection influenced; annual OOS is the matched retrospective evidence. They are not independent replications.

Refit slope norms approximately.0083/.9679/2.3581/.1240 differ widely with selected regularization. Matched-recipe recent/expanding coefficient cosines≈.170/.497/.554/.384; compare within fold where recipes match. Cross-fold coefficients use different phase scales, so changes are not raw-unit evidence of coefficient drift. Refit coefficients are freshly solved from recent rows without borrowing old coefficients. All28 coefficient hashes reload exactly; original normal-equation tolerance rtol1e-8/atol1e-9 is retained, with additional max-absolute residual≤1e-9. Independent direct prediction loss reconciles the sufficient-statistic quadratic objective. Equal-session fitting weights are recomputed on each recent sample.

## Monthly and source strata

[RECENT36_MONTHLY_PAIRED.csv](RECENT36_MONTHLY_PAIRED.csv) gives the primary recent−expanding contrast plus M1/T2R/NR context; [RECENT36_VS_EXPANDING_MONTHLY.html](RECENT36_VS_EXPANDING_MONTHLY.html) is offline. Recent beats expanding in8/12,5/12,6/12,8/12 months (27/48). It wins15/22 months where expanding LR's monthly IC was negative. That retrospective split at zero is descriptive, not a new selection rule. Correlation of improvement with the comparator's bad performance is mechanically coupled because the comparator is subtracted; it cannot prove adaptivity or predictive error timing.

[RECENT36_SLOT_COMPARISON.csv](RECENT36_SLOT_COMPARISON.csv) uses full within-origin cross-sections at each original slot. [RECENT36_QUALITY_STOCK_ATTRIBUTION.csv](RECENT36_QUALITY_STOCK_ATTRIBUTION.csv) attributes full-cross-section IC and loss/error mass by pre-existing historical quality/fallback/ticker/static-sector fields. Those row-subset contributions are not standalone Spearman correlations or new regimes; all group contributions conserve. Quality labels are descriptive inherited source facts, not certified historical publication-time observables. No population filtering was optimized.

Fitting process wall time35.77s, peak RSS893,321,216 bytes, CPU4 thread environment; includes source initialization, forecasts and immediate fold checks. Preflight18.80s/1,079,099,392bytes. No CPU-time total was measured; solve-only per-attempt timings exclude shared Gram accumulation and diagnostics. No network/install/neural inference/scaler fit.
