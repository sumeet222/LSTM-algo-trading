# Market-source handoff

Run from the repository root in the documented environment. The v2 default selector
uses only SPY/SIP/raw/30Min and the original source version/store. V1 remains archival.

```python
from lstm_data.market_source import MarketSource, load_market_history
from lstm_data.market_features import window_from_history

source = MarketSource.load()
history = load_market_history(source)  # all 11 SHA/parameter-verified chunks required
window = window_from_history(history, "2020-07-01", 1)
```

Currently the loader raises `MISSING_SPY_PARTITION_NO_FALLBACK`; it consumes no network.
After acquisition, it calls the existing `hourly_archive` and `history_from_archive`.
Complete hours exclude closing stubs; the genuine terminal interval supplies each
daily close. Extended native bars remain in the raw archive. No derived Parquet is saved.
Publication remains UNKNOWN and split scope remains unverified.

`window_from_history(history, session, origin, floors=None, scaler=None, *,
allow_synthetic=False) -> MarketWindow` composes the existing `scheduled_window`,
own-step `measures`, `vector`, and `standardized_window`. Missing certificates return
an explicitly blocked window; the function never fits them. UNKNOWN publication wins
over a missing floor when applicable. Values are either None or exactly 48×5; masks
remain separate. Metadata includes scheduled ends, source IDs, per-step source reasons,
source version and certificate references. When a scaler is absent, the reason is
`MARKET_SCALER_CERTIFICATE_REQUIRED`; source causes remain in `step_reasons`.

All original D7 equations remain byte-identical after removing the additive import,
window metadata and composition function (verified by baseline SHA reconstruction).
U2 retains absolute log RMS60; U4/U5 lock to the preceding session. All original tests
remain intact. Floors/scalers in the positive smoke use synthetic training-only data
with explicit opt-in. Historical rows are never assigned synthetic availability.

`market_source.archive_qa(source)` computes exact calendar/year/quarter/month/DST,
session type and origin denominators from the full source, missing windows and raw
48-step retention. Its raw mask is structural only. The existing `qa` command emits
`source_qa_full_period.json`; it requires the full archive and performs no fit.
`spy_completion.archive_complete(source)` requires all fixed keys, contiguous request
bounds, source SHA/schema uniqueness and verified terminal-response receipts. Coverage
QA is separate: sparse but exhausted partitions cannot create a calendar coverage PASS.

Real canonical traces are deferred. The three inherited pilot sample traces in
`market_source_integration.json` are explicitly identified as pilot-derived and
UNPERSISTED_SOURCE, with pilot/frame/request identities; none are represented as
durable canonical native rows. Their D7 measures correctly block PUBLICATION_UNKNOWN.

Next: approve a feasible acquisition resource policy, acquire/resume the same archive,
run source QA and canonical training-era traces, reconcile actions/publication,
then separately review scientific fitting and activation. FT0=16, market=5, MC0=21,
hidden width32, five-stock forecasts, target/proxy/maturity/M2/C01 and 0/40 pairs remain
unchanged. No downstream FT0/model/backtest implementation occurs here.

For another machine, transport_journal_proof.json binds the ignored canonical journal
SHA and its new eight records to the retained nine-line historical evidence prefix.
It is a read-only proof, not another active counter. Verify exact reconstructed bytes
before adoption if the canonical journal is absent; never overwrite an existing journal.
