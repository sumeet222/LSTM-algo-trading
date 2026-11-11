# Concentration and economic limitations

| Policy | Arm | Own top-two net-positive names | Net after omission, USD (ARITHMETIC ONLY) |
| --- | --- | --- | --- |
| M04-T480 | EQUAL | AMD/WFC | -2,587.38 |
| M04-T480 | ROLLING_RISK | AMD/MRK | -3,297.95 |
| M04-T480 | EWMA_RISK | AMD/SBUX | -8,163.06 |
| M04-T480 | S2C_RISK | AMD/WFC | -8,205.29 |
| R01-A | EQUAL | CVX/COP | -11,212.17 |
| R01-A | ROLLING_RISK | CVX/MS | -9,468.51 |
| R01-A | EWMA_RISK | CVX/MS | -9,482.44 |
| R01-A | S2C_RISK | MS/BA | -9,564.22 |
| R07-PERSIST | EQUAL | AAPL/TSLA | -117.98 |
| R07-PERSIST | ROLLING_RISK | TSLA/AAPL | +697.10 |
| R07-PERSIST | EWMA_RISK | TSLA/AAPL | -207.72 |
| R07-PERSIST | S2C_RISK | TSLA/AMD | +41.08 |

Closed-cohort net allocations reconcile to account net and include execution cost,
borrow, funding and signed action allocations. Gross winners/losers use raw signed
price P&L; net winners/losers use allocated cohort cash P&L. They are different
classifications. Fees are already included in `cost`, not subtracted twice. Orders may
serve multiple virtual cohorts; per-cohort costs are the engine's deterministic
allocation, not independent broker orders. Per-ticker, side, slot, entry/exit year,
cohort-span overnight and exit-reason projections are alternate lifetime allocations:
never add those views, and never treat a lifetime cohort exit-year sum as yearly NAV.

M04's primary matched 155 earlier partial-risk cohorts have an unavailable earlier
specific risk cause after a later final policy close (38/42/40/35 by arm); generic
RISK_OTHER_CAP is not proof of an aggregate-cap breach. Any-risk count, final-risk
count and policy-final count differ. A cohort's risk label need not identify the
portfolio constraint that triggered whole-account liquidation. Dynamic `early_exits`
semantics do not imply the absence of risk closures.

Annual marked NAV and costs are supported. Calendar-year raw-price/action separation,
exact action events on worst days, per-stock marked exposure, gross long/short physical
exposure, minute-exact invested time, cap utilization and complete post-reservation
buying power are NOT_IDENTIFIABLE_FROM_SAVED_OUTPUTS. Required minimal additional
saved fields: per-timestamp physical symbol quantities/marks with receipt times,
reservation balances and binding constraint IDs; action ex/pay/claim cash postings;
cohort-to-physical-order allocation keys. No source extraction or replay is authorized
or performed. Tail-day claim changes include revaluation/settlement and are not
invented action cash flow. Closing signed net inventory does not measure gross risk.

RTH filled-virtual exposure and overnight ACT/365 carry use different clocks. Mean
unrestricted cash before pending reservations is a cash proxy, not actual idle buying
power or investable leverage. Dollar-exposure-year normalization does not prove alpha
or a superior multiday variance forecast. No IID-trade inference, p-values, untouched
confirmation, fee calibration, strategy optimization or Stage 6 audit occurred.
