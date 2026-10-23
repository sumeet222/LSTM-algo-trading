# P024 H64: completed

Seed 42; primary reference T2/42. Single frozen variant: `{'arm': 'H64', 'seed': 42, 'learning_rate': 0.001, 'head_dropout': 0.1, 'matrix_decay': 0.01, 'improvement': 0.001, 'hidden': 64, 'layers': 1}`. Measured parameters 21057; calibration stopped 15, qualified-selected 5, raw-best 6; fresh refit 5 epochs.

Exploratory development MSE 3.107416294 (difference +0.000856279); daily Rank IC 0.035427630 (difference -0.040131816). Judgment: unsupported on joint MSE/IC point estimates. This is one seed, with 109 reused development sessions. No independent replication or promotion.

Full four-role metrics, exact cases, objective allocation and gradient records: `reports/experiments/ta024_hf1m_long_optimization_2026-10-23_recovery_preparation_v1/H64_diagnostics_v1`. Core and supplemental gates both passed. Online training uses pre-update/dropout settings; fixed-checkpoint validation is dropout OFF. Counterfactual selector fields never imply another trained refit.
