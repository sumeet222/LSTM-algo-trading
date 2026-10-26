# Proposed one-time live-fit approval — HF20 S1 + S2

**AWAITING APPROVAL. No real fits/new starts. Ledger62/200.**

Proposal [proposal.json](proposal.json), SHA256 **7d47e5e893e2450b63d348f9c539df7c6ac2790b07b0d94ecaaee02acbe9b04a**. Execution five-module bundle SHA256 **9185edba7e01e2fa6d7ea0d519fdfa60fc818fdc548215cc1c986439403b3660**. Exact code hashes,3994 source/config/test/fold/preflight preservation references and all settings are bound by the proposal. P020 contract SHA256 `7adfec916b7eb74fead83ef1fe6082ff0fcee9ff0b6ebae5722077e2a82c01a5`. Required design record matches `f676ca3c0690a06e66a47a6769f82d1e94d5d755e550387ed226db36892883d1`.

**Requested scope:** eight same-P020-formula train-prefix preprocessing recipes, exactly64 separately logged S1 fits (P8, LR28, LP28; six inner λ values plus fresh refits), fixed N0/N1/N2 controls, then exactly12 neural seed42 calibration/fresh-refit lifecycles below. S1-only approval is possible and stops before neural starts. No reservations before a matching live response.

| Fold | Inner fit through | Selection starts (nominal) | Refit through | Inner / validation origins | Refit / OOS origins | OOS sessions |
|---|---|---|---|---|---|---|
| F21 | 2020-06-30 | 2020-07-01 | 2020-12-31 | 3510 / 197 | 3720 / 293 | 177 |
| F22 | 2021-06-30 | 2021-07-01 | 2021-12-31 | 3890 / 137 | 4027 / 364 | 203 |
| F23 | 2022-06-30 | 2022-07-01 | 2022-12-30 | 4245 / 143 | 4403 / 284 | 172 |
| F24 | 2023-06-30 | 2023-07-03 | 2023-12-29 | 4578 / 111 | 4701 / 308 | 185 |

Neural order and maximum charged starts:

63. `HF20-S1S2-F21-T2R-S42`
64. `HF20-S1S2-F21-NR-S42`
65. `HF20-S1S2-F21-PW-S42`
66. `HF20-S1S2-F22-T2R-S42`
67. `HF20-S1S2-F22-NR-S42`
68. `HF20-S1S2-F22-PW-S42`
69. `HF20-S1S2-F23-T2R-S42`
70. `HF20-S1S2-F23-NR-S42`
71. `HF20-S1S2-F23-PW-S42`
72. `HF20-S1S2-F24-T2R-S42`
73. `HF20-S1S2-F24-NR-S42`
74. `HF20-S1S2-F24-PW-S42`

LR/LP: all768 existing inputs, weighted-mean objective+λ||w||², λ=(.0001,.001,.01,.1,1,10), highest inner dailyIC, exact tie largerλ. LP matrix-free float64 L-BFGS100iterations/125closures; required final max-gradient≤1e-5. No hidden model grid.

All neural arms: existing one-layer hidden32 SharedLSTM6433 parameters, final-hidden dropout.1/recurrent dropout0; AdamW .001, betas(.9,.999), eps1e-8, weight-matrix decay.01/bias0; clip1,16 whole sessions, CPUfloat32, seed42, threads4/1. T2R asinh-MSE, NR bounded normalized-rank MSE, PW pure untied-pair logistic τ1. Same rank-led selector: strict absolute improvement>.001, min12 observed/max60/patience10, raw maximum separate; fresh seed42 refit selected epochs. Old future-trained T2 remains contextual only.

**Gates/evidence:** [readiness](REHEARSAL_AND_READINESS.md):33 tests;444-file static0 errors/warnings; zero real-data optimizer steps/starts. Source returns reconstructed for137,200 rows; bounded real sampler bit-exact; all four inner supports adequate; source feasibility does not force constant IC. Require99% defined OOS IC except N0; constants undefined. S1 must pass technical reconciliation before S2; each completed neural four-role independent scientific/hash gate before next start. Weak finite performance passes. True error stops; no retry or replacement. Failed starts permanently count. Neural maximum **74/200**, no refund or extra fit.

**Resources:** planning2–8h (unbenchmarked estimate), CPU4/1, RSS≤2GB, cumulative task additions≤1GB, project≤10GB; no dependency installation/download. At most211,860 neural optimizer steps and3500 LP closure evaluations plus28 final gradient checks. No abandoned-fit restart within this approval.

**Diagnostics/closeout:** exact keyed four-role scores; annual/month/slot/stock/static-sector-proxy/quality/fallback tables; matched IC/concordance/rank errors/retrieval/ties; original target1%/5% and prior-fit95%/99% events, complements, NUM/MAD partitions, true-objective conservation/pair types/gaps, original TG20 MSE only for T2R, same22 genuine source cases per neural family; complete training/selection/refit traces; independent stored-output checks; one offline annual figure and seven readable reports indexed by README. No new dashboard framework.

**Qualifications retained:** historical target starts2 minutes before modeled issuance; price-only ordering, no executable/P&L claim. Publication, corporate-action vintage, historical cohort/PIT and underlying licensing remain qualified under existing bounded private-use attestation. No2025 selection or2026 numerical access; no other seeds/architectures/losses/features/folds, trading or Git publication. See [preflight/reconciliation](PREFLIGHT_AND_DESIGN_RECONCILIATION.md).

The submitted brief's “Authorization checkpoint” explicitly requires a new live response; the six directional defaults do not authorize fitting. Approve the exact proposal/execution hashes,64 baseline fits and12 listed neural starts (or explicitly S1-only), or hold. Any material scientific/code/resource change or true failure requires new review. No routine per-fold approval is planned once this combined scope is approved.
