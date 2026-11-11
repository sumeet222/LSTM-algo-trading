# Assumptions fixed for Rapid V2

| Topic | Executed convention |
|---|---|
| Study scope | The sealed V1 fixed 20-stock survivor universe, 18 directional formulas, input hashes, 2021–24 cutoffs and original mode schedules. Existing features are reused. |
| Funding | Separate USD 100,000 books, carried across years. H100 uses V1 sizing. H85 and H70 multiply only eligible new-vintage budget by .85 and .70. |
| Hard risk limits | V1 20% vintage, 10% name, gross/own-cash and short-collateral checks remain in force. Existing exposure stays until a real eligible settlement. A reduced commitment can still breach a hard cap. |
| Timing | Receipt and valid next-bar logic follow V1/V5. Entry expiry is nominal origin plus ten wall minutes. Exit price selection remains causal. The default is 240 scheduled minutes. Micro also tests 60, 120 and 480. Retail tests the same Eastern slot after 1, 3 and 5 sessions. |
| Calendar edge | A session endpoint keeps the slot across weekends, holidays and DST. A half-day without the target slot leads to an explicit abstention. Market prices after 2024 remain out of scope. |
| Participation and fees | V1's prior-received minute volume, atomic pairs, retail minimum notional, physical order budget and cost reference remain fixed. See the friction contract for the two price proxies and commissions. |
| Exposure normalization | RTH marked filled gross dollar-minutes divided by 252 × 390. Pending commitments remain in the risk limits. Mean spendable-cash fraction uses received NAV and settled cash less restricted short proceeds. |
| Action truth | V1/V5 retrospective source and ordinary/special action conventions. Signed accruals, ex/pay dates, splits and MRK–OGN whole and fractional claims are carried through the ledger. |
| Friction diagnostic | Arrival from the received mark to the actual eligible raw open is part of the price path. Concessions above the raw open are assumptions. Zero incremental concession is arithmetic on the same fills with other expenses held fixed. |
| Causality and interpretation | No outcome-conditioned eligibility, quote or locate inference, new neural features, optimizer, dynamic exit or headroom × horizon grid. Holdout confirmation requires a new period. |

The experiment registry and its SHA256 seal preserve the original pre-outcome
policy. An engineering amendment corrected type handling, the expected
reserved gross in the mixed-fill fixture and the audit's Decimal ticket
rounding before the full run. The economic case axis, inputs and policies
match the initial seal. There were no market downloads or new dependencies.
