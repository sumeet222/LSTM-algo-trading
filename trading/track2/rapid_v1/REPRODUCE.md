# Reproduce Rapid V1

Run the following from the repository root with the existing .venv and the
local Stage35/V5 raw-share source and action cache. The registry binds the root
menu, strategy code, source receipt and numerical choices. The feature manifest
lists all sixty raw monthly partitions. The preparation and screen are offline.

    .venv/bin/python -m lstm_data.trading.track2.rapid_v1.cli list
    .venv/bin/python -m lstm_data.trading.track2.rapid_v1.cli freeze
    .venv/bin/python -m lstm_data.trading.track2.rapid_v1.cli validate
    .venv/bin/python -m lstm_data.trading.track2.rapid_v1.cli prepare

Use the cache path printed by prepare. If the current cache already exists,
reuse it after the loader validates its SHA256 and feature-code identity.

    rapid_cache=trading/track2/rapid_v1/cache/49a590a7d44f5900b67cf2faf37584b584a942807cca2fbab262250b80ea1f93
    .venv/bin/python -m lstm_data.trading.track2.rapid_v1.cli pilot --cache "$rapid_cache"
    .venv/bin/python -m lstm_data.trading.track2.rapid_v1.cli benchmark --cache "$rapid_cache"
    .venv/bin/python -m lstm_data.trading.track2.rapid_v1.cli screen --cache "$rapid_cache" --run-id NEW_UNIQUE_ID
    .venv/bin/python -m lstm_data.trading.track2.rapid_v1.cli verify --run trading/track2/rapid_v1/runs/NEW_UNIQUE_ID/results
    .venv/bin/python trading/track2/rapid_v1/analyze_screen.py trading/track2/rapid_v1/runs/NEW_UNIQUE_ID trading/track2/rapid_v1/runs/NEW_UNIQUE_ID/analysis

Resume an interrupted screen after checking its process, completion receipt
and checkpoint. Use cli resume with --cache and --run <run-directory> under
the same registry, cache and period. The CLI checks those identities and locks
the screen before restoring. Verify a completed run from its existing outputs.
Annual states include the last committed session, cash, open lots, orders,
dividend/OGN claims, budgets and outcome queue. Restart begins at the next session.

The exploratory outputs use the fixed survivor universe and retrospective V5
action assumptions. Prices use the OHLCV execution proxy. Borrow, receipt
timing and friction are modeled. Independent inference is a separate task.
