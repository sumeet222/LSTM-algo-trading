# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-11T05:46:52.964501+00:00 (start UTC; filename uses America/New_York).
- Contributor / session: Codex, P2.2A-R1.
- Task requested: human acceptance of P2.2A synthetic foundation; introduce hourly-close execution proxy while preserving minute implementation and tests. Source and execution approvals remain separate.
- Branch: `feat/track-a-data-intake`.
- Starting commit: `40840aee20d2fedb481b5f1060909e21c16ca145`.
- Ending commit: unchanged; no staging, commit or push authorized/performed.
- Working tree at start: modified audit ledger and nine untracked corporate-action package files (exact inventory below/preservation.json).
- Working tree at end: inherited work intact, nine R1 files untracked, ledger appended once.
- Related issue/PR: none.

## 2. Executive summary

Implemented a separate synthetic hourly-close proxy module using the accepted minute foundation's TG0 mathematics, action validation, maturity and fitting/purge rules. Exact session-anchored completed hourly CLOSE references replace minute-open prices only through explicit R1 wrappers. Original defaults/source/tests remain byte-identical. Full suite: 205 passed; 25 new tests. No scientific readiness or fill approval follows from implementation acceptance.

## 3. Research/protocol impact

- Core research question, five-stock universe, four-hour horizon, FT0, frozen dates/splits, search budget and final-test protocol unchanged.
- Introduces registered proxy execution/target lineage: `COMPLETED_HOURLY_CLOSE_PROXY:v1`, `TG0:HOURLY_CLOSE_PROXY:v1`; M2 marked `M2:HOURLY_CLOSE_PROXY:v1:REBUILD_REQUIRED` without computing M2.
- Fixed close endpoints 10:30→14:30 and 11:30→15:30 ET; actual scheduled events retained from P2.1. Nominal age 180 seconds, delayed issuance example 360 seconds. Delayed issuance never shifts input cutoff.
- Feature-set changes: none. Trading/backtest implementation: none. No experimental selection or confirmation outcomes.
- Five frozen authorities, CURRENT_PROTOCOL, shared-decision/proxy amendments and all seven historical blockers unchanged. Scientific G2 remains BLOCKED; market branch HOLD; zero neural pairs of 40.

## 4. Files created

- `src/lstm_data/hourly_proxy.py` — reusable synthetic hourly-close reference, causal eligibility, TG0 and fitting interfaces.
- `tests/test_hourly_proxy.py` — 25 independent synthetic timing, numerical, action, purge and version tests.
- `docs/track_a/P2_2A_R1_Hourly_Close_Proxy_API.md` — public API and limitations; standalone extension documentation.
- `reports/data_audit/p2_2a_r1_2026-10-11_014652/package_report.md` — implementation outcome and review scope.
- `reports/data_audit/p2_2a_r1_2026-10-11_014652/checks.json` — five schema-valid scoped evidence checks.
- `reports/data_audit/p2_2a_r1_2026-10-11_014652/proxy_trace_examples.md` — hand calculations and timing counterexamples.
- `reports/data_audit/p2_2a_r1_2026-10-11_014652/human_review_card.md` — five focused code/test review pointers.
- `reports/data_audit/p2_2a_r1_2026-10-11_014652/preservation.json` — hashes, prior-ledger prefix and exact R1 growth inventory.
- `reports/codex_sessions/2026-10-11_014652_feat-track-a-data-intake_p2-2a-r1-proxy.md` — this mandatory handoff report.

## 5. Files modified

- `reports/audit/track_a_events.jsonl`: append-only audit `p2-2a-r1-2026-10-11-014652` records synthetic completion and accepted foundation; G2 BLOCKED, no supersession or clearance. Prior 21 events preserved as exact byte prefix; now 22 events. Existing locked atomic append/schema implementation reused unchanged.
- No existing source/test/config/README/authority file modified. Standalone API document supplies new interface documentation.

## 6. Files deleted, renamed, or moved

None.

## 7. Critical functions, classes, variables, and config keys

All new public interfaces reside in `src/lstm_data/hourly_proxy.py`; exact signatures and contracts are in the API document.

- `HourlyCloseReference`: immutable one-hour raw stock CLOSE with explicit source/version/interval/availability/evidence; rejects stubs, adjusted/index prices, nonfinite or nonpositive values and availability preceding completion.
- `resolve_reference(rows, plan, symbol, event, *, side=None, test_scenario=False)`: exact calendar-slot match; returns reference row, scheduled event, source age and validity at event. Missing/duplicate/unknown timing fails closed; no minute or nearby-row fallback.
- `proxy_causal_eligibility(plan, forecast, entries, *, test_scenario=False)`: consumes accepted upstream full-FT0 ForecastEvidence assertion; checks entry availability by original cutoff. No future exit, action or fitted-floor arguments. Does not independently calculate FT0 or physical fillability.
- `ProxyLabelSample` / `proxy_label_sample(...)`: five reference-boundary split-aware log returns, median/unscaled MAD, versioned origin, references/source/action lineage. Maturity is maximum of scheduled exit and supported required availability. Future exit loss invalidates label without changing causal entry flags. Late publication can mature a label later while reference remains invalid at earlier execution event.
- `ProxyFloor` / `fit_proxy_floor(samples, window, *, test_scenario=False)`: accepted training-only floor max(1e-4, 0.1×training median MAD), with distinct proxy hash binding prices, clocks, intervals, ages and versions. Rejects mixed minute artifacts and invalid/empty lineage.
- `proxy_fitting_membership(...)`: accepted chronological membership and actual-maturity purging with strict proxy version guards.
- `ProxyTG0Target` / `apply_proxy_floor(...)`: accepted TG0 standardization, no clipping/refit; validates floor/sample lineage. Outputs research_ready=False and execution_outcome=NOT_EVALUATED.
- `_require_proxy`: verifies valid sample reference completeness, symbol/side/end/event/source alignment. Accepted private `_valid_plan` and `_split_factors` are reused without editing original module. Original minute APIs remain original contract; callers must use R1 wrappers for proxy artifacts rather than bypassing guards via subclassing.
- No new configuration keys or CLI added. No file/network side effects in proxy functions.

## 8. Data/schema/provenance changes

New in-memory versioned synthetic reference/sample/floor/target schemas only. Aware timestamps normalize to UTC; session boundaries are calendar/P2.1-derived. SYNTHETIC requires opt-in; ASSUMED/unknown availability inactive; DOCUMENTED is caller-provided evidence assertion, not verified here. Raw price split factors use (entry CLOSE, exit CLOSE]; ActionScope must cover cutoff through scheduled exit. A split between cutoff and scheduled entry is included; after exit CLOSE does not alter the reference return. Dividend cash excluded from TG0; P3 scheduled wealth/share accounting separate. Split-adjusted store prices cannot silently become raw references. No acquired price dataset, production labels, M2, scaler, market join, feature computation, fill engine or portfolio output. Historical minute artifacts must not be relabeled as proxy artifacts.

## 9. Dependency/environment changes

None. Existing declared environment used; no secret variables added. Setup remains README virtualenv route. All new committed content uses relative paths; private orchestration helpers are local-only and unnecessary for reproducing tests.

## 10. Commands and tests run

- Repository inspection: AGENTS and recent minute/registration/CA reports, `git status --short --branch`, `git branch --show-current`, `git rev-parse HEAD`, `git remote -v`, `git fetch --all --prune`, ahead/behind inspection. Fetch required network escalation and completed; one ahead/zero behind.
- `.venv/bin/ruff format src/lstm_data/hourly_proxy.py tests/test_hourly_proxy.py`: completed.
- `.venv/bin/ruff check src/lstm_data/hourly_proxy.py tests/test_hourly_proxy.py --fix`: fixed one import ordering issue; subsequent check passed.
- `.venv/bin/python -B -m pytest tests/test_hourly_proxy.py tests/test_labels.py -q`: 53 passed in 8.41s (25 new plus 28 original minute cases).
- `.venv/bin/python -B -m pytest -q`: 205 passed in 12.33s after final lineage guard; inherited CA tests included.
- `.venv/bin/ruff check src tests`: all checks passed.
- Final metadata checks: protected-file hashes, bound artifact hashes, unchanged HEAD/staged entries, exact old ledger prefix, event schema, seven blocker IDs and zero-pair budget. `git diff --check` and final status reviewed before handoff.
- Full suite includes inherited optional bounded 116-action metadata fixture; no source prices scanned, no provider requests, no new metadata acquisition. No full raw-data hash scan claimed.

## 11. Experiment/results summary

Synthetic engineering checks only, not empirical research results. Hand ratios and TG0 scores are detailed in proxy_trace_examples.md and independently asserted in tests. No model/seed/training, predictive/trading metrics, final test or walk-forward analysis run. No fill/risk/portfolio claim. Scoped implementation PASS checks do not clear scientific G2/G4.

## 12. Reproduction instructions

Use README setup (`python -m venv .venv`, activate and `python -m pip install -e '.[dev]'` as documented). No credentials or source data needed for focused R1 tests: `python -m pytest tests/test_hourly_proxy.py tests/test_labels.py -q`; expected 53 passes. Run `python -m pytest -q` for integration (205 passes in this environment); optional CA metadata coverage follows inherited fixture availability. `ruff check src tests`. Read new API document and package examples for synthetic-only usage. Preserve proxy versions when fitting/applying; no production CLI or hidden local helper required.

## 13. Git / collaboration status

- Branch `feat/track-a-data-intake`; HEAD unchanged `40840aee20d2fedb481b5f1060909e21c16ca145`; remote fetched, one ahead/zero behind at inspection.
- No commits/staging/push. Git staged entries unchanged (hash of git ls-files --stage). R1: nine new untracked paths listed above and one append to already-dirty ledger.
- Inherited initial status (all retained byte-for-byte except ledger exact prefix plus R1 row):

```text
M reports/audit/track_a_events.jsonl
?? reports/codex_sessions/2026-10-11_011815_feat-track-a-data-intake_p1-ca-accounting.md
?? reports/data_audit/p1_ca_2026-10-11_011815/accounting_examples.md
?? reports/data_audit/p1_ca_2026-10-11_011815/action_reconciliation.json
?? reports/data_audit/p1_ca_2026-10-11_011815/checks.json
?? reports/data_audit/p1_ca_2026-10-11_011815/human_review_card.md
?? reports/data_audit/p1_ca_2026-10-11_011815/package_report.md
?? reports/data_audit/p1_ca_2026-10-11_011815/preservation.json
?? src/lstm_data/corporate_actions.py
?? tests/test_corporate_actions.py
```

- Ledger is the only shared modified tracked file and likely conflict point. It contains inherited uncommitted CA evidence referencing those untracked files; do not commit the ledger as an isolated R1 change leaving CA evidence artifacts behind. Review/commit the complete CA package first, or review a coherent combined CA+R1 commit. Do not discard the inherited row or selectively rewrite it to force clean history.
- After review, stage the exact nine R1 paths and ledger only with the inherited CA references properly included in history. Suggested R1 commit subject: `feat: add versioned hourly-close proxy foundation`; fetch before push/PR. No integration over dirty work performed.

## 14. Known issues, risks, and limitations

No known failing tests. Source/publication/coverage/action scientific readiness remains unverified and separately blocked. Full FT0 is an upstream assertion; no real eligible fitting population established. Older close used as later execution price can introduce delay bias. Costs do not certify source coverage. Label maturity is not historical fill validation. Hourly risk/retry/liquidation/benchmark exception policy, real-source conversion, M2 recomputation and P3 dividends/cashbook require separate scoped work. Private helpers were not committed and are not dependencies. No full source scan or final portability rehearsal performed.

## 15. Decisions requiring human or teammate review

Original P2.2A synthetic foundation approval already received and recorded accurately; no repeat approval requested. Source and execution approvals, shared proxy policy and downstream admission/exception semantics remain separate. Review R1 version and interval contract before downstream use. No collaborator sign-off fabricated and no global gate cleared.

## 16. Next recommended steps

1. Review R1 code/API, five review-card pointers and preservation manifest.
2. Safely reconcile/review inherited CA and R1 work before commit/PR.
3. Scope source and execution/exception validation or next implementation package explicitly; no automatic P2.3/P3/data acquisition.

## 17. Artifact inventory

Nine new R1 files above intended for version control, currently untracked. Audit ledger tracked but modified; new checks and event bind implementation hashes. Inherited CA artifacts remain untracked and unchanged. No plots, checkpoints or acquired data created. Private /tmp orchestration/baseline snapshots intentionally local; needed evidence is captured in preservation.json. No secrets included.
