# Rapid V2 validation

| Gate | Evidence |
|---|---|
| Input frontier | Inherited V1 feature mutation and decision tests. A single frozen signal evaluation supplies every variant. V2 only replaces the nominal endpoint. |
| Calendar | 60/120/240/480 compared with the frozen XNYS clock. 1/3/5-session cases retain the Eastern slot across weekends, holidays and DST. Half-day and year cutoff fixtures. |
| Submission and fills | Frozen V5 partial, expiry, no-hindsight and prior-volume fixtures. Source AVGO replay uses 16:34 UTC, after the known missing 16:33 UTC bar. |
| Headroom | Allocation method matches V1 structurally except for the pre-rounding multiplier. Synthetic paired commitments are 99/84/69 shares under the same mark, cap and $2,000 floor. Pending reserves and adverse mark breach tested. |
| Internal transfers and fees | Signed buy/short bridge, zero net and mixed internal/external partial fixture. Cumulative retail fee is paid once. All V1 original Parquet fill prices and physical-order commissions rechecked. |
| Action and carry | Bounded June 2021, August 2022, May 2024 and Thanksgiving windows. Additional seeded signed MRK/OGN real-price witness. Inherited splits, dividends, weekend borrow, risk and netting tests. |
| January parity | All 108 cases on 19 actual sessions. All 18 H100 daily account components exactly match the sealed V1 pilot. Scoped no-trade cases are retained. |
| Restart | Interrupted January week restored after session 2. The full checkpoint state hash matches the uninterrupted all-case state. |
| Full-run release | Tests and source-pilot receipts bound to the executed registry. Final H100 daily balances and metrics compared with V1 on all 1,005 sessions. |
| Integrity and cost scope | Original SHA256 and mtime rechecked. One raw-share price traversal. V1 model estimates remain frozen and no new quote or broker claim is made. |

The final targeted validation receipt records 48 tests, Ruff E/F/I and owned
Pyright. The additional inherited economics group records 27 passing tests.
Arrow's sandbox CPU-cache probe warnings did not affect Parquet reads.
