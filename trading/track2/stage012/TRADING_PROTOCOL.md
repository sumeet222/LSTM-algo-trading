# Track 2 Stage 0–2 protocol v1

The execution prompt of 2026-11-08 authorizes infrastructure only. `protocol.json` is the central review contract. No strategy performance inference is authorized.

| Decision | Authority/status |
|---|---|
| Track2, long and short, seven calendar-valid origins, original240 scheduled minutes | Human approved |
| Original annual C-A FT16/CLOCK/C3, fixed holding, no dynamic resizing | Human approved |
| Five-session trend, frozen for session | Proposed, unvalidated at this horizon |
| g=clip(b/max(mhat,m_floor),0.5,1.5) | Proposed; references unavailable; historical sizing blocked |
| Gross100%, net100%, name10%, new vintage20% NAV | Proposed; reject excess, retain unused cash |
| Assumed2-minute receipt;1/2/5-minute stress support | Proposed; not a vendor measurement |
| No stale reference fallback; entry expires nominal+5 wall minutes | Proposed conservative defaults |
| Shorts reserve100% own capital, proceeds unavailable for reuse | Synthetic reservation convention, not a broker margin claim |

Magnitude is endpoint absolute log return, neither sign nor conditional sigma. No auxiliary signed head is exposed. P_t is a label anchor, never a fill. No target shifting, retrospective calibration, Phase2 mixing, S5C substitution, architecture changes, paid data or later market observations.

Prior dates are the actual six completed XNYS sessions. Compare D[-1]/D[-6], not D[-5]. Early close without15:30 or missing last reference means abstain; no earlier full-session substitution under stale limit0. Session sign must be constructed once at the first eligible decision and reused. The low-level function does not persist a session cache; callers must supply that frozen sign. Adjustment basis and reference availability must agree.

All lots retain original endpoints. Capacity is conservative gross virtual exposure, even when physical shares net. Never assume five concurrent vintages is a universal maximum. Aggregate capacity and full-vintage sleeve allocation must gate entry; the per-name reservation primitive alone is not a completed allocation engine.

No actual trading-risk b/floor has been fitted. In its absence signals explicitly record RISK_REFERENCE_UNAVAILABLE and no executable intent follows. These parameters are distinct from neural feature floors and C3. Human review of defaults and a separately authorized prefix-only preparation are prerequisites for Stage3.
