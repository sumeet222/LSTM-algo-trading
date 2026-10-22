# Package 018D minute-source intake and hourly QA

The current human amendment limits intake to **July 2010–March 2026**, 189 monthly
files at `mito0o852/OHLCV-1m` revision
`776328445b7ac6e7815ef3a483e9c8ded1eb6d56`. The 411-file upstream listing remains
provenance; it is not authorization to process earlier files. No modeling interval
has been selected. All 20 stocks retain their canonical order.

The live packet is
`reports/data_audit/ta018d_hf1m_long_2026-10-22_155547/`. Read `active_scope.json`,
`dataset_identity_preflight_018D.md` and `data_quality_issue_register.md` first.
The scoped checkpoint is `month_checkpoint_scope_201007.json`. Earlier checkpoint
versions and completed/partial pre-scope files are preserved and remain included
in the 10,000,000,000-byte additional occupied-storage accounting.

## Resume on the current machine

From the repository root, using its documented `.venv`:

```bash
.venv/bin/python -B -m lstm_data.hf_minute_long --run --out reports/data_audit/ta018d_hf1m_long_2026-10-22_155547
```

Use the same output packet to reuse verified source/derived checkpoints. Never
start a second acquisition worker against these paths. Checkpoint states distinguish
pending, in progress, verified raw, raw QA done, hourly done and failed/blocked.
Networking failures are recorded without hidden automatic retries. Rerunning the
command resumes the incomplete month and skips verified completed months.

After all 189 scoped months finish:

```bash
.venv/bin/python -B -m lstm_data.hf_minute_long --report --out reports/data_audit/ta018d_hf1m_long_2026-10-22_155547
```

The report command checks committed hashes, reconstructs representative hours
directly from raw observations, creates compact coverage matrices and unselected
candidate intervals, and performs source-regime diagnostics. Its optional old
provider comparison reads only a hash-bound cached training source whose entire
footer proves it predates July 2024. It never requests old data or reads protected
model outcomes.

The scoped checkpoint, QA resume receipts and source footer statistics contain
private price cursors/statistics and remain ignored/local, along with numerical
reconstruction and provider examples. Compact acquisition manifests, checksums,
coverage counts and issue summaries provide the shareable audit map. A new private
machine regenerates its own source and resume artifacts; do not add those local
price-bearing JSON files to Git.

## Layers and interpretation

`data/raw/hf20_hf1m_long_v1/<revision>/raw_1m_selected/` contains all selected source
records, including extended hours, conflicts and invalid observations. Original
values/order and source row-group/global-row provenance remain intact. The verified
March 2026 extract is referenced in place from the earlier 018C namespace rather
than copied. If that optional cache is absent on another machine, March is acquired
from the same immutable upstream file.

The `data/processed/hf20_hf1m_long_v1/<revision>/qa_v2/` tree separates:

- `canonical_observed`: identical copies collapsed once; conflicts excluded in full;
  invalid records excluded. Genuine means recorded source evidence, not independent
  issuer/trade correctness or publication certification.
- `fill_proxies_cap5`: a delta over canonical observations, not a duplicated full
  numerical store. Synthetic OHLC all equal the latest earlier unambiguous
  same-session close; zero volume is an unknown-volume placeholder. Canonical plus
  this delta is the logical filled-minute representation.
- `raw_record_classification`, `minute_quality_issues`, `hourly_quality_issues`:
  provenance-linked source, reconciliation, fill and aggregation evidence.
- `hourly_ohlcv`: full hours from the actual exchange session open plus separate
  closing stubs, with genuine boundary, completeness, missingness, proxy and
  observed-volume flags. Empty hours retain missing prices.
- `ticker_session_coverage`, `fill_sensitivity`: actual expected/observed/valid
  coverage and the two-minute versus five-minute proxy comparison.

Because earlier files are preserved, **do not glob a physical dataset directory**.
Use only files allowlisted in the scoped acquisition/QA receipts and the final
`complete_acquisition_manifest.json`. The hourly coverage projection has its own
allowlist manifest. Empty issue partitions may be skipped by their recorded row
count. No old Alpaca or Twelve Data data are pooled into these stores.

Proxy eligibility is evaluated using only information within the completed bin.
It never uses later-hour prices or observations to revise an earlier completed
hour. Long gaps already known to exceed five minutes remain unfilled. A short
trailing proxy can precede a subsequently discovered longer outage; that endpoint
remains nongenuine and is not a verified forecast/label boundary. Session openings,
empty hours and action-uncertain bins receive no fabricated prices. No overnight,
cross-stock or pre-listing carry is performed. Nominal completion/availability
fields express the arithmetic clock, not attested historical vendor publication.

All genuine outliers and conflicting source versions remain recoverable. No split
factor, volume conversion, clipping or price smoothing is inferred. Candidate
strict/moderate/broad source-coverage standards are diagnostic comparisons, not
final model masks. The old STOP_RIGHTS and 018C STOP_QUALITY audits remain intact.

## Reproduce on another authorized private machine

Use the repository's authoritative setup and existing dependencies. No new login,
token or package is required. In a fresh packet, copy the reviewed identity,
permission, active-scope receipts and identity Markdown from this packet, then run
`--verify-only`, `--run` and `--report` against that packet. `--verify-only` is for a
fresh packet; an existing verified immutable manifest need not be fetched again.
Do not copy raw vendor data to a teammate without separately established rights.
Public accessibility and the human-reported private-research permission are not
independent licensing or redistribution certification.

Focused checks:

```bash
.venv/bin/python -B -m pytest tests/test_hf_minute_long.py tests/test_hf_minute_boundary.py tests/test_hf_minute_preflight.py -q
.venv/bin/ruff check .
```

Use the existing `scripts/check_python_types.py` command with the local Pylance
extension's `dist` path to reproduce basic-severity editor parity. No source path
depends on a username. No features, targets, scales, final splits, predictions,
training, trading or research-pair expenditure are authorized here.
