# Can redesigned recurrent cells replace specialized financial modules?

## 1. Executive verdict

**The core hypothesis is partly correct—and the strongest version of it concerns structured recurrence, not simply adding more gates.**

A modest recurrent model can plausibly perform several functions that your earlier architecture menu assigned to separate modules: infer persistent market conditions, change how it processes indicators, maintain information at different timescales, and combine stock-specific observations with common market information. Those functions do not inherently require a Transformer, hypergraph, vector-quantized codebook, or mixture of experts.

However, three different issues must not be conflated:

\\[ \boxed{ \text{Information available} \\;\neq\\; \text{Functions representable} \\;\neq\\; \text{Functions learnable reliably}. } \\]

A larger LSTM can help with the second issue. A better structured cell can help with the third. Neither can repair the first without receiving additional observations.

Your current setting—approximately 20 stocks, hourly observations, a preliminary 48-observation lookback, and four-hour relative-return targets—is an appropriate setting for testing economical architectures, but not for assuming that the benefits reported for much larger daily panels will transfer. The uploaded prompt explicitly leaves that setting open to revision.    Pasted markdown

### What survives scrutiny

**A standard LSTM already has substantial conditional-processing capacity.** Its gates depend jointly on current inputs and past hidden states. Therefore, a market-conditioned LSTM can learn different responses to momentum, volume, or volatility in different environments. An additional “regime gate” is not automatically a new capability.

**Partitioned and interacting memories have a more defensible motivation than indiscriminately adding gates.** They can impose sparse information pathways, preserve separate slow and fast states, and avoid allocating a separate copy of the common market state to every stock. There is substantial precedent for interacting, multidimensional, multiscale, and modular recurrent systems, although their empirical successes do not validate this financial application. [arXiv](https://arxiv.org/pdf/1507.01526)

**External controllers can be coherent, but “another model trains the gates” is not a complete method.** A controller must either supply inputs or gate activations, generate parameters, optimize a stated auxiliary objective, or participate in a well-defined joint or bilevel learning problem. HyperNetworks and recurrent filtering systems provide established examples of such interfaces. [arXiv](https://arxiv.org/pdf/1609.09106)

### What does not survive scrutiny

A stockwise LSTM receiving only its own history and USA500 cannot recover arbitrary unobserved peer innovations. Sharing parameters across stocks is not sharing observations.

A standard feature-only LSTM also does not automatically reproduce FinPFN’s adaptation mechanism. Adaptation to recently successful predictor–outcome relationships requires access to **completed labels, historical predictions, or sufficient statistics derived from them**. Market-state inference and performance-state inference are different problems. FinPFN explicitly conditions on recent feature–return pairs. [sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S1386418125000825?utm_source=chatgpt.com)

Neither an LSTM state nor a learned “factor” embedding is automatically an identifiable economic factor. Likewise, a discrete code does not automatically identify a market regime.

### Two particularly important corrections to the earlier menu

First, the proposed pooled update

\\[ \widetilde h\_{i,t}=h\_{i,t}+W_m m_t \\]

can be **incapable of changing cross-sectional rankings** when followed by a shared linear prediction head. The common additive contribution cancels in every pairwise score difference. That illustrative update appears in the prior literature notes.    Modern_Quant_DL_Papers_2023_2026

Second, PRISM-VQ’s discrete objects are principally **stock-level representations of cross-sectional structure**, not simply a single global bull/bear regime variable. Turning it into a quantized USA500 controller is a substantial adaptation, not a lightweight implementation of the original mechanism. [arXiv](https://arxiv.org/html/2605.13407v1)

### My ranked assessment

| Research objective                                  | Best current hypothesis                                                                                |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Lowest-risk immediate test                          | Shared LSTM and ridge models with the same compact market, sector, and peer summaries                  |
| Most promising parsimonious integrated architecture | A shared global state interacting with stock-local memories                                            |
| Most informative custom-cell experiment             | Partitioned memories, first without communication and then with controlled low-rank recurrent coupling |
| Most defensible first adaptive mechanism            | A frozen encoder with a shrunk rolling prediction head or an explicit coefficient filter               |
| Higher-upside exploratory direction                 | Selective recurrent communication driven by current peer innovations and delayed feedback              |
| Lowest immediate priority                           | A large combination of extra gates, hidden factors, quantization, recurrent experts, and meta-learning |

These are **theoretically motivated hypotheses**, not demonstrated performance rankings.

Throughout the report, I use four evidence labels:

**Mathematically established** means derived under stated assumptions.\
**Supported by existing research** means supported in the cited paper’s setting.\
**Theoretically motivated hypothesis** means a coherent but unverified prediction for this application.\
**Speculative** means the supporting mechanism or evidence remains weak.

The five-paper audit uses original papers, publication records, and available author code. For FinPFN, I verified the publisher-accessible description and official training/data code, but did not obtain unrestricted access to the entire journal article. No financial experiments or numerical replications were performed.

---

## 2. LSTM mechanism analysis

### 2.1 Correct equations and terminology

For \\(x_t\in\mathbb R^d\\), a conventional modern LSTM with width \\(H\\) has

\\[ \begin{aligned} i_t&=\sigma(W_i x_t+U_i h\_{t-1}+b_i),\\\ f_t&=\sigma(W_f x_t+U_f h\_{t-1}+b_f),\\\ u_t&=\tanh(W_u x_t+U_u h\_{t-1}+b_u),\\\ c_t&=f_t\odot c\_{t-1}+i_t\odot u_t,\\\ o_t&=\sigma(W_o x_t+U_o h\_{t-1}+b_o),\\\ h_t&=o_t\odot\tanh(c_t). \end{aligned} \\]

Here \\(i_t,f_t,o_t,u_t,c_t,h_t\in\mathbb R^H\\).

There are **three named gates**, a candidate update \\(u_t\\), and two state vectors. There are not three independent memories. The modern forget-gate formulation also incorporates developments subsequent to the original 1997 LSTM paper. [direct.mit.edu](https://direct.mit.edu/neco/article/9/8/1735/6109/Long-Short-Term-Memory)

A coordinate \\(c\_{t,k}\\) might retain a slow signal while another coordinate responds to a short-lived shock. But there is no built-in rule assigning one coordinate to “volatility” and another to “momentum.”

### 2.2 What the cell can store

Unrolling one coordinate gives

\\[ c\_{t,k} = \left(\prod\_{v=1}^{t}f\_{v,k}\right)c\_{0,k} + \sum\_{s=1}^{t} \left[ i\_{s,k}u\_{s,k} \prod\_{v=s+1}^{t}f\_{v,k} \right]. \\]

**Mathematically established:** the direct memory contribution of an old write is controlled by subsequent forget gates.

For a constant forget value \\(f\in(0,1)\\), the e-folding timescale is

\\[ \tau=-\frac{1}{\log f}. \\]

Thus \\(f=0.9\\) corresponds to approximately \\(9.5\\) observations, while \\(f=0.99\\) corresponds to approximately \\(99.5\\). These are memory-path calculations—not claims about the actual predictive horizon learned by a fitted model.

For an initial timescale \\(\tau\\), a corresponding forget bias is

\\[ b_f=\operatorname{logit}(e^{-1/\tau}), \\]

when other contributions to the forget preactivation initially vanish. Time-scale-aware initialization has a theoretical connection to gated recurrence, but does not guarantee that training will preserve the intended timescale. [arXiv](https://arxiv.org/abs/1804.11188)

### 2.3 The forget-gate product is not the complete gradient

It is common to write

\\[ \frac{\partial c_t}{\partial c\_{t-1}}\approx\operatorname{diag}(f_t). \\]

That identifies the direct carry path. It is not generally the full derivative of the recurrent system, because \\(h\_{t-1}\\) influences the gates and candidate update.

For the complete state \\(s_t=(c_t,h_t)\\),

\\[ \frac{\partial s_t}{\partial s\_{t-k}} = J_tJ\_{t-1}\cdots J\_{t-k+1}, \qquad J_t=\frac{\partial s_t}{\partial s\_{t-1}}. \\]

Consequently, gates close to one do not guarantee stable gradients; nor does bounded hidden output guarantee well-conditioned learning. Gradient clipping addresses excessively large gradient updates, not all causes of unstable internal dynamics. [Proceedings of Machine Learning Research](https://proceedings.mlr.press/v28/pascanu13.html)

A further subtlety: individual transition matrices having eigenvalues inside the unit disk is not, by itself, enough to control arbitrary products of changing, noncommuting matrices. A uniform induced-norm bound is a stronger sufficient condition, but strong contraction can conflict with long memory.

### 2.4 Width, layers, streams, and lookback are different resources

| Modification                | What changes                                              | What does not automatically change                       |
| --------------------------- | --------------------------------------------------------- | -------------------------------------------------------- |
| Increase width \\(H\\)      | More state coordinates and denser interactions            | Available observations                                   |
| Add layers                  | Greater compositional depth at each temporal step         | Direct peer access                                       |
| Add separate streams        | Explicit memory allocation and routing constraints        | Total information, unless streams receive different data |
| Add recurrent coupling      | Information exchange during state evolution               | Correctness of learned relationships                     |
| Increase lookback \\(L\\)   | More historical observations available to the forecast    | Ability to learn which history matters                   |
| Carry state between windows | Potential access to history preceding the explicit window | Length of gradient propagation under truncated training  |

If each 48-observation window begins from a reset state, the model cannot retain information preceding that window except through features that already summarize earlier history.

A stateful model with truncated backpropagation is different: it may carry older information forward even though gradients are stopped at truncation boundaries.

### 2.5 Parameter and computational scaling

With one bias vector per gate/candidate map,

\\[ \boxed{P\_{\mathrm{LSTM}}(d,H)=4H(d+H+1).} \\]

A scalar linear head adds \\(H+1\\) parameters.

For a stacked model,

\\[ P=\sum\_{\ell=1}^{D} 4H\_\ell(d\_\ell+H\_\ell+1), \qquad d\_{\ell}=H\_{\ell-1}\ \text{for }\ell>1. \\]

For \\(N\\) stocks, one shared stockwise LSTM still has \\(P\_{\mathrm{LSTM}}\\) parameters, but maintains \\(N\\) distinct state pairs.

Ignoring constant factors,

\\[ \text{sequence compute} = O\\!\left(BNLH(d+H)\right), \\]\\[ \text{stored training activations} = O(BNLH). \\]

For illustration, with \\(d=24\\):

| Width    | Recurrent parameters |
| -------- | -------------------- |
| \\(16\\) | \\(2{,}624\\)        |
| \\(32\\) | \\(7{,}296\\)        |
| \\(64\\) | \\(22{,}784\\)       |

These are calculations, not proposed final settings.

A joint flattened model receiving all stocks has input dimension \\(Nd\\):

\\[ P\_{\mathrm{joint}}=4J(Nd+J+1). \\]

It provides direct cross-stock access, but a fixed-dimensional state \\(J\\) becomes a shared bottleneck. If \\(J\\) is increased proportionally to \\(N\\), recurrent parameter growth becomes quadratic in \\(N\\).

### 2.6 What additional gates do—and do not—provide

Suppose another gate multiplies the existing write:

\\[ c_t=f_t\odot c\_{t-1} + a_t\odot i_t\odot u_t. \\]

This does not create another memory. It introduces a more structured parameterization of the effective write control.

Although \\(a_ti_t\\) is an effective gate, a product of two sigmoid-affine functions is not generally another sigmoid-affine function. Therefore, “the new gate can be algebraically absorbed” does **not** imply exact equivalence to a same-width conventional LSTM.

The appropriate conclusion is narrower:

> Extra gates may change the function class or its parameterization, but they do not automatically create an important new capability, improve optimization, or reduce estimation variance.

A broad empirical study of LSTM variants found that several modifications did not consistently outperform the standard formulation across its tested sequence tasks. That supports demanding strong ablations, not treating the conventional cell as universally optimal. [DOI](https://doi.org/10.48550/arXiv.1503.04069)

---

## 3. Capability-versus-access matrix

Let “stockwise” mean that each stock is processed separately using shared weights.

| Desired functionality                 | Own history only                         | Add market/sector history            | Add peer summaries         | Add joint observations or recurrent messages | Add completed labels                                   |
| ------------------------------------- | ---------------------------------------- | ------------------------------------ | -------------------------- | -------------------------------------------- | ------------------------------------------------------ |
| Own-stock temporal patterns           | Available in principle                   | Available                            | Available                  | Available                                    | Not necessary                                          |
| Slow market-state inference           | Only through own-stock proxies           | Directly supported by inputs         | Additional proxies         | Richer panel evidence                        | Sometimes informative                                  |
| Regime-dependent indicator processing | Limited to observable regime proxies     | Available in principle               | Available                  | Available                                    | Helps when regime is about predictor success           |
| Common sector effects                 | Indirect                                 | Available through sector inputs      | Available                  | Available                                    | Not necessary                                          |
| Arbitrary peer-specific innovation    | Generally unavailable                    | Still unavailable                    | Only if summary retains it | Available                                    | Historical labels do not reveal current missing shocks |
| Fixed peer lead–lag relation          | Generally unavailable                    | Only through a proxy                 | Possible                   | Possible                                     | Not necessary                                          |
| Changing predictor–outcome mapping    | Only if changes are signaled by features | Same limitation                      | Same limitation            | Same limitation                              | Direct evidence becomes available after maturity       |
| Economic factor identification        | Not guaranteed                           | Requires definitions and constraints | Still not guaranteed       | Still not guaranteed                         | Still requires identification                          |
| Calibrated predictive uncertainty     | Not supplied by hidden state alone       | Same                                 | Same                       | Same                                         | Requires a probabilistic objective and calibration     |

### A precise information-access result

Let \\(\mathcal F_t\\) contain own-stock and market observations. Let \\(\mathcal G_t\supseteq\mathcal F_t\\) additionally contain peer observations.

Under squared loss,

\\[ \begin{aligned} &\mathbb E\\!\left[(Y-\mathbb E[Y\mid\mathcal F_t])^2\right] - \mathbb E\\!\left[(Y-\mathbb E[Y\mid\mathcal G_t])^2\right]\\\ &\qquad= \mathbb E\\!\left[ \left( \mathbb E[Y\mid\mathcal G_t] - \mathbb E[Y\mid\mathcal F_t] \right)^2 \right] \geq0. \end{aligned} \\]

**Mathematically established:** additional information can lower Bayes risk. Increasing network width while leaving \\(\mathcal F_t\\) unchanged cannot eliminate the missing-information term.

For example,

\\[ Y\_{i,t+1}=b\varepsilon\_{j,t}+\eta\_{i,t+1}, \\]

where \\(\varepsilon\_{j,t}\\) is independent of \\(\mathcal F_t\\). A model restricted to \\(\mathcal F_t\\) cannot predict that component, regardless of gate count.

Conversely, if a controller \\(q_t=C(m\_{\leq t})\\) is a deterministic function of history already available to a model, it adds no new information **conditional on that full history**. Its benefit must come from compression, prior structure, optimization, or external training—not newly observed market information.

That qualification matters when the controller sees five years of history while the baseline sees only 48 observations. Such a comparison is not purely architectural.

---

## 4. Original-paper mechanism audit

### 4.1 MASTER: market-guided feature processing and temporal–spatial exchange

**Supported by existing research.** MASTER uses a market-conditioned feature gate of the form

\\[ \alpha(m_t) = d\\,\operatorname{softmax}\\!\left( \frac{W_m m_t+b_m}{\tau} \right), \qquad \widetilde x\_{i,s}=\alpha(m_t)\odot x\_{i,s}. \\]

The latest market state conditions the whole observed lookback. The architecture then uses intra-stock temporal attention, cross-stock attention on temporally enriched representations, and temporal aggregation. Its stock experiments are daily and substantially larger than the proposed panel. [AAAI Publications](https://ojs.aaai.org/index.php/AAAI/article/download/27767/27575)

**Assessment.** A conventional LSTM receiving \\([x\_{i,s};m_s]\\) can learn market-dependent processing. The external gate makes a specific restriction explicit: market conditions modulate raw feature channels before subsequent transformations.

That is an inductive bias, not proof that concatenation lacks the relevant capacity.

#### The fair comparison

The earlier menu contrasts concatenation with gated stock features. Those are not necessarily nested information-preserving models.    Consolidated_Architecture_Desig…

A cleaner experiment is

\\[ \begin{aligned} \text{Baseline: }&[x\_{i,s};m_s],\\\ \text{Gated: }&[\alpha(m_t)\odot x\_{i,s};m_s]. \end{aligned} \\]

Both retain direct market information. Uniform \\(\alpha=\mathbf1\\) recovers the baseline input transformation.

#### Latest-state gating is not automatically leakage

At forecast time \\(t\\), all \\(m_t\\) and \\(x\_{i,s}\\), \\(s\leq t\\), may be available. Reweighting historical observations using the current state is then causal **at the endpoint**.

But it is not equivalent to an online state that processed each observation once using the state available then. Changing \\(m_t\\) requires recomputing the window if the gate applies retrospectively.

Thus

\\[ \alpha(m_t)x\_{i,s} \quad\text{versus}\quad \alpha(m_s)x\_{i,s} \\]

tests **current-context reinterpretation** versus **historically conditioned encoding**, not simply “causal versus noncausal.”

**Implementation caution.** MASTER’s official repository documents a validation-preprocessing issue involving inappropriate use of a learning processor. The authors state that their reported checkpoints/results were unaffected because stopping used a training-loss threshold. This is a reason to audit reproduction pipelines, not evidence that I independently verified that assertion. [GitHub](https://github.com/SJTU-DMTai/MASTER)

---

### 4.2 StockMixer: efficient cross-stock communication, not generic mean pooling

**Supported by existing research.** StockMixer combines indicator mixing, multiscale temporal mixing, and stock-to-market-to-stock mixing. A central operation has the structure

\\[ H'=H+M_2\sigma(M_1\operatorname{LN}(H)), \\]

with \\(M_1\in\mathbb R^{q\times N}\\), \\(M_2\in\mathbb R^{N\times q}\\). The original output construction also retains the original representation. Experiments use daily NASDAQ, NYSE, and S&P 500 panels, not a 20-stock hourly setting. [AAAI Publications](https://ojs.aaai.org/index.php/AAAI/article/download/28681/29322)

**Assessment.** This is not equivalent to taking one market mean. Different rows of \\(M_2\\) can route different common representations to different stocks.

The economical transferable idea is a **communication bottleneck**. It should not automatically be called an economic factor model.

#### A mathematical problem with the earlier pooled adaptation

If

\\[ \widetilde h_i=h_i+W_m m, \qquad \hat y_i=w^\top\widetilde h_i+b, \\]

then

\\[ \hat y_i-\hat y_j=w^\top(h_i-h_j). \\]

**Mathematically established:** the common pooled contribution cannot change pairwise rankings for fixed upstream representations.

The same issue arises within a sector when all stocks receive the same sector offset.

Valid alternatives include

\\[ \hat y_i=g(h_i,m) \\]

with genuinely interactive nonlinear fusion, or

\\[ \hat y_i=w^\top h_i+\beta(h_i)^\top m. \\]

The second expression allows heterogeneous sensitivities to the common state.

A common additive branch may still influence joint training through regularization or loss fitting. That is different from directly using peer information to alter rankings at inference.

---

### 4.3 FactorGCL: recurrent encoding already exists inside the model

**Supported by existing research.** FactorGCL uses a GRU encoder, known-factor hypergraph aggregation, learned hidden-factor aggregation on residual embeddings, and a final residual branch. In consistent notation,

\\[ E_r=E_s-E_p,\qquad B^h\_{ik}=\sigma(E\_{r,i}^{\top}c_k), \\]\\[ E_h=\operatorname{HyperGCN}(E_r,B^h),\qquad E\_\alpha=\operatorname{LeakyReLU}(W\_\alpha(E_s-E_p-E_h)+b\_\alpha). \\]

It sums prediction heads and trains multiple forward horizons. Its temporal contrastive construction uses past/future residual representations during training. [arXiv](https://arxiv.org/html/2502.05218v1)

**Assessment.** “Can an LSTM replace FactorGCL?” is too coarse. Replacing the GRU is straightforward. Replacing the hypergraph requires preserving the common-information exchange or accepting its removal.

There are at least five distinct things to compare:

\\[ \begin{array}{ll} \text{Implicit nonlinear features} & \text{ordinary recurrent state},\\\ \text{Common-information exchange} & \text{pooling/messages/joint inputs},\\\ \text{Residual target construction} & \text{a different supervised task},\\\ \text{Dynamic exposures} & \text{a structured prediction map},\\\ \text{Identifiable economic factors} & \text{additional restrictions}. \end{array} \\]

The previous notes already warn that two additive heads are not identifiable. That warning should remain central.    Modern_Quant_DL_Papers_2023_2026

For

\\[ \hat r=Bf+\alpha, \\]

any invertible \\(R\\) gives

\\[ Bf=(BR)(R^{-1}f). \\]

Moreover, without restrictions on \\(\alpha\\), common and residual contributions can be reassigned.

**Mathematically established:** predictive fit alone does not identify the factor interpretation.

Useful restrictions include anchored observed factors, specified exposure structures, rank constraints, and residual orthogonality such as

\\[ B^\top W\alpha=0. \\]

Even these do not automatically identify a unique economic interpretation for learned latent factors.

Using future observations in a training-only contrastive objective is not intrinsically leakage. The decisive requirement is that every such future window remains inside the permitted training information. It also does not prove that the residual representation is economically idiosyncratic rather than, for example, a stable stock-identity representation.

---

### 4.4 PRISM-VQ: discrete cross-sectional structure, not merely market regimes

**Supported by existing research.** PRISM-VQ first encodes each stock with a GRU, applies cross-asset processing, assigns stock embeddings to codewords, and learns reconstruction/auxiliary prediction objectives. A second stage uses code-conditioned temporal processing and experts to generate loadings:

\\[ \hat y_i = \alpha_i+\beta\_{p,i}^{\top}f_p+\beta\_{l,i}^{\top}f\_{l,i}. \\]

The codebook is fixed after the first stage, while stock assignments may change. The experiments concern daily CSI 300 and S&P 500 data. The paper is in IJCAI 2026. [arXiv](https://arxiv.org/html/2605.13407v1)

**Correction to the prior framing.** The proposed adaptation

\\[ m_t\longrightarrow q(m_t)\longrightarrow\text{LSTM conditioning} \\]

changes the object being quantized. The original concerns cross-sectional stock structure, not solely a global market state. The notes label that construction an adaptation, but its distance from the original deserves greater emphasis.    Modern_Quant_DL_Papers_2023_2026

**Assessment.** A continuous recurrent bottleneck can perform some useful functions of discrete codes: compression, information sharing, and state-dependent conditioning. It does not impose a finite prototype set unless explicitly constrained.

Discrete states are potentially useful when recurring types genuinely exist and enough data support each type. They can hurt when exposures drift smoothly, assignments are unstable, or the codebook is unnecessarily large.

Two interpretive cautions follow directly from the mechanism:

- Freezing a codebook prevents subsequent codebook changes; it does not retrospectively prevent poor learning or collapse during its estimation.
- A contrastive objective based on distances to assigned prototypes encourages geometric separation. That alone does not establish economic semantics.

The smallest credible test is **continuous versus discrete conditioning with otherwise matched inputs and prediction capacity**, not a simultaneous addition of quantization, experts, new factors, and auxiliary losses.

---

### 4.5 FinPFN: adaptation through labeled context

**Supported by existing research.** FinPFN conditions predictions on recent feature–return relationships and trains a financial prior using real financial data. Its official code fine-tunes a TabPFN-based model and constructs past-date labeled context with a later query date. The publisher reports daily Chinese and monthly U.S. experiments; LightGBM remains stronger in the overall U.S. comparison. The striking reported Chinese long–short Sharpe is explicitly before transaction costs. [sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S1386418125000825?utm_source=chatgpt.com)

**Assessment.** The conceptual distinction is

\\[ \underbrace{\hat y_t=f\_\theta(x\_{\leq t})}\_{\text{feature-state inference}} \qquad\text{versus}\qquad \underbrace{\hat y_t=F\_\theta(\\{(x_s,y_s)\\}\_{s\in\mathcal C_t},x_t)}\_{\text{relationship inference}}. \\]

A recurrent network could implement the second type of computation, but only if its inputs and training protocol support it.

#### Strict label maturity

Let \\(a(s)\\) be the actual availability time of the label attached to forecast origin \\(s\\). Then

\\[ \boxed{\mathcal C_t=\\{s:a(s)\leq t\_{\mathrm{decision}}\\}.} \\]

For a four-hour target, \\(s+4\leq t\\) is only shorthand under a correctly defined trading-time index. Entry lag, bar completion, the closing stub, overnight policy, missing prices, and cross-sectional label construction can change the actual availability time.

A four-observation horizon is not necessarily four complete hours.

#### Honest errors are issued-forecast errors

A performance state should use

\\[ e_s=y_s-\hat y_s^{\\,\mathrm{issued}}, \\]

where \\(\hat y_s^{\\,\mathrm{issued}}\\) was actually available at \\(s\\).

It should not use

\\[ y_s-f\_{\theta\_{\mathrm{new}}}(x_s) \\]

when \\(\theta\_{\mathrm{new}}\\) was fitted using \\(y_s\\). The latter is an in-sample reconstruction of historical performance.

#### A strong simpler comparator

For frozen embeddings \\(h_s\\),

\\[ w_t = \arg\min_w \left[ \sum\_{s\in\mathcal C_t}\omega\_{t,s}(y_s-w^\top h_s)^2 + \lambda\\|w-w_0\\|^2 \right]. \\]

Therefore,

\\[ w_t= \left(\sum_s\omega\_{t,s}h_sh_s^\top+\lambda I\right)^{-1} \left(\sum_s\omega\_{t,s}h_sy_s+\lambda w_0\right). \\]

This directly adapts the mapping with relatively few parameters. It is a more decisive first benchmark than immediately meta-training a feedback LSTM.

There is also an important filtering subtlety: a label arriving at \\(t\\) may measure a coefficient state at origin \\(s\<t\\). An exact time-varying-coefficient filter must handle that delayed measurement through state augmentation or an out-of-sequence update. Treating it as a measurement of the current coefficient is an approximation that requires sufficiently slow coefficient drift.

---

## 5. Broader literature: what transfers and what does not

The following evidence is relevant, but none establishes the best architecture for the present hourly panel.

| Literature family                                     | Established mechanism or finding                                                                                            | Relevant limitation                                                                                                                                                                                                                     |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LSTM variant comparisons                              | Gate/cell alterations have been compared systematically; added complexity did not consistently dominate across tested tasks | Speech, handwriting, and music results are not financial evidence. [DOI](https://doi.org/10.48550/arXiv.1503.04069)                                                                                                                     |
| Grid LSTM                                             | Separate memories along different computational axes, with interacting hidden representations                               | Supports separate memory pathways, not a particular stock/sector partition. [arXiv](https://arxiv.org/pdf/1507.01526)                                                                                                                   |
| Clockwork and hierarchical multiscale RNNs            | Different modules update at different rates; some models learn update boundaries                                            | Financial regimes are not necessarily periodic or cleanly segmented. [Proceedings of Machine Learning Research](https://proceedings.mlr.press/v32/koutnik14)                                                                            |
| Phased LSTM                                           | An additional time gate controls whether states update                                                                      | Strongest motivation concerns event-driven or irregular sampling. [proceedings.neurips.cc](https://proceedings.neurips.cc/paper/2016/hash/5bce843dd76db8c939d5323dd3e54ec9-Abstract.html)                                               |
| ConvLSTM and graph recurrence                         | Structured operators replace dense input/state transformations                                                              | An image grid or road network supplies structure that ticker ordering does not. [NeurIPS Papers](https://papers.nips.cc/paper/2015/hash/07563a3fe3bbe7e3ba84431ad9d055af-Abstract.html)                                                 |
| Relational memory and RIMs                            | Memories communicate through attention; modular systems can update selectively                                              | Their generalization evidence does not establish stable financial relationships. [arXiv](https://arxiv.org/abs/1806.01822)                                                                                                              |
| HyperNetworks                                         | A smaller network generates or modulates another network’s weights                                                          | Conditional weights can introduce substantial capacity and instability. [arXiv](https://arxiv.org/pdf/1609.09106)                                                                                                                       |
| Recurrent Kalman networks and deep state-space models | Learned representations or recurrent parameter generators are combined with explicit filtering                              | Probabilistic meaning depends on the state-space assumptions. [Proceedings of Machine Learning Research](https://proceedings.mlr.press/v97/becker19a.html)                                                                              |
| xLSTM and selective state-space models                | Altered memory structures, normalization, and input-selective transitions                                                   | Large-sequence/language evidence does not demonstrate small-panel financial superiority. [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2024/hash/c2ce2f2701c10a2b2f2ea0bfa43cfaa3-Abstract-Conference.html) |
| Financial adaptive learning                           | Time-varying predictive regressions and DoubleAdapt explicitly address changing relationships                               | Different horizons, information sets, and evaluation protocols remain material. [sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S0304405X12000633)                                                                |

### Evidence under limited effective data

The strongest general conclusion is not “RNNs beat attention” or its reverse. It is that architectural rankings depend heavily on information sets, preprocessing, target, and evaluation.

For example, simple linear forecasting models have outperformed the compared Transformer systems on several general long-horizon forecasting benchmarks. That does not show that attention is intrinsically inappropriate for financial panels. [AAAI Publications](https://ojs.aaai.org/index.php/AAAI/article/view/26317)

Conversely, pooled recurrent modeling has strong financial precedent in large-scale order-book data, including cross-stock generalization. That evidence involves a much richer information source and far larger datasets than hourly OHLCV indicators. [arXiv](https://arxiv.org/abs/1803.06917)

**Evidence gap:** I did not find a decisive, controlled study that matches the present combination of small equity panel, hourly relative-return prediction, equal information access, parameter-matched custom cells, comparable tuning, delayed feedback, and realistic costs.

That missing comparison is a legitimate research opportunity.

---

## 6. Architecture alternatives

Let \\(X\in\mathbb R^{B\times L\times N\times d}\\), market inputs \\(M\in\mathbb R^{B\times L\times d_m}\\), and local states \\(H_t\in\mathbb R^{N\times H}\\). “BPTT” means backpropagation through time.

The custom candidates below are formalized in Section 13.

| Candidate                                      | Inputs and main operation                                            | Capacity/scaling                                                            | Expected advantage                                        | Principal failure mode                                           | Training                                                               |
| ---------------------------------------------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------- | --------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **A0. Lagged ridge / compact MLP**             | Lagged own, market, sector, peer features                            | Ridge linear in feature count; MLP depends on width                         | Strong low-variance comparator                            | Misses complex path dependence                                   | Closed-form/iterative regression or ordinary backpropagation           |
| **A1. Shared rich-input LSTM**                 | \\(h\_{i,t}=\mathrm{LSTM}(z\_{i,t},h\_{i,t-1},c\_{i,t-1})\\)         | \\(4H(d_z+H+1)\\); \\(N\\) state pairs                                      | Few architectural assumptions                             | Information compressed into one state; difficult interactions    | BPTT                                                                   |
| **A2. Market-conditioned input gate**          | \\([\alpha(m_t)x\_{i,s};m_s]\\)                                      | Adds approximately \\(d(d_m+1)\\)                                           | Shared, explicit feature modulation                       | Suppresses information; redundant with ordinary conditioning     | BPTT                                                                   |
| **A3. Extra-write single memory**              | \\(c=f c^-+iu+\gamma g_pu_p\\)                                       | Extra candidate and gate maps; no extra state dimension                     | Separate write pathway for a specific information family  | Write competition, saturation, unnecessary flexibility           | BPTT                                                                   |
| **A4. Independent partitioned memories**       | Separate cells for input families, then nonlinear fusion             | Sum of smaller-cell parameter counts                                        | Enforced memory allocation                                | Cross-family interactions occur too late                         | BPTT                                                                   |
| **A5. Recurrently coupled memories**           | Gate preactivations receive low-rank messages from other states      | Adds low-rank off-block maps                                                | Online conditional interactions                           | Coupling destroys useful separation or learns unstable relations | BPTT                                                                   |
| **A6. Global–local hierarchy**                 | Shared global state updates once; local stock states condition on it | Global parameters plus one shared local cell; state \\(G+NH\\)              | Common-state sharing and local specialization             | Common bottleneck erases idiosyncratic peer information          | BPTT                                                                   |
| **A7. LSTM plus final-state mixing/attention** | Encode separately, then mix \\(H_t\\)                                | Low-rank mixing \\(O(NqH)\\); attention \\(O(N^2H)\\), plus projections     | Simple way to test peer access                            | Relevant temporal detail already discarded                       | BPTT                                                                   |
| **A8. Dynamic factor/state-space model**       | \\(r_t=B_tf_t+\epsilon_t,\ f_t=Af\_{t-1}+\eta_t\\)                   | Small factor dimension; filtering cost depends on covariance structure      | Explicit shrinkage and uncertainty                        | Misspecified factors/linear dynamics                             | Likelihood, EM, filtering; optional neural components                  |
| **A9. Filter-controlled recurrent weights**    | Filtered state \\(\pi_t\\) modulates low-rank recurrent parameters   | Base LSTM plus low-rank generator and filter                                | Smooth conditional dynamics with explicit state estimator | Controller error and duplicated capacity                         | Separate filter estimation plus BPTT, or joint differentiable training |
| **A10. Recurrent mixture of experts**          | Several recurrent states, routed or combined outputs                 | Roughly \\(K\\) cell parameter sets and states                              | Different recurrent dynamics for distinct environments    | Expert starvation, stale states, scarce regime data              | BPTT; hard routing needs special treatment                             |
| **A11. Feedback-adaptive recurrent system**    | Completed \\((h_s,y_s)\\), issued errors, rolling statistics         | From \\(O(H^2)\\) regression statistics to a second learned recurrent model | Adapts to changing predictor success                      | Delayed/noisy feedback, optimistic training errors               | Rolling regression/filtering or episodic meta-training                 |

For A10, three designs must be separated:

\\[ (h_t^k,c_t^k)=\mathrm{Cell}\_k(z_t,h\_{t-1}^k,c\_{t-1}^k), \qquad \hat y_t=\sum_k\pi_k(m_t)g_k(h_t^k) \\]

maintains every expert’s history.

Hard selective updating leaves inactive expert states unchanged. Those states can become stale.

A single state updated by a mixture of expert transitions is different again:

\\[ s_t=\sum_k\pi_k(m_t)F_k(s\_{t-1},z_t). \\]

It does not retain independent expert memories.

Before maintaining several recurrent experts, test a cheaper mixture of output heads on one encoder. Otherwise, an apparent “regime memory” gain may only be a benefit from a conditional readout.

---

## 7. Design trade-offs and mapping to the existing menu

### 7.1 Which components duplicate one another?

| Existing IDs  | Relationship                                                  | Recommended interpretation                                                     |
| ------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| MC1, RG1, FT1 | Essentially the same market-guided feature mechanism          | Implement once                                                                 |
| SP2, TM2      | Joint temporal–spatial processing choices                     | Do not count them as independent additions                                     |
| SP4/SP5, FC6  | Common/sector aggregation under different descriptions        | One communication mechanism, not two factor modules                            |
| MC6, AD6, RG4 | Overlapping state-conditioned expert mechanisms               | Separate from actual labeled-feedback adaptation                               |
| FC1/TG1       | Target definition                                             | Not evidence that the architecture learned factors                             |
| FC2           | Factor-adjusted labels                                        | Requires historical exposure estimation and a separate economic interpretation |
| AD3/TR4/CP7   | Rolling head, training protocol, and shrinkage                | One coherent adaptive baseline                                                 |
| FC9/RG2/CP4   | Quantization viewed as factors, regimes, and capacity control | One bottleneck with several possible interpretations                           |

These overlaps are already partly acknowledged in the menu and should remain explicit.    Consolidated_Architecture_Desig…    Consolidated_Architecture_Desig…

### 7.2 Which components complement one another?

**Potential complements:** market context and peer innovations; common-state memory and stock-local memory; a frozen encoder and a shrunk adaptive readout; observed factor anchors and a small residual predictor.

**Initial competitors:** final attention versus stock mixing; continuous versus discrete state conditioning; rolling-head adaptation versus a feedback LSTM; independent partitions versus recurrently coupled partitions.

**Combinations to postpone:** quantized states plus multiple recurrent experts plus dynamic factor loadings; both learned graphs and unrestricted attention; simultaneous target changes and custom-cell changes.

### 7.3 Where should a controller act?

Let \\(q_t\\) denote a filtered or learned state.

| Location          | Example                                | What changes                      | Main risk                                             |
| ----------------- | -------------------------------------- | --------------------------------- | ----------------------------------------------------- |
| Inputs            | \\(\tilde x=\alpha(q)x\\)              | Which raw signals enter           | Information suppression                               |
| Writes            | \\(c=f c^-+g(q)\odot i\odot u\\)       | Whether new information is stored | Lost shocks                                           |
| Forget rates      | \\(f=\sigma(a_f+C_fq)\\)               | Memory persistence                | Incorrectly erasing useful history                    |
| Messages          | \\(\mu=g(q)\odot\mathrm{Message}(H)\\) | Inter-stock information flow      | Disabling useful relationships                        |
| Readout           | \\(\hat y=g(h,q)\\)                    | How existing state is interpreted | Insufficient when state already discarded information |
| Recurrent weights | \\(U(q)=U_0+\Delta U(q)\\)             | State transition itself           | Highest instability/capacity risk                     |

**Theoretically motivated hypothesis:** start with readout or input conditioning when the problem appears to be changing interpretation of existing information. Escalate to write/forget control only when diagnostics indicate that the wrong information is being retained.

A volatility increase does not logically imply that memory should be forgotten faster. Increased **observation noise** can justify slower updating; increased **latent-state drift** can justify faster updating. A controller should distinguish these possibilities.

### 7.4 FiLM, conditional normalization, and hypernetworks are not identical

FiLM applies

\\[ \tilde h=\gamma(q)\odot h+\beta(q). \\]

Its conditioning principle has established precedent, originally demonstrated in visual reasoning. [AAAI Publications](https://ojs.aaai.org/index.php/AAAI/article/view/11671)

A positive sigmoid gate can suppress or amplify within its range, but cannot itself reverse a feature’s sign. A signed \\(\gamma\\), a conditional candidate update, or different prediction heads can represent sign reversals.

A gate-bias adjustment

\\[ W x+U h+Cq+b \\]

is **exactly equivalent to concatenating \\(q\\)** into that gate’s input.

In contrast,

\\[ U(q)h \\]

creates explicit interactions between the controller and the prior hidden state. It is not merely a new additive input.

### 7.5 A parameter-count correction

Applying the same attention module at every historical step does not multiply its parameter count by \\(L\\).

For fixed total attention width, shared per-step attention increases compute and stored activations approximately from

\\[ O(N^2H+NH^2) \\]

to

\\[ O(LN^2H+LNH^2), \\]

but can use the same projection parameters.

Therefore, the menu’s suggestion that per-step attention necessarily has more parameters than final-step attention is too strong. More parameters arise only if additional or untied transformations are introduced.    Consolidated_Architecture_Desig…

---

## 8. Ranked research directions

### Best immediate low-risk test

**Shared LSTM versus ridge, with identical engineered peer and market information.**

The purpose is to determine whether missing information—not insufficient cell sophistication—explains the baseline limitation. Include relative returns, sector summaries, dispersion, and a small number of lagged peer summaries.

**Retain complexity only when it improves the same-information comparison.**

### Best parsimonious integrated architecture

**A shared global state with local stock memories, initially without learned arbitrary stock-to-stock edges.**

The mechanism is economical: estimate common dynamics once, then let local gates respond differently to that state. The principal unresolved question is whether this structured sharing improves estimation or merely duplicates a rich-input LSTM.

### Best high-upside custom-cell direction

**Partitioned memories with sparse recurrent communication.**

The strongest hypothesis is not “more gates find more alpha.” It is:

> When predictive information depends on interactions between signals arriving at different times, communication before compression can reduce the memory burden imposed by late fusion.

Section 10 gives a precise toy problem supporting that distinction.

### Best separate research program

**Causal adaptation to changing predictor–outcome mappings.**

Begin with coefficient filtering and shrunk rolling heads. Progress to recurrent meta-learning only after demonstrating that completed feedback contains useful incremental information and that simple adaptation cannot exploit it adequately.

A broader program would use more assets, more distinct environments, and predictive distributions rather than only point return scores.

---

## 9. Controlled experiment roadmap

### 9.1 Separate information experiments from architecture experiments

A clean sequence is:

| Stage | Controlled question                  | Comparators                                                            |
| ----- | ------------------------------------ | ---------------------------------------------------------------------- |
| I     | Does market information help?        | Own-only versus own-plus-market, for ridge and LSTM                    |
| II    | Does peer information help?          | Add the same peer summaries to both families                           |
| III   | Does explicit input modulation help? | Concatenation versus market gate, preserving direct context            |
| IV    | Does memory partitioning help?       | Dense LSTM versus independent smaller streams                          |
| V     | Does recurrent communication help?   | Independent streams versus coupled streams                             |
| VI    | Does another write pathway help?     | Ordinary, ungated extra-candidate, and extra-gated cells               |
| VII   | Does labeled feedback help?          | Static head versus shrunk rolling/filtering head                       |
| VIII  | Does hybrid control add more?        | Same state estimates as inputs versus gates versus conditional weights |

Do not make every later experiment depend on the “best” earlier architecture without recording that selection. The research path itself creates selection effects.

### 9.2 Capacity matching

For a target recurrent parameter budget \\(P\\), the one-layer width approximately solves

\\[ H= \frac{-(d+1)+\sqrt{(d+1)^2+P}}{2}. \\]

This is more principled than giving every architecture the same hidden width.

Use both:

**Same-width controls**, which reveal the effect of adding parameters.

**Parameter-matched controls**, which reveal whether the proposed structure is preferable to spending the same budget on ordinary recurrent capacity.

A small starting grid such as \\(H\in\\{16,32,64\\}\\) is defensible because it spans materially different capacities without unrestricted architecture search. It is not a claim that those values are optimal.

For coupled models, test very small message ranks first—for example \\(1,2,4\\)—because the hypothesis is low-dimensional common structure, not arbitrary unrestricted communication.

### 9.3 Chronological discipline

All learned transformations must be fitted using the permitted training period: scaling, feature selection, exposure estimates, graph estimation, HMM parameters, codebooks, pretraining, and controller calibration.

Purging must respect the **longest future window used by any objective**, not merely the primary four-hour label. A contrastive or auxiliary horizon may require a larger exclusion.

Conversely, sharing legitimate historical input observations across adjacent train/test windows is not automatically leakage. A blanket embargo equal to the lookback is not a substitute for analyzing actual information flow.

A period used to decide which architecture to try next is development data, even if it was initially called a test set. Preserve a genuinely untouched confirmation period.

### 9.4 Panel eligibility and missing data

Eligibility must be determined from information available at the decision time.

Do not remove stocks from the input panel because their future labels are missing. That can change both the stock being predicted and the information available to other stocks.

Use masks, data-age features, explicit benchmark eligibility, and defined handling of delistings or unavailable exits. Recompute peer summaries over the valid contemporaneous set, not a hindsight-selected set.

### 9.5 Effective sample size

For a stationary scalar metric series with autocorrelations \\(\rho_k\\), a familiar variance-based approximation is

\\[ T\_{\mathrm{eff}} \approx \frac{T}{1+2\sum\_{k\geq1}\rho_k}. \\]

For an exchangeable cross-section with common pairwise correlation \\(\rho\\), the variance of its average suggests

\\[ N\_{\mathrm{eff}} = \frac{N}{1+(N-1)\rho}. \\]

These are illustrative variance calculations under specific assumptions—not universal neural-network sample-complexity formulas.

Five seeds do not provide five independent market histories. They measure optimization variability conditional on the same data.

### 9.6 Prediction and economic metrics

Use per-decision rank IC and prediction loss, together with daily aggregated portfolio outcomes, turnover, drawdown, exposure, and cost sensitivity.

For overlapping four-hour forecasts, impose a fixed aggregate exposure rule. Do not count each forecast as a fully funded independent portfolio.

Hourly OHLCV alone does not identify actual spread or market impact. Report cost assumptions and break-even costs rather than presenting a selected cost scenario as measured implementation performance.

Serial dependence also affects risk-adjusted performance estimation and annualization. [CFA Institute Research & Policy Center](https://rpc.cfainstitute.org/research/financial-analysts-journal/2002/the-statistics-of-sharpe-ratios)

### 9.7 Nulls and selection-aware inference

A useful null must destroy the hypothesized predictive link while retaining the relevant dependence structure as far as possible.

Whole-panel day-block shifts can preserve contemporaneous cross-stock relationships better than independently shuffling each stock. But under regime change, arbitrary circular shifts are not automatically exchangeable transformations, so resulting permutation p-values are not automatically exact.

For peer-specific tests, consider transformations of estimated peer residual innovations conditional on market/sector state. Their validity depends on the residual model; they are not a universal conditional-randomization solution.

When testing the complete discovery process, rerun fitting and selection under the null, including label-dependent controllers and feedback construction. A post-fit shuffle addresses a narrower question.

Selection-aware procedures such as White’s Reality Check and Hansen’s superior-predictive-ability test provide relevant frameworks, subject to their assumptions. [Wiley Online Library](https://onlinelibrary.wiley.com/doi/abs/10.1111/1468-0262.00152)

### 9.8 Prospective decision rules

A proposed component should be retained only when it:

1. succeeds on the synthetic mechanism it was designed to address;
2. improves a preregistered paired OOS criterion against its strongest simpler comparator;
3. survives reasonable seed, fold, exposure, and cost checks.

For exploratory development, a one-standard-error preference for the simpler model is reasonable. For a confirmatory claim, use dependence-aware uncertainty and account for the model family searched.

Do not invent a required numerical IC improvement before understanding metric variability and implementation costs.

---

## 10. Concrete falsification tests and toy problems

### Test 1: an unobserved peer shock

\\[ y\_{i,t+1}=b\varepsilon\_{j,t}+\eta\_{i,t+1}, \\]

with \\(\varepsilon\_{j,t}\\) independent of own-stock and market inputs.

**Mathematically established prediction:** own-only and own-plus-market models cannot recover this term. A peer-informed linear model may succeed. More gates without peer observations should not.

This isolates information access from recurrent sophistication.

### Test 2: a fixed delayed peer response

\\[ y\_{i,t+1}=b x\_{j,t-\ell}+\eta\_{i,t+1}. \\]

A final-state mixing model can succeed if its encoder retains the relevant lag. Recurrent coupling is not inherently necessary.

**Falsification:** if coupled recurrence only beats a final-state model whose encoder was not allowed to retain the relevant history, the comparison does not establish a communication advantage.

### Test 3: cross-stream interactions before compression

Let

\\[ y=\sum\_{\tau=1}^{L}a\_\tau b\_\tau. \\]

Consider a late-fusion architecture

\\[ \hat y=g(\phi(a),\psi(b)), \\]

where \\(\phi\\) is continuous and maps an open subset of \\(\mathbb R^L\\) into \\(\mathbb R^H\\), with \\(H\<L\\).

If this architecture represented all such inner products exactly, then \\(\phi(a)=\phi(a')\\) would imply

\\[ (a-a')^\top b=0 \quad\text{for every }b, \\]

hence \\(a=a'\\). Thus \\(\phi\\) would have to be a continuous injection into a lower-dimensional Euclidean space, which is impossible on an open domain.

**Mathematically established:** sufficiently compressed independent encodings cannot represent this entire task exactly.

An online recurrent accumulator with access to both streams can update

\\[ s\_\tau=s\_{\tau-1}+a\_\tau b\_\tau. \\]

A conventional joint recurrent network can approximate bounded versions of this computation; a custom multiplicative update represents it directly.

This is a genuine communication/compression distinction—not proof of a financial advantage.

### Test 4: slow state plus transient shocks

Generate

\\[ z_t=\rho z\_{t-1}+\nu_t,\qquad y\_{t+1}=az_t+b\varepsilon_t+\eta_t, \\]

with \\(\rho\\) close to one and sparse \\(\varepsilon_t\\).

Compare a larger ordinary LSTM, an extra-write cell, independent memories, and coupled memories.

**Theoretically motivated hypothesis:** partitioning can preserve the slow state while processing shocks. It is disconfirmed if an ordinary parameter-matched LSTM learns equally stable retention and OOS prediction.

Inspect impulse responses and slow-state reconstruction—not only final loss.

### Test 5: observable state-dependent sign reversal

\\[ y\_{t+1}=s_t x_t+\eta_t, \qquad s_t\in\\{-1,+1\\}, \\]

where noisy market observations reveal \\(s_t\\).

Compare ordinary conditioning, a filtered state appended as input, explicit gating, and conditional weights.

The controller architecture earns its complexity only if it improves on the same filtered state supplied to the ordinary LSTM.

### Test 6: an unobservable mapping change

Keep the distribution of \\(x_t,m_t\\) unchanged, but reverse the coefficient linking \\(x_t\\) to future \\(y_t\\).

**Mathematically established prediction:** a feature-only model cannot know the switch immediately. Feedback-aware models may respond only after informative labels mature.

A model that reacts before any revealing observation or completed label arrives has exploited an unintended information channel.

### Test 7: common factors and ranking invariance

Generate

\\[ r\_{i,t+1}=\beta_i f\_{t+1}+\alpha\_{i,t+1}. \\]

When all \\(\beta_i\\) are equal, a common additive factor cannot alter cross-sectional rankings. When loadings differ, it can.

This test distinguishes a genuine heterogeneous-factor mechanism from a common offset that merely improves raw-return loss.

### Test 8: information destroyed by pooling

Construct peer shocks with zero cross-sectional mean but a target depending on one particular peer.

A simple mean pool loses the signal. Directed peer features or messages can retain it.

Do not generalize this result to every nonlinear set encoder: the limitation concerns the specified pooling map. More generally, universal set representation requires sufficiently rich latent dimension, not an arbitrarily tiny bottleneck. [Proceedings of Machine Learning Research](https://proceedings.mlr.press/v97/wagstaff19a.html)

### Test 9: universe changes

Reorder stocks and update masks while preserving stock-associated metadata. A permutation-equivariant model should reorder its predictions correspondingly.

Then remove a stock or introduce an unseen stock. These are stronger tests than reordering: they probe dependence on learned identity-specific parameters.

### Test 10: controller misspecification

Train a volatility/HMM controller under one emission model, then change the observation-noise distribution while retaining the underlying predictive relation.

**Theoretically motivated hypothesis:** an uncertainty-aware soft controller should degrade less abruptly than hard regime switching.

Failure to beat “append the same posterior probabilities” rejects the stronger gate-control claim.

For real-data diagnostics, post-fit gate interventions are sensitivity experiments, not causal identification. Retrained ablations are needed alongside interventions that may push the model outside its training distribution.

---

## 11. Open questions and directions beyond the current project

### Should the dataset change?

Possibly—but only for a specific scientific reason.

A larger cross-section would make latent-factor and cross-stock-structure questions more meaningful. More distinct historical environments would help evaluate adaptation. Higher-frequency order-flow data would make short-delay propagation questions more directly observable. None of these changes automatically increases usable alpha.

The current panel remains suitable for deciding whether market conditioning, simple peer access, and small structured memories are useful.

### Promising broader problems

**Conditional distributions rather than only mean returns.** A state-space or recurrent model may provide useful risk forecasts even when expected-return improvements are weak. Evaluate whether uncertainty improves exposure decisions with alpha held fixed.

**Dynamic coefficients rather than hidden “regimes.”** A continuously evolving regression coefficient can sometimes describe changing predictability more directly than a discrete regime label.

**Shared structure with changing local mechanisms.** Modular recurrence is particularly interesting when some relationships remain stable while others change. Financial evidence for that decomposition must be established rather than assumed.

**Delayed-observation filtering.** Four-hour labels create a concrete, mathematically meaningful adaptation problem. Properly comparing delayed Kalman updates, rolling regression, and learned feedback recurrence could be a standalone contribution.

**Separate covariance learning from alpha learning.** Better common-state estimation may improve portfolio risk management without improving cross-sectional ranking. Those outcomes should not be conflated.

**Cold-start generalization.** A global–local model using observable metadata rather than unrestricted ticker embeddings can be tested on unseen stocks. Its success would demonstrate transfer, not merely good fitting of the original names.

---

## 12. Source list and verified implementation links

### Required financial papers

| Paper                         | Publication                                     | Primary source                                                                                 | Verified code                                                                            |
| ----------------------------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Li et al., **MASTER**         | AAAI 2024                                       | [DOI: 10.1609/aaai.v38i1.27767](https://doi.org/10.1609/aaai.v38i1.27767)                      | [SJTU-DMTai/MASTER](https://github.com/SJTU-DMTai/MASTER?utm_source=chatgpt.com)         |
| Duan, Wang, Li, **FactorGCL** | AAAI 2025                                       | [DOI: 10.1609/aaai.v39i1.31993](https://doi.org/10.1609/aaai.v39i1.31993)                      | I did not verify an official repository                                                  |
| Fan and Shen, **StockMixer**  | AAAI 2024                                       | [DOI: 10.1609/aaai.v38i8.28681](https://doi.org/10.1609/aaai.v38i8.28681)                      | [SJTU-DMTai/StockMixer](https://github.com/SJTU-DMTai/StockMixer?utm_source=chatgpt.com) |
| Wang and Lera, **FinPFN**     | *Journal of Financial Markets* 79, 101042, 2026 | [DOI: 10.1016/j.finmar.2025.101042](https://doi.org/10.1016/j.finmar.2025.101042)              | [wangy8989/FinPFN](https://github.com/wangy8989/FinPFN?utm_source=chatgpt.com)           |
| Kim and Song, **PRISM-VQ**    | IJCAI 2026                                      | [DOI: 10.24963/ijcai.2026/492](https://doi.org/10.24963/ijcai.2026/492?utm_source=chatgpt.com) | [finxlab/PRISM-VQ](https://github.com/finxlab/PRISM-VQ?utm_source=chatgpt.com)           |

The publication and repository records support these entries. PRISM-VQ’s linked repository is a fork of the earlier repository mentioned in your notes; record an exact commit for reproduction rather than assuming both locations are interchangeable. [AAAI Publications](https://ojs.aaai.org/index.php/AAAI/article/view/27767)

### Foundations and architecture genealogy

| Reference                                                        | Venue/year and primary link                                                                                                                       |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Hochreiter and Schmidhuber, **Long Short-Term Memory**           | *Neural Computation*, 1997. [DOI](https://doi.org/10.1162/neco.1997.9.8.1735)                                                                     |
| Gers, Schmidhuber, Cummins, **Learning to Forget**               | *Neural Computation*, 2000. [DOI](https://doi.org/10.1162/089976600300015015)                                                                     |
| Greff et al., **LSTM: A Search Space Odyssey**                   | *IEEE TNNLS*, 2017. [Paper](https://arxiv.org/abs/1503.04069)                                                                                     |
| Pascanu, Mikolov, Bengio, **On the Difficulty of Training RNNs** | ICML 2013. [PMLR](https://proceedings.mlr.press/v28/pascanu13.html?utm_source=chatgpt.com)                                                        |
| Kalchbrenner, Danihelka, Graves, **Grid LSTM**                   | ICLR 2016. [Paper](https://arxiv.org/abs/1507.01526?utm_source=chatgpt.com)                                                                       |
| Koutník et al., **A Clockwork RNN**                              | ICML 2014. [PMLR](https://proceedings.mlr.press/v32/koutnik14.html)                                                                               |
| Neil, Pfeiffer, Liu, **Phased LSTM**                             | NeurIPS 2016. [Proceedings](https://proceedings.neurips.cc/paper/2016/hash/5bce843dd76db8c939d5323dd3e54ec9-Abstract.html?utm_source=chatgpt.com) |
| Chung, Ahn, Bengio, **Hierarchical Multiscale RNNs**             | ICLR 2017. [Paper](https://arxiv.org/abs/1609.01704?utm_source=chatgpt.com)                                                                       |
| Shi et al., **ConvLSTM**                                         | NeurIPS 2015. [Paper](https://arxiv.org/abs/1506.04214?utm_source=chatgpt.com)                                                                    |
| Li et al., **DCRNN**                                             | ICLR 2018. [Paper](https://arxiv.org/abs/1707.01926?utm_source=chatgpt.com)                                                                       |
| Santoro et al., **Relational Recurrent Neural Networks**         | NeurIPS 2018. [Paper](https://arxiv.org/abs/1806.01822?utm_source=chatgpt.com)                                                                    |
| Goyal et al., **Recurrent Independent Mechanisms**               | ICLR 2021. [Paper](https://arxiv.org/abs/1909.10893?utm_source=chatgpt.com)                                                                       |
| Ha, Dai, Le, **HyperNetworks**                                   | ICLR 2017. [Paper](https://arxiv.org/abs/1609.09106)                                                                                              |
| Perez et al., **FiLM**                                           | AAAI 2018. [DOI](https://doi.org/10.1609/aaai.v32i1.11671)                                                                                        |
| Wu et al., **Multiplicative Integration with RNNs**              | NeurIPS 2016. [Paper](https://arxiv.org/abs/1606.06630?utm_source=chatgpt.com)                                                                    |
| Tallec and Ollivier, **Can RNNs Warp Time?**                     | ICLR 2018. [Paper](https://arxiv.org/abs/1804.11188?utm_source=chatgpt.com)                                                                       |
| Beck et al., **xLSTM**                                           | NeurIPS 2024. [Paper](https://arxiv.org/abs/2405.04517); [official code](https://github.com/NX-AI/xlstm?utm_source=chatgpt.com)                   |
| Gu and Dao, **Mamba**                                            | COLM 2024. [Paper](https://arxiv.org/abs/2312.00752?utm_source=chatgpt.com)                                                                       |
| Feng et al., **Were RNNs All We Needed?**                        | 2024 preprint. [Paper](https://arxiv.org/abs/2410.01201)                                                                                          |

### Filtering, adaptation, theory, and evaluation

| Reference                                                                                        | Primary link                                                                                                                            |
| ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| Becker et al., **Recurrent Kalman Networks**, ICML 2019                                          | [PMLR](https://proceedings.mlr.press/v97/becker19a.html?utm_source=chatgpt.com)                                                         |
| Rangapuram et al., **Deep State Space Models for Time Series Forecasting**, NeurIPS 2018         | [Proceedings](https://papers.nips.cc/paper_files/paper/2018/hash/5cf68969fb67aa6082363a6d4e6468e2-Abstract.html?utm_source=chatgpt.com) |
| Dangl and Halling, **Predictive Regressions with Time-Varying Coefficients**, JFE 2012           | [DOI](https://doi.org/10.1016/j.jfineco.2012.04.003)                                                                                    |
| Gu, Kelly, Xiu, **Autoencoder Asset Pricing Models**, *Journal of Econometrics*, 2021            | [DOI](https://doi.org/10.1016/j.jeconom.2020.07.009?utm_source=chatgpt.com)                                                             |
| Zhao, Kong, Shen, **DoubleAdapt**, KDD 2023                                                      | [DOI](https://doi.org/10.1145/3580305.3599315); [official code](https://github.com/SJTU-DMTai/DoubleAdapt?utm_source=chatgpt.com)       |
| Andrychowicz et al., **Learning to Learn by Gradient Descent by Gradient Descent**, NeurIPS 2016 | [Paper](https://arxiv.org/abs/1606.04474?utm_source=chatgpt.com)                                                                        |
| Chen, Chang, Mehta, **Differentiable Filtering for Learning HMMs**, L4DC 2026                    | [PMLR](https://proceedings.mlr.press/v331/chen26c.html?utm_source=chatgpt.com)                                                          |
| Wagstaff et al., **On the Limitations of Representing Functions on Sets**, ICML 2019             | [PMLR](https://proceedings.mlr.press/v97/wagstaff19a.html?utm_source=chatgpt.com)                                                       |
| Wagstaff et al., **Universal Approximation of Functions on Sets**, JMLR 2022                     | [JMLR](https://jmlr.org/beta/papers/v23/21-0730.html?utm_source=chatgpt.com)                                                            |
| Sirignano and Cont, **Universal Features of Price Formation**, *Quantitative Finance*, 2019      | [Paper](https://arxiv.org/abs/1803.06917?utm_source=chatgpt.com)                                                                        |
| Zeng et al., **Are Transformers Effective for Time Series Forecasting?**, AAAI 2023              | [DOI](https://doi.org/10.1609/aaai.v37i9.26317)                                                                                         |
| White, **A Reality Check for Data Snooping**, *Econometrica*, 2000                               | [DOI](https://doi.org/10.1111/1468-0262.00152?utm_source=chatgpt.com)                                                                   |
| Hansen, **A Test for Superior Predictive Ability**, JBES 2005                                    | [DOI](https://doi.org/10.1198/073500105000000063)                                                                                       |
| Lo, **The Statistics of Sharpe Ratios**, FAJ 2002                                                | [DOI](https://doi.org/10.2469/faj.v58.n4.2453)                                                                                          |

The newer differentiable-HMM work is relevant evidence that structured filtering can itself be trained as a neural computation. It is not evidence that such a controller improves financial LSTM gates. [Proceedings of Machine Learning Research](https://proceedings.mlr.press/v331/chen26c.html)

---

## 13. Custom-cell mathematical appendix

The following are research candidates, **not claims of architectural novelty or production specifications**.

Unless stated otherwise, all stock-local parameters are shared across stocks. A common supervised objective is

\\[ \mathcal L\_{\mathrm{pred}} = \frac1{|\mathcal T|} \sum\_{t\in\mathcal T} \frac1{N_t} \sum\_{i\in\mathcal U_t} \ell(\hat y\_{i,t},y\_{i,t}) + \lambda\\|\theta\\|^2. \\]

The date-level normalization prevents dates with more eligible stocks from automatically receiving more weight. The choice of Huber, squared, or ranking loss must be held fixed across an architectural comparison.

### 13.1 Candidate C1: a separate write pathway into one memory

#### Problem and information set

The intended limitation is **write competition within one shared representation**, not lack of peer observations.

Let \\(z\_{i,t}\in\mathbb R^d\\) contain the complete information available to every comparator. Let \\(p\_{i,t}\in\mathbb R^{d_p}\\) be a designated subset, such as peer-innovation features.

Compute ordinary LSTM gates and candidate from \\((z\_{i,t},h\_{i,t-1})\\). Add

\\[ u^p\_{i,t} = \tanh(A_p p\_{i,t}+B_p h\_{i,t-1}+b_p), \\]\\[ g^p\_{i,t} = \sigma(C_p z\_{i,t}+D_p h\_{i,t-1}+d_p^{\\,b}), \\]

where \\(u^p,g^p\in\mathbb R^H\\), and define

\\[ \boxed{ c\_{i,t} = f\_{i,t}\odot c\_{i,t-1} + i\_{i,t}\odot u\_{i,t} + \gamma g^p\_{i,t}\odot u^p\_{i,t}, } \\]\\[ h\_{i,t}=o\_{i,t}\odot\tanh(c\_{i,t}), \qquad \gamma=\gamma\_{\max}\tanh\eta. \\]

The additional gate sees all available context, controls only the designated write, updates each observation, and is trained jointly from prediction loss.

#### Exact baseline reduction

Set \\(\eta=0\\), hence \\(\gamma=0\\). This recovers the conventional LSTM exactly.

Initialize the extra candidate branch nontrivially. If both its output and its multiplier are initialized to zero, the branch can be unnecessarily difficult to activate.

At \\(\gamma=0\\), the branch’s internal parameters initially receive no gradient, but \\(\eta\\) can receive one. Once \\(\gamma\\) moves, the branch can learn.

#### Parameters and compute

Excluding the prediction head,

\\[ \boxed{ P\_{C1} = 4H(d+H+1) + H(d_p+H+1) + H(d+H+1) + 1. } \\]

Memory remains \\(2NH\\) state coordinates. Compute increases by the two additional affine transformations per stock and observation.

#### State boundedness

Assume

\\[ 0\leq f\_{i,t,k}\leq\rho<1, \quad |u\_{i,t,k}|,|u^p\_{i,t,k}|\leq1, \quad |\gamma|\leq\gamma\_{\max}. \\]

Then

\\[ \\|c_t\\|\_\infty \leq \rho^t\\|c_0\\|\_\infty + (1+\gamma\_{\max}) \frac{1-\rho^t}{1-\rho}. \\]

**Mathematically established:** this bounds state magnitude under those assumptions.

It does not establish contraction of the complete recurrent Jacobian or good gradient conditioning. If forget gates remain extremely close to one, the bound can be large and the readout can saturate.

#### Gradients

Let \\(\delta^c\_{i,t}\\) be the total adjoint at the memory update, including future effects. For extra-branch preactivations \\(a_g,a_u\\),

\\[ \frac{\partial\mathcal L}{\partial a_g} = \delta^c \odot\gamma u^p \odot g^p(1-g^p), \\]\\[ \frac{\partial\mathcal L}{\partial a_u} = \delta^c \odot\gamma g^p \odot(1-(u^p)^2), \\]\\[ \frac{\partial\mathcal L}{\partial\eta} = \gamma\_{\max}\operatorname{sech}^2\eta \sum\_{i,t} \left\langle \delta^c\_{i,t},g^p\_{i,t}\odot u^p\_{i,t} \right\rangle. \\]

These equations define the learning signal; no second algorithm is needed.

#### Mechanism → Expected consequence → Failure mode → Falsification test

| Item                 | Assessment                                                                                                                                           |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Mechanism            | **Mathematically established:** a designated information family has a separately controlled additive write without additional memory coordinates     |
| Expected consequence | **Theoretically motivated hypothesis:** easier selective incorporation of sparse peer shocks without reconfiguring the entire ordinary candidate map |
| Failure mode         | Redundant branch, conflicting writes, larger cell magnitude, gate saturation, unstable dependence on noisy peers                                     |
| Synthetic test       | Slow latent state plus sparse peer shocks; compare state retention and shock response                                                                |
| Real OOS test        | Shock-conditioned prediction errors and overall net performance, against same-information controls                                                   |
| Simpler comparators  | Wider LSTM; ordinary LSTM with an ungated extra candidate; input-gated LSTM                                                                          |
| Retain/reject rule   | Retain only if the gate—not merely the extra candidate or parameters—has repeatable value                                                            |

**Research grounding:** additional control pathways have precedent, including time gates and multidimensional gated updates. The specific financial extra-write construction above is an untested combination. [arXiv](https://arxiv.org/pdf/1610.09513)

#### A normalized alternative

An explicitly competing update is

\\[ c_t = \pi\_{0,t}\odot c\_{t-1} + \pi\_{1,t}\odot u^1_t + \pi\_{2,t}\odot u^2_t, \\]

where, coordinatewise,

\\[ (\pi\_{0,t},\pi\_{1,t},\pi\_{2,t}) = \operatorname{softmax}(a_t). \\]

If candidates lie in \\([-1,1]\\), each coordinate remains in the convex hull of its previous value and those candidates.

**Mathematically established:** this prevents additive-write accumulation beyond that hull.

But it is not an unrestricted conventional LSTM: retention and writing must compete. Removing one candidate gives a coupled input–forget form, not arbitrary independent \\(f_t\\) and \\(i_t\\).

For \\(v_0=c\_{t-1},v_1=u^1_t,v_2=u^2_t\\),

\\[ \frac{\partial\mathcal L}{\partial a\_{k,t}} = \delta^c_t\odot\pi\_{k,t}\odot(v\_{k,t}-c_t). \\]

With all maps using \\((z_t,h\_{t-1})\\), three routing-logit maps, two candidate maps, and one output map use \\(6H(d+H+1)\\) parameters.

The falsifiable trade-off is lower update magnitudes and saturation **versus** worse performance on tasks requiring accumulation. This variant should not be called superior merely because it is bounded.

---

### 13.2 Candidate C2: input-partitioned, recurrently coupled memories

#### Shapes and recurrence

Let

\\[ x^{(1)}\_t\in\mathbb R^{d_1}, \qquad x^{(2)}\_t\in\mathbb R^{d_2}, \\]

with states

\\[ h^{(k)}\_t,c^{(k)}\_t\in\mathbb R^{H_k}. \\]

For each stream, form all four gate/candidate preactivations together:

\\[ a^{(k)}\_t = W_kx^{(k)}\_t + U\_{kk}h^{(k)}\_{t-1} + b_k + \sum\_{j\neq k} A\_{kj}B\_{kj}h^{(j)}\_{t-1}, \\]

where

\\[ W_k\in\mathbb R^{4H_k\times d_k}, \quad U\_{kk}\in\mathbb R^{4H_k\times H_k}, \\]\\[ A\_{kj}\in\mathbb R^{4H_k\times r\_{kj}}, \quad B\_{kj}\in\mathbb R^{r\_{kj}\times H_j}. \\]

Split \\(a^{(k)}\\) into input, forget, output, and candidate blocks and apply the standard LSTM update separately to each memory.

Finally,

\\[ \hat y_t=g([h^{(1)}\_t;h^{(2)}\_t]). \\]

Both cells use **previous** states of the other stream. Thus the update is well-defined without an instantaneous circular dependency.

#### What is genuinely different?

**Mathematically established:** this is a conventional larger LSTM with block-sparse input weights and structured low-rank off-diagonal recurrent blocks.

It is not a new universal function class beyond a sufficiently unrestricted LSTM.

Its potential value is the restriction:

\\[ \text{dense arbitrary interaction} \quad\longrightarrow\quad \text{separate local dynamics + limited communication}. \\]

That restriction can reduce parameters and enforce a scientifically motivated memory allocation.

#### Parameter count

\\[ \boxed{ P\_{C2} = \sum_k4H_k(d_k+H_k+1) + \sum\_{k\neq j} r\_{kj}(4H_k+H_j). } \\]

For example, \\(d_1=16,d_2=8,H_1=24,H_2=8\\) gives \\(4{,}480\\) independent-stream recurrent parameters. Rank-two communication in both directions adds \\(320\\), yielding \\(4{,}800\\).

A dense \\(d=24,H=32\\) LSTM uses \\(7{,}296\\). Therefore, same-total-width and same-parameter comparisons answer different questions.

#### Gradients and initialization

For one message path,

\\[ \frac{\partial\mathcal L}{\partial A\_{kj}} = \delta a^{(k)}\_t (B\_{kj}h^{(j)}\_{t-1})^\top, \\]\\[ \frac{\partial\mathcal L}{\partial B\_{kj}} = A\_{kj}^{\top}\delta a^{(k)}\_t (h^{(j)}\_{t-1})^\top, \\]

and the message contributes

\\[ B\_{kj}^{\top}A\_{kj}^{\top}\delta a^{(k)}\_t \\]

to the adjoint of \\(h^{(j)}\_{t-1}\\).

Initialize \\(A\_{kj}=0\\) and \\(B\_{kj}\\) nonzero to recover independent streams while allowing the coupling to activate. Different initial forget biases may encode different timescale hypotheses.

#### Mechanism → Expected consequence → Failure mode → Falsification test

| Item                 | Assessment                                                                                                                             |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Mechanism            | **Mathematically established:** information from one stream changes the other stream’s gates before final compression                  |
| Expected consequence | **Theoretically motivated hypothesis:** improved learning of conditional temporal interactions with fewer unnecessary cross-parameters |
| Failure mode         | Incorrect partition, bottleneck too narrow, excessive coupling, or no actual need for early interaction                                |
| Synthetic test       | Cross-stream inner-product task; delayed conditional interactions; slow/fast state mixture                                             |
| Real OOS test        | Same inputs and head, comparing independent streams, coupled streams, and dense LSTMs                                                  |
| Simpler comparators  | Nonlinear late fusion; all-input ordinary LSTM; engineered cross-features                                                              |
| Retain/reject rule   | Reject recurrent coupling if late fusion or engineered interactions match its performance and stability                                |

**Research grounding:** separate communicating memories are established precedent in Grid LSTM and modular recurrent systems. The appropriate financial partition remains unverified. [arXiv](https://arxiv.org/pdf/1507.01526)

#### Cross-stock version

A causal peer-message variant first computes

\\[ p\_{j,t} = \tanh(E x\_{j,t}+F h\_{j,t-1}+b_p) \in\mathbb R^r, \\]

then

\\[ \mu\_{i,t} = \sum\_{j\neq i}a\_{ij,t}p\_{j,t}, \qquad a\_{ij,t}\geq0, \quad \sum\_{j\neq i}a\_{ij,t}=1. \\]

Add \\(C\mu\_{i,t}\\), \\(C\in\mathbb R^{4H\times r}\\), to the local gate preactivations.

Current peer observations enter before the forecast, but only after their bars are complete. Using only \\(h\_{j,t-1}\\) would delay a new peer shock by one model step; the current-input term avoids that artificial delay.

For fixed known peer weights, extra parameters are

\\[ r(d+H+1)+4Hr. \\]

Sparse graph aggregation costs \\(O(|E\_{\mathrm{graph}}|r)\\) per observation. A nonnegative low-rank stock mixing matrix can reduce aggregation cost further, but identity-specific mixing parameters complicate universe changes.

Initialization \\(C=0\\) recovers the ordinary local LSTM. BPTT passes gradients through \\(C\\), the message aggregation, and peer encoders.

**Mechanistic prediction:** this design should beat final-state mixing specifically when relevant cross-stream interactions would otherwise be lost during independent encoding. It should not systematically beat a simpler peer-lag regression on a purely linear fixed-lag toy task.

---

### 13.3 Candidate C3: shared global–local recurrent memory

#### Problem

The proposed benefit is **shared estimation of common dynamics**, not arbitrary peer-specific routing.

Let \\(x\_{i,t}\in\mathbb R^{d_s}\\), \\(m_t\in\mathbb R^{d_m}\\), local state width \\(H\\), and global state width \\(G\\).

Define a masked pool

\\[ p_t = \frac{1}{N_t}\sum\_{i\in\mathcal U_t}\phi(x\_{i,t}), \qquad \phi(x)=\tanh(W\_\phi x+b\_\phi)\in\mathbb R^q, \\]

and

\\[ \bar h\_{t-1} = \frac1{N_t}\sum\_{i\in\mathcal U_t}h\_{i,t-1}. \\]

Update the global state first:

\\[ (g_t,c^G_t) = \mathrm{LSTM}\_G( [m_t;p_t;\bar h\_{t-1}], g\_{t-1},c^G\_{t-1}). \\]

Then update every local state:

\\[ (h\_{i,t},c\_{i,t}) = \mathrm{LSTM}\_L( [x\_{i,t};g_t], h\_{i,t-1},c\_{i,t-1}). \\]

Use

\\[ \hat y\_{i,t}=w^\top h\_{i,t}+b. \\]

The update order is triangular: current global state depends on current observations and previous local states; current local states then depend on the current global state.

#### Why this can alter rankings

Unlike adding the same scalar output offset, \\(g_t\\) changes each stock’s gates jointly with its own \\(x\_{i,t}\\) and \\(h\_{i,t-1}\\). Consequently, the resulting effect can differ across stocks.

#### Parameter count

\\[ \boxed{ P\_{C3} = q(d_s+1) + 4G(d_m+q+H+G+1) + 4H(d_s+G+H+1), } \\]

excluding the head and optional count/mask features.

There is one global state pair and \\(N\\) local state pairs. The global state is not \\(N\\) independent observations merely because it affects \\(N\\) predictions.

#### Training and reduction

All neural parameters receive gradients from \\(\mathcal L\_{\mathrm{pred}}\\). The global state receives the sum of downstream local contributions, with the date-normalized loss controlling scaling across different \\(N_t\\).

An ablation that removes global-to-local input blocks recovers an ordinary local recurrent model. Another that removes local-to-global feedback tests a market encoder with one-way conditioning.

A market-only global stream can be reproduced by duplicated, parameter-tied computations inside each stock’s model. Computing it once is then an efficiency and organization advantage, not a new function.

With local-to-global feedback, the system genuinely communicates across stocks.

#### Mechanism → Expected consequence → Failure mode → Falsification test

| Item                 | Assessment                                                                                                       |
| -------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Mechanism            | **Mathematically established:** common information is summarized once and influences local transitions           |
| Expected consequence | **Theoretically motivated hypothesis:** more consistent common-state estimation and reduced redundant capacity   |
| Failure mode         | Global pooling loses directed innovations; common state dominates local alpha; feedback destabilizes both levels |
| Synthetic test       | Shared latent factor plus local dynamics, followed by a zero-sum peer-shock counterexample                       |
| Real OOS test        | Compare engineered pooling, separate market encoder, one-way hierarchy, and two-way hierarchy                    |
| Simpler comparators  | Rich-input shared LSTM with identical pooled inputs; dynamic-factor filter                                       |
| Retain/reject rule   | Keep only the minimum direction of coupling supported by OOS evidence                                            |

Sector states can be inserted between global and local states, but should share transition parameters across sectors unless data justify otherwise. With approximately four names per sector, sector-specific neural parameter sets are especially difficult to justify.

This is a **theoretically motivated financial specialization** of established hierarchical/modular recurrent ideas, not a demonstrated new financial model.

---

### 13.4 Candidate C4: filtered-state, low-rank conditional recurrent weights

#### Problem

This design tests whether an externally estimated state should control the transition rule rather than merely enter as another input.

#### Filter

Let \\(S_t\in\\{1,\dots,K\\}\\) be an HMM state and

\\[ \pi\_{t,k}=P(S_t=k\mid m\_{\leq t}). \\]

For transition matrix \\(T\\) and emission density \\(p_k(m_t)\\),

\\[ \boxed{ \pi\_{t,k} = \frac{ p_k(m_t)\sum_j T\_{jk}\pi\_{t-1,j} }{ \sum\_\ell p\_\ell(m_t)\sum_j T\_{j\ell}\pi\_{t-1,j} }. } \\]

This is filtering, not smoothing.

Fit the filter using permitted historical data, then compute forward probabilities. A hindsight-smoothed regime sequence must not be used as real-time input.

#### Conditional recurrent map

Stack the four LSTM preactivations:

\\[ a_t=Wz_t+U_0h\_{t-1}+b + A\left[s_t\odot(Bh\_{t-1})\right], \\]

where

\\[ A\in\mathbb R^{4H\times r}, \quad B\in\mathbb R^{r\times H}, \\]\\[ s_t=\tanh(R(\pi_t-\pi_0)), \qquad R\in\mathbb R^{r\times K}. \\]

Equivalently,

\\[ U_t=U_0+A\operatorname{diag}(s_t)B. \\]

The controller affects gate **weight matrices**, not just gate activations or biases.

#### Parameter count and stability restriction

Extra neural parameters are

\\[ \boxed{5Hr+rK} \\]

without a generator bias.

For a \\(K\\)-state HMM with diagonal Gaussian emissions in \\(d_m\\) dimensions, the statistical degrees of freedom are

\\[ (K-1)+K(K-1)+2Kd_m, \\]

before any additional restrictions.

Because \\(\\|s_t\\|\_\infty\leq1\\),

\\[ \\|U_t-U_0\\|\_2 \leq \\|A\\|\_2\\|B\\|\_2. \\]

**Mathematically established:** this bounds the conditional perturbation of the recurrent matrix.

It does not by itself bound the full recurrent Jacobian.

#### Initialization and training

Set \\(R=0\\), with \\(A,B\\) nonzero, to recover the ordinary LSTM initially.

A coherent two-stage procedure is:

\\[ \widehat\eta\_{\mathrm{HMM}} = \arg\max\_\eta \sum_t\log p\_\eta(m_t\mid m\_{\<t}), \\]

followed by BPTT on the recurrent prediction loss while treating \\(\pi_t\\) as fixed inputs.

For \\(\delta a_t=\partial\mathcal L/\partial a_t\\),

\\[ \frac{\partial\mathcal L}{\partial s_t} = (A^\top\delta a_t)\odot Bh\_{t-1}, \\]\\[ \frac{\partial\mathcal L}{\partial R} = \left[ (1-s_t^2)\odot \frac{\partial\mathcal L}{\partial s_t} \right] (\pi_t-\pi_0)^\top. \\]

No gradient passes into the frozen HMM.

A differentiable filter could instead be jointly trained, but then its objective and interpretation change. Recent structured differentiable-HMM work supports the feasibility of that computation, not this financial performance hypothesis. [Proceedings of Machine Learning Research](https://proceedings.mlr.press/v331/chen26c.html)

#### Mechanism → Expected consequence → Failure mode → Falsification test

| Item                         | Assessment                                                                                                                         |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Mechanism                    | **Mathematically established:** filtered state changes a low-rank subspace of the recurrent transition                             |
| Expected consequence         | **Theoretically motivated hypothesis:** smoother adaptation to recurring conditional dynamics than separate full recurrent experts |
| Failure mode                 | Incorrect regimes, uncertain state treated as certain, redundant capacity, unstable transition changes                             |
| Synthetic test               | Noisy observable HMM with state-dependent dynamics, plus misspecified-emission stress test                                         |
| Real OOS test                | Regime-switch recovery and overall OOS performance using strictly filtered states                                                  |
| Essential simpler comparator | The same \\(\pi_t\\) appended to a conventional LSTM                                                                               |
| Further controls             | Fixed rule-based state; conditional head; gate-bias conditioning; full versus low-rank modulation                                  |
| Retain/reject rule           | Reject conditional weights if appended states or a conditional head perform as well                                                |

**Research grounding:** conditional parameter generation is established by HyperNetworks. The filtered financial controller and low-rank restriction above are a proposed combination whose incremental value remains untested. [arXiv](https://arxiv.org/pdf/1609.09106)

---

## 14. Hybrid-training comparison table

### 14.1 A general differentiable controller

Let

\\[ q_t=C\_\phi(v\_{\leq t}),\qquad s_t=F\_\theta(s\_{t-1},x_t,q_t),\qquad \hat y_t=G\_\psi(s_t). \\]

Then

\\[ \frac{d\mathcal L}{d\phi} = \sum_t \frac{d\mathcal L}{dq_t} \frac{\partial q_t}{\partial\phi}. \\]

The total derivative \\(d\mathcal L/dq_t\\) includes all later consequences of changing the recurrent state. Ordinary BPTT provides that signal when the computation is differentiable.

Merely fitting \\(C\_\phi\\) to a separate regime label does not optimize this downstream objective.

| Training method                     | What learns the gate-related quantity?                                          | Gradient between components?                                      | Label/timing requirement                                                   | Main risk                                                              |
| ----------------------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Joint BPTT                          | Controller and recurrent weights optimize the same forecast loss                | Yes                                                               | All supervised labels restricted to training windows                       | Co-adaptation and overfitting                                          |
| Truncated BPTT                      | Same, but temporal gradients stop at boundaries                                 | Yes, within truncation                                            | State carry and label maturity must remain causal                          | Missed long-range credit assignment                                    |
| Pretrain/freeze controller          | Auxiliary model estimates regime, volatility, or state                          | No downstream gradient into controller                            | Auxiliary targets must have matured                                        | Objective mismatch and propagated controller error                     |
| HMM/Kalman filtering                | Statistical estimator updates state using observations                          | Not necessarily                                                   | Filtered—not smoothed—state at forecast time                               | Model misspecification                                                 |
| Alternating optimization            | Optimize recurrent weights, then controller, against a defined common objective | Can use blockwise gradients                                       | Chronological validation and matured targets                               | Nonconvex local solutions; naive alternating targets may be incoherent |
| Soft tree/controller                | Differentiable routing parameters optimize prediction or auxiliary loss         | Yes                                                               | Same restrictions as joint training                                        | Soft routing may differ from desired hard decisions                    |
| Frozen hard tree/EBM/boosting model | Separate algorithm supplies controller features or masks                        | No                                                                | Use chronological out-of-fold or prequential training outputs where needed | Optimistic stacking and brittle thresholds                             |
| Functional boosting of gate outputs | Fit weak learners to negative functional gradients of downstream loss           | Gradients computed through recurrent system to controller outputs | Full causal sequence construction                                          | Expensive and difficult recurrent credit assignment                    |
| Bilevel/meta-learning               | Controller optimized for future-within-training adaptation performance          | Through inner optimization or implicit gradients                  | Query tasks must remain before held-out test                               | Noisy hypergradients and too few environments                          |
| Online recursive updates            | Regression/filter coefficients update when labels mature                        | Usually no end-to-end gradient                                    | Delayed measurements handled explicitly                                    | Feedback noise and drift                                               |
| Learned optimizer                   | RNN produces parameter updates                                                  | Through unrolled optimization during meta-training                | Requires many legitimate training tasks                                    | Optimizer overfits its task distribution                               |
| Evolutionary/black-box search       | Search gate parameters or architectures using a scalar objective                | No                                                                | Every trial counts as model selection                                      | Very poor sample/compute efficiency for high-dimensional weights       |
| Reinforcement learning              | Controller trained through action-dependent rewards                             | Policy/value gradients or other RL method                         | Reward availability and trading costs explicit                             | Unnecessary variance when supervised differentiation is available      |

Learned optimizers and financial meta-adaptation have established precedents, but their successful use requires an appropriate distribution of training tasks and a defined inner/outer objective. [NeurIPS Papers](https://papers.nips.cc/paper_files/paper/2016/hash/fb87582825f9d28a8d42c5e5e5e8b23d-Abstract.html)

### 14.2 A valid bilevel formulation

For controller parameters \\(\phi\\),

\\[ \theta^\*(\phi) = \arg\min\_\theta \mathcal L\_{\mathrm{train}}(\theta,\phi), \\]\\[ \min\_\phi \mathcal L\_{\mathrm{query}}(\theta^\*(\phi),\phi). \\]

Under differentiability, a suitable isolated optimum, and an invertible inner Hessian,

\\[ \frac{d\mathcal L\_{\mathrm{query}}}{d\phi} = \partial\_\phi\mathcal L\_{\mathrm{query}} - \nabla\_\theta\mathcal L\_{\mathrm{query}}^\top H\_{\theta\theta}^{-1} \nabla\_{\theta\phi}^2\mathcal L\_{\mathrm{train}}. \\]

This is a mathematical account of how a second learning process could shape gate behavior. The required regularity and optimization assumptions should not be silently assumed in a noisy nonconvex implementation.

### 14.3 Where nondifferentiable algorithms are genuinely usable

A hard tree can supply a volatility-state estimate, an EBM can supply a calibrated auxiliary prediction, or a boosting model can supply a frozen contextual score.

Those are coherent interfaces.

A hard tree cannot simply be inserted into an end-to-end computational graph and treated as though ordinary gradients train its splits. One must freeze it, alternate a well-defined objective, use a differentiable surrogate, or adopt a gradient-free method.

For the present data scale, **frozen auxiliary state estimates and shrunk online heads are realistic**. Large black-box optimization of all gate weights and unrestricted recurrent meta-learning are much more speculative.

---

## 15. Architecture genealogy and literature map

The user’s ideas have substantial precedent, but the precedents make different modifications.

| Lineage                              | Actual recurrent modification                                              | Connection to this investigation                                       |
| ------------------------------------ | -------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Conventional LSTM → forget-gate LSTM | Add adaptive retention to the memory path                                  | Gate roles can be genuine research variables                           |
| Multidimensional LSTM                | \\(c=\sum_k f_k\odot c^{(k)}+i\odot u\\)                                   | Multiple incoming memories require control of additive growth          |
| Grid LSTM                            | Each axis retains its own memory while hidden representations interact     | Closest precedent for communicating but nonconflated memories          |
| Phased LSTM                          | \\(c=k_t\tilde c+(1-k_t)c^-\\), similarly for \\(h\\)                      | Extra gates can control update timing rather than input importance     |
| Clockwork RNN                        | Predetermined module update schedules                                      | Explicit timescale allocation without several full-resolution encoders |
| Hierarchical multiscale RNN          | Learned COPY/UPDATE/FLUSH behavior                                         | Boundary-controlled memory operations                                  |
| ConvLSTM / DCRNN                     | Replace dense transformations with spatial/graph operators                 | Communication can be placed inside recurrent gates                     |
| RIMs / relational memory             | Selective module updating and attention-mediated memory interaction        | Sparse interacting recurrent mechanisms                                |
| Multiplicative integration           | Replace purely additive integration by terms involving \\((Wx)\odot(Uh)\\) | Explicit low-cost conditional interactions                             |
| HyperNetworks                        | Generate recurrent parameters from another network                         | Distinguishes weight generation from gate activation                   |
| Recurrent Kalman networks            | Prediction/update structure with latent uncertainty                        | External-state estimation can be part of the recurrent computation     |
| xLSTM                                | Normalized exponential-gated scalar memories and matrix memories           | Memory structure can change fundamentally, not merely gate count       |

The multidimensional sum versus separate Grid memories is particularly relevant: unconstrained summation of many incoming memories can create growth that separate memory paths avoid. [arXiv](https://arxiv.org/pdf/1507.01526)

### Modern gated alternatives deserve consideration

For the scalar xLSTM memory, the essential normalized structure is

\\[ c_t=f_tc\_{t-1}+i_tz_t, \qquad n_t=f_tn\_{t-1}+i_t, \qquad h_t=o_t\frac{c_t}{n_t}, \\]

with exponential gating and additional numerical stabilization.

Its matrix-memory variant uses an update of the form

\\[ C_t=f_tC\_{t-1}+i_tv_tk_t^\top \\]

and query-based retrieval. These are materially different memory mechanisms, with matrix-state costs rather than merely another sigmoid gate. [arXiv](https://arxiv.org/pdf/2405.04517)

The minGRU/minLSTM line instead investigates simpler input-driven updates that permit efficient parallel scans. Mamba likewise uses selective state-space transitions. Their efficiency arguments are relevant, but a 48-observation panel task may not be dominated by long-sequence throughput. [arXiv](https://arxiv.org/html/2410.01201v3)

For local Apple hardware, optimized kernels should not be assumed available simply because a paper reports GPU throughput. The current xLSTM repository explicitly distinguishes optimized GPU paths from native implementations for other platforms. [GitHub](https://github.com/nx-ai/xlstm?utm_source=chatgpt.com)

**Assessment of novelty:** extra gates, multiple memories, sparse coupling, and conditional recurrent weights are established architectural themes. A contribution here would need to lie in a specific coherent mechanism, a rigorous property, a carefully isolated empirical finding, or a genuinely new treatment of delayed financial feedback—not merely in combining their names.

---

## 16. Design criteria for specialization and interaction

### Number of gates

Add a gate only after identifying a distinct controlled quantity.

“Regime gate” is insufficient. A defensible description is:

> It sees filtered market state and current peer innovations; it controls a bounded peer-write contribution; it updates at every completed bar; it receives gradients from the future relative-return loss.

A second gate that controls exactly the same quantity from the same inputs may provide little beyond a deeper parameterization.

### Number of memory compartments

Choose compartments to represent different persistence or communication requirements, not the number of indicator categories.

A plausible initial split is slow/common versus fast/local. A return/volume/volatility split may also be useful, but could unnecessarily separate interactions that should be learned jointly.

The appropriate number is the smallest one that passes a mechanism-specific test and improves OOS evidence.

### Input partitioning

Three alternatives must be compared:

\\[ \text{restricted routing}, \qquad \text{all inputs to all streams}, \qquad \text{one unpartitioned model}. \\]

Otherwise, an apparent specialization benefit may come from accidentally withholding useful information from a comparator.

### Message rank and sparsity

A small rank is a hypothesis that only a few communication directions matter.

Increase rank when the bottleneck demonstrably loses relevant information—for example, a controlled peer-shock test—not because a larger model reduces training error.

Known sector relations are a useful initial prior. Learned arbitrary edges should be justified by evidence that sector summaries are insufficient.

### Timescales and update frequency

Choose timescales according to the persistence being modeled and the observation clock.

Trading observations, elapsed clock time, and release-event time are not interchangeable. Include timing information or an explicit update policy when overnight gaps or asynchronous inputs matter.

A slow-updating common state should not prevent an important current shock from reaching the fast local state.

### Parameter sharing

Share stock-local transition parameters unless stock-specific dynamics earn their additional estimation cost.

A common market trajectory should be computed once when it is mathematically common. Sector states may differ while sector transition parameters remain shared.

Ticker embeddings can help encode stable identity, but weaken cold-start claims. Observable attributes provide a more transferable conditioning interface.

### Joint versus separate training

Use joint BPTT for differentiable modules whose role is directly defined by the forecasting objective.

Use separate estimation when a controller has a meaningful independent target or statistical interpretation. Then test whether that separation reduces variance enough to offset controller error and objective mismatch.

### Interpretability

A named compartment is a structural constraint, not an interpretation theorem.

Useful diagnostics include retained-information probes, controlled perturbations, message ablations, and alignment with independently defined states. Gate plots alone cannot establish that the network has learned a causal market mechanism.

### Comparative accounting of claimed benefits

| Claimed benefit                                     | Architectural, informational, or unproven?                   |
| --------------------------------------------------- | ------------------------------------------------------------ |
| Using current peer shocks                           | Primarily **additional information access**                  |
| Using completed forecast errors                     | Primarily **additional feedback information**                |
| Computing a common market state once                | **Computational sharing**; sometimes a structural constraint |
| Separating memories at fixed total width            | **Architectural restriction / inductive bias**               |
| Communicating before final compression              | **Architectural information-flow difference**                |
| Adding an extra write gate                          | **Parameterization and optimization hypothesis**             |
| Appending HMM probabilities                         | **State estimation / feature construction**                  |
| Generating recurrent weights from HMM probabilities | **Conditional-transition architecture**                      |
| Calling embeddings “factors”                        | **Unproven interpretation** without restrictions             |
| Calling quantized codes “regimes”                   | **Unproven interpretation** without validation               |
| Higher net returns                                  | **Requires empirical testing** for every candidate           |

---

## 17. Research decision tree

**Begin with the information set.**\
When a desired prediction depends on peer observations or completed labels absent from the baseline, supply that information to a simple comparator first. Do not begin by increasing gate count.

**Then ask whether recurrence is earning its cost.**\
When lagged ridge or a compact nonrecurrent model matches the recurrent models, retain the simpler model unless recurrence demonstrates a separate benefit such as transfer or uncertainty estimation.

**When recurrence helps but one memory appears overloaded, test partitioning.**\
Compare an ordinary larger LSTM with separate smaller memories under both equal-state and equal-parameter budgets.

**When partitioning helps but late fusion loses relevant interactions, test recurrent coupling.**\
Require success on a communication-sensitive toy problem and an OOS improvement against nonlinear late fusion.

**When the problem is selective storage rather than communication, test one extra write or update gate.**\
Include an ungated extra-candidate control. Reject the gate when its value is explained by additional parameters alone.

**When observable regimes alter processing, test explicit state estimates as ordinary inputs before hybrid gate control.**\
Move to conditional recurrent weights only when input or readout conditioning is insufficient.

**When predictor success changes without reliable feature-state clues, move to matured-label adaptation.**\
Begin with shrinkage and filtering. Meta-trained recurrence must beat those baselines using the same historical feedback.

**When several sophisticated branches remain statistically indistinguishable, simplify rather than combine them.**

The most defensible central research question is therefore not:

> “How many cells or gates should we add?”

It is:

\\[ \boxed{ \begin{gathered} \text{What information must be available,}\\\ \text{what must be remembered separately,}\\\ \text{when must those memories communicate,}\\\ \text{and what learning signal justifies each adaptation?} \end{gathered} } \\]

A conventional LSTM may be sufficient once those questions are answered well. Where it is not, the strongest next step is a small, explicitly structured recurrent system whose claimed mechanism can be disproved—not a collection of modules whose benefits cannot be separated.