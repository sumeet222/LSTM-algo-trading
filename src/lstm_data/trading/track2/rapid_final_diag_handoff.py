"""Render fixed descriptive conclusions from sealed economic and audit tables."""

import pandas as pd

from .rapid_exit_audit.io import as_rows
from .rapid_final_diag.policy import TREATMENTS
from .rapid_final_diag.provenance import ROOT, load
from .rapid_v1.paths import digest, publish
from .rapid_v2_diagnostics.report import csv_write

RUN = ROOT / "runs/final-diag-20261110-r1"


def write(name: str, text: str) -> None:
    with (ROOT / name).open("x") as f:
        f.write(text.strip() + "\n")


def render() -> None:
    funded = RUN / "funded"
    d = pd.read_csv(funded / "FUNDED_TARGETED_RESULTS.csv")
    s = {r.strategy_id + "_" + r.variant: r for r in as_rows(d)}
    receipt = load(RUN / "RUN_RECEIPT.json")
    decisions = []
    labels = {
        "M04": "FALSIFIED_IN_THIS_SAMPLE",
        "R01": "MECHANISM_SUPPORTED_EXPLORATORY",
        "M01": "LOW_SUPPORT",
        "M05": "MECHANISM_SUPPORTED_EXPLORATORY",
        "M03": "FALSIFIED_IN_THIS_SAMPLE",
        "R07": "LOW_SUPPORT",
    }
    lines = [
        "# Six prespecified mechanism decisions",
        "",
        "Reused 2021–2024, selected survivors, repeated inspection. Labels concern the exact",
        "diagnostic mechanism; they do not select investment algorithms or prove alpha.",
        "",
        "| ID | Control USD | Treatment USD | Delta | Net/$1M gross-year: old → new | Decision |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for sid, variant in TREATMENTS.items():
        control = sid + ("_H100" if sid == "R01" else "_CONTROL")
        a, b = s[control], s[sid + "_" + variant]
        change = b.net_PnL_USD - a.net_PnL_USD
        normalized = (
            b.net_per_1M_RTH_gross_dollar_years_USD - a.net_per_1M_RTH_gross_dollar_years_USD
        )
        decisions.append(
            {
                "test_id": "F-" + sid,
                "control": control,
                "treatment": sid + "_" + variant,
                "status": "COMPLETE",
                "decision": labels[sid],
                "net_change_USD": change,
                "normalized_net_change_per_1M_gross_year": normalized,
                "both_primary_endpoints_improved": change > 0 and normalized > 0,
                "actual_distinct_policy_change": sid != "M01",
                "final_algorithm_selected": False,
            }
        )
        lines.append(
            f"| {sid} | {a.net_PnL_USD:,.2f} | {b.net_PnL_USD:,.2f} | {change:+,.2f} | "
            f"{a.net_per_1M_RTH_gross_dollar_years_USD:,.0f} → "
            f"{b.net_per_1M_RTH_gross_dollar_years_USD:,.0f} | {labels[sid]} |"
        )
    csv_write(ROOT / "MECHANISM_DECISIONS.csv", decisions)
    lines += [
        "",
        """## M04 — two-event-check gap continuation

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
""",
    ]
    write("MECHANISM_DECISION_TABLE.md", "\n".join(lines))
    write(
        "FINAL_DIAGNOSTICS_HANDOFF.md",
        f"""# Final targeted diagnostic handoff

**Completed 6/6 prespecified treatment accounts and 7/7 unchanged controls:**
13 independent $100k continuous 2021–2024 books, one shared 48-month funded pass.
All 7 controls reproduce all 1,005 archived days and terminal totals. M01 is an
explicit identity arm because its original rule already has two confirmations.

| Mechanism | Control → treatment net USD | Interpretation |
|---|---:|---|
| M04 event confirmation | -2,117.97 → -3,615.01 | Falsified in this sample |
| R01 vintage reserve (H100) | -7,629.39 → +991.13 | Capital-feedback support, fragile |
| M01 weakening two checks | -9,003.75 → -9,003.75 | Existing rule; no new contrast |
| M05 range confirmation | -21,099.81 → -18,741.32 | Both primary endpoints improve; still poor |
| M03 capped gap trail | -11,881.76 → -13,428.23 | Tails improve, normalized net worsens |
| R07 daily confirmation | +117.01 → +445.41 | Improved but LOW_SUPPORT/concentrated |

R01/M05/R07 improve both total net and exposure-normalized net. R01 H85 remains
+$10,488.39, substantially above the guarded H100. R01 guarded primary vintage
closures fall 223→40 per 832 original candidates, but TSLA/AVGO dominate gains.
R07 depends on AAPL/TSLA. M05 loses in every year, and risk closures rise.
This is mechanism diagnosis, not persistent alpha or a final strategy selection.

The funded replay took {receipt["elapsed_seconds"]:.2f}s including export;
engine {receipt["engine"]["elapsed_seconds"]:.2f}s, peak RSS
{receipt["peak_RSS_bytes"] / 1e9:.3f} GB. Exact final storage and tests are in
FINAL_DIAGNOSTIC_CONTENT_MANIFEST.json and VALIDATION_AND_INTEGRITY.md.

A small exporter omission of three OGN physical rows was recovered exactly from
the sealed 2021 checkpoint; account results never changed and no replay was used.
Per-candidate rejection reasons were not exported; original potential keys and
aggregate budget/duplicate/other rejection counts remain explicit. Further
financial or risk improvements cannot be inferred from an unfilled key alone.

Read MECHANISM_DECISION_TABLE.md, analysis_01/PAIRED_OPPORTUNITY_AND_EXIT_DIVERGENCE.csv,
and supplement_01/ for complete physical-cost and stress checks. The 449-portion
future-reference sample is non-funded and contains risk-infeasible extensions.

**Next:** separately authorized final-design meeting: review reserve mechanics,
range persistence versus weak raw edge, and gap-tail trade-offs against unchanged
controls; freeze a small slate before new testing. All 18 remain eligible.
Fresh prospective/untouched confirmation is required for strong claims.
No final algorithms selected, no S2-C risk overlay, no Stage6 independent audit.
""",
    )
    write(
        "R01_V20_ENTRY_RESERVE_DIAGNOSTICS.md",
        """# R01 one-v20 reserve and actual capital feedback

u_i is unchanged H100 absolute provisional dollars after the existing name cap and
before integer shares. v_i is the strictly prior completed-session daily log SD
v20 from the original trailing contract; it is not an expected return. s_i=exp(v_i).
N is received marked NAV; R is original .002*N plus eligible physical-order minima.
Existing same-vintage filled plus pending absolute value x_j gives A=sum(x_j*s_j)
and L=sum(x_j*(s_j-1)). The permitted inequality is

    A + t sum(u_i s_i) <= .20 [N-R-L-t sum(u_i(s_i-1))].

Thus C=.20*(N-R-L)-A, D=sum(u_i*s_i)+.20*sum(u_i*(s_i-1)), and
t=clip(C/D,0,1) for D>0; otherwise zero. C-tD is affine decreasing. No larger
positive feasible t exists beyond the clipped root. Decimal exponential/division
uses the existing book precision. Numeric tests allow only 1e-20 rounding at the
algebraic root; financial assertions remain USD1e-7. Missing/invalid new v20 removes
the leg before budget; missing existing v20 blocks new vintage commitments. Old
positions, restrictions and liquidation are untouched. Common t precedes all
original whole-share, volume, ticket floor and short/cash checks, with no redistribution.

The 538 actual proposed leg records have t .947129–1, mean .975705, median .975054.
The same-vintage existing A/L are zero in these actual once-weekly decisions;
nonzero existing reservations are covered by synthetic witnesses, not falsely
claimed as observed market support. See funded/R01_ENTRY_RESERVES.csv for every
N/R/A/L/t, current name exposure, gross, restricted funds, old/new USD and rounded
signed shares. supplement_01/R01_STRESS_INEQUALITY_CHECKS.csv independently groups
these rows by original origin and confirms all stressed-vintage inequalities.

Unchanged H100: net -$7,629.389176; gross price $1,499.048; 618 cohorts/1,254 orders,
420 risk closures, 223 primary-vintage closures (233 with any vintage trigger).
Guarded H100: net +$991.126461; gross $10,197.5678; 538 cohorts/1,100 orders,
242 risk closures, 40 primary-vintage (50 any-trigger). Both have 832 original
weekly candidate intents. Rates: primary .268029→.048077; any .280048→.060096.
Unchanged H85: +$10,488.392222, 498 cohorts/1,016 orders, 140 risk closures and
zero vintage closures. Whole-account tags and simultaneous name/vintage causes
must not be interpreted as an individually identified causal exit.

Mean RTH gross/NAV: H10011.93%, guarded15.70%, H8516.54%. Guarding slightly smaller
commitments can leave more capital invested by avoiding disruptive cap events.
Gross exposure-year normalization also improves versus H100, but remains far
below H85. Of shared filled keys, 336 exits and 413 entry notionals differ.
114 H100-only and 34 guard-only cohorts demonstrate endogenous opportunity paths.
All marked name/vintage/aggregate/collateral rules and mandatory exits still run.

Guarded annual returns: -0.344%, +0.977%, -1.430%, +1.815%. TSLA/AVGO net $7,176
versus total $991; removing them arithmetically leaves -$6,185. This supports an
entry-reserve mechanism in this sample, not a validated momentum or sizing edge.
A next design must retain H85/H100 unchanged and explicit per-entry constraint
records. No extra buffer level, rank filter or LSTM experiment was run.
""",
    )
    write(
        "EXECUTION_COST_AND_TAIL_DIAGNOSTICS.md",
        """# Physical costs, tails and actual-price distinctions

The inherited cash change is -signed external shares*executed price-commission.
Executed price is the later valid raw open plus an adverse assumed concession.
Raw-price gross excludes that modeled concession; gross+actions-commission-spread-
impact-borrow-funding equals terminal NAV minus initial. Subtracting costs again
from executed-price gross would double charge. All 13 bridges and complete cohort
sum checks pass. Signed decision-mark→raw-open arrival is reported separately;
absolute arrival is not a fee, and a favorable movement is not a measured spread.

MICRO_PRO retains h=.0003*clip(v20/v60,.5,2), clipped1–6bp, plus prior-ADV/physical
net-size impact .0001*ratio*sqrt((abs(q)/ADV20)/.0001), clipped.25–5bp; commission
$.002/external share with no minimum. RETAIL retains assumed5bp+5bp per external
side, adverse cent rounding, $.005/share and cumulative $1 minimum once per physical
order across partials. Internal transfers pay zero external costs. Net physical
short carry remains2% ACT/365 across calendar days; base funding0. Short proceeds
are restricted. No measured midpoint, quote spread, locate or broker fill exists.

The canonical physical-cost table is supplement_01/PHYSICAL_COST_DIAGNOSTICS_COMPLETE.csv,
with ORDER_NOTIONAL_BANDS.csv and PHYSICAL_ORDERS_RECONCILIATION.csv. The regular
funded fill export omitted three OGN disposal records already charged by the
account. Exact signed quantities12/12/6, actual raw34.28, commission$1 each and
concessions survive in the content-bound 2021 checkpoint. They are added only to
the analysis supplement, preserving the original funded manifest. All physical
commission, concession, impact, notional and distinct-order counts then reconcile.
This is an export repair, not altered financial accounting or a rerun.

Median order notionals: M04 about$5,600; M01$2,947; M05about$3,200; M03about$2,900–3,000;
R01$4,691 H100/$4,993 guard/$5,619 H85; R07about$8,400. About95–98% of retail orders
bind the $1 minimum. The fee floor is physical-order level, not cohort-level.
The 0.5×/1.5× concession columns are same-holdings arithmetic, not rebudgeted or
independently funded counterfactuals. Guarded R01 becomes -$2,524 at1.5×, R07 -$347;
M05 remains deeply negative even at0.5×. No favorable quote assumption was inserted.

Full net/gross winner and loser sums, worst cohort, worst/best five and profit
factors are in analysis_01/COHORT_TAILS.csv. M03's worst-five reduction does not
improve net economics. M04's worst-five loss worsens. M05's worst-five improves
slightly but its negative gross price is a serious contrary finding. R01/R07
positive totals disappear after arithmetic removal of their two leading names.
Those removals are descriptive sensitivities, not executable portfolios.

Raw source gaps, receipt+2, standing orders, prior-minute1% participation, partial
fees and next-valid execution remain inherited. All control daily cash/exposure
and reason counts match. No material unresolved terminal exposure remains; signed
payable claims remain valued by the original conditional protocol, including
post-2024 pay metadata without post-2024 prices. Source/unknown action caveats
and conditional borrow remain. Source samples and action tests do not certify
point-in-time completeness or actual historical broker availability.
""",
    )
    write(
        "NEXT_STAGE_FINAL_DIRECTIONAL_ALGORITHM_DESIGN_HANDOFF.md",
        """# Design input only — user selection is a separate stage

All 18 original mechanisms remain context in the all-18 matrix. No final 2–3
algorithms are chosen here. The six tests were fixed before outcomes and provide
these inputs for a separately authorized design session:

| Family | Evidence to retain | Contradiction / control |
|---|---|---|
| Intermediate momentum + entry reserve | R01 vintage-feedback mechanism, exact per-entry \
ledger | H85 better; TSLA/AVGO concentration; keep H85/H100 unchanged |
| Opening-range persistence | M05 both primary endpoints improved | Still negative gross/net, \
all years lose; more risk closures |
| Confirmed opening gap | M04 definite branch support | Exact two-event confirmation worsened \
economics/tails; retain original |
| Opening-gap fade tail control | M03 worst tails reduced | Lower normalized net, stop-outs \
destroy recovering winners |
| Compression breakout | R07 small positive change | Sparse/concentrated, cost fragile; retain \
original and V2 context |
| Intraday / cross-sectional continuation | M01 unchanged two-check identity; M06 existing \
context | No new slower M01 rule tested, no M06 funded run |

The next meeting should freeze a SMALL candidate slate with one mechanism change
per proposed algorithm, immutable original controls and common within-mode costs,
entry opportunities, caps, outcome and source rules. Do not blend successful
pieces from these historical paths into an untested proclaimed winner. Keep the
negative mechanisms and all other12 original IDs visible. A prospective or genuinely
untouched period needs separately documented authorization and source contract
before any strong claim. No such prices were read here.

Controls must distinguish entry reserve from altered concentration, discretionary
exit from hard solvency, and intended horizon from realized holdings. Require both
net dollars and gross-exposure-year economics, risk-trigger/entry denominators,
negative tails, annual/side/name stability, complete fees/actions/claims and
opportunity divergence. A smaller risk count alone does not establish value.
Maintain source/cap ledgers and test unfavorable hypotheses without changing
thresholds in response to outcomes.

S2-C entry sizing remains on HOLD until the user commits a directional baseline.
Its frozen original 240-minute absolute-magnitude target is not a ten-session
variance or direction forecast. No neural overlay, fit, auxiliary signed head,
Phase2 substitution or independent Stage6 validation occurred in this task.
""",
    )
    write(
        "ISSUES_AND_LIMITATIONS.md",
        """# Explicit issues and limits

- FD-001: M01's requested two-check weakening policy was already executed in V3.
  Its funded arm is an exact identity result. A third check was not authorized.
- FD-002: independent original weakening/trail/reversal/risk can preempt event
  confirmation. Fewer event labels do not prove the intended hold effect.
- FD-003: three OGN physical-fill export rows were absent from regular captures.
  Exact checkpoint recovery closes all physical money/count bridges; funded
  performance and original outputs remain unchanged. See supplement_01.
- FD-004: all causal potential opportunities and filled keys are matched, but
  per-unfilled-key rejection reasons are not identifiable from compact exports.
  Aggregate duplicate/budget/minimum/cutoff/missing counters are preserved. Do not
  assign a cap cause to an unfilled key by inference.
- FD-005: primary risk cause follows a whole-account liquidation. Any-vintage and
  primary-vintage counts differ; neither isolates a name-specific causal effect.
- FD-006: the offline hash sample449 portions/1347 references is deliberately
  bounded and unweighted. It is not a population-dollar estimate or funded path.
  No action/carry oracle is substituted for the true book. M01 has no changed exits.
- FD-007: pilot cutoff retains known open positions. Seven pilot summary HOLDs
  mean incomplete terminal horizons at a diagnostic slice, not unknown NAV or a
  passed full strategy. Every full-period account is COMPLETE after reconciliation.
- FD-008: repeated2021–24, survivor universe, retrospective source/action cleaning,
  assumed receipt, no NBBO/queue/locates, conditional borrow and dividends remain.
  Statistical independence, untouched-OOS and deployment are not established.
- FD-009: Git fetch could not write sandbox-protected .git/FETCH_HEAD. Local
  upstream state was0/0. No pull/reset/stash/commit/push occurred. Read-only process
  inspection found no active matching job before launch.
- FD-010: full installed-Pylance results remain a repository qualification; details
  in VALIDATION_AND_INTEGRITY.md distinguish frozen errors from owned checks.
""",
    )
    # Tiny root copies make canonical requested summaries easy to discover.
    for name, path in (
        ("FUNDED_TARGETED_RESULTS.csv", funded / "FUNDED_TARGETED_RESULTS.csv"),
        (
            "ALL18_CONTEXT_AND_FINAL_DIAGNOSTIC_MATRIX.csv",
            ROOT / "analysis_01/ALL18_CONTEXT_AND_FINAL_DIAGNOSTIC_MATRIX.csv",
        ),
    ):
        with (ROOT / name).open("xb") as f:
            f.write(path.read_bytes())
    publish(
        ROOT / "REPORT_BUILD_RECEIPT.json",
        {
            "status": "COMPLETE",
            "funded_manifest_sha256": digest(funded / "FUNDED_MANIFEST.json"),
            "mechanisms": decisions,
            "no_final_selection": True,
            "no_S2C": True,
            "no_Stage6": True,
        },
    )


if __name__ == "__main__":
    render()
