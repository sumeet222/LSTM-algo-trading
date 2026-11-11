# Final V4 issue disposition

The final terminal decision is STAGE35_BACKTEST_HOLD. Research authorization is present; no RSA key, external reviewer identity or new approval ID is required. The blocker is the approved execution-price contract.

| ID | Disposition | Evidence / residual |
|---|---|---|
| V3-ACTION-001 MRK/OGN | Resolved for the approved conditional research accounting | Issuer/SEC terms, real raw OGN SIP observations, signed whole/CIL claims, deferred conditional payment, independent long/short/offset tests and actual June pilot. Broker-specific CIL/clearing remain conditional. |
| T2-003 / S35-001 crossing | Synthetic and source-backed conservation pass | One physical net position; common ex-post reference; internal zero fees; cumulative external minimum; stable whole-share residuals and 200 randomized permutation witnesses. |
| T2-004 / S35-002 ledger | Implemented; full financial certification HOLD | Cash/claims/splits/carry integrate into real source replay. Books reconcile within declared Decimal tolerance. Unknown submitted executions deliberately prevent complete valuation. |
| T2-009 marked capacity | Implemented and tested | Pending virtual gross, 100/100/10/20 caps, own cash and restricted proceeds. Cap breach cancels only unsent entry remainder; held lots are not resized by later forecasts. |
| V4-PRICE-001 | **HARD HOLD** | AVGO 2021-06-09 16:33 UTC: no approved raw OHLCV opening bar. API returns the next 16:34 bar. Eighteen raw trades are available, but 17 are odd lots and the other is average/derivatively priced. No later-bar substitution or retroactive cancellation is allowed. See MATERIAL_PRICE_BLOCKER_V4.json. |
| V4-ENGINE-001 typed checkpoint | Fixed | Real action dates/confidence enums round-trip; immutable source due tape rebuilt on resume. Failed pilot_r1 is retained. |
| V4-ENGINE-002 nullable controls | Fixed | None/NaN classical controls abstain for their own arm; attainable EQUAL/S2C remain eligible. Failed pilot_r2 is retained. |
| V4-VAL-001 future pending order | Fixed | A known next-session order leaves current marked equity known. An unobservable past effective execution makes it unknown. Synthetic and final half-day witnesses distinguish them. |
| T2-006 stock loan | Conditional implementation approved; strict certification unknown | 2% ACT/365 baseline, 1%/5% stresses; physical net shorts only. No point-in-time locates asserted. |
| T2-005 receipt | Qualification retained | 1/2/5-minute scenarios are assumed, not measured vendor/broker receipt. |
| T2-007 retrospective source / survivors | Qualification retained | Fixed survivor panel; archival adjustment/action/cleaning and new retrospectively retrieved quote vintages. No live PIT claim. |
| T2-010 repository static | Separate frozen repository HOLD | New owned files clean; inherited frozen replication diagnostics remain. No protected repair or severity suppression. |
| Phase3 scientific mismatch | Unchanged | MATERIAL_NUMERICAL_OR_METHODOLOGICAL_MISMATCH; no original/Phase2 mixing or broad replication rerun. |

A new price-source convention (for example, a reviewed odd-lot-aware trade reconstruction or quote proxy) would need its own versioned specification, data inventory and causal/conservation tests. A valid independently sourced exact-minute raw bar could instead satisfy the current contract. Merely taking the first available trade or the next minute without that review would change the frozen experiment. No universal claim that all free sources are unavailable is made: raw trades were successfully retrieved; other provider keys were not configured and no accounts were created.
