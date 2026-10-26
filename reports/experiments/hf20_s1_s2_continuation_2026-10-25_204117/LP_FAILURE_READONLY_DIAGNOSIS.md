# LP failure — bounded read-only forensic review

**LP DEFERRED_AFTER_PRIOR_FAILURE; no real-data LP evaluation or optimization was run.** The exact old implementation is `src/lstm_data/hf20_ranking.py:145` (value/gradient) and `:174` (solver/outer guard), bound by the prior9185edba… helper bundle. The original F21 failed attempt8/log/stop receipt remain unchanged in the prior namespace.

For fixed finite768-dimensional stock histories, LP minimizes weighted origin/session means of logistic pair loss plus λ||w||². Every untied unordered pair is included once (190 when20 outcomes are distinct), sign d=sign(Ri−Rj), margin−d·wᵀ(xi−xj), τ1; equal-origin-in-session then equal-session weights. No intercept: common offsets cancel. The gradient is −d·sigmoid(margin)·(xi−xj) with the same normalization, plus2λw. The matrix-free endpoint scatter is algebraically correct and its derivative is independently tested. Hessian is a positive-semidefinite weighted sum of pair-difference outer products plus2λI: strictly convex forλ>0. Stable logaddexp/softplus and bounded sigmoid avoid exponential overflow for finite representable dot products; finite guards remain necessary in floating point.

**Confirmed:** Torch L-BFGS returned, then the final max-absolute-gradient≤1e-5 guard failed forλ.0001. Solver settings were100 iterations,125 closure calls, internal gradient tolerance1e-7 and change tolerance1e-12. The error was not the closure-cap exception. The writer saved no accepted coefficient, final residual/objective, iterations/calls or termination reason before raising. None is recoverable from current artifacts. No claim that100 iterations were exhausted or that any particular numerical pathology occurred is supported.

Ranked possible explanations, not measured diagnoses:

1. A weakly regularized, correlated768-feature problem can require more than the fixed limited L-BFGS work budget. Neither condition number nor final residual was recorded, so this is plausible, not established.
2. A change/line-search stopping condition can return before the independent residual guard passes. The1e-7 internal gradient tolerance is stricter than the1e-5 acceptance guard; the two gradient thresholds alone are not logically inconsistent, but other termination conditions can intervene.
3. An unobserved numerical or implementation issue remains possible. Source/gradient inspection and existing independent synthetic derivatives found no visible shared sign/normalization/penalty bug; they do not certify real-prefix convergence.

Missing receipt fields: initial/final objective and data/L2 components; max/L2 gradient residual; accepted coefficient hash/checkpoint; iterations, evaluations and closure count; actual termination reason/line-search status; finite checks; wall/RSS. Existing failure logs are preserved, not retrospectively amended.

One possible future separately authorized remedy: retain the same objective/data/normalization, add immutable final-state/failure receipts and test a bounded convex-solver/preconditioning/work-budget amendment against independent derivatives and residuals. No solver, grid or tolerance change and no LP retrial is authorized here.

No shared defect invalidating LR or neural PW was established. LP absence is a disclosed missing comparator and is not the continuation's S2 gate. See original `execution_stop_v1/TRAINING_AND_SELECTION_TRACE.md`, `STOP_AND_PRESERVATION_RECEIPT.json`, `baseline_attempt_events.csv` and `execution_stdout.log`, referenced by hashes in the new manifest.

Evidence: [frozen implementation](../../../src/lstm_data/hf20_ranking.py), [original log](../hf20_s1_s2_ranking_2026-10-25_225152_preparation_v1/execution_stdout.log), [attempt events](../hf20_s1_s2_ranking_2026-10-25_225152_preparation_v1/execution_stop_v1/baseline_attempt_events.csv), [stop/preservation receipt](../hf20_s1_s2_ranking_2026-10-25_225152_preparation_v1/execution_stop_v1/STOP_AND_PRESERVATION_RECEIPT.json), [original trace](../hf20_s1_s2_ranking_2026-10-25_225152_preparation_v1/execution_stop_v1/TRAINING_AND_SELECTION_TRACE.md).
