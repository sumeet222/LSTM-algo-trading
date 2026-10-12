# Guarded stock/SPY handoff

Engineering complete; HUMAN_REVIEW_REQUIRED. Scientific G2/G3 and subsequent empirical activation HOLD. Mechanical training retention FAIL61.19% vs 90%.

| API | Contract |
|---|---|
|stock_source.load_stock_history(config)|Existing verified split/SIP/30Min core-five archive; returns StockHistory and QA; no download or second store |
|StockHistory.hour/day|Exact own-step gates; distinct publication/action known-at; genuine terminalclose/fullsessionvolume |
|FeatureCalculator.components/evaluate|Cached15 frozen channels + existing evaluate_m2; immutable48-position semantics |
|fit_floors/fit_m2_floor/fit_scaler|Explicit synthetic-only fit certificates, canonical keys, training chronology/source/action/dictionary bindings |
|ft0_tensor.stock_window|Exact ordered5×48×16 raw/scaled values, mask/reasons/lineage; None for invalid |
|ft0_tensor.forecast_bridge|No exits/labels/fills; only matching ASOF tensor may issue; historical-training batch blocked |
|ft0_tensor.join_market|Existing window_from_history; exact shared48 UTC ends; separate48×5 market mask; SPY is not a sixth stock |
|ft0_audit CLI|Offline source QA/mechanical retention/cutoff-negative traces; choose a new report directory |

Reproduce with documented editable .venv setup, canonical60 stock pairs and11 SPY pairs/manifests. No credentials required for offline audit:

```bash
python -m pytest -q
ruff check .
python scripts/check_python_types.py --pylance-dist '<installed-extension>/dist'
python -m lstm_data.ft0_audit --report reports/data_audit/<new-report-directory>
```

Synthetic fit mathematics and positive tensors reproduce in tests/test_stock_features.py and tests/test_ft0_transforms.py; no actual-data fitting route is enabled. A missing archive fails clearly. Reports are refused overwrite; all outputpaths project-relative.

Before P2.4/P3.1/MC0 use, humans must review the eight-item card; resolve inadequate training coverage through separately authorized immutable data remediation or an explicitly versioned sensitivity decision; supply historical native stock/SPY publication and action-vintage evidence; establish adjusted→raw proxy conversion known-at; provide legally available M2 and stock/market training certificate populations; and obtain required joint/course approval. Then a separately authorized task may implement actual empirical admission, not infer it from green synthetic tests. No initial M2 floor is silently fitted on future history. P3 execution/portfolio, P4 models, confirmation outcomes and40-pair consumption are outside this package.
