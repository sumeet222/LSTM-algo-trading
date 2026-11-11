# R01 execution and post-exit diagnostics

| Regime | Executed turnover | Median ticket (IQR) | Physical orders per closed lot | USD 1 fees | All-in bps | Break-even bps |
|---|---:|---:|---:|---:|---:|---:|
| Conservative | USD 6.169M | 5,619 (4,346–8,390) | 2.040 | 984/1,016 | 13.14 | 30.14 |
| Standard | USD 6.854M | 4,691 (4,549–6,133) | 2.029 | 1,228/1,254 | 12.92 | 1.79 |
| High-risk | USD 6.922M | 4,732 (4,505–6,005) | 2.033 | 1,210/1,240 | 12.89 | −2.44 |

Break-even is (raw price P&L + signed action value) divided by executed
turnover, expressed in bps of one-way turnover. It is the aggregate cost
capacity of the recorded paths. Negative cost capacity means the price
and action result was already negative. Conservative cost USD 7.98 per
physical ticket, averaging across commission, price costs and carry.
Its 96.85% USD 1 incidence uses verified inferred ticket quantities
and the actual total commission. Exit legs sometimes required multiple
physical tickets. V3 recorded 517, 635 and 629 exit legs, with 19, 16 and
19 lots respectively having multiple exit legs. Exit-leg fees and
concessions are reconstructed from raw and executed prices. The inherited
aggregate arrival drift uses signed physical quantity times raw open
minus last known order mark. Positive means adverse. H85 signed drift
was +USD 468 across ordinary orders; absolute drift was USD 10,164.
The raw-price P&L already carries those market movements.

| Same-holdings spread and impact multiplier | Conservative | Standard | High-risk |
|---|---:|---:|---:|
| 0.5× | +USD 13,724 | −USD 4,030 | −USD 6,977 |
| 1.0× | +USD 10,488 | −USD 7,629 | −USD 10,611 |
| 1.5× | +USD 7,253 | −USD 11,229 | −USD 14,245 |

Arithmetic uses the same filled quantities and fee/carry amounts. Order
eligibility, cash, realized holding and liquidation would change in a
funded replay under different costs. Raw open is a trade-print proxy.
Minute OHLCV cannot establish simultaneous NBBO, queue position, fees
negotiated with a broker, or actual locate/borrow terms.

## H85 sealed extensions after actual exits

| Leg-level cause | Later target | Valid / targets | Positive | Missed gross upside | Gross losses avoided |
|---|---|---:|---:|---:|---:|
| Policy | +60 scheduled minutes | 377/377 | 56.5% | USD 6,866 | USD 4,697 |
| Policy | +240 scheduled minutes | 377/377 | 52.0% | USD 10,149 | USD 8,817 |
| Policy | Next full session | 369/377 | 48.8% | USD 17,329 | USD 20,085 |
| Risk | +60 scheduled minutes | 140/140 | 46.4% | USD 4,640 | USD 3,377 |
| Risk | +240 scheduled minutes | 140/140 | 48.6% | USD 6,662 | USD 5,359 |
| Risk | Next full session | 140/140 | 48.6% | USD 7,851 | USD 9,652 |

The diagnostic uses actual signed exit shares and modeled fill, then a
later raw-open mark. It can recover some original exit concession. It
excludes incremental borrow, another exit fee and use of freed capital.
Risk extensions are infeasible under the breached policy. Policy extensions
are unfunded and can face new constraints. Eight H85 targets crossing
corporate actions are censored. Standard's risk-leg next-session extension
had USD 25,650 missed upside and USD 18,949 avoided loss over 419 valid
of 422. High-risk had USD 21,071 and USD 18,996 over 374 of 377.
Within H85 ordinary +240-minute exits, the low entry-strength stratum
had USD 4,369 upside versus USD 4,694 avoided loss; the middle stratum
USD 4,966 versus USD 3,830; the high stratum USD 813 versus USD 293 from
31 legs. This describes already-selected exits. The mix of exit causes,
side and stock differs across strata. The three extension horizons reuse
the same exit events.

[All three regimes, causes, strengths and cost arithmetic](extraction_02/R01_POST_EXIT_AND_COST_DIAGNOSTICS.csv)
