# Reproduce the read-only attribution

Run from the project root with the existing `.venv`; no package installation or
secret is needed for this task. Required local external artifacts are the frozen
final-slate `analysis_03`, `runs/sizing-matched-20261110-r1/results`, final registry,
content manifest and stage012 model/protocol anchors listed in SOURCE_REGISTER_BEFORE.
They are intentionally not copied here. A clone needs these documented exact-hash
research artifacts supplied from the project's archive, not vendor downloads.

Executed main command:

```sh
.venv/bin/python -m lstm_data.trading.track2.final3_risk_attribution.cli --run-id analysis_01
.venv/bin/python -m lstm_data.trading.track2.final3_risk_attribution.reporting --run-id analysis_01
.venv/bin/python -m lstm_data.trading.track2.final3_risk_attribution.supplement --run-id analysis_01
```

Before the first command, `io.prepare()` captured SHA256 and local mtimes and sealed
the protocol. The final CLI offers a portable fresh-namespace version of that step:

```sh
.venv/bin/python -m lstm_data.trading.track2.final3_risk_attribution.cli --prepare --output-root trading/track2/final3_risk_attribution_reproduction_01 --run-id analysis_01
.venv/bin/python -m lstm_data.trading.track2.final3_risk_attribution.reporting --output-root trading/track2/final3_risk_attribution_reproduction_01 --run-id analysis_01
.venv/bin/python -m lstm_data.trading.track2.final3_risk_attribution.supplement --output-root trading/track2/final3_risk_attribution_reproduction_01 --run-id analysis_01
```

Use a fresh output-root each time; every publication uses exclusive creation. This
also captures that machine's source mtimes after SHA verification. Existing outputs
are never truncated or overwritten; a failed run keeps START/HOLD evidence and a
completed run cannot be restarted over itself. An interrupted analysis can be
reaggregated in a new uniquely named output namespace because it has no trading
state and cannot double-book actual orders. Inspect prior receipts first.

Main aggregation measured 10.558 seconds, peak process RSS 199.26 MB on macOS,
Python 3.14.6. It reads existing daily/cohort/fill files once into shared tables;
bounded discovery and a later projected physical-year supplement are separate reads.
The supplement reads only 16,758 existing fill records, not market-source partitions.
No original forecasts or massive V5 journals are traversed. Output sizes and hashes
are in ANALYSIS_MANIFEST.json; main runtime excludes tests, documentation and global
static checking (184.383 seconds reported by the global checker).

```sh
.venv/bin/python -m pytest -q tests/track2_final3_risk_attribution
.venv/bin/ruff check --select E,F,I src/lstm_data/trading/track2/final3_risk_attribution tests/track2_final3_risk_attribution
.venv/bin/pyright --pythonpath .venv/bin/python src/lstm_data/trading/track2/final3_risk_attribution tests/track2_final3_risk_attribution --level error
.venv/bin/python scripts/check_python_types.py --pylance-dist <installed-pylance-extension>/dist
```

Final owned editor-stub configuration is recorded in validation/OWNED_PYLANCE_FINAL_02.json; global 32 inherited diagnostics are preserved in FULL_PYLANCE_RAW.txt. Final
numerical policy matches the sealed ANALYSIS_PROTOCOL; later code changes repaired
rendering/type/schema issues and added output-root configuration, not a new financial
rule. START.json and the final manifest retain both executed and final code hashes.
No new trading, neural or market-source procedure is part of reproduction.
