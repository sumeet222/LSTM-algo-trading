# P2.4 market trace

SYNTHETIC_TEST and SOURCE_INTEGRITY_ONLY are separate from scientific activation.

The analytic fixture has every complete-hour log(C/O)=0.02 and prior daily log-return=0.01. Thus RMS12=RMS60=0.02, daily RMS63=0.01, five-day momentum=0.05 and20-day momentum=0.20. With earlier positive floors≤these scales:

| Channel | Independent arithmetic | Value |
|---|---|---|
| U1 |0.02/0.02|1|
| U2 |log(0.02)|−3.912023005428|
| U3 |log(0.02/0.02)|0|
| U4 |0.05/(sqrt(5)×0.01)|sqrt(5)|
| U5 |0.20/(sqrt(20)×0.01)|sqrt(20)|

The earlier certificate fits July1–July10, factual fitted_at July10. The August3 48-step input begins2020-07-22 15:30:00+00:00 and ends2020-08-03 14:30:00+00:00; all own cutoffs follow fit completion. Floors count36 unique hourly keys and6 unique daily keys. The scaler sees180 appearances but counts only36 unique timestamps. Constant-channel zeros and novel variation are distinct from standardized missing-state zeros. No clipping.

`src/lstm_data/market_features.py:581` emits the separate48×5 state; `src/lstm_data/market_tensor.py:45` yields5×48×21 by repeating the same direct market rows, with a separate48×5 mask and no learned mask channels/model. Source/stock lineage and identical endpoints are in JSON; the full actual stock FeatureCalculator composition is tested in `tests/test_stock_features.py::test_p2_4_actual_feature_calculator_to_causal_mc0_data_only`.

Acceptance edges: existing and new tests cover12/12,57/60 and60/63 with max2 consecutive misses; two missing standardized states pass46/48 while three fail; an invalid endpoint cannot be zero-filled; exactly90min source age passes, later age fails; duplicate/shifted hours fail. U4/U5 lock to previous session. Summer/winter and2020-11-27 early-close/stub traces are saved; the early close has no permitted240-minute origin. Future exit price/publication mutations leave prior input and C01 bridge unchanged.

The two-partition real trace uses only source observations throughJuly1 2020, no confirmation features. Both real origins retain publication UNKNOWN, missing floors/scalers, values=None and zero valid numerical cells. No synthetic availability, arbitrary empirical parameters or verified market vector was substituted. The remaining canonical9 partitions are preserved and reconciled through cached source manifests, not re-parsed. Arrow emitted sandbox CPU-cache probes denied by sysctl; parsing and the trace completed normally.

The preserved legacy helper default is HISTORICAL_TRAINING. Production joins pass the stock context; inference callers must pass ASOF. A fit within the same retrospective training interval is not historically available before its true fitted_at. Actual empirical fitting/admission staysHOLD (DEF004/005/007/008/009/011/016).
