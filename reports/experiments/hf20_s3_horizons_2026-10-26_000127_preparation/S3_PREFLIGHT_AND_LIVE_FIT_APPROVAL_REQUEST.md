# S3 amended eligibility design — human review required

**Source-support gates PASS. Await amended eligibility design approval; no live fitting authority.** Your latest instruction explicitly says “Await explicit approval of the amended eligibility design.” This card requests that scientific design decision only. Real supervised fitting/optimizer updates, target/M2 parameter fitting, candidate checkpoints and ledger reservations remain unapproved. The original future32-start campaign is listed for transparency, not activated.

Sealed proposed card: [S3_FROZEN_EXPERIMENT_CARD.json](S3_FROZEN_EXPERIMENT_CARD.json), SHA256 **bf12ae80cdd5a7c4418ffb7735e80eb93b7e720a90ba942518195839b2a266c3**. Canonical amended evidence is in eligibility_amendment_v2/. Initial mandatory-intersection audit and its42-session F24 failure remain preserved at root; this live amendment supersedes that fitting-population proposal.

## Eligibility and support

Independent h1/h2/h4 endpoint and price-basis validity is intersected only with the same original FT16 input/quality mask and frozen role clock. Missing4h future prices never exclude otherwise valid h1/h2 observations. The original canonical two morning schedule, source,20 stock order,48×16 channels, phase recipes, calendar cutoffs,48-step input embargo and conservative4h maturity cutoff stay unchanged. No new early-close/afternoon/overnight origins. Future availability is a supervision-validity flag, never an input.

Counts below are eligible origins / distinct sessions, **not fitted models**. A and B have exactly the same masks/stock rows within h/year/role; B h4 is an identity control with no fit.

| year | horizon | inner_fit | validation | refit | OOS |
| --- | --- | --- | --- | --- | --- |
| 2021 | 1 | 3332 / 1830 | 191 / 104 | 3535 / 1942 | 270 / 156 |
| 2021 | 2 | 3183 / 1898 | 191 / 113 | 3386 / 2019 | 257 / 164 |
| 2021 | 4 | 3510 / 1982 | 197 / 115 | 3720 / 2105 | 293 / 177 |
| 2022 | 1 | 3699 / 2033 | 120 / 73 | 3819 / 2106 | 346 / 189 |
| 2022 | 2 | 3540 / 2113 | 117 / 78 | 3657 / 2191 | 330 / 194 |
| 2022 | 4 | 3890 / 2202 | 137 / 87 | 4027 / 2289 | 364 / 203 |
| 2023 | 1 | 4024 / 2217 | 137 / 76 | 4174 / 2300 | 274 / 159 |
| 2023 | 2 | 3854 / 2309 | 130 / 75 | 3996 / 2392 | 241 / 156 |
| 2023 | 4 | 4245 / 2411 | 143 / 80 | 4403 / 2499 | 284 / 172 |
| 2024 | 1 | 4343 / 2393 | 107 / 66 | 4463 / 2467 | 299 / 168 |
| 2024 | 2 | 4151 / 2486 | 93 / 64 | 4252 / 2556 | 281 / 181 |
| 2024 | 4 | 4578 / 2598 | 111 / 74 | 4701 / 2679 | 308 / 185 |


All12 horizon×year inner-validation sets meet≥50 sessions; both origin types meet≥25 origins (36 total gate checks). F24 now has h1 **107 origins/66 sessions**, h2 **93/64**, h4 **111/74**. Their slot counts are57/50,49/44,50/61 respectively. No threshold lowered. F24 h1 includes22 and h2 includes17 validation origins absent from original h4; full-prefix refit includes337/297 additional distinct keys beyond h4, while losing other unavailable short endpoints. New populations therefore are neither simple supersets nor subsets of original h4.

The three-horizon intersection is **secondary matched evaluation**, not a fit/selection restriction. Its F24 validation remains61 origins/42 sessions, which is acceptable only as a descriptive subset, never the epoch/penalty selector or a waiver of the50-session primary gate. H-specific models retain their own legitimate fitting sets; a common evaluation set does not make those estimation sets identical. Primary cross-horizon differences include natural population differences. No causal horizon-only training-data effect is claimed.

## Fixed scientific proposal and budgets

S3-A: unchanged original-M2 FT16, h1/h2 P/LR/N0/N1/N2/T2R/NR; h4 archived source/recipes/models/predictions are reused. Up to72 non-neural attempts (9 per newh/fold), and16 neural lifecycles. S3-B: only M2's historical return horizon becomes1h/2h, both T2R/NR for each year,16 more neural lifecycles. [Exact proposed neural IDs](S3_PROPOSED_NEURAL_TASKS.csv), [baseline jobs](S3_PROPOSED_BASELINE_TASKS.csv). None reserved/started. Future maximum74→106 only if separately authorized and all32 actually start. No retries/refunds, other seeds/windows/horizons/architectures, PW or LP.

One hidden32 layer,6433 parameters,48×16, seed42, final dropout.10/recurrent dropout0. AdamW.001, betas.9/.999, eps1e-8, matrix decay.01/bias0, clip1,16 complete sessions; CPU4 intra/1 inter/0 workers. Original IC selector: strict+.001, min12 observed/max60/patience10, raw/qualified best separately, fresh same-seed selected-count refit. Weak/negative IC never suppresses B. NR uses true normalized-rank MSE; T2R float32 asinh-MSE and once-inverted diagnostic Y only. Equal stocks/origins/sessions; equal4 annual IC means. Target transforms share one h/fold/phase recipe across A/B; new h1/h2 parameters remain unfitted. Exact rules and masks are in JSON; no recent-only scaler or rolling LSTM.

M2 inspection matches the live contract: previous **regular-day** same-origin returns; fixed20/60 scheduled regular-session windows,19/20 and57/60 valid counts, max2 consecutive missing; RMS, not centered SD. No compressed valid-day history and no today's future outcome. Forecast10:30/11:30 chooses context0/1 consistently throughout its48 historical steps. Previous regular15:30+2min reference precedes each historical step's start. h4 native mean/RMS/reference match exactly and scaled M2 is bitwise equal under all8 stored phase recipes. For h1/h2, only M2's floor/robust scale/fallback may be fitted later on original input-only unique prefix day keys, contexts50:50. Other15 channels remain bitwise unchanged. There is no B-native-availability row filter; legitimate fitted fallback preserves A/B matching.

## Verification, resources and remaining qualifications

Source audit and independent verifier reconstruct all48 memberships,16 exact original h4 index sets,48 exclusion partitions and hierarchical weight sums. B/A key hashes match. Actual endpoint arithmetic, calendar/DST/early closes/weekend gaps and22 source stock-events (20 distinct origins/13 sessions) are recorded.32 proposed configurations passed disposable SYN shape/gradient/memory-reload/fresh-state checks with zero optimizer calls in those rehearsal processes. Old accepted weights were not replayed or changed. Real h1/h2 forecasts/accuracy and B−A effects are NOT_RUN.

Source-vintage/rights remain QUALIFIED: actual vendor available_at unknown, retrospective action units/fixed survivors/private use; target starts2min before modeled issuance. No investability or trading claim. Protected2026 numerical data and2025 tuning remain closed. All5847 preserved byte references unchanged; live registry remainsv20/74, including failed65 and deferred LP.

Amended audit99.22s/880,115,712bytes peak RSS; native-coverage audit4.28s/773,718,016bytes. Future fit planning≈1–6h,≈.65–.85GB additions based on old observed artifacts, not a guarantee; stricter existing limits2GB RSS/1GB additions/10GB total retained. Current project logical bytes≈7.35GB. No network/install/secrets/Git publication.

**Verification scope exception:** an early inherited test command ran42 AdamW.step invocations and one LBFGS.step invocation on disposable synthetic fixtures only. This violated the literal zero-update instruction for tests. No empirical model/checkpoint/ledger changed; internal LBFGS iterations were not retained. [Disclosure](eligibility_amendment_v2/LEGACY_TEST_SCOPE_EXCEPTION.json). Final guarded tests exclude those optimizer-using fixtures and make AdamW/LBFGS.step raise; that final run has0 calls. Do not read the separately guarded source/rehearsal receipt's0 count as a session-wide synthetic-update claim.

Approval sought now: accept this amended eligibility design. Any later live-fit activation requires its exact executable/authority gates and explicit fit response; this design review grants none.
