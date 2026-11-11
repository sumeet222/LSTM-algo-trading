# Final V5 source-backed pilot reconciliation

Code fingerprint: `9e093b3f6a62`. This successor references the final arithmetic adapter; earlier pilot receipts remain unchanged. These were authorized ledger diagnostics before financial release.

| Window | Sessions | Opportunities | Maximum USD residual | Pending / unpriced / incomplete |
|---|---:|---:|---:|---|
| 2021-01-04 to 2021-01-08 | 5 | 700 | 1.2E-22 | 0 / 0 / 0 |
| 2021-06-02 to 2021-06-11 | 8 | 1120 | 1.0368E-21 | 0 / 0 / 0 |
| 2022-08-24 to 2022-08-26 | 3 | 420 | 4.546182E-22 | 0 / 0 / 0 |
| 2024-05-09 to 2024-05-17 | 7 | 980 | 1.48480E-22 | 0 / 0 / 0 |
| 2024-11-27 to 2024-12-02 | 3 | 360 | 3.4969E-23 | 0 / 0 / 0 |

All five windows passed in all eight independent arm/population books. The June window includes signed MRK/OGN claims and the AVGO missing-minute witness.

Exact files and hashes: `audits/PILOT_CERTIFICATION_V5_9e093b3f6a62.json`. Pre-AVGO checkpoint, independent restart and byte-identical uncompressed JSONL suffixes: `audits/RESTART_CERTIFICATION_V5_9e093b3f6a62.json`. Gzip transport headers are excluded from suffix equality; typed daily state compression is deterministic.

The AVGO orders were already standing before the source-valid 16:34 UTC bar. Their opening proxy was 464.965 raw USD/share, the adverse short execution price 464.50, and commission $1 once per order. EQUAL −2 shares changed physical −8 to −10; S2C −3 changed −10 to −13. Effective fill 16:34, completed 16:35, available/posted 16:37; decision/submission 16:32:00.000001. This is the approved conditional simulation, not evidence of a historical broker fill. The absent 16:33 bar and odd-lot/derived-print exclusions remain unchanged.

Full source/order/reservation/cash/fee/virtual states: `audits/AVGO_ORDER_WITNESS_V5_9e093b3f6a62.json`; bounded original source row and partition identity: `sources/AVGO_NEXT_BAR_SOURCE_WITNESS_V5.json`.
