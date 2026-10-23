# Inspect the HF1M Long research study in 5–10 minutes

If the dashboard is already running, open http://localhost:8501. Otherwise use
`./scripts/run_track_a_dashboard.sh` from the repository root with its documented.venv.
Open **HF1M Long — 20 stocks (2010–2025)** in the sidebar, or its **Start Here** button.
This study uses only pinned Hugging Face minute-derived hourly FT16/TG20 data. It never pools
older Alpaca or Twelve Data observations, fitted recipes, models or result populations.

1. Open **Training Data / Targets & Extremes**. Keep **Full-prefix refit training** and **All**stocks.
   Select **Largest |numerator|**. A real starting example is **TSLA / 2014-01-14T16:30:00+00:00**.
   Search that exact origin, select its durable ticker/origin key and inspect the numeric operands.
2. Change to **Smallest raw MAD**. A distinct real example is **AAPL / 2013-02-08T16:30:00+00:00**.
   This mode ranks each origin once; its expanded table still shows all 20 stocks' future returns.
   Filters and sorting cover all 104,200 refit stock rows before50-row pagination. No first30-row cap.
3. Read genuine entry and exit prices, UTC/ET clocks, r, contemporaneous20-name median m,
   signed numerator n=r−m, raw MAD, train-fitted epsilon and TG20=n/(MAD+epsilon).
   Large numerator means |n|≥training p95; small MAD means originMAD≤training p05.
   The both/neither categories and targetp99 use the matching training prefix, never development.
4. Follow the blue48-hour input shading and the separate orange future 4-hour outcome region.
   The exact 48×16 model matrix excludes every future outcome step. Native missingness and
   source-proxy/fallback flags remain visible; a fallback never admits a banned origin.
5. Choose **M1**, **Q1**, **Q2**, or any of the 16 channels in **FT16 channels**. Native and
   model-normalized values use separate synchronized plots with correct dimensionless axes.
   Open the formula dictionary, per-step coefficient table and stock/phase-specific floors.
   **Reconstruct source operands at this step** shows independent scalar source replay.
   M1 is completed-hour log(C/O)/max(RMS60,h), not the cross-sectional target median.
   There is no invented MST channel. FeatureT2 and the target-transformation armT2 are distinct.
6. Press **Open this event in Complete History**. All 20 tickers and every permitted month from
   July 2010 through December 2025 are browsable; the display window is bounded to 93 days.
   Use **Jump to day / week / month → Apply history jump**, or **History dates (ET)**.
   Candles distinguish missing wicks, input proxies, quarantines and closing stubs. Volume bars
   show as-reported observed shares; feature markers are lower bounds with small absent-minute
   zeros, never fabricated measured volume. Select any source hour for exact OHLCV/quality detail.
   For a split/reset example browse **AVGO / July 12–16, 2024**; for a COP basis guard browse
   **COP / May 1, 2012**; for warmup quarantine detail browse **AAPL / August 31, 2010**.
   Warmup and other non-admitted hours show truthful unavailable native features and no invented labels.
7. Open **Training Diagnostics**. Keep all 4 runs to compare C0/T2 within each seed and seeds42/123
   within each arm. Calibration and fresh refit are separate. Compare originalTG20 losses across
   arms; C0 objective is TG20² and T2 objective is z², so their objective magnitudes are separate.
   Inspect selected versus raw-best versus stopping epochs and all actual late-epoch gradients,
   with preclip cap 1 and clipping fractions over optimizer steps. The original C0/42 export failure
   and lost per-batch calibration telemetry remain disclosed; its 12 epoch summaries survived.
8. Open **Predictions / Errors / Comparisons**, default **Exploratory development**. A genuine
   C0/42 largest-error example is **TSLA / 2025-10-23T15:30:00+00:00**. Return to the target explorer,
   choose development and search that origin to inspect its price/target/input operands and all runs.
   Compare matched ZERO, original-scale MSE/MAE, prediction dispersion, daily 20-stock SpearmanIC,
   top-4 recall, tail/group errors and the exact identity MSE−MSE(ZERO)=E[p²]−2E[yp].
   ZERO rankIC is undefined; a plotted 0 line is a reference. Filtered metrics are separately labeled
   and reweighted; complete-population metrics remain above. Two seeds do not establish significance.
9. Open **Feature / Source QA** for actual Q1/Q2 fallback rates, stock/year volume/proxy/missingness,
   share-basis resets, admission waterfall and approved saved descriptive correlations.
   These are not feature-importance fits. Read the source/anomaly register for remaining limitations.

The forward target transformation is **z=asinh(TG20/s_phase)**. The inverse is
**TG20_pred=s_phase*sinh(z_pred)**, applied exactly once before original-scale comparisons.
The saved inner/refit recipes, floors, pseudocounts and epsilon/s values are displayed at full precision.
They are training-prefix retrospective transforms, not assertions of real-time availability in warmup.

The fitting prefix is 14 years 3 months, preceded by nine months of warmup. Inner validation selects
checkpoints; full-prefix refit training includes those historical validation dates. Only development
is a time-separated post-fit assessment here, and it remains exploratory. Protected January–March 2026
numeric candles/features/labels/predictions are unavailable in every view, cache and date/role path.
Source rights remain reported private research permission. Publication timing, dividend/action vintage,
price-reference execution and tradability are not independently certified. No trading P&L is fabricated.

Experiment, approval, failure/continuation history and review artifacts:
`reports/experiments/ta021_hf1m_long_four_lstm_2026-10-22_232248_recovery_v1`. Reproduce only with legitimate exact private stores and documented manifests; no bulk data
or checkpoint sharing is implied. The standard launcher remains the single local dashboard entrypoint.

Additional exact prediction controls: choose **Forecast detail stock** for all-four forecast versus actual time series. The selected **Inspect prediction run** supplies the signed-residual time series and prediction/actual scatter with its identity line. Daily IC and monthly IC heatmaps appear side by side. Fixed |TG20| MSE bins compare matched ZERO; error results are sorted on the full filtered population before50-row pagination. **All-name input-context quality** filters targets by past proxy/volume quality. Source QA includes stock/year terminal input-price ages.
