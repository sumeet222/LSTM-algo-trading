# Completion validation matrix

Final command receipts are authoritative; earlier failed/intermediate receipts are retained. Final pytest total is filled into STAGE35_COMPLETION_HUMAN_HANDOFF.md after execution. No SKIP/XFAIL was introduced. Baseline:87/87. Added tests live in four completion_v2 files; old Stage012/Stage35/neural tests are unchanged.

|Group|Evidence|Result scope|
|---|---|---|
|A/P frozen identity|FINAL_COVERAGE_AND_INTEGRITY.json, H0_inventory.json|568 protected objects and227 source partitions, hash+mtime unchanged|
|B future-source/label isolation|test_causal_cache, old completion-boundary tests|Maturity mutation, as-of48-slot gather and sign unchanged by future cache sources; earlier lawful input mutation changes snapshot; no View/F09/economics imports|
|C/M full original path|CACHE_PARITY_V2.json, final coverage, test_orchestration_and_history|12 tensor/CLOCK keys;16 H4 keys;all 20/F21–F24 actual signals, ordinary/half-day/overnight|
|D controls|test_mature_controls_future_mutation, full control manifest|Endpoint+2 strictly beforedecision;60/min40,.94 recurrence; strict missingness and prefix reference|
|E execution clocks|test_engine_and_release plus old calendar fixtures|Submit<barstart;complete<=receipt<=posting;dependent decisions held before fill receipt;closed exchange forbidden|
|F/G crossing/fees|test_settlement_v2 and old golden cases|+10/-6=>+4=>-6;zero net gross;opposed partials;stable matching/pro-rata;single physical commission/minimum|
|H actions|old corporate tests;new due/split/unknown-date tests;actual raw split source fixture|Known ex/pay,signed claims,split/reverse,CIL;unknown date claims retained andHOLD. Full historical action coverage stillFAIL|
|I/N carry/borrow|physical-net weekend and segmented-rate tests;fixed_short_stress|ACT/365 Friday–Monday,rate changes,missing rateHOLD;strict locates fail;conditional labels and deterministic hash stress no price input|
|J gaps|future open mutation,debt repayment,liquidation request tests|No retro rejection;observed costs/loan liability conserved;prospective response only;missing fill stays unresolved|
|K allocator|old caps tests plus fabricated20-name manager roundtrip|Integer lots,expense reserve,20/10/100 caps,pending virtual gross,no short-proceeds recycling,fixed exits|
|L anomalies|raw OHLCV tests,RAW_ACTION_SOURCE_FIXTURES and inherited P019B register|Invalid/adjusted/missing/corrected price fails;no profit-dependent outlier threshold|
|O release|forged flags/key tests;historical shadow refusal|No source loader/output before independent signed release;metadata labels cannot approve it|
|P static/replay|Ruff E/F/I,owned/basic and full Pylance-stub checks,synthetic replay|No suppressions/severity changes;inherited27 remain separate;adjacent state hashes and deterministic synthetic publication|

Intermediate defects corrected: first-eligible sign timestamp; static timestamp narrowing; duplicate synthetic journal ID; decimal expected-value operation order; emergency funding claim repayment bookkeeping. Earlier receipts remain for audit. The full source-only runs were not profitable-case selection or re-training. No historical financial test ran.

Final definitive receipt: audits/validation_release_v2/ —121 passed (52+26+34+9),Ruff E/F/I PASS,16owned files0 errors/0 warnings,642full files27unchanged frozen errors. A missingV2Book import caught in an intermediate expiry test was fixed;thefailed receipt remains archived. No test was skipped/XFAILed orseverity suppressed.
