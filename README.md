# LSTM Algorithmic Trading Project

Group project investigating shared LSTM models for short-horizon
cross-sectional equity prediction with broad-market conditioning.

See `AGENTS.md` for repository and development guidelines.

## Track B: Preliminary Data Checks and Model Pilots

These experiments explore whether the course-provided USA500 and USATECH hourly data can be aligned with Alpaca stock data and used for return prediction.

### Files

| Code | Saved outputs |
| --- | --- |
| `Track_B_Alpaca_Data_Check.ipynb` — data and alignment checks | `Track_B_Alpaca_Audit_Results/` |
| `Track_B_Ridge_Pilot.py` — Ridge baseline | `track_b_ridge_pilot_Results/` |
| `Track_B_LSTM_Pilot.py` — exploratory LSTM pilot | `track_b_lstm_pilot_Results/` |

Start with `validation_summary.csv` in each model's results folder. See `pilot_settings.json` for settings and assumptions.

### Experiment Setup

- **Stocks:** AAPL, MSFT, NVDA, INTC, and CSCO.
- **Target:** Each stock's next four-hour, same-session log return minus the equal-weight mean log return of the five stocks.
- **Training:** Before January 2023.
- **Validation:** Calendar year 2023.
- **Feature variants:** Stock only; stock + USA500; stock + USA500 + USATECH.
- **Metrics:** MAE, RMSE, and mean cross-sectional rank correlation between predicted and realized returns.

The alignment uses exact matching of complete hourly intervals without forward-filling index data. Course timestamps are provisionally treated as bar-start timestamps; this convention has not been confirmed with the source.

### Preliminary Findings

Both pilots produced validation predictions using the aligned data. Adding index features improved mean rank correlation in some configurations, but did not consistently reduce forecast errors.

### Limitations and Next Steps

These are exploratory validation results, not final test results or evidence of trading profitability. The LSTM pilot uses one random seed. Ridge and LSTM use different feature designs, so direct comparisons require matching prediction samples and consideration of those differences.

Next steps are to confirm the course timestamp convention, agree on a common evaluation setup, and assess robustness before a trading backtest with execution assumptions and costs.
