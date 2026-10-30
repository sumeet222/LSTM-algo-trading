# HF20 S9-MAG classical volatility and rolling-magnitude benchmarks

**Status: PARTIAL study; B1, B2 and B4 complete on all four folds, B3 GARCH BLOCKED before fitting.** No completed classical arm closes the calibrated raw-magnitude MSE or magnitude-ranking gap to CLOCK-C3/S2C-C3. This is bounded exploratory/post-search evidence, not proof that recurrence is necessary and not a trading claim.

HAR-RV-A-CAL is the closest completed classical magnitude forecaster: equal-year MSE **0.000109068193648**, versus CLOCK-C3 **0.000106665945886** (+2.2521%) and S2C-C3 **0.000106548167844** (+2.3652%). It is worse in all four annual MSE point estimates. The paired CLOCK difference is +2.40225e-6, descriptive 95% interval [1.25862e-6,3.89825e-6]; the F23/F24 individual-year intervals include zero. Its MAE is0.0068339672 versus CLOCK0.0067570931.

ROLL60 has the highest completed classical IC, **0.318689978**, versus CLOCK0.330254043, S2C0.331235977 and S5C0.332045935. Its CLOCK IC difference is−0.0115641 [−0.0169563,−0.00644209]. ROLL60-CAL MSE is5.0838% above CLOCK. HAR's IC0.314465180 and top4 retrieval0.407792743 also trail CLOCK0.330254043/0.429465854. “Closest” is descriptive across the independently preregistered arms; it is not a selector-chosen new model or automatic promotion.

Much ranking signal exists in the causal static-stock prior: B0-RMEAN IC0.300238273. Dynamic classical forecasts add some signal (ROLL60 +0.0184517 IC; HAR +0.0142269), but CLOCK adds+0.0300158. Relative to that prior's MSE0.000122364416770, HAR-CAL reduces loss10.8661% and CLOCK reduces it12.8293%. These comparisons support incremental information beyond a stock-only prior in the completed models; neither an IC ratio nor the score-variance decomposition measures a fraction of predictive skill caused by stock priors.

The calibration-neutral view differs: HAR-UNCAL MSE0.000108962199651 is4.6452% below CLOCK-RAW0.000114270289094 (paired−5.30809e-6 [−7.29776e-6,−3.22874e-6]). All completed classical UNCAL arms have lower MSE than CLOCK-RAW, while CLOCK's raw MAE is lower. The leading neural advantage is therefore an advantage of the **frozen neural-plus-C3 forecasting package**, not an isolated proof about its raw encoder. Classical CAL uses a different, fixed global multiplicative family. CAL was primary prospectively; no RAW arm replaces it after OOS inspection.

## Frozen task, chronology and execution

Original genuine A=abs(log(P_endpoint/P_origin)), endpoint240 actual XNYS trading minutes, 20 names in canonical order, all seven original slots and actual early-close categories. No target, source vintage, eligibility, input recipe, role index or outer key changed. Exactly80,260 rows /4,013 origins /793 sessions; annual rows19,100/23,600/17,740/19,820. Equal stocks within origin, equal origins within session, equal sessions within year, equal four annual scores. Conditional magnitude groups renormalize original row weights; conditional ranking groups use the established equal-origin/session reducer.

**The original target's nominal origin is before approximate origin+2-minute publication.** This remains a historical timing proxy, not measured vendor arrival or executable post-issue return. Fixed survivors, retrospectively curated adjustments/quarantine, and repeatedly inspected2021–24 folds remain limitations.

Exact roles come from the archived O1 role_indices.npz and DesignA Session2B amendment/role_counts; all20 arrays, first-of48 embargo and endpoint+2minute maturity were replayed. No selector tuning is needed for these fixed designs. Parameters are estimated only from the September restricted role. Calibration uses the independent preceding Oct–Dec role. Dynamic states can consume preceding cal/OOS observations only once their genuine endpoint+2minutes is strictly earlier than issuance; this is prequential filtering, not parameter refitting. Their histories may therefore be fresher than frozen neural weights; neural input windows also update causally. No assertion of identical information sets is made.

| year | role | origins | sessions | rows | first | last |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | inner_train | 11449 | 2100 | 228980 | 2011-04-01 | 2020-06-30 |
| 2021 | selector | 349 | 57 | 6980 | 2020-07-13 | 2020-09-30 |
| 2021 | restricted_refit | 11846 | 2164 | 236920 | 2011-04-01 | 2020-09-30 |
| 2021 | calibration | 283 | 56 | 5660 | 2020-10-12 | 2020-12-30 |
| 2021 | oos | 955 | 188 | 19100 | 2021-01-13 | 2021-12-31 |
| 2022 | inner_train | 12560 | 2301 | 251200 | 2011-04-01 | 2021-04-30 |
| 2022 | selector | 278 | 58 | 5560 | 2021-05-12 | 2021-09-30 |
| 2022 | restricted_refit | 12888 | 2366 | 257760 | 2011-04-01 | 2021-09-30 |
| 2022 | calibration | 245 | 50 | 4900 | 2021-10-12 | 2021-12-31 |
| 2022 | oos | 1180 | 210 | 23600 | 2022-01-12 | 2022-12-30 |
| 2023 | inner_train | 13776 | 2526 | 275520 | 2011-04-01 | 2022-05-31 |
| 2023 | selector | 313 | 59 | 6260 | 2022-06-10 | 2022-09-27 |
| 2023 | restricted_refit | 14137 | 2592 | 282740 | 2011-04-01 | 2022-09-27 |
| 2023 | calibration | 258 | 48 | 5160 | 2022-10-13 | 2022-12-30 |
| 2023 | oos | 887 | 187 | 17740 | 2023-01-13 | 2023-12-29 |
| 2024 | inner_train | 14824 | 2719 | 296480 | 2011-04-01 | 2023-05-31 |
| 2024 | selector | 291 | 69 | 5820 | 2023-06-12 | 2023-09-29 |
| 2024 | restricted_refit | 15167 | 2795 | 303340 | 2011-04-01 | 2023-09-29 |
| 2024 | calibration | 163 | 40 | 3260 | 2023-10-11 | 2023-12-29 |
| 2024 | oos | 991 | 208 | 19820 | 2024-01-11 | 2024-12-31 |

## Model and source decisions

- **B1:** ROLL20/ROLL60 equal arithmetic means of the last20/60 original eligible stock-slot A observations, EXPANDING all earlier such observations. Original source/input/label complete-panel support from2011-04-01 is the history universe. All selector/calibration/OOS origins have at least60 mature observations; no fallback and no source expansion. These arms capture persistent stock risk and dynamic same-clock history.
- **B2:** lambda.94 per observed same-slot session. Restricted-prefix conditional hierarchical signed mean and positive variance seeds for EWMA-R2, raw-A mean seed for EWMA-A; burn through each corresponding legal fitting observation once, then filter newly matured observations. Folded-normal conversion includes the exact zero-sigma/zero-mean limits; Gaussian expectation is a modeling assumption, not a distribution-free identity.
- **Approved B2 amendment:** The source audit found59 consecutive same-slot interval overlaps:16 at09:30,15 at10:30,11 at11:30,17 at12:30. Researcher explicitly required chronological de-overlap. Greedy keep start>=last retained genuine endpoint excludes exactly59 history origins and leaves zero overlaps. The same thinned history determines EWMA-R2 prefix moments and subsequent updates. Evaluation origins are untouched; ROLL/EXPANDING/EWMA-A/HAR histories are not thinned. R2-versus-A is consequently not a pure variance-conversion ablation: the approved history thinning also differs. R2_history_role_counts.csv and r2_deoverlap_audit.csv expose the precise keys and role counts.
- **B3 GARCH:** BLOCKED_DEPENDENCY. scipy,arch,statsmodels are absent from the existing .venv. No installation was authorized, no ad-hoc replacement optimizer was introduced, and zero GARCH fits/convergence attempts occurred. There is no GARCH score, negative result, EWMA fallback, or claim that the completed study exhausts classical models. GARCH likelihood/optimizer fixtures are N/A because no GARCH implementation executed.
- **B4 HAR-RV-A:** The researcher separately authorized same-source pre2025 full-session closes, including the closing half-hour. Pinned revision776328445b7ac6e7815ef3a483e9c8ded1eb6d56;174 receipt-bound monthly files,2010-07..2024-12. Only projected historical OHLC/timestamps/quality and compatible saved hourly factors/basis/quarantine/count/close fields were read; no minute volume or new source. Full390-position regular days only;389 possible adjacent returns, minimum370 observed pairs; valid incomplete RV is389*sum(r²)/n_pairs. No bridging or fabricated zeros. Early closes do not enter the daily RV history but remain in all original forecast keys. All22-lag windows precede the forecast day. Six fixed predictors: log RV1/meanRV5/meanRV22 and three corresponding missing fractions. Prefix-only stock native-RV median fallback, floor max(median*1e-8,1e-16); conditional stock-slot weighted standardization; fixed ridge.01 on slopes, free intercept, A/s response, nonnegative raw decode. This is direct A regression informed by RV, not canonical next-day HAR-RV and not variance mechanically relabeled as A.

Full source check:27,955,304 projected minute rows,18 quarantined rows,506,520 hourly/stub bins reconciled, zero terminal-close discrepancy at atol/rtol1e-10.3,618 regular days /72,360 stock-days;67,038 (92.6451%) meet RV coverage and51,694 have all389 pairs. Only compact daily RV/coverage is retained, not source minutes. Every original target row survives. Native daily RV has no observed zero values in this footprint.

Missingness is concentrated and not assumed random. Equal-year OOS prior-day missing-RV fractions: AVGO72.4060%, MA37.9899%, AMZN19.7448%; prior22 fractions73.8241%,38.3102%,20.7465%. The HAR stock-prefix fallback is often active for these names, so its aggregate result is not evidence about a uniformly well-observed minute-RV model. Coverage-normalizing incomplete valid days also assumes approximately representative missing pairs; this is an approximation, not source certification of missing-at-random. har_input_coverage.csv,rv_coverage.csv and rv_source_reads.csv retain denominators and source identity.

## Equal-year magnitude and ranking evidence

CAL and UNCAL were fixed arms. Constant IC contributes0; true-pair ties excluded, predicted tieshalf-credit; fractional-boundary top/bottom4, chance0.20. No OOS jitter or favorable tie order. No new arm has a constant-score origin; HAR has a small explicitly reported clamped-zero rate. Positive global calibration multipliers leave all within-origin ranks unchanged, verified directly.

| arm | raw_MSE | raw_MAE | IC | pair_concordance | top4 | ratio |
| --- | --- | --- | --- | --- | --- | --- |
| ROLL20-UNCAL | 0.0001135859129 | 0.0069907645 | 0.3000493706 | 0.6082209902 | 0.4109666891 | 1.014092104 |
| ROLL20-CAL | 0.0001136300531 | 0.006908991774 | 0.3000493706 | 0.6082209902 | 0.4109666891 | 0.9695855957 |
| ROLL60-UNCAL | 0.0001105962474 | 0.006919326454 | 0.3186899781 | 0.6154855776 | 0.4210668469 | 1.027385337 |
| ROLL60-CAL | 0.0001120886527 | 0.007016268636 | 0.3186899781 | 0.6154855776 | 0.4210668469 | 1.052963687 |
| EXPANDING-UNCAL | 0.0001136096836 | 0.006865722737 | 0.3085301471 | 0.6106544137 | 0.4000342723 | 0.9484489463 |
| EXPANDING-CAL | 0.0001139959169 | 0.007141920288 | 0.3085301471 | 0.6106544137 | 0.4000342723 | 1.061665588 |
| EWMA-R2-FN-UNCAL | 0.0001129321412 | 0.007084762077 | 0.3087128935 | 0.6112846878 | 0.4143438681 | 1.071754126 |
| EWMA-R2-FN-CAL | 0.0001123762041 | 0.006916589421 | 0.3087128935 | 0.6112846878 | 0.4143438681 | 0.9987527943 |
| EWMA-A-UNCAL | 0.0001106694416 | 0.006897390934 | 0.3145553383 | 0.6135628232 | 0.4208887995 | 1.017439552 |
| EWMA-A-CAL | 0.0001109304181 | 0.006889857387 | 0.3145553383 | 0.6135628232 | 0.4208887995 | 1.008123867 |
| HAR-RV-A-UNCAL | 0.0001089621997 | 0.006795825375 | 0.3144651797 | 0.6134663322 | 0.4077927428 | 0.9960882607 |
| HAR-RV-A-CAL | 0.0001090681936 | 0.006833967203 | 0.3144651797 | 0.6134663322 | 0.4077927428 | 1.013485619 |
| CLOCK-C3 | 0.0001066659459 | 0.006757093117 | 0.3302540433 | 0.6194433131 | 0.429465854 | 1.013762811 |
| CLOCK-RAW | 0.0001142702891 | 0.006480820201 | 0.3302540433 | 0.6194433131 | 0.429465854 | 0.7772366052 |
| S2C-C3 | 0.0001065481678 | 0.006756096004 | 0.3312359769 | 0.6198189902 | 0.4296407266 | 1.015220833 |
| S2C-RAW | 0.0001139845065 | 0.006474520606 | 0.3312359769 | 0.6198189902 | 0.4296407266 | 0.7783296672 |
| S5C-C3 | 0.0001068490463 | 0.006772348477 | 0.3320459348 | 0.6201762758 | 0.4276809817 | 1.01637554 |
| S5C-RAW | 0.000113656777 | 0.006486732391 | 0.3320459348 | 0.6201762758 | 0.4276809817 | 0.791603536 |
| C0 | 0.000114783568 | 0.006497448339 | 0.3246681015 | 0.6173021171 | 0.4246095608 | 0.7788756444 |
| C3 | 0.0001072269421 | 0.00680102945 | 0.3246681015 | 0.6173021171 | 0.4246095608 | 1.02669511 |
| C1a | 0.000108218653 | 0.006815934794 | 0.3246681015 | 0.6173021171 | 0.4246095608 | 1.018191079 |
| M1 | 0.0001082663992 | 0.00688398945 | 0.3246681015 | 0.6173021171 | 0.4246095608 | 1.052601689 |
| B0-VOL | 0.0001115604213 | 0.007012769595 | 0.3041431609 | 0.6094227002 | 0.4098864948 | 1.027889426 |
| B0-CLOCK | 0.000114669543 | 0.006839084761 | 0.3028002039 | 0.6085286495 | 0.3866813807 | 0.9216707461 |
| B0-RMEAN | 0.0001223644168 | 0.007129612585 | 0.3002382727 | 0.6075409545 | 0.3906921517 | 0.9227510231 |
| B0-RMED | 0.0001380921626 | 0.006949601025 | 0.2961144338 | 0.6061252718 | 0.3741662913 | 0.6277364669 |

## Annual calibrated comparisons

| year | arm | raw_MSE | raw_MAE | IC | top4 |
| --- | --- | --- | --- | --- | --- |
| 2021 | ROLL20-CAL | 8.920650883e-05 | 0.006361258652 | 0.305088668 | 0.3779730243 |
| 2021 | ROLL60-CAL | 8.692453148e-05 | 0.00636017088 | 0.3191925242 | 0.3922998987 |
| 2021 | EXPANDING-CAL | 9.113804061e-05 | 0.006991056287 | 0.3002666359 | 0.374762538 |
| 2021 | EWMA-R2-FN-CAL | 8.673721803e-05 | 0.006260784814 | 0.3133247142 | 0.3854768237 |
| 2021 | EWMA-A-CAL | 8.628876974e-05 | 0.006310118336 | 0.3166558403 | 0.3916223404 |
| 2021 | HAR-RV-A-CAL | 8.471601476e-05 | 0.006426268023 | 0.3171084687 | 0.3780870061 |
| 2021 | CLOCK-C3 | 8.255461312e-05 | 0.006378167537 | 0.326276066 | 0.3971821175 |
| 2021 | S2C-C3 | 8.257578687e-05 | 0.006384710302 | 0.3274607114 | 0.3979388298 |
| 2021 | S5C-C3 | 8.309191526e-05 | 0.00642987544 | 0.3294364541 | 0.3918724671 |
| 2022 | ROLL20-CAL | 0.0001576910306 | 0.00856474023 | 0.3153867026 | 0.4120776644 |
| 2022 | ROLL60-CAL | 0.0001598529837 | 0.0091019385 | 0.3296172233 | 0.4257029478 |
| 2022 | EXPANDING-CAL | 0.0001575824623 | 0.008269038574 | 0.3243752514 | 0.3901417234 |
| 2022 | EWMA-R2-FN-CAL | 0.0001549481417 | 0.008630145404 | 0.3254165103 | 0.4157653061 |
| 2022 | EWMA-A-CAL | 0.0001541671267 | 0.008632703031 | 0.3307781272 | 0.4215362812 |
| 2022 | HAR-RV-A-CAL | 0.0001508891265 | 0.008518703177 | 0.3281932699 | 0.4173469388 |
| 2022 | CLOCK-C3 | 0.0001459095063 | 0.00830866763 | 0.3544509105 | 0.4364937642 |
| 2022 | S2C-C3 | 0.0001457649721 | 0.008314501581 | 0.3517644971 | 0.4336706349 |
| 2022 | S5C-C3 | 0.0001457445656 | 0.008314339851 | 0.3542956386 | 0.4370719955 |
| 2023 | ROLL20-CAL | 8.898803817e-05 | 0.006069693152 | 0.2944770848 | 0.408148714 |
| 2023 | ROLL60-CAL | 8.67859161e-05 | 0.006010269921 | 0.315863317 | 0.4114081996 |
| 2023 | EXPANDING-CAL | 9.270313276e-05 | 0.006825841397 | 0.3063249791 | 0.4020339954 |
| 2023 | EWMA-R2-FN-CAL | 8.76355358e-05 | 0.00603932528 | 0.3063455651 | 0.4161064426 |
| 2023 | EWMA-A-CAL | 8.729007783e-05 | 0.006034577865 | 0.3125542336 | 0.4173860453 |
| 2023 | HAR-RV-A-CAL | 8.743997927e-05 | 0.005988840272 | 0.3111256104 | 0.3903329514 |
| 2023 | CLOCK-C3 | 8.617307336e-05 | 0.005998685915 | 0.3238041506 | 0.420960657 |
| 2023 | S2C-C3 | 8.614824508e-05 | 0.005981576476 | 0.326300734 | 0.4226476954 |
| 2023 | S5C-C3 | 8.599183224e-05 | 0.005978927551 | 0.328670863 | 0.4223644003 |
| 2024 | ROLL20-CAL | 0.0001186346349 | 0.006640275061 | 0.285245027 | 0.4456673535 |
| 2024 | ROLL60-CAL | 0.0001147911797 | 0.006592695242 | 0.310086848 | 0.4548563416 |
| 2024 | EXPANDING-CAL | 0.000114560032 | 0.006481744893 | 0.3031537221 | 0.4331988324 |
| 2024 | EWMA-R2-FN-CAL | 0.000120183921 | 0.006736102186 | 0.2897647846 | 0.4400269002 |
| 2024 | EWMA-A-CAL | 0.0001159756982 | 0.006582030317 | 0.2982331521 | 0.4530105311 |
| 2024 | HAR-RV-A-CAL | 0.000113227654 | 0.006402057341 | 0.3014333697 | 0.4454040751 |
| 2024 | CLOCK-C3 | 0.0001120265908 | 0.006342851385 | 0.3164850461 | 0.4632268773 |
| 2024 | S2C-C3 | 0.0001117036674 | 0.006343595656 | 0.3194179649 | 0.4643057463 |
| 2024 | S5C-C3 | 0.0001125678721 | 0.006366251066 | 0.3157807834 | 0.4594150641 |

All six CAL arms are worse than CLOCK and S2C in equal-year MSE and IC. HAR-CAL annual CLOCK MSE excesses are2.6181%,3.4128%,1.4702%,1.0721%. Raw inverse sensitivity and all original controls are in metrics.csv; all years and all conditional scopes are retained, with no pooled-row replacement for equal-year scores.

## Paired descriptive uncertainty

400 whole-calendar-month draws,seed22042, independently resampled within each annual fold and equally averaged across years. Entire sessions/stock panels/overlapping origins remain together. Positive MSE delta is worse; positive IC delta is better. These intervals condition on fitted/calibrated models and previous repeated development, not selection-adjusted or independent confirmatory inference.

| left | right | metric | delta | low | high | percent |
| --- | --- | --- | --- | --- | --- | --- |
| ROLL20-CAL | CLOCK-C3 | raw_MSE | 6.964107248e-06 | 5.476907564e-06 | 8.509890589e-06 | 6.528894663 |
| ROLL20-CAL | CLOCK-C3 | IC | -0.03020467272 | -0.03526426466 | -0.02531019842 | -9.145890363 |
| ROLL20-CAL | S2C-C3 | raw_MSE | 7.081885291e-06 | 5.642887893e-06 | 8.552903502e-06 | 6.646651401 |
| ROLL20-CAL | S2C-C3 | IC | -0.03118660627 | -0.03632429128 | -0.02570126937 | -9.415223119 |
| ROLL60-CAL | CLOCK-C3 | raw_MSE | 5.422706857e-06 | 3.426835491e-06 | 7.957119097e-06 | 5.083822031 |
| ROLL60-CAL | CLOCK-C3 | IC | -0.01156406518 | -0.01695634217 | -0.006442087095 | -3.501566571 |
| ROLL60-CAL | S2C-C3 | raw_MSE | 5.540484899e-06 | 3.467112646e-06 | 8.156232209e-06 | 5.19998139 |
| ROLL60-CAL | S2C-C3 | IC | -0.01254599873 | -0.01796565227 | -0.007498710744 | -3.787631661 |
| EXPANDING-CAL | CLOCK-C3 | raw_MSE | 7.32997105e-06 | 5.408987846e-06 | 9.499536079e-06 | 6.871894295 |
| EXPANDING-CAL | CLOCK-C3 | IC | -0.02172389619 | -0.02814276625 | -0.01562110235 | -6.577934967 |
| EXPANDING-CAL | S2C-C3 | raw_MSE | 7.447749093e-06 | 5.587591389e-06 | 9.570480498e-06 | 6.990030184 |
| EXPANDING-CAL | S2C-C3 | IC | -0.02270582975 | -0.02901404299 | -0.01678922344 | -6.854880307 |
| EWMA-R2-FN-CAL | CLOCK-C3 | raw_MSE | 5.710258252e-06 | 4.122627106e-06 | 7.244702123e-06 | 5.353403286 |
| EWMA-R2-FN-CAL | CLOCK-C3 | IC | -0.02154114978 | -0.0262848729 | -0.01655718556 | -6.522599863 |
| EWMA-R2-FN-CAL | S2C-C3 | raw_MSE | 5.828036295e-06 | 4.254424071e-06 | 7.317150819e-06 | 5.469860639 |
| EWMA-R2-FN-CAL | S2C-C3 | IC | -0.02252308333 | -0.02749728229 | -0.01726044691 | -6.799709241 |
| EWMA-A-CAL | CLOCK-C3 | raw_MSE | 4.264472227e-06 | 2.91694704e-06 | 5.481947346e-06 | 3.997969728 |
| EWMA-A-CAL | CLOCK-C3 | IC | -0.01569870502 | -0.02017193159 | -0.01080069145 | -4.753523943 |
| EWMA-A-CAL | S2C-C3 | raw_MSE | 4.382250269e-06 | 3.038399628e-06 | 5.561362334e-06 | 4.112928789 |
| EWMA-A-CAL | S2C-C3 | IC | -0.01668063857 | -0.02101197574 | -0.01153295764 | -5.035877664 |
| HAR-RV-A-CAL | CLOCK-C3 | raw_MSE | 2.402247762e-06 | 1.25861975e-06 | 3.89824963e-06 | 2.252122495 |
| HAR-RV-A-CAL | CLOCK-C3 | IC | -0.01578886362 | -0.02426419744 | -0.008932868494 | -4.780823713 |
| HAR-RV-A-CAL | S2C-C3 | raw_MSE | 2.520025804e-06 | 1.383954336e-06 | 3.986071077e-06 | 2.365151701 |
| HAR-RV-A-CAL | S2C-C3 | IC | -0.01677079717 | -0.02452210883 | -0.01022117447 | -5.063096505 |

HAR-CAL vs CLOCK annual MSE intervals:

| year | delta | low | high | percent |
| --- | --- | --- | --- | --- |
| 2021 | 2.161401641e-06 | 1.036218799e-06 | 3.45753505e-06 | 2.618147623 |
| 2022 | 4.979620254e-06 | 9.115426064e-07 | 1.026609386e-05 | 3.412814134 |
| 2023 | 1.266905914e-06 | -6.574134608e-07 | 3.583693399e-06 | 1.470187687 |
| 2024 | 1.201063238e-06 | -1.822961984e-07 | 2.524145922e-06 | 1.07212335 |
| EQ | 2.402247762e-06 | 1.25861975e-06 | 3.89824963e-06 | 2.252122495 |

paired_differences.csv also reports every classical CAL vsS5C/ROLL20-CAL, every UNCAL vsCLOCK/S2C/S5C-RAW/ROLL20-UNCAL, and each own CAL-vsUNCAL, for MSE/IC/concordance/top4 and both actual schedule categories. No OOS comparator was selected for fitting.

## Calibration, tails, clock and stock interpretation

Own past-only global k= max(0,sum(w*A*UNCAL)/sum(w*UNCAL²)), with canonical cal weights. All24 coefficients are finite positive; all denominators positive. Both calibration and forecast paths replay. Maximum top10 contribution to the calibration numerator is8.3215%, maximum top1%16.2070%; no trimming or new conditional correction. F24's40-session independent calibration tail is smaller and is disclosed. Classical regression/fixed-state parameters never update from cal/OOS labels; only dynamic latent histories update after maturity.

| year | ROLL20 | ROLL60 | EXPANDING | EWMA-R2-FN | EWMA-A | HAR-RV-A |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | 0.8896567159 | 0.9276010596 | 1.192925959 | 0.8484422015 | 0.9240340726 | 1.026010843 |
| 2022 | 0.9444569487 | 1.138651528 | 1.133724431 | 0.9682466161 | 1.018450577 | 1.065574514 |
| 2023 | 0.9522066752 | 0.926486184 | 1.183350924 | 0.9105096161 | 0.9580442267 | 0.9539488692 |
| 2024 | 1.046316555 | 1.073038979 | 0.970322523 | 0.9887281834 | 1.056249874 | 1.007685626 |

HAR-CAL and EWMA-A-CAL have lower conditional realized95/99 tail MSE than CLOCK, but worse ordinary-complement error and weaker event retrieval. For HAR, prefix95/99 top4 recall0.531405/0.635104 versus CLOCK0.553064/0.675660; false-low rates0.176754/0.170625 versus0.169008/0.126699. Conditional realized-tail underprediction alone does not establish conditional-mean miscalibration. No tail result was used to change a model or calibrator.

| arm | group | raw_MSE | raw_MAE | ratio | raw_MSE_loss_share |
| --- | --- | --- | --- | --- | --- |
| EWMA-A-CAL | PREFIX95 | 0.001103918682 | 0.02781897162 | 0.3752474668 | 0.5511809844 |
| EWMA-A-CAL | LE_PREFIX95 | 5.323753711e-05 | 0.005643349773 | 1.220410136 | 0.4488190156 |
| EWMA-A-CAL | PREFIX99 | 0.003856854364 | 0.05743269138 | 0.2430908189 | 0.3118174745 |
| EWMA-A-CAL | LE_PREFIX99 | 7.713753716e-05 | 0.006428693845 | 1.063633531 | 0.6881825255 |
| HAR-RV-A-CAL | PREFIX95 | 0.001104584476 | 0.02779028268 | 0.3758111336 | 0.557026042 |
| HAR-RV-A-CAL | LE_PREFIX95 | 5.16682097e-05 | 0.005592589093 | 1.2266041 | 0.442973958 |
| HAR-RV-A-CAL | PREFIX99 | 0.00385994203 | 0.05731470871 | 0.2446457202 | 0.3185440189 |
| HAR-RV-A-CAL | LE_PREFIX99 | 7.509974166e-05 | 0.006372110946 | 1.069263834 | 0.6814559811 |
| CLOCK-C3 | PREFIX95 | 0.001139785797 | 0.02859071722 | 0.3578697988 | 0.5891801902 |
| CLOCK-C3 | LE_PREFIX95 | 4.682141169e-05 | 0.005455355283 | 1.232713967 | 0.4108198098 |
| CLOCK-C3 | PREFIX99 | 0.003944421224 | 0.05824463448 | 0.2323901679 | 0.332966115 |
| CLOCK-C3 | LE_PREFIX99 | 7.188615454e-05 | 0.006284977493 | 1.070417055 | 0.667033885 |
| S2C-C3 | PREFIX95 | 0.001135728151 | 0.02850488814 | 0.3597903497 | 0.5870787812 |
| S2C-C3 | LE_PREFIX95 | 4.701508231e-05 | 0.00546119801 | 1.233956565 | 0.4129212188 |
| S2C-C3 | PREFIX99 | 0.003934708747 | 0.05815365769 | 0.2335891569 | 0.3321695627 |
| S2C-C3 | LE_PREFIX99 | 7.189297585e-05 | 0.00628520784 | 1.071866201 | 0.6678304373 |

Both intraday and overnight HAR-CAL MSE/IC remain worse than CLOCK. Seven slots, early-close versus normal dates, all20 stocks, months, shared descriptive C0-score deciles, tail complements/contributions and rank/recall tables are in groups.csv,rank_groups.csv,stock_diagnostics.csv,tail_retrieval.csv. Small early-close cohorts are flagged by explicit row/origin/session counts; these slices are descriptive, not selection gates. The historical C0 decile boundaries use comparator scores only, never outcomes, and are shared by all arms.

Centered cross-sectional score static-variance fractions average about83.93% forROLL60-CAL,74.73% forHAR-CAL,77.15% forCLOCK,77.47% forS2C. B0-RMEAN is100% by construction. These are output-variance descriptions, **not fractions of predictive accuracy explained by a stock prior**. The original A task remains unchanged; no anomaly-target fitting or post-hoc baseline was added.

## Verification, failure trace and reproducibility

TECHNICAL_PASS for all completed families: exact keys/labels/weights and endpoint identity; all20 DesignA masks/48-step boundaries; all calibration formulas; all rolling forecasts independently recomputed without cumulative subtraction; all HAR predictions replayed from stored coefficients without fitting;336 EWMA examples independently replayed using closed-form discounted sums; every dynamic forecast's latest mature timestamp checked; all174 minute hashes and explicit predecessor bindings preserved.13 frozen reference arms exactly reproduce archived annual/equal-year category MSE/MAE/IC/top4. verification.json/comparator_parity.json contain receipts; forecast_update_examples.csv includes actual early-close and overnight cases.

A completion-logger implementation error occurred **after F21 numerical artifacts were saved**: duplicate year/status keywords. execution.log and the FAILED journal entry remain. No OOS performance had been scored. The fix changes logging/recovery flow only; all numerical function ASTs are identical. F21 artifacts were hash-frozen and remain byte-identical. The guarded --resume-unstarted path ran onlyF22–F24, once each; no optimizer/model/calibrator retry, no new namespace, no scientific protocol edit. logging_failure_preservation.json,logging_recovery_final.json and logging_fix_final.diff document the correction. Exact F21 runtime/peak telemetry was not persisted because of the logger error; the resource-ceiling check had passed before that error. Later measured fit-process peak554,811,392bytes; preflight458,260,480bytes; all below2GB. The F22–F24 resume segment took15.159s; do not mislabel that as a complete four-fold runtime.

Classical counts:560 HAR stock-slot regressions;560 EWMA-R2 stock-slot mean/variance parameter sets and560 EWMA-A seed sets;24 global multipliers; three unfitted rolling arithmetic families. No candidate search, no GARCH fit, no neural calls/starts. Ledger and registry unchanged **186/300**. Resources stay below2.5GB task/15GB project; final_integrity.json gives final bytes.18 focused tests pass; Ruff passes; installed Pylance/basic533project-owned files zero errors/warnings. Human VSCode Problems refresh remains outstanding, not claimed. Arrow sysctl cache warnings are nonfatal environment notices.

Authoritative executed sources: Session2B amendment.json and role_counts.csv (there is no protocol.json in that successor folder), O1 role_indices.npz and phase recipes; S4 source policy/read receipt/genuine endpoints; original S9_TARGET_AND_BASELINE_CONTRACT.md; S2B-CLOCK and S2C saved scores; Stage5 A/B ranking-only archives and S5C final saved magnitude scores. The requested HF20_S9_MAG_Stage1_Session2_Codex_DesignA_B0_C1_Fitting_Prompt_2026-10-27.md was not found in the inspected docs/reports/config paths; binding definitions were recovered from executed assets. Relevant methodological/consolidation handoff sections were inspected; their original December-history scales were not substituted for September DesignA scales. S2-D is a different gap target and is excluded from all four-hour loss comparisons. S5-A/B are rank-only and receive no magnitude-MSE fiction.

Completed commands (never repeat fit/source commands in this namespace):

```sh
.venv/bin/python -u -B -m lstm_data.hf20_classical --prepare
.venv/bin/python -u -B -m lstm_data.hf20_classical --run
# One recorded logging recovery only; cannot rerun once its journal advances:
.venv/bin/python -u -B -m lstm_data.hf20_classical --resume-unstarted
# Saved-score report replay only: no model/calibration fit or neural inference:
.venv/bin/python -B -m lstm_data.hf20_classical --report
.venv/bin/python -m pytest tests/test_hf20_classical.py tests/test_hf20_mag_rank.py tests/test_hf20_stage2_bcd.py -q
.venv/bin/ruff check src/lstm_data/hf20_classical*.py tests/test_hf20_classical.py --output-format concise
.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-Pylance-extension>/dist
```

The daily-RV compact derivative and four combined keyed score stores avoid duplicating source/targets once per model. All selectors/calibration/source paths, fitted constants and hashes are retained. Dependencies/environment/previous code/results/dashboard were not changed; no network,fetch,commit,push,2025 market or protected2026 content/path/hash access. Published source timing/action and fixed-survivor limitations remain. User-supplied method references are definition/context only; no external pages were fetched: [Bollerslev1986](https://doi.org/10.1016/0304-4076(86)90063-1), [Corsi2009](https://doi.org/10.1093/jjfinec/nbp001), [RiskMetrics1996](https://www.msci.com/documents/10199/5915b101-4206-4ba0-aee2-3449d5c7e95a).

## Researcher decision and STOP

The completed classical families explain substantial persistent risk ordering and improve over the static prior. The preserved calibrated LSTM packages retain incremental aggregate magnitude/ranking evidence on this exact sample; HAR narrows the MSE gap most, ROLL60 narrows the ranking gap most. Tail and calibration-neutral results prevent a universal “LSTM wins every criterion” conclusion. GARCH remains untested, HAR coverage is stock-dependent, and these post-search years cannot establish that a recurrent architecture is necessary or economically useful.

Review this partial study and its limitations. Any GARCH environment change/new execution, richer classical model, model promotion, blend, strategy, protected release or next stage requires a separate researcher decision. **STOP: no further fits or autonomous follow-up.**
