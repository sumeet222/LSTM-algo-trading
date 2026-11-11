# R01 reconciliation and definitions

**Gate A passed.** The funded manifest and checkpoint binding verified. All
3,015 account-day NAVs reconcile as cash plus signed physical inventory plus
claims and special value. Terminal exact Decimal reconciliation is within
USD 2e−21. The largest daily export rounding residual is USD 1.46e−11.

| USD | Conservative | Standard | High-risk |
|---|---:|---:|---:|
| Starting NAV | 100,000 | 100,000 | 100,000 |
| Signed raw-open price P&L | 19,099.2932 | 1,499.0480 | −1,294.2120 |
| Signed action value | −507.0100 | −273.2000 | −392.1600 |
| Commission | 1,025.28 | 1,259.92 | 1,249.98 |
| Assumed price concession | 3,235.6366 | 3,599.5040 | 3,633.9840 |
| Assumed impact | 3,235.6366 | 3,599.5040 | 3,633.9840 |
| Borrow | 607.3378 | 396.3092 | 406.6996 |
| Funding | 0 | 0 | 0 |
| Net P&L | **10,488.3922** | **−7,629.3892** | **−10,611.0196** |
| Terminal cash | 110,488.3922 | 92,370.6108 | 89,423.0004 |
| Terminal accrued claims | 0 | 0 | −34.02 |
| Terminal NAV | **110,488.3922** | **92,370.6108** | **89,388.9804** |

The bridge adds actions once to signed raw price, then subtracts fees,
concession, impact, borrow and funding once. Executed cash already embeds
modeled adverse prices. The terminal MRK liability in high-risk is a recognized
payable. All accounts are flat with zero terminal stock orders and restricted
cash. January 2025 payment metadata require no 2025 price.

Independent daily reconstruction matches all four year-end returns, annualized
daily Sharpe at zero cash return, date-span CAGR and peak-to-trough drawdown.
The predeclared 2021-01-04 through 2021-01-08 formation fixture checked 12
cohorts at actual raw execution markers. Full extraction checked 832 candidates,
1,726 cohorts, 1,781 exit legs and 3,510 physical tickets. It derived ordinary
entry quantity from signed exit shares converted through effective split
ratios and looked up the original first-entry raw open. Saved exit legs are
external. Inferred physical ticket keys are unique within regime. Gross winners
and losers, raw and executed turnover, commissions and modeled concessions
match the archive. Each regime includes one evidenced OGN disposition.

## Cohort count chain

| Archived count | Conservative | Standard | High-risk | Unit |
|---|---:|---:|---:|---|
| closed_cohorts | 498 | 618 | 610 | Completed virtual lots |
| early_exits | 0 | 0 | 0 | Inherited V2 endpoint comparison |
| scheduled_final_exits | 367 | 208 | 244 | Final fill role EXIT |
| risk_final_exits | 131 | 410 | 366 | Final fill role RISK_LIQUIDATION |
| cohorts_with_risk_fill | 140 | 420 | 374 | At least one risk fill |
| risk_closed_cohorts | 140 | 420 | 374 | V3 primary cause retained as risk |
| risk_before_240 | 20 | 80 | 71 | Retained risk cause and actual age <240 scheduled minutes |
| policy_before_240 | 0 | 0 | 0 | Retained ordinary cause and age <240 scheduled minutes |
| Risk closes before maximum order's first eligible fill | 133 | 416 | 371 | Dynamic clock comparison |

V3 places the nominal origin in the legacy endpoint field for a dynamic lot.
The inherited early condition compares actual exit against that origin and
evaluates false. The dynamic clock uses actual entry and the ten-session
anchor. The two final-fill-role columns sum to completed lots. The differences
of 9, 10 and 8 between any risk fill and final risk fill are partially reduced
lots whose final fill was ordinary. V3 retains the first risk cause for each
such lot. Offline labels use each leg's cause, so offline risk-leg denominators
differ from lot totals. Physical orders include entry, exit and the OGN ticket.

## Actions and support

Each regime recorded three splits and one MRK short distribution, whole OGN
disposition, OGN borrow and signed conditional fractional settlement.
Conservative's MRK entitlement was −12.5 OGN shares, including −12 whole and
−0.5 fractional. Its conditional CIL was −USD 17.10. Ordinary ex/pay counts
were 22/22, 20/20 and 21/20. COP base and variable-return cash records remain
distinct. The 2012 COP spinoff predates this test. JNJ/Kenvue uses the frozen
voluntary no-election policy. JNJ conservative contributed USD 329.11 net,
including −USD 17.76 in actions. Each regime logged one missing-minute attempt
and zero expiry. Conservative and high-risk each have one deferred exit leg.
Standard's deferral appears at entry.

**NOT_IDENTIFIABLE_FROM_AVAILABLE_EXPORTS** applies to the exact action and
carry allocation for each individual cohort and therefore to fully net tail
statistics and fine joint net splits. Frozen grouped net values reconcile.
Per-order marked name and vintage dollars, reservations, free collateral,
arrival by ticker and full per-intent rejection journals were compacted.
A future fixed diagnostic can instrument DecisionEngine.decide,
DynamicLedger.capacity and FastAccount.compact before session compaction.

[Precise reconciliation](extraction_02/R01_RECONCILIATION.csv) · [Committed events](extraction_02/R01_COMMITTED_EVENT_EVIDENCE.json) · [Inherited ledger](../../../src/lstm_data/trading/track2/rapid_v2_diagnostics/book.py) · [V3 reason retention](../../../src/lstm_data/trading/track2/rapid_v3_dynamic/book.py)
