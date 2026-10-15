# Codex Session Report

## 1. Session metadata

Date/time: 2026-10-15T10:04:56.241565-04:00, America/New_York. Contributor: Codex root, no subagents. Task: Package008 read-only T0/T1 diagnostics. Branch: feat/track-a-data-intake. Starting and ending HEAD: f53feb4ba8a43c23695d3ed7dd01535ec9460a8f; no commit. Start: clean after human commit f53feb4. Fetch passed; upstream 0/0. No issue/PR or Git mutation. End status: git_status_final.txt.

## 2. Executive summary

TA008_DIAGNOSIS_COMPLETE. All 2822 protected files are unchanged; a concurrent external RandomNotes.md edit is retained; budget remains 4/40. Eight matched WF1 model/baseline records reconcile. Canonical target decomposition and 21 bounded origin replays pass. Heavy target/session-loss tails and MC0/MC1 cancellation are quantified; historical clipping causes remain unidentified. Final analysis took 21.158074s core / 24.388905s outer; all diagnostic attempts totaled 73.655752s. Session through final snapshot: 1561.646s.

## 3. Research/protocol impact

No target, horizon, feature, universe, split, cost, trading, architecture, seed, search or scaler change. Only the four completed seed-42 June-2023/WF1 fits were analyzed. Bootstrap intervals are post-screen EXPLORATORY_NOT_FULL_G8. No confirmation values, economic replay, promotion, source-right certification or production change. P2 v1 hashes were verified with load_deferred_work (16 entries), and the v4 successor was read. All statuses and pointers remain unchanged.

## 4. Files created

New source: src/lstm_data/four_model_diagnostics.py, one CLI and diagnostic helpers. New tests: tests/test_four_model_diagnostics.py. New API: docs/track_a/Four_Model_Diagnostics_008_API.md. New packet: reports/data_audit/ta008_four_model_diagnostics_2026-10-15_094143, containing the requested health, tail, loss, daily/cohort/paired, replay, mechanism, hypothesis, check, resource and review records. The complete artifact_inventory.csv gives each file type, purpose, size and hash. This 17-section session report is new. All remain untracked.

## 5. Files modified

This audit changed no preexisting file. A concurrent external edit added a descriptive target-tail sentence to docs/track_a/RandomNotes.md; it was inspected for scope, hashed and preserved without modification. Only new diagnostic files were revised by this audit. The new preflight start metadata was corrected to the first observed session clock, 09:40:13 ET, with that basis recorded. Old model code, weights, recipes, journals, registries and protocol pointers remain unchanged.

## 6. Files deleted, renamed, or moved

No preexisting file was deleted, renamed or moved. Eighteen newly generated first-attempt report files were moved into attempt1_report_serialization_failure after an integer serialization error. Twenty newly generated second-version files were preserved in attempt2_before_distribution_extension before adding output-dispersion and feature-distribution fields. Ten additional own unsealed report files, including the initial API draft, were preserved in report_build_attempt1_note_check when the concurrent-note guard stopped report sealing. All bytes remain available; no raw/source archive or human work was moved.

## 7. Critical interfaces

four_model_diagnostics.main(--previous: Path, --output: Path) reads exact completed inputs and writes only a fresh report namespace. legal_key rejects observations outside training/WF1 before access. session_concentration averages origins within sessions and uses ceil(p×N). pairwise_accuracy omits target ties and gives forecast ties half credit. rank_difference honors undefined target cases. paired_blocks uses contiguous exchange-calendar positions, seed8008 and 5000 exploratory resamples. safe_model validates hashes, preparation/stage/epoch/contract and returns a weights-only CPU model in eval mode with gradients disabled. Inputs, outputs and limits are in the API doc. Existing target, feature, scaler, peer, encoder, metric and G6 functions are reused; no duplicate training loop or optimizer exists.

## 8. Data/schema/provenance changes

No input schema or source changed. New diagnostic tables label partitions/modes and conditional evidence. Inner 1376/688, validation 110/55, refit 1502/751 and WF1 232/116 origins/sessions are unchanged. All audited target decompositions match float32 labels. Feature distributions describe unique input rows including lookback context, not new fitting populations. Twelve error-blind representative origins plus bounded post-hoc classes deduplicate to 21 traces. Only endpoint values, hashes and hidden norms are saved. Unadjusted OHLC and action/publication vintage are explicitly unavailable from the component store; exact retrospective price references are linked. No confirmation data or raw archive copies.

## 9. Dependency/environment changes

None. Existing repository .venv and declared NumPy/Pandas/Torch dependencies only. CPU float32, one Torch thread and OMP/OPENBLAS/MKL/VECLIB caps of one. No installation, secret or provider access. New-audit peak RSS was not recorded and is not borrowed from historical training measurements. Compact tables provide the evidence; no plot dependency was added.

## 10. Commands and tests run

Exact commands, output and source hashes are in commands.md and *_command.json. Focused release: `.venv/bin/python -B -m pytest tests/test_four_model_diagnostics.py tests/test_neural_health.py -q`: 13 passed. `.venv/bin/ruff check .`: passed. Option A: `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist`: {'filesAnalyzed': 181, 'errorCount': 0, 'warningCount': 0, 'informationCount': 0, 'timeInSec': 14.912}. Initial optional-IC/Boolean-mask type issues and formatting were corrected. A NumPy int64 episode-count serialization failure was corrected with an explicit int conversion; earlier report attempts and logs remain. Final CLI returned zero. No full legacy suite or synthetic fits ran; historical 728/703 results are inherited only under their recorded hash scopes. Editor: use repository .venv/bin/python, Pylance basic and matching stubs; refresh the language server/Problems and have a human confirm zero errors. Git diff --check passes.

## 11. Results summary

| Model | Equal-day WF1 MSE | Daily IC |
|---|---:|---:|
| TM0 | 5.4388296 | 0.0349138 |
| MC0 | 5.4508656 | -0.0120690 |
| MC1 | 5.4514664 | -0.0120690 |
| E5 | 5.4756397 | 0.0387931 |
| ZERO | 5.4275318 | 0.0000000 |
| M1 | 12.6919763 | -0.0219828 |
| RIDGE_OWN_112 | 5.4655180 | -0.0228448 |
| RIDGE_MARKET_147 | 5.4681203 | -0.0034483 |

Candidate, retrospective/ideal-clock/hourly-proxy evidence only. E5−TM0 daily IC is +0.0038793 with a five-session exploratory interval [−0.07932,+0.08750]. None beats ZERO MSE. MC0/MC1 ranks differ at 47/232 origins; 19 better and 19 worse days cancel. All four retain G6 WARN; no nonfinite gradients. E5 refit warnings cover epochs4–8. Training |TG0|max82.028 and worst10% session-loss share≈55.6%. Floor dominance is20/1502 and zero-MAD count is0. Maximum sampled forward error1.192e−7 is below2e−6. No new fit, trading metric or confirmation result.

## 12. Reproduction instructions

Use the authoritative README environment setup and legitimate existing component stores, recipes, manifests and weights. Create a new output directory, then run `.venv/bin/python -B -m lstm_data.four_model_diagnostics --previous reports/data_audit/ta007_multimodel_firstpass_2026-10-15_010008 --output <fresh-existing-directory>` with the thread caps in commands.md. Existing report paths refuse overwrite. The same CLI reproduces numerical tables/traces; narratives link their fields and equations. The Pylance extension path is an intentionally configured checker argument, not a runtime data path. Another machine must provision the documented inputs; a clean-clone rehearsal was not performed.

## 13. Git / collaboration status

Branch feat/track-a-data-intake; HEAD f53feb4ba8a43c23695d3ed7dd01535ec9460a8f unchanged. Startup fetch passed with upstream0/0. Start was clean; new audit source, test, API, packet and session report are untracked at end. RandomNotes.md also has a concurrent external tracked edit, which remains untouched. No stage, commit, push, stash, reset, cleanup or remote communication. Preserve this work before integration. If later explicitly authorized, review the inventory and stage only the approved new code/test/API and small reports/session; exclude raw stores and checkpoints. No Git action was authorized here.

## 14. Known issues, risks and limitations

No final failing tests or type errors. The final preservation check initially stopped on the concurrent note edit; its non-scientific scope was verified and recorded without discarding it. CLIPPING_CAUSE_NOT_IDENTIFIABLE_FROM_SAVED_BATCH_LOGS: old dropout masks, intermediate optimizer states and paired batch losses/norms are missing. Correct finite replays do not certify publication/PIT/action/license facts or alpha. Only one explored seed/fold and five stocks. Intervals lack full G8/HAC/selection adjustment and depend on block length and gap/edge weighting. Feature bounds do not exclude optimization sensitivity. B0 unadjusted fields are not replayable from this component store. Final editor Problems refresh remains human-confirmed.

## 15. Decisions requiring review

NO_HYPERPARAMETER_CHANGE_YET. Choose one future paired seed-123 WF1 or seed-42 WF2 TM0/MC0 design, costing two additional pairs, only after exact new data/code/preparation and qualified rights/clock approval. No future fit is approved by this audit. A loss/floor/clip change is a separate research amendment; explored WF1 cannot be described as untouched. The ≤3-family finalist versus four screened families remains a separate decision.

## 16. Next steps

Read human_review_card.md, then the hypothesis/evidence ledger and paired/monthly tables. Preserve the frozen models. Prioritize a matched replication of the primary market increment over a performance-driven rescue. If later approved, small effective-batch telemetry can discriminate clipping hypotheses. Economic/proxy-accounting and confirmation gates remain separate. No task was scheduled and no follow-on training starts.

## 17. Artifact inventory

reports/data_audit/ta008_four_model_diagnostics_2026-10-15_094143/artifact_inventory.csv lists all new code, tests, API, packet files and this report, with bytes, SHA256, type and purpose; it excludes itself. Existing source stores, baselines and fitted weights are linked, not copied. New outputs are untracked review artifacts. Earlier report attempts are preserved. No new checkpoints, dense histories, gradient tensors, activation dumps, trading logs or economic plots were created.
