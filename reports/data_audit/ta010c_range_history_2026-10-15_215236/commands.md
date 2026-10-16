# Reproduction / run commands

```bash
./scripts/run_track_a_dashboard.sh
./scripts/run_track_a_dashboard.sh --check
./scripts/run_track_a_dashboard.sh --smoke
.venv/bin/python -m pytest tests/test_target_range_history.py tests/test_controlled_visualization.py tests/test_visualization_readonly.py tests/test_controlled_review.py -q
.venv/bin/ruff check .
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist
git diff --check
git status --short --branch
```

Use the locally installed Pylance extension path on another machine; keep the repository
interpreter/basic severity/stub parity. Socket smoke/tests need localhost permission.
No package install or fit required in this provisioned environment. Follow README setup
and data/README.md for another legitimately provisioned machine; missing source files
must remain unavailable instead of triggering downloads or substituted prices.

Preflight also ran git branch --show-current, git rev-parse HEAD, git remote -v,
git fetch --all --prune and git rev-list --left-right --count HEAD...@{upstream}.
Only fetch changed remote-tracking metadata; no working-tree/index/history Git writes.
