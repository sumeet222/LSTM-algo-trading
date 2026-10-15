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



##

What should we investigate now?
I recommend proceeding with our planned Package 008, focusing on five questions:
1. Gradient clipping: Why do all four LSTMs experience sustained clipping during calibration?
2. Extreme targets: Are large volatility-normalized returns and small volatility denominators driving the gradients?
3. Overfitting: How do training and validation losses evolve across epochs?
4. Architecture comparison: Why does adding SPY information worsen ranking accuracy, while E5 slightly improves it?
5. Statistical reliability: Are the differences in daily Rank IC and MSE distinguishable from noise?

Target tails and session loss concentration are substantial: training \(|TG0|\) reaches 82.03, and about 56% of squared loss sits in the worst 10% of sessions.

## first. batch of results

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