# SPY source and D7 API

This is a source/feature foundation; no FT0, model or portfolio integration is claimed.

- `MarketSource.load()` validates the versioned SPY-only config. `partitions()` computes
  eleven fixed UTC-bounded intervals, starting March19,2020 and ending June30,2025.
- `HistoricalClient` supplies bounded retries and complete pagination; `save_chunk`,
  `read_verified` and `chunk_paths` supply immutable request-keyed resume. Missing or
  interrupted chunks fail closed. The canonical transport journal survives report changes.
- `hourly_archive(frame,start,end)` reuses the existing half-hour aggregation. Known
  period ends are retained; assumed `available_at` is replaced by UNKNOWN/NaT. It emits
  complete hours and closing stubs in memory, with constituent request lineage, not
  another stored panel. The original stock/hourly aggregator remains byte-identical.
- `history_from_archive(calendar,hours)` creates actual-source observations with UNKNOWN
  publication and unverified split scope. Terminal interval close is a closing value;
  no daily open/OHLC is invented. Real SPY history is currently absent and must block.
- `MarketHistory.measures(step)` computes log(C/O), scheduled RMS12/60, preceding-session
  daily RMS63 and complete5/20 daily momentum chains at that step's own source cutoff.
- `MarketFloors` binds positive hourly/daily floor, separate training timestamp sets,
  source version, fit window, basis and evidence. `fit_synthetic_floors` pools positive
  hourly RMS12+60 for p05 and distinct actual daily-close samples for daily p05. No
  empirical fitting is performed or authorized by existence of this verification function.
- `vector(measures,floors)` emits exactly U1–U5 or a blocked reason. Public certificates
  are caller assertions, not provider clock proof or verified floor population. SYNTHETIC
  requires explicit opt-in; real gates stay held even for caller DOCUMENTED assertions.
- `fit_synthetic_scaler` fits each unique timestamp once, rejects conflicts, applies
  median/unscaled MAD → IQR/1.349 → audited population SD(ddof0), then constant-zero.
  No hard clipping; later constant-channel novelty is diagnostic. Real preparation is deferred.
- `standardized_window(steps,rows,scaler,calendar=...)` validates48consecutive scheduled
  positions, endpoint and46/48 complete vectors; fills an invalid vector entirely with
  zero after standardization and keeps its mask separate. There are five channels and
  research_ready remains False. Fit information cutoff is independently guarded.

Hand-check: hourly log(C/O)=.02, RMS12=RMS60=.02, previous-session daily returns=.01,
complete5/20-session momenta=.05/.20, floors=.005 give
U=(1,log(.02),0,sqrt(5),sqrt(20)). Current-day close mutations leave U4/U5 unchanged.
A late hourly publication is rejected, as are unknown clocks, stale>90min state,
missing momentum-chain closes, unverified split scope and source gaps.

A model-ready market/stock intersection mask, FT0, fitted empirical SPY floor/scaler
certificates, MC0/MC1/MC2 and model wiring remain later reviewed work. Volume/raw price
levels are absent from neural channels; SPY is absent from target normalization/trading.
