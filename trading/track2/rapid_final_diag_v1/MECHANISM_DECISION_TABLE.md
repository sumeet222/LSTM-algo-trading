# Six prespecified mechanism decisions

Reused 2021–2024, selected survivors, repeated inspection. Labels concern the exact
diagnostic mechanism; they do not select investment algorithms or prove alpha.

| ID | Control net USD | Treatment net USD | Delta net | Net / $1M RTH gross-year: control → treatment | Decision |
|---|---:|---:|---:|---:|---|
| M04 | -2,117.97 | -3,615.01 | -1,497.04 | -47,875 → -76,501 | FALSIFIED_IN_THIS_SAMPLE |
| R01 | -7,629.39 | 991.13 | +8,620.52 | -170,773 → 16,006 | MECHANISM_SUPPORTED_EXPLORATORY |
| M01 | -9,003.75 | -9,003.75 | +0.00 | -227,002 → -227,002 | LOW_SUPPORT |
| M05 | -21,099.81 | -18,741.32 | +2,358.49 | -252,168 → -199,294 | MECHANISM_SUPPORTED_EXPLORATORY |
| M03 | -11,881.76 | -13,428.23 | -1,546.47 | -165,682 → -277,714 | FALSIFIED_IN_THIS_SAMPLE |
| R07 | 117.01 | 445.41 | +328.40 | 12,548 → 42,675 | LOW_SUPPORT |

## M04 — two-event-check gap continuation

The original entry requires abs(gap_z)>=1, received first-hour confirmation with
the same gap sign and cumulative volume ratio>1, at slots1–3. It retains the entry
day opening reference. The treatment defers only its support-failure event, not
weakening, reversal, trail, risk or 780-minute maximum. There were 687 deferred
checks and 103 recoveries, providing real branch support; independent exits often
preempted the confirmation. Net worsened $1,497.04 and normalized net worsened.
Risk-closed cohorts increased 604→685. Worst net cohort deteriorated -$591→-$690;
worst five -$2,715→-$3,094. Annual returns improved slightly in 2021/2024 but worsened
in 2022/2023. The shared-opportunity set has 1,752 entries in both arms, 95 control-only
and 88 treatment-only; 997 shared exits changed. The funded difference includes
capacity and later-entry feedback, not just waiting on the same lots.

The bounded +240 offline sample has $294 price upside net of downside on forced
exits but -$1,198 on non-forced exits; these are isolated quantities, not feasible
portfolio gains. Earlier M04/V2 T480 +$1,454 remains a different policy context.
This particular confirmation does not support carrying forward a generic hold-longer
rule. Do not compensate with a third confirmation or cheaper costs here.

## R01 — one-v20 vintage reserve

The six-minus-one-month log score/ranking, weekly scan, H100 name caps, native exits
and ten-session maximum are unchanged. Guarded H100 improves -$7,629.39 to +$991.13;
net per $1M gross RTH dollar-year improves -$170,773→+$16,006. Gross price rises
$1,499.05→$10,197.57. Primary vintage-tagged closures fall 223→40 per 832 candidate
intents; any-vintage-trigger risk closures fall 233→50. All risk-closed cohorts fall
420→242. Hard prospective liquidation remains active. H85 remains substantially
better at +$10,488.39 and +$153,476 per $1M gross-year with 140 risk closures.

The common scale averages .9757, so this is approximately a 2.4% entry buffer, not
a renamed H85 allocation. Gross exposure increases 11.93%→15.70% despite smaller
initial commitments, supporting the capital-feedback mechanism. There are 504
shared funded opportunities, 114 H100-only and 34 guarded-only; 336 shared exits
change. These endogenously different paths prevent a pure dollar decomposition
into causal name/risk contributions. The guarded account is negative in 2021/2023,
positive in 2022/2024. TSLA/AVGO contribute $7,176; arithmetic removal yields -$6,185.
Its five best cohorts contribute $6,409, far above the $991 total. Half-again the
assumed concession changes same-holdings arithmetic net to -$2,524.40. Capital
feedback has descriptive support; persistent directional profitability does not.

## M01 — requested rule already exists

The original continuation uses received r60, standardized by past same-slot scale,
with abs(z)>=1 at slots1–6. Its native dynamic weakening already requires two
successive valid micro checks, aligned strength <=50% of entry, below 1, and at
least 60 scheduled minutes of age. Decisive reversal separately requires two
checks. The actual scheduler invokes each received frame once. Missing eligible
scores reset the streak. The requested treatment therefore makes no policy change.
Both accounts are exactly -$9,003.75, with 6,007 cohorts, 12,348 external orders,
568 risk closures and identical daily economics. This is an identity result, not
a failed test of a newly invented slower exit. No third check was authorized.
M06 remains non-funded context in the all-18 historical matrix.

## M05 — range failure confirmation

The original completed 09:30–10:00 opening range and 5bp breakout buffer, slots1–4,
entry direction and costs remain intact. Only EVENT_RESOLVED waits for two distinct
valid boundary-failure observations; reversal/trail/weakening/risk remain eligible.
There are 3,425 deferred checks and 664 recoveries. Net improves $2,358.49, and
normalized net improves -$252,168→-$199,294 per $1M gross-year. Worst cohort and
worst-five losses improve modestly. Gross price remains negative (-$1,746.90), and
net remains a substantial -$18,741.32. All four years lose; 2022 worsens. Exposure
increases 22.66%→25.74%, external orders 11,909→12,024 and risk closures 1,192→1,825.
The mechanism did not reduce ordering or solve raw directional weakness.

There are 5,587 shared entries, 412 control-only, 418 treatment-only and 3,868 shared
exits changed. The offline +240 sample is positive by $208 non-forced and $70 forced,
with both substantial missed gains and avoided losses. These samples are not a
capital-feasible return and cannot establish why the full funded difference arose.
The exact mechanism has descriptive economic support, with severe remaining losses
and risk feedback. It is design input, not a selected baseline or viable strategy.

## M03 — one causal gap-volatility stop cap

The entry remains the >=1-standardized opening gap fade, slots0/1. The trail is
fixed at entry to min(2*v20, abs(gap/gap_z)) in log units. No hindsight stop fill,
new gap threshold or price-path filter is used. The cap improves worst net cohort
-$1,741→-$1,014 and worst five -$4,926→-$2,569, but total net worsens $1,546.47 and
normalized net worsens -$165,682→-$277,714 per $1M gross-year. Winning dollars drop
$113,962→$95,833; the win rate drops 54.6%→46.4%. Lower exposure and fewer risk exits
740→437 are insufficient: funded economic falsification takes precedence over a
better worst trade. External orders increase 7,556→7,769. No alternate stop multiplier
was tried. The modified future-reference sample has more avoided loss than upside
at +240; it cannot rescue the actual funded economics. Retain the tail insight as
an unresolved trade-off, not as justification to optimize another cap now.

## R07 — sparse channel persistence

Compression remains an entry qualifier only; weekly entries, 5bp frozen channel
failure band, conservative retail costs, trail and ten-session maximum are fixed.
Daily checks are full-session slot1, distinct sessions; half days do not fabricate
observations. There are 38 deferred checks and five recoveries. Net improves
$117.01→$445.41; normalized net $12,548→$42,675 per $1M gross-year. All 94 funded
opportunities are shared, 40 exits change, orders fall 193→191 and risk closures
27→25. The 2021/2023 returns worsen, and the worst-five loss worsens slightly.
AAPL/TSLA contribute $1,900; removing them arithmetically gives -$1,454. The gain is
small relative to friction uncertainty (1.5× concession arithmetic gives -$347).
The +240 sample has +$321 non-forced raw continuation but -$693 on risk-forced
portions. V2 3/5-session positives are context, not matched tests. LOW_SUPPORT is
appropriate despite improved primary values; no new horizon was adopted.

## Common confounds and source support

All controls pass exact 1,005-day economics, exposure and terminal count parity.
Complete new cohort rows sum to each account's gross/actions/net; physical-order
costs and turnover also sum after three checkpoint-recovered OGN rows. Risk labels
can follow whole-account liquidation and are not an individual causal constraint
attribution. Each funded account has independent capital. No totals across them
represent one portfolio. Sample later marks cover 449 portions × three fixed
references = 1,347 valid targets, all raw-to-raw and offline-only. Risk-forced
extensions are explicitly infeasible under the realized limit. Neither they nor
signed/absolute arrival movement are added as funded profits or extra fees.
