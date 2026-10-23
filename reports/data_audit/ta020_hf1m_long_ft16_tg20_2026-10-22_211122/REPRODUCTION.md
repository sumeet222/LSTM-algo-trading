# Reproduction

Use repository .venv setup and lawful private upstream source cache. No network, new dependencies or credentials. From repository root:

```bash
.venv/bin/python -B -m lstm_data.hf1m_ft16_prepare --out reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122
.venv/bin/python -B -m lstm_data.hf1m_ft16_audit --out reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122
.venv/bin/python -B -m lstm_data.hf1m_ft16_oracles --out reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122
.venv/bin/python -B -m lstm_data.hf1m_ft16_quality --out reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122
.venv/bin/python -B -m lstm_data.hf1m_ft16_report --out reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122
```

Existing preparation command checks sealed file hashes; numeric stores are not rebuilt. Audits/reports permit identical replay and reject changed immutable evidence. A fresh full derivation requires a NEW report/private output directory, the same frozen config plus recreated preflight/formula freeze evidence, exact approved parent manifests and source allowlists. No paths depend on a username. Do not redistribute ignored source/component/target stores or load untrusted checkpoint/pickle content. No model training command is part of Package020. Full focused test/static commands and final code hashes are in tests_static_receipt.json and the session report.
