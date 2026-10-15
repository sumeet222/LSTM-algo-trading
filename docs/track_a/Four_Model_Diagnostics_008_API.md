# Four-model diagnostics API — Package008

Run `python -m lstm_data.four_model_diagnostics --previous <completed-Package007-directory> --output <fresh-existing-directory>`. Create the output directory first. Existing output paths refuse overwrite. Use the documented repository environment and the exact existing manifests, component stores, recipes and checkpoints. No new dependency or secret is introduced.

The module performs read-only T0/T1 analysis of the four completed seed-42 June-2023/WF1 models. It reuses canonical target, feature, scaler, peer, model and metric functions. It contains no optimizer step, neural/ridge fitting, normalization estimation or journal writer. Inputs remain subject to the retrospective/ideal-clock/hourly-proxy candidate qualifications.

- `legal_key(day, origin)` rejects observations outside training/WF1 before access.
- `session_concentration(days, origin_mse)` averages origins within sessions, then sums the largest ceil(p×N) session losses.
- `pairwise_accuracy(scores, target)` omits target ties and gives forecast ties half credit.
- `paired_blocks(values, calendar_positions, length, seed=8008, samples=5000)` preserves contiguous exchange-session blocks and returns exploratory percentile intervals.
- `safe_model(path, manifest, contract, pair_key)` verifies hashes and preparation/stage/epoch/contract identity before a weights-only CPU load; returns eval mode with gradients disabled.

The CLI freezes error-blind representative keys before reading predictions. It keeps historical dropout-on telemetry separate from final-weight evaluation. Outputs contain aggregate tables and compact endpoint/hash/hidden-norm traces, not dense histories or gradient tensors. The target floor is never refitted. ZERO IC=0 follows the project convention; its defined-only Spearman is unavailable. Bootstrap results are EXPLORATORY_NOT_FULL_G8 and not selection-adjusted.

Provision legitimate existing local inputs using prior manifests and README instructions. Preserve a failed report attempt under a versioned subdirectory before regenerating its own output files; never overwrite a historical fitted artifact. The Package008 command, check, preservation and session records document reproducibility and its limits. No next fit, promotion, confirmation, course substitution or production migration is authorized.
