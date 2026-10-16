# Commands and results

```bash
.venv/bin/python -m lstm_data.normalization_audit --out reports/data_audit/ta012a_ft0_normalization_2026-10-15_230238_v2
.venv/bin/python -m pytest tests/test_normalization_audit.py tests/test_target_range_history.py tests/test_controlled_visualization.py tests/test_visualization_readonly.py tests/test_controlled_review.py -q
.venv/bin/python -m pytest tests/test_normalization_audit.py::test_registered_packet_complete_distributions_and_tail_identities -q
.venv/bin/ruff check .
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist
./scripts/run_track_a_dashboard.sh --check
./scripts/run_track_a_dashboard.sh --smoke
git diff --check
git status --short --branch
```

The audit command above was executed once into a new directory; choose a different
new suffix to reproduce. CLI rejects an existing directory before reading data.
Active audit tables and annotations are sealed by display_manifest_final.json;
consumer_resolution.json and identity_schema_addendum.json document new metadata
files produced during focused verification without replacing earlier outputs.
The current CLI creates resolved consumers and qualified tail keys directly.
Source equations, scalers and scientific artifacts were never changed.
Initial synthetic constant-contract and mistaken target-vs-M2 fit-count tests
exposed the disclosed fallback gap and four early-close input days; they were
replaced with explicit discrepancy and correct source-population oracles, not
hidden or repaired in historical code. Initial integration caught pooled identity
ambiguity; corrected complete identities pass all count/uniqueness checks.

Preflight: git status --short --branch; git branch --show-current; git rev-parse HEAD;
git remote -v; git fetch --all --prune; git rev-list --left-right --count HEAD...@{upstream}.
No Git stage/commit/push/cleanup/reset/stash/merge. CPU/RSS in resource_usage.json.
Socket checks ran with approved localhost access. Bare Streamlit context and sandbox
Arrow CPU-info warnings are environment messages, not Pylance diagnostics.
