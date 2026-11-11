# Codex Session Report

## 1. Session metadata

- Date/time: 2026-11-10T21:38:01.603217-05:00.
- Task: final targeted HF20 Track2 directional diagnostics; owner-authorized
  historical exploratory runs only.
- Branch: feat/track-a-data-intake.
- Starting/ending HEAD:8061483cb65d03264a7836b8b882123f67cbe4ad.
- Starting tree: tracked clean, extensive pre-existing untracked trading,
  replication, tests, owner menus and session reports. Retained in place.
- Ending tree: additive new diagnostics/code/tests/report, no commit/push.

## 2. Executive summary

Completed13 independently funded accounts, six treatments plus seven exact
V3 controls over1005 sessions. All controls reproduce daily/cash/exposure/exit
and terminal economics. M01 is an explicit identity because two-check weakening
already exists. R01 reserve and M05 confirmation improve both primary endpoints;
R07 improves weakly but remains LOW_SUPPORT. M04/M03 fail economic criteria.
All78 relevant tests pass; Ruff and owned Pyright pass. Global Pylance remains
HOLD with32 diagnostics in unchanged legacy files, detailed below.

## 3. Research/protocol impact

Only the six prespecified mechanisms were addressed; five are distinct changes.
Entry formulas, universe, source vintages, cost modes, source receipts, cash/
short restrictions, action claims, hard caps, original trailing/max-age handling
and dynamic cohorts otherwise frozen. No S2-C activity, final baseline selection,
new period, tuning grid, deployment or Stage6 audit. Reused2021–24 is post-selection.

## 4. Files created

New reusable code/tests:

- src/lstm_data/trading/track2/rapid_final_diag/__init__.py
- src/lstm_data/trading/track2/rapid_final_diag/allocation.py
- src/lstm_data/trading/track2/rapid_final_diag/book.py
- src/lstm_data/trading/track2/rapid_final_diag/cli.py
- src/lstm_data/trading/track2/rapid_final_diag/engine.py
- src/lstm_data/trading/track2/rapid_final_diag/policy.py
- src/lstm_data/trading/track2/rapid_final_diag/provenance.py
- src/lstm_data/trading/track2/rapid_final_diag/results.py
- src/lstm_data/trading/track2/rapid_final_diag/state.py
- src/lstm_data/trading/track2/rapid_final_diag_analysis.py
- src/lstm_data/trading/track2/rapid_final_diag_handoff.py
- src/lstm_data/trading/track2/rapid_final_diag_supplement.py
- tests/track2_rapid_final_analysis/test_published.py
- tests/track2_rapid_final_diag/test_policies.py

New artifacts live under trading/track2/rapid_final_diag_v1/: sealed input/protocol,
seven-control parity, compact13-account funded products, cohort/physical/entry
stress tables, small offline sample, six mechanism decisions, final handoff,
source/integrity/static receipts. FINAL_DIAGNOSTIC_CONTENT_MANIFEST.json enumerates
all exact new files and identities; this report is included separately.

## 5. Files modified

Only new task-owned drafts were refined before/after their relevant publication.
No prior scientific source, model, registry, cache, data, report or result changed.
The sealed online code was not changed after viewing funded outcomes. Postrun
analysis/report code was lint/type-refined; numeric first-pass outputs retained.

## 6. Deleted, renamed, moved

None.

## 7. Critical interfaces

- policy.stress_scale: Decimal maximal common t for the exact prescribed one-v20
  vintage inequality; same-vintage reservations included; no old position resize.
- policy.observe_changed/confirm: filter only named event resolution, distinct
  source/monitor tokens, missing/recovered streak reset, all other triggers preserved.
- capped_trail: fixed-at-entry min(2*v20, historical gap log scale).
- DiagnosticBatch: inherits original chronological source/decision/fill/accounting;
  routes only guarded R01 allocation or specified exit adapters.
- DiagnosticLedger: captures completed cohort/physical rows before compaction;
  adds finite constraint samples and full R01 pre-rounding reserve records.
- state: code/config/cache-bound session restart; source-backed equality tested.
- results.parity: all1005 archived daily rows and financial/count summaries for7
  controls; refuses publication on mismatch. Ledger USD tolerance1e-7.
- postrun analysis/supplement: no import path into online scoring or execution.
  The supplement recovers three exact OGN disposal rows from a sealed checkpoint.

## 8. Data/schema/provenance

Existing V1 shared feature cache49a590a7… and original48-month raw/action tape.
Original adjusted inputs versus raw-share fills preserved;2-minute receipt,
nominal+10 entry lifetime,1% prior received volume, next-valid observed bar.
New tables retain original opportunity keys, fill/exit times, immutable cohort
identity, source hashes, dollar gross/action/net/cost, exposure and exit causes.
No2025+ market observation or HTTP acquisition. Later payable metadata remains
under original conditional action policy. Immediate357 input hashes/mtimes and
35496 protected objects checked before/after; zero material changes.

## 9. Environment/dependencies

Existing .venv. No package installation, credential, environment or dependency
specification change. Arrow printed sandbox CPU-cache sysctl warnings; real
source reads succeeded. Full Pylance installed2026.4.1; basic severity unchanged.

## 10. Commands and tests

Exact arguments, stdout/stderr, wall times and return codes: validation/ and
final_validation/ under the new root. Key executed commands:

    .venv/bin/python -m lstm_data.trading.track2.rapid_final_diag.cli freeze
    .venv/bin/python -m lstm_data.trading.track2.rapid_final_diag.cli validate
    .venv/bin/python -m lstm_data.trading.track2.rapid_final_diag.cli pilot
    .venv/bin/python -m lstm_data.trading.track2.rapid_final_diag.cli run --run-id final-diag-20261110-r1
    .venv/bin/python -m lstm_data.trading.track2.rapid_final_diag_analysis
    .venv/bin/python -m lstm_data.trading.track2.rapid_final_diag_supplement
    .venv/bin/python -m lstm_data.trading.track2.rapid_final_diag_handoff
    .venv/bin/python -m pytest -q tests/track2_rapid_final_diag tests/track2_rapid_final_analysis tests/track2_rapid_v3 tests/track2_rapid_v2 tests/track2_rapid_v1

78 passed in4.11s. Scoped Ruff E/F/I PASS after fixing three postreport lint findings;
initial failed receipt preserved. Scoped command .venv/bin/pyright --pythonpath
.venv/bin/python with all new code/tests:0 errors,0 warnings. Full command:

    .venv/bin/python scripts/check_python_types.py --pylance-dist <installed-vscode-pylance>/dist

Actual installation path/argv saved in final_validation/RECEIPT.json. Final full
result759 files,32 errors,0 warnings:27 frozen replication,3 Plotly tests,2 newly
exposed frozen R01 line121 decoder/kwargs diagnostics under combined inference.
Prior all18 result had30. Zero errors in new files. Global type HOLD remains;
no suppression or frozen edit. Editor: select .venv/bin/python, Pylance basic,
restart server and compare exact locations; editor Problems refresh is human-confirmed.

## 11. Results

Control→treatment netUSD: M04-2117.97→-3615.01; R01H100-7629.39→+991.13;
M01-9003.75→identical; M05-21099.81→-18741.32; M03-11881.76→-13428.23;
R07+117.01→+445.41. R01 H85 unchanged+$10488.39. All financial bridge residuals
within1e-7. Positive net is concentrated; no alpha confirmation or final selection.
R01 vintage-primary closures223→40/832 candidates; reserve mean t.9757.
M03 worst tails improve but net/exposure economics worsen. Exact values, annual
returns, orders/cohorts, normalization and reasons are in funded CSVs and handoff.
Offline449 signed portions×3 targets=1347 valid. Risk-infeasible future extensions
are distinct; no combined oracle return. Full13-account replay146.33s including
export; engine143.48s; peakRSS1,339,998,208bytes. Analysis14.36s; pilot6.48s.

## 12. Reproduction

See ANALYSIS_REPRODUCE.md, sealed registry/source refs and no-overwrite run IDs.
Existing completed run must be verified, not resumed/rerun after interruption.
Same-code interrupted runs support content-bound year-end restart only. Full
source/cache availability and provider rights are inherited local requirements.

## 13. Git/collaboration

No tracked diff, no integration/commit/push. Git fetch failed to write protected
.git/FETCH_HEAD; locally known ahead/behind0/0. Read-only process inspection found
no matching job before launch; final inspection found no remaining research/static
worker. Do not pull or clean over extensive inherited untracked research work.
Review/stage only specifically intended additive files in a separate future action.

## 14. Issues/risks

Global type qualification remains. Three missing regular-fill OGN export rows
were recovered from exact checkpoint events; funded account results were always
correct. Per-unfilled-opportunity rejection causes are not individually retained;
aggregate counters remain available. Whole-account risk tags are not isolated
lot-level causal effects. M01 is no new rule; R07 sparse. Source/actions/borrow and
print proxy are conditional/retrospective; repeatedly inspected survivor sample.

## 15. Human review decisions

User will separately approve final slate design and later selection of2–3.
No new thresholds or blends should be inferred as approved. Resolve global
legacy type behavior through a separately scoped permitted engineering change;
do not rewrite frozen research evidence. S2-C remains on HOLD until direction frozen.

## 16. Next recommended steps

Use six mechanism decisions in a focused design meeting, retain unchanged
controls/all18 context, define fresh confirmation requirements before strong claims.
No more diagnostic parameter search was launched.

## 17. Artifact inventory

Main entry FINAL_DIAGNOSTICS_HANDOFF.md; full mechanism table, funded summary,
paired opportunity CSV, reserve examples/checks, physical OGN supplement, tail/
concentration/annual tables, source-bound offline sample, hashes and validation.
All remain local/untracked consistent with inherited research tree; no raw-price
or model copies, no plots, no full event journals. Four compact year-end restart
snapshots are retained. Final exact bytes in the self-excluded content manifest.
