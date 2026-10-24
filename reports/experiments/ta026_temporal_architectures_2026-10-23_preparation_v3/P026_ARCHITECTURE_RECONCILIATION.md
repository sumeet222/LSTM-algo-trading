# P026 architecture reconciliation

The newly supplied `docs/track_a/Consolidated_Architecture_Design_Menu.md` was read in full following the researcher's current instruction. Package026's explicit definitions and October10 §12.1 take precedence over generic menu examples. No candidate has trained. The Stage0 receipt's earlier missing-menu observation is historical and is superseded by this append-only reconciliation.

| Candidate | Menu / October10 | Frozen P026 implementation |
|---|---|---|
| P026 A1 TM1_ATTENTION | Menu Table2 shows a generic attention-weighted hidden readout. October10 §12.1 fixes normalized query scores and a residual readout with gamma0=0. | All48 LSTM states, no-affine LayerNorm eps1e-5, q/sqrt32, softmax48, h48+gamma(c−h48), original scalar head/dropout. 6,466 parameters. |
| P026 A2 TM3_MULTISCALE | Menu Table2 specifies multiscale processing before one LSTM and warns of duplication with engineered horizons. October10 leaves TM3 deferred. | Current package explicitly elects this narrow arm: causal inclusive1/4/12 means over released scaled positions, Linear48→16 initialized[I,0,0], then original LSTM/head. 7,217 parameters. No separate encoders, new observations, extra masks or nonlinear mixer. |
| P026 A3 GRU32 | No named GRU arm in the menu or October10 temporal shortlist. | Explicit package election: PyTorch GRU16→32, one layer, final hidden, unchanged scalar head/dropout;4,833 parameters. No invented gate measurements. |

The menu's §14 A1/A2/A3 names mean market concatenation/gating/stock mixing. They are unrelated to package-local P026 arm labels; fully qualified run IDs include TM1_ATTENTION/TM3_MULTISCALE/GRU32 and T2 to prevent collisions. No menu market, spatial, factor, regime, multi-task or combined module is activated.

Bound implementation details supplied by this preparation: attention query uses a local CPU generator seed2643 with Normal(0,.01); gamma is exactly0; LayerNorm has PyTorch default eps1e-5 and no affine parameters. Added-module initialization preserves the base T2 weights and global RNG stream. Multiscale averages use already released finite scaled/fallback values and actual prefix lengths; they do not invent missing-data observations. These details will be included in the proposal for the separate three-start approval.

No unresolved architecture ambiguity remains under the explicit package formulas. Different capacities and initialization families prevent a parameter-matched causal interpretation. The broader menu and frozen roadmap remain intact.
