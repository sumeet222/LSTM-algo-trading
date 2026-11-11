# Clean Phase 2 modeling Gate C report

## 1. Session metadata

- Date: 2026-11-02.
- Contributor: independent modeling collaborator, `/root/clean_phase2/model_gate`.
- Task: reconstruct S2-C modeling behavior from the released experiment specification and validate synthetic Gate C fixtures.
- Authority: `replication/EXPERIMENT_SPEC.md`, fully read; current clean Phase 2 authorization and lead's integration instructions.
- Git branch, starting/ending commit and working tree: deliberately not inspected by this collaborator under the clean-room boundary; lead/coordinator owns those receipts. No Git commands or changes were made.

## 2. Executive summary

Implemented the 6,572-parameter CPU float32 S2-C model, phase initialization, hierarchical losses, global auxiliary normalization, session batching, exact optimizer groups, selector, fresh restricted refit, inference, checkpoint persistence and failure receipts. All **35 synthetic tests pass: 25 modeling and 10 independent feature-math review tests**. Isolated basic Pyright reports **0 errors, 0 warnings, 0 informations**. No real-data model fit was run by this collaborator.

## 3. Research/protocol impact

No research choices changed. The main target, auxiliary geometry, scales, seed, architecture, objective, epoch selector, dropout, CPU/thread policy and no-retry rule follow the released specification. All earlier outcomes remained sealed. No comparator was implemented or imported. Raw data, preprocessing artifacts and role counts were not inspected by this collaborator.

## 4. Files created

- `replication/phase2/code/model.py`: independent model, loss and isolated training/inference interfaces.
- `replication/phase2/tests/test_model.py`: 25 synthetic mathematical/behavioral audits.
- `replication/phase2/tests/test_feature_math_review.py`: ten independent synthetic checks of the newly written feature mathematics, added at the lead's request.
- `replication/phase2/audit/pyright_model.json`: narrowly scoped basic-mode static-check config, with relative paths.
- `replication/phase2/audit/model_gate.json`: test result, current library versions, seed42 initial-parameter digest and hashes of the specification and owned implementation/test/config files.
- `replication/phase2/audit/model_gate.md`: this handoff.

## 5. Files modified

Only newly created owned files were refined during synthetic validation. The first test run exposed cumulative-weight normalization using the final accumulated sum; it was corrected to normalization by `np.sum(weights)` as specified. Main inference was separated from diagnostic auxiliary-output finiteness so auxiliary weights cannot determine a finite main prediction's success.

## 6. Files deleted, renamed or moved

None. Temporary synthetic checkpoint folders were managed by Python `TemporaryDirectory` and removed at fixture completion.

## 7. Critical interfaces

- `configure_runtime()`: Torch 2.10.0, CPU, float32, four intra-op/one inter-op threads and deterministic algorithms. No backend substitution.
- `fresh_model()`: seeds Python random, NumPy legacy RNG and Torch with 42; constructs LSTM, Dropout, main and auxiliary heads in that order.
- `S2CModel.forward(x, clock)`: flattened `[origins*20,48,16]` and repeated `[origins*20,10]`; returns main `[origins*20]` and normalized signed auxiliaries `[origins*20,3]`. No labels, masks or auxiliary outputs feed the main head.
- `PhaseData`: sessions, float64 signed primary/auxiliary labels, overnight categories, complete-triple mask, phase scale and a feature/clock-only `get_inputs(origin_indices)` callback. It checks finite primary labels, finite supported triples, unsupported NaNs, signed additivity and intraday mask exclusion.
- `fit_scale`, `origin_weights`, `auxiliary_weights`: training-only left-median magnitude scale, equal-session/equal-origin primary hierarchy and one phase-wide auxiliary normalization. Unsupported stock cells are never redistributed within an origin.
- `batch_losses`: float32 target construction, local primary hierarchy, `S/B` auxiliary factor, index-before-arithmetic masking and differentiable exact zero for empty auxiliary batches.
- `session_batches`: sorted dates shuffled with NumPy `default_rng(42+epoch)`; 16 sessions per batch, preserving a smaller last group and original within-session origin order.
- `make_optimizer`: fresh AdamW with exhaustive rank-two matrix decay and all-other no-decay groups in registration order.
- `Selector.update`: qualified improvement `v <= .999*best`, separate strict raw minimum, patience stop before epoch cap, full detached state clone.
- `train_selector` / `train_refit`: independent fresh initialization and optimizer, epoch callback, optional fresh run directory, source-neutral receipts and failure-stop propagation. Real fits must supply a fresh output directory; omitting it is for synthetic fixtures.
- `predict` / `predict_heads`: eval/inference mode, chronological chunks of 32 origins. The primary-only path ignores auxiliary diagnostic finiteness. Signed raw diagnostic head predictions are `scale * predict_heads(...)[1]`.
- `save_state` / `load_state` / `state_digest`: atomic checkpoints, strict state loading, serialization-independent named tensor identity. Reload is for frozen inference; it deliberately initializes a fresh model first.

## 8. Data/schema/provenance changes

None. All executed fixtures use generated arrays. No raw download, source market observation, existing derived feature, prior fitted checkpoint, archived prediction or historical result was read. The lead additionally requested read-only review of the newly written `dataset.py` and `features.py`; those new files were inspected only after the modeling tests passed.

## 9. Dependencies/environment

No package installations or dependency changes. The isolated test process used the existing third-party environment: Python 3.14.6, NumPy 2.5.3 and Torch 2.10.0. Runtime threads are checked as 4/1. No `lstm_data` import was attempted. The clean Phase 2 boundary was installed before NumPy/Torch or other third-party imports in test launches.

## 10. Commands and tests run

Commands below are portable equivalents of the exact invocations, using `REPL_REPO` for the repository's absolute path and a clean working directory such as `/private/tmp`:

```sh
"$REPL_REPO/.venv/bin/python" -I -c 'import sys, runpy; from pathlib import Path; root=Path(sys.argv[1]); sys.path.insert(0,str(root/"replication/phase2/code")); import boundary; boundary.install(); runpy.run_path(str(root/"replication/phase2/tests/test_model.py"),run_name="__main__")' "$REPL_REPO"
"$REPL_REPO/.venv/bin/pyright" --project "$REPL_REPO/replication/phase2/audit/pyright_model.json" --pythonpath "$REPL_REPO/.venv/bin/python"
```

The final test receipt was generated by loading both test files with `runpy`, constructing their `ModelGate` and `FeatureMathReview` suites and executing `unittest.TextTestRunner(verbosity=2)`. **35 tests passed, zero failures/errors/skips**, final duration 1.587 seconds. The audit JSON hashes bind the tested implementation and suites. Run the same command with `test_feature_math_review.py` to reproduce the ten added feature checks separately. An initial 24-test run had one synthetic quantile boundary failure; that defect was corrected before the passing runs. Static checking initially found 11 test-only Tensor/Module/optional-gradient typing diagnostics; explicit parameter lookup and real non-null assertions resolved all 11 without lowering severity or exclusions. The isolated config now includes both test files.

Audits cover: exact parameter and RNG ordering; independent gate recurrence and both biases; 48-step reset; dropout inversion and shared representations; clock preservation; eval RNG invariance; original-vs-masked hierarchy; global `Z=7/8`; primary `20/3`; auxiliary `3` and contribution `.3`; `S/B` scaling and noncanonical simple batch averaging; empty auxiliary NaN avoidance and zero gradients; main/auxiliary loss finite differences; recurrent matrix/bias and head finite differences using a synthetic double-precision derivative oracle; target float32 conversion order; session shuffle/no-drop-last; AdamW decay, bias treatment, moments and explicit two-step equations; global clipping and nonfinite rejection; momentum movement on zero auxiliary gradients; inference invariance to labels/masks/auxiliary head weights; 32-origin chunk/order; selector equality/near improvement, patience, cap and zero losses; fresh refit identity; exact checkpoint reload; persistent epoch callbacks; failure receipt and no-retry refusal.

The float64 derivative oracle is test-only. All production model construction and training remain float32.

The ten additional feature tests compare explicit finite-window means against rolling full/minimum/triple/regime masks; exercise remote-large-prefix cancellation; distinguish weighted-left and interpolated quantiles; test MAD/IQR/SD/constant fallback; verify all16 native formulas, floors, B2 tolerance and COP blocking; reject Q2 cross-regime histories; check scaled missing fallback; establish EMA360 and Wilder140 warmup boundaries, one-gap freezes, three-gap and basis resets, no RSI gap bridging; and verify origin-fixed M2 context and origin/stock/step/channel assembly order. The first feature run found one real indexing error in the new assembler. The lead corrected `steps` to `steps[:,:,None]` before all ten passed.

## 11. Experiment/results summary

Only synthetic fits ran. No historical selected epoch, calibration coefficient, forecast, metric or empirical comparator outcome was accessed or reported. Synthetic selector histories were explicitly prescribed fixtures and cannot select real-fit settings.

## 12. Reproduction

Use the repository third-party environment and clean working directory, install the new boundary before third-party imports, then run the commands above for each test file. No external data or credentials are needed for these 35 tests. Real integration supplies lawfully reconstructed windows, role rows and phase scales through `PhaseData` after the lead's data and source gates pass.

## 13. Git/collaboration status

No commit, push, fetch, branch operation or historical repository inspection was authorized for this collaborator. Owned new files are ready for lead integration. No other agent's source was edited. The lead must include the clean Phase 2 inventory and exact repository state in the enclosing session report.

## 14. Known issues, risks and limits

- Passing synthetic Gate C is not a real-data fit or final replication result.
- Original package binary/backend snapshots remain unavailable; arithmetic agreement is the accepted objective, not historical bitwise claims.
- The latest editor Problems refresh remains human-confirmed: select the repository `.venv/bin/python`, open the new Phase 2 files, refresh Pylance basic diagnostics and verify zero error-level items. No editor confirmation is claimed here.
- A read-only review of new `dataset.rolling` identified global-prefix subtraction cancellation (for example `[1e16,1,1,1]` with a two-position window). The lead replaced it with blocked window-local sums before feature fitting. A fresh synthetic check confirms the final two windows both return1. Its triple-NaN window indexing was found correct. The new `features.quantile` normalizes with the total weight sum as required.
- New Q2 construction initially allowed a current-regime pseudocount with entirely prior-regime daily histories. The lead added current-versus-prior daily-regime equality; its boundary fixture passes. This implements the released cross-regime-unavailable requirement.
- New assembler M2 indexing initially failed to broadcast for multiple origins. The lead added the explicit stock-axis dimension; reordered-origin/fixed-context fixtures now pass. No real fit was attempted before these fixes.

## 15. Decisions for human/teammate review

No new research decision requested. Keep real training gated by the lead's all-fold checks. Preserve the accepted nominal-origin issuance mismatch, retrospective source policies, fixed survivor universe and historical-result sealing.

## 16. Next recommended steps

Integrate the stable `PhaseData` and training APIs; finish all-fold data/support gates; launch only the authorized chronological fold sequence with fresh output namespaces and epoch receipts; stop on any unexpected real-fit failure. Do not inspect archived outcomes until the independent result freeze.

## 17. Artifact inventory

The four owned source/test/static-config files and the two audit files above are the deliverables. The JSON also binds the reviewed new dataset/feature files at the final combined test run. Synthetic temporary checkpoints are intentionally ephemeral. No large generated models or data were added by this collaborator.

## Follow-up: feature typing audit

At the lead's subsequent request, `features.py` was added explicitly to the isolated basic Pyright scope. Two diagnostics reflected the paired optional Wilder gain/loss state: Pyright could not infer that a non-null initialized gain implies a non-null loss. Two `assert losses is not None` statements now enforce that genuine invariant immediately before the update and emission. No formula, warmup, missing-data rule, output dtype or other behavior for valid inputs changed. The ten feature-math tests pass again in0.144 seconds.

The same config was expanded to explicitly inspect new `dataset.py` and `geometry.py`. The owned model/features/test files have **zero error-level diagnostics**. The expanded dependency check currently reports **8 errors, 0 warnings, 0 informations**: dataset has three array-mapping/`savez_compressed` signature diagnostics, and geometry has five pandas scalar/index typing diagnostics. These were reported to the lead; this collaborator did not edit those dependency files. The expanded static check remains a handoff/HOLD item until resolved. The JSON receipt now records this current scope and the updated source/config hashes; the earlier zero-error result above refers to its earlier, narrower checked scope.
