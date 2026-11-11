# HF20 Track 2 — Directional Strategy Research Menu for Micro and Retail Trading

**Date:** 2026-11-10  
**Status:** Research proposals only; no implementation, data access, backtest, parameter fitting or model modification authorized by this document.  
**Scope:** 18 strategies (9 micro, 9 retail), within the original fixed 20-equity HF20 universe.  
**Core objective:** Find a causal, cost-aware *directional* trading rule worth testing, then determine whether the frozen **original S2-C magnitude LSTM** improves its position sizing against equal-weight and classical-risk alternatives.

## Executive conclusion

The first V5 strategy was *not* a test of LSTM directional forecasting. It used the sign of a five-session stock return for direction at seven origins each day and the S2-C four-trading-hour endpoint **absolute-return** forecast for sizing. It lost about 97–98% of starting capital under its actual, repeatedly charged simulated costs. In the matched S2-C arm, total modeled commissions were **$64,507**, spread plus impact **$37,695**, and net portfolio loss about **$98,073** on initial $100,000. The accounting cost-addback was mildly positive, but is **not** the return of an independently rerun zero-cost strategy. The model was not shown to deliver economically useful incremental sizing in V5.

Three corrective design decisions follow:

1. **Test the sign independently of S2-C.** Directional signals must use only completed, causally available OHLCV and predetermined rules; S2-C never supplies a sign and its training-only signed auxiliary heads remain unavailable to trading.
2. **Do not evaluate seven origins automatically as seven new trades.** Origin opportunities can be observed without trading. Sparse triggers, capacity constraints, consolidation and no unnecessary duplicate positions are especially important under the $1 retail minimum fee.
3. **Match economic horizon and research claim.** The primary, comparable trade exits around the original **240 scheduled XNYS trading-minute** endpoint, after applicable exit delay. Many published momentum/reversal findings concern *other horizons*, markets or universes. These are inspirations for falsifiable hypotheses, **not evidence of four-hour stock alpha**. Optional longer retail holds must be identified as a separate experiment; S2-C's four-hour absolute-movement output is not a calibrated risk forecast for a multiweek holding period.

**First practical screen (six ideas, without selecting by previously seen V5 profits):** M01 intraday continuation, M02 intraday reversal, M06 cross-sectional intraday residual continuation, R02 daily trend, R04 weekly cross-sectional reversal, and R05 peer-pair residual reversion. Retain the old five-session sign as a labeled negative/legacy comparator, not as an assumed viable strategy.

---

## 1. Fixed inputs, clocks and evidence standard

### 1.1 Actual research universe

In frozen order:

`VZ, COP, BAC, BA, AAPL, PEP, MRK, SBUX, CVX, MS, AMD, KO, JNJ, AMZN, XOM, WFC, AVGO, TSLA, MA, CSCO`.

This is a **retrospectively selected surviving** universe, not an unbiased point-in-time constituent set. Use the already checked **original** HF20 market-source records and action policy, the cached 131,111 original S2-C predictions over F21–F24 (2021–2024), and existing matured classical risk-control data. Missing forecast/input opportunities remain explicitly missing; neither direction ranking nor a backtest may condition on eventual label completeness or trade profitability.

**Free data:** original historical stock minute OHLCV; derived full completed daily OHLCV; raw minute opening marks for execution; the existing verified/conditional splits, dividends and spinoff tape; XNYS calendar. Cross-sectional market proxy can be made solely from currently observed names (prefer leave-one-out for stock-specific relative returns). No expensive feeds, options, news or paid borrow inventory are needed for these **research hypotheses**. Optional SPY/sector ETF data are **not prerequisites** and should not be silently assumed available from our original source.

### 1.2 Notation and causal semantics

- Session index `d`, stock `i`, original nominal origin `t` in the seven calendar-valid slots from 09:30 through 15:30 ET; `tau(i,t)` is the *actual simulated decision time* after inputs have been received. The fixed model endpoint `e(t)` is 240 scheduled trading minutes beyond the nominal origin. If the endpoint crosses a close/weekend, preserve its actual market calendar meaning.
- `C[i,d-k]`: adjusted **signal-only** close of completed session `d-k`, with `d-1` the latest completed session (not today's future close). `O[i,d]`: today's opening minute reference, usable only after that source minute is complete and received. `P[i,tau]`: last correctly received eligible signal-price observation at decision time. Economic fills/accounting use raw-share prices and corporate actions, never the neural adjusted-price units.
- `r[i;a,b] = log(P[i,b]/P[i,a])` when both references actually exist and are causally available. Minute windows use genuine scheduled market minutes; do not compress gaps or fabricate bars.
- `L(tau)`: the information frontier; all rolling means, quantiles, volatilities, regressions, betas, ranks and volume references use only `L(tau)`. Fit any reusable parameter only on an earlier permitted prefix.
- Each strategy outputs **direction** `s(i,t) ∈ {-1,0,+1}`, an optional **signal strength** `u(i,t) >= 0` for *causal* prioritization, and an abstention reason. No forecast of expected signed return is claimed without separate validation.
- The *predictive outcome* to inspect is the **executed-entry-to-executed-exit signed return**, as distinct from the original nominal-origin-to-endpoint target. Label maturation does not control signal eligibility; it controls only when a realized outcome can be scored.
- Cross-sectional ranks are computed from names actually known/eligible at that **decision** and do not use future price availability. For paired decisions, both legs must be independently eligible and the combined risk limit must pass.

The 09:30 model opportunity requires its original completed opening reference; it is not tradable at the contemporaneously unknowable 09:30 open. Historical provider receipt is modeled (2-minute base, 1-/5-minute stresses), not observed. Orders occur after issuance; a missing intended bar follows the approved V5 *next-valid-bar within deadline* process. No post-2024 equity-price read is permitted for a 2021–2024 pilot.

### 1.3 Evidence grades used below

- **D — directly relevant phenomenon:** a cited paper studies substantially related security type, timing or signal mechanism, **but not necessarily this exact signal/horizon**.
- **A — analogical:** robust established research in a different horizon, market or portfolio structure motivates a test; the target application is not demonstrated.
- **H — heuristic/design extension:** deterministic rule is operationally clear, but the citation does not validate that specific implementation. Treat as a weaker research hypothesis.

The papers were checked through their publisher/author/research abstracts. None certifies profit in this 20-stock universe, 2021–2024, or at a four-hour executable horizon.

---

## 2. Two economic configurations — **same directional hypothesis, separate test accounts**

| Dimension | MICRO: frequent research strategy | RETAIL: scarce, higher-conviction trades |
|---|---|---|
| Candidate decisions | All 7 daily S2-C origin slots (not automatic trades) | Screen at most the same 7 slots, prefer a single predeclared weekly decision schedule; no churning to use a budget |
| New-entry caps (pilot) | Candidate **2/6/12 new physical entry orders per day**; all prespecified, no retroactive choice | **2/5/10 new physical entry orders per ISO week**, not “completed trades”; no unused-budget carryover |
| Main commission | **$0.002/share, no minimum**, *hypothetical negotiated institutional research assumption*; track pass-through charges separately | **$0.005/share, cumulative $1 minimum per physical external order**, as in V5 conservative scenario |
| Spread | Causally estimated ticker/time liquidity proxy; compare fixed 1/3/5 bps half-spread if no historical quote calibration exists | Fixed **5 bps half-spread per side** (V5) |
| Impact | Stock/day order-size and volatility-sensitive proxy, fitted/frozen before outcome inspection; compare fixed 1/5/15 bps stress | Fixed **5 bps per side** (V5), with a later conditional size-aware sensitivity |
| Common safeguards | Raw-price next-valid-minute fill convention, original delays/calendar, <=1% of **previously received** minute volume, capital/share constraints, logged missingness | Same, plus no insignificant $1-minimum tickets; initial candidate **$2,000** minimum *external order* notional if feasible (the $1 fee is then at most 5 bps on that side) |
| Shorting | Explicit hypothetical short availability, **2% ACT/365** physical net borrow baseline, 1%/5% stress | Same, no recycling short-sale proceeds into new buying capacity |
| Positions | Fixed independent cohorts (no dynamic resizing); physical netting across opposing cohorts | Same, and no re-entering an identical current-direction stock merely to use remaining weekly slots |
| First execution | Reuse same approved V5 causal execution module; avoid launching multi-GB scenario grids for initial ideas | Same engine, weekly budget enforced online and charged for both legs of pairs where applicable |
| First reporting | Daily NAV, daily market exposure, signal/prediction and transaction counts, gross/net P&L, fees/spread/impact, borrow, turnover, drawdown; compressed aggregate file | Same, plus reason each weekly candidate was rejected/selected |

**Spread/impact caution:** The economic reference is an actual *trade-bar opening print*, not an observed quote midpoint. Applying a full midpoint-based half-spread after that can double-count part of the realized spread. Therefore the micro model should distinguish a *trade-print incremental-slippage* scenario from a *midpoint + half-spread* proxy. In neither case represent estimated half-spreads as observed NBBO. [R12, R13]

**Micro mode is not subsecond HFT.** The signals are mostly hourly/intraday, and costs must be realistic at this cadence. Neither mode should open a trade if its notional/estimated edge cannot justify the costs under its own frozen rule. A signal's absolute return *magnitude* is not automatically an expected alpha or an economic edge. Restrict count and rank by **causal signal strength**, without pretending that strength has been calibrated into expected profit.

**Retail opportunity-budget semantics:** Count *new physical market entry orders*, after netting; a long/short pair normally consumes **two** slots. Closing and mandatory risk liquidations do not consume entry slots, but incur all applicable costs. Weekly slot choice is chronological, subject to a predetermined score ranking among **currently available** candidates; never retrospectively pick that week's best-performing trade. If a weekly cross-sectional scan occurs only once, the best-known candidates at that scan can be compared and chosen simultaneously. Keep the capital, per-name and per-vintage constraints from V5 until a distinct, prospective protocol changes them.

---

## 3. Candidate menu at a glance (18 distinct signals)

| ID | Mode | Directional hypothesis | First eligible origins | Evidence | Priority | Main failure mode |
|---|---|---|---|---|---|---|
| **M01** | Micro | 30–60-minute **intraday continuation** | 10:30–15:30 | A [R1] | **A** | Published strongest effect concerns ETF close-period, not arbitrary stock four-hour returns |
| **M02** | Micro | 30–60-minute **intraday reversal** | 10:30–15:30 | D/A [R2] | **A** | Bid–ask bounce; effect may vanish after delay/costs |
| M03 | Micro | Opening **gap fade** | 09:30 (after receipt), 10:30 | H [R2,R3] | B | Overnight news continuation and open-reference noise |
| M04 | Micro | Opening gap + first-hour **confirmation** | 10:30–12:30 | A/H [R1] | B | Filter picks high-volatility news days without positive alpha |
| M05 | Micro | 30/60-minute **opening-range breakout** | 10:30–13:30 | H [R9] | B | Multiple false breakouts, executable price may chase move |
| **M06** | Micro | Cross-sectional **intraday residual momentum** | 10:30–15:30 | A [R2,R8] | **A** | Small 20-name cross-section, common-factor and correlated exposures |
| M07 | Micro | **Same-clock** historical return persistence | all 7, with matured prior-session slots | D/A [R2] | B | Study concerns daily-lag half-hour patterns, not an immediate 4h return |
| M08 | Micro | High-volume **short-term reversal** | 10:30–15:30 | A [R6] | C | Volume can signal information rather than temporary pressure |
| M09 | Micro | Late-day **overnight/intraday cross-period reversal** | 14:30/15:30 | A [R3] | B | Most of the 240-minute hold is *not* the overnight leg alone |
| R01 | Retail | **6-month minus 1-month** relative-strength winners/losers | once weekly | A [R4] | B | Literature holds for months, not 4 hours |
| **R02** | Retail | 20/60-day **daily trend** | once weekly | A [R5,R9] | **A** | Trend likely too slow to forecast next 4 hours |
| R03 | Retail | 20-day **trading-range breakout** | once weekly | A/H [R9] | B | Whipsaws, reversals, abrupt gaps |
| **R04** | Retail | 5-session cross-sectional **reversal** | once weekly | A [R7] | **A** | Published reversal pertains to next week, not fixed 4h hold |
| **R05** | Retail | Predeclared **peer-pair spread reversion** | once weekly | A [R10,R11] | **A** | Pair instability, two-leg trading costs, tiny sample |
| R06 | Retail | Factor/market **residual reversion** | once weekly | A [R11] | B | Regression/factor instability, correlated tail risks |
| R07 | Retail | Volatility-compression **range breakout** | once weekly | H [R9] | C | No direct academic validation of this combined rule |
| R08 | Retail | Overnight-versus-intraday **drift divergence** | late-day weekly | A [R3] | B | Opposing return sources not necessarily forecast 4h signed return |
| R09 | Retail | Abnormally **high-volume relative strength** | once weekly | A [R14] | C | Literature predicts following month, not immediate 4h return |

**Priority A** means strong design value and feasibility for a *first screen*, **not** expected profitability. B/C ideas are registered alternatives, not 18 chances to cherry-pick a retrospective winner. The hypothesis family itself is a multiple-testing choice.

---

## 4. MICRO strategy specifications (M01–M09)

For every strategy: **first** construct the signal from the decision-time information frontier; **then** enter under the shared micro cost, receipt, volume, liquidity, and capacity policy; **then** exit at the original 240-minute endpoint using the actual later valid execution bar. Report signal strength but leave primary sizing equal/static until the directional screen is complete.

### M01 — Intraday return continuation (priority A)

- **Signal:** Compute `r60_i(tau) = log(P_i(tau)/P_i(tau−60 scheduled minutes))` from completed observations entirely inside the present session; `s_i = sign(r60_i)` when `|r60_i|` exceeds a *past-only* same-slot volatility-scale threshold, otherwise 0. `u_i=|r60_i|/sigma_60,past`.
- **Selection:** Evaluate 10:30–15:30; rank eligible signals by `u`, take at most the micro new-entry budget, and avoid a second new cohort in the same stock and sign before the existing one exits (pilot turnover ablation).
- **Reason/evidence:** Gao et al. [R1] show first-half-hour market-ETF returns can forecast last-half-hour ETF returns, with state dependence. **This does not directly validate an individual-stock 60-minute signal for a four-hour horizon.**
- **Required data:** Causal, scheduled minute price references; historical same-clock volatility from completed earlier observations. **Risks:** return autocorrelation may be negative, input staleness, opening/closing structural effects. **Ablation:** `r30` vs `r60` and 10:30/11:30 origins, predeclared rather than optimized on profits.

### M02 — Intraday short-term reversal (priority A)

- **Signal:** Same `r30_i(tau)` or `r60_i(tau)` and historical scale as M01, but `s_i = −sign(r_L)` for a sufficiently extreme standardized move; 0 inside its no-trade region.
- **Reason/evidence:** Heston–Korajczyk–Sadka [R2] report stock-return reversal over intervals shorter than an hour attributable partly to liquidity and bid–ask bounce. **A 240-minute holding period is a different hypothesis.**
- **Required data:** Minutes, prior-known volatility, no future bar dependence. **Risks:** apparent reversal may be untradeable bid–ask bounce, high cost relative to small gross moves. **Ablation:** compare same signal at 30/60/240-minute *diagnostic outcomes* while keeping primary executable 240-minute test prespecified; directional IC conditional on lag.

### M03 — Opening gap fade

- **Signal:** After the day’s opening reference has actually been received, `g_i,d = log(O_i,d/C_i,d−1)` on consistent split units. When `|g|/sigma_gap,past` exceeds a predetermined past-only threshold, `s_i=−sign(g)`; no gap/reference means abstain.
- **Reason/evidence:** An opening dislocation might partly unwind; this *exact strategy is a heuristic*, not a result established by [R2,R3]. Both papers warn that intraday vs overnight behavior differs and can reverse.
- **Origin/data:** 09:30 only after opening minute ready, or 10:30; prior close and opening minute. **Risks:** real news gaps, conditional event risk, open-price validity. **Ablation:** compare gap fade vs M04 continuation under identical gap eligibility.

### M04 — Opening-gap continuation with first-hour confirmation

- **Signal:** Use `g_i,d` from M03 and completed early-session `r_open_i = log(P_i(10:30−)/O_i,d)`. `s_i=sign(g)` only if `sign(g)=sign(r_open)` and volume through the decision exceeds its prior same-clock reference; `u=min(|g|/sigma_g,|r_open|/sigma_open)`.
- **Reason/evidence:** A continuation hypothesis based on persistent order flow; analogical to intraday market momentum [R1], not directly demonstrated for stock gaps. **Data:** Opening, early minutes, volume observed before decision.
- **Risks:** a large signed gap may already be fully incorporated; volume can increase impact. **Ablation:** gap continuation *without* volume filter to isolate its contribution.

### M05 — Opening-range breakout

- **Signal:** Construct the completed 09:30–10:00 (or predeclared 09:30–10:30) session high/low `H_OR,L_OR`. At a later eligible decision, `s=+1` if the **already observed** reference price has exceeded `H_OR` by a predetermined noise buffer; `s=−1` if below `L_OR`; otherwise 0. Treat breakout events as triggers, not predictable same-bar fills.
- **Reason/evidence:** Trading-range-break rules have been formally studied [R9] on historical **daily index** data; this opening-range intraday variant is a *heuristic translation*.
- **Data/risks:** Minute highs/lows and signal price, exact completion. False breakouts, chasing the same move, missing prices, possible event-driven jumps. **Ablation:** 30/60-minute opening range.

### M06 — Cross-sectional intraday residual continuation (priority A)

- **Signal:** At the decision `tau`, compute `r60_i` and a *leave-one-out*, contemporaneously available basket reference `m60_-i=mean(r60_j : j≠i, j currently eligible)`. Then `a_i = r60_i−m60_-i`; long top two positive `a_i` and short bottom two negative `a_i` provided each passes a past-only scale screen. `u_i=|a_i|/sigma_a,i,past`.
- **Reason/evidence:** Tests whether individual-stock moves continue after removing broad co-movement, motivated indirectly by [R2,R8]. **No published four-hour 20-name stock evidence is claimed.**
- **Data/risks:** Current own/peer 60-minute causal returns, adequate eligible peer count (e.g. at least 12 of 20), no future-completeness gate. **Ablation:** raw `r60` versus residual `a_i`; equal-weight vs beta-adjusted market proxy fitted on past data.

### M07 — Same-time-of-day return persistence

- **Signal:** For each fixed origin clock slot `h`, calculate each stock’s *historical* next-half-hour return after the **same** slot over the preceding 20 **completed** trading sessions. `s_i = sign(mean_{k=1..20} r_i[d-k,h→h+30m])`, subject to a past-only magnitude/standard-error threshold.
- **Reason/evidence:** [R2] directly finds same-clock half-hour continuation across trading days. Our application uses that prior-session clock pattern to choose a **four-hour** position, so the endpoint translation is exploratory.
- **Data/risks:** A genuine previous-session half-hour return panel aligned to the calendar and receipt frontier; never today's *future* same-slot return. Small sample, nonstationarity and a potentially weak 20-name panel. **Ablation:** compare 5/20-day lookbacks *predeclared*; test whether any edge is concentrated in 30-minute rather than four-hour outcomes.

### M08 — Volume-conditioned short-term reversal

- **Signal:** At decision `tau`, compute signed last-hour return `r60` and volume shock `v_z = (log(1+V_recent)−median_prev20_same_slot)/MAD_prev20_same_slot` using only completed volume. `s_i=−sign(r60_i)` only if `|r60|/sigma_past` and `v_z` both exceed predeclared thresholds.
- **Reason/evidence:** Campbell–Grossman–Wang [R6] link high trading volume to the dynamics of later returns and temporary liquidity pressure at **daily** frequency. The intraday 4h rule is **analogical**, not an empirically verified extension.
- **Data/risks:** Minute volume and same-clock prior-session volume reference, not an eventual day's total volume. Volume can reflect genuine information. **Ablation:** reversal without volume gate, same entry limits.

### M09 — Late-day intraday/overnight reversal

- **Signal:** At 14:30 or 15:30, calculate the observable intraday return from prior close or today's received opening reference; if extreme, `s_i=−sign(r_intra)`, using a separate threshold trained on preceding sessions. Do *not* use today's future close.
- **Reason/evidence:** Lou–Polk–Skouras [R3] document distinct overnight/intraday continuation and **cross-period reversal**. Their measured effects do not guarantee that shorting this afternoon move over the next nominal four trading hours will work.
- **Data/risks:** Completed current-session returns, overnight segment attribution, next-day raw trading hours. **Ablation:** separately attribute entry→close, close→next-open and next-open→exit; do not mistakenly label a cross-overnight 240-minute return “pure overnight.”

---

## 5. RETAIL strategy specifications (R01–R09)

For retail, predeclare an **ISO-week decision event** (for example the first fully open XNYS session's 10:30 eligible decision) and **2/5/10 new physical entry orders per week** as three separate models. This is not an annual or weekly portfolio reset: cash, lots, fees, claims and borrow carry through continuously. Select strongest currently known eligible candidates, with no future week completion or return information. Keep original fixed 240-minute holding as the main *S2-C horizon-aligned* research test; a 1–5-session or multiweek natural-horizon retail study is a **secondary separately labeled experiment**, not automatically justified by the frozen four-hour risk proxy.

### R01 — Intermediate-horizon cross-sectional momentum (6–1 months)

- **Signal:** Using completed daily closes, `J_i = log(C_i,d−22/C_i,d−126)` (approximately six months ending one month ago). Long the highest-ranked two stocks with positive `J`; short the lowest two with negative `J`; abstain if rank universe too small.
- **Evidence:** Jegadeesh–Titman [R4] provide direct evidence for medium-horizon **formation and holding in months**; holding for just 240 trading minutes is a substantial extrapolation. **Data:** completed split-consistent daily close, 126+ days warmup.
- **Retail caveat:** A sparse 4h bet on a six-month score is a diagnostic of return-predictive transfer, not a reproduction of academic momentum. **Ablation:** candidate 1–5-session holding *separate from* primary four-hour experiment, with classical multi-day volatility sizing also tested.

### R02 — Daily trend following with 20/60-day structure (priority A)

- **Signal:** Using completed prior-session closes, compute `MA20_i`, `MA60_i` (or their log-price equivalents) and `s_i=sign(MA20_i−MA60_i)` only if the normalized difference exceeds a past-only trend-strength threshold. Rank by relative separation and take budget-limited entries.
- **Evidence:** Daily moving-average and trend following are analogical to Brock et al. [R9] and time-series momentum in index/other futures [R5]; neither establishes 4h long/short equity alpha.
- **Data/risks:** 60+ completed sessions, no today's closing price at an intraday decision; slow signals and rare genuine innovations. **Ablation:** 20 vs 60-day trend *not* an OOS-optimized grid; compare weekly decision to repeated hourly entry to demonstrate cost discipline.

### R03 — 20-session price-channel breakout

- **Signal:** Let `H20_i = max(high of prior 20 completed sessions)` and `L20_i = min(low of those sessions)`. At weekly decision, buy if the price **already observed and received** at `tau` crosses `H20` by a predetermined buffer; sell/short if crosses below `L20`. No fill at the breakout bar's unknowable price.
- **Evidence:** Brock et al. [R9] studied a trading-range-break strategy on a very different sample, not this exact 20-day stock/4h rule.
- **Data/risks:** Past daily high/low; unusual corporate actions, gaps and intraday execution. **Ablation:** breakout gated on preceding daily volatility; only after directional screen.

### R04 — Weekly cross-sectional loser/winner reversal (priority A)

- **Signal:** `J5_i=log(C_i,d−1/C_i,d−6)`, known before this week's decision. **Long bottom two** negative 5-session performers and **short top two** positive performers, limited to the weekly entry budget. This is a cross-sectional contrarian rule, not merely flipping the failed V5 per-name sign on every origin.
- **Evidence:** Lehmann [R7] studied short-run stock-return reversals over approximately week-to-week intervals. An executed four-hour bet is again a new hypothesis.
- **Data/risks:** Completed daily close and current eligible names; potential liquidity pressure versus genuine news effects, split-adjustment consistency. **Ablation:** raw per-name reversal versus market-residual reversal; same weekly budget.

### R05 — Preselected related-stock spread mean reversion (priority A)

- **Signal:** Fix a short list *before testing* based on economic relatedness, e.g. `KO/PEP`, `XOM/CVX`, `BAC/WFC`. Fit historical `beta_ij` and rolling residual mean/sd on **past completed** daily closes only. Define `z_ij = [log(P_i,tau)−beta_ij log(P_j,tau)−mu_ij,past]/sigma_ij,past`; if z is high, short the expensive leg and long the relatively cheap leg; reverse if low. Omit if the pair fails prespecified stability or short-availability checks.
- **Evidence:** Gatev–Goetzmann–Rouwenhorst [R10] study historical paired stocks over **months** and Avellaneda–Lee [R11] residual mean reversion at daily horizons. Our hourly execution and fixed 20-stock candidate roster are **not their original design**.
- **Data/risks:** Daily/received-minute prices for both stocks, 60+ day historical fit, actions, *two-leg* orders and fees; each leg consumes a weekly retail entry slot. A pair is not riskless or automatically cointegrated. **Ablation:** equal-dollar vs historical beta-neutral hedge; model-specific risk sizing must preserve both-leg hedge exposure.

### R06 — Factor-neutral residual reversal

- **Signal:** On prior 60 completed sessions, estimate stock return `beta_i` against the equal-weight universe return (or a predeclared, *available* index). Define the most recent five-session residual cumulative return `A_i=∑_{k=1..5}(r_i,d-k−beta_i r_m,d-k)`. Long the most negative two standardized residuals and short the most positive two, once weekly.
- **Evidence:** The residual mean-reversion logic is closely related to [R11] (PCA/sector ETF statistical arbitrage), but a single equal-weight panel factor and a four-hour exit are deliberately simplified.
- **Data/risks:** 60+ completed days and beta estimation using only earlier history, consistent leave-one-out construction where appropriate. Market factor and individual residual can change after a shock. **Ablation:** R04 raw reversal versus R06 residual reversal.

### R07 — Volatility-contraction breakout

- **Signal:** Detect low *past* volatility (`RV10_i` below its previous 60-session 20th percentile), then require a subsequently **observed** price to break the past 20-session high/low in a consistent direction. Enter at the next eligible executed bar, not at a retrospective threshold crossing.
- **Evidence:** A deterministic hypothesis combining volatility compression with a range-break rule, **not directly supported** by [R9] or [R15]. Research-grade until demonstrated.
- **Data/risks:** 60+ completed days of volatility and highs/lows, plus current price known at decision. Very few triggers, event breaks and gaps. **Ablation:** breakout without low-volatility condition.

### R08 — Prior overnight vs intraday trend divergence

- **Signal:** For the last ten completed sessions, calculate `ON10_i=∑ log(O_i,k/C_i,k−1)` and `ID10_i=∑ log(C_i,k/O_i,k)`. If `ON10` is strongly positive and `ID10` negative, select long near a predeclared late-day eligible origin; reverse for strongly negative overnight/positive intraday. Threshold each leg against pre-existing historical scales.
- **Evidence:** Lou–Polk–Skouras [R3] document the tension between overnight and intraday expected returns. Their long-horizon decomposition does not prove a simple 10-session predictor or four-hour edge.
- **Data/risks:** Genuine completed daily opens/closes and corporate actions, no current-day close before it exists; weekend/overnight borrow exposure. **Ablation:** overnight-only versus difference score (predeclared).

### R09 — High-volume return premium proxy

- **Signal:** Normalize each fully completed day's volume by a *past-only* same-ticker rolling 60-session volume reference. Over the last five completed sessions compute an abnormal-volume score `V5_i`. On a predeclared weekly rebalance, long highest positive standardized V5 names and short lowest negative V5 names (if rank separation exceeds a fixed prefix-derived cutoff).
- **Evidence:** Gervais–Kaniel–Mingelgrin [R14] document daily/weekly abnormal volume patterns predictive of returns **over the following month**, not an intraday four-hour return. Our construction is thus a transfer test, not a replication.
- **Data/risks:** Volumes must respect split/unit changes; a high-volume name can be reacting to news and never mean-revert. Distinguish return continuation versus volume-only score as a separate later question.

---

## 6. Fast, scientifically useful screening sequence

**Do not immediately run all 18 strategies × 2 modes × 4 sizing arms × many cost scenarios.** That would repeat V5's storage/runtime problem and create excessive multiple testing.

### Gate S0 — Pre-register the economic identity

For each strategy, store one short immutable specification with: ID, code hash, inputs, original-origin eligibility, causal observation frontier, trigger, two-sided sign, optional score, weekly/daily entry limit, 240-minute nominal exit, cost regime, abstention and forced-close behavior. Define signal thresholds using historical *prefix* or fixed initial values, not realized 2021–2024 profits. Fixed 20 survivors are an explicit limitation. Also retain the legacy V5 five-day sign and no-trade reference.

### Gate S1 — Direction-only signal quality, no portfolio costs (fastest)

Calculate for **all eligible origins**, without conditioning on eventual success:

1. Number of potential signals, actual entries after scheduled caps, distinct names, long/short balance and origin/time distributions;
2. Mean/median **executable holding** signed log return `s_i * log(P_exit/P_entry)` and hit rate; report nominal forecast-horizon return *separately*;
3. Day-level, clustered summaries (not naive standard errors treating thousands of overlapping cohorts as independent);
4. Gross winner dollars, gross loser dollars, median winner/loser and outlier concentration under a common *hypothetical equal notional* — not yet an actual funded S2-C portfolio;
5. Gross break-even friction versus plausible round-trip costs at the observed effective trade sizes;
6. Lookahead negative control: lag the directional score by one session or shuffle within predefined session/day blocks, without changing price eligibility or the execution clock.

**Do not call a positive mean signed return proof of alpha.** Check dependence, year stability and the scale of the expected gross move against transaction costs.

### Gate S2 — Cheap *funded* micro/retail simulation

Advance only a handful of priority candidates that pass a **predefined** minimum gross signal/coverage and economic plausibility screen. Reuse the V5 causal execution logic, corporate actions and baseline accounting invariants but run a **streaming lightweight simulator**, not 24 ledger-rich reproductions. Primary equal-notional vs no-trade and legacy five-session sign. Use separate 2021–2022 exploratory construction, 2023 diagnostic, 2024 secondary retrospective comparison; **none of these years is untouched independent confirmation after previous extensive research**.

Save compressed per-experiment files only: `config.json`, `summary.json`, `daily_nav.parquet`, `trades.parquet` (or minimal equivalent), `cost_breakdown.csv`, `signal_counts.csv`, `integrity.json`; an optional capped sample of example events. **Target under 100 MB/experiment** where feasible and no repeated daily state/checkpoint archives. Do not delete or mutate V5 artifacts. Missing prices, splits/dividends, unresolved claims, short borrow and timing still fail transparently; fast means smaller evidence payload, *not imaginary fills*. Do not use 2025+ equity prices.

### Gate S3 — Test incremental S2-C value **only after** selecting a directional rule

With a *fixed* direction/entry selection and horizon, test in the same mode/accounting base:

- `EQUAL` (constant or equal-notional allocation),
- `ROLLING_RISK` (pre-existing strictly matured 60 observations),
- `EWMA_RISK` (pre-existing strictly matured `.94`),
- `S2C_RISK` (original frozen C-A main magnitude forecast and 2019 b/floor, initial cap `clip(b/max(mhat,m_floor), .5, 1.5)`).

Compare matched eligible trade opportunities and separate attainable populations. Do not let each arm's current S2-C prediction change the **direction** or retrospectively select trades. Different allocators may legitimately encounter different funding/cap exclusions; report both matched decision opportunities and actual funded trades/exposure, and compare matched gross risk and matched realized volatility separately. S2-C forecast size estimates physical conditional absolute endpoint move; **not** signed alpha, future quadratic variation or a multiweek sigma forecast.

### Gate S4 — Escalate only if meaningful

Promote to ledger-rich validation when a candidate survives: (i) two-sided execution and gross edge versus chosen costs, (ii) plausible performance after *both* professional and conservative cost estimates where relevant, (iii) no single-stock/year anomaly drives the result, (iv) no hidden lookahead/missingness advantage, and (v) demonstrable reason S2-C sizing beats simpler risk sizing. The final independent Stage6 audit remains separate. A strategy rejected at S1/S2 should remain rejected and reported; don't silently tune until one looks good.

### Output discipline and audit requirements

- **Micro and retail results are distinct economic experiments** and should not be collapsed into a single Sharpe table without capital/frequency/cost labels.
- For each simulation provide **gross signed price-move trading P&L**, gross winning dollars, gross losing dollars, commissions, incremental spread proxy, impact proxy, borrow, financing, corporate-action net cash, *net* P&L and reconciliation to closing NAV; ensure that all P&L components are on the same physical/virtual attribution basis, avoiding double charging.
- In particular **$1 applies to a physical external order, never to each virtual cohort**. Endogenous position sizes can make a no-minimum sensitivity noncomparable without a funded rerun.
- Store accounts and costs consistently through annual model switch; no reset or privileged 2024 relabeling.
- Report conditional-short and retrospective-corporate-action uncertainty, 2010–24 adjusted source vintage limitations and short-availability unknowns.

---

## 7. Six-experiment starter matrix (preregistered recommendation, not a claim about winners)

| Experiment | Strategy | Mode | Why this is first | Direct ablation | Primary test |
|---|---|---|---|---|---|
| A1 | M01 | Micro | Closest simple directional momentum to intraday horizon | M01 vs M02 (same return window, flipped sign) | Are net four-hour returns continuing or reversing? |
| A2 | M02 | Micro | Tests short-term liquidity reversal without expensive features | 30 vs 60 minutes | Does any reversal survive delay/friction? |
| A3 | M06 | Micro | Separates stock-specific direction from broad-market co-movement | Raw vs market-residual 60min | Does cross-sectional residual information add value? |
| B1 | R02 | Retail | Transparent low-turnover slow trend reference | 20/60 daily trend vs V5 five-day sign at same weekly budget | Can capping trades make a trend policy economically sane? |
| B2 | R04 | Retail | Weekly reversal is a theoretically different sign mechanism | Weekly CS reversal vs weekly CS continuation | Does reversal transfer to next 4h? |
| B3 | R05 | Retail | Pair-spread relative value has different economics from one-stock directional momentum | Historical pair spread vs market residual (R06) | Can a hedgeable relative signal cover two-leg retail costs? |

Initial number of new entry orders: micro `2/6/12 per day`, retail `2/5/10 per ISO week` as separate frozen configurations; in a truly fast first pass, evaluate **one default cap per mode (micro 6/day, retail 5/week)** and report the others only if worth deeper examination. This choice is *preregistered*, not selected by returns. Pair entry counts two physical legs. Use one baseline professional cost and one conservative retail model at first, without a costly scenario grid.

## 8. References and what each actually supports

These papers were verified from journal, university or author-hosted abstracts. Their reported contexts are shown to guard against incorrectly transferring empirical findings to our four-hour 20-stock problem.

- **[R1]** Gao, L., Han, Y., Li, S. Z., Zhou, G. (2018), *Market intraday momentum*, **Journal of Financial Economics** 129, 394–414. [DOI](https://doi.org/10.1016/j.jfineco.2018.05.009). **Context:** first half-hour market ETF signal predicts last half-hour ETF return, not 4h single-stock alpha.
- **[R2]** Heston, S., Korajczyk, R., Sadka, R. (2010), *Intraday Patterns in the Cross-section of Stock Returns*, **Journal of Finance** 65, 1369–1407. [DOI](https://doi.org/10.1111/j.1540-6261.2010.01573.x). **Context:** same half-hour return patterns across days and subhour liquidity-driven reversals; the current-signal→4h translation is a hypothesis.
- **[R3]** Lou, D., Polk, C., Skouras, S. (2019), *A Tug of War: Overnight versus Intraday Expected Returns*, **Journal of Financial Economics** 134, 192–213. [DOI](https://doi.org/10.1016/j.jfineco.2019.03.011). **Context:** overnight/intraday returns and offsetting cross-period tendencies, not our exact hold.
- **[R4]** Jegadeesh, N., Titman, S. (1993), *Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency*, **Journal of Finance** 48, 65–91. [DOI](https://doi.org/10.1111/j.1540-6261.1993.tb04702.x). **Context:** 3–12-month relative-strength formation/holding, not intraday.
- **[R5]** Moskowitz, T., Ooi, Y. H., Pedersen, L. (2012), *Time Series Momentum*, **Journal of Financial Economics** 104, 228–250. [DOI](https://doi.org/10.1016/j.jfineco.2011.11.003). **Context:** 58 liquid index/currency/commodity/bond futures, 1–12-month return persistence; not 4h single-stock evidence.
- **[R6]** Campbell, J., Grossman, S., Wang, J. (1993), *Trading Volume and Serial Correlation in Stock Returns*, **Quarterly Journal of Economics** 108, 905–939. [DOI](https://doi.org/10.2307/2118454). **Context:** daily return autocorrelation and volume/liquidity-demand theory.
- **[R7]** Lehmann, B. (1990), *Fads, Martingales, and Market Efficiency*, **Quarterly Journal of Economics** 105, 1–28. [DOI](https://doi.org/10.2307/2937816). **Context:** short-horizon week-to-week contrarian returns, not a four-hour holding.
- **[R8]** Lo, A., Mamaysky, H., Wang, J. (2000), *Foundations of Technical Analysis: Computational Algorithms, Statistical Inference, and Empirical Implementation*, **Journal of Finance** 55, 1705–1765. [DOI](https://doi.org/10.1111/0022-1082.00265). **Context:** formal, objective evaluation of daily technical patterns; not direct evidence for specific M06 returns.
- **[R9]** Brock, W., Lakonishok, J., LeBaron, B. (1992), *Simple Technical Trading Rules and the Stochastic Properties of Stock Returns*, **Journal of Finance** 47, 1731–1764. [DOI](https://doi.org/10.1111/j.1540-6261.1992.tb04681.x). **Context:** moving-average and trading-range rules on long historical Dow index sample.
- **[R10]** Gatev, E., Goetzmann, W., Rouwenhorst, K. G. (2006), *Pairs Trading: Performance of a Relative-Value Arbitrage Rule*, **Review of Financial Studies** 19, 797–827. [DOI](https://doi.org/10.1093/rfs/hhj020). **Context:** historical multi-month U.S. equity pairs study; two-leg trading and stability matter.
- **[R11]** Avellaneda, M., Lee, J.-H. (2010), *Statistical Arbitrage in the U.S. Equities Market*, **Quantitative Finance** 10, 761–782. [Record](https://ideas.repec.org/a/taf/quantf/v10y2010i7p761-782.html). **Context:** PCA/ETF residual mean reversion in broad equity universes, not a two-leg hourly strategy on twenty survivors.
- **[R12]** Corwin, S., Schultz, P. (2012), *A Simple Way to Estimate Bid-Ask Spreads from Daily High and Low Prices*, **Journal of Finance** 67, 719–760. [DOI](https://doi.org/10.1111/j.1540-6261.2012.01729.x). **Context:** daily H/L historical spread estimator, not direct contemporaneous intraday quote evidence.
- **[R13]** Frazzini, A., Israel, R., Moskowitz, T. (working-paper draft), *Trading Costs of Asset Pricing Anomalies*. [Author-hosted research PDF](https://pages.stern.nyu.edu/~afrazzin/pdf/Trading%20Cost%20of%20Asset%20Pricing%20Anomalies%20-%20Frazzini%2C%20Israel%20and%20Moskowitz.pdf). **Context:** institution-level empirical execution/capacity; not a guarantee of $0.002 per-share access for us.
- **[R14]** Gervais, S., Kaniel, R., Mingelgrin, D. (2001), *The High-Volume Return Premium*, **Journal of Finance** 56, 877–919. [DOI](https://doi.org/10.1111/0022-1082.00349). **Context:** abnormal volume predicts subsequent **month** returns, not four-hour alpha.
- **[R15]** Sullivan, R., Timmermann, A., White, H. (1999), *Data-Snooping, Technical Trading Rule Performance, and the Bootstrap*, **Journal of Finance** 54, 1647–1691. [DOI](https://doi.org/10.1111/0022-1082.00163). **Context:** multiple-testing/data-snooping and technical trading evaluation; relevant to pre-registration and falsification, **not** a directional edge by itself.

---

## 9. What a legitimate successful result would look like

A credible CV-strength conclusion would not merely say that one of 18 ideas was the best in 2021–2024. It would show, under a **frozen, reproducible, cost-aware** design: a plausible directional effect at the actual executable horizon; economic survival in the chosen micro or retail mode; enough trades to estimate uncertainty; robustness to real source gaps and corporate actions; and a **paired improvement from S2-C sizing over equal, rolling, and EWMA sizing** that is not simply lower exposure or selection artifacts. A fresh prospective or genuinely independent confirmation period would then be necessary for stronger out-of-sample claims.

**Nothing in this menu asserts that any of the 18 strategies is profitable or authorizes experiments.**
