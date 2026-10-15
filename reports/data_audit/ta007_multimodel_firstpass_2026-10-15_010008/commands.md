# Package007 commands

The exact reviewed execution command (requires the actual approval file):

```sh
.venv/bin/python -B -m lstm_data.real_multimodel_batch --plan reports/data_audit/ta007_multimodel_firstpass_2026-10-15_010008/batch_plan.json --approval reports/data_audit/ta007_multimodel_firstpass_2026-10-15_010008/batch_authorization.json --output reports/data_audit/ta007_multimodel_firstpass_2026-10-15_010008
```

Use the same command with `--dry-run` or `--status` for zero-fitting validation. Preparation was `python -B -m lstm_data.real_multimodel_batch --prepare --output reports/data_audit/ta007_multimodel_firstpass_2026-10-15_010008` under the repository interpreter. All exact commands, numerical thread settings, timings and code hashes are recorded by the command JSON files.

The optional separately approved market ridge command is:

```sh
.venv/bin/python -B -m lstm_data.real_batch_baseline --plan reports/data_audit/ta007_multimodel_firstpass_2026-10-15_010008/batch_plan.json --approval reports/data_audit/ta007_multimodel_firstpass_2026-10-15_010008/market_ridge_authorization.json --output reports/data_audit/ta007_multimodel_firstpass_2026-10-15_010008/RIDGE_MARKET_147
```

Neither pending approval templates nor the consumed TM0 decision authorize execution.

Completed runs are consumed and refuse execution replay. The post-batch read-only review command is:

```sh
.venv/bin/python -B -m lstm_data.real_batch_review --package reports/data_audit/ta007_multimodel_firstpass_2026-10-15_010008
```

Actual runs used `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1` and the repository interpreter. `batch_execution_command.json` records the actual outer command and wall time; each worker has separate phase timings. The whole-project Python hash changed during execution solely because the read-only report module was added; the nine approved execution modules retained their exact `1d3f6bab5263dcf0d579b825c804809c6abf7815051592fc452470b067d0132e` binding. This report module contains no optimizer or journal writer.

Focused tests and exact Ruff/type commands are in `focused_command.json`, `ruff_final_command.json`, `static_release_command.json`; static checking covers all project-owned Python using the actual local Pylance extension and repository `.venv`. The installed editor-extension path is an intentionally machine-specific checker argument, not a runtime data path.
