# Consolidated human review card

P4.6/P4.7 synthetic engineering complete; SCIENTIFIC_ACTIVATION_HOLD. MC0/MC1 human acceptance remains REVIEW_ACCEPTANCE_PENDING. Review these 14 checks once; no empirical activation is proposed.

| Check | Code / test anchors | Expected and observed |
|---|---|---|
| Authority/source/SYN permission | `src/lstm_data/regime_peer_audit.py:113` / `tests/test_peer_inputs.py:83` | 16 P2/33 P3/7 blockers;0/40; source hashes conserved |
| U2 median / U5 sign / exact equality | `src/lstm_data/regime_diagnostics.py:217` / `tests/test_regime_diagnostics.py:83` | U2=median LOW, U5=0 NEUTRAL; nonfinite and NaT reject |
| First eligible origin and episodes | `src/lstm_data/regime_diagnostics.py:237` / `tests/test_regime_diagnostics.py:153` | Missing days break episodes; first eligible anchor; origin vs session counts distinct |
| Support boundaries | `src/lstm_data/regime_diagnostics.py:237` / `tests/test_regime_diagnostics.py:177` | 29/3 sparse;30/2 sparse;30/3 descriptive support; NO_INFERENCE |
| MC2 valid mask and inclusive thresholds | `src/lstm_data/regime_diagnostics.py:320` / `tests/test_regime_diagnostics.py:91` | 11/46 fail;12/46 pass;12/48 pass; U1 never counts |
| 20 percent and20 distinct sessions | `src/lstm_data/regime_diagnostics.py:338` / `tests/test_regime_diagnostics.py:191` | 20/100 across20 pass arithmetic,20 origins over10 sessions fail; MC2_NOT_ACTIVATED |
| Paired outcome provenance | `src/lstm_data/regime_diagnostics.py:408` / `tests/test_regime_diagnostics.py:231` | MSE delta -1; mismatch/duplicate/unmatured reject; financial and approved rank metrics unavailable |
| Four peers/population dispersion | `src/lstm_data/peer_inputs.py:26` / `tests/test_peer_inputs.py:45` | z1..5: means3.5/3/2.5; SD sqrt1.25/sqrt2.5/sqrt1.25; equal peers SD0 |
| Permutation/own exclusion/caveat | `src/lstm_data/peer_inputs.py:26` / `tests/test_peer_inputs.py:57` | Own perturbation leaves own peers unchanged; others change; common addition can preserve ranks |
| Own-step completeness and publication | `src/lstm_data/peer_inputs.py:44` / `tests/test_peer_inputs.py:108` | Unknown/NaT/future/missing/source/order/scaler/market/grid all reject |
| Ephemeral48x23/reference storage | `src/lstm_data/peer_inputs.py:142` / `tests/test_peer_inputs.py:190` | Shape1x2x5x48x23; exact21 prefix; no neural23 model activation; mutation/rebinding reject |
| 147-prefix and161 sentinel lags | `src/lstm_data/peer_inputs.py:60` / `tests/test_peer_inputs.py:165` | 147 unchanged;14 lag-major mean/dispersion; positions47,46,45,42,36,24,0 |
| Matched ridge/P3 kernel/train-only fits | `src/lstm_data/peer_ridge.py:14` / `tests/test_peer_inputs.py:233` | Five penalties/free intercept/session weights/63 tail/one fresh refit reused; exact TG0 cohort/fit identities |
| Conservation/final quality/scope STOP | `src/lstm_data/peer_inputs.py:76` / `tests/test_peer_inputs.py:217` | CLI0errors/0warnings; Ruff/full pytest PASS;0NNpairs; SCIENTIFIC_ACTIVATION_HOLD; no Git integration |

Review only: accept or request changes to this synthetic prerequisite package. Genuine causal sources, training retention, action/fit/execution/course approval and actual paired evaluations remain unresolved. Further P4.8/P4.9/MC2/SP3 work needs separate scope. No stock switch, imputation, source download, new neural fit pair, empirical trading replay, confirmation or Git integration occurred. Existing synthetic portfolio and neural algebra scenarios ran only through the mandatory regression tests.

Final full suite: **556 tests passed**, 1472.59s; source/test SHA unchanged throughout. See checks.json for exact logs/commands and independent tests. Refresh Problems using .venv only as the final human editor check; CLI parity is separately measured.
