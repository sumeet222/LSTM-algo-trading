# Track 2 approved implementation scenarios, V2

This successor leaves V1 and Stage012 bytes unchanged. The current prompt approves these engineering conventions; it does **not** approve historical financial execution. Central signal policy: `protocol_stage35_completion_v2.json`. The external signed financial release remains absent.

|Item|Candidate convention|Status|
|---|---|---|
|Model|Original F21–F24 C-A/O1/CLOCK/C3; main magnitude only|Inherited frozen|
|Direction|D[-1]/D[-6] adjusted 15:30 references; first input-eligible decision freezes sign or abstention; no stale substitutes|Approved hypothesis, not proven alpha|
|Origins/horizon|All actual XNYS hourly origins; exact 240 scheduled minutes; no after-close origins|Frozen|
|Receipt/inference|Assumed nominal+2 wall minutes, actual later dependency readiness dominates; zero compute duration|Unmeasured scenario; 1/2/5 supported|
|Expiry|Nominal+10 wall minutes|Supersedes V1 +5 only in new path|
|Fill|Submitted strictly before next regular minute start; finalized raw open observed later, then posted|OHLCV proxy, not NBBO/broker evidence|
|Costs|5bps half-spread+5bps impact per external side; $.005/share, $1 cumulative minimum/order|Assumptions, not measured averages|
|Stress|Spread/impact 1/5/15bps; fee 0/.005/.01, minimum 0/1/2|No historical economic sweeps run|
|Participation|1% of already received prior minute volume; missing volume blocks submission|No fill-bar volume in pretrade decision|
|Shorts|CONDITIONAL_ACADEMIC_SHORT, 2% ACT/365; 1/5% stress|Human-approved assumption only; STRICT_LOCATE still fails|
|Caps|20% new vintage, 10% aggregate ticker, 100% virtual gross and absolute net; pending included|No short-proceeds recycling|
|Mark age|5 wall minutes for pretrade marks|Not a fill processing-age rejection|
|Holding|Original cohort horizon; new forecasts never resize old lots|Dynamic resize/rebalance rejected|
|Controls|EQUAL=1; rolling60 median, minimum40; EWMA .94 RMS initialized earliest window squared magnitude|Strict known-missing support; no future maturity|
|Scale|clip(b/max(scale,m_floor),.5,1.5), common frozen 2019 b/floor; S2C uses calibrated magnitude|No LSTM/recipe/C3 fitting|

The orchestration layer reserves a conservative estimate of known candidate costs **before allocating new risk**: `n*$1 + .005*(.20*NAV/min_current_price) + .001*(.20*NAV)`. It reduces the new allocation's NAV/cash capacity, then applies the unchanged caps and integer rounding. This derived reserve deliberately double-bounds some fee terms; it is an auditable conservative implementation convention, not an optimized capital model or forecast of a future gap. It cannot resize existing lots. Unknown future gaps are booked first and then trigger prospective risk holds/liquidation intents.

A full rolling window includes the last60 scheduled, matured same-slot observations; a known missing observation makes that window unavailable, preserving the prior Stage35 strict-missing contract. It is not retrospectively replaced by an older successful observation. Before60 observations exist, at least40 are required. No interpolation/pooling. EQUAL/S2C do not require classical control availability. All arms otherwise use the common original input/sign eligibility; paired and attainable universes are recorded separately.

No discretionary margin leverage or positive-cash remuneration. Forced gap deficits are explicit liabilities, not free capital. Borrow is on physical net short shares, never the sum of virtual shorts. Fees accrue until explicitly settled; uncertain dividend payment dates remain undated claims and HOLD.
