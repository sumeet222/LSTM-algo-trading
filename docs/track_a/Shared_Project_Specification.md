# Shared Project Specification — Two-Track Hourly Equity LSTM Research

**Version:** 1.0 (pre-design working agreement)  
**Date:** 10 October 2026  
**Audience:** Both project collaborators and their separate ChatGPT architecture-design sessions  
**Status:** Shared research contract with explicitly provisional defaults; **not** a frozen architecture, hyperparameter plan, or implementation instruction.

## 1. Project purpose and research questions

Develop and evaluate compact, shared-parameter recurrent forecasting systems for **short-horizon relative equity performance**, with controlled comparisons against simpler approaches. The central scientific question is not whether a large neural network produces a good backtest, but **which information and architectural mechanisms contribute incremental, reproducible out-of-sample predictive and post-cost trading value**.

The collaboration consists of two distinct but comparable tracks:

| | Track A — Across-sector cross-section | Track B — Within technology sector |
|---|---|---|
| Researcher | Researcher A | Researcher B |
| Initial universe | **Five liquid U.S. stocks from different sectors**, selected using predeclared coverage/liquidity criteria | **Five liquid U.S. technology stocks**, selected using comparable criteria |
| Initial history | Approximately five years of hourly data | Approximately five years of hourly data |
| Primary ranking task | Future relative performance against eligible stocks in the **whole Track A universe** | Future relative performance **within the technology stock set / sector benchmark** |
| Required market-context experiment | Course-provided **USA500** | Course-provided **USA500 and USATECH.IDX**; separately test incremental value of each |
| Main peer hypothesis | Across-sector stock-to-stock predictive information and directed lead–lag | Within-tech peer and sector information, directed lead–lag |
| Primary mechanism families | MASTER-type market gating; StockMixer-style information exchange; compact shared LSTM | Sector-aware conditioning and pooling; MASTER gating; FactorGCL-inspired sector/factor structure; compact shared LSTM |
| First meaningful expansion | More stocks across sectors, if architecture hypothesis requires it | More **technology** stocks first, if five stocks underpower within-sector tests; multi-sector transfer is a separate extension |

**Both tracks forecast equity outcomes.** USA500 and USATECH.IDX are external information series unless a separate, expressly approved experiment designates them as tradable assets. Neither index is assumed to have reliable tradable volume.

## 2. Decision-status conventions

Every design document and experiment config must identify its decisions as one of:

- **COMMON-REQUIRED:** Both collaborators must follow the same conceptual rule; changes require joint agreement.
- **PROVISIONAL DEFAULT:** Recommended starting choice, not yet frozen. The interactive design chat may change it with a documented reason; changes affecting comparison require coordination.
- **TRACK-SPECIFIC:** Each researcher can decide independently while retaining shared accounting and methodology.
- **CONDITIONAL / DEFERRED:** Investigate only if an earlier result or a mechanism-specific diagnostic justifies the extra compute.
- **UNRESOLVED:** Must be settled before implementation of the affected experiment.

A default is **not** empirical evidence, an approved final hyperparameter, or permission to tune repeatedly against the final test set.

## 3. Shared information and starting defaults

| Dimension | Status | Starting specification |
|---|---|---|
| Data frequency | COMMON-REQUIRED | Hourly **regular U.S. equity-session** bars for the stock panel; carefully align course indices. |
| History | PROVISIONAL DEFAULT | Approximately five usable years, conditional on actual feed/index overlap. Earlier proposal suggested ~July 2020–June 2025; verify coverage before freezing dates. |
| Initial sample size | COMMON-REQUIRED for prototype | Five eligible stocks per track; different compositions as specified above. |
| Horizon | **PROVISIONAL DEFAULT** | **Four *trading* hours**, i.e. four valid full trading-hour advances under a precisely agreed trading-session clock; exclude ambiguous incomplete and overnight cases at first. |
| Lookback | PROVISIONAL DEFAULT | **48 trading-hour observations**, with 24/96 considered only if a targeted memory experiment warrants them. |
| Main encoder | COMMON-REQUIRED reference architecture | Small **shared-parameter LSTM** across eligible stocks, stockwise processing before any explicitly selected peer module. |
| Initial inputs | PROVISIONAL DEFAULT | Compact, causal, predominantly scale-invariant OHLCV features; market/sector context is added in controlled ablations. |
| Market states | COMMON-REQUIRED research question; UNRESOLVED operationalization | Test whether observed bull/bear, trend, volatility or related states modify feature relevance and predictive relationships; states use *past/current available* data only. |
| Peer lead–lag | COMMON-REQUIRED research question; UNRESOLVED implementation | Test causally available, direction-specific lagged peer signals and whether their effect varies by state. |
| MC2 | COMMON-REQUIRED candidate in both menus | Explicitly include **time-varying market-guided input gating MC2** as a candidate: historical step `s` is modulated by market state available at `s`. Compare with MC0/MC1 conditionally; not automatically run all variants. |
| Feature fit/scaling | COMMON-REQUIRED | Training-only fitted preprocessing; causal rolling statistics; never use future labels/market bars. |
| Principal evaluation | COMMON-REQUIRED | Comparable predictive, ranking, and **net-of-assumed-cost** trading metrics using one declared timing/exposure protocol. |
| Strategy reference | PROVISIONAL DEFAULT | Rank forecasts; dollar-neutral top/bottom tails, initially equal weight with fixed gross exposure, trading after completed input bar. Tail proportions must be sensible for `N=5` and agreed in advance. |
| Model resources | COMMON-REQUIRED | Favor minimal credible pilot tests; prioritize low-cost information tests over training many complex networks. |

### 3.1 Crucial definition of a four-trading-hour horizon

Agree a complete **decision/label/entry/exit clock** before writing labels or backtests. In particular, a naïve `t+4` row shift is not automatically four elapsed hours, and four regular-session bars may cross a closing boundary. The initial reference should use **four complete, eligible forward trading hours within the same session** where possible; otherwise declare the exclusion and its effect on sample size. The exact feasible decision times must be checked against the real provider's hourly bar convention, opening/closing stub, daylight saving, holidays, and early closes. If there are too few valid same-session observations, the design sessions may recommend a clearly named alternative (e.g., explicit multi-session trading-hour indexing), with **joint approval** and consistent implementation.

### 3.2 Track-specific target defaults, not mandatory identical formulas

**Track A — TG0:** Let `r_i,t^(4)` be the future four-trading-hour log return. Default relative target is

\[
y^{CS}_{i,t}=\frac{r^{(4)}_{i,t}-\operatorname{median}_{j\in\mathcal U_t}r^{(4)}_{j,t}}{\operatorname{MAD}_{j\in\mathcal U_t}(r^{(4)}_{j,t})+\varepsilon}.
\]

Use a predeclared robust denominator floor, valid eligible cross-section and masking rule. With only five stocks, median/MAD may be noisy; a development-stage alternative can be proposed but should not silently replace TG0.

**Track B — TG1 / FC1:** Default within-tech return target is

\[
y^{Tech}_{i,t}=r^{(4)}_{i,t}-r^{(4)}_{Tech,t}.
\]

**UNRESOLVED:** define `r_Tech,t^(4)` consistently: (i) future return of a clearly identified USATECH.IDX series if genuinely comparable with equity sessions and construction; or (ii) a predefined eligible technology peer basket, ideally excluding the target stock where required by the scientific question. These alternatives are *different labels*, and choosing one must be documented before experimentation. USATECH.IDX serving as a **historical input** does not automatically determine the benchmark/label. Track B must preserve the distinction between *sector benchmark* and *five-stock peer pool*.

Different raw target scales mean Track A versus Track B **loss values and raw Sharpe figures are not directly exchangeable without context**. Compare common baselines, within-track increments and compatible ranking/economic evidence—not a naïve contest between unlike labels or universes.

## 4. Data provenance, chronology, and leakage prevention

**COMMON-REQUIRED safeguards:**

1. Document source, timestamp timezone, publication/completion time, OHLCV adjustment conventions, splits/corporate actions, missingness, symbol changes, exchange trading calendar, and market-index definitions. **Validate the precise identity and provenance of `USA500` and `USATECH.IDX`; do not assume an index is exchange-traded or matches equity trading hours.**
2. Use only bars and state estimates available at the stated forecast decision time. Trades occur **after** the bar that supplies the forecast inputs has completed, with an explicit fill/lag assumption.
3. Build market and sector index features from a causally aligned feed; do not forward fill across closures as though stale observations were current live market prices without declaring the semantics and masks.
4. Fit clipping thresholds, scalers, imputers, feature selection, factor exposures, regimes, graph estimates and any learned preprocessing **using permitted training information only**. Rolling transforms must be causal.
5. Use shared **calendar-time split boundaries** across the two stock panels when feasible. Purge any sample whose **future supervised target** crosses a prohibited boundary; if auxiliary tasks extend the horizon, purge for the longest target window. Historical input overlap across splits is not automatically leakage if the input is legitimately known at decision time.
6. Eligibility is point-in-time; no choosing the universe based on final-test performance or hindsight coverage. Record survivorship and delisting limitations. Do not omit a stock from the input peer panel solely because its **future** label will later be missing.
7. State/regime classifications (bull/bear, high/low volatility, etc.) must be computed from contemporaneously available inputs. Fit regime thresholds on development history only; test **continuous state and hard-bucket versions** only when the question warrants it. HMM/state-space *filtered* probabilities are causal; retrospective smoothed states are not.
8. For directed lead–lag, define ordered sender `j`, recipient `i`, lag `ℓ`, and the exact information interval of the peer signal. Evaluate whether the feature is distinct from a market/sector common shock. A relation can change a risk/covariance forecast without adding expected-return alpha.
9. For FinPFN-inspired feedback/adaptation, only a **matured** label at its actual availability time may enter a later prediction. Performance summaries should use historical **issued** out-of-sample/prequential forecasts, not retrospectively recomputed in-sample fitting errors.

## 5. Shared architectural research questions, with menu references

Use `Consolidated_Architecture_Design_Menu.md` as the **component menu**, not as a recipe to stack every module. `Modern_Quant_DL_Papers_2023_2026.md` is a literature reference, not a project-specific performance guarantee.

| Question | Shared minimum comparison | Track A emphasis | Track B emphasis |
|---|---|---|---|
| Does recurrence help? | Lagged ridge/momentum vs TM0 shared LSTM, matching causal input information | Across-sector target TG0 | Within-tech target TG1 |
| Does broad-market data help? | Stock-only vs MC0 stock + USA500 | Mandatory primary market ablation | Mandatory USA500 ablation |
| Does sector index add value? | Controlled known-series feature ablation | Optional only with a justified comparable sector-information design | **Mandatory** incremental `+USATECH.IDX` versus `+USA500` |
| Does explicit state conditioning help? | Ordinary state inputs vs MC1 static endpoint gate vs **MC2 stepwise gate** when justified | USA500 state | USA500 and USATECH state; specify whether both enter gate |
| Does peer information help? | Same peer summaries in ridge and stockwise LSTM before expensive spatial model | Cross-sector lead–lag | Tech-specific directed lead–lag and sector pooling |
| Does learned information exchange help? | SP0 vs appropriate SP3/SP4/SP5 or SP1, with matched information | Compact StockMixer-like mixing SP3 | Sector-wise nonlinear pooling SP5; selective SP1 only if needed |
| Does state modify lead–lag? | Static peer feature vs compact state-dependent coefficient/product vs selected recurrent fusion | Cross-sector and market-conditioned signs/strengths | Tech peer/sector-conditioned signs/strengths |
| Are factor models beneficial? | FC0/observed FC7 before FC6/FC8 or latent factors | Conditional | Stronger optional motivation, but **not** presumed identified |
| Does relation evolve beyond observed state? | Fixed relation vs slow/rolling adaptive coefficients using matured information | Deferred conditional research | Deferred conditional research |

**Overlap and compatibility:** `MC1 = FT1 ≈ RG1` is one gate, not three independent additions; `SP5` overlaps the sector component of `FC6`; `SP2/TM2` is a coupled spatiotemporal choice. `MC2` is *step-specific* and genuinely different from applying MC1's latest state to the entire lookback. A shared additive pooled score followed by an identical linear head cannot change pairwise rankings; spatial-fusion experiments must allow heterogeneous stock responses. Parameter sharing is not equivalent to observing other stocks' histories.

A changing contemporaneous correlation, a changing **lead–lag predictive coefficient**, and a changing **within-stock feature effect** are different hypotheses. Prefer a low-parameter **observed-state interaction** as the first test; only then test whether more involved recurrent communication is necessary.

## 6. Resource-constrained staged experiment philosophy

**COMMON-REQUIRED:** The goal is a high-information-per-compute research sequence, **not** an exhaustive architectural sweep.

**Stage 0 — One shared data/clock sanity audit (no neural training).** Hand-check a few stocks/dates and indices, bar boundaries, target maturation, split crossing, trade lag, missingness, and reproducible portfolio arithmetic. The two researchers share reusable audit logic wherever feasible.

**Stage 1 — Cheap information-value tests.** Momentum, lagged ridge (and possibly one compact MLP if an actual question warrants it); compare own-only, +USA500, Track B +USATECH, simple peer/sector summaries, and a small predeclared set of lead–lag interactions. This prevents attributing *new information* to a more complex architecture.

**Stage 2 — Compact shared LSTM reference.** Establish stock-only, market/sector-conditioned LSTM comparisons with a tiny bounded training budget. Use compatible input/label/decision times, not artificially impoverished ridge features.

**Stage 3 — Mechanism-specific tests.** Test MC1 versus MC0 and, **in both tracks**, MC2 versus MC1/MC0 **when an intra-window state-change hypothesis is plausible**. Test one spatial mechanism only after cheap peer-information evidence or a strong information-access argument. Compare state-dependent peer coefficients before adding learned dynamic communication.

**Stage 4 — Selective combinations.** Only if individual mechanisms justify it, test the relevant market gate + spatial module, or sector state + technology peer pooling. Avoid uninformative Cartesian-product sweeps. A negative result in five stocks may lead to one planned rescue or larger-universe check, not automatic deletion.

**Stage 5 — Targeted rescue/expansion.** If a literature/theory-motivated mechanism underperforms, diagnose whether it is (a) not implemented/optimized correctly, (b) unable to access needed observations, (c) data- or regime-limited, (d) poorly matched to target/horizon, (e) unnecessarily flexible, or (f) genuinely lacking incremental evidence. Permit **one or very few justified diagnostic changes**, logged as additional model-selection effort. Expand the relevant *cross-section* for Track A or the *technology peer set* for Track B only when that directly addresses the question.

**Stage 6 — Shortlist confirmation.** Reserve repeated seeds, limited walk-forward testing, suitable permutation/null tests, costs and regime breakdowns for finalists and strongest necessary baselines. Keep an untouched confirmation period out of all adaptive architecture decisions. Report negative results and material uncertainty.

### 6.1 Preliminary training-budget defaults (not frozen)

- Prototype should favor **one development seed per conceptual architecture**, optionally a second seed for a borderline decision. A screening result is *not* a significance claim.
- Use small recurrent sizes (e.g. 16/32/64 in principle) and bounded searches rather than an unrestricted architecture/hyperparameter grid; select the actual range only after inspecting data and runtime.
- One important comparison should change **one causal mechanism at a time**. Match information sets, history reach, objectives and as nearly as practical parameter/tuning budgets. Where a new mechanism adds capacity, consider a simple parameter-matched LSTM as a **targeted** comparator.
- **No fixed number of experiments is mandatory** beyond data integrity, cheap baselines, core conditioning comparisons and scientifically necessary checks. Both tracks retain the right to stop a branch when its prerequisite fails.
- Document training time, model size, fit diagnostics and why every expensive follow-up is justified.

### 6.2 How to interpret failure

Do not classify one weak five-stock run as proof of architectural impossibility. Use explicit labels:

| Label | Meaning | Sensible action |
|---|---|---|
| PROMISING | Development improvement and mechanism works plausibly | Shortlist, then verify |
| UNDERPOWERED / INCONCLUSIVE | Too few peers, few regime episodes, unstable rank/target, wide uncertainty | One targeted expansion or alternate meaningful diagnostic |
| OPTIMIZATION / IMPLEMENTATION FAILURE | Nonlearning or unstable training, saturated gates, gradients, bug | Fix issue or use a minimal toy/sanity test; do not interpret as a scientific negative result |
| INFORMATION-LIMITED | Relevant peer/index/feedback observations absent or stale | Compare access to information first |
| STRUCTURAL MISMATCH | Mechanism cannot represent relevant information or suppresses it | Test an appropriate minimal variant, then consider deprioritization |
| NO INCREMENTAL EVIDENCE | Works technically but fails versus adequate same-information baseline | Deprioritize, document, do not endlessly tune |

Published support on large daily panels **motivates** a component but does not prove it should improve a five-stock hourly U.S. sample.

## 7. Common metrics and execution accounting

**Predictive:** predeclared pointwise loss on the relevant track's target; per-decision rank IC (Spearman, noting very low granularity at `N=5`), mean IC over decision dates, time-block dispersion/ICIR where appropriate, score bucket checks only at feasible universe sizes, and regime/sector-conditioned diagnostics. Do not treat each stock-hour as independent statistical evidence.

**Trading:** same price/entry/exit conventions, gross and net returns, realized annualized risk/Sharpe with dependence-aware caveats, maximum drawdown, turnover, cost drag, long/short contributions, market/sector exposures and sensitivity to multiple plausible cost assumptions. Hourly OHLCV does not directly reveal realized spread/market impact; cost inputs are assumptions, not observed execution costs. Compare against momentum and matched-exposure random trading where feasible. With five names, top/bottom-20% translates into **one long and one short**, so diversification and uncertainty are limited; do not overinterpret that prototype Sharpe.

**Holding overlap:** Four-hour labels and hourly updates can create overlapping intended positions. Apply one common **aggregate gross-exposure cap** with staggered sleeves or another clearly declared method. Never treat overlapping forecasts as separately fully funded portfolios.

**Inference:** Use contiguous/date-block uncertainty summaries rather than naïve independent-row tests; preserve market/peer dependence in null transforms as far as defensible. Where feasible, rerun the discovery/selection pipeline within full null tests on the finalists; any post-fit or fixed-choice null is **weaker** and must be labeled accordingly. Account for model search and repeated validation peeking.

## 8. Two-person coordination and provenance

Both tracks should share **data conventions, calendars, asset/index definitions, split dates, preprocessing primitives, software/environment assumptions where practical, strategy execution conventions, and metric implementations**. They may share caches and immutable source data to limit storage duplication, but each experiment must be reproducibly distinguishable by config and results.

Researchers do **not** need identical stock universes, target functions, sector-state models, neural modules, or selected hyperparameters. This is a controlled **parallel investigation**, not a demand that unlike experiments produce a single winner.

### 8.1 Shared decisions requiring mutual sign-off before modeling

1. Historical coverage and common held-out calendar windows.
2. Exact stock-bar conventions and index alignment, especially USA500 and USATECH.IDX timestamp and value semantics.
3. Four-trading-hour label and actual decision/entry/exit clock (or jointly agreed revision).
4. Universal eligibility, corporate-action, missing-data and split-purge rules.
5. Common cost, turnover, exposure and overlapping-position accounting.
6. Shared primary metric definitions and the rule for protecting confirmation data.

### 8.2 Light collaboration protocol

- Maintain a versioned **shared decision register** with key, status (`required/default/finalized`), value, reason, date, and owners' approval.
- Give every experiment an ID including track, hypothesis, information set, architecture-menu IDs, target version, split version, config/code hash or revision, seed, and development-stage status.
- Record hypotheses *before* viewing comparisons, including the strongest simpler model, expected failure modes and decision after results.
- When changing a common rule, notify the other researcher and create a new protocol version. Identify which experiments become noncomparable or need rerunning. Do not silently overwrite frozen configs.
- Coordinate shared data creation and tests once where possible; **avoid repeated bulk dataset copies**, duplicated parquet versions, or rerunning the other track's models merely for symmetry.
- Hold short checkpoints after initial data audit, after shared baselines, before shortlist validation, and before final interpretation.

## 9. What remains for the interactive design chats

**Not finalized by this document:** exact stock symbols, feed/provider, available date overlap, stock universe selection/expansion threshold, USA500/USATECH metadata, precise intra-day decision points, benchmark construction for TG1, complete input list, lookback alternatives, state/threshold definitions, lag dictionary, peer graphs, MC2 gate parameterization, objective/loss, model widths/layers/dropout, optimizer/stopping rules, per-experiment training budget, statistical uncertainty procedures, cost assumptions and position sizing details.

The separate **Track A** and **Track B interactive design prompts** should use this document as the shared agreement and the respective track roadmap as the experimental hypothesis sequence. Work **one design block at a time**, show mathematical details, compare alternatives and evidence, recommend a parsimonious default, wait for researcher approval, record selections, flag conflicts with shared rules, and distinguish provisional defaults from fully frozen decisions. Do not turn the design prompt into a Codex implementation request prematurely.

## 10. Document hierarchy and reading package

**Authoritative working order:** (1) this jointly approved shared specification for cross-track requirements; (2) the respective track's **current revision** of the architecture-experiment roadmap for intended comparisons; (3) the finalized future track design record/protocol for implementation choices; (4) `Consolidated_Architecture_Design_Menu.md` for candidate IDs/compatibility; and (5) `Modern_Quant_DL_Papers_2023_2026.md` for literature mechanisms and qualifications.

The menu/paper notes contain **proposals rather than verified evidence for this sample**. MC2 has been subsequently agreed as a candidate in **both** tracks even if a prior roadmap version has not yet been updated to reflect it. Do not infer that a mechanism is mandatory to train merely because it appears here.

### Immediate next actions

Agree this shared specification; then update both roadmaps to reflect any final architectural additions, including MC2; then generate **two separate self-contained interactive prompts**. The collaborator needs this document, Track B roadmap, the architecture menu, the literature notes, and eventually the Track B design prompt. Track A receives the corresponding Track A roadmap/prompt.

---

**Research standard:** When an expected benefit is absent, determine whether the hypothesis was correctly tested and adequately powered before deprioritizing it. When complexity does not outperform a simpler same-information model, prefer the simpler model and record the scientific finding.
