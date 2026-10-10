# LSTM Algorithmic Trading Project

Group project investigating shared LSTM models for short-horizon
cross-sectional equity prediction with broad-market conditioning.

See `AGENTS.md` for repository and development guidelines.

Task 01 implements data intake and audits only. No targets, features, model training,
trading or final experiment definitions are implemented.

## Setup

Use Python 3.11–3.14 and run from the cloned repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
ruff check src tests
```

`pyproject.toml` is the authoritative dependency specification. Version ranges support
different Python/platform wheels; each execution records the actual package versions
and Git SHA in `runtime.json`. The initial implementation was tested on Python 3.14.
No global packages or manual `PYTHONPATH` are required.

## Data commands

Place the supplied original CSV at the documented path in [data/README.md](data/README.md).
Raw files, intermediate pilot samples and local `.env` files are already gitignored.
Course data must be supplied by the researcher; the repository does not redistribute it.

```bash
lstm-data --help
lstm-data source-audit
lstm-data sip-pilot --dry-run
lstm-data download --dry-run
```

For the small live pilot, populate an ignored local `.env` using `.env.example`
(or export the two standard environment variables), then run:

```bash
lstm-data --env-file .env sip-pilot
```

`.env` loading is explicit and never overrides exported variables. Existing
`ALPACA_API_KEY` / `ALPACA_API_SECRET` aliases also work. Credentials are never printed;
only the fixed historical market-data GET endpoint is called. No trading/account API
or subscription purchase is implemented. Missing credentials or a failed access/timing
gate produce a useful report and exit code 2. There is no IEX fallback.

Bulk acquisition needs successful SIP **and** native-bar timing evidence, followed by
explicit researcher approval covering the config and split adjustment. Inspect
[data/README.md](data/README.md) before preparing an approval. Then:

```bash
lstm-data --env-file .env download --approval configs/track_a_bulk_approval_2026-10-10.json
lstm-data stock-qa
lstm-data alignment --max-age-minutes 90
```

The native `1Hour` pilot failed session anchoring. The researcher approved `30Min`
source bars and session-anchored hourly aggregation; the new seven-window pilot
passed. The default config now uses `30Min`. One canonical source store preserves
provider bars; `aggregate_session_hours` materializes hourly windows in memory.
Missing constituents produce diagnostic masks, not fabricated OHLCV. Closing stubs
retain their actual 30-minute duration/availability. Aggregate VWAP is omitted because
provider VWAP may use a different volume denominator than source `volume`.
The researcher approved full acquisition with split adjustment after the pilot passed.
That authorization and the matching pilot hash are recorded in
`configs/track_a_bulk_approval_2026-10-10.json`; resumption reuses the same approval.

All five commands support `--dry-run` without network, credentials or writes.
Reports use new directories and never overwrite previous runs. `--output` can select
a new directory. Configuration paths resolve relative to the parent of `configs/`,
and data locations stay project-relative. A config's parent directory must therefore
be the project's `configs/` directory. Invoke from the repository root or pass
`--config /path/to/clone/configs/track_a_data.json`.

The researcher approved a provisional **USA500 timestamp-as-close** assumption on
2026-10-10. Provider semantics and publication latency remain unverified. Alignment
compares that assumption with a one-hour-delay sensitivity scenario; the 90-minute
staleness bound is diagnostic, not a frozen model rule.

Task 01 evidence:

- [Course audit](reports/data_audit/task01_course/course_audit.md)
- [Live SIP pilot status](reports/data_audit/task01_sip_pilot_network_retry/sip_pilot.md)
- [Decisions and coverage](reports/data_audit/task01_decisions.md)
- [Live pilot follow-up](reports/data_audit/task01_live_followup/live_followup.md)
- [Approved 30Min pilot](reports/data_audit/task01_30min_pilot/sip_pilot.md)
- [Final intake handoff](reports/data_audit/task01_final_handoff.md)

The approved bulk run acquired 159,008 source bars in 60 monthly chunks (5.85 MB
Parquet). QA records 168 missing RTH half-hour bars across 15 symbol-session pairs;
no source gaps are filled and incomplete hourly windows are masked/omitted. See
the handoff before choosing later research eligibility or trade-clock rules.

Alignment can run on the small pilot samples before full acquisition:

```bash
lstm-data alignment --pilot-report reports/data_audit/task01_30min_pilot/sip_pilot.json
```
