# Scientific summary — S3-C price-only

## Scientific decision

**Execution COMPLETE, 4/4 folds. No incremental evidence over CLOCK-C3; retain CLOCK-C3 and close this fixed S3-C candidate.** No training restart, retry or new candidate was made during resumed supervision. The completed four selector/refit pairs consumed starts 171–174 (170 → 174/300).

The primary calibrated model has equal-year raw magnitude MSE **0.000106739896737**, versus **0.000106665945886** for CLOCK-C3: **+0.069329% (worse)**. The paired difference is +7.39509e-8, with 400-draw, year-stratified whole-month descriptive 95% interval **[−1.40500e-7, +2.63861e-7]**. F21/F23/F24 lose (+0.114%, +0.051%, +0.298%); F22 improves (−0.121%). F24's descriptive interval is entirely positive; these intervals do not adjust for repeated research selection. Near equality is not evidence of equivalence or improvement.

Equal-year magnitude IC falls from **0.330254043 to 0.327834230**; top-four retrieval falls from 0.429466 to 0.424269 (fixed20 chance 0.20). Pair concordance is 0.618639 versus 0.619443; bottom-four retrieval is essentially unchanged (0.303025 versus 0.303028). No clamp ties or constant outputs occurred; raw/C3 rankings match exactly within every origin. MAE is slightly worse, **0.0067606731 versus 0.0067570931**. The ratio of equal-year weighted forecast and observed means is 1.014784 versus 1.013763; bias is +0.000152476 versus +0.000141941 in log-return units. MSE is in squared log-return units; MAE/means/bias are in log-return units.

The raw diagnostic improves raw MSE by **0.449590%** against CLOCK-RAW (descriptive delta interval [−7.91645e-7, −2.75640e-7]), with gains in 2021–23 but a loss in 2024. This does not promote RAW over the predeclared calibrated primary. The calibrated model is also 0.068509% worse than completed S3B-C3, with an interval spanning zero. Improvements over older C3 (−0.454219%), C0 (−7.007685%) and B0-VOL (−4.320999%) do not demonstrate incremental minute-path value beyond CLOCK-C3.

The modest tail gains are offset by ordinary-period and overnight deterioration. The primary result does not support incremental price-path evidence beyond CLOCK-C3. Retain the completed negative/near-tied evidence and keep CLOCK-C3 as reference. No S3-D, Stage5, new seed, calibration or control is automatically authorized.
