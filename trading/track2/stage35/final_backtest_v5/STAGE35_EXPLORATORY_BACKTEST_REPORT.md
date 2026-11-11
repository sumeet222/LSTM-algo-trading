# V5 exploratory backtest: baseline and frozen sensitivity study

The baseline and 23 frozen sensitivities are complete and reconciled (24/24 total). Actual statuses and any failures remain in the immutable master manifest. These are retrospective conditional OHLCV-proxy research results, not broker-realized returns or independently validated alpha. No strategy parameter was selected using these outcomes.

The study asks whether frozen S2-C magnitude forecasts improve sizing conditional on a separately frozen five-session directional sign. It does not test S2-C sign prediction. Original F21–F24 C-A/O1/FT16/CLOCK/C3 cached forecasts and prefix reference/control artifacts were reused without neural inference reruns, retraining or calibration. The fixed universe contains 20 surviving names, a material survivorship limitation.

## Reconciled baseline

All eight accounts start at $100,000 and run continuously over 1,005 exchange sessions, 2021–2024. Checkpoints/models switch by annual fold; account cash, lots and claims do not reset. New entries requiring a 2025 executable exit are excluded by calendar only. Annual metrics therefore begin at each prior year-end NAV. Whole-share rounding and the $1 physical-order fee minimum materially change investability as wealth falls.

| Population | Sizing arm | Final NAV USD | Compound net return | CAGR | Daily Sharpe (252, rf=0) | Mean virtual gross / NAV |
|---|---|---:|---:|---:|---:|---:|
| matched | EQUAL | 2,222.13 | -97.7779% | -61.3907% | -12.6523 | 32.17% |
| matched | ROLLING_RISK | 1,840.62 | -98.1594% | -63.1667% | -13.7099 | 29.72% |
| matched | EWMA_RISK | 2,008.24 | -97.9918% | -62.3553% | -13.2364 | 30.82% |
| matched | S2C_RISK | 1,926.90 | -98.0731% | -62.7424% | -13.4494 | 30.74% |
| attainable | EQUAL | 2,911.95 | -97.0881% | -58.6909% | -13.1366 | 29.14% |
| attainable | ROLLING_RISK | 1,840.62 | -98.1594% | -63.1667% | -13.7099 | 29.72% |
| attainable | EWMA_RISK | 2,008.24 | -97.9918% | -62.3553% | -13.2364 | 30.82% |
| attainable | S2C_RISK | 2,638.94 | -97.3611% | -59.6951% | -13.5346 | 26.58% |

The baseline loses approximately 97–98% in every arm. On the matched opportunity population, S2-C ends $295.23 below EQUAL and $81.33 below EWMA, and $86.28 above ROLLING. These small relative differences within severely losing portfolios do not support a useful incremental sizing claim. S2-C mean gross exposure is lower than EQUAL, so a return difference alone would not establish risk-adjusted improvement. No significance claim is made.

Attainable EQUAL/S2C can use valid opportunities lacking classical-control support; their comparison against classical arms includes eligibility differences. Rolling/EWMA attainable populations equal their matched populations. The common population is formed from currently mature input support, never eventual filled/exit-complete outcomes.

## Costs and capital use

| Matched arm | Commission USD | Spread + impact USD | Physical short borrow USD | Funding USD |
|---|---:|---:|---:|---:|
| EQUAL | 66,064.00 | 36,613.12 | 539.67 | 0.00 |
| ROLLING_RISK | 62,514.38 | 37,331.09 | 471.79 | 0.00 |
| EWMA_RISK | 63,501.00 | 37,258.58 | 499.92 | 0.00 |
| S2C_RISK | 64,507.34 | 37,694.99 | 491.27 | 0.00 |

Costs, particularly repeated minimum commissions, are economically large relative to the initial capital. The report retains them exactly as preregistered. Adding these costs back to the same actual holdings is only an accounting decomposition; it is not a frictionless portfolio rerun because costs also affect later cash, share rounding, risk reservations and fill eligibility. No favorable zero-cost headline is substituted.

The allocator caps each origin at 20% marked NAV, each aggregate name at 10%, virtual gross including pending at 100% and physical net at 100%; short proceeds remain restricted within cash once. Whole-share rounding leaves residual cash unused. Exposure/cap/rejection records and available own cash are retained by account; idle cash is an outcome, not redistributed after caps. No dynamic resizing of held cohorts is active.

## Source, execution and action diagnostics

The baseline processed all 140,280 calendar-generated stock opportunities. Source-side forecast eligibility remains 131,111 forecasts and 9,169 explicit unavailable inputs; candidate eligibility is distinct from funded cohorts, external orders and fills. The frozen control intersection has 87,557 candidates; EQUAL/S2C have 128,192 attainable candidates. No F09/future endpoint-completeness trading gate was used.

A V5 order must stand before the selected later valid RTH minute starts. The actual raw opening marker is learned only on completed-bar receipt, with separate effective, observed and posted timestamps. Prior received minute volume limits submitted capacity to 1%; fill-bar future volume cannot authorize its own order. Baseline receipt is assumed +2 minutes, spread/impact 5+5 bp per external side, commission $0.005/share with $1 cumulative order minimum. These are research scenarios, not NBBO, measured latency or broker fills.

The 10,374 residual missing/invalid source cells are not 10,374 failed executions. Actual baseline: 212 missing attempts, 168 affected account orders, 90 distinct ticker-minute keys; 166 later-qualified reference settlements and two simulation-only expired entry batches. Final pending orders, unpriced OGN claims, incomplete account-days and unresolved exposures: zero. Every later reference uses its actual time and source hash. V4 strict-minute performance remains NOT_COMPARABLE because its submitted orders were unresolved; no cleaned strict-mode Sharpe is reported.

AVGO June 9, 2021: intended 16:33 UTC absent; still-standing attainable EQUAL −2 and S2C −3 requests use the source-valid 16:34 raw open 464.965, adverse price 464.50 and one $1 fee. Physical shares change −8→−10 and −10→−13, posted at 16:37. This resolves the simulated policy mismatch, not historical broker execution uncertainty. See the final pilot/source/order witness.

Ordinary actions retain 16 supported and 251 single-provider observed cash-event confidence classes, three splits, eight verified-zero and eight unknown security-years. Unknown ordinary-event years are zero-recorded in base with a separately tagged 1.5%/3% yield sensitivity, never duplicate observed payments. Known 2024 entitlements paid in 2025 remain claims without any 2025 market-price read. MRK/OGN signed 1:10 whole/fraction obligations, source-derived quotes and conditional CIL settlement preserve physical/virtual ownership; tax-basis movement does not create NAV. JNJ/Kenvue no-election and original COP treatment remain unchanged.

A repeating-Decimal OGN allocation assertion was found on the first funded attempt before complete performance publication. The failed run/code/checkpoints are preserved. An additive integer-attoshare residual allocation fixed exact virtual/physical shares without changing source values or economic policy. The fresh full baseline reconciles with maximum USD residual 5.63e-21 (threshold 1e-8); full closed/terminal cohort attribution reconciles to NAV. All pre-spinoff recoverable records match the failed run exactly.

## Metrics, attribution and interpretation

Daily return is consecutive session-end NAV ratio minus one, including fees, carry, claims and marked inventory. Arithmetic annualization and daily volatility/Sharpe/Sortino use 252 sessions, zero risk-free rate and zero MAR; CAGR uses elapsed calendar-year conventions. Maximum drawdown includes starting cash and duration is counted in observed sessions. Undefined/nonpositive/incomplete wealth metrics are rejected or marked N/A. Overlapping 240-minute cohorts are not treated as independent statistical observations.

Official machine-readable outputs include daily cash/restricted cash/physical and virtual risk, source/action/order/fill journals, cohort cash attribution, terminal lots, checkpoint states, annual metrics, costs, turnover, rejection reasons, time invested and per-ticker/slot/sign/overnight/year summaries. Attribution dimensions are alternate views; summing them together would double-count the same cohorts. Gross/net exposure, costs and participation refer to physical execution and virtual risk consistently. Sector/beta metadata are not independently established and are reported unavailable.

Source and strategy qualifications remain material: fixed survivors, repeatedly researched 2021–2024 period, retrospective corporate-action/cleaning vintages, conditional locates and ACT/365 loan costs, no exchange bid/ask/order-book evidence, unknown actual broker cancellation/remittance, assumed source receipt and nominal-target versus delayed executable-hold mismatch. Daily financial identities passing does not certify these assumptions as historical truth or deployment readiness.

## Frozen sensitivity completion

The sealed grid contains 24 total scenarios: baseline plus 23 predetermined sensitivities. No result-dependent scenario or factor selection is allowed. The final master manifest and presentation tables enumerate complete, failed and not-run cases without dropping adverse results. Each case uses all four arms and both populations under the same current-code gate.

## Independent follow-on

Stage 6 is pending and was not executed. It should independently recompute cash/lot/action/fee/borrow books, inspect source/corporate-action confidence and timing, audit exposure/fairness and reused-period selection, and conduct appropriate dependence-aware null, walk-forward and prospective checks under separate authorization. These descriptive results do not establish profitable alpha, significance or live deployability.


Final scenario tables: `presentation/FINAL_TABLES_V5/SCENARIO_RESULTS.md`. Exact annual cost/exposure and actual holding-time summaries plus daily/mechanical identities: `presentation/ADDITIONAL_DESCRIPTIVE_TABLES_V5/`. Final run, integrity and recovery details: `STAGE35_V5_FINAL_HANDOFF.md`.
