# Independent acceptance review

Status: **prefit supported with nonblocking findings; final run evidence pending**. This review uses the full `replication/EXPERIMENT_SPEC.md` and only NEW Phase 2 files. It supports the authorized independent **MODELING-LAYER** replication with audited **INHERITED** preprocessing. It does not certify independent raw-to-results replication, live tradability, or historical-result agreement.

The reviewer began with fresh context. No original source/tests/configs/reports, other Phase 1 documents, original market inputs, historical outcomes, Git or network were accessed. No model was constructed, trained, restarted or interrupted. Only these acceptance-review files are written. The exact-threshold check below was separately requested by the lead and read only newly generated `source_geometry.npz` R, `origins.parquet` dates and `roles.json` indices, with the Phase 2 boundary installed. The exit provenance writer was unregistered to retain the reviewer's two-file write restriction; file identities and arithmetic results are in the JSON.

## Prefit evidence and scope

The prefit acceptance is dated **2026-11-02T23:41:27.714932+00:00**, before the ledger's run start **23:41:37.706891+00:00**. It records 64 combined synthetic fixtures and zero real neural fits before acceptance. I directly checked all 18 frozen code/test hashes and all eight bound evidence hashes: every one matches. All eight actual initial/refit recipe files also match the no-fit preflight hashes. I inspected the new numerical implementation and the relevant independent fixture assertions. I did not rerun model-construction or fit fixtures during the active real run.

| Gate | Independent review finding | Evidence boundary |
|---|---|---|
| D0 | Supported under inherited scope. Exactly 348 unique literal paths, 174 months/family, July 2010–December 2024, all hashes recorded. Actual schemas distinguish genuine/proxy/absence/conflict/invalid/quarantine fields. Canonical revision, uniqueness and RTH calendar checks are explicit. | Receipt: 509,140 hourly rows; 33,296,542 canonical rows; 28,092,143 RTH. Bounded 284 stock-hours / 2,272 field assertions, zero failures, all 18 quarantines. Code selects all nine split ex-dates and preceding sessions, COP boundary, DST, half-day and missing/proxy cases. No whole-history independent raw QA claim. |
| A | Supported. Literal schedule, scheduled-minute endpoints, strict role maturity and embargo, 48 full-hour windows, previous full hour at opening, no stubs. Source admission is separate from future endpoint scoreability. | Explicit endpoint/frontier fixtures plus all 20 fold/role and auxiliary-support geometry checks. Genuine endpoints/auxiliary triple reconstruction uses separate references. |
| B | Supported. All 16 native formulas, seven M2 contexts and historical daily lock, minimum/triple-gap positions, prior-regular-day 15:30 and six-full-hour volume, volume regimes, floors/pseudocounts, unscaled MAD fallback, source-only unique unions and axes follow the specification. | Direct reference and state/reset fixtures, prefix future perturbation, 8 phase recipes, finite all-role tensor traversal and 89,600 fallback-incidence rows. Code review confirms current full-session values and future opens do not enter current features. |
| C | Supported. Signed common-mask triples, index-before-arithmetic NaNs, global Z, actual S/B and smaller last batch, 6,572 parameters, both recurrent biases, shared final dropout, zero state, exact fresh seed ordering, AdamW groups/clip and qualified selector/refit. | Reviewed implementation plus independent loss/gradient, direct recurrence, finite-difference, optimizer, RNG, inference invariance, selector and synthetic persistence fixtures. Real phase completion remains pending. |
| D | Supported for the authorized population, with AR01 below. Own unclamped q, effective-session shrinkage/kappa25, decoder clamp, original category weights, frozen identity and frontiers; scalar/EQ ratio, conditional-versus-rank hierarchy, fractional ties, tails and signed diagnostics are explicit. | Calibration/evaluation fixtures, keyed shuffled joins and synthetic replay. Real frozen checkpoints, score bundles, calibration coefficients and final report replay remain pending. |

The 29 completed provenance receipts inspected contain no original `lstm_data` module. Their only denied file opens are the deliberately nonexistent synthetic `FORBIDDEN_BOUNDARY_PROBE`. This supports procedural separation; it is not a claim of physical repository isolation or independent forensic proof of every session action.

## Supplemental scale/auxiliary frontier timing

The explicit external-future perturbation in `AUDIT_MATRIX_SUPPLEMENTAL.md` ran **after** prefit acceptance during the authorized fits. Its report clearly says that it is **not part of the 64 prefit fixtures**. This timing is honest. It holds lawful phase rows fixed, changes external future R/aux/masks, and obtains identical s, Z and weights; an intentionally unsliced sensitivity control changes.

The original prefit evidence is adequate structurally: strict independent role frontiers were tested; `prepare.run` fits s and auxiliary weights on `[ix]` from the admitted phase role; `run_experiment.phase` constructs `PhaseData` from those same sliced arrays; constructors never access the full original dataset. The original fixtures check the estimator mathematics, supported masks, global Z, S/B and target-scale precision. The post-prefit direct witness strengthens that combined proof but must never be retroactively described as prefit.

## AR01 — confirmed synthetic tail-quantile numerical edge, no actual-run effect

`evaluation.weighted_left_quantile` divides cumulative mass by its sequential cumulative final value. At exact mass boundaries, rounding can choose the following observation. Directly executing the frozen helper on values 0…599 with equal weights1/600 returns **570 at .95** and **594 at .99**, whereas the exact weighted-left answers are569 and593. For 40 equal weights the median similarly returns20 instead of19. This is a confirmed numerical edge in a general-purpose helper; the existing two-value median fixture does not expose it.

The lead immediately requested a read-only impact check before the next modeling phase. I used newly reconstructed restricted-refit role keys and R only. For each fold, all actual daily origin counts are1…7. With **L=LCM(1…7)=420**, assign integer cell mass `L/O_d`; the common `1/(S*20*L)` cancels. Stable-sort absolute R and take the first index satisfying `100*cumulative >= percentile*total`. Integer arithmetic avoids floating normalization ambiguity. I compared the exact result, the actual frozen evaluation helper, and the separate `np.sum(weights)` denominator implementation.

| Fold | p95 threshold, identical in all three methods | p99 threshold, identical in all three methods | Refit/OOS changed strict-tail memberships |
|---|---:|---:|---:|
| F21 | 0.029152683601565685 | 0.055591859892280306 | 0 / 0 |
| F22 | 0.029381635568292794 | 0.0550530573806432 | 0 / 0 |
| F23 | 0.030483335140690741 | 0.056214445055673128 | 0 / 0 |
| F24 | 0.030410684031328988 | 0.055872346745723445 | 0 / 0 |

All **eight actual thresholds match bit-for-bit**. Every refit and OOS `A>threshold` membership is identical. AR01 therefore has **zero effect on this authorized population's tail diagnostic thresholds or cohorts**. It does not affect feature fitting, s, auxiliary Z/S/B, neural training, selector, refit, C3, unconditional scalar metrics or ranks. The implementation remains frozen; no model retry or numerical edit is warranted by this finding. A future general-purpose correction requires a separately documented disposition, preserving this frozen run. Full counts, exact integer totals, index positions, values and input hashes are in `acceptance_review.json`.

The read-only numerical check completed successfully. PyArrow emitted sandbox-denied `sysctlbyname` CPU/cache-probe warnings; all requested new-artifact reads and calculations succeeded. No source data or model outcomes were consulted to choose a method or alter settings.

## AR02 — raw OOS inference order

`run_experiment` computes frozen raw OOS heads before fitting C3, while the specification narrates calibration followed by OOS inference. It constructs decoded/stored OOS scores only after calibration. The raw inference interface receives only X and CLOCK, the calibration estimator receives only its admitted calibration rows, and neither model selection nor coefficients consume OOS targets. I find no associated information leak or changed numerical outcome. Record the actual order and preserve the frozen run.

## Accepted residual limits and final checks

The known nominal-t versus assumed-issue-t+2 mismatch is retained. Retrospective action/quarantine vintage, unmeasured vendor arrival, exceptional-calendar announcement vintage, fixed survivor universe, future-endpoint complete20 scoreability, exploratory repeated-year use and inherited source QA remain explicit limitations. The modeling-validity audit's classifications are appropriately bounded; AR01 is an additional confirmed synthetic numerical edge with no realized effect. C0 deciles, comparator models/deltas and paired comparator intervals remain deferred. No historical outcomes have been unsealed for this review.

At the last run snapshot reviewed, F21 was complete and F22 refit was active. Missing later outputs were treated as **pending, not failure**. Final acceptance still needs the eight-phase no-retry ledger; selected/refit epoch and fresh-state receipts; own calibration/OOS full-key scores; exact checkpoint reload and report-only replay; final process RSS/new-output storage; and a manifest binding code/tests/import provenance/inputs/audits/role keys/recipes/checkpoints/coefficients/scores/metrics. The coordinator retains Git/session-report responsibilities; editor Problems refresh remains human-confirmed.

No newly confirmed severe leak, false association, wrong training weighting or unreconstructible target was identified. Final run completion remains a separate evidence check.

Additional independent phase-scale check: all eight stored initial/refit `s_phase` values equal the exact integer-hierarchy weighted-left median bit-for-bit. This uses only the same new geometry/role arrays, no model construction or fitting, and leaves numerical code unchanged. Per-phase values are in the JSON.
