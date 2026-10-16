# Feature dependencies and independent oracles

3,216 source/model-input checks, 3,216 passed.
All16 channels and all5 stocks are represented. Fixed examples span AAPL's
2020-08-28/31 split basis,2020-12-09, both sides of2021-03 DST,2023-11-24 early
close and2024-06-28 archive edge. Additional family maxima are selected only
by |scaled feature|; no target correlation or importance scoring is used.

normalization_oracles.source_replay reads genuine immutable source windows of
at most91 dates per call, temporarily in RAM, through the last permitted example.
It independently combines the two source half-hours, derives full-session
daily closes/volumes including stubs, and separately streams EMA/Wilder state
from its actual first seed. No partial-history EMA seed approximation.
native_oracle independently checks hourly/daily RMS, momentum, older momentum,
bar shape, prior matching-slot/full-session volume ratios/pseudocounts, SMA,
signs, normalized EMAs and bounded RSI. M2 recomputes only matured historical
origin-matched price returns with nominal+3minute maturity, not new TG0 labels.

For each check, a **real original registered consuming forecast's48-step index**
is located. Its saved recipe is applied through CandidateView.row and the exact
real_bridge_data.build_view float32 conversion; the independent scalar transform
must match bitwise. Native equations tolerate relative/absolute1e-10, reflecting
independent floating summation/recursive state arithmetic. No windows are saved.
**Limit:** historical neural batches/tensors were not persisted. This verifies
the identical frozen constructor and registered masks/recipes, not a nonexistent
captured batch. Any material defect would HOLD its affected channel branch;
none occurred in these actual-input checks.

independent_feature_oracles.csv includes equations' values, identity and consuming
cutoff. feature_replay_examples.csv contains compact per-stock/channel/population
maxima with source lineage and recipe, not all feature arrays. Mathematical
synthetic cases cover floors, pseudocounts, all fallback branches and the disclosed
nonzero-constant rounding gap; synthetic observations never enter audit tables.

Large B1 values are genuine wide source high-low ranges divided by ordinary
positive recorded scales; no fitted degeneracy was found. T3's SBUX May2024
negative extreme replays from causal EMA state, including the genuine overnight
change, on the same retrospective split basis. Corporate action vintage,
economic explanation (earnings/news) and true historical publication remain
unverified: lawful price mechanics do not independently certify those facts.
