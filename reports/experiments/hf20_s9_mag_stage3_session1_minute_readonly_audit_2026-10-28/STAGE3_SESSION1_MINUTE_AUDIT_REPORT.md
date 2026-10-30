# HF20 Stage3 Session1 — minute-source and representation audit

**Status: PARTIAL — metadata/count audit completed; full minute-path verification SOURCE_PERMISSION_BLOCKED.** No neural starts, optimizer phases, calibration/baseline fits, model forward passes, forecast scores or outcome-based feature selection. Ledger remains **166/300**, with134 unspent capacity and no future fit permission. This report does not promote a model or change a protocol.

The pinned canonical minute files are locally present according to a pre2025 receipt-member existence/size check. The verified S4 grant/receipt is **genuine minute endpoints**, while recent Design A grants reuse adjusted hourly and saved endpoint/component artifacts. Neither establishes a current full-path feature-read grant. Consequently no raw/canonical minute contents were opened, and no minute OHLCV reconstruction, sequence validity or numerical feature calculation was performed. The absence of current permission is distinct from absence of files.

## Executive feasibility and five decisions

| Arm | Evidence / current verdict | Human recommendation |
| --- | --- | --- |
| S3-B compact minute statistics | Hour geometry and saved count support audited; full paths/value/latency proof blocked. Seven-channel unapproved proposal attached. | **CONDITIONAL** design discussion; **BLOCKED for fitting now** until an explicit bounded minute-source grant and value/mask checks. |
| S3-C newest-hour minute encoder | Correct newest block proven; strict complete20 latest-hour admission loses most sampled origins. Masked sequence could structurally preserve keys, but is not certified. | **CONDITIONAL** masked late-fusion proposal; **BLOCKED for fitting now**. Resolve timeliness, normalizers and fair controls first. |
| S3-D all48-hour hierarchy | Exactly2,880 expected minute positions/stock/origin, real closures excluded; full-path/activation costs unresolved. | **DEFERRED / CONDITIONAL** later Session3 only, following B/C evidence and a separate resource/design grant. |
| S3-E market context | Own-panel context has historical code antecedents; independent USA500/external context is not established for these masks. | **DEFERRED**; external context presently **BLOCKED** without its own source/as-of approval. |

1. **Source available?** Canonical historical files exist (174 receipt members;583,710,999 bytes), but only their filenames/existence/sizes were checked. Current unrestricted path-read permission is not established. Adjusted-hourly metadata and saved genuine endpoints do not expose a full genuine minute path.
2. **How much within-hour information?** In **26,880 unique sampled stock-hours**, 1,600,640/1,612,800 expected minute positions are genuine by saved hourly counts (**99.2460%**); **88.9769%** of stock-hours are complete. These are exact counts in a deliberately stratified sample, **not population estimates** or freshly validated minute records. Complete20 full48 support is0 in all sampled role windows. Latest-hour complete20 support is5/134 sampled OOS origins. Population intersections and actual consecutive-return support remain unverified.
3. **Which summaries?** Propose five content distinctions—absolute realized minute variation, semivariance contrast, equal-half variation timing, directional efficiency, last15 scheduled-minute volume share—plus two explicit observation-validity masks. See ordered MIN01–07 contract. No target correlation or performance screening.
4. **Latest-hour encoder without key loss?** A fixed masked60-position input with explicit observed/return/volume masks and an all-missing branch can preserve the original keys structurally. This is **not proof of certified usable inputs**. A strict-complete rule would alter the cohort. Compare against CLOCK-C3, B's different full48-hour summaries, and preferably a separately approved simple newest-hour summary control with matched fields/reach; capacity attribution remains qualified.
5. **Ready for combined fitting?** **No.** First approve exact source scope, action/latency interpretation, masks/fallbacks/phase normalizers, model contracts and whether a third matched control is included. B+C normally require8 starts/16 phases; a third four-fold neural control would add4 starts and needs explicit approval. No capacity has been reserved or consumed here.

## Source-of-truth and access map

All paths below are repository-relative. Executed code/masks govern over older prose.

| Assertion | Authoritative artifact / code inspected | Scope and qualification |
| --- | --- | --- |
| Pinned source | `configs/hf1m_p019_action_scan_v1.json`; `configs/hf1m_long_ft16_v1.json`; methodological handoff§2.1a | HF dataset `mito0o852/OHLCV-1m`, revision `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`; original vendor/feed/rights not independently verified. No internet research. |
| Current historical read footprint | `reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation/opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv` |174 adjusted-hourly partitions(39,431,072 bytes) plus174 canonical-observed minute partitions recorded for **endpoints**. All members2010-07..2024-12. No old acquisition manifest/whole-source loader invoked. |
| Existing local minute format | Receipt paths `data/processed/hf20_hf1m_long_v1/<revision>/qa_v2/canonical_observed/YYYY-MM.parquet` |174/174 present; file-size sum matches receipt. Parquet fields/QA semantics inferred from source writer, not newly schema/value-certified. Raw selected store path is documented, not independently inspected. Canonical-observed QA is upstream of P019B action adjustment/quarantine; no ready-to-use fully adjusted minute-input store is certified. Future legal projections must apply the exact saved hourly-compatible source/action rules, not assume those two namespaces share a price basis. |
| Source/action semantics | `S4_SOURCE_POLICY.json`; `configs/hf1m_action_qa_v1.json`; `hf1m_action_source.py:adjust_prices,reaggregate` | Historical March2026 split-consistent OHLC basis, not dividend-total-return/auction certification; volume as reported. No2026 observations read to inspect this metadata. COP2012-05-01 compatibility boundary, quarantine/conflict rules preserved. |
| Hour mapping | `hf1m_ft16_math.py:build`; `hf20_s4_preflight.py:run`; `hf20_s4_witnesses.py:assemble` | Drop stubs; origin maps to completed hour-end; opening maps to previous grid end; saved `first_step=entry_index−47`. |
| Clock/calendar | `hf20_s4_clock.py:sessions,schedule`; `hf20_stage2_bcd.py:clock_values` | XNYS UTC instants, ET slots/DST, actual early closes; schedule-based crossing; no price-dependent routing. |
| Frozen roles | Stage1 Session2B `amendment.json`; Stage1 O1 `role_indices.npz`; S2-B `protocol.json` |20 exact annual role arrays, original cutoff/maturity/first-input embargo checked without outcome values. O1 role metadata reused, not its target/loss/model. |
| FT16/fallbacks | `hf1m_ft16_math.py`; `hf1m_ft16_fit.py`; S9 methodological handoff§2 | Original16 remain; no fitting invoked. Hourly source availability and native-feature fallback are distinct. |
| Known source heterogeneity | Completed C/D coverage audit receipt/narrative; completed C-A and masked-gap source handoffs | Genuine endpoint MS/MRK/MA sensitivity does not imply the same minute-path pattern. This audit's bounded input-count sample also finds AVGO concentration. No label values/diagnostic score stores opened. |
| MIN-0/1/2 design antecedents | `docs/track_a/brainstorm/HF20_Focused_Second_Pass_Ranking_Inputs_Minute_Data_and_Horizons_2026-10-24.md`§5 | Methodological proposals only; no feature or fit approval. Stage3 S3-B/C names are distinct from older roadmap S3 horizon experiments. |
| Preservation / budget | Current registry, new S2-D journal, sixteen scoped preexisting hashes/mtimes |166/300, zero starts here; registry/journals unchanged. Existing dirty S2-D edits preserved. |

**Permission decision:** historical endpoint access and a physically mounted canonical file are insufficient authority to broaden its purpose to path features. Full-path sampling is therefore **SOURCE_PERMISSION_BLOCKED**, not a failed minute-quality test. A later grant should name this revision/qa_v2,2010-07..2024-12, projected timestamp/ticker/OHLCV/RTH/source-validity fields, bounded blocks and applicable action/quarantine policy; no retrieval or2025/2026 content is needed. The present audit does not grant that permission.

## True48-hour geometry and as-of convention

The projected pre2025 canonical grid contains **21,807 distinct full60-minute rows**. Every admitted role origin selects exactly48 consecutive *scheduled full-hour* positions: **2,880 expected minute cells per stock**, not48 elapsed wall-clock hours. Normal sessions contribute six full hours;13:00 early closes contribute three. The normal15:30–16:00 and early-close12:30–13:00 stubs are source/endpoint bars, never recurrent input rows. Overnight, weekends and holidays introduce gaps in wall time, not synthetic trading-hour rows.

| origin ET | newest FT16 full block | exception / convention | age at origin |
| --- | --- | --- | --- |
| 09:30 | Prior scheduled session last full hour | 14:30–15:30 on normal prior day;11:30–12:30 after13:00 close | 18–90h in geometry examples |
| 10:30 | 09:30–10:30 current session | same on early closes when present | 0 |
| 11:30 | 10:30–11:30 current session | same | 0 |
| 12:30 | 11:30–12:30 current session | same;13:00 close stub excluded | 0 |
| 13:30 | 12:30–13:30 current session | not a candidate after13:00 close | 0 |
| 14:30 | 13:30–14:30 current session | not a candidate after13:00 close | 0 |
| 15:30 | 14:30–15:30 current session | not a candidate after13:00 close | 0 |

For bar start `u`, genuine minute timestamps are starts `u+k·1min`,k0..59; each interval ends one minute later. All input intervals must finish no later than the saved origin, with historical publication assumed by approximately origin+2minutes. Stored `completed_at_utc==hour_end_utc` is a construction timestamp, **not an observed vendor-arrival timestamp**. Same source-minute evidence supports a price reference; it does not independently prove historical arrival by that time. At09:30 no current-session minute is a completed input hour. The label's09:30 source open and original target endpoint remain unchanged and were not read numerically.

Across the saved geometry examples, opening newest-hour age is18–90 wall-clock hours; nonopening origins have age0. Full48 history spans about9.25–13.88 calendar days in these examples. `sample_input_geometry.csv` contains274 unique representative/early-close origin geometries with role bindings; it is not a new index mask. An early-close morning origin can already be OVERNIGHT even before12:30. All14 saved OOS early-close origins were inspected as calendar/key metadata, never as outcome values. The unchanged CLOCK vector is seven nominal-slot one-hots, remaining scheduled trading minutes/240, schedule-only crossing boolean, and calendar days to next scheduled session/7; it has10 fields, fixed scaling and no fitted calendar values.

For both future representations, the candidate minute set is `[hour_start,hour_end)` for these exact blocks, not all data on the origin date. A future minute reader must apply the block cutoff before feature arithmetic, reject duplicate ticker/timestamps, and exclude any not-yet-completed interval; no next minute, future full-day high/volume, close, open or component can enter.

## Frozen phase population checks

Read-only checks reproduce **4,013 OOS origins /793 sessions /80,260 stock-origin keys**. The stock order is `VZ,COP,BAC,BA,AAPL,PEP,MRK,SBUX,CVX,MS,AMD,KO,JNJ,AMZN,XOM,WFC,AVGO,TSLA,MA,CSCO`, not alphabetical. No score Parquet was opened to establish these counts; they come from saved role indices and canonical source-origin metadata. CLOCK-C3 is contract-bound to this same role archive; an independent fresh key-column join to its saved score files was not repeated and remains a future pre-fit check.

Initial cutoffs are2020-06-30/2021-04-30/2022-05-31/2023-05-31. Nominal selector starts areJuly2020/May2021/June2022/June2023; restricted cutoffsSeptember2020/21/22 and2023-09-29, with F23 actual last eligible2022-09-27. October–December stays independently reserved. Each saved role satisfies its original strict label-maturity timestamp boundary (ET midnight+1day−4hours, i.e.20:00ET) and first-of48 input-date embargo. No split is recomputed from target values or moved for minute coverage.

| fold | role | first | last | sessions | origins | stock_rows | sampled_origins |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F21 | inner_train | 2011-04-01 | 2020-06-30 | 2100 | 11449 | 228980 | 46 |
| F21 | selector | 2020-07-13 | 2020-09-30 | 57 | 349 | 6980 | 14 |
| F21 | restricted_refit | 2011-04-01 | 2020-09-30 | 2164 | 11846 | 236920 | 60 |
| F21 | calibration | 2020-10-12 | 2020-12-30 | 56 | 283 | 5660 | 16 |
| F21 | oos | 2021-01-13 | 2021-12-31 | 188 | 955 | 19100 | 32 |
| F22 | inner_train | 2011-04-01 | 2021-04-30 | 2301 | 12560 | 251200 | 76 |
| F22 | selector | 2021-05-12 | 2021-09-30 | 58 | 278 | 5560 | 14 |
| F22 | restricted_refit | 2011-04-01 | 2021-09-30 | 2366 | 12888 | 257760 | 90 |
| F22 | calibration | 2021-10-12 | 2021-12-31 | 50 | 245 | 4900 | 18 |
| F22 | oos | 2022-01-12 | 2022-12-30 | 210 | 1180 | 23600 | 31 |
| F23 | inner_train | 2011-04-01 | 2022-05-31 | 2526 | 13776 | 275520 | 108 |
| F23 | selector | 2022-06-10 | 2022-09-27 | 59 | 313 | 6260 | 14 |
| F23 | restricted_refit | 2011-04-01 | 2022-09-27 | 2592 | 14137 | 282740 | 122 |
| F23 | calibration | 2022-10-13 | 2022-12-30 | 48 | 258 | 5160 | 17 |
| F23 | oos | 2023-01-13 | 2023-12-29 | 187 | 887 | 17740 | 28 |
| F24 | inner_train | 2011-04-01 | 2023-05-31 | 2719 | 14824 | 296480 | 139 |
| F24 | selector | 2023-06-12 | 2023-09-29 | 69 | 291 | 5820 | 14 |
| F24 | restricted_refit | 2011-04-01 | 2023-09-29 | 2795 | 15167 | 303340 | 153 |
| F24 | calibration | 2023-10-11 | 2023-12-29 | 40 | 163 | 3260 | 14 |
| F24 | oos | 2024-01-11 | 2024-12-31 | 208 | 991 | 19820 | 43 |

These are full existing populations, distinct from sampled minute-count coverage. Equal20 stock within origin→equal origins/session→equal sessions/year→equal years remains the future primary score hierarchy. Category diagnostics would condition and renormalize within each year, not impose50/50 intraday/night mass. No evaluation, bootstrap or tail cohort was formed here.

## Bounded coverage audit: what was measured

**Evidence basis:**16 prespecified monthly adjusted-hourly files; only timing/count/quality fields projected, **zero OHLCV payload columns**. For each exact fold-role×month×slot×normal/early stratum, select lower-middle and last eligible origin with all48 grid blocks within the month. Selection uses keys/calendar, never quality counts or outcomes. This yields **210 unique origin windows**,1,049 overlapping fold-role occurrences,1,344 unique historical input hours and26,880 stock-hours. Observations are not independent and role rollups must not be added together as a new population.

Requested months:2011-04,2012-05,2015-06,2018-11,2020-07,2020-11,2021-05,2021-11,2022-06,2022-11,2023-06,2023-11,2024-03,2024-07,2024-11,2024-12. **2012-05 and2024-11 contribute zero retained sample windows** under the fixed original-role/within-month geometry filter; this does not mean those months have zero minute observations. COP's historical dependency exclusions and sparse eligible month segments limit this design; no replacement month was chosen based on quality.14 months have retained source blocks. Earlier/middle/later history and all four OOS years are represented, but month-boundary windows and full seasonal coverage are not certified.

Retained block start/end: **2011-04-06T18:30Z–2024-12-31T16:30Z**. Source count/timing column projections opened the16 whole monthly nonstub metadata tables before retaining the needed keys; therefore source-metadata decode scope includes other rows in those allowed months. The full-month count/timing decode boundaries are2011-04-01T13:30Z–2024-12-31T20:30Z; these are metadata, not the retained sample bounds. No market price/volume values, labels or future directed returns were decoded. No retained source block ends after its sample's origin; no post-cutoff metadata enters a sample summary. This is not a full-history or within-minute inspection.

Unique sampled counter conservation: **1,612,800 expected =1,600,640 genuine +12,143 absent +17 conflicting +0 invalid +0 quarantined**. Legacy cap5 `proxy_count` totals12,034 placements; those overlap the unobserved positions and must **not** be added to genuine or missing totals. They are historic input computation proxies, not genuine minute paths. This audit creates no synthetic observations. Sample quarantine0 does not contradict the historical policy's18 quarantined RTH records: those are different coverage universes. Exact-duplicate collapse, invalid positivity/ranges and quarantines are inherited source-writer semantics, not independently revalidated minute-by-minute.

| ticker | blocks | missing | complete_fraction | ge54 | ge57 | ge59 |
| --- | --- | --- | --- | --- | --- | --- |
| ALL20 | 26880 | 12160 | 88.977% | 97.693% | 95.885% | 93.270% |
| AAPL | 1344 | 5 | 99.702% | 100.000% | 100.000% | 99.926% |
| AMZN | 1344 | 883 | 79.836% | 97.396% | 93.527% | 86.682% |
| AVGO | 1344 | 5288 | 33.929% | 76.488% | 61.012% | 46.057% |
| MA | 1344 | 3591 | 48.512% | 84.896% | 73.958% | 62.426% |
| MRK | 1344 | 70 | 95.982% | 100.000% | 99.926% | 99.256% |
| MS | 1344 | 143 | 93.304% | 100.000% | 99.628% | 97.619% |
| XOM | 1344 | 1 | 99.926% | 100.000% | 100.000% | 100.000% |

AVGO and MA account for8,879/12,160 missing positions (73.02%) in this unique-hour sample. MS/MRK have different patterns here than in genuine future-component availability; do not transplant label-support conclusions to input paths. Minimum/median complete-hour share across20 sampled stocks are33.93%/96.02% (not an eligibility gate). Missingness is not assumed random. Observed zero-volume/unchanged minute frequencies, within-hour ordering, exact gap placement and source-staleness causes cannot be inferred from these aggregates. No volatility-proxy screening was performed.

**Newest-hour OOS sample intersections** (all20 completeness is a hypothetical source restriction, not an approved panel):

| fold | sampled_origins | full48_complete20_origins | newest_complete20_origins | newest_complete_stock_fraction |
| --- | --- | --- | --- | --- |
| F21 | 32 | 0 | 1 | 90.938% |
| F22 | 31 | 0 | 1 | 91.129% |
| F23 | 28 | 0 | 1 | 88.571% |
| F24 | 43 | 0 | 2 | 86.744% |

The134 sampled OOS origins contain2,680 newest stock-hours:159,614/160,800 genuine minute positions,2,389/2,680 complete stock-hours (89.14%). Fractions with at least54/57/59 genuine minutes are97.91%/95.60%/92.91%. Thresholds54/57/59 are illustrative count diagnostics only, not selected future gates; they do not prove enough consecutive pairs or complete volume. Complete20 newest-hour support is5/134; complete20 full48 support0/134. These are **not** projected OOS attrition estimates. A full-key source-verified masked tensor remains an unverified prerequisite.

Newest-hour sampled OOS exposure by origin (stock-hour counts, no forecasts):

| origin_slot | blocks | expected | observed | missing_unobserved | complete | complete_fraction |
| --- | --- | --- | --- | --- | --- | --- |
| 09:30 | 420 | 25200 | 24988 | 212 | 371 | 88.333% |
| 10:30 | 420 | 25200 | 25112 | 88 | 387 | 92.143% |
| 11:30 | 380 | 22800 | 22678 | 122 | 347 | 91.316% |
| 12:30 | 400 | 24000 | 23805 | 195 | 355 | 88.750% |
| 13:30 | 340 | 20400 | 20194 | 206 | 286 | 84.118% |
| 14:30 | 360 | 21600 | 21386 | 214 | 317 | 88.056% |
| 15:30 | 360 | 21600 | 21451 | 149 | 326 | 90.556% |

Hour-position buckets1–32,33–47 and48, all-stock fold/role/month/slot rollups, all20 stock/month rollups and OOS stock/slot rows are in `minute_coverage.csv` (2,849 rows). It is an explicitly mixed-rollup table: filter `aggregation`; do not sum across rollup types. The CSV's `windows` denotes stock-window exposures when pooled over stocks. `observed` means saved genuine counts, `synthetic` means legacy proxy placements, `missing_unobserved=expected−observed`; cause fields conserve missing mass. Neither proxy positions nor volume-zero assumptions are certified observed input.

For era context, `sample_era_summary.csv` uses **F24 restricted-refit sampled stock-hour exposures**, not unique hours or full-era rates: complete-hour shares range78.35% in sampled June2015 to97.55% in sampled November2018. This is descriptive coverage variation, not a feature-selection result or market-regime model. Early-close calendar geometry is exhaustive on saved OOS keys; minute-quality coverage on early-close blocks is sampled only. No small sample can certify all stock×month×role interactions. Additional unique-input-hour rollups in `input_hour_calendar_quality.csv` separate actual input-block session type, ET source-hour slot and year×stock: early-close blocks300 stock-hours,17,884/18,000 genuine positions,90.00% complete; normal blocks26,580,1,582,756/1,594,800 genuine positions,88.965% complete. They are not outcome-origin performance groups. Saved terminal minute age is0–5minutes on these sampled blocks, with no unknown age, consistent with the original cap5 terminal-source rule. Counts alone bound genuine adjacent-close pairs between1,561,600 and1,573,760 across the sample (vs1,585,920 at60/60 throughout); exact gap positions and usable numeric return pairs remain unverified.

## Source QA, fallback and reconstruction limits

- Canonical source code removes all conflicting versions at a ticker/minute, collapses exact duplicates and requires positive finite internally consistent OHLC plus finite nonnegative volume. P019B additionally quarantines unresolved minutes; an empty or bad minute is not a no-trade bar.
- `close_input_cap5` may carry a legal recent close for a short missing terminal run, within its strict source/action limits. It cannot become an observed minute or genuine target price. Original high/low and volume quality rules differ from terminal-price eligibility.
- Existing FT16 volume sums may treat limited absent minutes as zero for computation, with explicit lower-bound flags and no unknown-conflict/quarantine bin repair. This is not evidence of actual zero volume. No fabricated minute volume is proposed for S3.
- Native FT16 masks exist separately: unbounded feature fallback uses the legal prefix median (normalized zero); B2/T2/T5 use neutral0. Deficient all48 price eligibility cannot be repaired by fallback. Future minute masks cannot use future target/endpoint/component support.
- Retrospective source issue IDs/quarantine/action classifications and saved quality tiers are not proven historically observable at issuance. Treat them as source provenance controls; a causal mask must be specified from timely observations or explicitly qualified as a historical timing proxy. Vendor revision/arrival timestamps are not available from the inspected fields.
- **Minute-to-hour OHLCV reconciliation: BLOCKED by permission.** Static aggregation code uses genuine first/last boundaries, observed extrema/volume and specific quality handling. That mathematical recipe is not an independently executed identity check. No exact-match assertion, zero-volume claim or source repair is made. Positive/finite minute checks and duplicate-timestamp checks remain required after a future read grant.

## Proposed representations and fair later study

The attached S3-B contract orders MIN01–07 (five content statistics+two validity masks), exact59 adjacent-close return convention, fixed equal-half boundaries, lawful phase normalizers and no cohort drops. Strict60 applies to **feature validity**, not primary-row admission. Content redundancies with FT16 are explicitly excluded. Values/degeneracy have not been screened or calculated.

S3-C proposes60×7 newest-block channels (scaled adjacent return, range, activity, three masks and position), shared H8 minute LSTM and late fusion into the unchanged hourly H32/10-clock head. All-missing embedding0; no invented minute. This architecture is a proposal, not code or approval. Opening newest-hour age is audited metadata, **not an extra eighth learned channel**; adding an age input later would need an explicit contract change.

Strongest scientific controls remain frozen C0/C3/CLOCK-C3 and, for future S3-C representation attribution, a same-newest-hour simple summary control with the same underlying fields/masks. S3-B supplies statistics over48 hours and is **not information-reach-matched** to newest-hour C. Without an approved summary/capacity control, claim only a representation+information+capacity package comparison. Prior S2-C and S2-D are preserved; S2-D is a different gap task and its numerical loss must never be compared as a4h improvement.

## Analytic resource envelope and later boundaries

No model instantiated, timing benchmark, tensor cache or training performed. Counts below describe proposed float32 shapes, not allocations or measured future RAM/runtime. Existing caps:2GB process /2.5GB new-task /15GB project. Last completed S2-D report had~12.44GB project use; no broad storage traversal was run here. Current filesystem free space is not a substitute for the project cap.

| Design | Proposed parameters | Dominant recurrent arithmetic / stock-origin | Dense OOS-only extra representation if duplicated per key |
| --- | --- | --- | --- |
| Frozen CLOCK |6,443|294,912 multiply-adds/hourly48 sequence|reference|
| S3-B seven channels|7,339 (+896)|337,920 (~1.146×)|107,869,440 bytes for80,260×48×7|
| S3-C example H8 minute encoder|6,995 (+552)|+28,800 minute MACs (~1.098× old recurrence total)|134,836,800 bytes for80,260×60×7|
| S3-D example shared H8 all48 blocks|8,011 (+1,568)|1,726,464 (~5.854×)|6,472,166,400 bytes for80,260×48×60×7 — exceeds task/process caps|

S3-D parameter estimate assumes concatenating8-minute embeddings to each original16-dimensional hour, then H32 and unchanged clock head; a different fusion changes it. A maximum16-session×7-origin×20-stock batch contains2,240 stock windows. Raw minute input tensors are~3.76MB for C and~180.63MB for D before gradients/activations; full autograd and recurrent CPU overhead remain unmeasured. Unique full-grid hour/stock caching at60×7 float32 would be~732.7MB even before index/source/feature buffers; do not create it here. B's unique-grid extra seven summaries would be~12.2MB; lawful streaming/reuse is preferable to repeated origin-window caches. A later2GB readiness check must include source loading and activations; no runtime promise follows from MAC ratios.

Full source-quality enumeration would project174 pre2025 canonical partitions (receipt compressed total583.7MB) plus source/action masks; logical60-minute-grid joins cover about26.17million expected stock-minute positions across21,807 grid hours, reused by many origin windows. This is a workload estimate, not exhaustive verified coverage; exact file row counts/decoded memory and all-history minute support were not measured. Future sampling should precede any full scan/materialization.

Future B+C budget plan only:8 charged selector/refit pairs /16 phases, one seed, no grids.166+8=174/300 if separately approved and all gates pass. No journal/pointer change here. S3-D/E each need their own design, source/resource and fit approval after B/C review.

S3-E inventory: historical P028/panel-state and peer code can calculate endogenous common-state means/dispersion from the fixed20 inputs; these are not an independent market index. Source/as-of/missing-stock normalization and identical-information linear/clock controls would be needed. `state_screen_source.verify_support` and broad old discovery/parent verifiers must **not** be called here because their old scopes include2025/protected bindings. `market_source.py` marks the older SPY adapter's research status BLOCKED/available-at UNKNOWN; it is not HF20 four-fold permission. No independent USA500 pre2025 as-of overlap has been established. No source acquisition or market-state values inspected; keep E deferred.

Future evaluation concepts only: original4h raw-A MSE primary, annual/equal-year matched metrics, MAE/calibration, within-origin magnitude ordering, seven clocks/early closes, original matured prefix95/99 cohorts and complements,400 whole-month paired draws/seed22042 under original weights. No metrics, labels, tail thresholds or bootstrap draws were computed now. Stage5 ranking-loss training is deferred.

## Readiness gates requiring a later explicit decision

1. **Source grant / verification:** authorize bounded full-path projections of the pinned pre2025 canonical source, then establish numeric validity, unique timestamps, consistent action basis, actual minute→hour checks and gaps/zero activity. No hourly proxy substitution.
2. **As-of policy:** resolve whether origin+2min publication proxy and retrospectively curated quarantine/action basis are acceptable for this exploratory representation comparison; no claim of verified execution latency.
3. **Input contract:** freeze the seven S3-B fields and exact masks/fallbacks; C's seven channels,H8 late fusion, all-missing behavior/dropout and phase-only volume normalizer. These are unapproved proposals, not implemented features.
4. **Population:** verify all original keys can be represented under the approved masked policy. Full-history intersections remain unknown. If not, stop or obtain prospective common-support approval—never silently drop difficult outer keys or substitute a new label horizon.
5. **Fairness/budget:** decide whether to authorize a simple newest-hour summary/capacity control in addition to B/C, or qualify attribution. Approve exact starts/resource/single-use protocol only in the later prompt.

**GO:** review the metadata evidence and proposals. **CONDITIONAL:** B/C after the five gates. **BLOCKED now:** any minute-feature fitting/inference, minute-value certification or model comparison. **DEFERRED:** D/E and Stage5. No human experiment choice is made by this audit.

## Verification, preservation and files

Exact checks:20 saved role geometries;48 consecutive full-hour lengths;allOOS count/axis identity;embargo/maturity and last-input≤origin;count conservation;sampled hour-stock uniqueness;completion/end and observed first/last timestamp bounds;all source revision metadata;existing receipt-member sizes;read-only166 ledger. Within-minute duplicate/positivity/zero-volume/reaggregation checks are **NOT VERIFIED**, not PASS. No synthetic learned signal, new source/feature store or future outcome used.

Sixteen scoped existing assets' SHA256/mtimes are preserved, including dirty S2-D module/test/handoff, current registry/journal, source policy/receipt/origin mask and role archive. The mixed-date grid is projected only through2024 and **not content-hashed**. There was no broad all-artifact hash sweep. Git HEAD remains997b30cff98785911b0e33b7e3d2e72f61b8270b on `feat/track-a-data-intake`; cached upstream0/0, not freshly fetched. Existing registry/S2-D uncommitted work remains unchanged; only this new namespace is written.

Lightweight inline `.venv/bin/python -B` projections/aggregations and assertions produced the audit. `git diff --check` passes; no full-repo Pylance, Ruff/test sweep, library/model import for training, checkpoint load, inference, optimizer or scorer was run. No package, environment, code, test, live config, registry or ledger change. Arrow's sandbox CPU-cache metadata warnings were nonfatal. No network/fetch/credentials/download/commit/push; no2025 market or2026 protected path/content/hash access. Existing documentation can mention those years as policy/vintage metadata without releasing them.

Files: this report;source access receipt;minute_coverage.csv;B/C proposals;readiness matrix;SESSION_HANDOFF.md;small role,unique-hour,era/slot and geometry supporting summaries;metadata_audit_summary.json. No per-minute export, outcome/score copy, model, plot, large manifest or new persistent Python module. All files are new/uncommitted, appropriate for researcher review before any separately authorized commit. The namespace handoff fulfills the current prompt's explicit write-only-here instruction; no additional existing/report directory was changed.

**STOP. No Session2/3 starts, calibration, source grant, winner selection, routing, trading/options work or protected confirmation is authorized or initiated.**
