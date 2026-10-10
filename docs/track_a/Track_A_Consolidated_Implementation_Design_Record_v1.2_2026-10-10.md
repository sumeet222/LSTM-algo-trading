# Track A — Consolidated Research-Design and Implementation Contract

**Version:** Consolidation draft v1.2, 10 October 2026 (D13-C07 baselines; G0–G9 audits; NEW post-run failure diagnosis and replay requirements)  
**Project:** Cross-sectional equity alpha with shared, market-conditioned LSTMs  
**Scope:** Track A only — five stocks across sectors; four-hour relative equity ranking  
**Status:** **Approved choices D1–D12, D13-C01, D13-C07, and newly user-requested D13 post-run diagnostic-engineering obligations transcribed; NOT a fully executable/frozen protocol.** Source/clock audits, collaborative sign-off, and conditional branch/blocker details remain open. No implementation or experiment has been run.  
**Purpose:** A self-contained decision record to carry into a future Codex implementation discussion even if conversation history is unavailable. **This document does not authorize implementation, training, new experimental branches, a data-source substitution, or confirmation-period access.**

## 0. How to read and trust this document

### 0.1 Authority and provenance

This file consolidates explicit decisions made during the Track A interactive design conversation through **D13-C01** and the **new D13-C07 approval and the additive post-run diagnosis requirement**. It has also been checked against these attached project sources:

1. `Shared_Project_Specification.md` — cross-track **common requirements and provisional defaults**; joint sign-offs still required.
2. `Track_A_Architecture_Experiment_Roadmap_First_Pass_FROZEN_v1.0.md` — **frozen first-pass architecture menu and stage dependencies**.
3. `Consolidated_Architecture_Design_Menu.md` — IDs, alternatives, descriptions; not evidence of real performance.
4. `Modern_Quant_DL_Papers_2023_2026.md` — literature motivation and cautions, not verified results for these data.
5. This conversation's explicit D1–D12 approvals, D13-C01 approval, and the user's subsequent authorization to select recommended D13-C07 baseline details and post-run failure-diagnosis capabilities. Those approve Track A implementation-level choices only, not unobserved data facts or another collaborator's agreement.

The files `Recurrent_Architecture_Research.md`, `State_Dependent_Signed_Recurrent_Interactions.md`, and `LST_Proposal.pdf` are background; **they do not add mandatory architecture families to the frozen first pass**.

**Authority rule:** A common requirement or frozen experiment menu must not be silently overridden by an implementation detail. If a conflict persists, stop the affected branch and obtain explicit approval/versioned amendment. Distinguish *a design selected* from *a source, implementation, or scientific finding verified*. References/papers are motivations, not demonstrations of profit in this project.

### 0.2 Decision-status vocabulary

- **FINALIZED:** The user explicitly approved the Track A choice in the design chat.
- **FINALIZED CONDITIONAL DESIGN:** Formula/scope approved, but activation tests are pending; the run is not automatically authorized.
- **BLOCKED:** A genuine source, clock, audit, or sign-off prerequisite has not been verified.
- **UNRESOLVED:** The record does not contain an approved numerical/operational choice. **Do not invent one**; bring it back for a decision.
- **DEFERRED:** Explicitly outside the initial first-pass workload unless an amendment/activation permits it.
- **SUPERSEDED:** An earlier approved choice was later explicitly revised (e.g. sleeve sizing from 25% to 24.75% per leg).

The aim is faithfulness. **Where the exact formula, hyperparameter, or corner-case rule was not actually agreed, it is intentionally left unfilled and listed in §21.** Do not treat a plausible default as approval.

### 0.3 Overarching scientific design

Study whether shared recurrence, USA500 market information, market-guided feature gating, or causally available peer-stock information improves **out-of-sample universe-relative four-hour equity ranking** enough to justify complexity and transaction costs. Use the **cheapest credible same-information comparator first**; one mechanism at a time; preserve a strictly untouched confirmation window. Report prediction and economics separately. Report *every* completed, failed, not-promoted, blocked, deferred, and inactive conditional branch.

**Track A** ranks across sectors. **Track B** studies a separate within-technology-stock task. Track-specific target values, training losses, and raw portfolio Sharpe ratios should not be compared as though they were a single experiment. Jointly agree shared timing, data source, costs, and evaluation conventions.

---

## 1. Master decision register and amendment history

| Block | Approved choice | State |
|---|---|---|
| D1 | Fixed initial five names, backups, formation date, chronological evaluation windows, formation and retrospective data-use rules | FINALIZED; source verification pending |
| D2 | Alpaca SIP stock source proposal, six anchored completed hourly bars, split/volume adjustments, minute execution and causal USA500 alignment | FINALIZED design; both stock and USA500 availability BLOCKED |
| D3 | Same-session 240 continuous regular trading-minute horizon, two morning origins, specified TG0 target/floor and forecast-label availability | FINALIZED Track A; shared clock sign-off BLOCKED |
| D4 | 16-channel FT0; 48 scheduled-hour independent windows; feature validity/floors/scaling and retention guards | FINALIZED design; coverage not audited |
| D5 | Session-weighted MSE, daily Rank IC and paired inference; two portfolio policies; costs, borrow, execution failures; absolute direction diagnostic only | FINALIZED; actual execution audit pending |
| D6 | One-layer width-32 TM0 LSTM, dropout 0.10, AdamW, session batches, inner early stopping/refit, 1/2/3 seeds and 40-pair limit | FINALIZED |
| D7 | Five USA500 channels; exact FT0-style transformations; MC0, MC1; conditional MC2, regime diagnostics, one conditional ridge state interaction | FINALIZED design; source BLOCKED; conditional runs inactive |
| D8 | Peer means/dispersion, preformation volume-leader directional lags, ridge-first tests, bounded expansion | FINALIZED design; source-dependent identities pending |
| D9 | Conditional SP3 low-rank mixer (K=2) plus full-peer ordinary-LSTM control; SP1 alternative only | FINALIZED CONDITIONAL DESIGN; no SP3/SP1 training activated |
| D10 | TM0/TG0 primary; at most one optional TM1 or TG2 | FINALIZED CONDITIONAL DESIGN; A-E7 inactive |
| D11 | FC0/AD0/TG0 primary; at most one optional FC7/FC6, TG4 or AD3; default defer | FINALIZED CONDITIONAL DESIGN; A-E8 inactive |
| D12 | Rank-IC-led development selection, ≤3 neural finalists, three seeds, immutable A-E9 confirmation, full economics/ledger, go/no-go | FINALIZED design; A-E9 BLOCKED until preflight |
| D13-C01 | **Causal entry eligibility is separate from future four-hour label validity; do not retrospectively delete trades** | FINALIZED |
| D13-C07 | **Minimal FT0.M1 momentum, seven-lag pooled session-weighted ridge, contextual buy-and-hold, 1,000 seeded random policies** | **NEWLY FINALIZED in present request; §17** |
| D13 audit | Readiness issues C02–C12; stage-gated G0–G9 failure tracing and go/no-go | **Audit design finalized; actual gates not run** |

**Revisions expressly approved:**

- D5e-4 initially set each sleeve to +25% long/−25% short (50% gross). **D5e-4d superseded that with +24.75%/−24.75% (49.5% gross), targeting 99% for two sleeves.** Use the later values everywhere.
- D5e-6 originally contemplated separately trained absolute-direction confirmation. User explicitly restricted it to **tiny, ex-post reporting only**, **no direction model, head, filtering or trading decision**. This restriction supersedes any earlier future-extension suggestion for the first pass.
- D13-C01 is the binding clarification of D3/D5e: future label validity can gate training/scoring, **not** contemporaneous entry decisions.

---

## 2. D1 — Universe, dates, and formation

### 2.1 Universe and chronology

**Exactly five initial stocks, canonical order:** `AAPL, JPM, JNJ, WMT, CAT`. They represent five distinct sectors. The formation date is **2020-07-01**. **Predeclared backups, sector by sector:** `MSFT, BAC, MRK, COST, HON`, used only on documented eligibility failure under the approved sequence, not chosen for favorable performance.

- Initial fitting period: **2020-07-01 through 2023-06-30**.
- Development / architecture research: **2023-07-01 through 2024-06-30**.
- WF1 development evaluation: **July–December 2023**, fit using data through June 2023.
- WF2 development evaluation: **January–June 2024**, fit using data through December 2023.
- Strictly untouched final confirmation: **2024-07-01 through 2025-06-30**.
- Final confirmation refit allowed fitting history through **2024-06-30**, with label maturation, chronological purging and inner validation applied.
- These are inclusive calendar spans; actual samples are verified exchange sessions and eligible origin times, not every calendar date.

### 2.2 Predeclared inclusion/quality thresholds

- Liquidity: **$50 million trailing 60-session average dollar volume** (formation-time assessment).
- Historical index membership: verify each original stock was a member of the specified USA500 underlying historical universe at formation, **if the course series actually supplies a defensible historical-membership notion**. Identity/member data **not yet verified**.
- Provider coverage: at least **98% overall** and **95% within each adequately represented year**. **Important:** these whole-history coverage conditions are *retrospective usability* filters, not information known on formation day.
- Universe expansion: one **conditional** approximately **20-stock, sector-balanced** expansion when the five-stock panel is structurally inadequate for peer mechanisms, backed by mechanism/timing audits and a budget/protocol amendment. No performance-searched universe. Expansion changes TG0 cross-sectional labels and requires fresh matched baselines.

**D13-C03 flag:** Formation eligibility and ex-post data completeness must be reported separately. Do not falsely claim that full-history retention was knowable on 2020-07-01. No original or backup eligibility has been audited yet.

---

## 3. D2 — Source prices, session grid, adjustment, as-of clock

### 3.1 Stock-data design

- Proposed stock provider/feed: **Alpaca SIP**. Its accessible historical coverage, entitlements and actual fields have **not been established**.
- U.S. regular session starts at **09:30 America/New_York**, using exchange trading calendar/DST, early-close and holiday checks.
- **Six scheduled completed one-hour feature bars:** 09:30–10:30, 10:30–11:30, 11:30–12:30, 12:30–13:30, 13:30–14:30, 14:30–15:30 ET.
- The **15:30–16:00 closing stub is excluded from the six-complete-hour neural input grid**. It may be included for *daily* session statistics where specified, and genuine minute-price execution at 15:33 under D3 is not the same thing as treating that stub as a complete hourly input bar.
- Stock OHLC features use **split-adjusted** OHLC; volumes adjusted inversely for split consistency. Preserve raw source observations. Daily volume includes the full session including the final stub, as specified in D4.
- Execution and P&L use genuine **raw** minute execution-price references, with corporate-action/split/share-count bookkeeping so returns and wealth do not acquire fictitious gains at splits/dividends. Exact verified cash-dividend treatment is an audit prerequisite, not an invented source convention.
- Store event-time distinctions: scheduled period end, actual source publication/`available_at`, nominal feature cutoff, issuance, execution event, label maturity. Times must be timezone-aware and as-of audited (UTC internally is acceptable; presentation in ET).

### 3.2 USA500

- **Course-provided USA500 is a required information series**, not automatically a tradable index/security, and cannot be silently replaced with SPY, an S&P 500 feed or another index.
- USA500's true identity, OHLC fields, timestamp semantics, period coverage and publication delay are **unverified**. These audits block source-dependent model experiments.
- For each scheduled historical feature endpoint, select the latest compatible completed market observation actually available by the corresponding historical cutoff. **Age from market observation period end ≤90 minutes**; do not relabel a stale bar as a fresh new market return.
- Endpoint market state must be valid; for a 48-step market history at least **46/48 complete market-state steps valid**, historical missing steps subject to D7 neutral fills and separately preserved masks.
- Do not use USA500 volume unless source identity and volume semantics are verified; no market-volume features are approved in U1–U5.
- Source-specific mismatch in hour, daily close, or published time **BLOCKS** the dependent feature formula; do not guess data semantics.

---

## 4. D3 + D13-C01 — Forecast origins, actual horizon, labels, causal eligibility

### 4.1 Trading/forecast clock

- Two eligible forecast origins **after completion of the 09:30–10:30 and 10:30–11:30 hourly stock bars**.
- Indicative first: completed 10:30; nominal processing allowance 2 minutes; first permitted entry uses the approved ceil-to-next-one-minute convention after issuance + 1-minute lag, **approximately 10:33**; scheduled exit **14:33**.
- Indicative second: completed 11:30; entry **approximately 11:33**; scheduled exit **15:33**.
- Forecast issuance no more than **5 minutes** after nominal origin; exact input information may not incorporate an index observation whose period ends after that original bar cutoff just because issuance was delayed.
- The intended holding horizon is **240 minutes of continuous eligible regular-session trading time**, without overnight crossing. Genuine one-minute **opening-price** observations at entry/exit are required for TG0 outcome measurement. No synthetic exit, no naive `t+4` stored-row shift.
- **OPEN CROSS-TRACK SIGN-OFF:** shared specification provisionally described four complete hourly advances, not continuous minute duration. This is a material distinction, especially the 15:33 stub exit. Explicit joint approval is required before presenting the clocks as shared.
- Normal full five-name usable forecast origin requirement applies; early closes and irregular sessions must be evaluated by exchange calendar and may not support 240 forward minutes.

### 4.2 TG0 target

For a valid label at forecast origin \(t\), compute genuine executable-reference log returns

\[
r_{i,t}^{4h}=\log\!\left(\frac{P_{i,t}^{exit}}{P_{i,t}^{entry}}\right), \qquad i\in\mathcal U, \quad |\mathcal U|=5.
\]

Let \(m_t=\operatorname{median}_i r_{i,t}^{4h}\) and \(a_t=\operatorname{median}_i|r_{i,t}^{4h}-m_t|\) (**unscaled MAD**). Then

\[
y_{i,t}^{TG0}=\frac{r_{i,t}^{4h}-m_t}{a_t+\epsilon_{TG0}},
\qquad
\epsilon_{TG0}=\max\left(10^{-4},\ 0.1\operatorname{median}_{t\in\mathrm{train}} a_t\right).
\]

- No TG0 target clipping, arbitrary truncation, or replacement with raw stock price.
- Floor fitted only with allowed training labels; respect D6g inner-training versus full-refit calibration.
- Preserve raw four-hour returns, centered returns, cross-sectional median/MAD and floor for diagnostics.
- The cross-sectional ranking of TG0 equals the ranking of the corresponding raw stock returns at that origin.
- For supervised training, the five relevant outcomes must be genuine and complete; label availability is after **all five scheduled exits and any source publication delay**, never at the forecast issuance.
- Purge training labels that would mature/cross a prohibited chronological boundary; allowed input histories may extend backwards into a prior period, never use future data.

### 4.3 **D13-C01 — binding separation of eligibility (approved)**

**Do not use future exit-price availability to decide whether a contemporaneous historical trade was opened.** Maintain logically distinct indicators/records:

1. **Causal forecast-issuance eligibility**: permitted FT0/market/peer histories, complete five-name input cross-section, model fitted by time, issuance/source-latency rules.
2. **Causal entry eligibility**: a prediction was issuable and paired trade can actually be admitted under contemporaneously available prices, entry conditions, portfolio risk/position rules and approved fill assumptions.
3. **Ex-post label validity**: all five genuine four-hour entry and outcome prices exist and target can be scored; **known only after the outcome**.
4. **Execution outcome**: scheduled exit completed, delayed, partially filled, or not executed; maintain actual physical holdings and exceptions.

**Forecast score population:** models compared on the *same* causally issuable origins with valid matured TG0 labels; no training on unobserved future labels. **Portfolio population:** process all causally eligible forecasts/entries without requiring the future-label flag. An entered trade with missing scheduled exit remains in physical accounting, with D5e retry/overnight policy. Scores and trade outcomes may therefore cover different counts; report each separately and do not retroactively suppress bad-exit trades. This clarifies an ambiguity of earlier D3 complete-label wording and does not relax source/entry checks.

### 4.4 Development walk-forward

- WF1: use only its pre-July-2023 permitted fit history; evaluate Jul–Dec 2023.
- WF2: use only permitted fit history through Dec 2023; evaluate Jan–Jun 2024.
- Confirmation: one locked evaluation Jul 2024–Jun 2025, fitted through Jun 2024; protected from any design, checkpoint, cost, seed or selection choices.
- Labels crossing any fitting/evaluation boundary must be purged per their actual maturation; feature rolling context across a boundary is allowed if it is from the past.

---
## 5. D4 — Stock FT0: 16 engineered features

### 5.1 Shape and general rules

Each stock/sample uses **48 exchange-calendar scheduled completed-hour slots** and **16 features**, in approved order below: \(X_{i,t}\in\mathbb R^{48\times16}\). No row-skipping to manufacture 48 observations, no overnight synthetic hourly rows, no premarket substitution, and no forward-fill of invalid stock features. Require all 48×16 input feature cells valid for all five stocks at an eligible origin. Legitimate history before July 2020 can provide warm-up context, but not scaler-fitting observations outside the authorized fit history.

The same feature calculator and fit parameters are shared where specified; data aligned to the historical step's own causal `available_at` clock. All stock-specific feature origins and scheduled positions must be retained as metadata.

**Approved 16 channels (M1–M4, V1–V3, B1–B2, Q1–Q2, T1–T5):**

| Channel | Approved content/formula convention | Source timing / thresholds |
|---|---|---|
| **M1** | Latest complete-hour \(\log(C/O)\) divided by trailing 60-hour RMS of completed-hour \(\log(C/O)\) | Hourly complete bars; 60-scale 57/60 valid and max 2 consecutive missing; denominator floor |
| **M2** | Mean of **20 previous origin-matched four-hour log returns**, divided by RMS of **60 previous origin-matched four-hour returns** | Separate origin types (10:30 or 11:30), strictly earlier structurally eligible trading sessions, all historic outcomes already matured at each historical feature step; 19/20 and 57/60 valid; max 2 consecutive missing; session-locked within same origin type |
| **M3** | \(\log(C_{d-1}/C_{d-6}) / (\sqrt{5}\,\text{daily RMS}_{63})\) | Previous completed daily sessions only, no same-day closing observation |
| **M4** | Older momentum \(\log(C_{d-21}/C_{d-126}) / (\sqrt{105}\,\text{daily RMS}_{63})\) | Previous completed daily sessions only; 105-session separated endpoints; not present-day momentum |
| **V1** | \(\log(\max(\text{hourly RMS}_{12},\epsilon_H))\) | Latest trailing 12 completed-hour \(\log(C/O)\); **12/12** valid |
| **V2** | \(\log(\max(\text{hourly RMS}_{60},\epsilon_H))\) | **57/60** valid, max 2 consecutive missing |
| **V3** | \(V1-V2\) | Common hourly RMS denominator floor |
| **B1** | \(\log(H/L)\) | Valid high/low of current completed bar, scaled robustly |
| **B2** | \((2C-H-L)/(H-L)\) close-location value | Genuine \(H=L\) -> B2=0 **and** quality metadata; invalid/implausible bars rejected; bounded [-1,1] |
| **Q1** | Same-scheduled-slot \(\log\) volume surprise relative to preceding 20 matching sessions | At least **19/20** valid; early-close matching slots allowed if complete; stock-specific positive volume pseudocount |
| **Q2** | \(\log(\text{mean daily volume last 5 full sessions}/\text{mean daily volume last 60 full sessions})\) | 5/5 and 57/60 valid, max 2 consecutive missing; full prior sessions incl. stub |
| **T1** | \(\log(\text{current completed-hour price}/\text{previous 20-day close SMA})\) | SMA on 20 preceding daily closes, ≥19/20 valid, denominator session-locked |
| **T2** | Mean sign of preceding 20 daily close-to-close returns | ≥19/20 valid, native [-1,1]; previous sessions only |
| **T3** | Qlib-style normalized MACD DIF \((\operatorname{EMA}_6-\operatorname{EMA}_{18})/\text{current close}\) | Hourly closing prices, causal update/warm-up rules below |
| **T4** | \((\operatorname{EMA}_{24}-\operatorname{EMA}_{72})/\text{current close}\) | Hourly closing prices, causal update/warm-up rules below |
| **T5** | Wilder RSI14 from successive completed hourly **closing-price changes**; \((\mathrm{RSI}_{14}-50)/50\) | Includes genuine overnight gaps between consecutive scheduled closing observations; special missing recovery and warm-up rules below; native [-1,1] |

**M2 caution:** “previous origin-matched four-hour returns” are **historical returns**, not today's target. At every 48-step historical input location, M2 may use only past trading sessions with outcomes matured by that historical location. This is a stronger timing condition than simply lagging an array computed retrospectively. Canonical scaler key for M2 is `(stock, session, forecast_origin_type)`; weight the two origin types 50/50 in the **single pooled** M2 scaler as approved.

### 5.2 Indicator detail and warm-up

- Hourly volatility: use RMS (square root of average squared valid bar returns), not automatically centered sample standard deviation; include only eligible scheduled complete hourly slots.
- Stock volume: share volumes adjusted inversely for splits. For Q1 and Q2 use a **stock-specific pseudocount equal to 1% of the training median valid positive hourly/daily volume at the appropriate frequency**, then approved log transformation; do not fit on later observations. The exact algebraic log-ratio implementation must preserve the already agreed numerator/denominator/pseudocount policy and should be unit-tested on hand cases.
- T3/T4: first valid closing price seeds each EMA, then **360 good hourly EMA updates after seeding** before using the feature; bounded gaps skip EMA updates. In a recent 72 scheduled slots require at least **69/72** valid and no more than 2 consecutive misses.
- T5: use Wilder RSI from consecutive observed completed-hour **closing-price differences**, including legitimate overnight changes between the last completed hour one day and the first completed hour next session. Seed with **14 valid consecutive price changes, then 140 further valid Wilder updates**. Missing scheduled bar: freeze RSI; on first observed recovery bar, do **not** calculate an RSI price change across that missing interval. Recent 72 scheduled slots need ≥69/72 valid with no >2 consecutive missing. Conventions at zero loss/gain are 0, 50 or 100 as appropriate. Scale to \((RSI-50)/50\).
- Raw T3/T4 denominators use the current valid closing price. No unapproved signal-line/histogram MACD channels.
- Calendar semantics for daily variables: only previously completed valid full regular sessions. No use of a current day's incomplete daily close.

### 5.3 Floors and scaling

**Approved featurewise robust scaling** on the permitted training data for:

`M1 M2 M3 M4 V1 V2 V3 B1 Q1 Q2 T1 T3 T4`.

For each selected channel \(k\), compute pooled training-only median \(\mu_k\) and **unscaled** median absolute deviation \(a_k=\mathrm{median}|x_k-\mu_k|\), then transform \((x_k-\mu_k)/a_k\). Fallback order: IQR / 1.349 if MAD degenerates; audited standard-deviation fallback if both degenerate; truly training-constant feature -> zero throughout inference and flag later novel variation. **No hard input clipping** initially. Audit hypothetical ±3, ±5, ±10 clipping effects, including loss of distinction among five-stock cross-sectional ranks/collisions; those are diagnostics, not new fitted models.

`B2 T2 T5` retain native bounded scaling; no robust scaler. All fitting keys are canonical unique feature observations, **not duplicated appearances in sliding windows**. Pretraining feature-warm-up observations may exist, but scalers must not use them if outside the approved training prefix. Train-only fifth-percentile positive volatility floors as described in D4; if unavailable, flag/block instead of silent constant insertion.

### 5.4 D4i complete-window and retention guards

- Input windows use the **last 48 scheduled complete-hour grid slots**, no skip-over-missing strategy to collect 48 valid rows. Strict stock-feature validity: every channel valid for each of 48 steps for each of five names.
- No automatic stock input imputation; missing/corrupt bars and invalid feature histories disqualify origin.
- Before fitting, audit joint eligible-origin retention: **≥90%** for train and development, **≥85%** for each walk-forward fold, forecast-origin time, and adequately supported volatility regime; no >10-percentage-point retention gap between volatility regimes; **≥100 distinct eligible trading sessions per approximately six-month fold**. Regime-supported qualification must be described and counts reported.
- A failed threshold **blocks/pushes to explicit protocol revision**, not automatic masked stock imputation, shortening lookbacks, or retrospective origin selection.
- FT0 48×16 and the new USA500 48×5 history should be stored/reconstructed canonically; architecture fairness requires the same eligible origin intersection for matched comparisons.

**NOTE on information-source feasibility:** D2 source verification remains incomplete; there are no measured retention rates yet.

---

## 6. D5a–D5d — Loss, ranking evaluation, uncertainty, promotion

### 6.1 Supervised objective

- **D5a-A:** Primary **MSE regression** on the TG0 scores; **no pairwise loss** in the initial model. A MSE + pairwise auxiliary objective is a **conditional, later approved only** change if ranking instability warrants it; not automatically run.
- **D5b-B:** Hierarchical equal weighting: average 5 stocks within each eligible origin; average 1 or 2 eligible origins within each session; average eligible sessions equally.
- **D5c-A:** Retain all extreme TG0 targets and squared errors; no Huber substitution, target/winsorized loss clipping, or automatic deletion of large-loss days. Audit top 1/5/10% session loss concentration, MAD-floor days and gradients. D6e gradient clipping is a separate optimization safeguard.

For session \(d\) with eligible origin set \(\mathcal O_d\),

\[
L_d(\theta)=\frac1{|\mathcal O_d|}\sum_{o\in\mathcal O_d}\frac15\sum_{i=1}^5 (\widehat y_{d,o,i}(\theta)-y_{d,o,i}^{TG0})^2,
\quad
L(\theta)=\frac1{|\mathcal D|}\sum_{d\in\mathcal D}L_d(\theta).
\]

### 6.2 Rank IC and descriptive ranking metrics

- Primary predictive metric **D5d-1A**: Spearman Rank IC over the five stocks at each valid origin, followed by equal-origin-per-day and equal-day aggregation (**D5d-2B**). Secondary pairwise concordance and top/bottom ranking accuracy, plus TG0 MSE.
- Partial ties receive **midranks**.
- If model predictions are constant but realized five returns are not, the **project-defined Rank IC score is 0**, flagged as mathematically undefined and separately report the mathematical **defined-only** Spearman mean and constant-prediction rate. Never silently jitter ties.
- If the entire realized five-return cross-section is constant, omit that origin from Rank IC but **not** from MSE; count and report these exclusions.
- For paired comparisons use identical valid origin/date populations. Report rank IC at each forecast-origin time as well as combined daily aggregates.

### 6.3 Inference and model promotion

- Architecture screening is descriptive; repeated-seed finalists receive paired day-block uncertainty and HAC cross-checks. Do not treat five stocks, two overlapping daily origins or different seeds as independent market trials.
- Paired difference: \(\Delta_d=IC_{B,d}-IC_{A,d}\).
- Primary **moving-block bootstrap on actual consecutive trading sessions**, block length **5**, sensitivity **10 and 20**, **10,000** resamples, **95% percentile CI**. Keep complete per-session pairs; do not independently resample tickers/origins; do not concatenate days across unsampled gaps as if contiguous.
- HAC/Newey–West **Bartlett lag 5**, lag 10 sensitivity; present WF1 and WF2 separately.
- Evidence-based promotion: primary Rank IC paired evidence together with fold/seed consistency, TG0 MSE, selection accuracy, economic net trading results and complexity. When improvement is small relative to a reliable paired standard error, use the **one-SE simplicity preference**. Classify as promoted/not promoted/inconclusive/blocked, as justified, without unsupported significance assertions.
- These intervals are **not automatically multiple-model-search-corrected**; state the limitation. Formal temporal null must repeat relevant discovery/fitting/selection if claiming search-adjusted significance; D12 makes expensive formal null conditional with additional budget approval.
- **D5d-7R:** every planned, attempted, invalid, failed, rescued, blocked, inactive and unpromoted run and all valid metrics belong in an append-only ledger and final report.

---

## 7. D5e — Portfolio policies, exposure, fills, friction and exceptions

### 7.1 What scores mean

At each eligible origin choose highest predicted TG0 as long and lowest as short. Since TG0 is universe-relative and shift-invariant, **positive TG0 does NOT imply positive absolute expected stock return**. The approved initial strategy does **not** use absolute-direction forecast or direction-confirmed abstention. Only a **small descriptive ex-post direction report** is authorized (fraction of realized longs positive, shorts negative, both, and positive pair/trading net P&L). Future returns in that report must never influence trading, training, or selection.

### 7.2 Two mandatory strategies on every baseline/model

**Policy A — unconditional fixed four-hour sleeves.** At each admissible origin, try opening a top-one long/bottom-one short virtual sleeve, with its own fixed intended 240-minute expiry. Later rankings do not explicitly terminate earlier sleeves. Physically net all sleeve exposures before computing external orders and their costs; opposite virtual sleeves can offset and later require restoring physical exposure. Do not charge trading costs on virtual quantities which never reach the external market.

**Policy B — conflict veto.** If opening the proposed top/bottom pair would require an **opposite position in any stock already held by an active accepted sleeve**, **veto the entire new pair**, not one leg; existing sleeves continue to their original expiry. Otherwise admit and net exactly as in A. Veto decisions use only current active sleeve instructions, not future ranks or realized results. This policy may reduce turnover but is not guaranteed to improve net returns. Record veto counts and untraded opportunity outcomes descriptively.

Both strategies apply from ridge/momentum through all approved neural models and use the **same execution/financing assumptions**; cost-aware Policy B is not cost-free and does not automatically get a different capital budget. Portfolio policies, fill model, risk, cost, borrow and exception handling must be **separate configurable software components**. Training/prediction data are reused across portfolio policies.

### 7.3 Sleeve allocation, net positions, admission

- **Superseding D5e-4d:** per accepted sleeve nominal **+24.75% portfolio equity long** and **−24.75% short** (49.5% gross), using equity just before *that sleeve's own entry*. Two sleeves target **99% combined nominal gross** before netting, leaving a 1% buffer below the normal cap.
- Each sleeve's quantities set using the entry reference prices; do not routinely rescale existing shares because rankings or mark-to-market values change.
- Physical shares \(Q_{i,\tau}=\sum_{a\,active}q_{i,a}\). At an event, the **external share order** is \(\Delta Q_{i,\tau}=Q_{i,\tau}^{target}-Q_{i,\tau}^{physical}\).
- **Normal admission cap:** proposed *post-execution-cost* gross physical exposure ≤**100% equity** after actual stock-wise netting. If the full proposed pair does not fit, **reject entire new sleeve**; no fractional scaling, no resizing older sleeves to make room, no routine leverage tolerance above 100% on new admission.
- At scheduled entry and exit events, mark positions and apply the approved exposure/admission checks. **Passive between-event drift above 100% is allowed** without ordinary continuous rebalancing.

With reference prices \(P_{i,\tau}\), equity \(E_\tau\), gross exposure is

\[
G_\tau=\frac{\sum_i|Q_{i,\tau}|P_{i,\tau}}{E_\tau}.
\]

If \(G_\tau>1.10\) (**strict >110%**, not equality), emergency mode triggers. **D5e-4f-A:** prohibit new entries for rest of session, target **all physical positions to zero**, issue liquidation at the next genuinely permissible execution opportunity, charge actual costs, terminate virtual sleeves after *completed* liquidation. Pending unfilled liquidations and actual holdings continue in the ledger; do not mark them flat fictitiously. Emergency intervention can shorten realized holding period and P&L; original four-hour forecast label remains separate. At next eligible session resume only after unresolved positions and normal eligibility are cleared. The exact causally available risk-monitoring observation schedule is source/implementation-audit dependent; no intra-minute fill can be asserted from one-minute bars.

### 7.4 Execution-cost assumptions — D5e-3

- Combined *per external executed notional*, covering commissions/half-spread/slippage **once**: **0 bps gross diagnostic, 2 bps low, 5 bps PRIMARY, 10 bps stress**, on both buys and sells and entry/exit/emergency orders.
- Cost for event \(\tau\): \(TC_\tau(c)=\frac c{10000}\sum_i P_{i,\tau}^{ref}|\Delta Q_{i,\tau}^{executed}|\), with \(c\) in bps.
- Reference execution price is the validated **one-minute bar open** under D3. Do not both shift the price for bid/ask/slippage and deduct the same combined bps again.
- Actual size/cost change alters future equity, gross-cap admission and possible trade paths. **Replay** the strategy per policy and cost scenario; cannot assume a fixed list of trades when doing sensitivity.
- Fixed bps are **assumed**, not historical observed fills or calibrated market impact. Break-even-cost analysis is useful only where well-defined; may require repeat simulation and may be nonmonotonic if admission paths differ.

### 7.5 Short borrowing and financing — D5e-5a/b

- **Five prototype names assumed borrowable / easy-to-borrow** in the initial simulation; this is *not* historical borrow verification. Reaudit any 20-stock expansion.
- Annualized fee **0% primary**, **0.5% and 3% sensitivity**, independent of execution bps. Use per-day convention based on maximum **observed physical net short notional** during that session:

\[
N_{i,d}^{short}=\max_{\tau\in d}\big(\max(-Q_{i,\tau},0)P_{i,\tau}\big),\qquad
BorrowCost_d(b)=\frac b{360}\sum_i N_{i,d}^{short}.
\]

- Do not double charge virtual short sleeves offset by simultaneous physical long positions; if physical short was present earlier, the day's maximum convention may still incur a charge.
- Assume **zero interest credit** on short-sale proceeds. Ordinary intraday flat/no end-of-day debit is not assigned separate overnight debit interest. Unintended overnight exposures require real/documented treatment; if necessary finance/valuation cannot be supported, flag the affected P&L path as incomplete or assumption-dependent. **Exact overnight exception financing treatment has not been calibrated from verified broker history.**

### 7.6 Causal failed fills and overnight exceptions — D5e-5c/d/e

- Attempt paired new entries only when both legs meet the contemporaneous approved execution conditions. If one leg has actually filled and its partner cannot, **record the real simulated partial exposure and causally flatten it**; do not erase the event retrospectively.
- Missing scheduled exit: leave the unfilled position in physical holdings. Suspend new sleeve entries while required exits unresolved, but continue other required liquidations and risk checks.
- **Retry at each next permissible one-minute regular-session execution opportunity** until genuinely simulated fill. A retry without fill incurs no bps cost; charge on filled external notional only.
- Distinguish confirmed halt, missing vendor data, valid no-price interval, outstanding order and completed fill. Missing vendor bar is **not proof the exchange could not fill**; flag uncertain execution paths honestly.
- If regular session ends unfilled, carry the actual exposure and resume attempts at the **next permissible regular-session minute**, with new entries suspended. Do not treat the overnight event as an approved strategy signal.
- At dataset end with no valid liquidation/valuation, report **incomplete portfolio path**, not fictitious realized terminal return. Report true holding time, intended/actual exits, cost, P&L, retries and exceptions.
- One-minute price executions are **backtest proxies**, not confirmation that real orders would have filled; no live broker execution engine is required for the course/CV project.

### 7.7 Outputs required for every model and both policies

Full-calendar equity, gross/net daily and cumulative P&L, costs separated by execution/borrow/other financing, net Sharpe with dependence caveat, annualized return where meaningful, drawdown, turnover, external orders, trade counts, actual position durations/early exits, stock/sector/market exposure where computable, skipped conflicts, cap rejections, emergency stops, outages, no-trade days, capacity distribution, break-even trading cost if meaningful. Report cost scenarios and financing sensitivities **even if a model is unpromoted**. Preserve the matched risk/opportunity settings for randomized trading and contextual buy-and-hold/cash baselines under D12.

---
## 8. D6 — Frozen shared-LSTM architecture and training

### 8.1 Model, input, output

**TM0/SP0 stock-only A-E2:** single standard PyTorch-style LSTM layer, input dimension 16, hidden width **32**, independent fixed 48-step sequences with \(h_0=c_0=0\) each sample, and one **shared scalar linear prediction head**. No persistent state across windows, stocks, minibatches, evaluation periods or folds; no ticker-specific head. Training uses 10% dropout **explicitly on the final hidden state immediately before the head**, not `nn.LSTM(dropout=0.1)` (built-in inter-layer dropout is ineffective for a one-layer LSTM). Dropout off for inference and validation.

\[
\widehat y_{i,t}=w^\top\operatorname{Dropout}_{0.10}(h_{i,t,48})+b,
\qquad h_{i,t,0}=c_{i,t,0}=0.
\]

For one PyTorch LSTM with input \(d\), hidden width 32, two bias vectors per gate plus scalar head: \(4(32)(d+32+2)+33\). **Stock-only d=16 → 6,433 parameters**. No 2-layer/wide-grid search; one targeted capacity rescue only under shared rescue rules.

### 8.2 D6d optimizer / D6e gradient control

- **AdamW**, \(\eta=0.001\) constant (no scheduler, warmup or automatic ReduceLROnPlateau), \(\beta_1=0.9\), \(\beta_2=0.999\), \(\epsilon=10^{-8}\), `amsgrad: false`.
- **Weight decay 0.01** for LSTM/recurrent/input/head (and applicable gate/mixer) **weight matrices**; **0** for biases and any normalization parameters. Ensure nonoverlapping groups covering all trainable parameters exactly once.
- No initial input or recurrent dropout. Only 10% final representation dropout.
- **Global L2 gradient-norm cap 1.0** across *all trainable parameters including zero-decay biases*. Once per complete effective optimizer batch, **after backward and optional gradient accumulation / AMP unscale, before AdamW step**. Preserve direction by one common scale; nonfinite gradients cause explicit failure (`error_if_nonfinite` concept), never silently zero.
- Record preclip norm median, quantiles 90/95/99, max, fraction clipped, scale multipliers, nonfinite events. >50% sustained clipping is a **diagnostic warning**, not permission to retune threshold.
- One **conditional** lower-learning-rate rescue \(3\times10^{-4}\) predeclared for documented genuine optimization instability after data/code checks; it consumes rescue budget and is **not automatically run**. Negative net P&L or weak Rank IC alone cannot trigger it.

### 8.3 D6f minibatching — complete session unit

- **16 exchange trading sessions per target minibatch**; shuffle *complete eligible sessions* once per epoch using a deterministic seed, without replacement, each session exactly once; balance final batch sizes if necessary, **drop_last=false**.
- Each session contains **1 or 2 eligible origins**, each origin all five stocks, each stock a 48×16 (or architecture-specific input) sequence. Under two fully eligible origins a 16-session batch has 16×2×5=160 stock sequences.
- Do not shuffle historical steps inside an input window or randomly cut apart the five-stock cross-section for interaction modules. For standard shared stockwise LSTM, flatten stock sequences only as computation, then restore hierarchy for weighting.
- Per-batch loss average *session losses* (see §6.1), not an unweighted average over stock rows or origins. An eligible one-origin session and two-origin session have equal total weight. Full-epoch loss and evaluation metric must be recomputed as exact session-weighted aggregates regardless of batch sizes.
- Validation and testing chronological, no random sampling. Use a stable canonical ticker order. Train-session shuffling is confined within fit history and does not imply random train/test splitting.
- Reuse one feature/target store and lightweight sampled window indices; no materialized duplicated 48-step datasets for each seed.

### 8.4 D6g early stopping and two-pass full-history refit

**Approved fixed numerical rules:**

| Component | Value |
|---|---|
| Maximum calibration epochs | **60** |
| Earliest epoch to **stop** | **12** completed epochs |
| Patience | **10** successive nonqualifying epochs |
| Monitor | Inner-validation **session-weighted TG0 MSE** (dropout disabled) |
| Improvement threshold | Strictly **>0.1% relative** improvement (new MSE <0.999 × prior qualifying best) |
| Validate | Every completed epoch |
| Checkpoint selection | Best **qualifying** validation-MSE checkpoint; earliest epoch tie break; record absolute raw minimum separately |
| Inner validation | Chronological **last 63 exchange sessions** of permitted fitting period, not an outer evaluation fold |
| Inner validation adequacy | At least **50 eligible distinct sessions**, at least **25 valid observations at each forecast-origin time**; if not, BLOCK rather than shift after peeking |
| Preprocessing | Fit on the inner-training prefix for stopping pass; purge labels crossing its boundary |
| Refit | Fresh initialization and optimizer, refit preprocessing on all permitted fitting history, train **exactly selected epoch count**; no further stopping |
| Final refit checkpoint | Last epoch of locked refit duration |
| Selection prohibition | Never choose checkpoint via outer Rank IC, Sharpe, net P&L or confirmation results |

**Two passes per independently fitted seed/cutoff**: (1) calibration fit on earlier fitting prefix with a 63-session inner validation tail, obtain selected epoch \(e^*\); (2) new model from scratch, fit on all permitted history for exactly \(e^*\) epochs. Refitting on more sessions per epoch may entail more gradient updates; report actual optimizer step counts, calibration vs refit run times, best and stopping epochs, raw/qualifying minima, loss trajectories. A calibration checkpoint is retained for audit; the refit checkpoint is used for outer forecasts.

At a chronological cutoff, last 63 *calendar exchange sessions* determine validation membership; do not retrospectively choose the 63 best available sessions. Data eligibility and label-maturity/purge rules remain binding. If calibration is invalid, do not present a refit as valid. A no-improvement-at-epoch-60 case is flagged, not silently extended.

### 8.5 D6h seeds, experiment-resource ceiling and reproducibility

- Initial neural architecture screening: **seed 42**.
- Conditional extra borderline follow-up: **seed 123** (at most one additional seed under documented evidence).
- Shortlisted finalist families (up to **three**) use **42, 123, 2026**, all reported, no best-seed cherry-picking. Match comparator seed IDs wherever sensible; random IDs do not guarantee the same initial tensors for different architectures.
- Each mechanism at most **one primary justified full-training rescue**; cheap diagnostics may supplement without becoming a hyperparameter search. Fix verified bugs and preserve the invalid attempt in ledger.
- **Global cap 40 two-pass calibration/refit training pairs** (at most 80 individual fit passes); include expensive failed attempts. Reused identical fitting checkpoint is not counted again. An additional **preliminary 24 cumulative neural-fitting wall-clock hours** envelope, subject to actual machine benchmark and explicit human revision; do not assert it has already been met or is feasible.
- Count unique architecture, fitted information, seed, fitting cutoff, config/code/data version; avoid per-policy/per-cost retraining.
- Record Python/NumPy/PyTorch seeds, canonical session permutations, framework/hardware/library versions, deterministic operations where practical, remaining nondeterminism, config/data/code/checkpoint hashes, full seed-level metrics and runtime. Bitwise equality across unlike hardware is not promised.
- Failed/blocked/inconclusive runs count and remain documented. Never spend remaining ceiling automatically on every conditional branch; mandatory baselines/finalist evidence have priority.

---

## 9. D7 — USA500 market-state representation and market-guided gates

### 9.1 D7a — Five continuous market channels

**Approved**, subject to verified true USA500 semantics, U1–U5. With \(M_t\in\mathbb R^{48\times5}\):

| ID | Market variable | Basis |
|---|---|---|
| U1 | Latest completed-hour \(\log(C^M/O^M)\) divided by 60-hour market RMS | Market directional move versus recent hourly scale |
| U2 | Log of floored **absolute** 60-hour market RMS | Preserves absolute market-volatility level, not rescaled away |
| U3 | Log ratio of floored 12-hour to floored 60-hour RMS | Volatility expansion/contraction |
| U4 | Previous-session-locked 5-session market momentum normalized by \(\sqrt5\) × daily RMS63 | Short trend/rebound |
| U5 | Previous-session-locked 20-session market trend normalized by \(\sqrt{20}\) × daily RMS63 | Medium-term trend |

No USA500 volume, raw index-level neural feature, learned regime classifier, index RSI/MACD, market transformer, or USATECH substitute is authorized.

### 9.2 D7b — Exact formulas, floors, completeness, scaling

Assuming verified compatible complete-hour OHLC fields, define \(R_s^M=\log(C_s^M/O_s^M)\). For \(k\in\{12,60\}\), \(\sigma_{k,s}^M=\sqrt{\sum_{j\in V_{k,s}}(R_j^M)^2/|V_{k,s}|}\) on valid scheduled hourly returns. Then

\[
U1_s=\frac{R_s^M}{\max(\sigma_{60,s}^M,\epsilon_H^M)},\quad
U2_s=\log\max(\sigma_{60,s}^M,\epsilon_H^M),\quad
U3_s=\log\frac{\max(\sigma_{12,s}^M,\epsilon_H^M)}{\max(\sigma_{60,s}^M,\epsilon_H^M)}.
\]

If \(C_d^M\) is the verified closing value of a completed market trading session, \(r_d^{M,D}=\log(C_d^M/C_{d-1}^M)\), and \(\sigma_{63,d}^{M,D}\) is its valid rolling 63-session daily RMS, then for historical step in session \(d\):

\[
U4_s=\frac{\log(C_{d-1}^M/C_{d-6}^M)}{\sqrt5\max(\sigma_{63,d-1}^{M,D},\epsilon_D^M)},\quad
U5_s=\frac{\log(C_{d-1}^M/C_{d-21}^M)}{\sqrt{20}\max(\sigma_{63,d-1}^{M,D},\epsilon_D^M)}.
\]

- Hourly RMS12 **12/12 valid**, RMS60 **≥57/60** valid and max 2 consecutive missing; daily RMS63 **≥60/63** valid, max 2 consecutive missing. U4/U5 daily-return chains and endpoints genuinely complete (5 and 20 sessions), no interpolated closes.
- Positive hourly denominator floor \(\epsilon_H^M\): training-only **5th percentile** of pooled positive valid market RMS12 and RMS60. Daily floor \(\epsilon_D^M\): training-only 5th percentile of positive RMS63 daily values. Zero insufficient-scale cases flagged/blocked.
- Fit U1–U5 separately with **training-only median/unscaled MAD**, then IQR/1.349, then audited SD fallback; training-constant channel -> zero and flag novel later variation. Count each *unique actual market timestamp once*, not five stock copies or repeated overlapping-window appearances. **No hard clipping.** Report extreme-tail and hypothetical clipping diagnostics only.
- U4/U5 are **locked across intraday steps of their session** and use the most recently already completed preceding session. Each historical step recomputed using **its own** as-of history, not the final forecast's market state copied backwards. U1–U3 update only at valid completed market observations; stale observations may not be represented as fresh returns.
- Market time alignment and <=90-minute age as in §3; original source observational semantics remain to be audited.
- Required 48-step market-vector validity: **endpoint valid and ≥46/48 historical valid complete U1–U5 market vectors**. Missing historical standardized U-components neutrally fill **0**; store validity masks separately. No unapproved learned mask channels; **21 numerical channels** in MC0, even though masks are used for quality/audit and MC2 fallback.
- Match market-conditioned and stock-only model evaluation origins on their **intersection**, report coverage separately. Require D4 retention and regime-imbalance checks; do not quietly change feature windows if they fail.

### 9.3 D7c — MC0 and endpoint MC1

**MC0:** concatenate 16 stock features and 5 market features at each of 48 historical steps; shared LSTM input \(d=21\), total **7,073 parameters** with scalar head and D6 width 32.

**MC1:** at forecast endpoint \(t\), with standardized market vector \(m_t\in\mathbb R^5\),

\[
\alpha(m_t)=16\,\operatorname{softmax}(Wm_t+b),\quad W\in\mathbb R^{16\times5},\ b\in\mathbb R^{16},\quad\tau=1.
\]

Apply common stock-feature weights across all five stocks and all 48 historical stock steps:

\[
\widetilde x_{i,s}=\alpha(m_t)\odot x_{i,s},\qquad z_{i,s}=[\widetilde x_{i,s};m_s]\in\mathbb R^{21}.
\]

- Initialize gate **W=b=0**, producing **identity \(\alpha=\mathbf1_{16}\)**; direct 5-channel USA500 historical inputs remain present unchanged.
- Gate adds **96 trainable parameters**, total **7,169**. The softmax weights are strictly positive, sum 16, can both amplify and suppress, but should not be treated as causally identified feature importances.
- AdamW decay 0.01 on W, 0 on bias; no gate-specific dropout, sparsity/entropy penalty or temperature search.
- Synthetic identity-equivalence test: with equal encoder/head parameters and dropout off, initial MC1 outputs equal MC0; verify gate gradients and entropy/variance/saturation. Compare MC1 against MC0 on same information, origins, D6 protocol and seeds.

### 9.4 D7d — Conditional historical-step MC2

**Approved architecture, not automatic run.** Same 5→16 scaled-softmax map as MC1, total **7,169 parameters**, but per historical step:

\[
\widetilde x_{i,s}=\alpha(m_s)\odot x_{i,s},\qquad z_{i,s}=[\widetilde x_{i,s};m_s].
\]

At a historically permitted but invalid market step, fill standardized \(m_s=\mathbf0\) and force **identity \(\alpha_s=\mathbf1_{16}\)**; do not treat the neutral fill as an observed market regime. Endpoint valid. Note: MC1 uses a valid endpoint-derived gate even on historical stock steps with missing market observation; this differs by construction and must be disclosed.

**Predeclared activation diagnostic on training history only:** for valid historical market states, define \(\delta_{s,t}=\max_{k\in\{U2,U3,U4,U5\}}|m_{s,k}-m_{t,k}|\). Define \(A_t=\text{fraction of valid historical steps with }\delta_{s,t}\ge1\). A window shows meaningful state change when \(A_t\ge0.25\). A single MC2 initial pilot **may be activated** if ≥20% of otherwise eligible training windows meet that condition, those windows occur across ≥20 distinct sessions, source/time audits pass, relevant MC0/MC1 diagnostics are sound and sufficient compute budget remains. U1 intentionally excluded from this activation rule. Initial pilot seed 42; further seeds only D6h promotion. Failure to activate => `INACTIVE_CONDITIONAL`, not failed mechanism. Do not threshold-search using development Sharpe.

### 9.5 D7e — Causal market-state reporting and one conditional RS3 control

- Market state used as neural input is continuous U1–U5; no categorical bull/bear labels drive trading or the predictive model.
- **Trend diagnostic:** U5>0 bullish trailing trend, U5<0 bearish, U5=0 neutral.
- **Volatility diagnostic:** compare valid U2 to **training-only median** U2; higher is high-volatility, at or below is low. Do not fit threshold on the evaluation period.
- Primary descriptive comparisons are one-dimensional trend and volatility slices; four joint bullish/bearish × high/low cells only with data support. Require **≥30 distinct sessions AND ≥3 contiguous episodes** per interpretable state, else `SPARSE — EXPLORATORY ONLY`; still report counts/results without strong inferences. For episode session-level state use first eligible origin as anchor; preserve actual per-origin states and within-day changes.
- Report paired MC1−MC0 Rank IC differences, MSE, top/bottom accuracy, gate behavior, net portfolio and cost metrics by supported states, including occupancy and episodes. No cherry-picked thresholds or new regime-specific LSTMs.
- **RS3 conditional cheap ridge interaction only:** standardized stock M3 × standardized market U2, one predeclared term added to matched-information ridge, existing ridge penalty protocol. Activate only upon documented state-dependent evidence/coverage; development-driven activation is exploratory/model-selected. No broad term/threshold search.

---
## 10. D8 — Peer information, simple summaries, directed lead–lag

### 10.1 Fixed peers and signal

Initial peer universe remains the same five names in canonical order. For target stock \(i\), all four other names are peers \(\mathcal P_i=\mathcal U\setminus\{i\}\); no in-universe same-sector pool is possible with one name per sector. Strict five-stock valid-origin rule; no dynamic ticker substitutions. Use canonical **already FT0-normalized and robust-scaled M1** as peer completed-hour movement \(z_{j,s}\). Do not create a separate M1 scaler or hard clipping, and do not use future outcome-window prices.

### 10.2 A-E5 — Two leave-one-out peer summaries

For target \(i\), historic step \(s\),

\[
P^{mean}_{i,s}=\frac14\sum_{j\ne i}z_{j,s},\quad
P^{disp}_{i,s}=\sqrt{\frac14\sum_{j\ne i}(z_{j,s}-P^{mean}_{i,s})^2}.
\]

Use **population divisor 4**. Add two channels to MC0 per stock-step; **LSTM input 48×23**, width32, **7,329 parameters**. Compare **ridge MC0 vs ridge + summaries** and **ordinary MC0 shared LSTM vs same ordinary LSTM + summaries**; preserve the same source information, labels, dates and D6. The added peer information is not evidence of directed transmission by itself. A shared linear leave-one-out mean can algebraically decompose into a common (ranking-canceling) sum minus the target's own return.

### 10.3 A-E5L — Preformation-directed pair and lags

**Approved economic pair-selection rule, ticker identities NOT yet known**: among initial five, rank by **formation-time previous 60-session average daily dollar volume**, strictly known before 2020-07-01; let \(H\) highest and \(L\) lowest. Study **H→L** and **L→H reverse control**, both predeclared, without choosing whichever later performs better.

- Source-stock lags **\(\ell=0,1\)** over prior scheduled *completed trading-hour observations*: lag 0 most recently completed permissible return, lag 1 the immediately preceding scheduled completed return. Neither is a future 4h target return.
- The first forecast origin's lag1 may cross the preceding session; the second typically references the first completed same-day hour. **Do not call lag1 a uniform 60 elapsed-minute lag**; separately report elapsed age/origin and overnight-boundary cases. Do not promote the 15:30 closing stub into a full-hour peer step.
- Directed signals (four channels): \(D^{H\to L}_{i,s,\ell}=\mathbf1\{i=L\}z_{H,s-\ell}\), \(D^{L\to H}_{i,s,\ell}=\mathbf1\{i=H\}z_{L,s-\ell}\) for \(\ell=0,1\).
- Add one lagged leave-one-out mean \(P^{mean}_{i,s-1}\), total **five extra LL1 signal channels**.
- Include **two fixed H and L target-identity flags**, identically in both LL0 and LL1 controls (not learned ticker embeddings). Thus LL0 LSTM uses **25 channels / 7,585 parameters**, LL1 uses **30 channels / 8,225 parameters**.
- Pair selection blocked if reliable preformation dollar-volume ranking absent. No dynamic reselecting after development results.
- LL0-R versus LL1-R **ridge first**, same ridge hyperparameter fitting protocol and information except LL1 signal addition. If credible incremental relationship, a documented nonlinear concern, matched inputs, coverage and budget permit: one **conditional** LL0-L vs LL1-L shared-LSTM pilot at seed 42, further seed replication only via D6h rules.
- No coefficient-sign constraints. Association is **predictive** hypothesis, not causally identified price transmission. Condition on target own features and USA500; report raw-return association separately because TG0 includes peer-dependent cross-sectional median and MAD.

### 10.4 D8f information controls and cheap diagnostics

- Correlation between same-time stock returns is **not** lead–lag. Required focus is incremental held-out predictive usefulness of earlier peer movements beyond own stock and market inputs.
- When hourly market/stock observations genuinely align, an optional market-beta residual diagnostic may use \(\xi_{j,s}=r_{j,s}-\widehat\beta_{j,s^-}r_s^M\) with beta estimated causally, **diagnostic only**, not a primary new feature or mandatory fit. Skip/flag if series incompatible.
- One **negative-information timing-destruction diagnostic**: replace predeclared peer signal with that stock's signal **10 preceding eligible trading sessions**, same scheduled slot, where available. Preserve controls/date population. **Not** a formal permutation p-value or search-adjusted test; input shifts can change distributions. Formal null needs properly redesigned and rerun fitting/selection.
- Record lag ages, direction asymmetry, source timestamps, predicted raw-vs-relative outcomes, origin-specific results and cost/turnover consequences.

### 10.5 Conditional LL2 and universe expansion

- State-dependent LL2 is a later **A-E6R** conditional ridge-first interaction using the **standardized U2 market-volatility** variable and the predeclared H→L peer signal:

\[
\widehat y_{L,t}=f_0(X_{L,t},M_t,P_{L,t})+(\beta_0+\beta_1U2_t)z_{H,t}.
\]

- Do **not** impose forced coefficient sign or sign reversal. Activate only on credible, documented LL1/state evidence and adequate market episodes; compare same-information constant coefficient control. No automatic MC1+SP3 stacked model from a favorable coefficient.
- One conditional approximately **20 sector-balanced stock expansion** only after synthetic mechanism and source timing tests pass and small-panel results are structurally inadequate / wide-uncertainty. Rebuild TG0 and matched baselines for expanded universe; do not silently compare five- and twenty-stock labels as identical.

---

## 11. D9 — Conditional learned spatial representation exchange

### 11.1 SP3 preferred first; only if activated

Initial SP3 is built on **MC0** (stock + same USA500 history), **not automatically combined with MC1**. Encode five stocks independently using shared one-layer width-32 LSTM to final hidden matrix \(H_t\in\mathbb R^{5\times32}\). With bottleneck rank **K=2**:

\[
M_1\in\mathbb R^{2\times5},\ M_2\in\mathbb R^{5\times2},\qquad
\widetilde H_t=H_t+M_2\operatorname{GELU}(M_1\operatorname{LN}(H_t)).
\]

- LayerNorm applied across **32 hidden coordinates within each stock**, `elementwise_affine=false`, fixed framework epsilon; no learned normalization parameters.
- Bias-free mixing matrices: **20 extra trainable matrix parameters**, SP3 total **7,093** from MC0 7,073.
- M1 seeded standard small-matrix initialization; **M2=0 initially** -> exact identity representation. At first step M1 gradient can be zero until M2 changes; verify eventual gradient flow.
- Residual, GELU, shared scalar head, no learned ticker embeddings, no special mixer dropout, entropy/sparsity penalty or K grid. D6 protocol remains.
- Model can have stock-specific score shifts; however, learned stock-axis weights are **identity/order dependent**, not necessarily economically identifiable stock-to-stock causal coefficients.

### 11.2 Full-peer same-information ordinary LSTM (mandatory for strong claim)

An ordinary shared LSTM for target stock \(i\) sees target's own 16 FT0 channels, five market channels, and **all four peers' 16-channel historical FT0 sequences** in deterministic excluding-target canonical order:

\[
z_{i,s}^{fullpeer}=[x_{i,s};m_s;x_{j_1,s};x_{j_2,s};x_{j_3,s};x_{j_4,s}]\in\mathbb R^{85}.
\]

Length 48, width 32, scalar shared head: **15,265 parameters**. This controls peer-information access, **not exact parameter count**. Compare it to SP3, MC0 and E5. If a claimed SP3 advantage relies only on a weaker peer-summary comparator, do **not** claim the learned mixer itself established an incremental advantage over full peer access. A narrow parameter-matched control is optional **only** if justified, approved and budgeted.

**D13-C06:** Replicating TM0, MC0, full-peer LSTM and SP3 constitutes four distinct neural families, exceeding D6h/D12 default maximum of three. The necessary full-peer control must not vanish. Resolve by explicit scope/resource amendment **before confirmation** or narrow the architectural claim; no silent fourth family.

### 11.3 Identity and expansion

- Fixed ticker axis in this exact order: **AAPL, JPM, JNJ, WMT, CAT**. Complete panel only, no zero-embedding replacement for a missing stock; no dynamic row resorting by volume/volatility.
- With a permutation matrix \(P\), an equivalent coordinate reparameterization is \(H'=PH, M_1'=M_1P^\top, M_2'=PM_2\), and should imply \(\widetilde H'=P\widetilde H\). This is **not** invariance when only the inputs are reordered without changing parameters.
- A 20-stock model requires new \(M_1,M_2\) dimensions and a new relative target/controls; cannot reuse the fitted five-stock model as though composition were unchanged.

### 11.4 SP1 alternative (not automatically trained)

One head of input-dependent cross-stock attention, dimensions **16**, non-affine LayerNorm, bias-free \(W_Q,W_K,W_V\in\mathbb R^{32\times16}\), \(W_O\in\mathbb R^{16\times32}\):

\[
Q=\mathrm{LN}(H)W_Q,\ K=\mathrm{LN}(H)W_K,\ V=\mathrm{LN}(H)W_V,\quad
A=\mathrm{rowSoftmax}(QK^\top/\sqrt{16}),\quad
\widetilde H=H+AVW_O.
\]

- Additional **2,048** attention parameters, SP1 total **9,121**; initialize \(W_O=0\) residual identity; no projection biases/additional dropout, verify gradient flow.
- **Conditional alternative only**: activate upon separately recorded need for input-dependent peer relationships, SP3 mechanism limitation, or justified changing-universe/equivariance question. Poor SP3 net Sharpe alone does not authorize SP1. Initial pilot seed 42. Attention weights are not causal explanation.

### 11.5 Activation, mechanism tests, evaluation

SP3 A-E6 pilot requires completed/credible D8 peer-information evidence **or a strong documented information-access argument**, suitable full-peer control, source/audit validity, complete five-name panel and available D6h budget. One initial seed 42; seed expansion only normal promotion rules. Conditional A-E6R can study at most one MC1+SP3 combination upon distinct evidence; not automatic.

Mandatory cheap tests: input/output shapes, exact residual-identity equivalence, peer-perturbation sensitivity, zero peer sensitivity in stockwise MC0, planted causal peer influence on synthetic sequences, stable ticker ordering/permutation coordinate test, no future peer access, dropout-off deterministic evaluation, eventual M1/M2 gradient flow. These do not establish real trading alpha.

SP3 results report primary matched daily Rank IC, MSE, pairwise accuracy, folds/seeds, cost-inclusive portfolio metrics, gain relative to **full-peer** ordinary LSTM, parameters/runtime, local off-diagonal cross-hidden sensitivities \(\partial\widehat y_i/\partial h_j\), mixer rank/identity effects, stock domination and caveats. No causal peer inference from sensitivity magnitude.

---

## 12. D10 — Optional temporal readout or multi-horizon auxiliary objective (A-E7)

**Default:** TM0 final hidden state and TG0 four-hour target remain primary. **At most one initial A-E7 experiment** if prior development diagnostics identify a specific temporal **readout** or **supervision** deficiency. No automatic TM1+TG2 combination, TM3, multi-encoder/multiscale architecture, or test-data-directed activation. Use one previously chosen parent information set, matched controls and D6 fitting budget.

### 12.1 TM1 (preferred if readout deficiency)

Given \(h_{i,s}\in\mathbb R^{32}\), all 48 hidden states, trainable query \(q\in\mathbb R^{32}\), no-affine hidden LayerNorm:

\[
e_{i,s}=q^\top\mathrm{LN}(h_{i,s})/\sqrt{32},\quad
 a_{i,s}=\mathrm{softmax}_{s=1\ldots48}(e_{i,s}),\quad c_i=\sum_sa_{i,s}h_{i,s},\quad
\bar h_i=h_{i,48}+\gamma(c_i-h_{i,48}).
\]

- Shared across stocks, fixed 48 steps, **\(\gamma_0=0\)** exact identity to parent TM0, small seeded query initialization. At \(\gamma=0\), query gradient initially zero; verify flow after \(\gamma\) learns.
- **33 additional parameters** (32 query +1 scalar), e.g. stock-only TM1 6,466; MC0 TM1 7,106. AdamW decay 0.01 for query, 0 for gamma; no separate attention dropout. Keep final 10% readout dropout.
- Diagnose time-position entropy, learned gamma, historical-position sensitivity, synthetic informative-event recovery. Attention distribution is not causal explanation.

### 12.2 TG2 (alternative only if short-horizon supervision deficiency)

Three shared-encoder scalar heads for **60-, 120-, 240-minute** future cross-sectional median/unscaled-MAD targets, genuine entry/exit minute price and **horizon-specific training-fitted floor**, comparable to TG0 but never assumed to use same \(\epsilon\). Fixed loss

\[
L_{TG2}=0.2 L_{1h}+0.2 L_{2h}+0.6 L_{4h}.
\]

- Exactly two auxiliary heads (**66 added parameters**, stock-only 6,499; MC0 7,139); trade using **four-hour head only**; no new trade origins, no direction filter or change to portfolio policy.
- All three labels genuine and matured before fitting; match TG0 control population and report attrition. Four-hour purge at least as strict as largest supervised horizon. Inner checkpoint chosen by **primary 4h validation MSE**, not weighted auxiliary or portfolio metrics.
- Report individual loss/gradient contributions and negative-transfer diagnostics. Activation conditional, not automatically an additional fit. TM1 **or** TG2, not both; one initial seed 42.

### 12.3 Conditional branch protection

A low Rank IC alone is not proof of final-state memory compression; a negative Sharpe is not proof auxiliary labels are needed. Examples of valid activation rationale were a cheap earlier-hidden-state probe/synthetic temporal limitation for TM1, or mature short-horizon representation/learning diagnostics for TG2. If no specific deficiency, `A-E7 = INACTIVE_CONDITIONAL`. Do not try across multiple parent architectures and pick the best post hoc.

---
## 13. D11 — Optional factor, volatility and feedback adaptation (A-E8)

**Primary stays FC0 / AD0 / TG0**: no learned factor decomposition, no rolling feedback adaptation, four-hour relative-return target. **Default A-E8 DEFER**. At most **one** optional factor, volatility-supervision or adaptation branch if a distinct earlier deficiency justifies it; do not run all three, introduce a separate learned regime/MoE, or modify trading sizing based on auxiliary output.

### 13.1 FC7/FC6 factors — conditional, not initial five-stock run

- Five initial stocks come from **five different sectors**; no meaningful within-universe leave-one-out sector pool. The target stock cannot serve as its own independent sector benchmark.
- **FC7** first: supply verified, point-in-time, external observed market/sector factor series as a same-information ordinary-model control. No sector source assumed available or automatically substituted. **Not activated for five-stock first pass**.
- **FC6** possible only after justified expanded universe provides sector replication, FC7 information control and a distinct factor hypothesis beyond already attempted SP3/pooled peer exchange. Conceptual sector leave-one-out factor \(m_{S(i),-i}=\frac1{|S(i)|-1}\sum_{j\in S(i),j\ne i}h_j\) and all-stock pooled factor \(m=\frac1N\sum_jh_j\) may feed stock-specific nonlinear fusion \(\widetilde h_i=h_i+g_\phi(h_i,m,m_{S(i),-i})\). **Exact fusion MLP dimensions were not approved; leave unresolved if activated**, do not invent from this conceptual formula.
- No full FactorGCL/hypergraph/VQ/learned quantized regime architecture in v1.

### 13.2 TG4 — four-hour volatility auxiliary head (conditional)

Using **genuine complete 240 one-minute price increments** during the already approved future horizon, define

\[
RV_{i,t}^{4h}=\sum_{k=1}^{240}\left[\log\frac{P_i(e_t+k)}{P_i(e_t+k-1)}\right]^2,\quad
v_{i,t}=\log(RV_{i,t}^{4h}+\epsilon_{RV}).
\]

The positive \(\epsilon_{RV}\) and robust label scaler are fitted on permitted training labels. **The exact numerical floor algorithm/constant was not separately fixed**; implementation must not invent it if this branch activates. One added scalar volatility head **+33 parameters**; fixed weighted loss

\[
L_{TG4}=0.8L_{TG0}+0.2L_{RV}.
\]

Checkpoint using **primary TG0 validation MSE**. Four-hour return head alone selects long/short; no volatility-dependent sizing, trading duration or risk-policy change. Require complete genuine minute path; compare target/labels on matched eligible origin intersection. Default inactive.

### 13.3 AD3 — frozen encoder + shrinkage regularized daily rolling head (conditional)

Preferred *if* a time-varying predictive mapping deficiency is documented, without full LSTM retraining. Freeze the historically fitted LSTM encoder \(h_{i,t}\in\mathbb R^{32}\) and its original static 33-parameter linear head \(\theta_0=(w_0,b_0)\). At beginning of each eligible trading session, use preceding **63 exchange sessions**, with at least **50 eligible distinct sessions**, only four-hour labels **matured by the actual daily adaptation cutoff**. Use same adaptive head at both daily forecast origins; if insufficient data or numerical instability, **static \(\theta_0\) fallback**, flagged.

With \(\bar h=[h;1]\) and rolling eligible sessions \(\mathcal C_d\), proposed approved objective was

\[
\widehat\theta_d=\arg\min_\theta\left\{
\frac1{|\mathcal C_d|}\sum_{s\in\mathcal C_d}\frac1{O_s}\sum_{o\in\mathcal O_s}\frac15\sum_{i=1}^5 (y_{i,s,o}^{TG0}-\theta^\top\bar h_{i,s,o})^2
+\lambda_d\|\theta-\theta_0\|_2^2\right\},
\quad\lambda_d=\frac{\operatorname{tr}(\widehat\Sigma_{h,d})}{32}.
\]

This is a project-defined multiplier-one mean hidden-coordinate-variance ridge shrinkage; not claimed optimal. The record does **not** settle all covariance denominator/intercept-penalty corner cases; retain/ask rather than invent if activated.

**Critical prequential rule:** every adaptation update must be replayed from historical **actually matured labels** available by that decision. If using recent *issued-prediction performance*, the feedback predictions must genuinely originate from earlier chronological out-of-training issuance, not retrospectively generated in-sample forecasts from a later-fitted model. Never inspect confirmation outcomes to set AD3 window/penalty. AD3 remains inactive absent demonstrated dynamic mapping issue.

**AD1** recent realized error/Rank IC inputs and AD2/AD4–AD6 adaptive mechanisms are deferred until after credible AD3 rationale, not part of initial implementation.

### 13.4 A-E8 activation and claims

At most one of FC7/FC6, TG4, AD3; default no A-E8. Document triggering earlier evidence before fitting and retain matched static/control information, causal availability, target/portfolio unchanged, full D5/D6 economics/reporting. Negative net Sharpe is **not** a sufficient trigger. An unused branch must be listed `INACTIVE_CONDITIONAL` or `DEFERRED` with rationale.

---

## 14. A-E0…A-E9 — Frozen experiment dependency ladder

This **menu and priority** comes from `Track_A_Architecture_Experiment_Roadmap_First_Pass_FROZEN_v1.0.md`, with later chat choices specifying mechanisms; entries marked conditional are not commands to train.

| Experiment | Requirement | Purpose / compare against | Initial activation status |
|---|---|---|---|
| **A-E0** | MANDATORY | Price/index/timestamp/corporate action, feature/label eligibility, retained samples, simulator and leakage QA | Audit pending |
| **A-E1** | MANDATORY CHEAP | Momentum, seven-lag ridge, later ridge+USA500 and peers (cheap source-matched controls) | **D13-C07 rules finalized (§17); implementation and source QA pending** |
| **A-E2** | MANDATORY | FT0/TM0/SP0 stock-only LSTM vs momentum/ridge | Data blocked; D6 architecture frozen |
| **A-E3** | MANDATORY | MC0 market history information increment vs A-E2 and ridge market control | USA500 audit blocked |
| **A-E4** | HIGH | MC1 endpoint gate vs information-matched MC0 | USA500 audit blocked |
| **A-E4R** | HIGH/CHEAP | Causal U5 trend and U2 volatility diagnostics; one conditional RS3 ridge interaction | No fitting required for basic descriptive slices |
| **A-E4M** | CONDITIONAL | MC2 stepwise historical market gate vs MC1/MC0 | Activation rule not yet assessed |
| **A-E5** | HIGH | Leave-one-out peer mean/dispersion in ridge/shared LSTM | Requires clean peer histories |
| **A-E5L** | HIGH/CHEAP | Lag 0/1 H↔L directed peer signals, ridge first, neural follow-up conditional | Preformation H/L audit pending |
| **A-E6** | CONDITIONAL | SP3 low-rank learned peer exchange vs full-peer same-information ordinary LSTM and MC0/E5 | Not activated |
| **A-E6R** | CONDITIONAL | Continuous volatility×peer LL2; at most one later MC1+SP3 combination | Not activated |
| **A-E7** | OPTIONAL | TM1 **or** TG2 targeted temporal deficiency | Inactive |
| **A-E8** | OPTIONAL | One factor **or** volatility supervision **or** AD3 feedback adaptation | Inactive default defer |
| **A-E9** | MANDATORY FOR CONFIRMATORY CLAIMS | Locked finalist confirmation Jul2024–Jun2025 | Preflight blocked |

**No additional full custom signed recurrent cell, VQ-MoE, large Transformer, option-chain or macro architecture**, nor all-branch training, is authorized under roadmap v1.0. The first-pass menu controls which designs are even candidates. Source unavailability may BLOCK a mandatory branch; it is never silently declared complete.

---

## 15. D12 — Development selection, finalist replication and A-E9 confirmation

### 15.1 Selection metric and evidence

Use **daily-aggregated five-stock Spearman Rank IC** as primary development architecture ranking metric, with matched-origin/seed/fold comparisons, paired confidence intervals, MSE, ranking accuracy, economic net returns and complexity. Apply the D5d one-SE simpler-model preference when uncertainty estimate defensible. **Do not force a complex winner.** Confirmation is one first-look evaluation, not a new validation window to tune against.

### 15.2 Confirmation shortlist and independent controls

- Mandatory **nonneural** references: predefined momentum and lagged ridge, including necessary same-information ridge variants; cash, equal-weight buy-and-hold and matched-opportunity randomized long/short economic references.
- Default neural shortlist **at most three architecture families**, including **TM0 stock-only** and **MC0 stock+USA500 if source valid**; at most one additional eligible development-selected architecture. A weaker model is retained as a scientific reference, not portrayed as winning.
- Neural finalists evaluated at **all seeds 42, 123, 2026** in development, with no best seed selection, and supported stage/cutoff refits; only development evidence promotes one extension.
- Full-peer information control for SP3 is **still required** for strong mechanism attribution; see unresolved three-family vs four-control conflict in §20. If it cannot fit approved budget, narrow claim or request an explicit amendment, not skip control without disclosure.
- Use identical information sets for claimed mechanism increments, matched eligibility and identical protocol budget where practicable. Same-width does not always imply parameter-matched; disclose dimensions.

### 15.3 Locked manifest and final refit

Before any confirmation metric calculation, freeze a **versioned, immutable A-E9 manifest** containing selected architectures, controls, seeds, forecast/label/execution clock, input/target transformation versions, allowable historical fitting windows, selected selection protocol, feature and denominator fitting policy, data/config/code/checkpoint hashes, uncertainty method, both portfolio policies and all cost/borrow scenarios, required reporting.

For final confirmation fitting cutoff **2024-06-30** (purge labels crossing cutoff), D6g inner tail/epoch calibration then **fresh full permitted-history refit** per seed; no confirmation supervision or confirmation-based checkpoint choice. A predeclared AD3 update rule, **if separately activated**, can use subsequently matured labels at their true time in a causal adaptive replay; this is not the default AD0 protocol.

**A-E9 evaluation:** once, **2024-07-01 through 2025-06-30**. If results disappoint, report them and stop confirmatory selection; a later exploratory redesign would require new protocol and a genuinely new confirmation sample. Correct confirmed bugs and disclose first-look status impact; do not quietly overwrite reports.

### 15.4 Statistical interpretation

Use paired daily \(\Delta IC\), 5-session primary moving blocks, 10/20 sensitivity, 10,000 replicates, percentile 95% CI, HAC lags 5 and 10. No unqualified independence or distributional certainty; block assumptions may fail under nonstationarity. Do not claim selection-adjusted p-value from a model-conditional bootstrap.

**Temporal permutation/null:** A rigorously search-adjusted claim needs defensible panel/time-preserving null transforms and **rerun of the relevant fitting/model-selection procedure**, not merely shuffling final fitted predictions. D12 decision: **formal full-selection null test is CONDITIONAL and needs additional resource/protocol approval**, because global initial 40-pair cap may not fund it. If not run, report missing inference evidence and limit claims. Earlier project-wide desire for null testing and this conditional first-pass budget should be explicitly reconciled with collaborators if a formal null is a mandatory deliverable. The conceptual proposed null is a whole-panel same-origin trading-session target shift, but its precise lag distribution, stationarity/exchangeability and boundary handling were **not finalized**. Do not claim an exact valid permutation p-value.

### 15.5 Economic benchmarking and reporting

**All applicable baselines and model seeds**: both trading policies; 0/2/**5**/10bps execution scenarios; 0/0.5/3% annualized borrow fee scenarios; entire calendar including no-trade days; mark-to-market and full net P&L after external net trading/financing; turnover, holding-period distribution, drawdown, Sharpe (not a p-value), annualized returns where complete, stock/sector concentration, cost/rejection/veto/emergency decomposition. Portfolio paths can vary by friction scenario due to admission/equity differences.

- **Cash** reference.
- **Equal-weight buy-and-hold** five-stock equity context, **not risk matched** to intraday long/short; corporate actions and rebalancing convention must be documented (exact rebalance schedule not finalized).
- **1,000 randomized long/short strategy paths** (predeclared random seeds), same forecast opportunity calendar, paired one-long/one-short and sleeve/execution policies; report empirical distribution of gross/net returns, Sharpe, turnover, drawdown. This is a **descriptive comparator**, not a formal exact matched-realized-exposure statistical null. Random paths may veto different pairs, generate different holdings and cannot be assumed to match realized exposure perfectly.
- Net daily simple return where coherent: \(R_d=E_d/E_{d-1}-1\). If justified, annualized geometric equity growth \((E_T/E_0)^{252/D}-1\), descriptive Sharpe \(\sqrt{252}\,\overline{R_d-R_{f,d}}/\mathrm{SD}(R_d-R_{f,d})\); cash benchmark/risk-free convention must be disclosed rather than fabricated from unavailable data. Report market beta only with genuinely aligned market series.
- Break-even execution bps where a meaningful \(\Pi(c)=0\) threshold exists; avoid assuming linear monotone P&L under path-dependent cap decisions.
- Absolute-direction diagnostic **report only**, never a filter: ex-post fraction of selected long stocks with positive realized four-hour returns, shorts with negative realized returns, both, and positive realized pair/net P&L. Do not train a direction head.

### 15.6 Claims and report ledger

Separate claims of improved forecasting loss, improved cross-sectional ordering, architecture incremental advantage **beyond same information**, positive post-cost historical strategy return, and genuine selection-adjusted statistical robustness. Report support/inconclusive/refutation/blocked appropriately. A profitable backtest does not prove causation or universal edge; 5-stock one-year confirmation has low effective independent sample size.

Final report must include literature, source audits, timing and all feature/label formulas, data retention, baselines, full E0–E9 ledger, seeds, conditional activations and nonactivations, prediction metrics, every both-policy trading scenario, statistical limitations, untouched confirmation and realistic source/borrow/execution limitations. Do not present omitted or invalid branch as a tested negative result.

---

## 16. D13 — Implementation sequencing and non-duplication policy

**No Codex implementation prompt or actual fitting was requested in this consolidation task.** The later handoff should implement with staged explicit go/no-go controls:

1. **Feasibility-only source audit (A-E0):** verify Alpaca SIP stock prices/minute opens, course USA500 identity and price/timestamp semantics, historical membership, liquidity, split adjustments, data warmth/retention and cross-track 240-minute interpretation. Stop blocked branches if absent; no guessed substitutions.
2. **Canonical causal features and labels:** build/verify FT0, U1–U5, TG0, market/peer masks, train-only scalers and purges; synthetic/hand-calculated tests on splits, early closes, DST, missing minute data and historical as-of state. Confirm retention guards before fitting.
3. **Minimal nonneural references + modular portfolio simulator:** implement D13-C07 approved momentum/ridge (§17) only after source and feature audits, reusable prediction interface, two portfolio policies, physical netting, fills, bps costs, borrow, exposure and incomplete exits. Verify accounting by independent small hand cases.
4. **Minimal TM0/D6 pilot:** verify convergence, reproducibility, honest loss, runtime and storage; then progress through E3/E4/peer experiments by frozen priorities and branch activation, not all at once.
5. **Selection and confirmation:** full development/seed/uncertainty/cost reporting, manifest lock, independent final one-look evaluation, publish complete negative and positive results.

**Storage**: one canonical immutable source OHLC/minute/index/actions dataset per version; shared features, targets, masks, indicator warmups and derived lightweight indexed views; avoid per-architecture/per-seed/per-cost Parquet copies. Recompute cheap windows lazily or via reusable memory-mapped canonical arrays. Predictions immutable per fitted checkpoint; evaluate different portfolio policies/cost assumptions without retraining. Small selected model checkpoints and epoch logs rather than every epoch checkpoint. Append-only, resumable run ledger, disk-use audit, no unnecessary duplication of 25GB-style artifacts.

**Modular code responsibilities** (interfaces and paths NOT fixed): data/availability clock; calendar/execution grid; feature/target fitting; eligibility/missingness; prediction models; model training/calibration/refit; portfolio policies; physical holdings/orders/valuation; cost and fill models; borrow/financing; exposure and emergency risk; exceptions; metrics/inference; run ledger and report generator. All settings versioned/config-driven, no hardcoded performance-driven changes.

**Future agent instructions** should follow the user's standard project expectations: explicit reproducibility/tests, secure credentials/environment variables, preserve raw data, Git discipline, documented functions/loops/key variables and appropriate docstrings, contradiction questions before changing frozen rules, and a Markdown after each coding session listing created/modified files, their purposes, tests/results and open issues. Do not manufacture previously unknown repository paths/functions or require implementation choices that the user has not yet approved.

---
## 17. D13-C07 — Finalized inexpensive baselines (new choices approved 2026-10-10)

**Status: FINALIZED DESIGN, implementation/audit NOT TESTED.** The user explicitly authorized using the recommended settings for the previously missing A-E1 details. **These numerical choices are new to the present request**—they are not reconstructed from an earlier discussion and do not revise the frozen architecture menu. Full details are reproduced below so this file remains self-contained if conversation memory is unavailable.


**Authority:** User's current instruction, “small D13-C07 baseline decisions go ahead and use recommended.” These are **new recommendations now adopted**, *not* choices recovered from the former conversation. They do not change TG0, FT0, D6, the experiment ladder, or the trading rules.

### A.1 Momentum baseline

- At each valid forecast origin, assign each stock the already-available **FT0 M1**: latest completed hourly open/close log return divided by its trailing 60-hour RMS (with approved floor), using the canonical pooled training-robust-scaled M1 values.
- Rank five stocks **descending in M1** (largest is long, smallest is short). Do not tune reversal/momentum sign, time horizon or weights using development results.
- This is an **intraday 1-hour momentum baseline**, not a conventional multi-month equity momentum portfolio; identify it accurately in the report.
- Use the identical forecast calendar, five-stock input eligibility and both approved portfolio policies/cost scenarios. The baseline has no supervised fitting, but its FT0 scaler must still be fitted only on authorized history.

### A.2 Lagged ridge baseline, feature dictionary and fit

- Base feature matrix uses the **same 16 FT0 channels** as TM0 at seven fixed **scheduled completed-hour lags** relative to each forecast origin: **`[0, 1, 2, 5, 11, 23, 47]`** (0 = latest completed hourly step). Concatenate in precisely this lag order, FT0 channel order within lag. **112** stock inputs; no learned ticker identity for baseline A-E1.
- The ridge+USA500 information arm appends the same five D7 market channels at **these same seven historical steps**, with the approved standardized neutral historical missing fills and separate masks used for audit/eligibility, adding **35** channels for **147** total. No extra learned missingness-mask inputs or raw USA500 levels.
- In A-E5 add the approved mean and dispersion at these seven lags; in E5L use its preapproved directional features and H/L identity controls **in both LL0 and LL1**, not selectively. No new ridge feature-search grid.
- **Fairness disclosure:** The ridge reaches the same 48 scheduled-hour history horizon but observes only seven predeclared time snapshots; TM0/MC0 LSTMs read all 48 steps. The ridge is a **compact lagged-history comparator**, not an exactly full-step information-equivalent model. Market-on/off and peer-on/off ridge contrasts do have the same lag dictionary within each paired ridge comparison.
- Fit **one pooled common ridge model** across five stocks; one global unpenalized intercept, all other coefficients penalized; no learned stock ID or sector ID in the primary ridge. Use TG0 and the exact D5 equal-stock/eligible-origin/session weighting.
- For feature vector \(z_{d,o,i}\) and intercept \(b\), minimize

  \[
  \boxed{\sum_{d\in D_{fit}}\frac1{|D_{fit}|}\frac1{O_d}\sum_{o\in O_d}\frac15\sum_{i=1}^5(y_{d,o,i}^{TG0}-b-z_{d,o,i}^\top\beta)^2+\lambda\|\beta\|_2^2}.\]

- Ridge coefficient penalty grid: **`[0.0001, 0.001, 0.01, 0.1, 1.0]`**, with the objective normalized to *mean session loss* as written. Do not blindly pass those numeric values to a software API whose ridge penalty multiplies **unweighted sum-of-squares** instead of weighted mean loss; derive the matching rescaling and test against the reference objective.
- Select \(\lambda\) on the **last 63 exchange-calendar sessions** of each permitted fitting period as a chronological inner validation tail (with D6g ≥50 eligible days and ≥25 valid observations of each origin type; respect label maturity and purge). Fit candidate ridge models only on the earlier permitted inner-training prefix, including its own fitted FT0/U1–U5 scalers and TG0 floor. Choose the minimum **inner-validation session-weighted TG0 MSE**; in an exact numerical tie prefer the **larger** penalty. Do not use Rank IC/net Sharpe or outer fold outcomes to choose \(\lambda\).
- Then recompute any fitted preprocessing on the full permitted fitting history and refit ridge once using the chosen \(\lambda\). No D6g neural two-pass epoch loop, optimizer search, gradient clipping or neural seed requirement applies to the deterministic ridge solution; record solver version/tolerance, numerical conditioning and residual diagnostics.
- Keep market, peer and state-interaction arms on the **same five-candidate penalty budget**, dates and metrics; individual arms may choose different selected penalties on their own inner validation. No large ridge-grid search.
- **Important limitation:** seven-snapshot ridge need not be as expressive as an all-48-hour flattened ridge; report this when interpreting TM0-versus-ridge evidence. A separate full-flattened ridge would require an explicit additional control approval if this limitation becomes scientifically decisive.

### A.3 Predictive ranking ties

- Rank IC continues to use **midranks and the already approved constant-prediction conventions**.
- For *trading only*, break exact predicted-score ties deterministically using the five-name canonical ticker order: long = first in score-descending/canonical ascending order; short = last. Thus an all-tied origin gives two distinct names but is prominently reported as a **constant/undefined-prediction origin**, not quietly treated as ranking skill. No random tie-breaking or future-outcome tie resolution.

### A.4 Contextual equal-weight buy-and-hold

- **Not risk-matched:** start a separate contextual five-stock portfolio for each named outer evaluation segment, with no predictive model and **no scheduled rebalance**. Use the same genuine regular-session one-minute opening-price reference and verified corporate-action accounting as the primary simulator.
- **Predeclared timing:** attempt to buy all five at the **09:30 ET one-minute open on the first exchange session of the evaluated segment**; if the necessary prices are not eligible, remain in cash and retry the **next session's 09:30 ET** without retrospectively selecting a convenient day. Schedule terminal sales at the **last scheduled regular-session one-minute opening** on the segment's final exchange session (15:59 ET on an ordinary 16:00-close day; exchange-calendar-defined last minute on an early close). If that fill fails, use the causal exit-exception/retry rule and flag the segment's benchmark as incomplete where necessary; no fictitious mark or sale is inserted. These times are **new benchmark-specific conventions**, not D3 stock-ranking forecast origins.
- **Initial equal-dollar weights after costs:** for cost rate \(c\) in bps, with initial equity \(E_0\), target each name's initial gross purchase notional at \(E_0/[5(1+c/10{,}000)]\) using the observed reference prices. This allocates no more than initial cash after the modeled entry costs (subject to independently audited share/fill arithmetic). Recompute benchmark holdings/equity for each execution-cost scenario; do not simply subtract expenses from a fixed-return series.
- No cash dividend reinvestment. Credit verified dividends to cash; preserve economically correct share quantities through splits. At the end, report full-calendar **net marked equity and realized terminal sale** where feasible. If the last sale cannot be supported by genuine prices, disclose incomplete or assumption-dependent performance, not an invented total return.
- Label buy-and-hold explicitly as a **long-only equity-market-exposed contextual reference**, not a risk-/turnover-matched comparator for dollar-neutral four-hour strategies.

### A.5 Random 1-long/1-short reference

- Create **1,000** reproducible independent random ranking paths on the common **causally eligible forecast opportunity calendar**. At each origin, draw a uniform permutation of the five names and use its first and last entries as long and short; never condition on observed future labels or returns.
- Use a **separate deterministic random-seed namespace** from neural training: master `20261010`, with independent per-path substreams and versioned NumPy/random-generator information. Hold draws fixed across model comparisons so the reference distribution is not selected to favor one model.
- Replay **both** existing portfolio policies and **all** approved execution/borrow/cost scenarios. Count veto/cap rejections, actual gross exposure, turnover and P&L. Random paths match **opportunities and nominal sizing rules**, **not necessarily realized exposure or trade counts**; do not overstate risk matching or present the random distribution as a formal selection-adjusted null test.

### A.6 D13-C07 test obligations and status

- Verify hand-constructed FT0 M1 ranking, all seven ridge lag offsets/dimensions, session weights, inner validation separation, penalty objective normalization, deterministic tie handling and fixed random draws.
- Compare own-ridge versus market-ridge and own-ridge versus peer-ridge **within the same lag dictionary and matched evaluation calendar**; do not claim that seven-snapshot ridge and full 48-step LSTM have identical information access.
- Include benchmark implementation costs in the existing modular simulator; do not train neural networks for alternative policies or bps sensitivity.
- **Status: FINALIZED by current user request, subject to actual implementation tests and source/governance blockers.**

---

## 18. Preflight go/no-go matrix — no audits were passed by design approval

| Gate | Actual verification required | Status as of 2026-10-10 |
|---|---|---|
| P01 | Alpaca SIP historical six-hour regular-session stock OHLC, genuine minute opens and allowed data availability | **NOT VERIFIED** |
| P02 | USA500 source identity, exact index/feed semantics, historical OHLC/daily closes, publish times, 90-minute freshness | **NOT VERIFIED** |
| P03 | Five original stocks' 2020-07-01 historical USA500 membership (if meaningful), formation liquidity, backups, corporate actions | **NOT VERIFIED** |
| P04 | Five-stock 2020–2025 coverage, sufficient preformation and indicator warm-up history, D4 retention/regime balance | **NOT VERIFIED** |
| P05 | Shared Track A vs Track B interpretation of 240 continuous regular trading minutes vs four complete hourly advances | **JOINT SIGN-OFF PENDING** |
| P06 | Complete forecast issuance/label maturity/entry/exit `available_at` checks incl. two origins, DST, early close, stub | **NOT TESTED** |
| P07 | FT0, TG0, U1–U5 exact hand-audit, training-only fit, purged chronological splits, independent normalizer fit | **NOT TESTED** |
| P08 | Physical portfolio simulator: long/short, share netting, bps once, borrow, entry cap, conflict veto, emergency/exit retry, no hindsight | **NOT TESTED** |
| P09 | Exact A-E1 ridge/momentum/benchmark settings (§17) | **DESIGN FINALIZED; IMPLEMENTATION NOT TESTED** |
| P10 | Neural training/checkpoint/seed and synthetic gate/peer/mixer mechanism tests | **NOT TESTED** |
| P11 | Four-family SP3/full-peer shortlist conflict if SP3 qualifies | **CONDITIONAL PROTOCOL AMENDMENT NEEDED** |
| P12 | Immutable finalist shortlist/configuration and shared confirmation-release agreement | **NOT LOCKED** |
| P13 | Joint collaborator sign-off on shared date/calendar/data/cost/metric conventions | **PENDING** |
| P14 | Formal null test budget and source-compatible transform, if claimed as mandatory by course/shared agreement | **UNRESOLVED CONDITIONAL FUNDING** |

**Consequences:** A failed source audit blocks its dependent experiments, and no dummy values, silent source replacements or imaginary executions may be used to pretend it passed. An audit-only Codex phase can be prepared *after appropriate approval* to measure feasibility; a full training/backtesting launch remains unauthorized until applicable gates pass. Track B has not been assumed to approve Track A's particular timing/cost specification.

---

## 19. D13 audit of cross-block conflicts and caveats

The initial D13 audit recorded the following 12 items. **C01 and C07 have explicit user approval (C07 through the current recommendation-authorizing request); all other flagged items retain their recorded conditional or blocked status.**

| ID | Topic | Recorded state / disposition |
|---|---|---|
| **C01** | Future label validity vs causal portfolio entry | **FINALIZED now:** separate forecast, entry, label and execution outcome; never decide entry from future exit availability (§4.3) |
| **C02** | Four complete trading-hour advances vs 240 continuous regular trading minutes | **BLOCKED pending two-track clock sign-off**, preserve provisional D3 without hiding distinction |
| **C03** | Retrospective data coverage criterion vs point-in-time 2020 formation | **Report two criteria separately**; eligibility audit/source history pending |
| **C04** | USA500 identity/fields/history/availability | **BLOCKED source audit** |
| **C05** | Genuine one-minute execution reference prices and feasibility | **BLOCKED source audit** |
| **C06** | Three neural families vs scientifically necessary fourth full-peer control | **Conditional explicit amendment** or appropriately narrowed claim before A-E9 |
| **C07** | Exact momentum and ridge baselines | **FINALIZED by current request:** exact choices in §17; implementation and audit not performed |
| **C08** | Forty pairs vs mandatory fold/seed/controls and rescues | **Resource ledger mandatory**; no unapproved overrun; D13 proposed planning allocations were recommendations not independently approved exact reservations |
| **C09** | Separate USA500 validity masks vs fixed 21-channel MC0 | **Design specified**: masks separately stored, zero historical neutral fills, no unapproved neural mask channels |
| **C10** | Formal full-selection temporal null is conditional | **Inference caveat**: no adjusted-significance claim without correctly rerun procedure and extra approval |
| **C11** | D6g calibration epoch vs new full-history refit | **Approved deliberate trade-off**; record different optimizer-step counts |
| **C12** | Ex-post absolute-direction diagnostics vs trading signals | **Finalized prohibition**: direction influences no initial trading or model-selection decision |

An additional **unresolved optional-branch detail** occurs with FC6 nonlinear fusion dimensions, TG4 numerical auxiliary floor, and several AD3 covariance/rolling-fit edge cases. Because these branches are inactive, the design does **not** license inventing those details at implementation time. They require a fresh decision **if and only if** the relevant branch activates.

---

## 20. Version, approvals and research completeness rules

### 20.1 Do not mislabel the current state

- **Architecture/menu design:** complete through D12 at the level of approved main mechanisms.
- **D13-C01 and D13-C07:** explicitly approved and final (D13-C07 choices newly selected, not recovered historical settings).
- **A-E1 exact numerical baseline contract:** **FINALIZED DESIGN by current approval** (§17); implementation, objective/scaler tests and benchmark accounting still pending.
- **Source/clock preflight and shared approvals:** **not passed**.
- **Mandatory training and out-of-sample results:** **none have been run or verified as part of this conversation**.
- **A-E9:** confirmation entirely protected; release only after locked manifest and sign-offs.

This v1.1 consolidated record is a **draft implementation contract** with high detail, not a substitute for actual source verification, shared-clock sign-off or a final executable freeze. The companion `Track_A_Stage_Gated_Audit_and_Failure_Traceability_Plan_v1.1_2026-10-10.md` defines the G0–G9 audit boundaries **and §13 post-run diagnostic/replay obligations**, but **no audit has been run**. Future amendments must be new versioned changes identifying affected runs and comparability; never silently rewrite the v1.0 frozen architecture menu or old results.

### 20.2 Complete experiment ledger expectations

Minimum metadata for every planned/attempted run: A-E stage, hypothesis, branch activation rationale, models and identical-information comparator, universe/time split, stock and USA500 source versions, FT0/U1–U5/TG0 versions, eligibility/retention, code/config/dataset/checkpoint hashes, seed, fold, inner/refit epochs, optimizer parameters, elapsed compute/disk footprint, result validity, prediction and both-policy economics/costs, uncertainty where applicable, failure/reason/next action. Keep planned but inactive conditional branches in a visible experiment map.

Statuses must distinguish: `COMPLETED`, `PROMOTED`, `NOT_PROMOTED`, `INCONCLUSIVE`, `FAILED`, `INVALID`, `BLOCKED`, `DEFERRED`, `INACTIVE_CONDITIONAL`, `RESCUED`. Also retain scientific diagnostic classes from the roadmap: `DATA/TIMING ERROR`, `OPTIMIZATION/IMPLEMENTATION FAILURE`, `INFORMATION-LIMITED`, `UNDERPOWERED/INCONCLUSIVE`, `STRUCTURAL MISMATCH`, `NO INCREMENTAL EVIDENCE`, `PROMISING`.

Do not silently omit failed candidates or cherry-pick successful seeds. Report actual valid metrics where available; do not compute performance metrics from defective/incomplete data solely for table completeness.

### 20.3 References to preserve in final report (motivations, not guaranteed results)

- Fischer & Krauss (2018), *Deep Learning with Long Short-Term Memory Networks for Financial Market Predictions*, EJOR, https://doi.org/10.1016/j.ejor.2017.11.054 — precedent for a modest shared cross-sectional LSTM, not proof of optimal depth.
- MASTER (AAAI 2024), https://github.com/SJTU-DMTai/MASTER — market-guided feature weighting; do not copy reported edge or large feature menu into our data without audit.
- StockMixer (AAAI 2024), https://doi.org/10.1609/aaai.v38i8.28681 — economical cross-stock information exchange, not proof of five-stock intraday advantage.
- Gu, Kelly & Xiu (2020), *Empirical Asset Pricing via Machine Learning*, https://doi.org/10.1093/rfs/hhaa009 — nonlinear cross-sectional predictor relationships.
- Daniel & Moskowitz (2016), *Momentum Crashes*, https://doi.org/10.1016/j.jfineco.2015.12.002 — market trend/volatility-conditioned momentum; different frequency/horizon.
- Moreira & Muir (2017), *Volatility-Managed Portfolios*, https://doi.org/10.1111/jofi.12513 — absolute volatility importance; does not authorize volatility-based sleeve sizing.
- Chordia & Swaminathan (2000), *Trading Volume and Cross-Autocorrelations in Stock Returns*; Hou (2007), *Industry Information Diffusion and the Lead-lag Effect in Stock Returns* — motivation/limitations for directed peer analysis; primarily different universe/horizon.
- Loshchilov & Hutter (ICLR 2019), *Decoupled Weight Decay Regularization*, https://arxiv.org/abs/1711.05101 — AdamW distinction.
- Pascanu, Mikolov & Bengio (ICML 2013), *On the Difficulty of Training Recurrent Neural Networks*, https://proceedings.mlr.press/v28/pascanu13.html — recurrent gradient clipping.
- Goodfellow, Bengio & Courville (2016), *Deep Learning*, §7.8, https://www.deeplearningbook.org/ — early stopping and full-history refit.
- Prechelt (1998), *Automatic Early Stopping Using Cross Validation*, https://doi.org/10.1016/S0893-6080(98)00010-0 — stopping/computational trade-offs.
- Cawley & Talbot (2010), *On Over-fitting in Model Selection*, https://www.jmlr.org/papers/v11/cawley10a.html — noisy development selection.
- White (2000), *A Reality Check for Data Snooping*, https://doi.org/10.1111/1468-0262.00152 — repeated strategy selection caveat.
- Künsch (1989), *The Jackknife and the Bootstrap for General Stationary Observations*, https://doi.org/10.1214/aos/1176347265 — dependent resampling background.
- Almgren & Chriss (2001); Gârleanu & Pedersen (2013) — intended versus executed portfolio positions and transaction costs, not evidence that our bps rates or veto are optimal.

These are documentary context; links and paper summaries should be independently checked before publishing bibliographic details as verified facts. No real financial results from Track A have been observed in this design chat.

---

## 21. Next actions and change log — still no Codex training authorization

1. **D13-C01 and D13-C07 are completed design decisions**. The former enforces entry-time causal eligibility distinct from future-label validity; the latter fixes the inexpensive baseline formulas, small ridge regularization-selection budget, tie policy, contextual buy-and-hold and 1,000-path random benchmark (§17). Their implementation and numerical audits **have not yet been performed**.
2. The companion **G0–G9 stage-gated audit plan** is the approved way to detect and trace implementation failures at logical boundaries, without repetitive expensive audits; it is an audit specification, not evidence of a PASS.
3. Obtain actual **joint sign-off on the four-hour-clock definition** (D13-C02) and other shared data/cost/metric conventions. Track B collaborator consent is **not assumed**.
4. Verify genuine source entitlement, stock/USA500 coverage, historical minute fills, memberships, corporate actions and retention in a **separately authorized A-E0 audit-only** implementation phase. Do not silently replace USA500, relax eligibility, or manufacture fills.
5. Resolve any *conditionally material* three-family-versus-four-control SP3 confirmation conflict **only if SP3 becomes a finalist**. Optional FC6/TG4/AD3 details explicitly marked unresolved remain unresolved until activation and fresh approval.
6. After gate evidence passes, lock the true executable protocol and prepare a **separate staged Codex prompt**. Do not automatically fit A-E1–A-E9 or open July 2024–June 2025 confirmation now.

### v1.1 change record (relative to preserved v1)

- Newly selected recommended baseline settings entered verbatim in §17, clearly labeled as **new D13-C07 decisions**.
- Revised A-E1 readiness statuses in §§1,14,18–20; no longer claim baseline hyperparameters are missing.
- Associated approved G0–G9 audit companion cited; source/clock/collaborator/blocker statuses **not upgraded**.
- No modifications to preexisting D1–D12 formulas, frozen roadmap family list, spending limit, model selection rules or untouched-confirmation dates.

**Preserve v1 as an earlier provenance artifact.** v1.1 is the more complete design record but is still not a fully verified runnable experiment.


## 22. Additive D13 — Post-run model-failure diagnosis and replay (NEW user-requested requirement)

**Authority/status:** The user has newly required a **resource-conscious explanation/traceback capability** after training and results review, especially when a promising five-stock model performs poorly after a justified universe expansion. This is an **additional implementation contract**, not an earlier D1–D12 architecture choice, and is **not yet implemented or tested**. The detailed, binding stage-by-stage list is in `Track_A_Stage_Gated_Audit_and_Failure_Traceability_Plan_v1.1_2026-10-10.md`, §13. It supplements, rather than replaces, the existing G0–G9 gate audits.

### 22.1 Required behavior and resource limits

- **Cheap mandatory run summaries (T0):** reuse the already required canonical manifests, feature distributions/eligibility, training curves/gradients, prediction ranges/cohort performance and physical portfolio event ledgers. Keep small numeric summaries; no unbounded intermediate-tensor dumps.
- **Small on-demand evaluation-mode replay (T1):** given a run ID and a concrete session/origin/ticker, reconstruct and compare `raw source → canonical as-of → raw feature → fitted scaled input/mask → actual model encoder/gate/mixer/readout → prediction and five-stock rank → sleeve/order/fill → marked equity`. Preserve source timestamps, fitted scaler/checkpoint hashes and stable identifiers. Only replay modules present in that run.
- **Fixed plus anomaly cases:** an approximately 8–12-origin frozen representative development set; up to 3–5 explicitly `POST_HOC_DIAGNOSTIC` exception cases per failure class when needed. Never use failure-selected confirmation examples to tune the model. Do not promise exact reconstruction of training-time dropout masks or unretained optimizer steps.
- **Model failure report:** a concise Markdown report plus small JSON summary that shows before/after differences, the **first identifiable discrepant boundary**, evidence for and against a few root-cause hypotheses, sample/episode counts, run/checkpoint/source IDs, downstream invalidation/rerun scope, and unresolved alternatives. A result may be `NO DETERMINISTIC DIVERGENCE FOUND`; poor financial performance alone is not a software failure.
- **One reusable diagnostic library/CLI:** support commands conceptually equivalent to `summarize`, `trace-origin`, `trace-trade`, `compare-runs` without duplicating feature-engineering functions. Create small examples or optional bounded arrays only on demand. No new large persistent datasets, no logging of every activation at every epoch and no automatic extra training runs.
- **Hypothesis-driven checks:** distinguish implementation/data leaks, target/floor amplification, scaler/representation shift, optimization nonlearning, under/overfitting, unstable seeds/regimes, insufficient peer signal, ranking-instability/churn and net execution cost drag. Report performance by stock, origin, volatility/trend state and calendar period with honest sample sizes.
- **Five-to-twenty-stock bridge (only if D8h expansion is independently activated):** compare the original five's raw and transformed observations in the expanded source; show how five-stock TG0 differs from twenty-stock TG0 on common names/dates; compare old and new stock distributions/coverage/sector mix; audit canonical identities, peer composition and SP3 dimension change; decompose economic turnover and costs. Do **not** treat a change in five-name IC versus twenty-name IC as a matched evaluation or apply an N=5 SP3 mixer to N=20 unmodified.
- **Experimental boundaries:** rerunning any neural fit, activating optional mechanisms, changing features, or inspecting the untouched confirmation for new selection requires the previously approved protocol and D6h/G9 protections. Postconfirmation forensics can explain a frozen result but cannot restore the period's untouched status after model selection changes.

### 22.2 Acceptance conditions for eventual Codex handoff

Codex must deliver a small tested replay utility and report template; demonstrate reconstruction of one model prediction through its actual intermediate boundaries and one physical trade through final equity; compare two immutable runs/versions; and catch small injected synthetic timestamp/scaler/ticker/cost faults at the correct boundaries. The test must not claim financial alpha or declare any source passed. Attach diagnostic output to the **same append-only experiment ledger**; preserve the canonical source store and the frozen experiment limits.

**Status:** DESIGN REQUIREMENT ADDED; NOT IMPLEMENTED, NOT EXECUTED, NO NEW MODEL TRAINING AUTHORIZED.

### v1.2 change record

- Added this §22 and updated the companion audit-plan reference to **v1.1**, which contains the detailed post-run diagnostic/replay contract.
- Existing D1–D12 formulas, D13-C01/C07 baseline choices, G0–G9 logical gates, numerical thresholds, conditional branch rules, and 40-pair limit remain unchanged.
- No missing source identity, collaborator approval, architecture-specific conditional detail, actual audit result or empirical performance was invented or upgraded to PASS.
