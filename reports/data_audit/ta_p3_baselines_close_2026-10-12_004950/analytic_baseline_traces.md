# Synthetic analytic values

Scope:SYNTHETIC_ONLY; scientific HOLD. Values are independently calculated in the linked tests and checked against actual baseline/physical primitives.

|Value|Expected|Actual|Status|
|---|---|---|---|
|positive_long|FOX|FOX|PASS|
|positive_short|TIN|TIN|PASS|
|negative_long|FOX|FOX|PASS|
|negative_short|TIN|TIN|PASS|
|ties_long|FOX|FOX|PASS|
|ties_short|TIN|TIN|PASS|
|constant_long|FOX|FOX|PASS|
|constant_short|TIN|TIN|PASS|
|day1_each_stock_weight|0.1|0.1|PASS|
|day2_each_stock_weight|0.05|0.05|PASS|
|free_intercept|10.0|10.0|PASS|
|ridge_coefficient|1.3333333333333333|1.3333333333333333|PASS|
|ridge_objective|2.6666666666666665|2.666666666666667|PASS|
|exact_loss_tie_selected_lambda|1.0|1.0|PASS|
|BH_0bps_each_shares|20|20|PASS|
|BH_0bps_entry_fee|0|0|PASS|
|BH_0bps_entry_cash|0|0|PASS|
|BH_0bps_terminal_cash|10000|10000|PASS|
|BH_5bps_each_shares|20|20|PASS|
|BH_5bps_entry_fee|5|5|PASS|
|BH_5bps_entry_cash|0|0|PASS|
|BH_5bps_terminal_cash|9995|9995|PASS|
|BH_10bps_each_shares|20|20|PASS|
|BH_10bps_entry_fee|10|10|PASS|
|BH_10bps_entry_cash|0|0|PASS|
|BH_10bps_terminal_cash|9990|9990|PASS|
|missing_open_whole_cash|10000|10000|PASS|
|early_close_terminal|2020-11-27T17:59:00+00:00|2020-11-27T17:59:00+00:00|PASS|
|split_shares|40|40|PASS|
|dividend_paid_once_cash|40|40|PASS|
|partial_entry_is_aborted|True|True|PASS|
|partial_entry_NAV|None|None|PASS|
|missing_terminal_NAV|None|None|PASS|
|random_examples_scenarios|72|72|PASS|

Ridge independent augmented normal equations and sentinel mapping: [tests](../../../tests/test_baseline_ridge.py#L22). Full benchmark cash/share journals: [JSON](analytic_baseline_traces.json). Synthetic fitted TG0 chronology and candidate/refit hashes: [primary](baseline_evidence.json) and [alternate](alternate_baseline_evidence.json).
