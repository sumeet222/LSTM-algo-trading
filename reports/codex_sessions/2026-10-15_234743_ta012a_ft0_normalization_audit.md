# Codex Session Report

## 1. Session metadata

- Date/time: 2026-10-15T23:47:43.700543-04:00 America/New_York; preflight 2026-10-15T23:02:38.918302-04:00; elapsed since preflight 45.1 minutes.
- Contributor/session: Codex root, no subagents. Task Package012A read-only normalization audit.
- Branch: feat/track-a-data-intake; starting/ending SHA `55cf948eb6423a67e80e3ae5bd6d28d34e7e8a71`. No commit/PR.
- Start clean; fetched upstream0/0. End four tracked UI/config edits plus new audit modules/test/guide, two new audit namespaces and this report. No unrelated human work changed.

## 2. Executive summary

**P012A_AUDIT_PASS.** Audited all16 native and actual float32 channels across WF1/WF2 and four partitions;1536 channel/representation/stock summary rows. Four exact fit-population hashes reproduce;52 positive-MAD fits and12 bounded identities match. All3216 independent genuine-source/model-input scalar checks pass. No actual-input defect or degenerate active scaler found. B1 has the clearest rare-amplitude tail; V1/V2 have development level drift. Native floor binding is a separate important mechanism: M3 daily RMS floors bind up to61.05% of WF1 development observations for one stock. Rolling centering cannot undo native floor ties. Two future one-factor proposals only, with no performance claim.

Synthetic fallback discrepancy: [7,7,7] produces SD8.881784197001252e-16, selecting SD instead of the documented constant-to-zero branch. No current recipe uses this branch. It is explicitly HOLD for a separate narrow repair/re-audit; historical source math unchanged. Old audit-link metadata needed one consumer-origin resolution and stock-qualified pooled tail keys; new append-only files correct those without changing any feature value/count.

## 3. Research/protocol impact

No feature/target formula, fitted parameter, source, universe/order,48-hour lookback, horizon, split/mask, optimizer, costs/trading or seed/search change. No supervised/scaler fitting, new predictions, checkpoint execution, resampling, replay, provider requests, confirmation numerical access or pair reservation. Ledger24/40 remains byte-identical. Original TG0 fixed and distinct from historical FT0 RMS and pooled feature MAD. P2 v1 handoff hash-verified16entries, statuses unchanged. Shared spec, frozen roadmap, D4§5 and source/proxy/Q-volume/candidate amendments read; current source-defined conditional implementations audited. Existing production D1, publication/action/PIT/source-rights/joint/course qualifications remain; no scientific gate promotion. WF1/WF2-driven proposals are exploratory due to repeated prior inspection.

## 4. Files created

- `src/lstm_data/normalization_population.py`: canonical recipe/mask and fit-key readers; unique hourly vs M2 origin keys; exposure counts; non-M2 consuming metadata resolution.
- `src/lstm_data/normalization_stats.py`: signed/magnitude distribution diagnostics, descriptive pair collisions and independent recorded-scaler arithmetic.
- `src/lstm_data/normalization_oracles.py`: genuine bounded source reads, independent hourly/daily/EMA/Wilder/M2 replay and registered consuming48-step float32 comparisons.
- `src/lstm_data/normalization_audit.py`: single CLI, exclusive new output, grouped reports/resources/preservation, no fit path.
- `src/lstm_data/normalization_report.py`: sealed compact report reader, report documents and recipe-bound display manifest.
- `src/lstm_data/visualization/normalization_ui.py`: compact full-population audit controls/histograms/drift, existing Full data example navigation and bounded48-step context.
- `tests/test_normalization_audit.py`:14 focused mathematical/population/protection/identity/UI cases.
- `docs/track_a/FT0_Normalization_Audit_012A.md`: launch, reproduce, interpret, scope and protected-period guide.
- `reports/data_audit/ta012a_ft0_normalization_2026-10-15_230238_v2/`: required equations, population/recipe bindings, distributions/heterogeneity/drift/floors/fallbacks/dependence/clipping/tails/replay/oracles, hypotheses, walkthrough, checks/resources/preservation, logs and human review. Each path/type/bytes/SHA in artifact_inventory.csv.
- Preliminary `reports/data_audit/ta012a_ft0_normalization_2026-10-15_230238/`: first numerical pass retained locally; not active or proposed for staging. Finalv2 includes floor/segment/stability/consumer metadata and interpretation.
- This mandatory17-section report.

## 5. Files modified

- `apps/track_a_dashboard.py`: Start Here button opens existing Feature Scaling Explorer with bounded legal defaults.
- `src/lstm_data/visualization/controlled_ui.py`: opt-in compact012A expander; old traces/Package011 views preserved.
- `src/lstm_data/visualization/range_ui.py`: explicit state keys for existing Full data recipe/indicator controls and optional linked48-step context; confirmation guard still precedes readers.
- `configs/track_a_visualization_v1.json`: visualization-only reader/cache hashes plus additive normalization_audit manifest ref. Scientific source/model/recipe/study references unchanged.

## 6. Files deleted, renamed or moved

None. No source archive/component/model/previous report/notes/ledger overwritten or removed. Original new audit outputs also retained; corrected metadata has new filenames/manifests.

## 7. Critical functions, classes, variables and config keys

- `audit_guard(end)` rejects any scope other than fixed preconfirmation end before Catalog/source/output access. `run(root,out,end)` only admits a never-existing ta012a namespace under reports/data_audit.
- `Population/channel/tags` and `population(catalog,base,study,fold,part,view)` bind exact original masks/counts, fitted prefix and48 scheduled endpoints. Training stats exclude warm-up fit membership; OOS steps must follow recipe stop. No convenient intersection. M2 preserves origin; others deduplicate duplicate contexts. Tensor exposure counts separate.
- `fit_records/verify_fit_binding/scaler_records`: reproduce all four recorded unique key/value hashes without invoking a fitter. M2 uses50/50 origin weights and session/origin fit keys; WF1 inner6920 feature fit keys vs6880 stock/forecast targets includes four early-close input sessions. Other channels retain original hourly fit keys, even daily-locked features.
- `distribution/clipping_collisions/independent_scaler_check`: finite counts, signed vs |x| quantiles, ddof0 SD, unscaled MAD/IQR/Bowley skew, near-zero<=1e-8, maximum-multiplicity constant rate, bounds and3/5/10/20 tails. Hypothetical clipping only; complete five-stock pair distinctions lost, no order reversal. No IID significance or target correlations.
- `source_replay/native_oracle/replay_oracles`: independent source equations from original seed; exact matured prior-origin M2, no TG0 calculation. Uses real registered consuming forecasts for48-step input comparisons; native tolerance1e-10, scaled bitwise float32. Limitation: no persisted historical tensor capture, so frozen constructor replay is explicit.
- `floor_usage`: actual recorded native RMS floor activation and additive volume pseudocount shares; units distinguished from post-feature scaler MAD. `resolve_example_consumers`: only identical non-M2 contexts, fixed values verified exactly; M2 substitution forbidden.
- `AuditPacket.discover/table/json` and `publish_manifest`: exact source/recipe/no-confirmation binding; hash-verified registered artifacts. UI caches include actual table SHA/size/mtime/ctime. Active ref is display_manifest_final.json; resolved examples and verified stock/UTC/origin tail sets are explicit.
- `audit_panel/open_example/linked_context`: full selected-population summaries, original recipe identity, exact stock/date consumer, genuine candles/volume and one48-step trace. No alternate normalizer, anonymous fallback or training API.

## 8. Data/schema/provenance changes

Only derived compact audit schemas. Required numeric metadata includes feature/label/native/scaled/fold/partition/recipe/stock/unit/UTC-end clock/count/input-status/source. Shared floor/scaler engineering parameters are transparently mapped by numeric_table_schema_notes.json and full recipe/count JSON. Tail identities include stock/UTC/context; M2 context cannot be dropped. Primary hourly keys and exact fitting keys are distinct; overlapping48-step exposures are not the distributional population. Early-close/DST-offset/slot summaries retain original clocks. Source RTH split-adjusted USD/inverse-share volumes immutable; no raw exports or dense windows. All numerical reads pre2024-07; no confirmation feature generation. Native code remains authoritative; Q1/Q2 are signed logs, M2 uses its own mature4h RMS, B2/T2/T5 identity with float32 rounding.

## 9. Dependency/environment changes

None. Existing .venv, NumPy/Pandas/Arrow/Streamlit/Plotly and installed Pylance basic/stubs. No new credential/settings/environment package. RSS via resource.getrusage; Darwin byte semantics recorded. Approved localhost socket verification; no public server/upload/provider connection.

## 10. Commands and tests run

Exact commands in packet commands.md. Final focused command `.venv/bin/python -m pytest tests/test_normalization_audit.py tests/test_target_range_history.py tests/test_controlled_visualization.py tests/test_visualization_readonly.py tests/test_controlled_review.py -q`: **50passed,0failed,96.37s**. After test-only pandas stub-compatible record access change, isolated complete identity test **1passed/4.16s**. Initial49/50 exposed missing symbol in pooled identities; full corrected run passed. Earlier synthetic constant-contract and mistaken M2-label-count expectations were reconciled to actual code, with the fallback discrepancy disclosed, not hidden. No historical feature fix or weakened severity/test assertions.

`.venv/bin/ruff check .` PASS. Exact full static command `.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist`: **214owned Python files,0errors,0warnings,20.197s**. No suppressions/casts/Any/severity/exclusion/stub changes. Editor verification: select repo .venv/bin/python and installed Pylance basic, restart language server/refresh Problems; human confirmation pending.

`./scripts/run_track_a_dashboard.sh --check` PASS. `--smoke`: occupied8501 preserved, selected8502, health200/HTML200, clean exit0; startup1.895s/shutdown0.452s. Actual AppTests cover new audit and CMCSA2024-01-25 B1 candle/volume/exact48-step example, old TG ranges/full-data confirmation spy checks, Package011 deep-link and old adapters/scores. git diff --check PASS. Nonfatal bare Streamlit and sandbox Arrow CPU probe warnings disclosed; no final failing test. No long legacy model-training regression was run because scientific numerical modules are unchanged and890original bound fingerprints match.

## 11. Audit/results and resources

All3216 native/source and scaled-input oracles pass; all four fit hashes and52MAD fits/12identities match; zero nonfinite/missing primary eligible cells and zero bounded-input violations. Signed and absolute percentiles separated. All3072 tail groups match complete counts and unique stock-qualified identities. B1 development max WF1=20.742947, WF2=25.040920, |scaled|p99=6.010534/7.194288; >10 rates0.2156%/0.3248%. Genuine range magnitude plus ordinary positive scale explains amplitude, not degenerate MAD. V2 development medians−1.262600/−0.807365 training-MAD units; V1−1.062182/−0.702371. Native floor activation and stock differences require context; no Gaussianity, causal market-news or predictive claim.

B1 hypothetical±3 loses1.1456%/2.2869% of originally distinct five-stock pairs in WF1/WF2 development; ±10 loses no such pairs but still removes unique amplitude distinctions. SBUX T3 May2024 extreme source-replays. Propose only N-B1 asinh monotone compression and weaker N-V12 causal rolling centering/scaling, each independently against unchanged C0. Proposed60-session/0.25floor choices need human predeclaration. No per-stock/cross-sectional/stronger feature-MAD floor/target combination activated.

Final numerical CLI267.3448wall seconds/258.996CPU seconds, peak RSS719044608bytes (arm64,8logical CPUs), core outputs19,821,780bytes before appended verification/metadata. Final packet before this report/inventory about21,351,245bytes. First preliminary pass216.60s retained; final pass adds floor/segment/stability evidence. No model fits, checkpoints, dense windows or raw copies. Derived metadata resolution/tail verification does not redo or change scientific statistics.

## 12. Reproduction instructions

Use documented README .venv setup and legitimately provisioned original local artifacts (data/README.md); no new package/secrets. Launch dashboard and Start Here → Package012A normalization audit. Follow packet visualization_walkthrough.md and docs/track_a/FT0_Normalization_Audit_012A.md. Reproduce with `.venv/bin/python -m lstm_data.normalization_audit --out reports/data_audit/ta012a_ft0_normalization_local_recheck_01` into a new suffix, never an existing path. Current CLI emits resolved consumers and symbol-qualified sorted tail identities. It does not repoint the dashboard automatically. Final active manifest explicitly references the append-only verified metadata files. Run the focused checks/static command above; use local installed Pylance dist on another machine.

## 13. Git / collaboration status

Branch/HEAD unchanged; fetch0/0; no stage/commit/push/restore/reset/clean/stash/pull/merge/rebase. Four tracked changes listed above; new modules/test/guide/final and preliminary packet/report untracked. Final_preservation confirms890 original protected bound files unchanged and all original tracked changes limited to intended UI/config paths. Likely conflicts app/controlled_ui/range_ui/config. Exact final tree in git_final.txt.

If separately authorized later, review inventory and stage only its explicit code/test/guide/report and final small audit packet paths (exclude preliminary packet, licensed source data and checkpoints), then focused commit `feat: audit FT0 normalization without fitting`; fetch/recheck and push existing feature branch/use team PR workflow. Do not integrate over unknown work/divergence. No Git integration authority requested or exercised.

## 14. Known issues, risks and limitations

No current test/static failure or actual-input discrepancy. The nonzero-constant SD rounding fallback is a genuine synthetic contract gap, not an active fit failure; repair separately with retrospective checks if authorized. Constructed recipes are retrospective, not observed historical publications; live availability/action vintage/rights/PIT/source/course qualifications remain. M2 fit-vs-hour count differences are lawful and explicit. Source replay is from the same genuine provider, not an independent provider certification/news attribution. No persisted historical input tensors; exact frozen-constructor evidence only. Preliminary/uncorrected new audit files retained, active manifest/interpretation addenda disambiguate them. Human browser appearance/editor refresh and clean-machine rehearsal not claimed. No final confirmation or012B work.

## 15. Decisions requiring human/teammate review

Whether to authorize a narrow fallback repair; whether either separately specified012B variant merits an exploratory matched training plan/budget; primary metric/go-no-go/causal rolling scope must be frozen before that future work. Do not infer approval from this audit. Confirmation remains locked with no authorization requested. Human editor Problems refresh/native visual review pending; existing independent scientific holds not cleared.

## 16. Next recommended steps

Read ranked hypotheses plus interpretation_addendum before approving any treatment. Use registered CMCSA B1 and AAPL M1 examples in the existing app. Review the synthetic fallback edge independently. Refresh editor Problems. Review explicit files/inventory before any authorized Git integration; preserve the original data/models/ledger.

## 17. Artifact inventory

artifact_inventory.csv enumerates new code/test/guide/session report and every final packet file with type/bytes/SHA/intended tracking (excludes itself). Main deliverables: feature_registry_and_equations.md, population_and_recipe_bindings.json, ft0_normalization_distribution.csv, ft0_stock_scale_comparison.csv, ft0_temporal_drift.csv, ft0_tail_and_fallback_audit.csv, ft0_floor_activation.csv, scaler_stability.csv, feature_dependency_and_oracles.md, feature_replay_examples.csv plus resolved version, independent_feature_oracles.csv, normalization_hypotheses_ranked.md, visualization_walkthrough.md, checks/validation/resource_usage/preservation/final_preservation JSON, logs and single human_review_card.md. Active display_manifest_final.json seals verified metadata. No plot/checkpoint/raw dataset copies. Preliminary packet intentionally local and excluded from staging guidance; user-owned8501 server untouched, smoke8502stopped cleanly.
