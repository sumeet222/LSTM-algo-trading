# Implementation and reproduction

Code follows the established installable `src/lstm_data/trading/track2/stage012/` namespace; tests under `tests/track2_stage012/`. Review artifacts under this directory. Run from repository root with the documented existing environment including the neural optional dependency:

```
.venv/bin/python -m pytest tests/track2_stage012 -q
```

No PYTHONPATH, network, keys, paid providers or new packages required. Original archive paths must exist and match registry; the archive files are gitignored local artifacts and are not copied into this package. A clean clone without these archives cannot run original-load tests; obtain the frozen authorized bundles using the registry rather than regenerate them. Calendar and pure-domain tests can still run independently.

Protocol numerical defaults require human review. Source modules contain explicit default values matching protocol.json and are checked against the contract by tests; no implicit fitting. This version is a bounded interface package, not a simulator. See OPEN_ISSUES and STAGE012_HANDOFF before any downstream use.
