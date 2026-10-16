# Interpretation addendum: floor activation and audit identity corrections

The active display manifest is display_manifest_final.json. It binds the resolved example CSV and symbol-qualified verified tail identity file; original outputs are preserved. One AAPL M4 boundary example used an origin-independent value consumed by origin2, while its first duplicate context was origin1. Only consumer metadata was resolved; native/scaled values, timestamps, scalers and population counts are identical. Pooled tail identifiers initially omitted the stock name; verified sets are exact unions of the five stock-specific sets, with all3072 group counts preserved and no duplicate identities. Fresh CLI runs generate qualified keys directly.

## Native floors are distinct from pooled feature MAD scaling

Measured development activation is informative but not proof of a broken formula. In WF1, the M3 daily RMS floor binds on26.68–61.05% of per-stock unique observations and the M2 origin-matched RMS floor on0–48.58%. In WF2 the corresponding maxima are24.22% and27.91%. V1 floor activation is16.31–30.32% in WF1 and8.53–15.70% in WF2. These are frozen training-percentile floors applied in later quieter regimes. Q1/Q2 are always additive-pseudocount log ratios; their maximum stock p99 denominator shares are about2.48% and1.70% in WF1,2.21% and1.62% in WF2. They are not max-denominator floors. See ft0_floor_activation.csv for exact stock/sample counts.

A rolling post-feature center/scale cannot recover distinctions already removed by a native RMS floor. N-V12 is therefore weaker than N-B1 and may remove meaningful absolute-volatility state. A future native-floor-policy experiment would change native feature definitions and needs its own approved causal floor schedule/population; it is not quietly included in N-V12. No stronger feature-MAD floor is supported by the current52 positive-MAD fits.

## Channel-by-channel assessment

| Channels | Measured interpretation / current action |
|---|---|
| M1 | Finite bounded-by-own-RMS mechanism, heavy MAD-unit tails; no input defect. Retain. |
| M2 | Correct50/50 origin fit; distinct hourly-vs-fit keys; later floor activation warrants context, no automatic rescaling. |
| M3 | Material daily-floor activation in quieter development; native-floor mechanism, not small pooled MAD. |
| M4 | Long-horizon regime/stock shifts; no degenerate scale. Retain pending a specific hypothesis. |
| V1/V2 | Development level drift and V1 floor plateaus; optional weaker causal rolling proposal with information-loss caveat. |
| V3 | Log-RMS ratio, algebraically linked to V1/V2; normalization does not resolve redundancy. |
| B1 | Genuine high-low range tails, stable positive scales; strongest limited amplitude-compression candidate. |
| B2 | Actual bounded identity, valid endpoint mass; retain. |
| Q1/Q2 | Already signed log ratios with small lawful pseudocount shares; no generic second log. |
| T1 | Moderate per-stock dispersion/temporal changes; evidence insufficient to prioritize per-stock scaling. |
| T2 | Discrete bounded mean signs; high repeated-value mass is expected, retain identity. |
| T3/T4 | Genuine causal EMA contrasts; isolated T3 SBUX tail is source-replayed, no numerical repair implied. |
| T5 | Bounded Wilder RSI, independent streaming replay passed; retain identity. |

No normalization was scored by supervised outcomes. Label/feature timing, historical publication/action/rights/PIT and untouched-confirmation limitations remain.
