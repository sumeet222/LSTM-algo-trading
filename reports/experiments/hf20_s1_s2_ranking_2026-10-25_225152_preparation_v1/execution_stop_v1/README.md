# HF20 S1 + S2 — stopped execution and full diagnostic index

**STOP_S1_LP_CONVERGENCE.** Seven baseline fits completed, one failed. No annual OOS predictions and no neural starts. Ledger62/200. Do not retry under the prior approval.

| Stage | Status |
|---|---|
| 0 Source/protocol | QUALIFIED: unchanged verified sources/rights/vintage;1/8 prefix recipes estimated |
| 1 Rehearsal | PASS:33 tests;444 static files,0 errors/warnings |
| 2 S1 | FAIL: first LP numerical residual gate;7 completed/1 failed baseline attempts |
| 3 S2 | NOT_RUN: no start63 or neural update |
| 4 Diagnostics | QUALIFIED: only the four saved F21 inner P/LR exports |
| 5 Closeout | QUALIFIED: stop/preservation audit completed; full campaign NOT_RUN |

All readable reports:

1. [S1 detailed baseline results](S1_FOUR_FOLD_RANKING_BASELINES.md)
2. [S2 explicit NOT_RUN report](S2_FOUR_FOLD_LSTM_RANKING_COMPARISON.md)
3. [Detailed extremes, actual-objective and NUM/MAD diagnostics](RANKING_EXTREMES_AND_OBJECTIVE_DIAGNOSTICS.md)
4. [Attempt/selection/failure trace](TRAINING_AND_SELECTION_TRACE.md)
5. [Research decision and continuation limits](FINAL_RESEARCH_DECISION.md)
6. [Session handoff](WORK_SESSION_REPORT.md)

All machine analysis/evidence:

- [Selected inner metrics](partial_selected_model_metrics.csv), [complete cohorts](partial_all_cohorts.csv), [extreme examples](partial_extreme_examples.csv), [cohort stock/month/quality/fallback concentration](partial_tail_stock_month_quality.csv).
- [Independent stored-output reconciliation](partial_output_reconciliation.csv), [attempt events](baseline_attempt_events.csv), [stop/preservation receipt](STOP_AND_PRESERVATION_RECEIPT.json), [no restart authority](NO_RESTART_AUTHORITY.json).
- [Tests](tests.txt), [static checks](static_check.json), [Ruff](ruff.txt), [full artifact inventory](artifact_inventory.csv).
- Parent [live approval](../live_approval_full_campaign.json), [execution preflight](../execution_preflight_receipt.json), [runtime environment](../runtime_environment.json), [execution log](../execution_stdout.log), [original proposal](../proposal.json), [original preparation index](../README.md).

The inventory lists every actual file under parent F21_S1_P/F21_S1_LR/F21_S1_LP and this stop directory with SHA256: coefficients, selections, keyed scores and per-role metrics, origins, month/slot, stock/static-sector-proxy/quality/fallback, cohorts and thresholds. These are inner-only, not four-fold results. LP's folder has no accepted saved model. All other S1/S2 diagnostics are explicitly unproduced, never hidden behind a summary.
