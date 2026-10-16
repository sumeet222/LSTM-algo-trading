# Package 016 review card

**HF20_P016_DIAGNOSIS_COMPLETE** · ledger 30/200 unchanged · zero new fits/optimizer updates.

Both selected epoch 1 because neither later raw gain met strict 0.1% qualifying improvement;
T2 epoch 2 improved only 0.046661%. Falling fitting loss with worsening validation is
consistent with overfitting/weak stable signal, not proof of insufficient epochs or capacity.

C0 MSE=3.478315061; T2=3.475102472;
ZERO=3.474505991.
C0 covariance is near-zero/negative; T2 has small positive covariance but its mean/bias component
accounts for most of the remaining ZERO gap. No development intercept correction was fitted.
Rank IC=0.015876/0.023222;
exploratory intervals and reused-development
history prevent a validated signal/alpha claim. Outputs are small but nonconstant; bounded
float32eval replay agrees with saved scores, without gradients or parameter changes.

Tail events remain intact, not automatically clipped or downweighted. Training|TG20|q99=6.508506;
read actual numerator/MAD/epsilon and event-sign/rank evidence in the main diagnosis.
Preserve the research goal of detecting unusual stock-specific returns. No external event
cause, vendor adjustment/PIT/publication certification or source-quality causal attribution.

Read **HF20_P016_MAIN_DIAGNOSIS.md**, then **docs/track_a/HOW_TO_VISUALLY_REVIEW_HF20_DIAGNOSIS.md**. Four exact saved development cases and
the epoch 1 view are provided. Existing HF20 views suffice; new comparative plots are specifications,
not fabricated UI features. Historical per-example gradients/dropout/optimizer states and later
checkpoints are NOT_RECORDED. Source/action/PIT/rights/idealized clock/hourly-close qualifications
remain ASSUMPTION_CONDITIONAL. HF20 and original five-stock held-outs remain locked.

Proposals only: paired seed replication first; separately preregister rare-event or rank auxiliary
hypotheses, or a fixed-target source-consistent training-panel control. No budget permission,
new architecture, training, trading, data acquisition or Git integration follows from this report.
Checks, preservation, exact replay and the mandatory session report complete the handoff.
