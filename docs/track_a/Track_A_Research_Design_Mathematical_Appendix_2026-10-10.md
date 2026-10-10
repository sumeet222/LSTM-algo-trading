# Track A — Mathematical Research-Design Appendix
## Cross-Sectional Equity Alpha with Shared, Market-Conditioned LSTMs

**Research-reference edition:** 10 October 2026  
**Purpose:** A detailed companion to `Track_A_Research_Design_Presentation_Summary_2026-10-10.md`, explaining **what was selected, the mathematics of the selections, and why**. Suitable as a technical research appendix, discussion aid, and presentation reference.  
**Authority:** Approved decisions D1–D12, D13-C01 and D13-C07, as recorded in `Track_A_Consolidated_Implementation_Design_Record_v1.2_2026-10-10.md`; conditional branches are governed by `Track_A_Architecture_Experiment_Roadmap_First_Pass_FROZEN_v1.0.md` and `Shared_Project_Specification.md`. The audit and staged-Codex plans are complementary implementation contracts.  
**Not a performance report:** No fitted Track A forecasting model, predictive accuracy result, or trading result is established by the design conversation or the two supplied Codex data-intake reports. **No inference of profitability is made here.**  
**Documentary discipline:** A formula marked **approved** is a design specification; a formula marked **schematic** illustrates a concept without pretending missing implementation details were approved. Numerical thresholds described as *project choices* are not claimed to be optimal or established in the cited studies. **Conditional design ≠ activated experiment**; **source audit required ≠ source passed**.

> **Central research question.** Does shared recurrence improve four-hour **within-universe equity ranking**, and do observed market state, simple peer information, market-guided gating, or conditional learned cross-stock exchange add enough reproducible predictive value to survive realistic *assumed* transaction costs? We prioritize a small set of interpretable, information-controlled comparisons over a large architecture sweep.

---

## Guide to the research questions

| Comparison | Information added or mechanism changed | What a favorable result would **and would not** establish |
|---|---|---|
| Momentum / ridge → TM0 | Shared nonlinear sequential mapping instead of a simple fixed feature/lag mapping | Potential added value of recurrence **with differing input-density/complexity**, not a mathematically isolated LSTM advantage |
| TM0 → MC0 | Verified USA500 historical states | Incremental *market information*, confounded modestly with larger input dimension |
| MC0 → MC1 | Same market information, explicit endpoint-dependent feature gate | Incremental *architectural bias* of gating; not necessarily economic regime discovery |
| MC1 → MC2 | Same gate parameters, but gate varies at each historical step | Effect of within-window state conditioning; **conditional test** |
| MC0 → E5 | Leave-one-out peer mean and dispersion | Value of simple observable peer information |
| LL0 → LL1 | Frozen directed and lagged peer signals | Out-of-sample incremental directional *association*, **not causal influence** |
| Full-peer ordinary LSTM → SP3 | Learned low-rank exchange of peer representations | Potential usefulness of structured stock mixing beyond rich ordinary peer information; **conditional** |
| TM0 → TM1 or TG0 → TG2 | More temporal readout flexibility **or** shorter-horizon auxiliary supervision | A *targeted* temporal/supervision hypothesis; at most one initial A-E7 branch |
| AD0/FC0/TG0 → one A-E8 mechanism | Recent-label adaptation, factor information or volatility supervision | Conditional supplemental research, normally deferred |
| Development finalists → A-E9 | New, locked chronological confirmation period | A guarded out-of-sample observation, not proof of a universal trading edge |

### Three different things are measured

1. **Supervised forecast fit**, principally TG0 MSE: does a model reproduce the numerical normalized relative returns?
2. **Cross-sectional ordering**, principally Spearman Rank IC: does it put the five stocks in a useful order?
3. **Economic outcome**, principally full-calendar net portfolio P&L for *both* approved policies and every assumed cost scenario: does the ranking survive execution, turnover, financing and risk controls?

A model can improve one without improving the other two. The experiment must never substitute one claim for another.

---

# Part I. Data universe, historical clocks and targets

## 1. D1 — Five-stock formation, history and research population

### Approved universe

The fixed canonical initial ticker order is

\[
\mathcal U_5=(\mathrm{AAPL},\mathrm{JPM},\mathrm{JNJ},\mathrm{WMT},\mathrm{CAT}),\qquad N=5.
\]

These were chosen to form a small prototype spanning **five different sectors**, not a broad diversified sample. The fixed replacement sequence, **only if a documented eligibility test fails**, is `MSFT, BAC, MRK, COST, HON` in corresponding sector order. The formation date is **2020-07-01**.

**Approved admission checks** include trailing 60-session mean daily dollar volume of at least **$50 million** and verification of historical formation-date membership in the relevant USA500 underlying universe *if that notion is defensible for the course source*. The latter remains source-dependent. Retrospective vendor completeness should be at least **98% overall** and **95% in each adequately represented year**. These retrospective coverage criteria describe **research-source usability**, not what an investor could have known at formation.

For a preformation daily dollar-volume series \(DV_{i,d}=P_{i,d}V_{i,d}\), the formation statistic is conceptually

\[
\overline{DV}_{i,60}=\frac1{60}\sum_{d\in\text{60 completed preformation sessions}}DV_{i,d},
\]

with the exact underlying price/volume provenance to be audited. The calculation must not incorporate postformation outcomes when determining the frozen initial candidates.

**Reasoning.** Five names make joint timestamp, feature and ranking checks tractable and keep neural fitting modest. Spreading them across sectors offers heterogeneity for observed common-market and cross-sector information questions, but *removes within-sector peer replication*. That matters when interpreting weak directed peer or factor results. One sector-balanced expansion to **approximately 20 stocks** is **conditional** on demonstrated structural limitations, not permission to seek a favorable stock subset.

### Chronological partitions

| Role | Dates | Allowed supervised fitting history |
|---|---|---|
| Original training | 2020-07-01 to 2023-06-30 | Valid matured observations before fitting cutoff |
| Development WF1 | 2023-07-01 to 2023-12-31 | History through June 2023, correctly purged |
| Development WF2 | 2024-01-01 to 2024-06-30 | Expanded history through December 2023, correctly purged |
| Overall development | 2023-07-01 to 2024-06-30 | Used for architecture comparisons and selection, **not independent confirmation** |
| **Untouched A-E9** | **2024-07-01 to 2025-06-30** | Finalist refits may use permitted history through June 2024 only |

Intervals identify calendar boundaries. Actual examples require qualifying exchange sessions, valid two-origin decision times and feature/label status.

**Why chronological separation?** Financial predictors and market regimes drift; randomly mixing dates into train/test sets can produce implausible estimates of future performance. Model comparisons are allowed to use WF1/WF2 results to select architectures, but that makes those folds *development evidence*. The separate 2024–2025 period must remain unopened for model selection.

### Source-status update, carefully distinguished from design

The **subsequently supplied Codex data-intake report** (not an independently inspected repository) states that the existing implementation downloaded **159,008 Alpaca SIP 30-minute source bars** for five stocks in 60 monthly immutable chunks, constructed an on-demand **09:30-anchored hourly aggregation**, and reported **168 missing regular-session half-hour observations in 15 stock-session combinations**. It reports successful 60 offline tests and does not report a fitted model. It also states that genuine **one-minute stock execution prices**, full corporate-action evidence, point-in-time membership and the actual USA500 publication semantics remain unverified. The course-USA500 timestamp-as-close interpretation is a *provisional researcher assumption*. **These reports update the data-acquisition status; they do not amend D1/D2 formulas or certify A-E0 end-to-end feasibility.**

---

## 2. D2 — Trading-session grid, corporate actions and information availability

### Completed-hour grid

The approved stock model grid contains six **scheduled complete one-hour intervals** on an ordinary full U.S. session:

\[
\begin{aligned}
&09{:}30\!\to10{:}30,\quad10{:}30\!\to11{:}30,\quad11{:}30\!\to12{:}30,\\
&12{:}30\!\to13{:}30,\quad13{:}30\!\to14{:}30,\quad14{:}30\!\to15{:}30
\end{aligned}
\]

in **America/New_York** exchange time. The **15:30–16:00** closing stub is **not** treated as a seventh complete neural-input hour. It can still contribute to explicitly full-session daily statistics and can contain real minute-open execution observations. No overnight synthetic hourly slot and no premarket padding is permitted. Early closes, holidays and daylight-saving boundaries use the exchange calendar.

The reported 30-minute source is suitable for *potentially* constructing the desired hours from two genuine constituents; an hour with a missing constituent is invalid rather than synthetically completed. Approved 30-minute acquisition is a **source-resolution choice**, not a change to the intended **hourly model-input frequency**.

### Price and volume transformations

Stock feature prices are **split-adjusted**, with share volume inversely adjusted for split consistency. Corporate-action-adjusted quantities are useful for stable technical features, but actual portfolio accounting is based on genuine **raw execution-reference prices and economically correct shares, dividends and cash flows**. A stock split should not create fictitious wealth:

\[
Q_{\text{after split}}=kQ_{\text{before}},\qquad
P_{\text{after split}}\approx P_{\text{before}}/k,
\]

so the economic position value \(QP\) should remain consistent aside from genuine market movement. The equality is a **split-accounting intuition**, not a promise that observed prices are exactly unchanged at split time. Dividend treatment must be independently source-audited.

### Causal `available_at`, not just bar timestamps

Every observation needs its genuine or explicitly justified information-availability time. For source observation \(u\), a historical step with cutoff \(s\) can use it only if

\[
\operatorname{periodEnd}(u)\le s,
\qquad \operatorname{availableAt}(u)\le s.
\]

For USA500 the age since the market observation's period end is bounded by **90 minutes**:

\[
0\le s-\operatorname{periodEnd}(u)\le90\text{ minutes}.
\]

An older bar may be used as an explicitly eligible prior observation under the rule; it **cannot be relabeled as a newly completed hourly return**. A provider timestamp is not necessarily a verified publication timestamp. The course USA500 is **an external information source**, not assumed tradable or guaranteed to have meaningful exchange volume. **Do not silently substitute SPY or another index.**

**Reasoning.** An impressive Rank IC produced by unavailable bar values is a timing error, not alpha. Distinguishing observation period end, provider publication, feature cutoff, forecast issuance and trade execution is foundational to the entire project.

---

## 3. D3 and D13-C01 — Decision clock, four-hour target, and separate eligibility notions

### Two decisions per eligible session

The two approved forecast origins occur after the first two complete hourly bars (ending at **10:30** and **11:30** ET). The nominal processing allowance is **2 minutes**, the issuance delay must be at most **5 minutes** relative to the nominal origin, and the entry convention uses the next permissible one-minute opening after the issuance/lag rule. Indicative times are

| Historical feature cutoff | Indicative entry | Planned exit |
|---|---|---|
| 10:30 ET | **10:33 ET** | **14:33 ET** |
| 11:30 ET | **11:33 ET** | **15:33 ET** |

The primary target interval is **240 continuous eligible regular-session trading minutes**, with no ordinary overnight crossing. The time difference must be computed on the eligible exchange clock, not as “four arbitrary rows later.” The second exit is inside the closing stub and requires a genuine one-minute execution reference, not a fabricated complete-hour bar.

**Open shared approval:** the original two-track specification described four **complete hourly advances**, which is not automatically equivalent to 240 continuous minutes. This cross-track timing difference requires explicit collaborator sign-off before the full shared comparison is considered frozen.

### Four-hour raw log return and cross-sectional TG0

For each stock \(i\) in the complete five-stock evaluation cross-section, with genuine minute-reference prices \(P_{i,t}^{entry},P_{i,t}^{exit}>0\), set

\[
\boxed{r_{i,t}^{4h}=\log\frac{P_{i,t}^{exit}}{P_{i,t}^{entry}}.}
\]

Let

\[
\begin{aligned}
\mu_t&=\operatorname{median}_{j\in\mathcal U_5}r_{j,t}^{4h},\\
a_t&=\operatorname{median}_{j\in\mathcal U_5}\big|r_{j,t}^{4h}-\mu_t\big|,
\end{aligned}
\]

where \(a_t\) is the **unscaled** cross-sectional median absolute deviation. The training-fitted floor is

\[
\boxed{\epsilon_{TG0}=\max\left(10^{-4},\;0.1\operatorname{median}_{t\in\mathrm{permitted\ train}}a_t\right).}
\]

The supervised target is

\[
\boxed{y_{i,t}^{TG0}=\frac{r_{i,t}^{4h}-\mu_t}{a_t+\epsilon_{TG0}}.}
\]

Every component of a training label must be genuinely available and its outcome **matured** by the fitting cutoff. Fit the floor on the correct training prefix; purging applies at inner-validation, walk-forward and final-confirmation boundaries. There is **no target clipping**.

**Intuition.** Subtracting the same five-stock median asks *which stocks outperform their contemporaneous cross-section*, rather than whether the whole market rises. Dividing by a robust measure of cross-sectional dispersion reduces variation in target scale across calm and dispersed days. A positive denominator guarantees rank preservation:

\[
\boxed{y_{i,t}^{TG0}>y_{j,t}^{TG0}\iff r_{i,t}^{4h}>r_{j,t}^{4h}.}
\]

But the five-name MAD may be small and unstable; this is why the fixed floor, extreme-target concentration audits and unscaled-return reports are important. A **positive TG0 score is relative, not an absolute-price-direction forecast**.

### Four logically distinct states — C01 (approved clarification)

**This is a critical causal rule**, not an extra model choice:

\[
\begin{aligned}
E_t^{forecast}&=1\quad\text{if the model's permitted input/history and issuance requirements hold},\\
E_t^{entry}&=1\quad\text{if a contemporaneously permissible paired entry can be admitted/executed},\\
E_t^{label}&=1\quad\text{if the eventual full five-name 4h labels can be scored},\\
E_t^{exit}&=1\quad\text{if the intended physical liquidation actually occurred as modeled}.
\end{aligned}
\]

The forecasting-score population requires genuine matured labels:

\[
\boxed{E_t^{forecast}E_t^{label}=1.}
\]

The **portfolio entry decision cannot use** \(E_t^{label}\), because it reflects future outcome data. A trade entered on valid contemporaneous information remains an actual simulated position if the scheduled exit observation is later missing. The approved retry/overnight exception policy then applies. Forecast-score and economic-trade populations need not coincide; their counts and reasons must be reported separately.

**Why this separation?** Retrospectively deleting trades whose exits were missing can condition on future information and favor unrealistically easy-to-execute outcomes. Conversely, learning from labels that never matured would leak future supervision. Keeping the two ledgers separate prevents both errors.

---
# Part II. Feature representation and inexpensive predictive references

## 4. D4 — FT0: sixteen interpretable stock-history channels

**Approved model-ready stock tensor:** at an eligible forecast origin \(t\), each stock has

\[
\boxed{X_{i,t}\in\mathbb R^{48\times16},}\qquad
\boxed{\text{five valid stocks per eligible origin}.}
\]

Forty-eight is a count of **scheduled completed-hour slots**, not a count obtained by skipping bad rows. It spans approximately eight ordinary six-hour observation sessions, while some individual features summarize much older *completed* history. An origin is excluded if any required stock-feature element in its five \(48\times16\) windows is invalid. The stock inputs are not routinely imputed. Historical warm-up data preceding the first fitting date can construct causal values, but cannot be used to fit postformation feature normalizers when outside the authorized fitting period.

The selected ordering is

\[
\boxed{(M1,M2,M3,M4,V1,V2,V3,B1,B2,Q1,Q2,T1,T2,T3,T4,T5).}
\]

### 4.1 Momentum channels M1–M4

Let \(O_{i,s},H_{i,s},L_{i,s},C_{i,s}\) be split-adjusted OHLC for a **valid completed stock hour** \(s\). Define its within-bar log return

\[
R_{i,s}^{OC}=\log\frac{C_{i,s}}{O_{i,s}}.
\]

For the valid eligible scheduled 60-hour history \(W_{60}(s)\), define a trailing **root-mean-square**, *not* centered sample standard deviation,

\[
\sigma_{i,60,s}^{H}=\sqrt{\frac1{|V_{60}(s)|}\sum_{u\in V_{60}(s)}(R_{i,u}^{OC})^2},
\]

where \(V_{60}(s)\subseteq W_{60}(s)\) holds valid observations. Approved validity is **at least 57/60** with **no more than two consecutive misses**; the actual model-ready sample remains subject to stricter 48-step overall validity. Let \(\epsilon_{H,i}\) denote the applicable training-fitted positive RMS floor.

- **M1, latest normalized hourly return:**

  \[
  \boxed{M1_{i,s}^{raw}=\frac{R_{i,s}^{OC}}{\max(\sigma_{i,60,s}^{H},\epsilon_{H,i})}.}
  \]

  *Rationale:* Compare a recent move against the stock's own recent risk scale; raw dollar changes are not comparable across AAPL and CAT.

- **M2, origin-matched historical four-hour response:** Let \(o\in\{10{:}30,11{:}30\}\) label the historical forecast-origin type. Let \(\mathcal H_{20}(i,s,o)\) and \(\mathcal H_{60}(i,s,o)\) be the preceding **20** and **60** structurally matching sessions' four-hour log returns, **already matured as of the historical feature step \(s\)**. The approved statistic has the form

  \[
  \boxed{M2_{i,s,o}^{raw}=\frac{\operatorname{mean}_{q\in\mathcal H_{20}}r_{i,q}^{4h}}{\max\!\left(\sqrt{\operatorname{mean}_{q\in\mathcal H_{60}}(r_{i,q}^{4h})^2},\epsilon_{M2,i}\right)}.}
  \]

  Require **19/20** valid in the mean window and **57/60** in the RMS window, with no more than two consecutive missing historical matches. The M2 denominator is a volatility-style normalization consistent with the approved FT0 floor convention. Its **exact per-channel floor object belongs to the approved training-only floor machinery**, not a new arbitrary numerical constant. The scaler uses canonical `(stock, session, forecast-origin type)` records and an approved **50/50 weight across the two origin types**, not duplicated appearances inside overlapping neural windows.

  *Rationale:* A return that followed a 10:30 decision may have different intraday characteristics from one that followed an 11:30 decision. Matching the observation clock and waiting until historical outcomes have matured avoids accidental label leakage. M2 uses *historically observable past responses* as a feature; it does not use the current decision's future return.

- **M3, recent prior-session momentum:** With \(C_{i,d}\) the closing price of a **completed full daily session**, and \(\sigma_{i,63,d}^{D}\) the approved 63-valid-session daily close-to-close RMS,

  \[
  \boxed{M3_{i,s}^{raw}=\frac{\log(C_{i,d-1}/C_{i,d-6})}{\sqrt5\max(\sigma_{i,63,d-1}^{D},\epsilon_{D,i})}.}
  \]

  *Rationale:* Separates a recently rising or falling stock from its contemporaneous hourly move. Using the **previous** day's completed close keeps the statistic fixed during the current session.

- **M4, older momentum distinct from the immediate trend:**

  \[
  \boxed{M4_{i,s}^{raw}=\frac{\log(C_{i,d-21}/C_{i,d-126})}{\sqrt{105}\max(\sigma_{i,63,d-1}^{D},\epsilon_{D,i})}.}
  \]

  *Rationale:* It measures an older 105-session interval rather than collapsing all medium- and long-horizon momentum into the last few days. The exact offset \(d-21\) to \(d-126\) matters: replacing it with current-to-126-day momentum changes the hypothesis.

Daily variables depend only on prior completed sessions; no current incomplete daily bar is treated as the daily close.

### 4.2 Volatility channels V1–V3

Define hourly RMS \(\sigma_{i,12,s}^{H}\) from **12/12 valid** completed hourly OC returns and \(\sigma_{i,60,s}^{H}\) from **at least 57/60**, as above. Their common positive training-only floor is \(\epsilon_{H,i}\). Then

\[
\begin{aligned}
\boxed{V1_{i,s}^{raw}}&=\log\max(\sigma_{i,12,s}^{H},\epsilon_{H,i}),\\
\boxed{V2_{i,s}^{raw}}&=\log\max(\sigma_{i,60,s}^{H},\epsilon_{H,i}),\\
\boxed{V3_{i,s}^{raw}}&=V1_{i,s}^{raw}-V2_{i,s}^{raw}.
\end{aligned}
\]

*Rationale:* V2 retains the **absolute** recent volatility level, whereas V3 describes whether volatility is elevated relative to its own longer history. Using only a volatility ratio could erase a distinction between calm and highly volatile markets; using only a level misses whether volatility is expanding. Logging compresses the large positive dynamic range. V3 is a deterministic contrast rather than a third independently measured volatility quantity.

### 4.3 Intrabar geometry B1–B2

\[
\boxed{B1_{i,s}^{raw}=\log\frac{H_{i,s}}{L_{i,s}}.}
\]

For a positive-range genuine bar,

\[
\boxed{B2_{i,s}=\frac{2C_{i,s}-H_{i,s}-L_{i,s}}{H_{i,s}-L_{i,s}}\in[-1,1].}
\]

If \(H=L\) for a genuinely valid zero-range bar, set **B2 = 0** and preserve quality metadata. An inconsistent OHLC bar is rejected rather than converted into zero range.

*Rationale:* B1 captures the completed bar's intrahour amplitude; B2 identifies whether it closed near the high or low. Unlike B1, B2 is already naturally bounded and is **not** robust-scaled again.

### 4.4 Relative volume Q1–Q2

Let \(v_{i,s}\) be split-consistent stock share volume. Define a stock-specific pseudocount \(p_{i,H}\) equal to **1% of the median strictly positive valid training hourly volume**. There is an analogous daily pseudocount \(p_{i,D}\) fitted on valid positive daily volumes. Both are fitted only on the applicable training history.

- **Q1:** The approved indicator is a **log same-slot relative volume surprise**, comparing the current completed hour with preceding **20 matching scheduled-slot sessions**; require **19/20** valid. Conceptually it is a log relative-volume statistic using the appropriate stock-specific pseudocount and a matching-slot historical mean. **The original decision record fixes its inputs, matching, pseudocount and log convention but leaves the fully expanded pseudocount placement to an independently hand-tested implementation.** It should not be presented here as a newly approved algebraic expression.
- **Q2:** The approved five-versus-sixty *completed full-session* volume ratio is, schematically,

  \[
  \boxed{Q2_{i,d}^{raw}=\log\frac{\overline v_{i,d-5:d-1}^{\text{daily}}\ [\text{approved }p_{i,D}\text{ handling}]}{\overline v_{i,d-60:d-1}^{\text{daily}}\ [\text{same }p_{i,D}\text{ handling}]}.}
  \]

  Require **5/5** valid recent days, **57/60** valid long days, no run of more than two missing; the daily volume includes the actual 15:30–16:00 stub if present in that session. A bracketed pseudocount placement is deliberately not invented as an exact mathematical identity.

*Rationale:* These features describe *abnormal activity*, not nominal share-volume size, and help distinguish quiet from unusually active trading hours or weeks. Split consistency and identical same-slot comparison are essential; adding source volume from the course index is **not** authorized.

### 4.5 Technical channels T1–T5

- **T1, previous 20-day moving-average distance:** Let \(SMA_{20,d-1}\) be the mean of previous 20 completed daily closes, **at least 19/20 valid**. Then

  \[
  \boxed{T1_{i,s}^{raw}=\log\frac{C_{i,s}}{SMA_{20,i,d-1}}.}
  \]

  The denominator is session-locked; the completed-hour numerator updates as hours complete. *Rationale:* A stationary, normalized trend-distance alternative to raw price level.

- **T2, daily trend-sign fraction:** For the preceding 20 valid daily close-to-close returns,

  \[
  \boxed{T2_{i,s}=\frac{1}{n}\sum_{q\in\text{valid prior 20 days}}\operatorname{sign}(r_{i,q}^{D}),\quad n\ge19.}
  \]

  It lies in \([-1,1]\) and is not separately robust-scaled. *Rationale:* Directional persistence is more scale-invariant than raw cumulative return.

- **T3 and T4, normalized EMA distances:** For the standard causally updated closing-price EMA recursions,

  \[
  \begin{aligned}
  \operatorname{EMA}_{k,s}&=a_k C_{i,s}+(1-a_k)\operatorname{EMA}_{k,s^-},\qquad a_k=\frac2{k+1},\\
  \boxed{T3_{i,s}^{raw}}&=\frac{\operatorname{EMA}_{6,s}-\operatorname{EMA}_{18,s}}{C_{i,s}},\\
  \boxed{T4_{i,s}^{raw}}&=\frac{\operatorname{EMA}_{24,s}-\operatorname{EMA}_{72,s}}{C_{i,s}}.
  \end{aligned}
  \]

  Each EMA starts at the first valid observed price and requires **360 good hourly updates after seeding** before its associated feature is eligible. Bounded missing-bar gaps **skip updates**; the recent 72 scheduled slots require **at least 69/72 valid** and no more than two consecutive misses. The usual EMA smoothing factor above is the standard mathematical definition of the stated EMA spans, not a newly selected hyperparameter. *Rationale:* Fast-vs-slow trend differences, normalized by current price, without adding MACD signal-line/histogram channels.

- **T5, Wilder RSI14:** With observed completed-hour closing-price changes \(\Delta C_s=C_s-C_{s^-}\), set \(g_s=\max(\Delta C_s,0)\), \(\ell_s=\max(-\Delta C_s,0)\). Wilder's smoothed components have the standard recurrence

  \[
  \bar g_s=\frac{13\bar g_{s^-}+g_s}{14},\quad
  \bar\ell_s=\frac{13\bar\ell_{s^-}+\ell_s}{14},\quad
  RSI_s=100\frac{\bar g_s}{\bar g_s+\bar\ell_s}
  \]

  where the last expression needs approved zero-gain/loss edge conventions. The normalized channel is

  \[
  \boxed{T5_{i,s}=\frac{RSI_{14,i,s}-50}{50}\in[-1,1].}
  \]

  Seed using the **first 14 valid consecutive closing-price changes** and require **140 additional valid Wilder updates**. Unlike OC bar returns, successive observed scheduled closing prices can involve a **genuine overnight inter-observation gap**. Missing scheduled bars freeze the state, and the first recovery bar does **not** compute an RSI change across the invalid missing interval. The last 72 scheduled hours require **at least 69 valid** and no more than two consecutive misses. If there are zero observed gains/losses, use the approved 0/50/100 RSI conventions rather than an undefined 0/0. *Rationale:* A bounded oscillator complementary to EMA trends; special recovery rules prevent manufactured momentum after a data outage.

### 4.6 Scaling and denominator safeguards

The following **13** channels are pooled-featurewise robust-scaled:

`M1 M2 M3 M4 V1 V2 V3 B1 Q1 Q2 T1 T3 T4`.

For such a channel \(k\) and unique eligible training observations \(x_{k,u}\), define

\[
\mu_k=\operatorname{median}_{u\in\mathrm{train}}x_{k,u},\qquad
s_k=\operatorname{median}_{u\in\mathrm{train}}|x_{k,u}-\mu_k|,
\]

and

\[
\boxed{z_{k,u}=\frac{x_{k,u}-\mu_k}{s_k}.}
\]

The **MAD is unscaled**, not multiplied by a Gaussian-consistency factor. If it degenerates, use the approved fallback order **IQR/1.349 → audited SD → zero for a genuinely training-constant channel**, with later variation flagged. **B2, T2 and T5** retain their native bounded values. No initial feature clipping is allowed; hypothetical \(\pm3,\pm5,\pm10\) clipping is a *diagnostic only*, including checks for lost cross-sectional distinctions.

For volatility denominators, the selected method fits the **fifth percentile of positive valid training RMS scale observations**, with consistent appropriate hourly/daily pools. Floor values are **fitted quantities**, not universally specified prices or volatilities. If a meaningful floor cannot be fitted from valid positive training scales, the branch is blocked, not assigned a convenient constant.

**Why pooled instead of per-ticker scaling?** A shared LSTM should receive comparably transformed features across the selected stock panel. Per-stock transformations could erase or distort cross-stock differences and add a separate fitting convention. Each unique source feature record is counted once in scaler fitting—not repeatedly for every overlapping 48-step window. M2's two origin types receive equal fitting weight as expressly approved.

### 4.7 Completeness and retention: cost of strictness

The basic origin requirement is

\[
\boxed{\forall i\in\mathcal U_5,\ \forall s\in\{1,\dots,48\},\ \forall k\in\{1,\dots,16\}:\ \operatorname{valid}(X_{i,t}[s,k])=1.}
\]

**Retention guards, approved before fitting:** ≥**90%** joint train and development origin retention; ≥**85%** within each approximately six-month walk-forward fold, origin-time and adequately supported volatility regime; no more than **10 percentage points** difference in retention across volatility regimes; ≥**100** distinct eligible trading sessions in each approximately six-month fold. A guard failure blocks progress or requires an explicit protocol amendment; it does not authorize shortening lookbacks or hidden forward filling.

**Why strictness?** Weak market signals are easy to overstate if a model is silently evaluated only on “easy” fully populated dates. The strict rule limits fabricated histories, and the retention audit quantifies whether those exclusions become an important source of sample selection or regime imbalance.

---

## 5. D13-C07 — Approved inexpensive baselines

These exact baseline choices were **added and approved later in D13-C07**. They were *not* retrospectively attributed to D1–D12. They are inexpensive scientific and economic controls, not additional neural architectures.

### 5.1 Intraday normalized momentum

Rank stocks descending by their **already computed, finalized FT0 M1** score:

\[
\boxed{\widehat s_{i,t}^{mom}=M1_{i,t}.}
\]

The highest receives the proposed long leg and the lowest receives the proposed short leg. It is explicitly a **latest-completed-hour momentum comparator**, not conventional multi-month momentum. There is no supervised fit, no horizon/sign search and no selected reversal strategy.

**Reasoning.** A neural model should beat a cheap, causally available ordering heuristic before we claim its additional training complexity is valuable. The same two trading policies and all costs apply to this baseline.

### 5.2 Pooled, lagged ridge

Let \(x_{i,t}\in\mathbb R^{16}\) be the finalized stock feature vector at a scheduled completed hour. The seven **predeclared completed-hour lags** are

\[
\boxed{\mathcal L=\{0,1,2,5,11,23,47\},}
\]

so the stock-only design vector is

\[
\boxed{z_{i,t}^{ridge}=[x_{i,t};x_{i,t-1};x_{i,t-2};x_{i,t-5};x_{i,t-11};x_{i,t-23};x_{i,t-47}]\in\mathbb R^{112}.}
\]

The market-informed arm adds the same five U1–U5 channels at these seven historical steps: **35 more channels, 147 total**. Within-ridge market/no-market and peer/no-peer comparisons use the same dictionary; adding peer summaries uses the D8 fixed features rather than another ridge lag search.

For session \(d\) and valid origin set \(\mathcal O_d\), fit one shared pooled intercept \(b\) and coefficients \(\beta\) by

\[
\boxed{
\min_{b,\beta}\left\{
\frac1D\sum_{d=1}^{D}\frac1{|\mathcal O_d|}\sum_{o\in\mathcal O_d}\frac15\sum_{i=1}^{5}\left(y_{i,d,o}^{TG0}-b-z_{i,d,o}^{\mathsf T}\beta\right)^2
+\lambda\|\beta\|_2^2
\right\}.}
\]

The intercept is **unpenalized**, all other coefficients are penalized, and no learned stock-ID or sector-ID appears in the primary ridge. The fixed candidate grid is

\[
\boxed{\lambda\in\{10^{-4},10^{-3},10^{-2},10^{-1},1\}.}
\]

Choose \(\lambda\) by minimum **session-weighted inner-validation TG0 MSE** on the **last 63 permitted fitting-calendar sessions**, with maturity/purge and scaler rules. If two candidate penalties tie numerically, prefer the **larger**. Refit preprocessing and ridge on the entire permitted fitting history with the selected penalty. A software solver that penalizes an *unweighted sum of squares* needs a correctly derived conversion to the approved *mean session loss* objective; merely entering the same \(\lambda\) number into an API may be wrong.

**Reasoning and fairness caveat.** Ridge controls for learnability of a fixed nonlinear-feature dictionary through a linear score. It observes the same *reach* of 48 scheduled hours but only **seven snapshots**, whereas TM0 reads all 48. It is a **credible compact lagged control**, not exactly information-identical to the LSTM. If that distinction becomes decisive, a full 48-step flattened ridge is a *new approval*, not secretly included.

### 5.3 Exact-score ties

For *trading only*, exact-score ties use the approved canonical ticker order to select distinct top and bottom stocks reproducibly. Rank IC instead uses **midranks**, the separate zero-scoring convention for constant predictions, and explicit counts. A constant five-stock predictor cannot obtain spurious ranking skill through arbitrary tie-breaking.

### 5.4 Cash, buy-and-hold and randomized economic references

- **Cash:** No position and no stock-trading edge claim; defines a zero-position investment comparison under stated interest convention.
- **Equal-weight five-stock buy-and-hold:** A **long-only, non-risk-matched contextual benchmark**. No routine rebalancing. Attempt initial purchases at the **09:30 ET one-minute opening** on the first evaluated exchange session; if entry prices unavailable, retry subsequent session opens without choosing a favorable day. Attempt final sale at the **last scheduled regular-session one-minute opening** of the segment's final session (ordinarily **15:59 ET**); no invented terminal fill. At all-in execution cost rate \(c\) bps and initial equity \(E_0\), approved per-stock entry notional is

  \[
  \boxed{N_{i,0}=\frac{E_0}{5\left(1+c/10^4\right)}.}
  \]

  This reserves cash for entry costs. Credit verified dividends to cash without reinvesting; preserve split-correct shares and separate execution-cost scenarios.
- **Randomized dollar-neutral pair reference:** Exactly **1,000 reproducible uniform random ticker permutations** on the same causally eligible opportunity calendar; first selected name long, last short, with fixed master random seed **20261010** in a seed namespace separate from neural training. Replay **both** policy A/B and all cost/borrow assumptions. This matches opportunity calendar and nominal sizing, **not necessarily realized exposure**, since cap and veto paths can differ. The random distribution is **descriptive**, not a formal selection-adjusted null.

**Reasoning.** Buy-and-hold asks how a simple equity investment performed, but its positive market beta means it is not a matched-risk test of intraday dollar neutrality. Random long/short evaluates whether a scored ranking does better than arbitrary top/bottom picks under similar *rules*, but does not automatically provide an exact inferential permutation test.

---
# Part III. Training, ranking inference and economic implementation

## 6. D5a–D5d — Why MSE for fitting but Rank IC for scientific evaluation?

### 6.1 Approved hierarchical session-weighted regression objective

Let \(d\) index eligible trading sessions, \(\mathcal O_d\) the set of **one or two valid origins** within session \(d\), and \(i=1,\ldots,5\) the fixed stocks. For model \(f_\theta\), define

\[
\ell_{d,o,i}(\theta)=\big(f_\theta(X_{d,o,i})-y_{d,o,i}^{TG0}\big)^2.
\]

The approved objective is

\[
\boxed{
\mathcal L_{TG0}(\theta)=\frac1D\sum_{d=1}^{D}\underbrace{\frac1{|\mathcal O_d|}\sum_{o\in\mathcal O_d}\underbrace{\frac15\sum_{i=1}^{5}\ell_{d,o,i}(\theta)}_{\text{equal stocks per origin}}}_{\text{equal origins within session}}.
}
\]

The outer average gives each **eligible session equal weight**, not each stock-origin record equal global weight. For example, a two-origin session with origin losses \(2,6\) has session loss \(4\); a one-origin session with loss \(10\) has session loss \(10\). Their correct equal-session mean is **7**, not the origin-row average \(6\).

**Why MSE?** It is an inexpensive differentiable regression objective, aligned with the continuous TG0 score. A later hybrid MSE-plus-pairwise objective was discussed as a *separately approved conditional rescue for unreliable ranking*, not part of the initial training specification. **Do not silently introduce pairwise loss, Huber loss or target winsorization.**

**Extremes remain:** the design explicitly includes all genuinely valid large squared errors. A single extreme target contributes gradient proportional to \(2(\widehat y-y)\), so we monitor the fractions of total session loss concentrated in the highest **1%, 5% and 10%** of days, as well as low-MAD floor activity. Gradient clipping is an optimizer safeguard; it does not remove these observations from the statistical objective.

### 6.2 Spearman Rank IC, ties and five-stock discreteness

At each fully valid origin, define the **cross-sectional Spearman rank correlation**

\[
\boxed{IC_{d,o}=\rho_S\big((\widehat y_{1,d,o},\ldots,\widehat y_{5,d,o}),\;(y_{1,d,o}^{TG0},\ldots,y_{5,d,o}^{TG0})\big).}
\]

For *no ties*, this is equivalently

\[
\rho_S=1-\frac{6\sum_{i=1}^{5}d_i^2}{5(5^2-1)},
\]

where \(d_i\) is the difference between predicted and realized ranks. With ties, compute the **Pearson correlation of midranks**, not the no-tie shortcut.

The primary aggregate first averages valid origins **within** an exchange session, then sessions:

\[
\boxed{IC_d=\frac1{|\mathcal O_d|}\sum_{o\in\mathcal O_d}IC_{d,o},\qquad \overline{IC}=\frac1D\sum_d IC_d.}
\]

The special cases are deliberately unusual and **must be documented**:

- Predicted values all equal but realized returns are not: mathematically Spearman is undefined; assign the **project-defined score 0**, flag this origin, and **also** report the mathematically defined-only IC mean and constant-prediction frequency.
- Realized five-stock outcomes all equal: omit that origin from Rank IC **but not from supervised MSE**, and count it separately.
- Partial ties: use midranks; never add random jitter to make a score defined.

**Why Rank IC?** TG0 removes a common cross-sectional shift, and the trading rule only needs to identify a top and a bottom stock. Numerically accurate TG0 forecasts are desirable but not sufficient if the ordering is poor. With just five stocks, per-origin Rank IC is discrete and volatile, so no individual high correlation should be treated as reliable evidence by itself. Secondary metrics are pairwise concordance, top/bottom selection accuracy and target MSE.

### 6.3 Dependent uncertainty and promotion

For two models \(A,B\) evaluated on identical trading sessions and origins, form paired daily differences

\[
\boxed{\Delta_d=IC_{B,d}-IC_{A,d},\qquad\widehat\Delta=\frac1D\sum_{d=1}^{D}\Delta_d.}
\]

The approved primary uncertainty estimate is a **paired moving-block bootstrap on complete, genuinely consecutive trading-session blocks**, with:

| Choice | Approved value and reason |
|---|---|
| Resampling unit | Entire sessions containing all five names and eligible origins; preserve cross-stock/common-market and within-day overlap |
| Primary block length | **5 consecutive sessions**, to retain short-range dependence |
| Sensitivity | **10 and 20 sessions**, to disclose block-length sensitivity |
| Resamples | **10,000** |
| Interval | **95% percentile interval** |
| Cross-check | HAC/Newey–West with Bartlett lag **5** and lag **10** sensitivity |
| Reporting | WF1 and WF2 separately; descriptive seed variability, no independence fiction |

A conceptual HAC variance estimator for daily differences is

\[
\widehat{\mathrm{Var}}(\overline\Delta)=\frac1D\left(\widehat\gamma_0+2\sum_{k=1}^{L}\left(1-\frac{k}{L+1}\right)\widehat\gamma_k\right),
\]

where \(\widehat\gamma_k\) are sample lag-\(k\) autocovariances of the paired daily differences and \(L\) is the declared HAC lag. This is an **explanatory standard formula**; the exact implementation must be tested and reported with its convention.

**Why block the days?** The five stock outcomes share shocks; two daily forecasts have overlapping four-hour future intervals; neighboring trading days can have persistent volatility and predictor conditions. Resampling stock rows or origins as if independent would exaggerate effective sample size. Bootstrap/HAC results remain conditional on weak-dependence assumptions and the selected models; they are **not automatically adjusted for having searched many architectures**.

The approved promotion logic considers primary paired Rank IC, consistency across folds/seeds, MSE, economic costs and parameter/runtime complexity. If an increase is small relative to a defensible paired standard error, apply the **one-SE simplicity preference**. Classify valid results as promoted/not promoted/inconclusive; never require a complex winner. A single positive development Sharpe is not an automatic promotion criterion.

---

## 7. D5e — Turning rankings into a real physical-portfolio simulation

### 7.1 Two separate portfolio policies on every model

At an otherwise admissible origin \(t\), the forecast scores determine

\[
\boxed{i_t^+=\arg\max_i\widehat y_{i,t}^{TG0},\qquad i_t^-=\arg\min_i\widehat y_{i,t}^{TG0}.}
\]

With exact ties, the predeclared canonical stock-order tie rule fixes distinct selections reproducibly. **No absolute-direction classifier, head or filter** is allowed in the first pass. Sign of TG0 is not sign of the stock's absolute expected return.

- **Policy A (fixed sleeves):** Try a new equal-notional top-long/bottom-short *virtual sleeve* at each eligible origin. A later ranking does not intentionally close an existing sleeve early; each accepted sleeve has its own intended **240-minute** expiration.
- **Policy B (conflict veto):** At a new origin, if either proposed leg would require an **opposite stock position to any still-active accepted sleeve instruction**, veto **the entire new long/short pair** and leave prior sleeves to expire normally. Otherwise enter like A. This is not a tuned net-signal threshold or a separately trained model.

**Why compare both?** Repeated rankings may reverse within one hour; with a four-hour intended hold, overlapping sleeves can create high churn. Policy B tests whether a predeclared veto decreases transaction costs and improves **net** outcomes; it could also reject profitable opportunities. Thus both policies, with actual costs, are mandatory for momentum, ridge and every neural architecture. Literature on costly dynamic trading and no-trade regions motivates the question (Gârleanu–Pedersen; Novy-Marx–Velikov), but does not establish that this specific veto is optimal.

### 7.2 Virtual sleeves versus actual external executions

If \(q_{i,a}\) is the signed shares intended by active virtual sleeve \(a\), the physical aggregate target is

\[
\boxed{Q_{i,\tau}^{target}=\sum_{a\in\mathrm{active}(\tau)}q_{i,a},\qquad \Delta Q_{i,\tau}^{external}=Q_{i,\tau}^{target}-Q_{i,\tau^-}^{physical}.}
\]

**Costs are charged on actual external stock orders**, not on each virtual sleeve separately. An existing short sleeve and later long sleeve in the same stock can offset in the physical account, yet offsets at *different times* may still incur external orders and costs. Preserve the virtual-sleeve ledger for attribution and a separate physical position/cash ledger for real net NAV.

### 7.3 Approved sleeve capital and admission

**Superseding the earlier 25%/25% choice**, each accepted sleeve is initially

\[
\boxed{w_{i,a}=\begin{cases}+0.2475,&i=i_a^+,\\-0.2475,&i=i_a^-,\\0,&\text{otherwise},\end{cases}}
\]

using the portfolio equity observed just before that sleeve's entry and the chosen genuine reference minute prices. Thus each sleeve has **49.5% nominal gross** and two nonoffsetting sleeves initially target **99% gross**, leaving a 1-percentage-point buffer under the normal new-entry cap. The buffer is a project-specific engineering choice; it reduces mechanical rejections caused by immediate transaction costs but does not guarantee every second sleeve fits after price drift.

The physical gross exposure is

\[
\boxed{G_\tau=\frac{\sum_i|Q_{i,\tau}|P_{i,\tau}}{E_\tau},}
\]

where \(E_\tau\) is correctly marked equity after accounting for cash, long assets, short liabilities and applicable charges. A complete candidate pair enters only if its **proposed post-cost, netted** gross exposure is \(\le1.00\); otherwise **reject the entire sleeve**, no partial fill to use residual capacity and no resizing older sleeves solely to make room.

**Why all-or-nothing?** It avoids a hidden capital-allocation optimizer, tiny residual-capacity trades and apples-to-oranges accepted sleeve sizes. The cost is potential loss of opportunities after small admissibility changes. All rejections must be attributed by origin and mechanism. Normal passive drift above 100% between scheduled events is permitted; routine weights are not continuously rebalanced.

### 7.4 Emergency exposure and session stop

The approved emergency trigger is

\[
\boxed{G_\tau>1.10}\quad\text{(strictly greater than 110%, not equal).}
\]

Upon a causally *observed* breach:

1. Cancel or prohibit further new entries for the rest of that trading session.
2. Target \(Q_i^{target}=0\) for every physical stock holding, executing at the **next genuinely permissible one-minute opportunity**, not a retrospectively favorable trigger price.
3. Charge actual resulting execution costs; retain any unfilled exposure until a real simulated fill becomes available.
4. Terminate associated virtual sleeves when liquidation really completes; retain their original expiry metadata.
5. Resume next eligible session only subject to resolution of outstanding holdings and the normal entry checks.

**Why 110% instead of a continuously hard 100% limit?** The selected combination limits uncontrolled leverage while avoiding many small corrective trades as positions mark to market. **110% is not a finance-literature optimum**, and a one-minute dataset cannot show every possible intra-minute breach or guarantee filling at exactly the threshold.

### 7.5 Execution friction and physical borrow charges

At execution event \(\tau\), let \(P_{i,\tau}^{ref}\) be the permitted **one-minute opening-price reference** and \(\Delta Q_{i,\tau}^{filled}\) actual simulated *external* filled shares. The approved combined spread/commission/slippage allowance is

\[
\boxed{TC_\tau(c)=\frac{c}{10^4}\sum_i P_{i,\tau}^{ref}|\Delta Q_{i,\tau}^{filled}|,\qquad c\in\{0,2,5,10\}\text{ bps}.}
\]

**5 bps per side is the primary headline assumption**, 2 and 10 bps are sensitivities, and 0 bps is the gross diagnostic. Charge the combined allowance once; do not additionally move fill prices adversely by an identical spread/slippage amount and double count. These are modeled, *not measured broker fill costs*.

The five prototype names are **assumed borrowable/easy-to-borrow for the research simulation**, not demonstrated historically borrowable. The principal physical stock-borrow fee is **0% annualized**, with **0.5% and 3%** sensitivity. The approved conservative daily maximum-notional convention is

\[
\boxed{N_{i,d}^{short}=\max_{\tau\in d}\big[\max(-Q_{i,\tau},0)P_{i,\tau}\big],\qquad BorrowCost_d(b)=\frac{b}{360}\sum_iN_{i,d}^{short},\quad b\in\{0,0.005,0.03\}.}
\]

The maximum is over the **net physical short**, not virtual sleeves. No short-sale proceeds interest credit is assigned. Exceptional unintended overnight financing remains assumption-sensitive and must not be presented as historically verified if necessary source terms are unavailable.

A schematic per-day P&L decomposition is

\[
\boxed{\Pi_d^{net}=\Pi_d^{gross}-TC_d-BorrowCost_d-OtherFinancing_d.}
\]

This P&L identity is only meaningful after correct marking of shares, cash, dividends and outstanding orders. It is not a method for inventing a realized sale when no execution price exists.

**Important path dependence:** A different cost changes equity; equity changes capital admission and possibly subsequent trades. Consequently, each cost-policy combination needs a consistent **portfolio replay** on immutable predictions. It is not always correct to subtract alternative basis points from one fixed list of trades. Break-even cost \(c^*\), where \(\Pi(c^*)=0\), must likewise be evaluated as a path-dependent simulation when well-defined; uniqueness/monotonicity is not automatic.

### 7.6 Failed orders, delayed exits and exceptional overnight positions

The approved research-grade simulator separates the **desire to trade** from **actual modeled fills**:

- Intend a paired entry only if both legs meet contemporaneous execution conditions. If one leg nevertheless fills and the other fails, retain and causally flatten the real partial exposure; never delete that fill in hindsight.
- A missing scheduled exit leaves the physical position **open**. Suspend new entries while required liquidation is unresolved; continue risk monitoring and other closing orders.
- Retry at **each next permissible one-minute regular-session opportunity**. No modeled proportional cost for an unfilled retry; charge only on executed shares.
- If regular trading closes, carry the outstanding exposure and resume at the **next permissible regular-session minute**. This is an exceptional unintended overnight holding, not a forecast signal.
- A dataset-end or source failure without defensible terminal valuation/liquidation produces an **incomplete or assumption-dependent portfolio path**, not a fabricated final realized return.

**Why preserve these inconvenient paths?** Retrospectively dropping hard-to-exit trades would bias economic evaluation. For a course/CV project we do not need exchange queue simulation or production brokerage software, but we do need truthful historical-price proxies and accounting.

### 7.7 What is reported for *both* policies and *all* models

Full-calendar marked equity including no-trade days; gross/net daily and cumulative returns; drawdown; descriptive net Sharpe; net annualized growth when well-defined; turnover; trading/cost drag; separated borrowing and other charges; long/short leg contributions; actual holding-duration distribution; intraday cross-ranking churn; veto and cap rejection reasons; emergency trigger/exit events; occupancy, gross/net exposure and concentration; exceptional missing fills; hypothetical break-even bps if coherent. **All completed and unpromoted models** report every available economic scenario; a negative result is not omitted.

### 7.8 Ex-post absolute-direction report, not a strategy

Only lightweight description is authorized. For selected pair \((i_t^+,i_t^-)\), after its genuine four-hour outcomes mature, one example statistic is

\[
\boxed{D_t=\mathbf1\{r_{i_t^+,t}^{4h}>0\ \text{and}\ r_{i_t^-,t}^{4h}<0\}.}
\]

Report the fractions of realized positive long legs, negative short legs, both together, and positive realized pairs/trades. **No absolute-return prediction head, no new classifier and no direction-based entry veto** in Track A v1. Direction outcomes must not affect model selection or earlier orders.

---

## 8. D6 — One shared standard LSTM and the frozen training protocol

### 8.1 Why a shared recurrent predictor?

An ordinary recurrent model evolves its hidden state from past observations. An LSTM adds a long-lived cell state and learned gates. In standard notation, with input \(x_s\), previous hidden \(h_{s-1}\), cell \(c_{s-1}\), logistic sigmoid \(\sigma\), and elementwise multiplication \(\odot\), the recurrent equations are

\[
\begin{aligned}
i_s&=\sigma(W_i x_s+U_i h_{s-1}+b_i),\\
f_s&=\sigma(W_f x_s+U_f h_{s-1}+b_f),\\
g_s&=\tanh(W_g x_s+U_g h_{s-1}+b_g),\\
o_s&=\sigma(W_o x_s+U_o h_{s-1}+b_o),\\
c_s&=f_s\odot c_{s-1}+i_s\odot g_s,\\
h_s&=o_s\odot\tanh(c_s).
\end{aligned}
\]

The forget and input gates offer a learned way to retain or overwrite recent historical information; the output gate regulates the exposed representation. The equations explain **architectural capacity**, not proof that market data contain a learnable forecasting edge.

The same parameters \(\theta\) encode each of the five stocks independently in the **SP0 control**:

\[
\boxed{h_{i,t,48}=F_\theta(X_{i,t}),\qquad \widehat y_{i,t}=w^\top\operatorname{Dropout}_{0.10}(h_{i,t,48})+b.}
\]

One shared model pools learning across heterogeneous stocks and avoids fitting five high-variance ticker-specific networks. The cost is an assumption of some transferable stock-predictive structure; conditional spatial models test whether peers add more.

### 8.2 D6a–D6c: compact architecture, reset state and dropout

**Approved reference:** **one** standard LSTM recurrent layer, hidden width \(h=32\), input dimension \(d=16\), sequence length **48**, **zero** initial hidden/cell states **for every independent sample**, no state persistence across stocks, windows, minibatches, days or splits. The same final linear head is shared across stocks.

For a standard PyTorch-style one-layer LSTM with two gate-bias vectors and scalar head, the parameter count is

\[
\boxed{N(d,h)=4h(d+h+2)+(h+1).}
\]

At \(d=16,h=32\):

\[
\boxed{N(16,32)=4(32)(16+32+2)+33=6{,}433.}
\]

For an input dimension \(d=21\) in MC0, the same formula gives **7,073**.

**Why one layer, 32?** Fischer–Krauss (2018) is a relevant precedent for a modest shared cross-sectional equity LSTM; other studies show that deeper networks can overfit financial data or need different training. None establishes 32 as universally optimal. The experiment budget is better spent comparing *information mechanisms* than sweeping depths and widths. A targeted capacity rescue can be considered only through the bounded protocol.

Zero reset does **not** eliminate memory *inside* the 48 steps. It makes each forecast reproducible from its explicit historical window and prevents hidden state from depending on shuffled minibatch order. Several FT0 channels summarize older history beyond those 48 input steps.

During training, apply **0.10 inverted dropout to the final hidden representation**, not recurrent/input dropout; disable it in validation/inference. PyTorch's built-in `nn.LSTM(dropout=0.1)` does not provide this final-output dropout for a one-layer model, so it must be an explicit module. This is modest regularization, not a validated optimal dropout rate.

### 8.3 D6d–D6e: AdamW and global gradient clipping

The fixed optimizer is **AdamW**, initial/constant learning rate \(\eta=10^{-3}\), decoupled weight decay \(\lambda=0.01\) on applicable weight matrices, **zero decay on biases and normalization parameters**, and standard moments \(\beta_1=0.9,\beta_2=0.999,\epsilon=10^{-8}\); no scheduler, warmup or AMSGrad.

The familiar update for decayed parameters is schematically

\[
\boxed{\theta_{k+1}=(1-\eta\lambda)\theta_k-\eta\frac{\widehat m_k}{\sqrt{\widehat v_k}+\epsilon}.}
\]

AdamW separates decay from Adam's adaptive gradient normalization (Loshchilov–Hutter, ICLR 2019). The chosen numerical defaults are engineering choices, **not finance-optimal values**.

Let \(g_k=\nabla_\theta \mathcal L_k\) be the gradient of the **complete effective batch objective**. Approved global L2 clipping is

\[
\boxed{\widetilde g_k=g_k\min\left(1,\frac1{\|g_k\|_2}\right),\qquad \|\widetilde g_k\|_2\le1,}
\]

with a numerical zero-denominator safeguard. Clip **once after full backward/accumulation (and AMP unscale if used), before AdamW**, across every trainable tensor, including parameters excluded from weight decay. Never silently zero nonfinite gradients. Record preclip quantiles, max, clipping fraction and multiplier; sustained clipping on **>50% of steps** is a **warning**, not an automatic threshold change.

**Why global norm?** Scaling all components by one factor preserves gradient direction, unlike componentwise clipping. Pascanu–Mikolov–Bengio (ICML 2013) motivates it for recurrent exploding gradients. It does not establish that a cap of 1.0 is optimal, nor guarantee a bound on the final AdamW parameter-update size.

**Bounded rescue only:** a lower learning rate \(3\times10^{-4}\) was predeclared if a genuine optimization pathology remains after code/data checks. It is **not** a routine candidate chosen after weak net P&L; any rescue consumes the declared budget.

### 8.4 D6f: session-grouped minibatches

The unit of minibatch randomization is a **complete exchange trading session**, not an individual stock row. Sample **16 sessions** per target batch, each eligible session once per epoch without replacement, seed-shuffle session IDs, preserve all five stocks and eligible 1–2 origins. Keep the chronological order of 48 steps *inside* every stock sample. Balance remaining batch sizes to avoid dropping sessions.

For batch \(\mathcal B\) of \(B\) sessions,

\[
\boxed{\mathcal L_{\mathcal B}=\frac1B\sum_{d\in\mathcal B}\frac1{|\mathcal O_d|}\sum_{o\in\mathcal O_d}\frac15\sum_i(\widehat y_{d,o,i}-y_{d,o,i})^2.}
\]

At full eligibility, **16 sessions × 2 origins × 5 stocks = 160 stock windows** per minibatch. Grouping preserves the approved loss weighting and prepares a common interface for later five-stock interaction modules. It **does not** make the sessions statistically independent; inference still uses time blocks. Batch size 16 is a fixed economical default, not a literature-proven optimum.

### 8.5 D6g: early stopping without using the evaluated fold to choose epochs

Within each independent fitting cutoff, reserve the **last 63 exchange-calendar sessions of the permitted historical fitting period** as **inner validation**. Require at least **50 eligible distinct sessions**, with at least **25 valid origin observations of each forecast-origin type**; otherwise block instead of moving the boundary for a better result. Fit normalizers on the earlier inner-training prefix, purge unmatured/cross-boundary labels, and evaluate the exact session-weighted validation TG0 MSE every completed epoch.

The **calibration pass** stops with:

- Maximum **60** epochs.
- Earliest permitted stop **after 12** completed epochs.
- **10** consecutive epochs without a qualifying improvement.
- Qualifying improvement \(V_e<0.999V_{best}\) (**strictly more than 0.1% relative decrease**).
- Save the **best qualifying checkpoint** (earliest exact tie), while separately recording the absolute raw minimum and why it may differ.

If the selected calibration epoch is \(e^*\), the **second pass** initializes a **fresh model and optimizer**, refits all preprocessing on the full permitted fitting history, and trains for **exactly \(e^*\) epochs**, with no additional outer-validation checkpoint choice:

\[
\boxed{\widehat f^{\mathrm{refit}}_{e^*}=\operatorname{TrainFresh}\big(\text{permitted full history};\ e^*\text{ epochs}\big).}
\]

**Why two passes?** Checkpoint selection against the *same* later dates used for evaluating a model would invite selection bias; using an earlier inner block protects WF1/WF2 and A-E9. Refit uses the originally held-out inner-validation dates for final fitting without opening the outer period. The selected epoch count is reused, **not the calibration weights**. The refit may have more updates per epoch because it has more sessions; the run log must record optimizer-step counts. Goodfellow–Bengio–Courville's early-stopping/retraining discussion motivates this procedure, but the exact 63/60/10/12 values remain project defaults.

### 8.6 D6h: controlled seed and compute budget

\[
\boxed{S_{screen}=\{42\},\quad S_{followup}=\{42,123\}\text{ (conditional)},\quad S_{final}=\{42,123,2026\}.}
\]

A complete **training pair** means one inner calibration fit **plus** one fresh full-history refit at a unique architecture/fitting cutoff/seed/configuration. The global initial ceiling is **40 such pairs** (up to 80 fit passes), with **one primary justified full-fit rescue per mechanism**; an initial **24 cumulative neural-fitting hours** is a preliminary envelope subject to the actual hardware benchmark. Individual Codex training packages should target **≤4 hours of fitting** (about 4.5 hours hard-stop allowance) and never launch a run that cannot finish under the approved constraints without escalation.

**Reasoning.** One seed is enough to smoke-test a mechanism, not to infer superiority; three finalist seeds describe initialization sensitivity but create **no new independent market histories**. Matching seed IDs and fitting cutoffs makes comparisons more auditable. Do not retain only the best seed, automatically train every conditional family, or exceed resource limits without a versioned decision. Record all attempted, failed, blocked and unused branches.

---
# Part IV. Market information and stock-to-stock mechanisms

## 9. D7 — USA500 features, additive information versus gating, and causal regimes

### 9.1 Economic hypothesis and the additive-cancellation argument

Financial predictor importance can depend on market conditions: for example, a momentum feature may behave differently during high-volatility decline than during a quiet uptrend. **MASTER** (AAAI 2024) motivates market-guided feature weighting; **Gu–Kelly–Xiu** (RFS 2020) motivates nonlinear predictor interactions; **Daniel–Moskowitz** and **Moreira–Muir** motivate studying market trend and absolute volatility. None establishes that a 5-feature gate will improve our four-hour net trading returns.

There is a simple mathematical reason to test *interactions* rather than only a shared additive market term. If each stock's predicted score is

\[
\widehat y_{i,t}=f(x_{i,t})+g(m_t)
\]

with \(m_t\) identical across stocks at origin \(t\), then

\[
\boxed{\widehat y_{i,t}-\widehat y_{j,t}=f(x_{i,t})-f(x_{j,t}),}
\]

and the common additive market term **cannot alter that cross-sectional ranking**. A nonlinear model of \([x_i;m]\) can learn interactions, and a feature gate builds such interactions into the architecture explicitly:

\[
\widehat y_{i,t}=f\big(\alpha(m_t)\odot x_{i,t},\,m_t\big).
\]

Our three-step comparison therefore asks different questions: stock-only → direct market information → explicit conditioning. This does *not* prove a gate is necessary; the ordinary MC0 LSTM could already learn useful interactions.

### 9.2 D7a–D7b: five fixed continuous USA500 channels

Let \(O_s^M,C_s^M\) be compatible, **verified** USA500 completed-hour price fields, and \(R_s^M=\log(C_s^M/O_s^M)\). For \(k\in\{12,60\}\), define the RMS \(\sigma_{k,s}^M\) of valid past completed-hour OC returns, with common *market* hourly positive-floor \(\epsilon_H^M\). Let \(C_d^M\) be the verified completed session close and \(\sigma_{63,d}^{M,D}\) the trailing daily close-to-close RMS with market daily floor \(\epsilon_D^M\).

The **approved** features at each historical input step \(s\) in exchange session \(d\) are

\[
\begin{aligned}
\boxed{U1_s}&=\frac{R_s^M}{\max(\sigma_{60,s}^M,\epsilon_H^M)},\\
\boxed{U2_s}&=\log\max(\sigma_{60,s}^M,\epsilon_H^M),\\
\boxed{U3_s}&=\log\frac{\max(\sigma_{12,s}^M,\epsilon_H^M)}{\max(\sigma_{60,s}^M,\epsilon_H^M)},\\
\boxed{U4_s}&=\frac{\log(C_{d-1}^M/C_{d-6}^M)}{\sqrt5\max(\sigma_{63,d-1}^{M,D},\epsilon_D^M)},\\
\boxed{U5_s}&=\frac{\log(C_{d-1}^M/C_{d-21}^M)}{\sqrt{20}\max(\sigma_{63,d-1}^{M,D},\epsilon_D^M)}.
\end{aligned}
\]

The market-state vector is \(m_s=(U1_s,\ldots,U5_s)\in\mathbb R^5\), and a market-conditioned model receives a **48×5** market history.

| Channel | Economic intuition | Why not replace it with another channel? |
|---|---|---|
| U1 | Current market move relative to its recent volatility | Immediate directional state, unlike only using daily trend |
| U2 | **Absolute** logarithmic 60-hour volatility level | Avoids normalizing away calm-versus-stressed environments |
| U3 | 12h/60h relative volatility | Indicates volatility expansion or contraction |
| U4 | Completed prior-five-session risk-normalized market move | Recent rebound or decline information |
| U5 | Prior-twenty-session risk-normalized trend | Medium-term bullish/bearish context |

The daily channels U4/U5 are **fixed within each trading session**, based on previously completed daily closes, and each historical 48-step vector uses the market state genuinely available at **its own historical timestamp**. They must not be populated by copying the final forecast's latest trend backward.

**Fitting and data guards** mirror FT0:

- RMS12 **12/12** valid; RMS60 **≥57/60**, with ≤2 consecutive missing; daily RMS63 **≥60/63**, with ≤2 consecutive missing; U4/U5 require genuinely complete constituent daily-return chains and endpoints.
- Hourly floor: fifth percentile of pooled positive training RMS12/RMS60; daily floor: fifth percentile of positive training daily RMS63. The source-specific floor value is learned **only from permitted training data**.
- Each U channel uses its training-only median/**unscaled MAD** robust normalization and the FT0 fallback hierarchy. Count each unique genuine market timestamp **once** in scaler fitting, not five ticker copies or its appearances in overlapping windows. No clipping.
- Endpoint must be genuinely valid and at least **46/48** complete historical market vectors valid. Permitted invalid non-endpoint standardized market channels are neutrally filled with zero **with separate validity masks**; no automatic learned mask-input channels. All market-conditioned models retain **five numerical market channels**.
- The 90-minute staleness limit and `available_at` constraints govern every step. Missing index volume is not filled or added as a sixth feature.

**Why not MASTER's much larger market-feature list?** That literature uses other indices, horizons and stock universes. Our fixed five-dimensional design isolates the market-state hypothesis without a large feature-selection search. If course USA500 lacks compatible price fields/daily closes, the dependent experiments are **blocked**, not silently replaced with another source.

### 9.3 MC0: direct market concatenation

For stock features \(x_{i,s}\in\mathbb R^{16}\) and the aligned standardized market vector \(m_s\in\mathbb R^5\), define

\[
\boxed{z_{i,s}^{MC0}=[x_{i,s};m_s]\in\mathbb R^{21},\qquad Z_{i,t}^{MC0}\in\mathbb R^{48\times21}.}
\]

Feed the same D6 shared LSTM. The exact PyTorch-style parameter count becomes

\[
\boxed{N_{MC0}=4(32)(21+32+2)+33=7{,}073.}
\]

**Question answered:** Does giving an ordinary LSTM the directly observed market history help beyond its own-stock history? A-E2 versus A-E3 should use a matched eligible evaluation intersection, not different dates determined by market missingness. Stock-only coverage remains reported separately.

### 9.4 MC1: endpoint feature-gating versus MC0

At forecast endpoint \(t\), the same contemporaneously available state \(m_t\) controls **16 positive feature weights**:

\[
\boxed{\alpha(m_t)=16\operatorname{softmax}(Wm_t+b),\qquad W\in\mathbb R^{16\times5},\ b\in\mathbb R^{16},\ \tau=1.}
\]

For historical steps \(s=t-47,\ldots,t\):

\[
\boxed{z_{i,s}^{MC1}=[\alpha(m_t)\odot x_{i,s};\,m_s]\in\mathbb R^{21}.}
\]

Thus direct historical market information \(m_s\) remains available, and the same current endpoint gate is broadcast across the stock's preceding 48 steps and across all five stocks.

Scaled softmax ensures

\[
\alpha_j>0,\qquad\boxed{\sum_{j=1}^{16}\alpha_j=16},
\]

so it can **amplify or suppress** different features while keeping mean gate weight 1. Initialize **\(W=b=0\)** to obtain exactly \(\alpha=\mathbf1_{16}\) at model initialization. This permits a unit test that **MC1 equals MC0 before learning** when encoders and heads are copied identically and dropout is disabled.

The gate adds **\(16\cdot5+16=96\)** parameters, for **7,169** total. Gate W uses the existing AdamW 0.01 matrix decay; gate b has no decay. No entropy regularizer, gate dropout, learned temperature, or temperature sweep is approved.

**Reasoning.** Gating is a small inductive bias for state-dependent *relative* feature importance. Because the output passes through a nonlinear LSTM, a high gate coefficient is **not** by itself causal predictor importance. Report gate entropy, saturation/variance, gradients and state-specific behavior. The central controlled contrast is **MC1 versus MC0** on identical information, not MC1 versus stock-only TM0.

### 9.5 MC2: same gate, different historical time of conditioning (**conditional**)

For each history step, substitute its own causally available market state:

\[
\boxed{z_{i,s}^{MC2}=[\alpha(m_s)\odot x_{i,s};\,m_s],\qquad \alpha(m_s)=16\operatorname{softmax}(Wm_s+b).}
\]

MC2 has the **same 7,169 parameters** as MC1. Their difference is the market-state timestamp used to determine the weights, not extra market input or a larger gate.

At an approved invalid historical market step, use the neutral standardized market fill and force **identity stock-feature gate** \(\alpha_s=\mathbf1_{16}\); keep the true validity mask and require a valid market endpoint. Note that MC1's endpoint gate remains defined even on a historical step with a neutral-filled direct market channel; the resulting missing-state behavior is explicitly a design difference and must be reported.

**Activation is not automatic.** On permitted training histories only, compute

\[
\delta_{s,t}=\max_{k\in\{U2,U3,U4,U5\}}|m_{s,k}-m_{t,k}|,
\qquad A_t=\frac{\#\{\text{valid }s:\delta_{s,t}\ge1\}}{\#\{\text{valid }s\}}.
\]

A window qualifies as materially state-varying if **\(A_t\ge0.25\)**. One initial seed-42 MC2 pilot becomes **eligible** only if **≥20% of otherwise eligible training windows** meet the condition across **≥20 distinct trading sessions**, and source, MC0/MC1 diagnostics and compute gates pass. U1 is intentionally excluded from this *structural* variation screen. These thresholds are project heuristics, **not discovered optimal regime boundaries**. Failure of this screen means `INACTIVE_CONDITIONAL`, not evidence MC2 failed financially.

### 9.6 Descriptive causal state slices, never trading signals

The approved diagnostic wording is **"U5 > 0 bullish / U5 < 0 bearish / U5 = 0 neutral"**. There is, however, a **pre-implementation notation ambiguity**: D7b also applies a training-median robust transformation to U5. The sign of the *raw* risk-normalized U5 identifies the sign of the trailing market log return (its denominator is positive), whereas the sign of *median-centered standardized* U5 identifies above/below the **training median**, not necessarily positive/negative raw market return. **The design documents do not explicitly distinguish raw U5 from scaled U5 in the state-label rule; this must be clarified before implementing/reporting the bullish/bearish buckets rather than silently choosing a new threshold.** The approved project still has two primary state axes; use the **training-only median of U2** to label high versus low volatility:

\[
\boxed{V_t=\mathbf1\{U2_t>\operatorname{median}_{\mathrm{train}}U2\}.}
\]

Primary reports are one-dimensional trend and volatility slices. The four joint high/low × bull/bear descriptive cells are reported as interpretable only with **≥30 distinct trading sessions and ≥3 contiguous episodes** each; otherwise flag `SPARSE — EXPLORATORY ONLY`. For episode counting with two possibly different intraday states, the approved session anchor is the **first eligible origin**. Preserve real origin-specific labels and episode counts rather than claiming 30 adjacent days are 30 independent regimes.

One separate cheap **conditional** ridge control, RS3, uses the single predeclared stock-market interaction

\[
\boxed{\phi_{i,t}^{RS3}=\widetilde{M3}_{i,t}\,\widetilde{U2}_t.}
\]

It is added to a same-information ridge only if development state-slice diagnostics and coverage justify it. Its development-led motivation is **exploratory**. There is no automatic regime-specific LSTM or state-dependent trading-size change.

---

## 10. D8 — Cheap peer information and genuinely directed predictive tests

### 10.1 Why distinguish contemporaneous correlation from lead–lag?

Observing \(\operatorname{Corr}(r_{i,s},r_{j,s})\neq0\) shows co-movement, potentially from a common market shock. A *directed predictive* hypothesis is instead of the form

\[
\boxed{\mathbb E\big[y_{i,t}^{TG0}\mid X_{i,t},M_t,z_{j,t-\ell}\big]\neq\mathbb E\big[y_{i,t}^{TG0}\mid X_{i,t},M_t\big],\qquad i\ne j.}
\]

This remains an association about subsequent *relative* outcomes after controlling for own-stock and market information—not proof of causal price transmission. Hou (2007) and Chordia–Swaminathan (2000) motivate information-diffusion/volume-related lead–lag tests at other frequencies and often within industries. Our five stocks are **liquid, cross-sector** names; negative results would not refute that research.

### 10.2 Canonical peer signal and E5 leave-one-out summaries

Use the already transformed **FT0.M1 stock signal** \(z_{j,s}\) as the primary observed peer movement, **without refitting a peer-specific scaler**. For target stock \(i\) with the other four as peers:

\[
\boxed{P^{mean}_{i,s}=\frac14\sum_{j\ne i}z_{j,s},\qquad P^{disp}_{i,s}=\sqrt{\frac14\sum_{j\ne i}\left(z_{j,s}-P^{mean}_{i,s}\right)^2}.}
\]

The dispersion divisor is **4** (population convention). Add both summaries at every historical step to an otherwise unchanged MC0 encoder:

\[
\boxed{z_{i,s}^{E5}=[x_{i,s};m_s;P^{mean}_{i,s};P^{disp}_{i,s}]\in\mathbb R^{23}.}
\]

Its width-32 LSTM plus scalar head has **7,329 parameters**. Evaluate **both** a same-lag-dictionary ridge+peer control and a standard peer-informed LSTM versus corresponding MC0 controls.

**Why this cheap control first?** If summaries supply no incremental information, a learned mixer may have little useful signal to exchange; if summaries help, we know peer information is relevant before crediting a special spatial architecture. The algebra warns against overinterpretation: with five stocks,

\[
P^{mean}_{i,s}=\frac{\sum_{j=1}^{5}z_{j,s}-z_{i,s}}4.
\]

A linear coefficient times the common sum adds the same value to every stock score and cancels from their ranking, so a linear mean-peer term can act partly like modifying the target's own coefficient. **A fitted peer mean is not automatically evidence of an individual directional leader.**

### 10.3 A-E5L: one formation-frozen leader–follower pair and reverse test

Among the original five, compute their **60 completed preformation-session mean daily dollar volumes**. Define

\[
\boxed{H=\arg\max_i\overline{DV}_{i,60},\qquad L=\arg\min_i\overline{DV}_{i,60}.}
\]

The **ticker identities have not yet been established by an audited preformation calculation**; do not guess or select later according to returns. Test both \(H\to L\) and \(L\to H\) as a reverse-direction control.

The approved lags are **\(\ell=0,1\)** over **scheduled *completed trading-hour observations***. Lag zero means the most recent completed, available peer hour at the historical step, **not** a return from the forecast's future four hours. Lag one may cross a session boundary at the first daily forecast origin and must not be described as uniformly sixty elapsed minutes.

Four targeted direction-and-lag channels are

\[
\boxed{D_{i,s,\ell}^{H\to L}=\mathbf1\{i=L\}\,z_{H,s-\ell},\qquad D_{i,s,\ell}^{L\to H}=\mathbf1\{i=H\}\,z_{L,s-\ell},\quad\ell\in\{0,1\}.}
\]

Add lagged leave-one-out mean \(P^{mean}_{i,s-1}\). Thus LL1 has **five additional signal channels** beyond E5. Use **two fixed H/L target-identity indicators** in **both** LL0 and LL1 controls; otherwise an apparent gain could come from disclosing ticker identity rather than from directed signals.

| Ordinary LSTM information arm | Channels | Parameters |
|---|---:|---:|
| MC0 | 21 | 7,073 |
| E5 summaries | 23 | 7,329 |
| LL0 (E5 + two fixed H/L indicators) | 25 | 7,585 |
| LL1 (LL0 + lagged peer mean + four directed channels) | 30 | 8,225 |

**Research sequencing:** Fit **LL0-R versus LL1-R ridge first**, using the fixed ridge-selection rules, then consider **one** conditional seed-42 ordinary-LSTM directed pilot if evidence or a carefully documented nonlinear hypothesis justifies it. Report both lag ages and origins. There are **20 possible ordered stock pairs**, but the study does not search all 20 and report the best: that would severely increase selection flexibility.

### 10.4 Cheap falsification/interpretation checks

- A *market-residual* exploratory diagnostic may compute \(\xi_{j,s}=r_{j,s}-\widehat\beta_{j,s^-}r_s^M\) **only** when genuinely aligned USA500 and stock returns and a causal prior beta estimator exist. This is not another main model input.
- The single predeclared **timing-destruction diagnostic** substitutes the peer's signal from **10 preceding eligible trading sessions at the same scheduled slot**, wherever valid. It can show a model's sensitivity to short-run alignment, but is **not** a valid formal temporal permutation p-value or selection-adjusted test.
- TG0 is relative to the five-stock median and MAD. A peer can predict shifts in the *other four names* that change the denominator or median without predicting the target stock's absolute raw return. Report raw four-hour-return associations **descriptively** alongside TG0 associations to clarify interpretation; **do not** train an absolute-direction trading model.

### 10.5 Conditional continuous state dependence LL2

A later ridge-first control (A-E6R), not automatically activated, asks whether a directed source coefficient varies with the already approved continuous **U2 volatility state**:

\[
\boxed{\widehat y_{L,t}=f_0(\text{own, market, peer controls})+\big(\beta_0+\beta_1\widetilde U2_t\big)z_{H,t}.}
\]

Its conditional slope is \(\partial\widehat y_{L,t}/\partial z_{H,t}=\beta_0+\beta_1\widetilde U2_t\). No sign reversal or positive coefficient is forced. Activation needs LL1/state evidence, enough distinct regimes, same-information constant-coefficient control and explicit budget. A successful coefficient on one development slice does **not** automatically authorize MC1+SP3 or a new neural architecture.

### 10.6 One conditional universe expansion

The initial panel has only four peers per stock and **no within-sector peers**. One approximately **20-stock sector-balanced** expansion may be justified by structural underpowering and passed source/synthetic audits; it may not be activated solely because development Sharpe is poor. A bigger universe changes **TG0 median/MAD, stock distribution, available peers and model dimensions**. Its results require newly matched baselines and cannot be compared with five-stock IC as though the target stayed fixed.

---
## 11. D9 — Learned stock mixing, attention alternative and the full-information control

### 11.1 Scientific question and order of evidence

Once ordinary ridge and LSTM controls have already tested the presence of peer information, a **conditional** architecture test can ask whether a structured neural exchange of representations adds value. The first permitted learned mechanism is **SP3, StockMixer-inspired low-rank stock mixing**; **SP1 attention** is an alternate branch requiring a distinct rationale. StockMixer (AAAI 2024) motivates economical learned stock interactions; the study's full architecture is *not* copied.

It would be scientifically weak to say “SP3 is better than the plain LSTM because mixing is valuable” when SP3 is given all peer histories but the plain comparator sees only one target's history. D9 therefore requires an ordinary **full-peer-information LSTM control** before a strong architecture-specific claim.

### 11.2 SP3 rank-two residual exchange

The shared MC0 encoder produces one final hidden representation for each of five stocks:

\[
H_t=\begin{bmatrix}h_{1,t}^{\mathsf T}\\\vdots\\h_{5,t}^{\mathsf T}\end{bmatrix}\in\mathbb R^{5\times32}.
\]

The **approved low-rank bottleneck is \(K=2\)**. Let

\[
M_1\in\mathbb R^{2\times5},\qquad M_2\in\mathbb R^{5\times2}.
\]

With a **non-affine LayerNorm applied across the 32 hidden coordinates of each stock**, the mixer is

\[
\boxed{\widetilde H_t=H_t+M_2\operatorname{GELU}\big(M_1\operatorname{LN}(H_t)\big).}
\]

This maps \(5\times32\) stock states → \(2\times32\) bottleneck → \(5\times32\) received exchange, then adds the original representation as a residual. The two stock-axis matrices are **bias-free**, adding

\[
\boxed{2\cdot5\cdot2=20}\quad\text{trainable parameters},
\]

so the total MC0+SP3 has **7,093 parameters**. The linear stock-axis component has rank at most two, although the **GELU** makes the complete function nonlinear. Two learned channels are a compact regularized design, **not** economically identified market factors.

Initialize \(M_1\) with the seeded standard small-matrix initialization and **\(M_2=0\)**, so

\[
\boxed{\widetilde H_t\big|_{init}=H_t.}
\]

This exact identity permits a matched MC0 equivalence test. Since \(M_2=0\), \(M_1\)'s gradient can initially be zero; test that gradients reach it after \(M_2\) starts learning. The 10% dropout and shared scalar head remain unchanged. Do not automatically add learned ticker heads, factor losses, extra mixer dropout or a rank search.

**Interpretation:** SP3 can make *stock-specific* predicted-score adjustments despite the shared head, since different rows of \(M_2\) redistribute bottleneck channels differently. But trained mixing weights are not causal lead–lag coefficients, and fixed stock-axis matrices depend on ticker identity and order.

### 11.3 Ordinary LSTM with full four-peer feature histories

For target \(i\), list the other four names \(j_1,\ldots,j_4\) in the documented deterministic target-excluding ticker order. Give an ordinary LSTM the same source histories:

\[
\boxed{z_{i,s}^{fullpeer}=[x_{i,s};m_s;x_{j_1,s};x_{j_2,s};x_{j_3,s};x_{j_4,s}]\in\mathbb R^{16+5+4(16)}=\mathbb R^{85}.}
\]

With length 48 and hidden width 32, the full-peer ordinary LSTM has

\[
\boxed{N_{fullpeer}=4(32)(85+32+2)+33=15{,}265.}
\]

This is an **information-matched but not parameter-matched** control: it observes all peers explicitly but processes their histories *jointly inside recurrence*; SP3 processes each stock recurrently before endpoint exchange. If SP3 beats the full-peer control on matched dates, that supports an economical **architectural inductive bias**, not a mathematically pure effect of the bottleneck independent of parameter count.

There is an approved resource tension: replicating **TM0, MC0, full-peer ordinary LSTM, SP3** makes **four neural families**, while the default D6h/D12 finalist limit is **three**. If SP3 qualifies, the control **must not disappear quietly**. Resolve through a deliberate protocol/budget amendment or narrow the claim that is made at confirmation.

### 11.4 Canonical stock order and a mathematical equivariance sanity check

The stock axis is *always* `AAPL, JPM, JNJ, WMT, CAT`. The SP3 mixing matrices act on that specific order. An accidental reordering alone changes its function and is an error. A legitimate simultaneous **coordinate change** can be checked using permutation matrix \(P\):

\[
\boxed{H'=PH,\qquad M_1'=M_1P^{\mathsf T},\qquad M_2'=PM_2.}
\]

With stockwise LayerNorm and the shared head, the equivalent model should satisfy

\[
\boxed{\widetilde H'=P\widetilde H.}
\]

This **does not** imply a fitted SP3 is permutation invariant when ticker rows alone change. An N=5 mixer cannot accept N=20 without changing matrix dimensions, the target universe and the training population.

### 11.5 SP1: one-head cross-stock attention (**conditional alternative**)

If the roadmap's distinct activation hypothesis is met, one small attention model is specified. With \(H\in\mathbb R^{5\times32}\), non-affine stockwise LayerNorm, no projection biases, and \(W_Q,W_K,W_V\in\mathbb R^{32\times16}\), \(W_O\in\mathbb R^{16\times32}\):

\[
\begin{aligned}
Q&=\operatorname{LN}(H)W_Q,\quad K=\operatorname{LN}(H)W_K,\quad V=\operatorname{LN}(H)W_V,\\
A&=\operatorname{rowSoftmax}\left(\frac{QK^{\mathsf T}}{\sqrt{16}}\right),\\
\boxed{\widetilde H}&=H+AVW_O.
\end{aligned}
\]

It adds \(4(32\cdot16)=\mathbf{2,048}\) projection parameters, so **9,121 total** with MC0. Initialize \(W_O=0\) for residual identity and verify gradient propagation. Unlike SP3's stock-axis map, the attention matrix \(A_t\) changes with current learned stock representations. That can model dynamically changing information relationships but adds greater flexibility to a very small panel.

**No automatic SP1 training:** acceptable reasons include a demonstrated need for input-dependent peer association, SP3's *mechanism-specific* failure on a planted dynamic-peer test, or an explicitly approved changing-universe/equivariance experiment. Weak SP3 net Sharpe **by itself** does not trigger SP1. Attention weights are diagnostics, **not faithful or causal explanations by assumption** (Jain–Wallace, 2019).

### 11.6 Activation and reporting

SP3's initial seed-42 pilot is **conditional** on D8 peer-information evidence *or a documented information-access hypothesis*, completed as-of and source audits, a suitable full-peer control, valid five-name panels and remaining D6h budget. A combined **MC1+SP3** is at most one separate later conditional A-E6R candidate, not part of initial SP3 training.

Mandatory synthetic checks include identity equivalence, planted source-stock prediction of later target response, off-diagonal perturbation sensitivity (changing stock \(j\) can affect \(i\)), zero peer sensitivity in ordinary stockwise MC0, ticker/order mapping and eventual gradient flow. Financial reports include Rank IC, MSE, paired uncertainty, net trading, parameter/runtime budget, bottleneck domination and local model sensitivity

\[
S_{ij,t}=\frac{\partial\widehat y_{i,t}}{\partial h_{j,t}},\qquad i\ne j,
\]

which **is not** proof that company \(j\) causally influences company \(i\).

---

## 12. D10 — Optional temporal readout *or* auxiliary horizon supervision

The default remains **TM0 final hidden state and TG0**. A-E7 is **not** a mandatory model family. At most **one** new mechanism is eligible when a *specific temporal-memory or training-objective problem* is documented from permitted development diagnostics. Simply observing a disappointing Sharpe is not a temporal diagnosis.

### 12.1 TM1: one trainable temporal query over 48 hidden states

Let the standard LSTM's 48 hidden vectors be \(h_{i,s}\in\mathbb R^{32}\). A shared trainable query \(q\in\mathbb R^{32}\) scores each historical state with a **non-affine LayerNorm**:

\[
\boxed{e_{i,s}=\frac{q^\mathsf T\operatorname{LN}(h_{i,s})}{\sqrt{32}},\quad a_{i,s}=\frac{\exp(e_{i,s})}{\sum_{u=1}^{48}\exp(e_{i,u})},\quad c_i=\sum_{s=1}^{48}a_{i,s}h_{i,s}.}
\]

A one-scalar residual readout forms

\[
\boxed{\bar h_i=h_{i,48}+\gamma(c_i-h_{i,48}),\qquad \gamma_0=0.}
\]

Thus at initialization \(\bar h_i=h_{i,48}\) **exactly**, recovering TM0 before learning. The new parameters are **32** query components plus **one** \(\gamma\): **+33** (stock-only TM1 **6,466**; MC0 TM1 **7,106**). Standard decay 0.01 applies to \(q\), zero to scalar \(\gamma\), with no extra attention dropout. An initially zero \(\gamma\) can initially suppress query gradients; test later gradient flow.

**Reasoning.** A final LSTM hidden state is intended to summarize the preceding window, but may fail to preserve a predictive early event whose useful position varies. A cheap query over earlier hidden states tests that specific readout limitation. It does not make a 48-hour history longer. Attention entropy

\[
\boxed{H_i=-\frac1{\log48}\sum_{s=1}^{48}a_{i,s}\log a_{i,s}}
\]

is a behavior diagnostic, not a causal explanation of financial returns.

### 12.2 TG2: 1h/2h/4h auxiliary *relative-return* tasks

The alternative changes supervision rather than temporal readout. For \(h\in\{60,120,240\}\) eligible **regular-session trading minutes**, use real minute entry/exit references:

\[
\boxed{r_{i,t}^{(h)}=\log\frac{P_i(e_t+h)}{P_i(e_t)},\qquad y_{i,t}^{(h)}=\frac{r_{i,t}^{(h)}-\operatorname{median}_jr_{j,t}^{(h)}}{\operatorname{MAD}_j(r_{j,t}^{(h)})+\epsilon_h}.}
\]

Each auxiliary horizon floor \(\epsilon_h\) is fitted separately on its permitted training outcomes; do not copy the 240-minute floor by assumption. Three shared-encoder scalar heads use fixed weights

\[
\boxed{\mathcal L_{TG2}=0.2\mathcal L_{60}+0.2\mathcal L_{120}+0.6\mathcal L_{240}.}
\]

Two extra heads add **66** trainable parameters. All heads require matured genuine labels; match the TG0 comparator on the same valid label population and report attrition. **Only the 240-minute head** supplies rankings/trades. Select checkpoint by the **primary four-hour inner-validation MSE**, not the weighted auxiliary score or trading Sharpe.

**Reasoning.** Shorter-horizon supervision could stabilize a weak representation, but tasks can also compete (*negative transfer*). Report loss contribution and inter-task gradient alignment, schematically

\[
\operatorname{cos}(g_{h},g_{240})=\frac{g_h^\top g_{240}}{\|g_h\|_2\|g_{240}\|_2},
\]

as a diagnostic, not an automatic license for another gradient-correction algorithm. The 0.2/0.2/0.6 weights are project defaults, not experimentally optimal.

### 12.3 Activation discipline

- **TM1** is preferred only for evidence that the final hidden-state readout loses useful information (e.g., cheap earlier-state probe or synthetic event-position test).
- **TG2** is the alternative only for credible limitation of sole four-hour supervision, with valid matured shorter-horizon outcomes.
- Choose **one parent information set before training** the extension; compare with its own TM0/TG0 parent, not whichever parent later looks favorable.
- At most **one** initial A-E7 family, seed 42, other seeds only via D6h. TM1+TG2 jointly and large learned multiscale recurrent networks are **not authorized**. If neither deficiency is established, report `INACTIVE_CONDITIONAL`.

---

## 13. D11 — Optional factor information, future volatility supervision or recent-feedback adaptation

The frozen first-pass default is **FC0, AD0, TG0**: no additional latent-factor model, no rolling label-feedback adaptation, and one primary four-hour relative-return target. A-E8 is **normally deferred**. If a distinct later issue is identified, **at most one** factor/risk/adaptation mechanism may be considered.

### 13.1 FC7 observed factors before FC6 nonlinear pooling

Five stocks drawn from five sectors give **no meaningful in-universe same-sector leave-one-out group**. A sector average consisting only of the target stock is not independent sector information.

**FC7** would first provide a verified, historically available external observed market/sector factor through an ordinary information-matched control:

\[
\widehat y_{i,t}=f_\theta(X_{i,t},M_t,F_{S(i),t}),
\]

where \(F_{S(i),t}\) has actual as-of provenance. No external sector source is assumed available, and FC7 is **not activated for the initial five-name first pass**.

**FC6** is conceptually a compact pooled hidden factor after a justified expanded universe with sufficient sector representation. For a stock hidden vector \(h_i\), schematic common and leave-one-out sector pools are

\[
\boxed{m_t^{pool}=\frac1N\sum_jh_{j,t},\qquad m_{S(i),-i,t}=\frac1{|S(i)|-1}\sum_{\substack{j\in S(i)\\j\ne i}}h_{j,t}.}
\]

A *stock-interactive* fusion might have schematic form

\[
\widetilde h_{i,t}=h_{i,t}+g_\phi(h_{i,t},m_t^{pool},m_{S(i),-i,t}),
\]

rather than adding an identical common vector to every stock score, which would cancel in the ranks. **The exact FC6 fusion MLP width and some implementation details were not approved**; do not fill them unless this branch is formally activated. Full FactorGCL hypergraph/VQ/factor-discovery structures are deferred.

### 13.2 TG4 auxiliary four-hour realized volatility (**conditional**)

TG4 would teach the shared encoder a separate *future volatility* target from a **genuine complete one-minute price path**, with 240 log increments:

\[
\boxed{RV_{i,t}^{4h}=\sum_{k=1}^{240}\left[\log\frac{P_i(e_t+k)}{P_i(e_t+k-1)}\right]^2,\qquad v_{i,t}=\log(RV_{i,t}^{4h}+\epsilon_{RV}).}
\]

A separate linear volatility head adds **33 parameters**, with fixed training objective

\[
\boxed{\mathcal L_{TG4}=0.8\mathcal L_{TG0}+0.2\mathcal L_{RV}.}
\]

The volatility label must use permitted training-only scaling and a genuinely observed full path; no missing-minute patching. Use primary TG0 validation MSE for checkpoint selection. The volatility head **does not change position sizing, ranking, exit time or risk limits**—it is a representation-learning hypothesis only.

**Unsettled if activated:** the exact positive \(\epsilon_{RV}\) numerical/fitting rule was *not* separately fixed. The later Codex implementation must ask for approval rather than inserting a guessed constant. The TG4 branch remains inactive until a credible volatility-representation limitation and source feasibility are established.

### 13.3 AD3: a rolling regularized linear head on a fixed LSTM encoder (**conditional**)

Unlike MC1 (which conditions features on observed market state), AD3 would respond to **recently matured labels**. Freeze the historically fitted encoder \(h_{i,t}=F_{\widehat\theta}(X_{i,t})\in\mathbb R^{32}\) and its static head \(\theta_0=(w_0,b_0)\in\mathbb R^{33}\). At the beginning of each trading day \(d\), estimate a head \(\theta_d\) from the **previous 63 exchange sessions' matured four-hour labels**, requiring **≥50 eligible sessions**. Use the same head at both origins that day. If data or numerical conditions fail, retain \(\theta_d=\theta_0\) and record the fallback.

With augmented hidden vector \(\bar h_{i,t}=[h_{i,t};1]\), the approved conceptual weighted ridge-to-static objective is

\[
\boxed{
\widehat\theta_d=\arg\min_{\theta\in\mathbb R^{33}}\left\{
\frac1{|\mathcal C_d|}\sum_{s\in\mathcal C_d}\frac1{|\mathcal O_s|}\sum_{o\in\mathcal O_s}\frac15\sum_i(y_{i,s,o}^{TG0}-\theta^\top\bar h_{i,s,o})^2+\lambda_d\|\theta-\theta_0\|_2^2
\right\},\quad \lambda_d=\frac{\operatorname{tr}(\widehat\Sigma_{h,d})}{32}.}
\]

Here \(\widehat\Sigma_{h,d}\) is a causal covariance of rolling permitted hidden representations. The multiplier-one mean-hidden-variance shrinkage is a project default; covariance denominator and intercept-penalty **corner cases remain unspecified** and need approval *if activated*.

**Prequential discipline is essential:** at daily update time \(\tau_d\), every used label must satisfy

\[
\boxed{\operatorname{labelAvailableAt}(s,o)\le\tau_d.}
\]

If adaptation relies on *recent issued forecast performance*, those forecasts must be genuine prior out-of-training historical issuances, **not** predictions retrospectively generated by a model fitted using later data. This is a high-risk leakage boundary. Full encoder retraining, new per-hour adaptation schedules and broader meta-learning machinery are **not authorized**. FinPFN motivates adaptation concepts but does not establish that AD3 works for this panel.

### 13.4 AD1 and advanced approaches remain deferred

AD1 would use recent correctly issued performance statistics (Rank IC, loss or bias) as inputs, but only after AD3 provides a defensible rationale. Discrete latent regimes, vector-quantized factor codebooks, full mixture-of-experts and large hypergraph/meta-learning models are **outside first pass**. D11's default outcome is an honestly documented *no extra A-E8 run*.

---
# Part V. Research inference, confirmation and failure diagnosis

## 14. D12 — Architecture selection, one-look confirmation and limits of statistical claims

### 14.1 The frozen experiment ladder

| Experiment | Role and approved comparator | Mandatory or conditional? |
|---|---|---|
| **A-E0** | Historical source, timestamp, feature, target, corporate-action and execution feasibility | **Mandatory audit**, source/test status must be verified |
| **A-E1** | Fixed FT0.M1 momentum and pooled lagged ridge; same-information cheap market/peer ridge controls later | **Mandatory inexpensive references** |
| **A-E2** | FT0/TM0/SP0 stock-only shared LSTM versus momentum/ridge | **Mandatory** |
| **A-E3** | MC0 USA500 concatenation versus TM0 and market-ridge | **Mandatory central market-information hypothesis**, source-blocked until verified |
| **A-E4 / A-E4R** | MC1 endpoint gating versus MC0; causal U2/U5 diagnostic slices | **High priority**, data dependent |
| **A-E4M** | MC2 historical-step gate versus MC1/MC0 | **Conditional**, training-history activation test |
| **A-E5 / A-E5L** | Peer mean/dispersion, directed H↔L lags, ridge-first/ordinary LSTM | **High priority cheap controls**, neural LL1 conditional |
| **A-E6 / A-E6R** | SP3 versus full-peer ordinary LSTM; separately justified state-dependent combination | **Conditional** |
| **A-E7** | **One of** TM1 or TG2 | **Optional; normally inactive** |
| **A-E8** | **One of** factors, TG4 volatility supervision or AD3 adaptation | **Optional; default defer** |
| **A-E9** | Locked finalist forecasting and economic evaluation, 2024-07 to 2025-06 | **Mandatory only for a confirmatory claim**, not yet unlocked |

The roadmap is an **ordered list of hypotheses and conditional possibilities**, not permission to fit every named neural model. MC1 aliases in the source menu (`FT1`/`RG1`) are not separate additional experiments; similarly some pooling/factor and adaptation IDs represent overlapping concepts. Avoid duplicate fits dressed as distinct mechanisms.

### 14.2 Finalist-selection evidence

Select on **development session-aggregated Rank IC**, supported by paired differences, fold/seed stability, MSE, economically realized after-cost results, complexity and the **one-standard-error simplicity preference**. Do not choose an epoch using outer Rank IC/net Sharpe (D6g uses inner MSE). Do not select one lucky seed while suppressing the other seeds. A weak extension need not win a confirmation slot.

The normal confirmation neural shortlist has **≤3 architecture families**, conventionally **TM0**, **MC0 when source-valid**, and at most **one additional development-promoted architecture**, accompanied by necessary nonneural references. Every neural finalist uses seeds **42, 123, 2026**. If SP3 requires a fourth full-peer neural family for its strongest mechanism claim, the three-family limit must be expressly reconciled *before* A-E9; silently dropping the matched control is not permitted.

A project-level results record should distinguish:

- `PROMOTED`: valid model supported by the selected evidence for further evaluation;
- `NOT_PROMOTED`: valid result without enough evidence to justify escalation;
- `INCONCLUSIVE`: insufficient precision/coverage/seed stability;
- `FAILED` or `INVALID`: defective fitting/information/accounting, with preserved trace;
- `BLOCKED`, `DEFERRED`, `INACTIVE_CONDITIONAL`: prerequisites unavailable or branch intentionally unrun.

**Why no automatic model-selection p-values?** Repeated trials over architectures, losses, seeds and trading policies can select a high realized score even under weak true predictability. Cawley–Talbot (2010) and White (2000) motivate keeping a full search ledger and a separate confirmation period; the adopted block bootstrap alone is not a correction for the whole search.

### 14.3 Locked A-E9 protocol

Before seeing **any confirmation forecasting or economic metric**, lock a versioned manifest containing selected candidate/controls, three seeds, the allowed through-June-2024 fitting history, preprocessing/target formulas, data/code/config/checkpoint hashes, timing and eligibility, paired statistical methods, both trading policies, all cost/borrow assumptions and planned report columns. Run D6g's *fresh preconfirmation two-pass* refits using only permitted history; no confirmation-supervision information in scaling, epoch selection, candidate ranking or new mechanism activation.

If the eventual first-look result is negative, **report it**. A later model revision using information learned from that period can be legitimate new exploration, but the same dates are then no longer pristine confirmation data for that revision. A verified implementation defect must be corrected, with the invalid first look and its changed evidential status preserved rather than overwritten.

### 14.4 Daily equity, net returns and Sharpe

A physically correct portfolio is represented by cash \(C_d\), long and short signed share holdings \(Q_{i,d}\), and marked prices \(P_{i,d}\). The bookkeeping equity is conceptually

\[
\boxed{E_d=C_d+\sum_i Q_{i,d}P_{i,d},}
\]

where cash must already reflect completed short-sale proceeds, trade fills, financing, and real dividend/split obligations. With a complete and defensibly marked path:

\[
\boxed{R_d^{net}=\frac{E_d}{E_{d-1}}-1,\qquad R_{ann}=\left(\frac{E_T}{E_0}\right)^{252/D}-1.}
\]

Descriptive annualized Sharpe (under a clearly disclosed risk-free convention) is

\[
\boxed{SR_{ann}=\sqrt{252}\frac{\operatorname{mean}_d(R_d^{net}-R_{f,d})}{\operatorname{SD}_d(R_d^{net}-R_{f,d})}.}
\]

Annualization is a reporting convention; with time dependence, daily Sharpe is **not** itself a statistical significance test. A missing valid end-of-day mark or unresolved terminal fill prevents a falsely complete realized growth result. Cash, dividends, borrow and gross/net equity must reconcile in the ledger.

### 14.5 Complete economic references and path-dependent costs

Report **cash**, equal-weight five-stock buy-and-hold (long-only contextual benchmark), and **1,000 reproducible randomized two-sided strategy paths**. Every predictive model receives both Policy A/B and **0/2/5/10-bps execution** plus **0/0.5/3%-annual borrow** scenarios, with no-trade days included. Break down turnover, short-duration churn, costs, actual holding times, veto and cap failures, emergency stops, market exposure, stock/sector concentration, return/drawdown. Never compare a long-only five-stock buy-and-hold Sharpe to dollar-neutral intraday Sharpe as if exposures were risk matched.

A performance claim can be **predictively successful but economically unsuccessful**: suppose predicted ranks improve but top/bottom choices fluctuate hourly. The physical sleeve account may execute costly offsets, the veto may skip good entries, and the 5-bps reference can erase an otherwise small gross edge. This is a *substantive research outcome*, not automatically a software failure.

### 14.6 Formal null testing and its scope

The project-wide shared specification expresses interest in dependence-aware temporal nulls, but the approved **first-pass D12** decision makes an expensive **full-selection null conditional**, requiring an additional budget/protocol decision. **Do not report a selection-adjusted permutation p-value if that rerun did not occur.**

A conceptual candidate would shift **whole five-stock, same-origin trading-session label panels** against predictors rather than independently permuting five tickers or overlapping outcomes. But the exact lag distribution, stationarity/exchangeability assumptions and split-boundary handling are **not finalized**; a naive circular shift is not thereby a valid exact null.

If an appropriate protocol is approved, the strong test statistic requires rerunning the relevant fitting/selection process on each defensible null dataset. A conventional Monte Carlo exceedance formula would be

\[
\widehat p=\frac{1+\sum_{b=1}^{B}\mathbf1\{T_b^{null}\ge T^{obs}\}}{B+1},
\]

but **the formula does not confer validity** absent a valid null mechanism and complete relevant reruns. Cheap post-fit shuffled outputs or D8's ten-session shifted-peer diagnostic have narrower descriptive roles.

---

## 15. D13 — Why an audit can pass while a model still fails economically

The project separates **procedural correctness** from **scientific effectiveness**:

\[
\boxed{\text{valid pipeline}\ \not\Rightarrow\ \text{predictive signal}\ \not\Rightarrow\ \text{profitable net trading}.}
\]

A passing data-timing test guarantees only that the check's specified invariant held. It cannot guarantee that future four-hour returns are predictable or stable across regimes.

### 15.1 Ten logical stage gates (not ten separate expensive systems)

| Gate | Checkpoint | What failure is localized | When it matters |
|---|---|---|---|
| G0 | Authority, repository, source, protocol and human approvals | Incompatible versions, unauthorized conditional branch, secret/protocol drift | At kickoff/change |
| G1 | Raw prices, source gaps, formation, actions | Duplicates, implausible OHLCV, split wealth error, missing minute/market source | After data version |
| G2 | Exchange calendar, `available_at`, label and entry clock | 10:30/11:30 or 240-minute mistakes, future-label entry conditioning, stale index | After time/target work |
| G3 | FT0, U1–U5, peer inputs, fitted scaling, retention | Formula/warm-up error, future scaler, distorted missingness/target MAD | After feature version |
| G4 | Baselines and physical simulator | Wrong ridge lag/penalty objective, double costs, phantom P&L, incorrect sleeve netting | Before economic claims |
| G5 | Training engine sanity | Wrong session weights, dropout, clipping, early-stopping logic, inability to fit tiny planted task | Before real neural fits |
| G6 | Per neural calibration/refit pair | Nonfinite loss, collapsed forecasts, clipping, wrong seed/cutoff, missing checkpoint | After each run |
| G7 | Gating, peer, temporal/spatial/optional mechanism | Broken identity, wrong stock order, unfair comparator, unauthorized activation | At conditional activation |
| G8 | Development metrics, economic and inferential comparisons | Unpaired Rank IC, invalid block bootstrap, selection by lucky seed/Sharpe, unreconciled equity | Before promotion |
| G9 | Locked confirmation and complete report | Post-lock changes, test peeking, missing unsuccessful runs, irreproducible claims | Once at A-E9 |

**Resource discipline:** G0–G5 are primarily once-per-canonical-version; G6 is cheap per completed fitting pair; G7 runs when an applicable optional mechanism is genuinely under consideration; G8 at meaningful development comparisons; G9 once around protected confirmation. Failures block the smallest valid dependent branch, rather than rerunning unrelated expensive models.

### 15.2 Trace the earliest divergent boundary B0–B7

The approved **post-run boundary replay** is intended to explain *why* a valid model underperformed, not merely catch blatant code errors:

| Boundary | Reconstruct for a selected origin or trade | Plausible explanation if it diverges |
|---|---|---|
| **B0** source → canonical bar | Source row, raw/adjusted OHLCV, corporate-action and version hash | Feed gap, changed adjustment or symbol |
| **B1** canonical → historical as-of | True period end, `available_at`, 90-minute market freshness, chosen source row | Future input, stale market, wrong stub/DST mapping |
| **B2** historical → unscaled features/target | Window numerators, denominator floors, indicator warm-up, TG0 median/MAD | Incorrect feature, low-MAD amplification, changed universe |
| **B3** unscaled → model-ready | Fitted training median/MAD, fallback, masks and final 48×channels tensor | Scaler mismatch, feature compression, new out-of-range values |
| **B4** model input → representation | Selected hidden state, market gate, peer exchange, TM1 readout *if present* | Collapse, saturated gate, stock-order bug, no effective mixing |
| **B5** representation → forecast/ranks | Five scores, midranks, selected top/bottom, matured outcomes | No stock discrimination, rank instability, concentrated errors |
| **B6** score → sleeve/order/fill | Veto/admission, virtual vs physical shares, minute-open fill, actual external cost | Good rank turned into needless reversal or missed entry |
| **B7** fills → equity/result | Cash, short liability, cost and borrow, daily NAV/report row | Bookkeeping error or genuine signal too small after costs |

A targeted *deterministic inference-mode replay* should locate the earliest comparable divergence using canonical source data, scaler metadata and retained checkpoint. It should **not claim** to recover unlogged training-time dropout masks or historical optimizer steps. The output is a small Markdown diagnosis with exact keys, actual before/after values, evidence for and against plausible hypotheses, and the smallest downstream work requiring rerun if a defect is real.

### 15.3 Three resource tiers for model-failure explanation

**T0 — mandatory cheap summaries:** counts, percentiles, feature/target distribution, model-score spread and ties, clipped-gradient fraction, train/inner-validation curves, per-stock/origin/regime Rank IC, trade turnover, P&L and costs. Reuse existing metrics and canonical storage; no entire tensor dumps.

**T1 — small on-demand replay:** reconstruct about **8–12 fixed representative development origins** across periods/origins/regimes where actually available, plus up to **3–5 explicitly post-hoc anomalous cases** per relevant failure class when needed. Show selected before/after transformations and source IDs, not entire historical arrays. Mark post-hoc examples as diagnostic, not independent selection evidence.

**T2 — justified intervention:** a cheap planted mechanism test or separately approved full neural rescue/retraining/20-stock expansion only when T0–T1 cannot discriminate competing explanations. Every actual neural fit consumes the D6h budget; no automatic architecture/hyperparameter search.

The plan calls for **one** reusable importable diagnosis library/CLI with actions conceptually like `summarize`, `trace-origin`, `trace-trade`, `compare-runs`, and a concise `.md` + small `.json` report. These names are illustrative interfaces, not repository paths already known to exist.

### 15.4 Examples of *scientific* failure diagnosis

**Case A — training loss flat.** Inspect source/target alignment, tiny synthetic overfit ability, zero/NaN gradients, wrong loss normalization, output variance and actual optimizer config before concluding inadequate architecture capacity.

**Case B — training MSE improves but development Rank IC falls.** Inspect the training–development gap, target MAD floors, market state mix, per-origin sample coverage, forecast ties, seed effects and source-scaler shifts. Possible explanations include overfitting, regime change, weak ranking signal or objective mismatch. The audit cannot decide which without discriminating evidence.

**Case C — Rank IC improves but 5-bps net P&L deteriorates.** Trace selected top/bottom positions, paired leg contributions, ranking reversals, external orders and cost drag under A and B. The cause could be a valid but insufficiently monetizable edge, a high-churn policy, concentration, or a simulator defect. Do not automatically add a direction filter or retune sleeves: that would change the approved experiment.

**Case D — a five-stock method performs poorly after a justified twenty-stock expansion.** First check that the *original five* raw OHLC, transformed FT0/U1–U5 and timestamp/adjustment lineage still match. Then compare **five-name and twenty-name TG0 median/MAD/floors on common names/dates**, original versus new stock distributions and retention, sector/peer topology, SP3 mixer dimensions and finally transaction-cost/turnover differences. A drop in five-name IC versus twenty-name IC is **not a matched performance contrast on the same target**. The diagnosis should classify evidence as source/pipeline change, target/population change, representation/capacity change, trading-economics change or inconclusive. No automatic 20-stock refit or confirmation-period retuning.

### 15.5 Audit artifacts and software boundaries

Maintain linked, canonical identifiers from `source_observation → as-of feature step → scaler/target → fitted model checkpoint → prediction ID → policy/order/fill → equity event → report row`. Normally save **small manifests/metrics/exception examples** only, not per-seed raw datasets or per-epoch activation dumps. Repairing a raw-price error may invalidate features/labels, affected model fits and later portfolios; repairing a pure cost bug should require **portfolio replay**, not neural retraining, if predictions are valid. Preserve the invalid results and a rerun dependency map.

---

## 16. Incremental Codex research implementation and human review

The separately approved implementation plan divides broad phases into small **human-gated work packages**, instead of one massive model-training prompt:

| Phase | Work and representative small packages | Why split it? |
|---|---|---|
| P0 | Repository/protocol inventory; environment/ledger/audit skeleton | Establish what already exists, avoid destructively replacing good code |
| P1 | Stock SIP/source; USA500 source; formation/actions/coverage | A data-source failure should not contaminate every later model |
| P2 | Calendar/as-of; real minute-label clock; FT0; USA500 features | Human can hand-check each raw-to-feature transformation before fitting |
| P3 | Prediction/physical event ledger; Policy A; Policy B/costs; emergencies/failed exits; momentum/ridge; contextual benchmarks | Portfolio dollar accounting is independently testable before LSTM fitting |
| P4 | Neural engine; calibration/refit; separate bounded TM0, MC0, MC1, E5 and conditional models | Never train all architectures in a single Codex request |
| P5 | Forecast comparison; net economics; dependence inference; finalist seed batches; targeted diagnosis; manifest lock | Deliberately slower human scientific interpretation |
| P6 | Confirmation preflight; bounded final refits; one permitted confirmation evaluation; archive/report | Protect the last out-of-sample evidence |

Every package requires a compact human report containing changed file/function paths and lines, 3–8 inspectable outputs/code locations, tests and audit status, resource/disk footprint, unresolved blockers and a concrete next-stage recommendation. **Human approval separates packages**. Model-training packages target **≤4 hours active fitting** and a safe stop/report period rather than a multiple-day autonomous architecture search. Reuse already validated data and training components; do not write a new trainer or Parquet copy for each experiment.

### A practical review example

For a first TM0 fit, a human should be able to inspect:

1. Exact 48×16 input examples and corresponding causal TG0 labels on authorized development dates.
2. Session-weighted-loss test reproducing **7, not 6** in the approved toy case.
3. Training/inner-validation loss curves, selected epoch, full-history refit and fixed seed/cutoff manifest.
4. Preclip gradient quantiles, clip fraction, finite values, output dispersion and stock-score ties.
5. Correctly joined development Rank IC and both policy A/B P&L with a one-trade physical-order trace.
6. Explicit blocked/failed checks, data retention and all created or modified files.

These are *review aids*, not proof that the model has useful alpha.

---

## 17. Status and unresolved decisions that cannot be invented

The following are **not** established merely by this appendix or by approval of a model architecture. Their status must remain visible in presentations, Codex instructions and empirical reports.

| Topic | Actual research status | Why it matters |
|---|---|---|
| USA500 identity, instrument/source and availability | **Unverified**; supplied intake report uses a provisional timestamp-as-close interpretation | MC0/MC1/U1–U5 cannot claim point-in-time causality without defensible source semantics |
| Stock source and hourly reconstruction | **Data intake reported**: 159,008 approved 30-minute SIP source bars and 09:30-hour aggregation; local repository not independently inspected here | A reported download is not a complete FT0, label or simulator audit |
| Stock-data source gaps | **168 half-hours / 15 stock-session pairs reported**, not filled | FT0 complete-window and downstream attrition must be measured |
| Genuine one-minute entry/exit execution prices | **Not established by 30-minute acquisition** | TG0 and historical physical portfolio simulation cannot substitute 30-minute price proxies |
| Formation membership, complete actions and daily corporate cash accounting | **Pending audit** | Look-ahead universe, split/dividend wealth effects |
| 240 continuous regular minutes versus four complete hourly advances | **Joint cross-track approval pending** | Changes target, clocks and cross-track comparability |
| Actual retention thresholds and M2/EMA/RSI warm-up feasibility | **Not yet computed as model-ready panels** | High data attrition may block sample and change regime mix |
| Three-family finalist cap versus SP3 full-peer control | **Conditional unresolved** if SP3 earns finalist status | Do not claim a spatial mechanism advantage without its necessary control |
| Detailed FC6 fusion, TG4 RV floor and certain AD3 edge cases | **Unresolved only for inactive optional branches** | Revisit only on justified activation; no guessed parameters |
| Formal selection-aware temporal null | **Conditional, not funded in standard 40-pair ceiling** | No search-adjusted null p-value without valid transformation and full reruns |
| A-E9 confirmation | **Not unlocked** | Cannot use July 2024–June 2025 outcomes for selecting the design |
| Actual neural model accuracy/trading results | **None reported** in the provided design discussion/data-intake reports | Do not fill this appendix with synthetic “results” or imply a strategy works |
| D7e "bullish/bearish" U5 sign after feature scaling | **Notation ambiguity in approved documents**: U5 raw log-return sign versus scaled-U5 deviation from train median | Clarify intended diagnostic threshold before labeling trends; no quiet choice or change to model inputs |

The approved A-E1 baseline details are **now** complete at the design level (D13-C07), although their implementation and empirical testing remain undone. This corrects the older presentation summary's statement that ridge and momentum parameter choices were still open.

---

## 18. Literature and technical-source guide

The works below are **research motivations and methodological precedents**, not evidence that our chosen 5-stock hourly design will generate profit or that our particular numerical thresholds are optimal. Links and bibliographic details are reproduced from the project's research notes and earlier design discussion; independently verify final bibliographic metadata before publication.

| Reference | Relevant idea used in Track A | Link |
|---|---|---|
| Fischer & Krauss (2018), *Deep Learning with Long Short-Term Memory Networks for Financial Market Predictions*, European Journal of Operational Research | Small shared cross-sectional LSTM and ranked stock predictions; precedent **not** proof of optimal depth or 4h edge | https://doi.org/10.1016/j.ejor.2017.11.054 |
| MASTER (AAAI 2024), *Market-Guided Stock Transformer for Stock Price Forecasting* | Market-dependent feature weighting and explicitly observed market context; motivates MC1/MC2 hypothesis | https://github.com/SJTU-DMTai/MASTER |
| Fan & Shen (AAAI 2024), *StockMixer: A Simple Yet Strong MLP-Based Architecture for Stock Price Forecasting* | Economical learned cross-stock exchange; motivates conditional SP3 | https://doi.org/10.1609/aaai.v38i8.28681 |
| Gu, Kelly & Xiu (2020), *Empirical Asset Pricing via Machine Learning*, Review of Financial Studies | Nonlinear interactions between predictors and cross-sectional equity outcomes | https://doi.org/10.1093/rfs/hhaa009 |
| Daniel & Moskowitz (2016), *Momentum Crashes*, Journal of Financial Economics | Market declines, volatility and changing momentum behavior; motivation for U2/U5 state diagnostics | https://doi.org/10.1016/j.jfineco.2015.12.002 |
| Moreira & Muir (2017), *Volatility-Managed Portfolios*, Journal of Finance | Absolute volatility level can be economically relevant; motivates retaining U2 instead of normalizing it away | https://doi.org/10.1111/jofi.12513 |
| Chordia & Swaminathan (2000), *Trading Volume and Cross-Autocorrelations in Stock Returns* | Motivates volume-frozen directional H→L peer test, but at different horizons | Bibliographic details in project notes; verify official paper |
| Hou (2007), *Industry Information Diffusion and the Lead-lag Effect in Stock Returns* | Information-diffusion lead–lag and important **within-industry** limitation of our across-sector five-stock sample | https://doi.org/10.1093/revfin/hhm003 |
| Loshchilov & Hutter (ICLR 2019), *Decoupled Weight Decay Regularization* | AdamW and explicit decoupling of decay from adaptive gradients | https://arxiv.org/abs/1711.05101 |
| Pascanu, Mikolov & Bengio (ICML 2013), *On the Difficulty of Training Recurrent Neural Networks* | Gradient explosion and global-norm clipping | https://proceedings.mlr.press/v28/pascanu13.html |
| Sutskever, Vinyals & Le (2014), *Sequence to Sequence Learning with Neural Networks* | Influential LSTM training with gradient clipping, demonstrates threshold need not be universal | https://arxiv.org/abs/1409.3215 |
| Goodfellow, Bengio & Courville (2016), *Deep Learning*, especially early stopping (§7.8) | Best inner-validation checkpoint then full-history refit; methodological justification | https://www.deeplearningbook.org/ |
| Prechelt (1998), *Automatic Early Stopping Using Cross Validation* | Stopping patience versus generalization/compute trade-off | https://doi.org/10.1016/S0893-6080(98)00010-0 |
| López de Prado (2018), *Advances in Financial Machine Learning* | Overlapping-label dependence, chronological leakage and purging | Book; verify exact edition/section before citation |
| Cawley & Talbot (2010), *On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation* | Architecture, hyperparameter and lucky-seed selection bias | https://www.jmlr.org/papers/v11/cawley10a.html |
| White (2000), *A Reality Check for Data Snooping* | Why backtest selection affects inferential claims | https://doi.org/10.1111/1468-0262.00152 |
| Künsch (1989), *The Jackknife and the Bootstrap for General Stationary Observations* | Resampling dependent time series in contiguous blocks | https://doi.org/10.1214/aos/1176347265 |
| Almgren & Chriss (2001), *Optimal Execution of Portfolio Transactions* | Execution price, implementation shortfall and the distinction between intended and executed trades | https://doi.org/10.21314/JOR.2001.041 |
| Gârleanu & Pedersen (2013), *Dynamic Trading with Predictable Returns and Transaction Costs* | Desired holdings versus costly trading adjustments; trading-friction motivation | Verify journal DOI in project notes |
| Novy-Marx & Velikov (2016), *A Taxonomy of Anomalies and Their Trading Costs* | Trading costs and turnover can absorb paper alpha; motivates Policy B comparison | Verify journal DOI in project notes |
| Jain & Wallace (2019), *Attention is not Explanation* | Learned attention weights require care as explanatory evidence | https://aclanthology.org/N19-1357/ |
| Kendall, Gal & Cipolla (CVPR 2018), *Multi-Task Learning Using Uncertainty to Weigh Losses for Scene Geometry and Semantics* | Auxiliary loss weights and negative transfer as a design consideration | https://openaccess.thecvf.com/content_cvpr_2018/html/Kendall_Multi-Task_Learning_Using_CVPR_2018_paper.html |
| FinPFN (discussed in project 2023–2026 paper notes) | Adaptation using recent matured feature–return relations; conceptual motivation for much simpler AD3 | https://doi.org/10.1016/j.finmar.2025.101042 |
| FactorGCL (discussed in project papers) | Factor/residual-factor interaction as a **deferred**, richer alternative | https://doi.org/10.1609/aaai.v39i1.31993 |

### Other project documents and their roles

- **Authoritative complete numeric/operational decisions:** `Track_A_Consolidated_Implementation_Design_Record_v1.2_2026-10-10.md`.
- **Frozen allowed architecture ladder and conditional scope:** `Track_A_Architecture_Experiment_Roadmap_First_Pass_FROZEN_v1.0.md`.
- **Common two-track obligations requiring mutual agreement:** `Shared_Project_Specification.md`.
- **G0–G9 audits and B0–B7 post-run replay:** `Track_A_Stage_Gated_Audit_and_Failure_Traceability_Plan_v1.1_2026-10-10.md`.
- **Small Codex packages and human checkpoints:** `Track_A_Codex_Incremental_Implementation_and_Human_Review_Plan_v1_2026-10-10.md`.
- **Earlier communication-oriented executive overview:** `Track_A_Research_Design_Presentation_Summary_2026-10-10.md` (predates the final D13-C07 baseline choices and uploaded completed data-intake report).
- **Background research menus:** `Consolidated_Architecture_Design_Menu.md`, `Modern_Quant_DL_Papers_2023_2026.md`, `Recurrent_Architecture_Research.md`, `State_Dependent_Signed_Recurrent_Interactions.md`, and `LST_Proposal.pdf`. These are sources of hypotheses, **not automatic mandates to add extra first-pass architectures**.

---

## 19. Discussion guide: how to present the scientific logic

**Question: Why use a five-stock shared LSTM instead of predicting absolute stock prices?**  
Because the initial claim is *relative short-horizon ranking*. Price levels are nonstationary and not directly comparable across tickers; FT0 largely uses scale-adjusted features, and TG0 asks whether a stock outperforms the five-name contemporaneous median. Five stocks keep audits and computation manageable, though conclusions must be qualified as a small prototype.

**Question: Why does broad-market information matter if TG0 subtracts the common cross-sectional median?**  
A shared *additive* market prediction cancels in relative ordering. But state-dependent **interactions** can alter the relevance of each stock's own features, and heterogeneous companies can respond differently to observed broad-market conditions. MC0 tests access to those states; MC1 tests an explicit mechanism that scales stock channels given the state.

**Question: What would prove the gate or spatial mixer is scientifically useful?**  
Not attractive gate weights alone, nor good training loss. Require held-out **paired improvement** against a control already given the same raw market or peer information, stable seeds/folds, mechanism sanity tests, and a transparent net-economic report. Even then the finding is predictive/architectural, not identified causality.

**Question: Why report both portfolio policies?**  
Four-hour sleeves overlap at the two daily origins. A high-Rank-IC predictor may issue quickly reversing top/bottom choices and incur net orders and transaction costs. The pure policy is the scientific fixed-horizon reference; the conflict-veto policy asks whether avoiding a narrowly defined class of reversals improves after-cost outcomes **without modifying forecasts**.

**Question: Why so many source and data tests before expensive training?**  
Off-by-one completed bars, source-publication ambiguities, high-MAD/low-MAD target issues, split mistakes and future-informed trade eligibility can create apparently excellent alpha from invalid information. Correctness must be established at the input and portfolio level before interpreting model performance.

**Question: What if a model is weaker on a twenty-stock universe?**  
First ask whether the same raw/processed input, same relative target, same peer graph and same trading costs are being compared. The twenty-stock median/MAD, sector composition and mixer dimensions change, so an apparent decline is not automatically architectural failure. Use the B0–B7 replay and the approved five-to-twenty bridge report *before* requesting new training.

**Question: Does the plan establish a statistically significant profitable strategy?**  
**No.** The source audits, labels, model runs and economic tests are not yet complete. Planned paired confidence intervals have limitations under financial dependence and prior architecture search. The expensive selection-aware temporal-null test is conditional, so the final claims must not claim that level of significance unless it is actually performed.

**Question: Which choices are scientifically central versus engineering defaults?**  
The *central hypotheses* are the controlled increments—shared sequence processing, adding market information, explicit market gating, causally lagged peer information, and possibly low-rank stock exchange. Numerical choices such as 32 hidden units, batch size 16, patience 10, 5-bps assumed execution cost and 110% emergency trigger are **predeclared, auditable defaults** selected to control complexity; they are not put forward as universal optima.

---

## Closing perspective

Track A is best understood as a **research-controlled ladder of information sets and modest architectural inductive biases**, coupled to an explicit causal historical trading simulation. Its strength will come from reproducible source-to-score-to-trade attribution, matched controls and complete reporting—including **negative, blocked and inconclusive outcomes**. The stated equations define what the project intends to test. **Whether any mechanism predicts returns or earns net alpha remains an empirical question.**
