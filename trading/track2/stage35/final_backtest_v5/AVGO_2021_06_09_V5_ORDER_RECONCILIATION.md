# AVGO 2021-06-09 V5 conditional order reconciliation

V4 exact-minute evidence remains unchanged and NOT_COMPARABLE for strategy performance. These are actual-source V5 ledger diagnostics, not verified broker fills. No odd-lot trade was promoted to an opening marker. V5 keeps the standing modeled request pending at16:33 and uses the actual valid raw16:34 bar within the nominal+10-minute lifetime. The original target endpoint remains fixed.

All times below UTC on June9. Nominal12:30 ET is16:30 UTC. Entries expire16:40 UTC. Conditional academic short availability and the originally reserved quantity/prior-volume capacity apply. No new risk/volume decision uses16:34's future price/volume.

| Arm/attainable | Signed submitted | Nominal | Decision/submission | First attempt | Effective fill | Raw open USD | Adverse external USD | Commission USD | Physical shares before → after | Receipt/post |
|---|---:|---|---|---|---|---:|---:|---:|---|---|
| EQUAL | -2 | 16:30 | 16:32:00.000001 | 16:33 absent | 16:34 | 464.965 | 464.50 | 1.00 | -8 → -10 | 16:37 |
| S2C_RISK | -3 | 16:30 | 16:32:00.000001 | 16:33 absent | 16:34 | 464.965 | 464.50 | 1.00 | -10 → -13 | 16:37 |

The .999 adverse sell factor combines5bp half-spread and5bp impact; the result is rounded down to cents. Each fully fills its submitted request, leaving0submitted shares; any unsent portion remains separately governed by the original entry policy. Restricted short proceeds remain inside cash and cannot fund more risk. The machine witness stores before cash, restricted proceeds, virtual shares/gross, prior-volume availability, decision timestamp, source identity, fill legs, cumulative fee and resulting physical/cash/claim state. It preserves every subsequent cohort/action/carry event.

Original canonical source partition SHA256: `47710016435ad7c56a2a32e11586c80a2d199de9cc2b6715bb23fb1813f083ed`. Projected exact-bar row content SHA256: `4c5ecf3c5e687c831694554c2ae9a74827a5cb4053242d91e7bf301581489796`. Source row is saved in sources/AVGO_NEXT_BAR_SOURCE_WITNESS_V5.json, with raw OHLCV and its timestamp. Composite day/source hashes are present in each qualified-bar event. The original16:33 missing-bar/trade payload hashes remain in V4 and the V5 protected boundary.

Restart from the V5June8 checkpoint, strictly before these submissions, reproduces the uncompressed event/daily/cohort JSONL suffix byte-for-byte. All checks are in audits/RESTART_CERTIFICATION_V5_5899f5a9865c.json. Compressed gzip headers are not confused with event determinism; checkpoints themselves also have deterministic zero-mtime gzip and corruption/idempotence tests. No failed V4 JSON was edited or reclassified.
