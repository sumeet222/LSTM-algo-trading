# S4-A final research decision

**Eight of eight authorized neural lifecycles completed, with eight scientific/visual gates and final all-eight browser QA passed. Eight P baseline fits and eight train-prefix recipes also completed. Ledger: 106 → 114/200; no failures, retries or extra fits.**

**Scientific decision: technically feasible with seven daily candidate origins, but no reliable incremental ranking edge established.** All primary absolute-IC and model-minus-baseline descriptive intervals include zero. No trading-profit, independently verified publication or protected-confirmation claim is made.

## Complete diagnostic map

- [Detailed training, validation, refit and OOS diagnostics](S4_DETAILED_TRAINING_VALIDATION_REFIT_OOS.md): all eight runs, all four roles, every epoch, raw-best versus selected checkpoints, gradients and updates.
- [Detailed extreme-value, actual-objective, numerator/MAD and energy diagnostics](S4_EXTREME_OBJECTIVE_NUMERATOR_MAD_DIAGNOSTICS.md): all roles, original TG20 tails, error-ranked tails, ordinary complements, signs and exact saved witnesses.
- [All-eight numerical/visual summary](S4_VISUAL_AND_SCIENTIFIC_DIAGNOSTICS.md), [all run reports](S4_EIGHT_START_DIAGNOSTIC_INDEX.csv), [complete diagnostic file index](DIAGNOSTIC_FILE_INDEX.csv).
- [S4 dashboard](plots/s4_a_rankings.html): select year → objective → category → ticker/date. Every actual run has its own view and PNG. Full-role panels retain their stated populations; origin filters affect the labeled origin panels.
- [Historical S1/S2 report](HISTORICAL_S1_S2_RANKING_VISUAL_DIAGNOSTICS.md), [complete historical index](HISTORICAL_COMPLETE_DIAGNOSTIC_FILE_INDEX.csv), [historical dashboard](plots/historical_s1_s2_rankings.html). Archived results remain separate. Failed F21 PW and deferred LP were not backfilled.

## 1. Annual and equal-year absolute Rank IC

Average origins within session, sessions within year, then the four years equally. N1 is positive M1; N2 negative M1; P is the training-prefix stock profile. N0 IC is undefined, with tie-aware retrieval/concordance reference values 20%/50%. Optional LR was not included in S4; no new LR/LP/PW fit occurred.

| model | 2021 | 2022 | 2023 | 2024 | equal_year |
| --- | --- | --- | --- | --- | --- |
| N0 | nan | nan | nan | nan | nan |
| N1 | 0.003829874 | 0.002257178 | 0.0103904 | -0.002945501 | 0.003382987 |
| N2 | -0.003829874 | -0.002257178 | -0.0103904 | 0.002945501 | -0.003382987 |
| NR | -0.005321352 | 0.01059864 | 0.009054869 | 0.0009395374 | 0.003817924 |
| P | -0.01887889 | -0.02841185 | 0.05694703 | -0.01267275 | -0.0007541144 |
| T2R | 0.01520458 | 0.01614774 | 0.0041718 | -0.01184016 | 0.00592099 |


Descriptive 95% intervals use 400 whole-calendar-month resamples within each fixed year, seed 22042, then equal-year aggregation. They are not post-search significance tests. Shared stock pairs, overlapping targets and overnight episodes are dependent.

| model | origins | sessions | mean | low | high | top4 | bottom4 | pair_concordance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| N0 | 4013 | 793 | nan | nan | nan | 0.2 | 0.2 | 0.5 |
| N1 | 4013 | 793 | 0.003382987 | -0.005124307 | 0.01220491 | 0.2149129 | 0.2029752 | 0.5012538 |
| N2 | 4013 | 793 | -0.003382987 | -0.01220491 | 0.005124307 | 0.2037678 | 0.2081479 | 0.4987462 |
| NR | 4013 | 793 | 0.003817924 | -0.0108051 | 0.01513654 | 0.2169723 | 0.2050785 | 0.5017273 |
| P | 4013 | 793 | -0.0007541144 | -0.01917039 | 0.01575391 | 0.2358837 | 0.2022706 | 0.4995569 |
| T2R | 4013 | 793 | 0.00592099 | -0.008670409 | 0.01767533 | 0.2301175 | 0.2066976 | 0.5018802 |


Identical-key paired model-minus-control IC differences:

| model | reference | mean | low | high | years | replicates |
| --- | --- | --- | --- | --- | --- | --- |
| NR | N1 | 0.0004349366 | -0.01768958 | 0.01430042 | 4 | 400 |
| NR | N2 | 0.007200911 | -0.00826772 | 0.0193362 | 4 | 400 |
| NR | P | 0.004572038 | -0.02119402 | 0.02654518 | 4 | 400 |
| T2R | N1 | 0.002538003 | -0.01528818 | 0.01697008 | 4 | 400 |
| T2R | N2 | 0.009303977 | -0.008667142 | 0.0234868 | 4 | 400 |
| T2R | P | 0.006675105 | -0.02023075 | 0.03143609 | 4 | 400 |


NR minus M1 is +0.000435 [−0.017690, +0.014300]; T2R minus M1 is +0.002538 [−0.015288, +0.016970]. T2R's higher point estimate does not establish an objective winner. Its 2024 IC is negative (−0.011840). P is positive only in 2023 and has negative equal-year IC, yet its top-four retrieval (23.59%) exceeds both neural estimates. Full-rank association and a single retrieval metric can disagree. Pair concordance remains near 50%.

## 2. Does adding origins help?

NR's all-origin IC (+0.003818) exceeds its old 10:30/11:30 slice (+0.000727); T2R's all-origin IC (+0.005921) is below its old-morning slice (+0.011607). Expansion therefore does not consistently improve the objectives. These slices have different origins and session weights and are not an isolated causal comparison.

Against archived S2 on common morning keys, equal-year S4-minus-archive differences are approximately −0.002331 NR and +0.002877 T2R. Every annual matched interval includes zero. The joins contain 293/364/284/308 origins in 2021–2024, with verified target-return identity. Fitting populations, M2 context pooling and fitted recipes differ; do not attribute results solely to new forecast times. [Exact annual comparisons](S4_MATCHED_BASELINE_AND_ARCHIVE_COMPARISONS.csv).

## 3. Opening, morning, afternoon, intraday and overnight

Each objective has 4,013 OOS origins, 793 sessions and 80,260 stock rows. The two models reuse these source events; they do not double independent evidence.

| model | group | origins | sessions | mean | low | high | top4 | bottom4 | pair_concordance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NR | AFTERNOON | 2262 | 769 | 0.005933602 | -0.01106807 | 0.02130203 | 0.2179075 | 0.1977381 | 0.5025834 |
| NR | INTRADAY | 1740 | 757 | -0.00203433 | -0.01427615 | 0.007575787 | 0.2119275 | 0.2151469 | 0.4995337 |
| NR | OLD_MORNING | 1256 | 742 | 0.0007268679 | -0.01098782 | 0.01232101 | 0.2150072 | 0.2198251 | 0.5002632 |
| NR | OPENING | 495 | 495 | 0.004131775 | -0.01737199 | 0.02533601 | 0.2091085 | 0.2064059 | 0.5016355 |
| NR | OVERNIGHT | 2273 | 771 | 0.005460851 | -0.01159933 | 0.02089219 | 0.2180316 | 0.1979626 | 0.5023884 |
| T2R | AFTERNOON | 2262 | 769 | 0.00334954 | -0.01401046 | 0.01834385 | 0.2295377 | 0.2031826 | 0.5010832 |
| T2R | INTRADAY | 1740 | 757 | 0.006747943 | -0.006323934 | 0.01804541 | 0.2276733 | 0.2116688 | 0.5021369 |
| T2R | OLD_MORNING | 1256 | 742 | 0.01160678 | -0.004084447 | 0.02667181 | 0.2255131 | 0.2179178 | 0.5038272 |
| T2R | OPENING | 495 | 495 | -0.0009401589 | -0.02291817 | 0.01929606 | 0.2335887 | 0.1963006 | 0.4992489 |
| T2R | OVERNIGHT | 2273 | 771 | 0.002770481 | -0.01443795 | 0.01757047 | 0.2298412 | 0.2027142 | 0.500858 |


On 735 sessions supporting both categories:

| model | contrast | sessions | mean | low | high | years | replicates |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NR | OVERNIGHT_MINUS_INTRADAY_SHARED_SESSIONS | 735 | 0.003330843 | -0.01568609 | 0.0193879 | 4 | 400 |
| T2R | OVERNIGHT_MINUS_INTRADAY_SHARED_SESSIONS | 735 | -0.005532275 | -0.02292522 | 0.01100223 | 4 | 400 |


Neither matched contrast establishes a category advantage. Opening-only IC is +0.004132 NR and −0.000940 T2R, with intervals spanning zero. The 495 opening origins are genuinely observed. Overnight count (2,273) differs from afternoon-slot count (2,262) because actual calendar endpoints, including early closes, determine category.

## 4. Stability, churn and outcome association

Within-session adjacent predicted ranks change by an equal-year average of 2.76 NR / 2.44 T2R ranks. Top-four Jaccard overlap averages 0.545/0.597, with 1.36/1.20 names entering per side per transition. Across-session rank changes are 2.61/2.41 and top-four overlaps 0.559/0.597. Missing-slot transitions are separately labeled and show larger changes. [Full table](S4_RANK_STABILITY_AND_SELECTION_CHURN.csv).

Moderate persistence, especially T2R, coexists with weak later-outcome association. Persistence is neither accuracy nor an executed position. All eight PNGs use each year's first ten saved sessions and default AAPL, without selecting favorable outcomes; the dashboard exposes full permitted years and all 20 stocks. Origin metrics retain score margins, ties and dispersion. Every neural OOS origin has defined IC.

## 5. Training and extreme-value findings

| year | model | calibration_epochs | selected_epoch | raw_best_epoch | refit_updates | reload_max_error |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | NR | 14 | 4 | 4 | 560 | 0 |
| 2021 | T2R | 13 | 3 | 3 | 420 | 0 |
| 2022 | NR | 12 | 1 | 1 | 152 | 0 |
| 2022 | T2R | 12 | 2 | 2 | 304 | 0 |
| 2023 | NR | 13 | 3 | 3 | 495 | 0 |
| 2023 | T2R | 38 | 28 | 35 | 4620 | 0 |
| 2024 | NR | 17 | 7 | 7 | 1246 | 0 |
| 2024 | T2R | 23 | 13 | 13 | 2314 | 0 |


F23 T2R selected epoch 28 although its raw-best was epoch 35: the later gain did not clear the frozen absolute 0.001 qualification threshold. Each selected epoch controls a fresh same-seed, reset-optimizer refit. Every final checkpoint reload matched saved predictions exactly. F23 T2R's longer fit still produced OOS IC +0.004172, below M1 +0.010390 and P +0.056947 that year.

The top 1% of realized |TG20| rows contribute approximately 6.6–7.5% of T2R transformed OOS loss but 25.7–36.0% of separate original-Y MSE. NR's same target-tail rows contribute about 2.5–2.7% of ordinal loss. Train-threshold 95% event cohorts contribute about 20–27% of transformed T2R loss and 10–14% of NR loss. These are within-objective shares; NR and T2R loss units must not be compared directly.

NUM_ONLY contributes more transformed loss than MAD_ONLY in all four T2R OOS folds; BOTH is sparse. This does not authorize target changes or dismissal of denominator effects. Original-Y forecast energy is only about 0.03–0.52% of target energy across T2R folds. Exact loss/error complements, positive/negative tails, floor membership, numerator/MAD partitions, and common/centered/cross terms are retained in the detailed report and CSVs. Repeated model views are not independent extreme events.

## 6. Source-clock decision: seven candidate origins

S4 includes 09:30, 10:30, 11:30, 12:30, 13:30, 14:30 and 15:30. The pinned documentation uses interval-start minute labels. A genuine 09:30 minute OPEN is the opening price reference; its 09:30–09:31 bar completes before assumed 09:32 issuance. Actual publication latency and auction identity remain unverified. Missing prices and unverified latency are distinct findings.

Opening inputs use the previous 48 completed hourly steps and causal FT16 indicators, never the unfinished 09:30–10:30 bar. The normal opening target ends at exactly 13:30 using the genuine 13:29 minute close. No fabricated price, shifted endpoint or new channel was used. [All-20 opening audit](opening_reaudit_v2/S4_0930_REAUDIT.md), [clock/eligibility audit](S4_CLOCK_AND_ELIGIBILITY_AUDIT.md), [all role/slot counts](opening_reaudit_v2/S4_FOLD_ROLE_SLOT_COUNTS.csv).

The horizon counts 240 actual regular-session minutes, including the final 30-minute stub. Normal exits are 13:30/14:30/15:30 same day, then 10:00/11:00/12:00/13:00 next session. Calendar tests cover early closes, DST, weekends and holidays. Genuine entry/exit prices are mandatory. Missing intermediate close disables only decomposition. Of 45,460 overnight OOS stock rows, 44,861 support the three-leg decomposition and 599 remain unsupported; supported sums reconcile to direct returns. These are price-only observations, not certified fills.

Nominal OOS retention is about 51–67% by fold: seven candidate slots do not imply seven valid daily observations. The fixed 20 names, 48-step source quality/maturity/embargo rules, train-only recipes and unchanged 50-session validation minimum remain enforced. Quality/fallback cases stay in their documented strata. Fixed-survivor selection, action-vintage and bounded private-use/publication qualifications remain unresolved research limitations.

## 7. Verification and stopping decision

Proposal SHA256: `971765111037fb649a7c5319e4a260223301a9bc8a80ce8621fe29e7061349f0`.
Execution SHA256: `a737c9219513ddbbfffb882a2e76af7708e2f3ee55a297e1b145790bc47f2a95`.

The approved executor remained unchanged. `scripts/summarize_hf20_s4.py` aggregates saved allowed-period outputs and verifies annual IC/partition identities; it performs no fitting, checkpoint replay or raw-source reads. [Final live verification](S4_LIVE_FINAL_VERIFICATION.json) records browser/static/source/ledger/resource checks. Earlier preflight NOT_RUN files remain historical; the live record supplies current completion status.

**TECHNICALLY_COMPLETE / EXPLORATORY_NO_RELIABLE_INCREMENTAL_EDGE_ESTABLISHED.** Stop here. No S4-B, additional seeds, architecture, backtest or confirmation access follows from these results. Protected 2026 files were neither opened nor hashed; no 2025 tuning occurred. No Git publication occurred. Checkpoints, scores, exact witnesses and HTML remain private local artifacts.
