"""Single cached pass across settled accounts; all outputs are re-aggregations."""

from decimal import Decimal
from math import ceil
from pathlib import Path

import numpy as np
import pandas as pd

from .io import ARMS, NI, POLICIES, col, records, table, write_csv
from .metrics import nonexecutable_proxy, performance, ratio, simple_returns
from .saved import SavedData

D = Decimal
ORIENTATION = {
    **{
        k: 1
        for k in (
            "net_PnL_USD",
            "total_return",
            "CAGR",
            "mean_session_return",
            "median_session_return",
            "arithmetic_annual_return",
            "Sharpe",
            "Sortino",
            "Calmar",
            "worst_daily_return",
            "daily_q01",
            "daily_q05",
            "max_drawdown",
            "current_drawdown",
            "net_per_1M_RTH_gross_year",
            "gross_per_1M_executed_notional",
        )
    },
    **{
        k: -1
        for k in (
            "annual_volatility",
            "downside_deviation_daily",
            "downside_semivol_annual",
            "drawdown_severity",
            "longest_underwater_sessions",
            "max_DD_underwater_sessions",
            "total_underwater_sessions",
            "loss_day_fraction",
            "worst_daily_loss_USD",
            "VaR95_loss",
            "VaR99_loss",
            "ES95_loss",
            "ES99_loss",
            "total_cost_USD",
            "commission_USD",
            "print_concession_USD",
            "impact_USD",
            "borrow_USD",
            "funding_USD",
            "cost_per_1M_executed_notional",
            "cost_per_1M_RTH_gross_year",
        )
    },
}


def select(d: pd.DataFrame, account: str) -> pd.DataFrame:
    return table(d.loc[col(d, "account_id") == account])


def epoch_dates(values: pd.Series, fmt: str = "%Y-%m-%d") -> np.ndarray:
    return np.asarray(
        pd.to_datetime(values.to_numpy(float) * 60, unit="s", utc=True)
        .tz_convert("America/New_York")
        .strftime(fmt)
    )


def cost_summary(p: pd.DataFrame) -> dict:
    x = p.copy()
    x["notional"] = abs(col(x, "shares")) * col(x, "external_price")
    x["abs_shares"] = abs(col(x, "shares"))
    orders = table(x.groupby("order_id")[["notional", "abs_shares", "commission"]].sum())
    return {
        "physical_orders_recomputed": len(orders),
        "external_fill_rows": len(p),
        "fills_per_order": len(p) / len(orders) if len(orders) else None,
        "executed_physical_side_notional": float(col(orders, "notional").sum()),
        "arithmetic_roundtrip_equivalent_notional": float(col(orders, "notional").sum()) / 2,
        "mean_order_notional": float(col(orders, "notional").mean()) if len(orders) else None,
        "median_order_notional": float(col(orders, "notional").median()) if len(orders) else None,
        "p25_order_notional": float(col(orders, "notional").quantile(0.25))
        if len(orders)
        else None,
        "p75_order_notional": float(col(orders, "notional").quantile(0.75))
        if len(orders)
        else None,
        "median_order_abs_shares": float(col(orders, "abs_shares").median())
        if len(orders)
        else None,
        "fraction_retail_orders_at_one_USD": float((col(orders, "commission") == 1).mean())
        if len(orders)
        else None,
    }


def cohort_distribution(t: pd.DataFrame) -> dict:
    out = {}
    for field, label in (("cash_pnl", "net"), ("gross_signed_price_pnl", "gross_price")):
        x = col(t, field).to_numpy(float)
        positive = x[x > 0]
        negative = x[x < 0]
        out.update(
            {
                label + "_winning_USD": float(positive.sum()),
                label + "_losing_USD": float(negative.sum()),
                label + "_win_fraction": float(np.mean(x > 0)),
                label + "_mean_winner": float(positive.mean()) if len(positive) else None,
                label + "_median_winner": float(np.median(positive)) if len(positive) else None,
                label + "_mean_loser": float(negative.mean()) if len(negative) else None,
                label + "_median_loser": float(np.median(negative)) if len(negative) else None,
                label + "_profit_factor": ratio(float(positive.sum()), float(-negative.sum())),
            }
        )
        for n in (1, 5, 10):
            out[label + f"_top_{n}_winners_USD"] = float(np.sort(positive)[-n:].sum())
            out[label + f"_worst_{n}_losers_USD"] = float(np.sort(negative)[:n].sum())
    names = table(t.groupby("ticker")[["cash_pnl", "gross_signed_price_pnl"]].sum())
    best = (
        table(names.loc[col(names, "cash_pnl") > 0])
        .sort_values("cash_pnl", ascending=False)
        .head(2)
    )
    top = float(col(best, "cash_pnl").sum())
    net = float(col(t, "cash_pnl").sum())
    out.update(
        top_two_net_ticker_ids="|".join(str(x) for x in best.index),
        top_two_net_USD=top,
        net_without_top_two_ARITHMETIC_ONLY=net - top,
        top_two_net_contribution_over_net=top / net if abs(net) > 1e-7 else None,
        gross_price_of_net_top_two_USD=float(col(best, "gross_signed_price_pnl").sum()),
        median_cohort_span_scheduled_minutes=float(col(t, "scheduled_minutes").median()),
        median_cohort_span_wall_minutes=float((col(t, "exit_at") - col(t, "entry_at")).median()),
        max_cohort_span_scheduled_minutes=float(col(t, "scheduled_minutes").max()),
    )
    for q in (0.25, 0.5, 0.75, 0.9):
        out[f"cohort_span_scheduled_p{int(q * 100)}"] = float(
            col(t, "scheduled_minutes").quantile(q)
        )
    return out


def build(data: SavedData, out: Path) -> dict:
    days = data.days.copy()
    cohorts = data.cohorts.copy()
    fills = data.fills.copy()
    cohorts["entry_date_ET"] = epoch_dates(col(cohorts, "entry_at"))
    cohorts["exit_date_ET"] = epoch_dates(col(cohorts, "exit_at"))
    cohorts["origin_slot_ET"] = epoch_dates(col(cohorts, "origin"), "%H:%M")
    cohorts["entry_year"] = np.asarray(cohorts["entry_date_ET"], str).astype("U4")
    cohorts["exit_year"] = np.asarray(cohorts["exit_date_ET"], str).astype("U4")
    cohorts["side"] = np.where(col(cohorts, "direction") > 0, "LONG", "SHORT")
    cohorts["overnight"] = np.where(
        col(cohorts, "entry_date_ET") == col(cohorts, "exit_date_ET"),
        "INTRADAY_COHORT_SPAN",
        "CROSSED_SESSION_COHORT_SPAN",
    )
    fills["effective_date_ET"] = epoch_dates(col(fills, "effective"))
    metrics = []
    capital = []
    episodes = []
    annual = []
    context = []
    tail_days = []
    exposure_rows = []
    distributions = []
    risk_reasons = []
    account_daily = {}
    account_yearly = {}
    native = {}
    cost_fields = ("commission", "friction", "borrow", "funding")
    for a in data.accounts:
        key = a["account_id"]
        meta = {
            "account_id": key,
            "candidate": a["candidate"],
            "policy": a["policy"],
            "arm": a["arm"],
            "population": "MATCHED",
        }
        d = select(days, key).copy()
        t = select(cohorts, key)
        p = select(fills, key)
        dates = list(col(d, "date").astype(str))
        nav = col(d, "nav").to_numpy(float)
        returns = simple_returns(nav)
        changes = np.diff(np.r_[100000.0, nav])
        m, eps = performance(nav, dates)
        account_daily[key] = (d, returns, changes)
        rth = col(d, "RTH_minutes").to_numpy(float)
        grossday = col(d, "gross_NAV_minutes").to_numpy(float) / rth
        grossyear = float(col(d, "gross_dollar_minutes").sum()) / (252 * 390)
        grossmean = float(col(d, "gross_NAV_minutes").sum() / rth.sum())
        if not np.isclose(grossyear, float(a["RTH_gross_dollar_years"]), atol=1e-7, rtol=1e-12):
            raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION GROSS_EXPOSURE")
        if not np.isclose(
            grossmean, float(a["mean_RTH_marked_gross_fraction"]), atol=1e-12, rtol=1e-12
        ):
            raise ValueError("HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION GROSS_FRACTION")
        orders = cost_summary(p)
        turnover = orders["executed_physical_side_notional"]
        cost = float(a["total_cost_USD"])
        gross = float(a["gross_signed_price_PnL_USD"])
        action = float(a["gross_action_value_USD"])
        net = float(a["net_PnL_USD"])
        d["return"] = returns
        d["NAV_change_USD"] = changes
        d["RTH_mean_filled_virtual_gross_fraction"] = grossday
        d["close_physical_net_fraction"] = col(d, "physical_value") / col(d, "nav")
        d["close_virtual_reserved_gross_fraction"] = col(d, "virtual_gross") / col(d, "nav")
        d["close_unrestricted_cash_before_reservations"] = col(d, "cash") - col(d, "restricted")
        close = data.calendar["close"]
        close_map = {str(pd.Timestamp(str(k)).date()): v.isoformat() for k, v in close.items()}
        d["scheduled_close_UTC"] = col(d, "date").map(close_map)
        for field in cost_fields:
            d["day_" + field] = np.diff(np.r_[0.0, col(d, field).to_numpy(float)])
        d["day_claim_change"] = np.diff(np.r_[0.0, col(d, "claims").to_numpy(float)])
        account_daily[key] = (d, returns, changes)
        m.update(
            {
                **meta,
                "net_PnL_USD_exact": a["net_PnL_USD"],
                "terminal_NAV_USD_exact": str(D(100000) + D(a["net_PnL_USD"])),
                "gross_price_PnL_USD": gross,
                "action_value_USD": action,
                "total_cost_USD": cost,
                "commission_USD": float(a["commission_USD"]),
                "print_concession_USD": float(a["assumed_spread_USD"]),
                "impact_USD": float(a["assumed_impact_USD"]),
                "borrow_USD": float(a["borrow_USD"]),
                "funding_USD": float(a["funding_USD"]),
                "mean_RTH_gross_fraction": grossmean,
                "median_daily_RTH_gross_fraction": float(np.median(grossday)),
                "RTH_filled_virtual_gross_dollar_years": grossyear,
                "mean_close_physical_net_fraction": float(
                    col(d, "close_physical_net_fraction").mean()
                ),
                "max_abs_close_physical_net_fraction": float(
                    abs(col(d, "close_physical_net_fraction")).max()
                ),
                "mean_close_virtual_gross_including_pending_fraction": float(
                    col(d, "close_virtual_reserved_gross_fraction").mean()
                ),
                "invested_session_count": int((col(d, "gross_dollar_minutes") > 0).sum()),
                "fraction_sessions_with_any_RTH_exposure": float(
                    (col(d, "gross_dollar_minutes") > 0).mean()
                ),
                "net_per_1M_RTH_gross_year": ratio(net * 1e6, grossyear),
                "cost_per_1M_RTH_gross_year": ratio(cost * 1e6, grossyear),
                "gross_per_1M_executed_notional": ratio(gross * 1e6, turnover),
                "cost_per_1M_executed_notional": ratio(cost * 1e6, turnover),
                "expense_over_price_plus_action_edge": cost / (gross + action)
                if abs(gross + action) > 1e-7
                else None,
                "physical_order_count": int(a["external_orders"]),
                "filled_cohort_count": int(a["cohorts"]),
                "risk_closed_cohort_count": int(float(a.get("cohorts_with_risk_fill", "0"))),
                "risk_final_exits": int(float(a["risk_final_exits"])),
                "policy_final_exits": int(float(a["scheduled_final_exits"])),
                "duplicate_suppression": int(a["duplicate_suppression"]),
                "order_budget_suppression": int(a["order_budget_suppression"]),
                "retail_minimum_notional_rejection": int(a["retail_minimum_notional"]),
                "missing_bar_attempts": int(a["missing_bar_attempts"]),
                "simulated_entry_expiries": int(a["simulated_entry_expiries"]),
                "mode": a["mode"],
                "turnover_over_mean_NAV": turnover / float(nav.mean()),
            }
        )
        metrics.append(m)
        native[key] = m
        distributions.append({**meta, **cohort_distribution(t)})
        cap = {
            **meta,
            **orders,
            "gross_price_PnL_USD": gross,
            "action_value_USD": action,
            "net_PnL_USD": net,
            "RTH_gross_dollar_years": grossyear,
            "mean_RTH_gross_fraction": grossmean,
            "mean_close_cash_USD": float(col(d, "cash").mean()),
            "mean_close_restricted_USD": float(col(d, "restricted").mean()),
            "mean_close_unrestricted_cash_before_reservations_USD": float(
                col(d, "close_unrestricted_cash_before_reservations").mean()
            ),
            "mean_RTH_unrestricted_cash_before_reservations_fraction": float(
                col(d, "spendable_cash_NAV_minutes").sum() / rth.sum()
            ),
            "true_free_buying_power": NI,
            "exact_RTH_invested_time_fraction": NI,
            "physical_gross_and_long_short_exposure": NI,
            "name_vintage_utilization": NI,
            "per_stock_marked_exposure": NI,
            "cash_restriction_already_inside_cash": True,
        }
        if a["mode"] == "MICRO_PRO":
            cap["fraction_retail_orders_at_one_USD"] = None
        for field, label in (
            ("commission_USD", "commission"),
            ("assumed_spread_USD", "print_concession"),
            ("assumed_impact_USD", "impact"),
            ("borrow_USD", "borrow"),
            ("funding_USD", "funding"),
        ):
            cap[label + "_USD"] = float(a[field])
            cap[label + "_bps_per_executed_side_notional"] = float(a[field]) / turnover * 1e4
        capital.append(cap)
        for n, e in enumerate(eps[:3], 1):
            episodes.append({**meta, "severity_rank": n, **e})
        for z in records(d):
            exposure_rows.append(
                {
                    **meta,
                    "date": z.date,
                    "scheduled_close_UTC": z.scheduled_close_UTC,
                    "RTH_mean_filled_virtual_gross_USD": z.gross_dollar_minutes / z.RTH_minutes,
                    "RTH_mean_filled_virtual_gross_fraction": (
                        z.RTH_mean_filled_virtual_gross_fraction
                    ),
                    "close_physical_net_USD": z.physical_value,
                    "close_physical_net_fraction": z.close_physical_net_fraction,
                    "close_virtual_gross_including_pending_USD": z.virtual_gross,
                    "close_unrestricted_cash_before_reservations": (
                        z.close_unrestricted_cash_before_reservations
                    ),
                    "close_restricted": z.restricted,
                    "exact_snapshot_received_at": NI,
                }
            )
        prev = 100000.0
        year_metrics = {}
        for year in ("2021", "2022", "2023", "2024"):
            z = table(d.loc[col(d, "date").astype(str).str.startswith(year)])
            ym, _ = performance(col(z, "nav").to_numpy(float), list(col(z, "date")), prev)
            year_metrics[year] = ym
            ar = {
                **meta,
                "year": year,
                **ym,
                "year_opening_NAV": prev,
                "commission_USD": float(col(z, "day_commission").sum()),
                "price_concession_USD": float(col(z, "day_friction").sum()),
                "borrow_USD": float(col(z, "day_borrow").sum()),
                "funding_USD": float(col(z, "day_funding").sum()),
                "invested_sessions": int((col(z, "gross_dollar_minutes") > 0).sum()),
                "mean_RTH_gross_fraction": float(
                    col(z, "gross_NAV_minutes").sum() / col(z, "RTH_minutes").sum()
                ),
            }
            annual.append(ar)
            prev = float(col(z, "nav").iloc[-1])
        account_yearly[key] = year_metrics
        # Stratified closed-cohort totals are lifetime allocations, not calendar NAV attribution.
        for axis in (
            "ticker",
            "side",
            "overnight",
            "origin_slot_ET",
            "entry_year",
            "exit_year",
            "cause",
        ):
            for label, block in t.groupby(axis):
                z = table(block)
                context.append(
                    {
                        **meta,
                        "axis": "COHORT_" + axis,
                        "label": str(label),
                        "sample_count": len(z),
                        "support": "LOW_SUPPORT" if len(z) < 20 else "DESCRIPTIVE",
                        "net_USD": float(col(z, "cash_pnl").sum()),
                        "gross_price_USD": float(col(z, "gross_signed_price_pnl").sum()),
                        "action_value_USD": float(col(z, "gross_action_cash").sum()),
                        "total_execution_cost_USD": float(col(z, "cost").sum()),
                        "commission_USD": float(col(z, "fees").sum()),
                        "combined_price_concession_USD": float(
                            (col(z, "cost") - col(z, "fees")).sum()
                        ),
                        "borrow_USD": float(col(z, "borrow").sum()),
                        "funding_USD": float(col(z, "funding").sum()),
                        "median_cohort_span_scheduled_minutes": float(
                            col(z, "scheduled_minutes").median()
                        ),
                        "physical_orders": None,
                        "marked_exposure": None,
                        "unsupported_fields": NI
                        + " physical orders by virtual stratum/marked exposure",
                        "not_calendar_year_NAV_attribution": True,
                    }
                )
        for ticker, block in p.groupby("ticker"):
            z = table(block)
            cs = cost_summary(z)
            context.append(
                {
                    **meta,
                    "axis": "PHYSICAL_EXECUTION_TICKER",
                    "label": str(ticker),
                    "sample_count": len(z),
                    "physical_orders": cs["physical_orders_recomputed"],
                    "external_notional": cs["executed_physical_side_notional"],
                    "commission_USD": float(col(z, "commission").sum()),
                    "modeled_print_concession_USD": float(col(z, "print_slippage").sum()),
                    "modeled_impact_USD": float(col(z, "impact").sum()),
                    "marked_exposure": None,
                    "unsupported_fields": NI
                    + " ticker marked exposure; ticker20=OGN special execution",
                }
            )
        for cause, block in t.groupby("cause"):
            z = table(block)
            prior = (
                (col(z, "final_role") != "RISK_LIQUIDATION")
                if "final_role" in z
                else pd.Series(False, index=z.index)
            )
            unknown = (
                int(prior.sum()) if str(cause) == "RISK_OTHER_CAP" and a["candidate"] == "F3" else 0
            )
            risk_reasons.append(
                {
                    **meta,
                    "cause": str(cause),
                    "cohorts": len(z),
                    "share_of_closed_cohorts": len(z) / len(t),
                    "net_USD": float(col(z, "cash_pnl").sum()),
                    "gross_price_USD": float(col(z, "gross_signed_price_pnl").sum()),
                    "execution_cost_USD": float(col(z, "cost").sum()),
                    "borrow_USD": float(col(z, "borrow").sum()),
                    "median_span_scheduled_minutes": float(col(z, "scheduled_minutes").median()),
                    "cohorts_prior_partial_risk_final_policy_cause_unidentified": unknown,
                    "risk_tag_not_individual_causal_constraint": True,
                }
            )
        for ix in np.argsort(returns, kind="stable")[:10]:
            day = d.iloc[int(ix)]
            date = str(day["date"])
            pf = table(p.loc[col(p, "effective_date_ET") == date])
            ct = table(t.loc[col(t, "exit_date_ET") == date])
            ids = "|".join(str(x) for x in sorted(set(col(pf, "order_id")))[:10])
            tail_days.append(
                {
                    **meta,
                    "date": date,
                    "daily_return": float(returns[ix]),
                    "NAV_change_USD": float(changes[ix]),
                    "RTH_mean_virtual_gross_fraction": float(grossday[ix]),
                    "close_signed_physical_value_USD": float(day["physical_value"]),
                    "prior_close_signed_physical_value_USD": float(d.iloc[ix - 1]["physical_value"])
                    if ix
                    else 0.0,
                    "physical_orders": int(col(pf, "order_id").nunique()),
                    "physical_fill_rows": len(pf),
                    "order_sample_max10": ids,
                    "closed_cohorts": len(ct),
                    "closed_cohort_lifetime_net_NOT_day_PnL": float(col(ct, "cash_pnl").sum()),
                    "commission_charged_day": float(day["day_commission"]),
                    "combined_print_impact_charged_day": float(day["day_friction"]),
                    "borrow_charged_day": float(day["day_borrow"]),
                    "funding_charged_day": float(day["day_funding"]),
                    "net_claim_value_change_NOT_complete_actions": float(day["day_claim_change"]),
                    "exact_action_events_and_day_action_PnL": NI,
                    "gross_price_plus_action_combined_day": float(changes[ix])
                    + sum(float(day["day_" + k]) for k in cost_fields),
                }
            )
    # Fixed non-outcome-selected contemporaneous exposure bins; all sessions are retained.
    exposure_bins = []
    edges = np.array([-0.000000000001, 1e-12, 0.05, 0.10, 0.20, 0.40, 1.0, np.inf])
    labels = (
        "ZERO",
        "0_to_5pct",
        "5_to_10pct",
        "10_to_20pct",
        "20_to_40pct",
        "40_to_100pct",
        "OVER_100pct",
    )
    for a in data.accounts:
        d, r, _ = account_daily[a["account_id"]]
        values = col(d, "RTH_mean_filled_virtual_gross_fraction").to_numpy(float)
        bins = np.searchsorted(edges, values, side="left") - 1
        for i, label in enumerate(labels):
            b = bins == i
            exposure_bins.append(
                {
                    "account_id": a["account_id"],
                    "candidate": a["candidate"],
                    "arm": a["arm"],
                    "bin": label,
                    "sessions": int(b.sum()),
                    "mean_simple_return": float(r[b].mean()) if b.any() else None,
                    "mean_RTH_gross_fraction": float(values[b].mean()) if b.any() else None,
                    "contemporaneous_endogenous_NOT_pretrade_filter": True,
                }
            )
        if int(np.sum([np.sum(bins == i) for i in range(len(labels))])) != 1005:
            raise ValueError("EXPOSURE_BIN_CENSUS")
    paired = pairwise(data, native, account_daily, account_yearly, out)
    write_csv(out / "MATCHED_PORTFOLIO_RISK_TABLE.csv", metrics)
    write_csv(out / "COST_CAPITAL_ATTRIBUTION.csv", capital)
    write_csv(out / "TAIL_DRAWDOWN_EPISODES.csv", episodes)
    write_csv(out / "ANNUAL_NAV_RISK.csv", annual)
    write_csv(out / "ANNUAL_AND_STOCK_CONTEXT.csv", context)
    write_csv(out / "COHORT_WIN_LOSS_CONCENTRATION.csv", distributions)
    write_csv(out / "EXIT_RISK_AND_HOLDING_CONTEXT.csv", risk_reasons)
    write_csv(out / "WORST_TAIL_DAYS.csv", tail_days)
    write_csv(out / "EXPOSURE_BIN_DESCRIPTORS.csv", exposure_bins)
    pd.DataFrame(exposure_rows).to_parquet(
        out / "DAILY_CAPITAL_DESCRIPTORS.parquet", index=False, compression="zstd"
    )
    # Collapse the 12,108 exact checks into bounded account/scope maxima.
    grouped = {}
    for row in data.checks:
        k = (row["account_id"], row["scope"])
        v = grouped.setdefault(k, {"count": 0, "max": D(0)})
        v["count"] += 1
        v["max"] = max(v["max"], abs(D(row["residual_USD"])))
    write_csv(
        out / "ACCOUNT_RECONCILIATION.csv",
        [
            {
                "account_id": k[0],
                "scope": k[1],
                "checks": v["count"],
                "maximum_abs_residual_USD": str(v["max"]),
                "status": "PASS",
            }
            for k, v in grouped.items()
        ],
    )
    return {
        "metrics": metrics,
        "paired": paired,
        "annual": annual,
        "capital": capital,
        "distributions": distributions,
        "cohort_rows": len(cohorts),
        "physical_rows": len(fills),
        "max_daily_and_terminal_residual_USD": str(
            max(abs(D(x["residual_USD"])) for x in data.checks)
        ),
    }


def pairwise(data, native, daily, yearly, out: Path) -> list[dict]:
    pairs = []
    days_out = []
    periods = []
    tail_rows = []
    proxies = []
    channels = []
    overlap = []
    episode_rows = []
    channel_fields = (
        "net_PnL_USD",
        "Sharpe",
        "Sortino",
        "annual_volatility",
        "drawdown_severity",
        "ES95_loss",
        "ES99_loss",
        "downside_semivol_annual",
    )
    for fid in POLICIES:
        s = next(a for a in data.accounts if a["candidate"] == fid and a["arm"] == "S2C_RISK")
        sm = native[s["account_id"]]
        sd, sr, sc = daily[s["account_id"]]
        dates = list(col(sd, "date"))
        for arm in ARMS[:-1]:
            c = next(a for a in data.accounts if a["candidate"] == fid and a["arm"] == arm)
            cm = native[c["account_id"]]
            cd, cr, cc = daily[c["account_id"]]
            if dates != list(col(cd, "date")):
                raise ValueError("PAIRED_DATE_MISMATCH")
            meta = {
                "candidate": fid,
                "policy": POLICIES[fid],
                "control": arm,
                "S2C_account": s["account_id"],
                "control_account": c["account_id"],
                "population": "MATCHED",
            }
            dr = sr - cr
            dc = sc - cc
            row = {
                **meta,
                "paired_sessions": len(dr),
                "positive_return_difference_days": int((dr > 0).sum()),
                "negative_return_difference_days": int((dr < 0).sum()),
                "zero_difference_days": int((dr == 0).sum()),
                "mean_return_difference": float(dr.mean()),
                "median_return_difference": float(np.median(dr)),
                "worst_return_difference": float(dr.min()),
                "mean_NAV_change_difference_USD": float(dc.mean()),
                "sum_NAV_change_differences_USD": float(dc.sum()),
                "terminal_relative_wealth_ratio_minus1": sm["final_NAV"] / cm["final_NAV"] - 1,
                "sum_simple_return_differences_NOT_USD": float(dr.sum()),
            }
            for field in sm:
                x, y = sm[field], cm.get(field)
                if (
                    isinstance(x, (int, float))
                    and not isinstance(x, bool)
                    and isinstance(y, (int, float))
                ):
                    row[field + "_S2C"] = x
                    row[field + "_control"] = y
                    direction = ORIENTATION.get(field, 0)
                    row[field + "_improvement"] = direction * (x - y) if direction else None
                    if not direction:
                        row[field + "_S2C_minus_control_DESCRIPTIVE"] = x - y
            pairs.append(row)
            for n, date in enumerate(dates):
                days_out.append(
                    {
                        **meta,
                        "date": date,
                        "return_difference": float(dr[n]),
                        "NAV_change_difference_USD": float(dc[n]),
                        "actual_NAV_gap_USD": float(sd.iloc[n]["nav"] - cd.iloc[n]["nav"]),
                    }
                )
            for count, label, ascending in (
                (ceil(0.05 * len(cr)), "CONTROL_WORST5PCT", True),
                (ceil(0.01 * len(cr)), "CONTROL_WORST1PCT", True),
                (ceil(0.05 * len(cr)), "CONTROL_BEST5PCT", False),
            ):
                ix = np.argsort(cr if ascending else -cr, kind="stable")[:count]
                s_exp = col(sd, "RTH_mean_filled_virtual_gross_fraction").to_numpy(float)[ix]
                c_exp = col(cd, "RTH_mean_filled_virtual_gross_fraction").to_numpy(float)[ix]
                tail_rows.append(
                    {
                        **meta,
                        "same_control_selected_dates": label,
                        "count": count,
                        "mean_control_return": float(cr[ix].mean()),
                        "mean_S2C_return": float(sr[ix].mean()),
                        "mean_return_difference": float(dr[ix].mean()),
                        "S2C_mean_RTH_gross_fraction": float(s_exp.mean()),
                        "control_mean_RTH_gross_fraction": float(c_exp.mean()),
                        "S2C_to_control_mean_exposure": ratio(
                            float(s_exp.mean()), float(c_exp.mean())
                        ),
                        "S2C_days_with_better_return": int((dr[ix] > 0).sum()),
                        "selected_by_control_outcome_DESCRIPTIVE_NOT_strategy": True,
                    }
                )
            for kind, field in (
                ("MEAN_RTH_GROSS", "mean_RTH_gross_fraction"),
                ("NATIVE_VOLATILITY", "annual_volatility"),
            ):
                proxy = nonexecutable_proxy(sr, dates, cm[field], sm[field], kind)
                proxies.append(
                    {
                        **meta,
                        "normalizer": kind,
                        "control_level": cm[field],
                        "S2C_level": sm[field],
                        **proxy,
                        "control_total_return": cm["total_return"],
                        "control_drawdown_severity": cm["drawdown_severity"],
                        "control_annual_volatility": cm["annual_volatility"],
                        "control_ES95_loss": cm["ES95_loss"],
                        "not_a_funded_portfolio": True,
                        "cost_schedule_not_recomputed": True,
                    }
                )
            for year in ("2021", "2022", "2023", "2024"):
                ym_s = yearly[s["account_id"]][year]
                ym_c = yearly[c["account_id"]][year]
                periods.append(
                    {
                        **meta,
                        "period_type": "YEAR",
                        "period": year,
                        "S2C_net_USD": ym_s["net_PnL_USD"],
                        "control_net_USD": ym_c["net_PnL_USD"],
                        "net_difference_USD": ym_s["net_PnL_USD"] - ym_c["net_PnL_USD"],
                        "S2C_return": ym_s["total_return"],
                        "control_return": ym_c["total_return"],
                        "compounded_return_difference": ym_s["total_return"] - ym_c["total_return"],
                    }
                )
            for month in sorted(set(str(x)[:7] for x in dates)):
                ix = np.flatnonzero(np.asarray([str(x).startswith(month) for x in dates]))
                n0 = int(ix[0])
                s0 = float(sd.iloc[n0 - 1]["nav"]) if n0 else 100000.0
                c0 = float(cd.iloc[n0 - 1]["nav"]) if n0 else 100000.0
                s1 = float(sd.iloc[int(ix[-1])]["nav"])
                c1 = float(cd.iloc[int(ix[-1])]["nav"])
                periods.append(
                    {
                        **meta,
                        "period_type": "MONTH",
                        "period": month,
                        "S2C_net_USD": s1 - s0,
                        "control_net_USD": c1 - c0,
                        "net_difference_USD": (s1 - s0) - (c1 - c0),
                        "S2C_return": s1 / s0 - 1,
                        "control_return": c1 / c0 - 1,
                        "compounded_return_difference": s1 / s0 - c1 / c0,
                    }
                )
            for field in channel_fields:
                value = row.get(field + "_improvement")
                annual = []
                for year in ("2021", "2022", "2023", "2024"):
                    x = yearly[s["account_id"]][year].get(field)
                    y = yearly[c["account_id"]][year].get(field)
                    if x is not None and y is not None:
                        annual.append(ORIENTATION[field] * (x - y))
                if value is None:
                    label = "NOT_IDENTIFIABLE"
                elif value > 1e-12 and annual and all(x >= -1e-12 for x in annual):
                    label = "SUPPORTED_EXPLORATORY"
                elif value > 1e-12 or (annual and any(x > 1e-12 for x in annual)):
                    label = "MIXED"
                else:
                    label = "NO_EVIDENCE"
                channels.append(
                    {
                        **meta,
                        "channel": field,
                        "full_period_improvement": value,
                        "annual_improving_years": sum(x > 1e-12 for x in annual),
                        "annual_defined_years": len(annual),
                        "status": label,
                        "no_composite_score": True,
                    }
                )
            st = select(data.cohorts, s["account_id"])
            ct = select(data.cohorts, c["account_id"])
            left = {(int(r.origin), int(r.ticker), int(r.direction)): r for r in records(ct)}
            right = {(int(r.origin), int(r.ticker), int(r.direction)): r for r in records(st)}
            both = left.keys() & right.keys()
            overlap.append(
                {
                    **meta,
                    "source_opportunity_base_shared": True,
                    "both_funded": len(both),
                    "control_only": len(left.keys() - right.keys()),
                    "S2C_only": len(right.keys() - left.keys()),
                    "shared_exit_timestamp_changed": sum(
                        left[k].exit_at != right[k].exit_at for k in both
                    ),
                    "shared_entry_notional_changed": sum(
                        left[k].entry_notional_raw_USD != right[k].entry_notional_raw_USD
                        for k in both
                    ),
                    "exact_rounding_vs_cap_dollar_causal_split": NI,
                }
            )
            _, eps = performance(col(cd, "nav").to_numpy(float), dates)
            for e in eps[:3]:
                peak = e["peak_index"]
                end = dates.index(e["episode_last_date"]) + 1
                sx = np.r_[100000.0, col(sd, "nav").to_numpy(float)]
                cx = np.r_[100000.0, col(cd, "nav").to_numpy(float)]
                episode_rows.append(
                    {
                        **meta,
                        "control_peak_date": e["peak_date"],
                        "control_trough_date": e["trough_date"],
                        "control_episode_end": e["episode_last_date"],
                        "control_own_episode_return": float(cx[end] / cx[peak] - 1),
                        "S2C_return_on_same_interval": float(sx[end] / sx[peak] - 1),
                        "control_recovered": e["recovered"],
                        "same_calendar_interval_NOT_matched_holdings": True,
                    }
                )
    write_csv(out / "S2C_PAIRWISE_RISK_DELTAS.csv", pairs)
    write_csv(out / "PAIRED_CONTROL_TAIL_DATES.csv", tail_rows)
    write_csv(out / "NONEXECUTABLE_EXPOSURE_AND_VOL_NORMALIZATION.csv", proxies)
    write_csv(out / "PAIRED_MONTHLY_AND_ANNUAL.csv", periods)
    write_csv(out / "CHANNEL_ASSESSMENTS.csv", channels)
    write_csv(out / "FUNDED_OPPORTUNITY_OVERLAP.csv", overlap)
    write_csv(out / "PAIRED_CONTROL_DRAWDOWN_INTERVALS.csv", episode_rows)
    pd.DataFrame(days_out).to_parquet(
        out / "PAIRED_DAILY_DIFFERENCES.parquet", index=False, compression="zstd"
    )
    return pairs
