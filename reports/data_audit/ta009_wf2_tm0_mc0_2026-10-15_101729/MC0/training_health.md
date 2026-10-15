# MC0 actual training health

MC0: calibration stopped epoch 12, selected qualifying epoch 1; selected inner MSE 5.820079916; selector PATIENCE_STOP. First >50% clipping warning: calibration 5, refit None; selected calibration clipped fraction 0.274510; final refit fraction 0.327273. Both-pass status WARN_INVESTIGATE; nonfinite gradients 0. Warning epochs: {'calibration': [5, 6, 7, 8, 9, 10, 11, 12], 'refit': []}.

Full train/validation curves and norm p50/p90/p95/p99/max are in epoch_health_summary.csv and immutable per-epoch JSON. The refit uses a fresh model with empty optimizer state, same seed initialization, distinct full-prefix recipe and exactly the selected epoch count. Final checkpoint predictions were reloaded and verified over the full WF2 panel.
