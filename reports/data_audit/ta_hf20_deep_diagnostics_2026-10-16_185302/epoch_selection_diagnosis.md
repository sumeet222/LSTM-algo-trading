# Why epoch 1 was selected

C0: optimizer objective 3.6614445360 → 3.5750141365; 11/11 adjacent changes decrease. Canonical inner-validation MSE 3.2945880196 → 3.3727396185. Selected qualifying epoch 1, raw minimum at1; stop=PATIENCE_STOP, patience=11.

T2: optimizer objective 1.3174404660 → 1.2857217722; 11/11 adjacent changes decrease. Canonical inner-validation MSE 3.2926493558 → 3.3143952456. Selected qualifying epoch 1, raw minimum at2; stop=PATIENCE_STOP, patience=11.

Exact T2 hand oracle (full saved float precision):

- Epoch1=3.292649355801669; epoch 2=3.2911129691384056.
- Raw improvement=0.0015363866632633894, or0.046661107736%.
- Qualifying requires new MSE **strictly below**0.999×epoch 1=3.2893567064458673.
- Epoch2 minus this required boundary=0.0017562626925382574>0.

This is a genuine positive raw improvement smaller than 0.1%, not a precision tie or a
coding error. Minimum12 limits when stopping is allowed; it does not prohibit selecting
an earlier checkpoint. Both fresh refits therefore ran1epoch, not12. Training has336 updates
per calibration and32 in each refit; full-prefix data has a different number of batches.

The recorded original-scale training MSE is an ONLINE changing-weights, dropout-ON loss.
It is not end-of-epoch evaluation loss. T2 optimizer loss is squared asinh(TG20/s) units;
C0 loss is squared original TG20. Canonical inner-validation MSE always uses eval mode
and the proper inner T2 inverse. Do not compare the two optimizer-objective numbers.

Falling fitting objectives plus worsening inner validation are CONSISTENT_WITH_OVERFITTING /
NO_VALIDATION_GAIN under this small validation sample. They do not identify a unique cause:
weak conditional signal, regime instability, insufficient effective data or representation
limitations remain possible. No evidence justifies simply forcing more epochs. Recorded
calibration/refit checkpoints show epoch 1 outputs; weights/output histories for epochs2–12
are NOT_RECORDED, so their later contraction cannot be reconstructed from final weights.

The last63exchange-calendar sessions begin2024-12-26; only 55 sessions/110 origins pass the
frozen feature/fit-availability mask. Inner fit ends2024-12-24; refit ends2025-03-28;
development starts2025-03-31 and never selects epochs. Exact maturity/purge checks and distinct
inner/refit recipe IDs are in chronology_and_selection_checks.json. Fresh initialization
hashes equal the recorded seed 42 initial state and optimizers were recorded empty.
