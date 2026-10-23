# P021 tail and extreme-event audit

Canonical source formula: r_i=log(genuine_exit/genuine_entry); m=median20(r); n_i=r_i−m; rawMAD=median20(|r−m|); TG20=n/(rawMAD+epsilon_fit); z=asinh(TG20/s_fit). Source prices/returns remain in ignored local Parquets.

| fit | epsilon | s | MAD_p05 | abs_numerator_p95 | abs_TG_p99 |
| --- | --- | --- | --- | --- | --- |
| inner | 0.0003297043193 | 0.90640683 | 0.0016793681 | 0.01587214315 | 7.350173695 |
| refit | 0.000334640211 | 0.9057319697 | 0.001704490251 | 0.01599275271 | 7.265029595 |

Large numerator is |n|≥training pooled stock/originp95; small MAD is rawMAD≤training unique-originp05; p99 is |TG20|≥matching trainingp99. Both/neither labels are explicit. Thresholds are retrospective diagnostics, not decision-time information or model/trade rules. Development never fits them.

Four complete private event tables contain88,560/15,320/104,200/3,660 rows by role, including true genuine endpoint prices/flags/source IDs, UTC+ET times, all20 returns (join by origin), median/numerator/rawMAD/epsilon/denominator, TG20/s/z/inverse discrepancy, source proxy/volume/fallback quality and role/fit IDs. Every source decomposition was independently recomputed; no exceptional TG was clipped or repaired. Small-MAD sorting deduplicates origins before pagination, then exposes the full20-name vector.

Real navigation witnesses: TSLA2014-01-14 16:30UTC (largest training numerator); AAPL2013-02-08 16:30UTC (smallest training MAD); TSLA2025-10-23 15:30UTC (C0/42 development largest error, explicitly ex post). See `guide_event_keys.json`; outcomes/operands stay local. Training extremes are selected independently of model performance.

Development p99-tail concentration under original full-population weights:

| run_id | stock_rows | weighted_full_population_loss_share | weighted_full_population_target_square_share |
| --- | --- | --- | --- |
| HF1M-LONG-TM0-C0-S42-DEV1 | 14 | 0.1028776525 | 0.102583445 |
| HF1M-LONG-TM0-T2-S42-DEV1 | 14 | 0.1033100326 | 0.102583445 |
| HF1M-LONG-TM0-C0-S123-DEV1 | 14 | 0.1019584457 | 0.102583445 |
| HF1M-LONG-TM0-T2-S123-DEV1 | 14 | 0.1022513386 | 0.102583445 |

The full CSV includes large-numerator/small-MAD/both/neither and p99/non-p99 groups. Rare-event precision/recall and counts are in metrics.csv; undefined precision stays unavailable. Fixed |TG20| bins are display groups, not newly tuned thresholds.

Independent feature display checks cover14 cases across both fits (proxy prices, absent-minute volume zeros, Q1/Q2 fallback, quarantine, COP dependency and share-basis reset). A separate AAPL2018-01-02 scalar replay reconciles all16 finite native formulas, plus actual saved scaling coefficients. Two additional channels unavailable in the TSLA witness remain truthful native-missing/fallback values, not invented operands.
