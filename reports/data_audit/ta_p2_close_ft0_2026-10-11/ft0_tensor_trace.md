# Selected tensor traces

`synthetic_ft0_tensor_trace.json` pins analytic September15 2020 origin1:five stocks in AAPL,JPM,JNJ,WMT,CAT order,48 exact scheduled steps,16 channels,3,840 valid cells. It contains actual synthetic fitted certificate IDs, last AAPL raw/scaled values, masks and lineage, plus the separate aligned48×5 D7 result. Both stock-only and matched market fixture eligibility pass; science=false and model wiring=NOT_BUILT. Eventual width21 is metadata only.

`ft0_tensor_trace.json` pins actual March15 2021 origin1. Shape and scheduled joins are intact, but all 3,840 stock masks are false, actual scalers/floors NOT_RUN, SPY publication unknown and no eligible real case. Genuine source-only B/T values may be reported diagnostically; None scaled values and invalid masks are preserved. Missing bars keep their original positions; no shifting, zero-fill or per-model/window files.

Tests pin normal/DST/half-day, split, zero-range, missing-bar, previous-day, overnight-RSI and M2 late-maturity cases before outcomes. Existing corruption guards cover the immutable reader; no fabricated source clock or payment date is substituted.
