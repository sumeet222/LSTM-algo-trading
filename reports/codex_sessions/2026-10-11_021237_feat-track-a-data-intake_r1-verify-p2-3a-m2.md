# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-11T06:12:37.975557+00:00 (Gate A baseline); filename America/New_York.
- Contributor/session: Codex, P2.2A-R1-VERIFY → P2.3A-M2, explicit conditional user prompt.
- Task: verify actual R1, preserve inherited CA/R1; only on PASS implement scheduled grid and causal M2; stop for human review.
- Branch: `feat/track-a-data-intake`; starting/ending HEAD `40840aee20d2fedb481b5f1060909e21c16ca145` unchanged.
- Starting tree: dirty ledger plus18 untracked inherited CA/R1 files; exact status below.
- Ending tree: inherited work intact;8new files and one ledger append. No staged changes/commits/PR/push.
- Related issue/PR: none. Remote fetched once;1ahead/0behind.

## 2. Executive summary

Gate A PASS,94 focused tests and independent hand calculations; original contract verified without repairs. Gate B COMPLETE(SYNTHETIC),15 new M2 tests and single final220-test suite PASS. Implements only scheduled source quality, stock-specific historic proxy returns,20/60 M2, explicit floor certificate and canonical keys. Production/source/floor/shared-execution branches remain blocked. Stop here.

## 3. Research/protocol impact

No question/universe/target/horizon/split/confirmation/cost/portfolio/model/search change. Implements one already approved D4 channel under registered proxy lineage. No other15FT0 features, scaler fitting or production48×16 data. Five authorities/CURRENT_PROTOCOL/decision records unchanged. Market HOLD and seven historical blockers preserved. Zero40-budget neural pairs, no empirical label/feature-statistics fitting or confirmation access. Historical minute/R1 artifacts retain meaning; no relabeling.

## 4. Files created

- `src/lstm_data/m2.py`: Python reusable source-grid/M2 foundation; contracts below.
- `tests/test_m2.py`: 15 independent synthetic test cases, including parameterized coverage boundaries.
- `docs/track_a/P2_3A_M2_API.md`: Markdown public API/schema/causal limitation documentation.
- `reports/data_audit/p2_2a_r1_verify_p2_3a_2026-10-11_021237/package_report.md`: bounded Markdown gate verdict, result/resource/blocker summary.
- `reports/data_audit/p2_2a_r1_verify_p2_3a_2026-10-11_021237/checks.json`: schema-valid JSON evidence and exact hash/integration/resource inventory.
- `reports/data_audit/p2_2a_r1_verify_p2_3a_2026-10-11_021237/trace_examples.md`: four hand-checkable synthetic examples.
- `reports/data_audit/p2_2a_r1_verify_p2_3a_2026-10-11_021237/human_review_card.md`: six actual code/test/Git review pointers.
- `reports/codex_sessions/2026-10-11_021237_feat-track-a-data-intake_r1-verify-p2-3a-m2.md`: mandatory17-section handoff report.

## 5. Files modified

`reports/audit/track_a_events.jsonl`: one non-clearing audit, G3 BLOCKED, Gate A verified and Gate B synthetic completion evidence. Prior22events exact byte prefix;23events afterwards. Old blockers neither removed nor superseded. No existing code/test/config/authority/README modified.

## 6. Files deleted, renamed, or moved

None.

## 7. Critical functions, classes, variables, and config keys

New reused interfaces are in `src/lstm_data/m2.py`; exact signatures/fields/invariants in API document.

- `ScheduledCalendar(start,end)` / `ScheduledStep`: reusable XNYS metadata and exact full-hour step keys; no source loader or synthetic overnight rows.
- `scheduled_window(calendar,session,origin)`: immutable tuple of48 calendar slots ending at valid origin; insufficient history is explicit.
- `window_quality(calendar,steps,rows,*,test_scenario=False)`: five×48 IDs/mask/reasons, source interval and step-availability checks; no future outcome argument; full_ft0_eligible remainsFalse.
- `historical_return(plan,symbol,rows,actions,*,test_scenario=False)` / `HistoricalReturn`: one stock's split-aware log return from accepted exact R1 refs; scheduled-exit/source maturity, source/action/version hashes, no TG0 or five-peer label filter. Direct records are asserted metadata, not authenticated evidence.
- `ReturnIndex(records)`: keyed lookup; rejects duplicate or minute-mode records.
- `M2FloorCertificate`: validates supplied positive training p05 assertion, permitted prefix/phase/unique keys and evidence; no fitting or empirical verification. Supports original INNER_TRAIN/REFIT phase names.
- `evaluate_m2(calendar,index,symbol,step,origin,floor=None,*,test_scenario=False)` / `M2Result`: last60 scheduled earlier structurally eligible same-origin sessions; meanlast20/RMSlast60 on valid mature returns,19/20,57/60,max2 consecutive missing. Stable RMS arithmetic avoids direct-square overflow; zero RMS uses explicit certificate; no floor ->FLOOR_UNVERIFIED. Preserves session/count/reason/reference traces. As-of guard rejects future floor certificate.
- `canonical_m2_keys(results)`: unique stock/session/origin identities; deduplicate identical value/provenance, reject conflicts;50/50 total origin weights for one future pooled scaler. No fitting.
- `M2_VERSION="M2:HOURLY_CLOSE_PROXY:v1"`; execution binds existing COMPLETED_HOURLY_CLOSE_PROXY:v1. Existing R1 floor/label tags remain unchanged; no automatic migration. No new config/CLI/dependencies or side effects in calculator calls.

## 8. Data/schema/provenance changes

New in-memory scheduled steps, source-quality masks, per-stock return references, floor assertions and M2 results. UTC aware period/availability clocks; XNYS full hours only, terminalstub separate; original sessions/origins retained. No row skipping/ffill/interpolation. Raw reference price basis with explicit entry share epoch; accepted R1 split factors over(entry CLOSE,exit CLOSE], action scope cutoff→scheduledexit. No dividend cash in M2. Action/publication facts remain caller evidence, not independently certified. Source/action hashes include current record value/maturity and versions. Previous structurally ineligible early-close sessions excluded by approved clock; missing eligible outcomes remain scheduled missing cells. No raw/source files written or copied; prior source IDs/checksums reused, no raw rehash. Synthetic opt-in required; unknown availability cannot contribute. Old M2/scalers must be rebuilt, not renamed.

## 9. Dependency/environment changes

None. README setup remains authoritative. No secrets/new variables. Pathlib-relative artifact paths; private helpers are local orchestration, not dependencies.

## 10. Commands and tests run

- Read actual AGENTS, five located authorities' relevant sections, both decision records, API/checks/review cards and latest R1/CA/shared session reports; inspect Git branch/SHA/staged/unstaged/untracked state. `git fetch --all --prune` succeeded; no pull/integration/branch switch.
- `.venv/bin/python -B -m pytest tests/test_hourly_proxy.py tests/test_labels.py tests/test_clocks.py tests/test_corporate_actions.py -q`:94passed7.52s (Gate A). No full suite in A.
- Independent two-origin synthetic arithmetic: exact cutoffs,issue+2min,event+3min,240min and five log returns; observed14:30 does not mature14:33 label. Prior R1 check schemas and file hashes verified.
- `.venv/bin/python -B -m pytest tests/test_m2.py tests/test_hourly_proxy.py -q`: first1failed/39passed28.48s. New test incorrectly expected same-session return to be a missing queued item; actual policy excludes session. Corrected assertion only; rerun40passed34.45s. No R1 defect/fix.
- Inspection tightened new floor provenance to original REFIT name and ET confirmation boundary, unique observation IDs, hash-bound current record fields and canonical conflicts. `.venv/bin/python -B -m pytest tests/test_m2.py -q`:15passed26.02s.
- Added final invalid-plan/NaT/naive guard to new factory/tests; `.venv/bin/python -B -m pytest tests/test_m2.py::test_split_lineage_and_unsupported_epoch -q`:1passed1.44s.
- `.venv/bin/ruff format src/lstm_data/m2.py tests/test_m2.py` and focused Ruff fixes/checks: PASS.
- One final `.venv/bin/python -B -m pytest -q`:**220passed59.65s**.
- One final `.venv/bin/ruff check src tests`:all checks passed.
- `git diff --check`:PASS; final diff/status review and preservation/event/schema/link checks performed before handoff.
- No provider request/source-price scan. Integration includes inherited optional bounded116-action metadata fixture. Historical205result remains prior evidence only.

## 11. Experiment/results summary

No research/model fit,seed,IC,P&L or confirmation outcomes. Synthetic examples only: M2(.001…060)=.0505/.035073731861=1.439823974248;19/20 lastmissing gives1.449427589131. Missing/late/unknown future return never changes earlier input/window eligibility; R1 C01 tests preserved. All result readinessFalse; source/time/floor metadata assertions do not pass scientific G2/G3.

## 12. Reproduction instructions

README environment: `python -m venv .venv`, activate; `python -m pip install -e '.[dev]'`. No source data/secrets needed for focused M2/R1: `python -m pytest tests/test_m2.py tests/test_hourly_proxy.py -q` (40cases). Full `python -m pytest -q` (220observed); inherited CA optional metadata fixture as documented previously. `ruff check src tests`. API/trace examples describe constructors and explicit synthetic opt-in. No need for private helper/attachments.

## 13. Git / collaboration status

HEAD/branch unchanged, staged-entry hash unchanged. Fetch succeeded,1ahead/0behind; no auto integration/staging/commit/push/PR/stash/reset/branch change. Baseline status:

```text
 M reports/audit/track_a_events.jsonl
?? docs/track_a/P2_2A_R1_Hourly_Close_Proxy_API.md
?? reports/codex_sessions/2026-10-11_011815_feat-track-a-data-intake_p1-ca-accounting.md
?? reports/codex_sessions/2026-10-11_014652_feat-track-a-data-intake_p2-2a-r1-proxy.md
?? reports/data_audit/p1_ca_2026-10-11_011815/accounting_examples.md
?? reports/data_audit/p1_ca_2026-10-11_011815/action_reconciliation.json
?? reports/data_audit/p1_ca_2026-10-11_011815/checks.json
?? reports/data_audit/p1_ca_2026-10-11_011815/human_review_card.md
?? reports/data_audit/p1_ca_2026-10-11_011815/package_report.md
?? reports/data_audit/p1_ca_2026-10-11_011815/preservation.json
?? reports/data_audit/p2_2a_r1_2026-10-11_014652/checks.json
?? reports/data_audit/p2_2a_r1_2026-10-11_014652/human_review_card.md
?? reports/data_audit/p2_2a_r1_2026-10-11_014652/package_report.md
?? reports/data_audit/p2_2a_r1_2026-10-11_014652/preservation.json
?? reports/data_audit/p2_2a_r1_2026-10-11_014652/proxy_trace_examples.md
?? src/lstm_data/corporate_actions.py
?? src/lstm_data/hourly_proxy.py
?? tests/test_corporate_actions.py
?? tests/test_hourly_proxy.py
```

Dependency-correct proposed human staging manifest (not executed; existing tracked decisions/authority files excluded):

```text
docs/track_a/P2_2A_R1_Hourly_Close_Proxy_API.md
docs/track_a/P2_3A_M2_API.md
reports/audit/track_a_events.jsonl
reports/codex_sessions/2026-10-11_011815_feat-track-a-data-intake_p1-ca-accounting.md
reports/codex_sessions/2026-10-11_014652_feat-track-a-data-intake_p2-2a-r1-proxy.md
reports/codex_sessions/2026-10-11_021237_feat-track-a-data-intake_r1-verify-p2-3a-m2.md
reports/data_audit/p1_ca_2026-10-11_011815/accounting_examples.md
reports/data_audit/p1_ca_2026-10-11_011815/action_reconciliation.json
reports/data_audit/p1_ca_2026-10-11_011815/checks.json
reports/data_audit/p1_ca_2026-10-11_011815/human_review_card.md
reports/data_audit/p1_ca_2026-10-11_011815/package_report.md
reports/data_audit/p1_ca_2026-10-11_011815/preservation.json
reports/data_audit/p2_2a_r1_2026-10-11_014652/checks.json
reports/data_audit/p2_2a_r1_2026-10-11_014652/human_review_card.md
reports/data_audit/p2_2a_r1_2026-10-11_014652/package_report.md
reports/data_audit/p2_2a_r1_2026-10-11_014652/preservation.json
reports/data_audit/p2_2a_r1_2026-10-11_014652/proxy_trace_examples.md
reports/data_audit/p2_2a_r1_verify_p2_3a_2026-10-11_021237/checks.json
reports/data_audit/p2_2a_r1_verify_p2_3a_2026-10-11_021237/human_review_card.md
reports/data_audit/p2_2a_r1_verify_p2_3a_2026-10-11_021237/package_report.md
reports/data_audit/p2_2a_r1_verify_p2_3a_2026-10-11_021237/trace_examples.md
src/lstm_data/corporate_actions.py
src/lstm_data/hourly_proxy.py
src/lstm_data/m2.py
tests/test_corporate_actions.py
tests/test_hourly_proxy.py
tests/test_m2.py
```

Ledger contains uncommitted CA,R1,and this package rows referencing untracked artifacts. Do not stage ledger alone. Review inherited CA and R1 packages with this package, then stage exact manifest coherently, or have humans create dependency-ordered commits with correctly scoped ledger history. Agent did not rewrite/split ledger. Reinspect any newly arriving teammate work before authorized integration; never bulk discard or stage it. Suggested combined subject after review: `feat: add corporate-action and proxy M2 foundations`; fetch before eventual normal push/PR.

## 14. Known issues, risks, and limitations

No known failing tests. SOURCE_CLOCK_BLOCKED/FLOOR_UNVERIFIED production branch: no actual historical publication/action evidence or empirical floor certificate/population. DOCUMENTED is assertion; synthetic PASS not certified source timing. Floor-certificate as-of guard is a narrow request-level contract; later batch fit/application to older training windows not implemented. Within-session late publication causing canonical value/provenance changes fails closed rather than inventing freeze/copy policy. No complete FT0,OHLCV adequacy/retention,market features or scientific G3 PASS. Raw source unchanged by no writes, without rehash claim. Scheduled price proxies not genuine fills. Shared proxy approval remains pending independently of240min agreement. No final clean-machine rehearsal.

## 15. Decisions requiring human or teammate review

Review Gate A evidence and five M2 interfaces/constraints. Independently certify publication/action provenance and review training floor/population before production; no floor fitting authorized here. If session-locked canonical conflicts occur, approve precise causal handling rather than retrospective copying. Shared-execution/source approvals remain separate. Approval required for further P2.3B/P2.4/P3; no automatic nextpackage. Dependency-aware Git review required before commit.

## 16. Next recommended steps

1. Review package/checks/trace/card/API and inherited CA/R1 together.
2. Safely integrate reviewed dependencies through explicit human Git action.
3. Separately scope source/floor/batch application conventions if production M2 desired. Stop after this authorized subpackage.

## 17. Artifact inventory

8new code/test/Markdown/JSON files intended tracked after review, currently untracked; ledger tracked but modified. Inherited18new files untouched. Protected hashes/integration manifest/byte growth in checks.json. No plots/checkpoints/datasets/model caches. Measured elapsed since Gate A baseline694.2s (excludes initial inspection); final source-free metadata/index tests in this package. Private /tmp baseline/report helpers intentionally local; no committed dependency. Raw data untouched; zero acquisitions/fits.
