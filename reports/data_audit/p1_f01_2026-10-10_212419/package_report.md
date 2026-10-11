# P1-F01 — isolated freshness repair

The original F01 diagnostic accepted a period ending 120 minutes before the historical cutoff because its publication was only 60 minutes old. D2 requires freshness from the separately documented period end, with actual publication independently no later than that step's cutoff.

`asof_diagnostic` now computes `period_end_age_minutes`, checks its nonnegative 90-minute bound, and separately rejects future availability, future period ends and publication before completion. It preserves the existing signature. Optional market fields are `period_end`, `available_at` and `timing_basis`; documented and synthetic bases can test arithmetic, while missing, hypothetical, ambiguous or unverified metadata are explicitly BLOCKED. No course period end is inferred. A label-plus-delay value is display-only when actual availability is absent. `research_ready=False` always: documented is a caller assertion, not source certification.

Optional stock `decision_cutoff` takes precedence over legacy stock `available_at` and interval assumptions. Source label, period end, actual availability, hypothetical availability basis and cutoff are distinct outputs. The ambiguous `age_minutes`/quantiles names are replaced with period-end names; publication age and lag are separately named. Selection keeps the latest known period by each historical cutoff, so a late arrival of an older stale period does not replace a fresher observation. Rejected/future rows may be displayed for diagnosis only, never as usable inputs. Existing session/calendar behavior is untouched.

Caller inspection found one runtime CLI call (`cli.py:227`), the live F01 fixture, and alignment/aggregation tests. The CLI has no verified course-clock fields: its unchanged signature now fails closed. The live fixture supplies explicit synthetic clocks and expects rejection; its code regression is PASS. Historical P0.1/P0.2/P1.2D reports and their earlier INVALID finding remain untouched.

Validation: affected suites passed 69 tests after correcting one stale CLI fixture expectation; the full suite ran once, 111 passed. Full Ruff found one overlong message; the corrected five-file check passed. The seven independent blockers, G0–G2 BLOCKED, G3–G9 NOT_RUN and zero fitting pairs are preserved. One append-only G2 audit has `blocks=[]`, `supersedes=[]`; the old F01 event is historical evidence, not cleared. No source requests, credential reads, raw hashing or data processing were performed. Preservation uses small metadata hashes and data-file stats only.

The instructor's permission for conventional S&P 500 data in later full-model experiments is deferred human direction. No current USA500 contract, D1 membership, Track B inputs, source configuration or frozen protocol is changed. No proxy selected or downloaded.

Review `human_review_card.md`, `checks.json`, `preservation.json` and the mandatory session report. Integrate only the five named source/test files, central ledger append, this package directory and its session report after human review. Nothing staged, committed or pushed.

- F01 CODE STATUS: FIXED.
- SOURCE CLOCK STATUS: STILL BLOCKED.
- D3 SHARED CLOCK: UNSIGNED.
- P1.3 STOCK ACQUISITION: NOT AUTHORIZED by this package.
- FULL-MODEL S&P 500 REPLACEMENT: USER-REQUESTED FUTURE AMENDMENT; NOT IMPLEMENTED.
- RECOMMENDED NEXT INCREMENTAL PACKAGE: P1.3C bounded stock formation/corporate-actions readiness, after human approval of the liquidity convention and historical re-export/vintage policy; require its own acquisition authorization.
- STOP — HUMAN REVIEW. No P2, features, labels, fitting, portfolio or confirmation analysis.
