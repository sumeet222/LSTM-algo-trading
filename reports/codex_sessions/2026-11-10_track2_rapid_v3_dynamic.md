# Codex Session Report

## 1. Session metadata

2026-11-10 America/New_York. HF20 Rapid V3 authorized research. Branch
feat/track-a-data-intake. Start and end HEAD 8061483cb65d03264a7836b8b882123f67cbe4ad.
Tracked tree started clean. Existing local owner menu and V1/V2/V5 and
replication evidence were retained.

## 2. Executive summary

54 requested portfolios. Census {'COMPLETE': 54}. Direction-only
signals, three risk budgets and one dynamic policy per strategy. A sealed
postrun process scored the three later price references independently.

## 3. Research and protocol impact

Same source/entry/cost conventions, new causal holding and approved 15%
higher-risk name limit. No reset by year. Endpoints of fixed prior
strategies are contextual. Maximum feasibility is calendar-only.
Existing S2-C forecast and calibration were not invoked.

## 4. Files created

src/lstm_data/trading/track2/rapid_v3_dynamic, tests/track2_rapid_v3 and
trading/track2/rapid_v3_dynamic are additive. See V3_CONTENT_MANIFEST.json
for exact paths and hashes. Local runs are Git ignored.

## 5. Files modified

No earlier research, code or receipt modified. The additive amendment
corrected M04's zero-displacement scale and cap recheck after releasing
unsent reservations, and separated overnight offline strata.
A report-only amendment corrected a float/Decimal division. The final
checkpoint was verified and exported once without a funded replay.

## 6. Files deleted, renamed, or moved

None.

## 7. Critical interfaces

policy.initial/observe freeze event or spread references and consume
received scores. DynamicBatch shares features and prices among 54 books.
DynamicLedger reconciles exact positions, claims and order fees and
records causal exit provenance. State binds case axis, code, period
and day. offline analyzes only an already sealed funded exit tape.

## 8. Data and provenance

Original fixed 20 symbols. 2021–24 market dates. One 48-month read pass
each for funded and offline. Calendar metadata only after 2024.
The V1 cache preserves raw-share execution basis versus split-neutral
signal price. V1/V2 protected evidence and all parent checks passed.
OGN claims and exposures follow the prior conditional convention.

## 9. Dependencies

Existing .venv, no package changes, credentials or price downloads.
Arrow CPU-cache sysctl warnings in the sandbox did not prevent reads.

## 10. Commands and tests

V3_VALIDATION_AND_REPRODUCE.md and validation receipts carry exact
commands. 78 passed in 6.65s. Ruff E/F/I and V3 owned types passed.
Installed full Pylance basic check used

    .venv/bin/python scripts/check_python_types.py --pylance-dist ~/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist

It reported 30 pre-existing diagnostics, 27
replication and three Plotly tests. Zero V3. To refresh editor diagnostics,
select .venv/bin/python, enable basic checking and reload Problems.

## 11. Experiment results

2 positive cases. Their names and amounts, all 18 ID rows,
mode costs and exit evidence are in V3_SCREENING_ASSESSMENT.md.
The 2021–24 panel is reused exploratory research. Later marks are
unfunded and conditional censoring is explicit.

## 12. Reproduction

Use the original source hashes and cache and the documented registry
amendment. New run IDs or an exactly bound unfinished restart only.
Run final audit from the actual sealed artifacts.

## 13. Git and collaboration

No commits, pushes or branch integrations. No fresh network fetch in
this offline diagnostic. Final worktree before report:

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
    ?? reports/codex_sessions/2026-11-10_track2_rapid_v2_diagnostics.md
    ?? reports/codex_sessions/2026-11-10_track2_v5_next_valid_bar.md
    ?? src/lstm_data/trading/
    ?? tests/track2_rapid_v1/
    ?? tests/track2_rapid_v2/
    ?? tests/track2_rapid_v3/
    ?? tests/track2_stage012/
    ?? tests/track2_stage35/
    ?? tests/track2_stage35_completion_v2/
    ?? tests/track2_stage35_completion_v3/
    ?? tests/track2_stage35_v4/
    ?? tests/track2_stage35_v5/
    ?? trading/

## 14. Known issues and limitations

Reused survivors, retrospective actions and source QA, modeled costs
and receipt and conditional shorts. R06 pre-entry trail warmup has
explicitly missing support until enough completed history accumulates.
A risk exit can lack a simultaneous score. Post-exit mark statistics
can include recovery of the original execution concession and cannot
be interpreted as a new feasible cash path.

## 15. Decisions for review

Treat nominal allowance, actual hold and mandatory risk reduction as
separate measurements. Freeze any changed trail or sizing policy before
testing a new period. Higher name cap preserves gross, net, vintage
and own-capital limits.

## 16. Next steps

Use the mechanism report for a precommitted fresh-sample test if
separately authorized. S2-C sizing and independent Stage 6 remain separate.

## 17. Artifact inventory

All 54 cases, reason and annual tables, compact exit tape, isolated
post-exit table, registry and exact integrity hashes are in the V3
subtree. Run 56,802,831 bytes, total new 57,658,643 bytes before the
final note/manifest. Funded checkpoint wall 359.85 s,
report recovery 34.24 s, and offline
10.23 s. The funded process peak RSS was lost
when the initial export failed. Recovery and offline RSS are measured.
