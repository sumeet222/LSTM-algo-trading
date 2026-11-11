# Sealed baseline descriptive results

All eight accounts completed1,005sessions /140,280sourceopportunities with no unresolved orders, no incomplete account-days and no unpriced special claims. Maximum ledger residual5.63e-21. No original model or source was changed. Net results are **strongly negative**, dominated by commissions and modeled external friction. These are exploratory retrospective OHLCV-proxy simulations with assumed borrow/costs and conditional actions, not live executable or independently audited results.

| Population | Arm | Final NAV | Net cumulative return | CAGR | Daily Sharpe ×sqrt252, RF0 | Commissions | Spread+impact+adverse rounding | Borrow | Mean virtual gross/NAV |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| matched | EQUAL | $2,222.13 | -97.78% | -61.39% | -12.65 | $66,064.00 | $36,613.12 | $539.67 | 32.2% |
| matched | ROLLING_RISK | $1,840.62 | -98.16% | -63.17% | -13.71 | $62,514.38 | $37,331.09 | $471.79 | 29.7% |
| matched | EWMA_RISK | $2,008.24 | -97.99% | -62.36% | -13.24 | $63,501.00 | $37,258.58 | $499.92 | 30.8% |
| matched | S2C_RISK | $1,926.90 | -98.07% | -62.74% | -13.45 | $64,507.34 | $37,694.99 | $491.27 | 30.7% |
| attainable | EQUAL | $2,911.95 | -97.09% | -58.69% | -13.14 | $68,289.00 | $30,763.68 | $512.45 | 29.1% |
| attainable | ROLLING_RISK | $1,840.62 | -98.16% | -63.17% | -13.71 | $62,514.38 | $37,331.09 | $471.79 | 29.7% |
| attainable | EWMA_RISK | $2,008.24 | -97.99% | -62.36% | -13.24 | $63,501.00 | $37,258.58 | $499.92 | 30.8% |
| attainable | S2C_RISK | $2,638.94 | -97.36% | -59.70% | -13.53 | $70,980.00 | $28,737.99 | $449.44 | 26.6% |

On the matched population S2C_RISK finishes below EQUAL and EWMA_RISK, and slightly above ROLLING_RISK. This does not demonstrate financially useful incremental sizing under the baseline. Attainable-population classical controls have fewer eligible opportunities; those comparisons are not solely a sizing contrast. All accounts start100,000USD and use the same actual source and prospective execution/capital rules; different size/cost/cap histories legitimately produce different funded trades and idle cash.

The gross-cost addback in the machine analysis holds actual positions fixed and is an accounting decomposition, **not** an independently rerun zero-cost strategy. The cash-dependent whole-share/minimum-order-fee dynamics affect trade counts and investability as wealth declines. No protocol coefficient was changed to improve these outcomes. The predeclared sensitivity suite remains separate and must be reported with its actual completion/hold states.

The daily NAV parquet and standalone HTML in presentation/ contain only certified session observations; connecting lines do not impute nontrading/intraday NAV. All source/conditional/S6 qualifications remain. Recompute from the journals for an independent financial audit; none is claimed here.
