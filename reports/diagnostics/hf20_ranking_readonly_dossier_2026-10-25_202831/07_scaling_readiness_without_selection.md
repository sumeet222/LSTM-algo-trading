# 07 — Scaling readiness: interface/design audit only

**QUALIFIED / DESIGN ONLY. No stock selection, variable-N implementation, acquisition or target migration.**

Actual interfaces: hf1m_ft16_loader.ModelInput.batch builds exactly20×48×16; hf1m_training_data.TrainingView groups complete sessions and origin labels; objective_screen_loss.Objective.contributions requires20stocks and R1 allocates190unordered pairs; state_screen_models.StateModel and panel_state require complete20 histories and two phase-scaled summaries. SYMBOLS fixes identity/order; training floors/pseudocounts include stock/share-regime entries. Median/MAD targets require all20genuine compatible endpoints and mark the entire origin invalid when one outcome is absent. These are real interface restrictions, not a generic variable-panel API.

| Interface | Required future design | Current status |
| --- | --- | --- |
| Membership/security identity | PIT input membership, stable issuer/share-class IDs, additions/deletions; no future survival selection | NOT_PRESENT_IN_FIXED_SURVIVOR_CONTRACT |
| Input eligibility | causal history/quality mask, independent from eventual label support | separate source_input_eligible already exists; full20 tensor assumption remains |
| Supervised validity | own later outcome validity, matured before fitting; no input/portfolio eligibility from a future exit | current full20 label conjunction; variable-N semantics UNFROZEN |
| Incomplete histories | mask/age-aware gathering; no closed-market synthetic prices | requires new version; no mask channels added here |
| Missing peers | masked mean/median/attention with explicit all-missing behavior and self inclusion | current panel proxies require all20 finite |
| Relative target | define reference cross-section/median/MAD/epsilon when membership/outcomes change | TG-N is a new target, not directly comparable with TG20 MSE |
| Transform fitting | global versus per-stock/share-regime rules; handle genuinely unseen names without evaluation fitting | current train-only pooled scaler + stock/regime floors; unseen rule needed |
| Loss hierarchy | equal session→origin→actual valid stocks or valid pair count; distinguish feature and supervised masks | fixed20/190 today |
| Stock-axis models | identity/order masks and out-of-universe transfer semantics | fixed peer mixer not automatically exchangeable |
| Storage | one shared canonical store + indices and saved outputs; chunk windows on demand | existing P020 design already avoids per-arm dense copies |

Expanding all-N completeness can collapse coverage; missingness is dependent, so no independence-based percentage is asserted as a dataset forecast. Do not select a universe size or coverage threshold from this audit.

Separate (a) more training securities, (b) more contemporaneous peer information and (c) a larger evaluated ranking opportunity set. Preserve common20stocks/common dates/common original TG20 labels as an evaluation bridge. Larger-pool training labels may need a frozen reference-basket/economic outcome; do not pool incomparable TG20/TG-N labels and call it pure sample-size improvement.

Existing measured P028 fit lifecycle: A7 373.703s, A8 393.120s, A12 357.663s including calibration and selected fresh refit; engineering, diagnostics and source checks are separate. Current audit core numerical work is30.99s and427MB peak RSS (numerical_receipt.json). Larger-panel times are unmeasured. Shared recurrent encoder compute broadly grows with N at unchanged parameter count, attention stock pairs with N²; microbatching must preserve cross-stock operations and session weighting. No10× runtime figure is presented as measured. A future synthetic/limited benchmark would need separate authority and explicit resource accounting; none ran here.

Minute-to-hour extension needs honest observed-minute masks/age and pooled versus latest-hour history matching. Multiple horizons need separate per-head validity/maturity and longest-cross-boundary purge. Extra origins change sample composition. Overnight targets require actual opening/closing/stub/action definitions. Rolling/expanding fits need earlier-cutoff recipes and genuinely issued forecast stitching. These are interface decisions, not built features, labels, panels or models.

Checklist before scaling: source rights/publication/action assumptions appropriate to intended claim; membership semantics frozen; input/label masks separated; complete-panel intersection replaced only by approved protocol; target bridge defined; finite matched controls and prolonged chronological plan approved; canonical store/resource benchmark defined. No scientific gate is cleared by this design review.
