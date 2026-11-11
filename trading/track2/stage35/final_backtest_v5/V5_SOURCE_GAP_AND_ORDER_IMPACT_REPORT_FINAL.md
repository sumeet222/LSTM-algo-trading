# V5 final source-gap and order-impact report

Source coverage is unchanged: 7,813,800 ticker-minute cells; 10,374 remain missing/invalid after the sealed V4 supplement. Those are not 10,374 failed trades. The source gap is not silently imputed or used to filter earlier opportunities. All rows below are from actual completed current-code cases.

| Case | Missing scheduled attempts | Qualified postponed references | Simulated entry expiries | Terminal pending |
|---|---:|---:|---:|---:|
| baseline | 212 | 166 | 2 | 0 |
| borrow_0.01 | 210 | 164 | 2 | 0 |
| borrow_0.05 | 210 | 165 | 2 | 0 |
| cil_postclose_33.30 | 211 | 165 | 2 | 0 |
| cil_postclose_40.70 | 211 | 165 | 2 | 0 |
| cil_sessions_1 | 212 | 166 | 2 | 0 |
| cil_sessions_10 | 212 | 166 | 2 | 0 |
| fee_0 | 212 | 166 | 2 | 0 |
| fee_0.01 | 214 | 168 | 2 | 0 |
| fixed_borrow_reject_recall | 229 | 174 | 2 | 0 |
| funding_0.05 | 212 | 166 | 2 | 0 |
| funding_0.10 | 212 | 166 | 2 | 0 |
| impact_1 | 258 | 193 | 2 | 0 |
| impact_15 | 149 | 128 | 2 | 0 |
| joint_adverse | 29 | 27 | 0 | 0 |
| known_mrk_cross_prohibition | 209 | 163 | 2 | 0 |
| lag_1 | 157 | 104 | 2 | 0 |
| lag_5 | 125 | 107 | 2 | 0 |
| minimum_0 | 462 | 383 | 2 | 0 |
| minimum_2 | 98 | 98 | 0 | 0 |
| spread_1 | 258 | 193 | 2 | 0 |
| spread_15 | 149 | 128 | 2 | 0 |
| unknown_yield_0.015 | 212 | 166 | 2 | 0 |
| unknown_yield_0.03 | 212 | 166 | 2 | 0 |

Baseline detail: 212 attempts affect 168 account orders /90 distinct ticker-minute keys; 166 later-qualified reference settlements and two explicitly modeled expired entries. A reference event is not necessarily an external trade. Per-order source hashes, UTC clocks, requests and outcomes remain in the event journals.

Qualified fallback wall-minute delay distributions by account are in `presentation/FINAL_TABLES_V5/QUALIFIED_REFERENCE_DELAY_MINUTES.csv`. They include overnight/closure waits when applicable. All cases have zero terminal pending orders, unpriced specials and incomplete account-days. Priced unpaid claims and source confidence remain separately visible.

The V4 strict-minute diagnostic remains UNRESOLVED/NOT_COMPARABLE for its AVGO submitted requests; its source/odd-lot evidence is unchanged. V5 does not claim a historical broker fill/cancel. No odd-lot print or interpolated bar was substituted.
