"""Read an immutable Rapid V1 screen and publish compact, separate analysis."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from lstm_data.trading.track2.rapid_v1.paths import digest, publish
from lstm_data.trading.track2.rapid_v1.strategies import IDS
from lstm_data.trading.track2.stage012.calendar_schedule import MarketClock
from lstm_data.trading.track2.stage012.model_registry import SYMBOLS
from lstm_data.trading.track2.stage35.final_backtest_v4.market import minute

ET = "America/New_York"


def verified_run(run: Path) -> tuple[dict, Path]:
    completions = list(run.glob("RUN_COMPLETION_*.json"))
    if len(completions) != 1:
        raise ValueError("ONE_FINAL_COMPLETION_REQUIRED")
    receipt = json.loads(completions[0].read_text())
    results = Path(receipt["results"])
    manifest = json.loads((results / "manifest.json").read_text())
    if receipt["result_manifest_sha256"] != digest(results / "manifest.json"):
        raise ValueError("COMPLETION_MANIFEST_DRIFT")
    if tuple(manifest["strategy_IDs"]) != IDS:
        raise ValueError("SCREEN_STRATEGY_AXIS")
    for name, sha in manifest["files"].items():
        if digest(results / name) != sha:
            raise ValueError("SCREEN_OUTPUT_DRIFT:" + name)
    return receipt, results


def rth_axis() -> np.ndarray:
    cal = MarketClock("2021-01-01", "2024-12-31").calendar
    return np.concatenate(
        [np.arange(minute(row["open"]), minute(row["close"])) for _, row in cal.iterrows()]
    )


def groups(trades: pd.DataFrame, clock: np.ndarray) -> tuple[pd.DataFrame, float]:
    if trades.empty:
        return pd.DataFrame(), 0.0
    t = trades.copy()
    opened = pd.to_datetime(t["entry_at"] * 60, unit="s", utc=True).dt.tz_convert(ET)
    closed = pd.to_datetime(t["exit_at"] * 60, unit="s", utc=True).dt.tz_convert(ET)
    origins = pd.to_datetime(t["origin"] * 60, unit="s", utc=True).dt.tz_convert(ET)
    t["year"] = opened.dt.strftime("%Y")
    t["slot_ET"] = origins.dt.strftime("%H:%M")
    t["symbol"] = [SYMBOLS[int(j)] for j in t["ticker"].to_list()]
    t["side"] = np.where(t["direction"] > 0, "long", "short")
    t["session_crossing"] = np.where(
        closed.isna(), "open", np.where(opened.dt.date == closed.dt.date, "intraday", "overnight")
    )
    t["gross_win"] = t["gross_signed_price_pnl"].clip(lower=0)
    t["gross_loss"] = t["gross_signed_price_pnl"].clip(upper=0)
    t["holding_minutes"] = t["exit_at"] - t["entry_at"]
    occupied = np.zeros(len(clock) + 1, dtype=np.int32)
    ends = t["exit_at"].fillna(clock[-1] + 1)
    np.add.at(occupied, np.searchsorted(clock, t["entry_at"]), 1)
    np.add.at(occupied, np.searchsorted(clock, ends), -1)
    summary = []
    for dimension in ("year", "slot_ET", "symbol", "side", "session_crossing"):
        group = t.groupby(dimension, dropna=False)
        result = group.agg(
            lots=("key", "count"),
            gross_price_USD=("gross_signed_price_pnl", "sum"),
            gross_wins_USD=("gross_win", "sum"),
            gross_losses_USD=("gross_loss", "sum"),
            net_attributed_USD=("cash_pnl", "sum"),
            gross_action_USD=("gross_action_cash", "sum"),
            transaction_cost_USD=("cost", "sum"),
            borrow_USD=("borrow", "sum"),
            fees_USD=("fees", "sum"),
            median_wall_minutes=("holding_minutes", "median"),
        ).reset_index()
        result = result.rename(columns={dimension: "group"})
        result.insert(0, "dimension", dimension)
        summary.append(result)
    return pd.concat(summary, ignore_index=True), float(np.mean(occupied[:-1].cumsum() > 0))


def classify(trades: pd.DataFrame) -> dict[str, pd.DataFrame]:
    if trades.empty:
        return {}
    wrong = trades["gross_signed_price_pnl"] < 0
    erased = (
        (trades["gross_signed_price_pnl"] > 0)
        & (trades["cash_pnl"] < 0)
        & (trades["gross_action_cash"].abs() < 1e-8)
    )
    return {
        "Wrong gross direction": pd.DataFrame(trades.loc[wrong]),
        "Positive gross price move erased by modeled costs": pd.DataFrame(trades.loc[erased]),
    }


def utc_minute(value: object) -> str | None:
    if value is None or str(value) == "nan":
        return None
    return datetime.fromtimestamp(float(str(value)) * 60, timezone.utc).isoformat()


def analyze(run: Path, destination: Path) -> None:
    receipt, results = verified_run(run)
    destination.mkdir(parents=True, exist_ok=False)
    clock = rth_axis()
    diag_rows, attribution, monthly, examples = [], [], [], []
    for strategy in IDS:
        base = results / strategy
        summary = json.loads((base / "summary.json").read_text())
        detail = json.loads((base / "diagnostics.json").read_text())
        trades = pd.read_parquet(base / "trades.parquet")
        orders = pd.read_parquet(base / "physical_orders.parquet")
        daily = pd.read_parquet(base / "daily_nav.parquet")
        signals = pd.read_csv(base / "signal_counts.csv")
        grouped, invested = groups(trades, clock)
        if not grouped.empty:
            grouped.insert(0, "strategy_id", strategy)
            attribution.append(grouped)
        if not signals.empty:
            signals["month"] = signals["date"].str[:7]
            roll = pd.DataFrame(
                signals.groupby(["month", "slot"], as_index=False).sum(numeric_only=True)
            )
            roll.insert(0, "strategy_id", strategy)
            monthly.append(roll)
        paid = float(summary["commissions_USD"])
        external = summary["physical_external_orders"]
        outcome = detail["quality"]
        for reason, subset in classify(trades).items():
            for row in subset.head(3).to_dict(orient="records"):
                examples.append(
                    {
                        "strategy_id": strategy,
                        "failure": reason,
                        "symbol": SYMBOLS[int(row["ticker"])],
                        "decision_utc": utc_minute(row["decision"]),
                        "entry_utc": utc_minute(row["entry_at"]),
                        "exit_utc": utc_minute(row["exit_at"]),
                        "intent_lineage": row["intent_lineage"],
                        "trade_key": row["key"],
                        "gross_USD": float(row["gross_signed_price_pnl"]),
                        "net_USD": float(row["cash_pnl"]),
                    }
                )
        for item in detail["anomalies"]:
            if item["kind"] in (
                "REJECT",
                "V5_PENDING_MISSING_BAR",
                "EXPIRED_UNFILLED_BY_V5_SIMULATION",
                "MRK_OGN_ENTITLEMENT",
            ):
                examples.append({"strategy_id": strategy, "failure": item["kind"], **item})
        usable = daily[(daily["status"] == "OBSERVED") & (daily["nav"] > 0)]
        gross_sum = float(summary["gross_signed_price_PnL_USD"])
        diag_rows.append(
            {
                "strategy_id": strategy,
                "mode": summary["mode"],
                "status": summary["status"],
                "price_edge_USD": gross_sum,
                "gross_wins_USD": summary["gross_winning_USD"],
                "gross_losses_USD": summary["gross_losing_USD"],
                "net_PnL_USD": summary.get("net_PnL_USD"),
                "commissions_USD": paid,
                "commission_per_filled_external_order_USD": paid / external if external else None,
                "physical_orders": external,
                "executed_notional_USD": float(
                    (orders["shares"] * orders["external_price"]).abs().sum()
                )
                if not orders.empty
                else 0.0,
                "time_in_market_RTH_fraction": invested,
                "average_close_spendable_cash_NAV": float(
                    ((usable["cash"] - usable["restricted"]) / usable["nav"]).mean()
                )
                if not usable.empty
                else None,
                "average_close_net_stock_NAV": float(
                    (usable["physical_value"] / usable["nav"]).mean()
                )
                if not usable.empty
                else None,
                "loss_driver": (
                    "unresolved_economics"
                    if summary["status"] == "HOLD"
                    else "no_fills"
                    if not external
                    else "weak_gross_signed_price_edge"
                    if gross_sum < 0
                    else "net_loss_with_positive_gross_price_edge"
                    if summary["net_PnL_USD"] < 0
                    else "net_positive"
                ),
                "funded_cohorts": summary["cohorts_filled"],
                "candidate_intents": summary["candidate_intents"],
                "observed_unfunded_outcomes": outcome["mature_outcomes"],
                "unfunded_sign_hit_rate": outcome["sign_hit_rate"],
                "unfunded_mean_signed_log_return": outcome["mean_signed_log_return"],
            }
        )
    pd.DataFrame(diag_rows).to_csv(destination / "MODE_COST_AND_CAPACITY.csv", index=False)
    if attribution:
        pd.concat(attribution, ignore_index=True).to_csv(
            destination / "FUNDED_ATTRIBUTION.csv", index=False
        )
    if monthly:
        pd.concat(monthly, ignore_index=True).fillna(0).to_csv(
            destination / "MONTHLY_SLOT_COVERAGE.csv", index=False
        )
    publish(destination / "SOURCE_BACKED_EXAMPLES.json", examples)
    publish(
        destination / "ANALYSIS_MANIFEST.json",
        {
            "screen_result_manifest_sha256": receipt["result_manifest_sha256"],
            "source": str(results),
            "analysis_code_sha256": digest(Path(__file__)),
            "files": {p.name: digest(p) for p in destination.iterdir() if p.is_file()},
            "qualification": (
                "Reused 2021–24 fixed survivors. Retrospective actions and cleaning. "
                "Receipt, borrow and OHLCV execution are conditional research scenarios."
            ),
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    analyze(args.run, args.destination)
