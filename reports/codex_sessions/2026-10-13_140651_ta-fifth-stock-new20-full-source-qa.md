# Codex Session Report

## 1. Session metadata

- Task: TA-FIFTH-STOCK-20-NEW-FAST-QA-001; source acquisition and quality assessment only.
- Date/time: session directory2026-10-13_140651; pool frozen2026-10-13T14:13:00.446071-04:00; completed2026-10-13T18:54:39.316651+00:00.
- Contributor: Codex root; no subagents.
- Branch: feat/track-a-data-intake.
- Starting and ending commit: `c3ca6ea940ccb3c01546e1d24b2d2dba6096a7df`; no commit created.
- Starting tree: prior 15-name session report and audit directory untracked, protected.
- Ending tree: those unchanged prior artifacts plus this new package, two new source modules and one new test file, all uncommitted.
- Related PR/issue: none; Git integration prohibited.

## 2. Executive summary

**FIFTH_STOCK_FULL_SOURCE_QA_PASS — HUMAN_REVIEW_REQUIRED; SCIENTIFIC_HOLD.** CME passes complete native candle QA:16,261/16,261 Jul2020–Jun2025 RTH keys plus1,736/1,736 Dec18,2019–Jun30,2020 prehistory. Zero gaps, missing terminal stubs, duplicate/malformed/off-grid RTH records. Five-year1255 and prehistory134 true XNYS sessions.

The exact20-name training screen used six successful batched calls, not20 full downloads. All 20 have exactly60 formation daily sessions and retrospective dollar-volume proxies≥$50m; five names have65/65 targeted keys. Earlier priorities1–8 fail preferred source coverage; CME(priority 9) is the first clean candidate, independently historically identity-qualified by primary documentary triangulation. Other 19 independent security/PIT formation evidence remains UNVERIFIED, notPASS. Their unresolved eligibility cannot outrank CME: higher priorities already fail source quality; lower clean names tie on source quality but have later fixed priority. No historical index-weight crawl or predictive ranking was performed.

RetainedAAPL/COST/CMCSA/SBUX plusCME is only a proposed ordered panel. AAPL earlier full QA is SHA-bound; COST/CMCSA/SBUX are still partial, each64 unverified required month partitions. Whole-panel FT0/TG0/M2 readiness and actual training retention remain NOT_MEASURED. Production stillAAPL,JPM,JNJ,WMT,CAT.

## 3. Research/protocol impact

No target, horizon, feature, calendar, decision time, split, cost, model, search-space or production-universe change. Candidate raw source evidence was added in an isolated inactive namespace. CME selection was frozen from TRAIN five-date source quality and retrospective formation before full acquisition. Confirmation2024-07–2025-06 was accessed only for source-key/schema integrity after that freeze; no features, labels, returns, model outputs or economic outcomes were computed. No next candidate was selected after opening that horizon. All scientific dependencies, P2/P3 deferrals and0/40 budget remain unchanged.

## 4. Files created

- `src/lstm_data/candidate_acquisition.py`: generic plan/pool-bound immutable SIP downloader, durable transport, cumulative caps and zero-GET exact cache resume.
- `src/lstm_data/candidate_quality.py`: symbol-injected 60-session liquidity, native grid/cluster census and training-only ranking; reuse existing validators/calendar/report primitives.
- `tests/test_candidate_quality.py`:16 synthetic/no-network cases for missing/unknown distinction,1/2/3/12/13 runs, early close/DST, identity/duplicate/overlap, formation dollars, sector/training ordering, lifetime-budget and loop/zero-GET/hash preservation.
- `reports/data_audit/ta_fifth_new20_2026-10-13_140651`: frozen manifests, exact screen and full QA records, provenance, preservation, check logs and review documents; every individual file/purpose/SHA/byte count is in `artifact_inventory.csv`.
- `data/raw/alpaca/track_a_new20_fifth_candidate_v1`:73 Parquet/manifest pairs plus dedicated durable journal; each pair/request/SHA/page count is in `fifth_stock_source_manifest.json`; each individual file also appears in the artifact inventory.
- `reports/codex_sessions/2026-10-13_140651_ta-fifth-stock-new 20-full-source-qa.md`: this mandatory17-section handoff.

## 5. Files modified

None of the files present at session start. New task files were iterated before final checks. All 1,527 pre-existing protected files match their startingSHA, including previous untracked15-name work. No old source, manifest, journal, test, feature, configuration, protocol, ledger, README, dependency specification or editor settings was changed.

## 6. Files deleted, renamed, or moved

None. No cleanup, raw correction, imputation, overwrite or source duplication of existing archives.

## 7. Critical functions, classes, variables, and config keys

- `CandidateTransport(BroadTransport)`: preserve reviewed before-send/after-response pacing and lifetime-page rules; add inherited task charges and hash-only continuation lineage; stop source/budget failures. No credential or page-token logging.
- `acquire(report: Path, plan_path: Path, *, get=requests.get) -> dict`: validate pool/plan/prior-journal/selected hashes and explicit SIP/USD/frequency/adjustment/asof/date identities; only frozen selected symbol may have full history. Inactive atomic publication only after complete pagination; SHA-verified cached pairs need zero GET and no credentials. Remaining-send envelope excludes already complete verified cache chunks.
- `liquidity60(frame, ticker)`: exact60 genuine preformation exchange dates; arithmetic mean of rawclose×sharevolume, threshold$50m. Retrospective vendor proxy only.
- `audit_native(refs, ticker, start, end)`: true session expected keys, unknown intervals separately, exact missing/cluster reconciliation, outside-RTH keys separately; no prices synthesized or transformed.
- `quality_summary(ticker, days, gaps)`: exact measured denominators, missing/session/run/terminal and coverage counts.
- `rank_candidates(rows, fixed_sectors=...)`: historical eligibility/source qualified, distinct fifth sector, only TRAIN evidence, preferred zero/small-run masks, deterministic prescribed priority. Confirmation/development inputs are rejected.
- `frozen_pool.json`, `selected_fifth.json`, `screen_request_plan.json`, `full_request_plan.json`: immutable scientific-inactive task configurations and prequery SHA bindings. Current protocol/source pointers never reference this archive.

## 8. Data/schema/provenance changes

New isolated Alpaca namespace only. Full/native and five-date SIP USD30Min split adjustment, asof2025-06-30, ascending limit10000, UTC interval starts; formation raw1Day/asof2020-07-01. Existing canonical `ALPACA_SIP_SPLIT_REMED_NATIVE_V1` metadata contract retained, explicit `available_at=null`, `availability_basis=UNKNOWN`, `action_vintage=UNVERIFIED`, `scientific_activation=false`. Every response and normalized Parquet has receipt/content hashes; each partition is published atomically once after exhausted pagination. No feed fallback or second vendor.

67 full month partitions:2019-12-18–2025-06-30. Actual prehistory derived by existing FT0 dependency calendar, lower boundaryM4 and causality clocks rather than fitted returns. Main yearly totals2020Jul–Dec1652,20213270,20223257,20233238,20243258,2025Jan–Jun1586; all observed100%. Prehistory1736; additional3864 outside-RTH source keys preserved/excluded. Zero-row missing CSVs have headers and represent truly fully measured intervals, not missing requests.

Formation source supports1200 raw daily rows for20×60 sessions. CME proxy$413,761,647.02/day. Historical CME security is supported by the2020 SEC cover and membership/Financials inferred from primary2020 index-fund holdings plus issuer S&P inclusion evidence. This retrospective triangulation is not an official July1 daily constituent certificate or certified historical publication clock. Other independent eligibility statuses are unresolved. Known2012 CME split predates prehistory; exhaustive later corporate-action history/vintage/raw proxy conversion remainHOLD. URLs and evidence rationale are frozen in `formation_evidence.json`.

## 9. Dependency/environment changes

None. Existing `.venv/bin/python`, dotenv loader and credentials mechanism reused; local.env loaded with `override=False`, never printed or committed. No package installations, purchases, plan changes, editor/severity modifications, casts/ignores/noqa or excluded files.

## 10. Commands and tests run

- Read-only Git inspection: `git status --short --branch`, `git branch --show-current`, `git rev-parse HEAD`, `git remote -v`, `git fetch --all --prune`; upstream ahead1/behind0. No integration.
- `.venv/bin/python -B -m lstm_data.candidate_acquisition --report reports/data_audit/ta_fifth_new20_2026-10-13_140651 --plan reports/data_audit/ta_fifth_new20_2026-10-13_140651/screen_request_plan.json --output reports/data_audit/ta_fifth_new20_2026-10-13_140651/screen_acquisition.json`: six completed HTTP200 source units, no retry/failure.
- `.venv/bin/python -B -m lstm_data.candidate_acquisition --report reports/data_audit/ta_fifth_new20_2026-10-13_140651 --plan reports/data_audit/ta_fifth_new20_2026-10-13_140651/full_request_plan.json --output reports/data_audit/ta_fifth_new20_2026-10-13_140651/full_acquisition.json`:67 complete monthly units; cumulative73 new GETs.
- Actual zero-GET resume of both plans with a failing GET sentinel:73 cached pairs verified, journal SHA unchanged, no credential loading.
- `.venv/bin/python -B -m pytest -q tests/test_candidate_quality.py tests/test_broad_screen.py tests/test_fast_screen.py tests/test_greedy_screen.py`:57passed, 25.36s.
- `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist`:basic0errors/0warnings across 129Python files, 15.47s. Installed Pylance original severity/include scope; new Python included. Earlier five diagnostics and their corrected successor outputs retained.
- `.venv/bin/ruff check .`:PASS. Formattingcheck three new filesPASS; `git diff --check`PASS.
- `.venv/bin/python -B -m pytest -q`:**613 passed in 1330.95s (0:22:10)**, 1332.68s. Run once after last functional edit; identical source hashes during check. Existing 597tests retained plus16new, no weakened assertions.
- Independent raw hand checks: expected first/last/early-close/DST clocks and keys;65 pilot/monthly OHLCV records exactlyequal, no return computation.
- Preservation: all 1,527 protected files/prior-journal prefixes/exactP2=16,P3=33/0pairs/sevenblockers unchanged.

Transient development failures: missingStorageLimit in one new test fixture corrected; DatetimeIndex typing and explicit heterogeneous-dict annotations corrected five basic diagnostics; two temporary evidence-builder field-name errors corrected before selection/acquisition. No production source/code was overwritten. Arrow printed sandbox hardware-cache sysctl warnings during local read-only probes; all validations completed, no source/diagnostic/test warnings claimed from those messages. Full Pytest actual output is preserved separately.

Editor verification: OptionA is authoritative for this task. Optional human refresh with repository `.venv/bin/python` can confirm current VSCode Problems; no current human editor0 count is claimed, and no restart/settings changes are requested. On another machine pass its installed Pylance `dist` path to the same portable checker.

## 11. Experiment/results summary

No predictive/economic experiment, fit, label, feature, scaler, floor, baseline, backtest or neural pair. Source-only study:20 training-day candidates, one pre-ranked full candidateCME. Five-date aggregate1300expected,707observed,593missing in53maximal runs;15names have long runs,5clean. CME full+prehistory17997/17997,0missing. All observed source native guardsPASS. Full FT0 retention remainsNOT_MEASURED, not inferred1502/1502. Original 919/1502 and inactive1183/1502 preserved; frozen target1352/1502 unchanged.

## 12. Reproduction instructions

Use README-authoritative clean `.venv` editable install and documented Alpaca credentials in local.env. Keep all task configs/evidence and original source artifacts; current untracked code/report must be reviewed and explicitly integrated by a human before another clone has them.

The downloader invocation above is portable from the project root. For a verified existing archive use a **new output filename**, preserving old outputs; resume makes zero GETs. On a fresh authorized reconstruction, the same frozen plans retrieve exact material identities with new immutable journals. Do not bypass old lifetime-page holds or treat retrieval as a new scientific approval.

Recompute numerical full QA without fitting: load `reports/data_audit/ta_fifth_new20_2026-10-13_140651/full_acquisition.json` chunks and `reports/data_audit/ta_fifth_new20_2026-10-13_140651/selected_fifth.json` ticker, then call `lstm_data.candidate_quality.audit_native(chunks, ticker, "2019-12-18", "2025-06-30")`. Split its day/cluster lists at2020-07-01 and call `quality_summary` to reproduce16261and1736 denominators; annual slices reproduce the six year counts. `liquidity60(verified_frame(formation_chunk), ticker)` reproduces60-session proxies; raw snapshot-evidence URLs/rationale are in `formation_evidence.json`. No Desktop/private temporary file is required by the reusable source or numerical audit path. Markdown/CSV records contain complete measured facts, exact provenance and caller inputs.

Run focusedchecks, portable Pyright/Pylance checker, Ruff and fullpytest commands above. Expected613PASS,0/0diagnostics, originalsourceSHA unchanged. New rawsource is intentionally ignored and must be supplied via documented archive/authorized acquisition, not presumed present in anotherclone.

## 13. Git / collaboration status

Branchfeat/track-a-data-intake, HEADunchanged, ahead1/behind0 afterfetch. No staging/commit/PR/push/pull/merge/rebase/stash/reset/clean. Existing teammate/untracked15-candidate work protected. Current tracked diff empty; allnewpackage/code/session files remain untracked. Ignored rawsource/.env remain local. Review/integrate only exact intended files later under explicit Git authorization; no broad gitadd.

```text
## feat/track-a-data-intake...origin/feat/track-a-data-intake [ahead 1]
?? reports/codex_sessions/2026-10-13_100857_ta-final-fifth-stock-15-candidates-source-screen.md
?? reports/data_audit/ta_fifth_new20_2026-10-13_140651/
?? reports/data_audit/ta_final_fifth15_2026-10-13_100857/
?? src/lstm_data/candidate_acquisition.py
?? src/lstm_data/candidate_quality.py
?? tests/test_candidate_quality.py
```

## 14. Known issues, risks, and limitations

- Three retained archives incomplete; no wholefive-stock source readiness claim.
- Other 19 independent identity/PIT eligibility statuses unresolved. Lower clean alternatives are not full-history rejects.
- CME historical membership qualification is explicitly retrospective primary-document triangulation, not an officialJuly1 constituent file or publication certificate; human universe/amendment/source review required.
- SIP available_at/actionvintage, exhaustive actions/rawexecutionunit conversion/dividends/paymentdates, causal execution/exception evidence, collaborator/course signoff, empirical fitted certificates/floors/scalers and scientific retention remain independentHOLDs.
- Source-only confirmation key QA was permitted after selection; no confirmation candidate comparison or outcome access.
- Old March four-page HOLD and its lifetime charges remain untouched. New broader pageguard did not authorize resending that old request.
- Full regression runtime is substantial; one final suite was required and run, not repeated during downloads. No remaining test/static failure.

## 15. Decisions requiring human or teammate review

Review `human_review_card.md`: accept CME only as provisional source-quality evidence; separately authorize completion of COST/CMCSA/SBUX; decide any versioned canonical universe amendment and its hindsight/formation disclosure. Keep scientific publication/action/fitting/causal/source/course approval separate. No further work or stock switch is activated by this report.

## 16. Next recommended steps

1. Human review ofCME evidence and partial whole-panel status.
2. Separately scoped and budgeted completion of only missing three-name partitions, resolving old pagination/lifetime hold explicitly.
3. Complete five-source/key/prehistory audit, then independently authorized scientific eligibility/action/clock/retention work. No empirical labels/fits/trading orP4real usage until approved.

## 17. Artifact inventory

Every task-created source/report/check/code file is listed individually in `artifact_inventory.csv` with purpose,type,bytecount andSHA.73sourceParquets+73manifests+dedicatedjournal are ignored/local under the isolated archive. Small source metadata, CSV/Markdown QA, logs, frozen taskconfigs, new code/tests and thisreport are untracked pending authorized humanintegration. No plot/checkpoint/model/featureinput or trading artifact created. Inventory excludes its own bytes/hash to avoid self-reference.

Resource accounting: worstcase full envelope836including old 26vs ceiling1000; actual73new+26carried=99. All 73HTTP200, zero failed/retried/429; actual eachrequestone terminalpage. SourceParquets 1,566,353bytes; archive(manifests+journal included) 1,798,897bytes before finalinventory; report evidence 2,681,602bytes before finalreview/checkfiles, safely below256MiB. Final exact budget in `budget_summary.json`. No canonical archive copied. Master source hashes in `fifth_stock_source_manifest.json`; checks/source/protocol preservation in separate JSON.
