# Candidate source remediation API

`TA-DATA-REMED-FT0-001` acquired genuine missing pre-July context without changing
`stock_source.load_stock_history` or the approved primary source config. The
current candidate config is `configs/track_a_remediation_v2.json`; it is inactive.
Version1 and the original request manifest remain immutable historical records.

`remediation_plan.dependency_calendar` derives the earliest required source date
from the first July input and all frozen feature lookbacks. December 18, 2019
supplies M4's oldest daily endpoint and, if complete, 754 EMA updates before the
first June 19 input. Native warmup is stored once in the separate immutable
`data/raw/alpaca/track_a_remediation_v1` namespace. Existing source rows win on
all overlaps. New numerical compatibility checks never certify original vintage,
publication or actual execution prices.

`remediation_transport` provides append-before-send receipts, three lifetime
attempts per page, an independent 180-attempt ceiling and shared 256 MiB storage
checks. The observed pagination amendment raises the initial per-chunk page
estimate only; original request parameters and global ceilings remain unchanged.
`remediation_overlay.resolve_native` selects compatible real Alpaca additions;
`history_from_view` reuses existing aggregation/calendar/StockHistory;
`fixed_retention` reuses FT0 math and the unchanged 1502/496 original populations.

`remediation_secondary` preserves Massive native observations in a separate
namespace with a cumulative attempt journal. Its original ceiling was 80; the
human-approved budget amendment raises the total ceiling to 200 using
`--budget-amendment <budget_amendment_v1.json>`. Source identity, timestamp and adjustment
flags are explicit; native volume adjustment is unverified. No returned secondary
row is silently mapped to Alpaca SIP. Both the original historical probe and
the explicitly authorized renewed key check received HTTP 403. Two cumulative
attempts are used, 198 remain under the amended ceiling; no secondary data or
source overlay was created.

After the predecessor FT0 package is integrated, reproduce in a clone with the
README's editable `.venv` setup and the documented original archives. Offline
tests require no keys. For a fresh report directory, run the original `ft0_audit`
into its `original_replay/`, then write `dependency_calendar.json` and
`request_manifest.json` using the exported planner and original immutable QA.
Acquisition reads only repository-configured credentials; no new paid access is
permitted by this package.

```bash
python -m pytest -q
ruff check .
python scripts/check_python_types.py --pylance-dist '<installed-extension>/dist'
# SHA-verified completed resumption; fixed report/manifest and package authority.
python -m lstm_data.remediation acquire --report reports/data_audit/ta_data_remed_ft0_001_2026-10-11_195135 --env-file .env --authorization TA-DATA-REMED-FT0-001
# Recompute candidate audits only into a FRESH prepared report directory.
python -m lstm_data.remediation audit --report reports/data_audit/<new-prepared-report>
```

The secondary acquisition requires permitted historical access; its current 403
journal stops further requests. An explicitly authorized renewed access check
can use `--access-review <review.json>` with the existing secondary CLI. The review
binds `package`, unique `review_id`, `prior_journal_sha256`, `prior_attempts` and
`validation_request_hash` to the frozen first historical request. It appends an
`ACCESS_REVIEW` event and permits one validation attempt. Only HTTP 200 permits
further acquisition; denial, transport failure or interruption stops resumption.
The same review never grants a second check. It cannot clear a prior 401/429 or
reset the cumulative budget or three-attempt lifetime page ceiling. Never generate
another review automatically to bypass a failed check. The latest human review
and sanitized receipts are in the package's `secondary_resume_2026-10-11_212118/`.
Further acquisition needs genuinely resolved historical access and renewed
explicit authority. All candidate data remain
unactivated, with historical publication/action/fitting/formal approval holds.
No real floor/scaler fit, P3/P4, confirmation outcome or neural attempt is enabled.

The budget amendment binds the approved 200 total to the exact old journal byte
prefix, SHA, spent-attempt count and frozen request-manifest SHA. It grants 198
remaining attempts with the current 2 spent; it does not grant 200 additional
attempts or clear HTTP403/401/429. Primary Alpaca 180 and prior SPY 129 are unchanged.
Use the amendment path recorded in `configs/track_a_remediation_v2.json`; without
the explicit amendment the secondary CLI keeps the original 80 ceiling. Historical
receipts remain append-only and all failures continue to consume the total.

[The Alpaca contract](https://docs.alpaca.markets/us/reference/stockbars) documents
split price/volume adjustment and entity mapping as-of. These are distinct from
historical publication. [Massive's contract](https://www.massive.com/docs/rest/stocks/aggregates/custom-bars)
defines native window-start timestamps and qualifying-trade aggregates; empty
provider responses alone do not establish market-wide absence of trading.
