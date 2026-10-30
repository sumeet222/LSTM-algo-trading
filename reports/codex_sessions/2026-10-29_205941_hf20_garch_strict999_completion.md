# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-29T20:59:41.469472+00:00; researcher task dated2026-10-29.
- Contributor: Codex; bounded GARCH11-STRICT999 successor.
- Branch: feat/track-a-data-intake.
- Starting/ending commit: 997b30cff98785911b0e33b7e3d2e72f61b8270b; no commit created.
- Working tree at start: dirty prior research work; git_status_initial.txt in experiment records the snapshot after readiness creation.
- Working tree at end: prior work preserved plus only new strict999 code/test/experiment/session report/successor pointer. Final Git snapshot is bound by seal_receipt.json.
- Issue/PR: none.

## 2. Executive summary

COMPLETE:560/560 fits pass under one uniform inside-optimizer alpha+beta<=.999 constraint. All three old COP boundaries pass;13 contacts and five tiny roundoff overshoots explicitly audited. Zero retries. New G/IO calibration completes on independent prior Oct–Dec only. Full80,260-row comparison preserves all old scores and calibrators. GARCH MSE loses to S2-C by3.7736% G/4.1538% IO in all four years; IC0.307433340 remains below neural models. Raw and native-package/tail comparisons differ and are reported separately. Benchmark technically closed; STOP.

## 3. Research/protocol impact

Only authorized scientific change is the same .999 persistence cap on all560 new fits. Target,20-stock order, genuine240-minute endpoints, timing proxy, source revision,48-hour embargo, role masks, fit series, eligible keys, weights, neural models and old calibrations unchanged. New G/IO fits concern only new GARCH. No architecture, training, trading,2025/protected2026 or final-test protocol change. Source/timing/survivor/repeated-search limitations remain. Ledger186/300 unchanged.

## 4. Files created

- New code/test files: src/lstm_data/hf20_strict999.py, src/lstm_data/hf20_strict999_audit.py, src/lstm_data/hf20_strict999_fit.py, src/lstm_data/hf20_strict999_model.py, src/lstm_data/hf20_strict999_report.py, src/lstm_data/hf20_strict999_verify.py, tests/test_hf20_strict999.py. Interfaces and purposes below.
- New experiment directory: reports/experiments/hf20_s9_mag_garch_strict999_2026-10-29; every artifact path/type/size/SHA256/purpose and tracking policy is enumerated in artifact_inventory.csv. FINAL_REPORT.md is the scientific verdict; SESSION_HANDOFF.md is the operational handoff; README-style IMPLEMENTATION.md explains the frozen method.
- Readiness/API/input/hash/role receipts, fit-unit parameters and state traces, new calibration/OOS Parquets, full47-arm metrics/annual/group/rank/tail/pair tables, tests/logs, independent verification, source snapshots, append-only journal and final integrity are in that inventory.
- New append-only config: configs/track_a_hf20_garch_strict999_successor_v1.json, added only after audited scientific artifacts.
- This session report; late git_status_final.txt/seal_receipt.json bind final pointer/Git state without rewriting the scientific seal.

## 5. Files modified

No pre-existing repository/source/environment file was modified by this task. New task files were developed and corrected before sealing. All3,296 bound predecessors plus old frozen fit/source/journal assets were rehashed unchanged. Earlier dirty registry/README/pyproject changes belong to predecessor work and were preserved.

## 6. Files deleted, renamed, or moved

No pre-existing files deleted/renamed/moved. Within the new run, provisional new fold diagnostic score files were renamed to eligible score files only after all560 fits passed. No partial panel was scored.

## 7. Critical interfaces

- Strict999GARCH.constraints / make_model / constraint_audit: public arch component construction and unrounded coefficient audit; only the persistence matrix bound changes.
- hf20_strict999.main/calibrate/load_panel/preservation/resources: single-use new fitting/calibration lifecycle, exact frozen-score reads, predecessor hash checks and resource gates; no old calibration fitting.
- hf20_strict999_fit.run/admitted: 560 uniformly constrained signed-return fits, prefix initialization, causal per-event state updates and folded-normal forecasts; no retries or dropped OOS rows.
- hf20_strict999_audit.audit: saved optimizer/input/start/normal-likelihood/bound verification and all560 old/new coefficient deltas; no fit.
- hf20_strict999_verify.verify_garch: independent public package prefix recursion and every saved subsequent state/forecast replay, exact issue/endpoint/role/score checks.
- hf20_strict999_report.report(output=None)/verify: existing magnitude/rank/group reducers and paired-month implementation, optional fresh-directory report-only replay; saved G/IO arithmetic and660 old metric parity checks. Default report output is guarded against overwrite.
- tests/test_hf20_strict999.py: synthetic package parity, deterministic starts, constraint and optimizer boundary fixtures.

## 8. Data/schema/provenance changes

No market source/schema/adjustment changes. Source revision776328445b7ac6e7815ef3a483e9c8ded1eb6d56; saved genuine signed return histories and masks only. Exact indices/x vectors match each archived unit;59 exact exclusions remain history-only. Metadata columns and A/weights/stock order match all prior panels. New raw/G/IO score columns are appended only in the new namespace. data_source_receipt.json and predecessor_bindings.json provide exact paths/hashes. No minute source, market fetch,2025 observations or protected2026 material accessed.

## 9. Dependency/environment changes

None. Existing .venv Python3.14.6, arch8.0.0/scipy1.18.1/statsmodels0.14.6 verified. Pip freeze before/after byte-identical. Public package constraints extension only; no package source patch or dependency upgrade. Portable setup remains existing README/pyproject route plus exact archived private artifacts.

## 10. Commands and tests

Exact fit/audit/calibration/report/static commands and logs are in SESSION_HANDOFF.md. Guarded fit/calibration commands were run once and must not be rerun.37 focused tests pass; Ruff passes. Full installed Pylance/basic command:

```sh
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist
```

Final546files/0errors/0warnings, exit0; peak child RSS1,718,730,752 bytes. No severity/exclusion/suppression changes. Human VSCode Problems refresh confirmed zero errors by researcher. Git diff --check passes.

Initial non-scientific failures retained: incorrect public base-class import location corrected; CSV literal None sentinel preserved with exact parsing; initial synthetic fixture did not force cap contact and was corrected before data fits;30 test-only kwargs typing errors fixed with explicit arguments; initial Ruff import-order fixes. A time-wrapper sysctl query failed after a clean static check; a subsequent resource-aware full check exited0. Arrow hardware/cache and pip cache notices were nonfatal. Sandbox process inspection denial was resolved with the already approved read-only ps permission. No real fit failed or was retried.

## 11. Experiment/results

New experiment hf20_s9_mag_garch_strict999_2026-10-29.560fits,560pass,0retry;37tests;99,240 forward traces replayed including80,260 OOS rows. GARCH all3variants share IC0.307433340. S2-C same-family MSE remains lower in every annual fold; S5-C IC0.332045935 remains higher in every fold. HAR and ROLL60 remain the strongest descriptive classical MSE/IC comparators in the fixed grid. New calibrator fits8family-folds; old fits0/neural starts0.13contacts; five overshoots max1.7942e-13 within frozen1e-10 tolerance. Gaussian/irregular-event approximation retained. Inference is descriptive400draws/seed22042, not selection-adjusted confirmation. No trading metrics or claims.

## 12. Reproduction

Supply exact authorized artifact lineage through the existing private-artifact route; do not download/rebuild data under this task. Authenticate the successor pointer and manifests. Use a new nonexistent output directory:

```sh
.venv/bin/python -u -B -m lstm_data.hf20_strict999 report --output reports/experiments/hf20_strict999_report_replay_NEW
```

Executed report_replay_001 produced8byte-identical numerical CSVs; zero model/calibration fitting, neural inference or source reconstruction. Code snapshots, fixed coefficients and saved scores are available. Do not rerun guarded fit/calibrate or writing verifier commands into the sealed directory. A new scientific fit requires separate researcher authorization.

## 13. Git/collaboration

No fetch/commit/push per explicit instruction. Cached ahead/behind0/0; current remote state unverified. All old local work protected, no resets/stash/merges/branch switch. New uncommitted artifacts and source are listed in inventory/Git snapshots. Large unit state/Parquet/trace files intentionally ignored. For a later authorized integration, review and stage only this task's explicit code/test/small receipts/session/pointer files; never git add the entire dirty tree. No PR/merge is initiated.

## 14. Risks and limitations

Repeated 2021–2024 inspection; overlapping events and residual dependence; unequal features across families; fixed Gaussian assumption; irregular same-slot horizon; retrospective source/survivor cohort; nominal-origin/+2min availability proxy; early-close support only5sessions. No proof of recurrence necessity or tradability. Original blocked GARCH has no full-panel performance score. Task output exceeded150MB estimate due saved comparator panels but remains under2.5GB; numerical RSS<528MB and static child RSS<2GB; project<15GB. There are no residual failing scientific/type/unit checks and editor refresh is confirmed.

## 15. Human review

Review scientific interpretation and append-only artifact linkage. Any further cap, calibration, architecture, hybrid/router, trading or holdout work needs a new explicit decision. No request to repair or assert the ledger.

## 16. Next steps

STOP after this report/seal. No autonomous sequel. Researcher review only.

## 17. Artifact inventory

artifact_inventory.csv enumerates the complete new experiment and new code/test/session report with purpose/type/SHA/bytes/tracking policy. final_integrity.json binds the inventory and journal; the new successor config binds final integrity. seal_receipt.json additionally binds final pointer/Git snapshot. Older primaries and journals remain immutable. No plots/checkpoints/neural outputs were newly generated; numerical tables, model parameters, calibration coefficients, keyed forecasts and filter/replay logs are preserved.
