# Canonical SPY → D7 handoff

Source engineering is complete. Upcoming P2.2/P2.3 packages can reuse:

```python
from lstm_data.market_source import MarketSource, load_market_history
from lstm_data.market_features import window_from_history

source = MarketSource.load()  # additive v3 policy, original source version
history = load_market_history(source)  # all 11 original chunks, SHA/schema checked
window = window_from_history(history, "2020-07-01", 1)
assert len(window.scheduled_ends) == 48
assert window.values is None and window.reason == "PUBLICATION_UNKNOWN"
assert not any(window.valid_mask) and not window.research_ready
```

MarketWindow retains scheduled UTC ends, each step's source IDs/reason and
floor/scaler references. It computes each step at its own information cutoff and
locks daily channels to its preceding completed session. Actual output values stay
None until independently supported source availability/action basis and approved
training-only certificates exist. Neutral zeros apply only after valid
standardization under the frozen historical-mask rule.

Existing synthetic certificate tests exercise 48×5 outputs and exact U1–U5
mathematics; synthetic_D7_regression.json records this run. Actual SPY floors and
scalers were not fitted. Frozen market_features.py bytes are unchanged.

load_market_history aggregates original native rows on demand; no derived raw
store. Complete hours are feature positions; the terminal stub supplies the daily
close. Derived evidence IDs now qualify constituent original request keys with
their native timestamps, making each hourly observation's lineage distinct.
Original parquet provenance keys and source bytes are unchanged.

market_source_integration.json uses actual canonical regular/DST/early-close
training rows. Native OHLC/request/row traces are in source_qa_full_period.json.
All real publication remains UNKNOWN, split scope false. An early-close origin
raises STRUCTURALLY_INELIGIBLE_ORIGIN. Missing rows keep scheduled slots and
source reasons; they never shift the window or receive fabricated raw prices.

Reproduction: existing pyproject setup, documented local SIP credentials and
canonical journal/data. Run the acquisition command in README for immutable
resumption; use a new report destination with python -m lstm_data.spy_qa for
offline measured QA. The original 13-attempt prefix is required; missing/tampered
journal fails before GET. Partial partition bodies are not durable and must be
re-requested within lifetime per-page/global guards. Complete chunks never refetch.

FT0 remains 16 stock channels, D7 five channels, eventual MC0 width 21; hidden
width 32, five prediction stocks, origins 1/2, TG0/C01/M2 and 240-minute timing
remain unchanged. No FT0 admission, model wiring, training, backtest or next
research stage is authorized by this handoff. ACTIVATION_PENDING.
