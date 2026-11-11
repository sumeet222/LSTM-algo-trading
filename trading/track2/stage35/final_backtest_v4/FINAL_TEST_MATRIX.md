# Final test and gate evidence

Code/test fingerprint: `e61bd23fd232`. No code changed after the certified commands. The complete Track2 owned regression and original neural IO tests report **234 passed**, no skipped/XFAIL additions. The pre-change baseline was 197 passing tests. Certified pytest runtime was 58.62 seconds (wall command 59.74 seconds). Ruff E/F/I passed in .02 seconds; new owned type analysis covered 19 files with zero errors/warnings. Full installed Pylance basic analysis covered 681 files and reports **27 errors, zero warnings**, all in preserved Phase2/Phase3 files. This is a repository HOLD, not a globally clean report. Earlier full-check receipts included transient Plotly viewer-test diagnostics; the final fresh check reproduces the 27 frozen diagnostics. No viewer/replication repair was made.

| Acceptance scope | Evidence / result |
|---|---|
| A01–A02 originals/universe/control counts | Source-only preflight reproduces 140,280 opportunities / 131,111 forecasts / 87,557 matched; no neural refit or Phase2 substitution. |
| A03–A04 clocks/sign/fixed holdings | Existing regressions plus V4 receipt/order barriers, nullable per-arm eligibility, indexed calendar equivalence, future mutation and fixed lots. PASS tests. |
| A05–A07 raw/actions/MRK | Original raw source lineage, issuer PDF/SEC and actual OGN/MRK observations; signed claims, account fraction, deferred close reference, conditional settlement/basis tests. PASS conditional. |
| A08 crossing/fees | +10/-6, zero-net gross, whole-share partials, cumulative physical fee, 200 seeded permutation/conservation cases. PASS. |
| A09 missing/gaps | Known future open cannot decide order; missing submitted exact-minute fill remains unresolved. Negative path PASS; actual V4-PRICE-001 blocks financial certification. |
| A10–A12 carry/actions/risk | Physical-net ACT/365, restricted proceeds, ordinary ex/pay/splits, marked limits and pending reservations. PASS tests; actual unknown fill retains obligation. |
| A11 restart | Actual Jan4–8 source run equals stop-Jan5/resume-Jan6 in event/daily/cohort streams, cash, physical shares and journal hash. PASS. |
| A13 release | Actual baseline invocation raises MANDATORY_RESEARCH_GATE_HOLD before Market/account/performance directory. Hash drift/omitted baseline/flags and wrong scope fail tests. |
| A14 historical pilot | Four PASS windows / one HOLD below. No full historical strategy run. |
| A15 baseline/sensitivities | NOT RUN: mandatory source/pilot HOLD; all 24 scenarios preserved, not discarded or tuned. |
| A16 integrity | 6,901 protected SHA256+mtime checks and 227 source SHA256 checks unchanged before/after. |
| A17 lint/types/regression | 234 tests; Ruff PASS; owned 0 errors/warnings; repository 27 inherited errors. |

| Historical diagnostic window | Sessions | Calendar opportunities | State | Pending terminal orders | Maximum Decimal ledger residual |
|---|---:|---:|---|---:|---:|
| 2021-01-04–2021-01-08 | 5 | 700 | PASS | 0 | 1.2E-22 |
| 2021-06-02–2021-06-11 | 8 | 1120 | HOLD | 2 | 8.214E-22 |
| 2022-08-24–2022-08-26 | 3 | 420 | PASS | 0 | 4.546182E-22 |
| 2024-05-09–2024-05-17 | 7 | 980 | PASS | 0 | 1.48480E-22 |
| 2024-11-27–2024-12-02 | 3 | 360 | PASS | 0 | 3.4969E-23 |

The 3,580 opportunities are calendar keys, not independent returns or filled trades. Each window has eight independent accounts (four arms × matched/attainable). Diagnostics record actual cash/share/claim/NAV reconciliation; no strategy return metrics or headline performance comparisons were calculated. June has six incomplete daily account records and two unresolved submitted orders, with zero unpriced special claims. Small ledger residuals do not certify missing execution truth.

## Exact commands executed

```sh
.venv/bin/python -m pytest tests/track2_stage012 tests/track2_stage35 tests/track2_stage35_completion_v2 tests/track2_stage35_completion_v3 tests/track2_stage35_v4 tests/test_hf20_s2c_ca.py tests/test_hf20_mag_c3_io.py -q
.venv/bin/ruff check src/lstm_data/trading/track2/stage35/final_backtest_v4 tests/track2_stage35_v4 --select E,F,I
.venv/bin/pyright src/lstm_data/trading/track2/stage35/final_backtest_v4 tests/track2_stage35_v4 --pythonpath .venv/bin/python --outputjson
.venv/bin/python -m lstm_data.trading.track2.stage35.final_backtest_v4.run pilot --version pilot_r6
.venv/bin/python -m lstm_data.trading.track2.stage35.final_backtest_v4.run baseline --version financial_gate_final_r1
```

The last command intentionally exits 1 with a saved refusal. Receipts: `audits/ENGINEERING_ACCEPTANCE_V4_e61bd23fd232.json`, `audits/FULL_PYLANCE_RELEASE.json`, `audits/ACTUAL_SOURCE_RESTART_V4.json`, `audits/FINANCIAL_LAUNCH_REFUSAL_V4.txt`. The installed full-check command used `scripts/check_python_types.py --pylance-dist` with the locally resolved `ms-python.vscode-pylance-2026.4.1/dist`; resolve that path locally on another machine rather than copying a developer absolute path. Editor verification: select repository .venv, preserve basic severity, restart Pylance and refresh Problems; human editor refresh remains unconfirmed.
