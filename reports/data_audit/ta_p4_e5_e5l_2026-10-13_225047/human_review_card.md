# Human review — P4.8 / P4.9 synthetic prerequisites

**P4.8_SYNTHETIC_ENGINEERING_PARTIAL; P4.9_SYNTHETIC_ENGINEERING_PARTIAL.**
E5 is 48×23 with 7,329 parameters. Learning proof missed its fixed engineering
criterion; further E5 fitting stopped. Directed signals/formation/sham checks pass,
but frozen ridge flag placement is silent. No final E5 fit/checkpoint/forecast,
LL ridge fits or LL neural architecture was executed. Scientific G0–G4 HOLD,
real G5/G6/G7 NOT_RUN; real pairs0/40. This is one review, not primary activation.

| Check | Exact code / test anchors | Expected versus actual |
|---|---|---|
|1. Source/authority/pair budget|`src/lstm_data/e5_audit.py:144`; `tests/test_e5_neural.py:171`|No credentials/provider/OHLCV;402 source-file SHAs conserved;16P2/33P3/seven blockers/0real pairs. PASS|
|2. Shape and parameter inventory|`src/lstm_data/neural_models.py:84`; `tests/test_e5_neural.py:22`|48×23,2944+4096+128+128+32+1=7329; one-layer/dropout/readout. PASS|
|3. Four-peer population math|`src/lstm_data/peer_inputs.py:26`; `tests/test_peer_inputs.py:45`|Target excluded, divisor4, no new scaling; direct hand SD and means. PASS|
|4. Exact21 prefix and clocks|`src/lstm_data/peer_neural.py:47`; `tests/test_e5_neural.py:53`|Shared21prefix,48 original stamps, origins, masks and ephemeral indexed storage; forged23 rejects. PASS|
|5. Causal publication / missingness|`src/lstm_data/directed_peers.py:189`; `tests/test_directed_peers.py:122`|Unknown/NaT/future/outcome/stub/unit/source/action/scaler/order/partial sources reject. PASS|
|6. Peer gradients and learning proof|`src/lstm_data/e5_audit.py:72`; `tests/test_e5_neural.py:53`|Positivegrad .0005105; loss .22564→.14391, zero-peer .21520. Missed <.35×initial and >2×final proof. PARTIAL; unchanged replay only logged metrics|
|7. Session loss / optimizer / D6g|`src/lstm_data/neural_lifecycle.py:59`; `tests/test_neural_lifecycle.py:22`|Session4/10→7,19-session→9; frozen optimizer/clip/selector shared. E5 actualcalibration/refit NOT_RUN afterhealthSTOP|
|8. Checkpoint/five-score boundary|`src/lstm_data/neural_artifacts.py:121`; `tests/test_e5_neural.py:89`|Cross-family/stale/calibration-stage rejects; CPUboundaryresume. Mock checks PASS; E5finalforecast integration NOT_RUN|
|9. Preformation H/L/flags|`src/lstm_data/directed_peers.py:94`; `tests/test_directed_peers.py:55`|300 fictionalrows/60actualsessions; uniqueH/L, tableSHA, late/tiesdeny; fixedflags. RealHL_UNRESOLVED|
|10. Two directions/lag0 and1|`src/lstm_data/directed_peers.py:228`; `tests/test_directed_peers.py:84`|OnlyLreceivesH; only H receives L; other names 0; lagged four-peermean correct. PASS|
|11. Overnight/DST/stub/lag48|`src/lstm_data/directed_peers.py:336`; `tests/test_directed_peers.py:166`|Explicit49thsource; ordinary1140min,DST3960,earlyclose4200; no closingstub promotion. PASS|
|12. Ridge161prefix/objective|`src/lstm_data/directed_peers.py:496`; `tests/test_directed_peers.py:216`|147+14 conserved in oldP4.7 tests. Flags-once163/198 vs repeated175/210 unresolved; λ/7 penalty difference. LLfitAPI refuses; controlledfits NOT_RUN|
|13. Ten-session sham/matched masks|`src/lstm_data/directed_peers.py:436`; `tests/test_directed_peers.py:180`|Actual10eligible sessions/same slot, all arms same origin mask;49 missing sources rejectorigin. Timing-only PASS; no coefficients/p-value/scoreclaims|
|14. Conservation / release / remaining authority|`tests/test_e5_neural.py:89`; `checks.json`|TM0/MC0/MC1 same CPU numeric reload; cleanup/profile unchanged. 662 passed in 1593.73s (0:26:33); Pyright 0/0 across139files; Ruff PASS. Upstreamacceptance pending; no P4.10–P4.13 activation|

**One design decision:** approve two H/L flags once per target observation after
161 columns (LL0-R163,LL1-R198), or repeated at all seven lags (175/210)?
The task's§1.2/GateB.3 requires human choice because frozen D8§10.3/D13§17 do not
resolve it. This changes ridge shrinkage and requires additive versioned registration.
No choice activates real fits or clears the independent E5 learning-proof HOLD.

[Package](package_report.md) · [Evidence](synthetic_evidence.json) · [Checks](checks.json) ·
[API](../../../docs/track_a/P4_E5_E5L_SYNTHETIC_API_v1.md) · [Decision](review_decision_request.json).
