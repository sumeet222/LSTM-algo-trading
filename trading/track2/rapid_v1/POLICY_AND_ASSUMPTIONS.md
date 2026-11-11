# Rapid V1 policy and assumptions

The 18 direction-only defaults use the owner menu and fixed numerical choices
in the registry. Each account begins with USD 100,000 and carries its cash,
inventory and accrued claims continuously across calendar years. Sizing is
equal notional within each current decision and observes V5 capital limits.
Retail scans the first full session of each ISO week, at 10:30 ET except R08
at 14:30. The micro and retail caps are six daily and five weekly external
entry orders. The retail entry floor is USD 2,000 per external order.

The underlying price observations are raw-share regular-session minutes.
Feature prices and volumes use causal split normalization. Receipt is modeled
as completion plus two minutes. An order stands before its next eligible bar,
which is used only after receipt. Entry expiry is nominal origin plus ten
wall minutes. Exit anchors use 240 scheduled XNYS minutes. Unresolved economic
exposure or an unavailable required mark is reported explicitly.

Micro fees are USD 0.002 per physical share plus the registered incremental
print slippage and size impact proxies. Retail uses the V5 five-plus-five
basis-point proxies and USD 0.005 per share with a cumulative USD 1 order
minimum. Borrow is 2% ACT/365 on physically net short exposure. Funding is
zero in the unlevered baseline. V5 retrospective ordinary and special action
assumptions, including MRK/OGN, govern ledger economics.

The period is reused exploratory research on fixed surviving names.
Publication and action vintages are retrospective. Receipts, short availability
and friction are scenarios. The bar open is a simulated execution proxy.
Signal-quality diagnostics have separate price-only denominators and score
only after the actual modeled bar receipt. Reported addbacks are arithmetic
on the same holdings. Stage 6 independent evaluation is outside this screen.
