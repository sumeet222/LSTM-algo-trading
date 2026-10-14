# Provisional candle engineering API v1

The opt-in ordered profile is **AAPL, COST, CMCSA, SBUX, CME**, in Information
Technology, Consumer Staples, Communication Services, Consumer Discretionary and
Financials respectively. It is a retrospective data-usability proposal. The
original AAPL/JPM/JNJ/WMT/CAT universe, CURRENT_PROTOCOL, experiment registry and
scientific gates remain unchanged.

The genuine source census contains 16,261 main-period RTH half-hours and 1,736
prehistory half-hours **per stock**, with no missing records. Thus this profile's
engineering overlay inserts **zero** rows. All 89,985 observed records remain
genuine, while the *engineering view* remains quarantined from scientific use.
The source manifests reference existing archives instead of copying history.

```python
from pathlib import Path
from lstm_data.candle_cleanup import MODE
from lstm_data.engineering_profile import load_engineering_profile

selection = load_engineering_profile(
    Path("configs/track_a_provisional_engineering_v1.json"), mode=MODE
)
candles = selection.for_activity("CANDLE_QA")
geometry = selection.universe  # Existing universe-injected P3/P4 schema; no price permission.
binding = selection.cache_binding()
```

`MODE` is `ENGINEERING_CAUSAL_CANDLE_VIEW_ONLY`, distinct from the permissions
used by P3/P4 synthetic model tests. Only `CANDLE_QA` and `DATA_SHAPE` activities
are supported. FT0, TG0, T2, empirical fitting, forecasts and trading conversion
raise an error. The genuine-source validator rejects `engineering_only` and
`is_synthetic` markers even if DataFrame attributes were removed or there were
zero fills. No legacy genuine reader, hourly feature definition or model
mathematics was replaced. Profile/code/source SHA and universe order are bound;
later floor, target or preparation identities change the cache binding.

## Generic cleanup policy

`candle_cleanup.cleanup(frame, symbols, start, stop, profile_id=...,
source_binding=..., segments=...)` accepts an injected ordered universe of any
positive size. The canonical calendar is XNYS, with actual early closes and DST.
Optional per-stock `active_intervals` represent explicit listing/segment scope;
the current profile uses the entire fixed interval, without shrinking denominators.

For each missing scheduled 30-minute RTH key, choose the latest **genuinely
observed RTH** candle whose end is **strictly earlier** than the missing start.
Equality is rejected: a preceding candle ending exactly at the missing start is
not eligible under the user's selected rule. Later missing slots may acquire
that genuinely observed anchor once its end is strictly earlier. Synthetic rows
never become anchors. Extended-session records are preserved upstream and never
substituted as RTH anchors.

Synthetic O/H/L/C equal the genuine close. Volume, trade count and VWAP remain
null, with explicit unknown flags. A genuine observed zero volume remains zero
and is not flagged as a synthetic unknown. Cross-session anchors preserve wall
clock age and scheduled market-clock age; overnight and holidays introduce no
extra candles. Missing runs are recorded both within a session and across
consecutive scheduled RTH keys. Runs of any length can be displayed, including
entire sessions, with long-gap and terminal flags. No placeholder is a confirmed
trade, halt classification, executable opportunity, publication time or true
daily-close evidence.

`PriceUnitSegment` requires an explicit verified compatible-price epoch and
evidence locator before anchoring. Unverified units, crossing an epoch boundary,
or absence of a genuine strictly prior anchor produce unresolved rows. A vendor
`adjustment=split` signature alone does not independently certify an action
history. Current real segments remain unverified; they require no anchoring
because the authentic source grid is already complete. `CleanupView` detects
mutation of the genuine observed records before materialization.

## Evidence and rebuilding

The source and overlay bindings, exact fills/unresolved CSVs, genuine missing-key
census, scientific HOLDs and human review are in
`reports/data_audit/ta_provisional_source_integration_2026-10-13_163141/`.
The two overlay CSVs contain headers and zero rows because the **complete** source
grid has zero absent keys. Their source manifests, profile/code hashes and
reconstructed cleanup ID are in `candle_overlay_binding.json`.

Only a sparse overlay and small bindings are persisted. The reader reconstructs
the deterministic engineering view from SHA-verified genuine references and the
registered policy. It does not ingest an edited CSV as genuine provider data.
Changed source, ordering, policy or implementation requires a new profile/view
version and new evidence; previous outputs must remain intact.

The draft universe amendment records future rebuild dependencies. Genuine
FT0/TG0/M2/T2 admission, publication, actions, raw execution conversion, empirical
floors/scalers, matched populations and the 90% training-retention gate remain
unmeasured or on HOLD. Source coverage and a filled geometry prove none of them.
