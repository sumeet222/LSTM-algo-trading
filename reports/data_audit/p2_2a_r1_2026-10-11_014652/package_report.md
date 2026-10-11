# P2.2A-R1 — hourly-close proxy synthetic foundation

IMPLEMENTATION_COMPLETE; scientific source/execution readiness BLOCKED. Human instruction: “APPROVE P2.2A synthetic implementation” and proceed with R1; this accepts the original foundation and authorizes this coding extension, not source/execution/shared-rule gate sign-off.

New `src/lstm_data/hourly_proxy.py` and25new tests extend the accepted minute/TG0/maturity/purge foundation. Original labels.py and every preexisting test remain byte-identical. [API documentation](../../../docs/track_a/P2_2A_R1_Hourly_Close_Proxy_API.md), [hand traces](proxy_trace_examples.md), [checks](checks.json), [review pointers](human_review_card.md), [preservation manifest](preservation.json).

Exact source CLOSE boundaries10:30→14:30 /11:30→15:30; nominal event times10:33→14:33 /11:33→15:33 unchanged. Source/event ages180s, delayed+5min issue gives360s. No stub/rowshift/nearest/minute fallback; only raw stock closes with explicit source clock. Original cutoff does not move; the same input close requires availability by cutoff. Late exit publication delays label maturity but never proves an earlier fill; a missing exit cannot change past entry eligibility. Upstream full FT0 forecast eligibility remains an assertion, not computed here.

TG0 math and fitting_window/purge reuse accepted code; R1 wrappers reject minute/mixed artifacts. Proxy floor adds hash-bound price/clock/lag/version references; distinct execution/target/M2 versions. M2 is tagged REBUILD_REQUIRED, not calculated. Raw split factors use close-to-close boundaries with action coverage through scheduled exit; no dividend/total-return target change or cashbook. P3 admission/physical order/risk/exception/benchmark treatment remains separate; all outputs non-ready and fills not evaluated.

Validation:53focused proxy+minute tests PASS8.41s, final205integration tests PASS12.33s, Ruff PASS. No repeat after report formatting. Original minute tests unchanged; inherited corporate-action tests included. Integration includes the earlier optional bounded116-action metadata fixture, not a price scan/new source investigation. R1 fixtures and outputs solely synthetic; no data requests, new production labels, price scans, confirmations, training, market joins or simulator.

All five authority/CURRENT_PROTOCOL hashes and prior shared/proxy records preserved. All seven ledger blockers remain. One non-clearing G2/BLOCKED audit follows exact21-event prefix;22events now. Prior uncommitted CA files preserved, Git index/HEAD unchanged, no stage/commit/push. Full source availability/action coverage and hourly portfolio exceptions remain unresolved. No new empirical results or source swap; zero40-budget fits.

Review the R1 public contract and five pointers. Next coding scope/source/exception audits need separate authorization; no automatic P2.3/P3/real-source execution. Code approval and scientific approval stay distinct.
