# Visually review the HF20 diagnosis

Read HF20_P016_MAIN_DIAGNOSIS.md in the Package 016 packet first. From repository root:

```bash
./scripts/run_track_a_dashboard.sh --check
./scripts/run_track_a_dashboard.sh
```

Choose **HF20: TM0 vs T2** in Explore, or **Start Here → Open HF20: TM0 vs T2**.
The exact existing controls are **HF20 recorded run**, **HF20 stock**, **HF20 development dates**,
and **HF20 origin**. Tabs: **Predictions & Errors**, **Training Diagnostics**,
**Price & Features / extremes**, **Five-minute guide**. Choose each C0/T2 run in turn.
No new Package 016 tab or MSE-algebra chart was added; linked compact CSVs support those comparisons.

1. **TSLA, 2025-09-15, origin 2**
   NEAR_ZERO_SCORE_LARGE_TARGET.
   Set stock, both development dates to 2025-09-15, and origin 2.
   Target=-11.61460018; C0=0.00298666; T2=0.00279261.
   Test tiny forecasts against a large target and residual.
   In **Price & Features / extremes**, search the genuine-origin dropdown for that date/origin,
   then click **Load genuine HF hourly candles + 48 feature steps**. Choose an FT1 channel,
   including M2, for native/scaled history. These examples are explicitly POST_HOC_DIAGNOSTIC.

2. **AAPL, 2025-08-14, origin 2**
   TYPICAL_QUIET_RAW_RETURN_ORIGIN.
   Set stock, both development dates to 2025-08-14, and origin 2.
   Target=0.64974046; C0=0.06938472; T2=0.06070360.
   Contrast quiet raw candles with normalized TG20.
   In **Price & Features / extremes**, search the genuine-origin dropdown for that date/origin,
   then click **Load genuine HF hourly candles + 48 feature steps**. Choose an FT1 channel,
   including M2, for native/scaled history. These examples are explicitly POST_HOC_DIAGNOSTIC.

3. **TSLA, 2025-06-05, origin 1**
   LARGEST_STOCK_SPECIFIC_TG20_TAIL.
   Set stock, both development dates to 2025-06-05, and origin 1.
   Target=-23.35028267; C0=0.13087973; T2=0.10941870.
   Inspect numerator/MAD/epsilon; preserve tails.
   In **Price & Features / extremes**, search the genuine-origin dropdown for that date/origin,
   then click **Load genuine HF hourly candles + 48 feature steps**. Choose an FT1 channel,
   including M2, for native/scaled history. These examples are explicitly POST_HOC_DIAGNOSTIC.

4. **AMD, 2025-11-26, origin 1**
   LARGEST_C0_T2_DISAGREEMENT.
   Set stock, both development dates to 2025-11-26, and origin 1.
   Target=3.42399240; C0=-0.02036897; T2=0.05909761.
   Compare scores/errors on the same row.
   In **Price & Features / extremes**, search the genuine-origin dropdown for that date/origin,
   then click **Load genuine HF hourly candles + 48 feature steps**. Choose an FT1 channel,
   including M2, for native/scaled history. These examples are explicitly POST_HOC_DIAGNOSTIC.

5. **Epoch1 learning case, both recorded runs.** Open **Training Diagnostics**;
   inspect the selected-epoch vertical marker and epoch table. Compare optimizer loss in its
   own units, original-TG20 inner-validation MSE, online original-scale training MSE, gradient
   percentiles and actual clip fraction. T2 epoch 2 is raw minimum but fails strict 0.1% qualifying
   improvement. No later-epoch weight/activation chart exists; those checkpoints were not saved.

Units and interpretation: C0 optimizer loss is TG20 squared; T2 optimizer loss is squared asinh
units and is NOT DIRECTLY COMPARABLE. Inner validation selects epochs; development is later
exploratory OOS. T2 saved scores are already inverted once: never invert again. Full-population
equal-day metrics retain 366 origins×20 names; date/stock/origin plots are filtered subsets.
Reported neural fitting time, worker wall and supervisor wall differ, and host load differed
between runs; elapsed seconds do not prove a transform speed advantage. Hourly candles use
interval START; FT1 uses completed END/scheduled steps−47…0; no reconstructed30-minute bars
or actual fills. TG20/raw future outcomes are EX-POST labels, absent from feature channels.

Existing charts do not show the new exact MSE algebra, denominator-tail attribution or grouped
paired-contribution charts. Their bound CSVs and suggested axes are in visualization_handoff.json;
no synthetic/placeholder chart is claimed. If original source/derived artifacts are unavailable,
use the saved score/diagnostic tabs and report SOURCE/CHRONOLOGY HOLD for the missing chart.

No dates 2026-01-07+ are allowed, including Full data/cache routes; the five-stock lock remains
independent. Source/publication/action/PIT/licensing qualifications in the main diagnosis
remain unchanged. Close only the server you launched with Ctrl+C. No screenshot was synthesized.
