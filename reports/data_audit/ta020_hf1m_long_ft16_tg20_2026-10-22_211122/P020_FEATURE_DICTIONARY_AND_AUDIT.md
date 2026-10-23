# P020 FT16 dictionary and audit

**FEATURE_READY_FOR_TRAINING. Dataset preparation only; neural training is not authorized.**

| Order/name | Formula | History | Inputs / availability | Fallback / scaling |
| --- | --- | --- | --- | --- |
| 1 M1 | log(C/O)/max(RMS60,h) | 60h | cap5 close; genuine open; current completed-hour or earlier only | unique-eligible-training-native median; pooled train median/unscaledMAD with documented nonzero fallback |
| 2 M2 | mean20(previous same-origin matured4h returns)/max(RMS60(previous same-origin returns),m2floor) | 60 previous regular sessions | genuine endpoints; each historical day locked before its open; origin1/2 context; current completed-hour or earlier only | unique-eligible-training-native median; pooled train median/unscaledMAD with documented nonzero fallback |
| 3 M3 | log(D[d-1]/D[d-6])/(sqrt(5)*max(RMS63,dailyfloor)) | 63/5 previous regular sessions | genuine15:30 surrogate; current completed-hour or earlier only | unique-eligible-training-native median; pooled train median/unscaledMAD with documented nonzero fallback |
| 4 M4 | log(D[d-21]/D[d-126])/(sqrt(105)*max(RMS63,dailyfloor)) | 126 previous regular sessions | genuine15:30 surrogate; current completed-hour or earlier only | unique-eligible-training-native median; pooled train median/unscaledMAD with documented nonzero fallback |
| 5 V1 | log(max(RMS12,h)) | 12h | RMS of OC; current completed-hour or earlier only | unique-eligible-training-native median; pooled train median/unscaledMAD with documented nonzero fallback |
| 6 V2 | log(max(RMS60,h)) | 60h | RMS of OC; current completed-hour or earlier only | unique-eligible-training-native median; pooled train median/unscaledMAD with documented nonzero fallback |
| 7 V3 | V1-V2 | 12/60h | log volatility ratio; current completed-hour or earlier only | unique-eligible-training-native median; pooled train median/unscaledMAD with documented nonzero fallback |
| 8 B1 | log(H/L) | current complete hour | trusted observed extremes; missing completeness retained; current completed-hour or earlier only | unique-eligible-training-native median; pooled train median/unscaledMAD with documented nonzero fallback |
| 9 B2 | (2C-H-L)/(H-L), zero range=>0 | current hour | missing if unreliable/outside observed range; current completed-hour or earlier only | neutral0; identity |
| 10 Q1 | log((hour_volume+q_h)/(mean_previous20_same_slot_volume+q_h)) | 20 matching slots, >=19 valid,maxgap2 | <=5absent minutes and no conflict/quarantine; same volume regime; current completed-hour or earlier only | unique-eligible-training-native median; pooled train median/unscaledMAD with documented nonzero fallback |
| 11 Q2 | log((mean5daily_volume+q_d)/(mean60daily_volume+q_d)) | 5/60 previous regular sessions | sum6usable hourly lower bounds, no stub, same share regime; current completed-hour or earlier only | unique-eligible-training-native median; pooled train median/unscaledMAD with documented nonzero fallback |
| 12 T1 | log(C/mean20previous_daily_close) | 20 previous regular sessions | >=19 valid,maxgap2; current completed-hour or earlier only | unique-eligible-training-native median; pooled train median/unscaledMAD with documented nonzero fallback |
| 13 T2 | mean20(sign(previous daily logreturns)) | 20 previous regular sessions | >=19 valid,maxgap2; bounded identity; current completed-hour or earlier only | neutral0; identity |
| 14 T3 | (EMA6-EMA18)/C | >=360usable hourly updates and69/72recent,maxgap2 | gap>=3 resets; COP resets; current completed-hour or earlier only | unique-eligible-training-native median; pooled train median/unscaledMAD with documented nonzero fallback |
| 15 T4 | (EMA24-EMA72)/C | same as T3 | price invariant; current completed-hour or earlier only | unique-eligible-training-native median; pooled train median/unscaledMAD with documented nonzero fallback |
| 16 T5 | (WilderRSI14-50)/50 | 14seed changes+140updates | gap disconnects predecessor;gap>=3 resets;neutral0 if missing; current completed-hour or earlier only | neutral0; identity |

For feature calculation only, an ABSENT minute contributes0 to volume. This is not evidence of no trades. Observed sums remain lower bounds; measured zeros, absent assumptions and unknown conflict/quarantine volumes have distinct flags. An hourly volume is usable only with at least one genuine minute, <=5 total absent minutes, longest gap<=5, no conflicting, quarantined or invalid minute. Sensitivities0/1/2/5 are reported without changing the declared threshold. Severe hours remain indexed and their volume channels missing.

Q1 uses previous20matching slots (>=19 valid,maxgap2). Q2 uses previous5/60regular sessions (5/5 and57/60,maxgap2); a daily volume requires all6full-hour sums to meet the tier, excludes the closing stub and remains a six-hour lower bound, never verified full-day exchange volume. No inverse split share-volume multiplier is applied. Matching histories must remain in one volume_basis_id regime; ratios reset at split share-unit changes. Pseudocounts are1% of positive unique training medians separately by stock and compatible share regime; an unseen/unfitted regime stays missing and receives the documented feature fallback.

Prices use only P019B bounded cap5 causal input closes. Genuine opening minutes are required for M1; independently observed trustworthy range is required for B1/B2. Partial ranges are observed ranges with extrema_complete=false, not certified complete-hour extrema. A proxy outside that observed range makes B2 missing, not clipped. Genuine15:30 last-full-hour closes on ordinary6hour sessions are independent prior-day close surrogates, not16:00 exchange closes. No stale earlier-hour or external daily close is substituted.

For each historical step, M2 is session-locked to strictly prior regular sessions with already matured genuine same-origin4h outcomes. The forecast origin1/2 selects its history across all48steps; two small M2 contexts accompany15shared hourly channels, preserving the established16-channel tensor without storing overlapping windows.

Invalid closes freeze EMA and disconnect the RSI predecessor; >=3consecutive invalid scheduled full-hour positions or a COP price-basis change reset state. Regular overnight closure is expected calendar progression, not an outage. T3/T4 require>=360usable updates and69/72recent valid closes,maxgap2. RSI requires14seed changes+140Wilder updates. All16 features are dimensionless and invariant to uniform future split-unit rescaling; independent multiplier7 and prefix tests passed with fixed fitting recipe.

Native nonfinite values remain missing in stored components. For fixed-width model input, use native training medians for13unbounded channels and explicitly neutral0 for B2/T2/T5. Fit on the union of eligible training history keys, prefix-clipped, with no duplicated overlapping windows. M2 uses unique stock/session/origin keys and50/50origin mass. Fit separate inner/refit recipes. Scale13channels by pooled train median/unscaledMAD, then IQR/1.349, populationSD, or scale1 for an exact constant if needed. B2/T2/T5 remain native identity; there is no clipping, asinh input mapping or extra17th model channel. Full reason masks remain separate from inputs. Prefix-only recomputation reproduced every floor, pseudocount, scaler and fallback; no development fitting.

| Input category | Computational action | Retained evidence |
| --- | --- | --- |
| Genuine price/volume | Use valid observation | source row/hash, genuine endpoints, completeness |
| Bounded price proxy | Input-close continuity only | proxy count/age, never target |
| Absent minute volume | Assume0 only for small-gap feature tier | observed=false, lower bound, missing_assumed_zero=true |
| Conflicting source row | No arbitrary selection or zero | volume unknown, field/dependency masks |
| Material anomaly | P019B local exclusion | 18minutes/14bins and causal masks |
| Split share regime | Reset volume history; never invented conversion | volume_basis_id and reset reason |
| True missing/long gap | Native missing then permitted train fallback; no price-window repair | indexed gaps and channel fallback mask |

Reference implementations were reviewed as mathematics only: hf20_features.py, hf20_transforms.py, stock_features.py and ft0_transforms.py. No prior dataset or fitted values were loaded. This new version intentionally adapts minute-quality volume tiers, channel fallbacks, share-regime resets and severe indicator gaps. It preserves16economic channel meanings and the prior approved independent15:30surrogate policy.

Independent scalar source examples cover all16channels at three real dates/stocks (48checks), with operands retained privately. Prefix checks cover2011startup, COP2012,2020halt period and2024; a November2015 real example follows DST. Protected synthetic rows fail before computation. Original source future/stub perturbation leaves earlier48step features unchanged. Real arithmetic operands: independent_oracle_and_causality.json links the private Parquet.

Exact fit values and populations: train_only_fit_recipes.json. Native availability, fallback runs and volume/proxy reliance: feature_missingness_stock_year.csv and source_channel_reason_rates_stock_year.csv. Train distributions/outliers/constants: feature_distributions_train_unique.csv; drift: feature_drift_train_vs_development.csv. Training input/target Spearman diagnostics are descriptive only and do not select features. No channel was dropped.
