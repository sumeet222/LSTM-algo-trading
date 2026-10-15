# Frozen WF1 context and WF2 development replication

| Fold | TM0 MSE | MC0 MSE | ZERO MSE | TM0 IC | MC0 IC | MC0−TM0 ΔMSE | MC0−TM0 ΔIC |
|---|---|---|---|---|---|---|---|
| WF1 | 5.438829600 | 5.450865550 | 5.427531844 | .034913793 | -.012068966 | +.012035950 | -.046982759 |
| WF2 | 7.631510203 | 7.647346744 | 7.628119050 | 0.050862069 | -0.022413793 | +0.015836542 | -0.073275862 |

ZERO WF2 MSE 7.628119050; project-conventional IC 0, defined-only IC N/A. Exact common panel: 232 origins, 116 sessions, 1160 stock forecasts, AAPL/COST/CMCSA/SBUX/CME, two origins per day. Neither arm has extra attrition. MC0−TM0 ΔMSE +0.015836542; Δdaily IC -0.073275862. MC0 has lower MSE on 48/116 days and higher IC on 49/116 (4 ties).

WF1 values are read-only references from Packages007/008; no historical baseline was refitted. WF2 uses a longer permitted training prefix and newly fitted normalizers/TG0 floor, so absolute losses across folds have different targets/populations and should not be interpreted as a fixed-label temporal change. Use each fold's own ZERO and paired arm contrast. Both folds have now been inspected for development. One seed, five stocks and two development folds cannot settle market-feature usefulness. Five-session paired block intervals in review_summary.json are exploratory, reuse the existing utility and are not full G8 or selection-adjusted significance.

ASSUMPTION_CONDITIONAL candidate preparation/pilot evidence: idealized zero-latency completed-hour period-end clock; retrospective split-price/inverse-volume representation and five surviving stocks; researcher-attested local stock/SPY rights/shared clock with private evidence uninspected; completed-hourly-close label proxy, not executable fills. SPY is an ETF state proxy, with no certified course USA500 substitution. No independent license, observed publication, action-vintage or PIT-universe certification. No redistribution authority. Production D1/CURRENT_PROTOCOL and confirmation outcomes remain unchanged.

Neither network beats ZERO in WF2 MSE: TM0 is +0.003391153 and MC0 +0.019227694 above its 7.628119050 reference. Both exploratory five-session paired95% intervals include zero: MC0−TM0 MSE [−0.026781253,+0.045731423], daily IC [−0.157758621,+0.039665948]. These are descriptive post-screen intervals without full G8/selection correction.
