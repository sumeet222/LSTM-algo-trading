# FT0 engineering API

Version `FT0:HOURLY_CLOSE_PROXY:v1` preserves the fixed order
`M1 M2 M3 M4 V1 V2 V3 B1 B2 Q1 Q2 T1 T2 T3 T4 T5`.
The additive [Q-volume decision](decisions/TA_P2_FT0_Q_VOLUME_001_v1.json)
records explicit researcher approval of the pseudocount placement. Frozen
documents and the protected protocol pointer remain unchanged.

`stock_source.load_stock_history` reads the existing immutable core-five archive.
`stock_features.FeatureCalculator` caches canonical rolling components and
composes the existing `m2.evaluate_m2`; it does not recompute target mathematics.
Source periods, native publication, action known-at and adjustment basis are
separate. A terminal stub contributes to legitimate daily metrics but never
becomes an hourly input. Each historical input uses its own information cutoff.

`ft0_transforms.fit_floors`, `fit_m2_floor` and `fit_scaler` currently accept only
explicit synthetic populations. Certificates bind canonical deduplicated keys,
source/action versions, feature dictionary and exact permitted training window.
M2 has balanced origin-type weights; the other13 scaled channel populations are
pooled across stocks. `B2 T2 T5` retain native bounds. No clipping is applied.

`ft0_tensor.stock_window` returns raw/scaled values, masks, reasons and lineage
at exactly5×48×16. Invalid cells retain `None` and their scheduled positions.
`join_market` reuses the existing D7 adapter and produces a separate48×5 object
on identical UTC steps. Eventual21-channel model width is metadata only; SPY
never enters the five-name universe. `forecast_bridge` has no exit, label or fill
arguments and rejects historical-training normalization as a live forecast.

`ASOF` requires fitted transforms already available at every step.
`HISTORICAL_TRAINING` permits explicit batch normalization of a lawful training
prefix without backdating fitted_at. The original M2 floor-versus-step guard
remains mandatory in both contexts; an earlier lawful M2 floor is a prerequisite.
These interfaces do not create a first empirical M2 floor from future data.

The [handoff](../../reports/data_audit/ta_p2_close_ft0_2026-10-11/market_stock_ft0_handoff.md)
and [feature dictionary](../../reports/data_audit/ta_p2_close_ft0_2026-10-11/ft0_feature_dictionary.json)
describe inputs and reproduction. Engineering is ready for human review.
Mechanical training retention FAIL and source/action/real-fitting/formal-approval
HOLDS prevent scientific activation. No P2.4 fitting, P3 execution, P4 training
or confirmation evaluation is authorized by this API.
