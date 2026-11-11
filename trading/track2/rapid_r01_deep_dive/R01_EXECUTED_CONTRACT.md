# R01 executed contract

R01 ranks **six-minus-one-month cross-sectional momentum** on 20 fixed survivors.
For stock i on session d, J is log(C[d−22] / C[d−126]), using two completed-session
closes on the same split-consistent price basis. The 104-session difference
also sets the normalization length. Cash dividends and special distributions
enter the accounting separately. The signal can retain ex-distribution price moves.

## Formation and funding

- The original menu specifies at most two positive longs and two negative shorts.
  The executed rule adds a current received raw-price screen, finite J and
  positive v60 support, and at least 12 eligible names. v60 is the sample standard
  deviation of the last 60 completed daily log returns with at least 48 valid
  observations. Rank by raw J within each tail, with fixed ticker-order ties.
  There is no positive magnitude threshold. Prioritize accepted intents by
  absolute J/(v60 × √104), then ticker.
- The scan is the first full XNYS session of each ISO week, slot 1 at 10:30 ET.
  The received 10:29-minute close confirms the current reference. Decision is
  at 10:32 ET, earliest modeled fill at the 10:33 raw open. Entry lifetime is
  ten wall minutes from origin, with the next-valid-minute rule.
- Re-evaluating the frozen feature cache gives 4,180 scheduled stock cells
  and 832 common candidates. Funding produced 498, 618 and 610 cohorts in
  conservative, standard and high-risk. The physical entry budget is five
  per ISO week. Whole-share rounding, USD 2,000 estimated minimum notional,
  prior received minute volume at 1%, short collateral, duplicate suppression
  and the calendar cutoff also apply.
- Allocation reserves 0.2% of NAV plus ready-ticket minimum commissions.
  Before rounding, B is the minimum of 20% of positive NAV after reserve,
  remaining gross room, and positive free capital after reserve. Divide
  H×B equally among ready intents and apply remaining per-name capacity
  and volume. H is 0.85 in conservative and 1 otherwise. The marked name cap
  is 10% in conservative and standard and 15% in high-risk. The marked
  vintage cap stays 20%, aggregate gross at most 100%, and absolute physical
  net bounded by gross. Restricted short proceeds are unavailable for new funding.

## Dynamic exits

R01 observes received 10:30 features each full session for existing holdings.
It uses aligned J/(v60 × √104) with the same raw eligibility and peer support.

- Mandatory marked risk has priority. A still-breached account submits
  prospective reductions across live lots, subject to executable capacity.
  Recorded cause is name first, vintage next, then other. This is an
  account-level reason and may apply to a lot whose own name was within cap.
  A reservation-only breach can clear after releasing unsent quantity.
- Reversal requires aligned z ≤ −1 and fewer than four names with lower
  aligned raw rank score, using one valid daily checkpoint. Weakening requires
  aligned z ≤ half entry strength, aligned z < 1 and four or more better-aligned
  ranks. It is permitted after the same actual-fill slot on the next session
  plus receipt. Missing data do not trigger reversal.
- Trail uses the favorable extremum of the signed split-consistent log price
  from received observations and fixed entry-time distance 2×v20. A breach
  triggers a later order at an observed price. Reversal, weakening, trail and
  maximum are prioritized in that order among simultaneous ordinary triggers.
  R01 has no named event-resolution exit.
- The maximum is the same actual-fill offset on the tenth following XNYS
  session, clamped to the shortened close where applicable, plus receipt and
  later execution. Calendar admission assumes the latest eligible entry.
  Signal reversal or weakening blocks same-name, same-side re-entry through the
  next weekly entry opportunity. Trail, cap and maximum do not start that
  cooldown. Existing lots keep their original shares except for action or exit.
- Orders precede their raw bar-open reference. Posting follows completion
  and receipt. Exit orders can wait for later valid RTH. Costs are 5 bps
  modeled price concession plus 5 bps impact, with adverse cent rounding,
  and USD 0.005/share with USD 1 minimum once per physical ticket. The
  price concession is split equally for reporting. Short borrow is 2% ACT/365
  on physical net short exposure, and funding is zero.

## Primary local sources

- [Original R01 menu](../../../HF20_Track2_Directional_Strategy_Research_Menu_Micro_and_Retail_2026-11-10.md)
- [Executed V1 registry](../rapid_v1/runs/rapid-v1-defaults-20261110-r1/results/EXPERIMENT_REGISTRY.json)
- [Signal evaluation](../../../src/lstm_data/trading/track2/rapid_v1/strategies.py) and [feature basis](../../../src/lstm_data/trading/track2/rapid_v1/shared_features.py)
- [Dynamic policy](../../../src/lstm_data/trading/track2/rapid_v3_dynamic/policy.py), [allocation](../../../src/lstm_data/trading/track2/rapid_v3_dynamic/decisions.py) and [engine](../../../src/lstm_data/trading/track2/rapid_v3_dynamic/engine.py)
- [Executed V3 registry](../rapid_v3_dynamic/amendments/20261110T232738967440Z.json) and [input identity seal](R01_INPUT_SEAL.json)
