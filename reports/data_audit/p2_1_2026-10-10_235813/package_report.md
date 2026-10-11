# P2.1 — candidate clock implementation complete

**IMPLEMENTATION_COMPLETE; overall G2 BLOCKED.** One reusable module reuses existing XNYS schedule/session_grid. Existing calendar/aggregation/alignment/CLI behavior unchanged; F01 reused without bypass. No dependencies added.

Ordinary day:six complete-hour intervals anchored09:30, separate15:30–16:00stub; first/second cutoffs10:30/11:30. Nominal issue+2min, inclusive maximum+5min. Planned ceil(issue+1min) entries10:33/11:33 and exits14:33/15:33, each240min. Actual issuance shifts both planned entry/exit; no favorable fill selected. Early-close Nov27,2020 closes13:00, yields3 complete hours+stub and rejects both candidates. DST keys UTC; local events stable. Holiday:no origins.

SourceObservation carries native label/basis, nominal interval/basis, supported publication/basis and evidence reference. observation_at_cutoff uses each historical cutoff, never issuance, and rejects unknown/NaT/derived publication. DOCUMENTED is a caller assertion requiring evidence review, not an independently audited provider fact. Opt-in synthetic/assumed fixtures never set source_asof_verified. Legacy aggregation's assumed availability cannot certify this contract. origin_boundary computes only a clock/information subclaim, not full forecast/cross-section/risk admission; actual entry eligibility, label validity and outcome remain null. Scheduled histories must preserve missing slots; no48-window built.

**Validation:**18 focused tests passed3.39s; one integration suite129 passed7.06s; Ruff src/tests PASS. First scoped Ruff found6 line-length violations, fixed with formatting. No pytest failures. Final integration includes explicit NaT rejection. Existing F01 fixture rejects120min period-age despite60min publication-age; seven global blockers preserved. Small actual-calendar/synthetic-source traces are in clock_trace_examples.md.

Researcher-reported agreement on continuous240min and future conventional S&P500 is recorded **reported_agreement=true/formal_evidence_verified=false**. No attributable formal amendment found; signoff_pending.md gives exact registration requirements. Five authorities/CURRENT_PROTOCOL unchanged. Future instrument unselected; USA500/U1–U5/MC0–MC2 HOLD.

**Scientific dependencies:**unknown historical source publication, incomplete genuine minute/retry history, four action cash-date records and mapping/adjustment obligations,168 missing stock half-hours/full FT0 validity, formal shared registration and market-source contract remain. P1 findings reused; zero source reads/downloads/migrations. No labels/returns/portfolio/forecasts/models/confirmation outcomes. One scoped BLOCKED audit event preserves predecessor bytes; no blockers superseded.

**Next package:**P2.2 target/eligibility only under a separately authorized prompt. Synthetic interfaces may be scoped separately; real labels need actual minute references and maturity/split purging, reviewed source assumptions/formal common clock, and D13-C01 separation. Missing exits cannot decide contemporaneous entry. Trading/cashbook remains separately blocked. No automatic P2.2.

Git:feat/track-a-data-intake HEAD3fb0e17b093a4dc8afc52325ad2223dffa937b84; start clean, prior closeout already committed; fetched0ahead/0behind. No staging/commit/push/branch/integration action. Exact proposed path manifest in session report. **Human decision:APPROVE / CORRECT / HOLD** this implementation, independently of scientific readiness.

Resources:elapsed snapshot307.0s; added persistent source/test/report/docs/ledger delta68428bytes; source bytes/queries0; addedfiles8, modifiedfiles2; no data scans, fits or external source calls.
