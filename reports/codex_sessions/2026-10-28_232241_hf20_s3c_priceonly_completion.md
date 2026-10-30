# Codex Session Report

## 1. Session metadata

- Completion: 2026-10-28T23:22:41.389063-04:00; Codex S3-C price-only implementation/execution and resumed supervision.
- Requested: complete the authorized four-fold candidate, resume the existing Python process without another experiment/restart, finish verification/reporting.
- Branch: feat/track-a-data-intake. Starting/ending HEAD: 997b30cff98785911b0e33b7e3d2e72f61b8270b. No commit/PR.
- Opening tree dirty: registry successor from earlier sessions, S2D and Stage3 Session1/2 code/tests/reports untracked. Preserved. Closing tree retains those plus this candidate's files.

## 2. Executive summary

Completed all four existing selector/refit pairs; same original80260/4013/793 evaluation. Calibrated equal-year MSE+0.069329% versus CLOCK-C3, descriptive interval spanszero; IC0.327834 versus0.330254. Keep CLOCK-C3; no incremental evidence. Ledger170→174/300; no training restart/retry. See reports/experiments/hf20_s9_mag_stage3_s3c_priceonly_2026-10-28/S3C_PRICE_ONLY_RESULTS.md.

## 3. Research/protocol impact

Only prospectively authorized price-only60×5 H8 latefusion with original48×16/H32/10clocks,6931parameters. No target/universe/calendar/split/weight/trading change. SameM-space training,seed42,selector and ownOct–Dec C3κ25. Former volume-based S3C staysBLOCKED; B stayscompleted. No2025market/protected2026access/finaltest release. One candidate; no search or new baseline.

## 4. Files created

- src/lstm_data/hf20_s3c_priceonly.py: bounded OHLC adapter, masked input/model, all-fold readiness, single-use selector/refit lifecycle.
- src/lstm_data/hf20_s3c_price_report.py: saved-score exact-key comparisons/diagnostics/month bootstrap, no fitting/inference.
- tests/test_hf20_s3c_priceonly.py: six focused research-critical fixtures;23tests with inherited coverage.
- reports/experiments/hf20_s9_mag_stage3_s3c_priceonly_2026-10-28/: frozen protocol/readiness/source, compact native feature cache, four phase/selection/checkpoint/score sets, own calibration tables, metrics/groups/paired results, verification/static receipts, scientific report and handoff. artifact_inventory.csv enumerates files/types/sizes/hashes; large arrays/checkpoints/Parquets ignored, small reports/code untracked pending human Git review.
- This session report: required reproducibility/collaboration handoff.

## 5. Files modified

configs/CURRENT_EXPERIMENT_REGISTRY.json only existing file: authorized schema32→33 successor points to this frozen protocol and append-only current journal, with fit_permission=false. Git diff includes inherited previous registry changes; no historical journal entries edited. Current generated report was finalized with interpretation after scores froze.

## 6. Files deleted, renamed, moved

None. No reset/restore/clean/stash/rebase, bulk copy or source rewrite.

## 7. Critical interfaces and invariants

price_channels(prices, observed): nativeRET/RANGE from positive compatible genuine OHLC, no bridged returns, missing payloads inert. five_channels(native, observed, floors):60×5 using own-phase h; masks/position fixed. PriceOnlyMAG/PriceView: originalhourly history and known clocks plus gatedH8; allmissing embedding exactlyzero. model_for_price: seed42,assert6931. construct/prepare: unique newest-hour reuse, allfour role/key/source/scale gates, no volume normalizer. run lifecycle:16complete-session batches,mainM selector,freshrefit,unchanged checkpoint acrosscal/OOS. equal_year/report: canonical annual scores then equalyears; descriptive shared bins; no model choice. Public CLI --source/--prepare/--run rejects duplicate namespaces. All-source/phase dependencies are existing project-relative artifacts.

## 8. Data/schema/provenance

Pinned mito0o852/OHLCV-1m revision776328445b7ac6e7815ef3a483e9c8ded1eb6d56; receipt-bound local canonical_observed through2024, OHLC/time/ticker only plus necessary existing adjustment/quality metadata.159monthly projections;14628uniquehours;17452556genuine positions;zero empty stockhours. Prior footprint covers allnewblocks. Approxorigin+2min timingproxy and retrospective action/quarantine vintage remain. Original20ticker order and48completed blocks untouched; sourceflags not learned issue codes. New private cache nativeRET/RANGE andobservationmask only; no dataset migration.

## 9. Dependencies/environment

None added/changed. Existing .venv CPUfloat32,Pytorch/Arrow; no package/environment adjustment. Actual installed Pylance2026.4.1/basic parity retained. Nonfatal Arrow sandbox hardware-cache sysctl warnings disclosed.

## 10. Commands/tests

Exact CLI commands recorded in reports/experiments/hf20_s9_mag_stage3_s3c_priceonly_2026-10-28/SESSION_HANDOFF.md, source_execution.log, preparation.log, execution.log, report_execution.log. Existing training session61912/PID68169 continued toF24completion; no second --run invocation on resume. Saved verifier `/private/tmp/verify_s3c_price.py` → verification.json PASS; no inference. Focused pytest23passed3.57s; Ruffnew3filesPASS. Full static command:

```sh
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist
```

522files,0errors,0warnings,189.708s; full_typecheck.json. Prefit position fixture initially mismatchedfloat32/64 exactness and dynamic testbias attributes triggeredstub errors; correctedtestexpectation/access only beforefit, no scientific kernel change, noignored diagnostics. Final focused/full checks pass. gitdiff--checkPASS. Editor instructions: selectrepo.venv,retainbasicseverity,reloadPylance/Problems andconfirmzeroerrors; human visual refresh outstanding. Sandbox ps inspection denied late in supervision; completed per-fold records/managed session closure and journal establish run completion without restarting.

## 11. Results

4/4COMPLETED; selectedepochs29/13/22/16; all6931params, freshoptimizer/reloadmaxerror0. PrimaryMSE 0.000106739896737;CLOCK0.000106665945886;delta+7.395085e-8,95%[-1.4050045e-7,2.6386056e-7]. Threeannual losses,onegain. IntradayMSE−0.089787%,overnight+0.107268%;ordinaryprefix95complement+0.645795%,tail−0.105533%. No incremental evidence. No trading metrics. Exploratory/post-search only;400monthdraws/seed22042,notselection-adjusted. Four fit times total4571.54s. TrainingpeakRSS1185546240bytes;project12822974464/task162687464bytes atfinalfit,belowcaps.

## 12. Reproduction

Use unchanged authoritative project environment and approved pinned local data/phase artifacts. Commands in SESSION_HANDOFF; do not rerun completed single-use source/prepare/run. Existing saved-score report can be recomputed without training, but no need to overwrite these final results. A fresh research reproduction requires a separately approved new namespace. Large ignored checkpoints/cache/scores must be supplied as documented external artifacts on another machine; no claim they are inGit. Ephemeral verification results are preserved as JSON; main report computations resideinversionablemodule.

## 13. Git/collaboration

No commits/push/fetch/network (current research boundary overrides genericfetch workflow). Cached upstream0ahead/0behind,notfreshremoteverification. Preserve allopeningdirtyfiles. Humanreview thenstageonlythissession's2modules,1test,smallnamespaceoutputs/sessionreport andappropriate registrysuccessor; inspectinheritedregistrydiffbeforecommit. Do notstageprivatearrays/checkpoints/Parquets ormergeoverotherdirtywork.

## 14. Risks/limitations

Timingproxy/actionvintage/survivorship;488extraparams+missingnessconfounders;BversusCdifferentinformationreach;no latest-hour fittedsummarycontrol authorized. F24calibrationeffective30.69/32.96sessions. Conditionalintervalsomitselector/calibrationuncertainty and repeatedinspection. No knownfailingtests; humaneditorrefreshstillpending. Fullprotectedsourceimmutabilityisnotclaimedfromabroadrescan: exactboundpredecessorassets andprefithashes verified, no forbiddenhashing.

## 15. Human decisions

Review near-tied/negative result; retainCLOCK-C3. HumaneditorProblemsconfirmation andGitreview pending. AnyS3D/E,Stage5,extra controls/seed/features,volatilitybenchmarks orprotectedrelease requires newauthorization. Deferredintraday/routingchoices untouched.

## 16. Next steps

Researcherreviewonly. No automatic model promotion, training or background follow-up.

## 17. Artifact inventory

reports/experiments/hf20_s9_mag_stage3_s3c_priceonly_2026-10-28/artifact_inventory.csv enumerates protocol/source/readiness/coverage/tests/logs, per-fold phaserecipes/training/selection/modelhashes/checkpoints/scores, owncoefficients, metrics/groups/pairedMSE, reports andhandoff. JSON/CSV/Markdown small artifacts pendingGitreview; `.pt/.npy/.parquet` intentionallyignored. No plots/dashboard edits. reports/experiments/hf20_s9_mag_stage3_s3c_priceonly_2026-10-28/verification.json certifies fourfold keys/reload/calibration/hierarchy andpreservedbindings; final_integrity.json records completion checks.
