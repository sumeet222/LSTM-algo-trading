# Codex Session Report

## 1. Session metadata

- Date/time: started 2026-10-10T23:23:57.365161+00:00; handoff drafted 2026-10-10T23:35:55.893469+00:00 (UTC).
- Contributor / session: Codex; Track A P0.2 offline evidence infrastructure.
- Task requested: bounded reproducibility, append-only ledger and G0 audit skeleton;
  stop for human review without source acquisition or scientific implementation.
- Branch: `feat/track-a-data-intake`.
- Starting commit: `92aecd1a382f93c1133f41b8ae2432bd9863ff70`.
- Ending commit: identical; no commits created.
- Working tree at start: no tracked edits; five P0.1 artifacts plus mathematical
  appendix untracked. Current upstream 0 ahead / 0 behind after fetch.
- Working tree at end: two tracked files modified plus twelve new P0.2 files;
  all six pre-existing untracked files preserved. Exact paths below / preservation JSON.
- Related issue/PR: none created.

## 2. Executive summary

Implemented offline protocol identity, local environment attribution, validated
check/event contracts, append-only central ledger, narrow blocker view, safe CLI
and forward guards. Infrastructure PASS; research G0/G1/G2 BLOCKED; G3–G9 NOT_RUN.
F01 remains open and its synthetic D2 result is INVALID. No model/source jobs.

## 3. Research/protocol impact

- Research question, target/horizon, feature set, universe/data, splits/validation,
  trading/backtest rules, hyperparameters/search space: unchanged.
- Final-test protocol: untouched; no real confirmation data/metrics accessed.
- Existing source approval retained by reference, not a new scientific approval.
- Exact five authority hashes pinned; stale internal version references preserved.
- No conditional branch activated, D3 sign-off inferred or source timing assumed.

## 4. Files created

| File | Purpose / important interface (actual line) |
| --- | --- |
| `src/lstm_data/audit.py` | New offline utility: fingerprint :76; pinned protocol check :121; environment snapshot :177; check validator :217; F01 fixture :276; inspect :307; CLI modes :434. |
| `src/lstm_data/ledger.py` | New JSONL utility: event schema :118; history validation :168; blockers :205; 40-pair guard :215; operation guard :240; human reference :260; safe append :281. |
| `tests/test_evidence.py` | New offline tests: pointer mismatch :83; immutable append :104; fsync/replace failures :152; F01 :217; budget :245; explicit CLI append/read :264; no source/network/secret access :308. |
| `configs/CURRENT_PROTOCOL.json` | New schema-v1 five-document pointer and hash-bound P0.1/data evidence references; identity fields do not grant approval. |
| `reports/audit/track_a_events.jsonl` | New central ledger, seven P0.1 BLOCKED events, zero attempted fits; UTC event timestamps describe registration now. |
| `docs/track_a/p0_2_evidence_harness.md` | New command/schema/example, single-writer limits, guard and status contract. |
| `reports/data_audit/p0_2_2026-10-10_193236/checks.json` | New validated G0-focused checks; infrastructure PASS versus research BLOCKED; synthetic F01 INVALID. |
| `reports/data_audit/p0_2_2026-10-10_193236/environment.json` | New local OS/Python/dependency snapshot; no lock or clean-machine claim. |
| `reports/data_audit/p0_2_2026-10-10_193236/storage_and_preservation.json` | New final byte/allocated-size measurement and preserved-file inventory; no bulk data QA. |
| `reports/data_audit/p0_2_2026-10-10_193236/package_report.md` | New compact package inventory and handoff. |
| `reports/data_audit/p0_2_2026-10-10_193236/human_review_card.md` | New seven-item manual review route. |
| `reports/codex_sessions/2026-10-10_193236_feat-track-a-data-intake_p0-2-evidence.md` | New mandatory 17-section session report. |

The table lists type/purpose and key line references; all listed files are new.
No artifact depends at runtime on P0.1 scratch in temporary storage.

## 5. Files modified

- `src/lstm_data/cli.py`: four added lines import/register/route evidence before
  existing config/credential logic. Existing five command defaults and behavior
  retained. Required to reuse the established console entrypoint rather than fork it.
- `README.md:107`: appended evidence commands, protocol/ledger/schema links and F01
  warning. Required to document the new interface and scientific scope.

## 6. Files deleted, renamed, or moved

None pre-existing. Only this session's newly created report-directory draft was
renamed to match its creation timestamp before final handoff.

## 7. Critical functions, classes, variables, and config keys

- `stable_fingerprint(dict)->str`, audit.py:76: canonical SHA-256 of portable
  substantive config; no writes; excludes metadata/secret fields, preserves dates.
- `protocol_identity(dict)->str` :104 and `protocol_check(root,pointer)->dict` :121:
  exact ordered five authority paths/versions and durable evidence hashes; missing
  or changed input BLOCKED, no version fallback, approval or source-truth inference.
- `code_identity(root)->str` :170 / `environment_snapshot(root)->dict` :177:
  uncommitted code-content identity and separate actual installed environment;
  no network or dependency changes.
- `validate_check(dict)->None` :217 / `make_check(context,id,status,evidence,...)->dict`
  :244: schema-v1 G0–G9 evidence, nullable IDs/thresholds and actions/rerun scope.
- `f01_fixture()->dict` :276: two fake 2001 OHLCV rows; calls unchanged alignment;
  reports INVALID D2, never verifies a real publication assumption.
- `inspect(root,pointer_name,ledger_name,diagnose=False)->dict` :307: read-only
  metadata/synthetic path, stable run identity, BLOCKED research, no executors.
- `validate_event(dict)->None` ledger.py:118 / `decode_ledger(bytes)->list` :168:
  strict statuses/schema/UTC, duplicates/corrections/protocol/truncation checks.
- `current_blockers(events)->list` :205: derived view, unrelated PASS does not clear
  scientific blockers; input history is validated before managed inspection.
- `pair_budget(events,candidate_attempt_id=None)->dict` :215: global 40 ceiling,
  counts failed/superseded pair IDs; a reused candidate ID is rejected. Synthetic
  fixtures only; P0.2 append rejects actual attempt IDs/results.
- `guard_operation(operation,events)->dict` :240: narrow dependency causes; only
  administration can PASS here; all research/confirmation execution unavailable.
- `verify_decision(root,reference)->None` :260: real relative file/hash/id with human
  attribution/scope; no empty booleans. Local record is not authenticated identity.
- `append_event(path,event,root=...)->None` :281: explicit small reports-only write,
  exclusive sidecar and atomic publication preserving prior byte prefix. No blocker
  narrowing/clearance or protocol migration allowed in P0.2; stale lock fails closed.
- `add_parser` :422 / `run_cli` :434: inspect default, synthetic diagnose, explicit
  append; optional new report only; dry-run forbids writes; never loads `.env`.
- Config: CURRENT_PROTOCOL schema_version, documents, data_refs, source_ids,
  protocol_hash, attribution git/created_at; pair ceiling constant remains 40.

## 8. Data/schema/provenance changes

No data/schema corrections or source edits. Added metadata-only check and JSONL
event schemas documented in `docs/track_a/p0_2_evidence_harness.md`. Source IDs inherit
P0.1: 159,008 stock rows / 60 canonical manifest-Parquet pairs and 29,510 USA500
rows. No all-Parquet hash/row QA repeated. Course and stock provenance hashes remain
references, not evidence of provider semantics. All event/check timestamps explicitly
UTC; synthetic source dates are fabricated. Corporate actions and timing remain
unverified. Rebuild/migration: none. New ledger is not a complete approval history.

## 9. Dependency/environment changes

None. Existing `pyproject.toml` ranges remain authoritative. Snapshot:
`reports/data_audit/p0_2_2026-10-10_193236/environment.json`; Darwin 25.6.0 arm64, Python 3.14.6; no exact portable
lock, upgrades, package downloads or clean-machine rehearsal. No new environment
variables; no `.env` or credential values read/printed. Installed setuptools is
absent in this runtime snapshot (editable package already works); no build attempted.

## 10. Commands and tests run

- `git status --short --branch`, `git branch --show-current`, `git rev-parse HEAD`,
  `git remote -v`, `git fetch --all --prune`: inspected/fetched origin nondestructively;
  fetch used the existing approved escalation prefix. No pull/integration.
- Baseline `.venv/bin/python -m pytest -q`: 60 passed / 4.90s.
- Baseline and final `.venv/bin/ruff check src tests`: PASS.
- Initial focused new tests: 28 passed / 3 failed due to missing volume on a fake
  row. Corrected new fixture; no production alignment change. Initial new-code
  lint import/line-format errors fixed using Ruff on only new files.
- Final `.venv/bin/python -m pytest -q`: 94 passed / 5.75s (60 existing + 34 new).
- Final `.venv/bin/python -m pytest -q tests/test_evidence.py`: 34 passed.
- `.venv/bin/lstm-data evidence --help`: PASS; inspect / --dry-run smoke: exit 0,
  infrastructure PASS / research BLOCKED, 0 attempted pairs.
- `.venv/bin/lstm-data evidence --mode diagnose`: expected exit 2; F01-D2 INVALID.
- `git diff --check`: PASS. Tracked diff and all new Python/interfaces reviewed.
- File hashes and sizes compared to preflight: details in preservation JSON.

## 11. Experiment/results summary

No scientific experiments, training, features/labels, portfolio simulation or
confirmation metrics. Synthetic F01 fixture only: availability-age 60 versus
period-end-age 120 minutes against D2 maximum 90. This is defect evidence, not
report-eligible model performance. No fitting pairs consumed; no seed/cutoff results.

## 12. Reproduction instructions

Follow README's Python 3.11–3.14 venv + editable dev setup; then from repository root:
`.venv/bin/python -m pytest -q` and `.venv/bin/ruff check src tests`.
Run `.venv/bin/lstm-data evidence` (exit 0, research BLOCKED) and
`.venv/bin/lstm-data evidence --mode diagnose` (expected exit 2, F01 INVALID).
A unique `--output reports/my_review.json` saves a small report without overwrite.
Current pointer requires the five authority docs, preserved P0.1 checks and existing
approval/pilot JSON in the clone; raw sources/credentials are unnecessary for P0.2.
The P0.1 untracked checks prerequisite must accompany a future reviewed integration;
this session is explicitly not authorized to stage it. No hidden scratch dependencies.

## 13. Git / collaboration status

Current branch/HEAD unchanged. Origin fetched; upstream 0 ahead / 0 behind; origin/main
2 ahead / 0 behind. No stage, commit, push, PR, merge, stash, reset or rebase.
Shared conflict-sensitive edits limited to README and CLI. Six pre-existing untracked
files are preserved and excluded from P0.2 staging. Exact end-state path inventory
and hashes in `storage_and_preservation.json`.
After separate human approval, minimal proposed add set (guidance, NOT EXECUTED):

```bash
git add -- README.md src/lstm_data/cli.py src/lstm_data/audit.py src/lstm_data/ledger.py tests/test_evidence.py configs/CURRENT_PROTOCOL.json docs/track_a/p0_2_evidence_harness.md reports/audit/track_a_events.jsonl reports/data_audit/p0_2_2026-10-10_193236/package_report.md reports/data_audit/p0_2_2026-10-10_193236/checks.json reports/data_audit/p0_2_2026-10-10_193236/environment.json reports/data_audit/p0_2_2026-10-10_193236/human_review_card.md reports/data_audit/p0_2_2026-10-10_193236/storage_and_preservation.json reports/codex_sessions/2026-10-10_193236_feat-track-a-data-intake_p0-2-evidence.md
git commit -m "feat: add offline Track A evidence and audit ledger"
```

Do not add entire reports/docs folders. A teammate must separately review/integrate
P0.1 prerequisites before a complete portable clone; no automatic staging of them.
Fetch and inspect again before a later authorized push/PR. No push performed here.

## 14. Known issues, risks, and limitations

F01 unchanged; USA500 identity/publication, stock availability, minute execution,
actions/dividends, formation/prehistory and shared D3 sign-off BLOCKED. G3–G9 NOT_RUN.
No exact cross-platform lock/rehearsal. Ledger logical append-only, bounded 2 MB,
cooperating local writers; not tamper-proof OS permissions or distributed storage.
Crash-stale lock/temp needs human inspection; no automatic history repair. Human
record is hash-bound local attribution, not authentication. Research guards operate
only in this API; arbitrary external scripts are not constrained. No remaining
software test/lint failures. Data sizes are unchanged, not a new bulk-integrity proof.

## 15. Decisions requiring human or teammate review

Review P0.2 evidence and file ownership/integration. Decide separately whether
F01/source-clock repair precedes gated P1.1/P1.2 feasibility. Resolve shared D3 via
actual two-track sign-off. No next package or source/model/confirmation approval
is implied. Do not use synthetic delay as provider truth.

## 16. Next recommended steps

1. Review the seven-item human card and central contracts; preserve all local work.
2. Authorize one bounded next package if appropriate; this session launches none.
3. Separately coordinate integration of required P0.1 evidence and P0.2 artifacts.

## 17. Artifact inventory

Central metadata pointer/ledger; `reports/data_audit/p0_2_2026-10-10_193236/checks.json`, environment snapshot,
package/human cards and storage/preservation JSON; this report and schema docs:
all intended for version control after approval, currently untracked. Existing
canonical raw data remain ignored and local; no new plots, checkpoints, scientific caches,
window stores, per-seed trees or scientific outputs. Data before/after 8,682,157
bytes; reports before 4,960,531 bytes; final sizes/elapsed duration in preservation
JSON. Preflight scratch is audit-only, not a runtime prerequisite.

**AWAITING HUMAN REVIEW — NO AUTOMATIC NEXT PACKAGE**
