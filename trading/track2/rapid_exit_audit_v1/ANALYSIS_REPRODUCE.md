# Reproduce the offline audit

Use the repository .venv and the exact local files bound by INPUT_SEAL.json.
No credentials, package installation, new price download or neural inference
is needed. Launch from the repository root. Read the original source and
scope files before interpreting a result.

## Validation

    .venv/bin/python -m pytest -q tests/track2_rapid_exit_audit tests/track2_rapid_r01 tests/track2_rapid_v3
    .venv/bin/ruff check --select E,F,I src/lstm_data/trading/track2/rapid_exit_audit tests/track2_rapid_exit_audit
    .venv/bin/pyright --pythonpath .venv/bin/python --outputjson src/lstm_data/trading/track2/rapid_exit_audit tests/track2_rapid_exit_audit
    .venv/bin/python scripts/check_python_types.py --pylance-dist ~/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist

The installed Pylance stubs are the authoritative full-check setup for this
machine. Select .venv/bin/python and basic mode in the editor to refresh its
Problems list. Inherited frozen errors are separately qualified.

## Main command

The existing results_01 is sealed and must be verified rather than overwritten.

    .venv/bin/python -u -m lstm_data.trading.track2.rapid_exit_audit.runner /tmp/hf20-exit-audit-NEW_UNIQUE_DIRECTORY

The input seal, original funded file manifest, source pilot, test receipt,
and pre-extraction all-account check are required. The runner reads the
48 authorized raw months once and validates their hashes. It shares
231,010 actual entry/extension lookup keys across 474,354 targets and
all 54 accounts. There is no account simulation or order submission.

Outputs are compact aggregate CSVs plus one deterministic 100-reference
sample. START.json identifies process and executed code. RUN_RECEIPT.json
binds every completed result file. An absent receipt means unsealed partial
work. Inspect the matching PID/session and output mtimes before resuming
a disconnected run. No run may overwrite a prior directory.

The source pilot used eight hash-selected exits from the first January
2021 formation week, producing 24 valid targets in one monthly source
read. Source-only test and code hashes are saved in SOURCE_PILOT_RELEASE.json.
The counted preflight also reconciled the full terminal checkpoint against
daily NAV, original cash and claims, preserved inventory and all exit-count
definitions. Its receipt is PRE_EXTRACTION_ACCOUNT_CHECK.json. The current
read-only checkpoint validator uses encoded Decimal fields and preserves
the original preflight proof without importing a trading engine.

## Reports

    .venv/bin/python -m lstm_data.trading.track2.rapid_exit_audit.report /tmp/hf20-exit-audit-NEW_UNIQUE_DIRECTORY

This helper authors new Markdown and refuses existing report paths.
The final candidate-specific findings appendices and handoff are authored
analysis in the new subtree. They refer to the same sealed numeric outputs.

## Resource and identity

The measured full extraction and review took 294.48 seconds and peaked at
1,675,313,152 bytes RSS. It wrote approximately 14.13 MB before its receipt.
These measurements exclude preparation and human-readable report authoring.
The final content manifest gives exact total bytes, largest table, code,
test, source identities and completion status. The study uses 158,118
actual signed exit legs, including internal and external portions.

The executed source-only run preceded a local boundary-helper refactor for
static-check portability. START.json retains its exact initial module
hashes. Equivalent local JSON/table checks replaced imports of the old
R01 utility, and the full repository error baseline returned to 30.
No offline price rule, selected horizon, payoff, candidate threshold or
frozen source changed. The final source helpers and all evidence are bound
by ALL18_EXIT_ANALYSIS_MANIFEST.json.
