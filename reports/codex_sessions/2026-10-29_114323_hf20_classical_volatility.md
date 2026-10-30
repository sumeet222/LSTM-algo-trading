# Codex Session Report

## 1. Session metadata

- Date: 2026-10-29; Codex classical benchmark session.
- Task: one bounded, non-neural study of original four-hour magnitude forecasts.
- Branch: `feat/track-a-data-intake`.
- Starting and ending HEAD: `997b30cff98785911b0e33b7e3d2e72f61b8270b`; no commit or PR.
- Opening tree: dirty registry and earlier S2D, Stage3 and Stage5 code, tests, reports and handoffs. All preserved. Closing additions are this study's four modules, one test, experiment namespace and session report.

## 2. Executive summary

PARTIAL study: rolling20/60/expanding, EWMA-R2-folded-normal, EWMA-A and HAR-RV-A completed four folds. GARCH was blocked before fitting because scipy, arch and statsmodels are absent; no package installation or substitute was attempted. Each of the six completed arms has its own global calibration per fold.

No completed calibrated classical arm closes the MSE or ranking gap to CLOCK-C3/S2C-C3. HAR-CAL MSE is0.000109068193648, 2.2521% above CLOCK and2.3652% above S2C. ROLL60 has the highest classical IC,0.318689978 versus CLOCK0.330254043. Calibration-neutral and tail comparisons give different trade-offs. All evidence is exploratory/post-search. Neural ledger remains186/300.

## 3. Research/protocol impact

The target remains absolute genuine240-trading-minute endpoint log return, with the original20 stocks,80,260 keys,4,013 origins,793 sessions, DesignA roles,48-step embargo and hierarchical weights. Fixed parameters use the restricted September prefix; only matured observations update dynamic states. Own Oct–Dec global raw-A calibration is separate from frozen neural C3 calibration.

Two explicit user amendments were recorded before fitting: full-session pre2025 minute-close access, including the closing half-hour, for HAR; and chronological greedy de-overlap of EWMA-R2 history only. Exactly59 history intervals are excluded, leaving zero overlaps. Evaluation keys and other models' histories are unchanged. No additional target, neural model, trading rule, search, calibration family or protected release was introduced.

## 4. Files created

- `src/lstm_data/hf20_classical_math.py`: conversion, state update, calibration, de-overlap, RV, causal lag features and fixed ridge arithmetic.
- `src/lstm_data/hf20_classical_rv.py`: bounded receipt-bound minute source checks and compact daily RV.
- `src/lstm_data/hf20_classical.py`: protocol, readiness, history/model fitting and guarded export lifecycle.
- `src/lstm_data/hf20_classical_report.py`: saved-score reporting and paired month-block comparisons; no fitting.
- `tests/test_hf20_classical.py`: six numerical/causality fixtures.
- `reports/experiments/hf20_s9_mag_classical_volatility_benchmarks_2026-10-29`: frozen protocol, readiness, source/history/role audits, compact daily RV, four fold parameter/calibration/forecast sets, comparison tables, logs, verification and reports. `artifact_inventory.csv` enumerates individual files.
- `reports/codex_sessions/2026-10-29_114323_hf20_classical_volatility.md`: this mandatory handoff.

## 5. Files modified

No pre-existing repository file was changed by this session. The already-dirty registry remains byte-identical. A logger bug in the newly created runner was fixed after F21 outputs were saved, with immutable failure/recovery receipts and a code diff. Its numerical functions were unchanged. The new report's zero-forecast rate was corrected to use canonical weights, followed by a saved-score replay without fitting. No predecessor kernel, test, model, score or report changed.

## 6. Files deleted, renamed or moved

None. No reset, clean, restore, stash, merge, rebase or bulk source copy.

## 7. Critical interfaces

`history` and `stream_masks` preserve original eligible stock-slot history and apply greedy endpoint de-overlap to R2 only. `dynamic_forecasts` uses fixed September parameters and observations with maturity strictly before issuance; it saves the latest used maturity for every forecast. Prefix seed burn-in is applied once.

`build_rv` streams one month at a time, preserves390 scheduled positions, applies saved adjustment/quarantine policy, and reconciles counts and genuine terminal closes. `har_features` uses only prior1/5/22 regular sessions; `ridge_fit` uses training-only normalization, ridge0.01 on slopes and an unpenalized intercept. `multiplier` fits one global nonnegative raw-A correction on the independent calibration role.

`--prepare` and `--run` are single-use. The special `--resume-unstarted` requires the exact recorded F21 logger failure, unchanged F21 files and absent F22–F24 outputs. It cannot be reused now. `--report` reads saved scores and performs no fitting or inference.

## 8. Data/schema/provenance

Pinned dataset `mito0o852/OHLCV-1m`, revision `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`. Used174 existing receipt-bound monthly files through2024, projecting OHLC/timestamps/quality and saved hourly factor/basis/quarantine/count/close metadata; no minute volume or new source.

Checked27,955,304 minute rows,18 quarantined rows and506,520 hourly/stub bins, with zero terminal-close discrepancy. Compact daily RV covers2010-07-01 through2024-12-30:3,618 regular days,72,360 stock-days,67,038 valid at370/389 adjacent pairs. HAR fallback is frequent for AVGO, MA and AMZN; this is disclosed, with no scoring-row drops.

No source migration. New score stores combine all arms per fold to avoid repeated source/target copies. Original source curation, action vintage, survivor population and approximately+2-minute availability proxy remain limitations. No2025 market or protected2026 content, path or hash was accessed.

## 9. Dependencies/environment

No package, environment, interpreter, severity, exclusion or ignore changes. Existing NumPy/Pandas and repository .venv used. GARCH dependencies are absent. Imported historical metadata utilities depend on Torch, but no neural model or optimizer was instantiated. Installed Pylance2026.4.1/basic retained.

## 10. Commands and tests run

```sh
.venv/bin/python -u -B -m lstm_data.hf20_classical --prepare
.venv/bin/python -u -B -m lstm_data.hf20_classical --run
.venv/bin/python -u -B -m lstm_data.hf20_classical --resume-unstarted
.venv/bin/python -B -m lstm_data.hf20_classical --report
.venv/bin/python -m pytest tests/test_hf20_classical.py tests/test_hf20_mag_rank.py tests/test_hf20_stage2_bcd.py -q
.venv/bin/ruff check src/lstm_data/hf20_classical*.py tests/test_hf20_classical.py --output-format concise
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist
git diff --check
git status --short --branch
git rev-list --left-right --count 'HEAD...@{upstream}'
```

Six prefit fixtures passed;18 combined tests passed in3.78s. Ruff passed. Affected installed-stub check: five files, zero errors/warnings. Final whole-project Pylance check:533 owned files, zero errors/warnings in89.201s. Receipts retained. Human editor verification remains outstanding: select repository .venv, retain basic severity, refresh Pylance/Problems and confirm zero errors.

Prefit fixtures caught and corrected a read-only Pandas array mutation and timestamp microsecond/nanosecond mismatch. All timestamp comparisons now explicitly use nanoseconds. An early scratch type-check invocation incorrectly included unrelated temporary files; it was replaced by the proper relative-path installed-stub profile. No diagnostics were hidden or severity weakened. Arrow CPU-cache sysctl notices were nonfatal. P2 register hashes verified16 entries; unrelated scientific holds remain.

Execution failure: F21 fit parameters, calibrations and score files were saved, then the completion logger raised duplicate `year`/`status` keywords. The original traceback and FAILED entry remain. Before any OOS performance calculation, those F21 files were hash-frozen. Only logger/recovery flow changed; numerical function ASTs were identical. Resume fitted only the unstarted F22–F24 folds, once each. Exact F21 runtime/peak telemetry was lost at logging, although its resource-ceiling check had passed. All recovery receipt versions remain.

Independent verification replayed every rolling mean, every HAR stored-coefficient forecast, all calibrators, keys/weights/labels and336 closed-form EWMA cases; checked every maturity frontier,171 explicit bindings and174 minute hashes; and verified F21 remained byte-identical. Thirteen frozen comparator arms reproduce archived annual/equal-year category metrics. Verification logs and JSON/CSV receipts persist. No model was refitted for verification.

## 11. Experiment/results summary

All six completed arms retain the exact four-year panel. HAR-CAL versus CLOCK paired MSE delta is+2.40225e-6, descriptive interval[1.25862e-6,3.89825e-6]. ROLL60 IC delta is−0.0115641 [−0.0169563,−0.00644209]. HAR-UNCAL beats CLOCK-RAW MSE by4.6452%, but the fixed calibrated package comparison reverses this result. Classical tail errors can improve while ordinary errors and event retrieval worsen. No promotion or trading conclusion.

Fitting counts:560 HAR regressions,560 R2 stock-slot parameter sets,560 EWMA-A seed sets and24 global calibrations; rolling arms require no optimized parameters. Zero GARCH attempts and zero neural starts. Measured source preflight peak458,260,480 bytes; resumed fitting peak554,811,392 bytes; verification454,590,464 bytes. F22–F24 run segment15.159s is not the total four-fold runtime. Final task/project usage is recorded in `final_integrity.json`, below2.5GB/15GB.

## 12. Reproduction instructions

Use the documented project setup and approved artifacts bound in `protocol.json`. `--report` replays tables from saved scores and role/phase metadata without source extraction, fitting or calibration. Do not repeat consumed `--prepare`, `--run` or `--resume-unstarted` commands, or evade guards using another name. A fresh fit requires separate research authorization. Private ignored data/forecasts require the existing legitimate transfer procedure. Formulas, history rules and fallback recipes are in the main report and protocol.

## 13. Git/collaboration status

Named branch unchanged; cached upstream is0 ahead/0 behind. No fetch/network under the explicit task restriction, so this is not current remote confirmation. No commit/push. Existing dirty work and registry preserved. Review and stage only the four new modules, test, appropriate small reports and session handoff; do not stage private Parquets or unrelated work. Do not pull or merge over unknown dirty changes.

## 14. Known issues, risks and limitations

GARCH is untested, so the result does not rule out classical models generally. HAR source missingness is stock-dependent, and coverage normalization assumes representative missing pairs. R2 thinning prevents interpreting its comparison with EWMA-A as a pure conversion ablation. Calibration families and available histories differ. Static score-variance fractions are not fractions of predictive accuracy. Repeated historical inspection, source vintage and timing uncertainty remain. Logger failure/recovery is fully documented; exact F21 telemetry is unavailable. No residual focused/static failure; editor refresh remains human work.

## 15. Decisions requiring human review

Review the partial scientific result and source-coverage limitations. Any GARCH dependency installation/execution, richer classical model, neural sweep, calibration rescue, blend, next stage, trading or protected release requires separate approval. Human VSCode Problems confirmation is pending.

## 16. Next recommended steps

Researcher review only. Preserve all positive, negative, near-tied and blocked evidence. No automatic winner promotion, fitting or background follow-up. STOP.

## 17. Artifact inventory

`artifact_inventory.csv` lists paths, types, sizes, hashes and ignored status. Main outputs: frozen protocol/readiness, source/RV/history audits, four parameter/calibration/OOS sets, metrics/groups/rank/tail/paired/static-dynamic tables, execution/recovery logs, verification/static/test receipts, `CLASSICAL_VOLATILITY_BENCHMARK_REPORT.md`, `SESSION_HANDOFF.md` and final integrity receipt. No plots, dashboards, checkpoints or raw-source copies were added. Small artifacts remain untracked pending review; binary derivatives remain private where existing ignore rules apply.
