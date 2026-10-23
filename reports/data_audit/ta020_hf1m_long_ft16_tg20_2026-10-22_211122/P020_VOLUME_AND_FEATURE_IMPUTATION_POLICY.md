# P020 volume and feature imputation

**FEATURE_READY_FOR_TRAINING. Dataset preparation only; neural training is not authorized.**

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

Source-wide minute assumptions in this permissible numeric span: 271188 absent minutes; 283 conflict/quarantine/invalid minutes remain unknown. These include startup history and are not all admitted training observations. No complete48hour all20volume tape is claimed. See volume_quality_stock_year.csv, volume_threshold_sensitivity_stock_year.csv and source_channel_reason_rates_stock_year.csv.
