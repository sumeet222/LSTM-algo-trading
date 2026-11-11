# Codex Session Report

## 1. Session metadata

2026-11-10 America/New_York. HF20 Track 2 R01 deep dive.
Branch feat/track-a-data-intake, HEAD 8061483cb65d03264a7836b8b882123f67cbe4ad.
Tracked tree started clean. Untracked owner prompts, replication, earlier
Track 2 sources, tests, outputs and session notes were preserved.

## 2. Executive summary

Verified the three saved R01 books. The conservative net gain was
USD 10,488.39, led by a subset of long price outcomes. Matched
opportunities expose exit-price and risk-feedback differences. A
single follow-on vintage-reserve comparison is drafted. S2-C sizing is HOLD.

## 3. Research and protocol impact

No prior entry, exit, horizon, universe, data, model, sizing, cost or
frozen study rule changed. Analysis uses archived 2021–24 outputs.
Future extensions are read from the sealed offline table only.
The proposed refinement and overlay are explicitly unexecuted.

## 4. Files created

- src/lstm_data/trading/track2/rapid_r01_deep_dive.py contains the read-only
  extractor, causal opportunity reconstruction and matching audit.
- tests/track2_rapid_r01/test_deep_dive.py covers the dollar bridge, order
  fee sides, split units, drawdown, outcome-independent entry, and exit census.
- trading/track2/rapid_r01_deep_dive contains the input seal, derived
  CSV and Markdown, overlay-support audit, validation receipts and manifest.
  extraction_02 is the main result. extraction_01 is retained as the first
  successful reconciliation before additional rank and peer-state fields.

## 5. Files modified

Only new R01-owned code was refined during verification. Report-only
typing and schema fixes were checked against the extraction_02 results.
Frozen files were read in place.

## 6. Files deleted, renamed, or moved

None.

## 7. Critical interfaces

opportunities evaluates archived received frames using V1's R01 evaluator.
validated_legs joins by origin, ticker and sign and checks archived strength
and clocks. reconstruction transforms signed split quantities back to
entry units and matches actual raw-open and V3 execution-price rules.
financial_check validates the independently observed terminal snapshot,
daily marks, dollar components and count semantics. overlay_support.py
binds only archived availability and reference metadata. It places no orders.

## 8. Data and provenance

One 48-month verified raw projection per full descriptive extraction.
The bounded source fixture uses a January 2021 formation week and its
archived execution markers. Each final comparison uses the same
832 pre-funding candidates. The signed MRK terminal payable is −USD 34.02
in high-risk. The 2025 date is payable metadata. R01 cash accounting
uses raw shares. Cash dividends are outside the split-consistent signal.
The cohort archive omits exact individual action/carry and pre-order
risk-reservation records. Frozen aggregate categories remain available.

## 9. Dependency and environment changes

None. The existing .venv supplied pandas, Arrow and repository tools.
Sandbox Arrow CPU-cache probes issued warnings without affecting reads.
No source download, future prices, model inference or funded replay.

## 10. Commands and tests

    .venv/bin/python -m pytest -q tests/track2_rapid_r01 tests/track2_rapid_v3
    .venv/bin/ruff check --select E,F,I src/lstm_data/trading/track2/rapid_r01_deep_dive.py tests/track2_rapid_r01 trading/track2/rapid_r01_deep_dive/overlay_support.py
    .venv/bin/pyright --pythonpath .venv/bin/python --outputjson src/lstm_data/trading/track2/rapid_r01_deep_dive.py tests/track2_rapid_r01 trading/track2/rapid_r01_deep_dive/overlay_support.py
    .venv/bin/python scripts/check_python_types.py --pylance-dist ~/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist

12 tests passed. Ruff and targeted basic checking passed. Full diagnostics
and the final owned count are in the manifest. For editor verification,
select the repository .venv/bin/python, enable Pylance basic mode and
refresh Problems with the same extension version. The initial full check
identified stricter stub issues in new code. These were addressed using
validated column and monetary-scalar boundaries.

## 11. Experiment/results summary

Existing 2021–2024 result only. H85 +USD 10,488.39 net, standard
−USD 7,629.39, high-risk −USD 10,611.02. All 3,015 NAV rows and 3,510 physical
orders reconcile. 438 of 832 opportunities filled in all books. H85's
exit-price contribution against standard was +USD 14,320 on shared
opportunities. TSLA and AVGO jointly contributed USD 11,390 net.
H85 result is retrospective selection among 18 strategies, 54 V3 cases
and earlier screens.

## 12. Reproduction instructions

From the repository root, use a fresh output directory.

    .venv/bin/python -m lstm_data.trading.track2.rapid_r01_deep_dive /tmp/r01-source-fixture-new.json --fixture
    .venv/bin/python -m lstm_data.trading.track2.rapid_r01_deep_dive /tmp/r01-extract-new
    .venv/bin/python trading/track2/rapid_r01_deep_dive/overlay_support.py /tmp/r01-extract-new/R01_OPPORTUNITY_MATCH.csv /tmp/r01-overlay-support-new.json

The extractor validates its input seal, checkpoint, funded manifest
and file scope. Final-code reproduction is captured separately.

## 13. Git and collaboration

Fetched origin per repository instructions. Ahead/behind was 0/0 after
fetch. No commits, pushes, branch changes or integration. All new files
are local additive work. Keep the existing untracked work if integrating.

## 14. Known issues and limitations

Fully net cohort tails and exact timestamped per-order headroom are
unavailable. Archived legacy five-day sign and neural masks qualify the
reported classical availability lower bound. Conditional actions, shorts,
OHLCV cost proxies and fixed survivors limit inference. The raw analysis
used about 1.54 GB peak RSS including verification of the gzip checkpoint.

## 15. Decisions for review

Refinement registry remains NOT_EXECUTED. Predeclare untouched dates and
require source readiness before any evaluation. Preserve unchanged
controls. Do not use the 2021–24 winners to set a score cutoff.

## 16. Next step

If separately approved, run unchanged H85 and H100 against one H100
variant with a one-v20 pre-entry vintage reserve on a fixed untouched
period. Measure forced exits and exposure-normalized net with an order
audit. Keep S2-C sizing on HOLD pending that evidence.

## 17. Artifact inventory

The R01 deep-dive subtree contains the handoff, executed contract,
precise account bridge, matched opportunity and cohort records, offline
summary, refinement draft, overlay readiness and reproducibility receipts.
The content manifest binds code, tests and local research records.
