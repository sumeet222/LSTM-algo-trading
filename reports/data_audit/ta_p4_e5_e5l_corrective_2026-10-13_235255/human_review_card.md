# Human review — corrective synthetic engineering

**P4.8_PARTIAL / E5_HEALTH_BLOCKED; P4.9_SYNTHETIC_ENGINEERING_PASS.**

| Fixture | LL0 held-out TG0 MSE | LL1 | Ten-session sham | Selected lambda (LL0/LL1/sham) |
|---|---:|---:|---:|---|
| NULL | 0 | 0 | 0 | 1.0/1.0/1.0 |
| FORWARD | 0.041100282 | 2.6605979e-09 | 0.041736638 | 0.1/0.0001/1.0 |
| REVERSE | 0.036375824 | 3.940078e-09 | 0.036663707 | 0.1/0.0001/1.0 |

| Check | Expected and observed | Exact evidence/code/test anchors |
|---|---|---|
| E5 proof | Both original inequalities still fail; no new 60-update fit | `src/lstm_data/e5_health_diagnosis.py:22`; `tests/test_directed_ridge.py:168` |
| E5 capability boundary | 7329 parameters; finite initial gradients; mature TG0 health absent | `src/lstm_data/e5_audit.py:72` |
| E5 final authority | Actual E5 D6g/refit/checkpoint/P3 forecast NOT_RUN | `health_diagnosis_final.json` |
| Human layout | 163/198 penalized slopes plus separate free intercept | `ridge_layout_decision_final.json`; `src/lstm_data/ridge_extension.py:33` |
| Prefix and lags | Exact 161 prefix, flags once, 35 lag-major tail; sham controls identical | `tests/test_directed_ridge.py:48` |
| Penalty oracle | Unequal day/origin weights; free intercept; repeated flags lambda/7 unequal | `tests/test_directed_ridge.py:87` |
| Formation | 300 exact causal fictional records; unique H/L; actual H/L unresolved | `src/lstm_data/directed_peers.py:101` |
| Antecedent | 49th exact scheduled full-hour source; no padding/stubs | `src/lstm_data/directed_peers.py:343`; `tests/test_directed_peers.py:166` |
| Sham clock/mask | Same stock/slot ten eligible sessions; current transform, original publication; all-arm exclusions | `tests/test_directed_ridge.py:115` |
| Actual fits | Forward/reverse/null; 5 lambda candidates and 1 fresh refit per arm | `tests/test_directed_ridge.py:185`; `src/lstm_data/directed_ridge.py:289` |
| Score limits | Five finite historical synthetic illustrations; no forecast/replay authority | `src/lstm_data/directed_ridge_audit.py:31` |
| Alternate order | Injected fictional names/order; no live-universe default | `tests/test_directed_ridge.py:153` |
| Regressions | 670 full tests PASS; 145 files types 0/0; Ruff/AST/diff PASS | `checks.json`; `full_pytest.txt` |
| Preservation | 1780 originals checked; 402 native source files and old packet unchanged;16/33/7/0 maintained | `preservation_final.json` |
| Next authority | P4.8 PARTIAL / P4.9 synthetic PASS; v2 health proposal unapproved; scientific HOLD; STOP | `e5_health_failure_diagnosis.md`; `package_report.md` |

Review the additive once-flag registration and matched ridge evidence. Separately decide whether to approve the proposed E5 chronology/TG0 fixture and 256-update cap; it has not been run. Scientific gates remain HOLD, 0/40, upstream human acceptance pending. No P4.10–P4.13, observed fitting/trading or Git integration is authorized.
