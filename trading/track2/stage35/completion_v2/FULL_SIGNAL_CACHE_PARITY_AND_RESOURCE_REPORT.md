# Full source-only inference: actual parity and resources

Final authority: `audits/full_run_release/FULL_SIGNAL_COVERAGE_REPORT.json`; partition set `audits/signals_release/`. Initial root reports/partitions and `signals_final` are retained superseded witnesses. The first full pass had an incorrect09:32 freeze timestamp for otherwise missing opening inputs. A successor freezes at each stock's **first input-eligible decision**, including explicit sign abstention; a final type-safe datetime guard run preserves the same forecasts. No date/ticker/model was selected based on these outcomes. Counts below are **unique opportunities**, not three-pass summed observations.

|Fold|Sessions|Opportunities|Original forecasts|S2C intents eligible|Classical eligible|
|---|---:|---:|---:|---:|---:|
|F21|252|35220|34401|33666|25304|
|F22|251|35080|31263|30913|19914|
|F23|250|34880|32443|31666|19666|
|F24|252|35100|33004|31947|22673|

All 20 original names,1005 sessions,7014 actual nominal origins and140280 stock/origin opportunities were processed. There are131111 input-eligible main-head/C3 forecasts and9169 explicit unavailable-past-input rows. There are128192 eligible EQUAL andS2C candidates;87,557 ROLLING/EWMA and four-arm matched candidates. Missing classical windows never remove otherwise valid EQUAL/S2C candidates. Unavailable rows retain attempted-decision timestamps/status, not an emitted numeric forecast. The full80 fold/ticker disposition table is in FINAL_COVERAGE_AND_INTEGRITY.json. No future endpoint-completeness condition is applied; late2024 signals keep their calendar endpoints beyond2024 without reading2025 prices.

Cache math reuses original build/native/scaled/assemble. EMA/Wilder hourly ancestry is advanced once from authorized2010 genesis, not rebuilt per opportunity. Missing scheduled slots, original COP mask/recipe and Q2 semantics are retained. Seven M2 contexts use source-matured prior regular-origin observations strictly before each input-day open, preserving the old source-only producer's rule. Annual recipes/weights/C3 are separate; no fitting. Daily batches use four CPU threads, eval and inference_mode, with no state carried between stock/windows. Model output is scale only; sign comes from prior-session reference history.

Predeclared cache-vs-existing-input-producer comparison:12 AAPL/COP keys across F21–F24, normal/opening/overnight/half-day, max tensor difference0 and exact CLOCK equality; elapsed75.540s. Forecast tolerances were fixed before values: atol1e-7, rtol1e-5. All16 frozen H4 forecast keys compare within tolerance, max absolute difference2.61595012666e-09. This is **not archived original OOS forecast parity**: HISTORICAL_PREDICTION_PARITY_NOT_COMPARABLE remains.

Actual source cache construction: 234.193s;509,140 hourly rows and236131 selected minute-anchor rows from227 distinct authorized partitions (174 hourly,53 minute). Extra8-row raw-action shadow uses two of those same files. Cache disk208105716 bytes; final signal metadata/partitions50554023 bytes. Final forward/control pass288.643s, about454.2 valid forecasts/s. Peak RSS was not independently measured; the3GB plan estimate is not a measured claim. PyArrow emitted harmless macOS sysctl CPU-cache warnings; no failed reads or dependency replacement followed.

Each daily parquet has a SHA receipt; cache arrays and source projections have inventories/hashes. RUN_BINDING binds exact signal/cache code, protocol, source plan and cache manifest. Normal-boundary incomplete runs resume from sealed days; an unsealed parquet deliberately refuses and requires review, never silent replacement. Complete runs refuse overwriting their report; use the read-only auditor after completion. Elapsed-time metadata may differ on a fresh run; fixed inputs produce the deterministic numerical tensor/forecast/control values. No raw dataset was duplicated; caches contain derived features and bounded anchor projections. Large local arrays and signal partitions are ignored; small manifests/receipts remain reviewable.

Full inference completed; no resource-limited remainder. Source-only counts/latency diagnostics are not financial results. No historical orders, fills, NAV, P&L, turnover or Sharpe were computed.
