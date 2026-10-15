# Codex Session Report

## 1. Session metadata

Date/time 2026-10-15T13:45:16.162354-04:00; Codex root, no subagents. Package011 controlled target-tail/loss/clip interventions. Branch feat/track-a-data-intake; starting commit 62f5cf20a8f916563f495d2419be7709499d55f3; ending HEAD 62f5cf20a8f916563f495d2419be7709499d55f3, no commit. Initial Git inspection clean; concurrent human RandomNotes edit appeared by preflight and was preserved. Fetch all/prune succeeded; ahead/behind 0/0 at seal. No PR/issue, stage, commit or push. Recorded clock anchor 2026-10-15T16:45:46+00:00; deadline 2026-10-15T18:45:46+00:00.

## 2. Executive summary

TA011_CONTROLLED_BATCH_COMPLETED;18/18 completed,0failed;6→24/40. All four arms MIXED_OR_INCONCLUSIVE; no finalist or further task activation. Original seed 42 controls reused. See reports/data_audit/ta011_controlled_interventions_2026-10-15_124546/human_review_card.md.

| Arm / seed | WF1 ΔMSE / ΔIC | WF2 ΔMSE / ΔIC | G6 WF1/WF2 | Pairs | Fit s |
|---|---:|---:|---|---:|---:|
| H1 / 42 | -0.007828 / +0.00172 | +0.003338 / -0.02457 | P/P | 2 | 124.6 |
| H1 / 123 | +0.000789 / -0.01767 | -0.008775 / -0.00043 | P/P | 2 | 89.7 |
| T1 / 42 | -0.002160 / +0.00043 | -0.006092 / +0.01810 | W/W | 2 | 106.1 |
| T1 / 123 | +0.000742 / -0.00517 | -0.004716 / +0.00603 | W/W | 2 | 86.3 |
| T2 / 42 | -0.011421 / +0.01509 | -0.011104 / +0.01552 | P/P | 2 | 119.7 |
| T2 / 123 | -0.003009 / -0.00388 | -0.010273 / +0.00603 | P/P | 2 | 89.6 |
| O1 / 42 | +0.000396 / -0.00733 | +0.005706 / -0.00431 | W/W | 2 | 111.8 |
| O1 / 123 | +0.003331 / -0.00948 | +0.004850 / -0.00905 | W/W | 2 | 91.1 |


## 3. Research/protocol impact

Prospective approved amendments only: Huber delta2; pooled unique-observation linear99th-percentile train-label cap; asinh training representation with independent median-absolute scale/floor1e−6 and canonical inverse; clip5. Same original TG0 evaluation,48×16 FT0,6433 weights, AdamW, D6g, horizon, universe/order, masks and splits. Seed123 controls/treatments added exactly as approved. No feature, market/peer, cost, trading, architecture, production or confirmation change. P2 v1 load_deferred_work hash verification16entries and authorized v4 successor read; no statuses cleared. Factual source gates remain conditional, never independently certified.

## 4. Files created

- src/lstm_data/controlled_loss.py
- src/lstm_data/controlled_authority.py
- src/lstm_data/controlled_batch.py
- src/lstm_data/controlled_review.py
- tests/test_controlled_interventions.py
- tests/test_controlled_review.py
- docs/track_a/Controlled_Interventions_011_API.md
- configs/track_a_candidate_experiment_registry_v4.json
- reports/audit/track_a_real_pairs_v4.jsonl
- reports/data_audit/ta011_controlled_interventions_2026-10-15_124546
- reports/codex_sessions/2026-10-15_134516_ta011_controlled_experiments.md

Each generated artifact is itemized with path/type/purpose/size/hash/tracking intent in reports/data_audit/ta011_controlled_interventions_2026-10-15_124546/artifact_inventory.csv: per-run calibration/refit traces, actual batch logs, selected/final checkpoints/manifests, runtime/results; paired scores/tables; parameter IDs; proposals/actual decisions; source/checkpoint audits; dashboard QA; guides and sealed inventory. Checkpoints are intentionally local/gitignored. All other new small metadata/code/docs are left for human Git review, not staged.

## 5. Files modified

- src/lstm_data/real_bridge_run.py
- src/lstm_data/real_bridge_authority.py
- src/lstm_data/batch_telemetry.py
- src/lstm_data/visualization/loaders.py
- src/lstm_data/visualization/figures.py
- apps/track_a_dashboard.py
- configs/track_a_visualization_v1.json
- configs/CURRENT_EXPERIMENT_REGISTRY.json
- docs/track_a/Visualization_Quickstart.md

Shared trainer adds exact controlled-authority dispatch, seed-bound sampler/init, isolated objective/canonical inverse/cap, actual telemetry and pre-STARTED target/panel verification. Defaults preserve legacy behavior. Authority admits exact sealed controlled type and excludes only Finder `.DS_Store` from source identity. Observer adds backward-compatible seed/cap/arm fields and v2 tag. Existing dashboard adds read-only arm/seed discovery and genuine cap5 display, preserves old choices and exposes corrected historical both-pass G6. Configs register actual conditional science starts and saved results. Quickstart links exact guide. docs/track_a/RandomNotes.md is a concurrent human edit, never edited here.

## 6. Files deleted, renamed, or moved

No pre-existing file deleted/renamed/moved. Known new unapproved drafts moved within the fresh packet to preapproval_draft_01; pre-STARTED launcher logs archived with prestart_launcher_* names. No raw file restored or removed.

## 7. Critical functions, classes, variables, and config keys

- LossPolicy(arm,cap,scale), canonical(Tensor), objective(logits,target,origins), clip: controlled_loss.py. Pure one-factor adapter; no raw mutation or future statistic. fit_policy(RealInputView,arm)->dict binds lawful prefix/view/preparation/population and deterministic parameter_id.
- ControlledAuthority / authority(root,plan_ref,approval_ref,name): controlled_authority.py. Exact sealed human/code/data/config permission; inputs()/view()/policy() reuse stock readers; ensure() fails closed; append() atomically links monotone STARTED/CALIBRATED/REFITTING/COMPLETED/FAILED journal. Fixed QUEUE (18), JOURNAL v4, ceiling 40, opening 6. Failed starts count; no retry/reorder/overlap.
- controlled_batch.prepare(out), main(): one-shot preparation and supervised sequential whole-pair queue with actual-runtime projection, deadline/report reserve and explicit --plan/--approval. No implicit authority or outer-score branch.
- Existing epoch_pass/run_worker remain the only real loop/lifecycle. Canonical original-scale MSE always selects; T2 inverse exactly once; fresh seeded model/empty optimizer; refit exact selected epochs. BatchTelemetry.record remains detached observational scalar logging after optimizer.step; v1 defaults unchanged, v2 names actual cap/seed/arm.
- controlled_review.review(out,plan_path), audit_batches, checkpoint_metadata, verify_tables: read-only source/mask/target, D6g/G6/step/session/checkpoint audit; compact canonical tables and seed/fold differences, exploratory 5-session intervals, source bindings and optional CSV-only recomputation. No fit/write to raw; review exporter writes only new derived files plus requested visualization config registration.
- Dashboard controlled_models/controlled_telemetry/both_pass_health/global_started_at_seal: explicit model-family metadata; saved scores have canonical units and no second inverse; both historical and actual clipping are labeled. Current experiment pointer activates approved registryv4 only at first STARTED; CURRENT_PROTOCOL unchanged.

## 8. Data/schema/provenance changes

No new source or candle/window store. Existing genuine stock canonical components, lawful June2023/December2023 recipes and mature/purged/as-of masks reused. T1/T2 parameters independently fitted inner/full prefixes from unweighted pooled unique session/origin/stock observations in float64; tensors remain float32. Actual engineering computation October2026, historical cutoff is population boundary, not historical publication. New compact long prediction rows carry fold/seed/arm/symbol/origin UTC/canonical TG0/authority/checkpoint;20 panels×1160scores,232origins/116days each. Training raw TG0 reaches84.416 inWF2; none excluded or capped in evaluation. New CSV schemas documented in guide/API; original controls/source/archive/checkpoint hashes preserved. Finder OS metadata exception and authorized config changes are explicitly audited.

## 9. Dependency/environment changes

None. Existing repository .venv and declared neural/visualization extras used. CPU float32/one thread, deterministic registered seeds 42/123. Actual Python/Torch/NumPy/platform/RSS/version details in each training_actual_runtime.json and resource_and_elapsed.json. No package installation, environment variable or severity change.

## 10. Commands and tests run

Exact major commands/results in commands.md, final_pytest.txt and final_pylance.json.72 focused pytest cases pass in16.38s;0 failures,1 existing runpy warning. Includes original bridge/multimodel authority, checkpoint, leakage/mask and observer/update/RNG oracles. No expensive unchanged legacy learning proofs. Ruff check . and owned diff check pass. Full diff reports only concurrent human Notes trailing blank line, preserved.

Exact full static command: `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist` —200 owned Python files,0 errors,0 warnings. No suppressions/exclusions or severity reductions. Editor: select workspace .venv/bin/python, keep installed Pylance basic/stub parity, refresh/restart language server and Problems; final editor UI refresh requires human confirmation and was not claimed.

Dashboard setup PASS;54 actual adapter reconciliations,15 AppTest interactions PASS; HTTP health200/HTML200 and own server SIGINT exit0. Nonfatal sandbox Arrow sysctl/bare-mode warnings retained. Initial localhost socket test failure passed under approved sandbox permission. Read-only recomputation matches20 panels/23,200 scores,0 optimizer steps/0 confirmation rows.

## 11. Experiment/results summary

All four arms are **MIXED_OR_INCONCLUSIVE**. T2 improves MSE in 4/4 cells and IC in 3/4; every IC interval spans zero. H1 has no sustained clipping warning but favorable paired MSE+IC in only 1/4 cells. T1 has favorable paired point estimates in 3/4, with warnings retained and a reversal at seed 123/WF1. O1 has worse MSE and IC point estimates in 4/4 cells despite much less applied clipping at cap5; these are valid poor scores, not invalid runs. No numerical/integrity failure or automatic finalist promotion occurred.

H1/T2 G6 changes **W→P in both folds at both seeds**; T1/O1 remain W. P means both-pass telemetry PASS, W means warning from at least one epoch/pass. For O1 the historical norm>1 warning remains separate from its actual cap5. Calibration applied clipping is 0–0.19% for H1 and 0.49–2.94% for T2; their refits have 0%. O1 calibration actual clipping is 0.16–1.00% and refit 0%, but its predictions worsen. See target_tail_and_clipping.csv for all actual fractions and the explicitly missing historical WF1 batch summaries. Lower norms can follow a smaller derivative or changed units; causation is not established.

ZERO remains competitive: seed 42 T1/WF2 and T2/both folds beat ZERO on MSE; no intervention beats ZERO at seed 123. Every model uses the same 232 origins/116 days/1,160 stock scores per fold. All 23,200 saved scores are finite with no forecast constants/ties. Original TG0 extremes remain: up to 84.416 in full training and 39.403 in development. The original seed 42 controls are reused, never refitted.


All new cases seed 42/123,WF1 July–December2023 /WF2 January–June2024 development, stock-only candidate AAPL/COST/CMCSA/SBUX/CME. Calibration/fresh-refit pair IDs/proposals/approval/code/data/parameter/checkpoint hashes in registry/results. Total neural fitting 910.756 s and sequential supervised queue 1465.818 s. No economics, alpha, full G8 or confirmatory result. All source limitations remain ASSUMPTION_CONDITIONAL.

## 12. Reproduction instructions

Use README authoritative.venv setup and existing declared extras. Provision only legitimately entitled documented artifacts under project-relative paths; no redistribution was granted. Launch `./scripts/run_track_a_dashboard.sh`; follow HOW_TO_VIEW_PACKAGE_011.md. CSV-only no-fit reproduction: `.venv/bin/python -B -m lstm_data.controlled_review --output reports/data_audit/ta011_controlled_interventions_2026-10-15_124546 --verify-only`. Must return READ_ONLY_RECOMPUTATION_MATCH/20 panels/23,200 forecasts/0 optimizer/0 confirmation. Source and artifact hashes must match sealed bindings; local weights are optional for compact saved-score inspection. Historical fit commands are consumed/deadline-bound and must not be rerun; any new fit needs a new actual grant/namespace, not this report.

## 13. Git / collaboration status

Branch feat/track-a-data-intake, HEAD 62f5cf20a8f916563f495d2419be7709499d55f3; no commits created. Fetch succeeded; ahead/behind 0/0. Full final short status in git_status_final.txt and report present there. All new files uncommitted; existing modifications listed above; concurrent Notes preserved. Likely conflict areas: shared trainer/authority/observer, visualization loader/config/current registry. Do not pull/rebase over this dirty tree. Human review may prepare a focused code/config/docs/report PR; keep Notes separate and review sharing rights for data-derived outputs. No stage/commit/push authorized or performed.

## 14. Known issues, risks, and limitations

No final failing tests or reproducible static diagnostics. All IC intervals cross zero; multiple comparisons, two related market folds and two seeds do not provide full G8 or independent market histories. Some seed 42 scores beatZERO MSE but not atseed 123. Loss scale and clipping changes cannot identify root cause; measured batch associations are dependent, not per-example causal gradients. Original WF1 paired batch history remains NOT_RECORDED, never fabricated. G6 warnings from calibration persist despite quiet refits; O1 historical >1 and actual5 are separate.

Private researcher-attested source rights/shared clock, retrospective surviving universe/actions, idealized availability and hourly-close price proxy remain unverified facts; strict observed-causality certification false. No licensing/action/PIT/publication/course/execution/production or alpha certification. No confirmation access. Parameter fitting occurred now, not historically.

First real launcher stopped pre-STARTED because external Finder `.DS_Store` changed; raw vendor bytes unchanged. Narrow exact-filename source guard correction and explicit launcher plan binding received actual renewed approval before every real fit. Initial unapproved prepare refresh hit atomic-new FileExistsError; drafts preserved. No scientific identity was consumed/retried by these prefit failures. All 18 actual starts completed. Timestamp-component limits and RSS scope are in resource_and_elapsed.json; full-prefix preprocessing was prechecked, later timer is cached lookup, and unprofiled pre-start/journal work is not falsely assigned. Browser drawing and human editor refresh remain unverified, not claimed.

## 15. Decisions requiring human or teammate review

No approval pending for this completed exact scope. Record all arms inconclusive and retain controls; decide separately whether unchanged T2 deserves independent evidence; keep confirmation/source/course/production decisions outside this package. Remaining16 slots are not automatically spent. Human editor Problems refresh/confirmation and Git integration remain human tasks. No private emails or teammate messages requested/sent.

## 16. Next recommended steps

Inspect paired table and worst raw-TG0 days using guide; distinguish apparent MSE improvement from robust ranking gain. Review O1's consistently worse estimates despite lower applied clipping. Retain frozen arms/constants and candidate limitations. Any next experiment must use a separately reviewed question/manifest/authority; do not retune on these folds or open confirmation automatically. STOP here.

## 17. Artifact inventory

reports/data_audit/ta011_controlled_interventions_2026-10-15_124546/artifact_inventory.csv itemizes every packet/source/config/doc/test/report path, type, purpose, bytes, SHA and tracking intent. Important tables: predictions_long,model_metrics,model_by_fold,metrics_daily,metrics_by_origin/month/epoch,paired_fold_seed_comparison,per_day_differences,monthly_paired_differences,seed_variability_within_fold,temporal_variability_within_seed,target_tail_parameters,target_tail_and_clipping,canonical_target_tail_and_loss,historical_baseline_context. plot_handoff contains only reused data pointers. Checkpoints/local runtime logs are original per-pair artifacts; weights gitignored. Proposals/actual approvals,72-event journal,source/checkpoint audits,checks/resource/preservation/bindings,QA and guides are linked from the card. No raw archive or dense feature-window copies.
