# P026 frozen temporal architecture screen

Preparation only. Exactly three proposed seed42 starts, in this order:

| Start | Arm | Run | Parameters | Controlled change |
|---|---|---|---:|---|
|54|A1|HF1M-LONG-TM1_ATTENTION-T2-S42-DEV1|6,466|Residual temporal attention over the same LSTM hidden sequence|
|55|A2|HF1M-LONG-TM3_MULTISCALE-T2-S42-DEV1|7,217|Causal inclusive1/4/12 means, Linear48→16 before the same LSTM|
|56|A3|HF1M-LONG-GRU32-T2-S42-DEV1|4,833|GRU cell replaces LSTM; one32-dimensional final hidden and scalar head|

A1 uses no-affine LayerNorm eps1e-5 and q/sqrt32 softmax over48 states, c=sum(a*h), readout=h48+gamma*(c−h48). Gamma starts exactly0. Query uses a local CPU generator seed2643 and Normal(0,.01). Query receives AdamW decay.01; gamma0 decay. Additional construction preserves the original T2 base weights and global training RNG.

A2 averages existing released scaled/fallback feature values over inclusive prefix windows of actual length min(window,s+1), then applies Linear48→16 initialized[I16,0,0],bias0. No extra candles, native-availability remasking, nonlinear mixer, second encoder or peer input. A1/A2 are exact T2 identities at initialization. A3 uses native PyTorch GRU16→32, one layer, zero fresh state per sequence; recurrent module then scalar head are constructed under seed42. Gates are not directly observed. Capacity and initialization differ across arms; this is not a parameter-matched causal experiment.

All arms preserve P020 FT16, TG20,20 canonical stocks/order,48-step lookback, source/action/quality masks, original clocks, four chronological roles and training-only inner/refit recipes. Source: mito0o852/OHLCV-1m at776328445b7ac6e7815ef3a483e9c8ded1eb6d56. Contract SHA2567adfec916b7eb74fead83ef1fe6082ff0fcee9ff0b6ebae5722077e2a82c01a5.

Counts: inner training4,428 origins/88,560 stock rows/2,513 sessions; inner validation766/15,320/459; refit5,210/104,200/2,980; development183/3,660/109. FittingApril2011–June2025; developmentJuly–December2025 with unchanged48-hour availability embargo. ProtectedJanuary–March2026 remains numerically locked. No future returns enter features or input eligibility.

Training is the original T2 z-MSE with equal session→eligible origin→20 stock mass. z=asinh(float32(y)/prefix scale); invert once using scale*sinh(zhat). AdamW LR.001, betas(.9,.999),eps1e-8; matrix/query decay.01, bias/gamma decay0; global gradient clip1;16 complete sessions per batch; no schedule. Head dropout.1, recurrent dropout0. D6g selects original-TG20 inner-validation MSE using STRICT loss<.999*qualifying_best (equality fails), min12/max60/patience10. Raw minimum and qualifying selection remain separate. Fresh same-seed initialization and empty optimizer refit for selected epochs only; calibration weights/scalers cannot be transferred to refit.

Primary comparator is saved T2/42, with saved T2/123 and ZERO contextual. No baseline fits. Primary scientific evidence is joint development original-TG20 MSE and equal-day origin SpearmanIC change. Forecast SD, lower optimized training loss, synthetic witnesses and module use alone do not establish skill. Report positive/negative/mixed/inconclusive/implementation failure distinctly; no automatic promotion. Compare signed deltas with400 fixed-seed22042 intact-calendar-month and two-month-block sensitivity resamples.109 reused days and three comparisons preclude a formal independent-confirmation interpretation.

Required diagnostics are preregistered in scientific_definitions.json and the submitted instruction: all four roles; MSE/MAE/RMSE/IC/direction/zero ties/top-bottom4 retrieval, weighted calibration/dispersion/residuals; fit-derived absolute event thresholds; stock/month/year/source-quality and causal V1 volatility slices. Ranked top1/5% target and numerator tails, origin-level smallMAD, disjoint NUM_ONLY/MAD_ONLY/BOTH/NEITHER, signs/complements and separate95/99%-of-fit-maximum magnitude ranges must conserve the actual float32 z objective. Every arm supplies22 distinct source cases (five per named stock plus BOTH_5/MAD_ONLY_5), each52 hourly rows and16 native/scaled/fallback channels, all20 target operands, UTC/ET clocks and observed-volume provenance.

A1 diagnostics: gamma/q trajectory, entropy/effective lookback and lag/stock/date distributions, actual readout change and historical perturbation. A2: coefficient blocks, branch signal/gradient norms, identity deviation, prefix causality, perturbations. A3: actual hidden dynamics, input-history BPTT/perturbations, capacity/compute; no fabricated reset/update gates. Attention and perturbations are not faithful causal attribution.

The controller requires the predecessor's complete SHA-bound scientific receipt (all4 populations, exact checkpoint reload, target reconstruction, objective conservation, uncertainty,22 cases, mechanism evidence, tests and source/resource integrity). A fit exit0 alone cannot authorize the next arm. Missing evidence or any failure halts the sequence. Starts are charged once immediately before calibration optimization; calibration+fresh refit share that start. Failures remain permanently charged. No retry, extra seed, combination, market download, trading, neural null or Git publication is authorized. Ledger stays53 until separate live approval and actual starts; maximum56/200.

Plan CPU4/inter-op1, approximately0.5–6h for three fits and diagnostics (estimate, not benchmark), ≤2GB process working RAM, ≤1GB additional private artifacts and ≤10GB total research storage. Source rights/publication/action-vintage assumptions remain bounded researcher-attested private research, without independent certification or data redistribution.

The menu reconciliation is in P026_ARCHITECTURE_RECONCILIATION.md. The package explicitly elects only these three independent candidates; broader market/peer/regime, E1/QR1 combination, extra seeds, walk-forward/null and protected confirmation research remain deferred.
