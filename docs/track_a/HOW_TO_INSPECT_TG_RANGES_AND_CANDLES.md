# Inspect TG ranges and genuine candles

Launch locally with `./scripts/run_track_a_dashboard.sh`. Setup checks:
`./scripts/run_track_a_dashboard.sh --check`; local server check:
`./scripts/run_track_a_dashboard.sh --smoke`. Stop with Ctrl+C. Use the repository
environment and legitimately provisioned, hash-matching existing sources/artifacts.
No fitting, model inference, provider request or neural pair is needed.

## Three-minute guided example

1. **Start Here → Package 011: Compare C0 and T2 → Target & denominator**.
   Keep **Study fold WF1 / Study seed 42**. Scroll to **Generic target range explorer**,
   choose **TG0 / Range population: Full refit prefix**. Blank both numeric bounds
   initially includes every eligible observation. These controls are independent
   of the sidebar's development dates and of the separate training-histogram controls.
2. Set **Range variable: Absolute / Upper bound: 2 / Include upper endpoint: off**
   with a blank lower bound for `|TG0| < 2`. Set **Range stock: AAPL**, then use
   **Select observation (stock / session / origin / UTC)** to choose any ordinary
   observation. The selector searches every matching identity, across all pages.
   **Show candles** is always visible. Selection updates the chart on the same page,
   immediately beneath the table and its selection controls. Table cells are not clickable.
3. Clear the stock filter. To see `|TG0| > 10`, blank the upper bound, enter lower
   **10**, and turn **Include lower endpoint** off. Inclusive endpoints instead
   give `>=10` or `<=2`. Choose **Signed**, lower **-2**, upper **0**, and exclude
   the upper endpoint for negative-only ordinary observations. Blank means unbounded;
   NaN, infinity, invalid text and reversed bounds produce a useful validation message.
4. Clear both bounds, choose **AAPL / 2020-12-09 / origin 2 / 16:30 UTC** in the
   observation selector. Inspect the exact decomposition and chart; origin is
   **11:30 EST**. **Open in Full data** carries the exact identity, stock and date.
   Choose **Indicator(s): M1** and switch **Standard / native indicator →
   Normalized / model input → Both**, using **WF1 / refit** as the explicit recipe.

The referenced WF1 full-refit relation has 7,510 observations: strict `|TG0|>1`
selects 2,860; strict `|TG0|>10` selects 67. These are fixture checks, not hardcoded
dashboard populations. The original defect counted every match but rendered
`tails.head(30)` and decomposed only `head(20)`. The replacement reports total
eligible population, stock/date/origin-selected population, target-range matches,
rendered rows and page number separately. At 50 rows per page the 2,860 matches
span 58 pages, with 10 rows on the last page. Every matching identity is reachable;
sorting never changes row identity. A removed/changed population resets selection.

## What the target and markers mean

TG0 is `(future 4h log return − cross-sectional median) / (MAD + epsilon_train)`.
The original float64 registered training population is hash-verified; saved
development labels have float32 precision and are validated against the same
decomposition (absolute tolerance 2e-6). Development displays the canonical
float64 decomposition, not an optimizer-transformed label. T1 clipping and T2
asinh labels remain separate. TG0 is **not** a historical-volatility-normalized
return. Future return, median, MAD, numerator, denominator and TG0 are **EX-POST**,
unavailable at the forecast cutoff. The training epsilon and recipe stay fixed.

The denominator is additive **MAD + epsilon**, not `max(MAD, epsilon)`.
`floor_ge_MAD` is the existing `epsilon >= MAD` flag, including equality;
`MAD_lt_epsilon` is a separate strict comparison. The optional comparison expander
uses the full selected stock/date/origin population, independent of pagination
and target range. MAD is shared by all five stocks in a session/origin; these
observations are not statistically independent. It is descriptive, with no new
resampling or scientific comparison.

The inline chart defaults to two exchange sessions before and after (maximum
five on each side). Gold marks the precise forecast **completed-hour boundary**,
blue the **EX-POST four-scheduled-full-hour proxy close**; dashed lines mark
nominal three-minute entry/maturity events. The last completed native intervals
are listed. A source candle is labeled at its **start**, and the cutoff is not a
newly invented candle. All horizon steps use the exchange calendar; early-close
ineligible horizons are unavailable. Archive edges are clipped with a message.
The existing **Extreme Events → Inspect on Price & Features** action also remains.

Prices are genuine local SIP 30-minute OHLC, USD on the vendor's retrospective
split-adjusted basis; volume uses corresponding inverse-split adjusted shares.
Hover exposes both clocks, OHLC and volume; exact details preserve full numerical
precision. Volume sits directly under prices on a shared time axis. Use Plotly's
zoom, pan and reset controls. Completed-hour mode uses the existing genuine
aggregation and excludes closing stubs. Missing candles remain missing.
Completed-hour proxy prices do **not** establish executable fills. Future candle
context never enters the separate exact 48-hour model-input trace.

## Price & Features → Partition → Full data

Choose **Price & Features**, then **Partition: Full data**. It is labeled
**Full data — chart-only history, not a training/evaluation partition**.
Select **Stock**, **Jump to date (ET)** or a bounded **Date range**, **Candle interval**,
**Indicator(s)**, **Indicator display**, **Fitted preparation** and **Indicator origin
context** (M2 is origin-specific). For a direct check choose AAPL / December 9, 2020;
its candles match the existing native chart and inline TG inspector exactly.
Previous/next exchange-session buttons handle weekends/holidays; early closes
are identified. The default is one session; ranges are bounded to 32 calendar days.
No five-year browser trace or duplicated historical dataset is created.

All 16 registered FT0 channel IDs are selectable, with their actual definitions.
Native means the project's actual formula using the explicitly chosen recipe's
saved floors/pseudocounts; it does not mean unadjusted prices or a substitute
industry indicator. For example, native M1 already divides hourly log(C/O) by
floored RMS60. Normalized M1 additionally uses the exact saved pooled center/scale
and float32 model-input conversion. B2/T2/T5 use native bounded identity.
Actual fitted method, center/median, MAD or fallback scale, training cutoff,
preparation ID, source binding and floors are available in recipe/details and
hover. Price, volume and every native/scaled indicator have separate aligned axes.

The recipe is selected explicitly, not inferred from the date. Refit recipes
cover their own training prefix and registered development interval; inner recipes
cover inner training plus the registered inner-validation tail. WF1 recipes do not
authorize 2024 observations: choose a legitimately scoped WF2 recipe or see
**UNAVAILABLE / out of preparation scope**. There is no scaler fallback or refit.
Training-prefix displays apply the saved training normalizer **retrospectively**;
they are not a claim that a later-fitted recipe was available live on that old date.
Model forecasts and TG outcomes are not loaded in Full data.

**Refit training** means the historical training prefix used for the final refit;
its forecasts are in-sample diagnostics. **Development** means that fold's saved
outer evaluation mask. **Inner validation** belongs to calibration selection.
Full data changes none of these meanings in any other dashboard section.

## Confirmation protection and limitations

The entire selector timeline is visible through June 30, 2025. **2024-07-01 through
2025-06-30 remains LOCKED**, including price/volume. Selecting any range touching
it stops before numerical source, recipe or feature readers. There is no unlock
checkbox in this implementation. Even viewing later-period raw numeric prices
visually can compromise an untouched-confirmation claim. A separate affirmative
researcher authorization must record/reclassify any later viewing, and may require
a new holdout plan. This implementation prompt does not supply that authorization.

Only TG0 is registered. Unknown TG IDs return **NOT_IMPLEMENTED**, without invented
values or a TG0 horizon fallback. Missing/changed genuine source files produce
unavailable/provenance messages; no approximate prices, imputation, downloads or
on-demand fits are substituted. ASSUMPTION_CONDITIONAL universe/action/period-end
clock and local source-rights qualifications remain. No production D1 readiness,
trading or alpha claim is made. Do not bulk export licensed raw data.
