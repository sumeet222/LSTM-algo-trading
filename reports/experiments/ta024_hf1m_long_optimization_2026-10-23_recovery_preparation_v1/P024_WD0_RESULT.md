# P024 WD0: completed

Seed 42; primary reference T2/42. Single frozen variant: `{'arm': 'WD0', 'seed': 42, 'learning_rate': 0.001, 'head_dropout': 0.1, 'matrix_decay': 0.0, 'improvement': 0.001, 'hidden': 32, 'layers': 1}`. Measured parameters 6433; calibration stopped 17, qualified-selected 7, raw-best 7; fresh refit 7 epochs.

Exploratory development MSE 3.106679440 (difference +0.000119425); daily Rank IC 0.074069475 (difference -0.001489971). Judgment: unsupported on joint MSE/IC point estimates. This is one seed, with 109 reused development sessions. No independent replication or promotion.

Full four-role metrics, exact cases, objective allocation and gradient records: `reports/experiments/ta024_hf1m_long_optimization_2026-10-23_recovery_preparation_v1/WD0_diagnostics_v1`. Core and supplemental gates both passed. Online training uses pre-update/dropout settings; fixed-checkpoint validation is dropout OFF. Counterfactual selector fields never imply another trained refit.
