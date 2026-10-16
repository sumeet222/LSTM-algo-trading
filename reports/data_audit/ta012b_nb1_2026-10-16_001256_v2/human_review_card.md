# Package012B consolidated human review

**P012B_ENGINEERING_PASS — four approved pairs completed; 28/200 cumulative starts.**

The prospective40→200 amendment is researcher-authorized by submitted Package012B §1.1, recorded as researcher-reported prior authorization, not a fabricated earlier receipt. Registryv5 linked it before STARTED. Distinct live approval “Approve these exact four pairs” was recorded for proposal49a8518f4814a602631f83382de998008cd6ba75b4b18ace641c4f48076f3080, codea2993dc041d32e5fa2917f2df6c96f2fb77c4b455597dfb3a265d71f36024eee, recipes4e9794c123fde1c990d23f7ac18215e0a5a9d5953f332d752ac9bd208ddb5106 and amendment9b9b32c2cdf275a1195240afd5765b9d381bbc6eaf0bcc1196373f70cf3735e4. See live_four_pair_approval.json and experiment_design.json. Original40-cap records and24-pair journal prefix remain unchanged.

|Fold|Seed|C0 MSE|N-B1 MSE|ΔMSE|C0 IC|N-B1 IC|ΔIC|
|---|---:|---:|---:|---:|---:|---:|---:|
|WF1|42|5.438830|5.440565|+0.001735|0.034914|0.034914|0.000000|
|WF1|123|5.430641|5.430569|−0.000073|0.056897|0.053879|−0.003017|
|WF2|42|7.631510|7.631310|−0.000200|0.050862|0.037500|−0.013362|
|WF2|123|7.639672|7.649372|+0.009700|0.046552|0.049569|+0.003017|

**MSE wins2/4; IC wins1/4, one tie. No consistent generalization gain.** All exploratory five-session block intervals span zero. Two folds×two seeds are dependent development cells, not four independent histories. No significance, causal market-event, alpha, production or confirmation claim. Both C0 and N-B1 MSE remain slightly above ZERO in every cell. Ridge context is retained for WF1 without refitting.

B1 development maximum20.742947→7.270555 (WF1),25.040920→7.895438 (WF2); absolute p99 6.010534→3.714068 and7.194288→4.170654. This demonstrates amplitude compression. Canonical pooled/per-stock distributions and histograms retain regime drift. All15 other channels, TG0 and original masks are exact;232 origins/116 sessions per fold. No cross-stock order reversals or added cross-stock float32 pair ties in any audited population. Some adjacent distinct historical values share final float32 representations: finite arithmetic, no clipping; full counts are recorded. The native/q transform has no float64 ties.

G6 remains WARN_INVESTIGATE in all four treatments, as in controls. Calibration clipping fraction falls in3cells and ties in1; refit falls in2, ties in1, worsens in1 (WF2/123). Maximum calibration gradient falls in2cells and rises in2; refit maxima fall in all4. These descriptive changes do not establish a predictive improvement or remove extreme TG0/loss concentration. See gradient_comparison.csv, gradient_health.csv and loss_concentration.csv.

Actual neural fitting203.307s (3m23s); supervised batch about338s (5m38s, one-second OS start resolution). Pair subprocess durations88.087/66.162/85.655/92.372s in frozen queue order. Selected refit epochs4/1/2/1; calibration14/12/12/12. Detailed per-pass loading/preprocessing/validation/forecast/worker timings and CPU/RSS are saved, with no projection presented as actual. Maximum whole-worker RSS671,678,464bytes; CPU float32, one PyTorch thread. Preflight and postrun/reporting are separate from fitting.

Inspect: run `./scripts/run_track_a_dashboard.sh`, then **Start Here → Package012B B1 experiment**. All four cells, original/q/new B1 traces on separate axes, canonical histograms, both-pass learning/clipping/gradient views and exact CMCSA tail candles+volume+48-step context are available. Follow HOW_TO_VIEW_PACKAGE_012B.md. Prior Price&Features, Full data/TG0 ranges, Package011 and012A remain.

QA:97 distinct focused/regression cases passed (96 in sandbox plus the localhost socket case outside it); completed-results UI also passed separately. Full installed-Pylance basic:220Python files,0errors/0warnings; Ruff and diff check PASS. Checkpoint identities/CPU reloads,58 batch-epoch reconstructions,402 independent transform examples,8 genuine two-half-hour oracles,8 exact frozen input views and1,101 original-file preservation checks pass. First preflight metadata-serialization failure and a pre-start receipt-publication race consumed no pair; both are disclosed in the session report. No neural fit was retried.

Source rights/private shared-clock attestation, retrospective candidate/action/PIT, unknown publication, idealized period end, hourly-close price proxy, course/joint and production qualifications persist. Synthetic nonzero-constant SD fallback remains a separate HOLD; no real recipe invokes it. ConfirmationJuly2024–June2025 stays locked. **N-V12 remains untrained; Package012C is not activated.** Human editor Problems refresh/visual appearance and clean-machine rehearsal remain unclaimed. All changes are uncommitted; no Git integration authorized.
