# TM0 actual training health

TM0: calibration stopped epoch 12, selected qualifying epoch 2; selected inner MSE 5.811720166; selector PATIENCE_STOP. First >50% clipping warning: calibration 6, refit None; selected calibration clipped fraction 0.254902; final refit fraction 0.254545. Both-pass status WARN_INVESTIGATE; nonfinite gradients 0. Warning epochs: {'calibration': [6, 7, 8, 9, 10, 11, 12], 'refit': []}.

Full train/validation curves and norm p50/p90/p95/p99/max are in epoch_health_summary.csv and immutable per-epoch JSON. The refit uses a fresh model with empty optimizer state, same seed initialization, distinct full-prefix recipe and exactly the selected epoch count. Final checkpoint predictions were reloaded and verified over the full WF2 panel.
