# Package010 exact commands and verification

Repository setup remains README's `.venv` route including the preexisting neural extra. The new visualization extra pins Streamlit1.64.0 and Plotly6.3.1. Actual installation used `.venv/bin/python -m pip install streamlit==1.64.0 plotly==6.3.1 -c /private/tmp/ta010_core_constraints.txt`; dependency_delta.json records the exact seven core constraints. All existing installed versions remained unchanged. `pip check` returned0 with no broken requirements. For another prepared machine the documented command is `.venv/bin/python -m pip install -e ".[visualization]"`.

```sh
./scripts/run_track_a_dashboard.sh --check
./scripts/run_track_a_dashboard.sh
# Open the printed localhost URL; actual server was127.0.0.1:8501. Ctrl+C exited0.
./scripts/run_track_a_dashboard.sh --smoke
# Direct fallback, retaining project .streamlit/config.toml:
.venv/bin/python -m streamlit run apps/track_a_dashboard.py --server.address 127.0.0.1 --server.port 8501
# While running:
curl --fail http://127.0.0.1:8501/_stcore/health
# Override preferred port without public binding:
./scripts/run_track_a_dashboard.sh --port 8502
```

`--smoke` is the executed portable health/HTML/SIGINT test; it returned0, health200/ok, HTML200/7260bytes, measured startup0.777785s, HTML request0.001977s and shutdown0.507203s. The standalone interactive launcher was also started, printed its URL, and stopped via actual Ctrl+C with exit0. No server was left running. The sandbox denied listening/connecting sockets; the focused socket test and server checks were rerun with approved outside-sandbox execution. The initial failure and all corrected results remain documented. Native browser interaction could not be independently verified (IAB absent, Firefox changed during control, Safari timed out); no screenshot was created.

```sh
env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python -B -m pytest tests/test_visualization_readonly.py tests/test_aggregation.py tests/test_pilot_postrun.py -q
.venv/bin/ruff check .
.venv/bin/python scripts/check_python_types.py --pylance-dist /Users/pradeepgupta/.vscode/extensions/ms-python.vscode-pylance-2026.4.1/dist
git diff --check
.venv/bin/python -m pip check
```

Focused release returned0:19passed in10.69s. Ruff and diff check returned0. The installed-extension checker returned0:194files,0errors,0warnings. The absolute extension argument records this machine's installed checker/stubs; substitute the installed extension `dist` on another machine. Use the repository .venv interpreter and Pylance basic; reload the language server/Problems and have a human confirm editor parity.

A portable minimal programmatic UI reproduction (no server/browser required):

```python
from pathlib import Path
from streamlit.testing.v1 import AppTest
at = AppTest.from_file(str(Path.cwd() / "apps/track_a_dashboard.py"), default_timeout=60).run()
assert not at.exception and not at.error
for section in ("Price & Features", "Predictions & Errors", "Training Diagnostics", "Research Notes / Provenance"):
    at.sidebar.radio[0].set_value(section).run()
    assert not at.exception and not at.error
```

The actual extended run exercised18cases, detailed in app_interaction_smoke.json/.txt: default price/T5; stock/interval/feature changes; event markers; faithful SMA; paired neural scores; both folds; numerator/MAD/floor reconstruction; E5 peers; MC1 gates; provenance and aggregate/batch training diagnostics. Its first temporary harness used an AppTest-relative path and failed before app execution; it was corrected to `Path.cwd()` and the draft failure is preserved. Programmatic timings measure AppTest server-side work, not browser drawing time.

Final missing-artifact diagnostic batch: identical focused command returned0,19passed in14.85s; identical static command returned0,194files/0errors/0warnings in23.266s. --check returned0 with538dependencies. The two final AppTest checks had no errors or exceptions; final_UI_diagnostic_smoke.json records timings.
