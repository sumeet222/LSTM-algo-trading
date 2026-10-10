# P0.1 — Existing implementation review

**Audit only · 10 October 2026 · AWAITING HUMAN REVIEW — NO AUTOMATIC NEXT PACKAGE**

P0.1 inspection is complete. **Research preflight remains BLOCKED.** Task 01 provides reusable, tested intake infrastructure and intact canonical observations. It does not establish the minute execution, source publication, formation, feature or accounting prerequisites for fitting. One deterministic mismatch was found between the diagnostic freshness calculation and D2's required period-end age. No code or data was repaired.

Evidence: [checks](p0_1_checks.json), [coverage and blockers](p0_1_protocol_coverage.md), [eight inspection targets](p0_1_human_review_card.md), and the [mandatory session entry](../../codex_sessions/2026-10-10_190015_feat-track-a-data-intake_p0-1-review.md).

## Actual checkout and authority

Branch `feat/track-a-data-intake`, HEAD `92aecd1a382f93c1133f41b8ae2432bd9863ff70`, was clean at start. Repository-required `git fetch --all --prune` succeeded. HEAD matches `origin/feat/track-a-data-intake` (ahead/behind 0/0), and is two commits ahead of `origin/main`, with no divergence. `ccdd85a` committed Task 01; `92aecd1` added preparation documents. This supersedes the older handoff's *uncommitted/base-SHA/no-upstream* statements. No Git integration, staging, commit or push occurred here.

All five requested authority documents were located and read under `docs/track_a/`: shared specification v1.0; frozen roadmap v1.0; consolidated design v1.2; audit plan v1.1; implementation plan v1. Their full paths, declared versions and SHA-256 values are in the coverage report/checks. **Missing authoritative documents: zero.** Older reports' absent-document warnings describe the prior checkout, not this one. The consolidated record contains stale internal v1.1 wording; the audit plan's introduction references an earlier consolidated filename. Preserve them and use an explicit current-document pointer after review.

Proposed `CURRENT_PROTOCOL` manifest: ordered relative paths and exact hashes for these five documents, explicit precedence, references to the existing source approval and provisional USA500 assumption, plus pending shared sign-offs. This is a proposal only; no manifest or governance code was installed.

```text
.
├── AGENTS.md, README.md, pyproject.toml, .gitignore, .env.example
├── configs/                         intake config and dated approval
├── docs/track_a/                     five authoritative documents
├── src/lstm_data/                   11 data-only modules
├── tests/                           conftest + five test modules
├── data/README.md
│   ├── raw/course/                  original CSV, ignored
│   ├── raw/alpaca/track_a/           60 Parquet/manifest pairs, ignored
│   └── interim/alpaca_pilot/         small historical samples, ignored
└── reports/{data_audit,codex_sessions}/
```

Root AGENTS.md is the only repository instruction file found outside ignored environment/Git internals. No structured run/audit ledger or `CURRENT_PROTOCOL` file exists. The session-report archive exists; this audit adds a new entry without editing old entries.

## Task 01 reconciliation

| Property | P0.1 observation | Evidence scope |
|---|---|---|
| Source choices | SIP / 30Min / split / USD; original five names and fixed July 2020–June 2025 local dates | Actual config, all request manifests, `check_approval` succeeded offline |
| Approved amendment | Passing 30Min pilot hash matches dated bulk approval and config fingerprint | Preserve existing authorization; native 1Hour diagnostic failure is historical evidence |
| Canonical store | 60 expected pairs; 159,008 rows; 5,845,266 Parquet bytes; 581,833 manifest bytes | Streamed SHA-256, footer/schema, request/name/coverage metadata; no table loading |
| Per-stock rows | AAPL 39,528; JPM 32,898; JNJ 27,982; WMT 31,934; CAT 26,666 | Summed manifest coverage equals footer totals |
| Missing RTH constituents | 168 across 15 stock-session pairs; AAPL 0/JPM 36/JNJ 37/WMT 48/CAT 47 | Compact QA exceptions and 51 newer coverage manifests agree; nine legacy manifests legitimately lack optional QA |
| Incomplete derived windows | 98 recorded; omitted without manufactured OHLCV | Newer manifests and aggregation code; full derived panel not rebuilt |
| Prior complete-hour/stub panel | 43,692 outputs; native RTH 81,137 half-hours | Existing alignment/QA evidence, not a new full-panel computation |
| Course original | 29,510 data records; 2,083,715 bytes; original SHA unchanged | Streaming record count/hash; one source row handled at a time |
| Course last timestamp | 2025-07-01 00:00 ET, one local observation outside named dates | Original timestamp and course manifest agree; raw row retained |
| Approved 30Min pilot | 738 bars, 165 derived windows, 24 stubs, seven recorded HTTP 200s | Existing hashed pilot metadata, no requests repeated |

The documented full-source OHLCV/key audit has zero required defects. P0.1 verifies its evidence against unchanged chunk bytes and reruns schema tests; it **does not rerun all-row numerical or calendar QA**. Source hashes establish integrity of the stored observations, not vendor truth, availability vintages, licensing rights or corporate-action accuracy.

Ordinary/missing/early-close fixtures independently reproduced the aggregation: synthetic first pair OHLCV `(100,103,99,102,20)`, six complete hours plus a 30-minute stub; removing one half-hour omits that whole hour and emits a missing mask. The early-close fixture emits three hours plus a stub ending 13:00 ET. Existing DST tests passed. All printed prices in this package are synthetic.

## Findings by severity and dependency

**Deterministic conflict — F01:** `alignment.py:51` measures age from `candidate_available_at`. Under the approved provisional close interpretation with a +60-minute publication sensitivity, a market period ending 13:00Z, available 14:00Z, matched at 15:00Z is reported as 60 minutes old and usable. D2 period-end age is 120 minutes, so it must be stale at the 90-minute bound. The current unit suite passes because it tests the diagnostic contract, not this D2 distinction. Historical reports remain descriptions of their diagnostic; their zero-stale delayed result is **not D2 freshness evidence**. No model result exists to invalidate. Hold production reuse until separately reviewed/versioned. The alternative historical interpretation “timestamp is start” would require a separately identified period end and verified semantics; it cannot silently replace the approved close assumption.

**External/governance blockers:** USA500 identity, compatible complete-hour OHLC/daily closes and actual publication history remain unknown. Stock derived `available_at` is assumed interval end, not measured publication. D3's continuous 240-minute horizon and shared four-complete-hour convention still lack joint approval. Raw minute opens at approximately 10:33/11:33/14:33/15:33, delayed exits, splits/dividends and formation membership/liquidity are absent. No pre-July-2020 canonical history was found for formation or FT0 warm-up. These block dependent work, not this inspection or an offline infrastructure package.

**Partial implementation / caution:** `asof_diagnostic` checks availability against interval start only; it is not a completed-bar/issuance validator. Aggregation correctly flags stubs, but has no six-slot-only feature view or distinct verified `period_end`/publication schema. Source gaps can affect the strict joint 48×16 windows, RMS/EMA/RSI recovery and daily-volume validity after the affected dates; exact retention was not computed. No imputation or origin deletion decision was made. The trailing course observation must be excluded by later authorized fit/window logic while retaining raw bytes.

**Infrastructure gaps:** environment setup, config hashing, immutable outputs, manifests and runtime snapshots already exist. Exact dependency locking, dirty-tree/code-content hashes, structured gate propagation, training-pair budgets and confirmation release guards do not. Historical runtime snapshots name the base SHA while the code was uncommitted, so a Git SHA alone does not reconstruct those executions. Current committed code is identifiable; historical execution equivalence is not retroactively proven. Conditional SP3/full-peer versus three-family cap and optional FC6/TG4/AD3 numerical details remain inactive review items.

No FT0/U1–U5/TG0, execution calendar, portfolio, baseline, neural engine, selection or confirmation implementation was found. These are **NOT_STARTED**, not failed Task 01 deliverables. G0 has verified inventory/permissions/safety components but blocked source and common-clock prerequisites. G1 has verified integrity and prior raw-price QA evidence, while actions, formation, minutes and source semantics remain blocked. **Neither overall gate is PASS.**

## Checks and footprint

Current offline tests: **60 passed in 5.06 seconds**, exit 0. Ruff passed, exit 0. In-memory compilation of 17 Python files passed without bytecode writes; `git diff --check`, dependency consistency and CLI help passed. No new dependency installation. Metadata/hash verification took 2.254 seconds; synthetic sample command took approximately 1.60 seconds. Exact end-to-end review wall time was not instrumented. An initial metadata display helper exited 1 when it assumed the legacy manifests had `coverage_audit`; a schema-aware retry succeeded. This was an audit-helper error, not a repository test failure. Pip printed a disabled-cache permission warning and still reported no broken requirements.

Largest persistent consumers before reports: `.venv` 282,571,065 logical bytes (288M allocated); data 8,682,157; reports 4,844,054. The ignored exhaustive QA JSON accounts for 3,850,223 report bytes. No cleanup occurred. New package/session byte totals are recorded in `checks.json`; only five small report files persist in the repository. Existing `.env` was never opened/copied; tracked-file and ignore checks protect it. Public code/config/setup scanning found no machine paths or credential-bearing URLs, a bounded check rather than a comprehensive historical-secret audit.

## Single proposed next package — P0.2 infrastructure delta

**Objective:** add a small offline evidence runner and append-only run/gate registry with conservative dependency status, code/config/protocol hashes and human-release boundaries. Reuse `config.digest/fingerprint/atomic_new`, `cli.runtime`, manifests, dry-run conventions and the existing 60 tests. Do not rebuild ingestion or the environment.

Prerequisite: explicit human acceptance of this P0.1 review and P0.2 scope. Source, minute, action, warm-up and shared-clock blockers may remain open; P0.2 must record them and block their dependents. Record F01 without repairing alignment as an unrelated side task.

Likely existing files: `src/lstm_data/config.py`, `src/lstm_data/cli.py`, `tests/test_store_cli.py`, `README.md`, `pyproject.toml` only if evidence metadata needs it. Proposed new paths, subject to review: `src/lstm_data/audit.py`, `tests/test_audit.py`, `configs/CURRENT_PROTOCOL.json`, `reports/audit/run_ledger.jsonl`. One lightweight file-based registry, no service. Existing historical reports are referenced as historical evidence, never assigned synthetic run success or rewritten.

Five review targets: protocol/hash manifest; deliberately failed synthetic gate and dependency block; append-only write/restart protection; exact code/config/source lineage; dry-run plus confirmation/conditional/pair-budget authorization guards. Estimated 1–3 hours implementation/review, seconds to minutes of offline validation, <1 MB new persistent metadata, zero new market rows or fitting pairs. Estimates are not benchmarks.

Stop if automation can bypass human review, source blockers, the 40-pair ceiling or confirmation protection, or needs a research-rule change. Out of scope: downloads, timing repair, source substitutions, feature/label/portfolio/model code, fitting, performance, optional branch activation and confirmation access.

Restart from this directory, its checks, the new session report, HEAD `92aecd1`, and unchanged source approval. Review the evidence first. **AWAITING HUMAN REVIEW — NO AUTOMATIC NEXT PACKAGE.**
