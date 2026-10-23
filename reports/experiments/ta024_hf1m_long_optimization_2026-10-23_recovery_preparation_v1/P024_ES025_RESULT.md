# P024 ES025: completed

Seed 123; primary reference T2/123. Single frozen variant: `{'arm': 'ES025', 'seed': 123, 'learning_rate': 0.001, 'head_dropout': 0.1, 'matrix_decay': 0.01, 'improvement': 0.00025, 'hidden': 32, 'layers': 1}`. Measured parameters 6433; calibration stopped 12, qualified-selected 2, raw-best 12; fresh refit 2 epochs.

Exploratory development MSE 3.112703314 (difference -0.002208939); daily Rank IC 0.032606549 (difference +0.007113552). Judgment: inconclusive exploratory positive signal. This is one seed, with 109 reused development sessions. No independent replication or promotion.

Full four-role metrics, exact cases, objective allocation and gradient records: `reports/experiments/ta024_hf1m_long_optimization_2026-10-23_recovery_preparation_v1/ES025_diagnostics_v1`. Core and supplemental gates both passed. Online training uses pre-update/dropout settings; fixed-checkpoint validation is dropout OFF. Counterfactual selector fields never imply another trained refit.
