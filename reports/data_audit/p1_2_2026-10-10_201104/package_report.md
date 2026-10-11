# P1.2 — USA500 source contract and historical as-of feasibility

The actual course file has verified local schema, explicit UTC timestamp encoding, sampled numeric OHLC and study-spanning labels consistent with prior evidence. **Independent vendor/instrument identity, hourly start/end/completion, daily-session close and historical publication remain UNKNOWN-BLOCKED.** Consequently D7/U1–U5, market-conditioned ridge, MC0/MC1/MC2 and market-dependent joins/diagnostics remain blocked. This adds no USA500 restriction to stock-only work, whose existing stock/shared-clock prerequisites remain independent. No G0/G1/G2 promotion, production alignment, proxy, feature/label/model/backtest or confirmation outcome occurred.

The field-by-field VERIFIED / SUPPORTED_WITH_QUALIFICATION / UNKNOWN-BLOCKED / CONTRADICTED matrix and evidence citations are in [source_contract.md](source_contract.md). [checks.json](checks.json) contains 15 schema-valid scoped checks. `CURRENT_PROTOCOL` matches all five pinned authorities/references: `119513911f3f7fb1c51cb93381e3f5ebae6b8939bac8e056bf53448726ceb843`. Pointer/config/source code are unchanged; the provisional close assumption is preserved without promotion.

The configured source is `data/raw/course/USA500.IDXUSD_1h_2020-07-01_to_2025-06-30_UTC.csv`. Timestamps span2020-07-01 04:00 UTC through2025-07-01 04:00 UTC. Original Task01/P0.1 raw hash `ba78d6bf933f0aca4dfcdedb69454d19aa29bfed84481b6ba1bcccdaf7b1634a`, 29,510 records and2,083,715 bytes were reused; the small course manifest matches its prior hash. No raw rehash or all-OHLC scan. Source stats match P1.1; no apparent source change. No sidecar/source handout or precise vendor document was found in the repository/source folder, so no speculative external identification search was made.

## Three predeclared day comparisons

Dates were fixed before inspecting OHLC. E = [evidence.json](evidence.json); all values/stamps below are original source fields with exact CSV line locators in E. Each day retains six unique OHLC records; volume was omitted and unused.

| ET source day | Around09:30 | Around10:30 | Around11:30 | Around15:30 /16:00 close | Native10:00 label |
|---|---|---|---|---|---|
| 2020-07-08 (-04) |09:00 /10:00 |10:00 /11:00 |11:00 /12:00 |15:00 /16:00; exact16:00 |14:00+00:00, line123 |
| 2023-03-10 (-05) |09:00 /10:00 |10:00 /11:00 |11:00 /12:00 |15:00 /16:00; exact16:00 |15:00+00:00, line15929 |
| 2025-06-03 (-04) |09:00 /10:00 |10:00 /11:00 |11:00 /12:00 |15:00 /16:00; exact16:00 |14:00+00:00, line29065 |

At the :30 boundaries, genuine neighbors are -30/+30 minutes; no exact row exists. The later neighbor is shown only as raw QA, never used as an as-of input. For example, line123 has O3170.437/H3172.149/L3159.637/C3163.137. Under an unverified close-label hypothesis it would end10:00, but under an unverified start-label hypothesis it would cover10:00–11:00 and be unfinished at10:30. Neither hypothesis proves availability. An exact16:00 stamp likewise does not establish an official daily closing value. No half-hour stock bar was fabricated or source bar divided.

One streaming **timestamp-only** calendar pass found zero duplicates/order defects, all labels on whole hours,7,502 labels inside XNYS RTH and22,008 outside;2,240 lie on non-XNYS-session dates. Latest-label distance at2,510 nominal10:30/11:30 study cutoffs is30min for2,509 and90min forone. These are label distances only, not D2 PASS or46/48 model retention. Prior timestamp gap/early-close/DST examples are referenced/reused. Vendor closure/gap semantics remain unknown. The file has no preformation labels; no hourly RMS12/60, daily RMS63, daily momentum, validity masks or48-step windows were built.

## F01 and the separate as-of predicates

Three deterministic synthetic cases in E were validated without real course alignment:

| At hypothetical15:00 cutoff | Period-end age | Publication | Required interpretation |
|---|---|---|---|
| End13:00, available14:00 |120min |Before cutoff |Stale: reject; reused F01 fixture incorrectly accepts availability age60. |
| End14:00, available15:01 |60min |After cutoff |Causally unavailable: reject even though fresh. |
| End14:00, available14:30 |60min |Before cutoff |Eligible on these two predicates only, conditional on stipulated compatible completed semantics. Synthetic, not empirical course PASS. |

Proposed follow-up repair specification, **not implemented**: preserve/document `market_period_start`, `market_period_end`, actual `available_at` and each historical `feature_cutoff`; require compatible completed semantics, `period_end <= cutoff`, `available_at <= cutoff`, and `0 <= cutoff - period_end <=90min`. Select the latest compatible completed eligible observation under the verified source contract. Keep availability-age separate from freshness; reject unknown required timing. Define tie/revision handling from genuine source metadata, never an invented delay. Regression examples must cover the table and90min boundary. `alignment.asof_diagnostic` lines40–55 remains unchanged/INVALID (F01); no production source join or repair was run. Shared complete-hour versus240-RTH-minute sign-off remains blocked.

## Evidence, dependencies and stop

Five focused existing tests passed in1.24s (F01, pointer, non-clearing ledger and external blockers). Three synthetic cases and15 report checks passed validation. Prior P0.2's94 tests and P1.1's22 tests are inherited evidence; no full suite/Ruff rerun. Zero source HTTP calls, no credentials accessed, no installs. New footprint/duration and preservation are recorded in `preservation.json` / mandatory session report.

One P1.2 BLOCKED audit event was appended with `blocks=[]`, `supersedes=[]`: nine total events, seven original blockers,0/40 fitting pairs. All P1.1 uncommitted files and the previous ledger byte prefix are preserved. Branch/HEAD remains `feat/track-a-data-intake` / `bf76774`, upstream0ahead/0behind; no staging/commit/push/integration.

P1.3 stock QA/acquisition requires separate authorization and its stock/formation/actions prerequisites; the unresolved course identity cannot supply a defensible membership construct. P2.4 remains blocked pending source identity, compatible hourly/daily contracts, historical availability, D2/F01 verification and separately audited warmup/retention. No source substitution, numerical-match identification, latency rule or clock amendment was approved.

**Recommended single next action:** review/send the six-question source-owner inquiry drafted in `source_contract.md` and obtain original documentation/metadata. It has not been sent automatically. Decide subsequent package/repair authorization only after reviewing the response.

**STOP AND AWAIT HUMAN REVIEW — NO AUTOMATIC NEXT PACKAGE.**
