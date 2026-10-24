# P027 A5 SP3_STOCKMIXER

Scope: RESEARCH_CANDIDATE. Run HF1M-LONG-P027-SP3-RANK4-T2-S42-DEV1; seed42; 6593 parameters.

A4 sees own FT16 plus two leave-one-out peer M1 summaries at every historical step; A5/A6 encode all16 channels of all20 histories before final-state exchange. A4 is not a full-information-matched control. No fourth full-peer LSTM is authorized; A5/A6 gains cannot identify the exchange mechanism independently of information/capacity.

Selector: `{"best": 3.6511536732738055, "epoch": 13, "patience": 10, "raw_epoch": 7, "raw_min": 3.65105703206883, "selected": 3, "status": "PATIENCE_STOP"}`. Fresh refit initialization equals original calibration initialization; no baseline refit. Strict original-TG20 D6g, frozen AdamW/session weighting, phase-correct train-only epsilon/scale and once-only inverse.

| role | original_TG20_MSE | MAE | daily_IC | origin_IC | actual_z_MSE | prediction_SD | matched_peer_shift_origins |
|---|---|---|---|---|---|---|---|
| inner_train | 4.14646 | 1.29857 | 0.0630502 | 0.0623139 | 1.32989 | 0.0436805 | 4407 |
| inner_validation | 3.65115 | 1.27033 | 0.0240593 | 0.0267996 | 1.31126 | 0.0447146 | 766 |
| refit | 4.05977 | 1.29248 | 0.0638551 | 0.0643335 | 1.32576 | 0.0414524 | 5189 |
| development | 3.10992 | 1.24049 | 0.0495687 | 0.042894 | 1.28414 | 0.0380494 | 183 |


Full gradients/clipping/epoch updates, saved model/optimizer/RNG hashes and four-role reload receipts are bound in run_result.json. Actual-objective z-MSE is distinct from raw TG20 MSE and historical online dropout-ON losses. Mechanisms use saved weights; off-diagonal sensitivity and attention are not causal explanations. Ten-session same-slot peer replacement is a matched distribution shift, not a trained null or p-value. Source/rights/clock assumptions remain conditional; repeated109-session development is exploratory. No automatic promotion, fourth full-peer control, seed123 fit or additional model is authorized.

Detailed read-only closeout: scientific_closeout_v2/P027_CROSS_STOCK_COLLECTIVE_COMPARISON_v2.md; full gradient/step evidence: scientific_closeout_v2/P027_FIT_AND_GRADIENT_VERIFICATION.md.
