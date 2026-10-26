# Codex Session Report

## 1. Session metadata

- Date/time:2026-10-25T20:21:37.825795-04:00, America/New_York; user-facing date2026-10-25.
- Contributor/session:Codex, approved HF20 S1+S2 execution and stop audit.
- Task: user explicitly approved S1 and all12 enumerated neural starts for proposal7d47e5e893e2450b63d348f9c539df7c6ac2790b07b0d94ecaaee02acbe9b04a / execution9185edba7e01e2fa6d7ea0d519fdfa60fc818fdc548215cc1c986439403b3660.
- Branch:feat/track-a-data-intake.
- Starting/ending commit:05f2ac140f5ce02031200ea0fb43b448983be704; no agent commits.
- Working tree at start: prior prepared five modules/test/report root/session and supplied design record untracked; no tracked diff. Cached upstream0/0.
- Working tree at end: same prior work plus new execution/stop reports/session untracked; no tracked source/config diff.
- Related issue/PR:none. No Git publication/integration/network fetch.

## 2. Executive summary

Recorded exact live approval, verified proposal/code/all3994 preserved references, verified16-entry P2 handoff, then invoked the frozen executor once. It completed F21's static-profile fit and six ridge inner fits, but first LP candidate lambda0.0001 failed its required final maximum-gradient≤1e-5 convergence gate. Campaign automatically stopped with exit1 before remaining baselines or any neural start. No retry or source-code change. Eight baseline attempts:7 completed/1 failed; one prefix recipe completed. Neural ledger remains62/200. All2026 numerical outcomes remained closed. Partial saved outputs independently reconciled and complete partial diagnostics indexed; this is not successful full-campaign completion.

## 3. Research/protocol impact

No target, features, universe, clock, dates, optimizer, seed, penalty grid, scientific threshold or old definition changed. The approved first F21 inner P020-family recipe was genuinely fitted through2020-06-30. P/LR labels/scores are inner training/validation only. No full-prefix model refit, annual OOS score or neural calibration/refit/checkpoint. Source qualifications and original P2 holds remain, P028 executed identity/reporting correction preserved. No2025 selection,2026 numerical I/O, trading or extra experiments. Failed baseline attempt8 is permanent and not charged as a neural lifecycle.

## 4. Files created

Within `reports/experiments/hf20_s1_s2_ranking_2026-10-25_225152_preparation_v1`:

- `live_approval_full_campaign.json`: actual affirmative response/exact approved scope and hashes; new file, false template preserved.
- `execution_preflight_receipt.json`, `runtime_environment.json`, `execution_authority_ref.json`: pre-fit/source/authority/versions/command receipts.
- `execution_stdout.log`, `baseline_fit_jobs.jsonl`: unchanged captured execution/exception and8 attempted/terminal coefficient-fit records.
- `F21_inner_recipe.json`: first causal prefix floors/scalers/fallbacks, epsilon and scale; no other recipe fit.
- `F21_S1_P/`: static-profile coefficients, inner selection and two inner-role complete score/diagnostic sets.
- `F21_S1_LR/`: six penalty coefficient arrays, selected inner receipt and two inner-role complete score/diagnostic sets.
- `F21_S1_LP/`: empty failed-output directory; no accepted LP weights/solver receipt.
- `execution_stop_v1/`: README, S1/S2 results, detailed extreme/objective/NUM–MAD report, training/selection trace, research decision, this report copy; partial combined metrics/cohorts/examples/stock-month-quality tables; independent reconciliation; stop/preservation/no-restart receipts; tests/static/Ruff; exact artifact inventory.
- `reports/codex_sessions/2026-10-25_202137_hf20_s1_s2_execution_stop.md`: mandatory new session report.

## 5. Files modified

No preexisting source/config/report/raw/derived file modified. All five approved Python module hashes still match. No ledger/registry pointer mutation. Earlier preparation reports remain historical; the new execution_stop_v1 index reports actual stopped state. No change to the approved numerical tolerances or tests.

## 6. Files deleted, renamed, or moved

None. No cleanup, rollback, stash, reset or replacement of old evidence. All previous work/failed starts preserved.

## 7. Critical functions, classes, variables, and config keys

No new or changed public code interfaces. Executed existing `authorize`, `FoldData.phase`, `s1`, `ridge_system/ridge_solution`, `linear_pair`, `Journal.baseline/baseline_done`. `linear_pair` called frozen Torch L-BFGS with max_iter100/max_eval125/tolerance_grad1e-7/tolerance_change1e-12, then raised `LINEAR_PAIR_NOT_CONVERGED_NO_AUTOMATIC_RETRY` at final max-gradient guard1e-5. It did not reach coefficient/solver receipt export. No `s2`, neural journal append, model optimizer epoch or full closeout ran. Stop audit used existing read-only `verify_exports` plus stored outputs, without data refits or model predictions.

## 8. Data/schema/provenance changes

Existing raw/processed data unchanged. One new prefix recipe: fit cutoff2020-06-30, epsilon0.00031079729533760086, scale0.9072704147262087. Selected P/LR saved inner-train3510 origins/1982 sessions each and inner-validation197 origins/115 sessions each; four score files and148280 total score rows. Same canonical20 stocks×48×16 FT16; masks/clock/label maturity frozen. Keyed score schema includes source/recipe/coefficient hashes and true ordinal objective. Additional stop tables derive only from these saved scores/receipts. No extra fitted threshold or new input channel. No OOS/2026 outcome read for a new diagnostic.

## 9. Dependency/environment changes

None. Existing .venv, CPU4 intra/1 inter/0 loader workers; numerical package versions captured in runtime_environment.json. No .env/secrets/network/download/install. No new project Python files beyond earlier prepared unchanged modules/test. No new dashboard/server.

## 10. Commands and tests run

- Git status/branch/SHA/remotes/cached ancestry read; cached0/0, HEAD unchanged. No fetch under task no-network scope, no stage/commit/push/integration. `git diff --check` pass; tracked diff empty.
- Verified `load_deferred_work(Path('configs/track_a_p2_engineering_handoff_v1.json'))`:16 bound entries; no changes/hold closure.
- Exact approved execution:
  `OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 VECLIB_MAXIMUM_THREADS=4 .venv/bin/python -u -m lstm_data.hf20_ranking_run --run --out reports/experiments/hf20_s1_s2_ranking_2026-10-25_225152_preparation_v1 --approval reports/experiments/hf20_s1_s2_ranking_2026-10-25_225152_preparation_v1/live_approval_full_campaign.json` with stdout/stderr captured —exit1, frozen LP residual guard. No rerun.
- Authority-reference to final-log filesystem timestamp span≈89.96s, approximately20:13:02–20:14:32 America/New_York; not instrumented per-fit wall/CPU timing. Training-process peak RSS was not captured; no invented measurement. Later audit-only process peak522,584,064 bytes; task17,695,434 bytes/project projected6,878,134,584 bytes at that probe, including16MB journal reserve. These are not training peak figures.
- Independent read-only audit: all3994 source/code/checkpoint references unchanged, four saved outputs exact-key/weight/IC/objective/cohort conservation PASS. No OOS files or v19 neural journal/definition.
- `.venv/bin/python -m pytest tests/test_hf20_ranking.py tests/test_hf1m_ft16.py::test_protected_read_and_unknown_split_fail_before_file_access tests/test_state_screen.py::test_protected_routes_fail_before_io -q` —33 passed,16.22s.
- `.venv/bin/ruff check .` —All checks passed.
- `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist` —444 files,0 errors/0 warnings,61.088s. No suppressions, reduced severities, exclusions or weakened tests.
- Editor verification remains human-confirmed: choose repository .venv/bin/python, restart Pylance, refresh Problems and confirm0 project-owned errors. Local extension path is tooling only.
- Arrow sandbox sysctl/cache/NEON warnings preceded fitting; actual terminal error is the LP convergence guard, not permission/network rejection. No auto-review rejection occurred.

## 11. Experiment/results summary

Only inner F21 outcomes are available. P dailyIC train0.02891413/validation0.01862831. Selected LR lambda.01 dailyIC train0.09445465/validation0.03894013. This is a six-way selected inner-validation score, not an annual OOS result or superiority conclusion. Actual ordinal point loss validation P0.36840242/LR0.36963089; LR validation pair concordance0.51281138. Four-fold primary IC is unavailable for every model. NR/PW/T2R never started.

Original-|Y| top1% validation LR cohort39 rows contributes≈2.50% of actual rank-score loss, top5%197 rows≈11.88%, with ordinary complements preserved. No original TG20 output MSE, asinh prediction loss or neural gradient trace exists. Full signed/event/NUM–MAD/floor/quality/stock/month tables and examples are linked by stop README. All partial scientific findings remain exploratory and inner-only.

## 12. Reproduction instructions

Do not rerun the failed fit or use previous live approval as restart authority. Read execution_stop_v1/README.md, FINAL_RESEARCH_DECISION.md, STOP_AND_PRESERVATION_RECEIPT.json and unchanged execution_stdout.log. Reproduce only read-only metric/hash checks and focused tests using documented .venv and existing sources. Actual LP final objective/residual/weights/call counts are unavailable; do not reconstruct by refitting without authorization. Any amended continuation requires a newly reviewed exact executor/budget and actual response.

## 13. Git / collaboration status

Branch feat/track-a-data-intake, HEAD05f2ac1 unchanged, cached upstream0/0. No agent commits/PR/push/index mutation. All new implementation/preparation/execution/stop/session artifacts remain untracked alongside user design record. Preserve all before another session's integration. Future conflict surfaces: prospective v19 journal/registry and executor changes, but none were activated here. No local raw/source/checkpoint sharing authorized by these reports. Separately review intended compact code/report files before a future focused commit; no automatic Git action.

## 14. Known issues, risks, and limitations

**Campaign HOLD:** LP failed final convergence requirement. No accepted LP scorer; no S1 gate; no neural runs. The executor throws before recording final solver state/residual/objective, so detailed solver failure diagnostics cannot be recovered without new fitting; this is a concrete observability limitation. Do not assume iteration cap was exhausted merely from this error. Synthetic solver tests passed but did not establish real-prefix convergence. Resource estimates were not a substitute for measurements. No source integrity change found. Source publication/action vintage/rights/PIT and2-minute historical issuance mismatch remain qualified. Four-fold and full tail/weight/neural analysis NOT_RUN, despite valid partial output checks.

## 15. Decisions requiring human or teammate review

A continuation must preserve failed baseline attempt8, seven completed coefficient fits and one prefix recipe. Retrying the same missing candidate would add57 new baseline attempts (restart plus56 originally unstarted), making65 total rather than refunding the64-fit cap. All12 neural starts remain available only under newly reviewed post-failure authority. A solver iteration/tolerance/state-export amendment or deliberate LP omission changes the reviewed executor/design and requires a concrete new proposal plus approval. No such continuation is prepared or authorized in this session. Existing approval explicitly stops after true failure/no retries.

## 16. Next recommended steps

Review the stop decision/diagnostic index. If a continuation is separately requested, prepare a bounded LP numerical/receipt amendment and explicit resumable fit accounting; run synthetic/zero-real-step rehearsal before asking for exact live continuation. Do not silently repeat P/LR fits, refund failed attempt8, start neural training or adapt from the partial validation metrics. No later research branch is justified by the incomplete result.

## 17. Artifact inventory

`execution_stop_v1/artifact_inventory.csv` lists all actual task report/receipt/index/recipe/log/coefficient/score/diagnostic files plus this session report with bytes and SHA256, excluding self-hash. Existing raw/old checkpoints were hash-verified only, not copied. No new real neural checkpoint, annual OOS score, model figure/dashboard or training replay. Detailed source-case preparation exists but no neural source replay. All new artifacts local/uncommitted; compact reports may be reviewed for later Git inclusion separately.
