# P027 frozen three-arm architectures

Preparation only; no fitting authority. Canonical definitions: scientific_definitions_v2.json. All three arms are independent alternatives on original TM0/T2, seed42, not stacked models. The source, 20 names, dates, 48-step embargo, FT16 formulas/masks/recipes, TG20, weights and original D6g selector remain frozen.

| Arm | Coupled inputs / exchange | Parameters | Proposed start |
|---|---|---:|---:|
| A4 PEER19-M1-MEANSD | [B,20,48,16] plus two leave-one-out M1 summaries → [B,20,48,18], shared LSTM18→32 | 6,689 |57|
| A5 SP3-RANK4 | Shared stockwise LSTM16→32, final H[B,20,32], rank4 stock-axis residual |6,593|58|
| A6 SP1-ATTN16 | Same encoder; one-head same-origin 20×20 attention, d16 |8,481|59|

All outputs are transformed scores [B,20]. Ordinary base T2 has6,433 parameters. Stock panels remain coupled; no cross-origin/session exchange, independent-stock minibatch shuffling, ticker embedding, sector input, USA500, new quality feature or target-window value.

A4 at each input step: mu_i=sum_{j≠i}u_j/19, sd_i=sqrt(sum_{j≠i}(u_j−mu_i)^2/19), u is the exact phase-scaled/fallback M1 input. Explicit centered float32 squared deviations avoid cancellation; clamp roundoff-negative variance to0, no epsilon or added fitting. Own16 channels unchanged. Initialize LSTM18 then unchanged dropout/head using seed42.

A5: Htilde=H+M2 GELU(M1 LN(H)), M1[4,20], M2[20,4], exact GELU, hidden-axis non-affine LN32 eps1e-5. Shared base constructed first; local CPU generator2747 initializes M1 sequential Normal(0,.01); M2=0. Base/global dropout RNG unchanged. Bias-free projections, no added dropout. Exact identity at initialization. Canonical-axis, position-specific weights require M1'=M1 P^T and M2'=P M2 under coordinate permutation.

A6: Q=LN(H)WQ, K=LN(H)WK, V=LN(H)WV; A=rowSoftmax(QK^T/4); Htilde=H+AVWO. Q/K/V matrices[32,16], WO[16,32], no biases, non-affine hidden LN eps1e-5. Local CPU generator2748 sequential Normal(0,.01) Q/K/V, WO=0; base initialized first. All20 keys including self; report self/off-diagonal masses separately. No learned identities; eval mode is stock-permutation equivariant. Attention/Jacobians describe associations, not economic causality.

All heads: dropout0.1 then Linear32→1; recurrent dropout0, eval dropout disabled. AdamW lr.001, betas(.9,.999), eps1e-8, weight decay.01 for all matrices/projections and0 for bias; gradient norm cap1;16 whole sessions/batch; no schedule. parameter_groups_frozen.json lists exact memberships and counts. Seed42 for calibration and separately initialized fresh refit; empty refit optimizer. Original strict D6g: original-TG20 validation MSE <.999×qualifying-best, equality fails; min12/max60/patience10. Track raw minimum separately; refit only selected epoch count, not raw-min count. Refit uses its own full-prefix epsilon/scalers/T2 scale.

Target: same-session four-hour log returns, cross-stock median and median absolute deviation; y=(r−median(r))/(MAD(r)+epsilon_prefix). z=asinh(float32(y)/s_prefix); optimized equal-session→origin→20-stock z-MSE; original inverse s_prefix*sinh(zhat) exactly once. Future returns/median/MAD/targets are labels only and cannot influence input transforms, peer pools or masks. Inner epsilon .00032970431934696, scale .906406830018944; refit epsilon .00033464021096456584, scale .9057319697455458. Independent prefix receipts reproduce these; no clipping/truncation or extra floors.

A4 sees two peer summaries at each historical step; A5/A6 encode all16 peer channels before final-state exchange. A4 is not an information-matched ordinary-LSTM control. A5/A6 gains alone cannot isolate exchange from fuller information, stock-position effects, capacity or optimization. A5 vs A6 have comparable raw histories, different mechanisms/parameter budgets. The October10 full-peer ordinary-LSTM caveat remains; a fourth fit is prohibited here.

Read-only negative control: shift only other-stock histories by ten preceding distinct source-input-eligible sessions at the same10:30/11:30 slot, strictly earlier availability, role-correct fitted recipe. Missing exact slot/window excludes only that diagnostic origin, no future/admission/label eligibility filters and no fallback dates. Original/shifted are rescored on the same matched subset and equal-session allocation. Own history is fixed; A4 recomputes two summaries, A5/A6 retain original own H and donor peer H. Compare original via the same focal-counterfactual batching to prevent floating-point batching artifacts, with neutral-vs-native inverse tolerance unchanged. This is distribution-shifting sensitivity, not trained null/significance/causal proof.

Numerical gates (rtol,atol): exact hyperparameters and full checkpoint replay0; original target(1e-10,1e-11); point float32 z-loss(3e-5,2e-6); weighted objective(5e-7,1e-8); inverse/neutral-control original score(7e-7,1e-7). Peer mean/SD independent float64 NumPy(1e-6,2e-7) verified across both entire training prefixes, not selected examples alone. No postapproval tolerance relaxation. Undefined IC remains undefined, never0.400 intact-month and two-month block replicates seed22042; paired origin IC uses joint finite origin pairs and their true counts, daily IC joint finite day statistics. Report occupancy and exploratory dependency.

Hard gate before each next start checks full four-role numerical/source/objective/reload/resource/uncertainty/peer-control/case evidence, named artifact hashes, genuine Streamlit component payloads, and both arm reports. Boolean/text PASS alone cannot bypass it. Failure or changed execution stops without retry; every genuine start is permanently charged. Protected Jan–Mar2026 values remain inaccessible before any path lookup.
