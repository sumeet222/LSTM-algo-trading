# Codex Session Report

## 1. Session metadata

- Date:2026-10-13; preflight directory163141 ET; completed2026-10-13T21:25:27.302233+00:00.
- Task: provisional five-stock source integration and universe-agnostic all-gap engineering cleanup, under the attached user implementation prompt.
- Contributor: Codex root, no subagents.
- Branch:feat/track-a-data-intake.
- Starting and ending commit:`5c0455cdccaf03ae2c6834d8cdaa7dc3115f6c27`; no commit created.
- Starting tree:clean, aligned with upstream0ahead/0behind after read-only fetch. Prior15/20-name work is now committed at the human's `Stock universe finalised` commit; this commit title did not change the canonical universe.
- Ending tree:two tracked modifications plus new isolated code/tests/profile/docs/audit package and this report, all uncommitted.
- No PR, stage, commit, push, pull, merge, rebase, stash, reset or cleanup.

## 2. Executive summary

**PROVISIONAL FIVE NATIVE SOURCE COMPLETE; ENGINEERING VIEW COMPLETE; HUMAN REVIEW REQUIRED; SCIENTIFIC G0–G4 HOLD.** Ordered proposalAAPL,COST,CMCSA,SBUX,CME now has16,261/16,261 scheduled main RTH30Min keys and1,736/1,736 prehistory keys **for every stock**. Combined89,985/89,985. Zero genuinely absent candles, maximal runs, missing terminal closes or unresolved source partitions.

The old March2020 four-name request had four successful pages and continued pagination; its transport journal was on HOLD, not exhausted at the three-send lifetime limit. GateA.2 required a narrow decision. The user explicitly approved a new three-name replacement with12-page guard, preserving the old HOLD and99 charges.64 missing three-name month units completed using193 new HTTP200 attempts, cumulative292/1000. All original source pairs were referenced instead of copied; no HON acquisition. Actual64-pair resume made zero GETs.

The all-length causal-flat engineering API is implemented and tested on deliberately synthetic missing1/2/3/12/13/26/39-candle runs, entire sessions and first-session exceptions. It inserts **zero real-source candles**, because the genuine grid is complete. Unknown volume/trade count/VWAP stay null, synthetic terminal evidence is invalid, unit discontinuities/unknown units and missing genuine anchors fail closed. The opt-in profile exposes only candle QA and geometry; it cannot produce actual FT0/T2/TG0, model fits or trades.

## 3. Research/protocol impact

No primary universe, target, horizon,48-step/16-feature math, calendar, origin, split, cost, neural architecture/search/seed or experiment registry change. OriginalAAPL/JPM/JNJ/WMT/CAT and CURRENT_PROTOCOL remain untouched. The new **ENG:TRACK_A_PROVISIONAL_CORE5:v1** source/overlay profile is explicitly retrospective data-usability selection, not a historically known 2020 investable universe or original D1 automatic backup activation. Draft amendment only.

Confirmation2024-07–2025-06 access was allowed source-key/schema/numeric conservation only, after stock selection was already frozen. No features, labels,4h returns, model outcomes, trading, scientific scalers/floors or source-based empirical fitting was executed. Full48×16 FT0/TG0/M2/T2 admission and ≥1352/1502 train retention remain NOT_MEASURED. All scientific experimentsNOT_RUN, pair ledger0/40,16P2/33P3 deferrals and seven blockers unchanged.

## 4. Files created

- `src/lstm_data/source_completion.py`: explicitly authorized SHA-bound legacy replacement and bounded immutable three-name acquisition CLI; secure existingdotenv/client/parser/transport/store reuse.
- `src/lstm_data/candle_cleanup.py`: injected-universe sparse all-gap engineering cleanup, price-unit epoch/active-calendar scope, unknown-volume semantics, strict genuine anchor, protected materialized view and scientific rejection.
- `src/lstm_data/engineering_profile.py`: opt-in profile/source/code reader, existing P3/P4 UniverseSpec geometry, source/policy/order/floor/target/preparation cache identity and prohibited scientific routes.
- `tests/test_source_completion.py`:3 no-network cases for durable send/publication, scoped old HOLD conservation, tamper rejection and zero-GET/zero-secret resume.
- `tests/test_candle_cleanup.py`:19 hand-controlled policy, calendar, unit, unknown-volume, population, cache, quarantine and profile-loader cases including parameterization; existing tests retained.
- `configs/track_a_provisional_engineering_v1.json`: named ordered source engineering profile, fixed sectors, immutable references, explicit mode/policy/code/units/fitting-status bindings.
- `docs/track_a/PROVISIONAL_CANDLE_ENGINEERING_API_v1.md`: API, strict-before equality semantics, inactive real units, geometry-only use, source/overlay reproduction and separate scientific HOLDs.
- `docs/track_a/decisions/Track_A_Provisional_Universe_Engineering_Amendment_DRAFT_v1_2026-10-13.md`: human-review-only D1 proposal, retrospective disclosure and exact later rebuild graph.
- `reports/data_audit/ta_provisional_source_integration_2026-10-13_163141`: original preflight/checkpoints, scoped approval/plan, source QA, sparse overlay and bindings, machine checks,14-item review card. Every file/purpose/type/SHA/size is listed individually in artifact inventory.
- `data/raw/alpaca/track_a_provisional_three_completion_v1`:64 new immutable Parquet/manifest pairs and one separate journal, ignored/local; each exact source request, SHA and page state bound in source_completion.json/complete_genuine_source_manifest.json.
- `reports/codex_sessions/2026-10-13_163141_ta-provisional-source-integration-cleanup.md`: this mandatory17-section report.

## 5. Files modified

- `src/lstm_data/validation.py`:7-line fail-closed guard rejects engineering_only/is_synthetic source frames before ordinary genuine source validation. Prevents authentic hourly/daily/reference paths from stripping an engineering view's scientific distinction. Existing genuine observations and feature math unchanged; tested even with attributes removed and zero fills.
- `README.md`:6-line opt-in profile/API description and unchanged primary/scientific/pair-ledger status.

No other pre-existing file changed. Of1728 protected files, exactly those two intentional changes; all1726 others match startingSHA, including sources, manifests, old journals, frozen protocol, historical reports, prior untracked-now-committed packages, original tests and P2/P3 registers.

## 6. Files deleted, renamed or moved

None. No native source overwrite, cleaning, imputation-in-raw, historical report rewrite, or full-history copy.

## 7. Important interfaces and assumptions

- `source_completion.validated_plan(report: Path) -> dict`: verifies exact user approval/first replacement request/plan/reuse/journal hashes and explicit SIP/USD/split30Min/asof/date/request bounds. OldHOLDs remain in original journals; any changed inherited prefix fails closed.
- `source_completion.acquire(report: Path, get=...) -> dict`: current request allowlist, durable pre/post-send journal,100/min pacing, strict1000 cumulative cap,12 pages and one send/page envelope,256MiB reserve, terminal-only publication. Verified cached exact pairs load no credentials and send no GET.
- `PriceUnitSegment(symbol,start,stop,unit_id,verified,evidence_ref)`: caller-provided compatible-price epoch, aware clocks and verified evidence; no guessed action coverage. Actual current segments remain unverified, irrelevant to0 actual fills.
- `cleanup(frame,symbols,start,stop,profile_id,source_binding,segments,active_intervals=None) -> CleanupView`: true XNYS grid, original-only anchors with end<missingstart, any-length run metadata, no overnight candles, same-unit guarded flat prices and null nonprice placeholders. No target/publication/action/SPY filling.
- `CleanupView.materialize_engineering(mode=MODE)`: source+overlay view with observed/synthetic/unknown/engineering flags, original-row mutation detection, no duplicate keys. Non-scientific regardless of number of fills.
- `CleanupView.require_scientific(activity)`: always rejects; cannot become genuine daily/T2/FT0/TG0/execution evidence.
- `load_engineering_profile(path,mode=MODE) -> EngineeringSelection`: exact ENG profile, source/code SHA validation, original source references, generic cleanup and existing UniverseSpec ordering.
- `EngineeringSelection.for_activity`: onlyCANDLE_QA/DATA_SHAPE. `cache_binding(floor_id,target_id,preparation_id)` includes profile/source/cleanup/policy/universe identity; future object changes invalidate stale artifacts.

## 8. Data/schema/provenance changes

Only missing March2020–June2025 COST/CMCSA/SBUX month units were acquired. First three shared native prehistory months, AAPL full+warmup, CME full+warmup, and prior pilots remain immutable. Pilots are preserved as evidence, but full-month chunks supply the complete current source route. Each new source uses existing ALPACA_SIP_SPLIT_REMED_NATIVE_V1, explicit SIP/USD/split/30Min/asof2025-06-30 and interval-start UTC. Native extended-session records remain stored and separately excluded from the RTH grid.

Every source pair validates schema/OHLCV/uniqueness/UTC and exhausted pagination; every response and normalized source has receipts/contentSHA. Historical available_at and action vintage remain UNKNOWN/UNVERIFIED. Independent split/share-volume and raw conversion QA remain HOLD rather than inferred from query parameters.

`candle_fills.csv` retains complete scheduled UTC/ET, run/index/length, genuine anchor, wall/market age, OHLC, unknown-volume/trade-count/VWAP, unit/cross-session/terminal/long/synthetic/scientific flags schema. `unresolved_candle_gaps.csv` retains exact keys/reasons/context. Both0 rows reflect fully measured zero gaps. Sparse CSV/binding only; no dense cleaned historical Parquet. Materialized candles have unambiguous observed/synthetic markers and engineering-only status. All observed rawOHLCV/trade-count/VWAP values independently compared unchanged across89,985 records.

## 9. Dependency/environment changes

None. Existing repository.venv, declared dependencies, dotenv loading withoverride=False and Alpaca credential mechanism reused. No secrets printed/logged/committed, no purchases/subscriptions, no alternate feed/provider, no Python/editor severity/stub settings changes. No ignores/noqa/unjustified casts/Any suppression. Installed Pylance basic checker retains original include scope plus five newPython files.

## 10. Commands and verification

- `git status --short --branch`, `git branch --show-current`, `git rev-parse HEAD`, `git remote -v`, `git fetch --all --prune`, `git rev-list --left-right --count HEAD...@{upstream}`: clean start, branch aligned0/0; no integration.
- `.venv/bin/python -B -m lstm_data.source_completion --report reports/data_audit/ta_provisional_source_integration_2026-10-13_163141 --output reports/data_audit/ta_provisional_source_integration_2026-10-13_163141/source_completion.json`:64 complete month pairs,193 successful GET attempts, no failure/retry/429. Authenticated execution outside network sandbox only after explicit scoped approval; no charged sandbox failures.
- Actual same-plan resumption with a failing GET sentinel:64 exactSHA pairs,0newGET, journalSHA unchanged, no credential load.
- `.venv/bin/python -B -m pytest -q tests/test_candle_cleanup.py tests/test_source_completion.py tests/test_candidate_quality.py tests/test_stock_source.py tests/test_validation_course.py tests/test_calendar_alignment.py tests/test_p2_handoff.py`:88passed, 18.16s. Earlier focused source/cleanup batches19 and59passed; baseline preflight source/handoff checks also passed. No runtime test failure.
- `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist`:basic0errors/0warnings across134project Python files, 23.13s. Exact logrelease_static.txt; source hash stable. Earlier new-file formatting/dataframe scalar/hash-array/Decimal diagnostics corrected and preserved in failed batch logs.
- `.venv/bin/ruff check .`:PASS. `git diff --check`:PASS.
- `.venv/bin/python -B -m pytest -q`:**635 passed in 1428.85s (0:23:48)**, 1430.54s. One final full run after final functional change; baseline613 tests plus22new, all existing tests/assertions preserved. No repeated20-minute unchanged suites.
- Direct Parquet/derived-view conservation:89,985 numeric records equal; calendar arithmetic1255×13−9×6=16261 and134×13−1×6=1736; allfive early-close/DST cases match. Synthetic7-slot early session: wall-age2490min; market-age0,30,...180; all volumes/trade counts null, genuineT2 false.
- Profile smoke:89985 rows,0fills,0unresolved; all FT0/TG0/T2/P3_TRADING/P4_FIT activities reject.
- Preservation: original source/journal/protocol/tests/report hashes,16P2/33P3/seven scientific blockers/0pairs unchanged.

The preflight inherited613-test check was an exact current-code SHA replay before coding and is not mislabeled as a fresh suite. Once functional code changed, the mandatory full regression was run. Arrow emitted sandbox hardware-cache sysctl warnings in offline probes; validation completed. Tests themselves passed without diagnostic suppression.

Editor check: optional human Problems refresh with repository.venv interpreter; no current human editor count is claimed. OptionA portable checker is the required current parity evidence, no routine restart requested. On another machine substitute its installedPylance extensiondist path.

## 11. Results and experiment status

Source-only and engineering-only results. Main81,305/81,305; prehistory8,680/8,680;0absent,0runs,0maxrun,0missingterminal,0malformed/duplicate/off-grid RTH records. Every observed annualnative guard100%. Entire89,985-key geometry complete and identity-preserving; actual synthetic fills0, unresolved0. All-gap policy proven on fabricated cases, not an empirically approved data-admission technique. Fullgenuine FT0/M2/TG0/T2/48-step scientific retention remainsNOT_MEASURED; original919/1502 and inactive1183/1502 preserved, frozen1352/1502 target unchanged. No model fitting, trading replay or scientific experiment; neural0/40.

## 12. Reproduction

Use README setup with repository.venv and existing licensed source/journal files. Ignored originals/new archives and attempt journals must be handed off legitimately or recreated under explicit source/lifetime authorization; a clone alone does not include them. No hidden Desktop/private temporary file is needed by reusable source or profile APIs.

SourceCLI above uses project-relative frozen proposal/approval and inherited hash references. For completed resume choose a **new output filename**; exact cached pairs make0GET. Missing inherited journal/provenance fails closed; do not silently reset old budgets.

For offline engineering access run the example in `PROVISIONAL_CANDLE_ENGINEERING_API_v1.md`: `load_engineering_profile(Path("configs/track_a_provisional_engineering_v1.json"),mode=MODE)`, then `.for_activity("CANDLE_QA")`. Expected89985observed,0synthetic rows. `.view.fills`/`.view.unresolved` regenerate sparse records from immutable references; choose a new directory and preserve old outputs. Code/profile/source bindings and reconstruction ID are in candle_overlay_binding.json. No real feature/target preparation or fit call exists in this route.

For nativeQA call candidate_quality.audit_native on each symbol's fullrefs from complete_genuine_source_manifest.json for2019-12-18–2025-06-30, split atJuly1,2020 and usequality_summary for annual/native/prehistory counts. Required source identities and data/manifestSHA are portable in that manifest. Run focused/static/Ruff/full commands above; expected635tests and0/0basic diagnostics.

## 13. Git/collaboration status

HEAD `5c0455cdccaf03ae2c6834d8cdaa7dc3115f6c27` unchanged; branchfeat/track-a-data-intake, upstream0/0afterfetch. No Git integration. Two intentional tracked modifications plus exact new files/package/report. Source archive and.env ignored/local. Prior committed15/20-name files protected. Status captured before final report publication; final status also includes this session report:

```text
## feat/track-a-data-intake...origin/feat/track-a-data-intake
 M README.md
 M src/lstm_data/validation.py
?? configs/track_a_provisional_engineering_v1.json
?? docs/track_a/PROVISIONAL_CANDLE_ENGINEERING_API_v1.md
?? docs/track_a/decisions/Track_A_Provisional_Universe_Engineering_Amendment_DRAFT_v1_2026-10-13.md
?? reports/data_audit/ta_provisional_source_integration_2026-10-13_163141/
?? src/lstm_data/candle_cleanup.py
?? src/lstm_data/engineering_profile.py
?? src/lstm_data/source_completion.py
?? tests/test_candle_cleanup.py
?? tests/test_source_completion.py
```

Future integration requires explicit authorization and exact-path review of this inventory, then coordinated commit/PR if approved. No gitadd or push is authorized by this report. Source-sharing and clean-machine data reproduction remain separate obligations.

## 14. Issues, risks and limitations

- Complete source presence is not source publication/action/PIT/scientific retention certification. G0–G4,16P2/33P3/seven blockers remainHOLD.
- Real price-unit epochs remain unverified. No real gap needs an anchor; any future required fill with unknown units, split boundary or missing genuine prior anchor must remain unresolved and require review.
- Causal filling uses nominal completed-interval clocks for engineering only, retainingunknownpublication; no implied actual historical availability or executions.
- No scientific T2/daily close, minute reference, maturedlabel, floor/scaler, course/collaborator signoff or source rights is manufactured. Engineered placeholders have null volume/trade count/VWAP and cannot be admitted scientifically.
- Existing aggregation did not preserve engineering distinctions; a small central source-validator guard now rejects the view rather than silently route it through that consumer. TypedP3/P4 compatibility is geometry only.
- Profile/input source/policy/code/order changes invalidate bindings; stale forecasts/checkpoints cannot be reused as approved artifacts. Later fits must be separately authorized and rebuilt.
- The prior20-name report contains a cosmetic generated `new 20` filename typo; actual file/inventory names were used here. Historical report was not edited.
- Full regressions takeabout22minutes; one final run executed, no remaining failures. Current changes remain uncommitted; ignored raw/journal handoff not supplied byGit.

## 15. Human/teammate decisions

Use the14-item reviewcard. Review native coverage and isolated engineering profile. The narrow March replacement is already explicitly approved and executed; no repeated approval needed. Separately decide any **primary D1 versioned amendment**, retrospective formation/disclosure, genuine source/action/publication/raw execution/maturity/borrow evidence, course/teammate/SPY/proxy/common-clock signoff and empirical fitting/scientific retention work. No fabricated data can clear scientific gates by implication.

## 16. Next steps

1. Consolidated human review of source and engineering API/guard evidence.
2. Resolve exact scientific source/publication/formation/action/clock/rights/approval dependencies and a versioned primary-universe decision if desired.
3. Only after separate authority, rebuild genuine TG0/M2/FT0/floors/scalers/peer identities/matched baselines and retention under the published dependency graph. No automatic research execution or neural-pair spending.

## 17. Artifact inventory and resources

Every new code/test/config/doc/source/report/check file is individually listed with purpose,type,size,SHA in artifact_inventory.csv; all modified existing files also listed explicitly. Its own hash is excluded to avoid self-reference. Large genuine sourceParquets/manifests/journal remain ignored/local; sparseCSV/JSON/Markdown/config/code/tests untracked or modified pending reviewed integration. No dense feature tensor, checkpoint, model, plot, training or portfolio artifact created.

Bounded plan:64×12=768newmaximum +99carried =867≤1000; actual193new+99carried=292, leaving708understricter inheritedcumulative cap. Eachpage sentonce, below lifetime3;193HTTP200, zero failures/retries/429. Actualcomplete64-pairzeroGETresume. Newarchive includingmanifests/journal 4,267,090bytes; audit evidence before finalreport/inventory 9,429,835bytes, below256MiB. Budget summary/inventory give exact byte accounting. OriginalAAPL/CME/three prehistory archives andSPY not copied. No secrets or defaultscientificactivation.
