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