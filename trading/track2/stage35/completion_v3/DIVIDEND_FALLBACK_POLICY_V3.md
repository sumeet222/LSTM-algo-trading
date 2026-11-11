# Ordinary-dividend policy ORDINARY_DIVIDEND_V3_1

The binding constants are in DIVIDEND_FALLBACK_POLICY_V3.json. These are conditional
research assumptions approved for implementation, not verified historical events
or permission for financial results. Supported values always take precedence.

| Rule | Frozen treatment | Guard / sensitivity |
|---|---|---|
| A | Actual supported amount/ex/pay in contemporaneous raw-share units | No overwrite under stress |
| B | Missing ordinary ex-date from valid record date: prior joint exchange/banking day before 2024-05-29; same record business day thereafter | May28 record→May24 ex; nonbusiness/special/due-bill HOLD; ±1 business-day stress for inferred dates only |
| C | Missing pay: ex+30 calendar days, next banking day | 14/45 day stress; pending claims past2024 persist without prices |
| D | Last strictly earlier verified regular-series amount, split-converted | Explicit series evidence, max2 payout intervals;0/1/1.5 amount stress; no later dividends |
| E | Missing recurring event only from documented payer/cadence and2 verified earlier events | Max2 extrapolations; no inferred chaining; known suspension excludes extrapolation |
| F | Unknown payer:1.5% ACT365 signed exposure sensitivity,0/3% | Separate pseudo schedule only; no factual ex/pay or cash/NAV injection; suppress security-year with supported dividends or verified zero |
| G | Extraordinary terms/value/CIL unknown | Unresolved special hold; never ordinary imputation |

The implemented recurrence helper requires a declared monthly/quarterly cadence;
it is not a cadence estimator. A caller must supply its documentary payer/series
reference. Every inferred field retains the reference event, cutoff, payer,
formula, lag and truth. Historical publication/receipt times are generally unknown.
The retrospective effective-date midnight availability convention is a separate
assumption, not a claim that a provider delivered announcements then.

Observed actions and conditional-imputed, low, high and unresolved populations
remain distinct. The actual returned cash events have complete ex/pay/amount
fields: zero factual-date/amount/event-existence imputations were needed.
The8 uncertain AMD/AMZN security-years have2,922 daily proxy *templates*, with
no exposure amounts calculated. These are standalone sensitivities only; they
are not silently booked as dividends.251 single-provider cash events separately
record the USD/US-common-share denomination assumption because the response has
no currency field.270 cash/split records have unknown actual publication timing.

The May2024 Apple event uses the independently returned May10 ex-date, not B.
Apple's issuer table confirms amount/record/pay and raw non-split-adjusted amounts;
Nasdaq and Alpaca agree on the ex-date. The 2020 $.82→$.205 comparison reflects
the4:1 share split, not a fourfold dividend cut.

The [SEC T+1 bulletin](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/new-t1-settlement-cycle-what-investors-need-know-investor-bulletin)
and [exchange transition rule](https://www.sec.gov/files/rules/sro/phlx/2023/34-98955.pdf)
support the ordinary May28/May29 transition. The [SEC ex-date guidance](https://www.investor.gov/introduction-investing/investing-basics/glossary/ex-dividend-dates-when-are-you-entitled-stock-and)
distinguishes large/special distributions and due-bill exceptions. This policy
never applies the ordinary shortcut to them. Calendar geometry beyond2024 is
used for payment scheduling only, with no later market observations.
