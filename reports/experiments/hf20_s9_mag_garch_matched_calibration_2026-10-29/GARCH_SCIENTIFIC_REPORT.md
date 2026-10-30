# GARCH scientific report

## GARCH scientific and technical outcome

The supported package estimator was called exactly 560 times, once for each stock×slot×fold. 557 units pass; 3 fail strict stationarity. All optimizer convergence flags are reported, including stationary-boundary outcomes. No alternative starts, order/distribution, penalty, grouping, fallback or retry. The original BLOCKED_DEPENDENCY record is byte-preserved; this successor resolves installation but has a separate PARTIAL_BLOCKED status.

| year | ticker | slot | n | convergence_flag | alpha | beta | persistence | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2022 | COP | 15:30 | 1843 | 0 | 0.1149643264 | 0.8850356736 | 1 | BLOCKED_FIT_GATE |
| 2023 | COP | 13:30 | 1933 | 0 | 0.1266985799 | 0.8733014201 | 1 | BLOCKED_FIT_GATE |
| 2024 | COP | 15:30 | 2177 | 0 | 0.1054477222 | 0.8945522778 | 1 | BLOCKED_FIT_GATE |


Admitted fit counts range 1526–2412; 65 units have α+β≥.99. Effective weighted-session support ranges 1339.70–1960.55; zero prefix numerical-bound contacts, detailed in garch_variance_bounds.csv. Full effective support, exclusions, dates, scale, convergence, iterations, variance ranges and extremes appear in garch_support_prefit.csv and garch_fit_diagnostics.csv. Exactly59 history origins are excluded by chronological start>=last retained end (same complete20 support); equality is admitted. Evaluation keys are never dropped.

Gaussian constant-mean GARCH(1,1) uses x=100R, rescale=False, deterministic package starting values, SLSQP maxiter1000, ftol/tol1e-9. Fitting uses signed R, not |R|, and only the restricted prefix. The package likelihood weights its ordered events normally; common hierarchical weights govern calibration and evaluation. Its one-next-same-slot-event distribution is an approximation with variable event spacing and intraday/overnight composition. It is not a continuous-time four-hour variance or fully clock-regime-aware process.

Frozen coefficients drive h_next=ω+α(x−μ)²+βh. Only previously matured genuine endpoint returns update states, strictly before issue. Filtering continues through embargo gaps, calibration and OOS without reoptimization. Prefix state and all later updates/forecast frontiers are independently replayed in garch_replay_verification.csv; garch_filter_trace.csv includes 09:30,15:30 and early-close cases. Each unit has immutable parameter, initial-state and update files. Passing-unit forecasts in GARCH/F*/ are diagnostic only; no complete-score result is computed by dropping the three blocked units.

UNCAL magnitude uses the folded-normal E|N(μ,σ²)|, μ and σ divided by100, h divided by10000. Unit fixtures cover zero mean, zero variance, signed-mean symmetry, positive output, numerical quadrature, unit conversion, supported arch recursion and strict maturity/equality. No unexplained horizon multiplier. The conditional-Gaussian conversion is a modeling assumption, not a distribution-free identity.


No complete GARCH MSE/IC: boundary failures are not an empirical loss. Dependency block from the predecessor remains unchanged. Researcher review only; no retry or fallback.
