# Approved matched non-neural comparison

The original public P3.5 FitData/RidgeModel/Prediction interfaces remain synthetic-only. No prior candidate real-baseline permission was found. Actual researcher reply “Approve this non-neural baseline scope” approved proposalSHA `cb77779f44eb2310bb6375ebda3adccefc8c3fd5c90f41b1151d388e84fbc16e` in this session. baseline_decision_v1.json preserves provenance. This separate permission covers M1 and own112ridge only; market 147-column ridge, neural fits and trading are excluded.

A typed real-view adapter reuses the existing pure P3 solve_weighted/session_weights/choose_penalty and LAGS/PENALTIES unchanged. No synthetic mode is applied to genuine data. All48steps/16FT0 are the reviewed float32TM0inputs. Ridge extracts scheduledlags[0,1,2,5,11,23,47],lag-major/channel-minor,112 columns, float64linear algebra. One free common intercept, no ticker ID. The objective weights each day equally, each eligible origin equally inside day and each of5 names equally. Five inner candidates on1376 origins; select only minimum MSE on110tailorigins/55 days, exact tie largerlambda; fresh solve on1502 full-prefix origins. Immutable distinct preprocessing/TG0floors are reused, with no WF1 fitting. Ridge sees7 snapshots over48hours, whileTM0reads all 48, so information is not exactly identical.

Selected lambda **1.0** from the frozen five-value grid; no grid expansion. Candidate MSE/conditioning/residuals and final 112 coefficients / free intercept are stored in baseline_execution.json. An exclusive baseline_started.json prevents unnoticed refitting on replay. Exactly 5 inner + 1 fresh refit algebraic fits occurred;0 neural pairs. The neural journal/pointer/legacyledger are byte-unchanged.

| Model | WF1 MSE | daily IC | Origins / days |
|---|---:|---:|---:|
|TM0|5.438829600|0.034913793|232 / 116|
|ZERO|5.427531844|0.000000000|232 / 116|
|M1|12.691976309|-0.021982759|232 / 116|
|RIDGE_OWN_112|5.465518006|-0.022844828|232 / 116|


All four use the exact same 232 origins / 116 sessions and five ordered candidates; no intersection attrition. The mask and preparation IDs are bound in pilot_metrics.json/mc0_input_readiness.json. Zero is a fit-free constant prediction: project IC 0, mathematically defined-only IC null,232 constant/tied origins. It is not a random-trading benchmark. M1 is descending canonical scaled 1-hour momentum, fixed without sign/horizon tuning; its raw score is not fitted/calibrated toTG0, so its MSE must be interpreted with that limitation. No score rescaling was introduced.

Actual baseline timings: design/recipe application0.343483s;5inner solves0.032885s;1fresh refit0.008396s;prediction/metrics0.093783s. Fitting sum **0.041280s**. Complete review/market-input/frozen-inference/baseline command24.611s includes setup/source loading and is not baseline fitting time. No cost/economic/buy-and-hold/random replay, market ridge or confirmation run. No p-value/significance claim or winner-driven next configuration.
