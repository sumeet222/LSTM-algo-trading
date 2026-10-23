# Release lineage

`release_gate.json` is the current Package020 readiness decision and binds the immutable `model_input_contract.json` by SHA256. The preparation contract retains its publication-stage PENDING_INDEPENDENT_QA status; the completed gate supplies the later FEATURE_READY_FOR_TRAINING decision without rewriting preparation evidence. Both deny model-training authority. The next training manifest binds both files.

Original preparation-time code snapshots match all five execution hashes exactly. Later type-safe indexing/strict loader guards did not change numerical arithmetic. QA/report helpers and final prose are bound by final_code_and_static_receipt_v2.json. Source/target/component bytes are unchanged and all oracle/prefix/batch checks passed. The root019Bregister and its release bindings remain unchanged.

An initial longer review card is preserved as initial_review_card.md.txt; the current human_review_card.md contains the same result with concise preprocessing/resource details. No prior package reports were overwritten.
