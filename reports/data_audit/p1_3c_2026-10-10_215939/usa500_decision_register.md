# USA500 decision register — pending human/joint approval

| Category | Supportable statement | Limitation / disposition |
|---|---|---|
| Reported provenance | Instructor supplied CSV as Dukascopy export (user attestation); instructor permits later conventional S&P500 replacement. | Neither statement authenticates original export settings or amends frozen initial comparison. |
| Inherited local observations | UTC whole-hour labels, OHLC,29510 rows, observations outside XNYS hours, inherited source hash. | Reused P1.2 evidence; CSV not rescanned. Labels do not prove interval ends/publication or source daily close. |
| Provider context | P1.2D records USA500.IDX/USD CFD context at provider level. | Does not verify file instrument/side/export transforms or underlying historical-membership construct. |
| Unknown export contract | BID/ASK/MID, start/end side, source day boundary, original export time, first-release/revisions, pre-July2020 history. | Keep source-dependent gates BLOCKED; no default or vendor reverse engineering. |

## Conservative proposal, not an implemented scenario

1. With a documented genuine complete one-hour **start** stamp, period_end=label+1h; with a documented **end** stamp, period_end=label. Until validated, neither interpretation is a factual period end. Offline label+1h is only the latest possible end under an explicitly approved exhaustive start-or-end one-hour alternative; durations/gaps/export transforms can invalidate that premise. No :30 resampling/splitting of whole-hour OHLC, no synthetic stock-grid market bars.
2. Actual historical available_at is independent and UNKNOWN. No available_at=end, invented60-minute release delay or retrieval time is adopted. A future exploratory assumed bounded-delay scenario needs a finite bound with rationale, explicit approval/version, no immediate completion use, and stressed alternative delays. Scenario output must be excluded from verified-as-of claims. If no credible finite bound is supportable, keep joins blocked; a conservative-looking buffer alone cannot certify observability.
3. Both clocks use each step's own cutoff: end≤cutoff, available_at≤cutoff, and0≤cutoff−end≤90min. Later forecast issuance/availability cannot flow backward into historical steps. F01 logic is fixed; the diagnostic rejects hypothetical timing as usable and remains non-ready. A future scenario implementation, if authorized, needs explicit scenario output semantics; do not mark invented clocks documented to bypass it.
4. U4/U5 need an independently specified completed source trading day/daily close and its observability. Final UTC row, final ET row or16:00 ET is not an official CFD day definition. No daily close manufactured; U1–U5 production remains NOT_RUN/BLOCKED.

| Information arm | Exact risk / boundary |
|---|---|
| MC0 stock-only | Market series is not a model input, but primary comparison/matched information, formation/membership, stock timing and D3 remain unresolved. Not a blanket exemption or activation. |
| MC1 endpoint market | Endpoint must genuinely satisfy both clocks and approved complete U1–U5; unknown day definition blocks U4/U5 even if hypothetical hourly timing looks fresh. No retention PASS from arithmetic. |
| MC2 historical-step market (conditional) | Every historical step needs its own causal state; later endpoint copied backward leaks. Required46/48 market-state completeness/masks must be audited on approved source semantics; MC2 remains conditional, not activated. |

## Future versioned amendment options — none selected or acquired

| Option | Hours/availability/as-of/permission requirements | Comparability and collaborator implications |
|---|---|---|
| S&P500 cash index | Exact authorized vendor/index identifier, licensed historical OHLC, interval publication/revision and day-close semantics; prehistory and reproducible access. | Constituent membership history and Track B joint source clock required. Economic index differs from CFD; new data/protocol version, matched reruns, no mixing versions. |
| Liquid ETF proxy | Specific instrument not chosen; verify splits/dividends, trading hours/halts, bar publication, raw vs adjusted prices, source permissions/history. | Tradable security is an index proxy with tracking/distribution differences; explicit information-set/membership interpretation and Track B approval. No silent benchmark substitution. |
| Retained Dukascopy CFD | Exact course export contract, price side/hour/day boundary, finite publication evidence/approved scenario and prehistory/permission. | Preserve course comparison but remaining causal unknowns may make it unusable; CFD is neither cash index nor ETF. No extra broad documentation passes without instructor settings. |

All alternatives must freeze source version and matched dates/target/timing/costs/tuning, declare availability/retention differences and obtain collaborator sign-off. Later replacement cannot be attributed solely to model architecture or pooled with current-source results. Current course USA500 requirement, D1 conditional membership, Track B inputs and CURRENT_PROTOCOL remain unchanged.

**Decision if instructor cannot supply settings:** Keep verified-as-of USA500 modeling on HOLD unless the humans can jointly justify and record a precisely bounded exploratory timing/day-definition scenario in a versioned amendment; label all such results assumption-dependent. Separately plan the instructor-permitted conventional S&P500 migration under a new jointly approved source/protocol version, without substituting it into the current comparison.

The outstanding instructor request is the existing [three-question unsent inquiry](../p1_2d_2026-10-10_210500/instructor_export_questions.md): original export settings/label side/source day and any publication/revision or prehistory materials. No new email, web research or contact. **All provisional conventions PENDING HUMAN/JOINT APPROVAL.**
