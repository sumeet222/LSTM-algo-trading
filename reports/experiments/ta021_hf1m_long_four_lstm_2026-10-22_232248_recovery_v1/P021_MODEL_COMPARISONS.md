# P021 model comparisons

**Exploratory development: 183 origins ×20 stocks, 109 equal-weight sessions.**

| run_id | mse | mae | rmse | zero_mse | excess_mse | daily_ic_mean | sign_hit | top4_recall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HF1M-LONG-TM0-C0-S42-DEV1 | 3.112566351 | 1.240969108 | 1.764246681 | 3.11656044 | -0.003994088353 | 0.04031797049 | 0.4958715596 | 0.2717889908 |
| HF1M-LONG-TM0-T2-S42-DEV1 | 3.106560016 | 1.238970854 | 1.762543621 | 3.11656044 | -0.01000042395 | 0.07555944626 | 0.5105504587 | 0.2591743119 |
| HF1M-LONG-TM0-C0-S123-DEV1 | 3.11725688 | 1.241638655 | 1.76557551 | 3.11656044 | 0.0006964405074 | 0.01437370406 | 0.505733945 | 0.253440367 |
| HF1M-LONG-TM0-T2-S123-DEV1 | 3.114912253 | 1.240476659 | 1.764911401 | 3.11656044 | -0.001648186772 | 0.02549299694 | 0.5107798165 | 0.246559633 |

T2 has slightly lower development MSE than matched C0 for both seeds. Gains over ZERO are small; seed dependence and109 days prevent a confirmatory significance or trading-alpha claim. No configuration was promoted or further fit authorized from these results.

All permitted roles, kept separate:

| run_id | partition | rows | sessions | mse | zero_mse | daily_ic_mean |
| --- | --- | --- | --- | --- | --- | --- |
| HF1M-LONG-TM0-C0-S42-DEV1 | inner_train | 88560 | 2513 | 4.152025419 | 4.156866646 | 0.02808633895 |
| HF1M-LONG-TM0-C0-S42-DEV1 | inner_validation | 15320 | 459 | 3.658381291 | 3.653762776 | -0.007002155531 |
| HF1M-LONG-TM0-C0-S42-DEV1 | refit | 104200 | 2980 | 4.065076281 | 4.069544431 | 0.02424118774 |
| HF1M-LONG-TM0-C0-S42-DEV1 | development | 3660 | 109 | 3.112566351 | 3.11656044 | 0.04031797049 |
| HF1M-LONG-TM0-T2-S42-DEV1 | inner_train | 88560 | 2513 | 4.141503593 | 4.156866646 | 0.06869564222 |
| HF1M-LONG-TM0-T2-S42-DEV1 | inner_validation | 15320 | 459 | 3.652177634 | 3.653762776 | 0.01511319346 |
| HF1M-LONG-TM0-T2-S42-DEV1 | refit | 104200 | 2980 | 4.055393999 | 4.069544431 | 0.06817597297 |
| HF1M-LONG-TM0-T2-S42-DEV1 | development | 3660 | 109 | 3.106560016 | 3.11656044 | 0.07555944626 |
| HF1M-LONG-TM0-C0-S123-DEV1 | inner_train | 88560 | 2513 | 4.151608294 | 4.156866646 | 0.02311007044 |
| HF1M-LONG-TM0-C0-S123-DEV1 | inner_validation | 15320 | 459 | 3.658193662 | 3.653762776 | 0.005935012491 |
| HF1M-LONG-TM0-C0-S123-DEV1 | refit | 104200 | 2980 | 4.064984203 | 4.069544431 | 0.01994315322 |
| HF1M-LONG-TM0-C0-S123-DEV1 | development | 3660 | 109 | 3.11725688 | 3.11656044 | 0.01437370406 |
| HF1M-LONG-TM0-T2-S123-DEV1 | inner_train | 88560 | 2513 | 4.152673657 | 4.156866646 | 0.03049865121 |
| HF1M-LONG-TM0-T2-S123-DEV1 | inner_validation | 15320 | 459 | 3.655665085 | 3.653762776 | 0.004502514903 |
| HF1M-LONG-TM0-T2-S123-DEV1 | refit | 104200 | 2980 | 4.066120849 | 4.069544431 | 0.02710550086 |
| HF1M-LONG-TM0-T2-S123-DEV1 | development | 3660 | 109 | 3.114912253 | 3.11656044 | 0.02549299694 |

`metrics.csv` includes original-scale distributions, errors, IC/direction/top4, tail precision/recall and matched ZERO. Original64 source targets are scored against float32-network predictions; selection uses the frozen float32 engine, so last-bit differences from selected-epoch logs are expected. C0 objective TG20² and T2 objective z² are displayed separately.

ZERO decomposition uses identical weights: MSE(pred)−MSE(0)=E[pred²]−2E[y·pred]. Independent NumPy weights and pandas day/origin/stock reductions agree within1e-10. Every saved T2 raw output reconstructs its canonical prediction once; every source TG20 reconstructs from genuine endpoint prices and all20 returns.

Spearman uses average ranks across20 stocks per origin, then averages origins within each day and days equally. ZERO IC is undefined; plotted0 is only a reference. Sign hit is exact equality of negative/zero/positive classes. Top/bottom4 boundary ties use canonical stock order. `paired_comparisons.csv` contains four matched exploratory contrasts per role; dependent origins and two seeds are disclosed.

Private diagnostics contain every row and stock/month/year/tail/volume/proxy group, origin and daily IC/top4 series. `mse_by_target_magnitude_bins.csv` adds fixed display bins; `tail_error_concentration.csv` uses original full-population weights. All predictions retain run/seed/arm/phase/fit/checkpoint provenance. Overlapping calibration/refit dates are never pooled as independent OOS observations.

Five-stock Alpaca FT0/TG0 and former Twelve Data HF20 FT1/TG20 have different sources, universes, dates and versions. Only within-study matched comparisons are controlled here. No exact-source audited execution/cost engine exists, so trading P&L is UNAVAILABLE.
