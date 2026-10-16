# HF20 hourly-native methodology — approved v2

Identifiers: CAND:HF_TWELVEDATA20:HOURLY_NATIVE:DATASET:v2; FT1_HF20_HOURLY_NATIVE_V2; TG20_HF20_CROSS_SECTIONAL_V1; HF20_COMPLETED_VENDOR_HOUR_CLOSE_PROXY_V1. See the exact configs and live approval transcripts. All source/action/publication/rights limitations remain attached to this version.

Use the fixed ordered 20 stocks and chronology in cohort_and_chronology.json. Ordinary-session origins are completed-hour cutoffs 10:30/11:30 ET, issuance 10:32/11:32, entry close references 10:30/11:30, exit close references 14:30/15:30, maturity 14:32/15:32. There is no trading replay. All four subsequent same-session full hours must be genuine/valid for the label; no overnight horizon. A missing future exit affects the ex-post label mask, never forecast issuance.

A daily **close proxy** is the genuine 15:30 last-full-hour close of the previous ordinary regular session, independently valid if earlier hours are absent. A daily **volume proxy** requires all six complete hours and sums their genuine volumes, omitting the final half-hour tail. Missing volume is never reconstructed. Daily history follows the structural regular-session calendar; no skipping missing observations to obtain a desired count. Early closes supply hourly history only.

|Channel|FT1 rule and causal reference|
|---|---|
|M1|Current log(C/O) / max(trailing RMS60, hourly floor).|
|M2|Mean20 / max(RMS60, M2 floor) of own-stock, same-origin four-hour source returns from strictly earlier structurally eligible sessions; all antecedents matured before each historical feature day. Session-locked by historical day and origin, never today's outcome or TG20.|
|M3|log(previous daily close / daily close six references back) / (sqrt(5) × floored daily RMS63).|
|M4|log(daily proxy close d−21 / d−126) / (sqrt(105) × floored daily RMS63).|
|V1,V2,V3|log floored RMS12; log floored RMS60; their difference. Hourly returns are log(C/O).|
|B1,B2|log(H/L); (2C−H−L)/(H−L), with genuine zero range mapped to B2=0 and preserved source condition.|
|Q1|log((current source-hour volume + stock pseudocount)/(mean previous20 same-scheduled-slot volumes + pseudocount)).|
|Q2|log((mean previous5 regular daily-volume proxies + daily pseudocount)/(mean previous60 + pseudocount)).|
|T1,T2|log(current close / mean previous20 daily-close proxies); mean sign of previous20 daily proxy close-to-close changes.|
|T3,T4|(EMA6−EMA18)/current close; (EMA24−EMA72)/current close. First genuine close seeds, then >=360 valid updates.|
|T5|Wilder RSI14 normalized as (RSI−50)/50; seed14 consecutive genuine closing changes plus140 updates. Missing price freezes state and clears previous close, so recovery creates no false gap-crossing delta. Genuine consecutive overnight endpoints remain legitimate.|

Coverage: RMS12 requires12/12; RMS60 and M2 RMS60 require57/60; M2 mean20 and Q1 require19/20. Daily RMS63 requires60/63; Q2 short5 requires5/5 and long60 requires57/60. SMA20 and sign20 require19/20. All bounded-missing windows reject three consecutive missing scheduled observations. EMA/RSI also require recent69/72 valid closes and max2 consecutive misses. Native input channels B2/T2/T5 remain bounded; the other13 use pooled train-only median/unscaledMAD, fallback IQR/1.349, populationSD, then exact-constant zero with novel-variation flags. No clipping.

Fit floors from the fifth percentile of positive permitted-training volatility observations; hourly floor pools unique RMS12/RMS60 keys. Per-stock volume pseudocounts are1% of positive training median hourly/daily-proxy volume. Canonical daily fitting dates must lie inside the prefix. M2 uses unique stock/day/origin keys and origin weights50/50, not duplicate sliding-window appearances. Other scalers use unique stock/hour/channel keys. Inner fit ends2024-12-24; tail2024-12-26–2025-03-28 is exactly63 exchange sessions. Fresh refit ends2025-03-28. Train transforms are retrospective inside their permitted prefix; evaluation requires the fit to be available at every historical input step, excluding the first16 development origins and16 inner-tail origins.

TG20 uses the complete fixed20 cross-section of log(exit close / entry close), median m and unscaledMAD a. Epsilon=max(1e−4,0.1×median a) on complete, matured structural training origins only, independent of feature readiness. Inner epsilon=0.0003449186163060719 from1,022 origins; refit epsilon=0.00035168796854748245 from1,148. One missing member invalidates the whole cross-sectional label, without changing the forecast issuance mask. No target clipping or deletion based on size; raw returns, centered deviations, MAD/epsilon and maturity are retained separately. No protected-period targets are calculated.

All model inputs require exactly48 consecutive scheduled full-hour positions ×20stocks ×16finite float32 channels. No collecting48 good rows by skipping gaps, stock substitution or zero filling. The source six missing hours remain missing. The approved v2 acceptance is >=85% full training, >=84% inner training, >=90% development and >=100 development sessions; inner validation >=50 sessions and>=25 origins/type. The original90%-training failure remains reported. This is an exploratory source-specific preparation, not FT0 equality, PIT certification, a transferable five-stock checkpoint, or a price-executability claim.
