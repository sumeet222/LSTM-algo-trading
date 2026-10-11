# Human review — TA-MKT-SPY-001

**PARTIAL / SOURCE_BLOCKED / ACTIVATION_PENDING.** All human checks are NOT_YET_REVIEWED.

Review each independently; an implementation pass is not scientific approval.

1. **registration — IMPLEMENTATION_PASS / NOT_YET_REVIEWED**. Track A researcher SPY amendment and machine decision; no fabricated joint sign-off. Inspect `docs/track_a/decisions/Track_A_SPY_Market_Source_Amendment_v1.0_2026-10-11.md:1`.

2. **selector — IMPLEMENTATION_PASS / NOT_YET_REVIEWED**. SPY/SIP/raw default, immutable namespace, no fallback; calendar-derived March19 warm-up and 11 partitions. Inspect `src/lstm_data/market_source.py:29`.

3. **source_archive — BLOCKED / NOT_YET_REVIEWED**. Five-session pilot passed; first bulk partition exceeded planned two-page allowance. Publication and split scope unverified; no archive saved. Inspect `reports/data_audit/ta_mkt_spy_2026-10-11/source_failure_9.json:1`.

4. **D7_math — IMPLEMENTATION_PASS / NOT_YET_REVIEWED**. Independent U1–U5, absolute U2, prior-session locking, RMS thresholds, train p05 and robust scaling. Inspect `src/lstm_data/market_features.py:352`.

5. **causal_masks — IMPLEMENTATION_PASS / NOT_YET_REVIEWED**. UNKNOWN/late/stale rejection; exact consecutive48x5, endpoint and46/48, separate zero-fill masks; no empirical fits. Inspect `src/lstm_data/market_features.py:466`.

6. **preservation — IMPLEMENTATION_PASS / NOT_YET_REVIEWED**. Original source and tests unchanged; exact snapshots, five frozen documents, CURRENT_PROTOCOL and seven blockers preserved,0/40. Inspect `reports/data_audit/ta_mkt_spy_2026-10-11/preservation.json:1`.

7. **zero_diagnostics — IMPLEMENTATION_PASS / NOT_YET_REVIEWED**. Dedicated typing check: basic profile36files0errors; Ruff and parser pass. Final editor Problems human refresh pending. Inspect `scripts/check_python_types.py:18`.

8. **activation — BLOCKED / NOT_YET_REVIEWED**. Protected pointer remains original; proposal only. Shared/course/source/preparation gates and downstream FT0/model wiring pending. Inspect `reports/data_audit/ta_mkt_spy_2026-10-11/activation_proposal.json:1`.

Commands:
.venv/bin/python -m pytest -q →264passed,0skips; original baseline subset109passed.
`.venv/bin/ruff check src tests scripts reports/data_audit/p0_p1_close_2026-10-10_230214/source_intake.py` →PASS.
`.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-Pylance-extension>/dist` →36files,0errors,0warnings.
Select repository `.venv/bin/python` in VS Code, keep basic checking, restart Language Server and refresh Problems. The new editor state remains human-confirmed.

**Next single decision:** authorize a pagination diagnostic capped at four additional transports, with sanitized page-size/continuation evidence, to prepare a revised acquisition plan? The prompt requires review when the planned page allowance proves inadequate. This authorizes neither another bulk run nor scientific activation.

Keep CURRENT_PROTOCOL and the seven scientific blockers held. Review the proposed identity later with source and shared/course proof. No staging, commit or push was performed.
