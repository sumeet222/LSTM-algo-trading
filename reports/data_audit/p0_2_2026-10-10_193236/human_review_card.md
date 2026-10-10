# P0.2 human review card

Infrastructure PASS; research G0/G1/G2 BLOCKED; F01-D2 INVALID. All commands below
run from the repository root after README setup. Fixture tests never modify the
central ledger or authority documents.

1. **Read current state:** `.venv/bin/lstm-data evidence --dry-run`.
   Expected `infrastructure_status=PASS`, `research_status=BLOCKED`, seven blocker
   events, `attempted_pairs=0`; stock administration PASS, market/confirmation BLOCKED.
   Review `checks.json` (check IDs `protocol-identity`, `ledger-schema`, F01).
2. **Normal ledger write/read:**
   `.venv/bin/python -m pytest -q tests/test_evidence.py::test_explicit_cli_append_and_read`.
   Expected one passed: a tiny temporary event is appended and read unchanged;
   duplicate append rejected. Exact old-byte-prefix/correction test is
   `tests/test_evidence.py:104`. Real append syntax/schema: evidence contract § Ledger.
3. **Intentional synthetic failure:** `.venv/bin/lstm-data evidence --mode diagnose`.
   Expected exit **2**, F01-D2 **INVALID**, observed availability-age **60** versus
   period-end age **120**; actual source lag remains unknown. Inspect
   `src/lstm_data/audit.py:276`, `checks.json`; do not interpret passing pytest as D2 PASS.
4. **Narrow blocker propagation:**
   `.venv/bin/python -m pytest -q tests/test_evidence.py::test_narrow_failure_and_no_test_auto_approval`.
   Expected one passed: unverified market blocks market work, independent stock
   administration stays PASS; portfolio failure adds economic, not predictive, causes.
   All research operations still need a future reviewed executor/authorization.
5. **Immutable protocol/hash mismatch:**
   `.venv/bin/python -m pytest -q tests/test_evidence.py::test_pointer_mismatch_blocks`.
   Expected five passed: altered/missing temporary authorities, version/hash/extra
   document changes all produce BLOCKED; original files remain untouched.
   Exact pinned paths/SHA-256: `configs/CURRENT_PROTOCOL.json`; resolver :121.
6. **Confirmation and missing sign-off refusal:**
   `.venv/bin/python -m pytest -q tests/test_evidence.py::test_external_blockers_and_confirmation_locked`.
   Expected one passed: shared D3, USA500 and minute execution stay BLOCKED; even an
   empty ledger cannot unlock confirmation. Guard: `src/lstm_data/ledger.py:240`.
7. **Budget/safety and provenance:**
   `.venv/bin/python -m pytest -q tests/test_evidence.py` → 34 passed.
   Review :245 (39→40 allowed by budget alone, 40→41 and reused ID blocked), :152
   (fsync/replace failure preserves history), :308 (no source/secret/network access).
   Compare `environment.json`, `storage_and_preservation.json`, and mandatory
   session report `reports/codex_sessions/2026-10-10_193236_feat-track-a-data-intake_p0-2-evidence.md`. No exact cross-platform lock/rehearsal is claimed.

The pointer and ledger are not approvals. Keep P0.1 and the appendix outside any
P0.2 staging set. Decide the next package explicitly; this report grants no green
light for F01 repair, P1.1/P1.2, model work or G9.

**AWAITING HUMAN REVIEW — NO AUTOMATIC NEXT PACKAGE**
