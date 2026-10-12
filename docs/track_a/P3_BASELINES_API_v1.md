# P3.5–P3.6 synthetic baseline API v1

TA-P3-BASELINES-CLOSE-001. Human approval accepts the existing P3.1–P3.4 engineering foundation. All empirical/source/scientific approvals remain separate and on HOLD; P4 is not started.

## Portable entry point

From the repository root, use the README environment, then:

```sh
.venv/bin/python -m lstm_data.baseline_audit --mode ENGINEERING_SYNTHETIC_ONLY --out reports/data_audit/my_new_baseline_audit
.venv/bin/python -B -m pytest -q
.venv/bin/ruff check .
.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-Pylance-extension>/dist
```

The CLI accepts no panel path or empirical fitting mode. It fabricates all features, labels and prices, checks the protected P2/P3 authorities, refuses existing outputs and writes only synthetic evidence. No credentials, vendor requests, confirmations or neural fitting occur. NumPy/pandas and existing dependencies suffice.

## Forecast inputs and one physical bridge

`BaselineInput` injects an immutable ordered five-name `UniverseSpec`, canonical P2 `StockTensor`, full per-cell availability, stock scaler/floor certificates, P2 execution plan, explicit synthetic basis and optional D7 window/scaler. Forecast functions require `allow_synthetic=True`. All 48 scheduled slots and 16 FT0 channels must remain in canonical order; stock membership, values, masks, sources, own-step availability, transform context and certificate bindings are validated. ASOF application requires the fitted transform to be available at every historical step, following the existing P2 contract. Historical training context never becomes a live as-of assertion.

`momentum` uses only each stock's latest training-robust-scaled FT0 M1. No supervised score fit, horizon/sign search, label or future exit is an input. Descending M1 goes through the original P3 tie/rank contract; all-equal scores are tagged CONSTANT_PREDICTION, not ranking skill. Predictive Spearman midranks remain distinct; this package emits no empirical Rank IC.

`Prediction` binds scores, method, model/rule ID, input ID, plan and universe. `forecast_adapter` is the only new momentum/ridge/random bridge to the unchanged P3 `Forecast`. Its ID fingerprints method/model/input/universe/scores, preserving method lineage even when scores coincide. Original P3 model/input versions remain visibly synthetic; no real model adapter is activated. All methods use the same P3 policy, physical cash/share/order/fill, fee/borrow/risk/retry and action logic.

## Frozen ridge and chronological selection

`lag_vectors` takes ordered snapshots at `[0,1,2,5,11,23,47]` relative to the latest of the 48 scheduled steps. Concatenate 16 stock channels inside each lag:112 dimensions. Market arm appends a separate 35-value tail:seven matching lag snapshots×five D7 channels, width147. Missing permitted historical market rows use standardized zero, with audit masks separate; endpoint and46/48 constraints remain. No stock ID, sector ID, learned mask, raw market level, peer or full48 flattening is added. Ridge observes seven snapshots over48 steps; later LSTM would observe all48, so the representations are not identical.

`session_weights` assigns each stock row `1/days/origins_in_day/5`. `solve_weighted` solves the weighted centered normal system with one unpenalized global intercept and all coefficients penalized. Objective is mean-session weighted TG0 MSE + λ||β||². Grid is exactly `[.0001,.001,.01,.1,1]`. Nonfinite, ill-conditioned (>1e12) or excessive normal-equation residual fails without inverse/fallback. Small-width algebra tests are permitted; public models require112/147 dimensions.

`select_and_refit` uses the original `fitting_window`/`proxy_fitting_membership` constructors for WF1, WF2 and PRECONFIRMATION. Candidate transforms/TG0 epsilon and ridge fits use only the earlier inner-training prefix; inner validation is the final63 exchange sessions. Source maturity and split crossing are independent exclusions. The validation guard requires≥50 eligible days and≥25 observations of each origin. Select session-weighted validation TG0 MSE, with exact ties choosing larger λ. Recompute training-only preprocessing on the full permitted prefix and refit once. No neural epoch calibration, outer result, economic metric, arbitrary near-tie threshold or extra search enters selection.

Preprocessing reuses P2 `fit_scaler`, `fit_floors`, D7 synthetic floor/scaler functions, and `fit_proxy_floor`/`apply_proxy_floor`. Certificate windows have a visibly synthetic namespace with the exact authoritative bounds/phase. Bounded memoization delegates to the original scaler apply; keys bind full certificate, value, source/action, time and context, and never fit new parameters. If recomputed stock floors change the supplied raw feature values' numeric floor basis, preprocessing fails with UPSTREAM_RAW_FEATURE_FLOOR_REBUILD_REQUIRED. The upstream feature producer must rebuild those features under the new prefix; this baseline does not silently recompute indicators or reuse a mismatched basis.

The old P2 `MarketFitWindow` INNER cap is specific to WF1. The isolated synthetic `RidgeMarketFitWindow` adapter validates the exact original frozen WF1/WF2/PRECONFIRMATION stock window and preserves its phase/bounds; it permits the approved later-fold candidate prefixes without changing P2 code or opening arbitrary/empirical fitting dates.

## Contextual benchmarks

`CashControl` uses actual P3 cash with an explicit synthetic zero-interest assumption; it is not a risk-matched portfolio. `BuyAndHold` requires a distinct synthetic segment ID, its first/last XNYS session keys, universe, frictions and starting equity. Entry must first be attempted09:30 on the first session, then exactly the next session's09:30 after a contemporaneous missing-reference rejection. All five opening references must be eligible before orders. An `OpeningOffer` explicitly declares synthetic one-minute **open**, keeping the price field distinct from an hourly proxy or minute close.

Initial per-name notional is `E0/[5*(1+c/10000)]`, with declared P3 Decimal40 HALF_EVEN exact fractional assumptions. Cash budget is checked using the same sequential physical fill arithmetic before submission; incompatible finite-precision budget arithmetic fails closed rather than inventing cash or broker rounding. Each cost case starts a fresh portfolio. No periodic rebalancing or dividend reinvestment occurs. Splits/dividends/settlement use the unchanged P3 action adapter and original CA primitives.

A partial actual initial fill remains physical and pays its fee; the existing P3 exception engine pursues causal flattening. The contextual entry is marked aborted/incomplete after that partial initial execution. Restarting a fully invested E0 allocation after paid correction costs is not silently invented; that would require an explicit restart/capital convention. Missing-reference cases with no fills continue normal next-session opening retries.

Terminal sales use the last RTH minute opening, derived as exchange close−1min (15:59 normal,12:59 early close). Missing/partial sales keep positions/claims; subsequent corrections require supplied synthetic minute-open offers. A later correction cannot make the original segment's terminal sale complete. Unsupported overnight exception funding, unknown payment dates, missing marks or execution keep NAV=None. Normal long-only contextual holding is separate from the intraday sleeve strategy, and is labeled LONG_ONLY_CONTEXTUAL_NOT_RISK_MATCHED.

## Seeded paths, replay and checkpointing

`RandomOpportunity` explicitly binds eligibility/publication, input ID, canonical plan, universe and synthetic basis; no label/exit/result input exists. `draws` uses NumPy PCG64DXSM with SeedSequence(master20261010, spawn_key=(0x503352,path_id)). Exactly1000 distinct path namespaces0–999 use a common causal opportunity calendar. Each eligible origin gets a uniform five-name permutation; first/last choose long/short. Draws are unchanged by global RNG activity, execution rejection or future exit mutation. Invalid/early-close origins remain in the calendar but get no draw. Draw collisions across independent paths are legitimate; no favorable reseeding or best-path selection occurs.

`random_matrix` runs each path through A/B×0/2/5/10bps×0/.005/.03 borrow as24 fresh accounts. One immutable price/event template is reused. Checkpoints store compact scenario counts/expense/hash summaries in25-path chunks; their binding includes the full synthetic input/event script, code hashes, NumPy version, initial conditions and seed. SHA/prefix checks refuse mismatched resumption. Partial summaries are versioned; complete1000-path summary is separate. Few examples independently reconstruct full journals. This is a descriptive randomized reference, not a formal selection-adjusted permutation null or a claim of identical realized exposure.

Each replay activation verifies full P2/P3 registry SHA before and after execution. Inside one account, a private immutable authority lease checks size/mtime/ctime/inode of the already verified authorities at every P3 mutation. File changes fail closed. This reduces repeated JSON parsing without changing P3 public signatures, source permission, numerical behavior or science status; original-vs-leased journals are tested identical.

## Deferred science and future P4

Use the additive P3 deferred register v2 and closure matrix. All16 inherited P2 and10 inherited P3 holds remain; v1 files stay immutable. Historical gaps/retention, publication/action vintage, raw price/unit conversions, actual causal tensors, empirical preprocessing/target floors, execution/minute exceptions/marks/financing, joint/course/proxy/source approvals and portable data handoff remain unresolved. Missing-data, source/provenance, approval/policy, real-fit/evaluation and portable-handoff causes are separate.

Future approved P4 may consume the typed universe/input/Prediction adapter and shared physical engine after those dependencies close. This package does not implement P4, consume any of40 neural pairs, open confirmation, report real portfolio performance, or perform Git integration.

For post-fit market prediction, `Preparation.with_market_history` accepts separately supplied, explicitly synthetic as-of market observations. It preserves the exact fitted scaler/floors and refuses conflicting replacement of an existing timestamp. The audit supplies fabricated July observations separately from the preceding fitting population; missing post-fit market data fail closed rather than becoming invented observations in a real pipeline.
