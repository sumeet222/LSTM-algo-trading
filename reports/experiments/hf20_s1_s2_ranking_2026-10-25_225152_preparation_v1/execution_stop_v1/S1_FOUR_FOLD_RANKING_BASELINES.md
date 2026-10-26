# S1 partial results — STOP before OOS

**Stage2 FAILED/STOPPED at the first LP candidate. Seven baseline fits completed, one failed;56 planned attempts remain unstarted. No four-fold OOS evidence exists.**

Only F21 inner calibration was reached: one static-profile fit and six ridge penalties (.0001,.001,.01,.1,1,10). Profile and selected-ridge inner training/validation scores were saved. No profile/ridge full-prefix refit, no OOS control or later fold ran. LP F21 lambda.0001 returned from its fixed L-BFGS call without meeting final max-gradient≤1e-5; its fit was marked permanently FAILED. No retry, new solver tolerance, penalty choice or neural start was attempted.

## Inner-only metrics, not OOS results

| model | role | origins | sessions | daily_ic | pair_concordance | actual_objective | normalized_rank_mse |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LR | inner_train | 3510 | 1982 | 0.094454649 | 0.53371175 | 0.36498912 | 0.66723664 |
| LR | inner_validation | 197 | 115 | 0.038940134 | 0.51281138 | 0.36963089 | 0.70814163 |
| P | inner_train | 3510 | 1982 | 0.028914128 | 0.50999873 | 0.3680672 | 0.71552888 |
| P | inner_validation | 197 | 115 | 0.018628312 | 0.50678653 | 0.36840242 | 0.72310731 |

“Actual objective” is the weighted normalized-rank score loss (s−q)². “Normalized rank MSE” ranks the predictions first and is a different ordinal evaluation loss. Neither is original TG20 MSE. P is a fitted security profile; LR uses the complete768-feature sequence. Coefficients and input recipe identity are preserved.

## Ridge inner-validation selection

| penalty | ic |
| --- | --- |
| 0.0001 | 0.029208809 |
| 0.001 | 0.030467451 |
| 0.01 | 0.038940134 |
| 0.1 | 0.036530507 |
| 1 | 0.024418788 |
| 10 | 0.024478128 |

Selected λ=0.01, dailyIC=0.0389401344, using validation only. This selected validation IC is optimistically selected among the six candidates, not an annual OOS estimate. The static profile's validation dailyIC is0.01862831; LR's0.03894013 cannot establish a generalizable improvement from one selected inner tail.

The frozen primary metric (equal mean of four annual OOS dailyICs) is **NOT_AVAILABLE for every model**. No year was substituted or omitted to obtain a favorable score.
