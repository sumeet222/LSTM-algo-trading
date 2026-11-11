# Original input-only feature dependency proof v1 — before numerical reads

Runtime graph: explicit allowed hourly projection → original `hf1m_ft16_math.build` → original `hf1m_ft16_fit.native`/`hf20_s4_witnesses.scaled` with original archived O1 restricted recipe → scheduled48-slot own-stock gather → ComponentMAG main forward → own C-A C3 decode. Seven-context M2 uses **source-derived historical ratios**, strictly matured before each input day's09:30, replacing only the obsolete2-context components in a shallow copy. No saved labels, role/evaluation tables, View, source_components, Phase2 implementation or dummy target arrays enter this graph. Offline risk prep is separate and not imported by producer. Runtime enum is fixed20×calendar origins; unrequested sources are explicit missing placeholders and never issued.

All feature values are per stock. Floors/scalers/fallbacks are SAVED, never re-estimated. Common feature source: `hf1m_ft16_math.py:build`; native formulas: `hf1m_ft16_fit.py:native`; scaler/fallback application: `hf20_s4_witnesses.py:scaled`. Native missingness masks precede archived fallback/scaling, preserving48 scheduled slots. Original COP component masking in build (including aliased VOLUME_H source) is reused; archived floors/pseudocounts retain original pre-fit masking. No Phase2 Q2 current/prior regime guard is added.

|FT16|Original arithmetic|Raw dependency and maturity|
|---|---|---|
|M1|OC/max(RMS60,h_floor)|log(close_input_cap5/open);60 scheduled OC,57 finite,max2 consecutive misses;latest input hour end|
|M2|prior20 mean/max(prior60 RMS,m2_floor)|original seven contexts;19/57 support,max2 misses;prior regular-origin source ratios whose endpoint+2min is strictly before input-day09:30|
|M3|MOM5/(sqrt5 max(RMS63,d_floor))|prior regular genuine15:30 closes, D[-1]/D[-6],63 daily changes60 valid;all prior input day|
|M4|MOM105/(sqrt105 max(RMS63,d_floor))|prior daily closes shifted20/125;126-session warmup;prior input day|
|V1|log(max(RMS12,h_floor))|12 completed scheduled OC,12 valid,max2 missing run|
|V2|log(max(RMS60,h_floor))|60 OC,57 valid|
|V3|V1−V2|same as V1/V2|
|B1|log(high/low)|genuine observed extrema of completed hour;quarantine masks inherited|
|B2|(2close−high−low)/(high−low)|completed hour;zero-width0;outside[-1,1] or invalid width missing|
|Q1|log((VOLUME_H+qh)/(prior20 same-slot volume mean+qh))|observed volume lower bound,cap5 source validity;known share regimes;19/20 prior slots;qh archived per regime|
|Q2|log((prior5 daily volume mean+qd)/(prior60 daily volume mean+qd))|daily6 full-hour volume sums,all valid andsame regime;5/5 and57/60;**no extra current-vs-prior regime guard**;qd archived current hour's regime|
|T1|log(close/prior20 daily SMA)|genuine15:30 daily reference,19/20 same price regime|
|T2|prior20 mean(sign(daily change))|19/20 prior regular dates|
|T3|(EMA6−EMA18)/close|original IndicatorState recurrence from source genesis,360 updates;72 scheduled closes69 valid;reset after3 missing or basis change|
|T4|(EMA24−EMA72)/close|same streaming genealogy as T3|
|T5|normalized Wilder RSI14|same original IndicatorState,140 post-initial updates;state freezes on missing;reset policy as original|

`h_floor`, `d_floor`, `m2_floor`, `qh`,`qd`, scalers and native fallbacks are original archived neural recipe fields, not trading-risk parameters. B2/T2/T5 identity bounded scaler semantics preserved; no clipping added.

CLOCK is exact original `hf20_stage2_bcd.clock_values` arithmetic, extracted without its experiment workflow: CLOCK0..6 one-hot09:30..15:30;CLOCK7=remaining session minutes/240;CLOCK8=remaining<240;CLOCK9=calendar days to next session/7. Cast float32 in original order. Schedule only; known calendar geometry is not a measured historical announcement vintage. No market outcome input. `nominal_endpoint` is calendar arithmetic, not a price read.

M2 context order0..6 =10:30,11:30,12:30,13:30,14:30,15:30,09:30. For each input day, use preceding60 **regular** session origins, retaining scheduled missing/immature cells. Origins reference prior minute genuine close except09:30 genuine open; endpoint references genuine preceding-minute close; no proxy. Their ratio is allowed only after endpoint+2minutes < input-day open. Latest prior overnight origin often remains missing at next day open. Means use last20 slots; RMS last60. Half-day input uses same prior regular-origin dates. COP pre/post2012-05-01 crossing ratios missing; component dependency envelope remains original126-day+48-slot mask. No current or future forecast label is evaluated.

Hourly snapshots reject source values after cutoff before original build. All scheduled current-day full-hour positions exist as NaN until completed, so session classification does not depend on future bar presence. Initial input gate is original48 close_input finite,126 priorregular warmup,360 genuine updates and COP envelope. Genuinely missing input slots abstain, rather than compress time. Original cap5 proxies are inherited completed-hour values only; no new proxy interpolation performed.

Receipt: source interval end distinct from available_at. Hour completion+assumed1/2/5min; M2 original maturity fixed+2. Feature/decision barrier is max dependencies and nominal+scenario delay. Opening reference comes from09:30–09:31 bar, assumed ready09:32 in2min scenario, not a phantom completed hour. All inferred execution markers are strictly subsequent minute START, with no price read. Five-wall-minute deadline is an abstention guard.

Exact streaming EMA/Wilder initialization requires replay from2010-07 genesis unless a verified state archive exists (none identified). Plan therefore projects **only AAPL/COP** hourly history from genesis to sample cutoff, not whole20-stock panel or minute history. Only the last60 regular-origin source anchors needed for48-slot M2 are read from canonical minutes; all are before input-day lock. Per-field lineage conservatively records full recursive hourly envelope plus bounded M2 dependency inventory/hash. This is an envelope proof, not a separate row for every EMA ancestry term. CLOCK entries are calendar-only and conservatively receive the common ready barrier.

Inherited split-consistent March2026 share basis (no split facts after2024), retrospective quarantines, fixed survivor universe, vendor receipt and calendar-vintage uncertainty persist. Source reconstruction within that inherited dataset does not prove point-in-time corporate-action knowledge or live tradability.
