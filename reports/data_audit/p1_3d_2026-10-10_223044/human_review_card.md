# P1.3D human review — five checks

1. `query_plan.json:1`: frozen split/date/type and dividend exact-ID filters, mapping BLOCKED, three-query/four-attempt ceiling; no first-page continuation. IDs cannot be combined with symbol/type/date filters.
2. `source_examples.json:1`: three attempts and two sanitized records. Split ratio4/1, ex/processAug31, recordAug24 and payableAug28 are distinct reported dates. Dividend ID/exFeb7/rate0.77; absent payment/record dates null, not copied from prior issuer dates. Source release times unknown. Hashes describe original response bytes; those bodies are not persisted.
3. `checks.json:1`: narrow PASS versus missing date INCONCLUSIVE and mapping BLOCKED. Hand-check10×100+50=40×25+50=1050 and10×0.77=7.70; hypothetical receivable/liability and later cash transfer conserve equity. No actual raw/split-price reconciliation or complete action ledger certified.
4. `src/lstm_data/alpaca.py:24` and `src/lstm_data/alpaca.py:70`: existing authentication helper reused; HistoricalClient is bars-only with incompatible schema/automatic pagination/retry policy. A temporary bounded single-GET wrapper was necessary; no production utility/source changes. Two substantive requests, three attempts; no new subscription.
5. `preservation.json:1` and `reports/audit/track_a_events.jsonl:15`: predecessor code/reports and14-event prefix preserved, one non-clearing event, seven blockers, zero fits, nothing staged. Formation/actions completeness/minutes/USA500/D3/G1/G2 stay blocked. Existing F01 regression PASS is code-only.

Decisions: (1) review missing dividend dates/status and require a qualified stable-entity mapping interface before a new query; (2) continue source-vintage/formation/USA500 HOLD without inventing publication or approving the daily proxy; (3) separately authorize an exact next metadata closure package if useful. No broad actions/minutes, new market source, P2 or model activation.

**STOP — AWAIT HUMAN REVIEW.**
