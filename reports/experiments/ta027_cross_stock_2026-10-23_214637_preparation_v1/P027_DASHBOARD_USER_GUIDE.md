# P027 dashboard guide

Launch `./scripts/run_track_a_dashboard.sh`; choose Explore → HF1M Long — Cross-Stock Sharing (P027). During preparation it says no trained candidate is available. After live approval and full arm gates, only completed/gated arms appear progressively; a selector cannot start training, generate predictions or bypass protected routes. Historical P021–P026 sections remain available.

Choose arm, one of inner_train/inner_validation/refit/development, then view:

|View|Evidence|
|---|---|
|Start Here|Source/contract/checkpoint/recipe/parameter identity, scope and information caveats|
|Comparison|Original TG20 metrics, saved T2/42 primary, T2/123/ZERO context, role comparisons and paired uncertainty|
|Outputs|Score vs actual and baseline distributions; original TG20 MSE is distinct from optimized z-MSE|
|Actual Objective Tails|Ranked and magnitude-range groups, numerator/MAD disjoint partitions, weights/mass/loss conservation|
|Exact Cases|22 final-refit source cases,48 input+4 future outcome candles, UTC/ET endpoints, genuine observed volume/quality and16 native/scaled channel values; peer hidden/operands/attention|
|Mechanisms|A4 leave-one-out operands/dispersion, A5 fixed-axis rank4 matrices/spectra/derivatives, A6 true20×20 attention and self/peer masses|
|Peer Information Control|Original and10-prior-session same-slot shifted peers on the same subset, own histories fixed, counts/mapping/MSE/IC/sensitivities; no refitting|
|History / Features|Canonical20 ticker selectors, guarded role/date/origin histories and16 feature channels|
|Training / Gradients|Raw/qualified epoch selection, actual objective and clipping/gradient/parameter diagnostics|

Future source candles are label evidence, never model inputs. Volume carry is not observed volume; use observed_volume_sum/volume_quality_tier. Empty diagnostic groups are reported without changing the model population. Jan–Mar2026 and malformed queries are rejected before numerical lookup. Private model/data artifacts must be provisioned lawfully via manifests on another machine; do not commit them. Tests establish component/Plotly specs and localhost HTTP, not screenshot/pixel verification.

A4 receives two peer summary channels; A5/A6 encode fuller FT16 peer histories. No full-information-matched architecture claim follows from A5/A6 vs A4. A5 weights require canonical ticker order; A6 attention is permutation-equivariant without learned identities. Associations and historical-peer distribution shifts are not causal evidence or trained null tests. Reused109-session development is exploratory.
