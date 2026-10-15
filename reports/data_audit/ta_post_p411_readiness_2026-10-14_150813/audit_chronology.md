# Source → clock → reference audit chronology

`audit_chronology.csv` contains12 hand-auditable calendar rows: ordinary2020-07-01; DST2021-03-12/15; early close2020-11-27; genuine AAPL split boundary2020-08-28/31. Each row links the actual source archive hash and two native30Min starts to an anchored completed hour. All times are aware ET/UTC. Values are schedules and source-key evidence, not features, prices, labels, issued forecasts or fills.

Ordinary first origin:09:30/10:00 raw starts → completed09:30–10:30 step at14:30Z in winter or13:30Z in summer → own-step stock/market available_at UNKNOWN → hypothetical10:32 issuance →10:33 minute reference →14:33 reference → TG0 only after all five genuine endpoints/publications and maturity. Second origin:10:30/11:00 starts →11:30 cutoff →11:32 hypothetical issue →11:33/15:33 references. Exactly240 elapsed same-session minutes is calendar geometry; historical reference prices/publication are missing, so no target exists here.

DST:2021-03-12 opens14:30Z, March15 opens13:30Z; ET origins stay10:30/11:30. Cross-session lag antecedent for Monday March15's first completed hour is Friday March12's final full step14:30–15:30 ET (20:30Z end), not the15:30–16:00 stub, weekend synthetic row or a skipped missing row. Daily features may use only Friday's genuine terminal daily close after Friday source availability; Monday's close cannot enter Monday morning.

Early close2020-11-27:13:00 ET close, three full hours through12:30, terminal12:30–13:00 stub. Both nominal14:33/15:33 exits lie outside session and execution_plan rejects them. A four-hour label or entry cannot be manufactured. Nine main early-close dates and the prehistory one are individually listed for each stock in complete_five_stock_qa.json; confirmation dates are calendar/key checks only.

Split boundary: retained AAPL 2020-08-31 action record is genuine retrospective metadata; actual publication remains null. The pre-split2020-08-28 candle comparison and original dividend records are in corporate_action_unit_samples.json. No split-adjusted candle is relabeled a raw minute opening.

Keep four states separate: forecast_issuable depends only on available inputs; entry_eligible depends on contemporaneous forecast/entry/risk facts; label_valid is ex-post all-five matured-reference completeness; exit_filled is a later physical execution result. C01 synthetic counterfactual tests pass; no real state counts were inferred. Missing future exits may change label_valid/exit_filled and must not change prior admission.

Hourly-close proxy amendment exists:10:30/11:30 closes and14:30/15:30 closes are separate approximate reference clocks, not10:33/11:33/14:33/15:33 raw fills. A proxy label must still mature no earlier than its nominal scheduled exit. No imaginary16:00 full hour. Shared proxy exception/risk and benchmark approval remain separate from conceptual240-minute agreement.
