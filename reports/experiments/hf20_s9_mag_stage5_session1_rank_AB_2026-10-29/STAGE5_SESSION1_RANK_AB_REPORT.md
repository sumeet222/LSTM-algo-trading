# Stage 5 Session 1: absolute-magnitude ranking

## Executive decision

Both authorized experiments are **COMPLETE / TECHNICAL_PASS**, four annual folds each, with the full-history ridge control also complete. Neither establishes incremental ranking quality over the frozen CLOCK-C3/S2-C magnitude LSTMs. Keep those references; preserve both rank-only results as exploratory evidence. No model promotion or follow-on fitting is authorized.

| Experiment | Scientific verdict | Main evidence |
| --- | --- | --- |
| S5-A normalized-rank MSE | NO_INCREMENTAL_RANKING_EVIDENCE | IC lower in all four years; lower concordance and top-four retrieval; also trails ridge IC |
| S5-B pure RankNet, tau=1 | MIXED / NO_INCREMENTAL_RANKING_EVIDENCE | Near-tied with CLOCK-C3, below S2-C; two annual gains/two losses; beats ridge but no strong-reference gain |

Ledger **174 → 182 / 300**, exactly eight starts/pairs and sixteen phases, no retries. All 80,260 stock-origin rows / 4,013 origins / 793 sessions preserved per arm. No magnitude decoder, calibration, raw-A MSE/MAE, or trading interpretation exists for the dimensionless new scores.

## Primary and common ranking evidence

IC uses within-origin average ranks of scores and genuine absolute four-trading-hour returns, then equal origins within session, equal sessions within year, equal four years. Higher IC/concordance/retrieval is better. Constant-score IC contributes zero; historical omit-undefined IC is also saved. All fitted new arms have zero constant/tied-score rates; constant control has IC zero, concordance 0.5, top/bottom retrieval 0.2. Frozen magnitude scores are used only as ordering scores.

| year | C0 | CLOCK-C3 | LINEAR | S2C-C3 | S5A | S5B |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | 0.31785841 | 0.32627607 | 0.32476782 | 0.32746071 | 0.31832188 | 0.32899138 |
| 2022 | 0.35029686 | 0.35445091 | 0.32974904 | 0.3517645 | 0.31219076 | 0.34610461 |
| 2023 | 0.32024473 | 0.32380415 | 0.31266667 | 0.32630073 | 0.30363185 | 0.32346909 |
| 2024 | 0.3102724 | 0.31648505 | 0.30558808 | 0.31941796 | 0.30370308 | 0.31962411 |
| EQ | 0.3246681 | 0.33025404 | 0.3181929 | 0.33123598 | 0.30946189 | 0.3295473 |

Equal-year common metrics:

| arm | IC | pair_concordance | top4 | bottom4 | tie_rate | constant_rate |
| --- | --- | --- | --- | --- | --- | --- |
| C0 | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| M1 | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| B0-VOL | 0.30414316 | 0.6094227 | 0.40988649 | 0.29618868 | 0.00026150811 | 0 |
| B0-CLOCK | 0.3028002 | 0.60852865 | 0.38668138 | 0.30584502 | 0 | 0 |
| B0-RMEAN | 0.30023827 | 0.60754095 | 0.39069215 | 0.30584502 | 0 | 0 |
| C3 | 0.3246681 | 0.61730212 | 0.42460956 | 0.29915518 | 0 | 0 |
| CLOCK-C3 | 0.33025404 | 0.61944331 | 0.42946585 | 0.30302756 | 0 | 0 |
| S2C-C3 | 0.33123598 | 0.61981899 | 0.42964073 | 0.30288517 | 0 | 0 |
| CONSTANT0 | 0 | 0.5 | 0.2 | 0.2 | 1 | 1 |
| LINEAR | 0.3181929 | 0.61474379 | 0.41498423 | 0.29945096 | 0 | 0 |
| S5A | 0.30946189 | 0.61128801 | 0.41046308 | 0.2980071 | 0 | 0 |
| S5B | 0.3295473 | 0.61947882 | 0.42685327 | 0.30338846 | 0 | 0 |

Paired equal-year differences (new minus reference; positive favors new), 400 whole-calendar-month draws, seed 22042:

| arm | reference | metric | delta | low | high |
| --- | --- | --- | --- | --- | --- |
| S5A | CLOCK-C3 | IC | -0.020792151 | -0.027675591 | -0.015672549 |
| S5A | CLOCK-C3 | pair_concordance | -0.0081552991 | -0.010925193 | -0.0061445239 |
| S5A | CLOCK-C3 | top4 | -0.019002774 | -0.027187189 | -0.011037572 |
| S5A | S2C-C3 | IC | -0.021774084 | -0.02899568 | -0.016338655 |
| S5A | S2C-C3 | pair_concordance | -0.0085309762 | -0.011277645 | -0.0065479952 |
| S5A | S2C-C3 | top4 | -0.019177646 | -0.027691354 | -0.011155142 |
| S5A | LINEAR | IC | -0.0087310115 | -0.014025932 | -0.0036250859 |
| S5A | LINEAR | pair_concordance | -0.0034557778 | -0.0055317793 | -0.001478064 |
| S5A | LINEAR | top4 | -0.0045211469 | -0.014731267 | 0.0047277774 |
| S5B | CLOCK-C3 | IC | -0.00070674535 | -0.0028790189 | 0.0013950382 |
| S5B | CLOCK-C3 | pair_concordance | 3.5508827e-05 | -0.00085890697 | 0.0008888138 |
| S5B | CLOCK-C3 | top4 | -0.0026125885 | -0.0064597897 | 0.0014086747 |
| S5B | S2C-C3 | IC | -0.0016886789 | -0.0039227812 | 0.00040809149 |
| S5B | S2C-C3 | pair_concordance | -0.00034016826 | -0.0012482675 | 0.00053798476 |
| S5B | S2C-C3 | top4 | -0.0027874612 | -0.0071064501 | 0.001105396 |
| S5B | LINEAR | IC | 0.011354394 | 0.0073164887 | 0.016669342 |
| S5B | LINEAR | pair_concordance | 0.0047350301 | 0.0030603815 | 0.0068612954 |
| S5B | LINEAR | top4 | 0.011869038 | 0.0051161609 | 0.018922136 |

Annual IC differences versus CLOCK-C3 are −0.007954/−0.042260/−0.020172/−0.012782 for S5-A and +0.002715/−0.008346/−0.000335/+0.003139 for S5-B (2021–2024). All S5-A annual descriptive IC intervals lie below zero; S5-B's 2022 interval is [−0.012988, −0.004292], with the other three spanning zero. Full annual/category intervals are in paired_ranking.csv. No interval adjusts for prior research search, surrogate epoch selection, or ridge selection; overlapping origins/stocks stay together in calendar-month clusters. Four folds are not independent seeds or untouched confirmation.

## Conditional, tail and stock-prior diagnostics

| arm | scope | IC | pair_concordance | top4 |
| --- | --- | --- | --- | --- |
| CLOCK-C3 | INTRADAY | 0.31804631 | 0.61505755 | 0.42717511 |
| CLOCK-C3 | OVERNIGHT | 0.34099113 | 0.62331562 | 0.43118663 |
| S2C-C3 | INTRADAY | 0.31811022 | 0.61516697 | 0.42610967 |
| S2C-C3 | OVERNIGHT | 0.34240804 | 0.62392834 | 0.43140148 |
| S5A | INTRADAY | 0.29412877 | 0.60552913 | 0.40740243 |
| S5A | OVERNIGHT | 0.32276361 | 0.61637695 | 0.41379947 |
| S5B | INTRADAY | 0.31639171 | 0.61479113 | 0.42313108 |
| S5B | OVERNIGHT | 0.34063691 | 0.62351124 | 0.43079602 |

Equal-year clock-slot IC (actual saved early-close categories remain authoritative):

| group | CLOCK-C3 | S5A | S5B |
| --- | --- | --- | --- |
| 09:30 | 0.3050349 | 0.28768291 | 0.30608694 |
| 10:30 | 0.33257734 | 0.30643252 | 0.33163268 |
| 11:30 | 0.32425718 | 0.29618981 | 0.32156296 |
| 12:30 | 0.33797545 | 0.32869001 | 0.33903669 |
| 13:30 | 0.34212942 | 0.32279561 | 0.33954459 |
| 14:30 | 0.33896565 | 0.31746689 | 0.34074901 |
| 15:30 | 0.33666945 | 0.31044593 | 0.33594006 |

S5-A loses IC at all seven slots. S5-B has small mixed slot differences, including a 15:30 deficit; no slot was used to select a model. Only 14 early-close origins are present (4/3/3/4 annually), so their IC and retrieval are fragile descriptive diagnostics; see groups.csv. Month-specific and stock-specific diagnostics are retained in groups.csv and stock_diagnostics.csv, not used for retuning.

Prefix-defined tail event retrieval (weighted annual ratios, then equal years):

| arm | level | weight_mass | top4_event_recall | false_low_rank |
| --- | --- | --- | --- | --- |
| CLOCK-C3 | 95 | 0.059318601 | 0.55306374 | 0.16900817 |
| CLOCK-C3 | 99 | 0.009373201 | 0.67565952 | 0.12669868 |
| S2C-C3 | 95 | 0.059318601 | 0.55348591 | 0.16429971 |
| S2C-C3 | 99 | 0.009373201 | 0.66686869 | 0.12770865 |
| LINEAR | 95 | 0.059318601 | 0.52632789 | 0.18689478 |
| LINEAR | 99 | 0.009373201 | 0.62081539 | 0.13550545 |
| S5A | 95 | 0.059318601 | 0.52399515 | 0.18820462 |
| S5A | 99 | 0.009373201 | 0.6276729 | 0.1594615 |
| S5B | 95 | 0.059318601 | 0.54812526 | 0.1784641 |
| S5B | 99 | 0.009373201 | 0.67100064 | 0.1361716 |

The prefix95 cohort has equal-year mass 5.9319%, prefix99 0.9373%; both models have lower tail top-four recall and more false-low ranks than CLOCK-C3. Here false-low means forecast average rank <=10.5, as in the saved diagnostic. These are retrospective outcome-selected cohorts, not probabilities or a fitted event head. Complements are included in tail_retrieval.csv; no magnitude loss is computed for rank-only scores. In that CSV the EQ stock_rows column is the arithmetic mean annual count, not a pooled integer count.

Cross-sectional centered-score variance has a substantial static-stock component: equal-year static fractions are 76.59% S5-A, 81.77% S5-B, 81.06% ridge, 77.15% CLOCK-C3, 77.47% S2-C, and 100% saved B0-RMEAN. These are descriptive decompositions using OOS scores, not newly fitted forecasts. S5-B is dynamic and beats the frozen static stock prior (IC 0.300238), but much of its score variation still reflects persistent stock risk ordering. Arbitrary score scales prevent comparing variance levels across models as predictive quality.

Normalized predicted-rank discrepancy is secondary: constant midranks have discrepancy about 0.3684 versus about 0.49 for nonconstant predictions because ties shrink rank spread. This does not make the constant predictor a better ranker; its IC is zero and retrieval is chance. No tie jitter or favorable alphabetical boundary rule was used. Fourteen exact realized pairs are tied across OOS and excluded from concordance/pair loss; predicted ties receive half credit and top/bottom-four boundary ties fractional membership.

## Frozen scientific and engineering contract

The target is the within-origin ordering of A=abs(log(genuine four-trading-hour endpoint/origin price)), not signed return, stock-normalized volatility or the distinct S2-D gap. S5-A uses ascending average ranks q=2*(r−1)/19−1 and unconstrained scalar squared error. S5-B uses each unequal unordered pair once, softplus(−sign(A_i−A_j)*(z_i−z_j)), tau=1; no distance/tail weighting. Pair means are normalized inside each origin before equal-origin/session reduction. No all-tied origin occurred in any legal role (minimum 184 valid pairs in a training origin).

Both models retain exact original 48×16 FT16, shared own-stock H32 single-layer recurrent encoder, final dropout .10, ten schedule-only CLOCK fields and scalar head: 6,443 parameters. No minute inputs, stock ID, peer exchange, additional head, score centering, tanh, loss mixture or new normalizer. Clock readout terms are common to stocks at one origin and therefore cancel from pure pairwise loss/ranking; their architecture was retained exactly and ordinary weight decay still applies. Coupled pair gradients do not mean the forward model receives peer features.

Input-only phase floors/scalers are reproduced exactly against all eight saved initial/September recipes. Role indices bind to the saved O1 archive and exact Design A masks, original 48-step first-input embargo, endpoint+2-minute maturity and actual calendar categories. Initial cutoffs are June2020/April2021/May2022/May2023, selectors July2020/May2021/June2022/June2023 through September; restricted refits stop at saved September cutoffs. October–December is reserved and unused for fitting, model inference and calibration. Annual rows are 19,100/23,600/17,740/19,820; all twenty tickers remain in their executed order. See role_counts.csv, phase_recipes.csv and clock_dictionary.csv for exact bindings/counts.

CPU float32, seed42, AdamW lr .001/betas(.9,.999)/eps1e−8, matrix decay .01/bias decay0, clipping1, sixteen complete-session minibatches, shuffle42+epoch. Selector uses its own positive surrogate loss, first finite nonnegative then <=.999 incumbent qualified-best, minimum12/patience10/maximum60. IC is diagnostic only. Each refit is freshly initialized with an empty optimizer and exactly the selected epoch count. No candidate was chosen from OOS. Selected epochs may precede epoch12 or differ from the raw minimum:

| arm | year | alpha | selected_epoch | selector_epochs | raw_minimum_epoch | seconds |
| --- | --- | --- | --- | --- | --- | --- |
| LINEAR | 2021 | 100 | N/A | N/A | N/A | N/A |
| S5A | 2021 | N/A | 4 | 14 | 4 | 238.30007 |
| S5B | 2021 | N/A | 3 | 13 | 8 | 215.67016 |
| LINEAR | 2022 | 0.01 | N/A | N/A | N/A | N/A |
| S5A | 2022 | N/A | 2 | 12 | 9 | 177.4977 |
| S5B | 2022 | N/A | 3 | 13 | 3 | 235.07434 |
| LINEAR | 2023 | 100 | N/A | N/A | N/A | N/A |
| S5A | 2023 | N/A | 5 | 15 | 5 | 273.39923 |
| S5B | 2023 | N/A | 5 | 15 | 5 | 330.26255 |
| LINEAR | 2024 | 1 | N/A | N/A | N/A | N/A |
| S5A | 2024 | N/A | 9 | 19 | 9 | 441.99823 |
| S5B | 2024 | N/A | 9 | 19 | 14 | 478.51557 |

The same-information linear control uses intercept + all 768 flattened hourly features + ten clocks (779 coefficients, no stock ID), causal phase normalizers and identical row/session weights. Streaming float64 sufficient moments avoid a full flattened cache. Objective is normalized weighted q-MSE + alpha*sum(nonintercept coefficients squared); alpha in {.01,1,100}, selector q-MSE, exact ties prefer larger alpha. Selected alpha is 100/.01/100/1; fresh September refits use that alpha. It is not a same-capacity control. No pairwise linear model was fitted (explicit baseline limitation). B0-RMEAN is the saved causal static stock-magnitude prior; the zero constant is an analytic chance control, not random ranking.

S5-A own q-MSE is 0.339025 (ridge 0.341612), decomposing into offset-squared 0.007536 + centered error 0.331489. Lower q-MSE did not mean higher IC. S5-B own logistic loss is 0.650629; its common offset is unidentified by pair differences. The two objective levels cannot select a winner against each other. No raw magnitude amplitude/calibration claims follow from either output.

## Verification, preservation and reproduction

All-fold preflight and mathematical fixtures passed before any start. Focused tests cover midranks/exact ties/permutations/rescaling, once-only pairs/offset invariance/coupled finite gradients, unequal-origin session weighting and batching, original clock/parameter/optimizer/selector parity, ridge sufficient moments, fractional retrieval, conservative constant IC and original reducer parity. Twelve tests passed; Ruff passed; installed Pylance basic full project check analyzed 525 files with zero errors and zero warnings. Editor Problems refresh remains human-confirmed and outstanding; no severity/exclusion/ignore workaround was used.

verification.json confirms exact keys/labels/stock order, all model completion records, qualified epoch replay/refit counts, checkpoint hashes and zero save/load prediction error. Frozen protocol/readiness/code/test hashes and bound predecessor assets are unchanged; current registry alone is an authorized schema33→34 successor with fit_permission=false, linking the previous immutable journal. Preservation is based on exact authorized bound files, not a forbidden broad scan/hash of protected data. No source or earlier checkpoint/result/dashboard was rewritten.

Observed preflight peak RSS 1,015,922,688 bytes and final training-process peak 923,631,616 bytes are below 2GB. Sum of eight neural pair runtimes is approximately 2,390.72 seconds (ridge/preflight/reporting excluded). Final training receipt reports project 12,829,425,664 bytes and task 4,981,788 bytes; final reporting footprint is recorded separately in final_integrity.json. Caps remain 15GB project /2.5GB task. No large new source/feature cache or pair expansion was created.

Only existing receipt-bound 174 adjusted-hourly partitions and saved genuine target/role artifacts through 2024 were used. No raw minute opens, 2025 market values, protected2026 paths/values/hashes, network or downloads. Calendar-only boundary metadata is distinct from market observations. Historical approximate origin+2-minute publication is a proxy, not independently observed vendor latency; retrospective action adjustments and fixed-survivor bias remain. The original nominal-origin price target is not executable post-issuance return, options profit, signed alpha or validated strategy.

Commands, source identifiers, initial dirty Git state, known prefit corrections and report-only reproduction are in SESSION_HANDOFF.md and the mandatory Codex session report. Large checkpoints/Parquets are intentionally ignored; small code/config/receipts require human Git review. No commit/push/fetch or dependency changes occurred.

## Researcher stop

Retain CLOCK-C3/S2-C as ranking references and magnitude products. S5-A is negative incremental evidence; S5-B is near-tied, with an advantage over weaker linear/static controls but no stronger-reference improvement. Do not promote a subgroup win, lower surrogate loss, or tiny concordance difference. STOP: no S5-C/D/E, tau/seed/feature tuning, new calibrator, trading, 2025 exploration or protected release. Further work requires a new researcher decision.
