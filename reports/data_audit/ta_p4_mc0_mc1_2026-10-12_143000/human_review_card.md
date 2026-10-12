# Consolidated MC0/MC1 human review

**A/B/C engineering PASS (C corrected); SCIENTIFIC_HOLD; real fitting0/40.**
MC0 and MC1 use the same fabricated histories, preprocessing and mature TG0 population.
No historical A-E3/A-E4 batch, P4.3, MC2, P4.6, real source approval or Git action ran.

| Check | Expected | Actual / evidence |
|---|---|---|
| 1. Scope/permission | Fabricated only; real context denied | Negative tests pass; zero source/.env calls; checks.json |
| 2. Parameters | MC0 7073; MC1 +96=7169 | Exact constructors and hand_oracles.json |
| 3. Initial identity | Zero gate→16 ones; matched cores equal | Max score error 0.0; copied tensors only in identity test |
| 4. Temporal information | 48×21; historical m_s stays direct | Sentinel/order/peer-independence tests pass; no channel22 |
| 5. Endpoint gate | One m_t gate shared over five×48 | Historical perturbation leaves gate unchanged; endpoint perturbation spans all stock steps |
| 6. Market admission | Endpoint valid, ≥46/48 | 46 accepted/neutral zeros;45 and missing/late/unknown/NaT/stale endpoint rejected |
| 7. Source/fit clocks | Own-step availability and exact fits | Clock/version/order/source/mask negatives; novel training-constant values retain flags |
| 8. Gate constraints | Positive; sum16; tau1 | Independent exponential oracle; min/max/entropy/variance diagnostics; underflow fails closed |
| 9. Gradients/optimizer | Gate W/b/core nonzero; all params once | W norm 19.650480; b 8.904004; groups6896/.01+273/0; global clip1 within float precision |
| 10. Session math | Mean stocks→origins→sessions | Independent loss7; full19-session epoch MC0=9.0,MC1=9.0 |
| 11. D6g/refit | 63-calendar tail,50/25 guards; fresh selected duration | Both55 validation sessions; scripted selected1/raw2/stop12;36 calibration updates,7 fresh-refit updates each |
| 12. Checkpoint/P3 | Final-only, exact source/architecture/order | Both reload error0; one ordered five-score forecast each; cross-family/source/fit/code swaps refused; CPU boundary recovery passes |
| 13. Regression | All tests; basic parity0/0; Ruff/AST/diff | 512 passed in 828.30s (0:13:48); 112 Python files0 errors/0 warnings; remaining checks PASS |
| 14. Conservation/resources | Source/old tests/deferrals untouched; bounded output | 1130/1134 originals unchanged (four intended code/docs edits); original TM0 score error0;16 P2/33 P3 deferrals, ledger0/40; peak 379,224,064 bytes |

Current evidence: synthetic_final/synthetic_evidence.json and both final checkpoint
manifests. All three view IDs and both preprocessing IDs match across MC0/MC1;
architecture/pair/checkpoint/forecast IDs differ. Exact five scores and IDs are in
that JSON. Stock_only_conservation.json retains the tiny layout-dependent initial
roundoff and exact matched-layout replay. Earlier synthetic_release is superseded:
its forecast was blocked by code-version conservation after the novelty correction.

The integrated example deliberately uses a config-bound synthetic selection oracle,
not a real validation result. Actual finite losses/gradients are also recorded.
Two current seed42 pairs; one prior code-version MC0 draft. Seeds123/2026 were
constructor checks only. No predictive, financial-importance or economic claim.
Preprocessing dominates the measured 836.96s whole audit; individual
training times are in the per-architecture pair results, not a historical benchmark.

Review source math, clock provenance and this engineering package as one decision.
Source publication, action vintage, sample retention, real preprocessing, execution,
formal collaborator/course permissions and all scientific readiness stay HOLD.
Optional editor check: repository .venv interpreter, refresh Problems; no restart
requested and no fresh human editor count claimed. Integration requires separate
permission; STOP after review.
