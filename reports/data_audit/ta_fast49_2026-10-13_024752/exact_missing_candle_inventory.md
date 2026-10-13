# Exact missing-candle inventory

**PARTIAL native source-key audit; FULL_SOURCE_QA_INCOMPLETE; SCIENTIFIC_HOLD.**

AAPL first, followed by the four frozen selections. Each normal XNYS day has 13 starts from 09:30 through 15:30 ET. Early closes use their actual terminal stub. ET timestamps below carry explicit UTC offsets. Confirmation candles were checked only as source keys after selection; no features, labels or performance were computed.

|Stock|Provisional sector|Expected|Observed|Missing|Runs|Largest run|Terminal absent|98% / yearly95%|
|---|---|---:|---:|---:|---:|---:|---:|---|
|AAPL|Technology|16261|16261|0|0|0|0|True / True|
|COST|Consumer Staples|65|65|0|0|0|0|NOT_MEASURED_FULL_INTERVAL / NOT_MEASURED_FULL_INTERVAL|
|CMCSA|Communication Services|65|65|0|0|0|0|NOT_MEASURED_FULL_INTERVAL / NOT_MEASURED_FULL_INTERVAL|
|SBUX|Consumer Discretionary|65|65|0|0|0|0|NOT_MEASURED_FULL_INTERVAL / NOT_MEASURED_FULL_INTERVAL|
|HON|Industrials|65|53|12|1|12|1|NOT_MEASURED_FULL_INTERVAL / NOT_MEASURED_FULL_INTERVAL|

## Largest clumps

|Stock|Session ET|Start UTC|End UTC|Half-hours|
|---|---|---|---|---:|
|HON|2021-04-19|2021-04-19T14:00:00+00:00|2021-04-19T20:00:00+00:00|12|

## AAPL — complete absent-candle list

|ET start|ET end|UTC start|Run size|Terminal stub|
|---|---|---|---:|---|
No missing expected RTH keys.

## COST — available-partition absent-candle list

|ET start|ET end|UTC start|Run size|Terminal stub|
|---|---|---|---:|---|
No absent keys in the measured partitions; unmeasured sessions are not gap-free.

## CMCSA — available-partition absent-candle list

|ET start|ET end|UTC start|Run size|Terminal stub|
|---|---|---|---:|---|
No absent keys in the measured partitions; unmeasured sessions are not gap-free.

## SBUX — available-partition absent-candle list

|ET start|ET end|UTC start|Run size|Terminal stub|
|---|---|---|---:|---|
No absent keys in the measured partitions; unmeasured sessions are not gap-free.

## HON — available-partition absent-candle list

|ET start|ET end|UTC start|Run size|Terminal stub|
|---|---|---|---:|---|
|2021-04-19T10:00:00-04:00|2021-04-19T10:30:00-04:00|2021-04-19T14:00:00+00:00|12|False|
|2021-04-19T10:30:00-04:00|2021-04-19T11:00:00-04:00|2021-04-19T14:30:00+00:00|12|False|
|2021-04-19T11:00:00-04:00|2021-04-19T11:30:00-04:00|2021-04-19T15:00:00+00:00|12|False|
|2021-04-19T11:30:00-04:00|2021-04-19T12:00:00-04:00|2021-04-19T15:30:00+00:00|12|False|
|2021-04-19T12:00:00-04:00|2021-04-19T12:30:00-04:00|2021-04-19T16:00:00+00:00|12|False|
|2021-04-19T12:30:00-04:00|2021-04-19T13:00:00-04:00|2021-04-19T16:30:00+00:00|12|False|
|2021-04-19T13:00:00-04:00|2021-04-19T13:30:00-04:00|2021-04-19T17:00:00+00:00|12|False|
|2021-04-19T13:30:00-04:00|2021-04-19T14:00:00-04:00|2021-04-19T17:30:00+00:00|12|False|
|2021-04-19T14:00:00-04:00|2021-04-19T14:30:00-04:00|2021-04-19T18:00:00+00:00|12|False|
|2021-04-19T14:30:00-04:00|2021-04-19T15:00:00-04:00|2021-04-19T18:30:00+00:00|12|False|
|2021-04-19T15:00:00-04:00|2021-04-19T15:30:00-04:00|2021-04-19T19:00:00+00:00|12|False|
|2021-04-19T15:30:00-04:00|2021-04-19T16:00:00-04:00|2021-04-19T19:30:00+00:00|12|True|

The PARTIAL CSV contains 12 absent keys in 1 maximal within-session runs. Source/manifest/SHA and stable cluster IDs are in [the CSV](missing_candles_all_selected.csv). [Prehistory](prehistory_native_quality.csv) is separate; 5340 stock-sessions have unverified source partitions. Malformed/duplicate/off-grid keys are rejected by the source validator, with no corrections.

Training: conditional T2-only upper bound 1448/1502 = 96.40%; required1352. This assumes all other dependencies ideal. Actual complete48×16 FT0, M2 and scientific eligibility are NOT_MEASURED; no floor/scaler fit or TG0 label was manufactured.

Source percentages alone do not resolve a major run, missing terminal close, unknown publication, action vintage or historical membership. The original five stocks, frozen rules and 0/40 scientific ledger remain unchanged. No missing candle has been filled.
