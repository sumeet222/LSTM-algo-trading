"""Small projected physical-year re-aggregation and derived table validation."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from . import io
from .io import (
    BASE,
    RAW,
    ROOT,
    col,
    load,
    publish,
    records,
    table,
    verify_inputs,
    write_csv,
)
from .saved import near


def main() -> None:
    global ROOT
    from decimal import Decimal

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-root", type=Path, default=ROOT)
    args = parser.parse_args()
    ROOT = args.output_root
    io.ROOT = ROOT
    out = ROOT / "runs" / args.run_id
    verify_inputs()
    accounts = load(out / "ACCOUNT_BINDINGS.json")["accounts"]
    catalog = {r["account_id"]: r for r in accounts}
    m = pd.read_csv(out / "MATCHED_PORTFOLIO_RISK_TABLE.csv")
    y = pd.read_csv(out / "ANNUAL_NAV_RISK.csv")
    context = pd.read_csv(out / "ANNUAL_AND_STOCK_CONTEXT.csv")
    pairs = pd.read_csv(out / "S2C_PAIRWISE_RISK_DELTAS.csv")
    old = pd.read_csv(BASE / "FOUR_ARM_S2C_SIZING_RESULTS.csv")
    old = table(old.loc[col(old, "population") == "MATCHED"])
    checks = []
    for a in accounts:
        account = a["account_id"]
        new = table(m.loc[col(m, "account_id") == account]).iloc[0]
        prior = table(
            old.loc[(col(old, "candidate") == a["candidate"]) & (col(old, "arm") == a["arm"])]
        ).iloc[0]
        near(
            Decimal(str(new["Sharpe"])),
            Decimal(str(prior["Sharpe_252_zero_rf"])),
            "ARCHIVED_SHARPE",
        )
        near(Decimal(str(new["max_drawdown"])), Decimal(str(prior["max_drawdown"])), "ARCHIVED_DD")
        annual = table(y.loc[col(y, "account_id") == account]).sort_values("year")
        if len(annual) != 4:
            raise ValueError("ANNUAL_CENSUS")
        net = float(col(annual, "net_PnL_USD").sum())
        near(Decimal(str(net)), Decimal(a["net_PnL_USD"]), "ANNUAL_PNL_SUM")
        near(
            Decimal(str(np.prod(1 + col(annual, "total_return").to_numpy(float)) - 1)),
            Decimal(str(new["total_return"])),
            "ANNUAL_COMPOUNDING",
        )
        checks.append(
            {
                "account_id": account,
                "archived_Sharpe_and_DD": "PASS",
                "annual_net_and_compounding": "PASS",
            }
        )
    if len(m) != 12 or len(pairs) != 9:
        raise ValueError("DERIVED_CENSUS")
    write_csv(out / "DERIVED_PARITY_CHECKS.csv", checks)
    # Existing report aggregates suffice for common-name arithmetic omission, no market reads.
    named = table(context.loc[col(context, "axis") == "COHORT_ticker"])
    omitted = []
    for p in records(pairs):
        s = table(named.loc[col(named, "account_id") == p.S2C_account])
        c = table(named.loc[col(named, "account_id") == p.control_account])
        top = table(c.loc[col(c, "net_USD") > 0]).sort_values("net_USD", ascending=False).head(2)
        ids = set(col(top, "label"))
        s_remove = float(col(table(s.loc[col(s, "label").isin(ids)]), "net_USD").sum())
        c_remove = float(col(top, "net_USD").sum())
        omitted.append(
            {
                "policy": p.policy,
                "control": p.control,
                "control_top_two_ticker_ids": "|".join(str(x) for x in col(top, "label")),
                "S2C_net_after_same_names_omitted_ARITHMETIC": p.net_PnL_USD_S2C - s_remove,
                "control_net_after_same_names_omitted_ARITHMETIC": p.net_PnL_USD_control - c_remove,
                "NOT_funded_or_fixed_capital_counterfactual": True,
            }
        )
    write_csv(out / "COMMON_CONTROL_TOP_TWO_NAME_OMISSION.csv", omitted)
    # One bounded projected re-read of 16,758 saved physical records, no price source scan.
    p = pd.read_parquet(
        RAW / "PHYSICAL_FILLS.parquet",
        columns=[
            "case",
            "order_id",
            "effective",
            "shares",
            "external_price",
            "commission",
            "print_slippage",
            "impact",
        ],
    )
    if not bool(col(p, "case").isin(catalog).all()):
        raise ValueError("UNKNOWN_PHYSICAL_CASE")
    p["year"] = (
        pd.to_datetime(col(p, "effective").to_numpy(float) * 60, unit="s", utc=True)
        .tz_convert("America/New_York")
        .strftime("%Y")
    )
    p["notional"] = abs(col(p, "shares")) * col(p, "external_price")
    rows = []
    for group, block in p.groupby(["case", "year"]):
        if not isinstance(group, tuple) or len(group) != 2:
            raise ValueError("PHYSICAL_YEAR_GROUP")
        case, year = group
        z = table(block)
        a = catalog[str(case)]
        rows.append(
            {
                "account_id": case,
                "policy": a["policy"],
                "arm": a["arm"],
                "year": year,
                "physical_orders": int(col(z, "order_id").nunique()),
                "physical_fill_rows": len(z),
                **{
                    k: float(col(z, k).sum())
                    for k in ("notional", "commission", "print_slippage", "impact")
                },
            }
        )
    write_csv(out / "ANNUAL_PHYSICAL_EXECUTION.csv", rows)
    publish(
        out / "SUPPLEMENT_RECEIPT.json",
        {
            "source": "existing PHYSICAL_FILLS projected once",
            "rows": len(p),
            "new_market_or_funded_reads": 0,
            "archived_Sharpe_DD_and_annual_book_parity": "PASS",
        },
    )


if __name__ == "__main__":
    main()
