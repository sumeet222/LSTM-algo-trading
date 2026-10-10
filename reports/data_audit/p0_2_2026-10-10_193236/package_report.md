# P0.2 package report

**Infrastructure: PASS. Research G0/G1/G2: BLOCKED. G3–G9: NOT_RUN.**
Seven scientific/source-clock blockers remain open; F01 is reproduced as INVALID,
not repaired. No jobs, provider calls, confirmation metrics or conditional branches.

## Change and ownership

Added one small offline audit API, one central append-only JSONL ledger and one
subcommand of the existing CLI. No parallel executable, dependencies or new source
store. The only shared tracked edits are the four-line CLI extension and a README
section because the new interface needs a discoverable existing entrypoint.

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
| `src/lstm_data/cli.py` | Modified :21, :65, :91: route one evidence command before config loading or `.env`; existing five workflows unchanged. |
| `README.md` | Modified :107: document the evidence command, F01 and current blockers. |

No pre-existing file was deleted, renamed or moved. The new report directory was
named to match its recorded creation time during draft preparation.

## Evidence and validation

- Baseline: `.venv/bin/python -m pytest -q` → 60 passed in 4.90s;
  `.venv/bin/ruff check src tests` → PASS.
- Final implementation: the same suite → **94 passed in 5.75s**; focused
  `.venv/bin/python -m pytest -q tests/test_evidence.py` → **34 passed**; Ruff PASS;
  `git diff --check` PASS. Help and inspect/dry-run smoke commands exit 0.
- `lstm-data evidence --mode diagnose` → expected exit 2; F01-D2 INVALID:
  decision 15:00, assumed period end 13:00, hypothetical availability 14:00.
  Observed age 60; D2 period-end age 120; approved maximum 90 minutes. Fake 2001
  records only. `alignment.py` remains SHA-256
  `e4690828dde48dcc41b60c88b5f0e1d563092640ec003c8abf3dc65711000b8d`.
- Initial new-test run: 28 passed / 3 failed because the new fake market row lacked
  required volume; corrected the fixture, not production alignment. Initial new
  code lint formatting errors were corrected; no failures remain in final checks.
- Five exact authority hashes and three durable evidence references are in
  `configs/CURRENT_PROTOCOL.json`; protocol identity
  `119513911f3f7fb1c51cb93381e3f5ebae6b8939bac8e056bf53448726ceb843`.
  Historical P0.1 source IDs/counts are inherited, not re-audited provider facts.

## Safeguards and sizes

Explicit appends preserve old byte prefixes under an exclusive local lock and
atomic publication. Duplicate IDs, malformed/partial history and attempts to clear
scientific blockers fail closed. Tests exercise failure before publication, stale
locks, immutable corrections, narrow dependency causes, absent human evidence,
confirmation refusal and the synthetic 39/40/41-pair boundary. No genuine fits
are registered. An approval needs a hash-bound human-attributed decision file;
no such file or boolean unlocks research in P0.2. No research executor is provided.

Data before/after: **8,682,157 bytes unchanged**. Reports before: **4,960,531 bytes**;
exact final reports/ledger sizes, allocated KB and preserved-file hashes are in
`storage_and_preservation.json`, measured after the other deliverables. No Parquet
copies or raw row reads. The environment stays unchanged: Darwin arm64, Python
3.14.6; installed-version snapshot uses existing version ranges, not a portable lock.
New tests are offline: synthetic/temp fixtures plus current document/config metadata;
the CLI safety test refuses raw/secret reads and Python network connections. This
is not OS-wide enforcement, source verification or a clean-machine rehearsal.

## Handoff

Branch `feat/track-a-data-intake`, start/end HEAD
`92aecd1a382f93c1133f41b8ae2432bd9863ff70`; fetched origin; upstream 0 ahead/0 behind,
2 ahead/0 behind origin/main. No stage/commit/push. P0.1's five untracked artifacts
and the untracked appendix are preserved and excluded from the proposed P0.2 set.
Remaining blockers: F01; USA500 identity/publication; stock publication; minute
execution; actions/dividends; formation/prehistory; joint D3 clock sign-off.
Stale internal version wording in frozen documents remains visible and unchanged.

Review `human_review_card.md` and decide on a separately approved focused F01/source
clock repair or gated P1.1/P1.2 feasibility. Neither is started. Runtime and exact
Git/storage state are recorded in the session and preservation reports.

**AWAITING HUMAN REVIEW — NO AUTOMATIC NEXT PACKAGE**
