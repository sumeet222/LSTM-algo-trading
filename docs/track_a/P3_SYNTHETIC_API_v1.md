# P3.1–P3.4 synthetic engineering API v1

Package TA-P3-ENGINEERING-001. This is an additive software handoff. G4 scientific acceptance remains HOLD; P3.5/P3.6 and P4 are not started. Current scientific membership and all P2 source/fit/formal holds remain intact.

## Activation and reproduction

Use the repository's documented `.venv` setup. No new dependencies, credentials or provider access are needed. From the repository root:

```sh
.venv/bin/python -m lstm_data.p3_audit --mode ENGINEERING_SYNTHETIC_ONLY --out reports/data_audit/my_new_p3_synthetic_audit
.venv/bin/python -B -m pytest -q
.venv/bin/ruff check .
.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-Pylance-extension>/dist
```

The audit refuses existing destination files. It emits synthetic ledger, independent expected/actual oracles, a 24-scenario matrix, and an alternate-universe trace. There are no real-source, performance, model-fitting or historical strategy CLI branches. The explicit `Permission` object verifies the unchanged, SHA-bound 16-item P2 handoff at every replay/scenario/export activation and economic mutation. An invalid mode fails before account creation or output. Missing/unknown publication, non-synthetic basis, historical or confirmation source identifiers, incompatible versions, and claimed provider fills are rejected.

## Contracts and universe binding

`p3_domain.UniverseSpec(version, symbols, sectors=())` is immutable, with exactly five distinct ordered uppercase names and optional aligned sector pairs. Its fingerprint binds the complete version/order/mapping. Every forecast, intent, sleeve, policy, friction configuration, reference, order, fill, action and replay frame carries this universe. Mixing versions, reordering without rebinding, duplicates or unknown names fails. Arbitrary alternate five-name sets work; this does not authorize selecting scientific replacements or changing TG0/FT0 dimensions.

`Forecast(universe, forecast_id, plan, scores, ...)` accepts only the canonical P2 `ExecutionPlan`, five finite ordered synthetic scores and exact synthetic input/model versions. `rank_intent` sorts descending score, then canonical index. Long first, short last; all-equal scores long first/short last. Negative scores still produce a pair. There is no label-valid, future return or future-exit-reference admission input. A later approved model adapter must translate into a separately authorized contract; the present synthetic gate cannot be used to activate that adapter.

`PriceReference` declares raw price/share epoch, positive finite Decimal price, observation time, known availability time, synthetic source ID and version, and one of HOURLY_CLOSE_PROXY / SYNTHETIC_MINUTE_EVENT / MARK. UNKNOWN publication is rejected. Hourly references require an exact complete one-hour interval. Normal entry prices are the exact original cutoff close and must already be available by that cutoff. Normal exit prices are the exact cutoff+4h close, available by actual exit; delayed issuance retains that close and reports the longer age. Fill events preserve scheduled/actual time, observation/available time and proxy age. MARK cannot fill an order. Physical minute fills require a genuine supplied synthetic minute event at the offered RTH minute. No nearest-hour substitution, interpolation or actual provider-fill claim exists.

`ExecutionOffer(universe, reference, fraction, outcome, attempt_allowed)` separates contemporaneous feasibility (`attempt_allowed=False` rejects the whole entry pair) from a scripted outcome discovered after order submission. FILLED=1, PARTIAL strictly between 0 and 1, REJECTED/CANCELED/HALT=0. These are scenario facts; the names do not classify historical vendor gaps or actual broker behavior. Fees occur only on actual nonzero synthetic fills.

## Engine and arithmetic

`PortfolioEngine(universe, Permission(...), Policy(universe, 'A'|'B'), Frictions(...), cash, at)` is one shared engine. `PhysicalBook` owns actual cash/shares/claims/orders; `Sleeve` owns immutable intended share instructions and 240-minute expiry. Internal amounts use Decimal precision 40, HALF_EVEN, with explicit exact fractional share assumptions. Forecast scores affect ranking only. No routine rounding, integer-share policy or cash-in-lieu is invented.

`enter`, `expire`, `monitor`, `retry`, `apply_actions`, `valuation` are synthetic-only operations. Prefer the immutable `ReplayFrame` and `replay` interface for deterministic replay and identical-frame idempotence. Direct duplicate forecast processing rejects; identical actual fill IDs are no-ops and divergent IDs reject. Frames must be monotonic. Different frames at the same instant must be combined into one frame. Same-time action+fill and simultaneous new entry+unresolved exit/exception lack approved priority and fail closed. Within supported frames: explicitly sequenced actions/settlements, causal mark/risk, due exit or outstanding retry, ordinary entry, daily borrow close, valuation. A risk trigger at an instant targets liquidation at a later supplied execution minute, never an invented same-instant fill. There are no random seeds because the script is deterministic.

Policy A sizes each leg at 24.75% of pre-entry equity, freezing shares. Active sleeves sum to physical targets before external deltas. Full-pair admission projects filled external net notional fees and requires physical gross ≤100% post-cost equity. Existing sleeve shares are never resized to admit a new pair. At admission, a held selected stock's valuation price must match its declared execution-reference price; incompatible inputs reject rather than conceal a projection mismatch. Policy B adds only the veto against an opposing leg in any active virtual sleeve, even if physical aggregate is zero.

Normal 10:33/11:33 entries and 14:33/15:33 exits reuse P2 clocks, actual issuance delay and early-close exclusions. A missing expiry keeps actual shares/cash/claims, suspends entries and preserves the virtual record until correction. Retry targets remove any other sleeve that has itself expired while waiting. Split units transform both physical and still-active virtual instructions through the original action primitive, including pending targets; virtual dividends do not create extra physical claims.

Only the corporate-action adapter knows ordinal legacy validator keys, using an invertible map to the unchanged `corporate_actions` functions. No new economic rule depends on a ticker. The original P2/CA modules, signatures and tests remain untouched. Actual source action normalization remains in the existing P1.CA workflow; P3 accepts explicit synthetic `ActionInstruction` and reuses `Action`, `apply_action`, `apply_actions`, `settle_dividend`, `retain_missing_exit` and `snapshot`. Unsupported merger treatment and ambiguous action sequence fail closed.

## Frictions, risk and incompleteness

`Frictions` permits only 0/2/5/10 bps (primary 5) and annual borrow 0/.005/.03 (primary 0), with a version/universe-bound fingerprint. Fees are combined assumed bps on actual external filled notional, exactly once. No extra modeled spread is added. Borrow is each symbol/session's maximum **observed physical net short** ×annual rate/360, once at exchange close. Covered shorts retain their day max. Missing necessary observations or omitted prior session close produce incomplete financing, including under the zero-rate scenario. Marks already supplied at the same event can value borrow; they cannot create fills. No interest on short proceeds is modeled.

`scenario_matrix` runs A/B×four costs×three borrow rates as 24 fresh account paths on one immutable script. Fees affect later equity/sizing/admission. Matrix output is accounting-only expenses/rejections/exceptions/hashes, without empirical performance metrics or copied source panels.

Risk is gross physical marked value/equity. Missing marks or equity≤0 halt unsafe entries. Strict >110% triggers; 109.9% and 110% do not. Passive >100% does not resize. Emergency halts entries for the rest of that session, keeps sleeves until actual liquidation completes, and charges actual partial/delayed fills. After a completed flat correction, a later session can resume only if normal risk/execution/financing criteria are satisfied.

`valuation` retains a diagnostic toy accrual equity but returns NAV=None for missing marks, unresolved execution, nonpositive equity, unknown payable date, incomplete borrow, unknown action coverage, or unsupported overnight financing. An unresolved overnight state and its financing hold are conservative, persistent synthetic states; no automatic funding approval is inferred after flattening. No terminal sale, annualized performance or final-test inspection occurs. Hourly proxy optimism/age, real minute retry prices, risk sampling, borrow availability and financing require separate shared/source approvals (P2-DEF-015 and new P3 register).

## Evidence and handoff

The combined package under `reports/data_audit/ta_p3_engineering_2026-10-11_230724/` supplies four phase gates, 24 paths, full linked events, cash/share reconstruction, independent hand values, alternate membership, protected-hash checks, and the exact future Git integration manifest. See the single human review card and `P3_DEFERRED_WORK_REGISTER_v1.md`. Synthetic PASS never clears a scientific gate or any P2 dependency. No Git integration is performed by this package.
