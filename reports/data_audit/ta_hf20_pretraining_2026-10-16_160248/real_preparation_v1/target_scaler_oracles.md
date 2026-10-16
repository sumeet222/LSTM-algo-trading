# Target and transform oracles

Feature arithmetic is independently recomputed from aligned source fields, including ordinary, missing-hour, DST, early-close and split-boundary examples. Three real complete20stock targets retain raw returns, median, unscaledMAD, epsilon and maturity. Targets and features are never clipped. The synthetic extreme/zero-constant and no-leak tests are independent of these genuine samples. All comparisons are training/development only; see finite_oracle_checks.json and scaler_population_oracles.csv.
