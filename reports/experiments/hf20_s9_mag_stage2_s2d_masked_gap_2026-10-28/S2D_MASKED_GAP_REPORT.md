# S2-D genuine overnight-gap magnitude — masked stock-day panel

**Status: COMPLETE — 4/4 folds.** LOWER_MSE_THAN_BOTH_FROZEN_MEAN_CONTROLS_REVIEW_TRADEOFFS. Exploratory/post-search.

**COMPLETE: four valid folds; provisional evidence of incremental raw-gap-magnitude MSE quality against the predeclared controls.** On the new variable-size masked panel of **15,325 stock-days / 776 sessions**, equal-year S2D-SMEAR raw MSE is **0.000080683492553**, versus fixed primary GAP-RMEAN **0.000084924085368** (**−4.9934%**). All four annual point contrasts improve: **−5.1828%, −10.6760%, −0.4879%, −2.6050%**. The whole-month descriptive equal-year delta interval is **[−5.84551e−6, −2.62205e−6]**, with point delta−4.24059e−6. F23/F24 annual intervals include zero; about64.9% of the net primary gain is from2022. These are conditional, post-search results, not independent confirmation.

The individually predeclared locked RECENT20 contrast is **−22.1319% MSE**; the explicitly more-current LIVE RECENT20 diagnostic is **−4.8237%**. No OOS-best baseline was selected. The locked control is particularly weak in2021, so its large aggregate gap is not the principal evidence. All four annual LIVE point contrasts also favor the LSTM, with F23/F24 intervals including zero. Raw uncalibrated LSTM MSE is0.000083422340365; the fixed smear improves it3.2831%, while worsening its MAE7.7606%. Raw remains a diagnostic, not an ex-post primary winner.

Trade-offs remain: primary MAE0.00515107431 is2.0810% below GAP-RMEAN and2.0007% below LIVE, but **2.9516% worse than the MAE-oriented GAP-RMED**. Primary mean ratio is1.03624 and varies1.1666/.9669/1.1121/.9280 annually; LIVE's aggregate mean ratio1.00394 is closer to one. Primary IC.363285 vs GAP-RMEAN.354510 improves on average, but loses in2023/2024. Top-four retrieval.42375 compares with a variable-panel chance.20280, not a fixed20% convention. The observed OOS panel has14–20 genuine names/date under the uniformly fixed minimum10.

Four starts/eight phases completed without failure/retry: **162→166/300**, selected epochs6/3/4/24. Original all20 FT16 input eligibility and all50/month gates remain. The earlier strict20 S2-D stays archived BLOCKED, and all four-hour S2-B/C studies are frozen separate tasks. No protected2026,2025 market research,source expansion,network,options/trading,extra model or deferred route.

## Target, timing and population

A_gap=abs(log(next scheduled genuine09:30 minute open/current genuine final-minute regular-session close)). One normal full-day15:30 forecast per stock/session, approximate15:32 issuance before16:00 close. This is not15:32-to-open execution, a four-hour endpoint target, signed alpha, integrated variance or option profit. Source references are vendor-adjusted/quarantine-filtered last-minute closes and minute opens, not verified auction fills. No early close remapping, synthetic price, duplicate nightly label or future gap input.

This is an explicit prospective amendment of the strict20 blocked S2-D: original20-name universe and all20 FT16 input eligibility remain, but only sessions with>=10 genuinely labeled stocks are admitted and actual valid stocks receive equal weight within each date. Source support is retrospective, not known as a future tradable stock-selection rule. Missing labels never become zero or a small realized gap. All arrays retain canonical tensor order; no label support is a neural feature. Main four-hour S2-B/C studies are untouched and no four-hour MSE appears in the comparison.

## All-fold gate, source and coverage

| year | role | sessions | stock_days | min_valid_stocks | max_valid_stocks | months | minimum_month_sessions | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | inner_train | 2080 | 41274 | 17 | 20 | 105 | 0 | PASS |
| 2021 | selector | 56 | 1117 | 19 | 20 | 3 | 15 | PASS |
| 2021 | restricted_refit | 2144 | 42550 | 17 | 20 | 108 | 0 | PASS |
| 2021 | calibration | 54 | 1068 | 18 | 20 | 3 | 15 | PASS |
| 2021 | oos | 183 | 3591 | 14 | 20 | 12 | 7 | PASS |
| 2022 | inner_train | 2278 | 45208 | 17 | 20 | 115 | 0 | PASS |
| 2022 | selector | 56 | 1068 | 14 | 20 | 5 | 7 | PASS |
| 2022 | restricted_refit | 2342 | 46431 | 14 | 20 | 120 | 0 | PASS |
| 2022 | calibration | 47 | 937 | 19 | 20 | 3 | 8 | PASS |
| 2022 | oos | 205 | 4070 | 18 | 20 | 12 | 6 | PASS |
| 2023 | inner_train | 2500 | 49573 | 14 | 20 | 128 | 0 | PASS |
| 2023 | selector | 56 | 1112 | 19 | 20 | 4 | 6 | PASS |
| 2023 | restricted_refit | 2564 | 50842 | 14 | 20 | 132 | 0 | PASS |
| 2023 | calibration | 46 | 914 | 19 | 20 | 3 | 12 | PASS |
| 2023 | oos | 186 | 3676 | 16 | 20 | 12 | 8 | PASS |
| 2024 | inner_train | 2692 | 53375 | 14 | 20 | 140 | 0 | PASS |
| 2024 | selector | 66 | 1304 | 18 | 20 | 4 | 14 | PASS |
| 2024 | restricted_refit | 2766 | 54838 | 14 | 20 | 144 | 0 | PASS |
| 2024 | calibration | 38 | 754 | 19 | 20 | 3 | 8 | PASS |
| 2024 | oos | 202 | 3988 | 18 | 20 | 12 | 7 | PASS |

All20 role session/stock-day counts reproduce the coverage audit under the fixed>=10 rule after positive/finite source certification. Selector>=50 and monthly>=5,calibration>=25 and monthly>=5,OOS>=100/all12 months,prefix>=252 remain binding. Gap maturity is next-open+2min, and first-of48 input-step date must exceed role embargo. The future four-hour endpoint/label-eligible flag is never used for gap admission. Original15:30 inputs end exactly15:30 and every grid step is a completed full60 minutes;16:00 close is future label-only.

source_validation.json binds source versions and exact allowed columns/semantics. stock_month_coverage.csv,monthly_role_counts.csv and eligibility_exclusions.csv disclose label/input/embargo/maturity attrition;baseline_history.csv proves all20 required controls have>=20 genuine historical gaps. The audit's2-stock selector date is excluded by the fixed>=10 gate. Source selection concentrates in MS/MRK and other historical provider gaps, not assumed random. Role arrays/stock masks and hashes are in role_masks.npz/preflight.json. Prefix monthly minimum0 is descriptive only; the monthly5 gate applies only to selector/calibration. No source repair, minute store,2025 market or2026 protected access.

## Frozen model, phase fitting and baselines

Original H32 one-layer48×16 shared LSTM,6433 parameters,scalar transformed-gap head,final hidden dropout.10,zero recurrent state per window,seed42,CPUfloat32. No S2-B clock vector or S2-C heads. AdamW lr.001 betas(.9,.999)eps1e-8,matrix decay.01,bias0,clip1;16 full sessions shuffled42+epoch. Loss is equal valid-stock M_gap squared error within each admitted date, then equal dates; masked cells never enter target arithmetic and have zero loss gradient. Selector monitors this same gap M risk with .999 qualified best,min12,patience10,max60,followed by fresh same-seed/empty-optimizer September refit at selected epochs.

Every phase independently fits its own weighted-left-median gap s (floor1e-8); no four-hour scale/threshold/coef is borrowed. Own input-only-prefix recipes exactly reproduce the inherited FT16 recipes at the same cutoffs. The native FT16 M2 construction may read historical original four-hour returns as part of its unchanged causal features; these are not gap targets or admission criteria. Own September checkpoint/recipe/s generates both independent Oct–Dec and following OOS predictions unchanged.

The fixed principal mean-target reference is B0-GAP-RMEAN,not an OOS winner. Also report stock weighted median (MAE-oriented),frozen September stock RECENT20 and live-updated RECENT20. Mean/median use only legal phase prefix labels weighted by the masked panel; stock normalization conditions those weights. RECENT20 is the arithmetic mean of20 actual observed matured gaps per stock; no imputed or current-night observations. Locked uses only September role. LIVE uses an explicitly more-current normal15:30 input/source-admissible>=10 bank with maturity strictly before issuance,including preceding calibration/OOS labels;it is not an identical-history principal control or a tuning signal. No baseline selection,fit on test outcomes,EWMA/GARCH/HAR expansion or fallback. Optional lagged EWMA/RMS: NOT INCLUDED, no already-verified gap implementation reused.

| year | selected_epoch | selector_epochs | raw_minimum_epoch | initial_scale_gap | restricted_scale_gap | seconds | peak_rss_bytes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 6 | 16 | 6 | 0.0038734716 | 0.0039101288 | 108.42999 | 920240128 |
| 2022 | 3 | 13 | 3 | 0.0039852559 | 0.0039871653 | 88.098305 | 920240128 |
| 2023 | 4 | 14 | 4 | 0.0040582323 | 0.0041048368 | 104.52947 | 920240128 |
| 2024 | 24 | 34 | 24 | 0.0041543086 | 0.0041473349 | 290.08367 | 920240128 |

## Annual and equal-year gap scores

| year | arm | rows | sessions | observed | predicted | bias | ratio | raw_MSE | raw_MAE | magnitude_IC | top4 | chance_top4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | S2D-SMEAR | 3591 | 183 | 0.0066961811 | 0.0078119796 | 0.0011157985 | 1.1666321 | 5.1932478e-05 | 0.0048637915 | 0.38427 | 0.40163934 | 0.2043861 |
| 2021 | S2D-RAW | 3591 | 183 | 0.0066961811 | 0.0047868868 | -0.0019092943 | 0.71486817 | 5.4386541e-05 | 0.004296384 | 0.38427 | 0.40163934 | 0.2043861 |
| 2021 | B0-GAP-RMEAN | 3591 | 183 | 0.0066961811 | 0.0068493244 | 0.00015314334 | 1.0228703 | 5.4771169e-05 | 0.0048357196 | 0.33903871 | 0.34289617 | 0.2043861 |
| 2021 | B0-GAP-RMED | 3591 | 183 | 0.0066961811 | 0.0041905835 | -0.0025055976 | 0.62581693 | 6.1576513e-05 | 0.0045453429 | 0.34269128 | 0.34289617 | 0.2043861 |
| 2021 | B0-GAP-RECENT20-LOCKED | 3591 | 183 | 0.0066961811 | 0.010279496 | 0.0035833147 | 1.5351281 | 0.00011348888 | 0.0069402482 | 0.30896969 | 0.26502732 | 0.2043861 |
| 2021 | B0-GAP-RECENT20-LIVE | 3591 | 183 | 0.0066961811 | 0.0068340479 | 0.00013786681 | 1.0205889 | 5.482136e-05 | 0.0047603712 | 0.36572226 | 0.4057377 | 0.2043861 |
| 2022 | S2D-SMEAR | 4070 | 205 | 0.0094275976 | 0.0091150922 | -0.00031250544 | 0.96685206 | 9.2049357e-05 | 0.006168406 | 0.42236752 | 0.42195122 | 0.20154614 |
| 2022 | S2D-RAW | 4070 | 205 | 0.0094275976 | 0.0072205298 | -0.0022070678 | 0.76589287 | 9.6776546e-05 | 0.0059665965 | 0.42236752 | 0.42195122 | 0.20154614 |
| 2022 | B0-GAP-RMEAN | 4070 | 205 | 0.0094275976 | 0.0069307897 | -0.0024968079 | 0.73515969 | 0.00010305106 | 0.0061302946 | 0.38938184 | 0.34512195 | 0.20154614 |
| 2022 | B0-GAP-RMED | 4070 | 205 | 0.0094275976 | 0.0042797721 | -0.0051478255 | 0.45396211 | 0.00012588948 | 0.0066003143 | 0.38947528 | 0.39146341 | 0.20154614 |
| 2022 | B0-GAP-RECENT20-LOCKED | 4070 | 205 | 0.0094275976 | 0.0058498893 | -0.0035777083 | 0.62050689 | 0.0001129235 | 0.0062632666 | 0.3485509 | 0.3097561 | 0.20154614 |
| 2022 | B0-GAP-RECENT20-LIVE | 4070 | 205 | 0.0094275976 | 0.0093511632 | -7.643442e-05 | 0.99189248 | 9.842609e-05 | 0.0064613904 | 0.40332341 | 0.41097561 | 0.20154614 |
| 2023 | S2D-SMEAR | 3676 | 186 | 0.0063723571 | 0.0070866603 | 0.00071430322 | 1.112094 | 7.5949668e-05 | 0.0047482341 | 0.32402742 | 0.4233871 | 0.20254512 |
| 2023 | S2D-RAW | 3676 | 186 | 0.0063723571 | 0.0051228841 | -0.001249473 | 0.80392295 | 7.7058384e-05 | 0.0042612768 | 0.32402742 | 0.4233871 | 0.20254512 |
| 2023 | B0-GAP-RMEAN | 3676 | 186 | 0.0063723571 | 0.0070825065 | 0.00071014942 | 1.1114422 | 7.6322067e-05 | 0.0047563257 | 0.34421516 | 0.38172043 | 0.20254512 |
| 2023 | B0-GAP-RMED | 3676 | 186 | 0.0063723571 | 0.0044245869 | -0.0019477702 | 0.69434071 | 8.0823161e-05 | 0.0042489055 | 0.35570759 | 0.40994624 | 0.20254512 |
| 2023 | B0-GAP-RECENT20-LOCKED | 3676 | 186 | 0.0063723571 | 0.0083194612 | 0.0019471042 | 1.3055548 | 8.2858253e-05 | 0.0054441663 | 0.33612096 | 0.41263441 | 0.20254512 |
| 2023 | B0-GAP-RECENT20-LIVE | 3676 | 186 | 0.0063723571 | 0.0065327634 | 0.00016040631 | 1.0251722 | 7.7767177e-05 | 0.004640591 | 0.32239581 | 0.37096774 | 0.20254512 |
| 2024 | S2D-SMEAR | 3988 | 202 | 0.0064907696 | 0.006023702 | -0.0004670676 | 0.92804126 | 0.00010280247 | 0.0048238657 | 0.3224743 | 0.4480198 | 0.2027329 |
| 2024 | S2D-RAW | 3988 | 202 | 0.0064907696 | 0.0049659958 | -0.0015247738 | 0.76508582 | 0.00010546789 | 0.0045961767 | 0.3224743 | 0.4480198 | 0.2027329 |
| 2024 | B0-GAP-RMEAN | 3988 | 202 | 0.0064907696 | 0.0070873939 | 0.00059662429 | 1.0919189 | 0.00010555205 | 0.0053198527 | 0.34540513 | 0.3700495 | 0.2027329 |
| 2024 | B0-GAP-RMED | 3988 | 202 | 0.0064907696 | 0.0044744725 | -0.0020162971 | 0.68935932 | 0.00011139743 | 0.0046190081 | 0.34380214 | 0.3700495 | 0.2027329 |
| 2024 | B0-GAP-RECENT20-LOCKED | 3988 | 202 | 0.0064907696 | 0.0053537055 | -0.0011370641 | 0.8248183 | 0.00010519172 | 0.0046943352 | 0.34657091 | 0.49257426 | 0.2027329 |
| 2024 | B0-GAP-RECENT20-LIVE | 3988 | 202 | 0.0064907696 | 0.0063830726 | -0.00010769699 | 0.98340767 | 0.00010807618 | 0.0051625861 | 0.32767928 | 0.44554455 | 0.2027329 |
| EQ | S2D-SMEAR | 15325 | 776 | 0.0072467263 | 0.0075093585 | 0.00026263217 | 1.0362415 | 8.0683493e-05 | 0.0051510743 | 0.36328481 | 0.42374937 | 0.20280257 |
| EQ | S2D-RAW | 15325 | 776 | 0.0072467263 | 0.0055240741 | -0.0017226522 | 0.76228546 | 8.342234e-05 | 0.0047801085 | 0.36328481 | 0.42374937 | 0.20280257 |
| EQ | B0-GAP-RMEAN | 15325 | 776 | 0.0072467263 | 0.0069875036 | -0.0002592227 | 0.96422899 | 8.4924085e-05 | 0.0052605481 | 0.35451021 | 0.35994702 | 0.20280257 |
| EQ | B0-GAP-RMED | 15325 | 776 | 0.0072467263 | 0.0043423538 | -0.0029043726 | 0.59921592 | 9.4921647e-05 | 0.0050033927 | 0.35791907 | 0.37858883 | 0.20280257 |
| EQ | B0-GAP-RECENT20-LOCKED | 15325 | 776 | 0.0072467263 | 0.0074506379 | 0.00020391161 | 1.0281384 | 0.00010361559 | 0.0058355041 | 0.33505311 | 0.36999802 | 0.20280257 |
| EQ | B0-GAP-RECENT20-LIVE | 15325 | 776 | 0.0072467263 | 0.0072752618 | 2.8535427e-05 | 1.0039377 | 8.4772702e-05 | 0.0052562347 | 0.35478019 | 0.4083064 | 0.20280257 |

A_gap/MAE/means/bias are absolute log-return units; MSE is squared log-return units. Equal surviving stocks/date→equal dates/year→arithmetic equal years; ratio is equal-year predicted/observed means. No naive equal-stock-day pooling. Variable-size cross-sectional IC uses average ranks within the same10–20 source-supported names; undefined constant cross-sections are excluded and counts disclosed. Pair concordance excludes realized ties, gives forecast ties.5;top/bottom4 use fractional tie membership and chance4/n_valid,not a fixed20%. Constant/tie/pair/bottom retrieval and valid IC count in metrics.csv.

## Paired dependent-time uncertainty

| reference | year | delta | low | high | percent_change | interval_includes_zero |
| --- | --- | --- | --- | --- | --- | --- |
| B0-GAP-RMEAN | 2021 | -2.8386914e-06 | -4.8173093e-06 | -6.5385803e-07 | -5.1828205 | False |
| B0-GAP-RMEAN | 2022 | -1.10017e-05 | -1.567973e-05 | -5.9856465e-06 | -10.67597 | False |
| B0-GAP-RMEAN | 2023 | -3.7239909e-07 | -2.0206958e-06 | 1.0875986e-06 | -0.48793108 | True |
| B0-GAP-RMEAN | 2024 | -2.7495808e-06 | -6.4222735e-06 | 8.9671963e-07 | -2.6049526 | True |
| B0-GAP-RMEAN | EQ | -4.2405928e-06 | -5.8455147e-06 | -2.6220466e-06 | -4.9933924 | False |
| B0-GAP-RECENT20-LOCKED | 2021 | -6.1556404e-05 | -7.0146559e-05 | -5.4008226e-05 | -54.24003 | False |
| B0-GAP-RECENT20-LOCKED | 2022 | -2.0874142e-05 | -2.6684563e-05 | -1.4934577e-05 | -18.485207 | False |
| B0-GAP-RECENT20-LOCKED | 2023 | -6.9085848e-06 | -1.0364749e-05 | -3.8974696e-06 | -8.3378355 | False |
| B0-GAP-RECENT20-LOCKED | 2024 | -2.3892541e-06 | -7.3004731e-06 | 8.6584137e-07 | -2.2713329 | True |
| B0-GAP-RECENT20-LOCKED | EQ | -2.2932096e-05 | -2.5974986e-05 | -2.0443753e-05 | -22.131898 | False |
| B0-GAP-RMED | 2021 | -9.6440354e-06 | -1.5712404e-05 | -4.027821e-06 | -15.661873 | False |
| B0-GAP-RMED | 2022 | -3.3840127e-05 | -4.1574144e-05 | -2.523291e-05 | -26.880821 | False |
| B0-GAP-RMED | 2023 | -4.873493e-06 | -8.1525163e-06 | -1.8782874e-06 | -6.0298224 | False |
| B0-GAP-RMED | 2024 | -8.5949624e-06 | -1.5018795e-05 | -4.5254407e-06 | -7.7155841 | False |
| B0-GAP-RMED | EQ | -1.4238155e-05 | -1.7145778e-05 | -1.1657638e-05 | -14.999903 | False |
| B0-GAP-RECENT20-LIVE | 2021 | -2.8888825e-06 | -4.9448886e-06 | -2.9346368e-07 | -5.2696294 | False |
| B0-GAP-RECENT20-LIVE | 2022 | -6.3767326e-06 | -1.0305866e-05 | -2.8267247e-06 | -6.4787016 | False |
| B0-GAP-RECENT20-LIVE | 2023 | -1.8175092e-06 | -4.1398944e-06 | 1.7084519e-07 | -2.3371161 | True |
| B0-GAP-RECENT20-LIVE | 2024 | -5.2737128e-06 | -1.1765484e-05 | 6.474196e-08 | -4.8796255 | True |
| B0-GAP-RECENT20-LIVE | EQ | -4.0892093e-06 | -6.0733409e-06 | -2.2078404e-06 | -4.8237336 | False |
| S2D-RAW | 2021 | -2.4540632e-06 | -5.7320815e-06 | 1.5745599e-06 | -4.512262 | True |
| S2D-RAW | 2022 | -4.7271883e-06 | -7.7780612e-06 | -1.7783018e-06 | -4.8846425 | False |
| S2D-RAW | 2023 | -1.1087163e-06 | -3.2040856e-06 | 7.0728186e-07 | -1.4388004 | True |
| S2D-RAW | 2024 | -2.6654234e-06 | -4.1457972e-06 | -1.286774e-06 | -2.5272369 | False |
| S2D-RAW | EQ | -2.7388478e-06 | -3.9853932e-06 | -1.4942823e-06 | -3.2831107 | False |

400 draws,seed22042,whole-calendar-month blocks with full correlated stock/session panels;year-stratified equal-year aggregation. Point differences are SMEAR minus each explicitly named control (negative favors LSTM). These are post-search descriptive95% intervals conditional on fitted weights,calibrator and repeated adjacent-year research;not selection-adjusted inference. No IID stock-row tests or independent confirmation. LIVE's history advantage and median's different functional remain explicit.

## Independent own-gap smearing

| year | scale_gap | c_gap | sessions | stock_days | effective_sessions | q_max | top10_share | top1pct_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 0.0039101288 | 1.3478311 | 54 | 1068 | 54 | 13.156049 | 0.068335813 | 0.068335813 |
| 2022 | 0.0039871653 | 1.1690412 | 47 | 937 | 47 | 10.610186 | 0.065279745 | 0.060228339 |
| 2023 | 0.0041048368 | 1.2128127 | 46 | 914 | 46 | 6.7146591 | 0.042831861 | 0.039069229 |
| 2024 | 0.0041473349 | 1.1160614 | 38 | 754 | 38 | 14.612171 | 0.077889984 | 0.062719769 |

Only one global own-gap exp(log1p(A_gap/s)-Mhat_gap) weighted moment is fitted on reserved Oct–Dec with the exact frozen September model/scale. Residual uses unclamped Mhat;raw decode alone maxes Mhat at0. No double inverse,borrowed C3 factors,conditional map,trimming or chosen raw winner. Calibration counts/effective sessions and top10/top1% weighted-moment concentrations above describe stability,not OOS performance. F24 tail is smaller; uncertainty does not refit the scalar.

## Reliability, tails, month and stock diagnostics

| arm | group | rows | sessions | raw_MSE | raw_MAE | ratio | weight_mass | raw_MSE_loss_share | forecast_top4_membership | false_low_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2D-SMEAR | PREFIX95 | 800 | 364 | 0.0012112995 | 0.026651998 | 0.29106315 | 0.051267145 | 0.69472916 | 0.50871699 | 0.19980476 |
| S2D-SMEAR | PREFIX99 | 95 | 76 | 0.0054719124 | 0.068349353 | 0.14377834 | 0.0061299908 | 0.44608406 | 0.65186509 | 0.12207917 |
| S2D-SMEAR | LE_PREFIX95 | 14525 | 776 | 2.6073803e-05 | 0.0040649943 | 1.2900527 | 0.94873286 | 0.30527084 | 0.18703931 | 0.5163238 |
| S2D-SMEAR | LE_PREFIX99 | 15230 | 776 | 4.4967229e-05 | 0.0047463448 | 1.103135 | 0.99387001 | 0.55391594 | 0.20004063 | 0.50233481 |
| S2D-RAW | PREFIX95 | 800 | 364 | 0.0013405912 | 0.029170041 | 0.22249253 | 0.051267145 | 0.74571688 | 0.50871699 | 0.19980476 |
| S2D-RAW | PREFIX99 | 95 | 76 | 0.0058102519 | 0.070975043 | 0.11088595 | 0.0061299908 | 0.4547909 | 0.65186509 | 0.12207917 |
| S2D-RAW | LE_PREFIX95 | 14525 | 776 | 2.2459506e-05 | 0.0035442876 | 0.94553235 | 0.94873286 | 0.25428312 | 0.18703931 | 0.5163238 |
| S2D-RAW | LE_PREFIX99 | 15230 | 776 | 4.5762796e-05 | 0.004358572 | 0.81106693 | 0.99387001 | 0.5452091 | 0.20004063 | 0.50233481 |
| B0-GAP-RMEAN | PREFIX95 | 800 | 364 | 0.0012884836 | 0.028610427 | 0.23738846 | 0.051267145 | 0.72127419 | 0.42024932 | 0.22909296 |
| B0-GAP-RMEAN | PREFIX99 | 95 | 76 | 0.0057119917 | 0.070418871 | 0.1178532 | 0.0061299908 | 0.43905765 | 0.4791093 | 0.20041648 |
| B0-GAP-RMEAN | LE_PREFIX95 | 14525 | 776 | 2.5002252e-05 | 0.0040417183 | 1.2139899 | 0.94873286 | 0.27872581 | 0.19178743 | 0.5144681 |
| B0-GAP-RMEAN | LE_PREFIX99 | 15230 | 776 | 4.7931896e-05 | 0.0048455017 | 1.0276035 | 0.99387001 | 0.56094235 | 0.20104805 | 0.50196478 |
| B0-GAP-RMED | PREFIX95 | 800 | 364 | 0.0014964089 | 0.032083312 | 0.14481863 | 0.051267145 | 0.75399899 | 0.42576295 | 0.22980557 |
| B0-GAP-RMED | PREFIX99 | 95 | 76 | 0.0062365145 | 0.074182039 | 0.070711476 | 0.0061299908 | 0.42798044 | 0.46255231 | 0.20041648 |
| B0-GAP-RMED | LE_PREFIX95 | 14525 | 776 | 2.4764725e-05 | 0.0035933111 | 0.75530371 | 0.94873286 | 0.24600101 | 0.19120921 | 0.51443397 |
| B0-GAP-RMED | LE_PREFIX99 | 15230 | 776 | 5.4629554e-05 | 0.0045631628 | 0.63876184 | 0.99387001 | 0.57201956 | 0.20108464 | 0.50196478 |
| B0-GAP-RECENT20-LOCKED | PREFIX95 | 800 | 364 | 0.001279891 | 0.02841546 | 0.27379332 | 0.051267145 | 0.60314622 | 0.39931146 | 0.26585076 |
| B0-GAP-RECENT20-LOCKED | PREFIX99 | 95 | 76 | 0.0056113066 | 0.068604619 | 0.14058058 | 0.0061299908 | 0.35983402 | 0.46672082 | 0.24016072 |
| B0-GAP-RECENT20-LOCKED | LE_PREFIX95 | 14525 | 776 | 4.3109068e-05 | 0.0046161301 | 1.2909526 | 0.94873286 | 0.39685378 | 0.1938536 | 0.51286144 |
| B0-GAP-RECENT20-LOCKED | LE_PREFIX99 | 15230 | 776 | 6.6701277e-05 | 0.0054261223 | 1.0952307 | 0.99387001 | 0.64016598 | 0.2010874 | 0.50167148 |
| B0-GAP-RECENT20-LIVE | PREFIX95 | 800 | 364 | 0.001237973 | 0.027315625 | 0.27273463 | 0.051267145 | 0.67621763 | 0.46728565 | 0.24363964 |
| B0-GAP-RECENT20-LIVE | PREFIX99 | 95 | 76 | 0.0055255724 | 0.068912916 | 0.1367185 | 0.0061299908 | 0.42593032 | 0.58541803 | 0.21387747 |
| B0-GAP-RECENT20-LIVE | LE_PREFIX95 | 14525 | 776 | 2.9068144e-05 | 0.0041449394 | 1.2545025 | 0.94873286 | 0.32378237 | 0.18913094 | 0.51389562 |
| B0-GAP-RECENT20-LIVE | LE_PREFIX99 | 15230 | 776 | 4.8968256e-05 | 0.004850332 | 1.0688566 | 0.99387001 | 0.57406968 | 0.20034809 | 0.50184586 |

groups.csv includes annual/month/stock/variable-panel-size/known-calendar-day separation and RAW-score decile aggregates. Deciles are predeclared descriptive weighted RAW-score quantiles per year,shared across arms,never a fitted map. Tail95/99 thresholds are weighted genuine-gap restricted-prefix quantiles;ordinary complements retain original population weights. Loss contributions use unconditional annual masked-panel weights. Event top4 membership and fractional bottom-half false-low are computed in each full valid-stock cross-section before conditioning on true historical events;they are not deployable event probabilities. Equal-year group summaries require a nonempty cohort in all4 years. Missingness/population and repeated dates/stocks are not independent replications.

## Scientific decision and limitations

**Retain this as a provisional gap-specific research candidate, subject to human review; do not promote it automatically.** It improves the declared proper raw-MSE target against both frozen mean-oriented controls and the separately reported live-updated diagnostic. This establishes evidence only against the listed gap controls on this source-selected historical population. Full EWMA/GARCH/HAR and broader traditional benchmarking were not run or implicitly beaten; they require a separately agreed stage. No extra seed, new objective, mask threshold or calibration family is authorized here.

Monthly point MSE improves in34/48 months versus the fixed primary,42/48 versus locked RECENT20 and35/48 versus LIVE. Equal-year per-stock MSE improves for14/20,17/20 and15/20 names respectively. These are overlapping descriptive strata, not independent replications. Equal-year top-four retrieval is.423749 versus.359947 primary and.408306 LIVE; Spearman and pair ordering do not improve uniformly, and bottom-four retrieval is lower than GAP-RMEAN. Raw/calibrated neural rankings are exactly identical, with zero clamp rows: any ranking benefit comes from the network forecasts, not the global scalar. This does not establish signed gap predictability.

Large realized gaps still carry most loss. Prefix95 events have mean predicted/realized ratio.2911 and contribute69.47% of primary raw MSE; prefix99 ratio.1438 and loss share44.61%. Relative to GAP-RMEAN,95/99 tail MSE improves5.99%/4.20%, but the95 ordinary complement worsens4.29%. Relative to RAW, smearing improves95 tail MSE9.64% while worsening its95 complement16.09%. These outcome-selected cohorts do not alone prove E[A_gap|X] miscalibration or predictable jumps. Gap forecast means are not integrated volatility, option-implied values or profitable holdings.

Source missingness remains nonrandom: in OOS, MS is missing15/183 stock-days in2021 and28/202 in2024; MRK is missing15/205 in2022 and19/186 in2023. All20 names remain the universe; the stock/month source and loss tables disclose every name, including historical MA issues. The2-stock27September2022 selector date is excluded, not repaired. Availability is not a future-known trading or neural input. Prefix-locked controls use only matured September-role labels; LIVE includes previously matured calibration/OOS gaps under its fixed bank rule, so it has an explicit information advantage rather than identical frozen history. Baseline coefficients/cutoffs and last20 date spans are in baseline_recipes.csv; no OOS reference selection or fallback occurs.

The supported numerical close/open source, next-session date, action basis, exact masks/weights, gap-scale/decoder/global-smear identities, causal LIVE replay, same-key controls and checkpoint reload checks all pass. Every point MSE also matches an independent mean of per-date valid-stock losses. Final tests/Ruff/static and byte-preservation evidence are in integrity_checks.json/final_checks.json and the standard session handoff. Prefix-role monthly minimum0 is nonbinding metadata, not a relaxed selector/calibration gate; those keep the original five-session minimum. All outputs are finite/nonnegative and all source/version bindings are preserved.

The model uses past48 complete hourly FT16 steps ending15:30; future16:00 last-minute close and next09:30 minute open are labels only. Issuance around15:32 precedes the label's holding interval, but auction/execution prices and actual publication are unverified. No numerical four-hour-versus-gap MSE comparison is meaningful. STOP for researcher review; do not run any further experiment.

Final verification:12 focused tests passed (3.86s),Ruff PASS,and514 project files have zero basic-Pylance errors/warnings (100.936s). Nine frozen numerical/protocol/mask/journal files replay byte-identically. All four exact checkpoint reloads and same-key control checks pass; model code still matches its pre-fit readiness hash. The actual editor Problems refresh remains human-confirmed:select the repository .venv/bin/python,retain Pylance basic,and refresh Problems. Fit lifecycle totals591.14s,114 epochs,17924 optimizer updates,477 clipped batches;peakRSS920240128 bytes,task output about1.83MB,project12.44GB. Ledger166/300;no pending fit,model promotion,commit or push. Standard handoff: reports/codex_sessions/2026-10-28_172337_hf20_s2d_masked_gap.md.

This gap task cannot be compared numerically with original four-hour magnitude MSE to infer a winner. Even genuine gap predictability does not imply signed return alpha,option mispricing or profitable auction execution. The strict20 BLOCKED study remains archived;this is a new masked study. STOP for researcher review.

## Reproduction and preservation

Entry point: `.venv/bin/python -m lstm_data.hf20_s2d_gap --preflight`,then mandatory focused tests/Ruff/basic static gate,and one single-use `--run`;`--report` replays only this task's saved selected forecasts without neural/baseline/calibration fitting. No retry/namespace overwrite. Source and prior journals/control assets are hash-bound in protocol. New checkpoints/forecast Parquets are local ignored artifacts;small JSON/CSV/reports/code/tests are reviewable. Exact commands,tests,resources,current registry and all changed paths are in readiness/final_checks and the standard Codex session handoff. No commit/push.
