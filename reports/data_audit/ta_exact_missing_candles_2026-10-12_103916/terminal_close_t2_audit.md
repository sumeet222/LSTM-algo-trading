# Terminal-close and T2 audit

Original source only: 2020-07-01 through 2025-06-30 ET. Each affected stock-session is below, all with absent terminal candles. Native terminal absence occurs in 15 stock-sessions; adapter interpretation exceptions: 0.

|Stock|Session ET|Terminal start ET|Terminal end ET|UTC interval|Earlier native rows|Latest earlier start ET|Native terminal / retained stub|Diagnosis|
|---|---|---|---|---|---|---|---|---|
|CAT|2021-04-19|2021-04-19T15:30:00-04:00|2021-04-19T16:00:00-04:00|2021-04-19T19:30:00+00:00 → 2021-04-19T20:00:00+00:00|1|2021-04-19T09:30:00-04:00|False / False|SOURCE_ABSENCE|
|CAT|2021-10-25|2021-10-25T15:30:00-04:00|2021-10-25T16:00:00-04:00|2021-10-25T19:30:00+00:00 → 2021-10-25T20:00:00+00:00|1|2021-10-25T09:30:00-04:00|False / False|SOURCE_ABSENCE|
|CAT|2022-01-24|2022-01-24T15:30:00-05:00|2022-01-24T16:00:00-05:00|2022-01-24T20:30:00+00:00 → 2022-01-24T21:00:00+00:00|3|2022-01-24T10:30:00-05:00|False / False|SOURCE_ABSENCE|
|CAT|2022-03-08|2022-03-08T15:30:00-05:00|2022-03-08T16:00:00-05:00|2022-03-08T20:30:00+00:00 → 2022-03-08T21:00:00+00:00|0|none|False / False|SOURCE_ABSENCE|
|JNJ|2021-04-19|2021-04-19T15:30:00-04:00|2021-04-19T16:00:00-04:00|2021-04-19T19:30:00+00:00 → 2021-04-19T20:00:00+00:00|1|2021-04-19T09:30:00-04:00|False / False|SOURCE_ABSENCE|
|JNJ|2021-10-25|2021-10-25T15:30:00-04:00|2021-10-25T16:00:00-04:00|2021-10-25T19:30:00+00:00 → 2021-10-25T20:00:00+00:00|1|2021-10-25T09:30:00-04:00|False / False|SOURCE_ABSENCE|
|JNJ|2022-03-08|2022-03-08T15:30:00-05:00|2022-03-08T16:00:00-05:00|2022-03-08T20:30:00+00:00 → 2022-03-08T21:00:00+00:00|0|none|False / False|SOURCE_ABSENCE|
|JPM|2021-04-19|2021-04-19T15:30:00-04:00|2021-04-19T16:00:00-04:00|2021-04-19T19:30:00+00:00 → 2021-04-19T20:00:00+00:00|1|2021-04-19T09:30:00-04:00|False / False|SOURCE_ABSENCE|
|JPM|2021-10-25|2021-10-25T15:30:00-04:00|2021-10-25T16:00:00-04:00|2021-10-25T19:30:00+00:00 → 2021-10-25T20:00:00+00:00|1|2021-10-25T09:30:00-04:00|False / False|SOURCE_ABSENCE|
|JPM|2022-03-08|2022-03-08T15:30:00-05:00|2022-03-08T16:00:00-05:00|2022-03-08T20:30:00+00:00 → 2022-03-08T21:00:00+00:00|1|2022-03-08T09:30:00-05:00|False / False|SOURCE_ABSENCE|
|WMT|2021-04-19|2021-04-19T15:30:00-04:00|2021-04-19T16:00:00-04:00|2021-04-19T19:30:00+00:00 → 2021-04-19T20:00:00+00:00|1|2021-04-19T09:30:00-04:00|False / False|SOURCE_ABSENCE|
|WMT|2021-10-25|2021-10-25T15:30:00-04:00|2021-10-25T16:00:00-04:00|2021-10-25T19:30:00+00:00 → 2021-10-25T20:00:00+00:00|1|2021-10-25T09:30:00-04:00|False / False|SOURCE_ABSENCE|
|WMT|2022-01-24|2022-01-24T15:30:00-05:00|2022-01-24T16:00:00-05:00|2022-01-24T20:30:00+00:00 → 2022-01-24T21:00:00+00:00|3|2022-01-24T10:30:00-05:00|False / False|SOURCE_ABSENCE|
|WMT|2022-01-26|2022-01-26T15:30:00-05:00|2022-01-26T16:00:00-05:00|2022-01-26T20:30:00+00:00 → 2022-01-26T21:00:00+00:00|11|2022-01-26T14:30:00-05:00|False / False|SOURCE_ABSENCE|
|WMT|2022-03-08|2022-03-08T15:30:00-05:00|2022-03-08T16:00:00-05:00|2022-03-08T20:30:00+00:00 → 2022-03-08T21:00:00+00:00|1|2022-03-08T09:30:00-05:00|False / False|SOURCE_ABSENCE|

All affected sessions are normal 09:30–16:00 ET XNYS sessions. A real earlier native row may exist, but it cannot supply the scheduled daily close under the current rules. A retained genuine terminal stub requires its exact 15:30–16:00 half-hour. No permitted independent daily-close input exists in this original 30Min namespace/config; auxiliary formation/probe/warmup sources are outside this inventory and are not substitutes. For missing terminal keys the existing aggregation emits no terminal stub; this is direct source absence, rather than an adapter dropping a present candle. All 15 terminal stubs are absent. WMT on 2022-01-26 has only two missing source candles (15:00–15:30 and 15:30–16:00 ET), but the terminal half-hour is one of them; an earlier 14:30–15:00 candle cannot supply the scheduled close.

Evidence: [aggregation.py](../../../src/lstm_data/aggregation.py) `aggregate_session_hours`, lines 17–83 (complete constituents required, genuine closing stub retained); [stock_source.py](../../../src/lstm_data/stock_source.py) `StockHistory`, lines 241–283 (daily close uses terminal part, no earlier-close substitution); [stock_features.py](../../../src/lstm_data/stock_features.py), lines 255–267 (T2: preceding 21 daily prices, 20 adjacent signs, at least 19 valid). D2 §3 and D4 §5.2 in the [frozen design](../../../docs/track_a/Track_A_Consolidated_Implementation_Design_Record_v1.2_2026-10-10.md) distinguish complete-hour neural inputs from the daily closing stub.

## Previously evidenced T2-origin effects

|Stock|Original-source T2 failed origins|Inactive warmup T2 failed origins|
|---|---|---|
|AAPL|58|0|
|JPM|220|162|
|JNJ|220|162|
|WMT|278|220|
|CAT|274|216|

Counts are read from the already published [original origin masks](../ta_universe_screen_2026-10-12_092402/original_origin_masks.json) and separately labeled [inactive warmup masks](../ta_universe_screen_2026-10-12_092402/warmup_origin_masks.json); the latter remove startup/prehistory effects but do not replace the original source inventory. The unique warmup T2-failure union is 220; per-stock counts overlap and must not be summed into panel losses. These are origins with a T2 input failure somewhere in their 48-step input window, not missing candles, not necessarily T2-only rejections, and not per-terminal-session causal estimates. An interior missing daily close invalidates two adjacent sign changes when both are in the trailing window, which can exceed the 19/20 guard and propagate through later 48-step windows. No new FT0 calculation was run.

The prior [gap ledger](../ta_data_remed_ft0_001_2026-10-11_195135/gap_cluster_reconciliation.json) records 75 direct 48-step origins and 244 additional propagated losses, totaling 319 after warmup. These effects include several feature dependencies and must not all be attributed to T2. Raw omissions do not establish zero volume, no trades, or a vendor defect. Scientific source and execution HOLDs remain unchanged.
