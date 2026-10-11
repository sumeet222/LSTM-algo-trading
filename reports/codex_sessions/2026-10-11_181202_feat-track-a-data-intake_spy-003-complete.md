# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-11T22:12:02.658567+00:00.
- Contributor/session: Codex / TA-MKT-SPY-003.
- Task: execute approved 900-attempt SPY archive, measured historical QA and canonical D7 handoff.
- Branch: feat/track-a-data-intake.
- Starting commit: 245fc64edd2e63422402eda83c72c0c87d51adc9.
- Ending commit: unchanged; no Git integration authorized.
- Working tree at start: clean, one commit ahead of upstream (human commit superseded prior dirty-state report).
- Working tree at end: five tracked files modified; additive config, two modules, two test modules, package evidence and this report untracked; zero staged.
- Related PR: none.

## 2. Executive summary

SPY_ENGINEERING_COMPLETE — HUMAN_REVIEW_REQUIRED; ACTIVATION_PENDING.
Acquired and verified all 11 immutable native partitions: 41,861 rows, including
17,197/17,197 expected RTH half-hours across 1,327 XNYS sessions. Canonical D7
adapter and both first-July warm-up windows pass engineering checks. Usage is
129/900 cumulative attempts (13 inherited, 114 native GETs, 2 metadata GETs);
zero new diagnostic GETs or failures. Complete SHA resumption was verified with
a transport mock that raises on every GET. Source publication and full action
vintage remain unverified, and all formal/scientific gates remain held.

## 3. Research/protocol impact

Approved operational change only: v3 900 cumulative / 32 successful response pages
per original fixed key / 3 lifetime attempts per page / 256 MiB. Source selection,
version, SIP/raw/30Min/as-of, original 11 keys and dates unchanged. SPY remains
an information ETF proxy, never a sixth stock or strategy holding. TG0, C01,
M2 20/60, horizon 240 minutes, originals/proxies, splits, FT0=16, D7=5, eventual
MC0=21, hidden width 32, seed/search policy and comparison definitions unchanged.
Frozen five governing documents and CURRENT_PROTOCOL were byte-preserved.
Confirmation rows were used solely for source integrity/coverage; no returns,
labels, predictions, model selection or performance analysis.

## 4. Files created

- configs/track_a_market_spy_v3.json: additive approved operational config; same source identity.
- src/lstm_data/spy_qa.py: offline full_source_qa, structural_history and canonical_integration CLI; no empirical fits.
- src/lstm_data/spy_actions.py: bounded existing corporate-action endpoint inspection, same durable budget; process-date follow-up for June 2025 event.
- tests/test_spy_policy_v3.py: 7 offline resource/history/identity/corruption/report-capacity guards.
- tests/test_spy_qa.py: 6 parametrized warm-up/missingness/lineage/metadata-hold cases.
- reports/data_audit/ta_mkt_spy_003_2026-10-11/: additive JSON/Markdown/test evidence, itemized below and artifact_inventory.
- This session report: technical and collaboration handoff.

Additive evidence files:

- reports/data_audit/ta_mkt_spy_003_2026-10-11/acquisition_plan_v3.json: Initial measured853 conservative cumulative envelope, fixed11 requests and zero replay (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/acquisition_progress.jsonl: Per-page and partition rolling-budget evidence, not a second attempt counter (jsonl).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/action_scope_reconciliation.json: 22 observed distributions; no certified split absence or original vintage claim (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/activation_proposal_v3.json: Proposal-only follow-up hash bindings; protected pointer remains untouched (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/archive_integrity_final.json: Final partition SHAs, native bounds, terminal and request-event hashes (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/archive_manifest.json: Initial verified11-partition archive proof at127 cumulative acquisition attempts (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/artifact_inventory.json: Package file paths/types/purposes/bytes and hashes; self-describing index (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/baseline.json: Starting clean Git state, protected file and stock hashes, journal proof and disk capacity (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/checks.json: Baseline278, final291 and focused26 test evidence, source/resume/disk/cache guard statuses (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/corporate_action_followup.json: June2025 ex-date record with July31 process date, one additional bounded query (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/corporate_action_scope.json: First bounded process-date query,21 distributions; unknown historical action certification (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/decision_compatibility_matrix_v3.json: Separate engineering/source/fitting/joint approval/gate/model statuses (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/diagnostics.json: 42-file basic Pyright/AST and separate researcher-reported editor refresh (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/focused_final.txt: Final26-case regression log after default-cache rejection (txt).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/human_review_card.md: Six intervention groups; engineering proposedPASS, independent scientific/activationHOLD (md).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/integration_manifest.json: Exact coherent future Git integration set with hashes, currently not staged (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/market_api_handoff.md: Public source/history/window signatures and next-package use under unresolved gates (md).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/market_source_integration.json: Actual canonical regular/DST/early-close D7 boundary, masked real MarketWindows (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/preservation.json: All protected files and60 stock pairs SHA unchanged; seven blockers and0/40 pairs (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/pytest.txt: Earlier290-case full suite log retained (txt).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/pytest_291.txt: Final291-case full suite log after pre-write guard (txt).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/pytest_final.txt: Earlier final290-case full suite log retained (txt).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/resource_authorization_v3.json: Researcher-conversation operational approval; explicitly unsigned, no scientific clearance (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/runtime.json: Environment/dependencies and acquisition/storage measurements; no new packages (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/source_qa.md: Concise measured QA with source coverage/scientific holds distinguished and primary citations (md).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/source_qa_calendar_retention.json: Additive holiday and research-origin retention numerators/denominators (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/source_qa_full_period.json: Measured coverage by calendar/session/year/quarter/month, warm-up and native training traces (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/storage_final.json: Measured canonical/report namespace bytes and256MiB bound; zero staging (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/synthetic_D7_regression.json: Existing approved synthetic48x5 numeric regression; no actual-data fitting (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/transport_budget_reconciliation.json: Original13 prefix and116 new attempt/result lineage; actual129, metadata included (json).
- reports/data_audit/ta_mkt_spy_003_2026-10-11/zero_get_resume.json: GET-that-raises proof of completed SHA resumption with journal129 unchanged (json).
- Ignored canonical store: 11 new Parquet/manifest pairs; journal appended, no alternate raw store.

## 5. Files modified

- src/lstm_data/market_source.py: validates/read-routes v3, persists strict per-page/fixed-key/global guards and sanitized receipts; acquire_partition forwards optional pre-publication disk callback. Aggregated evidence IDs qualify original request provenance by each constituent native timestamp, correcting repeated IDs across a partition. Raw request keys unchanged.
- src/lstm_data/spy_completion.py: policy-aware planning with explicit zero discarded-cache deduction, historical prefix verification, rolling progress and capacity guards, single-page response retention under v3, canonical terminal/hash proof.
- src/lstm_data/store.py: optional before_publish(byte_count) callback after serialization and before canonical file creation. Existing stock callers retain default behavior.
- README.md and data/README.md: current measured archive status, v3 CLI/reproduction, scientific holds and journal/data requirements.

## 6. Files deleted, renamed, or moved

None. No raw/source file replaced or repaired. No previous session/report rewritten.

## 7. Critical functions, classes, variables, and config keys

- MarketSource.load(path=DEFAULT_CONFIG): strict version 1/2/3 source/config validator. DEFAULT_CONFIG points to additive v3; original v1/v2 reads stable.
- AttemptBudget.get(url, **kwargs): pre-send fsynced unique attempt IDs, result receipts not double-counted, known fixed endpoint/params, cumulative 900 and lifetime page limits. Original nine legacy lines and next four receipts preserved. Legacy first bulk page and unknown continued token are conservatively reserved in retry guards; exact old token identities are not invented.
- verify_historical_journal(source, budget): original13 checksum, original9 prefix, sequential new attempt/result associations, expected journal hash against concurrent modifications. No reconstruction/reset in live executor.
- storage_guard(source, report, additional=0): measured canonical/report bytes plus required new bytes and free-space reserve, before receipt writes/publication; write_bounded_report also reserves exact JSON bytes before audit writes.
- RollingProgress: observed continuing-page density and exact calendar residual envelope; periodic and partition progress. Same canonical budget, not a second counter.
- acquisition_plan(..., cached_pages=0): credible original per-partition page bounds 15–27, sum280 ×3 +13 =853. No assumption that all 11 use32 pages; no former response bodies reused.
- save_chunk(..., *, before_publish=None): optional additive pre-write guard; original signature positional callers preserved.
- full_source_qa / canonical_integration / structural_history: canonical source-only QA and same existing market_features D7 interface, every historical step's own cutoff and previous-session lock.
- inspect_actions(..., late_process=False): at most two pages per bounded query, same journal/lock, no certified absence or publication claim.
- New policy keys: acquisition_policy_version=3, authorization_package=TA-MKT-SPY-003, operational-only authorization_basis; limits900/32/11/3/268435456. No external side effects other than approved GETs and immutable source/evidence writes.

## 8. Data/schema/provenance changes

ALPACA_SIP_SPY_RAW_30MIN_V1, USD, raw SIP SPY, 2020-03-19–2025-06-30 ET,
as-of2025-06-30. Original native schema/provenance IDs, fixed inclusive UTC bounds
and extended-session rows preserved. 11 partitions have terminal receipts/SHA,
unique keys, native min/max, events and source row lineage. Complete hours aggregate
on demand; actual terminal 30-minute stub supplies close, not a feature position.
Derived lineage now includes native timestamps. Publication always UNKNOWN/NaT;
retrieval and period_end do not become available_at. No migration of existing
stock or old course source. Two current process-date queries returned 22 cash
distributions; no observed split in those responses does not certify absence.
June2025 ex-date processes July31, demonstrating why process/effective dates differ.

## 9. Dependency/environment changes

No dependency, pins, interpreter, editor severity or setup-route changes.
Existing .venv, basic Pyright/Pylance stubs, pyproject authoritative setup used.
No new secrets/environment variables; local documented Alpaca aliases only.
Runtime versions are recorded in runtime.json. No private helper required at runtime.

## 10. Commands and tests run

- git status/branch/rev-parse/remote/log; git fetch --all --prune: PASS; ahead1/behind0, no divergence; no pull/merge.
- Baseline .venv/bin/python -m pytest -q: 278 passed in59.13s.
- Focused policy/source/QA batches: final 26 selected cases passed; full focused with market regressions ran during development. A journal-field name initially broke an old assertion; corrected without altering any old tests.
- .venv/bin/python -B -m pytest -q: final 291 passed in 72.49s (0:01:12) (earlier290 run75.56s). Exact final log: pytest_291.txt. Last cache guard was also covered by26 focused passing cases.
- .venv/bin/python scripts/check_python_types.py --pylance-dist <installed-extension>/dist: final42 owned files,0 errors,0 warnings, basic repository .venv. Transient new-code type errors were repaired; no suppression.
- .venv/bin/ruff check .: PASS.
- AST parse all42 owned Python files with Python3.11 syntax: PASS.
- git diff --check: PASS; full diff and protected hashes reviewed.
- .venv/bin/python -m lstm_data.spy_completion --env-file .env --report reports/data_audit/ta_mkt_spy_003_2026-10-11: PASS 11/11,114 new GETs,127 cumulative at archive completion.
- .venv/bin/python -m lstm_data.spy_actions --env-file .env --report reports/data_audit/ta_mkt_spy_003_2026-10-11 [then --late-process]: PASS1+1 metadata GET,129 cumulative.
- .venv/bin/python -m lstm_data.spy_qa --report reports/data_audit/ta_mkt_spy_003_2026-10-11: PASS actual canonical QA/adapter. Later offline calendar/retention additions measured separately.
- Mock transport zero-GET canonical resume: PASS, journal SHA and129 unchanged.
- Existing explicit synthetic certificates re-executed: 48×5,48 valid masks, exact U1–U5 regression output, research_ready false.
- CLI --help smoke: PASS.
- Researcher separately reports VS Code Problems refresh0 Python errors/warnings.
- Sandbox pyarrow CPU-information sysctl warnings during offline reads are informational; source/tests passed. Live GET commands used required technical network escalation, within already approved research scope.

## 11. Experiment/results summary

No model experiment, performance results or confirmation evaluation.
Source engineering only:1327 sessions,7935 complete hours,1327 genuine closes,
zero RTH missing bars/windows. Pure research raw retention2492/2492 possible
origins; full-horizon2620/2636 includes initial warm-up origins lacking48 prior
steps. Both first-July windows meet64 preceding close /60 hourly /48-position
requirements at each step. Scientific real causal eligibility remains zero.
Neural model pairs remain0/40; all seven blockers and G0–G4 remain held.

## 12. Reproduction instructions

Clone/setup with existing README pyproject commands; supply documented local SIP
credentials and canonical journal/data. Verify original13 prefix against SPY-002
proof before any further calls. Missing/tampered journal stops; no zeroed budget.
Use v3 spy_completion command above for complete SHA resumption.
Run spy_qa with a NEW report destination, and python -m pytest -q plus basic type
helper/Ruff. Only source QA and synthetic certificates execute; no empirical fit.
Completed chunks resume without GET; interrupted partial partition pages are not
durable and must be re-requested within lifetime/global/page guards.
Clean-machine final-submission rehearsal was not performed in this package.

## 13. Git / collaboration status

Branch feat/track-a-data-intake, HEAD 245fc64edd2e63422402eda83c72c0c87d51adc9 unchanged. Fetched upstream; ahead1/behind0.
No commits, staging, pushes, merges, stashes, rebase/reset or destructive operations.
Exact future-integration files are in integration_manifest.json. Include code,
tests, v3 config, docs, compact evidence and this session report together in a later
human-authorized commit. Exclude ignored raw data/.env; supply canonical data/journal
through documented research-data handling. Human RandomNotes and prior evidence
unchanged. Source adapter/orchestration and README are likely overlap points.
Suggested later title: Complete approved SPY archive and canonical D7 handoff.

## 14. Known issues, risks, and limitations

No failing tests or remaining Python diagnostics. Historical available_at and
source/action vintage unknown; no certified split absence, empirical floors/scalers,
formal shared/course activation or scientific gate clearance. Current action
process-date inventory is finite evidence, not full historical availability proof.
Original SPY001 second-page token/body IDs were not retained; conservative legacy
retry reservations preserve safety and uncertainty. Initial853 attempt estimate
was conservative planning, actual129 cumulative. Real vectors are masked/None
with PUBLICATION_UNKNOWN, not valid zeros. Machine-specific absolute paths are
used only for local checker discovery, not committed runtime/config paths.
No clean-clone portability rehearsal or downstream FT0/model admission here.

## 15. Decisions requiring human or teammate review

Operational900/32 approval is already granted and correctly registered.
Separately review historical publication/action evidence, formal joint/course
source approval, training certificate provenance and G0–G4. Authorize the next
P2.2/P2.3 package and Git integration separately. No need to approve another SPY
redownload for existing complete chunks. No signature or gate was fabricated.

## 16. Next recommended steps

1. Review human_review_card, measured QA, canonical native/D7 traces and matrix.
2. Reuse load_market_history → window_from_history in separately authorized
   next-stage work; retain unknown clocks/action holds and exact scheduled masks.
3. Resolve source/scientific approval and empirical training-only fits through their
   own packages; keep formal pointer proposal-only until explicitly authorized.
4. Integrate the manifest's coherent code/config/test/docs/evidence set only after
   separate human Git authorization; preserve journal and raw hashes.

## 17. Artifact inventory

- Additive package JSON/Markdown and test logs: untracked pending authorized integration;
  exact names/SHA in artifact_inventory.json. Includes approved policy,853 initial
  plan,129 receipt reconciliation, archive/final integrity/zero-GET proof, full source
  QA and calendar retention, action inventories, real D7 and synthetic regression,
  compatibility/activation proposals, diagnostics/checks/preservation/runtime and
  human/API handoffs.
- Ignored canonical SPY:11 Parquet/manifest pairs, 1780060 Parquet bytes,
  89575 manifest bytes, 103188 journal bytes,
  zero staging. One archive only; current store total 1972823 bytes.
- Existing ignored stock60 pairs: unchanged hashes/159008 rows. No copied stock store.
- No model/checkpoint/plot/performance artifacts. Source receipts redact credentials,
  headers and page tokens; .env remains local.
- Local temporary validation/build helpers are not runtime inputs or committed artifacts.
