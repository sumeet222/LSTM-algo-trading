# Rapid V3 validation and reproduction

Run rapid-v3-20261110-r1 finished COMPLETE. Census {'COMPLETE': 54}.
The funded manifest is adacdc47524ac4fdd0fbf8fa450e116a4ca7c004aa2d56be0a48d6fe16e2a9b5.
The executed registry is 2a77d69b5fe1bc5fa864679820931e03f78a622941d2353928aca70ab7b19196.
The report-only amendment is 4fdb94a1f6d65ea553b5e124d501216a77c572eb7bfa6476157b6c5c0034d7e0.
The funded period contains 1005 sessions through 2024-12-31.
The raw reader opened 48 months during the funded pass
and 48 during the isolated offline pass. The feature
cache was reused and calendar geometry alone extended beyond 2024.

- Funded wall time 359.85 s, measured from START
  to the final committed checkpoint. The exporter then failed converting a
  Decimal exit-share denominator. The trading process did not persist its
  peak RSS or row counts. Source hashes and the final day frontier identify
  the 48 funded months.
- Recovery took 34.24 s and peaked at
  1,468,907,520 bytes. It read the terminal checkpoint
  and preserved the partial export. No trades or market observations were
  replayed for report recovery.
- Offline wall time 10.23 s and peak RSS
  592,887,808 bytes.
- Total run artifacts 56,802,831 bytes. New V3 artifacts 57,658,643 bytes
  before final note and manifest. Annual snapshots retain exact cohort state.
- Ledger max residual USD 1.03E-20.
  Independent daily NAV residual USD 2.91e-11.
  Independent cash-bridge residual USD 1.8E-22.
- 78 passed in 6.65s. Ruff E/F/I and V3 owned basic types passed.
- Full Pylance basic 735 files and
  30 existing diagnostics. Zero V3 diagnostics.
- January fixed fixture exact V1 daily balance parity and dynamic restart
  hash parity. Actual-source AVGO, 2021 OGN, 2022 split, 2024 dividend and
  Thanksgiving windows. One-dollar fee and short ACT/365 fixtures.
- Future-source mutation preserved the prior committed state and prior exit
  rows. The variable-cohort fixture reconciled 60, 390 and 1,950 scheduled
  minute holds with a mixed external order and partial fill.
- Verified 35,496 protected older objects and all
  323 separately bound V1/V2 objects by SHA256 and mtime. Five earlier
  Finder metadata differences remain documented in the parent receipt.
- Offline census {'CORPORATE_ACTION_CROSSING': 2877, 'EVALUATION_CUTOFF': 70, 'VALID': 471407}, all three targets for every leg.
  No execution or NAV path was read back from the offline table.

## Commands

From the repository root with the existing .venv and bound local source files:

    .venv/bin/python -m lstm_data.trading.track2.rapid_v3_dynamic.cli freeze
    .venv/bin/python -m lstm_data.trading.track2.rapid_v3_dynamic.cli validate
    .venv/bin/python -m lstm_data.trading.track2.rapid_v3_dynamic.cli pilot
    .venv/bin/python -u -m lstm_data.trading.track2.rapid_v3_dynamic.cli screen --run-id NEW_UNIQUE_ID
    .venv/bin/python -m lstm_data.trading.track2.rapid_v3_dynamic.offline trading/track2/rapid_v3_dynamic/runs/NEW_UNIQUE_ID
    .venv/bin/python -m lstm_data.trading.track2.rapid_v3_dynamic.cli assess --run-id NEW_UNIQUE_ID
    .venv/bin/python trading/track2/rapid_v3_dynamic/verify_outputs.py trading/track2/rapid_v3_dynamic/runs/NEW_UNIQUE_ID

When using this checkout's existing registry, reuse its current seal and omit
freeze and obtain a pilot under the current registry before launching a
new unique run. The pre-full engineering amendment is documented. For an interrupted
run, inspect START.json, the PID/lock and committed checkpoint hashes. Resume
with cli resume and the original run ID under exactly the same registry and
source hashes. Completed runs should be checked by manifest. No completed
state, prior result or source data should be overwritten.

The actual report-only recovery used this command, with exclusive lock,
verified pre-amendment code identity and a terminal state. Do not invoke it
over the sealed output.

    .venv/bin/python trading/track2/rapid_v3_dynamic/recover_export.py trading/track2/rapid_v3_dynamic/runs/rapid-v3-20261110-r1 trading/track2/rapid_v3_dynamic/amendments/20261110T232738967440Z.json

The V2 compatibility columns `early_exits` and `scheduled_final_exits` retain
their inherited bookkeeping conventions. Use `risk_before_240`,
`policy_before_240`, and V3_EXIT_REASONS for dynamic comparisons.
`closed_cohorts` counts completed virtual legs of pair holdings separately.
R05's sealed exit tape reconciled 215 two-leg batches with opposing sides,
a shared causal fill time and one cause per batch.

## Artifacts

- [Funded 54 cases](runs/rapid-v3-20261110-r1/funded_20261110T233807328833Z/V3_ALL54_SUMMARY.csv)
- [Exit reasons](runs/rapid-v3-20261110-r1/funded_20261110T233807328833Z/V3_EXIT_REASONS.csv)
- [Risk regime comparison](runs/rapid-v3-20261110-r1/funded_20261110T233807328833Z/V3_RISK_REGIME_COMPARISON.csv)
- [Annual and mechanism rows](runs/rapid-v3-20261110-r1/funded_20261110T233807328833Z/V3_ANNUAL_CAUSAL_DIAGNOSTICS.csv)
- [Offline price extensions](runs/rapid-v3-20261110-r1/offline_diagnostic/V3_POST_EXIT_EXTENSION.csv)
- [Full 18-ID assessment](runs/rapid-v3-20261110-r1/V3_SCREENING_ASSESSMENT.md)
- [Funded status receipt](runs/rapid-v3-20261110-r1/V3_RUN_STATUS.json)
- [Post-export independent check](runs/rapid-v3-20261110-r1/INDEPENDENT_OUTPUT_CHECK.json)
- [R05 pair-close check](runs/rapid-v3-20261110-r1/R05_ACTUAL_EXIT_ATOMICITY.json)
