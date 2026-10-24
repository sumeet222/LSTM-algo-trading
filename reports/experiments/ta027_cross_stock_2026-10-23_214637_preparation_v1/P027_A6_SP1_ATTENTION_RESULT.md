# P027 A6 SP1_ATTENTION

Scope: RESEARCH_CANDIDATE. Run HF1M-LONG-P027-SP1-ATTN16-T2-S42-DEV1; seed42; 8481 parameters.

A4 sees own FT16 plus two leave-one-out peer M1 summaries at every historical step; A5/A6 encode all16 channels of all20 histories before final-state exchange. A4 is not a full-information-matched control. No fourth full-peer LSTM is authorized; A5/A6 gains cannot identify the exchange mechanism independently of information/capacity.

Selector: `{"best": 3.656685697486977, "epoch": 12, "patience": 11, "raw_epoch": 3, "raw_min": 3.6537736756869132, "selected": 1, "status": "PATIENCE_STOP"}`. Fresh refit initialization equals original calibration initialization; no baseline refit. Strict original-TG20 D6g, frozen AdamW/session weighting, phase-correct train-only epsilon/scale and once-only inverse.

| role | original_TG20_MSE | MAE | daily_IC | origin_IC | actual_z_MSE | prediction_SD | matched_peer_shift_origins |
|---|---|---|---|---|---|---|---|
| inner_train | 4.15418 | 1.29954 | 0.0350243 | 0.0340791 | 1.33369 | 0.0383022 | 4407 |
| inner_validation | 3.65669 | 1.27081 | -0.0132269 | -0.00941722 | 1.31423 | 0.0360128 | 766 |
| refit | 4.06739 | 1.29358 | 0.0337845 | 0.0326807 | 1.32978 | 0.0287512 | 5189 |
| development | 3.11263 | 1.24036 | 0.0482016 | 0.0452886 | 1.28509 | 0.0250582 | 183 |


Full gradients/clipping/epoch updates, saved model/optimizer/RNG hashes and four-role reload receipts are bound in run_result.json. Actual-objective z-MSE is distinct from raw TG20 MSE and historical online dropout-ON losses. Mechanisms use saved weights; off-diagonal sensitivity and attention are not causal explanations. Ten-session same-slot peer replacement is a matched distribution shift, not a trained null or p-value. Source/rights/clock assumptions remain conditional; repeated109-session development is exploratory. No automatic promotion, fourth full-peer control, seed123 fit or additional model is authorized.

Detailed read-only closeout: scientific_closeout_v2/P027_CROSS_STOCK_COLLECTIVE_COMPARISON_v2.md; full gradient/step evidence: scientific_closeout_v2/P027_FIT_AND_GRADIENT_VERIFICATION.md.
