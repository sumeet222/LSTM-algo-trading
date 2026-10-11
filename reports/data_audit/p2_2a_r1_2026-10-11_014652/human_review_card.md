# P2.2A-R1 review pointers

1. src/lstm_data/hourly_proxy.py:113 resolve_reference; test_exact_nominal_slots_and_independent_five_name_tg0 / test_delayed_issuance_keeps_original_source_boundaries_and_true_age: fixed CLOSE endpoints, scheduled events,180/360s ages; no nearest/minute fallback.
2. proxy_label_sample:213 and tests no_early_maturity / late_exit_availability / future_exit_counterfactual: scheduled exit floor on maturity; late publication does not imply fill; entry flags independent of future exits.
3. proxy_split reference boundaries and test_split_covers_reference_interval_even_before_scheduled_entry: raw100→51 with2:1 at10:31 givesln1.02; action scope must start by10:30, not10:33. This is proxy price-return basis, not physical trade wealth.
4. proxy_fitting_membership:351 / fit_proxy_floor:358 / apply_proxy_floor:403; tests purge/version/floor: actual maturity purging, training-only floor and mandatory proxy lineage; reject minute samples/floors and forged missing references. M2 calculation deferred with explicit rebuild version.
5. From README virtualenv: python -m pytest tests/test_hourly_proxy.py tests/test_labels.py -q (53expected passes). Read checks/preservation for exact old-label/test/CA hashes and unchanged blockers. Scientific source/execution/shared-rule approval remains pending; no full global G2/G4 PASS.
