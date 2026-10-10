# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-10, approximately 04:40–05:05 America/New_York.
- Contributor / session: Codex; no delegated agents.
- Task requested: Track A / Task 01 course USA500 intake, historical SIP feasibility,
  auditable shared market-data infrastructure. Data layer only.
- Starting branch: `main`; working branch: `feat/track-a-data-intake`.
- Starting commit: `d335de9528092852b3049687f53fbfaf007812d1`.
- Ending commit: none created; HEAD remains the starting commit.
- Working tree at start: clean tracked tree; original ignored course CSV already present.
- Working tree at end: two tracked files modified and new implementation/config/test/
  documentation/report files untracked, all intentionally left for review.
- Related issue/PR: none. No commit or push authorized/performed.

## 2. Executive summary

Implemented an installable data-only package with source audit, small SIP pilot,
gated bulk acquisition skeleton, stock QA and audit-only causal alignment commands.
All commands have dry runs requiring neither credentials nor network/writes.
Audited all 29,510 course observations, preserved original bytes and recorded provenance.
The final timestamp is July 1, 2025 00:00 New York, beyond the named end date.

The live pilot command produced a useful blocked report because credentials were
absent. No HTTP request or stock download occurred. Native-hour acquisition is
intentionally blocked where session anchoring/closing stubs cannot be established;
30Min acquisition/reaggregation is a proposed next controlled change, not implemented.
50 offline tests, Ruff, compilation, source CLI smoke and dependency checks passed.

## 3. Research/protocol impact

- Research question: unchanged; infrastructure supports the original comparison.
- Target/horizon, feature set, splits/validation, trading/backtest, search space,
  seed policy and final-test protocol: untouched. No experiments/model results.
- Universe: original five provisional candidates retained; sector labels are coarse
  metadata and not verified historical sector vintages. No stock selected/replaced.
- Data dates: original 2020-07-01 through 2025-06-30 in New York, not a rolling window.
- Feed/resolution/adjustment: explicit SIP / native 1Hour / split are provisional,
  guarded by pilot evidence and approval. No alternate feed or resolution activated.
- Researcher follow-up: **"assume close for now"** for course USA500. Config explicitly
  records provisional timestamp-as-close approval dated 2026-10-10. Provider timestamp
  semantics remain unknown; alignment also exposes a +60-minute sensitivity scenario.
  Neither stock alignment scenario has run on actual stock data yet.
- Frozen specification documents requested by the prompt were absent:
  `Shared_Project_Specification.md` and
  `Track_A_Architecture_Experiment_Roadmap_First_Pass_FROZEN_v1.0.md`.
  No contents were invented. Root AGENTS.md was read and preserved; no nested rules
  or previous session reports existed. No research-design contradiction was found.

## 4. Files created

| Path | Purpose / type / key assumptions |
|---|---|
| `pyproject.toml` | Authoritative constrained dependencies, editable package/CLI, pytest and Ruff configuration. Python 3.11–3.14; verified here on 3.14 only. |
| `configs/track_a_data.json` | Small JSON config: candidates, fixed dates, SIP/hour/split choices, calendar, paths, retry/page budgets, researcher assumption. No credentials. |
| `data/README.md` | Source catalog, schema, provenance, setup/gate/resume conventions, issuer/API references, safe recovery limits. |
| `src/lstm_data/__init__.py` | Package marker, no model/trading functionality. |
| `src/lstm_data/config.py` | Portable config validation, fingerprints, source hashing, atomic create-only files. Hard-link publishing assumes supported local filesystem. |
| `src/lstm_data/validation.py` | Offset-aware UTC parsing, OHLCV schema/defect counts; rejects bad required rows without repair. |
| `src/lstm_data/calendar.py` | Historical XNYS schedules, desired session windows/stubs and native-hour timing/coverage QA. One-day/holiday queries use padded calendar construction. |
| `src/lstm_data/course.py` | Full byte-preserving CSV audit, gap/time tables, representative days and compact manifest/report generation. |
| `src/lstm_data/alpaca.py` | Fixed-host market-data GET client, explicit SIP/adjustment, all-page traversal, pacing, bounded retry and redacted errors/events. |
| `src/lstm_data/alignment.py` | Backward as-of comparisons of candidate availability, stale/unmatched counts; no future available row or final feature join. |
| `src/lstm_data/store.py` | Monthly parameter-hashed canonical Parquet/manifests, verification/resumption, writer lock, approval gate and acquisition skeleton. |
| `src/lstm_data/pilot.py` | Seven small historical access/timing/split probes, compact safe success/blocked reports; small samples only if fetched. |
| `src/lstm_data/cli.py` | Five installed commands, dry run, runtime/version metadata, explicit optional local .env. |
| `tests/conftest.py` | Temporary-path config and tiny mock-bar fixtures. |
| `tests/test_validation_course.py` | UTC/naive/DST parsing, duplicate/OHLC/nonfinite/null checks, source immutability, trailing date and atomic no-overwrite tests. |
| `tests/test_calendar_alignment.py` | DST/early close/holiday grids, refusal to shift native bars or invent stubs, causal as-of and stale-weekend tests. |
| `tests/test_alpaca.py` | Explicit policy, cross-symbol pagination, access failures, 429/5xx bounded retry, no fallback, optional fields and safe-event tests. |
| `tests/test_store_cli.py` | Parameter/date chunking, typed store roundtrip, checksum/resume/interruption/approval protections, missing credentials, config and all-command dry runs. |
| `reports/data_audit/task01_course/course_audit.md` | Actual source audit, representative-day/gap/hour tables. Its initial pending close-approval statement is superseded by task01_decisions.md. |
| `reports/data_audit/task01_course/course_manifest.json` | Small byte checksum, schema, ranges, distribution and provenance catalog; no full source rows copied. |
| `reports/data_audit/task01_course/runtime.json` | Actual Python/package versions, SHA, config fingerprint. Added after researcher assumption entered config. |
| `reports/data_audit/task01_sip_pilot/sip_pilot.json` | Requested probes, missing-credential diagnostic, false/unmeasured gates, zero events/stock bytes. |
| `reports/data_audit/task01_sip_pilot/sip_pilot.md` | Human-readable blocked pilot and proposed resolution alternative. |
| `reports/data_audit/task01_sip_pilot/runtime.json` | Pilot execution environment/SHA/config fingerprint. |
| `reports/data_audit/task01_download_plan.json` | Initial network-free request/size plan. Preserved; theoretical globally-packed page count superseded by v2. |
| `reports/data_audit/task01_download_plan_v2.json` | Corrected plan removing global packed-page count; 60 monthly initial calls/size estimates unchanged. |
| `reports/data_audit/task01_decisions.md` | Actual coverage table, user close-assumption follow-up, storage bounds, conditional next steps. |
| This session report | Mandatory handoff/audit; tracked-intent Markdown, currently untracked. |

## 5. Files modified

- `.env.example`: standard `APCA_API_KEY_ID` / `APCA_API_SECRET_KEY` placeholders,
  safe market-data context, compatibility note. Existing legacy names remain supported.
- `README.md`: authoritative setup, commands, gate behavior, explicit dotenv loading,
  reproducibility/portability assumptions and report links. Original project description retained.
- `.gitignore` was inspected and needs no change: original rules already protect raw,
  interim/processed data, environments, secrets and logs. No purposely tracked document ignored.

## 6. Files deleted, renamed, or moved

None. Course filename and original data location are unchanged. No raw edits, data
deletions, Git resets, stashes, merges, rebases or history rewrites.

## 7. Critical functions, classes, variables, and config keys

| Interface | Inputs → outputs / effects / invariants / callers |
|---|---|
| `config.load_config(path: Path) -> dict` | Config → validated data choices, fingerprint and resolved paths. No writes/network. Paths relative to the config project's root; CLI/tests use it. Refuses IEX, unsupported resolution and machine paths. |
| `config.digest(path: Path) -> str`, `atomic_new(path: Path, data: bytes) -> None` | Read-only streaming SHA-256; complete create-if-absent file publishing. Never replaces source/existing output. Called by source/store/reports. |
| `validation.parse_utc(values: Series) -> Series` | Offset-aware timestamps → UTC; naive/missing/unparseable rejected. Used by `normalize(frame, stocks=False)`; required numerical schema validated, no coercion/drop/dedup repair. |
| `validation.defects(frame, stocks=False) -> dict`, `require_valid(...) -> None` | Required schema/key/OHLCV defects → counts or explicit failure. Zero/fractional volume is diagnosed; optional trade_count/VWAP nulls do not invalidate required rows. |
| `calendar.schedule(start, end) -> DataFrame`, `session_grid(open_time, close_time) -> list[dict]` | Real XNYS UTC schedules and desired anchored hours with flagged stubs. DST/closures respected, no synthetic price filling. |
| `calendar.stock_qa(frame, symbols, start, end) -> dict` | Source observations → symbol ranges, coverage, per-day starts/missing/extra/overlap lists, jump candidates and conservative native timing gate. Never relabels/truncates aggregates. |
| `course.audit_course(path, provider, start, end) -> (DataFrame, dict)` | Original course bytes → typed in-memory observations and audit, including full-file bounds beyond named period. Before/after hashes ensure unchanged source. Called by source CLI/alignment. |
| `alpaca.credentials() -> tuple[str, str]` | Standard environment names or compatible aliases → secret pair, never logged. `.env` optional and explicit at CLI only. |
| `alpaca.request_params(cfg, symbols, start, end) -> dict` | Explicit SIP/hour/adjustment/asof/currency/date/limit choices; no provider defaults. Pilot/store callers. |
| `alpaca.HistoricalClient.bars(params) -> DataFrame` | Fully paginated fixed-host read-only GET → validated typed native bars. Optional trade_count/VWAP retained; required OHLCV/time/symbol violations fail. Safe events exclude credentials/tokens/body. Bounded 429/5xx/transport retries; no entitlement retry/fallback. |
| `store.monthly_requests(cfg) -> list[dict]`, `plan(cfg) -> dict` | Fixed New York dates → disjoint inclusive monthly requests and no-network size plan. No writes/secrets needed. |
| `store.save_chunk(store, frame, params, events, cfg) -> dict`, `read_verified(path, manifest_path, params) -> DataFrame` | New compressed canonical chunk/manifest, or byte/parameter/schema-verified resume read. Provenance ID attached once; never overwrite/dedup old files. Orphan pair requires review. |
| `store.check_approval(cfg, approval_path) -> dict`, `acquire(cfg, client, approval_path) -> list[dict]` | Matching successful pilot hash/config plus explicit human adjustment/hour approval → guarded acquisition/resume. Exclusive store lock; conflicting same-month parameters, partial universe or failed chunk timing stop before publication. |
| `store.load_store(cfg) -> DataFrame` | Matching verified chunks → single in-memory panel. Missing store fails clearly. Does not create dataset copies. |
| `pilot.pilot_requests(cfg) -> list[dict]`, `run_pilot(cfg, output, client=None) -> dict` | Seven small windows → all-page evidence/QA, optional tiny ignored Parquet samples and safe report even when access missing. Never bulk acquisition. |
| `alignment.asof_diagnostic(stocks, course, *, index_delay_minutes, stock_delay_minutes=60, max_age_minutes=90) -> (DataFrame, dict)` | Explicit candidate delays → backward matches, age/stale/unmatched metrics. Future availability forbidden; delayed metadata is an audit hypothesis, no features/targets. |
| `cli.main(argv=None) -> int` | CLI → five workflows, new report directories and runtime snapshots. Dry runs have no network/writes. Exit 2 for missing credentials/access/gate failure, exit 0 for completed audit/dry run. |

Important config keys: `symbols`, `start_date`, `end_date`, `feed`, `timeframe`,
`adjustment`, `asof`, `currency`, `calendar`, `timezone`, `session_policy`,
`course_timestamp_semantics`, `course_availability_assumption`, source/store/report
paths, monthly chunks, page and bounded retry/rate limits. Native 1Hour/split are
explicit provisional values; unsupported `30Min` config changes fail deliberately.

## 8. Data/schema/provenance changes

- Source course CSV unchanged: 2,083,715 bytes; 29,510 rows;
  SHA-256 `ba78d6bf933f0aca4dfcdedb69454d19aa29bfed84481b6ba1bcccdaf7b1634a`.
- Full-file UTC bounds: 2020-07-01 04:00 through 2025-07-01 04:00.
  Last local timestamp: 2025-07-01 00:00 EDT. One row outside named local dates.
- No required nulls, duplicates, ordering defects, nonfinite OHLCV, invalid OHLC,
  nonpositive prices or negative volume. Fractional volume: 29,508 rows; zero volume: 0.
- 7,502 timestamps inside XNYS RTH; 22,008 outside. These classify timestamps,
  not verified intervals/availability. 1,542 Sunday observations; UTC offsets show DST.
- Stock schema described in data/README.md; timezone-aware UTC with immutable
  native bar timestamps, explicit feed/adjustment/source_timeframe/provenance.
  All provider pages required before checkpointing; no forward-fill.
- Stock volume/prices will be retrospectively split-adjusted when approved; dividends
  unadjusted. Corporate-action dataset, historical sector vintages, source-calendar
  semantics and actual common overlap remain unverified.
- Actual acquired coverage/storage: no stocks; no pilot Parquet samples; zero stock bytes.
  Original course source is the only market dataset touched (read-only).
- No migration/rebuild needed. Other machine must supply original course bytes and,
  for live acquisition, its own securely configured market-data credentials.

## 9. Dependency/environment changes

Created ignored local `.venv`; authoritative constrained dependencies in pyproject.toml.
Added NumPy/Pandas for typed/audit/time joins, PyArrow for compressed timezone-preserving
Parquet, exchange-calendars for historical holiday/DST/early-close correctness,
Requests for small read-only REST calls and python-dotenv for explicit ignored local
secrets. The scaffold had no existing dependencies providing these capabilities.
Pytest and Ruff are development extras. No model/deep-learning dependencies added.

Actual versions: Python 3.14.6; NumPy 2.5.3; Pandas 3.0.6; PyArrow 23.0.1;
exchange-calendars 4.13.2; Requests 2.34.2; python-dotenv 1.2.4;
pytest 9.1.1; Ruff 0.17.0. runtime.json captures executed data dependencies.
Ranges, not a cross-platform lock, are authoritative; other platform/Python versions
were not tested in this task. Direct credentials use standard names with legacy aliases.
No actual local `.env` existed, was created, or was read.

## 10. Commands and tests run

- Read root AGENTS.md, repository files/tree/status and ignored course location;
  no older relevant reports available.
- `git status --short --branch`, `git branch --show-current`, `git rev-parse HEAD`,
  `git remote -v`: clean main at recorded SHA, origin configured.
- `git fetch --all --prune`: first sandbox attempt could not write FETCH_HEAD;
  approved escalated retry succeeded. No remote changes. `git rev-list --left-right
  --count HEAD...origin/main`: `0 0` at start and final verification.
- `git switch -c feat/track-a-data-intake`: approved branch creation; no content/history changes.
- `python3 -m venv .venv`; `.venv/bin/python -m pip install -e '.[dev]'`: succeeded.
  Package imports and installed `lstm-data` command exercised.
- Full source audit via `audit_course`/`save_course_audit`: actual output stored under
  reports/data_audit/task01_course; original checksum rechecked afterward, unchanged.
- `.venv/bin/lstm-data sip-pilot --output reports/data_audit/task01_sip_pilot`:
  expected exit 2, missing credentials; no HTTP calls, provider errors/retries or downloads.
- `.venv/bin/lstm-data --help`: five useful subcommands shown.
- `.venv/bin/lstm-data source-audit --output /private/tmp/lstm_task01_source_smoke_20261010`:
  passed, exit 0. Temporary machine path is execution-only, not a code dependency.
- `.venv/bin/python -m pytest -q`: initial 32 pass / 3 failures exposed one-day
  calendar construction; fixed with padded calendar range and reran expanded suite.
  Final **50 passed in 3.29 seconds**. No existing project tests predated this task.
  Mock HTTP only; no secrets/integration access needed. All five CLI dry runs tested.
- `.venv/bin/ruff format src tests`; `.venv/bin/ruff check src tests`: formatting
  completed; initial line-length findings fixed; final lint **passed**.
- `.venv/bin/python -m compileall -q src`: passed.
- `.venv/bin/python -m pip check`: no broken requirements. Warning: system pip
  cache was not writable, so disabled; environment install/imports unaffected.
- `git diff --check`, tracked diff review, untracked code/config/report inspection,
  project-specific absolute-path/credential-URL scan: passed; no developer path in
  implementation/config/docs/data reports. No credential values logged.
- `git check-ignore` verified source CSV, .env and .venv protection. AGENTS.md and
  .gitignore were not modified. No large market files eligible for add.

## 11. Experiment/results summary

No empirical/model experiment ran; no predictive/trading metrics or final-test
conclusions. Actual work consists of data-quality audit and offline engineering tests.
SIP feasibility remains unmeasured, not passed/failed entitlement.
Initial estimates: 1,255 XNYS sessions, 150,600 native-hour rows at a conservative
24 hours per session-day, about 19.28 MB uncompressed at 128 bytes/row.
Proposed 30Min doubles those estimates to 301,200 rows / 38.55 MB.
60 monthly initial requests in either case; pages/retries may increase actual calls.
These are size plans, not actual data/storage measurements or exact provider bounds.

## 12. Reproduction instructions

From another clone's repository root, following README.md:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
ruff check src tests
lstm-data source-audit
lstm-data sip-pilot --dry-run
lstm-data download --dry-run
```

For source audit, supply the exact original course CSV at its documented relative
path and verify the recorded SHA-256. Without it source audit fails clearly; offline
unit tests still run on tiny synthetic fixtures. For small live SIP probes, populate
ignored `.env` locally or export credentials, then:

```bash
lstm-data --env-file .env sip-pilot
```

Inspect the new timestamped report directory. Missing credentials yields a blocked
report/exit 2. No implicit .env loading. Only after passing measured timing/access,
explicit approved convention and matching hashed approval evidence, the guarded
native acquisition/QA interfaces are:

```bash
lstm-data --env-file .env download --approval configs/local_bulk_approval.json
lstm-data stock-qa
lstm-data alignment --max-age-minutes 90
```

The native gate is expected to block unproven closing stubs on normal XNYS sessions;
these commands are not a claim bulk can presently run. The likely 30Min alternative
requires researcher approval, implementation and a fresh pilot. All data commands
have dry runs. Previously reported output directories are never overwritten.

## 13. Git / collaboration status

- Branch: `feat/track-a-data-intake`, created from synchronized main; no upstream yet.
- Commits created: none; no push/PR. Current HEAD equals origin/main, ahead/behind `0/0`.
- Fetched remote successfully at start. No pull/integration over dirty work.
- Modified tracked: `.env.example`, `README.md`.
- Untracked intentional: `pyproject.toml`, config, data/README.md, ten source modules,
  five test files, nine small data-audit artifacts including corrected plan, and this report.
  Exact files are inventoried above; raw CSV/environment/caches remain ignored.
- Likely conflict points: README.md, .env.example and future dependency/config/package setup.
- Recommended review workflow after human review/commit authorization:

```bash
git diff --check
git add .env.example README.md pyproject.toml configs/track_a_data.json data/README.md src/lstm_data tests reports/data_audit reports/codex_sessions/2026-10-10_050256_feat-track-a-data-intake_task01.md
git commit -m "Add guarded Track A data intake and source audits"
git fetch --all --prune
git push -u origin feat/track-a-data-intake
```

Inspect fetched main before pushing; do not discard collaborator work or force-push
if divergence appears. Use a PR with tests and unresolved data gates made explicit.
Do not add data/raw/, .env or .venv. Commands above were **not** executed.

## 14. Known issues, risks, and limitations

- No failing final tests. Live SIP access, provider timings, actual stock ranges/gaps,
  split/volume behavior and stock/index overlap are unverified because credentials absent.
- Native-hour bulk is a guarded skeleton, not a completed collection route; no
  native aggregate can establish a closing stub merely by changing its label.
- 30Min alternative not implemented/authorized. No 1-minute/other-asset/subscription work.
- Course close timestamps are a researcher assumption, not verified availability.
  Upstream provenance, calendar, volume meaning and publication latency remain unknown.
- Corporate-action and historical sector reference datasets not acquired; jump
  candidates are diagnostic, not confirmed event corrections.
- The final July 1 course row is preserved; no dataset overlap/window truncation finalized.
- Config directory convention is documented: config parent is configs/ under root.
- Atomic publish uses local hard links. Interrupted data/manifest pairs or orphaned
  writer lock stop for human review, not automatic deletion. Network filesystem and
  nonmacOS execution are not rehearsed here; paths/code are platform-neutral.
- Package ranges support portability, but exact cross-platform lock/rehearsal is not
  performed. Runtime snapshots record actual versions used. No final-submission rehearsal.
- Runtime SHA identifies the base commit; code is intentionally uncommitted. Review/
  commit this implementation before presenting it as a reproducible reported experiment.

## 15. Decisions requiring human or teammate review

1. Set market-data credentials locally, then inspect measured SIP pilot evidence.
   Do not paste credentials into chat; no paid subscription or IEX fallback authorized.
2. On native-hour mismatch/stub failure, approve a small 30Min SIP pilot and specific
   session-anchored aggregation implementation. Recommend this measured alternative;
   it doubles source-row estimates but avoids five-year minute history.
3. Before bulk, approve explicit split price/volume adjustment after reviewing vintage/
   dividend implications and corporate-action QA. No default adjustment is hidden.
4. Later research-design task: final trade clock, latency/staleness policy and index
   join. The provisional course timestamp-as-close assumption is already approved
   and must not be re-requested merely because the provider metadata is incomplete.
5. Review/authorize commit/PR separately. No permission to commit/push inferred.

## 16. Next recommended steps

1. Review the source audit and this report; preserve all local implementation work.
2. Populate local credential variables/.env; run the seven-window SIP pilot.
3. Use actual per-day timing evidence to make the resolution/adjustment decision.
   If native timing fails, implement only the approved 30Min alternative and tests,
   rerun the pilot, then review the new gate before bulk.
4. Acquire/resume the five-symbol canonical store only after a passing reviewed gate;
   run stock QA and causal alignment under the user-approved provisional close assumption.
5. Resolve data-quality/event/trade-clock questions in the later research design task.
   Do not begin target/model/trading implementation under this Task 01 authorization.

## 17. Artifact inventory

- Original USA500 CSV: ignored, researcher-provided, 2,083,715 bytes; byte-identical.
- Course Markdown audit, JSON manifest/runtime; pilot Markdown/JSON/runtime; initial
  and corrected dry-run plans; decisions note; this session report: small files intended
  for Git, currently untracked. Data reports were approximately 63 KB before this report.
- Temporary source CLI smoke reports: `/private/tmp/lstm_task01_source_smoke_20261010`,
  local verification only; not required by repository execution and not tracked.
- `.venv`, Python/Ruff/pytest caches: intentionally local/ignored.
- Stocks/pilot sample Parquet, model checkpoints, derived features/targets, plots,
  trading tables and training logs: none created. Representative time/gap evidence
  is provided as Markdown tables; no full data copies or secret-bearing logs.
