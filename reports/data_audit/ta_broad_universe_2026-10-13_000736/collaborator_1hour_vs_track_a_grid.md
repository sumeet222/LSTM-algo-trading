# Collaborator comparability

The reported Colab endpoint is `/v2/stocks/{symbol}/bars`, timeframe1Hour,
names AAPL,CSCO,MSFT,INTC,NVDA, next_page_token pagination and CSV caching.
Exact START,END,FEED,ADJUSTMENT,ASOF, normalization, session filtering, expected
hour grid and structural_audit algorithm are **not supplied**. The example says
SIP and displays AAPL08–12Z premarket and80 rows over a July2024 week. None is
a proven Track A completeness audit. No collaborator credentials were collected.

This task instead fixes SIP/split/USD/asof2025-06-30/sortasc/limit10000, using
RFC3339 UTC full ET-date envelopes and exact RTH calendar filtering. Complete
monthly local requests are reused with identical material identity and recorded
containing date bounds; older retrieval timestamps are disclosed, not presented
as fresh HTTP responses. All new pages are HTTP200 and exhausted, including the
494-row nonterminal page on Jan26 and its170-row continuation. There are no
partial-success-as-complete responses. No single-versus-multi discrepancy was
observed that would require duplicate source requests.

|Name|Role|Apr19|Oct25|Jan24|Jan26|Mar8|Full FT0/T2|
|---|---|---:|---:|---:|---:|---:|---|
|AAPL|anchor|13/13|13/13|13/13|13/13|13/13|Inherited original reference|
|JPM|negative control|1/13|1/13|13/13|13/13|1/13|Inherited original reference|
|CSCO|ineligible Tech control|13/13|13/13|13/13|13/13|13/13|DATA_NOT_MEASURED|
|MSFT|ineligible Tech control|13/13|13/13|13/13|13/13|13/13|DATA_NOT_MEASURED|
|INTC|ineligible Tech control|13/13|13/13|13/13|13/13|13/13|DATA_NOT_MEASURED|
|NVDA|ineligible Tech control|13/13|13/13|13/13|13/13|13/13|DATA_NOT_MEASURED|


**Matching five-date answer:** all five collaborator Technology names have65/65
native30Min RTH starts including the five terminal stubs. CSCO,INTC,NVDA were
freshly checked on all five dates; MSFT reused four verified older pilots and
was freshly checked on Jan26. AAPL reused four original immutable monthly chunks.
Full prehistory/5-year16-channel FT0/T2 coverage is **unknown** for the additional
Tech controls. They cannot enter a non-Tech slot.

The new native1Hour control uses AAPL,JPM on Apr19, same material identity,
start2021-04-19T04:00:00Z, inclusive end2021-04-20T03:59:59.999999999Z.
AAPL returned16 rows, labels08:00Z through23:00Z; JPM returned one at13:00Z.
RTH starts13:30Z, so these whole-hour starts differ from Track A13:30/14:30…
anchored hourly inputs. AAPL13:00–14:00 straddles the open;19:00–20:00 includes
both an input half-hour and the closing stub. It cannot furnish their separate
OHLCV. Extended-hour counts cannot repair or certify the exact half-hour keys.
Native starts are preserved unchanged, never shifted/truncated or forward filled.

Hour-control source: `data/raw/alpaca/track_a_broad_candidate_v1/native_1hour_control/2021-04-996cb72c7545703e86d3.parquet`;
SHA256 `29b95e6188e34fd9c5aeb6b65168a8cf8e9bf0331dc75c39bcbe82f8ff050a38`. Exact params/receipt hashes in immutable_source_manifest.json.
The current [Alpaca bars contract](https://docs.alpaca.markets/us/reference/stockbars)
documents inclusive bounds, total-per-page limit and token continuation, and
distinguishes entity mapping asof from price/volume split adjustment. asof is
not proof of historical publication vintage. The earlier JPM asof=- versus
2025-06-30 minute pairs and first1/5-minute trades were successful but empty;
they do not establish no actual historical trading or a cause of omissions.
