# Owned static-check receipt correction

The first directory-based editor-stub config analyzed zero files and is NOT accepted
as validation. Its receipt is retained for transparency. The corrected explicit-file
profile in `validation/OWNED_PYLANCE_FINAL_02.json` analyzes all nine owned Python
files (eight package files plus one test), with zero errors/warnings. It uses basic
severity, the existing repository .venv and installed Pylance stubs without exclusions,
ignores or severity reductions. This is the authoritative final owned receipt.

The 780-file full-project snapshot has 32 inherited errors; the later explicit owned
profile includes the supplemental utility not present when that snapshot's file list
was captured. No whole-project zero-error claim is made. Final pytest has 16 passes;
Ruff E/F/I passes. These results supersede initial owned lint/type failures, all of
which were corrected and whose receipts are retained. No numerical policy changed.
