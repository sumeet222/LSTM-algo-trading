# Disclosed inference-order detail

The specification narrates frozen September checkpoint → calibration forecasts → C3 fitting/freezing → following-year OOS prediction. The new runner computes both calibration and uncalibrated OOS main/auxiliary forward outputs first, verifies both against a reloaded identical checkpoint, then fits C3 from calibration rows alone and decodes/stores OOS magnitudes with those frozen factors.

This is a **literal software-call-order deviation**, not a claim of exact historical execution ordering. Both independent reviewers identified it during the running fixed experiment. No numerical code was changed and no phase was restarted.

The dependency graph remains one-way: `predict_heads` receives only fixed transformed inputs and CLOCK; inference uses `eval()`/inference mode, no dropout RNG draw, state carry, optimizer or label input. The same frozen recipe/checkpoint produces both populations. `fit_c3` receives only the admitted calibration table, restricted scale and model identity; it receives neither OOS forward outputs nor OOS labels. OOS magnitudes are decoded after coefficients are fitted/frozen. This is arithmetic-equivalent to postponing the independent raw OOS forward calls until after C3 fitting; it does not establish literal execution-order identity.

No new OOS results choose a model, epoch, coefficient, feature, threshold, or continuation decision. Final acceptance must retain this disclosure and distinguish numerical/dependency agreement from exact procedural ordering.
