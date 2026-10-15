# Track A visualization user guide

Start with [Visualization_Quickstart.md](Visualization_Quickstart.md). Launch from the repository root with `./scripts/run_track_a_dashboard.sh`. The app has six sections and no model-fitting controls. Its real-pair ledger stays24/40. The added **Controlled Experiments** page is explained in [HOW_TO_VISUALLY_INSPECT_PACKAGE_011.md](HOW_TO_VISUALLY_INSPECT_PACKAGE_011.md).

## Controls and coverage

The sidebar always shows stock, fold, model, partition, inclusive ET date range and forecast origins. **Development** means held-out, already explored WF1 or WF2. **Inner validation** shows saved scores from the selected calibration checkpoint. **Refit training** shows in-sample diagnostics from the final fresh-refit checkpoint. Training and validation scores are not outer OOS evidence. Fold/partition changes reset dates to a known recorded range.

| Fold | Development models and references | Fitting prefix |
|---|---|---|
| WF1 | TM0, MC0, MC1, E5, ZERO, M1, RIDGE_OWN_112, RIDGE_MARKET_147 | Through June2023 |
| WF2 | TM0, MC0, ZERO | Through December2023 |

Neural inner-validation/refit-training snapshots are provided where actually saved. Baselines have development snapshots only. No WF2 E5, MC1, momentum or ridge result is invented. Training diagnostics requires a neural model. A missing file or unsupported filter produces an information panel with the reason; other sections remain usable.

## Price & Features

The top chart uses genuine regular-session OHLC, with matching-resolution volume directly below. **30 min source** includes the closing stub, highlighted by gold volume. **Completed hour** uses the existing session-anchored causal builder; an ordinary day has six full hours, an early-close day three, with the terminal half-hour excluded. Missing constituents create a gap, never an inserted candle. Weekends/holidays are not manufactured.

Candles are labeled at interval starts. Feature values are labeled at completed interval ends. The x-axis displays Eastern wall time with DST; hover gives the true UTC key. Linked axes support pan/zoom and hover. Optional overnight/weekend rangebreaks change only display gaps, not source timestamps; holidays/early-close gaps may remain. Linear/log price scale does not change values.

The vendor representation is retrospective split-adjusted price in USD and inverse-split-adjusted share volume. It is not a PIT action record or raw cashbook. AAPL2020 split context gets a visible scale warning. Use the **Inspect candle** selector to see a single bar's fields and source references. No bulk price export is added.

Forecast markers use the approved clocks: cutoff10:30/11:30 ET; future proxy close14:30/15:30; nominal entry10:33/11:33 and exit/maturity14:33/15:33. The latter are idealized model/evaluation events, not observed fills. Early-close origins lacking the complete horizon are omitted. Future label boundaries are explicitly ex-post context.

### FT0 and indicator units

Choose up to four channels, normally one or two. **Native** means the frozen feature transform after applying the selected existing fitted floors. **Scaled** means its actual float32 model-input representation under the bound inner/full-prefix recipe. No normalizer or floor is refitted by plotting. Retrospective historical recipe application is disclosed; plotting a transform does not certify that the model existed historically. Gaps mean unavailable/invalid values and are not interpolated.

| Channels | Meaning |
|---|---|
| M1 | Completed-hour log(C/O) divided by floored RMS60; normalized move, not raw return |
| M2 | Mature previous-origin four-hour-return mean20 / floored RMS60; choose10:30 or11:30 context |
| M3 / M4 | Previous-session5-day momentum / older105-day momentum, daily-volatility normalized |
| V1 / V2 / V3 | Log floored RMS12 / log floored RMS60 / their difference |
| B1 / B2 | Log high/low range / bounded close location |
| Q1 / Q2 | Same-slot relative volume / previous full-session short/long volume ratio with fitted pseudocounts |
| T1 / T2 | Log close/prior20-daily-close SMA / prior20-daily-return sign mean |
| T3 / T4 | (EMA6−EMA18)/close / (EMA24−EMA72)/close; not MACD histogram or signal line |
| T5 | (Wilder RSI14−50)/50, native[−1,1], with frozen warm-up/missing recovery |

All these feature channels use dimensionless lower panels. The optional dollar-price overlay reconstructs the same prior20-daily-close SMA exactly as `completed close / exp(native T1)`, using compatible source prices. T1 itself is never labeled a raw SMA. Individual absolute EMA lines are not recorded in the canonical store and are not invented. No extra VISUAL_ONLY indicator library is added.

Market-conditioned models can display SPY U1–U5 separately, native or scaled: normalized hourly move, absolute log volatility, short/long volatility ratio, previous-session5-day momentum and20-day trend. Their own missing-state/clock status is preserved; missing native observations are not rendered as observed neutral zeros. SPY is an ETF state proxy, not certified course USA500.

## Predictions & Errors

Saved forecasts are loaded without checkpoint inference or optimizer construction. The chart separates scores/realized TG0 from dollar prices. The residual is score minus realized target. **EX-POST OUTCOMES** identifies information unavailable at the original cutoff. M1 is a ranking feature rather than a calibrated TG0 forecast and gets a separate units panel.

Choose another saved neural model or a ZERO/ridge comparator where available. Matching requires identical session/origin/stock keys and identical targets. A mismatch rejects a matched comparison instead of silently selecting favorable rows. The five-stock table gives score, true target, residual, predicted rank, realized rank and rank difference;1 is best. Score sign does not imply positive/negative absolute return.

Summary scope can use visible date/origin filters or the whole recorded partition. MSE averages five stocks per origin, origins within each day, then days equally. Rank IC computes five-stock Spearman midranks per origin, then equal-origin/day means. It is not a one-stock statistic; the app gives stock-specific MSE separately. Constant ZERO has project-conventional IC0, while its defined Spearman is N/A. Counts, tied origins, score dispersion and monthly/origin summaries make the denominator visible.

For E5, optional peer context shows the exact48-step mean and population dispersion of the other four stocks' scaled M1 using the existing peer calculator. MC1's gate panel uses only the21 captured, checkpoint-bound examples from Package008. The selected example may differ from the current chart date and is labeled explicitly. It plots `16 × softmax(W_g m_t + b_g)`, common across stocks; other dates' gate weights are Not recorded. These modulation weights are not validated feature importance. No checkpoint tensor is deserialized by this app.

## Training Diagnostics

Calibration training loss is dropout-on telemetry; inner-validation MSE is dropout-off evaluation. Selection is the frozen best qualifying >0.1% improvement, not necessarily the absolute raw minimum. Refit has its own plot: a fresh model/optimizer with a full-prefix recipe, trained for exactly the selected epoch count. It is not a continuation or second selection.

Both passes preserve norm/clip warnings. Global cap1 is separate from the >50% warning line. The PyTorch multiplier is `min(1,1/(preclip_norm+1e-6))`; G6 cap exceedance uses norm>1. Nonfinite counts are separate. WF1 has epoch aggregates only; its per-batch norms, optimizer histories and dropout masks were not recorded. WF2 TM0/MC0 have actual paired batch loss/norm rows and one row per optimizer step. The scatter color denotes maximum absolute target. Repeated-session batch association does not identify per-example causal responsibility.

The independent **Target / loss partition** defaults to refit training, with optional date/month/origin/stock filters. Histograms offer linear/log counts; percentile filters only select displayed extremes. Quantiles and maximum |TG0| come from actual loaded labels, so the previously observed≈82.03 training tail is shown only for its supporting population. Select an extreme and **Inspect this date's candles** to navigate; these observations are explicitly ex-post.

Optional decomposition uses canonical future log return, cross-sectional median/MAD, the exact fitted epsilon and numerator/denominator. It reconciles with saved TG0 and does not infer raw denominators from normalized targets. Loss concentration retains complete five-stock origins and equal days; the curve accumulates worst-loss sessions first. Top1/5/10% use `ceil(p×N)`. It is not an equity curve or evidence those days caused clipping.

## Provenance, safety and troubleshooting

**Research Notes / Provenance** computes full-fold figures from loaded predictions and reconciles them to bound reports; reference numbers are not hard-coded into charts. It lists source, recipe, checkpoint and prediction hashes from `configs/track_a_visualization_v1.json`. Missing local weights are reported separately from hash-verified saved snapshots. Bound file changes invalidate in-memory caches; changed hashes are rejected. There is no duplicate feature database or disk cache.

Use `./scripts/run_track_a_dashboard.sh --check` for exact missing paths or `--smoke` to start/check/stop localhost. Use `--port 8502`, or `TRACK_A_DASHBOARD_PORT=8502`, if needed. The direct Streamlit command uses the port you specify and does not perform fallback selection. Ctrl+C stops the launching server. No public interface is bound and Streamlit usage statistics are disabled in `.streamlit/config.toml` and the launcher. Keep that config when using the direct command. No `.env`, vendor API or brokerage connection is used.

Dates outside a selected model partition give a friendly timeframe message; select **Refit training** to inspect earlier price/split dates. Confirmation begins July1,2024 ET and is rejected before Arrow numeric reads, including in straddling source files. The interactive source/feature window is limited to94 calendar dates to bound work. For a large-fold metric comparison choose the full recorded summary instead of expanding raw candle reads.

The current package verifies programmatic Streamlit interactions plus real local HTTP/HTML and clean shutdown. Native browser automation was unavailable/unreliable during the session; no screenshot is fabricated or claimed as verified. The researcher should follow the five-minute example for final visual review. Local rights, observed publication and action/PIT assumptions remain qualified; no redistribution or alpha certification follows from a chart. Check applicable rights before sharing screenshots.

Framework API references used: [Streamlit Plotly charts](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart), [in-memory caching](https://docs.streamlit.io/develop/concepts/architecture/caching), [local configuration](https://docs.streamlit.io/develop/api-reference/configuration/config.toml).

## Controlled Experiments and Feature Scaling Explorer

Use **Start Here → Package 011: Compare C0 and T2**, or the new sidebar section. The study has separate treatment/comparator/fold/seed/partition/stock/date/origin controls. TM0 remains the architecture; C0/H1/T1/T2/O1 are treatment arms. Its five views are **Target & denominator**, **Training Curves & Gradients**, **Predictions & Errors**, **Extreme Events**, and **Feature Scaling Explorer**. Follow the linked five-minute guide for exact controls, actual training populations, a verified SBUX November17,2023 outlier and one-click candle navigation.

Target distributions use registered inner/full-refit training labels, independently of the development date filter. Their cap/scale/preparation/population identities are checked; no parameters are fitted. Original TG0, clipped optimizer labels and asinh labels use separate axes. Predictions always read original canonical saved scores, including T2's already applied inverse. Full-epoch training curves ignore stock/date filters; matched prediction/event metrics retain every selected five-stock origin. Recorded loss/gradient units and missing historical telemetry are explicit. Fold×seed intervals are the existing exploratory five-session blocks, not newly sampled significance results.

The Feature Scaling Explorer shows all16 real FT0 channels with their native/scaled traces, distributions and actual fitted parameters. After event navigation, the Price & Features expander can show the exact48-step context from bound components and recipes. No rolling z-score, alternative floor/MAD or other Package012 transform is estimated. Complete raw target/mask/clock matches are required before paired metrics; mismatch states never silently drop rows. New adapter and UI hashes are additive to the visualization config; every sealed Package011 artifact and its scientific source remains unchanged.
