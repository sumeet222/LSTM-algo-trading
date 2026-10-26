# Rank-objective and original-TG20 extreme cohorts

The new linear score estimates normalized rank q=2(midranks(R)−1)/19−1. Actual fit loss is equal-session, equal-origin mean_stock(score−q)² plus λ||slopes||²; intercept is unpenalized. Reported rank error uses (midrank-normalized predicted score−q)², a distinct ordinal diagnostic. The row allocation is(score−q)²/20; multiply by origin weight, not an extra1/20. Saved row `weight` is origin_weight/20 and sums to1. Exact actual-loss/weight checks pass across all16 roles. There is no new asinh/original-return prediction, inverse transform or fictitious return MSE.

## Common target-key masks and thresholds

OOS [OBJECTIVE_AND_EXTREME_COHORTS.csv](OBJECTIVE_AND_EXTREME_COHORTS.csv) evaluates recent36 and expanding LR on identical keyed observations and weights. Every new fold also has `objective_cohorts.csv` covering inner_train, inner_validation, refit and OOS. The8 source-keyed bounded examples in [BOUNDED_MATCHED_EXTREME_EXAMPLES.csv](BOUNDED_MATCHED_EXTREME_EXAMPLES.csv) show one maximum-|TG20| and one ordinary median-|TG20| row per year, with recent/expanding scores/ranks and source-file SHA; no raw candle store is duplicated.

Original Y=(R−median20 R)/(MAD20 R+epsilon_phase). Top1%/5% uses descending |Y| in the evaluated role, deterministic ties by origin then canonical stock order, exact floor(n*p/100) rows. Complements retain ordinary observations. Positive/negative sides use the same selected rows and numerator sign, not independently selected marginal tails. Training event95/99:|Y| exceeds the saved applicable expanding-prefix train/refit95th/99th threshold. NUM:|R−median|>savednum95; MAD:raw MAD<savedmad05. NUM_ONLY/MAD_ONLY/BOTH/NEITHER are exhaustive disjoint classes; FLOOR=rawMAD≤epsilon. Thresholds are reused from saved LR, never estimated on OOS or monthly results. Thus both models use the same earlier-permissible cohort definitions; they are not recent-only threshold treatments. [COHORT_THRESHOLD_PROVENANCE.csv](COHORT_THRESHOLD_PROVENANCE.csv) records16 exact paths/SHA/values. Original full-prefix scaler/epsilon also remains intentionally shared.

Actual squared-rank loss and normalized ordinal-error contributions, row/stock weight mass, distinct origins/sessions and conditional means are reported. Weight mass need not equal row fraction under equal-session weighting. Cohort contributions reconcile for each top/complement pair, NUM/MAD partition and numerator sign partition. Shares are descriptive loss attribution, not causal gradient influence. Cohort intersections overlap where declared; do not sum all labels together.

Pair concordance excludes realized-return ties and gives predicted ties half credit. Each valid pair contributes half its normalized mass/credit to each endpoint; endpoint cohort masses sum to1 and concordant masses sum to overall concordance. This is endpoint-conditioned pair credit, not a new pair-loss fit or a partial-cross-section IC. There are at most190 dependent pairs per origin, not190 independent experiments. Every realized target/rank/weight and OOS key matches the saved LR source row.

## Same-key ordinal-error contribution contrasts

Negative means recent36 improves ordinal error. These contributions use identical original-Y masks for both models.

| year | cohort | LR | RECENT36_LR | recent_minus_expanding |
| --- | --- | --- | --- | --- |
| 2021 | ALL | 0.7209306 | 0.721278 | 0.0003474329 |
| 2021 | BOTH | 0.0003521292 | 0.001129944 | 0.0007778143 |
| 2021 | FLOOR | 0 | 0 | 0 |
| 2021 | MAD_ONLY | 0.01799302 | 0.01891795 | 0.0009249259 |
| 2021 | NEITHER | 0.6386262 | 0.6386481 | 2.190878e-05 |
| 2021 | NUM_ONLY | 0.06395918 | 0.06258197 | -0.001377216 |
| 2021 | TOP1 | 0.01614004 | 0.01675666 | 0.0006166173 |
| 2021 | TOP1_COMPLEMENT | 0.7047905 | 0.7045213 | -0.0002691843 |
| 2021 | TOP5 | 0.07318027 | 0.0749597 | 0.001779426 |
| 2021 | TOP5_COMPLEMENT | 0.6477503 | 0.6463183 | -0.001431993 |
| 2022 | ALL | 0.7389872 | 0.7377441 | -0.001243125 |
| 2022 | BOTH | 1.091658e-05 | 0 | -1.091658e-05 |
| 2022 | FLOOR | 0 | 0 | 0 |
| 2022 | MAD_ONLY | 0.01359115 | 0.01326911 | -0.0003220391 |
| 2022 | NEITHER | 0.6250181 | 0.6282699 | 0.003251777 |
| 2022 | NUM_ONLY | 0.1003671 | 0.09620512 | -0.004161947 |
| 2022 | TOP1 | 0.01490523 | 0.01425706 | -0.000648172 |
| 2022 | TOP1_COMPLEMENT | 0.724082 | 0.723487 | -0.0005949529 |
| 2022 | TOP5 | 0.06700326 | 0.06245377 | -0.004549485 |
| 2022 | TOP5_COMPLEMENT | 0.671984 | 0.6752903 | 0.003306361 |
| 2023 | ALL | 0.7273586 | 0.7283668 | 0.001008185 |
| 2023 | BOTH | 0.0002802293 | 0.0005057012 | 0.0002254719 |
| 2023 | FLOOR | 0 | 0 | 0 |
| 2023 | MAD_ONLY | 0.02459898 | 0.02317529 | -0.001423694 |
| 2023 | NEITHER | 0.6514052 | 0.6528756 | 0.001470402 |
| 2023 | NUM_ONLY | 0.05107421 | 0.05181022 | 0.0007360043 |
| 2023 | TOP1 | 0.01373124 | 0.01353475 | -0.0001964826 |
| 2023 | TOP1_COMPLEMENT | 0.7136274 | 0.714832 | 0.001204667 |
| 2023 | TOP5 | 0.06129292 | 0.0648747 | 0.003581782 |
| 2023 | TOP5_COMPLEMENT | 0.6660657 | 0.6634921 | -0.002573598 |
| 2024 | ALL | 0.742273 | 0.7308363 | -0.0114367 |
| 2024 | BOTH | 0 | 0 | 0 |
| 2024 | FLOOR | 0 | 0 | 0 |
| 2024 | MAD_ONLY | 0.02121434 | 0.01850416 | -0.00271019 |
| 2024 | NEITHER | 0.6611724 | 0.6508303 | -0.01034214 |
| 2024 | NUM_ONLY | 0.0598862 | 0.06150183 | 0.001615632 |
| 2024 | TOP1 | 0.01444786 | 0.01344913 | -0.0009987277 |
| 2024 | TOP1_COMPLEMENT | 0.7278251 | 0.7173871 | -0.01043797 |
| 2024 | TOP5 | 0.06461331 | 0.07141274 | 0.00679943 |
| 2024 | TOP5_COMPLEMENT | 0.6776597 | 0.6594235 | -0.01823613 |


The2024 total rank-error improvement−0.011437 comes from ordinary observations: top5 worsens by≈+0.006800, complement improves≈−0.018237. Top1 improves≈−0.000998, so the outermost1% and broader5% tell different stories. Actual rank-score loss worsens by+0.004720 that year. On original-Ytop5, recent endpoint concordance≈.4839 versus expanding≈.5230; total concordance improves≈.0040. A headline IC gain therefore does not establish improved handling of all extremes or both selection tails.

No floor-active or BOTH row occurs in2024; empty conditional means remain unavailable, not zero performance. See all years' actual counts before generalizing denominator effects. NUM/MAD/target/error operands are outcome-only audit fields, never features or eligibility inputs. Prior T2R-only z/original error/energy/common-centered diagnostics remain intact at [the original detailed report](../hf20_s1_s2_continuation_2026-10-25_204117/RANKING_EXTREMES_AND_OBJECTIVE_DIAGNOSTICS.md); they are not reinterpreted as new linear errors. No recurrent inference was run.
