# HF20 — Complete Experimental Consolidation, Scientific Evidence Archive, and Novel LSTM Architecture Handoff (v3: FT16/Data/Replication Integrated)

**Prepared:** 27 October 2026  
**Purpose:** Primarily the **frozen experimental consolidation and reproducibility record** of the full HF20 research program to date; secondarily a scientific/protocol handoff for a future novel-architecture ChatGPT/Codex conversation. Preserve completed **positive, negative, mixed and failed** results with the exact known configurations and report every unresolved detail without invention.  
**Status:** Expanded **v3 historical archive** with the executed-code FT16 specification and S9-MAG methodological-replication supplement; **no novel-architecture training authorized by this document**. Supersedes v1 as the preferred reference without altering historical run artifacts.  
**Current project focus:** Twenty-stock, hourly-OHLCV-based **cross-sectional four-trading-hour return ranking**, initially with a shared LSTM; subsequently investigate whether deliberately structured recurrent architectures add out-of-sample ranking information.  
**Last reported neural research ledger:** **130 / 200** cumulative started pairs, **70 unspent**. Confirm against the actual live ledger before reserving anything.  
**Protected 2026:** Remains **closed**; do not read its observations, labels, forecasts, numerical metrics, or protected content hashes without a separate explicit release.

> **Instruction to the receiving chat.** Treat this first as a historical source of truth and only second as a launch point. Read this **entire v3**, including **Part II appendices A–K and Part III source-preservation annexes**, and the referenced *executed* project records before writing any implementation instructions. Do not mistake a proposal for a completed experiment or a positive descriptive metric for a robust edge. First reconcile existing code, feature/target recipes, source and budget; discuss **one** architecture, matched comparator(s), objective, key ablation, resource cost and stop criteria with the user. Prepare a small, explicit research design and Codex execution prompt only after that discussion. **Do not automatically launch all N1–N6 or A9–A11, retrain old models, open 2026, build a new dashboard, or create enterprise-grade auditing infrastructure.**

## 0. The latest user decisions—these supersede older planning prose

1. **Move now to novel recurrent-architecture research.** The user can already open and inspect the existing HTML dashboards. **No dashboard integration/redesign/repair is requested now**; earlier tentative plans to add S1/S2/S4 rank visualizations into the original dashboard are *superseded for the immediate work*. Preserve existing dashboard files; link or reuse them only as needed.
2. **Keep options/trading-signal research separate.** The encouraging S9-MAG magnitude forecast and the idea of calibrated/thresholded/smoothed signals against option-implied movement, followed by a long-straddle test, have their own later project handoff: `HF20_S9_MAG_LSTM_to_Options_Strategy_Research_Handoff_2026-10-27.md`. Do **not** implement a straddle backtest, strategy thresholds, live signals or execution in the novel-architecture campaign.
3. **Engineering overhead is a hard constraint, not a slogan.** The user raised excessive engineering/auditing overhead repeatedly. Previous prompts used “lightweight” language while simultaneously requiring huge stage-gated per-parameter/per-batch logs, hundreds of file/hash checks, extensive diagnostic receipts and sequential postfit gates. **Do not repeat this.** See §7 for mandatory lean execution rules, what must remain tested, and forbidden overhead.
4. **Scientific comparisons must remain consistent with the executed HF20 protocol.** Preserve genuinely causal input/label timing, frozen annual folds, exact observed output populations, prefix-fitted transforms, correct target-specific losses and baselines, equal-year ranking metrics, descriptive dependence-aware uncertainty, and the reserved future confirmation set.
5. **Preserve all past evidence without trying to “fix” weak experiments.** Some past arms completed with no edge; they remain scientifically informative. Failed/paused arms are not zero-score or “proven useless.” A model that predicts magnitude may still fail at ranking; they are distinct tasks.
6. **Seek scientific economy.** One clearly stated hypothesis at a time; initial reference one seed and compact model, information-matched simpler control, at most one decisive ablation when worthwhile, no unconditional architecture sweep and no automatic rescue fitting.

### Evidence tiers and authority precedence

**Tier A, authoritative for a numerical rerun:** The live repository’s **executed** source/FT16/TG20 contracts, exact annual fold indices and eligible score keys, per-run configuration/target/scale files, checkpoints, raw saved predictions, actual start-ledger records, and final execution reports. **Only actual artifacts establish that a run took place.**

**Tier B, supplied retrospective result reports and executed-code extracts:** The user's final S3, S4 and S5/S9 decisions and numeric CSVs; additionally two Codex extractions made **27 October 2026** from repository HEAD `5f7bb86a35d5aaff34ff79ef8f471117de6d3e42`: `HF20_FT16_Complete_Feature_Specification.md` and `HF20_S9_MAG_Exact_Replication_Supplement.md`. These now establish precise feature/source/formula/recipe identities and MAG per-fold parameters, but **were not independently recomputed against raw data in this chat**. Original executed-code/receipt paths are given in the source-preserved Part III.

**Tier C, earlier frozen/proposed designs:** Original Track A 10 October first-pass menu, consolidated architecture menu, 10+3, S0–S11 plan and N1–N6 literature proposals. These record intent/hypotheses and **do not automatically grant fitting authority or override a later actual implementation**. Some implementation specifics are available only in local code/receipts. The handoff flags those gaps rather than guessing.

The **historical five-stock Track A design** and the **later twenty-stock HF20 executed workflow** differ in stock universe, some data/clock conventions, target eligibility and evaluation dates. Never apply the older five-stock `D1`–`D13` or `A-E*` instructions as if they were the executed HF20 source contract where superseded. “Frozen” in an older document refers to that document's then-current scope, not necessarily today's latest decision.

---

## 1. Current reference data, mathematical task and reproducible core configuration

### 1.1 Cohort, data and source

- **Fixed HF20 stocks (readability order):** `AAPL, AMD, AMZN, AVGO, BA, BAC, COP, CSCO, CVX, JNJ, KO, MA, MRK, MS, PEP, SBUX, TSLA, VZ, WFC, XOM`. **Actual executed tensor axis:** `VZ, COP, BAC, BA, AAPL, PEP, MRK, SBUX, CVX, MS, AMD, KO, JNJ, AMZN, XOM, WFC, AVGO, TSLA, MA, CSCO`.
- **Historical source:** Frozen `mito0o852/OHLCV-1m` monthly minute Parquets at Hugging Face revision `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`, processed by P019B/P020 into **hourly U.S. equities OHLCV**. Warmup starts July 2010; the S4/S9 **numerical source ends December 2024** (189 acquired monthly files through March 2026 does **not** mean 2025/2026 were numerically read for S9). Use the pinned existing local source; **no duplicate/download in new architecture work**.
- **Input:** `X_{i,t} ∈ R^{48×16}`, **FT16** in exactly this order: `M1 M2 M3 M4 V1 V2 V3 B1 B2 Q1 Q2 T1 T2 T3 T4 T5`. **The complete executed mathematical definitions, rolling windows, as-of M2 and all feature preprocessing are now in §1.1a and Part III Annex A.** Actual per-phase numerical fitted scalers/floors and eligible indices remain in the S4 repository recipes.
- **Temporal input:** An hour means a complete scheduled market observation, **not** an uninterrupted wall-clock hour; no synthetic weekend/overnight hourly entries. Some feature windows themselves reach further back than the explicit 48-step tensor. Original FT16-only LSTMs process stocks independently at inference despite shared parameters; they do not natively consume other stocks' histories unless separately constructed panel features are added.
- **Causality:** All feature information, historical same-origin M2 outcomes, newly introduced market/panel state and source-quality markers must obey an as-of cutoff. The documented source uses **origin+2-minute assumed issuance**, **endpoint+2-minute label maturity**, seven S4 M2 contexts, and prefix-only per-phase recipes. Historical actual publication/arrival times and retrospective corporate-action vintages **remain unverified**; do not reinterpret retrospective QA fields as real-time observed state.
- **Fixed-survivor caveat:** Twenty selected historical survivors do not establish point-in-time broad-market generalization. Increasing stock count is a future separately authorized research dimension.

### 1.1a Fully documented FT16 and source/quality contract (executed-code extraction)

**Authoritative formula ID:** `HF20_HF1M_LONG_v1_FT16_v1` from `configs/hf1m_long_ft16_v1.json`. Its executed S4/S9 48×16 model uses **own-stock** features only, with no USA500/sector/ticker-ID or options inputs. The full source includes all 16 native formulas, 13 robustly scaled channels and 3 bounded identity channels, historical same-origin M2 maturity, EMA/Wilder state, quality-admission masks, exact source files/line references and all phase-dependent recipe fitting details. The table below is the complete native-feature list at a methodological level; read Part III for the exact corner cases.

| Position | ID | Native feature: exact mathematical definition (before robust scaling) | Source/lookback |
|---:|---|---|---|
| 1 | `M1` | $a_t/\max(s_{60,t},h_i)$, $a_t=\log(C_t/O_t)$ | Hourly open/cap5 close; 60 scheduled bars, ≥57 valid; current hour included |
| 2 | `M2` | $\mu^{(o)}_{20,i,t}/\max(s^{(o)}_{60,i,t},b_i)$ | Matured historical same-origin **four-trading-hour** returns; 20 prior regular-origin days (≥19), RMS60 (≥57), context-specific |
| 3 | `M3` | $\log(D_k/D_{k-5})/[\sqrt{5}\max(s_{63,k},\delta_i)]$ | Prior genuine 15:30-surrogate daily closes, RMS63 ≥60 |
| 4 | `M4` | $\log(D_{k-20}/D_{k-125})/[\sqrt{105}\max(s_{63,k},\delta_i)]$ | 105 daily-return intervals, skipping last 20 sessions; daily RMS63 |
| 5 | `V1` | $\log\max(s_{12,t},h_i)$ | RMS of hourly $\log(C/O)$, 12/12 |
| 6 | `V2` | $\log\max(s_{60,t},h_i)$ | Hourly RMS60, ≥57 valid |
| 7 | `V3` | $V1_t-V2_t$ | Log short/long floored RMS ratio |
| 8 | `B1` | $\log(H_t/L_t)$ | Safe observed hourly high/low; may be partial and quality-marked |
| 9 | `B2` | $(2C_t-H_t-L_t)/(H_t-L_t)$ | Close location, zero if zero range; invalid if outside ±(1+1e−10) |
| 10 | `Q1` | $\log[(U_t+q^h_{i,r})/(\bar U^{slot}_{20,t}+q^h_{i,r})]$ | Same scheduled-slot prior 20 occurrences, ≥19; current excluded, same share regime |
| 11 | `Q2` | $\log[(\operatorname{Mean}_{5,5}(W)_k+q^d_{i,r})/(\operatorname{Mean}_{60,57}(W)_k+q^d_{i,r})]$ | Previous regular-session six-hour volumes; same share regime |
| 12 | `T1` | $\log[C_t/\operatorname{Mean}_{20,19}(D)_k]$ | Current cap5 close versus mean of prior daily surrogate closes |
| 13 | `T2` | $\operatorname{Mean}_{20,19}(\operatorname{sign}(d))_k$ | Prior daily-return signs, including zero |
| 14 | `T3` | $(E_{6,t}-E_{18,t})/C_t$ | EMA6/EMA18 on cap5 closes; ≥360 post-seed updates and 69/72 recent coverage |
| 15 | `T4` | $(E_{24,t}-E_{72,t})/C_t$ | EMA24/EMA72; same initialization and gates |
| 16 | `T5` | $(\mathrm{RSI}_{14,t}-50)/50$ | Wilder RSI14, first 14 connected changes +≥140 updates and recent coverage |

`C_t` is the capped causal completed-hour closing-price input proxy, distinct from the genuine hourly terminal `G_t`. `D_k` is a genuine **15:30 surrogate**, not the 16:00 close. $s_{n,t}$ and $s_{63,k}$ are **root mean squares** of returns, not demeaned standard deviations. $h_i,\delta_i,b_i$ are positive fitted floors. Volume pseudocounts $q$ are per-stock and split-share-regime. Full formula edge cases, EMA/RSI state transitions and M2 maturity gates are preserved verbatim in the annex.

**P019B/P020 data and bad-data handling:** The source is [the pinned public HF dataset](https://huggingface.co/datasets/mito0o852/OHLCV-1m); original exchange/vendor/feed is **not verified**. Use `exchange_calendars` XNYS RTH, UTC minute-start records, ET session dates, six completed full-hour input bars and a separate 15:30–16:00 source stub. OHLC is retrospectively split-adjusted through March 2026, with unchanged share volume and a hard COP 2012 spinoff price-basis break. Exact duplicate rows are collapsed; all conflicting observations at identical `(ticker,timestamp)` are excluded; P019B separately quarantined 18 unresolved RTH minutes affecting 14 hourly bins while retaining four identified genuine major moves. Bounded last-close proxy: **at most five minutes**, causal and never a target price; no overnight/interpolation/missing target repair. Input-only volume zero assumptions are permitted under capped-gap and clean-bin gates, not treated as certain no-trade observations. Native missing 13 unbounded inputs→training-fitted median→zero after robust scaling; bounded `B2/T2/T5` missing→zero with identity scaling. A failure of all-48-close source admission is **not** repaired by feature fallback; any missing genuine endpoint in one stock removes the complete 20-stock label origin. **No target fill or silent exclusion of extreme genuine moves**. Detailed A18/P019B QA and exact event-ledger codes are in Part III B.

**Feature fitting:** Unique eligible historical input-hour keys, training phase only, fitted from 2011-04-01 through the appropriate inner/refit stop. Hourly/daily/M2 floors use 5th percentile of positive pooled RMS, volume pseudocounts 1% of positive regime-specific median, 13 unbounded channel robust scales median + unscaled MAD (fall back IQR/1.349, then population SD, then 1); 3 bounded channels zero/identity. M2 uses **seven** contexts in S4/S9, **two** in S1/S2; S3-B changes only M2 for h1/h2 while S3-A keeps original four-hour M2. **S5** alone adds six time metadata channels (22 total). Numerical phase parameters are in `S4/Fxx_{inner,refit}_recipe.json` and bound into S9 by `S9/S4_REUSED_RECIPES.json`.

**Scientific distinction for next experiment:** Changing to different M2 contexts, including missingness flags in a new model, updating source-vintage adjustments, or recomputing robust scales under new keys changes the information set; a difference with old S4 cannot then be claimed to isolate architecture.


### 1.2 Four-hour target and seven origin slots

For stock `i`, an actually eligible forecast origin `t`, and the source-backed four-*trading*-hour endpoint `e(t)`:

\[
R^{(4)}_{i,t}=\log\frac{P_{i,e(t)}}{P_{i,t}},\qquad
m_t=\operatorname{median}_{j=1}^{20}R^{(4)}_{j,t},\qquad
D_t=\operatorname{median}_{j=1}^{20}|R^{(4)}_{j,t}-m_t|,
\]

\[
Y_{i,t}=\frac{R^{(4)}_{i,t}-m_t}{D_t+\epsilon_{\mathrm{fit}}},\qquad
Z_{i,t}=\operatorname{asinh}(Y_{i,t}/s_{\mathrm{fit}}).
\]

`epsilon_fit` and `s_fit` are **training-phase-fitted** and must use the true per-fold recipes. Median, MAD and future-return values are **labels only**, never inputs. Monotone common-cross-section transforms preserve the *realized ordering* but not the objective's raw-return interpretation.

The standard S4/S5/S9 **candidate** origins in Eastern time and ordinary-session nominal endpoints are:

| Forecast origin ET | Four trading-hour reference endpoint | Label class |
|---|---|---|
| 09:30 | 13:30 same session | INTRADAY |
| 10:30 | 14:30 same session | INTRADAY; original S1–S3 morning slot |
| 11:30 | 15:30 same session | INTRADAY; original S1–S3 morning slot |
| 12:30 | 10:00 next session | OVERNIGHT-crossing |
| 13:30 | 11:00 next session | OVERNIGHT-crossing |
| 14:30 | 12:00 next session | OVERNIGHT-crossing |
| 15:30 | 13:00 next session | OVERNIGHT-crossing |

Actual eligibility is source-, calendar- and endpoint-dependent; **not every session has seven eligible origins**. A normal cash session is 09:30–16:00 (6.5 hours); the 15:30–16:00 closing stub is a half-hour, **not a full hourly input bar**, but counts toward trading minutes. Never pretend 15:30 is an official 16:00 close. True minute-price endpoints are required, especially 09:30 opening and overnight-return endpoints. Do not invent missing prices or treat early closes/holidays as ordinary sessions. Historical 09:30 uses **previously completed hours**, not an unfinished current-session input bar.

**Crucial execution limitation:** The model's time-of-issue is approximated as the label-origin timestamp **plus about two minutes**; the return starts at the **earlier** price proxy. This is a price-only forecasting target, **not** an executable post-issuance fill or tradable four-hour P&L. No new architecture may silently change that starting-price convention, or it ceases to be matched to S4/S5.

### 1.3 Frozen annual walk-forward evaluation and partition policy

- **F21**: calendar-2021 OOS; earlier history for training, inner validation approx most recent six calendar months, purge/embargo and label maturity, then fresh refit.
- **F22**: 2022 OOS, earlier history only.
- **F23**: 2023 OOS, earlier history only.
- **F24**: 2024 OOS, earlier history only.
- **Actual S4/S9 common OOS population:** **4,013 origins**, **793 exchange sessions**, **80,260 stock-origin rows** (20 per origin), distributed as F21 955/188 sessions, F22 1,180/210, F23 887/187, F24 991/208. These are verified *reported* counts for S4 and S9; architecture inputs may legitimately change admissibility only if a separately disclosed source requirement forces it, and must not relabel an unpaired comparison as matched.
- **2025:** Prior research used a later 2025 development sample. Do not draw on it for new exploratory tuning or retrospectively re-optimize S4/S9 choices. In particular, 2025/2026 dates must not be silently assigned to an invented fifth fold.
- **2026:** Protected for separate confirmatory planning and explicit user release; **never use** it for discovery, architecture design, debugging, data schema exploration, quality statistics or incidental source traversal.
- These F21–F24 OOS folds were **repeatedly inspected during model development**; their intervals are **descriptive/post-search**, not pristine statistical confirmation. Later fold training may use earlier folds' calendar years legitimately; four folds are four training/evaluation lifecycles, **not four neural seeds or four independent market experiments**.

Exact boundaries, embargo, fold-row indices and label-maturity cutoffs come from **saved per-fold recipe/index files**, not these rough calendar descriptions.

### 1.4 The compact, reproducible standard LSTM (reference backbone)

| Item | Executed compact reference—check run-specific differences |
|---|---|
| LSTM | Standard shared PyTorch-style one-layer, two-bias LSTM, hidden dimension **32**, zero `(h,c)` at start of every independent 48-step window |
| FT16-only network | `48×16 → LSTM(32) → Dropout(0.10 on final hidden) → Linear(32,1)` |
| Parameters | **6,433** for plain FT16 → scalar architecture: `4·32·(16+32+2) + 33` |
| Optimization | **AdamW**, learning rate **0.001**, betas **(0.9,0.999)**, epsilon **1e-8** |
| Regularization | Weight decay **0.01 matrices**, **0 biases**; global gradient norm clip **1.0**; no recurrent dropout |
| Minibatching | **16 complete exchange sessions** per batch, retaining origins/stocks with correct weights |
| Numeric | Historical reference **CPU / float32**; exact implementation source authoritative |
| Seed | **42** for newer S1–S5/S9 fold runs; earlier C0/T2 comparison also ran **123** for limited seed-sensitivity screen |
| Selection/refit | Chronological inner training/validation **select epoch using the task-specific frozen validation rule**; then **fresh network and empty optimizer at the same specified seed**, train full eligible prefix for the selected epoch count, reload saved checkpoint, evaluate outer fold with dropout OFF |
| Loss reduction | Average valid stocks (or pairs) in origin, origins in session, sessions in role; four annual OOS results given **equal year weight** |

**Do not transplant selectors between tasks.** Original T2 and new T2R are asinh-target regression variants; **NR** is normalized-rank squared loss; **PW** is pairwise softplus/logistic; **S9-MAG** is `log1p(|raw R|/training-fitted scale)` squared loss; S9-EVENT is natural unweighted three-class CE; S9-QUANTILE is 5/50/95% asinh-target pinball. Their best/selected epochs and calibration losses are **not numerically interchangeable**. Consult each executed `configuration.json`, `calibration_binding.json` and target recipes for exact stopping rule, cutoff, scale and any deviations.

### 1.5 Primary ranking objective and controls

At each origin, compare score ordering with future raw returns (or equally ordered TG20): **ascending realized midrank 20 = best**, but a visual display may label **display rank 1 = best**; make the orientation explicit and consistent.

\[
q_{i,t}=\frac{2(r_{i,t}-1)}{19}-1,
\qquad L_{\rm NR,t}=\frac1{20}\sum_i(\hat s_{i,t}-q_{i,t})^2.
\]

**Primary statistical result**: origin Spearman IC → mean within session → mean across sessions in year → arithmetic mean of four annual ICs. Constant-score reference **N0 has undefined Spearman IC**, not zero. **N1 baseline** is the positive M1 rank; **N2 baseline** is its sign reversal; **P** is training-prefix-fitted fixed per-stock profile; **LR** is a regularized 768-input full-history linear rank predictor when available; **LP** linear-pairwise baseline did not complete due isolated optimization failure. N0 chance reference for top/bottom four of twenty is **20%**; pair concordance **50%**. A model's reported score is **not** a calibrated signed return unless formally constructed and shown so.

**Naming warning:** “N1/N2” in the *baseline* notation means **M1 momentum and reverse momentum**. “N1–N6” in the *novel architecture menu* (§5) is a **different namespace**. Always display `BASELINE-N1 (M1)` versus `ARCH-N1 (residual LSTM)` to avoid confusion.

For neural architecture promotion, require a strictly **same-task, identical-key**, appropriately simple strong comparison; per-year and equal-year IC, descriptive month-block uncertainty preserving stock cross-sections and target-overlap, top/bottom-four retrieval, pair concordance, errors and **ranking churn**. More complex encoders receiving more inputs require information-matched controls (or an explicit statement that causal attribution is unresolved). Report model size/training speed, not just accuracy.

---

## 2. Complete historical 10+3 research-question register

This was an **earlier HF20 research backlog**, **not** a requirement that all 13 items be trained again. Its evaluated roles often referred to the original long-history 2025 development sample, not the later four F21–F24 walk-forward studies. The exact question-to-experiment mapping below is from `HF20_LSTM_Comprehensive_Review_and_Expansion_Plan_2026-10-24.md` §3.4.

| Original # | Research question | What was actually done | Verdict / current disposition |
|---|---|---|---|
| **1** | C0 versus T2 replication | Standard-original-target **C0** and asinh-target **T2**, seeds 42 and 123 in earlier P020/P021 development screens | Two T2-vs-C0 gains; **seed-sensitive, not stable signed alpha**; broader replication unresolved |
| **2** | Early stopping / optimizer diagnosis | P024 and per-run training/gradient/checkpoint lifecycle checks | No universal gradient/disconnection failure shown; more audits alone not progress |
| **3** | Longer training / alternative optimization/objectives | Learning rate, dropout, weight decay, capacity/depth and other model variants | Forcing epochs or capacity not established to help; do not rerun blind |
| **4** | Tail-event classification | **E1** task: tail-event probabilities/discrimination | Development AP above pooled prior but CE worse; **S9-EVENT** later fails stock-prior proper score; event modeling reserved only with better calibration/controls |
| **5** | Tail weighting / sampling | **W1**, **SS1** | No main-ranking improvement; no priority for more generic tail reweighting |
| **6** | Rank-focused loss | Original **R1** auxiliary rank term, later S2 pure **NR** and **PW** approaches | R1 not a pure-ranking test; S2 NR weak, PW incomplete; architecture may matter more than another loss switch |
| **7** | Quantile regression | **QR1** earlier; later **S9-QUANTILE** | Earlier outer-quantile improvement over pooled control; later stock-specific quantile control marginally **better**, so no established incremental edge |
| **8** | Robust loss / transforms | Huber **H2**, asinh T2; other proposed transforms | H2 did not beat T2; log-cosh/Yeo–Johnson **not established as completed**, low priority |
| **9** | Architecture variation | A1–A8 and A12 plus P024 size/depth comparisons | Nine of 12 A-candidates screened; **A9/A10/A11 untested/paused**, not disproved |
| **10** | More historical data | Long-history P019B/P020 (~2011–2025 fitted history) | Using long history feasible; matched causal effect of additional years **not identified** |
| **A** | Is predictive information in the inputs? | Baselines, some sensitivity and read-only diagnostics | Full-information/interaction decomposition still uncertain; use strong same-info controls |
| **B** | Direction vs magnitude | DM1 earlier; S9-MAG later | **S9-MAG promising for absolute movement, not signed ranks**; separate later S9 handoff |
| **C** | Rare-event predictability before weighting | E1/QR1/W1/SS1 and later S9 tasks | Probability discrimination alone does not imply good CE or trading; remain conservative |

### 2.1 Early twenty-stock 2025 development: all named core model screens with reported results

**Do not numerically compare this table with F21–F24 annual metrics as though dates, populations and tasks were identical.** These are original **TG20 MSE** and mean daily rank IC on the earlier repeatedly inspected **2025 development set**, transcribed from the Oct-24 HF20 review, §3.1. ZERO MSE ≈ **3.116560**, ZERO IC undefined.

| Historical arm / change | Development original-TG20 MSE | Development daily IC | Interpretation at the time |
|---|---:|---:|---|
| `C0` seed 42 (original-target regression) | 3.112566 | +0.040318 | Weak reference; not established alpha |
| `T2` seed 42 (asinh-target regression) | 3.106560 | +0.075559 | Better than C0 on this development view; working reference |
| `C0` seed 123 | 3.117257 | +0.014374 | Worse MSE than ZERO |
| `T2` seed 123 | 3.114912 | +0.025493 | Better than C0/123; seed sensitive |
| `H2` Huber | 3.111709 | +0.054480 | No main improvement |
| `W1` tail reweighting | 3.108253 | +0.050782 | No main improvement |
| `R1` auxiliary rank loss | 3.106240 | +0.074718 | Very small MSE gain vs T2/42, lower IC |
| `DM1` direction/magnitude | 3.116785 | −0.000043 | Direction essentially chance |
| `SS1` importance-corrected tail sampling | 3.109769 | +0.053402 | No main improvement |
| `LRLOW` lower LR | 3.110404 | +0.071641 | No established improvement |
| `DROP0` dropout off | 3.104692 | +0.072780 | Lower MSE but IC below T2/42; not confirmed |
| `WD0` weight decay off | 3.106679 | +0.074069 | Did not help IC |
| `ES025` seed 123 stopping alteration | 3.112703 | +0.032607 | Limited point-estimate gain over T2/123; inconclusive |
| `H64` hidden width 64 | 3.107416 | +0.035428 | Larger network worse IC |
| `L2H32` two recurrent layers / hidden 32 | 3.116366 | −0.001326 | Extra depth poor |

Separate earlier task evidence: **E1** `ANY`-tail average precision ≈ **0.132** vs global-prior prevalence ≈ **0.0415**, but unweighted CE **0.2357** vs prior **0.2023**, signed ordinal IC ≈ **−0.0037**. **QR1** mean pinball **0.22608** vs unconditional pooled quantiles **0.22983** (~1.63% lower), mostly via outer quantiles, approximately 89.93% central interval coverage and weak median directional signal. Do not claim these produced reliable stock-rank alpha. `DM1` earlier magnitude-related diagnostic is not interchangeable with S9's later raw endpoint magnitude target.

---

## 3. Complete A1–A12 architecture register, with actual screen status

The A-series precedes the new N-series and must not be silently rerun or called globally novel. **Nine arms had reported 2025 development screens: A1–A8 and A12. A9, A10, A11 were *not trained* at the Oct-24 archive cutoff and no later run establishing their completion is present in supplied S1–S5/S9 reports.** Final live run ledger/source supersedes if new evidence appears. Below are the exact **reported short mechanisms and measured aggregate metrics**; more granular settings (heads, projections, ablation hyperparameters, source fingerprints, checkpoint epochs) must be recovered from individual P026–P028 run configurations before an exact replay. Do not invent them.

| Arm | Actual tested mechanism or proposed idea | Status | Development MSE / daily IC | Decision/useful information |
|---|---|---|---|---|
| **A1** | Temporal attention readout on LSTM histories | **TESTED** | 3.10630 / +0.075801 | Minuscule positive point estimates; uncertainty includes no gain; not promoted |
| **A2** | Multiscale temporal processing | **TESTED** | 3.10866 / +0.059596 | Worse than reference on key ranking metric |
| **A3** | GRU recurrent alternative | **TESTED** | 3.11474 / +0.012118 | Worse in tested protocol; not “all GRUs fail” |
| **A4** | Historical peer M1 mean/dispersion summary | **TESTED** | 3.10646 / +0.063840 | Coarse peer information somewhat useful for MSE, worse ranking; directed peer signals not ruled out |
| **A5** | Rank-four cross-stock mixer **after stock-history compression** | **TESTED** | 3.10992 / +0.049569 | Active stock exchange, but forecasts worse; not evidence all spatial mixing fails |
| **A6** | Final-state cross-stock attention | **TESTED** | 3.11263 / +0.048202 | Attention near uniform; no demonstrated selective-peer gains |
| **A7** | `MC1`: endpoint state-conditioned *feature* gate (two self-including endogenous panel summaries) | **TESTED** | 3.10571 / +0.060536 | Slight raw MSE improvement; worse transformed z-loss/rank; no external market data tested |
| **A8** | Reduced **one-way** global-8 / local-32 recurrent memory | **TESTED** | 3.10859 / +0.047244 | Global pathway active but worse ranking; does **not** test full two-way C3 |
| **A9** | Coupled specialized recurrent memories | **NOT RUN / PAUSED** | — | Distinct possible future architectural question, requires new explicit design |
| **A10** | State-dependent signed/recurrent interactions | **NOT RUN / PAUSED** | — | Prior mathematical proposal; needs feasible exact parameterization/strong simple comparator |
| **A11** | xLSTM-based recurrent cell variant | **NOT RUN / PAUSED** | — | Literature-based option, not evidence of feasibility/edge on HF20 |
| **A12** | Two **soft**, state-routed learned prediction/readout heads | **TESTED** | 3.10543 / +0.065696 | Slight raw MSE improvement, transformed loss/ranking worse; do not call it a fixed-indicator router |

**Critical negative-mechanism result, later than the original Oct-24 review:** Read-only analysis reported that **A7/A12 raw-MSE point gains were *not* attributable to improved common-level error** as earlier conjectured. Common-level error actually worsened; improved centered **extreme-target** error offset degraded ordinary-row performance, with ranking worsening. The Oct-26 architecture literature review flags this earlier conjecture as *refuted*. Do not build a new hypothesis around the now-refuted “common component improved” account.

**Information confounding:** A4 summaries are not the same input as full-history peer models A5/A6. Saved `T2/42` used **16 own-stock FT16** inputs, while A7/A8/A12 used **two additional panel-derived channels** and changed processing. No saved trained *plain 18-input* identical-information LSTM is documented; this limits architecture-only attribution. A8 was one-way market→stock, not a bidirectional global/local model; A12's experts were learned heads, not a small fixed bank of named indicator rankings.

**P028 execution context:** The earlier sequence for these screens was P027 A4–A6 → P028 Experiment 3 A7/A8/A12, with **62/200** ledger after P028. A proposed Experiment 4 (A9/A10/A11) was **not automatically executed**. Keep the previous P028 fit/failure receipts, don't roll its runs into current F21–F24 annual OOS simply because both concern HF20.

### 3.1 Original Track A **A-E0–A-E9** ladder (different from A1–A12)

The original 10-Oct five-stock `Track_A_Architecture_Experiment_Roadmap_First_Pass_FROZEN_v1.0.md` used **A-E** labels for its staged experimental *decisions*. These are not the P026–P028 **A1–A12** screens, and there is **no basis for marking the whole A-E ladder as executed on the current HF20 panel**. This additional registry preserves the historical choices for future reasoning:

| Historic node | Question or optional branch | Old plan status vs current HF20 evidence |
|---|---|---|
| **A-E0** | Data, labels, execution and zero-neural sanity | Foundational principles carried forward, **not** a separate new neural study |
| **A-E1** | Information-matched simple momentum/ridge/USA500 baselines | Analogous S1 M1/LR baselines implemented on HF20; **independent USA500 effect not identified** |
| **A-E2** | Standard stock-only shared recurrence versus cheap nonrecurrent models | C0/T2 and subsequent ranking LSTMs implement related comparison under **different later data/clock population** |
| **A-E3** | Add **genuinely available USA500** to LSTM and ridge, isolate incremental information | **Not verified as implemented on HF20**; later A7/A8 used *endogenous* panel summaries, not independently audited USA500 |
| **A-E4** | Endpoint market-conditioned **MC1** input-feature gate vs concatenation | Related HF20 A7 tested, with qualification about different source channels |
| **A-E4M** | Time-step-specific **MC2** gate, only if interval state varies | Historical *conditional* candidate, **no verified corresponding executed HF20 arm** |
| **A-E4R** | Market-state input vs gate attributable improvements | Diagnostic comparison principle; no independent market-state causal effect proven |
| **A-E5** | Same-information peer indicators before learned spatial mechanisms | HF20 A4 partial coarse-peer antecedent, not full lead–lag test |
| **A-E5L** | Directed **lagged** peer innovations and ridge first | Remains a candidate; no completed causal directed lead–lag evidence demonstrated |
| **A-E6** | One spatial mechanism **SP3** stock mixer or **SP1** attention, not every graph | HF20 A5/A6 related tests; not full original five-stock scope, do not duplicate blindly |
| **A-E6R** | Conditional market state × peer lead–lag mechanism | Historical optional hypothesis, **not verified as specifically tested** |
| **A-E7** | Temporal attention **TM1** or multi-horizon **TG2** auxiliary supervision | HF20 A1 temporal attention, S3 multiple horizon *separate training*; **does not imply joint multihead TG2 trained** |
| **A-E8** | One optional factor-aware, volatility auxiliary, regime or adaptive branch | Earlier E1/QR1/DM1 and S9 **separate tasks**, not a general A-E8 architecture execution |
| **A-E9** | Shortlist confirmation and costed reporting | **Not completed as original untouched-confirmation/strategy program**; 2026 remains locked and no net P&L claim |

The original plan also used `LL0–LL3`, `SP0/SP1/SP3`, `MC0/MC1/MC2`, `FC`, `RG` and `AD` namespaces. These are **design components**, not automatically completed experiments or additional ledger entries. Source `Consolidated_Architecture_Design_Menu.md` defines the larger alternatives. Old Track A’s proposed *five-stock* confirmation dates and costs were later superseded by the **twenty-stock F21–F24 exploratory OOS / protected-2026** policy.

---

## 4. S0–S11 research-workstream roadmap: full named family-level status

These **S-numbers are roadmap headings**, not always exact one-configuration model IDs. The user’s previously established roadmap was: `S0` protocol, `S1` baselines, `S2` ranking LSTM, `S3` horizons/origins, `S4` overnight/multiday, `S5` input quality/context, `S6` price representations/smoothing, `S7` minute information, `S8` cross-stock/factor, `S9` magnitude/distribution, `S10` robustness/loss/training, `S11` architecture revisits. They are **not** the `[S01]...` bibliography keys in the focused literature review.

| Workstream | Original purpose | Verified executed portion / status by 27 Oct 2026 | Current inference and open options |
|---|---|---|---|
| **S0** | Protocol: chronology, source/labels/benchmark discipline | **IMPLEMENTED AND REVISED** through P020, S1–S5/S9; 2026 lock remains | Live executed contracts govern; do not repeat huge audits |
| **S1** | Nonrecurrent ranking baselines | **COMPLETED WITH ISOLATED LP FAILURE/DEFERRAL** across four folds; 29 successful baseline fits reported; N0, N1/M1, N2, P, LR available as specified | Momentum competitive but weak; LP is not a zero-IC model |
| **S2** | Rank-focused shared-LSTM objectives | **12 NEURAL STARTS, 11 FINISHED, 1 FAILED** (F21 PW); T2R, NR and partial PW; ledger 62→74 | None established reliable incremental rank edge; saved true OOS forecasts exist |
| **S3** | Horizon dependence and horizon-aligned inputs | **COMPLETE**: S3-A h1/h2 comparisons retaining original M2; S3-B one-/two-hour **M2 aligned**; **32 new neural starts**, 72 non-neural attempts, ledger 74→106 | h2 M2-aligned T2R notable *paired* gain, but interval includes zero and absolute IC remains weak; don't treat as confirmatory |
| **S4** | Overnight/multiday timing and expanded origin times | **S4-A COMPLETE** (seven candidate hourly origins, same 4 trading-hour horizon; includes eligible overnight-crossing); 8 new starts, ledger 106→114. **S4-B dropped/unrun** | No robust model-over-M1 ranking gain; overnight differences descriptive; don't auto-implement long holding strategies |
| **S5** | Causal input quality and timing/context | **COMPLETE LIMITED VERSION:** 6 verified clock channels, *not unverified historical age/quality flags*, 4 META-T2R starts, ledger part of 114→130 | Δ IC small, inconclusive; no isolated causal missingness mechanism was tested |
| **S6** | Alternative price representation / smoothing | **NOT ESTABLISHED AS A COMPLETED S6 EMPIRICAL CAMPAIGN** in supplied reports | Could revisit only if specific representation hypothesis; smoothing not guaranteed useful |
| **S7** | Minute-level history/information or minute→hour encoder | **NOT RUN as S7** in supplied reports | High information/compute/source burden; no automatic authorization; existing minute data not additional independent labels |
| **S8** | Cross-stock/factor information / structure | **NOT RUN as S8 annual-fold workstream**; earlier A4–A8/P028 exploratory peer/panel screens *are relevant antecedents* | N2/N3/N5 may study bounded variants with matched-information controls |
| **S9** | Magnitude and distributional future outcomes | **COMPLETE:** MAG, EVENT, QUANTILE; 12 starts; 4 years each, ledger part of 114→130 | MAG promising magnitude, EVENT and QUANTILE fail stock-specific proper controls; separate option work later |
| **S10** | Robustness, objective, loss, training and sampling follow-ups | **NOT RUN as a separate S10 campaign**; earlier 10+3, P024/H2/W1/SS1 and fold diagnostics partially address topics | No blanket search; seed robustness and real confirmation still unresolved |
| **S11** | Structured/novel architecture revisits | **NEXT RESEARCH PHASE, NOT YET RUN** | N1–N6 literature menu, plus reserved A9–A11; choose one first, not an all-design campaign |

**Terminology caution:** `S3-A/S3-B` and `S4-A/S4-B` are actual subarm names, whereas the original terse `S3`/`S4` roadmap headings can be broader. Likewise `S9-A/B/C` corresponds to MAG/EVENT/QUANTILE. The above is a **complete named roadmap-family registry**, *not* a fabricated list of every possible combination or every one of the 130 start IDs. For start-level completeness, read the live run ledger and package indices (§9).

### 4.1 Neural ledger timeline — reconcile to actual registry before each new job

| Phase | Cumulative starts | New starts | Completion/failure interpretation |
|---|---:|---:|---|
| Early P020–P028 and previous core screens | **62/200** | Earlier 62 cumulative | Multiple model families on earlier 2025 development; this handoff does not claim to reconstruct every one of those 62 individual start IDs |
| S1/S2 | **74/200** | **12** | 11 completed; **F21 PW failed**, preserved as charged; S1 baselines count separately |
| S3-A and S3-B | **106/200** | **32** | 32/32 completed; no new neural failures/retries |
| S4-A | **114/200** | **8** | NR and T2R × 4 annual folds, 8/8 completed |
| S5 + S9 | **130/200** | **16** | S5 META-T2R ×4; S9 MAG/EVENT/QUANTILE ×4 each; 16/16 completed, zero retries |
| **Remaining** | **70 potentially available** | **not assigned** | Live ledger may override; free budget ≠ authorization |

**Operational rule:** A model trained for four outer folds typically consumes **four** neural starts, one per annual fold, *not four seeds*. A full matched two-arm architecture experiment could be eight new starts if both arms require training. Comparisons against frozen saved controls may avoid new training **only if exact input, target, eligibility, fitting chronology and output comparability are supported**.

---

## 5. Four-fold S1–S5/S9 results: what worked, failed or deserves revisiting

### 5.1 S1/S2: the signed-ranking reference

For the original S1/S2 four-hour **two-morning-origin** populations, equal-year primary daily Rank IC (2021–2024):

| Model | Equal-year Rank IC | Interpretation |
|---|---:|---|
| `N1 = M1` positive momentum | **+0.0117255** | Strongest of this listed set, but tiny and no proved economic edge |
| `T2R` stockwise LSTM trained on asinh TG20 | **+0.0076733** | Weak; below momentum |
| `LR` pooled regularized rank regression | **+0.0060425** | Cheap full-history linear comparator; under momentum |
| `NR` stockwise LSTM trained on normalized ranks | **+0.0023695** | No demonstrated advantage |
| `P` fitted stock identity profile | **+0.0006351** | Weak overall, unstable |
| `PW` stockwise LSTM pairwise-loss variant | **F21 missing due failure** | In the three evaluable years, reported to trail T2R; no four-year estimate |
| `N0` constant reference | **undefined IC** | Random top4 expectation 20%; pair concordance 50% |

S1-LP pairwise linear model was **deferred after a distinct solver/numerical failure** and has no legitimate completed OOS score. The numerical training/selector settings for F21–F24 must be recovered from saved runs; the prior S1/S2 design and continuation prompts explain what was approved. These S1/S2 models do not receive S4’s additional forecast slots automatically.

### 5.2 S3: shorter horizons and M2 alignment

- **S3-A**, original historical M2: on strictly common evaluation keys, `T2R` IC for h1/h2/h4 **+0.007222 / −0.000707 / +0.014836**, and NR **+0.008443 / +0.005232 / +0.010354**. The full h4 measures here are **common-key slices**, not necessarily the primary S2 h4 population.
- **S3-B** changed *only* M2 to align its historical lookback to the h1/h2 target. **h2 T2R** had *paired B−A* primary IC change **+0.015958**, interval **[−0.000770,+0.029417]** (400 whole-month descriptive replicates) with positive changes in all four years. Its *absolute* primary IC rose only to **+0.004283**, still below h2 `BASELINE-N1=M1` **+0.006269** and profile P **+0.009499**.
- The h2 bottom-four selection/retrieval reportedly improved about **19.75%→21.86%** (chance expectation 20%), possibly suggesting asymmetric weaker-stock identification. This is **exploratory**, not robust short alpha.
- Other S3-B h1/h2 NR/T2R matched effects are mixed; **all** B−A IC descriptive intervals include zero. Lower transformed loss versus original-scale errors must not be confused. **No h1/h2 architecture follow-up automatically approved.**

### 5.3 S4-A: seven origins, same h4, overnight crossing

**8/8 technical PASS**, four folds × (`T2R`, `NR`), common full 4,013-origin OOS population, no same-task LR trained in S4.

| OOS ranking model | Equal-year daily IC | Top-four retrieval | Pair concordance |
|---|---:|---:|---:|
| `BASELINE-N1` M1 | **+0.003383** | 21.49% | 50.13% |
| `S4 T2R` | **+0.005921** | 23.01% | 50.19% |
| `S4 NR` | **+0.003818** | 21.70% | 50.17% |
| `P` stock profile | **−0.000754** | 23.59% | 49.96% |
| `N0` | undefined | 20% reference | 50% reference |

Paired IC changes versus M1: `S4 T2R − N1` **+0.002538 [−0.015288,+0.016970]**; `S4 NR − N1` **+0.000435 [−0.017690,+0.014300]**. Thus **no established incremental ranking edge**. T2R annual IC: 2021 +0.015205, 2022 +0.016148, 2023 +0.004172, **2024 −0.011840**. NR yearly: 2021 −0.005321, 2022 +0.010599, 2023 +0.009055, 2024 +0.000940. The T2R/NR “winner” depends on year and metric.

Useful model-behavior observations: adjacent intra-session top-four Jaccard **0.597 T2R / 0.545 NR**; mean rank change **2.44 T2R / 2.76 NR** between eligible adjacent forecasts. Thus predictions have persistence, **not demonstrated accuracy or profit**. Overnight-minus-intraday paired contrasts overlap zero; NR overnight +0.005461 vs intraday −0.002034 and T2R overnight +0.002770 vs intraday +0.006748 are descriptive category means, *not* an overnight advantage proof. Training/validation IC generally exceeds actual OOS IC in several runs; nonstationarity/overfitting are possible, **not proven sole causes**.

**S4 refit-epoch identity (for exact historical configuration tracking):** Saved S4 selected epochs by year F21/F22/F23/F24 were **NR = 4, 1, 3, 7** and **T2R = 3, 2, 28, 13**. For F23 T2R raw-best calibration epoch was **35**, but the frozen qualifying-improvement rule selected **28**. These describe four independent fold fit/refit histories for each objective, not a hyperparameter search over OOS years. The executed model source/calibration bindings take precedence over this summary.

### 5.4 S5: extra causal metadata channels

Four `S5 META-T2R` fold lifecycles succeeded; **six verified clock channels** appended, **no unverified historical quality/observation-age flags appended**. Equal-year OOS daily Rank IC **+0.008904**, vs saved S4-T2R **+0.005921**; matched Δ **+0.002983 [−0.010230,+0.014905]**, positive in **3/4** years. **INCONCLUSIVE**; this tests the *training-with-clock package*, not a separately identified missingness effect or evidence of a market-state regime mechanism. Do not infer N4 dual-clock memory will therefore help or fail.

### 5.5 S9: three separate *different-target* LSTM studies (not rank comparisons)

All use original S4 **FT16 only**, 48 steps, hidden32 one-layer, 4h seven origins, seed42, each with four folds. They **do not** use S5's six clock channels. The neural campaign had **16/16 passes total S5+S9**, 32 prefix recipes and 64 recorded task-control outputs/receipts (some controls are parameter-free); ledger 114→130.

| Study | Four-year OOS actual loss, matched comparator | Outcome | Status |
|---|---|---|---|
| **S9-MAG** raw endpoint `|R^{(4)}|`, `log1p(|R|/s)` MSE | Model **0.232454** vs stock-specific constant **0.269383**; difference **−0.036929 [−0.042946,−0.031723]**, **13.7% lower**, better all 4 years | Raw `|R|` MAE **0.006505** vs stock **0.006903** (~5.8% lower); size-rank association **0.408** | **PROMISING/QUALIFIED**, exploratory, undercalibrated |
| **S9-MAG** vs trailing-volatility-based control | Difference **−0.035812 [−0.040886,−0.031409]**, **13.3% lower**, all 4 years | Same MAG trained network, not an extra architecture/seed | **PROMISING**, same statistical caveats |
| **S9-EVENT** original E1-compatible 3-class, natural unweighted cross entropy | Model **0.202028** vs stock-prior **0.196030**; model worse **+0.005998 [+0.002984,+0.009021]** in all 4 years | `ANY` AP **0.1442** vs stock prior **0.1493**; pooled-prior advantage alone insufficient | **NO incremental edge** |
| **S9-QUANTILE** signed TG20 transformed 5/50/95% pinball | Model **0.230705** vs stock quantiles **0.230242**; model worse **+0.000464 [+0.000035,+0.000914]** in 3/4 years | 90% interval coverage **91.86%** vs stock-control **90.03%**, with wider transformed intervals | **NO incremental edge** |

**S9-MAG calibration warning:** mean displayed model magnitude **0.00836**, mean realized **0.01031**; it underpredicts many extremes. The one-time inverse of its transformed conditional-mean forecast is **not guaranteed** to be the true conditional mean `E[|R| | X]` by Jensen. Four-hour **absolute endpoint movement is not realized intrapath variance** and carries no predicted return sign. Strong forecast MSE by itself is **not** an options mispricing or straddle-P&L claim. All twenty stocks were reportedly improved by mean proper MAG loss after equal-year aggregation; this is a concentration check, **not twenty independent confirmations**.

For exact S9 magnitude target scale formula, selected epochs (F21 **27**, F22 **20**, F23 **41**, F24 **27**), control semantics, stock-specific baseline and file maps, consult the separate `HF20_S9_MAG_LSTM_to_Options_Strategy_Research_Handoff_2026-10-27.md`; don't transplant those scales or epoch selectors to a signed-rank experiment.

### 5.5a S9-MAG exact executed task/controls/training (new replication-quality supplement)

**This is a distinct magnitude task**, not an improvement to directional ranking. It uses original 48×16 S4 tensors, shared one-layer H32 LSTM, final hidden state with dropout 0.10, scalar head (6,433 parameters), seed42, CPU/FP32, AdamW lr0.001/betas0.9/0.999/eps1e−8, decay0.01 on matrix weights only, gradient norm cap1.0, and 16 complete sessions per batch. `torch==2.10.0` with default parameter initialization and deterministic algorithms. No ticker ID, cross-stock communication, S5 clock metadata, learning rate schedule or recurrent dropout.

**Target:** $R=\log(P_{exit}/P_{entry})$, $A=|R|$ on true four-trading-hour endpoints. Fit $s=\max(Q^w_{0.5}(A),10^{-8})$ as the **earlier-role weighted median**, and minimize $(\widehat m-\log(1+A/s))^2$; this is **not TG20/asinh and not squared raw magnitude**. Display raw magnitude as $s\operatorname{expm1}(\max(\widehat m,0))$, clamped **at decoding only**; it is not proven to estimate conditional $E[|R|\mid X]$.

| Fold | Inner $s$ | Refit $s$ | Selected refit epochs | OOS MAG transformed MSE | STOCK MSE | VOL MSE |
|---|---:|---:|---:|---:|---:|---:|
| F21 | .005797117684325846 | .0058994931438253 | 27 | .2227765003 | .2614438622 | .2599329620 |
| F22 | .0059347355198145265 | .005957669984582455 | 20 | .2792002367 | .3487977529 | .3187140675 |
| F23 | .0060897938914411046 | .006150424755601047 | 41 | .2088574693 | .2269527907 | .2449411506 |
| F24 | .006174065175292481 | .0061703009229596 | 27 | .2189824305 | .2403389347 | .2494764070 |

**MAG baselines:** `GLOBAL` is a prefix-fitted **one-pool** transformed-$m$ mean; `STOCK` is **20 separately prefix-fitted transformed-$m$ means**; `VOL` is **not fitted**. It decodes the already scaled/imputed latest FT16 `V2` with $\sigma=\exp(V2^{scaled}s_{V2}+c_{V2})$ and predicts $\widehat m_{VOL}=\log(1+2\sqrt{2/\pi}\,\sigma/s)$. Thus `VOL` decoded raw magnitude is $2\sqrt{2/\pi}\sigma$, with $\sigma$ **hourly OC RMS60**, not close-to-close or EWMA volatility. Saved `*_VOL_control.json` files are `{}`; all comparisons use matched OOS keys/weights.

**Exact MAG epoch selector:** First finite nonnegative inner-validation proper loss qualifies. Later loss qualifies only if `L <= 0.999*best_qualified_loss`. Stop at epoch≥12 after ten nonqualified epochs or max60, logging raw minimum separately. Freshly reset seed/model/optimizer for full earlier-prefix refit selected epoch count; do not fine-tune the calibration checkpoint. Shuffle sessions each epoch $n$ via `np.random.default_rng(42+n)` before 16-session batches. Use dropout off for calibration metric and OOS; real role metric reduction is equal-session, within-day equal-origin, then within-origin equal-stock. Exact S9 checkpoint/initialization binding IDs and all 4×20 saved STOCK means appear in Part III Annex B.

**Historical benchmark:** MAG equal-year transformed-MSE **0.232454** versus STOCK **0.269383** (13.7% lower), and VOL **0.268266** (13.3% lower), both better in four years; MAG raw `|R|` MAE **0.006505** versus STOCK **0.006903** (5.8% lower) and VOL **0.006992**. Magnitude rank association **0.408**; raw mean forecast **0.00836** vs observed **0.01031**. Correct breadth: **78/80** stock-year MAG-vs-STOCK improvements (exceptions PEP2023, MRK2024), **80/80** vs VOL. These four research years are **already repeatedly inspected**; no confirmatory trading significance is established.

**Original execution support (all roles):** `F21` inner 2100 sessions/11449 origins, validation 120/674, refit 2227/12171, OOS 188/955; `F22` 2331/12716, 92/457, 2423/13173, 210/1180; `F23` 2547/13896, 86/453, 2640/14395, 187/887; `F24` 2740/14945, 87/350, 2835/15332, 208/991. All 20 stocks per admitted origin; first OOS session dates 2021-01-13, 2022-01-12, 2023-01-13, 2024-01-11. Training starts 2011-04-01. Nominal last-six-calendar-month inner validation and a **48-scheduled-full-hour input embargo**, plus conservative label-maturity cutoff, determine actual role indices. Exact code/role indices preserved in Part III.


### 5.6 Overall interpretation that motivates new architectures

**There is no convincing stable four-year incremental stock-ranking alpha from ordinary shared LSTMs compared with strong inexpensive controls.** Yet nontrivial history-dependent magnitude prediction **does** appear possible within the same FT16 backbone. This does **not** prove that there is latent directional alpha recoverable by a more complicated recurrent cell. The scientific question is which *restriction*—indicator anchoring, dynamic indicator combination, common/local interaction, elapsed-time awareness, selective peer memory or pairwise context—might help estimate weak conditional *relative* returns while controlling variance and avoiding spurious inference.

The user's ultimate goal is an LSTM-based trading system, but **this architecture phase tests forecasting**, not trading P&L. No existing model should be called profitable until a later correctly timed, costed strategy study supports that claim.

---

## 6. Novel architecture candidates N1–N6 — research menu, not a fit grid

**Primary source:** `HF20_LSTM_Architecture_Literature_Review_and_Research_Proposals_2026-10-26.md`, §§4–9 for the full mathematical specifications, §§10–11 for selection/discipline, §§12–13 for primary literature and provenance. Additional older ideas: `Recurrent_Architecture_Research.md`, `State_Dependent_Signed_Recurrent_Interactions.md`, `Consolidated_Architecture_Design_Menu.md`. The N-series labels describe **proposed designs, not trained evidence**, and the source explicitly makes **no claim of global architectural novelty**.

| Novel arm | Concrete testable restriction | Main reason/closest earlier negative experiment | Cheapest decisive comparator and mechanism check | Initial priority |
|---|---|---|---|---|
| **ARCH-N1** indicator-anchored residual LSTM | Anchor score to `M1`, learn small **cross-section-centered recurrent correction** | Strong simple M1; standalone T2R/NR rarely add; R1 was merely auxiliary ranking loss | M1 + **linear residual correction** (and cheap nonrecurrent same-history correction if needed); zero correction = M1, count wrongly/correctly reversed pairs | **Preferred first practical test** |
| **ARCH-N2** global-to-stock indicator router | Recurrently set nonnegative weights on **3–5 predeclared, comparable-scale indicator rankings**, initially one global gate; local deviations only later | A7 gated features, A12 routed learned heads; *neither* tested adaptive mixing of fixed indicator rankings | Individual indicators, fixed mixture and small nonrecurrent state-conditioned gate; uniform/fixed mixture, expert disagreement | Conditional next |
| **ARCH-N3** two-stream centered factor-style interaction | Separate stock and causal global-state LSTMs, couple via centered low-rank loadings `β_i−β̄` times forecast common factors | A8 was one-way global→local recurrent and worse; **not** a test of centered late interaction | Same-input one-stream LSTM + simple late fusion; common additive offset null, rank-changing heterogeneous effects | Conditional next |
| **ARCH-N4** dual trading-clock / age-aware recurrent memory | Explicit elapsed open/closed-market time and *verified contemporaneous* missingness/age; learned constrained memory decay | S5 six clocks gave inconclusive score gain; **S5 did not test new recurrent memory or verified age masks** | Ordinary LSTM using **identical clocks/masks/ages**; zero decay should recover that control | High if real causal metadata exists |
| **ARCH-N5** contrast-centered lagged peer attention | LSTM historical states of other stocks at **selected lags**; centered peer values make uniform-peer attention contribute zero | A5/A6 saw final-state exchange, A6 attention ~uniform; selective earlier peer innovations not tested | Fixed lagged peer linear/aggregation model with **same information**; zero correction for uniform attention | Exploratory, later |
| **ARCH-N6** antisymmetric pair comparator + expected-rank aggregation | Shared LSTM encoders with context-dependent comparator `p_ij`, enforce `p_ji=1−p_ij`; score by predicted expected wins | Old PW used scalar score differences, F21 failed; nontransitive pair patterns may require richer comparator | Same-loss scalar PW and small static comparator; symmetry and expected-rank sum tests | Exploratory, later |

### 6.1 Core formulas and scientific traps

**N1 (recommended first discussion, not authorized yet):** Let `B_{i,t}` be normalized M1 rank and `γ>0` a *predeclared or inner-prefix-fitted* scale. Let `u_{i,t}=wᵀh_{i,t}`, and `δ_{i,t}=u_{i,t}−mean_j u_{j,t}`. Predict

\[
\boxed{s_{i,t}=\gamma B_{i,t}+\delta_{i,t}.}
\]

Zero initialize the correction readout to recover the M1 score at initialization; the LSTM itself must not be all-zero. Compare the **combined rank model** to a supervised **linear correction of the same M1 anchor** (not just M1 alone). Small baseline-score differences may be statistically unreliable; `γ` is part of the *scientific treatment* and must not be chosen from final OOS. Report **M1 wrong pairs corrected versus correct pairs broken** and correction amplitude. The optional indicator-orthogonal projection is a **later** ablation, not a necessary first fit.

**N2:** With fixed comparable indicator scores `b_{ik,t}` and normalized nonnegative common weights `w_{k,t}` from a small global-state LSTM, `s_{i,t}=Σ_kw_{k,t}b_{ik,t}`. This **cannot reverse** a pair that every expert agrees on. Dynamic indicator weighting is already present in literature; success is an empirical restriction result, not invention of mixture-of-experts.

**N3:** With local `h_{i,t}` and global `g_t` and small rank `K`, `s_i=uᵀh_i +(Bh_i−mean_j Bh_j)ᵀ A g_t`. A *common scalar shift* changes no stock ranks; the heterogeneous low-rank term can. Endogenous panel averages are not independent USA500 or independently observed macro factors. The sign of an unidentifiable latent factor is not a causal interpretation.

**N4:** Treat normal hourly transitions and closed-session gaps differently, with **information-available** masks/ages, not the retrospective data-audit knowledge. The same-feature ordinary LSTM comparator is mandatory or new information is confounded with memory architecture.

**N5:** A6's nearly uniform final-state attention does not refute lag-specific peer information. Center the peer-value path so *uniform within-lag peer weighting* has a zero correction. Check actual *change to relative rankings*, not attention entropy alone. No full stock×time Transformer needed initially.

**N6:** For 20 securities there are 190 unordered pairs per origin, **not 190 independent market observations**. Anti-symmetric logits give complementary pair probabilities; expected rank combines those probabilities. The comparator class is not a new loss synonym and has close nonfinancial prior art.

### 6.2 Recommended experimental ordering—not a commitment

1. **First study ARCH-N1**, because it directly asks whether the LSTM can **add to M1**, rather than replace it. Freeze one ranking objective and anchor scale; use the existing S4 h4 seven-origin F21–F24 reference unless a separate compelling scientific reason changes that population. The N1 literature design includes controls and a tractable null.
2. Alternatively, **ARCH-N4 first** only if sufficient *causally verified* time/observation-age metadata exists. S5's six clocks alone are not a sufficient age-quality audit.
3. **Choose ARCH-N2 basic or ARCH-N3** according to evidence of indicator complementarity or useful causal global state; do not run both automatically.
4. Consider **N5/N6** only when simpler mechanisms cannot address a documented limitation, or when a small, bounded hypothesis makes them worthwhile.
5. A9–A11 remain in the reserve library; they are **not** compulsory outstanding tasks and are not new merely because left unrun.

The receiving chat should **read the exact N-series primary report** before producing architecture code. The table above is a quick decision map, *not* an exhaustive specification of layer dimensions or all optimizers for unimplemented models. Cite recent finance papers and distinguish primary-paper designs from our adapted hypotheses.

---

## 7. BINDING engineering, testing, inference and operational protocol for new Codex prompts

### 7.1 Mandatory lean-engineering constraints—enforce as prohibitions

**The user has repeatedly objected to excessive engineering time.** Prior stages spent hours on source reconstruction and serial lifecycle ceremonies, logged **89,187** per-batch updates and **535,122** nonzero gradient records in the S5/S9 campaign, and verified dozens/hundreds of hashes per fold despite requests to reduce overhead. Those are historical outputs, **not a specification to repeat**.

**Every next Codex prompt MUST:**

- **Reuse existing P019B/P020/FT16/S4/S5/S9** windowing, fitted recipes, folds, optimizer, score exports, metric reducers, plots, and the **existing working project dashboard** if visualization is needed. No unnecessary rewrites or new dashboard HTML clone.
- **No dataset copying:** Use indexed/shared source and windows. Do **not** replicate multi-GB minute or hourly datasets per fold/run, or silently create another tens-of-GB experiment cache. Historical duplicate storage in another project was a serious issue.
- **No generalized orchestration/research frameworks**: no new experiment scheduler, stage-gating engine, generalized plugin architecture, web server, data warehouse, gigantic manifest forest, or elaborate QA harness when the existing code runs.
- **No per-parameter, per-batch, per-file forensic recording by default:** Save short epoch-level training/validation traces, a few aggregate gradient-norm/clip/update summaries sufficient to catch vanishing/nonfinite gradients, selected epoch and checkpoint identity, key OOS scores/labels, a concise reproducibility manifest, one human-readable decision report and useful plots. Full batch traces **only when investigating a concrete failure**, not as a precondition for every successful run.
- **No hundreds of hash proofs/receipts:** Verify a small set of essential source, target, fold, configuration and saved-checkpoint fingerprints once per campaign (and compare exact keys/metrics where needed), not per-file hash traversal and repetitive independent gate checks. Preserve originals, but do not rehearse full run lifecycle multiple times.
- **Do not serialize science through oversized postfit gate ceremonies.** One lightweight preflight before the approved campaign, independent minimal checks at model export, and a consolidated final verification are enough. A localized scientific failure blocks the affected arm; unrelated valid work should proceed if safe. Do not wait for a complete audit monograph after each year to run the next preauthorized fold.
- **No automatic repetitions, retries, hyperparameter grids or seed sweeps.** A negative IC is a valid research result; log and stop at scope. If a model legitimately fails numerical convergence, preserve the failed attempt and count its neural start; do not silently change solver or training budget.
- **Control runtime/storage proactively:** State a concrete upper bound for new neural starts (typically **4** for one candidate/four folds; **8** if its comparator also needs fitting), how many **nonneural** baseline fits, expected memory and artifact footprint, and conditions for a hard stop. The previously discussed **2 GB RAM**, **2.5 GB task artifacts**, **15 GB whole project** are *historical operational caps*—confirm the live limits, don't invent entitlements. Track actual disk usage, not number of receipts.
- **Treat this as a quant-research/CV project**, not enterprise deployment. Prefer interpretable questions, credible baselines and finished, readable science to extensive infrastructure or aesthetic complexity.

**Minimum output package for one new architecture** (reuse existing directory conventions; names illustrative, not a new folder mandate): one readable `DESIGN_AND_DECISION.md`; one concise `METRICS.csv` containing each fold/role and baselines; `OOS_SCORES.parquet` or reference to already saved actual scores; compact epoch summary `TRAINING.csv`; one or a few relevant visual panels and *one* verification note. **Do not require 22 source examples × role × model, 16 PNGs, per-epoch checkpoint files, massive cohort tables or exhaustive bootstrap grids** unless a specific scientific failure merits them. Existing old artifacts remain accessible and unchanged.

### 7.2 Absolutely non-negotiable scientific correctness tests

Being lightweight is **not** permission for leakage or invalid numerical claims. Retain focused, deterministic and inexpensive tests for:

1. **Time and source availability:** no input/gate/peer datum at or after a forecast cutoff that wasn't legitimately available; actual label endpoints; real trading-minute calendar incl. 09:30 and closing stub/overnight; genuine maturity/embargo; no protected year.
2. **Folds and transforms:** exact F21–F24 cutoff/key identity, no OOS fitting/tuning, phase-fitted robust scale/fallback/target thresholds and correctly fixed seeds; never fit controls on OOS. For a changed information set, show accurate matched-key join and source coverage.
3. **Correct mathematical loss/score:** tie-aware midrank, pair softplus orientation, effective session/origin/stock weights, genuine optimized loss on actual rows, correct logits/quantiles/units and once-only inverse where valid; **do not apply sinh to ordinal rank scores**.
4. **Run integrity:** checkpoint selected using **inner validation**, actual optimizer updates (not fake training), finite gradients and losses, independent fresh refit, deterministic reload/inference consistency, actual ledger starts and failed attempts preserved; one or two targeted numerical fixtures are enough to check a new architecture's algebraic null.
5. **Matched evaluation:** when saying “architecture helps,” same horizon, target, FT16 and allowed context, same outer keys and weights, same model-selection information; compare performance year by year and on existing strong baselines. If control has less information or greater/smaller capacity, label the claim appropriately.
6. **Meaningful mechanism diagnostic:** e.g. residual pairs corrected/broken, router weights across disagreement, heterogeneous common-state rank effect, real metadata decays, contrast-attention vs uniform null, or pair-comparator consistency. **Gradient-connected ≠ predictive.**

Compute **actual optimized loss shares** for large-original-outcome tails and ordinary complements when relevant, rather than misleading “extreme domination” from a different loss. Keep `TG20 NUM/MAD/epsilon`, positive/negative and source-quality cohort definitions, all eligible cases (no ex-post trimming) and a short summary; do **not** automatically create hundreds of per-cohort files. Preserve full saved predictions for later read-only diagnostic expansion.

### 7.3 Evaluation, statistics and promotion language

- **Primary metric:** equal-year daily within-origin Spearman Rank IC; include annual IC and matched M1/S4 baseline differences. Secondary: top/bottom 4 retrieval, pairwise concordance, signed and absolute rank error, forecast-spread/tie diagnostics and **top4 churn / ranking stability**.
- **Descriptive uncertainty:** Resample whole calendar months *within year* (or an equivalent dependency-aware block) keeping same-session origins and 20-stock cross-sections intact; overlap, cross-stock common shocks and four folds' changing training sets violate naive i.i.d. row/bootstrap assumptions. Existing S4 used 400 month-resamples seed 22042; using a saved routine avoids building a new inference engine. Intervals are **not confirmatory p-values** after repeated research.
- **Separate TECHNICAL PASS from SCIENTIFIC EDGE.** Scientific labels: `SUPPORTED/QUALIFIED/INCONCLUSIVE/NO_EDGE`, with exact comparator and uncertainty. No success from “model converged,” nonzero gradients, more variance, lower *unrelated* loss, visually pretty charts, or cherry-picked subgroups.
- **No portfolio or options claims.** Future costed positions, borrow, funding, transaction prices, option premiums, execution and thresholds need their own study. Scoring the old label is not a fill-time profit backtest.
- **No results-based sample exclusions or rescues.** Keep every source-eligible stock/origin/label, including large shocks and unfavorable years. Any required source-eligibility differences are documented and matched where possible, never forced by peeking at realized returns.
- **Research budget accounting:** All actual neural optimizer-started pairs count, including failures; **baseline fits are distinct**. The cumulative counter **130/200** is reported, **not license** to consume 70. No automatic access to 2026, extra seeds, feature families, labels, source vendors, universe expansion, roll/refit regimes or other N-series after a positive/negative result.

### 7.4 Coding/working-repository safety and review

- Inspect `AGENTS.md` and the repository's current instructions first; follow existing credentials, path, data-privacy, reproducibility and Git policies. **Never print or store API credentials, vendor tokens or secret values.** Avoid raw data export to chat or commit.
- Preserve original reports, target/feature source maps, protected files, failed-run logs, checkpoints and uncommitted user work. No force reset, stash, destructive rename, broad cleanup, automatic commit/push or publication.
- Before altering source, identify and name exactly what the new design changes; avoid accidental changes to shared FT16, M2, TG20, origin clocks or previous models. Existing files remain canonical; the new model should be a minimal isolated variant.
- Keep a short session report: edited files, actual starts, outputs, known blockers, exact result paths and remaining budget. No giant reporting matrix.
- Where an old approved plan explicitly required a more complex gate, treat that as **historical scope** unless live repository policy still demands it. If a genuinely mandatory current gate cannot be met, explain the smallest blocker and request a targeted decision instead of manufacturing approval.

---

## 8. Protocol for the receiving chat: first conversation and first candidate

**Do not jump straight to code.** The next architecture-design conversation should proceed in this order:

1. **Read and reconcile** §9 source files and the live repository; verify exact FT16 names/formulas/scales, eligible origins, S4 and S5 scored keys, actual training recipe/checkpoints, current ledger and current disk/resources. Verify that the two already-visible dashboards need **no work**. List only material conflicts; do not dump thousands of filenames.
2. **Present a one-page experiment choice**: ARCH-N1 (default preferred) versus one alternative supported by the evidence. State the *precise limitation* being tested, what new structure changes, what baseline information/capacity is matched, the mathematical loss, and what a null result would mean. Ask the user to select/approve **one** choice; do not implement all menus automatically.
3. **Freeze exact training design before any OOS-dependent change:** single target and price-origin/endpoint definition, seven origins on S4 keys (unless separately approved), 48 FT16, input availability, F21–F24 inner rules, seed42, hidden32 reference or justified small width allocation, dropout/AdamW/decay/clip, target/selector, predicted output interpretation. Define **one primary matched comparator**, one essential mechanism null and only one targeted ablation if truly needed.
4. **Show an engineering budget with the fit card:** total neural starts (typically four candidate starts, perhaps four matched new-control starts), nonneural fits, minimal files, resource bound, tests, no 2026 reads and **no dashboard rebuild**. A negative result is still “finished.” Obtain **one explicit user approval**; then Codex can execute the bounded campaign without repeated routine human review prompts.
5. **Run and evaluate:** preflight source/label/test fixture → four chronological fold fits (or only agreed scope) → saved OOS scores → primary/secondary matched metrics and read-only diagnostic plots → compact scientific decision. Keep results intact; **stop** after approved work. Do not take the best-performing architecture and automatically move on to the next proposal.
6. **After the scientific report**, discuss whether a second seed, an alternative architecture (N2/N3/N4), or broad stock universe is justified and separately approved. The S9-MAG-to-options strategy remains another chat.

**Suggested first-hypothesis template** (draft **only**, not live execution authorization):

> Can a shared, 48-step FT16 width-32 LSTM produce **cross-section-centered corrections to a fixed M1 ranking** that improve four-hour F21–F24 OOS IC over both M1 and a **linear residual correction**, with a justified rank-correction mechanism and no increase in information set? Freeze the baseline scaling/regularization/epoch selector on inner data; use S4 seven-origin population and all stocks; count corrected vs broken M1 pairs, IC by year, top/bottom-four, churn and descriptive whole-month paired uncertainty. Four candidate neural starts, one seed, no feature/target changes, no extra training without approval.

A correct negative conclusion might be “the LSTM corrections mostly broke correct M1 pairs; the nonrecurrent correction performed similarly,” not “LSTM universally cannot rank stocks.” A positive result must exceed a *strong simpler anchor-control* consistently enough to deserve additional seed/period confirmation; a tiny OOS IC gain with intervals covering zero is not a promoted edge.

---

## 9. File map and exact missing data needed for a fully reproducible numerical replay

### 9.1 Project documents available for reading in the new chat

**Core background and originally agreed protocols** (typically project-file attachments):

- `Shared_Project_Specification.md` — original shared Track A/Track B conventions; read for common boundaries, **not** to overwrite current HF20 implementation.
- `Track_A_Architecture_Experiment_Roadmap_First_Pass_FROZEN_v1.0.md` — frozen older **A-E0–A-E9** five-stock first-pass ladder; useful prior menu, not automatically executed HF20 experiment IDs.
- `Track_A_Consolidated_Implementation_Design_Record_v1.2_2026-10-10.md` — original five-stock detailed decisions and conditionals; may be superseded.
- `Track_A_Codex_Incremental_Implementation_and_Human_Review_Plan_v1_2026-10-10.md`, `Track_A_Stage_Gated_Audit_and_Failure_Traceability_Plan_v1.1_2026-10-10.md` — **historical engineering/control proposals**; science-critical principles persist, but do **not** import their whole G0–G9 ceremony into new HF20 work.
- `Consolidated_Architecture_Design_Menu.md`, `Recurrent_Architecture_Research.md`, `State_Dependent_Signed_Recurrent_Interactions.md` — full cross-stock, factor, temporal, regime and recurrent interactions idea inventory.
- `Modern_Quant_DL_Papers_2023_2026.md` and `LST_Proposal.pdf` — background research/course concept, not an executed data recipe.

**Twenty-stock scientific audits and decisions** (date suffixes matter):

- `HF20_LSTM_Comprehensive_Review_and_Expansion_Plan_2026-10-24.md` — **earlier 10+3, core 2025 development screens, A1–A12** registry, data/source limitations and twenty-stock adequacy discussion.
- `HF20_Focused_Second_Pass_Ranking_Inputs_Minute_Data_and_Horizons_2026-10-24.md` — ranking targets, minute-data/clock and representation ideas.
- `HF20_Ranking_First_Experiment_Design_Record_v0.1_2026-10-25.md` — S1/S2 original reference proposal, not on its own final execution authority.
- `HF20_S1_S2_Staged_Ranking_Baselines_and_LSTM_Codex_Prompt_2026-10-25.md` and `HF20_S1_S2_Resume_After_LP_Failure_All_12_LSTM_Fits_Codex_Prompt_2026-10-25.md` — original and revised executed-scope instructions.
- `HF20_Monthly_Rank_IC_and_Recent_vs_Expanding_Linear_Codex_Prompt_2026-10-25.md` — exploratory 2025/monthly baseline diagnostics, not established recurrent superiority.
- `HF20_S3_Horizon_Comparison_and_Aligned_M2_Codex_Prompt_2026-10-25.md` plus **S3 actual final report** — fully evaluated h1/h2 comparison and M2 alignment.
- `HF20_S4A_Revised_Codex_Prompt_S1_S2_Visuals_8_Neural_Starts_2026-10-26.md` plus **S4 actual final report** — executed seven-origin population, 8 starts, two legacy dashboard links.
- `HF20_S5_S9_Combined_Bounded_Codex_Execution_and_Diagnostics_2026-10-26.md` plus **executed S5/S9 final report/index/CSVs** — four metadata + twelve distinct risk outputs.
- `HF20_LSTM_Architecture_Literature_Review_and_Research_Proposals_2026-10-26.md` — **primary N1–N6 novel-architecture hypothesis report**, including prior papers and minimum information-matched controls; **not trained**.
- `HF20_FT16_Complete_Feature_Specification.md` and `HF20_S9_MAG_Exact_Replication_Supplement.md` — new executed-code extraction documents, **integrated and copied completely into Part III**.
- `HF20_S9_MAG_LSTM_to_Options_Strategy_Research_Handoff_2026-10-27.md` (now superseded as a standalone file by `HF20_S9_MAG_Methodological_Replication_and_Options_Research_Handoff_v2_2026-10-27.md`) — magnitude forecasting and **separate later** options-trading idea.
- `P028_Experiment_3_Final_Approved_Codex_Execution_Prompt.md` and relevant P028 pasted diagnostics — A7/A8/A12 historical tested definitions and results; not a live authorization.

### 9.2 What lives only in the **local repository** (must be inspected, not invented)

1. **P019B/P020 data/FT16 source:** Exact 16 feature names/formulas, M1/M2 maturity, tensor stock order, cap5/volume/fallback, 48-slot indexing, split/action events and provenance are now **methodologically documented in §1.1a and Part III**. The raw minute/processed Parquet bytes, complete original event ledger, exact numerical phase scaler recipes, data rights and real historical publication timestamps are still repository/source matters; this handoff does not claim independent verification of them.
2. **P020/P021/P022/P024/P026–P028 original run manifests/checkpoints:** Exact prior core `C0/T2/H2/W1/SS1/R1/.../A1–A12` hyperparameters, run IDs, source+target recipes, fitted transformations, and all historical attempts. The current report only gives a **complete named family** inventory, not 62 start IDs. Claiming a fully exhaustive start-by-start historical list without this ledger would be fabricated.
3. **S1/S2 actual reports:** `PRIMARY_RESULTS.md`, `S1_FOUR_FOLD_RANKING_BASELINES.md`, `S2_FOUR_FOLD_LSTM_RANKING_COMPARISON.md`, `FINAL_RESEARCH_DECISION.md`, detailed per-fold configuration/epoch/score files and one failed 2021 PW record. A historic **LP** failure is distinct from this PW failure.
4. **S3 executed reports:** `S3_FINAL_RESEARCH_DECISION.md` and related A/B per-year/control tables; saved score keys/feature recipes for shorter horizons and M2-aligned variants. The user has supplied the final decision text but not necessarily every underlying per-run config.
5. **S4 executed reports:** `S4_FINAL_RESEARCH_DECISION.md`, `S4_DETAILED_TRAINING_VALIDATION_REFIT_OOS.md`, `S4_VISUAL_AND_SCIENTIFIC_DIAGNOSTICS.md`, `S4_RANK_STABILITY_AND_SELECTION_CHURN.csv` and per-run saved `oos_scores.parquet` with the authentic 2021–24 score populations.
6. **S5/S9 executed campaign root:** `reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation/` with `S5_S9_FINAL_RESEARCH_DECISION.md`, `S9_TARGET_AND_BASELINE_CONTRACT.md`, `S5_S9_MODEL_METRICS.csv`, `S5_S9_PAIRED_OOS_UNCERTAINTY.csv`, `S5_S9_OOS_PAIRED_SOURCE_STOCK_STRATA.csv`, `S5_S9_DIAGNOSTIC_INDEX.md`, `RUN_INVENTORY.csv`, `S5_S9_VISUAL_DIAGNOSTICS.html`, and 16 actual run folders. Each S9-MAG run contains target/control recipes, per-role saved scores, selections and checkpoint. **No need to reread/copy enormous per-parameter logs.**
7. **Existing dashboards:** Historical S1/S2 `plots/historical_s1_s2_rankings.html`, S4 `plots/s4_a_rankings.html`, and S5/S9 `S5_S9_VISUAL_DIAGNOSTICS.html`, plus **the user's existing working main dashboard**. The user **can already see both dashboard views and has explicitly decided no additional dashboard implementation is necessary** now.
8. **Actual research start ledger**, AGENTS.md, Git status/uncommitted files and resource caps. Must inspect before fitting; summary's 130/200 count is not enough to certify current spending.

### 9.3 Known knowledge gaps—not permission to invent

- **FT16 named native formulas, robust fallback/fitting algorithms, S9 MAG scale values and S9 VOL rules are documented here** (Part III and §5.5a). Numerically precise phase **FT16 scaler arrays** and TG20-specific ε/s for ranking arms remain in the historical recipe JSONs and have not been pasted as 16×fold×phase tables.
- Full per-model **A1–A12** layer configuration, optimization episodes, number of completed starts within each old P026–P028 campaign: current dated review gives mechanisms/results, not all parameter hashes or fit IDs.
- Start-by-start identities for the historical first **62 neural starts**: obtain the repository ledger before a “complete 130-run register” claim.
- Exact execution-locked **S0–S11 full subarm map** beyond the family names in §4: inspect the original protocol/decision notes if available. **Do not infer that a workstream title implies experiments ran.**
- Availability of independent USA500 historical hourly data in HF20: earlier Track A intended it, but A7/A8/A12's actual added state was **endogenous self-including stock-panel means**, **not** confirmed external USA500. Do not presume macro/FX/options data can be used as existing FT16 inputs.
- A genuinely **untouched** future period for statistical confirmation: 2021–24 are reused research evidence; protected 2026 remains inaccessible without authorization.

---

## 10. Interpretations, decisions, and what would count as a good next result

- **Do not redo the already working visualizations.** The user is moving to novel architectures now; preserve the existing UI and actual saved predictions.
- **Do not erase the S3 h2 M2-aligned signal**: +0.015958 paired IC change is worth recording, but its interval includes zero and its final IC is still below simple competitors. It is a targeted horizon-feature observation, not a reason to replace the standard S4 h4 architecture task.
- **Do not erase the S9-MAG result**: 13.7% better task-specific transformed MSE than stock constant, 13.3% better than trailing vol, all four years, though undercalibrated and not signed. It is held for later magnitude/option work and possibly a **separate, explicitly evaluated auxiliary-head hypothesis**, not a free predictor of return sign.
- **Do not claim A7/A12 discovered a helpful common-state component**: later diagnostics **contradicted** that proposed explanation.
- **Do not treat past weak results as a guarantee future architectures fail**, or recent literature as guarantees they succeed. The central research criterion is **incremental, credible, matched OOS ranking performance** in four varied years, with proper uncertainty and a smaller comparable control.
- **No full architecture grid:** Start N1 or a comparably justified single alternative; obtain human sign-off on concrete hyperparameters, architecture and regularization, loss, optimization, search budget, stop criteria and matched baselines; execute a compact campaign only.
- **A scientific no-edge result is complete** when the intended question has been answered. For a positive result, suggest independent confirmation and seed robustness *after* a prospective frozen plan, not hidden OOS refitting.

### Copy-ready opening request for the receiving architecture chat

> This conversation is dedicated to **novel HF20 LSTM/recurrent architecture research and limited authorized implementation**, beginning from the project file `HF20_Novel_LSTM_Architectures_Complete_Research_and_Implementation_Handoff_2026-10-27.md` and the Oct-26 `HF20_LSTM_Architecture_Literature_Review_and_Research_Proposals_2026-10-26.md`. Read both and reconcile the actual local ledger/FT16/TG20/annual folds before drafting a Codex prompt. We have already completed legacy 10+3 diagnostics, A1–A8/A12 screens, S1–S5 and S9; other workstreams are proposals. Existing dashboards work; **do not build or modify a dashboard**. 2026 is protected. Research ledger last known **130/200**. **Hard requirement: minimal engineering overhead**—reuse source, saved predictions, tests and reports; no per-batch/per-file audit industry, no new orchestration stack or redundant rehearsal. Compare **one** new architecture to strong identical-information simpler controls over the frozen F21–F24 OOS years with equal-year rank IC and clearly descriptive uncertainty. Start by evaluating **ARCH-N1 indicator-anchored recurrent residual ranking** against M1 + linear residual correction, or present one justified alternative, and request approval of a bounded scientific/design/compute plan **before** training. Treat S9-MAG/options trading as a separate later study. Never invent past experiments or 2026 results.

---

**End of Part I (standing handoff).** The following **Part II** provides the more granular historical consolidation—including annual and per-fold results, actual fit histories, tested architecture equations, source and role counts, failure accounting, scientifically important negative findings and missing-input requirements—requested for long-term project archiving. Exact run-ID-by-run-ID or byte-identical reproduction still requires the living repository's ledger, configurations, recipes and score exports.

---

# PART II — EXPANDED HISTORICAL EVIDENCE ARCHIVE AND REPLICATION DOSSIER

**Purpose of Part II:** The preceding sections are the standing design/implementation handoff. This second part is a **historical research notebook frozen at 27 October 2026**: it preserves experimental configurations, evaluation populations, actual numerical outcomes, failure and deferral status, hypotheses falsified or left open, and the information required for a comparable rerun. This part deliberately includes unsuccessful trials. It is **not** a ranked shopping list of algorithms or a new training authorization. Where a precise setting was only *proposed* in a Codex prompt rather than verified from an executed receipt, it is labelled accordingly.

## A. Evidence provenance and what “replication” means here

### A.1 Three levels of reproducibility

| Level | What a future reader can reproduce | Available from this Markdown alone? | Additional authoritative source |
|---|---|---|---|
| **Conceptual replication** | Rebuild the same learning task, 20-stock universe, broad feature families, architectures/objectives, clock, evaluation hierarchy and comparison logic | **Mostly yes**, with explicitly flagged unknown ingredients | This handoff and named project design files |
| **Metric replay without refitting** | Recalculate saved-model OOS IC/loss/controls and regenerate scientific plots with exactly matched observations | **No**: needs saved output files and their phase-specific weights/keys | Executed per-run `oos_scores.parquet`, baseline score exports, fold indices, metric reducers, target/scale recipes |
| **End-to-end numerical rerun** | Recompute original FT16, targets and model training, recover comparable fitted checkpoints, scores and annual metrics | **No**: needs frozen raw/source data, code, numerical environment, all fit recipes, initial-state/selector conventions | P019B/P020, `AGENTS.md`, environment, local run configurations/checkpoints and neural ledger |

Even with all records, nondeterminism or unpinned numerical library versions can prevent **bit-for-bit** reproduction; that does not excuse changes to target, cutoff, features, seed, baselines or weighting. The proper standard for a new independent rerun is **predeclared numerical tolerance and scientific equivalence**. A model with only approximately similar features is an *analogous experiment*, not a historical replication.

**Source precedence:** actual fit/source outputs > final executed results > frozen approved implementation prompt > exploratory research/design report > this historical synthesis. Do not “correct” an executed configuration to match an earlier proposal. Do not use a 2025 development checkpoint to claim true OOS performance in 2021–2024. For every future result record population **and** objective in the comparison label.

### A.2 Status vocabulary used throughout

`COMPLETED`: model or fixed comparison actually executed, with reported outputs. `TECHNICAL_PASS`: code/fit/evaluation checks passed; **not** a predictive edge. `NEGATIVE/NO_EDGE`: an executed candidate failed its stated predictive comparator on the stated metric. `MIXED/INCONCLUSIVE`: metrics, years or uncertainty did not justify a robust advantage. `QUALIFIED_POSITIVE`: useful matched predictive effect in *exploratory* historical data; not independent confirmation. `FAILED`: a run/solver did not provide a valid scientific outcome. `NOT_RUN/DEFERRED`: no evidence that the intended fit was performed. `READ_ONLY`: analysis of saved outputs, not a neural experiment. `PROPOSAL`: mathematical construction or intended plan, not evidence.

**Special naming collisions:** `N1`/`N2` in S1–S4 baseline reports are **M1 momentum / reverse M1**, while **ARCH-N1/ARCH-N2** are novel architecture proposals. `A-E0…A-E9` is an older five-stock Track A *decision ladder*; `A1…A12` denotes later HF20 architectural screens. `E1` in the early development suite is *tail-event classification*, not `A-E1` in the old roadmap. `S9` includes three *different-target* experiments and cannot be assessed against a rank-IC-only baseline. `F21…F24` label held-out **calendar years**, not seeds or model depth.

## B. Chronological master experiment history — a single consolidated map

| Period/stream | What was actually examined | Population and core input | Training/objective/selector distinction | Strongest observed conclusion | Status / authoritative follow-up |
|---|---|---|---|---|---|
| **Pre-HF20 Track A** (10 Oct frozen plan) | A-E0…A-E9; LL, SP, MC, FC/RG/AD mechanism menus | *Original proposed* five-stock data/USA500 use; not the final HF20 20-stock panel | Stage-gated experimental **plan**, not 10 executed HF20 models | Valuable hypothesis and data-timing archive; no blanket claim that proposed 5-stock tests were carried out on HF20 | **PROPOSAL/ARCHIVE**; older Track A files |
| **P019B/P020 source + baseline** | Minute→hour source, FT16 and TG20, first common compact stockwise LSTM | 20 stocks; 48×16; two morning origins; long-prefix calibration/refit and 2025 development | TG20 or asinh TG20 squared loss; fresh refit and task-specific selection | Working reproducible predictor; weak signed results; source-quality/price-only timing caveats | **COMPLETED reference/source**, development not F21–F24 OOS |
| **C0 vs T2** | Original-target versus asinh-target signed regression, seeds 42 and 123 | Same early 2025 development population | `C0`: original-Y MSE; `T2`: asinh Z MSE and once-only inverse; original-Y checkpoint selection for early series | T2 better than C0 for both tested seeds, but absolute IC highly seed sensitive | **COMPLETED/MIXED** |
| **P024 and 10+3 optimization/objective screens** | H2/W1/R1/DM1/SS1/LRLOW/DROP0/WD0/ES025/H64/L2H32, E1, QR1 | Same early common source/panel; task-specific target for E1, QR1 | Single changes to objective/regularization/capacity/selector or target family | No general improvement in signed ranking; E1/QR1 suggested distributional information but not properly calibrated superiority | **COMPLETED screens**; exact run-specific selectors/hyperparameters in local receipts |
| **P026 architectures** | A1 temporal attention, A2 multiscale, A3 GRU | Early 2025 development | Compare to compact T2/42 under exploratory 2025 reference | A1 nearly ties/slightly exceeds by point IC; A2 and A3 worse | **TESTED/NOT PROMOTED** |
| **P027 architectures** | A4 peer mean/dispersion, A5 post-compression rank-4 mixer, A6 final-state attention | Early development; differing access to peer summaries/representations | Source/architecture interventions, not always information matched | A4 weak; A5/A6 degraded ranking despite active mixing | **TESTED/NOT PROMOTED** |
| **P028 Experiment 3** | A7 MC1 gate, A8 reduced one-way global–local cell, A12 two soft heads | Earlier 2025 development; 16 own features **plus** 2 derived panel state inputs | Common T2/asinh objective; 3 new starts; some comparisons confounded by additional information | A7/A12 marginally improved original MSE but worsened ranking; A8 worse; later common-level explanation **refuted** | **TESTED/NOT PROMOTED**; correct ledger after P028 **62/200** |
| **Seven-workstream dossier** | Time/source bridge, true objective/tails, rank/common error decomposition, FT16 quality, ranking contract, baselines, expansion readiness | Saved development outputs and source metadata | No neural starts | Sharpened causes and limitations; historical quality flags not automatically causal input | **READ_ONLY**, not a new model |
| **S1** | M1 and reversal, N0, fitted stock profile, full-history linear ridge and attempted linear pairwise | Two morning origins; F21–F24, 48×16 for LR/LP | Normalized-rank regression for LR, pairwise loss for LP | M1 competitive; LR below M1; **LP solver failed and was deferred**, not a negative return-IC result | **COMPLETED with LP failure** |
| **S2** | T2R, normalized-rank `NR`, pairwise `PW` shared LSTMs | Two morning origins, same F21–F24 fold and 48×16 input | Different training losses but **same rank-led validation selection**, seed42 | Weak signed ranks; one **F21 PW neural failure** and only three remaining PW years | **12 starts/11 finishes**, ledger **62→74** |
| **Recent-36 / monthly rank-IC** | Monthly IC patterns, training-window comparison for **linear** baseline | Earlier/repeatedly inspected research folds; *not* a rolling-LSTM fit | Full expanding vs 36-month recent linear history | Recent-36 equal-year IC about **0.00988** vs full-history LR about **0.00604**, mostly 2024 and uncertainty included zero; not robust evidence for rolling LSTMs | **READ_ONLY/limited linear diagnostic** |
| **S3-A** | Future h=1, h=2 vs archived h=4 with unchanged FT16/M2 | Two morning origins, four annual folds, natural h-specific and common matched populations | NR and T2R four folds each at h1/h2; h4 archived reference | Shorter horizon alone **did not** establish better neural ranking | **16 starts; COMPLETED** |
| **S3-B** | h1/h2 use horizon-aligned causal historical M2; other 15 FT16 unchanged | Matched within each horizon to S3-A, unchanged target and keys | NR and T2R for h1/h2 × four folds | h2 T2R improved paired IC **+0.015958**, interval includes zero; absolute skill weak | **16 starts; COMPLETED**; total S3 **74→106** |
| **S4-A** | Four-trading-hour target at seven candidate times, same compact shared LSTM | 20 stocks, S4 4,013 OOS origins, 793 sessions, 80,260 rows | T2R/NR × F21–F24, seed42; original seven-clock data / new fit populations | T2R IC **+0.005921** vs M1 **+0.003383**, inconclusive paired delta | **8 starts; COMPLETED**, ledger **106→114** |
| **S4-B** | Longer/multiday horizon branch | Never authorized after user decision | N/A | No findings; do not call its absence a poor result | **DROPPED/NOT_RUN** |
| **S5 META-T2R** | Add six *verified clock* channels; historical age/quality flags excluded | S4 F21–F24 seven-origin data + verified clock metadata | One-layer H32; transformed TG20 MSE, same reference selector and seed42 | IC **+0.008904**, paired +0.002983 with interval straddling zero | **4 starts; COMPLETED/INCONCLUSIVE** |
| **S9 MAG** | Predict raw four-hour endpoint absolute-log-return magnitude | S4 FT16, 48×16, seven origins, same four folds, no S5 clocks | `log1p(|R|/scale)` MSE, task-specific validation loss selector | **−13.7%** MSE vs STOCK and **−13.3%** vs VOL; all four years | **4 starts; COMPLETED/QUALIFIED POSITIVE** |
| **S9 EVENT** | Three-class rare-event classification, E1-compatible labels | Same as MAG but different head and loss | Natural unweighted 3-class CE, task-specific selector | Worse than stock-specific event prior: CE 0.202028 vs 0.196030 | **4 starts; COMPLETED/NO_EDGE** |
| **S9 QUANTILE** | Conditional 5/50/95% quantiles of asinh signed TG20 | Same S4 information and fold clocks | Original QR1 asinh-space pinball, task-specific selector | Worse than stock-specific quantiles in primary mean pinball | **4 starts; COMPLETED/NO_EDGE** |
| **S6/S7/S8/S10** | Smoothing, minute encoder, peer/factor, dedicated robust-training studies | No completed annual-fold families found in reviewed evidence | Future possible protocols | Earlier A screens and optimization work are only partial antecedents | **NOT VERIFIED EXECUTED** |
| **S11 / ARCH-N1…N6; A9…A11** | Novel mechanisms held for new discussion | No new fit as of this archive | Proposed controls and nulls | No outcome or superiority claim exists yet | **PROPOSAL/DEFERRED** |

**On total accounting:** the first **62** old starts are cumulative across multiple original studies and are **not exhaustively itemized** by the available handoff; later starts account for 12 + 32 + 8 + 16 = 68 additional attempted lifecycles, reaching **130**. Start identities and number of model calibration/refit passes are not interchangeable. The original P028 reporting error showing successive values 63/64/65 was corrected to **62** after three starts **60–62**; do not restore the incorrect display. Exact individual IDs for those earlier starts require the live journal.

## C. The original P019B/P020 2025 development experiment — sample, data, targets and interpretation

### C.1 Four roles and exact historical support in the supplied review

| Role | Origins | Exchange sessions | Stock-origin rows | Chronological context |
|---|---:|---:|---:|---|
| Inner training | **4,428** | **2,513** | **88,560** | Fit first-pass optimizer; documented ending 2023-01-23 |
| Inner validation | **766** | **459** | **15,320** | Begins 2023-02-03, with 48-scheduled-hour separation, and runs through 2025-06-30 |
| Full-prefix fresh refit | **5,210** | **2,980** | **104,200** | 2011-04-01 through 2025-06-30 after initial warm-up |
| Repeated development | **183** | **109** | **3,660** | 2025-07-15 through 2025-12-31; **NOT untouched confirmation** |

Source nominally begins **July 2010** and start-up/warm-up extends through March 2011. This source was **two morning origins**, unlike seven-slot S4/S9; the row populations and validation selection are incompatible with simply pasting S4 statistics next to a 2025 development metric. Early documents speak of January–March 2026 protected confirmation; later HF20 research policy retains **2026 closed** without redefining its contents here.

**Inputs:** per-stock 48 complete scheduled-hour observations × 16 FT16 channels, shared stockwise LSTM, no ticker embedding in the backbone, hidden32, final hidden dropout0.1, linear scalar head, zero state at each independent window. **M1 specifically** is the *latest completed bar’s open-to-close return standardized relative to historical hourly RMS*, subject to actual scale/fallback implementation; **M2 originally** summarizes **previous origin-matched four-hour return** information using historical 20-observation mean / 60-observation RMS and previous-label maturity rules. These descriptions are from the S3 execution specification and **do not replace exact formulas**. In S3-B, only M2 is aligned to h=1/h=2; other 15 FT16 columns remain unchanged. For any precise data rerun retrieve canonical FT16 names, lookbacks, floors and historical numeric scaler values.

**Source-quality specifics worth retaining:** the P020 review reported approximately **Q2 fallback 21.68% in refit / 10.05% in development**, **Q1 fallback 6.70% / 4.46%**, and a reported maximum across-channel fallback near **34.25%**. The earlier historical “daily close” feature proxy used the **15:30 last complete hourly observation**, not the official 16:00 close; daily-volume features omit the closing 30-minute stub. Later genuine minute-price *target endpoints* and S4 opening conventions must not be mistaken for proof that the **input features** used verified official 16:00 daily closes or were executable minute-by-minute.

### C.2 Exact numeric phase constants available for the P028/T2-like legacy setup

| T2/P028 phase | TG20 denominator epsilon | Asinh scale `s` | Scope |
|---|---:|---:|---|
| Inner calibration | **0.00032970431934696** | **0.906406830018944** | Derived from permitted inner-training history |
| Full-prefix refit | **0.00033464021096456584** | **0.9057319697455458** | Derived from permitted 2011–2025 refit history |

These are **historical P028 target-recipe constants explicitly given in the P028 final approved Codex prompt**, not general values for the S1–S9 F21–F24 phases. Each annual fold and each horizon must fit its **own** phase-correct constants. Numeric P028 D6g training prescription: select epoch by dropout-OFF **original TG20 validation MSE** with strictly better than `0.999×` previous qualifying best; minimum calibration duration **12** epochs, maximum **60**, patience **10** nonqualifying epochs; fresh refit for *selected* count even when selected below 12. This must **not** be confused with S1–S4 rank-IC-led epoch selection or S9 task-specific selectors.

### C.3 All 15 core 2025 screen outcomes, interpreted **within their own objective**

The existing §2.1 table retains all original MSE and IC values. The additional mapping below spells out the tested intervention rather than treating a model name as a self-explanatory configuration. Except where explicitly supplied, **exact alternative numerical values** (e.g., the smaller learning rate used in LRLOW, the Huber cutoff, W1 weights, SS1 proposal distribution, ES025 threshold, E1 thresholds, QR1 training selector) are **not supported by this archive**; verify their run-specific recipes before coding a faithful rerun.

| ID | What was changed relative to original compact reference | What remained fixed / unknown | Evidence-based interpretation |
|---|---|---|---|
| `C0-S42` | Optimize squared **original TG20 Y** prediction error | 48×16, H32, one layer, 2025 development; phase recipe from run | MSE 3.112566, IC +0.040318; weak reference |
| `T2-S42` | Optimize squared **asinh-transformed TG20 Z** and inverse once for original-scale diagnostics | Same architecture; original-Y validation selection in this development series | MSE 3.106560, IC +0.075559; modest better than C0 in this screen |
| `C0-S123` | Same C0 with **seed123** | Same earlier population | MSE 3.117257, IC +0.014374; worse than ZERO MSE |
| `T2-S123` | Same T2 with **seed123** | Same earlier population | MSE 3.114912, IC +0.025493; demonstrates seed sensitivity |
| `H2` | Substitute **Huber** training objective | Huber cutoff not copied from unknown run config | MSE 3.111709, IC +0.054480; no improvement over T2/42 |
| `W1` | Tail/outcome-dependent weighting | Precise cap/threshold/weight law only in original artifacts | MSE 3.108253, IC +0.050782; no ranking benefit |
| `R1` | Retain regression with **auxiliary ranking loss** | **Not** a pure NR or PW experiment; mixing coefficient requires run record | MSE 3.106240, IC +0.074718; no ranking improvement |
| `DM1` | Decompose direction and movement magnitude | Not S9-MAG target/units; task-specific heads require exact record | Signed MSE 3.116785, IC −0.000043; magnitude-related submetric may still carry signal |
| `SS1` | Importance-corrected tail sampling | Correctly weighted training risk, not a new target; exact sampling law in run record | MSE 3.109769, IC +0.053402; no main improvement |
| `LRLOW` | Lower optimization learning rate | **Numerical LR not established here**, verify fit | MSE 3.110404, IC +0.071641; inconclusive benefit |
| `DROP0` | Remove final-hidden dropout | Dropout rate = **0** for this arm | MSE 3.104692 (**lowest shown original-Y MSE**), IC +0.072780 (worse than T2) |
| `WD0` | Remove weight decay | Weight decay = **0** for this arm | MSE 3.106679, IC +0.074069 |
| `ES025-S123` | Modified early-stopping/qualification screen at seed123 | The code-name alone does **not** establish exact cutoff or patience | MSE 3.112703, IC +0.032607; marginal/seed-dependent |
| `H64` | Increase hidden dimension from32→**64** | Layer count remains one in reported width comparison | MSE 3.107416, IC +0.035428; more capacity not a cure |
| `L2H32` | Increase recurrent layers one→**two**, each hidden32 | Higher capacity/depth, exact training trace in run records | MSE 3.116366, IC −0.001326; poor ranking in that design |

**A cross-objective comparison trap:** `DROP0` original-Y MSE is lower than A7/A12's reported original-Y MSE, while their ICs differ; **no single 2025 “best model”** can be declared independent of metric and selection. `R1`'s apparent MSE improvement was tiny and not its ranking objective's proof. The T2 output inverse `s·sinh(Zhat)` does not generally equal `E[Y|X]`; a small forecast amplitude alone does not prove broken gradient flow. The development set has been used repeatedly, so ranking arms by these point estimates is exploration, not an unbiased architecture tournament.

**Early risk tasks (different targets):** `E1` ANY-tail AP ≈0.132 vs pooled prevalence≈0.0415, but unweighted CE≈0.2357 vs pooled prior≈0.2023, signed ordinal IC≈−0.0037. `QR1` mean pinball≈0.22608 vs pooled quantile≈0.22983 (≈1.63% improvement), 90% central interval coverage≈89.93%, improvement largely on **outer quantiles**, median weak. They do **not** demonstrate same-task superiority against later stronger per-stock controls, as confirmed by S9 EVENT/QUANTILE. Original `DM1` had a magnitude-error improvement against a prefix constant in its own units, but is *not* the new raw absolute endpoint magnitude target.

## D. P026–P028 A1–A12 architecture inventory — deeper configuration reconstruction

### D.1 What was genuinely tested, and what remains unknown

The original §3 table reports all 12 A-series choices. The **tested** subset is `A1,A2,A3,A4,A5,A6,A7,A8,A12` and the **untrained** subset is `A9,A10,A11`. All nine numbers in §3 are **2025 development original-TG20 MSE / mean daily rank IC**; none is directly a four-year F21–F24 OOS result. Where only a mechanism class and one measured result are supported, do **not** supply imagined attention heads, kernels, hidden widths or stopping epochs.

| Candidate | Historical mechanism detail verified by the reviewed sources | Development MSE | Development daily Rank IC | Attribution/scope |
|---|---|---:|---:|---|
| **A1** | LSTM temporal attention over earlier stockwise hidden states | 3.10630 | +0.075801 | Tiny IC advantage over T2/42; interval includes no gain; precise attention projection settings from P026 only |
| **A2** | Multiscale encoding (stockwise temporal mechanism) | 3.10866 | +0.059596 | Underperformed T2/42; multiscale **category** not exhausted |
| **A3** | GRU recurrent alternative | 3.11474 | +0.012118 | Underperformed one tested compact GRU, not all GRUs |
| **A4** | Causal mean/dispersion of peers' historical M1 | 3.10646 | +0.063840 | Partial summary-information intervention; not complete peer-history control |
| **A5** | **Rank-four** post-encoding cross-stock mixing | 3.10992 | +0.049569 | Hidden cross-stock Jacobian fraction ~**0.37**, evidence of computational sensitivity, not alpha |
| **A6** | Final-state cross-stock attention | 3.11263 | +0.048202 | Attention weights near uniform, not evidence of learned selective lead–lag |
| **A7** | Market-conditioned MC1 **input-feature gate**, 2 contemporaneous panel summary channels | 3.10571 | +0.060536 | Slight original-Y MSE gain, worse z-loss/IC; not external USA500 |
| **A8** | Reduced **one-way** global8 / local32 recurrent cells | 3.10859 | +0.047244 | Active market→local path, worse ranking; not the full reciprocal C3 model |
| **A9** | Coupled specialized recurrent memories | — | — | **NOT_RUN**; mathematical idea only |
| **A10** | State-dependent signed recurrent interactions | — | — | **NOT_RUN**; mathematical idea only |
| **A11** | xLSTM-family cells | — | — | **NOT_RUN**; method library only |
| **A12** | Two state-conditioned soft **readout** heads on one input18 LSTM | 3.10543 | +0.065696 | Slight original-Y MSE gain, weaker z-loss/IC; not fixed-indicator MoE |

### D.2 The frozen *approved* A7/A8/A12 recipes (check executed model configs for exact replay)

**All three**: original P028 **inner 4,428 origins / refit 5,210 origins / development 183 origins**; all 20 stocks. Stock tensor `float32[B,20,48,16]`; shared self-including panel state history `float32[B,48,2]`; output `float32[B,20]` original-TG20 regression scores. The two panel variables at completed historical step `s` were:

\[
m_s=(\operatorname{mean}_{20}(\operatorname{scaled/fallback}M1_s),\;\operatorname{median}_{20}(\operatorname{scaled/fallback}V1_s)).
\]

They are **dimensionless endogenous panel summaries**; the focal stock is included. The shared input `m_s` is available only under the original historical causality qualification and **does not substitute for a genuine USA500/macro/index feed**. All three used same fitted T2 asinh objective and P028 D6g original-Y validation selector, fresh seed42 inner/refit and original AdamW `lr=.001`, `betas=(.9,.999)`, `eps=1e−8`, matrix weight decay .01, bias decay0, clip1, final dropout.1 (OFF in diagnostics), session batches of16, no automatic rescue. The older **T2/42 comparator lacked the extra two input channels**, so the claimed architecture-only effect is *unidentified*.

**A7 — MC1 endpoint input-feature gate**, frozen approved formulation:

\[
\alpha_t=16\,\operatorname{softmax}(W_gm_t+b_g),\quad
u_{i,s}=[\alpha_t\odot x_{i,s};\,m_s],\quad
\hat z_{i,t}=\operatorname{Linear}_{32\to1}(\operatorname{Dropout}_{.1}(\operatorname{LSTM}_{18\to32}(u_{i,1:48}))).
\]

- `Linear(2→16)` gate, temperature1; zero gate weights/bias initially → `alpha≡1` and a mathematical identity with a **fresh same-input18** ungated network, *not* with the old saved 16-input T2 checkpoint. The origin-end gate is held fixed across the 48 historical timesteps, while the concatenated two state channels vary by historical step. No MC2 per-timestep gate fitted. **Expected approved reference trainable parameters: 6,737.** Exact selected epoch and run ID remain in P028 run configurations.

**A8 — one-way common/global state → stock-local cell**, frozen approved formulation:

\[
 g_s=\operatorname{LSTMCell}_{2\to8}(m_s,g_{s-1}),\quad
 h_{i,s}=\operatorname{LSTMCell}_{24\to32}([x_{i,s};g_s],h_{i,s-1}),\quad
\hat z_{i,t}=w^\top\operatorname{Dropout}_{.1}(h_{i,48})+b.
\]

Both recurrent cells also have cell states and reset to zero for each 48-step window. Global cell updates **once** per step (not once per stock); local shared weights operate on all20. Initial `local.weight_ih[:,16:24]` are **zeroed** to start at a null coupling; learning can then open the pathway. No local-to-global feedback, peer-history full exchange, ticker embeddings or new data. **Expected approved reference parameters: 7,841.** A8's failure does not test all common/local memory architectures.

**A12 — two soft state-routed readout heads**, frozen approved formulation:

\[
 h_{i,t}=\operatorname{LSTM}_{18\to32}([x_{i,s};m_s]_{s=1}^{48}),\quad
\pi_t=\operatorname{softmax}(W_rm_t+b_r),\quad
\hat z_{i,t}=\pi_{t,1}\,w_1^\top d(h_{i,t})+\pi_{t,2}\,w_2^\top d(h_{i,t})+\pi_t^\top(b_1,b_2),
\]

where `d(h)` is **one shared** dropout0.1 vector (not two independently sampled expert masks). `K=2` `Linear(32→1)` experts; `Linear(2→2)` origin-end router at temperature1. Experts start as identical copies of the fresh common initial head; router weights are initialized with local CPU generator **seed2812**, `N(0,.01)` and zero bias; this permits subsequent expert differentiation without changing the base seed42 RNG path. No expert-specific LSTM, delayed labels, new entropy regularizer or regime-learning guarantee. **Expected approved reference parameters: 6,728.** An optional diagnostic low/high split used training-derived second-panel-state median (inner **−0.06340353935956955**, refit **−0.03880869597196579**) and was descriptive, not real externally observed market regime truth.

**P028 ledger provenance:** A7/A8/A12 were exactly starts **60–62** (three) with **no retries**; postfit reporting-only correction changed erroneous progressive display 63/64/65 to correct cumulative **62**. Do not interpret three full inner/refit passes as six research neural start charges. Keep original source and run ID receipts authoritative.

### D.3 Important mechanism inference supersession: A7/A12

An initial hypothesis attributed A7/A12's modest original-Y MSE gains to learning a shared **common-level** component; **later read-only decompositions contradicted that**: common-level error *worsened*, while improved error on the **centered extreme-target** subset offset degradation on ordinary rows, with less useful rank ordering. This is an example of why a slight improvement in one aggregate loss cannot validate a supposed financial factor/regime mechanism. Do not reintroduce the disproved explanation in N2/N3 proposals.

## E. Four-fold S1/S2 ranking: actual annual results, objective contract and failure accounting

### E.1 Exactly what was fit, and why the 2025 T2/42 checkpoint is not the S2 comparator

All S1/S2 outer-year models use **original two morning origins, 10:30 and 11:30 ET**, FT16 48×16 and price-only 4-trading-hour labels. F21 train/validation are earlier than 2021; F22 uses eligible matured prior history (including 2021), etc. Each fold has chronological inner train/validation with phase-specific scaling, then **fresh seed42 initialization, empty AdamW and refit** on all earlier eligible labels for the selected epoch count, then annual evaluation. S1 nonneural controls use the corresponding as-of fitting rule. The neural architectures are all plain stockwise LSTM(16→H32, one layer)+final dropout.1+Linear(32→1), 6,433 parameters.

| Arm | Input and target | Fitted model | Training objective | Validation selector | Observed status |
|---|---|---|---|---|---|
| `S1-N0` | None | Constant all ties; no fit | None | None | Completed reference; Spearman **undefined** |
| `S1-N1 / M1` | Latest causally completed M1 | Fixed positive score | None | None | Completed; same sign every fold, no hindsight reversal |
| `S1-N2` | Same M1 | Fixed **negative** M1 score | None | None | Completed; descriptive reversal reference |
| `S1-P` | Historical *past-only* stock rank labels | Per-stock constant expected rank/profile | Weighted normalized-rank square | Prefix-only fit | Completed; unconditional stock identity, not time-varying indicator |
| `S1-LR` | Flatten **all 48×16=768** chronological own-stock inputs | Shared regularized linear rank regressor | Normalized-rank MSE | Inner validation IC, ridge penalty fit on earlier data | Completed, no ticker-ID embedding |
| `S1-LP` | Difference of same **768** covariates over pairs | Shared linear pairwise ranker | Pairwise softplus/logistic | Inner validation IC | **Solver/numerical failure**, **no valid OOS LP** |
| `S2-T2R` | FT16 48×16; labels true future returns→TG20/asinh | Shared H32 LSTM scalar Z prediction | MSE in **Z** space | **Inner validation Rank IC**, not old original-Y MSE | 4/4 completed |
| `S2-NR` | FT16 48×16; future within-origin normalized midrank | Same H32 LSTM scalar score | Squared normalized rank-label error | Same inner Rank IC | 4/4 completed |
| `S2-PW` | FT16 48×16; future unordered pair signs | Same H32 LSTM scalar score | Pairwise-only softplus / temperature `τ=1` in frozen proposal | Same inner Rank IC | **F21 failed after a neural start; F22–F24 completed** |

The S1/S2 *approved design* proposed ridge regularization grid `{10⁻⁴,10⁻³,10⁻²,10⁻¹,1,10}` and `τ=1` for PW, with ranking selection; check **actual** saved LR/PW configuration before claiming precisely which penalty was selected or whether the solver used a particular regularization package. A failed LP baseline is a **technical missing comparator**, not evidence LR dominates LP. A failed neural F21 PW means **PW four-year equal-weight rank IC is unavailable**; never use three-year PW average as a four-year estimate.

**T2R distinction:** the earlier T2/42 model was trained with history reaching **2025**, so it sees 2021–24 during fitting and is invalid as an OOS reference for those years. S2-T2R is a **new fold-matched reference**, same width/input as NR/PW and **new rank-led epoch selector**. It is not a saved rerun of the earlier original-MSE-selected T2/42. S2 planned 12 starts; **11 completed and one F21-PW failed**; ledger **62→74**. S1 also reported **29 successful nonneural baseline fits**, but fitted baseline attempts and neural-start credits are **different ledgers**.

### E.2 Complete annual S1/S2 four-trading-hour primary IC table

**Original two-morning-origin annual populations.** The published S3-A *h4 primary-horizon-specific* table exactly carries these S1/S2 reference ranking values. Ascending realized rank means higher true return = higher rank, while plots may display best as rank1. Annual IC is a Spearman within-origin → equal-origin within session → equal-session within year; **equal-year** is the simple mean of annual values.

| Model | 2021 | 2022 | 2023 | 2024 | Equal-year | Scope |
|---|---:|---:|---:|---:|---:|---|
| `BASELINE-N1 M1` | +0.019108 | +0.002620 | +0.016731 | +0.008443 | **+0.011726** | Positive fixed M1, 4 years |
| `BASELINE-N2 -M1` | −0.019108 | −0.002620 | −0.016731 | −0.008443 | **−0.011726** | Deterministic reversal |
| `LR` 768-input ridge | +0.021587 | −0.002914 | +0.012870 | −0.007373 | **+0.006042** | Supervised simple model |
| `T2R` asinh LSTM | +0.013794 | +0.011797 | +0.018445 | −0.013342 | **+0.007673** | Common rank-led validation selector |
| `NR` rank LSTM | +0.018516 | −0.009882 | +0.011110 | −0.010266 | **+0.002370** | Pure normalized-rank objective |
| `P` stock profile | −0.028270 | −0.007669 | +0.018362 | +0.020117 | **+0.000635** | Static stock identity, unstable |
| `PW` pairwise LSTM | **FAILED / NO OOS** | run completed; inspect saved number | run completed; inspect saved number | run completed; inspect saved number | **undefined / not estimable** | Cannot invent missing fold |
| `LP` linear pairwise | **NOT VALID** | **NOT VALID** | **NOT VALID** | **NOT VALID** | **undefined** | Technical solver failure |
| `N0` constant | undefined | undefined | undefined | undefined | undefined | Ties cannot be coerced to IC0 |

**What this shows:** the simple M1 momentum score beats the available equal-year T2R, LR and NR IC point estimates; none has demonstrated meaningful signed stock-selection alpha or costed profitability. 2024 T2R and NR negative IC explains some year instability. The `P` profile's 2021–22 negative and 2023–24 positive annual signs also caution against a single fixed-stock mean. The relative M1 advantage is **not** evidence M1 itself is a profitable executable strategy.

### E.3 Read-only recent-36-month linear test

A separate diagnostic compared **historical full-expanding linear** and **recent 36-calendar-month** training windows, with a reported recent36 mean IC about **+0.00988** (vs original full-expanding LR **+0.00604**) and most visible benefit from 2024. The uncertainty interval of its gain included zero and the recent36 predictor remained below M1's full-year IC. **This was a linear baseline window comparison, not proof of an improved rolling LSTM**, not a license to search window lengths on reused OOS, and not a changed definition of all four F21–F24 model fits. Exact per-year values/selected regularization are in the corresponding read-only experiment report, not safely derivable from the current handoff.

## F. S3 A/B horizon experiment — the full outcome matrix and interpretation

### F.1 Experiment definition and counted starts

- **Origins:** the unchanged **10:30 and 11:30 completed-hour** origins; h1/h2/h4 true later full-hour endpoints. For the ordinary clock these are **10:30→11:30/12:30/14:30** and **11:30→12:30/13:30/15:30**. No overnight endpoints or final 15:30→16:00 stub in S3.
- **S3-A:** h1 and h2 **unchanged FT16/M2_4**; separately refit **T2R** and **NR** for every F21–F24 = `2 horizons × 2 objectives × 4 years = 16` neural starts. The h4 comparator is **archived** S2, not a new 4h fit. Baselines N0/N1/N2/P/LR supplied by same-key horizon-based evaluation and permitted prefix-only refits.
- **S3-B:** same h1/h2 target and exact source/key/weights **within horizon**, but **only M2** is recalculated using historically matured **horizon-specific prior same-origin returns**, leaving other 15 FT16 unchanged; `2 × 2 × 4 = 16` further neural starts. M2_4 is an unchanged **identity check**, not a 4h neural rerun.
- The original M2 historical protocol was previous same-origin **20-return mean / 60-return RMS** (subject to exact P020 transformation/fallback). Preserve source causality and immutable h4. Four-hour conservative admission embargo was retained for *all* horizons even though h1/h2 labels mature sooner; that is a deliberate comparison-control choice.
- **32/32 new neural lifecycles and 72/72 nonneural attempts technically completed; 74→106/200, no new model failures/retries**. Small ± numerical differences depend on actual masks and selected role; use saved run outputs for a byte-exact replay.

### F.2 Annual IC on the **secondary common** evaluation population, S3-A

This table uses only genuine shared evaluation keys where all three h1/h2/h4 future outcomes exist. It is **not** the primary natural population for each individual horizon.

| Objective/control | h | 2021 | 2022 | 2023 | 2024 | Equal-year |
|---|---:|---:|---:|---:|---:|---:|
| `N1 M1` | 1 | −0.008462 | +0.013774 | +0.033337 | +0.001439 | **+0.010022** |
| `N1 M1` | 2 | +0.011381 | −0.003529 | +0.002723 | +0.000390 | **+0.002741** |
| `N1 M1` | 4 | +0.000424 | +0.017009 | +0.002289 | +0.002872 | **+0.005648** |
| `P` | 1 | +0.022571 | −0.007098 | +0.015900 | +0.034028 | **+0.016350** |
| `P` | 2 | +0.008249 | −0.023682 | +0.039320 | +0.022811 | **+0.011674** |
| `P` | 4 | −0.015873 | −0.005569 | +0.021824 | +0.027415 | **+0.006949** |
| `LR` | 1 | +0.006612 | +0.014897 | +0.023116 | −0.020474 | **+0.006038** |
| `LR` | 2 | −0.007395 | −0.000304 | +0.046787 | −0.035812 | **+0.000819** |
| `LR` | 4 | +0.019497 | +0.010789 | +0.011311 | −0.011828 | **+0.007442** |
| `NR` | 1 | +0.006001 | +0.007843 | +0.030889 | −0.010960 | **+0.008443** |
| `NR` | 2 | −0.000673 | +0.008924 | +0.020883 | −0.008207 | **+0.005232** |
| `NR` | 4 | +0.029004 | −0.014380 | +0.022766 | +0.004025 | **+0.010354** |
| `T2R` | 1 | +0.015180 | +0.009550 | +0.016064 | −0.011906 | **+0.007222** |
| `T2R` | 2 | +0.002666 | +0.000612 | +0.011010 | −0.017117 | **−0.000707** |
| `T2R` | 4 | +0.011509 | +0.011619 | +0.036025 | +0.000191 | **+0.014836** |

The S3-A *primary* h1/h2 T2R means are **+0.004642 / −0.011675** and NR **+0.003725 / −0.003504**. The different S3-A common-key means above illustrate how even a legitimate comparison can change simply because sample and session weights are different. In particular **h4 T2R +0.014836 on S3 common keys is NOT the original S2 full-population +0.007673**. Do not claim that h4 improved without new training.

### F.2a S3-A annual **primary horizon-specific** results (separate from common keys)

This is the population a new model would ordinarily be judged on at *its own* horizon. It is important precisely because the common-population figures in §F.2 can differ markedly.

| Model | Horizon | 2021 | 2022 | 2023 | 2024 | Equal-year primary IC |
|---|---:|---:|---:|---:|---:|---:|
| `M1` | h1 | −0.008511 | +0.005595 | +0.044283 | −0.007136 | **+0.008558** |
| `M1` | h2 | +0.005102 | −0.011828 | +0.043761 | −0.011958 | **+0.006269** |
| `P` | h1 | +0.004463 | +0.002740 | +0.014012 | +0.013478 | **+0.008673** |
| `P` | h2 | +0.008795 | −0.034122 | +0.032144 | +0.031180 | **+0.009499** |
| `LR` | h1 | −0.013416 | +0.021536 | +0.010932 | −0.008651 | **+0.002600** |
| `LR` | h2 | −0.007240 | +0.008655 | +0.003001 | −0.029564 | **−0.006287** |
| `NR` | h1 | −0.002800 | +0.008284 | +0.023875 | −0.014460 | **+0.003725** |
| `NR` | h2 | −0.018882 | +0.022084 | −0.003056 | −0.014161 | **−0.003504** |
| `T2R` | h1 | +0.019147 | +0.012879 | +0.009732 | −0.023190 | **+0.004642** |
| `T2R` | h2 | −0.015127 | +0.001970 | −0.011194 | −0.022347 | **−0.011675** |

The h4 primary table is the original S1/S2 table in §E.2; S3-A reused those four-hour artifacts rather than spending a new h4 neural start. **No direct comparison of h1/h2 primary IC with h4 primary IC isolates the horizon** because the eligible origin/session populations differ. For causal attribution of forecast horizon, use the secondary common-key table §F.2 and disclose the horizon-specific fitting support.

### F.3 S3-B horizon-aligned M2: all four annual IC values on the natural horizon-specific population

| Model | Horizon | 2021 | 2022 | 2023 | 2024 | Equal-year |
|---|---:|---:|---:|---:|---:|---:|
| `T2R` | h1 | +0.019807 | +0.000408 | +0.024863 | −0.020368 | **+0.006177** |
| `T2R` | h2 | −0.004759 | +0.021034 | −0.002410 | +0.003268 | **+0.004283** |
| `NR` | h1 | +0.025335 | +0.005297 | +0.034238 | −0.013182 | **+0.012922** |
| `NR` | h2 | −0.022545 | +0.018836 | +0.006193 | −0.006327 | **−0.000961** |

### F.4 Exact *within-horizon* B minus A change: whole-month descriptive intervals

| Model/horizon | Δ primary Rank IC | 95% descriptive interval | Δ on common keys | Scientific reading |
|---|---:|---|---:|---|
| `T2R h1` | +0.001535 | [−0.010504, +0.013881] | +0.002997 | Minimal, uncertain |
| `T2R h2` | **+0.015958** | **[−0.000770,+0.029417]** | **+0.011140** | Promising bounded M2 alignment; interval **includes zero** |
| `NR h1` | +0.009197 | [−0.003711,+0.022299] | +0.001548 | Population-sensitive; not robust |
| `NR h2` | +0.002543 | [−0.007314,+0.013126] | −0.001072 | Changes sign on common population |

For h2 T2R, primary M2 B−A transformed training objective difference was **−0.004185**, original TG20 MSE difference **−0.005181**, and improvement was positive by IC in **all 4 OOS years**. Yet the B model's absolute primary rank IC was only **+0.004283**, compared to same h2 primary `M1` **+0.006269** and prefix `P` **+0.009499**. Reported h2 **bottom-four retrieval 19.75%→21.86%** (chance 20%). The narrower downside-selection improvement is **descriptive** and was flagged for possible future study, not a proven profitable short strategy.

**Extremes matter, but in the correct units:** S3 A/B original-TG20 **top5%** values account for approximately **50.49–52.34%** of *original-Y squared error*, but **23.08–23.32%** of *actually optimized T2R transformed loss*. For top1% it is **24.78–27.10%** original-Y MSE vs **6.53–6.66%** transformed objective loss. The ordinary complement supplies roughly **76.7–76.9%** of transformed loss. Do not use original-Y MSE concentration to justify changing a model optimized in Z units. The same top5% values contribute roughly **12.57–12.60%** of actual NR ordinal loss. Source numerator/MAD partitions are associations, not causal drivers.

**Source of F.2–F.4:** supplied executed `S3_FINAL_RESEARCH_DECISION.md` (also saved in this conversation as `Pasted markdown(20261026-132856).md`) and S3's annual matched uncertainty CSV. A per-run learning-epoch history requires `S3_TRAINING_AND_FAILURE_TRACE.md` / live receipt; do not manufacture it from the equal-year mean.

## G. S4-A expanded origins — annual checkpoints, categories, stability and tails

### G.1 OOS support and absolute model performance

There are **4,013** actual eligible four-hour forecast origins across **793 sessions** and **80,260 stock-origin rows**. Annual origin/session/row counts are **2021 955/188/19,100**, **2022 1,180/210/23,600**, **2023 887/187/17,740**, **2024 991/208/19,820**. Opening 09:30 has 495 genuine OOS origins overall. Expanded target endpoints cross the overnight session boundary at 12:30, 13:30, 14:30, 15:30; these are four *trading*-hour endpoints, not `t+4` wall hours.

**Actual OOS forecast-origin support by clock** (sums to exactly 4,013; the nominal seven slots are **not guaranteed each day**):

| Origin ET | 2021 | 2022 | 2023 | 2024 | Four-year origins |
|---|---:|---:|---:|---:|---:|
| 09:30 | 130 | 152 | 99 | 114 | **495** |
| 10:30 | 146 | 177 | 133 | 154 | **610** |
| 11:30 | 149 | 188 | 152 | 157 | **646** |
| 12:30 | 135 | 174 | 137 | 154 | **600** |
| 13:30 | 131 | 159 | 115 | 135 | **540** |
| 14:30 | 125 | 162 | 120 | 140 | **547** |
| 15:30 | 139 | 168 | 131 | 137 | **575** |
| **Total** | **955** | **1,180** | **887** | **991** | **4,013** |

These counts are derived from the executed identical-key S9 role/source-strata table, which inherited S4's frozen OOS population; they are **not** a rule to force an origin where the source lacks the needed true price endpoint.

| Rank model | 2021 IC | 2022 IC | 2023 IC | 2024 IC | Four-year IC | Top4 | Bottom4 | Pair concordance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `M1 N1` | +0.003830 | +0.002257 | +0.010390 | −0.002946 | **+0.003383** | 21.49% | 20.30% | 50.13% |
| `-M1 N2` | −0.003830 | −0.002257 | −0.010390 | +0.002946 | **−0.003383** | 20.38% | 20.81% | 49.87% |
| `S4-NR` | −0.005321 | +0.010599 | +0.009055 | +0.000940 | **+0.003818** | 21.70% | 20.51% | 50.17% |
| `S4-T2R` | +0.015205 | +0.016148 | +0.004172 | −0.011840 | **+0.005921** | 23.01% | 20.67% | 50.19% |
| `P` | −0.018879 | −0.028412 | +0.056947 | −0.012673 | **−0.000754** | 23.59% | 20.23% | 49.96% |
| `N0` | — | — | — | — | **undefined IC** | 20% | 20% | 50% |

**All** displayed S4 model absolute-IC 95% descriptive intervals include zero: S4-NR **[−0.010805,+0.015137]** and S4-T2R **[−0.008670,+0.017675]**. On identical origin/session/stock keys, `NR−M1` **+0.000435 [−0.017690,+0.014300]**, and `T2R−M1` **+0.002538 [−0.015288,+0.016970]**. Both are inconclusive. A higher top4 value for the negative-IC P baseline is a reminder that retrieval and rank IC test different properties. No new ridge LR, linear pairwise LP or PW model was fitted under S4-A.

### G.2 Individual training histories — all 8 fold/model fits

These are the **executed** selected epochs, calibrations and fresh refit updates from `S4_FINAL_RESEARCH_DECISION.md`, not hyperparameters optimized on OOS.

| Fold | Model | Calibration epochs | Selected refit epochs | Raw-best epoch | Fresh refit optimizer updates |
|---|---|---:|---:|---:|---:|
| F21 | NR | 14 | **4** | 4 | 560 |
| F21 | T2R | 13 | **3** | 3 | 420 |
| F22 | NR | 12 | **1** | 1 | 152 |
| F22 | T2R | 12 | **2** | 2 | 304 |
| F23 | NR | 13 | **3** | 3 | 495 |
| F23 | T2R | 38 | **28** | 35 | 4,620 |
| F24 | NR | 17 | **7** | 7 | 1,246 |
| F24 | T2R | 23 | **13** | 13 | 2,314 |

For F23-T2R, the frozen IC selector picked **epoch28** despite raw best validation IC at epoch35 (the later increment did not qualify under the **absolute +0.001 improvement** rule). Fresh refit starts again from the same-seed initial state, not the calibration checkpoint. F23's prolonged 28-epoch refit still produced OOS IC **+0.004172**, below that year's M1 **+0.010390** and P **+0.056947**. Later epochs alone are not proof of a better generalizable rank predictor.

### G.3 Slot/overnight/stability diagnostics worth retaining

| View | NR | T2R | Scientific qualification |
|---|---:|---:|---|
| Original 10:30/11:30 **slice within S4** IC | +0.000727 | +0.011607 | Different weighting; not isolated causal effect of extra slots |
| `INTRADAY` IC | −0.002034 | +0.006748 | Actual eligible category |
| `OVERNIGHT` IC | +0.005461 | +0.002770 | Category mean; overlapping category contrasts include zero |
| `OPENING 09:30` IC | +0.004132 | −0.000940 | 495 origins, neither interval excludes zero |
| Within-session adjacent **top4 Jaccard** | **0.545** | **0.597** | Model ranking persistence, **not correctness** |
| Within-session adjacent mean absolute **rank change** | **2.76** | **2.44** | Some stickiness/churn, not an executed trade |
| Names newly entering top4 per transition | **1.36** | **1.20** | Descriptive; varying eligibility/gaps distinguished |

On the **735** sessions supporting both intraday and overnight labels, the matched overnight-minus-intraday IC for NR was **+0.003331 [−0.015686,+0.019388]**, T2R **−0.005532 [−0.022925,+0.011002]**. Neither is a robust overnight category effect. On matched S2 historical *morning* keys, `S4−old S2` effects were approximately **−0.002331 NR** and **+0.002877 T2R**, with intervals including zero; the **training origins and M2 context** also differ. The old morning models were not repainted as all-day models.

**2023 overfit/nonstationarity warning:** F23 T2R inner-train IC **+0.136215**, inner-validation IC **+0.060273**, OOS **+0.004172**. This is a real loss of association across roles, not a proof that one specific market regime shift caused it. F24 T2R's OOS IC **−0.011840** despite a nontrivial earlier fitting IC is another generalization concern. Full S4 diagnostic files give all four roles, losses, gradient summaries and exact source witnesses without needing to repeat that engineering in future experiments.

**Tail behavior:** top1% realized original-`|TG20|` rows account for approximately **6.6–7.5%** of S4-T2R's *transformed* OOS loss but **25.7–36.0%** of *separate original-Y MSE*. For S4-NR, the same original-target tail accounts for **2.5–2.7% of ordinal loss**. This difference is central to truthful target-specific diagnosis; never call ordinal output an inverted return or infer a tradable payoff from a rank score.

## H. S5 + S9 complete 16-run log and quantitative evidence

### H.1 Frozen common treatment, objective differences and status

S5/S9 reuses the complete **S4 h4 seven-candidate-origin** population, frozen F21–F24 chronological roles and prior resource/privacy/source qualifications. All new fits use **seed42**, 48 completed hours per stock and one layer H32 shared recurrent backbone unless metadata raises the input dimension. S5 adds **six verified trading-clock channels** to FT16; it **does not include historical QA/missingness/observation-age flags lacking point-in-time certification**. The executed-code FT16 extraction identifies the six S5 names (`step_sin`, `step_cos`, `session_boundary`, `elapsed_scheduled_wall`, `origin_sin`, `origin_cos`) and their **per-step** concatenation, making **48×22** S5 inputs. Consult `S5_CAUSAL_METADATA_MANIFEST.md` and its actual run configuration before asserting the six fields' individual numerical encodings; S9 instead retains 48×16 FT16. Its target/loss remains T2R asinh TG20 MSE.

S9 MAG/EVENT/QUANTILE use **the original 16 FT16 only**; each changes **target and, where necessary, output head and task-specific validation selector**, not the recurrence width/history. This makes them **three distinct regression/classification/distribution tasks**, not three evaluation metrics for one scalar output. They each have proper same-task baseline(s). S5+S9 together had **16/16 technical passes, 32 training/refit prefix recipes, 64 campaign control records/outputs (not all controls have fitted coefficients), 0 failed neural starts/retries, ledger 114→130/200**. Their prior excessive audit logs are archived but **must not be copied as future engineering requirements**.

| Arm | Target (beyond shared h4 price endpoints) | Optimized train loss | Main supervised comparator | Important units |
|---|---|---|---|---|
| **S5 META-T2R** | `TG20`, phase-scaled then `asinh(TG20/s)` | MSE of asinh transformed signed relative-return target | Frozen **S4-T2R** on matched origin keys, plus M1/P | IC is score ordering; Z-loss not MAE |
| **S9 MAG** | `A=|log(P_future/P_origin)|`; target `m=log1p(A/s_f)` | MSE of transformed **raw endpoint magnitude** | Train-prefix per-stock transformed-magnitude constant `STOCK`; trailing-vol-based `VOL` | Not TG20 magnitude, no sign; inverse lacks conditional-mean guarantee |
| **S9 EVENT** | Original E1-compatible **three mutually exclusive classes** | **Natural unweighted three-class CE** | Per-stock fitted class prior, plus pooled prior and volatility proxy | ANY event Brier/AP are ancillary to 3-class CE |
| **S9 QUANTILE** | `TG20` asinh transformed; 5%, 50%, 95% conditional quantiles | Mean pinball across **0.05/0.50/0.95** in transformed Z units | Per-stock conditional-history-free fitted quantiles, pooled quantiles | Width/coverage and median rank are ancillary, not directional alpha |

Do not compare numeric MSE 0.232454, CE 0.202028, pinball 0.230705 as if they represent the same statistic. For MAG, the training scale `s_f` is **prefix-fitted per appropriate phase and fold**, not the P028/T2 `s≈0.906` scale. The exact scale-fitting statistic and values are not copied in the uploaded final report and must come from saved `inner_target_recipe.json`/`refit_target_recipe.json`.

### H.2 Every S5/S9 fold run — calibration, selected epoch, raw best and actual optimizer updates

The following is transcribed from the user's supplied complete S5/S9 `Detailed training and extreme-value diagnostics` table. Column `selected` is the number of epochs for the **fresh refit**; raw-best does not always meet the frozen qualifying-improvement rule. **All reload errors reported zero**, every reported optimizer batch updated parameters, and completed-run resource use remained below approved caps.

| Arm | Fold | Calibration epochs | Selected refit epochs | Raw-best epoch | Calibration updates | Refit updates |
|---|---|---:|---:|---:|---:|---:|
| **S5 META-T2R** | F21 | 13 | **3** | 3 | 1,716 | 420 |
| | F22 | 12 | **1** | 1 | 1,752 | 152 |
| | F23 | 13 | **3** | 3 | 2,080 | 495 |
| | F24 | 12 | **2** | 2 | 2,064 | 356 |
| **S9 MAG** | F21 | 37 | **27** | 30 | 4,884 | 3,780 |
| | F22 | 30 | **20** | 20 | 4,380 | 3,040 |
| | F23 | 51 | **41** | 41 | 8,160 | 6,765 |
| | F24 | 37 | **27** | 27 | 6,364 | 4,806 |
| **S9 EVENT** | F21 | 14 | **4** | 4 | 1,848 | 560 |
| | F22 | 37 | **27** | 27 | 5,402 | 4,104 |
| | F23 | 24 | **14** | 14 | 3,840 | 2,310 |
| | F24 | 12 | **2** | 2 | 2,064 | 356 |
| **S9 QUANTILE** | F21 | 14 | **4** | 4 | 1,848 | 560 |
| | F22 | 22 | **12** | 15 | 3,212 | 1,824 |
| | F23 | 21 | **11** | 18 | 3,360 | 1,815 |
| | F24 | 19 | **9** | 9 | 3,268 | 1,602 |

**Run identifier rule in saved outputs:** `HF20-S5-F21-H4-META-T2R-S42` for S5 (analogous F22–F24), `HF20-S9-F21-H4-MAG-S42`, `HF20-S9-F21-H4-EVENT-S42`, `HF20-S9-F21-H4-QUANTILE-S42` for S9 families (analogous folds). Use actual file inventory rather than generate a new run ID by changing a string. S5 F21 calibration selected epoch3 after13; MAG F21 selected27 despite raw-best30; S9 QUANTILE F22 selected12 despite raw-best15 and F23 selected11 despite raw-best18. These are **real qualification-rule distinctions**, not evidence that final OOS outcomes chose epochs.

### H.3 Annual paired OOS effects, including negative findings

**Conventions:** `Δ(S5)` is signed **IC(S5 − S4-T2R)** (positive helps); S9 deltas are **model proper loss minus task-matched baseline loss** (negative helps). The full-year statistics are equal-weight across four OOS calendar years, with **95% descriptive whole-month block intervals** only for the four-year effect in the table; no claim of post-search confirmation.

| Arm / reference / metric | 2021 | 2022 | 2023 | 2024 | Equal-year effect | Descriptive 95% interval | Outcome |
|---|---:|---:|---:|---:|---:|---|---|
| `S5 − S4-T2R` **Rank IC** | +0.004075 | **−0.021349** | +0.022643 | +0.006562 | **+0.002983** | [−0.010230,+0.014905] | Positive 3/4; **INCONCLUSIVE** |
| `MAG − STOCK` **Z=MAG log1p MSE** | −0.038667 | −0.069598 | −0.018095 | −0.021357 | **−0.036929** | [−0.042946,−0.031723] | Better 4/4 |
| `MAG − VOL` **MAG log1p MSE** | −0.037156 | −0.039514 | −0.036084 | −0.030494 | **−0.035812** | [−0.040886,−0.031409] | Better 4/4 |
| `EVENT − STOCK` **natural 3-class CE** | +0.002800 | +0.012089 | +0.008319 | +0.000784 | **+0.005998** | [+0.002984,+0.009021] | Worse 4/4 |
| `QUANTILE − STOCK` **mean Z pinball** | +0.000349 | +0.001413 | +0.000571 | −0.000478 | **+0.000464** | [+0.000035,+0.000914] | Worse 3/4 |

**Absolute primary proper scores** (equal-year): S5 rank IC **+0.008904** vs S4-T2R **+0.005921**; MAG proper MSE **0.232454** vs STOCK **0.269383** and VOL **0.268266**; EVENT three-class CE **0.202028** vs STOCK prior **0.196030** and GLOBAL pooled prior **0.220307**; QUANTILE mean asinh-Z pinball **0.230705** vs STOCK fitted quantiles **0.230242** and GLOBAL quantiles **0.234292**. A model outperforming **GLOBAL** but losing to **STOCK** is not an incremental historical-information success beyond the stronger stock-specific control.

### H.4 S9-MAG quantified strengths and limits

For magnitude **transformed-target MSE**: `(0.269383−0.232454)/0.269383 ≈ 13.7%` versus STOCK; `(0.268266−0.232454)/0.268266 ≈ 13.3%` versus VOL. For **raw absolute-log-return MAE**, LSTM **0.006505**, STOCK **0.006903** (~**5.8%** improvement) and VOL **0.006992** (~**7.0%** improvement). The **GLOBAL and STOCK** constants were fitted to the **transformed** objective; the VOL baseline is the **parameter-free** transformed V2/RMS60 heuristic (§5.5a). None of the three controls is established as optimal for raw-magnitude MAE. Reported movement-size rank association is **0.408** (refer to actual metric file for precise definition/weighting).

The displayed original-magnitude forecast **mean 0.00836**, actual **mean 0.01031**, gap **0.00195 log-return units**, i.e., approximately **0.195 percentage points** of movement for small returns. Predictions average roughly **81% of realized magnitudes** and miss many of the more extreme individual price movements. The lower-clamped inverse of the trained `log1p` prediction is **not** necessarily the conditional mean of `|R|`; calibration against earlier chronological data, not hindsight OOS rescaling, is a separate future study. `|R|` at one endpoint has no return sign and is **not** intrapath volatility, risk-neutral implied volatility or an executable straddle payoff.

**Breadth from the supplied 1,764-row source/stock stratum CSV:** MAG is better in transformed proper loss against STOCK for **78/80 stock-year cells**, against VOL for **80/80**. The **two** STOCK exceptions are **PEP in 2023** (MAG−STOCK ≈ **+0.001085**) and **MRK in 2024** (≈**+0.000678**). MAG improved averaged annual proper loss for **all 20/20 stocks**. Against **each** of STOCK and VOL, gains occurred in **48/48 calendar-month × year groups, 28/28 clock-slot × year groups, 8/8 intraday/overnight-category groups, 8/8 source-quality groups, and 8/8 fallback groups**. On observation-age grouping MAG beat STOCK in **15/16** nonempty year/age-band cells (exception **2022 LE5** Δ≈+0.005021), and beat VOL in 16/16. **This is descriptive, overlapping evidence, not 78+48+28 independent experimental replications.** All these groups reuse the same 80,260 or fewer weighted stock-origin records under different partitions; some age/source fields describe observed *source metadata*, not additional verified inputs learned by S9-MAG.

**Four-year fold magnitudes** (actually optimized MAG MSE; not per-year raw MAE): 2021 **0.222777**, 2022 **0.279200**, 2023 **0.208858**, 2024 **0.218982**. Their arithmetic average gives the reported **0.232454**. The year-2022 MAG baseline reduction −0.069598 is particularly large (against STOCK); year 2023 still improves but less (−0.018095). The stronger association of high predicted risk with high realized risk does not imply model tail calibration.

**Annual raw `|R|` MAE differences**, MAG minus the respective transformed-MSE-trained baseline. More negative indicates a smaller *raw* absolute error, but this is a secondary diagnostic rather than a raw-MAE-optimal-baseline experiment:

| Comparator | 2021 | 2022 | 2023 | 2024 | Equal-year MAG-minus-control raw MAE |
|---|---:|---:|---:|---:|---:|
| `STOCK` | −0.00043418 | −0.00066508 | −0.00022286 | −0.00027166 | **−0.00039845** |
| `VOL` | −0.00050702 | −0.00052709 | −0.00050143 | −0.00041314 | **−0.00048717** |

These differences are supported by the supplied `S5_S9_PAIRED_OOS_UNCERTAINTY.csv` numeric extract. All are negative across 2021–2024; the primary reported conclusion still rests on **transformed MSE**.

### H.5 Why S9-EVENT and S9-QUANTILE remain negative despite useful-looking plots

**EVENT:** three-class CE model **0.202028**, STOCK prior **0.196030**: worse proper loss **+0.005998** in every year. ANY-class average precision: **0.1442** vs STOCK **0.1493**, both well above pooled event prevalence **0.04646**. Yet EVENT ANY **Brier 0.042775** vs STOCK **0.041273** and ANY **log loss 0.169894** vs STOCK **0.163901**. The model improves over a much weaker pooled prior but **fails against stock-level priors**, so strong AP/prevalence alone does not justify trading/claimed probability skill. The original E1 labels and **natural unweighted CE** were deliberately retained; no class-weighted rescue fit was authorized.

**QUANTILE:** mean asinh-Z pinball **0.230705** vs STOCK **0.230242**, worse by **+0.000464**, and the descriptive four-year interval for the difference is **[+0.000035,+0.000914]**. It beats a pooled control **0.234292** but not the stronger per-stock quantile baseline. Its nominal **90%** central interval realized coverage was about **91.86%**, vs STOCK **90.03%**, while mean **Z interval width increased to 3.755 vs 3.598**: broader intervals can improve coverage without lowering proper score. Median daily rank IC around **+0.00128**, mixed signs by year; not directional-alpha evidence. Actual optimized units are `QR1` **asinh pinball**, with one inverse only for original-TG20 presentation; do not invent a raw-MSE comparison from quantiles.

**By-quantile stock-control comparison** from the uploaded annual/equal-year paired table: model-minus-STOCK mean asinh-Z pinball is **+0.000770 at q=0.05**, **−0.000090 at q=0.50**, and **+0.000711 at q=0.95**. This reinforces the conclusion that favorable pooled-tail comparisons did not survive the stronger per-stock control, particularly at the two outer quantiles. Do not infer significance of an individual quantile from aggregate pinball alone; see saved 95% descriptive intervals and per-year data. A slightly better point estimate at the median is not evidence of a useful signed-return ranking model.

### H.6 Across-task extreme-loss concentrations — actual optimized objectives, not false equivalents

| Arm | OOS phase training95th-tail observation weight | % actual optimized loss from this tail | % optimized loss from worst-error1% | Meaning |
|---|---:|---:|---:|---|
| `S5 META-T2R` | 4.63% | **22.96%** | 7.04% | T2R asinh squared loss |
| `S9 MAG` | 5.87% | **24.08%** | 9.49% | log1p magnitude squared loss |
| `S9 EVENT` | 4.63% | **71.81%** | 22.48% | **Natural 3-class CE**, rare-event log loss expected to concentrate |
| `S9 QUANTILE` | 4.63% | **12.69%** | 3.78% | **Mean asinh pinball** |

The source NUM_ONLY/MAD_ONLY attribution to their own optimized losses was reported about **S5 24.75%/2.61%**, **MAG 22.71%/1.46%**, **EVENT 49.39%/3.24%**, **QUANTILE 14.55%/2.56%**, respectively; `BOTH/NEITHER` are separate **disjoint** partitions in that comparison. Target-top5%, error-top1%, the sign groups, and NUM/MAD partitions **overlap across families**; never add across these different cohort definitions or imply a causal decomposition. No reported OOS row belonged to the epsilon-dominated denominator cohort. A future ARCH-N1 rank-only loss must be diagnosed as **rank loss**, not as if it were an original-TG20 return MSE.

### H.7 Report locations and numerical reproduction for S5/S9

Use the executed root (relative to repository):

```text
reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation/
```

Main saved files include `S5_S9_FINAL_RESEARCH_DECISION.md`, `S5_S9_MODEL_METRICS.csv`, `S5_S9_MATCHED_BASELINE_DIFFERENCES.csv`, `S5_S9_PAIRED_OOS_UNCERTAINTY.csv`, `S5_S9_OOS_PAIRED_SOURCE_STOCK_STRATA.csv`, `S5_S9_EXTREME_LOSS_SUMMARY.csv`, `S5_S9_TRAINING_TRACE.csv`, `S5_S9_DETAILED_TRAINING_AND_EXTREME_DIAGNOSTICS.md`, `S9_TARGET_AND_BASELINE_CONTRACT.md`, `S5_CAUSAL_METADATA_MANIFEST.md`, `S5_S9_VISUAL_DIAGNOSTICS.html`, and `S5_S9_DIAGNOSTIC_INDEX.md`. Each of the **16** run folders should expose its authoritative `configuration.json`, `inner_target_recipe.json`, `refit_target_recipe.json`, `calibration_binding.json`, `refit_binding.json`, `oos_scores.parquet`, same-task controls and checkpoint information under the actual index. **Do not infer a file exists from a proposed illustrative name**; follow the index if a named artifact is missing.

For exact matched recalculation, key by `(fold, origin timestamp, ticker, role, target endpoint, horizon, model/contract)` and preserve the saved hierarchical evaluation weights; check the role's target/scale at the corresponding inner/refit phase. Do not fit controls to OOS, or average all 80,260 rows as though they were 80,260 independent equal-weight years. The **source study** is exploratory with reused F21–F24 annual outcomes, not fresh independent confirmation.

## I. Scientific findings worth retaining as hypotheses — what is established versus still speculative

### I.1 Positive, negative and mixed outcome inventory

| Finding or hypothesis | Best numerical/behavioral evidence | Supported claim | **Not** supported |
|---|---|---|---|
| Asinh T2 vs original MSE C0 | 2025 T2 IC 0.075559 vs C0 0.040318 seed42; T2 0.025493 vs C0 0.014374 seed123 | Transformed target was a better exploratory fit under these two seeds | Generalizable alpha or a unique optimal transform |
| Temporal attention A1 | 2025 IC +0.075801 vs T2 +0.075559 | Very small positive point estimate | Significant/selective attention advantage |
| Larger width/depth | H64 IC +0.035428; L2H32 IC −0.001326 vs T2 +0.075559 | Those particular capacity changes failed to improve the 2025 benchmark | All larger networks fail |
| Peer/spatial mixing | A5 Jacobian cross-stock fraction ~0.37 but IC +0.049569; A6 attention near uniform and IC +0.048202 | Cross-stock channels can be active yet unhelpful for prediction | No cross-stock effects exist |
| Endogenous market-conditioned models | A7/A12 original-Y MSE ~3.10571/3.10543 but IC below T2 | Slight MSE gain, no ranking gain | Independent USA500 effect or improved common-level error |
| Shorter horizons | S3-A h2 T2R −0.000707 on common keys, h4 +0.014836 | Simple horizon shortening did not establish improvement | 1h/2h never predictable |
| **Aligned historical M2 at h2** | S3-B h2 T2R ΔIC +0.015958 [−0.000770,+0.029417]; bottom4 21.86% | Bounded reason to retain this feature/horizon idea for later | Confirmed significant alpha or superiority to M1 |
| Additional four-hour origin times | S4-T2R +0.005921 vs M1 +0.003383; interval on Δ includes 0 | Feasibility of seven candidate times and overnight-crossing labels | Statistically reliable incremental rankings/trades |
| Ranking persistence | S4 T2R adjacent top4 Jaccard ~0.597, mean rank-change 2.44 | Some forecast stability without smoothing | Accuracy, turnover-adjusted P&L |
| S5 clock channels | S5 +0.008904 IC, Δ vs S4 +0.002983 interval crosses 0 | Mild total-package point gain | Causal age-quality effect or N4 memory success |
| **Magnitude predictive skill S9-MAG** | −13.7% vs STOCK, −13.3% vs VOL MSE, better 4/4 years, 78/80 stock-year | Qualified historical conditional movement-size information | Calibrated `E|R|`, future implied-volatility edge or signed alpha |
| S9 EVENT | CE 0.202028 vs stock prior 0.196030; AP 0.1442 <0.1493 | Worse on primary proper score and stock-prior discrimination | No tail information at all |
| S9 QUANTILE | Pinball 0.230705 > 0.230242 STOCK despite coverage 91.86% | No incremental primary loss gain versus stock quantiles | All distributional models are useless |
| 2025 recent-36 linear history | IC ~0.00988 vs ~0.00604 original expanding LR | Mixed hint of nonstationarity/benefit from recency | Rolling-LSTM superiority or regime causality |

### I.2 Research interpretation boundaries

- **Functionals are different:** A forecast minimizing transformed-target squared error estimates a conditional transformed mean, not necessarily an untransformed mean. A normalized-rank regressor estimates an expected rank (under its conditions), not `E[R]`. Pairwise logistic scores, event probabilities and conditional quantiles also target distinct objects. Do not merge them into one “predictive edge” axis.
- **Multiple tests are correlated:** 2025 development was repeatedly inspected; four historical OOS years F21–F24 were revisited with many design decisions; month-block uncertainty is a useful *descriptive* variability diagnostic, not post-search confirmatory p-values.
- **Trading assumptions unresolved:** the returned price starting at labeled origin precedes the assumed +2-minute issuance; no bid/ask transaction prices, options quotes, borrow, liquidity, funding or turnover costs are in model IC/loss tables. Neither a top4 selection rate above 20% nor MAG MSE gain establishes profit.
- **Fixed twenty-name survivor set:** a historically surviving 20-stock panel is not a point-in-time membership process, broad-universe risk or sector-neutral benchmark. Peer models based on this restricted set must describe it accurately.
- **Overlapping outcomes:** stock rows share market time, multiple candidate 4h outcomes overlap, and full 20-stock cross-sections are dependent. A valid block procedure keeps origins within session and same-market-year dependencies together as far as the chosen resampling allows; reporting four annual results is more informative than one pooled row p-value.
- **No permutation-null confirmation shown for these HF20 stages:** Some wider algorithmic-trading project plans mention permutation-based null tests, but no submitted S1–S9 final report establishes a completed **full-pipeline permutation null test** for these annual HF20 candidates. Never claim it was performed without a matching run report; a future permutation study needs separate pre-registered scope and compute allocation.
- **No held-back 2026 result:** The 2026 protected period remains closed. An architecture winner selected after multiple F21–F24 inspections cannot be called independently validated until a separate explicitly authorized test.

## J. Lightweight but scientifically exact reconstruction checklist for the next chat

This section is a **read-and-reconcile checklist**, not an instruction to create a new auditing software stack. The new researcher should inspect existing files **without refitting anything** before preparing a single architecture card.

### J.1 Minimum artifact set to understand a historical family

| To understand… | Read these authoritative items first | What to extract / never invent |
|---|---|---|
| Earliest 10+3 / 2025 `C0/T2/H2/W1/...` | `HF20_LSTM_Comprehensive_Review_and_Expansion_Plan_2026-10-24.md` §§2–3 and original P020/P024 runs | Two-origin population, source/target recipes, exact hyperparameters per run, objective units, model/seed selected epoch, original development IC |
| A1–A6 | P026/P027 actual configuration and diagnostics + Oct24 HF20 review §3.3 | Actual attention/GRU/mixer widths, input information access, selected epochs and null probes |
| A7/A8/A12 | `P028_Experiment_3_Final_Approved_Codex_Execution_Prompt.md`, then **executed** P028 run folder and final report | Exact two panel channels, feature transforms, selected epochs, actual parameter count, once-inverted target, 3 starts60–62 |
| S1/S2 | `PRIMARY_RESULTS.md`, `S1_FOUR_FOLD_RANKING_BASELINES.md`, `S2_FOUR_FOLD_LSTM_RANKING_COMPARISON.md` and actual run configs | F21–F24 score keys, ridge λ, selected neural epochs, PW F21 error, failed LP solver |
| S3 | `S3_FINAL_RESEARCH_DECISION.md`, `S3A_HORIZON_ONLY_COMPARISON.md`, `S3B_HORIZON_ALIGNED_M2.md`, S3 target/M2 recipes | Horizon-specific vs common populations, identity of 15 unchanged channels, 32 starts, paired A/B deltas |
| S4 | `S4_FINAL_RESEARCH_DECISION.md`, `S4_DETAILED_TRAINING_VALIDATION_REFIT_OOS.md`, `S4_RANK_STABILITY_AND_SELECTION_CHURN.csv`, saved score Parquets | Seven genuine candidate origin times, 8 per-fold fits, selected epochs, year/category IC, source and ranking-stability views |
| S5/S9 | Campaign root `reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation/` and full diagnostic index | Every one of 16 fit IDs, S5 six metadata names, MAG fitted scales/STOCK/VOL rules, EVENT thresholds, QUANTILE levels and all proper scores |
| Novel designs only | `HF20_LSTM_Architecture_Literature_Review_and_Research_Proposals_2026-10-26.md` plus older recurrent interaction menus | What is a proposed mechanism vs established prior art, which matched control is necessary and what falsifies it |

### J.2 Exact unknowns before claiming a **fully repeatable numerical training run**

These gaps are not evidence of a poor previous study; they are evidence that **the uploaded summaries are not a repository snapshot**. Recover only when needed; do not ask the user to paste giant logs by default.

1. **Largely resolved for documented methodology:** Part III Annex A includes all FT16 formulas/scalers/fallbacks/M2 maturity, genuine minute-price endpoint construction, the canonical stock-axis order and exact source QA rules. **Still unresolved:** factual historical vendor/feature *publication* timestamps (the implementation assumed origin+2-minute issuance), historical completeness certification and retrospective action-fact vintage; the actual **numeric** per-fold robust scales remain in saved S4 JSON, not this report.
2. **S4/S9 role methodology resolved:** §5.5a and Part III Annex B give exact inner/validation/refit/OOS date rules, saved fold-role counts and boundary/maturity/embargo definitions, S9 MAG target scalers and coefficients. **Numeric member-by-member key lists and TG20 ε/s for other objectives** still reside in the executed S4 indices and task-specific files; do not extrapolate MAG scales to rank targets.
3. P026/P027 A1–A6 implementation variants: actual layer sizes/head counts/activation/dropout, checkpoint selection epochs, exact input information and their original run IDs. The aggregate Oct24 review supports the model-class labels and numbers, **not** exact unseen architectural internals.
4. P028 A7/A8/A12 actual selected epoch and code/identity of source state channels; approved 6,737/7,841/6,728 parameter counts are specific to the frozen proposed layers and should be compared to saved actual full model configurations.
5. S1/S2 fold model epoch selections, realized PW F22–F24 annual metrics, the selected `LR` λ values and specific LP solver failure; their complete record remains local.
6. S3 individual fit histories and detailed h1/h2 M2 phase scales/fallback values, per-run input/score keys and epoch selectors beyond final summary.
7. **Partly resolved:** The six S5 channels are `step_sin, step_cos, session_boundary, elapsed_scheduled_wall, origin_sin, origin_cos`, appended as per-step fields for a 48×22 input as recorded by the executed-code extraction. **Their complete per-channel numeric encoding ranges, exact normalization and saved per-role run parameters still require direct S5 executed-source/manifest consultation** before independent S5 recreation.
8. **S9-MAG resolved:** The phase-specific weighted-median log1p scale and its eight values, decode-only clamp, parameter-free **V2 RMS60** VOL formula and exact MAG model/selector are documented in §5.5a and Part III Annex B. **Remaining other-task gaps:** S9-EVENT class thresholds/stock prior details and S9-QUANTILE control quantile fit and transformation should be checked against their own completed run files if independently reproducing those tasks.
9. Live **all-attempt neural ledger** (first 62 starts are not exhaustively listed here), actual Git/env versions, protected-path denial rules, resource limits and file ownership; verify only the minimum needed for the next approved experiment.
10. Any literal future options data/quote feed; none is included with these price-only ranking/magnitude forecasting archives.

**Minimal task-level correctness gates in a new architecture** remain: causal source/label maturity, identical target/population/control keys, phase-fitting, correct actual loss + session/origin weights, finite optimization and saved refit, model-specific mathematical null/invariance fixture, and exact saved OOS metric recomputation. These are **not** a justification to generate per-parameter gradient ledgers, hundreds of file hashes, repeated full-dataset rehearsal, or new experiment orchestration. Reuse current code and leave legacy audits intact.

### J.3 Design freeze card for the first novel-architecture experiment (to be completed, NOT assumed)

| Field | To freeze prospectively | Source / constraint |
|---|---|---|
| Scientific hypothesis | e.g. indicator-anchored corrections supply incremental relative-stock ordering beyond M1 | One hypothesis; not an A1–A12/N1–N6 grid |
| Exact architecture | Dimensions, intermediate states, gate null, parameter count, dropout position, information access | N-series primary report; count actual parameters; default H32 FT16 reference |
| Training | Objective and actual unit, optimizer/hyperparameters, seeds, max epochs/selection/refit, weight decay/clipping | Reuse S4 and disclose any deviation, no retraining old models |
| Inputs | FT16 and any **verified** added causal features/peer context | Information-matched control if changed; avoid data duplication |
| Prediction horizon | Four *trading* hours, seven candidate origins unless user authorizes another h | Use genuine endpoints and existing OOS keys |
| Baselines | M1, frozen S4-T2R/NR if genuinely matched, **one strong identical-information simple comparator** | Differences in fitting support must be disclosed |
| Primary metric | Annual + equal-year daily Spearman IC, matched paired deltas | Same sessions/origins/stocks and midrank treatment |
| Secondary metrics | Top/bottom4, pair concordance, score/rank error, stability, mechanism-specific change | Do not mistake original Y MSE for rank-only model objective |
| Evaluation validity | F21–F24 descriptive post-search; protected 2026 closed | Month-block resampling only descriptive; no silent new OOS |
| Engineering scope | Bounded new neural starts, few essential tests/files, disk/RAM estimate, no extra dashboard | Last ledger130/200 is not permission to train |
| Decision/stop rule | One predeclared scientific comparison and one null/ablation; stop on true technical invalidity, not negative IC | Human review once before campaign; no automatic rescue |

## K. Primary project source register (internal archival citations)

The following precise project filenames should travel with this Markdown in the Project files so that a future chat can verify the historical facts and distinguish **planned** from **executed** content. Textual citations here refer to these local files, not public web links.

1. `HF20_LSTM_Comprehensive_Review_and_Expansion_Plan_2026-10-24.md` §§2–3, 5, 8, 12 and App C: 2025 sample, early experiment values, source quality, 10+3 and A1–A12.
2. `HF20_Focused_Second_Pass_Ranking_Inputs_Minute_Data_and_Horizons_2026-10-24.md` §§2–6, 8–13: rank target, price representation, S3 clock and magnitude distinction, diagnostic requirements.
3. `P028_Experiment_3_Final_Approved_Codex_Execution_Prompt.md` §§2–3: approved A7/A8/A12 exact operations, fitted P028 constants, selector, parameters and source-information limitation. `Pasted markdown (2)(7).md` / `Pasted markdown(20261024-135923).md`: postfit P028 actual ledger **62**, source/tail evidence.
4. `HF20_S1_S2_Staged_Ranking_Baselines_and_LSTM_Codex_Prompt_2026-10-25.md` §§1–3 and `HF20_S1_S2_Resume_After_LP_Failure_All_12_LSTM_Fits_Codex_Prompt_2026-10-25.md`: S1/S2 training objectives, rank selector, intended candidate set; **actual fit records prevail**.
5. `HF20_Monthly_Rank_IC_and_Recent_vs_Expanding_Linear_Codex_Prompt_2026-10-25.md`: separate monthly and recent36 linear questions; do not infer a rolling-LSTM execution.
6. `HF20_S3_Horizon_Comparison_and_Aligned_M2_Codex_Prompt_2026-10-25.md`, executed `S3_FINAL_RESEARCH_DECISION.md` (uploaded as `Pasted markdown(20261026-132856).md`) and annual delta table (`Pasted markdown(20261026-133236).md`): all genuine A/B h1/h2/h4 result splits and paired values.
7. `HF20_S4A_Revised_Codex_Prompt_S1_S2_Visuals_8_Neural_Starts_2026-10-26.md`, actual executed `S4_FINAL_RESEARCH_DECISION.md` (uploaded as `Pasted markdown(20261026-200251).md`), `S4_DETAILED_TRAINING_VALIDATION_REFIT_OOS.md` (uploaded as `Pasted markdown (2)(9).md`): seven-origin task, 8 fits, annual/selectors, rank-stability and dashboards.
8. `HF20_S5_S9_Combined_Bounded_Codex_Execution_and_Diagnostics_2026-10-26.md` (approved design) and **executed** S5/S9 report and index: actual 16/16 completed starts and four task comparisons. The numerical annual paired table was uploaded as `Pasted markdown(20261027-051232).md`; the full source/stock stratum CSV as `Pasted text (2)(1).txt`. The report names may live only in the local Codex repository, not among the project-file attachments.
9. `HF20_S9_MAG_LSTM_to_Options_Strategy_Research_Handoff_2026-10-27.md` (original; updated standalone v2 also generated): detailed S9-MAG backbone, transformed `log1p` magnitude objective, selected epochs and controls, calibration caveats, and separate **not-run** future options research.
12. `HF20_FT16_Complete_Feature_Specification.md` and `HF20_S9_MAG_Exact_Replication_Supplement.md`: read-only Codex source inspections at Git `5f7bb86a35d5aaff34ff79ef8f471117de6d3e42`, documenting FT16 formulas, data QA, source, S4/S9 role details, MAG numeric target/control values, training selector and saved artifact identities; verbatim snapshots included in Part III.
10. `HF20_LSTM_Architecture_Literature_Review_and_Research_Proposals_2026-10-26.md` §§1–13: N1–N6 formulas, input-matched comparators, prior-art/novelty limits. `Recurrent_Architecture_Research.md`, `State_Dependent_Signed_Recurrent_Interactions.md`, `Consolidated_Architecture_Design_Menu.md`: older C2–C4, memory/gates/interactions hypotheses.
11. `Track_A_Architecture_Experiment_Roadmap_First_Pass_FROZEN_v1.0.md`, `Track_A_Consolidated_Implementation_Design_Record_v1.2_2026-10-10.md`, `Track_A_Stage_Gated_Audit_and_Failure_Traceability_Plan_v1.1_2026-10-10.md`: original five-stock A-E ladder and historical audit protocol, **not an instruction to reimpose excessive engineering overhead** on new HF20 experiments.

**Archival closing rule:** If a later repository discovery contradicts a figure or “NOT_RUN” status here, append a **dated correction/addendum with the exact executed evidence path**, retain earlier version, and never silently massage historical numbers. If future actual training progresses beyond **130/200**, update the ledger in a dated addendum, not by retroactively assigning new starts to old programs. **No additional diagnostics, trading backtest or architecture fits are authorized by merely saving this document.**

---

**END OF PART I–II HISTORICAL ARCHIVE / NOVEL-ARCHITECTURE HANDOFF (v3; 27 October 2026). Full executed-code method extracts follow in Part III.**

---

# PART III — EXECUTED-CODE FORMULAS, BAD-DATA PROTOCOL, AND S9-MAG REPLICATION SOURCE ARCHIVE

## L. Consolidated source-document authority and methodological reproduction boundary

**Extraction provenance (27 October 2026):** The two appended Codex documents report inspection of repository HEAD `5f7bb86a35d5aaff34ff79ef8f471117de6d3e42` (branch `feat/track-a-data-intake`), executed S4/S9 artifacts and saved configuration/recipe files. These descriptions were **not independently reproduced on the original numerical datasets** in this documentation session. Their local-code references and values are source-derived, not new empirical findings. Actual executed artifacts always prevail on discrepancies. Their statements that “only this document was created” refer to their original *read-only extraction tasks*, not to the present consolidation.

**Scope and source hierarchy:** Part I–II's 10+3, legacy model-screen, A1–A12, S0–S11, S1–S5/S9 and N1–N6 status/result discussions remain intact; they are **not** reclassified based solely on the new source inspection. Part III instead supplies the exact **executed S4/S9 inputs and S9-MAG method** previously absent in the archival record. Most P026/P027 individual hyperparameters and the first 62 start-ID ledger still require the separate historic repository receipts. Claims of exact re-computation or trading profitability are not added.

For practical independent research the documented formulas, treatment and fitting rules are sufficient to implement analogous experiments on the linked publicly hosted source, subject to historical-source-quality qualifications. Reproducing the old original numerical tensors/scores requires the complete source/receipt/event/role/checkpoint bytes retained by the original implementation. **No raw prices, protected-2026 observations, neural training or additional backtesting were accessed or run for this document update.**

## M. Complete original FT16 implementation extraction (preserved source)

#### HF20 FT16 Complete Feature Specification

Extracted 2026-10-27 from existing implementation, fitted recipes and completed-run records at Git commit `5f7bb86a35d5aaff34ff79ef8f471117de6d3e42` (branch `feat/track-a-data-intake`). This describes the **minute-derived HF20/P019B/P020 experiments**, especially completed **S4-A and S9-MAG**, rather than the proposed hourly USA500 research protocol. FT16 contains own-stock information; it has no USA500 channel, stock ID, sector, raw price-level channel or future label channel.

Only this document was created. No training, downloads, dataset reconstruction, new scientific audits, tests or static checks were run. Existing completion/verification receipts below are historical evidence, not checks rerun for this extraction. The explicit single-file scope supersedes the repository's additional session-report-file convention.

##### 1. Authority and exact artifact locations

The following directory aliases are used only to shorten references in this document; all paths are repository-relative.

| Alias | Exact directory |
| --- | --- |
| `P019B` | `reports/data_audit/ta019b_action_qa_2026-10-22_201224` |
| `P020` | `reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122` |
| `S12` | `reports/experiments/hf20_s1_s2_continuation_2026-10-25_204117` |
| `S3` | `reports/experiments/hf20_s3_live_2026-10-26_010204` |
| `S4` | `reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation` |
| `S59` | `reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation` |

**Executed evidence takes precedence over proposal labels.** Despite its directory name and the frozen card's `PROPOSED_...` kind, `S4/S4_LIVE_FINAL_VERIFICATION.json` records eight completed neural runs, eight prefix recipes, zero failures and unchanged approved execution. Individual `S4/HF20-S4A-F{21..24}-H4-{NR,T2R}-S42/PASS.json` and saved calibration/refit configurations establish execution. `S59/HF20-S9-F{21..24}-H4-MAG-S42/configuration.json` records `input_dim:16`, seed 42 and execution SHA256 `e19fc1da419d6456d16a7dec7777bc7e1400b2d0412be65ba116906d01cfd73e`; each has a completed `PASS.json`.

`S59/S4_REUSED_RECIPES.json` binds the **eight actual S4 input recipes**, `S4/F{21..24}_{inner,refit}_recipe.json`, by saved SHA256. S9's per-run `inner_target_recipe.json` and `refit_target_recipe.json` are **task/label recipes**, not replacement FT16 scalers. The executed path `hf20_s5s9.Data.phase()` loads the S4 input recipe directly.

Core identity is frozen in [configs/hf1m_long_ft16_v1.json](configs/hf1m_long_ft16_v1.json): feature ID `HF20_HF1M_LONG_v1_FT16_v1`; source `mito0o852/OHLCV-1m`, revision `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`; action namespace `HF20_HF1M_LONG_v1_ACTION_QA_v1`. `P020/model_input_contract.json` binds source-derived stores, grid, origins, targets and `train_only_fit_recipes.json`; later annual runs reuse the formula family with earlier, fold-specific recipes.

Fixed stock-axis order: `VZ, COP, BAC, BA, AAPL, PEP, MRK, SBUX, CVX, MS, AMD, KO, JNJ, AMZN, XOM, WFC, AVGO, TSLA, MA, CSCO`.

##### 2. Notation, source fields and clocks

For stock \(i\), \(t\) indexes **scheduled, non-stub, completed RTH full-hour positions**, ordered by UTC time. An ordinary session contributes six bars, 09:30–10:30 through 14:30–15:30 Eastern. The final 15:30–16:00 stub is excluded from FT16. Early-close sessions contribute their available full hours; no overnight/weekend bars are inserted. UTC timestamps and `America/New_York` session dates preserve DST/calendar ordering.

- \(O_t,H_t,L_t\): adjusted hourly `open`, `high`, `low`. Open requires the genuine first minute at the scheduled start. High/low are extrema of genuine, unquarantined observed minutes; any quarantine in the hour masks both extrema. A partial observed range is not certified complete-hour high/low.
- \(C_t\): **`close_input_cap5`**, genuine terminal-minute close when available, otherwise the permitted causal terminal close proxy. It is used by OC, B2, T1 and indicators. Distinguish \(G_t=\texttt{close}\), which requires the genuine minute at `hour_end_utc - 1 minute` and is used for daily closes and historical-return endpoints.
- \(U_t\): `volume_for_feature`, derived from `observed_volume`; never price-proxy volume. Units are as-reported source shares. Quality rules are in §4.
- \(D_k\): genuine \(G\) at 15:30 on the \(k\)-th ordinary six-full-hour session. This uses the 15:29 minute's close; it is a **15:30 surrogate**, not the exchange's 16:00 daily close. Earlier missing hours do not invalidate an independently genuine terminal close. Early-close sessions are excluded from this daily series.
- \(W_k\): sum of the six \(U\) values on regular session \(k\), only if all six are finite and share one volume regime. This is six-hour observed/lower-bound volume, not full-session exchange volume.
- \(k(t)\): last regular-session index **strictly before the session containing \(t\)**. All daily components below use this index, including on early-close input days. Set \(d_k=\log(D_k/D_{k-1})\), masking price-basis transitions.
- \(\operatorname{Mean}_{n,m}(x)\), \(\operatorname{RMS}_{n,m}(x)\): last **n scheduled positions**, at least **m finite values**, no run of three missing positions within the window, and no result before n positions exist. Means divide by the number of observed values; RMS is \(\sqrt{\operatorname{mean}(x^2)}\), not demeaned standard deviation. Missing positions remain indexed.

Define \(a_t=\log(C_t/O_t)\), \(s_{12,t}=\operatorname{RMS}_{12,12}(a)_t\), \(s_{60,t}=\operatorname{RMS}_{60,57}(a)_t\), and \(s_{63,k}=\operatorname{RMS}_{63,60}(d)_k\). These hourly RMS values include the current completed hour. Let \(h_i,\delta_i,b_i\) be the fitted hourly, daily and M2 floors; \(q^h_{i,r},q^d_{i,r}\) are fitted volume pseudocounts for the current share regime \(r\), as defined in §4.

Source: `src/lstm_data/hf_minute_long_qa.py:60–88` (`calendar_frame`), `hf1m_action_source.py:67–95,141–248` (`price_factors`, `adjust_prices`, `derive_month`), `hf1m_ft16_math.py:15–33,84–191` (`rolling`, `regime_rolling`, `build`).

##### 3. All 16 native features, in tensor order

Names in code are the IDs below; parenthetical descriptions explain their economic meaning. Formulas are **before affine scaling/fallback**. All 16 outputs are dimensionless. Log returns use natural logs and decimal returns, not percentages or basis points; no volatility annualization is applied.

| # / exact name | Exact native formula | Source fields and lookback | Native units / special rule |
| --- | --- | --- | --- |
| 1 **M1** (hourly momentum) | \(a_t/\max(s_{60,t},h_i)\) | Current `open`, `close_input_cap5`; 60 scheduled hourly OC returns, ≥57 valid | Volatility-normalized return; current OC is included in RMS60 |
| 2 **M2** (same-origin historical momentum) | \(\mu^{(o)}_{20,i,t}/\max(s^{(o)}_{60,i,t},b_i)\) | Genuine historical same-origin endpoint log returns: mean over 20 prior regular-origin days, ≥19 valid; RMS over 60, ≥57 valid | Normalized historical return, session-start locked; exact context/horizon rules below |
| 3 **M3** (five-session momentum) | \(\log(D_k/D_{k-5})/[\sqrt5\max(s_{63,k},\delta_i)]\) | Prior genuine regular-session closes; 5 return intervals plus 63 daily-return RMS positions, ≥60 valid | Volatility-normalized return |
| 4 **M4** (skip-month momentum) | \(\log(D_{k-20}/D_{k-125})/[\sqrt{105}\max(s_{63,k},\delta_i)]\) | Prior genuine daily closes, 105 return intervals ending 20 regular sessions before k; needs close lag 125; daily RMS63 as above | Volatility-normalized return; not a 125-session cumulative return |
| 5 **V1** (short volatility) | \(\log\max(s_{12,t},h_i)\) | `open`, `close_input_cap5`; 12/12 hourly OC returns | Log of decimal-return RMS |
| 6 **V2** (long volatility) | \(\log\max(s_{60,t},h_i)\) | Same fields; 57/60 hourly OC returns | Log of decimal-return RMS |
| 7 **V3** (volatility ratio) | \(V1_t-V2_t\) | Same fields; 12/60 hourly windows | Log short/long floored RMS ratio |
| 8 **B1** (range) | \(\log(H_t/L_t)\) | Current observed adjusted `high`, `low` | Log price ratio; may describe a partial observed range |
| 9 **B2** (close location) | \((2C_t-H_t-L_t)/(H_t-L_t)\) | Current `close_input_cap5`, `high`, `low` | Zero if width is zero; nonfinite width or absolute result >\(1+10^{-10}\) → missing, **not clipped** |
| 10 **Q1** (same-slot relative volume) | \(\log[(U_t+q^h_{i,r})/(\bar U^{slot}_{20,t}+q^h_{i,r})]\) | Current usable hourly volume; mean of previous 20 occurrences of the same scheduled slot, ≥19 valid, current value excluded | Log share-volume ratio; previous slot occurrences can include early-close sessions; all dependencies must match current share regime |
| 11 **Q2** (daily volume trend) | \(\log[(\operatorname{Mean}_{5,5}(W)_k+q^d_{i,r})/(\operatorname{Mean}_{60,57}(W)_k+q^d_{i,r})]\) | Six-hour daily volumes from prior regular sessions; 5/5 and 57/60 | Log share-volume ratio; regime-consistent windows |
| 12 **T1** (moving-average distance) | \(\log[C_t/\operatorname{Mean}_{20,19}(D)_k]\) | Current `close_input_cap5`, 20 prior regular-session closes | Log price ratio; daily mean stays within one price basis |
| 13 **T2** (daily sign trend) | \(\operatorname{Mean}_{20,19}(\operatorname{sign}(d))_k\) | Genuine prior daily closes; 20 daily-return positions, ≥19 valid | Bounded [−1,1]; exact zero return has sign 0 |
| 14 **T3** (short EMA spread) | \((E_{6,t}-E_{18,t})/C_t\) | `close_input_cap5`; recursive EMA6/18, with ≥360 post-seed EMA updates and recent coverage gate | Relative price spread |
| 15 **T4** (long EMA spread) | \((E_{24,t}-E_{72,t})/C_t\) | Same field; recursive EMA24/72, same warmup/coverage gate | Relative price spread |
| 16 **T5** (normalized RSI) | \((\operatorname{RSI}_{14,t}-50)/50\) | Successive `close_input_cap5` price differences; 14 seed changes + ≥140 subsequent Wilder updates, recent coverage gate | Bounded [−1,1]; special zero-gain/loss rules below |

Formula authority: `src/lstm_data/hf1m_ft16_fit.py:49–76` (`native`) and `hf1m_ft16_math.py:123–229` (`build`). The order is `hf1m_ft16_source.py:15–17`, not alphabetical order. M3/M4 momentum numerators require their specified endpoints; the code does not add a separate completeness requirement over all 5/105 intervening closes.

###### M2: historical labels used only after maturity

For P020/S1/S2, context \(o=0\) is the 10:30 origin and \(o=1\) is 11:30. On prior regular day j,

\[
R^{(o)}_{i,j}=\log\left(G_{i,p_j[o+4]}/G_{i,p_j[o]}\right),\quad
\mu^{(o)}_{20,i,t}=\operatorname{Mean}_{20,19}(R^{(o)})_{k(t)},\quad
s^{(o)}_{60,i,t}=\operatorname{RMS}_{60,57}(R^{(o)})_{k(t)}.
\]

Here \(p_j[0..5]\) are that day's six full-hour positions. Endpoints must be genuine and price-basis compatible. The forecast's context is held fixed across **all 48 historical steps**, but each step uses its own preceding-day history. It is not a current forecast's future return repeated into the sequence.

S4/S9 use seven contexts: `0..5 = 10:30,11:30,12:30,13:30,14:30,15:30`, `6 = 09:30`. Historical R is the genuine endpoint return over **240 XNYS trading minutes**, including closing stubs and pausing across closures; later origins can mature next session. Opening R uses the genuine first-minute **open**, not close. For each historical input session, only prior regular-origin days enter; an endpoint whose `label_maturity_utc >= current session 09:30` is masked **within its original scheduled slot**. In particular, the latest overnight outcome is not available merely because its origin day is yesterday. Apply the same 20/60 count/gap rules; values are locked for that entire input session. Early-close input days use preceding regular-origin dates with the same maturity test. COP dependency masks also apply.

Authority: `hf1m_ft16_math.py:157–159,214–229`; `hf20_s4_clock.py:18–70`; `hf20_s4_preflight.py:143–212,219–250`. S3-B's verified horizon substitution is described in §6.

###### EMA and RSI state, exactly

For each period p ∈ {6,18,24,72}, seed \(E_p=C\) at the first valid close; thereafter \(E_{p,t}=\alpha_p C_t+(1-\alpha_p)E_{p,prev}\), \(\alpha_p=2/(p+1)\). The first seed does **not** increment `ema_updates`. T3/T4 require `ema_updates >= 360`. All T3/T4/T5 outputs additionally require a valid current close and ≥69 valid closes in the last 72 scheduled positions with maximum missing run two; the full 72 positions must exist.

RSI seeds average gain/loss with arithmetic means of positive/negative parts of the first 14 valid predecessor-connected price changes. Each later connected change Δ updates \(A=(13A+\max(\Delta,0))/14\), \(B=(13B+\max(-\Delta,0))/14\). After ≥140 such post-seed updates, \(RSI=100-100/(1+A/B)\). Normalized output is 0 when A=B=0, +1 when only B=0, −1 when only A=0.

A missing close freezes EMAs and clears the RSI predecessor. Before RSI seeding it also clears seed changes; after seeding it preserves gain/loss averages but creates no change across the gap. Three consecutive invalid scheduled full-hour closes reset the entire indicator state; a price-basis change also resets it. Normal overnight closure is not a missing scheduled observation. Authority: `stock_features.py:44–96` (`IndicatorState`); `hf1m_ft16_math.py:192–213`.

##### 4. Preprocessing, fitted parameters and fallback

###### Price, volume and missingness policy

P019B adjusts **OHLC prices only** backward for verified splits through 2026-03-31; prices are split-consistent, not dividend-total-return adjusted. Volume remains in observed share units. COP's 2012-05-01 spinoff separates price bases; the 125-regular-session dependency history plus 48-step envelope is masked. Split share regimes separately reset incompatible volume ratios. No unverified inverse split-volume conversion is applied. See `configs/hf1m_action_qa_v1.json`, `configs/hf1m_p019_verified_event_facts_v1.json`, `hf1m_action_source.py:67–95,237–256`, `hf1m_action_release.py:208–236`, and S4's equivalent `hf20_s4_preflight.field_masks():25–54`.

P019B removes 18 unresolved RTH minutes; genuine expected opens/closes can survive independently, but affected-hour high/low are masked and volume is unusable. No close proxy is allowed in a quarantined hour. Elsewhere `close_input_cap5` can reuse an original causal terminal proxy with missing-run cap five. Proxy creation uses a preceding observed close, never interpolation from a later bar, and rejects no-observation/action-blocked bins; carry state resets each session. The completed bin's known gap length determines acceptance; a later-discovered longer outage cannot rewrite an earlier trailing proxy. See `hf_minute_long_qa.py:92–118,395–403` and `hf1m_action_source.py:210–234`.

Usable hourly volume requires at least one genuine minute, ≤5 absent minutes, longest gap ≤5 minutes, and **zero conflicts, quarantines and invalid minutes**. Absent-minute zero is a feature-only assumption: observed sums remain lower bounds, not evidence of no trades. Otherwise \(U_t\) is missing. Real observed zero volume is retained. Daily W requires all six usable hours and compatible volume bases; stub volume is excluded. Q1's prior matching slots and Q2's daily windows cannot mix share regimes. Missing or unseen fitted pseudocount regimes produce native missingness, then feature fallback. Authority: `hf1m_ft16_math.py:36–63,147–191`.

###### Fitting population and numerical rules

For each fold/phase, the fit-hour set F is the **union** of all 48 scheduled history keys of `source_input_eligible` origins in that training prefix, clipped to `[2011-04-01, fit_stop_inclusive]`. No overlapping-window multiplicity and no label-value filter are used to choose feature-fit keys. Warmup components may use source history from July 2010, but those pre-start keys are excluded from fitted input statistics. For daily floor and M2 pools, J is the first F timestamp per input session (`drop_duplicates("session_date_et")`), including eligible early-close input days.

| Fitted quantity | Exact estimation |
| --- | --- |
| Hourly floor \(h_i\) | NumPy 5th percentile of strictly positive finite RMS12 **concatenated with** RMS60 at F, separately per stock (a timestamp can contribute both RMS values) |
| Daily floor \(\delta_i\) | NumPy 5th percentile of positive finite carried RMS63 values at J, separately per stock |
| M2 floor \(b_i\) | Weighted 5th percentile of positive finite M2 RMS values at J, separately per stock; context total mass 1/2 for original two-context runs, 1/7 for S4/S9; equal weights within each context's valid values |
| Hourly/day volume pseudocount | 0.01 × median positive finite volume, separately per stock and share regime. Hour pool uses F; daily pool uses **all regular days** in `[2011-04-01, stop]`, not just J. Both hour and day positive pools must exist for that regime |
| Common-channel center/scale | Native finite values pooled across stocks and unique F timestamps, independently for each of the 15 non-M2 channels; no window/session-loss weighting |
| M2 center/scale | Native finite stock/session/context values at J, pooled across stocks with equal total mass per context (1/2 or 1/7), not weighted by forecast-slot frequency |

An unweighted quantile uses `np.quantile` / `np.percentile` default linear interpolation. A weighted quantile sorts values stably and selects the first value whose normalized cumulative weight is ≥q (`searchsorted(..., side="left")`); it does not interpolate. Missing all required positive/native training pools raises an error; it does not borrow another stock's floor or another regime's pseudocount.

For each of the **13 unbounded channels** (M1/M2/M3/M4/V1/V2/V3/B1/Q1/Q2/T1/T3/T4), let c be its native training median and MAD = median(|x−c|), using the above weights for M2. Use scale s = MAD if positive; otherwise `(Q75−Q25)/1.349`; otherwise population SD about the mean; otherwise exactly 1 for a constant. **MAD is unscaled**, without a 1.4826 factor. Replace nonfinite native x with c, then output `(x−c)/s`. Consequently these fallbacks become model-space zero. Fit statistics use native values **before imputation**.

**B2/T2/T5:** replace nonfinite values by neutral 0; center 0/scale 1, `BOUNDED_IDENTITY`. There is **no input clipping, winsorization, asinh/log1p mapping of the full tensor, or per-sequence normalization**. Feature-specific logarithms and denominator floors are already part of the native formulas. Final arrays are cast to `float32`; component arithmetic generally uses NumPy floating arrays. Native-missing/fallback/proxy/quality masks remain separate diagnostic data, not extra FT16 channels. A missing required input close cannot be repaired by feature median fallback to admit a deficient 48-close window. Targets have no feature-style imputation.

Authority: `hf1m_ft16_fit.py:12–46,49–187`; S4 seven-context counterpart `hf20_s4_fit.fit_expanded():13–125`; recipe application `hf20_s4_witnesses.scaled():19–32`; prefix selection `hf20_s4_data.py:105–157` and `hf20_ranking_data.py:189–243`.

###### Actual saved fitting windows

S4 and S9 use the following eight input recipes. Every start is **2011-04-01**; an inner recipe is applied unchanged to inner validation, and a refit recipe unchanged to that fold's OOS year. All exact floors, pseudocounts, scalers, native fallbacks and fit-hour indices are in the corresponding `S4/Fxx_phase_recipe.json` (`floors`, `scalers`, `fallbacks`, `fit_hour_indices`).

| Fold / OOS year | Inner inclusive stop | Refit inclusive stop | Unique F timestamps inner / refit | Unique J sessions inner / refit |
| --- | --- | --- | --- | --- |
| F21 / 2021 | 2020-06-30 | 2020-12-31 | 13,102 / 13,864 | 2,198 / 2,326 |
| F22 / 2022 | 2021-06-30 | 2021-12-31 | 14,567 / 15,247 | 2,445 / 2,560 |
| F23 / 2023 | 2022-06-30 | 2022-12-30 | 15,991 / 16,716 | 2,684 / 2,808 |
| F24 / 2024 | 2023-06-30 | 2023-12-29 | 17,420 / 18,164 | 2,926 / 3,052 |

Original P020 preparation's `P020/train_only_fit_recipes.json` instead has inner stop **2023-01-23** and refit stop **2025-06-30**. Those are not the annual S4/S9 recipes and must not be substituted for them. S1/S2 annual recipes also share the earlier cutoffs above but have different input-key populations, e.g. F21 inner has 13,057 F timestamps / 2,197 J sessions rather than S4's 13,102 / 2,198.

##### 5. Exact 48-step sequence and leakage controls

For an admitted origin, set `first_step = entry_index − 47`. Gather the 48 consecutive scheduled grid positions `first_step + arange(48)` in chronological order. The common 15 fields depend on stock and historical timestamp; M2 additionally selects the **forecast-origin context for every historical step**. In S4, `assemble()` returns `[origins, 20 stocks, 48 steps, 16 features]`, `float32`, in §3 order. The LSTM receives stock sequences reshaped to `[origins×20,48,16]`; weights are shared across stocks, and hidden/cell states start at zero on every call. No recurrent state carries from an overlapping prior sequence.

At a full-hour forecast, the last step is the bar ending at that origin. At conditional **09:30**, the last step is the most recent prior-session full-hour bar (normally ending 15:30, or 12:30 on an early close). Neither the new day's 09:30–10:30 bar nor the opening price is inserted into FT16. The opening price is a genuine reference for labels only. Thus 48 means scheduled trading observations, **not 48 elapsed clock hours**, and feature calculations can require substantially older history.

Input eligibility requires all 20 stocks to have 48 finite cap5 input closes, the daily-history warmup (`day_index >=125`, allowing the required 126 prior regular-session closes), ≥360 cumulative genuine hourly closes, and the COP dependency envelope. Other native channel deficiencies use the declared feature fallback. Input eligibility is computed independently of future endpoint validity; supervised/evaluation membership additionally requires a complete eligible 20-stock label panel. S4's final `eligible` combines its source and label masks, rather than manufacturing missing endpoints.

Issuance is assumed at origin +2 minutes; label maturity at genuine endpoint +2 minutes. S4 endpoints consume 240 actual trading minutes and may include overnight closure; the price-only return starts at the nominal origin, **before issuance**, and is not an executable fill return. For a normal 10:30 forecast the newest feature bar covers 09:30–10:30; for 09:30 issuance at 09:32, inputs still end with the prior session's last full hour. Publication latency is an assumption, not verified historical availability.

Daily statistics always use prior regular days, Q1 shifts same-slot history by one occurrence, all rolling functions are backward-looking, and M2 maturity is checked at **each historical input session**, not just at the current prediction time. Scalers/floors/fallbacks are prefix-only and fixed for the relevant validation/OOS phase. Split admission requires the first of all 48 input steps to be after the preceding boundary (48-full-step embargo), and labels to mature before their role cutoff. S4 additionally retains the conservative four-hour boundary limit: cutoff-day local midnight +1 day −4 hours, with `label_maturity_utc < limit`. Future outcomes remain labels except for strictly matured historical outcomes used in M2.

Authority: `hf20_s4_preflight.input_valid():57–67` and `run():235–255`; `hf20_s4_witnesses.assemble():35–56`; `hf20_s4_data.S4Data:32–76,159–178`; `hf20_s4_epoch.py:47`; `neural_engine.SharedLSTM:28–54`. Original two-slot gather: `hf20_ranking_data.assemble():24–49`. S4 clock: `hf20_s4_clock.schedule():39–70`.

##### 6. Are S1–S9 identical?

**No: stable feature IDs/economic meanings do not imply identical contexts, fitted parameters or complete model inputs.**

| Stage | Verified executed input treatment |
| --- | --- |
| S1 | Baselines consume the original two-context FT16 path; full-history ridge uses the 48-step information. Not every control uses all channels: N1/N2 use M1/sign reversal; N0/P are constant/profile controls. See `S12/S1_FOUR_FOLD_RANKING_BASELINES.md` and `S12/Fxx_phase_recipe.json` |
| S2 | Same two-context FT16 recipe family and per-fold inputs as S1 for T2R/NR/PW; objectives differ, not feature formulas. Failed F21 PW is preserved and has no completed refit/OOS surrogate. See `S12/S2_FOUR_FOLD_LSTM_RANKING_COMPARISON.md`, `hf20_ranking_data.py` |
| S3-A | H1/H2 labels change, but all 16 input channels, including original **four-hour M2**, reuse S1/S2 phase recipes. H4 references are archived runs, not new fits |
| S3-B | **Only M2 changes** to historical same-origin H1 or H2 genuine endpoint returns; mean20/RMS60, gap rules, two contexts and 50/50 pooling remain. M2 floors, fallback center and scaler are refitted on the original unique input-prefix day keys. Other 15 channels remain unchanged. Saved `S3_M2` overrides are authoritative; inherited top-level M2 fields are lineage, not the active B parameters |
| S4-A | Same 15 non-M2 native formulas; **seven M2 contexts**, 240-trading-minute endpoint/maturity handling and prior48 opening inputs. Feature-fit origin/key support expands, so even common-channel fitted floors/scalers can differ from S1/S2. M2 pooling changes to equal 1/7 context mass. NR and T2R share these phase recipes |
| S5 | Reuses S4 FT16 unchanged, then appends **six clock fields**, making **22 model inputs**: `step_sin`, `step_cos`, `session_boundary`, `elapsed_scheduled_wall`, `origin_sin`, `origin_cos`. Scheduled elapsed time is not observed-price age; source-repair flags are not model features |
| S6–S8 | **NOT VERIFIED as executed FT16 experiments.** Latest completed S5/S9 handoff explicitly states no S6/S7/S8 was launched; no identical-feature assertion is justified for those stages |
| S9-MAG / EVENT / QUANTILE | Exactly S4's 48×16 input and saved phase recipes, no S5 extra metadata. Different label/head/objective definitions do not change FT16 |

S3 evidence: `S3/EXECUTION_MANIFEST.json`, `S3/S3_FINAL_RESEARCH_DECISION.md`, `S3/{A,B}/Fxx_H{1,2}/Fxx_phase_recipe.json`; `hf20_horizon_data.py:42–45,92–164`; `hf20_horizon_math.py:98–175`. In B, apply `S3_M2.floors` and `S3_M2.scaler`. Older `hf20_s3_horizons_2026-10-26_000127_preparation` documents marked NOT_RUN predate completed live execution and do not establish final run status.

S5/S9 evidence: `hf20_s5s9.py:23–51,82–131`; S6–S8 status: `S59/LIVE_WORK_SESSION_REPORT.md`, §16. For MAG specifically, the optimized target is `log1p(abs(R)/magnitude_scale)`, with prefix-fitted magnitude scale; this is **not a feature transformation** (`hf20_s5s9.py:60–67,141–179`). Likewise the target-transform term **T2/T2R/asinh is distinct from FT16 feature T2**, the daily sign average.

##### 7. Source map for replication

Line ranges refer to source at the extraction commit; paths below are exact. No module listed here was executed for this extraction.

| File | Relevant implementation / evidence |
| --- | --- |
| `configs/hf1m_long_ft16_v1.json:1–91` | Source revision, symbols, feature ID/order, warmup/splits, volume tier, timing assumptions; original P020 recipe defaults |
| `configs/hf1m_action_qa_v1.json` and `configs/hf1m_p019_verified_event_facts_v1.json` | Frozen price adjustment, quarantine and event facts; volume regime policy |
| `src/lstm_data/hf1m_action_source.py:67–95,141–309` | Price split factors, genuine-hour aggregation, quarantines, cap5 terminal input-close selection |
| `src/lstm_data/hf_minute_long_qa.py:48–118,395–403` | Minute validity, session-hour grid, causal bounded proxy rules |
| `src/lstm_data/hf1m_action_masks.py:39–41,49–108` | Scheduled full-window AND, original source warmup/basis eligibility |
| `src/lstm_data/hf1m_action_release.py:208–236` | P019B volume-basis and COP dependency overlay |
| `src/lstm_data/hf1m_ft16_source.py:13–17,24–101` | Exact order/bounded IDs, source allowlists and identity checks |
| `src/lstm_data/hf1m_ft16_math.py:15–63,84–232` | Rolling rules, quality-conditioned volume, all source components/daily alignment/original M2 |
| `src/lstm_data/stock_features.py:44–96` | Actual imported EMA/Wilder state; other legacy feature calculators are not this pipeline |
| `src/lstm_data/hf1m_ft16_fit.py:12–187` | Quantiles, robust scales, positive floors, native 16-channel formulas and original two-context fitting |
| `src/lstm_data/hf1m_ft16_prepare.py:47–102,129–154` | P020 origin/window timing, input-only fitting keys, separate target parameters |
| `src/lstm_data/hf20_ranking_data.py:24–49,75–140,189–273` | S1/S2 gather, annual split masks and actual prefix recipes |
| `src/lstm_data/hf20_s4_clock.py:10–83` | XNYS schedule, actual trading-minute endpoints, seven contexts and issuance/maturity |
| `src/lstm_data/hf20_s4_preflight.py:25–67,70–140,154–212,235–255` | P019B-equivalent masks, permitted monthly source inventory, expanded M2 and prior48 opening indices |
| `src/lstm_data/hf20_s4_fit.py:13–125` | Executed S4 seven-context fitting implementation (historical docstring still says proposed) |
| `src/lstm_data/hf20_s4_witnesses.py:19–56` | Apply sealed scales and gather exact float32 48×16 tensors |
| `src/lstm_data/hf20_s4_data.py:32–76,90–178` | Fold maturity/embargo, fitting keys, saved recipe application and role guards |
| `src/lstm_data/hf20_s4_run.py:30–45` | Actual source adapter loads card-selected `opening_reaudit_v2` source/endpoint stores and replaces M2 components with seven-context values |
| `src/lstm_data/hf20_s5s9.py:82–131` | S9 reuses exact S4 recipes; only S5 appends metadata |

For byte-exact input replication, preserve the **saved recipe**, not just the written formulas. Resolve the recorded monthly inputs from `P019B/adjusted_hourly_manifest.json` and `S4/opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv`. The adjusted-hourly root is `data/processed/hf20_hf1m_long_v1_action_qa_v1/ta019b_action_qa_2026-10-22_201224/hourly/`. S4 source/role identities are in `S4/opening_reaudit_v2/S4_ORIGIN_SOURCE_ELIGIBILITY.parquet`, `S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet` in that same subdirectory, and `S4/Fxx_{inner_train,inner_validation,refit,oos}_indices.csv`.

Existing scalar/tensor evidence: `P020/independent_oracle_and_causality.json`, `P020/preparation_execution_snapshots/hf1m_ft16_{math,fit,source,prepare,loader}.py.txt`, and `S4/opening_reaudit_v2/{S4_ARCHIVED_ALL16_TENSOR_IDENTITY,S4_ALL16_SCALAR_SOURCE_WITNESSES}.csv`. These are supporting historical records; archived original-recipe tensor identity does **not** mean newly fitted S4 recipes equal S1/S2 recipes. S9 input-recipe SHA identities are recorded in `S59/S4_REUSED_RECIPES.json`.

##### 8. NOT VERIFIED / replication qualifications

- **NOT VERIFIED — historical publication latency and point-in-time availability.** Config explicitly sets `publication_timing_verified:false`; two-minute issuance is assumed. Arithmetic cutoffs/maturity controls do not certify that a vendor delivered each minute, opening quote or correction by that time.
- **NOT VERIFIED — historical action-information vintage.** Executed OHLC uses backward split factors through March 2026 and known quarantine/event facts. This is the implemented retrospective representation; it does not prove those facts were known contemporaneously. Scale invariance and stored causal-prefix evidence do not independently certify historical publication timing.
- **NOT VERIFIED — economic meaning of missing minute volume, complete extrema and share-volume adjustment.** Small absent gaps are assumed zero only for features. Provider absence versus no trading is unresolved; observed ranges/volumes can be incomplete. No independently verified inverse split-volume convention exists, so replication must retain share-regime masking rather than invent an adjustment.
- **NOT VERIFIED — bitwise reproduction on another machine from this document alone.** Exact source bytes, recorded adjusted-hourly/endpoint stores, fitted numerical recipes, grid order and compatible NumPy/pandas/calendar versions remain necessary. This extraction did not reopen numerical datasets, rerun hash audits, reconstruct tensors or validate a clean-machine replay. Existing manifests/receipts supply recorded identities, not a fresh certification. Private source accessibility/redistribution is not established here.
- **NOT VERIFIED — S6/S7/S8 executed definitions.** The latest completed handoff says they were not launched; proposals cannot supply executed definitions. No feature equality claim is made for them.

No unknown formula or parameter was filled from a generic indicator library, older source branch, proposal or inferred research preference. Numerical input parameters are available in the cited saved recipes; they are phase-specific, not universal constants omitted from the implementation.


## N. Complete original S9-MAG executed-method replication supplement (preserved source)

#### HF20 S9-MAG Exact Replication Supplement

Documentation extraction, 2026-10-27; inspected repository HEAD `5f7bb86a35d5aaff34ff79ef8f471117de6d3e42`, branch `feat/track-a-data-intake`. Scope: the four completed seed-42 **HF20 S9-MAG** lifecycles, F21–F24. This is an exploratory retrospective absolute-return-magnitude experiment, with no trading simulation or protected-2026 evaluation.

The executed code, saved recipes, role indices, configurations, checkpoint contents and binding records govern this specification. The existing [FT16 specification](HF20_FT16_Complete_Feature_Specification.md) supplies the detailed 16-feature formulas; this supplement specifies their S9-MAG application. Only this new document was written. Checkpoints were deserialized for inspection without model construction, forward inference or updates. No downloads, preprocessing, training, audits or tests were run, and no existing files were changed. The explicit one-file request overrides the additional session-report-file convention.

##### 1. Identities and authoritative artifacts

These aliases below denote exact repository-relative directories, not alternate sources.

Unless explicitly identified as PyTorch package code, an unprefixed Python module reference such as `hf20_s5s9.py:60–67` means `src/lstm_data/hf20_s5s9.py` at those lines in the inspected repository version.

| Alias | Directory |
| --- | --- |
| `A18` | `reports/data_audit/ta018d_hf1m_long_2026-10-22_155547` |
| `P019B` | `reports/data_audit/ta019b_action_qa_2026-10-22_201224` |
| `P020` | `reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122` |
| `S4` | `reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation` |
| `S9` | `reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation` |
| `MAGxx` | `S9/HF20-S9-Fxx-H4-MAG-S42`, xx ∈ {21,22,23,24} |

All four `MAGxx/configuration.json` record the same input dimension 16, seed 42, initialization identity and execution hash. Each has `PASS.json`, two target recipes, two checkpoint bindings and four saved role score/metric bundles. `S9/S5_S9_VERIFICATION.json` records all 16 campaign lifecycles completed, including these four MAG runs. Do not substitute rehearsal outputs, proposal-only receipts or other S9 objectives.

- Source revision: `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`.
- Action namespace: `HF20_HF1M_LONG_v1_ACTION_QA_v1`; feature ID: `HF20_HF1M_LONG_v1_FT16_v1`.
- S9 execution SHA256: `e19fc1da419d6456d16a7dec7777bc7e1400b2d0412be65ba116906d01cfd73e`.
- S4 execution SHA256: `a737c9219513ddbbfffb882a2e76af7708e2f3ee55a297e1b145790bc47f2a95`.
- Recorded preparation/live-session starting Git HEAD: `960b81753036366522dbbd61189d4e4d51d25967` (`S9/START.json`, `reports/codex_sessions/2026-10-27_005216_hf20_s5_s9_live_final.md`). Execution included then-uncommitted files; that Git SHA alone is insufficient. Use the recorded execution hash and artifact bindings.

`src/lstm_data/hf20_s5s9_run.py:36–46` defines the S9 code hash from the S4 execution identity plus the `hf20_s5s9*` files; `hf20_s4_authority.py:21–41` defines the underlying source bundle. `S9/design.json`, `LIVE_AUTHORITY.json`, `EXECUTION_STARTED.json`, `S4_REUSED_RECIPES.json` and the v23 journal `reports/audit/track_a_real_pairs_v23_hf20_s5_s9.jsonl` bind the actual campaign. Earlier preparation status is not final execution status.

##### 2. Dataset, acquisition and historical clock

###### Provider, files and request semantics

The source is the Hugging Face dataset uploaded under **`mito0o852/OHLCV-1m`**: [dataset page](https://huggingface.co/datasets/mito0o852/OHLCV-1m). **NOT VERIFIED:** the uploader's original exchange/vendor feed, consolidation/feed tier, historical correction vintage and independent completeness certification. This was not an Alpaca, TwelveData, Yahoo or course USA500 download.

Acquisition code uses these immutable endpoints, where `REV` is the revision above and `YYYY-MM` the selected provider month:

```text
https://huggingface.co/api/datasets/mito0o852/OHLCV-1m/revision/REV
https://huggingface.co/api/datasets/mito0o852/OHLCV-1m/tree/REV?recursive=true&limit=1000
https://huggingface.co/datasets/mito0o852/OHLCV-1m/resolve/REV/data/ohlcv_YYYY-MM.parquet
```

There are **no server-side ticker/date/adjustment/bar-size query parameters**. Code scans monthly Parquet ticker columns and filters exact strings locally. Sparse reads add `?range_start=START&range_end=END` and HTTP `Range: bytes=START-END`, `Accept-Encoding: identity`; all seven source columns are selected from relevant row groups, `use_threads=False`. If projected selected-group compressed bytes exceed 75% of file size, the code uses a complete-month streamed download and its pinned SHA256 instead. Range reads validate returned range/size; full downloads validate complete size/hash. HTTP uses no login/credentials, `trust_env=False`, no automatic retries; recorded redirects/requests and per-month strategies are in `A18/months/YYYY-MM/{http_events.jsonl,raw_receipt.json,row_groups.json}` and the complete manifest. The threshold is a transport choice, not a sample filter.

Authority: `src/lstm_data/hf_minute_long_io.py:188–258,261–305,309–438` (`verify_remote`, `selected_table`, `stream_full`, `acquire_month`), `hf_minute_boundary_io.py:17–18,22–75` (`RemoteParquet`), `hf_hourly_source.py:41–104` (`PublicHTTP`).

**Stock-axis order, preserved everywhere:**

```text
VZ COP BAC BA AAPL PEP MRK SBUX CVX MS AMD KO JNJ AMZN XOM WFC AVGO TSLA MA CSCO
```

This fixed surviving-stock cohort is not historical index membership; survivorship/issuer lineage remains a qualification. No OOS performance-based stock selection is implemented in these runs.

###### Distinguish acquired history from S9-used history

| Layer | Exact date/month policy |
| --- | --- |
| Activated minute acquisition | 189 monthly files, July 2010–March 2026; manifest `A18/complete_acquisition_manifest.json`. Earlier legacy acquisitions are excluded from the active source |
| P020 preparation | Warmup 2010-07-01–2011-03-31; original training 2011-04-01–2025-06-30; development 2025-07-01–2025-12-31; protected 2026-01-01–2026-03-31 |
| **S9 numerical source** | **Only July 2010–December 2024** monthly adjusted-hourly and genuine-minute partitions; no 2025 tuning or protected-2026 numerical access/hash. Source inventory: `S4/opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv` |
| S9 fitted samples | Expanding training prefixes beginning 2011-04-01; annual OOS years 2021,2022,2023,2024; exact admitted dates in §4 |

Nominal source bounds do not imply every stock/minute exists. Preserve the per-stock missingness and exact saved origin indices. The full stock/minute tape was not independently re-read for this document; per-symbol first/last genuine-minute timestamps are **NOT VERIFIED here**. Existing per-session coverage is bound by `A18/ticker_session_hour_coverage_manifest.json`.

###### Timestamp and minute-to-hour construction

Raw schema is `timestamp: timestamp[ns,UTC]`, float64 `open,high,low,close,volume`, and string `ticker`; source rows/file/row-group identities are appended without overwriting raw values. The pipeline interprets timestamps as **minute starts**. Calendar is `exchange_calendars` **XNYS**, with actual holidays, early closes and DST. RTH minute starts are `[session.open, session.close)`; ET dates use `America/New_York`. Noncalendar/extended observations remain source evidence but do not enter hourly features or endpoint anchors.

Bins are anchored at 09:30 ET: offsets `floor(minute_of_session/60)`. Normal full hours are 09:30–10:30 through 14:30–15:30; a separate 15:30–16:00 stub is retained in source processing but excluded from FT16. A normal full-hour close at 10:30 means the close of the **10:29 minute**. Genuine hourly open requires an observation at the scheduled first minute; genuine close requires `hour_end−1 minute`. High/low are extrema of safe observed minute highs/lows, volume their sum. Partial observed extrema are not certified complete-hour extrema. Empty/missing scheduled positions remain indexed.

Authority: `src/lstm_data/hf_minute_boundary.py:70–80,223–237` (`validate_schema`, `session_grid`), `hf_minute_long_qa.py:48–88`, `hf1m_action_source.py:141–204` (`derive_month`); S9 source loader `hf20_s4_preflight.py:70–140`.

###### Corporate actions and point-in-time limitations

Prices are backward split-consistent OHLC in the March-2026 share basis: for each applicable split at date e, divide prices strictly before e by `factor_denominator`; multiply factors when needed. Volume is unchanged. There is no dividend/total-return adjustment or fabricated inverse split-volume adjustment. The exact event facts are `configs/hf1m_p019_verified_event_facts_v1.json`, used by `configs/hf1m_action_qa_v1.json`.

Applied splits: KO 2012-08-13 ×2; MA 2014-01-22 ×10; AAPL 2014-06-09 ×7 and 2020-08-31 ×4; SBUX 2015-04-09 ×2; TSLA 2020-08-31 ×5 and 2022-08-25 ×3; AMZN 2022-06-06 ×20; AVGO 2024-07-15 ×10. COP's 2012-05-01 spinoff has no invented multiplicative adjustment: preserve levels in separate PRE/POST price bases and exclude dependent histories crossing the boundary. Split dates create separate as-reported share-volume regimes.

Authority: `src/lstm_data/hf1m_action_source.py:67–95,237–256`; COP/volume masks `hf1m_action_release.py:208–236`, S4 equivalent `hf20_s4_preflight.field_masks():25–54`.

**NOT VERIFIED:** historical arrival/publication times of bars, openings, corporate-action facts and corrections. Factors/quarantine decisions are retrospective. `configs/hf1m_long_ft16_v1.json` explicitly records `publication_timing_verified:false`. Origin+2-minute issuance is a proxy, not an exchange execution timestamp. Dataset access was based on human-reported maintainer permission for private research; redistribution and independent data rights are not certified by this supplement.

##### 3. Data quality: source treatment versus feature treatment

###### Source detection, filtering and correction

1. Parse timestamps in UTC; reject NaT, non-minute alignment and rows whose ET month differs from their file month. Require finite OHLCV, positive OHLC, nonnegative volume, high ≥ every OHLC value and low ≤ every OHLC value. Preserve genuine zero volume and rare/extreme candles otherwise.
2. Exact duplicates across the seven original fields collapse to one canonical observation. If distinct versions share `(ticker,timestamp)`, **all versions are excluded**, not first/last selected or averaged. Raw records remain immutable. The activated full-history acquisition report records no invalid raw rows or exact-copy duplicates, but 856 conflicting records / 406 keys excluded; these are full-source counts, not S9-only sample counts.
3. Compare expected XNYS minute grid against canonical observations to flag absence, conflict/invalid minutes, missing opens/closes, longest gaps, no-observation bins and coverage outside first/last source dates. No pre/post-coverage price history is invented.
4. Source QA flags absolute adjacent genuine-close changes >`log(1.25)` across overnight/month boundaries, genuine zero volume, and 30 consecutive same-OHLC zero-volume observations. These flags alone do not delete a genuine market move. Large jumps block original proxy creation in the affected bin.
5. P019 scans additional event candidates using: ALL_SESSION adjacent close and open/previous close; RTH adjacent close; minute body `abs(log(close/open))>log(1.25)`; minute high/low >1.5; session first-30/previous-session last-30 observed-close median ratio outside `[1/1.25,1.25]`. Comparisons are strict. Session medians are retrospective diagnosis only. External evidence/manual dispositions, not an automatic return cap, decide action treatment.
6. P019B's 67 candidate IDs resolve to 17 split-adjusted candidates, 4 genuine moves retained, 18 unresolved RTH minutes locally quarantined, 24 EH out-of-scope candidates, 3 KO mixed-basis premarket candidates excluded from RTH influence, and the COP spinoff boundary. Do not remove every detected jump. All five fields of the 18 RTH minutes are excluded; 14 affected hourly bins are reaggregated. Independently genuine scheduled opens/closes may survive; high/low and volume quality are untrusted, and **no proxy is allowed anywhere in an anomaly-containing hour**.

Exact dispositions/timestamps are in `P019B/unresolved_event_ledger_v3.json`, bound by `canonical_event_ledger_pointer.json` to SHA256 `015d672c11d61b3a14441a2abbfb689ffa59191016398bdc32bb580524a0b937`. This ledger, not the summary counts, reproduces the exclusions. Quality tiers are diagnostic metadata; the eventual S4 origin mask is the actual admission rule.

Sources: `src/lstm_data/hf_minute_long_qa.py:48–57,176–240,306–440`; `hf1m_action_audit.scan_stock():110–174`; `configs/hf1m_p019_action_scan_v1.json`; `hf1m_action_source.event_dispositions():98–138` and `derive_month():141–309`. Acquisition findings: `reports/codex_sessions/2026-10-22_184817_ta018d_hf1m_long.md`.

###### Input close proxies and feature-level fallback

Original cap5 proxies are a separate derived layer, not genuine raw bars. A missing run can reuse its preceding observed close only when its completed-bin known length, including a leading carry gap, is ≤5 minutes. No future-price interpolation, overnight carry, no-observation-bin fill or action-blocked-bin fill occurs; state resets per session. A trailing short run remains accepted under the information known at that completion even if the next bin reveals a longer outage. P019B uses only a permitted terminal proxy for `close_input_cap5`, split-adjusted like prices; genuine `close` remains separate. Proxy OHLC/zero-volume placeholders do not become genuine extrema or observed volume. Sources: `hf_minute_long_qa.bounded_hour_proxies():92–118,395–403`; `hf1m_action_source.py:210–234`.

FT16 order is `M1 M2 M3 M4 V1 V2 V3 B1 B2 Q1 Q2 T1 T2 T3 T4 T5`; exactly 48 full-hour steps, no S5 clock metadata. Apply `S4/Fxx_{inner,refit}_recipe.json` as-is; `S9/S4_REUSED_RECIPES.json` records all eight hashes. Important distinctions from source cleaning:

- Hour volume is usable only with >0 genuine minutes, ≤5 absent minutes, longest gap ≤5, zero conflicts/quarantines/invalid minutes. Absent-minute zero is a feature-only assumption; volume remains an observed lower bound. Otherwise volume-derived channels become native missing. Daily volume requires six usable full-hour sums in one share regime; stubs excluded.
- Rolling windows keep scheduled gaps: required counts include 12/12 or 57/60 hourly OC returns, 60/63 daily returns, 19/20 matching-slot histories; maximum two consecutive misses. Indicators freeze/disconnect on missing closes and reset after three invalid full-hour positions or basis transitions. Full EMA/RSI seeding rules are in the FT16 specification and `stock_features.IndicatorState():44–96`.
- Fitted floors and volume pseudocounts use unique input-only eligible training-prefix keys; hourly/day volume pseudocounts are 1% of positive training medians by stock/share regime. An unfitted regime stays native missing. M2 uses matured prior regular-origin returns, seven contexts pooled equally 1/7, mean20/RMS60 with 19/20 and 57/60 coverage. No current or immature future outcome enters M2.
- Thirteen unbounded channels use native pooled median/unscaled MAD, then IQR/1.349, population SD, or constant scale 1 if necessary. Native nonfinite values receive the fitted center; B2/T2/T5 instead receive neutral zero and identity scale. No winsorization, input clipping or per-sequence normalization. B2 outside `1+1e-10` in absolute value is missing, not clipped. Masks stay outside the tensor.
- Feature fallback does not repair a deficient 48-input-close window to admit it. COP's 125-regular-session dependency plus 48-step envelope remains excluded. All fitted statistics are phase-specific, never fitted on validation/OOS. The original P020 2025-refit recipe must not replace S4's earlier annual recipes.

Authority: `hf1m_ft16_math.py:15–63,84–232`, `hf1m_ft16_fit.py:12–76`, `hf20_s4_fit.fit_expanded():13–125`, `hf20_s4_witnesses.py:19–56`, `hf20_s4_data.py:105–157`. See [HF20_FT16_Complete_Feature_Specification.md](HF20_FT16_Complete_Feature_Specification.md) for exact feature-by-feature mathematics.

###### Missing target endpoint prices

Targets require **positive finite genuine prices for all 20 names** at both exact endpoints, plus COP price-basis compatibility. A missing/quarantined endpoint in one stock invalidates the **entire origin's 20-stock label panel**. No target median fill, price proxy, forward/backfill, nearest-time substitution, external daily price or endpoint shift is used. Historical bad/missing endpoints similarly leave scheduled holes in M2, subject to its coverage/fallback rules. Missing intermediate hour/16:00 closes can make decomposition unavailable without invalidating a direct return whose two exact endpoints are genuine. Authority: `hf20_s4_clock.complete_prices():73–77`; `hf20_s4_preflight.py:143–151,219–268`; `hf20_s4_opening.py:145–160`.

##### 4. Samples, splits, maturity, embargo and weights

###### Origin and sequence construction

Candidate regular-session ET clocks are **09:30,10:30,11:30,12:30,13:30,14:30,15:30**, only when strictly before the actual session close. Context IDs are 6 for opening, then 0–5 for the six full-hour ends. From nominal origin t consume **240 actual XNYS trading minutes**, including closing stubs and pausing across overnight/weekend/holiday closures. Normal exits for the seven clocks are respectively 13:30,14:30,15:30 same session, then 10:00,11:00,12:00,13:00 next session. Early closes use the same trading-minute algorithm.

Opening entry is the genuine **09:30 minute open**; other entries and all exits use the genuine close of the minute starting one minute before the endpoint. Issuance is t+2 minutes and label maturity endpoint+2 minutes. Returns start before assumed issuance and are price-only outcomes, not realizable fill returns.

At full-hour origin t, `entry_index` maps to its completed-hour grid row; at opening, it is the previous completed full hour (normally prior session 15:30; early close 12:30). `first_step=entry_index−47`; gather exactly those 48 scheduled chronological full hours. No opening price or unfinished 09:30–10:30 bar enters FT16. M2 uses the forecast context throughout the sequence, with history locked separately at each historical input session's open.

Source admission: every stock has all 48 finite cap5 closes, sufficient daily warmup (`day_index>=125`), ≥360 cumulative genuine hourly closes and no active COP dependency crossing. Other feature deficiencies use their allowed fallback. Final origin `eligible` combines that input mask with complete20 endpoint eligibility and session date ≥2011-04-01. Supervised label validity does not determine the feature-fit input-key population.

Sources: `hf20_s4_clock.py:10–83`, `hf20_s4_preflight.py:57–67,154–212,219–268`, `hf20_s4_witnesses.assemble():35–56`, `hf20_s4_run.source_data():30–45`.

###### Nominal chronological roles

All inner/refit starts are 2011-04-01. Validation is the last six **calendar** months before the OOS year; no random sample split. These date windows are followed by the source/maturity/embargo filters.

| Fold | Inner inclusive stop | Nominal validation | Refit inclusive stop | Nominal OOS |
| --- | --- | --- | --- | --- |
| F21 | 2020-06-30 | 2020-07-01–2020-12-31 | 2020-12-31 | 2021-01-01–2021-12-31 |
| F22 | 2021-06-30 | 2021-07-01–2021-12-31 | 2021-12-31 | 2022-01-01–2022-12-31 |
| F23 | 2022-06-30 | 2022-07-01–2022-12-30 | 2022-12-30 | 2023-01-01–2023-12-31 |
| F24 | 2023-06-30 | 2023-07-01–2023-12-29 | 2023-12-29 | 2024-01-01–2024-12-31 |

For validation, require the **first of its 48 input steps** to have session date strictly after the inner cutoff; for OOS strictly after the refit cutoff. This is a 48-scheduled-step input embargo, not a fixed elapsed-hour or calendar-day gap. All roles also require `label_maturity_utc < local_midnight(cutoff)+1 day−4 hours`. Cutoff is inner stop for inner training, refit stop for validation/refit, and December 31 of OOS year for OOS. Preserve the conservative four-hour cutoff even when the actual endpoint matures earlier. For F23 refit, for example, cutoff uses December 30, not the weekend December 31. Validation must have ≥50 sessions and ≥25 origins in each of seven contexts.

Exact mask implementation: `src/lstm_data/hf20_s4_data.py:32–76`. Exact samples are `S4/Fxx_{inner_train,inner_validation,refit,oos}_indices.csv`; do not recreate membership from the date table alone. S9 inherits these populations unchanged.

###### Actual saved support and admitted date bounds

Bounds below are first/last admitted **origin ET session dates**, not label-exit dates. Counts are saved in `S9/S5_S9_ROLE_COUNTS.csv`, `S4/opening_reaudit_v2/S4_FOLD_ROLE_SLOT_COUNTS.csv`, and each `MAGxx/role_metrics.json`; bounds were read from the saved role indices.

| Fold | Role | Admitted date bounds | Sessions | Origins | Stock rows |
| --- | --- | --- | ---: | ---: | ---: |
| F21 | inner_train | 2011-04-01–2020-06-30 | 2,100 | 11,449 | 228,980 |
| F21 | inner_validation | 2020-07-13–2020-12-30 | 120 | 674 | 13,480 |
| F21 | refit | 2011-04-01–2020-12-30 | 2,227 | 12,171 | 243,420 |
| F21 | oos | 2021-01-13–2021-12-31 | 188 | 955 | 19,100 |
| F22 | inner_train | 2011-04-01–2021-06-29 | 2,331 | 12,716 | 254,320 |
| F22 | inner_validation | 2021-07-22–2021-12-31 | 92 | 457 | 9,140 |
| F22 | refit | 2011-04-01–2021-12-31 | 2,423 | 13,173 | 263,460 |
| F22 | oos | 2022-01-12–2022-12-30 | 210 | 1,180 | 23,600 |
| F23 | inner_train | 2011-04-01–2022-06-30 | 2,547 | 13,896 | 277,920 |
| F23 | inner_validation | 2022-07-13–2022-12-30 | 86 | 453 | 9,060 |
| F23 | refit | 2011-04-01–2022-12-30 | 2,640 | 14,395 | 287,900 |
| F23 | oos | 2023-01-13–2023-12-29 | 187 | 887 | 17,740 |
| F24 | inner_train | 2011-04-01–2023-06-30 | 2,740 | 14,945 | 298,900 |
| F24 | inner_validation | 2023-07-14–2023-12-29 | 87 | 350 | 7,000 |
| F24 | refit | 2011-04-01–2023-12-29 | 2,835 | 15,332 | 306,640 |
| F24 | oos | 2024-01-11–2024-12-31 | 208 | 991 | 19,820 |

Refit can admit boundary observations omitted from embargoed validation; it is not necessarily the union of inner_train and inner_validation.

###### Weighting

For a role with D admitted sessions, n_d admitted origins on session d, and all 20 names, stock-row mass is **`1/(D*n_d*20)`**. Each session has equal total weight, origins equal within session, stocks equal within origin. The same formula fits magnitude scales and GLOBAL/STOCK controls; it is not uniform weighting of every row across the history. `hf20_ranking.origin_weights():39–41`; `hf20_s5s9_metrics.weights():15–16`. Annual report summaries average years equally rather than pooling unequal annual sample sizes.

##### 5. Magnitude target, inversion and three controls

For exact genuine endpoints, let `R=log(P_exit/P_entry)` and `A=abs(R)` in decimal log-return units. In each fold/phase fit

\[
s_A=\max\{Q^{w}_{0.5}(A),10^{-8}\},\qquad m=\log(1+A/s_A).
\]

The pooled weighted median uses the stock-row weights above; sort stably and select the first observed value whose normalized cumulative weight is ≥0.5 (`searchsorted(...,side="left")`), without interpolation. Inner parameters use **inner_train** only; refit parameters use **refit** only. Saved tail/NUM/MAD thresholds are diagnostic cohort definitions, not additional target clipping or loss weights.

A scalar unconstrained head predicts `m_hat`; optimized row loss is `(m_hat−log1p(abs(R)/s_A))²`. R is not cross-sectionally demeaned or divided by MAD for MAG. TG20, epsilon and asinh Z are retained as companion diagnostics but **do not enter the MAG loss**. The FT16 feature named T2 is unrelated to the T2R target transform.

For reporting/inference, retain raw `prediction_m=m_hat` and decode once:

\[
\widehat A=s_A\operatorname{expm1}(\max(\widehat m,0)).
\]

Only the inverse lower-clamps predicted m at zero. There is no upper cap, target winsorization, output ReLU in the model, smearing/Jensen correction, sign reconstruction or portfolio mapping. This estimates transformed magnitude; its inversion is not an unbiased conditional expected absolute return. Sources: `hf20_s5s9.py:60–67,141–175`, `hf1m_ft16_fit.quantile():12–20`, `hf20_s5s9_metrics.decode():29–36`.

###### Exact phase parameters

These are the full saved decimal values from `MAGxx/{inner,refit}_target_recipe.json` and `{inner,refit}_GLOBAL_control.json`.

| Fold | Inner magnitude scale | Refit magnitude scale | Inner GLOBAL m | Refit GLOBAL m |
| --- | ---: | ---: | ---: | ---: |
| F21 | 0.005797117684325846 | 0.0058994931438253 | 0.7807054887617804 | 0.7804020257437488 |
| F22 | 0.0059347355198145265 | 0.005957669984582455 | 0.7800440769243104 | 0.7795002079091725 |
| F23 | 0.0060897938914411046 | 0.006150424755601047 | 0.780037173411231 | 0.779600015468851 |
| F24 | 0.006174065175292481 | 0.0061703009229596 | 0.7786992711980216 | 0.7780814265022555 |

###### Control definitions

**GLOBAL:** fitted weighted mean of m over all training stocks/origins/sessions, broadcast to every evaluation row. **STOCK:** one fitted weighted mean m per stock, averaging origins with session-normalized weights. Both are means in **transformed space**, not mean raw A transformed afterward. Each phase's training coefficients remain fixed for its evaluation roles; all controls use exactly the neural run's eligible keys and phase scale.

**VOL:** parameter-free, `inner_VOL_control.json` and `refit_VOL_control.json` are `{}`. At the last input step decode the actual scaled/imputed float32 V2 channel through its frozen affine recipe:

\[
\sigma=\exp(V2_{scaled}\,s_{V2}+c_{V2}),\qquad
\widehat m_{VOL}=\log(1+2\sqrt{2/\pi}\,\sigma/s_A).
\]

Thus decoded raw magnitude is `2*sqrt(2/pi)*sigma`. Sigma is the **floored RMS60 of hourly open-to-close returns, or its native feature fallback**, as represented in the consumed tensor; do not recompute a new close-to-close or overnight volatility. The multiplier is fixed, with no fitted regression, cross-sectional rho, quantile bins or optimization for MAG. EVENT/QUANTILE control rules in the shared module do not apply.

Authority: `hf20_s5s9.Data.volatility():133–138`; `hf20_s5s9_metrics.fit_control():223–242`, `control_raw():268–273`; `hf20_s5s9_report.finish_run():264–305` explicitly bypasses fitting MAG/VOL.

###### Exact STOCK coefficients (predicted m)

Column I is inner, R is refit; row order is the fixed stock axis. Values are transcribed at saved JSON precision from `MAGxx/{inner,refit}_STOCK_control.json`, key `value`.

| Ticker | F21 I | F21 R | F22 I | F22 R | F23 I | F23 R | F24 I | F24 R |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| VZ | 0.6279239829544796 | 0.6167956218897865 | 0.6111868859978398 | 0.6063645879065321 | 0.6024794237421662 | 0.6046993122653715 | 0.6059534101854324 | 0.6095732038337187 |
| COP | 0.8649228246455933 | 0.8724123331712701 | 0.8774437958724485 | 0.8790176260826301 | 0.8821195316836852 | 0.8833155990178297 | 0.8819279444737617 | 0.8794144093456454 |
| BAC | 0.8509585259857807 | 0.8470046027304942 | 0.844737468828631 | 0.8432745197123446 | 0.8394720347706234 | 0.8360168331262082 | 0.8338673165986042 | 0.832847367223927 |
| BA | 0.7966578398437266 | 0.8086393844849904 | 0.8153904119609365 | 0.8178858106957089 | 0.8281163642465779 | 0.8301363982847985 | 0.8300477165844106 | 0.8272891594421045 |
| AAPL | 0.762259958350848 | 0.7668212840001577 | 0.7659805582226921 | 0.7645625328609627 | 0.7646081352111939 | 0.7659347484636029 | 0.7640595384640354 | 0.7620176374449703 |
| PEP | 0.565912532805736 | 0.5648754603141318 | 0.5659250521473685 | 0.5653923959861803 | 0.5640893187456197 | 0.5625970823939321 | 0.5612584301086677 | 0.561035513490638 |
| MRK | 0.6741091901021926 | 0.6701630347400371 | 0.667412713954337 | 0.668873895831577 | 0.6644209539481736 | 0.6623056013718924 | 0.6615410830249369 | 0.6615497094326539 |
| SBUX | 0.7314813757620817 | 0.7287625934246942 | 0.7284180320590486 | 0.7261141528792093 | 0.7291581860787641 | 0.7293217552223225 | 0.7261484641294293 | 0.723533801072121 |
| CVX | 0.7326044265457307 | 0.7396449233417284 | 0.7416967422315551 | 0.7410215533593928 | 0.7437594466866562 | 0.7443197027187195 | 0.7434080032876285 | 0.7421434290692308 |
| MS | 0.8976736246286194 | 0.8898513329895162 | 0.8866560083235383 | 0.8849190527579411 | 0.8813116625956565 | 0.8766079526679454 | 0.8714132807655216 | 0.868096573895736 |
| AMD | 1.1911804336055587 | 1.1772892041545568 | 1.1670303861878246 | 1.1672819676126576 | 1.1637840329612998 | 1.160878067363297 | 1.1589997956606992 | 1.1594172176638717 |
| KO | 0.570023040151916 | 0.5727389014919869 | 0.5716668398804869 | 0.5706262058399103 | 0.5702301894840448 | 0.5705492777806171 | 0.5674047345594221 | 0.5660014792851307 |
| JNJ | 0.5805823030395609 | 0.5791104007215112 | 0.5772595748116877 | 0.5749511118049682 | 0.572624189050347 | 0.5694789506076492 | 0.5669630970276622 | 0.5679642971461746 |
| AMZN | 0.831234442505602 | 0.8308253448121442 | 0.8273375170467794 | 0.8240723685425374 | 0.8280194274407634 | 0.8332842721975509 | 0.8365133962841659 | 0.8395944352310111 |
| XOM | 0.6831851437157815 | 0.6950894615572155 | 0.7031660567018804 | 0.7075932994665731 | 0.7147017937655964 | 0.717080032403105 | 0.720006334757303 | 0.7216554265287107 |
| WFC | 0.7386934820054066 | 0.7473715869489501 | 0.7523987584500912 | 0.7565053289432724 | 0.7612790087609722 | 0.7606807716835553 | 0.7632459085306618 | 0.7640994163630038 |
| AVGO | 0.920097330904426 | 0.9070145791019004 | 0.9044769678994897 | 0.8978844391551416 | 0.8934294269451727 | 0.8890947107655133 | 0.8867874504318067 | 0.888056011922942 |
| TSLA | 1.1358787529448477 | 1.1412772017239643 | 1.1417226649210317 | 1.1399749670634702 | 1.1409808347983368 | 1.1421804962722573 | 1.1459934731875774 | 1.1466114252491153 |
| MA | 0.7335556318096461 | 0.734229336479566 | 0.7366476156145039 | 0.7407029121166331 | 0.7449162758797422 | 0.7437195827768808 | 0.741231959503208 | 0.7363643441421157 |
| CSCO | 0.7251749329280699 | 0.7181239267963748 | 0.7143274873740106 | 0.7129854295657729 | 0.7112432314292202 | 0.7097991619939825 | 0.707214086395472 | 0.7043636722622822 |

##### 6. Model, optimization, selection and refit

###### Executed hyperparameters and initialization

| Item | Executed setting |
| --- | --- |
| Architecture | Shared unidirectional `nn.LSTM(input_size=16,hidden_size=32,num_layers=1,batch_first=True)`, default biases, no projection; scalar `nn.Linear(32,1)` head |
| Sequence | 48×16 per stock; no stock embedding, peer/market input, persistent hidden/cell state, padding or truncated-state carry |
| Readout/dropout | Last hidden state, `nn.Dropout(0.10)`, then affine head; this is readout dropout, not inter-layer recurrent dropout |
| Parameter count | 6,433: 6,144 LSTM matrix +32 head matrix elements; 256 LSTM bias +1 head bias elements |
| Seed | Exactly 42; Python `random`, NumPy legacy RNG and `torch.manual_seed`; `torch.use_deterministic_algorithms(True)` |
| Initialization | PyTorch 2.10.0 defaults; no custom Xavier/orthogonal/forget-bias override. LSTM parameters uniform ±1/√32; Linear uses `kaiming_uniform_(a=√5)` and uniform bias ±1/√32. Preserve constructor order: LSTM, dropout, head |
| Initial parameter identity | `1e6f1b81ccd0286b5da1eb7c47ffff1702ae8b677f34c2058f7538417bc928bc` for all four runs |
| Device/numerics | CPU float32 model and training inputs/targets; no AMP, GPU/MPS or mixed precision; 4 intra-op threads, 1 inter-op thread |
| Optimizer | AdamW, fixed lr 0.001, betas (0.9,0.999), eps 1e−8, AMSGrad false; no scheduler/warmup |
| Weight decay | 0.01 for all 2-D matrices (including head); 0 for 1-D biases |
| Gradient rule | One global L2 `clip_grad_norm_(...,1.0,error_if_nonfinite=True)` per optimizer step; nonfinite loss/gradient/weights fail closed |
| Batches | 16 complete admitted sessions; all their eligible origins and all 20 stocks; keep final shorter session batch; no accumulation or replacement sampling |
| Epoch policy | Minimum 12 calibration epochs before stopping, maximum 60, patience 10; exact qualifying loss rule below |

Sources: `src/lstm_data/neural_engine.py:18–57,159–171`; `hf20_s5s9.model_for():40–51`; `hf20_s5s9_run.py:224–320,348–378,512–513`; each run's saved configuration. Default initialization was also inspected in the installed `torch==2.10.0` package's `torch/nn/modules/rnn.py:RNNBase.reset_parameters` and `torch/nn/modules/linear.py:Linear.reset_parameters`.

All four refit checkpoint contents have float32 tensors: `lstm.weight_ih_l0[128,16]`, `weight_hh_l0[128,32]`, `bias_ih_l0[128]`, `bias_hh_l0[128]`, `head.weight[1,32]`, `head.bias[1]`. Saved AdamW groups additionally record `maximize=False`, `foreach=None`, `capturable=False`, `differentiable=False`, `fused=None`, `decoupled_weight_decay=True`. Preserve defaults/CPU backend rather than enabling fused/foreach execution independently.

###### Exact epoch order and objective reductions

Group the selected role positions by ET session date, sort dates, then for epoch n shuffle with a **fresh `np.random.default_rng(42+n)`**. Group indices retain original chronological origin order; flatten origin-major then stock-major into `[origins*20,48,16]`. Every batch calls `model.train()`, clears gradients, computes per-stock transformed squared error, averages the 20 stocks, and weights each origin by `1/(number_of_sessions_in_this_batch * origins_on_its_day)`. Sum to one scalar and take one optimizer step. There is no extra full-history scaling of the final short batch's gradient. Phase-specific day lists make refit batches different, but the same epoch-number shuffle seeds are reused. There are no DataLoader workers; the runner directly constructs batches.

After every calibration epoch, `predict()` evaluates the **entire** inner-training and validation roles with dropout off, `torch.inference_mode()`, batches of 32 origins, and unchanged chronological sample order. Selection's `off()` loss recomputes targets from R cast to float32 and reduces stock mean, then full-role session-normalized origin weights. Online training loss is reported separately; it is not the selection statistic.

Saved score exports later recompute row loss in float64 from saved float32 predictions and original float64 R, then aggregate with row weights. Therefore last-digit differences between validation traces and saved diagnostic metrics are expected; do not use exported float64 losses to reconstruct the stopping rule. Sources: `hf20_s5s9_run.predict/off/epoch():189–320`; `hf20_s5s9_metrics.make_frame():173–220`.

###### Selector and actual completed epochs

`objective_screen_run.Selector:40–65` is the imported MAG selector. First finite nonnegative loss qualifies. Later validation L qualifies only when **`L <= 0.999*best_qualified_loss`**; equality qualifies. A qualifying epoch replaces selected epoch/best and resets patience, otherwise patience increments. Independently track the raw numerical minimum. Stop when epoch≥12 and patience≥10, else at epoch 60. The selected epoch can be less than 12 and need not equal the raw minimum. There is no rank-IC selection for MAG.

| Fold | Calibration stop | Selected / refit epochs | Raw-best epoch | Calibration optimizer updates | Refit updates | Saved qualified best validation loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| F21 | 37 | 27 | 30 | 4,884 | 3,780 | 0.27765695714096117 |
| F22 | 30 | 20 | 20 | 4,380 | 3,040 | 0.222935593875287 |
| F23 | 51 | 41 | 41 | 8,160 | 6,765 | 0.25486852119791253 |
| F24 | 37 | 27 | 27 | 6,364 | 4,806 | 0.20448313889638625 |

All stop statuses are `PATIENCE_STOP`. F21 raw-best loss was 0.2775669336205141 at epoch 30, insufficient to replace qualified epoch 27. Counts and losses above are recorded in `MAGxx/calibration_binding.json` and `refit_binding.json`; refit optimizer step counters were inspected in the four saved checkpoints.

###### Refit, checkpoint and inference rules

Each epoch saves `calibration_NNN.pt` containing model `state_dict` only. At calibration stop, `calibration_stop_optimizer.pt` contains the **stop-epoch** optimizer, not selected-epoch optimizer state. Reload selected calibration weights for both inner_train and inner_validation exports.

Then apply the refit FT16 recipe and refit magnitude scale; recreate the seed-42 model at the identical initial parameter hash and a fresh empty AdamW optimizer. Train the **whole admitted refit role** for exactly the selected number of epochs, with no further validation selection or OOS inspection. This is not fine-tuning the selected calibration weights. `refit_final.pt` contains `{model: state_dict, optimizer: optimizer_state_dict}`. Recreate a model, load saved model weights, and export refit/OOS from that final model; historical runner asserts exact prediction equality with checkpoint reload.

For inference use the matching fold's **refit** input recipe, magnitude scale, checkpoint and exact endpoint/source conventions. Set `eval()` and use the scalar head output without target inversion inside the LSTM. Apply the decode formula once afterward. Raw R, TG20 or future endpoint availability are not model input fields. Omitted LSTM h0/c0 are new zeros on every call.

Sources: `hf20_s5s9_run.neural():323–486`, `predict():189–202`, `neural_engine.SharedLSTM.encode():40–54`. The checkpoint serialization does not include full Python/NumPy/Torch RNG states; a bitwise resumed training procedure is not supplied by these files.

###### Saved checkpoint paths and recorded SHA256

Each filename below is under its corresponding `MAGxx/`; hashes are **recorded binding values**, not a fresh hash audit in this task.

| Fold | Selected calibration file | Recorded calibration SHA256 | Recorded `refit_final.pt` SHA256 |
| --- | --- | --- | --- |
| F21 | `calibration_027.pt` | `9b09865ab9e495f29b1cff69b7c4dc11d16949c873fafe88ead79453c66791b0` | `0cd6d35ef59be7ca184680de0489fdcf2d2b24871219594c18f49c1a213971e7` |
| F22 | `calibration_020.pt` | `c4c49eb12b396ad172ece5ac0c0e495380186e72c0b4166ff701a89ee193ccd8` | `2ce9c2f9c9036b9df3885ed2667c6b30bee68fac8e227fdcdc2be3ca274a7412` |
| F23 | `calibration_041.pt` | `5f06f005b7b48e55d6fa8ba307435c83f8cb041b8a32a1d300137323e884457a` | `97be88d97a7a350813f03dadc2fcb95ecefcd0aaee945e30f985a7cd81632b8b` |
| F24 | `calibration_027.pt` | `cc86cf4a7d41408e0e5e46ed8a358d7b1d9e939c7ad0c37332d8ef6c13536c1f` | `3e985c2c2ab3042a5914513c6be34cbc9c2ddc4aaf54ba69fdccd84f8f26c1e8` |

##### 7. Reproduction entry points, artifacts and numerical qualifications

###### Required inputs and saved outputs

To reproduce existing scores using checkpoints, retain these exact artifacts and their recorded identities:

| Required layer | Paths / role |
| --- | --- |
| Source provenance | `A18/complete_acquisition_manifest.json`, `source_revision_manifest.json`, `months/YYYY-MM/*receipt.json`; raw selected minute path `data/raw/hf20_hf1m_long_v1/REV/raw_1m_selected/YYYY-MM.parquet` (REV as above) |
| Authoritative canonical minute QA | `data/processed/hf20_hf1m_long_v1/REV/qa_v2/canonical_observed/YYYY-MM.parquet`; original cap5 proxies/quality are separate `qa_v2/` stores. `qa_v2`, not earlier QA attempts, governs |
| P019B adjustment/exclusion layer | `P019B/adjusted_hourly_manifest.json`, event ledger/pointer, `pre_feature_gate.json`, field-mask manifest; adjusted hours under `data/processed/hf20_hf1m_long_v1_action_qa_v1/ta019b_action_qa_2026-10-22_201224/hourly/` |
| P020 lineage | `configs/hf1m_long_ft16_v1.json`, `P020/model_input_contract.json`, original `train_only_fit_recipes.json`; lineage only where superseded by S4 phase recipes |
| Actual S4 source/targets | `S4/S4_FROZEN_EXPERIMENT_CARD.json`; `S4/opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv`, `S4_ORIGIN_SOURCE_ELIGIBILITY.parquet`, `S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet` (all three in that subdirectory). Card-selected source is **opening_reaudit_v2** |
| Actual input fits/populations | Eight `S4/Fxx_{inner,refit}_recipe.json`; sixteen `S4/Fxx_role_indices.csv`; `S9/S4_REUSED_RECIPES.json` |
| MAG target/control/model | Per-run `configuration.json`, two target recipes, six control JSON files, two bindings, selected calibration checkpoint, `refit_final.pt` |
| Existing comparison outputs | Per-run `role_scores.parquet`, `role_metrics.json`, `role_KIND_control_scores.parquet`, `model_and_control_metrics.csv`, `RUN_DIAGNOSTICS.md`; root `S5_S9_ROLE_COUNTS.csv`, `S5_S9_VERIFICATION.json`, `artifact_inventory.csv` |

Actual `Data()` calls `hf20_s4_run.source_data(S4)`, loads the saved source/endpoint stores, rebuilds source components in memory and expands M2; it is not a standalone checkpoint-only inference CLI. This reconstruction was **not invoked here**. Source code: `hf20_s4_run.py:30–45`, `hf20_s4_preflight.py:70–140`, `hf20_s5s9.py:82–115`. The legacy P020 contract is also an inherited metadata dependency (`hf20_s4_data.py:23–30`; `hf20_ranking_data.metadata():52–72`). Private Parquets/checkpoints are intentionally ignored by Git; cloning alone does not supply them.

###### Actual commands and executable boundaries

Historical commands are documented for reproducibility, **not executed by this extraction**:

```bash
# Activated source acquisition/QA; A18 contains its state/identity prerequisites.
.venv/bin/python -B -m lstm_data.hf_minute_long --run --out reports/data_audit/ta018d_hf1m_long_2026-10-22_155547
# Adjusted source and original P020 feature preparation.
.venv/bin/python -B -m lstm_data.hf1m_action_source --out reports/data_audit/ta019b_action_qa_2026-10-22_201224
.venv/bin/python -B -m lstm_data.hf1m_ft16_prepare --out reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122
# Executed S5/S9 untrained preparation and complete live campaign.
.venv/bin/python -m lstm_data.hf20_s5s9_prepare --out reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation/preflight_v2
.venv/bin/python -u -m lstm_data.hf20_s5s9_run --out reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation
```

These are staged entry points, not a complete from-empty-directory recipe. P019B release/masks, original source QA state, S4's approved opening reaudit/fits and evidence bindings must already exist. Their historical creation commands and prerequisites are recorded in `reports/codex_sessions/2026-10-22_184817_ta018d_hf1m_long.md`, `2026-10-22_204909_ta019b_action_qa_release.md`, `2026-10-22_214605_ta020_hf1m_long_ft16_tg20.md`, `2026-10-26_125645_hf20_s1s2_visual_s4a_opening_preflight.md` and `2026-10-26_155600_hf20_s4a_live_final.md`.

The actual neural runner has only `--out`; **no MAG-only `--arm`, `--seed`, `--resume` or fold-selection argument exists**. It executes S5 F21–F24, then MAG F21–F24, then EVENT and QUANTILE. It requires frozen live authority/preflight/code/input bindings and rejects an existing journal or `EXECUTION_STARTED.json` (`hf20_s5s9_run.py:504–527`). Therefore the completed namespace is not restartable and its prior authority is exhausted. **NOT VERIFIED:** a turnkey independent training/inference CLI that bypasses this campaign lifecycle while preserving every rule; none was implemented for this documentation task.

Saved-output report entry points, distinct from training, are `scripts/summarize_s5_s9_saved_outputs.py --out S9` and `scripts/render_s5_s9_complete_views.py --out S9 --reuse-screenshots` (replace alias S9 with its full path). They write reports; they were not run under this read-only request.

###### Environment and bitwise identity

Authoritative setup route: repository `.venv`, `python -m pip install -e '.[dev,neural]'` (README); include `visualization` extra for Plotly reports. `pyproject.toml` requires Python ≥3.11,<3.15; NumPy ≥2.2,<3; pandas ≥2.3,<3.1; PyArrow ≥21,<24; exchange-calendars ≥4.11,<5; requests ≥2.32.5,<3; python-dotenv ≥1.1,<2; neural extra pins **torch==2.10.0**. Report extra pins Plotly 6.3.1 and Streamlit 1.64.0; Streamlit is not the MAG training engine.

Recorded acquisition environment (`A18/runtime_environment.json`): macOS 27.0.1 arm64, Python 3.14.6 / Clang 21, NumPy 2.5.3, pandas 3.0.6, PyArrow 23.0.1, exchange-calendars 4.13.2, requests 2.34.2. The earlier completed S3 session records the same Python/NumPy/pandas/PyArrow plus torch 2.10.0; S9's handoff reports no environment changes. **NOT VERIFIED:** a full package/build/BLAS/backend freeze captured specifically at the S9 live start. Current broad dependency ranges alone cannot guarantee byte-identical recomputation.

Deterministic seeds and CPU execution improve reproducibility but do not certify cross-machine bitwise identity. Differences can arise from CPU/OS/PyTorch kernels or threading, default AdamW dispatch, compiler/math-library builds, NumPy quantile/transcendental and float32 rounding, calendar/tzdata versions, and reordered origin/stock keys. Preserve FP32 training versus FP64 export reductions, batch/inference chunk sizes, constructor/RNG call order and saved source/recipes. Changing batch size changes stochastic training even with seed 42. Serialized file bytes may differ while tensor values agree. No RNG state was checkpointed for arbitrary continuation.

**NOT VERIFIED:** fresh cross-machine reconstruction/checkpoint forward equality, full source hash revalidation or independent lawful access to the private artifacts. This task inspected saved metadata/checkpoint structures only. Existing `refit_binding.json` records `reload_max_error:0` for every fold, and the completed runner required exact reload predictions; those historical checks were not repeated here.

##### 8. Saved-results reconciliation reference

The following are existing **OOS transformed magnitude MSE** values, copied from each `MAGxx/model_and_control_metrics.csv` and neural `oos_metrics.json`; no metrics were recomputed. They provide a compact expected-output reference for the four identified refit models.

| Fold | NEURAL | GLOBAL | STOCK | VOL |
| --- | ---: | ---: | ---: | ---: |
| F21 | 0.22277650031658225 | 0.28464272048962214 | 0.261443862246743 | 0.2599329619784624 |
| F22 | 0.27920023665744426 | 0.38055613654435844 | 0.3487977528967771 | 0.3187140675233866 |
| F23 | 0.20885746933969868 | 0.2549552875755001 | 0.22695279066099444 | 0.24494115063661848 |
| F24 | 0.21898243045736782 | 0.2680606168260498 | 0.24033893466207923 | 0.2494764069720326 |

The saved handoff reports equal-year MAG MSE ≈0.232454 and qualifies the result as magnitude information with raw-magnitude underprediction. These are retrospective exploratory results, not confirmation, signed alpha or transaction-cost-adjusted performance. Source publication/action-vintage and survivor-cohort limitations remain part of exact replication, not details to silently repair.


---

**FINAL ARCHIVAL DECISION (v3):** Keep this file as the consolidated historical project record; use the updated S9-MAG v2 handoff for the separate options-signal research later. The empirical results remain exploratory, and the project's currently protected confirmation data remain closed. The next novel-architecture campaign must reuse the exact S4 information/target/population contract or explicitly disclose any input, recipe, objective or evaluation intervention. No experiments, dashboard changes, new engineering frameworks or protected data accesses are authorized merely by these handoff documents.
