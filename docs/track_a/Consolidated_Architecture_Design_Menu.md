# Consolidated Architecture Design Menu
## Ideas from MASTER, FactorGCL, StockMixer, FinPFN, and PRISM-VQ

Our discussions have identified several ways to improve the shared LSTM architecture for our cross-sectional equity forecasting project.

Rather than choosing an entire published model, I suggest treating the papers as a **library of architectural components**. We can choose an approach for each modeling problem, combine compatible components, and progressively develop our own architecture.

I will organize the recommendations into tables by **the problem each component is supposed to solve**, rather than organizing everything by paper.

This will make it easier to compare competing approaches.

### Our starting environment

I will use the current LSTM group proposal as the baseline:

| Property | Current project |
|---|---|
| Stock universe | Approximately 20 liquid U.S. equities, with a five-stock prototype |
| Data frequency | Hourly |
| Historical lookback | Initially 48 trading-hour observations |
| Input features | Stationary/normalized OHLCV-derived features |
| Market information | USA500; potentially USATECH and options-derived market state |
| Primary prediction | Four-hour cross-sectional relative return |
| Additional prediction | Four-hour within-sector relative return |
| Base architecture | Shared LSTM across stocks |
| Trading strategy | Long top-ranked stocks, short bottom-ranked stocks |
| Evaluation | Chronological OOS, walk-forward, transaction costs, multiple seeds, permutation tests |

The baseline model is

\[
\boxed{
\hat y_{i,t}
=
g_\psi\left(
\operatorname{LSTM}_{\theta}(X_{i,t},M_t)
\right).
}
\]

Here,

\[
X_{i,t}\in\mathbb R^{L\times d}
\]

contains stock features, while

\[
M_t\in\mathbb R^{L\times d_m}
\]

contains market features.

**Our goal is to investigate whether the architecture should include more sophisticated mechanisms for temporal learning, stock interactions, factor decomposition, market conditioning, and adaptation to changing regimes.**

The consolidated literature document explicitly identifies these as the principal transferable ideas. fileciteturn0file1L575-L623

### How to read the tables

Each suggestion has a unique identifier, such as **SP2** or **TF3**.

I will distinguish:

- **Original-paper mechanism:** A component derived relatively directly from the published architecture.
- **Adaptation:** A modification proposed for our LSTM project.
- **New alternative:** A simpler or modified approach developed during our discussions.

The recommendations are candidates, not finalized design choices.

I will also indicate which approaches I currently favor. We can override those preferences when we design the model.

---

# Table 1. Capturing spatial relationships: Inter-stock information

**Research question:** Does information about other stocks improve the prediction for a particular stock?

Our shared LSTM learns from multiple stocks through shared parameters, but it does not directly observe other stocks' histories when forecasting stock \(i\).

This is the central problem addressed by the spatial modeling proposals.

| ID | Source | Proposed method | Mathematical mechanism | Advantages | Limitations |
|---|---|---|---|---|---|
| **SP0** | Baseline | No explicit inter-stock interaction | \(h_i=\operatorname{LSTM}(X_i)\) | Simple; strong reference for measuring improvements | Cannot directly use contemporaneous histories of other stocks |
| **SP1** | MASTER-inspired suggestion 1 | Cross-stock attention using final LSTM hidden states | \(\widetilde h_i=\operatorname{Attention}(h_i,\{h_j\}_{j=1}^N)\) | Learns which stocks are relevant to each stock; attention changes with the inputs | Compresses each stock's history before mixing |
| **SP2** | MASTER-inspired suggestion 2 | Cross-stock attention at every historical time step | \(z_{i,s}=\operatorname{Attention}(h_{i,s},\{h_{j,s}\}_{j=1}^N)\) | Captures time-varying inter-stock relationships; closer to MASTER | More computation, parameters, and overfitting opportunities |
| **SP3** | StockMixer-inspired suggestion 1 | Stock-to-market-to-stock MLP mixing | \(Z=\sigma(M_1H),\;\widetilde H=H+M_2Z\) | Efficient exchange of information through a small number of learned representations | Learned stock-mixing matrices depend on stock identities and ordering |
| **SP4** | StockMixer-inspired suggestion 2 | Nonlinear pooled market representation | \(m=\operatorname{Pool}(h_1,\ldots,h_N),\;\widetilde h_i=g(h_i,m)\) | Very lightweight; can accommodate changing stock universes | A pooled representation may lose important stock-specific relationships |
| **SP5** | StockMixer + FactorGCL-inspired adaptation | Sector-wise representation pooling | \(m_s=\operatorname{Pool}_{j\in S(s)}h_j,\;\widetilde h_i=g(h_i,m_{S(i)})\) | Focuses on within-sector relationships | Only approximately four stocks per sector in our proposed universe |
| **SP6** | FactorGCL-inspired adaptation | Known-factor hypergraph aggregation | \(\widetilde H=\operatorname{HypergraphConv}(H,B)\) | Encodes known sector/factor relationships directly | Requires a well-specified factor-incidence structure; greater complexity |

**My initial preference:** Compare **SP3 (StockMixer)** and **SP1 (MASTER)** against SP0.

SP3 is particularly interesting because its intermediate market representations act as a learned bottleneck, which may reduce unnecessary flexibility in our small stock universe.

SP1 is attractive because attention weights adapt to the current stock representations.

I would reserve SP2 for a later experiment explicitly testing cross-time inter-stock relationships.

### Important implementation consideration

SP3 uses learned matrices across the stock dimension. The mapping can be sensitive to which stock occupies each position.

SP1 and SP4 are more naturally compatible with changing stock membership, provided their implementations do not add fixed position-dependent stock parameters.

Since our universe is currently small and mostly fixed, SP3 is feasible, but we should consider whether we may later expand to 50–100 stocks.

---

# Table 2. Learning temporal relationships

**Research question:** How should the model extract predictive information from the history of each stock?

Our existing LSTM already learns temporal relationships. The papers provide alternatives for improving this representation.

| ID | Source | Proposed method | Mechanism | Advantages | Limitations |
|---|---|---|---|---|---|
| **TM0** | Baseline | Standard shared LSTM | Use final LSTM hidden state \(h_{i,t}\) | Simple recurrent representation; low implementation complexity | Compresses all historical information into one state |
| **TM1** | MASTER-inspired suggestion 1 | LSTM followed by temporal attention | \(\bar h_i=\sum_s a_{i,s}h_{i,s}\) | Selectively aggregates informative historical periods | Additional attention parameters; attention weights are not causal explanations |
| **TM2** | MASTER-inspired suggestion 2 | LSTM → time-specific stock attention → final temporal attention | \(H_i\to Z_i\to \operatorname{TemporalAttention}(Z_i)\) | Closest adaptation to MASTER's temporal–spatial–temporal structure | More complex architecture; overlaps with SP2 |
| **TM3** | StockMixer-inspired suggestion 1 | Multiscale temporal representation before the LSTM | \(X_i\to\operatorname{MultiscaleMix}(X_i)\to\operatorname{LSTM}\) | Learns patterns at multiple temporal scales | May duplicate information already present in engineered returns |
| **TM4** | StockMixer-inspired suggestion 2 | Separate temporal representations at different resolutions | \(h_i^{(1)},h_i^{(4)},h_i^{(8)}\to\operatorname{Fusion}\) | Explicitly separates short- and longer-horizon patterns | Several encoders or branches may increase variance |
| **TM5** | FactorGCL-inspired adaptation | Shared LSTM trained on multiple prediction horizons | \(h_i\to(\hat r_i^{(1)},\hat r_i^{(2)},\hat r_i^{(4)})\) | May improve temporal representation through auxiliary supervision | Conflicting horizon objectives can cause negative transfer |

**My initial preference:** Keep **TM0**, and consider **TM1** as the first temporal extension.

For our application, multiscale feature engineering already supplies information from one-hour, four-hour, eight-hour, and longer return windows.

Consequently, TM3 needs to demonstrate that *learned multiscale representations* improve on those engineered features.

### Interaction between Tables 1 and 2

TM2 and SP2 are not independent modules.

Together, they define something like

\[
\boxed{
\text{LSTM}
\longrightarrow
\text{Cross-stock attention at each hour}
\longrightarrow
\text{Final temporal attention}.
}
\]

If we select TM2, we are also selecting a particular spatial mechanism.

We should not treat the rows as entirely independent architectural decisions.

---

# Table 3. Using market information: USA500 and market regimes

**Research question:** How should broad-market information influence the stock prediction model?

MASTER provides the strongest motivation for this dimension.

Our current approach simply concatenates USA500 features with the stock features.

The alternatives allow market information to modify how stock features are processed.

| ID | Source | Proposed method | Mechanism | Advantages | Limitations |
|---|---|---|---|---|---|
| **MC0** | Baseline | Concatenate USA500 with stock features | \(\operatorname{LSTM}([X_i,M])\) | Simple, economical, clean baseline | The model must learn useful market-feature interactions implicitly |
| **MC1** | MASTER-inspired suggestion 1 | Market-guided feature gating | \(\widetilde x_{i,s}=\alpha(m_t)\odot x_{i,s}\) | Explicitly makes feature importance depend on market conditions | Can suppress useful features; gate regularization matters |
| **MC2** | MASTER-inspired suggestion 2 | Time-varying market-guided gating | \(\widetilde x_{i,s}=\alpha(m_s)\odot x_{i,s}\) | Allows feature relevance to vary across the historical sequence | Different from the closest MASTER adaptation; more flexibility |
| **MC3** | MASTER-inspired adaptation | Market-conditioned LSTM hidden-state gating | \(\widetilde h_i=h_i\odot\sigma(W_m m_t+b)\) | Conditions learned representations rather than raw input indicators | Hidden units may be harder to interpret |
| **MC4** | FinPFN-inspired adaptation | Market state plus recent predictor-performance state | \(\hat y_i=g(h_i,m_t,e_t)\) | Adapts to both market conditions and recent predictive success | Requires leakage-safe historical performance information |
| **MC5** | PRISM-VQ-inspired suggestion | Discrete latent market-state conditioning | \(q(m_t)=e_{k^*},\;\hat y_i=g(h_i,q(m_t))\) | Finite regime representations may constrain model flexibility | Quantization can discard useful continuous information |
| **MC6** | PRISM-VQ-inspired adaptation | Mixture-of-experts conditioning | \(\hat y_i=\sum_k\pi_k(m_t)f_k(h_i)\) | Different expert mappings for different states | Experts can overfit or collapse; higher capacity |

**My initial preference:** Compare **MC1 (MASTER)** against MC0.

The main research question becomes:

\[
\boxed{
\text{Is USA500 more useful when it controls feature relevance}
}
\]

rather than merely appearing as another input variable?

The original MASTER notes explicitly identify market-guided feature gating as one of the highest-priority adaptations. fileciteturn0file1L41-L107

**Important distinction:** MC5 and MC6 are based on the PRISM-VQ ideas described in the original `.md` file. They are conceptual LSTM adaptations, not direct implementations of PRISM-VQ's complete VQ-VAE and mixture-of-experts architecture.

---

# Table 4. Factor decomposition: Market, sector, hidden factors, and individual alpha

**Research question:** Can we improve stock predictions by separating common market movements, sector movements, and stock-specific information?

This is primarily motivated by **FactorGCL and PRISM-VQ**.

It is especially relevant because our project considers both cross-sectional and within-sector prediction.

| ID | Source | Proposed method | Mechanism | Advantages | Limitations |
|---|---|---|---|---|---|
| **FC0** | Baseline | No explicit factor decomposition | \(\hat y_i=g(h_i)\) | Simple; lets the LSTM learn predictive relationships freely | Does not distinguish common factors from stock-specific information |
| **FC1** | FactorGCL-inspired suggestion 1 | Sector-relative prediction target | \(y_i^S=r_i^{(4)}-r_{S(i)}^{(4)}\) | Directly studies within-sector outperformance | Changes the prediction objective rather than introducing learned factors |
| **FC2** | FactorGCL-inspired suggestion 2 | Historical factor-model residual target | \(y_i^\alpha=r_i^{(4)}-\hat\beta_i^\top r_F^{(4)}\) | Tests prediction of returns unexplained by specified factors | Factor estimates may be noisy; forecast target depends on factor-model assumptions |
| **FC3** | FactorGCL-inspired suggestion 3 | Separate common-factor and stock-specific prediction heads | \(\hat r_i=f_{\mathrm{common}}(h_i,M)+f_{\mathrm{specific}}(h_i)\) | Explicitly allocates model capacity to two prediction components | Components are not identifiable without additional constraints |
| **FC4** | FactorGCL-inspired suggestion 4 | Prior-factor hypergraph after LSTM | \(E^P=\operatorname{HypergraphConv}(H,B)\) | Aggregates information according to predefined factor exposures | Greater complexity; requires factor specifications |
| **FC5** | FactorGCL-inspired suggestion 5 | Learned nonlinear hidden-factor module | \(B^H_{ik}=\sigma(h_i^\top c_k)\), followed by factor aggregation | Learns previously unspecified common stock relationships | Hidden factors may overfit and need not be economically identifiable |
| **FC6** | FactorGCL + StockMixer-inspired adaptation | Nonlinear market/sector representations | \(m=\operatorname{Pool}(H),\;m_s=\operatorname{Pool}(H_s),\;\widetilde h_i=g(h_i,m,m_s)\) | Lightweight way to model common and sector information | Does not provide a formal factor decomposition |
| **FC7** | PRISM-VQ-inspired suggestion 1 | Financial factor priors | Supply market, sector, trend, and volatility factors to a structured model | Introduces useful financial inductive biases | Priors can be incomplete or inappropriate |
| **FC8** | PRISM-VQ-inspired suggestion 2 | Dynamic factor loadings | \(\hat r_{i,t}=\sum_k\beta_{ik,t}\hat f_{k,t}+\hat\alpha_{i,t}\) | Allows exposures to vary with market conditions | Factor forecasts, exposures, and residuals require careful specification and regularization |
| **FC9** | PRISM-VQ-inspired suggestion 3 | Quantized latent factors | \(z_t\to q(z_t)\), followed by factor-conditioned prediction | Bounded set of learned factor representations | Quantization adds training complexity and may lose information |

### Mathematical interpretation of FC8

FC8 deserves particular attention because it connects FactorGCL and PRISM-VQ.

A traditional linear factor model might assume

\[
r_{i,t}
=
\sum_{k=1}^{K}\beta_{ik}f_{k,t}
+
\alpha_{i,t}.
\]

The exposures \(\beta_{ik}\) are often treated as fixed over a chosen estimation window.

A dynamic nonlinear model could instead use

\[
\boxed{
\hat r_{i,t}^{(4)}
=
\sum_{k=1}^{K}
\underbrace{\beta_{ik,t}}_{\text{Dynamic factor loading}}
\underbrace{\hat f_{k,t}^{(4)}}_{\text{Predicted factor contribution}}
+
\underbrace{\hat\alpha_{i,t}^{(4)}}_{\text{Stock-specific prediction}}.
}
\]

The factor loadings could depend on the LSTM representations:

\[
\beta_{ik,t}
=
g_k(h_{i,t},m_t).
\]

This is an attractive research direction because it combines nonlinear stock representations with an economically structured prediction.

However, **this mathematical expression is a proposed LSTM adaptation, not the exact PRISM-VQ model**.

The original notes describe PRISM-VQ as combining expert financial priors, discrete latent factors, structure-conditioned experts, and time-varying loadings. They recommend borrowing these ideas before attempting its entire two-stage system. fileciteturn0file1L378-L435

### My initial preference

I would separate two questions:

**Question A: What should we predict?**

Compare FC0, FC1, and potentially FC2.

These concern prediction targets and can be investigated without adding complex factor-learning modules.

**Question B: Should we explicitly learn factors?**

Compare FC6 against a model incorporating FC7 and eventually FC5 or FC8.

I would not begin with FC3 alone because its apparent market/individual decomposition is mathematically non-identifiable without extra structure.

I also would not immediately combine FC4, FC5, FC8, and FC9. That would introduce several overlapping factor-learning mechanisms before determining whether any one is useful.

---

# Table 5. Adapting to changing predictive relationships

**Research question:** Can the model learn when previously useful predictors stop working?

This is the principal idea we discussed from **FinPFN**.

It differs from merely conditioning on market volatility or identifying a market regime.

Two periods with similar market volatility might have different momentum–return relationships.

| ID | Source | Proposed method | Mechanism | Advantages | Limitations |
|---|---|---|---|---|---|
| **AD0** | Baseline | Fixed trained LSTM | \(\hat y_i=f_\theta(X_i,M)\) | Simple; stable parameters between retraining periods | Does not explicitly adapt to recent prediction success |
| **AD1** | FinPFN-inspired suggestion 1 | Recent predictive-performance features | \(\hat y_i=g(h_i,e_t)\), where \(e_t\) contains recent IC, bias, errors, etc. | Lightweight; easily combined with LSTM | Recent performance estimates are noisy |
| **AD2** | FinPFN-inspired suggestion 2 | Recent-performance gating | \(\widetilde h_i=h_i\odot\sigma(W_e e_t+b)\) | Allows recent success/failure to change how representations are used | Assumes a compact summary of performance is sufficient |
| **AD3** | FinPFN-inspired suggestion 3 | Rolling regularized prediction head | \(\hat w_t=\arg\min_w\sum_{s\in\mathcal C_t}\omega_s(y_s-w^\top h_s)^2+\lambda\|w-w_0\|^2\) | Explicit adaptation with relatively few parameters | Rolling estimates can be unstable; requires causal refitting |
| **AD4** | FinPFN-inspired suggestion 4 | LSTM + attention over recent labeled examples | \(c_i=\operatorname{CrossAttention}(h_i,\{(h_j,y_j)\}_{\mathrm{past}})\) | Directly learns which historical feature–return relationships matter | Additional neural capacity; label-availability complications |
| **AD5** | FinPFN-inspired suggestion 5 | Pretrained/fine-tuned FinPFN benchmark | \(\hat y=F_\theta(X_{\mathrm{context}},y_{\mathrm{context}},X_{\mathrm{query}})\) | Tests whether PFN pretraining offers an advantage under limited data | Domain, feature, horizon, and data-format mismatch may require substantial adaptation |
| **AD6** | PRISM-VQ-inspired adaptation | State-dependent mixture of experts | \(\hat y_i=\sum_k\pi_k(m_t)f_k(h_i)\) | Different prediction functions under different learned states | Learns state-dependent mappings, but does not explicitly use recent realized predictor success |

### My recommendation: AD3 is an important baseline

During our FinPFN discussion, I proposed **AD3**, a rolling regularized regression head applied to frozen LSTM representations.

It is valuable because it allows us to test whether recent relationships matter without introducing a second neural network.

Then AD1 and AD2 ask whether the neural model can exploit that information more effectively.

Finally, AD4 tests a richer form of adaptation that is closer to FinPFN's in-context learning idea.

An attractive experimental progression is

\[
\boxed{
AD0\longrightarrow AD3\longrightarrow AD1/AD2\longrightarrow AD4.
}
\]

AD5 should be considered a separate model-family benchmark, not a mandatory component of our LSTM.

### Critical timing requirement

Our primary target spans four trading hours.

At decision time \(t\), historical labels can enter the adaptive model only after those outcomes are observable.

With a suitable trading-hour index, the basic condition is

\[
\boxed{s+4\le t.}
\]

The implementation must additionally account for actual bar completion and session boundaries.

This is especially important for AD1–AD5. Any recent IC, forecast error, or labeled context must be constructed causally.

For AD1 and AD2, performance statistics should also be based on appropriate historical predictions rather than optimistically evaluating a model on the same labels used to fit it.

---

# Table 6. Learning discrete market states and regimes

**Research question:** Should the model represent market conditions continuously, or learn a finite collection of latent states?

This table is primarily based on the original PRISM-VQ recommendations.

| ID | Source | Proposed method | Mechanism | Advantages | Limitations |
|---|---|---|---|---|---|
| **RG0** | Baseline | Continuous USA500 market features | \(m_t\in\mathbb R^{d_m}\) | Preserves continuous information | Does not explicitly constrain the model to a small set of regimes |
| **RG1** | MASTER-inspired adaptation | Continuous market-dependent gating | \(\widetilde x_i=\alpha(m_t)\odot x_i\) | Feature relevance can change smoothly with market conditions | Requires learning the state-to-feature relationship |
| **RG2** | PRISM-VQ-inspired suggestion 1 | Vector-quantized market representation | \(q(z_t)=e_{\arg\min_k\|z_t-e_k\|^2}\) | Finite codebook constrains latent capacity | Discrete states may introduce information loss |
| **RG3** | PRISM-VQ-inspired suggestion 2 | Quantized states followed by different experts | \(\hat y_i=f_{q(z_t)}(h_i)\) | Allows different predictors for different latent states | Hard expert assignment can be unstable |
| **RG4** | PRISM-VQ-inspired suggestion 3 | Structure-conditioned mixture of experts | \(\hat y_i=\sum_k\pi_k(z_t)f_k(h_i)\) | Smooth combination of specialized predictors | More parameters and potentially weakly identified expert roles |
| **RG5** | PRISM-VQ-inspired suggestion 4 | Dynamic factor loadings conditioned on discrete representations | \(\beta_{ik,t}=g_k(h_i,q(z_t))\) | Connects regime learning with changing factor exposure | Combines two difficult estimation problems |

The motivation from PRISM-VQ is that a finite codebook may impose a useful inductive bias in a noisy financial environment.

However, **discrete does not automatically mean interpretable**.

If a model learns eight latent states, they need not correspond to identifiable bull markets, bear markets, volatility regimes, or liquidity states.

The states may simply represent patterns that happen to reduce the training loss.

### My initial preference

Keep RG0 initially.

If we want to test regime-dependent feature importance, RG1 is the more economical first experiment.

RG2 is an interesting later alternative, especially if continuous market conditioning proves unstable.

I would not begin with RG3–RG5 because our approximately 20-stock universe may provide limited evidence for learning multiple specialized prediction functions.

**Compatibility note:** RG1 and MC1 describe closely related versions of MASTER-style market gating. Likewise, RG3–RG4 overlap with MC6 and AD6. They should not be counted as separate modules merely because they appear under different research questions.

---

# Table 7. Financial indicators and input representations

**Research question:** Should the model receive predefined financial indicators directly, or learn transformations and interactions among them before temporal processing?

This dimension draws primarily from MASTER, StockMixer, and PRISM-VQ.

| ID | Source | Proposed method | Mechanism | Advantages | Limitations |
|---|---|---|---|---|---|
| **FT0** | Baseline | Direct normalized financial inputs | Feed returns, volatility, volume, momentum, etc. into LSTM | Simple and interpretable information set | Relationships among indicators must be learned implicitly |
| **FT1** | MASTER-inspired suggestion | Market-guided indicator weighting | \(\widetilde x_{i,s}=\alpha(m_t)\odot x_{i,s}\) | Financial indicators can have regime-dependent relevance | Repeats MC1; should be implemented once |
| **FT2** | StockMixer-inspired suggestion 1 | Learned nonlinear indicator mixing | \(z_{i,s}=\operatorname{MLP}_{\mathrm{indicator}}(x_{i,s})\) | Explicit feature-interaction representation | Adds capacity before the LSTM |
| **FT3** | StockMixer-inspired suggestion 2 | Multiscale feature/time mixing | \(Z_i=\operatorname{Mix}_{\mathrm{time,feature}}(X_i)\) | Learns transformations jointly across indicators and temporal scales | May duplicate LSTM memory and engineered indicators |
| **FT4** | PRISM-VQ-inspired suggestion | Incorporate financial factor priors | Include or structurally encode known market, sector, momentum, and risk factors | Introduces economically motivated structure | Requires careful distinction between inputs, exposures, and predicted factor returns |

FT2 is an interesting option because it changes how the LSTM sees the input.

Instead of

\[
x_{i,s}\longrightarrow\operatorname{LSTM},
\]

we use

\[
\boxed{
x_{i,s}
\longrightarrow
\operatorname{IndicatorMLP}
\longrightarrow
\operatorname{LSTM}.
}
\]

The indicator MLP could learn nonlinear combinations of momentum, volume, and volatility.

However, our LSTM already applies nonlinear transformations to its inputs. Therefore, FT2 needs to demonstrate an incremental advantage rather than merely add parameters.

**My initial preference:** FT0, with FT1 as the principal market-conditioned extension. FT2 is a secondary experiment.

---

# Table 8. Prediction targets and multi-task learning

**Research question:** What should the network learn to predict, and can additional prediction tasks improve the representation used for our four-hour target?

FactorGCL is the principal inspiration here, although some options come from our existing project proposal rather than the five papers.

| ID | Source | Proposed method | Mathematical objective | Advantages | Limitations |
|---|---|---|---|---|---|
| **TG0** | Current project | Four-hour cross-sectional relative return | \(y_{i,t}^{CS}=(r_{i,t}^{(4)}-\operatorname{Median}_j r_{j,t}^{(4)})/(\operatorname{MAD}_j r_{j,t}^{(4)}+\epsilon)\) | Directly targets relative outperformance | Noisy; normalization depends on cross-sectional dispersion |
| **TG1** | FactorGCL-inspired suggestion 1 | Four-hour within-sector relative return | \(y_{i,t}^{S}=r_{i,t}^{(4)}-r_{S(i),t}^{(4)}\) | Focuses on relative performance within sectors | Each sector contains relatively few stocks |
| **TG2** | FactorGCL-inspired suggestion 2 | Multi-horizon return prediction | \(\mathcal L=\lambda_1\mathcal L_{1h}+\lambda_2\mathcal L_{2h}+\lambda_4\mathcal L_{4h}\) | Auxiliary prediction tasks may improve temporal representation | Negative transfer; overlapping labels |
| **TG3** | FactorGCL-inspired extension | Include an eight-hour prediction head | Add \(\lambda_8\mathcal L_{8h}\) | Tests whether longer-horizon information benefits four-hour forecasts | Requires an explicit overnight/multi-session labeling convention |
| **TG4** | Current project extension | Return + future realized-volatility prediction | \(\mathcal L=\lambda_r\mathcal L_r+\lambda_v\mathcal L_{\mathrm{RV}}\) | Tests whether volatility learning improves alpha representations or risk scaling | Return and volatility tasks may compete |
| **TG5** | FactorGCL + PRISM-VQ-inspired adaptation | Common-factor and stock-specific auxiliary objectives | \(\mathcal L=\mathcal L_{\mathrm{return}}+\lambda_f\mathcal L_{\mathrm{factor}}+\lambda_\alpha\mathcal L_{\mathrm{specific}}\) | Can encourage structurally meaningful representations | Auxiliary factor labels and constraints must be defined |

### My recommendation

Keep **TG0 as the primary Track A target** and **TG1 as the separate Track B target**.

The first multi-task experiment I would prioritize is TG2.

For example,

\[
\boxed{
\mathcal L
=
0.2\mathcal L_{1h}
+
0.2\mathcal L_{2h}
+
0.6\mathcal L_{4h}.
}
\]

These weights are illustrative, not finalized recommendations.

The question is whether learning shorter-horizon returns improves the shared LSTM's representation for the four-hour target.

TG4 is another useful experiment, particularly because we already plan to investigate realized-volatility prediction. It should be tested separately from TG2 initially.

**One distinction:** TG0/TG1 specify the main prediction problem; TG2–TG5 specify possible auxiliary learning objectives. We may eventually select one primary target and one auxiliary training scheme, rather than treating all these options as mutually exclusive.

---

# Table 9. Controlling complexity and overfitting

**Research question:** Which mechanisms can improve generalization when our stock universe is small and financial returns contain weak predictive signals?

This is particularly relevant to FactorGCL, StockMixer, and PRISM-VQ.

| ID | Source | Proposed method | How it controls complexity | Potential drawback |
|---|---|---|---|---|
| **CP0** | Current project | Compact LSTM, dropout, early stopping | Limits model capacity and overtraining | May underfit genuine relationships |
| **CP1** | FactorGCL-inspired suggestion | Bounded hidden-size exploration | Compare \(d_h\in\{32,64,128\}\) | Hidden width alone does not control all sources of complexity |
| **CP2** | StockMixer-inspired suggestion | Low-dimensional stock-to-market bottleneck | Use \(m\ll N\) intermediate representations | Important relationships may be lost |
| **CP3** | MASTER-inspired adaptation | Limit attention heads and dimensions | Begin with small attention modules | May underrepresent complex interactions |
| **CP4** | PRISM-VQ-inspired suggestion | Discrete latent codebook | Restricts latent representations to learned prototypes | Codebook collapse or loss of predictive information |
| **CP5** | PRISM-VQ-inspired adaptation | Small number of factor components or experts | Limits the number of distinct learned prediction mechanisms | Too few components may be restrictive |
| **CP6** | FactorGCL-inspired adaptation | Restrict learned hidden-factor count | Avoid an excessively flexible latent-factor representation | Optimal factor count may vary over time |
| **CP7** | FinPFN-inspired adaptation | Shrink recent estimates toward historical coefficients | Regularized rolling adaptation | Excessive shrinkage prevents useful adaptation |

These are not necessarily competing choices. They are controls that accompany particular architectural modules.

For example, choosing SP3 would naturally introduce CP2.

Choosing SP1 or SP2 would introduce CP3.

Choosing RG2 would introduce CP4.

**My recommendation is to prefer architectural regularization initially**, such as small hidden dimensions and compact stock-mixing modules, rather than relying on dropout alone to control an unnecessarily large system.

---

# Table 10. Training architecture and implementation strategy

**Research question:** Should the components be trained separately, jointly, or through pretraining and fine-tuning?

This matters when combining ideas originating in substantially different models.

| ID | Source | Training approach | Recommended use |
|---|---|---|---|
| **TR0** | Current LSTM | Train the shared LSTM and prediction head jointly | Baseline |
| **TR1** | MASTER-inspired adaptation | Jointly train LSTM, market gate, and cross-stock attention | Natural implementation of MASTER-inspired extensions |
| **TR2** | StockMixer-inspired adaptation | Jointly train LSTM and stock-mixing MLP | Natural implementation of StockMixer-inspired extensions |
| **TR3** | FactorGCL-inspired adaptation | Jointly train LSTM, factor aggregation, and prediction heads | Appropriate if explicit nonlinear factor learning is selected |
| **TR4** | FinPFN-inspired adaptation | Freeze or periodically update LSTM embeddings; adapt a rolling prediction head | Useful inexpensive test of changing predictor relationships |
| **TR5** | FinPFN-inspired adaptation | Jointly train LSTM and a small attention module over historical labeled examples | More ambitious context-based learning |
| **TR6** | FinPFN original-model option | Evaluate pretrained FinPFN, with carefully controlled fine-tuning if appropriate | Separate benchmark rather than a required LSTM component |
| **TR7** | PRISM-VQ-inspired option | Two-stage representation learning followed by predictor training | Advanced experiment; closer to the original PRISM-VQ training philosophy |

For the majority of our initial experiments, **joint end-to-end training is the simplest approach**.

That means the LSTM, stock-mixing module, market gate, and prediction head can all receive gradients from the same loss function.

We do not need to train MASTER, StockMixer, or FactorGCL independently and feed their outputs into the LSTM.

The main exceptions are FinPFN's pretrained-model approach and PRISM-VQ's original two-stage training scheme.

---

# Table 11. Validation and interpretation

These are not architecture choices in the same sense as the preceding tables. They are necessary comparisons for determining whether a new module is useful.

| ID | Inspired by | Proposed test | What it establishes |
|---|---|---|---|
| **EV1** | MASTER | Stock-only vs stock + USA500 vs market-gated LSTM | Whether market data helps, and whether gating adds value beyond concatenation |
| **EV2** | MASTER / StockMixer | No mixing vs attention vs stock-to-market mixing | Whether explicit cross-stock information helps |
| **EV3** | MASTER | Final-state mixing vs time-dependent mixing | Whether preserving time-specific stock interactions matters |
| **EV4** | FactorGCL | Universe-relative vs sector-relative targets | Whether the prediction problem changes when sector effects are removed |
| **EV5** | FactorGCL | Single-horizon vs multi-horizon learning | Whether auxiliary return horizons improve four-hour prediction |
| **EV6** | FactorGCL / PRISM-VQ | Known factors vs additional learned factors | Whether latent common representations add predictive information |
| **EV7** | FinPFN | Fixed prediction mapping vs recent-performance conditioning | Whether adapting to recently observed predictor relationships helps |
| **EV8** | PRISM-VQ | Continuous state vs discrete state vs mixture of experts | Whether explicit state structure improves robustness |
| **EV9** | All five | Walk-forward, multiple seeds, costs, and null testing | Whether improvements survive realistic evaluation |

There is one additional diagnostic I would include when testing cross-stock models.

**Cross-stock information destruction test:** Keep a stock's own history and the market information intact, but disrupt the alignment of information from other stocks using a carefully constructed null transformation.

This can help distinguish useful inter-stock information from additional model flexibility.

Such tests must respect market dependence and timestamp structure; independently shuffling stock observations would not necessarily produce a valid null.

---

# 12. Architecture selection table

We now have a component menu. The next step is to select a combination.

The table below summarizes the principal architecture decisions in a form we can use when designing our model.

| Architectural dimension | Candidate methods | My provisional first choice | Later alternative |
|---|---|---|---|
| **1. Input feature representation** | FT0, FT1, FT2, FT3 | FT0: normalized financial features | FT2: indicator MLP |
| **2. Market conditioning** | MC0, MC1, MC2, MC3, MC5, MC6 | MC0 baseline, then MC1: MASTER gating | MC3: hidden-state gating |
| **3. Temporal modeling** | TM0, TM1, TM2, TM3, TM4 | TM0: shared LSTM | TM1: temporal attention |
| **4. Inter-stock relationships** | SP0–SP6 | Compare SP3 and SP1 against SP0 | SP2: time-dependent attention |
| **5. Factor structure** | FC0–FC9 | FC0 initially; FC6 as first factor-aware extension | FC5 or FC8 |
| **6. Regime representation** | RG0–RG5 | RG0: continuous state | RG2: discrete latent states |
| **7. Regime adaptation** | AD0–AD6 | AD0 initially; AD3 and AD1 as first tests | AD4: attention over labeled context |
| **8. Prediction targets** | TG0–TG5 | TG0 for Track A; TG1 for Track B | TG2: multi-horizon learning |
| **9. Complexity control** | CP0–CP7 | CP0 and small-capacity settings appropriate to selected modules | Learned-factor/codebook restrictions |
| **10. Training strategy** | TR0–TR7 | Joint end-to-end training | Separate adaptation or pretraining where justified |

**These ten dimensions are not completely independent.** Some options implement the same mechanism at different locations, and others presuppose a particular earlier choice.

For example, choosing SP2 and TM2 commits us to a joint spatiotemporal attention structure. Choosing FC8 and RG5 creates a coupled dynamic-factor model.

This table should therefore be treated as an architecture-design menu with compatibility constraints, not a Cartesian product of interchangeable modules.

---

# 13. How I would assemble our first research architecture

There are many possible combinations, but I would initially investigate a relatively compact model combining three of the strongest ideas:

- MASTER's market-dependent feature selection.
- Our existing shared LSTM for temporal representation.
- StockMixer's stock-to-market-to-stock information exchange.

The proposed architecture is

\[
\boxed{
\begin{aligned}
\text{Stock features }X_{i,t}
&\\[-2pt]
\text{USA500 market features }M_t
&\longrightarrow
\text{Market-guided feature gate}
\\
&\downarrow\\
&\text{Shared LSTM}\\
&\downarrow\\
&\text{StockMixer-style stock mixing}\\
&\downarrow\\
&\text{Prediction head}\\
&\downarrow\\
&\hat y_{i,t}^{(4)}.
\end{aligned}
}
\]

More explicitly:

### Step 1: Market-guided gating

Compute

\[
\alpha_t
=
d\operatorname{softmax}
\left(
\frac{W_m m_t+b_m}{\tau}
\right).
\]

Then

\[
\widetilde X_{i,t}
=
X_{i,t}\odot\alpha_t,
\]

where the gate is broadcast across the historical lookback.

### Step 2: Shared LSTM

Compute

\[
h_{i,t}
=
\operatorname{LSTM}_{\theta}(\widetilde X_{i,t}).
\]

We obtain

\[
H_t\in\mathbb R^{N\times D}.
\]

### Step 3: StockMixer-style mixing

Compute

\[
Z_t
=
\sigma\left(
M_1\operatorname{LayerNorm}(H_t)
\right)
\]

and

\[
\widetilde H_t
=
H_t+M_2Z_t.
\]

### Step 4: Prediction

For each stock,

\[
\boxed{
\hat y_{i,t}^{(4)}
=
g_\psi(\widetilde h_{i,t}).
}
\]

This gives us a relatively compact architecture that combines market-guided feature weighting, recurrent temporal representation learning, and explicit cross-stock information exchange.

**I would regard this as a candidate architecture, not our finalized model.**

In particular, we should establish the incremental usefulness of market gating and stock mixing separately before claiming that their combination is better.

---

# 14. How to develop the architecture progressively

I would avoid immediately implementing every promising mechanism.

A more informative strategy is to build several nested models.

| Stage | Architecture | Research question |
|---|---|---|
| **A0** | Shared LSTM, stock features only | Can pooled recurrent learning predict relative returns? |
| **A1** | Shared LSTM + USA500 concatenation | Does broad-market conditioning improve prediction? |
| **A2** | Shared LSTM + MASTER feature gating | Does market-dependent feature weighting improve over concatenation? |
| **A3** | A2 + StockMixer stock mixing | Does explicit cross-stock information add value? |
| **A4** | A2 + MASTER cross-stock attention | Is dynamic attention preferable to MLP-based mixing? |
| **A5** | Best supported model + FactorGCL multi-horizon objective | Does auxiliary temporal supervision improve four-hour forecasts? |
| **A6** | Best supported model + factor-aware representation | Do market, sector, and stock-specific representations improve prediction? |
| **A7** | Best supported model + FinPFN-inspired adaptation | Do recently realized predictor relationships provide additional information? |
| **A8** | Best supported model + PRISM-VQ-inspired discrete state or dynamic factor module | Does explicit latent-state/factor structure improve robustness? |

At A3 and A4, we should compare the alternatives using the same starting backbone and comparable tuning budgets.

We should not necessarily stack StockMixer mixing and MASTER attention together. Initially, they are competing ways to solve the same spatial-information problem.

Likewise, A6–A8 are research branches rather than mandatory sequential additions.

The extensions should be retained only if they provide convincing incremental evidence.

---

# 15. Important interactions between the five papers

Some recommendations are particularly interesting when combined.

| Combination | Proposed interaction | Potential research contribution |
|---|---|---|
| **MASTER + StockMixer** | Market-guided gating followed by stock-to-market mixing | Tests whether market-dependent indicator relevance and cross-stock information are complementary |
| **MASTER + FactorGCL** | Market-conditioned LSTM with known-factor aggregation | Tests whether market information and sector/factor structure contribute independently |
| **StockMixer + FactorGCL** | Learned stock-mixing representations combined with sector-aware information | Tests whether unrestricted cross-stock learning adds information beyond predefined sector relations |
| **MASTER + FinPFN** | Market gating plus recent predictive-performance conditioning | Tests whether market state alone explains changing feature relevance |
| **FactorGCL + FinPFN** | Recent performance state controlling factor exposures or prediction heads | Tests whether factor predictability changes in ways that recent outcomes can identify |
| **FactorGCL + PRISM-VQ** | Known factors, learned latent factors, and dynamic loadings | More structured nonlinear factor modeling |
| **MASTER + PRISM-VQ** | Market-guided feature gating conditioned on learned discrete states | Tests continuous versus discrete control of indicator relevance |
| **StockMixer + PRISM-VQ** | Compact learned stock mixing combined with discrete latent market/factor representations | Tests whether factor-like bottlenecks provide complementary regularization |

These are proposed combinations, not results demonstrated by the corresponding papers.

I find **MASTER + StockMixer** the most practical near-term combination.

**FactorGCL + PRISM-VQ** is a more ambitious research direction because it would move the project toward an explicitly structured nonlinear factor model.

**MASTER + FinPFN** may offer the most interesting experiment about adaptation under changing market conditions.

---

# 16. My overall assessment

The five papers contribute somewhat different things:

| Paper | Most useful immediate contribution | Most interesting advanced contribution |
|---|---|---|
| **MASTER** | Market-guided feature gating | Time-dependent cross-stock attention |
| **FactorGCL** | Factor-adjusted/sector-relative targets and multi-horizon learning | Known and learned nonlinear factor representations |
| **StockMixer** | Efficient stock-to-market-to-stock mixing | Learned multiscale temporal and cross-stock structure |
| **FinPFN** | Recent predictive-performance conditioning | In-context adaptation through historical labeled examples |
| **PRISM-VQ** | Financial priors and bounded latent-factor capacity | Vector-quantized states, dynamic factor loadings, and mixtures of experts |

My preference would be to **preserve the LSTM as the central temporal encoder** while treating all other components as individually testable additions.

The architecture should develop around three questions:

1. **Which information should the model observe?** Own-stock history, USA500, other stocks, sectors, known factors, and realized historical prediction outcomes.
2. **How should the model combine that information?** Concatenation, market gating, temporal attention, stock mixing, hypergraph aggregation, or context-based adaptation.
3. **What should the model learn?** Four-hour relative returns, sector-relative returns, multiple return horizons, volatility, or explicitly factor-adjusted returns.

These questions should be answered through controlled experiments rather than by assuming that a more elaborate architecture is better.

### Suggested next step

We can now use the architecture selection table as our **design notebook**.

I suggest making the decisions in this order:

**Input representation → Market conditioning → Temporal modeling → Spatial relationships → Factor structure → Regime representation → Adaptation → Prediction heads → Regularization → Training.**

For each dimension, we can discuss the available methods, their mathematical and statistical trade-offs, and then select an option.

Once the choices are settled, we can assemble them into a coherent architecture and check compatibility, computational requirements, leakage risks, and whether each component has a clearly defined research purpose.

**No architecture choices have been frozen by this synthesis.**
