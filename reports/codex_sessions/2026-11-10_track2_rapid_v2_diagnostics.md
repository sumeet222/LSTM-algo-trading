# Codex Session Report

## 1. Session metadata

2026-11-10, America/New_York. Implement and execute Rapid V2.
Branch feat/track-a-data-intake. Starting and ending HEAD
8061483cb65d03264a7836b8b882123f67cbe4ad. Existing untracked HF20 work,
owner menus and prior reports were present. Tracked files were clean.

## 2. Executive summary

Run rapid-v2-20261110-r1 finished COMPLETE, with {'COMPLETE': 108}. H100 passed the
full V1 reconciliation. All 90 new funded cases completed or are explicitly
listed with status and evidence in the tables. Arrival drift was measured
separately from the incremental V1 cost proxies.

## 3. Research and protocol impact

The 18 frozen signals are shared across the V1 baseline and five variants.
Precommitted changes are H85/H70 before share rounding, plus three independent
holding horizons at H100 per mode. No headroom-horizon cross-product. All
budgets, roles, trading window and cash continuity follow V1. No model inputs,
learned parameters, data universe, future-conditioned selection or final-test
definition changed.

## 4. Files created

- src/lstm_data/trading/track2/rapid_v2_diagnostics: indexed case horizons,
  allocation hook, shared batch replay, exact ledger aggregation, state,
  result tables and sealed CLI.
- tests/track2_rapid_v2/test_diagnostics.py: cap, causal clock, partial fill,
  arithmetic and allocation parity tests.
- trading/track2/rapid_v2_diagnostics: initial and amendment registries,
  source integrity, pilots, validation, assumption and cost contracts,
  report scripts and compact local results. Full inventory and hashes in
  RAPID_V2_CONTENT_MANIFEST.json.

## 5. Files modified

No pre-existing project file modified. The additive V2 engineering amendment
corrected report/audit type boundaries and Decimal fee rounding expectations
and the fixture for reserved gross. Research parameters stayed fixed.

## 6. Files deleted, renamed, or moved

None.

## 7. Critical interfaces

Endpoints.anchor and retime select a nominal calendar endpoint without looking
at outcomes. AllocationEngine.allocate reuses the source-linked V1 policy
with one eligible-budget multiplication. RiskScreen is a vector prefilter.
The inherited exact V1 decision still authorizes or rejects each order.
Ledger.record audits physical arrival, price concession and role allocation.
Batch.run shares one feature evaluation per strategy per frame and one price
tape across 108 independent books. State snapshots bind the committed frontier
and deterministic replay. Result summaries retain actual and nominal duration.

## 8. Data and provenance

The V1 immutable feature cache and actual V1 raw-share source/action conventions
were reused. RawShare economic prices were read only for 2021–24. Market month
partitions 48. Calendar-only geometry
extends past the cutoff. Signed claims, splits and MRK/OGN follow V1. Source
hashes, code, registered variants and V1 outputs are bound in the registry.
Protected object SHA256 and nanosecond mtime checks passed.

## 9. Dependencies

Existing .venv only. No installs or vendor downloads. Arrow's optional sandbox
CPU-cache sysctl probe emitted warnings and the Parquet reads completed.

## 10. Commands and tests

See RUN_STATUS_AND_RECOVERY.md for the exact study commands and unique run ID.
The validation receipt contains exact pytest, Ruff and targeted Pyright argv
and output digests. 48 targeted tests and 27 additional inherited economics
tests passed. Ruff E/F/I and owned basic types passed. The full Pylance check ran

    .venv/bin/python scripts/check_python_types.py --pylance-dist ~/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist

It analyzed 723 files with 30 inherited errors
(27 frozen replication and three Plotly viewer tests), zero new V2 diagnostics.
To verify editor parity, select .venv/bin/python in VS Code, enable Pylance
basic diagnostics, reload and refresh Problems. Editor refresh is user-verifiable.
The AVGO real-source, January restart, extra action/early-close and seeded
signed OGN probes passed.

## 11. Experiment results

All-ID funded and friction tables are under trading/track2/rapid_v2_diagnostics/runs/rapid-v2-20261110-r1/results_20261110T225245268428Z.
H85 improved net results for 13 of 18, H70 for
14 of 18. Positive net cases ['M04/T480', 'R07/D3', 'R07/D5'].
The results are exploratory on an already used sample. Gross signed-price
P&L excludes separately modeled concessions and fees. Full mode and
mechanism diagnostics are in the report, including exposure-normalized
contrasts and the marked annual net bridge.

## 12. Reproduction

Run the documented CLI from repository root with the sealed V1 cache and source
files. Validate and pilot before a new unique run. Replay committed state only
under matching registry hashes. Annual account and event-cursor checkpoints
are intentionally local.

## 13. Git and collaboration

No commits, merges or pushes. The tracking branch was 0 ahead and 0 behind
locally. Existing successful fetch is recorded in the V1 session. No fresh
fetch in this offline diagnostic. Final worktree before this report:

    ## feat/track-a-data-intake...origin/feat/track-a-data-intake
    ?? HF20_Track2_Directional_Strategy_Research_Menu_Micro_and_Retail_2026-11-10.md
    ?? HF20_Track2_Rapid_Backtest_Engine_All18_Micro_Retail_Codex_Prompt_2026-11-10.md
    ?? replication/
    ?? reports/codex_sessions/2026-11-08_180500_track2_stage012_infrastructure.md
    ?? reports/codex_sessions/2026-11-09_005156_track2_signal_layer_completion.md
    ?? reports/codex_sessions/2026-11-09_032258_track2_stage35_partial_gate.md
    ?? reports/codex_sessions/2026-11-09_082800_track2_stage35_completion_v2.md
    ?? reports/codex_sessions/2026-11-09_151724_track2_stage35_completion_v3.md
    ?? reports/codex_sessions/2026-11-09_204000_track2_final_backtest_v4_hold.md
    ?? reports/codex_sessions/2026-11-10_124734_track2_v5_transport_recovery.md
    ?? reports/codex_sessions/2026-11-10_171400_track2_rapid_v1_all18.md
    ?? reports/codex_sessions/2026-11-10_track2_v5_next_valid_bar.md
    ?? src/lstm_data/trading/
    ?? tests/track2_rapid_v1/
    ?? tests/track2_rapid_v2/
    ?? tests/track2_stage012/
    ?? tests/track2_stage35/
    ?? tests/track2_stage35_completion_v2/
    ?? tests/track2_stage35_completion_v3/
    ?? tests/track2_stage35_v4/
    ?? tests/track2_stage35_v5/
    ?? trading/

## 14. Known issues and limitations

V1 price concessions are assumed above OHLCV trade prints. No contemporaneous
bid/ask or locate observations exist in the consumed source. Price drift is
measured relative to the latest received close, and can be favorable.
Retrospective survivor and action decisions remain. Horizon choices affect
participation, risk exits and exposure as well as scheduled duration. The
same-fill zero-concession number does not include new trading or sizing.

## 15. Decisions for review

Prospective research would need a newly frozen horizon, validated liquidity
and a separate untouched period. Keep the headroom hypothesis distinct from
changes in source coverage or directional signal design.

## 16. Next steps

Review the all-18 and four mechanism tables. If authorized, precommit a limited
retail 10-session and longer horizon test on new data. Any S2-C sizing study
uses matched opportunities under a separately fixed rule. No automated winner
selection or Stage 6 independent audit.

## 17. Artifact inventory

Run and source checkpoints are intentionally ignored in Git. Registry, code,
test receipts, analytical scripts, content manifest and documentation are
additive local review artifacts. Run plus analysis and checkpoints
39,566,905 bytes. Replay 531.82 seconds. Peak process RSS
1,225,359,360 bytes. All new Rapid V2 artifacts
39,984,196 bytes before this report and final manifests.
