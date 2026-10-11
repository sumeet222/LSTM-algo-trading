# P1.2D — Dukascopy contract delta

Checked **2026-10-11 UTC / 2026-10-10 ET**. Provider-general documentation does not authenticate the instructor's export. No new historical price query, raw-file read, export or price fingerprinting was performed. Existing course facts refer to `reports/data_audit/p1_2_2026-10-10_201104/evidence.json` (**E**) and `source_contract.md`; inherited course hash is `ba78d6bf933f0aca4dfcdedb69454d19aa29bfed84481b6ba1bcccdaf7b1634a` (not rehashed).

## Official references

- **R:** [Range of markets](https://www.dukascopy.com/swiss/english/cfd/range-of-markets/), Indices, Trading Hours, CFD Disclaimer.
- **A:** [JForex IHistory](https://www.dukascopy.com/client/javadoc/com/dukascopy/api/IHistory.html), `getBars`, `getBarStart`, `getBar`; API 2.12.46 documentation, not an export manifest.
- **H:** [History bars](https://www.dukascopy.com/wiki/en/development/strategy-api/historical-data/history-bars/), Bars by shift / Bars by time interval.
- **P:** [JForex4 Preferences](https://www.dukascopy.com/wiki/en/manuals/jforex4-desktop/preferences/), General → Time Zone / Day Start Time.
- **X:** [Historical Data Export](https://www.dukascopy.com/swiss/english/marketwatch/historical/), tool introduction and FAQ on download sources.
- **Q:** [Historical data export widget description](https://www.dukascopy.com/api/data/get/historical-data-export), available bid/ask quotes.
- **S:** [Historical Data Service](https://www.dukascopy.com/wiki/en/development/strategy-api/historical-data/historical-data-service/), first-available-data methods.
- **T:** [Terms of Use](https://www.dukascopy.com/swiss/english/legal-pages/terms-of-use/), §§3–5 (use/license/fees).
- **W:** [Trading-tools API documentation](https://www.dukascopy.com/trading-tools/api/documentation), landing page; rendered view supplied no exact historical-candle request schema. No undocumented endpoint inferred.

## Field classifications

| Field | Provider / local evidence | Course-export delta and disposition |
|---|---|---|
| Provider | **USER_ATTESTED:** researcher says instructor supplied a Dukascopy export (P1.3B/current prompt). | Testimony retained; **EXPORT_SETTING_UNVERIFIED** original export/tool/version. No independent delivery receipt or instrument match. |
| Instrument / currency | **OFFICIAL_PROVIDER_GENERAL:** R lists `USA500.IDX/USD` as a USD index CFD. Its pricing disclaimer distinguishes CFDs from exchange/hedging prices. | **UNKNOWN/BLOCKED:** exact course instrument. Similar filename supports a candidate, not verification; no cash S&P 500/SPY substitution. |
| Constituent membership | R's broad product description is not a dated constituent roster or a course-specific investable universe. | **UNKNOWN/BLOCKED:** D1 conditional membership construct. A CFD may make literal membership inapplicable; this is an inference requiring joint human resolution, not a waiver or automatic false finding. |
| Price / adjustment basis | **OFFICIAL_PROVIDER_GENERAL:** A/H specify BID or ASK; Q describes bid/ask export data. No midpoint/trade selector was qualified by the reviewed material. | **EXPORT_SETTING_UNVERIFIED:** chosen side, any midpoint/custom processing, rounding/adjustments. No claim course OHLC are trades. |
| Bar label / interval | **OFFICIAL_PROVIDER_GENERAL:** A/H query boundaries are bar starts; round-hour boundaries apply to standard one-hour requests. Shift 0 can be incomplete; shift 1 is formed. | **COURSE_FILE_OBSERVED:** E's native labels are UTC whole hours. **EXPORT_SETTING_UNVERIFIED:** whether this CSV retains API start labels, uses close labels or was transformed. Earlier provisional close assumption remains diagnostic only. |
| Timezone / DST / export formatting | **OFFICIAL_PROVIDER_GENERAL:** P separates display timezone from day-start timezone; day-start affects intervals longer than two hours and daily statistics. H shows GMT formatting examples. | **COURSE_FILE_OBSERVED:** explicit `+00:00`; summer/winter ET conversions below. **EXPORT_SETTING_UNVERIFIED:** export timezone controls, original aggregation/formatting, DST settings. Platform display preferences do not prove CSV defaults or authorize changing its labels. |
| Session / daily close | **OFFICIAL_PROVIDER_GENERAL:** R currently lists summer GMT Sun–Fri 22:00–20:15, break 20:15–22:00; winter 23:00–21:15, break 21:15–23:00. | **UNKNOWN/BLOCKED:** original 2020–25 session/holiday versions and completed daily-close definition. A trading break is not an approved daily candle cutoff or 16:00 ET cash close. P allows daily-boundary settings; do not select the last row as an official close. |
| Completion / publication / revisions | A/H distinguish in-progress from formed bars; neither checked reference gives this course's historic first-publication times or revision vintages. | **UNKNOWN/BLOCKED:** mathematical end, provider formation, first publication, export date and corrected values are distinct. `available_at` remains null. Today's retrieval or file mtime does not establish historical observability. |
| RTH compatibility | **COURSE_FILE_OBSERVED:** native :00 labels differ from stock :30 cutoffs; E already reports overnight/non-XNYS labels. **CONTRADICTED:** source labels restricted to cash-equity RTH. | Conditional freshness arithmetic below is possible; **UNKNOWN/BLOCKED** actual interval/session compatibility and historical observability. No :00→:30 shift, bar split/resampling, U1–U5 or coverage certification. |
| Prehistory / granularity | **OFFICIAL_PROVIDER_GENERAL:** A/H document hourly histories; S exposes a first-data lookup facility. X describes multiple export resolutions. | **UNKNOWN/BLOCKED:** no reviewed promise of USA500 hourly history before July 2020, nor a verified actual first date. E's file starts at formation; no download or changed warmup/start date. |
| Access / rights | **OFFICIAL_PROVIDER_GENERAL:** X describes a free public export tool; JForex manager requires platform login. T restricts reuse/licensing and automated extraction absent written consent. | **UNKNOWN/BLOCKED:** course-specific research/reproduction/redistribution rights and safe exact candle query. Free access is not an unrestricted data license. No key/account/subscription sought; no sample request attempted. |

The optional comparison was **NOT_RUN**: the reviewed official materials do not establish an exact public, credential-free, permitted request with instrument/side/time limits for this comparison. W's non-rendered schema is a limitation of this inspection, not proof that no API exists. A supported tool/session, documented query schema, usage authorization and actual export settings would be needed first. Numerical matches could not prove vintage anyway; mismatches would not automatically mean corruption.

## Two inherited rows and conditional clock arithmetic

These were selected from E before any possible comparison. Both are ordinary XNYS session dates; original physical CSV locators and OHLC text are reused, with no course-file scan.

| Locator | Native stamp → ET | Original O / H / L / C |
|---|---|---|
| `course-line-123` | 2020-07-08 14:00 UTC → 10:00 EDT | 3170.437 / 3172.149 / 3159.637 / 3163.137 |
| `course-line-15929` | 2023-03-10 15:00 UTC → 10:00 EST | 3893.69 / 3915.897 / 3886.46 / 3914.837 |

For either row, **if** its stamp is a one-hour start, period end is 11:00 ET: age at 10:30 is −30 minutes (unfinished, reject); age at 11:30 is 30 minutes (freshness only). **If** it is a close label, period end is 10:00: ages are 30 and 90 minutes, respectively (freshness only). Neither premise is verified for the export. The start-labelled 09:00–10:00 alternative at 10:30 would also be only a conditional freshness candidate, not a verified compatible RTH input. No source comparison or approval results from this arithmetic.

For each bar and **each historical step's own cutoff** `t`, require documented compatible/session-matched OHLC, `0 <= t - documented_period_end <= 90 minutes`, and `documented_available_at <= t`. Apply the original cutoff/issuance rules: delayed issuance cannot admit a period ending after the original cutoff. Unknown metadata stays UNKNOWN/BLOCKED; do not infer publication at interval end or copy endpoint market state into earlier steps. These predicates are necessary, not sufficient for complete U1–U5 vectors, daily inputs or 46/48 retention.

## F01 and next repair boundary

Existing `alignment.asof_diagnostic` uses availability age at `src/lstm_data/alignment.py:51`, while D2 requires period-end age. E's inherited `synthetic-F01` has period age 120 minutes, availability age 60, and a false acceptance; F01 remains **INVALID**. Production code was not invoked or changed.

Official API start/formed-bar semantics clarify a possible metadata contract, but cannot settle this CSV's semantics or historical availability. A separately authorized isolated repair can require explicit `period_end` and independently evidenced `available_at`, rejecting/flagging unknowns; regression cases should cover the existing stale counterexample, fresh-unpublished/future-end/unknown metadata and each historical cutoff. This is a blocker-preserving design recommendation, not implementation or G2 approval. Shared D3 sign-off remains pending.
