# P024 final human review

**Completed: six successful controlled arms; ledger51/200.** Your exact five-start recovery approval was executed in order47–51. Completed LRLOW45 and failed DROP046 remain preserved. There was no further retry, fit, seed, combination, download, trading run or protected2026 numerical access.

The bounded screen does not establish that the near-zero forecasts were caused by the tested optimization settings or insufficient capacity. ES025/123 offers a small exploratory checkpoint-selection signal; it is not confirmed. No candidate is automatically promoted.

## Main diagnostic files

- [Collective model comparison](collective_v1/P024_COLLECTIVE_MODEL_COMPARISON.md): all six arms, both saved T2 seeds, ZERO, all four roles and matched uncertainty.
- [Actual-objective extreme loss attribution](collective_v1/P024_OBJECTIVE_SPACE_EXTREME_LOSS_ATTRIBUTION.md): ranked tails, magnitude ranges, numerator/MAD decomposition and exact witnesses.
- [Dashboard guide](collective_v1/P024_DASHBOARD_USER_GUIDE.md): exact clicks for the new page.
- [Numerical reconciliation](collective_v1/population_consistency.json):24 real populations; unchanged tolerances.
- `final_closeout_receipt.json` and `artifact_inventory_final.csv`: final status and complete hash/Git-intent inventory.

## Exploratory development

| model | seed | mse | daily_ic | prediction_sd |
| --- | --- | --- | --- | --- |
| ZERO | 42 | 3.11656 | undefined | 0 |
| HF1M-LONG-TM0-T2-S42-DEV1 | 42 | 3.10656 | 0.07555945 | 0.04888722 |
| HF1M-LONG-TM0-T2-S123-DEV1 | 123 | 3.114912 | 0.025493 | 0.03490043 |
| LRLOW | 42 | 3.110404 | 0.07164103 | 0.03125112 |
| DROP0 | 42 | 3.104692 | 0.07277976 | 0.05279653 |
| WD0 | 42 | 3.106679 | 0.07406947 | 0.04930352 |
| ES025 | 123 | 3.112703 | 0.03260655 | 0.03119632 |
| H64 | 42 | 3.107416 | 0.03542763 | 0.05017057 |
| L2H32 | 42 | 3.116366 | -0.001325824 | 0.00953835 |

Use T2/42 for LRLOW, DROP0, WD0, H64 and L2H32; use T2/123 for ES025. ZERO IC is undefined. These109 reused development sessions are correlated;3660 stock rows are not independent trials.

- **LRLOW:** smaller output dispersion and slightly worse MSE/IC than T2/42. The lower learning rate does not support the proposed remedy here.
- **DROP0:** lower MSE and better top4 recall, but slightly lower IC. Both month-block sensitivities include zero for MSE and IC differences: mixed and inconclusive.
- **WD0:** tiny deterioration in both MSE and IC; both exploratory block sensitivities retain those directions. Removing matrix decay offers no positive signal in this seed.
- **ES025:** selected epoch2 instead of baseline123 epoch1; raw minimum remains12. MSE decreases by0.002209 and IC increases by0.007114, but both one/two-month intervals include zero. Its entire calibration validation curve matches the saved baseline to4.44e-16 CSV precision, supporting the intended selection-mechanism isolation. No raw-best12 refit or counterfactual refit was created.
- **H64:**21,057 parameters; MSE slightly worse and IC markedly lower. Both IC intervals exclude zero in the unfavorable direction. Extra width and slightly larger forecast dispersion did not help here.
- **L2H32:**14,881 parameters; MSE worsens and IC is near zero/negative, with adverse differences in both block sensitivities. Output SD falls to about0.00954. Extra depth did not resolve compression.

The intervals use400 seed22042 calendar-month and two-month-block replicates. They are exploratory sensitivity intervals, not confirmatory p-values. No across-seed repeatability is established for any factor.

## Training and tail interpretation

| arm | parameters | selected | raw_best | stop | clipping_fraction | calibration_steps | refit_steps |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LRLOW | 6433 | 6 | 7 | 16 | 0.001643836 | 2528 | 1122 |
| DROP0 | 6433 | 6 | 7 | 16 | 0.003013699 | 2528 | 1122 |
| WD0 | 6433 | 7 | 7 | 17 | 0.002503129 | 2686 | 1309 |
| ES025 | 6433 | 2 | 12 | 12 | 0.002202643 | 1896 | 374 |
| H64 | 21057 | 5 | 6 | 15 | 0.00484115 | 2370 | 935 |
| L2H32 | 14881 | 1 | 7 | 12 | 0.002400384 | 1896 | 187 |

Measured clipping fractions are only about0.16–0.48% across these successful fits. Gradients and updates are finite. Neither clipping frequency nor bounded hidden/cell samples demonstrates saturation, vanishing gradients, or an optimizer defect. Training traces are online pre-update train-mode z-MSE; checkpoint validation is dropout OFF and epoch selection uses original TG20 MSE. DROP0 has no effective head dropout even in train mode.

All candidate development forecasts remain strongly compressed relative to target SD≈1.765. None crosses the frozen absolute-event prediction threshold, so event recall is zero. More dispersion alone is not improvement.

Refit ranked top1% contributes about7.15–7.22% of actual weighted z-MSE; ranked top5% about24.34–24.52%. The≥0.99/0.95 training-maximum magnitude ranges each contain one row and only about0.026–0.028% of loss. Thus the single maximum-range observation is not the dominant transformed-objective explanation. Numerator-only, small-MAD-only and both mechanisms remain separately available with their complements and provenance flags. These are in-sample checkpoint allocations, not trading evidence or additive RMSE shares.

Every model has22 exact refit witnesses: five largest weighted z-loss cases for each of AAPL/AMZN/TSLA/SBUX plus both/small-MAD representatives. They retain48 input plus4 future genuine hourly candles, all16 native/scaled features and independent all20 return reconstruction.

## Dashboard and engineering verification

Run `./scripts/run_track_a_dashboard.sh` and select **Explore → HF1M Long — Optimization & Capacity (P024)**. Use the actual free port printed by the launcher. All48 arm/view combinations, all20 stock histories, four roles, matched baseline overlays, eight protected query routes and prior sections were exercised. Model labels and candlestick boundary markers were checked from Plotly specifications.

A display-only schema mismatch (`volume` versus the source's audited volume fields) was corrected without changing any numerical file. The chart uses `observed_volume_sum`, colored by `volume_quality_tier`, with assumed-zero/lower-bound flags. The original failed UI test and the separate hashed correction are preserved. Final P024 tests:3 passed; preserved P022/P023 tests:4 passed; focused fitting/authority/math tests:39 passed (one reader test overlaps those suites). Full static check:369 files,0 errors,0 warnings. Ruff and diff checks passed. Native localhost health/HTML200 and clean shutdown passed on8502; existing8501 was preserved. No pixel screenshot is asserted.

## Preservation and next decisions

The original failed46 remains charged: two complete calibration epochs plus24 updates in epoch3 survived, totaling340 updates; incomplete optimizer/RNG/partial-epoch state was not a resumable continuation. The fresh47 run exactly reproduces both surviving epoch model hashes, selectors and losses. All five recovery starts are permanently completed and reject retries.

Frozen HF1M revision776328445b7ac6e7815ef3a483e9c8ded1eb6d56, P019B action/QA rules, P020 FT16/TG20 contract7adfec916b7eb74fead83ef1fe6082ff0fcee9ff0b6ebae5722077e2a82c01a5,20 names, dates, recipes, masks, costs and protected locks remain unchanged. Rights remain researcher-attested bounded private use, not independent licensing/clock/action-vintage certification. All1701 upstream raw/derived files remain hash-identical.

If pursuing ES025, first freeze a separately approved additional matched-seed design that has an informative selector discrepancy; saved seed42 already has matching raw/qualified epoch7 and is not an informative automatic replay. No such work is authorized now. Preserve the10+3 backlog, E1 seed123/calibration, QR1 seed123 and conditional-state variation, walk-forward, permutation/null and final-confirmation holds.

The work remains local and uncommitted. Refresh Pylance using the repository `.venv/bin/python`; editor Problems confirmation is human-owned and is not asserted by CLI parity.
