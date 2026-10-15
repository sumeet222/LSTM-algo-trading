# Matched models and exploratory uncertainty

**ASSUMPTION_CONDITIONAL candidate evidence:** retrospective AAPL/COST/CMCSA/SBUX/CME selection on2026-10-13 (formation reference2020-07-01), vendor adjusted-price/action/PIT uncertainty, researcher-attested local rights/shared clock with private evidence uninspected, idealized own-step zero-latency period-end availability and completed-hourly-close price proxy. SPY is an ETF state proxy, not certified course-USA500 substitution. No executable-fill, independent license/publication, causality, significance or production claim.

| Model | Equal-day WF1 MSE | Daily IC |
|---|---:|---:|
| TM0 | 5.4388296 | 0.0349138 |
| MC0 | 5.4508656 | -0.0120690 |
| MC1 | 5.4514664 | -0.0120690 |
| E5 | 5.4756397 | 0.0387931 |
| ZERO | 5.4275318 | 0.0000000 |
| M1 | 12.6919763 | -0.0219828 |
| RIDGE_OWN_112 | 5.4655180 | -0.0228448 |
| RIDGE_MARKET_147 | 5.4681203 | -0.0034483 |

All rows join one-to-one on(session,origin,symbol),232origins/116sessions/1160stock rows. No selective drop. Frozen midrank Spearman is averaged within session then equally over sessions; ZERO project IC=0 while its mathematically defined-only Spearman is unavailable. M1 is an unfitted ranking score; its MSE has uncalibrated score units. Ridge uses7snapshots versus48LSTM steps, not identical information history. Pooled MSE equals equal-day MSE here only because every session has exactly two origins and five names; score_health.json records both to avoid implying general equivalence.

Five distinct no-tie ranks yield coarse Spearman support (multiples0.1); daily two-origin means are correspondingly coarse and dependent. Target ties, constant targets and constant forecasts follow the existing explicit conventions. Pairwise concordance uses ten name pairs per origin, target ties omitted and forecast ties half credit; it is descriptive and pairs are not independent. TM0 pairwise accuracy51.4224%, E551.4655%; no superiority claim follows.

Contrasts below are A−B: **negative ΔMSE is better; positive ΔIC is better**. Positive-day fractions always mean A−B>1e−12, even when that means worse MSE. Monthly/day/origin/stock tables retain all observations.

| Contrast | Metric | Mean | Median | Positive days | 5-session95% | 10-session95% | 20-session95% |
|---|---|---:|---:|---:|---|---|---|
| TM0-ZERO | MSE | 0.0112978 | 0.0170418 | 53.4% | [-0.02142, 0.03883] | [-0.01827, 0.02546] | [-0.01956, 0.02339] |
| TM0-ZERO | IC | 0.0349138 | 0.0250000 | 50.0% | [-0.02931, 0.09397] | [-0.00172, 0.08707] | [0.00043, 0.08147] |
| MC0-TM0 | MSE | 0.0120360 | 0.0073156 | 56.9% | [-0.01693, 0.04878] | [-0.00658, 0.04223] | [-0.00276, 0.04862] |
| MC0-TM0 | IC | -0.0469828 | -0.0500000 | 40.5% | [-0.11811, 0.01639] | [-0.12026, 0.00302] | [-0.10345, -0.00042] |
| MC1-MC0 | MSE | 0.0006008 | 0.0005524 | 55.2% | [-0.00145, 0.00224] | [-0.00096, 0.00159] | [-0.00089, 0.00132] |
| MC1-MC0 | IC | 0.0000000 | 0.0000000 | 16.4% | [-0.01207, 0.01595] | [-0.01078, 0.01724] | [-0.01509, 0.01250] |
| E5-MC0 | MSE | 0.0247741 | 0.0169833 | 52.6% | [-0.05469, 0.09040] | [-0.05647, 0.07885] | [-0.07192, 0.05033] |
| E5-MC0 | IC | 0.0508621 | 0.1000000 | 56.9% | [-0.03319, 0.14224] | [-0.02415, 0.15905] | [0.02069, 0.16855] |
| E5-TM0 | MSE | 0.0368101 | 0.0067079 | 51.7% | [-0.02052, 0.08664] | [-0.02259, 0.07919] | [-0.02944, 0.05387] |
| E5-TM0 | IC | 0.0038793 | 0.0250000 | 50.0% | [-0.07932, 0.08750] | [-0.08708, 0.09355] | [-0.03060, 0.11293] |
| MC0-RIDGE_MARKET_147 | MSE | -0.0172548 | 0.0034325 | 50.9% | [-0.06938, 0.04217] | [-0.04074, 0.04283] | [-0.02779, 0.04253] |
| MC0-RIDGE_MARKET_147 | IC | -0.0086207 | 0.0250000 | 50.0% | [-0.12112, 0.08622] | [-0.10862, 0.06164] | [-0.08922, 0.04742] |

**EXPLORATORY_NOT_FULL_G8:**5000 moving-block resamples, seed8008, paired daily arrays only,5/10/20exchange-session blocks,95%percentile intervals. Blocks cannot cross an omitted exchange session (108/98/78 permissible starts); resample joins are permitted. No independent stock/origin bootstrap, no model refits, no HAC or full10,000-resample G8 contract, no selection adjustment. Gap/edge weighting and block length influence these intervals. Some20-session intervals exclude zero while corresponding5/10-session intervals include it; never select the favorable length or call an architecture significant. WF1 has already been explored in screening.

E5−TM0 mean IC is only+0.0038793, with5-session interval[−0.07932,+0.08750], and MSE is worse by0.0368101. E5−MC0 improves mean IC0.0508621 but worsens MSE0.0247741. MC0−TM0 is worse by0.012036MSE and−0.046983IC. None beats ZERO MSE. These observations concern this seed/fold, not fundamental architecture limits or absence of market/peer information.

| Month | MC0−TM0 ΔIC | MC1−MC0 ΔIC | E5−MC0 ΔIC | E5−TM0 ΔIC |
|---|---:|---:|---:|---:|
| 2023-07 | 0.05909 | 0.00000 | -0.12727 | -0.06818 |
| 2023-08 | -0.10000 | 0.02174 | 0.14565 | 0.04565 |
| 2023-09 | -0.09750 | -0.01000 | 0.15750 | 0.06000 |
| 2023-10 | 0.04091 | -0.02045 | 0.07955 | 0.12045 |
| 2023-11 | -0.08500 | -0.02000 | -0.00750 | -0.09250 |
| 2023-12 | -0.05250 | 0.02750 | -0.04000 | -0.09250 |

Monthly reversals and differing origin/stock residuals argue for a replication question, not a WF1-tuned intervention. See stock_score_residual_diagnostics.csv, origin_model_diagnostics.csv and monthly_model_diagnostics.csv. Floating-equality fields named `atol1e12` in the JSON use the actual code tolerance1e−12.
