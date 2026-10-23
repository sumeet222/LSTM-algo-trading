# P024 recovery proposal — VERIFIED, NOT AUTHORIZED

**Current state: STOP_DROP0, ledger46/200. No recovery start reserved or executed.**

I launched DROP0 before inspecting the failed LRLOWsupplemental check. That sequencing error caused an interrupted charged start46. It is preserved and not refunded. LRLOWstart45completed its16epoch calibration/selected6epoch fresh refit and all corrected immediate checks; it will not be repeated. The diagnostic issue was one-ULP JSON parsing, not a training hyperparameter defect. DROP0saved two complete calibration epochs plus24updates of epoch3 (340total); its full calibration/refit state is unavailable. An epoch1checkpoint is not a valid continuation of the interrupted optimizer/RNG state.

## Exact proposed continuation

|Start|Run|Work|
|---|---|---|
|47|`HF1M-LONG-TM0-DROP0-S42-DEV1-REPAIR1`|Explicit fresh DROP0/42 calibration from initialization plus selected-epoch refit|
|48|`HF1M-LONG-TM0-WD0-S42-DEV1`|Original unstarted frozen calibration plus fresh selected-epoch refit|
|49|`HF1M-LONG-TM0-ES025-S123-DEV1`|Original unstarted frozen calibration plus fresh selected-epoch refit|
|50|`HF1M-LONG-TM0-H64-S42-DEV1`|Original unstarted frozen calibration plus fresh selected-epoch refit|
|51|`HF1M-LONG-TM0-L2H32-S42-DEV1`|Original unstarted frozen calibration plus fresh selected-epoch refit|

**Five new starts46→51/200**, one additional start beyond the original six-start package endpoint50. Failed46stays permanent; no extra retry/refund. The global registered ceiling200is unchanged. New v14journal/registry are only proposed and do not exist until explicit authorization.

## Verification and prevention

[Full parser/workflow verification](REHEARSAL_AND_PARSER_VERIFICATION.md): five complete zero-step phase workflows,20exact full-population exports,24tolerance populations including actual LRLOW,38focused tests,366files0static errors/warnings. All existing scientific tolerances retained; effective hyperparameters/reloads checked exactly. No new data or protected2026numeric access. Rehearsal receipts cannot authorize real starts.

The numerical run function has an AST identical to the reviewed original. It reuses unchanged T2epoch/export/gradient/checkpoint code. Only run identity/authority routing changes: first require the verified LRLOWcomplete receipt, then require both core and supplemental receipts before every subsequent start. A core-only/failed/missing receipt cannot consume a new start. Source/scientific settings remain the original frozen six-arm design; seed123only for ES025. No tuning from LRLOWdevelopment metrics.

## Exact bindings

- Proposal SHA256: `70a6fddda2ec87051f90d56f1ac0252aebb8a024b7e49542b0921815a8fe9597`.
- Execution SHA256: `a0f05f614f811bd62aabb1ae8855133228df13498323e7925fede8bd5ad62c97`.
- Input contract: `7adfec916b7eb74fead83ef1fe6082ff0fcee9ff0b6ebae5722077e2a82c01a5`.
- Existing LF/TG20/source/rights/clock/mask/chronology/optimizer/scaler definitions preserved. CPU4,0.5–6hplanning,≤2GBRAM,≤2GBadditional local outputs under10GBtotal. No protectedoutcomes, otherseeds/arms/combinations, trading, marketdownloads or Gitpublication.

After new approval: record its verbatim live response with `failed_start_46_preserved=true`, `additional_drop0_restart_authorized=true`, the five run IDs and exact hashes. Invoke `python -m lstm_data.optimization_screen_recovery_run --plan <this>/experiment_design.json --approval <new_live_approval.json> --run-id <first ID>`. After each fit run recovery_diagnostics and recovery_supplement, verify the complete receipt, then invoke only the next listed run. All fits remain forbidden pending that response.

After all five new arms pass, combine them with immutable LRLOWfor six-model diagnostics and additive dashboard integration. No six-way result, dashboard completion or PASS_P024_COMPLETE is currently asserted.

## Why a new live response is required

Package024 states: “An important defect must STOP and require renewed authorization before code-changing resumption or restart.” The original approval bound earlier authority code and maximum50starts. The strengthened guard plus fresh DROP0and proposed endpoint51therefore require new explicit authorization. This is a package requirement; no training will be restarted on this proposal alone.
