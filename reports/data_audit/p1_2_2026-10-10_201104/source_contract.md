# P1.2 — course USA500 source contract

**Observed file facts are supportable; independent instrument identity and historical observability are UNKNOWN-BLOCKED.** This contract classifies evidence rather than approving an interpretation. “VERIFIED” below applies only to the stated local invariant. Machine checks use the existing PASS/WARN/BLOCKED/INVALID/INCONCLUSIVE/NOT_RUN schema in [checks.json](checks.json).

Evidence locators: **E** = [evidence.json](evidence.json), with `course-line-N` referring to the configured CSV's physical line including its header; **T** = `reports/data_audit/task01_course/course_manifest.json`; **P** = `configs/track_a_data.json`; **D** = `docs/track_a/Track_A_Consolidated_Implementation_Design_Record_v1.2_2026-10-10.md` §§3.2/9.2. T's small metadata-file hash still matches the P0.1 reference; the raw hash is inherited, not recalculated.

| Contract field | Classification | Evidence and precise boundary |
|---|---|---|
| Actual local source / retained name | VERIFIED | P and E identify `data/raw/course/USA500.IDXUSD_1h_2020-07-01_to_2025-06-30_UTC.csv`; same 2,083,715 bytes and source stats as P1.1. Original upstream/export filename is not independently documented. |
| Course provenance | SUPPORTED_WITH_QUALIFICATION | `data/README.md:5` calls it researcher-supplied course data; T reports unknown retrieval date. No original delivery receipt/handout/source-owner description found in the repository or source folder. |
| Vendor / instrument / quote construction | UNKNOWN-BLOCKED | T/P explicitly say upstream provider unverified. Filename code is not proof of an index, CFD, synthetic quote, bid/ask/trade basis, currency calculation or adjustment policy. No source-specific official document locator supplied. |
| Underlying historical membership | UNKNOWN-BLOCKED | D §2.2 makes membership conditional on a defensible construct. Membership is not definable from this CSV alone; no constituent history was supplied. Do not invent S&P membership. |
| Timestamp encoding | VERIFIED | E: `YYYY-MM-DD HH:MM:SS+00:00`; all 29,510 fields have explicit UTC offsets and whole-hour labels. Native timestamps retained unchanged. |
| DST / source aggregation timezone | SUPPORTED_WITH_QUALIFICATION | E converts 2020/2025 examples to ET -04:00 and March10,2023 to -05:00. `America/New_York` conversion is defined; the timezone/rules originally used to aggregate bars remain undocumented. |
| Timestamp ordering/duplicates | VERIFIED | E timestamp-only scan: zero duplicates, zero out-of-order labels. This is not a numerical OHLC rescan. |
| O/H/L/C fields | VERIFIED | E header and 18 sampled positive, finite, internally consistent OHLC tuples. T's original all-row quality result is reused; column presence does not prove economic price/bar semantics. |
| Hourly interval / label / completion | UNKNOWN-BLOCKED | E: one-hour label spacing is modal (28,216 adjacent gaps); 995 two-hour gaps also occur. Neither establishes interval start versus end, continuous coverage, or historical completion/publication. |
| Only U.S. equity RTH observations | CONTRADICTED | E: 22,008 labels outside XNYS RTH, including 2,240 on non-XNYS-session dates; these are label classifications, not inferred source intervals. The actual vendor calendar remains unknown. |
| Compatible six stock hours / closing stub | UNKNOWN-BLOCKED | E: source labels occur on whole ET hours; stock boundaries are :30. No exact half-hour label exists. Coarser source OHLC cannot be divided into 09:30-anchored bars without missing constituent data. Source-specific compatible completed observations still require verification; no stock-grid resampling or stub merge performed. |
| Holidays, early closes, overnight gaps | SUPPORTED_WITH_QUALIFICATION | E reuses T's November27,2020 early-close and March15,2021 DST timestamp examples. XNYS close is not proof of this instrument's close. Largest reported gap77h is not automatically missing data without its calendar. |
| Daily close / completed session | UNKNOWN-BLOCKED | No daily-close series/definition or source-session cutoff supplied. A label at16:00 ET, final UTC-day row or final ET-day row is not a proven daily close. Source overnight schedule and early-close rules require confirmation. |
| Historical publication / revisions / vintage | UNKNOWN-BLOCKED | CSV has only timestamp/OHLCV; no actual `available_at`, first-publication, revision or historical-vintage fields. File mtime/export time cannot establish what was available at a historical cutoff. |
| D2 freshness | UNKNOWN-BLOCKED | D requires age from documented market period end ≤90min **and** actual completion/publication by each step's cutoff. E's nearest-label distances are not period-end or publication evidence. |
| Study span | VERIFIED | E confirms label range2020-07-01 04:00 UTC to2025-07-01 04:00 UTC; last label is next local date. Same 29,510-record reference as T; raw hash `ba78d6bf933f0aca4dfcdedb69454d19aa29bfed84481b6ba1bcccdaf7b1634a` reused. |
| Prehistory / full U1–U5 / 48-step validity | UNKNOWN-BLOCKED | No labels before formation in this file. 48-step context, hourly RMS12/60, daily RMS63 and valid endpoint/46-of-48 requirements not computed or certified. Calendar span alone cannot supply earlier history or validate a vector. |
| Volume | VERIFIED for nonuse only | D7 forbids market-volume channels. Volume column exists; its values were not parsed, retained or interpreted here. Instrument volume semantics remain unknown. |

The local-only search stopped at the proof boundary: no named, authenticated course/vendor contract exists for this exact source. No web price-fingerprinting, price correlation, proxy retrieval or speculative vendor match was attempted. Price magnitudes play no role in identity classification.

## Source-owner inquiry draft — not sent

Please confirm the contract for the exact retained USA500 file above, ideally with its original export instructions/handout and vendor specification:

1. Which provider and instrument does `USA500.IDXUSD` represent? Is it an index calculation, CFD/synthetic quote or other series; what are its price/quote, currency and adjustment bases? Does it have a meaningful historical constituent membership list?
2. Does a native timestamp such as `2020-07-08 14:00:00+00:00` mark the start or end of which precise OHLC interval? What timezone/DST rules and included trading sessions define that interval?
3. What explains overnight/Sunday observations, gaps, holidays and early closes? Can this source supply genuinely completed hourly observations compatible with historical 10:30/11:30 ET stock cutoffs without dividing/relabeling source bars?
4. What is the source's daily session and official closing value? How are overnight sessions, early closes and the following morning's previous-session close handled, and is a separately defined historical daily series available?
5. When were each hour and daily close first available historically, and what delays/corrections/revisions occurred? Can original historical `available_at` or vintage records be supplied? If only an assumption is possible, identify it explicitly for separate human protocol review.
6. What are the original delivery/export date, source version, permitted research/reproduction use, and availability of pre-July2020 history needed for D7 warmup?

The earlier “assume close for now” instruction remains provisional. It does not answer the publication question or approve U1–U5 construction. No source-owner message was sent.
