# HF20 S2-C C-A: clean-room replication specification

Phase 1 extraction, 2026-11-02. **INCOMPLETE_SPEC for exact execution provenance; behavioral reconstruction below is specified, but the unresolved items in §18 require review before Phase 2.** No execution is authorized by this document. It contains no original forecast scores, selected epochs, fitted calibration coefficients, or network weights. It is the only Phase 1 document eligible for release to a clean-room implementer, together with the original selected raw downloads identified below, after human review.

Evidence labels: **EXECUTED/VERIFIED (E/V)** means a historical run receipt, bound source, or archived output supports the claim; it does not mean Phase 1 reran that check. **CODE-INFERRED (CI)** means inspected implementation without a complete immutable execution binding. **DOCUMENTED-ONLY (D)** means documentary assertion. **UNRESOLVED/CONTRADICTORY (U)** means missing/conflicting proof. Citations identify audit evidence only: **never open those project sources in Phase 2**. All behavioral definitions needed from them are expanded here. Labels apply to the associated section unless qualified more narrowly.

## 1. Identity, scope, and information boundary

**E/V.** The experiment is the C-A amendment of S2-C: shared own-stock hourly LSTM, schedule inputs, three *signed*, training-only component heads, complete-triple stock-cell masking, original 240 scheduled-trading-minute **absolute endpoint log return** main target, and its own C3 intraday/overnight residual-smearing calibration. Four yearly Design A folds are F21–F24. The completed namespace is `reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28/`; `verification.json` records COMPLETE, four pairs/eight phases, no retries. This is not the earlier blocked all-20-auxiliary S2-C proposal. C-A preserves every primary eligible 20-stock origin and masks only the auxiliary loss.

This is not S2-D's close-to-next-open gap-magnitude task, S5-C's hybrid pairwise objective, or CLOCK-C3 without auxiliary supervision. No USA500, market index, peer channel, stock identifier embedding, sector channel, minute encoder, pairwise loss, event classifier, separate gap inference output, trading portfolio, or learned allocator enters S2-C. Shared preprocessing across stocks and stock-specific floor estimates are nevertheless forms of pooled/stock-conditioned information.

**\* ISSUANCE-TARGET MISMATCH — preserve in first replication.** Targets start at nominal origin `t`, but completed-hour data ending at `t` are assumed available only at `t+2 minutes`. At 09:30 even the minute-open reference comes from the 09:30–09:31 bar, assumed usable at 09:32. Thus historical forecasts may cover an interval already partly realized when issued. **The mismatch is confirmed by definitions; actual vendor arrival, economic exploitability, and severity are unverified.** The two-minute lag is a proxy, not a measured receipt. Do not move origin prices, omit the last hour, move the endpoint, or repair this in replication. Matching old results does not establish causal live tradability.

All market observations in scope end by 2024-12-31. Calendar-only lookup can extend through 2025-01-10. Do not open any 2025 market or protected 2026 numerical partitions, values, paths inventories, or hashes. Reports created in 2026 about pre-2025 experiments are distinct from protected 2026 market data.

Audit citations: `src/lstm_data/hf20_s2c_ca.py:98–310,453–673` (protocol, preflight, phases, run); `.../S2C_CA_PROTOCOL.json`, `verification.json`; `src/lstm_data/hf20_s4_clock.py:39–70`; `reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation/opening_reaudit_v2/S4_SOURCE_POLICY.json` (opening/issuance policy).

## 2. Original downloaded inputs and immutable identity

**E/V for local schema/existence; D/U for upstream origin/rights.** Hugging Face dataset identifier `mito0o852/OHLCV-1m`; pinned revision `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`. Provider-side objects are named `data/ohlcv_YYYY-MM.parquet`. The retained original downloads are *exact-symbol selected extracts*, not full provider-wide files. They preserve original values and order, including extended hours, duplicates and invalid records; they have acquisition provenance columns, but have not undergone minute QA, adjustment or feature processing.

Clean-room raw entry point, resolved relative to a supplied data root:

`data/raw/hf20_hf1m_long_v1/776328445b7ac6e7815ef3a483e9c8ded1eb6d56/raw_1m_selected/YYYY-MM.parquet`

Enumerate exactly July 2010 through December 2024, inclusive: 174 files. Do not glob the surrounding directory. Phase 1 checked these exact files' Parquet footers; all exist. They contain 33,297,202 selected source rows, including non-RTH and rows later rejected. Yearly raw row counts:

| Year | Rows | Year | Rows | Year | Rows |
|---|---:|---|---:|---|---:|
|2010 Jul–Dec|1,117,302|2015|2,170,493|2020|2,587,633|
|2011|2,256,293|2016|2,158,180|2021|2,464,571|
|2012|2,171,063|2017|2,172,878|2022|2,469,294|
|2013|2,165,117|2018|2,257,264|2023|2,423,722|
|2014|2,177,536|2019|2,251,319|2024|2,454,537|

Schema in order: `timestamp: timestamp[ns, tz=UTC]`; `open,high,low,close,volume: float64`; `ticker: string`; `source_dataset,source_revision,source_file: string`; `source_row_group: int64`; `is_genuine: bool`; `source_row: int64`. Original seven market columns precede appended acquisition metadata. `source_row` is original global row ordinal within the provider monthly file; `source_row_group` is its zero-based Parquet group. Acquisition selected exact strings in the fixed universe, with no alias stitching. `is_genuine` here means copied source record, not independently authenticated trade, valid candle, auction price, or verified arrival.

Tensor stock axis, **literal order**, index 0 through 19:

`VZ, COP, BAC, BA, AAPL, PEP, MRK, SBUX, CVX, MS, AMD, KO, JNJ, AMZN, XOM, WFC, AVGO, TSLA, MA, CSCO`.

The historical study uses this fixed surviving-symbol universe. It is not a point-in-time membership reconstruction. No delisted-name replenishment, suspension interpolation, alias substitution, or OOS-performance-based universe change is part of the procedure. Original economic identity/AVGO successor lineage and the rationale for choosing precisely these 20 are not independently established by the downloaded rows. The acquisition authorization was reported as private research permission; public availability is not independently verified redistribution/licensing permission. Historical vendor/source upstream of the HF uploader and revisions/arrival timestamps are not certified. No external lookup was performed in Phase 1.

The prohibited derived starting points include `canonical_observed`, filled proxies, adjusted hourly stores, FT16 arrays, S4 labels, role indices, recipes, checkpoints and scores. The pipeline below must rederive them. An old derived artifact hash is never an algorithm.

Audit citations: `src/lstm_data/hf_minute_boundary.py:74–88` (`validate_schema`); `hf_minute_long_io.py:238–260` (`selected_table`); `hf1m_action_audit.py:24–100` (identity/order); `docs/track_a/HF1M_LONG_SOURCE_018D.md`, “Layers and interpretation”/rights; exact raw footers inspected in Phase 1. Upstream acquisition receipt identifier historically recorded: `complete_acquisition_manifest.json`, SHA-256 `2b8f9165b0387acaf650d1f1514afb8b41d081aacc9b2056b2f6efa496adf40c`. That mixed-era manifest is not a clean-room input and was not scanned for protected entries in this extraction.

## 3. Calendar and scheduled-minute geometry

**E/V algorithm; CI exact current calendar dependency; U historical full environment pin.** Use XNYS regular sessions, America/New_York timezone, aware UTC instants for storage/comparison. Generate dates 2010-07-01 through 2025-01-10 for calendar lookup, but no prices after 2024. Normal open 09:30, close 16:00, 390 minutes; early close 13:00, 210 minutes. No lunch break. Weekend/holiday time does not consume horizon minutes. U.S. DST: second Sunday in March changes UTC−5 to UTC−4, first Sunday in November returns to UTC−5. Construct local session dates then convert; never hard-code UTC hours.

The implementation calls `exchange_calendars` XNYS schedule; current local version is 4.13.2, not conclusively pinned at execution. For an independent schedule over this interval, exclude Saturdays/Sundays and these holidays: New Year January 1 (Sunday observed Monday; Saturday has no preceding-Friday observation), MLK third Monday January, Presidents third Monday February, Good Friday (Gregorian Easter minus two days), Memorial last Monday May, Juneteenth June 19 nearest weekday starting 2022, July 4 nearest weekday, Labor first Monday September, Thanksgiving fourth Thursday November, Christmas December 25 nearest weekday. Exceptional closures in range: 2012-10-29, 2012-10-30, 2018-12-05, and calendar-only 2025-01-09. Close at 13:00 on the Friday after Thanksgiving; December 24 Monday–Thursday when a session; July 3 Monday/Tuesday/Thursday; from 2013 also Wednesday July 3; before 2013 Friday July 5 when a session. Holiday closure takes precedence. These rules are transcribed from the installed calendar's actual holiday definitions, not its inaccurate Juneteenth docstring.

For each session `[open, close)`, create each minute-start `open + m minutes`, `m=0,...,duration−1`. Raw timestamp denotes start of a one-minute bar; its close is observed at the end of that minute. Session-close reference is the close of `close−1 minute`, e.g. 15:59 bar close represents 16:00, and 12:59 represents a 13:00 early close. It is not an invented auction price.

Group minute offsets by integer division `m//60`. Hour start is open plus 60 times slot; hour end is minimum(start+60 minutes, close). Keep a separate 30-minute closing stub. Six full hours on normal days, three on early-close days. Only full hours enter FT16/history. Stubs may supply true session-close/target endpoints and consume target minutes.

Candidate origins are open plus integer hours 0,...,6, retaining only times strictly less than close. Clock slots are 09:30,10:30,11:30,12:30,13:30,14:30,15:30; early closes retain 09:30–12:30. Iterate sessions then ascending origins. `origin_id` is UTC timestamp ISO string including timezone; `(origin_id,ticker)` is the unique score key. Feature context indices differ from one-hot indices: 09:30→6, 10:30→0,11:30→1,...,15:30→5. Do not conflate them.

Endpoint algorithm: set cursor=t, remaining=240 minutes. Walk sessions in chronological order; skip intervals whose close≤cursor, move cursor to next open if cursor<open. Available=close−cursor. If remaining≤available, return cursor+remaining (equality may return close). Otherwise subtract available and advance across the closure. Fail if schedule exhausted. This is **240 scheduled minutes**, not elapsed minutes or four retained full-hour rows. `category=INTRADAY` iff endpoint≤current session close, otherwise OVERNIGHT. Exactly one closure is supported by the historical auxiliary geometry; independently verify it rather than equating every overnight interval to a gap-only target. Label maturity is endpoint+2 minutes.

Examples (local ET; each assumes genuine requisite source prices):

| Origin/session | Latest full-hour input | Price reference at origin | Endpoint | Clock remaining/240; crossing |
|---|---|---|---|---|
|Normal 09:30|previous session's last full-hour end (normally15:30)|09:30 minute **open**|13:30 current day|390/240;0|
|Normal 11:30|10:30–11:30|11:29 minute close|15:30 current day|270/240;0|
|Normal 12:30|11:30–12:30|12:29 minute close|10:00 next session|210/240;1|
|Normal Friday15:30|14:30–15:30|15:29 minute close|Monday13:00 if Monday open|30/240;1|
|Early-close09:30|preceding session's last full hour|09:30 minute open|next session10:00|210/240;1|
|Early-close12:30|11:30–12:30|12:29 minute close|next session13:00|30/240;1|

Normal15:30 diagram: `[48 completed full hours ... 14:30→15:30] → nominal t15:30 → assumed issue15:32 → stub15:30→16:00 → closed interval → next09:30→13:00 endpoint → maturity13:02`. Weekend/holiday duration changes elapsed time, not 240-minute arithmetic. Early-close opening can be OVERNIGHT even though the same clock slot is intraday on a full session.

Audit citations: `src/lstm_data/hf20_s4_clock.py:10–85`; `hf_minute_long_qa.py:60–89`; installed `exchange_calendars/exchange_calendar_xnys.py` regular/special closures and `us_holidays.py` holiday definitions.

## 4. Raw reconciliation, action facts, quarantine and hourly aggregation

**CI with historical source-policy/receipt support.** Process monthly raw files chronologically. Preserve their original records. Convert timestamps to aware UTC; reject missing or not minute-aligned timestamps and rows whose Eastern calendar month differs from the file month. Numerical validity requires finite OHLCV, all four prices>0, volume≥0, high≥max(O,H,L,C), low≤min(O,H,L,C). Zero-volume genuine candles remain valid. No clipping, smoothing or magnitude-based rejection of otherwise valid returns.

Deduplicate using equality of all seven original market columns. For each `(ticker,timestamp)`, count distinct seven-column versions **before validity filtering**. If more than one version, exclude every version, even if only one is valid. Identical duplicates collapse once, retaining the first source row. Classification priority is invalid, conflicting duplicate, identical duplicate, unique. Canonical observations are valid, nonconflicting rows sorted ticker then timestamp; calendar membership determines RTH. Exclude all extended/noncalendar rows from prices, feature aggregation, anchors and action-adjusted inputs. Retain an expected minute grid for each stock/session, with separate absent, conflicting and invalid flags; a missing observation is not proof of no trade. Entire missing hours retain NaNs. No across-stock or across-session price carry.

### 4.1 Fixed action metadata embedded here

Backward-adjust all **RTH OHLC only**, for each observation date d, by multiplying with the product of `1/split_ratio` for the ticker's split dates strictly greater than d in this fixed list. On ex-date use new share units. The source's declared basis is “split-consistent through 2026-03-31”; the fixed fact list contains no later split beyond 2024, so no protected data are needed. Volume is **unchanged as reported**. Do not inverse-adjust volume or dividend-adjust prices.

| Ticker | Ex trading date | Split ratio |
|---|---|---:|
|KO|2012-08-13|2|
|MA|2014-01-22|10|
|AAPL|2014-06-09|7|
|SBUX|2015-04-09|2|
|AAPL|2020-08-31|4|
|TSLA|2020-08-31|5|
|AMZN|2022-06-06|20|
|TSLA|2022-08-25|3|
|AVGO|2024-07-15|10|

COP's 2012-05-01 PSX spinoff has **no adjustment multiplier**. Price basis is COP_PRE_SPINOFF before that date and COP_POST_SPINOFF on/after it. Reject target returns crossing that boundary; reset indicators at the boundary and apply the dependency exclusion below. Do not apply the retrospective 77.09% tax allocation or add PSX prices. Other prices share one split-consistent basis. Per-stock volume basis is ticker plus count of listed split events effective on/before date; histories requiring compatible volume units must stay in one such regime.

Preserve the documented real dislocations SBUX 2015-08-24, AMD 2016-04-22, COP 2020-03-09 as economic moves with factor1. Three KO mixed-basis premarket records are outside RTH anyway. Corporate-action facts were researched retrospectively; the original raw data alone do not establish their announcement times or completeness. Historical use of future split factors is not automatically an invariant violation for homogeneous price ratios, but must be tested for indicator initialization, rounding, basis flags and derived eligibility.

### 4.2 Literal historical quarantine list

Exclude **all OHLCV fields** of the following 18 canonical RTH minutes. These are fixed retrospective source decisions, not a new threshold filter. Do not infer a new list from Phase 2 model outcomes.

|Ticker|UTC minute start|Original event ID|
|---|---|---|
|AAPL|2010-08-31 18:39|P019-001|
|AAPL|2010-08-31 18:43|P019-002|
|AAPL|2010-09-07 16:00|P019-003|
|AAPL|2010-09-07 16:39|P019-004|
|TSLA|2010-11-19 20:39|P019-012|
|TSLA|2010-11-19 20:55|P019-013|
|AAPL|2010-12-17 20:55|P019-014|
|AMZN|2010-12-08 16:26|P019-016|
|AMZN|2010-12-08 16:42|P019-017|
|BAC|2011-01-25 15:10|P019-019|
|AAPL|2011-01-03 18:43|P019-020|
|AAPL|2011-01-13 16:31|P019-021|
|AAPL|2011-02-18 20:32|P019-022|
|AAPL|2011-02-18 20:40|P019-023|
|AMZN|2011-03-25 17:02|P019-024|
|AMZN|2011-03-25 17:14|P019-025|
|AMZN|2011-06-23 17:53|P019-037|
|BAC|2011-10-10 13:37|P019-039|

The historical investigation scanned absolute consecutive genuine close/open log jumps exceeding log1.25, minute bodies exceeding log1.25, H/L>1.5, and shifts in median first/previous-last30 RTH closes. These retrospective diagnostics proposed events; they are **not** a reproducible contemporaneous information set or an automatic rule to remove every large move. In particular session-median investigation can require later minutes. Replicate the literal dispositions above, and separately flag historical availability. The source did not prove these 18 records were vendor errors rather than real trades.

### 4.3 Bounded close-input proxies and source QA

First derive the original unadjusted canonical QA/proxies. At each genuine RTH close, flag a source action-uncertain hour if absolute log change from the previous genuine RTH close (including prior session/month) exceeds log1.25. First source observation has no jump unless a preceding observation is present. This flag blocks original proxy generation, not genuine return retention. Do not substitute the later action-corrected jump flag for this ordering.

Within each completed hour, form runs of missing canonical closes. An hour with no genuine observations or any action-uncertain minute gets no proxies. Reset previous close/gap at each session open. For a missing run `[a,b)`, total known run length is `b−a`, plus the previous hour's trailing missing count if a=0. Its candidate price is the genuine close immediately before a within the hour, or the most recent same-session genuine close from earlier hours when a=0. Fill the whole run only if total known length≤5 and this preceding price exists and is finite. If a later minute **inside the completed hour** reveals length>5, fill none. Do not use later-hour evidence to retract a short trailing run. Maintain last genuine close and trailing gap across hours of the same session, including empty hours. Proxies have OHLC all equal preceding price and volume0 as an **unknown-volume placeholder**, not an observation. A leading session-open gap has no preceding same-session price and stays missing.

Adjusted-hour construction then removes the 18 quarantines, adjusts genuine RTH OHLC, and aggregates each scheduled stock-hour. Genuine open exists only if the first remaining timestamp equals hour start; genuine close only if last timestamp equals hour end−1 minute. Otherwise corresponding O/C is NaN. H/L are extrema over remaining genuine rows, **but both become NaN for any quarantine-containing hour**. In other incomplete hours, observed extrema can be finite lower-coverage extrema; they are not filled with proxies. Observed volume is the sum over remaining genuine rows; empty aggregation has no genuine volume population. Quarantine-containing hours allow no proxy, even if an old proxy existed. A missing terminal close may otherwise use the previously generated cap5 terminal-minute proxy, multiplied by the price split factor. This is `close_input_cap5`; genuine `close` remains separate and is mandatory for labels. Proxy cap is not a target tolerance.

Volume feature eligibility: at least one remaining genuine minute, absent-minute count≤5, longest missing canonical run (including a previous-hour leading gap)≤5, and **zero** conflicting, quarantined or invalid minutes. The observed sum is used for eligible bins; absent minutes contribute no volume (lower bound, not verified zero). Ineligible volume is NaN. Quarantine, conflict and invalid counts are separate, never silently treated as absence. Genuine zero volume is allowed. Volume pseudocounts are learned later.

Audit citations: `src/lstm_data/hf_minute_long_qa.py:48–119,175–548` (`valid_values`, `process_month`, proxies); `hf1m_action_source.py:76–304` (`price_factors`, `adjust_prices`, `derive_month`); `hf1m_ft16_math.py:35–66` (`volume_fields`); `configs/hf1m_p019_verified_event_facts_v1.json`, events; `reports/data_audit/ta019b_action_qa_2026-10-22_201224/unresolved_event_ledger_v3.json`, the 18 specified event IDs. No protected numerical source was needed for these fixed pre-2025 dispositions.

## 5. Grid, warmup, origin eligibility and tensors

**CI plus E/V original population receipts.** Build one chronological grid of scheduled **full** hours, retaining holes; 20 rows per grid position in the stock order. No compression of missing hours. At a nonopening origin, last input index j is the grid hour ending at t; at 09:30 it is the largest full-hour end strictly before t. First index is j−47; input is exactly these 48 positions oldest→newest. This can cross nights, holidays and early closes. Stubs never occupy a position.

For each stock, require all 48 `close_input_cap5` values finite. At the final indexed step require at least 126 preceding/current-reference regular-session positions as encoded below (`previous_regular_day_index≥125`, zero-based) and cumulative count of finite **genuine full-hour closes**≥360 from source start. These are structural input gates, not all16-native gates: unavailable native features may be imputed. Input admission for an origin is AND over all20 stocks. For an opening origin this exact gate is evaluated at the previous full-hour index, not recomputed at the new open.

COP dependency rule: let `p` be index of last regular day strictly before a grid step's session date. Before 2012-05-01 basis_ok=true. On/after it require p≥125 and the date of regular day p−125≥2012-05-01. Form a trailing48-position AND of basis_ok with a full48 requirement. COP blocked at post-boundary steps where that AND is false. Block every native common/M2 feature at those steps and disallow input eligibility there. This deliberately extends beyond the immediate spinoff. Other stocks have no analogous boundary exclusion in the executed fact set.

`source_input_eligible` depends only on this source/input gate, not future primary label success. Final primary `eligible` also requires all20 positive finite genuine origin and endpoint prices on compatible COP basis, date≥2011-04-01, and later role maturity/embargo. Missing one primary endpoint drops the entire 20-stock origin. Missing intermediate close or next open affects only auxiliary support. Historical label-completeness selection is not a live eligibility proof.

Shapes: common features `[full_hour,20,15]`; M2 `[full_hour,20,7]`; origin rows hold `entry_index,first_step,context`; assembled X `[origin,20,48,16]` float32. For each origin, the **forecast origin context** chooses M2's context at every one of its 48 historical steps; it is not replaced by each historical hour's own slot. Flatten origin-major then stock-major for LSTM calls to `[origin*20,48,16]`. Clock `[origin,10]` is repeated20 times in the same order. Target R,A and mask are `[origin,20]`, signed auxiliary labels `[origin,20,3]`. Inference receives only X and clock. No quality/fallback/auxiliary mask is a 17th input.

Audit citations: `src/lstm_data/hf20_s4_preflight.py:23–67,226–288`; `hf1m_action_masks.py:39–41`; `hf20_s4_witnesses.py:22–61`; `hf20_mag_designa.py:369–397`.

## 6. Complete FT16 mathematics

**CI; historical phase parity and all16 witnesses are E/V receipts, not fresh verification.** Compute source/rolling arithmetic in float64, then transform into float32 network arrays. All logs are natural. Raw missing/invalid operations produce NaN, later subject to phase-fitted fallback; never invent a zero target. No clipping/winsorization.

Let O,H,L,C be adjusted hourly genuine open, observed high/low, and **C=close_input_cap5**. Let G be independently genuine hourly close, V the volume-feature value defined above. Ordered full-hour index h includes early-close full hours. OC=log(C/O). Define rolling mean `roll(x,n,m)` over the n scheduled positions ending at current position, requiring at least m finite observations, averaging only finite values, but disallowing any three consecutive NaNs wholly in that n-window. Before n scheduled positions exist, result is NaN even if m exist. `rms` applies that mean to squares then sqrt. Do not compress time to last n valid observations. Missing inputs in this pipeline are NaNs; infinities are later rejected/imputed, not made observations. For compatible-regime rolling quantities also require first and last window regime equal (regimes here are monotone).

Regular days are those with exactly six full-hour grid positions. For each regular day d: D_d=G at the last full hour (15:30), independently of earlier missing hours. U_d=sum of six V values **only if all six are finite and volume regimes compatible**, otherwise NaN. U is six-hour volume, not full-session volume. Daily return δ_d=log(D_d/D_{d−1}), made NaN across price-basis change. The preceding regular day is selected strictly before the historical input step's date; early-close days do not create daily-reference rows. No current-day final value is available to intraday steps.

Per-stock positive floors h_i,d_i,m_i and volume pseudocounts q_hi,q_di are fitted separately per phase (§7). Below, max with NaN remains NaN.

|Index/name|Exact native formula and support|
|---|---|
|0 M1|OC_h / max(rms(OC,60,57)_h,h_i). Current hour body, not close-to-close hourly return.|
|1 M2|Same-context matured prior-regular-origin mean20 / max(RMS60,m_i), defined fully below.|
|2 M3|log(D_p/D_{p−5}) / [sqrt(5) max(rms(δ,63,60)_p,d_i)], p preceding regular day.|
|3 M4|log(D_{p−20}/D_{p−125}) / [sqrt(105) max(rms(δ,63,60)_p,d_i)].|
|4 V1|log(max(rms(OC,12,12)_h,h_i)).|
|5 V2|log(max(rms(OC,60,57)_h,h_i)).|
|6 V3|V1−V2 in native log units, before either channel is scaled.|
|7 B1|log(H_h/L_h); observed genuine extrema, NaN for quarantined hour.|
|8 B2|(2C−H−L)/(H−L). If finite H−L=0 output0. Nonfinite width gives NaN; abs(result)>1+1e−10 gives NaN, **not** clipping.|
|9 Q1|log((V_h+q_hi)/(same-slot preceding20-volume mean+q_hi)). Same-slot mean requires19/20 and no three-position NaN run, excludes current hour.|
|10 Q2|log((roll(U,5,5)_p+q_di)/(roll(U,60,57)_p+q_di)); compatible volume regimes.|
|11 T1|log(C_h / roll(D,20,19)_p), compatible price regime for SMA20.|
|12 T2|roll(sign(δ),20,19)_p. Zero return contributes0; bounded identity channel.|
|13 T3|(EMA6(C)_h−EMA18(C)_h)/C_h, with state/warmup below.|
|14 T4|(EMA24(C)_h−EMA72(C)_h)/C_h, same state/warmup.|
|15 T5|Normalized Wilder RSI14, `(RSI−50)/50`, with state/warmup below.|

MOM5/MOM105 are direct shifted daily ratios, not sums of the δ series. COP's dependency envelope above independently blocks histories crossing its price discontinuity. Other split events do not create a price-basis reset because historical OHLC already share the backward basis.

**Q1 exact ordering.** Group grid positions by within-session full-hour slot (0...5; early closes retain slots0...2). In each slot sequence, shift V by one, then apply roll20/min19. Regime guard compares the current indexed volume-basis sequence at first and last positions of that 20-window; additionally for slot index k≥20 require basis at original slot position k−20 equal current basis. Thus a new split regime does not borrow an old share-unit denominator. No normalization by minute coverage fraction. Zero V works via positive pseudocount when available; an unavailable regime pseudocount gives a missing feature.

**EMA/RSI exact state.** Separate state per stock. First finite positive C initializes EMA6/18/24/72 to C and leaves ema_updates=0. Each later finite update uses α=2/(period+1), E←αC+(1−α)E and increments ema_updates. A missing C freezes EMAs, sets RSI predecessor to absent and, if Wilder averages are not initialized, clears pending initial changes. Three consecutive missing scheduled full-hour values reset **all** state; basis change also resets. Regular overnight time alone is not a gap. On recovery do not bridge the missing interval with an RSI difference. First14 consecutive available changes initialize average gain/loss to their ordinary mean positive/negative changes; subsequent updates use `(13*old+new)/14`, incrementing wilder_updates. T5 requires at least140 subsequent Wilder updates. Both averages0→T5=0; loss0→1; gain0→−1; otherwise `1−2/(1+gain/loss)`. T3/T4 require ema_updates≥360. All three channels also require current C finite and roll(C,72,69) finite (including no triple gap). Warmup is state update count, not merely elapsed positions.

**Expanded M2, all seven contexts.** Independently compute genuine signed R for every scheduled candidate stock cell (§8), even where a different stock or input window renders the primary origin ineligible. For each regular day and each context keep its scheduled R slot. At historical input-session open d09:30, select the preceding20 and preceding60 **regular origin days**, same context. Mask any slot whose endpoint+2 minutes is ≥d09:30 and any invalid genuine return; do not replace it by an older valid slot. Mean20 needs19, RMS60 needs57, both use max2 consecutive missing positions and full scheduled-window lengths. For regular input days require20/60 preceding regular positions respectively. For an early-close input day the executed branch populates both quantities only when ≥60 preceding regular days exist, then applies the same20/60 windows. Hold both statistics fixed for all full-hour steps that day. An immature preceding-day overnight target remains missing even if it matures later that morning. M2 uses the **historical input day's** lock at each sequence step, not the eventual forecast's later information. Apply COP block after reconstruction. This dynamic historical state can incorporate earlier matured calibration/OOS outcomes during later days, with no refitting of scales or weights; it is not forbidden future information if the stated lock is honored.

All channel dependency times: OC/range/close/volume/indicators use source minutes no later than that full-hour end; daily quantities use prior regular day's15:30 references; Q1 uses current V plus prior same-slot full hours; M2 uses only returns mature strictly before that historical session's09:30. Every channel may also depend on the phase's frozen training estimator and retrospective action/quarantine policy. Logical interval causality is not proof of vendor arrival. Q1's20 positions are prior occurrences of that scheduled slot: a half-day has no slots3–5 to insert into those slot sequences. A scheduled but missing full hour remains a position. Wilder's initial14-delta gain/loss means use Python `statistics.fmean` in the inspected implementation; subsequent state arithmetic is double precision.

|Logical datum|Observation/dependency frontier|Availability assumed vs proved|Role/issue use and future-dependent flag risk|
|---|---|---|---|
|Raw minute OHLCV at m|Interval[m,m+1min)|Minute-start semantics documented; historical delivery unmeasured|QA can see whole completed bin; future corporate-action/quarantine decisions are separate retrospective dependencies.|
|Genuine origin price|Nonopening close(t−1min); opening open(t)|Assumed usable by t+2; no measured receipt|Primary label begins at nominal t; not an executable fill. Opening reference cannot certify09:30 live issuance.|
|Full-hour O/H/L/C/V and cap5 close|All included source intervals end≤hour end|Assumed available by end+2|Latest hour end=t is only usable at assumed issue t+2; same-bin gap decisions known then, later-bin retraction prohibited.|
|Daily D/U, momentum/RMS/SMA/T2|Prior regular day's15:30 plus earlier regular days|Same source-delay proxy; not full-day auction data|Strict preceding-day map; no current session end/stub. Historical action/quality revisions remain possible.|
|Q1 and EMA/RSI|Current full hour plus past scheduled same-stock state|Same hour-end+2 assumption|No interstock/time fill; phase fallback may replace native NaN, but fallback not an observed source price.|
|M2 history|Prior regular origin labels with e+2<that input day's09:30|Maturity proxy, not delivery receipt|Frozen within input day; later mature OOS history may update later days. Current/future target forbidden.|
|Floor/scaler/fallback/s_phase|Entire lawful phase prefix; label scale uses admitted mature training labels|Available only after phase fitting|Applied retrospectively to training windows as fitted parameters, then frozen for selector or cal/OOS. They need not have existed at each historical training input timestamp.|
|Aux triples/mask|Current true close, next open, final endpoint|All assumed mature by endpoint+2|Training/diagnostic labels only, never inference inputs. Missingness depends on later source observations.|
|Primary label eligibility|Genuine origin and endpoint complete20|Retrospective scoreability, not origin-known live eligibility|Can depend on future endpoint absence; preserve and flag sample selection.|
|CLOCK/category|Current and next known exchange schedule|Schedule-known assumption; exceptional announcement vintage unproved|No future price input; next date can be calendar-only2025.|
|C3 coefficients|All admitted calibration forecasts/labels after frozen September model|Fit after tail labels mature|No selector/OOS residuals, no new model/scaler fit, then frozen for OOS.|

Audit citations: `src/lstm_data/hf1m_ft16_math.py:15–245`; `hf1m_ft16_fit.py:13–89`; `stock_features.py:45–96`; `hf20_s4_preflight.py:157–222`; `hf1m_ft16_source.py`, ORDER/COMMON/BOUNDED. The old two-context FT16 configuration is superseded **only for M2** by the executed seven-context S4 fitting/assembly.

## 7. Phase-fitted normalization and fallback

**CI mathematics, E/V eight-recipe parity receipt.** For each initial and restricted-refit phase independently:

1. Collect `source_input_eligible` origins with dates2011-04-01 through phase stop inclusive, regardless of their future label success. Union all full-hour indices in their48-step histories. Clip union to grid dates2011-04-01 through stop. Count each stock-hour key once, not once per overlapping window. Do not fit on selector/calibration/OOS. `unique_day` is first union-selected grid index per date.
2. Per stock hourly floor h_i is ordinary NumPy linear-interpolated5th percentile of finite positive RMS12 and RMS60 values concatenated over fit hours (both populations included). Daily floor d_i is5th percentile of finite positive RMS63 at unique_day. Empty positive population is fatal.
3. M2 floor m_i: at unique_day, collect finite positive M2 RMS separately for each of seven contexts. Each context has total weight1/7, uniform among its values. Take weighted-left5th percentile of pooled values. All seven must have positive support.
4. Per stock and volume regime present in fit hours: q_hi=.01×ordinary median of positive finite hourly V in that regime/fit-hour union; q_di=.01×ordinary median of positive finite U for regular dates2011-04-01 through stop in that regime. Both populations must exist to create the pair. Otherwise leave that regime without pseudocounts; never borrow another regime's share units. Daily U population is date-clipped, not restricted to unique_day.
5. Build all native channels. For each common channel except M2 pool finite values over fit hours×20 stocks equally. Center is ordinary NumPy median, scale is **unscaled MAD** median(abs(x−center)); if MAD≤0 use `(Q75−Q25)/1.349`, then weighted/unweighted population SD about the mean if needed, then1 for an exact constant. Quantiles without supplied weights are NumPy's default linear interpolation. No1.4826 factor. Empty native population is fatal.
6. B2,T2,T5 keep center0/scale1 and replace nonfinite values by0. Others replace nonfinite native values by their native training median then subtract center/divide scale (fallback becomes0 in scaled units). No feature clipping. Float32 conversion must leave every tensor finite.
7. M2 scaling: finite native M2 values at unique_day over all stocks, separately by context. Each context has mass1/7, equally divided among its finite cells. Apply the same robust procedure with weighted-left quantiles and weighted population SD. Use its median for fallback; one scaler shared across contexts/stocks. Do not use window multiplicity.

Weighted-left quantile: stable sort values ascending, preserve corresponding weights; normalize cumulative weights by total; return first value whose cumulative mass≥q (left search), capped to final index. No interpolation between observations, including at median ties. Unweighted medians/percentiles above retain interpolation. All scaling is phase-specific. Future calculations use frozen recipe but causally evolving raw histories.

Audit citations: `src/lstm_data/hf20_s4_fit.py:14–153`; `hf1m_ft16_fit.py:13–45`; `hf20_mag_designa.py:369–397`; `hf20_s2c_ca.py:283–310`; run `phase_parity.json`.

## 8. Primary labels, auxiliary labels and phase scale

**E/V executed target contract; CI upstream construction.** For opening origins P_t is genuine09:30 minute open. Other P_t is close of genuine minute t−1. Endpoint P_e is genuine minute e−1 close. No previous-close proxy, filled minute, hourly nominal close or fabricated auction. With positive finite compatible references, compute float64 R=log(P_e/P_t), A=abs(R). This is price-only endpoint magnitude, not sum of absolute legs, realized volatility/variance, signed alpha or executable P&L. Adjacent hourly origins overlap heavily; they are not independent observations.

For each phase's admitted primary training origins, let S be number of sessions, O_d eligible origins in session d. Cell weight w=1/(S O_d 20). `s_phase=max(weighted_left_median(A,w),1e−8)`. M=log1p(A/s_phase). Recompute initial/refit s from their separate legal labels; no scale learned on the auxiliary subset. In actual training cast signed R to float32 **before** abs/division/log1p in Torch. Selector target also uses that float32 sequence. Do not train on the float64 transformed values if seeking arithmetic fidelity. Evaluation A remains float64.

For an OVERNIGHT stock-origin with exactly one closure, source current true session close C_d from final-minute close, next session open O_next from its09:30 minute open, and original P_t/P_e independently. Require main compatible finite return and finite genuine C_d/O_next. Upstream valid-candle checks make them positive; S2-C's gate explicitly verified positivity of all supported values. Supported mask is common to all three heads; intraday mask always false. Signed labels:

`R_pre=log(C_d/P_t); R_gap=log(O_next/C_d); R_post=log(P_e/O_next)`.

Their signed sum must match R with absolute tolerance1e−12, relative1e−11. Do not recover any missing leg algebraically. Do not feed labels or mask to inference. An invalid auxiliary cell has NaN labels and zero auxiliary weight; index valid cells **before arithmetic** to prevent NaN×0. Do not give intraday cells zero gap labels. Missing intermediates never remove an otherwise eligible primary origin. Endpoint+2 maturity is later than all needed leg prices for supported geometry; role maturity therefore covers all heads. The original gate verified exit date is the immediately following scheduled session and no supported COP target crosses its boundary.

Audit citations: `src/lstm_data/hf20_s4_preflight.py:143–155,226–319`; `hf20_s2c_ca.py:158–224,283–309`; `source_validity.json`, `source_formula_checks.json` in the C-A run.

Historical mask geometry expectations (counts only, not model outcomes). Each supported cell has all three labels; primary rows remain unchanged. These are checks on an independently generated mask, not permission to load it.

|Fold / role|Overnight origins|Supported triples|All20-supported origins|
|---|---:|---:|---:|
|F21 / inner_train|6474|128566|5613|
|F21 / selector|195|3890|185|
|F21 / restricted_refit|6697|133012|5822|
|F21 / calibration|165|3256|131|
|F21 / oos|533|10465|421|
|F22 / inner_train|7103|141061|6169|
|F22 / selector|152|2901|86|
|F22 / restricted_refit|7286|144561|6273|
|F22 / calibration|137|2729|126|
|F22 / oos|665|13167|570|
|F23 / inner_train|7793|154640|6719|
|F23 / selector|177|3477|148|
|F23 / restricted_refit|7998|158667|6889|
|F23 / calibration|139|2763|122|
|F23 / oos|505|9978|389|
|F24 / inner_train|8380|166238|7202|
|F24 / selector|167|3291|124|
|F24 / restricted_refit|8578|170146|7354|
|F24 / calibration|90|1782|72|
|F24 / oos|570|11251|433|

Audit citation: `reports/experiments/hf20_s9_mag_stage2_s2c_s2d_readonly_coverage_audit_2026-10-28/S2C_ROLE_SUMMARY.csv`, fold/role rows.

## 9. Schedule-only CLOCK inputs

**E/V.** Ten float32 values, in order: seven one-hot indicators for09:30,...,15:30; `(session_close−t in minutes)/240`; `1{remaining<240}`; `(next scheduled session's local date−current local date in calendar days)/7`. No fitting, cap or centering. The last field is present even for intraday targets. Friday→Monday is3/7; holiday weekends can be larger. Early close uses actual remaining time. Crossing flag must equal the endpoint-based category. These are schedule metadata, shared across stocks, concatenated **after dropout of final hidden state**, before every head. Clock variables themselves are not dropped. This is not a clock input at each recurrent time step. Future calendar knowledge is assumed; historical announcement-vintage proof for exceptional closures is unavailable.

Audit citation: `src/lstm_data/hf20_stage2_bcd.py:97–118,452–472`.

## 10. Design A role-generation algorithm and fixed roles

**E/V.** Regenerate rows, not saved indices. First-of-window date is the session date at first_step; invalid index gets sentinel `0000`. For requested inclusive role start/stop, admit rows with primary eligible=true, origin session date in [start,stop], first-of-window date **strictly greater** than embargo date, and label_maturity **strictly less** than local stop-date20:00. Implement that cutoff as local midnight(stop)+20 elapsed hours (the executed expression was +1day−4hours); these cutoffs do not coincide with DST-transition dates. Embargo `0000` means no extra boundary restriction. Do not remove early-close origins merely because fewer hours occur that day.

For OOS year Y, identify last scheduled full-hour grid session on/before September30 and December31 of Y−1. Evaluate selector start months July, June, May of Y−1, in that order. Initial cutoff is last scheduled grid session **before** start date. Construct selector with cutoff September and embargo initial cutoff; choose the first/latest candidate having≥50 eligible sessions and≥25 eligible origins in **each of all seven slots**. Coverage only, not validation loss. If none passes, block; do not choose a fourth window. F21 retained the same July choice. Initial train starts2011-04-01; restricted refit starts2011-04-01 and ends September cutoff; calibration October1→December cutoff with September embargo; OOS January1→December31(Y) with previous-December embargo. Purge any target whose maturity violates its own cutoff even if its nominal origin is inside the role. This yields gaps in admitted dates beyond calendar boundaries.

|Fold|Initial stop|Selector start/stop|Refit stop|Calibration stop / OOS embargo|
|---|---|---|---|---|
|F21|2020-06-30|2020-07-01 / 2020-09-30|2020-09-30|2020-12-31|
|F22|2021-04-30|2021-05-01 / 2021-09-30|2021-09-30|2021-12-31|
|F23|2022-05-31|2022-06-01 / 2022-09-30|2022-09-30|2022-12-30|
|F24|2023-05-31|2023-06-01 / 2023-09-29|2023-09-29|2023-12-29|

Counts below are integrity expectations, **not replacements for selection arithmetic**. Rows=20×origins. Dates are actual first/last eligible dates.

|Fold/role|First–last date|Sessions|Origins|Stock rows|
|---|---|---:|---:|---:|
|F21 initial|2011-04-01–2020-06-30|2100|11449|228980|
|F21 selector|2020-07-13–2020-09-30|57|349|6980|
|F21 refit|2011-04-01–2020-09-30|2164|11846|236920|
|F21 calibration|2020-10-12–2020-12-30|56|283|5660|
|F21 OOS|2021-01-13–2021-12-31|188|955|19100|
|F22 initial|2011-04-01–2021-04-30|2301|12560|251200|
|F22 selector|2021-05-12–2021-09-30|58|278|5560|
|F22 refit|2011-04-01–2021-09-30|2366|12888|257760|
|F22 calibration|2021-10-12–2021-12-31|50|245|4900|
|F22 OOS|2022-01-12–2022-12-30|210|1180|23600|
|F23 initial|2011-04-01–2022-05-31|2526|13776|275520|
|F23 selector|2022-06-10–2022-09-27|59|313|6260|
|F23 refit|2011-04-01–2022-09-27|2592|14137|282740|
|F23 calibration|2022-10-13–2022-12-30|48|258|5160|
|F23 OOS|2023-01-13–2023-12-29|187|887|17740|
|F24 initial|2011-04-01–2023-05-31|2719|14824|296480|
|F24 selector|2023-06-12–2023-09-29|69|291|5820|
|F24 refit|2011-04-01–2023-09-29|2795|15167|303340|
|F24 calibration|2023-10-11–2023-12-29|40|163|3260|
|F24 OOS|2024-01-11–2024-12-31|208|991|19820|

Total OOS80,260 rows/4,013 origins/793 sessions. OOS slot counts ordered09:30→15:30: F21 `[130,146,149,135,131,125,139]`; F22 `[152,177,188,174,159,162,168]`; F23 `[99,133,152,137,115,120,131]`; F24 `[114,154,157,154,135,140,137]`. These are selected source populations, not every exchange session. Initial/selector disjoint; initial and selector are subsets of refit; refit/calibration and calibration/OOS disjoint. Calibration tail can have fewer than50 sessions; do not import the selector's50-session minimum into calibration. No same-year OOS labels choose that fold's model, epoch or calibration, but the repeated reuse of 2021–24 for research makes the overall study exploratory rather than pristine confirmation.

Audit citations: `src/lstm_data/hf20_mag_designa.py:64–77`; `hf20_mag_designa_continue.py:30–157`; `.../hf20_s9_mag_stage1_session2b_fourfold_2026-10-27/role_counts.csv` and `selector_candidates.csv`; `hf20_mag_o1.py:71–200`; C-A preflight role identity.

## 11. Architecture, defaults, initialization and numerical execution

**E/V explicit settings; CI library default expansion; U full historical binary stack.** CPU float32, one unidirectional LSTM layer, input16, hidden32, batch-first; no projection, packing, recurrent dropout or state carry. Every stock-window starts h0=c0=0. For each chronological step:

`[a_i,a_f,a_g,a_o]=W_ih x + b_ih + W_hh h_prev + b_hh` in gate order input,forget,candidate,output; `i=sigmoid(a_i), f=sigmoid(a_f), g=tanh(a_g), o=sigmoid(a_o)`; `c=f*c_prev+i*g`; `h=o*tanh(c)`. Both bias vectors are present. Use final h after48 steps.

Apply elementwise inverted dropout p=.10 to final h in training: retained entries divide by.9. Eval disables dropout. Concatenate ten clock values to yield42. Main linear42→1 is unconstrained Mhat. Auxiliary linear42→3 yields u_pre,u_gap,u_post; signed raw prediction is s_phase*u. All heads share the **same dropped representation** for a training forward call. No main activation or aux-to-main output link. LSTM parameters128×16 +128×32 +128+128=6400; main43; auxiliary129; total6572. CLOCK control lacks the129 auxiliary parameters and totals6443.

Before each initial and each fresh refit: Python random.seed42, NumPy legacy seed42, Torch manual_seed42; deterministic algorithms true. Construct in order LSTM, Dropout (no parameters/random draw), main Linear42→1, auxiliary Linear42→3; cast to float32. Do not instantiate an unused32→1 head first. LSTM initializes each parameter in registration order W_ih,W_hh,b_ih,b_hh uniform[−1/sqrt32,+1/sqrt32]. Main then auxiliary each initialize weight via PyTorch Kaiming uniform with a=sqrt5 (equivalent bound1/sqrt42), then bias uniform[−1/sqrt42,+1/sqrt42]. Both LSTM biases are random, not zero; no special forget-bias1. No reseeding per batch/epoch; dropout RNG advances through training. Validation eval does not consume dropout draws. Auxiliary initialization consumes RNG after the main head, so matching the initial main parameters to CLOCK does not imply the same later dropout trajectory.

Torch2.10.0 is pinned/documented; four intra-op and one inter-op threads are explicitly set. No GPU execution is part of the historical run. Current extraction environment, **not proved run-time snapshot**, is Python3.14.6 (Clang21), NumPy2.5.3, pandas3.0.6, PyArrow23.0.1, exchange-calendars4.13.2, tzdata2026.5. Backend dispatch/BLAS/OS/hardware and package binaries are not archived conclusively. Bitwise reproduction may depend on these. Independent implementation may use public libraries but cannot import project helpers. All scalar definition/rounding distinctions in this specification remain binding even if numerical tolerances are needed.

Audit citations: `src/lstm_data/hf20_stage2_bcd.py:452–472`; `hf20_s2c_ca.py:32–51,643–673`; `neural_engine.py:22–66`; local Torch2.10.0 `nn/modules/rnn.py` parameter creation/reset and `linear.py:117–128`; S2-B session report §9.

## 12. Objective, minibatches and optimizer

**E/V.** Primary phase risk is `L_M=Σ_d Σ_o Σ_i (Mhat−M)^2/(S O_d 20)` over all primary cells. Auxiliary weights are constructed **once per phase**: restrict primary origins to OVERNIGHT; let S_N count sessions with any such origin and N_d their overnight-origin counts. Base aux cell weight b=1/(S_N N_d 20), zero outside overnight/phase. Let m be complete-triple mask. Global mass Z=Σ b*m; require finite Z>0. Final a=b*m/Z. Do not recompute N_d using only all20-supported origins or surviving stocks; no per-origin redistribution to make a partially masked origin whole. The three risks use these same a values and errors `(u_k−R_k/s)^2`. Intended full objective is

`L_total=L_M + (.10/3) Σ_k Σ_cells a_cell (u_k−R_k/s)^2`.

An epoch visits every admitted training session once. Sort session dates, shuffle with **NumPy default_rng(42+epoch)**, starting epoch1. Do not use the similarly named older hash-seeded session sampler. Consecutive groups of16 session dates form batches; retain smaller last group. Include all phase origins and all20 stocks of those dates, preserving original order within each session. No sequence packing/padding or drop-last. Updates per epoch=ceil(S/16). No sample weights by year within a phase.

For batch with B actual sessions, primary autograd loss recomputes hierarchical weights `1/(B O_d 20)`. Auxiliary autograd loss is `(S/B)/3 × Σ_batch,mask a_cell Σ_k(u−R/s)^2`. Total adds .10×that auxiliary loss. Thus S is **all phase sessions**, not S_N; a already contains overnight and global mask normalization. Empty-aux batch returns differentiable exact zero (`sum of aux predictions *0`) before any NaN-label arithmetic. Convert labels/weights to float32 for autograd. Both losses sum once, one backward, one global clip, one optimizer step. Finite-loss/parameters required. Auxiliary phase weights are float64 before conversion.

Uniform session subsets give an unbiased full-risk estimate at fixed parameters. A finite shuffled pass with a smaller last batch does not make an unweighted mean of batch losses identical to the phase mean: reconstruct the latter using B/S on each fixed-model batch. Actual sequential optimizer updates use the local mean and full learning rate even for the smaller final batch. Stored `batch_main_mean` and `batch_aux_three_head_mean` are unweighted arithmetic means of batch scalars; they are telemetry, not the canonical frozen-model phase objective. Do not silently alter this last-batch convention.

Hand fixture (different from old tests): three sessions A,B,C; A has one intraday origin, B two overnight origins, C one overnight. Each has20 stocks; at B's first overnight origin only10 auxiliaries supported; B second and C all20 supported. S=3,S_N=2; base masses B origins1/4 each,C1/2; Z=1/8+1/4+1/2=7/8. Supported normalized origin masses1/7,2/7,4/7. Let every supported head normalized squared error be9,4,1 respectively. Full mean-three-head auxiliary risk=`9/7+8/7+4/7=3`, contribution.3. A alone has auxiliary0. Batch{A,B}, B=2, has auxiliary `(3/2)*(17/7)=51/14`; batch{C}, B=1, has `3*(4/7)=12/7`. Weighting their estimates2/3 and1/3 returns3; simple average does not. If primary origin errors are A1, B first4, B second16, C9, full primary=(1+10+9)/3=20/3; batch{A,B}=5.5 and batch{C}=9. Missing aux changes none of those main values.

Optimizer: fresh AdamW per phase, lr=.001, betas(.9,.999), eps1e−8, amsgrad=false. Two exhaustive groups in parameter registration order: every rank2 matrix weight decay.01; all other parameters (biases) decay0. No scheduler, momentum warm start, gradient accumulation, mixed precision or post-selection optimizer change. At step t: clip all gradients jointly by min(1,1/(globalL2norm+1e−6)); error on nonfinite norm. Apply decoupled decay θ←(1−lr*wd)θ, Adam moments m←.9m+.1g, v←.999v+.001g², bias corrections `m/(1−.9^t),v/(1−.999^t)`, θ←θ−lr*mhat/(sqrt(vhat)+eps). PyTorch implementation ordering/default CPU dispatch governs floating-point details. Inspected2.10.0 defaults: maximize=false, foreach=None, capturable=false, differentiable=false, fused=None, decoupled_weight_decay=true. Initial moments empty/zero. `zero_grad()` before every forward/backward (default set_to_none=true). An empty-aux batch's zero auxiliary gradient does not mean auxiliary parameters freeze: existing Adam momentum and matrix decay can still move them. Preserve this behavior.

Audit citations: `src/lstm_data/hf20_s2c_ca.py:54–95,368–431`; `hf20_overnight_specialist.py:45–51`; `hf20_ranking.py:39–41`; `neural_engine.py:175–190`. Historical test receipts cover gradient and mask identities; Phase 1 did not run them.

## 13. Selector, fresh restricted refit, and stage order

**E/V.** Fit initial recipe/scale, construct fresh seed42 model/optimizer and phase auxiliary weights. After each epoch, predict all selector origins with eval/dropout off, inference mode, in chronological chunks of32 origins (640 stock-windows). Main prediction reshapes[origins,20]. Compute weighted M MSE only: per-origin mean20 squared float32 errors against float32 Torch-log1p target, then dot with float64 origin weights. Aux labels/loss do not select epochs.

Initialize epoch=0, selected=0, best=+∞, raw_best=+∞, raw_epoch=0, patience=0. At each finite nonnegative validation value v: epoch++; update raw_best/raw_epoch only if v<raw_best. Qualified improvement iff v≤.999*best. If qualified, set best=v, selected=epoch, patience=0 and clone the entire state dictionary. Otherwise patience++. Stop if epoch≥12 AND patience≥10; else stop if epoch≥60. Patience stop takes precedence when both conditions hold. First finite loss qualifies. Ties at a positive best are stale; exact zero equals .999*zero and qualifies. Save qualified best, not raw minimum. Selected epoch can be below12; minimum12 applies to selector execution, not chosen epoch. Original selected values are deliberately sealed and must not become Phase 2 stopping rules.

Discard selector model and optimizer. Refit recipe, s and aux weights on the restricted-through-September population. Reinitialize from seed42 in exactly the same order; confirm initial parameter identity and empty optimizer. Fit **exactly the independently selected epoch count**, restarting epoch shuffle seeds at43. No validation stopping in refit. Freeze final model, recipe and scale. Produce own October–December Mhat, fit fixed C3 (§14), freeze coefficients, then predict following-year OOS. Same refit checkpoint/preprocessing serves calibration and OOS. Saved/reloaded checkpoint must reproduce predictions; never transplant CLOCK or selector weights. Four folds execute chronological F21→F24; no retry/seed/architecture search.

Algorithmic stage order, non-executable: raw QA → fixed action/quarantine hourly and genuine endpoint derivation → calendar/grid/source input masks → FT16 causal components and genuine targets → role construction → per-fold initial recipe/s/weights → selector fit → fresh September recipe/s/weights/refit → frozen-model calibration forecasts → own fixed C3 coefficient fit → frozen OOS forecasts → deterministic scoring. Data geometry and all-fold support gates precede fits. Historical implementation recomputed recipes then referenced equal old recipes; clean-room implementation must retain its own recomputed values instead.

Audit citations: `src/lstm_data/objective_screen_run.py:41–65`; `hf20_s2c_ca.py:453–591`; `hf20_stage2_bcd.py:680–692`.

## 14. Own C3 calibration, decoding and frontiers

**E/V.** Use every primary cell in the calibration role, not only supported auxiliary cells, with calibration-role `w=1/(S_cal O_d 20)`. Given restricted scale s and **unconstrained** float32 network output promoted to float64:

`Ahat_RAW=s*expm1(max(Mhat,0))` (diagnostic only).

`q=exp(log1p(A/s)−Mhat)`. Never clamp Mhat inside q. Require s finite positive, A finite nonnegative, Mhat finite, q finite positive. Use float64 exponential arithmetic. Overflow/invalid fails; there is no clipping, trimming, cap, epsilon stabilization, tail removal or calibrated-output selection.

Global moment c0=Σwq/Σw. For g∈{INTRADAY,OVERNIGHT}, take its fixed schedule-assigned subset and its **inherited original weights**, not rebuilt equal-category-session weights. c_g=Σ_g wq/Σ_g w. Let session mass b_d=Σ_{rows in d,g}w; normalize p_d=b_d/Σb. `n_eff=1/Σp_d²`; rho=n_eff/(n_eff+25); `c*_g=c0+rho*(c_g−c0)`. Require each group nonempty, all masses positive and moments finite positive. Shrinkage counts effective **sessions**, not stock rows or origins. With unequal category share across sessions, n_eff is below raw session count. Do not use auxiliary masks or future magnitude to assign g, and do not borrow CLOCK's c values.

Primary forecast: `Ahat_C3=s*max(0,exp(Mhat)*c*_g−1)`. Clamp decoded A only, after multiplication and subtraction. This differs from multiplying RAW by c*. Calibration and RAW are not competing OOS-selected alternatives. C3 is predeclared primary. Category is constant within an origin; positive factor and monotone transform preserve within-origin order unless clamping creates ties. Report any such ties independently rather than assume their absence.

Frontiers: supervised fit uses only targets with e+2min<role cutoff; a Friday late target can mature Monday and must be excluded from a Friday-ending fit. On a13:00 half-day,09:30 target matures next session10:02; it is not an intraday calibration residual. A refit ending September cannot use October labels, even when origin was in September. Calibration is finalized only after all its admitted labels mature, before following-year OOS. At every historical feature day M2 is locked at09:30, strictly before then for maturity; it does not use that day's newly matured overnight label. Across a split, only defined adjusted-price bases are compatible; volume regime never retroactively becomes homogeneous. Quarantine/action revision timing is an unresolved input-vintage assumption, not solved by these arithmetic frontiers.

Optional calibration diagnostics use contributions v_j=w_j*q_j sorted descending: q_max=max(q); top10_share=sum(first10 v)/sum(v); top1pct_share=sum(first max(1,floor(n/100)) v)/sum(v), separately global and each category. No trimming follows these diagnostics.

Audit citations: `src/lstm_data/hf20_mag_c3_io.py:81–171`; `hf20_overnight_specialist.py:386–390`; `hf20_s2c_ca.py:565–592`.

## 15. Scoring and descriptive uncertainty

**E/V reducers; CI undefined-edge behavior.** A sufficient independent score schema is `origin_id` UTC ISO string, `session_date_et` YYYY-MM-DD string, `slot` HH:MM string, `category` INTRADAY/OVERNIGHT string, `entry_end_utc`, `exit_end_utc`, `label_maturity_utc` aware UTC timestamps normalized to nanoseconds for joins, `ticker` string, `weight` float64, `A` float64, `Mhat` float32, `S2C-RAW` and `S2C-C3` float64. Historical main score files contain these columns; an independent receipt may additionally retain R and diagnostic signed heads, which must never enter inference. Store unique origin-major/stock-major keys and original A, timestamps, slot/category, weights, Mhat, RAW and C3. Join by full keys and verify order, uniqueness,20-name presence and label identity before any comparison. Main scalar outputs remain raw log-return units; MSE has squared log-return units. No percentage-return substitution.

Annual metrics: equal stocks within origin→equal eligible origins within session→equal sessions within year. Observed=ΣwA; predicted=ΣwP; bias=Σw(P−A); MAE=Σw|P−A|; MSE=Σw(P−A)²; ratio=predicted/observed. Four-fold “EQ” means arithmetic average of four annual metrics, **except ratio is average predicted divided by average observed**, not mean annual ratios. Counts sum. Do not pool all years' rows/sessions as one equally weighted population. Differences are new−reference; relative MSE percent is100*(new/reference−1). Original scalar reducer has no custom zero-observed guard: undefined division can produce NaN/inf; expose that, do not invent0. Empty cohorts are skipped.

Conditional scalar metrics (INTRADAY/OVERNIGHT, stock, slot, tail, calendar) retain original annual cell weights, renormalizing by subset mass; **do not recompute equal session mass inside the category**. Category loss contribution=Σ_subset w(P−A)² without renormalization, share=contribution/full annual MSE. Equal-year conditional metrics average corresponding annual values only when all four exist; EQ contribution averages annual contributions; EQ share divides that average by EQ full MSE. This can differ from pooled conditional means. Stock stratification is a requested independent diagnostic under this same rule; the C-A central group table itself emits slot/calendar/tail/C0-decile, while signed auxiliary diagnostics include per-stock results. Do not claim an archived main per-stock table was established when it was not located.

Rank metrics within each20-stock origin:

* Spearman magnitude IC: ascending average ranks for true A and predicted magnitude, subtract each mean, normalized dot product. Constant actual or predicted vector gives NaN. Then pandas-style mean over valid origin ICs in each session, followed by mean over valid session means. Undefined origins/sessions are skipped, not set0.
* Pair concordance over190 unordered pairs: drop genuine A ties; correct predicted sign scores1, predicted tie scores.5, wrong sign0. Divide by number of nontied actual pairs. All-actual-tied case yields undefined; same mean/skip behavior. Predicted tie_rate counts ties among all190; constant_rate marks max(P)=min(P).
* Top4 membership: descending rank_min r_min and rank_max r_max; fractional membership `clip((5−r_min)/(r_max−r_min+1),0,1)`. Its mass is4 even at boundary ties. Bottom4 applies same formula to −values. Retrieval=(true fractional membership·predicted fractional membership)/4. Aggregate origin→session→year and equal years. Rank metrics for a full-origin category **rebuild** equal-origin/session means within that selected category, unlike conditional scalar metrics' inherited mass. Do not substitute one weighting scheme for the other.

Tail cohorts: on each restricted training role fit weighted-left95th and99th percentiles of A with full primary hierarchy. Event is strict A>threshold, complement A≤threshold. No OOS threshold estimation. Within each ALL/INTRADAY/OVERNIGHT scope, event prevalence=event original mass/base original mass. Event top4 recall=Σ_event(w*predicted fractional top4)/event mass. Top4 event precision=that numerator/Σ_base(w*predicted fractional top4). False-low rank is weighted event fraction whose within-origin **ascending average predicted rank≤10.5**. This is bottom-half rank, not bottom4 and not negative signed return. Equal-year event metrics average the four annual rates, unlike the primary mean-ratio exception.

Historical deciles used weighted-left10%,20%,...,90% quantiles of **archival C0 predictions in the OOS year**, unique cut points, then `1+left_searchsorted(cuts,C0)`. These are ex-post forecast-distribution descriptions; they did not set model parameters, target thresholds or selectors. Equal-value boundaries stay in the lower bin. They cannot be reproduced from S2-C forecasts alone, because C0 is a separately fitted model. In clean-room S2-C freeze, omit that archival-comparator-dependent table and mark pending separately authorized C0 implementation; do not use old C0 scores or silently replace with S2-C deciles. Standard full/category/tail/rank metrics are fully independent. S2-C auxiliary signed diagnostic covariance/correlation uses original OOS weights renormalized over supported cells, separately all-stocks or a named stock; zero variance denominator yields undefined. For each component compute weighted signed MSE/MAE, observed/predicted signed means, and Pearson covariance divided by the square root of weighted centered variances; zero denominator gives null. Sessions count distinct origin-session dates with any supported selected cell. These do not evaluate a separately trained S2-D task.

Paired descriptive MSE uncertainty: for each year and chosen scope retain same forecast-target rows, compute daily numerator Σw[(P_new−A)²−(P_ref−A)²] and daily massΣw. Sum both by calendar month, preserving their pairing. Let K be number of present months. Draw a400×K integer matrix uniform0...K−1 with replacement using NumPy default_rng22042; for each draw sum selected month numerators divided by selected month masses. Annual point delta uses unsampled sums; interval is ordinary linear2.5/97.5 quantiles. Annual draws reset RNG22042 for each year. For EQ draws, initialize a **separate** RNG22042 once, draw each year's400×K indices sequentially in F21→F24 order, average each draw's four annual ratios, then take quantiles. No refitting/calibration/selector inside this archival descriptive procedure. Do not bootstrap stocks/pairs/origins IID. Whole months only partly address overlap and dependence; these are not search-adjusted confidence or causal-significance claims. No comparator uncertainty is computable until independent comparator predictions exist.

Audit citations: `src/lstm_data/hf20_mag_designa.py:781–823`; `hf20_ranking.py:20–41`; `hf20_s2c_ca.py:681–891`; `hf20_overnight_specialist.py:620–649`; C-A session report §12 event-retrieval derivation. Prefix thresholds: `hf20_mag_designa.py:680–692`.

## 16. Comparator identities; no hidden dependency on their outputs

**E/V archival identities.** CLOCK-C3 uses same48×16/H32 and10 clock inputs, no auxiliaries, own fixed C3 calibration. Older C3 has no10-clock head and applies fixed category smearing to its own September model. C0 is that older Design A model's RAW decoder; C1a its global residual-smearing correction; M1 its nonnegative raw-A multiplicative calibration. M1 comparator is **not FT16 channel M1**. For clarity their definitions are: base=s*expm1(max(z,0)); C1a=s*max(0,exp(z)*Σ_cal w exp(log1p(A/s)−z)/Σ_cal w−1); M1=k*base with k=max(0,Σw base*A/Σw base²). C0/C1a/M1 share that old restricted model, not S2-C's network.

B0-RMEAN/RMED are September-prefix per-stock weighted mean/left median A. B0-CLOCK is a per-stock/slot mean shrunk toward stock mean with50 origin-equivalent prior mass: origin mass=(number of refit origins)*hierarchical origin weight. B0-VOL is raw-A ridge with intercept,19 stock dummies,6 slot dummies and standardized log current native RMS60, penalties{.001,.1,10} chosen by selector raw MSE; nonnegative clamp. These controls have explicit stock identity, unlike S2-C. They are archival benchmarks, not required ingredients of S2-C training/calibration.

Later classical controls include ROLL20,ROLL60,expanding mean, EWMA-R2 folded-normal, EWMA-A,HAR-RV-A and separately amended GARCH/matched calibration studies. HAR uses full-session minute realized-volatility information and different preprocessing; later G/IO matched raw-A calibrators are not automatically the original transformed-residual C3. S2-D predicts a distinct genuine closing-price-to-next-open gap at a normal15:30 issue and cannot be compared as the same target. S5-C changes the objective. No saved comparator score, fitted coefficient or normalizer may enter clean-room implementation. Independent comparator reproduction requires separate authorization; archival outcomes stay sealed until S2-C results freeze.

Audit citations: `src/lstm_data/hf20_mag_designa.py:488–593`; S2-B/C/D `protocol.json` estimands; `reports/codex_sessions/2026-10-29_114323_hf20_classical_volatility.md`, §3/11; `2026-10-29_201017_hf20_garch_matched_calibration.md`, §3/7.

## 17. Independent fixtures and acceptance protocol

These are mathematical specifications, not executed tests or copied old tests. No Phase 2 implementation is supplied.

|Fixture|Required expectation/tolerance|
|---|---|
|Full/half-day endpoints|All six examples in §3; exact aware timestamps. A 240-minute horizon landing exactly at close stays intraday. No minute from a closed interval counted.|
|DST/holiday|Friday before spring DST→Monday uses new UTC offset;2012-10-29/30 absent;2024-11-29 closes13:00; nominal09:30 that day exits next session10:00. Exact dates/times.|
|Source validity|Identical duplicate counts once; two differing values at same key exclude both even if one otherwise valid; high below open invalid; zero volume retained. Exact masks.|
|Proxy horizon|At completed hour a trailing two-minute gap after a genuine close may fill; revealing longer outage in next hour cannot rewrite it. A six-minute run already inside the bin remains wholly missing. Session-open gap remains missing. Exact values/masks.|
|Action/volume|Pre-split OHLC100 with ratio4→25; volume80 stays80; cross-regime Q1/Q2 unavailable. COP crossing target invalid. Price-ratio invariance tolerance1e−12.|
|Windows|Nonopening last input ends at origin, opening last input before origin; j−first=47; no stubs; exact key/order equality. Change a future minute: preceding features unchanged except documented retrospective policy, which must be isolated.|
|M2 maturity|Prior regular slot maturing exactly current09:30 is missing; one minute earlier admitted. Keep its scheduled position when missing; no older replacement. Later intraday maturation cannot update day's M2. Exact masks, arithmetic1e−12.|
|Quantiles|Values[1,3],equal weights: weighted-left median1, unweighted linear median2. Constant vector robust scale1. No1.4826 MAD multiplier. Float64 tolerance1e−12.|
|Signed decomposition|Prices P=80,C=88,O=84,E=90: sum(log88/80,log84/88,log90/84)=log90/80; abs(sum) differs from sum(abs). Missing O masks all three while leaving main target. Sum tolerance atol1e−12/rtol1e−11.|
|Loss weights|Use §12's unequal-origin/partial-mask fixture: full auxiliary3, contribution.3, main20/3; no-aux batch exactly0 and masked-cell gradient0. Float64 algebra1e−12; float32 gradients atol1e−7/rtol1e−6.|
|Direct recurrence|All LSTM parameters/input zero gives h=c=0 for all48 steps; eval heads with zero weights output biases exactly. For nonzero toy weights compare direct gate recurrence to library recurrence, atol1e−6/rtol1e−5; verify reset between reordered independent samples.|
|Selector|v1=2 qualifies; v2=1.999 raw-improves but does not qualify; v3=1.998 qualifies at equality. Constant positive losses stop at epoch12 after≥10 stale; selected remains1. Exact state.|
|Decoder/smear|s=.02,Mhat=log2,A=.06 gives raw.02,q2. At factor1.5 calibrated.04. Negative Mhat must stay negative in q even though RAW clamps. Two category-session masses3:1 give n_eff=1/(.75²+.25²)=1.6. Float64 tolerance1e−12.|
|Rank/ties|Perfect increasing20 scores: IC1,pair1,top4/bottom4=1. Constant predictions: IC undefined, each top4 membership.2, retrieval.2, concordance.5 when truths untied. Exact tie classification; numerical1e−12.|
|Role frontier|Origin before cutoff with maturity after cutoff is excluded; first-step date equal embargo excluded; one day later potentially admitted. Refit/selector relationships in §10 exact.|
|Hierarchy|Session A one origin loss2, B two origins losses4,8 gives annual loss4, not row-pooled14/3. Four annual metrics averaged equally even with unequal sessions. Exact arithmetic1e−12.|

After separate authorization, first freeze independent code hash, environment/source receipts, reconstructed roles/features/scales, selected checkpoints/epochs, calibration factors, all forecasts and metrics. The implementer must not see old results during construction, selection or debugging. A separate reviewer may then unseal reference results. Compare in order: raw input identity/rows → calendar/reference prices → QA/action masks → full-hour features and maturity → role keys/counts → phase recipe/s/aux mass → initialization/training/selector → own calibration → predictions → annual/equal-year metrics. A matching headline alone is insufficient. Do not tune model settings to reach old OOS scores. Distinguish byte equality (serialization/dependencies matter), arithmetic agreement at declared tolerance, and statistical replication. Any correction to a discovered defect is a separately authorized branch/study; retain historical reproduction first unless human review blocks it.

## 18. Completeness self-audit and unresolved proof

|Requirement|Status|Meaning / residual issue|
|---|---|---|
|Experiment identity, amendment,4/4 receipt|EXACT|C-A separate from blocked C and distinct S2-D.|
|Raw entry paths/schema/174 files/order/counts|EXACT locally|Raw selected extracts identified; upstream completeness/true vendor provenance unresolved.|
|Historical membership, issuer continuity, rights|UNRESOLVED|Fixed symbols are exact; point-in-time universe/AVGO lineage/redistribution proof absent.|
|Calendar, minutes, endpoint/open/close/stub conventions|EXACT algorithm|Current calendar rules expanded; exact historical installed version UNRESOLVED.|
|Raw QA, proxies, actions, quarantine|EXACT inspected behavior|Contemporaneous availability of retrospective dispositions/action metadata UNRESOLVED.|
|All16 formulas, warmup, fallback, precision|EXACT inspected behavior|Transitive upstream source revisions not all individually run-bound; not an instruction to read old code.|
|Input order/48-step geometry/seven M2 contexts/CLOCK|EXACT|Calendar-aware opening/early-close distinctions explicit.|
|Primary/aux labels, masks, denominators|EXACT|Historical source positivity/additivity gates documented; not reexecuted here.|
|Roles and coverage amendment|EXACT|Algorithm/date/counts specified; fresh reconstruction not performed in Phase 1.|
|Initialization/AdamW/dropout/selector/refit|EXACT explicit math|Full historical binary/backend/RNG portability is UNRESOLVED; Torch pinned2.10.0.|
|Own C3 mathematics/category/maturity|EXACT|No original fitted values needed; all estimated afresh later.|
|Main/rank/tail/uncertainty scoring|EXACT|Undefined-edge behavior preserved; descriptive limitations explicit.|
|C0-deciles and comparator paired outputs|UNRESOLVED for S2-C-only delivery|Require independently reproduced C0/other controls; cannot derive from S2-C alone. No archival score access permitted.|
|Vendor arrival / \* nominal-origin mismatch|UNRESOLVED live validity|Known definition mismatch; arrival proxy unmeasured. Preserve unchanged.|
|Run-time commit/transitive source provenance|APPROXIMATE|S2-C source matches prefit hash; historical worktree was dirty/untracked, so base Git SHA alone is not complete execution identity.|
|Original outcomes and chosen epochs|EXACT sealed location|Intentionally absent here, not missing tuning inputs.|

Mandatory review items before claiming exact replication readiness: establish or explicitly accept unavailable historical package/backend snapshot and transitive source binding; accept literal retrospective quarantine/action policy for reproduction despite unproved historical availability; resolve whether independently reproduced comparators (especially C0-deciles) belong to Phase 2 or a later authorization. The latter cannot be silently substituted. No confirmed severe causal leak beyond the expressly disclosed issuance mismatch was established by this read-only extraction; absence of proof is not a clean validity verdict.

Documentary claims of all16/phase parity are not independent replication. This specification is deliberately marked **INCOMPLETE_SPEC** because the requested exact historical provenance and every comparator-dependent output cannot currently be established from the permitted clean-room bundle alone. It supplies the recovered S2-C behavior without opaque project helper references. **STOP for human review.**
