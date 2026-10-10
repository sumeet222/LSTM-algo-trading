# Alignment diagnostic

[
  {
    "audit_only": true,
    "index_delay_minutes": 0,
    "stock_delay_minutes": 30,
    "stock_availability_policy": "start plus configured interval",
    "max_age_minutes": 90,
    "rows": 159008,
    "unmatched": 0,
    "stale": 2434,
    "usable_candidate": 156574,
    "age_minutes_quantiles": {
      "0.0": 0.0,
      "0.5": 30.0,
      "0.9": 30.0,
      "1.0": 300.0
    },
    "closure_policy": "Age bounded; overnight/weekend prices are never forward-filled. All source bars remain diagnostic; inspect RTH QA before interpretation.",
    "sample_policy": "all_native_source_bars",
    "researcher_assumption": "timestamp_as_close; provisional researcher approval 2026-10-10"
  },
  {
    "audit_only": true,
    "index_delay_minutes": 60,
    "stock_delay_minutes": 30,
    "stock_availability_policy": "start plus configured interval",
    "max_age_minutes": 90,
    "rows": 159008,
    "unmatched": 0,
    "stale": 1123,
    "usable_candidate": 157885,
    "age_minutes_quantiles": {
      "0.0": 0.0,
      "0.5": 30.0,
      "0.9": 30.0,
      "1.0": 240.0
    },
    "closure_policy": "Age bounded; overnight/weekend prices are never forward-filled. All source bars remain diagnostic; inspect RTH QA before interpretation.",
    "sample_policy": "all_native_source_bars",
    "researcher_assumption": "timestamp_as_close; provisional researcher approval 2026-10-10"
  },
  {
    "audit_only": true,
    "index_delay_minutes": 0,
    "stock_delay_minutes": 30,
    "stock_availability_policy": "start plus configured interval",
    "max_age_minutes": 90,
    "rows": 81137,
    "unmatched": 0,
    "stale": 0,
    "usable_candidate": 81137,
    "age_minutes_quantiles": {
      "0.0": 0.0,
      "0.5": 0.0,
      "0.9": 30.0,
      "1.0": 90.0
    },
    "closure_policy": "Age bounded; overnight/weekend prices are never forward-filled. All source bars remain diagnostic; inspect RTH QA before interpretation.",
    "sample_policy": "native_source_bars_inside_rth",
    "researcher_assumption": "timestamp_as_close; provisional researcher approval 2026-10-10"
  },
  {
    "audit_only": true,
    "index_delay_minutes": 60,
    "stock_delay_minutes": 30,
    "stock_availability_policy": "start plus configured interval",
    "max_age_minutes": 90,
    "rows": 81137,
    "unmatched": 0,
    "stale": 0,
    "usable_candidate": 81137,
    "age_minutes_quantiles": {
      "0.0": 0.0,
      "0.5": 0.0,
      "0.9": 30.0,
      "1.0": 90.0
    },
    "closure_policy": "Age bounded; overnight/weekend prices are never forward-filled. All source bars remain diagnostic; inspect RTH QA before interpretation.",
    "sample_policy": "native_source_bars_inside_rth",
    "researcher_assumption": "timestamp_as_close; provisional researcher approval 2026-10-10"
  },
  {
    "audit_only": true,
    "index_delay_minutes": 0,
    "stock_delay_minutes": 30,
    "stock_availability_policy": "explicit available_at",
    "max_age_minutes": 90,
    "rows": 43692,
    "unmatched": 0,
    "stale": 0,
    "usable_candidate": 43692,
    "age_minutes_quantiles": {
      "0.0": 0.0,
      "0.5": 30.0,
      "0.9": 30.0,
      "1.0": 90.0
    },
    "closure_policy": "Age bounded; overnight/weekend prices are never forward-filled. All source bars remain diagnostic; inspect RTH QA before interpretation.",
    "sample_policy": "session_anchored_hourly_with_stubs",
    "researcher_assumption": "timestamp_as_close; provisional researcher approval 2026-10-10"
  },
  {
    "audit_only": true,
    "index_delay_minutes": 60,
    "stock_delay_minutes": 30,
    "stock_availability_policy": "explicit available_at",
    "max_age_minutes": 90,
    "rows": 43692,
    "unmatched": 0,
    "stale": 0,
    "usable_candidate": 43692,
    "age_minutes_quantiles": {
      "0.0": 0.0,
      "0.5": 30.0,
      "0.9": 30.0,
      "1.0": 90.0
    },
    "closure_policy": "Age bounded; overnight/weekend prices are never forward-filled. All source bars remain diagnostic; inspect RTH QA before interpretation.",
    "sample_policy": "session_anchored_hourly_with_stubs",
    "researcher_assumption": "timestamp_as_close; provisional researcher approval 2026-10-10"
  }
]

Provisional course close assumption approved; final feature join unset.
