# HF20 FT16 Complete Feature Specification

Extracted 2026-10-27 from existing implementation, fitted recipes and completed-run records at Git commit `5f7bb86a35d5aaff34ff79ef8f471117de6d3e42` (branch `feat/track-a-data-intake`). This describes the **minute-derived HF20/P019B/P020 experiments**, especially completed **S4-A and S9-MAG**, rather than the proposed hourly USA500 research protocol. FT16 contains own-stock information; it has no USA500 channel, stock ID, sector, raw price-level channel or future label channel.

Only this document was created. No training, downloads, dataset reconstruction, new scientific audits, tests or static checks were run. Existing completion/verification receipts below are historical evidence, not checks rerun for this extraction. The explicit single-file scope supersedes the repository's additional session-report-file convention.

## 1. Authority and exact artifact locations

The following directory aliases are used only to shorten references in this document; all paths are repository-relative.

| Alias | Exact directory |
| --- | --- |
| `P019B` | `reports/data_audit/ta019b_action_qa_2026-10-22_201224` |
| `P020` | `reports/data_audit/ta020_hf1m_long_ft16_tg20_2026-10-22_211122` |
| `S12` | `reports/experiments/hf20_s1_s2_continuation_2026-10-25_204117` |
| `S3` | `reports/experiments/hf20_s3_live_2026-10-26_010204` |
| `S4` | `reports/experiments/hf20_s1s2_visual_s4a_2026-10-26_110310_preparation` |
| `S59` | `reports/experiments/hf20_s5_s9_2026-10-26_164825_preparation` |

**Executed evidence takes precedence over proposal labels.** Despite its directory name and the frozen card's `PROPOSED_...` kind, `S4/S4_LIVE_FINAL_VERIFICATION.json` records eight completed neural runs, eight prefix recipes, zero failures and unchanged approved execution. Individual `S4/HF20-S4A-F{21..24}-H4-{NR,T2R}-S42/PASS.json` and saved calibration/refit configurations establish execution. `S59/HF20-S9-F{21..24}-H4-MAG-S42/configuration.json` records `input_dim:16`, seed 42 and execution SHA256 `e19fc1da419d6456d16a7dec7777bc7e1400b2d0412be65ba116906d01cfd73e`; each has a completed `PASS.json`.

`S59/S4_REUSED_RECIPES.json` binds the **eight actual S4 input recipes**, `S4/F{21..24}_{inner,refit}_recipe.json`, by saved SHA256. S9's per-run `inner_target_recipe.json` and `refit_target_recipe.json` are **task/label recipes**, not replacement FT16 scalers. The executed path `hf20_s5s9.Data.phase()` loads the S4 input recipe directly.

Core identity is frozen in [configs/hf1m_long_ft16_v1.json](configs/hf1m_long_ft16_v1.json): feature ID `HF20_HF1M_LONG_v1_FT16_v1`; source `mito0o852/OHLCV-1m`, revision `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`; action namespace `HF20_HF1M_LONG_v1_ACTION_QA_v1`. `P020/model_input_contract.json` binds source-derived stores, grid, origins, targets and `train_only_fit_recipes.json`; later annual runs reuse the formula family with earlier, fold-specific recipes.

Fixed stock-axis order: `VZ, COP, BAC, BA, AAPL, PEP, MRK, SBUX, CVX, MS, AMD, KO, JNJ, AMZN, XOM, WFC, AVGO, TSLA, MA, CSCO`.

## 2. Notation, source fields and clocks

For stock \(i\), \(t\) indexes **scheduled, non-stub, completed RTH full-hour positions**, ordered by UTC time. An ordinary session contributes six bars, 09:30–10:30 through 14:30–15:30 Eastern. The final 15:30–16:00 stub is excluded from FT16. Early-close sessions contribute their available full hours; no overnight/weekend bars are inserted. UTC timestamps and `America/New_York` session dates preserve DST/calendar ordering.

- \(O_t,H_t,L_t\): adjusted hourly `open`, `high`, `low`. Open requires the genuine first minute at the scheduled start. High/low are extrema of genuine, unquarantined observed minutes; any quarantine in the hour masks both extrema. A partial observed range is not certified complete-hour high/low.
- \(C_t\): **`close_input_cap5`**, genuine terminal-minute close when available, otherwise the permitted causal terminal close proxy. It is used by OC, B2, T1 and indicators. Distinguish \(G_t=\texttt{close}\), which requires the genuine minute at `hour_end_utc - 1 minute` and is used for daily closes and historical-return endpoints.
- \(U_t\): `volume_for_feature`, derived from `observed_volume`; never price-proxy volume. Units are as-reported source shares. Quality rules are in §4.
- \(D_k\): genuine \(G\) at 15:30 on the \(k\)-th ordinary six-full-hour session. This uses the 15:29 minute's close; it is a **15:30 surrogate**, not the exchange's 16:00 daily close. Earlier missing hours do not invalidate an independently genuine terminal close. Early-close sessions are excluded from this daily series.
- \(W_k\): sum of the six \(U\) values on regular session \(k\), only if all six are finite and share one volume regime. This is six-hour observed/lower-bound volume, not full-session exchange volume.
- \(k(t)\): last regular-session index **strictly before the session containing \(t\)**. All daily components below use this index, including on early-close input days. Set \(d_k=\log(D_k/D_{k-1})\), masking price-basis transitions.
- \(\operatorname{Mean}_{n,m}(x)\), \(\operatorname{RMS}_{n,m}(x)\): last **n scheduled positions**, at least **m finite values**, no run of three missing positions within the window, and no result before n positions exist. Means divide by the number of observed values; RMS is \(\sqrt{\operatorname{mean}(x^2)}\), not demeaned standard deviation. Missing positions remain indexed.

Define \(a_t=\log(C_t/O_t)\), \(s_{12,t}=\operatorname{RMS}_{12,12}(a)_t\), \(s_{60,t}=\operatorname{RMS}_{60,57}(a)_t\), and \(s_{63,k}=\operatorname{RMS}_{63,60}(d)_k\). These hourly RMS values include the current completed hour. Let \(h_i,\delta_i,b_i\) be the fitted hourly, daily and M2 floors; \(q^h_{i,r},q^d_{i,r}\) are fitted volume pseudocounts for the current share regime \(r\), as defined in §4.

Source: `src/lstm_data/hf_minute_long_qa.py:60–88` (`calendar_frame`), `hf1m_action_source.py:67–95,141–248` (`price_factors`, `adjust_prices`, `derive_month`), `hf1m_ft16_math.py:15–33,84–191` (`rolling`, `regime_rolling`, `build`).

## 3. All 16 native features, in tensor order

Names in code are the IDs below; parenthetical descriptions explain their economic meaning. Formulas are **before affine scaling/fallback**. All 16 outputs are dimensionless. Log returns use natural logs and decimal returns, not percentages or basis points; no volatility annualization is applied.

| # / exact name | Exact native formula | Source fields and lookback | Native units / special rule |
| --- | --- | --- | --- |
| 1 **M1** (hourly momentum) | \(a_t/\max(s_{60,t},h_i)\) | Current `open`, `close_input_cap5`; 60 scheduled hourly OC returns, ≥57 valid | Volatility-normalized return; current OC is included in RMS60 |
| 2 **M2** (same-origin historical momentum) | \(\mu^{(o)}_{20,i,t}/\max(s^{(o)}_{60,i,t},b_i)\) | Genuine historical same-origin endpoint log returns: mean over 20 prior regular-origin days, ≥19 valid; RMS over 60, ≥57 valid | Normalized historical return, session-start locked; exact context/horizon rules below |
| 3 **M3** (five-session momentum) | \(\log(D_k/D_{k-5})/[\sqrt5\max(s_{63,k},\delta_i)]\) | Prior genuine regular-session closes; 5 return intervals plus 63 daily-return RMS positions, ≥60 valid | Volatility-normalized return |
| 4 **M4** (skip-month momentum) | \(\log(D_{k-20}/D_{k-125})/[\sqrt{105}\max(s_{63,k},\delta_i)]\) | Prior genuine daily closes, 105 return intervals ending 20 regular sessions before k; needs close lag 125; daily RMS63 as above | Volatility-normalized return; not a 125-session cumulative return |
| 5 **V1** (short volatility) | \(\log\max(s_{12,t},h_i)\) | `open`, `close_input_cap5`; 12/12 hourly OC returns | Log of decimal-return RMS |
| 6 **V2** (long volatility) | \(\log\max(s_{60,t},h_i)\) | Same fields; 57/60 hourly OC returns | Log of decimal-return RMS |
| 7 **V3** (volatility ratio) | \(V1_t-V2_t\) | Same fields; 12/60 hourly windows | Log short/long floored RMS ratio |
| 8 **B1** (range) | \(\log(H_t/L_t)\) | Current observed adjusted `high`, `low` | Log price ratio; may describe a partial observed range |
| 9 **B2** (close location) | \((2C_t-H_t-L_t)/(H_t-L_t)\) | Current `close_input_cap5`, `high`, `low` | Zero if width is zero; nonfinite width or absolute result >\(1+10^{-10}\) → missing, **not clipped** |
| 10 **Q1** (same-slot relative volume) | \(\log[(U_t+q^h_{i,r})/(\bar U^{slot}_{20,t}+q^h_{i,r})]\) | Current usable hourly volume; mean of previous 20 occurrences of the same scheduled slot, ≥19 valid, current value excluded | Log share-volume ratio; previous slot occurrences can include early-close sessions; all dependencies must match current share regime |
| 11 **Q2** (daily volume trend) | \(\log[(\operatorname{Mean}_{5,5}(W)_k+q^d_{i,r})/(\operatorname{Mean}_{60,57}(W)_k+q^d_{i,r})]\) | Six-hour daily volumes from prior regular sessions; 5/5 and 57/60 | Log share-volume ratio; regime-consistent windows |
| 12 **T1** (moving-average distance) | \(\log[C_t/\operatorname{Mean}_{20,19}(D)_k]\) | Current `close_input_cap5`, 20 prior regular-session closes | Log price ratio; daily mean stays within one price basis |
| 13 **T2** (daily sign trend) | \(\operatorname{Mean}_{20,19}(\operatorname{sign}(d))_k\) | Genuine prior daily closes; 20 daily-return positions, ≥19 valid | Bounded [−1,1]; exact zero return has sign 0 |
| 14 **T3** (short EMA spread) | \((E_{6,t}-E_{18,t})/C_t\) | `close_input_cap5`; recursive EMA6/18, with ≥360 post-seed EMA updates and recent coverage gate | Relative price spread |
| 15 **T4** (long EMA spread) | \((E_{24,t}-E_{72,t})/C_t\) | Same field; recursive EMA24/72, same warmup/coverage gate | Relative price spread |
| 16 **T5** (normalized RSI) | \((\operatorname{RSI}_{14,t}-50)/50\) | Successive `close_input_cap5` price differences; 14 seed changes + ≥140 subsequent Wilder updates, recent coverage gate | Bounded [−1,1]; special zero-gain/loss rules below |

Formula authority: `src/lstm_data/hf1m_ft16_fit.py:49–76` (`native`) and `hf1m_ft16_math.py:123–229` (`build`). The order is `hf1m_ft16_source.py:15–17`, not alphabetical order. M3/M4 momentum numerators require their specified endpoints; the code does not add a separate completeness requirement over all 5/105 intervening closes.

### M2: historical labels used only after maturity

For P020/S1/S2, context \(o=0\) is the 10:30 origin and \(o=1\) is 11:30. On prior regular day j,

\[
R^{(o)}_{i,j}=\log\left(G_{i,p_j[o+4]}/G_{i,p_j[o]}\right),\quad
\mu^{(o)}_{20,i,t}=\operatorname{Mean}_{20,19}(R^{(o)})_{k(t)},\quad
s^{(o)}_{60,i,t}=\operatorname{RMS}_{60,57}(R^{(o)})_{k(t)}.
\]

Here \(p_j[0..5]\) are that day's six full-hour positions. Endpoints must be genuine and price-basis compatible. The forecast's context is held fixed across **all 48 historical steps**, but each step uses its own preceding-day history. It is not a current forecast's future return repeated into the sequence.

S4/S9 use seven contexts: `0..5 = 10:30,11:30,12:30,13:30,14:30,15:30`, `6 = 09:30`. Historical R is the genuine endpoint return over **240 XNYS trading minutes**, including closing stubs and pausing across closures; later origins can mature next session. Opening R uses the genuine first-minute **open**, not close. For each historical input session, only prior regular-origin days enter; an endpoint whose `label_maturity_utc >= current session 09:30` is masked **within its original scheduled slot**. In particular, the latest overnight outcome is not available merely because its origin day is yesterday. Apply the same 20/60 count/gap rules; values are locked for that entire input session. Early-close input days use preceding regular-origin dates with the same maturity test. COP dependency masks also apply.

Authority: `hf1m_ft16_math.py:157–159,214–229`; `hf20_s4_clock.py:18–70`; `hf20_s4_preflight.py:143–212,219–250`. S3-B's verified horizon substitution is described in §6.

### EMA and RSI state, exactly

For each period p ∈ {6,18,24,72}, seed \(E_p=C\) at the first valid close; thereafter \(E_{p,t}=\alpha_p C_t+(1-\alpha_p)E_{p,prev}\), \(\alpha_p=2/(p+1)\). The first seed does **not** increment `ema_updates`. T3/T4 require `ema_updates >= 360`. All T3/T4/T5 outputs additionally require a valid current close and ≥69 valid closes in the last 72 scheduled positions with maximum missing run two; the full 72 positions must exist.

RSI seeds average gain/loss with arithmetic means of positive/negative parts of the first 14 valid predecessor-connected price changes. Each later connected change Δ updates \(A=(13A+\max(\Delta,0))/14\), \(B=(13B+\max(-\Delta,0))/14\). After ≥140 such post-seed updates, \(RSI=100-100/(1+A/B)\). Normalized output is 0 when A=B=0, +1 when only B=0, −1 when only A=0.

A missing close freezes EMAs and clears the RSI predecessor. Before RSI seeding it also clears seed changes; after seeding it preserves gain/loss averages but creates no change across the gap. Three consecutive invalid scheduled full-hour closes reset the entire indicator state; a price-basis change also resets it. Normal overnight closure is not a missing scheduled observation. Authority: `stock_features.py:44–96` (`IndicatorState`); `hf1m_ft16_math.py:192–213`.

## 4. Preprocessing, fitted parameters and fallback

### Price, volume and missingness policy

P019B adjusts **OHLC prices only** backward for verified splits through 2026-03-31; prices are split-consistent, not dividend-total-return adjusted. Volume remains in observed share units. COP's 2012-05-01 spinoff separates price bases; the 125-regular-session dependency history plus 48-step envelope is masked. Split share regimes separately reset incompatible volume ratios. No unverified inverse split-volume conversion is applied. See `configs/hf1m_action_qa_v1.json`, `configs/hf1m_p019_verified_event_facts_v1.json`, `hf1m_action_source.py:67–95,237–256`, `hf1m_action_release.py:208–236`, and S4's equivalent `hf20_s4_preflight.field_masks():25–54`.

P019B removes 18 unresolved RTH minutes; genuine expected opens/closes can survive independently, but affected-hour high/low are masked and volume is unusable. No close proxy is allowed in a quarantined hour. Elsewhere `close_input_cap5` can reuse an original causal terminal proxy with missing-run cap five. Proxy creation uses a preceding observed close, never interpolation from a later bar, and rejects no-observation/action-blocked bins; carry state resets each session. The completed bin's known gap length determines acceptance; a later-discovered longer outage cannot rewrite an earlier trailing proxy. See `hf_minute_long_qa.py:92–118,395–403` and `hf1m_action_source.py:210–234`.

Usable hourly volume requires at least one genuine minute, ≤5 absent minutes, longest gap ≤5 minutes, and **zero conflicts, quarantines and invalid minutes**. Absent-minute zero is a feature-only assumption: observed sums remain lower bounds, not evidence of no trades. Otherwise \(U_t\) is missing. Real observed zero volume is retained. Daily W requires all six usable hours and compatible volume bases; stub volume is excluded. Q1's prior matching slots and Q2's daily windows cannot mix share regimes. Missing or unseen fitted pseudocount regimes produce native missingness, then feature fallback. Authority: `hf1m_ft16_math.py:36–63,147–191`.

### Fitting population and numerical rules

For each fold/phase, the fit-hour set F is the **union** of all 48 scheduled history keys of `source_input_eligible` origins in that training prefix, clipped to `[2011-04-01, fit_stop_inclusive]`. No overlapping-window multiplicity and no label-value filter are used to choose feature-fit keys. Warmup components may use source history from July 2010, but those pre-start keys are excluded from fitted input statistics. For daily floor and M2 pools, J is the first F timestamp per input session (`drop_duplicates("session_date_et")`), including eligible early-close input days.

| Fitted quantity | Exact estimation |
| --- | --- |
| Hourly floor \(h_i\) | NumPy 5th percentile of strictly positive finite RMS12 **concatenated with** RMS60 at F, separately per stock (a timestamp can contribute both RMS values) |
| Daily floor \(\delta_i\) | NumPy 5th percentile of positive finite carried RMS63 values at J, separately per stock |
| M2 floor \(b_i\) | Weighted 5th percentile of positive finite M2 RMS values at J, separately per stock; context total mass 1/2 for original two-context runs, 1/7 for S4/S9; equal weights within each context's valid values |
| Hourly/day volume pseudocount | 0.01 × median positive finite volume, separately per stock and share regime. Hour pool uses F; daily pool uses **all regular days** in `[2011-04-01, stop]`, not just J. Both hour and day positive pools must exist for that regime |
| Common-channel center/scale | Native finite values pooled across stocks and unique F timestamps, independently for each of the 15 non-M2 channels; no window/session-loss weighting |
| M2 center/scale | Native finite stock/session/context values at J, pooled across stocks with equal total mass per context (1/2 or 1/7), not weighted by forecast-slot frequency |

An unweighted quantile uses `np.quantile` / `np.percentile` default linear interpolation. A weighted quantile sorts values stably and selects the first value whose normalized cumulative weight is ≥q (`searchsorted(..., side="left")`); it does not interpolate. Missing all required positive/native training pools raises an error; it does not borrow another stock's floor or another regime's pseudocount.

For each of the **13 unbounded channels** (M1/M2/M3/M4/V1/V2/V3/B1/Q1/Q2/T1/T3/T4), let c be its native training median and MAD = median(|x−c|), using the above weights for M2. Use scale s = MAD if positive; otherwise `(Q75−Q25)/1.349`; otherwise population SD about the mean; otherwise exactly 1 for a constant. **MAD is unscaled**, without a 1.4826 factor. Replace nonfinite native x with c, then output `(x−c)/s`. Consequently these fallbacks become model-space zero. Fit statistics use native values **before imputation**.

**B2/T2/T5:** replace nonfinite values by neutral 0; center 0/scale 1, `BOUNDED_IDENTITY`. There is **no input clipping, winsorization, asinh/log1p mapping of the full tensor, or per-sequence normalization**. Feature-specific logarithms and denominator floors are already part of the native formulas. Final arrays are cast to `float32`; component arithmetic generally uses NumPy floating arrays. Native-missing/fallback/proxy/quality masks remain separate diagnostic data, not extra FT16 channels. A missing required input close cannot be repaired by feature median fallback to admit a deficient 48-close window. Targets have no feature-style imputation.

Authority: `hf1m_ft16_fit.py:12–46,49–187`; S4 seven-context counterpart `hf20_s4_fit.fit_expanded():13–125`; recipe application `hf20_s4_witnesses.scaled():19–32`; prefix selection `hf20_s4_data.py:105–157` and `hf20_ranking_data.py:189–243`.

### Actual saved fitting windows

S4 and S9 use the following eight input recipes. Every start is **2011-04-01**; an inner recipe is applied unchanged to inner validation, and a refit recipe unchanged to that fold's OOS year. All exact floors, pseudocounts, scalers, native fallbacks and fit-hour indices are in the corresponding `S4/Fxx_phase_recipe.json` (`floors`, `scalers`, `fallbacks`, `fit_hour_indices`).

| Fold / OOS year | Inner inclusive stop | Refit inclusive stop | Unique F timestamps inner / refit | Unique J sessions inner / refit |
| --- | --- | --- | --- | --- |
| F21 / 2021 | 2020-06-30 | 2020-12-31 | 13,102 / 13,864 | 2,198 / 2,326 |
| F22 / 2022 | 2021-06-30 | 2021-12-31 | 14,567 / 15,247 | 2,445 / 2,560 |
| F23 / 2023 | 2022-06-30 | 2022-12-30 | 15,991 / 16,716 | 2,684 / 2,808 |
| F24 / 2024 | 2023-06-30 | 2023-12-29 | 17,420 / 18,164 | 2,926 / 3,052 |

Original P020 preparation's `P020/train_only_fit_recipes.json` instead has inner stop **2023-01-23** and refit stop **2025-06-30**. Those are not the annual S4/S9 recipes and must not be substituted for them. S1/S2 annual recipes also share the earlier cutoffs above but have different input-key populations, e.g. F21 inner has 13,057 F timestamps / 2,197 J sessions rather than S4's 13,102 / 2,198.

## 5. Exact 48-step sequence and leakage controls

For an admitted origin, set `first_step = entry_index − 47`. Gather the 48 consecutive scheduled grid positions `first_step + arange(48)` in chronological order. The common 15 fields depend on stock and historical timestamp; M2 additionally selects the **forecast-origin context for every historical step**. In S4, `assemble()` returns `[origins, 20 stocks, 48 steps, 16 features]`, `float32`, in §3 order. The LSTM receives stock sequences reshaped to `[origins×20,48,16]`; weights are shared across stocks, and hidden/cell states start at zero on every call. No recurrent state carries from an overlapping prior sequence.

At a full-hour forecast, the last step is the bar ending at that origin. At conditional **09:30**, the last step is the most recent prior-session full-hour bar (normally ending 15:30, or 12:30 on an early close). Neither the new day's 09:30–10:30 bar nor the opening price is inserted into FT16. The opening price is a genuine reference for labels only. Thus 48 means scheduled trading observations, **not 48 elapsed clock hours**, and feature calculations can require substantially older history.

Input eligibility requires all 20 stocks to have 48 finite cap5 input closes, the daily-history warmup (`day_index >=125`, allowing the required 126 prior regular-session closes), ≥360 cumulative genuine hourly closes, and the COP dependency envelope. Other native channel deficiencies use the declared feature fallback. Input eligibility is computed independently of future endpoint validity; supervised/evaluation membership additionally requires a complete eligible 20-stock label panel. S4's final `eligible` combines its source and label masks, rather than manufacturing missing endpoints.

Issuance is assumed at origin +2 minutes; label maturity at genuine endpoint +2 minutes. S4 endpoints consume 240 actual trading minutes and may include overnight closure; the price-only return starts at the nominal origin, **before issuance**, and is not an executable fill return. For a normal 10:30 forecast the newest feature bar covers 09:30–10:30; for 09:30 issuance at 09:32, inputs still end with the prior session's last full hour. Publication latency is an assumption, not verified historical availability.

Daily statistics always use prior regular days, Q1 shifts same-slot history by one occurrence, all rolling functions are backward-looking, and M2 maturity is checked at **each historical input session**, not just at the current prediction time. Scalers/floors/fallbacks are prefix-only and fixed for the relevant validation/OOS phase. Split admission requires the first of all 48 input steps to be after the preceding boundary (48-full-step embargo), and labels to mature before their role cutoff. S4 additionally retains the conservative four-hour boundary limit: cutoff-day local midnight +1 day −4 hours, with `label_maturity_utc < limit`. Future outcomes remain labels except for strictly matured historical outcomes used in M2.

Authority: `hf20_s4_preflight.input_valid():57–67` and `run():235–255`; `hf20_s4_witnesses.assemble():35–56`; `hf20_s4_data.S4Data:32–76,159–178`; `hf20_s4_epoch.py:47`; `neural_engine.SharedLSTM:28–54`. Original two-slot gather: `hf20_ranking_data.assemble():24–49`. S4 clock: `hf20_s4_clock.schedule():39–70`.

## 6. Are S1–S9 identical?

**No: stable feature IDs/economic meanings do not imply identical contexts, fitted parameters or complete model inputs.**

| Stage | Verified executed input treatment |
| --- | --- |
| S1 | Baselines consume the original two-context FT16 path; full-history ridge uses the 48-step information. Not every control uses all channels: N1/N2 use M1/sign reversal; N0/P are constant/profile controls. See `S12/S1_FOUR_FOLD_RANKING_BASELINES.md` and `S12/Fxx_phase_recipe.json` |
| S2 | Same two-context FT16 recipe family and per-fold inputs as S1 for T2R/NR/PW; objectives differ, not feature formulas. Failed F21 PW is preserved and has no completed refit/OOS surrogate. See `S12/S2_FOUR_FOLD_LSTM_RANKING_COMPARISON.md`, `hf20_ranking_data.py` |
| S3-A | H1/H2 labels change, but all 16 input channels, including original **four-hour M2**, reuse S1/S2 phase recipes. H4 references are archived runs, not new fits |
| S3-B | **Only M2 changes** to historical same-origin H1 or H2 genuine endpoint returns; mean20/RMS60, gap rules, two contexts and 50/50 pooling remain. M2 floors, fallback center and scaler are refitted on the original unique input-prefix day keys. Other 15 channels remain unchanged. Saved `S3_M2` overrides are authoritative; inherited top-level M2 fields are lineage, not the active B parameters |
| S4-A | Same 15 non-M2 native formulas; **seven M2 contexts**, 240-trading-minute endpoint/maturity handling and prior48 opening inputs. Feature-fit origin/key support expands, so even common-channel fitted floors/scalers can differ from S1/S2. M2 pooling changes to equal 1/7 context mass. NR and T2R share these phase recipes |
| S5 | Reuses S4 FT16 unchanged, then appends **six clock fields**, making **22 model inputs**: `step_sin`, `step_cos`, `session_boundary`, `elapsed_scheduled_wall`, `origin_sin`, `origin_cos`. Scheduled elapsed time is not observed-price age; source-repair flags are not model features |
| S6–S8 | **NOT VERIFIED as executed FT16 experiments.** Latest completed S5/S9 handoff explicitly states no S6/S7/S8 was launched; no identical-feature assertion is justified for those stages |
| S9-MAG / EVENT / QUANTILE | Exactly S4's 48×16 input and saved phase recipes, no S5 extra metadata. Different label/head/objective definitions do not change FT16 |

S3 evidence: `S3/EXECUTION_MANIFEST.json`, `S3/S3_FINAL_RESEARCH_DECISION.md`, `S3/{A,B}/Fxx_H{1,2}/Fxx_phase_recipe.json`; `hf20_horizon_data.py:42–45,92–164`; `hf20_horizon_math.py:98–175`. In B, apply `S3_M2.floors` and `S3_M2.scaler`. Older `hf20_s3_horizons_2026-10-26_000127_preparation` documents marked NOT_RUN predate completed live execution and do not establish final run status.

S5/S9 evidence: `hf20_s5s9.py:23–51,82–131`; S6–S8 status: `S59/LIVE_WORK_SESSION_REPORT.md`, §16. For MAG specifically, the optimized target is `log1p(abs(R)/magnitude_scale)`, with prefix-fitted magnitude scale; this is **not a feature transformation** (`hf20_s5s9.py:60–67,141–179`). Likewise the target-transform term **T2/T2R/asinh is distinct from FT16 feature T2**, the daily sign average.

## 7. Source map for replication

Line ranges refer to source at the extraction commit; paths below are exact. No module listed here was executed for this extraction.

| File | Relevant implementation / evidence |
| --- | --- |
| `configs/hf1m_long_ft16_v1.json:1–91` | Source revision, symbols, feature ID/order, warmup/splits, volume tier, timing assumptions; original P020 recipe defaults |
| `configs/hf1m_action_qa_v1.json` and `configs/hf1m_p019_verified_event_facts_v1.json` | Frozen price adjustment, quarantine and event facts; volume regime policy |
| `src/lstm_data/hf1m_action_source.py:67–95,141–309` | Price split factors, genuine-hour aggregation, quarantines, cap5 terminal input-close selection |
| `src/lstm_data/hf_minute_long_qa.py:48–118,395–403` | Minute validity, session-hour grid, causal bounded proxy rules |
| `src/lstm_data/hf1m_action_masks.py:39–41,49–108` | Scheduled full-window AND, original source warmup/basis eligibility |
| `src/lstm_data/hf1m_action_release.py:208–236` | P019B volume-basis and COP dependency overlay |
| `src/lstm_data/hf1m_ft16_source.py:13–17,24–101` | Exact order/bounded IDs, source allowlists and identity checks |
| `src/lstm_data/hf1m_ft16_math.py:15–63,84–232` | Rolling rules, quality-conditioned volume, all source components/daily alignment/original M2 |
| `src/lstm_data/stock_features.py:44–96` | Actual imported EMA/Wilder state; other legacy feature calculators are not this pipeline |
| `src/lstm_data/hf1m_ft16_fit.py:12–187` | Quantiles, robust scales, positive floors, native 16-channel formulas and original two-context fitting |
| `src/lstm_data/hf1m_ft16_prepare.py:47–102,129–154` | P020 origin/window timing, input-only fitting keys, separate target parameters |
| `src/lstm_data/hf20_ranking_data.py:24–49,75–140,189–273` | S1/S2 gather, annual split masks and actual prefix recipes |
| `src/lstm_data/hf20_s4_clock.py:10–83` | XNYS schedule, actual trading-minute endpoints, seven contexts and issuance/maturity |
| `src/lstm_data/hf20_s4_preflight.py:25–67,70–140,154–212,235–255` | P019B-equivalent masks, permitted monthly source inventory, expanded M2 and prior48 opening indices |
| `src/lstm_data/hf20_s4_fit.py:13–125` | Executed S4 seven-context fitting implementation (historical docstring still says proposed) |
| `src/lstm_data/hf20_s4_witnesses.py:19–56` | Apply sealed scales and gather exact float32 48×16 tensors |
| `src/lstm_data/hf20_s4_data.py:32–76,90–178` | Fold maturity/embargo, fitting keys, saved recipe application and role guards |
| `src/lstm_data/hf20_s4_run.py:30–45` | Actual source adapter loads card-selected `opening_reaudit_v2` source/endpoint stores and replaces M2 components with seven-context values |
| `src/lstm_data/hf20_s5s9.py:82–131` | S9 reuses exact S4 recipes; only S5 appends metadata |

For byte-exact input replication, preserve the **saved recipe**, not just the written formulas. Resolve the recorded monthly inputs from `P019B/adjusted_hourly_manifest.json` and `S4/opening_reaudit_v2/S4_NUMERICAL_SOURCE_READS.csv`. The adjusted-hourly root is `data/processed/hf20_hf1m_long_v1_action_qa_v1/ta019b_action_qa_2026-10-22_201224/hourly/`. S4 source/role identities are in `S4/opening_reaudit_v2/S4_ORIGIN_SOURCE_ELIGIBILITY.parquet`, `S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet` in that same subdirectory, and `S4/Fxx_{inner_train,inner_validation,refit,oos}_indices.csv`.

Existing scalar/tensor evidence: `P020/independent_oracle_and_causality.json`, `P020/preparation_execution_snapshots/hf1m_ft16_{math,fit,source,prepare,loader}.py.txt`, and `S4/opening_reaudit_v2/{S4_ARCHIVED_ALL16_TENSOR_IDENTITY,S4_ALL16_SCALAR_SOURCE_WITNESSES}.csv`. These are supporting historical records; archived original-recipe tensor identity does **not** mean newly fitted S4 recipes equal S1/S2 recipes. S9 input-recipe SHA identities are recorded in `S59/S4_REUSED_RECIPES.json`.

## 8. NOT VERIFIED / replication qualifications

- **NOT VERIFIED — historical publication latency and point-in-time availability.** Config explicitly sets `publication_timing_verified:false`; two-minute issuance is assumed. Arithmetic cutoffs/maturity controls do not certify that a vendor delivered each minute, opening quote or correction by that time.
- **NOT VERIFIED — historical action-information vintage.** Executed OHLC uses backward split factors through March 2026 and known quarantine/event facts. This is the implemented retrospective representation; it does not prove those facts were known contemporaneously. Scale invariance and stored causal-prefix evidence do not independently certify historical publication timing.
- **NOT VERIFIED — economic meaning of missing minute volume, complete extrema and share-volume adjustment.** Small absent gaps are assumed zero only for features. Provider absence versus no trading is unresolved; observed ranges/volumes can be incomplete. No independently verified inverse split-volume convention exists, so replication must retain share-regime masking rather than invent an adjustment.
- **NOT VERIFIED — bitwise reproduction on another machine from this document alone.** Exact source bytes, recorded adjusted-hourly/endpoint stores, fitted numerical recipes, grid order and compatible NumPy/pandas/calendar versions remain necessary. This extraction did not reopen numerical datasets, rerun hash audits, reconstruct tensors or validate a clean-machine replay. Existing manifests/receipts supply recorded identities, not a fresh certification. Private source accessibility/redistribution is not established here.
- **NOT VERIFIED — S6/S7/S8 executed definitions.** The latest completed handoff says they were not launched; proposals cannot supply executed definitions. No feature equality claim is made for them.

No unknown formula or parameter was filled from a generic indicator library, older source branch, proposal or inferred research preference. Numerical input parameters are available in the cited saved recipes; they are phase-specific, not universal constants omitted from the implementation.
