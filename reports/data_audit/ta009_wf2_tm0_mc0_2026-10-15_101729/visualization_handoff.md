# Later visualization handoff — no app implemented

All links below refer to compact local review artifacts under this packet; transfer/redistribution remains separately unevidenced.

- `wf2_matched_predictions.csv`: session, origin, symbol, TG0, TM0, MC0, ZERO, grade. Join by exact session/origin/symbol; 1160 rows. Display model scores and realized labels with labels clearly future-only.
- `paired_daily_monthly.csv` and `paired_monthly.csv`: each model's MSE/IC and MC0−TM0 differences. `wf2_comparison.csv` gives matched denominator and score dispersion/ties.
- `training_curves_and_health.csv`: model/stage/epoch, train MSE, validation MSE, qualifying selection, step counts, score std, norm p50/p90/p95/p99/max, clipped fraction and nonfinite count. Preserve both passes and mark selection separately from stop.
- `batch_loss_vs_gradient.csv`: architecture/stage/epoch/batch/step, session IDs, effective session weights, MSE, preclip norm, multiplier, target max/p95/counts and largest session-loss share. Use log axes where appropriate; label repeated-epoch batch association as descriptive. `batch_association_summary.csv` supplies the fixed sensitivity summaries.
- `wf2_target_loss_tails.csv` and `loss_concentration.csv`: target tails and session concentration, with actual denominator and partition.
- `input_binding.json` and four new recipe JSONs: exact stock/market source IDs and retrospective transform metadata; `preparation_review.md` explains time boundaries and exclusions.

A later candlestick/volume/indicator viewer should retrieve authorized local bars through the existing component/source APIs using these source IDs and exact UTC/Eastern session clocks. The compact prediction files do not contain OHLCV. Do not invent candles or raw/unadjusted prices from normalized channels. Closing stubs, split representation, source/ideal availability, feature value time and forecast/label horizon need distinct UI marks. Existing U1–U5 definitions and 16-channel stock feature metadata are linked through the recipes and component binding. The historical retrospective representation is available locally; PIT action/publication facts and executable minute fills remain uncertified. No raw archive, dense window store, vendor GET, Plotly/Streamlit app or redistribution bundle was created.
