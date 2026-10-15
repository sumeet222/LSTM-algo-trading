# Package008 commands

Exact actual invocations/timing/source hashes: `analysis_final_command.json`, `focused_release_command.json`, `static_release_command.json`, `ruff_release_command.json`. One earlier serialization failure and an earlier completed report before distribution fields were added are preserved as separate attempts; none fitted anything.

```sh
mkdir reports/data_audit/NEW_DIAGNOSTIC_DIRECTORY
env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python -B -m lstm_data.four_model_diagnostics --previous reports/data_audit/ta007_multimodel_firstpass_2026-10-15_010008 --output reports/data_audit/NEW_DIAGNOSTIC_DIRECTORY
env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python -B -m pytest tests/test_four_model_diagnostics.py tests/test_neural_health.py -q
.venv/bin/ruff check .
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist
git diff --check
```

The last checkerargument is the intentionallyconfiguredactualeditorstubpath, not adataruntimepath; choose the equivalentinstalledextensiononanothermachine. Same.venvinterpreter andPylancebasicseverity. RefreshProblems/languageserver andhumanconfirmzeroerrors. No new source/credentials/download. No fit/retrycommand, Gitmutations orledgerwrite. The report packet records its originalsource/prep/checkpoint bindings. Dataset andweightsremain local inputs under existinglegitimaterightsrequirements; a cleanclonehandoffisnotcertified.
