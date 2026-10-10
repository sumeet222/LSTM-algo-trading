# Track A — Stage-Gated Audit and Failure-Traceability Plan

**Version:** v1.1 audit design, 10 October 2026 (adds resource-conscious post-run model-failure diagnosis and boundary replay)  
**Scope:** Track A five-stock, four-hour cross-sectional shared-LSTM research; A-E0 through A-E9  
**Status:** **Design approved by user instruction to use recommended settings; audit results NOT RUN.**  
**Related records:** `Track_A_Consolidated_Implementation_Design_Record_v1_2026-10-10.md` (approved D1–D12/D13-C01 transcription); `Track_A_Architecture_Experiment_Roadmap_First_Pass_FROZEN_v1.0.md` (frozen menu); `Shared_Project_Specification.md` (joint obligations). A subsequent consolidated-record revision incorporating newly approved D13-C07 baseline details may accompany this plan.  
**Purpose:** Catch and localize failures **at logical handoffs**, and explain *why valid models generalize or trade poorly* through small post-run diagnostic replays, rather than repeatedly inspecting each bar, parameter, model, seed, and portfolio run. This is a **Codex handoff audit contract**, not an implementation prompt and not permission to train or access the untouched confirmation period.

## 0. Interpretation, precedence, and what is new

- **Already approved and inherited:** the D1–D12 architecture/trading/validation rules, D13-C01 causal entry-versus-label separation, D13 data/source/clock blockers, FT0/USA500 retention guards, loss concentration/gradient audits, synthetic mechanism tests, both cost-aware portfolio replays, three-seed finalist protocol, append-only ledger, and the 40 neural training-pair ceiling.
- **New D13-C07 recommendations approved in this request:** the narrow momentum/ridge/buy-and-hold/random-benchmark conventions collected in **Appendix A** and to be incorporated into the updated consolidated design record. They were **not** fixed in the original D1–D12 conversation; do not misattribute them.
- **New audit-engineering recommendations approved in this request:** the ten **G0–G9** logical gate layout, evidence package, severity/traceback scheme, trigger cadence, and compact dashboard.
- **New v1.1 diagnostic-engineering requirements (user-requested):** §13 extends the same gates with cheap boundary summaries, deterministic post-run trace replay, a five-to-twenty-stock change-of-universe bridge, and a structured hypothesis/evidence failure report. **No new training runs or promotion thresholds are automatically authorized.** These do **not** change forecasting targets, architectures, experiment activation conditions, splits, cost levels, source assumptions, or model-selection rules.
- **Still unresolved / blocked:** verified historical Alpaca SIP access and one-minute bars, historical USA500 definition/availability, formation membership/liquidity, the shared `240 continuous regular trading minutes` versus `four complete hourly advances` sign-off, possible additional SP3 full-peer finalist control beyond three families, and optional-branch implementation details specifically identified as unresolved. **No audit can be marked PASS without evidence.**
- **No invented pass thresholds:** quantitative cutoffs below come from approved D1–D12 wherever available. New diagnostic plots/counts do **not** become hidden numerical model-selection or automatic retraining thresholds. Additional hard thresholds require an explicit versioned approval.

## 1. Operating model: 10 gates, not hundreds of stand-alone audits

**Run G0–G5 once on the canonical infrastructure and again only when an affected data/code/protocol version changes.** Run **G6 for each genuinely distinct neural training configuration/fitting cutoff**, using cheap per-run telemetry and a targeted deep-dive only on exceptions. Run **G7 only when a conditional mechanism is about to activate**. Run **G8 at the completed development comparison and before selection**. Run **G9 once for the locked confirmation/research-delivery phase**. There is no continuous human inspection after every optimizer step.

| Gate | Logical boundary | Main purpose | When to run | Cost class | Blocks what? |
|---|---|---|---|---|---|
| **G0** | Contract, provenance, permissions | Detect incompatible decisions, unauthorized changes or unknown sources | Project kickoff and protocol amendment | Very low | Affected implementation/training branch |
| **G1** | Raw market data, actions, point-in-time universe | Detect missing, untrustworthy or misadjusted market inputs | After source ingestion/version change | Low–medium | Feature or trading branches relying on failed source |
| **G2** | Calendar → as-of clock → trade/label eligibility | Detect look-ahead, wrong 240-minute horizon, fabricated fills, future-label entry filters | After timeline/label construction change | Low–medium | All affected training/evaluation/backtests |
| **G3** | FT0/U1–U5/peer features → scales → retention | Detect wrong formulas, leaking scalers, stale market observations, selection/attrition | After canonical feature build/version change | Medium, sampled deep check | Models needing invalid features |
| **G4** | A-E1 references and simulator foundation | Detect baseline information mismatch and portfolio P&L/bookkeeping errors | Before any comparative neural claim | Low–medium, synthetic | Trading results and any baseline-dependent claim |
| **G5** | TM0 neural learning engine readiness | Detect nonlearning, leakage, invalid optimizer/stopping/seed implementation | After first tiny and first valid TM0 pilot; on engine changes | Medium (one tiny run) | Neural fitting/promotion |
| **G6** | Every neural run's fit/calibrate/refit handoff | Detect unstable loss/gradients, accidental config drift, lucky-seed/report omissions | Automated at each distinct fit-pair completion | Very low beyond actual fitting | That run's valid result / further promotion |
| **G7** | Optional gate/peer/spatial/auxiliary/adaptive mechanism | Verify actual hypothesis, information matching and conditional eligibility | Only at activation of D7–D11 branch | Low synthetic; expensive training only if separately eligible | Affected optional run and mechanism claims |
| **G8** | Development evaluation, net trading, inference, shortlist | Detect comparison bias, suspect economics, bootstrap/model-selection mistakes | At development checkpoint / shortlist | Medium; reuse forecasts/trades | Promotion and confirmation unlock |
| **G9** | Confirmation manifest → one-look run → final handoff/report | Detect test leakage, post-lock changes, incomplete outputs | Immediately before and once after authorized A-E9 | Low–medium beyond final fits | Confirmatory claims and release |

**G0–G9 are conceptual gates, not an imposed directory structure or ten independent heavyweight software packages.** The new §13 replay/diagnosis capability is **not an eleventh gate**; it reuses artifacts from these stages. A small common validator plus stage-specific checks and one ledger/dashboard is preferable to ten separate frameworks.

### 1.1 Severity and disposition

| Status | Meaning | Required behavior |
|---|---|---|
| **PASS** | Required invariants verified, with saved evidence | Continue only to authorized next stage |
| **WARN / INVESTIGATE** | Anomaly or weak evidence that does not by itself invalidate inputs | Retain results but hold *promotion or interpretation* if material; inspect small diagnostic sample and record conclusion |
| **BLOCKED** | External source, collaborator approval, prerequisite, or resource not available | Stop **dependent** branch; do not fabricate or swap inputs; unaffected independent work may continue |
| **HARD FAIL / INVALID** | Deterministic violation (leakage, impossible return/position, broken accounting, test peeking, nonfinite fitted result) | Stop affected pipeline before using output; retain invalid run in ledger; fix and version, then rerun dependent artifacts |
| **INCONCLUSIVE** | Correct procedure but not enough sessions/episodes/seeds or broad uncertainty | Do not label mechanism ineffective; record limitations and permitted follow-up |
| **INACTIVE CONDITIONAL** | Predeclared branch activation condition not met | No training; record why |

**Stop propagation at the smallest correct boundary.** A failed USA500 audit blocks MC0/MC1-dependent research, not stock-only raw-source QA. A failed portfolio ledger blocks economic claims but may leave correctly constructed, separately scored predictions valid. A nonfinite training gradient invalidates *that fit*, not prior raw-data audits.

### 1.2 One compact audit package per gate

For each execution of a gate, write a compact human-readable Markdown summary and a machine-readable result with at least:

`gate_id, audit_run_id, timestamp_utc, stage, protocol_version, code_hash, config_hash, source/data_version_hashes, applicable_symbols, fitting_cutoff, evaluation_window_if_any, status, metric/count, approved_threshold_if_any, anomaly_examples, affected_artifact_ids, root_cause_hypothesis, owner_action, rerun_scope`.

Save **counts, checksums, small example row references and lightweight plots/summary tables**, not duplicate raw market datasets, full copies of overlapping windows or giant gradient traces.

**End-to-end trace key:** `source_observation_id → symbol/session/scheduled_slot → period_end/available_at → feature_version/historical_step → origin/issuance → eligibility_flags → label_entry/exit/maturity → scaler_fit_id → model/run/seed/checkpoint → prediction_id → policy/cost_scenario/order/fill/position/equity_event → metric/report_row`.

Maintain the links rather than physically duplicating rows. Each anomaly report should expose the identifiers required to walk **upstream** and reproduce the first divergent value.

---

## 2. G0 — Contract, authorization, and source-provenance audit

**Trigger:** Initial repo preparation; whenever source, configuration, shared clock, frozen experiment menu or protocol version changes. **Lightweight, no modeling.**

| Check | Failure / anomaly to detect | Action and evidence |
|---|---|---|
| Authority/version | Shared project spec, frozen architecture menu and approved design decisions disagree or were silently overwritten | **BLOCK** affected decision; include exact document, section, proposed change and requested approval |
| Conditional status | Optional MC2/SP3/SP1/TM1/TG2/TG4/AD3 marked mandatory or auto-launched | **HARD FAIL** unauthorized run request; preserve inactive branch record |
| Source identity/entitlement | Alpaca SIP and USA500 data presumed available without evidence or access/usage rights | **BLOCK** dependent task; record source ID, contract/metadata requested, and access check status |
| Common clock/sign-offs | Track A 240-minute and shared four-complete-hour conventions presented as equivalent; collaborator approvals implied | **BLOCK shared-clock-dependent implementation**; store pending approvals without guessing assent |
| Window/confirmation | Research period or final 2024-07–2025-06 dates modified without versioned approval | **HARD FAIL**; preserve original windows |
| Resource and scope | More than 40 two-pass neural pairs planned without approval, extra model families inserted, no compute reserve for required controls | **BLOCK** unauthorized jobs; create budget forecast and priority ledger |
| Secret handling | Credentials, API tokens or private data in config, logs, Git or generated reports | **HARD FAIL** for exposure; fix without publishing credential values |
| Repository/data safety | Raw source overwritten, copied per seed, or storage growth not explained by new canonical assets | **WARN/FAIL** depending on data loss; provide disk-usage and file-hash summary |

**Artifact:** Protocol/approval matrix, dependency and budget ledger, source inventory, first go/no-go report. **Never mark G0 PASS on a shared-clock requirement that the collaborator has not signed.**

## 3. G1 — Raw price, corporate-action, and point-in-time universe audit

**Trigger:** Complete initial download or version change of stock minutes/hourlies, corporate actions or USA500. Use inexpensive column-level checks for all rows, with a few manually inspected exception clusters. Avoid bulk duplicate copies.

| Check | Candidate failure point | Method / disposition |
|---|---|---|
| Raw dataset keys | Duplicate `(symbol, timestamp, source/version)` rows; unsorted timestamps; conflicting multiple observations | Key uniqueness and ordering summaries; **FAIL** ambiguous canonical bar until reconciled |
| OHLCV plausibility | Zero/negative adjusted prices, `low > high`, open/close outside range, negative volume, `NaN/Inf`, impossible zero-range quality interpretation | Automated invariants; **FAIL** invalid records; inspect representative cases (not blind repair) |
| Calendar/market sessions | Missing holidays, early closes, DST shifts, pre/postmarket bars in regular-session grid; 15:30–16:00 stub treated as full hourly bar | Calendar schedule cross-check; **FAIL** incorrect timing conversion |
| Historical source coverage | Missing year/stock/session/source intervals; 1-minute gaps at 10:33, 11:33, 14:33, 15:33 and liquidations | Per-source/year/stock coverage heatmap and counts; **BLOCK** unsupported execution claims |
| Issuance provenance | Source timestamps treated as publication times without evidence; look-ahead from finalized/revised bars | Raw `period_end`, raw label and `available_at` samples; **BLOCK** if publication semantics unknown |
| Split/dividend accounting | Incorrect adjusted OHLC vs adjusted share-volume inverse, dividend cash ignored, false jumps at splits; raw price used in feature training by accident | Independently reconstruct a few known action dates before/after; **FAIL** if equity not conserved under a pure split |
| Formation eligibility | 2020-07-01 membership, trailing 60-session $50m liquidity and preformation coverage not point-in-time; backups chosen after seeing subsequent returns | Eligibility matrix using preformation records; **BLOCK** unverifiable membership; disclose retrospective completeness separately |
| Retrospective coverage | ≥98% overall and ≥95% per adequately represented year may rely on future observed vendor completeness | Report separately as **source usability**, not investable 2020 selection; warn of look-ahead selection risk |
| USA500 semantics | Wrong identity/instrument, missing compatible OHLC or daily close, index data volume assumed, timestamp/timezone or market age unverified | Source-backed metadata + sample source records; **BLOCK** U1–U5-dependent branches, no silent SPY replacement |

**Artifacts:** One source inventory, corporate-action exception sheet, five-stock formation/backup matrix, year/slot coverage summary, and traceable 3–5 human-inspection examples per *encountered anomaly class*. No 2024–2025 predictive metrics.

## 4. G2 — Calendar, information clock, eligibility and four-hour target audit

**Trigger:** After session/forecast/entry/exit and target-building logic; anytime time-alignment code changes. This is a **hard leakage gate**.

| Check | Candidate failure | Required evidence / behavior |
|---|---|---|
| Hourly input grid | Hourly observations not anchored 09:30 ET or stub counted as an ordinary full hour; 48 slots manufactured by skipping gaps | Audit first/last hour and DST/early-close examples; **FAIL** if slot mapping wrong |
| Forecast origin/issuance | First/second origin accidentally derived from unfinished 10:30/11:30 bar; 2-min allowance/5-min maximum issuance delay violated | Timestamp timeline from raw bar end → publish → feature cutoff → issuance; **FAIL** future observation |
| Minute entry/exit | Trade filled at forecast bar close or 16:00 fictional hour; not using true minute open; invalid 240 regular-trading-minute count | Hand-check scheduled 10:33→14:33 and 11:33→15:33 including exchange-calendar definition; **FAIL** impossible entries/exits |
| Source as-of | Feature step uses stock/market/peer `available_at` later than its own historical cutoff; market source stale >90 min | Query max source availability per feature row; **FAIL** information leak, stale market invalid |
| Historical daily features | Current-day completed close copied back into earlier same-session feature steps; later feature values retroactively copied through 48 steps | Synthetic post-close price jump test; **FAIL** any backward change |
| Label and boundary | TG0 uses missing/incorrect five exit prices, future date labels in fitting period, or labels before maturation | Hand-calc five-log-return median and **unscaled** MAD; test purge on WF/inner/confirmation cutoffs |
| **C01 entry vs label** | Backtest entry suppressed because `future_label_valid=false` or because a profitable/unprofitable exit price is missing | Counterfactual toy case: change *future* exit availability while holding entry-time facts fixed; entry decision **must not change**. **HARD FAIL** otherwise |
| Entry and exit eligibility | Ineligible missing entry leg magically fills, failed exit deletes physical position, labels substituted for trading P&L | Separate `forecast_issuable`, `entry_eligible`, `label_valid`, `exit_filled` flags; **FAIL** conflation |
| Cross-sectional population | One missing stock silently changes N=5 median/MAD or ranking comparator population | Require full five-stock input/label population where specified; report distinct score vs trading counts |
| Shared clock approval | Four complete hourly advances and 240 continuous minute labels represented as formally signed off | **BLOCK** common comparison until actual collaborator approval |

**Artifact:** One annotated timing diagram and eligibility reconciliation: **issuable predictions → executable entries → matured valid labels → normally exited trades → exceptions**, by session and origin. Provide trace IDs of mismatches. The forecast score population and economic trade population need **not** have identical counts under D13-C01; the mismatch must be explained, not silently forced away.

## 5. G3 — Feature, scaling, warm-up, market-state, target and retention audit

**Trigger:** After canonical FT0/U1–U5/peer and TG0 construction; again if preprocessing configuration changes. Start with hand-computable synthetic/real samples; global summary checks run once.

| Feature group | Potential failure / anomaly | Cheap high-value check |
|---|---|---|
| FT0 input shape | Wrong 16-channel order, fewer than 48 scheduled slots, padded/skipped stock hours | Assert `(5,48,16)` per eligible origin, strict all-cell stock validity, check order/slot mapping |
| M1/M2/M3/M4 | Incorrect OC vs close-close, M2 history accidentally uses not-yet-matured historical 4h outcomes, M3/M4 off by one daily session | Recompute representative dates by independent formula; include 10:30 vs 11:30 M2 and 105-session M4 spacing |
| V1/V2/V3 | Standard deviation substituted for RMS; wrong short/long floors; valid-count and max-consecutive-gap logic wrong | Hand-check 12/12, 57/60, V3=V1−V2; inspect low-volatility edge |
| B1/B2 | Invalid OHLC range accepted; genuine `H=L` zero-range CLV mishandled | Unit tests for CLV ±1, zero range→0 + metadata, invalid bar rejected |
| Q1/Q2 | Missing volume treated as real zero, pseudocount sourced from test, closing stub excluded from completed daily volume, mismatched slot | Check split-inverse shares, 19/20, 5/5,57/60, training-only 1%-median pseudocount |
| T1/T2 | Incomplete current-day SMA/return used; bounded sign channel rescaled contrary to D4 | Verify previous-session 20-day SMA and sign average, min 19/20 |
| T3/T4/T5 | EMA/RSI warm-up skipped, missing-bar recovery uses fabricated return, RSI overnight-gap convention changed | Test 360 EMA good updates, 14+140 RSI, recent ≥69/72, gap freeze/recovery; no unauthorized MACD extras |
| FT0 scaling | Training/test medians mixed, unscaled MAD swapped for Gaussian-consistent MAD, per-stock scaler used instead of pooled, constant channel mishandled | Refit scalers independently on permitted fit prefixes; verify MAD→IQR/1.349→audited SD→zero fallback; no clipping |
| U1–U5 | USA500 missing bars reused as fresh 1h returns; U4/U5 daily state leaked back; market volume assumed | Source-dependent hand tests; 12/12,57/60,60/63; source incompatibility **BLOCKS** market branch |
| Market masks | Missing endpoint imputed, historical 0-fill passed as real volatility, learned mask channels silently added | Endpoint valid, ≥46/48 complete historical states, separate masks, MC0 exactly 21 numeric channels |
| Peer summaries/lags | Target included among own four peers, wrong population-STD divisor, H/L selected using future liquidity or target Sharpe, lag 1 assumed elapsed hour across session boundary | Independent peer leave-one-out and `H↔L` hand examples; preformation selection proof; lag-boundary report |
| Target TG0 | Scaled vs unscaled MAD confusion; epsilon fitted on development; outlier clipping | Recompute target on five raw genuine returns; floor max(1e-4,0.1 training median MAD); report floor-hit/extreme-day counts |
| Feature-tailing | Hypothetical clipping hides distinctions between top/bottom stock features | Audit FT0 ±3/±5/±10 **hypothetical** clipping rate and cross-sectional collision count; no clipping actually applied |
| Repeated windows | Same `(stock, session, origin)` M2 or market timestamp counted repeatedly in scaler; feature source copied across models | Unique fit-key checks; market one real timestamp per scaler fit, M2 origin-balanced; disk/cache lineage |

**Predeclared retention gates (inherited; do not loosen automatically):** stock-required complete `48×16×5`; training and development joint retention **≥90%**; each approximately six-month WF fold, each origin time and each adequately supported volatility regime **≥85%**; volatility-regime retention imbalance **≤10 percentage points**; **≥100 distinct eligible sessions** per approximately six-month fold. For market history, valid endpoint and ≥46/48 states. **Compute separate stock-only versus market-conditioned origin retention and compare models on a matched origin intersection.** The D6g inner-calibration tail uses 63 calendar sessions with ≥50 eligible sessions and ≥25 valid observations at each origin time. Failures are **BLOCKED/data adequacy**, not signal or architecture negatives.

**Artifact:** Compact feature QA table, sample formula reconciliation, training-only scaler manifest, rolling-validity and warm-up maps, stock/market attrition waterfall (including losses by regime/origin), target distribution/zero-MAD/tail diagnostics. Preserve source and feature hashes, not more copies of raw data.

## 6. G4 — Baselines, benchmark consistency and physical portfolio simulator

**Trigger:** Before accepting *any* neural versus baseline or net-return result. Part A and B can share one G4 report; test on a small synthetic price/order sequence plus hand-calculated real observation examples.

### 6.1 Predictive and contextual baseline verification

| Check | Failure mode | Required result |
|---|---|---|
| Momentum | Wrong FT0 M1 sign, target horizon substituted, score from future price or later bar | Highest causally observed normalized latest-hour M1 is ranked first; never use future 4h return to form score |
| Ridge lag dictionary | Wrong lags, sequence history reaching beyond available 48, stock/time columns reordered, market data privileged in own-stock model | Explicit 7-lag order `[0,1,2,5,11,23,47]`; 16 stock channels per lag = **112** baseline inputs; MC0 ridge adds 5 market channels ×7 = **35**, total **147**. Record sparse reach vs full LSTM history |
| Ridge penalties | Alpha chosen from development Rank IC, Sharpe or confirmation; unweighted row-average loss; intercept penalized | Inner 63-calendar-session tail; five fixed λ candidates; session-weighted MSE; intercept unpenalized, tie prefers higher λ |
| Ridge source matching | Different target, dates, validity or downstream execution from TM0/MC0 | Same TG0 and matched eligible evaluation origins; information channels from same canonical stores, with disclosed sparse lag sampling |
| LL0/LL1 | Ticker identity flags only in LL1, target/market information changes across pair comparison | Keep fixed `H`,`L` flags and all non-lagged inputs in both arms; compare only permitted extra peer channels |
| Momentum ties | Different run randomly resolves identical scores | Fixed canonical ticker tie-break for *trading only*; preserve midranks and constant prediction audit for Rank IC |
| Buy-and-hold | Rebalancing silently, adjusted-price gains double-counted, marketed as risk-matched | 5-stock equal initial holdings, no periodic rebalance, actual splits/dividends and entry/exit costs, clearly contextual benchmark |
| Random long/short | Future return used to choose random pair; repeated favorable random paths selected | 1,000 independent reproducible paths, separate fixed seed namespace, identical candidate forecast calendar and portfolio rules; report distribution and exposure mismatch |

### 6.2 Physical simulator stress cases (each a tiny deterministic hand ledger)

| Small scenario | What must be reconciled |
|---|---|
| Buy 1 stock, then sell later | `cash + long market value` equals expected equity before/after costs |
| Short 1 stock, cover later | Short proceeds, liability, borrow-day charge and equity reconcile |
| Open two opposing virtual sleeves in same stock | Physical netting can create zero external order; **no phantom trading cost** |
| Sequential opposing orders | Each actually external fill incurs cost; netting at different timestamps does not remove prior cost |
| Conflict-veto case | Reject **entire second pair**, keep first four-hour expiry; no fictitious new transaction cost |
| Full 49.5%-gross sleeve versus 100% cap | Per leg +24.75%/−24.75%; reject *whole* proposed pair if post-cost physical gross exceeds 100%; no hidden scaling |
| Passive gross drift | Small drift above 100% alone causes no ordinary rebalance; >110% observed breach triggers emergency |
| Emergency breach | Cancel further session entries, target physical zero at **next valid fill**, charge costs, do not mark unfilled liquidations complete |
| Missing entry leg, then partial fill exception | Do not intentionally establish unmatched pair; if partial execution occurred, preserve/fix actual exposure and costs |
| Missing scheduled four-hour exit | Keep physical position, retry next permissible one-minute opening; no future-label deletion; suspend new entries |
| Close/overnight exception | Preserve unresolved position and valuation uncertainty; resume next regular session causally; no fabricated terminal liquidation |
| Cost scenario replay | Execute independent 0/2/5/10-bps portfolio paths because costs can alter future equity and cap admissions; do not merely reprice fixed trades |
| Borrow fee | 0/0.5/3% annual assumptions, annual/360 × **daily max net physical short** not duplicated virtual shorts |
| Ex-post direction report | Future signs appear in **report only**, never in entry/veto/admission/trading model |

**Required accounting invariants:** filled share quantities match physical-position deltas; each modeled fill cost charged once; equity change reconciles to market moves, cash flows, dividends, borrow, and execution costs; virtual sleeve ledger sums to the aggregate physical target; exits never occur before admissible order/fill time. Compare independent hand ledger to simulator event-by-event, not just final Sharpe.

**Artifact:** Baseline ridge-fit/validation manifest, synthetic transaction ledger with expected vs actual amounts, baseline outputs, two-policy cost matrix, outstanding-position exception examples. **Any failed P&L invariant blocks economic claims, even if Rank IC is valid.**

## 7. G5 — Neural engine preflight: small proof of implementation correctness

**Trigger:** Once after first canonical dataset approval and when model/training engine changes. A synthetic/tiny-batch pass is **not** a financial-alpha result and need not consume an expensive full two-pass fitting slot.

| Check | Potential failure | Evidence/action |
|---|---|---|
| Input/model shapes | `(48,16)` versus `(48,21)` accidental transpose; bad `batch_first`, wrong stock axis | Small forward test with exact expected shapes; parameter counts TM0 **6433**, MC0 **7073** |
| Independent windows | Carrying `(h,c)` between stocks/batches/splits; prediction depends on batch order | Zero-state reset and individual-vs-batched forecast equivalence |
| Dropout | PyTorch one-layer `nn.LSTM(dropout=0.1)` mistaken for D6c final-head dropout; dropout active in validation | Model structure check; stochastic training versus deterministic eval behavior |
| Weighted MSE | Origin-weighted rather than session-weighted loss | Synthetic 2-origin session losses 2,6 and 1-origin session loss 10 → **correct 7, not 6** |
| Session sampler | Some sessions repeated/omitted, last batch dropped, 48 time steps shuffled | Seeded epoch permutation, no-replacement coverage; 16-session target; balanced remainder |
| Optimizer groups | Missing parameter, double-counted tensor, decay on bias/norm | Every trainable tensor exactly once; AdamW 0.001, β=(.9,.999), eps 1e-8, weights 0.01 decay only |
| Gradient clipping | Clip before accumulating/unscaling; clip each stock separately; nonfinite gradients ignored | Whole-effective-batch global L2 max=1.0; unit direction-preservation test |
| Small-batch learnability | Network cannot reduce loss on tiny correct synthetic task, or outputs identical across all stocks | Tiny-batch overfit/finite-gradient test; debug before claiming no alpha |
| Checkpoint logic | Stop before epoch 12, wrong 0.1% relative rule, choose Rank IC/Sharpe checkpoint | Synthetic loss trajectory tests for 60 max, patience 10, best qualifying epoch, earliest tie |
| Inner/refit separation | Validation preprocessing fit with outer data, refit reuses calibration optimizer state | 63 calendar-session inner validation with maturity/purge, fresh model/optimizer and full-history scaler refit |
| Determinism | Different predictions after reload of same checkpoint or unlogged random state | Fixed seed registry and same-environment reproducibility tolerance documented |

**Artifact:** Tiny neural preflight test matrix and one short training trace, with gate G5 PASS independent of later observed Rank IC/net P&L. No expensive parameter search.

## 8. G6 — Lightweight per-run training, checkpoint and reproducibility audit

**Trigger:** For each **distinct neural `(architecture, fitting cutoff, seed, configuration, data version)` two-pass pair**, automatically at calibration completion, refit completion and before predictions are accepted. This is mostly a **summary derived from existing logs**, not a new training run.

| Health signal | Failure/anomaly to detect | Handling |
|---|---|---|
| Loss path | Nonfinite/divergent training or inner MSE; suspiciously zero loss on financial targets; train-only improvement with unstable validation | Nonfinite = **INVALID/FAIL**; otherwise analyze train/validation gap, do not auto-retune |
| Optimizer | Learning-rate schedule unexpectedly active; weight decay, clip or sampler config different | **FAIL** config mismatch; compare immutable hash |
| Gradients | Norm NaN/Inf, sustained >50% clipping, gradient nearly absent, persistent zero output variance | Nonfinite = **FAIL**; sustained clipping / near-constant forecasts = **WARN/INVESTIGATE**, not automatic threshold change |
| Target tails | Few dates dominate MSE due to TG0 low MAD or extreme returns | Report top 1/5/10% **session** loss concentration, MAD-floor activity and affected dates; don't clip |
| Window weights | One-origin dates given half as much importance, final minibatch ignored | Reference equal-session loss and sample-count reconciliation |
| Early stopping | Checkpoint selected on wrong metric, no 0.1%-qualification logic, invalid 63-session inner tail | **FAIL** calibration selection; record both raw minimum and selected qualifying epoch |
| Final refit | Wrong epoch count, warm-start instead of fresh initialization, different input version | **FAIL** refit comparability; log actual optimizer steps and both pass runtimes |
| Seed/fold | Wrong seed, selective rerun of disappointing result, predictor from wrong fitting cutoff | **FAIL** run contract; hash each model and permutation |
| Stability | Entire cross-section gets identical predictions; unusually high ties or unstable rank flips | Flag mathematically defined-only Rank IC and constant-rate; inspect outputs; report even if valid |
| Cost and storage | Unexplained checkpoint/data/cache growth; failed fits omitted or duplicate successful fit | Summarize pair-count, compute runtime, disk changes, artifact deduplication; block unapproved >40-pair jobs |

**Artifact:** One concise run-health row and a small diagnostic plot/summary *only when anomalous*, referencing full training metrics already logged. Do not store every gradient tensor or every epoch's model weights. Each failed attempt stays in the append-only experiment ledger.

## 9. G7 — Conditional mechanism and information-matching audits

**Trigger:** **Only when** a D7–D11 optional mechanism's activation prerequisites are actually considered. Use preexisting training data and tiny synthetic tasks before allocating a neural training pair.

| Branch or mechanism | Failure points / targeted tests | Activation/claim rule |
|---|---|---|
| **D7 MC0 vs MC1** | Different market history or feature masks; MC1 drops direct U1–U5; zero gate not identity; saturation/entropy collapse; gate gradients absent | Both have same underlying five-feature market history; MC1 5→16 scaled softmax, τ=1, zero logits → all ones, total **7169** parameters. No gain attributed to gate if information differs |
| **D7 MC2** | Step gate accidentally uses endpoint, later market values copied backward, invalid historical state nonneutral; state-variation threshold calculated on development | Training-history activation: U2–U5 step difference ≥1, ≥25% of valid steps for a changed window, ≥20% of training windows and ≥20 distinct sessions; otherwise **INACTIVE CONDITIONAL** |
| **D7 market state slices** | Bull/bear future-peeking, volatile threshold fitted using development, very few episodes | U5 sign, U2 training median; label **SPARSE** if <30 distinct sessions or <3 contiguous episodes; diagnostic only |
| **D8 peer mean/dispersion** | Leave-one-out mistakenly includes target; 4-peer STD uses wrong divisor; wrong stock order, lag crosses overnight undetected | Hand-recompute with 4 peers, population variance divisor 4; matched own+USA500 controls |
| **D8 H→L / reverse** | Leader/follower selected by realized return, wrong 2020 preformation volume, lag 0 from future, LL0 identity flags omitted | Select fixed formation-time 60-session dollar-volume extremes; predeclared lags [0,1], reverse direction, same LL0/LL1 flags |
| **D8 cheap destruction** | Ten-session-lag sham test called selection-adjusted permutation p-value | Diagnostic only, never a formal null claim |
| **D9 SP3** | Misordered stocks; M2 nonzero at init; peer sensitivity absent; wrong LayerNorm axis; K changed from 2 | Exact MC0 initial equivalence, K=2, 7093 parameters; synthetic planted peer signal and permutation-coordinate test; mandatory full-peer control for strong claim |
| **D9 SP1 alternative** | Automatically launched after weak SP3 Sharpe; incorrect one-head 16D shape; attention used as causal explanation | Only separately justified activation, total 9121 parameters; weights descriptive only |
| **D10 TM1/TG2** | TM1 γ=0 not identity; attention attends future; TG2 auxiliary label overlaps split; short heads change trades; both branches run | At most one activated A-E7; identity/gradient test for TM1 or 1h/2h/4h matured-label and primary-4h-head tests for TG2 |
| **D11 FC/TG4/AD3** | Unapproved factor data, target stock used as own sector, fabricated 240-increment realized variance, future matured labels in rolling AD3 head, silent change to portfolio sizing | A-E8 default defer, at most one; **unresolved optional numerical details require fresh approval when activated**; prequential AD3 tests |

**Dedicated fairness checks when a branch runs:** identical target/horizon/source/eligibility, D6 training protocol, comparable seed/cutoff, predeclared reference control, actual parameter count, and same two-policy/cost simulator. Information-matched does **not** imply exactly parameter matched; state the difference. Mechanism diagnostics that fail do not prove financial inefficacy. No automatic retry/grids; document any targeted rescue under D6h.

**Artifact:** Mechanism-specific one-page test report, activation evidence and comparator-matching manifest. If not activated, a short `INACTIVE_CONDITIONAL` ledger row is enough; **do not execute these diagnostics for every unused branch**.

## 10. G8 — Development, dependence-aware inference, economic realism and promotion

**Trigger:** At E3/E4 peer/model milestone reviews and end of development; reuse already stored prediction and physical-ledger outputs. Run heavier bootstraps only for meaningful pairwise comparisons/finalist evidence, not for every smoke test.

| Check | Failure/anomaly | Required handling |
|---|---|---|
| Equal comparison population | One model gains Rank IC solely because it drops hard dates or because market-feature attrition changes periods | Matched five-name forecast origin/date intersection and **separate** coverage waterfall; hard fail for invalid unmatched comparison |
| Rank IC implementation | Five-stock row autocorrelation called Spearman, arbitrary tie jitter, constant predictions excluded without disclosure, constant realized labels included | Hand-check ranks and midranks, constant-prediction project score 0, defined-only mean, separate true-constant exclusions |
| Daily aggregation | Treat 10 stock-origin rows as 10 independent sessions or average unequal minibatch losses | Daily mean of 1–2 eligible origins, then equal days; paired model delta over same days |
| Fold/prediction dates | WF1/WF2 label/refit cutoff violated, outer results used for inner checkpoint, development used as "independent" after selection | **FAIL** contaminated comparison; keep chronology provenance |
| Inference | Independent-row bootstrap; discontinuous calendar treated as contiguous; time-block labels broken; overly confident interval | 5-session moving blocks over actual sessions; 10/20 sensitivity, 10k resamples, 95% percentile interval, HAC lag 5/10; caveat model selection |
| Model promotion | Best seed or best net Sharpe selected post hoc; model promoted despite missing comparator; one-SE simplicity ignored | Freeze selection rule, include every seed and failed branch; do not force winner |
| Gross versus net economics | Costs deducted twice/missing, cumulative wealth inconsistent, positive Sharpe from filtering no-trade dates, negative cash/borrows ignored | Independent reconciliation of full-calendar portfolio equity and both policies under all 0/2/5/10-bps scenarios and 0/0.5/3% borrow assumptions |
| Market exposure / churn | Huge short-duration physical holdings from opposing sleeves; conflict veto mistakenly treated as free; leverage/exposure spikes | Report actual holding-duration distributions, turnover, order counts, veto/cap rejections, gross/net beta and emergency events |
| Random baseline | Random strategy appears risk-matched when not; future outcomes steer random draws | 1000 fixed seeded opportunity-matched paths; report actual exposures and compare on consistent horizon; buy-and-hold labeled non-risk-matched |
| Apparent anomalies | Rank IC extremely high, unusually smooth P&L, zero turnover yet large strategy profits, huge Sharpe with tiny number of days | **Investigate** trace to prediction, time, labeling and cashbook; no arbitrary universal numeric cutoff, no automatic retune |
| Null claims | Post-fit shuffled predictions called significant after architecture selection | **FAIL claim**; full-discovery rerun under defensible temporal null needs separate approved budget; otherwise mark unestablished |

**Artifact:** Per-comparator development card (date population, seed/fold deltas, CIs, portfolio cost matrix, anomalies, promotion rationale), full candidate ledger and failed/inactive branches. **Only after this gate** may a valid architecture be nominated for A-E9 manifest lock.

## 11. G9 — Confirmation lock, once-only evaluation, final report and archive

**Trigger:** Immediately before releasing any July 2024–June 2025 confirmation results, and once after the authorized evaluation. This gate has two phases but one immutable confirmation stage.

### G9-pre: all hard prerequisites and frozen manifest

- G0–G4 source/timing/label/simulator essentials **PASS** for claimed branches; G5/G6 neural readiness **PASS** for finalists; G7 conditional mechanisms correctly activated/deferred; G8 candidate selection complete.
- Cross-track clock and shared-convention sign-offs actually recorded; no fictitious approvals.
- Full A-E0–A-E8 ledger includes completed, failed, invalid, blocked, deferred, rescued and inactive branches.
- Shortlist is frozen by development Rank IC, paired evidence/one-SE simplicity and costs/complexity; **TM0 and valid MC0 references**, at most **three replicated neural families** by default; resolve the SP3 full-peer **fourth-control conflict** through explicit amendment or narrow claim.
- All finalist seed IDs 42/123/2026 and fitting cutoffs specified; 40-pair and runtime budgets reconciled. D6g fresh preconfirmation refit uses training only through June 2024, purging unmatured labels.
- Lock code/config/data/preprocessing/checkpoint hashes, eligible-origin/calendar rule, exact metric and portfolio procedures, benchmark random-seed namespace, and the selected models. Set confirmation result storage to **read-only for selection decisions**.
- The formal null experiment remains conditional; if not performed, the confirmation claims explicitly exclude selection-adjusted null significance.

**Any unmet item = `NOT READY / BLOCKED`.** Audit-only or repair work can continue; no confirmation metric is unlocked.

### G9-post: verification without tuning

- Compute exactly the locked confirmation metrics and both portfolio-policy cost/borrow replays. Verify the result joins the locked prediction/model/checkpoint IDs and eligible dates; do not recompute a convenient sample after viewing outcomes.
- Audit one or two hand-selected example predictions and physical trade paths from confirmation **for correctness only**. Samples must be preselected by stable keys or fixed sampling seed, **not chosen after noticing which result helps a model**.
- Report the originally selected hypotheses, paired effect sizes/uncertainty, gross/net and drawdown results, seed/fold consistency, failed/inactive branches, source limitations and no demonstrated effects.
- If a deterministic defect is discovered, preserve the first-look output as invalidated, correct it in a **new version**, disclose that the 2024–2025 period is no longer untouched for revised selection. Do not erase evidence or iterate to a winning confirmation model.
- Archive manifest, lightweight analysis summaries, hashes, approved decisions, budget/space ledger and a reproducibility command summary. No user credentials or raw-data copies in the report.

**Artifact:** Locked confirmation manifest, gated release log, complete results report, error/limitation addendum, experiment/run provenance index and compact disk inventory.

---

## 12. Cross-cutting resource, anomaly and traceback controls (not additional gates)

### 12.1 Resource sampling schedule

| Point | What to record | Stop condition |
|---|---|---|
| After G1 raw acquisition | Source bytes, unique raw source files, coverage, checksums | Incomplete provenance, duplicate raw versions used without explanation |
| After G3 feature store | Data and cache bytes, shared feature/target versions, new Parquet counts, canonical-vs-derived duplication | Large unexpected copies or overwrite of canonical source; investigate before further materialization |
| After first G5 tiny model | Seconds/epoch, approximate two-pass cost, hardware/environment, storage per checkpoint | Forecast violates approved 24-hour preliminary compute envelope or 40-pair cap without revised approval |
| At each G6 fit-pair completion | Actual pair count, GPU/CPU time, peak working memory if available, new persistent disk bytes, failed attempts | **Block unapproved extra training pairs**; no automatic rescues |
| Before G9 lock | Remaining necessary fits/controls vs budget; storage and package/version changes | No scientifically valid confirmation manifest or required controls unsupported |

A large output folder or multiple near-identical Parquet versions is an audit anomaly, **not automatically permission to delete files**. Produce a size/duplication report and obtain approval before deleting historical artifacts; never discard audit evidence for an unsuccessful run.

### 12.2 Cheap anomaly localization and human-review sampling

For any gate failure, generate a concise **failure card**:

`stage → first violated invariant → exact symbol/session/slot (or model/seed/fold) → upstream source observation / configuration → smallest reproducing case → affected branches and evaluation dates → severity/status → recommended repair and rerun dependency scope`.

Prioritize:

1. **Causal correctness** (future input, label leak, invalid fill, test contamination).
2. **Accountability correctness** (raw splits/dividends, short cash/position signs, cost once, P&L reconciliation).
3. **Model/prediction correctness** (wrong scaler, loss weights, model output or checkpoint).
4. **Statistical comparability** (different eligible populations, selection on final period, invalid paired resample).
5. **Performance/resource oddities** (slow training, excess clipping, high churn or expensive duplicated caches).

Run deterministic checks on **all records where cheap** (timestamp monotonicity, keys, row counts, exact transformations and ledger invariants). Perform **small targeted independent hand audits** on a few distinct edge cases: split, early close, DST transition, data outage, high-volatility/MAD-floor date, cross-day lag, opposed sleeves and missing exit. Run expensive repeated training, broad perturbation or bootstrap computations **only at the appropriate later stage**.

### 12.3 Rerun dependency map

| Root cause repaired | Minimum affected downstream work to invalidate/recompute |
|---|---|
| Raw source/adjustment correction | Derived features, labels, eligible populations, affected fits, predictions, portfolios, metrics |
| Calendar/`available_at`/horizon correction | Any impacted feature windows, labels, eligibility, affected fits/predictions, portfolio paths and statistical comparison |
| Scaler/feature formula correction | Corresponding trained fits, predictions, all downstream metrics/trades; raw immutable data unchanged |
| TG0 target/floor correction | Supervised fits, targets, score comparators, metrics; price accounting separately audited |
| Neural code/optimizer/early-stop correction | Only affected model fits and their evaluations; unrelated verified source/feature stores remain |
| Gate/peer/mixer implementation correction | The relevant branch and required matched comparisons, not all independent baselines |
| Fill/cost/borrow/risk policy bug | Portfolio event paths, cost scenarios, economic metrics and random reference; **not necessarily forecasting model fits** |
| Rank IC/bootstrap/report formula bug | Recompute affected statistical reports from immutable predictions/returns; no neural refit if scores valid |
| Confirmation-selection leak | Invalidate the claimed pristine confirmation status; do not 'fix' by quietly rerunning on same sample |

Never overwrite old results in place; version outputs and preserve the invalid attempt with its cause.

---

## 13. Post-run model-failure diagnosis and deterministic boundary replay (NEW v1.1 requirement; no new G gate)

**Purpose and authority.** This section is a **new user-requested D13 diagnostic-engineering requirement**. It extends G1–G9 rather than adding another mandatory expensive gate. Existing audits check whether the research procedure is *valid*; the diagnostic workflow investigates **why a valid run learns little, generalizes poorly, changes its outputs unexpectedly, or earns poor net portfolio returns**. Its goal is to distinguish hypotheses and identify the earliest supportable divergence; it cannot prove that a market lacks alpha or that a particular change would improve future returns. No new architecture, target, threshold-based promotion, discretionary retraining, test-time selection, or budget exemption is authorized here.

### 13.1 Three resource tiers and when to run them

| Tier | When | Data captured / generated | Cost and permission |
|---|---|---|---|
| **T0 — ordinary run summary** | At each existing logical G1/G2/G3 dataset version, G6 completed fit pair, and G8 portfolio evaluation; no extra per-batch instrumentation required | Compact counts, quantiles, shapes, masks, fitted-scaler IDs, train/validation curves, gradient/parameter norms already available, per-cohort forecast and P&L metrics; fingerprints and trace IDs | **Default and mandatory; cheap, streaming/aggregated, no raw/activation duplication** |
| **T1 — deterministic post-run replay** | One predeclared representative sample per first model family, and on a material anomaly or development underperformance requiring explanation | Reopen canonical input rows, recompute selected intermediate values and selected trained-model activations in **evaluation mode**, compare module inputs/outputs, produce a small Markdown diagnosis card with linked trace IDs | **Required capability; run on demand**, normally a handful of origins/trades, no model refit |
| **T2 — controlled diagnostic experiment** | Only if T0/T1 cannot separate credible hypotheses and the frozen roadmap permits the intended experiment | Small approved synthetic probe or separately approved refit/ablation/capacity or five-to-twenty-stock comparison with matched controls | **Conditional; any actual neural fit consumes D6h budget and must be authorized/logged**; do not auto-search |

**No constant live activation dump.** The program needs to *reconstruct* evaluation-mode intermediate tensors from the immutable canonical data, scaler, config and retained model checkpoint. Exact historical training-time dropout masks/optimizer internals **cannot** be reconstructed from a final checkpoint alone and must not be falsely claimed replayable; training failures are diagnosed using existing epoch/gradient/sampler summaries and, if indispensable, a separately justified short reproducible run.

### 13.2 What must be traceable at each boundary

Use a stable `run_id`, `(ticker, session, origin, historical-step)` key, source `period_end`/`available_at`, and final `prediction_id`/`trade_event_id`. Maintain a **compact stage manifest** for the full dataset and **on-demand actual values** for selected cases. These are **not new input features**.

| Boundary | T0: inexpensive full-population evidence | T1: exact values available for a selected case | What a divergence may indicate |
|---|---|---|---|
| **B0 Raw source → canonical bars** | Source/version hash; per-stock/period/bar-slot coverage; OHLC and actions anomaly counts | Genuine unadjusted and adjusted OHLC, share volume, split/dividend events, source timestamp and unique source-row locator | Missing/corrupt vendor bar, wrong adjustment, symbol changes, calendar mismatch |
| **B1 Canonical bars → as-of observations** | Selection/age statistics, freshness and missingness by stock, hour, market and period | Historical observation chosen for each required input, source publication time, forecast cutoff and reason for acceptance/rejection | Future bar, stale USA500, forward-filled completed return, overnight/closing-stub off-by-one |
| **B2 As-of → pre-scaled FT0/U1–U5/peer & TG0** | Feature validity/warm-up/denominator-floor counts, label and cross-sectional-MAD distributions, cohort retention | Component returns, rolling numerator/denominator, lookback observations, origin-matched M2 construction, feature flags, raw 4h five-name return vector, TG0 median/MAD/floor | Incorrect formula, wrong window, low-MAD label amplification, selection/attrition, peer misalignment |
| **B3 Pre-scaled → standardized/model-ready input** | Per-channel training median, unscaled MAD/fallback, empirical quantiles, missing-mask/neutral-fill rates, finite/constant-channel counts, historical extremes and no-clipping audit | Same chosen feature before/after floor and scaling, fitted training-stat identifiers, mask, final `(48,16)`/`(48,5)`/peer channels in correct order | Signal compressed, extreme scale, stale scaler, train/test transform mismatch, feature identity swap |
| **B4 Model input → encoder / gate / mixer / readout** | Input/output shape and finite-value check, aggregate hidden/output norm and variation (on a tiny fixed audit sample), optional mechanism entropy/variance from G7 | Initial model-ready tensor, final/selected historical hidden states, market gate weights, peer/synthetic exchange result, SP3 `H` and `H_tilde`, TM1 weights/readout **only if that module is actually present** | Hidden collapse, saturation, gate stuck at identity, peer mixing absent, wrong stock-axis, incorrect mask propagation |
| **B5 Representation → predictions/ranks** | Forecast dispersion across stocks/sessions, tie/constant-prediction frequency, per-stock score distributions, forecast/realized co-movement, session Rank IC/MSE and loss concentration | Five raw model scores, midranks, selected long/short, labels after maturity, checkpoint/seed and prediction IDs | Shared-intercept-only forecasts, weak cross-sectional separation, extreme-score sensitivity, ranking instability |
| **B6 Predictions → candidate sleeves/orders/fills** | Eligible/entered/vetoed/cap-rejected/emergency counts, actual order size/turnover, slippage-cost scenarios | Exact proposed sleeve ranks/weights, veto/admission reason, existing physical shares, target shares, net order, minute-open fill, cost and unresolved order state | Correct rankings but wrong trading choice, churn, veto suppression, phantom fill, post-cost cap rejection |
| **B7 Fills/positions → equity/metrics** | Full-calendar daily gross/net return, long/short contributions, cost/borrow drag, exposure, drawdown, policy A/B, randomized baseline distribution | Executed order and physical stock position state, cash/short liability, marked holdings, itemized costs, daily equity reconciliation, exact report-row provenance | Predictive signal not economically tradable, exposure concentration, bookkeeping defect or return aggregation error |

**Replay stops at the first causal divergence:** compare two models/dataset versions on the *same* keyed observation, when legitimately comparable. If B0–B3 disagree, inspect raw/timing/preprocessing before interpreting B4–B7. If B0–B5 agree and reported P&L differs, prioritize the portfolio execution and aggregation ledger. A correct model can still have poor predictive or economic results.

### 13.3 Lightweight samples, metrics and replay tools

- **Fixed representative case set:** choose and freeze approximately **8–12 eligible development origins** by stable keys before viewing their performance, covering both forecast origins, beginning/middle/end of the fitting/development chronology, at least one high-/low-volatility state where possible, and valid normal/masked-market cases. Include a stock action, DST/early-close or low-MAD case **only when truly present and valid**; these edge cases may instead use already approved synthetic G1–G3 tests. No fabricated cases.
- **Exception-directed set:** after noticing a failure, optionally add **up to 3–5 distinct worst/odd cases** per investigated failure class (e.g. extreme loss day, disagreement between policy A/B, missing exit). Mark these `POST_HOC_DIAGNOSTIC`, not a randomly representative sample and never a basis for retrospective model selection.
- **Efficient numeric profile:** for each applicable boundary summarize count, fraction missing/nonfinite/masked, mean or median, robust spread, a few fixed percentiles, proportion constant/tied, and small per-stock/per-origin/regime breakdowns. Derive most distributions from shared stored features and prediction tables rather than writing new materialized arrays. Optional compact plots only when they add interpretation.
- **One small reproducible diagnostic entry point** (names/paths are illustrative, not an imposed repository structure): commands equivalent to `diagnose summarize --run-id ...`, `diagnose trace-origin --run-id ... --session ... --origin ... --ticker ...`, `diagnose trace-trade --event-id ...`, and `diagnose compare --run-a ... --run-b ...`. The *same functions* must be importable into automated tests; avoid many independent scripts containing duplicate preprocessing code.
- **Generated output:** one concise `model_failure_diagnosis_<run-or-comparison>.md` plus a small machine-readable summary (`.json`/`.jsonl`), with **upstream source references, before/after boundary values and first divergence**, selected examples, hypotheses tested, evidence and unresolved uncertainties. A bounded `.npz`/table snapshot may be written for selected examples only when recomputation is difficult; never dump whole-batch per-layer tensors for every epoch.
- **Hashes and deterministic replay:** check that the snapshot can be reproduced using canonical data, fitted scaler, retained final-refit checkpoint, feature dictionary, model config and library versions. If replay cannot reproduce a recorded prediction within justified numerical tolerance, mark it a **reproducibility or version-lineage defect**, not simply a low-performing model.

### 13.4 Post-training diagnostic ladder: finding *why* a model performed poorly

Do not launch an automatic search. Generate a **hypothesis/evidence table** in the report and follow the least costly discriminating check first:

| Observed symptom | Prioritized post-run checks (cheap first) | Plausible interpretation, not an automatic conclusion |
|---|---|---|
| **Training loss does not fall** | G5 synthetic tiny-batch overfit and label alignment; feature/target spread; nonfinite/near-zero gradient, clipping rate, optimizer config; prediction variance | Implementation/optimization error, unusable input representation, excess target noise, or insufficient model capacity |
| **Training loss falls, development Rank IC/MSE poor** | Train-versus-development loss gap; per-stock/time/regime distributions; label MAD-floor concentration; seed variability; output range; training-only scaler IDs; selection provenance | Overfitting, nonstationarity, weak rank information, target noise or small-effective-sample instability |
| **Development strong, subsequent held-out result weak** | Frozen split/seed/manifest check; compare feature/target distributions, retention, regime/episode mix; cohort IC/turnover; one-look selection record | Dataset shift, selection optimism, unstable market relationships, or sampling uncertainty; do not retune using confirmation |
| **Predictions near identical across stocks** | Per-origin score SD, tie rate, final hidden-state cross-stock spread, readout weight, sample source identity, factor/common-market-only contribution | Forecast collapse, shared-common-effect dominance, loss/feature issue or truly weak cross-sectional signal |
| **Only a few dates dominate MSE or net P&L** | Top 1/5/10% session error/return concentration; raw returns, TG0 median/MAD/floor, extreme features; one trade/equity trace | Low dispersion amplifying TG0, event concentration, outlier dependence, leverage/transaction issue |
| **MC1/MC2 adds no gain or gate behaves oddly** | MC0 same-input control; endpoint/history state variation, mask, identity-equivalence, gate entropy/variance, weight and gradient norms | No incremental conditional signal, state not varying, undertrained/saturated gate, or mechanism not useful; no automatic temperature sweep |
| **Peer/SP3 improvement vanishes or fails** | D8 own+USA500 and full-peer matched controls; pair/lags/stock-order; SP3 off-diagonal response and synthetic probe; 5-stock sector diversity | No incremental peer information, common market explanation, wrong mixing, or structurally insufficient cross-section |
| **Rank IC improves but net P&L worsens** | Long/short leg gross contribution; correct stock ranking vs extreme selection, sign diagnostic *ex post only*; Policy A/B trade records; physical reversal duration, turnover, veto/cap failures, cost- and borrow-scenario replay | Economic signal too small relative to costs, rank stability/churn, exposure/concentration or simulator defect |
| **Model works for one stock/origin/regime, not another** | Matched eligible dates; source missingness, per-ticker feature shifts, source/regime occupancy, origin-specific label and P&L breakdown | Domain heterogeneity, limited peer coverage, regime exposure or insufficient subgroup sample |

**Training diagnostics versus explanation:** A model that fits a synthetic signal but not market data demonstrates *capability*, not market predictability. A model with acceptable train/dev MSE but weak Rank IC may simply be learning a magnitude/level relationship not useful for ordering five stocks. A positive Rank IC may be economically too small or too short-lived to survive turnover and execution costs. Do not automatically increase width, data window, dropout, gate temperature or loss weighting to chase these symptoms.

### 13.5 Special diagnostic protocol: performance drops when expanding the universe (e.g. five → twenty stocks)

**This is the user's key additional use case.** A five-to-twenty-stock comparison is not a pure scaling benchmark: it can simultaneously change source coverage, stock composition, the TG0 target (median/MAD across different stocks), feature scalers, the number/diversity of peers, and SP3 stock-axis matrix sizes. The prior D8h approval permits **at most one justified expansion**; this diagnostic does not independently activate it.

Before attributing poor twenty-stock results to model capacity, produce one **five-to-twenty bridge report**, using the permitted *development* population, with these checks in order:

1. **Common original five:** Compare original five-name raw OHLC/corporate actions, 48-step FT0 and U1–U5 values, availability/retention, and execution-price rows after they enter the expanded canonical store. At identical keys, unexpected differences isolate a source/preprocessing change **before** any claim of generalization failure. Do not leak new-universe scaler fit data into the old archived model.
2. **Separate target shift:** For the same original five stocks and same genuine future returns, calculate the existing five-name TG0 and the newly required twenty-name TG0 using each legitimately fitted denominator-floor protocol. Show median, MAD, rank and target-value changes. **Rank/median comparisons across different universes are not the same outcome**; never present a direct 5-stock IC versus 20-stock IC change as an apples-to-apples architecture effect.
3. **Old names versus new names:** Compare eligible-session/calendar coverage, missingness, liquidity, feature/target quantiles, scaler/floor fit values, sector composition and market-state occupancy. Break development metrics out by original-five versus newly added names, same dates where possible, and include uncertainty/coverage cautions; do not select favorable new tickers after seeing performance.
4. **Changed peer architecture:** Record N, canonical ticker order, peer composition/sector replication, SP3 `M1/M2` dimensions and any fixed-identity features. **A trained N=5 SP3 cannot be applied as an N=20 mixer without redesign/refitting.** Compare the stated N=5/N=20 architecture and parameter budgets; do not silently reuse incompatible weights.
5. **Decompose financial economics:** Compare turnover, rank-change frequency, long/short candidate switches, spread/cost assumptions, borrow sensitivity, exposure-cap rejections and realized gross/net returns. Fixed one-long/one-short trades across twenty candidates are not necessarily economically equivalent to those across five.
6. **Only after steps 1–5:** Determine whether there is enough evidence for a *new, separately authorized* matched development control or refit that isolates an information/capacity issue. Respect D6h and the expansion protocol. Retain frozen five-stock results; expansion cannot retrospectively change them or re-open protected confirmation for selection.

The bridge report's outcome must explicitly distinguish **SOURCE/PIPELINE CHANGE**, **TARGET/POPULATION CHANGE**, **REPRESENTATION/CAPACITY CHANGE**, **ECONOMIC/EXECUTION CHANGE**, and **STILL INCONCLUSIVE**. More than one label may apply. Negative twenty-stock evidence does not prove the five-stock mechanism was spurious, and a positive twenty-stock result does not repair a failed five-stock source audit.

### 13.6 Evidence strength, error attribution and confirmation protection

Every model-failure diagnostic report must contain:

- **Symptom and reproduction key:** model/fold/seed/date, observed metric or anomaly, relevant T0 summaries, and whether the run was valid under G0–G9.
- **First differing boundary:** B0–B7, exact selected before/after values and source/scaler/checkpoint lineage; or `NO DETERMINISTIC DIVERGENCE FOUND` for a scientifically plausible failure.
- **Candidate explanations:** at most a few testable hypotheses, strongest existing evidence for/against each, and the cheapest next discriminating test. Distinguish a **verified defect**, an **empirically supported but uncertain hypothesis**, and **unresolved**. Do not automatically assign one root cause.
- **Cohort decomposition:** when relevant, per stock, forecast origin, time period, regime, original/new universe, high-loss and high-churn dates, with sample/episode counts and selection/coverage caveats.
- **Downstream scope:** which artifacts need recalculation if a *verified defect* is repaired, using §12.3 dependency map; unchanged, valid checkpoints or datasets need not be duplicated or retrained.
- **Protection of the final confirmation:** diagnostic inspection of July 2024–June 2025 may verify correctness and explain a locked result **after** A-E9, but may **not** change an already locked model/feature/threshold, rerank candidates, authorize hidden rescues, or preserve claims that a newly modified model was independently confirmed on the same period. Mark all outcome-selected examples post hoc.
- **No change to advancement:** G0–G9 status, D5d Rank IC evidence, net trading results, D6h pair ceiling, optional-branch activation, and append-only reporting remain authoritative. This section adds reproducibility and interpretability evidence, not an alternative promotion metric.

### 13.7 Minimal deliverables and acceptance checks

The future Codex handoff must require **one small, testable replay/diagnosis utility** (library plus a CLI, not a suite of heavyweight services) and **one compact report template**. It must be possible, without a neural refit, to:

1. Reconstruct a fixed origin from its raw source observation IDs through calendar/as-of alignment, selected raw feature calculations, fitted preprocessing, model input tensor and final five-stock scores.
2. Reproduce the retained inference-mode output of a chosen gate/mixer/readout and expose the input/output of **only modules present in that trained architecture**, or explicitly report that a value cannot be recreated from retained artifacts.
3. Trace one scored decision through both policy choices, trade admission, executed net orders, borrow/transaction costs and marked equity.
4. Compare the same keyed case under two versions or models, locate the earliest validly comparable divergence, and identify differences due to information set, target, fitting history or stock-universe definition.
5. Generate a short development-phase failure report from already stored training metrics and a small selected replay sample, without copying raw datasets or changing fitted models.
6. When a twenty-stock expansion is explicitly activated, produce the five-to-twenty bridge report **before** interpreting a change in Rank IC or net Sharpe as an architectural failure.
7. Demonstrate with small **deliberately injected synthetic faults** (e.g. one shifted `available_at`, one scaler mismatch, one swapped ticker, one cost double charge) that the trace identifies the right boundary and affected artifact IDs; synthetic tests must not be reported as real financial results.

**Completion evidence:** An audit/diagnostic test matrix, reproducible example report and versioned diagnostic tool interface. Do not declare this requirement PASS until the tool can genuinely reconstruct a selected prediction and portfolio event from canonical files. **Do not save all per-layer activations, optimizer states at every update, full copies of pre/post processed data, or per-experiment Parquet datasets to meet this requirement.**

---

## 14. Minimal auditable artifacts and filenames (conceptual, not fixed repo paths)

An economical implementation needs **four** central product families, not a proliferation of independent monitoring systems:

1. **Canonical data/feature manifest**: source IDs, hashes, timestamps, sessions, actions, indicators, scalers, validity/retention and historical-availability constraints.
2. **Single stage-gate audit index**: G0–G9 statuses, key counts, approved thresholds, failure cards, human-inspection examples and upstream artifact links.
3. **Append-only experiment ledger**: planned/attempted/conditional model branches; fit hashes, seeds, optimizer/epoch summaries, predictions, failure status and budget.
4. **Portfolio and research-results ledger**: immutable per-model predictions and reusable physical transaction/equity events keyed by policy and cost, full development/confirmation metrics and mandatory negative-result reporting.

The implementation may place these as files or logical tables in a sensible repository layout. The §13 diagnosis report and selected-case replay are **small views of these same artifact families**, not a fifth full dataset or a second logging framework. **Do not prescribe new giant snapshots or require separate datasets for every audit gate.** Store a short Markdown coding-session report after each Codex session, listing changed files, tests passed/failed, unresolved questions and restart point.

## 15. Go/no-go logic before Codex handoff

**Ready for an audit-only A-E0 handoff:** The present gate definitions, versioned design record and unresolved-source table are sufficient to instruct an agent to *measure actual feasibility*, provided the user explicitly requests the handoff. The agent must stop rather than guess a different source or modify an approved clock.

**Not ready for unconditional A-E1–A-E9 fitting/trading:** Stock/USA500 source and minute-execution data remain unverified, shared clock sign-off remains pending, and conditional branch activation is not established. D13-C07 baseline choices can be implemented only after the consolidated addendum is acknowledged as the new approved version.

**No claim that any audit has passed:** This document prescribes checks; actual evidence must be generated by future implementation/testing. Audit reports must record PASS only with objective traceable outputs.

---

## Appendix A — D13-C07: newly adopted minimal A-E1 baseline protocol

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

### v1.1 change log (additive relative to preserved v1.0)

- Added §13 **post-run explanatory failure diagnosis** covering raw-to-processed values, fitted transformations, model module boundaries, rankings, trades and equity; on-demand deterministic replay; targeted cohort/error analysis; and five-to-twenty-stock generalization bridge.
- Existing sections G0–G9, baseline Appendix A, approved quantitative thresholds and experiment activation rules were **not changed**. Section numbers below the new material were adjusted (minimal artifacts §14, go/no-go §15).
- The new diagnostics are **implementation requirements approved by the current user request**, not assertions that older source documents mandated them or that data/model failures were already observed. No audit has run and no source/collaborator gate is passed.
