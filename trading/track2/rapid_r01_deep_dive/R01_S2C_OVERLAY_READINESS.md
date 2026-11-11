# R01 and frozen S2-C overlay readiness

**HOLD.** Directional evidence comes from a selected case in a reused
2021–2024 panel. Short contribution was negative, two names accounted
for more than total net, and risk/holding feedback dominated the H85
comparison. Confirm the R01 mechanism with a compact untouched-period
comparison before treating sizing as the next intervention.

## Proposed eventual test

- Freeze one R01 entry/exit and risk policy first. R01 raw J, sign,
  rank, scan and accepted opportunity lineage are the only directional
  source. Use a score-ready same-ticker same-origin key, never a legacy
  five-session direction, an auxiliary training head, future endpoint
  availability, or a later magnitude to backfill an earlier decision.
- The original S2-C C-A checkpoints F21–F24, O1/FT16 and CLOCK features
  and C3 emit a calibrated nonnegative magnitude for the absolute
  log return over 240 scheduled trading minutes. A V3 R01 lot can
  persist for ten scheduled sessions from actual entry. The sizing
  hypothesis is near-term exposure conditioning at formation. The
  magnitude has no ten-session variance interpretation.
- Run four entry-only allocation arms. EQUAL has g=1. Use
  g=clip(b/max(m,m_floor), 0.5, 1.5) in each risk arm, with the common
  original 2019 prefix reference per fold, ticker and slot. The floor
  is max(1e−6, 0.25b). Set m to C3 magnitude, rolling 60 matured
  240-minute median absolute movement, or EWMA .94 RMS as appropriate.
  Preserve the frozen initialization, strictly matured endpoint
  receipt, and minimum 40 observations of the original controls.
  Normalize the g weights across contemporaneously admitted same-vintage
  names to the common budget before existing caps and integer rounding.
  Preserve unused cash and use no size updates on held positions.
  A held-position risk policy would be a separate future experiment.
- Use equal start cash and identical prices, caps, exits, chronological
  constraints, borrow and commission. For matched support, freeze
  candidate keys with all four sizing inputs before independent
  account funding. Also report attainable per-arm input support,
  rejection and fill divergence. The alternative books can still take
  different realized paths after quantity is chosen. Pair results on
  common session and source opportunities. Do not choose the R01
  refinement based on a later S2-C result.

## Alignment evidence and dependency gate

R01 uses 10:30 ET on the first full XNYS session of each ISO week.
The same slot exists in the original seven-slot forecast schedule.
R01 decision is 10:32 ET under the assumed receipt convention, and
any order must precede its first eligible valid raw open. In the
historical input-only audit, 778 of 832 R01 candidates had the original
causal C3 magnitude at the R01 frontier. This census includes eight
candidates later excluded by the R01 terminal calendar rule. A missing
causal forecast produces an abstention for the magnitude arm. The
exact archive join checks UTC origin, issue, feature readiness and source
completion plus receipt, and validates partition SHA256 and the
reference identity. [Alignment receipt](R01_OVERLAY_INPUT_SUPPORT.json)

The 522 archived paired-control values with eligible C3 are a **lower
bound** on joint historical support. The archived control fields and
weights were masked by the legacy direction and neural input eligibility.
A null field can mean a legacy direction or neural mask. Build a
sign-independent classical readiness adapter from the already computed
causal movement tape and mature receipt fields before using R01.
Reconstruct g from C3 and the original b/floor. Preserve the archived
mask as provenance only. Check that mutating the legacy direction,
future outcomes, or future completeness does not change R01 eligibility.

Before any later run, bind the four original model/recipe/C3 hashes,
signal shards, fold mappings, 2019 reference, support adapter, calendar,
final direction policy and cost/position code. No inference or weights
were changed for this audit. For confirmation outside 2021–2024,
preregister the model version and inference authorization for that period.
Keep original weights and calibration frozen, and prove data readiness
with the new point-in-time inputs before measuring outcomes.

[Original signal protocol](../stage012/protocol_signal_layer_v2.json) · [Risk reference](../stage012/audits/completion_v1/historical_run_v1/RISK_REFERENCE_MANIFEST.json) · [Archived signal producer](../../../src/lstm_data/trading/track2/stage35/completion_v2/signals.py)
