# Package008 human review card

**TA008_DIAGNOSIS_COMPLETE. Real-pair ledger: 4/40 → 4/40.** No new fits, optimizer steps, trading, confirmation access or registry/protocol changes.

**ASSUMPTION_CONDITIONAL candidate evidence:** retrospective selection on 2026-10-13 (formation reference 2020-07-01), vendor adjustment/action/PIT uncertainty, researcher-attested local rights and shared clock with private evidence uninspected, idealized zero-latency period-end availability, and an hourly-close price proxy. SPY is an ETF state proxy; historical publication, executable fills, course substitution and production readiness are not certified.

| Model | Equal-day WF1 MSE | Daily IC |
|---|---:|---:|
| TM0 | 5.4388296 | 0.0349138 |
| MC0 | 5.4508656 | -0.0120690 |
| MC1 | 5.4514664 | -0.0120690 |
| E5 | 5.4756397 | 0.0387931 |
| ZERO | 5.4275318 | 0.0000000 |
| M1 | 12.6919763 | -0.0219828 |
| RIDGE_OWN_112 | 5.4655180 | -0.0228448 |
| RIDGE_MARKET_147 | 5.4681203 | -0.0034483 |

All rows use the same 232 origins / 116 sessions. ZERO IC=0 is the project convention; defined-only Spearman is unavailable. M1 MSE is an uncalibrated ranking-score diagnostic. **None of the four LSTMs beats ZERO in MSE.**

The strongest findings are target/loss concentration and cancellation in the gate comparison. Training |TG0| reaches 82.03; the worst 10% of sessions contribute about 55.6% of squared loss. There are no zero-MAD cases. MC0/MC1 ranks differ at 47 origins; 19 better and 19 worse MC1 days cancel in average IC. No deterministic input/checkpoint defect or gate collapse appeared in the bounded checks. Maximum replay error is 1.19e-07.

**G6 remains WARN for all four.** TM0/MC0/MC1 select before their first sustained clipping warning. E5 selects epoch 8 and its refit warns at epochs 4–8. No nonfinite gradients occurred. **CLIPPING_CAUSAL_LINK_UNRESOLVED:** saved epoch aggregates do not link individual batch losses to original gradients.

**NO_HYPERPARAMETER_CHANGE_YET.** Choose one future paired TM0/MC0 replication: seed 123 on explored WF1, or unchanged seed 42 on WF2. Each costs two additional pairs and requires separate approval; neither runs here. No automatic finalist shortlist or target/loss/clip change.

Final read-only analysis: **24.389s outer / 21.158s core**. All diagnostic passes: 73.656s. Session through release snapshot: 1561.646s (26.03min). All 2822 protected scientific/other files are unchanged. A concurrent external edit to RandomNotes.md is preserved and documented separately. Thirteen focused tests pass; Ruff passes; 181-file type check has zero errors/warnings. Editor Problems refresh remains human-confirmed.

Start with gradient_and_training_health.md and hypothesis_evidence_and_next_experiments.md. The matched, tail, mechanism and boundary documents link the full evidence and qualifications. Preservation and verification are in preflight_and_preservation.json and checks.json.
