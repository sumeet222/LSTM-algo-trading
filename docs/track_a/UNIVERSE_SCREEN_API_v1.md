# Candidate universe structural screen v1

TA-UNIVERSE-RETENTION-SCREEN-001 is a candidate-only source study. It does not
switch the original universe, activate its warm-up overlay, fit transforms or
labels, run historical trading, or clear scientific gates. All permitted panels
retain exactly one original/backup in each ordered sector slot:
AAPL/MSFT, JPM/BAC, JNJ/MRK, WMT/COST, CAT/HON.

## Reproduction

Use the README environment and run from the repository root. Original immutable
stock and remediation archives are required for attribution. Use a **new** report
directory; no older output is overwritten.

```sh
.venv/bin/python -B scripts/run_universe_screen.py --phase attribution --report reports/data_audit/new_universe_screen
.venv/bin/python -B -c 'from pathlib import Path; from lstm_data.config import write_json; from lstm_data.universe_screen_source import pilot_plan; write_json(Path("reports/data_audit/new_universe_screen/backup_pilot_plan.json"), pilot_plan())'
.venv/bin/python -B scripts/run_universe_screen.py --phase pilot --report reports/data_audit/new_universe_screen --env-file .env
.venv/bin/python -B scripts/run_universe_screen.py --phase analysis --report reports/data_audit/new_universe_screen
```

Pilot execution uses only the existing dotenv/Alpaca credential mechanism, with
no secret output. A completed archive resumes with zero GETs and no credential
loading. Historical vendor revisions may change newly retrieved bytes; preserve
canonical request/response/chunk hashes and do not promise a historical vintage.
The source namespace is `data/raw/alpaca/track_a_backup_candidate_v1`, shared by
all hypothetical panels. Never create a panel-specific raw store. Sharing or
recreating ignored source data remains subject to legitimate provider access.

The present package has a separately human-approved one-attempt exception for
its first formation page after three sandbox transport failures. Its six-record
journal prefix and exact page hash are bound in the report. All attempts remain
charged; the total is capped at 1000. Do not copy that exception into a fresh
journal or extend it to another page. Ordinary pages retain three lifetime
attempts. First 401/403/429, schema divergence or client validation/pagination
failure creates a persistent stop. Budget and 256 MiB storage limits fail closed.

## Structural interfaces

`verify_screen_authority()` checks the SHA-bound 16-entry P2 handoff and 33-entry
P3 v2 register; all scientific HOLD/NO_AUTO_CLEAR statuses remain. `primary_native`
reads only partitions ending before the requested training/development stop;
confirmation Parquets are not opened. `gate_a` reuses the original stock source,
FeatureCalculator and mechanical M2 presence rule, preserving 1502 train origins,
48 scheduled complete hours and all sixteen FT0 channels. Original and authentic
warm-up retention are independently reproduced; exact per-stock/channel masks and
first failures are retained. Technical source coverage is separate from actual
publication, action scope and empirical normalization eligibility.

`diagnostic_history(frame, symbols, start, stop)` is an isolated ordinal alias
adapter to the unchanged P2 names. Actual ticker identities remain in source IDs
and a distinct candidate universe binding. No global UNIVERSE or feature formula
is changed. The original and diagnostic adapters produce identical actual bar,
daily and calendar fields for the original training source; synthetic formula
parity and alternative P3 identities are tested. Its results are for source-only
masks; no scientific or production input admission is created.

`counterfactuals(rows)` requires exactly 1502 unique origin IDs and produces all
32 perfect-mask removal bounds. Removing a mask is not recovery, a valid feature
sample or a stock substitution. Counts of per-stock/channel losses overlap;
only the rejection union determines panel retention.

`t2_absence_bound(calendar, missing_daily_closes)` derives **necessary** T2
failures from observed missing terminal native bars. It assumes every other close
exists, uses the original `covered(...,20,19)` predicate on presence tokens, and
projects invalid daily states through the exact 48-step origin window. It creates
no price, return, target, imputation or fitted parameter. Other indicators, unknown
source gaps and causal HOLDs can only worsen the optimistic bound. An independent
calendar oracle and exact original JPM/JNJ T2 masks verify the propagation.

`analyze_pilot(report)` verifies immutable raw/split/day/native chunks, 60 exact
formation sessions, fixed RTH/DST/early-close grids, adjustment controls and the
32 fixed panel identities. No complete backup retention is claimed without full
history. In this study, the financial slot alone has either 228 original JPM
failures or at least 216 BAC T2 failures, so the all-panel ceiling is 1286/1502.
The bounded study stops with source QA on HOLD. Additional unknown context does
not fix the currently observed gaps. Genuine new observations for those exact
missing keys could change the bound; no permanent provider incapacity is claimed.

## Evidence and limits

The canonical QA is **backup_source_qa_v2.json**. Preliminary v1 incorrectly tagged
HON's coupled-volume control as PASS; v2 preserves the observed discrepancy as
INCONCLUSIVE and the old evidence remains auditable. HON's post-study reverse
split supports a retrospective basis explanation, but exact adjustment/rounding,
action vintage and raw execution conversion remain unverified. No row was edited.

All 31 backup-containing full panels, annual 98%/95% coverage, backup development,
regime classification and genuine maturity gates remain NOT_MEASURED/INCONCLUSIVE.
The bound is sufficient to reject the present source as a 90% rescue, without
claiming actual candidate fractions. Original development 496/496 and WF1/WF2
248/248 are independently calendar-reconciled disclosures after the training-only
decision froze; they did not alter ranking or acquisition priority. SPY was not
queried, its source hashes are preserved, and actual market publication remains
unknown. Confirmation feature/label/return/performance analysis is prohibited.

A future ex-post data-usability substitution requires a versioned human-approved
sensitivity and hindsight/survivorship disclosure. Formation membership/release,
source clocks/actions, real training fits, shared/course approvals and execution
remain independent scientific HOLDs. A changed universe would need new TG0
cross-sections, feature/certificate fits, matched P3.5 refits and D8 identities
before separately authorized P4. This package performs none of those steps.
