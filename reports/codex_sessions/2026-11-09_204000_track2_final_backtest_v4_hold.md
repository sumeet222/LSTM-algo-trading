# Codex Session Report

## 1. Session metadata

- Date/time: 2026-11-09 UTC; H0 16:20:44 UTC; final reporting about 20:40 UTC. Actual timestamps are in receipts; no CPU/peak-memory measurement claimed.
- Contributor: Codex, single agent; no delegation.
- Task: finish Stage35, conditional MRK/OGN economics and source integration; run the owner-approved 2021–2024 exploratory study only if all gates pass.
- Branch: feat/track-a-data-intake. Starting and ending HEAD: 8061483cb65d03264a7836b8b882123f67cbe4ad. No commits or pushes.
- Start: dirty with pre-existing untracked replication, trading source/tests/docs and five old reports. End: those preserved, plus additive V4 code/tests/output and this report. No tracked diff.
- Remote fetched at start after sandbox approval. Upstream 0 ahead /0 behind. No pull, merge, rebase, reset, stash or deletion.

## 2. Executive summary

**STAGE35_BACKTEST_HOLD.** Added the historical-capable V4 engine, actual MRK/OGN facts/raw prices, signed entitlements, physical/virtual economics, deterministic restart and research-only release. Full source-only coverage/count checks and all 234 regression tests pass. Four of five actual-source diagnostic windows pass; the June window has two unknown submitted AVGO executions at an unavailable exact-minute standard bar. The full baseline was actually invoked and denied before replay/output construction. No full 2021–2024 baseline/sensitivity performance series or financial comparison was computed. Authorized narrow financial ledger diagnostics, including intermediate cash/NAV and bookkeeping, did run. No assertion that no economic booking ever occurred is made.

## 3. Research/protocol impact

No neural target, feature, checkpoint, calibration, sign, horizon, seven-origin universe, OOS year or frozen historical source was changed. Original F21–F24 C-A/O1 FT16+10 CLOCK/C3 and 2019 sizing references remain. The current owner prompt authorizes a research-only hash-bound successor to V3 RSA, conditional ordinary dividends, academic short availability, MRK settlement and the exploratory study. Protocol frozen before financial diagnostics: four arms, matched/attainable independent accounts, $100,000 per account, continuous years, whole shares, no redistribution after caps, fixed endpoints, latency2, expiry10, 5+5bp adverse side, .005/share/$1 cumulative physical order minimum, 1% prior received volume, 2% ACT/365 borrow, zero funding. Twenty-four baseline/OAT/stress scenarios were frozen and remain unrun as full strategy studies. No performance tuning or final-test selection.

## 4. Files created

All below are NEW/additive; no prior evidence overwritten. Public code interfaces are in the 16 Python modules below. Three new tests live in tests/track2_stage35_v4/: test_special_and_book.py, test_replay_engine.py, test_gap_source_contract.py.

| File | Purpose |
|---|---|
| `src/lstm_data/trading/track2/stage35/final_backtest_v4/__init__.py` | Additive V4 package boundary. |
| `src/lstm_data/trading/track2/stage35/final_backtest_v4/analysis.py` | Predeclared descriptive analysis behind complete financial admission; not used for historical strategy metrics. |
| `src/lstm_data/trading/track2/stage35/final_backtest_v4/book.py` | Decimal physical/virtual cash, lots, claims, fees, carry, risk and atomic event invariants. |
| `src/lstm_data/trading/track2/stage35/final_backtest_v4/certification.py` | Live independent synthetic invariant witnesses for admission. |
| `src/lstm_data/trading/track2/stage35/final_backtest_v4/checkpoint.py` | Typed deterministic JSON snapshot/restart with immutable due-source reconstruction. |
| `src/lstm_data/trading/track2/stage35/final_backtest_v4/driver.py` | Chronological eight-account source-backed event orchestration, pending unknown executions and diagnostic circuit breaker. |
| `src/lstm_data/trading/track2/stage35/final_backtest_v4/execution_calendar.py` | Indexed equivalent XNYS next-observation lookup. |
| `src/lstm_data/trading/track2/stage35/final_backtest_v4/gap_sources.py` | Sealed source-only gap inventory/acquisition, all-date completion verification and exact-gap projection. |
| `src/lstm_data/trading/track2/stage35/final_backtest_v4/market.py` | Read-only raw minute projection, scheduled holes and exact-key source supplementation. |
| `src/lstm_data/trading/track2/stage35/final_backtest_v4/paths.py` | Project-relative paths, immutable publication and SHA256 helpers. |
| `src/lstm_data/trading/track2/stage35/final_backtest_v4/preflight.py` | Source-only calendar/cache/coverage validation. |
| `src/lstm_data/trading/track2/stage35/final_backtest_v4/protocol.py` | Frozen approved four-arm/population/scenario configuration and null-safe sizing eligibility. |
| `src/lstm_data/trading/track2/stage35/final_backtest_v4/release.py` | Owner-authorized hash-bound admission; no RSA/force; live evidence checks before replay. |
| `src/lstm_data/trading/track2/stage35/final_backtest_v4/run.py` | Versioned pilot/baseline/sensitivity/gate CLI. |
| `src/lstm_data/trading/track2/stage35/final_backtest_v4/sources.py` | Bounded official MRK/OGN and raw source acquisition receipts. |
| `src/lstm_data/trading/track2/stage35/final_backtest_v4/special.py` | Signed OGN whole/fractional entitlements, due-bill transition, conditional settlement and basis metadata. |

Top-level V4 documentation/configuration (JSON machine-readable; MD prose):

- `trading/track2/stage35/final_backtest_v4/.gitignore`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/ACTUAL_MATERIAL_ORDER_WITNESSES_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/ECONOMIC_GAP_COVERAGE_BY_STOCK_YEAR_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/ECONOMIC_GAP_SOURCE_PLAN_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/ECONOMIC_GAP_SUPPLEMENT_MANIFEST_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/ENVIRONMENT_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/FINAL_CONSOLIDATED_PROTOCOL.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/FINAL_CONSOLIDATED_PROTOCOL.seal.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/FINAL_FINANCIAL_RELEASE_PACKET_V4.md`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/FINAL_SOURCE_ACQUISITION_AND_COVERAGE_V4.md`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/FINAL_STAGE35_IMPLEMENTATION_AND_SOURCE_DELTA.md`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/FINAL_TEST_MATRIX.md`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/FROZEN_QUARANTINE_SCOPE_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/MATERIAL_PRICE_BLOCKER_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/MRK_OGN_2021_EVENT_AND_ACCOUNTING_RECONCILIATION.md`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/MRK_OGN_SOURCE_AND_ACCOUNTING_MANIFEST_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/MRK_PRICE_BASIS_SUPPLEMENT_PLAN_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/MRK_PUBLIC_KNOWLEDGE_SOURCE_PLAN_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/MRK_RAW_BASIS_COMPARISON_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/MRK_RAW_BOUNDARY_WITNESS_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/OPEN_ISSUES_FINAL_V4.md`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/PRICE_GAP_SCAN_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/PROTOCOL_IMPLEMENTATION_DETAILS_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/RAW_SOURCE_AND_SIGNAL_PREFLIGHT_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/RESEARCH_AUTHORIZATION_AND_BINDING_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/RESEARCH_BACKTEST_READINESS_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/SECONDARY_SOURCE_CAPABILITIES_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/SENSITIVITY_EXECUTION_STATUS_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/SINGLE_GAP_WITNESS_PLAN_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/SOURCE_ACCESS_PLAN_V4.json`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/STAGE35_COMPLETION_HUMAN_HANDOFF_V4.md`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/STAGE35_EXPLORATORY_BACKTEST_REPORT.md`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.
- `trading/track2/stage35/final_backtest_v4/STAGE35_FINAL_HANDOFF_TO_INDEPENDENT_STAGE6.md`: versioned configuration/source/evidence/review artifact; see its title and final child manifest.

Generated files under V4 audits/, releases/, sources/, and ignored PILOT_LEDGER_DIAGNOSTICS/ are individually enumerated with hashes/bytes in FINAL_STAGE35_CHILD_MANIFEST_V4.json, rather than duplicating thousands of provider/date receipts here. sources/gap_raw contains selected exact-gap raw bars, not a second full panel. Local vendor data/large financial diagnostics are intentionally ignored and need source entitlement/reproduction; metadata/plans and code are reviewable. The child manifest has explicit self-exclusion and includes this session report.

## 5. Files modified

No pre-existing tracked, frozen or unrelated file was modified. Iterative fixes were confined to the newly created V4 namespace before its final fingerprint e61bd23fd232. Root gate copies are exact archival copies of the actual refused financial release, not manually promoted gates. Old failed V4 pilot receipts are preserved. Later metadata makes a release time-specific; every invocation must rebuild and recheck bytes.

## 6. Files deleted, renamed, or moved

None. No raw dataset, source partition, original artifact or prior receipt was removed, renamed or replaced.

## 7. Critical functions, classes, variables, and config keys

- Account (book.py): Decimal physical quantities/cash/restricted proceeds plus cohort lots, action claims and append-only journal. Atomic fills allocate internal transfers at a common observed raw mark and external quantity/cost once. physical=sum virtual, independent cash/realized/basis and claims reconcile within 1e-8. Pending virtual gross uses own capital. Restricted proceeds are inside cash, never extra assets/buying power.
- Driver (driver.py): source/calendar/cache -> decisions -> submitted order -> observed ex-post bar -> posting/claims/carry; each account arm/population independent. Unknown past submitted fill is retained and valuation marked incomplete; known next-session future orders do not falsely invalidate current NAV. No automatic later-minute fill for missing submitted execution.
- Driver.restart / checkpoint pack/unpack: explicit typed JSON; no pickle. Sources/actions rebuilt from frozen bytes; same source streams/cash/holdings/journal after interrupted replay.
- create_release/check_admission (release.py): truthful current-prompt authorization plus expected frozen hashes, current protocol/source/code/environment, successful code-bound test receipts and live invariant checks. Financial mode additionally requires all five current-code actual pilots certified. No CLI force, environment override or editable PASS-only authority.
- Distribution/distribution/observe/settle_whole/pay_cil (special.py): 0.1 signed OGN per raw MRK share crossing regular-way Jun3 ex transition; net account rounding before virtual attribution; signed CIL, deferred known marks, conditional Jun10 settlement and postclose alternatives. Illustrative 95.23/4.77 is tax metadata only, no NAV creation.
- Scenario/protocol.py: immutable names/units/scenarios, exact sizing semantics, missing classical controls abstain only their own attainable arm. analysis.py is inaccessible to incomplete financial runs.
- gap_sources: full calendar-only invalid-minute inventory, cap/spacing and stable query receipts; supplements only invalid original keys, cannot replace valid originals or enter neural/control caches.

## 8. Data/schema/provenance changes

Read-only source pass: 48 OOS raw-minute partitions plus existing signal/control partitions; 7,813,800 scheduled ticker-minute cells /7,714,752 valid /99,048 invalid or missing. Existing 131,111 forecasts /9,169 unavailable /87,557 matched counts reproduced without re-forwarding or outcome filtering. All 20/four folds retained. Full predeclared raw SIP gap acquisition: 1,004 dates/HTTP200 complete responses, 88,674 usable exact-key bars, 10,374 still unavailable. No 2025 prices. Provider retrospective receipt is explicitly not live known data; model adjusted hourly values never cash prices.

Primary Merck Form8937 and SEC8k saved/hash-bound; PDF text/render verified via native PDFKit fallback after applying PDF skill; no PDF packages installed. Raw OGN Jun3–4 has 842 records. MRK canonical/provider opening prices agree at boundary; volume/oneclose differences retained as source vintage. Source observations need not match official auction close exactly. Merck May7 public announcement supports known-event stress, not future knowledge.

Preserved action classes: 267 cash events (16 supported AAPL, 251 observed uncorroborated), three splits; eight verified-zero and eight unknown security-years. No unknown AMD/AMZN quarterly dividends invented. Base zero-recorded ordinary events plus separate no-overlap 1.5/3% carry sensitivity; special fallback prohibited. JNJ no-election remains. OGN fractional broker price/payment is conditional, not observed.

Material raw case AVGO2021-06-09 16:33UTC: exact bar query yields only 16:34, trades query 18 records(17 odd-lot I, 1 average/derivative). No pagination. First reported trade 465.04 is NOT adopted as fill. Sources/receipts and MATERIAL_PRICE_BLOCKER_V4.json preserve evidence. This is no universal claim of free-data unavailability: alternate providers were not configured; no keys/accounts solicited/created.

## 9. Dependency/environment changes

None. Existing .venv Python3.14.6, torch2.10.0, pandas3.0.6, numpy2.5.3, pyarrow23, exchange_calendars4.13.2, Pyright1.1.414 and installed Pylance2026.4.1. Full versions ENVIRONMENT_V4.json. Existing local data credentials used only for read-only API; no values logged. Secret scan3,501 new files found0credential values. No brokerage-account or live-order call. Source GETs only. No paid resources or new dependency.

## 10. Commands and tests run

```sh
.venv/bin/python -m pytest tests/track2_stage012 tests/track2_stage35 tests/track2_stage35_completion_v2 tests/track2_stage35_completion_v3 tests/track2_stage35_v4 tests/test_hf20_s2c_ca.py tests/test_hf20_mag_c3_io.py -q
.venv/bin/ruff check src/lstm_data/trading/track2/stage35/final_backtest_v4 tests/track2_stage35_v4 --select E,F,I
.venv/bin/pyright src/lstm_data/trading/track2/stage35/final_backtest_v4 tests/track2_stage35_v4 --pythonpath .venv/bin/python --outputjson
.venv/bin/python -m lstm_data.trading.track2.stage35.final_backtest_v4.run pilot --version pilot_r6
.venv/bin/python -m lstm_data.trading.track2.stage35.final_backtest_v4.run baseline --version financial_gate_final_r1
.venv/bin/python -m lstm_data.trading.track2.stage35.final_backtest_v4.run --help
```

Final tests234 PASS,58.62s. Ruff PASS; owned19 files /0 errors /0 warnings. Full Pylance basic command: .venv/bin/python scripts/check_python_types.py --pylance-dist <locally resolved installed dist>; exact invocation in audits/FINAL_FULL_TYPE_COMMAND.json, output FULL_PYLANCE_SEALED.json. Final fresh check: 681 files, 27 frozen errors /0 warnings; new owned 0. No global clean claim. Editor select .venv/basic then restart Pylance/refresh Problems; final UI confirmation is human-pending. Transient earlier Plotly-test diagnostics retained, not suppressed. No skips/XFAIL/severity relaxation.

Actual pilot current code:26 sessions /3,580 calendar opportunities /8 accounts, four windows PASS /June HOLD; max Decimal residual8.214e-22. No per-run metric optimization. Actual restart Jan4–8 equals interrupted Jan5/resumeJan6 across all streams/cash/shares/hash. Source-only preflight1,275.13s; final pilot per-window31.61/41.53/28.09/34.56/41.81s. 227MB local V4 outputs measured. FullCPU/peak RAM not measured. Baseline command expected exit1 MANDATORY_RESEARCH_GATE_HOLD and no resultdirectories.

## 11. Experiment/results summary

No full financial baseline or sensitivity performance result. No S2C benefit/profitability/Sharpe/significance claim. Actual bounded authorized financial ledger diagnostics include normal/overnight, MRK action, split, ordinary dividend and half-day windows. Four pass; June retains2 submitted AVGO orders (EQUAL -2, S2C -3 attainable), 6 incomplete daily account records, 0 unpriced OGN terminal claims. Existing known inventory remains. Pilot is not a sample to choose strategy parameters. Entire 24-scenario performance suite marked NOT_RUN due mandatoryhold, not discarded after results.

## 12. Reproduction instructions

Use documented repo .venv/source setup and immutable model/cache/data artifacts; run from project root with no PYTHONPATH hacks. Run commands in section10. Source plans specify symbol/date/columns/query/rights and hashes; supply own authorized configured data credentials without printing them. vendor payloads intentionally local; no promise of redistribution entitlement. Snapshot the current artifacts; use unique new run versions. audits/REPRODUCE_ACTUAL_RESTART_V4.py.txt preserves exact restart code for a fresh output namespace. Full baseline must refuse until exact-minute source/policy resolution and all pilots certify. Never force, relabel real sources synthetic, or edit flags to bypass.

## 13. Git / collaboration status

No tracked diff; branch/head unchanged, remote fetched, upstream0/0. Large pre-existing untracked source/research namespaces preserved. New files remain uncommitted. No blanket git add recommended: review code/config/small evidence, rights and large ignored payloads; include this report in an eventual focused branch/PR. Do not pull/rebase/clean unknown local work. Final exact state in audits/FINAL_GIT_STATE_V4.json (captured before report addition; ending status receipt appended separately).

## 14. Known issues, risks, and limitations

V4-PRICE-001 is the smallest material HOLD. A missing published bar does not prove no trade/no fill/cancellation. First oddlot trade or later16:34 marker cannot silently become approved16:33 open. Unknown submitted executions retain quantity uncertainty and capital; no attractive deletion. Full 10,374 raw gap cells remain characterized, not automatically all financial blockers; first actual submitted contradiction is surfaced. Missing/late exits/marks/corrections remain explicit. Source retrospective/provider discrepancies, survivors, assumed latency/cost/borrow, no locates/NBBO and nominaltarget vs economic horizon remain. Original Phase3 methodological mismatch unchanged. Global 27 frozen diagnostics remain. Failed pilot_r1(datecheckpoint),r2(nullablecontrol), valuation futurepending bug and source gaps retain receipts; owned fixes fully retested.

## 15. Decisions requiring human or teammate review

Owner backtest permission already granted; no new generic approval or RSA signature required. Need valid exact-minute raw opening source OR separately review/freeze a quote/trade-derived price construction before changing this specific economic policy. Do not retrocancel unknown submittedmarketorders or select favorable laterbars. OGN CIL/clearing and conditional ordinary/borrow assumptions remain labeled. Stage6 scientific/financial independence not supplied by this agent.

## 16. Next recommended steps

1. Resolve V4-PRICE-001 contract/data with saved bar/trade/condition evidence. Preserve unknown exposures and all failed receipts.
2. Version/hash any actual source/policy change, rerun 234 tests/types/source fixtures, all five pilots and actual restart, then regenerate research release. Current metadata/release snapshots are immutable history, not reusable approval after changes.
3. If all gates PASS, execute already approved baseline/all predefined sensitivities and complete outputs before interpreting. Negative results equally retained.
4. Independent Stage6 later: independentcash/position/action recomputation, source/PIT and dependence-aware/null/selection audit, prospective confirmation. No live claim.

## 17. Artifact inventory

Main review: STAGE35_COMPLETION_HUMAN_HANDOFF_V4.md, FINAL_TEST_MATRIX.md, FINAL_FINANCIAL_RELEASE_PACKET_V4.md, STAGE35_EXPLORATORY_BACKTEST_REPORT.md, Stage6 handoff. Code/config/test metadata intended for review/commit after inspection. Live computed refusal/auth copies and releases/financial_gate_final_r1 are saved. PrimaryissuerPDF/SEC and rawresponse receipts plus complete gap manifest bind actual source evidence. Large vendor payloads, actual pilot journals/checkpoints and profile files intentionally local/ignored,227 MB total V4. No trained checkpoints, plots or strategy-performance artifacts produced. FINAL_STAGE35_CHILD_MANIFEST_V4.json enumerates new code/docs/tests/evidence/localdata with SHA256/bytes, excludes itself and caches. Original manifest bindings preserveprevious lineage. This report is new/untracked and must be included in a future intentional commit.
