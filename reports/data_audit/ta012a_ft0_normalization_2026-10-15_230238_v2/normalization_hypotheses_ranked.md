# Normalization hypotheses ranked — proposals only

All52 scaled-channel fits use MAD; all12 bounded recipes use identity. No current scale is degenerate; no bounded violation or input mismatch was found. A three-MAD event is not a three-standard-deviation event. Heavy tails alone do not establish bad normalization.

- WF1 B1 development: max 20.7429, |scaled|p99 6.01053, >10 rate 0.216%, N=3710.
- WF2 B1 development: max 25.0409, |scaled|p99 7.19429, >10 rate 0.325%, N=3695.
- WF1 V2 development: median -1.2626, IQR 1.35696 in original pooled training-MAD units.
- WF2 V2 development: median -0.807365, IQR 1.51171 in original pooled training-MAD units.

These are measured dynamic-range and regime-shift mechanisms, not instability
proofs. Per-stock IQR dispersion differs moderately (e.g. T1/T4), while B1
stock IQR/pool ratios are about0.89–1.17. No single stock owns all range tails.
Feature dependence is reported separately: normalization cannot remove the
algebra V3=V1−V2, EMA horizon dependence or establish causation.

## Restrained future 012B matrix

1. **N-B1 monotone tail compression (first candidate).** Hypothesis: rare genuine
   wide ranges dominate B1 input amplitude; compressing only this channel reduces
   leverage while retaining order. For native x=log(H/L)>=0, propose
   q=asinh(x/s_train), s_train=median strictly-positive native B1 on the same
   pooled training keys, followed by a freshly registered train-only robust
   center/scale of q. Inner and refit each have their own recipe. This deliberately
   adds a second transform to a log range; it is justified only by measured tails,
   not a generic log of already logged features. Desirable effect: lower rare
   amplitudes without hard ties. Harm: compression may remove useful volatility
   contrast and changes derivatives. Compare original C0 vs B1-only treatment;
   leave all other15 channels, TG0 and training protocol fixed.
2. **N-V12 causal rolling normalization (second, weaker candidate).** Hypothesis:
   measured V1/V2 level drift makes a long pooled prefix center less representative.
   Propose z=(x−median_past60sessions)/(max(MAD_past60sessions,0.25*a_train)) only
   for V1/V2, pooling the same5 names on unique prior full-hour keys strictly
   before t. The60-session horizon and0.25floor are proposed predeclaration
   choices, not tuned or approved here. Need complete prior coverage, explicit
   warm-up/failure rules, original native floors, exact per-step cutoffs and
   no fit on later observations. Desired: stable local level/dispersion. Harm:
   erases persistent volatility state/cross-stock contrasts and may amplify
   quiet regimes; V3 is deliberately unchanged as a one-block test. Compare
   C0 vs V1/V2-only normalization, no target transforms combined.

No active variants, alternative scalers or transformed input stores are created.
Human 012B approval must freeze hypothesis, causal population/recipe identities,
primary metric (suggest existing equal-day Rank IC with canonical MSE guard),
failure/go-no-go criteria, seeds, matched budget and multiplicity plan before
training. No pair reservation now. Preserve original C0 plus two independent
one-factor variants; do not combine them in the first comparison.

Per-stock scaling is lower priority: heterogeneity exists, but its magnitude
does not alone outweigh losing common peer-comparable units. Q1/Q2 are already
signed logs with lawful pseudocounts; V1/V2 are already logged RMS, so another
generic log is unsuitable. Retain B2/T2/T5 identity absent measured pathology.
No stronger MAD floor is supported by the52 current fits. The synthetic constant
fallback discrepancy needs separate engineering review, not retroactive input
or model edits. Five-stock cross-sectional normalization risks unstable MADs,
same-timestamp availability and selection/cohort effects; do not add it now.

WF1/WF2 have been examined repeatedly. Any selected variant and later score
comparison on them is exploratory, not untouched confirmation or selection-adjusted
evidence. No input variant was ranked by target correlation, model scores or P&L.

## Separate target-normalization handoff

TG0 remains (future4h return−five-stock median)/(cross-sectional MAD+training
epsilon). It is separate from FT0 historical RMS/pooled feature MAD. Package010C
already preserves the small-cross-sectional-MAD examples and exact TG0 ranges;
reuse its bound examples rather than constructing new labels. A future target
study needs its own hypothesis/population/maturity/units and inverse-evaluation
rules. No target variant, T2 combination or automatic 012B activation here.
