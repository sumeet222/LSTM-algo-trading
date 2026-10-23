# P020 TG20 and clock audit

**FEATURE_READY_FOR_TRAINING. Dataset preparation only; neural training is not authorized.**

At each allowed origin, r_i=log(genuine_exit_close/genuine_entry_close), m=median20(r), a=median20(abs(r-m)), TG20_i=(r_i-m)/(a+epsilon). Epsilon=max(1e-4,0.1median_unique_train(a)), fit independently for each training prefix using all complete20genuine mature origins, independent of feature values. No volatility scaling, 5stock cross-section, clipping or partial19/20target. If one genuine compatible endpoint is unavailable, all20labels are ineligible. No proxy, stub, overnight or COP-crossing price generates a label.

Regular-session completed-end clocks:10:30→14:30 and11:30→15:30 ET, with issuance and maturity2minutes later under the inherited publication assumption. Early closes produce no synthetic four-hour horizon. Feature input admission is separate from eventual ex-post label validity. Historical M2 outcomes are distinct past own-stock source signals; current future TG20 labels are never feature arguments.

T2 preprocessing s=max(median_unique_admitted_training_origin_stock(abs(TG20)),1e-6), z=asinh(TG20/s), inverse=s*sinh(z_prediction) exactly once. No learned model or target prediction was computed. C0 and T2 use the identical X, origin mask and original TG20 evaluation scale. Validation selection next package must use inverse-transformed original TG20 MSE, not transformed-space MSE or development results.

| Fit | Train end | Epsilon | Epsilon origins | T2 scale | T2 origins |
| --- | --- | --- | --- | --- | --- |
| inner | 2023-01-23 | 0.00032970431934696 | 4864 | 0.906406830018944 | 4428 |
| refit | 2025-06-30 | 0.00033464021096456584 | 5773 | 0.9057319697455458 | 5210 |

Training target quantiles (uncapped): {"0": -32.630348601739534, "0.01": -5.419494166849399, "0.5": 0.0, "0.99": 5.78997555449669, "1": 46.20068269622903}.

Training-only tail thresholds: {"mad_p05": 0.0017088144016643594, "abs_numerator_p95": 0.01593538084097676, "abs_TG20_p99": 7.249104565631099}. Tail mechanisms: {"LARGE_NUMERATOR": 1001, "BOTH": 101, "SMALL_MAD": 50, "ORDINARY": 3}. These thresholds are diagnostic labels, not target filters. Top absolute target, numerator and smallest-MAD examples remain private, with endpoint and source row links. Fifty extreme endpoints were independently verified against genuine candles. Protected2026numeric features/returns/targets were never calculated or stored.
