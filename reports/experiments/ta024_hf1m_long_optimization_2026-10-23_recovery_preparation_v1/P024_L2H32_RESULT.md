# P024 L2H32: completed

Seed 42; primary reference T2/42. Single frozen variant: `{'arm': 'L2H32', 'seed': 42, 'learning_rate': 0.001, 'head_dropout': 0.1, 'matrix_decay': 0.01, 'improvement': 0.001, 'hidden': 32, 'layers': 2}`. Measured parameters 14881; calibration stopped 12, qualified-selected 1, raw-best 7; fresh refit 1 epochs.

Exploratory development MSE 3.116366428 (difference +0.009806412); daily Rank IC -0.001325824 (difference -0.076885270). Judgment: unsupported on joint MSE/IC point estimates. This is one seed, with 109 reused development sessions. No independent replication or promotion.

Full four-role metrics, exact cases, objective allocation and gradient records: `reports/experiments/ta024_hf1m_long_optimization_2026-10-23_recovery_preparation_v1/L2H32_diagnostics_v1`. Core and supplemental gates both passed. Online training uses pre-update/dropout settings; fixed-checkpoint validation is dropout OFF. Counterfactual selector fields never imply another trained refit.
