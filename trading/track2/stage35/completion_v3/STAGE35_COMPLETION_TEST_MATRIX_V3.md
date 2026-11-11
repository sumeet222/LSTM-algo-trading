# V3 validation map

Tests use actual cached provider fixtures and declared raw observations for source
truth,and fabricated prices for funded financial accounting. No source download
runs inside pytest. Source-backed suites require the documented local authorized
source/model/cache bundle;generic provider failure tests use mocked responses.

| Requirement | Witness |
|---|---|
| Provider auth/429/retry/page repeat/schema/field absence | test_acquisition_and_inventory.py;one retry/backoff,cache immutability,redaction,empty!=zero |
| Actual ex/pay/amount and dedup |267 unique cash records;AppleMay10/May13/May16;coverage totals267,not sum of duplicate providers |
| B/C/D/E/F/G and truth | test_actions_and_fallback.py;May28/29transition,special/nonbusiness hold,14/30/45pay,split-unit carry,staleness,suspension,reference retention,proxy suppression |
| Raw/source factual path |11 actual projected minutes/5 partitions;48OOS partition identities;no adjusted ledger prices;source receipt hashes |
| Ex/pay/split/shared lots | test_event_and_book_integration.py;long/short claims,dated/undated/post2024pay,2:1/1:5/4:1units,old stale mark,unpriced OGN |
| Full action/book/due bridge | Fabricated V2 book plus V3 ex/pay/split/carry engine;attributed cash/claims/physical shares reconcile |
| Clock/borrow/carry |1/2/5receipt,Friday–Monday1/2/5%ACT365 physical short,missing rate,overlap/gap refusal,adjacent journal hashes |
| Restart | Closed JSON schema;exact roundtrip at unpaid claim;binding/hash/class rejection;no pickle/eval |
| Original signals/controls | Prior121 regressions unchanged;frozen131111 forecasts/87557 matched/hash evidence retained;future action mutation cannot change earlier due tape |
| Historical release | Old andV3 entry refuse before loader/mkdir/output;forgedflags/owner/env/source labels/untrusted key fail;raw historical Price cannot enter synthetic book |
| Nonperformance integration | Actual source/action kernel with synthetic endowed quantities;2 frozen original signals/8dimensionless allocations;zero funded history/orders/fills/NAV/returns |
| Source/old evidence integrity |6733 frozen objects+227 source partitions SHA256/mtime unchanged;parent V2 manifest linked |

The first full run passed194 tests. Additional ex-date stress cases and final
certification tooling are included in FINAL_PYTEST.txt for the authoritative final
count. Earlier failures and fixes remain in incremental receipts;none was skipped,
XFAILed or resolved by changing protected inputs.

Exact final commands:

```sh
.venv/bin/python -m pytest tests/track2_stage012 tests/track2_stage35 tests/track2_stage35_completion_v2 tests/track2_stage35_completion_v3 tests/test_hf20_s2c_ca.py tests/test_hf20_mag_c3_io.py -q
.venv/bin/ruff check --select E,F,I src/lstm_data/trading/track2/stage35/completion_v3 tests/track2_stage35_completion_v3
.venv/bin/pyright src/lstm_data/trading/track2/stage35/completion_v3 tests/track2_stage35_completion_v3 --pythonpath .venv/bin/python --outputjson
.venv/bin/python scripts/check_python_types.py --pylance-dist "$PERSISTED_INSTALLED_PYLANCE_DIST"
.venv/bin/python -m lstm_data.trading.track2.stage35.completion_v3.certify --integrity-only
```

The Pylance location above must be resolved from this machine's installed
`ms-python.vscode-pylance-*/dist`,checking bundled/stubs and typeshed-fallback;
it is not another developer's hard-coded path. The actual resolved distribution
is recorded by the full checker. Its basic-severity profile is authoritative.
The first full check found2 new holiday-calendar stub errors plus27 inherited;
V3 now supplies real datetime arguments and the final receipt must show only the
same27 frozen diagnostics. Standalone Pyright alone was insufficient evidence.
