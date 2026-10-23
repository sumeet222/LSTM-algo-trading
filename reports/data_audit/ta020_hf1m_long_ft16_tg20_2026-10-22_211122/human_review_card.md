# P020 human review card

**FEATURE_READY_FOR_TRAINING. Dataset preparation only; neural training is not authorized.**

Only mito0o852/OHLCV-1m at revision `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`. Parent `HF20_HF1M_LONG_v1_ACTION_QA_v1`, P019B current v3 action ledger and PRE_FEATURE_READY_WITH_QUARANTINES gate. All9 split events,6 genuine moves,18 quarantined RTH minutes/14 bins, EH/KO exclusion and COP boundary masks retained. Root anomaly register and all original source bytes are unchanged. No old Alpaca/Twelve Data numeric inputs, fitted statistics, model outputs or checkpoints.

New IDs: `HF20_HF1M_LONG_v1_FT16_v1`, `HF20_HF1M_LONG_v1_TG20_4H_v1`, `HF20_HF1M_LONG_v1_MODEL_INPUT_v1`. Ordered20: VZ,COP,BAC,BA,AAPL,PEP,MRK,SBUX,CVX,MS,AMD,KO,JNJ,AMZN,XOM,WFC,AVGO,TSLA,MA,CSCO.

Rights remain HUMAN_REPORTED_MAINTAINER_PERMISSION_FOR_PRIVATE_RESEARCH, not independent legal certification; numerical stores and price examples remain ignored/local. Publication timing remains UNKNOWN. Completed-hour end+2minute issuance and maturity are conditional research assumptions, not executable-fill evidence.

Frozen chronology: warmup2010-07-01–2011-03-31; research train2011-04-01–2025-06-30; inner train ends2023-01-23; nominal inner validation2023-01-24–2025-06-30; development2025-07-01–2025-12-31; protected confirmation2026-01-01–2026-03-31 (keys/calendar/source quality only). First48complete-hour contexts after fit cutoffs are embargoed. All horizons mature within the same session; no crossing labels survive. The nominal15calendar-year research/confirmation span contains14years3months of fitted training history plus9months earlier startup. Missing dates and hourly positions never compress.

| Split | Admitted origins | Stock rows | First/last admitted date |
| --- | --- | --- | --- |
| inner_train | 4428 | 88560 | 2011-04-01 / 2023-01-23 |
| inner_validation | 766 | 15320 | 2023-02-03 / 2025-06-30 |
| refit | 5210 | 104200 | 2011-04-01 / 2025-06-30 |
| development | 183 | 3660 | 2025-07-15 / 2025-12-31 |

16features usable under frozen causal fallback. Refit Q1fallback6.7006%,Q2fallback21.6755%; development Q1fallback4.4553%,Q2fallback10.0529%. Maximum across all channels/splits 34.2549%. Native components and missing masks remain separate; no claim of complete minute volume.

TG20 uses genuine same-session4hour returns, exactly20stock median/unscaledMAD, and separate train-only inner/refit epsilon. T2 uses saved train-only s=median(abs(TG20)), asinh(y/s), with inverse s*sinh(z) once. No clipping or target imputation. Details: P020_TARGET_TG20_AND_CLOCK_AUDIT.md.

Readiness:5,210training origins/104,200stock rows;183development/3,660stock rows;4,428inner training/88,560stock rows;766inner validation/15,320stock rows. Training covers15years with>=100origins each. Final development reduction11/194 is the frozen embargo. All20stocks retained.

Top limitations: incomplete/lower-bound volume, Q2fallback, historical source latency unverified,15:30daily surrogate, retrospective cohort and split units, dividends not reconstructed. All16future-split invariance and causal checks passed. No protected numeric features/targets stored.

83 focused tests passed; full static check:292files,0errors,0warnings; Ruff passed. Measured new storage157.4MB at receipt; peak processRSS1.295GB. Continuous storage peak was not instrumented; conservative transient bound is below0.5GB, versus10GB ceiling. Exact bytes and scope: final_resource_receipt.json. Ledger32/200unchanged. Next action is separately authorized matched seed42 C0/T2 training; no model has been trained and no training permission is implied.
