# Hourly-close price references — approved conditional study

| Information cutoff ET | Nominal issue | Simulated entry | Entry close interval | Simulated exit | Exit close interval |
|---|---|---|---|---|---|
| 10:30 | 10:32 | 10:33 | 09:30–10:30 | 14:33 | 13:30–14:30 |
| 11:30 | 11:32 | 11:33 | 10:30–11:30 | 15:33 | 14:30–15:30 |

The CSV contains 50 concrete symbol/date/origin examples with exact UTC and ET clocks, native-source IDs, vendor-adjusted closes, returns, 180-second observation-to-event age and idealized label maturity. These are approximate price references, not minute fills. Missing exact slots fail; no nearest observation or terminal stub substitution occurs. The event hold and close-to-close interval are each 240 minutes.

March 12, 2021 uses EST; March 15 uses EDT. Source interval starts/ends remain genuine calendar boundaries. The Friday last full-hour close to Monday first full-hour close contains the real overnight/weekend price change for RSI; it is not manufactured into hourly rows. On November 27, 2020 the exchange closes at 13:00 ET: three full hours and a 12:30–13:00 stub exist, but neither nominal 240-minute forecast origin is admitted.

Observed publication stays UNKNOWN. A positive publication delay would miss the original same-ended-hour cutoff, even if available by nominal issuance. The approved idealized zero-delay study makes no claim to replay the actually published historical feed. Late-bar revisions and retrospective action adjustments remain explicit study limitations. No minute acquisition or minute-coverage gate is active in this package.
