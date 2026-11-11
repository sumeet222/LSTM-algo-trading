"""Read-only independent V3 account, source and offline-census verification."""

import argparse
import csv
import json
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd

from lstm_data.trading.track2.rapid_v1.paths import digest, publish
from lstm_data.trading.track2.rapid_v1.strategies import IDS
from lstm_data.trading.track2.rapid_v3_dynamic.policy import REGIMES
from lstm_data.trading.track2.stage35.final_backtest_v4.market import minute

D = Decimal


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open() as stream:
        return list(csv.DictReader(stream))


def check(run: Path) -> None:
    status = json.loads((run / "V3_RUN_STATUS.json").read_text())
    result = Path(status["funded_directory"])
    manifest_path = result / "FUNDED_OUTPUT_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    if digest(manifest_path) != status["funded_manifest_sha256"] or any(
        digest(result / p) != h for p, h in manifest["files"].items()
    ):
        raise ValueError("V3_FUNDED_PAYLOAD_DRIFT")
    rows = csv_rows(result / "V3_ALL54_SUMMARY.csv")
    if len(rows) != 54 or {(r["strategy_id"], r["regime"]) for r in rows} != {
        (s, g) for s in IDS for g in REGIMES
    }:
        raise ValueError("V3_UNRECONCILED_CASE_CENSUS")
    baseline = {
        r["strategy_id"]: int(r["candidate_intents"])
        for r in csv_rows(
            Path("trading/track2/rapid_v1/runs/rapid-v1-defaults-20261110-r1/results")
            / "SUMMARY_18_STRATEGIES.csv"
        )
    }
    max_net = D(0)
    for r in rows:
        if int(r["candidate_intents"]) != baseline[r["strategy_id"]]:
            raise ValueError("PRE_FUNDING_DIRECTIONAL_INPUT_COUNT_DRIFT")
        if r["status"] in ("COMPLETE", "NO_TRADES"):
            if int(r["terminal_stock_symbols"]) or int(r["terminal_pending"]):
                raise ValueError("UNRESOLVED_COMPLETED_BOOK")
            difference = (
                D(r["gross_signed_price_PnL_USD"])
                + D(r["gross_action_value_USD"])
                - sum(
                    D(r[k])
                    for k in (
                        "commission_USD",
                        "assumed_spread_USD",
                        "assumed_impact_USD",
                        "borrow_USD",
                        "funding_USD",
                    )
                )
                - D(r["net_PnL_USD"])
            )
            max_net = max(max_net, abs(difference))
    if max_net > D("1e-7"):
        raise ValueError("V3_PNL_COMPONENT_BRIDGE")
    daily = pd.read_parquet(result / "DAILY_NAV.parquet")
    if len(daily) != 54 * 1005 or daily.duplicated(["strategy_id", "regime", "date"]).any():
        raise ValueError("V3_NAV_SESSION_AXIS")
    observed = daily["status"].to_numpy() == "OBSERVED"
    nav = daily["nav"].to_numpy(float)[observed]
    components = daily[["cash", "physical_value", "claims", "special"]].to_numpy(float)[observed]
    max_nav = float(np.max(np.abs(nav - components.sum(axis=1))))
    if max_nav > 1e-7 or not np.all(np.isfinite(nav) & (nav > 0)):
        raise ValueError("V3_DAILY_MARK_BRIDGE")
    tape = pd.read_parquet(result / "SEALED_ACTUAL_EXIT_LEGS.parquet")
    if (
        (tape["effective"] <= tape["decision"]).any()
        or (tape["posted"] < tape["effective"] + 3).any()
        or tape["effective"].max() >= minute("2025-01-01T00:00:00Z")
    ):
        raise ValueError("V3_EXIT_CAUSALITY")
    if len(status["source_months"]) != 48 or any(
        not str(r["path"]).endswith(".parquet") or "/2025-" in r["path"]
        for r in status["source_months"]
    ):
        raise ValueError("V3_RAW_SOURCE_SCOPE")
    offline = run / "offline_diagnostic"
    receipt = json.loads((offline / "POST_EXIT_RECEIPT.json").read_text())
    if receipt["funded_manifest_sha256"] != digest(manifest_path) or (
        digest(offline / "V3_POST_EXIT_EXTENSION.csv") != receipt["output_sha256"]
    ):
        raise ValueError("POST_EXIT_PROVENANCE")
    if sum(receipt["census"].values()) != len(tape) * 3 or receipt["targets"] != len(tape) * 3:
        raise ValueError("POST_EXIT_ALL_LEG_CENSUS")
    publish(
        run / "INDEPENDENT_OUTPUT_CHECK.json",
        {
            "status": "PASS",
            "cases": 54,
            "daily_rows": len(daily),
            "observed_NAV_rows": int(observed.sum()),
            "exit_legs": len(tape),
            "max_daily_USD_residual": max_nav,
            "max_cash_bridge_USD_residual": max_net,
            "all_54_original_prefunding_signal_counts_match": True,
            "original_approved_market_months": 48,
            "funded_manifest_sha256": digest(manifest_path),
            "offline_census": receipt["census"],
        },
    )
    print("PASS", len(rows), len(daily), len(tape), max_nav, max_net, flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("run", type=Path)
    check(p.parse_args().run)
