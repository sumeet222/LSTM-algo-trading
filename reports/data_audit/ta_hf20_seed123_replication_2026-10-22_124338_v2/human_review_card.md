# Package017 human review card

**Two approved seed123 pairs COMPLETED; exploratory development only. Ledger32/200.**
Actual human response: “Approve these exact two seed-123 pairs”. Attribution: live researcher reply in this
session, proposal `5004eeaa343dabb17f6b03fdface92a9c14b9bb976a468d363c33bd1f0cb79e2`, execution `eecebadf8b84cd444c34d023ab4af8d5a39ed0f54eabf6857f4c1b6eb06075d8`.
Consumed seed42 grants were not reused. Bounded local-rights/source/clock assumptions continue.

| seed | arm | MSE | MAE | Rank_IC | score_std |
| --- | --- | --- | --- | --- | --- |
| 42 | C0 | 3.4783150611826104 | 1.2658516470643137 | 0.015875754961173424 | 0.05056131765345306 |
| 42 | T2 | 3.4751024720779555 | 1.265187522300381 | 0.023221989399728832 | 0.04036604585766228 |
| 42 | ZERO | 3.4745059908061524 | 1.2647920105702217 | nan | 0.0 |
| 123 | C0 | 3.4794399066014856 | 1.266220140368681 | 0.021052631578947364 | 0.06556206003890631 |
| 123 | T2 | 3.4759127879099214 | 1.265011445646905 | 0.0319610501663996 | 0.05036579909312826 |
| 123 | ZERO | 3.4745059908061524 | 1.2647920105702217 | nan | 0.0 |

C0 selected1 / T2 selected1; fresh refits exactly those counts.
G6 health: {"C0": {"nonfinite_gradient_count": 0, "reasons": [], "scope": "BOTH_CALIBRATION_AND_REFIT", "status": "PASS_PER_RUN_TELEMETRY", "warning_epochs": {"calibration": [], "refit": []}}, "T2": {"nonfinite_gradient_count": 0, "reasons": [], "scope": "BOTH_CALIBRATION_AND_REFIT", "status": "PASS_PER_RUN_TELEMETRY", "warning_epochs": {"calibration": [], "refit": []}}}.
Independent calibration validation and canonical refit prediction replay are exact; no model
updates in diagnostics. See paired_intervals.csv for exploratory five-session95% intervals
(not G8/search-adjusted); see researcher_diagnosis.md for seed consistency and counterarguments.

GO: inspect both saved seeds using existing launcher → Start Here → HF20 seed replication.
HOLD: extra fitting, held-out/confirmation, source/history acquisition, trading, redistribution,
protocol migration or model promotion. No further experiment begins automatically.

Actual timing by arm (seconds):
| arm | calibration | validation | refit | inference | worker | peak_RSS_bytes |
| --- | --- | --- | --- | --- | --- | --- |
| C0 | 20.557742083998164 | 1.469991667981958 | 1.870151499984786 | 0.9577532499970403 | 26.958045582985505 | 431751168 |
| T2 | 21.283678084000712 | 1.630894832953345 | 1.877684582985239 | 1.0140005419962108 | 27.888738999987254 | 436060160 |

Supervisor/queue/package and exact check receipts supplement these worker measurements;
no causal C0-versus-T2 speed attribution. Tests/UI/preservation final status is in checks.json
and the coding-session report, not inferred here. artifact_inventory.csv lists all task paths,
hashes and Git intent. All work remains uncommitted; no raw data sharing is authorized.

Next decision: review the evidence, then separately discuss whether a source audit or one new
objective hypothesis is warranted. LONGER_HISTORY_FEASIBILITY_NEXT.md is proposal only.
