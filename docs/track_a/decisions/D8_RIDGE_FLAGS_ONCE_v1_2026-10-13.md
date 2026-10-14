# D8-RIDGE-FLAGS-ONCE-v1 — additive synthetic decision

Decision date: 2026-10-13. Authority: the researcher's corrective P4.8/P4.9
prompt and explicit reply, “Keep all 163/198 slopes penalized, with a separate
free intercept.” This is a new decision, not a claim about the frozen v1.2
document or collaborator approval.

| Block | Half-open offsets | Columns |
|---|---|---:|
| Unchanged stock FT0, lag-major | 0–112 | 112 |
| Unchanged D7, lag-major | 112–147 | 35 |
| Unchanged peer mean/dispersion, lag-major | 147–161 | 14 |
| Target is H, target is L, each once | 161–163 | 2 |
| LL1 directed channels, lag-major | 163–198 | 35 |

LL0 has 163 penalized slopes; LL1 and its timing sham have 198. Each has the
existing separate, unpenalized pooled intercept. The first 163 LL1 columns are
exactly LL0. Lags are `[0,1,2,5,11,23,47]`; directed channel order is
`H_TO_L_0,H_TO_L_1,L_TO_H_0,L_TO_H_1,PEER_MEAN_1`. The original objective and
lambda grid `[.0001,.001,.01,.1,1]` remain unchanged. Seven repeated flag
columns would lower their effective penalty to lambda/7; 175/210 is unapproved.

The canonical JSON decision SHA is
`c59c4486271f2d8c465c556272d8ea2fdde9fe08acff3d66bc7bada4819b485d`.
Adapters require this decision, an explicit synthetic Permission, fictional
qualified formation table, exact input/source/action/order/preparation identities,
and a common causal three-arm mask. Real H/L remains `HL_REAL_UNRESOLVED`.
Scientific gates remain HOLD and real neural pairs remain 0/40.
