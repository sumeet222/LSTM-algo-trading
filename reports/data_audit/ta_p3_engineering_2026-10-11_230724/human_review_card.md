# Combined P3.1–P3.4 human review card

P3_1_TO_P3_4_SYNTHETIC_ENGINEERING_COMPLETE — HUMAN_REVIEW_REQUIRED

One final human review; no intermediate approval is requested. All engineering recommendations below are PASS, pending human review. Every scientific recommendation is HOLD. Synthetic PASS does not clear G0–G4.

## Go/no-go

| Phase | Engineering recommendation | Scientific |
|---|---|---|
| P3.1 ledger/accounting | PASS | HOLD |
| P3.2 Policy A | PASS | HOLD |
| P3.3 Policy B/frictions/borrow | PASS | HOLD |
| P3.4 risk/exceptions | PASS | HOLD |
| P3.5/P3.6/P4 | NOT STARTED | HOLD |

## Fourteen review checks

| # / check | Exact functions / lines | Independent expectation | Observed evidence | Adverse case | Engineering / scientific |
|---|---|---|---|---|---|
| 1. Universe/order binding | `src/lstm_data/p3_domain.py:35`; `src/lstm_data/p3_domain.py:58` | Alternate FOX/ZEN/MAP/ORB/TIN, all five ordered; duplicate/unknown/stale binding rejects | Alternate trace +24 hashes and same 44 hand-oracle values PASS | Alter order/version; unknown symbol; no ticker math branches | PASS / HOLD |
| 2. Ranking and C01 | `src/lstm_data/p3_policy.py:36`; `src/lstm_data/p3_engine.py:118`; `tests/test_p3_exceptions.py:191` | Long first/short last on ties; negative scores still pair; identical entry journal prefix across four future-exit variants | Tie/sign tests PASS; missing/90-price/future-published exit variants preserve entry prefixes | Future label/exit availability cannot filter entry | PASS / HOLD |
| 3. Physical cash and fills | `src/lstm_data/p3_accounting.py:235`; `src/lstm_data/p3_audit.py:144` | Buy5@100: cash499.75/E999.75; sell@110:1049.475/fees.525. Short5@100:1499.75; cover90:1049.525/fees.475 | Exact expected/actual rows PASS; all nine journals reconstruct shares/cash | Unfilled target changes neither cash nor shares; changed duplicate ID rejects | PASS / HOLD |
| 4. Action reuse and signed claims | `src/lstm_data/p3_accounting.py:369`; `src/lstm_data/p3_accounting.py:450` | Held short -24.75 becomes -99 after4:1; price25 preserves liability2475; dividend.5 produces -49.5 claim/E9950.5 | Original CA tests and overnight hand trace PASS; known settlement paid once, unknown date NAV=None | Wrong epoch/unsupported merger; no virtual dividend duplication or split P&L | PASS / HOLD |
| 5. Policy A sizing and expiry | `src/lstm_data/p3_policy.py:101`; `src/lstm_data/p3_engine.py:237` | Leg24.75 shares at100/E10000; sleeve49.5%; two same-direction zero-cost sleeves99%; independent240m expiry | 4950/9900 gross and asynchronous expiry tests PASS; accepted old quantities stay frozen | Price drift/later scores cannot routinely resize old shares | PASS / HOLD |
| 6. Physical netting and reopening | `src/lstm_data/p3_policy.py:142`; `src/lstm_data/p3_accounting.py:166` | Equal opposing virtual quantities give zero target; from flat zero orders/fee. At different instants earlier fills retain fees; expiry reopens actual exposure | Zero-target test PASS; 5bps sequential reversal gives cash1499.25/fees.75; expiry external fee2.475 | Zero aggregate is not absence of virtual legs; do not erase earlier external fills | PASS / HOLD |
| 7. Post-cost full-pair cap | `src/lstm_data/p3_policy.py:152`; `tests/test_p3_financing.py:99` | Gross10000/E10000 accepted at0; projected fee2.475 givesE9997.525 and rejects full pair at5bps; E9999.9999 rejects at0 | Exact-boundary and epsilon tests PASS; predetermined102.02 price produces different0/5bps admission paths | No cap110 substitution, resizing, evicting or half-pair admission | PASS / HOLD |
| 8. Policy B virtual conflict | `src/lstm_data/p3_policy.py:91` | Entire opposite pair veto even when A virtual legs net to physical0; identical direction/other nonconflicting pair admitted | POLICY_B_VIRTUAL_CONFLICT and preserved old sleeve tests PASS | Veto inspects each accepted virtual instruction, not net physical/sign of score | PASS / HOLD |
| 9. Filled-notional bps and fresh paths | `src/lstm_data/p3_domain.py:100`; `src/lstm_data/p3_replay.py:112` | A/B x0/2/5/10bps x0/.005/.03borrow =24 independent states on one immutable script | 24 unique trace hashes; primary5bps; no-fill costs0; matrix SYNTHETIC_ACCOUNTING_ONLY | No posthoc repricing or additional half-spread | PASS / HOLD |
| 10. Physical day-max borrow | `src/lstm_data/p3_financing.py:25`; `src/lstm_data/p3_financing.py:50` | 2475*.03/360=.20625 per name; A reopening gives two names=.4125; B=.20625; .005 gives.034375 per name | Exact oracle/test values PASS; daily max survives offset/cover, closes once | Missing short marks/prior unclosed session ->incomplete, even zero rate | PASS / HOLD |
| 11. Strict emergency boundary | `src/lstm_data/p3_risk.py:11`; `src/lstm_data/p3_engine.py:279` | G109.9/110/110.1%: only last triggers. Passive >100 does not resize; new entry halted restsession | Three threshold cases PASS; delayed/canceled close keeps actual exposure; emergency partial long12.375, total fee afterhalf6.1875, flat9.90 | E<=0/missing marks gives no fictitious leverage; sleeves end only after real synthetic completion | PASS / HOLD |
| 12. Failed pair, missing exit and retry | `src/lstm_data/p3_engine.py:300`; `src/lstm_data/p3_execution.py:36` | Partial pair:cash7523.7625 then9997.525 after causal flatten; missing14:33 then explicit14:34 ->cash9995.05/fees4.95 | Exact hand rows PASS; hourly substitute rejected; partial/canceled minute correction retained | Both contemporaneous pair references required before attempting; no label-valid gating or terminal sale | PASS / HOLD |
| 13. Clock, overnight and ambiguous priority | `src/lstm_data/p3_replay.py:52`; `src/lstm_data/p3_engine.py:395` | Delayed14:36/18:36 keeps original14:30/18:30 proxies; exit publication18:31 permitted, entry publication14:31 disallowed. Holiday/earlyclose carries holdings to next legal minute | Clock/DST/earlyclose tests PASS; action carry claim persists; terminal/overnight funding NAV=None | Same-time action+fill, competing entry+exit and separate same-time frames fail closed; no historical minute fill inferred | PASS / HOLD |
| 14. Preservation, permissions and checks | `src/lstm_data/p3_domain.py:68`; `checks.json`; `preservation.json` | 489 original file SHA +257 raw stat identities +7 original module interfaces unchanged;16 P2 holds,7 blockers,0/40 neural pairs retained | 422 full tests;84 focused;78 Python files,0errors/0warnings;Ruff/AST/diff PASS;26 carried P3 holds | No API/credentials/source activation/confirmation/P3.5/P3.6/P4/Git mutation | PASS / HOLD |

## Evidence locators

All files below are in `reports/data_audit/ta_p3_engineering_2026-10-11_230724`:

- `expected_vs_actual.json`: 44 PASS rows, including independent cash/share reconstruction.
- `synthetic_ledger.json`: nine linked journals, every event has universe, parent, time and synthetic scope.
- `scenario_matrix.json`: 24 fresh expense/reject/veto/exception paths, no empirical performance.
- `alternate_universe.json`: non-default reordered names, alternate offset journal, all44 oracles and24 scenario hashes.
- `phase_gates.json`, `focused_pytest.txt`, `full_pytest.txt`, `basic_pyright.json`, `checks.json`, `preservation.json`, `integration_manifest.json`.
- `api_handoff.json` and additive `docs/track_a/P3_SYNTHETIC_API_v1.md`.
- `p3_deferred_work_register_v1.json` and additive `docs/track_a/P3_DEFERRED_WORK_REGISTER_v1.md`.

## Trace IDs

| Canonical case | Full trace identity | Events |
|---|---|---|
| BUY_SELL | `73f3be3d493ed0739353a5f8851d5b45eeaff823aec3e65544bd6373cb871fad` | 13 |
| EMERGENCY | `0fd7f375fad6cbb0c901dc8b7c312656d034129f7e1983528ecffb11ddebbfec` | 47 |
| MISSING_EXIT | `6cdfb304cbede68772f53c80aa008076ab34db2d22692c054a455329abf525a6` | 37 |
| OFFSET | `99d338b4568431d9cf7fcb1e28078f30b142335e0aeedecb482cfc9906aad469` | 39 |
| OVERNIGHT | `2da84eefa69ab4e0561ec44a49fb6ed8b877512de5b98f858399f5acda4b1cf4` | 27 |
| PARTIAL_PAIR | `786470f1c883bbf1fdd2891311a092a4838c38ef900f84828cb2cf12fa0fcae1` | 23 |
| POLICY_A | `bebb7bb4e1ad54942d0d7dfd586109a75d401f0d466c9674f13f319e9528c01c` | 74 |
| POLICY_B | `933ebc91f1460db0b7655aebb35c26dc83b34b6625c5b8e548d12af227ee04ce` | 51 |
| SHORT_COVER | `9926c50baae19fb6a79963bfaf9c72ef0151d6b8bb8f973eed0045aed4cbfd67` | 13 |

## Remaining causes

**NOT DONE — missing data:** native168 gaps/15 clusters; inactive candidate1183/1502=78.76% versus90%; historical publication/action vintage; real48×16/48×5 source/population/fitting; actual minute fills/marks/borrow/overnight funding. Genuine empirical metrics are unavailable, not zero.

**NOT DONE — approval/policy:** joint/course/source/SPY/proxy activation; minute-exception or explicit shared hourly amendment; undocumented simultaneous ordering; human engineering/scientific review; exact Git integration. Original USA500 remains archival, CURRENT_PROTOCOL unchanged. P2-DEF-015 and P3-DEF-003 explicitly retain the hourly-only exception hold.

No scientific self-approval. Review this card and exact manifest, then provide any corrections or a separate explicit integration/later-phase instruction.
