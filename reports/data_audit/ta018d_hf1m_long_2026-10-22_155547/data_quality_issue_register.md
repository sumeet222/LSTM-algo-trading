# Package 018D persistent data-quality issue register

Source mito0o852/OHLCV-1m at 776328445b7ac6e7815ef3a483e9c8ded1eb6d56; namespace HF20_HF1M_LONG_v1. All exact symbols retained, no old data pooling. COMPLETE_WITH_QUALITY_FLAGS is a source-collection status, not training readiness.

## Policy and issue taxonomy

SOURCE: absence, invalid values, zero/stale volume, action/scale uncertainty, identity/coverage unknowns. RECONCILIATION: identical copies collapsed once; all conflicting versions excluded from canonical, every raw version retained. FILL: separate zero-volume price proxies, volume unknown, <=5 minutes as known at completed-hour clock, no overnight/opening/cross-stock carry. AGGREGATION: partial/open/close/volume/stub flags. Strict/moderate/broad are source-coverage standards, never a final model mask. No price or label clipping.

## Preserved March 2026 evidence

018C STOP_QUALITY remains correct under its policy: 226,433 raw rows, 25 conflicting keys/50 rows, 387 absent expected RTH slots, PEP three-minute gap and MRK/WFC missing session opens. This package keeps those rows and flags instead of aborting. See the immutable ta018c_hf20_hf1m_2026-10-22_143400 audit.

## Unresolved human decisions

Actual adjustment/action/dividend/publication semantics and historic issuer/ticker identity remain unverified. No retroactive aliases, inferred split factors, final 15-year selection, feature/target transforms or training are authorized. Missing minutes do not prove no trading. Source comparison is descriptive only.

<!-- MONTH:1992-01 -->

## 1992-01 — 2026-10-22T20:16:27.509068+00:00

RAW 71,122 rows; CANONICAL 71,122; FILL proxies 20,938; hourly 2,002. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 42398, "ACTION_OR_SCALE_JUMP_OVER25PCT": 4, "CAUSAL_PRICE_PROXY": 20938, "MANY_STOCKS_SYNCHRONOUS_GAP": 579, "NO_EXACT_SYMBOL_SOURCE_ROWS": 7}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-01/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1992-02 -->

## 1992-02 — 2026-10-22T20:16:53.975052+00:00

RAW 57,812 rows; CANONICAL 57,812; FILL proxies 20,382; hourly 1,729. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 39875, "ACTION_OR_SCALE_JUMP_OVER25PCT": 4, "CAUSAL_PRICE_PROXY": 20382, "MANY_STOCKS_SYNCHRONOUS_GAP": 764, "NO_EXACT_SYMBOL_SOURCE_ROWS": 7}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-02/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1992-03 -->

## 1992-03 — 2026-10-22T20:17:17.580131+00:00

RAW 61,767 rows; CANONICAL 61,767; FILL proxies 24,598; hourly 2,002. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 51171, "ACTION_OR_SCALE_JUMP_OVER25PCT": 3, "CAUSAL_PRICE_PROXY": 24598, "MANY_STOCKS_SYNCHRONOUS_GAP": 1556, "NO_EXACT_SYMBOL_SOURCE_ROWS": 7}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-03/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1992-04 -->

## 1992-04 — 2026-10-22T20:17:40.161933+00:00

RAW 63,530 rows; CANONICAL 63,530; FILL proxies 22,688; hourly 1,911. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 43566, "ACTION_OR_SCALE_JUMP_OVER25PCT": 2, "CAUSAL_PRICE_PROXY": 22688, "MANY_STOCKS_SYNCHRONOUS_GAP": 901, "NO_EXACT_SYMBOL_SOURCE_ROWS": 7}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-04/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1992-05 -->

## 1992-05 — 2026-10-22T20:18:02.029935+00:00

RAW 58,293 rows; CANONICAL 58,293; FILL proxies 22,629; hourly 1,820. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 44414, "ACTION_OR_SCALE_JUMP_OVER25PCT": 5, "CAUSAL_PRICE_PROXY": 22629, "MANY_STOCKS_SYNCHRONOUS_GAP": 1145, "NO_EXACT_SYMBOL_SOURCE_ROWS": 7}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-05/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1992-06 -->

## 1992-06 — 2026-10-22T20:18:25.111229+00:00

RAW 67,463 rows; CANONICAL 67,463; FILL proxies 22,356; hourly 2,156. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 46895, "ACTION_OR_SCALE_JUMP_OVER25PCT": 3, "CAUSAL_PRICE_PROXY": 22356, "MANY_STOCKS_SYNCHRONOUS_GAP": 1994, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-06/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1992-07 -->

## 1992-07 — 2026-10-22T20:18:49.556592+00:00

RAW 71,248 rows; CANONICAL 71,248; FILL proxies 25,024; hourly 2,156. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 50438, "CAUSAL_PRICE_PROXY": 25024, "MANY_STOCKS_SYNCHRONOUS_GAP": 1482, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-07/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1992-08 -->

## 1992-08 — 2026-10-22T20:19:14.172461+00:00

RAW 60,626 rows; CANONICAL 60,626; FILL proxies 25,096; hourly 2,058. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 55404, "ACTION_OR_SCALE_JUMP_OVER25PCT": 2, "CAUSAL_PRICE_PROXY": 25096, "MANY_STOCKS_SYNCHRONOUS_GAP": 2713, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-08/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1992-09 -->

## 1992-09 — 2026-10-22T20:19:43.783638+00:00

RAW 64,192 rows; CANONICAL 64,192; FILL proxies 24,612; hourly 2,058. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 51929, "CAUSAL_PRICE_PROXY": 24612, "MANY_STOCKS_SYNCHRONOUS_GAP": 2079, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-09/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1992-10 -->

## 1992-10 — 2026-10-22T20:20:11.330108+00:00

RAW 70,802 rows; CANONICAL 70,802; FILL proxies 24,593; hourly 2,156. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 50891, "CAUSAL_PRICE_PROXY": 24593, "MANY_STOCKS_SYNCHRONOUS_GAP": 1544, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-10/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1992-11 -->

## 1992-11 — 2026-10-22T20:20:38.090237+00:00

RAW 64,623 rows; CANONICAL 64,623; FILL proxies 21,626; hourly 1,932. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 44342, "CAUSAL_PRICE_PROXY": 21626, "MANY_STOCKS_SYNCHRONOUS_GAP": 1123, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-11/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1992-12 -->

## 1992-12 — 2026-10-22T20:21:04.528508+00:00

RAW 67,974 rows; CANONICAL 67,974; FILL proxies 22,877; hourly 2,128. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 47117, "CAUSAL_PRICE_PROXY": 22877, "MANY_STOCKS_SYNCHRONOUS_GAP": 1733, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-12/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1993-01 -->

## 1993-01 — 2026-10-22T20:21:27.529194+00:00

RAW 68,650 rows; CANONICAL 68,650; FILL proxies 19,059; hourly 1,960. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 41919, "ACTION_OR_SCALE_JUMP_OVER25PCT": 2, "CAUSAL_PRICE_PROXY": 19059, "MANY_STOCKS_SYNCHRONOUS_GAP": 645, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-01/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1993-02 -->

## 1993-02 — 2026-10-22T20:21:50.490869+00:00

RAW 65,494 rows; CANONICAL 65,494; FILL proxies 18,975; hourly 1,862. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 39636, "ACTION_OR_SCALE_JUMP_OVER25PCT": 2, "CAUSAL_PRICE_PROXY": 18975, "MANY_STOCKS_SYNCHRONOUS_GAP": 668, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-02/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1993-03 -->

## 1993-03 — 2026-10-22T20:22:17.582426+00:00

RAW 73,428 rows; CANONICAL 73,428; FILL proxies 24,826; hourly 2,254. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 53569, "ACTION_OR_SCALE_JUMP_OVER25PCT": 7, "CAUSAL_PRICE_PROXY": 24826, "MANY_STOCKS_SYNCHRONOUS_GAP": 1569, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-03/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1993-04 -->

## 1993-04 — 2026-10-22T20:22:40.884370+00:00

RAW 71,061 rows; CANONICAL 71,061; FILL proxies 20,885; hourly 2,058. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 44988, "ACTION_OR_SCALE_JUMP_OVER25PCT": 6, "CAUSAL_PRICE_PROXY": 20885, "MANY_STOCKS_SYNCHRONOUS_GAP": 874, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-04/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1993-05 -->

## 1993-05 — 2026-10-22T20:23:05.328055+00:00

RAW 65,883 rows; CANONICAL 65,883; FILL proxies 22,364; hourly 1,960. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 43855, "ACTION_OR_SCALE_JUMP_OVER25PCT": 4, "CAUSAL_PRICE_PROXY": 22364, "MANY_STOCKS_SYNCHRONOUS_GAP": 1128, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-05/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1993-06 -->

## 1993-06 — 2026-10-22T20:23:30.357963+00:00

RAW 71,614 rows; CANONICAL 71,614; FILL proxies 25,357; hourly 2,156. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 49882, "ACTION_OR_SCALE_JUMP_OVER25PCT": 1, "CAUSAL_PRICE_PROXY": 25357, "MANY_STOCKS_SYNCHRONOUS_GAP": 1291, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-06/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1993-07 -->

## 1993-07 — 2026-10-22T20:23:55.054071+00:00

RAW 67,305 rows; CANONICAL 67,305; FILL proxies 24,802; hourly 2,058. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 48666, "ACTION_OR_SCALE_JUMP_OVER25PCT": 8, "CAUSAL_PRICE_PROXY": 24802, "MANY_STOCKS_SYNCHRONOUS_GAP": 1362, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-07/qa_receipt.json and partitioned issue tables.

<!-- MONTH:1993-08 -->

## 1993-08 — 2026-10-22T20:24:20.008956+00:00

RAW 70,478 rows; CANONICAL 70,478; FILL proxies 25,758; hourly 2,156. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 51031, "ACTION_OR_SCALE_JUMP_OVER25PCT": 4, "CAUSAL_PRICE_PROXY": 25758, "MANY_STOCKS_SYNCHRONOUS_GAP": 1433, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-08/qa_receipt.json and partitioned issue tables.

<!-- QA_SCHEMA_V2 -->

## QA schema v2 authority

Initial v1 trial outputs/checkpoints are retained. The v2 issue schema correctly reports actual source multiplicity behind synthetic proxies (zero for absent minutes, all raw versions for conflicts). qa_v2 directories and qa_v2_receipt.json are authoritative; raw unchanged. The same deterministic price and volume rules apply.

<!-- MONTH_V2:1992-01 -->

## 1992-01 — 2026-10-22T20:26:00.999660+00:00

RAW 71,122 rows; CANONICAL 71,122; FILL proxies 20,938; hourly 2,002. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 42398, "ACTION_OR_SCALE_JUMP_OVER25PCT": 4, "CAUSAL_PRICE_PROXY": 20938, "MANY_STOCKS_SYNCHRONOUS_GAP": 579, "NO_EXACT_SYMBOL_SOURCE_ROWS": 7}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1992-02 -->

## 1992-02 — 2026-10-22T20:26:13.876514+00:00

RAW 57,812 rows; CANONICAL 57,812; FILL proxies 20,382; hourly 1,729. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 39875, "ACTION_OR_SCALE_JUMP_OVER25PCT": 4, "CAUSAL_PRICE_PROXY": 20382, "MANY_STOCKS_SYNCHRONOUS_GAP": 764, "NO_EXACT_SYMBOL_SOURCE_ROWS": 7}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1992-03 -->

## 1992-03 — 2026-10-22T20:26:25.150406+00:00

RAW 61,767 rows; CANONICAL 61,767; FILL proxies 24,598; hourly 2,002. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 51171, "ACTION_OR_SCALE_JUMP_OVER25PCT": 3, "CAUSAL_PRICE_PROXY": 24598, "MANY_STOCKS_SYNCHRONOUS_GAP": 1556, "NO_EXACT_SYMBOL_SOURCE_ROWS": 7}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-03/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1992-04 -->

## 1992-04 — 2026-10-22T20:26:35.446406+00:00

RAW 63,530 rows; CANONICAL 63,530; FILL proxies 22,688; hourly 1,911. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 43566, "ACTION_OR_SCALE_JUMP_OVER25PCT": 2, "CAUSAL_PRICE_PROXY": 22688, "MANY_STOCKS_SYNCHRONOUS_GAP": 901, "NO_EXACT_SYMBOL_SOURCE_ROWS": 7}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-04/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1992-05 -->

## 1992-05 — 2026-10-22T20:26:45.163184+00:00

RAW 58,293 rows; CANONICAL 58,293; FILL proxies 22,629; hourly 1,820. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 44414, "ACTION_OR_SCALE_JUMP_OVER25PCT": 5, "CAUSAL_PRICE_PROXY": 22629, "MANY_STOCKS_SYNCHRONOUS_GAP": 1145, "NO_EXACT_SYMBOL_SOURCE_ROWS": 7}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-05/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1992-06 -->

## 1992-06 — 2026-10-22T20:26:55.869681+00:00

RAW 67,463 rows; CANONICAL 67,463; FILL proxies 22,356; hourly 2,156. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 46895, "ACTION_OR_SCALE_JUMP_OVER25PCT": 3, "CAUSAL_PRICE_PROXY": 22356, "MANY_STOCKS_SYNCHRONOUS_GAP": 1994, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-06/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1992-07 -->

## 1992-07 — 2026-10-22T20:27:08.510409+00:00

RAW 71,248 rows; CANONICAL 71,248; FILL proxies 25,024; hourly 2,156. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 50438, "CAUSAL_PRICE_PROXY": 25024, "MANY_STOCKS_SYNCHRONOUS_GAP": 1482, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-07/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1992-08 -->

## 1992-08 — 2026-10-22T20:27:24.071638+00:00

RAW 60,626 rows; CANONICAL 60,626; FILL proxies 25,096; hourly 2,058. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 55404, "ACTION_OR_SCALE_JUMP_OVER25PCT": 2, "CAUSAL_PRICE_PROXY": 25096, "MANY_STOCKS_SYNCHRONOUS_GAP": 2713, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-08/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1992-09 -->

## 1992-09 — 2026-10-22T20:27:35.071022+00:00

RAW 64,192 rows; CANONICAL 64,192; FILL proxies 24,612; hourly 2,058. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 51929, "CAUSAL_PRICE_PROXY": 24612, "MANY_STOCKS_SYNCHRONOUS_GAP": 2079, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-09/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1992-10 -->

## 1992-10 — 2026-10-22T20:27:46.345999+00:00

RAW 70,802 rows; CANONICAL 70,802; FILL proxies 24,593; hourly 2,156. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 50891, "CAUSAL_PRICE_PROXY": 24593, "MANY_STOCKS_SYNCHRONOUS_GAP": 1544, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-10/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1992-11 -->

## 1992-11 — 2026-10-22T20:27:59.388041+00:00

RAW 64,623 rows; CANONICAL 64,623; FILL proxies 21,626; hourly 1,932. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 44342, "CAUSAL_PRICE_PROXY": 21626, "MANY_STOCKS_SYNCHRONOUS_GAP": 1123, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-11/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1992-12 -->

## 1992-12 — 2026-10-22T20:28:23.996570+00:00

RAW 67,974 rows; CANONICAL 67,974; FILL proxies 22,877; hourly 2,128. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 47117, "CAUSAL_PRICE_PROXY": 22877, "MANY_STOCKS_SYNCHRONOUS_GAP": 1733, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1992-12/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1993-01 -->

## 1993-01 — 2026-10-22T20:28:42.411193+00:00

RAW 68,650 rows; CANONICAL 68,650; FILL proxies 19,059; hourly 1,960. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 41919, "ACTION_OR_SCALE_JUMP_OVER25PCT": 2, "CAUSAL_PRICE_PROXY": 19059, "MANY_STOCKS_SYNCHRONOUS_GAP": 645, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1993-02 -->

## 1993-02 — 2026-10-22T20:28:58.653587+00:00

RAW 65,494 rows; CANONICAL 65,494; FILL proxies 18,975; hourly 1,862. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 39636, "ACTION_OR_SCALE_JUMP_OVER25PCT": 2, "CAUSAL_PRICE_PROXY": 18975, "MANY_STOCKS_SYNCHRONOUS_GAP": 668, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1993-03 -->

## 1993-03 — 2026-10-22T20:29:11.027699+00:00

RAW 73,428 rows; CANONICAL 73,428; FILL proxies 24,826; hourly 2,254. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 53569, "ACTION_OR_SCALE_JUMP_OVER25PCT": 7, "CAUSAL_PRICE_PROXY": 24826, "MANY_STOCKS_SYNCHRONOUS_GAP": 1569, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-03/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1993-04 -->

## 1993-04 — 2026-10-22T20:29:21.270301+00:00

RAW 71,061 rows; CANONICAL 71,061; FILL proxies 20,885; hourly 2,058. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 44988, "ACTION_OR_SCALE_JUMP_OVER25PCT": 6, "CAUSAL_PRICE_PROXY": 20885, "MANY_STOCKS_SYNCHRONOUS_GAP": 874, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-04/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1993-05 -->

## 1993-05 — 2026-10-22T20:29:32.777236+00:00

RAW 65,883 rows; CANONICAL 65,883; FILL proxies 22,364; hourly 1,960. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 43855, "ACTION_OR_SCALE_JUMP_OVER25PCT": 4, "CAUSAL_PRICE_PROXY": 22364, "MANY_STOCKS_SYNCHRONOUS_GAP": 1128, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-05/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1993-06 -->

## 1993-06 — 2026-10-22T20:29:43.920905+00:00

RAW 71,614 rows; CANONICAL 71,614; FILL proxies 25,357; hourly 2,156. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 49882, "ACTION_OR_SCALE_JUMP_OVER25PCT": 1, "CAUSAL_PRICE_PROXY": 25357, "MANY_STOCKS_SYNCHRONOUS_GAP": 1291, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-06/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1993-07 -->

## 1993-07 — 2026-10-22T20:29:54.309320+00:00

RAW 67,305 rows; CANONICAL 67,305; FILL proxies 24,802; hourly 2,058. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 48666, "ACTION_OR_SCALE_JUMP_OVER25PCT": 8, "CAUSAL_PRICE_PROXY": 24802, "MANY_STOCKS_SYNCHRONOUS_GAP": 1362, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-07/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1993-08 -->

## 1993-08 — 2026-10-22T20:30:06.191306+00:00

RAW 70,478 rows; CANONICAL 70,478; FILL proxies 25,758; hourly 2,156. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 51031, "ACTION_OR_SCALE_JUMP_OVER25PCT": 4, "CAUSAL_PRICE_PROXY": 25758, "MANY_STOCKS_SYNCHRONOUS_GAP": 1433, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-08/qa_v2_receipt.json and partitioned issue tables.

## Historical issuer identity warning — 2026-10-22T20:30:08.426883+00:00

SOURCE/IDENTITY: actual January1992 extract has2,508 exact MA rows. Mastercard announced its IPO inMay2006 ([issuer announcement](https://investor.mastercard.com/investor-news/investor-news-details/2006/MasterCard-Incorporated-Prices-Initial-Public-Offering/default.aspx)). These early rows cannot be assumed to be Mastercard common stock; they could reflect symbol reuse or source mapping. Disposition: preserve all rows, identity unresolved, no retroactive aliases or source corrections. This subset warning does not abort acquisition under018D.

<!-- MONTH_V2:1993-09 -->

## 1993-09 — 2026-10-22T20:30:16.879722+00:00

RAW 68,326 rows; CANONICAL 68,326; FILL proxies 24,993; hourly 2,058. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 47633, "ACTION_OR_SCALE_JUMP_OVER25PCT": 11, "CAUSAL_PRICE_PROXY": 24993, "MANY_STOCKS_SYNCHRONOUS_GAP": 1297, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-09/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1993-10 -->

## 1993-10 — 2026-10-22T20:30:37.241922+00:00

RAW 71,191 rows; CANONICAL 71,191; FILL proxies 24,647; hourly 2,058. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 44839, "ACTION_OR_SCALE_JUMP_OVER25PCT": 8, "CAUSAL_PRICE_PROXY": 24647, "MANY_STOCKS_SYNCHRONOUS_GAP": 913, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-10/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1993-11 -->

## 1993-11 — 2026-10-22T20:30:54.713698+00:00

RAW 67,886 rows; CANONICAL 67,886; FILL proxies 25,245; hourly 2,016. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 45631, "CAUSAL_PRICE_PROXY": 25245, "MANY_STOCKS_SYNCHRONOUS_GAP": 1155, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-11/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1993-12 -->

## 1993-12 — 2026-10-22T20:31:17.582313+00:00

RAW 69,219 rows; CANONICAL 69,219; FILL proxies 27,757; hourly 2,156. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 52337, "ACTION_OR_SCALE_JUMP_OVER25PCT": 6, "CAUSAL_PRICE_PROXY": 27757, "MANY_STOCKS_SYNCHRONOUS_GAP": 1759, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1993-12/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1994-01 -->

## 1994-01 — 2026-10-22T20:31:46.143748+00:00

RAW 71,950 rows; CANONICAL 71,950; FILL proxies 23,321; hourly 2,058. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 44200, "ACTION_OR_SCALE_JUMP_OVER25PCT": 2, "CAUSAL_PRICE_PROXY": 23321, "MANY_STOCKS_SYNCHRONOUS_GAP": 769, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1994-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1994-02 -->

## 1994-02 — 2026-10-22T20:32:02.295749+00:00

RAW 62,970 rows; CANONICAL 62,970; FILL proxies 21,311; hourly 1,862. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 42058, "ACTION_OR_SCALE_JUMP_OVER25PCT": 12, "CAUSAL_PRICE_PROXY": 21311, "MANY_STOCKS_SYNCHRONOUS_GAP": 970, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1994-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1994-03 -->

## 1994-03 — 2026-10-22T20:32:42.694316+00:00

RAW 79,305 rows; CANONICAL 79,305; FILL proxies 25,499; hourly 2,254. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 47959, "ACTION_OR_SCALE_JUMP_OVER25PCT": 2, "CAUSAL_PRICE_PROXY": 25499, "MANY_STOCKS_SYNCHRONOUS_GAP": 850, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1994-03/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:1994-04 -->

## 1994-04 — 2026-10-22T20:33:08.904658+00:00

RAW 64,413 rows; CANONICAL 64,413; FILL proxies 21,317; hourly 1,862. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 39508, "CAUSAL_PRICE_PROXY": 21317, "MANY_STOCKS_SYNCHRONOUS_GAP": 898, "NO_EXACT_SYMBOL_SOURCE_ROWS": 6}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/1994-04/qa_v2_receipt.json and partitioned issue tables.

## Human scope amendment — 2026-10-22T20:33:50.078619+00:00

Active source scope now July2010–March2026 only (189months). Pre-July2010 records above are preserved legacy evidence and excluded from the active completion/coverage assessment. No additional older file will be downloaded or processed. Historical MA issuer warning stays recorded without requiring more pre2010 work.

<!-- MONTH_V2:2010-07 -->

## 2010-07 — 2026-10-22T20:46:37.530670+00:00

RAW 185,759 rows; CANONICAL 185,759; FILL proxies 3,171; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 3300, "CAUSAL_PRICE_PROXY": 3171}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2010-07/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2010-08 -->

## 2010-08 — 2026-10-22T20:47:08.769118+00:00

RAW 189,640 rows; CANONICAL 189,640; FILL proxies 4,661; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 4909, "CAUSAL_PRICE_PROXY": 4661}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2010-08/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2010-09 -->

## 2010-09 — 2026-10-22T20:47:41.424869+00:00

RAW 181,432 rows; CANONICAL 181,432; FILL proxies 3,113; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 3142, "CAUSAL_PRICE_PROXY": 3113}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2010-09/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2010-10 -->

## 2010-10 — 2026-10-22T20:48:12.669923+00:00

RAW 183,993 rows; CANONICAL 183,993; FILL proxies 4,372; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 5233, "CAUSAL_PRICE_PROXY": 4372}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2010-10/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2010-11 -->

## 2010-11 — 2026-10-22T20:48:43.482795+00:00

RAW 184,308 rows; CANONICAL 184,308; FILL proxies 2,600; hourly 2,880. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2763, "CAUSAL_PRICE_PROXY": 2600}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2010-11/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2010-12 -->

## 2010-12 — 2026-10-22T20:49:13.223608+00:00

RAW 192,170 rows; CANONICAL 192,170; FILL proxies 2,651; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2699, "CAUSAL_PRICE_PROXY": 2651}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2010-12/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2011-01 -->

## 2011-01 — 2026-10-22T20:49:44.438990+00:00

RAW 182,510 rows; CANONICAL 182,510; FILL proxies 1,692; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1703, "CAUSAL_PRICE_PROXY": 1692}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2011-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2011-02 -->

## 2011-02 — 2026-10-22T20:50:13.048313+00:00

RAW 171,901 rows; CANONICAL 171,901; FILL proxies 1,565; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1589, "CAUSAL_PRICE_PROXY": 1565}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2011-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2011-03 -->

## 2011-03 — 2026-10-22T20:50:47.029367+00:00

RAW 205,345 rows; CANONICAL 205,345; FILL proxies 1,540; hourly 3,220. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1559, "CAUSAL_PRICE_PROXY": 1540}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2011-03/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2011-04 -->

## 2011-04 — 2026-10-22T20:51:17.731690+00:00

RAW 177,276 rows; CANONICAL 177,276; FILL proxies 2,000; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2014, "CAUSAL_PRICE_PROXY": 2000}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2011-04/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2011-05 -->

## 2011-05 — 2026-10-22T20:51:59.371757+00:00

RAW 180,971 rows; CANONICAL 180,971; FILL proxies 2,108; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2120, "CAUSAL_PRICE_PROXY": 2108}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2011-05/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2011-06 -->

## 2011-06 — 2026-10-22T20:52:40.993450+00:00

RAW 191,663 rows; CANONICAL 191,663; FILL proxies 1,000; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1007, "CAUSAL_PRICE_PROXY": 1000}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2011-06/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2011-07 -->

## 2011-07 — 2026-10-22T20:53:14.331644+00:00

RAW 178,708 rows; CANONICAL 178,708; FILL proxies 1,355; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1398, "CAUSAL_PRICE_PROXY": 1355}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2011-07/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2011-08 -->

## 2011-08 — 2026-10-22T20:53:50.467447+00:00

RAW 213,769 rows; CANONICAL 213,769; FILL proxies 1,034; hourly 3,220. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1041, "CAUSAL_PRICE_PROXY": 1034}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2011-08/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2011-09 -->

## 2011-09 — 2026-10-22T20:54:23.258790+00:00

RAW 190,756 rows; CANONICAL 190,756; FILL proxies 1,230; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1232, "CAUSAL_PRICE_PROXY": 1230}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2011-09/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2011-10 -->

## 2011-10 — 2026-10-22T20:55:03.811351+00:00

RAW 192,351 rows; CANONICAL 192,351; FILL proxies 1,269; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1276, "CAUSAL_PRICE_PROXY": 1269}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2011-10/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2011-11 -->

## 2011-11 — 2026-10-22T20:55:39.897630+00:00

RAW 187,522 rows; CANONICAL 187,522; FILL proxies 1,290; hourly 2,880. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1306, "CAUSAL_PRICE_PROXY": 1290}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2011-11/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2011-12 -->

## 2011-12 — 2026-10-22T20:56:11.765005+00:00

RAW 183,521 rows; CANONICAL 183,521; FILL proxies 2,199; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2239, "CAUSAL_PRICE_PROXY": 2199}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2011-12/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2012-01 -->

## 2012-01 — 2026-10-22T20:56:42.539392+00:00

RAW 178,872 rows; CANONICAL 178,872; FILL proxies 1,769; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2120, "CAUSAL_PRICE_PROXY": 1769}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2012-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2012-02 -->

## 2012-02 — 2026-10-22T20:57:16.249170+00:00

RAW 178,170 rows; CANONICAL 178,170; FILL proxies 2,139; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2199, "CAUSAL_PRICE_PROXY": 2139}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2012-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2012-03 -->

## 2012-03 — 2026-10-22T20:57:50.284289+00:00

RAW 194,146 rows; CANONICAL 194,146; FILL proxies 2,789; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2845, "CAUSAL_PRICE_PROXY": 2789}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2012-03/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2012-04 -->

## 2012-04 — 2026-10-22T20:58:23.495652+00:00

RAW 178,290 rows; CANONICAL 178,290; FILL proxies 2,038; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2049, "CAUSAL_PRICE_PROXY": 2038}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2012-04/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2012-05 -->

## 2012-05 — 2026-10-22T20:59:08.621497+00:00

RAW 194,199 rows; CANONICAL 194,199; FILL proxies 1,807; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1819, "ACTION_OR_SCALE_JUMP_OVER25PCT": 1, "CAUSAL_PRICE_PROXY": 1807}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2012-05/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2012-06 -->

## 2012-06 — 2026-10-22T20:59:45.652844+00:00

RAW 182,167 rows; CANONICAL 182,167; FILL proxies 2,332; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2383, "CAUSAL_PRICE_PROXY": 2332}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2012-06/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2012-07 -->

## 2012-07 — 2026-10-22T21:00:15.266980+00:00

RAW 179,736 rows; CANONICAL 179,736; FILL proxies 2,011; hourly 2,880. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2035, "CAUSAL_PRICE_PROXY": 2011}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2012-07/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2012-08 -->

## 2012-08 — 2026-10-22T21:00:46.451214+00:00

RAW 193,473 rows; CANONICAL 193,473; FILL proxies 4,289; hourly 3,220. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 4384, "ACTION_OR_SCALE_JUMP_OVER25PCT": 1, "CAUSAL_PRICE_PROXY": 4289}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2012-08/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2012-09 -->

## 2012-09 — 2026-10-22T21:01:13.361639+00:00

RAW 165,120 rows; CANONICAL 165,120; FILL proxies 2,381; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2413, "CAUSAL_PRICE_PROXY": 2381}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2012-09/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2012-10 -->

## 2012-10 — 2026-10-22T21:01:42.760373+00:00

RAW 181,636 rows; CANONICAL 181,636; FILL proxies 3,296; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 3348, "CAUSAL_PRICE_PROXY": 3296}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2012-10/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2012-11 -->

## 2012-11 — 2026-10-22T21:02:11.681086+00:00

RAW 177,246 rows; CANONICAL 177,246; FILL proxies 2,854; hourly 2,880. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2927, "CAUSAL_PRICE_PROXY": 2854}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2012-11/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2012-12 -->

## 2012-12 — 2026-10-22T21:02:40.702386+00:00

RAW 168,008 rows; CANONICAL 168,008; FILL proxies 2,991; hourly 2,740. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 3004, "CAUSAL_PRICE_PROXY": 2991}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2012-12/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2013-01 -->

## 2013-01 — 2026-10-22T21:03:12.352497+00:00

RAW 184,967 rows; CANONICAL 184,967; FILL proxies 2,666; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2807, "CAUSAL_PRICE_PROXY": 2666}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2013-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2013-02 -->

## 2013-02 — 2026-10-22T21:03:41.385704+00:00

RAW 163,393 rows; CANONICAL 163,393; FILL proxies 2,181; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2205, "CAUSAL_PRICE_PROXY": 2181}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2013-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2013-03 -->

## 2013-03 — 2026-10-22T21:04:14.306397+00:00

RAW 169,605 rows; CANONICAL 169,605; FILL proxies 3,460; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 3562, "CAUSAL_PRICE_PROXY": 3460}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2013-03/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2013-04 -->

## 2013-04 — 2026-10-22T21:04:46.127615+00:00

RAW 188,156 rows; CANONICAL 188,156; FILL proxies 3,220; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 3297, "CAUSAL_PRICE_PROXY": 3220}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2013-04/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2013-05 -->

## 2013-05 — 2026-10-22T21:05:19.873083+00:00

RAW 192,892 rows; CANONICAL 192,892; FILL proxies 2,557; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2625, "CAUSAL_PRICE_PROXY": 2557}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2013-05/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2013-06 -->

## 2013-06 — 2026-10-22T21:05:51.846556+00:00

RAW 173,620 rows; CANONICAL 173,620; FILL proxies 1,504; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1531, "CAUSAL_PRICE_PROXY": 1504}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2013-06/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2013-07 -->

## 2013-07 — 2026-10-22T21:06:30.856551+00:00

RAW 187,272 rows; CANONICAL 187,272; FILL proxies 2,643; hourly 3,020. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2677, "CAUSAL_PRICE_PROXY": 2643}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2013-07/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2013-08 -->

## 2013-08 — 2026-10-22T21:07:04.369799+00:00

RAW 187,900 rows; CANONICAL 187,900; FILL proxies 3,076; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 4225, "CAUSAL_PRICE_PROXY": 3076}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2013-08/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2013-09 -->

## 2013-09 — 2026-10-22T21:07:46.923929+00:00

RAW 171,819 rows; CANONICAL 171,819; FILL proxies 2,700; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2745, "CAUSAL_PRICE_PROXY": 2700}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2013-09/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2013-10 -->

## 2013-10 — 2026-10-22T21:08:36.558710+00:00

RAW 201,666 rows; CANONICAL 201,666; FILL proxies 3,004; hourly 3,220. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 3077, "CAUSAL_PRICE_PROXY": 3004}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2013-10/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2013-11 -->

## 2013-11 — 2026-10-22T21:09:12.115460+00:00

RAW 168,780 rows; CANONICAL 168,780; FILL proxies 2,958; hourly 2,740. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 3021, "CAUSAL_PRICE_PROXY": 2958}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2013-11/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2013-12 -->

## 2013-12 — 2026-10-22T21:09:41.407563+00:00

RAW 175,047 rows; CANONICAL 175,047; FILL proxies 2,855; hourly 2,880. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2921, "CAUSAL_PRICE_PROXY": 2855}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2013-12/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2014-01 -->

## 2014-01 — 2026-10-22T21:10:11.950388+00:00

RAW 185,936 rows; CANONICAL 185,936; FILL proxies 1,798; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1821, "ACTION_OR_SCALE_JUMP_OVER25PCT": 1, "CAUSAL_PRICE_PROXY": 1798}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2014-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2014-02 -->

## 2014-02 — 2026-10-22T21:10:39.360684+00:00

RAW 167,797 rows; CANONICAL 167,797; FILL proxies 746; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 752, "CAUSAL_PRICE_PROXY": 746}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2014-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2014-03 -->

## 2014-03 — 2026-10-22T21:11:49.927029+00:00

RAW 182,911 rows; CANONICAL 182,911; FILL proxies 895; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 896, "CAUSAL_PRICE_PROXY": 895}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2014-03/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2014-04 -->

## 2014-04 — 2026-10-22T21:12:22.513773+00:00

RAW 184,107 rows; CANONICAL 184,107; FILL proxies 494; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 498, "CAUSAL_PRICE_PROXY": 494}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2014-04/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2014-05 -->

## 2014-05 — 2026-10-22T21:12:52.531687+00:00

RAW 177,905 rows; CANONICAL 177,905; FILL proxies 850; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 850, "CAUSAL_PRICE_PROXY": 850}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2014-05/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2014-06 -->

## 2014-06 — 2026-10-22T21:13:31.527416+00:00

RAW 178,183 rows; CANONICAL 178,183; FILL proxies 1,199; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1212, "ACTION_OR_SCALE_JUMP_OVER25PCT": 1, "CAUSAL_PRICE_PROXY": 1199}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2014-06/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2014-07 -->

## 2014-07 — 2026-10-22T21:14:05.894729+00:00

RAW 188,907 rows; CANONICAL 188,907; FILL proxies 884; hourly 3,020. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 884, "CAUSAL_PRICE_PROXY": 884}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2014-07/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2014-08 -->

## 2014-08 — 2026-10-22T21:14:43.801070+00:00

RAW 179,331 rows; CANONICAL 179,331; FILL proxies 1,385; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1387, "CAUSAL_PRICE_PROXY": 1385}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2014-08/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2014-09 -->

## 2014-09 — 2026-10-22T21:15:24.254105+00:00

RAW 181,024 rows; CANONICAL 181,024; FILL proxies 699; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 701, "CAUSAL_PRICE_PROXY": 699}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2014-09/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2014-10 -->

## 2014-10 — 2026-10-22T21:16:16.104721+00:00

RAW 204,998 rows; CANONICAL 204,998; FILL proxies 264; hourly 3,220. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 446, "CAUSAL_PRICE_PROXY": 264}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2014-10/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2014-11 -->

## 2014-11 — 2026-10-22T21:16:44.417170+00:00

RAW 159,209 rows; CANONICAL 159,209; FILL proxies 814; hourly 2,600. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 823, "CAUSAL_PRICE_PROXY": 814}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2014-11/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2014-12 -->

## 2014-12 — 2026-10-22T21:17:16.803335+00:00

RAW 187,228 rows; CANONICAL 187,228; FILL proxies 880; hourly 3,020. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 887, "CAUSAL_PRICE_PROXY": 880}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2014-12/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2015-01 -->

## 2015-01 — 2026-10-22T21:17:49.129668+00:00

RAW 177,735 rows; CANONICAL 177,735; FILL proxies 922; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 928, "CAUSAL_PRICE_PROXY": 922}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2015-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2015-02 -->

## 2015-02 — 2026-10-22T21:18:22.181478+00:00

RAW 167,126 rows; CANONICAL 167,126; FILL proxies 864; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 866, "CAUSAL_PRICE_PROXY": 864}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2015-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2015-03 -->

## 2015-03 — 2026-10-22T21:18:54.376835+00:00

RAW 190,127 rows; CANONICAL 190,127; FILL proxies 1,026; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1034, "CAUSAL_PRICE_PROXY": 1026}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2015-03/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2015-04 -->

## 2015-04 — 2026-10-22T21:19:28.087364+00:00

RAW 181,583 rows; CANONICAL 181,583; FILL proxies 1,113; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1122, "ACTION_OR_SCALE_JUMP_OVER25PCT": 1, "CAUSAL_PRICE_PROXY": 1113}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2015-04/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2015-05 -->

## 2015-05 — 2026-10-22T21:20:00.204466+00:00

RAW 170,536 rows; CANONICAL 170,536; FILL proxies 1,400; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1404, "CAUSAL_PRICE_PROXY": 1400}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2015-05/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2015-06 -->

## 2015-06 — 2026-10-22T21:20:35.172805+00:00

RAW 186,278 rows; CANONICAL 186,278; FILL proxies 1,396; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1396, "CAUSAL_PRICE_PROXY": 1396}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2015-06/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2015-07 -->

## 2015-07 — 2026-10-22T21:21:10.361505+00:00

RAW 192,280 rows; CANONICAL 192,280; FILL proxies 1,060; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1063, "CAUSAL_PRICE_PROXY": 1060}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2015-07/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2015-08 -->

## 2015-08 — 2026-10-22T21:21:43.485348+00:00

RAW 186,243 rows; CANONICAL 186,243; FILL proxies 1,248; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1290, "ACTION_OR_SCALE_JUMP_OVER25PCT": 1, "CAUSAL_PRICE_PROXY": 1248}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2015-08/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2015-09 -->

## 2015-09 — 2026-10-22T21:22:14.579775+00:00

RAW 181,643 rows; CANONICAL 181,643; FILL proxies 1,732; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1834, "CAUSAL_PRICE_PROXY": 1732}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2015-09/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2015-10 -->

## 2015-10 — 2026-10-22T21:22:45.274671+00:00

RAW 189,034 rows; CANONICAL 189,034; FILL proxies 1,538; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1600, "CAUSAL_PRICE_PROXY": 1538}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2015-10/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2015-11 -->

## 2015-11 — 2026-10-22T21:23:14.461278+00:00

RAW 165,140 rows; CANONICAL 165,140; FILL proxies 1,603; hourly 2,740. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1609, "CAUSAL_PRICE_PROXY": 1603}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2015-11/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2015-12 -->

## 2015-12 — 2026-10-22T21:23:46.870124+00:00

RAW 182,768 rows; CANONICAL 182,768; FILL proxies 1,161; hourly 3,020. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1236, "CAUSAL_PRICE_PROXY": 1161}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2015-12/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2016-01 -->

## 2016-01 — 2026-10-22T21:24:15.347872+00:00

RAW 171,248 rows; CANONICAL 171,248; FILL proxies 359; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 359, "CAUSAL_PRICE_PROXY": 359}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2016-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2016-02 -->

## 2016-02 — 2026-10-22T21:24:45.300149+00:00

RAW 174,698 rows; CANONICAL 174,698; FILL proxies 1,211; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1263, "CAUSAL_PRICE_PROXY": 1211}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2016-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2016-03 -->

## 2016-03 — 2026-10-22T21:25:15.805924+00:00

RAW 186,490 rows; CANONICAL 186,490; FILL proxies 613; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 615, "CAUSAL_PRICE_PROXY": 613}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2016-03/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2016-04 -->

## 2016-04 — 2026-10-22T21:25:47.295961+00:00

RAW 181,397 rows; CANONICAL 181,397; FILL proxies 769; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 772, "CAUSAL_PRICE_PROXY": 769}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2016-04/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2016-05 -->

## 2016-05 — 2026-10-22T21:26:23.637302+00:00

RAW 177,289 rows; CANONICAL 177,289; FILL proxies 736; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 737, "CAUSAL_PRICE_PROXY": 736}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2016-05/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2016-06 -->

## 2016-06 — 2026-10-22T21:27:17.475900+00:00

RAW 189,564 rows; CANONICAL 189,564; FILL proxies 578; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 578, "CAUSAL_PRICE_PROXY": 578}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2016-06/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2016-07 -->

## 2016-07 — 2026-10-22T21:27:46.241079+00:00

RAW 170,780 rows; CANONICAL 170,780; FILL proxies 522; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 522, "CAUSAL_PRICE_PROXY": 522}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2016-07/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2016-08 -->

## 2016-08 — 2026-10-22T21:28:19.008297+00:00

RAW 189,779 rows; CANONICAL 189,779; FILL proxies 1,217; hourly 3,220. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1218, "CAUSAL_PRICE_PROXY": 1217}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2016-08/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2016-09 -->

## 2016-09 — 2026-10-22T21:28:53.198644+00:00

RAW 178,834 rows; CANONICAL 178,834; FILL proxies 455; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 455, "CAUSAL_PRICE_PROXY": 455}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2016-09/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2016-10 -->

## 2016-10 — 2026-10-22T21:29:23.701254+00:00

RAW 179,295 rows; CANONICAL 179,295; FILL proxies 630; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 630, "CAUSAL_PRICE_PROXY": 630}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2016-10/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2016-11 -->

## 2016-11 — 2026-10-22T21:30:00.639863+00:00

RAW 179,281 rows; CANONICAL 179,281; FILL proxies 311; hourly 2,880. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 311, "CAUSAL_PRICE_PROXY": 311}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2016-11/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2016-12 -->

## 2016-12 — 2026-10-22T21:30:56.817058+00:00

RAW 179,525 rows; CANONICAL 179,525; FILL proxies 672; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 672, "CAUSAL_PRICE_PROXY": 672}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2016-12/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2017-01 -->

## 2017-01 — 2026-10-22T21:31:26.069573+00:00

RAW 172,020 rows; CANONICAL 172,020; FILL proxies 445; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 445, "CAUSAL_PRICE_PROXY": 445}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2017-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2017-02 -->

## 2017-02 — 2026-10-22T21:32:07.605464+00:00

RAW 166,560 rows; CANONICAL 166,560; FILL proxies 442; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 444, "CAUSAL_PRICE_PROXY": 442}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2017-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2017-03 -->

## 2017-03 — 2026-10-22T21:32:40.376553+00:00

RAW 197,857 rows; CANONICAL 197,857; FILL proxies 704; hourly 3,220. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 706, "CAUSAL_PRICE_PROXY": 704}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2017-03/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2017-04 -->

## 2017-04 — 2026-10-22T21:33:23.125177+00:00

RAW 164,572 rows; CANONICAL 164,572; FILL proxies 628; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 629, "CAUSAL_PRICE_PROXY": 628}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2017-04/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2017-05 -->

## 2017-05 — 2026-10-22T21:33:54.242952+00:00

RAW 190,738 rows; CANONICAL 190,738; FILL proxies 654; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 656, "CAUSAL_PRICE_PROXY": 654}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2017-05/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2017-06 -->

## 2017-06 — 2026-10-22T21:34:25.959502+00:00

RAW 194,036 rows; CANONICAL 194,036; FILL proxies 423; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 425, "CAUSAL_PRICE_PROXY": 423}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2017-06/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2017-07 -->

## 2017-07 — 2026-10-22T21:34:51.290891+00:00

RAW 173,046 rows; CANONICAL 173,046; FILL proxies 570; hourly 2,740. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 573, "CAUSAL_PRICE_PROXY": 570}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2017-07/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2017-08 -->

## 2017-08 — 2026-10-22T21:35:22.637799+00:00

RAW 199,383 rows; CANONICAL 199,383; FILL proxies 730; hourly 3,220. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 732, "CAUSAL_PRICE_PROXY": 730}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2017-08/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2017-09 -->

## 2017-09 — 2026-10-22T21:35:51.667732+00:00

RAW 172,041 rows; CANONICAL 172,041; FILL proxies 715; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 716, "CAUSAL_PRICE_PROXY": 715}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2017-09/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2017-10 -->

## 2017-10 — 2026-10-22T21:36:24.623156+00:00

RAW 191,231 rows; CANONICAL 191,231; FILL proxies 974; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 974, "CAUSAL_PRICE_PROXY": 974}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2017-10/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2017-11 -->

## 2017-11 — 2026-10-22T21:36:57.326253+00:00

RAW 179,664 rows; CANONICAL 179,664; FILL proxies 763; hourly 2,880. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 764, "CAUSAL_PRICE_PROXY": 763}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2017-11/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2017-12 -->

## 2017-12 — 2026-10-22T21:37:27.395983+00:00

RAW 171,730 rows; CANONICAL 171,730; FILL proxies 1,259; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1265, "CAUSAL_PRICE_PROXY": 1259}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2017-12/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2018-01 -->

## 2018-01 — 2026-10-22T21:37:56.430252+00:00

RAW 188,608 rows; CANONICAL 188,608; FILL proxies 513; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 513, "CAUSAL_PRICE_PROXY": 513}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2018-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2018-02 -->

## 2018-02 — 2026-10-22T21:38:24.088574+00:00

RAW 176,952 rows; CANONICAL 176,952; FILL proxies 200; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 202, "CAUSAL_PRICE_PROXY": 200}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2018-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2018-03 -->

## 2018-03 — 2026-10-22T21:38:53.032618+00:00

RAW 188,894 rows; CANONICAL 188,894; FILL proxies 147; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 149, "CAUSAL_PRICE_PROXY": 147}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2018-03/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2018-04 -->

## 2018-04 — 2026-10-22T21:39:23.457962+00:00

RAW 191,356 rows; CANONICAL 191,356; FILL proxies 198; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 203, "CAUSAL_PRICE_PROXY": 198}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2018-04/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2018-05 -->

## 2018-05 — 2026-10-22T21:39:58.749763+00:00

RAW 193,048 rows; CANONICAL 193,048; FILL proxies 502; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 510, "CAUSAL_PRICE_PROXY": 502}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2018-05/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2018-06 -->

## 2018-06 — 2026-10-22T21:40:27.690665+00:00

RAW 187,361 rows; CANONICAL 187,361; FILL proxies 477; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 483, "CAUSAL_PRICE_PROXY": 477}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2018-06/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2018-07 -->

## 2018-07 — 2026-10-22T21:40:59.647993+00:00

RAW 184,783 rows; CANONICAL 184,783; FILL proxies 436; hourly 2,880. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 445, "CAUSAL_PRICE_PROXY": 436}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2018-07/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2018-08 -->

## 2018-08 — 2026-10-22T21:41:28.901928+00:00

RAW 202,793 rows; CANONICAL 202,793; FILL proxies 719; hourly 3,220. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 820, "CAUSAL_PRICE_PROXY": 719}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2018-08/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2018-09 -->

## 2018-09 — 2026-10-22T21:41:55.546139+00:00

RAW 170,437 rows; CANONICAL 170,437; FILL proxies 259; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 265, "CAUSAL_PRICE_PROXY": 259}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2018-09/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2018-10 -->

## 2018-10 — 2026-10-22T21:42:23.908642+00:00

RAW 213,171 rows; CANONICAL 213,171; FILL proxies 76; hourly 3,220. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 81, "CAUSAL_PRICE_PROXY": 76}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2018-10/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2018-11 -->

## 2018-11 — 2026-10-22T21:42:52.191903+00:00

RAW 187,703 rows; CANONICAL 187,703; FILL proxies 98; hourly 2,880. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 101, "CAUSAL_PRICE_PROXY": 98}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2018-11/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2018-12 -->

## 2018-12 — 2026-10-22T21:43:19.816095+00:00

RAW 172,158 rows; CANONICAL 172,158; FILL proxies 16; hourly 2,600. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 16, "CAUSAL_PRICE_PROXY": 16}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2018-12/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2019-01 -->

## 2019-01 — 2026-10-22T21:43:48.439070+00:00

RAW 194,282 rows; CANONICAL 194,282; FILL proxies 103; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 106, "CAUSAL_PRICE_PROXY": 103}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2019-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2019-02 -->

## 2019-02 — 2026-10-22T21:44:15.128127+00:00

RAW 169,453 rows; CANONICAL 169,453; FILL proxies 263; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 274, "CAUSAL_PRICE_PROXY": 263}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2019-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2019-03 -->

## 2019-03 — 2026-10-22T21:44:45.468007+00:00

RAW 189,065 rows; CANONICAL 189,065; FILL proxies 114; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 116, "CAUSAL_PRICE_PROXY": 114}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2019-03/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2019-04 -->

## 2019-04 — 2026-10-22T21:45:15.466314+00:00

RAW 190,470 rows; CANONICAL 190,470; FILL proxies 445; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 448, "CAUSAL_PRICE_PROXY": 445}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2019-04/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2019-05 -->

## 2019-05 — 2026-10-22T21:45:47.654973+00:00

RAW 200,196 rows; CANONICAL 200,196; FILL proxies 323; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 327, "CAUSAL_PRICE_PROXY": 323}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2019-05/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2019-06 -->

## 2019-06 — 2026-10-22T21:46:15.696545+00:00

RAW 179,237 rows; CANONICAL 179,237; FILL proxies 446; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 452, "CAUSAL_PRICE_PROXY": 446}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2019-06/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2019-07 -->

## 2019-07 — 2026-10-22T21:46:44.351852+00:00

RAW 193,160 rows; CANONICAL 193,160; FILL proxies 568; hourly 3,020. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 574, "CAUSAL_PRICE_PROXY": 568}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2019-07/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2019-08 -->

## 2019-08 — 2026-10-22T21:47:15.278232+00:00

RAW 200,063 rows; CANONICAL 200,063; FILL proxies 573; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 741, "CAUSAL_PRICE_PROXY": 573, "MANY_STOCKS_SYNCHRONOUS_GAP": 9}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2019-08/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2019-09 -->

## 2019-09 — 2026-10-22T21:47:45.954194+00:00

RAW 175,068 rows; CANONICAL 175,068; FILL proxies 621; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 628, "CAUSAL_PRICE_PROXY": 621}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2019-09/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2019-10 -->

## 2019-10 — 2026-10-22T21:48:18.307249+00:00

RAW 205,204 rows; CANONICAL 205,204; FILL proxies 882; hourly 3,220. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 918, "CAUSAL_PRICE_PROXY": 882}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2019-10/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2019-11 -->

## 2019-11 — 2026-10-22T21:48:45.526523+00:00

RAW 172,627 rows; CANONICAL 172,627; FILL proxies 815; hourly 2,740. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 819, "CAUSAL_PRICE_PROXY": 815}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2019-11/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2019-12 -->

## 2019-12 — 2026-10-22T21:49:21.062911+00:00

RAW 182,494 rows; CANONICAL 182,494; FILL proxies 923; hourly 2,880. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 927, "CAUSAL_PRICE_PROXY": 923}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2019-12/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2020-01 -->

## 2020-01 — 2026-10-22T21:49:55.395299+00:00

RAW 200,881 rows; CANONICAL 200,881; FILL proxies 402; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 440, "CAUSAL_PRICE_PROXY": 402}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2020-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2020-02 -->

## 2020-02 — 2026-10-22T21:50:34.275341+00:00

RAW 185,281 rows; CANONICAL 185,281; FILL proxies 390; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 392, "CAUSAL_PRICE_PROXY": 390}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2020-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2020-03 -->

## 2020-03 — 2026-10-22T21:51:13.090760+00:00

RAW 245,272 rows; CANONICAL 245,272; FILL proxies 29; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1221, "ACTION_OR_SCALE_JUMP_OVER25PCT": 1, "CAUSAL_PRICE_PROXY": 29, "MANY_STOCKS_SYNCHRONOUS_GAP": 56}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2020-03/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2020-04 -->

## 2020-04 — 2026-10-22T21:51:45.266374+00:00

RAW 227,972 rows; CANONICAL 227,972; FILL proxies 179; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 179, "CAUSAL_PRICE_PROXY": 179}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2020-04/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2020-05 -->

## 2020-05 — 2026-10-22T21:52:17.711424+00:00

RAW 204,552 rows; CANONICAL 204,552; FILL proxies 299; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 299, "CAUSAL_PRICE_PROXY": 299}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2020-05/qa_v2_receipt.json and partitioned issue tables.

## March 2020 synchronous gaps — 2026-10-22T21:52:30.846315+00:00

The 56 synchronous missing-minute positions align with the four market-wide halts documented in the [NYSE working-group report](https://www.nyse.com/publicdocs/nyse/markets/nyse/Report_of_the_Market-Wide_Circuit_Breaker_Working_Group.pdf), pages 5–6. This is an inference from matching dates and intervals, not independent certification of source prices or volumes. All absence flags and raw observations remain unchanged; no halt prices or zero traded volumes are invented. Long gaps remain unfilled. Future eligibility must distinguish market structure from feed failure.

|Date|Official halt ET|Official reopening ET|Observed full-minute absence ET|Slots|
|---|---|---|---|---:|
|2020-03-09|09:34:13|09:49:13|09:35–09:48|14|
|2020-03-12|09:35:44|09:50:44|09:36–09:49|14|
|2020-03-16|09:30:01|09:45:01|09:31–09:44|14|
|2020-03-18|12:56:17|13:11:17|12:57–13:10|14|

Machine-readable context: market_halt_context_2020_03.json. No source, repair or candidate-mask change.

<!-- MONTH_V2:2020-06 -->

## 2020-06 — 2026-10-22T21:52:56.552006+00:00

RAW 229,026 rows; CANONICAL 229,026; FILL proxies 229; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 229, "CAUSAL_PRICE_PROXY": 229}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2020-06/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2020-07 -->

## 2020-07 — 2026-10-22T21:53:41.499667+00:00

RAW 223,899 rows; CANONICAL 223,899; FILL proxies 283; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 284, "CAUSAL_PRICE_PROXY": 283}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2020-07/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2020-08 -->

## 2020-08 — 2026-10-22T21:54:18.005089+00:00

RAW 205,964 rows; CANONICAL 205,964; FILL proxies 834; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 841, "ACTION_OR_SCALE_JUMP_OVER25PCT": 2, "CAUSAL_PRICE_PROXY": 834}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2020-08/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2020-09 -->

## 2020-09 — 2026-10-22T21:54:59.834469+00:00

RAW 217,749 rows; CANONICAL 217,749; FILL proxies 262; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 265, "CAUSAL_PRICE_PROXY": 262}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2020-09/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2020-10 -->

## 2020-10 — 2026-10-22T21:55:38.584405+00:00

RAW 226,542 rows; CANONICAL 226,542; FILL proxies 799; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 803, "CAUSAL_PRICE_PROXY": 799}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2020-10/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2020-11 -->

## 2020-11 — 2026-10-22T21:56:07.256255+00:00

RAW 205,966 rows; CANONICAL 205,966; FILL proxies 1,029; hourly 2,740. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1036, "CAUSAL_PRICE_PROXY": 1029}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2020-11/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2020-12 -->

## 2020-12 — 2026-10-22T21:56:39.499904+00:00

RAW 214,529 rows; CANONICAL 214,282; FILL proxies 1,350; hourly 3,020. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1248, "CAUSAL_PRICE_PROXY": 1350, "CONFLICTING_DUPLICATE": 247}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2020-12/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2021-01 -->

## 2021-01 — 2026-10-22T21:57:10.113079+00:00

RAW 200,269 rows; CANONICAL 200,269; FILL proxies 748; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 748, "CAUSAL_PRICE_PROXY": 748}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2021-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2021-02 -->

## 2021-02 — 2026-10-22T21:57:45.677270+00:00

RAW 193,948 rows; CANONICAL 193,948; FILL proxies 690; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 692, "CAUSAL_PRICE_PROXY": 690}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2021-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2021-03 -->

## 2021-03 — 2026-10-22T21:58:24.645764+00:00

RAW 234,745 rows; CANONICAL 234,745; FILL proxies 527; hourly 3,220. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1231, "CAUSAL_PRICE_PROXY": 527}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2021-03/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2021-04 -->

## 2021-04 — 2026-10-22T21:58:57.896871+00:00

RAW 205,737 rows; CANONICAL 205,737; FILL proxies 1,010; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1018, "CAUSAL_PRICE_PROXY": 1010}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2021-04/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2021-05 -->

## 2021-05 — 2026-10-22T21:59:31.812986+00:00

RAW 193,708 rows; CANONICAL 193,708; FILL proxies 850; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1023, "CAUSAL_PRICE_PROXY": 850, "MANY_STOCKS_SYNCHRONOUS_GAP": 5}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2021-05/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2021-06 -->

## 2021-06 — 2026-10-22T22:00:05.130603+00:00

RAW 207,165 rows; CANONICAL 207,165; FILL proxies 1,339; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1825, "CAUSAL_PRICE_PROXY": 1339}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2021-06/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2021-07 -->

## 2021-07 — 2026-10-22T22:00:37.713122+00:00

RAW 202,899 rows; CANONICAL 202,899; FILL proxies 1,220; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1505, "CAUSAL_PRICE_PROXY": 1220}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2021-07/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2021-08 -->

## 2021-08 — 2026-10-22T22:01:11.967367+00:00

RAW 203,759 rows; CANONICAL 203,755; FILL proxies 1,623; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2546, "CAUSAL_PRICE_PROXY": 1623, "CONFLICTING_DUPLICATE": 4}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2021-08/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2021-09 -->

## 2021-09 — 2026-10-22T22:01:45.611473+00:00

RAW 199,541 rows; CANONICAL 199,539; FILL proxies 1,047; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1218, "CAUSAL_PRICE_PROXY": 1047, "CONFLICTING_DUPLICATE": 2}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2021-09/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2021-10 -->

## 2021-10 — 2026-10-22T22:02:22.578302+00:00

RAW 205,030 rows; CANONICAL 205,030; FILL proxies 1,343; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1485, "CAUSAL_PRICE_PROXY": 1343}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2021-10/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2021-11 -->

## 2021-11 — 2026-10-22T22:02:59.201577+00:00

RAW 204,498 rows; CANONICAL 204,496; FILL proxies 1,248; hourly 2,880. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1250, "CAUSAL_PRICE_PROXY": 1248, "CONFLICTING_DUPLICATE": 2}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2021-11/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2021-12 -->

## 2021-12 — 2026-10-22T22:03:39.186286+00:00

RAW 213,272 rows; CANONICAL 213,272; FILL proxies 1,380; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1382, "CAUSAL_PRICE_PROXY": 1380}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2021-12/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2022-01 -->

## 2022-01 — 2026-10-22T22:04:22.915891+00:00

RAW 203,956 rows; CANONICAL 203,956; FILL proxies 468; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 469, "CAUSAL_PRICE_PROXY": 468}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2022-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2022-02 -->

## 2022-02 — 2026-10-22T22:05:11.309125+00:00

RAW 190,279 rows; CANONICAL 190,279; FILL proxies 510; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 515, "CAUSAL_PRICE_PROXY": 510}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2022-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2022-03 -->

## 2022-03 — 2026-10-22T22:05:55.162038+00:00

RAW 228,298 rows; CANONICAL 228,298; FILL proxies 961; hourly 3,220. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 975, "CAUSAL_PRICE_PROXY": 961}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2022-03/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2022-04 -->

## 2022-04 — 2026-10-22T22:06:34.223916+00:00

RAW 194,301 rows; CANONICAL 194,301; FILL proxies 891; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 891, "CAUSAL_PRICE_PROXY": 891}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2022-04/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2022-05 -->

## 2022-05 — 2026-10-22T22:07:13.794737+00:00

RAW 207,507 rows; CANONICAL 207,507; FILL proxies 430; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 432, "CAUSAL_PRICE_PROXY": 430}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2022-05/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2022-06 -->

## 2022-06 — 2026-10-22T22:07:52.970605+00:00

RAW 209,059 rows; CANONICAL 209,059; FILL proxies 737; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 747, "ACTION_OR_SCALE_JUMP_OVER25PCT": 1, "CAUSAL_PRICE_PROXY": 737}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2022-06/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2022-07 -->

## 2022-07 — 2026-10-22T22:08:29.866675+00:00

RAW 195,828 rows; CANONICAL 195,828; FILL proxies 791; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 803, "CAUSAL_PRICE_PROXY": 791}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2022-07/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2022-08 -->

## 2022-08 — 2026-10-22T22:09:16.482149+00:00

RAW 219,430 rows; CANONICAL 219,430; FILL proxies 1,224; hourly 3,220. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2673, "ACTION_OR_SCALE_JUMP_OVER25PCT": 1, "CAUSAL_PRICE_PROXY": 1224, "MANY_STOCKS_SYNCHRONOUS_GAP": 92}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2022-08/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2022-09 -->

## 2022-09 — 2026-10-22T22:09:52.192704+00:00

RAW 200,486 rows; CANONICAL 200,472; FILL proxies 586; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 6645, "CAUSAL_PRICE_PROXY": 586, "CONFLICTING_DUPLICATE": 14, "MANY_STOCKS_SYNCHRONOUS_GAP": 304}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2022-09/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2022-10 -->

## 2022-10 — 2026-10-22T22:10:35.503046+00:00

RAW 213,152 rows; CANONICAL 213,150; FILL proxies 600; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 613, "CAUSAL_PRICE_PROXY": 600, "CONFLICTING_DUPLICATE": 2}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2022-10/qa_v2_receipt.json and partitioned issue tables.

## September 2022 shared absence detail — 2026-10-22T22:10:53.774099+00:00

304 expected cohort minute positions have fewer than ten present names, on September8/9/28/30; 35 stock-hour/stub bins contain zero genuine minutes and remain missing. Per-date first/last hulls are not uninterrupted-gap claims. Source cause remains unresolved; this is no automatic market-halt or corrupt-provider assertion. See large_shared_gap_2022_09.json plus the complete per-minute ledger. Acquisition continues with flags; no fabricated full hours or cohort/window change.

<!-- MONTH_V2:2022-11 -->

## 2022-11 — 2026-10-22T22:11:16.567683+00:00

RAW 203,510 rows; CANONICAL 203,510; FILL proxies 921; hourly 2,880. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 937, "CAUSAL_PRICE_PROXY": 921}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2022-11/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2022-12 -->

## 2022-12 — 2026-10-22T22:11:52.123013+00:00

RAW 203,488 rows; CANONICAL 203,486; FILL proxies 814; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 815, "CAUSAL_PRICE_PROXY": 814, "CONFLICTING_DUPLICATE": 2}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2022-12/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2023-01 -->

## 2023-01 — 2026-10-22T22:12:48.057546+00:00

RAW 201,487 rows; CANONICAL 201,483; FILL proxies 883; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 924, "CAUSAL_PRICE_PROXY": 883, "CONFLICTING_DUPLICATE": 4}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2023-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2023-02 -->

## 2023-02 — 2026-10-22T22:13:27.179289+00:00

RAW 187,975 rows; CANONICAL 187,975; FILL proxies 819; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 854, "CAUSAL_PRICE_PROXY": 819}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2023-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2023-03 -->

## 2023-03 — 2026-10-22T22:14:09.682717+00:00

RAW 204,485 rows; CANONICAL 204,485; FILL proxies 750; hourly 3,220. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 20755, "CAUSAL_PRICE_PROXY": 750, "MANY_STOCKS_SYNCHRONOUS_GAP": 750}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2023-03/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2023-04 -->

## 2023-04 — 2026-10-22T22:14:47.389681+00:00

RAW 187,867 rows; CANONICAL 187,863; FILL proxies 1,094; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1097, "CAUSAL_PRICE_PROXY": 1094, "CONFLICTING_DUPLICATE": 4}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2023-04/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2023-05 -->

## 2023-05 — 2026-10-22T22:15:31.130290+00:00

RAW 217,890 rows; CANONICAL 217,872; FILL proxies 1,154; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1176, "CAUSAL_PRICE_PROXY": 1154, "CONFLICTING_DUPLICATE": 18}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2023-05/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2023-06 -->

## 2023-06 — 2026-10-22T22:16:07.707684+00:00

RAW 207,964 rows; CANONICAL 207,954; FILL proxies 947; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 976, "CAUSAL_PRICE_PROXY": 947, "CONFLICTING_DUPLICATE": 10, "MANY_STOCKS_SYNCHRONOUS_GAP": 4}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2023-06/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2023-07 -->

## 2023-07 — 2026-10-22T22:16:37.383648+00:00

RAW 196,278 rows; CANONICAL 196,256; FILL proxies 1,340; hourly 2,740. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1348, "CAUSAL_PRICE_PROXY": 1340, "CONFLICTING_DUPLICATE": 22}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2023-07/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2023-08 -->

## 2023-08 — 2026-10-22T22:17:14.869732+00:00

RAW 223,864 rows; CANONICAL 223,860; FILL proxies 1,711; hourly 3,220. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1805, "CAUSAL_PRICE_PROXY": 1711, "CONFLICTING_DUPLICATE": 4}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2023-08/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2023-09 -->

## 2023-09 — 2026-10-22T22:17:48.432464+00:00

RAW 190,594 rows; CANONICAL 190,594; FILL proxies 1,831; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1883, "CAUSAL_PRICE_PROXY": 1831}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2023-09/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2023-10 -->

## 2023-10 — 2026-10-22T22:18:22.244266+00:00

RAW 216,119 rows; CANONICAL 216,119; FILL proxies 1,754; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1790, "CAUSAL_PRICE_PROXY": 1754}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2023-10/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2023-11 -->

## 2023-11 — 2026-10-22T22:18:53.207951+00:00

RAW 198,319 rows; CANONICAL 198,319; FILL proxies 1,349; hourly 2,880. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1366, "CAUSAL_PRICE_PROXY": 1349}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2023-11/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2023-12 -->

## 2023-12 — 2026-10-22T22:19:25.412285+00:00

RAW 190,880 rows; CANONICAL 190,880; FILL proxies 1,294; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1329, "CAUSAL_PRICE_PROXY": 1294}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2023-12/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2024-01 -->

## 2024-01 — 2026-10-22T22:19:56.480535+00:00

RAW 211,387 rows; CANONICAL 211,387; FILL proxies 1,114; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1114, "CAUSAL_PRICE_PROXY": 1114}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2024-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2024-02 -->

## 2024-02 — 2026-10-22T22:20:48.587639+00:00

RAW 195,412 rows; CANONICAL 195,378; FILL proxies 1,887; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1934, "CAUSAL_PRICE_PROXY": 1887, "CONFLICTING_DUPLICATE": 34}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2024-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2024-03 -->

## 2024-03 — 2026-10-22T22:21:26.604175+00:00

RAW 194,793 rows; CANONICAL 194,771; FILL proxies 1,446; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1439, "CAUSAL_PRICE_PROXY": 1446, "CONFLICTING_DUPLICATE": 22}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2024-03/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2024-04 -->

## 2024-04 — 2026-10-22T22:22:04.117257+00:00

RAW 215,911 rows; CANONICAL 215,869; FILL proxies 1,655; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1681, "CAUSAL_PRICE_PROXY": 1655, "CONFLICTING_DUPLICATE": 42}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2024-04/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2024-05 -->

## 2024-05 — 2026-10-22T22:22:37.975825+00:00

RAW 209,346 rows; CANONICAL 209,334; FILL proxies 1,973; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 2023, "CAUSAL_PRICE_PROXY": 1973, "CONFLICTING_DUPLICATE": 12}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2024-05/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2024-06 -->

## 2024-06 — 2026-10-22T22:23:09.054198+00:00

RAW 180,614 rows; CANONICAL 180,588; FILL proxies 859; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 905, "CAUSAL_PRICE_PROXY": 859, "CONFLICTING_DUPLICATE": 26}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2024-06/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2024-07 -->

## 2024-07 — 2026-10-22T22:23:44.731481+00:00

RAW 215,149 rows; CANONICAL 215,131; FILL proxies 1,115; hourly 3,020. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1147, "ACTION_OR_SCALE_JUMP_OVER25PCT": 1, "CAUSAL_PRICE_PROXY": 1115, "CONFLICTING_DUPLICATE": 18}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2024-07/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2024-08 -->

## 2024-08 — 2026-10-22T22:24:15.700191+00:00

RAW 219,159 rows; CANONICAL 219,145; FILL proxies 1,577; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1591, "CAUSAL_PRICE_PROXY": 1577, "CONFLICTING_DUPLICATE": 14}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2024-08/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2024-09 -->

## 2024-09 — 2026-10-22T22:24:43.814970+00:00

RAW 197,389 rows; CANONICAL 197,362; FILL proxies 701; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 691, "CAUSAL_PRICE_PROXY": 701, "CONFLICTING_DUPLICATE": 27}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2024-09/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2024-10 -->

## 2024-10 — 2026-10-22T22:25:30.131790+00:00

RAW 230,345 rows; CANONICAL 230,249; FILL proxies 1,150; hourly 3,220. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1139, "CAUSAL_PRICE_PROXY": 1150, "CONFLICTING_DUPLICATE": 96}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2024-10/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2024-11 -->

## 2024-11 — 2026-10-22T22:26:07.187039+00:00

RAW 178,552 rows; CANONICAL 178,544; FILL proxies 867; hourly 2,740. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 15556, "CAUSAL_PRICE_PROXY": 867, "CONFLICTING_DUPLICATE": 8, "MANY_STOCKS_SYNCHRONOUS_GAP": 770}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2024-11/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2024-12 -->

## 2024-12 — 2026-10-22T22:26:59.143651+00:00

RAW 206,480 rows; CANONICAL 206,454; FILL proxies 1,517; hourly 2,880. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1943, "CAUSAL_PRICE_PROXY": 1517, "CONFLICTING_DUPLICATE": 26}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2024-12/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2025-01 -->

## 2025-01 — 2026-10-22T22:27:31.574398+00:00

RAW 207,447 rows; CANONICAL 207,426; FILL proxies 626; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 625, "CAUSAL_PRICE_PROXY": 626, "CONFLICTING_DUPLICATE": 21}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2025-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2025-02 -->

## 2025-02 — 2026-10-22T22:28:03.509825+00:00

RAW 193,081 rows; CANONICAL 193,058; FILL proxies 1,053; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1065, "CAUSAL_PRICE_PROXY": 1053, "CONFLICTING_DUPLICATE": 23}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2025-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2025-03 -->

## 2025-03 — 2026-10-22T22:28:37.717285+00:00

RAW 213,101 rows; CANONICAL 213,081; FILL proxies 810; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 807, "CAUSAL_PRICE_PROXY": 810, "CONFLICTING_DUPLICATE": 20}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2025-03/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2025-04 -->

## 2025-04 — 2026-10-22T22:29:14.323867+00:00

RAW 226,073 rows; CANONICAL 226,053; FILL proxies 615; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 611, "CAUSAL_PRICE_PROXY": 615, "CONFLICTING_DUPLICATE": 20}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2025-04/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2025-05 -->

## 2025-05 — 2026-10-22T22:29:47.091153+00:00

RAW 216,237 rows; CANONICAL 216,221; FILL proxies 1,173; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1170, "CAUSAL_PRICE_PROXY": 1173, "CONFLICTING_DUPLICATE": 16}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2025-05/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2025-06 -->

## 2025-06 — 2026-10-22T22:30:24.608836+00:00

RAW 203,624 rows; CANONICAL 203,620; FILL proxies 1,302; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1331, "CAUSAL_PRICE_PROXY": 1302, "CONFLICTING_DUPLICATE": 4}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2025-06/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2025-07 -->

## 2025-07 — 2026-10-22T22:30:56.417329+00:00

RAW 217,772 rows; CANONICAL 217,730; FILL proxies 1,378; hourly 3,020. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1363, "CAUSAL_PRICE_PROXY": 1378, "CONFLICTING_DUPLICATE": 42}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2025-07/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2025-08 -->

## 2025-08 — 2026-10-22T22:31:31.709017+00:00

RAW 205,552 rows; CANONICAL 205,552; FILL proxies 1,518; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1526, "CAUSAL_PRICE_PROXY": 1518}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2025-08/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2025-09 -->

## 2025-09 — 2026-10-22T22:32:08.783350+00:00

RAW 208,876 rows; CANONICAL 208,876; FILL proxies 1,377; hourly 2,940. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1386, "CAUSAL_PRICE_PROXY": 1377}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2025-09/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2025-10 -->

## 2025-10 — 2026-10-22T22:32:55.599224+00:00

RAW 238,126 rows; CANONICAL 238,126; FILL proxies 1,043; hourly 3,220. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1044, "ACTION_OR_SCALE_JUMP_OVER25PCT": 1, "CAUSAL_PRICE_PROXY": 1043}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2025-10/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2025-11 -->

## 2025-11 — 2026-10-22T22:33:47.517688+00:00

RAW 192,059 rows; CANONICAL 192,059; FILL proxies 178; hourly 2,600. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 178, "CAUSAL_PRICE_PROXY": 178}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2025-11/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2025-12 -->

## 2025-12 — 2026-10-22T22:34:20.826103+00:00

RAW 211,816 rows; CANONICAL 211,816; FILL proxies 1,025; hourly 3,020. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 1027, "CAUSAL_PRICE_PROXY": 1025}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2025-12/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2026-01 -->

## 2026-01 — 2026-10-22T22:34:56.075377+00:00

RAW 209,394 rows; CANONICAL 209,394; FILL proxies 240; hourly 2,800. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 241, "CAUSAL_PRICE_PROXY": 240}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2026-01/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2026-02 -->

## 2026-02 — 2026-10-22T22:35:35.648746+00:00

RAW 195,668 rows; CANONICAL 195,668; FILL proxies 409; hourly 2,660. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 411, "CAUSAL_PRICE_PROXY": 409}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2026-02/qa_v2_receipt.json and partitioned issue tables.

<!-- MONTH_V2:2026-03 -->

## 2026-03 — 2026-10-22T22:35:55.271473+00:00

RAW 226,433 rows; CANONICAL 226,383; FILL proxies 408; hourly 3,080. SOURCE/RECONCILIATION issues: `{"ABSENT_MINUTE": 387, "CAUSAL_PRICE_PROXY": 408, "CONFLICTING_DUPLICATE": 50}`. Disposition: quality flags retained; no source correction or training admission. Evidence: months/2026-03/qa_v2_receipt.json and partitioned issue tables.

## Final source-regime and event-context audit

Supplemental source issue counts: `{}`. 20x or1/20x month-to-month median reported volume is only a source-regime candidate, not proof of a unit change. No volume or price rescaling applied. Jump neighbor candles retain actual OHLCV, including rare genuine moves. Noncalendar prints remain raw/canonical evidence and never enter RTH hourly bins. All passes obey July2010 start. Earlier issuer warnings remain legacy evidence only.

|Category|Issue|Records|Distinct ticker/timestamp occurrences|
|---|---|---:|---:|
|AGGREGATION|HOURLY_ABSENT_MINUTES|60,558|60,558|
|AGGREGATION|HOURLY_ACTION_UNCERTAINTY|13|13|
|AGGREGATION|HOURLY_AMBIGUOUS_MINUTES|240|240|
|AGGREGATION|HOURLY_CLOSE_NOT_GENUINE|4,643|4,643|
|AGGREGATION|HOURLY_NO_GENUINE_MINUTE|532|532|
|AGGREGATION|HOURLY_OPEN_NOT_GENUINE|4,213|4,213|
|AGGREGATION|HOURLY_PRICE_PROXY_VOLUME_UNKNOWN|58,894|58,894|
|FILL|CAUSAL_PRICE_PROXY|226,423|226,423|
|RECONCILIATION|CONFLICTING_DUPLICATE|856|406|
|SOURCE|ABSENT_MINUTE|279,180|279,180|
|SOURCE|ACTION_OR_SCALE_JUMP_OVER25PCT|13|13|
|SOURCE|MANY_STOCKS_SYNCHRONOUS_GAP|1,990|1,990|

Minute/source records and affected-hour reasons have separate count units. Counts of records include all conflicting versions; distinct occurrences count ticker/timestamps within each issue type. Categories overlap and must not be summed as independent defects. NaT coverage markers have no timestamp. See the ticker-month and ticker-year issue tables for exact location/severity summaries.

## Final source-regime and event-context audit

Supplemental source issue counts: `{}`. 20x or1/20x month-to-month median reported volume is only a source-regime candidate, not proof of a unit change. No volume or price rescaling applied. Jump neighbor candles retain actual OHLCV, including rare genuine moves. Noncalendar prints remain raw/canonical evidence and never enter RTH hourly bins. All passes obey July2010 start. Earlier issuer warnings remain legacy evidence only.

|Category|Issue|Records|Distinct ticker/timestamp occurrences|
|---|---|---:|---:|
|AGGREGATION|HOURLY_ABSENT_MINUTES|60,558|60,558|
|AGGREGATION|HOURLY_ACTION_UNCERTAINTY|13|13|
|AGGREGATION|HOURLY_AMBIGUOUS_MINUTES|240|240|
|AGGREGATION|HOURLY_CLOSE_NOT_GENUINE|4,643|4,643|
|AGGREGATION|HOURLY_NO_GENUINE_MINUTE|532|532|
|AGGREGATION|HOURLY_OPEN_NOT_GENUINE|4,213|4,213|
|AGGREGATION|HOURLY_PRICE_PROXY_VOLUME_UNKNOWN|58,894|58,894|
|FILL|CAUSAL_PRICE_PROXY|226,423|226,423|
|RECONCILIATION|CONFLICTING_DUPLICATE|856|406|
|SOURCE|ABSENT_MINUTE|279,180|279,180|
|SOURCE|ACTION_OR_SCALE_JUMP_OVER25PCT|13|13|
|SOURCE|MANY_STOCKS_SYNCHRONOUS_GAP|1,990|1,990|

Minute/source records and affected-hour reasons have separate count units. Counts of records include all conflicting versions; distinct occurrences count ticker/timestamps within each issue type. Categories overlap and must not be summed as independent defects. NaT coverage markers have no timestamp. See the ticker-month and ticker-year issue tables for exact location/severity summaries.

## Final completion and offline verification replay — 2026-10-22T22:43:50.371566+00:00

All 189 active months are complete. The first final audit child completed successfully, but its BSD time wrapper failed on a sandbox-denied sysctl. The authorized native replay exited zero, with zero source downloads. Repeated final summary blocks are verification receipts, not additional defects; authoritative distinct counts are issue_counts_by_type.csv and partitioned ledgers. No source/derived candle was overwritten. No pre-July2010 source content was reread; all 412 preserved older data files have unchanged modification times after the human cutoff.
