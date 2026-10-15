# Measured conditional G3 population

All counts below come from actual finite 48×16×5 inputs, mature five-stock hourly-close proxy targets, origin-matched historical M2 and training-prefix preprocessing. They are not candle-presence counts. Every result is ASSUMPTION_CONDITIONAL and candidate-only; observed historical causality and source rights remain uncertified.

| Population | Nominal | Admissible | Retention | Distinct sessions |
|---|---:|---:|---:|---:|
| TRAIN July2020–June2023 | 1,502 | 1,502 | 100% | 751 |
| WF1 July–December2023 | 248 | 248 | 100% | 124 |
| WF2 January–June2024 | 248 | 248 | 100% | 124 |

Both origin types retain every nominal observation. The required 1,352/1,502 training threshold, 90% development, 85% fold/origin and 100-fold-session checks pass in the conditional study. Exact stock-window masks and four distinct admission states are preserved in build_v4/stock_window_masks.csv and origin_admission.jsonl. No score was issued: forecast_issuable=false because no model or issuance permission exists. `entry_reference_eligible` is a price/input condition, not portfolio/fill admission.

The 63-calendar-session inner tails retain: WF1 63 sessions / 63 observations at each origin; WF2 62 admissible sessions / 62 at each origin (one early-close session cannot host the nominal hold); preconfirmation fitting 63 sessions / 63 at each origin. The June2023 calibration prefix has 1,376 origins, with 126 inner-tail origins; the refit prefix has 1,502. All labels mature before their applicable boundary. No inner tail was shifted based on values.

All 1,998 stock origins also have admissible conditional SPY endpoint/history masks under the separate annex. The market observations are counted once per market timestamp. Six prefix floor/scaler recipes preserve separate inner-train and full-refit populations. No development-only preprocessing was fitted; WF1 development may enter the separately defined WF2 training prefix, as frozen chronological walk-forward requires.

The first actual 48-step input starts 2020-06-19 slot2. The required prior M2 return histories are genuine and mature on the approved ideal clock. Daily/EMA/RSI warmups use the archived 2019-12-18 onward context without making it scaler-fitting membership before July2020. No four-name fallback, skipped missing slot or synthetic candle was used.

Conditional volatility retention is HIGH/LOW=100% in every period, gap0pp. Nominal counts: train752/750; WF1 22/226; WF2 15/233. Support/episode counts are in conditional_regime_retention.json: WF1 HIGH and both WF2 states are sparse by the ≥30-session AND ≥3-episode interpretation rule. No regime-specific conclusion, training branch or threshold search is activated. Trend follows the existing standardized-U5-sign diagnostic; raw U5 sign is recorded separately so it is not confused with positive absolute trailing momentum.

No G3 count certifies historical publication, complete action vintage, source licensing, course substitution or production migration. DATASET_READY_FOR_FIRST_P4_3_PAIR remains false under the researcher's permanent candidate-only limit. G6 is NOT_RUN; optional branches remain inactive unless separately authorized.
