# Execution and selection trace — stopped S1

| job | key | status |
| --- | --- | --- |
| 1 | F21/P/inner/None | COMPLETED |
| 2 | F21/LR/inner/0.0001 | COMPLETED |
| 3 | F21/LR/inner/0.001 | COMPLETED |
| 4 | F21/LR/inner/0.01 | COMPLETED |
| 5 | F21/LR/inner/0.1 | COMPLETED |
| 6 | F21/LR/inner/1.0 | COMPLETED |
| 7 | F21/LR/inner/10.0 | COMPLETED |
| 8 | F21/LP/inner/0.0001 | FAILED |

Exactly eight supervised baseline attempts: seven completed and one failed. Failed attempt8 remains in the immutable original job log; no refund or restart. Remaining56 original planned attempts, seven remaining prefix recipes and all12 neural lifecycles were not launched.

The one fitted F21 inner recipe has cutoff2020-06-30, epsilon0.00031079729533760086 and asinh scale0.9072704147262087, with the original P020 floors/fallbacks/scalers. It is not an old2023/2025-fitted recipe. Its exact file/hash is in the stop inventory. No alternate recipe or hyperparameter was fitted after failure.

LR chose lambda.01 from its original six inner-validation candidates; P has no grid. Exact candidate coefficients and selection receipts survive. LP's Torch L-BFGS used the frozen100-iteration/125-closure settings, tolerance_grad1e-7 and tolerance_change1e-12, followed by required max-gradient≤1e-5. The failure specifically came from the final residual guard after opt.step returned. It was not the closure-count-cap exception, and it is not a weak-IC result.

The execution code throws before returning/saving LP convergence data. Therefore actual final residual, objective, iterations/calls and LP weights are unavailable. Do not claim it necessarily exhausted100 iterations, invent a residual, or reconstruct it by an unauthorized rerun. This missing failure receipt is an observability limitation requiring a reviewed code amendment if continuation is proposed.

No neural epoch/gradient/clipping/optimizer/refit trace exists because no neural start occurred. The initial seed42 and neural definitions remained frozen and unused.

[Full unchanged execution log](../execution_stdout.log), [attempt events](baseline_attempt_events.csv), [live authority](../live_approval_full_campaign.json) and [stop receipt](STOP_AND_PRESERVATION_RECEIPT.json) bind the actual execution. Original model/code/source/checkpoint bytes and P028 reporting-only amendment are preserved.
