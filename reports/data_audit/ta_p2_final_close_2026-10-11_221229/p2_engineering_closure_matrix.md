# P2 engineering closure matrix

P2_ENGINEERING_CLOSED_WITH_SCIENTIFIC_HOLDS — HUMAN_REVIEW_REQUIRED. Engineering completeness does not promote G0–G4.

| Phase | ENGINEERING_STATUS | SCIENTIFIC_STATUS | DATA_PENDING | TEST_EVIDENCE | NEXT_GATE |
|---|---|---|---|---|---|
| P2.1 | P2_1_ENGINEERING_VERIFIED | HOLD | P2-DEF-004, P2-DEF-009, P2-DEF-011 | tests/test_clocks.py; pinned summer/winter/early-close trace | Human scoped review; resolve register separately |
| P2.2 | P2_2_ENGINEERING_VERIFIED | HOLD | P2-DEF-004, P2-DEF-005, P2-DEF-006, P2-DEF-009, P2-DEF-011 | tests/test_labels.py; tests/test_hourly_proxy.py (original test bodies intact) | Human scoped review; resolve register separately |
| P2.3 | P2_3_FT0_ENGINEERING_VERIFIED | HOLD | P2-DEF-001, P2-DEF-002, P2-DEF-003, P2-DEF-004, P2-DEF-005, P2-DEF-007, P2-DEF-008, P2-DEF-014 | tests/test_stock_features.py; test_ft0_transforms.py; test_stock_source.py; test_m2.py | Human scoped review; resolve register separately |
| P2.4 | P2_4_MARKET_ENGINEERING_VERIFIED | HOLD | P2-DEF-002, P2-DEF-004, P2-DEF-005, P2-DEF-007, P2-DEF-008, P2-DEF-009, P2-DEF-011, P2-DEF-016 | tests/test_market_features.py; test_p2_market_closure.py; actual stock FeatureCalculator assembly test | Human scoped review; resolve register separately |

P2.3 real admission remains BLOCKED and P2.4 real market-state activation HOLD. No independent P2 algorithm/interface/test remains unimplemented. Real fit executors and P3/model/portfolio work are explicitly deferred or outside authority, rather than claimed implemented. The later P3 exception/benchmark decision (DEF015) is not a missing P2 clock or target algorithm.

Exact typed interfaces: [interfaces.json](interfaces.json); future boundaries: [P3 handoff](p3_engineering_only_handoff.md); remaining evidence: [register](p2_deferred_work_register.json). All 384 tests pass, static63-file errors/warnings0 and RuffPASS.
