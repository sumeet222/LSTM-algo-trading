# S5 + S9 — single live-fit approval card

**READY FOR REVIEW; no new fitting or starts. Ledger114/200.**

Proposal [`design.json`](design.json) SHA256 `74f15becfc412697db87a837f625efadcdffb302ccd28fea34b7cc95290ac632`. Execution SHA256 `e19fc1da419d6456d16a7dec7777bc7e1400b2d0412be65ba116906d01cfd73e`.

| Family | Frozen input/optimized loss | Four starts, F21→F24 |
| --- | --- | --- |
| S5 META-T2R | FT16 + **six clock-only** fields; original S4 T2R MSE | `HF20-S5-F{21,22,23,24}-H4-META-T2R-S42` |
| MAG | FT16; MSE of log1p(abs(raw endpoint log-return)/prefix scale) | `HF20-S9-F{21,22,23,24}-H4-MAG-S42` |
| EVENT | FT16; original E1 three-class labels; **unweighted** natural three-class CE | `HF20-S9-F{21,22,23,24}-H4-EVENT-S42` |
| QUANTILE | FT16; original QR1 ordered .05/.50/.95 **asinh-unit pinball**; report signed TG20 inverse | `HF20-S9-F{21,22,23,24}-H4-QUANTILE-S42` |

Execution order is all S5 years, then all MAG, all EVENT, all QUANTILE. Exactly16 seed42 lifecycles maximum, calibration + fresh selected-epoch refit each; **114→maximum130/200**, failed starts permanent, no retries. Also32 prefix-recipe fits and64 fixed same-task historical control fits, with separate accounting. No grid, calibrator or additional neural control.

**Scientific choices to approve:** S5 excludes historical repair/quality flags whose original availability is unverified; scheduled elapsed gap is not observation age. This tests clock context, not the complete missingness hypothesis. EVENT preserves E1 labels but intentionally removes its old [4,1,4] loss weights for proper probabilities. QUANTILE preserves executed QR1 transformed loss and ordered head; raw-Y pinball is not substituted. [Metadata details](S5_CAUSAL_METADATA_MANIFEST.md) · [Historical targets/controls](S9_TARGET_AND_BASELINE_CONTRACT.md).

Same20 names,48 completed inputs, seven S4 candidate clocks, genuine240-trading-minute endpoints, original folds/embargo/eligibility/weights and qualified09:32 opening proxy. Original AdamW .001, hidden32, dropout .1, clip1,16-session batches. S5 original strict IC+.001 selection; S9 original inclusive0.1% proper-loss D6g; min12/max60/patience10. Complete numerical/scientific PASS before the next start. Individual+collective diagnostics and offline visuals follow, with annual/equal-year matched controls and descriptive month-block intervals.

**Preflight:**34 tests;495 Python files0 errors/0 warnings; four bounded untrained family workflows,16 role exports,0 optimizer calls/starts/new historical fits;120 saved-loss checks;4 browser views/16 roles. All S4 populations match, metadata finite100%,50-session validation minimum unchanged. Peak rehearsal RSS0.992GB. [Receipt](PREFLIGHT.json) · [Untrained preview](preflight_v2/S5_S9_VISUAL_DIAGNOSTICS.html) · [Complete file map](S5_S9_DIAGNOSTIC_INDEX.md).

**Caps proposed for this campaign:**2.5GB task /15GB whole project /2GB RAM; CPU4/interop1. Project presently~10.09GB; planning additions1.4–2.2GB, runtime4–16h. Check before each fit; stop if exceeded; preserve artifacts. Existing bounded local-rights/source/clock assumptions remain. No protected2026 contents or hashes, new2025 tuning, downloads, trading, Git publication or other experiments.

The submitted brief §1.2 says: “If repository policy requires human authorization before new fits, present one consolidated approval card and await it”. The active registry has `live_approval_required=true`, `fit_permission=false`; therefore a direct response approving this exact sealed campaign and caps is the only remaining activation gate. Existing S4 approval cannot authorize these new inputs/targets/starts.
