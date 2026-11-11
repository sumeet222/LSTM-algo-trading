# V5 next-valid observed-bar policy

The current owner approved this general simulation policy before financial outcomes. The machine-readable execution_policy_v5.json is sealed into FINAL_CONSOLIDATED_PROTOCOL_V5.json.

## version

V5_NEXT_VALID_OBSERVED_BAR

## owner_authority

Current V5 owner prompt approves general next-valid-bar simulation; research-only 2021–2024 after substantive gates; no RSA or new chat approval

## order

Quantity, direction, prior-volume capacity, limits and source evidence frozen at submission. No future bar used in order formation.

## attempt

Standing order before actual RTH minute start. Valid original or sealed V4 raw supplement OHLCV only; no print reconstruction. Missing/invalid minutes leave order pending.

## entry

Actual effective start <= nominal origin +10 wall minutes. Expiry assessed after all eligible bar receipts; conditional simulation nonfill, not broker cancellation. Mixed entry/exit batch expires as a whole unfilled modeled order; entry remainder released; retained exit shares require a new prospective order.

## exit

No entry expiry. Inventory and carry/actions remain until qualified later observed minute, including next session; terminal unfilled exits HOLD.

## fill

Later bar actual open/time after completion+lag. Original submitted capacity retained, no future volume or hindsight risk rejection. Ex-post risk breach blocks subsequent new risk and invokes frozen prospective liquidation.

## posting

Bar[u,u+1), available/post u+1+lag; order strictly before u. Endpoint unchanged.

## valuation

Last valid received raw close; pretrade <=5 wall minutes. Daily held marks <=5 wall minutes or NAV_INCOMPLETE/HOLD. Pending nonfill alone does not make current inventory unknown under this explicit simulation; unknown material source/action still HOLD.

## partials

Whole shares; internal match first at common ex-post raw open; external net limited by frozen prior received 1% volume. Same order partials preserve cumulative fee; unsent target remains separate and may require a new order. No automatic capacity refresh from future bar.

## costs

Frozen V4 5+5bps adverse baseline, .005/share/$1 cumulative external-order fee, zero internal fee.

## outputs

Every journal row and output tagged V5_POLICY_VARIANT; journal tag included before hashing. Immutable V4 remains NOT_COMPARABLE strict diagnostic if unresolved.

## precision

Decimal kernel EPS1e-8; no weakened threshold

## special

All V4 corporate actions/OGN raw quotes and conditional settlements unchanged

## maximum_wait

Entry10wallminutes; exits until authorized terminal source bound, then explicit unresolved HOLD, no invented mark/fill

## planned_comparison

Four arms matched and attainable, independent same100000 cash, continuous2021–2024. No result-driven keys.

