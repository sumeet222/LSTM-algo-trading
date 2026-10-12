# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-11, 19:35 America/New_York.
- Contributor/session: Codex / TA-P2-CLOSE-FT0-001.
- Requested task: preserve P2.1/P2.2 and finish all 16 FT0 stock channels, synthetic training transforms, exact tensors, stock/SPY handoff and measured data adequacy.
- Branch: `feat/track-a-data-intake`.
- Starting/ending HEAD: `15bb3b440918387ca14005960534045975dafd1e`; no commit created.
- Start: clean, upstream aligned 0/0 after allowed fetch.
- End: task README/data README changes plus concurrent human RandomNotes changes; new implementation, tests, documentation, evidence and this report untracked; nothing staged.
- Issue/PR: none. Git integration was explicitly outside scope.

## 2. Executive summary

P2_1_P2_2_INTEGRATION_PASS + P2_3_FT0_ENGINEERING_COMPLETE — HUMAN_REVIEW_REQUIRED.

All 16 channels, immutable existing-store adapter, synthetic-only fit/apply certificates, 5×48×16 stock tensor and separate 48×5 SPY join are implemented. Existing clock, minute/proxy TG0, M2, action accounting and D7 code and tests remain byte-identical. Final validation: 322 tests passed; Ruff clean; 50 owned Python files with zero basic Pyright errors/warnings. The researcher’s editor follow-up reports “No problems.”

Actual mechanical training retention is 919/1502 (61.19%), below the frozen 90% guard. Development and both WF folds pass mechanical coverage. Historical source/action evidence, raw proxy conversion, actual empirical certificates and formal approvals remain pending; real causal admission is zero. No API calls, models, backtests, actual-data fits or confirmation feature/target/performance computation occurred.

## 3. Research/protocol impact

- Research question and the accepted stock/SPY comparison remain unchanged.
- TG0 target, M2 math, 240-minute horizon, minute versus hourly-close proxy versions and nominal events remain unchanged.
- Implemented the frozen FT0 feature set and its 13 pooled robust channels; B2/T2/T5 retain native bounds.
- Explicit researcher approval resolved Q1/Q2 pseudocount placement. An additive decision records the exact formulas; frozen D4 was not edited.
- Universe remains AAPL, JPM, JNJ, WMT, CAT; SPY is separate information state. No raw rows or source identity changed.
- Splits, 63-session inner tail, purging, costs, trading mapping, model/search/seed policy and 0/40 neural budget remain unchanged.
- Confirmation was used only for existing raw integrity/gap checks. Protocol pointer, frozen documents, gate status and formal joint/course sign-off were untouched.

## 4. Files created

| Path | Purpose / interface | Type |
|---|---|---|
| src/lstm_data/stock_source.py | Immutable existing-store adapter; StockBar/StockDaily/StockHistory; source/action/raw-conversion gates | py |
| src/lstm_data/stock_features.py | Canonical15-channel rolling engine plus existing M2; per-step source/lineage/mask | py |
| src/lstm_data/ft0_transforms.py | Synthetic-only training floor/pseudocount/pooled-scaler certificates and exact fit/apply chronology | py |
| src/lstm_data/ft0_tensor.py | StockTensor5×48×16; guarded ForecastEvidence bridge and separate D7 join | py |
| src/lstm_data/ft0_audit.py | Offline source QA, mechanical retention/overlap and timing-negative CLI | py |
| tests/test_stock_source.py | Six source/calendar/split/stub/clock tests | py |
| tests/test_ft0_transforms.py | Eight training population/scaler/fallback/window tests | py |
| tests/test_stock_features.py | Seventeen independent16-feature/state/tensor/C01/join tests | py |
| docs/track_a/FT0_API.md | Reusable API and authority/chronology documentation | md |
| docs/track_a/decisions/TA_P2_FT0_Q_VOLUME_001_v1.json | Explicit researcher-approved additive Q1/Q2 algebra; no formal joint sign-off | json |
| reports/codex_sessions/2026-10-11_193541_feat-track-a-data-intake_p2-close-ft0.md | Mandatory technical/collaboration handoff | md |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/baseline.json | Starting tracked SHA/signatures/raw143 file provenance inventory | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/checks.json | Commands/counts/results and corrected development failures | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/diagnostics.json | CLI/Pylance profile and separate editor follow-up | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/diff_check.txt | Validation log / deterministic snapshot / machine-readable checker output | txt |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/extra_after.json | Validation log / deterministic snapshot / machine-readable checker output | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/extra_before.json | Validation log / deterministic snapshot / machine-readable checker output | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/focused_features.txt | Validation log / deterministic snapshot / machine-readable checker output | txt |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/focused_source.txt | Validation log / deterministic snapshot / machine-readable checker output | txt |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/ft0_feature_dictionary.json | Sixteen exact formulas/contracts and per-channel fingerprints | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/ft0_floor_scaler_certificates.json | Actual synthetic fitted numerical certificates/canonical key weights; real pending | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/ft0_math_and_causality.md | Independent hand math, chronology and adjustment explanation | md |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/ft0_source_qa.json | Real source QA with168 gap locators and UNKNOWN clock/action basis | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/ft0_tensor_trace.json | Actual source-only negative tensor and separateSPY masks | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/ft0_tensor_trace.md | Selected positive synthetic and real negative tensor explanation | md |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/g2_timing_label_bridge.json | Pinned real negative origin IDs/times and label-entry waterfall | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/g2_timing_label_bridge.md | Human-readable preserved TG0/cutoff/C01 integration | md |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/human_review_card.md | Eight focused review decisions | md |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/hypothetical_clipping_diagnostic.json | Unactivated synthetic±3/5/10 collision stress illustration | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/initial/ft0_floor_scaler_certificates.json | Preserved superseded own-task evidence, not current conclusions | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/initial/ft0_source_qa.json | Preserved superseded own-task evidence, not current conclusions | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/initial/ft0_tensor_trace.json | Preserved superseded own-task evidence, not current conclusions | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/initial/g2_timing_label_bridge.json | Preserved superseded own-task evidence, not current conclusions | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/initial/retention_and_attrition.json | Preserved superseded own-task evidence, not current conclusions | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/initial/synthetic_ft0_tensor_trace.json | Preserved superseded own-task evidence, not current conclusions | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/market_stock_ft0_handoff.md | Exported interfaces and prerequisites for later packages | md |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/preservation.json | Final protected/public API/raw/journal/ledger/Git assertions | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/pyright_baseline.json | Validation log / deterministic snapshot / machine-readable checker output | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/pyright_final.json | Validation log / deterministic snapshot / machine-readable checker output | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/pytest_baseline.txt | Validation log / deterministic snapshot / machine-readable checker output | txt |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/pytest_final.txt | Validation log / deterministic snapshot / machine-readable checker output | txt |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/retention_and_attrition.json | All 1,998 preconfirmation structural origin rows and loss/intersection/guard tables | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/retention_and_attrition.md | Readable failed train guard, overlapping gap losses and holds | md |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/ruff_final.txt | Validation log / deterministic snapshot / machine-readable checker output | txt |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/runtime.json | Environment/cache/peak-memory measurements | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/scope_and_predecessors.md | Authority/predecessor/baseline inventory | md |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/snapshot_after.json | Validation log / deterministic snapshot / machine-readable checker output | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/snapshot_before.json | Validation log / deterministic snapshot / machine-readable checker output | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/source_audit_stdout.txt | Validation log / deterministic snapshot / machine-readable checker output | txt |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/source_remediation_proposal.json | Proposed-only exact warmup/gap scope, no acquisition | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/synthetic_ft0_tensor_trace.json | Pinned positive actual synthetic raw/scaled/lineage5×48×16 and48×5 join | json |
| reports/data_audit/ta_p2_close_ft0_2026-10-11/integration_manifest.json | Exact additive future Git package, file hashes and protected inherited interfaces | json |

## 5. Files modified

- `README.md`: FT0 API, offline command and explicit retention/source holds; setup preserved.
- `data/README.md`: canonical archive requirements and read-only FT0 audit, adjustment and timing caveats.
- `docs/track_a/RandomNotes.md`: edited concurrently by the human; preserved without Codex edits and excluded from the task integration manifest.
- Every original Python module/test, config, frozen document and historical report remains unchanged.

## 6. Files deleted, renamed, or moved

No existing repository or source file was deleted, renamed or moved. Earlier outputs created by this task were retained under this new package’s `initial/` directory before current evidence regeneration: four real audit artifacts and two synthetic artifacts. Those are superseded snapshots; root artifacts contain current conclusions.

## 7. Critical functions, classes, variables, and config keys

| Interface | Inputs/output and invariants |
|---|---|
| `StockCalendar(start, end)` | Memoizes the existing ScheduledCalendar origin/matching-slot prefixes; exact DST, half-day and stub semantics preserved. |
| `StockBar`, `StockDaily`, `StockHistory` | Immutable adjusted OHLCV, native IDs, source/action epochs and independent publication/action clocks. True terminal close is separate from complete full-session volume. UNKNOWN evidence fails closed. |
| `load_stock_history(config)` | Returns the verified existing archive history and QA. Strict SIP/split/30Min/core-five/as-of/store contract; no downloads, replacement store or double adjustment. |
| `convert_split_basis(bar, action, cutoff)` | Reuses reciprocal split accounting, preserves the original/native publication and requires independently known action evidence. No dividend cash is created. |
| `proxy_reference(bar, factor, evidence, conversion_known_at=...)` | Returns an existing hourly-close reference only with valid complete-hour/raw conversion evidence; documented factors require known-at no later than the proxy observation. Missing/stub/unverified conversions return None. |
| `FeatureCalculator.components/evaluate` | One causal rolling cache per stock/step/mode; frozen 15-channel computation plus existing evaluate_m2; no confirmation features. Cell values, masks, canonical keys and compact dependency lineage are separate. |
| `fit_floors`, `fit_m2_floor`, `fit_scaler` | Explicit synthetic-only populations; positive training p05/frequency-specific medians, exact FitWindow, unique keys, pooled robust fallback and M2 origin mass 50/50. Certificates bind source/action/dictionary and factual fitting time. |
| `transform_reason` | ASOF requires availability at each own cutoff. HISTORICAL_TRAINING permits lawful batch normalization without backdating or relaxing the M2 floor guard. |
| `stock_window`, `StockTensor` | Exact ordered 5×48×16 raw/scaled values, masks, reasons and lineage. Every stock cell must be valid; no fill or shifting. |
| `join_market`, `CandidateJoin` | Reuses window_from_history on identical 48 UTC steps, separate 48×5 D7 mask. Width 21 is future metadata; model wiring is not built. |
| `forecast_bridge(stock, plan)` | Matching ASOF inputs only; no exit, label or fill arguments. Historical-training normalization cannot issue a forecast. |
| `retention_audit`, `market_alignment`, `timing_bridge` | Preconfirmation mechanical coverage, gap overlap, existing D7 structural intersection and real negative timing traces; no real return/label/performance or regime fitting. |

FT0_VERSION, ORDER, SCALED and DICTIONARY_ID fix the versioned 16-channel dictionary and 13 robust-scaled channels. No config schema or original public API changed. Stable semantic source binding is separate from the full observation-content SHA; future-exit content changes cannot invalidate a prior forecast. Rolling lineage hashes include hourly state, prior daily IDs, matching-slot IDs and numeric/mask components without duplicating source arrays.

## 8. Data/schema/provenance changes

- Core stocks: existing 60 immutable SIP/split/30Min pairs, 159,008 native rows and 168 gaps. `ALPACA_SIP_CORE5_SPLIT_30MIN_V1` identifies the new adapter contract; original request identities remain unchanged.
- SPY: existing 11 SIP/raw/30Min pairs, 41,861 bars, 17,197 expected RTH native slots and 129 cumulative attempts; source version unchanged.
- Native publication remains UNKNOWN. Current vendor split-adjusted OHLC and inverse-adjusted shares do not certify original action vintage or raw proxy conversion.
- Explicit UTC timestamps and New York exchange calendar; stubs excluded from hourly inputs and included in legitimate daily close/volume.
- New in-memory FeatureCell/StockTensor/certificate schemas only. No raw migration, feature Parquets or per-model/window datasets; canonical disk cache is zero bytes.

## 9. Dependency/environment changes

None. Authoritative pyproject/editable .venv setup, package versions, editor settings, diagnostic severity and environment variables are preserved. No dependency install, suppression or secret added. Basic checker uses installed Pylance 2026.4.1. All 50 Python files parse with Python 3.11 grammar. Optional stdlib resource peak measurement is platform-aware and may be unavailable on Windows.

## 10. Commands and tests run

- Starting Git inspection and `git fetch --all --prune`: succeeded; no integration performed.
- `.venv/bin/python -B -m pytest -q`: baseline 291 passed in 63.76s; final 322 passed in 237.95s.
- Focused suites after meaningful changes: final feature math/C01 suite 31 passed in 148.15s; final source guards 6 passed. Exact logs are in the evidence package.
- `.venv/bin/ruff check .`: PASS.
- `.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-extension>/dist`: 50 files, zero basic errors/warnings; meaningful batches checked throughout.
- Python 3.11 AST parsing: 50 files PASS; no machine paths or type ignores introduced in new code.
- `.venv/bin/python -m lstm_data.ft0_audit --report reports/data_audit/ta_p2_close_ft0_2026-10-11`: actual offline stock QA/retention and negative stock/SPY timing smoke. Earlier generated evidence retained in initial/.
- Existing D7 structural helper measured the market intersection for all 1,998 preconfirmation calendar-valid origins; no empirical vector fit.
- `.venv/bin/python -m lstm_data.ft0_audit --help`: PASS. `git diff --check`: PASS.
- Public signatures/dataclass order and deterministic clock/proxy/M2/action NAV/F01 snapshots before/after: equal. Original minute/D7 bytes preserved; unchanged independent original math tests pass in the full suite.
- Native PyArrow CPU cache/NEON sysctl probes were denied in the sandbox; reads and audit succeeded. This was not a data failure.
- Earlier new-code fixture/key-binding/fingerprint-cost failures were corrected and recorded in checks.json. A superseded full run had one failure/320 passes; final 322 passes has no unresolved failure. No original expected values changed.
- Human editor check initially reported remaining diagnostics; follow-up reports “No problems.” This is recorded separately from CLI validation, without a screenshot claim.

## 11. Experiment/results summary

No model fitting, predictions, classical/neural experiment, portfolio/backtest or predictive/economic metric. Results are structural data diagnostics and explicit synthetic engineering fixtures.

| Population | Mechanical retention | Guard/result |
|---|---:|---|
| Train | 919/1502 = 61.19% | FAIL 90% |
| Development | 496/496 = 100% | PASS mechanical 90% |
| WF1 | 248/248; 124 sessions | PASS mechanical 85% / 100 sessions |
| WF2 | 248/248; 124 sessions | PASS mechanical 85% / 100 sessions |

Training origin counts are 460/751 and 459/751; both fail 85%. First mechanically complete origin: 2021-01-12. There are 264 startup rejects before it and 319 additional training rejects afterward. M4 fails 484 candidate origins, M3 330 and T3/T4 287 each; counts overlap.

The 168 native gaps form 15 stock-session clusters and directly affect 75 unique 48-window origins. Cluster contributions are 16–18 and overlap; rolling/daily dependencies widen loss. Mechanical stock/SPY intersection equals stock-only retention. Inner 63-session tails mechanically retain 63/62/63 sessions. Matured real-label and regime 85%/10pp guards remain INCONCLUSIVE because evidence is missing. Causal admission and actual fits are zero.

Synthetic fitted AAPL epsH≈.01, epsD≈.001, pH=6.3355, pD=38.7475; scaler has 7,770 unique keys and M2 weights .5/.5. Derived M2 epsilon=.008 from 42 unique origin keys. The pinned positive tensor has 3,840 valid cells plus aligned 48×5 market state; scientific readiness is false. These are not empirical strategy conclusions.

## 12. Reproduction instructions

1. Apply this reviewed package to the recorded baseline commit and follow README’s Python 3.11–3.14 editable `[dev]` setup.
2. Supply the documented immutable 60 stock and 11 SPY pairs/manifests at canonical relative paths. Offline audit needs no credentials; downloads need separate authority and documented provider credentials.
3. Run `python -m pytest -q`, `ruff check .` and the basic checker with the local installed Pylance dist. Expect 322 tests and 50 files with zero errors/warnings.
4. Run `python -m lstm_data.ft0_audit --report reports/data_audit/<NEW-directory>`. Expect measured training retention FAIL, separate source/action/certificate holds and no actual fitting.
5. Synthetic fit/tensor values reproduce in the new test fixtures. Numeric populations, certificate keys/weights and selected trace values are in ft0_floor_scaler_certificates.json and synthetic_ft0_tensor_trace.json.

No private temporary helper or IDE state is required for runtime/tests/CLI. Exact source bytes must match the documented manifests; vendor recreation alone does not certify original historical vintages.

## 13. Git / collaboration status

Branch/HEAD unchanged, upstream aligned 0/0. Fetch only; no stage, commit, push, merge, rebase, stash or reset. README/data README changes are ours; RandomNotes edits are concurrent human work and excluded from our package.

Five new modules, three test modules, API doc, Q decision, evidence and this report remain untracked. Integration manifest lists the exact proposed coherent package with hashes and inherited interfaces. Likely overlap: README/data README and concurrent RandomNotes. Never discard or stage the notes as our work.

After explicit review/integration authority, stage only manifest-listed task files plus the manifest, make a focused commit, then fetch and inspect upstream again. This session does not authorize those actions.

## 14. Known issues, risks, and limitations

- Training retention fails the frozen guard; pre-July warmup and later gaps/long dependencies are substantive data blockers. Warmup alone is not a demonstrated fix.
- Native historical publication, action vintage, raw conversion known-at, payment dates, actual fits and joint/course sign-off remain pending. Known source periods do not repair publication.
- The original M2 floor must be available at each input cutoff. An earlier lawful certificate is still a prerequisite; no initial real bootstrap route or backdated floor was invented.
- Real matured-label and volatility-regime guards are inconclusive; confirmation outcomes remain untouched.
- Recorded source-audit peak: 280,903,680 bytes, 30,060 cached canonical components and zero disk cache. Later lineage-only refinement was full-suite validated; peak is a measured run, not a portable limit.
- Full synthetic suite takes about four minutes; cached immutable certificate identities avoid repeated fingerprinting. Optional resource metric may be None on Windows.
- No failing final tests or known typing errors. Editor “No problems” is human-reported, not automated GUI evidence.

## 15. Decisions requiring human or teammate review

- Review the eight-item card for mathematics, own cutoffs, scaler populations/chronology, measured retention and truthful holds.
- Decide whether to separately authorize a bounded immutable pre-July warmup and 15-cluster gap-verification plan. M4’s calendar lower bound is 2019-12-18; this is not a guaranteed complete warmup or an API budget approval.
- If genuine data remediation cannot satisfy the current guards, predeclare a separate sensitivity branch. No current rule is weakened here.
- Obtain publication/action/raw-conversion/training-population and formal approval evidence before actual empirical admission.
- Git integration, P2.4 actual fits, P3/P4/MC0 models and confirmation use require separate authorization.

## 16. Next recommended steps

1. Review mathematics, causality and retention; preserve the current local work.
2. Scope a bounded data-evidence/remediation task with immutable versioning, transport budget and remeasurement criterion.
3. Establish source/action/transform chronology and formal prerequisites, then separately audit actual causal admission.
4. Advance to later gated implementation only with explicit authority.

## 17. Artifact inventory

The new evidence directory contains untracked metadata, logs and synthetic certificates intended for the review package. Section 4 lists each file’s path/purpose/type; integration_manifest.json hashes the coherent future package. Root artifacts are current; initial/ preserves superseded own-task evidence.

Existing ignored raw stock/SPY archives and journal remain immutable local inputs. No plots, checkpoints, feature datasets, predictions or trading ledgers were created. Temporary helpers outside the project are not runtime dependencies; relevant validation results were copied into the evidence set.
