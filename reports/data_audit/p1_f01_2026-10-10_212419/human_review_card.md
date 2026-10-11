# P1-F01 human review card

Five exact inspection references:

1. `src/lstm_data/alignment.py:24`: schema contract and audit-only boundary. At cutoff 2001-01-02 15:00Z, period end 13:00Z is 120 minutes old; publication 14:00Z is 60 minutes old. Required result: STALE_PERIOD_END, usable=False. Source label is not an inferred period end.
2. `tests/test_calendar_alignment.py:91`: stale120, fresh60, publication five minutes late, exact90, over90, future period and inconsistent clocks. Later tests cover missing/ambiguous metadata, separate historical cutoffs and late-arriving old periods.
3. `src/lstm_data/audit.py:276`: the live synthetic F01 fixture now reports code PASS because it rejects the stale period; inspect still reports research BLOCKED. No historical finding was rewritten.
4. `src/lstm_data/cli.py:227`: the sole runtime caller supplies delay hypotheses but no documented course period end/publication basis. It remains diagnostic and fail-closed; no CLI/source-config changes.
5. `reports/data_audit/p0_1_2026-10-10_190015/p0_1_human_review_card.md:12`: archived pre-fix F01 mismatch, preserved as historical evidence. New corrected behavior is in this package's checks, not retroactively applied there.

Reproduce offline from the configured environment:

```bash
.venv/bin/python -B -m pytest tests/test_calendar_alignment.py tests/test_aggregation.py tests/test_evidence.py -q
.venv/bin/lstm-data evidence --mode diagnose --dry-run
```

Expected: 69 tests pass; diagnosis prints synthetic F01 PASS, all seven original blockers and research BLOCKED, then exits 2 by the existing diagnostic CLI convention. No `.env` needed. Full validation recorded: 111 tests passed; Ruff passed after one line-length correction. Review `checks.json` for expected/observed values and code/config/protocol identities, `preservation.json` for 12→13 exact-prefix ledger events and unchanged protected files/data stats. No approval is inferred from a test.

- F01 CODE STATUS: FIXED.
- SOURCE CLOCK STATUS: STILL BLOCKED.
- D3 SHARED CLOCK: UNSIGNED.
- P1.3 STOCK ACQUISITION: NOT AUTHORIZED by this package.
- FULL-MODEL S&P 500 REPLACEMENT: USER-REQUESTED FUTURE AMENDMENT; NOT IMPLEMENTED.
- RECOMMENDED NEXT INCREMENTAL PACKAGE: P1.3C bounded stock formation/corporate-actions readiness, after human approval of the liquidity convention and historical re-export/vintage policy; require its own acquisition authorization.
- STOP — HUMAN REVIEW. No P2, features, labels, fitting, portfolio or confirmation analysis.
