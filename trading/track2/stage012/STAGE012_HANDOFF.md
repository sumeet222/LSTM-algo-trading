# Stage 0–2 human-review handoff

Verdict: **PARTIAL**. Original bundles are loadable. Infrastructure and synthetic witnesses exist; historical causal feature production and economic accounting are incomplete. No backtest may start from this package as-is.

## What ran

- Existing repository `.venv`, Python 3.14.6, torch 2.10.0, pandas 3.0.6, exchange_calendars 4.13.2.
- `.venv/bin/python -m pytest tests/track2_stage012 -q`: 42 passed; see `audits/pytest_completion.txt` for post-fix receipt.
- `.venv/bin/python -m pytest tests/test_hf20_s2c_ca.py tests/test_hf20_mag_c3_io.py -q`:9 passed; `audits/regression_pytest.txt`.
- `.venv/bin/python -m lstm_data.trading.track2.stage012.audit --output trading/track2/stage012/audits/calendar_witness.json`: calendar-only smoke; no market observations or intents.
- `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist`: full owned-code basic check; final receipt `audits/static_check_summary.json` records result. This absolute path is a local command receipt, never a runtime dependency. Another machine supplies its installed Pylance dist.
- A default-profile targeted check also ran for diagnostics; authoritative parity check is the command above.
- No historical signal dry-run, historical forecast parity, data scan, replication rerun, neural fit, retrospective calibration, trading-risk fit, P&L/Sharpe/turnover, orders sent, accounts, provider downloads or post2024 market reads.

## Model and input registry

`SOURCE_AND_MODEL_REGISTRY.md`, `original_bundles.json` and source-identity receipts identify exact paths/hashes. Original4 annual6572-parameter models actually loaded and predicted **synthetic tensors only**. Original recipes/cutoffs and C3 factors match their phase receipts. Checkpoints/recipes/calibration/source-code identity verification after execution is recorded separately. Independent Phase2 manifest is a reference only; no Phase2 tensor/preprocessing is mixed. Phase3 mismatch remains frozen.

Historical data path presence was verified on2024-01 files only; no price values were sampled. Complete causal original tensor construction is T2-001. Input-only opportunities are represented by calendar origins plus supplied snapshots, never by F09 evaluation keys. The package does not yet enumerate historical ticker eligibility from source stores.

## Protocol review

See the freeze table in TRADING_PROTOCOL.md and typed loader for protocol.json. Human facts: Track2, long/short, seven valid origins, unchanged240-minute model target, annual original bundles and fixed cohorts. Newly proposed: five-session sign, inverse magnitude sizing,0.5–1.5 clip,10% aggregate name cap,20% new-vintage gross,100% gross/net caps,2-minute assumed latency, zero stale reference sessions and5-minute entry deadline. These have not been optimized or empirically validated. No b/floor artifact exists; sizing is unavailable on historical signals.

## Clock witnesses

Minute intervals are [start,start+1min); execution marker denotes a strictly subsequent minute START, with price unspecified. Opening-reference receipt is distinct from prior full-hour FT16. Exit marker is strictly later than endpoint exit decision;10:30 nominal endpoint14:30 with assumed exit decision14:32 gives earliest event14:33. Source delivery delays can push decisions beyond nominal+2. The exact tested calendar source is the installed exchange_calendars XNYS via existing S4 sessions/endpoint.

|Origin ET|Endpoint ET|Assumed issuance UTC|Earliest entry observation UTC|
|---|---|---|---|
|2024-01-08T09:30:00-05:00|2024-01-08T13:30:00-05:00|2024-01-08T14:32:00+00:00|2024-01-08T14:33:00+00:00|
|2024-01-08T10:30:00-05:00|2024-01-08T14:30:00-05:00|2024-01-08T15:32:00+00:00|2024-01-08T15:33:00+00:00|
|2024-01-08T11:30:00-05:00|2024-01-08T15:30:00-05:00|2024-01-08T16:32:00+00:00|2024-01-08T16:33:00+00:00|
|2024-01-08T12:30:00-05:00|2024-01-09T10:00:00-05:00|2024-01-08T17:32:00+00:00|2024-01-08T17:33:00+00:00|
|2024-01-08T13:30:00-05:00|2024-01-09T11:00:00-05:00|2024-01-08T18:32:00+00:00|2024-01-08T18:33:00+00:00|
|2024-01-08T14:30:00-05:00|2024-01-09T12:00:00-05:00|2024-01-08T19:32:00+00:00|2024-01-08T19:33:00+00:00|
|2024-01-08T15:30:00-05:00|2024-01-09T13:00:00-05:00|2024-01-08T20:32:00+00:00|2024-01-08T20:33:00+00:00|
|2024-11-29T09:30:00-05:00|2024-12-02T10:00:00-05:00|2024-11-29T14:32:00+00:00|2024-11-29T14:33:00+00:00|
|2024-11-29T10:30:00-05:00|2024-12-02T11:00:00-05:00|2024-11-29T15:32:00+00:00|2024-11-29T15:33:00+00:00|
|2024-11-29T11:30:00-05:00|2024-12-02T12:00:00-05:00|2024-11-29T16:32:00+00:00|2024-11-29T16:33:00+00:00|
|2024-11-29T12:30:00-05:00|2024-12-02T13:00:00-05:00|2024-11-29T17:32:00+00:00|2024-11-29T17:33:00+00:00|

Full witnesses include DST, Sandy,2018-12-05 and half days in `audits/calendar_witness.json` and synthetic tests. Bounded November25–December3 geometry had maximum 5 concurrent vintages under these event conventions; this is not a universal theorem or a sizing authorization.

## Non-lookahead evidence and limits

Snapshots hold48 scheduled slots,16 fields,10 CLOCK values, masks and explicit Observation dependencies. `issue` verifies calendar slots/category; dependency receipt gates decision; original registry rejects wrong year/recipe. Tests mutate/delete synthetic future endpoint variables and F09 completeness outside the interface, leaving prior records identical. This proves interface separation, not end-to-end historical independence. No historical feature producer is present to certify ingredient completeness. Future-dependency injection into declared observations fails; delayed needed receipt delays decision. New code has no evaluation/universe gate based on future outcomes. Inherited retrospective actions/quarantines/universe and unmeasured source receipts remain limitations.

## Cohort-domain evidence and limits

FixedHorizonPolicy active; DynamicRebalancePolicy and resize events fail. Immutable append-only cohort state supports synthetic entries, partial fills, cancellation and fixed endpoint exits. Net geometry+10−6=+4; old+10 exit leaves−6. Same-side fills/fees reconcile. Opposing external-fill allocation fails until a transfer-price convention is approved. Reservations bound virtual gross and per-name capital without recycling short proceeds. No automatic full-vintage allocation, marked NAV, borrow ledger or real action accounting exists. Splits/dividends/halts/buy-in/borrow/financing produce explicit UNRESOLVED status; other accounting events reject unsupported. No manufactured P&L.

## Blockers and deviations

OPEN_ISSUES.md contains stable T2-001–010 with severity, first witness, impact and deferral. Most material: historical input-only snapshot boundary; unfitted prefix-only b/floor; missing mixed-side and action/cash ledger; unknown borrow; assumed receipt; basis compatibility. First session sign caching is a caller contract, not an implemented scheduler. Repository static validation has inherited frozen diagnostics (T2-010). No original checkpoint is missing: do not mislabel this ORIGINAL_BUNDLE_NOT_LOADABLE. No identical historical-key parity is claimed. This is a deliberately explicit partial implementation, not a completed executable trading engine.

## Stage3 checklist — separate authorization required

1. Review/approve proposed defaults and remaining accounting conventions.
2. Complete causal original input-only snapshot producer, all ingredient lineage and small predeclared historical parity witness; no Phase2 substitution.
3. Separately authorize/document training-prefix-only b/floor preparation, preserve maturity frontier.
4. Implement calendar/ticker signal enumeration, frozen first-decision session trend cache, vintage sleeve allocator, marked aggregate limits, deadline/exit observation orchestration.
5. Resolve internal crossing/fill/fee attribution; implement cash, short proceeds, collateral, borrow, dividends, splits, halts, buy-ins and financing.
6. Only after explicit Stage3 authorization run controlled historical simulator with genuinely subsequent minute fills; costs/latency1/2/5 and borrow stress, identical capital/exposure, all origins and overnight cases.
7. Predeclare constant, rolling-volatility, EWMA and S2C sizes and negative controls. Statistical evaluation/paper trading remain later stages. No dynamic sizing, options or broad optimizer.

## Output integrity and editor handoff

`stage012_manifest.json` lists SHA256 of new source/docs/tests/audits and session report, excluding itself and caches. No source data, frozen replication object or original bundle was modified. No training, strategy backtest or trading occurred. No commits/push. Existing untracked replication work preserved. Refresh VS Code Python interpreter to `.venv/bin/python`, restart Pylance and refresh Problems; final editor confirmation is human-performed and remains pending.

Final validation:42 Stage012 cases passed in28.61s;9 regression cases passed in14.07s. Full basic Pylance parity analyzed599 files:27 errors, all frozen replication/, zero new implementation/test errors and zero warnings. Repository validation HOLD remains. Frozen identity checks:31/31 hash and mtime unchanged.
