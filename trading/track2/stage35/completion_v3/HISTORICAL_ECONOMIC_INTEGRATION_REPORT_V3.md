# Bounded historical source/event integration: no performance

Plan:BOUNDED_ECONOMIC_SOURCE_PLAN_V3.json plus its pre-read seal. Receipt:
`audits/HISTORICAL_CLAIM_SHARE_WITNESS_V3.json`;raw checks:
`audits/RAW_SOURCE_FIXTURES_V3.json`. The actual source projection was11 rows from
5 partitions. Frozen F24 Jan8 AAPL/COP signals were reused,not recomputed;all4
arms reached the dimensionless allocator boundary(8 allocations),without orders,
fills,funded capital or cash from investment trades. The earlier full signal and
mature-control populations remain unchanged.

The V2 financial guard refuses actual historical prices without signed release.
It was preserved and tested;no forged ReleasedPrice or source-kind relabeling was
used. Following the user's fallback instruction,this run uses an isolated
claim/share kernel with *synthetic endowed*+10/−6 shares over actual action facts.
Its API has no investment trade,cost basis,NAV,realized/unrealized or return.

| Actual source/event fixture | Isolated consistency result | Residual |
|---|---|---|
| AAPL May10ex/May16pay2024 $.25 | Test endowments produce+2.50/−1.50 claims;net1.00 settlement once;physical share sum4 | Source events supported;quantities fabricated,no strategy return |
| TSLA Aug25,2022 3:1 split | +10/−6 endowed shares→+30/−18,physical12;raw source units checked | No economic fill or wealth valuation |
| MRK June3,2021 OGN distribution | +1/−.6 unpriced OGN quantity claims,net.4;MRK inventory retained | Valuation,CIL/due-bill/basis unresolved;financial release HOLD |
| BA2021–24/Tesla2021–24 common dividends | SEC-backed nonpayment coverage | Not inferred from empty feeds |
| MRK/PEP December2024 ex /January2025 pay | Due tape preserves both post-endpoint cash claims | No2025 price query needed |

Production integration is in `completion_v3/engine.py,book_bridge.py,tapes.py`.
It extends the unchanged V2 chronological fill engine with non-price ex/payment
journals,split unit conversions,pending-order adjustment and automatic calendar
carry. Claim truth/source/rule metadata remains in each journal and receipt.
Historical funded entry is still blocked before loader/output. This is an
implemented integration,not evidence of a historical funded trading replay.

Separate fabricated-price tests reconcile physical/virtual accounting,crosses,
fees,short proceeds,dividend liabilities,split NAV neutrality,weekend carry,
missing rates,delayed receipts,missing exits and resumable claims. These synthetic
financial tests are not combined with real prices to calculate investment results.

Restart is versioned JSON with an allowlisted explicit schema,exact source/code
bindings,adjacent journal hashes and pending/carry state. A first schema attempt
exposed the legacy Cohort float-vs-Decimal mismatch;the codec now checks its
existing float metadata contract instead of casting away typing errors. Monetary
lot fields stay exact Decimal. Unknown classes,changed source binding,cursor/hash,
late corrections and stale/unknown marks fail closed. Historical restore requires
a fresh independent release;the synthetic checkpoint roundtrip is tested.

Owned defects found and corrected are retained as receipts:initial calendar range
beyond the original calendar contract;HTML footer misclassification;duplicate
provider coverage totals;split payable date preceding ex causing a draft witness
to omit the split;restart schema diagnostics. Draft receipts remain labelled
under audits;the final source witness applies the split and verifies12 shares.
No skip/XFAIL,recipe change,source correction or profitable-case removal was used.

NO HISTORICAL FINANCIAL BACKTEST RUN. No historical investment cash,NAV,return,
Sharpe,drawdown,turnover,cost-drag comparison or scenario performance was computed.
