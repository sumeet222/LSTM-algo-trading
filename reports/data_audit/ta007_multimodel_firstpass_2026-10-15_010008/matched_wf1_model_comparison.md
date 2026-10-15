# Matched WF1 screening

ASSUMPTION_CONDITIONAL_RESEARCHER_ATTESTED_RETROSPECTIVE_IDEAL_CLOCK_HOURLY_PROXY. Retrospective universe/representation, idealized clock, researcher-attested rights and hourly-close proxy; SPY is an ETF state proxy. No observed-publication, executable-fill, course-substitution or production claim.

All eight rows use exactly 232 origins / 116 sessions / 1,160 stock predictions, same five targets and ordered names. No additional attrition.

| Model | MSE | Daily Rank IC | Neural fit seconds | Beats ZERO MSE |
|---|---:|---:|---:|---|
| TM0 | 5.4388296 | 0.0349138 | 52.63942466682056 | False |
| MC0 | 5.4508656 | -0.0120690 | 67.42830100090941 | False |
| MC1 | 5.4514664 | -0.0120690 | 72.02637625002535 | False |
| E5 | 5.4756397 | 0.0387931 | 153.7473515442107 | False |
| ZERO | 5.4275318 | 0.0000000 | n/a | False |
| M1 | 12.6919763 | -0.0219828 | n/a | False |
| RIDGE_OWN_112 | 5.4655180 | -0.0228448 | n/a | False |
| RIDGE_MARKET_147 | 5.4681203 | -0.0034483 | n/a | False |

Daily IC uses the existing midrank Spearman implementation: average two origins within session, then equal sessions. Constant forecasts receive project IC=0; defined-only ZERO IC is unavailable. MSE uses equal stock → origin → session weighting. M1 is an unfitted ranking score in different units; its MSE is diagnostic. Ridge uses seven lag snapshots, LSTM all 48 steps, so information is comparable but not identical. Pairwise ranking accuracy was not already implemented and was not added.

MC0-TM0: mean paired daily ΔIC=-0.0469828, ΔMSE=0.0120360, n=116.

MC1-MC0: mean paired daily ΔIC=0.0000000, ΔMSE=0.0006008, n=116.

E5-MC0: mean paired daily ΔIC=0.0508621, ΔMSE=0.0247741, n=116.

Existing TM0 final weights were safely reloaded and reproduced the frozen Package006 snapshot exactly; no TM0 or own-ridge refit. Each new final checkpoint reproduced its stored WF1 scores exactly. Monthly/origin/daily tables retain all observations. These are one-seed/one-development-fold descriptive contrasts; no significance, bootstrap, economic replay or causal increment claim. Frozen models were not modified after WF1.
