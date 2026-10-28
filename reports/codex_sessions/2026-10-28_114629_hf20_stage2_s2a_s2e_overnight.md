# Codex Session Report

## 1. Session metadata

- Date/session: 28 October 2026, Stage2 Session1 S2-A/S2-E overnight specialist.
- Task: four fixed lambda candidates per year, one past-selected fresh September refit, independent overnight smearing, matched old-calibration control and hard routing; stop after four folds.
- Branch: `feat/track-a-data-intake`; starting/ending SHA `5f7bb86a35d5aaff34ff79ef8f471117de6d3e42`, no commit.
- Start tree: modified current registry from earlier sessions, plus untracked supplied handoffs and Stage1 source/tests/reports. Preserved; no pull, merge, rebase, stash or deletion.
- Git fetch succeeded; branch0 ahead/0 behind. No commit/push/merge.

## 2. Executive summary

**COMPLETE execution, NO INCREMENTAL EVIDENCE.** All four folds retain80,260 rows/4,013 origins/793 sessions. Primary ROUTE-SMEAR raw MSE0.000107517993606 is **+0.2714% worse than C3**, losing every annual full-C3 point comparison. Overnight MSE0.000150570401605 is **+0.3387% vs C3, +0.4103% vs M1, +0.1905% vs same-operation OLD-N-SMEAR-MATCHED**. The old-matched equal-year interval includes zero; no incremental specialized representation is established. Ordinary overnight error, mean calibration, MAE and average IC worsen. Do not promote this specialist or choose N-RAW ex post.

All16 candidate starts and20 neural phase fits completed once, no empirical failure/retry. Ledger138→154/200.425 epochs/63,309 optimizer updates; fit-lifecycle sum6,746.00s. Peak process RSS1,137,885,184 bytes; new namespace about2.56MB, project about12.43GB. Ten focused tests and full508-file basic static check pass. No2025/2026 numerical access or new source acquisition.

## 3. Research/protocol impact

One authorized objective/selection package: `L_N + lambda L_D`, lambda in0/.10/.25/.50. Each training term is an independent equal group-session/origin/20-stock transformed-MSE mean. Epoch selection uses overnight transformed MSE and the exact original0.999/min12/patience10/max60 rule. Selected initial checkpoints compete on overnight raw MSE, exact ties preferring larger lambda. One fresh same-seed September refit uses the chosen candidate's selected epoch count.

Architecture, FT1648×16 own-stock windows, 20-name order, seed42, CPU float32, H32/one layer/final dropout.10/scalar M head/6,433 parameters, AdamW groups/settings, gradient clip1, session shuffle/batching, original four-trading-hour absolute endpoint labels and all Design A roles remain unchanged. The new model never receives clock/stock metadata or peer features. Loss weights do not remove any historical input step. Actual saved endpoint categories govern early-close morning exceptions.

One predefined overnight residual-smearing scalar is fit on honest Oct–Dec selected-refit forecasts; the same operation is fit on old C0 saved overnight calibration pairs. Old C3 intraday scores remain bit-identical. N-RAW is diagnostic, N-SMEAR the predeclared primary; no calibration choice is made from OOS. No other Stage2 hypothesis, event head, target, options/trading or confirmation work.

## 4. Files created

- `src/lstm_data/hf20_overnight_specialist.py`: isolated preflight, separately normalized group loss, fixed candidate selection/refit, append-only accounting, hard router and saved-score reporting. Reuses original source, window, recipe, model, optimizer, selector and metric code.
- `tests/test_hf20_overnight_specialist.py`: five small decisive fixtures; combined with existing C3 fixtures gives10 passing tests.
- `reports/experiments/hf20_s9_mag_stage2_session1_overnight_specialist_2026-10-28/`: one new campaign namespace,45 files/about2.56MB at final replay. Small protocol/preflight/readiness, eight-prefix parity record, four selected checkpoints, four new night OOS/calibration stores, compact epoch/selector/fit/coefficient summaries, metrics/groups/paired CSVs, report, interpretation, verification, continuation and journal.
- This handoff.

## 5. Files modified

Only `configs/CURRENT_EXPERIMENT_REGISTRY.json`: authorized atomic successor pointer schema26→27, pointing to the new immutable protocol and append-only journal. Prior pointer is preserved inside protocol; prior journal binding is recorded in every new event. The older registry diff was already present at session entry. No predecessor module, config, data, prediction, checkpoint, receipt, recipe, completed report or dashboard changed.

## 6. Files deleted, renamed or moved

None.

## 7. Critical interfaces

- `conditional_weights(days, category, group)`: independent normalized equal category-session/origin weights; zero elsewhere, empty group blocks.
- `loss_weights(days, category, lam)`: N weights plus lambda times D weights; only the four authorized values accepted.
- `weighted_loss(mhat, returns, scale, weights)`: un-clamped transformed-target squared error with20-stock mean, abs(R), correct phase scale; no sign leakage.
- `train_epoch`: original complete16-session batches, seed42+epoch shuffle, model/optimizer/clip path. Uses global role group weights times `all_sessions/batch_sessions`; a missing category contributes zero. Batch-session-weighted fixed-model epoch loss equals the declared population loss, without batch-mixture reweighting. At lambda0 D-label gradients are zero; unchanged AdamW regularization still operates normally.
- `choose_candidate`: four selected-checkpoint raw overnight selector losses, exact ties prefer larger lambda. No calibration/OOS argument.
- `route`: deterministic saved-category pick for every stock in an origin, preserving old intraday bits; unknown categories/shapes/nonfinite forecasts fail.
- `preflight`: exact saved NPZ role indices versus original mask derivation,48 steps/maturity/embargo, phase recipes/scales, calendar categories/20-stock axis, C1a decoder/C3 formula identity, permitted174-partition receipt, live138 ledger and caps. OOS outcomes are not projected.
- `event`: charge one start per candidate, including unselected ones; fresh selected refit belongs to the same charged pair. Separate phase count20; maximum16 starts154 total. No retry path.
- `run_fold`: four fresh initial candidates, selected weights only for historical selector scoring, then fresh chosen refit, frozen calibration/scalar, overnight OOS and exact reload comparison. No unselected OOS forecasts.
- `paired_months`: existing400/seed22042 month construction with category numerator/mass sampled together; reduces to old bootstrap for constant full-panel session mass. Keeps year-stratified equal-year aggregation, never IID stocks.
- `report`: only saved selected forecasts and frozen old comparisons, no neural calls/fitting. Refuses a four-year aggregate until four completed folds exist.

## 8. Data/schema/provenance

Reuse original S4 metadata/targets, original permitted adjusted-hourly read receipt and existing FT16 math.174 exact local partitions2010-07–2024-12, no directory-discovery source loader, download, minute reconstruction, bulk feature copy or new provider. Source/feature state is materialized in memory through the executed reader. All eight initial/September recipes and original weighted-left-median scales reproduce exactly before the first neural start; existing Session3 recipes are referenced, never O1 weights.

Exact saved Design A role indices are used from Session3 `role_indices.npz`, checked against Session2B roles and S4 masks. Full annual rows19,100/23,600/17,740/19,820. Night rows10,660/13,300/10,100/11,400, all complete20-stock origins; night subset45,460 rows/2,273 origins/771 sessions. D/N session counts overlap, not independent replications. Full original night weight masses.554711/.555454/.563420/.586470, never50/50. Full loss difference equals this annual mass times conditional overnight difference to numerical precision; intraday branch is unchanged.

New stores contain only the selected specialist's night metadata/canonical keys/weights/A/Mhat/N-RAW/N-SMEAR (OOS) or new calibration Mhat/A/keys/weights. No copied old predictor columns. Old C3 derives from its immutable factors and saved C0 Mhat; old C1a/M1/B0/O1 vectors are read unchanged. Existing prefix95/99 thresholds are referenced, not refitted on OOS.

## 9. Dependencies/environment

No dependency/install/environment change. Existing `.venv`, torch2.10.0 CPU float32, four intra-op/one inter-op threads, deterministic algorithms/seed42. Input-only causal FT16 preprocessing and target maturity semantics unchanged. PyArrow emits the known sandbox CPU-cache sysctl EPERM warnings without invalidating reads. A supplemental process-specific `ps` query was sandbox-denied and was not needed for fit/resource monitoring; the runner's existing resource checks remained authoritative.

## 10. Commands and tests

```sh
git status --short --branch
git branch --show-current
git rev-parse HEAD
git remote -v
git fetch --all --prune
git rev-list --left-right --count HEAD...@{upstream}
.venv/bin/ruff format src/lstm_data/hf20_overnight_specialist.py tests/test_hf20_overnight_specialist.py
.venv/bin/ruff check src/lstm_data/hf20_overnight_specialist.py tests/test_hf20_overnight_specialist.py --output-format concise
.venv/bin/python -m pytest tests/test_hf20_overnight_specialist.py tests/test_hf20_mag_c3_io.py -q
.venv/bin/python -m lstm_data.hf20_overnight_specialist --preflight
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist > /private/tmp/hf20_night_types_pre.json
.venv/bin/python -u -m lstm_data.hf20_overnight_specialist --run > reports/experiments/hf20_s9_mag_stage2_session1_overnight_specialist_2026-10-28/execution.log 2>&1
.venv/bin/python -m lstm_data.hf20_overnight_specialist --report
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist > /private/tmp/hf20_night_types_final.json
git diff --check
```

Final10 tests pass (4.06s), Ruff passes, full basic static508 files/zero errors/zero warnings (95.923s), diff check passes. Readiness pre-fit static also508 files/zero errors. Initial one pandas-group-key type diagnostic was resolved with an explicit string conversion; no broad Any, cast, ignore, exclusion or severity reduction. Initial preflight projection requested B0 columns absent from calibration stores; corrected to the actually saved C0/C1a/M1 columns, with no data/schema repair or neural start. Initial string-formatting compatibility diagnostics were corrected before training. No empirical neural run failed or was relaunched.

Fixtures: separate D/N means (L_N9,L_D10,lambda.25→11.5); lambda0 zero D-label gradient; unequal-origin days and missing-group minibatch exact population reduction; four-way deterministic selection/tie/nonfinite rejection; stored-category early-close routing/nonnegative formula identities; weighted month-mass bootstrap and historical full-case equivalence. No new synthetic research network fit. Empirical reload max error0 in all folds, all frozen-model identities unchanged through calibration/OOS.

Replay of protocol/coefficients/selection/fit summary/three statistical CSVs/journal is byte-identical. Code/tests match pre-fit readiness hashes. Critical old score/recipe/journal bindings remain unchanged. Full historical project tests and old mega-audit were not run.

Editor verification: select repository `.venv/bin/python`, keep Pylance basic and refresh Problems. Final editor Problems refresh remains human-confirmed, not agent-verified.

## 11. Experiment/results summary

- Identity: `HF20_STAGE2_S2A_S2E_OVERNIGHT_SPECIALIST_V1`, fold run directories `F21`, `F22`, `F23`, `F24` in the new namespace.
- Chosen lambda/epoch: .5/30, .5/27, 0/11, 0/3; no exact raw-score ties. F24 selector ran13 epochs; selected epoch3 is valid under the original rule, which constrains selector duration rather than minimum selected epoch.
- Refitted target scales: .005848759193156053 / .005933406715930685 / .006121673076939892 / .00617444719514992. Initial scales/recipes remain separately bound.
- New c_N:1.27239352305/1.27382207523/1.15212484787/1.19823530. Matched old c_N:1.28076157510/1.28937194995/1.18972688899/1.25310151013.
- Night calibration:56/47/47/36 sessions; n_eff53.01/44.70/44.98/32.96; all finite, no trimming/fallback. F24 maximum q10.2932, top10 moment contribution5.6033%, top1%8.3116%.
- Full primary MSE0.000107517993606 vs C3 .000107226942123, +.271435%; paired delta+2.910515e−7, descriptive95% interval[+4.704149e−8,+5.293811e−7]. Annual losses to C3 in all four years.
- Night primary MSE.000150570401605 vs C3 .000150062189438, M1 .000149955149007, old-matched .000150284037579. Relative changes+.3387%,+.4103%,+.1905%. The matched-control interval[−4.711101e−8,+6.025773e−7] includes zero; primary advantage is not demonstrated.
- Full MAE.00686473137 vs C3 .00680102945; ratio1.04616 vs1.02670. Night IC.334549 vs.337460; full IC.323146 vs.324668. Top-four slightly improves, other ranking evidence mixed, no ties/constants.
- Night prefix95/99 tail MSE improves2.0424%/1.3780% vs C3 but ordinary-complement MSE worsens5.2887%/1.7137%; even tail MSE is worse than the matched old smear.15:30 level improves while12:30 worsens; no new jump information is established.
- N-RAW improves night MSE1.0124% vs C0, but it is not substituted for the predefined calibrated primary. Full M1 gains inherit better C3 intraday forecasts and are not proof of new overnight skill.
- No trading, options, P&L or protected confirmation metric.

## 12. Reproduction

Use the documented existing environment and exact prior saved artifacts referenced in protocol. `--report` replays frozen new night forecasts joined to old saved predictor vectors; it requires no neural inference or raw hourly numerical reads. Synthetic fixtures run without historical source files. A fresh empirical reproduction requires the original174 allowed hourly partitions/S4 targets/masks, prior reports/recipes/scores, same Torch environment, exact protocol and separate fit authorization/budget; this completed namespace cannot be rerun because `neural_starts.jsonl` triggers `NO_RETRY`. Do not delete guards or rewrite ledger state to recreate fits. No background job was detached; the foreground run was monitored to completion.

## 13. Git/collaboration status

Same branch/SHA, fetched and0/0 upstream. No commit/push/merge. All new source/tests/report namespace/handoff remain untracked; the only pre-existing file modified by this session is the permitted registry successor pointer. Older untracked Stage1 work and the earlier registry changes remain protected. Review the complete linked session chain before any integration. After human review, add only the intended small code/metadata/report files and this handoff; PT/Parquet artifacts are intentionally ignored in the new namespace. Do not blindly commit earlier untracked work.

## 14. Issues, risks and limitations

No known failing test or outstanding correctness blocker. This negative/mixed scientific result is valid completion. Reused years and selector reuse across epochs/lambdas create development optimism; all intervals condition on selected model/scalar and omit their selection/estimation uncertainty. Month bootstrap is descriptive, not selection-adjusted significance. F24 scalar precision is limited. The model tests loss weighting, group monitor and selection jointly, not an isolated algebraic loss effect. Existing target prices precede approximate+2min issuance. Outcome-selected tail underprediction alone does not establish conditional-mean bias. Some morning-slot metric changes are early-close OVERNIGHT origins, not violations of frozen intraday routing.

## 15. Human decisions

Do not promote this specialist, widen lambda grid, rerun seed or rescue it using N-RAW. Retain provisional C3 and C1a/M1 benchmarks. If the researcher elects another Stage2 experiment, S2-B known-clock information is the more direct separately gated question for opposing12:30/15:30 level errors; this report authorizes none. S2-C/S2-D new labels require their own scientific design. Editor Problems refresh remains human-confirmed.

## 16. Next recommended steps

Review the main report/primary paired contrasts, then stop. No pending fold, retraining, dashboard, strategy or protected-data work remains. Any next experiment needs a new explicit authorization.

## 17. Artifact inventory

Everything below is under the new Stage2 namespace unless noted:

- `S2A_S2E_OVERNIGHT_SPECIALIZATION_REPORT.md`: self-contained result/decision, about31KB.
- `protocol.json`, `preflight.json`, `readiness.json`, `phase_parity.json`: frozen design, exact roles/group coverage, test/code identities, eight phase parity checks; small review metadata.
- `selection.csv`:16 initial candidate rows, historical selector diagnostics only; `fit_summary.csv`:4 selected final model records; `calibration_coefficients.csv`:4 new/old matched scalar records and concentration.
- `annual_and_equal_year_metrics.csv`:120 annual/EQ full/night arm rows; `conditional_groups.csv`:1,505 aggregate clock/category/tail/reliability rows; `paired_mse.csv`:35 annual/EQ paired contrasts.
- Per `F21`–`F24`: `selection.csv`, `training.csv`, `coefficients.json`, `result.json`, selected `restricted_final.pt`, selected-night `calibration_scores.parquet` and `oos_scores.parquet`. PT/Parquet files intentionally local/ignored; no unselected checkpoints or OOS scores.
- `neural_starts.jsonl`, `continuation.json`, `execution.log`, `verification.json`, `interpretation.json`: minimal lifecycle/replay evidence, empty continuation queue and final interpretation.
- New module/test and this handoff: untracked/reviewable. No new figure, dashboard, source/feature cache or duplicate old predictor store.
