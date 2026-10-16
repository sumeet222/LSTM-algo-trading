# Training signal and boundaries

C0: optimizer objective 3.6614445360 → 3.5750141365; 11/11 adjacent changes decrease. Canonical inner-validation MSE 3.2945880196 → 3.3727396185. Selected qualifying epoch 1, raw minimum at1; stop=PATIENCE_STOP, patience=11.

T2: optimizer objective 1.3174404660 → 1.2857217722; 11/11 adjacent changes decrease. Canonical inner-validation MSE 3.2926493558 → 3.3143952456. Selected qualifying epoch 1, raw minimum at2; stop=PATIENCE_STOP, patience=11.

|arm|stage|head_weight_L2|head_bias|head_norm_ratio_to_recorded_init|hidden_L2_median|hidden_cross_stock_sd_mean|hidden_abs_gt095_fraction|output_sd|
|---|---|---|---|---|---|---|---|---|
|C0|CALIBRATION_SELECTED|0.48744342|-0.049566437|0.96430326|1.2784769|0.18312996|0.0013671875|0.057929555|
|C0|REFIT_FINAL|0.48059398|-0.04673529|0.9507531|1.230066|0.16427838|0.00013020833|0.052297073|
|T2|CALIBRATION_SELECTED|0.47875419|-0.046485122|0.94711347|1.2698643|0.18002127|0.0015625|0.043760614|
|T2|REFIT_FINAL|0.47193703|-0.045516267|0.93362717|1.2216114|0.16268916|0.00013020833|0.042326006|

Bounded eval-only replay matches saved predictions within atol2e-6/rtol2e-5, with repeated example bitwise deterministic, unchanged parameter hashes and no gradients. Head norms alone do not identify useful signal. Nonconstant outputs/hidden variation reject constant collapse in tested cases; initial-to-selected contraction is assessed from recorded seed 42 hash reconstruction. Later contraction, dropout masks, per-example gradients and optimizer states are NOT_RECORDED. Healthy G6 does not establish good optimization or conditional predictability. Capacity/noise/representation remains NOT_IDENTIFIABLE without new controlled evidence.
