# Rare-event read-only findings

|split|rows|q99|minimum|maximum|event_q99_fraction|floor_dominant_fraction|
|---|---|---|---|---|---|---|
|inner_train|17440|5.4352829|-29.199883|21.382109|0.0098623853|0|
|refit|19960|5.3829457|-29.103548|21.321026|0.01002004|0|
|development|7320|5.2629573|-23.350283|14.394906|0.010655738|0|

|mechanism|rows|event_fraction|median_MAD_over_epsilon|
|---|---|---|---|
|BOTH_LARGE_NUMERATOR_SMALL_MAD|7|0.08974359|4.8062785|
|LARGE_NUMERATOR|62|0.79487179|8.0113118|
|NEITHER_TRAIN_Q95_Q05_FLAG|1|0.012820513|5.5599287|
|SMALL_MAD|8|0.1025641|4.7549178|

|arm|events|event_sign_accuracy|event_top4_magnitude_recall|top4_magnitude_precision|
|---|---|---|---|---|
|C0|78|0.51282051|0.37179487|0.019808743|
|T2|78|0.5|0.38461538|0.020491803|

Training-only q95/q99/q99.9 thresholds and numerator/MAD quantiles are saved. These describe canonical unmodified targets; no event information is suppressed. The top4 development rule is post hoc, not a validated precision/recall operating point. Train forecast thresholds are NOT_AVAILABLE. Largest target examples are ex-post, not X. No issuer-news explanation or adjustment certification is inferred.
