# Track A research explorer — five-minute Quickstart

Open the repository folder in VS Code, then **Terminal → New Terminal**. Run commands from the repository root. Complete the README setup (including its existing `neural` extra) first. The app uses the repository `.venv`; you do not need to activate it. Streamlit and Plotly are free packages installed locally. If they are missing, the one setup command is:

```sh
.venv/bin/python -m pip install -e ".[visualization]"
```

This visualization extra is pinned in `pyproject.toml`. It adds no paid service, account or API key. Follow the main README first if `.venv` itself is missing. Existing licensed source files and completed research artifacts must already be provisioned on this machine; the app does not download them.

Launch:

```sh
./scripts/run_track_a_dashboard.sh
```

The terminal prints **Open http://localhost:8501 in your browser**. Open that URL. If8501 is occupied, the launcher selects the next free local port and prints the actual URL. Direct fallback:

```sh
.venv/bin/python -m streamlit run apps/track_a_dashboard.py --server.address 127.0.0.1 --server.port 8501
```

Your first three clicks:

1. In **Start Here**, click **Open Price & Features**. Keep **AAPL / WF2 / TM0 / Development / January 16–19,2024 / Both origins**. These are verified available dates. You will see 52 genuine30-minute candles, volume directly underneath, and native **T5** below. Hover for exact ET/UTC, OHLC and volume. Scroll/zoom or drag to inspect.
2. Switch **Candle interval → Completed hour**: there are24 complete hours. Try **M1** in the FT0 selector and switch **native/scaled**. Enable **Show forecast / horizon events**. The four-hour future label close and three-minute nominal event times are explicitly marked; none is a fill.
3. Open **Predictions & Errors**, then **Training Diagnostics**. Inspect saved score versus EX-POST TG0, the five-stock ranking table, and calibration clipping separately from fresh refit. Diagnostics defaults its tail/loss scope to the recorded refit-training panel; its partition is labeled independently of the sidebar.

Candles are retrospective vendor split-adjusted USD with inverse-split volume. Native features, training-scaled model inputs and dollar prices have different units. T5 is `(RSI14−50)/50`; M1 is normalized momentum, not raw return. TG0 is future relative performance, not absolute return direction. Rank IC and MSE do not establish alpha or profitability.

Stop with **Ctrl+C in the launching terminal**. Useful checks:

```sh
./scripts/run_track_a_dashboard.sh --check
./scripts/run_track_a_dashboard.sh --smoke
./scripts/run_track_a_dashboard.sh --port 8502
curl --fail http://127.0.0.1:8501/_stcore/health
```

`--check` validates local bindings without starting a server. `--smoke` starts the app, checks local health/HTML, measures startup, then stops its own server. The curl command applies while a server is running.

For missing files, read the exact path in the app and provision the original artifacts using `data/README.md` and their manifests; do not substitute or retrain. For empty origins, try the verified default dates and **Both**. E5/MC1 have only WF1. To inspect the AAPL2020 split, choose **WF1 / Refit training**, then August28–31,2020; the chart retains a single retrospective scale. Dates are ET inclusive; hover preserves true UTC and DST. See the [User Guide](Visualization_User_Guide.md) for details.

Everything binds to localhost; telemetry collection is disabled. No public publishing or bulk raw-data export is provided. Local rights/clock/action assumptions remain qualified. Check applicable rights before sharing raw-data screenshots.

Package011 adds saved H1/T1/T2/O1 arms with explicit seed labels. **TM0 remains C0 seed42**; use **C0 [123]** for seed123 comparisons. Follow the [five-step Package011 guide](../../reports/data_audit/ta011_controlled_interventions_2026-10-15_124546/HOW_TO_VIEW_PACKAGE_011.md) for matched comparisons, original-scale TG0 and actual clipping diagnostics. Only completed cases appear; the explorer never starts training.
