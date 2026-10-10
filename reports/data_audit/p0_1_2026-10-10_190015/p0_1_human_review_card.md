# P0.1 — Eight human inspection targets

Use the current clone root and its existing environment. Commands below are offline; none loads `.env`, downloads data or computes performance. Recorded values are in [checks](p0_1_checks.json). Stop after review; the single proposed next package is the P0.2 infrastructure delta described in [review](p0_1_existing_work_review.md).

| # | Actual location / command | Expected and observed |
|---:|---|---|
| 1 | `src/lstm_data/aggregation.py:aggregate_session_hours:63`; `tests/test_aggregation.py:test_complete_session_pairs_and_stub_without_duplication:31` | Synthetic first pair open100/high103/low99/close102/volume20; 7 outputs, last 30min stub, volume conserved. PASS. No aggregate VWAP. |
| 2 | `reports/data_audit/task01_stock_qa_compact/stock_qa.json:510`; `tests/test_aggregation.py:test_missing_constituent_emits_mask_and_never_manufactures_ohlcv:50` | Actual JPM2021-04-19: 12 missing starts from14:00Z through19:30Z, one09:30ET source start recorded. Global168/15. Synthetic missing second constituent: 6 outputs, first window omitted, mask incomplete. PASS. |
| 3 | `src/lstm_data/calendar.py:schedule:9`; `tests/test_aggregation.py:test_early_close_and_dst_windows:60` | Nov27 early close: 3 hours +stub, end18:00Z=13:00ET. Mar12→Mar15 2021 open14:30Z→13:30Z, stays09:30ET. Tests PASS; no 240-minute label computed. |
| 4 | `configs/track_a_bulk_approval_2026-10-10.json:2`; `src/lstm_data/store.py:check_approval:147` | Existing approval covers30Min/split/aggregation; fingerprint `bcf0f99d5ac2dcd5a91889e477467096fbca960482d7ef40ddcdb5f600fe668e`, pilot SHA `33ee29e125e3c8f49a47c2fc9243cdf146bfed8e24ade614932c48bf8050f454`. Offline check PASS. |
| 5 | `reports/data_audit/task01_course/course_manifest.json:98`; `src/lstm_data/course.py:audit_course:14` | 29,510 rows; last localJuly1 00:00; one beyond named dates; SHA `ba78d6bf933f0aca4dfcdedb69454d19aa29bfed84481b6ba1bcccdaf7b1634a` matches source. Source semantics still unknown. Original audit function reads full frame: do not rerun it for this card. |
| 6 | `src/lstm_data/alignment.py:asof_diagnostic:51`; D2 design §3.2 | Counterexample below reports60-minute availability-age andusable=True despite120-minute period-end age. FAIL for D2 reuse; historical diagnostic is not production gate evidence. |
| 7 | `.venv/bin/python -m pytest -q`; `.venv/bin/ruff check src tests` | Current60 tests PASS in5.06s; Ruff PASS. Suite does not cover D2 freshness distinction, features/targets/portfolio/model readiness. |
| 8 | `src/lstm_data/cli.py:runtime:28`; `git status --short --branch`; `git rev-list --left-right --count HEAD...@{upstream}` | Runtime contains Git SHA/packages/config fingerprint but no dirty-content hash/ledger. HEAD92aecd1, upstream0/0. Start clean; end only five new reports untracked. Older runtime base SHA reflects historical uncommitted work. |

## Reproduce the small diagnostic mismatch

This is synthetic, never a proposed market delay or a licensed source observation. The stock input ends before the chosen availability; only the market freshness rule is being compared. Under provisional timestamp-as-close, the market timestamp is the candidate period end.

```bash
.venv/bin/python - <<'PY'
import pandas as pd
from lstm_data.alignment import asof_diagnostic
def row(timestamp, **extra):
    return pd.DataFrame(dict(timestamp=[timestamp], open=[100.],
        high=[102.], low=[99.], close=[101.], volume=[10.], **extra))
stocks = row('2020-07-01T14:00Z', symbol=['AAPL'],
             available_at=['2020-07-01T15:00Z'])
market = row('2020-07-01T13:00Z')
j, _ = asof_diagnostic(stocks, market, index_delay_minutes=60,
                       max_age_minutes=90)
r = j.iloc[0]
print(float(r.age_minutes), bool(r.usable_candidate),
      (r.decision_time-r.index_timestamp).total_seconds()/60)
# Observed: 60.0 True 120.0. D2 freshness requires False at age120.
PY
```

For a bounded source-store recheck, use footer metadata and streamed hashes rather than `load_store` or `read_verified` (both load observations). This auxiliary read-only recipe reproduces target4's canonical-source evidence without copying a table:

```bash
.venv/bin/python - <<'PY'
import json
from pathlib import Path
import pyarrow.parquet as pq
from lstm_data.config import load_config, digest
from lstm_data.store import monthly_requests, chunk_paths, check_approval
c = load_config(Path('configs/track_a_data.json'))
check_approval(c, Path('configs/track_a_bulk_approval_2026-10-10.json'))
rows = size = count = 0
for p in monthly_requests(c):
    f, m = chunk_paths(c['_stock_store'], p)
    x = json.loads(m.read_text())
    assert x['params'] == p and x['sha256'] == digest(f)
    n = pq.ParquetFile(f).metadata.num_rows
    assert n == x['rows'] and f.stat().st_size == x['size_bytes']
    rows += n; size += f.stat().st_size; count += 1
print(count, rows, size)  # 60 159008 5845266
PY
```

No ledger service was created. P0.2 inspection would cover exactly five surfaces: current-protocol hashes, synthetic failure propagation, append-only restart handling, code/config/source lineage, and dry-run/human-release/40-pair guards. No scientific source prerequisite is upgraded by that package.

**AWAITING HUMAN REVIEW — NO AUTOMATIC NEXT PACKAGE.**
