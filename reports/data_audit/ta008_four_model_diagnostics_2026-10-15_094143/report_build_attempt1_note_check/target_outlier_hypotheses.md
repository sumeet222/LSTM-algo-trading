# TG0 denominators, tails and session loss

**ASSUMPTION_CONDITIONAL candidate evidence:** retrospective AAPL/COST/CMCSA/SBUX/CME selection on2026-10-13 (formation reference2020-07-01), vendor adjusted-price/action/PIT uncertainty, researcher-attested local rights/shared clock with private evidence uninspected, idealized own-step zero-latency period-end availability and completed-hourly-close price proxy. SPY is an ETF state proxy, not certified course-USA500 substitution. No executable-fill, independent license/publication, causality, significance or production claim.

TG0 is `(proxy_return − five-stock median)/(unscaled MAD + frozen epsilon)`. The denominator is additive, not max(MAD,epsilon), and the epsilon protects against more amplification. Canonical reconstructed targets match the actual float32 labels exactly for every audited legal origin. No target/floor was fitted, clipped or changed.

| Partition | Origins / days | Frozen epsilon | MAD=0 | epsilon≥MAD | |TG0|>20 rows | TG0 min / max |
|---|---:|---:|---:|---:|---:|---|
| inner | 1376 / 688 | 0.0002583601 | 0 | 16 | 11 | -32.1736 / 80.1641 |
| validation | 110 / 55 | 0.0002583601 | 0 | 4 | 0 | -8.5565 / 12.0400 |
| refit | 1502 / 751 | 0.0002509780 | 0 | 20 | 11 | -32.4256 / 82.0280 |
| WF1 | 232 / 116 | 0.0002509780 | 0 | 4 | 1 | -24.3999 / 15.9617 |

The floor dominates only20/1502 full-prefix training origins (1.33%) and4/232 WF1 origins (1.72%). There are no zero-MAD origins or MAD<epsilon/10 cases. Thus a pervasive zero-denominator bug is not supported. Severe outcomes can still arise from one large relative move when the other names cluster.

Post-hoc example2022-09-14 origin1: CMCSA raw proxy log return0.02158199 versus cross-sectional median−0.00446155; unscaled MAD0.00006651754, epsilon0.0002509780 and denominator0.0003174955 give TG0+82.02804. Without epsilon the amplification would be greater. This combines a large relative numerator with a small denominator; it is not an impossible raw return or a division-by-zero event. Prices are retrospective vendor representations, not certified raw cashbook returns.

Across refit origins, log(max|TG0|) correlates−0.6161 with log denominator and+0.4098 with log maximum relative numerator. The largest1% targets have mean denominator0.00058058 versus0.00329321 overall. These are descriptive algebraic associations, not isolated causal effects. Signed quantiles, raw-return quantiles, per-stock/origin/month cohorts and the worst labeled examples are retained in tg0_denominator_and_tail_audit.csv and severe_target_examples.json.

| Model | Partition / mode | Top1% share | Top5% share | Top10% share | Days |
|---|---|---:|---:|---:|---:|
| TM0 | validation / selected-cal eval | 7.95% | 20.37% | 35.77% | 55 |
| TM0 | refit / final-refit eval | 25.49% | 44.61% | 55.66% | 751 |
| TM0 | WF1 / final-refit eval | 15.66% | 30.69% | 44.62% | 116 |
| MC0 | validation / selected-cal eval | 7.39% | 20.22% | 35.93% | 55 |
| MC0 | refit / final-refit eval | 25.47% | 44.61% | 55.71% | 751 |
| MC0 | WF1 / final-refit eval | 15.71% | 30.95% | 44.77% | 116 |
| MC1 | validation / selected-cal eval | 7.38% | 20.21% | 35.91% | 55 |
| MC1 | refit / final-refit eval | 25.47% | 44.61% | 55.70% | 751 |
| MC1 | WF1 / final-refit eval | 15.71% | 30.95% | 44.77% | 116 |
| E5 | validation / selected-cal eval | 7.98% | 20.48% | 35.58% | 55 |
| E5 | refit / final-refit eval | 25.58% | 44.67% | 55.55% | 751 |
| E5 | WF1 / final-refit eval | 15.62% | 30.49% | 44.41% | 116 |

Origin MSE first averages five stocks. Each session then averages its eligible origins. Rank sessions by that loss, sum the largest `ceil(p×N)` and divide by total session loss. Top1% uses8/751 training days,1/55 validation days,2/116 WF1 days; top10% uses76/751,6/55,12/116. Stock rows are never independently ranked for concentration.

The final-evaluation loss concentration is real and shared by the four models: roughly25.5% in the largest1% training days and55.5–55.7% in the largest10%. WF1 top10% contributes44.4–44.8%. target_loss_overlap.json quantifies squared-target/error association and top-session overlap using retained predictions. These large losses are compatible with clipping, but historical effective-batch gradient causality remains unidentifiable. Inner dropout-on per-session losses were not retained and are NOT_RECORDED; evaluation-mode concentrations must not be mislabeled original training-batch losses.
