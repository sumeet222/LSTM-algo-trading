# Track A — Incremental Codex Implementation and Human Review Plan

**Version:** Planning v1, 2026-10-10  
**Status:** Implementation *plan*, not authorization to start training, change the frozen protocol, access confirmation performance, or declare an audit passed.  
**Authority:** `Shared_Project_Specification.md`; `Track_A_Architecture_Experiment_Roadmap_First_Pass_FROZEN_v1.0.md`; `Track_A_Consolidated_Implementation_Design_Record_v1.2_2026-10-10.md`; `Track_A_Stage_Gated_Audit_and_Failure_Traceability_Plan_v1.1_2026-10-10.md`. The source documents—not this implementation schedule—control model mathematics, thresholds, experimental priorities, activation, and sign-offs.

## 1. Purpose and operating contract

The six broad phases are subdivided below into **small, independently reviewable Codex work packages**. Each is an individual Codex prompt and should normally end at a **human review point**. The researcher can inspect a small set of named artifacts and representative code paths, rather than read the whole implementation or supervise every function call.

**Hard requirements:**

1. **No automatic jump to the next package without human approval.** Codex reports what it finished and stops. Small *within-package* unit tests and inspections are automatic, not subject to manual approval after every file.
2. **Training packages target no more than 4 hours of active fitting and must have a hard stop at 4.5 hours**, leaving time for diagnostics and clean checkpoint/report writing within an approximately 5-hour working session. The estimate is **not a guarantee of runtime**; perform a small hardware benchmark first. Limit work by both time and the preapproved **40 D6g calibration/refit training-pair global ceiling**. A complete training pair is two fits (inner-calibration and fresh refit), not one epoch or one seed.
3. **Never interrupt halfway through a run in a way that makes evidence unverifiable.** Save completed checkpoint/ledger state between fitting tasks; when the time budget is reached, do not launch another fitting task. If a single fit cannot finish within the envelope, stop safely and request a plan revision rather than silently changing epochs, model, schedule, or metrics. If resuming a partial run is feasible, verify reproducible optimizer/sampler/RNG state before claiming equivalence; otherwise rerun according to the approved accounting.
4. **Implementation packages precede experiment packages.** Writing code for a conditional model is not approval to fit it. The first experiment phase after feasibility is the minimal reference ladder, not a giant all-model batch.
5. **Review by evidence:** every package must provide an executive `REPORT.md` (short summary), machine-readable test/audit results, relevant paths, and **3–8 exact source locations or commands** the human can check. Include small row examples, concise tables, and single-sample provenance/trace replays where applicable; do not dump whole datasets or hidden-state tensors.
6. **No silent assumptions:** report `PASS`, `WARN`, `BLOCKED`, `INVALID`, `INCONCLUSIVE`, `INACTIVE CONDITIONAL`. Missing USA500/Alpaca coverage, formation-membership evidence, 240-minute shared-clock approval, and any required comparator remain genuine blockers. One blocked branch need not stop unrelated verified tasks.
7. **No large duplication:** immutable canonical raw prices; single reusable feature/target store; lightweight keyed prediction records; reusable portfolio event ledger; no per-seed/per-model/per-cost Parquet copies. Avoid destructive cleanup without human permission.
8. **Completeness:** append-only experiment/decision/audit ledgers include unsuccessful, invalid, deferred, and inactive branches. Preserve confirmation unopened until explicit human authorization after a manifest lock.
9. **Repository safety:** use the existing repository/AGENTS.md if present; inspect before changing conventions; commit or provide a precise diff manifest; no credentials in logs, tests, or Git. Coding-session `.md` reports must list created/changed files and purposes.
10. **No live brokerage deployment:** minute-open fills remain historical proxies under the frozen model; focus on accurate research-grade causal replay.

### Deliverables for every Codex package

Use *equivalent naming if the repository's conventions differ*; these are suggested output roles, **not mandated paths**:

- `package_report.md`: objective, files changed with key functions, sample output, status, tests/audit counts, blockers, next recommendation, elapsed runtime and new disk usage.
- `checks.json`: named test IDs with PASS/FAIL/BLOCKED, evidence paths, input/code/config hashes.
- `trace_examples.md` or small CSV/JSON only when applicable: at most several ordinary and anomalous examples with source→feature→prediction→trade keys.
- Append to shared audit/experiment ledger and update dependency/blocker list. Reports use paths/IDs to shared artifacts; **never copy raw data into report folders**.

### Human review protocol (always)

The human inspects (i) package summary and status, (ii) two or three representative expected values against raw source or hand calculation, (iii) identified key function/line references and changes, (iv) failed/blocked samples and their provenance, (v) data/runtime impact. Then explicitly chooses **approve / correct and rerun / hold**. Code paths listed below are *functions to identify*, not claims that files already exist.

---

## 2. Package map and resource targets

Estimated durations are **planning ranges for Codex activity after data are locally available**, not verified benchmarks. External data downloads, vendor access negotiations, collaborative sign-offs and human review time are excluded. Tasks may need to be split again if a benchmark predicts overrun.

| ID | Package (individual Codex prompt) | Estimated Codex time | Relevant audit | Human decision |
|---|---|---|---|---|
| P0.1 | Repository and protocol inventory | 0.5–1.5 h | G0 | Approve scope and file ownership |
| P0.2 | Environment, reproducibility, ledger and audit skeleton | 1–3 h | G0 | Verify commands and evidence format |
| P1.1 | Alpaca/source provenance and historical coverage feasibility | 1–3 h + external delays | G1 | Approve/block source-dependent work |
| P1.2 | USA500 source contract and as-of semantics | 0.5–2 h + external delays | G1 | Approve/block market branches |
| P1.3 | Universe formation, corporate actions, stock hourly/minute QA | 2–4 h | G1 | Approve canonical raw panel |
| P2.1 | Exchange calendar, feature and issuance clocks | 1–3 h | G2 | Verify timestamp examples and sign-off gate |
| P2.2 | Execution-price calendar, TG0 outcomes, purge and eligibility | 2–4 h | G2 | Inspect five-stock return/label cases; C01 |
| P2.3 | FT0 stock feature build + normalization | 2–4 h | G3 | Inspect raw→indicator→scaled examples |
| P2.4 | U1–U5 market features, masks and market/stock coverage joins | 2–4 h | G3 | Verify source-aligned market examples |
| P3.1 | Canonical prediction/portfolio event schemas and synthetic ledger | 1–3 h | G4 | Inspect hand-computed cash/position identity |
| P3.2 | Portfolio policy A, netting and exposure admission | 2–4 h | G4 | Trace sleeve→net order→shares |
| P3.3 | Conflict-veto policy B, costs and borrowing scenarios | 2–4 h | G4 | Compare A/B on scripted conflicting origins |
| P3.4 | Risk, emergency, failed exits, overnight, mark-to-market | 2–4 h | G4 | Trace exception to equity and status |
| P3.5 | Momentum, ridge fitting and exact leakage-free selection | 2–4 h | G4 | Inspect lag mapping and ridge objective |
| P3.6 | Baseline backtests: cash, buy-and-hold, random paths | 2–4 h | G4/G8 | Inspect economic benchmark fairness |
| P4.1 | LSTM engine, loss, optimizer, grouped sampler and tiny smoke test | 2–4 h | G5 | Inspect mini-batch math and output shapes |
| P4.2 | Early stopping, two-pass refit, seeds/checkpoints and restart safety | 2–4 h | G5 | Inspect cutoff and checkpoint trace |
| P4.3 | **Training batch A:** A-E2 stock-only pilot | ≤4 h active fit | G6 | Review learning & failure diagnostics |
| P4.4 | **Training batch B:** A-E3 MC0 market information pilot | ≤4 h active fit | G6/G7 | Review matched TM0 comparison |
| P4.5 | **Training batch C:** A-E4 MC1 endpoint gate pilot + gate diagnostics | ≤4 h active fit | G6/G7 | Review identity and gate behavior |
| P4.6 | E4R regime slices and MC2 *activation audit* | 1–3 h; conditional fit separate | G7/G8 | Explicitly activate/defer MC2 |
| P4.7 | E5 peer summaries and ridge information tests | 2–4 h; neural fit separate | G7 | Review peer keys and comparison |
| P4.8 | **Training batch D:** E5 ordinary LSTM peer pilot, if eligible | ≤4 h active fit | G6/G7 | Compare with MC0/peer ridge |
| P4.9 | E5L directed lead–lag ridge, reverse/control/null diagnostics | 2–4 h | G7 | Decide if LL1 neural pilot justified |
| P4.10 | **Conditional training batch E:** exactly one eligible MC2/LL1/SP3-related pilot | ≤4 h active fit | G6/G7 | Approve only the predeclared branch |
| P4.11 | Full-peer information control and SP3 mechanism tests | 2–4 h implementation/test; fits separate | G7 | Review fair SP3 comparator prerequisite |
| P4.12 | **Conditional training batch F:** SP3 or alternative explicitly activated | ≤4 h active fit | G6/G7 | Review spatial generalization & costs |
| P4.13 | Other conditional A-E7/A-E8 or SP1/MC1+SP3 branches | **Separate per approved branch; normally skip** | G7 | Approve each branch and budget before prompt |
| P5.1 | Development forecasting comparison and sample/replay audit | 1–3 h | G8 | Check IC/MSE paired dates and anomalies |
| P5.2 | Development trading comparison (both policies, all costs) | 2–4 h | G8 | Inspect net P&L, churn, cost and rejected trades |
| P5.3 | Dependency-aware uncertainty and regime/seed stability | 2–4 h | G8 | Examine paired-block and HAC limitations |
| P5.4 | **Training batch G:** needed finalist seeds/folds, subdivided by cutoff/family | ≤4 h active fitting **per prompt** | G6/G8 | Review **each** train batch and remaining budget |
| P5.5 | Post-run root-cause replay, five→20 research bridge *if approved* | 1–3 h diagnostics; new training separate | G8 + §13 | Verify cause hypotheses and coverage |
| P5.6 | Development synthesis, shortlist and confirmation manifest | 1–3 h | G8/G9 prelock | Human locks candidates/protocol |
| P6.1 | Confirmation preflight and evidence-only dry run | 1–2 h | G9 | Explicit approval required to unlock |
| P6.2 | **Training batch H:** locked preconfirmation refits, split by family/seed | ≤4 h active fitting **per prompt** | G6/G9 | Verify checkpoint IDs and no test use |
| P6.3 | **One authorized** untouched confirmation predictive/economic evaluation | 2–4 h + bootstrap | G9 | No post-result reselection |
| P6.4 | Final comprehensive report and archive/replay index | 2–4 h | G9 | Review all results, limits and missing experiments |

**These packages are not all compulsory:** conditional pilots and additional-compute packages are activated only by approved evidence. P0/P1/P2 packages can be reorganized slightly if the actual repository/data dependencies demand it, but any meaningful change must be documented. Avoid running P6.3 merely because training P6.2 completed.

---

## 3. Concrete human-verification cards by package

These cards define the minimum inspection surface. Codex should fill in actual file names, function names, line numbers, and observed outputs; this plan must not pretend those files already exist.

### Phase P0 — Repository and infrastructure

**P0.1 Repository inventory.** Show repository tree (bounded depth), existing AGENTS.md and instructions, code/data locations, git status, current disk usage/top file sizes, input artifact presence, and conflicts with frozen specifications. **Human checks:** actual source paths, whether prior code exists, no accidental destructive rewrites. **Stop:** missing authority docs or contradictory repo rules unresolved.

**P0.2 Environment and evidence harness.** Minimal reproducible environment/lock metadata; deterministic test entrypoint, shared audit runner status schema, lightweight experiment registry, provenance keys, no-secret check and safe default `dry_run`. **Human checks:** run commands and inspect one deliberately failed synthetic audit; confirm it blocks its dependent branch; inspect artifact retention and disk delta. **Stop:** automation can bypass missing human approvals or confirmation protection.

### Phase P1 — Data/source layer

**P1.1 Historical stock-source feasibility.** Verify Alpaca SIP entitlement, sample 2020–25 minutes and required warm-up, genuine minute-open values at forecast entries/exits, availability metadata, stock adjusted/unadjusted semantics, costs and storage estimate. **Human checks:** 3–5 raw `symbol/time/OHLC/available_at` samples across years, including 10:33/15:33; coverage-by-year/stock; source metadata evidence. **Stop:** unverified source, entitlement or execution prices. No dummy substituted prices.

**P1.2 USA500 source contract.** Show source identity, index/cfd/instrument and time zone, history, completed OHLC and daily-close availability, timestamps, `available_at`, freshness and volume nonassumption. **Human checks:** 3 market-day source records and historical as-of examples; verify no SPY or other substitute slipped in. **Stop:** incompatible or unknown source; unaffected stock-only work may continue.

**P1.3 Universe/actions/raw QA.** Point-in-time membership evidence and trailing-liquidity selection versus retrospective data-quality thresholds, backup logic, early closes, missing/duplicate/malformed bars, split share-adjustment/dividend ledgers. **Human checks:** audited formation matrix, one split case, 2 gap/holiday cases, source→canonical mapping and no duplicated raw store. **Stop:** unusable data or look-ahead universe claim.

### Phase P2 — Timing/labels/features

**P2.1 Calendar and as-of clocks.** Exchange-calendar-based six-hour-slot grid, closing stub, timezone/DST/early close; 10:30/11:30 feature cutoff, publish lag, actual issue/entry constraints; market freshness 90 min. **Human checks:** concrete timestamp trace for ordinary day, early close, DST boundary; verify clock cross-track sign-off status is not auto-approved. **Stop:** mismatch of proposed 240 regular trading minutes and common definition unresolved for labels/trades.

**P2.2 Target and eligibility.** Entry-exit minute references, four-hour returns, cross-sectional median and **unscaled MAD**, train-fitted epsilon, split purging, label availability, true C01 separation: causal input/entry eligible versus future label valid. **Human checks:** hand-calc all five returns/TG0 on one date, one missed exit, one label crossing split, one valid entry with invalid future exit that remains in portfolio replay. **Stop:** invalid timing, hindsight entry filtering, or fabricated fills.

**P2.3 FT0 features.** M1–M4,V1–V3,B1–B2,Q1–Q2,T1–T5 exact rules; warmups, RMS floors, Q1 matching slot, session-locked daily features, EMA/RSI, volume corporate adjustments, training-only pooled median/MAD. **Human checks:** pre/post for at least one stock/hour, overnight RSI boundary, one zero-range bar, missing bar, no-scaled-future audit; retention per origin/regime versus approved guards. **Stop:** future fit leakage, incorrect formula, insufficient coverage.

**P2.4 USA500.** U1–U5 derived from verified compatible course series; floor/scaler fitting once per market timestamp; valid endpoint and 46/48 historical states with masks; no unapproved learned mask channels. **Human checks:** source→U1–U5→scaled one ordinary/one missing case, previous-day momentum across historical steps, matched MC0/MC1 eligibility. **Stop:** source/timestamp and retention failure.

### Phase P3 — Trading foundation and cheap models

**P3.1 Shared event ledger.** Define keyed forecast→intent→virtual sleeve→aggregate shares→external order→fill→cash/equity records, no model-specific simulator code. **Human checks:** a synthetic one-stock long/short ledger balances; inspect key reconciliation functions and single-event trace. **Stop:** negative/duplicated cash accounting or missing trace links.

**P3.2 Policy A.** Four-hour long/short sleeve, 24.75% each leg, overlap and physical netting, 100% post-cost entry admission, 99% nominal dual-sleeve target, all-or-nothing reject. **Human checks:** conflict case with physically netted zero shares; expiration reopens physical exposure only where warranted; compare dollar arithmetic and delta shares with hand values. **Stop:** charges virtual rather than external trades, or anticipates future exit validity.

**P3.3 Policy B and costs.** Full-pair conflict veto, no change to existing sleeve, 0/2/5/10 bps per external filled notional once, 0/0.5/3% assumed annual borrow on physical short exposure under adopted daily convention. **Human checks:** same scripted forecast stream through both policies and different cost settings; verify skipped pair, cash ledger, cost identity, no broker-spread double charge. **Stop:** phantom fee or incorrectly attributed P&L.

**P3.4 Risk/exceptions.** 110% strict gross-exposure breach, full close and session halt, one-minute causal exit retry, failed entry handling, next-session resumption for unresolved exits, bounded missing-data reporting, separate forecasting labels. **Human checks:** 109.9%/110%/110.1% trigger cases, missing 14:33 exit with later first valid bar, unintended overnight, no artificial terminal fill. **Stop:** false flat position, invented NAV or unsafe inability to reconstruct fill.

**P3.5 A-E1 baselines.** M1 descending momentum, ridge lags `[0,1,2,5,11,23,47]`/112 own/147 with market, penalty grid `[1e-4,1e-3,1e-2,1e-1,1]`, chronological 63-session inner selection, pooled session-weighted loss, final permitted refit. **Human checks:** exact lag timestamps/columns, hand-computed weighted regression objective, solver scaling/intercept, selected lambda evidence, one no-future scaler check, deterministic score ties. **Stop:** penalty API mismatch or outer/confirmation target leakage.

**P3.6 Contextual benchmarks.** Buy-and-hold 09:30 initial retry and last eligible minute final sale, equity/dividends; randomized 1,000 independent uniform 1-long/1-short paths with fixed seed master, same policies/cost engine, no future ranking. **Human checks:** one buy/hold split/dividend path, one random permutation/replay seed, distribution and unoccupied sessions; report non-risk-matched nature of buy-and-hold. **Stop:** simulated trades generated using realized future performance.

### Phase P4 — Neural engine, then small model-specific training batches

**P4.1 Model training engine.** One-layer LSTM 32, input 48×16 (or later channel extension), zero recurrent state, final dropout 0.1, session batches 16, equal-session TG0 MSE, AdamW 0.001/0.01, global grad norm 1. **Human checks:** tensor dimensions/6433 params, synthetic 2-vs-1 origin loss=7 example, gradients, dropout ON training/OFF eval, repeated prediction reproducibility, no future label. **Stop:** nonlearning on a planted tiny problem, wrong loss, nonfinite gradient.

**P4.2 Training lifecycle.** D6g 60 max epochs, 10 patience, >=12 before stop, 0.1% qualifying relative MSE, inner 63-session validation and full-data refit exactly selected epoch; seed registry 42/123/2026, pair ledger/budget. **Human checks:** scripted validation curve selects correct checkpoint, 63-session cutoff, new model/optimizer refit, reused run deduplication, stop-before-40 budget guard. **Stop:** outer fold used to early-stop or confirmation data touched.

**P4.3 A-E2 training batch.** **One seed 42, one June-2023 cutoff pair** as initial pilot, after prerequisites. Postrun `training_health.md` includes loss curve, clipping frequency, predicted score dispersion, extreme TG0 loss concentration, sample forecasts and baseline matching. **Human checks:** does learning occur, are predicted scores effectively constant, does runtime imply later packages fit 4-hour limit? Decide next only after report.

**P4.4 A-E3 MC0 training batch.** One compatible seed/cutoff, 21-channel input, source-audit pass required. **Human checks:** same dates as TM0, 7073 params, a few stock/USA500 joins and paired model outputs, no new fit preprocessing on development.

**P4.5 A-E4 MC1 training batch.** Linear 5→16 scaled-softmax endpoint gate, identity initialization, same 21-channel input. **Human checks:** initial MC1=MC0 equality, 7169 params, gate gradient/entropy/state slices, no missing source. Review development evidence independently of net Sharpe.

**P4.6 E4R and conditional MC2 check.** Compute approved U2/U5 slices/episode counts, gate diagnostics, training-only within-window MC2 state-variation activation statistic. **Human checks:** source dates, non-hindsight thresholds, whether condition met, whether budget permits pilot. *Do not fit MC2 in this package.*

**P4.7 E5 summaries and ridge controls.** Leave-one-out peer mean/dispersion, targeted E5 ridge contrasts with same lag grid. **Human checks:** one four-peer hand calculation, validity, common-signal algebra caveat, matched origins, no neural run.

**P4.8 E5 neural pilot** when high-priority feasibility passes, one seed 42; same shared D6 protocol, 23 input channels/7329 params. **Human checks:** E5 versus MC0 paired IC/MSE and economic diagnostics, peer features at true completed times.

**P4.9 Directed E5L ridge.** Preformation high-/low-dollar-volume identities, reverse direction, lags 0/1, pair controls and timing destruction diagnostic. **Human checks:** source identities fixed before future outcomes, overnight lag boundary, coefficients/signs and matched conditional tests; decide LL1 LSTM eligibility (not automatically run).

**P4.10 Conditional pilot**: *one* candidate (MC2 or LL1 or other roadmap-authorized pilot) per independent prompt if its trigger passes. **Human checks:** trigger evidence filed **before training**, one-seed diagnostic, remaining budget; invalid/unpromoted/inactive branches logged.

**P4.11 Full-peer / SP3 readiness.** Ordinary full-peer 85-channel architecture (15265 params) with canonical target-excluding peers; SP3 rank 2, 20 mixer params/7093 total, GELU, nonaffine LayerNorm, residual identity. **Human checks:** full-peer vs SP3 input information and parameter-count differences, input permutation invariants, planted directed peer transfer, gate mechanisms. No spatial training until human approves.

**P4.12 Spatial pilot**: one approved SP3 fitting pair, seed 42, compared against full-peer fitted control; if full-peer control needs training, schedule **separate** ≤4-hour package and count its pair. **Human checks:** training health, predictions, identity vs stock-specific effects, appropriate comparator and net portfolio costs. SP1 is not automatically next.

**P4.13 Other optional branch packages**: MC1+SP3, SP1, TM1/TG2, TG4, AD3, FC6/7, universe expansion require independent documented activation and (where applicable) extra approval; each training pair is a separate capped job group, not all in one prompt. If inactive, report status only, **no code required solely for completeness**.

### Phase P5 — Slow human-guided interpretation and finalist selection

**P5.1 Forecast diagnostics.** Daily mean Rank IC with fixed tie/constant conventions, MSE, pairwise accuracy, coverage, 5-stock ranking examples, five largest positive/negative residual days, fitted output distribution. **Human checks:** independently recompute one day's IC, inspect sample with score collapse/outlier or label issue; determine which differences warrant deep replay.

**P5.2 Portfolio diagnostics.** Both policies and 0/2/5/10 bps with borrowing stress, full-calendar equity, drawdown, turnover, churn, physical netting and emergency exception counts. **Human checks:** reconcile 1–2 unusual high-P&L and high-cost days to event ledger; do not confuse forecast four-hour outcome with actual realized sleeve P&L.

**P5.3 Dependence and inference.** Paired five-session block (10/20 sensitivity), 10,000 resamples, HAC 5/10, WF1/WF2 separate, regime occupancy and seeds; no formal selection-adjusted significance claim from a post-fit permutation. **Human checks:** block samples keep origins/stocks together and only valid contiguous sessions; inspect uncertainty versus point improvements.

**P5.4 Finalist-seed and fold batches.** Schedule **separately by `(architecture family, fitting cutoff, seed)`**, or a bounded number of complete pairs measured to fit ≤4 h. Never launch all families/folds/seeds in one Codex instruction. After each batch check seed stability, train/test population matching, fit-pair budget and whether next approved replication is necessary. A failed batch is logged, not replaced by searching for a lucky seed.

**P5.5 Root-cause replay.** Use audit v1.1 §13: reconstruct a small number of normal/failed observations raw→aligned→features→scaled→hidden/gates/peer→scores→orders→costs→equity. Sample deliberately chosen before examining confirmation, plus train-vs-development shift and feature retention. When 5→20 expansion is explicitly approved, compare universe/membership, transformed-feature distributions, TG0 median/MAD, capacity and model transfer; **no automatic 20-stock fit**. **Human checks:** each root-cause claim accompanied by evidence, alternative explanation and next discriminating test. No dump of full tensors.

**P5.6 Selection & lock.** Full development evidence, simple-vs-complex one-SE preference, three-seed record, necessary comparator inclusion, rejected/blocked branches, proposed ≤3 family shortlist; escalate SP3 control vs family cap conflict **before** confirmation. Create immutable confirmation manifest only after explicit signoff. **Human checks:** confirm selection never saw July 2024–June 2025 outcomes; approve actual list and budget.

### Phase P6 — Confirmation and final research archive

**P6.1 Pre-confirmation dry run.** Test data/config/checkpoint IDs and outputs using **synthetic data or authorized preconfirmation history only**. Verify access boundary, preflight sign-offs, fit pair availability, manifest match. **Human checks:** sign manifest; explicitly approve one-time confirmation unlock. **No confirmation forecasting/economic metrics here.**

**P6.2 Final preconfirmation refits.** Freeze architecture/seed/cutoff, then fit one or a small number of complete June-2024-cutoff D6g pairs in ≤4h groups; save checkpoint IDs/hashes and report. **Human checks:** no confirmation labels; correct epoch refit and model family, resource ceiling. Do not start next group without approval.

**P6.3 One confirmation execution.** Run the locked predictions, Rank IC/MSE, both costed policies, core uncertainty and expected reports **once**; full source/equity reconciliation. **Human checks:** are claims bounded by results, no hidden re-selection, all required controls? Any genuine code defect and corrected re-evaluation must preserve and disclose loss of pristine first-look status.

**P6.4 Archive and presentation.** One research report with success, failure, inconclusive and inactive statuses, architecture diagrams and parameter counts, prediction vs net-economics distinction, audit/trace links, resource/disk usage, limitations and release checklist. **Human checks:** complete experiment ledger, source provenance, disclosure of uncertainty, reproducible commands; no confidential keys or forbidden font files.

---

## 4. Training-time control and scheduling rules

1. **Benchmark before planning runs.** From P4.1/P4.3, estimate median/p90 time per complete calibration/refit pair on actual device and dataset. Since the initial experiments have different input dimensions or activation costs, measure at least one representative larger architecture before scheduling multiple pairs in a single package.
2. **At most ~4 h fitting per training package; ~0.5 h reserve for orderly stop and evidence generation**; never promise it will finish just because 40 pairs are globally permitted.
3. **Training pair is indivisible for scientific reporting** even if its calibration and refit can checkpoint or execute sequentially. If a refit is missing, status is INCOMPLETE, not COMPLETED.
4. If estimated next complete pair breaches the package budget, **do not start it**. Generate a queue continuation manifest with remaining seed/fold/architecture tasks; next human-approved prompt resumes the queue. Do not alter training hyperparameters to force completion.
5. Keep a small run manifest with `run_id`, `family`, `seed`, `fit_cutoff`, `data_hash`, `config_hash`, `checkpoint`, `status`, `epochs`, `elapsed`, `remaining_pair_budget`; skip exact duplicates after checksum verification.
6. Saving detailed tensors every batch is prohibited. Use cheap scalar telemetry; issue targeted post-run `.py` diagnostics and `.md` reports for anomalous runs. A single sample trace includes a handful of source rows, feature values, masks, hidden-state summaries and linked trades, not a full raw-data copy.
7. **The 24 cumulative training-hour envelope is preliminary**, subject to actual benchmark and human review; it does not supersede the 40-pair ceiling or justify truncating mandatory comparisons. If both cannot be satisfied, explicitly escalate a resource/scope amendment.
8. Formal full-selection temporal-null reruns are conditional and **not funded by default** under the 40-pair budget. Do not present cheap shifted-peer or shuffled-output checks as selection-adjusted significance tests.

## 5. Review cadence and stop/go policy

- **Human checkpoint after every P0–P3 package** (usually 1–4 hours of Codex work). Multiple tiny adjacent units may be combined only after the actual runtime and file changes are known; keep separate audit evidence and approval records.
- **Human checkpoint after P4.1 and P4.2**, then after every distinct training batch (≤4h fit); review signal/gradient/retention/compute before expanding.
- **Human checkpoint after each P5 package**; reserve extra review time for unexpected ranking gains/losses or trading-cost anomalies. Deep replay is on-demand and targeted, not automatic on every seed.
- **Human approval at P6.1 is mandatory** before any P6.3 confirmation-period metric, even if Codex considers every unit test passed.
- `PASS` permits only the next authorized dependent package. `BLOCKED` halts only dependent work. `INVALID` requires versioned repair and downstream re-evaluation. `WARN` requires documented review when material. `INACTIVE_CONDITIONAL` is a normal final state for optional experiments.

### Example of the human inspection surface after one model fit

1. `package_report.md`: one-page conclusion, statuses and changed files.
2. `training_health.md`: train/validation MSE curves, best epoch, clipping %, predicted-score spread, extreme-loss days, optimizer failures.
3. `examples.md`: at most 3–5 `stock/session/origin` prediction examples with true target and provenance keys (after labels mature).
4. `economics_summary.md`: both policies, headline 5bps net performance and 2/10bps sensitivity, with 1–2 P&L-day trace IDs.
5. `checks.json`: source/clock/leakage tests and pipeline checksum summary.
6. Functions/lines: data loader, feature scaler, `forward`, loss aggregation, checkpoint selector, portfolio external order calculation. Codex **must provide actual paths/line numbers from the repository**, not the conceptual names here.

## 6. Decisions that cannot be automated away

- Source authorization and proof of compatible historical Alpaca SIP and course USA500 timestamps/fields; no unapproved proxy replacement.
- D3's `240 continuous regular-session minutes` vs shared `four complete hourly advances` collaborator sign-off.
- Point-in-time formation membership/liquidity and disclosure of retrospective data-quality selection.
- Any change to the frozen design, source, historical window, TG0, cost schedule, eligibility, missingness, benchmark, or number of finalists.
- Conditional MC2/LL1/SP3/SP1/A-E7/A-E8 activation and any 20-stock expansion.
- Potential fourth full-peer neural family needed for a strong SP3 confirmation claim: seek explicit budget/protocol amendment or narrow the claim.
- Permission to compute untouched A-E9 confirmation metrics.

## 7. How to use the project files

**Yes, add the two latest authoritative files to the ChatGPT Project:**

1. `Track_A_Consolidated_Implementation_Design_Record_v1.2_2026-10-10.md` — current detailed approved-design record.
2. `Track_A_Stage_Gated_Audit_and_Failure_Traceability_Plan_v1.1_2026-10-10.md` — current audit and post-run diagnosis contract.

Also keep the **frozen Track A roadmap v1.0** and **Shared Project Specification** in the Project, and add **this implementation plan** as a third handoff document. The earlier consolidated v1/v1.1 and audit v1 files are superseded references and need not all be added as current authoritative Project knowledge; keep them in version control/history for traceability. Keep the shorter presentation summary separately if useful for communications—it is not the implementation authority.

**Version control:** Use explicit document version labels and one authoritative `CURRENT_PROTOCOL` pointer/manifest so Codex does not guess between similar files. Project files can provide context to ChatGPT; Codex must also have actual file access in its working repository or attached Codex environment. Uploading to this Project alone does not prove the Codex workspace sees them.

## 8. Handoff sequence to start

**First Codex prompt: P0.1 — Repository and protocol inventory only.** It should read the four authoritative research documents and existing `AGENTS.md`, report gaps/contradictions and paths, inspect disk/credential safety, and emit a bounded `package_report.md` plus `checks.json`. **It should not download large datasets, implement models, train, run backtests, or touch confirmation performance.**

After you submit that report here, we can inspect exact code/repository conditions and issue P0.2 or a small corrective package. This allows substantial autonomy within each manageable chunk without losing human control over experiment validity.
