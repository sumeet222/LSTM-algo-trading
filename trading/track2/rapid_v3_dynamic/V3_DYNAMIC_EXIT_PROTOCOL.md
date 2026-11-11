# Rapid V3 dynamic exit protocol

The 54 continuous USD 100,000 accounts use the frozen V1 entries, tickers,
physical order budgets (six per session micro and five per retail scan week),
retail USD 2,000 order floor, liquidity, costs and two-minute assumed receipt.
Conservative uses 0.85 of the eligible entry budget. Standard uses the full
budget. High risk uses the full budget with a 15% name cap. The other name
caps are 10%. The 20% vintage cap, 100% gross and net exposure ceilings,
restricted short proceeds and own-capital requirements are held fixed.
The absolute virtual gross ceiling also bounds physical net exposure.
Cap tests include reserved pending quantities and never revise a prior fill.

An accepted lot freezes the original signed signal, normalized strength,
feature lineage and relevant event reference. Actual filled inventory activates
the monitor. A pair activates once both legs are filled. Pending quantities
keep their reservations. The allocator never resizes an existing hold.
Unsent residual entry commitments can be released when an exit is required.
A standing order still follows the inherited next-valid-bar contract.
R05 also jointly tests the two combined physical requests against the
received participation and stale-price rules before either leg is submitted.

## Clock and trigger ordering

Micro uses legal V1 signal slots. M09 additionally observes 09:30 and 10:30
for existing holdings so the next session's received open and first-hour
segment can be monitored. M07 refreshes the score only in the corresponding
entry slot, with trailing checks at the other legal slots. Retail monitors
at the received 10:30 checkpoint of each full session, independent of its
weekly entry scan. Half days carry holdings under the risk and maximum clocks.
There is no use of the current day's final close at a morning checkpoint.

Mandatory priced risk reduction has first priority. A marked name-cap,
vintage-cap or other exact cap breach is typed separately. Preserve all
simultaneous exact cap and policy triggers. Ordinary priority is decisive
reversal, named event resolution, weakening, volatility trail and maximum.
An observed policy exit latches until a prospective eligible order can be
placed. The order uses a strictly later valid raw-share bar after receipt.
The missing-source flag records actual delayed settlement. Conditional
short availability supplies no factual recall series.

Reversal requires aligned z at most −1 (−2 for R05) on two successive
valid micro checks or one retail checkpoint. Missing observations reset
the streak at an eligible score refresh. Cross-sectional rules also require
an opposite top-four rank. Weakening requires aligned strength no more than
half the entry value and below the initial signal eligibility threshold.
For sign-only R01/R04 rank entries the buffer is exit from the original-side
top four and standardized aligned score below 1. Other cross-sectional
weakening rules also require leaving the top four. The weakening floor
is 60 scheduled minutes after actual micro entry or the same slot on the
next session for retail. Named resolution and decisive reversal can occur
earlier. A normal signal/event exit blocks the same name and side through
the next legal entry opportunity. There is no cooldown after a risk exit.

The past-only trail distance is two times prior completed-session V1 v20,
in split-consistent log units. R05 uses the frozen past beta to construct
the signed two-leg log spread and a conservative two-leg volatility
norm. R06 uses a frozen leave-one-out beta, fitted once per session
from up to 60 prior cached completed returns with at least 50 jointly
available observations and at least 11 peers. The trail fixes the entry
peer basket and abstains on incomplete received data. The V1 feature cache
does not export the pre-2021 beta history. The early R06 trail abstains
until this causal V3 warmup completes, while signal and risk exits remain
available. Missing pre-entry volatility likewise disables only the trail
and is counted. The favorable extremum starts with the received actual
entry proxy when supported, otherwise the first valid later checkpoint.
No intrabar high/low hindsight or assumed stop execution is used.

Micro maximum is 780 scheduled minutes after actual entry. Retail is the
same actual-entry Eastern offset on the tenth following XNYS session,
clamped to the close on a shortened target day. The maximum becomes due
after the two-minute receipt convention. Calendar admission assumes the
latest eligible entry minute and rejects the candidate if its maximum
order could not first become executable by the last authorized session.
Unexpected missing fills or marks are retained and can produce a HOLD.
The V1 nominal endpoint survives as a comparison, not an order target.

## All-ID score mapping

| ID | Received persistence and resolution |
|---|---|
| M01 | Own r60 z in the original direction. |
| M02 | Negative r60 z, with event resolution when the shock normalizes under the weakening test. |
| M03 | Signed distance from price to the frozen prior close, in initial gap-volatility units. Resolve when at most 25% of the initial aligned gap remains. |
| M04 | Log continuation beyond the frozen entry-day opening reference, scaled to the entry strength. Resolve on re-entry. Volume confirmation qualifies only the original entry. |
| M05 | Signed distance from the frozen opening range boundary, standardized by entry v20. Re-entry resolves. |
| M06 | Current residual z, original rank metric, minimum 12 peer support and top-four hysteresis. |
| M07 | Only matured same-clock z for the corresponding slot. |
| M08 | Negative r60 z normalization. The entry volume shock need not persist. |
| M09 | Signed remaining distance to entry-day open. Resolve at 25% of entry alignment. The first valid later session records prior-close, overnight and received intraday segments. |
| R01 | Completed-session log momentum standardized by past v60 and original duration, with rank hysteresis. |
| R02 | Completed 20/60 MA separation and .5 eligibility threshold. |
| R03 | Distance beyond the frozen prior channel level, with a 5 bp failure band. |
| R04 | Negative completed-session five-day score, scaled by past v60, with rank hysteresis. |
| R05 | Signed frozen-past-fit hedge spread z. Equilibrium is absolute z at most .5. Trail uses the hedged spread and unwind is atomic. |
| R06 | Negative completed five-day residual z and top-four hysteresis. The signed trail uses the past fitted factor hedge. |
| R07 | Frozen channel boundary, 5 bp failure band, distance trend and trail. Compression is an entry qualifier only. |
| R08 | Signed minimum aligned divergence of the two completed segment z scores. Absence of opposing segments normalizes the score to zero. |
| R09 | Completed-session volume anomaly score and top-four hysteresis. |

## Isolated later-reference diagnostic

Only after sealing the funded output, every filled virtual exit leg is
scored with its original signed quantity and actual raw-share modeled
fill. Partial fills are separate observations. Later marks are the first
valid raw open at or after the scheduled +60/+240 minute target or the
same slot on the next full XNYS session. An exact session-end target maps
to the next regular open. No later session is substituted when the
target session has no valid remaining mark. Censor unknown or outside-2024
targets and intervening corporate actions. Risk exits are labeled infeasible
under the original limit. No incremental carry or alternative portfolio
cash path is estimated. The diagnostic does not alter execution, budgets,
or thresholds. Its code is not imported by the funded engine.
