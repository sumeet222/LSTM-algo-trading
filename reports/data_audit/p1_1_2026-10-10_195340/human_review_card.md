# P1.1 human review card

**Sampled access PASS; historical publication/full readiness BLOCKED.** No G0/G1/G2 promotion. Review these five exact files from the repository root:

1. [`probe_plan.json`](probe_plan.json) — predeclared AAPL/JPM dates, all four clock slots, explicit SIP/raw parameters, 16-call ceiling. Expect unchanged symbols/source/feed and no performance-based date selection.
2. [`probe_results.json`](probe_results.json) — expect 16 HTTP 200 results, 24 designated minute rows, no next bar page, and response hashes. `response_feed_echo: null` distinguishes explicit request provenance from independent response identification. No account subscription SKU was inspected.
3. [`sample_records.json`](sample_records.json) — inspect AAPL 2020-07-08 10:33 ET open **378.82**, start **14:33 UTC**, derived end **14:34 UTC**; JPM 2023-03-10 11:33 ET open **135.11**, start **16:33 UTC**. Timestamps label interval starts; `available_at_if_evidenced` stays null. Source opens are indicative first-qualifying-trade references, not guaranteed fills. Source QA in 2025 carries no performance conclusion.
4. [`checks.json`](checks.json) — expect narrow PASS checks alongside publication/actions/formation BLOCKED, full coverage NOT_RUN, and inherited F01 INVALID. AAPL 30Min raw open 376.75 versus split 94.19 has a 0.0025 residual from exact division by four; two matched canonical rows agree. No historical delay, adjustment tolerance, labels or common clock were approved.
5. [`resource_estimate.json`](resource_estimate.json) — expect 2.44 million study minute rows before warmup; sizing scenarios 2.56–2.73 million rows, roughly 77–409 MB compressed. These are planning assumptions. Decide whether later P1.3 acquisition merits a separate approval, with full actions/prehistory, FT0 warmup and retry coverage specified first.

The current [bars reference](https://docs.alpaca.markets/us/reference/stockbars) and [minute-label FAQ](https://docs.alpaca.markets/us/docs/market-data-faq) support the documented parameter/interval interpretation. Neither provides the historical publication timestamp of these samples. Provider historical trade-clock descriptions need clarification (see package report).

Preserved evidence: central ledger contains one new P1.1 WARN audit, no supersession, seven unchanged scientific blockers, zero fitting attempts. Protocol pointer, source files, prior reports and application code are unchanged; exact preservation and Git state are in `preservation.json` and the session report. P0.1/P0.2/appendix were committed before this session, so the prompt's earlier uncommitted-work warning is stale. New P1.1 material awaits a separately authorized Git action.

Suggested single next package, only after explicit review/authorization: P1.2 USA500 provenance. Publication assumptions, shared D3 clock, F01 repair and bulk ingestion require their respective separate reviews. Do not rerun network probes merely to inspect this card.

**AWAITING HUMAN REVIEW — NO AUTOMATIC NEXT PACKAGE**
