# HF20 GARCH/matched-calibration handoff — STOP

Matched G/IO comparison complete for9frozen models on all80,260keys;72model/fold/family calibrations. Closest classical HAR MSE exceeds S2C by2.0788% (G) and2.4212% (IO), in all4folds. ROLL60 IC.318689978 remains below S5C.332045935 in all4. Raw-estimator, MAE and intraday conclusions differ; see FINAL_REPORT.md.

GARCH dependencies now executable, but complete arm blocked:560single fits,557admissible,3COPstationarity boundaries (F22 15:30,F23 13:30,F24 15:30). No retry/fallback/partial aggregate. Historical dependency block unchanged. Review GARCH_SCIENTIFIC_REPORT.md. Ledger186/300 unchanged.

22 focused tests and 24 endpoint/calendar tests pass; Ruff passes; installed Pylance/basic checks 539 files with zero errors and warnings. All400predecessors and390archived metric rows replay; allG/IO rank/closed-form checks pass;98,728GARCH diagnostic forecast traces independently checked. Human VSCode Problems refresh remains pending. Exact static command and editor instructions are in [2026-10-29_201017_hf20_garch_matched_calibration.md](../../codex_sessions/2026-10-29_201017_hf20_garch_matched_calibration.md).

Environment: existing .venvPython3.14; scipy1.18.1,arch8.0.0,statsmodels0.14.6,patsy1.0.3 added without changing existing packages. Python-index access only, no market/source/API access. Optional project extra classical requiresPython>=3.12. Freeze/plan/install/lock receipts are retained.

Saved-score reproduction, fitting disabled:

```sh
.venv/bin/python -B -m lstm_data.hf20_matched report
.venv/bin/python -B -m lstm_data.hf20_matched verify
.venv/bin/python -B -m lstm_data.hf20_matched_verify
```

Do not rerun garch/calibrate or remove guards. report regenerates derived tables only; final prose and historical records are frozen. Frozen source forecasts must be supplied via the existing artifact transfer procedure. predecessor_bindings.json/key_checks.json and frozen_fit_outputs.json record lineage. final_integrity.json/artifact_inventory.csv give final hashes and footprint.

Git:feat/track-a-data-intake at997b30cff98785911b0e33b7e3d2e72f61b8270b, cached0/0, nofetch/commit/push. Existing dirty registry and prior work preserved; newtask work uncommitted. git_status_initial.txt/git_status_final.txt give exact snapshots. Only README/pyproject existing files changed by this task. Newcode/test plus reports and append-only successor pointer are listed in the session report. The namespace .gitignore keeps binary forecasts, per-unit GARCH files and the full filter trace local; transfer them using the documented artifact route. Do not blanket-stage binaries or unrelated work.

No neural starts/inference,raw minute reads,2025numerical/protected2026 access,trading or further research. STOP for researcher review.
