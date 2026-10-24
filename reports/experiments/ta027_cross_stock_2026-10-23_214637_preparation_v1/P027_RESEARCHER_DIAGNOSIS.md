# P027 researcher diagnosis

**None of the three cross-stock arms improves both development MSE and ranking IC over the saved T2/42 reference.** A4 is mixed; A5 and A6 have worse point estimates on both primary metrics. This is a negative/inconclusive exploratory architecture screen, with correct execution. No model is promoted.


A4 sees own FT16 plus two leave-one-out peer M1 summaries at every historical step; A5/A6 encode all16 channels of all20 histories before final-state exchange. A4 is not a full-information-matched control. No fourth full-peer LSTM is authorized; A5/A6 gains cannot identify the exchange mechanism independently of information/capacity.

| arm | mse | daily_ic | origin_ic_mean | prediction_sd |
|---|---|---|---|---|
| A4 | 3.10646 | 0.0638402 | 0.0478981 | 0.0522742 |
| T2/42 | 3.10656 | 0.0755594 | 0.0615755 | 0.0488872 |
| T2/123 | 3.11491 | 0.025493 | 0.0215651 | 0.0349004 |
| ZERO | 3.11656 | undefined | undefined | 0 |
| A5 | 3.10992 | 0.0495687 | 0.042894 | 0.0380494 |
| A6 | 3.11263 | 0.0482016 | 0.0452886 | 0.0250582 |


These are original-TG20 MSE and within20 Spearman IC, with daily versus origin averages explicitly separated. ZERO IC is undefined. Development is109 reused sessions/183 origins/3,660 rows, Jul–Dec2025. Refit is in-sample. No2026 confirmation values, trading returns or extra fits were used.

A4 adds historical19-peer M1 mean/dispersion. MSE improves by only0.0000951 (about0.0031%) while daily IC falls0.01172 and origin IC falls0.01368. The one-/two-month MSE intervals straddle zero. Peer-channel derivatives are nonzero, and ten-session peer replacement moves forecasts by RMS0.01205 in original target units. Replacement slightly improves development MSE but reduces IC: sensitivity is real, yet there is no consistent timing-destruction benefit. This does not prove that all peer information is useless.

A5 rank4 mixing is computationally active: both matrices receive finite gradients, the fixed8-origin hidden-Jacobian off-diagonal norm fraction is0.372, and its readout shift RMS is0.03052 in transformed-z units. Those are descriptive associations, not causal influence or predictive gains. MSE worsens0.003355 and daily IC falls0.02599. M1/M2 have numerical rank4; entropy effective ranks are about2.42/2.41, while the M2M1 linear proxy has effective rank1.42. That proxy is not the rank of the nonlinear model. Peer replacement worsens both development MSE and daily IC but the unshifted candidate still trails T2/42. Stock-position effects, capacity and fuller information remain confounded.

A6 attention is close to uniform: effective attended count19.963 of20, normalized entropy0.99937, average self mass0.04938 and other19 mass0.95062 over the full refit population. Its off-diagonal hidden-Jacobian norm fraction is0.0462 on the fixed8-origin probe; peer replacement moves development forecasts RMS0.00328. MSE worsens0.006071 and daily IC falls0.02736. The attention mechanism functions, but the fitted weights offer little evidence of strong dynamic peer selection. Its month and two-month daily-IC difference intervals remain below zero; these reused-data sensitivity bands are not confirmatory significance. Input replacement slightly improves IC while marginally worsening MSE, again a mixed falsification diagnostic.

All three remain better than ZERO in MSE, which alone does not establish incremental peer value over T2. Score SDs0.0523/0.0380/0.0251 are far below target SD1.7654. Frozen95/99-percentile absolute-event recall is0 in development for all three; no threshold or amplitude repair is applied. No inference about E1/QR1's separate event/quantile tasks follows.

D6g semantics matter: A4 calibrated17 epochs/selected7/raw-min7/refit7; A5 calibrated13/selected3/raw-min7/refit3; A6 calibrated12/selected1/raw-min3/refit1. Later raw minima did not qualify under original strict0.1% improvement. Exactly8,693 optimizer updates are recorded, split across the three authorized pairs; no raw-min refits, retries, transferred parent weights, altered stopping rule or extra experiments.

Transformed-objective tails remain distinct from original-MSE tails. Every refit arm has104,200 rows: top1%1,042 and top5%5,210; each95%/99%-of-fitting-maximum magnitude range has only one row. The5% disjoint numerator/MAD partition is NUM_ONLY5,123 / MAD_ONLY5,113 / BOTH87 / NEITHER93,877 and conserves rows and actual z-MSE. About24.4–24.5% of refit z-loss lies in the ranked top5%, not in a one-row magnitude range. All66 exact source cases include48 input+4 outcome hours, observed-volume/quality, native/scaled16-channel histories and genuine20-return target operands; peer operands/hidden/attention are linked privately.

A4 lacks the fuller peer-history access of A5/A6; neither their losses nor their hidden weights isolate architecture from information. A5 vs A6 is a cleaner raw-information comparison with different capacity and identity assumptions; A6 has slightly higher origin IC than A5 but worse MSE and daily IC. No attention plot, nonzero gradient or Jacobian proves economic peer transmission. TG20 already removes the future common median as a label, so forecasting common state may not improve signed relative ranking.

The restrained next action is to retain T2/42 as the reference and avoid promoting a P027 arm. A future full-peer ordinary-LSTM control, seed123 replication or separate Experiment3 market-state design is a human decision/new proposal, not continuation authority. This screen does not establish an independent null, settle the broader research question or authorize T2/E1/QR1 fusion. All P2 scientific holds, bounded researcher-attested rights/clock assumptions, protected outcomes and the10+3 roadmap remain preserved.

Read scientific_closeout_v2/P027_CROSS_STOCK_COLLECTIVE_COMPARISON_v2.md for signed intervals/secondary metrics, P027_PEER_INFORMATION_AND_MECHANISM_FALSIFICATION_v2.md for four-role matched controls, P027_FIT_AND_GRADIENT_VERIFICATION.md for every phase's gradient/clip summaries, and collective_v1/P027_OBJECTIVE_SPACE_EXTREME_LOSS.md for objective accounting. The per-arm result reports and source cases are available through the P027 explorer. No private data redistribution is authorized.
