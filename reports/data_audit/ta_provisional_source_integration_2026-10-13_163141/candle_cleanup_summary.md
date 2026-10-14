# Engineering candle cleanup summary

**ENGINEERING_VIEW_COMPLETE — HUMAN_REVIEW_REQUIRED; SCIENTIFIC_HOLD.**

**89,985 source-observed candles; 0 synthetic insertions; 0 unresolved gaps.** The native archive is already complete. The cleaned engineering dataset is therefore a source-reference view plus a zero-row sparse overlay, without duplicated full-history Parquets.

|Stock|Main genuine|Prehistory genuine|Pre/post gaps|Runs1 /2 /3–11 /12+|Longest|Whole sessions synthetic|Terminal synthetic|
|---|---:|---:|---|---|---:|---:|---:|
|AAPL|16261|1736|0 /0|0 /0 /0 /0|0|0|0|
|COST|16261|1736|0 /0|0 /0 /0 /0|0|0|0|
|CMCSA|16261|1736|0 /0|0 /0 /0 /0|0|0|0|
|SBUX|16261|1736|0 /0|0 /0 /0 /0|0|0|0|
|CME|16261|1736|0 /0|0 /0 /0 /0|0|0|0|

[Every inserted candle](candle_fills.csv) and [every unresolved candle](unresolved_candle_gaps.csv) have complete schemas but zero rows. This is a measured zero, not omitted acquisition. [Summary JSON](candle_cleanup_summary.json), [binding manifest](candle_overlay_binding.json), [profile](../../../configs/track_a_provisional_engineering_v1.json) and [API](../../../docs/track_a/PROVISIONAL_CANDLE_ENGINEERING_API_v1.md).

For injected missing intervals, policy ENGINEERING_CAUSAL_FLAT_ALL_GAPS_v1 accepts any run length, but requires a genuine RTH anchor with end strictly earlier than the missing start, verified same-unit epoch and no use of a previous synthetic candle. Missing first-session anchors or unknown/crossed unit epochs remain unresolved. Completed-interval time is an engineering clock only; actual source publication remains UNKNOWN.

Synthetic OHLC is flat at the genuine close. Volume/trade count/VWAP are null and explicitly unknown; observed zero volume stays observed zero. Wall-clock and scheduled market-clock age are separate; holidays/overnight are not new candles. Long/full-session, opening/terminal and cross-session cases retain masks and genuine-terminal validity=false. No imputation enters targets, daily-close scientific evidence, execution, dividends, publication or SPY.

All materialized rows have is_observed/is_synthetic and engineering_only flags. Even a zero-fill engineering view is rejected by the genuine-source validator; FT0/T2/TG0/P3 trading/P4 fitting activities fail. UniverseSpec provides existing five-name geometry only, not a historical price or modeling permission. Profile, code, source, policy, order and later floor/target/preparation identifiers invalidate caches.

Independent checks compare all89,985 raw OHLCV/trade-count/VWAP rows numerically unchanged, plus early-close/DST controls. A synthetic whole early-close session inserts7 null-volume rows using the preceding genuine terminal close: first wall age2490 minutes versus market ages0,30,…,180. These are hand-controlled software checks, not real-trade assertions.

Scientific G0–G4, actual FT0/48-step/T2/mature-label eligibility and training retention remain HOLD/NOT_MEASURED. All experiments NOT_RUN, neural ledger0/40. Original universe and scientific deferrals are preserved.
