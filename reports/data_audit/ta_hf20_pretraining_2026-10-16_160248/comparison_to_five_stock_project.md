# Comparison with the historical five-stock project

HF20 is a separate retrospective 20-name availability-selected panel. It does not change original D1, FT0, TG0, dates, weights, model results or ledgers. CMCSA/CME are absent from the HF source, COST is not selected, and AAPL/SBUX overlap the old candidate by name only.

HF20 uses publisher hourly source candles on a conditionally accepted full-hour clock, not genuine native30-minute aggregation/lineage. Its daily references omit the closing half-hour; its observed last-full-hour close has independent validity while daily proxy volume requires six full hours. FT1 v2 therefore differs from FT0 even where formula names are shared. Adjustment and share-volume units are explicitly as-reported assumptions, not authenticated split/dividend/PIT histories.

TG20's20-stock median/MAD differs numerically and economically from TG0's five-stock cross-section. The dates, cross-sectional distribution, epsilon and peer ranking context differ. Raw MSE levels cannot be compared as identical targets; any future comparison must use within-version controls and disclose the changed source/universe/window. Historical five-stock checkpoints cannot be loaded as approved HF20 weights. No five-stock or HF20 model fitting/scoring occurred here.
