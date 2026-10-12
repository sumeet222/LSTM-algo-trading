# Consolidated P3.5–P3.6 engineering review

P3_1_TO_P3_6_SYNTHETIC_ENGINEERING_COMPLETE — HUMAN_REVIEW_REQUIRED; SCIENTIFIC_ACTIVATION_HOLD

All values below are SYNTHETIC_ONLY. Review the proposed engineering PASS independently of scientific HOLD. The human review is the remaining approval step.

1. **Ordered input and causal permission** — Proposed engineering **PASS**; scientific **HOLD**.
   [BaselineInput.validate](../../../src/lstm_data/baseline_inputs.py#L36); [negative input tests](../../../tests/test_baseline_momentum.py#L45).
   Five ordered names, 48 scheduled steps and 16 channels. Missing/future publication, reordered stocks, wrong context/scaler and empirical mode reject.

2. **M1 sign, ties and constant predictions** — Proposed engineering **PASS**; scientific **HOLD**.
   [momentum](../../../src/lstm_data/baseline_inputs.py#L206); [hand rank tests](../../../tests/test_baseline_momentum.py#L28).
   For FOX/ZEN/MAP/ORB/TIN, positive (5,4,3,2,1), negative (-1,-2,-3,-4,-5), ties (1,1,0,0,-1) and constant (1,1,1,1,1) choose FOX long/TIN short. Constant predictions receive CONSTANT_PREDICTION.

3. **Exact scheduled ridge lag mapping** — Proposed engineering **PASS**; scientific **HOLD**.
   [lag_vectors](../../../src/lstm_data/baseline_ridge.py#L24); [112/147 sentinel test](../../../tests/test_baseline_ridge.py#L107).
   Lags [0,1,2,5,11,23,47] map to scheduled indices [47,46,45,42,36,24,0]. Widths 112/147. Stock0/channel0 sentinels [.0752,.0736,.072,.0672,.0576,.0384,0]; D7 channel0 tail [.235,.230,.225,.210,.180,.120,0]. Permitted missing rows are standardized zero with separate audit masks.

4. **Mean-session loss and free intercept** — Proposed engineering **PASS**; scientific **HOLD**.
   [session_weights](../../../src/lstm_data/baseline_ridge.py#L82); [solve_weighted](../../../src/lstm_data/baseline_ridge.py#L111); [independent normal equations](../../../tests/test_baseline_ridge.py#L22).
   One-origin day stock weights .1; two-origin day .05. For x=(-2,-1,0,1,2), y=10+2x and lambda=1: intercept 10, beta=4/3, objective=8/3. Unequal-day constant targets yield hierarchical intercept 1 versus pooled 4/3.

5. **Selection, TG0 maturity and one refit** — Proposed engineering **PASS**; scientific **HOLD**.
   [select_and_refit](../../../src/lstm_data/baseline_fit.py#L311); [chronology/tie fit proof](../../../tests/test_baseline_ridge.py#L63); [purge/maturity negatives](../../../tests/test_baseline_ridge.py#L90).
   Synthetic WF1 has 74 training origins, 110 validation origins over 55 days (55 per origin) and 200 refit origins. Five identical MSE values 1.6528925619832657 select lambda 1; exactly one refit. Candidate/refit scaler IDs differ. Boundary-crossing and immature labels are excluded; inadequate 50/25 populations reject.

6. **Training-only preprocessing and held-out source** — Proposed engineering **PASS**; scientific **HOLD**.
   [prepare](../../../src/lstm_data/baseline_fit.py#L208); [with_market_history](../../../src/lstm_data/baseline_fit.py#L89); [validation-outlier isolation](../../../tests/test_baseline_ridge.py#L187); [asof-history immutability](../../../tests/test_baseline_ridge.py#L243).
   Validation outliers do not change the candidate scaler or TG0 epsilon. As-of history extension preserves fitted objects and rejects conflicting timestamp replacement. Changed raw-feature floor values require an upstream rebuild. All three frozen market candidate window bounds are tested.

7. **One forecast-to-physics adapter** — Proposed engineering **PASS**; scientific **HOLD**.
   [forecast_adapter](../../../src/lstm_data/baseline_inputs.py#L182); [counterfactual bridge](../../../tests/test_baseline_integration.py#L20).
   Momentum, own/market ridge and random retain method/model/input/universe bindings through one P3 adapter. Missing future exits leave earlier entry-event prefixes unchanged. Primary AAPL/JPM/JNJ/WMT/CAT and alternate FOX/TIN/MAP/ZEN/ORB each reconstruct six integrated policy journals.

8. **Cash and full five-name buy-hold costs** — Proposed engineering **PASS**; scientific **HOLD**.
   [CashControl](../../../src/lstm_data/baseline_benchmarks.py#L37); [attempt_entry](../../../src/lstm_data/baseline_benchmarks.py#L114); [four fresh cost cases](../../../tests/test_baseline_benchmarks.py#L68).
   Cash is 10000 with zero assumed interest. At price 100, capital 10000/10005/10010 and cost 0/5/10bps buy 20 shares per name, charge entry fees 0/5/10 and leave entry cash 0. Terminal cash is 10000/9995/9990. This long-only context is not risk matched.

9. **Missing opening and exchange terminal clocks** — Proposed engineering **PASS**; scientific **HOLD**.
   [attempt_terminal](../../../src/lstm_data/baseline_benchmarks.py#L200); [09:30 retry](../../../tests/test_baseline_benchmarks.py#L85); [normal/earlyclose minute tests](../../../tests/test_baseline_benchmarks.py#L97).
   One missing first-session 09:30 reference leaves 10000 cash and zero shares; retry is exactly next-session 09:30. Terminal normal 15:59 ET is 19:59UTC Aug3; early close 12:59ET is 17:59UTC Nov27. Hourly substitution rejects.

10. **Actions, partial fills and failed terminal** — Proposed engineering **PASS**; scientific **HOLD**.
   [retry](../../../src/lstm_data/baseline_benchmarks.py#L221); [split/dividend](../../../tests/test_baseline_benchmarks.py#L115); [partial-fill fee](../../../tests/test_baseline_benchmarks.py#L156); [terminal missing](../../../tests/test_baseline_benchmarks.py#L179).
   A split changes 20 to 40 shares at price 50 without phantom value. A $1 dividend on 40 post-split shares pays cash 40 once without reinvestment. Partial entry retains paid fees and causally flattens; entry is aborted and NAV is None. Missing terminal execution retains shares and incomplete NAV even after later correction.

11. **Stable seeds and golden permutations** — Proposed engineering **PASS**; scientific **HOLD**.
   [draws](../../../src/lstm_data/baseline_random.py#L80); [goldens](../../../tests/test_baseline_random.py#L129); [all1000streams](../../../tests/test_baseline_random.py#L19).
   Master 20261010, namespace 0x503352, PCG64DXSM NumPy2.5.3, 1000 distinct streams. Golden index permutations: path0 (1,4,2,3,0)/(3,1,4,0,2); path499 (3,1,2,0,4)/(1,0,2,3,4); path999 (2,4,3,1,0)/(0,1,3,2,4). Global RNG and future exits do not condition draws.

12. **Actual full matrix and independent physical journals** — Proposed engineering **PASS**; scientific **HOLD**.
   [random_matrix](../../../src/lstm_data/baseline_random.py#L189); [24-case state/exit control](../../../tests/test_baseline_random.py#L41).
   1000 paths × A/B × four costs × three borrow cases = 24000 fresh accounts, in 40 verified chunks. Calendar has two eligible daily origins and two ineligible early-close entries. Vetoes, physical fees, retries and borrow are recorded. 72 exported full example journals are independently reconstructed; no Sharpe, p-value or matched realized-exposure claim.

13. **Regression, diagnostics and preservation** — Proposed engineering **PASS**; scientific **HOLD**.
   [checks.json](checks.json); [preservation.json](preservation.json); [integration_manifest.json](integration_manifest.json).
   Fresh baseline 422 PASS; final 457 PASS after the last functional change. Basic diagnostics on 92 files: zero errors/warnings. Ruff/AST/diff PASS. All 524 original files, 257 raw stat records, original public interfaces and ledger seven blockers/zero of 40 neural pairs are preserved.

14. **Separate human review and scientific handoff** — Proposed engineering **PASS**; scientific **HOLD**.
   [closure matrix](closure_matrix.json); [v2 registry](p3_deferred_work_register_v2.json); [API handoff](api_handoff.json).
   All 16 P2 and 10 P3 inherited HOLDs remain, plus seven follow-ups: 33 NO_AUTO_CLEAR entries. Inherited 168 absent keys/15 clusters and 1183/1502=78.76% retention (<90%, deficit169) were checked against SHA-bound registers, not newly measured. Source/publication/action/raw units, real normalization/execution, retention and joint/course approvals remain. P4 is unstarted, G0–G4 HOLD, no Git integration.

[34 expected/actual hand values and eight benchmark journals](analytic_baseline_traces.json), [primary audit](baseline_evidence.json), [alternate audit](alternate_baseline_evidence.json), [all-path coverage](random_coverage.json), [72 full random example journals](random_example_ledgers.json).

Human acceptance can close the synthetic engineering package. It cannot clear scientific deferrals or authorize P4, empirical baselines, confirmation, vendor acquisition or Git integration.
