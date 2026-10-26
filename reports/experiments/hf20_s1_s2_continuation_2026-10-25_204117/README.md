# HF20 S1 + S2 continuation — final evidence map

**Authorized attempts completed with declared failures:29 new baseline fits succeeded;12 neural starts,11 completed/1 failed. Final ledger74/200. LP deferred. F21PW's four-year comparison remains unavailable.** No extra fit/retry/seed,2025 tuning,2026 numerical access, downloads or trading. All artifacts remain uncommitted/local.

| Stage | Final status | Evidence |
|---|---|---|
| A LP forensics | PASS, nonblocking | LP_FAILURE_READONLY_DIAGNOSIS.md; no real LP retry |
| Readiness | PASS | READINESS_REPLAY.json; original F21 fits/scaler exactly reused |
| B S1 | PASS for P/LR/naive; LP DEFERRED | S1_FOUR_FOLD_RANKING_BASELINES.md;29 new fits |
| C S2 | QUALIFIED |11 completed/1 failed; all12 starts charged, no retry |
| D Diagnostics | PASS for all accepted outputs; missing F21PW disclosed |88 role outputs,31 OOS cells; source-case60 replays |
| E Closeout | QUALIFIED scientific evidence | independent/preservation checks pass; source/rights/vintage and missing-fold limits retained |

## All readable scientific reports

- [Primary eight-row results](PRIMARY_RESULTS.md)
- [S1 four-fold baselines, selected penalties and F21 reuse](S1_FOUR_FOLD_RANKING_BASELINES.md)
- [S2 annual LSTM comparison and explicit failed fold](S2_FOUR_FOLD_LSTM_RANKING_COMPARISON.md)
- [Detailed extreme-value, objective, NUM/MAD and four-role diagnostics](RANKING_EXTREMES_AND_OBJECTIVE_DIAGNOSTICS.md)
- [Training/validation/refit/epoch/gradient/selection and all attempt IDs](TRAINING_AND_SELECTION_TRACE.md)
- [Research diagnosis, uncertainty and next unlaunched hypothesis](FINAL_RESEARCH_DECISION.md)
- [Read-only LP failure diagnosis](LP_FAILURE_READONLY_DIAGNOSIS.md) and [detached conservation-audit correction](PAIR_GUARD_RESOLUTION.md)
- [Mandatory session/handoff report](WORK_SESSION_REPORT.md)

## Full analysis and diagnostic tables

| Files | Contents |
|---|---|
| all_role_metrics.csv, four_fold_OOS_metrics.csv, equal_year_summary.csv | All88 accepted roles and31 OOS model-folds; equal-year result only when four years complete |
| cohort_objective_and_error_decomposition_v2.csv | Canonical actual objectives, original-Y energy/common/centered/cross terms only for T2R, target tails/complements, signed events, NUM/MAD/floor, IC attribution; N0 IC unavailable |
| cohort_stock_month_sector_quality_v2.csv | Canonical cohort ticker/month/static sectorETF/quality/fallback attribution; no historical-PIT sector claim |
| all_original_objective_and_error_cohorts.csv, T2R_original_error_ranked_cohorts.csv | Every own-objective-error and original-Y-error cohort, ordinary complement, signs, weights and phase meaning |
| paired_cohort_rank_error.csv | Same-key candidate-minus-P/LR/T2R ordinal errors; no favorable own-error subset comparison |
| return_gap_pair_diagnostics.csv, cohort_pair_concordance_and_PW.csv | Valid/dependent pair counts, training-only gap bins, endpoint-tail types, concordance, margins and true PW loss conservation |
| zero_score_objective_context.csv | Already-declared zero-score reference in each objective's units; no new fit and IC undefined |
| paired_month_block_sensitivity.json |400 full-calendar-month paired resamples; sensitivity, not significance/data-snooping correction |
| complete_epoch_trace.csv, neural_selection_and_runtime.csv | Full epoch/raw-best/qualifying-best/selected counts and lifecycle timings |
| gradient_clip_update_summary.csv, final_gradient_update_counts.csv | Calibration/refit pre/postclip/update/weight norms and all recorded steps; failed partial-epoch limitation disclosed |
| final_selector_checkpoint_optimizer_verification.csv | Independently reconstructed selectors, checkpoint hashes, fresh initialization and exact final refit step counters |
| source_case_checkpoint_replay.csv, source_case_native_fallback_by_channel.csv |60 model replays of22 underlying origins;352 case-channel native/fallback/age records; exact source/recipe/checkpoint inputs |
| original_target_extreme_examples.csv, shared_source_case_keys.csv | Keyed actual extreme rows and22 predetermined genuine source references; not duplicated raw candle stores |
| final_readonly_summary_smoke.csv, FINAL_INDEPENDENT_VERIFICATION.json | Full output/journal/source/selector/cohort/smoke reconciliation;12 starts/11 complete/1 failed |
| annual_rank_IC.html | One portable offline interactive annual-IC figure; no new UI/server |

The `v2` cohort/strata tables are canonical. Their v1 tables are retained; REPORT_ONLY_CORRECTION.json changes only N0 undefined-correlation attribution placeholders, without changing scores/metrics/fits. SOURCE_CASE_TYPING_FOLLOWUP_v2.json, if present, records the formatter-final hash of the read-only audit helper; its exact executed source snapshot is retained. Historical FATAL_STOP.json/FAILURE.json remain as failure evidence; PAIR_GUARD_RESOLUTION.md records the prospective resolution, not a retry or retrospective completion.

## Every per-model file

**DIAGNOSTIC_FILE_INDEX.csv** lists each actual diagnostic/analysis file, purpose and path; **artifact_inventory.csv** adds bytes/SHA256/local Git intent. This includes all31 OOS and88 role files, every model's inner training/validation/refit/OOS `*_scores.parquet`, `*_metrics.json`, `*_cohorts.csv`, `*_thresholds.json`, `*_origins.csv`, month/slot/stock-quality tables, PW `*_pair_types.csv`, all cal/refit checkpoints and per-batch/epoch receipts, source_cases.csv, configuration/binding/provenance files, selection/coefficient files and PASS/FAILURE receipts. Four original F21 inner score/diagnostic sets are reused by immutable prior path, not copied/refitted.

Source-case NPZs are shared once per fold and contain compact derived48×16selected-stock inputs/20 outcomes, not52raw candles per replay. They, row-level outputs and weights remain private/local research artifacts; no underlying-data or derived-store redistribution is authorized.

## Authority, history and safeguards

CONTINUATION_AUTHORITY_AND_RUN_MANIFEST.json records the actual direct user request, original8 baseline attempts, new29 tasks, seven reused F21 fits and12 exact neural IDs. PAIR_GUARD_PROSPECTIVE_AMENDMENT.json permits only the9 then-unstarted runs after audit-precision repair, preserving failed65. It does not claim a fabricated signature or new scientific choice. Both original v19 and successor v20 journals link back to original62; current registry is v20/74. Prior source/failed-run/checkpoint bytes are unchanged; live registry transitions are archived by snapshots.

Source publication/action vintage, retrospective20-stock cohort, bounded researcher-attested private rights and the2-minute historical label/issuance mismatch remain qualified. This is retrospective chronological OOS ranking, not pristine confirmation or an executable strategy. No formal selection-adjusted null or extra seeds were run.

## Reproduction and safe next steps

Use the documented .venv and exact licensed cached source/artifact bindings plus runtime_environment.json. Do not rerun any training/readiness/seal/audit writer into this populated namespace or use this exhausted authority for another model. Read-only aggregate verification can use `verify_exports(out, score_paths(out))` from the existing ranking helper modules and the stored final receipts; it neither fits nor writes. Focused tests and exact static commands are in WORK_SESSION_REPORT.md. A fresh machine needs a separately legitimate documented source/artifact handoff; clone-only portability and redistribution are not certified. No commit/push or future model is authorized by these results.

Prior context (archival, not newly fitted OOS comparators): [old stopped campaign](../hf20_s1_s2_ranking_2026-10-25_225152_preparation_v1/execution_stop_v1/README.md) and [complete seven-workstream dossier](../../diagnostics/hf20_ranking_readonly_dossier_2026-10-25_202831/README.md). Original P028 correction and all older source/checkpoint references remain bound by the preserved manifests. For N0, legacy per-role additive IC placeholders are not correlations; use canonical v2 unavailable IC attribution.
