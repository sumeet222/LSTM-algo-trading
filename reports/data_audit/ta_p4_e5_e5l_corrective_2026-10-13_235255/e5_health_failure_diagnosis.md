# E5 unchanged health proof — BLOCKED

The failed proof is preserved in the prior package. No tensor, loss, gradient,
channel-order, ablation or indexing defect was demonstrated. The fixed60-update
acceptance is still failed; there was no new optimization or health rerun.

| Quantity | Original measured value | Required unchanged bound |
|---|---:|---:|
| Initial evaluation MSE | 0.2256385386 | Reference |
| Final evaluation MSE | 0.1439103037 | `< 0.0789734885` |
| Zero-peer evaluation MSE, same final weights | 0.2152040154 | `> 0.2878206074` |

Loss improved, but both required inequalities failed. Positive peer gradients
alone do not establish the required peer dependence. Two historical identical
runs exist; the second recorded previously missing metrics. Neither is erased.

`health_diagnosis_final.json` reconstructs the same RNG8049,16×2×5×48×23 fixture with
independent four-peer sum/centered population-SD arithmetic. The first21 channels
are bitwise unchanged by zeroing the already-scaled peer21:23 channels. It
reproduces initial MSE0.2256385386 at seed42 without a single optimizer update.
One initial evaluation forward/backward has finite positive encoder/readout
and both peer-input gradients; the global preclip norm and initial would-clip
indicator are recorded. Actual historical clipping fraction and trajectory
were not retained and remain NOT_RECORDED. AdamW lr.001/decay.01, dropout.10,
clip1 and frozen session loss are unchanged. No own-only trained neural
comparator exists, and the initial zero-peer evaluation is not the old final
ablation.

The target equals the same input endpoint's peer mean exactly. Independent OLS
projections on the seven own M1 lags have rank8 and MSE0.2119861980; adding that
peer mean gives rank9 and MSE≈2.97e-31. This establishes mathematical
identifiability of the toy relation, not trained E5 acceptance or a TG0 result.
The fixture contains no `ProxyLabelSample`, genuine future-reference maturity,
TG0 centering/MAD/floor, or source clocks. Its toy target cannot certify the
requested chronological learning foundation. The60-update outcome establishes
failure under this proof, not that the architecture cannot learn in general.

**P4.8_PARTIAL / E5_HEALTH_BLOCKED.** Actual E5 D6g calibration/refit, selected
epoch checkpoint, final refit checkpoint, reload and final P3 forecast remain
NOT_RUN. Do not run them on the strength of gradients or the independent OLS.

For separate human review, proposed `E5_HEALTH_CHRONOLOGICAL_TG0-v2` would fix
RNG8051 and seed42, the first80 XNYS sessions with both valid forecast origins
on/after2022-10-03, split chronologically64-training/16-held-out,
48 completed steps, independent bounded raw M1 generated before labels,
zero stock/market controls elsewhere, and complete matured four-hour proxy
references through existing TG0. Preserve the complete causal prehistory and fit
any required floor/scaler on only those64 training sessions using existing math.
Predeclare raw future log return
`1e-4 * peer_mean_M1(i,t) * peer_SD_M1(i,t)`; this changes the old fixture and
must not be approved by implication. Use original model/optimizer/loss and
compare identical final weights with peers zeroed. A bounded256-update health
length and the original.35/2 inequalities are proposed, not measured or approved.
Before execution, independently check that the normalized TG0 relation retains
peer information beyond own/market controls, freeze all source/timing/fixture
hashes, and obtain explicit approval of the changed fixture and update cap.
No promised pass, seed search, tuned threshold, D6g fit or real pair is implied.
