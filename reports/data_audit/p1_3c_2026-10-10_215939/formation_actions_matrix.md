# P1.3C formation and corporate-action readiness

## Formation: existing evidence, no new data

Source: [P1.3B persisted aggregates](../p1_3b_2026-10-10_204558/probe_results.json), matrix and transport locators. Fixed formation date 2020-07-01; exactly 60 XNYS sessions **2020-04-06–2020-06-30**, common to all five. SIP requested, raw/unadjusted 1Day, USD, entity-mapping asof=2020-07-01, limit1000, one response300 rows/no next page. Retrieval 2026-10-11 00:53:53 UTC; this is retrospective retrieval, not then-available publication. ET-midnight labels identify source days, not release times. No raw panel or requery created.

Reported statistic: **L_i=(1/60) sum_d(C_raw,i,d [USD/share] × V_vendor,i,d [shares])**, in USD/session. Fixed threshold USD50,000,000; no alternate cutoff. Chosen for this report's diagnostic, not adopted for eligibility. Exact sums remain in predecessor JSON.

| Primary | Records / unique sessions / denominator | Missing / duplicates / quality defects | Mean C×V USD million | USD50m numerical outcome | Selection support |
|---|---:|---:|---:|---|---|
| AAPL | 60 / 60 / 60 | 0 / 0 / 0 | 12373.671687 | ABOVE (proxy only) | Provisional diagnostic; formal BLOCKED |
| JPM | 60 / 60 / 60 | 0 / 0 / 0 | 2588.086315 | ABOVE (proxy only) | Provisional diagnostic; formal BLOCKED |
| JNJ | 60 / 60 / 60 | 0 / 0 / 0 | 1437.483505 | ABOVE (proxy only) | Provisional diagnostic; formal BLOCKED |
| WMT | 60 / 60 / 60 | 0 / 0 / 0 | 1247.123100 | ABOVE (proxy only) | Provisional diagnostic; formal BLOCKED |
| CAT | 60 / 60 / 60 | 0 / 0 / 0 | 576.226357 | ABOVE (proxy only) | Provisional diagnostic; formal BLOCKED |

All 300 retained aggregates are consistent. No rows were dropped/filled; quality defects include null/nonfinite/nonpositive/OHLC/negative-volume/order defects. Eligible extended-hours volume can enter the vendor daily denominator; eligible-trade rules differ for OHLC and volume. This is neither RTH traded dollars nor a guaranteed low/high turnover bound. Split adjustment must pair prices and inverse volumes; dividend-adjusted prices are a different policy.

| Information layer | Meaning / allowed conclusion |
|---|---|
| Formation-time | Screen would require data genuinely available before 2020-07-01 plus approved dollar-volume/session definition and membership/sector evidence. Historical release/vintage not established. |
| Retrospective retrieval | Current historical vendor values and mapping asof are useful diagnostics. asof is entity mapping, not time-travel publication metadata. |
| Ex-post coverage | 98% overall /95% each sufficiently represented year are later usability filters. Existing half-hour summaries do not certify raw-minute or FT0 annual completeness and cannot become formation-day knowledge. |

**D1 verdict:** the price statistic is underspecified, but extended-hours close×volume is not established as the intended dollar turnover. Explicit human interpretation approval is necessary; replacing the requirement with proxy-based eligibility requires a versioned approval/amendment stating session, statistic, vintage limitation and provisional roster/D8 status. Preferred final evidence is contemporaneously available RTH traded-dollar turnover from eligible regular-session transactions, or qualified minute/half-hour turnover fields/aggregation with consistent trade denominators. Close×volume at finer frequency remains a proxy unless explicitly accepted. No formal primary selection, D8 pair/ranking or backup activation here.

## Source → calculation contract

Reuse [P1.3A action fields and algebra](../p1_3a_2026-10-10_202847/source_readiness.json) and [source discussion](../p1_3a_2026-10-10_202847/formation_and_actions.md), including inherited provider/issuer documentation; no new provider facts claimed.

| Source item | Calculation candidate under D2/D5 | Missing evidence / stop condition |
|---|---|---|
| Raw bars plus split ratios | Immutable raw OHLCV; feature prices adjusted by cumulative split factor and volume inversely. Match factors/events to history, preserve source/version IDs. | Complete factors, share basis, effective timestamp and historical publication/vintage unknown. No dividend total-return adjustment substituted. |
| Raw genuine minute opens | Physical shares, raw execution prices, cash, marked wealth; one canonical minute store. | Entry/exit/retry coverage and approved shared D3 clock required. Current access/probe cannot certify complete fills. |
| Splits | At effective event transform q→kq, reference P→P/k; cash unchanged, no split profit. | Correct ratio direction, fraction/rounding and event-time mapping, missing/duplicate event handling; today's history does not prove origin-time knowledge. |
| Cash dividends | Separate ex-date entitlement/receivable from pay-date cash. Long credit, short liability; no double count in price/return adjustments. | Verified event IDs, currency, per-share basis, ex/record/pay/declaration dates, effective/available times and coverage. No absent events or invented payment assumed. |
| Symbol changes | Stable entity ID, dated symbol mapping, avoid joining different issuers; retain source identifiers. | Mapping effective/announcement times, discontinued symbols and adjustment boundaries unverified. asof alone insufficient. |

Inherited synthetic split: 10×100+50=40×25+50=1050 USD; 100×200=25×800=20000 USD. Inherited dividend: 10×0.77=7.70 USD receivable; under a stipulated ex-price drop, the long mark loss is offset by that receivable. On actual verified pay date, transfer receivable→cash with no new wealth. Short symmetry under the same synthetic premise: mark gain7.70 offset by liability7.70; later cash payment extinguishes liability. This is algebra only, no real event inferred or simulator implemented. Prior AAPL examples distinguish 2020-02-07 ex-date from Feb13 payment and Aug31 split effective date; see predecessor evidence, not a complete five-name event ledger.

Smallest accounting blocker: complete, versioned split/dividend/mapping metadata with coherent price/share/event conventions, plus actual raw minute/retry coverage. Event-publication assumptions remain separate. **G1 BLOCKED.**

## Minimal acquisition sequence — proposal, zero requests authorized/executed here

| Order | Bounded future scope / request estimate | Storage / prerequisites / stop |
|---|---|---|
| P1.3D representative actions/mapping | Reuse preselected AAPL dividend/split illustrations: two narrow event queries and one symbol/entity mapping check. At most four transport attempts total including one retry; no automatic next pages or retries beyond cap. | Target ≤100 records /≤250KB persisted metadata; planning cap, not observed size. Freeze exact documented endpoint/filters, date/ratio/pay-date fields and access first; approve vintage policy separately. Missing dates, unexpected pagination, unsupported mapping or inconsistent adjustment stops. No full actions or bars download. |
| Warmup reach | Offline approved dependency manifest first; then missing split30Min prehistory once. Rough scenario126–160 prior sessions×13 half-hours×5 names =8190–10400 rows, ~1–2MB uncompressed at120–200B/row, plus metadata. Approx7–8 monthly multi-symbol requests if calendar span requires them; exact dates/pages unapproved. | M4 at each step uses d−21/d−126 (105 separated sessions); 48 historical steps add reach. EMA seed+360 good updates+48 context:408 closes; RSI14+140+48:202 closes in no-gap example. Prior calendar lower bound Dec18,2019 is illustrative only. Gaps extend reach. No scaling outside authorized fit history. |
| M2/raw execution and retries | 60 previously matured origin-matched outcomes at each historical step; genuine raw minute references, not computed labels here. Later specifically authorized minute acquisition: inherited2.56–2.73m rows,291–312 monthly pages,77–409MB compressed /256–546MB response sensitivity. | One raw-minute store, reuse existing split30Min source; no per-seed/windows copies. Four fixed slots insufficient for arbitrary exit retries. Joint clock, exact warmup, terminal-retry reach, permissions and resumable page cap must be approved first. Rate/entitlement estimates are historical, not current guarantees. |
| Full actions and annual QA | Only after representative schema passes: count/size plan before complete action pages; action counts unknown, not included in minute estimate. Later QA by sufficiently represented year and symbol, 98%/95% thresholds. | Stop for incomplete event coverage, mapping ambiguity, unavailable minute/retry rows or failed retention. No eligibility gate automatically passes, no bulk scope authorized now. |

Recommended immediate next package is **P1.3D bounded representative action/mapping metadata verification**, not another formation requery or Dukascopy documentation search. Exact queries and maximum attempts require separate authorization after liquidity/vintage decisions. Source-only metadata work does not authorize D8, P2 or fitting.
