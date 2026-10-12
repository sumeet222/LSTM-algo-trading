# JPM April 19, 2021: mapping, daily-bar and trade diagnosis

**Supported conclusion:** The missing 10:00–10:30 EDT minute bars do not change with the two tested ticker-mapping settings. SIP trades are also absent from successful exhaustive responses for the narrower 10:00–10:01 and 10:00–10:05 EDT windows. A positive-control minute bar and a daily bar exist. This does not prove historical trade absence, nor explain the provider data pattern.

## Results

|Request|asof|Timeframe / data|Window UTC (API start → inclusive end)|HTTP|Rows|Pages|Pagination|
|---|---|---|---|---:|---:|---:|---|
|target_mapped|2025-06-30|1Min|2021-04-19T14:00:00+00:00 → 2021-04-19T14:30:00+00:00|200|0|1|exhausted|
|target_unmapped|-|1Min|2021-04-19T14:00:00+00:00 → 2021-04-19T14:30:00+00:00|200|0|1|exhausted|
|control_mapped|2025-06-30|1Min|2021-04-19T13:30:00+00:00 → 2021-04-19T14:00:00+00:00|200|1|1|exhausted|
|control_unmapped|-|1Min|2021-04-19T13:30:00+00:00 → 2021-04-19T14:00:00+00:00|200|1|1|exhausted|
|daily_mapped|2025-06-30|1Day|2021-04-19T04:00:00+00:00 → 2021-04-20T03:59:59.999999999+00:00|200|1|1|exhausted|
|trades_1min_unmapped|-|raw trades|2021-04-19T14:00:00+00:00 → 2021-04-19T14:00:59.999999999+00:00|200|0|1|exhausted|
|trades_5min_unmapped|-|raw trades|2021-04-19T14:00:00+00:00 → 2021-04-19T14:04:59.999999999+00:00|200|0|1|exhausted|

**Budget:** 7 of15 transport attempts; all HTTP200, one page each, no retries, no continuation tokens. Failures: none. No 401/403, rate-limit, transport or pagination block. Existing rate limit/backoff transport policy was bounded to one attempt per page and at least one second between sends.

Target minute analysis uses [14:00,14:30) UTC; control uses [13:30,14:00). API bars end is inclusive, so records at either exclusive endpoint would be boundary extras; none returned. Each target query returns0/30 scheduled minute keys. Both control queries return the same one minute start13:30Z/09:30EDT, out of30 possible starts. The positive control is therefore successful but sparse, not complete intraday coverage. Returned control OHLC=153.42, volume160400, trade_count1. Existing native30Min09:30 candle is present;10:00 and10:30 native keys are absent, as verified previously and rechecked through original hashes.

The SIP daily record exists under asof2025-06-30, timestamp2021-04-19T04:00:00Z: O153.42/H153.42/L152.65/C152.65, volume160400, trade_count1, VWAP153.42. A daily record does not certify any particular missing intraday candle. Its differing low/close and sparse control warrant clarification, but daily versus one observed minute is not a complete full-session comparison. A second daily asof query was unnecessary for the existence test because the daily record was present and the minute/control mapping pairs were identical; daily asof=- remains untested.

Trades were explicitly queried with asof=-, avoiding symbol mapping, raw prices/sizes, currencyUSD, SIP. No trade rows were returned, so there are no timestamps, exchange codes, prices, sizes or sale conditions to enumerate. The one-minute empty response was exhausted before expansion to five minutes, which was also exhausted and empty. No entire-day trade request was made. These results do not establish trade coverage for10:05–10:30 or the remainder of the session. No trade-eligibility/OHLC condition assumptions were used.

## What is and is not established

- **Trades exist while bars are absent:** not demonstrated in the tested trade windows; no trade rows were returned.
- **Trades and minute bars both absent:** demonstrated as current successful-response absence for the tested first minute and first five minutes; both30-minute bar queries are empty. Historical absence of actual trades is not certified.
- **Ticker-mapping-dependent missingness:** not demonstrated. asof2025-06-30 and asof=- give identical empty target responses and identical positive-control records. This rules out a difference between these two current bar requests, not every conceivable mapping/source issue.
- **Request, permission or pagination prevents conclusion:** none occurred in these seven requests. Source completeness and historical publication are still unverified.

Per the [official bars documentation](https://docs.alpaca.markets/us/reference/stockbars), asof=- bypasses symbol mapping and bar endpoints are inclusive. The [official trades documentation](https://docs.alpaca.markets/us/reference/stocktrades-1) supports SIP/asof controls and pagination; trades carry their original condition fields, whereas bars here are split-adjusted. No raw/split conversion or reconstruction was performed.

## Exact reproducible requests and response hashes

### target_mapped

`https://data.alpaca.markets/v2/stocks/bars`

```json
{
  "adjustment": "split",
  "asof": "2025-06-30",
  "currency": "USD",
  "end": "2021-04-19T14:30:00+00:00",
  "feed": "sip",
  "limit": 10000,
  "sort": "asc",
  "start": "2021-04-19T14:00:00+00:00",
  "symbols": "JPM",
  "timeframe": "1Min"
}
```

Raw evidence: `response_01.json`; SHA256 `c700148960d500511ad0040f8b1c3c6ebbac07572176aff49cfc66b69eec9aee`.

### target_unmapped

`https://data.alpaca.markets/v2/stocks/bars`

```json
{
  "adjustment": "split",
  "asof": "-",
  "currency": "USD",
  "end": "2021-04-19T14:30:00+00:00",
  "feed": "sip",
  "limit": 10000,
  "sort": "asc",
  "start": "2021-04-19T14:00:00+00:00",
  "symbols": "JPM",
  "timeframe": "1Min"
}
```

Raw evidence: `response_02.json`; SHA256 `c700148960d500511ad0040f8b1c3c6ebbac07572176aff49cfc66b69eec9aee`.

### control_mapped

`https://data.alpaca.markets/v2/stocks/bars`

```json
{
  "adjustment": "split",
  "asof": "2025-06-30",
  "currency": "USD",
  "end": "2021-04-19T14:00:00+00:00",
  "feed": "sip",
  "limit": 10000,
  "sort": "asc",
  "start": "2021-04-19T13:30:00+00:00",
  "symbols": "JPM",
  "timeframe": "1Min"
}
```

Raw evidence: `response_03.json`; SHA256 `1d92167260f37c28fa41065b3c95c893c7b8c1bbcbecf0baa2a6f8655f7af9d3`.

### control_unmapped

`https://data.alpaca.markets/v2/stocks/bars`

```json
{
  "adjustment": "split",
  "asof": "-",
  "currency": "USD",
  "end": "2021-04-19T14:00:00+00:00",
  "feed": "sip",
  "limit": 10000,
  "sort": "asc",
  "start": "2021-04-19T13:30:00+00:00",
  "symbols": "JPM",
  "timeframe": "1Min"
}
```

Raw evidence: `response_04.json`; SHA256 `1d92167260f37c28fa41065b3c95c893c7b8c1bbcbecf0baa2a6f8655f7af9d3`.

### daily_mapped

`https://data.alpaca.markets/v2/stocks/bars`

```json
{
  "adjustment": "split",
  "asof": "2025-06-30",
  "currency": "USD",
  "end": "2021-04-20T03:59:59.999999999+00:00",
  "feed": "sip",
  "limit": 10000,
  "sort": "asc",
  "start": "2021-04-19T04:00:00+00:00",
  "symbols": "JPM",
  "timeframe": "1Day"
}
```

Raw evidence: `response_05.json`; SHA256 `711913b39b26a883a6edea8d7a9e742200fd73482d04a407f6dc1bbb9880c873`.

### trades_1min_unmapped

`https://data.alpaca.markets/v2/stocks/trades`

```json
{
  "asof": "-",
  "currency": "USD",
  "end": "2021-04-19T14:00:59.999999999+00:00",
  "feed": "sip",
  "limit": 1000,
  "sort": "asc",
  "start": "2021-04-19T14:00:00+00:00",
  "symbols": "JPM"
}
```

Raw evidence: `response_06.json`; SHA256 `d7e3220c2f8fe6e76f2cc4b8b74c54e14da90d5028f56f49334652cd88f0b57b`.

### trades_5min_unmapped

`https://data.alpaca.markets/v2/stocks/trades`

```json
{
  "asof": "-",
  "currency": "USD",
  "end": "2021-04-19T14:04:59.999999999+00:00",
  "feed": "sip",
  "limit": 1000,
  "sort": "asc",
  "start": "2021-04-19T14:00:00+00:00",
  "symbols": "JPM"
}
```

Raw evidence: `response_07.json`; SHA256 `d7e3220c2f8fe6e76f2cc4b8b74c54e14da90d5028f56f49334652cd88f0b57b`.

Request parameters are otherwise identical within each target/control asof pair and match the preceding diagnostic. Bar page limit10000; trade limit1000. The daily request spans the ET date only, including the midnight daily label. The trades end uses one nanosecond before the exclusive1/5-minute endpoint. No default feed, adjustment, currency or asof is relied upon. Existing authenticated HistoricalClient/request parser/pagination were reused for bars; the documented trade endpoint used the same credentials and durable redacted transport without a production adapter change.

`preflight.json` binds the exact prior request and original source/manifest hashes. `query_results.json` records all query counts, status, page completion and parameters. For each of7 calls, attempt_NN_before.json was durably written before sending, attempt_NN_after.json records HTTP metadata and raw-body SHA, and response_NN.json preserves exact successful bytes. CSV files preserve each bar response; empty trade-record JSON files preserve the analyzed trade populations. Python3.14.6, repository .venv and existing requests/pandas/dotenv packages; .env was loaded only by the existing secure mechanism and never displayed. No new packages or Python files.

**NO_CODE_CHANGE; NO_DATA_MODIFICATION; ORIGINAL_UNIVERSE_UNCHANGED; SCIENTIFIC_HOLD.** All protected original source, prior evidence, tracked code/protocol and gate files remain SHA-identical. No imputation, source activation, stock substitution, model fitting, confirmation access or Git integration. Further provider clarification is worthwhile using these existing request IDs and raw results, rather than assuming the daily record supplies the missing intraday prices. No provider contact or additional queries were performed.
