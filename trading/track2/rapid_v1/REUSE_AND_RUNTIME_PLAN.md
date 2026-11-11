# Reuse and runtime plan — rapid v1

The complete root menu and execution prompt were read before implementation. The current execution authorization overrides the menu's proposal-only status and starter-six funding suggestion: all18 defaults are screened, with no result-dependent selection. No strategy outcome has been computed at this freeze.

| Operation | Existing component/cache | Reuse and causal boundary | Calculation/storage |
|---|---|---|---|
| Raw prices, OHLCV QA | V4 market source receipts/canonical genuine minutes + sealed SIP gap supplement | Same raw/share validation; extend projection to high/low and2020warmup; no dependency on LSTM signal partitions | Monthly memory, one shared feature-preparation pass and one financial source pass for all18, not18panels; no persisted raw copy |
| Calendar/endpoint | Stage012 MarketClock; V4 ExecutionCalendar | XNYS legal slots,240scheduled minutes, next strictly later RTH minute;2025 calendar geometry only | Shared cached calendar |
| Standing order disposition | V5 execution.disposition | Known submitted order before effective minute; complete+2receipt; nominal+10entry expiry; exit carry retained | Exact pure reuse |
| Physical/virtual book | V4 Account inherited by V5 | Reuse nav,capacity,inventory,crossing,atomic fills,borrow,claims,split and conservation; replace journal sink with bounded statistics | <=18small accounts; no per-minute dump/checkpoint |
| Mode costs | Frozen retail pricing; new micro quote hook | Source-linked lossless fill-body extraction changes only price/fee equations; retail parity tests; fractional-cent micro commission exact | One cost quote per external fill; no fake NBBO |
| Actions/OGN | V3 load_actions; V5 before_day/special_tick/special_view and exact attoshare settlement | Preserve confidence and signed entitlement/due-bill/CIL; reuse actual old OGN tape. Special disposal has explicit conservative fallback where OGN has no60day ADV | Small state, source pointers, no payload duplication |
| Daily/slot features | No suitable already-derived daily OHLCV cache found; V2 cached arrays are neural-specific | One chronological raw2020–24 preparation, completed-session-only rolling; causal split-genesis units; no future total-return adjustment | Central content-addressed numeric feature cache target<80MB; monthly raw memory<150MB |
| Future risk overlay | Existing original forecasts/matured controls/prefix reference | Retain read-only optional interface; no forward pass, fitting or four-arm screen | Not consumed by direction functions |
| Reporting | V5 definitions/metrics and sealed legacy baseline summary | Stream compact trades/daily records; all18IDs, negative/zero/HOLD cases; no Stage6 statistics | target<200MB total; hard500MB; eachstrategy25MB; anomalies<=100 |

## Shared computation map

M01/M02/M06/M08 share identical received60minute return and prior20same-slot scales; M06 additionally uses currently eligible leave-one-out residuals; M08 uses the same received volume window. M03/M04 share exact opening gap and prior gap scale; M04 adds fixed first-hour confirmation/volume. M05/R03/R07 share completed range/high-low primitives. M07 uses previous20actual-session same-clock next-half-hour returns, not today's future value. M09/R08 share completed overnight/intraday components, with M09 current received intraday only. R01/R02/R04/R06/R09 share completed daily closes/returns/volumes. R05 uses one daily three-pair past60 fit cache. All rolling calculations are once per session/slot/ticker, then reused as immutable views.

## Benchmarks and budgets

Benchmark Jan4–8 2021 and Jan2021, plus fixed source pilots June2–11 2021, Aug24–26 2022, May9–17 2024, Nov27–Dec2 2024. Full financial launch requires source/pilot/accounting tests and a measured runtime extrapolation below two hours (target minutes), <500MB output. If not, redesign before launch; no V5 scenario suite or journal mode. One process preferred. No deletion of old artifacts. Existing V5 ~15.18GB is retained, not called stale/disposable. Free disk at inventory17.36GiB.

A separate feature preparation pass is explicit: it prevents repeated warmup for noncontiguous pilots. The full financial pass shares raw observations and cached features across18 accounts. No per-strategy raw-data traversal. Cached features are not outcomes and cannot provide future closes to the strategy interface.

## Qualifications

Reused exploratory2021–24, fixed survivors, retrospective QA/actions, assumed receipt and borrow, OHLCV proxies without NBBO/locates. Conditional special/ordinary actions retain original taxonomy. No untouched confirmation, deployment, neural campaign, Phase2 substitution or Stage6 audit.
