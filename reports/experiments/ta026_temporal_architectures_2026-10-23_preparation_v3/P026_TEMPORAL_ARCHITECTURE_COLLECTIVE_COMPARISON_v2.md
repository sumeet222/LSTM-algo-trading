# P026 temporal architectures — completed scientific comparison

All three implementations passed. This one-seed architectural screen does **not establish an improvement over saved T2/42**. Attention has a tiny joint positive point estimate with all primary sensitivity intervals spanning zero. Multiscale has negative joint point estimates with intervals spanning zero. GRU32 has worse MSE and IC with one/two-month sensitivity intervals consistently in the unfavorable direction. These are exploratory reused-development observations, not corrected p-values or independent confirmation.

## Controlled outcome

| arm | MSE | MAE | RMSE | daily_IC | origin_IC | prediction_SD | z_MSE |
|---|---|---|---|---|---|---|---|
| A1 | 3.1063 | 1.23898 | 1.76247 | 0.075801 | 0.0614892 | 0.0497437 | 1.28096 |
| A2 | 3.10866 | 1.23934 | 1.76314 | 0.0595961 | 0.0548858 | 0.0480931 | 1.28276 |
| A3 | 3.11474 | 1.24128 | 1.76486 | 0.012118 | 0.0129617 | 0.0348634 | 1.28743 |


| model | MSE | daily_IC | prediction_SD |
|---|---|---|---|
| T2/42 | 3.10656 | 0.0755594 | 0.0488872 |
| T2/123 | 3.11491 | 0.025493 | 0.0349004 |
| ZERO | 3.11656 | undefined | 0 |


| arm | delta | high | low | metric | months |
|---|---|---|---|---|---|
| A1 | -0.000257931 | 8.73538e-05 | -0.000559523 | mse | 1 |
| A1 | 0.00024151 | 0.002583 | -0.00245174 | ic | 1 |
| A1 | -0.000257931 | 7.10573e-05 | -0.000501336 | mse | 2 |
| A1 | 0.00024151 | 0.0036053 | -0.00415873 | ic | 2 |
| A2 | 0.00209625 | 0.00607871 | -0.00103837 | mse | 1 |
| A2 | -0.0159633 | 0.00880443 | -0.0417252 | ic | 1 |
| A2 | 0.00209625 | 0.00653514 | -0.00251159 | mse | 2 |
| A2 | -0.0159633 | 0.000371821 | -0.0311041 | ic | 2 |
| A3 | 0.00818003 | 0.0134212 | 0.00189656 | mse | 1 |
| A3 | -0.0634414 | -0.0351072 | -0.0869367 | ic | 1 |
| A3 | 0.00818003 | 0.0134061 | 0.0031341 | mse | 2 |
| A3 | -0.0634414 | -0.0532211 | -0.0767112 | ic | 2 |


Deltas are candidate minus T2/42: lower MSE/higher IC is better. Each interval uses400 seed22042 intact-calendar-month or two-month block resamples with daily IC recomputed at its proper level. Development is183 origins/3,660 rows/109 sessions after the frozen embargo. A1 MSE improves by approximately0.0083% relative to T2/42; this is too small and uncertain to support the mechanism hypothesis. No automatic model promotion or follow-on search follows.

## Complete fitting and four-role evidence

| arm | start | parameters | selected | raw_best | stopped | optimizer_steps | fit_seconds | gate_RSS_bytes |
|---|---|---|---|---|---|---|---|---|
| A1 | 54 | 6466 | 7 | 7 | 17 | 3995 | 244.176 | 989970432 |
| A2 | 55 | 7217 | 7 | 7 | 17 | 3995 | 271.223 | 989970432 |
| A3 | 56 | 4833 | 3 | 6 | 13 | 2615 | 147.975 | 1006354432 |


| MAE | MSE | RMSE | SD_ratio | abs95_recall | abs99_recall | arm | bottom4 | calibration_slope | daily_IC | origin_IC | prediction_SD | role | sign_hit | top4 | z_MSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.29811 | 4.14159 | 2.03509 | 0.0261368 | 0 | 0 | A1 | 0.255173 | 3.17942 | 0.0679147 | 0.0665703 | 0.0532862 | inner_train | 0.519459 | 0.238758 | 1.32784 |
| 1.27071 | 3.65215 | 1.91106 | 0.0263016 | 0 | 0 | A1 | 0.221405 | 0.818991 | 0.0140402 | 0.0154893 | 0.050275 | inner_validation | 0.5122 | 0.218137 | 1.31286 |
| 1.29208 | 4.05507 | 2.01372 | 0.0265699 | 0 | 0 | A1 | 0.263926 | 3.04007 | 0.0681036 | 0.0683668 | 0.0535979 | refit | 0.520998 | 0.224077 | 1.32394 |
| 1.23898 | 3.1063 | 1.76247 | 0.0281776 | 0 | 0 | A1 | 0.271789 | 2.56153 | 0.075801 | 0.0614892 | 0.0497437 | development | 0.511009 | 0.264908 | 1.28096 |
| 1.29788 | 4.1411 | 2.03497 | 0.0280436 | 0 | 0 | A2 | 0.261242 | 2.93154 | 0.0714076 | 0.0695176 | 0.0571736 | inner_train | 0.52306 | 0.234481 | 1.32743 |
| 1.27069 | 3.6509 | 1.91073 | 0.0283223 | 0 | 0 | A2 | 0.227669 | 0.990834 | 0.0164947 | 0.017683 | 0.0541376 | inner_validation | 0.507571 | 0.212418 | 1.3128 |
| 1.29207 | 4.05602 | 2.01396 | 0.0261585 | 0 | 0 | A2 | 0.263129 | 2.96244 | 0.0693395 | 0.068504 | 0.052768 | refit | 0.51953 | 0.225419 | 1.3241 |
| 1.23934 | 3.10866 | 1.76314 | 0.0272426 | 0 | 0 | A2 | 0.25 | 2.19656 | 0.0595961 | 0.0548858 | 0.0480931 | development | 0.509174 | 0.268349 | 1.28276 |
| 1.29918 | 4.14821 | 2.03672 | 0.0198262 | 0 | 0 | A3 | 0.215678 | 3.13945 | 0.0452136 | 0.0423752 | 0.0404204 | inner_train | 0.510237 | 0.257312 | 1.33144 |
| 1.27084 | 3.65495 | 1.91179 | 0.0240474 | 0 | 0 | A3 | 0.191176 | 0.219216 | 0.0044738 | 0.00133406 | 0.0459661 | inner_validation | 0.504739 | 0.236656 | 1.31376 |
| 1.29298 | 4.06286 | 2.01565 | 0.0179953 | 0 | 0 | A3 | 0.242659 | 3.1514 | 0.0514207 | 0.0510174 | 0.0363007 | refit | 0.514673 | 0.227685 | 1.32751 |
| 1.24128 | 3.11474 | 1.76486 | 0.0197486 | 0 | 0 | A3 | 0.208716 | 1.22631 | 0.012118 | 0.0129617 | 0.0348634 | development | 0.49633 | 0.224771 | 1.28743 |


The original strict D6g rule is loss<.999*qualifying_best, min12/max60/patience10. A3's raw minimum was epoch6 but did not qualify beyond epoch3. Fresh refits used7/7/3 epochs from original seed42 initialization and empty AdamW; no calibrated weights or calibration scalers were transferred. AdamW lr.001, betas(.9,.999), eps1e-8, matrix/query decay.01, bias/gamma decay0, head dropout.1, gradient cap1,16 whole sessions remain frozen. Original-scale MSE selects epochs; transformed z-MSE is the training objective. Four-role targets/populations and once-only inverse were independently replayed, with zero protected numeric reads.

## Gradients, capacity and cost

| arm | clip_fraction | phase | postclip_max | preclip_max | preclip_mean | preclip_p50 | preclip_p90 | preclip_p99 | steps |
|---|---|---|---|---|---|---|---|---|---|
| A1 | 0.00372301 | calibration | 1 | 1.7066 | 0.28691 | 0.270019 | 0.400464 | 0.55696 | 2686 |
| A1 | 0 | refit | 0.614021 | 0.614022 | 0.222118 | 0.211563 | 0.297138 | 0.393954 | 1309 |
| A2 | 0.00483991 | calibration | 0.999999 | 2.01994 | 0.303524 | 0.286277 | 0.416388 | 0.565265 | 2686 |
| A2 | 0 | refit | 0.590996 | 0.590996 | 0.227103 | 0.217399 | 0.296304 | 0.417928 | 1309 |
| A3 | 0.00681597 | calibration | 1 | 2.61848 | 0.424128 | 0.398209 | 0.573163 | 0.877663 | 2054 |
| A3 | 0.00356506 | refit | 0.999999 | 1.29865 | 0.456249 | 0.434808 | 0.619295 | 0.824005 | 561 |


All updates/weights/outputs are finite. Parameter-level gradients, pre/postclip distributions, gamma/query trajectory and model/optimizer/RNG identities remain in immutable per-epoch receipts and updates.jsonl. Finite hidden/input gradients alone cannot prove absence of vanishing gradients.

| model | parameters | parameter_bytes | stock_sequences | median_seconds | p90_seconds |
|---|---|---|---|---|---|
| T2/42 | 6433 | 25732 | 320 | 0.0122821 | 0.0127786 |
| A1 | 6466 | 25864 | 320 | 0.0117311 | 0.0120358 |
| A2 | 7217 | 28868 | 320 | 0.0160297 | 0.0172775 |
| A3 | 4833 | 19332 | 320 | 0.00672829 | 0.00701361 |


This inference diagnostic uses the same320 stock sequences (16 permitted development origins), CPU4, three warmups and20 forward-only repetitions, loading/export excluded. No optimizer was instantiated for this diagnostic and AdamW.step was blocked;0 extra starts. Saved T2/42's original full lifecycle took410.814 seconds, versus244.176/271.223/147.975 seconds here. Historical executor/export instrumentation and GRU's fewer selected epochs differ, so those whole-lifecycle times are not a causal speed benchmark. GRU has24.87% fewer parameters than TM0; A1 adds33 and A2 adds784. The inference timings are machine-specific, not a portability guarantee.

## Mechanism and event falsification

A1 gamma=-0.032128755, query norm=.38231003. In the **last refit measurement batch**, normalized entropy=.99945021 and effective lookback47.898/48; the stock/day lag tables cover the full104,200-row refit population. The learned residual is active but nearly uniform attention and recent-window perturbation sensitivity do not establish recovery of lost temporal information. Last-batch readout change RMS is.0016651 z units; this compares the same A1 encoder's final-state head, not an untouched T2 encoder. The saved T2 forecast comparison is separately matched above.

A2 window1/4/12 coefficient norms are4.055995/.592486/.587185 and signal RMS1.400079/.178792/.174714 on eight frozen origins. All three branches have finite nonzero input/readout gradients, and suffix/prefix causality checks pass. The16-dimensional mixed input uses the identical48 steps. Active extra branches did not improve the primary development comparison; they may duplicate engineered horizon information. Learned weights are not causal horizon attribution.

A3 has4,833 parameters. True native GRU update/reset gates were not instrumented and are not reported. Full-refit hidden summaries plus eight-origin BPTT/early-middle-recent perturbations are preserved. Recent-window ablation changes outputs most, while neither hidden magnitudes nor this diagnostic can isolate gating, capacity, initialization and optimization causes. Its negative primary comparison gives no support for replacing TM0 in this screen.

| arm | SD_ratio | sign_hit | top4 | bottom4 | calibration_slope | abs95_recall | abs99_recall |
|---|---|---|---|---|---|---|---|
| A1 | 0.0281776 | 0.511009 | 0.264908 | 0.271789 | 2.56153 | 0 | 0 |
| A2 | 0.0272426 | 0.509174 | 0.268349 | 0.25 | 2.19656 | 0 | 0 |
| A3 | 0.0197486 | 0.49633 | 0.224771 | 0.208716 | 1.22631 | 0 | 0 |


All three have zero absolute95%/99% event recall with genuine refit-derived thresholds3.8853028735/7.2650295954 and strict exceedance. Development contains153/14 absolute events; positive/negative directions and conditional tail MSE remain separate in role metrics. Top/bottom4 retrieval is rank based and can improve while absolute-event recall stays zero. Output SD is only about2.82%/2.72%/1.97% of target SD; no amplitude correction was applied. Calibration slope is descriptive, not a fitted output repair.

## Stability and source context

| arm | dimension | value | rows | origins | sessions | MSE | T2_MSE | delta_MSE |
|---|---|---|---|---|---|---|---|---|
| A1 | month | 2025-07 | 380 | 19 | 11 | 3.07249 | 3.07264 | -0.000150069 |
| A1 | month | 2025-08 | 620 | 31 | 21 | 2.98984 | 2.99052 | -0.000685333 |
| A1 | month | 2025-09 | 640 | 32 | 19 | 3.01802 | 3.01861 | -0.000587162 |
| A1 | month | 2025-10 | 640 | 32 | 20 | 3.61441 | 3.61459 | -0.000180792 |
| A1 | month | 2025-11 | 680 | 34 | 18 | 2.66775 | 2.66714 | 0.000604914 |
| A1 | month | 2025-12 | 700 | 35 | 20 | 3.21764 | 3.21805 | -0.000409414 |
| A2 | month | 2025-07 | 380 | 19 | 11 | 3.07006 | 3.07264 | -0.00257585 |
| A2 | month | 2025-08 | 620 | 31 | 21 | 2.98804 | 2.99052 | -0.00247793 |
| A2 | month | 2025-09 | 640 | 32 | 19 | 3.02144 | 3.01861 | 0.00283147 |
| A2 | month | 2025-10 | 640 | 32 | 20 | 3.62465 | 3.61459 | 0.0100536 |
| A2 | month | 2025-11 | 680 | 34 | 18 | 2.66726 | 2.66714 | 0.000116074 |
| A2 | month | 2025-12 | 700 | 35 | 20 | 3.22065 | 3.21805 | 0.00259515 |
| A3 | month | 2025-07 | 380 | 19 | 11 | 3.07055 | 3.07264 | -0.00208766 |
| A3 | month | 2025-08 | 620 | 31 | 21 | 3.00351 | 2.99052 | 0.0129835 |
| A3 | month | 2025-09 | 640 | 32 | 19 | 3.02729 | 3.01861 | 0.00868116 |
| A3 | month | 2025-10 | 640 | 32 | 20 | 3.63249 | 3.61459 | 0.0178948 |
| A3 | month | 2025-11 | 680 | 34 | 18 | 2.6753 | 2.66714 | 0.00815433 |
| A3 | month | 2025-12 | 700 | 35 | 20 | 3.21667 | 3.21805 | -0.00138411 |


| arm | dimension | value | rows | origins | sessions | MSE | T2_MSE | delta_MSE |
|---|---|---|---|---|---|---|---|---|
| A1 | V1_state | HIGH | 1216 | 181 | 107 | 5.18226 | 5.18293 | -0.000671445 |
| A1 | V1_state | LOW | 938 | 178 | 108 | 1.59669 | 1.59682 | -0.000123086 |
| A1 | V1_state | MID | 1363 | 183 | 109 | 2.54738 | 2.54742 | -3.64411e-05 |
| A1 | V1_state | MISSING | 143 | 97 | 61 | 1.45092 | 1.45076 | 0.000160716 |
| A1 | quality | FLAGGED | 3660 | 183 | 109 | 3.1063 | 3.10656 | -0.000257931 |
| A2 | V1_state | HIGH | 1216 | 181 | 107 | 5.18744 | 5.18293 | 0.00450983 |
| A2 | V1_state | LOW | 938 | 178 | 108 | 1.59863 | 1.59682 | 0.00181766 |
| A2 | V1_state | MID | 1363 | 183 | 109 | 2.54753 | 2.54742 | 0.000113511 |
| A2 | V1_state | MISSING | 143 | 97 | 61 | 1.45335 | 1.45076 | 0.00259452 |
| A2 | quality | FLAGGED | 3660 | 183 | 109 | 3.10866 | 3.10656 | 0.00209625 |
| A3 | V1_state | HIGH | 1216 | 181 | 107 | 5.2058 | 5.18293 | 0.0228648 |
| A3 | V1_state | LOW | 938 | 178 | 108 | 1.59889 | 1.59682 | 0.00207406 |
| A3 | V1_state | MID | 1363 | 183 | 109 | 2.54753 | 2.54742 | 0.000113783 |
| A3 | V1_state | MISSING | 143 | 97 | 61 | 1.45459 | 1.45076 | 0.00383389 |
| A3 | quality | FLAGGED | 3660 | 183 | 109 | 3.11474 | 3.10656 | 0.00818003 |


All20 stock and static publisher-sector slices are retained in postfit_development_slices.csv and the explorer, including unfavorable slices. V1 cuts use pooled finite fitting-prefix native values only; source-quality and sector labels are retrospective context, never predictors or PIT certification. Per-stock/time associations in heterogeneity.parquet are not origin cross-sectional IC. Month and state sample sizes are small; this screen has three comparisons and a repeatedly reused109-session development period. Walk-forward, null, other seeds, cross-stock/regime designs and protected confirmation remain deferred.

Read [actual-objective loss](P026_OBJECTIVE_SPACE_EXTREME_LOSS.md), [dashboard guide](P026_DASHBOARD_USER_GUIDE.md) and [final review](P026_FINAL_HUMAN_REVIEW.md). v1 reports/manifest remain immutable; this append-only v2 adds interpretation and explicit intervals, event/stability/cost summaries without changing any model or numeric definition.
