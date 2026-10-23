# P023 explorer guide — 5–10 minutes

Launch `./scripts/run_track_a_dashboard.sh`, then **Explore → HF1M Long — Direction / 
Quantiles / Sampling (P023)**. This is a section in the existing app.

1. **P023 view → Comparisons**, **P023 role → development**. Change **P023 model** among 
DM1/QR1/SS1. Inspect task-specific prefix constants and saved T2/42,T2/123,ZERO. QR1 
median MSE is descriptive, not a fair mean-optimum comparison; proper pinball/coverage is 
primary.
2. **Optimization / Gradients** separates calibration/refit actual objective curves and 
gradient percentiles/clipping. DM1 uses signCE+magnitudeMSE; QR1 uses pinball; SS1 uses 
sampled importance-corrected zMSE. Do not compare loss magnitudes across tasks.
3. **Head Outputs** and **P023 output stock** show DM1 
probability/magnitudes/cancellation, QR1 ordered .05/.50/.95 bands and calibration, or SS1
 forecasts plus actual sampler exposure. Probabilities and quantiles are different 
objects. Predicted magnitude alone is not success.
4. **Actual-Objective Tails** → **P023 cohorts** compares rank top1/top5, train-maximum 
ranges and numerator/MAD disjoint groups. Count/weight/loss percentages differ. 
Overlapping groups do not add; RMSE is not additive. Attribution is final-checkpoint 
dropoutOFF, distinct from online dropoutON.
5. **Exact Cases** uses saved in-sample refit witnesses independent of role selector. 
Inspect raw heads, true target components, source quality,52scheduled candles 
and48×16native/scaled features. First48hours are inputs and final4are outcomes. Verified 
example selections:

- **DM1 → Exact Cases → P023 exact case 1**: AAPL, origin `2013-08-13T15:30:00+00:00`.
- **QR1 → Exact Cases → P023 exact case 6**: AMZN, origin `2012-03-20T15:30:00+00:00`.
- **SS1 → Exact Cases → P023 exact case 11**: TSLA, origin `2013-05-09T15:30:00+00:00`.

6. **History / Features** → **P023 history stock/start/end** gives all20stock genuine 
OHLCV plus closing stubs, July2010–December2025,≤93days per request. **P023 feature 
recipe/M2 context/channel** selects all16native/scaled features. Missing/proxy/volume 
flags remain visible. Dates are checked before numeric loading.
7. **Guide** shows these controls. Existing P021/P022 and legacy study sections remain in 
Explore. Protected2026query/widget/role requests are denied; no fallback source.

Roles: inner_train calibration in-sample; inner_validation selected epochs; refit fresh 
in-sample; development183origins/3660rows/109sessions exploratory. Ledger44/200. No 
seed123newarm, combination, trading or confirmation access. All numeric artifacts remain 
private/local.
