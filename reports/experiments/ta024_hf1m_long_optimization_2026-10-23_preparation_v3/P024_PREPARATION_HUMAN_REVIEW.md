# P024 preparation review — PREPARED_NOT_TRAINED

**Ledger44/200, zero new starts, zero optimizer updates.** Stage0 and Stage1 pass. Stage2 live approval is pending; stages3–11 remain unexecuted. The existing journal/pointer are unchanged; v13 is only a proposed successor.

Verified immutable source/revision, P019B action/mask release, P020 FT16/TG20 contract and four exact role populations; all1701source/derived files (1,446,901,820bytes) retain their hashes. Protected2026 partitions were byte-hashed only. The researcher-attested private rights/clock/source limitations and broader scientific holds remain unchanged.

Both T2 baselines reproduce their original development metrics and population. Clipping rates across saved calibration+refit updates are0.2503% (seed42) and0.2400% (seed123), not evidence of widespread clipping. Prediction SD is0.048887/0.034900 versus actual target SD1.765362. These are observations, not proof of optimizer failure or vanishing gradients.

**Selector correction:** numeric forensic tables were correct, but the initial narrative/chat incorrectly said the0.025% replay selects12. It selects2/stops12 for seed123: epoch2 qualifies against1, epoch12 does not qualify against2. Historical0.1% selection is1/raw12. Seed42 selects7/raw7 under both replayed rules and stops17. Neither replay is censored. See stage_0_review_correction.md, which supersedes the initial narrative. ES025 remains exactly seed123/0.025%; no scientific trial definition changed.

Six frozen single-factor arms and exact start order are in [P024_EXPERIMENT_DESIGN_FROZEN.md](P024_EXPERIMENT_DESIGN_FROZEN.md). Counts6433/21057/14881verified independently. The existing T2 epoch/export kernel is reused; head placement, matrix/bias groups, session weighting, transform/inverse and zero recurrent state remain intact.

Validation: **33focused tests passed**; full static check **355files,0errors,0warnings**. Six real-source one-batch forward/backwards have finite gradients with AdamW.step blocked. All24arm/role full-population exports match saved checkpoint reloads, with compact private samples retained. Fourteen immutable progress receipts survive replaceable-snapshot updates and duplicate rejection. Initial-weight rehearsal exports are not trained model results. Full fit and postfit diagnostics/dashboard rendering are pending until live approval and genuine runs.

Preparation engineering history: first audit attempt used the wrong historical checkpoint payload key; the second hit a duplicate report-field name. Both aborted with zero starts/updates; their namespaces/logs survive. Fixed before sealing; third audit passed. Final preflight was rerun after atomic checkpoint/progress-schema fixes. Initial static issues were fixed without suppressions; two prior test assertions now explicitly convert tuples to NumPy arrays without changing expected values, and both focused tests pass.

Proposal SHA256: `d43c67eb83b2c0497a03460fe1c9f20e84f7adf9146aad1d512cb434b8920d44`

Execution SHA256: `d045c4a3ae8f2076e8bd108ee304783bc3becb59124a4bf9850b2afd9841b452`

CPU4, planning0.5–6h, RAM≤2GB, additional local outputs≤2GB under10GBtotal. No new data, protected numerical access, other seeds/arms, combinations, trading, publication or Git operations are authorized. Each failure counts and stops; no automatic retry. Per-model scientific checks must pass before the next start. Collective comparison and additive dashboard follow only after six successful arms.

Package024 Stage2 states: “The Markdown prompt is not itself authorization.” The separate live approval must bind these exact six runs, proposal and execution hashes. [Execution handoff](P024_EXECUTION_HANDOFF.md) gives the precise next commands and approval schema. No independent source licensing or scientific-gate certification is asserted.
