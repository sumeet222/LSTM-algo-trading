# Detailed four-role ranking, extreme-value and true-objective diagnostics

**31 accepted OOS model-fold outputs;88 accepted role outputs.** Full four-year P/LR/naive/T2R/NR; PW2022–24 only. No LP or failed F21PW outcome is fabricated. Inner training/refit are in sample; inner validation selects duration/penalty; subsequent-year OOS is retrospective. Complete counts/dates/units are in all_role_metrics.csv, folds.json and the16 frozen index CSVs.

## Units and independent reconciliation

T2R optimizes the phase-fitted float32 asinh(Y/s) squared error. A once-only inverse gives original TG20 Y units for contextual error; it is not calibrated expected raw return, because inverse(E[asinh(Y)|X]) generally differs from E[Y|X]. Future median/MAD used to define Y are labels/diagnostic operands, not available inputs. NR/LR/P have normalized-rank pointwise squared loss. PW has untied unordered-pair logistic loss, normalized by valid pairs, with half of each pair assigned to each endpoint. Rank-only outputs have no sinh inverse, original-return MSE or z-MSE.

Keyed score tables retain R, median, numerator, MAD, epsilon/scale, Y/Z, actual output/ranks, actual objective allocation, hierarchical weights, source/recipe/checkpoint hashes and quality/age flags. Nominal double-precision Z is diagnostic; actual training-loss allocations use the executed float32 transform/operations. Independent scalar/per-row checks use the frozen numerical tolerances and higher-precision audit sums, never changed loss values.

The canonical extended tables are the **v2** files: N0 additive IC contributions are unavailable, preserving its mathematically undefined correlation. REPORT_ONLY_CORRECTION.json explains the v1 zero-placeholder ambiguity; scores, primary metrics, fits and journals were untouched. Do not interpret a constant midrank score's small normalized-rank squared error as ordering skill.

## Original-target tails in each model's actual objective

| year | model | actual_objective | top1_objective_share | top5_objective_share | T2R_original_MSE | T2R_top5_original_MSE_share |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | NR | 0.3688489 | 0.02590159 | 0.1254907 | nan | nan |
| 2021 | T2R | 1.282905 | 0.06561743 | 0.2267692 | 3.344773 | 0.5084007 |
| 2022 | NR | 0.3690683 | 0.02633856 | 0.1268964 | nan | nan |
| 2022 | PW | 0.6931685 | 0.009976117 | 0.05041335 | nan | nan |
| 2022 | T2R | 1.322301 | 0.06233847 | 0.2338887 | 3.37831 | 0.5033432 |
| 2023 | NR | 0.3688205 | 0.02468848 | 0.1242902 | nan | nan |
| 2023 | PW | 0.6936035 | 0.009301657 | 0.04904591 | nan | nan |
| 2023 | T2R | 1.272957 | 0.06662968 | 0.2340079 | 3.552662 | 0.547841 |
| 2024 | NR | 0.3693503 | 0.02740517 | 0.1252425 | nan | nan |
| 2024 | PW | 0.6940236 | 0.01027381 | 0.04916559 | nan | nan |
| 2024 | T2R | 1.344914 | 0.06989726 | 0.2337226 | 3.836045 | 0.5328117 |

Top1/top5 sort original |TG20|, break ties deterministically and retain the exact ordinary complement. Row percentages and weight mass differ because the metric gives equal session→origin→stock/pair weight. Train-event95/99, high-numerator95 and small-MAD05 cuts use the applicable prior fit prefix; they are distinct from role-ranked target tails and from own-error-ranked subsets. No case is removed for being extreme.

T2R OOS top5 contributes22.68–23.40% of actual z-loss and50.33–54.78% of original-Y MSE. NR top5 contributes12.43–12.69% of its ordinal point loss; PW top5 contributes4.90–5.04% of allocated pair loss. The objectives redistribute tail stress, yet NR/PW do not show a consistent ranking gain over T2R. These loss units are not interchangeable, and contribution shares are not gradient influence or alpha. No OOS floor-active MAD≤epsilon row occurs in the completed neural folds. This rejects floor dominance for those observations, not every denominator effect.

## Same-row ordinary-versus-extreme ranking differences

NR minus T2R normalized predicted-rank error, negative favoring NR; identical source keys/targets and weights:

| year | cohort | weight_mass | normalized_rank_error_delta |
| --- | --- | --- | --- |
| 2021 | ALL | 1 | -0.003480601 |
| 2021 | TARGET_RANK_TOP5 | 0.04872881 | 0.006540212 |
| 2021 | TARGET_RANK_TOP5_COMPLEMENT | 0.9512712 | -0.01002081 |
| 2022 | ALL | 1 | 0.01597369 |
| 2022 | TARGET_RANK_TOP5 | 0.05036946 | 0.003695265 |
| 2022 | TARGET_RANK_TOP5_COMPLEMENT | 0.9496305 | 0.01227843 |
| 2023 | ALL | 1 | 0.005404882 |
| 2023 | TARGET_RANK_TOP5 | 0.04898256 | -0.0007553301 |
| 2023 | TARGET_RANK_TOP5_COMPLEMENT | 0.9510174 | 0.006160212 |
| 2024 | ALL | 1 | -0.002266977 |
| 2024 | TARGET_RANK_TOP5 | 0.04932432 | -0.003083028 |
| 2024 | TARGET_RANK_TOP5_COMPLEMENT | 0.9506757 | 0.000816051 |

In2021 the NR overall improvement comes from ordinary rows while the top5 worsens. In2022 both parts worsen. In2023 a small top5 improvement is outweighed by ordinary deterioration. In2024 top5 improvement offsets ordinary deterioration. There is no uniform tail or ordinary benefit. paired_cohort_rank_error.csv includes the full matched-role/control comparisons; own-error cohorts are never used as favorable paired populations.

## Numerator/MAD, error energy and conditional pair behavior

cohort_objective_and_error_decomposition_v2.csv contains ALL, signed training events, exact target1/5 complements, NUM_ONLY/MAD_ONLY/BOTH/NEITHER, floor activity, counts/origins/sessions/weight mass, real objective contribution and rank-IC attribution. The disjoint NUM/MAD partition conserves full objective loss. For T2R, target energy + forecast energy −2alignment equals original error; common + centered + subset cross term equals the same error. The cross term need not vanish inside a selected subset. Original MSE/energy columns are unavailable for ordinal-only models.

all_original_objective_and_error_cohorts.csv retains every original own-optimized-error top1/5 and complement, signed/floor/source event cohort, normalized-rank error and actual loss. T2R_original_error_ranked_cohorts.csv adds its original-Y-error top1/5/complements on the same observations; those are own-error diagnostic sets, not common cohorts for claiming another model's gain.

return_gap_pair_diagnostics.csv partitions untied pairs by both/one/neither training-event95 endpoint and training-prefix fifth-percentile return gap versus complement. It reports dependent-pair counts, origin/session counts, pair weight mass, concordance and actual PW loss; the six disjoint bins conserve pair mass/loss. The input gap is never a training multiplier or tuned tie dead-zone. cohort_pair_concordance_and_PW.csv retains endpoint-tail and score-gap diagnostics. Independent NumPy reconstruction verifies PW half-endpoint allocations.190 pairs per origin are not190 independent market events.

zero_score_objective_context.csv evaluates the already-declared zero-score reference in each actual loss space, without a new fit. NR OOS point loss is slightly above the zero-score reference in all four years; PW is near/slightly above log2 in all three completed years. T2R is above its z-zero reference in three years and marginally below in2023. Zero-score Spearman stays undefined. Finite/low-amplitude scores and stable bounded losses do not establish conditional ordering information.

## Source quality, features, witnesses and learning trace

cohort_stock_month_sector_quality_v2.csv disaggregates target/NUM–MAD/ordinary cohorts by ticker, month, static publisher-sector ETF proxy, source flags and fallback. The sector proxy is not historical PIT certification. Per-role model files add slot/month/full quality breakdowns, score margins/ties/retrieval and all raw metric quantities. No retrospective quality deletion or causality claim.

SOURCE_CASE_REPLAY_RECEIPT.json and source_case_checkpoint_replay.csv independently reload accepted refit checkpoints:22 T2R,22 NR and16 PW case replays from22 underlying origins/12 sessions. F21PW's6 cases are unavailable because start65 failed. Maximum saved/replayed score difference4.47e-8; feature tensors are bit-identical, targets match, optimizer calls/new recipe fits0. All families share one small case-input NPZ per fold; raw52-hour candle windows are not copied. source_case_native_fallback_by_channel.csv adds352 case-channel records, with native/fallback counts over48 steps and source-age/publication qualification. The same case replayed through multiple models remains one event.

TRAINING_AND_SELECTION_TRACE.md, complete_epoch_trace.csv and gradient_clip_update_summary.csv retain true online dropout-ON objectives versus fixed-checkpoint dropout-OFF role diagnostics, selected/raw epochs, initialization/optimizer reset and step counts. Online losses average changing stochastic models and need not equal the final fixed-checkpoint loss. No new gradient/fit was performed merely to recreate a failed log.

Archival P028 A7/A12 findings remain background: small original-MSE gains came from centered extreme rows and offset ordinary deterioration with worse ranking. They are not newly trained controls or evidence of improvement here. Publication/action vintage, retrospective fixed cohort, bounded private-use rights and the2-minute historical price-only target/issuance mismatch remain qualified; no trading/P&L or2026 confirmation inference.
