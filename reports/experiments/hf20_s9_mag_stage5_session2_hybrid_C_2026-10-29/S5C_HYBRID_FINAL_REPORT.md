# S5-C fixed hybrid CLOCK LSTM

## Executive decision

**TECHNICAL_PASS — mixed magnitude-versus-ranking tradeoff. Retain CLOCK-C3/S2-C as the existing references; do not promote S5-C as a clean hybrid improvement.**

S5C-C3 equal-year raw-A MSE is **0.00010684904630**, worse than CLOCK-C3 **0.00010666594589** by **0.171658%** and S2-C **0.00010654816784** by **0.282387%**. Paired MSE differences are +1.8310041e−7 [1.0439721e−8,3.5865391e−7] and +3.0087845e−7 [7.2902874e−8,5.4597221e−7], respectively. Raw MAE is also higher: 0.00677234848 versus 0.00675709312 (+0.225768%) and 0.00675609600 (+0.240560%). Mean predicted/observed ratio is 1.016376 versus 1.013763 and 1.015221. There is no magnitude-quality win under the fixed calibrated primary arm.

Magnitude-ranking IC rises to **0.332045935** versus CLOCK-C3 **0.330254043**: +0.001791891 [0.000375126,0.003280586]. Pair concordance improves by +0.000732963 [0.000147260,0.001364116]. Against S2-C IC0.331235977, the gain is only +0.000809958 [−0.001127334,0.002687193], and its pair-concordance interval also spans zero. Top-four retrieval declines to **0.427680982**, versus CLOCK-C3 0.429465854 and S2-C 0.429640727; both retrieval-difference intervals span zero. Thus the ranking evidence is metric- and comparator-dependent. CLOCK-relative annual IC directions are positive/negative/positive/negative; annual calibrated MSE directions are worse/better/better/worse.

The raw inverse diagnostic improves MSE by 0.536896% versus CLOCK-RAW (0.00011365677701 versus0.00011427028909). That raw-output advantage does not survive the predeclared own-C3 package comparison; RAW is not substituted after observing outcomes. All three new ordering paths—Mhat, RAW and C3—are identical, with zero clamp-created ties or zero forecasts. The IC change therefore comes from learned score ordering, not the decoder.

Tradeoffs remain visible: intraday/overnight calibrated MSE worsens by 0.442821%/0.096603% versus CLOCK-C3, with MAE also higher in both. Prefix95 ordinary-complement MSE worsens0.621165%; prefix95 tail MSE is nearly unchanged (−0.012268%), prefix99 tail MSE worsens0.038554%. Against S2-C, both ordinary and tail MSE worsen. Prefix95/99 top-four event recall is0.549834/0.672256 versus CLOCK-C3 0.553064/0.675660, while false-low rates improve to0.163506/0.116573 versus0.169008/0.126699. Improved avoidance of low ranks is not the same as improved top-four capture. S5-C's centered-score static fraction77.53% is close to CLOCK-C3's77.15% and S2-C's77.47%; this is not an attribution of predictive accuracy.

These are small, exploratory differences on repeatedly reviewed years. No retrospective acceptable-degradation threshold is invented. Preserve the mixed result, with no lambda/temperature/seed/calibration rescue.

**Technical completion: four of four folds and all four independent C3 calibrations passed.** Exact original 80,260 stock-origin rows / 4,013 origins / 793 sessions; twenty stocks at every origin. Ledger **182 → 186 / 300**, exactly four charged pairs/eight neural phases, one seed42, no retries, new baselines or other models. RAW remains diagnostic; own C3 calibration is the predeclared magnitude candidate. Ranking and magnitude are separate co-primary questions.

## Annual and equal-year primary evidence

| year | arm | raw_MSE | raw_MAE | ratio | IC | top4 |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | S5C-C3 | 8.309191526e-05 | 0.00642987544 | 1.052487313 | 0.3294364541 | 0.3918724671 |
| 2021 | CLOCK-C3 | 8.255461312e-05 | 0.006378167537 | 1.042000452 | 0.326276066 | 0.3971821175 |
| 2021 | S2C-C3 | 8.257578687e-05 | 0.006384710302 | 1.04521638 | 0.3274607114 | 0.3979388298 |
| 2022 | S5C-C3 | 0.0001457445656 | 0.008314339851 | 1.002965903 | 0.3542956386 | 0.4370719955 |
| 2022 | CLOCK-C3 | 0.0001459095063 | 0.00830866763 | 0.9988673768 | 0.3544509105 | 0.4364937642 |
| 2022 | S2C-C3 | 0.0001457649721 | 0.008314501581 | 1.003399629 | 0.3517644971 | 0.4336706349 |
| 2023 | S5C-C3 | 8.599183224e-05 | 0.005978927551 | 0.9799336588 | 0.328670863 | 0.4223644003 |
| 2023 | CLOCK-C3 | 8.617307336e-05 | 0.005998685915 | 0.9854650951 | 0.3238041506 | 0.420960657 |
| 2023 | S2C-C3 | 8.614824508e-05 | 0.005981576476 | 0.9786996905 | 0.326300734 | 0.4226476954 |
| 2024 | S5C-C3 | 0.0001125678721 | 0.006366251066 | 1.033343709 | 0.3157807834 | 0.4594150641 |
| 2024 | CLOCK-C3 | 0.0001120265908 | 0.006342851385 | 1.033007725 | 0.3164850461 | 0.4632268773 |
| 2024 | S2C-C3 | 0.0001117036674 | 0.006343595656 | 1.036524725 | 0.3194179649 | 0.4643057463 |
| EQ | S5C-C3 | 0.0001068490463 | 0.006772348477 | 1.01637554 | 0.3320459348 | 0.4276809817 |
| EQ | CLOCK-C3 | 0.0001066659459 | 0.006757093117 | 1.013762811 | 0.3302540433 | 0.429465854 |
| EQ | S2C-C3 | 0.0001065481678 | 0.006756096004 | 1.015220833 | 0.3312359769 | 0.4296407266 |

Full-panel co-primary differences, S5C-C3 minus each frozen reference (negative MSE favors S5-C; positive IC favors S5-C):

| year | right | metric | delta | percent | low | high |
| --- | --- | --- | --- | --- | --- | --- |
| 2021 | CLOCK-C3 | raw_MSE | 5.373021451e-07 | 0.6508444832 | 1.267428811e-07 | 8.713214723e-07 |
| 2022 | CLOCK-C3 | raw_MSE | -1.649407288e-07 | -0.1130431683 | -2.934519508e-07 | -3.898343867e-08 |
| 2023 | CLOCK-C3 | raw_MSE | -1.81241126e-07 | -0.2103222258 | -4.735256948e-07 | 2.498227707e-08 |
| 2024 | CLOCK-C3 | raw_MSE | 5.41281353e-07 | 0.4831722087 | -3.961529706e-08 | 1.016823665e-06 |
| EQ | CLOCK-C3 | raw_MSE | 1.831004108e-07 | 0.1716577951 | 1.043972068e-08 | 3.586539106e-07 |
| 2021 | CLOCK-C3 | IC | 0.003160388071 | 0.9686239355 | -0.001401419183 | 0.006180313123 |
| 2022 | CLOCK-C3 | IC | -0.0001552718829 | -0.04380631514 | -0.001563722831 | 0.001010620741 |
| 2023 | CLOCK-C3 | IC | 0.004866712325 | 1.502980217 | 0.002499824924 | 0.0078866586 |
| 2024 | CLOCK-C3 | IC | -0.000704262765 | -0.2225263954 | -0.004405401474 | 0.003284714259 |
| EQ | CLOCK-C3 | IC | 0.001791891437 | 0.542579712 | 0.0003751260895 | 0.003280586358 |
| 2021 | S2C-C3 | raw_MSE | 5.161283895e-07 | 0.625035993 | 6.42021814e-08 | 9.333683663e-07 |
| 2022 | S2C-C3 | raw_MSE | -2.040650428e-08 | -0.01399959399 | -3.946298056e-07 | 3.863951461e-07 |
| 2023 | S2C-C3 | raw_MSE | -1.564128484e-07 | -0.1815624315 | -6.148157776e-07 | 1.470163569e-07 |
| 2024 | S2C-C3 | raw_MSE | 8.642047756e-07 | 0.7736583731 | 1.717392273e-07 | 1.535935365e-06 |
| EQ | S2C-C3 | raw_MSE | 3.008784531e-07 | 0.2823872612 | 7.290287427e-08 | 5.459722054e-07 |
| 2021 | S2C-C3 | IC | 0.001975742658 | 0.6033525822 | -0.0028958818 | 0.006291468086 |
| 2022 | S2C-C3 | IC | 0.002531141537 | 0.7195557135 | -0.001054978355 | 0.005841440182 |
| 2023 | S2C-C3 | IC | 0.00237012891 | 0.7263633398 | -0.0001170438849 | 0.005589147283 |
| 2024 | S2C-C3 | IC | -0.003637181566 | -1.138690357 | -0.007127027887 | 0.0002121994063 |
| EQ | S2C-C3 | IC | 0.0008099578848 | 0.2445259396 | -0.001127333595 | 0.00268719303 |

All intervals are descriptive 95% whole-calendar-month blocks, 400 draws/seed22042, year-stratified equal-year aggregation. Entire sessions and their stocks/overlapping origins stay together. These repeatedly inspected 2021–2024 outcomes are exploratory/post-search. Intervals condition on selected/fitted/calibrated networks and omit model-selection and repeated-search uncertainty; no confirmatory p-values or independent-seed claim.

## Full comparator context

Calibrated/unadjusted magnitudes on the same original task:

| arm | raw_MSE | raw_MAE | predicted | observed | bias | ratio | IC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S5C-C3 | 0.0001068490463 | 0.006772348477 | 0.01048215586 | 0.01031327049 | 0.0001688853712 | 1.01637554 | 0.3320459348 |
| S5C-RAW | 0.000113656777 | 0.006486732391 | 0.008164021387 | 0.01031327049 | -0.002149249102 | 0.791603536 | 0.3320459348 |
| CLOCK-C3 | 0.0001066659459 | 0.006757093117 | 0.01045521008 | 0.01031327049 | 0.0001419395949 | 1.013762811 | 0.3302540433 |
| CLOCK-RAW | 0.0001142702891 | 0.006480820201 | 0.008015851344 | 0.01031327049 | -0.002297419146 | 0.7772366052 | 0.3302540433 |
| S2C-C3 | 0.0001065481678 | 0.006756096004 | 0.01047024706 | 0.01031327049 | 0.0001569765724 | 1.015220833 | 0.3312359769 |
| C0 | 0.000114783568 | 0.006497448339 | 0.008032755199 | 0.01031327049 | -0.002280515291 | 0.7788756444 | 0.3246681015 |
| C1a | 0.000108218653 | 0.006815934794 | 0.01050088001 | 0.01031327049 | 0.0001876095219 | 1.018191079 | 0.3246681015 |
| C3 | 0.0001072269421 | 0.00680102945 | 0.01058858438 | 0.01031327049 | 0.0002753138899 | 1.02669511 | 0.3246681015 |
| M1 | 0.0001082663992 | 0.00688398945 | 0.01085576594 | 0.01031327049 | 0.0005424954495 | 1.052601689 | 0.3246681015 |
| B0-VOL | 0.0001115604213 | 0.007012769595 | 0.01060090168 | 0.01031327049 | 0.0002876311933 | 1.027889426 | 0.3041431609 |
| B0-CLOCK | 0.000114669543 | 0.006839084761 | 0.009505439707 | 0.01031327049 | -0.000807830783 | 0.9216707461 | 0.3028002039 |
| B0-RMEAN | 0.0001223644168 | 0.007129612585 | 0.009516580896 | 0.01031327049 | -0.000796689594 | 0.9227510231 | 0.3002382727 |
| B0-RMED | 0.0001380921626 | 0.006949601025 | 0.006474015979 | 0.01031327049 | -0.003839254511 | 0.6277364669 | 0.2961144338 |

Common ranking metrics, including frozen dimensionless rankers:

| arm | IC | historical_IC | pair_concordance | top4 | bottom4 | tie_rate | constant_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S5C-C3 | 0.3320459348 | 0.3320459348 | 0.6201762758 | 0.4276809817 | 0.3035424503 | 0 | 0 |
| S5C-RAW | 0.3320459348 | 0.3320459348 | 0.6201762758 | 0.4276809817 | 0.3035424503 | 0 | 0 |
| CLOCK-C3 | 0.3302540433 | 0.3302540433 | 0.6194433131 | 0.429465854 | 0.3030275632 | 0 | 0 |
| CLOCK-RAW | 0.3302540433 | 0.3302540433 | 0.6194433131 | 0.429465854 | 0.3030275632 | 0 | 0 |
| S2C-C3 | 0.3312359769 | 0.3312359769 | 0.6198189902 | 0.4296407266 | 0.3028851697 | 0 | 0 |
| C0 | 0.3246681015 | 0.3246681015 | 0.6173021171 | 0.4246095608 | 0.2991551849 | 0 | 0 |
| C1a | 0.3246681015 | 0.3246681015 | 0.6173021171 | 0.4246095608 | 0.2991551849 | 0 | 0 |
| C3 | 0.3246681015 | 0.3246681015 | 0.6173021171 | 0.4246095608 | 0.2991551849 | 0 | 0 |
| M1 | 0.3246681015 | 0.3246681015 | 0.6173021171 | 0.4246095608 | 0.2991551849 | 0 | 0 |
| B0-VOL | 0.3041431609 | 0.3041431609 | 0.6094227002 | 0.4098864948 | 0.2961886751 | 0.0002615081141 | 0 |
| B0-CLOCK | 0.3028002039 | 0.3028002039 | 0.6085286495 | 0.3866813807 | 0.305845017 | 0 | 0 |
| B0-RMEAN | 0.3002382727 | 0.3002382727 | 0.6075409545 | 0.3906921517 | 0.305845017 | 0 | 0 |
| B0-RMED | 0.2961144338 | 0.2961144338 | 0.6061252718 | 0.3741662913 | 0.305845017 | 0 | 0 |
| Mhat | 0.3320459348 | 0.3320459348 | 0.6201762758 | 0.4276809817 | 0.3035424503 | 0 | 0 |
| S5A | 0.3094618925 | 0.3094618925 | 0.611288014 | 0.4104630803 | 0.2980071004 | 0 | 0 |
| S5B | 0.329547298 | 0.329547298 | 0.6194788219 | 0.4268532655 | 0.3033884617 | 0 | 0 |
| LINEAR | 0.318192904 | 0.318192904 | 0.6147437918 | 0.4149842272 | 0.2994509635 | 0 | 0 |

S5-A, S5-B and LINEAR remain rank-only scores: raw-A MSE/MAE and magnitude calibration are N/A for them, and they appear only in ranking tables. Their unlike surrogate losses are not used to choose a winner. B0-RMEAN is the saved causal static-stock magnitude prior; no baseline was refitted. S2-D's separate gap task is preserved and excluded from these losses. Frozen C0/C1a/C3/M1 and B0 controls are retained; no full-December historical model substitutes for Design A.

## Conditional losses, tails and score dynamics

| arm | scope | raw_MSE | raw_MAE | ratio | IC | top4 |
| --- | --- | --- | --- | --- | --- | --- |
| S5C-C3 | INTRADAY | 5.131205043e-05 | 0.00495934623 | 1.042489238 | 0.3187732473 | 0.4256151146 |
| S5C-C3 | OVERNIGHT | 0.0001494335489 | 0.008171452562 | 1.003990414 | 0.3432513466 | 0.4298520669 |
| CLOCK-C3 | INTRADAY | 5.108583152e-05 | 0.00494252625 | 1.040390816 | 0.3180463104 | 0.4271751056 |
| CLOCK-C3 | OVERNIGHT | 0.0001492893315 | 0.008157579562 | 1.001112642 | 0.3409911335 | 0.4311866314 |
| S2C-C3 | INTRADAY | 5.109997221e-05 | 0.004948096309 | 1.042930113 | 0.3181102165 | 0.4261096679 |
| S2C-C3 | OVERNIGHT | 0.0001490721701 | 0.008151472278 | 1.002011792 | 0.3424080419 | 0.4314014769 |

Prefix-tail and ordinary-complement magnitude diagnostics:

| arm | group | weight_mass | raw_MSE | raw_MAE | ratio | raw_MSE_loss_share |
| --- | --- | --- | --- | --- | --- | --- |
| S5C-C3 | PREFIX95 | 0.05931860114 | 0.001139645965 | 0.02858498133 | 0.3580031023 | 0.5873598836 |
| S5C-C3 | LE_PREFIX95 | 0.9406813989 | 4.71122501e-05 | 0.00547367061 | 1.236050332 | 0.4126401164 |
| S5C-C3 | PREFIX99 | 0.009373201042 | 0.00394594194 | 0.05824096925 | 0.2324384721 | 0.3321315924 |
| S5C-C3 | LE_PREFIX99 | 0.990626799 | 7.209898201e-05 | 0.006300749115 | 1.073178839 | 0.6678684076 |
| CLOCK-C3 | PREFIX95 | 0.05931860114 | 0.001139785797 | 0.02859071722 | 0.3578697988 | 0.5891801902 |
| CLOCK-C3 | LE_PREFIX95 | 0.9406813989 | 4.682141169e-05 | 0.005455355283 | 1.232713967 | 0.4108198098 |
| CLOCK-C3 | PREFIX99 | 0.009373201042 | 0.003944421224 | 0.05824463448 | 0.2323901679 | 0.332966115 |
| CLOCK-C3 | LE_PREFIX99 | 0.990626799 | 7.188615454e-05 | 0.006284977493 | 1.070417055 | 0.667033885 |
| S2C-C3 | PREFIX95 | 0.05931860114 | 0.001135728151 | 0.02850488814 | 0.3597903497 | 0.5870787812 |
| S2C-C3 | LE_PREFIX95 | 0.9406813989 | 4.701508231e-05 | 0.00546119801 | 1.233956565 | 0.4129212188 |
| S2C-C3 | PREFIX99 | 0.009373201042 | 0.003934708747 | 0.05815365769 | 0.2335891569 | 0.3321695627 |
| S2C-C3 | LE_PREFIX99 | 0.990626799 | 7.189297585e-05 | 0.00628520784 | 1.071866201 | 0.6678304373 |

Tail retrieval:

| arm | level | top4_event_recall | false_low_rank |
| --- | --- | --- | --- |
| S5C-C3 | 95 | 0.549833739 | 0.163505765 |
| S5C-C3 | 99 | 0.6722561204 | 0.1165726656 |
| CLOCK-C3 | 95 | 0.5530637394 | 0.1690081672 |
| CLOCK-C3 | 99 | 0.6756595205 | 0.1266986836 |
| S2C-C3 | 95 | 0.553485907 | 0.1642997115 |
| S2C-C3 | 99 | 0.6668686863 | 0.1277086489 |

Magnitude group metrics renormalize original row weights within the selected group. Raw-MSE contribution is its unconditional weighted contribution; loss shares use the full-panel denominator. Ranking group metrics retain equal eligible origins within each retained session, then equal sessions, and equal years. Do not add conditional MSEs without masses. Prefix95/99 thresholds come from the existing legal September training prefixes, never OOS fitting. Realized-tail underforecasting alone does not prove conditional-mean miscalibration, and event retrieval is not a calibrated probability model.

Shared C0-score deciles in groups.csv use fixed descriptive quantiles of the frozen comparator, identical membership across arms and no outcome-based calibration fit. The same file includes seven slots, each stock/month, and early-close origins. rank_groups.csv and stock_diagnostics.csv separate cross-sectional ranking from individual stock rank errors. Early-close evidence is sparse (14 origins total), not a new selection criterion. tail_retrieval.csv includes group-specific complements; its EQ stock_rows is mean annual count. False-low means forecast average rank <=10.5; top-four and bottom-four use fractional boundary ties (chance20%). No tie jitter or alphabetical advantage.

Persistent versus changing centered scores:

| arm | stock_static_variance | within_stock_temporal_variance | static_fraction |
| --- | --- | --- | --- |
| S5C-C3 | 8.894071291e-06 | 2.515957277e-06 | 0.7752731272 |
| CLOCK-C3 | 8.720628879e-06 | 2.506780708e-06 | 0.771540795 |
| S2C-C3 | 9.067318579e-06 | 2.537231829e-06 | 0.7747191104 |
| S5B | 0.1509291684 | 0.03366234792 | 0.8176957628 |

Static fraction is a descriptive decomposition of forecast-score variance using saved predictions, not the fraction of predictive accuracy caused by stock priors. Units and nonlinear decoding differ across models. No static-vs-dynamic decomposition was fitted as a new predictor or used to retune this model.

## Single approved objective and chronological contract

A=abs(log(genuine240-trading-minute endpoint/origin price)), M=log1p(A/s_phase). One shared own-stock48×16 FT16 H32 LSTM, final-hidden dropout.10, original10 schedule-only CLOCK fields at scalar readout: **6,443 parameters**. No second head, centering, peer input, minute features, stock ID or capacity increase. The unconstrained output remains M. Pair gradients couple stocks only in training; inference inputs are own-stock histories. Common clock readout contributions cancel in pair differences, while magnitude loss supplies clock learning signal.

For each legal initial/refit training role separately, float64 mu=E[M], v=E[(M−mu)^2], tau=sqrt(v), with original stock→origin→session weights. Positive finite v/tau required; no epsilon fallback. Fixed loss is M_MSE/v +0.25*mean_valid_pair_softplus(−sign(Ai−Aj)*(Mi_hat−Mj_hat)/tau)/ln2. Each unordered pair appears once; exact float64 A ties excluded. An all-tied origin contributes zero pair term but retains its magnitude term under the newly approved rule; none occurred. This is an objective/normalization/selector package: division by v changes gradient scale relative to optimizer regularization, so there is no isolated pair-term attribution against an unrun normalized-lambda0 ablation. Lambda.25 is a fixed choice, not equal gradient weighting.

Phase constants and exact final admitted training dates:

| year | phase | first_date | last_date | scale | mu | variance | tau | lambda_fixed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | initial | 2011-04-01 | 2020-06-30 | 0.005797117684 | 0.7807054888 | 0.2896750098 | 0.5382146503 | 0.25 |
| 2021 | restricted | 2011-04-01 | 2020-09-30 | 0.005848759193 | 0.7807308282 | 0.2896340476 | 0.5381765952 | 0.25 |
| 2022 | initial | 2011-04-01 | 2021-04-30 | 0.005935124632 | 0.7802456817 | 0.2880749511 | 0.5367261416 | 0.25 |
| 2022 | restricted | 2011-04-01 | 2021-09-30 | 0.005933406716 | 0.7797094958 | 0.2871196608 | 0.5358354792 | 0.25 |
| 2023 | initial | 2011-04-01 | 2022-05-31 | 0.006072334419 | 0.7795694899 | 0.2869324036 | 0.5356607169 | 0.25 |
| 2023 | restricted | 2011-04-01 | 2022-09-27 | 0.006121673077 | 0.7798391309 | 0.2870093721 | 0.5357325565 | 0.25 |
| 2024 | initial | 2011-04-01 | 2023-05-31 | 0.006173403502 | 0.7789533622 | 0.2855008534 | 0.5343227989 | 0.25 |
| 2024 | restricted | 2011-04-01 | 2023-09-29 | 0.006174447195 | 0.7780788828 | 0.2839588969 | 0.5328779381 | 0.25 |

Eight FT16 and target-scale recipes reproduced exactly against the executed archive. Original saved Design A indices, 48-full-hour first-input embargo, genuine endpoint+2-minute maturity, seven origins and actual early-close crossing categories are unchanged. Initial training ends June2020/April2021/May2022/May2023; selectors follow through September; fresh restricted refits use the saved September limits. Prior Oct–Dec is exclusively out-of-fit calibration and never a selector/normalizer source. See role_counts.csv, clock_dictionary.csv, per-fold phases.json and protocol bindings.

Selector monitor is the fixed hybrid evaluated on earlier selector labels with initial-training v/tau held fixed; first finite nonnegative, then <=.999 qualified incumbent, minimum12 epochs/patience10/max60. No OOS/IC/tail monitor choice. Fresh seed42, empty optimizer September refit for exactly the qualified-selected count; recompute legal refit s/mu/v/tau. Original AdamW lr.001, betas(.9,.999),eps1e−8, matrices decay.01/bias0, clip1, CPUfloat32,16complete-session minibatches and shuffle42+epoch. Online training component traces are session-weighted batch means from changing parameters, not an additional end-of-epoch fixed-model score.

| year | selected_epoch | selector_epochs | raw_minimum_epoch | parameters | seconds |
| --- | --- | --- | --- | --- | --- |
| 2021 | 3 | 13 | 8 | 6443 | 212.7079053 |
| 2022 | 13 | 23 | 13 | 6443 | 545.4737837 |
| 2023 | 20 | 30 | 22 | 6443 | 740.6006726 |
| 2024 | 4 | 14 | 9 | 6443 | 300.531877 |

## Own out-of-fit calibration and ordering checks

Unclamped residual q=exp(log1p(A/s_refit)−Mhat) from the frozen September encoder only. Global/category weighted moments and effective-session rho=n_eff/(n_eff+25) produce own c_star. No trimming, coefficient transfer, extra multiplier, OOS refit or raw-versus-calibrated selection. RAW=s*expm1(max(Mhat,0)); C3=s*max(0,exp(Mhat)*c_star−1).

| year | group | sessions | n_eff | c0 | c_raw | rho | c_star | q_max | top10_share | top1pct_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | INTRADAY | 53 | 49.96986197 | 1.201647829 | 1.118735816 | 0.666532666 | 1.146384264 | 5.009527094 | 0.01999334529 | 0.03820438869 |
| 2021 | OVERNIGHT | 56 | 53.00752899 | 1.201647829 | 1.258357105 | 0.6795181141 | 1.240182809 | 8.447489003 | 0.02193958479 | 0.05575048027 |
| 2022 | INTRADAY | 47 | 42.70758736 | 1.18715119 | 1.102744977 | 0.6307651627 | 1.133910691 | 6.193192242 | 0.02907198259 | 0.04966743019 |
| 2022 | OVERNIGHT | 47 | 44.69680058 | 1.18715119 | 1.257510581 | 0.6413034775 | 1.232272912 | 8.226999658 | 0.0240509775 | 0.05400077738 |
| 2023 | INTRADAY | 46 | 44.08942528 | 1.097455772 | 1.066600067 | 0.6381501236 | 1.0777652 | 7.155978983 | 0.02031352158 | 0.04139881472 |
| 2023 | OVERNIGHT | 47 | 44.98394583 | 1.097455772 | 1.124282838 | 0.6427752151 | 1.114699545 | 4.908721548 | 0.02914488006 | 0.06312853965 |
| 2024 | INTRADAY | 35 | 30.68798675 | 1.145179259 | 1.074840746 | 0.5510701417 | 1.106417805 | 5.03018394 | 0.04000770162 | 0.05318564516 |
| 2024 | OVERNIGHT | 36 | 32.95592049 | 1.145179259 | 1.204213093 | 0.5686376856 | 1.178748122 | 10.17110307 | 0.05693654169 | 0.08313600638 |

Mhat versus decoded ordering:

| year | arm | changed_origins | changed_stock_rows | zero_predictions |
| --- | --- | --- | --- | --- |
| 2021 | S5C-RAW | 0 | 0 | 0 |
| 2021 | S5C-C3 | 0 | 0 | 0 |
| 2022 | S5C-RAW | 0 | 0 | 0 |
| 2022 | S5C-C3 | 0 | 0 | 0 |
| 2023 | S5C-RAW | 0 | 0 | 0 |
| 2023 | S5C-C3 | 0 | 0 | 0 |
| 2024 | S5C-RAW | 0 | 0 | 0 |
| 2024 | S5C-C3 | 0 | 0 | 0 |

Checkpoint reload matches both calibration and OOS forecasts exactly. All outputs are finite/nonnegative after decoding. Coefficients, phase moments, loss traces, score keys and source identity are independently replayed in verification.json. Calibration concentration and F24's smaller independent tail constrain precision; no calendar category changes or event weighting were introduced.

## Integrity, reproduction and stop

Prefit focused mathematics/source/role/phase gates passed before the first start. Tests cover phase/global hierarchy, exact ties, zero all-tied pair term, float32 composite gradients, H32 backprop, clock cancellation versus magnitude signal, phase transforms, C3 residual/decoder identity and rank reducers. Ruff and installed Pylance basic checks pass without ignores or reduced severity. Post-fit checks and actual resource totals appear in verification.json/final_integrity.json and SESSION_HANDOFF.md. Human VSCode Problems refresh remains outstanding, not claimed.

Only174previously authorized adjusted-hourly partitions and saved genuine endpoint/role metadata through2024 were accessed. No minute source,2025market observations/protected2026 paths/values/hashes, network, downloads or data reconstruction. Original nominal-origin targets start before approximateorigin+2min issuance; vendor publication latency is a historical proxy, action/source vintage retrospective, and the fixed20 surviving-stock panel carries selection bias. Neither magnitudes nor ranks imply signed alpha, integrated volatility, option mispricing or executable trading profit.

Predecessor files and frozen protocol/code hashes remain unchanged; only the authorized registry successor points to the new append-only journal. No commit/push/fetch, environment/package change, dashboard edit or old result rewrite. Saved-score --report needs no training; exact commands, private artifact handling and source bindings are in SESSION_HANDOFF.md. No large feature/source or190-pair duplication.

**STOP for researcher review.** No S5-D/E, alternate lambda/tau/seed, calibrator, routing, new classical benchmark, trading/options work,2025research or protected release. Historical classical volatility benchmarks and static-vs-dynamic interpretation remain a separate future authorization.
