# Codex execution prompt — HF20 Track 2 fast directional-strategy engine and complete 18-strategy screening

**Authorization:** The project owner authorizes **this task**: build a lightweight research backtesting engine, reuse safe existing infrastructure and precomputed data, and screen **all 18 registered directional strategies** in the agreed **micro** and **retail** configurations, with lightweight diagnostics and compact outputs. This is retrospective exploratory research, not an approval for live/paper trading, LSTM retraining, an expensive V5-style financial sweep, or the independent Stage 6 audit.

**Inputs / research specification:** The owner will place `HF20_Track2_Directional_Strategy_Research_Menu_Micro_and_Retail_2026-11-10.md` in the repository root, alongside this prompt. **Read the complete menu before coding.** It defines strategies **M01–M09 and R01–R09**, the historical evidence, data caveats and research intent. Preserve its strategy identities; do not swap in generic indicators or silently omit the low-priority strategies. Where the menu states alternatives without fixing a unique numerical parameter, select one defensible **default before viewing trade outcomes**, record the chosen value and rationale in the experiment registry, and do not optimize it after examining results. If a source or method cannot be implemented faithfully, report an explicit `UNIMPLEMENTABLE` or `ABSTAIN` status with evidence instead of substituting another strategy.

## 0. Non-negotiable goal and failure lessons

The frozen V5 four-year strategy used a **five-session signed-return directional rule** at up to seven origins daily, with the original **S2-C LSTM forecasting absolute (unsigned) 240-scheduled-trading-minute endpoint movement solely for position sizing**. Its matched S2-C account fell from $100,000 to about $1,927. Reported matched S2-C simulated costs: approximately **$64,507 commissions, $37,695 spread+impact, and $491 short borrow**; its accounting cost-addback was only approximately $4,621. This does **not** imply a profitable frictionless counterfactual. Frequent small orders, minimum commissions, weak/untested four-hour directional alpha, and capital depletion were central failures.

**The new phase has two separate questions:**

1. Can any of the **18 directional hypotheses** deliver a gross, actually executable-horizon signal with enough economic scale to survive its appropriate costs when **frequency is controlled**?
2. Later, for a promising fixed directional rule, does **frozen original S2-C magnitude-based sizing** help relative to equal, rolling-risk and EWMA-risk sizing? **Do not run an 18 × 4 sizing-arm campaign in this task.** Screen all 18 with a common simple funding/sizing rule; retain an optional no-execution sizing adapter for the next pass.

**Speed, reuse, and compact evidence are primary design requirements.** There must be no inadvertent repeat of V5's multi-hour, multi-GB audit runs. Causal execution, corporate-action accuracy, cash conservation, realistic modeled costs and transparent exceptions still matter. Faster means *less work and fewer large artifacts*, not invented fills or hindsight.

### Scope and exclusion

- The **same fixed 20 names**, in preserved order: `VZ,COP,BAC,BA,AAPL,PEP,MRK,SBUX,CVX,MS,AMD,KO,JNJ,AMZN,XOM,WFC,AVGO,TSLA,MA,CSCO`.
- Period **2021-01-01 through 2024-12-31** (four F21–F24 years), with permitted *pre-2021* warmup. Do not read 2025+ equity market prices. For unresolved 2024 payables, apply the existing approved conditional claim treatment and do not invent post-2024 prices.
- This is **reused exploratory OOS** with fixed survivors, retrospective cleaning/actions and approximate unmeasured market-data latency. **No untouched confirmatory performance, true broker execution or historical locate claim.** Record these limitations in every report.
- Preserve all original F21–F24 checkpoints, O1/FT16/CLOCK/C3 fitted recipes, source partitions, action and risk-reference artifacts, prior Phase2/Phase3 audits, Stage012, Stage35 V1–V5 and their outputs. Hash-check before/after; **never modify, delete, move, clean, reformat or overwrite any of them**. Work in a new, additive fast-research namespace with unique immutable run IDs. Do not commit/push or install new dependencies unless demonstrably essential; prefer existing `.venv` packages.
- **No new neural fit/forward campaign is necessary for the initial direction-only screen**; do not waste time invoking torch on every origin. If needed later, use only the existing **131,111 frozen original S2-C forecasts** and prefix-only b/floor/controls; never substitute the Phase2 replica or use training auxiliary signed heads for alpha.
- No options, live/paper orders, web downloads by default, post-hoc winner parameter search, expensive 24-scenario per-algorithm grids, Stage 6 inference, or 15-GB journals.

## 1. First do a bounded, read-only reuse inventory — **before coding**

Examine the actual local repository rather than guessing module names. At minimum locate and inspect:

- Original prepared market-source, cleaned raw one-minute OHLCV, original adjusted signal-price conventions, exchange calendar, 2021–24 source hashes, and V5 verified/conditional actions/OGN records.
- Prior completed Stage35 V5 **causal next-valid-minute execution**, order scheduling, event/date frontier, raw-price basis, cash/collateral/borrow, position/corporate-action treatment, physical netting and order-fee minimum logic.
- Prior Stage35 V2 cached original hourly/minute inputs and full 2021–24 input-only signal/control outputs; already-derived daily data, volume caches or feature tables if available.
- Prior original S2-C cached forecast and matured rolling/EWMA values (only to preserve future sizing interface, not required in every direction-only evaluation).
- Source manifests, V5 scenario result readers, type/tests/finance reconciliations, and existing code/data license constraints.

Write a concise `REUSE_AND_RUNTIME_PLAN.md` table: needed operation → existing component or cache → safe reusable part → *why* it is causally valid → where/when it is calculated → memory/storage expectation. Distinguish **pure reusable utilities** from heavyweight V5 journaling and repeated full-run orchestration. If safe to import the exact tested V5 execution/accounting kernel without its gigantic logging mode, reuse it. If the V5 API forces checkpoint-per-session, 8-account allocation, or event dumps, implement a **small additive adapter** using the **same economic contract** and demonstrate parity on tiny fixtures. Do **not** fork or weaken core execution logic just to go faster.

For each of M01–M09 and R01–R09, also record a **computation-reuse map**. Examples: M01/M02/M06/M08 all reuse received 30/60-minute returns; M03/M04 reuse prior close/open gap; M05/R03/R07 reuse lookback range-high/low; R01/R02/R04/R06/R09 reuse completed-session return/daily reference tables; R05 shares a small past-only pair-fit cache; M07 uses historical same-clock windows; M09/R08 reuse causal session overnight/intraday components. **Calculate identical features once**, then consume them in multiple algorithms. Hash and version shared feature caches. No per-strategy reconstruction of recursive indicators from 2010 or re-download of minute panels.

Check disk budget/free space and identify stale huge artifacts without deleting any of them. Never start a repeated bulk vendor HTTP lookup merely because a cached source has a missing minute; reuse the V5 next-valid-price rule.

## 2. Architectural contract for the lightweight engine

Create an additive namespace, suggested (adjust if the repo requires a different layout):

```text
src/lstm_data/trading/track2/rapid_v1/
  sources.py           # read-only cached causal market/action adapters
  shared_features.py   # incremental cached daily/minute features
  strategies.py        # registry, 18 pure directional implementations
  scheduler.py         # original seven slots, weekly scan, eligibility and budgets
  costs.py             # MICRO_PRO and RETAIL_V5 models
  execution.py         # compact V5-consistent next-valid-minute settlement adapter
  portfolio.py         # light continuous funded book and conservation checks
  diagnostics.py       # streaming aggregations, failure attribution
  runner.py            # one input pass -> independent tiny strategy accounts
  cli.py               # small smoke, screen, verify, report, list
trading/track2/rapid_v1/
  EXPERIMENT_REGISTRY.json
  REUSE_AND_RUNTIME_PLAN.md
  POLICY_AND_ASSUMPTIONS.md
  test_receipts/       # small test receipts, no redundant raw streams
  runs/<unique_run_id>/
    ...compact products...
tests/track2_rapid_v1/
```

These are suggested organization names, not a demand to rewrite existing useful components. A simpler design is better if it is demonstrably faster, deterministic and testable.

### 2.1 Interfaces

- `FeatureFrame` / `FeatureView`: ticker, original nominal origin, **actual decision timestamp**, strictly matured/received input dependencies, numeric feature values, availability masks and input-hash/provenance pointer. Never expose future endpoint prices, trade P&L or future daily closes to signal-generation functions.
- `DirectionIntent`: `strategy_id`, `mode`, session/week, ticker(s), `sign ∈ {-1,0,1}`, causal **strength**, original 240-minute endpoint, decision receipt, reason for abstention, and raw-price readiness. Two-leg pair intents must be atomic where practical; short legs remain hypothetical with 2%-borrow model.
- `FastExecution`: pre-submitted order, earliest eligible minute, **next valid observed raw bar** within original lifetime for entries, actual receipt/post time, partial/expired/missing statuses. Do not turn a missing open into an earlier fill. Retain conservative known-versus-unknown order status and financial effects; no profit-based filtering.
- `FastAccount`: fixed starting cash, immutable holding cohort identity and endpoint, physical net inventory, restricted short proceeds, modeled fees/borrow, corporate-action claims and **one account for each strategy+mode/config**. Keep no weekly/annual capital reset, and no dynamic resizing of existing held lots. All accounting amounts reconcile; no fictitious cash from internal crosses or cost double charging.
- `StatsAggregator`: incremental, bounded-memory totals and by-session/by-year/by-ticker/by-origin summaries. Keep a **small trade ledger**, not a full journal or duplicate source-price arrays. Streaming online calculations should not require a pandas DataFrame copy per trade.

Choose only the fields needed for a trade-level audit sample and diagnostics. Implement stable IDs, deterministic ties/order prioritization, restart-by-run-directory where worthwhile, and fail-closed append-only results with atomic final publication. Do not accumulate gigabytes of event logs or routine checkpoints. A short bounded exception sample suffices when all accounts reconcile.

### 2.2 Common chronology and invariants

1. Source observations are completed/received before being used; 09:30 opening reference cannot be known at 09:30.
2. Strategy-specific signals and any past-only thresholds are computed at the **decision-time frontier**; no 2021–24 future outcomes enter the threshold calibration or candidate ranking.
3. Order acceptance/exposure and participation use only prior observed/cached data. **1% cap based on previously received minute volume**; no looking at fill-minute future volume to justify trade size.
4. Earliest external fill is strictly after decision/order submission; actual modeled execution is next valid observed minute (after observation it can be booked retroactively to that minute's execution timestamp, not used for the decision). **Original +10 wall-minute entry lifetime**, realistic later exit if scheduled bar absent, all exceptional XNYS sessions/overnights; 2-minute assumed receipt baseline and zero compute duration scenario as in V5.
5. **Exit near the original fixed 240 scheduled XNYS trading-minute endpoint**, with same V5 endpoint decision/receipt semantics and true realized entry-to-exit P&L. A hold crossing close, weekend or early close remains possible. Do not relabel 240 scheduled minutes as four wall-clock hours or equate original model magnitude with delayed-entry absolute return.
6. Gross/virtual exposures and physical net positions are separate. Borrow expense accrues **once on physical net short**, ACT/365 across calendar days; short proceeds are restricted. Track commissions once per physical external order, not once per virtual cohort. Account for raw-share splits and dividends (including MRK/OGN conditional policy) with no price-unit mismatch; all unknown source cases explicit.
7. Account wealth: cash (restricted proceeds already included) + signed marked physical inventory + properly valued action receivables/payables, with no second cost subtraction. Entry/exit/corporate-action cash and final NAV must reconcile within documented numerical tolerances. If essential economic value cannot be obtained or reasonably governed by the already reviewed V5 conditional action policy, report HOLD for that affected account/experiment, *not* a fabricated return.
8. Compute signal-quality outcomes only **after maturity**, never as a filter on which signals exist. Report full potential/abstained and actually traded denominators. Missing outcome observations are censored transparently and must not silently improve the winning sample.

## 3. Two distinct economic modes — do not merge their performance

Implement **one first-pass default configuration per mode**; do not start a cost/entry-cap Cartesian grid. The modes share underlying causal data and execution mechanics but own independent accounts, eligible decision schedules, budget policies and costs.

| Item | `MICRO_PRO` (M01–M09) | `RETAIL_CONSERVATIVE` (R01–R09) |
|---|---|---|
| Primary objective | Frequent-but-controlled hourly/intraday opportunities | Sparse/high-conviction weekly entries |
| Decision opportunities | Each strategy's menu-defined subset of seven calendar-valid nominal slots | **One ISO-week decision scan** using the first eligible full regular XNYS session (default 10:30 ET; R08 predeclared late-day 14:30 ET) |
| Default new physical entry order cap | **6 per session across the strategy account** | **5 per ISO week across the strategy account** |
| Cap variants (future, not now) | 2 and 12 per session | 2 and 10 per ISO week |
| Commission | **$0.002 per external share, zero ticket minimum**; hypothetical negotiated institutional assumption | **$0.005 per external share, $1 cumulative minimum per physical external order**, original conservative V5 |
| Spread proxy | Liquidity-dependent, **extra adverse trade-print slippage**; not claimed measured NBBO | Existing conservative **5 bp half-spread proxy** per external side |
| Impact proxy | Liquidity/size-dependent; predeclared capped functional form below | Existing conservative **5 bp incremental impact** per external side |
| Borrow / carry | Baseline conditional short **2%/year ACT/365**, 0 funding in unlevered base | Same |
| Minimum notional | No arbitrary $1-ticket minimum (still skip meaningless/funding-infeasible orders) | Candidate **$2,000 external-order notional floor**; if financially infeasible, skip with `RETAIL_MIN_NOTIONAL` |
| Capital/limits | V5: <=100% virtual gross, <=100% absolute physical net, <=10% per-name, <=20% per new vintage, reserve fees; no recycled short proceeds | Same; account starts at $100k |
| Frequency/churn | Do not initiate duplicate same-ticker/same-sign cohorts while one is active, unless a separately frozen exception is in the menu | Same; every pair consumes two *actual physical entry-order* slots unless valid netting changes the external count |
| Exits and risk | Same 240-minute endpoint and actual valid-bar exit, no dynamic resizing | Same |

**Critical caveat:** a $2,000 retail order is **not automatically feasible** under whole-share rounding, the 10%-per-name cap, declining NAV or the entry budget. Do not borrow or manufacture capital to satisfy it. The rule should reduce low-value tickets; count and report how many signals it rejects. If it makes an entire strategy non-investable, report that fact rather than silently lower the threshold. For pair trades, require both legs' funding/availability and two physical slots together or abstain, not a one-sided accidental hedge.

### 3.1 Candidate micro-professional price-friction model (no paid quotes)

We lack synchronized quote NBBO. Use **actual raw bar-open print** for the external reference and apply a separately labeled **incremental adverse-print slippage proxy**, not an asserted observed half-spread. Fix the following economical, causally computed *research* model before results:

- `v20_i,d`: standard deviation of the last 20 **completed** daily log returns, with a minimum warmup threshold; `v60_i,d`: last 60 completed sessions. `ADV20_i,d`: average **raw-share-consistent** volume over last 20 completed sessions. Split-unit transitions must be normalized/matured safely. If any required reference cannot be causally computed, abstain or use a documented conservative fixed fallback, never future replacement.
- Additional printed-price **spread/slippage proxy** per external side, in decimal fraction: `h_i,d = clip(0.0003 * clip(v20/v60,0.5,2.0),0.0001,0.0006)` (about 1–6 bp, centered on 3 bp). This is a *heuristic spread/friction proxy*, not a calibrated quote estimator.
- Size-sensitive *additional impact* per side: `j_i,t = clip(0.0001 * clip(v20/v60,0.5,2.0) * sqrt((abs(q)/max(ADV20,1))/0.0001), 0.000025, 0.0005)` (about 0.25–5 bp). `q` is the **physical net external signed share quantity**, never gross virtual cohort shares. Record daily shares, participation and inferred cost-rate components. This coefficient is deliberately a starting assumption, *not* an empirical impact calibration.
- Commission: `0.002 * abs(q)` USD per physical external fill, with **no per-order minimum**. If regulatory/clearing pass-through rates are unavailable, disclose them as *not modeled*, not observed zero. Do **not** charge friction on internal-only matched opposing cohort transfers.
- Later quote-midpoint and fixed-h/impact model comparisons can be implemented in the cost API but **not run now**; avoid potentially double-counting a full half-spread on the trade print without explicitly describing the reference convention.

Record both modes' economic cost components separately. The old V5 model is **the retail default** and a preserved historical benchmark; do not retroactively rerun or replace V5 results.

### 3.2 Signal prioritization and entry limits

- Always **observe and count** all eligible time slots; do not automatically open a position at every origin.
- Predefine ranking by each strategy's **absolute standardized signal strength** when meaningful; among same-time candidates choose strongest first, tie-break in frozen ticker order. An online strategy cannot rank against future-origin candidates later in the day/week.
- For `MICRO_PRO`, process origins chronologically, limit **new physical entry orders** to 6/session, and suppress duplicate same-ticker/same-sign active exposure; exits always permitted and charged.
- For `RETAIL_CONSERVATIVE`, one predeclared weekly scan, rank only signals known at that scan, cap 5 new **physical external entry orders** per ISO week, no unused carryover; pair legs are an atomic choice and consume 2 entries when externally required. Repeated subsequent origins in the same week do not generate entry invitations. If there is no valid full-session 10:30 or R08's late-day origin, abstain for that week under a documented rule rather than opportunistically choosing a winning later date.
- For a cross-sectional top/bottom choice, compute ranks from currently available eligible names, keep an explicit minimum peer count, and do not form the universe from future-complete realized returns.
- Every strategy must expose counts of: candidate signals, filtered thresholds, missing inputs, duplication suppression, cap suppression, min notional, unshortable conditional failures, unfillable price, risk/capital, and actual filled external orders.

## 4. Implement **all 18** strategies exactly by reference IDs

Use the root strategy-menu document as the **authoritative detailed math and intended timing**; the table below is a cross-check for implementation coverage. For unspecified noise buffers, z thresholds, minimum support, fit windows, opening range length or pair stability cutoff, select and lock a small defensible default *before looking at strategy returns*, and document units, exact source frontier, initialization, and historical prefix-maturity tests. Do not infer today-close, future same-clock return, post-decision peer return, or full-session volume before it arrives.

| ID | Required mechanism | Critical shared feature / causal condition |
|---|---|---|
| M01 | 30–60-min intraday continuation; initial 60-min direction | Currently received 60-min stock return, prior same-slot volatility scale |
| M02 | 30–60-min intraday reversal; initial negative 60-min sign | **Share the exact M01 return/features**, reverse sign after extreme move |
| M03 | Opening-gap fade | Prior completed close and observed/received opening price; no same-open fill |
| M04 | Gap continuation with observed first-hour confirmation/volume | **Reuse M03 gap**, completed first-hour price/volume, no future daily volume |
| M05 | Opening-range breakout | Completed 09:30–10:00 high/low, subsequently received break, noise buffer |
| M06 | Cross-sectional intraday residual continuation | **Reuse M01** returns, current eligible leave-one-out basket, top/bottom two, min peers |
| M07 | Same-time-of-day return persistence | Previous 20 completed sessions' same-clock half-hour returns, no same-day lookahead |
| M08 | High-volume short-term reversal | **Reuse M02** return, received recent volume against prior same-slot 20-session baseline |
| M09 | Late-day intraday/overnight cross-period reversal | Received current-session return, 14:30/15:30 origins, overnight carry attribution |
| R01 | 6-minus-1-month cross-sectional strength | Previous completed daily `C[d-22]/C[d-126]`, +/- top/bottom filtered ranks |
| R02 | Daily 20/60 MA trend | Previous 20/60 **completed** session prices; strength scale |
| R03 | Previous-20-session price-channel breakout | Prior 20-session high/low and presently received crossing |
| R04 | Weekly cross-sectional 5-day reversal | Previous `C[d-1]/C[d-6]`; long losers, short winners, once-weekly ranking |
| R05 | Precommitted related-stock pair-spread reversion | `KO/PEP`, `XOM/CVX`, `BAC/WFC` allowed exemplar pairs; fit beta/mean/sd **past-only**; atomic two-leg order |
| R06 | Factor-neutral residual reversal | Past 60 completed sessions' stock versus eligible equal-weight/leave-one-out factor and residuals |
| R07 | Volatility-contraction breakout | Past low RV10 vs previous 60-session quantile; **reuse R03** channel breakout |
| R08 | Prior 10-session overnight/intraday divergence | Past completed-session overnight and intraday sums, late-day weekly scan |
| R09 | High-volume relative strength | Past-only 60-session daily volume reference and last five completed sessions' volume ranking |

No strategy may be omitted because it seems implausible, weakly cited, or unprofitable in a preliminary scan. If a signal has zero trades under a frozen rule, record a valid zero-trade result and all abstention causes. The 18 ID set **must exactly match** the registry and the final output rows; throw a test failure if any ID is absent/duplicated.

### Horizon discipline

The initial funded screen uses **the same original nominal 240-scheduled-trading-minute endpoint for all strategies** so the study tests a common executable horizon. This is not an assertion that 6–1-month momentum or pairs trading was designed for a four-hour exit. A natural **multi-day retail holding** would require a separate preregistered follow-on and a different risk-matching interpretation for S2-C; do not quietly change retail exit horizon as a way of improving results.

## 5. Execution sequence: implement, test, then **screen every strategy**

**Do not stop at an outline**; proceed to code, automated tests, source-backed pilot, shared-data preparation and the complete default 18-strategy screen. Follow the boundaries below without waiting for optional approvals. If a genuinely material data/source/ledger blocker remains, finish all independent tasks and report it accurately rather than violating the existing research policy.

### Gate A — Freeze compact experiment registry

Write one versioned `EXPERIMENT_REGISTRY.json` **before** viewing any new strategy returns. For each ID bind:

- strategy source file/code hash, supporting menu reference, mode, eligible origin/weekly scan, directional formula, signal strength score, exact threshold/default assumptions, lookback/warmup, candidate minimum peer count;
- causal feature/readiness requirements, source basis and raw fill-price convention, 240-minute original endpoint, choice of baseline horizon;
- new-entry cap, no-duplicate logic, minimum notional for retail, allocation and max-cap policy, short borrow assumption, cost version;
- root data/corporate-action manifests and prior approved V5 rule hash, source cache version, output-size budget;
- preset abstention categories; failure conditions; strategies that may require two-leg transactional enforcement.

Keep the **legacy V5 five-session sign**, labeled `LEGACY_V5_SIGN`, and `NO_TRADE` as tiny contextual controls, **not** entries among the 18. Never use the V5 results to tune new thresholds. Reasonable defaults can be declared here once; record all modifications in an append-only changelog and forbid profit-based parameter changes during this run.

### Gate B — Reuse caches and build shared features exactly once

- Project only the needed historical columns/time windows from already approved local OHLCV, daily-source/action and signal caches. Prefer memory mapping, vectorized/grouped rolling and incremental forward iteration; avoid Python per-signal scans of the full history.
- Build only once per ticker/session/clock: completed daily returns, 5/10/20/60/126-session prices, past-minute 30/60 returns, opening gap, 30-minute opening range, last-day highs/lows, prior same-clock statistics, 20/60-day volatility and ADV, volume shocks, overnight/intraday splits, pair-beta/regression rolling fits, leave-one-out cross-sectional basket returns.
- Fit any nontrivial beta, normalization, quantile or spread threshold using only completed past data at that decision. Prefer running updates to recomputing rolling regression from scratch for each origin.
- Share common features across all 18. Enforce source timestamps and missingness masks; no weekend slot compression, same-bar lookahead or evaluation/F09 future-label gating.
- One source/data read pass should feed all strategy evaluations and ledgers. Cache features in **one central content-addressed compact cache**, not 18 copies. Track its bytes and building time; make it reusable for future candidate algorithms.

### Gate C — Test a short, **source-backed** pilot, plus synthetic adversarial cases

Tests must include at least:

1. Same input prices and timestamps produce identical shared features for strategies M01/M02/M06 and M03/M04, and breakout prices are received before acting;
2. Opening clock 09:30, half-day, DST, early close, weekend, session rollover, 2024 year-end cutoffs, no future daily close/next-slot values;
3. Delayed/missing minute source, V5 next-valid-bar within 10-minute entry expiry; expired entries and delayed exits are accounted without hindsight;
4. AAPL/TSLA/AVGO split changes, cash dividend long versus short, MRK/OGN special conditional settlement; no adjusted price in economic share ledger and no price from a later date before it was available;
5. Gross/net share and cash identities, once-per-external-order fees (especially **$1 retail**), commissions carried across partials, restricted short proceeds, physical-net ACT/365 carry, all exits, cancellation/missing-exit accounting;
6. A 2-leg pair's atomic eligibility and two-slot retail budget, multiple eligible candidates tie break and online 5/week cap, 6/day cap, no repeated same-side active-stock positions;
7. Direction-only outcomes independent of S2-C forecasts; mutate future returns/fills/labels and prove identical earlier intents; no F09 or later source availability gate;
8. Genuine **benchmark equivalence**, on a bounded agreed historical fixture, to the tested V5 **next-valid execution/accounting** for **identical intent and cost rules** (e.g. existing legacy V5 sign with original conservative retail costs). Explain any difference due to deliberately changed frequency policy; never claim parity where population differs;
9. Restart/partial-state invariants and lossless compact aggregation; no duplicate orders on resumed slices;
10. No negative/NaN/infinite NAV silently accepted, fee double charging, corporate action claim counted twice, or post-2024 source market read.

Run actual bounded market-source pilots (e.g. at least one normal week, the June 2021 MRK/OGN boundary, 2022 split window, 2024 dividend window, and 2024 Thanksgiving early-close) with each strategy's real inputs where supported. Pilot can abstain legitimately. Verify independent accounts and retained source/receipt identifiers. **Only after pilot gates pass run the full 18-strategy screen**. Fix genuine engineering errors without changing financial policy to make results prettier.

### Gate D — Lightweight directional diagnostics **for all 18**

For every actual decision opportunity, stream signal counts without requiring actual funding. Score *realized executable entry-to-exit outcomes after maturity* separately from nominal anchor returns. For all 18 produce:

- coverage, candidate/abstention breakdown, signed long/short counts, trades actually selected after budget, distinct names/clock slots/years;
- sign hit rate, mean/median signed **entry-to-exit log returns**, separately by year, long/short, intraday and overnight; clustered day-level averages (descriptive, not formal Stage6 statistical validation);
- hypothetical **equal notional** gross positive dollar sum, gross negative dollar sum, average winner, average loser, concentration in largest 1% trades, and roundtrip break-even cost magnitude;
- one explicitly labeled simple null diagnostic: opposite sign or one-session-lagged score on the **same causal opportunity base**. No iterative permutations or huge multiple-testing engine;
- signal availability and time-of-day dependence; months/years with sparse support and source missingness.

Do not use nominal-endpoint anchor P_t as if it were the post-issuance purchase price. If an executable outcome is unavailable, log the denominator and reason. Never use future outcome availability to generate trades. This table is exploratory signal quality, **not** a funded portfolio P&L estimate.

### Gate E — **Funded compact screen of all 18** under mode-specific costs

**Do run the 18 baseline funded portfolios**, one default config each (**9 MICRO_PRO at 6/day, 9 RETAIL_CONSERVATIVE at 5/week**), from $100,000 per separate strategy account, carrying account state through 2021–2024 without annual resets. Use one lightweight, causal, calendar-ordered engine with 18 isolated account states, shared observations and shared feature rows. Where a strategy is unimplementable with allowed data, emit `UNIMPLEMENTABLE` with a precise reason and a no-trade abstention run; do not invent a performance number. Do not automatically skip any strategy simply because Gate D looked weak; we need the full first-pass comparison, including failures.

**Initial sizing: `EQUAL` / simple fixed-notional and consistent risk caps**, not S2-C. Within each mode, keep allocations, execution, costs and budget treatment common so directional mechanisms are actually comparable. For pairs, two-leg size and historical beta-neutral hedge must be implemented without violating cap or creating a one-leg unhedged residual. No self-financed leverage or silent cash recycling.

For every filled lot and physical order preserve enough compact data to compute:

- realized and marked **gross signed-price trading P&L**, total **gross winning dollar sum** and **gross losing dollar sum** (clearly state whether winner/loser refers to pre-cost or post-cost trade), average winner/loser and hit rates;
- external commissions, modeled incremental trade-print spread/friction, modeled impact, physical-net borrow, funding, dividends/special distributions, final residual marked value;
- **Net P&L reconciliation to final NAV**, with costs already embedded in actual fills **not subtracted a second time**; all cost-addbacks marked as arithmetic accounting, not independent frictionless reruns;
- number of directional signals, candidates, entrants, cohorts, **external physical orders** (not the same), actual fills, paired legs, cancellations/expiries, turnover, median external order notional, minimum-fee incidence, realized holding time, time in market, gross/net exposure, idle cash, annual NAV/Sharpe/drawdown;
- by-year, ticker, clock origin, sign, overnight/regular-hours, profit/loss reason and cost dominance. Explain specific pathologies (fees per $ traded, many tiny tickets, weak gross signal, bad short leg, untradable gap, no-trade budget, missingness etc.).

Maintain **accounting parity** with the underlying V5 economic principles and the predeclared conditional data policy. For speed, output only *daily account summaries* and **condensed completed-trade rows**, not every journal event, every minute quote, state transitions or redundant day-level full checkpoints. Retain provenance pointers/hashes and a bounded sample of exceptional events so later Tier-2 audits can reproduce cases. A fast path must never silently hide unresolved exposure or unpaid claims; fail the affected result explicitly.

### Gate F — Consolidate, diagnose and report; no automatic search of winners

Produce a single table sorted **by predeclared ID**, not only by best Sharpe, with all M01–M09 and R01–R09; separate micro and retail modes. Include status, 2021–24 total net P&L/CAGR/Sharpe/drawdown, gross cost-addback and its limitation, gross signed-trade P&L, winner/loser sums, cost split, number of fills/orders/cohorts, and yearly return/coverage. Show legacy V5 comparison with clear different cost/frequency caveat (not an apples-to-apples incremental improvement claim).

Generate `DIAGNOSTICS_AND_FAILURE_MODES.md` organized by **why trades lose money**: raw sign wrong; gross edge smaller than modeled spread/impact; excessive ordering; $1 minimum; share rounding/min-notional; concentrated single name/event; reversal across overnight; missing source; unfunded/abstained; inherited survivor bias. Include at least a few concrete source-backed examples per *reason*, with before-decision source frontier and after-decision outcome strictly separate. Do **not** retrospectively improve rules in the same sealed run.

After the first screen, give an **evidence-based candidate shortlist**, but label it *exploratory, selected among 18 on reused OOS years*. The follow-on plan may compare S2-C against EQUAL/ROLLING/EWMA *only after freezing selected directional strategies* and requires separate, controlled evaluation. Stage6 independent review and untouched/prospective confirmation remain separate.

## 6. Output size, runtime and resource discipline — **enforce in code**

The prior V5 `final_backtest_v5` occupied ~15 GB. **Do not repeat that.** Implement concrete budgets and print output footprints.

**Required persistent outputs per strategy (target <= 5–10 MB; soft cap 10 MB, hard cap 25 MB compressed):**

```text
runs/<run_id>/<strategy_id>/
  config.json              # strategy/mode + hash and chosen defaults
  summary.json             # concise metrics, status, all reasons
  daily_nav.parquet        # at most one row per account per session
  trades.parquet           # compact filled/closed lot or physical-trade summaries only
  cost_breakdown.csv       # commissions/slippage/impact/borrow/actions
  signal_counts.csv        # by session/year/slot, no huge row-per-hour debug dump
  diagnostics.json         # counts/attribution/percentiles, capped examples
```

**Shared once per run:** `manifest.json`, `EXPERIMENT_REGISTRY.json` reference, `SHARED_FEATURE_CACHE_MANIFEST.json`, `REUSE_AND_RUNTIME_PLAN.md`, `ASSUMPTIONS.md`, `SUMMARY_18_STRATEGIES.csv`, `SIGNAL_QUALITY_18.csv`, `DIAGNOSTICS_AND_FAILURE_MODES.md`, `VALIDATION_RECEIPTS.json`, `EXECUTION_AND_RESOURCE_REPORT.json`. Keep a single central reuse feature cache and source references; **no copied OHLCV or LSTM checkpoint in individual algorithm folders**. No 24-sensitivity grid or dozens of daily checkpoint archives.

- **Target full 18-strategy output (excluding already-existing frozen source/input files): < 200 MB.** Hard safety threshold **500 MB total new persistent run output**; if at risk, stop verbose writes, apply streaming aggregation/column reduction, and still publish accurate summaries/byte counts. Never discard unresolved exposure, suppress failed cases or delete prior evidence to fit a limit. A shared cache may be transient or bounded separately, recorded explicitly, not counted as a license for multi-GB outputs.
- Compress columnar daily/trade files; exclude raw-price/event payload duplication, dense feature debug, raw HTTP/cache replications and per-minute account rows. Keep an optional **sample** of at most 100 order/execution anomalies *per strategy*, never millions of logs.
- **Benchmark one bounded representative day/week and one representative month** with per-phase timings and peak memory if obtainable, extrapolate to four years **before** full launch. If projected to take hours or use multi-GB incremental storage, redesign shared caching/streaming and rerun the benchmark before launching. Prefer one chronological source scan and 18 small accounts over 18 independent source traversals; cap worker concurrency for the user's Mac rather than opening dozens of Python processes.
- Reuse all completed source/forecast/core logic. No gratuitous modeling, no 2010-from-genesis rebuild per strategy, no new downloads by default. If source-partition access is missing, report it; do not launch an indefinite network search.
- Allow a stopped/restarted run to **resume only missing strategy outputs or postvalidated chunks** under the same sealed code/config/source hashes; never blindly rerun completed cases or overwrite them.
- If a hard gate fails, finish safe independent tests/source-only quality summaries and publish an explicit `PARTIAL` report, rather than blocking all 18 on one nonmaterial sample. Conversely, do not promote a financially unresolved account to `PASS`.

## 7. Mandatory tests / acceptance matrix

Write targeted tests and run relevant existing Stage35 V5 regressions, emphasizing **scope-relevant** validation. No wholesale Phase2/Phase3 rerun or giant full test sweep unless necessary.

| ID | Minimum acceptance requirement |
|---|---|
| A1 | All **18 exact IDs** implemented/registered and included in reports; all root-menu signals checked against reference, no silent replacement |
| A2 | Shared features computed once/cached with identical reuse across linked signals; source hashes, warmup and cutoff respected |
| A3 | Signal output invariant when future endpoint prices/scoreability/fill prices are mutated beyond decision frontier; no future rank/label gate |
| A4 | Seven XNYS origin slots/overnights/open/early-close/DST and +2 receipt / +10 entry expiry / next-valid-minute chronological conventions |
| A5 | Entry budgets **micro 6/day** and **retail 5/ISO-week** enforced online; weekly scans cannot use future candidates; pair slots/fills atomic |
| A6 | Micro cost total equals its documented physical-share/proxy formula; retail $1 minimum charged per **physical external order**, not cohort |
| A7 | Gross/net/nav/short-restricted proceeds/borrow/commission/action reconciliations; arbitrary partials and opposite cohorts don't manufacture NAV |
| A8 | Small source-backed comparison against V5 frozen known cases with identical conditions where possible; retained differences qualified |
| A9 | Realized outcome missingness not used for eligibility; no selected-winner-only report; negative control stays on same opportunities |
| A10 | No frozen original/V5 artifact/source bytes or mtimes changed; no 2025+ market price reads, no LSTM retraining or Phase2 substitution |
| A11 | All 18 funded experiments have terminal status `COMPLETE`, `NO_TRADES`, `UNIMPLEMENTABLE` or explicit `HOLD` with evidence; not falsified metrics |
| A12 | New compressed output per strategy <=25 MB, total new persistent output <=500 MB, no multi-GB journals and no redundant source copies |
| A13 | Determinism test, partial restart safety, hashes and full first-pass run summary accurately reconcile counts and status |

**Acceptance of test suite != profitability**. Do not invent successes. If everything is negative, report all 18 negative results and whether the predominant mechanism was weak gross directional edge, micro cost, retail fragmentation, or capital/frequency constraints.

## 8. Deliverables and final Codex response

Do all actionable steps **in this session** rather than producing a plan only. Produce code, tests, a tiny pilot, the one full default screening batch for all 18, compact machine-readable outputs, and a brief but truthful handoff document. Stage6 does not run.

In final chat report:

1. **Completion verdict** and exact `M01–M09`, `R01–R09` statuses and counts;
2. Actual source history and experiment versions/config/assumption hashes, preserved original artifacts and reuse components;
3. Measured *actual* wall/runtime and output sizes (total and max strategy), not estimates;
4. Micro vs retail performance **separately**, by ID including negative/zero-trade cases; high-level best/worst comparisons are exploratory and not a model-selection claim;
5. A concise cost-versus-gross-profit diagnostic, including **gross winning dollars vs gross losing dollars** and per-physical-order fees; do not confuse cohort count with external orders;
6. Outstanding blockers/unsupported source or action events, test receipts and any raw-vs-adjusted accounting caveat;
7. Next research actions, no automatic optimization nor automatic S2-C sizing grid.

**Priority order under constraints:** audit/reuse and freeze → implement **all 18** shared directional signals → causal source-backed pilots + tests → **direction-only quality for all 18** → compact funded portfolio screen **for all 18** → diagnostics/one honest report. Do not start 24 scenarios for each algorithm or heavy V5 logging as a substitute for this task.

**Research integrity rule:** V5's 97–98% loss and commissions are motivations to improve design, *not* permission to manipulate the historical 2021–2024 sample until some strategy looks profitable. Preserve source, causal clocks, realistic economic costs, all failures and sample-selection limitations. The primary goal here is a fast and informative **first screen**, not a CV profit claim.
