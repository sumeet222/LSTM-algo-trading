# LSTM Algorithmic Trading Project

Group project investigating shared LSTM models for short-horizon
cross-sectional equity prediction with broad-market conditioning.

See `AGENTS.md` for repository and development guidelines.

Future **Track A market-state source work uses Alpaca SIP SPY** under
[TA-D2-MARKET-SPY-001](docs/track_a/decisions/Track_A_SPY_Market_Source_Amendment_v1.0_2026-10-11.md).
SPY is an ETF information proxy, not a sixth target or traded instrument. Frozen D7
USA500 headings and course commands below remain historical references. The protected
protocol pointer, scientific gates and joint approvals remain pending; no model is activated.
The typed source entry point is:

```bash
python -m lstm_data.market_source plan --report reports/data_audit/ta_mkt_spy_2026-10-11
```

TA-MKT-SPY-003 completed the approved archive: **11/11 immutable partitions,
41,861 native bars**, including all **17,197 expected RTH half-hour slots** across
1,327 sessions. Both first-July 2020 market windows have the required warm-up.
The canonical journal counts **129/900** cumulative attempts: 13 inherited,
114 acquisition pages and two bounded corporate-action queries. SHA-verified
resumption was tested with zero GETs. No partial diagnostic cache is claimed.

[The review card](reports/data_audit/ta_mkt_spy_003_2026-10-11/human_review_card.md)
separates completed engineering from publication/action and scientific HOLDs.
The additive [v3 policy](configs/track_a_market_spy_v3.json) is the current
source CLI default (900 attempts / 32 response pages / 3 attempts per page /
256 MiB); original v1/v2 configs, source identity and reports remain unchanged.
The prior 240-attempt blocked result is preserved in its original evidence.

```bash
# Read-only selector.
python -m lstm_data.market_source plan --report reports/data_audit/ta_mkt_spy_003_2026-10-11
# Approved acquisition / SHA-verified completed resumption.
python -m lstm_data.spy_completion --env-file .env --report reports/data_audit/ta_mkt_spy_003_2026-10-11
# Offline measured QA + canonical D7 traces; choose a NEW output directory.
python -m lstm_data.spy_qa --report reports/data_audit/<new-report-directory>
```

[The API handoff](reports/data_audit/ta_mkt_spy_003_2026-10-11/market_api_handoff.md)
documents `load_market_history` → `window_from_history`. Real historical source
publication remains UNKNOWN; action certification and empirical floor/scaler
approval remain pending. These functions preserve masks and each step's own
cutoff, and do not fit empirical transforms. SPY has no portfolio position or
dividend-cash leg. CURRENT_PROTOCOL and G0–G4 remain unchanged; no training,
backtest or confirmation performance is activated.

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

During Task 01, the researcher approved a provisional **USA500 timestamp-as-close** assumption on
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

## Offline evidence review (P0.2)

```bash
lstm-data evidence                         # Read-only metadata; no source rows or secrets
lstm-data evidence --mode diagnose         # Synthetic F01 counterexample; expected exit 2
lstm-data evidence --help
```

[CURRENT_PROTOCOL.json](configs/CURRENT_PROTOCOL.json) pins the five governing
documents and existing evidence hashes. The [ledger](reports/audit/track_a_events.jsonl)
preserves P0.1 blockers. Neither grants scientific approval. G0/G1/G2 remain blocked;
the alignment diagnostic's F01 period-end freshness defect is now repaired and
verified by its existing synthetic regression. Actual source clocks remain unknown.
See the [evidence contract](docs/track_a/p0_2_evidence_harness.md) for schemas, explicit
append/report commands, failure handling and the confirmation lock. The evidence
command never loads `.env`, calls a provider, or executes research jobs.

## Candidate clocks (P2.1)

`lstm_data.clocks.session_clock("2020-07-01")` reuses XNYS sessions, separates
complete anchored hours from the terminal stub, and stores UTC keys.
`forecast_origins(clock)` produces two candidate plans: nominal ET entries/exits
10:33→14:33 and 11:33→15:33. These are planned timestamps, not fills.
`execution_plan(clock, 1, issued_at=<aware timestamp>)` preserves actual issuance,
rejects issuance outside cutoff through cutoff+5 minutes, and plans
`ceil(issuance + 1 minute)` entry followed by a 240-minute same-session exit.
Omitting `issued_at` explicitly marks nominal issuance `PLANNED_SYNTHETIC`.

`SourceObservation` separates native labels, period boundaries and publication
bases. `observation_at_cutoff` rejects unknown clocks and checks each historical
step's own cutoff; issuance never expands its information set. Documented clocks
require an evidence locator and remain caller assertions requiring source review.
Synthetic/assumed records require `test_scenario=True`, are non-verified, and are
for isolated tests only. Legacy aggregation's assumed `available_at` is insufficient
for this contract. `OriginBoundary` leaves actual entry eligibility, label validity
and execution outcome uncomputed (`None`). Callers must retain every scheduled
history slot, including missing ones; no 48-step windows are built here.

Run the offline acceptance tests with `python -m pytest tests/test_clocks.py -q`.
The researcher reports cross-track agreement on 240 continuous minutes and a future
conventional S&P 500 source. Formal versioned registration is pending. G0–G2 remain
blocked, current USA500/U1–U5/MC0–MC2 joins remain HOLD, and P2.2 requires separate
authorization plus its source/label prerequisites. No source replacement is installed.

## Synthetic target interfaces (P2.2A)

`lstm_data.labels` reuses P2.1 plans and the canonical AAPL/JPM/JNJ/WMT/CAT order.
`MinuteReference` requires an exact one-minute raw `open`, source row ID and version;
`minute_reference` never substitutes the next minute, another name or an adjusted price.
`causal_eligibility` accepts upstream `ForecastEvidence` and entry references only.
Its entry flags cover source/clock/reference eligibility; portfolio admission and fills
remain P3 work. Future exits and action records are excluded from that interface.

`label_sample` separately computes the five-name log-return median/unscaled MAD,
preserves source IDs and maturity, and requires explicit `ActionScope` evidence for
no-action or split/share conversion. Missing exits invalidate the label without
changing causal entry flags. Unknown publication produces `MATURITY_UNVERIFIED`;
no dividend cashflows or publication delays are invented. Reference availability
describes when that open is supported, not an assumed completed-minute-bar latency.

`fitting_window` supplies the frozen WF1/WF2/preconfirmation date boundaries and
63-exchange-session inner tail. `fitting_membership` purges outcome/maturity crossings
and enforces the actual fitting timestamp; historical input lookback is not embargoed.
Date stops are exclusive next-period ET midnight, with UTC keys.
`fit_tg0_floor` accepts only eligible inner-training/refit labels, fits
`max(1e-4, 0.1 * median(training MAD))` once, and records fitting keys/exclusions.
`apply_tg0_floor` reuses that frozen floor without clipping or refitting.

Run `python -m pytest tests/test_labels.py -q` without data or secrets. Examples use
explicit `test_scenario=True` and synthetic source/action/input evidence. Supported
DOCUMENTED metadata remains a caller assertion requiring review. ASSUMED publication
is retained but not activated. Every output has `research_ready=False`, execution
is `NOT_EVALUATED`, and market branches remain HOLD. Production label integration,
inner-tail adequacy checks and source/approval closure need separate authorization.
