# P021 final human review

**Four fixed candidate LSTM pairs completed; research ledger36/200.** Source: pinned `mito0o852/OHLCV-1m`, revision `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`, P020 FT16/TG20/model-input contract `7adfec916b7eb74fead83ef1fe6082ff0fcee9ff0b6ebae5722077e2a82c01a5`. All20 stocks and frozen partitions retained.

| Run | Cal/refit epochs | Cal/refit steps | Dev MSE | Daily IC |
|---|---|---|---|---|
| HF1M-LONG-TM0-C0-S42-DEV1 | 12/1 | 1896/187 | 3.112566 | 0.0403 |
| HF1M-LONG-TM0-T2-S42-DEV1 | 17/7 | 2686/1309 | 3.106560 | 0.0756 |
| HF1M-LONG-TM0-C0-S123-DEV1 | 12/1 | 1896/187 | 3.117257 | 0.0144 |
| HF1M-LONG-TM0-T2-S123-DEV1 | 12/1 | 1896/187 | 3.114912 | 0.0255 |

Total: **10,244 optimizer steps**,53 calibration epochs and10 fresh-refit epochs. Eight distinct checkpoint tensor states; exact reload predictions. Complete canonical exports:846,960 run/phase/stock rows across the four separately labeled roles; overlapping calibration/refit dates are never pooled.

Development is183 origins over109 sessions. Matched ZERO MSE=3.116560. T2 modestly lowers MSE versus C0 in both seeds, with small ZERO gains. Predictions remain near zero; ranking/top4 behavior varies by seed. Reduced T2 clipping is observed, not a proven cause of performance. Two seeds provide exploratory evidence, not confirmatory significance or trading alpha.

The original C0/42 export failure remains charged at33. Live-approved continuation reused its selected calibration checkpoint with no calibration replay, performed its selected one-epoch fresh refit, then started only the three remaining models. All12 original calibration epoch summaries survived; per-batch calibration rows did not and remain unavailable.

The existing dashboard now includes all20-stock history, genuine hourly OHLC/volume/quality,16 native/scaled channels and operands, full training/development targets, extremes, four-run training/clipping, forecast/residual/scatter/bin/IC-heatmap panels, ZERO and matched seed/arm comparisons. Start at the sidebar HF1M Long entry; `P021_DASHBOARD_USER_GUIDE.md` contains genuine examples.

Checks:32 focused integration tests passed; legacy32 plus its sandbox port test passed natively; Ruff clean;304 project Python files,0 errors/0 warnings. Launcher check and native smoke passed. All1,701 active source files and P019B/P020 inventories rehashed unchanged. **2026 numerical confirmation remains locked.**

Remaining limitations: reported private-use rights, source publication/action/dividend/volume-basis and execution assumptions; fixed-cohort survivorship; lost original per-batch calibration telemetry; original failed-process peak RSS unavailable. No P&L or final-test result. Editor Problems refresh remains human-confirmed. All changes are uncommitted; no Git staging/commit/push/integration.
