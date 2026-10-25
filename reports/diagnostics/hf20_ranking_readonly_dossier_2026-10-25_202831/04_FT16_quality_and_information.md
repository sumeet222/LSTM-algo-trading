# 04 — FT16 quality, fallback and source information

**QUALIFIED: actual representation/source quality measured; predictive value of a changed input remains NOT_TESTED.**

All findings are descriptive. Inner training/refit are in sample; inner validation is selection-influenced; development is 109 repeatedly inspected sessions, not confirmation. No new model, objective fit, labels, inference or trading.


## All16 executed feature formulas

| channel | formula | history | source |
| --- | --- | --- | --- |
| M1 | log(C/O)/max(RMS60,h) | 60h | cap5 close; genuine open; current completed-hour or earlier only |
| M2 | mean20(previous same-origin matured4h returns)/max(RMS60(previous same-origin returns),m2floor) | 60 previous regular sessions | genuine endpoints; each historical day locked before its open; origin1/2 context; current completed-hour or earlier only |
| M3 | log(D[d-1]/D[d-6])/(sqrt(5)*max(RMS63,dailyfloor)) | 63/5 previous regular sessions | genuine15:30 surrogate; current completed-hour or earlier only |
| M4 | log(D[d-21]/D[d-126])/(sqrt(105)*max(RMS63,dailyfloor)) | 126 previous regular sessions | genuine15:30 surrogate; current completed-hour or earlier only |
| V1 | log(max(RMS12,h)) | 12h | RMS of OC; current completed-hour or earlier only |
| V2 | log(max(RMS60,h)) | 60h | RMS of OC; current completed-hour or earlier only |
| V3 | V1-V2 | 12/60h | log volatility ratio; current completed-hour or earlier only |
| B1 | log(H/L) | current complete hour | trusted observed extremes; missing completeness retained; current completed-hour or earlier only |
| B2 | (2C-H-L)/(H-L), zero range=>0 | current hour | missing if unreliable/outside observed range; current completed-hour or earlier only |
| Q1 | log((hour_volume+q_h)/(mean_previous20_same_slot_volume+q_h)) | 20 matching slots, >=19 valid,maxgap2 | <=5absent minutes and no conflict/quarantine; same volume regime; current completed-hour or earlier only |
| Q2 | log((mean5daily_volume+q_d)/(mean60daily_volume+q_d)) | 5/60 previous regular sessions | sum6usable hourly lower bounds, no stub, same share regime; current completed-hour or earlier only |
| T1 | log(C/mean20previous_daily_close) | 20 previous regular sessions | >=19 valid,maxgap2; current completed-hour or earlier only |
| T2 | mean20(sign(previous daily logreturns)) | 20 previous regular sessions | >=19 valid,maxgap2; bounded identity; current completed-hour or earlier only |
| T3 | (EMA6-EMA18)/C | >=360usable hourly updates and69/72recent,maxgap2 | gap>=3 resets; COP resets; current completed-hour or earlier only |
| T4 | (EMA24-EMA72)/C | same as T3 | price invariant; current completed-hour or earlier only |
| T5 | (WilderRSI14-50)/50 | 14seed changes+140updates | gap disconnects predecessor;gap>=3 resets;neutral0 if missing; current completed-hour or earlier only |


Exact full-precision frozen centers/scales/fallbacks for both phases are in [exact_frozen_channel_recipes.csv](exact_frozen_channel_recipes.csv), with source binding to [train_only_fit_recipes.json](../../../reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122/train_only_fit_recipes.json). Thirteen channels use native training median fallback and pooled median/unscaledMAD scaling; B2/T2/T5 use neutral0 and identity. IQR/1.349, populationSD, then1 are the documented nonzero-scale fallbacks. No clipping or input asinh. Training fits use unique eligible historical keys, M2 context50/50, not duplicated48-step windows. Native nonfinite, substituted and scaled values remain separately accessible in the shared canonical NPZ. This audit gathers endpoints and prefix-sum masks without materializing overlapping feature tensors.

## Actual role fallback rates

The field `fallback_rate` is unique source-key incidence; `window_cell_fallback_rate` counts model exposure including overlapping windows. These denominators differ and must not be compared as the same statistic.

| role | channel | fallback_rate | window_cell_fallback_rate | endpoint_fallback_rate | windows_stock_any_fallback |
| --- | --- | --- | --- | --- | --- |
| inner_train | M1 | 0.03568009096 | 0.02695865327 | 0.02424345077 | 12168 |
| inner_train | M2 | 0.05866510186 | 0.05014491117 | 0.04856594399 | 5208 |
| inner_train | Q1 | 0.06944527557 | 0.06259127522 | 0.04331526649 | 14107 |
| inner_train | Q2 | 0.2037729639 | 0.1967757264 | 0.1930442638 | 20002 |
| inner_validation | M1 | 0.05132361689 | 0.04786907093 | 0.04608355091 | 2425 |
| inner_validation | M2 | 0.1479786595 | 0.1498313751 | 0.1361618799 | 2558 |
| inner_validation | Q1 | 0.1206573468 | 0.1114243364 | 0.08093994778 | 3468 |
| inner_validation | Q2 | 0.3247323022 | 0.3425492276 | 0.3244125326 | 6148 |
| refit | M1 | 0.03829315669 | 0.02997120921 | 0.02740882917 | 14633 |
| refit | M2 | 0.07355816227 | 0.06479926424 | 0.06142994242 | 7782 |
| refit | Q1 | 0.07516186871 | 0.06700575816 | 0.04593090211 | 17448 |
| refit | Q2 | 0.2225146927 | 0.2167546385 | 0.2109884837 | 26113 |
| development | M1 | 0.031 | 0.0299692623 | 0.02841530055 | 355 |
| development | M2 | 0.05797546012 | 0.05928392532 | 0.05956284153 | 242 |
| development | Q1 | 0.04646666667 | 0.04455259563 | 0.0325136612 | 390 |
| development | Q2 | 0.1056666667 | 0.1005293716 | 0.1040983607 | 483 |


Full16-channel statistics and counts of affected stock-windows/origins: `channel_by_role_quality.csv`. Slot/year exposure: `fallback_by_slot_year.csv`. Unique per-role stock/year source ages and genuine open/close/extrema/volume support: `source_age_by_role_stock_year.csv`; maximum terminal input-price age is5minutes. Original source-year census including startup: `source_quality_by_year.csv`; its source-wide counts are not admitted-role counts.

Zero volume and absent-minute-assumed-zero are distinct. Hour volume uses genuine observed sums; up to5absent minutes may contribute0 only for allowed feature computation. This remains a lower bound, not evidence of no trading. Conflict/quarantine/invalid volumes remain unknown. Q2 daily volumes require six usable full hours, omit the closing stub and reset across share regimes. No invented inverse-split volume conversion. The daily close proxy is genuine15:30 last-full-hour close, not official16:00. Partial observed extrema are not certified full-hour extrema; no synthetic OHLC component is relabeled genuine.

Missing-at-completion and proxy-age information is logically knowable only after the relevant scheduled minute/hour under the assumed feed clock; historical actual availability is not independently verified. P019B anomaly/action quarantine flags are retrospective QA and cannot be declared contemporaneous input features without known-at evidence. A price repeated because of a cap5 proxy differs from an observed unchanged price; flags retain that distinction outside the learned16channels. We measured support/age, not a full causal provenance certificate for every vendor action.

## What is retained and what is lost

| Distinction | Evidence label | Evidence / limitation |
| --- | --- | --- |
| M2 origin1/2 and Q1 same-slot context | VERIFIED_ALREADY_AVAILABLE | formulas/code; no claim all timing absent |
| Absolute historical volatility | VERIFIED_ALREADY_AVAILABLE | V1/V2 are log causal RMS, not only normalized shocks |
| Own history versus panel information | VERIFIED_ALREADY_AVAILABLE_WITH_DIFFERENT_BOUNDARIES | T2 own16; A7/A12 add mean20scaledM1/median20scaledV1 with self inclusion |
| Native missing versus ordinary fallback value | VERIFIED_LOST_IN_MODEL_REPRESENTATION | masks separate; substituted median can match genuine median; no17th mask input |
| Exact elapsed wall-clock gap | NOT_EXPLICITLY_INPUT / PARTLY_INFERABLE | 48scheduled slots cross overnight/holiday; M2/Q1 encode some calendar context, not a full timestamp sequence |
| Intrahour path order / timing of highs and lows | VERIFIED_LOST_IN_HOURLY_AGGREGATION | source contains minute path; hourly FT16 consumes aggregate hourly/daily operands |
| Minute RV, observed-minute counts, volume path | VERIFIED_AVAILABLE_SOURCE / NOT_TESTED_FOR_PREDICTIVE_VALUE | bounded offline cases; no learned encoder or new feature store |
| True publisher timing, full-volume authenticity, action vintage | SOURCE_UNVERIFIED | no entitlement/publication certificate inferred from technical PASS |

`minute_path_observability_cases.csv` contains eight genuine60-minute hour paths: AAPL/VZ,09:30–10:30 and10:30–11:30 on2015-11-02 and2025-07-15. `minute_read_manifest.json` binds exactly two pre2026 canonical monthly files and cap5 support files. The eight paths each have60genuine minutes and no observed-zero volumes; that selected-case fact does not certify the broader tape. Early/late movements, minute realized variation and high/low timestamps are actual descriptive source statistics. For example AAPL2025-07-15 second hour reverses from early−0.003814 to late+0.009887 log movement. Permuting interior minute order while preserving first open/last close/extrema/summed volume leaves hourly OHLCV (and subsequent hourly FT16) unchanged, so these path details are structurally unrecoverable. No source is permuted in storage and no predictive feature test is performed.

`preserved_source_witness_checks.csv` adds22 archived source cases including actual proxy/fallback differences. `ranking_quality_stock_strata.csv` and `matched_stock_quality_strata.csv` describe existing prediction errors by quality; no exclusion or quality cutoff is chosen. All20 self-including panel proxies are endogenous summaries, not independent index observations or peer-causal identification. An information-matched18-input plain control is absent.
