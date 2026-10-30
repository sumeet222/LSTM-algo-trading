# S3-C latest-hour encoder contract — UNAPPROVED PROPOSAL

Audit date2026-10-28. **SOURCE_PERMISSION_BLOCKED** for full minute paths; no encoder, tensors, feature values, normalizers or models created. This is a candidate contract for human review, not a frozen experiment or authorization.

## Keep the hourly history and select the newest block exactly

Retain the entire original **48×16 FT16** own-stock history and the completed S2-B **10-dimensional schedule-only clock readout**. Add minute detail for the block at saved `entry_index`, never a generic wall-clock “last hour.” At09:30 this is the previous scheduled session's last full hour; on a normal day at10:30–15:30 it is the full hour ending at that origin. On an early-close date only actual full-hour blocks enter. A15:30 origin may use14:30–15:30, before ~15:32 issuance. A prior day's15:30–16:00 stub remains excluded even at next opening. Sample geometry CSV gives exact dates/UTC boundaries and age.

Every block selected by these executed masks has60 scheduled trading minutes. The maximum here is one60-position sequence per stock/origin, **not48hours of minute sequences**, and not a replacement for the long FT16 sequence. Missing minute positions occupy their known scheduled position with masks; no closed-market time is padded into the sequence. If a future protocol admitted shorter completed blocks it would need a new rule; do not treat the present closing stub as such a block. For this proposal early closes do not shorten an admitted full hour.

## Proposed fixed minute channels: 60×7

For scheduled starts `k=0,…,59` within `[block_start,block_end)`:

1. `RET`: `log(C_k/C_(k−1))/h_(i,f)` only when k>0 and both consecutive minute closes are genuine/positive/compatible. First position and broken adjacency are masked, never a multi-minute bridged return.
2. `RANGE`: `log(H_k/L_k)/h_(i,f)` on genuine, internally consistent positive minute OHLC.
3. `ACTIVITY`: `log1p(v_k/u_(i,slot,phase))` for genuinely observed finite nonnegative volume. `u` is a positive legal training-prefix median of observed minute volume in the stock's compatible share regime and scheduled hourly slot, fitted once per phase; no current/future daily total. An unrepresented regime requires BLOCK or an explicit prior-approved fallback, not OOS fitting.
4. `PRICE_OBS`: genuine timely valid OHLC indicator.
5. `RET_OBS`: consecutive-close validity indicator, false at k=0; independent of return size.
6. `VOLUME_OBS`: genuine timely volume indicator. Genuine zero volume is zero ACTIVITY with mask1; missing is placeholder0 with mask0.
7. `POSITION`: `k/59`, fixed scheduled position, no fitted scale or future event time.

`h_(i,f)` is the original legal initial/refit phase's FT16 hourly floor, not the magnitude-target scale. This preserves absolute local volatility relative to a historical unit. Keep original FT16 V1/V2 absolute state. No per-sequence standard deviation, future ranks, target magnitude, future close/open, retrospective component-support flag or future source QA label enters the encoder.

With a masked field, use computational placeholder0 **and its explicit mask**. Return validity must ignore placeholder values. An entirely missing block has all observation masks0 and produces a fixed zero minute embedding by an explicit all-missing gate; no learned interpretation of a fabricated flat path. Partial blocks retain only observed fields at their scheduled positions. No forward/backward minute-price interpolation, hourly-derived synthetic path, raw-source recovery or target-admission change.

The as-of meaning of `OBS` needs approval: historical canonical QA can identify bad records retrospectively. It is not evidence of historical publication by block_end+2minutes. The future experiment must disclose this proxy or require independently certified arrival metadata, and must not smuggle later anomaly knowledge into inputs. Corporate-action compatibility and quarantine provenance remain gates, not unconstrained learned source-era inputs.

## Proposed compact fusion and capacity

One shared one-layer minute LSTM H8 with fresh zero states encodes60×7; retain its last hidden vector, gate to zero for an all-missing block, and concatenate it with the original dropped H32 hourly final hidden state and unchanged10 clocks. One scalar M head operates on32+10+8=50 inputs. No new event head, label supervision or regime router. Proposal only: dropout semantics for the minute branch must be frozen explicitly before fitting; suggested no extra dropout and retain original hourly final-hidden0.10.

Analytic count: minute LSTM `4·8·(7+8+2)=544` parameters, scalar head adds8 relative to CLOCK: **6,995 total** versus6,443. This is a capacity increase as well as different representation. Additional minute recurrence is about28,800 multiply-adds per stock/origin, versus294,912 in the original hourly trunk (~9.8% arithmetic, excluding memory, masks and CPU kernels). No measured speed or2GB peak-RAM guarantee follows from that ratio.

## Coverage, eligibility and fair comparators

Propose retaining every exact original main-task key with the fixed masked input policy, rather than requiring all20 stocks to have60 observed minutes in the newest hour. A strict-complete20 newest-hour sample loses a nonzero fraction of audited windows; see readiness matrix. These are sampled saved-hourly-count intersections, not verified population attrition. Value validation, timestamp uniqueness, adjacency, volume completeness and timely masks remain blocked; there is no certified full-key minute tensor yet.

Before a later fit, prove original all20 key identity, full48 FT16 history, schedule-as-of fields, one selected block/stock/origin, causal phase normalizers, mask-placeholder invariance, all-missing branch behavior, finite gradients and no extra input step. If a source/value problem cannot be represented under the prospectively approved policy, block rather than drop a difficult key.

Primary future comparator: frozen CLOCK-C3 on exact same4h keys, C0/C3 as scientific controls, and S3-B as a different information reach (summaries of all48 hours vs details of the newest hour). Do not call S3-B information-identical. A fixed deterministic **latest-hour summary** using the same minute fields/window/masks is the strongest cheap control for learned ordering versus extra information. Its compression differs, so even this matches fields/reach rather than every retained distinction. It would require a separately approved fitted control (normally four additional starts if neural), or a separately authorized non-neural control; the prospective eight-start B+C plan does not silently cover a third trained family. Without it, restrict attribution to the whole representation/capacity package. A capacity-matched hourly head control likewise requires its own approval, not an automatic ablation.

One seed/four annual folds, original transformed-M main objective and selector, fresh September model, its own independent Oct–Dec C3 calibration κ25. Raw and calibrated outputs can later be reported with the calibrated arm predefined primary. No coefficients transfer from CLOCK-C3. No fitting occurs now.

## Later full-window boundary

S3-D would encode each of the48 genuine full blocks (maximum2,880 expected minute positions/stock/origin) with shared minute weights and feed minute embeddings alongside FT16 to the hourly H32. It has much larger computation/activation demand and is reserved for a later conditional session. This latest-hour S3-C proposal neither implements nor authorizes S3-D. S3-E market context and Stage5 ranking objectives remain separate, unapproved work.

Source-adapter prerequisite: qa_v2/canonical_observed is the pre-P019B action/quarantine canonical stream. Apply only the existing approved source/action rules compatible with adjusted hourly inputs after a read grant; do not assume an already adjusted full-minute tensor exists. Within-block log ratios are invariant to one constant positive split factor, but that does not waive quarantine, action-boundary, genuine-interval, volume-regime or publication checks. No such adapter is implemented here.
