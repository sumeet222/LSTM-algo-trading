# P024 Stage 0 — corrected selector interpretation

This supersedes the narrative in stage_0_review.md. The numerical CSV tables were correct throughout.

Strict 0.1% replay: seed42 selects7/raw7/stops17; seed123 selects1/raw12/stops12. Strict 0.025% replay: seed42 selects7/stops17; seed123 selects2/stops12. Epoch2 qualifies relative to epoch1, and epoch12 does not qualify relative to epoch2. Both replays stop within the saved curves; neither is right-censored. No counterfactual fresh refit was run.

The earlier narrative and chat statement claiming selected epoch12 were incorrect. The ES025 arm remains exactly as submitted, using seed123 and threshold0.025%; no fitting result or trial definition changed.
