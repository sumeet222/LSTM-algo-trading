# HF20 S9-MAG Exact Replication Supplement

Documentation extraction, 2026-10-27; inspected repository HEAD `5f7bb86a35d5aaff34ff79ef8f471117de6d3e42`, branch `feat/track-a-data-intake`. Scope: the four completed seed-42 **HF20 S9-MAG** lifecycles, F21–F24. This is an exploratory retrospective absolute-return-magnitude experiment, with no trading simulation or protected-2026 evaluation.

The executed code, saved recipes, role indices, configurations, checkpoint contents and binding records govern this specification. The existing [FT16 specification](HF20_FT16_Complete_Feature_Specification.md) supplies the detailed 16-feature formulas; this supplement specifies their S9-MAG application. Only this new document was written. Checkpoints were deserialized for inspection without model construction, forward inference or updates. No downloads, preprocessing, training, audits or tests were run, and no existing files were changed. The explicit one-file request overrides the additional session-report-file convention.

## 1. Identities and authoritative artifacts

These aliases below denote exact repository-relative directories, not alternate sources.

Unless explicitly identified as PyTorch package code, an unprefixed Python module reference such as `hf20_s5s9.py:60–67` means `src/lstm_data/hf20_s5s9.py` at those lines in the inspected repository version.

| Alias | Directory |
| --- | --- |
| `A18` | `reports/data_audit/ta018d_hf1m_long_2026-10-22_155547` |
| `P019B` | `reports/data_audit/ta019b_action_qa_2026-10-22_201224` |
| `P020` | `reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122` |
| `S4` | `reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation` |
| `S9` | `reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation` |
| `MAGxx` | `S9/HF20-S9-Fxx-H4-MAG-S42`, xx ∈ {21,22,23,24} |

All four `MAGxx/configuration.json` record the same input dimension 16, seed 42, initialization identity and execution hash. Each has `PASS.json`, two target recipes, two checkpoint bindings and four saved role score/metric bundles. `S9/S5_S9_VERIFICATION.json` records all 16 campaign lifecycles completed, including these four MAG runs. Do not substitute rehearsal outputs, proposal-only receipts or other S9 objectives.

- Source revision: `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`.
- Action namespace: `HF20_HF1M_LONG_v1_ACTION_QA_v1`; feature ID: `HF20_HF1M_LONG_v1_FT16_v1`.
- S9 execution SHA256: `e19fc1da419d6456d16a7dec7777bc7e1400b2d0412be65ba116906d01cfd73e`.
- S4 execution SHA256: `a737c9219513ddbbfffb882a2e76af7708e2f3ee55a297e1b145790bc47f2a95`.
- Recorded preparation/live-session starting Git HEAD: `960b81753036366522dbbd61189d4e4d51d25967` (`S9/START.json`, `reports/codex_sessions/2026-10-27_005216_hf20_s5_s9_live_final.md`). Execution included then-uncommitted files; that Git SHA alone is insufficient. Use the recorded execution hash and artifact bindings.

`src/lstm_data/hf20_s5s9_run.py:36–46` defines the S9 code hash from the S4 execution identity plus the `hf20_s5s9*` files; `hf20_s4_authority.py:21–41` defines the underlying source bundle. `S9/design.json`, `LIVE_AUTHORITY.json`, `EXECUTION_STARTED.json`, `S4_REUSED_RECIPES.json` and the v23 journal `reports/audit/track_a_real_pairs_v23_hf20_s5_s9.jsonl` bind the actual campaign. Earlier preparation status is not final execution status.

## 2. Dataset, acquisition and historical clock

### Provider, files and request semantics

The source is the Hugging Face dataset uploaded under **`mito0o852/OHLCV-1m`**: [dataset page](https://huggingface.co/datasets/mito0o852/OHLCV-1m). **NOT VERIFIED:** the uploader's original exchange/vendor feed, consolidation/feed tier, historical correction vintage and independent completeness certification. This was not an Alpaca, TwelveData, Yahoo or course USA500 download.

Acquisition code uses these immutable endpoints, where `REV` is the revision above and `YYYY-MM` the selected provider month:

```text
https://huggingface.co/api/datasets/mito0o852/OHLCV-1m/revision/REV
https://huggingface.co/api/datasets/mito0o852/OHLCV-1m/tree/REV?recursive=true&limit=1000
https://huggingface.co/datasets/mito0o852/OHLCV-1m/resolve/REV/data/ohlcv_YYYY-MM.parquet
```

There are **no server-side ticker/date/adjustment/bar-size query parameters**. Code scans monthly Parquet ticker columns and filters exact strings locally. Sparse reads add `?range_start=START&range_end=END` and HTTP `Range: bytes=START-END`, `Accept-Encoding: identity`; all seven source columns are selected from relevant row groups, `use_threads=False`. If projected selected-group compressed bytes exceed 75% of file size, the code uses a complete-month streamed download and its pinned SHA256 instead. Range reads validate returned range/size; full downloads validate complete size/hash. HTTP uses no login/credentials, `trust_env=False`, no automatic retries; recorded redirects/requests and per-month strategies are in `A18/months/YYYY-MM/{http_events.jsonl,raw_receipt.json,row_groups.json}` and the complete manifest. The threshold is a transport choice, not a sample filter.

Authority: `src/lstm_data/hf_minute_long_io.py:188–258,261–305,309–438` (`verify_remote`, `selected_table`, `stream_full`, `acquire_month`), `hf_minute_boundary_io.py:17–18,22–75` (`RemoteParquet`), `hf_hourly_source.py:41–104` (`PublicHTTP`).

**Stock-axis order, preserved everywhere:**

```text
VZ COP BAC BA AAPL PEP MRK SBUX CVX MS AMD KO JNJ AMZN XOM WFC AVGO TSLA MA CSCO
```

This fixed surviving-stock cohort is not historical index membership; survivorship/issuer lineage remains a qualification. No OOS performance-based stock selection is implemented in these runs.

### Distinguish acquired history from S9-used history

| Layer | Exact date/month policy |
| --- | --- |
| Activated minute acquisition | 189 monthly files, July 2010–March 2026; manifest `A18/complete_acquisition_manifest.json`. Earlier legacy acquisitions are excluded from the active source |
| P020 preparation | Warmup 2010-07-01–2011-03-31; original training 2011-04-01–2025-06-30; development 2025-07-01–2025-12-31; protected 2026-01-01–2026-03-31 |
| **S9 numerical source** | **Only July 2010–December 2024** monthly adjusted-hourly and genuine-minute partitions; no 2025 tuning or protected-2026 numerical access/hash. Source inventory: `S4/opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv` |
| S9 fitted samples | Expanding training prefixes beginning 2011-04-01; annual OOS years 2021,2022,2023,2024; exact admitted dates in §4 |

Nominal source bounds do not imply every stock/minute exists. Preserve the per-stock missingness and exact saved origin indices. The full stock/minute tape was not independently re-read for this document; per-symbol first/last genuine-minute timestamps are **NOT VERIFIED here**. Existing per-session coverage is bound by `A18/ticker_session_hour_coverage_manifest.json`.

### Timestamp and minute-to-hour construction

Raw schema is `timestamp: timestamp[ns,UTC]`, float64 `open,high,low,close,volume`, and string `ticker`; source rows/file/row-group identities are appended without overwriting raw values. The pipeline interprets timestamps as **minute starts**. Calendar is `exchange_calendars` **XNYS**, with actual holidays, early closes and DST. RTH minute starts are `[session.open, session.close)`; ET dates use `America/New_York`. Noncalendar/extended observations remain source evidence but do not enter hourly features or endpoint anchors.

Bins are anchored at 09:30 ET: offsets `floor(minute_of_session/60)`. Normal full hours are 09:30–10:30 through 14:30–15:30; a separate 15:30–16:00 stub is retained in source processing but excluded from FT16. A normal full-hour close at 10:30 means the close of the **10:29 minute**. Genuine hourly open requires an observation at the scheduled first minute; genuine close requires `hour_end−1 minute`. High/low are extrema of safe observed minute highs/lows, volume their sum. Partial observed extrema are not certified complete-hour extrema. Empty/missing scheduled positions remain indexed.

Authority: `src/lstm_data/hf_minute_boundary.py:70–80,223–237` (`validate_schema`, `session_grid`), `hf_minute_long_qa.py:48–88`, `hf1m_action_source.py:141–204` (`derive_month`); S9 source loader `hf20_s4_preflight.py:70–140`.

### Corporate actions and point-in-time limitations

Prices are backward split-consistent OHLC in the March-2026 share basis: for each applicable split at date e, divide prices strictly before e by `factor_denominator`; multiply factors when needed. Volume is unchanged. There is no dividend/total-return adjustment or fabricated inverse split-volume adjustment. The exact event facts are `configs/hf1m_p019_verified_event_facts_v1.json`, used by `configs/hf1m_action_qa_v1.json`.

Applied splits: KO 2012-08-13 ×2; MA 2014-01-22 ×10; AAPL 2014-06-09 ×7 and 2020-08-31 ×4; SBUX 2015-04-09 ×2; TSLA 2020-08-31 ×5 and 2022-08-25 ×3; AMZN 2022-06-06 ×20; AVGO 2024-07-15 ×10. COP's 2012-05-01 spinoff has no invented multiplicative adjustment: preserve levels in separate PRE/POST price bases and exclude dependent histories crossing the boundary. Split dates create separate as-reported share-volume regimes.

Authority: `src/lstm_data/hf1m_action_source.py:67–95,237–256`; COP/volume masks `hf1m_action_release.py:208–236`, S4 equivalent `hf20_s4_preflight.field_masks():25–54`.

**NOT VERIFIED:** historical arrival/publication times of bars, openings, corporate-action facts and corrections. Factors/quarantine decisions are retrospective. `configs/hf1m_long_ft16_v1.json` explicitly records `publication_timing_verified:false`. Origin+2-minute issuance is a proxy, not an exchange execution timestamp. Dataset access was based on human-reported maintainer permission for private research; redistribution and independent data rights are not certified by this supplement.

## 3. Data quality: source treatment versus feature treatment

### Source detection, filtering and correction

1. Parse timestamps in UTC; reject NaT, non-minute alignment and rows whose ET month differs from their file month. Require finite OHLCV, positive OHLC, nonnegative volume, high ≥ every OHLC value and low ≤ every OHLC value. Preserve genuine zero volume and rare/extreme candles otherwise.
2. Exact duplicates across the seven original fields collapse to one canonical observation. If distinct versions share `(ticker,timestamp)`, **all versions are excluded**, not first/last selected or averaged. Raw records remain immutable. The activated full-history acquisition report records no invalid raw rows or exact-copy duplicates, but 856 conflicting records / 406 keys excluded; these are full-source counts, not S9-only sample counts.
3. Compare expected XNYS minute grid against canonical observations to flag absence, conflict/invalid minutes, missing opens/closes, longest gaps, no-observation bins and coverage outside first/last source dates. No pre/post-coverage price history is invented.
4. Source QA flags absolute adjacent genuine-close changes >`log(1.25)` across overnight/month boundaries, genuine zero volume, and 30 consecutive same-OHLC zero-volume observations. These flags alone do not delete a genuine market move. Large jumps block original proxy creation in the affected bin.
5. P019 scans additional event candidates using: ALL_SESSION adjacent close and open/previous close; RTH adjacent close; minute body `abs(log(close/open))>log(1.25)`; minute high/low >1.5; session first-30/previous-session last-30 observed-close median ratio outside `[1/1.25,1.25]`. Comparisons are strict. Session medians are retrospective diagnosis only. External evidence/manual dispositions, not an automatic return cap, decide action treatment.
6. P019B's 67 candidate IDs resolve to 17 split-adjusted candidates, 4 genuine moves retained, 18 unresolved RTH minutes locally quarantined, 24 EH out-of-scope candidates, 3 KO mixed-basis premarket candidates excluded from RTH influence, and the COP spinoff boundary. Do not remove every detected jump. All five fields of the 18 RTH minutes are excluded; 14 affected hourly bins are reaggregated. Independently genuine scheduled opens/closes may survive; high/low and volume quality are untrusted, and **no proxy is allowed anywhere in an anomaly-containing hour**.

Exact dispositions/timestamps are in `P019B/unresolved_event_ledger_v3.json`, bound by `canonical_event_ledger_pointer.json` to SHA256 `015d672c11d61b3a14441a2abbfb689ffa59191016398bdc32bb580524a0b937`. This ledger, not the summary counts, reproduces the exclusions. Quality tiers are diagnostic metadata; the eventual S4 origin mask is the actual admission rule.

Sources: `src/lstm_data/hf_minute_long_qa.py:48–57,176–240,306–440`; `hf1m_action_audit.scan_stock():110–174`; `configs/hf1m_p019_action_scan_v1.json`; `hf1m_action_source.event_dispositions():98–138` and `derive_month():141–309`. Acquisition findings: `reports/codex_sessions/2026-10-22_184817_ta018d_hf1m_long.md`.

### Input close proxies and feature-level fallback

Original cap5 proxies are a separate derived layer, not genuine raw bars. A missing run can reuse its preceding observed close only when its completed-bin known length, including a leading carry gap, is ≤5 minutes. No future-price interpolation, overnight carry, no-observation-bin fill or action-blocked-bin fill occurs; state resets per session. A trailing short run remains accepted under the information known at that completion even if the next bin reveals a longer outage. P019B uses only a permitted terminal proxy for `close_input_cap5`, split-adjusted like prices; genuine `close` remains separate. Proxy OHLC/zero-volume placeholders do not become genuine extrema or observed volume. Sources: `hf_minute_long_qa.bounded_hour_proxies():92–118,395–403`; `hf1m_action_source.py:210–234`.

FT16 order is `M1 M2 M3 M4 V1 V2 V3 B1 B2 Q1 Q2 T1 T2 T3 T4 T5`; exactly 48 full-hour steps, no S5 clock metadata. Apply `S4/Fxx_{inner,refit}_recipe.json` as-is; `S9/S4_REUSED_RECIPES.json` records all eight hashes. Important distinctions from source cleaning:

- Hour volume is usable only with >0 genuine minutes, ≤5 absent minutes, longest gap ≤5, zero conflicts/quarantines/invalid minutes. Absent-minute zero is a feature-only assumption; volume remains an observed lower bound. Otherwise volume-derived channels become native missing. Daily volume requires six usable full-hour sums in one share regime; stubs excluded.
- Rolling windows keep scheduled gaps: required counts include 12/12 or 57/60 hourly OC returns, 60/63 daily returns, 19/20 matching-slot histories; maximum two consecutive misses. Indicators freeze/disconnect on missing closes and reset after three invalid full-hour positions or basis transitions. Full EMA/RSI seeding rules are in the FT16 specification and `stock_features.IndicatorState():44–96`.
- Fitted floors and volume pseudocounts use unique input-only eligible training-prefix keys; hourly/day volume pseudocounts are 1% of positive training medians by stock/share regime. An unfitted regime stays native missing. M2 uses matured prior regular-origin returns, seven contexts pooled equally 1/7, mean20/RMS60 with 19/20 and 57/60 coverage. No current or immature future outcome enters M2.
- Thirteen unbounded channels use native pooled median/unscaled MAD, then IQR/1.349, population SD, or constant scale 1 if necessary. Native nonfinite values receive the fitted center; B2/T2/T5 instead receive neutral zero and identity scale. No winsorization, input clipping or per-sequence normalization. B2 outside `1+1e-10` in absolute value is missing, not clipped. Masks stay outside the tensor.
- Feature fallback does not repair a deficient 48-input-close window to admit it. COP's 125-regular-session dependency plus 48-step envelope remains excluded. All fitted statistics are phase-specific, never fitted on validation/OOS. The original P020 2025-refit recipe must not replace S4's earlier annual recipes.

Authority: `hf1m_ft16_math.py:15–63,84–232`, `hf1m_ft16_fit.py:12–76`, `hf20_s4_fit.fit_expanded():13–125`, `hf20_s4_witnesses.py:19–56`, `hf20_s4_data.py:105–157`. See [HF20_FT16_Complete_Feature_Specification.md](HF20_FT16_Complete_Feature_Specification.md) for exact feature-by-feature mathematics.

### Missing target endpoint prices

Targets require **positive finite genuine prices for all 20 names** at both exact endpoints, plus COP price-basis compatibility. A missing/quarantined endpoint in one stock invalidates the **entire origin's 20-stock label panel**. No target median fill, price proxy, forward/backfill, nearest-time substitution, external daily price or endpoint shift is used. Historical bad/missing endpoints similarly leave scheduled holes in M2, subject to its coverage/fallback rules. Missing intermediate hour/16:00 closes can make decomposition unavailable without invalidating a direct return whose two exact endpoints are genuine. Authority: `hf20_s4_clock.complete_prices():73–77`; `hf20_s4_preflight.py:143–151,219–268`; `hf20_s4_opening.py:145–160`.

## 4. Samples, splits, maturity, embargo and weights

### Origin and sequence construction

Candidate regular-session ET clocks are **09:30,10:30,11:30,12:30,13:30,14:30,15:30**, only when strictly before the actual session close. Context IDs are 6 for opening, then 0–5 for the six full-hour ends. From nominal origin t consume **240 actual XNYS trading minutes**, including closing stubs and pausing across overnight/weekend/holiday closures. Normal exits for the seven clocks are respectively 13:30,14:30,15:30 same session, then 10:00,11:00,12:00,13:00 next session. Early closes use the same trading-minute algorithm.

Opening entry is the genuine **09:30 minute open**; other entries and all exits use the genuine close of the minute starting one minute before the endpoint. Issuance is t+2 minutes and label maturity endpoint+2 minutes. Returns start before assumed issuance and are price-only outcomes, not realizable fill returns.

At full-hour origin t, `entry_index` maps to its completed-hour grid row; at opening, it is the previous completed full hour (normally prior session 15:30; early close 12:30). `first_step=entry_index−47`; gather exactly those 48 scheduled chronological full hours. No opening price or unfinished 09:30–10:30 bar enters FT16. M2 uses the forecast context throughout the sequence, with history locked separately at each historical input session's open.

Source admission: every stock has all 48 finite cap5 closes, sufficient daily warmup (`day_index>=125`), ≥360 cumulative genuine hourly closes and no active COP dependency crossing. Other feature deficiencies use their allowed fallback. Final origin `eligible` combines that input mask with complete20 endpoint eligibility and session date ≥2011-04-01. Supervised label validity does not determine the feature-fit input-key population.

Sources: `hf20_s4_clock.py:10–83`, `hf20_s4_preflight.py:57–67,154–212,219–268`, `hf20_s4_witnesses.assemble():35–56`, `hf20_s4_run.source_data():30–45`.

### Nominal chronological roles

All inner/refit starts are 2011-04-01. Validation is the last six **calendar** months before the OOS year; no random sample split. These date windows are followed by the source/maturity/embargo filters.

| Fold | Inner inclusive stop | Nominal validation | Refit inclusive stop | Nominal OOS |
| --- | --- | --- | --- | --- |
| F21 | 2020-06-30 | 2020-07-01–2020-12-31 | 2020-12-31 | 2021-01-01–2021-12-31 |
| F22 | 2021-06-30 | 2021-07-01–2021-12-31 | 2021-12-31 | 2022-01-01–2022-12-31 |
| F23 | 2022-06-30 | 2022-07-01–2022-12-30 | 2022-12-30 | 2023-01-01–2023-12-31 |
| F24 | 2023-06-30 | 2023-07-01–2023-12-29 | 2023-12-29 | 2024-01-01–2024-12-31 |

For validation, require the **first of its 48 input steps** to have session date strictly after the inner cutoff; for OOS strictly after the refit cutoff. This is a 48-scheduled-step input embargo, not a fixed elapsed-hour or calendar-day gap. All roles also require `label_maturity_utc < local_midnight(cutoff)+1 day−4 hours`. Cutoff is inner stop for inner training, refit stop for validation/refit, and December 31 of OOS year for OOS. Preserve the conservative four-hour cutoff even when the actual endpoint matures earlier. For F23 refit, for example, cutoff uses December 30, not the weekend December 31. Validation must have ≥50 sessions and ≥25 origins in each of seven contexts.

Exact mask implementation: `src/lstm_data/hf20_s4_data.py:32–76`. Exact samples are `S4/Fxx_{inner_train,inner_validation,refit,oos}_indices.csv`; do not recreate membership from the date table alone. S9 inherits these populations unchanged.

### Actual saved support and admitted date bounds

Bounds below are first/last admitted **origin ET session dates**, not label-exit dates. Counts are saved in `S9/S5_S9_ROLE_COUNTS.csv`, `S4/opening_reaudit_v2/S4_FOLD_ROLE_SLOT_COUNTS.csv`, and each `MAGxx/role_metrics.json`; bounds were read from the saved role indices.

| Fold | Role | Admitted date bounds | Sessions | Origins | Stock rows |
| --- | --- | --- | ---: | ---: | ---: |
| F21 | inner_train | 2011-04-01–2020-06-30 | 2,100 | 11,449 | 228,980 |
| F21 | inner_validation | 2020-07-13–2020-12-30 | 120 | 674 | 13,480 |
| F21 | refit | 2011-04-01–2020-12-30 | 2,227 | 12,171 | 243,420 |
| F21 | oos | 2021-01-13–2021-12-31 | 188 | 955 | 19,100 |
| F22 | inner_train | 2011-04-01–2021-06-29 | 2,331 | 12,716 | 254,320 |
| F22 | inner_validation | 2021-07-22–2021-12-31 | 92 | 457 | 9,140 |
| F22 | refit | 2011-04-01–2021-12-31 | 2,423 | 13,173 | 263,460 |
| F22 | oos | 2022-01-12–2022-12-30 | 210 | 1,180 | 23,600 |
| F23 | inner_train | 2011-04-01–2022-06-30 | 2,547 | 13,896 | 277,920 |
| F23 | inner_validation | 2022-07-13–2022-12-30 | 86 | 453 | 9,060 |
| F23 | refit | 2011-04-01–2022-12-30 | 2,640 | 14,395 | 287,900 |
| F23 | oos | 2023-01-13–2023-12-29 | 187 | 887 | 17,740 |
| F24 | inner_train | 2011-04-01–2023-06-30 | 2,740 | 14,945 | 298,900 |
| F24 | inner_validation | 2023-07-14–2023-12-29 | 87 | 350 | 7,000 |
| F24 | refit | 2011-04-01–2023-12-29 | 2,835 | 15,332 | 306,640 |
| F24 | oos | 2024-01-11–2024-12-31 | 208 | 991 | 19,820 |

Refit can admit boundary observations omitted from embargoed validation; it is not necessarily the union of inner_train and inner_validation.

### Weighting

For a role with D admitted sessions, n_d admitted origins on session d, and all 20 names, stock-row mass is **`1/(D*n_d*20)`**. Each session has equal total weight, origins equal within session, stocks equal within origin. The same formula fits magnitude scales and GLOBAL/STOCK controls; it is not uniform weighting of every row across the history. `hf20_ranking.origin_weights():39–41`; `hf20_s5s9_metrics.weights():15–16`. Annual report summaries average years equally rather than pooling unequal annual sample sizes.

## 5. Magnitude target, inversion and three controls

For exact genuine endpoints, let `R=log(P_exit/P_entry)` and `A=abs(R)` in decimal log-return units. In each fold/phase fit

\[
s_A=\max\{Q^{w}_{0.5}(A),10^{-8}\},\qquad m=\log(1+A/s_A).
\]

The pooled weighted median uses the stock-row weights above; sort stably and select the first observed value whose normalized cumulative weight is ≥0.5 (`searchsorted(...,side="left")`), without interpolation. Inner parameters use **inner_train** only; refit parameters use **refit** only. Saved tail/NUM/MAD thresholds are diagnostic cohort definitions, not additional target clipping or loss weights.

A scalar unconstrained head predicts `m_hat`; optimized row loss is `(m_hat−log1p(abs(R)/s_A))²`. R is not cross-sectionally demeaned or divided by MAD for MAG. TG20, epsilon and asinh Z are retained as companion diagnostics but **do not enter the MAG loss**. The FT16 feature named T2 is unrelated to the T2R target transform.

For reporting/inference, retain raw `prediction_m=m_hat` and decode once:

\[
\widehat A=s_A\operatorname{expm1}(\max(\widehat m,0)).
\]

Only the inverse lower-clamps predicted m at zero. There is no upper cap, target winsorization, output ReLU in the model, smearing/Jensen correction, sign reconstruction or portfolio mapping. This estimates transformed magnitude; its inversion is not an unbiased conditional expected absolute return. Sources: `hf20_s5s9.py:60–67,141–175`, `hf1m_ft16_fit.quantile():12–20`, `hf20_s5s9_metrics.decode():29–36`.

### Exact phase parameters

These are the full saved decimal values from `MAGxx/{inner,refit}_target_recipe.json` and `{inner,refit}_GLOBAL_control.json`.

| Fold | Inner magnitude scale | Refit magnitude scale | Inner GLOBAL m | Refit GLOBAL m |
| --- | ---: | ---: | ---: | ---: |
| F21 | 0.005797117684325846 | 0.0058994931438253 | 0.7807054887617804 | 0.7804020257437488 |
| F22 | 0.0059347355198145265 | 0.005957669984582455 | 0.7800440769243104 | 0.7795002079091725 |
| F23 | 0.0060897938914411046 | 0.006150424755601047 | 0.780037173411231 | 0.779600015468851 |
| F24 | 0.006174065175292481 | 0.0061703009229596 | 0.7786992711980216 | 0.7780814265022555 |

### Control definitions

**GLOBAL:** fitted weighted mean of m over all training stocks/origins/sessions, broadcast to every evaluation row. **STOCK:** one fitted weighted mean m per stock, averaging origins with session-normalized weights. Both are means in **transformed space**, not mean raw A transformed afterward. Each phase's training coefficients remain fixed for its evaluation roles; all controls use exactly the neural run's eligible keys and phase scale.

**VOL:** parameter-free, `inner_VOL_control.json` and `refit_VOL_control.json` are `{}`. At the last input step decode the actual scaled/imputed float32 V2 channel through its frozen affine recipe:

\[
\sigma=\exp(V2_{scaled}\,s_{V2}+c_{V2}),\qquad
\widehat m_{VOL}=\log(1+2\sqrt{2/\pi}\,\sigma/s_A).
\]

Thus decoded raw magnitude is `2*sqrt(2/pi)*sigma`. Sigma is the **floored RMS60 of hourly open-to-close returns, or its native feature fallback**, as represented in the consumed tensor; do not recompute a new close-to-close or overnight volatility. The multiplier is fixed, with no fitted regression, cross-sectional rho, quantile bins or optimization for MAG. EVENT/QUANTILE control rules in the shared module do not apply.

Authority: `hf20_s5s9.Data.volatility():133–138`; `hf20_s5s9_metrics.fit_control():223–242`, `control_raw():268–273`; `hf20_s5s9_report.finish_run():264–305` explicitly bypasses fitting MAG/VOL.

### Exact STOCK coefficients (predicted m)

Column I is inner, R is refit; row order is the fixed stock axis. Values are transcribed at saved JSON precision from `MAGxx/{inner,refit}_STOCK_control.json`, key `value`.

| Ticker | F21 I | F21 R | F22 I | F22 R | F23 I | F23 R | F24 I | F24 R |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| VZ | 0.6279239829544796 | 0.6167956218897865 | 0.6111868859978398 | 0.6063645879065321 | 0.6024794237421662 | 0.6046993122653715 | 0.6059534101854324 | 0.6095732038337187 |
| COP | 0.8649228246455933 | 0.8724123331712701 | 0.8774437958724485 | 0.8790176260826301 | 0.8821195316836852 | 0.8833155990178297 | 0.8819279444737617 | 0.8794144093456454 |
| BAC | 0.8509585259857807 | 0.8470046027304942 | 0.844737468828631 | 0.8432745197123446 | 0.8394720347706234 | 0.8360168331262082 | 0.8338673165986042 | 0.832847367223927 |
| BA | 0.7966578398437266 | 0.8086393844849904 | 0.8153904119609365 | 0.8178858106957089 | 0.8281163642465779 | 0.8301363982847985 | 0.8300477165844106 | 0.8272891594421045 |
| AAPL | 0.762259958350848 | 0.7668212840001577 | 0.7659805582226921 | 0.7645625328609627 | 0.7646081352111939 | 0.7659347484636029 | 0.7640595384640354 | 0.7620176374449703 |
| PEP | 0.565912532805736 | 0.5648754603141318 | 0.5659250521473685 | 0.5653923959861803 | 0.5640893187456197 | 0.5625970823939321 | 0.5612584301086677 | 0.561035513490638 |
| MRK | 0.6741091901021926 | 0.6701630347400371 | 0.667412713954337 | 0.668873895831577 | 0.6644209539481736 | 0.6623056013718924 | 0.6615410830249369 | 0.6615497094326539 |
| SBUX | 0.7314813757620817 | 0.7287625934246942 | 0.7284180320590486 | 0.7261141528792093 | 0.7291581860787641 | 0.7293217552223225 | 0.7261484641294293 | 0.723533801072121 |
| CVX | 0.7326044265457307 | 0.7396449233417284 | 0.7416967422315551 | 0.7410215533593928 | 0.7437594466866562 | 0.7443197027187195 | 0.7434080032876285 | 0.7421434290692308 |
| MS | 0.8976736246286194 | 0.8898513329895162 | 0.8866560083235383 | 0.8849190527579411 | 0.8813116625956565 | 0.8766079526679454 | 0.8714132807655216 | 0.868096573895736 |
| AMD | 1.1911804336055587 | 1.1772892041545568 | 1.1670303861878246 | 1.1672819676126576 | 1.1637840329612998 | 1.160878067363297 | 1.1589997956606992 | 1.1594172176638717 |
| KO | 0.570023040151916 | 0.5727389014919869 | 0.5716668398804869 | 0.5706262058399103 | 0.5702301894840448 | 0.5705492777806171 | 0.5674047345594221 | 0.5660014792851307 |
| JNJ | 0.5805823030395609 | 0.5791104007215112 | 0.5772595748116877 | 0.5749511118049682 | 0.572624189050347 | 0.5694789506076492 | 0.5669630970276622 | 0.5679642971461746 |
| AMZN | 0.831234442505602 | 0.8308253448121442 | 0.8273375170467794 | 0.8240723685425374 | 0.8280194274407634 | 0.8332842721975509 | 0.8365133962841659 | 0.8395944352310111 |
| XOM | 0.6831851437157815 | 0.6950894615572155 | 0.7031660567018804 | 0.7075932994665731 | 0.7147017937655964 | 0.717080032403105 | 0.720006334757303 | 0.7216554265287107 |
| WFC | 0.7386934820054066 | 0.7473715869489501 | 0.7523987584500912 | 0.7565053289432724 | 0.7612790087609722 | 0.7606807716835553 | 0.7632459085306618 | 0.7640994163630038 |
| AVGO | 0.920097330904426 | 0.9070145791019004 | 0.9044769678994897 | 0.8978844391551416 | 0.8934294269451727 | 0.8890947107655133 | 0.8867874504318067 | 0.888056011922942 |
| TSLA | 1.1358787529448477 | 1.1412772017239643 | 1.1417226649210317 | 1.1399749670634702 | 1.1409808347983368 | 1.1421804962722573 | 1.1459934731875774 | 1.1466114252491153 |
| MA | 0.7335556318096461 | 0.734229336479566 | 0.7366476156145039 | 0.7407029121166331 | 0.7449162758797422 | 0.7437195827768808 | 0.741231959503208 | 0.7363643441421157 |
| CSCO | 0.7251749329280699 | 0.7181239267963748 | 0.7143274873740106 | 0.7129854295657729 | 0.7112432314292202 | 0.7097991619939825 | 0.707214086395472 | 0.7043636722622822 |

## 6. Model, optimization, selection and refit

### Executed hyperparameters and initialization

| Item | Executed setting |
| --- | --- |
| Architecture | Shared unidirectional `nn.LSTM(input_size=16,hidden_size=32,num_layers=1,batch_first=True)`, default biases, no projection; scalar `nn.Linear(32,1)` head |
| Sequence | 48×16 per stock; no stock embedding, peer/market input, persistent hidden/cell state, padding or truncated-state carry |
| Readout/dropout | Last hidden state, `nn.Dropout(0.10)`, then affine head; this is readout dropout, not inter-layer recurrent dropout |
| Parameter count | 6,433: 6,144 LSTM matrix +32 head matrix elements; 256 LSTM bias +1 head bias elements |
| Seed | Exactly 42; Python `random`, NumPy legacy RNG and `torch.manual_seed`; `torch.use_deterministic_algorithms(True)` |
| Initialization | PyTorch 2.10.0 defaults; no custom Xavier/orthogonal/forget-bias override. LSTM parameters uniform ±1/√32; Linear uses `kaiming_uniform_(a=√5)` and uniform bias ±1/√32. Preserve constructor order: LSTM, dropout, head |
| Initial parameter identity | `1e6f1b81ccd0286b5da1eb7c47ffff1702ae8b677f34c2058f7538417bc928bc` for all four runs |
| Device/numerics | CPU float32 model and training inputs/targets; no AMP, GPU/MPS or mixed precision; 4 intra-op threads, 1 inter-op thread |
| Optimizer | AdamW, fixed lr 0.001, betas (0.9,0.999), eps 1e−8, AMSGrad false; no scheduler/warmup |
| Weight decay | 0.01 for all 2-D matrices (including head); 0 for 1-D biases |
| Gradient rule | One global L2 `clip_grad_norm_(...,1.0,error_if_nonfinite=True)` per optimizer step; nonfinite loss/gradient/weights fail closed |
| Batches | 16 complete admitted sessions; all their eligible origins and all 20 stocks; keep final shorter session batch; no accumulation or replacement sampling |
| Epoch policy | Minimum 12 calibration epochs before stopping, maximum 60, patience 10; exact qualifying loss rule below |

Sources: `src/lstm_data/neural_engine.py:18–57,159–171`; `hf20_s5s9.model_for():40–51`; `hf20_s5s9_run.py:224–320,348–378,512–513`; each run's saved configuration. Default initialization was also inspected in the installed `torch==2.10.0` package's `torch/nn/modules/rnn.py:RNNBase.reset_parameters` and `torch/nn/modules/linear.py:Linear.reset_parameters`.

All four refit checkpoint contents have float32 tensors: `lstm.weight_ih_l0[128,16]`, `weight_hh_l0[128,32]`, `bias_ih_l0[128]`, `bias_hh_l0[128]`, `head.weight[1,32]`, `head.bias[1]`. Saved AdamW groups additionally record `maximize=False`, `foreach=None`, `capturable=False`, `differentiable=False`, `fused=None`, `decoupled_weight_decay=True`. Preserve defaults/CPU backend rather than enabling fused/foreach execution independently.

### Exact epoch order and objective reductions

Group the selected role positions by ET session date, sort dates, then for epoch n shuffle with a **fresh `np.random.default_rng(42+n)`**. Group indices retain original chronological origin order; flatten origin-major then stock-major into `[origins*20,48,16]`. Every batch calls `model.train()`, clears gradients, computes per-stock transformed squared error, averages the 20 stocks, and weights each origin by `1/(number_of_sessions_in_this_batch * origins_on_its_day)`. Sum to one scalar and take one optimizer step. There is no extra full-history scaling of the final short batch's gradient. Phase-specific day lists make refit batches different, but the same epoch-number shuffle seeds are reused. There are no DataLoader workers; the runner directly constructs batches.

After every calibration epoch, `predict()` evaluates the **entire** inner-training and validation roles with dropout off, `torch.inference_mode()`, batches of 32 origins, and unchanged chronological sample order. Selection's `off()` loss recomputes targets from R cast to float32 and reduces stock mean, then full-role session-normalized origin weights. Online training loss is reported separately; it is not the selection statistic.

Saved score exports later recompute row loss in float64 from saved float32 predictions and original float64 R, then aggregate with row weights. Therefore last-digit differences between validation traces and saved diagnostic metrics are expected; do not use exported float64 losses to reconstruct the stopping rule. Sources: `hf20_s5s9_run.predict/off/epoch():189–320`; `hf20_s5s9_metrics.make_frame():173–220`.

### Selector and actual completed epochs

`objective_screen_run.Selector:40–65` is the imported MAG selector. First finite nonnegative loss qualifies. Later validation L qualifies only when **`L <= 0.999*best_qualified_loss`**; equality qualifies. A qualifying epoch replaces selected epoch/best and resets patience, otherwise patience increments. Independently track the raw numerical minimum. Stop when epoch≥12 and patience≥10, else at epoch 60. The selected epoch can be less than 12 and need not equal the raw minimum. There is no rank-IC selection for MAG.

| Fold | Calibration stop | Selected / refit epochs | Raw-best epoch | Calibration optimizer updates | Refit updates | Saved qualified best validation loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| F21 | 37 | 27 | 30 | 4,884 | 3,780 | 0.27765695714096117 |
| F22 | 30 | 20 | 20 | 4,380 | 3,040 | 0.222935593875287 |
| F23 | 51 | 41 | 41 | 8,160 | 6,765 | 0.25486852119791253 |
| F24 | 37 | 27 | 27 | 6,364 | 4,806 | 0.20448313889638625 |

All stop statuses are `PATIENCE_STOP`. F21 raw-best loss was 0.2775669336205141 at epoch 30, insufficient to replace qualified epoch 27. Counts and losses above are recorded in `MAGxx/calibration_binding.json` and `refit_binding.json`; refit optimizer step counters were inspected in the four saved checkpoints.

### Refit, checkpoint and inference rules

Each epoch saves `calibration_NNN.pt` containing model `state_dict` only. At calibration stop, `calibration_stop_optimizer.pt` contains the **stop-epoch** optimizer, not selected-epoch optimizer state. Reload selected calibration weights for both inner_train and inner_validation exports.

Then apply the refit FT16 recipe and refit magnitude scale; recreate the seed-42 model at the identical initial parameter hash and a fresh empty AdamW optimizer. Train the **whole admitted refit role** for exactly the selected number of epochs, with no further validation selection or OOS inspection. This is not fine-tuning the selected calibration weights. `refit_final.pt` contains `{model: state_dict, optimizer: optimizer_state_dict}`. Recreate a model, load saved model weights, and export refit/OOS from that final model; historical runner asserts exact prediction equality with checkpoint reload.

For inference use the matching fold's **refit** input recipe, magnitude scale, checkpoint and exact endpoint/source conventions. Set `eval()` and use the scalar head output without target inversion inside the LSTM. Apply the decode formula once afterward. Raw R, TG20 or future endpoint availability are not model input fields. Omitted LSTM h0/c0 are new zeros on every call.

Sources: `hf20_s5s9_run.neural():323–486`, `predict():189–202`, `neural_engine.SharedLSTM.encode():40–54`. The checkpoint serialization does not include full Python/NumPy/Torch RNG states; a bitwise resumed training procedure is not supplied by these files.

### Saved checkpoint paths and recorded SHA256

Each filename below is under its corresponding `MAGxx/`; hashes are **recorded binding values**, not a fresh hash audit in this task.

| Fold | Selected calibration file | Recorded calibration SHA256 | Recorded `refit_final.pt` SHA256 |
| --- | --- | --- | --- |
| F21 | `calibration_027.pt` | `9b09865ab9e495f29b1cff69b7c4dc11d16949c873fafe88ead79453c66791b0` | `0cd6d35ef59be7ca184680de0489fdcf2d2b24871219594c18f49c1a213971e7` |
| F22 | `calibration_020.pt` | `c4c49eb12b396ad172ece5ac0c0e495380186e72c0b4166ff701a89ee193ccd8` | `2ce9c2f9c9036b9df3885ed2667c6b30bee68fac8e227fdcdc2be3ca274a7412` |
| F23 | `calibration_041.pt` | `5f06f005b7b48e55d6fa8ba307435c83f8cb041b8a32a1d300137323e884457a` | `97be88d97a7a350813f03dadc2fcb95ecefcd0aaee945e30f985a7cd81632b8b` |
| F24 | `calibration_027.pt` | `cc86cf4a7d41408e0e5e46ed8a358d7b1d9e939c7ad0c37332d8ef6c13536c1f` | `3e985c2c2ab3042a5914513c6be34cbc9c2ddc4aaf54ba69fdccd84f8f26c1e8` |

## 7. Reproduction entry points, artifacts and numerical qualifications

### Required inputs and saved outputs

To reproduce existing scores using checkpoints, retain these exact artifacts and their recorded identities:

| Required layer | Paths / role |
| --- | --- |
| Source provenance | `A18/complete_acquisition_manifest.json`, `source_revision_manifest.json`, `months/YYYY-MM/*receipt.json`; raw selected minute path `data/raw/hf20_hf1m_long_v1/REV/raw_1m_selected/YYYY-MM.parquet` (REV as above) |
| Authoritative canonical minute QA | `data/processed/hf20_hf1m_long_v1/REV/qa_v2/canonical_observed/YYYY-MM.parquet`; original cap5 proxies/quality are separate `qa_v2/` stores. `qa_v2`, not earlier QA attempts, governs |
| P019B adjustment/exclusion layer | `P019B/adjusted_hourly_manifest.json`, event ledger/pointer, `pre_feature_gate.json`, field-mask manifest; adjusted hours under `data/processed/hf20_hf1m_long_v1_action_qa_v1/ta019b_action_qa_2026-10-22_201224/hourly/` |
| P020 lineage | `configs/hf1m_long_ft16_v1.json`, `P020/model_input_contract.json`, original `train_only_fit_recipes.json`; lineage only where superseded by S4 phase recipes |
| Actual S4 source/targets | `S4/S4_FROZEN_EXPERIMENT_CARD.json`; `S4/opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv`, `S4_ORIGIN_SOURCE_ELIGIBILITY.parquet`, `S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet` (all three in that subdirectory). Card-selected source is **opening_reaudit_v2** |
| Actual input fits/populations | Eight `S4/Fxx_{inner,refit}_recipe.json`; sixteen `S4/Fxx_role_indices.csv`; `S9/S4_REUSED_RECIPES.json` |
| MAG target/control/model | Per-run `configuration.json`, two target recipes, six control JSON files, two bindings, selected calibration checkpoint, `refit_final.pt` |
| Existing comparison outputs | Per-run `role_scores.parquet`, `role_metrics.json`, `role_KIND_control_scores.parquet`, `model_and_control_metrics.csv`, `RUN_DIAGNOSTICS.md`; root `S5_S9_ROLE_COUNTS.csv`, `S5_S9_VERIFICATION.json`, `artifact_inventory.csv` |

Actual `Data()` calls `hf20_s4_run.source_data(S4)`, loads the saved source/endpoint stores, rebuilds source components in memory and expands M2; it is not a standalone checkpoint-only inference CLI. This reconstruction was **not invoked here**. Source code: `hf20_s4_run.py:30–45`, `hf20_s4_preflight.py:70–140`, `hf20_s5s9.py:82–115`. The legacy P020 contract is also an inherited metadata dependency (`hf20_s4_data.py:23–30`; `hf20_ranking_data.metadata():52–72`). Private Parquets/checkpoints are intentionally ignored by Git; cloning alone does not supply them.

### Actual commands and executable boundaries

Historical commands are documented for reproducibility, **not executed by this extraction**:

```bash
# Activated source acquisition/QA; A18 contains its state/identity prerequisites.
.venv/bin/python -B -m lstm_data.hf_minute_long --run --out reports/data_audit/ta018d_hf1m_long_2026-10-22_155547
# Adjusted source and original P020 feature preparation.
.venv/bin/python -B -m lstm_data.hf1m_action_source --out reports/data_audit/ta019b_action_qa_2026-10-22_201224
.venv/bin/python -B -m lstm_data.hf1m_ft16_prepare --out reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122
# Executed S5/S9 untrained preparation and complete live campaign.
.venv/bin/python -m lstm_data.hf20_s5s9_prepare --out reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation/preflight_v2
.venv/bin/python -u -m lstm_data.hf20_s5s9_run --out reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation
```

These are staged entry points, not a complete from-empty-directory recipe. P019B release/masks, original source QA state, S4's approved opening reaudit/fits and evidence bindings must already exist. Their historical creation commands and prerequisites are recorded in `reports/codex_sessions/2026-10-22_184817_ta018d_hf1m_long.md`, `2026-10-22_204909_ta019b_action_qa_release.md`, `2026-10-22_214605_ta020_hf1m_long_ft16_tg20.md`, `2026-10-26_125645_hf20_s1s2_visual_s4a_opening_preflight.md` and `2026-10-26_155600_hf20_s4a_live_final.md`.

The actual neural runner has only `--out`; **no MAG-only `--arm`, `--seed`, `--resume` or fold-selection argument exists**. It executes S5 F21–F24, then MAG F21–F24, then EVENT and QUANTILE. It requires frozen live authority/preflight/code/input bindings and rejects an existing journal or `EXECUTION_STARTED.json` (`hf20_s5s9_run.py:504–527`). Therefore the completed namespace is not restartable and its prior authority is exhausted. **NOT VERIFIED:** a turnkey independent training/inference CLI that bypasses this campaign lifecycle while preserving every rule; none was implemented for this documentation task.

Saved-output report entry points, distinct from training, are `scripts/summarize_s5_s9_saved_outputs.py --out S9` and `scripts/render_s5_s9_complete_views.py --out S9 --reuse-screenshots` (replace alias S9 with its full path). They write reports; they were not run under this read-only request.

### Environment and bitwise identity

Authoritative setup route: repository `.venv`, `python -m pip install -e '.[dev,neural]'` (README); include `visualization` extra for Plotly reports. `pyproject.toml` requires Python ≥3.11,<3.15; NumPy ≥2.2,<3; pandas ≥2.3,<3.1; PyArrow ≥21,<24; exchange-calendars ≥4.11,<5; requests ≥2.32.5,<3; python-dotenv ≥1.1,<2; neural extra pins **torch==2.10.0**. Report extra pins Plotly 6.3.1 and Streamlit 1.64.0; Streamlit is not the MAG training engine.

Recorded acquisition environment (`A18/runtime_environment.json`): macOS 27.0.1 arm64, Python 3.14.6 / Clang 21, NumPy 2.5.3, pandas 3.0.6, PyArrow 23.0.1, exchange-calendars 4.13.2, requests 2.34.2. The earlier completed S3 session records the same Python/NumPy/pandas/PyArrow plus torch 2.10.0; S9's handoff reports no environment changes. **NOT VERIFIED:** a full package/build/BLAS/backend freeze captured specifically at the S9 live start. Current broad dependency ranges alone cannot guarantee byte-identical recomputation.

Deterministic seeds and CPU execution improve reproducibility but do not certify cross-machine bitwise identity. Differences can arise from CPU/OS/PyTorch kernels or threading, default AdamW dispatch, compiler/math-library builds, NumPy quantile/transcendental and float32 rounding, calendar/tzdata versions, and reordered origin/stock keys. Preserve FP32 training versus FP64 export reductions, batch/inference chunk sizes, constructor/RNG call order and saved source/recipes. Changing batch size changes stochastic training even with seed 42. Serialized file bytes may differ while tensor values agree. No RNG state was checkpointed for arbitrary continuation.

**NOT VERIFIED:** fresh cross-machine reconstruction/checkpoint forward equality, full source hash revalidation or independent lawful access to the private artifacts. This task inspected saved metadata/checkpoint structures only. Existing `refit_binding.json` records `reload_max_error:0` for every fold, and the completed runner required exact reload predictions; those historical checks were not repeated here.

## 8. Saved-results reconciliation reference

The following are existing **OOS transformed magnitude MSE** values, copied from each `MAGxx/model_and_control_metrics.csv` and neural `oos_metrics.json`; no metrics were recomputed. They provide a compact expected-output reference for the four identified refit models.

| Fold | NEURAL | GLOBAL | STOCK | VOL |
| --- | ---: | ---: | ---: | ---: |
| F21 | 0.22277650031658225 | 0.28464272048962214 | 0.261443862246743 | 0.2599329619784624 |
| F22 | 0.27920023665744426 | 0.38055613654435844 | 0.3487977528967771 | 0.3187140675233866 |
| F23 | 0.20885746933969868 | 0.2549552875755001 | 0.22695279066099444 | 0.24494115063661848 |
| F24 | 0.21898243045736782 | 0.2680606168260498 | 0.24033893466207923 | 0.2494764069720326 |

The saved handoff reports equal-year MAG MSE ≈0.232454 and qualifies the result as magnitude information with raw-magnitude underprediction. These are retrospective exploratory results, not confirmation, signed alpha or transaction-cost-adjusted performance. Source publication/action-vintage and survivor-cohort limitations remain part of exact replication, not details to silently repair.
