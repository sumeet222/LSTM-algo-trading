# HF20 Package 016 — what the two models learned

**HF20_P016_DIAGNOSIS_COMPLETE.** Zero new fits/optimizer steps; ledger 30/200 unchanged.
Same366 development origins×20 names/183 sessions. HF20 held-out2026-01-07 through2026-10-15
and old five-stock confirmation remain locked. **NO DETERMINISTIC DIVERGENCE FOUND** in
bounded B3–B5 replay; the observed weakness is at **B5: score–outcome alignment**. That
is an empirical symptom, not proof every vendor fact or historical training calculation is correct.

## Why epoch 1?

C0: optimizer objective 3.6614445360 → 3.5750141365; 11/11 adjacent changes decrease. Canonical inner-validation MSE 3.2945880196 → 3.3727396185. Selected qualifying epoch 1, raw minimum at1; stop=PATIENCE_STOP, patience=11.

T2: optimizer objective 1.3174404660 → 1.2857217722; 11/11 adjacent changes decrease. Canonical inner-validation MSE 3.2926493558 → 3.3143952456. Selected qualifying epoch 1, raw minimum at2; stop=PATIENCE_STOP, patience=11.

T2 epoch 2 raw improvement=0.001536386663, or0.04666111%, genuinely positive but below
0.1%. It required new MSE<3.289356706446; actual=3.291112969138. No rounding tie. Minimum12
limits when stopping may occur, not the earliest selectable checkpoint. Both refits were
fresh, exactly 1epoch. Inner validation uses the last63exchange-calendar sessions from
2024-12-26, with 55eligible days/110 origins; inner training ends2024-12-24. Development
never chose epochs. Separate inner/refit recipes and mature-label purge checks pass.

Falling fitting objectives with worsening validation are **consistent with overfitting /
NO_VALIDATION_GAIN**, not a unique causal diagnosis. Training MSE was recorded online with
changing weights/dropout ON, not end-of-epoch eval. C0 optimizer loss is TG20 squared;
T2 is squared asinh(TG20/s), not directly comparable. Later epoch 2–12 weights were not saved,
so later output/head contraction cannot be reconstructed or fixed by simulating more epochs.

## Why ZERO is competitive

Exact equal-day→origin→stock identity: ΔMSE=Ew[score²]−2Ew[y×score]. Original results reconcile
to 2e−12 and algebra to 3e−15; no difficult rows were intersected away.

|arm|MSE|prediction_mean|prediction_sd|E_prediction 2|E_y_prediction|delta_MSE_vs_ZERO|
|---|---|---|---|---|---|---|
|C0|3.4783151|0.0083251096|0.057148128|0.003335216|-0.00023692721|0.0038090704|
|T2|3.4751025|0.013627063|0.046097134|0.0023106426|0.00085708068|0.00059648127|
|ZERO|3.474506|0|0|0|0|0|

Target mean=-0.01462045, pooled SD=1.86394534.
Small variable scores are **not strict collapse**. Under squared loss, near-zero is rational
when the conditional mean is weak; this sample cannot establish the true conditional mean.
C0 forecast energy is not repaid by alignment (its pooled covariance is slightly negative).
T2 alignment nearly repays its forecast variance, but a positive forecast mean opposes the
slightly negative target mean. Its exact mean/bias contribution to the ZERO gap is
0.000584164, versus variance−2 covariance
0.000012317. No development intercept correction or
rescaled predictor was fitted. Descriptive covariance/variance slope and post-hoc score-bin
E[y|score] are analysis only. Median-centering each20 stock cross-section does not force its
mean to zero. Pooled variance and average WITHIN-origin variance are different statistics.

## Small rank signal is not validated predictive usefulness

Daily cross-sectional IC=0.015876/0.023222; pooled Pearson and
within-origin ranks measure different relationships. ZERO's defined-only Spearman is undefined;
project-zero is a convention. Pairwise concordance/sign accuracy remain close to chance.
Unchanged exploratory five-session blocks give ΔICinterval
[-0.005558979415752492, 0.01633232671843543]; mean IC around numerical0(not ZERO forecast IC):
C0[-0.0216083240889108, 0.043157175726200744], T2[-0.01819764575372858, 0.04830149143350178]. ΔMSE interval=[-0.00507084371783128, -0.0010925435376858148].
These are **EXPLORATORY_NOT_SELECTION_ADJUSTED**, not fullG8 or a temporal null. One seed,
prior development-guided choices,20 correlated names and overlapping four-hour outcomes
limit independence;7320 rows do not mean7320 independent trials or prove alpha/profitability.

T2 improves MSE on 102/183 days and16/20 stocks. The five largest
positive day gains supply17.14% of positive gain mass; AMD supplies
14.61% of net equal-stock gain (offsetting stocks can make a net share exceed100%).
Both-origin, month and tail/non-tail contrasts remain in paired_origin_stock_month.csv;
no favorable subgroup replaces the primary comparison.

## Rare events: preserve information, diagnose the numerator and denominator

Training pooled|TG20|q99=6.50850575. These events contribute
25.87% /25.87% of C0/T2 development
squared error on 78 stock observations. Full permitted target arithmetic is
independently exact; see tail/ordinary MAD, MAD/epsilon, raw numerator and floor-dominance
summaries plus12 bounded ex-post examples. Numerator/MAD attribution uses training q95/q05
flags, not a fitted predictor. A large stock-specific move against low peer dispersion can
be genuine, useful event information; large TG20 alone is not a defective normalization.
Of78 q99events, 62 meet only the large-numerator flag;
7 meet both numerator/
small-MADflags. Development floor-dominance fraction is0.0%: no MAD≤epsilon case.
There is no automatic floor increase, clipping, winsorization or tail deletion recommendation.

|arm|events|event_sign_accuracy|event_top4_magnitude_recall|top4_magnitude_precision|
|---|---|---|---|---|
|C0|78|0.51282051|0.37179487|0.019808743|
|T2|78|0.5|0.38461538|0.020491803|

Top4 absolute-score selection is a **post-hoc development rank diagnostic**, not a validated
event classifier. Full training forecast magnitudes were not saved; a training-derived
absolute score threshold/precision–recall operating point is **NOT_AVAILABLE**. No external
news cause is asserted for extreme rows. Target/feature period shifts are descriptive,
not iid significance or proof of harmful concept drift. All event labels remain EX-POST,
absent from X; no event cutoff enters a live model.

## Ranked diagnosis, with counterarguments

|rank|status|assessment|counterargument|
|---|---|---|---|
|1|SUPPORTED|Weak stable FT1→TG20 conditional mean: tiny covariance, small forecasts, no qualifying validation gain after1.|Positive rank IC and one seed/55 validation days leave signal and seed noise unresolved. Paired seed replication is the cheapest discriminator.|
|2|CONFIRMED symptom / SUPPORTED interpretation|Fitting loss falls while validation worsens; consistent with overfitting or unstable/low conditional signal.|Online training loss is not end-epoch eval. Later weights are unavailable. This does not uniquely identify noise, representation or sample insufficiency.|
|3|SUPPORTED|Unanticipated stock-specific tails spend substantial MSE; rank and magnitude objectives reward different behavior.|Exact target arithmetic and finite denominators do not establish a defect. Preserve events; separately test signed-tail/rank objectives.|
|4|PLAUSIBLE / NOT_IDENTIFIABLE cause|Descriptive shifts and coverage conditioning may affect transfer; source action/publication/PIT facts remain uncertified.|Measured drift does not prove harmful concept drift or vendor error. No source/news causal claim is supported.|
|5|NOT_SUPPORTED in tested boundary|Strict constant collapse, wrong inverse and exploding-gradient explanations conflict with variable finite outputs, G6 and bounded exact replay.|Synthetic capability is not market predictability; historical dropout, per-example gradients and later weights are missing.|
|6|NOT_IDENTIFIABLE|Capacity, update budget and limited regimes could contribute.|Worsening inner validation and healthy gradients do not justify widening, forced epochs or a lower-rate rescue. No search is authorized.|

G6 raw telemetry confirms no sustained clipping/nonfinite gradients. Bounded CPU float32eval
replay matches saved predictions, with unchanged states/no gradients; hidden variation,
head norms versus recorded initialization and saturation proxies are in the detailed training
report. This rejects strict constant collapse in tested examples, not low signal generally.
Final head norms
retain 95.08% /
93.36% of initial norms;
they did not vanish.
Historical per-example gradients, dropout masks, optimizer internals and later weights are
**NOT_RECORDED**. Source/feature readiness and coverage conditioning are not random by decree:
train998/1154, inner872/1028, validation 110/126, development366/382. Unique admitted-window
feature summaries flag missing/constant/extreme scale changes without changing scalers.
Measured drift and source limitations cannot be assigned a causal performance contribution here.

## Highest-information next controls — proposals only

No pair or acquisition is authorized. Measured prior neural fitting23.35–86.52 seconds/pair
reflects12 calibration+1 refit epochs and different host load, not a causal T2 speed benefit.
If selected epochs differ,60+60epochs could require several minutes/pair; setup/audit walls
are extra. Hypotheses, coefficient/metric, seed/fold and go/no-go must be fixed before fitting.

|priority|hypothesis|change|evaluation|budget|decision|
|---|---|---|---|---|---|
|1|Seed sensitivity|Repeat C0/T2 at preregistered seed 123 only; fixed20 names, FT1/TG20, masks, dates, D6 g.|Paired daily IC/MSE, all results; reused development, not confirmation.|2 unapproved pairs; observed-shape47–173 neural seconds, longer if epochs differ.|Stable gain supports more evidence; seed reversal weakens the T2 claim.|
|2|Missed rare-event direction|One fixed signed-tail auxiliary term on T2; retain canonical TG20 and all tails.|Frozen T2 comparator; separately inner/refit training-only thresholds, fixed coefficient/seed/fold; TG20 MSE/ICplus event-direction precision/recall.|1 treatment pair,2 if new matched control needed; observed-shape23–173 seconds.|Require preregistered event discrimination without hiding magnitude/rank costs.|
|3|Rank/magnitude mismatch|One fixed pairwise auxiliary loss on T2, same architecture/input/canonical target.|Frozen matched T2, fixed seed/fold, preregistered coefficient/ICmetric and TG20 MSE guard; no lambda search or development threshold tuning.|1 treatment pair,2 with fresh control; same conditional measured-shape range.|Small/unstable ICgain is no-go; economics remains a separate task.|
|4|Training-panel composition|Predetermined source-consistent5 vs20 training rows; fixed20 name TG20 labels/scalers.|Both evaluated on common 5 names/dates, same target; subset fixed before new outcomes. New source/history would first require rights/source audit.|2 fresh matched pairs preferred;47–173 seconds is only rough observed-shape context.|Isolates training-panel effect; never compare old five-stock TG0 MSE.|

Capacity escalation and automatic tail suppression are not prioritized by these observations.
Reused development cannot become pristine confirmation. Source-consistent history expansion
is conditional on a separate source/rights/methodology task, not a download instruction.

## Limits and actual visual review

**ASSUMPTION_CONDITIONAL:** retrospective surviving cohort/static source-sector mixture;
issuer/action/adjustment vintage/dividends/publication/PIT facts uncertified; bounded
researcher-attested local use, no independent licensing or sharing authorization; idealized
as-reported timing/hourly-close proxy, no actual fills or economics. No old-five-stock MSE
comparison or panel-size gain is claimed. No protected numerical application rows, new
provider requests, scaler/T2 recalibration or optimization updates.

Read docs/track_a/HOW_TO_VISUALLY_REVIEW_HF20_DIAGNOSIS.md for four exact saved development
IDs and the epoch 1 view. Existing views suffice; new comparison plots are compact CSVs/chart
specifications only. No UI code change, fabricated screenshot, retraining or promotion follows.
