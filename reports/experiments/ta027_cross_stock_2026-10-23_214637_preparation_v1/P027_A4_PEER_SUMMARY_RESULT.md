# P027 A4 PEER_SUMMARY

Scope: RESEARCH_CANDIDATE. Run HF1M-LONG-P027-PEER19-M1-MEANSD-T2-S42-DEV1; seed42; 6689 parameters.

A4 sees own FT16 plus two leave-one-out peer M1 summaries at every historical step; A5/A6 encode all16 channels of all20 histories before final-state exchange. A4 is not a full-information-matched control. No fourth full-peer LSTM is authorized; A5/A6 gains cannot identify the exchange mechanism independently of information/capacity.

Selector: `{"best": 3.65125032486739, "epoch": 17, "patience": 10, "raw_epoch": 7, "raw_min": 3.65125032486739, "selected": 7, "status": "PATIENCE_STOP"}`. Fresh refit initialization equals original calibration initialization; no baseline refit. Strict original-TG20 D6g, frozen AdamW/session weighting, phase-correct train-only epsilon/scale and once-only inverse.

| role | original_TG20_MSE | MAE | daily_IC | origin_IC | actual_z_MSE | prediction_SD | matched_peer_shift_origins |
|---|---|---|---|---|---|---|---|
| inner_train | 4.14072 | 1.29797 | 0.0697321 | 0.0685398 | 1.32749 | 0.0514219 | 4407 |
| inner_validation | 3.65125 | 1.27031 | 0.0208137 | 0.023762 | 1.31195 | 0.0484387 | 766 |
| refit | 4.05514 | 1.29199 | 0.0674683 | 0.0672768 | 1.32386 | 0.0531469 | 5189 |
| development | 3.10646 | 1.23968 | 0.0638402 | 0.0478981 | 1.28258 | 0.0522742 | 183 |


Full gradients/clipping/epoch updates, saved model/optimizer/RNG hashes and four-role reload receipts are bound in run_result.json. Actual-objective z-MSE is distinct from raw TG20 MSE and historical online dropout-ON losses. Mechanisms use saved weights; off-diagonal sensitivity and attention are not causal explanations. Ten-session same-slot peer replacement is a matched distribution shift, not a trained null or p-value. Source/rights/clock assumptions remain conditional; repeated109-session development is exploratory. No automatic promotion, fourth full-peer control, seed123 fit or additional model is authorized.

Detailed read-only closeout: scientific_closeout_v2/P027_CROSS_STOCK_COLLECTIVE_COMPARISON_v2.md; full gradient/step evidence: scientific_closeout_v2/P027_FIT_AND_GRADIENT_VERIFICATION.md.
