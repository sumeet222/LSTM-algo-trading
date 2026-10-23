# P024 frozen experiment design — PREPARED_NOT_TRAINED

Ledger **44/200**, zero new starts or optimizer updates. Six proposed runs in this exact order:

|Start|Run|Controlled change|Parameters|
|---|---|---|---|
|45|`HF1M-LONG-TM0-LRLOW-S42-DEV1`|`{'learning_rate': [0.001, 0.0003]}`|6433|
|46|`HF1M-LONG-TM0-DROP0-S42-DEV1`|`{'head_dropout': [0.1, 0.0]}`|6433|
|47|`HF1M-LONG-TM0-WD0-S42-DEV1`|`{'matrix_decay': [0.01, 0.0]}`|6433|
|48|`HF1M-LONG-TM0-ES025-S123-DEV1`|`{'improvement': [0.001, 0.00025]}`|6433|
|49|`HF1M-LONG-TM0-H64-S42-DEV1`|`{'hidden': [32, 64]}`|21057|
|50|`HF1M-LONG-TM0-L2H32-S42-DEV1`|`{'layers': [1, 2]}`|14881|

ES025 compares primarily with saved T2/123; all other arms with T2/42. Verified seed1230.025% replay selects **epoch2**, stops12; raw minimum12 does not imply qualification against epoch2. This corrects the initial stage0 narrative; numeric tables were always correct.

Reuse unchanged P021 T2 epoch/export computation, SharedLSTM encoder, weighting, transforms, sampler and clipping. Capacity variants change only LSTM dimensions. Observational hooks record original/clipped per-module norms and parameter updates without changing gradients, RNG or AdamW. Fresh same-seed refit and optimizer after calibration; strict historical comparator preserved.

Risk: weak information may persist; six correlated single-seed exploratory screens on reused development data cannot certify alpha. Conditional source/clock/rights and quality limitations persist. H64/depth increase compute/overfit risk. More dispersion/lower training loss/less clipping is not success. No automatic promotion.

Frozen math/thresholds, bootstrap400/seed22042, tails, witnesses, source boundaries, backlog and exact resources are in `scientific_design.json`. Every arm must pass its complete immediate gate before the next start. Dashboard/collective stages remain pending until six genuine completed fits. No held-out numerics, new data, extra seeds, combinations, retries, trading or Git publication. CPU4; planning0.5–6h; RAM≤2GB; additional storage≤2GB and total local task-data/artifact/report storage≤10GB.

Proposal SHA256: `d43c67eb83b2c0497a03460fe1c9f20e84f7adf9146aad1d512cb434b8920d44`

Execution SHA256: `d045c4a3ae8f2076e8bd108ee304783bc3becb59124a4bf9850b2afd9841b452`

Implementation diff: `implementation_source.patch`. Independent parameter/groups: `parameter_diff_audit.json`. Final zero-update full-population export/reload proof: `stage_1_preflight_final.json`. Tests/static check and immutable stage receipts are bound by the proposal. Proposed successor is not activated.

Package024 Stage2 explicitly requires separate live human approval before any start. Preserve failed historical starts. Approval must name the exact six runs, proposal and execution hashes.
