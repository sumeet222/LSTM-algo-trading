# Friction accounting contract

The executed V1 order is formed from the last received raw-share close m.
It attempts the next eligible observed open p. The fill f includes extra
modeled price concessions. Positive signed quantity q means buy or cover.
Negative q means sell or short. The three signed dollar quantities are

    arrival = q × (p − m)
    incremental price concession = q × (f − p)
    submission-to-fill movement = q × (f − m)

Only the second quantity is assessed as a separate price cost. Positive
arrival is adverse. Negative arrival is favorable. The absolute measure
does not establish an economic charge. The raw-open gross price P&L uses
p and already reflects the path to that raw open.

For micro, r = clip(v20 / v60, .5, 2). The assumed print concession rate
is h = clip(.0003 × r, .0001, .0006). The additional size impact is
j = clip(.0001 × r × sqrt((|q| / max(ADV20, 1)) / .0001),
.000025, .0005). Rates are computed with V1's causal volatility and ADV
references and actual signed external quantity. The modeled price is
p × (1 + sign(q) × (h + j)). Fees are $0.002 per external share.
The cost reference falls back to V1's conservative upper assumptions for
an exit with unavailable volatility/ADV. V1's OGN convention applies
its separate conservative concession if that exposure occurs.

For retail h = j = .0005. The resulting modeled price rounds up on buys
and down on sells to one cent. V1 allocates the full concession in the
h/(h+j) proportion, so each reported price component includes its part
of adverse tick rounding. The separately shown tick difference is a
subset of those components. External fees are the incremental change in
the cumulative order fee max($1, $0.005 × cumulative external shares),
quantized to cents. Virtual legs of a physical order share its fee.
Internal netting transfers use the raw price and no external fee.

The physical ledger changes cash by −q × f − incremental commission.
Borrow is the accrued 2% ACT/365 charge on physical net shorts.
Funding is zero in this baseline. Realized and outstanding signed
dividend/action cash or claims are included once. Gross signed-price
P&L is measured before the modeled execution concessions and fees.
The bridge to net is

    net change = gross signed-price P&L + gross action value
                 − assumed print concession − assumed impact
                 − physical commissions − borrow − funding.

Terminal NAV equals cash, marked stock and signed accrued claims and
special values. Unavailable valuation remains explicit. No paid-cost
component is added to the arrival drift as a second expense. The
zero-incremental-concession alternative is net plus those two price
components for the same filled path. It carries no revised entry,
capital, risk, fee or return series.

## Hand checks

- Buy 10 with mark $100, raw $101 and modeled $101.11. The arrival is
  +$10 and incremental price cost +$1.10. Relative to the mark the fill
  costs $11.10. A $1 commission lowers cash another $1. For a subsequent
  raw sell at $102, with modeled $101.89 and $1 fee, gross raw price
  P&L is $10 and net is $5.80 before carry or actions.
- Short 10 with mark $100, raw $101 and modeled $100.89. Arrival is
  −$10 and concession +$1.10. Cover raw $99 with modeled $99.10.
  With $1 per external ticket, gross raw P&L is $20 and net is $15.90
  before borrow or actions. The $10 favorable arrival is not a second
  credit.
- Internal requests +50 and −50 at raw $100 transfer inventory and
  cash between virtual legs. Physical net quantity and external
  concession, fee and arrival are all zero.
- Requests +250 and −50, net +200, settle +100 externally in each of
  two fills, with 50 internally crossed at the first fill. The $1
  retail minimum applies once. After the first fill 100 physical
  shares exist and virtual gross plus unsent reservations is 300.
  After the second fill physical shares are 200 and virtual gross
  is 300. A $0.10 per-share concession costs $20 in total.

The transaction print can already reflect market microstructure.
The model's added concessions are assumptions. The files do not
identify a contemporaneous bid, ask, midpoint or broker execution.
