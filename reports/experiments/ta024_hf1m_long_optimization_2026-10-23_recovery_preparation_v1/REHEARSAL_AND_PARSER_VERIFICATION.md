# P024 parser and complete zero-step workflow — PASS

**No training restarted. Ledger 46/200; failed start 46 remains FAILED.**

The repaired parser uses Python's standard JSON decoder before constructing the DataFrame. The old pandas fast decoder changed nested0.0003from `0x1.3a92a30553261p-12` to the adjacent binary value `0x1.3a92a30553262p-12`. All 3,650 actual LRLOW update records and both saved AdamW optimizer states have the exact approved 0.0003. No learning rate or other scientific setting was repaired. Exact metadata equality is retained; a one-ULP wrong rate is rejected.

The complete workflow was rehearsed for DROP0,WD0,ES025,H64,L2H32 using the real frozen P020source,20 stocks,48 × 16 inputs and all four permitted roles:

1. Instantiate the exact model and AdamW groups; run a real whole-session forward/backward and gradient clip. `AdamW.step` is patched to raise on ANY invocation; its call count remained **zero**. All parameter/state hashes remain unchanged.
2. Exercise the actual D6g selector, immutable epoch receipts and atomic progress snapshot. Because there are no updates, one measured deterministic dropoutOFF train/validation checkpoint pass is reused for 12 stationary selector observations; this is explicitly labeled, not presented as 12 new learning passes. The stationary replay selects epoch 1 and stops at epoch 12, then executes one zero-update refit pass from a fresh identical initializer. This does not predict the selected epoch of actual ES025 training.
3. Save and reload actual tensor checkpoints and actual empty optimizer states. Export and exactly compare all four complete prediction populations for each arm:88,560 / 15,320 / 104,200 / 3,660 rows. **20 full-population reload comparisons have zero error.** These are initial-weight rehearsal predictions, not empirical results.
4. Run the real scientific diagnostic and supplemental functions: every 20-stock genuine endpoint/target identity, phase recipe, once-only inverse, weighted actual z-MSE, ZERO identity, tail decomposition, exact source cases and optimizer/model settings. Only the research-journal lookup is supplied through an explicit rehearsal fixture; no human approval is fabricated and no research journal is written. All other numeric readers/checkers are real.
5. Test that missing, failed, and core-only receipts block the next rehearsal stage; only complete core+supplemental checks permit the next rehearsal. The production gate and fitting authority both reject the rehearsal scope, even after all rehearsal checks pass. The real recovery executor requires both receipts before creating its output directory, journaling a start, or constructing its model.

**38 focused tests pass;366 Python files have0 static errors / 0 warnings.** No suppressions, severity changes or weakened scientific tests. Ruff and whitespace checks pass. Original records/pointer/journal/LRLOW result/DROP0 failure hashes are unchanged; no v14 journal exists.

Tolerance audit covers 24 full populations:20 rehearsal populations plus4 actual LRLOW populations. No tolerances were widened:

|Check|Existing acceptance|Largest observed absolute error|Largest fraction of allowed budget|
|---|---|---|---|
|TG20=numerator/(MAD+epsilon)|rtol 1e-10, atol 1e-11|0|0|
|Once-only inverse|rtol 7e-7, atol 1e-7|4.74078e-8|0.108892|
|Float32 supervised point z-MSE|rtol 3e-5, atol 2e-6|2.82547e-6|0.005818|
|Equal-session weighted checkpoint z-MSE|rtol 5e-7, atol 1e-8|5.80413e-9|0.008906|
|Checkpoint reload and effective hyperparameters|exact, zero tolerance|0|0|

The point-loss bound is relative-plus-absolute, so its absolute error can exceed 2e-6 at a large loss while remaining well inside the total budget. These numerical budgets account for float32 Torch supervision versus independent float64 aggregation/NumPy calculations. Selector qualification still uses strict `<` without added tolerance. Injected 0.01 forecast errors are rejected in every audited population.

Machine receipts: `verification_receipt.json`, `tolerance_validation.json`, `workflow_tests.txt`, `workflow_types.json`; full workflow receipt and actual private artifacts are referenced by verification_receipt. The executed rehearsal source is retained; its current source differs only in formatting, with identical AST. Checkpoint/candle/feature outputs stay ignored/local. Protected 2026 outcomes were never decoded.

This verification does **not** authorize a new model start. The original six-start approval is rejected by the proposed recovery authority. See experiment_design.md for the separately scoped proposal; it is unapproved.
