# Exact commands and scope

```sh
 git fetch --all --prune
 .venv/bin/python -B -m lstm_data.controlled_batch --output reports/data_audit/ta011_controlled_interventions_2026-10-15_124546 --plan reports/data_audit/ta011_controlled_interventions_2026-10-15_124546/predeclared_experiment_matrix_corrected.json --approval reports/data_audit/ta011_controlled_interventions_2026-10-15_124546/authority_corrected.json
 .venv/bin/python -B -m lstm_data.controlled_review --output reports/data_audit/ta011_controlled_interventions_2026-10-15_124546 --plan reports/data_audit/ta011_controlled_interventions_2026-10-15_124546/predeclared_experiment_matrix_corrected.json
 .venv/bin/python -B -m lstm_data.controlled_review --output reports/data_audit/ta011_controlled_interventions_2026-10-15_124546 --verify-only
 .venv/bin/python -m pytest -q tests/test_controlled_interventions.py tests/test_controlled_review.py tests/test_real_bridge.py tests/test_real_multimodel_batch.py tests/test_wf2_replication.py tests/test_visualization_readonly.py
 .venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist
 .venv/bin/ruff check .
 git diff --check -- . ':!docs/track_a/RandomNotes.md'
 ./scripts/run_track_a_dashboard.sh --check
 ./scripts/run_track_a_dashboard.sh --smoke
```

All completed successfully. Fitting command is historical/deadline-bound/consumed: never rerun to reproduce a score. Use --verify-only, saved artifacts and the five-step dashboard guide.72 focused tests passed;200 Pylance files/0errors/0warnings. Full legacy learning suite, new baselines, economics, null/permutation fits and confirmation were not run. Localhost tests/smoke ran with approved sandbox permission; no external connection or deployment. Initial failed pre-STARTED launch, old and corrected live decisions, and unapproved draft preparation are preserved under this namespace. Final diff excludes only the preserved concurrent human Notes edit; its trailing blank line is not agent code.
