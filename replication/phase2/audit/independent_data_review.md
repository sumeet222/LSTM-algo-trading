# Independent review of new geometry, dataset and feature implementation

Status: targeted review and synthetic frontier checks PASS after correction of the M2 assembly bug described below. Ten independent tests pass in 9.333 seconds. Basic Pyright for new `geometry.py`, `dataset.py`, and `tests/test_frontiers_review.py` reports **0 errors, 0 warnings, 0 informations**.

Authority was solely `replication/EXPERIMENT_SPEC.md` §§3–10. Reviewed only the new `code/geometry.py`, `code/dataset.py`, and `code/features.py`; no original implementation, old tests, old configs, old result, raw market data, or protected partition was opened. Imports used the new boundary and existing public third-party packages. No fitting, network, package installation, or Git operation occurred during this review.

## Finding: blocking M2 advanced-index broadcast error — corrected

The initial assembler used `m2[steps, stock_indices, contexts]` with index shapes `(origins,48)`, `(1,1,20)`, and `(origins,1,1)`. A two-origin independently constructed fixture failed with an `IndexError` because these arrays cannot broadcast. The lead corrected the first index to `steps[:,:,None]`, giving `(origins,48,1)` before transposing the gathered result to origin/stock/time. The reviewer did not edit `features.py`.

The independent fixture now verifies the output shape `(2,20,48,16)`, reordered origin calls, multiple stock positions, first/interior/last historical steps, all fifteen common channel slots, the M2 slot, the forecast origin's fixed context at every historical step, and unchanged clock order. This closes the discovered assembly failure without changing the research definition.

## Other reviewed behavior

The calendar uses the literal holiday and early-close rules, includes the listed exceptional closures, and extends calendar lookup without market observations into early 2025. Inputs retain only full hours; normal closing stubs and half-day stubs do not enter the grid. Opening origins select the previous full-hour end, other origins select the hour ending at their nominal time. The forty-eight-position window remains intact.

The source-input gate is separate from twenty-name endpoint-label scoreability. Genuine main labels are independently constructed for M2, so source/input rejection by another stock does not suppress those historical label slots. The COP origin/endpoint basis comparison rejects the spinoff crossing; its native/input exclusion uses the preceding-regular-day 126-position envelope and trailing forty-eight-position AND. Volume regimes remain separate from split-adjusted price bases. These points were reviewed directly; inherited minute QA/action/proxy validity is outside this review and remains the lead's D0 responsibility.

Role selection requires maturity strictly before the local stop-date twenty-hour cutoff and first-window date strictly after embargo. Latest selector coverage windows are considered July, June, then May, with all seven slot requirements. The synthetic tests cover equality at both boundaries and Friday/half-day nominal origins whose labels mature in the next session. No same-day origin substitution or invented missing target enters the test.

M2 preserves scheduled regular-origin slots, all seven forecast contexts, and the strictly-before-open maturity mask. Its historical session state is fixed within a day. Early-close inputs require sixty prior regular positions for both the twenty-position mean and sixty-position RMS. The fixture confirms a label maturing exactly at the lock remains missing, a label one minute earlier is admitted, and the missing slot is not replaced with an older label.

The phase fit-index union uses source-input eligibility independently of future primary label completeness, deduplicates overlapping histories, clips hours to the declared phase dates, and selects the first included hour per date. A fixture flips scoreability while holding source eligibility fixed and verifies an unchanged fit population.

## Independent future perturbation test

A synthetic 150-session, twenty-stock population has nonconstant prices/volumes, full common-feature warmups and seven M2 contexts. After fitting a prefix recipe, the test changes later source prices, volume, and later signed labels, reconstructs the components, and refits the same prefix. The full recipe dictionary remains exactly equal; all earlier transformed common features and scaled M2 values remain exactly equal. Later M2 values change once the changed labels have matured, demonstrating allowed causal history updates rather than a globally frozen M2 series.

The synthetic feature fixture is deliberately an abstract weekday schedule, not an exchange-calendar certification. Separate tests use the complete new literal calendar for the six specification endpoints, exact-close equality, DST, Thanksgiving half-day, New Year Saturday behavior, Juneteenth and exceptional closures. Main-target scale and auxiliary-weight population invariance remain the model-phase gate's responsibility; this review does not claim to test functions it did not import.

## Static-only fixes and verification

At the lead's request, the reviewer made minimal static fixes in the new `geometry.py` and `dataset.py`: schedule iteration uses integer positions already defined by the fresh schedule, timestamp objects are checked before accessing `.value`, ISO-date arguments are explicit strings, and the heterogeneous numeric array dictionary is annotated as NumPy arrays. Numeric NPZ serialization now explicitly sets `allow_pickle=False`, which does not change the stored numeric arrays. No target, feature, role, action, eligibility or calendar definition changed.

No casts, `Any`, ignore directives, severity reductions, or weakened tests were added. The ten tests were rerun after these changes. The isolated static command form, with `REPO_ROOT` expanded to the active checkout, was:

```sh
"$REPO_ROOT/.venv/bin/python" -I -m pyright --project "$REPO_ROOT/replication/phase2/audit/pyright_evaluation.json" --pythonpath "$REPO_ROOT/.venv/bin/python" "$REPO_ROOT/replication/phase2/code/geometry.py" "$REPO_ROOT/replication/phase2/code/dataset.py" "$REPO_ROOT/replication/phase2/tests/test_frontiers_review.py"
```

Test execution used the existing `.venv/bin/python -I`, a clean `/private/tmp` working directory, explicit new phase-2 code on `sys.path`, and `boundary.install()` before public third-party imports. `runpy.run_path` executed only `tests/test_frontiers_review.py` as `__main__`. The lead's overall runner can include this suite alongside its comprehensive mathematical feature tests.

Pylance editor confirmation remains human-owned: select the repository `.venv/bin/python`, retain basic severity, restart/refresh the language server and verify Problems for these new files. This targeted check is not an original-project-wide static or editor verification. The lead owns the combined session report, full code freeze and empirical data-gate receipts.

Reviewed/tested snapshot SHA-256 values (the lead's final freeze may supersede this snapshot):

| New file | SHA-256 |
|---|---|
| `code/geometry.py` | `32dad3f6291838d02bf1a29203732cacb4f3017680bb60b8613ec82750fc8837` |
| `code/dataset.py` | `57e8408e34e8877b6c3624ea9a9945fb560c03af27813f9b7b14c2208d48ca7c` |
| `code/features.py` | `a48720cbf321c6168b2dea3090175d1a215865fc09f3b31ed62d16e21662521a` |
| `tests/test_frontiers_review.py` | `8fd7a1e31384ef07254bbf8f280b7301f86d44ddf57851d3e29b8860946448e3` |
