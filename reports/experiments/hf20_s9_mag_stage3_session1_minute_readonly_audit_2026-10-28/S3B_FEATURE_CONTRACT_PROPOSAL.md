# S3-B minute-summary contract — UNAPPROVED PROPOSAL

Audit date: 2026-10-28. No feature values, normalizers, targets, forecasts or models were fitted. Full-path minute reads are **SOURCE_PERMISSION_BLOCKED** under the presently verified scope. This contract requires explicit researcher approval and source certification before implementation.

## Information window and source

Keep each exact original 48-step FT16 window, seven origins, complete20 primary panel, Design A roles, transformed magnitude objective and fixed 10-field CLOCK readout. Append the following **seven ordered scalar channels** to every completed full-hour row: future shape `48×23`, plus the unchanged head clock vector. Use the genuine, quarantine/action-compatible minute records within that very block only. No closing stub, overnight/weekend padding, current unfinished hour, price proxy, reconstructed minute path or target component is a minute observation.

Index the expected UTC minute starts within a full block by `k=0,…,59`; its interval is `[start,end)`. For positive finite source-validated OHLC, let `C_k` be the genuine minute close and `v_k` genuine finite nonnegative source share volume. Use `r_k=log(C_k/C_(k−1))` only for consecutive scheduled minutes `k=1,…,59`. The first close has no within-block predecessor: omit its return. Never bridge a missing minute or import the preceding session's last close. This deliberately omits the first minute's open-to-close change and any boundary gap; the original FT16 retains hourly open-to-close/volatility information.

`P=1` only for all60 genuine, unique, timely, source-compatible minute OHLC records; otherwise `P=0`. `V=1` only if `P=1` and all60 volume observations are genuine, finite, nonnegative and in one compatible as-reported share regime. An observed zero-volume minute remains observed. Missing/conflicting/quarantined records never count as zeros. Historical source quarantine labels and action classifications are provenance controls, not automatically causal model inputs; an explicit as-of policy must be approved.

## Ordered feature definitions

| ID / order | Native quantity | Validity / numerical rule | New distinction and overlap |
|---|---|---|---|
| MIN01_RV | `log1p(RV/h_(i,f)^2)`, `RV=Σ_(k=1..59) r_k²` | Requires `P=1`; `h_(i,f)>0` is the legal phase's existing hourly FT16 floor, never an OOS estimate. Preserve actual RV amplitude relative to a fixed historical scale. | Within-hour quadratic variation; V1/V2 use RMS of hourly net open-to-close returns and cannot recover this path variation. B1 range is related but insufficient. |
| MIN02_SEMI_CONTRAST | `(Σ r_k²·1[r_k>0] − Σ r_k²·1[r_k<0])/RV` | `P=1`; zero if RV=0. Bounded [−1,1]. | Direction of within-hour squared variation; avoids redundant positive, negative and total channels together. Not a future signed-return target. |
| MIN03_LATE_EARLY_ENERGY | `(Σ_(k=31..59)r_k² − Σ_(k=1..29)r_k²)/(Σ_(31..59)r_k² + Σ_(1..29)r_k²)` | `P=1`; zero denominator→0. Each half has29 transitions; crossing transition `r_30` deliberately omitted from this contrast only. | Ordering of variation within the hour, absent from FT16 V3's multi-hour short/long ratio and clock fields. |
| MIN04_EFFICIENCY | `abs(Σ_(1..59)r_k)/Σ_(1..59)abs(r_k)` | `P=1`; no movement→0. Bounded [0,1]. | Cancellation/roughness, not merely hourly direction or range location B2. |
| MIN05_LAST15_VOLUME_SHARE | `Σ_(k=45..59)v_k / Σ_(k=0..59)v_k` | Requires `V=1`; complete observed all-zero volume→fixed1/4 neutral share. Last15 **scheduled** minutes, never the last15 available records. | Intrahour activity concentration; Q1/Q2 represent hourly/daily volume level or ratio, not timing. No future daily volume denominator. |
| MIN06_PRICE_COMPLETE | `P` | Boolean from the approved timely observation mask. Never inferred from future label validity. | Identifies absence of minute-content evidence; distinct from normalized-zero FT16 fallback. |
| MIN07_VOLUME_COMPLETE | `V` | Boolean, `V≤P`; missing volume does not fabricate quiet trading. | Distinguishes unavailable activity from an observed volume path. |

`h_(i,f)` must be taken from the corresponding **initial or September-refit** input recipe. Division by this historical floor preserves relative absolute variation; it is not a within-window volatility normalization that discards all scale. No floor is estimated in this audit.

## Missingness, preprocessing and unchanged keys

Propose strict60 **feature validity**, not strict60 sample admission. On `P=0`, MIN01–04 are native-missing; on `V=0`, MIN05 is native-missing. Do not replace unknown returns with true zero returns. For future neural tensors only, replace invalid MIN01 by its unique-input-key training-prefix native median before robust normalization; MIN02/03/04 by fixed neutral0 and MIN05 by1/4. MIN06/07 remain zero. Use identity scaling on bounded/mask fields; use the existing median/MAD→IQR/1.349→populationSD→1 convention for MIN01, fit on legal valid input keys only. If a legal phase has no valid values, BLOCK rather than borrow a later normalizer. A constant phase must be declared, not silently discarded. No scaling, fallback or threshold is fitted on selector, calibration or outer-year feature distributions.

This proposal retains all original primary keys and lets the model know when extra information is absent. It does **not** establish that historical timeliness/quarantine masks are available in real time or that the full paths are currently accessible. Missingness can encode vendor era/ticker/source selection; do not interpret a gain as pure path information. Fallback/masks are new information and capacity as well as content. Validate invariance to arbitrary hidden placeholder values before future fitting.

A stricter no-missing-minute *sample* policy would change the main population and is not proposed as an automatic rescue. Audit sample intersections in the readiness CSV are descriptive only. Source-sensitive dates/stocks must remain in the frozen primary score universe.

## Redundancy and optional items

Keep all original FT16 M1/M2/M3/M4/V1/V2/V3/B1/B2/Q1/Q2/T1–T5. M2 uses previously matured same-context outcomes locked at the historical session start; it is not minute path information and must not be recomputed in this audit. Clock metadata describes origin/calendar structure, not within-hour price ordering. Avoid adding net hourly return, high/low range, close location, total hourly volume, both semivariances plus RV, or another hourly volatility ratio as purported new path channels.

Optional, **not part of the proposed seven**: maximum absolute consecutive-minute return concentration; a normalized first-half/second-half signed return contrast; zero-activity flag if genuine zero-volume evidence makes it necessary. These require source/degeneracy assessment and separate prospective inclusion. No target correlations or forecast errors may select them. No realized-return tail event is an input feature.

## Future fitting and costs, conditional only

One seed42 H32 model/fold, original M-space objective/selector, fresh September refit and its own independent C3 calibration κ25, versus saved CLOCK-C3/C0/C3. Seven input channels add `4·32·7=896` recurrent parameters: **7,339 total versus CLOCK's6,443**. Same clock head; new capacity is disclosed. Four starts/eight phases for S3-B alone require a later grant. Analytic recurrent multiply-add increase is about14.6%; this is not a measured runtime prediction.

Source support: see `minute_coverage.csv` and `unique_hour_metadata_summary.csv`. They are saved hourly-count evidence on a stratified sample, not numerical minute-feature validation. RV, ordering, observed zero-volume frequency, degeneracy, minute duplicates, price/volume positivity and minute-to-hour OHLCV reconstruction remain unverified pending full-path permission. **No feature implementation or fitting is approved by this proposal.**

Source-adapter prerequisite: qa_v2/canonical_observed is the pre-P019B action/quarantine canonical stream. Apply only the existing approved source/action rules compatible with adjusted hourly inputs after a read grant; do not assume an already adjusted full-minute tensor exists. Within-block log ratios are invariant to one constant positive split factor, but that does not waive quarantine, action-boundary, genuine-interval, volume-regime or publication checks. No such adapter is implemented here.
