# P021 gradient and generalization audit

| run_id | calibration_steps | refit_steps | calibration_clipped_fraction | refit_clipped_fraction |
| --- | --- | --- | --- | --- |
| HF1M-LONG-TM0-C0-S42-DEV1 | 1896 | 187 | 0.1482067511 | 0.01069518717 |
| HF1M-LONG-TM0-T2-S42-DEV1 | 2686 | 1309 | 0.003723008191 | 0 |
| HF1M-LONG-TM0-C0-S123-DEV1 | 1896 | 187 | 0.1334388186 | 0.02673796791 |
| HF1M-LONG-TM0-T2-S123-DEV1 | 1896 | 187 | 0.002637130802 | 0 |

Clipping fractions count optimizer steps above preclip global L2cap1. Pre/postclip p50/p90/p99/max/mean and nonfinite counts are recorded for every actual epoch. All observed gradients/weights/predictions are finite. T2 has substantially less clipping here; this observation does not establish a causal explanation for prediction quality.

| run_id | first_train_MSE | last_train_MSE | first_validation_MSE | last_validation_MSE | selected | raw_best_epoch |
| --- | --- | --- | --- | --- | --- | --- |
| HF1M-LONG-TM0-C0-S42-DEV1 | 4.161738078 | 4.110060916 | 3.658381302 | 3.674310884 | 1 | 3 |
| HF1M-LONG-TM0-T2-S42-DEV1 | 4.158963327 | 4.121365793 | 3.656470381 | 3.656010189 | 7 | 7 |
| HF1M-LONG-TM0-C0-S123-DEV1 | 4.164020855 | 4.118480397 | 3.658193661 | 3.671421138 | 1 | 2 |
| HF1M-LONG-TM0-T2-S123-DEV1 | 4.162147788 | 4.138234795 | 3.655665116 | 3.653055626 | 1 | 12 |

Training numbers are online pre-update predictions with dropout active; validation uses a fixed epoch-end checkpoint with dropout off. Their difference is a descriptive gap, not an identical-context generalization estimate. All53 calibration epochs and10 refit epochs are retained, including late epochs after epoch1 selection. Full-prefix refit never early-stops on old validation.

Development dispersion and ZERO decomposition:

| run_id | prediction_mean | prediction_sd | actual_sd | prediction_squared | twice_target_prediction | excess_mse |
| --- | --- | --- | --- | --- | --- | --- |
| HF1M-LONG-TM0-C0-S42-DEV1 | -0.01033978746 | 0.03611721701 | 1.765362371 | 0.00141136457 | 0.005405452922 | -0.003994088353 |
| HF1M-LONG-TM0-T2-S42-DEV1 | -0.0076989826 | 0.0488872171 | 1.765362371 | 0.002449234329 | 0.01244965828 | -0.01000042395 |
| HF1M-LONG-TM0-C0-S123-DEV1 | 0.02785608425 | 0.05281722619 | 1.765362371 | 0.003565620813 | 0.002869180305 | 0.0006964405074 |
| HF1M-LONG-TM0-T2-S123-DEV1 | 0.004409325945 | 0.03490043078 | 1.765362371 | 0.001237482224 | 0.002885668996 | -0.001648186772 |

Predictions remain close to zero compared with actual target dispersion. Small MSE differences must be read alongside rank IC, target-tail losses, sign and top4 metrics. T2's original-scale gains are small across two seeds; no robust trading conclusion follows.

Original C0/42 export failure:12 completed calibration epoch summaries and its selected checkpoint survived; in-memory per-batch calibration rows were lost. The approved continuation performed no calibration replay and exactly one fresh refit epoch. Missing batch rows remain disclosed; they were not reconstructed by extra fitting. The original failure remains in journalv8, with continuation and the three remaining starts in linked journalv9.

Each run directory contains calibration_epochs.csv, refit_epochs.csv, gradient_health.csv, phase_contracts.json and run_result.json; private weights/step tables/predictions are referenced by SHA/size. Eight actual tensor-state hashes are distinct, and complete checkpoint reload predictions agree.
