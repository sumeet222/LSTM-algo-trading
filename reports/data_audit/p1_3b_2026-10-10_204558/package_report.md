# P1.3B — bounded formation-source evidence

**Source access and the 60-session record check passed; formation eligibility and G1 remain BLOCKED.** One successful five-symbol SIP/raw daily response supplied all 300 expected observations for April 6–June 30, 2020. No backups, bulk store, features, labels, models or confirmation outcomes were accessed or generated.

The request was predeclared in [probe_plan.json](probe_plan.json). Actual parameters, transport metadata, response hash, five small examples and exact diagnostic sums/means are in [probe_results.json](probe_results.json). [formation_matrix.md](formation_matrix.md) contains the compact comparison; [checks.json](checks.json) distinguishes narrow PASS findings from independent WARN/BLOCKED/INVALID/NOT_RUN statuses.

## Observed

- All five primaries have 60 unique expected sessions, with zero missing, duplicate, unordered, nonfinite or invalid OHLCV records. All returned symbols match the requested originals. Labels are midnight ET / 04:00 UTC, with no calendar mismatch.
- Explicit request: `https://data.alpaca.markets/v2/stocks/bars`, `AAPL,JPM,JNJ,WMT,CAT`, `sip`, `raw`, `1Day`, `USD`, `asof=2020-07-01`, ascending, limit 1000, inclusive `2020-04-06T04:00:00Z` through `2020-07-01T03:59:59.999999999Z`. Formation-date entity mapping replaces the P1.3A proposal's 2025 mapping **for this probe only**; repository config is unchanged. `asof` does not restore a publication vintage. [Provider parameter reference](https://docs.alpaca.markets/us/reference/stockbars).
- Mean close×volume proxies, in canonical order: **$12,373.672m / $2,588.086m / $1,437.484m / $1,247.123m / $576.226m**. Every open/close/low/high proxy mean uses 60 sessions and exceeds the fixed $50m reference. All four diagnostic rankings agree: AAPL > JPM > JNJ > WMT > CAT. AAPL/CAT are prospective extrema only; D8 identities are not selected.
- Daily volume admits eligible extended-hours trades; its exact extended-hours contribution was not measured. OHLC and volume filters differ, so low×volume/high×volume is proxy sensitivity, not guaranteed actual-turnover bounds. Nor is vendor VWAP×normal volume automatically exact turnover. This evidence does not supply D4 full-RTH daily volume. [Provider aggregation FAQ](https://docs.alpaca.markets/us/docs/market-data-faq).

## Unresolved

The liquidity estimator/session basis is unapproved. A modern raw historical re-export, entity-mapping date and source timestamps do not establish values observable on July 1, 2020. Historical `available_at` and vintage remain UNKNOWN. No complete action ledger was queried, so split/dividend events within the formation window remain unidentified; raw means no requested adjustment, not proof of event history or vintage. Paired split-price/inverse-volume invariance passed synthetically; dividend treatment remains separate.

Formation information, present-day source coverage, retrospective full-study 98%/95% usability, and conditional course membership remain separate. No full-study coverage, minute retry path, FT0 warmup or portfolio accounting was certified. The user's statement that the instructor supplied a Dukascopy export is retained as provenance testimony; exact contract, bid/ask basis, export settings, clocks, publication, daily close, prehistory and meaningful membership are unverified. The existing source-owner inquiry remains pending; no new inquiry or message was sent. F01 remains INVALID and unused; shared D3 sign-off remains outstanding.

## Budget and preservation

**Two authenticated transport attempts conservatively counted against the six-attempt ceiling; one HTTP response.** The sandbox attempt failed before a response. An explicitly approved escalation repeated the same single query; HTTP 200 returned 33,288 bytes, no continuation page. No provider retry, pagination, subscription/account/billing operation or source/feed fallback. Feed was explicitly requested, with no independent feed echo in the response. Headers showed 200/min and 199 remaining for that response, not a subscription SKU or future guarantee; no charging evidence was encountered.

Only summaries, hashes and five stock-day examples were persisted; the 300-row response was used in memory and not saved as another panel. Fourteen audit-check records validate; two hand calculations, split-product algebra, calendar and preservation checks passed. Prior test results are inherited, not rerun. One non-clearing WARN audit preserves the ten-event byte prefix, seven blockers and zero fits. Exact elapsed time/report bytes and Git state are in the mandatory session report. A concurrent external commit `6127cbc` committed P1.1/P1.2/P1.3A during this session; their bytes remain unchanged. P1.3B is uncommitted; no Git mutation was performed by this agent.

## Needed from human and single recommendation

1. **Liquidity convention:** allow raw daily close×vendor daily volume as a **provisional diagnostic proxy**, accepting its extended-hours/filter scope; or require a qualified RTH/actual-turnover construction before applying D1. Neither option approves the universe or D8 pair now.
2. **Vintage qualification:** document a justified assumption permitting current historical re-exports for the formation screen, while historical publication remains unverified; or require publication/version evidence and hold formation approval. No assumption is adopted here.
3. **Next scope:** approve a small separate Dukascopy source-contract verification using the already drafted owner questions/export settings, or HOLD. Do not repeat this complete daily probe or authorize bulk by implication.

**Recommendation:** resolve the course export contract next through a separately approved source-contract package. Another bounded stock probe is not warranted until a particular convention/action evidence gap is specified. Shared D3 agreement and Git integration remain separate human decisions.

**STOP — AWAIT HUMAN REVIEW.**
