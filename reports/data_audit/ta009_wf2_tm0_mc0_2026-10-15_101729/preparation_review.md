# WF2 preparation and timing review

Both arms use the exact AAPL/COST/CMCSA/SBUX/CME order, identical TG0 targets and 16 stock channels. MC0 adds the frozen five SPY U1–U5 channels. Input shape is 48 complete hourly steps; six full hourly bars per ordinary RTH session, with the closing stub excluded. No candle insertion, raw archive copy or dense per-seed window store was introduced.

| View | Eligible origins | Eligible sessions | Timing-excluded origins | Ordinary-origin denominator |
|---|---:|---:|---:|---:|
| Inner training | 1626 | 813 | 0 | 1626 |
| Inner validation | 108 | 54 | 16 | 124 |
| Full-prefix refit | 1750 | 875 | 0 | 1750 |
| WF2 | 232 | 116 | 16 | 248 |

Counts are identical for both arms. Each eligible session contributes both original forecast origins and five targets. The denominator is before the retained ASOF scaler timing exclusion, after calendar/ordinary-origin construction. It is not a count of all exchange sessions. The true last 63 exchange-calendar sessions begin October 2, 2023; one early-close session has no ordinary origins. Eight more sessions fail the existing scaler-at-every-own-step requirement. This yields 54 eligible validation sessions and 54 observations per origin, exceeding the frozen minima of 50 sessions and 25 per origin without moving the tail. WF2 likewise retains its 16 timing exclusions; its count happens to equal WF1 and was not forced to do so.

The existing view APIs enforce strict label maturation and split purging, own-symbol 48-step history, historical scaling availability and market endpoint/46-of-48 support. All actual prepared numeric inputs and targets were checked finite, both arms' stock prefixes and labels compared exactly, and the confirmation boundary remains July 1, 2024. Inner-only and full-prefix stock normalizers/TG0 floors and unique-time market normalizers were recomputed independently; June-2023 recipes were not substituted. `input_binding.json` records the exact IDs and hashes.

Recipe `window.stop` identifies the permitted historical information cutoff. Newly reconstructed recipes record their actual October-2026 construction/fitting metadata, with retrospective application explicitly approved. A first preparation attempt incorrectly reused the historical cutoff as fitting metadata and failed the existing availability guard. Its draft files and failure log are preserved in `prepare_attempt1_timestamp_metadata/` and `prepare.txt`; numerical parameters did not change in the corrected preparation. `numeric_recipe` compares all numerical/source/window fields while excluding only the two actual construction-clock fields.

Source grade remains ASSUMPTION_CONDITIONAL: idealized period-end availability, retrospective action representation and surviving-stock selection, researcher-attested local rights/shared clock, and completed-hourly-close proxy labels. These checks do not establish observed publication, PIT actions/universe, executable fills, course USA500 substitution or an independent license audit.
