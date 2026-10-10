# Track A — Cross-Sectional Equity Alpha
## First-Pass Frozen Architecture Experiment Roadmap v1.0 (v2 state + lead–lag roadmap, with MC2 added)

**Prepared:** 10 October 2026  
**Status:** **FROZEN FIRST-PASS EXPERIMENT MENU v1.0** — the architecture hypotheses, staged experiment sequence, and conditional branches in this document are fixed as the initial shortlist. This does **not** freeze exact stocks, feature definitions, hyperparameters, execution clock, train/test dates, or permission to train every optional row; those remain for the interactive design and shared sign-off.  
**Owner:** Researcher A — predictions and rankings **across stocks from different sectors**.  
**Baseline provenance:** Preserves the 10 October 2026 `Track_A_Cross_Sectional_Architecture_Experiment_Roadmap_v2_State_LeadLag.md` experiment menu, state/lead–lag scope, priorities, and conditional logic; the **sole newly selected architecture component is MC2** (step-specific market feature gating).  
**Freeze scope and amendments:** No new optional families are authorized by this revision. A proposed change to the first-pass menu must be documented as a new roadmap version and agreed between researchers if it affects shared comparisons. The separate `Shared_Project_Specification.md` governs common conventions; the later track design protocol will lock implementation details.  
**Primary design source:** `Consolidated_Architecture_Design_Menu.md` (hereafter **Menu**).  
**Context and literature:** `Modern_Quant_DL_Papers_2023_2026.md` (**Papers**) and `LST_Proposal.pdf` (**Proposal**).  
**Optional cautions:** `Recurrent_Architecture_Research.md` and `State_Dependent_Signed_Recurrent_Interactions.md` offer subsequent *hypotheses and mathematical diagnostics*, **not additional required experiments**. The first pass below is organized by the Menu's component IDs.

> **Central question:** For a small panel of liquid US equities from multiple sectors, do shared recurrent representations, USA500 conditioning, market-guided feature weighting, or explicit peer information improve four-trading-hour **universe-relative ranking** enough to justify their complexity and trading costs?
>
> **Decision philosophy:** Build the cheapest credible comparator, test *one architectural hypothesis at a time*, stop when information is insufficient, and protect one untouched confirmation period. A five-stock failure is not automatically an architectural failure.

---

## 1. Mandate, starting sample, and boundary with Track B

- **Prototype:** approximately five years of available **hourly, regular-session** history on **five stocks from different sectors**. The Proposal's starting example is **AAPL, JPM, JNJ, WMT, CAT** (provisional; subject to coverage, corporate-action, liquidity and point-in-time checks). The Proposal identifies July 2020–June 2025 as an intended overlapping window, **not a guarantee of usable observations**. The five stocks are for an engineering/scientific screen, not a definitive cross-sectional alpha claim.
- **Selective expansion:** roughly 20 liquid stocks across several sectors; up to 20–30 if data and resources permit. Expand **when a mechanism needs more independent peer information**, not only when a five-stock backtest looks good.
- **Frequency and horizon:** hourly features and a four-**complete-trading-hour** forward horizon, with execution strictly after the input bar is complete. Confirm trading-calendar and closing-stub conventions *before* calling a timestamp a valid four-hour origin.
- **Required core market series:** USA500. Use the same aligned, timestamp-causal version across market-conditioned models. USATECH.IDX belongs **primarily to Track B**; optionally examine it for Track A only as a *separately labeled additional-information* test if it is available and the question warrants it. Options/macroeconomic series are not prerequisites.
- **New core phenomena (2026-10-10 revision):** causally observed **bull/bear and volatility state** and **directed stock-to-stock lead–lag signals**. Start with inexpensive, fully specified indicators and matched-information ridge/LSTM controls. Test sophisticated state-dependent coupling only if these cheaper tests support it.
- **Stockwise shared parameters:** the recurrent stock encoder is initially shared across all names. Track A predicts relative performance **across the complete eligible multi-sector universe**.
- **Track B's different problem:** the collaborator ranks names *within sector* (initially five from one sector). Do **not** pool the two tracks' preliminary metrics or compare raw Sharpe numbers as if their portfolios and universes were identical.

**Primary target (Menu TG0):** for available stock returns over the chosen executable four-trading-hour interval,

\[
 r_{i,t}^{(4)}=\log\frac{P_{i,t+4}}{P_{i,t}},\qquad
 y_{i,t}^{CS}=\frac{r_{i,t}^{(4)}-\operatorname{median}_{j\in\mathcal U_t}r_{j,t}^{(4)}}{\operatorname{MAD}_{j\in\mathcal U_t}(r_{j,t}^{(4)})+\epsilon}.
\]

Here `t+4` denotes the *explicitly verified horizon*, not automatically four stored bar rows. Future returns are labels only. Choose and freeze the MAD convention, scale floor, and treatment of low-dispersion dates using development data. With **N=5**, target scaling and Spearman rank IC are unstable/discrete; report *unscaled relative returns*, pairwise ordering or rank hit rate, and daily aggregation as complementary diagnostics. Do **not** replace TG0 silently because an alternative target fits better.

### Core design envelope

| Dimension | First-pass choice | Status / meaning |
|---|---|---|
| Input representation | **FT0** — compact, stationary/normalized OHLCV indicators | Core; no large indicator search |
| Temporal representation | **TM0** — shared standard LSTM | Core; initial lookback **48** available trading-hour observations |
| Spatial mechanism | **SP0** own-history control, then **causal lagged peer indicators** | **SP3** mixing first conditional learned exchange; **SP1** alternative; lead–lag indicators are *inputs*, not another Menu spatial module |
| Market | Stock-only first; **MC0** USA500; then **MC1** endpoint gate and **MC2** step-specific gate (MASTER-inspired adaptation) | Compare MC2 with MC1/MC0 *conditionally* after checking intra-window state variation; monitor bull/bear × volatility coverage |
| Factors | **FC0** initially | **FC6/FC7** conditional after suitable cross-section exists |
| Regimes | **RG0** continuous observed USA500 state + *diagnostic* causal bull/bear/high/low-vol buckets | **MC1 = RG1 = FT1** is the *same* gating module; RG2 VQ deferred |
| Adaptation | **AD0** static fitted mapping | **AD3**, then **AD1** only if evidence supports feedback adaptation |
| Prediction | **TG0** 4h universe-relative target | **TG2** optional separate auxiliary-horizon test |
| Complexity | **CP0**, bounded widths **CP1**; **CP2** if SP3; **CP3** if SP1 | Prefer matched-information and capacity-aware comparisons |
| Training | **TR0** ordinary joint training; **TR1** gating/attention; **TR2** mixing | **TR4** only if AD3 is attempted |

**Avoid double-counting modules:** `MC1 = FT1 = RG1` for practical market-feature gating; `SP4` pooled exchange may overlap with `FC6`; `TM2` overlaps `SP2`; `AD3`, `TR4`, and `CP7` describe the same rolling-head family viewed from different angles. Adding duplicate modules is not evidence of an additional hypothesis.

---

## 2. Shared research contract: data, budget, and honest inference

### 2.1 Data/execution rules — non-negotiable, but inexpensive

1. Fix eligibility using information available **at decision time**. Audit symbols, actions, splits, session times, holidays, early closes, hourly USA500 alignment and vendor semantics. Verify at least a few hand-calculated features, labels, and executions, including near the market close.
2. Standardize/clip/impute with *training-only fitted* parameters. Define causal indicator warm-up. No forward-filled future prices or use of future-index/symbol membership in model inputs. Preserve quality and availability masks.
3. Construct labels from the specified executable entry/exit convention. For four-hour holding, explicitly reject origins for which four **complete** trading hours cannot be obtained under the initial no-overnight policy. Do not quietly treat a 30-minute closing stub as an hour.
4. Use a **chronological development split** with common dates across names, plus a **strictly untouched final confirmation period**. A nominal 60/20/20 split is a starting point, but *once used for architecture decisions, a period is development data*. Purge label windows crossing boundaries; longer auxiliary horizons require appropriate longer purges. Historical context windows may use legitimate pre-boundary past observations.
5. Compare models on exactly the same eligible date-name observations when claiming incremental improvements. Record how missing names change the target cross-section and peer inputs; avoid selection on future label availability.
6. No backtest trade based on a bar before the bar closes. For overlapping four-hour forecasts, fix total exposure via sleeves or an equivalent rule; do not count every hourly prediction as independently fully funded.

### 2.2 Screening resources versus final evidence

| Layer | Default economical rule | Why |
|---|---|---|
| Pipeline smoke test | Tiny date subset, one stock then all five; can use synthetic labels | Find errors without repeated neural training |
| First architecture screen | Usually **one seed** and **one sensible width** (e.g. 32) on training/development | A quick *screen*, **not** grounds for rejecting a promising component |
| Inconclusive or promising candidates | Add a second seed **or** one targeted data/capacity diagnostic (not a grid) | Separate implementation/optimization noise from possible signal |
| Shortlist | Approximately 2–3 architecture families, a small predefined capacity check, about **3 seeds** | Establish that a gain is not one lucky initialization |
| Confirmation | Finalist(s) only: locked test, selected walk-forward folds, trading costs; focused null where feasible | Spend expensive computation on actual claims |

The numbers above are **budget suggestions, not finalized hyperparameters**. The later interactive design conversation should lock an explicit wall-clock/GPU/CPU budget and maximum training count. **No exhaustive search across 10 Menu dimensions.** If resources tighten, drop conditional branches, not data-integrity controls.

### 2.3 Primary decision evidence

- **Forecast:** one predeclared validation ranking statistic (prefer mean per-decision Spearman IC, supplemented by pairwise concordance for five names), paired improvement in target loss, and daily/time-block stability. Cross-sectional IC with five names is very noisy; do not call a small increase significant.
- **Economic:** identical frozen ranking-to-trade mapping; gross/net P&L, turnover, cost drag, max drawdown, risk exposure, and net performance at more than one explicitly assumed cost. Start with top/bottom-20% (one long/one short for five names), dollar-neutral and fixed gross. This is a concentrated feasibility backtest, **not** a realistic deployable diversifier.
- **Complexity:** fit time, training/inference cost, parameters, learning curve and basic gradient health. Better training loss alone does not qualify.
- **Uncertainty:** confidence intervals/paired block variability based on date or trading-day blocks; correlated stocks and overlapping targets are not independent replicates. Seeds measure optimization variability, not new market histories.
- **Selection:** define the development metric and tie-break rule before running. Prefer the simpler candidate when improvements are small relative to paired uncertainty (an informal *one-standard-error simplicity preference* is reasonable for development, not a significance test).

### 2.4 Distinguish six outcomes; never infer 'architecture cannot work' from one weak run

| Finding | Plausible reading | Cheapest next action |
|---|---|---|
| Data/timing checks fail | Implementation/data defect | **Stop** all modeling and fix audit |
| Train loss does not fall; gradients/gates pathological | Optimization or code defect | Check overfit-on-a-tiny-batch, numerical ranges, width/LR; **one rescue** |
| Train improves, validation collapses; complex model unstable | Overfit or mismatch to effective sample | Capacity/regularization check; simpler control |
| Estimates imprecise, high period/seed dispersion, little sector/peer diversity | Insufficient *evidence* or limited cross-section | Label **inconclusive**; expand to 20 names if mechanism demands peers |
| Stable failure of the *mechanism* on a cheap planted synthetic sanity case | Misimplementation or structural limitation for the proposed mechanism | Debug or deprioritize that construction |
| Clean mechanism test, matched-information comparator, and adequately informative expanded OOS still do not improve | No evidence of incremental value **in this setting** | Deprioritize without asserting impossibility |

**Rescue rule:** each literature-motivated component gets at most **one primary rescue** (e.g., correct capacity mismatch, repair saturated gate, add relevant names, or verify peer access) plus an explicitly justified second diagnostic only if cheap. Document triggers *before* inspecting extra results. A synthetic success verifies capability/implementation; it **does not** establish financial edge. Negative evidence may stem from **no exploitable signal in the inputs**, not from architecture or sample size alone; this distinction may remain unresolved.

---

## 2A. New design contract: observed market states and directed predictive lead–lag

### State and lead–lag protocol (added in v2; operational definitions to freeze in the design chat)

**Three distinct hypotheses, not one large architecture:**

1. **State information:** Does knowing the *already observed* market/sector condition help? Supply state variables to lagged ridge and plain LSTM as ordinary inputs before adding a gate. A conventional LSTM with observed state can already learn conditional effects; an explicit gate tests an inductive bias, not access to new information.
2. **Directed predictive lead–lag:** Does a *completed* peer return at an earlier/current observable decision time predict **subsequent** stock relative return beyond own-stock and index history? Ordinary contemporaneous correlation is **not** a lead–lag finding. Test simple peer features first, then trained mixing/attention.
3. **State-dependent lead–lag:** Does that predictive peer coefficient **change magnitude or sign** across observed states? Start with a low-parameter interaction/varying-coefficient baseline; only afterward consider nonlinear conditional peer fusion or messages. Correlations that flip sign without conditional mean predictability may help risk models but do not imply alpha.

**Causal state construction** (proposals; exact windows/thresholds to select ex ante):

- Continuous, point-in-time features: lagged index log returns at a few lookbacks, trailing realized volatility, short/long volatility ratio, distance to *trailing* moving average or trailing trend score. Use data **published/completed** by the forecast decision and training-only fitted transformations.
- Descriptive **bull/bear** trend: e.g. sign of a predeclared lagged return or trailing MA-distance; **high/low volatility**: e.g. training-period quantile threshold for trailing realized volatility. Trend and volatility are **two separate axes** (bull-high-vol, bull-low-vol, bear-high-vol, bear-low-vol) *only when each cell has sufficient observations*. Default to separate trend and volatility diagnostics; never force four-cell modeling if sparse.
- Rules must not use hindsight market peaks/troughs, future 4h volatility, end-of-day prices before that close, smoothed full-sample HMM states, or post-test-fitted thresholds. These are descriptive state labels, not claimed latent economic regime identification.
- Report occupancy, number and duration of independent regime episodes, effective dependence and out-of-period stability. If an apparent benefit exists only in one very small regime, label it exploratory.

**Causal lead–lag candidate design** (cheap menu of alternatives, not an automatic full grid):

- Define stock log returns from completed hourly bars; construct market/sector **residual innovations** only from *historically fitted* betas or specified observed factors, using a documented convention and no future returns.
- Candidate directed predictor for stock \(i\) from peer \(j\): \(z_{j,t-\ell}\), for one or two predeclared lags \(\ell\in\{0,1,2\}\) measured in correctly aligned *completed trading observations*. If \(\ell=0\), the peer's bar must be fully completed before forecast/entry, and the outcome starts **after** that observation; this is not a same-time execution prediction.
- Screening features: a few lagged peer innovations; leave-one-out peer mean/dispersion; rolling **lagged** cross-covariance or lead–lag coefficient computed exclusively from past training/rolling windows; a single bounded state interaction \(u_{ij,t}=z_{j,t-\ell}z_{i,t}\) only if economically motivated. Avoid searching every directed pair, every lag and every indicator.
- For a transparent state-interaction null, use the same observed inputs in a **shrunk ridge or varying-coefficient comparator**, e.g.

  \[\widehat y_{i,t}=f_{0}(\text{own, index, peer histories})+\beta(q_t)z_{j,t-\ell},\qquad \beta(q)=b_0+b_1\phi(q),\]

  or one targeted product \(\beta(q_t)z_{j,t-\ell}z_{i,t}\). Smooth/low-dimensional \(\phi\) and sign flexibility are preferred initially. A *mandatory sign switch* is a **strong prior requiring a specific reason**, not a default.
- **Four controls** for any claimed learned lead–lag benefit: (i) own + exogenous index information; (ii) same *lagged peer access* through ridge; (iii) same access through ordinary LSTM; (iv) only then a special SP1/SP3/SP5 spatial module. When comparing state-dependent fusion, include a constant-coefficient (state-independent) counterpart; match horizons, known information, allowed peers and tuning budget.
- Use a **negative-information diagnostic** where useful: isolate peer *residual* signals after common-index history, then replace their alignment using a specified **training/development-only** timing-destruction procedure preserving meaningful calendar dependence where feasible. Do not casually shuffle individual stocks or claim an exact permutation p-value under nonstationarity.
- Distinguish **known lagged predictive association**, **contemporaneous dependence**, **causal influence**, and **trading net alpha**. The plan measures the first, not causal market transmission. A predictive relationship does not necessarily survive execution lag and costs.

**Economical triage:** compute candidate features once from canonical bars (no data duplication); screen a tiny predeclared set via ridge and paired date-block metrics; **one** matched LSTM experiment on the most defensible lead–lag signal; promote to trained SP1/SP3/SP5 or conditional coupling *only* if the cheaper mechanism tests support it or five names are demonstrably inadequate. Store every attempted selection in the experiment ledger; do not pick a different lag after inspecting final test data.

## 3. The core executable experiment ladder

These are **decision nodes**. A conditional node is *not* a promise to train it. Label versions `A-E0` through `A-E9` separately from the Menu's `A0–A8` illustrative architecture ladder.

### A-E0 — Data, labels, strategy, and zero-neural sanity **[MANDATORY]**

**Question:** Is the same research problem being measured accurately for every later model?  
**Models/training:** no neural model. Plot several stocks/periods; sample individual features and four-hour labels; simple momentum ranking and mechanically defined equal-exposure top/bottom portfolio.  
**Key deliverables:** coverage table, alignment/causality audit, eligible-decision calendar, split and purge demonstration, cost assumptions, buy/hold/execution convention, reproducible feature dictionary.  
**Pass:** no unexplained leakage, split, timestamp, missingness or exposure bug; a reproducible baseline produces finite and interpretable outputs.  
**Fail:** stop. A striking 5-stock backtest does not waive sanity checks.

### A-E1 — Information-equivalent nonrecurrent baselines **[MANDATORY; CHEAP]**

**Menu:** FT0 / TG0 / FC0 / AD0 / RG0.  
**Question:** Is there any simple evidence of temporal/market information without recurrence?  
**Compare:** predefined recent-return momentum; ridge with compact lagged normalized own-stock features; **separate** ridge + aligned USA500 features (later peer-input ridge). Optional tiny MLP only if inexpensive and useful for nonlinear-capacity attribution.  
**Controls:** same labels, splits, tuned regularization from a tiny grid, no hidden features available to one model alone. Ridge must receive enough lag information to be a meaningful sequence comparator.  
**Advance:** the pipeline has informative diagnostics regardless of whether returns are predictable. These controls stay in all later comparisons; do not waste repeated training on them.

### A-E2 — Does shared recurrence help? **[MANDATORY]**

**Menu:** FT0 + TM0 + SP0 + FC0 + RG0 + AD0 + TG0 + CP0/CP1 + TR0. Market input absent.  
**Architecture:** stock sequence \(X_{i,t}\in\mathbb R^{48\times d}\to\mathrm{SharedLSTM}\to h_{i,t}\to\mathrm{Head}\to\hat y_{i,t}^{CS}\).  
**Test:** shared stock-only LSTM against lagged ridge and momentum. One width and seed for initial sanity; bounded second width only if under-/overfitting diagnostic motivates it.  
**Mechanism expectation:** nonlinear path dependence may make 48-hour history more useful than a compact linear lag model; not guaranteed.  
**Failure modes:** too little predictive signal; 5-stock target noise; optimization or excessive width.  
**Advance to A-E3 regardless of win:** market conditioning is a central independent hypothesis, even if the stock-only LSTM does not outperform ridge. If LSTM cannot overfit a tiny batch, repair it first.

### A-E3 — Does USA500 contain useful incremental information? **[MANDATORY MAIN TEST]**

**Menu:** MC0 versus no-market baseline; EV1 (first comparison).  
**Architecture:** \([X_{i,t};M_t]\to\mathrm{SharedLSTM}\to\hat y_{i,t}^{CS}\). Compare `A-E2` to `A-E3`, and ridge-own to ridge-market; freeze target/features/split/trades.  
**Key interpretation:** improvement in both ridge and LSTM suggests an **information-set** benefit; an LSTM-only improvement can reflect nonlinear modeling but demands capacity/seed checks. Market data that improve raw return MSE but not universe-relative ranks should not be called an alpha success.  
**Rescue:** inspect USA500 bar alignment, effective tradable timestamps, and whether the market variables actually vary in the sample. Avoid adding USATECH/options here to rescue a failed USA500 ablation.  
**Advance:** A-E4 is scientifically justified even with inconclusive A-E3 because gating may reduce estimation variance; give it a small capped screening budget.

### A-E4 — Market-guided feature weighting versus concatenation **[HIGH PRIORITY]**

**Menu:** MC1 = FT1 = RG1; MASTER inspiration; TR1; EV1.  
**Core comparison:** `A-E3` receives \([x_{i,s};m_s]\), while gating receives \([\alpha(m_t)\odot x_{i,s};m_s]\), with identical stock and market observations (the gate broadcasts the latest causally observed market state across historical steps). One form from the Menu is

\[
\alpha(m_t)=d\,\mathrm{softmax}\bigl((Wm_t+b)/\tau\bigr).
\]

**Fairness requirement:** **retain direct USA500 inputs in the gated model**; otherwise a loss of information is confounded with the presence of a gate. A nearly uniform gate can approximate the ungated input. Do not count RG1 and FT1 as separate experiments.  
**Mechanism expectation:** market-dependent channel relevance may be an effective low-capacity inductive bias, even though a sufficiently flexible concatenated LSTM can already learn conditional processing.  
**Diagnostics:** distribution/entropy/variance of gates over market regimes, collapse to near-constant or one channel, sensitivity to scaling, small synthetic example with state-dependent indicator effect.  
**Go:** credible paired validation improvement or consistent stability/capacity benefit. **Rescue:** one gate-temperature/initialization/regularization correction if collapse or an obviously malformed gate, then classify as retained, deferred, or deprioritized.

### A-E4M — Stepwise, time-varying market-guided feature gating (MC2) **[FROZEN CANDIDATE; CONDITIONAL, LOW-COST COMPARISON]**

**Menu:** **MC2** (MASTER-inspired time-varying gate) versus **MC1** and **MC0**. MC2 is deliberately different from the closest MASTER endpoint-gate adaptation; it is **not** a second instance of MC1/FT1/RG1.

**Precisely isolated hypothesis:** if the observed USA500 state changes *within* the 48-trading-observation lookback, each historical stock observation may be more usefully interpreted under its **own contemporaneously available state** than under the single forecast-endpoint state. For each historical step `s` in a sample ending at `t`, compare:

\[
\begin{aligned}
\mathrm{MC0}:&\quad [x_{i,s};m_s],\\
\mathrm{MC1}:&\quad [\alpha(m_t)\odot x_{i,s};m_s],\\
\mathrm{MC2}:&\quad [\alpha(m_s)\odot x_{i,s};m_s].
\end{aligned}
\]

Use the **same stock, USA500 histories, lookback, target TG0, parameter-budget policy, loss, trading execution and causal timestamps**. Where feasible reuse the MC1 gate family/width/initialization rather than inventing a more capable controller for MC2. Keep the direct `m_s` features in **all** market-conditioned models, so MC2 tests *processing* and not unequal information access. `m_s` must be known at historical step `s`; `m_t` in MC1 must be known by the decision time `t`. Neither gate may see future returns, regime labels defined retrospectively, or the outcome window.

**Activation rule:** MC2 is **selected for the first-pass menu**, but is not an automatic extra training run. First inspect already computed within-window changes in causal market trend/volatility state, and the MC0/MC1 results. Run **one matched MC2 pilot** only if historical state variation is meaningful or a concrete regime-transition mechanism warrants the comparison; do not expand to a 3-way grid over MC2, spatial mixing, and multiple gate sizes. If the five-stock pilot is inconclusive, record **defer / one justified rescue** rather than a negative architectural verdict.

**Diagnostics and retention:** compare paired rank IC/loss and net-cost results with MC0 and MC1; examine gate trajectories, the extent of state changes *within* each window, saturation/uniformity, sensitivity to the last market bar, and training instability. MC2 is retained only with incremental evidence or a mechanistically informative inconclusive result that warrants one targeted expansion. If no meaningful state transitions exist, classify the comparison as **not adequately tested**, not as a failure of stepwise gating.

### A-E4R — Explicit market-state dependence: *inputs versus gate* **[HIGH-PRIORITY DIAGNOSTIC; MOSTLY FREE]**

**New IDs (v2 only):** `RS0` = continuous USA500 trend/volatility inputs; `RS1` = causal bull/bear × high/low-vol *diagnostic labels*; `RS2` = **MC1** market-dependent feature gate; `RS3` = bounded interaction between observed state and a predeclared predictive signal. These `RS` labels are **roadmap shorthand, not Menu IDs**.

**Hypothesis:** the same stock momentum or relative-volume feature has different *predictive usefulness* under observed bullish/bearish and volatile/calm conditions. **Cheap first check:** slice the E3 plain market-conditioned ridge/LSTM predictions by causal RS1 state; inspect *paired* rank loss/IC and state occupancy. Then E4 directly tests RS2 (MC1) against RS0 with **both given the same continuous state observations**. A gate does not deserve credit merely for seeing state information withheld from the comparator.

**One conditional focused test:** if there is a defensible state interaction, add **one** shrinkage-controlled `state × feature` term to ridge before attempting a new neural state-conditioned path (MC2 is now a selected **conditional** first-pass comparison in A-E4M; MC3 remains deferred). If high/low volatility has no reliable distinguishing behavior or few episodes, report insufficient state coverage; do not increase state counts. **Failure rescue:** one gate initialization/temperature or state-alignment correction; not a hidden search over thresholds.



### A-E5 — Is actual peer information needed? **[HIGH PRIORITY BEFORE SPATIAL MODULES]**

**Menu:** SP0 comparator; candidate peer pooling SP4 / factor-pool FC6; Papers' MASTER/StockMixer distinction.  
**Reason:** parameter sharing does **not** let stock \(i\) observe an unprovided peer's latest innovation. First test **access**, before paying for explicit mixing.  
**Cheapest test:** add causal peer-market summaries to *both* ridge and ordinary shared LSTM (e.g., leave-one-out peer mean/dispersion/sector-aware summaries, with eligibility masks). Compare to own+USA500 using same target. A full peer-history-access ordinary model may be necessary as a stronger information-matched comparator to SP3/SP1 if those models observe information the summaries discard.  
**Critical mathematical check:** an additive common vector \(\tilde h_i=h_i+Wm\) followed by a shared linear head **cannot change pairwise ranks**, since the common shift cancels. SP4/FC6 must use **interactive fusion** or heterogeneous loadings if rank improvement is the hypothesis.  
**Five-stock limitation:** each sector is represented only once, so there is **no meaningful within-sector pool** here. This does not invalidate across-sector peer tests; it limits factor/sector conclusions.  
**Go:** peer access adds signal or plausible state-specific effects. **Defer:** no clear gain but only five names, highly correlated peers or large uncertainty; consider expansion *before* rejecting SP3/SP1.

### A-E5L — Directed lead–lag alpha using cross-sector peers **[HIGH-PRIORITY, CHEAP FIRST]**

**New roadmap labels:** `LL0` no peer lag; `LL1` engineered causal peer-lag indicators supplied to baseline models; `LL2` peer signal × observed market-state interaction; `LL3` learned peer exchange (Menu **SP3**, alternate **SP1**). `LL` IDs are **not** rows of the Menu.

**Targeted hypothesis:** a completed move/shock in stock \(j\) predicts the *later* relative 4h outcome for \(i\), beyond USA500, own lagged return and common volatility. Because five initial stocks are from different sectors, this is a **cross-sector/market residual lead–lag** experiment, not a within-sector peer test. Some apparent lead–lags will vanish after market adjustment.

**Minimum comparison:** ridge + standard LSTM, both with `LL0` vs `LL1` and otherwise identical causal inputs. Predeclare 1–2 lags and at most a handful of economic peer pairs (or a single permutation-invariant lagged peer summary) *using training-period rationale*, not validation/test Sharpe. Compute rolling lagged cross-correlation only from observations before the forecast; don't mislabel zero-lag contemporaneous correlation as evidence. Verify any selected effect is **predictive of the later label**, not merely of the same bar. Inspect sector/beta exposure and matching clocks. **Selective expansion:** if all five stocks supply too few economically comparable peers, enlarge to ~20 diverse stocks rather than concluding lead–lag mechanisms fail.

**Escalation:** promote `LL1` to SP3/SP1 only if actual peer histories add information and there is a credible representation/routing question. Keep a rich-input ordinary LSTM with the **same directed peer access** as a control—simple pooled summaries may not retain the same information as learned stock mixing.



### A-E6 — One explicit spatial-exchange comparison, not every graph **[CONDITIONAL HIGH PRIORITY]**

**Menu:** first **SP3 + CP2 + TR2**, with **SP0** control; **SP1 + CP3 + TR1** as *competing alternative*, not an automatic extra branch. EV2.  
**Default spatial model:** `LSTM -> StockMixer-style bottleneck -> per-name head` with \(H\in\mathbb R^{N\times D}\),

\[
Z=\sigma(M_1\operatorname{LayerNorm}(H)),\qquad\widetilde H=H+M_2Z.
\]

**Question:** can low-dimensional learned inter-stock exchange outperform a stockwise encoder with an adequate peer-information comparator?  
**Expected advantage:** SP3 routes common representations differently by stock; low-rank bottleneck controls flexibility.  
**Failure modes:** fixed stock ordering/identity overfit, peer information redundant with USA500, small-N estimation noise. Include a **no-training** ticker-reordering/mask check; SP3 can be ordering/identity dependent, unlike permutation-equivariant attention or properly designed pooling.  
**Alternative SP1:** run **only** if SP3 yields evidence that directed/state-dependent peer choice could matter, or its fixed-universe limitation is unacceptable; compare from the **same ungated/gated backbone** as SP3 and a similar information/compute budget. Do not compare SP3+MC1 against SP1+MC0 and attribute differences to attention.  
**Expansion trigger:** inter-stock attention or factor exchange is underpowered on five stocks, or changing-universe robustness is part of the hypothesis: expand to ~20 stocks *once*, then retest SP0 and at most **one** spatial candidate.  
**Defer:** SP2/TM2 per-step cross-stock attention, SP6 hypergraphs, learned latent factors FC5 unless simple exchange first shows evidence.

### A-E6R — State-dependent predictive lead–lag **[TARGETED COMBINATION; NOT A MANDATORY EXTRA MODEL]**

**Combined mechanism:** **MASTER MC1 / RG1** conditions stock-feature relevance; **StockMixer SP3** (or **MASTER SP1**, competing alternative) shares peer information; a small **explicit state × peer-lag coefficient** tests whether that information matters differently in bearish/bullish and high/low-vol markets. **Do not claim SP3 inherently models sign-changing directed lead–lag effects.** Its unconstrained learned mixing is a broader hypothesis; the state interaction must be tested or explicitly provided.

**Progressive controlled design, not a factorial grid:**

1. Start with best simple `LL1` lagged peer signal and `RS0` continuous market state; fit an inexpensive constant-coefficient regression versus `LL2` varying-coefficient (`peer × state`) regression on the *same* information. Examine the fitted coefficient and uncertainty over well-populated states; test zero, constant and state-varying coefficients.
2. If `LL2` has credible development evidence, compare an ordinary LSTM supplied the *same engineered interaction* with a compact **MC1 + SP3** (or SP1) model of **matched full peer access**. First isolate gate-only and mixing-only effects using already completed E4/E6 runs. At most **one** new combined model is warranted initially.
3. If a neural model suggests sign reversals, verify using **observable-coordinate** fitted predictive contrasts / restricted coefficient probes; a negative internal latent edge is not an identified economic negative coefficient. Avoid unsupported claims of causal sector rotation.

**Stop/defer:** if constant-coefficient peer models offer no stable signal and market states have poor support, do not train a state-dependent spatial controller. If a planted *state-changing* peer-predictive relationship is not recoverable by the implementation, fix the mechanism once; if real data remain noisy, label **inconclusive**, not "architecture impossible." Distinguish market-dependence from feedback-conditioned FinPFN **AD1/AD3**, which requires matured labels and is a separate later research problem.



### A-E7 — Temporal readout / auxiliary supervision **[OPTIONAL; ONE BRANCH]**

**Candidates:** **TM1** temporal attention *or* **TG2** auxiliary 1h/2h/4h prediction, separately compared to TM0/TG0; optional TM3 learned multiscale only if engineered multi-horizon features are demonstrably insufficient.  
**Question for TM1:** does attention over LSTM hidden states recover predictive times not preserved in the final state?  
**Question for TG2:** do shorter-horizon supervised heads regularize the 4h representation, or create negative transfer?  
**Gate:** attempt **one** if temporal/learning diagnostics identify its failure mode; do not combine them initially. If no targeted temporal hypothesis, **skip A-E7**. Different objective horizons change purging requirements and must never be allowed to cross a split.

### A-E8 — Factor-aware, risk-aware, or adaptation branch **[CONDITIONAL; USUALLY DEFER]**

Choose **at most one**, only after core architecture results justify it and time remains.

| Branch | Menu IDs | Required comparator & question | Why not obligatory now |
|---|---|---|---|
| Common/sector information | FC6 (overlaps SP4/SP5), FC7 known factor priors | Ordinary LSTM supplied with **identical** market/sector features; do market/sector-aware representations alter *universe* ranks? | Five names, one per sector, do not estimate sector-specific representations well |
| Auxiliary volatility | TG4 | Return-only versus same encoder with 4h realized-volatility head; evaluate return IC and *separately* risk sizing with frozen scores | Changes the supervised objective; not required for primary question |
| Adaptation to changing predictive mapping | **AD3 + TR4 + CP7** first; AD1 only after | Static LSTM head versus shrinkage-regularized rolling head on *frozen* representations; if this works, test causal recent-issued-forecast statistics AD1 | Four-hour matured-label bookkeeping, noisy feedback, extra deployment complexity |
| Discrete regimes/dynamic factor learning | RG2/FC8/FC9 | Continuous-state matched-capacity control | High complexity and weak evidence from five names |

**Feedback-causality invariant:** at decision time \(t\), a historical origin \(s\) may inform the adaptive model **only if its full executable label is observable at the decision timestamp**, not simply because it is four file rows earlier. Recent error features must come from **predictions issued at s**, not optimistic in-sample reconstructions using a later fitted model. A rolling head needs honest prequential/out-of-training fitted context where applicable.  
**Explicit omission:** do not train a full FinPFN, two-stage PRISM-VQ, VQ-MoE, FactorGCL hypergraph/contrastive system, or free architecture search in the first pass.

### A-E9 — Shortlist confirmation and reporting **[MANDATORY FOR CLAIMS]**

1. **Freeze** information set, target, candidate ranking, hyperparameter and selection protocol using *development* evidence; record how many models were tried, including rescued runs.
2. Compare **best simple model** (at least ridge and the unmodified shared LSTM) with **one or two shortlisted extensions** on the untouched final period. Carry chosen controls into every comparison.
3. Report multi-seed variation for neural finalists (suggestion: three seeds), a modest expanding/rolling walk-forward exercise if affordable, paired day-block uncertainty, conditional regime breakdowns, concentration/beta exposure and several realistic **assumed** cost levels. Costs derived only from OHLCV must be labelled assumptions; report break-even costs if possible.
4. Use a focused whole-panel day-block shift/null only if needed to support a claim and if compute permits. A fixed-hyperparameter or post-fit null is **weaker** than a null that reruns model/hyperparameter selection. Never imply an exact permutation p-value without exchangeability justification under market nonstationarity.
5. State separately: **forecast improvement**, **incremental market information**, **incremental peer information**, **architectural improvement at matched information**, and **tradeable net value**. They are different claims.
6. Present failed/deferred branches prominently with reasons. Preserve an untouched confirmatory period if earlier analyses or walk-forward results influenced further design decisions.

---

## 4. Fast path and conditional experiment matrix

| Order | Mandatory? | Experiment / Menu comparison | What changes *only* | Primary decision | Immediate skip/defer reason |
|---:|:---:|---|---|---|---|
| 0 | Yes | A-E0 data/execution contract | No model | Causal, executable sample | Never skip |
| 1 | Yes | A-E1 momentum / lagged ridge | Baseline model | Predictability reference | Never skip |
| 2 | Yes | A-E2 TM0/SP0/FT0/TG0 | Shared recurrence | Does recurrence earn cost? | Never skip once pipeline works |
| 3 | Yes | A-E3 MC0 versus own-only | USA500 information | Incremental market value | Never skip; central course hypothesis |
| 4 | High | A-E4 MC1 (=FT1=RG1) versus MC0 | Market gate | Benefit beyond identical continuous USA500 input | Diagnostic/rescue once |
| 4M | **Selected, conditional** | A-E4M **MC2** vs MC1/MC0 | Historical-step gate rather than endpoint gate | Do within-window market-state changes justify stepwise weighting? | No meaningful state variation or remaining pilot budget → documented defer |
| 4R | High, cheap | A-E4R RS0/RS1; conditional RS3 | Bull/bear, high/low-vol state interpretation | Does predictive effect change with causally observed state? | Sparse regimes → descriptive only |
| 5 | High | A-E5 peer summaries in ridge/LSTM | Peer information access | Is additional information useful? | If no reliable peers, defer spatial nets |
| 5L | High, cheap | A-E5L LL0 vs LL1 | Lagged *directed* peer predictive signals | Is there alpha after own/index controls? | Low peer coverage → targeted expansion |
| 6 | Conditional | A-E6 SP3 versus SP0; optionally SP1 | Learned spatial mechanism | Benefit beyond same peer access? | Insufficient peer information or N |
| 6R | Conditional | A-E6R LL1 vs LL2; at most one MC1+SP3 combo | State-dependent peer effect | Does regime change lead–lag coefficients? | No state/peer mechanism → no combo |
| 7 | Optional | A-E7 TM1 **or** TG2 | Temporal readout or learning objective | Targeted temporal deficiency | No diagnosed need |
| 8 | Optional | A-E8 FC6/FC7 **or** TG4 **or** AD3 | One research branch | Domain-specific benefit | Weak data / high cost |
| 9 | Yes for claims | A-E9 finalists only | Stronger validation | Generalization/net robustness | Do not iteratively select on final test |

**Revised default path:** `E0 → E1 → E2 → E3 → E4/4R (shared runs + state slices) → [E4M / MC2 if within-window state variation warrants it] → E5/5L (ridge first) → [E6 if lagged peer information deserves learned exchange] → [E6R if state-dependent peer effect deserves testing] → E9`. **E6R is not mandatory**.  This is **not** an injunction to train every optional branch. If E4 fails because a gate saturates, fix the gate once; if it fails only because five names offer inadequate statistical precision, carry the hypothesis into a **predeclared 20-stock test** or label it unresolved.

---

## 5. Rules for a *single* justified enlargement or rescue

### Expansion beyond five stocks

Expand to ~20 **before** claiming the absence of benefits from inter-stock modeling when all of these hold: (i) a mechanism test shows the spatial component works when signal is planted; (ii) timing and peer data are sound; (iii) five-name results have broad paired uncertainty or structural insufficiency; and (iv) expansion is feasible within the remaining budget. Conversely, do **not** enlarge to select whichever ticker universe gives the best test Sharpe. Predefine coverage/liquidity rules and keep market periods aligned.

### Rescue classification and report wording

- **Verified defect:** “The first failure was implementation/optimization; the corrected run is a new logged experiment.”
- **Underpowered:** “Five-stock data do not resolve the difference; no negative architecture conclusion follows.”
- **No signal:** “Even rich-input baselines show no meaningful evidence of accessible predictive structure; architecture evaluation is inconclusive for mean-return alpha.”
- **Architecture not earning complexity:** “After matched-information/matched-budget diagnostics, the extension adds no established value in this sample.”
- **Mechanism rejected:** only if a defined property cannot hold or the model repeatedly fails an appropriate planted mechanism test after correcting implementation; be careful to distinguish wrong construction from universal impossibility.

Keep a ledger of planned hypothesis, model ID/hash, source menu IDs, seed, information set, dates, cost assumption, training minutes, key plots, go/no-go, and whether the run was a rescue. **Never refreeze the same protocol after peeking at the confirmation results.**

---

## 6. The two-person coordination contract

- Share **one canonical aligned hourly store**, trading calendar, USA500 feed, adjusted-price policy, feature code, masks, label-horizon/execution definitions, split boundaries, logging and cost model. **Do not duplicate large Parquet datasets** just because the tracks use distinct labels; materialize lightweight views/configurations and reuse derived columns.
- Agree on a *minimal* shared `FT0/TM0/MC0` stock-only/market-conditioned baseline, matched seed list, permitted tuning budget and core predictive/trading metric definitions; **do not force identical targets**.
- Track A: five **cross-sector** names and **TG0** universe-normalized labels; expansion adds sector-diverse names. Track B: five names **within one sector** and **TG1** sector-relative labels; expansion must include several names **per** sector. Their ranking and economic portfolios are different; compare *incremental uplift against each track's own baseline*, not direct level performance.
- Common stop/go review after A-E3/B-E3, after respective spatial experiments, and before final confirmation. At each checkpoint, pool lessons about data bugs and efficiency; do **not** cherry-pick architecture or cost settings based on the other track's final held-out results.

---

## 7. Explicit first-pass non-goals and evidence hierarchy

**State-dependent lead–lag safeguard:** the new RS/LL experiments test *observable causal prediction* first. They do **not** authorize unbounded learned signed graphs or custom-cell architectures. `MC1/FT1/RG1` count as **one** gate, and an extra interaction regression is **not** another recurrent module. Any claims of sign change require observable predictive contrasts, not latent edge signs.

**Defer by default:** SP2/TM2 full time-specific cross-stock attention; SP6/FC4–FC5 hypergraphs/unknown factors; FC8–FC9 dynamic/quantized factors; RG2–RG5 VQ/MoE; AD4–AD6 FinPFN-style attention/PFN/MoE; TM4 multi-encoder systems; fully learned portfolio allocators, individual-stock options chains and macro-release-state architecture. These are *valid later hypotheses*, not automatically poor models. Five stocks cannot adjudicate many of them well.

**If custom recurrent research is eventually revived:** the two additional project notes suggest low-rank global–local memories, restricted signed interactions, and a small varying-coefficient control *after* the Menu-based baselines. In particular, a shared additive output offset cannot alter stock rankings, while a signed hidden message is not by itself an economically interpretable coefficient. Do **not** silently substitute custom cells for the Menu's first-pass architecture ladder.

**Evidence order:** (1) input/timing correctness; (2) ability to express/optimize the intended mechanism on a *cheap controlled case* when needed; (3) paired development evidence with comparable information; (4) expanded-panel or period checks when the five-name prototype cannot test the idea; (5) locked OOS, realistic costs, and appropriately qualified inference. A published result motivates a test but **does not forecast its outcome** on five US stocks at hourly frequency.

---

## 8. Items to finalize in the next interactive design chat (not fixed here)

The next chat must make choices **one block at a time**, explain mathematical/statistical and implementation tradeoffs, recommend a default, and wait for researcher approval. Suggested decision order:

1. Exact five names, point-in-time eligibility and expansion rule; hourly vendor/bar and market alignment; target-horizon/trading execution convention.
2. TG0 robust normalization (MAD variant/floor); label availability, split boundaries, purge and untouched confirmation period.
3. FT0 features/rolling windows/missingness, causal scaling and feature timing; USA500 representation.
4. Predictive loss and portfolio mapping; metrics, costs, dependence-aware paired analysis and modest baseline tuning.
5. TM0 lookback/width/layer/dropout/optimizer/early stopping/gradient clipping, fair capacity budgets and per-stage seed count.
6. **MC1 and MC2** gate definitions: same base map, temperature, available state at endpoint **versus at each historical step**, direct-market-input retention, intra-window regime-change activation rule, diagnostics and precise rescue budget.
7. Explicit state design: USA500 trend/bull-bear and high/low-vol **causal definitions**; continuous state features vs descriptive buckets; predeclared windows/thresholds, state cell occupancy and RS2/MC1 gate comparison.
8. Lead–lag design: precise completed-bar/decision/entry timing, lags/pairs/sector or market residuals, leave-one-out choice, rolling-estimation scope, LL0/LL1/LL2 controls, state coefficient/sign constraints, and criteria for spatial escalation.
9. Peer-information summaries, SP3 bottleneck dimension or SP1 alternative, universe-ordering/eligibility masks and fair information control.
10. Conditional TM1/TG2/FC6/TG4/AD3 triggers, explicit maximum number of training runs and final evidence protocol.
11. Storage-efficient repo interface and independent track configurations; reproducibility and locked final reporting template.

**Deliverable of this roadmap:** a **frozen first-pass ordered architecture-hypothesis menu (v1.0)**: the remaining implementation/design settings are provisional and optional training is still gated by evidence. It does **not** certify profitable trading, finalize hyperparameters, or authorize training every architecture listed in the Menu.
