# Rehearsal and readiness evidence

**PASS for authorized preparation; no real-data fit permission.**

- 33 focused tests passed,9.58s, including seven inherited protected-route cases. Synthetic rank recovery uses disposable synthetic optimization, as explicitly allowed by Stage1. Real-data optimizer updates and neural starts are zero.
- All-project Ruff passed. Installed Pylance basic parity analyzed444 project-owned Python files with0 errors/0 warnings,56.334s. No severity reductions, ignored diagnostics or exclusions added.
- Independent 3-stock pair loss/finite-difference gradient,190-pair normalization/tie exclusion, endpoint conservation, equal-day weighting, ridge objective and linear-pair gradient oracles passed. Synthetic linear and NR/PW signal recovery passed.
- Fresh-seed initialization, optimizer isolation, synthetic checkpoint serialization/reload, stock permutation/zero-state behavior, future-fitted recipe rejection, invalid coverage, absent approval before I/O, permanent failed-start and64-baseline cap tests passed.
- Four synthetic exports (T2R/NR/PW/N0) passed with AdamW.step blocked:0 calls in these zero-step report rehearsals. Stored key/weight/IC/objective/cohort verification passed; deliberately corrupted weights were rejected.
- Four-fold synthetic S1 score→diagnostics→independent reconciliation→CSV/Markdown/offline Plotly closeout passed. A disposable synthetic journal exercised the real writer and blocked the next neural start when prior PASS was absent. No real journal/pointer was mutated by tests.
- Real source metadata/return/sampler checks are separately linked in the preflight. No newly fitted annual scaler or real neural checkpoint is represented as rehearsed/available.
- Actual CLI --help passed. Actual --run without --approval exited1 with LIVE_APPROVAL_REQUIRED_BEFORE_FIT_IO before data loading or any journal/output reservation. The traceback is retained as an expected rejection receipt, not an unexplained failure.

Receipts: [tests](tests.txt), [static](static_check.json), [Ruff](ruff.txt), [CLI](cli_help.txt), [approval denial](missing_approval_rejection.txt). Earlier disposable test iterations exposed writable-rank-array, formatting, report-smoke assertion and pandas type issues; all corrected before these final receipts. No real fit failed or was charged.

Exact commands:

```bash
.venv/bin/python -m pytest tests/test_hf20_ranking.py tests/test_hf1m_ft16.py::test_protected_read_and_unknown_split_fail_before_file_access tests/test_state_screen.py::test_protected_routes_fail_before_io -q
.venv/bin/ruff check .
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist
```

Editor verification remains human-confirmed: select repository .venv/bin/python, restart Pylance, refresh Problems and confirm zero project-owned errors. The local extension path is verification tooling only, not committed runtime code.

Sequential gates: S1 all64 fits/24 OOS model-fold populations plus admitted inner/refit exports must reconcile before S2. Every neural arm must pass finite training/checkpoint/optimizer-step/fresh-refit checks and independent four-role key, weight, IC, objective and tail conservation before its immutable PASS and COMPLETED journal event. The next STARTED verifies the previous PASS hashes. Resource, provenance or numerical failure stops subsequent starts permanently; finite negative IC is allowed. No retry or extra fit is permitted.
