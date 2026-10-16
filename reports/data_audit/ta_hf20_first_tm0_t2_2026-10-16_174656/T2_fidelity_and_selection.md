# T2 fidelity and selection

Package011 `controlled_loss.fit_policy` pools unweighted unique eligible origin-stock
training labels in float64, takes median absolute value with floor1e-6, and applies
asinh(y/s). `LossPolicy.canonical` is reused unchanged: s*sinh(logit), finite-or-fail,
no clipping. Its original real epoch engine evaluates session-weighted canonical MSE
before checkpoint selection. The historical Package011 report and saved T2 parameter/
selection records agree; no new scientific conflict or hidden historical rewrite arose.
HF20 uses independently fitted TG20 scales, not old TG0 scales.

Inner17440observations give s=0.9055291414260864; refit19960 give s=0.9057720005512238.
Inner validation and development never fit inner scale; development never fits either.
Original FT1 floors/scalers/epsilon are the two sealed precomputed recipes, not reestimated
by the model worker. The only newly estimated label-transform parameter is the separate
train-only pooled scale; the worker also independently recomputes it to reject staleness.

The shared SessionBatch/session_losses/batch_prediction kernel now takes an explicit20
stock count (five remains the default). The existing neural_lifecycle.epoch_pass is reused
with an optional imported LossPolicy, original-scale monitoring and observational timers.
The model, AdamW, sampler, clip and EarlyStop are reused. No training loop was copied.
Broader101legacy engine checks and the126case pre-fit suite passed before live fitting;
execution code was hash-frozen before the exact live approval and stayed unchanged.

Both arms stopped after12calibration epochs and selected qualifying epoch1. T2's raw
minimum was epoch2 (3.2911129691), but did not beat0.999×the epoch1qualifying best
(3.2926493558). C0 selected/raw-min epoch1 (3.2945880196). Fresh refits ran exactly1epoch,
not12. Minimum12 governs when stopping is permitted, not the earliest selectable checkpoint.
All4safe CPUfloat32 checkpoints reload with exact identity; final predictions agree
bitwise on the observed example. The independent postrun audit replays the selector.

Loss trajectories retain canonical training MSE and each optimizer's honest objective
units separately. G6 is PASS_PER_RUN_TELEMETRY in both passes for both arms; this is not
proof of useful prediction. Norm>1 fractions match actual min(1,1/(norm+1e-6)) fractions
at every recorded epoch. Tail counts/loss concentration and batch co-occurrence remain
available; batch co-occurrence is not individual-tail loss or causal attribution.
