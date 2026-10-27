# S9 target and baseline contract — proposed, no new fits

All three arms use original S4 FT16 only, fixed 20-stock order, 48 steps, exact seven-origin 240-RTH-minute source/endpoint convention, S4 F21–F24 masks, maturity, 48-step embargo and hierarchical weights. Inner/refit FT16, epsilon and T2 scales are reused from the eight sealed S4 recipes, without refitting or importing S5 metadata. Historical numeric thresholds from old populations are not transplanted into new folds.

## Historical definitions recovered and reconciliation requiring approval

- **E1 (P022/P025):** three classes NEG/NORMAL/POS from raw signed TG20 Y and the training-prefix unweighted linear 95th percentile of |Y|. NEG iff Y<−c, POS iff Y>c, equality NORMAL. Original weighted CE used [4,1,4] in executed recipes. Original P025 reports explain event AP versus natural probability calibration and analytical inverse-weight correction.
- **S9 EVENT proposal:** preserve those labels, strict-tail rule, unweighted linear cutoff estimator and three-logit head. Fit c separately in each S4 training prefix. Use **unweighted natural-frequency three-class CE**. ANY-tail is the lawful p_NEG+p_POS sum; binary ANY log loss/Brier are separate metrics, not the optimized three-class CE. No class weighting, probability recalibration fit or signed long/short output. This is an intentional new proper-probability experiment, not exact E1 objective replication. It uses the brief's original-multiclass exception instead of silently collapsing labels to a binary head.
- **QR1 (P023/P025):** levels .05/.50/.95, optimized mean pinball in Z=asinh(Y/s), with median and softplus gaps ensuring ordered quantiles. Original TG20 quantiles are s*sinh(qZ); historical baselines use the weighted left inverse empirical CDF. **The executed optimized units were Z, not raw Y.**
- **S9 QUANTILE proposal:** retain that exact Z-space pinball/head, report both qZ and signed qY, and label the units explicitly. This resolves the brief's generic “TG20 quantiles” wording through the exact historical contract. Pinball is not invariant under the nonlinear inverse. No raw-Y pinball optimization or free independent heads is silently substituted. Raw implied quantile crossing incidence is structurally zero; raw head coordinates are median/gap parameters, not three unconstrained quantiles. No presentation sorting is needed.
- **DM1:** sign CE plus conditional positive/negative |Z| regression, then a signed mixture. Its transformed conditional magnitude is not |raw endpoint R|. S9 MAG is a new separate direct raw-magnitude task and does not reproduce or combine DM1.

## MAG

R=log(genuine exit/reference entry), A=|R|. Training scale sA=max(weighted median A,1e−8), using equal session/origin/stock mass. Target m=log1p(A/sA); scalar linear head and ordinary MSE. Report Ahat=sA*expm1(max(mhat,0)), with lower-clamp frequency. The clamp applies only to reporting; the optimized target/output is not invisibly clamped. This inverse does not generally equal E[A|X]. Report transformed MSE, raw-magnitude MAE/RMSE, calibration and predicted-vs-observed magnitude association separately. This is endpoint movement, not intrapath RV or |TG20|.

## Same-task controls (64 bounded fitted control models)

| Arm | Prefix-fitted controls per phase | Unfitted control | Units |
| --- | --- | --- | --- |
| MAG | Global mean m; per-stock mean m | 2 sqrt(2/π) × trailing hourly OC RMS proxy | m-space proper MSE; original A MAE/RMSE |
| EVENT | Global three-class prior; stock prior; four trailing-volatility-bin priors | — | Natural three-class CE; ANY BCE/Brier/AP/ROC and reliability |
| QUANTILE | Pooled quantiles; stock quantiles; pooled quantiles of Z/ρ then multiply by current ρ | — | Z pinball at .05/.50/.95; both Z and Y coverage/width |

All fits are prefix-only, separately for inner calibration and refit. MAG is 2×8=16 fitted controls; EVENT and QUANTILE each 3×8=24, total64. There is no search, fitted calibrator or ridge grid. The existing ranking ridge hard-codes rank targets, so it is not repurposed as an undeclared magnitude regression.

The proxy sigma=exp(original native floored V2) is reconstructed by undoing only the frozen affine V2 scale at the latest completed input. It uses the original fallback and is an OC-volatility approximation; its sqrt(4)-Gaussian scaling is not a certified overnight-risk model. EVENT's four log-sigma bins use prefix-weighted quartile cutoffs and class priors. Probability-log guards use 1e−12 with renormalization; no class weights. Quantile ρ=clip(sigma/median20(sigma),.1,10) is contemporaneously causal; the conditional pooled CDF is fitted on training Z/ρ. Unconditional and stock quantiles use the weighted left inverse CDF, not a new interpolation rule. Ordered baseline gaps have a 1e−12 numerical floor when encoded in median/gap coordinates.

## Optimization, weights and diagnostics

The stock-shared LSTM remains one layer, hidden32, final dropout .1; MAG has 6,433 parameters, EVENT/QUANTILE 6,499. AdamW lr .001, betas .9/.999, eps1e−8; weight decay .01 on matrices,0 on bias; global norm cap1;16 whole sessions per batch,seed42. S9 checkpoint selection is its own proper validation loss with the original inclusive relative 0.1% qualification (loss ≤ 0.999×best), min12/max60/patience10 and fresh same-seed selected-epoch refit. S5 retains strict absolute RankIC+.001 selection. Raw-best and qualifying-selected epochs are separate.

Training and metrics average stocks within origin, origins within session, sessions within year, then years equally. Main S9 controls are legitimate same-target forecasts; saved S4 rank scores are context, not same-task risk baselines. Four-role exports retain exact targets, raw heads, inverse counts, endpoint/maturity/source/recipe/checkpoint bindings and correct actual row losses. Tail cohorts and complements use each task's own optimized loss; TG20 numerator/MAD provenance remains separate. AP gains with worse log loss are tradeoffs, not a general win. Quantile median ranking is secondary and cannot be inferred from width.

Paired proper losses, raw MAG MAE/MSE, ANY Brier/log loss and per-quantile pinballs use whole-month resampling (400,seed22042) with fixed-year equal weighting. AP and calibration remain separately reported; no post-search confirmatory significance is claimed. Role/stock/slot/month/clock/overnight/source/fallback/age analyses retain prescribed populations. Read-only distributional outputs are not fed to a second-stage ranker.
