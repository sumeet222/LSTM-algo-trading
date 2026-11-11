"""Validated settled-record join; never import or call a trading engine."""

from dataclasses import dataclass
from decimal import Decimal

import exchange_calendars as xcals
import numpy as np
import pandas as pd

from .io import ARMS, BASE, POLICIES, RAW, col, csv_rows, load, records, table, verify_inputs

D = Decimal
TOL = D("1e-7")


@dataclass
class SavedData:
    accounts: list[dict]
    days: pd.DataFrame
    cohorts: pd.DataFrame
    fills: pd.DataFrame
    checks: list[dict]
    opportunities: pd.DataFrame
    calendar: pd.DataFrame


def validate_keys(pairs: set[tuple]) -> None:
    if pairs != {(f, a) for f in POLICIES for a in ARMS} or len(pairs) != 12:
        raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION ACCOUNT_CENSUS")


def near(a: D, b: D, label: str) -> D:
    residual = a - b
    if not a.is_finite() or not b.is_finite() or abs(residual) > TOL:
        raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION " + label + " " + str(residual))
    return residual


def load_saved() -> SavedData:
    verify_inputs()
    anchors = csv_rows(RAW / "RESULTS.csv")
    validate_keys({(r["candidate"], r["arm"]) for r in anchors})
    if len(anchors) != 12:
        raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION DUPLICATE_ACCOUNT")
    run = load(BASE / "runs/sizing-matched-20261110-r1/RUN_RECEIPT.json")
    reg = load(BASE / "OVERLAY_RUN_REGISTRY.json")
    if (
        run["registry"] != reg["identity"]
        or run["population"] != "MATCHED"
        or run["sessions"] != 1005
    ):
        raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION REGISTRY_BINDING")
    canonical = csv_rows(BASE / "FOUR_ARM_S2C_SIZING_RESULTS.csv")
    canonical = {(r["candidate"], r["arm"]): r for r in canonical if r["population"] == "MATCHED"}
    source_days = pd.read_parquet(RAW / "DAILY_NAV.parquet")
    combined = pd.read_parquet(BASE / "analysis_03/COMBINED_DAILY_NAV.parquet")
    combined = table(combined.loc[col(combined, "population") == "MATCHED"]).copy()
    cohort = pd.read_parquet(RAW / "COHORTS.parquet")
    fills = pd.read_parquet(RAW / "PHYSICAL_FILLS.parquet")
    # The account catalog is authoritative; raw cohort arm/population are book/mode fields.
    accounts = []
    checks = []
    catalog = {}
    for r in anchors:
        f, a = r["candidate"], r["arm"]
        if r["population"] != "MATCHED" or r["label"] != POLICIES[f] or r["status"] != "COMPLETE":
            raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION WRONG_POLICY")
        case = r["strategy_id"] + "_" + r["variant"]
        catalog[case] = {"candidate": f, "arm": a, "population": "MATCHED", "account_id": case}
        d = table(
            source_days.loc[(col(source_days, "candidate") == f) & (col(source_days, "arm") == a)]
        )
        c = table(combined.loc[(col(combined, "candidate") == f) & (col(combined, "arm") == a)])
        if len(d) != 1005 or len(c) != 1005 or list(col(d, "date")) != list(col(c, "date")):
            raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION DAILY_CENSUS")
        for key in (
            "nav",
            "cash",
            "restricted",
            "claims",
            "physical_value",
            "special",
            "virtual_gross",
            "commission",
            "friction",
            "borrow",
            "funding",
            "gross_dollar_minutes",
            "gross_NAV_minutes",
            "spendable_cash_NAV_minutes",
            "RTH_minutes",
        ):
            x = col(d, key).to_numpy(float)
            y = col(c, key).to_numpy(float)
            if not np.isfinite(x).all() or not np.allclose(x, y, atol=1e-7, rtol=1e-12):
                raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION CANONICAL_DAY " + key)
        if not col(d, "status").eq("OBSERVED").all() or not col(d, "nav").gt(0).all():
            raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION UNKNOWN_MARK_OR_WEALTH")
        dates = list(col(d, "date").astype(str))
        if dates != sorted(set(dates)):
            raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION SESSION_ORDER")
        for z in records(d):
            resid = near(
                D(str(z.nav)),
                sum(
                    (
                        D(str(getattr(z, k)))
                        for k in ("cash", "claims", "physical_value", "special")
                    ),
                    D(0),
                ),
                case + " DAILY_NAV " + str(z.date),
            )
            checks.append(
                {
                    "account_id": case,
                    "scope": "DAILY_NAV",
                    "date": z.date,
                    "residual_USD": str(resid),
                }
            )
        if D(r["terminal_pending"]) or D(r["terminal_stock_symbols"]):
            raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION TERMINAL_POSITION_OR_ORDER")
        expected = D(100000) + D(r["net_PnL_USD"])
        cash = D(r["terminal_cash_USD"])
        claims = D(r["terminal_claims_USD"])
        for scope, x, y in (
            ("TERMINAL_CASH_CLAIM", cash + claims, expected),
            ("FINAL_NAV", D(r["final_NAV_USD"]), expected),
            ("LAST_DAILY_NAV", D(str(d.iloc[-1]["nav"])), expected),
            (
                "PRICE_ACTION_COST",
                D(r["gross_signed_price_PnL_USD"])
                + D(r["gross_action_value_USD"])
                - sum(
                    (
                        D(r[k])
                        for k in (
                            "commission_USD",
                            "assumed_spread_USD",
                            "assumed_impact_USD",
                            "borrow_USD",
                            "funding_USD",
                        )
                    ),
                    D(0),
                ),
                D(r["net_PnL_USD"]),
            ),
        ):
            checks.append(
                {
                    "account_id": case,
                    "scope": scope,
                    "date": dates[-1],
                    "residual_USD": str(near(x, y, case + " " + scope)),
                }
            )
        for key in (
            "net_PnL_USD",
            "final_NAV_USD",
            "gross_signed_price_PnL_USD",
            "gross_action_value_USD",
            "commission_USD",
            "assumed_spread_USD",
            "assumed_impact_USD",
            "borrow_USD",
            "funding_USD",
            "cohorts",
            "external_orders",
            "executed_turnover_USD",
        ):
            near(D(r[key]), D(canonical[f, a][key]), case + " CANONICAL " + key)
        accounts.append(
            {
                **r,
                "account_id": case,
                "policy": POLICIES[f],
                "run_id": "sizing-matched-20261110-r1",
                "protocol_hash": run["registry"],
                "five_registry_sha256": reg["five_registry_sha256"],
            }
        )

    def bind(frame: pd.DataFrame) -> pd.DataFrame:
        result = frame.copy()
        if not col(result, "case").isin(catalog).all():
            raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION UNKNOWN_CASE")
        result["raw_arm"] = col(result, "arm")
        result["raw_population"] = col(result, "population")
        for field in ("candidate", "arm", "population", "account_id"):
            result[field] = col(result, "case").map({k: v[field] for k, v in catalog.items()})
        return result

    cohort = bind(cohort)
    fills = bind(fills)
    if col(cohort, "key").duplicated().any() or col(cohort, "entry_at").isna().any():
        raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION COHORT_ID_OR_ENTRY")
    for r in accounts:
        t = table(cohort.loc[col(cohort, "account_id") == r["account_id"]])
        p = table(fills.loc[col(fills, "account_id") == r["account_id"]])
        for field, target in (
            ("cash_pnl", "net_PnL_USD"),
            ("gross_signed_price_pnl", "gross_signed_price_PnL_USD"),
            ("gross_action_cash", "gross_action_value_USD"),
            ("borrow", "borrow_USD"),
            ("funding", "funding_USD"),
            ("fees", "commission_USD"),
        ):
            if col(t, field).isna().any():
                raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION COHORT_NAN")
            near(D(str(float(col(t, field).sum()))), D(r[target]), r["account_id"] + " " + field)
        for field, target in (
            ("commission", "commission_USD"),
            ("print_slippage", "assumed_spread_USD"),
            ("impact", "assumed_impact_USD"),
        ):
            near(D(str(float(col(p, field).sum()))), D(r[target]), r["account_id"] + " " + field)
        near(
            D(str(float((abs(col(p, "shares")) * col(p, "external_price")).sum()))),
            D(r["executed_turnover_USD"]),
            r["account_id"] + " NOTIONAL",
        )
        if len(t) != int(r["closed_cohorts"]) or col(p, "order_id").nunique() != int(
            r["external_orders"]
        ):
            raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION COHORT_OR_ORDER_COUNT")
        # Costs are already embedded in cash; this is a check, not a second charge.
        residual = (
            col(t, "gross_signed_price_pnl")
            + col(t, "gross_action_cash")
            - col(t, "cost")
            - col(t, "borrow")
            - col(t, "funding")
            - col(t, "cash_pnl")
        )
        if abs(residual).max() > 1e-7:
            raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION COHORT_BRIDGE")
    calendar = xcals.get_calendar("XNYS").schedule.loc["2021-01-01":"2024-12-31"]
    expected = [str(x.date()) for x in calendar.index]
    if len(expected) != 1005 or set(col(source_days, "date")) != set(expected):
        raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION XNYS_DATES")
    for r in accounts:
        d = table(
            source_days.loc[
                (col(source_days, "candidate") == r["candidate"])
                & (col(source_days, "arm") == r["arm"])
            ]
        )
        duration = (
            col(calendar, "close") - col(calendar, "open")
        ).dt.total_seconds().to_numpy() / 60
        if not np.array_equal(col(d, "RTH_minutes").to_numpy(), duration):
            raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION HALF_DAY_LENGTH")
    source_days["account_id"] = (
        [catalog[r.strategy_id + "_" + r.variant]["account_id"] for r in records(source_days)]
        if "strategy_id" in source_days
        else (
            [
                (
                    next(
                        r["account_id"]
                        for r in accounts
                        if r["candidate"] == x.candidate and r["arm"] == x.arm
                    )
                )
                for x in records(source_days)
            ]
        )
    )
    counts = pd.read_csv(BASE / "S2C_MATCHED_VS_ATTAINABLE.csv")
    counts = table(counts.loc[col(counts, "population") == "MATCHED"])
    readiness = (
        col(counts, "risk_ready_original_alpha_keys").groupby(col(counts, "candidate")).nunique()
    )
    if not isinstance(readiness, pd.Series) or not bool(readiness.eq(1).all()):
        raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION UNMATCHED_ELIGIBILITY")
    return SavedData(accounts, source_days, cohort, fills, checks, counts, calendar)
