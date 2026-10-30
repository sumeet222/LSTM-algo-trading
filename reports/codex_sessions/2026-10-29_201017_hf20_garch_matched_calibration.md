# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-29T20:10:17.757350+00:00, Codex bounded GARCH/matched-calibration execution.
- Task: complete dependency-blocked B3 once; compare frozen magnitude predictors under common G/IO.
- Branch: feat/track-a-data-intake.
- Starting/ending HEAD: 997b30cff98785911b0e33b7e3d2e72f61b8270b; no commit/PR.
- Opening tree already dirty: registry and earlier S2D/Stage3/Stage5/classical work. Preserved. Exact initial/final status snapshots are in the experiment directory.
- Git fetch/commit/push and external API calls prohibited. Only authorized Python-index dependency access occurred.

## 2. Executive summary

Matched calibration COMPLETE: nine models × G/IO × four folds, all80,260 keys. Neural calibrated MSE edge remains: HAR versus S2C +2.0788% under G and +2.4212% under IO, HAR lower in0/4 folds. Strongest classical IC ROLL60 .318689978 versus S5C .332045935, lower in all4 folds. Raw HAR MSE still beats neural RAW; MAE and intraday comparisons have tradeoffs.

GARCH dependency resolved; scientific arm PARTIAL_BLOCKED. Exactly560 attempts,557 admissible; COP F22 15:30/F23 13:30/F24 15:30 converge at alpha+beta=1, violating strict stationarity. No retry/fallback/full-score omission. This is an admissibility block, not negative GARCH performance. Original BLOCKED_DEPENDENCY record unchanged.

## 3. Research/protocol impact

Only authorized Gaussian GARCH(1,1) and common G/IO calibrators added. Target,20-stock order,horizon,keys,roles,embargo,source vintage,execution proxy,tail thresholds,reducers and costs unchanged. No trading,protected release,2025numerical research,feature edit or neural call/start. Ledger186/300 authenticated. Strict stationarity and maxiter1000/tol1e-9 were frozen before fitting. One-next-same-slot-event approximation expressly qualified; variable event spacing/calendar composition is not continuous-time four-hour variance. No OOS-selected calibrator or model promotion.

## 4. Files created

- src/lstm_data/hf20_matched.py: guarded task CLI, saved RAW decoding, two common calibrator applications, append-only journal and preservation checks.
- src/lstm_data/hf20_matched_math.py: common G/IO coefficients/application, strict maturity index, one-step variance recurrence.
- src/lstm_data/hf20_matched_garch.py: independent overlap audit, exactly-once arch fitting, per-unit diagnostics and causal state replay export.
- src/lstm_data/hf20_matched_report.py: archived reducer-based complete grid, descriptive pairs, groups/tails and coefficient/comparator parity verification.
- src/lstm_data/hf20_matched_verify.py: independent stored-prefix and every-state-update replay without fitting.
- tests/test_hf20_matched.py: folded-normal quadrature/limits, scale/recursion, maturation/de-overlap, calibration/effective-session and supported-arch fixtures.
- reports/experiments/hf20_s9_mag_garch_matched_calibration_2026-10-29: reports, forecasts, coefficients, diagnostics, receipts, scoped .gitignore and append-only journal; artifact_inventory.csv inventories final artifacts.
- configs/track_a_hf20_classical_matched_successor_v1.json: appended audited successor pointer; existing live neural registry unchanged.
- reports/codex_sessions/2026-10-29_201017_hf20_garch_matched_calibration.md: this report.

## 5. Files modified

- pyproject.toml: optional classical extra pins scipy1.18.1,arch8.0.0,statsmodels0.14.6,patsy1.0.3. Existing dependencies unchanged.
- README.md: optional environment/replay instructions; pinned optional extra needs Python>=3.12, executed3.14; core3.11 support unchanged.
- No predecessor code,report,forecast,checkpoint,raw data,journal or contract changed. Dirty CURRENT_EXPERIMENT_REGISTRY.json byte-preserved.

## 6. Files deleted/renamed/moved

None.

## 7. Critical interfaces

fit_common(cal,prediction)->list[dict] accepts only authenticated calibration-role rows; apply_common(frame,prediction,coefficients,family)->ndarray never reads outcomes. n_eff uses normalized category session masses; kappa25 fixed. Global36 plus category72 raw coefficients support72 model/fold/family comparisons; no hyperparameter fitting.

next_variance(h,observed,mu,omega,alpha,beta)->float updates h_n to h_(n+1) from matured percent-scaled signed x_n. mature_prefix uses searchsorted(side=left), excluding equality at issue. admitted independently reproduces59 chronological overlap exclusions within the same slot; every stock shares original complete-panel history support. Evaluation keys remain intact.

GARCH fitting uses only restricted role values. Future endpoint states never enter predictions; later mature histories update state but not parameters. Single-use started files guard task/unit fits and calibration. Report/verify commands never call model or calibration optimizers or neural inference. Partial GARCH outputs cannot enter load_panel/calibration unless all560 pass.

## 8. Data/schema/provenance

Pinned revision776328445b7ac6e7815ef3a483e9c8ded1eb6d56; original genuine endpoint derivative, role masks and frozen calibration/OOS predictions. No raw minutes reopened or source rebuilt. Neural RAW replay uses frozen Mhat and restricted scale, bitwise OOS decoder equality. Canonical keys/labels/weights checksums match all models before scoring. Saved daily RV missingness only adds descriptive coverage cohorts. Log-return outputs, squared log-return MSE; arch uses x=100R and h/10000 conversion. Times timezone-aware UTC with original Eastern schedule/early-close categories. Source policy and historical +2minute publication limitation unchanged.

## 9. Dependencies/environment

Existing .venv Python3.14 only. Four packages added: scipy1.18.1,arch8.0.0,statsmodels0.14.6,patsy1.0.3. No existing installed package changed; torch2.10.0 untouched. Before/after freeze, constrained dry run, exact install report and wheel SHA256 lock retained. pip check passes. First sandbox PyPI resolution failed; approved escalation permitted only Python-index access. No environment-variable changes/global installs/new environments. Optional extra needs Python>=3.12 and compatible platform wheels; locked wheel hashes are this arm64 Python3.14 build.

## 10. Commands and tests run

```sh
.venv/bin/python -B /private/tmp/hf20_match_readiness.py
.venv/bin/python -m pip install --dry-run --only-binary=:all: --no-cache-dir --constraint reports/experiments/hf20_s9_mag_garch_matched_calibration_2026-10-29/existing_constraints.txt --report reports/experiments/hf20_s9_mag_garch_matched_calibration_2026-10-29/dependency_plan.json 'scipy>=1.16,<2' 'arch>=8,<9' 'statsmodels>=0.14.5,<0.15'
.venv/bin/python -m pip install --only-binary=:all: --no-cache-dir --constraint reports/experiments/hf20_s9_mag_garch_matched_calibration_2026-10-29/existing_constraints.txt --report reports/experiments/hf20_s9_mag_garch_matched_calibration_2026-10-29/dependency_install.json scipy==1.18.1 arch==8.0.0 statsmodels==0.14.6 patsy==1.0.3
.venv/bin/python -m pip freeze
.venv/bin/python -m pip check
.venv/bin/python -m pytest tests/test_hf20_matched.py tests/test_hf20_classical.py tests/test_hf20_mag_rank.py tests/test_hf20_stage2_bcd.py -q
.venv/bin/ruff check src/lstm_data/hf20_matched*.py tests/test_hf20_matched.py --output-format concise
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist
.venv/bin/python -u -B -m lstm_data.hf20_matched garch
.venv/bin/python -u -B -m lstm_data.hf20_matched calibrate
.venv/bin/python -u -B -m lstm_data.hf20_matched report
.venv/bin/python -u -B -m lstm_data.hf20_matched verify
.venv/bin/python -u -B -m lstm_data.hf20_matched_verify
.venv/bin/python -m pytest tests/test_hf20_s4_readonly.py -q
git diff --check
git status --short --branch
git rev-list --left-right --count 'HEAD...@{upstream}'
```

Final22 focused tests pass; an additional24existing independent endpoint/calendar/boundary fixtures pass (tests/test_hf20_s4_readonly.py,4.55s) in postfit validation. The prefit readiness had already authenticated saved endpoint geometry; these additional tests were run after fitting, not claimed prefit. RuffPASS. Affected installed-stub Pylance/basic5files zero errors/warnings. Final full installed Pylance/basic539files zero errors/warnings in139.925s. Exact static command above; do not alter severity/exclusions/ignores. Human editor refresh pending: select repository .venv, retain basic severity, restart language server/refresh Problems, confirm zero errors. No human confirmation claimed.

Prefit numerical fixture initially caught arch high-level forecast recomputing its backcast at the fitted mean. Corrected audit uses the public volatility.forecast API with the estimator's original prefix starting-residual backcast/bounds, preserving declared fitted terminal state. Failure receipt retained; no research fit preceded correction. Initial type check7diagnostics fixed by explicit NumPy conversion, module-name disambiguation and supported forecast-array access; no suppressions/severity changes. Formatting resolved initial Ruff style diagnostics. A supplementary postfit variance-bound audit glob included Parquet files as unit directories and raised NotADirectoryError; filtering directories fixed this read-only audit, with all560bounds subsequently checked and no artifact/model change. supplemental_audit_recovery.json preserves this trace. Arrow sysctl cache notices and pip cache warning were nonfatal. Process snapshot was read-only and found no unauthorized fitting; static node sampled about1.61GB RSS below2GB.

Independent verification:400predecessor bindings,390archived annual/equal-year/category metric rows,all36 common model/fold coefficient/rank checks and all24classical G replays. GARCH:560unit records,557prefix filters and every later update;98,728calibration/OOS prediction traces and maturity frontiers verified. No model refits during verification.

## 11. Experiment/results

Experiment hf20_s9_mag_garch_matched_calibration_2026-10-29; exploratory/post-search2021–2024. No new neural seed. GARCH exactly560default deterministic optimization calls;3boundary failures. Common-G HAR−S2C MSE+2.22117e-6 interval[1.09702e-6,3.74245e-6]; IO+2.57829e-6 [1.47156e-6,4.07563e-6]. ROLL60−S5C IC−.01335596 [−.01868969,−.00864341]. Descriptive month bootstrap400/22042, not selection-adjusted.

GARCH pass237.878s, calibration7.212s. Readiness-to-handoff elapsed1221.3s includes coding/checks/waits; not all active compute. GARCH measured peak473,726,976bytes; independent replay500,989,952bytes; calibration368,934,912bytes. Final artifact/project sizes in final_integrity.json. No trading performance or fresh-year conclusion.

## 12. Reproduction

Use documented project setup, Python>=3.12 for optional classical extra, and supplied frozen artifacts bound by predecessor_bindings.json. No API secrets needed for report-only replay. Run hf20_matched report, then hf20_matched verify and hf20_matched_verify as above. Those use saved forecasts/coefficients and permitted metadata, no fitting/inference/raw-minute extraction. Reports CSVs reproduce; frozen final scientific prose is not auto-overwritten. Never rerun consumed garch/calibrate commands or evade guards. New fitting needs separate authorization.

## 13. Git/collaboration

Branch/HEAD unchanged, cached upstream0ahead/0behind; no fetch so not live remote confirmation. No commit/push. Initial unrelated work preserved. This task leaves5new modules,1test,optional-extra/README edits,successor pointer,new reports and this handoff uncommitted. Do not pull/merge over the dirty tree. Review and stage only named task files and appropriate small reports; keep binary scores and detailed GARCH state traces local under the new namespace .gitignore. Exact git status snapshots identify other untracked work.

Suggested after human review (not executed): git add README.md pyproject.toml src/lstm_data/hf20_matched*.py tests/test_hf20_matched.py configs/track_a_hf20_classical_matched_successor_v1.json and individually reviewed small report files plus this session report; git diff --cached; git commit -m 'Complete bounded GARCH diagnostics and matched magnitude calibration'; fetch/reconcile safely only after task restriction is lifted, then ordinary push of the named branch. Do not stage all experiment binaries or unrelated registry changes.

## 14. Risks/limitations

Three strict-stationarity failures prevent a GARCH performance conclusion. Near-unit persistence in65units is disclosed. Remaining evidence repeatedly uses2021–24 and unequal predictor information sets. Native C3 differs from common multipliers; no equal-input architecture conclusion or proof recurrence is necessary. HAR missingness is stock-dependent. Historical timing/adjustments/survivor biases remain. No residual reproducible test/static failure; human VSCode check pending. Full-project node peak was sampled rather than continuously instrumented; numerical Python peaks recorded by ru_maxrss. No known resource breach.

## 15. Human review

Review full fixed-grid results and GARCH boundaries. Any changed stationarity rule/distribution/order/fallback or fresh fitting is outside this task. Human VSCode Problems refresh still required. No automatic deployment or protected release.

## 16. Next steps

Researcher review only. Preserve blocked results and all historical primaries. STOP; no automatic continuation.

## 17. Artifact inventory

FINAL_REPORT.md,GARCH_SCIENTIFIC_REPORT.md,SESSION_HANDOFF.md; metrics.csv,annual_metrics.csv,paired_differences.csv,calibration_coefficients.csv,calibration_support.csv,role_counts.csv,model_inventory.csv; data_source_receipt.json,readiness.json,verification.json,garch_verification.json,final_integrity.json; garch_fit_diagnostics.csv,garch_overlap_audit.csv,garch_filter_trace.csv,garch_support_prefit.csv; frozen model-state/update files and combined calibration/OOS Parquets; environment/static/test receipts; research_journal.jsonl and appended registry pointer. artifact_inventory.csv gives size/hash/ignored status. No plots/new neural checkpoints or raw market copies. Small files untracked pending review; Parquet/npz, per-unit GARCH files and full filter trace intentionally local under the new namespace .gitignore.
