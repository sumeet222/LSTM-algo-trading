# Codex Session Report

## 1. Session metadata

- Date/time: 2026-11-11T00:30:03.152204-05:00; task date 2026-11-11.
- Contributor/session: Codex, read-only final-three portfolio-risk attribution.
- Branch: feat/track-a-data-intake.
- Starting/ending HEAD: 8061483cb65d03264a7836b8b882123f67cbe4ad.
- No commit, push, fetch or integration performed. Cached upstream tracking only.
- Start: tracked tree clean; substantial existing untracked replication, trading,
  tests, reports and owner prompts preserved. End: only additive task namespaces
  and this report added; tracked diff remains empty. No PR/issue.

## 2. Executive summary

Analyzed all 12 saved MATCHED books and nine S2C/control pairs; no new portfolios,
models, forecasts or market-source data. All available accounting reconciles (maximum
USD 2e-11 residual, tolerance 1e-7), 1005 sessions each. Verdict
PARTIAL_WITH_EXPLICIT_MISSING_FIELDS: available daily risk analysis complete;
unarchived per-stock exposures/cap/mark/action fields explicitly unavailable.
R01 and M04 show no general S2C risk advantage. R07 native net/Sharpe/Sortino/DD
improve, but volatility rises, rolling-relative gain is tiny and action-sensitive,
and constant mean-exposure scaling removes its DD advantage versus equal/rolling.

## 3. Research/protocol impact

No changes to targets, directional policies, universe, market data, costs, horizons,
forecast recipes, splits, eligibility or original portfolio paths. No fitting, replay,
optimization, new selection, Stage 6 or untouched confirmation. Analysis-only risk
formula/denominator conventions sealed before calculation; calendar CAGR explicitly
supplemental. Underlying 2021–24 repeated-use/survivor caveats remain.

## 4. Files created

Task namespaces: `src/lstm_data/trading/track2/final3_risk_attribution`, `tests/track2_final3_risk_attribution`, `trading/track2/final3_risk_attribution_v1` and this
session report. Complete per-file inventory follows. Final ANALYSIS_MANIFEST.json
is also created after this report and binds its hash; no source records copied.

- `trading/track2/final3_risk_attribution_v1/ANALYSIS_PROTOCOL.json` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/ANALYSIS_REPRODUCE.md` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/ATTAINABLE_REFERENCE_ONLY.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/COMPARISON_OF_3_POLICIES.md` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/COMPLETION_HANDOFF.md` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/CONCENTRATION_AND_ECONOMIC_LIMITATIONS.md` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/INPUT_AND_ACCOUNT_BINDINGS.md` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/METRIC_DEFINITIONS.md` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/OWNED_TYPE_CHECK_CORRECTION.md` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/RECONCILIATION_AND_VALIDATION.md` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/REPORT_RECEIPT.json` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/SOURCE_REGISTER_AFTER.json` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/SOURCE_REGISTER_BEFORE.json` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/WHAT_DID_S2C_IMPROVE.md` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/ACCOUNT_BINDINGS.json` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/ACCOUNT_RECONCILIATION.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/ANALYSIS_RECEIPT.json` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/ANNUAL_AND_STOCK_CONTEXT.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/ANNUAL_NAV_RISK.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/ANNUAL_PHYSICAL_EXECUTION.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/CHANNEL_ASSESSMENTS.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/COHORT_WIN_LOSS_CONCENTRATION.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/COMMON_CONTROL_TOP_TWO_NAME_OMISSION.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/COST_CAPITAL_ATTRIBUTION.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/DAILY_CAPITAL_DESCRIPTORS.parquet` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/DERIVED_PARITY_CHECKS.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/EXIT_RISK_AND_HOLDING_CONTEXT.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/EXPOSURE_BIN_DESCRIPTORS.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/FUNDED_OPPORTUNITY_OVERLAP.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/MATCHED_OPPORTUNITY_COUNTS.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/MATCHED_PORTFOLIO_RISK_TABLE.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/NONEXECUTABLE_EXPOSURE_AND_VOL_NORMALIZATION.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/PAIRED_CONTROL_DRAWDOWN_INTERVALS.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/PAIRED_CONTROL_TAIL_DATES.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/PAIRED_DAILY_DIFFERENCES.parquet` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/PAIRED_MONTHLY_AND_ANNUAL.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/PAIRED_PRICE_ACTION_COST_BRIDGE.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/S2C_PAIRWISE_RISK_DELTAS.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/START.json` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/SUPPLEMENT_RECEIPT.json` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/TAIL_DRAWDOWN_EPISODES.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/runs/analysis_01/WORST_TAIL_DAYS.csv` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/validation/FULL_PYLANCE_RAW.txt` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/validation/OWNED_PYLANCE_FINAL.json` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/validation/OWNED_PYLANCE_FINAL_02.json` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/validation/OWNED_PYRIGHT.json` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/validation/OWNED_PYRIGHT_02.json` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/validation/PYTEST.json` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/validation/PYTEST_FINAL.json` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/validation/RUFF.json` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/validation/RUFF_02.json` — derived evidence, provenance or validation receipt
- `trading/track2/final3_risk_attribution_v1/validation/RUFF_FINAL.json` — derived evidence, provenance or validation receipt
- `src/lstm_data/trading/track2/final3_risk_attribution/__init__.py` — read-only analysis implementation
- `src/lstm_data/trading/track2/final3_risk_attribution/analysis.py` — read-only analysis implementation
- `src/lstm_data/trading/track2/final3_risk_attribution/cli.py` — read-only analysis implementation
- `src/lstm_data/trading/track2/final3_risk_attribution/io.py` — read-only analysis implementation
- `src/lstm_data/trading/track2/final3_risk_attribution/metrics.py` — read-only analysis implementation
- `src/lstm_data/trading/track2/final3_risk_attribution/reporting.py` — read-only analysis implementation
- `src/lstm_data/trading/track2/final3_risk_attribution/saved.py` — read-only analysis implementation
- `src/lstm_data/trading/track2/final3_risk_attribution/supplement.py` — read-only analysis implementation
- `tests/track2_final3_risk_attribution/test_analysis.py` — read-only analysis implementation
- `trading/track2/final3_risk_attribution_v1/ANALYSIS_MANIFEST.json` — final child content/source/test/runtime manifest.
- `reports/codex_sessions/2026-11-11_track2_final3_risk_attribution.md` — mandatory session handoff.

## 5. Files modified

No preexisting project file changed. Owned new utilities were refined during this
session for typing, schema names and portable output-root configuration. Financial
protocol values and original results were never edited. Failed/zero-file validation
receipts retained alongside authoritative final receipts.

## 6. Files deleted, renamed, or moved

None. No clean, stash, reset, restore, migration or file deletion.

## 7. Critical interfaces

- io.prepare(): SHA256/mtime relevant saved inputs and seal protocol into a new root.
- saved.load_saved(): bind immutable case IDs, validate 12 books/1005 sessions,
  original Decimal financial totals, daily/terminal and cohort/physical identities.
- metrics.simple_returns/performance/drawdowns/tail/nonexecutable_proxy: pure saved
  wealth arithmetic, explicit initial NAV, 252/0-rf, MAR0, ceil-tail ES and guardrails.
- analysis.build()/pairwise(): cached daily/cohort/fill re-aggregation and nine pair
  comparisons, no event generation or future price lookup.
- cli --run-id [--output-root PATH] [--prepare]: exclusive fresh publication;
  creates bounded HOLD witness on source/account error, never overwrites a run.
- reporting/supplement: compact human reports, common-name arithmetic sensitivity,
  archived Sharpe/DD/annual parity and projected existing physical-year attribution.
- No side effect outside fresh analysis namespaces; source reads only. Any resumed
  descriptive re-aggregation uses a new run/output root, not a trading checkpoint.

## 8. Data/schema/provenance

Canonical final-slate analysis_03 and sizing-matched-20261110-r1, protocol hash
4c0668bda5e4b84c5a346ad96bb23767af1e27edd98ab349022bd9977ea610d6. Binding uses
RESULTS strategy_id+variant case, avoiding raw cohort arm/book and population/mode
collision. 12060 daily marks, 8029 cohorts, 16758 fill records. No new source
partitions, forecasts or model bytes read; 26 relevant input/anchor fingerprints
verified against frozen content manifest where applicable and unchanged afterward.
Scheduled close metadata is UTC; source epochs map to ET for date/slot attribution.
Saved conditional action/borrow assumptions inherited, not independently re-audited.

## 9. Dependencies/environment

No install/dependency/setup change. Existing .venv Python3.14.6, pandas/numpy/pyarrow,
exchange_calendars and standard library. Project-relative paths/configurable output
roots. Pylance extension location is machine-specific verification metadata only.

## 10. Commands and tests

- `.venv/bin/python -m lstm_data.trading.track2.final3_risk_attribution.cli --run-id analysis_01`
- `.venv/bin/python -m lstm_data.trading.track2.final3_risk_attribution.reporting --run-id analysis_01`
- `.venv/bin/python -m lstm_data.trading.track2.final3_risk_attribution.supplement --run-id analysis_01`
- `.venv/bin/python -m pytest -q tests/track2_final3_risk_attribution`:16 PASS,no skips.
- `.venv/bin/ruff check --select E,F,I src/lstm_data/trading/track2/final3_risk_attribution tests/track2_final3_risk_attribution`:PASS.
- `.venv/bin/pyright --pythonpath .venv/bin/python src/lstm_data/trading/track2/final3_risk_attribution tests/track2_final3_risk_attribution --level error`:zero owned errors.
- `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist`:
  780 files,32 inherited errors (27 replication,3 Plotly tests,2 frozen R01),184.383s.
- Explicit nine-file basic installed-Pylance config:0 errors/warnings; exact temporary
  config/command receipt OWNED_PYLANCE_FINAL_02.json. First zero-file config rejected.
- `git diff --check`, `git diff --stat`, `git status --short --branch`:reviewed.
- Normal ps inspection denied by sandbox. No trading worker launched or restarted.
- Arrow CPU-cache sysctl sandbox warnings were nonfatal; reads and validation pass.

## 11. Results summary

Main saved-output aggregation10.558s,peak RSS199.26MB. No new funded experiment.
R01 S2C−8276.07 vs EQUAL−8981.08:less loss,larger DD/ES95; worse net than rolling/EWMA.
M04 S2C−2036.51 vs EQUAL+2606.13,rolling+1718.00:weak results despite slight vol reduction.
R07 S2C+3111.78 vs rolling+2984.09:increment+$127.68 includes raw-price−$21.80,
action+$153.98,cost+$4.50; positive annual relative return only2022. Higher vol all
controls, lower mean exposure. Own top-two removal leaves only+$41.08, while common
rolling-top-two omission leaves S2C+$812.17 vs rolling+$697.10. Neither is funded.
No universal benefit, no new shortlist or profitability claim.

## 12. Reproduction

Follow ANALYSIS_REPRODUCE.md. Supply exact-hash documented local final-slate artifacts
from project archive after clone, existing environment, fresh --output-root and
--prepare. Never run over this finalized directory. Missing required artifacts fail
closed. Code uses no developer paths for data. No hidden vendor/network requirement.

## 13. Git/collaboration

Branch/HEAD unchanged; no commits. Existing untracked work protected. No remote
fetch under read-only/no-network task instruction. Cached tracking showed no
branch divergence; actual remote freshness not asserted. Stage only these new
namespaces and this report if a teammate separately authorizes a focused commit;
do not add the whole untracked trading/ or replication/ trees. No merge required.

## 14. Known issues/limitations

Per-stock marked exposure, physical gross/long-short risk, exact invested minutes,
name/vintage utilization, reservation-complete buying power and complete daily action
journal/receipt timestamps not archived. Generic earlier partial-risk cause on155
matched fixed-policy cohorts cannot identify the true cap trigger. Overnight-cohort
span is not exact overnight P&L attribution. RTH virtual gross is not physical gross.
Daily float precision explains tiny residuals. Reused survivor sample, assumed
receipt/locates, raw-open proxy and 240-minute magnitude versus variable hold remain.
Global type-clean gate remains HOLD for32 inherited diagnostics, not hidden/fixed.
No empirical significance claim or bootstrap. Final editor refresh is human-confirmed.

## 15. Decisions requiring review

No approval needed to finish this authorized saved-output analysis. Economic use,
new funded research, any source extraction/replay to recover unavailable fields,
new baseline selection or Stage6 require separate authority. Do not infer risk
superiority from a deterministic rank or from action-sensitive small USD gains.

## 16. Next steps

Read WHAT_DID_S2C_IMPROVE.md and nine paired rows. Preserve native controls. Preregister
prospective/untouched matched sizing evaluation with downside/exposure endpoints and
full risk/action snapshots; do not search more historical rules in this task.
Refresh editor Problems using .venv and preserve frozen legacy diagnostics.

## 17. Artifact inventory

All paths in section4 are newly untracked/additive. Tables and compact Parquet
hold saved-account descriptors, not raw market panels. New outputs total about1.1MB
before final manifest; authoritative exact byte count is in ANALYSIS_MANIFEST.json.
No models, source caches, journal archives or checkpoints created. Original inputs
remain intentionally local and referenced by path/hash, not copied.
