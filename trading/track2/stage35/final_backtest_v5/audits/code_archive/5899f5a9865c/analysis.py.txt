"""Frozen descriptive OHLCV-proxy research reporting; no Stage6 inference."""

import gzip
import json
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd

from .paths import publish
from .release import Admission, check_admission


def metrics(values: np.ndarray, dates: pd.DatetimeIndex, initial: float = 100000.0) -> dict:
    if (
        not len(values)
        or len(dates) != len(values)
        or not np.isfinite(values).all()
        or (values <= 0).any()
    ):
        return {"status": "UNDEFINED_NONPOSITIVE_OR_INCOMPLETE_NAV"}
    ret = values / np.r_[initial, values[:-1]] - 1
    sigma = float(ret.std(ddof=1)) if len(ret) > 1 else 0.0
    downside = float(np.sqrt(np.mean(np.minimum(ret, 0) ** 2)))
    high = np.maximum.accumulate(np.r_[initial, values])[1:]
    drawdown = values / high - 1
    mdd = float(drawdown.min())
    duration = longest = 0
    for underwater in drawdown < 0:
        duration = duration + 1 if underwater else 0
        longest = max(longest, duration)
    period_start = pd.Timestamp(year=int(pd.Timestamp(str(dates[0])).year), month=1, day=1)
    years = ((dates[-1] - period_start).days + 1) / 365.25
    cagr = float((values[-1] / initial) ** (1 / years) - 1) if years > 0 else None
    return {
        "status": "EXPLORATORY_CONDITIONAL_OHLCV_PROXY",
        "days": len(values),
        "final_NAV": float(values[-1]),
        "cumulative_return": float(values[-1] / initial - 1),
        "CAGR": cagr,
        "arithmetic_annualized_return_252": float(ret.mean() * 252),
        "volatility_252": sigma * np.sqrt(252),
        "Sharpe_252_zero_rf": float(ret.mean() / sigma * np.sqrt(252)) if sigma else None,
        "Sortino_252_zero_MAR": float(ret.mean() / downside * np.sqrt(252)) if downside else None,
        "maximum_daily_drawdown": mdd,
        "maximum_drawdown_duration_sessions": longest,
        "Calmar": cagr / abs(mdd) if cagr is not None and mdd else None,
    }


def analyze(folder: Path, admission: Admission) -> dict:
    check_admission(admission, "2021-01-01", "2024-12-31", False)
    results = {}
    contrasts = {}
    for file in sorted(folder.glob("*/daily.jsonl.gz")):
        scenario = file.parent.name
        daily = pd.read_json(file, lines=True, compression="gzip")
        if daily.nav.isna().any() or (daily.status != "OBSERVED").any():
            raise ValueError("NO_HEADLINE_ON_INCOMPLETE_NAV")
        accounts = {}
        for names, group in daily.groupby(["population", "arm"]):
            if not isinstance(names, tuple) or len(names) != 2:
                raise ValueError("ACCOUNT_AXIS_SCHEMA")
            population, arm = names
            group = group.sort_values("date")
            if len(group) != 1005 or group.date.duplicated().any():
                raise ValueError("INCOMPLETE_FINANCIAL_CALENDAR")
            dates = pd.DatetimeIndex(pd.to_datetime(group.date))
            nav = group.nav.to_numpy(float)
            key = f"{scenario}/{population}/{arm}"
            item = metrics(nav, dates)
            item["annual"] = {}
            for year in (2021, 2022, 2023, 2024):
                mask = np.asarray([pd.Timestamp(v).year for v in dates]) == year
                start = int(np.flatnonzero(mask)[0])
                item["annual"][str(year)] = metrics(
                    nav[mask], pd.DatetimeIndex(dates[mask]), nav[start - 1] if start else 100000
                )
            last = group.iloc[-1]
            costs = {
                field: float(last[field])
                for field in (
                    "commission_cumulative",
                    "friction_cumulative",
                    "borrow_cumulative",
                    "funding_cumulative",
                )
            }
            item["costs_USD"] = costs
            item["gross_cost_addback_on_same_holdings_not_frictionless_rerun_USD"] = sum(
                costs.values()
            )
            item["gross_cost_addback_return"] = (nav[-1] + sum(costs.values())) / 100000 - 1
            item["mean_virtual_gross_NAV"] = float((group.gross / group.nav).mean())
            item["mean_available_own_cash_NAV"] = float((group.own_cash / group.nav).mean())
            item["session_fraction_invested"] = float((group.gross > 0).mean())
            item["rejections_attempt_counters"] = last["rejections_cumulative"]
            overlay = group.proxy_standalone_cumulative.to_numpy(float)
            if np.any(overlay):
                item["standalone_dividend_yield_adjustment_USD"] = float(overlay[-1])
                item["standalone_adjusted_metrics_not_buying_power"] = metrics(nav + overlay, dates)
            results[key] = item
            accounts[(population, arm)] = group
        for population in ("matched", "attainable"):
            target = accounts[(population, "S2C_RISK")].nav.to_numpy(float)
            for arm in ("EQUAL", "ROLLING_RISK", "EWMA_RISK"):
                base = accounts[(population, arm)].nav.to_numpy(float)
                key = f"{scenario}/{population}/S2C_MINUS_{arm}"
                contrasts[key] = {
                    "terminal_NAV_difference_USD": float(target[-1] - base[-1]),
                    "terminal_return_difference": float((target[-1] - base[-1]) / 100000),
                    "daily_mean_NAV_difference_USD": float((target - base).mean()),
                    "independent_or_significance_claim": False,
                }
        counts = Counter()
        wait = Counter()
        external = defaultdict(float)
        reasons = Counter()
        with gzip.open(file.parent / "events.jsonl.gz", "rt") as stream:
            for line in stream:
                row = json.loads(line)
                account = (row["population"], row["arm"])
                counts[(*account, row["kind"])] += 1
                if row["kind"] == "FILL":
                    external[account] += abs(float(row["external"]) * float(row["reference"]))
                elif row["kind"] == "V5_QUALIFIED_BAR":
                    wait[(*account, int(row["delay_scheduled_or_wall_minutes"]))] += 1
                elif row["kind"] == "OPPORTUNITY":
                    reasons[(*account, row["reason"])] += 1
        attribution = defaultdict(
            lambda: {"count": 0, "cash_pnl_USD": 0.0, "fees_USD": 0.0, "borrow_USD": 0.0, "wins": 0}
        )
        attributed = defaultdict(Decimal)
        closed_path = file.parent / "cohorts.jsonl.gz"
        if closed_path.exists():
            with gzip.open(closed_path, "rt") as stream:
                for line in stream:
                    row = json.loads(line)
                    account = (row["population"], row["arm"])
                    attributed[account] += Decimal(str(row["cash_pnl"]))
                    if row["entry_at"] is None:
                        continue
                    origin = pd.Timestamp(int(row["origin"]) * 60, unit="s", tz="UTC").tz_convert(
                        "America/New_York"
                    )
                    overnight = int(row["endpoint"]) // 1440 != int(row["origin"]) // 1440
                    for dimension, value in (
                        ("ticker", row["ticker"]),
                        ("slot", origin.strftime("%H:%M")),
                        ("direction", row["direction"]),
                        ("overnight", overnight),
                        ("year", origin.year),
                    ):
                        a = attribution[(*account, dimension, str(value))]
                        a["count"] += 1
                        a["cash_pnl_USD"] += float(row["cash_pnl"])
                        a["fees_USD"] += float(row["fees"])
                        a["borrow_USD"] += float(row["borrow"])
                        a["wins"] += int(Decimal(str(row["cash_pnl"])) > 0)
        terminal = file.parent / "terminal_lots.jsonl.gz"
        if terminal.exists():
            with gzip.open(terminal, "rt") as stream:
                for line in stream:
                    row = json.loads(line)
                    if row["snapshot_session"] != "2024-12-31":
                        continue
                    value = row["total_attributable_equity"]
                    if value is None:
                        raise ValueError("UNPRICED_TERMINAL_ATTRIBUTION")
                    attributed[(row["population"], row["arm"])] += Decimal(str(value))
        for account, group in accounts.items():
            difference = Decimal(str(group.iloc[-1]["nav"])) - 100000 - attributed[account]
            if abs(difference) > Decimal(".000001"):
                raise ValueError("ATTRIBUTION_NAV_NOT_RECONCILED:" + str(difference))
            key = f"{scenario}/{account[0]}/{account[1]}"
            results[key]["attribution_residual_USD"] = str(difference)
            results[key]["external_dollar_turnover_over_mean_NAV"] = external[account] / float(
                group.nav.mean()
            )
        publish(
            file.parent / "EXECUTION_AND_ATTRIBUTION_SUMMARY.json",
            {
                "events": {str(k): v for k, v in sorted(counts.items())},
                "fallback_delay_minutes_histogram": {str(k): v for k, v in sorted(wait.items())},
                "opportunity_reasons": {str(k): v for k, v in sorted(reasons.items())},
                "closed_cohort_attribution": {str(k): v for k, v in sorted(attribution.items())},
                "sectors_and_beta": "NOT_ESTABLISHED_FROM_TRUSTWORTHY_APPROVED_METADATA",
                "strict_V4_performance": "NOT_COMPARABLE_UNRESOLVED_EXACT_MINUTE_EXECUTIONS",
            },
        )
    result = {
        "metrics": results,
        "paired_contrasts": contrasts,
        "Stage6_independent_complete": False,
        "optimized_or_tuned": False,
        "label": "Exploratory retrospective survivor-based OHLCV-proxy conditional-short research",
    }
    publish(folder / "DESCRIPTIVE_ANALYSIS_V5.json", result)
    return result
