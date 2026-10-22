# HF20 Package017 — researcher diagnosis

## Key conclusions

Both approved seed123 pairs completed. C0 MSE=3.4794399066; T2=3.4759127879; ZERO=3.4745059908.
T2−C0 MSE=-0.0035271187, compared with seed42 -0.0032125891: the same direction.
Selected seed123 epochs: C0=1, T2=1.
These facts address initialization and session-order sensitivity; two seeds do not prove invariance,
market significance, data-history effects or model-family promotion. Exact matched366 origins /
183 days /7320 stock forecasts are retained for every model. ZERO's rank IC is undefined.

| seed | arm | MSE | MAE | Rank_IC | score_std |
| --- | --- | --- | --- | --- | --- |
| 42 | C0 | 3.4783150611826104 | 1.2658516470643137 | 0.015875754961173424 | 0.05056131765345306 |
| 42 | T2 | 3.4751024720779555 | 1.265187522300381 | 0.023221989399728832 | 0.04036604585766228 |
| 42 | ZERO | 3.4745059908061524 | 1.2647920105702217 | nan | 0.0 |
| 123 | C0 | 3.4794399066014856 | 1.266220140368681 | 0.021052631578947364 | 0.06556206003890631 |
| 123 | T2 | 3.4759127879099214 | 1.265011445646905 | 0.0319610501663996 | 0.05036579909312826 |
| 123 | ZERO | 3.4745059908061524 | 1.2647920105702217 | nan | 0.0 |

## Optimization and selection

C0: qualifying epoch 1, raw minimum epoch 1, calibration 12 epochs, stop PATIENCE_STOP; validation 3.2953873374 → 3.3446110119. Fresh refit exactly 1 epochs.
T2: qualifying epoch 1, raw minimum epoch 1, calibration 12 epochs, stop PATIENCE_STOP; validation 3.2906436573 → 3.3062740673. Fresh refit exactly 1 epochs.

The selector monitors original-TG20 inner-validation MSE, with eval-mode dropout disabled;
only a strict new value below0.999×the prior qualifying best resets patience. Raw minima and
nonqualifying improvements remain visible in epoch_selection_trace.csv. Minimum12 limits
stopping time, not the earliest selectable checkpoint. The inner tail is exactly63 exchange
sessions,55 eligible days/110 origins, not a random sample. Refit starts a fresh same-seed
model and empty optimizer on the full prefix, using its distinct train-only recipe.

C0 fitting objectives use TG20 squared units; T2 uses asinh(TG20/s) squared units. Compare
canonical validation/development metrics across arms. Online fitting MSE was accumulated with
changing weights and dropout ON, so it is not end-of-epoch evaluation. Complete epoch/batch
gradient quantiles and actual cap fractions are saved for both passes and seeds. Finite G6
does not establish useful signal. Historical per-example gradients, dropout masks and optimizer
internals are NOT_RECORDED; no later-epoch trajectory is reconstructed from absent weights.

## Forecast amplitude, alignment and calibration

| seed | arm | MSE | prediction_mean | prediction_sd | covariance | E_prediction2 | E_y_prediction | delta_MSE_vs_ZERO |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | C0 | 3.4783150611826112 | 0.008325109593672018 | 0.05714812773249544 | -0.00011521034534736747 | 0.0033352159530762654 | -0.0002369272116905723 | 0.003809070376458834 |
| 42 | T2 | 3.475102472077958 | 0.013627063095054341 | 0.04609713412005842 | 0.0010563144991766406 | 0.0023106426226792475 | 0.0008570806754379252 | 0.0005964812718057821 |
| 42 | ZERO | 3.4745059908061524 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 123 | C0 | 3.4794399066014883 | -0.012905628569017022 | 0.08284820888734729 | 0.0008595464598535448 | 0.007030380964602944 | 0.0010482325846349063 | 0.004933915795335864 |
| 123 | T2 | 3.4759127879099236 | -0.0201634375160181 | 0.0633233518688443 | 0.0012100084271946293 | 0.004416411104367836 | 0.0015048070002995659 | 0.001406797103771229 |
| 123 | ZERO | 3.4745059908061524 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

The exact equal-day→origin→stock identity is MSE(pred)−MSE(ZERO)=Ew[pred²]−2Ew[y·pred].
Pooled mean, variance and covariance components are separate from per-origin cross-sectional
IC. A small but variable forecast is not strict collapse. Near-zero squared-loss predictions
can be rational when the accessible conditional mean is weak; this does not identify the true
conditional mean. Stock/month/origin contribution tables, sign accuracy and pairwise concordance
are descriptive. Score quintiles are ex-post calibration summaries, never a fitted correction.
No development intercept, rescaling, event threshold or new predictor was fitted.

## Tails and context

Training-only |TG20| q99=6.5085057545; 78/7320 event rows across
51 development days. Same event IDs are compared between seeds in
same_tail_event_seed_comparison.csv. Tail tables preserve original returns, peer median,
unscaled MAD and train-fitted epsilon. Large numerators and small denominators are separated;
no outlier was removed or denominator inflated. Rare stock-specific moves can be real information.
Worst1/5/10% day loss shares and post-hoc top4 absolute-score precision/recall/sign accuracy
are in tail_concentration.csv and tail_event_metrics.csv, with event base rates. These are not
validated event classifiers; train forecast magnitude thresholds are NOT_AVAILABLE.

Seed-disagreement tables compare stock, month, origin and the actually observable final-step
train-scaled V2 context against a training-only median. An additional clearly marked ex-post
outcome-dispersion split is descriptive and never enters features or decisions. Group clustering
does not establish a causal regime effect;20 correlated stocks and two overlapping horizons
are not7320 independent trials. No issuer-news or vendor-error cause is inferred from a tail.

## Exploratory uncertainty

| contrast | metric | estimate | lower95 | upper95 |
| --- | --- | --- | --- | --- |
| S123_T2_minus_C0 | MSE | -0.003527118691564399 | -0.00699318903947576 | 0.00023186707394337404 |
| S123_T2_minus_C0 | Rank_IC | 0.010908418587452236 | -0.003385615678540616 | 0.021172295492830426 |
| S42_T2_minus_C0 | MSE | -0.0032125891046541136 | -0.00507084371783128 | -0.0010925435376858148 |
| S42_T2_minus_C0 | Rank_IC | 0.007346234438555405 | -0.005558979415752492 | 0.01633232671843543 |
| C0_S123_minus_S42 | MSE | 0.0011248454188757325 | -0.012386057886355273 | 0.011924073766938737 |
| C0_S123_minus_S42 | Rank_IC | 0.005176876617773947 | -0.04679454784502238 | 0.06250195160031223 |
| T2_S123_minus_S42 | MSE | 0.0008103158319654469 | -0.010930539841372093 | 0.009752972891736562 |
| T2_S123_minus_S42 | Rank_IC | 0.008739060766670772 | -0.04089640083816097 | 0.06335551994740944 |

Same established five-session moving blocks,5000 resamples, seed8008; blocks cannot bridge
omitted exchange sessions. Calendar positions are retained. Intervals compare seed123 T2−C0,
each arm seed123−42 and the seed42 contrast. **Exploratory, reused development, not fully
selection-adjusted G8; no new significance, independent-market-history or alpha claim.**

## Ranked explanations and counterarguments

| rank | hypothesis | status | evidence | counterargument |
| --- | --- | --- | --- | --- |
| 1 | Weak accessible conditional mean in this fixed setup | SUPPORTED | Seed123 ZERO MSE=3.4745059908; C0=3.4794399066, T2=3.4759127879; exact alignment decomposition saved. | Observed skill under this model/sample is not proof the true conditional mean is zero. |
| 2 | Optimization generalization gap / overfitting | PLAUSIBLE | Full qualifying/raw-minimum traces and online objectives saved; selected epochs={'C0': 1, 'T2': 1}. | Online dropout-ON losses are not fixed-weight eval curves; chronology/source shifts can also matter. |
| 3 | Insufficient regime diversity / too little history | NOT_IDENTIFIABLE | Both seeds reuse exactly the same 998 training and 366 development origins. | No longer-history contrast ran. More correlated history need not improve prediction. |
| 4 | Tail targets materially concentrate loss | SUPPORTED | Training |TG20| q99=6.5085057545; 78 development events; denominator and worst-day shares saved. | Concentrated loss does not establish invalid labels or that clipping/MAD inflation would improve generalization. |
| 5 | Nonfinite optimizer / deterministic seed-stage-target defect | REFUTED_IN_CHECKED_BOUNDARY | Independent stage audits verify exact canonical replay, train-only scales, full masks, D6g and checkpoint identities. | Checks do not certify unrecorded optimizer internals or every upstream vendor fact. |
| 6 | Source/publication/action assumptions explain weakness | PLAUSIBLE | As-reported retrospective survivor sample and idealized hourly-close clock remain conditional. | No independent corrected-source contrast, action vintage or publication facts establish a causal explanation. |

Potential next hypotheses remain proposals: source-consistent longer-history feasibility,
or a separately preregistered signed-tail/rank-aware objective preserving canonical TG20 and
all tails. The seed test neither authorizes these nor selects one automatically. ZERO winning
does not by itself show a broken model. Keep weak and negative results.

## Scope and reproducibility

Ledger32/200, two charged starts; source/input/older model preservation verified separately.
Source is ASSUMPTION_CONDITIONAL, researcher-attested bounded local use, retrospective survivor
selection, uncertified issuer/action/PIT/dividend/publication facts and idealized vendor-clock /
hourly-close proxies. No real fills, profitability, independent rights certification, bulk export,
held-out/old confirmation access, trading, source GET, further fit or Git operation.

Inspect run directories for raw epoch telemetry, both safe checkpoints and independent eval-only
replay receipts. The existing explorer exposes both seeds and full-fold metrics independently
of chart date filters. Follow docs/track_a/HOW_TO_VIEW_HF20_SEED123_REPLICATION.md.
