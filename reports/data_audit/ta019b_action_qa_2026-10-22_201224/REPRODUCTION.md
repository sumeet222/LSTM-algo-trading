# Reproduction

Use the repository authoritative .venv setup and exact active018D allowlist; no new credentials or downloads. From repository root, inspect the registered code/config/input SHAs before running. Reusing this sealed packet verifies completed checkpoints; a full new derivation must use a NEW --out directory and reproduce the documented discovery/closure order.

```bash
.venv/bin/python -B -m lstm_data.hf1m_action_source --out reports/data_audit/ta019b_action_qa_2026-10-22_201224
.venv/bin/python -B -m lstm_data.hf1m_action_release --prepare-events --boundary-proofs --out reports/data_audit/ta019b_action_qa_2026-10-22_201224
.venv/bin/python -B -m lstm_data.hf1m_action_masks --out reports/data_audit/ta019b_action_qa_2026-10-22_201224
.venv/bin/python -B -m lstm_data.hf1m_action_release --finalize-fields --verify-samples --out reports/data_audit/ta019b_action_qa_2026-10-22_201224
.venv/bin/python -B -m lstm_data.hf1m_action_docs --out reports/data_audit/ta019b_action_qa_2026-10-22_201224
.venv/bin/python -m pytest tests/test_hf1m_action_source.py tests/test_hf1m_action_audit.py tests/test_hf_minute_long.py -q
```

The final mask CLI emits v2 files and refuses unresolved scan candidates. Root-register publishing refuses replacement with different content; preserve this root and generate a separately named successor for any changed evidence. Price-bearing Parquets and trusted-local compact pickle checkpoints stay ignored. Never load untrusted pickles. Source checkpoint replay uses the explicit code-compatibility amendment; full new runs bind current code directly. Public URLs establish event facts, not vendor-feed certification. No FT/TG or training command is part of this procedure.
