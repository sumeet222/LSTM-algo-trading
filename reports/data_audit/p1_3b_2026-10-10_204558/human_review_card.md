# P1.3B decision card

**Observed:** all 300 SIP/raw daily records, 60 per primary, valid and aligned to the expected formation window. All four price-volume proxies exceed $50m; diagnostic extrema agree on AAPL/CAT. No universe or D8 activation.

**Unresolved:** unapproved liquidity convention, historical publication/vintage, full actions and source coverage, conditional USA500 membership/contract, F01 and shared D3 sign-off. G1 remains BLOCKED.

Four directly inspectable targets:

1. [probe_plan.json](probe_plan.json): verify five primaries only, SIP/raw/1Day, formation-date mapping, exact range, one-page plan and six-attempt ceiling. Existing config was not edited.
2. [probe_results.json](probe_results.json): verify one HTTP 200 plus one failed sandbox transport, no next page, 300 rows, source hash/locators, null historical availability, and documented extended-hours/filter limitations. Check April 6 AAPL `262.47 × 55,182,629 = 14,483,784,633.63`; JPM `89.46 × 31,402,576 = 2,809,274,448.96`.
3. [formation_matrix.md](formation_matrix.md): verify every denominator is 60, defects are zero, low/high products are sensitivity only, and each formation/membership verdict remains blocked. AAPL/CAT are diagnostic candidates, not activated identities.
4. [checks.json](checks.json): inspect narrow PASS versus WARN/BLOCKED/INVALID/NOT_RUN; F01 unchanged, seven ledger blockers, zero fits. Final preservation/Git/byte checks are recorded in the mandatory session report. A concurrent external commit `6127cbc` committed the unchanged predecessor files; only P1.3B remains uncommitted.

**Needed from human:** choose provisional close×vendor daily-volume proxy versus qualified RTH/turnover evidence; explicit justified historical re-export assumption versus required vintage evidence; approve a separate Dukascopy source-contract review or HOLD. [package_report.md](package_report.md) states consequences and the single recommendation. These choices do not authorize bulk, backups, labels, training or Git integration. The P1.3B prompt requires another human review before subsequent work.

**STOP — AWAIT HUMAN REVIEW.**
