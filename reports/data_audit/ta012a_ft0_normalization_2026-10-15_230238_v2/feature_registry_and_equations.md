# FT0 registry and equations — source-defined audit

Native means a registered engineered channel, not raw OHLCV. Every channel here
is dimensionless: log ratios, return ratios or bounded indicators. Scaled means
the saved pooled transform followed by the exact neural float32 conversion.
No extra Gaussianization, per-stock fitting or clipping is applied.

| Channel | Actual native formula | Support / source equation |
|---|---|---|
| M1 | log(hour close/open) / max(RMS60, fitted hourly floor); normalized, not raw return | signed real |
| M2 | previous 20 origin-matched mature 4h-return mean / floored RMS60; origin-specific | signed real |
| M3 | previous-session-locked 5-day log momentum / (sqrt(5) × floored daily RMS63) | signed real |
| M4 | older log(C[d−21]/C[d−126]) / (sqrt(105) × floored daily RMS63) | signed real |
| V1 | log(max(hourly RMS12, fitted hourly floor)) | signed real |
| V2 | log(max(hourly RMS60, fitted hourly floor)) | signed real |
| V3 | V1 − V2; log short/long volatility ratio | signed real |
| B1 | log(hourly high/low) | >=0 |
| B2 | (2C−H−L)/(H−L), bounded [−1,1]; genuine zero range gives0 plus quality flag | [-1,1] |
| Q1 | log same-slot volume / prior20 matching-session mean, with fitted pseudocount | signed real |
| Q2 | log(prior5 full-session mean volume / prior60 mean), fitted pseudocounts | signed real |
| T1 | log(current hourly close / previous20 daily-close SMA); not raw SMA | signed real |
| T2 | mean sign of preceding20 daily close returns, native [−1,1] | [-1,1] |
| T3 | (EMA6−EMA18)/current hourly close; normalized DIF, not MACD histogram | signed real |
| T4 | (EMA24−EMA72)/current hourly close; normalized EMA difference | signed real |
| T5 | (Wilder RSI14−50)/50, native [−1,1]; includes genuine overnight close changes | [-1,1] |

Equations: `stock_features.py:149` apply_component_floors; `:205` scheduled
hour/daily histories; `:56` EMA/Wilder updates; `:86` bounded RSI; `:316` native
bar/technical features. `pretraining_transforms.py:118` replaces M2 using its
own origin-matched mature-return RMS/floor, not hourly RMS. The other scalar
formulae use the exact saved floors. Q1/Q2 are **signed log volume ratios**,
not positive raw volumes, and already use approved additive stock-specific
pseudocounts (`TA_P2_FT0_Q_VOLUME_001_v1.json`). No second generic log is justified.

Clocks/warm-up: current completed hourly OC return is included in RMS12/60;
12/12 and57/60 valid, at most2 consecutive misses. Daily features use prior
completed full sessions, including genuine closing stub volume; RMS63 requires
60/63. Q1 uses19/20 matching slots; Q2 uses5/5 and57/60. M2 uses19/20 and57/60
previous ordinary origin-specific outcomes, mature by the historical step,
never today's target. EMA6/18/24/72 seed at first good full-hour close then
require360 updates; recent72 need69 good/no>2 misses. Wilder14 requires14
initial consecutive changes plus140 updates and the same recent coverage;
missing bars freeze state and do not bridge a synthetic recovery delta.
Native missing/quality reasons remain available; no imputation. Unknown observed
publication/action vintage is not converted into a certified live clock.

Scaling: exactly M1 M2 M3 M4 V1 V2 V3 B1 Q1 Q2 T1 T3 T4 use pooled training-prefix
median/unscaled MAD. B2 T2 T5 use identity, with only float32 rounding.
`pretraining_transforms.py:195` fits unique symbol/session/slot keys; M2 instead
uses symbol/session/origin and50/50 origin weights. Daily-locked channels other
than M2 still use the registered hourly keys. These are not48 duplicated window
observations. Every recorded center/scale/method and stock-specific floor or
pseudocount is in ft0_tail_and_fallback_audit.csv and floor_recipe_parameters.csv;
scope, source/action/population IDs and actual fitting/constructing clocks are
in population_and_recipe_bindings.json.

Fallback code: `ft0_transforms.py:357`: positive MAD, then IQR/1.349, then weighted
population SD; exact zero SD selects center/scale1 and CONSTANT->zero. Later
variation in a CONSTANT channel is a separate diagnostic, not clipping.
**Document/code discrepancy:** a synthetic nonzero constant [7,7,7] yields
SD8.881784197001252e-16 due to weighted-mean rounding, selecting SD instead of
the D4 constant-to-zero contract. No active recipe uses this branch: all52
recorded scaled-channel fits use positive MAD. Historical math is untouched.
Separate guarded repair review is required before relying on that fallback.

Primary distributions deduplicate hourly observations. M2 necessarily retains
origin in its key because its two values can differ at one timestamp; its fit
population additionally collapses repeated within-session values. For example,
WF1 inner training has6,920 M2 feature fit keys, versus6,880 stock/forecast labels;
four early-close sessions represented in lawful input histories explain the
difference. All four exact fit-population hashes reproduce. OOS masks are the
original saved masks; first16 potential validation/development origins are
excluded where their48-step history precedes the recipe stop, not intersected
away to improve a comparison. Training warm-up is excluded from fit statistics.

Definition notes: constant_rate=max multiplicity/finiteN; near-zero=|x|<=1e-8;
SD uses ddof0; Bowley skew=(p75+p25-2median)/IQR. p-prefixed columns are signed;
abs_p columns summarize |value|. Rates use finite canonical observations.
Temporal rows are non-overlapping pooled months and stock/pooled quarters;
segments separate origin/slot, DST offsets and early-close input sessions.
Hypothetical clipping preserves order but may create ties; cross-stock pair
loss uses only complete five-stock sections, reporting incomplete counts.
All tail identities (not only examples) are in tail_identity_sets.json.gz;
model window exposure counts are separate from primary unique-key statistics.
These observations are dependent; no IID test, change-point significance or
predictive-importance claim follows from these summaries.
