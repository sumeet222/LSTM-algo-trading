# View HF20: TM0 vs T2 in five minutes

From the repository root, with the documented `.venv` and legitimately provisioned local
HF20 artifacts, run:

```bash
./scripts/run_track_a_dashboard.sh --check
./scripts/run_track_a_dashboard.sh
```

Open the localhost address printed in the terminal. On **Start Here**, click
**Open HF20: TM0 vs T2**, or choose **HF20: TM0 vs T2** in the Explore sidebar.
The existing five-stock pages remain separate studies.

1. Expand **Study source, clock, recipes and scales**. Confirm20names, FT1v2, TG20,
   seed42, the pinned source revision and conditional badge. This is retrospective,
   as-reported source research with idealized publication timing and hourly-close proxies.
2. Choose each **HF20 recorded run** in turn. **Predictions & Errors** compares C0,
   already once-inverted T2, the original target and ZERO. Choose stock/date/origin.
   Full-population metrics always use all366origins ×20stocks across183sessions;
   the plotted subset and its row count are separate. Residual means score minus target.
3. Open **Training Diagnostics** for each recorded run. Calibration trains on the
   earlier prefix; original-TG20 inner-validation MSE alone selects the qualifying epoch.
   Refit starts with fresh weights and optimizer and trains the full legal prefix for
   exactly that epoch count. Development is later exploratory OOS, never used for selection.
   T2's optimizer objective uses squared asinh units and cannot be compared numerically
   with C0's original-target training objective. Canonical MSE graphs share TG20 units.
   Read clipping fractions, preclip percentiles, loss tails and actual phase timings.
4. Open **Price & Features / extremes**. Select stock and a genuine admitted origin
   (sorted by ex-post |TG20|), then click **Load genuine HF hourly candles + 48 feature steps**.
   Candles use original interval START timestamps; feature traces use completed-hour END
   timestamps and scheduled indices−47…0. Choose a channel for native and scaled traces.
   Dashed candle markers identify forecast cutoff and future price-proxy reference,
   never actual executable fills. The volume chart is as-reported share volume.
5. Inspect the matched tables and recorded warnings. ZERO rank IC is mathematically
   undefined; the optional project-zero convention is explicitly separate. One seed and
   a five-session block diagnostic do not establish significance, alpha or profitability.

Verified default example after release: **AAPL,2025-04-10,origin1 (10:32ET issuance)**.
The exact example is bound in `visualization_handoff.json`; select the matching origin
in the extreme-event dropdown to inspect its48steps. No source/model refit occurs in the UI.

If a handoff, checkpoint summary, feature store or source file is absent or changed,
the affected view explains the missing evidence. Provision the exact hash-bound artifacts
using the repository preparation guide and appropriate local-use permissions; do not
substitute another vendor, reprepare silently or train to fill a chart. Stop the server
with Ctrl+C. No paid or cloud service is required.

HF20 dates from2026-01-07 onward are rejected before numerical reads, including cache/viewer
routes. The original five-stock confirmation lock remains independent. No raw/derived data
sharing or screenshot redistribution rights are granted by this local viewer. Issuer/action
vintage, dividends, publication availability and PIT membership remain uncertified;
static source-sector selection and survivorship conditioning remain material limitations.
