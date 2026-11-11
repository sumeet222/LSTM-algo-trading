"""Publish compact human review of frozen risk tables, without new financial runs."""

import argparse
from pathlib import Path

from . import io
from .io import ROOT, csv_rows, load, publish, write_csv

TICKERS = (
    "VZ COP BAC BA AAPL PEP MRK SBUX CVX MS AMD KO JNJ AMZN XOM WFC AVGO TSLA MA CSCO"
).split()


def md_table(headers: list[str], rows: list[list]) -> str:
    return "\n".join(
        [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join("---" for _ in headers) + " |",
            *["| " + " | ".join(str(v) for v in row) + " |" for row in rows],
        ]
    )


def put(name: str, text: str) -> None:
    with (ROOT / name).open("x") as f:
        f.write(text.strip() + "\n")


def main() -> None:
    global ROOT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-root", type=Path, default=ROOT)
    args = parser.parse_args()
    ROOT = args.output_root
    io.ROOT = ROOT
    out = ROOT / "runs" / args.run_id
    risk = csv_rows(out / "MATCHED_PORTFOLIO_RISK_TABLE.csv")
    pairs = csv_rows(out / "S2C_PAIRWISE_RISK_DELTAS.csv")
    dist = csv_rows(out / "COHORT_WIN_LOSS_CONCENTRATION.csv")
    receipts = load(out / "ANALYSIS_RECEIPT.json")
    accounts = load(out / "ACCOUNT_BINDINGS.json")["accounts"]
    source = load(ROOT / "SOURCE_REGISTER_BEFORE.json")
    links = f"runs/{args.run_id}/"
    rows = []
    for r in risk:
        rows.append(
            [
                r["policy"],
                r["arm"],
                f"{float(r['net_PnL_USD']):+,.2f}",
                f"{float(r['Sharpe']):.3f}",
                f"{float(r['Sortino']):.3f}",
                *[
                    f"{100 * float(r[k]):.3f}%"
                    for k in (
                        "annual_volatility",
                        "drawdown_severity",
                        "ES95_loss",
                        "mean_RTH_gross_fraction",
                    )
                ],
            ]
        )
    base_table = md_table(
        [
            "Policy",
            "Arm",
            "Net USD",
            "Sharpe",
            "Sortino",
            "Vol/yr",
            "Max DD loss",
            "ES95/day loss",
            "Mean RTH gross",
        ],
        rows,
    )
    categories = [
        ("Net USD", "net_PnL_USD", 1),
        ("Sharpe", "Sharpe", 1),
        ("Sortino", "Sortino", 1),
        ("Vol %/yr", "annual_volatility", 100),
        ("DD loss %", "drawdown_severity", 100),
        ("ES95 loss %", "ES95_loss", 100),
        ("Net/1M gross-yr", "net_per_1M_RTH_gross_year", 1),
        ("Gross %", "mean_RTH_gross_fraction", 100),
        ("Cost USD", "total_cost_USD", 1),
        ("Orders", "physical_order_count", 1),
    ]
    rows = []
    for p in pairs:
        row = [p["policy"], p["control"]]
        for _, k, scale in categories:
            s, c = float(p[k + "_S2C"]), float(p[k + "_control"])
            delta = p[k + "_improvement"]
            suffix = f"; Δ+ {float(delta) * scale:+.3f}" if delta else "; descriptive"
            row.append(f"{s * scale:.3f}/{c * scale:.3f}" + suffix)
        rows.append(row)
    paired_table = md_table(["Policy", "Control", *[c[0] for c in categories]], rows)
    put(
        "WHAT_DID_S2C_IMPROVE.md",
        f"""# What did S2-C improve?

Status: PARTIAL_WITH_EXPLICIT_MISSING_FIELDS. All 12 saved matched books and all nine
comparisons are analyzed; unavailable exposure/mark/action fields are listed below.
No new portfolio, market-price extraction, neural inference or strategy selection ran.

{base_table}

Each pair cell below is S2C/control. Δ+ is the improvement-oriented difference:
higher net/Sharpe/Sortino/efficiency is better; lower volatility, DD loss, ES or cost is
better. Exposure and order counts are descriptive, not a preference. Values are
rounded only here; CSV retains full float precision and exact terminal Decimal strings.

{paired_table}

**R01-A: MIXED versus EQUAL, no general risk improvement.** S2C loses $705.02 less and
improves Sharpe/Sortino versus EQUAL, with 4.53% less mean RTH gross exposure. Its
max DD worsens from 11.51% to 12.49%; ES95 worsens, while ES99 improves marginally.
It loses more than rolling ($307.46) and EWMA ($572.81), with higher native volatility,
worse DD and ES95 than either. Exposure efficiency improves versus equal and only
slightly versus rolling, but not EWMA. Costs rise versus all controls. It improves
annual returns versus EQUAL in 2021 only. Net losses in all arms preclude an alpha claim.

**M04-T480: NO UNIVERSAL BENEFIT; MIXED only versus EWMA.** S2C turns the positive
EQUAL/rolling outcomes into a $2,036.51 loss, and worsens Sharpe/Sortino versus both.
Volatility falls slightly versus EQUAL/rolling, but DD and ES95 worsen versus EQUAL.
Versus rolling DD improves by only 0.0068 percentage points and ES95 improves, while
ES99 worsens. Versus EWMA, net improves $531.00 but volatility, DD, ES95 and ES99
worsen. S2C has more mean gross exposure than every control, so its losses are not
explained by simply investing less. Lower costs versus equal/rolling do not rescue it.

**R07-PERSIST: MIXED, encouraging mean/efficiency but weak risk dominance.** S2C has
the best native net, Sharpe, Sortino and DD, with lower mean exposure than all controls,
but native volatility is higher than all three. ES95 improves versus equal/EWMA but
worsens versus rolling; ES99 improves versus EWMA but worsens versus equal/rolling.
Versus rolling the $127.68 gain decomposes into $21.80 less price P&L, $153.98 more
signed action value and $4.50 more costs. It wins annual return versus rolling in
2022 only. After arithmetic omission of its top two profitable stocks (TSLA/AMD),
S2C net is just $41.08; rolling's own-top-two omission leaves $697.10. These are
separate descriptive omissions, not funded portfolios or matched subsets.

**Lower exposure is an incomplete explanation.** On each control's worst 5% dates,
S2C's paired mean return is better in all nine comparisons; it is worse on each
control's best 5% dates. These are retrospective control-selected dates, not an
implementable hedge. On rolling R07's worst 1%, S2C is worse. Native marginal ES
differences must not be interpreted as conditional protection. Constant mean-exposure
scaling of S2C already-net daily returns is explicitly NONEXECUTABLE: R07 at EQUAL
exposure has DD 2.264% versus EQUAL 2.261%, and ES95 0.1874% versus 0.1822%; at
rolling exposure its DD is 2.103% versus 2.101%, and ES95 0.1740% versus 0.1700%.
Thus its native drawdown advantage is largely associated with lower exposure in
those comparisons. Mean-exposure and native-volatility normalizers are reported
separately, without changing orders/fees or claiming feasible scaled performance.

Channels are independently labeled in `{links}CHANNEL_ASSESSMENTS.csv`; no composite
score or new winner selection is used. Full-period improvements conflicting with
annual evidence are MIXED. Four annual and 48 monthly paired descriptors replace
inferential claims; no optional bootstrap or Stage 6 audit was run.

These repeatedly inspected 2021–24 fixed-survivor results are exploratory. Original
S2-C predicts 240-scheduled-minute endpoint absolute movement, not direction,
conditional variance, or full multiday-hold risk. Unmeasured NBBO/locates, assumed
receipt and retrospective action/QA vintages remain material limitations.
""",
    )
    put(
        "INPUT_AND_ACCOUNT_BINDINGS.md",
        f"""# Input and account bindings

Canonical source: `trading/track2/final_directional_slate_v1/analysis_03`, backed by
`runs/sizing-matched-20261110-r1/results`. The final root content manifest validates
relevant inputs. `SOURCE_REGISTER_BEFORE.json` binds {len(source["files"])} paths with
SHA256, byte size, mtime, role and available row count. Model/protocol anchors are
hashed; no model weights or underlying market-source partitions are read.

`{links}ACCOUNT_BINDINGS.json` lists exact 12 case IDs, run ID, protocol hash, policy,
arm, population and all original Decimal terminal components. Joining uses the sealed
RESULTS `strategy_id + '_' + variant`; raw cohort `arm` is a book ID and `population`
is economic mode, so neither is used as an arm/sample key. Daily candidate/arm rows
are attached to the verified catalog after the 12-book/1,005-session check.

"""
        + md_table(
            ["Policy", "Arm", "Account ID", "Net USD exact", "Protocol SHA"],
            [
                [a["policy"], a["arm"], a["account_id"], a["net_PnL_USD"], a["protocol_hash"]]
                for a in accounts
            ],
        )
        + """

Primary population is MATCHED throughout. The 24-row source containers also hold
ATTAINABLE; those rows are excluded from paired financial analysis. Original readiness
counts are published separately in MATCHED_OPPORTUNITY_COUNTS.csv. Parent R01 H85
+$10,488.39 is not the matched EQUAL book: its causal opportunity population differs.
This task neither recomputes alpha eligibility nor changes its frozen availability.
""",
    )
    put(
        "COMPARISON_OF_3_POLICIES.md",
        f"""# Three policies at native portfolio risk

{base_table}

All accounts are separate $100k books, continuous across 2021–24. Their USD results
must not be summed into a fund. R01 uses weekly six-minus-one-month cross-sectional
momentum and dynamic exits; M04 uses confirmed gap continuation with a fixed nominal
480 scheduled-minute exit; R07 uses weekly compression breakout with two daily failure
checks and dynamic exits. Parent entry/exit/cost policies are unchanged by this task.

Risk sizing changes exposure, integer rounding, filled opportunities, constraints and
later exits, so matched input eligibility is not identical holdings. Funded opportunity
joins show R01 S2C/EQUAL shared 306, equal-only 26 and S2C-only 37; M04 shared 1,466,
equal-only 133 and S2C-only 144. R07 has the same 60 funded opportunity keys in every
arm, yet 25 of its S2C/EQUAL shared final exit times differ. Exact dollar allocation of
rounding versus risk reservations is not identifiable without the original reservation
snapshots, and is not reconstructed here.

The small R07 account has about 1.6–1.7% mean RTH gross exposure and 60 closed cohorts
per arm. Exposure-normalized dollar ratios can therefore look large; they are not
leveraged portfolio returns. R01 is negative in all four arms; M04's mode-specific
hypothetical micro costs differ from conservative retail and are not a fair cost switch.

See WHAT_DID_S2C_IMPROVE.md for nine dimension-by-dimension comparisons, plus paired
tail dates, annual/monthly differences, drawdown intervals and normalization CSVs.
""",
    )
    concentration = []
    for d in dist:
        concentration.append(
            [
                d["policy"],
                d["arm"],
                "/".join(TICKERS[int(x)] for x in d["top_two_net_ticker_ids"].split("|")),
                f"{float(d['net_without_top_two_ARITHMETIC_ONLY']):+,.2f}",
            ]
        )
    put(
        "CONCENTRATION_AND_ECONOMIC_LIMITATIONS.md",
        """# Concentration and economic limitations

"""
        + md_table(
            [
                "Policy",
                "Arm",
                "Own top-two net-positive names",
                "Net after omission, USD (ARITHMETIC ONLY)",
            ],
            concentration,
        )
        + """

Closed-cohort net allocations reconcile to account net and include execution cost,
borrow, funding and signed action allocations. Gross winners/losers use raw signed
price P&L; net winners/losers use allocated cohort cash P&L. They are different
classifications. Fees are already included in `cost`, not subtracted twice. Orders may
serve multiple virtual cohorts; per-cohort costs are the engine's deterministic
allocation, not independent broker orders. Per-ticker, side, slot, entry/exit year,
cohort-span overnight and exit-reason projections are alternate lifetime allocations:
never add those views, and never treat a lifetime cohort exit-year sum as yearly NAV.

M04's primary matched 155 earlier partial-risk cohorts have an unavailable earlier
specific risk cause after a later final policy close (38/42/40/35 by arm); generic
RISK_OTHER_CAP is not proof of an aggregate-cap breach. Any-risk count, final-risk
count and policy-final count differ. A cohort's risk label need not identify the
portfolio constraint that triggered whole-account liquidation. Dynamic `early_exits`
semantics do not imply the absence of risk closures.

Annual marked NAV and costs are supported. Calendar-year raw-price/action separation,
exact action events on worst days, per-stock marked exposure, gross long/short physical
exposure, minute-exact invested time, cap utilization and complete post-reservation
buying power are NOT_IDENTIFIABLE_FROM_SAVED_OUTPUTS. Required minimal additional
saved fields: per-timestamp physical symbol quantities/marks with receipt times,
reservation balances and binding constraint IDs; action ex/pay/claim cash postings;
cohort-to-physical-order allocation keys. No source extraction or replay is authorized
or performed. Tail-day claim changes include revaluation/settlement and are not
invented action cash flow. Closing signed net inventory does not measure gross risk.

RTH filled-virtual exposure and overnight ACT/365 carry use different clocks. Mean
unrestricted cash before pending reservations is a cash proxy, not actual idle buying
power or investable leverage. Dollar-exposure-year normalization does not prove alpha
or a superior multiday variance forecast. No IID-trade inference, p-values, untouched
confirmation, fee calibration, strategy optimization or Stage 6 audit occurred.
""",
    )
    # Separate algebraic decomposition is an alternative view, never another subtraction.
    decomposed = []
    for p in pairs:
        s = next(r for r in risk if r["policy"] == p["policy"] and r["arm"] == "S2C_RISK")
        c = next(r for r in risk if r["policy"] == p["policy"] and r["arm"] == p["control"])
        decomposed.append(
            {
                "policy": p["policy"],
                "control": p["control"],
                **{
                    k + "_S2C_minus_control": float(s[k]) - float(c[k])
                    for k in (
                        "net_PnL_USD",
                        "gross_price_PnL_USD",
                        "action_value_USD",
                        "total_cost_USD",
                        "commission_USD",
                        "print_concession_USD",
                        "impact_USD",
                        "borrow_USD",
                    )
                },
            }
        )
    write_csv(out / "PAIRED_PRICE_ACTION_COST_BRIDGE.csv", decomposed)
    put(
        "COMPLETION_HANDOFF.md",
        f"""# Completion handoff

PARTIAL_WITH_EXPLICIT_MISSING_FIELDS: all 12 matched accounts, 12,060 daily valuations,
8,029 closed cohorts, 16,758 physical fill records and nine paired comparisons were
analyzed from saved outputs. All available financial identities pass; maximum daily
and terminal residual is ${receipts["maximum_daily_and_terminal_residual_USD"]} against
$1e-7 tolerance. No new trading/neural run or market-data read occurred.

R01: less loss than EQUAL, worse drawdown/ES95, no dominance over rolling/EWMA.
M04: worse than profitable EQUAL/rolling; mixed against negative EWMA. R07: higher
native net/Sharpe/Sortino and smaller DD, but higher volatility, tiny action-sensitive
advantage over rolling and strong concentration. Mean-exposure scaling erases its
native DD advantage versus EQUAL/rolling. No robust universal sizing benefit follows.

Main aggregation took {receipts["elapsed_seconds"]:.3f} seconds; peak process RSS
{receipts["peak_RSS_bytes_macOS"] / 1e6:.2f} MB. Final manifest records total new evidence
bytes and test/type receipts. See WHAT_DID_S2C_IMPROVE.md for levels and all controls;
CONCENTRATION_AND_ECONOMIC_LIMITATIONS.md lists exact unsupported fields and minimal
saved-record requirements. Analysis_01 is immutable; final formatting/type-only code
changes are separately hashed with no altered numerical policy or rerun of accounts.

Next step: retain these policies/controls unchanged and preregister a prospective or
genuinely untouched matched sizing comparison, including downside-tail and exposure
endpoints, costs/actions and the 240-minute versus held-horizon limitation. Independent
Stage 6 remains separate. No new baseline selection or S2-C model claim is made.
""",
    )
    publish(
        ROOT / "REPORT_RECEIPT.json",
        {
            "run_id": args.run_id,
            "report_scope": (
                "Saved-output descriptive tables only; no new trading/model calculations"
            ),
        },
    )


if __name__ == "__main__":
    main()
