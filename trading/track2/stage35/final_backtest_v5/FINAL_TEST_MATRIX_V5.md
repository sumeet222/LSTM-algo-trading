# V5 acceptance and validation evidence

Final execution code fingerprint: `9e093b3f6a62`. No tests were skipped, marked xfail or weakened for this task. The complete selected regression command passed **255 tests**, including Stage012, Stage35 V1/V2/V3/V4/V5 and nine original neural/magnitude IO tests. The original pre-change baseline passed 234 tests.

| Requirement | Implemented witness and actual receipt |
|---|---|
| V5-T01 protected identities | H0 SHA256/mtime inventory; final before/after receipt. Original/Phase2/Phase3/Stage012/V1–V4 source artifacts unchanged. |
| V5-T02 actual later bar | Pure wait/execute/expire state machine; source-backed AVGO 16:33 absent → actual 16:34 reference; original submission retained. |
| V5-T03 AVGO requests | EQUAL −2 and S2C −3, qualified 16:34, observed/post 16:37, source hashes, physical/virtual/cash/fees in final witness. Strict V4 remains unresolved and not financially comparable. |
| V5-T04 no entry bar | Synthetic all-absent lifetime reaches explicit simulated expiry; no broker-cancel claim or backdated fill. |
| V5-T05 delayed exits | No entry deadline on exits; inventory, carry and claims persist; terminal unresolved prevents certification. |
| V5-T06 valuation separate | Pending order does not invalidate known inventory NAV; stale/unknown marks cannot become executable bars. |
| V5-T07 reconciliation | Opposed and partial virtual legs, physical net, restricted proceeds and cumulative external fee tested; no internal external-fee duplication. |
| V5-T08 clocks/calendar | Normal/half-day/DST/holiday/exceptional closure and receipt 1/2/5, nominal+10 deadline covered by combined regression and pilots. |
| V5-T09 source pilots/restart | Five final-code windows pass; June 8 checkpoint replays June 9–11 events/daily/cohorts byte-identically after decompression. |
| V5-T10 release/full runs | Negative release tests reject fake PASS, absent proof, source/code drift and wrong scope before financial source access. Full-run status is recorded by the suite manifest, never inferred from tests. |
| V5-T11 source causality | Frozen source/sign/control identity, no future F09/label selection, predecision volume only, future-bar mutation cannot change already submitted quantity. |
| V5-T12 strict reference | V4 policy, failed pilot and odd-lot receipts preserved. No cleaned V4 Sharpe or false V4/V5 equality claim. |

Additional numerical defects discovered and corrected additively: multi-year price-time integral uses arbitrary-size integers rather than int64; OGN virtual pro-rata allocation uses exact attoshare residual ownership. The first funded failure and its code/checkpoints remain intact. The OGN adapter preserves source terms, prices, fees and tax allocation and changes no signal or strategy parameter. A read-only recovered prefix comparison proves 522,866 pre-spinoff events, 832 daily records and 89,663 cohort records unchanged. See `OGN_ROUNDING_CORRECTNESS_DELTA_V5.md`.

Exact reproducible commands and return codes are in `audits/ENGINEERING_ACCEPTANCE_V5_9e093b3f6a62.json`:

```sh
.venv/bin/python -m pytest tests/track2_stage012 tests/track2_stage35 tests/track2_stage35_completion_v2 tests/track2_stage35_completion_v3 tests/track2_stage35_v4 tests/track2_stage35_v5 tests/test_hf20_s2c_ca.py tests/test_hf20_mag_c3_io.py -q
.venv/bin/ruff check src/lstm_data/trading/track2/stage35/final_backtest_v5 tests/track2_stage35_v5 --select E,F,I
.venv/bin/pyright src/lstm_data/trading/track2/stage35/final_backtest_v5 tests/track2_stage35_v5 --pythonpath .venv/bin/python --outputjson
```

Ruff passes. Owned basic types: 13 files, zero errors/warnings. The actual final full Pylance run checked 694 files and reported **30 existing errors**, not a globally clean repository: 27 frozen replication diagnostics plus three pre-existing Plotly viewer-test diagnostics in `tests/test_target_range_history.py` (Figure meta/annotations). Neither unrelated file nor frozen replication was edited. Full command, resolved installed Pylance distribution and diagnostics: `audits/POST_OGN_FULL_TYPE_COMMAND_V5.json`, `audits/POST_OGN_FULL_PYLANCE_V5.json`. Earlier 27-error receipts are retained rather than substituted for this actual final 30-error result.

Editor verification remains a human action: select this repository `.venv/bin/python`, retain basic severity, restart the Pylance language server and refresh Problems. The command-line receipts establish reproducible checks; they do not claim that a human refreshed the editor.

Financial reconciliation uses Decimal arithmetic, maximum USD balance residual threshold 1e-8 (unchanged V4 material threshold), exact physical/virtual signed shares and explicit cent/attoshare residual allocation. Base scenario maximum residual 5.63e-21; no terminal pending/unpriced/incomplete records. Per-scenario actual statuses and residuals are authoritative in their run receipts.


## Final recovery and financial census

Fresh recovery tests: 255 passed, Ruff E/F/I passed, owned basic types13 files/0 errors/0 warnings. Full installed Pylance694 files/30 unchanged errors (27 frozen replication +3 unmodified Plotly viewer-test diagnostics), zero added. Exact commands/stdout/stderr and diagnostic comparison: `recovery/20261110T124734Z/RECOVERY_VALIDATION_COMMANDS.json` and `REPOSITORY_DIAGNOSTIC_COMPARISON.json`. Arrow emitted sandbox sysctl CPU-cache-query warnings during chart rendering; the read/render succeeded, no market/source mutation.

All24 scenarios completed/reconciled. Per-case SHA checks/ending typed states/8,040 daily NAV identities verified; all5 current-code pilots and pre-AVGO checkpoint replay remain valid. `audits/FINAL_FROZEN_AND_SOURCE_INTEGRITY_V5.json` verifies SHA256 +mtime for10,410 protected objects and227 original partitions. Presentation-only equivalence/daily checks are in `presentation/ADDITIONAL_DESCRIPTIVE_TABLES_V5/DAILY_BALANCE_AND_EQUIVALENCE_CHECKS.json`. No skips, XFAIL, weakened material threshold or frozen diagnostic repair. Editor Problems refresh is human-confirmed later; no global type-clean claim.
