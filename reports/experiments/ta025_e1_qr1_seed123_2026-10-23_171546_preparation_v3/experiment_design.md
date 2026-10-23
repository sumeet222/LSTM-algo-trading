# P025 frozen E1/QR1 seed-123 preparation

Current phase: Stage 0/1 only. Separate live approval is required before either neural start. The final review card will bind the measured zero-step receipt and proposal hashes. Ledger remains **51/200**. Failed P024 start46 and all earlier results remain preserved.

## Exact proposed runs

1. `HF1M-LONG-TM0-E1-S123-DEV1`: exact E1 replication, signed class-weighted classification.
2. `HF1M-LONG-TM0-QR1-S123-DEV1`: exact QR1 replication, three ordered conditional quantiles.

If approved and started, charge52 then53. Each start covers D6g inner calibration and a fresh selected-epoch refit. Failure consumes its start permanently and stops subsequent execution. No retry, extra seed, combination or new T2 fit is proposed. QR1 requires the complete E1 immediate gate for this proposal, including full-role numerical checks, matched baseline diagnostics and exact cases.

## Frozen scientific definitions

The sole source is `mito0o852/OHLCV-1m` at revision `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`, using the released action/QA, FT16 and TG20 contracts. Input SHA256 is `7adfec916b7eb74fead83ef1fe6082ff0fcee9ff0b6ebae5722077e2a82c01a5`. The existing 20-stock order, 48 completed hourly steps, 16 channels, masks, chronology, training-only fallbacks/scalers/epsilon and inner/refit asinh scales are unchanged. January–March2026 is protected; preservation checks hash its bytes only.

Each model has one 16→32 LSTM layer, head dropout0.1, recurrent dropout0, three outputs and6,499 parameters. AdamW uses learning rate0.001, betas(0.9,0.999), epsilon1e-8, matrix decay0.01 and bias decay0; global gradient cap1.0; batches contain16 complete sessions. Seed123 controls initialization, dropout and the existing whole-session permutation algorithm.

E1 delegates the original Package022 tensor loss and saved fitting recipes: strict original-TG20 tails below−q95 or above+q95, equalityNORMAL; class weights capped at4; normalization across the full session before averaging sessions. QR1 delegates Package023 outputs/loss: median=raw0, lower=raw0−softplus(raw1), upper=raw0+softplus(raw2); mean pinball at(0.05,0.50,0.95) in transformed z. TG20 quantiles use the prefix scale times sinh exactly once.

The original selector is **inclusive**: validation loss≤0.999×qualifying best, minimum12 epochs, maximum60, patience10. E1 selects its original weightedCE; QR1 selects its original pinball. Development never selects epochs. Fresh refit resets the seed and optimizer and runs the selected epoch count.

## Fixed diagnostic estimators

E1 retains raw softmax and separately evaluates normalized inverse-class-weight probabilities. The correction is analytical and need not fully calibrate session-normalized weightedCE. **Temperature scaling is omitted** because inner-checkpoint to full-refit phase transfer is unverified. Natural-frequency CE/Brier/ECE, class andANY AP/PR/AUROC when defined, reliability bins[0,0.1,…,1], weighted linear probability slopes, thresholds0.05/0.10/0.20/0.50, origin top1/top4 budgets, argmax confusion and signed probabilityIC are fixed. Constant fitting-prior and alwaysNORMAL references remain separately identified. Report raw/corrected ranking changes; no development threshold fitting.

QR1 primary diagnostics are proper pinball, per-quantile/interval coverage, sharpness and interval score against training-prefix unconditional quantiles. Median TG20 MSE/IC are descriptive. Last-input-step47 native V1/M2/Q2 and their same-origin median20 market states use weighted training-only terciles. Existing prefix fallbacks are retained with missing/fallback flags. Inner thresholds apply to inner roles; refit thresholds apply to refit/development. LOW≤first cut, MID≤second cut, HIGH above; tied empty cohorts stay empty. Predicted-width terciles are training-only, independently for each seed/fit. Eras are2011–2015,2016–2020,2021–2025. Report output variability, conditional calibration and proper-score skill as separate findings. A fixed-seed25042,400-draw intact-day circular-shift comparison applies only to the width/absolute-future-z association, with no neural permutation claim.

Matched development comparisons preserve entire days and recompute nonlinear AP. Fixed seed22042,400 resamples with non-overlapping one- and two-calendar-month blocks provide exploratory sensitivity intervals on109 reused sessions. Dependent stocks/origins and few calendar blocks limit interpretation.

Actual-objective allocation uses the frozen tensor kernels plus independent NumPy checks. Preserve equal-session/origin/stock mass, ordinaryCE versus class-normalizedCE, all three QR1 pinball components, top1%/5% ranked target/numerator tails, unique-origin small-MAD groups, disjoint groups/signs/complements, and separate99%/95% fitting-maximum magnitude ranges. Float64 asinh can collapse adjacent magnitudes into exact ties: check zero order reversals and exact top1/top5 membership, keeping original target ranks. No tolerance is widened.

Each arm saves at least20 highest-loss ticker cases (AAPL/AMZN/TSLA/SBUX) plus BOTH5/MAD_ONLY5 witnesses when present:48 genuine scheduled input candles, four outcome candles,20 genuine horizon return operands,16 native/scaled features and provenance. Input and future outcome context are explicitly distinguished. These numerical stores remain local and ignored.

## Output formats and execution

The new modules are `branch_replication_{spec,source,engine,authority,run,metrics,comparison,states,diagnostics,rehearsal}.py`. Immutable JSON receipts/checkpoint references, standard-decoder JSONL update telemetry, full-role Parquets, objective cohorts/case Parquets, Plotly HTML state figures and bound gate JSON are prescribed. Only the progress snapshot and activated registry pointer are atomically replaceable. Checkpoints and optimizer states have immutable SHA256 references; reload predictions and persisted populations must match exactly. Nested optimizer floats are compared exactly.

The rehearsal patches AdamW.step to raise and counts attempted calls. It physically traverses full calibration training/validation and two zero-update refit epochs, with an explicitly stationary12-epoch selector/progress replay. These receipts are reliability evidence, not learning curves or empirical results. All four roles are exported and reloaded, reconstructed from genuine endpoints and subjected to complete diagnostic/case gates. A rehearsal gate cannot satisfy production authority. Code, source, baseline and registry hashes are checked again before the proposal is sealed.

CPU4/inter-op1; proposed fitting planning range0.5–6 hours; peak RSS≤2GB; additional local storage≤1GB under10GB total. No new dependencies, credentials, provider access or data downloads. Researcher-attested bounded private-use/source/clock assumptions persist; no independent certification, trading, redistribution or Git publication.

After separate live approval, use the exact proposal and approval file, one arm at a time:

```bash
.venv/bin/python -m lstm_data.branch_replication_run --plan <this-directory>/experiment_design.json --approval <recorded-live-approval.json> --arm E1
.venv/bin/python -m lstm_data.branch_replication_run --plan <this-directory>/experiment_design.json --approval <recorded-live-approval.json> --arm QR1
```

Before execution, record the exact human response/event, the approved run IDs and proposal/execution/scientific hashes. The approval must have actor_type=human, response_provenance=LIVE_USER_RESPONSE_IN_THIS_SESSION and status=APPROVED. No approval file has been created in this preparation.

Stages2–6 remain pending: real fits, scientific branch conclusions, the six final scientific deliverables, collective comparison and additive dashboard integration. The existing dashboard and its running port are preserved. They are not claimed complete by a zero-step rehearsal.

The [submitted Package025 instruction](submitted_instruction.txt), opening paragraph, states: “This prompt does not itself authorize optimizer updates.” Stage1 explicitly requires a separate live approval for the exact models, code and scientific hashes and two starts.
