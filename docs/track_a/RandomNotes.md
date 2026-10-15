# Critical Checks

## M2 indicaotr:
Check if an invalid 48 block due to one or two missing piece is being discarded,
is the loss of data too much or is it fine?

M2.py is the main place where data assembly for M2 is happening before training. Check visually later if needed if things look correct.

M2.py  calculates the feature 
\[
\boxed{
M2_{i,t}=
\frac{\operatorname{Mean}(\text{last 20 historical returns})}
{\max\left(\operatorname{RMS}(\text{last 60 historical returns}),\epsilon\right)}
}
\]
## Market features.py is where the market features are being calculated.

Verify the formula and causal avaialbity later



## Investiagte further
There is a Q1/Q2 that I selected. Need to investigate

The data audit found 61.2% mechanical FT0 retention in training, below the frozen 90% guard,


## Issue with data prep:

Need some older data to start the warmup otherwise some data lost there
Big chunck of data missing. Need to fix it.



## first. batch of results - 4 models
Model 1: 16 stocks generated data
Model 2: 16 stock + 5 SPY market features
Model 3: 16 stock features modulated by market state, plus 5 SPY features
Model 4: 16 stock + 5 SPY + 2 peer-summary features

(Modulation is the gating feature :\[
g_t=\operatorname{softmax}(W_gm_t+b_g)\in\mathbb R^{16}.
\]
The stock features are then modified:
\[
\boxed{\tilde x_t=x_t\odot(16g_t)}
\])



1. Package 008 — Investigating the trained models
Without retraining, Codex analyzed existing checkpoints, predictions, and training logs.
- Gradient clipping: Examined gradient norms and clipping frequency across epochs.
- Target outliers: Studied extreme TG0 values, volatility denominators, and their contribution to MSE.
- Overfitting: Compared training and validation loss trajectories and early stopping.
- Model behavior: Examined predictions, hidden-state magnitudes, and MC1 gating.
- Statistical comparisons: Compared daily MSE and Rank IC using matched observations and exploratory block-bootstrap intervals.
Finding: Extreme targets and concentrated losses are substantial, but the precise cause of clipping could not be established from saved logs.
2. Package 009 — Testing whether findings persist
Codex trained TM0 and MC0 on a second walk-forward period (WF2), preserving the architectures and training specifications.
It also recorded more detailed batch-level gradient telemetry to investigate clipping.
The models were compared on identical observations against the zero baseline.
3. What did we conclude?
- TM0 achieved positive Rank IC in both WF1 and WF2.
- Adding SPY information through MC0 did not improve performance.
- Neither model beat zero prediction on MSE.
- Gradient clipping persisted, without numerical divergence.


What should we investigate now?
I recommend proceeding with our planned Package 008, focusing on five questions:
1. Gradient clipping: Why do all four LSTMs experience sustained clipping during calibration?
2. Extreme targets: Are large volatility-normalized returns and small volatility denominators driving the gradients?
3. Overfitting: How do training and validation losses evolve across epochs?
4. Architecture comparison: Why does adding SPY information worsen ranking accuracy, while E5 slightly improves it?
5. Statistical reliability: Are the differences in daily Rank IC and MSE distinguishable from noise?

Target tails and session loss concentration are substantial: training \(|TG0|\) reaches 82.03, and about 56% of squared loss sits in the worst 10% of sessions.



Extreme targets matter: \(|TG0|\) reaches 82.03, and the worst 10% of training sessions account for approximately 56% of squared loss.
Gradient clipping remains unresolved: All four models exhibit clipping warnings, but the saved logs cannot establish exactly what causes them.
MC1 provides no demonstrated improvement over MC0: Their ranking differences largely cancel.
E5's apparent ranking advantage is uncertain: Its Rank IC improvement over TM0 is only 0.0039, with a wide exploratory confidence interval.
No model beats the zero baseline on MSE.

# Random Notes
Aggregating 30 min sotcks into hourly candles:
Missing OHLCV data handled
Data acquisition under incoorect config rejected
Guard the July 1, 2024 – June 30, 2025 period for confirmation of results

1. AAPL dividend
Confirm the following reported dates and amount:
Field	Value
Ex-dividend date	May 8, 2020
Record date	May 11, 2020
Payment date	May 14, 2020
Dividend per share	$0.82

3. Early market close
November 27, 2020, was an early-close session, with regular trading ending at 1:00 p.m. ET.
Therefore, the normal 14:33 and 15:33 ET exit times are unavailable on that date.


Change to convey Jessica:

Our subsequent discussions established substantive agreement on:
- The 240-minute holding convention.
- Using hourly-close execution-price proxies for the initial research pass.
- Replacing Dukascopy USA500 with conventional S&P 500 market data.

Lookahead preventin hard coded in clocks.py at multiple locations

Causal eligibility ; prevent more lookahead bias


Hourly proxy. The 2-3 minute tradable price is assumed to be hourly price.
Lookahead bias in proxy preventions 
Made sure \epsilon is fitted using correct data
Making sures missing rows cannot shift M2 construction

M2.py: Handles exceptions for 48 hours look back of 4 hour prediction. (used in both training and prediction)


# Visualisation
Open the printed URL, normally http://localhost:8501.
1. Click Open Price & Features. Defaults: AAPL, WF2, January 16–19, 2024.
2. Switch candle intervals and explore T5/M1 in the feature panels.
3. Open Predictions & Errors, then Training Diagnostics

# Track A research explorer — five-minute Quickstart

Open the repository folder in VS Code, then **Terminal → New Terminal**. Run commands from the repository root. Complete the README setup (including its existing `neural` extra) first. The app uses the repository `.venv`; you do not need to activate it. Streamlit and Plotly are free packages installed locally. If they are missing, the one setup command is:

```sh
.venv/bin/python -m pip install -e ".[visualization]"
```

This visualization extra is pinned in `pyproject.toml`. It adds no paid service, account or API key. Follow the main README first if `.venv` itself is missing. Existing licensed source files and completed research artifacts must already be provisioned on this machine; the app does not download them.

Launch:

```sh
./scripts/run_track_a_dashboard.sh
```

The terminal prints **Open http://localhost:8501 in your browser**. Open that URL. If8501 is occupied, the launcher selects the next free local port and prints the actual URL. Direct fallback:

```sh
.venv/bin/python -m streamlit run apps/track_a_dashboard.py --server.address 127.0.0.1 --server.port 8501
```

Your first three clicks:

1. In **Start Here**, click **Open Price & Features**. Keep **AAPL / WF2 / TM0 / Development / January 16–19,2024 / Both origins**. These are verified available dates. You will see 52 genuine30-minute candles, volume directly underneath, and native **T5** below. Hover for exact ET/UTC, OHLC and volume. Scroll/zoom or drag to inspect.
2. Switch **Candle interval → Completed hour**: there are24 complete hours. Try **M1** in the FT0 selector and switch **native/scaled**. Enable **Show forecast / horizon events**. The four-hour future label close and three-minute nominal event times are explicitly marked; none is a fill.
3. Open **Predictions & Errors**, then **Training Diagnostics**. Inspect saved score versus EX-POST TG0, the five-stock ranking table, and calibration clipping separately from fresh refit. Diagnostics defaults its tail/loss scope to the recorded refit-training panel; its partition is labeled independently of the sidebar.

Candles are retrospective vendor split-adjusted USD with inverse-split volume. Native features, training-scaled model inputs and dollar prices have different units. T5 is `(RSI14−50)/50`; M1 is normalized momentum, not raw return. TG0 is future relative performance, not absolute return direction. Rank IC and MSE do not establish alpha or profitability.

Stop with **Ctrl+C in the launching terminal**. Useful checks:

```sh
./scripts/run_track_a_dashboard.sh --check
./scripts/run_track_a_dashboard.sh --smoke
./scripts/run_track_a_dashboard.sh --port 8502
curl --fail http://127.0.0.1:8501/_stcore/health
```

`--check` validates local bindings without starting a server. `--smoke` starts the app, checks local health/HTML, measures startup, then stops its own server. The curl command applies while a server is running.

For missing files, read the exact path in the app and provision the original artifacts using `data/README.md` and their manifests; do not substitute or retrain. For empty origins, try the verified default dates and **Both**. E5/MC1 have only WF1. To inspect the AAPL2020 split, choose **WF1 / Refit training**, then August28–31,2020; the chart retains a single retrospective scale. Dates are ET inclusive; hover preserves true UTC and DST. See the [User Guide](Visualization_User_Guide.md) for details.

Everything binds to localhost; telemetry collection is disabled. No public publishing or bulk raw-data export is provided. Local rights/clock/action assumptions remain qualified. Check applicable rights before sharing raw-data screenshots.
