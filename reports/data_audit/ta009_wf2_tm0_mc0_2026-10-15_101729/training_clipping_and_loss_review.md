# Actual WF2 training, clipping and loss review

TM0: calibration stopped epoch 12, selected qualifying epoch 2; selected inner MSE 5.811720166; selector PATIENCE_STOP. First >50% clipping warning: calibration 6, refit None; selected calibration clipped fraction 0.254902; final refit fraction 0.254545. Both-pass status WARN_INVESTIGATE; nonfinite gradients 0. Warning epochs: {'calibration': [6, 7, 8, 9, 10, 11, 12], 'refit': []}.

MC0: calibration stopped epoch 12, selected qualifying epoch 1; selected inner MSE 5.820079916; selector PATIENCE_STOP. First >50% clipping warning: calibration 5, refit None; selected calibration clipped fraction 0.274510; final refit fraction 0.327273. Both-pass status WARN_INVESTIGATE; nonfinite gradients 0. Warning epochs: {'calibration': [5, 6, 7, 8, 9, 10, 11, 12], 'refit': []}.

| Model | Stage | Sensitivity | N batches | ρ loss/norm | ρ target max/norm | Clip fraction |
|---|---|---|---|---|---|---|
| TM0 | CALIBRATION | all_batches | 612 | 0.522367 | 0.456944 | 0.580065 |
| TM0 | CALIBRATION | exclude_5_largest_target_max_batches | 607 | 0.510731 | 0.443749 | 0.576606 |
| TM0 | REFIT | all_batches | 110 | 0.711102 | 0.598998 | 0.254545 |
| TM0 | REFIT | exclude_5_largest_target_max_batches | 105 | 0.671512 | 0.540665 | 0.219048 |
| MC0 | CALIBRATION | all_batches | 612 | 0.387137 | 0.350994 | 0.679739 |
| MC0 | CALIBRATION | exclude_5_largest_target_max_batches | 607 | 0.375371 | 0.338654 | 0.677100 |
| MC0 | REFIT | all_batches | 55 | 0.731962 | 0.647835 | 0.327273 |
| MC0 | REFIT | exclude_5_largest_target_max_batches | 50 | 0.681633 | 0.581561 | 0.280000 |

The sensitivity excludes the five batches with largest absolute target maxima in each model/stage; this rule was fixed before outcomes. Repeated observations of the same session over epochs and changing model weights make these pooled associations descriptive. Positive association identifies co-occurring batch properties; it does not identify individual examples as causes, establish a causal target-tail explanation, or authorize a target/loss/clip change. Detached summaries never replace the frozen MSE objective. No raw volatility denominator was reconstructed from TG0.

The selected epoch, complete stopping trace and both passes are retained even when warnings begin after checkpoint selection. A 100% clipping epoch is reported as WARN. Refit-only health cannot clear earlier calibration warnings. Weight/score stability evidence is limited to finite traces, preserved selected/final checkpoint identities, identical fresh initialization/empty optimizer and full frozen forecast replay; no hidden-state or optimizer-history attribution was attempted. See wf2_target_loss_tails.csv and loss_concentration.csv for target thresholds and session-loss concentration.

ASSUMPTION_CONDITIONAL candidate preparation/pilot evidence: idealized zero-latency completed-hour period-end clock; retrospective split-price/inverse-volume representation and five surviving stocks; researcher-attested local stock/SPY rights/shared clock with private evidence uninspected; completed-hourly-close label proxy, not executable fills. SPY is an ETF state proxy, with no certified course USA500 substitution. No independent license, observed publication, action-vintage or PIT-universe certification. No redistribution authority. Production D1/CURRENT_PROTOCOL and confirmation outcomes remain unchanged.

Strict qualifying selection differs from the raw minimum: TM0 raw minimum was epoch4 (5.808965961), while qualifying checkpoint stayed epoch2 (5.811720166); MC0 raw minimum was epoch2 (5.817792014), while qualifying checkpoint stayed epoch1 (5.820079916). Neither small raw improvement exceeded the frozen strict0.1% rule. No second selection occurred in refit.
