# Gradient and training health

**ASSUMPTION_CONDITIONAL candidate evidence:** retrospective AAPL/COST/CMCSA/SBUX/CME selection on2026-10-13 (formation reference2020-07-01), vendor adjusted-price/action/PIT uncertainty, researcher-attested local rights/shared clock with private evidence uninspected, idealized own-step zero-latency period-end availability and completed-hourly-close price proxy. SPY is an ETF state proxy, not certified course-USA500 substitution. No executable-fill, independent license/publication, causality, significance or production claim.

| Model | Calibration / refit epochs | Selected | First sustained clip warning | Last−selected inner MSE | Effective G6 |
|---|---:|---:|---|---:|---|
| E5 | 18 / 8 | 8 | cal 4, refit 4 | 0.127623 | WARN_INVESTIGATE |
| MC0 | 12 / 1 | 1 | cal 5, refit none | 0.078890 | WARN_INVESTIGATE |
| MC1 | 12 / 1 | 1 | cal 5, refit none | 0.042823 | WARN_INVESTIGATE |
| TM0 | 14 / 4 | 4 | cal 5, refit none | 0.072876 | WARN_INVESTIGATE |

All passes report zero nonfinite gradients. TM0 selected4 precedes warning5; MC0/MC1 selected1 precede warning5. E5 selected8 follows warning4 and its fresh refit warns at4–8. Late calibration warnings therefore do not mean the retained early TM0/MC0/MC1 states experienced those later updates. E5's retained final state does include warned refit epochs.

TM0's original runner reported refit-only PASS; that immutable historical field is preserved and the both-pass correction remains authoritative. MC1 raw validation minimum is epoch4, but its small improvement did not clear the frozen0.1% qualification rule, so selected1 is correct. No checkpoint was reselected.

`g6_four_model_epochs.csv` contains actual gradient median/p90/p95/p99/max, multiplier summaries, clipped fraction, nonfinite count, updates and train/inner loss plus saved output dispersion. Calibration/refit training is dropout-on; validation is dropout-off. Refit has **NOT_RECORDED** validation, not zero. Per-model final full-prefix evaluation is a different population/mode from historical dropout-on losses. Epoch Pearson matrices in epoch_associations.json are descriptive dependent trajectory summaries, not causal estimates.

**CLIPPING_CAUSE_NOT_IDENTIFIABLE_FROM_SAVED_BATCH_LOGS. CLIPPING_CAUSAL_LINK_UNRESOLVED.** The records retain per-epoch gradient quantiles/fractions and sampler fingerprints, not paired effective-batch loss, session membership and preclip norm. Even knowing the deterministic permutation cannot recover unretained gradients, dropout masks or intermediate weights. Final-weight gradient replay would not reproduce them; none was attempted.

Competing explanations remain: large-target batches, narrow global norm1 threshold, recurrent amplification, optimizer overshoot, fitting noise, overfitting or nonstationarity. Positive last-minus-selected inner loss is observed for all four models; it does not separate these hypotheses. No nonfinite failure or deterministic model defect was found in this sample. No rescue or hyperparameter change was performed.
