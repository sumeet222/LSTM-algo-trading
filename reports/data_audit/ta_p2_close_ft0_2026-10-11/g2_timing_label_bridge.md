# Timing / label / FT0 bridge

Existing minute-open and completed-hour-close proxy mathematics are preserved separately. New `stock_window` → `forecast_bridge` accepts no future exit, label or fill. C01 tests mutate only a future source exit price/publication and prove identical input tensor/forecast eligibility. Existing tests separately prove future label/exit quality can change without entry/forecast changes.

Pinned real traces are July1 2020 origin1, March15 2021 origin2 (DST), and November27 2020 early-close rejection. Normal cutoff10:30/11:30 ET, nominal issuance10:32/11:32, nominal events10:33→14:33 or11:33→15:33. Proxy closes10:30→14:30 or11:30→15:30 are observed-price conventions, not fills. Events remain240 continuous minutes. Source-only planned issuance is synthetic metadata, not historical issuance evidence.

Real preconfirmation waterfall:1,998 structurally calendar-valid origins →1,982 sufficient48-slot histories →1,907 complete raw48-stock histories →1,415 mechanically fullFT0 histories →0 own-clock/action/certificate-eligible inputs →0 certified all-five entry references →0 independently matured TG0 labels. Physical positions/fills are NOT_EVALUATED. Per-origin rows and precise first bad step/channel are in retention_and_attrition.json. Real raw proxy conversion is uncertified, so no adjusted close is mislabeled raw.

Existing TG0 uses five per-name split-consistent log returns, cross median, unscaled MAD and epsilon=max(1e-4,0.1*median(training MAD)). A synthetic five-name return vector(-.02,-.01,0,.01,.03) has median0,MAD.01,epsilon.001 and scores r/.011. These are fixtures, not empirical source estimates. Labels remain separately matured; train/inner-tail/WF/confirmation boundaries reuse original fitting-membership purging.

M2 is `evaluate_m2`, not TG0 reused as a predictor. Every return must have matured by the input step's own cutoff. Existing M2 floor.fitted_at<=step.end guard is unchanged; on ScheduledStep that endpoint equals information_cutoff. A later batch scaler can normalize lawful historical training data only with explicit HISTORICAL_TRAINING context; it cannot create an as-of forecast, and cannot bypass the M2 guard.
