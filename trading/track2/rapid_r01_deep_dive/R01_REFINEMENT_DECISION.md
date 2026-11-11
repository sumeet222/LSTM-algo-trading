# R01 refinement decision

**REVISE the risk-entry mechanism. HOLD S2-C sizing.** The first controlled
test should address vintage-cap feedback while preserving the executed
directional and exit rules. H85's historical advantage is economically
material in the recorded paths and concentrated in names, tails and
endogenous exits. A frozen H85 benchmark must remain present.

## One proposed modification

**H100 with a causal one-day vintage reserve.** At the weekly decision,
build the H100 eligible provisional dollar basket using the current allocator,
after name limits and before integer share rounding. For each new intended
notional uᵢ, compute a stress multiplier exp(v20ᵢ) from the same prior
completed daily log-return scale already used by the trail. Use the same
source-supported v20 rule. When v20 is unavailable for a new leg, abstain
for that leg before computing the budget. When an existing same-vintage
commitment lacks v20, admit no new commitments in that vintage and preserve
its existing orders and positions.

Let N be received marked NAV and R the original fee and buffer reserve.
For already filled and reserved same-vintage exposure, let A be the sum
of stressed absolute marked dollars using exp(v20) and L the sum of
notional times exp(v20)−1. Scale every new commitment by the largest common
t in [0,1] satisfying

    A + t Σ[uᵢ exp(v20ᵢ)] ≤ 0.20 × [N − R − L − t Σ[uᵢ(exp(v20ᵢ) − 1)]]

A negative available margin implies t=0. This is a joint conservative bound
on numerator expansion and denominator loss, with a fixed one-volatility
shock. It is not a fitted return expectation. Preserve integer rounding,
fee floors, ADV/volume limits, no redistribution, approved costs, conditional
borrow, vintage/name/aggregate hard caps and all prospective liquidation.
It changes new commitments only. Lower exposure and extra minimum-notional
rejects are foreseeable trade-offs.

## First controlled experiment

Run the unchanged H85 control, unchanged standard H100, and one guarded
H100 arm on identical prespecified untouched sessions and causal opportunities.
Keep the 10% name cap in each. Archive the 15% high-risk case and V1/V2
fixed results as context. Keep R01 rank, strength, scan, default exits,
trail, cooldown, capitalization and all execution conventions frozen.
Decide the sample dates and acceptable point-in-time feed before outcomes.
Require at least 52 scheduled weekly scans before interpreting the primary
comparison. Capture a compact per-decision audit of matched source identity,
accepted and rejected orders, quantities, NAV, own/free capital, restricted
proceeds, marks, name and vintage exposures, reserved dollars and which
cap tripped. Keep per-cohort gross, net, signed actions, all costs, durations
and cohort/order linkages. A bounded synthetic mark-shock test should show
that the reserve reduces new commitments while existing mandatory
liquidation remains operative. Check fee and dividend reconciliation.

Primary endpoints are vintage-risk exits per eligible weekly candidate
and net per marked gross RTH dollar-year, accompanied by gross per turnover,
filled counts, exposure, cash, all exit reasons and drawdown. Support
requires fewer vintage-forced exits per opportunity than H100, higher net
per gross dollar-year than H100, and positive aggregate net after costs
for the unchanged H85 control in the independent period. If normalized
net fails to improve, fewer liquidations alone do not support the change.
Report the two chronological halves, side attribution, and top-two-name
omission arithmetic. Treat an advantage confined to one half or two names
as fragile. These are advance descriptive decision criteria, with no
post-selection p-value or threshold search.

**Leave rank hysteresis and turnover gates unchanged in the first test.**
The archive had no R01 reversal closures and the entry-strength deciles
show no clean monotone economic edge. The matched ordinary-vs-risk subset
also contradicts a general lengthening rule. A separate exit study needs
precommitted evidence rather than a second change bundled with the reserve.

[Draft experiment registry](REFINEMENT_EXPERIMENT_REGISTRY_DRAFT.json)
