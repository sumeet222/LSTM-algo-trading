# Codex Session Report

## 1. Session metadata

2026-11-10 America/New_York, HF20 all-18 offline exit audit.
Branch feat/track-a-data-intake. Start and end HEAD
8061483cb65d03264a7836b8b882123f67cbe4ad. Existing untracked project
sources, research artifacts, owner menus and reports were retained.

## 2. Executive summary

All 54 V3 books reconciled. Source-only marks covered 474,109 of 474,354
targets from 158,118 actual signed exit portions. The original pooled
state means reproduced. M04/R07 received mandatory deep dives, M01/M03/M05
the three additional dives under the prespecified rubric, and R01 a delta.
All 18 remain context. The next proposed test is M04 event-failure
confirmation. No funded replay or LSTM activity occurred.

## 3. Research and protocol impact

No previous entry, exit, universe, model, economics or source changed.
New offline definitions fix a five-minute within-session search and
supported ordinary-action and split adjustments. All outcomes are
descriptive, selected on repeatedly researched 2021–24 data. Proposed
refinements and final strategy slate are unexecuted.

## 4. Files created

- src/lstm_data/trading/track2/rapid_exit_audit contains offline future
  marks, validation, aggregation, candidate review and reporting utilities.
- tests/track2_rapid_exit_audit contains source/time/action/economic,
  future-isolation and complete output-census assertions.
- trading/track2/rapid_exit_audit_v1 contains sealed inputs, rules,
  compact results, individual reports, issues and final provenance.

## 5. Files modified

Only new audit-owned code and report drafts were refined. An event-row
identity clarification retained both internal and external portions at
the same cohort minute. Local validated JSON/table helpers removed a
cross-module type-inference dependency without touching frozen R01 code.

## 6. Files deleted, renamed, or moved

None.

## 7. Critical interfaces

offline.economic_units applies signed ordinary claims and split ratios
to future references. Unsupported distributions are censored.
reference_status distinguishes the evaluation cutoff, absent mark,
search limit and unsupported terms. make_sample shares raw lookups
for the complete exit/reference population. runner checks the original
funded money/count receipts and generates compact strata. review keeps
actual positive configurations separate from diagnostic hypotheses.
report authors human-readable views only after the numeric receipt.

## 8. Data and provenance

48 original raw months in one full source pass. 231,010 unique shared
entry/reference keys, three fixed horizons, no market data after 2024.
The next-session rule retains the opening offset on the next full XNYS
session. Source files and prior R01/V1/V2/V3/V5 evidence were verified
by SHA256 and mtime. Old source/current model identity remained intact.
Ordinary source confidence and unknown-year conditions are retained.
Only a deterministic 100-reference sample is persisted.

## 9. Dependency and environment changes

None. Existing .venv only. No network market fetch or credentials.
Arrow CPU-cache sysctl warnings did not prevent source reads.

## 10. Commands and tests run

    .venv/bin/python -m pytest -q tests/track2_rapid_exit_audit tests/track2_rapid_r01 tests/track2_rapid_v3
    .venv/bin/ruff check --select E,F,I src/lstm_data/trading/track2/rapid_exit_audit tests/track2_rapid_exit_audit
    .venv/bin/pyright --pythonpath .venv/bin/python --outputjson src/lstm_data/trading/track2/rapid_exit_audit tests/track2_rapid_exit_audit
    .venv/bin/python scripts/check_python_types.py --pylance-dist ~/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist

20 tests passed in 2.58 seconds. Ruff and targeted types clean. Installed
Pylance full check retained 30 inherited errors (27 frozen replication,
three Plotly test issues), zero new audit errors. Select .venv/bin/python,
use basic mode and refresh editor Problems for parity.

## 11. Results summary

Five original positive configurations were verified: V2 M04/T480,
R07/D3 and D5, V3 R01/H85 and R07/H85. New future-price marks are neither
funded portfolio results nor an oracle trading strategy. A risk label can
be a whole-account spillover. M04 and M05 have an exit-persistence
hypothesis. R07 next-session evidence is favorable while +60/+240
nonforced marks are adverse and sample support is low.

## 12. Reproduction

Use the exact local inputs in INPUT_SEAL.json and a new output directory.

    .venv/bin/python -u -m lstm_data.trading.track2.rapid_exit_audit.runner /tmp/hf20-exit-audit-NEW
    .venv/bin/python -m lstm_data.trading.track2.rapid_exit_audit.report /tmp/hf20-exit-audit-NEW

Read ANALYSIS_REPRODUCE.md for required receipts and cold-state safety.
Keep the completed results_01 directory immutable.

## 13. Git and collaboration

No commits, pushes or branch integrations. Git fetch failed because
.git/FETCH_HEAD was read-only in this session. Locally recorded
ahead/behind was 0/0, with no assertion of refreshed remote state.
Existing unrelated untracked work remains untouched.

## 14. Known issues and limitations

23 micro cases lack exact original entry-basis information for inferred
individual raw tails (USD 0.315–35.73 residual). Original grouped/account
totals reconcile. Fully net per-cohort distributions and per-order
headroom were compacted. 175 unsupported distribution crossings and
70 evaluation-boundary targets are censored. Cost/carry continuations
are standalone assumptions with no capital, netting or liquidity path.
No sector mapping, actual NBBO or point-in-time locates were invented.

## 15. Decisions requiring review

All proposed refinement tests remain unexecuted. Freeze untouched dates
and an unchanged control before authorizing any funded new rule.
S2-C sizing remains on HOLD until the directional baseline is committed.

## 16. Next recommended step

One fixed M04 comparison, unchanged H85 versus two consecutive valid
event-failure confirmations, retaining every hard risk and other exit.
Measure net per turnover and gross-exposure-year, additional downside,
actual hold, fees and source-qualified causal decision records.

## 17. Artifact inventory

ALL18_EXIT_ANALYSIS_MANIFEST.json binds source and new artifacts.
The full numeric pass took 294.48 seconds, peak RSS 1,675,313,152 bytes.
It wrote about 14.13 MB before its receipt. Final exact size is in the
manifest. There are no market-panel copies or funded account journals.
