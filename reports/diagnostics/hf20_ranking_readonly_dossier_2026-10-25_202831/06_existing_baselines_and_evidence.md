# 06 — Existing baselines and evidence inventory

**QUALIFIED:28 actual current-HF1M-long run records located; missing strong controls and earlier-cutoff OOS evidence remain unavailable.**

All findings are descriptive. Inner training/refit are in sample; inner validation is selection-influenced; development is 109 repeatedly inspected sessions, not confirmation. No new model, objective fit, labels, inference or trading.


| arm | run_id | seed | status |
| --- | --- | --- | --- |
| C0 | HF1M-LONG-TM0-C0-S123-DEV1 | 123 | COMPLETED |
| C0 | HF1M-LONG-TM0-C0-S42-DEV1 | 42 | COMPLETED |
| T2 | HF1M-LONG-TM0-T2-S123-DEV1 | 123 | COMPLETED |
| T2 | HF1M-LONG-TM0-T2-S42-DEV1 | 42 | COMPLETED |
| E1 | HF1M-LONG-TM0-E1-S42-DEV1 | 42 | COMPLETED |
| H2 | HF1M-LONG-TM0-H2-S42-DEV1 | 42 | COMPLETED |
| R1 | HF1M-LONG-TM0-R1-S42-DEV1 | 42 | COMPLETED |
| W1 | HF1M-LONG-TM0-W1-S42-DEV1 | 42 | COMPLETED |
| DM1 | HF1M-LONG-TM0-DM1-S42-DEV1 | nan | COMPLETED_FIT_PENDING_IMMEDIATE_DIAGNOSTICS |
| QR1 | HF1M-LONG-TM0-QR1-S42-DEV1 | nan | COMPLETED_FIT_PENDING_IMMEDIATE_DIAGNOSTICS |
| SS1 | HF1M-LONG-TM0-SS1-S42-DEV1 | nan | COMPLETED_FIT_PENDING_IMMEDIATE_DIAGNOSTICS |
| LRLOW | HF1M-LONG-TM0-LRLOW-S42-DEV1 | 42 | COMPLETED |
| DROP0 | HF1M-LONG-TM0-DROP0-S42-DEV1-REPAIR1 | 42 | COMPLETED |
| ES025 | HF1M-LONG-TM0-ES025-S123-DEV1 | 123 | COMPLETED |
| H64 | HF1M-LONG-TM0-H64-S42-DEV1 | 42 | COMPLETED |
| L2H32 | HF1M-LONG-TM0-L2H32-S42-DEV1 | 42 | COMPLETED |
| WD0 | HF1M-LONG-TM0-WD0-S42-DEV1 | 42 | COMPLETED |
| E1 | HF1M-LONG-TM0-E1-S123-DEV1 | 123 | COMPLETED_FIT_PENDING_IMMEDIATE_GATE |
| QR1 | HF1M-LONG-TM0-QR1-S123-DEV1 | 123 | COMPLETED_FIT_PENDING_IMMEDIATE_GATE |
| A3 | HF1M-LONG-GRU32-T2-S42-DEV1 | 42 | COMPLETED_FIT_PENDING_IMMEDIATE_GATE |
| A1 | HF1M-LONG-TM1_ATTENTION-T2-S42-DEV1 | 42 | COMPLETED_FIT_PENDING_IMMEDIATE_GATE |
| A2 | HF1M-LONG-TM3_MULTISCALE-T2-S42-DEV1 | 42 | COMPLETED_FIT_PENDING_IMMEDIATE_GATE |
| A4 | HF1M-LONG-P027-PEER19-M1-MEANSD-T2-S42-DEV1 | 42 | COMPLETED_FIT_PENDING_IMMEDIATE_GATE |
| A6 | HF1M-LONG-P027-SP1-ATTN16-T2-S42-DEV1 | 42 | COMPLETED_FIT_PENDING_IMMEDIATE_GATE |
| A5 | HF1M-LONG-P027-SP3-RANK4-T2-S42-DEV1 | 42 | COMPLETED_FIT_PENDING_IMMEDIATE_GATE |
| A8 | HF1M-LONG-P028-GLOBAL8-LOCAL32-T2-S42-DEV1 | 42 | COMPLETED_FIT_PENDING_IMMEDIATE_GATE |
| A7 | HF1M-LONG-P028-MC1-T2-S42-DEV1 | 42 | COMPLETED_FIT_PENDING_IMMEDIATE_GATE |
| A12 | HF1M-LONG-P028-SOFT2-T2-S42-DEV1 | 42 | COMPLETED_FIT_PENDING_IMMEDIATE_GATE |


[model_inventory_final.csv](model_inventory_final.csv) is authoritative for this audit; it supersedes the preserved preliminary model_inventory.csv and model_inventory_v2.csv. It lists exact result/hash, four-role export/checkpoint refs, source/revision/recipe, declared seed evidence, objective formula/units and chrono status. model_artifact_references_v2.json gives verified underlying bytes. Some run_result statuses were intentionally sealed as FIT_PENDING_IMMEDIATE_GATE; later per-arm gates/collective reports establish completed diagnostics without rewriting those original results. A seed omitted from a P023 result field is not silently replaced: the runID and frozen dm_quantile_loss.py seed42 initialization are cited separately.

| Reference/control | Actual state |
| --- | --- |
| ZERO | deterministic null; squared error from saved Y; Spearman undefined, half-credit predicted pair ties |
| M1/M2 activity/volatility shortlist | descriptive existing-feature rank associations only; not trained baseline or new forecast campaign |
| Pooled full48×16ridge/rank-linear/nonrecurrent | no current matched saved trained control found in enumerated HF1M-long records; old5stock results not substitutes |
| Static historical stock-profile score | no current trained/issued held-out record identified; not fitted now |
| C0/T2 seed42/123 | saved full four-role point forecasts |
| H2/W1/R1/E1 seed42 | development saved separately in P022 collective_diagnostics_v2, not necessarily in initial run_result artifacts |
| DM1/QR1/SS1 seed42 | saved .parquet exports in original trained_runs; role filenames differ from P021 predictions naming |
| P024 six factors | saved actual variants including ES025seed123, LRLOW and repaired DROP0; no new optimization |
| E1/QR1 seed123 | archived P025 approved_runs, no new calibration |
| A1/A2/A3 | P026 temporal/GRU actual approved exports |
| A4/A5/A6 | P027 actual peer-information variants, not information-matched controls |
| A7/A8/A12 | P028 actual endpoint gate/global-local/two soft-head exports |
| A9/A10/A11 | untrained and paused, not failed; no output manufactured |
| Earlier-cutoff HF1M-long walk-forward folds | no legitimate additional fold forecasts identified in these run records; historical refit dates are in sample |
| Rolling versus expanding model training | not established by current screens; rolling input sequence is not rolling training |

## Ledger and reporting amendment

Current journal reports62/200, checked unchanged. Four P021 fits plus4P022+3P023+6P024+2P025+3P026+3P027+3P028 give28distinct completed fitted variants; failed starts and recoveries remain charged under the historical journal, not inferred by counting files. No start is reserved or refunded.

P028 actual journal ended62. Original progressive display incorrectly showed63/64/65; corrected historical display is60/61/62. [postfit_ledger_metadata_amendment.json](../../../reports/experiments/ta028_market_state_2026-10-24_064442_execution_v1/checkpoint_completion_v2/postfit_ledger_metadata_amendment.json) preserves the original executed bundle0f685db34dc42bd62fbad1333e1813a20edf0e71aab2d37e9373c5c80d4d0608 and reporting-corrected bundlec9d4d349f67db65a91704e9832a76b50dcd12d668d7d6cbafada94ce6efae9d4. No old artifact is rewritten or treated as new fitting authority.

Missing-control follow-up is a proposal only: one bounded full-information regularized rank-linear comparator is lower cost than recurrent calibration/refit; prolonged neural evidence multiplies the number of independently selected/fitted folds and seeds. No executable fit command or start authorization is supplied.
