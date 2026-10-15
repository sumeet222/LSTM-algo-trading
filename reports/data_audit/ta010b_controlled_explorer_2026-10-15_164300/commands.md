# Commands and verification

Run from repository root using its .venv. No fit/inference/download command was run.

```sh
git status --short --branch
git branch --show-current
git rev-parse HEAD
git remote -v
git fetch --all --prune
git rev-list --left-right --count HEAD...@{upstream}
./scripts/run_track_a_dashboard.sh --check
./scripts/run_track_a_dashboard.sh --smoke
.venv/bin/python -m pytest tests/test_visualization_readonly.py -q
.venv/bin/python -m pytest tests/test_controlled_visualization.py tests/test_visualization_readonly.py tests/test_controlled_review.py -q
.venv/bin/ruff check .
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist
.venv/bin/python -m lstm_data.controlled_review --output reports/data_audit/ta011_controlled_interventions_2026-10-15_124546 --verify-only
git diff --check
git status --short --branch
```

Installed-extension path is intentionally machine-specific verification tooling, not an application dependency. On another machine identify its installed Pylance dist. Final output logs provide actual counts/timings. Initial fixture omission, pandas typing diagnostics, sandbox socket denial and temporary harness logging/source-edit failures were fixed/retried as documented; none are reported as passes. Localhost smoke and socket tests required outside-sandbox approval. No full legacy training suite, native browser screenshot, clean-clone rehearsal or human editor confirmation is claimed.

The independent compact oracle pass used public read-only Study.panel/training_targets/paired_table, direct pandas grouped squared errors and rank correlations, NumPy label round-trip checks and existing source_bars/input_context over all60panels/20development panels/4prefixes. Its exact numerical outputs are in numerical_chart_oracles.json/target_label_oracles.json. These are recomputations, not new scientific fits or statistical sampling. The committed focused tests include independent metric and actual UI navigation checks.
