# Package 010C human review card

| Functionality | Status | Evidence |
|---|---|---|
| Complete signed/absolute target ranges and boundary validation | PASS | focused_pytest.log; numerical_oracles.json |
| 7,510 / strict >1:2,860 / strict >10:67; every page reachable | PASS | independent panel oracle; 58 pages/10 final rows for >1 |
| Stable selection, sorting, population reset and inline candles | PASS | actual AppTest with ordinary and extreme AAPL rows |
| Genuine OHLCV, both clocks, aligned volume, origin/maturity | PASS | direct exact-key Parquet oracle; calendar/DST/early-close tests |
| Full data date navigation and exact native/normalized/Both M1 | PASS | exact float32 arithmetic + source equality + AppTest |
| Out-of-preparation scope and unknown TGn fail closed | PASS | focused software tests |
| Confirmation selection locks before numeric readers | PASS | guard spies + actual AppTest; no unlock control |
| Legacy prices/predictions/diagnostics/provenance/refit/development | PASS | legacy_ui_smoke.json (8 actual UI cases), existing regression tests |
| Original raw/components/models/recipes/ledgers preserved | PASS | preservation_after.json; 887 original bound hashes unchanged |
| Ruff / installed Pylance / local launch+shutdown | PASS | ruff.log; installed_pylance.json; http_smoke.log |
| Native browser visual appearance review | HOLD — human review pending | Programmatic AppTest evidence supplied; screenshot not claimed |
| Editor Problems refresh | HOLD — human confirmation pending | Select repo .venv/bin/python, installed Pylance basic; restart language server and refresh Problems; expect 0 errors/warnings |

Confirmation remains locked; any future raw-price viewing requires separate affirmative
researcher authorization, an exploration audit record and holdout-plan review. This is
an intentional boundary, not an implementation permission request. Ledger remains 24/40.
No new scientific gate, Package012 experiment or D1 readiness is claimed.
