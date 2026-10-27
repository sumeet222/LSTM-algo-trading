# HF20 S5 + S9 completed campaign

**16/16 technical PASS; ledger130/200;32 prefix recipes and64 control fits completed,0 failures/retries.** Source hashes verified, protected2026 contents/hashes closed, all16 previews and64 browser role checks passed.

Read [final decision](S5_S9_FINAL_RESEARCH_DECISION.md), [complete analysis file index](S5_S9_DIAGNOSTIC_INDEX.md), [detailed training/extremes](S5_S9_DETAILED_TRAINING_AND_EXTREME_DIAGNOSTICS.md), [offline dashboard](S5_S9_VISUAL_DIAGNOSTICS.html) and [verification](S5_S9_VERIFICATION.json). MAG has qualified movement-size evidence; S5 ranking remains inconclusive; EVENT/QUANTILE do not beat stock-specific controls. No confirmation/trading claim.

The dashboard includes all16 actual models, four roles and13 task-specific panels. Full OOS trajectories are saved; other visible trajectories cover the first10 saved sessions, while all-role metrics/curves/strata use every row. Offline HTML is large (~236MB) because actual saved OOS data are embedded. Compact previews live in plots/.

All neural starts are exhausted for this campaign; the original runner deliberately rejects a restart. For separately reviewable **read-only** report reproduction with the existing private saved outputs, from the repository root:

```bash
.venv/bin/python scripts/summarize_s5_s9_saved_outputs.py --out reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation
.venv/bin/python scripts/render_s5_s9_complete_views.py --out reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation --reuse-screenshots
```

Omit --reuse-screenshots to regenerate previews. Browser QA runs16 actual four-role batches; all64 roles and13 panels are still mandatory. The initial all-model browser batch timed out after rendering16 previews and is preserved. No training was retried. The added scripts are report-only; sealed fitting/execution source and proposal hashes remain unchanged. Existing installed Chrome/Chromium suffices; no network or extra package is required.

The script recreates numerical detailed reports; the executive decision and appended scientific interpretation are curated from the saved tables. Private Parquets/checkpoints/case examples/HTML remain ignored; underlying source data and prior S1–S4 artifacts are unchanged. No Git publication or data sharing is authorized.

Historical dashboards: [S4](../hf20_s1s2_visual_s4a_2026-10-26_110310_preparation/plots/s4_a_rankings.html) · [S1/S2](../hf20_s1s2_visual_s4a_2026-10-26_110310_preparation/plots/historical_s1_s2_rankings.html). Preparation instructions/cards/receipts are retained as dated historical evidence. See [live session report](LIVE_WORK_SESSION_REPORT.md) for exact commands, limitations, resources and uncommitted Git status.
