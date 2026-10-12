# One consolidated P4.1–P4.2 human review

P4_1_P4_2_SYNTHETIC_ENGINEERING_COMPLETE — HUMAN_REVIEW_REQUIRED;
SCIENTIFIC_ACTIVATION_HOLD. Scientific usage 0/40; no P4.3.

## Eight inspection anchors

1. [Model and complete-session contract](../../../src/lstm_data/neural_engine.py), SharedLSTM line 28.
2. [Independent loss/sampler/optimizer tests](../../../tests/test_neural_engine.py), loss oracle line 54.
3. [D6g and fresh-refit controller](../../../src/lstm_data/neural_lifecycle.py), EarlyStop and run_pair.
4. [Calendar/outlier/selection tests](../../../tests/test_neural_lifecycle.py), scripted thresholds and calendar adequacy.
5. [P2 adapter and content identity](../../../src/lstm_data/neural_data.py), make_view and finite label clocks.
6. [Safe checkpoint and registry](../../../src/lstm_data/neural_artifacts.py), load_checkpoint and PairRegistry.
7. [Epoch recovery/budget/corruption tests](../../../tests/test_neural_artifacts.py), boundary resume and reservation race.
8. [Release pair trace/identity summary](synthetic_g5_release/seed42_pair/pair_result.json).

## Twelve substantive checks

1. Verify 6433 named parameters, zero recurrent state, explicit final-hidden dropout 0.10 and shared 32→1 head; independent/batched stock predictions agree.
2. Inspect unequal-origin hand values 4/10→7; reject pooled 6. Confirm actual 19-session epoch mean 9 and reject naive batch mean 12.25.
3. Inspect whole-session epoch permutations, 16+remainder, both complete origins, all five ordered stocks and 48 unshuffled scheduled steps.
4. Verify AdamW exact constants and disjoint/exhaustive matrix 0.01 versus bias0 decay, global one-time clip, zero-gradient and nonfinite rejection; no automatic rescue.
5. Inspect canonical indexed step data, source/order/version and per-cell clocks. Partial stocks, unknown/NaT clocks, observed context and stale certificates are rejected.
6. Verify last 63 calendar sessions retained, 55 eligible sessions/55 each origin after explicit ASOF exclusions; no shift or threshold relaxation. Held-out outlier leaves inner fit objects unchanged.
7. Inspect strict <0.999, 12/10/60, zero/near-zero/ties and raw versus qualifying minima. Script selected 1/raw 2/stop 12; actual selected 60 at cap.
8. Verify new full-prefix preprocessing IDs, fresh seed-reset model and empty optimizer, 180 calibration versus 420 refit updates, exactly 60 refit epochs.
9. Confirm only completed refit_final is forecasting-authoritative, with immutable SHA/parsed tensor schema, actual refit normalization and current code/version binding; calibration is audit-only.
10. Inspect exact same-CPU boundary recovery, no mid-epoch claim, interrupted directory refusal, isolated 39→40/40→41 and 24-hour guards, duplicate/race/corruption and failed-calibration denial.
11. Confirm alternate synthetic five-name binding, dataset source-value/version invalidation, labels/exit availability absent from forecast input, no P3 trading replay or actual historical fit. Cheap seeds 42/123/2026 initialize deterministically without extra fit pairs.
12. Review release full-suite/types/Ruff/AST/hash checks and resource report. All 16 P2/33 P3 scientific deferrals, original data and 0/40 real usage stay unchanged. Optional IDE Problems refresh with .venv is part of human review; no restart is requested.

Approval here can accept synthetic engineering only. Historical retention/publication/actions,
real fitted certificates/execution and joint/course sign-offs remain separate. STOP; no P4.3,
source amendment, scientific reservation, model search or Git action is authorized.
