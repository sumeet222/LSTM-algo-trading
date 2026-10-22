# Source-minute QA: STOP_QUALITY

March 2026 only, not RAW_MINUTE_QA_PASS and not full-period coverage. Final quantitative evidence is in `qa_2026-03_final/`; the earlier offline QA folder is preliminary and retains the progression. `month_2026-03_attempt2/runtime.json` records an implementation exception after the immutable extract committed; final offline replay used that same verified partition with zero network and resolved to STOP_QUALITY.

- 50 conflicting rows form25 keys across15 names.46 rows/23 keys are regular-session;4 rows/2 keys are extended-session TSLA. All 50 have different OHLCV at their duplicate key; exact duplicates0. Preserve both candles.
- AAPL March 31 14:21UTC: source rows21525046/21525047, row group20. First OHLC248.71/248.75/248.61/248.705, volume31785; second248.74/248.77/248.72/248.75, volume7428. There is no approved rule to choose or combine them.
- PEP March 10 has15 absent RTH minutes and maximum3 consecutive, exceeding the provisional2-minute bound.
- MRK March 19 13:30UTC and WFC March 31 13:30UTC opening minutes are absent. No preceding-session carry or backward fill is permitted.
- 387 absent genuine expected stock-minute slots;23 additional conflicting RTH keys excluded from unambiguous validity.171,213 observed unique RTH stock-minute keys /171,600 expected;171,190 unambiguous valid keys. All 440 stock/sessions have at least one RTH row.
- 0 nonpositive/nonfinite/malformed OHLCV,0 off-minute rows,0 wrong-local-month rows,0 all 20 synchronous absent RTH slots,0 observed regular-session close jumps above25% in the sample. These checks cannot establish historical corporate-action, dividend or adjustment coherence. No action factors or inferred corrections were introduced.

`conflicting_duplicate_candles.csv` retains all 50 original rows with source row offsets and RTH flag for LOCAL private review; do not automatically publish/upload it. `priority_missing_minute_examples.csv` and `qa_2026-03_final/anomalies.csv` identify missing/invalid slots. `ticker_session_qa.csv` has440 stock/session records. `ticker_year_partial_counts.csv` is March-only and expressly not annual coverage. No fill/hourly store exists because complete-period raw QA was never reached. UTC minute starts match publisher semantics structurally; calendar alignment is evidence, not independent attestation of trade publication time.
