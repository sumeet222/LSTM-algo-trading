# Track A SPY market-source amendment

Decision **TA-D2-MARKET-SPY-001**, version 1.0, 2026-10-11. Package TA-MKT-SPY-001.
**APPROVED_BY_TRACK_A_RESEARCHER / REGISTERED_BUT_ACTIVATION_BLOCKED.**

The explicit researcher instruction selects SPY (SPDR S&P 500 ETF Trust), obtained
from Alpaca historical stock bars with explicit SIP feed and raw adjustment, for
future Track A broad-market information. This local conversation attribution is
not an authenticated collaborator signature or retrieved instructor approval.
The machine-readable decision is [TA_D2_MARKET_SPY_001_v1.json](TA_D2_MARKET_SPY_001_v1.json).
Its hash-bound registration uses the existing evidence ledger's supported append API.

The shared specification requires course USA500, and consolidated D2/D7 prohibit
silent substitutions. This visible Track A amendment overrides only the future
market-source designation. Original USA500 investigations, their source HOLDs,
five governing documents, original course requirement and CURRENT_PROTOCOL remain
unchanged. CT-MKT-002 recorded a replacement direction with no chosen instrument;
this decision supplies the instrument for Track A. Track B USA500/USATECH and its
source decisions are unchanged. Formal applicable shared/course approval remains pending.

SPY is an ETF price proxy, not SPX/cash-index levels or a total-return benchmark.
It is an informational covariate, never a sixth prediction member, traded asset,
execution reference or free extra channel. Canonical bars use adjustment=raw;
ETF distributions stay in price returns and are never portfolio cash. Verified
splits would require consistent versioned adjustment before feature eligibility;
unverified absence of splits is not claimed. Market volume is excluded from U1–U5.

The selector [track_a_market_spy_v1.json](../../../configs/track_a_market_spy_v1.json)
uses ALPACA_SIP_SPY_RAW_30MIN_V1. The new source API defaults only to this selector:
missing SPY blocks, with no USA500/IEX/synthetic fallback. Original course CLI
commands remain explicit historical diagnostics. Native 30-minute bars are retained
once; existing XNYS aggregation derives 09:30-anchored complete hours and closing
stubs in memory. UTC is internal; ET supplies session displays. Publication time
is UNKNOWN, separately from known period ends and vendor left-boundary timestamps.
`asof` is symbol/entity mapping, never historical publication certification.

Frozen D7 §9.2 formulas and edge rules remain authoritative: U1 normalized hourly
log(C/O), U2 log absolute RMS60, U3 log RMS12/RMS60, preceding-session locked U4/U5
5/20-session momentum over sqrt(horizon) × daily RMS63. RMS12=12/12,
RMS60≥57/60 and daily RMS63≥60/63 with at most two consecutive misses; momentum
chains complete. Positive training p05 hourly/daily floors are separate from M2.
Training robust scaling counts unique timestamps once, uses median/unscaled MAD,
IQR/1.349 then audited SD; constant channels zero, novel variation flagged.
No hard clipping. A 48×5 history needs valid endpoint and ≥46 complete vectors;
neutral fills follow standardization, masks remain separate. Market age≤90 minutes
and each historical step's own publication cutoff are required.

Five target stocks, FT0=16, MC0=21, width32, 48 scheduled steps, TG0 median/unscaled
MAD and four-hour horizon, two morning origins, scheduled 240-minute holds, hourly
execution proxy and separate minute interface, C01 causal eligibility, chronological
splits, costs, conditional branches and 0/40 neural attempts are preserved.
No model, FT0, MC1/MC2 or portfolio engine is built or activated here.

SOURCE_SELECTED is distinct from SOURCE_VALIDATION_PENDING and MARKET_ARM_HOLD.
Archive OHLC/coverage QA cannot clear G0/G1/G2/G3. Applicable common sign-offs,
publication/as-of clocks, corporate actions, stock 168 half-hour gaps/four missing
dividend dates, as-of entity publication, sample retention, M2 floor cutoff and
remaining scientific gates stay open. Real SPY floor/scaler fitting needs a separate
approved preparation audit. A proposed next pointer is review material only; changing
CURRENT_PROTOCOL and migrating its ledger identity require separate human approval.
