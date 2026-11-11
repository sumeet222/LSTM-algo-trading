# Rapid V2 run status and recovery

Run rapid-v2-20261110-r1 finished **COMPLETE**. Case census {'COMPLETE': 108}.
The 54 headroom rows and 72 horizon rows share 18 H100 baseline rows, yielding
108 unique case results. The analysis and annual bridge audits both passed.
No case selection depended on an observed year, trade or result.

- Registry identity 88731c7e0c5438378ea7cd5d56d0a5334f918a5d9cc997ce457d52a5e857d995
- V1 results SHA256 7fe16983dbb7a77606020ce80dbd27fbc5253b53b3eb86d90ea1fe024281740f
- Result manifest SHA256 94605ec2d493711404026c8fb2e4406482846d6c5eff351ce3a0905fb8abdc00
- Last committed session 2024-12-31, after 1005 sessions.
- One 48-month financial source read pass. Reused the V1 feature cache.
- Replay wall time 531.82 s. Screen including final table and
  preservation checks 544.66 s wall and
  545.96 s CPU. Peak RSS 1,225,359,360 bytes.
- New run artifacts 39,566,905 bytes including annual states and analysis.
  All new Rapid V2 artifacts 39,984,196 bytes before this note and final manifest.
- H100 max daily USD component difference vs V1 0.
  Internal ledger max USD residual 9.6598E-21.
  Float output max USD NAV residual 2.18e-11.
- Marked annual bridge 432 rows. Max terminal lot comparison
  residual 9.426E-21 USD.
- 35,496 parent objects rechecked, zero material changes.
  V1 boundary independently rechecked at completion.

## Commands

Run at the repository root with the existing .venv. The initial registry
was sealed before the pilot. The engineering amendment is preserved.

    .venv/bin/python -m lstm_data.trading.track2.rapid_v2_diagnostics.cli freeze
    .venv/bin/python -m lstm_data.trading.track2.rapid_v2_diagnostics.cli validate
    .venv/bin/python -m lstm_data.trading.track2.rapid_v2_diagnostics.cli pilot
    .venv/bin/python -u -m lstm_data.trading.track2.rapid_v2_diagnostics.cli screen --run-id rapid-v2-20261110-r1
    .venv/bin/python trading/track2/rapid_v2_diagnostics/analyze.py trading/track2/rapid_v2_diagnostics/runs/rapid-v2-20261110-r1 trading/track2/rapid_v2_diagnostics/runs/rapid-v2-20261110-r1/analysis
    .venv/bin/python trading/track2/rapid_v2_diagnostics/audit_years.py trading/track2/rapid_v2_diagnostics/runs/rapid-v2-20261110-r1 trading/track2/rapid_v2_diagnostics/runs/rapid-v2-20261110-r1/year_audit

A stopped run without RUN_COMPLETION.json may resume with the same registry
and source identity. Inspect START.json for the recorded PID, examine running
processes where available and check the last sealed state. The process lock
also refuses a second writer. Use the same CLI command with resume in place
of screen and the same run ID. The latest committed annual checkpoint
contains all account state and daily observations through its date. Restoring
starts at the next session and leaves the earlier result files untouched.
A completed run should be verified by its manifests and analyzed from the
existing tables. Use a different run ID for a new authorized run.

## Local artifact map

- [results_20261110T225245268428Z/HEADROOM_RESULTS.csv](runs/rapid-v2-20261110-r1/results_20261110T225245268428Z/HEADROOM_RESULTS.csv)
- [results_20261110T225245268428Z/HORIZON_RESULTS.csv](runs/rapid-v2-20261110-r1/results_20261110T225245268428Z/HORIZON_RESULTS.csv)
- [results_20261110T225245268428Z/FRICTION_DECOMPOSITION.csv](runs/rapid-v2-20261110-r1/results_20261110T225245268428Z/FRICTION_DECOMPOSITION.csv)
- [Screening diagnostics](runs/rapid-v2-20261110-r1/analysis/RAPID_V2_SCREENING_DIAGNOSTICS.md)
- [Annual marked cash bridge](runs/rapid-v2-20261110-r1/year_audit/ANNUAL_MARKED_BRIDGE.csv)
- [Execution receipt](runs/rapid-v2-20261110-r1/RUN_COMPLETION.json)

These are conditional retrospective research results. They use the fixed
survivor panel, inherited retrospective QA/actions, modeled liquidity and
receipt, conditional short availability and the OHLCV price proxy.
