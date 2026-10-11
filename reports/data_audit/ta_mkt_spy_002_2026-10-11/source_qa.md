# SPY continuation source QA

**SOURCE_BLOCKED — HUMAN_REVIEW_REQUIRED.** Engineering completion is not claimed.
Four new GETs succeeded and returned 336, 344, 350 and 354 rows; each had a continuation.
Requested limit was 10,000. Exact payload lengths/hashes and timestamps are in
[pagination_diagnostic.json](pagination_diagnostic.json); all transport receipts are
in the single canonical `data/raw/alpaca/track_a_spy_v1/transport_attempts.jsonl`.
The original nine-line /607-byte prefix is unchanged. No further source transports ran.

The measured plan has 280 calendar-envelope pages and an in-process upper
budget of 841, including three attempts/page and four genuine reusable pages.
Those temporary responses were discarded after NO_GO; restart requires an upper
budget of 853. Even the smaller 48-bars/exchange-session estimate
requires 598 on restart. The authorized ceiling is 240. Subdividing
intervals does not remove the per-page transport cost and can add terminal-page rounding.
This does not prove actual acquisition would consume the upper bound.

There are **0/11 saved partitions, zero source Parquet bytes**. Full-period observed
coverage and missing slots are UNKNOWN, not pilot-derived PASS. Calendar-only denominators
are 1327 sessions, 17197 RTH
half-hours, 7935 complete hours and 1,327 closing stubs.
The inherited stock gaps remain 168 separately. The warm-up requirements in
[source_qa_full_period.json](source_qa_full_period.json) are scheduled requirements only.

[Alpaca bars documentation](https://docs.alpaca.markets/us/reference/stockbars) permits
limit <=10,000 and explicitly warns that shorter responses can still continue.
Raw means no adjustments; asof identifies symbol/entity mapping.
[The FAQ](https://docs.alpaca.markets/us/docs/market-data-faq) documents interval-start
timestamps. None of these establish original historical publication. `available_at`
stays UNKNOWN; no retrieval/end-time substitute is installed.

The [issuer notice](https://www.ssga.com/library-content/announcements/etfs/au/20200320-SPY-Distribution-Announcement.pdf)
corroborates the March 20, 2020 US distribution sample. The issuer's
[distribution inventory page](https://www.ssga.com/us/en/intermediary/resources/documents/etf-dividend-distributions)
provides the next primary-source entry point. Full distributions/splits and source
vintage are unverified. No split absence is certified, no raw prices were adjusted,
and no SPY distribution enters stock accounting. Metadata requests were not made
after the source budget NO_GO; a full acquired-range reconciliation remains deferred.

One resource decision is needed: review the proposed 900 cumulative attempt /32-page
per-partition continuation in [budget_review.json](budget_review.json), or retain 240
and remain blocked. It is PROPOSED_ONLY; no caps or scientific holds were raised.
