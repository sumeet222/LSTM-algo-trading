# Real feature oracles — conditional candidate study

These are genuine archived inputs and independently recomputed numbers under approved assumptions. Observed publication remains UNKNOWN; action vintage is unverified. No numeric result certifies historical availability, executable fills or source rights. No confirmation values were read.

The active build is `build_v4`; `independent_real_oracles.json` preserves all four deterministic cases and native constituent references. All 16 channels are recalculated independently from historical aggregate closes/daily records. The first-hour aggregate is also independently reconstructed from its exact two immutable native half-hours.

Example: AAPL 2020-07-01, slot 1 / origin 1. Inner/outer preprocessing is separately fitted; the trace below uses WF1 full-refit preprocessing and is retrospective research preparation, not a forecast issued in 2020.

| Native start UTC | Open | High | Low | Close | Volume |
|---|---:|---:|---:|---:|---:|
| 2020-07-01 13:30:00+00:00 | 91.26 | 91.84 | 91.15 | 91.49 | 17918484 |
| 2020-07-01 14:00:00+00:00 | 91.5 | 91.69 | 91.38 | 91.58 | 7404248 |

Independent hourly OHLCV: `[91.26, 91.84, 91.15, 91.58, 25322732.0]`; exact match to production aggregation.

| FT0 | Independent | Calculator | Absolute difference | Scaled |
|---|---:|---:|---:|---:|
| M1 | 0.666266116988555 | 0.666266116988555 | 0 | 1.21855065390335 |
| M2 | 0.106711551878466 | 0.106711551878466 | 1.39e-17 | 0.498317956178569 |
| M3 | -0.0962159030217156 | -0.0962159030217156 | 0 | -0.311683303452227 |
| M4 | 0.42559393890461 | 0.42559393890461 | 0 | 0.0190585156972392 |
| V1 | -5.37403626990413 | -5.37403626990413 | 0 | 0.0543196597842702 |
| V2 | -5.24883142187313 | -5.24883142187313 | 0 | 0.243974073093896 |
| V3 | -0.125204848030998 | -0.125204848030998 | 0 | -0.266542330377142 |
| B1 | 0.00754143144658414 | 0.00754143144658414 | 0 | 0.586098152053483 |
| B2 | 0.246376811594186 | 0.246376811594186 | 0 | 0.246376811594186 |
| Q1 | -0.338448819909667 | -0.338448819909667 | 0 | -0.869353001592175 |
| Q2 | 0.0649554205871777 | 0.0649554205871777 | 0 | 0.834032024237738 |
| T1 | 0.0510634383913193 | 0.0510634383913196 | 2.15e-16 | 1.68935532596419 |
| T2 | 0.4 | 0.4 | 0 | 0.4 |
| T3 | 0.00479784812448577 | 0.00479784812448577 | 0 | 0.883861023465704 |
| T4 | 0.0160039354542989 | 0.0160039354542989 | 0 | 1.36061816447938 |
| T5 | 0.236732091536657 | 0.236732091536657 | 0 | 0.236732091536657 |

RMS12=0.00463538384052168; RMS60=0.00525365411873861; daily RMS63=0.0223829862773739. These are RMS, not centered standard deviations.

M2 independently uses 20/60 prior same-origin price-only returns, ending before the current session: 2020-04-06…2020-06-30. Mean20=0.00110419106575943, RMS60=0.0103474370517729. All outcome events precede the historical step; no TG0 is used as M2.

Stock floors/pseudocounts: `{'daily_floor': 0.012007969923727213, 'daily_pseudocount': 729213.4500000001, 'hourly_floor': 0.0028288513643958254, 'hourly_pseudocount': 94113.815, 'm2_floor': 0.005840272578675711, 'symbol': 'AAPL'}`. The five stock-specific parameters and pooled 13-channel scaler are stored in each prefix recipe; B2/T2/T5 remain native bounded values.

M3/M4/T1/T2/Q2 use completed prior sessions, including the actual terminal stub in daily volume. Q1 uses the preceding 20 matching hourly slots. Independent EMA6/18/24/72 and Wilder RSI14 iterate actual scheduled hourly closes, including overnight differences; no synthetic overnight row is inserted.

| Case | Maximum absolute FT0 difference | Native aggregation |
|---|---:|---|
| AAPL 2020-07-01 | 2.151e-16 | exact two-half-hour match |
| AAPL 2020-08-28 | 2.082e-16 | exact two-half-hour match |
| AAPL 2020-08-31 | 2.776e-17 | exact two-half-hour match |
| AAPL 2021-03-15 | 2.255e-16 | exact two-half-hour match |

Cases include first training origin, pre-split Friday, post-split Monday, and post-DST overnight Monday. The AAPL split is represented in vendor split-consistent units, with unverified action vintage retained. One matching raw control does not certify all raw-price conversion.

# Five-stock TG0 oracle

Cross-sectional median=0.000877798037428799; unscaled MAD=0.004845923767524; TRAIN-only epsilon=0.000250978003799024. No target clipping.

| Stock | Entry proxy close | Exit proxy close | Log return | TG0 |
|---|---:|---:|---:|---:|
| AAPL | 91.58 | 91.41 | -0.00185802556322208 | -0.536762080847544 |
| COST | 302.87 | 304.9878 | 0.00696810526755271 | 1.19490378731451 |
| CMCSA | 39.855 | 39.89 | 0.000877798037428799 | 0 |
| SBUX | 74.49 | 74.195 | -0.00396812573009521 | -0.950758712829995 |
| CME | 167 | 169.22 | 0.0132058310795997 | 2.41873074963554 |

Maturity under the approved ideal source clock is 2020-07-01 18:33:00+00:00, never the 14:30 proxy boundary. The 14:33 simulated event is not a real observed fill.

Negative and boundary oracles: test_pretraining_candidate.py removes a future exit while preserving entry references; forecast input admission never reads that exit. Missing/unknown publication is rejected by strict source_reason even when conditional access is approved. An arbitrary DOCUMENTED or asserted available_at is rejected by ConditionalHistory. Tests also cover exact DST slots, early-close rejection, zero MAD, invalid floor, unit tampering, no confirmation numeric materialization and forbidden activity names. Existing stock-feature tests independently cover zero-range/zero-gain/loss, missing recovery, 360 EMA updates, 14+140 RSI updates, daily locking, denominator floors and full-window guards.

No genuine zero-range case occurs in this measured source cohort (`quality_flags={}`); the zero-range demonstration is synthetic and is not mislabeled as a real observation. The training target maximum absolute TG0 is 82.0280; retain it without clipping and inspect target-loss concentration in a future authorized training-health report.

Action boundaries: COST special cash distributions and CME annual variable distributions are documented in public_documentary_action_refs.json. They remain price-only gaps in daily/overnight features, not credited dividend cash. No complete new-name action history, historical vendor publication, raw cashbook or total-return claim is made. Alpaca asof=2025-06-30 maps symbol/entity names; it does not certify a corporate-action vintage.

# Independently recomputed genuine SPY U1–U5

SPY 2020-07-01 slot1: raw hourly open=309.56, close=310.91. The independent calculation uses actual raw hourly OC returns and prior completed session closes, separate TRAIN-only floors/scaler, and the same explicitly approved ideal clock.

| Channel | Independent raw | Calculator raw | Scaled |
|---|---:|---:|---:|
| U1 | 1.16540932902773 | 1.16540932902773 | 1.95801226966622 |
| U2 | -5.59029628505971 | -5.59029628505971 | 0.597178527566687 |
| U3 | -0.249120996197927 | -0.249120996197927 | -0.923497262447881 |
| U4 | -0.251958302373166 | -0.251958302373166 | -0.830609781927792 |
| U5 | 0.0161216189595682 | 0.0161216189595682 | -0.631654000763133 |

Maximum absolute raw U1–U5 difference=0. All1,998 full market windows and21-channel stock/market joins were actually materialized transiently; masks, finite float32 conversion and exact shape pass. No dense joined tensor was saved. The separate JSON audit preserves counts and numerical trace SHA.

Trend interpretation needs explicit care: this real example has positive raw U5 but negative standardized U5. Existing regime_diagnostics.classify signs standardized U5. Both signs are preserved in the conditional diagnostic records; BULL/BEAR library labels here do not certify positive/negative absolute trailing returns. No directional regime claim is made, and wording should be reviewed before such claims. Continuous U1–U5 inputs and the volatility-retention result are unaffected.
