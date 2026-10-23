# P024 DROP0: completed

Seed 42; primary reference T2/42. Single frozen variant: `{'arm': 'DROP0', 'seed': 42, 'learning_rate': 0.001, 'head_dropout': 0.0, 'matrix_decay': 0.01, 'improvement': 0.001, 'hidden': 32, 'layers': 1}`. Measured parameters 6433; calibration stopped 16, qualified-selected 6, raw-best 7; fresh refit 6 epochs.

Exploratory development MSE 3.104692269 (difference -0.001867746); daily Rank IC 0.072779755 (difference -0.002779691). Judgment: unsupported on joint MSE/IC point estimates. This is one seed, with 109 reused development sessions. No independent replication or promotion.

Full four-role metrics, exact cases, objective allocation and gradient records: `reports/experiments/ta024_hf1m_long_optimization_2026-10-23_recovery_preparation_v1/DROP0_diagnostics_v1`. Core and supplemental gates both passed. Online training uses pre-update/dropout settings; fixed-checkpoint validation is dropout OFF. Counterfactual selector fields never imply another trained refit.
