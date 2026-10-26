# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-26T03:36:48.467883-04:00 (America/New_York).
- Contributor/session: Codex; HF20 S3 live campaign and resource-only continuation.
- Task: execute approved amended design bf12ae80cdd5a7c4418ffb7735e80eb93b7e720a90ba942518195839b2a266c3, S3-A before S3-B; apply explicit task2.5GB/project15GB/RAM2GB amendment without restarting completed fits.
- Branch: feat/track-a-data-intake.
- Starting/ending commit: 353402daa11704cdcdea3a7265c51aeb33afaa3e; no commits.
- Start: existing untracked S3 preparation/source/tests/session reports, preserved. End: those plus this task's new files and authorized CURRENT_EXPERIMENT_REGISTRY.json pointer modification.
- Cached upstream:0ahead/0behind. No fetch under inherited no-network campaign scope; no PR/issue/publication.

## 2. Executive summary

All72 baseline attempts and32 neural lifecycles completed, zero new failed starts/retries; ledger74→106/200. S3-A and S3-B technical gates PASS; scientific result QUALIFIED/exploratory. Shorter horizons alone show no consistent neural improvement. Aligned M2 merits bounded follow-up most clearly for h2 T2R: primary B−A IC+0.015958, common+0.011140, positive primary differences in all four years, but descriptive equal-year interval[−0.000770,0.029417] includes zero. No follow-up fit is authorized.

Final research entry: `reports/experiments/hf20_s3_live_2026-10-26_010204/S3_FINAL_RESEARCH_DECISION.md`. Complete per-file diagnostic map: DIAGNOSTIC_FILE_INDEX.csv. All requested detailed training/validation/refit/OOS and heavy-tail/NUM-MAD reports are linked there.

## 3. Research/protocol impact

Executed the explicitly approved independent h1/h2 populations and secondary common evaluation; unchanged20stocks,48×16input, two morning origin slots, genuine endpoints, conservative4h admission purge/embargo, train-only recipes, seed42, frozen LSTM/AdamW/rank-selector settings. A preserves original M2; B replaces only M2 with horizon-matched historical returns. Four-hour archived models/recipes/predictions reused unchanged. No50-session relaxation: F24validation66/64/74sessions for h1/h2/h4. No2025tuning, protected2026numeric reads, portfolio/backtest or new scientific definitions. Resource amendments are separate from science.

## 4. Files created

Reusable new source:
- src/lstm_data/hf20_horizon_data.py: HorizonData, horizon-specific source/target recipes and B-only M2 override.
- src/lstm_data/hf20_horizon_authority.py: exact authorized start order, hash/ledger/previous-stage checks.
- src/lstm_data/hf20_horizon_run.py: baseline/neural preparation, zero-step rehearsals and sequential fitting.
- src/lstm_data/hf20_horizon_diagnostics.py: phase-correct exports, source-price/target/objective oracles and immediate model PASS gates.
- src/lstm_data/hf20_horizon_report.py: A/B/collective comparisons and tail/training summaries.
- src/lstm_data/hf20_horizon_resources.py: explicit decimal2.5GB/15GB/2GB policy and required-additional-capacity errors.
- src/lstm_data/hf20_horizon_resource_continue.py: exact unstarted suffix after approved resource boundary, unchanged original scientific executor.
- src/lstm_data/hf20_horizon_closeout.py: read-only216-role oracle,64A/B identities, paired effects, witness histories, portable plot and complete index.

New tests: tests/test_hf20_horizon_execution.py, tests/test_hf20_horizon_closeout.py, tests/test_hf20_horizon_resources.py. Existing untracked math/preflight/test_hf20_horizons.py were earlier preparation, preserved unchanged.

New registry configs/track_a_candidate_experiment_registry_v21_hf20_s3.json; journal reports/audit/track_a_real_pairs_v21_hf20_s3.jsonl. New live namespace `reports/experiments/hf20_s3_live_2026-10-26_010204` contains authority, immutable execution/source snapshots, recipes, model outputs, checkpoints, receipts and reports. Each generated file's purpose/type/bytes/SHA/Git intent is in artifact_inventory.csv; this report is copied as WORK_SESSION_REPORT.md. Bulk scientific stores remain local/private.

## 5. Files modified

Only previously tracked modification: configs/CURRENT_EXPERIMENT_REGISTRY.json points to append-only v21 at the first authorized neural start. Its prior bytes are preserved; ledger predecessor linkage remains intact. New task files were iterated within this session; no previously tracked scientific source/config was changed. The scientific execution hash stayed d6d038eaaa5b233d0ebb7cad477e890dc6154d53ba67a8c3230c66630dee6b0e throughout fitting.

## 6. Files deleted, renamed, or moved

No raw, model or scientific artifact deleted/recompressed. At the resource boundary, the verified empty, unstarted87 directory was moved to resource_boundary_unstarted_directories/HF20-S3A-F24-H1-T2R-S42 and preserved; zero scientific files existed there. Temporary rehearsal scratch used normal temporary-directory cleanup before fitting, not storage-cap bypass. All completed outputs remain in place.

## 7. Critical interfaces and invariants

HorizonData wraps one permitted-through2024 FoldData and preserves frozen role identities; actual h-specific maturity is distinct from inherited conservative4h admission maturity. Target epsilon/scale are per-horizon/fold/phase and shared by A/B. B recipes explicitly store S3_M2 override; retained legacy floor/scaler fields provide lineage and must not be used as B's actual M2 rule.

Journal validates exact32IDs, permanent starts, hash bindings, completion receipts and prior-stage PASS before the next start. ResourceJournal delegates the original validators and neural_one, adds resource-amendment binding, and accepts only the exact remaining20 IDs. capacity_check reports bytes required beyond each cap. Checks occur before subsequent fits and during epochs.

role_oracle reconstructs source-price returns, TG20, keys, weights and optimized objectives. paired_role_diagnostics verifies identical A/B keys and reports full/common conditional effects; whole-origin losses retain inherited FP32 reductions before session aggregation. witness_histories reconstructs M2 with stored parameters only, verifying historical reference maturity and exact saved inputs. All paths are project-relative; no developer path in committed execution logic.

## 8. Data/schema/provenance changes

No source acquisition/migration/raw edits. P020 input contract7adfec916b7eb74fead83ef1fe6082ff0fcee9ff0b6ebae5722077e2a82c01a5; pinned minute revision776328445b7ac6e7815ef3a483e9c8ded1eb6d56; HF20_HF1M_LONG_v1_ACTION_QA_v1. New outputs use explicit return_h/horizon/stage, actual source closes, actual vs conservative maturity, denominator, actual FP32 transformed target and M2 values/validity. Legacy carried label_eligible is the old4h source flag, not the new fitting filter. All numeric reads end2024; protected files were hashed as bytes only.

## 9. Dependency/environment changes

None. Existing .venv Python3.14.6/arm64, numpy2.5.3,pandas3.0.6,torch2.10.0,pyarrow23.0.1,plotly6.3.1. CPUFP32/4intra/1inter,0loader workers. No secrets/.env reads, downloads, installs or network requests. Arrow sandbox sysctl probe warnings were nonfatal.

## 10. Commands and tests run

Historical live commands (do not rerun a populated/charged campaign):
- `.venv/bin/python -u -m lstm_data.hf20_horizon_run --out reports/experiments/hf20_s3_live_2026-10-26_010204 --prepare`
- Same CLI with `--gate-rehearsal`, then authorized `--run`.
- `.venv/bin/python -u -m lstm_data.hf20_horizon_resource_continue --out reports/experiments/hf20_s3_live_2026-10-26_010204` — exact20 remaining starts, exit0.
- `hf20_horizon_report.collective(Path(...))`, then `.venv/bin/python -u -m lstm_data.hf20_horizon_closeout --out reports/experiments/hf20_s3_live_2026-10-26_010204` — final read-only closeout exit0.

Validation:
-64population checks/64zero-update workflows plus8complete four-role workflows, zero optimizer steps/starts; receipts READINESS_PASS.json and FULL_STAGE_GATE_REHEARSAL.json.
- Guarded seven-file regression suite:49passed,8deselected,13.82s; AdamW.step/LBFGS.step calls0 (FINAL_GUARDED_TEST_RECEIPT.json). Optimizer-requiring legacy synthetic tests were excluded, not silently executed.
- `.venv/bin/python -m pytest tests/test_hf20_horizons.py tests/test_hf20_horizon_execution.py tests/test_hf20_horizon_closeout.py tests/test_hf20_horizon_resources.py -q` — final19passed4.43s, final_focused_tests_v2.txt.
- `.venv/bin/ruff check .` — final_ruff_v3.txt, all checks passed.
- `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist` — final_static_v6.json:467project files,0errors,0warnings,66.593s. Earlier corrected static receipts remain; no severity reductions, suppressions or exclusions.
-216 independent saved-role checks,64A/B identities,416paired metric deltas at rtol=atol1e-12,4,224exact M2 history steps. Portable PlotlyHTML4,841,665bytes,0external script sources; browser visual inspection is not asserted.
-63preparation inventory and5,846prior-reference SHA checks pass, excluding only authorized current pointer. Frozen execution/resource bindings pass; old journal prefix unchanged.
-`git diff --check` passed; tracked diff reviewed as current pointer only.

Editor verification remains human-owned: select repository .venv/bin/python, restart Pylance, refresh Problems, confirm zero project-owned errors. CLI parity passed; actual editor refresh is not asserted.

## 11. Experiment/results summary

A:16new h1/h2×four-year×T2R/NR models plus72 supervised baseline attempts. B:16matched models with only M2 changed. 2021–2024annual OOS, seed42, fixed20stocks, no2025/2026 selection.32complete,0failed. Calibrations observed12–30epochs, selected1–20;71,980calibration and28,686refit optimizer updates; per-model lifecycle seconds sum5,170.36 (not whole-session overhead). Fresh selected-epoch refits/checkpoint reloads passed.

Primary B−A IC: h1T2R+0.001535, h1NR+0.009197, h2T2R+0.015958, h2NR+0.002543. Common: +0.002997,+0.001548,+0.011140,−0.001072 respectively. See S3_FINAL_RESEARCH_DECISION.md for all yearly/full/common baselines and neural results and qualified verdict.

Original-target top5% accounts for50.49–52.34% original-Y MSE but23.08–23.32% actual T2R loss. NUM_ONLY original-MSE share44.62–46.02%, MAD_ONLY2.99–3.95%, BOTH0.57–2.45%; remainingNEITHER. No ordinal raw-return MSE or trading/profitability claim. Tail report includes all roles, complements, thresholds, error-ranked cohorts, energy/alignment and selected-subset cross terms.

## 12. Reproduction instructions

Use documented repository .venv/dependencies and lawful local pinned source/derived caches. No new credentials or absolute paths are required. Read README.md, frozen card, LIVE_AUTHORITY.json, EXECUTION_MANIFEST.json and resource amendment bindings. Preparation/horizon/membership evidence remains in the prior preparation namespace. Existing live authority is exhausted; another fitting reproduction requires separate authorization and a new namespace/journal, never rerun this campaign.

Safe saved-output verification: import role_oracle from lstm_data.hf20_horizon_closeout and call it on each `reports/experiments/hf20_s3_live_2026-10-26_010204/[AB]/F*/*/*_scores.parquet`; this reads saved permitted partitions, fits nothing. Re-run the focused pytest/Ruff/static commands above. Read-only closeout is designed for the first closeout of a completed campaign; its immutable receipts reject duplicate writes. Preserve prior outputs and use append-only report corrections for later changes. The complete inventory and hashes identify every input/output required for review.

## 13. Git / collaboration status

Branch/HEAD unchanged. No fetch, index mutation, commit, branch operation, merge or push. Cached upstream0/0 only, not a fresh remote claim. Existing user/preparation work preserved. Current-pointer update, new v21 definition/journal,8newsource files,3tests and live/session report artifacts remain uncommitted. For a future separately authorized commit: review compact source/config/tests/reports and inventory; exclude ignored private Parquet/NPZ/PT/source-case stores and large telemetry. Coordinate CURRENT pointer/journal and CLI changes before integration. Do not pull over this dirty tree.

## 14. Known issues, risks, limitations and resolved interruptions

- Source publication/action vintage/rights conditional; retrospective survivors; price-only labels start2minutes before assumed issuance, not executable returns. Common evaluation does not imply identical horizon training sets. Four years/single seed/post-search exploration do not establish significance.
- Resource boundary: active model86 completed; original controller held before start87 using its journal lock. Preserved FATAL_STOP.json is operational, not a model failure. No active training interruption/replay; exact20remaining starts used separate resource-only wrapper. RESOURCE_BOUNDARY_CLASSIFICATION.json and RESOURCE_AMENDMENT_EXECUTION_v1.json are authoritative explanations.
- Pre-fit rehearsal relative/absolute temporary-path handling and initial guarded legacy-test selection were corrected before real attempts. Initial guard caught4synthetic optimizer calls before any update; final guarded suite0calls. Earlier preparation's disclosed synthetic-step scope exception remains in its original report and is not retroactively authorized.
- Post-training closeout timestamp formatting was slow. Only the identified read-only process was interrupted; trace and first-pass tables preserved. Cached origin-slot mapping is independently clock-verified; no model output changed. Read-only process inspection/targeted SIGINT used sandbox escalation; no other process was stopped.
- Strict supplemental paired checks exposed FP32 layout/reduction and CSV-roundtrip differences (~1.7e-9 rank error, up to1.25e-8 objective delta). Final report reconstructs inherited per-origin reductions before aggregation; all416checks pass1e-12 without relaxing any scientific gate. Initial paired draft tables remain archived and are superseded by top-level paired tables; PAIRED_RANK_ROUNDING_RECONCILIATION_v2.json plus READ_ONLY_CLOSEOUT_FINAL_CHECKS.json explain resolution.
- No remaining failing focused/static checks. Editor confirmation and actual publication availability remain unresolved external facts.

## 15. Decisions requiring human/teammate review

No approval is needed to close this completed campaign. Any replication, additional seed, model/horizon selection, trading study or confirmation access requires a separate scientific decision and authorization. Interpret h2T2R aligned-M2 as a follow-up hypothesis, not a selected production model.

## 16. Next recommended steps

Review S3_FINAL_RESEARCH_DECISION.md, then detailed training and extreme-objective reports. Use DIAGNOSTIC_FILE_INDEX.csv for every individual diagnostic/analysis file. Preserve this namespace and prior artifacts. Do not launch more fits automatically.

## 17. Artifact inventory

artifact_inventory.csv records each new implementation/config/journal/report/plot/table/checkpoint/log/store path, purpose,type,bytes,SHA and Git intent. DIAGNOSTIC_FILE_INDEX.csv covers all live artifacts and references the unchanged h4 index. Main reports: README; preflight; frozen card; S3A_HORIZON_ONLY_COMPARISON; S3B_HORIZON_ALIGNED_M2; S3_TRAINING_AND_FAILURE_TRACE; S3_HORIZON_EXTREMES_AND_OBJECTIVE_DIAGNOSTICS; S3_FINAL_RESEARCH_DECISION; this WORK_SESSION_REPORT. Shared tables include all216role metrics/oracles,64A/Bidentities,paired role/stock/slot/month/quality effects,year/horizon/common contrasts,all-role tail/NUM-MAD,training trace and4,224M2witness rows. All176model-stock-event replays derive from22events/20origins/13sessions. Model checkpoints/predictions/derived stores are intentionally local/private and ignored; no redistribution authorized. Inventory/index do not self-hash; FINAL_HANDOFF_RECEIPT.json binds their completed snapshots and final resource accounting.
