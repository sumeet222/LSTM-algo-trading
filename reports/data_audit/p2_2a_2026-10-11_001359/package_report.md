# P2.2A — synthetic label interface complete

**IMPLEMENTATION COMPLETE; overall G2 BLOCKED.** Added one reusable module and focused tests, using existing P2.1 plans and XNYS sessions. P2.1 was already committed; clean starting tree. No source rows or confirmation price outcomes were opened.

`MinuteReference` validates exact raw one-minute opens, symbol/time/source IDs/version/availability basis. Lookup rejects duplicate candidates and does not substitute next-minute, adjusted or other-stock prices. `causal_eligibility` consumes upstream forecast evidence and contemporaneous entry references only. It asserts source/clock/reference eligibility, not complete FT0 or P3 risk/admission/fills. Future exits/actions/floor are absent from that interface.

`label_sample` separately requires five entry/exit references and explicit action interval scope. It retains raw logs, centered returns, cross-sectional median/unscaled MAD, source identities, label maturity and reason. Unknown publication gives MATURITY_UNVERIFIED; diagnostic returns are not supervised-ready. Split conversion uses time-specific event/share facts; unknown/unsupported actions block. No dividend cashflows implemented. Execution outcome NOT_EVALUATED; market HOLD; research_ready=false for all outputs.

`fitting_window` provides frozen WF1/WF2/preconfirmation date stops and last63 XNYS-session inner tail. Date splits use exclusive next-period ET midnight, plus actual fitted_at observability. `fitting_membership` rejects outcome/maturity crossings, excludes out-of-window origins and preserves per-origin reasons without a48-hour lookback embargo. `fit_tg0_floor` uses only eligible inner-training/refit labels and fits max(0.0001,0.1×median(training MAD)); empty/duplicate/synthetic-without-opt-in fitting fails. `apply_tg0_floor` uses the frozen floor, no clipping, partial population or refit.

Hand example:five synthetic log returns(-0.02,-0.01,0,0.01,0.03), median0, unscaled MAD0.01, fitted epsilon0.001, scores=returns/0.011. Exact prices/IDs/maturity and C01 counterfactual in target_trace_examples.md. Removing future CAT exit leaves forecast and all entry flags identical; only label validity changes. Delayed future publication likewise cannot select entries after the fact.

**Validation:** initial26 focused tests passed4.11s. Added two plan/key guards before the single final full suite:157 passed30.51s (28 new cases); Ruff scoped and src/tests PASS; no pytest or lint failures. F01 reused once, unchanged. Formatting applied only new source/test paths. Existing protocol/check schemas and ledger preservation verified.

**Scientific dependencies:** all seven original blockers remain, including historical source publication, full minute/retry coverage,168 known half-hour gaps and formation/action/mapping obligations (four cash-date records unresolved), formal common clock registration and market-source contract. Researcher-reported240min/S&P replacement agreement remains formally pending under the existing P2.1 signoff card. Five authorities/CURRENT_PROTOCOL unchanged; no new source or assumed clock activated.

Next recommendation:separately approved source-coverage/availability bridge; P2.2B production integration only after concrete source/maturity/eligibility and registration prerequisites are supplied. No P2.3/features/portfolio/training/confirmation metrics. **Stop for APPROVE / CORRECT / HOLD.**

Branch feat/track-a-data-intake; HEADf298c6c9ee4948efe389b6d761e582851f395933 unchanged; fetched successfully0ahead/0behind after initial sandbox FETCH_HEAD denial and approved exact retry. One non-clearing G2 audit append; all previous bytes retained. All changes unstaged/uncommitted; exact human-review Git path manifest in session report.

Resources:elapsed snapshot 539.0s from pre-edit baseline; persistent code/test/docs/report/ledger delta 73797bytes; raw/source bytes and queries0; 7new and2modified files; no data scans or neural fits.
