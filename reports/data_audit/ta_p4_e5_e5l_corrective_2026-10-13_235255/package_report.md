# Corrective P4.8/P4.9 package report

**P4.8_PARTIAL / E5_HEALTH_BLOCKED. P4.9_SYNTHETIC_ENGINEERING_PASS.**
One consolidated human review remains. Scientific G0–G4 HOLD; real G5/G6/G7
NOT_RUN; real pairs 0/40. Upstream MC0/MC1/P4.6/P4.7 acceptance REVIEW_PENDING.

The approved additive layout uses once-only H/L flags: 163 LL0 and 198 LL1/sham
penalized slopes, with a separate free intercept. The researcher's explicit
clarification resolves the prompt's 162/197 arithmetic inconsistency. Canonical
offsets 0:112/112:147/147:161/161:163/163:198 and all 198 names are recorded.
Seven repeated flags would reduce effective shrinkage to lambda/7 and are not
equivalent. No frozen protocol or collaborator sign-off was changed.

## E5 failed proof preserved

Original initial/final/zero-peer MSE: 0.2256385386/0.1439103037/0.2152040154.
Required bounds: <0.0789734885 and >0.2878206074; both fail. Current initial
MSE reproduces exactly, with zero new optimizer steps or 60-update reruns.
There is no demonstrated implementation defect. The toy target is its input
endpoint peer mean, mathematically identifiable but missing mature TG0 clocks.
See `e5_health_failure_diagnosis.md` and `health_diagnosis_final.json`.
Actual E5 D6g calibration/refit/final checkpoint/reload/P3 forecast remain NOT_RUN.
A separately specified v2 chronology/TG0 fixture and 256-update cap are proposed
for explicit review, neither approved nor executed.

## Actual directed ridge fits, final checkout

| Fixture | LL0 held-out TG0 MSE | LL1 | Ten-session sham | Selected lambda (LL0/LL1/sham) |
|---|---:|---:|---:|---|
| NULL | 0 | 0 | 0 | 1.0/1.0/1.0 |
| FORWARD | 0.041100282 | 2.6605979e-09 | 0.041736638 | 0.1/0.0001/1.0 |
| REVERSE | 0.036375824 | 3.940078e-09 | 0.036663707 | 0.1/0.0001/1.0 |


Both predeclared forward and reverse prior-hour dependencies were recovered;
all null slopes and intercepts are zero, with exact ties choosing lambda 1.
The original solver runs five candidate lambdas and exactly one fresh full-prefix
refit per arm. No neural LL model, new solver, penalty, transform formula,
held-out fitting or economic replay was introduced.
Shared cohorts have 74 training,
110 validation and 200 refit origins;
validation adequacy is {'origins': {'1': 55, '2': 55}, 'sessions': 55}. The 63-calendar-session tail is fixed;
early ASOF windows that predate fitted preparation are rejected equally.
Exact source clocks, 49th full-hour antecedent, fit/order/pair hashes, masks,
weights, preparation IDs and exclusions agree among all three arms.

The sham changes only 35 directed columns to the same stock/slot ten earlier
eligible XNYS sessions. Older original publications remain original; the bound
fit transforms those known raw values at the current input step. Missing shifted
slots reject the whole origin equally. It is a weak diagnostic, not a p-value,
causal-transmission claim or statistical alpha result. Coefficients include
current/prior and reverse channels; none were selected by reported performance.
Some frozen directed lag columns are identical by construction: H_TO_L_1:lag0
equals H_TO_L_0:lag1 (and the reverse pair likewise). Individual coefficients
are not unique causal attribution; the combined signal and matched predictive
comparison are the supported toy diagnostic. All specified columns and penalties
remain present, with no result-based removal or renormalization.
Five-score examples use retrospective fabricated full-prefix preparation and
are explicitly HISTORICAL_TRAINING illustrations, not final ASOF/P3 forecasts.

## Verification and conservation

Full pytest: 670 passed in 5998.37s on unchanged final Python.
Comprehensive basic Pylance/Pyright: 145 files,
0 errors/0 warnings. Ruff, AST and diff check PASS. Commands and code SHAs are in
`checks.json`. Initial 3 Ruff and 3 type diagnostics were repaired without ignores,
severity changes or test weakening; their failed logs remain disclosed.
The preliminary forward fit was cancelled without a fit conclusion after a
one-second profile found locale-heavy timestamp repr hashing. New D8 metadata
uses versioned typed JSON/ISO clocks without omitting fields; protected legacy
encodings and numerical/source validation are unchanged. Its partial log remains
disclosed and is superseded by the three final-checkout regression fits.
Full regression was run once after the final functional edit.

All 402 protected native source/manifest files and the entire old partial packet
are unchanged. Of 1780 protected paths, only the three authorized source edits
changed. Original protocols, ledger, 16 P2/33 P3 deferrals and 7 blockers are intact.
No .env, provider request, real price/feature/label record, confirmation outcome,
universe activation, dependency, commit or Git integration occurred. Current
HEAD remains `9384fc0dc26b8bdb8485e0f26680d4f77b732ac9`. See `preservation_final.json` and integration manifest.
Reusable functions support ordered fictional universes; old 147/161 numerics and
TM0/MC0/MC1 tests remain intact. Code changes invalidate prior fitted code hashes;
do not reuse stale checkpoints even though upstream numerics are conserved.

## Reproduction and next decision

Use the existing README setup with approved torch2.10.0. No credentials or source
archive is required. Run focused tests and the comprehensive commands in APIv2;
the three actual-fit regressions write compact `ridge_case.json` files in pytest
temporary directories. CLI `directed_ridge_audit` reproduces each predeclared case
to a new audit path. All persistent final evidence is in this packet.
Review the12–16-check card and decide separately whether to approve the proposed
E5 health fixture revision. This package does not clear scientific holds or
authorize P4.10–P4.13, observed fits, trading or Git integration.
