# P028 C3/S3 reference reconciliation

Reference: docs/track_a/Recurrent_Architecture_Research.md, especially§6 A6 and§13.3 C3. The newly supplied document resolves the missing-reference blocker. It is research background, not approval of another architecture, source, fit or set of numerical widths. No separate formal S3 equation was found; P028's C3/S3 wording is reconciled to the actual C3 equations and self-contained work order, not an invented extra variant.

| Topic | Supplied C3 reference | Retained P028 proposed A8 |
|---|---|---|
| Common inputs | m_s plus learned masked phi(x) pool p_s | Exactly the authorized two proxy channels m_s; no additional pool/phi |
| Feedback | Previous mean local hidden state enters global cell | No local-to-global feedback |
| Global update | Once per historical step, before local updates | Same triangular global-before-local order, once per step |
| Widths | Symbolic G,H,q, not frozen HF20 numbers | Proposed G8,H32,q0; global input2/local input24 |
| Reset | Causal recurrence, history policy explicit | Zero global/local h,c per48-step window, no cross-window memory |
| Rank mechanism | Shared g changes local gates jointly with own x/h | Same nonlinear local input path, not common additive output offset |
| Interpretation | Two-way model communicates current pooled stock data and prior local memories | Market-only, one-way C3 reduction; no claim of full two-way C3 recurrence |
| Functional caveat | Market-only global stream can be duplicated with tied per-stock computations | Efficiency/organization hypothesis, not a new information/function class theorem |
| Parameters | Equations use a single bias vector per gate/candidate | PyTorch uses two bias vectors; actual proposed component count7,841 |
| Labels/feedback adaptation | Matured outcome feedback is separate research | No labels, prediction errors, delayed-label adaptation, or E1/QR1 fusion |

The reference's illustrative A7 is final-state spatial mixing, whereas P028 A7 is MC1. Its A6 global/local name is not P027 A6 attention. Package-qualified names prevent accidental substitution. Its parameter-matched/rich-input controls and sector/pooling/feedback research suggestions remain deferred; no extra comparator fit is authorized. Its warning that pooled summaries discard individual innovations still applies.

Scientific decision still needed: accept the proposed one-way market-only A8 as the intended bounded experiment, or request a separately scoped revision. Do not silently turn it into the reference's full feedback/pool architecture. Existing proposal unchanged; current audits do not approve it. A same-input plain18-input LSTM is absent, so mechanism-only attribution remains UNIDENTIFIED for all three new arms.
