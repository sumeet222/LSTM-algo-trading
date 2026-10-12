# Track A market-data catalog

## Course USA500

Researcher-supplied course source, original bytes retained:

`data/raw/course/USA500.IDXUSD_1h_2020-07-01_to_2025-06-30_UTC.csv`

Required CSV schema: `timestamp,open,high,low,close,volume`. Timestamps must contain
an explicit offset and are converted to UTC only in memory. The original is never
resaved, repaired, renamed or committed. The source is not reconstructible from a
public downloader: another group member needs the course file with the recorded hash.
Audit metadata is in `reports/data_audit/task01_course/course_manifest.json`.

Upstream provider, retrieval time, bar timestamp definition, publication latency,
adjustment and volume meaning were not supplied. The researcher instructed
"assume close for now" on 2026-10-10. This is a provisional availability assumption;
it does not verify provider semantics. Preserve Sunday and overnight observations.
Do not assume the course index has the equity exchange calendar or share volume.

## Stock source and canonical store

Candidate universe: AAPL, JPM, JNJ, WMT, CAT. Sector labels in the config are coarse
research metadata, not a historical point-in-time sector dataset. The sample comprises
surviving candidates and may have survivorship bias. No replacement is automatic.

Requested period: July 1, 2020 through June 30, 2025 in New York calendar dates.
Each chunk uses local midnight bounds converted to UTC; the API end is inclusive,
so next-month midnight minus one nanosecond prevents overlaps.

One canonical store: `data/raw/alpaca/track_a/`. Files are monthly, multi-symbol,
Zstandard-compressed Parquet paired with immutable small manifests. Filenames include
a hash of the request parameters. The manifest is the resume checkpoint and contains
request parameters, retrieval time, source, checksum, schema context, symbol coverage
and redacted request/retry events. No per-experiment table copies are required.

Columns: `symbol` (string), `timestamp` (timezone-aware UTC), OHLCV (float64),
`trade_count` (nullable Int64), `vwap` (float64/nullable), `feed`, `adjustment`,
`source_timeframe` and `provenance_id` (strings). Provider OHLCV is never forward-filled
or deduplicated silently. Fractional stock volume is retained and counted. Missing
optional provider trade_count/VWAP values are allowed; absent required OHLCV is not.
Calendar gaps and invalid rows are diagnosed rather than repaired.

The acquisition choice is explicit SIP / researcher-approved `30Min` / `split` / USD,
with entity mapping `asof=2025-06-30`. This mapping identifies the queried entity and
does **not** make split adjustments point-in-time. Split adjustments revise historical
prices and volumes retrospectively; cash dividends remain unadjusted. An authoritative
corporate-action reference dataset remains a later prerequisite for complete event QA.
Pilot split windows are selected from issuer documentation, without downloading
duplicate full raw/adjusted histories.

Preserve provider extended-session bars and classify their session overlap in QA.
No hourly bar is shifted or truncated to create a 09:30-anchored interval.
XNYS trading schedules handle daylight saving, holidays and early closes. There
is no regular NYSE lunch break. A normal session needs six complete hourly windows
plus a final 30-minute stub; an early close needs three hours plus a 30-minute stub.
The native-hour pilot failed. The researcher subsequently approved `30Min` source
and pairwise session-anchored hourly aggregation, retaining/flagging stubs. This is
implemented and the new small pilot passed. The source store retains native half-hour
bars, including extended sessions. Hourly outputs exist on demand only, without another
full-table copy. Incomplete windows emit missing masks, not filled prices/volumes.
Source VWAP is preserved; aggregate VWAP is omitted because Alpaca's VWAP volume basis
can differ from its bar volume. Native 1Hour remains available only for timing diagnostics.

## Gate and safe resumption

Run `lstm-data sip-pilot` with credentials set locally. Inspect `sip_pilot.json`,
the per-session timing evidence, split-window diagnostics and safe request events.
Do not proceed on HTTP 401/403/422, empty samples or failed timing. Rate-limit and
5xx errors have bounded exponential retries; excessive Retry-After stops the request.
Requests are paced at 180/minute, provisional below the documented Basic limit.
No account subscription is inferred from credentials or purchased by this code.

Only after both SIP and timing pass and the researcher approves the convention,
create a reviewable small JSON approval, with actual values:

```json
{
  "approved": true,
  "config_fingerprint": "COPY_FROM_MATCHING_PILOT",
  "source_timeframe_approved": "30Min",
  "session_aggregation_approved": true,
  "adjustment_approved": "split",
  "pilot_report": "reports/data_audit/ACTUAL_RUN/sip_pilot.json",
  "pilot_sha256": "ACTUAL_SHA256_OF_PILOT_JSON"
}
```

This is a schema example, not approval. Do not flip pilot booleans. The 30Min
source/aggregation already has researcher approval and passed the small pilot;
full acquisition and explicit split adjustment were subsequently approved by the
researcher. The actual reviewed approval is
`configs/track_a_bulk_approval_2026-10-10.json`. Reuse that authorization for resumption;
do not request it again unless material acquisition choices change. Config status
strings preserve their proposal context; the dated approval records the final choice.

Download resumes only matching, checksum-verified chunks without re-requesting them.
Unknown same-month files or a half-written data/manifest pair stop execution for
review. No old files are overwritten. An exclusive store lock protects concurrent
sessions; after an unclean process exit, inspect the writer and lock manually before
resuming. Atomic publish uses local-filesystem hard links; unsupported/network
filesystems must be separately verified. Moving/recovering an orphan is a human
decision, not automatic deletion. Pilot samples are small, ignored evidence under
`data/interim/alpaca_pilot/`, not a second canonical full-history store.

The pilot establishes timing conventions. During bulk collection, actual missing
source bars are preserved as gaps and counted in manifest `coverage_audit`, with
incomplete hourly-window masks. A gap does not cause OHLCV filling or a candidate
replacement. Off-grid/incompatible intervals, missing symbols, invalid required
values and duplicate keys still stop acquisition. Hourly aggregation emits only
complete observed windows; later research must explicitly decide eligibility around
gaps. Earlier manifests without `coverage_audit` remain valid and full-store QA can
recompute the diagnostics without rewriting them.

## Official references (checked 2026-10-10)

- [Alpaca historical bars](https://docs.alpaca.markets/us/reference/stockbars):
  explicit parameters, inclusive bounds, adjustments and multi-symbol pagination.
- [Alpaca market-data FAQ](https://docs.alpaca.markets/us/docs/market-data-faq):
  old SIP queries versus recent-data entitlement; bar aggregation description.
- [Market-data plans](https://docs.alpaca.markets/us/docs/about-market-data-api):
  Basic historical request limit (verify actual account behavior in the pilot).
- [exchange_calendars](https://github.com/gerrymanoim/exchange_calendars): historical schedules.
- [Apple split history](https://investor.apple.com/dividend-history/default.aspx):
  August 2020 4-for-1 split, trading date August 31.
- [Walmart February 23, 2024 filing](https://stock.walmart.com/sec-filings/all-sec-filings/content/0000104169-24-000033/wmt-20240223.htm):
  split-adjusted trading from February 26, 2024.


## Track A canonical SPY archive (TA-MKT-SPY-003)

The ignored `data/raw/alpaca/track_a_spy_v1/` namespace contains one shared
SIP/raw/30Min archive (11 immutable request keys, 2020-03-19–2025-06-30 ET,
as-of 2025-06-30). Preserve native extended-session rows and the append-only
`transport_attempts.jsonl`; no per-model copies or raw repairs.

Use `configs/track_a_market_spy_v3.json` and the acquisition command in README.
Local historical SIP credentials are required on another machine. The original
13-attempt journal must be supplied and verified against the committed SPY-002
proof before further source calls; the executor never creates a fresh zeroed
budget. Existing complete chunks resume by SHA without GETs. Missing/corrupt
pairs and missing/inconsistent historical journal evidence fail closed.

The archive contains 41,861 rows and all 17,197 expected RTH half-hours.
Completed closing stubs supply daily closes and stay outside hourly feature
positions. Publication timing and complete historical action scope remain
unverified; raw ETF distributions are price effects, not total-return or
portfolio cash adjustments. See the TA-MKT-SPY-003 source QA and review card.

## Track A FT0 offline audit

The existing stock SIP/split/30Min store and SPY SIP/raw/30Min store feed
`python -m lstm_data.ft0_audit --report reports/data_audit/<new-report-directory>`.
The command verifies immutable manifests, retains all 168 stock source gaps and
measures scheduled preconfirmation feature coverage. It makes no API calls and
fits no real transforms. Stock adjusted prices and inverse split-adjusted volume
are consumed without applying a second adjustment. Unknown publication and action
vintages remain separate admission holds; adjusted prices are not relabeled as raw
execution references. No source repair or pre-July stock warmup was acquired.
See [FT0 API](../docs/track_a/FT0_API.md) and the
[retention report](../reports/data_audit/ta_p2_close_ft0_2026-10-11/retention_and_attrition.md).
