# TA-MKT-SPY-002 human review card

**Overall: SOURCE_BLOCKED — HUMAN_REVIEW_REQUIRED; ACTIVATION_PENDING.**
All statuses below are proposed engineering findings, not human signatures or scientific
gate clearance. Inherited SPY-001 checks 1–7 were accepted; check8 was not explicitly signed.

| # | Review item | Proposed engineering result | Scientific / remaining status | Evidence |
|---|---|---|---|---|
| 1 | Preserve source decision, v1 and human work | PASS | Shared/course approval HOLD | preservation.json; unchanged TA-D2-MARKET-SPY-001, proposal and RandomNotes |
| 2 | Pagination, retry, checkpoint safety | PASS | Bulk capacity HOLD | pagination_diagnostic.json; acquisition_plan_v2.json; budget_review.json; 13/240 attempts; >2-page/replay/crash/repeated429 tests |
| 3 | Full archive/date/calendar QA | HOLD | 0/11; observed coverage not measured | archive_manifest.json; source_qa_full_period.json; QA code tested on sparse immutable fixtures |
| 4 | Corporate actions and source clock | HOLD | Publication UNKNOWN; full action scope unverified | corporate_action_scope.json; source_qa.md; no certified split absence |
| 5 | Archive→D7 and frozen formulas | PASS offline; real canonical trace HOLD | No empirical floors/scalers | market_api.md; market_source_integration.json; positive synthetic 48×5 and real inherited pilot blocks |
| 6 | Own-step causality, masks, research blockers | PASS implementation | Seven blockers HOLD; G0–G4 not cleared | preservation.json; source IDs/scheduled ends; 46/48 + endpoint tests; 0/40 pairs |
| 7 | Tests, typing, Ruff, frozen/ledger/Git | PASS tools; editor confirmation HOLD | No staging/commit/push | 278 passed; 38 files, 0 errors/warnings; AST/Ruff/diff PASS; 24-event ledger unchanged |
| 8 | Downstream handoff and activation | HOLD | Source resources and formal activation pending | market_api.md; activation_proposal_v2.json; decision_compatibility_matrix_v2.json |

Mark each item **PASS / CORRECT / HOLD**. Refresh VS Code Pylance Problems with
`.venv/bin/python` selected and confirm no errors/warnings; automated parity checking
does not count as an observed editor screenshot or human confirmation.

**One narrowly scoped resource decision:** approve a new versioned policy with at most
900 cumulative Alpaca attempts and 32 pages per fixed partition, retaining three attempts
per page, 11 original intervals, SIP/raw/30Min, 256 MiB, no repeated429 and all scientific
holds; or retain 240 and keep SOURCE_BLOCKED. Restart's current calendar envelope is
853 attempts. No temporary diagnostic pages remain. See budget_review.json.
This proposal is not executed or registered as an approval.

The prompt's Stage3C requires: “if credible worst-case budget exceeds 240, stop”.
That explicit boundary caused this stop.

```bash
python -m pytest -q
ruff check .
python scripts/check_python_types.py --pylance-dist <installed-pylance-extension>/dist
python -m lstm_data.market_source plan --report reports/data_audit/ta_mkt_spy_002_2026-10-11
```

The current acquire command returns SOURCE_BLOCKED with zero new GETs. Do not reset
the journal or copy a proposed protocol over CURRENT_PROTOCOL. After resource approval,
the next session must generate an additive feasible plan/config using these measurements,
retain the old plan as evidence, and preserve completed SHA-verified chunks on resume.
