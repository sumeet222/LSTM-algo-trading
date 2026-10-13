# Broad candidate source screen API v1

TA-BROAD-UNIVERSE-SCREEN-001 is source-only exploration. Production universe,
original protocols/source namespaces and all scientific holds are unchanged.

`lstm_data.broad_screen` freezes POOL/GROUPS/DATES and TECH_CONTROLS;
`prepare(report)` reads byte-verified containing original months/older pilots,
publishes immutable pre-query pool and exact seven-request plan. `acquire(report,
env_file=Path('.env'), get=requests.get)` validates training dates/material source
identity, uses existing authenticated HistoricalClient, one1000-attempt journal,
100/min paced transport, three-lifetime-attempt pages and256MiB StorageLimit.
It loads .env/credentials only for a missing verified chunk. New files remain in
data/raw/alpaca/track_a_broad_candidate_v1; corrupt/orphan chunks fail closed.
`read_candidate(store,params)` verifies hashes/material columns/row bounds;
successful missing symbols remain absent, never filled. `audit_day(frame,symbol,
day)` audits exact native30Min XNYS keys; `known_close_bounds(rows)` reuses the
existing necessary source-only T2 rule, never calculates real returns or fits.
`panel_identity(tuple)` accepts AAPL plus four distinct provisional non-Tech
sectors; `mask_intersection(masks,tuple)` requires identical five-name origin
keys and intersects65535 complete16-channel masks. It is tested against the
original919/1502 and inactive warmup1183/1502 saved feature-derived evidence.
`analyze(report)` creates key-level QA, formation liquidity proxies and bound
tables. It does not implement full-history acquisition, candidate48x16 feature
recomputation, source availability certificates, production activation or fitting.

Use the authoritative README environment; no new packages. From repository root:

```sh
.venv/bin/python -B scripts/run_broad_screen.py --phase plan --report reports/data_audit/NEW_SCREEN
.venv/bin/python -B scripts/run_broad_screen.py --phase acquire --report reports/data_audit/NEW_SCREEN
.venv/bin/python -B scripts/run_broad_screen.py --phase analyze --report reports/data_audit/NEW_SCREEN
```

The acquisition command is live and requires separately applicable permissions;
the pool here was explicitly authorized. Existing original/backup archives are
optional cost-saving containing-query caches; exact historical comparisons need
their original hash-bound bytes. Missing caches can be re-requested within the
same pilot budget; actual changed provider observations must receive a new report,
never a fabricated reproduction. Re-running acquire once on a completed report
writes zero_get_resume.json; journal SHA/count and source hashes must stay unchanged.
Do not rerun plan/analyze over existing outputs; choose a new evidence directory.

```sh
.venv/bin/python -B -m pytest -q tests/test_broad_screen.py
.venv/bin/python scripts/check_python_types.py --pylance-dist PATH_TO_INSTALLED_PYLANCE/dist
.venv/bin/ruff check .
.venv/bin/python -B -m pytest -q
```

Small checked-in audit JSONs are fixtures for original mask equivalence and the
independent calendar T2 oracle; tests need no live credentials or ignored source
Parquets. The full suite includes existing synthetic P2/P3/P4 tests only. Future
source/publication/action/formation/confirmation/amendment work remains HOLD.
