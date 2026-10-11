# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-10 America/New_York; source predeclaration/preservation snapshot at20:11:04; UTC date2026-10-11.
- Contributor / session: Codex / Track A P1.2 course-source contract audit.
- Task requested: bounded local source/metadata, timestamp/as-of evidence and human-review stop; no production repair or next package.
- Branch: `feat/track-a-data-intake`.
- Starting/ending commit: `bf767746f6757c7e04a9abe86c45f043c906da31`; no commit created.
- Working tree at start: central ledger modified by P1.1; its report directory and session report untracked. Nothing staged. Upstream0ahead/0behind after fetch.
- Working tree at end: prior P1.1 work preserved; one additional ledger event and seven new P1.2 reports, uncommitted/untracked. Nothing staged.
- Related issue/PR: none created.
- Resource accounting: **461.004** seconds from source predeclaration snapshot to handoff (excludes earlier repository/document reads); **94314** persistent report bytes including this session and incremental ledger growth. Exact inventory in `preservation.json`.

## 2. Executive summary

Verified observable source facts: actual configured course file, schema and sampled OHLC, explicit UTC encoding, ordered/unique whole-hour labels, study date span, nearest raw rows on three predeclared dates. Reused prior source hash/QA without full numerical reprocessing. Independent upstream/instrument identity, hourly interval definition, daily close and historical availability remain UNKNOWN-BLOCKED. Prepared a six-question source-owner inquiry; no message sent.

All source-dependent market branches remain blocked; no USA500-based restriction added to independent stock-only work. Three synthetic cases separate period-end freshness from publication. F01 remains INVALID/unrepaired. Fifteen existing-schema checks and one non-clearing audit event were produced; seven previous blockers and zero fits remain. No application code change.

## 3. Research/protocol impact

Research question, target/horizon, universe, features, dates/splits, trading/costs, architecture/search budget and final-test protocol unchanged. Exact five-authority binding PASS, no pointer/config edits. No U1–U5, masks, lookback windows, labels, model or economics were constructed. The2025 day was original-source QA only, with no performance metric opened or calculated. Shared four-complete-hour versus240-RTH-minute convention remains unsigned. Provisional close interpretation preserved without treating it as historical publication evidence.

## 4. Files created

Package directory: `reports/data_audit/p1_2_2026-10-10_201104/`.

| File | Type / purpose / assumptions |
|---|---|
| `package_report.md` | Markdown: answer, boundary examples, synthetic predicates, decisions/dependencies. |
| `source_contract.md` | Markdown: 18 field classifications with exact local evidence; source-owner inquiry draft, not sent. |
| `human_review_card.md` | Markdown: five quick checks with real source/config/function line references. |
| `checks.json` | JSON:15 validated P0.2-schema checks, protocol/code/config/source identities and narrow dependencies. |
| `evidence.json` | JSON:18 original timestamp/OHLC samples, timestamp-only summaries, nearest-neighbor comparisons, inherited exceptional-date metadata and three clearly synthetic examples. No volume values or source re-export. |
| `preservation.json` | JSON: scoped protected-work checks, source stats, ledger prefix, validation/Git/duration/exact byte inventory. |

This mandatory session Markdown is the seventh new report. No production module/test, dataset, notebook, dependency or copied source collection created.

## 5. Files modified

`reports/audit/track_a_events.jsonl`: one additional `kind=audit`, `package=P1.2`, `status=BLOCKED` event, ID `p1.2-usa500-source-contract-2026-10-10-201104`. Existing P1.1-inclusive ledger bytes preserved as exact prefix; `blocks=[]`, `supersedes=[]`. Evidence of unknown course identity/publication, not approval, blocker clearance or fitting. All other pre-existing work untouched.

## 6. Files deleted, renamed, or moved

None.

## 7. Critical functions, classes, variables, and config keys

No interface changed. Inspected relevant existing paths:

- `course.audit_course(path, provider, start, end)` (`src/lstm_data/course.py:14`): existing whole-file hash/numeric audit, deliberately not rerun. Its prior manifest supplies provenance/QA evidence; neither configured provider text nor pandas normalization establishes identity.
- `validation.parse_utc` (`src/lstm_data/validation.py:11`): rejects naive timestamps; source offsets remained explicit.
- `calendar.schedule` / `session_grid` (`src/lstm_data/calendar.py:9` /`:22`): existing XNYS calendar and independent stock-hour/stub metadata. Reused schedule for timestamp classification only.
- `aggregation.aggregate_session_hours` (`src/lstm_data/aggregation.py:10`): stock30Min aggregator; not called on USA500. Its interval-end `available_at` remains a completed-bar assumption, not proven historical publication.
- `alignment.asof_diagnostic` (`src/lstm_data/alignment.py:10`): hypothetical availability at`:40`, availability-age bug at`:51`; unchanged. No real course alignment run.
- `audit.f01_fixture` (`src/lstm_data/audit.py:276`): reused fake2001 counterexample; production diagnostic accepts age60 although required period age120. No new redundant permanent fixture.
- `audit.protocol_check` / `make_check` / `validate_check` (`:121` /`:244` /`:217`): existing binding/schema. Code/config IDs inherited from P1.1 after checking unchanged tracked source/config and scoped protected hashes.
- `ledger.append_event` (`src/lstm_data/ledger.py:281`): existing non-clearing append, used after exact starting-ledger comparison to detect concurrent edits. No concurrent edit detected.

Ephemeral inspection tooling streamed timestamps once, parsed OHLC only for18 predeclared nearest rows and performed report checks. It is outside the repository and not a submission dependency; persisted selection/parameters/row locators support independent inspection/reproduction. No permanent helper introduced.

## 8. Data/schema/provenance changes

No original data/schema changed. Actual path: `data/raw/course/USA500.IDXUSD_1h_2020-07-01_to_2025-06-30_UTC.csv`. Prior raw SHA256 `ba78d6bf933f0aca4dfcdedb69454d19aa29bfed84481b6ba1bcccdaf7b1634a` retained as inherited evidence, not recomputed. Its Task01 manifest hash still matches P0.1. Current source has same size/stats as P1.1 and same29,510 count/date range. Metadata consistency is not new cryptographic raw validation or upstream identity proof.

Header:timestamp/open/high/low/close/volume. Native timestamps explicitly UTC, converted to ET in metadata only; actual aggregation timezone unknown. Three days fixed before OHLC:2020-07-08,2023-03-10,2025-06-03. Neighbors around09:30/10:30/11:30/15:30 and16:00 retain six original timestamp/OHLC records per day, physical CSV line locators and null documented period-start/end/availability. No volume values parsed/interpreted.

Timestamp-only scan:0duplicates/order defects; all labels on whole hours;7,502 labels inside XNYS RTH,22,008 outside,2,240 on non-XNYS dates. Source labels span2020-07-01 04:00 UTC–2025-07-01 04:00 UTC, including one label beyond the named final local date and no preformation history. Calendar classification is not actual source-interval classification. Latest-label distance at2,510 nominal stock cutoffs is30min for2,509/90min forone; no period freshness or retention inference. Existing exception/gap timestamps reused by reference/metadata. No manual correction, interpolation or manufactured stock bars/daily close.

## 9. Dependency/environment changes

None. Existing environment/README setup unchanged. No installs, credential/.env reads, brokerage/provider queries or market downloads. No web price/instrument fingerprint search: an official source-specific vendor/course description was not supplied. Local metadata cannot identify an instrument from numerical similarity.

## 10. Commands and tests run

- Repository-required `git status --short --branch`, `git branch --show-current`, `git rev-parse HEAD`, `git remote -v`, `git fetch --all --prune`: successful; branch0ahead/0behind, dirty P1.1 work preserved. No integration action.
- Scoped `rg`/file reads: root is the only applicable AGENTS found; protocol/source summaries, config, actual relevant loader/alignment/calendar paths and documented source provenance inspected. No unrelated models/performance artifacts opened.
- `.venv/bin/python -B /private/tmp/lstm_p1_2_inspect.py`: exit0; streaming timestamp-only scan,18 source OHLC samples and3 synthetic cases validated.1.787s tool wall time; no raw hash/full numerical scan/HTTP call.
- `.venv/bin/python -m pytest -q tests/test_evidence.py::test_f01_production_counterexample_is_invalid tests/test_evidence.py::test_real_pointer_and_p01_links tests/test_evidence.py::test_cannot_clear_or_narrow_blockers tests/test_evidence.py::test_external_blockers_and_confirmation_locked`: **5 passed in1.24s**. Existing hermetic tests only.
- `.venv/bin/python -B /private/tmp/lstm_p1_2_checks.py`: exit0;15 valid checks, single compliant ledger append,7 preserved blockers,0fits. Starting-ledger comparison passed.
- `.venv/bin/python -B /private/tmp/lstm_p1_2_finalize.py`: final offline schema/sample/synthetic/ledger/raw-stat/protected-work/byte inventory verification; PASS. No numerical feature computation.
- `git diff --check`: PASS; tracked ledger diff and final Git status reviewed.
- No full pytest/Ruff rerun: no production/test code changed. P0.2's94 tests and P1.1's22 tests are prior evidence only, not rerun results. No known failing tests/errors in this package.

## 11. Experiment/results summary

No experiment/model/training/forecast/backtest/confirmation metrics. G0–G2 remain BLOCKED; G3–G9 NOT_RUN;0/40 fits. Physical source sample/date-span results do not establish G1/G2/D7 approval. Market branches blocked narrowly; unrelated stock-only work retains its own independent stock-publication, formation, shared-clock and other prerequisites.

## 12. Reproduction instructions

Use existing README setup. Open the package contract/card/evidence/check files; these do not require credentials or network. The original course file is intentionally ignored; another machine needs that documented source file/reference from the course owner, not a public proxy. Inspect actual CSV line123/15929 for card examples, retaining source bytes. A timestamp-only CSV iteration with explicit UTC→ET conversion reproduces metadata; predeclared days/boundaries/selection are in evidence. Do not call the full original audit merely to inspect this package.

Run the exact focused pytest command above if desired; expect5passes. The first synthetic case is existing `audit.f01_fixture()`; others use hypothetical2001 dates and independent freshness/publication predicates. Nothing synthetic is source-contract evidence. Current package authorizes no automatic rerun, repair or subsequent source acquisition.

## 13. Git / collaboration status

Branch/HEAD unchanged; fetch successful; upstream0ahead/0behind. No stage/commit/push/merge/rebase/stash/cleanup/branch switch. Original P1.1 nine untracked files and its ledger event preserved exactly. Only previously tracked modification remains the central ledger, now with P1.1 and P1.2 appended rows relative to HEAD.

Precise proposed P1.2 Git manifest, requiring separate authorization: the six named package files in §4, this session report, and `reports/audit/track_a_events.jsonl`. Prior P1.1 report paths are excluded from this new artifact manifest. **The ledger's full diff also contains the uncommitted P1.1 event**: review/integrate P1.1 first or explicitly authorize the contiguous combined ledger diff; do not blindly stage the file as solely P1.2. Proposed focused title:`docs: record P1.2 USA500 source contract`. Recheck fetch/divergence before any separately authorized push/PR. The shared ledger is the likely concurrent-append conflict; never overwrite/drop another writer's history.

## 14. Known issues, risks, and limitations

Unknown vendor/instrument, historical source-hour labeling/completion, official daily close, publication/revision/vintage and compatible market calendar. Provisional “assume close” is not proof. File starts at formation without prior course history;48-step/full RMS/daily feature readiness uncomputed. Date span and nearest-label age cannot establish46/48 validity, historical eligibility or a causal join. F01 unchanged/INVALID; independent availability and freshness requirements remain separate. No new scientific blocker closure or empirical performance claim. Raw preservation relies on existing hash evidence plus current file stats/metadata, not rehashing all bytes. No permanent new code or dependencies to maintain.

## 15. Decisions requiring human or teammate review

Review the source-owner inquiry and request actual instrument/hour/day/publication/version/prehistory contract. Any fallback timing assumption, new source, source substitution, membership interpretation, F01 repair or shared clock amendment requires explicit human review/authorization. Review new evidence and exact Git manifest separately; no approval inferred from this package.

## 16. Next recommended steps

**One action:** have the instructor/source owner answer the six questions in `source_contract.md` and supply original documentation/metadata. Draft not sent. Choose later package/repair authorization after reviewing that response. P1.3 stock QA may be separately considered on its own prerequisites; P2.4 market-feature implementation remains blocked. No next package started.

**STOP AND AWAIT HUMAN REVIEW — NO AUTOMATIC NEXT PACKAGE.**

## 17. Artifact inventory

Six small package artifacts plus this session report: currently untracked, intended for scoped review/tracking. Central ledger: tracked, uncommitted P1.1/P1.2 events. Previous P1.1 and original Task01/P0.1/P0.2 artifacts: untouched. Original course/Alpaca/pilot sources: ignored/local, unchanged. No plot, model/checkpoint, dataset copy,48-step/window/per-seed panel or persistent cache created. Temporary inspection scripts/snapshots: outside repo, local-only; not committed or required for submission.
