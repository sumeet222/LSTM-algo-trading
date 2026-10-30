# S5-C handoff — completed, STOP for review

Four of four selector/refit pairs and four own C3 calibrations completed. Technical verification passed; scientific verdict is **mixed magnitude-versus-ranking tradeoff**, not a clean hybrid improvement. Read S5C_HYBRID_FINAL_REPORT.md for the independent co-primary conclusions. Ledger182→186/300, four starts/eight phases, no retry. Selected epochs3/13/20/4. No further fitting or baseline work is authorized.

## Reproduction and commands

```sh
# Completed historical invocations; do not relaunch --prepare or --run.
.venv/bin/python -u -B -m lstm_data.hf20_mag_hybrid --prepare
.venv/bin/python -u -B -m lstm_data.hf20_mag_hybrid --run
.venv/bin/python -B -m lstm_data.hf20_mag_hybrid --report
.venv/bin/python -m pytest tests/test_hf20_mag_hybrid.py tests/test_hf20_mag_rank.py tests/test_hf20_stage2_bcd.py -q
.venv/bin/ruff check src/lstm_data/hf20_mag_hybrid.py src/lstm_data/hf20_mag_hybrid_report.py tests/test_hf20_mag_hybrid.py --output-format concise
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist
git diff --check
git status --short --branch
```

The managed run session94715 exited0; it was never relaunched. Preparation15355 and report75525 exited0. Logs are preparation.log, execution.log and report_execution.log. --report performs saved-score analysis only and regenerates numerical CSVs/report_receipt.json, not the manually finalized scientific report. Do not overwrite frozen protocol/readiness/phase files. A fresh training reproduction requires separate approval and a genuinely new run; never evade single-use guards. Another machine needs the authoritative project environment and the pinned authorized historical hourly/source/role/score artifacts referenced by protocol.json; private checkpoints/Parquets are intentionally ignored and must be supplied through the project's documented external artifact route.

Two new reusable modules: src/lstm_data/hf20_mag_hybrid.py (fixed objective, phase constants, gates and lifecycle) and hf20_mag_hybrid_report.py (saved-score magnitude/ranking comparisons). New test: tests/test_hf20_mag_hybrid.py. No predecessor numerical code or test changed. Only existing-file write is the authorized registry successor schema34→35 with fit_permission=false and previous-journal hash. Existing dirty work remains intact; no commit/push/fetch/network/environment changes.

## Verification

Prefit and post-fit focused tests:17 passed (4.01s /3.31s). RuffPASS. Affected installedPylancebasic3files0errors/0warnings. Full check528files0errors/0warnings (85.161s during execution;84.197s post-fit). No exclusions, severity reductions or ignores. The local extension path above identifies the actual checker/stubs; another machine should pass its installed Pylance distribution. Human VSCode verification remains outstanding: select repository.venv, keep basic severity, refresh Pylance/Problems, confirm zero errors. No editor refresh was claimed.

verification.json independently replays all eight phase scales/mu/v/tau from permitted saved labels and role weights, selector qualification/refit counts, component-loss arithmetic, four own C3 coefficients, exact old/new keys/labels, raw/calibrated decoding and checkpoint hashes. Run-time replay on both calibration and OOS was bit-identical. The ephemeral verifier /private/tmp/verify_s5c.py used no fitting or new inference; preserved JSON/log evidence records its checks. Source and model code hashes froze before any neural start. Post-report consistency and final footprint are in final_integrity.json; artifact_inventory.csv lists outputs and their tracking policy.

Initial prefit typing corrections concerned direct module type imports, explicit three-tensor tuple return, separate report dictionary/DataFrame names, and typed named-parameter gradient access. Formatter resolved initial style diagnostics. No objective/normalizer/source/gate was changed and no start was spent on these fixes. Earlier diagnostics were retained. Arrow hardware-cache sysctl sandbox warnings were nonfatal environment notices. Process inspection used permission escalation after the sandbox denied ps; no Python fit was active at entry.

## Scope and interpretation

Exact original20-stock48×16FT16 plus10CLOCK, H32,6443parameters, seed42, original80260/4013/793 OOS population. Loss MSE/v +.25*pair/log2, tau=sqrt(v), each initial/refit legal prefix independently; no per-origin centering. All-tied pair contribution zero while magnitude retained, as newly authorized; none occurred. Initial/refit cutoffs and48-step embargo unchanged. Own Oct–Dec C3κ25 only after neural freeze, no OOS refit. All past rankers and baselines were read unchanged, never retrained. Dimensionless S5A/B/LINEAR appear only in ranking tables; no gap-task MSE comparison.

New calibrated MSE0.00010684904630 versusCLOCK0.00010666594589 (+.171658%) andS2C0.00010654816784 (+.282387%). IC0.332045935 versus.330254043/.331235977; descriptive gain overCLOCK, uncertain overS2C. Top-four retrieval lower than both. RAW improves MSE againstCLOCK-RAW but is not substituted after seeing results. No ordering changes from clamps. Static-score variance fractions are not predictive-accuracy attribution.

Only174receipt-bound adjusted-hourly partitions plus saved genuine target/role metadata through2024; no minute source,2025market/protected2026 paths/values/hashes, network or reconstruction. Calendar-only future schedule metadata is distinct. Historical origin+2minute publication proxy, retrospective action/source vintage, survivor cohort and repeatedly inspected years remain limitations. Preservation covers exact permitted bound assets, not a forbidden broad protected-source rescan.

## STOP

Researcher review and human editor/Git checks only. No S5-D/E, lambda/tau/seed search, new calibrator, routing, classical volatility benchmark, trading/options or protected release. The next proposed classical-benchmark activity remains separately gated.
